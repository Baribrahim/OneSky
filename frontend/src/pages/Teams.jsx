import React, { useEffect, useState } from "react";
import { api, toResult } from "../lib/apiClient";
import TeamCard from "../components/TeamCard";
import MyTeams from "../components/MyTeams";
import "../styles/teams.css";

/**
 * Teams Page
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
    <>
      {/* My Teams Section */}
      <MyTeams />

      {/* Browse Teams Section */}
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
              <TeamCard 
                key={t.id || t.ID} 
                team={t} 
                isOwner={false} // TODO: Replace with actual ownership check from backend
                isMember={false} // TODO: Replace with actual membership check from backend
                showJoinCode={false} // TODO: Replace with actual membership check from backend
              />
            ))}
          </div>
        )}
      </div>
      </section>
    </>
  );
}
