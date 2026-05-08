from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.domain.services.realtime_service import realtime_service

router = APIRouter()

@router.post("/check-disruptions")
def trigger_disruption_check(db: Session = Depends(get_db)):
    """
    Webhook meant to be triggered periodically by Google Cloud Scheduler.
    It scans active itineraries for flight/weather changes and sends real-time alerts.
    """
    # In production, this should be secured via an API Key or GCP service account auth
    results = realtime_service.check_for_disruptions(db)
    return {
        "status": "success",
        "message": f"Checked {results['checked']} itineraries. Found {results['disruptions_found']} disruptions.",
        "details": results
    }
