import React, { useState } from "react";
import Popup from "reactjs-popup";
import { api, toResult } from "../lib/apiClient.js";

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
    >
      {(close) => (
        <div className="card">
          <div className="content">
            <label>
              Select Teams
              <div>
                {teamsError && <div className="error" role="alert">{teamsError}</div>}
                {loading ? (
                  <p>Loading teams...</p>
                ) : teams && teams.length > 0 ? (
                  <select name="teams" multiple size="4" onChange={handleTeamChange}>
                    {teams.map((team) => (
                      <option key={team.ID} value={team.ID}>
                        {team.Name}
                      </option>
                    ))}
                  </select>
                ) : (
                  <p>No teams available</p>
                )}
              </div>
            </label>

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
              <button className="button" onClick={close}>Close</button>
            </div>
          </div>
        </div>
      )}
    </Popup>
  );
};

export default EventTeamsPopup;
