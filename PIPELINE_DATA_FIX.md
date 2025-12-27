# 🚨 CRITICAL FIX: Pipeline Data Not Reaching Reports

**Date**: 2025-12-27  
**Issue**: Pipeline runs but PDF/HTML/Reports show empty data  
**Root Cause**: Pipeline and Report systems using different storage  
**Fix**: Connect pipeline results to context_storage

---

## 🐛 Problem Description

### User Report
```
"계속 이야기하는것처럼 ZeroSite v4.0 - 토지 분석 파이프라인
✓ M1 입력 → ✓ M1 확정 → ✓ M2-M6 분석 → 결과 검토 → 보고서 ✅
분석 완료! 실행 시간: 0.0초

의 pdf, html, 그리고 최종6종 보고서에 대한 세부 내용들이 안들어오고 있어"
```

### Symptoms
- ✅ Pipeline executes successfully
- ✅ Shows "분석 완료!" message
- ❌ PDFs show empty/placeholder data
- ❌ HTML reports show empty/placeholder data
- ❌ Final 6 reports show empty/placeholder data

---

## 🔍 Root Cause Analysis

### Architecture Problem

**Two Disconnected Storage Systems**:

1. **Pipeline Storage** (`app/api/endpoints/pipeline_reports_v4.py`)
   ```python
   # Line 405: Pipeline saves to in-memory dict
   results_cache[request.parcel_id] = result
   ```
   - Storage: `results_cache` (in-memory dictionary)
   - Scope: Only within pipeline_reports_v4.py
   - Lifetime: Process lifetime (lost on restart)

2. **Report Storage** (`app/routers/pdf_download_standardized.py`)
   ```python
   # Line 913: Reports read from context_storage
   frozen_context = context_storage.get_frozen_context(context_id)
   ```
   - Storage: `context_storage` (Redis + Database)
   - Scope: Global (shared across all services)
   - Lifetime: 24 hours (configurable TTL)

### The Disconnect

```
┌─────────────────────────────────────────────────────────────┐
│  BEFORE (BROKEN)                                            │
└─────────────────────────────────────────────────────────────┘

Pipeline Execution:
  User → POST /api/v4/pipeline/analyze
    ↓
  Pipeline runs M1→M2→M3→M4→M5→M6
    ↓
  result saved to results_cache ✅
    ↓
  "분석 완료!" ✅

Report Generation:
  User → GET /api/v4/reports/M2/pdf?context_id=xxx
    ↓
  Router reads from context_storage
    ↓
  context_storage.get_frozen_context(context_id)
    ↓
  ❌ NOT FOUND! (Because pipeline never saved there!)
    ↓
  Returns empty data or fallback values
```

---

## ✅ Solution Implemented

### Fix Location
**File**: `app/api/endpoints/pipeline_reports_v4.py`  
**Line**: ~405 (after `results_cache[request.parcel_id] = result`)

### What We Added

```python
# 🔥 CRITICAL FIX: Save to context_storage for PDF/HTML/Reports
from app.services.context_storage import context_storage

# Convert PipelineResult to Phase 3.5D assembled_data format
context_id = request.parcel_id
assembled_data = {
    "m6_result": {
        "lh_score_total": result.lh_review.total_score,
        "judgement": result.lh_review.decision,
        "grade": result.lh_review.grade,
        ...
    },
    "m2_result": {
        "land_value": result.appraisal.land_value,
        "land_value_per_pyeong": ...,
        "confidence_pct": ...,
        ...
    },
    "m3_result": {
        "recommended_type": result.housing_type.selected_type,
        "total_score": ...,
        ...
    },
    "m4_result": {
        "total_units": result.capacity.unit_summary.total_units,
        "incentive_units": ...,
        ...
    },
    "m5_result": {
        "npv_public_krw": result.feasibility.financial_metrics.npv_public,
        "irr_pct": ...,
        "roi_pct": ...,
        ...
    }
}

# Store in context_storage
context_storage.store_frozen_context(
    context_id=context_id,
    land_context=assembled_data,
    ttl_hours=24,
    parcel_id=request.parcel_id
)
```

### How It Works Now

```
┌─────────────────────────────────────────────────────────────┐
│  AFTER (FIXED)                                              │
└─────────────────────────────────────────────────────────────┘

Pipeline Execution:
  User → POST /api/v4/pipeline/analyze
    ↓
  Pipeline runs M1→M2→M3→M4→M5→M6
    ↓
  result saved to results_cache ✅
    ↓
  🔥 NEW: Convert to assembled_data format
    ↓
  🔥 NEW: context_storage.store_frozen_context(...)
    ↓
  "분석 완료!" ✅

Report Generation:
  User → GET /api/v4/reports/M2/pdf?context_id=xxx
    ↓
  Router reads from context_storage
    ↓
  context_storage.get_frozen_context(context_id)
    ↓
  ✅ FOUND! (Pipeline saved it!)
    ↓
  Extract M2 data: land_value = 60.82억원
    ↓
  Generate PDF with real data ✅
```

