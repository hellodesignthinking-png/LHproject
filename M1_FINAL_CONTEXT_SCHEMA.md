# M1 Final Context Schema (분석용 불변 컨텍스트)

**Date:** 2025-12-17  
**Version:** 2.0  
**Purpose:** M1 → M2-M6 파이프라인 간 데이터 계약 명세

---

## 📋 개요

### 설계 철학

1. **불변성 (Immutability)**
   - STEP 8에서 "분석 시작" 버튼 클릭 시 Context가 `frozen=true` 상태로 고정
   - 이후 M1 화면에서 수정해도 분석 결과는 변하지 않음

2. **분석 중심 구조**
   - 입력 UX 기준이 아닌 **분석 모듈 소비 기준**으로 재정렬
   - 각 모듈이 필요한 데이터만 명확히 추출 가능

3. **데이터 신뢰성**
   - 모든 필드에 `source` (API/PDF/MANUAL) 명시
   - `confidence_score` 포함 (PDF OCR의 경우)

---

## 🏗️ M1_FINAL_CONTEXT 구조

### 전체 스키마

```python
{
  "context_id": "uuid",
  "parcel_id": "1168010100100010001",
  "frozen_at": "2025-12-17T15:30:00Z",
  "frozen": true,
  
  "land_info": { ... },           # 토지 기본 정보 (M2, M3, M4, M5, M6 공통)
  "appraisal_inputs": { ... },    # 감정평가 입력 (M2 전용)
  "demand_inputs": { ... },       # 수요 분석 입력 (M3 전용)
  "building_constraints": { ... }, # 건축 제약 (M4 전용)
  "financial_inputs": { ... },    # 재무 입력 (M5 전용)
  "metadata": { ... }             # 메타데이터 (전체 파이프라인)
}
```

---

## 1️⃣ `land_info` (토지 기본 정보)

**사용 모듈:** M2, M3, M4, M5, M6 (전체 공통)

```python
{
  "land_info": {
    # 주소 정보 (STEP 1, 2)
    "address": {
      "road_address": str,        # 필수
      "jibun_address": str,       # 필수
      "sido": str,                # 필수
      "sigungu": str,             # 필수
      "dong": str,                # 필수
      "beopjeong_dong": str,      # 선택
      "source": "API|MANUAL"      # 필수
    },
    
    # 좌표 (STEP 2)
    "coordinates": {
      "lat": float,               # 필수 (6 decimals)
      "lon": float,               # 필수 (6 decimals)
      "source": "API|MANUAL",     # 필수
      "verified": bool            # 사용자 확인 여부
    },
    
    # 지적 정보 (STEP 3)
    "cadastral": {
      "bonbun": str,              # 필수
      "bubun": str,               # 필수
      "jimok": str,               # 필수 (대지, 전, 답, 임야 등)
      "area_sqm": float,          # 필수 (㎡)
      "area_pyeong": float,       # 자동 계산 (sqm / 3.3058)
      "source": "API|PDF|MANUAL", # 필수
      "confidence": float | null  # PDF일 경우 0.0-1.0
    },
    
    # 용도지역·지구 (STEP 4)
    "zoning": {
      "zone_type": str,           # 필수 (제1종, 제2종, 제3종 일반주거지역 등)
      "zone_detail": str | null,  # 선택 (추가 지구명)
      "land_use": str,            # 필수 (주거용, 상업용 등)
      "source": "API|MANUAL"      # 필수
    },
    
    # 도로 정보 (STEP 5)
    "road_access": {
      "road_contact": str,        # 필수 (접도, 각지, 맹지 등)
      "road_width": float,        # 필수 (m)
      "road_type": str,           # 필수 (대로, 중로, 소로 등)
      "nearby_roads": [           # 선택
        {
          "name": str,
          "width": float,
          "distance": float
        }
      ],
      "source": "API|MANUAL"      # 필수
    },
    
    # 지형 정보
    "terrain": {
      "height": str,              # 선택 (평지, 구릉지 등)
      "shape": str,               # 선택 (정형지, 부정형지 등)
      "source": "MANUAL"
    }
  }
}
```

**필수 필드 검증:**
- `address.road_address`, `address.jibun_address`
- `coordinates.lat`, `coordinates.lon`
- `cadastral.area_sqm`, `cadastral.jimok`
- `zoning.zone_type`
- `road_access.road_width`, `road_access.road_type`

---

## 2️⃣ `appraisal_inputs` (감정평가 입력)

**사용 모듈:** M2 감정평가

