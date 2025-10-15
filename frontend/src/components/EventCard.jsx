import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import React, { useEffect, useState } from "react";
import {api, toResult} from '../lib/apiClient.js';
import { useAuth } from '../context/AuthProvider'

function EventCard() {
  const [events, setEvents] = useState([]);
  const {user} = useAuth();
  const [signupEvents, setSignupEvents] = useState([]);

  const fetchEvents = async () => {
    try {
      const { data, error } = await toResult(api.get("/api/events"));
      
      if (error || !Array.isArray(data)) {
        console.warn("Not authenticated", data);
        setEvents([]); 
        return;
      }
      setEvents(data);
    } catch (error) {
      console.error("Error fetching events:", error);
      setEvents([]);
    }
  };


  const fetchStatuses = async () => {
    const { data, error } = await toResult(api.get(`/api/events/signup-status`));
    setSignupEvents(data);
    console.log("Fetched signup statuses:", signupEvents);
    console.log(signupEvents[3] ? "User signed up for event 3" : "User not signed up for event 3")
  };


  useEffect(() => {
    fetchEvents();
  }, []);

  useEffect(() => {
    if (events.length > 0) {
      fetchStatuses()
    }
  }, [events])

  //Debugging     
  useEffect(() => {
    console.log("Updated events:", events);
    console.log(Array.isArray(events) ? "events is an array" : "events is not an array");
  }, [events]);


  function formatDate(dateString) {
    const date = new Date(dateString);

    const months = [
      'Jan', 'Feb', 'March', 'April', 'May', 'June',
      'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'
    ];

    const day = date.getDate();
    const month = months[date.getMonth()];
    const year = date.getFullYear();

    const getOrdinal = (n) => {
      const s = ["th", "st", "nd", "rd"],
            v = n % 100;
      return s[(v - 20) % 10] || s[v] || s[0];
    };

    return `${month} ${day}${getOrdinal(day)} ${year}`;
  }

  function timeUnicode(time) {
      const unicode_clocks = [
      '\u{1F55B}',
      '\u{1F550}',
      '\u{1F551}',
      '\u{1F552}',
      '\u{1F553}',
      '\u{1F554}',
      '\u{1F555}',
      '\u{1F556}',
      '\u{1F557}',
      '\u{1F558}',
      '\u{1F559}',
      '\u{1F55A}',
    ];
    
    const hour = parseInt(time.slice(0,2)) % 12

    return unicode_clocks[hour]

  }


  function formatTime(time) {
    return time.length == 7 ? time.slice(0, 4) : time.slice(0, 5)
  }


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
                      <button className="button" disabled>
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
