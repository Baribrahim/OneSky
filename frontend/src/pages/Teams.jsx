import React, { useEffect, useState } from "react";
import { api, toResult } from "../lib/apiClient";
import TeamCard from "../components/TeamCard";
import MyTeams from "../components/MyTeams";
import "../styles/teams.css";
import { ToastContainer, toast } from 'react-toastify';
import "react-toastify/dist/ReactToastify.css";
/**
 * Teams Page
 * Displays all existing teams for browsing.
 * - Fetches data from GET /teams (requires auth)
 * - Shows cards in a responsive grid
 * - Handles loading, empty, and error states
 */

export default function Teams() {
  const [teams, setTeams] = useState([]);
  const [myTeams, setMyTeams] = useState([]);

  const [teamsLoading, setTeamsLoading] = useState(true);
  const [myTeamsLoading, setMyTeamsLoading] = useState(true);

  const [teamsError, setTeamsError] = useState("");
  const [myTeamsError, setMyTeamsError] = useState("");

  const fetchTeams = async (url, setter, setLoading, setError) => {
    setLoading(true);
    setError("");
    try {
      const { data, error } = await toResult(api.get(url));
      if (error) {
        throw new Error(error.message || "Could not load teams.");
      }
      setter(data?.teams || data?.data?.items || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  const notifyJoined = (joinedTeamName) => toast.success(`Joined Team ${joinedTeamName}`);  
  const notifyLeft = (joinedTeamName) => toast.success(`Left Team ${joinedTeamName}`);  
  const notifyDeleted = (deletedTeamName) => toast.success(`Deleted Team ${deletedTeamName}`);


  useEffect(() => {
    let active = true;

    if (active) {
      fetchTeams("/api/teams", setTeams, setTeamsLoading, setTeamsError);
      fetchTeams("/api/teams/joined", setMyTeams, setMyTeamsLoading, setMyTeamsError);
    }

    return () => { active = false; };
  }, []);

  const onJoin = (joinedTeam, toJoin) => {
    if (toJoin) {
      setMyTeams(prev => [...prev, joinedTeam]); notifyJoined(joinedTeam.name)
    }
    else {
      setMyTeams(prev => prev.filter(team => team.id !== joinedTeam.id)); 
      notifyLeft(joinedTeam.name)
    }
  }

  const onDelete = (deletedTeam) => {
    setTeams(prev => prev.filter(team => team.id !== deletedTeam.id));
    setMyTeams(prev => prev.filter(team => team.id !== deletedTeam.id));
    notifyDeleted(deletedTeam.name)
  }




  // --- UI rendering ---
  return (
    <>
    <div className="welcome-banner">
      <img 
        src={"src/assets/teams-img.jpg"} 
        alt="People volunteering" 
        className="welcome-image" 
      />
      <div className="welcome-text">
        <h1>Teams</h1>
        <p>Volunteer together - find a team that's making a difference</p>
      </div>
    </div>
      <MyTeams teams={myTeams}
               loading={myTeamsLoading} 
               error={myTeamsError} 
               onJoin={onJoin}
               onDelete={onDelete}
               />

      <section className="teams-section" aria-labelledby="teams-heading">
        <div className="teams-inner card">
          <h2 className="event-title" id="teams-heading">Browse Teams</h2>
          <p className="filter-tagline">Explore all active teams below.</p>

          {/* Browse Teams section */}
          {teamsLoading && <p className="filter-tagline" aria-busy="true">Loading teams...</p>}
          {teamsError && !teamsLoading && <p className="error" role="alert">{teamsError}</p>}
          {!teamsLoading && !teamsError && teams.length === 0 && <p className="filter-tagline">No teams found.</p>}
          {!teamsLoading && !teamsError && teams.length > 0 && (
            <div className="teams-grid">
              {teams.map(t => (
                <TeamCard
                key={t.id || t.ID}
                team={t}
                isMember={myTeams.some(mt => mt.id === t.id)}
                isOwner={t.is_owner}
                browseEvents = {true}
                onJoin={onJoin}
              />
              ))}
            </div>
            
          )}
        </div>
      </section>
      <ToastContainer
              toastClassName="my-toast"
              position="top-center"
              autoClose={3000}
              hideProgressBar={true}
              newestOnTop
              closeOnClick
        />
    </>
  );
}
