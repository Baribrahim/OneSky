import React from "react";
import "../../styles/events.css";

function EventActivities({ activities}) {
    const activityList = activities ? activities.split(',') : []

    return (
        <section className="event-section">
            <h2>What You'll Be Doing</h2>
            <ul>
                {activityList.map((activity, index) => (
                    <li key={index}> {activity.trim()}</li>
                ))}
            </ul>
        </section>
    )
}
export default EventActivities;