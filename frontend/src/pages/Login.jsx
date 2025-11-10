import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router";
import { useAuth } from "../context/AuthProvider";
import SkyBrand from "../components/SkyBrand";
import Header from "../components/Header";
import Footer from "../components/Footer";
import skyCaresImage from "../assets/skycares2.jpg";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from?.pathname || "/home";

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
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Header />
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
          {/* Left side - Auth form */}
          <div className="auth-form-container">
            <div className="container" style={{ maxWidth: "500px", width: "100%" }}>
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
              <div className="error-container" role="alert" style={{ minHeight: '24px', marginTop: 8, marginBottom: 0 }}>
                {error && <div className="error" style={{ marginTop: 0 }}>{error}</div>}
              </div>
              <button className="button-sky" disabled={submitting} style={{ marginTop: 16 }}>
                {submitting ? "Signing in..." : "Sign in"}
              </button>
            </form>
            <p className="helper" style={{ marginTop: 16 }}>
              New to OneSky? <Link to="/register">Create an account</Link>
            </p>
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
      <Footer />
      <style>{`
        .mobile-banner {
          width: 100%;
          display: none;
        }
        .banner-image {
          width: 100%;
          height: auto;
          max-height: 250px;
          object-fit: cover;
          display: block;
        }
        .auth-content-wrapper {
          flex: 1;
          display: flex;
          flex-direction: column;
          min-height: calc(100vh - 60px);
        }
        .auth-layout {
          flex: 1;
          display: flex;
          flex-direction: row;
        }
        .auth-form-container {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: var(--space-6) var(--space-8);
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
    </div>
  );
}
