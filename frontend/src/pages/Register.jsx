import React, { useState } from "react";
import { Link, useNavigate } from "react-router";
import { useAuth } from "../context/AuthProvider";
import SkyBrand from "../components/SkyBrand";
import Header from "../components/Header";
import Footer from "../components/Footer";
import skyCaresImage from "../assets/skycares2.jpg";

export default function Register() {
  const [first_name, setFirstName] = useState("");
  const [last_name, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const { register } = useAuth();
  const navigate = useNavigate();

  const emailPattern = /^[A-Za-z0-9._%+-]+@sky\.uk$/;
  const passwordPattern = /^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;

  const handleEmailBlur = (event) => {
    const value = event.target.value.trim();
    if (value && !emailPattern.test(value)) {
      setError("Email address not in a valid format. Please make sure it ends with @sky.uk");
    } else if (emailPattern.test(value)) {
      setError("");
    }
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!first_name || !last_name || !email || !password) {
      setError("All fields are required.");
      return;
    }
    if (!emailPattern.test(email.trim())) {
      setError("Email address not in a valid format");
      return;
    }
    if (!passwordPattern.test(password)) {
      setError("Password must be at least 8 characters and include an uppercase letter, a number, and a special character.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);
    const { error: err } = await register({ first_name, last_name, email: email.trim(), password });
    setSubmitting(false);

    if (err) {
      setError(err.message || "Registration failed.");
      return;
    }
    navigate("/home", { replace: true });
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
              <div className="card" role="region" aria-label="Register">
            <SkyBrand size={40} />
            <h1 className="brand-gradient" style={{ marginTop: 16 }}>Create your account</h1>
            <form onSubmit={onSubmit} noValidate style={{ marginTop: 24 }}>
              <label htmlFor="first_name">First name</label>
              <input id="first_name" className="input" value={first_name} onChange={(e) => setFirstName(e.target.value)} required style={{ marginTop: 8, marginBottom: 16 }} />
              <label htmlFor="last_name">Last name</label>
              <input id="last_name" className="input" value={last_name} onChange={(e) => setLastName(e.target.value)} required style={{ marginTop: 8, marginBottom: 16 }} />
              <label htmlFor="email">Email</label>
              <input id="email" className="input" type="email" autoComplete="email" value={email} onChange={(e) => {
                const value = e.target.value;
                setEmail(value);
                const trimmed = value.trim();
                if (trimmed && !emailPattern.test(trimmed)) {
                  setError("Email address not in a valid format");
                } else if (emailPattern.test(trimmed)) {
                  setError("");
                }
              }} onBlur={handleEmailBlur} required style={{ marginTop: 8, marginBottom: 16 }} />
              <label htmlFor="password">Password</label>
              <input id="password" className="input" type={showPassword ? "text" : "password"} autoComplete="new-password" value={password} onChange={(e) => {
                const value = e.target.value;
                setPassword(value);
                if (value && !passwordPattern.test(value)) {
                  setError("Password must be at least 8 characters and include an uppercase letter, a number, and a special character.");
                } else if (confirmPassword && value !== confirmPassword) {
                  setError("Passwords do not match.");
                } else if (passwordPattern.test(value)) {
                  setError("");
                }
              }} onBlur={(e) => {
                const value = e.target.value;
                if (value && !passwordPattern.test(value)) {
                  setError("Password must be at least 8 characters and include an uppercase letter, a number, and a special character.");
                } else if (confirmPassword && value !== confirmPassword) {
                  setError("Passwords do not match.");
                } else if (passwordPattern.test(value)) {
                  setError("");
                }
              }} minLength={8} required style={{ marginTop: 8 }} />
              <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
                <label htmlFor="show_password" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <input id="show_password" type="checkbox" checked={showPassword} onChange={(e) => setShowPassword(e.target.checked)} />
                  Show password
                </label>
              </div>
              <label htmlFor="confirm_password" style={{ marginTop: 16 }}>Confirm password</label>
              <input id="confirm_password" className="input" type={showConfirmPassword ? "text" : "password"} autoComplete="new-password" value={confirmPassword} onChange={(e) => {
                const value = e.target.value;
                setConfirmPassword(value);
                if (value && password !== value) {
                  setError("Passwords do not match.");
                } else if (passwordPattern.test(password) && value === password) {
                  setError("");
                }
              }} onBlur={(e) => {
                const value = e.target.value;
                if (value && password !== value) {
                  setError("Passwords do not match.");
                } else if (passwordPattern.test(password) && value === password) {
                  setError("");
                }
              }} minLength={8} required style={{ marginTop: 8 }} />
              <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
                <label htmlFor="show_confirm_password" style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <input id="show_confirm_password" type="checkbox" checked={showConfirmPassword} onChange={(e) => setShowConfirmPassword(e.target.checked)} />
                  Show confirm password
                </label>
              </div>
              {error && <div className="error" role="alert">{error}</div>}
              <button className="button" disabled={submitting} style={{ marginTop: 16 }}>
                {submitting ? "Creating..." : "Create account"}
              </button>
            </form>
            <p className="helper" style={{ marginTop: 16 }}>
              Already have an account? <Link to="/login">Sign in</Link>
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
