# 📘 ZeroSite v40.2 Developer Specification (PDRD)

**Product Design & Requirements Document**

**Version**: 40.2  
**Date**: 2025-12-14  
**Status**: 🔴 CRITICAL PRIORITY

---

## 🎯 Section 1 — 목표 (Objective)

### **Primary Goal**
ZeroSite를 "10초 만에 토지의 모든 개발 가능성과 가치를 판단하는 OS"로 완성.  
**모든 데이터의 기준은 감정평가 결과가 1차적으로 결정한다.**

### **Success Criteria**
- [x] 같은 주소 입력 시 모든 탭의 데이터가 100% 일치
- [x] 감정평가 엔진이 모든 분석의 Single Source of Truth
- [x] 보고서와 대시보드 데이터 완전 일치
- [x] 사용자가 "하나의 일관된 스토리"를 경험

---

## 🟥 Section 2 — 문제 정의 (Problem Statement)

| ID  | 문제                        | 원인                 | 해결 방식                             |
|-----|-----------------------------|---------------------|-------------------------------------|
| P-01| 각 탭의 결과 불일치           | 엔진이 서로 다른 계산 사용| Appraisal v39를 글로벌 기준 엔진으로 통합|
| P-02| 보고서 데이터 오류            | fallback 값 사용     | context 저장 기반 데이터 참조 구조 전환  |
| P-03| 규모검토/Zoning 충돌         | zoning 엔진 중복     | 감정평가 zoning 강제 사용             |
| P-04| 프로세스 순서 비논리적        | 감정평가가 마지막에 실행| 감정평가를 첫 번째 단계로 변경          |

---

## 🟦 Section 3 — 기능 요구사항 (Functional Requirements)

### **FR-01: Appraisal-First Architecture**

**요구사항**:
`run_analysis` 실행 시 다음 수행:

```python
# 1. Appraisal Engine FIRST
appraisal_result = appraisal_engine_v39.run(address, land_area)

# 2. 진단·규모·시나리오를 감정평가 기반으로 계산
diagnosis = extract_diagnosis(appraisal_result)
capacity = extract_capacity(appraisal_result)
scenario = calculate_scenario(appraisal_result)

# 3. Context 저장
context = {
    "uuid": generate_uuid(),
    "appraisal": appraisal_result,  # ← 기준 데이터
    "diagnosis": diagnosis,          # ← 추출된 뷰
    "capacity": capacity,            # ← 추출된 뷰
    "scenario": scenario             # ← 계산된 뷰
}
store_context(context)

# 4. UUID 반환
return {"context_id": context["uuid"]}
```

---

### **FR-02: Read-Only Tabs**

**요구사항**:
모든 탭은 계산 금지 → 무조건 context에서 읽기만 가능

```python
# ❌ 잘못됨
GET /api/v40/diagnosis → calculate_diagnosis()  # 재계산

# ✅ 올바름
GET /api/v40/context/{uuid}/diagnosis → return stored_diagnosis  # 조회만
```

---

### **FR-03: Report Generation with Validation**

**요구사항**:
보고서는 UUID 기반으로 감정평가 데이터를 사용. 내부 재계산 금지.

```python
def generate_report(context_id):
    context = get_context(context_id)
    
    # 검증: 감정평가 없으면 에러
    if not context.get("appraisal"):
        raise ValidationError("감정평가 결과 없음")
    
    # 검증: 필수 필드 확인
    validate_required_fields(context["appraisal"])
    
    # PDF 생성 (100% 감정평가 데이터 사용)
    return pdf_generator_v39.generate(context["appraisal"])
```

---

## 🟩 Section 4 — 기술 요구사항 (Technical Requirements)

### **TR-01: Appraisal Engine Output Schema**

감정평가 엔진 v39는 다음 필드를 반드시 반환:

