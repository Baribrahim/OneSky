import React from "react";
import "../../styles/events.css";

function EventInfoCards({ date, startTime, endTime, location, address, locationPostCode, capacity, causeName}) {
    // formate the date
    const formattedDate = new Date(date).toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    });

    // formate the time
    const formatTime = (time) => {
        if (!time) return ''; // If time is undefined, return empty string
        const [hour, minute] = time.split(':');
        const h = parseInt (hour, 10);
        const suffix = h >=12 ? 'PM' : 'AM';
        const displayHour = h % 12 || 12;
        return `${displayHour}:${minute} ${suffix}`;
    };

    return (
        <div className="event-info-cards">
            <div className="info-card">
                <h4>Date & Time</h4>
                <p>{formattedDate}</p>
           <    p>{formatTime(startTime)} - {formatTime(endTime)}</p> 
            </div>

            <div className="info-card">
                <h4>Location</h4>
                <p>{address}, {location}, {locationPostCode} </p>
            </div>

            <div className="info-card">
                <h4>Capacity</h4>
                <p>{capacity} Volunteers Maximum</p>
            </div>

            <div className="info-card">
                <h4>Cause</h4>
                <p> {causeName} </p>
            </div>
        </div>
    );
}

export default EventInfoCards;