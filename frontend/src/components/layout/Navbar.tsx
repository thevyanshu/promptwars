import React from 'react';
import { Link } from 'react-router-dom';
import { Compass, User } from 'lucide-react';
import './Navbar.css';

const Navbar = () => {
  return (
    <header className="navbar glass-panel">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <Compass className="logo-icon" size={28} />
          <span className="text-gradient">WanderAI</span>
        </Link>
        
        <nav className="navbar-links">
          <Link to="/plan" className="nav-link">Plan a Trip</Link>
          <Link to="/explore" className="nav-link">Explore</Link>
        </nav>
        
        <div className="navbar-actions">
          <button className="btn btn-secondary login-btn" onClick={() => {
            alert('Signed in as Guest for local MVP. Firebase Auth will be wired up in production.');
          }}>
            <User size={18} />
            <span>Sign In</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
