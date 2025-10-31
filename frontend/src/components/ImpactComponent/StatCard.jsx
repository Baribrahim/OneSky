import React from "react";
import "../../styles/statCard.css";

/**
 * StatCard
 * Square, compact stat card.
 * - Icon, label, big value, helper text
 * - Optional onClick handler for interactive cards
 */
export default function StatCard({ icon, label, value, helper, onClick, clickable = false, variant }) {
  const variantClass = variant ? `stat-card--${variant}` : '';
  const cardClasses = `stat-card card ${clickable ? 'stat-card--clickable' : ''} ${variantClass}`;
  
  return (
    <div 
      className={cardClasses}
      onClick={onClick}
      role={clickable ? "button" : undefined}
      tabIndex={clickable ? 0 : undefined}
      onKeyDown={clickable ? (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick?.();
        }
      } : undefined}
    >
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
