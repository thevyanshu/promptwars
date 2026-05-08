import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, JSON, Date, Integer
from sqlalchemy.dialects.postgresql import UUID # for postgres, but we'll use a generic String for MVP SQLite compatibility
from app.infrastructure.database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False) # Firebase UID
    title = Column(String, nullable=False)
    status = Column(String, default="planning") # planning, generated, active, completed
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Store NLP prompt, budget levels, group size
    preferences = Column(JSON, default={})
    constraints = Column(JSON, default={})
    metadata_info = Column(JSON, default={}) # Replaced metadata with metadata_info to avoid conflict with Base.metadata
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Itinerary(Base):
    __tablename__ = "itineraries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String, index=True, nullable=False)
    version = Column(Integer, default=1)
    plan_data = Column(JSON, nullable=False)
    generation_model = Column(String, default="gemini-2.5-pro")
    status = Column(String, default="ready")
    
    generated_at = Column(DateTime, default=datetime.utcnow)
