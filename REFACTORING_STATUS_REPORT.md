# 🔄 ZEROSITE 6-MODULE REFACTORING - 진행 현황 보고서

**작성일**: 2025-12-17  
**상태**: 🚧 Phase 1-2 완료 (33% 진행)  
**다음 단계**: M2 감정평가 모듈 고정  

---

## 📊 전체 진행률

```
┌─────────────────────────────────────────────┐
│      6-MODULE REFACTORING PROGRESS         │
├─────────────────────────────────────────────┤
│  STEP 1: 코드 스캔 & 분류    ████████████  100%  │
│  STEP 2: Context 정의        ████████████  100%  │
│  STEP 3: M2 모듈 고정        ░░░░░░░░░░░░    0%  │
│  STEP 4: M1,M3-M6 분리       ░░░░░░░░░░░░    0%  │
│  STEP 5: 파이프라인 고정      ░░░░░░░░░░░░    0%  │
│  STEP 6: 보고서 정리         ░░░░░░░░░░░░    0%  │
│  STEP 7: 테스트 생성         ░░░░░░░░░░░░    0%  │
├─────────────────────────────────────────────┤
│  전체 진행률                 ████░░░░░░░░   33%  │
└─────────────────────────────────────────────┘
```

---

## ✅ 완료된 작업 (STEP 1-2)

### STEP 1: 기존 코드 전체 스캔 & 분류 ✅

**완료 일시**: 2025-12-17 01:50

#### 스캔 결과
```
총 Python 파일:     498개
총 코드 라인:       190,910 lines
engines_v9/:        7개 엔진 파일
services/:          150+ 서비스 파일
reports/:           30+ 보고서 생성 파일
```

