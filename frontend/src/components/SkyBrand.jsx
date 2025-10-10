import React from "react";
import logo from "../assets/OneSky-logo.png";

export default function SkyBrand({ size = 32 }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <img src={logo} alt="OneSky" style={{ height: size }} />
      <span className="brand-gradient" style={{ fontSize: size * 0.6, fontWeight: 700 }}>
      </span>
    </div>
  );
}
