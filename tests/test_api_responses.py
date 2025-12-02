"""
Tests for API Response Standardization (Task 6)

Tests standardized response formats, error handling, and pagination.
"""

import pytest
from datetime import datetime
from typing import List

from app.api import (
    success_response,
    error_response,
    paginated_response,
    exception_to_response,
    health_check_response,
    wrap_response,
    generate_request_id,
    calculate_pagination,
    ErrorCode,
    InvalidAddressException,
    AnalysisNotFoundException,
    RateLimitException
)
from app.api.response_models import (
    StandardSuccessResponse,
    StandardErrorResponse,
    PaginatedResponse,
    HealthCheckStatus
)


# ============================================
# Test Success Response
# ============================================

def test_success_response_basic():
    """Test basic success response creation"""
    response = success_response(
        data={"analysis_id": "test123", "status": "completed"},
        message="Analysis successful"
    )
    
    assert isinstance(response, StandardSuccessResponse)
    assert response.success == True
    assert response.status_code == 200
    assert response.message == "Analysis successful"
    assert response.data["analysis_id"] == "test123"
    assert response.metadata is not None
    assert response.metadata.request_id.startswith("req-")
    assert isinstance(response.metadata.timestamp, datetime)
    assert response.metadata.version == "1.0.0"


def test_success_response_with_custom_request_id():
    """Test success response with custom request ID"""
    custom_id = "req-custom-12345"
    response = success_response(
        data={"result": "ok"},
        request_id=custom_id
    )
    
    assert response.metadata.request_id == custom_id


def test_success_response_with_execution_time():
    """Test success response includes execution time"""
    response = success_response(
        data={"result": "ok"},
        execution_time_ms=1250
    )
    
    assert response.metadata.execution_time_ms == 1250


def test_success_response_with_custom_status_code():
    """Test success response with custom status code (e.g., 201 Created)"""
    response = success_response(
        data={"id": "new123"},
        message="Resource created",
        status_code=201
    )
    
    assert response.status_code == 201
    assert response.success == True


# ============================================
# Test Error Response
# ============================================

def test_error_response_basic():
    """Test basic error response creation"""
    response = error_response(
        error_code=ErrorCode.INVALID_ADDRESS,
        message="주소를 찾을 수 없습니다"
    )
    
    assert isinstance(response, StandardErrorResponse)
    assert response.success == False
    assert response.status_code == 400
    assert response.error_code == ErrorCode.INVALID_ADDRESS.value
    assert response.message == "주소를 찾을 수 없습니다"
    assert response.metadata is not None
    assert response.metadata.request_id.startswith("req-")


def test_error_response_with_details():
    """Test error response includes detailed error info"""
    response = error_response(
        error_code=ErrorCode.INVALID_LAND_AREA,
        message="토지 면적이 유효하지 않습니다",
        details={"field": "land_area", "value": -100, "min": 0}
    )
    
    assert response.details is not None
    assert response.details["field"] == "land_area"
    assert response.details["value"] == -100


def test_error_response_status_code_inference():
    """Test error response infers correct status code from error code"""
    # 400 Bad Request
    response_400 = error_response(error_code=ErrorCode.INVALID_REQUEST)
    assert response_400.status_code == 400
    
    # 404 Not Found
    response_404 = error_response(error_code=ErrorCode.RESOURCE_NOT_FOUND)
    assert response_404.status_code == 404
    
    # 500 Internal Error
    response_500 = error_response(error_code=ErrorCode.INTERNAL_ERROR)
    assert response_500.status_code == 500
    
    # 502 Bad Gateway
    response_502 = error_response(error_code=ErrorCode.KAKAO_API_ERROR)
    assert response_502.status_code == 502
    
    # 503 Service Unavailable
    response_503 = error_response(error_code=ErrorCode.SERVICE_UNAVAILABLE)
    assert response_503.status_code == 503


def test_error_response_default_message():
    """Test error response uses default message if not provided"""
    response = error_response(error_code=ErrorCode.INVALID_ADDRESS)
    
    # Should use default Korean message
    assert "주소" in response.message or "Address" in response.message


# ============================================
# Test Paginated Response
# ============================================

def test_paginated_response_basic():
    """Test basic paginated response creation"""
    data = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
    response = paginated_response(
        data=data,
        page=1,
        page_size=10,
        total_items=25,
        message="Items retrieved successfully"
    )
    
    assert isinstance(response, PaginatedResponse)
    assert response.success == True
    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.pagination.page == 1
    assert response.pagination.page_size == 10
    assert response.pagination.total_items == 25
    assert response.pagination.total_pages == 3
    assert response.pagination.has_next == True
    assert response.pagination.has_prev == False


