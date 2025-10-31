import React from "react";
import "../../styles/events.css";

function EventDescription({ about}) {
    return (
        <section className="event-description">
            <h2>About This Event</h2>
            <p>{about}</p>
        </section>
    )
}
export default EventDescription