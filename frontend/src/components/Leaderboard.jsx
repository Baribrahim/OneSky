import React, { useEffect, useState } from "react";
import { api, toResult } from "../lib/apiClient";
import '../styles/leaderboard.css';

const Leaderboard = () => {
  const [rankedUsers, setRankedUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentRank, setCurrentRank] = useState("");
  const [expandedUsers, setExpandedUsers] = useState([]);
  const [userStats, setUserStats] = useState({});


  const getInitials = (firstName, lastName) => {
    const first = firstName?.[0]?.toUpperCase() || '';
    const last = lastName?.[0]?.toUpperCase() || '';
    return (first + last) || 'U'; // fallback "U" for Unknown User
  };

  const fetchRankedUsers = async () => {
    setLoading(true);
    setError("");

    const { data, error } = await toResult(api.get("/api/leaderboard"));
    if (error) {
      setError(error.message || "Error loading users");
    } else {
      setRankedUsers(data.users || []);
    }
    setLoading(false);
  };

  const fetchCurrentUserRank = async () => {
    const { data, error } = await toResult(api.get("/api/leaderboard/my-rank"));
    if (!error) setCurrentRank(data.currentRank);
  };

  useEffect(() => {
    fetchRankedUsers();
    fetchCurrentUserRank();
  }, []);

  const handleToggleStats = async (email) => {
    // Fetch stats if not already cached
    if (!userStats[email]) {
      const { data, error } = await toResult(api.post("/api/leaderboard/stats", { email }));
      if (!error) {
        setUserStats((prev) => ({ ...prev, [email]: data }));
      } else {
        setError(error.message || "Error fetching stats");
        return;
      }
    }

    // Toggle user in expandedUsers array
    setExpandedUsers((prev) =>
      prev.includes(email) ? prev.filter((e) => e !== email) : [...prev, email]
    );
  };

  return (
    <div className="leaderboard-card">
      <h2>Top Volunteers</h2>

      {loading && <p>Loading...</p>}
      {!loading && error && <div className="error" role="alert">{error}</div>}
      {!loading && !error && rankedUsers.length === 0 && <p>No users yet.</p>}
      <p className="helper">Scores are a weighted sum of events completed, hours spent, and badges earned.</p>
      <div className="leaderboard-list">
        {!loading && !error && rankedUsers.map((user, index) => (
          <div className="leaderboard-item" key={index} >
          <div className="leaderboard-user">
            <span className="rank">{index + 1}.</span>{" "}
            {user.ProfileImgURL && user.ProfileImgPath != 'default.png' ? (
              <img
                src={`http://localhost:5000${user.ProfileImgURL}`}
                alt="Profile"
                className="leaderboard-img"
              />
            ) : (
              <div className="leaderboard-avatar">
                {getInitials(user.FirstName, user.LastName)}
              </div>
            )}
            <span className="name">{user.FirstName} {user.LastName}</span>{" "}
            <span className="score-tooltip">
              <span className="score">{user.RankScore}</span>
            </span>

          </div>
          <div className="show-stats-wrapper" style={{ paddingLeft: '35px' }}>
            <div className="show-stats-wrapper-inner" style={{ display: 'flex', justifyContent: 'flex-end', paddingLeft: '35px' }}>
            <span className="show-stats-text" onClick={() => handleToggleStats(user.Email)}>
              {expandedUsers.includes(user.Email) ? "Hide Stats" : "Show Stats"}
            </span>
            </div>

            {expandedUsers.includes(user.Email) && userStats[user.Email] && (
              <div className="user-stats">
                <p>Completed Events: {userStats[user.Email].stats?.CompletedEvents}</p>
                <p>Total Hours: {userStats[user.Email].stats?.TotalHours}</p>
                <p>Badges: {userStats[user.Email].stats?.BadgesCount}</p>
              </div>
            )}
            </div>
          </div>
          
        ))}
      </div>

      {currentRank && <p className="your-rank">Your rank: <strong>{currentRank}</strong></p>}
    </div>
  );
};

export default Leaderboard;
