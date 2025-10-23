import React, { useEffect, useState } from "react";
import { api, toResult } from "../lib/apiClient";

/**
 * Teams Page (US2)
 * ------------------------------------------------------------
 * Displays all existing teams for browsing.
 * - Fetches data from GET /teams (requires auth)
 * - Shows cards in a responsive grid
 * - Handles loading, empty, and error states
 */
export default function Teams() {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // --- Fetch teams once on mount ---
  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      const { data, error } = await toResult(api.get("/teams"));
      if (!active) return;

      if (error) {
        setError(error.message || "Could not load teams.");
      } else if (data?.teams || data?.data?.items) {
        // support both {teams:[]} or {data:{items:[]}} formats
        setTeams(data.teams || data.data.items || []);
      }
      setLoading(false);
    })();
    return () => { active = false; };
  }, []);

  // --- UI rendering ---
  return (
    <section className="teams-section" aria-labelledby="teams-heading">
      <div className="teams-inner card">
        <h2 className="brand-gradient" id="teams-heading" style={{ margin: 0 }}>Browse Teams</h2>
        <p className="filter-tagline" style={{ marginTop: 4 }}>
          Explore all active teams below.
        </p>

        {/* Loading state */}
        {loading && <p className="filter-tagline" aria-busy="true">Loading teams...</p>}

        {/* Error state */}
        {error && !loading && (
          <p className="error" role="alert">{error}</p>
        )}

        {/* Empty state */}
        {!loading && !error && teams.length === 0 && (
          <p className="filter-tagline">No teams found.</p>
        )}

        {/* Teams grid */}
        {!loading && !error && teams.length > 0 && (
          <div className="teams-grid">
            {teams.map((t) => (
              <TeamCard key={t.id || t.ID} team={t} />
            ))}
          </div>
        )}
      </div>

      {/* --- Scoped styles --- */}
      <style>{`
        .teams-section {
          padding: 32px 16px;
          background: var(--color-surface-alt, #f9fafb);
        }

        .teams-inner {
          max-width: 1100px;
          margin: 0 auto;
          padding: 24px;
          border-radius: 12px;
        }

        .teams-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
          gap: 20px;
          margin-top: 20px;
        }

        .team-card {
          background: var(--surface, #fff);
          border: 1px solid var(--border, #e5e7eb);
          border-radius: 10px;
          box-shadow: var(--shadow-1, 0 1px 2px rgba(0,0,0,0.04));
          padding: 20px;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          transition: transform 0.15s ease, box-shadow 0.15s ease;
        }

        .team-card:hover {
          transform: translateY(-2px);
          box-shadow: var(--shadow-2, 0 2px 6px rgba(0,0,0,0.06));
        }

        .team-card h3 {
          font-size: 1.1rem;
          margin-bottom: 6px;
        }

        .team-card .meta {
          font-size: 0.9rem;
          color: var(--color-text-muted, #6b7280);
        }

        .team-card .join-code {
          margin-top: 8px;
          font-family: monospace;
          font-weight: 600;
          letter-spacing: 1px;
          color: var(--brand-primary);
        }

        .team-card .button {
          align-self: flex-start;
          margin-top: 12px;
        }
      `}</style>
    </section>
  );
}

/**
 * TeamCard
 * -------------------------------------------
 * Reusable UI card for team info.
 */
function TeamCard({ team }) {
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

      {/* Placeholder for later “Request to Join” button */}
      <button className="button">Request to Join</button>
    </div>
  );
}
