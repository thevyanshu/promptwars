import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Send, MapPin, Calendar, Users, DollarSign, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import './TripPlanner.css';

const TripPlanner = () => {
  const navigate = useNavigate();
  
  const [prompt, setPrompt] = useState('');
  const [title, setTitle] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [groupType, setGroupType] = useState('solo');
  const [budget, setBudget] = useState('moderate');

  // Mutation to create trip and immediately trigger generation
  const generateMutation = useMutation({
    mutationFn: async () => {
      // 1. Create Trip
      const tripData = {
        title: title || `Trip to ${prompt.slice(0, 15)}...`,
        start_date: startDate || new Date().toISOString().split('T')[0],
        end_date: endDate || new Date(Date.now() + 86400000 * 3).toISOString().split('T')[0],
        preferences: { budget },
        constraints: {},
        natural_language_prompt: prompt,
        group_type: groupType
      };
      const trip = await api.createTrip(tripData);
      
      // We no longer trigger generation here. The ItineraryView will trigger it via SSE stream on mount.
      return trip.id;
    },
    onSuccess: (tripId) => {
      navigate(`/itinerary/${tripId}`);
    },
    onError: (error) => {
      console.error("Generation failed:", error);
      alert("Failed to start itinerary generation.");
    }
  });

  const handleSubmit = () => {
    if (!prompt && !title) {
      alert("Please enter a destination or describe your dream trip.");
      return;
    }
    generateMutation.mutate();
  };

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
              <label className="input-label"><MapPin size={16}/> Destination / Title</label>
              <input type="text" className="input-field" placeholder="Where to?" value={title} onChange={e => setTitle(e.target.value)} />
            </div>
            
            <div className="input-group">
              <label className="input-label"><Calendar size={16}/> Start Date</label>
              <input type="date" className="input-field" value={startDate} onChange={e => setStartDate(e.target.value)} />
            </div>
            
            <div className="input-group">
              <label className="input-label"><Calendar size={16}/> End Date</label>
              <input type="date" className="input-field" value={endDate} onChange={e => setEndDate(e.target.value)} />
            </div>

            <div className="input-group">
              <label className="input-label"><Users size={16}/> Group Size</label>
              <select className="input-field" value={groupType} onChange={e => setGroupType(e.target.value)}>
                <option value="solo">Solo</option>
                <option value="couple">Couple</option>
                <option value="family">Family</option>
                <option value="friends">Friends Group</option>
              </select>
            </div>

            <div className="input-group">
              <label className="input-label"><DollarSign size={16}/> Budget Level</label>
              <select className="input-field" value={budget} onChange={e => setBudget(e.target.value)}>
                <option value="budget">Budget-friendly</option>
                <option value="moderate">Moderate</option>
                <option value="luxury">Luxury</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="action-row">
        <button 
          className="btn btn-primary generate-btn" 
          onClick={handleSubmit}
          disabled={generateMutation.isPending}
        >
          {generateMutation.isPending ? <Loader2 className="animate-spin" size={18} /> : <Send size={18} />}
          {generateMutation.isPending ? 'Starting Generation...' : 'Generate Itinerary'}
        </button>
      </div>
    </div>
  );
};

export default TripPlanner;
