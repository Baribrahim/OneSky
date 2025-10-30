import React, { useState } from "react";
import Popup from "reactjs-popup";
import { api, toResult } from "../lib/apiClient.js";
import "../styles/eventsTeamPopup.css"

const EventTeamsPopup = ({ eventID }) => {
  const [selectedTeams, setSelectedTeams] = useState([]);
  const [teams, setTeams] = useState([]);
  const [teamsError, setTeamsError] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchTeams = async () => {
    setTeamsError("");
    setLoading(true);
    try {
      const { data, error } = await toResult(api.get(`/api/events/${eventID}/available-teams`));
      if (error) throw new Error(error.message || "Could not load teams.");
      setTeams(data.teams);
    } catch (err) {
      setTeamsError(err.message);
    } finally {
      setLoading(false);
    }
  };

  //Store teams user has selected
  const handleTeamChange = (e) => {
    const options = Array.from(e.target.selectedOptions);
    setSelectedTeams(options.map((o) => o.value));
  };

  //Signup Team to an event  
  const handleTeamSignup = async (team_id) => {
    const { error } = await toResult(api.post("/api/events/signup-team", { event_id: eventID, team_id }));
    if (error) console.error("Signup failed:", error.message);
  };

  return (
    <Popup
      trigger={<button className="button">Register Team</button>}
      modal
      onOpen={fetchTeams}
      className="team-popup"
    >
      {(close) => (
        <div className="card">
          <div className="content">
            
            <h3 className="popup-header">Select Teams</h3>
            <div>
            {teamsError && <div className="error" role="alert">{teamsError}</div>}
            {loading ? (
                <p>Loading teams...</p>
            ) : teams && teams.length > 0 ? (
                <ul className="team-list">
                {teams.map((team) => {
                    const isSelected = selectedTeams.includes(team.ID);
                    return (
                    <li
                        key={team.ID}
                        className={`team-item ${isSelected ? "selected" : ""}`}
                        onClick={() => {
                        if (isSelected) {
                            setSelectedTeams(selectedTeams.filter((id) => id !== team.ID));
                        } else {
                            setSelectedTeams([...selectedTeams, team.ID]);
                        }
                        }}
                    >
                        {team.Name}
                    </li>
                    );
                })}
                </ul>
            ) : (
                <p>No teams available</p>
            )}
            </div>


            <div className="actions">
              <button
                className="button"
                onClick={async () => {
                  await Promise.all(selectedTeams.map(handleTeamSignup));
                  close();
                }}
              >
                Submit
              </button>
              <button className="button" onClick={() => {close(); setSelectedTeams([])}}>Close</button>
            </div>
          </div>
        </div>
      )}
    </Popup>
  );
};

export default EventTeamsPopup;
