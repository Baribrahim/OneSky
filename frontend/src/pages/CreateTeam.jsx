import React, { useState } from "react";
import { api, toResult } from "../lib/apiClient";
import { useNavigate } from "react-router-dom";
import skyCaresImage from "../assets/skycares2.jpg";

/**
 * CreateTeam Page
 * - Styled to match Register form
 * - Creates a new team via POST /teams
 * - Displays success view with join code
 */
export default function CreateTeam() {
  const [form, setForm] = useState({
    name: "",
    description: "",
    department: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(null);
  const navigate = useNavigate();

  // --- Handle controlled input updates ---
  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  // --- Validate before submit ---
  const validate = () => {
    if (!form.name.trim()) return "Team name is required.";
    if (!form.description.trim()) return "Description is required.";
    if (!form.department.trim()) return "Department is required.";
    return "";
  };

  // --- Submit handler ---
  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationError = validate();
    if (validationError) return setError(validationError);

    setLoading(true);
    setError("");

    const { data, error } = await toResult(
      api.post("/api/teams", {
        name: form.name.trim(),
        description: form.description.trim() || null,
        department: form.department.trim() || null,
      })
    );

    setLoading(false);

    if (error) {
      setError(error.message || "Failed to create team.");
      return;
    }

    setSuccess(data);
  };

  // --- Success screen ---
  if (success) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100%" }}>
        <div className="container" style={{ maxWidth: "500px", width: "100%" }}>
          <div className="card" role="region" aria-label="Team Created">
            <h1 className="brand-gradient" style={{ marginTop: 0 }}>🎉 Team Created!</h1>
            <p className="helper" style={{ marginTop: 8 }}>
              Your team <strong>{success.name}</strong> was created successfully.
            </p>
            <p className="join-code">Join Code: <code>{success.join_code}</code></p>

            <button className="button-sky" onClick={() => navigate("/teams")} style={{ marginTop: 16 }}>
              Back to Teams
            </button>
          </div>
        </div>
        <style>{`
          .join-code {
            margin: 16px 0;
            font-family: monospace;
            font-weight: 600;
            font-size: 1.1rem;
            color: var(--brand-primary);
          }
        `}</style>
      </div>
    );
  }

  // --- Default form view ---
  return (
    <>
      {/* Mobile: Sky Cares Banner at top */}
      <div className="mobile-banner">
        <img 
          src={skyCaresImage} 
          alt="Sky Cares" 
          className="banner-image"
        />
      </div>
      <div className="auth-content-wrapper">
        {/* Desktop: Split layout, Mobile: Stacked */}
        <div className="auth-layout">
          {/* Left side - Form */}
          <div className="auth-form-container">
            <div className="container" style={{ maxWidth: "500px", width: "100%" }}>
              <div className="card" role="region" aria-label="Create Team">
                <h1 className="event-title" style={{ marginTop: 0, textAlign: "center" }}>Create a Team</h1>
                <p className="filter-tagline" style={{ marginTop: 8 }}>
                  Fill in the details below to create your new team.
                </p>

                <form onSubmit={handleSubmit} noValidate style={{ marginTop: 24 }}>
                  <label htmlFor="name">Team Name</label>
                  <input
                    id="name"
                    name="name"
                    className="input"
                    value={form.name}
                    onChange={handleChange}
                    required
                    style={{ marginTop: 8, marginBottom: 16 }}
                  />

                  <label htmlFor="description">Description</label>
                  <textarea
                    id="description"
                    name="description"
                    className="input"
                    value={form.description}
                    onChange={handleChange}
                    rows={3}
                    required
                    style={{ marginTop: 8, marginBottom: 16 }}
                  />

                  <label htmlFor="department">Department</label>
                  <input
                    id="department"
                    name="department"
                    className="input"
                    value={form.department}
                    onChange={handleChange}
                    required
                    style={{ marginTop: 8 }}
                  />

                  {error && <div className="error" role="alert" style={{ marginTop: 12 }}>{error}</div>}

                  <button className="button-sky" disabled={loading} style={{ marginTop: 16 }}>
                    {loading ? "Creating..." : "Create Team"}
                  </button>
                </form>
              </div>
            </div>
          </div>
          {/* Right side - Sky Cares Image (Desktop only) */}
          <div className="desktop-image">
            <img 
              src={skyCaresImage} 
              alt="Sky Cares" 
              className="desktop-image-content"
            />
          </div>
        </div>
      </div>
      <style>{`
        .mobile-banner {
          width: 100vw;
          display: none;
          margin-top: calc(-1 * var(--space-6));
          margin-bottom: var(--space-6);
          text-align: center;
          position: relative;
          left: 50%;
          right: 50%;
          margin-left: -50vw;
          margin-right: -50vw;
        }
        .banner-image {
          width: 100%;
          height: auto;
          max-height: 250px;
          object-fit: cover;
          display: block;
          margin: 0 auto;
        }
        .auth-content-wrapper {
          flex: 1;
          display: flex;
          flex-direction: column;
          min-height: 100%;
        }
        .auth-layout {
          flex: 1;
          display: flex;
          flex-direction: row;
          gap: var(--space-6);
        }
        .auth-form-container {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .desktop-image {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0;
          background-color: var(--color-bg, #ffffff);
        }
        .desktop-image-content {
          width: 100%;
          height: 100%;
          object-fit: cover;
          display: block;
          border-radius: 8px;
        }
        @media (max-width: 768px) {
          .mobile-banner {
            display: block !important;
          }
          .desktop-image {
            display: none !important;
          }
          .auth-layout {
            flex-direction: column;
          }
        }
        @media (min-width: 769px) {
          .mobile-banner {
            display: none !important;
          }
          .desktop-image {
            display: flex !important;
          }
        }
      `}</style>
    </>
  );
}
