import React from "react";

/**
 * TextField
 * Label + Input + Inline error.
 * Props:
 *  - id, label, type, value, onChange, autoComplete, required, minLength, placeholder
 *  - error: string to show under the field
 *  - inputProps: spread for any extra input attributes
 */
export default function TextField({
  id,
  label,
  type = "text",
  value,
  onChange,
  autoComplete,
  required = false,
  minLength,
  placeholder,
  error,
  inputProps = {},
}) {
  const describedBy = error ? `${id}-error` : undefined;

  return (
    <div className="stack">
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        className="input"
        type={type}
        value={value}
        onChange={onChange}
        autoComplete={autoComplete}
        required={required}
        minLength={minLength}
        placeholder={placeholder}
        aria-invalid={!!error}
        aria-describedby={describedBy}
        {...inputProps}
      />
      {error ? (
        <div className="error" id={`${id}-error`} role="alert">
          {error}
        </div>
      ) : null}
    </div>
  );
}
