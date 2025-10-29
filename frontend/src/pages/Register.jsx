import React, { useState } from "react";
import { Link, useNavigate } from "react-router";
import { useAuth } from "../context/AuthProvider";
import SkyBrand from "../components/SkyBrand";

export default function Register() {
  const [first_name, setFirstName] = useState("");
  const [last_name, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const { register } = useAuth();
  const navigate = useNavigate();

  const emailPattern = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;

  const handleEmailBlur = (event) => {
    const value = event.target.value.trim();
    if (value && !emailPattern.test(value)) {
      alert("Email address not in a valid format");
      event.target.focus();
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
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setSubmitting(true);
    const { error: err } = await register({ first_name, last_name, email: email.trim(), password });
    setSubmitting(false);

    if (err) {
      setError(err.message || "Registration failed.");
      return;
    }
    navigate("/", { replace: true });
  };

  return (
    <div className="container">
      <div className="card" role="region" aria-label="Register">
        <SkyBrand size={40} />
        <h1 className="brand-gradient" style={{ marginTop: 16 }}>Create your account</h1>
        <form onSubmit={onSubmit} noValidate style={{ marginTop: 24 }}>
          <label htmlFor="first_name">First name</label>
          <input id="first_name" className="input" value={first_name} onChange={(e) => setFirstName(e.target.value)} required style={{ marginTop: 8, marginBottom: 16 }} />
          <label htmlFor="last_name">Last name</label>
          <input id="last_name" className="input" value={last_name} onChange={(e) => setLastName(e.target.value)} required style={{ marginTop: 8, marginBottom: 16 }} />
          <label htmlFor="email">Email</label>
          <input id="email" className="input" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} onBlur={handleEmailBlur} required style={{ marginTop: 8, marginBottom: 16 }} />
          <label htmlFor="password">Password</label>
          <input id="password" className="input" type="password" autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} minLength={8} required style={{ marginTop: 8 }} />
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
  );
}
