import React, { useEffect, useState } from "react";
import {api, toResult} from '../lib/apiClient.js';
import { formatDate, formatTime, timeUnicode } from '../utils/format.jsx';
import { Link } from "react-router-dom";


// I have changed eventCard so that it represents an individual event and no longer fetches all events. The event card now only handles signup/unregister. This means that the events page(parent) handles the filtering and fetching, and eventcard(child) handles the display and interaction. 

function EventCard({ event }) {
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
     <Link to={`/events/${event.ID}`} className="card event-card">
      <div className="card event-card">
        {/* When we depoloy this, update the URL to match backend domain/ api base url */}
        <img className='event-image' src={`http://127.0.0.1:5000/static/${event.Image_path}`}
            alt={event.Title}
          />
        <div className="card-body">
          <h3 className="card-subtitle mb-2 text-muted">{event.Title}</h3>
          <p className="card-text">{firstSentence}</p>
          <div className="event-info">
            <div className='event-location'>
              <span role="img" aria-label="location">{'\u{1F4CD}'}</span>
              {event.Address}, {event.LocationCity}, {event.LocationPostcode}
            </div>

            <p className="card-text">{'\u{1F4C5}'} {formatDate(event.Date)}</p>
            <p className="card-text">
              {timeUnicode(event.StartTime)} {formatTime(event.StartTime)} - {formatTime(event.EndTime)}
            </p>
            <p className="card-text">{'\u{1F465}'} {event.Capacity}</p>
          </div>

          {isSignedUp ? (
            <button className="button inverse" onClick={handleUnregister}>
              Unregister
            </button>
          ) : (
            <button className="button" onClick={handleSignup}>
              Register
            </button>
          )}
        </div>
      </div>
    </Link>
  );
}

export default EventCard;