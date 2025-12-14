# ZeroSite v42.2 - GitHub Issues
## Appraisal-Centric Pipeline Stabilization

**Created**: 2025-12-14  
**Target Release**: v42.2  
**Priority**: Critical (Structure Fix)

---

## 🧩 Issue #1 — Appraisal 기준 파이프라인 전면 고정

**Title**  
`[v42.2][CORE] Fix Appraisal as Single Source of Truth (SSOT)`

**Labels**  
`bug`, `architecture`, `critical`, `v42.2`

**Assignees**  
@zerosite-dev-team

**Milestone**  
v42.2 - Appraisal-Centric Pipeline Stabilization

---

### Description

현재 ZeroSite 일부 엔진에서 감정평가 외 계산값, fallback 값이 토지가치·공시지가·단가 계산에 개입할 수 있는 구조가 남아 있음.

**기획서 기준**:
- Appraisal 결과는 전체 시스템의 유일한 토지 기준 데이터(Single Source of Truth)
- 모든 엔진은 `context["appraisal"]`만 참조
- 토지가치 관련 계산·추정·fallback 금지

**현재 문제**:
- 일부 엔진에서 토지가치 중복 계산 가능성
- Engine 간 토지가치 불일치 위험
- 보고서 간 수치 미세 차이 발생 가능

---

### Tasks

- [x] **COMPLETED**: `app/core/appraisal_ssot_enforcer.py` 생성 (12.7KB)
  - Appraisal SSOT 강제 적용 엔진
  - Protected Fields 정의
  - Violation 검출 로직
  - Cross-engine validation

- [x] **COMPLETED**: `test_v42_2_ssot_validation.py` 생성 (11.2KB)
  - 7개 테스트 케이스 작성
  - 100% 테스트 통과 확인
  - Validation 자동화

- [ ] **PENDING**: context.appraisal 외 토지가치 계산 로직 제거
  - `land_engine.py` 검토 및 수정
  - `scenario_engine_v241.py` 검토 및 수정
  - `capacity_engine_v241.py` 검토 및 수정

- [ ] **PENDING**: zoning / official_price / unit_price 생성 로직 삭제
  - `zoning_engine_v241.py` 검토
  - `landprice_engine.py` 검토
  - Fallback 로직 제거

- [ ] **PENDING**: 모든 엔진에서 appraisal 결과 Read-Only 참조 강제
  - SSOT Enforcer 통합
  - Write 시도 시 에러 발생 구조 추가

- [ ] **PENDING**: context schema에 appraisal.locked = true 플래그 추가
  - Context validation 로직 추가
  - API 응답에 lock 상태 표시

---

### Acceptance Criteria

- [x] ✅ SSOT Enforcer 구현 완료
- [x] ✅ Validation 테스트 7개 모두 통과
- [ ] ⏳ 동일 context_id 기준 모든 API / Report에서 토지가치 100% 동일
- [ ] ⏳ fallback, random, 추정치 사용 불가
- [ ] ⏳ CI/CD에 SSOT validation 통합

---

### Related Files

**New Files (COMPLETED)**:
- `app/core/appraisal_ssot_enforcer.py` (12.7KB)
- `test_v42_2_ssot_validation.py` (11.2KB)

**Files to Review**:
- `app/engines/land_engine.py`
- `app/engines/scenario_engine_v241.py`
- `app/engines/capacity_engine_v241.py`
- `app/engines/zoning_engine_v241.py`
- `app/engines/v30/landprice_engine.py`

---

### Progress

**Current Status**: 🟡 In Progress (50% Complete)

**Completed**:
- ✅ SSOT Enforcer 구현
- ✅ Validation 테스트 작성
- ✅ 7/7 테스트 통과

**Remaining**:
- ⏳ 기존 엔진 코드 수정
- ⏳ API 통합
- ⏳ 문서화

---

## 🧩 Issue #2 — 토지진단 엔진 감정평가 의존 구조 수정

**Title**  
`[v42.2][ENGINE] Land Diagnosis must depend on Appraisal only`

**Labels**  
`bug`, `refactor`, `high`, `v42.2`

---

### Description

Land Diagnosis Engine에서 용도지역, 공시지가, 시장요약을 자체 계산하거나 fallback 생성 가능성 존재.

**기획서 기준**:
> "토지진단은 감정평가 기반의 적합성 판단 엔진"

**문제**:
- 용도지역을 자체 추정
- 공시지가 fallback 값 사용
- 감정평가 없이 단독 실행 가능

---

### Tasks

- [ ] Land Diagnosis에서 zoning 계산 제거
  - `land_diagnosis_fallback_engine.py` 삭제 또는 비활성화
  
- [ ] official_price 직접 계산 코드 제거
  - Appraisal 결과만 참조하도록 수정
  
- [ ] appraisal 결과만 참조하도록 수정
  ```python
  # ✅ CORRECT
  zoning = context["appraisal"]["zoning"]
  official_price = context["appraisal"]["official_price"]
  market_summary = context["appraisal"]["market_summary"]
  ```
  
