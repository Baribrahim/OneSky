import React, { useState, useEffect } from "react";
import "../styles/welcomePage.css";

function Testimonials() {
  const testimonials = [
    { quote: "OneSky helped me find amazing volunteering opportunities!", name: "Alex Carter" },
    { quote: "I love tracking my progress and earning badges!", name: "Jordan Lee" },
    { quote: "Joining events has never been easier!", name: "Taylor Morgan" },
    { quote: "The leaderboard motivates me to do more!", name: "Casey Brooks" },
    { quote: "Creating my own team was so simple, and now we volunteer together every month!", name: "Sam Rivers" },
    { quote: "I’ve connected with so many like-minded people through OneSky!", name: "Jamie Collins" },
    { quote: "The platform makes organising events stress-free!", name: "Morgan Blake"}
  ];

  const colors = ["#fef3c7", "#e0f2fe", "#fce7f3", "#ede9fe", "#dcfce7", "#fff7ed", "#f1f5f9"];

  const [currentIndex, setCurrentIndex] = useState(0);

  const nextTestimonial = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % testimonials.length);
  };

  const prevTestimonial = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === 0 ? testimonials.length - 1 : prevIndex - 1
    );
  };

  // Auto-flip every 4 seconds
  useEffect(() => {
    const interval = setInterval(nextTestimonial, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="testimonials">
      <h2>What Our Volunteers Say</h2>
      <div className="testimonial-carousel">
        <button onClick={prevTestimonial} className="carousel-btn">‹</button>
        <div
          key={currentIndex}
          className="testimonial-card slide-in"
          style={{ backgroundColor: colors[currentIndex] }}
        >
          <p className="quote">“{testimonials[currentIndex].quote}”</p>
          <p className="name">{testimonials[currentIndex].name}</p>
        </div>
        <button onClick={nextTestimonial} className="carousel-btn">›</button>
      </div>
    </section>

  );
}

export default Testimonials;