import React, { useEffect, useState } from "react";
import { api, toResult } from "../lib/apiClient";
import '../styles/profile.css'

const Profile = () => {
  const [userInfo, setUserInfo] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  const formatMonthYear = (dateStr) => {
    if (!dateStr) return "";
    const [year, month] = dateStr.split("-");
    const date = new Date(year, month - 1);
    return date.toLocaleString("default", { month: "long", year: "numeric" });
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
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, []);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

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
      console.error(e);
    } finally {
      setUploading(false);
    }
  };

  if (loading) return <p>Loading profile...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

return (
  <div>
    {/* Hero Banner */}
    <div className="hero-banner"/>

    {/* Profile Card */}
    <div className="profile-container">
      <div className="profile-card">
      <div className="profile-content">
        <img
          src={
            userInfo.info?.ProfileImgURL
              ? `http://localhost:5000${userInfo.info.ProfileImgURL}`
              : "src/assets/profileImgs/default.png"
          }
          alt="Profile"
          className="profile-img"
        />
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
            <span className="detail-value">{userInfo.info?.FirstName || "User"}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Surname:</span>
            <span className="detail-value">{userInfo.info?.LastName || ""}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Email:</span>
            <span className="detail-value">{userInfo.info?.Email || "Not provided"}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Member since:</span>
            <span className="detail-value">{formatMonthYear(userInfo.info?.DateJoined)}</span>
          </div>
        </div>
      </div>
      </div>
    </div>
  </div>
);

};

export default Profile;
