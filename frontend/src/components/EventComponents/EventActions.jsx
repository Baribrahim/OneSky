import React, { useEffect, useState } from "react";
import {api, toResult} from '../../lib/apiClient.js';
import EventTeamsPopup from "../EventTeamsPopup.jsx";
import "../../styles/events.css";

function EventActions({ event }) {
  const [isSignedUp, setIsSignedUp] = useState(false);

  const fetchSignupStatus = async () => {
    const { data, error } = await toResult(api.get("/api/events/signup-status"));
    if (!error && Array.isArray(data)) {
      setIsSignedUp(data.includes(event.ID));
    }
  };

  useEffect(() => {
    fetchSignupStatus();
  }, []);

  const handleSignup = async () => {
    const { data, error } = await toResult(api.post("/api/events/signup", { event_id: event.ID }));
    if (!error) {
      setIsSignedUp(true);
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

  return (
    <div>
      {isSignedUp ? (
        <button className="button inverse" onClick={handleUnregister}>
          Unregister
        </button>
      ) : (
        <button className="button" onClick={handleSignup}>
          👤 Register
        </button>
      )}
      <EventTeamsPopup eventID={event.ID}></EventTeamsPopup>
    </div>
  );
}

export default EventActions;
