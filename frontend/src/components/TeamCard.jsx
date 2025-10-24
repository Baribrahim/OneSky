import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import React, { useEffect, useState } from "react";
import {api, toResult} from '../lib/apiClient.js';
import { useAuth } from '../context/AuthProvider'
import { formatDate, formatTime, timeUnicode } from '../utils/format.jsx';
import Popup from 'reactjs-popup';
//import 'reactjs-popup/dist/index.css';
import '../styles/popup.css';



/** THIS COMPONENT IS ONLY FOR TESTING */

function TeamCard() {
  const [joinCode, setJoinCode] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [joinedTeams, setJoinedTeams] = useState([]);
 
  const fetchStatuses = async () => {
    const { data, error } = await toResult(api.get(`/api/teams/join-status`));
    setJoinedTeams(data);
  };

  //Dummy data remove
  const teams = [
    {id: 1, name: 'Red Dragons'},
    {id: 2, name: 'Blue Hawks'},
    {id: 3, name: 'Golden Wolves'},
    {id: 4, name: 'Silver Foxes'},
  ]

  // //This needs to be changed to use the actual db data
  // useEffect(() => {
  //   if (teams.length > 0) {
  //     fetchStatuses()
  //   }
  // }, [])


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

  // const handleLeave = async (team_id) => {
  //   const { data, error } = await toResult(api.post("api/events/unregister", {event_id}));
  //   if (error) {
  //     console.error("Unregister failed:", error.message);
  //   } 
  //   else {
  //     setSignupEvents(prev => prev.filter(id => id !== event_id)); 
  //   }
    
  // }


  return (
    <>
    <div className="cards-container">
    {teams?.map(team =>
    <div key = {team.id} className="card">
      <div className="card-body">
        <h3 className="card-subtitle mb-2 text-muted">{team.name}</h3>
          <Popup trigger={<button className="button">Join Team</button>} modal
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
  </Popup>
      </div>
    </div>
    )}
    </div>
    </>
  );
}

export default TeamCard;