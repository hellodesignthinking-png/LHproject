# 🏗️ ZeroSite v40.2 Architecture Redesign

**목적**: 감정평가 엔진(v39)을 Single Source of Truth로 승격하여 전체 시스템 데이터 일관성 확보

**작성일**: 2025-12-14  
**상태**: 🔴 CRITICAL - 즉시 실행 필요

---

## 🎯 핵심 문제 2개 (Critical Issues)

### **문제 ①: v39 토지감정평가 엔진의 데이터가 다른 탭으로 전달되지 않음**

**현상**:
- 각 탭(토지진단, 규모검토, 시나리오)이 서로 다른 엔진 또는 Fallback 데이터를 사용
- 용도지역, 공시지가, 거래사례, 토지특성 값이 탭마다 불일치
- 입력한 주소 기준의 정확한 감정평가 데이터가 전혀 반영되지 않음

**근본 원인**:
```python
# 현재 v40 router.py의 문제점

# STEP 1: Zoning은 별도 엔진 사용
zone_result = zoning_engine.get_zone_type(lat, lng, si, gu, dong, jibun)

# STEP 2: Land Price는 별도 엔진 사용
price_result = landprice_engine.get_land_price(...)

# STEP 3: Capacity는 자체 계산
far = get_far_by_zone(zone_type)  # ❌ 감정평가 무시

# STEP 4: Appraisal은 제일 마지막에 실행
appraisal_result = appraisal_engine.run_appraisal(...)  # ❌ 이미 늦음
```

**결과**:
- 감정평가 엔진이 **"Single Source of Truth"** 역할을 못함
- 각 탭이 다른 데이터를 표시하여 사용자 혼란 야기
- 보고서 데이터와 대시보드 데이터 불일치

---

### **문제 ②: 프로세스 순서가 잘못됨**

**현재 ZeroSite 흐름 (잘못됨)**:
```
주소 입력 → 토지진단 → 규모검토 → 시나리오 → 감정평가
```

**정확한 시스템 순서 (업계 표준)**:
```
주소 입력
   ↓
[1] 토지감정평가 (v39) ← 가장 기본 데이터 형성
   ↓
[2] 토지진단 (감정평가 결과 기반)
   ↓
[3] 건축규모검토 (감정평가+Zoning 기반)
   ↓
[4] 시나리오 A/B/C 계산
   ↓
[5] 종합 보고서 생성
```

**왜 이 순서가 맞는가?**
1. **감정평가가 모든 토지 기본 정보를 생성**
   - 용도지역 확정
   - 공시지가 + 시세 조사
   - 거래사례 12건 수집
   - 입지 프리미엄 분석
   - 위험도 평가

2. **다른 모듈은 감정평가 결과를 "참조만" 해야 함**
   - 토지진단: 감정평가의 zoning, restrictions 사용
   - 규모검토: 감정평가의 zoning, FAR, BCR 사용
   - 시나리오: 감정평가의 final_value 사용

3. **LH 실제 업무 흐름도 이 순서**
   - LH는 토지 매입 전 반드시 감정평가 선행
   - 감정평가 결과를 기반으로 사업성 검토

---

## 🧩 해결을 위한 필수 수정 항목 (6개)

### ✅ **1. 감정평가 엔진(v39)을 ZeroSite의 '기준 엔진'으로 강제**

**모든 데이터의 출처는 오직 하나**:

```python
# v40.2 새로운 구조
appraisal_result = appraisal_engine_v39.run(address, land_area)

# 이 값을 모든 탭이 사용
diagnosis_data = {
    "zoning": appraisal_result["zoning"],
    "official_price": appraisal_result["official_price"],
    "transactions": appraisal_result["transactions"]
}

capacity_data = {
    "zoning": appraisal_result["zoning"],
    "far": appraisal_result["zoning"]["final_far"],
    "bcr": appraisal_result["zoning"]["bcr"]
}

scenario_data = {
    "base_value": appraisal_result["final_value"],
    "premium": appraisal_result["premium"]
}
```

