import googlemaps
import json
from typing import Dict, Any, Optional
import redis
from app.config import settings

# In-memory fallback if Redis is unavailable locally
_fallback_cache: Dict[str, str] = {}

class MapsClient:
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.gmaps = googlemaps.Client(key=self.api_key) if self.api_key else None
        
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            self.redis_client.ping()
        except redis.ConnectionError:
            print("Warning: Redis unavailable, using in-memory cache for Maps API.")
            self.redis_client = None

    def _get_cache(self, key: str) -> Optional[dict]:
        if self.redis_client:
            val = self.redis_client.get(key)
        else:
            val = _fallback_cache.get(key)
        return json.loads(val) if val else None

    def _set_cache(self, key: str, data: dict, expire_seconds: int = 86400):
        val = json.dumps(data)
        if self.redis_client:
            self.redis_client.setex(key, expire_seconds, val)
        else:
            _fallback_cache[key] = val

    def search_places(self, query: str, location: str = None) -> dict:
        if not self.gmaps:
            return {"status": "error", "message": "Google Maps API Key not configured"}
            
        cache_key = f"places:search:{query}:{location}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
            
        try:
            # We use text_search as a simple proxy for MVP
            result = self.gmaps.places(query=query, location=location)
            self._set_cache(cache_key, result, 86400) # cache for 24h
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_place_details(self, place_id: str) -> dict:
        if not self.gmaps:
            return {"status": "error", "message": "Google Maps API Key not configured"}
            
        cache_key = f"places:details:{place_id}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
            
        try:
            result = self.gmaps.place(place_id=place_id)
            self._set_cache(cache_key, result, 86400)
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

maps_client = MapsClient()
