# 🔥 ULTIMATE_FINAL_EXECUTION_PROMPT

**⚠️ 이것이 마지막 프롬프트입니다.**  
**다음 세션에서 이 프롬프트 전체를 복사-붙여넣기하면 모든 것이 끝납니다.**

---

당신은 이제 **6종 보고서를 실제로 수정·검증·출고 확정하는 최종 집도자(QA + Implementer)**다.
이번 세션은 **실행 세션**이며, 설계·기획·문서화는 이미 모두 끝났다.

이 세션의 목표는 단 하나다.

> **"6종 보고서를 실제로 수정하고,
> LH 제출 가능 상태임을 시스템적으로 검증한 뒤,
> 'FINAL VERIFIED' 상태로 확정한다."**

---

## 🔒 절대 금지 (위반 시 즉시 FAILED)

* canonical_summary 구조 변경 ❌
* 계산 로직 / 엔진 수정 ❌
* KPI 산식 변경 ❌
* 보고서 문안(서술) 대량 추가 ❌

👉 허용 범위는 **오직 아래 3가지뿐이다**

1. 디자인(CSS/HTML 구조)
2. 데이터 바인딩(resolve_scalar / present)
3. 누락·불일치 수정

---

## 🎯 성공 기준 (이 기준 외 성공 없음)

```
6종 보고서 모두
- 디자인 완전 통일
- 데이터 100% 실연동
- Data Signature = 카드 = 본문 KPI
- LH 제출 품질
```

---

## 1️⃣ 디자인 실제 수정 (실행 필수)

### 반드시 수행할 작업

1. 모든 보고서 HTML에서 **단 하나의 CSS만 사용**

```html
<link rel="stylesheet" href="/static/unified_report_theme.css">
```

2. 전면 제거 대상

* `<style>` 태그
* inline style
* font-size / margin / padding 직접 지정

### 폰트·레이아웃 기준 (하나라도 다르면 실패)

| 항목          | 기준           |
| ----------- | ------------ |
| Font        | Noto Sans KR |
| H1          | 22px         |
| H2          | 18px         |
| H3          | 15px         |
| Body        | 14px         |
| Table       | 13px         |
| Line-height | 1.6          |

👉 **6개 PDF를 나란히 놓았을 때 시각적으로 구분 불가해야 함**

### 실행 방법

**Step 1:** unified_report_theme.css 생성 (없으면)

```bash
# 파일 위치
/home/user/webapp/static/unified_report_theme.css
```

**CSS 내용:**
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

**Step 2:** 6개 보고서 파일 수정

각 보고서 파일에서:
1. `<style>` 태그 전부 제거
2. inline `style=` 속성 전부 제거
3. `<link rel="stylesheet" href="/static/unified_report_theme.css">` 추가

**수정 대상 파일:**
```
/home/user/webapp/backend/reports/quick_check.py
/home/user/webapp/backend/reports/financial_feasibility.py
/home/user/webapp/backend/reports/lh_technical.py
/home/user/webapp/backend/reports/executive_summary.py
/home/user/webapp/backend/reports/landowner_summary.py
/home/user/webapp/backend/reports/all_in_one.py
```

---

## 2️⃣ 데이터 바인딩 실제 수정 (M2~M6)

### ❌ 전면 금지 패턴

```python
dict["key"]
value or "산출 중"
dict.get("value")
canonical_summary["M5"]["summary"]["npv"]
```

### ✅ 유일 허용 패턴

```python
from app.utils.report_value_resolver import resolve_scalar
from app.utils.present import present_currency, present_percent, present_text
```

```python
# 예시: NPV 출력
npv = resolve_scalar(
    canonical_summary["M5"]["summary"].get("npv_public_krw")
)
npv_display = present_currency(npv)
```

```python
# 예시: IRR 출력
irr = resolve_scalar(
    canonical_summary["M5"]["summary"].get("irr_pct")
)
irr_display = present_percent(irr)
```

### 반드시 실제 값이 출력되어야 하는 KPI

| 항목    | 기준 값 (예시)     |
| ----- | -------------- |
| 토지감정가 | 1,621,848,717원 |
| 총세대수  | 26세대           |
| NPV   | 793,000,000원   |
| IRR   | 12.81%         |
| LH 판단 | 적합             |

👉 **카드 / 본문 표 / Data Signature 값이 100% 동일해야 한다**

### 실행 방법

각 보고서에서:
1. KPI 출력 부분 찾기
2. dict 직접 접근 패턴 찾기
3. resolve_scalar + present 패턴으로 교체
4. "산출 중" 하드코딩 제거

---

## 3️⃣ 자동 검증 (실행 후 반드시 확인)

다음 명령을 **실제로 실행**하고 결과를 확인한다.

```bash
# 1. "산출 중" 존재 여부 (반드시 0)
cd /home/user/webapp
grep -r "산출 중" backend/reports/ | wc -l

# 2. <style> 태그 존재 여부 (반드시 0)
grep -r "<style>" backend/reports/ | wc -l

# 3. resolve_scalar 사용 여부 (6 이상)
grep -r "resolve_scalar" backend/reports/ | wc -l

# 4. present 함수 사용 여부 (12 이상)
grep -r "present_" backend/reports/ | wc -l

# 5. dict 직접 접근 여부 (0, canonical_summary 제외)
grep -r "\[\"" backend/reports/*.py | grep -v "canonical_summary" | wc -l
```

