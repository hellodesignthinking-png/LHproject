"""
API Response Utility Functions

Provides helper functions for creating standardized API responses.
"""

from typing import Any, Optional, List, TypeVar
from datetime import datetime
import uuid
import math

from app.api.response_models import (
    StandardSuccessResponse,
    StandardErrorResponse,
    PaginatedResponse,
    ResponseMetadata,
    PaginationMetadata
)
from app.api.error_codes import ErrorCode, get_status_code, get_error_message
from app.api.exceptions import APIException


T = TypeVar('T')


def generate_request_id() -> str:
    """
    Generate a unique request ID
    
    Returns:
        UUID-based request ID in format 'req-xxxxxxxx-xxxx-xxxx'
    """
    return f"req-{str(uuid.uuid4())[:23]}"


def success_response(
    data: Any,
    message: str = "Request successful",
    status_code: int = 200,
    request_id: Optional[str] = None,
    execution_time_ms: Optional[int] = None,
    version: str = "1.0.0"
) -> StandardSuccessResponse:
    """
    Create a standardized success response
    
    Args:
        data: Response payload (actual data)
        message: Human-readable success message
        status_code: HTTP status code (default: 200)
        request_id: Optional request ID (generates if not provided)
        execution_time_ms: Optional execution time in milliseconds
        version: API version (default: "1.0.0")
        
    Returns:
        StandardSuccessResponse with metadata
        
    Example:
        >>> response = success_response(
        ...     data={"analysis_id": "abc123"},
        ...     message="Analysis completed successfully"
        ... )
    """
    if not request_id:
        request_id = generate_request_id()
    
    metadata = ResponseMetadata(
        request_id=request_id,
        timestamp=datetime.now(),
        version=version,
        execution_time_ms=execution_time_ms
    )
    
    return StandardSuccessResponse(
        success=True,
        status_code=status_code,
        message=message,
        data=data,
        metadata=metadata
    )


def error_response(
    error_code: ErrorCode,
    message: Optional[str] = None,
    details: Optional[Any] = None,
    status_code: Optional[int] = None,
    request_id: Optional[str] = None,
    version: str = "1.0.0"
) -> StandardErrorResponse:
    """
    Create a standardized error response
    
    Args:
        error_code: Application-specific error code
        message: Optional human-readable error message (uses default if not provided)
        details: Optional detailed error information
        status_code: Optional HTTP status code (inferred from error_code if not provided)
        request_id: Optional request ID (generates if not provided)
        version: API version (default: "1.0.0")
        
    Returns:
        StandardErrorResponse with metadata
        
    Example:
        >>> response = error_response(
        ...     error_code=ErrorCode.INVALID_ADDRESS,
        ...     message="주소를 찾을 수 없습니다",
        ...     details={"field": "address", "value": "잘못된 주소"}
        ... )
    """
    if not request_id:
        request_id = generate_request_id()
    
    if not message:
        message = get_error_message(error_code)
    
    if not status_code:
        status_code = get_status_code(error_code)
    
    metadata = ResponseMetadata(
        request_id=request_id,
        timestamp=datetime.now(),
        version=version,
        execution_time_ms=None  # Not applicable for errors
    )
    
    return StandardErrorResponse(
        success=False,
        status_code=status_code,
        error_code=error_code.value,
        message=message,
        details=details,
        metadata=metadata
    )


def exception_to_response(
    exception: Exception,
    request_id: Optional[str] = None,
    include_details: bool = False
) -> StandardErrorResponse:
    """
    Convert an exception to a standardized error response
    
    Args:
        exception: Any exception (APIException or generic)
        request_id: Optional request ID
        include_details: Whether to include exception details (for debugging)
        
    Returns:
        StandardErrorResponse
        
    Example:
        >>> try:
        ...     raise InvalidAddressException("서울특별시 강남구...")
        ... except Exception as e:
        ...     response = exception_to_response(e, include_details=True)
    """
    if isinstance(exception, APIException):
        return error_response(
            error_code=exception.error_code,
            message=exception.message,
            details=exception.details if include_details else None,
            status_code=exception.status_code,
            request_id=request_id
        )
    
    # Generic exception handling
    return error_response(
        error_code=ErrorCode.INTERNAL_ERROR,
        message=str(exception) if include_details else "Internal server error",
        details={
            "exception_type": type(exception).__name__,
            "exception_message": str(exception)
        } if include_details else None,
        status_code=500,
        request_id=request_id
    )


