import React, { useEffect, useState } from "react";
import "../../styles/events.css"; // Import your CSS for styling

function EventSchedule({ event }) {
  // State to store the schedule items fetched from the API
  const [schedule, setSchedule] = useState([]);

  // useEffect runs when the component mounts or when event.ID changes
  useEffect(() => {
    async function fetchSchedule() {
      try {
        // Fetch schedule data for this event from your backend
        const response = await fetch(`http://localhost:5000/api/events/events/${event.ID}/schedule`);

        // If the response is not OK, throw an error
        if (!response.ok) {
          throw new Error("Failed to fetch schedule");
        }

        // Convert the response to JSON
        const data = await response.json();

        // Save the fetched schedule data into state
        setSchedule(data);
      } catch (error) {
        // Log any errors that occur during fetch
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
        const suffix = h >= 12 ? "PM" : "AM"; // Determine AM or PM
        const displayHour = h % 12 || 12; // Convert to 12-hour format
        return `${displayHour}:${minute} ${suffix}`;
    };

    return (
        <div className="event-schedule">
        <h3>🕒 Event Schedule</h3>

        {/* If no schedule items, show a message */}
        {schedule.length === 0 ? (
            <p>No schedule available</p>
        ) : (
            // Loop through each schedule item and render it
            schedule.map((item, index) => (
            <div key={index} className="schedule-item">
                <div className="time">{formatTime(item.Time)}</div>

                <div className="details">
                <strong>{item.Title}</strong>
                <p>{item.Description}</p>
                </div>
            </div>
            ))
        )}
        </div>
    );
}

export default EventSchedule;