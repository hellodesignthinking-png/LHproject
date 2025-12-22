# 🗂️ ZEROSITE 6-MODULE REFACTORING - 코드 분류 매핑표

**작성일**: 2025-12-17  
**목적**: 기존 코드를 6-MODULE 구조로 재배치하기 위한 분류 맵  
**상태**: 🔍 분석 완료 → 🚧 이동 대기

---

## 📊 STEP 1: 기존 코드 스캔 결과

### 프로젝트 규모
```
총 Python 파일: 498개
총 코드 라인: 190,910 lines
engines_v9/: 7개 엔진 파일
services/: 150+ 서비스 파일
reports/: 30+ 보고서 생성 파일
```

---

## 🗺️ 기존 코드 → 6-MODULE 매핑표

### ✅ M1: 토지정보 모듈 (FACT)
**책임**: 지번 → 면적, 지목, 용도지역, 토지이용계획 확인

| 기존 파일 | 위치 | 이동 대상 | 비고 |
|---------|------|---------|------|
| `gis_engine_v9_0.py` | `app/engines_v9/` | `app/modules/m1_land_info/service.py` | 주소→좌표 부분만 |
| `normalization_layer_v9_0.py` | `app/services_v9/` | `app/modules/m1_land_info/service.py` | `normalize_site_info()` |
| `address_resolver_v9_0.py` | `app/services_v9/` | `app/modules/m1_land_info/adapters/address_adapter.py` | 주소 파싱 |
| `zoning_auto_mapper_v9_0.py` | `app/services_v9/` | `app/modules/m1_land_info/adapters/zoning_adapter.py` | 용도지역 매핑 |
| `kakao_service.py` | `app/services/` | `app/modules/m1_land_info/adapters/kakao_adapter.py` | 좌표 변환 |
| `land_regulation_service.py` | `app/services/` | `app/modules/m1_land_info/adapters/regulation_adapter.py` | 규제 정보 |
| `mois_service.py` | `app/services/` | `app/modules/m1_land_info/adapters/mois_adapter.py` | 공공데이터 |

**⚠️ 제거해야 할 코드**:
- ❌ `land_value` 계산 코드 (M2로 이동)
- ❌ `premium` 계산 코드 (M2로 이동)
- ❌ `housing_type` 결정 로직 (M3로 이동)

**✅ Context 출력**:
```python
@dataclass(frozen=True)
class CanonicalLandContext:
    parcel_id: str
    address: str
    coordinates: Tuple[float, float]
    area_sqm: float
    zone_type: str
    land_use: str
    far: float
    bcr: float
    road_width: float
    terrain: str
```

---

### 🔒 M2: 토지감정평가 모듈 (FACT, IMMUTABLE)
**책임**: 공시지가, 거래사례, 프리미엄, Confidence Score

| 기존 파일 | 위치 | 이동 대상 | 비고 |
|---------|------|---------|------|
| **`land_valuation_engine_v9_1.py`** | `app/engines_v9/` | `app/modules/m2_appraisal/service.py` | ⭐ 핵심 엔진 |
| `EnhancedGeocodingService` | `backend/services/geocoding.py` | `app/modules/m2_appraisal/adapters/geocoding_adapter.py` | GenSpark AI |
| `EnhancedTransactionGenerator` | `backend/services/transaction_generator.py` | `app/modules/m2_appraisal/transaction/generator.py` | 동적 거래사례 |
| `EnhancedPriceAdjuster` | `backend/services/price_adjuster.py` | `app/modules/m2_appraisal/premium/price_adjuster.py` | 4-Factor 조정 |
| `EnhancedConfidenceCalculator` | `backend/services/confidence_calculator.py` | `app/modules/m2_appraisal/premium/confidence_score.py` | 신뢰도 계산 |
| `real_transaction_api.py` | `app/services/` | `app/modules/m2_appraisal/adapters/molit_adapter.py` | 실거래가 API |
| `land_trade_api.py` | `app/services_v13/` | `app/modules/m2_appraisal/adapters/trade_adapter.py` | 거래 데이터 |

