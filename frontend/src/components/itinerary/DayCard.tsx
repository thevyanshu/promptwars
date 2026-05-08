import React from 'react';
import { Clock, MapPin, CheckCircle, Tag } from 'lucide-react';
import './DayCard.css';

interface Activity {
  time_start: string;
  time_end: string;
  activity_name: string;
  location: string;
  description: string;
  estimated_cost: string;
  booking_type: string;
  dummy_booking_ref?: string;
  status?: string;
}

interface DayCardProps {
  dayNumber: number;
  date: string;
  theme: string;
  activities: Activity[];
}

const DayCard: React.FC<DayCardProps> = ({ dayNumber, date, theme, activities }) => {
  return (
    <div className="day-card glass-panel">
      <div className="day-header">
        <div className="day-badge">Day {dayNumber}</div>
        <div className="day-title-group">
          <h2>{theme}</h2>
          <span className="day-date">{date}</span>
        </div>
      </div>
      
      <div className="timeline">
        {activities.map((activity, idx) => (
          <div key={idx} className="timeline-item">
            <div className="timeline-time">
              <span>{activity.time_start}</span>
              <span className="time-end">{activity.time_end}</span>
            </div>
            
            <div className="timeline-content">
              <div className="timeline-marker"></div>
              
              <div className="activity-details">
                <h3>{activity.activity_name}</h3>
                <p className="activity-desc">{activity.description}</p>
                
                <div className="activity-meta">
                  <span className="meta-item"><MapPin size={14}/> {activity.location}</span>
                  <span className="meta-item"><Tag size={14}/> {activity.estimated_cost}</span>
                  
                  {activity.dummy_booking_ref && (
                    <span className="meta-item booking-success">
                      <CheckCircle size={14}/> Ref: {activity.dummy_booking_ref}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DayCard;
