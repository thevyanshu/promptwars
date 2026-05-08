from sqlalchemy.orm import Session
from app.domain.models.trip import Trip, Itinerary
from app.domain.services.email_service import email_service
import random
import uuid

class RealtimeService:
    def check_for_disruptions(self, db: Session):
        """
        Background job triggered by Cloud Scheduler.
        Checks active trips for flight or weather disruptions and sends alerts.
        """
        # 1. Fetch all "ready" itineraries (in a real app, only future/active trips)
        itineraries = db.query(Itinerary).filter(Itinerary.status == "ready").all()
        
        disrupted_count = 0
        
        for itinerary in itineraries:
            # 2. Simulate external API check (e.g. OpenMeteo for weather, Amadeus for flights)
            # We mock a 10% chance of a disruption occurring during this check for MVP demo purposes.
            is_disrupted = random.random() < 0.10
            
            if is_disrupted:
                # 3. Modify the itinerary to reflect the disruption
                disruption_msg = "ALERT: Incoming storm detected. Your afternoon outdoor activity has been replaced with a museum visit."
                
                plan = itinerary.plan_data
                if "ai_notes" in plan:
                    plan["ai_notes"] = disruption_msg + " | " + plan["ai_notes"]
                else:
                    plan["ai_notes"] = disruption_msg
                
                # Flag the itinerary as updated
                itinerary.plan_data = plan
                # Incrementing version to let clients know it changed
                itinerary.version += 1 
                
                trip = db.query(Trip).filter(Trip.id == itinerary.trip_id).first()
                
                # 4. Save to DB
                db.commit()
                
                # 5. Send Email Alert
                email_service.send_alert(
                    user_email="user@example.com", # In production, get from user profile
                    subject=f"Trip Update: {trip.title}",
                    message=disruption_msg
                )
                
                disrupted_count += 1
                
        return {"checked": len(itineraries), "disruptions_found": disrupted_count}

realtime_service = RealtimeService()
