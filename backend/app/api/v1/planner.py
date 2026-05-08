from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.domain.models.trip import Trip, Itinerary
from app.api.middleware.auth import get_current_user
from app.infrastructure.ai.client import planner_ai
import uuid
import json

router = APIRouter()

def get_dummy_booking_data(plan_data: dict) -> dict:
    """
    Simulates booking data integration (flights, hotels) using dummy data.
    In a real scenario, this would call Amadeus, Stripe, etc.
    """
    # Simply inject dummy confirmation numbers into the plan for 'hotel' or 'flight'
    for day in plan_data.get("itinerary", []):
        for activity in day.get("activities", []):
            if activity.get("booking_type") in ["hotel", "flight"]:
                activity["dummy_booking_ref"] = f"REF-{str(uuid.uuid4())[:8].upper()}"
                activity["status"] = "simulated_confirmed"
    return plan_data

def background_generate_plan(trip_id: str, db: Session):
    """
    Background task to generate the itinerary.
    In production, this would be a Pub/Sub + Cloud Task worker.
    """
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        return
        
    trip.status = "generating"
    db.commit()
    
    trip_details = {
        "title": trip.title,
        "start_date": str(trip.start_date),
        "end_date": str(trip.end_date),
        "preferences": trip.preferences,
        "constraints": trip.constraints
    }
    
    # 1. Call Vertex AI
    generated_plan = planner_ai.generate_plan(trip_details)
    
    if generated_plan.get("status") == "error":
        trip.status = "failed"
        db.commit()
        return
        
    # 2. Integrate Simulated Bookings
    final_plan = get_dummy_booking_data(generated_plan)
    
    # 3. Save Itinerary
    itinerary = Itinerary(
        trip_id=trip.id,
        plan_data=final_plan,
        generation_model="gemini-2.5-pro",
        status="ready"
    )
    db.add(itinerary)
    trip.status = "ready"
    db.commit()

@router.post("/{trip_id}/generate")
def request_plan_generation(
    trip_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """
    Triggers the async generation of the trip itinerary.
    """
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    # Fire and forget (in MVP we use FastAPI BackgroundTasks, in Prod use Pub/Sub)
    background_tasks.add_task(background_generate_plan, trip.id, db)
    
    return {"status": "accepted", "message": "Itinerary generation started in background."}

@router.get("/{trip_id}/itinerary")
def get_trip_itinerary(
    trip_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    # Verify ownership
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    itinerary = db.query(Itinerary).filter(Itinerary.trip_id == trip_id).order_by(Itinerary.version.desc()).first()
    if not itinerary:
        return {"status": "pending", "message": "Itinerary not ready yet."}
        
    return itinerary
