import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Map, Calendar, ArrowRight, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import './Explore.css';

const Explore = () => {
  const { data: trips, isLoading, error } = useQuery({
    queryKey: ['trips'],
    queryFn: () => api.getTrips()
  });

  if (isLoading) {
    return (
      <div className="explore-container loading-state">
        <Loader2 className="animate-spin" size={48} color="var(--primary)" />
        <p>Loading your adventures...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="explore-container">
        <div className="glass-panel">
          <h2>Oops!</h2>
          <p>Failed to load your trips. Please make sure you are signed in.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="explore-container">
      <div className="explore-header">
        <h1>My <span className="text-gradient">Adventures</span></h1>
        <p className="text-muted">Return to your generated itineraries and keep exploring the world.</p>
      </div>

      <div className="discovery-grid">
        {trips && trips.length > 0 ? (
          trips.map((trip: any) => (
            <Link to={`/itinerary/${trip.id}`} key={trip.id} className="discovery-card glass-panel no-underline">
              <div className="card-image-wrapper">
                <div className="card-placeholder-bg">
                   <Map size={48} color="white" opacity={0.2} />
                </div>
              </div>
              <div className="card-content">
                <div className="card-meta">
                  <span className="location"><Map size={14} /> {trip.title}</span>
                  <span className="status-badge">{trip.status}</span>
                </div>
                <h3>{trip.title}</h3>
                <p className="trip-dates">
                  <Calendar size={14} /> {trip.start_date} to {trip.end_date}
                </p>
                <div className="view-link">
                  View Itinerary <ArrowRight size={16} />
                </div>
              </div>
            </Link>
          ))
        ) : (
          <div className="empty-state glass-panel">
            <h3>No trips yet!</h3>
            <p>Ready to plan your first AI-powered adventure?</p>
            <Link to="/plan" className="btn btn-primary">Start Planning</Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Explore;