def paginated_response(
    data: List[T],
    page: int,
    page_size: int,
    total_items: int,
    message: str = "Request successful",
    request_id: Optional[str] = None,
    execution_time_ms: Optional[int] = None,
    version: str = "1.0.0"
) -> PaginatedResponse:
    """
    Create a standardized paginated list response
    
    Args:
        data: List of items for current page
        page: Current page number (1-indexed)
        page_size: Number of items per page
        total_items: Total number of items across all pages
        message: Human-readable success message
        request_id: Optional request ID (generates if not provided)
        execution_time_ms: Optional execution time in milliseconds
        version: API version (default: "1.0.0")
        
    Returns:
        PaginatedResponse with pagination metadata
        
    Example:
        >>> response = paginated_response(
        ...     data=[{"id": 1}, {"id": 2}],
        ...     page=1,
        ...     page_size=10,
        ...     total_items=25,
        ...     message="Notices retrieved successfully"
        ... )
    """
    if not request_id:
        request_id = generate_request_id()
    
    # Calculate pagination metadata
    total_pages = math.ceil(total_items / page_size) if page_size > 0 else 0
    has_next = page < total_pages
    has_prev = page > 1
    
    metadata = ResponseMetadata(
        request_id=request_id,
        timestamp=datetime.now(),
        version=version,
        execution_time_ms=execution_time_ms
    )
    
    pagination = PaginationMetadata(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev
    )
    
    return PaginatedResponse(
        success=True,
        status_code=200,
        message=message,
        data=data,
        pagination=pagination,
        metadata=metadata
    )


def calculate_pagination(
    total_items: int,
    page: int = 1,
    page_size: int = 10,
    max_page_size: int = 100
) -> tuple[int, int, int, int]:
    """
    Calculate pagination parameters
    
    Args:
        total_items: Total number of items
        page: Requested page number (1-indexed)
        page_size: Requested items per page
        max_page_size: Maximum allowed page size
        
    Returns:
        Tuple of (validated_page, validated_page_size, offset, limit)
        
    Example:
        >>> page, page_size, offset, limit = calculate_pagination(
        ...     total_items=100,
        ...     page=2,
        ...     page_size=10
        ... )
        >>> # page=2, page_size=10, offset=10, limit=10
    """
    # Validate and limit page_size
    page_size = min(max(1, page_size), max_page_size)
    
    # Calculate total pages
    total_pages = math.ceil(total_items / page_size) if page_size > 0 else 0
    
    # Validate page number
    page = max(1, min(page, total_pages if total_pages > 0 else 1))
    
    # Calculate offset and limit for database query
    offset = (page - 1) * page_size
    limit = page_size
    
    return page, page_size, offset, limit


def health_check_response(
    apis_status: List[dict],
    uptime_seconds: Optional[int] = None,
    request_id: Optional[str] = None
) -> StandardSuccessResponse:
    """
    Create a health check response
    
    Args:
        apis_status: List of API service statuses
        uptime_seconds: Optional system uptime
        request_id: Optional request ID
        
    Returns:
        StandardSuccessResponse with health check data
        
    Example:
        >>> response = health_check_response(
        ...     apis_status=[
        ...         {"name": "Kakao API", "status": "configured", "available": True},
        ...         {"name": "MOIS API", "status": "configured", "available": True}
        ...     ],
        ...     uptime_seconds=86400
        ... )
    """
    from app.api.response_models import HealthCheckStatus, HealthCheckData
    
    # Determine overall health status
    all_available = all(api.get("available", False) for api in apis_status)
    some_available = any(api.get("available", False) for api in apis_status)
    
    if all_available:
        status = HealthCheckStatus.HEALTHY
    elif some_available:
        status = HealthCheckStatus.DEGRADED
    else:
        status = HealthCheckStatus.UNHEALTHY
    
    health_data = HealthCheckData(
        status=status,
        apis=apis_status,
        uptime_seconds=uptime_seconds
    )
    
    return success_response(
        data=health_data.dict(),
        message=f"System is {status.value}",
        request_id=request_id
    )


# Utility function for wrapping existing endpoint responses

def wrap_response(
    original_response: Any,
    message: str = "Request successful",
    request_id: Optional[str] = None
) -> StandardSuccessResponse:
    """
    Wrap an existing response object in standardized format
    
    Useful for gradually migrating existing endpoints to new format.
    
    Args:
        original_response: Original response data (dict, model, etc.)
        message: Success message
        request_id: Optional request ID
        
    Returns:
        StandardSuccessResponse wrapping the original response
        
    Example:
        >>> old_response = {"analysis_id": "abc", "status": "success"}
        >>> new_response = wrap_response(old_response, "Analysis complete")
    """
    # Convert Pydantic models to dict
    if hasattr(original_response, 'dict'):
        data = original_response.dict()
    elif hasattr(original_response, '__dict__'):
        data = original_response.__dict__
    else:
        data = original_response
    
    return success_response(
        data=data,
        message=message,
        request_id=request_id
    )
