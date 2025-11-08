import React, { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import "../styles/header.css";
import logo from "../assets/OneSky-logo.png";
import { useAuth } from "../context/AuthProvider";

/**
 * Header
 * Full-width top bar with three sections:
 * - Left: Brand logo
 * - Center: Navigation links
 * - Right: Logout button (if logged in) or Login/Register links (if not logged in)
 * - Mobile: Hamburger menu with dropdown navigation
 */
export default function Header() {
  const { user, logout, isAuthenticated } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const headerRef = useRef(null);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  const handleLogout = (e) => {
    e.preventDefault();
    logout();
    closeMobileMenu();
  };

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (headerRef.current && !headerRef.current.contains(event.target)) {
        closeMobileMenu();
      }
    };

    if (isMobileMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      // Prevent body scroll when menu is open
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.body.style.overflow = '';
    };
  }, [isMobileMenuOpen]);

  return (
    <header className="header" role="banner" ref={headerRef}>
      {/* Left: Logo */}
      <div className="logo-container">
        <Link to="/" aria-label="OneSky Home" onClick={closeMobileMenu}>
          <img src={logo} alt="OneSky Logo" className="logo" />
        </Link>
      </div>

      {/* Center: Nav links (desktop) */}
      <nav className="nav-links" aria-label="Primary navigation">
        <Link to="/">Home</Link>
        <Link to="/events">Events</Link>
        <Link to="/teams">Teams</Link>
        <Link to="/profile">Profile</Link>
      </nav>

      {/* Right: Auth buttons (desktop) */}
      <div className="logout-container">
        {isAuthenticated ? (
          <a
            href="#"
            onClick={handleLogout}
            className="logout-btn"
          >
            Log out
          </a>
        ) : (
          <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
            <Link to="/login" className="logout-btn" style={{ textDecoration: "none" }}>
              Login
            </Link>
            <Link to="/register" className="logout-btn" style={{ textDecoration: "none" }}>
              Register
            </Link>
          </div>
        )}
      </div>

      {/* Mobile: Hamburger menu button */}
      <button
        className="mobile-menu-toggle"
        onClick={toggleMobileMenu}
        aria-label="Toggle navigation menu"
        aria-expanded={isMobileMenuOpen}
      >
        <span className={`hamburger ${isMobileMenuOpen ? 'open' : ''}`}>
          <span></span>
          <span></span>
          <span></span>
        </span>
      </button>

      {/* Mobile: Backdrop overlay */}
      {isMobileMenuOpen && (
        <div 
          className="mobile-nav-backdrop" 
          onClick={closeMobileMenu}
          aria-hidden="true"
        />
      )}

      {/* Mobile: Dropdown menu */}
      <nav 
        className={`mobile-nav ${isMobileMenuOpen ? 'open' : ''}`}
        aria-label="Mobile navigation"
      >
        <Link to="/" onClick={closeMobileMenu}>Home</Link>
        <Link to="/events" onClick={closeMobileMenu}>Events</Link>
        <Link to="/teams" onClick={closeMobileMenu}>Teams</Link>
        <Link to="/profile" onClick={closeMobileMenu}>Profile</Link>
        {isAuthenticated ? (
          <a
            href="#"
            onClick={handleLogout}
            className="mobile-logout-btn"
          >
            Log out
          </a>
        ) : (
          <>
            <Link to="/login" onClick={closeMobileMenu} className="mobile-logout-btn">
              Login
            </Link>
            <Link to="/register" onClick={closeMobileMenu} className="mobile-logout-btn">
              Register
            </Link>
          </>
        )}
      </nav>
    </header>
  );
}
