import React from "react";
import "../styles/welcomePage.css"
import welcomeVideo from "../assets/Welcome (1).mp4";
import Footer from "../components/Footer.jsx";
import beachClean from "../assets/welcomePage/beachClean.png";
import forestClean from "../assets/welcomePage/forestClean.png";
import social from "../assets/welcomePage/social.png";
import Header from "../components/Header.jsx";

function WelcomePage() {
  return (
    <div className="welcome-page">
        <Header />
        <section className="intro-video">
        <video className="video" autoPlay muted loop>
          <source src={welcomeVideo} type="video/mp4" />
        </video>
      </section>

      <section className="hero">
        <div className="hero-content">
          <h1 className="fade-in">Make an Impact with OneSky</h1>
          <p className="fade-in delay">Connecting people with meaningful volunteer opportunities.</p>
        </div>
      </section>

      {/* Intro Video */}
      

      {/* Features Section */}
      <section className="features">
        <h1>Explore Our Features</h1>
        <div className="feature-list">
          {[
            { 
                img: beachClean,
                title: "Search and Filter Events",
                description: "Discover volunteering opportunities tailored to your interests, location, and schedule. Use advanced filters to narrow down by date, tags, and location, making it easy to find the perfect event for you. Whether you’re looking for a quick activity or a long-term commitment, OneSky helps you connect with causes that matter most."
            },
            {
                img: social,
                title: "Join Events",
                description: "Sign up for events with just one click and start making an impact. From local cleanups to charity drives, you’ll always find something meaningful to participate in. Joining events is simple, and you’ll receive all the details you need to prepare and make the most of your experience."
            },
            {
                img: forestClean,
                title: "Create and Join Teams",
                description: "Join existing teams such as your department to collaborate on shared volunteering goals, or create new teams with friends from other departments. Build cross-functional connections while making a positive impact together. Whether you want to strengthen your team spirit or network across the organization, OneSky makes it easy to organize group efforts and track collective achievements."
            },
            {
                img: social,
                title: "Leaderboards and Badges",
                description: "Celebrate your achievements and see how you rank among peers. Earn badges for milestones like completing your first event or contributing a certain number of hours. Leaderboards showcase top contributors, inspiring friendly competition and recognition across teams and departments."
            },
            { 
                img: social,
                title: "Interactive Chatbot",
                description: "Get instant support and guidance with our interactive chatbot, designed to make your volunteering experience effortless. Whether you need help finding events, joining teams, or understanding how leaderboards work, the chatbot is available 24/7 to answer your questions. It provides personalized recommendations, step-by-step assistance, and quick solutions—so you can focus on making an impact without any hassle."
            },

          ].map((feature, index) => (
            <div key={index} className={`feature-section ${index % 2 === 0 ? "normal" : "reverse"}`}>
                <img src={feature.img} alt={feature.title} className="feature-image" />
                <div className="feature-text">
                    <h3>{feature.title}</h3>
                    <p>{feature.description}</p>
                </div>
            </div>
          ))}
        </div>
      </section>

      {/* Impact Stats */}
      <section className="impact">
        <h2 className="counter">121,819 Hours Volunteered This Year</h2>
        <p className="quote">“It's a fantastic way to give back and help others.”</p>
      </section>

      {/* Testimonials */}
      <section className="testimonials">
        <h2>What Our Volunteers Say</h2>
        <div className="testimonial-grid">
          {[
            { quote: "OneSky helped me find amazing opportunities!", name: "Volunteer A" },
            { quote: "I love tracking my progress and earning badges!", name: "Volunteer B" }
          ].map((testimonial, index) => (
            <div key={index} className="testimonial-card hover-zoom">
              <p className="quote">“{testimonial.quote}”</p>
              <p className="name">{testimonial.name}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer CTA */}
      <footer className="footer-cta">
        <h2>Ready to make a difference?</h2>
        <button className="btn-primary large">Join OneSky Today</button>
      </footer>
      <Footer />
    </div>
  );
};

export default WelcomePage;