**🔒 IMMUTABLE 규칙**:
```python
@dataclass(frozen=True)  # ⚠️ frozen=True 필수!
class AppraisalContext:
    land_value: float              # 감정평가액 (절대 변경 불가)
    unit_price_sqm: float          # ㎡당 단가
    official_price: float          # 공시지가
    premium_rate: float            # 프리미엄률
    premium_factors: Dict[str, float]  # 도로/지형/입지
    transaction_samples: List[Dict]    # 거래사례
    confidence_score: float        # 신뢰도 (0-1)
    confidence_level: str          # LOW/MEDIUM/HIGH
    valuation_date: str
```

**⚠️ 절대 금지**:
- ❌ M3-M6에서 `land_value` 재계산
- ❌ 보고서에서 `premium_rate` 수정
- ❌ 외부에서 `AppraisalContext` 필드 변경

---

### 🎯 M3: LH 지역·유형 선택 모듈 (INTERPRETATION)
**책임**: LH 유형별 수요 점수, 유형 1개 확정

| 기존 파일 | 위치 | 이동 대상 | 비고 |
|---------|------|---------|------|
| `demand_engine_v9_0.py` | `app/engines_v9/` | `app/modules/m3_lh_demand/service.py` | 수요 예측 |
| `lh_evaluation_engine_v9_0.py` | `app/engines_v9/` | `app/modules/m3_lh_demand/service.py` | 입지 평가 부분만 |
| `type_demand_score_v3.py` | `app/services/` | `app/modules/m3_lh_demand/scoring/demand_scoring.py` | 유형별 점수 |
| `demand_predictor.py` | `app/services_v3/demand_model/` | `app/modules/m3_lh_demand/scoring/predictor.py` | ML 모델 |
| `poi_integration_v8_1.py` | `app/services/` | `app/modules/m3_lh_demand/scoring/poi_scoring.py` | POI 점수화 |

**✅ Context 출력**:
```python
@dataclass(frozen=True)
class HousingTypeContext:
    selected_type: str  # "youth" | "newlywed_1" | "newlywed_2" | "multi_child" | "senior"
    type_scores: Dict[str, float]  # 5가지 유형별 점수
    location_score: float          # 입지 점수 (35점)
    demand_prediction: float       # 수요 예측
    confidence: str                # HIGH/MEDIUM/LOW
```

**⚠️ 제거해야 할 코드**:
- ❌ `land_value` 계산 (M2에서 이미 완료)
- ❌ 세대수 계산 (M4로 이동)
- ❌ 사업성 계산 (M5로 이동)

---

### 🏗️ M4: 건축물 규모 검토 모듈 (INTERPRETATION)
**책임**: FAR/BCR, 세대수, 주차대수, 층수

| 기존 파일 | 위치 | 이동 대상 | 비고 |
|---------|------|---------|------|
| `capacity_engine.py` | `app/engines/` | `app/modules/m4_capacity/service.py` | 용적률 계산 |
| `far_engine.py` | `app/engines/` | `app/modules/m4_capacity/rules/far_rules.py` | FAR 규칙 |
| `building_code_engine.py` | `app/engines/` | `app/modules/m4_capacity/rules/building_code.py` | 건축법 |
| `integration_engine.py` | `app/architect/` | `app/modules/m4_capacity/service.py` | 세대수 계산 |
| `geometry_engine.py` | `app/architect/` | `app/modules/m4_capacity/rules/geometry.py` | 형상 제약 |
| `unit_estimator_v9_0.py` | `app/services_v9/` | `app/modules/m4_capacity/rules/unit_rules.py` | 세대수 추정 |

**✅ Context 출력**:
```python
@dataclass(frozen=True)
class CapacityContext:
    far_available: float           # 사용 가능 용적률
    bcr_available: float           # 사용 가능 건폐율
    max_units: int                 # 최대 세대수
    recommended_units: int         # 권장 세대수
    parking_spaces: int            # 필요 주차 대수
    max_floors: int                # 최고 층수
    total_gfa_sqm: float          # 총 연면적
    building_type: str            # 건축물 유형
```

