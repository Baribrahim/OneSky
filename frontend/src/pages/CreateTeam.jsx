import React, { useState } from "react";
import { api, toResult } from "../lib/apiClient";
import { useNavigate } from "react-router-dom";

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
      <div className="container">
        <div className="card" role="region" aria-label="Team Created">
          <h1 className="brand-gradient" style={{ marginTop: 0 }}>🎉 Team Created!</h1>
          <p className="helper" style={{ marginTop: 8 }}>
            Your team <strong>{success.name}</strong> was created successfully.
          </p>
          <p className="join-code">Join Code: <code>{success.join_code}</code></p>

          <button className="button" onClick={() => navigate("/teams")} style={{ marginTop: 16 }}>
            Back to Teams
          </button>
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
    <div className="container">
      <div className="card" role="region" aria-label="Create Team">
        <h1 className="brand-gradient" style={{ marginTop: 0 }}>Create a Team</h1>
        <p className="helper" style={{ marginTop: 8 }}>
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

          <button className="button" disabled={loading} style={{ marginTop: 16 }}>
            {loading ? "Creating..." : "Create Team"}
          </button>
        </form>
      </div>
    </div>
  );
}
