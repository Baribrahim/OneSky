import React, { useEffect, useMemo, useState } from "react";
import { api, toResult } from "../../lib/apiClient";
import StatCard from "./StatCard";
import CompletedEventsPopup from "../CompletedEventsPopup";
import "../../styles/impact.css";

// Minimal inline icons (no extra deps)
const ClockIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <circle cx="12" cy="12" r="9" />
    <polyline points="12,7 12,12 16,14" />
  </svg>
);

const CheckIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M20 6L9 17l-5-5" />
  </svg>
);

const CalendarIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <rect x="3" y="4" width="18" height="18" rx="2" />
    <line x1="16" y1="2" x2="16" y2="6" />
    <line x1="8" y1="2" x2="8" y2="6" />
    <line x1="3" y1="10" x2="21" y2="10" />
  </svg>
);

const MedalIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <circle cx="12" cy="13" r="5" />
    <path d="M8 3l4 6 4-6" />
  </svg>
);

/**
 * ImpactContainer
 * Displays a compact summary of the user’s volunteering impact.
 * - Fetches /dashboard/impact
 * - Renders four StatCard components
 */
export default function ImpactContainer() {
  // Local state for API data and UI states
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCompletedEventsPopup, setShowCompletedEventsPopup] = useState(false);

  // Fetch dashboard data on mount
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

  // Format hours neatly (e.g., 12h or 12.5h)
  const hoursLabel = useMemo(() => {
    const h = Math.max(0, Number(data?.total_hours ?? 0));
    return `${Number.isFinite(h) ? h.toFixed(h % 1 === 0 ? 0 : 1) : 0} h`;
  }, [data]);

  // Handle completed events card click
  const handleCompletedEventsClick = () => {
    setShowCompletedEventsPopup(true);
  };

  // Predefined stats (keeps JSX declarative)
  const stats = useMemo(() => ([
    { key: "hours", label: "Total Hours", value: hoursLabel, icon: <ClockIcon />, helper: "Completed volunteering time", variant: 'hours' },
    { 
      key: "completed", 
      label: "Completed Events", 
      value: String(data?.events_completed ?? 0), 
      icon: <CheckIcon />, 
      helper: "Events you've completed",
      clickable: true,
      onClick: handleCompletedEventsClick,
      variant: 'completed'
    },
    { key: "upcoming", label: "Upcoming Events",  value: String(data?.counts?.upcoming_events ?? 0), icon: <CalendarIcon />, helper: "Next events you're attending", variant: 'upcoming' },
    { key: "badges", label: "Badges", value: String(data?.counts?.badges ?? 0), icon: <MedalIcon />, helper: "Achievements earned", variant: 'badges' },
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
                variant={s.variant}
                clickable={s.clickable}
                onClick={s.onClick}
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

      {/* Completed Events Popup */}
      <CompletedEventsPopup 
        isOpen={showCompletedEventsPopup}
        onClose={() => setShowCompletedEventsPopup(false)}
      />
    </section>
  );
}
