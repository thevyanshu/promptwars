from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.infrastructure.database import get_db
from app.domain.models.trip import Trip
from app.api.v1.schemas import TripCreate, TripResponse
from app.api.middleware.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(trip_in: TripCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    # Create new trip
    preferences = trip_in.preferences
    preferences["natural_language_prompt"] = trip_in.natural_language_prompt
    preferences["group_type"] = trip_in.group_type
    
    new_trip = Trip(
        user_id=user_id,
        title=trip_in.title,
        start_date=trip_in.start_date,
        end_date=trip_in.end_date,
        preferences=preferences,
        constraints=trip_in.constraints
    )
    
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    
    # In Phase 2: We would publish a message to Pub/Sub here to start AI Generation
    return new_trip

@router.get("/", response_model=List[TripResponse])
def get_user_trips(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    trips = db.query(Trip).filter(Trip.user_id == user_id).all()
    return trips

@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip
