import React from "react";
import { useNavigate } from "react-router";
import "../styles/myTeams.css";

/**
 * MyTeams
 * -------------------------------------------
 * Section showing user's team statistics and their joined teams.
 * Displays stats about teams joined, hours volunteered, and events completed.
 * Shows team cards for user's teams with view/manage buttons.
 */
export default function MyTeams() {
  const navigate = useNavigate();

  const handleCreateTeam = () => {
    navigate("/teams/new");
  };

  return (
    <section className="my-teams-section" aria-labelledby="my-teams-heading">
        <div className="my-teams-inner card">
          <div className="my-teams-header">
            <div className="my-teams-title-section">
              <h2 className="brand-gradient">
                My Teams
              </h2>
              <p className="filter-tagline">
                Track your team involvement and manage your memberships.
              </p>
            </div>
          </div>

    
        {/* Stats Section - Placeholder */}
        <div className="my-teams-stats">
          <div className="stat-item">
            <div className="stat-value">3</div>
            <div className="stat-label">Teams Joined</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">47</div>
            <div className="stat-label">Hours Volunteered</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">12</div>
            <div className="stat-label">Events Completed</div>
          </div>
        </div>

        {/* My Teams Grid - Placeholder */}
        <div className="my-teams-content">
          <div className="my-teams-content-header">
            <h3 style={{ marginBottom: 16, fontSize: "1.1rem" }}>My Team Memberships</h3>
            <button 
              className="button small" 
              onClick={handleCreateTeam}
              aria-label="Create a new team"
            >
              Create Team
            </button>
          </div>
          <div className="my-teams-grid">
            {/* Placeholder team cards will go here */}
            <div className="placeholder-card">
              <p className="meta">Your joined teams will appear here</p>
              <p className="meta">Each team card will have View and Manage buttons</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
