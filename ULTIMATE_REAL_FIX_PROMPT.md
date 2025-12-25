# 🔥 ULTIMATE_REAL_FIX_PROMPT - 실제 코드 수정용

**⚠️ 이 프롬프트는 실제 결과물을 변경합니다 ⚠️**  
**다음 세션에서 이 프롬프트를 복사-붙여넣기하면 실제 수정이 일어납니다.**

---

당신은 이제 **ZeroSite 6종 보고서의 실제 코드 수정 책임자**다.
이번 세션은 **문서 검토가 아니라, 실제 보고서 결과물을 바꾸는 세션**이다.

---

## 🎯 이번 세션의 절대 목표

> **6종 보고서 PDF/HTML 결과물에서**
>
> * "산출 중 / 산출 불가 / None" 이 단 한 글자도 남지 않게 한다
> * KPI 카드 · 요약 · 본문 · Data Signature 값이 100% 동일하게 만든다
> * LH 제출 가능한 보고서로 실제 출력 상태를 변경한다

---

## 🔒 절대 금지

* canonical_summary 구조 변경 ❌
* 계산 엔진 수정 ❌
* 점수/산식 변경 ❌
* 임의 숫자 하드코딩 ❌

---

## 📊 현재 상태 팩트 체크

### ❌ 실제로 남아있는 문제들

1. **KPI 영역에 여전히 "산출 중" 노출**
   - landowner_summary: 총세대수, M2/M5/M6 KPI
   - all_in_one: KPI 카드 전체 "산출 중"

2. **Data Signature ↔ 본문 불일치**
   - Signature: 총세대수 26, IRR 12.81%
   - 본문/Executive: "산출 중", "산출 불가"

3. **디자인 기존 상태 유지**
   - 섹션별 여백·행간·제목 간격 제각각
   - 웹페이지 출력물 느낌

4. **resolve_scalar + present 패턴 미적용**
   - 일부 테이블만 값 표시
   - 카드/요약 영역은 placeholder

---

## 1️⃣ 가장 먼저 할 일 (강제)

### 아래 파일을 **실제로 열고 읽는다**

```
/home/user/webapp/backend/reports/executive_summary.py
/home/user/webapp/backend/reports/landowner_summary.py
/home/user/webapp/backend/reports/quick_check.py
/home/user/webapp/backend/reports/financial_feasibility.py
/home/user/webapp/backend/reports/lh_technical.py
/home/user/webapp/backend/reports/all_in_one.py
```

**각 파일에서 찾아야 할 것:**
- "산출 중" 문자열
- "산출 불가" 문자열
- `value or "산출 중"` 패턴
- KPI 카드 영역 코드
- Executive Summary 영역 코드

---

## 2️⃣ KPI 영역 강제 수정 규칙 (핵심)

### ❌ 즉시 제거해야 하는 패턴

```python
"산출 중"
"산출 불가"
value or "산출 중"
dict["key"]
dict.get("key")
canonical_summary["M5"]["summary"]["npv"]
```

### ✅ 유일하게 허용되는 패턴

```python
from app.utils.report_value_resolver import resolve_scalar
from app.utils.present import present_currency, present_percent
```

```python
# 예시 1: 총세대수
units = resolve_scalar(
    canonical_summary["M4"]["summary"].get("total_units")
)
units_display = f"{units}세대" if units else "-"
```

```python
# 예시 2: NPV
npv = resolve_scalar(
    canonical_summary["M5"]["summary"].get("npv_public_krw")
)
npv_display = present_currency(npv)
```

```python
# 예시 3: IRR
irr = resolve_scalar(
    canonical_summary["M5"]["summary"].get("irr_pct")
)
irr_display = present_percent(irr)
```

👉 **KPI 카드 / 요약 / Executive Summary에 반드시 적용**

---

## 3️⃣ 반드시 값이 보여야 하는 항목 (모든 보고서 공통)

### 필수 출력 KPI

