import React from "react";
import SkyBrand from "../SkyBrand";

/**
 * FormCard
 * Centers a card on the page (mobile-friendly) with optional header (logo + title + subtitle).
 * Props:
 *  - title, subtitle (strings)
 *  - showBrand (bool) -> shows SkyBrand centered above title
 *  - children -> form/content
 */
export default function FormCard({
  title,
  subtitle,
  showBrand = true,
  children,
}) {
  return (
    <div className="container" style={{ display: "grid", placeItems: "center" }}>
      <div className="card" style={{ width: "100%", maxWidth: 520 }}>
        {showBrand && (
          <div style={{ display: "flex", justifyContent: "center", marginBottom: 16 }}>
            <SkyBrand size={56} />
          </div>
        )}
        {title && (
          <h1 className="brand-gradient" style={{ marginTop: 0, marginBottom: 8 }}>
            {title}
          </h1>
        )}
        {subtitle && <p className="helper" style={{ marginTop: 0 }}>{subtitle}</p>}
        <div style={{ marginTop: 24 }}>{children}</div>
      </div>
    </div>
  );
}
