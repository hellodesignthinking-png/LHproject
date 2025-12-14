# ZeroSite v40.6 Implementation Progress
## 감정평가 기준축 정합성 복원 & 연동 보강

**Start Date**: 2025-12-14  
**Status**: IN PROGRESS

---

## ✅ Completed Tasks

### v40.6-1: Appraisal Context 구조 확장 ✅ COMPLETE
**Purpose**: Add explanatory texts to prevent report recalculation

**Changes Made**:
- Modified `/app/engines/v30/appraisal_engine.py`
- Added 3 new methods:
  - `_generate_adjustment_logic()` - 조정계수 설명
  - `_generate_transaction_summary()` - 거래사례 요약문
  - `_generate_premium_explanation()` - 프리미엄 설명문
  
**New Context Fields**:
```json
{
  "adjustment_logic": {
    "area_factor": "대상 토지면적... 조정 불필요",
    "road_factor": "중로 접면... 조정계수 1.0",
    "shape_factor": "정방형... 조정계수 1.0",
    "use_factor": "제3종일반주거지역... 조정계수 1.0",
    "time_factor": "거래사례 평균... 시점조정 최소"
  },
  "transaction_summary_text": "대상 토지 인근... 247자",
  "premium_explanation": "대상 토지는 다음과 같은... 313자"
}
```

**Test Result**: ✅ PASS (All 3 fields present)

---

## 🔄 In Progress

### v40.6-2: Report Generators - Appraisal 단일 참조 강제
**Status**: Next  
**Files to Modify**:
- `app/services/reports/lh_submission_generator.py`
- `app/services/reports/template_generators.py`
- `app/services/reports/landowner_brief_generator.py`

**Required Changes**:
- Replace all `context.capacity.land_value` with `context.appraisal.final_value`
- Replace all price calculations with `context.appraisal.value_per_sqm`
- Use `context.appraisal.transactions` only
- Use `context.appraisal.premium` only

---

## ⏳ Pending Tasks

### v40.6-3: LH Review Engine - Appraisal-based Score 추가
**Files**: `app/services/lh_review_engine.py`

**Add New Scoring**:
```python
def _calculate_appraisal_based_score(context_data):
    """
    감정평가 기반 점수 (40% weight)
    - 감정가 대비 LH 매입가 비율: 15%
    - 거래사례 신뢰도 (개수/시점): 15%
    - 프리미엄 합리성: 10%
    """
    pass
```

**Add Response Fields**:
```json
{
  "appraisal_based_score": 85.0,
  "price_stability_flag": "STABLE | WARNING | RISK"
}
```

### v40.6-4: Diagnosis Engine - 외부 API 재조회 차단
**Files**: `app/api/v40/router_v40_2.py`

**Hard Lock**:
```python
def extract_diagnosis_view(appraisal_result, geo_info):
    # ONLY allow inputs from appraisal_result
    # NO external API calls
    # NO market engine calls
    pass
```

### v40.6-5: API Flow Enforcement - Appraisal 선행 강제
**Files**: `app/api/v40/router_v40_2.py`

**Enforce**:
```python
@router_v40_2.post("/run-analysis")
async def run_analysis(request):
    # 1. MUST run appraisal first
    # 2. MUST store context.appraisal
    # 3. THEN run diagnosis/capacity/scenario
    pass
```

### v40.6-6: Report Structure - 감정평가 Page 1 고정
**Files**: All report generators

**Standard Structure**:
```
Page 1: 감정평가 요약 (Final Value, 거래사례, 프리미엄)
Page 2+: 토지진단, 규모검토, 시나리오, LH 심사예측
```

### v40.6-7: 통합 테스트 (7/7 PASS 목표)
**Test File**: `test_v40_6_integrity.py`

**Tests**:
1. ✅ Appraisal Context 구조 확장
2. ⏳ Report Appraisal 단일 참조
3. ⏳ LH Review Appraisal Score
4. ⏳ Diagnosis 외부 API 차단
5. ⏳ API Flow Enforcement
6. ⏳ Report Structure Page 1
7. ⏳ End-to-End Integration

---

## 📊 Overall Progress

**Completed**: 1/8 (12.5%)  
**In Progress**: 1/8 (12.5%)  
**Pending**: 6/8 (75%)

**Estimated Time Remaining**: 2~3 hours

---

## 🎯 Critical Path

For fastest completion, focus on:
1. v40.6-2 (Report Generators) - High impact, affects all reports
2. v40.6-3 (LH Review Score) - User-visible feature
3. v40.6-7 (Integration Tests) - Validates everything

**Note**: v40.6-4, v40.6-5, v40.6-6 are structural improvements that can be deferred if time is limited.

---

**Last Updated**: 2025-12-14  
**Next Action**: Start v40.6-2 (Report Generators Appraisal 단일 참조)
