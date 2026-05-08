import React, { useState } from 'react';
import { Send, MapPin, Calendar, Users, DollarSign } from 'lucide-react';
import './TripPlanner.css';

const TripPlanner = () => {
  const [prompt, setPrompt] = useState('');

  return (
    <div className="planner-container">
      <div className="planner-header">
        <h1>Design Your <span className="text-gradient">Experience</span></h1>
        <p>Tell us what you want to do, or fill out the details below.</p>
      </div>

      <div className="planner-grid">
        {/* Natural Language Input */}
        <div className="nlp-section glass-panel">
          <h3>Describe your dream trip</h3>
          <div className="prompt-box">
            <textarea 
              className="prompt-input" 
              placeholder="e.g. I want a cheap family trip to Tokyo for 5 days but we love expensive sushi dinners..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={4}
            />
          </div>
        </div>

        {/* Structured Inputs */}
        <div className="structured-section glass-panel">
          <h3>Quick Details</h3>
          
          <div className="form-grid">
            <div className="input-group">
              <label className="input-label"><MapPin size={16}/> Destination</label>
              <input type="text" className="input-field" placeholder="Where to?" />
            </div>
            
            <div className="input-group">
              <label className="input-label"><Calendar size={16}/> Dates</label>
              <input type="text" className="input-field" placeholder="Select dates" />
            </div>

            <div className="input-group">
              <label className="input-label"><Users size={16}/> Group Size</label>
              <select className="input-field">
                <option value="solo">Solo</option>
                <option value="couple">Couple</option>
                <option value="family">Family</option>
                <option value="friends">Friends Group</option>
              </select>
            </div>

            <div className="input-group">
              <label className="input-label"><DollarSign size={16}/> Budget Level</label>
              <select className="input-field">
                <option value="budget">Budget-friendly</option>
                <option value="moderate">Moderate</option>
                <option value="luxury">Luxury</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="action-row">
        <button className="btn btn-primary generate-btn">
          <Send size={18} />
          Generate Itinerary
        </button>
      </div>
    </div>
  );
};

export default TripPlanner;
