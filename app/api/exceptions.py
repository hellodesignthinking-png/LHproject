"""
Custom API Exceptions

Provides custom exception classes for consistent error handling.
"""

from typing import Optional, Any, Dict
from app.api.error_codes import ErrorCode, get_status_code, get_error_message


class APIException(Exception):
    """
    Base exception for all API errors
    
    This exception provides structured error information that can be
    easily converted to a standardized error response.
    """
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Any] = None
    ):
        """
        Initialize API exception
        
        Args:
            error_code: Application-specific error code
            message: Optional custom error message (uses default if not provided)
            status_code: Optional HTTP status code (inferred from error_code if not provided)
            details: Optional additional error details
        """
        self.error_code = error_code
        self.message = message or get_error_message(error_code)
        self.status_code = status_code or get_status_code(error_code)
        self.details = details
        
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for JSON response
        
        Returns:
            Dictionary with error information
        """
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details
        }


class InvalidRequestException(APIException):
    """Exception for invalid client requests (400 Bad Request)"""
    
    def __init__(
        self,
        message: str = "Invalid request",
        error_code: ErrorCode = ErrorCode.INVALID_REQUEST,
        details: Optional[Any] = None
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=400,
            details=details
        )


class InvalidAddressException(InvalidRequestException):
    """Exception for invalid address (400 Bad Request)"""
    
    def __init__(
        self,
        address: str,
        message: Optional[str] = None,
        details: Optional[Any] = None
    ):
        if not message:
            message = f"주소를 찾을 수 없습니다: {address}"
        
        if not details:
            details = {"field": "address", "value": address}
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_ADDRESS,
            details=details
        )


class InvalidLandAreaException(InvalidRequestException):
    """Exception for invalid land area (400 Bad Request)"""
    
    def __init__(
        self,
        land_area: float,
        message: Optional[str] = None,
        details: Optional[Any] = None
    ):
        if not message:
            message = f"토지 면적이 유효하지 않습니다: {land_area}㎡"
        
        if not details:
            details = {"field": "land_area", "value": land_area}
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_LAND_AREA,
            details=details
        )


class ResourceNotFoundException(APIException):
    """Exception for resource not found (404 Not Found)"""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        message: Optional[str] = None,
        error_code: ErrorCode = ErrorCode.RESOURCE_NOT_FOUND,
        details: Optional[Any] = None
    ):
        if not message:
            message = f"{resource_type}을(를) 찾을 수 없습니다: {resource_id}"
        
        if not details:
            details = {"resource_type": resource_type, "resource_id": resource_id}
        
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=404,
            details=details
        )


class AnalysisNotFoundException(ResourceNotFoundException):
    """Exception for analysis not found (404 Not Found)"""
    
    def __init__(self, analysis_id: str):
        super().__init__(
            resource_type="분석",
            resource_id=analysis_id,
            error_code=ErrorCode.ANALYSIS_NOT_FOUND
        )


class NoticeNotFoundException(ResourceNotFoundException):
    """Exception for LH notice not found (404 Not Found)"""
    
    def __init__(self, version_id: str):
        super().__init__(
            resource_type="LH 공고문",
            resource_id=version_id,
            error_code=ErrorCode.NOTICE_NOT_FOUND
        )


class InternalServerException(APIException):
    """Exception for internal server errors (500 Internal Server Error)"""
    
    def __init__(
        self,
        message: str = "Internal server error",
        error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        details: Optional[Any] = None
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=500,
            details=details
        )


class ExternalAPIException(APIException):
    """Exception for external API errors (502 Bad Gateway)"""
    
    def __init__(
        self,
        api_name: str,
        message: Optional[str] = None,
        error_code: ErrorCode = ErrorCode.API_ERROR,
        details: Optional[Any] = None
    ):
        if not message:
            message = f"{api_name} API 호출 중 오류가 발생했습니다"
        
        if not details:
            details = {"api_name": api_name}
        
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=502,
            details=details
        )


class KakaoAPIException(ExternalAPIException):
    """Exception for Kakao API errors (502 Bad Gateway)"""
    
    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Any] = None
    ):
        super().__init__(
            api_name="Kakao",
            message=message,
            error_code=ErrorCode.KAKAO_API_ERROR,
            details=details
        )


class ServiceUnavailableException(APIException):
    """Exception for service unavailable (503 Service Unavailable)"""
    
    def __init__(
        self,
        service_name: str,
        message: Optional[str] = None,
        error_code: ErrorCode = ErrorCode.SERVICE_UNAVAILABLE,
        details: Optional[Any] = None
    ):
        if not message:
            message = f"{service_name} 서비스가 일시적으로 사용 불가능합니다"
        
        if not details:
            details = {"service_name": service_name}
        
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=503,
            details=details
        )


class RateLimitException(APIException):
    """Exception for rate limit exceeded (429 Too Many Requests)"""
    
    def __init__(
        self,
        retry_after: Optional[int] = None,
        message: Optional[str] = None,
        details: Optional[Any] = None
    ):
        if not message:
            message = "요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요."
        
        if not details and retry_after:
            details = {"retry_after_seconds": retry_after}
        
        super().__init__(
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message=message,
            status_code=429,
            details=details
        )


class ValidationException(InvalidRequestException):
    """Exception for request validation errors (400 Bad Request)"""
    
    def __init__(
        self,
        validation_errors: Dict[str, Any],
        message: str = "Request validation failed"
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            details={"validation_errors": validation_errors}
        )


# Exception utility functions

def wrap_exception(exception: Exception) -> APIException:
    """
    Wrap a generic exception into an APIException
    
    Args:
        exception: Any exception
        
    Returns:
        APIException with appropriate error code and message
    """
    if isinstance(exception, APIException):
        return exception
    
    # Map common exceptions to API exceptions
    if isinstance(exception, ValueError):
        return InvalidRequestException(
            message=str(exception),
            details={"original_exception": type(exception).__name__}
        )
    
    if isinstance(exception, KeyError):
        return InvalidRequestException(
            message=f"Required field missing: {str(exception)}",
            error_code=ErrorCode.MISSING_REQUIRED_FIELD,
            details={"missing_field": str(exception)}
        )
    
    # Default: wrap as internal server error
    return InternalServerException(
        message=str(exception),
        details={
            "exception_type": type(exception).__name__,
            "exception_message": str(exception)
        }
    )
