import React from 'react';
import DayCard from '../components/itinerary/DayCard';
import MapComponent from '../components/maps/MapComponent';
import './ItineraryView.css';

// Mock data for MVP preview
const mockItinerary = {
  budget_summary: "Stayed within the $1500 moderate budget.",
  ai_notes: "Weather looks clear. Be prepared for walking in the downtown area.",
  itinerary: [
    {
      day: 1,
      date: "2024-06-15",
      theme: "Arrival & City Highlights",
      activities: [
        {
          time_start: "10:00",
          time_end: "11:30",
          activity_name: "Check into Hotel",
          location: "The Grand Stay, Downtown",
          description: "Drop off bags and freshen up.",
          estimated_cost: "$0",
          booking_type: "hotel",
          dummy_booking_ref: "REF-HTL-9012"
        },
        {
          time_start: "12:00",
          time_end: "13:30",
          activity_name: "Lunch at Local Cafe",
          location: "Central Square",
          description: "Enjoy a light lunch and coffee to recover from the flight.",
          estimated_cost: "$25",
          booking_type: "dining"
        }
      ]
    }
  ]
};

const ItineraryView = () => {
  return (
    <div className="itinerary-view-container">
      <div className="itinerary-header">
        <h1>Your <span className="text-gradient">Itinerary</span> is Ready</h1>
        <div className="ai-summary glass-panel">
          <p><strong>Budget Summary:</strong> {mockItinerary.budget_summary}</p>
          <p><strong>AI Note:</strong> {mockItinerary.ai_notes}</p>
        </div>
      </div>

      <div className="itinerary-layout">
        <div className="itinerary-timeline-scroll">
          {mockItinerary.itinerary.map((day) => (
            <DayCard 
              key={day.day}
              dayNumber={day.day}
              date={day.date}
              theme={day.theme}
              activities={day.activities}
            />
          ))}
        </div>
        
        <div className="itinerary-map-sticky">
          <div className="glass-panel" style={{ height: 'calc(100vh - 120px)' }}>
             <MapComponent />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ItineraryView;
