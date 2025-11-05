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
      <div className="card">
        <h2 className="profile-title">
          Your details
        </h2>
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
        
        <p className="profile-email">First Name: {userInfo.info?.FirstName || "User"}{" "}</p>
        <p className="profile-joined">Surname: {userInfo.info?.LastName || ""}</p>
        <p className="profile-email">Email: {userInfo.info?.Email || "Not provided"}</p>
        <p className="profile-joined">Member since: {formatMonthYear(userInfo.info?.DateJoined)}</p>
      </div>
  );
};

export default Profile;
