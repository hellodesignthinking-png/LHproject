# Task 6: API Response Structure Standardization

## 📋 Overview

**Objective**: Standardize all API response formats for consistency, maintainability, and better client experience

**Current State**: Mixed response formats across endpoints (some use direct returns, others use custom dict structures)

**Target State**: Unified response wrapper with consistent success/error formats

---

## 🎯 Goals

### Primary Goals
1. **Consistent Success Response**: All successful responses follow the same structure
2. **Standardized Error Response**: Unified error format with proper error codes
3. **Type Safety**: Strong typing with Pydantic models
4. **Backward Compatibility**: Maintain existing API contracts where possible

### Secondary Goals
1. **HTTP Status Code Alignment**: Proper use of HTTP status codes (200, 400, 404, 500)
2. **Pagination Support**: Built-in pagination structure for list endpoints
3. **Metadata Inclusion**: Timestamp, request ID, version info in all responses
4. **Documentation**: Auto-generated API docs with consistent schemas

---

## 📊 Current Response Analysis

### Current Endpoints Overview

#### 1. `/` (Root Endpoint)
```python
# Current: Mixed (FileResponse or Dict)
return {
    "service": "LH 토지진단 자동화 시스템",
    "version": "1.0.0",
    "status": "running",
    "timestamp": datetime.now().isoformat()
}
```

#### 2. `/health` (Health Check)
```python
# Current: Custom dict
return {
    "status": "healthy",
    "apis": {...},
    "timestamp": datetime.now().isoformat()
}
```

#### 3. `/api/analyze-land` (Main Analysis)
```python
# Current: Pydantic model (LandAnalysisResponse)
return LandAnalysisResponse(
    status="success",
    analysis_id=...,
    # ... other fields
)
```

#### 4. `/api/analyze-multi-parcel` (Multi-Parcel)
```python
# Current: Pydantic model (MultiParcelResponse)
return MultiParcelResponse(
    status="success",
    analysis_id=...,
    # ... other fields
)
```

#### 5. `/api/lh-notices/*` (LH Notice APIs)
```python
# Current: Mixed dicts
return {
    "status": "success",
    "total": len(notices),
    "notices": notices
}
```

#### 6. `/api/generate-report` (Report Generation)
```python
# Current: Custom dict
return {
    "status": "success",
    "analysis_id": analysis_id,
    "report": report_html,
    # ... other fields
}
```

### Response Format Issues

| Issue | Current Behavior | Impact |
|-------|-----------------|--------|
| **Inconsistent Status Field** | Some have `status`, some don't | Hard to parse responses uniformly |
| **Mixed Error Formats** | `HTTPException` detail varies | Client error handling is complex |
| **No Request ID** | Most responses lack request tracking | Hard to trace issues in logs |
| **No Metadata** | Missing timestamp/version info | Hard to debug timing issues |
| **Inconsistent Pagination** | No standard pagination structure | Can't scale list endpoints easily |

---

## 🏗️ Proposed Standard Response Schema

### Success Response Structure

```python
class StandardSuccessResponse(BaseModel):
    """Standard success response wrapper"""
    success: bool = True
    status_code: int = 200
    message: str = "Request successful"
    data: Any  # Actual response data
    metadata: ResponseMetadata
    
class ResponseMetadata(BaseModel):
    """Response metadata"""
    request_id: str  # UUID for request tracking
    timestamp: datetime  # ISO 8601 format
    version: str = "1.0.0"  # API version
    execution_time_ms: Optional[int] = None  # Processing time
```

**Example Success Response**:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Land analysis completed successfully",
  "data": {
    "analysis_id": "abc123",
    "address": "서울특별시 강남구...",
    // ... actual analysis data
  },
  "metadata": {
    "request_id": "req-uuid-1234",
    "timestamp": "2025-12-01T12:00:00Z",
    "version": "1.0.0",
    "execution_time_ms": 1250
  }
}
```

### Error Response Structure

```python
class StandardErrorResponse(BaseModel):
    """Standard error response wrapper"""
    success: bool = False
    status_code: int  # HTTP status code (400, 404, 500, etc.)
    error_code: str  # Application-specific error code
    message: str  # Human-readable error message
    details: Optional[Any] = None  # Detailed error info (debug mode only)
    metadata: ResponseMetadata
```

**Example Error Response**:
```json
{
  "success": false,
  "status_code": 400,
  "error_code": "INVALID_ADDRESS",
  "message": "The provided address could not be found",
  "details": {
    "field": "address",
    "value": "잘못된 주소",
    "suggestion": "Please provide a valid Korean address"
  },
  "metadata": {
    "request_id": "req-uuid-5678",
    "timestamp": "2025-12-01T12:00:00Z",
    "version": "1.0.0"
  }
}
```

### Paginated Response Structure

```python
class PaginatedResponse(StandardSuccessResponse):
    """Paginated list response"""
    data: List[Any]
    pagination: PaginationMetadata
    
class PaginationMetadata(BaseModel):
    """Pagination metadata"""
    page: int  # Current page (1-indexed)
    page_size: int  # Items per page
    total_items: int  # Total number of items
    total_pages: int  # Total number of pages
    has_next: bool  # Whether next page exists
    has_prev: bool  # Whether previous page exists
```

**Example Paginated Response**:
```json
{
  "success": true,
  "status_code": 200,
  "message": "LH notices retrieved successfully",
  "data": [
    {"notice_id": "2024_8차", ...},
    {"notice_id": "2024_7차", ...}
  ],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_items": 25,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  },
  "metadata": {
    "request_id": "req-uuid-9012",
    "timestamp": "2025-12-01T12:00:00Z",
    "version": "1.0.0"
  }
}
```

---

## 🔧 Implementation Strategy

### Phase 1: Core Response Models (1 hour)

**Goal**: Create standardized response models

**Tasks**:
1. Create `app/api/response_models.py` with:
   - `StandardSuccessResponse`
   - `StandardErrorResponse`
   - `ResponseMetadata`
   - `PaginationMetadata`
   - `PaginatedResponse`

2. Create response utility functions in `app/api/response_utils.py`:
   - `success_response(data, message, status_code, request_id)`
   - `error_response(error_code, message, details, status_code, request_id)`
   - `paginated_response(data, page, page_size, total, request_id)`

### Phase 2: Middleware Implementation (30 mins)

**Goal**: Auto-wrap responses with metadata

**Tasks**:
1. Create `app/middleware/response_middleware.py`:
   - Generate `request_id` for each request
   - Track execution time
   - Auto-wrap responses with metadata
   - Handle exceptions globally

2. Register middleware in `app/main.py`

### Phase 3: Update Existing Endpoints (1.5 hours)

**Goal**: Migrate all endpoints to use standardized responses

**Priority Order**:
1. **High Priority**: Core analysis endpoints
   - `/api/analyze-land`
   - `/api/analyze-multi-parcel`
   - `/api/generate-report`

2. **Medium Priority**: LH notice endpoints
   - `/api/lh-notices/sync`
   - `/api/lh-notices/list`
   - `/api/lh-notices/{version_id}`

3. **Low Priority**: Utility endpoints
   - `/health`
   - `/api/dashboard-data`
   - Test endpoints

### Phase 4: Error Handling Standardization (30 mins)

**Goal**: Unified error handling across all endpoints

**Tasks**:
1. Define standard error codes in `app/api/error_codes.py`:
   ```python
   class ErrorCode:
       # 4xx Client Errors
       INVALID_REQUEST = "INVALID_REQUEST"
       INVALID_ADDRESS = "INVALID_ADDRESS"
       INVALID_LAND_AREA = "INVALID_LAND_AREA"
       RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
       
       # 5xx Server Errors
       INTERNAL_ERROR = "INTERNAL_ERROR"
       API_ERROR = "API_ERROR"
       SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
   ```

2. Create custom exception classes in `app/api/exceptions.py`:
   ```python
   class APIException(Exception):
       def __init__(self, error_code, message, status_code, details=None):
           self.error_code = error_code
           self.message = message
           self.status_code = status_code
           self.details = details
   ```

3. Implement global exception handler in middleware

### Phase 5: Testing & Documentation (1 hour)

**Goal**: Comprehensive testing and updated docs

**Tasks**:
1. Create `tests/test_api_responses.py`:
   - Test success response format
   - Test error response format
   - Test pagination format
   - Test metadata presence
   - Test backward compatibility

2. Update API documentation:
   - Update OpenAPI/Swagger schemas
   - Add response examples
   - Document error codes

---

## 📝 Detailed Implementation

### File Structure

```
app/
├── api/
│   ├── __init__.py
│   ├── response_models.py       # ✨ NEW - Standard response models
│   ├── response_utils.py        # ✨ NEW - Response helper functions
│   ├── error_codes.py           # ✨ NEW - Standard error codes
│   ├── exceptions.py            # ✨ NEW - Custom exception classes
│   └── endpoints/
│       └── __init__.py
├── middleware/
│   ├── __init__.py
│   └── response_middleware.py   # ✨ NEW - Response wrapping middleware
├── main.py                       # 🔧 MODIFIED - Register middleware
└── schemas.py                    # 🔧 MODIFIED - Update response schemas

