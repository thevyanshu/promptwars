"""
Security middleware for production hardening.
Adds security headers, rate limiting, and structured logging.
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import time
import logging
import json

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injects OWASP-recommended security headers into every response.
    """
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://maps.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https://*.googleapis.com https://*.gstatic.com; "
            "connect-src 'self' https://*.googleapis.com https://*.run.app; "
            "frame-src 'none';"
        )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter.
    Limits each IP to a configurable number of requests per window.
    In production, use Redis-backed rate limiting via Memorystore.
    """

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ("/healthz", "/readyz"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Prune old timestamps outside the current window
        self.request_counts[client_ip] = [
            ts for ts in self.request_counts[client_ip]
            if now - ts < self.window_seconds
        ]

        if len(self.request_counts[client_ip]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                content=json.dumps({"detail": "Rate limit exceeded. Try again later."}),
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": str(self.window_seconds)}
            )

        self.request_counts[client_ip].append(now)
        return await call_next(request)


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every request in structured JSON format compatible with Google Cloud Logging.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        log_entry = {
            "severity": "INFO" if response.status_code < 400 else "WARNING" if response.status_code < 500 else "ERROR",
            "httpRequest": {
                "requestMethod": request.method,
                "requestUrl": str(request.url),
                "status": response.status_code,
                "latency": f"{duration_ms}ms",
                "remoteIp": request.client.host if request.client else "unknown",
                "userAgent": request.headers.get("user-agent", "unknown"),
            },
        }

        if response.status_code >= 400:
            logger.warning(json.dumps(log_entry))
        else:
            logger.info(json.dumps(log_entry))

        return response
