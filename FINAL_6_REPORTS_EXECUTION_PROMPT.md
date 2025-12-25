# 🔥 FINAL_6_REPORTS_EXECUTION_PROMPT

**다음 세션에서 이 프롬프트를 전체 복사-붙여넣기하세요.**

---

당신은 6종 보고서를 LH 제출 직전 단계에서
실제 파일을 수정·검증·완료 처리하는 최종 QA 엔지니어다.

목표는 단 하나다:
**"6종 보고서를 실제로 수정하고, LH 제출 가능 상태로 확정한다."**

---

## 🔒 [절대 금지]

- canonical_summary 구조 변경 ❌
- 계산 로직 / 엔진 수정 ❌
- KPI 산식 변경 ❌
- 보고서 문안 대량 추가 ❌

---

## 1️⃣ [1단계] 디자인 통합 강제 적용

### 1. 모든 보고서 HTML에 다음 링크만 존재하도록 수정:
```html
<link rel="stylesheet" href="/static/unified_report_theme.css">
```

### 2. 다음을 전부 제거:
- `<style>` 태그
- inline style
- font-size 직접 지정

### 3. 기준 검증:
- H1:22px / H2:18px / H3:15px / Body:14px / Table:13px
- line-height:1.6
- 6개 PDF 육안 구분 불가

**실행 방법:**
1. 각 보고서 파일 읽기
2. `<style>` 태그 찾아서 제거
3. inline `style=` 속성 찾아서 제거
4. `<link rel="stylesheet" href="/static/unified_report_theme.css">` 추가

**파일 목록:**
- `/home/user/webapp/backend/reports/quick_check.py`
- `/home/user/webapp/backend/reports/financial_feasibility.py`
- `/home/user/webapp/backend/reports/lh_technical.py`
- `/home/user/webapp/backend/reports/executive_summary.py`
- `/home/user/webapp/backend/reports/landowner_summary.py`
- `/home/user/webapp/backend/reports/all_in_one.py`

---

## 2️⃣ [2단계] 데이터 바인딩 전면 검증

### 모든 KPI는 반드시 다음 흐름만 허용:

```python
canonical_summary
→ resolve_scalar()
→ present_currency / present_percent / present_text
```

### 금지 패턴:
```python
# ❌ 금지
dict["key"]
value or "산출 중"
canonical_summary["M5"]["summary"]["npv"]

# ✅ 필수
from app.utils.report_value_resolver import resolve_scalar
from app.utils.present import present_currency, present_percent

npv = resolve_scalar(
    canonical_summary["M5"]["summary"].get("npv_public_krw")
)
npv_display = present_currency(npv)
```

### 필수 출력 값 (예시):
- **토지감정가:** 1,621,848,717원
- **총세대수:** 26세대
- **NPV:** 793,000,000원
- **IRR:** 12.81%
- **LH 판단:** 적합

**카드 / 본문 / Signature 값이 반드시 동일해야 한다.**

**실행 방법:**
1. 각 보고서에서 KPI 출력 부분 찾기
2. dict 직접 접근 찾아서 제거
3. resolve_scalar + present 패턴으로 교체
4. "산출 중" 하드코딩 제거

---

## 3️⃣ [3단계] 자동 검증 실행

### 다음 명령 실행 후 결과 확인:

```bash
# "산출 중" 검색 (0건이어야 함)
grep -r "산출 중" backend/reports/

# <style> 태그 검색 (0건이어야 함)
grep -r "<style>" backend/reports/

# resolve_scalar 사용 확인 (6건 이상이어야 함)
grep -r "resolve_scalar" backend/reports/

# present 함수 사용 확인 (12건 이상이어야 함)
grep -r "present_" backend/reports/

# dict 직접 접근 검색 (0건이어야 함, canonical_summary 제외)
grep -r "\[\"" backend/reports/*.py | grep -v "canonical_summary"
```

**각 검증 결과를 명시적으로 출력하세요.**

---

## 4️⃣ [4단계] PDF 육안 검증

### 6개 보고서 생성 후 확인:
- 6개 PDF 나란히 열기 (시뮬레이션)
- 폰트·여백·표 스타일 동일 확인
- 웹페이지 느낌 제거 확인
- 숫자만 봐도 결론 이해 가능 여부 확인

### 체크리스트:
- [ ] 제목 크기 6개 보고서 모두 동일
- [ ] 표 스타일 100% 동일
- [ ] 숫자에 천단위 콤마 있음
- [ ] "산출 중" / None / {} 노출 없음
- [ ] 전문 보고서 느낌 (웹페이지 ❌)

---

## 5️⃣ [5단계] 수정 대상 파일 목록

### CSS 파일 (생성 또는 확인)
```
/home/user/webapp/static/unified_report_theme.css
```