#### 분류 완료
| 모듈 | 이동 대상 파일 수 | 주요 파일 |
|------|-----------------|----------|
| **M1** (토지정보) | 7개 | gis_engine_v9_0.py, address_resolver_v9_0.py |
| **M2** (감정평가) | 7개 | land_valuation_engine_v9_1.py, backend/services/* |
| **M3** (LH 유형) | 5개 | demand_engine_v9_0.py, lh_evaluation_engine_v9_0.py |
| **M4** (건축 규모) | 6개 | capacity_engine.py, far_engine.py |
| **M5** (사업성) | 7개 | financial_engine_v9_0.py, verified_cost_engine.py |
| **M6** (LH 심사) | 6개 | lh_evaluation_engine_v9_0.py, lh_decision_engine_v11.py |
| **Reports** | 6개 | report_generator_v11_expert.py, lh_report_generator_v7_5_final.py |

**📋 문서 산출물**:
- `REFACTORING_CODE_MAPPING.md` (14KB) - 완전한 매핑표

---

### STEP 2: Context 객체 정의 ✅

**완료 일시**: 2025-12-17 02:10

#### 생성된 Context 파일

| Context | 파일 크기 | 라인 수 | 핵심 기능 |
|---------|----------|---------|----------|
| **M1: CanonicalLandContext** | 4.3KB | 130 lines | 토지정보 FACT |
| **M2: AppraisalContext** 🔒 | 8.3KB | 250 lines | 감정평가 IMMUTABLE |
| **M3: HousingTypeContext** | 6.3KB | 200 lines | LH 유형 선택 |
| **M4: CapacityContext** | 4.2KB | 130 lines | 건축 규모 |
| **M5: FeasibilityContext** | 5.9KB | 180 lines | 사업성 분석 |
| **M6: LHReviewContext** | 6.6KB | 210 lines | LH 심사 예측 |

**총계**: 6개 파일, ~35KB, 1,100+ lines

#### Context 특징

##### 1. M1: CanonicalLandContext
```python
@dataclass(frozen=True)
class CanonicalLandContext:
    parcel_id: str
    address: str
    coordinates: Tuple[float, float]
    area_sqm: float
    zone_type: str
    far: float
    bcr: float
    road_width: float
    terrain_height: str
    # ... (총 20+ 필드)
```

**포함**:
- ✅ 순수 FACT만 (주소, 좌표, 면적, 용도지역)
- ✅ 규제 정보, 도로, 지형

**제외**:
- ❌ land_value (M2로 이동)
- ❌ premium (M2로 이동)
- ❌ housing_type (M3로 이동)

##### 2. M2: AppraisalContext 🔒 CRITICAL
```python
@dataclass(frozen=True)  # ⚠️ frozen=True 필수!
class AppraisalContext:
    land_value: float              # 🔒 절대 수정 불가!
    unit_price_sqm: float
    official_price: float
    premium_rate: float
    transaction_samples: List[TransactionSample]
    confidence_score: float
    confidence_level: str          # LOW/MEDIUM/HIGH
    # ... (총 25+ 필드)
```

**🔒 IMMUTABLE 규칙**:
1. ✅ `frozen=True`로 생성 후 수정 불가
2. ✅ M3-M6에서 `land_value` 재계산 절대 금지
3. ✅ 보고서에서 감정평가 로직 개입 금지
4. ✅ READ-ONLY로만 사용

**포함**:
- 감정평가액 (`land_value`)
- 거래사례 (`transaction_samples`)
- 4-Factor 프리미엄 (Distance/Time/Size/Zone)
- 4-Factor 신뢰도 (Sample/Variance/Distance/Recency)
- 협상 전략 (참고용)

##### 3. M3: HousingTypeContext
```python
@dataclass(frozen=True)
class HousingTypeContext:
    selected_type: str             # youth/newlywed_1/newlywed_2/multi_child/senior
    type_scores: Dict[str, TypeScore]  # 5가지 유형별 점수
    location_score: float          # 입지 점수 (35점)
    poi_analysis: POIAnalysis
    demand_prediction: float
    # ... (총 15+ 필드)
```

**포함**:
- 5가지 LH 유형별 점수
- POI 분석 (지하철, 학교, 병원, 상업시설)
- 수요 예측
- 경쟁 분석

**제외**:
- ❌ land_value (M2 결과만 참조)
- ❌ 세대수 (M4로 이동)

##### 4. M4: CapacityContext
```python
@dataclass(frozen=True)
class CapacityContext:
    far_available: float
    bcr_available: float
    building_specs: BuildingSpecs
    unit_plan: UnitPlan            # 세대 계획
    parking_plan: ParkingPlan
    # ... (총 15+ 필드)
```

**포함**:
- 용적률/건폐율 활용
- 세대수 (최대, 권장)
- 주차 대수
- 층수, 연면적

**제외**:
- ❌ land_value 재계산 (M2 결과 사용)
- ❌ ROI 계산 (M5로 이동)

##### 5. M5: FeasibilityContext
```python
@dataclass(frozen=True)
class FeasibilityContext:
    appraised_value: float         # M2.land_value 참조만!
    lh_purchase_price: float
    cost_breakdown: CostBreakdown
    financial_metrics: FinancialMetrics  # NPV, IRR, ROI
    is_profitable: bool
    # ... (총 20+ 필드)
```

**🔒 필수 규칙**:
```python
# ✅ 올바른 사용
appraised_value = appraisal_ctx.land_value  # READ-ONLY

# ❌ 절대 금지
appraised_value = appraisal_ctx.land_value * 1.2  # ❌
```

**포함**:
- 감정가 참조 (M2 READ-ONLY)
- LH 매입가
- 재무 지표 (NPV, IRR, ROI, Payback)
- 사업성 판단

##### 6. M6: LHReviewContext
```python
@dataclass(frozen=True)
class LHReviewContext:
    score_breakdown: ScoreBreakdown  # 입지35 + 규모20 + 사업성40 + 법규15
    total_score: float               # 110점 만점
    grade: ProjectGrade              # S/A/B/C/D/F
    decision: DecisionType           # GO/NO-GO/CONDITIONAL
    approval_prediction: ApprovalPrediction
    # ... (총 20+ 필드)
```

**포함**:
- LH 110점 체계 점수
- 최종 의사결정 (GO/NO-GO)
- 승인 확률 예측
- SWOT 분석
- 권장사항

**⚠️ 절대 금지**:
- ❌ M1-M5 Context 수정
- ❌ land_value 재계산
- ❌ 점수 조작

---

## 🚧 진행 중 작업 (STEP 3)

### STEP 3: 6-MODULE 디렉토리 구조 생성

**시작일**: 2025-12-17  
**상태**: 🔄 진행 중 (20%)

#### 생성 예정 구조

```
app/
├── core/                          ✅ 생성 완료
│   ├── context/                   ✅ 6개 Context 완료
│   │   ├── __init__.py
│   │   ├── canonical_land.py
│   │   ├── appraisal_context.py   🔒 IMMUTABLE
│   │   ├── housing_type_context.py
│   │   ├── capacity_context.py
│   │   ├── feasibility_context.py
│   │   └── lh_review_context.py
│   │
│   └── pipeline/                  ⏳ 다음 작업
│       └── zer0site_pipeline.py
│
├── modules/                       ⏳ 생성 예정
│   ├── m1_land_info/
│   ├── m2_appraisal/              🔒 가장 중요!
│   ├── m3_lh_demand/
│   ├── m4_capacity/
│   ├── m5_feasibility/
│   └── m6_lh_review/
│
└── reports/                       ⏳ 정리 예정
    ├── generators/
    └── layouts/
```

---

## ⏳ 예정된 작업 (STEP 4-7)

### STEP 4: M2 감정평가 모듈 고정 🔒

**예상 소요 시간**: 2-3시간  
**우선순위**: 🔴 CRITICAL

#### 작업 내용
1. ✅ `land_valuation_engine_v9_1.py` 분석
2. ⏳ `app/modules/m2_appraisal/service.py` 생성
3. ⏳ GenSpark AI 서비스 이동:
   - `backend/services/geocoding.py` → `m2_appraisal/adapters/`
   - `backend/services/transaction_generator.py` → `m2_appraisal/transaction/`
   - `backend/services/price_adjuster.py` → `m2_appraisal/premium/`
   - `backend/services/confidence_calculator.py` → `m2_appraisal/premium/`
4. ⏳ `AppraisalContext` 반환 로직 추가
5. ⏳ 외부 접근 차단 (`service.py`만 export)

#### 핵심 규칙
```python
# m2_appraisal/service.py
def run(land_ctx: CanonicalLandContext) -> AppraisalContext:
    # 기존 로직 그대로 이동 (수정 금지!)
    land_value = _calculate_land_value(...)
    
    # AppraisalContext 생성 및 LOCK
    return AppraisalContext(
        land_value=land_value,
        # ... (frozen=True로 수정 불가)
    )
```

---

### STEP 5: M1, M3-M6 모듈 분리

**예상 소요 시간**: 4-6시간  
**우선순위**: 🟡 HIGH

#### M1: 토지정보 모듈
- [ ] `m1_land_info/service.py` 생성
- [ ] `gis_engine_v9_0.py` → `service.py` 이동
- [ ] Adapters 분리 (kakao, vworld, land_registry, zoning)

#### M3: LH 유형 선택 모듈
- [ ] `m3_lh_demand/service.py` 생성
- [ ] `demand_engine_v9_0.py` 이동
- [ ] POI 점수화 로직 이동

#### M4: 건축 규모 모듈
- [ ] `m4_capacity/service.py` 생성
- [ ] `capacity_engine.py`, `far_engine.py` 이동
- [ ] 세대수 계산 로직 통합

#### M5: 사업성 모듈
- [ ] `m5_feasibility/service.py` 생성
- [ ] `financial_engine_v9_0.py` 이동
- [ ] LH 공사비 연동 (`verified_cost_engine.py`)
- [ ] **M2 결과 참조만** (재계산 금지)

#### M6: LH 심사 모듈
- [ ] `m6_lh_review/service.py` 생성
- [ ] `lh_evaluation_engine_v9_0.py` 이동
- [ ] 110점 체계 계산
- [ ] GO/NO-GO 의사결정

---

### STEP 6: 파이프라인 고정

**예상 소요 시간**: 2-3시간  
**우선순위**: 🟡 HIGH

#### 작업 내용
```python
# app/core/pipeline/zer0site_pipeline.py

def run(parcel_id: str) -> PipelineResult:
    # M1: 토지정보
    land = M1_LandInfo.run(parcel_id)
    
    # M2: 감정평가 (🔒 LOCK)
    appraisal = M2_Appraisal.run(land)
    
    # M3: LH 유형 선택
    housing = M3_LHDemand.run(land)
    
    # M4: 건축 규모
    capacity = M4_Capacity.run(land, housing)
    
    # M5: 사업성 (M2 참조만)
    feasibility = M5_Feasibility.run(appraisal, capacity)
    
    # M6: LH 심사 (최종 판단)
    lh_review = M6_LHReview.run(housing, capacity, feasibility)
    
    return PipelineResult(
        land, appraisal, housing,
        capacity, feasibility, lh_review
    )
```

#### 규칙 강제
- ❌ 역방향 참조 금지
- ❌ M5/M6에서 M2 service 호출 금지
- ✅ Context만 전달

---

### STEP 7: 보고서 코드 정리

**예상 소요 시간**: 3-4시간  
**우선순위**: 🟡 MEDIUM

#### 작업 내용
1. **모든 report 파일에서 계산 함수 제거**
2. **service import 제거**
3. **context 참조만 허용**

#### Before (❌ 금지)
```python
def render_section(report_ctx):
    # 보고서에서 계산 수행 ❌
    land_value = calculate_land_value(...)
    score = calculate_lh_score(...)
    return f"평가액: {land_value}"
```

#### After (✅ 올바름)
```python
def render_section(report_ctx):
    # Context에서 읽기만 ✅
    land_value = report_ctx.appraisal.land_value
    score = report_ctx.lh_review.total_score
    return f"평가액: {land_value}"
```

---

## 🧪 테스트 계획 (STEP 8)

### 필수 테스트 3종

#### 1. 감정평가 회귀 테스트
```python
def test_appraisal_regression():
    """동일 토지 → 동일 land_value"""
    result1 = M2_Appraisal.run(land_ctx)
    result2 = M2_Appraisal.run(land_ctx)
    
    assert result1.land_value == result2.land_value
    # ✅ PASS: 감정평가 결과 일관성
```

#### 2. Pipeline 불변성 테스트
```python
def test_pipeline_immutability():
    """M6 실행 후 M2 값 불변"""
    result = run_pipeline(parcel_id)
    
    original_value = result.appraisal.land_value
    # M6 실행 후 확인
    assert result.appraisal.land_value == original_value
    # ✅ PASS: M2 결과 보호됨
```

#### 3. Report 무계산 테스트
```python
def test_report_no_calculation():
    """보고서 내 연산식 없음"""
    report_files = glob("app/reports/**/*.py")
    
    for file in report_files:
        code = read_file(file)
        assert "calculate_" not in code
        assert "from app.modules" not in code
    # ✅ PASS: 보고서 READ-ONLY