**⚠️ 제거해야 할 코드**:
- ❌ `land_value` 재계산 (M2 결과 사용)
- ❌ 사업성 ROI 계산 (M5로 이동)
- ❌ LH 매입가 계산 (M5로 이동)

---

### 💰 M5: 사업성 검토 모듈 (JUDGMENT INPUT)
**책임**: 감정가 vs LH 매입가, ROI/IRR, 공사비

| 기존 파일 | 위치 | 이동 대상 | 비고 |
|---------|------|---------|------|
| `financial_engine_v9_0.py` | `app/engines_v9/` | `app/modules/m5_feasibility/service.py` | 재무 분석 |
| `financial_engine.py` | `app/engines/` | `app/modules/m5_feasibility/service.py` | NPV/IRR 계산 |
| `verified_cost_engine.py` | `app/engines/` | `app/modules/m5_feasibility/cost/verified_cost.py` | LH 공사비 |
| `lh_cost_service.py` | `app/services_v9/` | `app/modules/m5_feasibility/cost/lh_cost_link.py` | LH 연동 |
| `policy_transaction_financial_engine_v18.py` | `app/services/` | `app/modules/m5_feasibility/cost/policy_financial.py` | 공공 재무 |
| `private_rental_financial_engine.py` | `app/services/` | `app/modules/m5_feasibility/cost/private_financial.py` | 민간 재무 |
| `dynamic_capex_calculator.py` | `app/services_v13/` | `app/modules/m5_feasibility/cost/capex.py` | 자본 지출 |

**✅ Context 출력**:
```python
@dataclass(frozen=True)
class FeasibilityContext:
    # 감정평가 참조 (M2 결과 READ-ONLY)
    appraised_value: float         # M2.land_value 참조만
    
    # LH 매입가
    lh_purchase_price: float       # LH 매입 예상가
    purchase_premium: float        # 매입 프리미엄률
    
    # 재무 지표
    total_cost: float              # 총 사업비
    construction_cost: float       # 건축비
    land_acquisition_cost: float   # 토지비
    npv_public: float              # NPV (공공 2%)
    npv_market: float              # NPV (시장 5.5%)
    irr_public: float              # IRR (공공)
    irr_market: float              # IRR (시장)
    roi: float                     # ROI
    payback_years: float           # 회수 기간
    
    # 판단
    is_profitable: bool
    profitability_grade: str       # A/B/C/D/F
```

**🔒 필수 규칙**:
```python
# ✅ 올바른 사용 (M2 결과 참조만)
def calculate_roi(feasibility_ctx, appraisal_ctx):
    land_value = appraisal_ctx.land_value  # READ-ONLY
    roi = (land_value - cost) / cost
    return roi

# ❌ 절대 금지 (M2 결과 재계산)
def calculate_roi_WRONG(appraisal_ctx):
    land_value = appraisal_ctx.land_value * 1.2  # ❌ 금지!
    return roi
```

---

### 🎓 M6: LH 심사 예측 모듈 (FINAL JUDGMENT)
**책임**: 정책 가중치, 유형 적합성, GO/NO-GO 판단

| 기존 파일 | 위치 | 이동 대상 | 비고 |
|---------|------|---------|------|
| `lh_evaluation_engine_v9_0.py` | `app/engines_v9/` | `app/modules/m6_lh_review/service.py` | 최종 심사 |
| `lh_decision_engine_v11.py` | `app/` | `app/modules/m6_lh_review/service.py` | 의사결정 |
| `lh_score_mapper_v11.py` | `app/` | `app/modules/m6_lh_review/rules/scoring.py` | 점수 매핑 |
| `policy_engine.py` | `app/engines/` | `app/modules/m6_lh_review/rules/policy_weights.py` | 정책 가중치 |
| `lh_approval_model.py` | `app/services/` | `app/modules/m6_lh_review/rules/approval_model.py` | 승인 예측 |
| `lh_criteria_checker_v85.py` | `app/services/` | `app/modules/m6_lh_review/rules/criteria.py` | 기준 체크 |