| 항목 | 기대값 | 출처 |
|------|--------|------|
| **토지감정가** | 1,621,848,717원 | M2.summary.land_value_total_krw |
| **총세대수** | 26세대 | M4.summary.total_units |
| **NPV** | 793,000,000원 | M5.summary.npv_public_krw |
| **IRR** | 12.81% | M5.summary.irr_pct |
| **LH 판단** | 적합 | M6.summary.decision |

⚠️ **하나라도 "산출 중"이면 FAILED**

### 수정 위치

**각 보고서에서 이 값들이 나타나는 곳:**
1. Executive Summary (요약 카드)
2. KPI Dashboard (메트릭 카드)
3. Data Signature (상단 요약)
4. 본문 테이블
5. 결론 섹션

**모든 위치에서 동일한 값이 표시되어야 함**

---

## 4️⃣ 실제 수정 단계 (Step-by-Step)

### Step 1: 각 파일 열기 및 문제 위치 찾기

```bash
cd /home/user/webapp

# "산출 중" 위치 찾기
grep -n "산출 중" backend/reports/executive_summary.py
grep -n "산출 중" backend/reports/landowner_summary.py
grep -n "산출 중" backend/reports/all_in_one.py
```

### Step 2: KPI 카드 영역 수정

**각 파일에서 KPI 카드를 찾아서:**
```python
# ❌ Before (제거)
<div class="metric-value">산출 중</div>

# ✅ After (적용)
npv = resolve_scalar(canonical_summary["M5"]["summary"].get("npv_public_krw"))
<div class="metric-value">{present_currency(npv)}</div>
```

### Step 3: Executive Summary 영역 수정

```python
# ❌ Before
"NPV: 산출 중"

# ✅ After
npv = resolve_scalar(canonical_summary["M5"]["summary"].get("npv_public_krw"))
f"NPV: {present_currency(npv)}"
```

### Step 4: Data Signature 일치 확인

```python
# Data Signature의 값과 본문 KPI가 100% 동일해야 함
# canonical_summary를 단일 진실원(Source of Truth)으로 사용
```

---

## 5️⃣ 디자인 실적용 확인

### CSS 통합

1. **unified_report_theme.css 확인**
```bash
ls -la /home/user/webapp/static/unified_report_theme.css
```

2. **각 보고서에서 CSS 링크 확인**
```python
# 각 파일의 HTML 헤더에 있어야 함
<link rel="stylesheet" href="/static/unified_report_theme.css">
```

3. **inline style 제거**
```bash
# inline style 검색
grep -n 'style=' backend/reports/*.py
# 결과: 0건이어야 함
```

4. **<style> 태그 제거**
```bash
# <style> 태그 검색
grep -n '<style>' backend/reports/*.py
# 결과: 0건이어야 함
```

---

## 6️⃣ 수정 후 검증 (필수)

### 자동 검증 명령어

```bash
cd /home/user/webapp

# 1. "산출 중" 완전 제거 확인 (0이어야 함)
grep -r "산출 중" backend/reports/ | wc -l

# 2. "산출 불가" 완전 제거 확인 (0이어야 함)
grep -r "산출 불가" backend/reports/ | wc -l

# 3. resolve_scalar 사용 확인 (6개 이상)
grep -r "resolve_scalar" backend/reports/ | wc -l

# 4. present 함수 사용 확인 (12개 이상)
grep -r "present_" backend/reports/ | wc -l

# 5. inline style 제거 확인 (0이어야 함)
grep -r 'style=' backend/reports/*.py | wc -l

# 6. <style> 태그 제거 확인 (0이어야 함)
grep -r '<style>' backend/reports/*.py | wc -l
```

### 수동 검증 체크리스트

- [ ] executive_summary.py: KPI 카드 모두 실제 값
- [ ] landowner_summary.py: 총세대수, M2/M5/M6 KPI 실제 값
- [ ] all_in_one.py: KPI 카드 전체 실제 값
- [ ] Data Signature = 본문 KPI = 카드 KPI
- [ ] "산출 중" / "산출 불가" 완전 제거
- [ ] 6개 보고서 폰트/여백 통일

