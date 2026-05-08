import React from 'react';
import { Link } from 'react-router-dom';
import { Compass, User, LogOut } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, signInWithGoogle, logout } = useAuth();

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
          {user ? (
            <div className="user-info">
              <img 
                src={user.photoURL || ''} 
                alt={user.displayName || 'User'} 
                className="user-avatar"
              />
              <span className="user-name">{user.displayName?.split(' ')[0]}</span>
              <button className="btn btn-secondary login-btn" onClick={logout} aria-label="Sign out">
                <LogOut size={18} />
              </button>
            </div>
          ) : (
            <button className="btn btn-secondary login-btn" onClick={signInWithGoogle}>
              <User size={18} />
              <span>Sign In</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
