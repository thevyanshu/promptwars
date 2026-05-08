from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class TripCreate(BaseModel):
    title: str
    start_date: date
    end_date: date
    preferences: dict = Field(default_factory=dict, description="e.g., {'budget': 'moderate', 'pace': 'relaxed', 'interests': ['history', 'food']}")
    constraints: dict = Field(default_factory=dict, description="e.g., {'dietary': ['vegetarian'], 'mobility': 'standard'}")
    natural_language_prompt: Optional[str] = None
    group_type: str = "solo" # solo, couple, family, friends

class TripResponse(TripCreate):
    id: str
    user_id: str
    status: str
    
    class Config:
        from_attributes = True

class ItineraryResponse(BaseModel):
    id: str
    trip_id: str
    version: int
    plan_data: dict
    status: str
    
    class Config:
        from_attributes = True
