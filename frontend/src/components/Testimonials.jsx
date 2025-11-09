import React, { useState } from "react";
import "../styles/welcomePage.css"

function Testimonials() {
  const testimonials = [
    { quote: "OneSky helped me find amazing opportunities!", name: "Alex Carter, Community Volunteer" },
    { quote: "I love tracking my progress and earning badges!", name: "Jordan Lee, Event Coordinator" },
    { quote: "Joining events has never been easier!", name: "Taylor Morgan, Outreach Specialist" },
    { quote: "The leaderboard motivates me to do more!", name: "Casey Brooks, Engagement Officer" },
    { quote: "Creating my own team was so simple, and now we volunteer together every month!", name: "Sam Rivera, Team Lead" },
    { quote: "I’ve connected with so many like-minded people through OneSky!", name: "Jamie Collins, Volunteer Advocate" },
    { quote: "The platform makes organizing events stress-free!", name: "Morgan Blake, Community Manager" }
  ];

  const [currentIndex, setCurrentIndex] = useState(0);

  const nextTestimonial = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % testimonials.length);
  };

  const prevTestimonial = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === 0 ? testimonials.length - 1 : prevIndex - 1
    );
  };

  return (
    <section className="testimonials">
      <h2>What Our Volunteers Say</h2>
      <div className="testimonial-carousel">
        <button onClick={prevTestimonial} className="carousel-btn">‹</button>
        <div className="testimonial-card">
          <p className="quote">“{testimonials[currentIndex].quote}”</p>
          <p className="name">{testimonials[currentIndex].name}</p>
        </div>
        <button onClick={nextTestimonial} className="carousel-btn">›</button>
      </div>
    </section>
  );
}

export default Testimonials;