import React from "react";
import { useAuth } from "../context/AuthProvider";
import ImpactSection from "../components/ImpactComponent/ImpactSection";

export default function Home() {
  const { user, logout } = useAuth();
  return (
    <div className="container">
      <div className="card">
        <h1 className="brand-gradient" style={{ marginTop: 0 }}>Hello, {user?.first_name || "there"} 👋</h1>
        <p className="helper">This is the protected home. We can add dashabord, featured events here etc.</p>
        <button className="button" style={{ marginTop: 16, width: "auto", padding: "0 16px" }} onClick={logout}>
          Log out
        </button>
      </div>

      <ImpactSection />
    </div>
  );
}