- [ ] 진단 결과에 "감정평가 기준 수행" 메타 문구 추가
  ```python
  diagnosis["meta"]["based_on"] = "appraisal"
  diagnosis["meta"]["appraisal_version"] = context["appraisal"]["version"]
  ```

---

### Acceptance Criteria

- [ ] Land Diagnosis 단독 실행 불가
- [ ] appraisal 없는 context에서는 400 에러 반환
- [ ] 모든 토지 데이터는 appraisal에서만 가져옴
- [ ] Fallback 로직 완전 제거

---

### Files to Review

- `app/services/land_diagnosis_fallback_engine.py` (삭제 예정)
- `app/engines/land_engine.py`
- API routers that call land diagnosis

---

## 🧩 Issue #3 — 시나리오 A/B/C 토지가치 불변성 보장

**Title**  
`[v42.2][SCENARIO] Lock Land Value across Scenarios`

**Labels**  
`bug`, `high`, `v42.2`

---

### Description

시나리오 비교 시 토지가치가 변동될 수 있는 구조적 여지 존재.

**기획서 기준**:
> "시나리오는 건축·수익 구조만 비교, 토지가치는 불변"

**문제**:
- Scenario A/B/C 간 land_value 값이 다를 수 있음
- 토지가치 재계산 로직 존재 가능성

---

### Tasks

- [ ] scenario 엔진에서 land_value 수정 금지
  ```python
  # ❌ WRONG
  scenario["A"]["land_value"] = calculate_land_value()
  
  # ✅ CORRECT
  scenario["A"]["land_value"] = context["appraisal"]["total_value"]
  ```

- [ ] scenario 결과에 land_value 필드 제거 또는 readonly
  - 토지가치는 Appraisal에만 존재
  - Scenario는 건축·재무 결과만 포함

- [ ] "토지가치는 감정평가 기준으로 고정됨" 문구 추가
  ```python
  scenario["meta"]["land_value_locked"] = True
  scenario["meta"]["land_value_source"] = "appraisal"
  ```

---

### Acceptance Criteria

- [ ] A/B/C 시나리오 간 land_value, unit_price 동일
- [ ] 비교 테이블에 토지가치 중복 출력 금지
- [ ] 시나리오별로 변하는 값은 건축·재무 항목만

---

### Files to Review

- `app/engines/scenario_engine_v241.py`
- `app/engines/scenario_engine.py`
- Scenario report generators

---

## 🧩 Issue #4 — LH AI Judge Feature Source 명확화

**Title**  
`[v42.2][AI-JUDGE] Fix Feature Mapping Source to Appraisal Context`

**Labels**  
`bug`, `ML-prep`, `high`, `v42.2`

---

### Description

LH 심사예측 Feature 일부가 capacity/scenario 중간값을 직접 참조.  
Explainability 저하 및 기획서 불일치.

**기획서 기준**:
> "LH 심사예측은 감정평가 + 규모 + 정책 조합 모델"

---

### Tasks

- [ ] Feature → Context Mapping 테이블 고정
  ```python
  FEATURE_MAPPING = {
      "land_value": "appraisal.total_value",
      "unit_price": "appraisal.unit_price",
      "zoning": "appraisal.zoning",
      "market_score": "appraisal.market_summary.score",
      "capacity_score": "capacity.score",
      "scenario_score": "scenario.policy_score"
  }
  ```

- [ ] land_value, unit_price = appraisal 기준
  - LH Judge에서 토지가치 재계산 금지

- [ ] Feature 출처 API 응답에 명시
  ```json
  {
    "predicted_score": 82.5,
    "features": {
      "land_value": {
        "value": 1000000000,
        "source": "appraisal.total_value"
      }
    }
  }
  ```

- [ ] fallback feature 제거
  - 모든 Feature는 context에서 직접 추출
  - 추정치·대체값 사용 금지

---

### Acceptance Criteria

- [ ] 동일 context_id → 동일 심사예측 결과
- [ ] Feature 설명 가능 (Explainable)
- [ ] Feature source 추적 가능

---

### Files to Review

- `app/services/lh_review_engine_v42.py`
- `app/services/lh_review_engine_v42_1.py`
- `app/services/lh_review_engine.py`

---

## 🧩 Issue #5 — Report 5종 간 수치 정합성 검증 로직 추가

**Title**  
`[v42.2][REPORT] Enforce Cross-Report Data Consistency`

**Labels**  
`bug`, `quality`, `high`, `v42.2`

---

### Description

5종 보고서 생성기는 완성되었으나 Generator별 참조 경로 상이 가능성 존재.

**보고서 5종**:
1. Landowner Brief (3p)
2. LH Submission (15p)
3. Policy Report
4. Developer Report
5. Professional Report

---

### Tasks

- [ ] BaseReportGenerator 필수 상속
  ```python
  class LandownerReportGenerator(BaseReportGenerator):
      def __init__(self):
          super().__init__()
          self.enforce_ssot = True
  ```