**✅ Context 출력**:
```python
@dataclass(frozen=True)
class LHReviewContext:
    # 종합 점수
    total_score: float             # 110점 만점
    grade: str                     # S/A/B/C/D/F
    
    # 세부 점수
    location_score: float          # 입지 (35점)
    scale_score: float             # 규모 (20점)
    feasibility_score: float       # 사업성 (40점)
    compliance_score: float        # 법규 (15점)
    
    # 최종 판단
    decision: str                  # "GO" | "NO-GO" | "CONDITIONAL"
    approval_probability: float    # 승인 확률 (0-1)
    
    # 근거
    strengths: List[str]           # 강점
    weaknesses: List[str]          # 약점
    recommendations: List[str]     # 권장사항
```

**⚠️ 절대 금지**:
- ❌ M1-M5 Context 수정
- ❌ `land_value` 재계산
- ❌ 점수 조작 (계산만 수행)

---

### 📄 REPORTS: 보고서 생성 (READ-ONLY)
**책임**: Context 읽어서 PDF/JSON 생성만

| 기존 파일 | 위치 | 이동 대상 | 비고 |
|---------|------|---------|------|
| `report_generator_v11_expert.py` | `app/` | `app/reports/generators/professional.py` | 전문가급 |
| `lh_report_generator_v7_5_final.py` | `app/services/` | `app/reports/generators/lh_submission.py` | LH 제출용 |
| `pre_report_composer.py` | `app/services/report_composers/` | `app/reports/generators/landowner.py` | 토지주용 |
| `comprehensive_report_composer.py` | `app/services/report_composers/` | `app/reports/generators/comprehensive.py` | 종합 |
| `investor_report_composer.py` | `app/services/report_composers/` | `app/reports/generators/developer.py` | 투자자용 |
| `pdf_generator_weasyprint.py` | `app/services_v9/` | `app/reports/layouts/pdf_exporter.py` | PDF 생성 |

**🚫 보고서 코드 정리 규칙 (강제)**:
```python
# ✅ 올바른 보고서 코드
def render_land_value_section(report_ctx):
    # Context에서 읽기만
    land_value = report_ctx.appraisal.land_value
    unit_price = report_ctx.appraisal.unit_price_sqm
    
    return f"감정평가액: ₩{land_value:,.0f}"

# ❌ 절대 금지 (계산 수행)
def render_land_value_section_WRONG(report_ctx):
    # ❌ 보고서에서 계산 금지!
    land_value = report_ctx.land_info.area_sqm * 1000000
    return f"평가액: {land_value}"
```

**⚠️ 제거해야 할 코드**:
- ❌ 보고서 내 모든 계산 함수
- ❌ `from app.modules.m2_appraisal import *` (service import 금지)
- ❌ `land_value = calculate_value()` 같은 호출

---

## 🚨 위험 코드 패턴 (반드시 제거)

### 1. 감정평가 재계산
```python
# ❌ 절대 금지
def adjust_land_value(appraisal_ctx, factor):
    return appraisal_ctx.land_value * factor  # ❌

# ✅ 올바른 방법
def get_land_value(appraisal_ctx):
    return appraisal_ctx.land_value  # READ-ONLY
```

### 2. Context 필드 수정
```python
# ❌ 절대 금지
appraisal_ctx.land_value = 10000000  # ❌ frozen=True로 방지

# ✅ 올바른 방법
# 새 Context 생성만 가능
new_ctx = AppraisalContext(land_value=10000000, ...)
```

### 3. 순환 참조
```python
# ❌ 절대 금지
# M5에서 M2 service 직접 호출
from app.modules.m2_appraisal.service import AppraisalService
value = AppraisalService.calculate()  # ❌

# ✅ 올바른 방법
# M2 Context만 참조
land_value = appraisal_ctx.land_value  # READ-ONLY
```

