import React from "react";
import { Link } from "react-router-dom";
import "../styles/header.css";
import logo from "../assets/OneSky-logo.png";
import { useAuth } from "../context/AuthProvider";

/**
 * Header
 * Full-width top bar with three sections:
 * - Left: Brand logo
 * - Center: Navigation links
 * - Right: Logout button
 */
export default function Header() {
  const { user, logout } = useAuth();
  const isLoggedIn = !!user; // true if user object exists

  return (
    <header className="header" role="banner">
      {/* Left: Logo */}
      <div className="logo-container">
        <Link to="/" aria-label="OneSky Home">
          <img src={logo} alt="OneSky Logo" className="logo" />
        </Link>
      </div>

      {/* Center: Nav links (only show if logged in) */}
      {isLoggedIn && (
        <nav className="nav-links" aria-label="Primary navigation">
          <Link to="/">Home</Link>
          <Link to="/events">Events</Link>
          <Link to="/teams">Teams</Link>
        </nav>
      )}

      {/* Right: Auth buttons */}
      <div className="logout-container">
        {isLoggedIn ? (
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();   // prevent full page reload
              logout();          // call your logout handler
            }}
            className="logout-btn"
          >
            Log out
          </a>
        ) : (
          <>
          <Link to="/login" className="logout-btn">
            Log in
          </Link>
          <Link to="/register" className="logout-btn">
            Register
          </Link>
        </>
      )}
      </div>
    </header>
  );
}
