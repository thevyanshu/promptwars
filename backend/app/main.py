from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1 import trips, places, planner

app.include_router(trips.router, prefix=f"{settings.API_V1_STR}/trips", tags=["trips"])
app.include_router(places.router, prefix=f"{settings.API_V1_STR}/places", tags=["places"])
app.include_router(planner.router, prefix=f"{settings.API_V1_STR}/planner", tags=["planner"])

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.get("/readyz")
def ready_check():
    return {"status": "ready"}