---

## 📊 Data Flow Verification

### Expected Data Mapping

| Pipeline Result | assembled_data Key | Report Field |
|----------------|-------------------|-------------|
| `result.appraisal.land_value` | `m2_result.land_value` | M2 토지 가치: 60.82억원 |
| `result.appraisal.land_value_per_pyeong` | `m2_result.land_value_per_pyeong` | M2 평당 단가: 5,000만원 |
| `result.appraisal.confidence_metrics.confidence_score` | `m2_result.confidence_pct` | M2 신뢰도: 85.0% |
| `result.housing_type.selected_type` | `m3_result.recommended_type` | M3 추천 유형: youth |
| `result.capacity.unit_summary.total_units` | `m4_result.total_units` | M4 세대수: 20세대 |
| `result.feasibility.financial_metrics.npv_public` | `m5_result.npv_public_krw` | M5 NPV: 7.93억원 |
| `result.feasibility.financial_metrics.irr` | `m5_result.irr_pct` | M5 IRR: 12.5% |
| `result.lh_review.decision` | `m6_result.judgement` | M6 판단: CONDITIONAL |
| `result.lh_review.total_score` | `m6_result.lh_score_total` | M6 점수: 75.0/100 |
| `result.lh_review.grade` | `m6_result.grade` | M6 등급: B |

---

## 🧪 Testing

### Automated Tests
```bash
pytest tests/test_phase35c_data_restoration.py tests/test_data_propagation.py -v

# Expected: 13/13 PASSED ✅
```

### Manual Verification

1. **Run Pipeline**:
```bash
curl -X POST http://localhost:8001/api/v4/pipeline/analyze \
  -H "Content-Type: application/json" \
  -d '{"parcel_id": "test-001", "use_cache": false}'
```

**Expected Response**:
```json
{
  "parcel_id": "test-001",
  "status": "success",
  "land_value": 6081933538,
  "recommended_units": 20,
  "npv_public": 792999999,
  "lh_decision": "CONDITIONAL",
  "lh_total_score": 75.0
}
```

2. **Verify Data Saved to context_storage**:
```bash
# Check if context exists
curl "http://localhost:8001/api/v4/context/test-001"
```

**Expected**: Should return full context with M2-M6 data

3. **Generate PDF Report**:
```bash
curl -o "M2_test.pdf" \
  "http://localhost:8001/api/v4/reports/M2/pdf?context_id=test-001"

open M2_test.pdf
```

**Expected Values in PDF**:
- ✅ 토지 가치: 60.82억원 (NOT "N/A")
- ✅ 평당 단가: 5,000만원 (NOT "N/A")
- ✅ 신뢰도: 85.0% (NOT "N/A")

4. **Generate HTML Report**:
```bash
open "http://localhost:8001/api/v4/reports/M2/html?context_id=test-001"
```

**Expected**: HTML should show real values, not placeholders

5. **Generate Final Reports** (All 6 types):
```bash
# All-in-One
curl -o "final_all_in_one.pdf" \
  "http://localhost:8001/api/v4/reports/final/all_in_one/pdf?context_id=test-001"

# Landowner Summary
curl -o "final_landowner.pdf" \
  "http://localhost:8001/api/v4/reports/final/landowner_summary/pdf?context_id=test-001"

# ... (test all 6 report types)
```

**Expected**: All reports show consistent, real data

---

## 🔄 Data Consistency Verification

### Critical Check
**All reports MUST show identical values**:

| Value | Pipeline API | M2 PDF | M6 PDF | All-in-One | Landowner |
|-------|-------------|--------|--------|-----------|-----------|
| 토지 가치 | 60.82억 | 60.82억 | 60.82억 | 60.82억 | 60.82억 |
| 세대수 | 20 | - | 20 | 20 | 20 |
| NPV | 7.93억 | - | 7.93억 | 7.93억 | 7.93억 |
| M6 판단 | COND | COND | COND | COND | COND |
| M6 점수 | 75.0 | 75.0 | 75.0 | 75.0 | 75.0 |

**❌ FAIL CRITERIA**: If ANY value differs across reports → FIX IMMEDIATELY

---

## 📝 Technical Details

### Phase 3.5D assembled_data Schema

