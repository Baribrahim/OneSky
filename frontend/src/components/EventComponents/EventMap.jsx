import React from "react";
import "../../styles/events.css";

function EventMap({ latitude, longitude }) {
  if (!latitude || !longitude) {
    return <p>Loading map...</p>;
    
  }
  
    console.log("Map Props:", latitude, longitude);

  const mapSrc = `https://www.google.com/maps?q=${latitude},${longitude}&z=14&output=embed`;

  return (
    <div className="event-section map-section">
        <h2>Map</h2>
        <div className="map-container">
          <iframe
            title="Event Location"
            src={mapSrc}
            width="100%"
            height="100%"
            style={{ borderRadius: "10px", border: "none", minHeight: "400px" }}
            allowFullScreen
            loading="lazy"
          ></iframe>
        </div>
    </div>
  );
}

export default EventMap;