```typescript
interface AppraisalResult {
  // 토지 기본 정보
  zoning: {
    final_zone: string;         // "제2종일반주거지역"
    bcr: number;                // 60
    far: number;                // 200
    height_limit?: number;      // 20 (m)
  };
  
  // 가격 정보
  official_price: number;       // 공시지가 (원/㎡)
  market_price: number;         // 시세 (원/㎡)
  final_value: number;          // 최종 평가액 (원)
  value_per_sqm: number;        // 단위면적당 평가액 (원/㎡)
  
  // 거래사례 (최소 10건)
  transactions: Transaction[];  // minimum 10 cases
  
  // 프리미엄 분석
  premium_summary: {
    top_factors: Array<{
      factor: string;
      score: number;
      justification: string;
    }>;
    overall_premium: number;    // percentage
  };
  
  // 토지 물리적 특성
  land_characteristics: {
    shape: string;              // "정방형", "부정형" 등
    slope: string;              // "평지", "경사" 등
    road_access: string;        // "중로", "소로" 등
    orientation: string;        // "남향", "동향" 등
  };
  
  // 좌표
  coordinates: {
    lat: number;
    lng: number;
  };
  
  // 위험도 평가
  risk_assessment: {
    overall: string;            // "낮음", "보통", "높음"
    factors: RiskFactor[];
  };
  
  // 신뢰도
  confidence_level: string;     // "높음", "보통", "낮음"
  appraisal_date: string;       // "2025-12-14"
}
```

---

### **TR-02: Context Storage Structure**

```typescript
interface AnalysisContext {
  context_id: string;
  timestamp: string;
  
  // 입력 데이터
  input: {
    address: string;
    land_area_sqm: number;
    physical_characteristics: object;
  };
  
  // 기준 데이터 (Single Source of Truth)
  appraisal: AppraisalResult;
  
  // 파생 뷰 (appraisal 기반)
  diagnosis: {
    suitability: string;
    zoning: object;  // = appraisal.zoning
    restrictions: string[];
  };
  
  capacity: {
    max_floor_area: number;
    max_units: number;
    far: number;  // = appraisal.zoning.far
    bcr: number;  // = appraisal.zoning.bcr
  };
  
  scenario: {
    scenarios: ScenarioComparison[];
    recommended: string;
  };
}
```

---

### **TR-03: Data Flow Architecture**

```
Input (address, area)
    ↓
[Appraisal Engine v39]
    ↓
appraisal_result (complete land data)
    ↓
    ├─→ extract_diagnosis(appraisal_result)
    ├─→ extract_capacity(appraisal_result)
    └─→ calculate_scenario(appraisal_result)
    ↓
Store in Context (UUID)
    ↓
Frontend Retrieval (read-only)
```

**핵심 원칙**:
- Appraisal Engine은 단 1번만 실행
- 다른 모듈은 appraisal_result를 참조만 함
- Context 저장 후에는 수정 불가 (immutable)

---

## 🟨 Section 5 — API 명세 (API Specification)

### **API-01: Execute Full Analysis**

```http
POST /api/v40/run-analysis
Content-Type: application/json

{
  "address": "서울특별시 관악구 신림동 1524-8",
  "land_area_sqm": 450.5,
  "land_shape": "정방형",
  "slope": "평지",
  "road_access": "중로",
  "orientation": "남향"
}

Response 200:
{
  "status": "success",
  "context_id": "93061dbb-3a21-4457-9b6f-fe47a678ac2d",
  "timestamp": "2025-12-14 10:00:00",
  "summary": {
    "appraisal_value": 5237319137,
    "suitability": "적합",
    "max_units": 38,
    "recommended_scenario": "B안: 신혼형"
  }
}
```

---

### **API-02: Retrieve Context**

```http
GET /api/v40/context/{context_id}

Response 200:
{
  "context_id": "...",
  "appraisal": { ... },
  "diagnosis": { ... },
  "capacity": { ... },
  "scenario": { ... }
}
```

---

### **API-03: Retrieve Specific Tab**

```http
GET /api/v40/context/{context_id}/diagnosis
GET /api/v40/context/{context_id}/capacity
GET /api/v40/context/{context_id}/appraisal
GET /api/v40/context/{context_id}/scenario

Response 200:
{
  "tab": "diagnosis",
  "data": { ... }  # ← context에서 조회만
}
```

---

### **API-04: Generate Report**

```http
GET /api/v40/reports/{context_id}/appraisal_v39

Response 200:
Content-Type: application/pdf
Content-Disposition: attachment; filename="Appraisal_Report_v39.pdf"

[PDF Binary Data]
```

---

## 🟪 Section 6 — 품질 기준 (Quality Assurance)

### **QA-01: Data Consistency Test**

**테스트**: 같은 주소 입력 시 모든 엔진의 zoning이 동일해야 한다

