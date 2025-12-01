"""
API 패키지

Standardized API response system for consistent client experience.
"""

# Response models
from app.api.response_models import (
    StandardSuccessResponse,
    StandardErrorResponse,
    PaginatedResponse,
    ResponseMetadata,
    PaginationMetadata,
    HealthCheckStatus,
    HealthCheckData,
    SuccessResponse,
    ErrorResponse
)

# Error codes
from app.api.error_codes import ErrorCode

# Exceptions
from app.api.exceptions import (
    APIException,
    InvalidRequestException,
    InvalidAddressException,
    InvalidLandAreaException,
    ResourceNotFoundException,
    AnalysisNotFoundException,
    NoticeNotFoundException,
    InternalServerException,
    ExternalAPIException,
    KakaoAPIException,
    ServiceUnavailableException,
    RateLimitException,
    ValidationException
)

# Response utilities
from app.api.response_utils import (
    success_response,
    error_response,
    exception_to_response,
    paginated_response,
    health_check_response,
    wrap_response,
    generate_request_id,
    calculate_pagination
)

__all__ = [
    # Response models
    "StandardSuccessResponse",
    "StandardErrorResponse",
    "PaginatedResponse",
    "ResponseMetadata",
    "PaginationMetadata",
    "HealthCheckStatus",
    "HealthCheckData",
    "SuccessResponse",
    "ErrorResponse",
    
    # Error codes
    "ErrorCode",
    
    # Exceptions
    "APIException",
    "InvalidRequestException",
    "InvalidAddressException",
    "InvalidLandAreaException",
    "ResourceNotFoundException",
    "AnalysisNotFoundException",
    "NoticeNotFoundException",
    "InternalServerException",
    "ExternalAPIException",
    "KakaoAPIException",
    "ServiceUnavailableException",
    "RateLimitException",
    "ValidationException",
    
    # Response utilities
    "success_response",
    "error_response",
    "exception_to_response",
    "paginated_response",
    "health_check_response",
    "wrap_response",
    "generate_request_id",
    "calculate_pagination",
]
