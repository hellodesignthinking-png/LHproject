# 🔴 PRODUCTION API FIX REQUIRED

## 문제 상황

업로드된 PDF (`LH_Report_58e3d8ba-6136-4891-bab0-7b2d1f44cc93.pdf`):
- ✗ CAPEX: **0.00억원**
- ✗ NPV: **0.00억원**
- ✗ IRR: **0.00%**
- ✗ 모든 값이 0 또는 미제공

## 원인

**Production API (`app/routers/report_v13.py`)가 OLD 시스템을 사용 중:**

```python
# Line 22: OLD GENERATOR
from app.services_v13.report_full.report_full_generator import LHFullReportGenerator

# Line 99: OLD TEMPLATE
template = env.get_template('lh_submission_full.html.jinja2')
```

**우리가 수정한 파일은 테스트용:**
- `generate_expert_edition_v3.py` ← Test script (not used in production)
- `lh_expert_edition_v3.html.jinja2` ← New template (not used in production)
- Context fix in `generate_expert_edition_v3.py` (not applied to production)

---

## 해결 방법

### Option 1: Update Production Router (추천)

`app/routers/report_v13.py`를 수정하여 Expert Edition v3 사용:

```python
# BEFORE
from app.services_v13.report_full.report_full_generator import LHFullReportGenerator
template = env.get_template('lh_submission_full.html.jinja2')

# AFTER
from app.services_v13.report_full.report_context_builder import ReportContextBuilder
template = env.get_template('lh_expert_edition_v3.html.jinja2')

# Use build_expert_context() instead of generate_full_report_data()
builder = ReportContextBuilder()
context = builder.build_expert_context(
    address=request.address,
    land_area_sqm=request.land_area_sqm
)

# Apply same context flattening as in generate_expert_edition_v3.py
# (extract zoning['far'], zoning['bcr'], etc.)
```

### Option 2: Fix LHFullReportGenerator

`app/services_v13/report_full/report_full_generator.py`의 `generate_full_report_data()` 메서드를 수정하여 Expert Edition v3 context를 사용.

---

## 즉시 적용 가능한 패치

**Step 1:** `report_v13.py`에서 context flattening 추가
**Step 2:** `lh_submission_full.html.jinja2` 템플릿 업데이트 OR Expert Edition v3 템플릿 사용
**Step 3:** 테스트 후 배포

---

## 검증 방법

```bash
# Test production endpoint
curl -X POST http://localhost:8000/api/v13/report \
  -H "Content-Type: application/json" \
  -d '{
    "address": "월드컵북로 120",
    "land_area_sqm": 660.0
  }'

# Check PDF values
# Should see: CAPEX = 145억원, NPV = -140억원
```

---

## 긴급도: 🔴 HIGH

Production API가 0값을 출력하고 있어 즉시 수정 필요!

---

**Next Action:**
1. Patch `report_v13.py` to use Expert Edition v3 context builder
2. Apply context flattening logic
3. Test with actual API call
4. Verify PDF contains real values (145억원, -140억원)
5. Deploy to production