| 탭       | 데이터 소스                                                |
|---------|-------------------------------------------------------|
| 토지진단    | appraisal_result.zoning, official_price, transactions |
| 규모검토    | appraisal_result.zoning, premium, appraisal_value     |
| 시나리오    | appraisal_result + Scenario Weights                   |
| 보고서     | appraisal_result (PDF 그대로)                           |

**중요**: 각 탭 내에서 **절대로 새 계산을 하면 안 됨**

---

### ✅ **2. API 프로세스를 1단계 실행 → 4단계 조회로 재설계**

#### **기존 잘못된 구조**:
```python
# 각 탭마다 API 호출
GET /api/v40/diagnosis  # ❌ 자체 계산
GET /api/v40/capacity   # ❌ 자체 계산
GET /api/v40/appraisal  # ❌ 마지막에 실행
```

#### **새로운 정상 구조 (v40.2)**:
```python
# 1) 한 번만 실행
POST /api/v40/run-analysis
    ↓
    # Step 1: Appraisal FIRST
    appraisal_result = appraisal_engine_v39.run()
    
    # Step 2: Use appraisal result for everything
    diagnosis = extract_diagnosis(appraisal_result)
    capacity = extract_capacity(appraisal_result)
    scenario = calculate_scenario(appraisal_result)
    
    # Step 3: Store in context
    store_context(UUID, {
        "appraisal": appraisal_result,
        "diagnosis": diagnosis,
        "capacity": capacity,
        "scenario": scenario
    })
    
    ↓
    
# 2) 각 탭은 조회만
GET /api/v40/context/{UUID}           # 전체 조회
GET /api/v40/context/{UUID}/diagnosis  # 읽기 전용
GET /api/v40/context/{UUID}/capacity   # 읽기 전용
GET /api/v40/context/{UUID}/appraisal  # 읽기 전용
GET /api/v40/context/{UUID}/scenario   # 읽기 전용
```

---

### ✅ **3. 주소 입력 후 API 응답을 검증해야 하는 필드 리스트**

**반드시 응답돼야 하는 필드 (감정평가 기준)**:

```json
{
  "appraisal": {
    "zoning": {
      "final_zone": "제2종일반주거지역",
      "bcr": 60,
      "far": 200
    },
    "official_price": 5200000,
    "market_price": 7800000,
    "transactions": [
      {"price": 78000000, "date": "2024-11", "area": 450},
      // ... 10~15건
    ],
    "premium_summary": {
      "top_factors": [
        {"factor": "교통접근성", "score": 95},
        {"factor": "학군", "score": 88}
      ]
    },
    "final_value": 5237319137,
    "value_per_sqm": 11625569,
    "land_characteristics": {
      "shape": "정방형",
      "slope": "평지",
      "road_access": "중로",
      "orientation": "남향"
    },
    "coordinates": {
      "lat": 37.4713,
      "lng": 126.9294
    }
  }
}
```

**검증 규칙**:
```python
def validate_appraisal_result(result):
    required_fields = [
        "zoning.final_zone",
        "zoning.bcr",
        "zoning.far",
        "official_price",
        "transactions",  # minimum 10건
        "premium_summary",
        "final_value",
        "value_per_sqm",
        "coordinates.lat",
        "coordinates.lng"
    ]
    
    for field in required_fields:
        if not get_nested(result, field):
            raise ValidationError(f"Missing required field: {field}")
    
    if len(result["transactions"]) < 10:
        raise ValidationError("Insufficient transaction data")
```

---

### ✅ **4. 토지진단 모듈에서 절대 제거해야 하는 것**

**현재 토지진단이 하고 있는 잘못된 작업들**:
- ❌ 자체 zoning 계산
- ❌ 자체 공시지가 계산
- ❌ 자체 거래사례 생성
- ❌ 자체 premium 요인 계산
- ❌ 자체 위험도 계산
- ❌ dummy fallback 지역시세