**내용 예시:**
```css
/* 통합 보고서 테마 */
body {
    font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
    font-size: 14px;
    line-height: 1.6;
    color: #2c3e50;
    margin: 40px;
}

h1 {
    font-size: 22px;
    color: #1a237e;
    border-bottom: 4px solid #1a237e;
    padding-bottom: 10px;
    margin-top: 40px;
}

h2 {
    font-size: 18px;
    color: #283593;
    border-bottom: 2px solid #283593;
    padding-bottom: 8px;
    margin-top: 30px;
}

h3 {
    font-size: 15px;
    color: #303f9f;
    margin-top: 20px;
}

table {
    font-size: 13px;
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 16px;
}

table th {
    background: #3949ab;
    color: white;
    padding: 12px;
    text-align: left;
}

table td {
    padding: 10px;
    border: 1px solid #e0e0e0;
}

.metric-card {
    background: #f5f5f5;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 16px;
}

.metric-value {
    font-size: 1.8em;
    font-weight: bold;
    color: #1976d2;
}

p {
    margin-bottom: 12px;
}
```

### 6종 보고서 (수정 필수)
1. `backend/reports/quick_check.py`
2. `backend/reports/financial_feasibility.py`
3. `backend/reports/lh_technical.py`
4. `backend/reports/executive_summary.py`
5. `backend/reports/landowner_summary.py`
6. `backend/reports/all_in_one.py`

---

## 🔚 [출력 규칙]

### 모든 조건 만족 시 (성공):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL 6 REPORTS VERIFIED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Design unified (CSS applied to all 6 reports)
✅ Data bound correctly (resolve_scalar + present)
✅ Verification passed (grep checks: 0 errors)
✅ Ready for LH submission

Files modified:
- static/unified_report_theme.css (created/updated)
- backend/reports/quick_check.py (modified)
- backend/reports/financial_feasibility.py (modified)
- backend/reports/lh_technical.py (modified)
- backend/reports/executive_summary.py (modified)
- backend/reports/landowner_summary.py (modified)
- backend/reports/all_in_one.py (modified)

Next step: Git commit and push
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 하나라도 실패 시:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FAILED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reason: (report_type / design_or_data_issue)

Details:
[구체적인 실패 원인과 위치]

Fix required before proceeding.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📋 [실행 체크리스트]

### Before Execution
- [ ] Read this prompt completely
- [ ] Understand 5-step process
- [ ] Confirm file paths

### During Execution
- [ ] Step 1: Remove inline styles, add CSS link
- [ ] Step 2: Replace dict access with resolve_scalar
- [ ] Step 3: Run grep verification commands
- [ ] Step 4: Simulate PDF visual check
- [ ] Step 5: Verify all files modified

### After Execution
- [ ] All grep checks passed (0 errors)
- [ ] Output "FINAL 6 REPORTS VERIFIED"
- [ ] Git commit with clear message
- [ ] Push to remote
- [ ] Update PR description

---

## 🎯 [성공 기준]

### Quantitative Criteria
```
grep -r "산출 중" backend/reports/        → 0 results
grep -r "<style>" backend/reports/         → 0 results
grep -r "resolve_scalar" backend/reports/  → ≥6 results
grep -r "present_" backend/reports/        → ≥12 results
```

### Qualitative Criteria
- 6 PDFs look identical in design
- All KPIs show actual numbers (no "산출 중")
- Data Signature = Body KPI = Card KPI
- Professional government report quality
- LH submission ready

---

## 🚀 [Execution Workflow]

```
START
  ↓
[Step 1] Design unification
  → Remove <style>, inline styles
  → Add CSS link to all 6 reports
  ↓
[Step 2] Data binding fix
  → Replace dict access with resolve_scalar
  → Add present_* formatting
  ↓
[Step 3] Automated verification
  → Run grep commands
  → Check results
  ↓
[Step 4] Visual verification
  → Simulate PDF comparison
  → Check consistency
  ↓
[Step 5] Final output
  → If all pass: "FINAL 6 REPORTS VERIFIED"
  → If any fail: "FAILED Reason: ..."
  ↓
END
```

---

## ⚠️ [Important Notes]

### What to Modify
- ✅ CSS (create unified_report_theme.css)
- ✅ HTML structure (remove inline styles)
- ✅ Data access patterns (use resolve_scalar)
- ✅ Formatting (use present_* functions)

### What NOT to Modify
- ❌ canonical_summary structure
- ❌ Calculation engines (M2-M6)
- ❌ API endpoints
- ❌ resolve_scalar/present function internals
- ❌ Report content/text (unless fixing data binding)

---

**작성일:** 2025-12-25  
**용도:** 다음 세션에서 실제 6종 보고서 수정·검증 실행  
**예상 소요 시간:** 30-45분  
**예상 결과:** "FINAL 6 REPORTS VERIFIED" 출력 및 LH 제출 품질 달성

---

**END OF FINAL EXECUTION PROMPT**