**각 검증 결과를 명시적으로 출력하고 판정하세요.**

---

## 4️⃣ PDF 육안 최종 검증 (인간 기준)

다음 질문에 **모두 YES**여야 한다.

* 이 PDF를 출력해서 바로 결재선에 올릴 수 있는가?
* 웹페이지처럼 보이지 않는가?
* 숫자만 보고도 결론이 이해되는가?
* 6개 보고서가 같은 회사 문서처럼 보이는가?

### 10초 체크리스트

- [ ] 6개 PDF 제목 크기 동일
- [ ] 표 스타일 100% 동일
- [ ] 숫자에 천단위 콤마 있음
- [ ] "산출 중" / None / {} 없음
- [ ] 전문 보고서 느낌 (웹페이지 ❌)

---

## 5️⃣ 최종 출력 및 Git 커밋

### 검증 통과 시

**Step 1:** 성공 메시지 출력

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL 6 REPORTS VERIFIED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Design unified (CSS applied to all 6 reports)
✅ Data bound correctly (resolve_scalar + present)
✅ Verification passed (all grep checks: PASS)
✅ Ready for LH submission

Files modified:
- static/unified_report_theme.css
- backend/reports/quick_check.py
- backend/reports/financial_feasibility.py
- backend/reports/lh_technical.py
- backend/reports/executive_summary.py
- backend/reports/landowner_summary.py
- backend/reports/all_in_one.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Step 2:** Git 커밋

```bash
cd /home/user/webapp
git add .
git commit -m "fix: Unify 6 reports design and data binding - LH submission ready

Design Unification:
- Created unified_report_theme.css with standard font scale
- Removed all inline styles and <style> tags from 6 reports
- Applied consistent layout (H1:22px, H2:18px, H3:15px, Body:14px)

Data Binding Fix:
- Replaced dict direct access with resolve_scalar + present pattern
- Removed all '산출 중' hardcoding
- Ensured Data Signature = Card KPI = Body KPI

Verification Results:
- grep '산출 중': 0 results ✓
- grep '<style>': 0 results ✓
- grep 'resolve_scalar': 6+ results ✓
- grep 'present_': 12+ results ✓

Status: LH submission quality achieved"

git push origin feature/expert-report-generator
```

### 검증 실패 시

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FAILED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reason: (report_type / design_issue / data_binding_issue)

Failed Checks:
[구체적인 실패 원인과 위치]

Example:
- grep '산출 중': 3 results (expected: 0)
  → backend/reports/quick_check.py:45
  → backend/reports/financial_feasibility.py:120
  → backend/reports/lh_technical.py:89

Fix required before proceeding.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🔚 출력 규칙 (엄격)

### 모든 조건 충족 시 **정확히 이 문장만 출력**

```
FINAL 6 REPORTS VERIFIED
Design unified, data bound correctly
Ready for LH submission
```

### 하나라도 실패 시

```
FAILED
Reason: (report_type / design_issue / data_binding_issue)
```

---

## 📌 이 프롬프트의 의미

* 이것이 **마지막 프롬프트**다
* 이 이후는 "수정"이 아니라 "제출/활용" 단계다
* 성공 메시지가 나오면 **Git commit & PR merge 진행**

---

## 🔑 최종 정리 (중요)

* 지금까지의 모든 작업은 **이 프롬프트를 실패 없이 실행하기 위한 준비**
* 다음 세션에서 이 프롬프트 실행 = **프로젝트 1차 완결**
* 더 이상 설계·가이드·정리는 필요 없음

---

## 📋 실행 워크플로우

```
START
  ↓
[1단계] 디자인 수정
  → CSS 생성
  → 6개 보고서 <style> 제거
  → CSS 링크 추가
  ↓
[2단계] 데이터 바인딩 수정
  → dict 접근 → resolve_scalar + present
  → "산출 중" 제거
  ↓
[3단계] 자동 검증
  → 5개 grep 명령 실행
  → 결과 확인 및 판정
  ↓
[4단계] 육안 검증
  → 10초 체크리스트
  → LH 기준 4개 질문
  ↓
[5단계] 최종 출력
  → 성공: "FINAL 6 REPORTS VERIFIED"
  → 실패: "FAILED Reason: ..."
  → Git commit & push (성공 시)
  ↓
END
```

---

## ⚠️ 중요 주의사항

### 수정 허용
- ✅ CSS 파일 생성/수정
- ✅ HTML 구조 (style 제거, CSS 링크 추가)
- ✅ 데이터 접근 패턴 (resolve_scalar + present)
- ✅ "산출 중" 하드코딩 제거

### 수정 금지
- ❌ canonical_summary 구조
- ❌ M2-M6 계산 엔진
- ❌ API 엔드포인트
- ❌ resolve_scalar/present 함수 내부
- ❌ 보고서 서술 내용 대량 변경

---

**작성일:** 2025-12-25  
**용도:** 다음 세션 첫 메시지로 복사-붙여넣기  
**목표:** "FINAL 6 REPORTS VERIFIED" 출력 및 프로젝트 1차 완결  
**예상 소요 시간:** 30-45분

---

**⚠️ 이것이 마지막 실행 프롬프트입니다.**  
**다음 세션에서 이 프롬프트를 복사-붙여넣기하면 모든 것이 끝납니다.**

---

**END OF ULTIMATE FINAL EXECUTION PROMPT**
