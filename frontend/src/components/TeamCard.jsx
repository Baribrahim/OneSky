import React, { useEffect, useState } from "react";
import {api, toResult} from '../lib/apiClient.js';
import Popup from 'reactjs-popup';
import '../styles/popup.css';
import "../styles/teamCard.css";

/**
 * TeamCard
 * Reusable UI card for team info.
 * Displays team information including name, description, department,
 * and join code with conditional buttons based on whether the user is the owner of the team.
 */
export default function TeamCard({ team, isOwner = false, isMember = false, showJoinCode = false, onJoin, browseEvents = false, onDelete}) {
  const { name, description, department, join_code, JoinCode } = team;
  const [joinCode, setJoinCode] = useState("");
  const [error, setError] = useState("");
  const [joinedTeams, setJoinedTeams] = useState([]);
 
  function resetStates() {
    setJoinCode("");
    setError("");
  }

  const handleJoin = async (team_id, join_code, close) => {
    if(!join_code){
      setError("Join code is required.");
      return;
    }
    try {
      const { data, error } = await toResult(api.post("/api/teams/join", { team_id, join_code}));
      if (error) {
        console.error("Join failed:", error.message);
        setError(error.message);
      }
      else{
        resetStates();
        if (onJoin) onJoin(team, true);
        if (close) close();
      }
    } 
    catch (err) {
      console.error("Unexpected error during join:", err);
    }
  };

  const handleDelete = async () => {
    try {
      const { data, error } = await toResult(api.post(`/api/teams/${team.id}/delete`));
      if (error) {
        setError(error.message || "Failed to delete team");
      } else {
        if (onDelete) onDelete(team);
      }
    } catch (err) {
      setError(err.message || String(err));
    }
  };

  const handleLeave = async () => {
    try {
      const { data, error } = await toResult(api.post(`/api/teams/${team.id}/leave`));
      if (error) {
        setError(error.message || "Failed to leave team");
        console.log(error.message);
      } else {
        console.log("HELLO");
        if (onJoin) onJoin(team, false);
      }
    } catch (err) {
      setError(err.message || String(err));
    }
  };



  return (
    <div className="team-card">
      <div>
        {browseEvents && (
          <p className="meta-topright">
            {isMember ? "Joined" : "\u00A0"}
          </p>
        )}
        <h3>{name || team.Name}</h3>
        {description && (
          <p className="meta">{description}</p>
        )}
        {department && (
          <p className="meta">Dept: {department}</p>
        )}
        {/* Only show join code if user is a member of the team */}
        {(join_code || JoinCode) && showJoinCode && (
          <p className="join-code">Join Code: {join_code || JoinCode}</p>
        )}
      </div>

      {/* Conditional buttons based on user role */}
      <div className="team-card-actions">
        <div className="button-group">
          {isOwner ? <button className="button" onClick={handleDelete}>Delete</button> : null}
          {isOwner || isMember ? <button className="button">View Members</button> : null}
          {!isOwner && isMember ? <button className="button" onClick={handleLeave}>Leave</button> : null}
          {!isMember ? (           
            <Popup trigger={<button className="button primary">Request to Join</button>} modal
              onClose={() => {
                resetStates()
              }}>
              {close => (
                <div className="popup-card">
                  <h3 className="popup-title">Enter Code</h3>
                  {error && <div className="error" role="alert">{error}</div>}
                  <input
                    className='form-input'
                    type="text"
                    placeholder="Code"
                    value={joinCode}
                    onChange={e => setJoinCode(e.target.value)}
                    onKeyPress={e => {
                      if (e.key === 'Enter') {
                        handleJoin(team.id, joinCode, close);
                      }
                    }}
                  />
                  <div className="popup-actions">
                    <button 
                      className="button popup-button-primary" 
                      onClick={async () => { 
                        await handleJoin(team.id, joinCode, close);
                      }}
                    >
                      Submit
                    </button>
                    <button
                      className="button popup-button-secondary"
                      onClick={() => {
                        resetStates()
                        close();
                      }}
                    >
                      Close
                    </button>
                  </div>
                </div>
              )}
            </Popup>
          ) : null}
        </div>
      </div>

    </div>
  );
}