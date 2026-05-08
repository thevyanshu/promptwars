import React from 'react';
import { Compass, Map, Heart, Star } from 'lucide-react';
import './Explore.css';

const MOCK_RECOMMENDATIONS = [
  {
    id: 1,
    title: "Kyoto Serenity",
    location: "Kyoto, Japan",
    image: "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?q=80&w=800&auto=format&fit=crop",
    tags: ["Culture", "Relaxation"],
    rating: 4.9
  },
  {
    id: 2,
    title: "Alpine Adventure",
    location: "Swiss Alps",
    image: "https://images.unsplash.com/photo-1531366936337-77b15a6e87b7?q=80&w=800&auto=format&fit=crop",
    tags: ["Nature", "Active"],
    rating: 4.8
  },
  {
    id: 3,
    title: "Bali Retreat",
    location: "Ubud, Indonesia",
    image: "https://images.unsplash.com/photo-1537996194471-e657df975ab4?q=80&w=800&auto=format&fit=crop",
    tags: ["Wellness", "Tropical"],
    rating: 4.7
  }
];

const Explore = () => {
  return (
    <div className="explore-container">
      <div className="explore-header">
        <h1>Discover <span className="text-gradient">Destinations</span></h1>
        <p className="text-muted">AI-curated recommendations based on global trends and your past preferences.</p>
      </div>

      <div className="discovery-grid">
        {MOCK_RECOMMENDATIONS.map((item) => (
          <div key={item.id} className="discovery-card glass-panel">
            <div className="card-image-wrapper">
              <img src={item.image} alt={item.title} className="card-image" />
              <button className="favorite-btn"><Heart size={20} /></button>
            </div>
            <div className="card-content">
              <div className="card-meta">
                <span className="location"><Map size={14} /> {item.location}</span>
                <span className="rating"><Star size={14} fill="currentColor" color="#fbbf24" /> {item.rating}</span>
              </div>
              <h3>{item.title}</h3>
              <div className="tags">
                {item.tags.map(tag => (
                  <span key={tag} className="tag">{tag}</span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Explore;
