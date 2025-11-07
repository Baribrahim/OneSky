import React from "react";
import { useNavigate } from "react-router";
import TeamCard from "./TeamCard";
import "../styles/myTeams.css";

export default function MyTeams({ teams = [], loading = false, error = "" }) {
  const navigate = useNavigate();
  const handleCreateTeam = () => {
    navigate("/teams/new");
  };

  return (
    <section className="my-teams-section" aria-labelledby="my-teams-heading">
      <div className="my-teams-inner card">
        <div className="my-teams-header">
          <div className="my-teams-title-section">
            <h2 className="event-title">My Teams</h2>
            <p className="filter-tagline">Track your team involvement and manage your memberships.</p>
          </div>
        </div>

        {/* Stats Section - Placeholder */}
        <div className="my-teams-stats">
          <div className="stat-item">
            <div className="stat-value">{teams.length}</div>
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

        {/* My Teams Grid */}
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

          {/* Loading / Error / Empty states */}
          {loading && <p className="filter-tagline">Loading your teams...</p>}
          {error && <p className="error" role="alert">{error}</p>}
          {!loading && !error && teams.length === 0 && (
            <p className="filter-tagline">You haven't joined any teams yet.</p>
          )}

          {/* Teams grid */}
          <div className="my-teams-grid">
            {!loading && !error && teams.map(team => (
              <TeamCard 
                key={team.id || team.ID}
                team={team}
                isOwner={team.is_owner}
                isMember={true}
                showJoinCode={true}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