```python
assembled_data = {
    "m6_result": {
        "lh_score_total": float,      # 75.0
        "judgement": str,              # "CONDITIONAL" | "GO" | "NOGO"
        "grade": str,                  # "A" | "B" | "C" | "D"
        "fatal_reject": bool,          # false
        "deduction_reasons": List[str],
        "improvement_points": List[str],
        "section_scores": {
            "policy": int,
            "location": int,
            "construction": int,
            "price": int,
            "business": int
        }
    },
    "m2_result": {
        "land_value": int,             # 6081933538
        "land_value_per_pyeong": int,  # 50000000
        "confidence_pct": float,       # 85.0
        "appraisal_method": str,
        "price_range": {
            "low": int,
            "high": int
        }
    },
    "m3_result": {
        "recommended_type": str,       # "youth" | "newlywed" | "general"
        "total_score": float,          # 85.5
        "demand_score": float,         # 90.0
        "type_scores": Dict[str, float]
    },
    "m4_result": {
        "total_units": int,            # 20
        "incentive_units": int,        # 26
        "gross_area_sqm": float,       # 1500.0
        "far_used": float,
        "bcr_used": float
    },
    "m5_result": {
        "npv_public_krw": int,         # 792999999
        "irr_pct": float,              # 12.5
        "roi_pct": float,              # 15.2
        "financial_grade": str,        # "B"
        "total_cost": int,
        "total_revenue": int
    }
}
```

### Storage Configuration

**context_storage Settings**:
- Backend: Redis (primary) + PostgreSQL (backup)
- TTL: 24 hours (configurable)
- Key Format: `context:{context_id}`
- Serialization: JSON (UTF-8)

**Configuration** (`.env`):
```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Context Storage
CONTEXT_STORAGE_BACKEND=redis
CONTEXT_TTL_SECONDS=86400  # 24 hours
```

---

## ✅ Verification Checklist

After deploying this fix:

- [ ] Pipeline executes successfully
- [ ] Data saved to `results_cache` (existing behavior)
- [ ] **NEW**: Data saved to `context_storage` (fixes reports)
- [ ] M2 PDF shows real land_value (60.82억원, not N/A)
- [ ] M3 PDF shows real recommended_type (youth, not N/A)
- [ ] M4 PDF shows real total_units (20세대, not N/A)
- [ ] M5 PDF shows real NPV/IRR (7.93억원/12.5%, not N/A)
- [ ] M6 PDF shows real judgement/score (CONDITIONAL/75.0, not N/A)
- [ ] All 6 final reports show real data
- [ ] All reports show **consistent** values (no mismatches)
- [ ] HTML previews show real data
- [ ] Automated tests pass (13/13)

---

## 🚨 Critical Notes

1. **Dual Storage**: Pipeline now saves to BOTH:
   - `results_cache` (fast, for pipeline API responses)
   - `context_storage` (persistent, for reports)

2. **Data Format**: Pipeline result → Phase 3.5D `assembled_data` format
   - Ensures compatibility with existing report system
   - Maintains data contract consistency

3. **Error Handling**: If `context_storage` save fails:
   - Pipeline still succeeds
   - Error is logged
   - `results_cache` still has data

4. **TTL Management**: Context stored for 24 hours
   - After 24h, reports will fail (need to re-run pipeline)
   - Consider increasing TTL for production

---

## 📦 Files Modified

| File | Changes | Lines |
|------|---------|-------|
| `app/api/endpoints/pipeline_reports_v4.py` | Added context_storage save after pipeline execution | ~70 lines added |

---

## 🎯 Success Criteria

### Before Fix
```
❌ Pipeline runs → "분석 완료!"
❌ PDF generated → Shows "N/A" / empty data
❌ HTML rendered → Shows placeholders
❌ Final reports → Shows empty data
```

### After Fix
```
✅ Pipeline runs → "분석 완료!"
✅ Data saved to context_storage
✅ PDF generated → Shows "60.82억원, 20세대, 7.93억원"
✅ HTML rendered → Shows real values
✅ Final reports → Shows complete data
```

---

## 🔧 Deployment Instructions

1. **Pull latest code**:
```bash
cd /home/user/webapp
git pull origin main
```

2. **Run tests**:
```bash
pytest tests/test_phase35c_data_restoration.py tests/test_data_propagation.py -v
# Expected: 13/13 PASSED
```

3. **Restart server**:
```bash
pm2 restart zerosite-staging
# or
python app/main.py
```

4. **Verify fix**:
```bash
# Run pipeline
curl -X POST http://localhost:8001/api/v4/pipeline/analyze \
  -H "Content-Type: application/json" \
  -d '{"parcel_id": "verify-fix-001", "use_cache": false}'

# Check PDF
curl -o verify.pdf \
  "http://localhost:8001/api/v4/reports/M2/pdf?context_id=verify-fix-001"

open verify.pdf
# Should show real values, NOT "N/A"
```

---

**Prepared by**: AI Assistant (Claude)  
**Date**: 2025-12-27  
**Status**: 🟢 FIX READY FOR TESTING

**한 줄 요약**: 파이프라인 실행 후 데이터가 context_storage에 저장되지 않아서 보고서가 비어있었음. 수정: 파이프라인 완료 후 context_storage에 저장하도록 추가.
