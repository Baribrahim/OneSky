import React, { useEffect, useMemo, useState } from "react";
import { api, toResult } from "../../lib/apiClient";
import StatCard from "./StatCard";
import "../../styles/impact.css";

/**
 * ImpactContainer
 * ------------------------------------------------------------
 * Displays a compact summary of the user’s volunteering impact.
 * - Fetches /dashboard/impact
 * - Renders four StatCard components
 * - Uses a clean centered layout with balanced spacing (4 → 2 → 1)
 */
export default function ImpactContainer() {
  // --- Local state for API data and UI states ---
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // --- Fetch dashboard data on mount ---
  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      const { data, error } = await toResult(api.get("/dashboard/impact"));
      if (!active) return;
      error ? setError(error.message || "Could not load impact data.") : setData(data);
      setLoading(false);
    })();
    return () => { active = false; };
  }, []);

  // --- Format hours neatly (e.g., 12h or 12.5h) ---
  const hoursLabel = useMemo(() => {
    const h = Math.max(0, Number(data?.total_hours ?? 0));
    return `${Number.isFinite(h) ? h.toFixed(h % 1 === 0 ? 0 : 1) : 0} h`;
  }, [data]);

  // --- Predefined stats (keeps JSX declarative) ---
  const stats = useMemo(() => ([
    { key: "hours",     label: "Total Hours",      value: hoursLabel,                           icon: "⏱️", helper: "Completed volunteering time" },
    { key: "completed", label: "Completed Events", value: String(data?.events_completed ?? 0),  icon: "✅", helper: "Events you've finished" },
    { key: "upcoming",  label: "Upcoming Events",  value: String(data?.counts?.upcoming_events ?? 0), icon: "📅", helper: "Next events you're attending" },
    { key: "badges",    label: "Badges",           value: String(data?.counts?.badges ?? 0),    icon: "🏅", helper: "Achievements earned" },
  ]), [data, hoursLabel]);

  return (
    <section className="impact" aria-labelledby="impact-heading">
      <div className="impact__inner">
        {/* Section heading and intro */}
        <div className="impact__header">
          <h2 id="impact-heading" style={{ margin: 0 }}>Your Impact</h2>
          <p className="helper" style={{ marginTop: 4 }}>
            {data?.first_name
              ? `Great work, ${data.first_name}! Here's your contribution so far.`
              : "Here’s your contribution so far."}
          </p>
        </div>

        {/* Loading / error / data states */}
        {loading && (
          <div className="card impact__status">
            <p className="helper" aria-busy="true">Loading impact summary...</p>
          </div>
        )}
        {error && !loading && (
          <div className="card impact__status" role="alert">
            <p className="error">{error}</p>
          </div>
        )}

        {!loading && !error && (
          <div className="impact__grid">
            {stats.map((s) => (
              <StatCard
                key={s.key}
                icon={s.icon}
                label={s.label}
                value={s.value}
                helper={s.helper}
              />
            ))}
          </div>
        )}

        {/* Timestamp */}
        {data?.as_of && !loading && !error && (
          <p className="helper impact__timestamp">
            As of: {new Date(data.as_of).toLocaleString()}
          </p>
        )}
      </div>
    </section>
  );
}
