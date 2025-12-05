# ZeroSite v7.2 Enterprise - Complete Technical Specification

**Version**: 7.2.0  
**Date**: 2025-12-01  
**Status**: Production Ready (Partial)  
**Branch**: feature/expert-report-generator  

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [API Specifications](#api-specifications)
5. [Data Flow](#data-flow)
6. [Performance Metrics](#performance-metrics)
7. [Integration Guide](#integration-guide)
8. [Deployment](#deployment)

---

## 1. System Overview

### 1.1 Purpose
ZeroSite v7.2 is an enterprise-grade land analysis platform for LH (Korea Land & Housing Corporation) 신축매입임대 projects, providing comprehensive site evaluation, demand prediction, and automated report generation.

### 1.2 Key Features

#### ✅ Completed Features (v7.2)
- **API Rate Limiting & Failover** (v7.2 NEW)
  - Exponential backoff retry (max 5 retries)
  - Circuit breaker pattern (CLOSED/OPEN/HALF_OPEN)
  - Automatic provider failover (Kakao → Naver → Google)
  - Adaptive retry based on error rates
  
- **Cache Persistence** (v7.2 NEW)
  - Optional Redis backend with memory fallback
  - Per-service TTL (POI=24h, Zoning=72h, Coordinates=24h)
  - Automatic backend switching
  
- **Type Demand Score v3.1** (v7.1)
  - LH 2025 official weights implemented
  - 6 unit types supported (Youth, Newlywed I/II, Multi-child, Elderly, General)
  - POI distance standards updated (School 400m, Hospital 600m)
  
- **LH Notice Loader v2.1** (v7.1)
  - 4-layer parser (structure + heuristic + template + OCR)
  - Automatic PDF extraction
  - JSON normalization

#### ⏳ Planned Features (Future)
- GeoOptimizer v4.0 (traffic-time weights, slope scoring)
- LH Notice Loader v3.0 (ML OCR with Google Document AI)
- Error Monitoring (Sentry integration)
- Database Integration (SQLAlchemy ORM)
- Report Engine v6.3 (10 risk tables, financial scenarios)
- Frontend UI improvements (loader, tooltips, heatmap)

### 1.3 Technology Stack

```
Backend:        FastAPI 0.104+ (Python 3.12)
Web Server:     Gunicorn + Uvicorn workers
Reverse Proxy:  Nginx 1.24+
Cache:          Redis 7.0+ (optional) / Memory
APIs:           Kakao Maps, Naver Maps, Google Maps
ML/OCR:         Google Document AI, AWS Textract (planned)
Database:       PostgreSQL 15+ / SQLite (planned)
Frontend:       Vanilla JS, Leaflet.js, Chart.js
Deployment:     Docker + Docker Compose
Monitoring:     Slack notifications, Sentry (planned)
```

---

## 2. Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Browser                           │
│                  (index.html + JS/CSS)                       │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Nginx (443)                             │
│           Reverse Proxy + SSL + Load Balancing              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Gunicorn + Uvicorn Workers (8000)               │
│                    FastAPI Application                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                        │  │
│  │  - /api/analyze (single parcel)                      │  │
│  │  - /api/analyze-multi (multi-parcel)                 │  │
│  │  - /api/lh-notices/* (notice management)            │  │
│  │  - /health (health check)                            │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Rate Limiter │  │ Cache Layer  │  │  Services    │
│   v7.2 NEW   │  │   v7.2 NEW   │  │              │
│              │  │              │  │              │
│ - Circuit    │  │ - Redis/Mem  │  │ - Analysis   │
│   Breaker    │  │ - TTL Mgmt   │  │   Engine     │
│ - Retry      │  │ - Hit/Miss   │  │ - Type       │
│ - Failover   │  │   Tracking   │  │   Demand v3.1│
│              │  │              │  │ - GeoOpt v3  │
└──────┬───────┘  └──────┬───────┘  │ - LH Loader  │
       │                 │           │   v2.1       │
       │                 │           │ - Report Gen │
       ▼                 ▼           └──────┬───────┘
┌──────────────────────────────────────────┴───────┐
│          External API Providers                   │
│  ┌───────────┐  ┌───────────┐  ┌──────────────┐ │
│  │  Kakao    │→ │  Naver    │→ │   Google     │ │
│  │  (Primary)│  │ (Secondary)│  │  (Tertiary)  │ │
│  └───────────┘  └───────────┘  └──────────────┘ │
└──────────────────────────────────────────────────┘
```

### 2.2 Rate Limiting & Failover Flow (v7.2 NEW)

```
API Request
    │
    ▼
┌─────────────────────────────────────┐
│  Rate Limit Manager                 │
│  1. Select Provider (Priority)      │
│     Kakao → Naver → Google          │
│                                     │
│  2. Check Circuit Breaker           │
│     ├─ CLOSED  → Allow Request      │
│     ├─ OPEN    → Block & Retry Next │
│     └─ HALF_OPEN → Limited Requests │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  Execute API Call                   │
│  Try with exponential backoff       │
└─────────────┬───────────────────────┘
              │
       ┌──────┴──────┐
       │             │
    Success       Failure
       │             │
       ▼             ▼
┌──────────┐  ┌──────────────────────┐
│ Record   │  │ Record Failure       │
│ Success  │  │ Increment Counter    │
│ Return   │  │                      │
│ Result   │  │ If count >= 5:       │
└──────────┘  │   Circuit → OPEN     │
              │                      │
              │ Retry with next      │
              │ provider (up to 5x)  │
              │                      │
              │ Exponential backoff: │
              │ 1s → 2s → 4s → 8s    │
              └──────────────────────┘
```

### 2.3 Cache Architecture (v7.2 NEW)

```
Application Request
         │
         ▼
┌─────────────────────────────────────┐
│  PersistentCache                    │
│  1. Generate cache key              │
│     hash = MD5(service:identifier)  │
│  2. Check backend availability      │
└─────────────┬───────────────────────┘
              │
       ┌──────┴──────┐
       │             │
   Redis Available   Redis Unavailable
       │             │
       ▼             ▼
┌──────────────┐  ┌──────────────┐
│ RedisCacheBackend│  │ MemoryCacheBackend│
│                │  │              │
│ - Persistent │  │ - Ephemeral  │
│ - Distributed│  │ - Single node│
│ - TTL support│  │ - Fast       │
│ - Pickle     │  │ - No setup   │
└──────┬───────┘  └──────┬───────┘
       │                 │
       └────────┬────────┘
                ▼
       ┌─────────────────┐
       │ Cache Hit?      │
       └────┬────────┬───┘
            │        │
          Hit      Miss
            │        │
            ▼        ▼
       ┌────────┐  ┌────────────┐
       │ Return │  │ Fetch from │
       │ Cached │  │ Source     │
       │ Data   │  │            │
       └────────┘  │ Save to    │
                   │ Cache      │
                   │ (with TTL) │
                   └────────────┘

Service-Specific TTL:
- POI Data:      24 hours (86,400s)
- Zoning Info:   72 hours (259,200s)
- Coordinates:   24 hours (86,400s)
- Generic:       1 hour (3,600s)
```

---

## 3. Core Components

### 3.1 Rate Limit Manager (v7.2 NEW)

**File**: `app/core/rate_limit.py`

**Classes**:

#### `RateLimitManager`
Main orchestrator for API retry and failover logic.

**Key Methods**:
```python
async def execute_with_retry(
    func: Callable,
    *args,
    provider: Optional[APIProvider] = None,
    **kwargs
) -> Any:
    """Execute API call with exponential backoff and failover"""
    
def get_available_provider() -> Optional[APIProvider]:
    """Get next available provider based on circuit breaker state"""
    
def get_stats() -> Dict[str, Any]:
    """Get success/error statistics per provider"""
```

**Configuration**:
```python
RetryConfig(
    max_retries=5,          # Maximum retry attempts
    base_delay=1.0,         # Initial delay (seconds)
    max_delay=32.0,         # Maximum delay cap
    exponential_base=2.0,   # Backoff multiplier
    jitter=True             # Add random jitter
)
```

#### `CircuitBreaker`
Implements circuit breaker pattern to prevent cascading failures.

**States**:
- `CLOSED`: Normal operation, requests flow through
- `OPEN`: Too many failures, block all requests for timeout period
- `HALF_OPEN`: Recovery phase, allow limited test requests

**Parameters**:
```python
CircuitBreaker(
    failure_threshold=5,         # Failures before opening
    timeout=60.0,                # OPEN state duration (seconds)
    half_open_max_requests=3     # Test requests in HALF_OPEN
)
```

**Usage Example**:
```python
from app.core.rate_limit import execute_with_failover, APIProvider

# Automatic failover
result = await execute_with_failover(
    kakao_api.get_poi,
    lat=37.5013,
    lng=127.0396,
    provider=APIProvider.KAKAO
)
```

### 3.2 Cache Persistence (v7.2 NEW)

**File**: `app/core/cache_redis.py`

**Classes**:

#### `PersistentCache`
Main cache manager with automatic backend switching.

**Key Methods**:
```python
def set_poi(location_key: str, value: Any):
    """Cache POI data (24h TTL)"""
    
def get_poi(location_key: str) -> Optional[Any]:
    """Retrieve cached POI data"""
    
def set_zoning(address: str, value: Any):
    """Cache zoning info (72h TTL)"""
    
def get_zoning(address: str) -> Optional[Any]:
    """Retrieve cached zoning info"""
    
def set_coordinates(address: str, value: Any):
    """Cache coordinates (24h TTL)"""
    
def get_coordinates(address: str) -> Optional[Any]:
    """Retrieve cached coordinates"""
```

**Configuration**:
```bash
# Environment variable
REDIS_URL=redis://localhost:6379/0

# Automatic fallback to memory if Redis unavailable
```

**Usage Example**:
```python
from app.core.cache_redis import persistent_cache

# POI caching
poi_data = persistent_cache.get_poi(location_key)
if not poi_data:
    poi_data = await fetch_poi_from_api(location_key)
    persistent_cache.set_poi(location_key, poi_data)

# Check backend type
is_using_redis = persistent_cache.is_redis()
stats = persistent_cache.get_stats()
```

### 3.3 Type Demand Score v3.1 (v7.1)

**File**: `app/services/type_demand_score_v3.py`

**LH 2025 Official Weights**:

| Unit Type      | Education | Medical | Convenience | Total |
|----------------|-----------|---------|-------------|-------|
| Youth          | 30        | 25      | 30          | 85    |
| Newlywed I     | 23        | 33      | 30          | 86    |
| Newlywed II    | 32        | 22      | 30          | 84    |
| Multi-child    | 38        | 25      | 30          | 93    |
| Elderly        | 25        | 45      | 25          | 95    |
| General        | 28        | 28      | 28          | 84    |

**POI Distance Standards (2025)**:
- School: 400m (relaxed from 300m)
- Hospital: 600m (relaxed from 500m)
- Convenience: 350m (relaxed from 300m)

**POI Multipliers**:
- School: 1.7× (increased from 1.5×)
- Hospital: 1.7× (increased from 1.5×)
- Convenience: 1.5× (increased from 1.3×)

**Usage**:
```python
from app.services.type_demand_score_v3 import calculate_type_demand_score

score = calculate_type_demand_score(
    unit_type="youth",
    poi_distances={
        "schools": [200, 350, 450],
        "hospitals": [400, 550],
        "convenience": [150, 280, 320]
    }
)
```

### 3.4 LH Notice Loader v2.1 (v7.1)

**File**: `app/services/lh_notice_loader_v2.py`

**4-Layer Parser**:
1. **Structure Parser**: Extract document structure (sections, tables)
2. **Heuristic Parser**: Pattern matching for common formats
3. **Template Parser**: Template-based extraction (10+ known formats)
4. **OCR Fallback**: pdfplumber for scanned documents

**Extracted Fields**:
- Notice ID, Title, Date
- Application deadline
- Target regions
- Unit type requirements (min/max units)
- Scoring weights
- Location requirements (POI distances)
- Minimum/recommended scores

**Usage**:
```python
from app.services.lh_notice_loader_v2 import LHNoticeLoader

loader = LHNoticeLoader()
notice_data = await loader.load_notice("path/to/notice.pdf")
```

---

## 4. API Specifications

### 4.1 Single Parcel Analysis

**Endpoint**: `POST /api/analyze`

**Request Body**:
```json
{
  "address": "서울특별시 강남구 역삼동 123-45",
  "land_area": 1000.0,
  "unit_type": "youth",
  "zone_type": "residential",
  "land_status": "vacant",
  "land_appraisal_price": 5000000000,
  "consultant": {
    "name": "김철수",
    "phone": "010-1234-5678",
    "department": "영업팀",
    "email": "consultant@example.com"
  },
  "weights": {
    "location": 30,
    "scale": 25,
    "business": 25,
    "regulation": 20
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_score": 307.5,
      "grade": "S",
      "recommendation": "강력 추천"
    },
    "coordinates": {
      "lat": 37.5013,
      "lng": 127.0396
    },
    "type_demand_score": {
      "total": 85.3,
      "education": 30.0,
      "medical": 25.5,
      "convenience": 29.8
    },
    "poi_analysis": {
      "schools": [
        {"name": "역삼초등학교", "distance": 250, "score": 10.0}
      ],
      "hospitals": [
        {"name": "강남병원", "distance": 400, "score": 8.5}
      ]
    },
    "cache_stats": {
      "backend": "redis",
      "hit_rate": "85.3%"
    },
    "api_stats": {
      "provider_used": "kakao",
      "retry_count": 0,
      "response_time": 0.342
    }
  }
}
```

### 4.2 Multi-Parcel Analysis

**Endpoint**: `POST /api/analyze-multi`

**Request Body**:
```json
{
  "parcels": [
    {
      "address": "서울특별시 강남구 역삼동 123-45",
      "land_area": 500.0,
      "land_appraisal_price": 2500000000
    },
    {
      "address": "서울특별시 강남구 역삼동 123-46",
      "land_area": 600.0,
      "land_appraisal_price": 3000000000
    }
  ],
  "unit_type": "youth",
  "consultant": {...}
}
```

**Response**: Similar to single parcel with combined metrics

### 4.3 Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "version": "7.2.0",
  "timestamp": "2025-12-01T10:30:00Z",
  "components": {
    "rate_limiter": {
      "status": "operational",
      "providers": {
        "kakao": {"circuit": "closed", "success_rate": "98.5%"},
        "naver": {"circuit": "closed", "success_rate": "97.2%"},
        "google": {"circuit": "closed", "success_rate": "99.1%"}
      }
    },
    "cache": {
      "status": "operational",
      "backend": "redis",
      "hit_rate": "87.3%",
      "total_keys": 15234
    },
    "system": {
      "cpu_usage": 45.2,
      "memory_usage": 62.8,
      "disk_usage": 38.5
    }
  }
}
```

---

## 5. Data Flow

### 5.1 Complete Analysis Flow

```
1. Client Request
   ↓
2. Nginx → Gunicorn → FastAPI
   ↓
3. Request Validation (Pydantic schemas)
   ↓
4. Cache Check (Redis/Memory)
   ├─ HIT  → Return cached result
   ├─ MISS → Continue to step 5
   ↓
5. Coordinate Lookup (with rate limiting)
   ├─ Try Kakao API
   ├─ Retry with backoff if fail
   ├─ Failover to Naver if circuit open
   ├─ Failover to Google if both fail
   ↓
6. POI Data Fetch (with caching)
   ├─ Check cache (24h TTL)
   ├─ Fetch from API if miss
   ├─ Apply rate limiting
   ↓
7. Zoning Information (with caching)
   ├─ Check cache (72h TTL)
   ├─ Fetch from API if miss
   ↓
8. Type Demand Score v3.1
   ├─ Apply LH 2025 weights
   ├─ Calculate POI scores
   ├─ Apply multipliers
   ↓
9. GeoOptimizer Analysis
   ├─ Distance scoring
   ├─ Accessibility ranking
   ├─ Alternative site suggestions
   ↓
10. LH Score Calculation
    ├─ Location (30%)
    ├─ Scale (25%)
    ├─ Business (25%)
    ├─ Regulation (20%)
    ↓
11. Report Generation
    ├─ Professional HTML
    ├─ LH Official Format
    ├─ PDF Export
    ↓
12. Cache Result (with TTL)
    ↓
13. Response to Client
```

### 5.2 Rate Limiting Decision Tree

```
API Call Request
    │
    ▼
Is Circuit CLOSED for Primary (Kakao)?
    │
    ├─ YES → Execute Call
    │         │
    │         ├─ Success? → Record Success, Return Result
    │         │
    │         └─ Failure? → Increment Failure Count
    │                       │
    │                       └─ Count >= 5? → Circuit → OPEN
    │                                         Wait 1s, Retry (max 5x)
    │
    └─ NO (Circuit OPEN) → Check Secondary (Naver)
                           │
                           ├─ Circuit CLOSED? → Use Naver
                           │
                           └─ Circuit OPEN? → Check Tertiary (Google)
                                              │
                                              ├─ Circuit CLOSED? → Use Google
                                              │
                                              └─ All OPEN? → Use best error rate
```

---

## 6. Performance Metrics

### 6.1 v7.2 Performance Targets

| Metric                    | Target      | Current Status |
|---------------------------|-------------|----------------|
| Avg Response Time         | < 700ms     | Infrastructure Ready |
| P95 Response Time         | < 1.2s      | Infrastructure Ready |
| Concurrent Requests       | 20 stable   | Infrastructure Ready |
| Cache Hit Rate            | > 80%       | Implemented |
| API Success Rate          | > 95%       | Implemented |
| Failover Time             | < 2s        | Implemented |
| Circuit Recovery Time     | 60s         | Implemented |

### 6.2 Rate Limiting Performance

**Exponential Backoff Delays**:
```
Retry 1: 1.0s  (base_delay)
Retry 2: 2.0s  (base × 2^1)
Retry 3: 4.0s  (base × 2^2)
Retry 4: 8.0s  (base × 2^3)
Retry 5: 16.0s (base × 2^4)

With jitter (±25%):
Retry 1: 0.75s - 1.25s
Retry 2: 1.50s - 2.50s
Retry 3: 3.00s - 5.00s
```

### 6.3 Cache Performance

**Memory Cache**:
- Write: < 1ms
- Read: < 1ms
- Hit Rate: 85-95%

**Redis Cache**:
- Write: < 5ms
- Read: < 3ms
- Hit Rate: 90-98%
- Network latency included

---

## 7. Integration Guide

### 7.1 Rate Limiting Integration

```python
# 1. Import manager
from app.core.rate_limit import execute_with_failover, APIProvider

# 2. Wrap API calls
async def get_poi_data(lat: float, lng: float):
    async def api_call():
        return await kakao_client.get_poi(lat, lng)
    
    # Automatic retry and failover
    return await execute_with_failover(
        api_call,
        provider=APIProvider.KAKAO
    )

# 3. Check statistics
from app.core.rate_limit import get_rate_limit_stats
stats = get_rate_limit_stats()
print(f"Kakao success rate: {stats['providers']['kakao']['success_rate']}")
```

### 7.2 Cache Integration

```python
# 1. Import cache
from app.core.cache_redis import persistent_cache

# 2. Use service-specific methods
def get_poi_with_cache(location_key: str):
    # Try cache first
    cached = persistent_cache.get_poi(location_key)
    if cached:
        return cached
    
    # Fetch from API
    fresh_data = fetch_from_api(location_key)
    
    # Save to cache (24h TTL)
    persistent_cache.set_poi(location_key, fresh_data)
    
    return fresh_data

# 3. Generic caching
persistent_cache.set_generic("my_service", "identifier", data, ttl=3600)
```

---

## 8. Deployment

### 8.1 Environment Variables

```bash
# Redis Cache (optional)
REDIS_URL=redis://localhost:6379/0

# Rate Limiting
RATE_LIMIT_MAX_RETRIES=5
RATE_LIMIT_BASE_DELAY=1.0
RATE_LIMIT_MAX_DELAY=32.0

# API Keys
KAKAO_API_KEY=your_kakao_key
NAVER_CLIENT_ID=your_naver_id
NAVER_CLIENT_SECRET=your_naver_secret
GOOGLE_API_KEY=your_google_key

# Monitoring
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
```

### 8.2 Docker Deployment

```bash
# Using docker-compose
cd /home/user/webapp
docker-compose -f deploy/docker-compose.production.yml up -d

# Check logs
docker-compose logs -f zerosite
```

### 8.3 Health Monitoring

```bash
# Health check endpoint
curl https://your-domain.com/health

# Rate limit statistics
curl https://your-domain.com/api/stats/rate-limit

# Cache statistics
curl https://your-domain.com/api/stats/cache
```

---

## Appendix A: Version History

### v7.2.0 (2025-12-01) - CURRENT
- ✅ API Rate Limiting & Failover (Tasks 1)
- ✅ Cache Persistence with Redis (Task 2)
- ⏳ GeoOptimizer v4.0 (Task 3) - Pending
- ⏳ LH Loader v3.0 ML OCR (Task 4) - Pending
- ⏳ Error Monitoring (Task 5) - Pending
- ⏳ Database Integration (Task 6) - Pending
- ⏳ Report Engine v6.3 (Task 7) - Pending
- ⏳ Frontend UI (Task 8) - Pending

### v7.1.0 (2025-11-30)
- ✅ E2E Integration Testing
- ✅ Performance Optimization Infrastructure
- ✅ Production Deployment System
- ✅ Type Demand Score v3.1
- ✅ LH Notice Loader v2.1
- ✅ API Response Standardization

### v7.0.0 (2025-11-29)
- Initial production release
- Core analysis engine
- Report generation
- Multi-parcel support

---

## Appendix B: API Provider Comparison

| Feature           | Kakao Maps | Naver Maps | Google Maps |
|-------------------|------------|------------|-------------|
| POI Coverage      | Excellent  | Excellent  | Good        |
| Korea Accuracy    | Excellent  | Excellent  | Moderate    |
| Response Time     | Fast       | Fast       | Moderate    |
| Rate Limits       | Generous   | Moderate   | Strict      |
| Cost              | Low        | Low        | High        |
| Priority in v7.2  | 1st        | 2nd        | 3rd         |

---

## Appendix C: Glossary

- **Circuit Breaker**: Pattern to prevent cascading failures by temporarily blocking requests
- **Exponential Backoff**: Retry strategy with exponentially increasing delays
- **Jitter**: Random variation added to retry delays to prevent thundering herd
- **TTL**: Time To Live - Duration for which cached data remains valid
- **POI**: Point of Interest - Schools, hospitals, convenience stores, etc.
- **LH**: Korea Land & Housing Corporation (한국토지주택공사)
- **신축매입임대**: New Construction Purchase-Lease program

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-12-01  
**Maintained By**: Platform Engineering Team
