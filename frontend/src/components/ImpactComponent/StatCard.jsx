import React from "react";
import "../../styles/statCard.css";

/**
 * StatCard
 * ------------------------------------------------------------
 * Square, compact stat card aligned with theme tokens.
 * - Icon, label, big value, helper text
 * - Uses aspect-ratio to remain a square in the grid
 */
export default function StatCard({ icon, label, value, helper }) {
  return (
    <div className="stat-card card">
      <div className="stat-card__icon" aria-hidden="true">{icon}</div>

      <span className="helper stat-card__label">{label}</span>

      <span className="stat-card__value">{value}</span>

      {helper && (
        <span className="helper stat-card__helper">
          {helper}
        </span>
      )}
    </div>
  );
}