def test_paginated_response_last_page():
    """Test paginated response for last page"""
    data = [{"id": 21}, {"id": 22}]
    response = paginated_response(
        data=data,
        page=3,
        page_size=10,
        total_items=22
    )
    
    assert response.pagination.page == 3
    assert response.pagination.total_pages == 3
    assert response.pagination.has_next == False
    assert response.pagination.has_prev == True


def test_paginated_response_single_page():
    """Test paginated response when all items fit in one page"""
    data = [{"id": i} for i in range(5)]
    response = paginated_response(
        data=data,
        page=1,
        page_size=10,
        total_items=5
    )
    
    assert response.pagination.total_pages == 1
    assert response.pagination.has_next == False
    assert response.pagination.has_prev == False


def test_paginated_response_empty():
    """Test paginated response with no items"""
    response = paginated_response(
        data=[],
        page=1,
        page_size=10,
        total_items=0
    )
    
    assert len(response.data) == 0
    assert response.pagination.total_items == 0
    assert response.pagination.total_pages == 0
    assert response.pagination.has_next == False
    assert response.pagination.has_prev == False


# ============================================
# Test Exception to Response Conversion
# ============================================

def test_exception_to_response_api_exception():
    """Test converting APIException to response"""
    exception = InvalidAddressException("서울특별시 강남구 역삼동 123")
    response = exception_to_response(exception, include_details=True)
    
    assert isinstance(response, StandardErrorResponse)
    assert response.success == False
    assert response.error_code == ErrorCode.INVALID_ADDRESS.value
    assert "서울" in response.message
    assert response.details is not None


def test_exception_to_response_generic_exception():
    """Test converting generic exception to response"""
    exception = ValueError("Invalid input value")
    response = exception_to_response(exception, include_details=True)
    
    assert isinstance(response, StandardErrorResponse)
    assert response.success == False
    assert response.status_code == 500
    assert response.error_code == ErrorCode.INTERNAL_ERROR.value


def test_exception_to_response_without_details():
    """Test exception conversion without details (production mode)"""
    exception = InvalidAddressException("서울특별시 강남구 역삼동 123")
    response = exception_to_response(exception, include_details=False)
    
    assert response.details is None


# ============================================
# Test Health Check Response
# ============================================

def test_health_check_response_all_healthy():
    """Test health check response when all services are healthy"""
    apis_status = [
        {"name": "Kakao API", "status": "configured", "available": True, "response_time_ms": 150},
        {"name": "MOIS API", "status": "configured", "available": True, "response_time_ms": 200}
    ]
    
    response = health_check_response(
        apis_status=apis_status,
        uptime_seconds=86400
    )
    
    assert response.success == True
    assert response.data["status"] == HealthCheckStatus.HEALTHY.value
    assert len(response.data["apis"]) == 2
    assert response.data["uptime_seconds"] == 86400


def test_health_check_response_degraded():
    """Test health check response when some services are unavailable"""
    apis_status = [
        {"name": "Kakao API", "status": "configured", "available": True},
        {"name": "MOIS API", "status": "error", "available": False}
    ]
    
    response = health_check_response(apis_status=apis_status)
    
    assert response.data["status"] == HealthCheckStatus.DEGRADED.value


def test_health_check_response_unhealthy():
    """Test health check response when all services are unavailable"""
    apis_status = [
        {"name": "Kakao API", "status": "error", "available": False},
        {"name": "MOIS API", "status": "error", "available": False}
    ]
    
    response = health_check_response(apis_status=apis_status)
    
    assert response.data["status"] == HealthCheckStatus.UNHEALTHY.value


# ============================================
# Test Utility Functions
# ============================================

def test_generate_request_id():
    """Test request ID generation"""
    req_id1 = generate_request_id()
    req_id2 = generate_request_id()
    
    assert req_id1.startswith("req-")
    assert req_id2.startswith("req-")
    assert req_id1 != req_id2  # Should be unique


def test_calculate_pagination_basic():
    """Test basic pagination calculation"""
    page, page_size, offset, limit = calculate_pagination(
        total_items=100,
        page=2,
        page_size=10
    )
    
    assert page == 2
    assert page_size == 10
    assert offset == 10  # (page - 1) * page_size
    assert limit == 10


def test_calculate_pagination_first_page():
    """Test pagination for first page"""
    page, page_size, offset, limit = calculate_pagination(
        total_items=100,
        page=1,
        page_size=10
    )
    
    assert page == 1
    assert offset == 0


def test_calculate_pagination_last_page():
    """Test pagination for last page"""
    page, page_size, offset, limit = calculate_pagination(
        total_items=95,
        page=10,
        page_size=10
    )
    
    assert page == 10
    assert offset == 90