### 4. 보고서에서 계산
```python
# ❌ 절대 금지
def render_section(report_ctx):
    # 보고서에서 계산 수행 ❌
    score = calculate_lh_score(...)
    return f"점수: {score}"

# ✅ 올바른 방법
def render_section(report_ctx):
    # Context에서 읽기만 ✅
    score = report_ctx.lh_review.total_score
    return f"점수: {score}"
```

---

## 📋 이동 체크리스트 (순서대로 진행)

### Phase 1: Context 정의 ✅
- [ ] `app/core/context/canonical_land.py` (M1 출력)
- [ ] `app/core/context/appraisal_context.py` (M2 출력, frozen=True)
- [ ] `app/core/context/housing_type_context.py` (M3 출력)
- [ ] `app/core/context/capacity_context.py` (M4 출력)
- [ ] `app/core/context/feasibility_context.py` (M5 출력)
- [ ] `app/core/context/lh_review_context.py` (M6 출력)

### Phase 2: M2 감정평가 고정 🔒
- [ ] `land_valuation_engine_v9_1.py` → `m2_appraisal/service.py` 이동
- [ ] GenSpark AI 서비스 이동 (backend/services/ → m2_appraisal/)
- [ ] AppraisalContext frozen=True 적용
- [ ] 외부 접근 차단 (service.py만 export)

### Phase 3: M1, M3-M6 분리
- [ ] M1: 토지정보 모듈 구축
- [ ] M3: LH 유형 선택 모듈 구축
- [ ] M4: 건축 규모 모듈 구축
- [ ] M5: 사업성 모듈 구축 (M2 결과 참조만)
- [ ] M6: LH 심사 모듈 구축

### Phase 4: 파이프라인 고정
- [ ] `app/core/pipeline/zer0site_pipeline.py` 생성
- [ ] M1→M2→M3→M4→M5→M6 순서 고정
- [ ] 역방향 참조 차단

### Phase 5: 보고서 정리
- [ ] 모든 report 파일에서 계산 함수 제거
- [ ] service import 제거
- [ ] context 참조만 허용

### Phase 6: 테스트 생성
- [ ] 감정평가 회귀 테스트
- [ ] Pipeline 불변성 테스트
- [ ] Report 무계산 테스트

---

## 📊 예상 파일 수 변화

| 구분 | Before | After | 변화 |
|------|--------|-------|------|
| 엔진 파일 | 24개 (분산) | 6개 (모듈화) | -75% |
| 서비스 파일 | 150+ | 30 (adapter만) | -80% |
| 보고서 파일 | 30+ | 10 (generator만) | -67% |
| Context 파일 | 0 | 6 (새로 생성) | +6 |
| 총 파일 수 | 498 | ~250 (예상) | -50% |

---

## 🎯 성공 기준

### 1. 감정평가 불변성 ✅
```bash
# 동일 입력 → 동일 출력
$ python test_appraisal_immutability.py
✅ land_value 불변: ₩12,000,000
✅ M6 실행 후에도 동일: ₩12,000,000
```

### 2. 단방향 흐름 ✅
```bash
# 역방향 참조 없음
$ python test_circular_dependency.py
✅ M5 → M2 참조 없음
✅ M6 → M2 참조 없음
✅ Report → Service 참조 없음
```

### 3. 보고서 무계산 ✅
```bash
# 보고서에서 계산 없음
$ python test_report_read_only.py
✅ 보고서 내 계산 함수: 0개
✅ Context 참조만: 100%
```

---

## 📚 다음 문서

- **REFACTORING_STEP_BY_STEP.md** - 단계별 실행 가이드
- **CONTEXT_SCHEMA_DEFINITION.md** - Context 객체 전체 스키마
- **MIGRATION_GUIDE.md** - 기존 API 호환성 유지 방법

---

**문서 버전**: 1.0  
**최종 수정일**: 2025-12-17  
**작성자**: ZeroSite Refactoring Team  
**상태**: 🔍 분석 완료 → 🚧 Phase 1 시작 예정

---

**END OF MAPPING**
