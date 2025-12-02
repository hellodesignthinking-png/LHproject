"""
Standard API Response Models

Provides consistent response wrappers for all API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Any, Optional, List, Generic, TypeVar
from datetime import datetime
from enum import Enum


T = TypeVar('T')


class ResponseMetadata(BaseModel):
    """Metadata included in all API responses"""
    request_id: str = Field(..., description="Unique request identifier for tracing")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp (ISO 8601)")
    version: str = Field("1.0.0", description="API version")
    execution_time_ms: Optional[int] = Field(None, description="Request processing time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req-a1b2c3d4-e5f6-7890",
                "timestamp": "2025-12-01T12:00:00Z",
                "version": "1.0.0",
                "execution_time_ms": 1250
            }
        }


class StandardSuccessResponse(BaseModel, Generic[T]):
    """
    Standard success response wrapper
    
    All successful API responses follow this structure for consistency.
    """
    success: bool = Field(True, description="Indicates successful request")
    status_code: int = Field(200, description="HTTP status code")
    message: str = Field("Request successful", description="Human-readable success message")
    data: T = Field(..., description="Response payload")
    metadata: ResponseMetadata = Field(..., description="Response metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "status_code": 200,
                "message": "Land analysis completed successfully",
                "data": {
                    "analysis_id": "abc123",
                    "address": "서울특별시 강남구 역삼동 123-45",
                    "unit_type": "청년",
                    "grade": "A"
                },
                "metadata": {
                    "request_id": "req-a1b2c3d4",
                    "timestamp": "2025-12-01T12:00:00Z",
                    "version": "1.0.0",
                    "execution_time_ms": 1250
                }
            }
        }


class StandardErrorResponse(BaseModel):
    """
    Standard error response wrapper
    
    All error responses follow this structure for consistent error handling.
    """
    success: bool = Field(False, description="Indicates failed request")
    status_code: int = Field(..., description="HTTP status code (400, 404, 500, etc.)")
    error_code: str = Field(..., description="Application-specific error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Any] = Field(None, description="Detailed error information (debug mode only)")
    metadata: ResponseMetadata = Field(..., description="Response metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "status_code": 400,
                "error_code": "INVALID_ADDRESS",
                "message": "The provided address could not be found",
                "details": {
                    "field": "address",
                    "value": "잘못된 주소",
                    "suggestion": "Please provide a valid Korean address"
                },
                "metadata": {
                    "request_id": "req-e5f6g7h8",
                    "timestamp": "2025-12-01T12:00:00Z",
                    "version": "1.0.0"
                }
            }
        }


class PaginationMetadata(BaseModel):
    """Pagination metadata for list responses"""
    page: int = Field(..., description="Current page number (1-indexed)", ge=1)
    page_size: int = Field(..., description="Number of items per page", ge=1, le=100)
    total_items: int = Field(..., description="Total number of items across all pages", ge=0)
    total_pages: int = Field(..., description="Total number of pages", ge=0)
    has_next: bool = Field(..., description="Whether next page exists")
    has_prev: bool = Field(..., description="Whether previous page exists")
    
    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 10,
                "total_items": 25,
                "total_pages": 3,
                "has_next": True,
                "has_prev": False
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated list response
    
    For endpoints returning lists of items with pagination support.
    """
    success: bool = Field(True, description="Indicates successful request")
    status_code: int = Field(200, description="HTTP status code")
    message: str = Field("Request successful", description="Human-readable success message")
    data: List[T] = Field(..., description="List of items for current page")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")
    metadata: ResponseMetadata = Field(..., description="Response metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "status_code": 200,
                "message": "LH notices retrieved successfully",
                "data": [
                    {"notice_id": "2024_8차", "title": "신축매입임대..."},
                    {"notice_id": "2024_7차", "title": "신축매입임대..."}
                ],
                "pagination": {
                    "page": 1,
                    "page_size": 10,
                    "total_items": 25,
                    "total_pages": 3,
                    "has_next": True,
                    "has_prev": False
                },
                "metadata": {
                    "request_id": "req-i9j0k1l2",
                    "timestamp": "2025-12-01T12:00:00Z",
                    "version": "1.0.0",
                    "execution_time_ms": 350
                }
            }
        }


class HealthCheckStatus(str, Enum):
    """Health check status codes"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class APIServiceStatus(BaseModel):
    """Status of an external API service"""
    name: str = Field(..., description="Service name")
    status: str = Field(..., description="Service status (configured/missing/error)")
    available: bool = Field(..., description="Whether service is available")
    response_time_ms: Optional[int] = Field(None, description="Average response time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Kakao API",
                "status": "configured",
                "available": True,
                "response_time_ms": 150
            }
        }


class HealthCheckData(BaseModel):
    """Health check response data"""
    status: HealthCheckStatus = Field(..., description="Overall system health status")
    apis: List[APIServiceStatus] = Field(..., description="External API services status")
    uptime_seconds: Optional[int] = Field(None, description="System uptime in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "apis": [
                    {"name": "Kakao API", "status": "configured", "available": True, "response_time_ms": 150},
                    {"name": "Land Regulation API", "status": "configured", "available": True, "response_time_ms": 200}
                ],
                "uptime_seconds": 86400
            }
        }


# Type aliases for common response types
SuccessResponse = StandardSuccessResponse
ErrorResponse = StandardErrorResponse
