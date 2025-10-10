import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router";
import { useAuth } from "../context/AuthProvider";
import SkyBrand from "../components/SkyBrand";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from?.pathname || "/";

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Email and password are required.");
      return;
    }
    setSubmitting(true);
    const { error: err } = await login(email.trim(), password);
    setSubmitting(false);

    if (err) {
      setError(err.message || "Invalid credentials");
      return;
    }
    navigate(redirectTo, { replace: true });
  };

  return (
    <div className="container">
      <div className="card" role="region" aria-label="Login">
        <SkyBrand size={40} />
        <h1 className="brand-gradient" style={{ marginTop: 16 }}>Welcome back</h1>
        <p className="helper">Log in to discover volunteering opportunities.</p>
        <form onSubmit={onSubmit} noValidate style={{ marginTop: 24 }}>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            className="input"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ marginTop: 8, marginBottom: 16 }}
          />
          <label htmlFor="password">Password</label>
          <input
            id="password"
            className="input"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            style={{ marginTop: 8 }}
          />
          {error && <div className="error" role="alert">{error}</div>}
          <button className="button" disabled={submitting} style={{ marginTop: 16 }}>
            {submitting ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <p className="helper" style={{ marginTop: 16 }}>
          New to OneSky? <Link to="/register">Create an account</Link>
        </p>
      </div>
    </div>
  );
}
