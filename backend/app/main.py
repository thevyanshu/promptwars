import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.config import settings
from app.api.middleware.security import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    StructuredLoggingMiddleware,
)

# Configure structured logging for Cloud Logging compatibility
logging.basicConfig(
    level=logging.INFO,
    format='{"severity":"%(levelname)s","message":"%(message)s","time":"%(asctime)s"}',
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --- Production CORS ---
# In production, restrict to known origins. Locally, allow all.
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

if "*" in ALLOWED_ORIGINS:
    # Local dev / MVP fallback
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

# --- Security Middleware Stack ---
# Order matters: outermost middleware executes first
app.add_middleware(GZipMiddleware, minimum_size=500)           # Compress responses > 500 bytes
app.add_middleware(SecurityHeadersMiddleware)                    # HSTS, CSP, X-Frame-Options
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)  # 100 req/min per IP
app.add_middleware(StructuredLoggingMiddleware)                  # JSON logs for Cloud Logging

# --- Routes ---
from app.api.v1 import trips, places, planner, realtime

app.include_router(trips.router, prefix=f"{settings.API_V1_STR}/trips", tags=["trips"])
app.include_router(places.router, prefix=f"{settings.API_V1_STR}/places", tags=["places"])
app.include_router(planner.router, prefix=f"{settings.API_V1_STR}/planner", tags=["planner"])
app.include_router(realtime.router, prefix=f"{settings.API_V1_STR}/realtime", tags=["realtime"])

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.get("/readyz")
def ready_check():
    return {"status": "ready"}
