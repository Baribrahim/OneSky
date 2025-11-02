import React from "react";
import "../../styles/events.css";

function EventRequirements({ requirementsBring, requirementsProvided }) {
    const bring = requirementsBring ? requirementsBring.split(',').map(item => item.trim().charAt(0).toUpperCase() + item.trim().slice(1)) : [];

    const provided = requirementsProvided ? requirementsProvided.split(',').map(item => item.trim().charAt(0).toUpperCase() + item.trim().slice(1)): [];

    return (
        <section className="event-section">

            <h2>Requirements & What to Bring</h2>
            <div className="requirements-container">
                <div className="requirements-section">
                    <h3> ✅ What We Provide:</h3>
                    <ul>
                        {provided.map((item, index) => (
                            <li key={index}>{item.trim()}</li>
                        ))}
                    </ul>
                </div>
            
                <div className="requirements-section">
                    <h3>🎒 Please Bring:</h3>
                    <ul>
                        {bring.map((item, index) => (
                            <li key={index}>{item.trim()}</li>
                        ))}
                    </ul>
                </div>
            </div>
        
        </section>
    );
}

export default EventRequirements;