tests/
├── test_api_responses.py        # ✨ NEW - Response format tests
└── test_error_handling.py       # ✨ NEW - Error handling tests
```

### Backward Compatibility Strategy

**Approach**: Gradual migration with versioning

1. **Version Header**: Support `API-Version` header
   - `API-Version: 1.0` → Old format (for legacy clients)
   - `API-Version: 2.0` → New standardized format
   - Default: New format

2. **Response Adapter**: Create adapter for old format
   ```python
   def adapt_to_old_format(standard_response):
       """Convert new format to old format for v1.0 clients"""
       if is_old_client():
           return standard_response.data  # Return data only
       return standard_response  # Return full wrapper
   ```

3. **Deprecation Timeline**:
   - Week 1-2: Both formats supported
   - Week 3-4: Warning headers for old format
   - Week 5+: Old format deprecated (return warning)

---

## 🧪 Testing Strategy

### Unit Tests

```python
def test_success_response_format():
    """Test standard success response structure"""
    response = success_response(
        data={"analysis_id": "test123"},
        message="Test successful",
        request_id="req-test"
    )
    
    assert response.success == True
    assert response.status_code == 200
    assert response.data["analysis_id"] == "test123"
    assert response.metadata.request_id == "req-test"
    assert response.metadata.version == "1.0.0"

def test_error_response_format():
    """Test standard error response structure"""
    response = error_response(
        error_code=ErrorCode.INVALID_ADDRESS,
        message="Address not found",
        status_code=400,
        request_id="req-test-err"
    )
    
    assert response.success == False
    assert response.status_code == 400
    assert response.error_code == ErrorCode.INVALID_ADDRESS
    assert response.metadata.request_id == "req-test-err"

def test_paginated_response_format():
    """Test paginated response structure"""
    response = paginated_response(
        data=[{"id": 1}, {"id": 2}],
        page=1,
        page_size=10,
        total=25,
        request_id="req-test-page"
    )
    
    assert response.success == True
    assert len(response.data) == 2
    assert response.pagination.total_items == 25
    assert response.pagination.has_next == True
```

### Integration Tests

```python
async def test_analyze_land_response_format():
    """Test /api/analyze-land returns standardized format"""
    request = {
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500.0,
        "unit_type": "청년"
    }
    
    response = client.post("/api/analyze-land", json=request)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check standard fields
    assert "success" in data
    assert "status_code" in data
    assert "message" in data
    assert "data" in data
    assert "metadata" in data
    
    # Check metadata
    assert "request_id" in data["metadata"]
    assert "timestamp" in data["metadata"]
    assert "version" in data["metadata"]
```

---

## 📈 Success Metrics

### Completion Criteria

- [ ] All response models created and documented
- [ ] Response middleware implemented and registered
- [ ] All 10+ endpoints migrated to new format
- [ ] 30+ response format tests passing (>90% coverage)
- [ ] API documentation updated
- [ ] Backward compatibility verified
- [ ] Zero breaking changes for existing clients

### Quality Metrics

- **Code Coverage**: ≥90% for response utilities
- **Test Pass Rate**: ≥95% (28/30 tests)
- **Response Time**: No performance degradation (middleware overhead <1ms)
- **Documentation**: 100% of endpoints documented with examples

---

## 🚀 Rollout Plan

### Stage 1: Development (Current)
- Implement core models and utilities
- Create middleware
- Write comprehensive tests

### Stage 2: Internal Testing (Week 1)
- Test with development environment
- Validate all endpoints
- Fix any issues

### Stage 3: Staging Deployment (Week 2)
- Deploy to staging environment
- Notify internal users
- Collect feedback

### Stage 4: Production Deployment (Week 3)
- Gradual rollout with version header support
- Monitor error rates and response times
- Full migration to new format

---

## 🔗 Dependencies

### Internal Dependencies
- `app/schemas.py` - May need updates for compatibility
- `app/main.py` - Register middleware
- All endpoint files - Update return statements

### External Dependencies
- FastAPI middleware support (existing)
- Pydantic v2 (existing)
- No new dependencies required

---

## 📊 Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking changes for clients | Medium | High | Version header support + deprecation timeline |
| Performance degradation | Low | Medium | Benchmark middleware overhead, optimize if needed |
| Incomplete migration | Low | Medium | Comprehensive checklist + automated tests |
| Documentation out of sync | Medium | Low | Auto-generate from Pydantic models |

---

## 🎯 Next Steps

1. **Review & Approval**: Get stakeholder approval on design
2. **Implementation**: Start with Phase 1 (Core Models)
3. **Testing**: Write tests alongside implementation
4. **Migration**: Update endpoints one by one
5. **Documentation**: Update API docs
6. **Deployment**: Follow rollout plan

---

## 📝 Notes

- **Priority**: Medium (improves maintainability, not urgent)
- **Estimated Time**: 4-5 hours total
- **Impact**: Improves developer experience, easier client integration
- **Breaking Changes**: None (with version header support)

---

**Status**: READY TO IMPLEMENT  
**Last Updated**: 2025-12-01  
**Author**: ZeroSite Team

---

© 2025 ZeroSite. All Rights Reserved.
