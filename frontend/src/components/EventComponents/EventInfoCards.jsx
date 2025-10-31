import React from "react";
import "../../styles/events.css";

function EventInfoCards({ date, startTime, endTime, location, capacity}) {
    // formate the date
    const formattedDate = new Date(date).toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    });

    // formate the time
    const formatTime = (time) => {
        if (!time) return '';
        const [hour, minute] = time.split(':').slice(0, 2);
        const h = parseInt (hour, 10);
        const suffix = h >=12 ? 'PM' : 'AM';
        const displayHour = h % 12 || 12;
        return `${displayHour}:${minute} ${suffix}`;
    };

    return (
        <div className="event-info-cards">
            <div className="info-card">
                <h4>Date</h4>
                <p>{formattedDate}</p>
            </div>

            <div className="info-card">
                <h4>Time</h4>
                <p>{formatTime(startTime)} - {formatTime(endTime)}</p> 
            </div>

            <div className="info-card">
                <h4>Capacity</h4>
                <p>{capacity} spots</p>
            </div>
        </div>
    );

}

export default EventInfoCards;