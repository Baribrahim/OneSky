import React from 'react'
import '../styles/welcome.css'

const Welcome = ({ user }) => {
    const now = new Date();
    const hour = now.getHours();
    let greeting = 'Welcome';
    if (hour >= 5 && hour < 12) {
        greeting = 'Good morning, ';
    } else if (hour >= 12 && hour < 18) {
        greeting = 'Good afternoon, ';
    } else {
        greeting = 'Good evening, ';
    }



  return (
    <div className="welcome-banner">
      <div className="welcome-overlay"></div>
      <img 
        src={"src/assets/welcome-img.jpg"} 
        alt="People volunteering" 
        className="welcome-image" 
      />
      <div className="welcome-text">
        <h1>{greeting} {user?.first_name || "Volunteer"}</h1>
      </div>
    </div>
  )
}

export default Welcome
