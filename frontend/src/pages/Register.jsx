import React, { useState } from "react";
import { Link, useNavigate } from "react-router";
import { useAuth } from "../context/AuthProvider";
import FormCard from "../components/FormComponents/FormCard";
import TextField from "../components/FormComponents/TextField";
import SubmitButton from "../components/FormComponents/SubmitButton";

export default function Register() {
  // Form state
  const [first_name, setFirstName] = useState("");
  const [last_name, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState("");

  const { register } = useAuth();
  const navigate = useNavigate();

  // Handle form submission
  const onSubmit = async (e) => {
    e.preventDefault();
    setFormError("");

    if (!first_name || !last_name || !email || !password) {
      setFormError("All fields are required.");
      return;
    }
    if (password.length < 8) {
      setFormError("Password must be at least 8 characters.");
      return;
    }

    setSubmitting(true);
    const { error } = await register({ first_name, last_name, email: email.trim(), password });
    setSubmitting(false);

    if (error) {
      setFormError(error.message || "Registration failed.");
      return;
    }
    navigate("/", { replace: true });
  };

  return (
    <FormCard title="Create your account">
      <form onSubmit={onSubmit} noValidate className="stack">
        <TextField
          id="first_name"
          label="First name"
          value={first_name}
          onChange={(e) => setFirstName(e.target.value)}
          required
        />
        <TextField
          id="last_name"
          label="Last name"
          value={last_name}
          onChange={(e) => setLastName(e.target.value)}
          required
        />
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
          autoComplete="new-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
        />
        {formError && <div className="error" role="alert">{formError}</div>}
        <SubmitButton loading={submitting} loadingLabel="Creating…">
          Create account
        </SubmitButton>
      </form>

      <p className="helper" style={{ marginTop: 16 }}>
        Already have an account? <Link to="/login">Sign in</Link>
      </p>
    </FormCard>
  );
}
