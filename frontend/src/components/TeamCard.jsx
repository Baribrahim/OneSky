import React from "react";
import "../styles/teamCard.css";

/**
 * TeamCard
 * -------------------------------------------
 * Reusable UI card for team info.
 * Displays team information including name, description, department,
 * capacity, and join code with a "Request to Join" button.
 */
export default function TeamCard({ team }) {
  const { name, description, department, capacity, join_code, JoinCode } = team;

  return (
    <div className="team-card">
      <div>
        <h3>{name || team.Name}</h3>
        {description && (
          <p className="meta">{description}</p>
        )}
        {department && (
          <p className="meta">Dept: {department}</p>
        )}
        {capacity && (
          <p className="meta">Capacity: {capacity}</p>
        )}
        {(join_code || JoinCode) && (
          <p className="join-code">Join Code: {join_code || JoinCode}</p>
        )}
      </div>

      {/* Placeholder for later "Request to Join" button */}
      <button className="button">Request to Join</button>
    </div>
  );
}
