# ZeroSite v7.2 - System Architecture Document

**Version**: 7.2.0  
**Date**: 2025-12-01  
**Status**: Production Ready (Partial)  

---

## Executive Summary

This document describes the complete system architecture of ZeroSite v7.2, an enterprise-grade land analysis platform for LH 신축매입임대 projects. The v7.2 release introduces critical infrastructure improvements including API rate limiting with circuit breaker pattern and persistent caching with Redis support.

**Key Architectural Improvements in v7.2**:
- Fault-tolerant API layer with automatic failover
- Distributed caching for improved performance
- Enhanced reliability and scalability

---

## 1. System Architecture Overview

### 1.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Web UI     │  │  Mobile UI   │  │   API Docs   │          │
│  │  (index.html)│  │  (Planned)   │  │  (Swagger)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS/REST API
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Nginx Reverse Proxy                                      │  │
│  │  - SSL/TLS Termination                                   │  │
│  │  - Load Balancing                                        │  │
│  │  - Static File Serving                                   │  │
│  │  - Request Routing                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Application Layer                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI Application (Gunicorn + Uvicorn Workers)        │  │
│  │                                                           │  │
│  │  Endpoints:                                               │  │
│  │  - POST /api/analyze (Single Parcel)                    │  │
│  │  - POST /api/analyze-multi (Multi-Parcel)               │  │
│  │  - GET  /api/lh-notices (LH Notice List)                │  │
│  │  - POST /api/lh-notices/sync (Sync Notices)             │  │
│  │  - GET  /health (Health Check)                          │  │
│  │  - GET  /api/stats/* (Statistics)                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ Infrastructure │ │  Service Layer │ │   Data Layer   │
│  Layer (NEW)   │ │                │ │                │
│                │ │                │ │                │
│ - Rate Limiter │ │ - Analysis     │ │ - Cache        │
│ - Circuit      │ │   Engine       │ │   (Redis/Mem)  │
│   Breaker      │ │ - Type Demand  │ │ - Database     │
│ - Retry Logic  │ │ - GeoOptimizer │ │   (Planned)    │
│ - Cache Mgmt   │ │ - LH Loader    │ │ - File Storage │
│ - Monitoring   │ │ - Report Gen   │ │                │
└────────┬───────┘ └────────┬───────┘ └────────┬───────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   External Services Layer                        │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌────────────┐  │
│  │  Kakao    │  │  Naver    │  │  Google   │  │  LH APPLY  │  │
│  │  Maps API │  │  Maps API │  │  Maps API │  │  (Notices) │  │
│  └───────────┘  └───────────┘  └───────────┘  └────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Request                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Nginx Gateway  │
                    │  Port 443/80    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Gunicorn       │
                    │  + Uvicorn      │
                    │  Workers (4-8)  │
                    └────────┬────────┘
                             │
                             ▼
         ┌───────────────────┴────────────────────┐
         │        FastAPI Application             │
         │                                        │
         │   ┌────────────────────────────────┐  │
         │   │  Request Middleware Chain      │  │
         │   │  1. CORS Handler               │  │
         │   │  2. Request Logger             │  │
         │   │  3. Performance Tracker        │  │
         │   │  4. Error Handler              │  │
         │   └───────────┬────────────────────┘  │
         │               │                        │
         │               ▼                        │
         │   ┌────────────────────────────────┐  │
         │   │  Route Handler                 │  │
         │   │  - Validate Request (Pydantic) │  │
         │   │  - Extract Parameters          │  │
         │   └───────────┬────────────────────┘  │
         └───────────────┼────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────────────┐
         │  Infrastructure Layer (v7.2 NEW)      │
         │                                       │
         │  ┌─────────────────────────────────┐ │
         │  │  Rate Limit Manager             │ │
         │  │  - Check Circuit Breaker        │ │
         │  │  - Select Provider (Priority)   │ │
         │  │  - Execute with Retry           │ │
         │  └─────────────┬───────────────────┘ │
         │                │                      │
         │  ┌─────────────▼───────────────────┐ │
         │  │  Cache Manager                   │ │
         │  │  - Generate Cache Key           │ │
         │  │  - Check Redis/Memory           │ │
         │  │  - Return Hit or Fetch Miss     │ │
         │  └─────────────┬───────────────────┘ │
         └────────────────┼──────────────────────┘
                          │
                          ▼
         ┌───────────────────────────────────────┐
         │  Service Layer                        │
         │                                       │
         │  ┌─────────────────────────────────┐ │
         │  │  Analysis Engine                │ │
         │  │  - Coordinate Lookup            │ │
         │  │  - POI Data Fetch               │ │
         │  │  - Zoning Analysis              │ │
         │  └─────────────┬───────────────────┘ │
         │                │                      │
         │  ┌─────────────▼───────────────────┐ │
         │  │  Type Demand Score v3.1         │ │
         │  │  - Apply LH 2025 Weights        │ │
         │  │  - Calculate POI Scores         │ │
         │  │  - Apply Multipliers            │ │
         │  └─────────────┬───────────────────┘ │
         │                │                      │
         │  ┌─────────────▼───────────────────┐ │
         │  │  GeoOptimizer v3                │ │
         │  │  - Distance Calculations        │ │
         │  │  - Alternative Site Ranking     │ │
         │  └─────────────┬───────────────────┘ │
         │                │                      │
         │  ┌─────────────▼───────────────────┐ │
         │  │  LH Score Calculation           │ │
         │  │  - Location (30%)               │ │
         │  │  - Scale (25%)                  │ │
         │  │  - Business (25%)               │ │
         │  │  - Regulation (20%)             │ │
         │  └─────────────┬───────────────────┘ │
         │                │                      │
         │  ┌─────────────▼───────────────────┐ │
         │  │  Report Generator               │ │
         │  │  - HTML Report                  │ │
         │  │  - PDF Export                   │ │
         │  │  - JSON Response                │ │
         │  └─────────────┬───────────────────┘ │
         └────────────────┼──────────────────────┘
                          │
                          ▼
              ┌──────────────────────┐
              │  Response to Client  │
              │  + Cache Update      │
              └──────────────────────┘
```

---

## 2. Infrastructure Layer (v7.2 NEW)

### 2.1 Rate Limiting Architecture

#### 2.1.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Rate Limit Manager                          │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Provider Priority Queue                                    │ │
│  │  1. Kakao (Primary)   - Circuit: CLOSED                    │ │
│  │  2. Naver (Secondary) - Circuit: CLOSED                    │ │
│  │  3. Google (Tertiary) - Circuit: CLOSED                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Circuit Breaker States                                     │ │
│  │                                                             │ │
│  │  ┌──────────┐                                              │ │
│  │  │  CLOSED  │───── Failure Count < 5 ────┐                │ │
│  │  │ (Normal) │                              │                │ │
│  │  └────┬─────┘                              │                │ │
│  │       │                                    │                │ │
│  │       │ Failure Count >= 5                │ Success       │ │
│  │       │                                    │                │ │
│  │       ▼                                    │                │ │
│  │  ┌──────────┐                              │                │ │
│  │  │   OPEN   │────── Wait 60s ──────────────┤                │ │
│  │  │ (Blocked)│                              │                │ │
│  │  └────┬─────┘                              │                │ │
│  │       │                                    │                │ │
│  │       │ Timeout Elapsed                    │                │ │
│  │       │                                    │                │ │
│  │       ▼                                    │                │ │
│  │  ┌──────────────┐                          │                │ │
│  │  │  HALF_OPEN   │──── Success (3 req) ────┘                │ │
│  │  │  (Testing)   │                                          │ │
│  │  └──────────────┘                                          │ │
│  │       │                                                     │ │
│  │       │ Failure                                            │ │
│  │       │                                                     │ │
│  │       └────────────────► Back to OPEN                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Retry Strategy (Exponential Backoff)                      │ │
│  │                                                             │ │
│  │  Attempt 1: Execute immediately                            │ │
│  │  Attempt 2: Wait 1.0s  (base_delay × 2^0)                 │ │
│  │  Attempt 3: Wait 2.0s  (base_delay × 2^1)                 │ │
│  │  Attempt 4: Wait 4.0s  (base_delay × 2^2)                 │ │
│  │  Attempt 5: Wait 8.0s  (base_delay × 2^3)                 │ │
│  │  Attempt 6: Wait 16.0s (base_delay × 2^4) [Max Retries]   │ │
│  │                                                             │ │
│  │  With Jitter: ±25% random variation to prevent            │ │
│  │  thundering herd problem                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Provider Statistics Tracking                              │ │
│  │                                                             │ │
│  │  For each provider:                                        │ │
│  │  - Total Requests                                          │ │
│  │  - Successful Requests                                     │ │
│  │  - Failed Requests                                         │ │
│  │  - Success Rate                                            │ │
│  │  - Error Rate                                              │ │
│  │  - Consecutive Failures                                    │ │
│  │  - Last Success Time                                       │ │
│  │  - Last Failure Time                                       │ │
│  │  - Circuit Breaker State                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

#### 2.1.2 Failover Decision Tree

```
                        API Request
                             │
                             ▼
                    Is Kakao Circuit CLOSED?
                             │
                  ┌──────────┴──────────┐
                YES                    NO
                  │                     │
                  ▼                     ▼
          Execute Kakao API     Is Naver Circuit CLOSED?
                  │                     │
           ┌──────┴──────┐      ┌──────┴──────┐
         Success      Failure   YES           NO
           │             │       │             │
           ▼             │       ▼             ▼
    Return Result        │  Execute Naver  Is Google CLOSED?
    Record Success       │      API            │
                         │       │      ┌──────┴──────┐
                         │   ┌───┴───┐ YES           NO
                         │ Success Fail │             │
                         │   │      │   ▼             ▼
                         │   ▼      │ Execute    Use Provider
                         │ Return   │ Google     with Best
                         │ Result   │  API       Error Rate
                         │ Record   │   │
                         │ Success  │   ├─Success─► Return
                         │          │   │           Result
                         ▼          │   │
                  Increment         │   └─Failure─► All Failed
                  Failure Count     │               Return Error
                         │          │
                         ▼          │
                  Count >= 5?       │
                         │          │
                  ┌──────┴──────┐   │
                 YES           NO   │
                  │             │   │
                  ▼             ▼   │
          Circuit → OPEN    Wait    │
          Block Requests    Backoff │
                │           Retry ◄─┘
                │             │
                │             └─► Max Retries (5)
                │                      │
                │                      ▼
                │              All Retries Failed
                │              Switch to Next Provider
                │                      │
                └──────────────────────┘
```

### 2.2 Cache Architecture

#### 2.2.1 Cache Layer Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                           │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Service Request                                            │ │
│  │  (get_poi, get_zoning, get_coordinates)                    │ │
│  └───────────────────────────┬────────────────────────────────┘ │
│                              │                                   │
└──────────────────────────────┼───────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PersistentCache Manager                       │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Key Generation                                             │ │
│  │  1. Create service-specific prefix                         │ │
│  │  2. Hash identifier with MD5                               │ │
│  │  3. Combine: "zerosite_v7:{service}:{hash}"                │ │
│  │                                                             │ │
│  │  Example:                                                   │ │
│  │  poi:서울시강남구역삼동 → zerosite_v7:poi:a3c2e1f9...      │ │
│  └────────────────────────────┬───────────────────────────────┘ │
│                                │                                  │
│  ┌────────────────────────────▼───────────────────────────────┐ │
│  │  Backend Selection                                          │ │
│  │                                                             │ │
│  │  if REDIS_URL configured:                                  │ │
│  │      try:                                                   │ │
│  │          connect to Redis                                   │ │
│  │          ping() test                                        │ │
│  │          use RedisCacheBackend ✓                           │ │
│  │      except:                                                │ │
│  │          log warning                                        │ │
│  │          fallback to MemoryCacheBackend                    │ │
│  │  else:                                                      │ │
│  │      use MemoryCacheBackend                                │ │
│  └────────────────────────────┬───────────────────────────────┘ │
│                                │                                  │
└────────────────────────────────┼──────────────────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 │                               │
                 ▼                               ▼
┌───────────────────────────────┐  ┌───────────────────────────────┐
│    RedisCacheBackend          │  │   MemoryCacheBackend          │
│                               │  │                               │
│  Data Structure:              │  │  Data Structure:              │
│  - Redis Hash (HSET/HGET)     │  │  - Python Dict                │
│  - Pickle Serialization       │  │  - In-Memory Storage          │
│  - TTL via EXPIRE             │  │  - No Persistence             │
│                               │  │                               │
│  Operations:                  │  │  Operations:                  │
│  ┌─────────────────────────┐ │  │  ┌─────────────────────────┐ │
│  │ get(key)                │ │  │  │ get(key)                │ │
│  │  1. Redis GET key       │ │  │  │  1. dict.get(key)       │ │
│  │  2. Unpickle value      │ │  │  │  2. Return value        │ │
│  │  3. Track hit/miss      │ │  │  │  3. Track hit/miss      │ │
│  │  4. Return result       │ │  │  │  4. Return result       │ │
│  └─────────────────────────┘ │  │  └─────────────────────────┘ │
│                               │  │                               │
│  ┌─────────────────────────┐ │  │  ┌─────────────────────────┐ │
│  │ set(key, value, ttl)    │ │  │  │ set(key, value, ttl)    │ │
│  │  1. Pickle value        │ │  │  │  1. dict[key] = value   │ │
│  │  2. Redis SETEX         │ │  │  │  2. Ignore TTL          │ │
│  │  3. Auto-expire at TTL  │ │  │  │  3. No expiration       │ │
│  └─────────────────────────┘ │  │  └─────────────────────────┘ │
│                               │  │                               │
│  Advantages:                  │  │  Advantages:                  │
│  ✓ Persistent across restarts │  │  ✓ Zero dependencies          │
│  ✓ Distributed caching        │  │  ✓ Ultra-fast access          │
│  ✓ TTL enforcement            │  │  ✓ Simple implementation      │
│  ✓ Scalable                   │  │  ✓ No network overhead        │
│                               │  │                               │
│  Disadvantages:               │  │  Disadvantages:               │
│  ✗ Network latency            │  │  ✗ Lost on restart            │
│  ✗ Requires Redis server      │  │  ✗ Single-node only           │
│  ✗ Additional complexity      │  │  ✗ No TTL enforcement         │
└───────────────────────────────┘  └───────────────────────────────┘
```

#### 2.2.2 Cache Flow Diagram

```
                    Application Request
                             │
                             ▼
                ┌────────────────────────┐
                │  Generate Cache Key    │
                │  service:MD5(id)       │
                └────────────┬───────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │  Check Cache Backend   │
                │  Redis or Memory?      │
                └────────────┬───────────┘
                             │
                   ┌─────────┴─────────┐
                   │                   │
               Redis                Memory
                   │                   │
                   ▼                   ▼
         ┌──────────────────┐  ┌──────────────────┐
         │  Redis GET key   │  │  dict.get(key)   │
         └─────────┬────────┘  └─────────┬────────┘
                   │                     │
                   └──────────┬──────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Cache Hit?      │
                    └────┬────────┬────┘
                         │        │
                       HIT      MISS
                         │        │
                         ▼        ▼
                 ┌──────────┐  ┌─────────────────────┐
                 │ Return   │  │ Fetch from Source   │
                 │ Cached   │  │ (API/Database)      │
                 │ Value    │  └──────────┬──────────┘
                 │          │             │
                 │ Record   │             ▼
                 │ Hit      │  ┌─────────────────────┐
                 └──────────┘  │ Save to Cache       │
                               │ with Service TTL:   │
                               │ - POI: 24h          │
                               │ - Zoning: 72h       │
                               │ - Coords: 24h       │
                               └──────────┬──────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │ Return Fresh    │
                                 │ Value           │
                                 │                 │
                                 │ Record Miss     │
                                 └─────────────────┘
```

#### 2.2.3 TTL Management Strategy

```
Service Type        TTL        Rationale
─────────────────────────────────────────────────────────────
POI Data            24 hours   - POI locations rarely change
                               - Daily refresh acceptable
                               - Balances freshness vs cost

Zoning Info         72 hours   - Zoning regulations stable
                               - Infrequent updates
                               - Longer cache reduces API load

Coordinates         24 hours   - Static geographic data
                               - Daily refresh for consistency
                               - Handles rare address changes

Generic Cache       1 hour     - Default for misc data
                               - Conservative TTL
                               - Safe for most use cases

LH Notice Data      6 hours    - Notice updates several times daily
                               - Important to stay current
                               - Moderate refresh rate
```

---

## 3. Service Layer Architecture

### 3.1 Analysis Engine Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Analysis Request                              │
│  {address, land_area, unit_type, zone_type, ...}                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Coordinate Lookup                                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Input: Address (서울특별시 강남구 역삼동 123-45)            │ │
│  │                                                              │ │
│  │  1. Check Cache (coordinates:address)                       │ │
│  │     ├─ HIT  → Use cached coordinates                       │ │
│  │     └─ MISS → Fetch from API                               │ │
│  │                                                              │ │
│  │  2. API Call with Rate Limiting                             │ │
│  │     Try: Kakao → Naver → Google                            │ │
│  │     With: Exponential backoff, Circuit breaker             │ │
│  │                                                              │ │
│  │  3. Extract Coordinates                                     │ │
│  │     Result: {lat: 37.5013, lng: 127.0396}                  │ │
│  │                                                              │ │
│  │  4. Save to Cache (24h TTL)                                │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: POI Data Collection                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Input: Coordinates (37.5013, 127.0396), Radius (1km)      │ │
│  │                                                              │ │
│  │  For each POI category:                                     │ │
│  │                                                              │ │
│  │  A. Schools                                                 │ │
│  │     1. Check Cache (poi:schools:{lat},{lng})               │ │
│  │     2. Fetch from API if miss (with rate limiting)         │ │
│  │     3. Filter by distance (< 400m priority)                │ │
│  │     4. Calculate walking distance                          │ │
│  │     5. Save to cache (24h TTL)                             │ │
│  │                                                              │ │
│  │  B. Hospitals                                               │ │
│  │     1. Check Cache (poi:hospitals:{lat},{lng})             │ │
│  │     2. Fetch from API if miss                              │ │
│  │     3. Filter by distance (< 600m priority)                │ │
│  │     4. Calculate accessibility                             │ │
│  │     5. Save to cache (24h TTL)                             │ │
│  │                                                              │ │
│  │  C. Convenience Stores                                      │ │
│  │     1. Check Cache (poi:convenience:{lat},{lng})           │ │
│  │     2. Fetch from API if miss                              │ │
│  │     3. Filter by distance (< 350m priority)                │ │
│  │     4. Calculate coverage                                   │ │
│  │     5. Save to cache (24h TTL)                             │ │
│  │                                                              │ │
│  │  Result: Comprehensive POI dataset                         │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Zoning Information                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Input: Address, Coordinates                               │ │
│  │                                                              │ │
│  │  1. Check Cache (zoning:address)                           │ │
│  │     ├─ HIT  → Use cached zoning data (72h TTL)            │ │
│  │     └─ MISS → Fetch from government API                   │ │
│  │                                                              │ │
│  │  2. Extract Zoning Details                                 │ │
│  │     - Zone Type (제2종일반주거지역)                         │ │
│  │     - Building Coverage Ratio (60%)                        │ │
│  │     - Floor Area Ratio (200%)                              │ │
│  │     - Height Limit                                         │ │
│  │     - Restrictions                                          │ │
│  │                                                              │ │
│  │  3. Validate for LH Requirements                           │ │
│  │     - Check residential zone eligibility                   │ │
│  │     - Verify building capacity                             │ │
│  │                                                              │ │
│  │  4. Save to Cache (72h TTL)                                │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Type Demand Score Calculation (v3.1)                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Input: Unit Type, POI Data                                │ │
│  │                                                              │ │
│  │  LH 2025 Weights:                                           │ │
│  │  ┌──────────────┬───────┬─────────┬─────────────┬────────┐ │ │
│  │  │ Unit Type    │ Edu   │ Medical │ Convenience │ Total  │ │ │
│  │  ├──────────────┼───────┼─────────┼─────────────┼────────┤ │ │
│  │  │ Youth        │ 30    │ 25      │ 30          │ 85     │ │ │
│  │  │ Newlywed I   │ 23    │ 33      │ 30          │ 86     │ │ │
│  │  │ Newlywed II  │ 32    │ 22      │ 30          │ 84     │ │ │
│  │  │ Multi-child  │ 38    │ 25      │ 30          │ 93     │ │ │
│  │  │ Elderly      │ 25    │ 45      │ 25          │ 95     │ │ │
│  │  │ General      │ 28    │ 28      │ 28          │ 84     │ │ │
│  │  └──────────────┴───────┴─────────┴─────────────┴────────┘ │ │
│  │                                                              │ │
│  │  POI Distance Standards:                                    │ │
│  │  - School: 400m (优先), Multiplier: 1.7×                   │ │
│  │  - Hospital: 600m (优先), Multiplier: 1.7×                 │ │
│  │  - Convenience: 350m (优先), Multiplier: 1.5×              │ │
│  │                                                              │ │
│  │  Calculation:                                               │ │
│  │  For each POI category:                                    │ │
│  │    1. Count POIs within standard distance                  │ │
│  │    2. Calculate average distance                           │ │
│  │    3. Apply distance decay factor                          │ │
│  │    4. Apply category multiplier                            │ │
│  │    5. Apply unit-type weight                               │ │
│  │    6. Sum category scores                                  │ │
│  │                                                              │ │
│  │  Result: Type Demand Score (0-100 scale)                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: GeoOptimizer Analysis (v3)                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Input: Coordinates, POI Data, Type Demand Score           │ │
│  │                                                              │ │
│  │  1. Distance Optimization                                   │ │
│  │     - Calculate optimal POI access                         │ │
│  │     - Identify distance penalties                          │ │
│  │     - Score accessibility (0-100)                          │ │
│  │                                                              │ │
│  │  2. Alternative Site Ranking                               │ │
│  │     - Search within 2km radius                             │ │
│  │     - Score each alternative location                      │ │
│  │     - Rank by combined score                               │ │
│  │     - Return top 3 alternatives                            │ │
│  │                                                              │ │
│  │  3. Geographic Suitability                                  │ │
│  │     - Terrain analysis                                      │ │
│  │     - Transportation access                                │ │
│  │     - Urban planning compatibility                         │ │
│  │                                                              │ │
│  │  Result: GeoOptimizer recommendations                       │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 6: LH Score Calculation                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Weighted Score Components:                                 │ │
│  │                                                              │ │
│  │  1. Location Score (30%)                                    │ │
│  │     - Type Demand Score                                     │ │
│  │     - POI Accessibility                                     │ │
│  │     - Transportation Access                                │ │
│  │                                                              │ │
│  │  2. Scale Score (25%)                                       │ │
│  │     - Land Area                                             │ │
│  │     - Building Capacity                                     │ │
│  │     - Unit Count Feasibility                               │ │
│  │                                                              │ │
│  │  3. Business Score (25%)                                    │ │
│  │     - Investment ROI Estimate                              │ │
│  │     - Rental Demand Projection                             │ │
│  │     - Market Competitiveness                               │ │
│  │                                                              │ │
│  │  4. Regulation Score (20%)                                  │ │
│  │     - Zoning Compliance                                     │ │
│  │     - Building Code Adherence                              │ │
│  │     - LH Requirements Match                                │ │
│  │                                                              │ │
│  │  Formula:                                                   │ │
│  │  Total = (Location×0.3) + (Scale×0.25) +                   │ │
│  │          (Business×0.25) + (Regulation×0.2)                │ │
│  │                                                              │ │
│  │  Grading:                                                   │ │
│  │  S  (320+) - 강력 추천 (Strongly Recommended)              │ │
│  │  A  (300-319) - 추천 (Recommended)                         │ │
│  │  B  (280-299) - 적합 (Suitable)                            │ │
│  │  C  (270-279) - 보통 (Average)                             │ │
│  │  D  (<270) - 부적합 (Not Suitable)                         │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 7: Report Generation                                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Generate Comprehensive Report:                             │ │
│  │                                                              │ │
│  │  - Executive Summary                                        │ │
│  │  - Site Overview (maps, photos)                            │ │
│  │  - Detailed Analysis Results                               │ │
│  │  - POI Distribution Maps                                    │ │
│  │  - Risk Assessment Tables                                   │ │
│  │  - Financial Projections                                    │ │
│  │  - LH Score Breakdown                                       │ │
│  │  - Alternative Sites                                        │ │
│  │  - Recommendations                                          │ │
│  │                                                              │ │
│  │  Output Formats:                                            │ │
│  │  - HTML (interactive, web-viewable)                        │ │
│  │  - PDF (printable, archival)                               │ │
│  │  - JSON (API response)                                      │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Return Results │
                    │  + Cache Update │
                    └─────────────────┘
```

---

## 4. Data Models

### 4.1 Analysis Request Schema

```python
class LandAnalysisRequest(BaseModel):
    address: str                    # 주소
    land_area: float                # 대지면적 (㎡)
    unit_type: UnitType             # 유형 (youth, newlywed_1, etc.)
    zone_type: str                  # 용도지역
    land_status: str                # 토지현황
    land_appraisal_price: int       # 토지감정가격 (원)
    consultant: ConsultantInfo      # 담당자 정보
    weights: Optional[CategoryWeights] = None  # 가중치 (선택)
```

### 4.2 Analysis Response Schema

```python
class LandAnalysisResponse(BaseModel):
    success: bool
    data: AnalysisResult
    metadata: ResponseMetadata
    cache_info: CacheInfo         # v7.2 NEW
    api_info: APIInfo             # v7.2 NEW

class AnalysisResult(BaseModel):
    summary: SummaryInfo
    coordinates: Coordinates
    type_demand_score: TypeDemandScore
    poi_analysis: POIAnalysis
    geo_optimizer: GeoOptimizerResult
    lh_score: LHScore
    report_urls: ReportURLs
```

### 4.3 Cache Info Schema (v7.2 NEW)

```python
class CacheInfo(BaseModel):
    backend: str                    # "redis" or "memory"
    coordinates_cached: bool
    poi_cached: bool
    zoning_cached: bool
    total_cache_hits: int
    total_cache_misses: int
    hit_rate: str                   # "85.3%"
```

### 4.4 API Info Schema (v7.2 NEW)

```python
class APIInfo(BaseModel):
    provider_used: str              # "kakao", "naver", "google"
    circuit_state: str              # "closed", "open", "half_open"
    retry_count: int
    total_api_time: float           # seconds
    failover_occurred: bool
```

---

## 5. Deployment Architecture

### 5.1 Production Deployment Diagram

```
                        Internet
                            │
                            ▼
                 ┌──────────────────┐
                 │  Cloudflare CDN  │
                 │  (Optional)      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   Load Balancer  │
                 │   (Optional)     │
                 └────────┬─────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
     ┌────────────────┐      ┌────────────────┐
     │  Server 1      │      │  Server 2      │
     │  (Primary)     │      │  (Secondary)   │
     └────────┬───────┘      └────────┬───────┘
              │                       │
              └───────────┬───────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  Nginx (443)                        │
        │  - SSL Termination                  │
        │  - Reverse Proxy                    │
        │  - Static Files                     │
        │  - Load Balancing                   │
        └─────────────┬───────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────────┐
        │  Gunicorn (8000)                    │
        │  - 4-8 Uvicorn Workers              │
        │  - Process Management               │
        │  - Worker Recycling                 │
        └─────────────┬───────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────────┐
        │  FastAPI Application                │
        │  - Business Logic                   │
        │  - Rate Limiting                    │
        │  - Cache Management                 │
        └─────────────┬───────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐
│  Redis       │ │PostgreSQL│ │  File    │
│  (Cache)     │ │(Planned) │ │  Storage │
│              │ │          │ │          │
│Port 6379     │ │Port 5432 │ │  /data   │
└──────────────┘ └──────────┘ └──────────┘
```

### 5.2 Container Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Docker Host                                 │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  ZeroSite Network (bridge)                                  │ │
│  │                                                              │ │
│  │  ┌─────────────────┐  ┌─────────────────┐                 │ │
│  │  │  nginx          │  │  zerosite-app   │                 │ │
│  │  │  Container      │  │  Container      │                 │ │
│  │  │                 │  │                 │                 │ │
│  │  │  Port: 443,80  ◄───┤  Port: 8000     │                 │ │
│  │  │  Volume:        │  │  Volume:        │                 │ │
│  │  │  - /etc/nginx   │  │  - /app         │                 │ │
│  │  │  - /var/log     │  │  - /var/log     │                 │ │
│  │  └─────────────────┘  └────────┬────────┘                 │ │
│  │                                 │                           │ │
│  │  ┌─────────────────┐  ┌────────▼────────┐                 │ │
│  │  │  redis          │  │  postgres       │                 │ │
│  │  │  Container      │  │  Container      │                 │ │
│  │  │                 │◄─┤  (Planned)      │                 │ │
│  │  │  Port: 6379     │  │  Port: 5432     │                 │ │
│  │  │  Volume:        │  │  Volume:        │                 │ │
│  │  │  - /data        │  │  - /var/lib/pg  │                 │ │
│  │  └─────────────────┘  └─────────────────┘                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Security Architecture

### 6.1 Security Layers

```
Layer 1: Network Security
    ├─ Firewall Rules (UFW/iptables)
    ├─ DDoS Protection (Cloudflare)
    ├─ Rate Limiting (Nginx)
    └─ IP Whitelisting (Optional)

Layer 2: Transport Security
    ├─ TLS 1.3 (Let's Encrypt)
    ├─ HSTS Headers
    ├─ Certificate Pinning
    └─ Secure Ciphers Only

Layer 3: Application Security
    ├─ Input Validation (Pydantic)
    ├─ SQL Injection Prevention
    ├─ XSS Protection
    ├─ CSRF Tokens
    └─ API Key Rotation

Layer 4: Data Security
    ├─ Encryption at Rest (Redis/DB)
    ├─ Encryption in Transit (TLS)
    ├─ Secure API Key Storage (.env)
    └─ Data Anonymization (Logs)

Layer 5: Monitoring & Audit
    ├─ Access Logs
    ├─ Error Tracking (Sentry - Planned)
    ├─ Security Alerts (Slack)
    └─ Audit Trail (Database - Planned)
```

---

## 7. Monitoring & Observability

### 7.1 Monitoring Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    Monitoring Architecture                       │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Application Metrics                                        │ │
│  │  - Request Count                                            │ │
│  │  - Response Time (avg, p95, p99)                           │ │
│  │  - Error Rate                                               │ │
│  │  - Cache Hit Rate                                           │ │
│  │  - API Success Rate per Provider                           │ │
│  │  - Circuit Breaker States                                  │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
│                             │                                    │
│  ┌──────────────────────────▼─────────────────────────────────┐ │
│  │  System Metrics                                             │ │
│  │  - CPU Usage                                                │ │
│  │  - Memory Usage                                             │ │
│  │  - Disk I/O                                                 │ │
│  │  - Network Traffic                                          │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
│                             │                                    │
│  ┌──────────────────────────▼─────────────────────────────────┐ │
│  │  Infrastructure Metrics                                     │ │
│  │  - Redis: Hit Rate, Memory, Connections                    │ │
│  │  - Nginx: Request Rate, Connections                        │ │
│  │  - Gunicorn: Worker Status, Queue Depth                   │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
│                             │                                    │
│                             ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Alerting Channels                                          │ │
│  │                                                              │ │
│  │  ┌───────────┐  ┌───────────┐  ┌──────────────┐           │ │
│  │  │  Slack    │  │  Email    │  │  Sentry      │           │ │
│  │  │  (Current)│  │  (Current)│  │  (Planned)   │           │ │
│  │  └───────────┘  └───────────┘  └──────────────┘           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Scalability & Performance

### 8.1 Horizontal Scaling Strategy

```
Traffic Increase:
    │
    ▼
Add Nginx Load Balancer
    │
    ├─► Server 1 (Nginx + Gunicorn + FastAPI)
    ├─► Server 2 (Nginx + Gunicorn + FastAPI)
    └─► Server N (Nginx + Gunicorn + FastAPI)
            │
            ▼
    Shared Redis Cluster
    (3-node master-replica)
            │
            ▼
    Shared PostgreSQL
    (Master-Replica setup)
```

### 8.2 Vertical Scaling Guidelines

```
Resource Requirements by Load:

Light Load (<100 req/min):
    - CPU: 2 cores
    - RAM: 4 GB
    - Redis: 1 GB
    - Workers: 2-4

Medium Load (100-500 req/min):
    - CPU: 4 cores
    - RAM: 8 GB
    - Redis: 2 GB
    - Workers: 4-8

Heavy Load (500-2000 req/min):
    - CPU: 8 cores
    - RAM: 16 GB
    - Redis: 4 GB
    - Workers: 8-16
```

---

## Appendix A: Glossary

See ZEROSITE_V7.2_TECHNICAL_SPEC.md Appendix C

---

## Appendix B: References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Redis Documentation: https://redis.io/docs/
- Nginx Documentation: https://nginx.org/en/docs/
- Circuit Breaker Pattern: Martin Fowler's Blog
- Rate Limiting Best Practices: OWASP Guidelines

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-12-01  
**Maintained By**: Platform Engineering Team
