// Footer Component Code

import React from 'react';
import './Footer.css';

function Footer() {
  return (
    <footer className='footer'>
      <div className='footer-content'>
        <p>&copy; {new Date().getFullYear()} OneSky. All rights reserved.</p>
        <nav className='footer-links'>
          <a href='/terms'>Terms of Service</a>
          {/* This can be changed to anything necessary - I've just put it in as a placeholder like most other things */}
        </nav>
      </div>
    </footer>
  );
}

export default Footer;
