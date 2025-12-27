"""
ZeroSite v4.0 Middleware
========================

Rate Limiting, Logging, Error Handling

Author: ZeroSite Security Team
Date: 2025-12-27
Version: 1.0
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import logging
from typing import Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== Rate Limiter ====================

limiter = Limiter(key_func=get_remote_address)


# ==================== Request Logging Middleware ====================

async def log_requests_middleware(request: Request, call_next: Callable):
    """
    모든 요청을 로깅하는 미들웨어
    
    Args:
        request: FastAPI Request
        call_next: 다음 미들웨어/핸들러
        
    Returns:
        Response
    """
    start_time = time.time()
    
    # Request 정보 로깅
    logger.info(
        f"Incoming request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    try:
        response = await call_next(request)
        
        # Response 정보 로깅
        process_time = time.time() - start_time
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"status={response.status_code} duration={process_time:.3f}s"
        )
        
        # 응답 헤더에 처리 시간 추가
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path} "
            f"error={str(e)} duration={process_time:.3f}s"
        )
        raise


# ==================== Error Handler ====================

async def http_exception_handler(request: Request, exc: HTTPException):
    """
    HTTP 예외 핸들러
    
    Args:
        request: FastAPI Request
        exc: HTTPException
        
    Returns:
        JSONResponse
    """
    logger.error(
        f"HTTP Exception: {request.method} {request.url.path} "
        f"status={exc.status_code} detail={exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": str(request.url.path)
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    일반 예외 핸들러
    
    Args:
        request: FastAPI Request
        exc: Exception
        
    Returns:
        JSONResponse
    """
    logger.error(
        f"Unhandled Exception: {request.method} {request.url.path} "
        f"error={str(exc)}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "status_code": 500,
            "message": "Internal server error",
            "detail": str(exc),
            "path": str(request.url.path)
        }
    )


# ==================== CORS Headers Middleware ====================

async def add_security_headers_middleware(request: Request, call_next: Callable):
    """
    보안 헤더 추가 미들웨어
    
    Args:
        request: FastAPI Request
        call_next: 다음 미들웨어/핸들러
        
    Returns:
        Response with security headers
    """
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response


# ==================== API Key Rate Limit Storage ====================

from collections import defaultdict
from datetime import datetime, timedelta

# API 키별 요청 카운트 저장 (메모리, 프로덕션에서는 Redis 사용)
api_key_requests = defaultdict(list)

API_KEY_RATE_LIMIT = 1000  # 1시간당 요청 수
API_KEY_RATE_WINDOW = 3600  # 1시간 (초)


def check_api_key_rate_limit(api_key: str) -> bool:
    """
    API 키 Rate Limit 확인
    
    Args:
        api_key: API 키
        
    Returns:
        True if allowed, False if rate limit exceeded
    """
    now = datetime.utcnow()
    window_start = now - timedelta(seconds=API_KEY_RATE_WINDOW)
    
    # 오래된 요청 제거
    api_key_requests[api_key] = [
        req_time for req_time in api_key_requests[api_key]
        if req_time > window_start
    ]
    
    # 현재 요청 수 확인
    if len(api_key_requests[api_key]) >= API_KEY_RATE_LIMIT:
        return False
    
    # 요청 기록
    api_key_requests[api_key].append(now)
    return True


async def api_key_rate_limit_middleware(request: Request, call_next: Callable):
    """
    API 키 기반 Rate Limiting 미들웨어
    
    Args:
        request: FastAPI Request
        call_next: 다음 미들웨어/핸들러
        
    Returns:
        Response or 429 Too Many Requests
    """
    # Authorization 헤더에서 API 키 추출
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer zerosite_"):
        api_key = auth_header.replace("Bearer ", "")
        
        if not check_api_key_rate_limit(api_key):
            logger.warning(f"Rate limit exceeded for API key: {api_key[:20]}...")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": True,
                    "status_code": 429,
                    "message": "Rate limit exceeded. Maximum 1000 requests per hour.",
                    "retry_after": API_KEY_RATE_WINDOW
                }
            )
    
    response = await call_next(request)
    return response
