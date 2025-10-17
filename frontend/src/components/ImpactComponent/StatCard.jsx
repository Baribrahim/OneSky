import React from "react";

/**
 * StatCard
 * A small reusable card that displays:
 *   - icon (emoji or image)
 *   - label (title)
 *   - value (main metric)
 *   - helper (optional subtext)
 *
 * Used by ImpactSection, but can be reused anywhere
 * that needs to show a stat summary.
 */
export default function StatCard({ icon, label, value, helper }) {
  return (
    <div className="card" style={{ padding: 20, display: "flex", flexDirection: "column" }}>
      {/* Icon */}
      <div
        aria-hidden="true"
        style={{
          width: 44,
          height: 44,
          borderRadius: 12,
          background: "var(--brand-primary-050)",
          color: "var(--brand-primary)",
          display: "grid",
          placeItems: "center",
          fontSize: 22,
          marginBottom: 12,
        }}
      >
        {icon}
      </div>

      {/* Label */}
      <span className="helper" style={{ fontWeight: 600 }}>{label}</span>

      {/* Value */}
      <span style={{ fontSize: 28, fontWeight: 700, marginTop: 6 }}>
        {value}
      </span>

      {/* Helper text */}
      {helper && (
        <span className="helper" style={{ marginTop: 8 }}>
          {helper}
        </span>
      )}
    </div>
  );
}
