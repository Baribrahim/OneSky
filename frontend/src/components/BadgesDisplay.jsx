import React, { useEffect, useRef, useState } from 'react';
import { api, toResult } from '../lib/apiClient.js';
import '../styles/theme.css';
import '../styles/badges.css';
import helpingHandImg from '../assets/badges/helpingHand.png'

const BadgesDisplay = () => {
  const [badges, setBadges] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedBadge, setSelectedBadge] = useState(null);
  const [showToast, setShowToast] = useState(false);
  const prevCountRef = useRef(
    Number.parseInt(window.localStorage.getItem('user_badge_count') || '0', 10)
  );

  // Fetch badges belonging to the current user
  const fetchUserBadges = async () => {
    setLoading(true);
    try {
      const { data, error } = await toResult(
        api.get('/api/badges')
      );
      if (error) {
        console.error("API error:", error);
        setLoading(false);
        return;
      }

      const userBadges = data?.badges ?? [];
      setBadges(userBadges);

      // Simple celebration if badge count increased since last visit
      const newCount = userBadges.length;
      if (newCount > prevCountRef.current) {
        setShowToast(true);
        window.setTimeout(() => setShowToast(false), 3000);
      }
      prevCountRef.current = newCount;
      window.localStorage.setItem('user_badge_count', String(newCount));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Load badges on mount
  useEffect(() => {
    fetchUserBadges();
  }, []);

  // Gets badge icon from API IconURL or falls back to name-based mapping
  const getBadgeIcon = (badge) => {
    // Use IconURL from API if available
    if (badge.IconURL) {
      // Convert /src/assets/badges/ to ../assets/badges/ for frontend
      const iconPath = badge.IconURL.replace('/src/assets/badges/', '../assets/badges/');
      return iconPath;
    }
    
    // Fallback to name-based mapping if IconURL is missing
    const badgeIconMap = {
      'Event Starter': 'firstStep.png',
      'Event Enthusiast': 'eduEnthusiast.png',
      'First Step': 'firstStep.png',
      'Volunteer Veteran': 'volunteerVetran.png',
      'Marathon Helper': 'marathonVolunteer.png',
      'Weekend Warrior': 'weekendWarrior.png',
      'Marathon Volunteer': 'marathonVolunteer.png',
    };

    const iconFile = badgeIconMap[badge.Name] || 'helpingHand.png';
    return `../assets/badges/${iconFile}`;
  };

  // Handles opening and closing modal for badge details
  const handleBadgeClick = (badge) => {
    setSelectedBadge(selectedBadge?.ID === badge.ID ? null : badge);
  };

  return (
    <>
      <h2>My Badges</h2>
      
      <div className="badges-container">
        {showToast && (
          <div className="badge-toast" role="status" aria-live="polite">
            🎉 New badge earned!
          </div>
        )}
        {loading ? (
          <p className="helper">Loading badges...</p>
        ) : badges.length === 0 ? (
          <p className="helper">No badges earned yet. Start volunteering to earn your first badge!</p>
        ) : (
          <div className="badges-grid">
            {badges.map((badge) => (
              <div 
                key={badge.ID} 
                className={`badge-card ${selectedBadge?.ID === badge.ID ? 'selected' : ''}`}
                onClick={() => handleBadgeClick(badge)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleBadgeClick(badge);
                  }
                }}
              >
                {/* Badge icon preview */}
                <div className="badge-icon">
                  <img 
                    src={getBadgeIcon(badge)} 
                    alt={badge.Name}
                    onError={(e) => {
                      e.target.src = helpingHandImg;
                    }}
                  />
                </div>
                {/* Badge name and description toggle */}
                <div className="badge-info">
                  <h3 className="badge-name">{badge.Name}</h3>
                  {selectedBadge?.ID === badge.ID && (
                    <p className="badge-description">{badge.Description}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Modal to show full badge detail */}
      {selectedBadge && (
        <div className="badge-modal-overlay" onClick={() => setSelectedBadge(null)}>
          <div className="badge-modal" onClick={(e) => e.stopPropagation()}>
            <div className="badge-modal-header">
              <img 
                src={getBadgeIcon(selectedBadge)} 
                alt={selectedBadge.Name}
                className="badge-modal-icon"
                onError={(e) => {
                  e.target.src = helpingHandImg;
                }}
              />
              <h3 className="badge-modal-title">{selectedBadge.Name}</h3>
            </div>
            <p className="badge-modal-description">{selectedBadge.Description}</p>
            <button 
              className="button button--secondary"
              onClick={() => setSelectedBadge(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default BadgesDisplay;
