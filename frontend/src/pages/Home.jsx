import React from "react";
import { useAuth } from "../context/AuthProvider";
import ImpactContainer from "../components/ImpactComponent/ImpactContainer";

export default function Home() {
  const { user, logout } = useAuth();

  return (
    <>
      {/* Keep the greeting area narrow */}
      <div className="page-narrow">
        <div className="card">
          <h1 className="brand-gradient" style={{ marginTop: 0 }}>
            Hello, {user?.first_name || "there"} 👋
          </h1>
          <p className="helper">
            This is the protected home. We can add dashboard, featured events here etc.
          </p>
          <button
            className="button"
            style={{ marginTop: 16, width: "auto", padding: "0 16px" }}
            onClick={logout}
          >
            Log out
          </button>
        </div>
      </div>

      {/* Impact section stays full-width and handles its own layout */}
      <ImpactContainer />
    </>
  );
}