```python
{
  "appraisal_inputs": {
    # 공시지가 (STEP 6)
    "official_price": {
      "amount": float | null,           # 원/㎡
      "date": str | null,               # YYYYMMDD
      "source": "API|MANUAL"
    },
    
    # 거래사례 (분석용 - M2 입력)
    "transaction_cases_for_appraisal": [  # 최대 5건
      {
        "date": str,                      # YYYYMMDD
        "area": float,                    # ㎡
        "amount": int,                    # 거래금액 (원)
        "distance": float,                # 대상지로부터 거리 (m)
        "address": str,                   # 주소
        "use_in_calculation": bool        # M2에서 사용 여부
      }
    ],
    
    # 프리미엄 요소 (M2에서 보정에 사용)
    "premium_factors": {
      "corner_lot": bool,                 # 각지
      "wide_road": bool,                  # 광로 접면
      "subway_proximity": float | null,   # 지하철역까지 거리 (m)
      "school_district": str | null,      # 학군 정보
      "development_plan": str | null      # 개발 계획 여부
    }
  }
}
```

**M2 처리 로직:**
- `official_price`를 기준값으로 사용
- `transaction_cases_for_appraisal` 중 `use_in_calculation=true`인 것만 비교 분석
- `premium_factors`로 최종 보정

---

## 3️⃣ `demand_inputs` (수요 분석 입력)

**사용 모듈:** M3 수요 분석

```python
{
  "demand_inputs": {
    # 지역 특성
    "region_characteristics": {
      "population_density": str | null,   # 고밀도, 중밀도, 저밀도
      "age_distribution": str | null,     # 청장년층 집중, 고령화 등
      "income_level": str | null,         # 고소득, 중소득, 저소득
      "source": "API|MANUAL"
    },
    
    # LH 타입 선호도 (M3에서 자동 추론 + 사용자 override)
    "preferred_lh_types": [
      "청년",
      "신혼·신생아 I",
      "신혼·신생아 II",
      "다자녀"
    ],
    
    # 경쟁 물건 현황
    "competition": {
      "nearby_lh_count": int | null,      # 반경 1km 내 LH 주택 수
      "nearby_apartments": int | null,    # 반경 500m 내 아파트 단지 수
      "source": "MANUAL"
    }
  }
}
```

---

## 4️⃣ `building_constraints` (건축 제약)

**사용 모듈:** M4 용적 산출

```python
{
  "building_constraints": {
    # 법정 제약 (STEP 4)
    "legal": {
      "far_max": float,           # 필수 (%) - 용적률 상한
      "bcr_max": float,           # 필수 (%) - 건폐율 상한
      "height_limit": float | null, # 선택 (m) - 최고 높이 제한
      "source": "API|MANUAL"
    },
    
    # LH 인센티브 적용 가능 여부
    "lh_incentive": {
      "available": bool,          # M4에서 자동 판정
      "far_bonus": float | null,  # % (예: 20% 추가)
      "reason": str | null        # "주거지역 내 공공임대주택" 등
    },
    
    # 규제 사항 (STEP 4)
    "regulations": [
      "고도지구",
      "경관지구"
    ],
    
    "restrictions": [
      "일조권 제한",
      "사선제한"
    ]
  }
}
```

---

## 5️⃣ `financial_inputs` (재무 입력)

**사용 모듈:** M5 사업성 분석

```python
{
  "financial_inputs": {
    # 건축비 모델 (M5에서 자동 계산 + override 가능)
    "construction_cost_model": {
      "unit_cost_per_sqm": float | null,  # ㎡당 건축비 (원)
      "method": "STANDARD|CUSTOM",        # 표준단가 vs 사용자 입력
      "source": "AUTO|MANUAL"
    },
    
    # 연계 대출 가능 여부
    "linkage": {
      "available": bool,                  # M5에서 자동 판정
      "loan_amount": float | null,        # 대출 가능 금액 (원)
      "interest_rate": float | null       # 금리 (%)
    }
  }
}
```

---

## 6️⃣ `metadata` (메타데이터)

**사용 모듈:** 전체 파이프라인

```python
{
  "metadata": {
    # 데이터 소스 분포
    "data_sources": {
      "api_count": int,         # API로 가져온 필드 수
      "pdf_count": int,         # PDF에서 추출한 필드 수
      "manual_count": int       # 사용자 직접 입력 필드 수
    },
    
    # 신뢰도 점수
    "confidence_score": {
      "overall": float,         # 전체 평균 신뢰도 (0.0-1.0)
      "cadastral": float | null,
      "market_data": float | null
    },
    
    # 생성 정보
    "created_by": str,          # 사용자 ID
    "created_at": str,          # ISO 8601
    "frozen_at": str,           # ISO 8601
    "version": str              # "2.0"
  }
}
```

