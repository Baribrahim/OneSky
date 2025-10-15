import React from 'react'
import '../styles/theme.css'
const UpcomingEvents = () => {
  
    const events = 
        [{
            id: 1,
            title: "Community Clean-Up",
            date: "2024-05-15",
            time: "10:00 AM - 1:00 PM",
            location: "Central Park"},
        { id: 2,
            title: "Charity Run",
            date: "2024-06-20",
            time: "8:00 AM - 12:00 PM",
            location: "City Stadium"},
        { id: 3,
            title: "Food Drive",
            date: "2024-07-10",
            time: "9:00 AM - 5:00 PM",
            location: "Community Center"}
        ]
    
  
    return (
    <>
    <h2>Upcoming Events</h2>
    <div className="timeline-container">
      {events.map((event) => (
        <div key={event.id} className="timeline-item">
          <div className="timeline-dot"></div>
          <div className="timeline-content">
            <h3>{event.title}</h3>
            <p>{event.date}</p>
            <p>{event.time} • {event.location}</p>
          </div>
        </div>
      ))}
    </div>
    </>

  )
}

export default UpcomingEvents