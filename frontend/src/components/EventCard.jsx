import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import React, { useEffect, useState } from "react";
import {api, toResult} from '../lib/apiClient.js';
import { useAuth } from '../context/AuthProvider'
import { formatDate, formatTime, timeUnicode } from '../utils/format.jsx';

function EventCard() {
  const [events, setEvents] = useState([]);
  const {user} = useAuth();
  const [signupEvents, setSignupEvents] = useState([]);

  const fetchEvents = async () => {
    try {
      const { data, error } = await toResult(api.get("/api/events"));
      
      if (error || !Array.isArray(data)) {
        console.warn("Not authenticated", data);
        return;
      }
      setEvents(data);
    } catch (error) {
      console.error("Error fetching events:", error);
    }
  };


  const fetchStatuses = async () => {
    const { data, error } = await toResult(api.get(`/api/events/signup-status`));
    setSignupEvents(data);
    console.log("Fetched signup statuses:", signupEvents);
  };


  useEffect(() => {
    fetchEvents();
  }, []);

  useEffect(() => {
    if (events.length > 0) {
      fetchStatuses()
    }
  }, [events])

  // //Debugging     
  // useEffect(() => {
  //   console.log("Updated events:", events);
  //   console.log(Array.isArray(events) ? "events is an array" : "events is not an array");
  // }, [events]);

  const handleSignup = async (event_id) => {
    try {
      const { data, error } = await toResult(api.post("api/events/signup", { event_id}));
      if (error) {
        console.error("Signup failed:", error.message);
      } 
      else {
        setSignupEvents(prev => ([...prev, event_id])); 
      }
    } 
    catch (err) {
      console.error("Unexpected error during signup:", err);
    }
  };

  const handleUnregister = async (event_id) => {
    const { data, error } = await toResult(api.post("api/events/unregister", {event_id}));
    if (error) {
      console.error("Unregister failed:", error.message);
    } 
    else {
      setSignupEvents(prev => prev.filter(id => id !== event_id)); 
    }
    
  }


  return (
    <>
    <div className="cards-container">
    {events?.map(events =>
    <div key = {events.ID} className="card">
      <div className="card-body">
        <h3 className="card-subtitle mb-2 text-muted">{events.Title}</h3>
        <p className="card-text">{events.About}</p>
        <div className="event-info">
        <p className="card-text">{'\u{1F4CD}'} {events.LocationCity}</p> 
        <p className="card-text">{'\u{1F4C5}'} {formatDate(events.Date)}</p>
        <p className="card-text">{timeUnicode(events.StartTime)} {formatTime(events.StartTime)} - {formatTime(events.EndTime)}</p>
        <p className="card-text">{'\u{1F465}'} {events.Capacity}</p>
        </div> 
        {signupEvents.includes(events.ID)? (
                      <button className="button inverse" onClick={() => handleUnregister(events.ID)}>
                        Unregister
                      </button>
                    ) : (
                      <button className="button" onClick={() => handleSignup(events.ID)}>
                        Sign Up
                      </button>
        )}
      </div>
    </div>
    )}
    </div>
    </>
  );
}

export default EventCard;
