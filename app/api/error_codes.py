"""
Standard Error Codes

Defines application-specific error codes for consistent error handling.
"""

from enum import Enum


class ErrorCode(str, Enum):
    """
    Standard error codes for API responses
    
    Error code format: CATEGORY_SPECIFIC_ERROR
    Categories: INVALID (4xx client errors), INTERNAL (5xx server errors)
    """
    
    # ============================================
    # 400 Bad Request - Client Input Errors
    # ============================================
    INVALID_REQUEST = "INVALID_REQUEST"
    """Generic invalid request error"""
    
    INVALID_ADDRESS = "INVALID_ADDRESS"
    """Address cannot be found or is invalid"""
    
    INVALID_LAND_AREA = "INVALID_LAND_AREA"
    """Land area is invalid (negative, zero, or unreasonably large)"""
    
    INVALID_UNIT_TYPE = "INVALID_UNIT_TYPE"
    """Unit type is not supported or invalid"""
    
    INVALID_ZONE_TYPE = "INVALID_ZONE_TYPE"
    """Zone type is not supported or invalid"""
    
    INVALID_COORDINATES = "INVALID_COORDINATES"
    """Coordinates are invalid or out of range"""
    
    INVALID_PAGINATION = "INVALID_PAGINATION"
    """Pagination parameters are invalid"""
    
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    """Required field is missing from request"""
    
    VALIDATION_ERROR = "VALIDATION_ERROR"
    """Request failed validation"""
    
    # ============================================
    # 404 Not Found - Resource Errors
    # ============================================
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    """Requested resource not found"""
    
    ANALYSIS_NOT_FOUND = "ANALYSIS_NOT_FOUND"
    """Analysis with specified ID not found"""
    
    NOTICE_NOT_FOUND = "NOTICE_NOT_FOUND"
    """LH notice with specified version not found"""
    
    REPORT_NOT_FOUND = "REPORT_NOT_FOUND"
    """Report with specified ID not found"""
    
    # ============================================
    # 409 Conflict - State Errors
    # ============================================
    DUPLICATE_ANALYSIS = "DUPLICATE_ANALYSIS"
    """Analysis for this land already exists"""
    
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    """Resource state conflict"""
    
    # ============================================
    # 422 Unprocessable Entity - Business Logic Errors
    # ============================================
    INELIGIBLE_LAND = "INELIGIBLE_LAND"
    """Land does not meet LH eligibility criteria"""
    
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    """Insufficient data to complete analysis"""
    
    CALCULATION_ERROR = "CALCULATION_ERROR"
    """Error in score or capacity calculation"""
    
    # ============================================
    # 500 Internal Server Error - Server Errors
    # ============================================
    INTERNAL_ERROR = "INTERNAL_ERROR"
    """Generic internal server error"""
    
    DATABASE_ERROR = "DATABASE_ERROR"
    """Database operation failed"""
    
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    """Server configuration error"""
    
    # ============================================
    # 502 Bad Gateway - External API Errors
    # ============================================
    API_ERROR = "API_ERROR"
    """Generic external API error"""
    
    KAKAO_API_ERROR = "KAKAO_API_ERROR"
    """Kakao API request failed"""
    
    LAND_REGULATION_API_ERROR = "LAND_REGULATION_API_ERROR"
    """Land regulation API request failed"""
    
    MOIS_API_ERROR = "MOIS_API_ERROR"
    """MOIS (행정안전부) API request failed"""
    
    GOOGLE_SHEETS_ERROR = "GOOGLE_SHEETS_ERROR"
    """Google Sheets API request failed"""
    
    GOOGLE_DOCS_ERROR = "GOOGLE_DOCS_ERROR"
    """Google Docs API request failed"""
    
    # ============================================
    # 503 Service Unavailable - Temporary Errors
    # ============================================
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    """Service temporarily unavailable"""
    
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    """API rate limit exceeded"""
    
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    """Request timeout"""
    
    MAINTENANCE_MODE = "MAINTENANCE_MODE"
    """System under maintenance"""
    
    # ============================================
    # 507 Insufficient Storage
    # ============================================
    STORAGE_FULL = "STORAGE_FULL"
    """Storage quota exceeded"""


