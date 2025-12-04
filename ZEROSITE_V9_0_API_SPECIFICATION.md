# ZeroSite v9.0 API Specification

## 문서 개요
- **작성일**: 2025-12-04
- **버전**: v9.0 Part 6
- **목적**: REST API 완전 명세서 (개발자용)
- **Base URL**: `https://api.zerosite.kr` (프로덕션) / `http://localhost:8000` (개발)

---

## Part 6: REST API 전체 명세

### 목차
1. [API 개요](#1-api-개요)
2. [인증 및 보안](#2-인증-및-보안)
3. [공통 응답 형식](#3-공통-응답-형식)
4. [엔드포인트 명세](#4-엔드포인트-명세)
5. [에러 코드](#5-에러-코드)
6. [Rate Limiting](#6-rate-limiting)

---

## 1. API 개요

### 1.1 API 버전

| 버전 | 상태 | Base Path | 설명 |
|------|------|-----------|------|
| v9.0 | ✅ Active | `/api/v9` | 최신 버전 (권장) |
| v8.6 | ⚠️ Deprecated | `/api/v8` | 2025-03-01 지원 종료 예정 |
| v7.5 | ❌ Removed | - | 더 이상 지원 안 함 |

### 1.2 주요 엔드포인트

| Method | Endpoint | 설명 | 응답 시간 |
|--------|----------|------|-----------|
| GET | `/health` | 헬스 체크 | < 100ms |
| POST | `/api/v9/analyze-land` | 토지 분석 | < 30s |
| POST | `/api/v9/generate-report` | 보고서 생성 | < 2min |
| GET | `/api/v9/reports/{id}` | 보고서 조회 | < 1s |
| POST | `/api/v9/analyze-multi-parcel` | 다필지 분석 (v5.0) | < 3min |

---

## 2. 인증 및 보안

### 2.1 API Key 인증

```http
POST /api/v9/analyze-land
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### 2.2 API Key 발급

```bash
# 개발용 API Key (무료, Rate Limit: 10 req/hour)
curl -X POST https://api.zerosite.kr/auth/generate-dev-key \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com"}'

# 프로덕션 API Key (유료, Rate Limit: 1000 req/day)
# Contact: sales@zerosite.kr
```

---

## 3. 공통 응답 형식

### 3.1 성공 응답

```json
{
  "success": true,
  "data": { /* 실제 데이터 */ },
  "metadata": {
    "version": "v9.0",
    "timestamp": "2025-12-04T10:00:00Z",
    "request_id": "req_abc123"
  }
}
```

### 3.2 에러 응답

```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "land_area must be between 100 and 10000",
    "details": {
      "field": "land_area",
      "provided_value": 50000
    }
  },
  "metadata": {
    "version": "v9.0",
    "timestamp": "2025-12-04T10:00:00Z",
    "request_id": "req_abc123"
  }
}
```

---

## 4. 엔드포인트 명세

### 4.1 Health Check

#### `GET /health`

**Description**: 시스템 상태 확인

**Request**: None

**Response**:
```json
{
  "status": "healthy",
  "version": "v9.0",
  "timestamp": "2025-12-04T10:00:00Z",
  "services": {
    "kakao_api": "configured",
    "mois_api": "configured",
    "openai_api": "configured",
    "database": "connected"
  },
  "uptime_seconds": 86400
}
```

---

### 4.2 토지 분석 API

#### `POST /api/v9/analyze-land`

**Description**: 단일 필지 토지 분석 수행

**Request Headers**:
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Request Body**:
```json
{
  "address": "서울시 마포구 월드컵북로 120",
  "land_area": 660.0,
  "land_appraisal_price": 5000000,
  "zone_type": "제3종일반주거지역",
  "unit_type": "든든전세",
  "latitude": 37.5665,
  "longitude": 126.9780,
  "options": {
    "include_visualizations": true,
    "detailed_risk_analysis": true
  }
}
```

**Request Parameters**:

| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|------|------|------|
| `address` | string | ✅ | 도로명 주소 | "서울시 마포구 월드컵북로 120" |
| `land_area` | float | ✅ | 대지 면적 (m²) | 660.0 |
| `land_appraisal_price` | float | ✅ | 감정평가액 (원/m²) | 5000000 |
| `zone_type` | string | ✅ | 용도지역 | "제3종일반주거지역" |
| `unit_type` | string | ✅ | 주택 유형 | "든든전세" |
| `latitude` | float | ❌ | 위도 (자동 계산 가능) | 37.5665 |
| `longitude` | float | ❌ | 경도 (자동 계산 가능) | 126.9780 |
| `options` | object | ❌ | 추가 옵션 | {...} |

**Valid `zone_type` Values**:
- `제1종일반주거지역`
- `제2종일반주거지역`
- `제3종일반주거지역`
- `준주거지역`

**Valid `unit_type` Values**:
- `든든전세`
- `역세권청년주택`
- `통합공공임대`
- `행복주택`
- `장기전세`
- `영구임대`
- `국민임대`

**Response** (Success 200):
```json
{
  "success": true,
  "data": {
    "analysis_id": "anlz_abc123def456",
    "version": "v9.0",
    "timestamp": "2025-12-04T10:30:00Z",
    
    "site_info": {
      "address": "서울시 마포구 월드컵북로 120",
      "land_area": 660.0,
      "zone_type": "제3종일반주거지역",
      "land_appraisal_price": 5000000,
      "total_land_price": 3300000000,
      "building_coverage_ratio": 50.0,
      "floor_area_ratio": 250.0,
      "height_limit": 35.0,
      "latitude": 37.5665,
      "longitude": 126.9780
    },
    
    "gis_result": {
      "elementary_schools": [
        {
          "category": "elementary_school",
          "name": "서울초등학교",
          "distance_m": 450.0,
          "distance_display": "450m",
          "walk_time_min": 6,
          "drive_time_min": 2,
          "accessibility_score": 9.2,
          "interpretation": "매우 우수"
        }
      ],
      "subway_stations": [
        {
          "category": "subway_station",
          "name": "월드컵경기장역 (6호선)",
          "distance_m": 1200.0,
          "distance_display": "1.2km",
          "walk_time_min": 15,
          "drive_time_min": 4,
          "accessibility_score": 8.5,
          "interpretation": "우수"
        }
      ],
      "overall_accessibility_score": 85.3,
      "accessibility_grade": "A"
    },
    
    "financial_result": {
      "total_land_price": 3300000000,
      "construction_cost_per_sqm": 2500000,
      "total_construction_cost": 10594947381,
      "total_capex": 13894947381,
      "analysis_mode": "STANDARD",
      "lh_purchase_price": null,
      "lh_purchase_price_per_sqm": null,
      "verified_cost": null,
      "annual_noi": 250000000,
      "cap_rate": 1.8,
      "roi_10yr": -16.55,
      "irr_10yr": -2.1,
      "unit_count": 33,
      "unit_type_distribution": {
        "든든전세": 33
      },
      "financial_grade": "D",
      "breakeven_year": 12
    },
    
    "lh_scores": {
      "location_score": 28.5,
      "scale_score": 10.0,
      "business_score": 18.4,
      "regulation_score": 12.0,
      "total_score": 68.9,
      "grade": "C"
    },
    
    "risk_assessment": {
      "total_items": 25,
      "pass_count": 18,
      "warning_count": 5,
      "fail_count": 2,
      "critical_risks": [
        {
          "id": "FIN-003",
          "category": "FINANCIAL",
          "name": "낮은 수익성 (ROI < 0%)",
          "severity": "HIGH",
          "status": "FAIL",
          "description": "10년 ROI가 -16.55%로 손실 예상",
          "mitigation": "공사비 절감 또는 임대료 인상 필요"
        }
      ],
      "all_risks": [ /* 25개 항목 */ ],
      "overall_risk_level": "MEDIUM"
    },
    
    "demand_result": {
      "population_total": 125000,
      "household_count": 52000,
      "target_households": 8500,
      "demand_score": 72.5,
      "demand_grade": "B",
      "recommended_unit_type": "든든전세"
    },
    
    "final_recommendation": {
      "decision": "REVISE",
      "confidence_level": 75.0,
      "key_strengths": [
        "우수한 교통 접근성 (지하철 1.2km)",
        "양호한 교육 환경 (초등학교 450m)",
        "적정 세대수 (33세대)"
      ],
      "key_weaknesses": [
        "낮은 수익성 (ROI -16.55%)",
        "긴 손익분기년도 (12년)",
        "Cap Rate 1.8% (목표 3.0% 미달)"
      ],
      "action_items": [
        "공사비 10% 절감 방안 검토",
        "임대료 5% 인상 가능성 분석",
        "세대수 증가 가능성 재검토 (용적률 활용)"
      ],
      "executive_summary": "본 사업은 입지 및 규모는 양호하나, 재무적 타당성이 부족합니다. 공사비 절감 및 임대료 조정을 통해 수익성 개선 후 재검토를 권장합니다."
    },
    
    "visualizations": {
      "capex_breakdown": "data:image/png;base64,iVBORw0KG...",
      "cash_flow_10yr": "data:image/png;base64,iVBORw0KG...",
      "sensitivity_analysis": "data:image/png;base64,iVBORw0KG...",
      "lh_radar_chart": "data:image/png;base64,iVBORw0KG...",
      "poi_map": "data:image/png;base64,iVBORw0KG..."
    }
  },
  "metadata": {
    "version": "v9.0",
    "timestamp": "2025-12-04T10:30:15Z",
    "request_id": "req_abc123",
    "processing_time_seconds": 28.5
  }
}
```

**Response** (Error 400 - Invalid Input):
```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "land_area must be between 100 and 10000 m²",
    "details": {
      "field": "land_area",
      "provided_value": 50000,
      "min_allowed": 100,
      "max_allowed": 10000
    }
  }
}
```

**Response** (Error 500 - Internal Error):
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Failed to fetch POI data from Kakao API",
    "details": {
      "service": "GIS Engine",
      "cause": "API timeout"
    }
  }
}
```

---

### 4.3 보고서 생성 API

#### `POST /api/v9/generate-report`

**Description**: 분석 결과 기반 60+ 페이지 전문 보고서 생성

**Request Headers**:
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Request Body**:
```json
{
  "analysis_id": "anlz_abc123def456",
  "data": { /* StandardAnalysisOutput from /analyze-land */ },
  "tone": "professional",
  "options": {
    "include_appendix": true,
    "language": "ko",
    "format": "pdf"
  }
}
```

**Request Parameters**:

| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|------|------|------|
| `analysis_id` | string | ✅ | 분석 ID | "anlz_abc123def456" |
| `data` | object | ✅ | StandardAnalysisOutput | {...} |
| `tone` | string | ❌ | 보고서 톤 | "professional" (기본값) |
| `options` | object | ❌ | 추가 옵션 | {...} |

**Valid `tone` Values**:
- `professional`: 전문적이고 객관적 (기본값)
- `academic`: 학술적이고 연구 중심
- `lh_submission`: LH 제출용 정부 문서 스타일

**Response** (Success 200):
```json
{
  "success": true,
  "data": {
    "analysis_id": "anlz_abc123def456",
    "report_id": "rpt_xyz789ghi012",
    "pdf_url": "https://api.zerosite.kr/api/v9/reports/rpt_xyz789ghi012.pdf",
    "html": "<html>...</html>",
    "metadata": {
      "version": "v9.0",
      "pages": 62,
      "size_kb": 5248,
      "generation_time_seconds": 118,
      "tone": "professional",
      "chapters": [
        "Executive Summary",
        "Site Overview",
        "GIS Accessibility",
        "Location Metrics",
        "Demand Analysis",
        "Regulation Review",
        "Construction Feasibility",
        "Financial Analysis",
        "LH Evaluation",
        "Risk Assessment",
        "Final Decision",
        "Appendix"
      ]
    }
  },
  "metadata": {
    "version": "v9.0",
    "timestamp": "2025-12-04T10:35:00Z",
    "request_id": "req_def456"
  }
}
```

---

### 4.4 보고서 조회 API

#### `GET /api/v9/reports/{report_id}`

**Description**: 생성된 보고서 조회

**Request Headers**:
```
Authorization: Bearer YOUR_API_KEY
```

**URL Parameters**:
- `report_id`: 보고서 ID (예: `rpt_xyz789ghi012`)

**Query Parameters**:
- `format`: `pdf` (기본값) 또는 `html`

**Response** (Success 200):
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="report_rpt_xyz789ghi012.pdf"

[PDF Binary Data]
```

---

### 4.5 다필지 분석 API (v5.0)

#### `POST /api/v9/analyze-multi-parcel`

**Description**: 최대 10개 필지 동시 분석 및 비교

**Request Body**:
```json
{
  "parcels": [
    {
      "address": "서울시 마포구 월드컵북로 120",
      "land_area": 660.0,
      "land_appraisal_price": 5000000
    },
    {
      "address": "서울시 마포구 성산로 500",
      "land_area": 800.0,
      "land_appraisal_price": 4500000
    }
  ],
  "zone_type": "제3종일반주거지역",
  "unit_type": "든든전세",
  "options": {
    "recommend_top_n": 3
  }
}
```

**Request Parameters**:

| 필드 | 타입 | 필수 | 설명 | 제약 |
|------|------|------|------|------|
| `parcels` | array | ✅ | 필지 목록 | 1-10개 |
| `zone_type` | string | ✅ | 용도지역 (공통) | - |
| `unit_type` | string | ✅ | 주택 유형 (공통) | - |
| `options` | object | ❌ | 추가 옵션 | - |

**Response** (Success 200):
```json
{
  "success": true,
  "data": {
    "multi_analysis_id": "multi_abc123",
    "total_parcels": 2,
    "parcels_analyzed": [
      {
        "parcel_id": "parcel_001",
        "address": "서울시 마포구 월드컵북로 120",
        "analysis_result": { /* StandardAnalysisOutput */ },
        "rank": 1,
        "overall_score": 85.3
      },
      {
        "parcel_id": "parcel_002",
        "address": "서울시 마포구 성산로 500",
        "analysis_result": { /* StandardAnalysisOutput */ },
        "rank": 2,
        "overall_score": 78.1
      }
    ],
    "recommendations": [
      {
        "parcel_id": "parcel_001",
        "reason": "최고 접근성 점수 (A등급), 재무 타당성 양호"
      },
      {
        "parcel_id": "parcel_002",
        "reason": "낮은 토지비, 개발 잠재력 우수"
      }
    ],
    "comparative_analysis": {
      "average_lh_score": 81.7,
      "average_roi": -8.3,
      "best_accessibility": "parcel_001",
      "best_financial": "parcel_002"
    }
  },
  "metadata": {
    "version": "v9.0",
    "timestamp": "2025-12-04T10:40:00Z",
    "processing_time_seconds": 165
  }
}
```

---

## 5. 에러 코드

### 5.1 클라이언트 에러 (4xx)

| 코드 | HTTP Status | 메시지 | 설명 |
|------|-------------|--------|------|
| `INVALID_INPUT` | 400 | Invalid input parameters | 입력 파라미터 오류 |
| `MISSING_FIELD` | 400 | Required field is missing | 필수 필드 누락 |
| `INVALID_ZONE_TYPE` | 400 | Invalid zone_type value | 잘못된 용도지역 |
| `INVALID_UNIT_TYPE` | 400 | Invalid unit_type value | 잘못된 주택 유형 |
| `LAND_AREA_OUT_OF_RANGE` | 400 | land_area must be 100-10000 m² | 대지 면적 범위 초과 |
| `UNAUTHORIZED` | 401 | Invalid or missing API key | API 키 오류 |
| `FORBIDDEN` | 403 | API key quota exceeded | API 호출 한도 초과 |
| `NOT_FOUND` | 404 | Report not found | 보고서 없음 |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Rate Limit 초과 |

### 5.2 서버 에러 (5xx)

| 코드 | HTTP Status | 메시지 | 설명 |
|------|-------------|--------|------|
| `INTERNAL_ERROR` | 500 | Internal server error | 내부 서버 오류 |
| `GIS_API_ERROR` | 500 | Failed to fetch GIS data | GIS API 오류 |
| `FINANCIAL_CALCULATION_ERROR` | 500 | Financial calculation failed | 재무 계산 오류 |
| `PDF_GENERATION_ERROR` | 500 | PDF generation failed | PDF 생성 실패 |
| `AI_WRITER_ERROR` | 500 | AI text generation failed | AI Writer 오류 |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable | 서비스 일시 중단 |

---

## 6. Rate Limiting

### 6.1 Rate Limit 정책

| 계정 유형 | Rate Limit | 버스트 허용 | 가격 |
|----------|-----------|------------|------|
| **무료 (Dev)** | 10 req/hour | 3 req/min | 무료 |
| **Basic** | 100 req/day | 10 req/min | $50/month |
| **Pro** | 1000 req/day | 30 req/min | $200/month |
| **Enterprise** | 무제한 | 무제한 | 협의 |

### 6.2 Rate Limit 헤더

**Response Headers**:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1701684000
```

**Rate Limit 초과 시**:
```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 45 minutes.",
    "details": {
      "limit": 10,
      "remaining": 0,
      "reset_at": "2025-12-04T11:00:00Z"
    }
  }
}
```

---

## 7. 예제 코드

### 7.1 Python (requests)

```python
import requests
import json

API_KEY = "your_api_key_here"
BASE_URL = "https://api.zerosite.kr"

def analyze_land(address, land_area, land_appraisal_price, zone_type, unit_type):
    """토지 분석 API 호출"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "address": address,
        "land_area": land_area,
        "land_appraisal_price": land_appraisal_price,
        "zone_type": zone_type,
        "unit_type": unit_type
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v9/analyze-land",
        headers=headers,
        json=payload,
        timeout=60
    )
    
    if response.status_code == 200:
        return response.json()["data"]
    else:
        raise Exception(f"API Error: {response.json()}")

# 사용 예시
result = analyze_land(
    address="서울시 마포구 월드컵북로 120",
    land_area=660.0,
    land_appraisal_price=5000000,
    zone_type="제3종일반주거지역",
    unit_type="든든전세"
)

print(f"분석 ID: {result['analysis_id']}")
print(f"LH 점수: {result['lh_scores']['total_score']}/110")
print(f"최종 결정: {result['final_recommendation']['decision']}")
```

### 7.2 JavaScript (axios)

```javascript
const axios = require('axios');

const API_KEY = 'your_api_key_here';
const BASE_URL = 'https://api.zerosite.kr';

async function analyzeLand(address, landArea, landAppraisalPrice, zoneType, unitType) {
  try {
    const response = await axios.post(
      `${BASE_URL}/api/v9/analyze-land`,
      {
        address,
        land_area: landArea,
        land_appraisal_price: landAppraisalPrice,
        zone_type: zoneType,
        unit_type: unitType
      },
      {
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
          'Content-Type': 'application/json'
        },
        timeout: 60000
      }
    );
    
    return response.data.data;
  } catch (error) {
    console.error('API Error:', error.response?.data || error.message);
    throw error;
  }
}

// 사용 예시
analyzeLand(
  '서울시 마포구 월드컵북로 120',
  660.0,
  5000000,
  '제3종일반주거지역',
  '든든전세'
).then(result => {
  console.log(`분석 ID: ${result.analysis_id}`);
  console.log(`LH 점수: ${result.lh_scores.total_score}/110`);
  console.log(`최종 결정: ${result.final_recommendation.decision}`);
});
```

### 7.3 cURL

```bash
curl -X POST https://api.zerosite.kr/api/v9/analyze-land \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울시 마포구 월드컵북로 120",
    "land_area": 660.0,
    "land_appraisal_price": 5000000,
    "zone_type": "제3종일반주거지역",
    "unit_type": "든든전세"
  }'
```

---

## 8. 변경 이력 (Changelog)

### v9.0 (2025-12-04) - Latest
- ✅ 새로운 표준 데이터 스키마 (`StandardAnalysisOutput`)
- ✅ GIS Engine v9.0 (POI 거리 무한대 문제 해결)
- ✅ Financial Engine v9.0 (공사비 연동제 + IRR + ROI)
- ✅ LH Evaluation v9.0 (110점 체계 + 25개 리스크)
- ✅ AI Report Writer (12-Chapter 자동 생성)
- ✅ PDF Renderer v9.0 (KeyError ZERO)
- ✅ Normalization Layer (Engine 레벨 데이터 정규화)
- ✅ Multi-parcel Analysis v5.0

### v8.6 (2024-11-15) - Deprecated
- ⚠️ 2025-03-01 지원 종료 예정
- Data Mapper v8.6 (사후 변환 방식)
- v7.5 Template + v8.5 Engine (하이브리드)

### v7.5 (2024-06-01) - Removed
- ❌ 더 이상 지원 안 함

---

## 9. 지원 및 문의

### 9.1 문의 채널
- **기술 지원**: support@zerosite.kr
- **영업 문의**: sales@zerosite.kr
- **문서**: https://docs.zerosite.kr
- **GitHub**: https://github.com/zerosite/api

### 9.2 SLA (Service Level Agreement)
- **Uptime**: 99.9%
- **응답 시간**: < 30초 (분석), < 2분 (보고서)
- **지원 시간**: 09:00-18:00 (KST, 평일)
- **긴급 지원**: 24/7 (Enterprise 플랜)

---

**문서 종료**

---

## ZeroSite v9.0 전체 문서 완성 🎉

총 6개 Part 완성:
1. ✅ **Part 1**: ZEROSITE_V9_0_COMPLETE_ARCHITECTURE.md (35KB)
2. ✅ **Part 2**: ZEROSITE_V9_0_ENGINES_SPECIFICATION.md (34KB)
3. ✅ **Part 3**: ZEROSITE_V9_0_AI_REPORT_WRITER.md (32KB)
4. ✅ **Part 4**: ZEROSITE_V9_0_PDF_RENDERER.md (28KB)
5. ✅ **Part 5**: ZEROSITE_V9_0_IMPLEMENTATION_GUIDE.md (24KB)
6. ✅ **Part 6**: ZEROSITE_V9_0_API_SPECIFICATION.md (현재)

**총 문서 크기**: ~180KB (개발자 직접 구현 가능 수준)
