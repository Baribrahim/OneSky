import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router";
import { useAuth } from "../context/AuthProvider";
import FormCard from "../components/FormComponents/FormCard";
import TextField from "../components/FormComponents/TextField";
import SubmitButton from "../components/FormComponents/SubmitButton";

export default function Login() {
  // Form state
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState("");

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = location.state?.from?.pathname || "/";

  // Handle form submission
  const onSubmit = async (e) => {
    e.preventDefault();
    setFormError("");

    if (!email || !password) {
      setFormError("Email and password are required.");
      return;
    }

    setSubmitting(true);
    const { error } = await login(email.trim(), password);
    setSubmitting(false);

    if (error) {
      setFormError(error.message || "Invalid credentials");
      return;
    }
    navigate(redirectTo, { replace: true });
  };

  return (
    <FormCard title="Welcome back" subtitle="Log in to discover volunteering opportunities.">
      <form onSubmit={onSubmit} noValidate className="stack">
        <TextField
          id="email"
          label="Email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <TextField
          id="password"
          label="Password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
        />
        {formError && <div className="error" role="alert">{formError}</div>}
        <SubmitButton loading={submitting} loadingLabel="Signing in…">
          Sign in
        </SubmitButton>
      </form>

      <p className="helper" style={{ marginTop: 16 }}>
        New to OneSky? <Link to="/register">Create an account</Link>
      </p>
    </FormCard>
  );
}
