import React from "react";

/**
 * SubmitButton
 * Primary action button with loading state.
 * Props:
 *  - loading (boolean)
 *  - children (label)
 *  - loadingLabel (optional; default "Submitting...")
 *  - fullWidth (default true)
 */
export default function SubmitButton({
  loading = false,
  children,
  loadingLabel = "Submitting...",
  fullWidth = true,
  ...rest
}) {
  return (
    <button
      className="button"
      disabled={loading}
      style={{ width: fullWidth ? "100%" : "auto" }}
      {...rest}
    >
      {loading ? loadingLabel : children}
    </button>
  );
}
