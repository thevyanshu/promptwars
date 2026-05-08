import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Map, Calendar, Sun } from 'lucide-react';
import './Home.css';

const Home = () => {
  return (
    <div className="home-container">
      <section className="hero">
        <h1 className="hero-title">
          Plan Your Next <span className="text-gradient">Adventure</span>
        </h1>
        <p className="hero-subtitle">
          AI-powered travel planning that adapts to your budget, preferences, and real-time conditions.
        </p>
        <Link to="/plan" className="btn btn-primary hero-btn">
          <Sparkles size={20} />
          Start Planning Now
        </Link>
      </section>

      <section className="features grid">
        <div className="feature-card glass-panel">
          <Map className="feature-icon" size={32} />
          <h3>Smart Itineraries</h3>
          <p>Optimized routes and activity pairings tailored just for you.</p>
        </div>
        <div className="feature-card glass-panel">
          <Sun className="feature-icon" size={32} />
          <h3>Real-Time Updates</h3>
          <p>Live adjustments for weather, flight delays, and unexpected closures.</p>
        </div>
        <div className="feature-card glass-panel">
          <Calendar className="feature-icon" size={32} />
          <h3>Seamless Scheduling</h3>
          <p>We respect your pace. Early riser or night owl, we've got you covered.</p>
        </div>
      </section>
    </div>
  );
};

export default Home;