```

---

## 📊 성공 지표

### 정량적 지표

| 지표 | 목표 | 현재 | 상태 |
|------|------|------|------|
| Context 정의 | 6개 | 6개 | ✅ 완료 |
| 모듈 분리 | 6개 | 0개 | ⏳ 대기 |
| 코드 라인 감소 | -50% | 0% | ⏳ 대기 |
| 파일 수 감소 | -50% | 0% | ⏳ 대기 |
| 테스트 통과율 | 100% | 0% | ⏳ 대기 |

### 정성적 지표

- ✅ **감정평가 불변성**: `frozen=True` 적용 완료
- ⏳ **단방향 흐름**: 파이프라인 미구현
- ⏳ **보고서 무계산**: 정리 미완료
- ⏳ **모듈 독립성**: 분리 미완료

---

## 🚨 리스크 & 이슈

### 1. 기존 API 호환성 ⚠️ HIGH
**문제**: 기존 API 엔드포인트가 새 Context 구조와 맞지 않음  
**해결 방안**: Adapter 패턴으로 기존 API 유지

### 2. 데이터 마이그레이션 ⚠️ MEDIUM
**문제**: 기존 응답 형식과 새 Context 구조 차이  
**해결 방안**: `to_dict()` 메서드로 변환

### 3. 테스트 데이터 부족 ⚠️ MEDIUM
**문제**: 회귀 테스트용 기준 데이터 없음  
**해결 방안**: 현재 결과를 기준값으로 저장

---

## 📅 예상 일정

```
Week 1 (현재):
├─ STEP 1-2: Context 정의          ✅ 완료 (2025-12-17)
└─ STEP 3: 디렉토리 구조           🔄 진행 중

