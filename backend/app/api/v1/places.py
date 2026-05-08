from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.middleware.auth import get_current_user
from app.infrastructure.maps.client import maps_client

router = APIRouter()

@router.get("/search")
def search_places(
    query: str = Query(..., description="Search query"),
    location: str = Query(None, description="Lat,Lng bias"),
    user_id: str = Depends(get_current_user)
):
    result = maps_client.search_places(query, location)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
    return result

@router.get("/{place_id}/details")
def get_place_details(
    place_id: str,
    user_id: str = Depends(get_current_user)
):
    result = maps_client.get_place_details(place_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
    return result