---

## 🔒 Context Lock (불변성 보장)

### Lock 시점

**STEP 8 Review 화면에서 "분석 시작 (M1 Lock)" 버튼 클릭 시:**

1. 모든 필수 필드 검증
2. 6개 카테고리로 데이터 재정렬
3. `frozen=true` 상태로 Redis 저장
4. `frozen_at` 타임스탬프 기록

### Lock 후 동작

- ✅ M1 STEP 1-8 화면 재진입 가능 (수정 가능)
- ❌ 하지만 M2-M6 파이프라인은 **frozen된 context만 사용**
- ✅ 재분석하려면 새로운 context 생성 필요

### 구현 방법

```python
# Redis에 두 개의 키로 저장
redis.set(f"context:draft:{parcel_id}", draft_context)    # 수정 가능
redis.set(f"context:frozen:{context_id}", frozen_context)  # 불변

# M2-M6는 오직 frozen context만 읽음
frozen_context = redis.get(f"context:frozen:{context_id}")
```

---

## 📊 필수 필드 검증 규칙

### Level 1: 최소 필수 (분석 불가능 방지)

- `land_info.address.road_address`
- `land_info.coordinates.lat`, `lon`
- `land_info.cadastral.area_sqm`
- `land_info.zoning.zone_type`
- `building_constraints.legal.far_max`
- `building_constraints.legal.bcr_max`

### Level 2: 권장 필수 (분석 품질 향상)

- `appraisal_inputs.official_price.amount`
- `appraisal_inputs.transaction_cases_for_appraisal` (최소 1건)
- `land_info.road_access.road_width`

### Level 3: 선택 (보고서 풍부화)

- `demand_inputs.*`
- `financial_inputs.*`

---

## 🔄 M1 STEP → Final Context 매핑

| M1 STEP | 입력 항목 | Final Context 위치 |
|---------|-----------|-------------------|
| STEP 1  | 주소 검색 | `land_info.address` |
| STEP 2  | 좌표 확인 | `land_info.coordinates` |
| STEP 3  | 지적 정보 | `land_info.cadastral` |
| STEP 4  | 용도지역 | `land_info.zoning`, `building_constraints.legal` |
| STEP 5  | 도로 정보 | `land_info.road_access` |
| STEP 6  | 시장 정보 | `appraisal_inputs.official_price`, `transaction_cases_for_appraisal` |
| STEP 7  | 검토     | (데이터 검증만 수행) |
| STEP 8  | 확정     | **Context Freeze** |

---

## 📌 M2-M6 모듈별 사용 필드

### M2 감정평가
- `land_info.*` (전체)
- `appraisal_inputs.*` (전체)
- 출력: `estimated_value`, `premium_rate`

### M3 수요 분석
- `land_info.address`
- `land_info.zoning`
- `demand_inputs.*`
- 출력: `recommended_lh_types[]`

### M4 용적 산출
- `land_info.cadastral`
- `building_constraints.*`
- 출력: `legal_capacity`, `incentive_capacity`, `schematics[]`

### M5 사업성 분석
- M2, M3, M4 출력값
- `financial_inputs.*`
- 출력: `irr`, `npv`, `roi`

### M6 보고서 생성
- `land_info.*` (전체)
- M2-M5 출력값
- 출력: `final_report.pdf`

---

## 🚨 주의사항

### 1. Context ID vs Parcel ID
- **parcel_id**: 토지 고유 식별자 (예: `1168010100100010001`)
- **context_id**: 분석 세션 고유 ID (UUID)
- 같은 토지에 대해 여러 개의 context 생성 가능

### 2. 거래사례 분리
- `transaction_cases_for_appraisal`: M2 계산 입력 (최대 5건)
- `transaction_cases_for_reference`: 보고서 참고용 (무제한)

### 3. Source 추적
- 모든 데이터는 `source` 필드 필수
- PDF의 경우 `confidence` 추가

---

## 📚 참고 문서

- M1 Backend API: `M1_BACKEND_IMPLEMENTATION_COMPLETE.md`
- M1 UX Flow: `M1_STEP_UX_IMPLEMENTATION_PLAN.md`
- M4 Capacity Module: `M4_CAPACITY_MODULE_V2_SPEC.md`

---

**Last Updated:** 2025-12-17  
**Version:** 2.0  
**Status:** API Contract Specification
