import React, { useEffect, useState } from "react";
import "../../styles/events.css";

function EventSchedule({ event }) {
  const [schedule, setSchedule] = useState([]);

  // useEffect runs when the component opens or when event.ID changes
  useEffect(() => {
    async function fetchSchedule() {
      try {
        const response = await fetch(`http://35.210.202.5:5001/api/events/events/${event.ID}/schedule`);

        // If the response is not OK, throw an error
        if (!response.ok) {
          throw new Error("Failed to fetch schedule");
        }

        const data = await response.json();

        setSchedule(data);
      } catch (error) {
        console.error(error);
      }
    }

    
    fetchSchedule();
    }, [event.ID]); // Dependency array ensures this runs when event.ID changes

    // format time from "HH:MM:SS" to "12-hour format"
    const formatTime = (time) => {
        if (!time) return "";
        const [hour, minute] = time.split(":"); 
        const h = parseInt(hour, 10);
        const suffix = h >= 12 ? "PM" : "AM";
        const displayHour = h % 12 || 12; // Convert to 12-hour format
        return `${displayHour}:${minute} ${suffix}`;
    };

    return (
       <div className="event-schedule">
            <h2>
                <span className="icon">🕒</span>
                <span className="gradient-text">Event Schedule</span>
            </h2>
            <div className="event-timeline-container">
                <div className="event-timeline"></div>
                <div className="schedule-list">
                {schedule.map((item, index) => (
                    <div key={index} className="schedule-item">
                    <div className="time">{formatTime(item.Time)}</div>
                    <div className="details">
                        <strong>{item.Title}</strong>
                        <p>{item.Description}</p>
                    </div>
                    </div>
                ))}
                </div>
            </div>
        </div>
    );
}

export default EventSchedule;