Week 2:
├─ STEP 3-4: M2 모듈 고정          ⏳ 예정 (2일)
├─ STEP 5: M1,M3-M6 분리           ⏳ 예정 (3일)
└─ STEP 6: 파이프라인 고정         ⏳ 예정 (2일)

Week 3:
├─ STEP 7: 보고서 정리             ⏳ 예정 (2일)
├─ STEP 8: 테스트 생성             ⏳ 예정 (2일)
└─ STEP 9: 통합 테스트             ⏳ 예정 (1일)

총 예상 소요 시간: 12-15일
```

---

## 🎯 다음 액션 아이템

### 즉시 수행 (우선순위 순)
1. **M2 감정평가 모듈 고정** 🔴 CRITICAL
   - `land_valuation_engine_v9_1.py` → `m2_appraisal/service.py`
   - GenSpark AI 서비스 이동
   - AppraisalContext 반환 로직

2. **M1 토지정보 모듈 구축** 🟡 HIGH
   - `m1_land_info/service.py` 생성
   - Adapters 분리

3. **파이프라인 프로토타입** 🟡 HIGH
   - `zer0site_pipeline.py` 초안
   - M1→M2 연결 테스트

---

## 📚 참고 문서

- ✅ **REFACTORING_CODE_MAPPING.md** - 코드 매핑표
- ✅ **DEVELOPMENT_MASTER_PLAN.md** - 전체 개발 계획
- ⏳ **REFACTORING_STEP_BY_STEP.md** - 단계별 가이드 (작성 예정)
- ⏳ **CONTEXT_SCHEMA_DEFINITION.md** - Context 스키마 (작성 예정)

---

## 💬 코멘트

이번 리팩토링의 핵심은 **"감정평가(M2) 결과의 불변성 보장"**입니다.

`frozen=True`로 `AppraisalContext`를 보호하고, M3-M6와 보고서 코드에서 **절대 재계산하지 못하도록** 강제합니다.

이를 통해:
- ✅ 감정평가 결과가 흔들리지 않음
- ✅ LH 판단이 "결과"로 명확해짐
- ✅ 보고서가 시스템을 망치지 않음
- ✅ 향후 ML / 정책 변경도 모듈 단위로 대응 가능

---

**문서 버전**: 1.0  
**최종 수정일**: 2025-12-17  
**작성자**: ZeroSite Refactoring Team  
**상태**: 🚧 Phase 1-2 완료, Phase 3 진행 중

---

**END OF REPORT**