```python
def test_data_consistency():
    address = "서울특별시 관악구 신림동 1524-8"
    context = run_analysis(address, 450.5)
    
    appraisal_zone = context["appraisal"]["zoning"]["final_zone"]
    diagnosis_zone = context["diagnosis"]["zoning"]["final_zone"]
    capacity_zone = context["capacity"]["zoning"]["final_zone"]
    
    assert appraisal_zone == diagnosis_zone == capacity_zone
    # 모두 "제2종일반주거지역" 이어야 함
```

---

### **QA-02: Official Price Consistency Test**

```python
def test_price_consistency():
    context = run_analysis(address, area)
    
    appraisal_price = context["appraisal"]["official_price"]
    diagnosis_price = context["diagnosis"]["official_price"]
    
    assert appraisal_price == diagnosis_price
    # 공시지가는 반드시 동일
```

---

### **QA-03: Transaction Data Consistency Test**

```python
def test_transaction_consistency():
    context = run_analysis(address, area)
    
    appraisal_txs = context["appraisal"]["transactions"]
    report_txs = generate_report(context["context_id"]).transactions
    
    # PDF에 표시된 거래사례는 appraisal의 것과 동일해야 함
    assert len(appraisal_txs) == len(report_txs) == 12
    assert appraisal_txs[0]["price"] == report_txs[0]["price"]
```

---

### **QA-04: FAR/BCR Consistency Test**

```python
def test_far_bcr_consistency():
    context = run_analysis(address, area)
    
    appraisal_far = context["appraisal"]["zoning"]["far"]
    capacity_far = context["capacity"]["far"]
    
    assert appraisal_far == capacity_far
    # 규모검토의 FAR은 감정평가 FAR과 동일해야 함
```

---

## 🟧 Section 7 — 구현 우선순위 (Implementation Priority)

### **P0 (Critical - 즉시 실행)**
1. ✅ `router.py` 리팩토링: Appraisal-First 구조로 변경
2. ✅ Context 저장 구조 재설계
3. ✅ 탭별 추출 로직 작성 (diagnosis, capacity, scenario)

### **P1 (High - 1일 내)**
4. ✅ 토지진단 모듈 수정: appraisal_result 참조만
5. ✅ 규모검토 모듈 수정: appraisal.zoning 강제 사용
6. ✅ 시나리오 모듈 수정: appraisal.final_value 기반

### **P2 (Medium - 2일 내)**
7. ✅ Frontend 수정: 탭 순서 변경 (감정평가 최상단)
8. ✅ API 호출 로직 변경: 1회 실행 + N회 조회
9. ✅ 보고서 검증 로직 추가

### **P3 (Low - 3일 내)**
10. ✅ 통합 테스트 스위트 작성
11. ✅ 10개 주소 회귀 테스트
12. ✅ 문서화 업데이트

---

## 📝 Section 8 — 체크리스트 (Deployment Checklist)

### **Before Deployment**

- [ ] 같은 주소 입력 시 모든 탭의 용도지역 100% 동일
- [ ] 같은 주소 입력 시 모든 탭의 공시지가 100% 동일
- [ ] 감정평가 탭과 보고서 PDF의 거래사례 100% 동일 (12건)
- [ ] 규모검토의 FAR/BCR이 감정평가 zoning과 100% 일치
- [ ] 시나리오 계산에 사용된 토지가치가 감정평가 final_value와 일치
- [ ] 감정평가 없이 보고서 생성 시도 시 에러 발생 확인
- [ ] 탭 전환 시 재계산이 일어나지 않음 (context 조회만)
- [ ] 10개 이상의 다양한 주소로 테스트 통과

### **Regression Tests**

```python
test_addresses = [
    "서울특별시 관악구 신림동 1524-8",
    "서울특별시 강남구 역삼동 123-45",
    "부산광역시 해운대구 우동 456-78",
    "제주특별자치도 제주시 연동 789-12",
    # ... 10개 이상
]

for address in test_addresses:
    context = run_analysis(address, 450)
    validate_data_consistency(context)
    validate_report_generation(context)
```

---

## 🔐 Section 9 — 보안 & 성능 (Security & Performance)

### **Security**
- Context는 UUID로만 접근 가능
- Context는 1시간 후 자동 삭제 (TTL)
- API Rate Limiting: 100 req/15min

### **Performance**
- Appraisal Engine 실행: ~30초
- Context 저장: <100ms
- Context 조회: <50ms
- PDF 생성: ~2초

---

**문서 작성**: GenSpark AI Developer  
**상태**: 🟢 APPROVED FOR IMPLEMENTATION  
**Target Version**: v40.2  
**Expected Completion**: 2025-12-15