# Error code to HTTP status code mapping
ERROR_CODE_TO_STATUS = {
    # 400 Bad Request
    ErrorCode.INVALID_REQUEST: 400,
    ErrorCode.INVALID_ADDRESS: 400,
    ErrorCode.INVALID_LAND_AREA: 400,
    ErrorCode.INVALID_UNIT_TYPE: 400,
    ErrorCode.INVALID_ZONE_TYPE: 400,
    ErrorCode.INVALID_COORDINATES: 400,
    ErrorCode.INVALID_PAGINATION: 400,
    ErrorCode.MISSING_REQUIRED_FIELD: 400,
    ErrorCode.VALIDATION_ERROR: 400,
    
    # 404 Not Found
    ErrorCode.RESOURCE_NOT_FOUND: 404,
    ErrorCode.ANALYSIS_NOT_FOUND: 404,
    ErrorCode.NOTICE_NOT_FOUND: 404,
    ErrorCode.REPORT_NOT_FOUND: 404,
    
    # 409 Conflict
    ErrorCode.DUPLICATE_ANALYSIS: 409,
    ErrorCode.RESOURCE_CONFLICT: 409,
    
    # 422 Unprocessable Entity
    ErrorCode.INELIGIBLE_LAND: 422,
    ErrorCode.INSUFFICIENT_DATA: 422,
    ErrorCode.CALCULATION_ERROR: 422,
    
    # 500 Internal Server Error
    ErrorCode.INTERNAL_ERROR: 500,
    ErrorCode.DATABASE_ERROR: 500,
    ErrorCode.CONFIGURATION_ERROR: 500,
    
    # 502 Bad Gateway
    ErrorCode.API_ERROR: 502,
    ErrorCode.KAKAO_API_ERROR: 502,
    ErrorCode.LAND_REGULATION_API_ERROR: 502,
    ErrorCode.MOIS_API_ERROR: 502,
    ErrorCode.GOOGLE_SHEETS_ERROR: 502,
    ErrorCode.GOOGLE_DOCS_ERROR: 502,
    
    # 503 Service Unavailable
    ErrorCode.SERVICE_UNAVAILABLE: 503,
    ErrorCode.RATE_LIMIT_EXCEEDED: 503,
    ErrorCode.TIMEOUT_ERROR: 503,
    ErrorCode.MAINTENANCE_MODE: 503,
    
    # 507 Insufficient Storage
    ErrorCode.STORAGE_FULL: 507,
}


def get_status_code(error_code: ErrorCode) -> int:
    """
    Get HTTP status code for an error code
    
    Args:
        error_code: Error code enum
        
    Returns:
        HTTP status code (default: 500 if not found)
    """
    return ERROR_CODE_TO_STATUS.get(error_code, 500)


# User-friendly error messages
ERROR_MESSAGES = {
    ErrorCode.INVALID_ADDRESS: "제공된 주소를 찾을 수 없습니다. 정확한 주소를 입력해주세요.",
    ErrorCode.INVALID_LAND_AREA: "토지 면적이 유효하지 않습니다. 양수 값을 입력해주세요.",
    ErrorCode.INVALID_UNIT_TYPE: "지원하지 않는 세대 유형입니다.",
    ErrorCode.RESOURCE_NOT_FOUND: "요청한 리소스를 찾을 수 없습니다.",
    ErrorCode.ANALYSIS_NOT_FOUND: "해당 분석 ID를 찾을 수 없습니다.",
    ErrorCode.NOTICE_NOT_FOUND: "해당 LH 공고문 버전을 찾을 수 없습니다.",
    ErrorCode.INTERNAL_ERROR: "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
    ErrorCode.API_ERROR: "외부 API 호출 중 오류가 발생했습니다.",
    ErrorCode.SERVICE_UNAVAILABLE: "서비스가 일시적으로 사용 불가능합니다. 잠시 후 다시 시도해주세요.",
    ErrorCode.RATE_LIMIT_EXCEEDED: "요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.",
}


def get_error_message(error_code: ErrorCode, custom_message: str = None) -> str:
    """
    Get user-friendly error message for an error code
    
    Args:
        error_code: Error code enum
        custom_message: Optional custom message to override default
        
    Returns:
        User-friendly error message (Korean)
    """
    if custom_message:
        return custom_message
    
    return ERROR_MESSAGES.get(error_code, "알 수 없는 오류가 발생했습니다.")
