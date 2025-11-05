import React, { useEffect, useState } from "react";
import {api, toResult} from '../lib/apiClient.js';
import { formatDate, formatTime, timeUnicode } from '../utils/format.jsx';
import { Link } from "react-router-dom";
import EventTeamsPopup from "./EventTeamsPopup.jsx";



function EventCard({ event}) {
  const [isSignedUp, setIsSignedUp] = useState(false); //tracks signup for individual event 


  // Fetch signup status for this specific event
  const fetchSignupStatus = async () => {
    const { data, error } = await toResult(api.get("/api/events/signup-status"));
    if (!error && Array.isArray(data)) {
      setIsSignedUp(data.includes(event.ID)); //is this event in the users signup list
    }
  };

  useEffect(() => {
    fetchSignupStatus();
  }, []);

  const handleSignup = async () => {
    const { data, error } = await toResult(api.post("/api/events/signup", { event_id: event.ID }));
    if (!error) {
      setIsSignedUp(true);
      
      // Check for badges after successful signup
      try {
        await api.post("/api/badges/check");
      } catch (err) {
        console.warn("Failed to check badges after signup:", err);
      }
    } else {
      console.error("Signup failed:", error.message);
    }
  };

  const handleUnregister = async () => {
    const { data, error } = await toResult(api.post("/api/events/unregister", { event_id: event.ID }));
    if (!error) {
      setIsSignedUp(false);
    } else {
      console.error("Unregister failed:", error.message);
    }
  };
  // takes the first sentance from the about section from db.
  const firstSentence = event.About.match(/.*?[.!?]/)?.[0] || event.About;

  return (
    <div className="card event-card">
      {/* Clickable area for navigation */}
      <Link to={`/events/${event.ID}`} className="event-card-link">
        <img
          className="event-image"
          src={
            event.Image_path
              ? `http://127.0.0.1:5000/static/${event.Image_path}`
              : `http://127.0.0.1:5000/static/event-images/default-event.jpeg`
          }
          alt={event.Title}
          onError={(e) => {
            e.target.onerror = null;
            e.target.src = `http://127.0.0.1:5000/static/event-images/default-event.jpeg`;
          }}
        />
        
        <div className="card-body">
              <h3>{event.Title}</h3>
              <p>{firstSentence}</p>
              <div className="event-info">
                <p>
                  📍{event.Address}, {event.LocationCity}
                  <br />
                  {event.LocationPostcode}
                </p>
                <p>📅 {formatDate(event.Date)}</p>
                <p>{timeUnicode(event.StartTime)} {formatTime(event.StartTime)} - {formatTime(event.EndTime)}</p>
                <p>👥 {event.Capacity}</p>
              </div>
            </div>
        </Link>

      {/* Buttons */}
      <div className="event-actions">
        {isSignedUp ? (
          <button className="button inverse" onClick={handleUnregister}>Unregister</button>
        ) : (
          <button className="button" onClick={handleSignup}>👤 Register</button>
        )}
        <EventTeamsPopup eventID={event.ID} />
      </div>
    </div>


  );
}

export default EventCard;