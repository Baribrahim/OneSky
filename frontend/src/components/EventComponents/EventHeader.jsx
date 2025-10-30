import React, { useEffect, useState } from "react";
import "../../styles/events.css";

function EventHeader({title, causeName, tags}) {
    const tagList =tags? tags.split(',') : [];

    return (
        <header className="event-header">

        <p className="event-cause">{causeName}</p>

        <h1 className="event-title">{title}</h1>

        <div className="event-tags">
            {tagList.map((tag, index) => (
                <span key={index} className="event-tag">{tag}</span>
            ))}
        </div>
        </header>
    )
}

export default EventHeader;