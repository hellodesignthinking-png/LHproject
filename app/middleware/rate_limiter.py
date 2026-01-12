"""
Production-Grade Rate Limiting Middleware
==========================================
Prevents API abuse and ensures fair resource usage
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class RateLimiter(BaseHTTPMiddleware):
    """
    Rate limiting middleware with multiple strategies:
    - IP-based rate limiting
    - Endpoint-specific limits
    - Sliding window algorithm
    - Automatic cleanup of old records
    """
    
    def __init__(self, app, default_limit: int = 100, window_minutes: int = 15):
        super().__init__(app)
        
        # Default limits: 100 requests per 15 minutes
        self.default_limit = default_limit
        self.window_minutes = window_minutes
        
        # Endpoint-specific limits (requests per window)
        self.endpoint_limits = {
            "/api/v9/real/generate-report": (10, 15),  # 10 requests per 15 minutes
            "/api/v9/real/analyze-land": (20, 15),      # 20 requests per 15 minutes
            "/api/v9/real/health": (100, 1),            # 100 requests per minute
        }
        
        # Storage: {ip_address: {endpoint: [(timestamp, request_count), ...]}}
        self.request_history: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        
        # Last cleanup time
        self.last_cleanup = datetime.now()
        
        logger.info(f"✅ Rate Limiter initialized: {default_limit} req/{window_minutes}min (default)")
        for endpoint, (limit, window) in self.endpoint_limits.items():
            logger.info(f"   📊 {endpoint}: {limit} req/{window}min")
    
    async def dispatch(self, request: Request, call_next):
        """
        Main rate limiting logic
        """
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Get endpoint path
        endpoint = request.url.path
        
        # Check if rate limit should be applied
        if not self._should_apply_rate_limit(endpoint):
            return await call_next(request)
        
        # Get limit configuration
        limit, window_minutes = self._get_limit_config(endpoint)
        
        # Check rate limit
        is_allowed, remaining, reset_time = self._check_rate_limit(
            client_ip, endpoint, limit, window_minutes
        )
        
        # Cleanup old records periodically (every 5 minutes)
        if (datetime.now() - self.last_cleanup).total_seconds() > 300:
            self._cleanup_old_records()
        
        if not is_allowed:
            # Rate limit exceeded
            logger.warning(f"⚠️ Rate limit exceeded: {client_ip} on {endpoint}")
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Too many requests. Please try again in {reset_time} seconds.",
                        "details": {
                            "limit": limit,
                            "window_minutes": window_minutes,
                            "retry_after": reset_time
                        }
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request
        Handles proxy headers (X-Forwarded-For, X-Real-IP)
        """
        # Try X-Forwarded-For first (for proxies)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Try X-Real-IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _should_apply_rate_limit(self, endpoint: str) -> bool:
        """
        Determine if rate limiting should be applied to this endpoint
        """
        # Don't rate limit static files
        if endpoint.startswith("/static/") or endpoint.startswith("/docs"):
            return False
        
        # Don't rate limit favicon
        if endpoint == "/favicon.ico":
            return False
        
        # Don't rate limit health and status endpoints
        if endpoint == "/health" or "/status" in endpoint:
            return False
        
        # Don't rate limit analysis status polling (prevent 429 errors)
        if "/api/analysis/projects/" in endpoint and endpoint.endswith("/status"):
            return False
        
        return True
    
    def _get_limit_config(self, endpoint: str) -> Tuple[int, int]:
        """
        Get rate limit configuration for endpoint
        Returns: (requests_limit, window_minutes)
        """
        return self.endpoint_limits.get(endpoint, (self.default_limit, self.window_minutes))
    
    def _check_rate_limit(
        self, 
        client_ip: str, 
        endpoint: str, 
        limit: int, 
        window_minutes: int
    ) -> Tuple[bool, int, int]:
        """
        Check if request is within rate limit
        
        Returns:
            (is_allowed, remaining_requests, reset_time_seconds)
        """
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Get request history for this client and endpoint
        history = self.request_history[client_ip][endpoint]
        
        # Remove requests outside the time window
        history[:] = [(ts, count) for ts, count in history if ts > window_start]
        
        # Count requests in current window
        current_count = sum(count for _, count in history)
        
        # Check if limit exceeded
        if current_count >= limit:
            # Calculate reset time (oldest request + window)
            if history:
                oldest_ts = history[0][0]
                reset_seconds = int((oldest_ts + timedelta(minutes=window_minutes) - now).total_seconds())
            else:
                reset_seconds = window_minutes * 60
            
            return False, 0, max(reset_seconds, 1)
        
        # Record this request
        history.append((now, 1))
        
        # Calculate remaining requests
        remaining = limit - current_count - 1
        
        # Calculate reset time
        reset_seconds = window_minutes * 60
        
        return True, remaining, reset_seconds
    
    def _cleanup_old_records(self):
        """
        Clean up old request records to prevent memory bloat
        """
        now = datetime.now()
        cutoff = now - timedelta(hours=1)  # Remove records older than 1 hour
        
        cleaned_ips = 0
        for ip in list(self.request_history.keys()):
            for endpoint in list(self.request_history[ip].keys()):
                # Remove old records
                history = self.request_history[ip][endpoint]
                history[:] = [(ts, count) for ts, count in history if ts > cutoff]
                
                # Remove empty endpoint histories
                if not history:
                    del self.request_history[ip][endpoint]
            
            # Remove empty IP records
            if not self.request_history[ip]:
                del self.request_history[ip]
                cleaned_ips += 1
        
        self.last_cleanup = now
        
        if cleaned_ips > 0:
            logger.info(f"🧹 Cleaned up {cleaned_ips} old IP records")


class RateLimitConfig:
    """
    Configuration presets for different environments
    """
    
    @staticmethod
    def development():
        """Lenient limits for development"""
        return {
            "default_limit": 1000,
            "window_minutes": 15,
            "endpoint_limits": {
                "/api/v9/real/generate-report": (100, 15),
                "/api/v9/real/analyze-land": (200, 15),
            }
        }
    
    @staticmethod
    def production():
        """Strict limits for production"""
        return {
            "default_limit": 100,
            "window_minutes": 15,
            "endpoint_limits": {
                "/api/v9/real/generate-report": (10, 15),   # Heavy endpoint
                "/api/v9/real/analyze-land": (20, 15),
                "/api/v9/real/health": (100, 1),
            }
        }
    
    @staticmethod
    def testing():
        """No limits for testing"""
        return {
            "default_limit": 999999,
            "window_minutes": 1,
            "endpoint_limits": {}
        }
