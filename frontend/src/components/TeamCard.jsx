import React from "react";
import "../styles/teamCard.css";

/**
 * TeamCard
 * Reusable UI card for team info.
 * Displays team information including name, description, department,
 * capacity, and join code with conditional buttons based on whether the user is the owner of the team.
 */
export default function TeamCard({ team, isOwner = false, isMember = false, showJoinCode = false }) {
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
        {/* Only show join code if user is a member of the team */}
        {(join_code || JoinCode) && showJoinCode && (
          <p className="join-code">Join Code: {join_code || JoinCode}</p>
        )}
      </div>

      {/* Conditional buttons based on user role */}
      <div className="team-card-actions">
        {isOwner ? (
          <button className="button">View/Manage</button>
        ) : (
          <div className="button-group">
            <button className="button secondary">View</button>
            {!isMember && (
              <button className="button primary">Request to Join</button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
