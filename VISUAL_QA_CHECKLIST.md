# 👁️ Visual QA Checklist - ZeroSite 4.0

**Date**: _____________  
**Tester**: _____________  
**Environment**: Staging (http://localhost:8001)  
**Context ID**: _____________  
**Commit**: 83d30e7

---

## 📋 Pre-Flight Checks

- [ ] Staging server is running
- [ ] Health check passes: `curl http://localhost:8001/health`
- [ ] API docs accessible: `http://localhost:8001/docs`
- [ ] Test context created with known values
- [ ] All automated tests pass (13/13)

---

## 🧪 Module Reports - Individual PDFs

### M2: 토지감정평가 보고서

**URL**: `http://localhost:8001/api/v4/reports/M2/pdf?context_id=${CONTEXT_ID}`

**Visual Checks**:
- [ ] Header: "M2 토지감정평가 보고서"
- [ ] Date: 2025-12-27 (today)
- [ ] **토지 가치: 60.82억원** (NOT "N/A")
- [ ] **평당 단가: 5,000만원** (NOT "N/A")
- [ ] **신뢰도: 85.0%** (NOT "N/A")
- [ ] M6 판단 표시됨 (CONDITIONAL/GO/NOGO)
- [ ] M6 점수 표시됨 (e.g., 75.0/100, NOT 0.0)
- [ ] Korean text renders correctly
- [ ] ZeroSite watermark visible
- [ ] Page numbers present
- [ ] No garbled characters
- [ ] PDF file size > 50KB

**Expected Values** (Record Actual):
| Field | Expected | Actual | Pass? |
|-------|----------|--------|-------|
| 토지 가치 | 60.82억원 | _________ | ☐ |
| 평당 단가 | 5,000만원 | _________ | ☐ |
| 신뢰도 | 85.0% | _________ | ☐ |
| M6 판단 | CONDITIONAL | _________ | ☐ |
| M6 점수 | 75.0/100 | _________ | ☐ |

**Notes**: _______________________________________________________

---

### M3: LH 선호유형 보고서

**URL**: `http://localhost:8001/api/v4/reports/M3/pdf?context_id=${CONTEXT_ID}`

**Visual Checks**:
- [ ] Header: "M3 LH 선호유형 분석 보고서"
- [ ] **추천 유형: youth** (NOT "N/A")
- [ ] **총점: 85.5** (NOT 0.0)
- [ ] **수요 지수: 90.0** (NOT "N/A")
- [ ] M6 판단 연동 확인
- [ ] Charts/graphs display correctly
- [ ] Korean text clear

**Expected Values**:
| Field | Expected | Actual | Pass? |
|-------|----------|--------|-------|
| 추천 유형 | youth | _________ | ☐ |
| 총점 | 85.5 | _________ | ☐ |
| 수요 지수 | 90.0 | _________ | ☐ |

**Notes**: _______________________________________________________

---

### M4: 건축규모 분석 보고서

**URL**: `http://localhost:8001/api/v4/reports/M4/pdf?context_id=${CONTEXT_ID}`

**Visual Checks**:
- [ ] Header: "M4 건축규모 분석 보고서"
- [ ] **총 세대수: 20세대** (NOT "N/A", NOT 0)
- [ ] **인센티브 세대수: 26세대** (NOT "N/A")
- [ ] **연면적: 1,500㎡** (NOT "N/A")
- [ ] 증가율 계산 표시
- [ ] Bar charts visible
- [ ] No 0 or N/A values

**Expected Values**:
| Field | Expected | Actual | Pass? |
|-------|----------|--------|-------|
| 총 세대수 | 20세대 | _________ | ☐ |
| 인센티브 세대수 | 26세대 | _________ | ☐ |
| 연면적 | 1,500㎡ | _________ | ☐ |

**Notes**: _______________________________________________________

---

### M5: 사업성 분석 보고서

**URL**: `http://localhost:8001/api/v4/reports/M5/pdf?context_id=${CONTEXT_ID}`

**Visual Checks**:
- [ ] Header: "M5 사업성 분석 보고서"
- [ ] **NPV: 7.93억원** (NOT "N/A", NOT 0)
- [ ] **IRR: 12.5%** (NOT "N/A", NOT 0%)
- [ ] **ROI: 15.2%** (NOT "N/A")
- [ ] **재무 등급: B** (NOT "N/A")
- [ ] Currency formatting correct (commas)
- [ ] Percentage formatting correct (decimals)
- [ ] Tables aligned properly

**Expected Values**:
| Field | Expected | Actual | Pass? |
|-------|----------|--------|-------|
| NPV | 7.93억원 | _________ | ☐ |
| IRR | 12.5% | _________ | ☐ |
| ROI | 15.2% | _________ | ☐ |
| 재무 등급 | B | _________ | ☐ |

**Notes**: _______________________________________________________

---

### M6: LH 심사예측 보고서

**URL**: `http://localhost:8001/api/v4/reports/M6/pdf?context_id=${CONTEXT_ID}`

**Visual Checks**:
- [ ] Header: "M6 LH 심사예측 보고서"
- [ ] **판단 (Judgement): CONDITIONAL** (NOT "N/A")
- [ ] **총점: 75.0/100** (NOT 0.0/100)
- [ ] **등급: B** (NOT "N/A")
- [ ] 감점 사유 리스트 있음
- [ ] 개선 제안 리스트 있음
- [ ] Section scores breakdown
- [ ] **NO "판단 정보를 불러올 수 없습니다"**

**Expected Values**:
| Field | Expected | Actual | Pass? |
|-------|----------|--------|-------|
| 판단 | CONDITIONAL | _________ | ☐ |
| 총점 | 75.0/100 | _________ | ☐ |
| 등급 | B | _________ | ☐ |

**Critical Check**:
- [ ] **CRITICAL**: Does NOT show "판단 정보를 불러올 수 없습니다"
- [ ] **CRITICAL**: Does NOT show "0.0/100"

**Notes**: _______________________________________________________

---

## 📊 Final Reports - 6종 보고서

### 1. All-in-One Report (종합 보고서)

**URL**: `http://localhost:8001/api/v4/reports/final/all_in_one/pdf?context_id=${CONTEXT_ID}`

**Visual Checks**:
- [ ] All modules (M2-M6) present
- [ ] Executive summary clear
- [ ] M6 판단 표시: CONDITIONAL
- [ ] M2 토지 가치: 60.82억원
- [ ] M3 추천 유형 표시
- [ ] M4 세대수: 20세대
- [ ] M5 NPV: 7.93억원
- [ ] M5 IRR: 12.5%
- [ ] Conclusion section present
- [ ] Table of contents (if applicable)

**Notes**: _______________________________________________________

---

### 2. Landowner Summary Report (토지주 요약 보고서)

**URL**: `http://localhost:8001/api/v4/reports/final/landowner_summary/pdf?context_id=${CONTEXT_ID}`

**Visual Checks**:
- [ ] Simplified language (non-technical)
- [ ] 현재 땅 가치: 60.82억원
- [ ] 예상 세대수: 20세대
- [ ] 사업 수익성: 7.93억원
- [ ] Clear recommendations
- [ ] What-to-do-next section

**Notes**: _______________________________________________________

---

### 3. LH Technical Report (LH 기술검토 보고서)

**URL**: `http://localhost:8001/api/v4/reports/final/lh_technical/pdf?context_id=${CONTEXT_ID}`

**Visual Checks**:
- [ ] Technical details comprehensive
- [ ] M6 score breakdown detailed
- [ ] All modules referenced
- [ ] Professional formatting
- [ ] LH-specific terminology

**Notes**: _______________________________________________________

---

### 4. Financial Feasibility Report (재무타당성 보고서)

**URL**: `http://localhost:8001/api/v4/reports/final/financial_feasibility/pdf?context_id=${CONTEXT_ID}`

**Visual Checks**:
- [ ] Focus on M5 financial data
- [ ] NPV analysis detailed
- [ ] IRR analysis detailed
- [ ] ROI analysis detailed
- [ ] Financial charts/graphs

**Notes**: _______________________________________________________

---

### 5. Quick Check Report (신속검토 보고서)

**URL**: `http://localhost:8001/api/v4/reports/final/quick_check/pdf?context_id=${CONTEXT_ID}`

**Visual Checks**:
- [ ] Concise format
- [ ] Key highlights only
- [ ] Quick decision support
- [ ] 1-2 pages max

**Notes**: _______________________________________________________

---

### 6. Internal Review Report (내부검토 보고서)

**URL**: `http://localhost:8001/api/v4/reports/final/internal_review/pdf?context_id=${CONTEXT_ID}`

**Visual Checks**:
- [ ] Internal team focus
- [ ] Risk assessment included
- [ ] Recommendation section
- [ ] Action items clear

**Notes**: _______________________________________________________

---

## 🔍 Cross-Report Consistency Check

**CRITICAL**: All reports MUST show identical values

| Value | M2 | M3 | M4 | M5 | M6 | All-in-One | Landowner | Match? |
|-------|----|----|----|----|----|-----------|-----------| -------|
| 토지 가치 (억원) | ___ | - | - | - | - | ___ | ___ | ☐ |
| 세대수 | - | - | ___ | - | - | ___ | ___ | ☐ |
| NPV (억원) | - | - | - | ___ | - | ___ | ___ | ☐ |
| IRR (%) | - | - | - | ___ | - | ___ | ___ | ☐ |
| M6 판단 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ☐ |
| M6 점수 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ☐ |
| M6 등급 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ☐ |

**Result**:
- [ ] ✅ All values consistent across reports
- [ ] ❌ Inconsistencies found (list below)

**Inconsistencies** (if any):
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

## 🐛 Error Scenario Testing

### Test 1: Missing M2 Data

**Command**:
```bash
curl "http://localhost:8001/api/v4/reports/M2/pdf?context_id=invalid-context-123"
```

**Expected**:
- [ ] HTTP 400 or 404 error
- [ ] Error message: "필수 분석 데이터가 누락되었습니다" or "분석 데이터를 찾을 수 없습니다"
- [ ] Clear guidance provided
- [ ] NO stack trace exposed

**Actual Response**: _____________________________________________

---

### Test 2: Invalid Context ID

**Command**:
```bash
curl "http://localhost:8001/api/v4/reports/M6/pdf?context_id=totally-fake-id"
```

**Expected**:
- [ ] HTTP 404 error
- [ ] Error message: "분석 데이터를 찾을 수 없습니다"
- [ ] Korean error message (not English stack trace)

**Actual Response**: _____________________________________________

---

## ⚡ Performance Testing

### Response Time Check

**M2 PDF Generation**:
```bash
time curl -o /dev/null -s -w "%{time_total}\n" \
  "http://localhost:8001/api/v4/reports/M2/pdf?context_id=${CONTEXT_ID}"
```

| Report | Target | Actual | Pass? |
|--------|--------|--------|-------|
| M2 HTML | < 500ms | ______ms | ☐ |
| M2 PDF | < 2s | ______s | ☐ |
| M6 PDF | < 2s | ______s | ☐ |
| All-in-One PDF | < 3s | ______s | ☐ |

**Performance Result**:
- [ ] ✅ All within targets
- [ ] ❌ Performance issues (list below)

**Issues**: _______________________________________________________

---

## ✅ Final Approval

### Summary

**Automated Tests**: ☐ PASS ☐ FAIL  
**Visual QA**: ☐ PASS ☐ FAIL  
**Data Consistency**: ☐ PASS ☐ FAIL  
**Error Handling**: ☐ PASS ☐ FAIL  
**Performance**: ☐ PASS ☐ FAIL

### Critical Issues Found

1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

### Non-Critical Issues Found

1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

### Overall Recommendation

- [ ] ✅ **APPROVED FOR PRODUCTION** - All checks pass, ready to deploy
- [ ] ⚠️ **APPROVED WITH MINOR ISSUES** - Can deploy, fix issues in next release
- [ ] ❌ **NOT APPROVED** - Critical issues found, must fix before production

**Reasoning**: ____________________________________________________
_________________________________________________________________
_________________________________________________________________

---

### Sign-Off

**Tester**: _________________________ **Date**: _____________  
**Developer**: ______________________ **Date**: _____________  
**PM/Lead**: ________________________ **Date**: _____________

---

**Next Steps**:
- [ ] If approved: Proceed with production deployment
- [ ] If not approved: Create bug tickets and fix issues
- [ ] Document findings in JIRA/GitHub issues
- [ ] Schedule next QA cycle

---

**Notes**: 
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