- [ ] appraisal 기준 단일 참조 강제
  ```python
  # ✅ CORRECT
  land_value = self.get_from_appraisal("total_value")
  
  # ❌ WRONG
  land_value = context.get("land_value", fallback)
  ```

- [ ] 보고서 생성 전 수치 검증 로직 추가
  ```python
  def generate_report(self, context):
      # 1. SSOT validation
      if not appraisal_ssot_enforcer.validate_context(context):
          raise ValueError("Context violates SSOT")
      
      # 2. Generate report
      report = self._generate(context)
      
      # 3. Cross-report consistency check
      self._validate_consistency(report, context["appraisal"])
      
      return report
  ```

- [ ] 불일치 시 보고서 생성 차단
  - 500 에러 대신 명확한 validation 에러 반환

---

### Acceptance Criteria

- [ ] 5종 PDF 간 토지가치·단가·공시지가 동일
- [ ] QA 테스트 자동 통과
- [ ] 보고서 생성 시 SSOT validation 자동 실행

---

### Files to Review

- `app/services/landowner_brief_pdf_generator.py`
- `app/services/lh_submission_pdf_generator.py`
- All report generators in `app/services/`

---

## 🧩 Issue #6 — 기획서·문서 문구 현실화

**Title**  
`[v42.2][DOC] Align Planning Docs with Actual Implementation`

**Labels**  
`documentation`, `medium`, `v42.2`

---

### Description

기획서 일부 문구가 "이미 ML 기반", "전국 확장 완료"로 오해 소지.

**문제**:
- v42.x는 Rule-based지만 ML로 표현된 곳 존재
- Multi-Parcel Engine은 미완성이지만 완성으로 표현
- 지자체 확장은 계획 단계인데 실행 중으로 표현

---

### Tasks

- [ ] ML 기반 표현 제거 (v42.x)
  - "ML 기반 LH 심사예측" → "Rule-based LH 심사예측"
  - "AI 모델" → "룰 기반 모델"

- [ ] Rule-based + Calibration 명시
  - v42.0: Rule-based with weight optimization
  - v42.1: Rule-based with data-driven calibration
  - v43.0 (예정): ML-based prediction

- [ ] Multi-Parcel / ML 기능 "향후 고도화"로 분리
  - "현재 개발 중" → "v43+ 계획"
  - "사용 가능" → "향후 제공 예정"

- [ ] 투자/LH 오해 소지 제거
  - 과장 표현 제거
  - 현실적인 수치로 수정

---

### Acceptance Criteria

- [ ] 모든 문서에서 현재 상태 정확히 반영
- [ ] v42.x, v43, v44+ 로드맵 명확히 구분
- [ ] 오해 소지 표현 제거

---

### Files to Review

- `ZEROSITE_PRODUCT_WHITEPAPER_COMPLETE_KR.md`
- `LH_PILOT_PROGRAM_PROPOSAL.md`
- `COMPLETE_DEVELOPMENT_ROADMAP.md`
- All documentation files

---

## 📊 Issue Summary

| Issue # | Title | Priority | Status | Progress |
|---------|-------|----------|--------|----------|
| #1 | Appraisal SSOT | Critical | In Progress | 50% |
| #2 | Land Diagnosis | High | Pending | 0% |
| #3 | Scenario Lock | High | Pending | 0% |
| #4 | LH Judge Features | High | Pending | 0% |
| #5 | Report Consistency | High | Pending | 0% |
| #6 | Doc Alignment | Medium | Pending | 0% |

---

## 🎯 v42.2 Release Criteria

**Must Complete**:
- [x] Issue #1: SSOT Enforcer 구현 (COMPLETED)
- [ ] Issue #1: 기존 엔진 통합 (PENDING)
- [ ] Issue #2: Land Diagnosis 수정 (PENDING)
- [ ] Issue #3: Scenario 수정 (PENDING)
- [ ] Issue #4: LH Judge 수정 (PENDING)
- [ ] Issue #5: Report 검증 추가 (PENDING)

**Should Complete**:
- [ ] Issue #6: 문서 정리 (PENDING)

**Overall Progress**: 🟡 **15% Complete** (1.5/6 issues)

---

## 📅 Timeline

**Week 1 (2025-12-14 ~ 2025-12-20)**:
- [x] Issue #1: SSOT Enforcer 구현 ✅
- [ ] Issue #2: Land Diagnosis 수정 ⏳
- [ ] Issue #3: Scenario 수정 ⏳

**Week 2 (2025-12-21 ~ 2025-12-27)**:
- [ ] Issue #4: LH Judge 수정
- [ ] Issue #5: Report 검증 추가
- [ ] Integration testing

**Week 3 (2025-12-28 ~ 2026-01-03)**:
- [ ] Issue #6: 문서 정리
- [ ] Final QA
- [ ] v42.2 Release

---

**Repository**: https://github.com/hellodesignthinking-png/LHproject  
**Branch**: v24.1_gap_closing → v42.2_ssot_stabilization  
**Milestone**: v42.2 Release

