import React from "react";
import "../../styles/events.css";
import EventActions from "./EventActions.jsx";
import EventHeader from "./EventHeader.jsx";


function EventInfoCards({ date, startTime, endTime, location, address, locationPostCode, capacity, causeName, event, title, tags}) {
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
        <div className="event-info-cards-wrapper">
            <EventHeader
                title={event.Title}
                tags={event.TagName}
            />
            <div className="event-info-card">
                <div className="info-item">
                    <h4>Date & Time</h4>
                    <p>{formattedDate}</p>
                    <p>{formatTime(startTime)} - {formatTime(endTime)}</p> 
                </div>

                <div className="info-item">
                    <h4>Location</h4>
                    <p>
                        {address}, {location}
                        <br />
                        {locationPostCode} 
                    </p>
                </div>

                <div className="info-item">
                    <h4>Capacity</h4>
                    <p>{capacity} Volunteers Maximum</p>
                </div>

                <div className="info-item">
                    <h4> Associated Cause</h4>
                    <p> {causeName} </p>
                </div>
            </div>
            <EventActions event={event} />
        </div>
    );
}

export default EventInfoCards;