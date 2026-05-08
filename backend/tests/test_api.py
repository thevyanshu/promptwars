from fastapi.testclient import TestClient
from app.main import app
from app.infrastructure.database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
import pytest

# Test client
client = TestClient(app)

# Test DB Setup
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_trip():
    payload = {
        "title": "Test Paris Trip",
        "start_date": "2024-08-01",
        "end_date": "2024-08-05",
        "preferences": {"budget": "moderate"},
        "constraints": {"dietary": ["vegan"]},
        "natural_language_prompt": "I want to see the Eiffel Tower",
        "group_type": "couple"
    }
    
    # Needs auth token bypass (we defined 'local-dev-token' in middleware)
    headers = {"Authorization": "Bearer local-dev-token"}
    
    response = client.post("/api/v1/trips/", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Paris Trip"
    assert "id" in data
    
    return data["id"] # Return ID for next tests

def test_get_user_trips():
    headers = {"Authorization": "Bearer local-dev-token"}
    response = client.get("/api/v1/trips/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_trigger_planner_generation():
    headers = {"Authorization": "Bearer local-dev-token"}
    # Fetch trips to get a valid ID
    response = client.get("/api/v1/trips/", headers=headers)
    trip_id = response.json()[0]["id"]
    
    gen_response = client.post(f"/api/v1/planner/{trip_id}/generate", headers=headers)
    assert gen_response.status_code == 200
    assert gen_response.json()["status"] == "accepted"

def test_get_itinerary_pending():
    headers = {"Authorization": "Bearer local-dev-token"}
    response = client.get("/api/v1/trips/", headers=headers)
    trip_id = response.json()[0]["id"]
    
    itin_response = client.get(f"/api/v1/planner/{trip_id}/itinerary", headers=headers)
    # The generation is async (background task), so it might be pending or completed depending on speed
    # But it shouldn't 404
    assert itin_response.status_code == 200
