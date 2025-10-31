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
  
  const notify = (joinedTeamName) => toast.success(`Joined Team ${joinedTeamName}`);  


  useEffect(() => {
    let active = true;

    if (active) {
      fetchTeams("/api/teams", setTeams, setTeamsLoading, setTeamsError);
      fetchTeams("/api/teams/joined", setMyTeams, setMyTeamsLoading, setMyTeamsError);
    }

    return () => { active = false; };
  }, []);


  // --- UI rendering ---
  return (
    <>
      <MyTeams teams={myTeams} loading={myTeamsLoading} error={myTeamsError} />

      <section className="teams-section" aria-labelledby="teams-heading">
        <div className="teams-inner card">
          <h2 className="brand-gradient" id="teams-heading">Browse Teams</h2>
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
                onJoin={(joinedTeam) => {setMyTeams(prev => [...prev, joinedTeam]); notify(joinedTeam.name)}}
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
