import React, { useEffect, useState } from "react";
import {api, toResult} from '../lib/apiClient.js';
import Popup from 'reactjs-popup';
import '../styles/popup.css';
import "../styles/teamCard.css";

/**
 * TeamCard
 * Reusable UI card for team info.
 * Displays team information including name, description, department,
 * capacity, and join code with conditional buttons based on whether the user is the owner of the team.
 */
export default function TeamCard({ team, isOwner = false, isMember = false, showJoinCode = false, onJoin, browseEvents = false }) {
  const { name, description, department, capacity, join_code, JoinCode } = team;
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
        if (onJoin) onJoin(team);
        if (close) close();
      }
    } 
    catch (err) {
      console.error("Unexpected error during join:", err);
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
        {capacity && (
          <p className="meta">Capacity: {capacity}</p>
        )}
        {/* Only show join code if user is a member of the team */}
        {(join_code || JoinCode) && showJoinCode && (
          <p className="join-code">Join Code: {join_code || JoinCode}</p>
        )}
      </div>

      {/* Conditional buttons based on user role */}
      <div className="team-card-actions">
        {isOwner ? (
          <button className="button">View/Manage</button>
        ) : (
          <div className="button-group">
            <button className="button secondary">View</button>
            {!isMember && (           
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
  </Popup>)}


          </div>
        )}
      </div>
    </div>
  );
}