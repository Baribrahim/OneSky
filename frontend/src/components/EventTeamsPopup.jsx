import React, { useState } from "react";
import Popup from "reactjs-popup";
import { api, toResult } from "../lib/apiClient.js";
import "../styles/eventsTeamPopup.css";

const EventTeamsPopup = ({ eventID }) => {
  const [selectedTeams, setSelectedTeams] = useState([]);
  const [teams, setTeams] = useState([]);
  const [teamsError, setTeamsError] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchTeams = async () => {
    setTeamsError("");
    setSelectedTeams([]);
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

  const handleTeamSignup = async (team_id) => {
    const { error } = await toResult(api.post("/api/events/signup-team", { event_id: eventID, team_id }));
    if (error) console.error("Signup failed:", error.message);
  };

  const handleTeamClick = (team) => {
    if (team.isRegistered) return;
    const isSelected = selectedTeams.includes(team.ID);
    if (isSelected) {
      setSelectedTeams(selectedTeams.filter((id) => id !== team.ID));
    } else {
      setSelectedTeams([...selectedTeams, team.ID]);
    }
  };

  const handleSubmit = async (close) => {
    await Promise.all(selectedTeams.map(handleTeamSignup));
    setSelectedTeams([]);
    close()
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
                    const isRegistered = team.isRegistered === 1;
                    return (
                      <li
                        key={team.ID}
                        className={`team-item 
                          ${isSelected ? "selected" : ""} 
                          ${isRegistered ? "registered" : ""}`}
                        onClick={() => handleTeamClick(team)}
                      >
                        <span>{team.Name}</span>
                        {isRegistered && <span className="registered-text">Registered</span>}
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
                onClick={() => handleSubmit(close)}
                disabled={selectedTeams.length === 0}
              >
                Submit
              </button>
              <button
                className="button"
                onClick={() => {
                  close();
                  setSelectedTeams([]);
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </Popup>
  );
};

export default EventTeamsPopup;
