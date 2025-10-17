// Header Component Code
// Will need to link to css and logo asset, a few other things,
// just put most of them in as placeholders until it was linked up
// to debug and fix so change as required

import React from 'react';
import './Header.css';
import logo from 'assets/OneSky-logo.png';

function Header() {
  return (
    <div className='header'>
      <div className='logo-container'>
        <img src={logo} alt='OneSky Logo' className='logo' />
      </div>
      <nav className='nav-links'>
        <a href='/home'>Home</a>
        <a href='/logout'>Log Out</a>
      </nav>
    </div>
  );
}

export default Header;
