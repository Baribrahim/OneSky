import React, { useEffect, useMemo, useState } from "react";
import { api, toResult } from "../../lib/apiClient";
import StatCard from "./StatCard";

/**
 * ImpactSection
 * Fetches and displays the user's volunteering impact summary.
 * Data source: GET /dashboard/impact (requires auth).
 *
 * Renders four StatCards (Hours, Completed, Upcoming, Badges).
 * Uses a horizontal flex row on large screens (single line),
 * and wraps to 2 / 1 columns on smaller screens.
 */
export default function ImpactSection() {
  const [data, setData] = useState(null);   // { total_hours, events_completed, counts:{...}, first_name, as_of }
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Fetch impact data once on mount
  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      const { data, error } = await toResult(api.get("/dashboard/impact"));
      if (!active) return;

      if (error) {
        setError(error.message || "Could not load impact data.");
      } else {
        setData(data);
      }
      setLoading(false);
    })();

    return () => { active = false; };
  }, []);

  // Format total hours
  const hoursLabel = useMemo(() => {
    const h = Math.max(0, Number(data?.total_hours ?? 0));
    return `${Number.isFinite(h) ? h.toFixed(h % 1 === 0 ? 0 : 1) : 0} h`;
  }, [data]);

  // Precompute stat definitions
  const stats = useMemo(
    () => [
      {
        key: "hours",
        label: "Total Hours",
        value: hoursLabel,
        icon: "⏱️",
        helper: "Completed volunteering time",
      },
      {
        key: "completed",
        label: "Completed Events",
        value: String(data?.events_completed ?? 0),
        icon: "✅",
        helper: "Events you've finished",
      },
      {
        key: "upcoming",
        label: "Upcoming Events",
        value: String(data?.counts?.upcoming_events ?? 0),
        icon: "📅",
        helper: "Next events you’re attending",
      },
      {
        key: "badges",
        label: "Badges",
        value: String(data?.counts?.badges ?? 0),
        icon: "🏅",
        helper: "Achievements earned",
      },
    ],
    [data, hoursLabel]
  );

  // --- Render states ---
  if (loading) {
    return (
      <div className="card" style={{ padding: 20 }}>
        <p className="helper" aria-busy="true">Loading impact summary...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card" role="alert" style={{ padding: 20 }}>
        <p className="error">{error}</p>
      </div>
    );
  }

  // --- Main UI ---
  return (
    <section aria-labelledby="impact-heading" style={{ marginTop: 24 }}>
      <div style={{ marginBottom: 12 }}>
        <h2 id="impact-heading" style={{ margin: 0 }}>Your Impact</h2>
        {data?.first_name && (
          <p className="helper" style={{ marginTop: 4 }}>
            Great work, {data.first_name}! Here’s your contribution so far.
          </p>
        )}
      </div>

      {/* Horizontal row of cards (single line on large screens) */}
      <div className="impact-row">
        {stats.map((s) => (
          <div key={s.key} className="impact-item">
            <StatCard
              icon={s.icon}
              label={s.label}
              value={s.value}
              helper={s.helper}
            />
          </div>
        ))}
      </div>

      {/* Timestamp */}
      {data?.as_of && (
        <p className="helper" style={{ marginTop: 12 }}>
          As of: {new Date(data.as_of).toLocaleString()}
        </p>
      )}

      {/* Layout styles: row on desktops; wrap on tablets/mobiles */}
      <style>
        {`
          .impact-row {
            display: flex;
            gap: 16px;
            justify-content: space-between;
            flex-wrap: nowrap;           /* keep a single row on large screens */
            overflow-x: auto;            /* allow horizontal scroll if space is tight */
            padding-bottom: 4px;         /* small space for scrollbar overlap */
          }
          .impact-item {
            flex: 0 0 calc(25% - 12px);  /* 4 items per row, evenly spaced */
            min-width: 240px;            /* keeps cards readable on narrower screens */
          }

          /* Medium screens: wrap into 2 columns */
          @media (max-width: 1024px) {
            .impact-row {
              flex-wrap: wrap;
              overflow-x: visible;
            }
            .impact-item {
              flex: 0 0 calc(50% - 8px);
            }
          }

          /* Small screens: stack in a single column */
          @media (max-width: 640px) {
            .impact-item {
              flex: 1 0 100%;
            }
          }
        `}
      </style>
    </section>
  );
}
