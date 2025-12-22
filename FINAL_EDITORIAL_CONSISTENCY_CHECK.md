# Final Editorial & Consistency Check - Execution Log

**Purpose:** Audit and correct presentation-level inconsistencies  
**Scope:** Module Reports ↔ HTML ↔ Final 6 Report Types  
**Date:** 2025-12-22  
**Status:** 🔍 IN PROGRESS

---

## Constraints Applied

```
❌ NO calculation logic changes
❌ NO new value derivation
❌ NO new metrics introduction
❌ NO QA rule changes
❌ NO architecture changes
✅ ONLY: HTML structure, ordering, labeling, units, formatting, narrative linkage
```

---

## 7 Fixes to Apply

### FIX 1: Numeric Identity Lock ⭐ MOST IMPORTANT
- [ ] Audit all numeric values across module → HTML → final
- [ ] Ensure IDENTICAL display (rounding, unit, label)
- [ ] Remove approximations (약, 수준, 내외)
- [ ] Correct final report display if mismatch found

### FIX 2: Mandatory Core Data Preservation (M3/M4)
- [ ] Verify M3 data (추천 유형, 총점, 등급) in all reports
- [ ] Verify M4 data (총 세대수, 기본/인센티브, 법적 기준) in all reports
- [ ] Ensure summary reports reduce explanation, NOT numbers

### FIX 3: Section Order Canonicalization
- [ ] Enforce order: Title → KPI → Interpretation → Transition
- [ ] Reorder sections where needed
- [ ] No content rewriting

### FIX 4: Terminology Canonical Lock
- [ ] Replace synonyms with canonical terms:
  - 총 세대수 (not 공급 세대, 전체 세대)
  - 순현재가치(NPV)
  - 내부수익률(IRR)
  - 추진 가능/조건부 가능/부적합

### FIX 5: Narrative ↔ KPI Cross-Validation
- [ ] Verify every narrative number exists in KPI
- [ ] Match units and formatting
- [ ] Add missing numbers to KPI OR rewrite narrative

### FIX 6: Module Source Traceability
- [ ] Add source reference boxes to each section
- [ ] Format: "본 섹션은 M5 사업성 분석 결과를 기반으로 구성되었습니다."

### FIX 7: HTML Preview ↔ Final Report Parity
- [ ] Verify identical KPI grouping
- [ ] Verify identical metric order
- [ ] Verify identical highlight emphasis
- [ ] Ensure final report follows module HTML structure

---

## Validation Checklist

Before completion:
- [ ] Same number never appears differently
- [ ] No module output silently dropped
- [ ] All conclusions trace back to a module
- [ ] HTML preview ≒ Final PDF (content-wise)
- [ ] Report reads as "assembled", not "rewritten"

---

## Files to Audit

### Module Outputs (Source of Truth)
- `/app/services/module_html_renderer.py` (or equivalent)
- Module HTML templates
- Module summary data structures

### Final Report Assemblers (Audit Targets)
- `/app/services/final_report_assembly/assemblers/landowner_summary.py`
- `/app/services/final_report_assembly/assemblers/lh_technical.py`
- `/app/services/final_report_assembly/assemblers/quick_check.py`
- `/app/services/final_report_assembly/assemblers/financial_feasibility.py`
- `/app/services/final_report_assembly/assemblers/all_in_one.py`
- `/app/services/final_report_assembly/assemblers/executive_summary.py`

### Base Components
- `/app/services/final_report_assembly/base_assembler.py`
- KPI generation methods
- Decision block generation
- Narrative generation

---

## Audit Results

### Phase 1: Automated Checks
*To be filled during execution*

### Phase 2: Manual Verification
*Sample reports to be generated and reviewed*

### Phase 3: Corrections Applied
*List of changes made*

---

## Next Actions

1. Generate sample reports with real data
2. Side-by-side comparison: Module HTML vs Final Report
3. Document all inconsistencies found
4. Apply corrections (display-level only)
5. Re-generate and verify
6. Mark as COMPLETE when all validation passes

---

*This is the final editorial pass before production deployment.*
