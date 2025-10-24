import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import React, { useEffect, useState } from "react";
import {api, toResult} from '../lib/apiClient.js';
import { useAuth } from '../context/AuthProvider'
import { formatDate, formatTime, timeUnicode } from '../utils/format.jsx';
import Popup from 'reactjs-popup';
//import 'reactjs-popup/dist/index.css';
import '../styles/popup.css';
import "../styles/teamCard.css";


/** THIS COMPONENT IS ONLY FOR TESTING */

  // //This needs to be changed to use the actual db data
  // useEffect(() => {
  //   if (teams.length > 0) {
  //     fetchStatuses()
  //   }
  // }, [])






  // const handleLeave = async (team_id) => {
  //   const { data, error } = await toResult(api.post("api/events/unregister", {event_id}));
  //   if (error) {
  //     console.error("Unregister failed:", error.message);
  //   } 
  //   else {
  //     setSignupEvents(prev => prev.filter(id => id !== event_id)); 
  //   }
    
  // }





/**
 * TeamCard
 * Reusable UI card for team info.
 * Displays team information including name, description, department,
 * capacity, and join code with conditional buttons based on whether the user is the owner of the team.
 */
export default function TeamCard({ team, isOwner = false, isMember = false, showJoinCode = false }) {
  const { name, description, department, capacity, join_code, JoinCode } = team;
  const [joinCode, setJoinCode] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [joinedTeams, setJoinedTeams] = useState([]);
 
  const fetchStatuses = async () => {
    const { data, error } = await toResult(api.get(`/api/teams/join-status`));
    setJoinedTeams(data);
  };

  function resetStates() {
    setJoinCode("");
    setError("");
    setSuccess("");
  }

  const handleJoin = async (team_id, join_code) => {
    if(!join_code){
      setError("Join code is required.");
      return;
    }
    try {
      const { data, error } = await toResult(api.post("api/teams/join", { team_id, join_code}));
      if (error) {
        console.error("Join failed:", error.message);
        setError(error.message);
      }
      else{
        console.log("DATA", data)
        setSuccess("Successfully joined!");
        //setJoinedTeams(prev => ([...prev, team_id])); 
      }
    } 
    catch (err) {
      console.error("Unexpected error during join:", err);
    }
  };


  return (
    <div className="team-card">
      <div>
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
      <div className="card">
        <div className="content">
            <p>Enter Code </p>
            {error && <div className="error" role="alert">{error}</div>}
            {success && <div className="success" role="alert">{success}</div>}
            <input
              className='form-input'
              type="text"
              placeholder="Code"
              onChange={e => setJoinCode(e.target.value)}
            />
        
        <div className="actions">
            <button className="button" onClick={ async () => { await handleJoin(team.id, joinCode);
            }}>
            Submit
            </button>
          <button
            className="button"
            onClick={() => {
              resetStates()
              close();
            }}
          >
            Close
          </button>
        </div>
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