---

## 7️⃣ Git 커밋 (수정 완료 후)

### 커밋 메시지 템플릿

```bash
git add backend/reports/
git commit -m "fix: Remove '산출 중' and apply resolve_scalar + present pattern

ACTUAL CODE CHANGES (not just documentation):

1. KPI Cards Fixed:
   - executive_summary.py: All KPI cards show actual values
   - landowner_summary.py: 총세대수, M2/M5/M6 KPIs fixed
   - all_in_one.py: All KPI cards updated

2. Data Binding Pattern Applied:
   - Replaced dict access with resolve_scalar()
   - Applied present_currency(), present_percent()
   - Removed all '산출 중' / '산출 불가' hardcoding

3. Verification Results:
   - grep '산출 중': 0 results ✓
   - grep 'resolve_scalar': 6+ results ✓
   - grep 'present_': 12+ results ✓

4. Data Consistency:
   - Data Signature = Body KPI = Card KPI ✓

Status: ACTUAL OUTPUTS CHANGED - Ready for testing"

git push origin feature/expert-report-generator
```

---

## 🔚 출력 규칙 (엄격)

### 모든 수정이 실제 결과물에 반영되었을 때만

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL 6 REPORTS VERIFIED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Actual code modified (6 files)
✅ KPI cards show real values
✅ "산출 중" completely removed
✅ Data Signature = Body = Card
✅ Ready for LH submission

Files modified:
- backend/reports/executive_summary.py
- backend/reports/landowner_summary.py
- backend/reports/quick_check.py
- backend/reports/financial_feasibility.py
- backend/reports/lh_technical.py
- backend/reports/all_in_one.py

Next step: Test with actual report generation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 하나라도 미반영 시

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FAILED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reason: Output not changed

Failed items:
- "산출 중" still exists (N locations)
- KPI cards still show placeholders
- Data inconsistency detected

Details:
[구체적인 실패 위치와 내용]

Fix required before proceeding.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📌 핵심 포인트 (반드시 이해)

### 1. 이번 세션 = 실행 세션
```
문서 검토 ❌
계획 수립 ❌
준비 작업 ❌
→ 실제 코드 수정 ✅
```

### 2. 결과물 변경 필수
```
문서만 수정 ❌
주석만 추가 ❌
→ 실제 HTML/PDF 출력 변경 ✅
```

### 3. 검증은 결과물 기준
```
코드 수정 완료 ❌
→ 실제 "산출 중" 제거 확인 ✅
→ KPI 값 실제 표시 확인 ✅
```

---

## 🎯 성공 기준 요약

### 정량적 기준
```
✅ grep "산출 중" → 0 results
✅ grep "resolve_scalar" → ≥6 results
✅ grep "present_" → ≥12 results
✅ grep 'style=' → 0 results
✅ grep '<style>' → 0 results
```

### 정성적 기준
```
✅ KPI 카드 모두 실제 값 표시
✅ Data Signature = 본문 = 카드
✅ "산출 중" 완전 제거
✅ 6개 보고서 디자인 통일
✅ LH 제출 가능 품질
```

---

## ⚠️ 이 프롬프트의 의미

```
지금까지: 준비·설계·문서 = 100점 ✓
실제 변경: 0점 (아직 안 함) ✗

이 프롬프트: 실제 변경을 일으키는 마지막 키 🔑

다음 세션에서 이 프롬프트 실행
→ 비로소 "6종 보고서 수정 완료" 상태
```

---

**작성일:** 2025-12-25  
**용도:** 다음 세션에서 실제 코드 수정 실행  
**목표:** 실제 결과물 변경 (HTML/PDF에서 "산출 중" 제거)  
**예상 소요 시간:** 45-60분

---

**⚠️ 이 프롬프트는 실제 파일을 수정합니다 ⚠️**  
**⚠️ 다음 세션에서 복사-붙여넣기하면 실제 변경이 발생합니다 ⚠️**

---

**END OF ULTIMATE REAL FIX PROMPT**