def test_calculate_pagination_exceeds_max():
    """Test pagination limits page_size to maximum"""
    page, page_size, offset, limit = calculate_pagination(
        total_items=1000,
        page=1,
        page_size=200,  # Exceeds max (100)
        max_page_size=100
    )
    
    assert page_size == 100  # Limited to max


def test_calculate_pagination_invalid_page():
    """Test pagination handles invalid page numbers"""
    # Page < 1
    page, _, _, _ = calculate_pagination(
        total_items=100,
        page=0,
        page_size=10
    )
    assert page == 1  # Corrected to 1
    
    # Page > total_pages
    page, _, _, _ = calculate_pagination(
        total_items=100,
        page=999,
        page_size=10
    )
    assert page == 10  # Corrected to last page


def test_wrap_response_with_dict():
    """Test wrapping a dictionary response"""
    original = {"analysis_id": "abc123", "status": "completed"}
    response = wrap_response(original, message="Analysis complete")
    
    assert response.success == True
    assert response.data["analysis_id"] == "abc123"
    assert response.message == "Analysis complete"


def test_wrap_response_with_pydantic_model():
    """Test wrapping a Pydantic model response"""
    from app.schemas import Coordinates
    
    original = Coordinates(latitude=37.5, longitude=127.0)
    response = wrap_response(original, message="Coordinates retrieved")
    
    assert response.success == True
    assert response.data["latitude"] == 37.5
    assert response.data["longitude"] == 127.0


# ============================================
# Test Response Metadata
# ============================================

def test_response_metadata_timestamp():
    """Test response metadata includes valid timestamp"""
    response = success_response(data={"test": "data"})
    
    # Timestamp should be recent (within last minute)
    now = datetime.now()
    time_diff = (now - response.metadata.timestamp).total_seconds()
    assert time_diff < 60  # Less than 60 seconds ago


def test_response_metadata_version():
    """Test response metadata includes API version"""
    response = success_response(data={"test": "data"})
    
    assert response.metadata.version == "1.0.0"


def test_response_metadata_custom_version():
    """Test response with custom API version"""
    response = success_response(
        data={"test": "data"},
        version="2.0.0"
    )
    
    assert response.metadata.version == "2.0.0"


# ============================================
# Test Edge Cases
# ============================================

def test_success_response_with_none_data():
    """Test success response with None data"""
    response = success_response(data=None)
    
    assert response.success == True
    assert response.data is None


def test_success_response_with_empty_dict():
    """Test success response with empty dictionary"""
    response = success_response(data={})
    
    assert response.success == True
    assert response.data == {}


def test_error_response_with_empty_details():
    """Test error response with empty details"""
    response = error_response(
        error_code=ErrorCode.INTERNAL_ERROR,
        details={}
    )
    
    assert response.details == {}


def test_paginated_response_with_fractional_pages():
    """Test pagination with non-divisible total items"""
    # 25 items with page_size 10 = 3 pages (10, 10, 5)
    response = paginated_response(
        data=[{"id": i} for i in range(5)],
        page=3,
        page_size=10,
        total_items=25
    )
    
    assert response.pagination.total_pages == 3
    assert len(response.data) == 5  # Last page has 5 items


# ============================================
# Test Consistency
# ============================================

def test_all_responses_have_metadata():
    """Test that all response types include metadata"""
    success_resp = success_response(data={"test": "data"})
    error_resp = error_response(error_code=ErrorCode.INTERNAL_ERROR)
    paginated_resp = paginated_response(data=[], page=1, page_size=10, total_items=0)
    
    assert hasattr(success_resp, 'metadata')
    assert hasattr(error_resp, 'metadata')
    assert hasattr(paginated_resp, 'metadata')
    
    assert success_resp.metadata.request_id is not None
    assert error_resp.metadata.request_id is not None
    assert paginated_resp.metadata.request_id is not None


def test_all_responses_have_success_field():
    """Test that all response types include success boolean"""
    success_resp = success_response(data={"test": "data"})
    error_resp = error_response(error_code=ErrorCode.INTERNAL_ERROR)
    paginated_resp = paginated_response(data=[], page=1, page_size=10, total_items=0)
    
    assert success_resp.success == True
    assert error_resp.success == False
    assert paginated_resp.success == True


def test_all_responses_have_status_code():
    """Test that all response types include status_code"""
    success_resp = success_response(data={"test": "data"})
    error_resp = error_response(error_code=ErrorCode.INVALID_ADDRESS)
    paginated_resp = paginated_response(data=[], page=1, page_size=10, total_items=0)
    
    assert success_resp.status_code == 200
    assert error_resp.status_code == 400
    assert paginated_resp.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
