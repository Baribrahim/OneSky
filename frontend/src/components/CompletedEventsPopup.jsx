import React, { useEffect, useState } from "react";
import { api, toResult } from "../lib/apiClient";
import "../styles/completedEventsPopup.css";

/**
 * CompletedEventsPopup
 * Modal popup that displays a list of completed events when user clicks on the completed events card.
 */
export default function CompletedEventsPopup({ isOpen, onClose }) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Fetch completed events when popup opens
  useEffect(() => {
    if (!isOpen) return;

    let active = true;
    (async () => {
      setLoading(true);
      setError("");
      const { data, error } = await toResult(api.get("/dashboard/completed-events"));
      if (!active) return;
      
      if (error) {
        setError(error.message || "Could not load completed events.");
      } else {
        setEvents(data?.completed_events || []);
      }
      setLoading(false);
    })();

    return () => { active = false; };
  }, [isOpen]);

  // Close popup when clicking outside or pressing Escape
  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e) => {
      if (e.key === "Escape") onClose();
    };

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose]);

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) onClose();
  };

  const formatDate = (dateStr) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric"
      });
    } catch {
      return dateStr;
    }
  };

  const formatTime = (timeStr) => {
    try {
      const [hours, minutes] = timeStr.split(":");
      const hour = parseInt(hours);
      const ampm = hour >= 12 ? "PM" : "AM";
      const displayHour = hour % 12 || 12;
      return `${displayHour}:${minutes} ${ampm}`;
    } catch {
      return timeStr;
    }
  };

  const formatDuration = (hours) => {
    if (!hours) return "N/A";
    const h = parseFloat(hours);
    if (h < 1) {
      return `${Math.round(h * 60)}m`;
    }
    return `${h.toFixed(1)}h`;
  };

  const formatLocation = (event) => {
    const parts = [];
    if (event.Address) parts.push(event.Address);
    if (event.LocationCity) parts.push(event.LocationCity);
    if (event.LocationPostcode) parts.push(event.LocationPostcode);
    return parts.join(", ") || "Location not specified";
  };

  if (!isOpen) return null;

  return (
    <div className="popup-backdrop" onClick={handleBackdropClick}>
      <div className="popup-content">
        <div className="popup-header">
          <h2>Completed Events</h2>
          <button 
            className="popup-close" 
            onClick={onClose}
            aria-label="Close popup"
          >
            ×
          </button>
        </div>

        <div className="popup-body">
          {loading && (
            <div className="popup-loading">
              <p>Loading completed events...</p>
            </div>
          )}

          {error && !loading && (
            <div className="popup-error" role="alert">
              <p>{error}</p>
            </div>
          )}

          {!loading && !error && events.length === 0 && (
            <div className="popup-empty">
              <p>No completed events found.</p>
            </div>
          )}

          {!loading && !error && events.length > 0 && (
            <div className="events-list">
              {events.map((event) => (
                <div key={event.ID} className="event-item">
                  <div className="event-header">
                    <h2>{event.Title}</h2>
                    <span className="event-duration">{formatDuration(event.DurationHours)}</span>
                  </div>
                  
                  <div className="event-details">
                    <div className="event-date">
                      <span className="event-label">Date:</span>
                      <span>{formatDate(event.Date)}</span>
                    </div>
                    
                    <div className="event-time">
                      <span className="event-label">Time:</span>
                      <span>{formatTime(event.StartTime)} - {formatTime(event.EndTime)}</span>
                    </div>
                    
                    <div className="event-location">
                      <span className="event-label">Location:</span>
                      <span>{formatLocation(event)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
