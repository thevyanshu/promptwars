from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
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

@router.get("/{trip_id}/stream")
def stream_trip_itinerary(
    trip_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    # Check if already generated
    existing = db.query(Itinerary).filter(Itinerary.trip_id == trip_id).first()
    if existing:
        # Just return the JSON as a single SSE chunk
        def single_yield():
            yield f"data: {json.dumps(existing.plan_data)}\n\n"
        return StreamingResponse(single_yield(), media_type="text/event-stream")
        
    trip_details = {
        "title": trip.title,
        "start_date": str(trip.start_date),
        "end_date": str(trip.end_date),
        "preferences": trip.preferences,
        "constraints": trip.constraints
    }

    # Generate and save after stream finishes
    def event_stream():
        full_json_str = ""
        for chunk in planner_ai.stream_generate_plan(trip_details):
            # Parse the chunk to accumulate the final JSON
            # chunk looks like: "data: {\"itinerary\"...\n\n"
            data_str = chunk[6:-2].replace('\\n', '\n')
            full_json_str += data_str
            yield chunk
            
        # Try to save to DB at the end
        try:
            final_plan = json.loads(full_json_str)
            final_plan = get_dummy_booking_data(final_plan)
            itinerary = Itinerary(
                trip_id=trip.id,
                plan_data=final_plan,
                generation_model="gemini-2.5-pro",
                status="ready"
            )
            db.add(itinerary)
            trip.status = "ready"
            db.commit()
        except Exception as e:
            print(f"Failed to save streamed itinerary: {e}")

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@router.post("/{trip_id}/chat")
def chat_modify_itinerary(
    trip_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """
    Conversational endpoint to modify a specific part of the itinerary.
    The frontend sends the user message and the current itinerary JSON.
    The AI modifies only the relevant parts and returns the full updated itinerary.
    """
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    user_message = payload.get("message", "")
    current_itinerary = payload.get("current_itinerary", {})

    if not user_message:
        raise HTTPException(status_code=400, detail="Message is required")

    chat_prompt = f"""You are modifying an existing travel itinerary based on user feedback.

CURRENT ITINERARY:
{json.dumps(current_itinerary, indent=2)}

USER REQUEST:
"{user_message}"

INSTRUCTIONS:
1. Modify ONLY the parts of the itinerary that the user is asking about.
2. Keep all other days and activities exactly the same.
3. Maintain the exact same JSON schema structure as the current itinerary.
4. Include lat and lng coordinates for any new locations.
5. Update the budget_summary if costs changed.
6. Add a brief note about what you changed in ai_notes.

Return the FULL updated itinerary JSON (not just the changed parts)."""

    try:
        response = planner_ai.model.generate_content(
            chat_prompt,
            generation_config={"response_mime_type": "application/json"}
        ) if planner_ai.model else None

        if response:
            updated_plan = json.loads(response.text)
            updated_plan = get_dummy_booking_data(updated_plan)

            # Save updated version to DB
            existing = db.query(Itinerary).filter(
                Itinerary.trip_id == trip_id
            ).order_by(Itinerary.version.desc()).first()

            if existing:
                existing.plan_data = updated_plan
                existing.version += 1
            else:
                new_itinerary = Itinerary(
                    trip_id=trip.id,
                    plan_data=updated_plan,
                    generation_model="gemini-2.5-pro",
                    status="ready"
                )
                db.add(new_itinerary)

            db.commit()

            return {
                "reply": f"Done! I've updated your itinerary based on your request: \"{user_message}\"",
                "updated_itinerary": updated_plan
            }
        else:
            # Mock fallback for local dev without GCP
            return {
                "reply": f"[Mock] I would modify the itinerary based on: \"{user_message}\". Connect Vertex AI for real modifications.",
                "updated_itinerary": current_itinerary
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat modification failed: {str(e)}")
