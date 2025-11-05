import React, { useEffect, useState } from "react";
import { api, toResult } from "../lib/apiClient";

const Leaderboard = () => {
  const [rankedUsers, setRankedUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentRank, setCurrentRank] = useState("");
  const [userStats, setUserStats] = useState("");

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

  const fetchUserStats = async (email) => {
    const { data, error } = await toResult(api.post("/api/leaderboard/stats", { email: email }));
    if (!error) {
      setUserStats(data);
    } 
    else {
      setError(error.message || "Error fetching stats");
    }
  };

  return (
    <div className="card">
      <h3>Leaderboard</h3>

      {loading && <p>Loading...</p>}
      {!loading && error && <div className="error" role="alert">{error}</div>}
      {!loading && !error && rankedUsers.length === 0 && <p>No users yet.</p>}

      {!loading && !error && rankedUsers.map((user, index) => (
        <div key={index}>
        <p >
          {index + 1}. {user.FirstName} {user.LastName} {user.RankScore}
        </p>
        <button className="button" onClick={() => fetchUserStats(user.Email)}>More Info</button>
        {userStats && (
            <div>
                Completed Events: {userStats.stats.CompletedEvents} <br/>
                Total Hours: {userStats.stats.TotalHours} <br/>
                Badges: {userStats.stats.BadgesCount}
            </div>
            )}
        </div>
      ))}
      {currentRank && <p>Your rank: {currentRank}</p>}
    </div>
  );
};

export default Leaderboard;
