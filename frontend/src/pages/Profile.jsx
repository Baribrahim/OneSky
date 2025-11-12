import React, { useEffect, useState } from "react";
import { api, toResult } from "../lib/apiClient";
import '../styles/profile.css';

const Profile = () => {
  const [userInfo, setUserInfo] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [updateError, setUpdateError] = useState("");
  const [uploading, setUploading] = useState(false);

  // Password fields
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [updatingPassword, setUpdatingPassword] = useState(false);
  const [passwordErrors, setPasswordErrors] = useState({
    newPassword: "",
    confirmPassword: ""
  });

  const passwordPattern = /^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;

  const formatMonthYear = (dateStr) => {
    if (!dateStr) return "";
    const [year, month] = dateStr.split("-");
    const date = new Date(year, month - 1);
    return date.toLocaleString("default", { month: "long", year: "numeric" });
  };

    // Generates user initials
    const getInitials = (firstName, lastName) => {
      if (!firstName && !lastName) return "U";
      const first = firstName ? firstName[0].toUpperCase() : "";
      const last = lastName ? lastName[0].toUpperCase() : "";
      return `${first}${last}`;
    };


  const fetchDetails = async () => {
    setLoading(true);
    setError("");
    try {
      const { data, error } = await toResult(api.get("/api/profile"));
      if (error) {
        setError(error.message || "Error loading user info");
      } else {
        setUserInfo(data || {});
      }
    } catch (e) {
      setError("Unexpected error loading profile");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, []);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    const MAX_FILE_SIZE = 5 * 1024 * 1024;
    if (!file) return;
    if (file.size > MAX_FILE_SIZE) {
      setError("File too large. Please select an image under 5MB.");
      return;
    }

    setUploading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("image", file);

      const { data, error } = await toResult(
        api.post("/api/profile/update-image", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        })
      );

      if (error) {
        setError(error.message || "Error uploading file");
      } else {
        fetchDetails();
      }
    } catch (e) {
      setError("Unexpected error uploading profile image");
    } finally {
      setUploading(false);
    }
  };

  const handlePasswordUpdate = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    // Check if all fields are filled
    if (!oldPassword || !newPassword || !confirmPassword) {
      setUpdateError("All password fields are required.");
      return;
    }

    // Check for live validation errors
    if (passwordErrors.newPassword || passwordErrors.confirmPassword) {
      setUpdateError("Please fix the validation errors before submitting.");
      return;
    }

    setUpdatingPassword(true);

    try {
      const { data, error } = await toResult(
        api.post("/api/profile/update-password", {
          old_password: oldPassword,
          new_password: newPassword,
        })
      );

      if (error) {
        setUpdateError(error.message || "Failed to update password.");
      } else {
        setSuccess("Password updated successfully!");
        setOldPassword("");
        setNewPassword("");
        setConfirmPassword("");
        setPasswordErrors({ newPassword: "", confirmPassword: "" });
      }
    } catch (e) {
      setUpdateError("Unexpected error updating password");
    } finally {
      setUpdatingPassword(false);
    }
  };


  const info = userInfo.info || {};

  return (
    <div>
      <div className="hero-banner" />

      <div className="profile-container">
        <div className="profile-card">
          {loading && (
            <div className="status-message loading">
              <p>Loading profile...</p>
            </div>
          )}

          {error && !loading && (
            <div className="error image-error" role="alert">
              <p>{error}</p>
            </div>
          )}

          {!loading && (
            <div className="profile-content">
            {info.ProfileImgURL && info.ProfileImgPath != 'default.png' ? (
              <img
                src={`http://35.210.202.5:5001${info.ProfileImgURL}`}
                alt={`${info.FirstName || ''} ${info.LastName || ''}`}
                className="profile-img"
              />
            ) : (
              <div className="profile-avatar">
                {getInitials(info.FirstName, info.LastName)}
              </div>
            )}

              <div className="upload-section">
                <label className={`button-sky ${uploading ? "disabled" : ""}`}>
                  {uploading ? "Uploading..." : "Upload Profile Picture"}
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleUpload}
                    className="hidden-input"
                    disabled={uploading}
                  />
                </label>
              </div>

              <div className="profile-details">
                <div className="detail-row">
                  <span className="detail-label">First Name:</span>
                  <span className="detail-value">{info.FirstName || "User"}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Surname:</span>
                  <span className="detail-value">{info.LastName || ""}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Email:</span>
                  <span className="detail-value">{info.Email || "Not provided"}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Member since:</span>
                  <span className="detail-value">
                    {formatMonthYear(info.DateJoined)}
                  </span>
                </div>
              </div>

              {/* Password Update Form */}
              <div className="password-update-section">
                <h3 className="profile">Update Password</h3>
                {success && <div className="success" role="alert">{success}</div>}
                {updateError && <div className="error" role="alert">{updateError}</div>}

                <form onSubmit={handlePasswordUpdate}>
                  <div className="old-password">
                    <label htmlFor="oldPassword"  >Old Password</label>
                    <input
                      type="password"
                      id="oldPassword"
                      className="input"
                      value={oldPassword}
                      onChange={(e) => setOldPassword(e.target.value)}
                      required
                    />
                  </div>
                <div className="new-password">
                  <label htmlFor="newPassword">New Password</label>
                  <input
                    type={showNewPassword ? "text" : "password"}
                    id="newPassword"
                    className="input"
                    value={newPassword}
                    onChange={(e) => {
                      const val = e.target.value;
                      setNewPassword(val);

                      // Live validation for new password
                      if (!passwordPattern.test(val)) {
                        setPasswordErrors(prev => ({
                          ...prev,
                          newPassword: "Password must be at least 8 characters and include an uppercase letter, a number, and a special character."
                        }));
                      } else {
                        setPasswordErrors(prev => ({ ...prev, newPassword: "" }));
                      }

                      // Live validation for confirm password match
                      if (confirmPassword && val !== confirmPassword) {
                        setPasswordErrors(prev => ({ ...prev, confirmPassword: "Passwords do not match." }));
                      } else {
                        setPasswordErrors(prev => ({ ...prev, confirmPassword: "" }));
                      }
                    }}
                    required
                  />
                  {passwordErrors.newPassword && <p className="error">{passwordErrors.newPassword}</p>}

                  <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 4 }}>
                    <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <input
                        type="checkbox"
                        checked={showNewPassword}
                        onChange={(e) => setShowNewPassword(e.target.checked)}
                      />
                      Show password
                    </label>
                  </div>
                  </div>
                  <div className="confirm-password">
                  <label htmlFor="confirmPassword">Confirm New Password</label>
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    id="confirmPassword"
                    className="input"
                    value={confirmPassword}
                    onChange={(e) => {
                      const val = e.target.value;
                      setConfirmPassword(val);

                      // Confirm password validation
                      if (newPassword !== val) {
                        setPasswordErrors(prev => ({ ...prev, confirmPassword: "Passwords do not match." }));
                      } else {
                        setPasswordErrors(prev => ({ ...prev, confirmPassword: "" }));
                      }
                    }}
                    required
                  />
                  {passwordErrors.confirmPassword && <p className="error">{passwordErrors.confirmPassword}</p>}

                  <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 4 }}>
                    <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <input
                        className="confirm-password-checkbox"
                        type="checkbox"
                        checked={showConfirmPassword}
                        onChange={(e) => setShowConfirmPassword(e.target.checked)}
                      />
                      Show password
                    </label>
                  </div>
                  </div>

                  <button
                    className="button-sky"
                    type="submit"
                    disabled={updatingPassword || passwordErrors.newPassword || passwordErrors.confirmPassword}
                  >
                    {updatingPassword ? "Updating..." : "Update Password"}
                  </button>
                </form>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
