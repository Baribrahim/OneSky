import React from "react";
import "../../styles/events.css";

function EventRequirements({ requirements }) {
    //splits the requirements into two arrays
    let provided = [];
    let bring = [];

    if (requirements) {
        const parts = requirements.split('|');
        const providedPart = parts [0]?.replace('What We Provide:', '').trim();
        const bringPart = parts [1]?.replace('What to Bring:', '').trim();

        provided = providedPart ? providedPart.split(',') : [];
        bring = bringPart ? bringPart.split(',') : [];
    }

    return (
        <section className="event-section">

            <h2>Requirements</h2>
            <div className="requirements-container">
                <div className="requirements-section">
                    <h3>What We Provide</h3>
                    <ul>
                        {provided.map((item, index) => (
                            <li key={index}>{item.trim()}</li>
                        ))}
                    </ul>
                </div>
            
                <div className="requirements-section">
                    <h3>Please Bring</h3>
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