**v40.2 수정**:
```python
# Before (❌ 잘못됨)
def land_diagnosis(address):
    zoning = calculate_zoning(address)        # ❌ 제거
    price = get_official_price(address)       # ❌ 제거
    transactions = fetch_transactions()       # ❌ 제거
    return {
        "zoning": zoning,
        "price": price,
        "transactions": transactions
    }

# After (✅ 올바름)
def land_diagnosis(appraisal_result):
    # 모든 데이터는 appraisal_result에서 추출만
    return {
        "zoning": appraisal_result["zoning"],
        "official_price": appraisal_result["official_price"],
        "transactions": appraisal_result["transactions"],
        "suitability": determine_suitability(appraisal_result),
        "restrictions": appraisal_result["restrictions"]
    }
```

---

### ✅ **5. 규모검토 모듈이 감정평가의 Zoning/FAR을 강제 참조하도록 수정**

**현재 문제**:
```python
# 현재 규모검토는 zoning 엔진이 따로 있음
capacity_engine.zoning = separate_zoning_engine.get_zone()  # ❌ 충돌
```

**v40.2 수정**:
```python
# 규모검토는 감정평가 zoning을 강제로 사용
def capacity_review(appraisal_result, land_area):
    # 감정평가의 zoning 값 사용 (변경 불가)
    zoning = appraisal_result["zoning"]
    far = zoning["final_far"]
    bcr = zoning["bcr"]
    
    # 계산은 이 값을 기준으로만
    max_building_area = land_area * (bcr / 100)
    max_floor_area = land_area * (far / 100)
    max_units = estimate_units(max_floor_area)
    
    return {
        "zoning": zoning,  # 동일한 zoning 반환
        "far": far,
        "bcr": bcr,
        "max_floor_area": max_floor_area,
        "max_units": max_units
    }
```

---

### ✅ **6. 보고서 생성 전 감정평가를 강제 실행**

**보고서 생성 로직 변경**:

```python
# Before (❌ 잘못됨)
def generate_report(context_id):
    context = get_context(context_id)
    # 감정평가 없이도 보고서 생성 가능 ❌
    return create_pdf(context)

# After (✅ 올바름)
def generate_report(context_id):
    context = get_context(context_id)
    
    # 감정평가 없으면 에러
    if "appraisal" not in context or not context["appraisal"]:
        raise ValidationError(
            "감정평가 결과가 없습니다. 먼저 토지분석을 실행하세요."
        )
    
    # 감정평가 데이터 검증
    validate_appraisal_result(context["appraisal"])
    
    # 보고서 생성 (100% 감정평가 데이터 사용)
    return create_pdf(context["appraisal"])
```

---

## 🏗️ v40.2 새로운 아키텍처

### **시스템 흐름도**:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input (Index v40)                    │
│              주소 + 면적 + 물리적 특성 (선택)                      │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
         POST /api/v40/run-analysis
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                 [STEP 1] Appraisal Engine v39                │
│                  (Single Source of Truth)                    │
│  • Geocoding                                                 │
│  • Zoning 확정                                               │
│  • 공시지가 조회                                              │
│  • 거래사례 12건 수집                                          │
│  • 프리미엄 분석                                              │
│  • 최종 감정가 산출                                           │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
         appraisal_result (완전한 토지 정보)
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              [STEP 2] Extract Derived Data                   │
│  • Diagnosis = extract_diagnosis(appraisal_result)          │
│  • Capacity = extract_capacity(appraisal_result)            │
│  • Scenario = calculate_scenario(appraisal_result)          │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                [STEP 3] Store in Context                     │
│  context = {                                                 │
│    "uuid": "...",                                            │
│    "appraisal": appraisal_result,  ← 기준 데이터              │
│    "diagnosis": diagnosis,          ← 추출된 뷰               │
│    "capacity": capacity,            ← 추출된 뷰               │
│    "scenario": scenario             ← 계산된 뷰               │
│  }                                                           │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
                Return UUID to Frontend
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              [STEP 4] Frontend Tabs (Read-Only)              │
│  GET /api/v40/context/{uuid}/diagnosis   ← 조회만            │
│  GET /api/v40/context/{uuid}/capacity    ← 조회만            │
│  GET /api/v40/context/{uuid}/appraisal   ← 조회만            │
│  GET /api/v40/context/{uuid}/scenario    ← 조회만            │
│  GET /api/v40/context/{uuid}/reports     ← PDF 생성          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 데이터 흐름 비교

### **Before (v40.0 - 문제 있음)**:

```
Zoning Engine ──→ Diagnosis Tab ──→ 용도지역: 준주거
                                     
Land Price Engine ──→ Capacity Tab ──→ 공시지가: 5,200,000원

Appraisal Engine ──→ Appraisal Tab ──→ 용도지역: 제2종일반주거
                                        공시지가: 5,400,000원

❌ 결과: 탭마다 다른 데이터 표시
```

### **After (v40.2 - 해결됨)**:

```
Appraisal Engine v39
    ↓
  [appraisal_result]
    • 용도지역: 제2종일반주거지역
    • 공시지가: 5,400,000원/㎡
    • 거래사례: 12건
    ↓
  ├─→ Diagnosis Tab ──→ 동일한 데이터
  ├─→ Capacity Tab ──→ 동일한 데이터
  ├─→ Appraisal Tab ──→ 동일한 데이터
  └─→ Scenario Tab ──→ 동일한 데이터

✅ 결과: 모든 탭이 100% 동일한 데이터 표시
```

---

## 🎓 핵심 원칙 (Design Principles)

### **1. Single Source of Truth**
```
감정평가 엔진(v39) = 모든 데이터의 유일한 출처
다른 엔진 = 감정평가 결과를 "표시"만 하는 뷰
```

### **2. Calculate Once, Display Many**
```
1번 계산 (감정평가) → N개 탭에서 조회
재계산 금지
```

### **3. Appraisal-First Architecture**
```
감정평가 없으면 시스템 작동 불가
보고서, 시나리오 모두 감정평가 필수
```

### **4. Read-Only Tabs**
```
모든 탭 = 읽기 전용
수정 불가, 재계산 불가
```

---

## 📁 수정 필요 파일 목록

| 파일                                     | 수정 내용                                    |
|----------------------------------------|------------------------------------------|
| `app/api/v40/router.py`                | 프로세스 순서 변경: Appraisal First           |
| `app/engines/v30/appraisal_engine.py`  | 승격: Single Source of Truth             |
| `app/api/v40/diagnosis.py` (신규)       | appraisal_result 기반 추출 로직              |
| `app/api/v40/capacity.py` (신규)        | appraisal_result.zoning 강제 사용          |
| `app/api/v40/scenario.py` (신규)        | appraisal_result 기반 시나리오 계산           |
| `app/services/v30/pdf_generator_v39.py`| 변경 없음 (이미 완성됨)                        |
| `public/index_v40_FINAL.html`          | 탭 순서 변경: 감정평가 탭을 최상단으로                |
| `public/js/app_v40.js`                 | API 호출 구조 변경: 1회 실행 + N회 조회          |

---

## ✅ 검증 체크리스트

**v40.2 배포 전 필수 확인 사항**:

- [ ] 같은 주소 입력 시 모든 탭의 용도지역이 100% 동일
- [ ] 같은 주소 입력 시 모든 탭의 공시지가가 100% 동일
- [ ] 감정평가 탭과 보고서 PDF의 거래사례가 100% 동일 (12건)
- [ ] 규모검토의 FAR/BCR이 감정평가 zoning과 100% 일치
- [ ] 시나리오 계산에 사용된 토지가치가 감정평가 final_value와 일치
- [ ] 감정평가 없이 보고서 생성 시도 시 에러 발생 확인
- [ ] 탭 전환 시 재계산이 일어나지 않음 (context 조회만)
- [ ] 10개 이상의 다양한 주소로 테스트 (서울, 부산, 제주 등)

---

## 🚀 다음 단계

1. **Phase 1**: 이 문서 검토 및 승인 (✅ 완료)
2. **Phase 2**: `router.py` 리팩토링 시작
3. **Phase 3**: 진단/규모/시나리오 모듈 재작성
4. **Phase 4**: Frontend 수정 (탭 순서, API 호출)
5. **Phase 5**: 전체 통합 테스트
6. **Phase 6**: v40.2 배포

---

**문서 작성**: GenSpark AI Developer  
**상태**: 🟢 APPROVED FOR IMPLEMENTATION  
**우선순위**: 🔴 CRITICAL  
**예상 작업 시간**: 3-4시간
