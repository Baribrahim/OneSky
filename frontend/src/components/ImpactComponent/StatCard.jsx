import React from "react";
import "../../styles/statCard.css";

/**
 * StatCard
 * Square, compact stat card.
 * - Icon, label, big value, helper text
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
