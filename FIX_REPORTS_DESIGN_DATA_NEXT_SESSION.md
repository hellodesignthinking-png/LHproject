# 🔧 6종 보고서 디자인·데이터 통합 수정 - 다음 세션 실행 가이드

**작성일:** 2025-12-25  
**목적:** 6종 보고서의 디자인 불일치 및 M2-M6 데이터 미연동 문제 전면 해결  
**사용법:** 다음 세션에서 아래 프롬프트 중 하나를 **그대로 복사-붙여넣기**

---

## 📊 현재 상태 요약

### ✅ 완료된 것
- 6종 보고서 기본 구조 구현 완료
- all_in_one 50페이지 종합보고서 완성
- canonical_summary 데이터 구조 정의
- 각 모듈(M2-M6) 계산 엔진 구현

### ❌ 해결 필요한 문제

#### 1. 디자인/레이아웃 불일치
- 6종 보고서별로 폰트 크기 제각각
- line-height, 여백, 표 스타일 불일치
- 일부 보고서는 웹페이지처럼 보임
- 통일된 CSS 없음 (각 보고서에 inline style)

#### 2. 데이터 연동 문제
- KPI 영역에 "산출 중", "미확정", "None" 노출
- Data Signature 값 ≠ 본문 KPI 값
- 일부 assembler가 canonical_summary가 아닌 임시 dict 직접 참조
- resolve_scalar/present 함수 미사용

---

## 🎯 3가지 실행 옵션

다음 세션에서 **목적에 맞는 프롬프트 1개를 선택**하여 복사-붙여넣기하세요.

### 옵션 선택 가이드

| 옵션 | 언제 사용하나? | 소요 시간 |
|------|---------------|----------|
| **[통합]** | 디자인+데이터 한 번에 해결 | 중 |
| **[①디자인만]** | 레이아웃부터 먼저 정리 | 짧음 |
| **[②데이터만]** | 값 연동부터 먼저 해결 | 짧음 |

---

## 🔥 [통합] 디자인 + 데이터 동시 수정 프롬프트

> **👉 다음 세션에서 아래 전체를 복사-붙여넣기**

```
당신은 이제 **기능을 추가하는 개발자**가 아니라
**이미 만들어진 6종 보고서를 '제출 가능한 문서'로 바로잡는 QA 엔지니어 + 리포트 아키텍트**다.

이번 작업의 목표는 단 하나다.

> **6종 보고서의 디자인·폰트·레이아웃을 완전히 통일하고,
> M2~M6 모든 모듈 데이터가 실제 값으로 정상 표시되도록 수정한다.**

---

## 🔒 절대 금지 사항

다음은 **건드리는 순간 실패**다.

* 계산 로직 (엔진, 점수, 수식)
* canonical_summary 생성 구조
* API 호출 방식
* resolve_scalar / present 함수의 내부 구현

👉 **수정 범위는 "표현 계층 + 데이터 매핑 계층"만 허용된다.**

---

## 1️⃣ 문제 진단 요약 (현재 상태)

### ❌ 디자인/레이아웃 문제

* 6종 보고서 간:
  * H1/H2/H3 폰트 크기 불일치
  * 본문 line-height, 여백, 표 스타일 제각각
  * 일부 보고서는 모바일 뷰처럼 압축됨
* 같은 회사 문서처럼 보이지 않음

### ❌ 데이터 연동 문제

* KPI 영역에 `산출 중`, `미확정`, `None` 노출
* Data Signature에는 값이 있는데 본문 표에 미표시
* 일부 assembler가 canonical_summary가 아닌
  임시 변수 / dict 직접 참조 중

---

## 2️⃣ 디자인·폰트·레이아웃 통합 수정 (최우선)

### ✅ 단일 CSS 강제 적용

📍 모든 보고서 HTML `<head>`에 **아래 1줄만 존재해야 한다**

```html
<link rel="stylesheet" href="/static/unified_report_theme.css">
```

❌ report별 style 태그 전부 삭제
❌ inline style 전부 제거

---

### ✅ 폰트 스케일 강제 규격 (6종 공통)

| 요소 | 크기 |
|------|------|
| H1 | 22px |
| H2 | 18px |
| H3 | 15px |
| 본문 | 14px |
| 표 | 13px |
| line-height | 1.6 |

👉 육안으로 6개 PDF를 나란히 놓았을 때
**같은 템플릿에서 나온 문서처럼 보여야 한다.**

---

### ✅ 페이지 구조 규칙

* `<h2>` = 새 페이지 시작
* KPI 카드 영역 → 항상 동일한 위치
* 표 아래 반드시 여백 16px

---

## 3️⃣ 데이터 미연동 전면 수정 (핵심)

### 🔴 현재 문제 패턴 (반드시 제거)

```python
value = module_result.get("npv")
```

```python
value = m5["npv"]
```

```python
if value is None:
    value = "산출 중"
```

---

### ✅ 올바른 단일 규칙 (모든 assembler 공통)

📍 **canonical_summary → resolve_scalar → present**

```python
from app.utils.report_value_resolver import resolve_scalar
from app.utils.present import present_currency, present_percent
```

```python
npv = resolve_scalar(
    canonical_summary["M5"]["summary"].get("npv_public_krw")
)
npv_display = present_currency(npv)
```

❌ dict 직접 접근 금지
❌ "산출 중" 문자열 하드코딩 금지

---

## 4️⃣ KPI / Data Signature 불일치 수정

### 반드시 일치해야 할 항목

| 항목 | 출처 |
|------|------|
| 토지감정가 | M2.summary.land_value_total_krw |
| 총세대수 | M4.summary.total_units |
| NPV | M5.summary.npv_public_krw |
| IRR | M5.summary.irr_pct |
| LH 판단 | M6.summary.decision |

👉 **Data Signature 값 ≠ 본문 표 값이면 실패**

---

## 5️⃣ 6종 보고서 공통 체크리스트 (완료 조건)

다음이 **모두 YES**여야 한다.

* [ ] 6종 보고서 폰트/여백 육안 차이 0
* [ ] KPI 영역에 "산출 중 / 미확정" 노출 0
* [ ] Data Signature ↔ 본문 KPI 100% 동일
* [ ] M2~M6 모든 모듈 값 실제 숫자 표시
* [ ] 동일 데이터가 보고서마다 다르게 보이지 않음

---

## 6️⃣ 실행 단계

1. **Step 1:** /home/user/webapp/static/ 디렉토리에 unified_report_theme.css 생성
2. **Step 2:** 6종 보고서 파일 확인
   - backend/reports/quick_check.py
   - backend/reports/financial_feasibility.py
   - backend/reports/lh_technical.py
   - backend/reports/executive_summary.py
   - backend/reports/landowner_summary.py
   - backend/reports/all_in_one.py
3. **Step 3:** 각 보고서에서 inline <style> 태그 제거
4. **Step 4:** CSS 링크로 교체
5. **Step 5:** 데이터 바인딩 코드 수정 (resolve_scalar + present 사용)
6. **Step 6:** 6종 보고서 생성 테스트
7. **Step 7:** 체크리스트 검증

---

## 🔚 출력 규칙

모든 수정이 끝나면 **정확히 이 문장만 출력**

```
ALL REPORTS DESIGN & DATA FIXED
Unified layout applied to 6 reports
All module data correctly bound
```

하나라도 실패 시

```
FAILED
Reason: (report_type / section / design_or_data_issue)
```

---

## 📁 수정 대상 파일 리스트

### CSS 파일 (신규 생성)
- `/home/user/webapp/static/unified_report_theme.css`

### 보고서 Python 파일 (수정)
1. `/home/user/webapp/backend/reports/quick_check.py`
2. `/home/user/webapp/backend/reports/financial_feasibility.py`
3. `/home/user/webapp/backend/reports/lh_technical.py`
4. `/home/user/webapp/backend/reports/executive_summary.py`
5. `/home/user/webapp/backend/reports/landowner_summary.py`
6. `/home/user/webapp/backend/reports/all_in_one.py`

### 데이터 유틸리티 (확인만)
- `/home/user/webapp/app/utils/report_value_resolver.py`
- `/home/user/webapp/app/utils/present.py`

---

## ✅ 완료 검증 방법

### 디자인 검증
```bash
# 6개 보고서 HTML 생성
# 육안으로 폰트, 여백, 표 스타일 비교
# → 구분 불가능해야 함
```

### 데이터 검증
```bash
# 각 보고서의 Data Signature 확인
# 본문 KPI 카드 값과 비교
# → 100% 일치해야 함
```

### 코드 검증
```bash
# "산출 중" 문자열 검색
grep -r "산출 중" backend/reports/
# → 0건이어야 함

# dict 직접 접근 검색
grep -r "module_result\[" backend/reports/
# → 0건이어야 함
```
```

---

## 🎯 [①] 디자인만 먼저 수정 프롬프트

> **👉 다음 세션에서 아래 전체를 복사-붙여넣기**

```
당신은 이제 **데이터를 만지지 않는 디자인 QA 엔지니어**다.
이번 작업의 목적은 단 하나다.

> **6종 보고서의 폰트·레이아웃·여백을
> 완전히 동일한 '하나의 보고서 템플릿'처럼 보이게 만든다.**

---

## 🔒 절대 금지

* canonical_summary
* 계산 로직
* resolve_scalar / present 함수
* 데이터 바인딩 코드
* KPI 값

👉 **CSS / HTML 구조 / 여백 / 태그만 수정 허용**

---

## 1️⃣ 단일 CSS 강제 적용

📍 모든 보고서 HTML `<head>`에 **아래 1줄만 존재**

```html
<link rel="stylesheet" href="/static/unified_report_theme.css">
```

❌ report별 `<style>` 전부 제거
❌ inline style 전부 제거

---

## 2️⃣ 폰트 & 타이포그래피 고정 규칙

| 요소 | 규격 |
|------|------|
| Font | Noto Sans KR |
| H1 | 22px |
| H2 | 18px |
| H3 | 15px |
| Body | 14px |
| Table | 13px |
| Line-height | 1.6 |

👉 6개 PDF를 나란히 놓았을 때 **구분 불가해야 함**

---

## 3️⃣ 페이지 레이아웃 규칙

* `<h2>` = 새 페이지 시작
* KPI 카드 위치 고정 (상단)
* 표 아래 여백 `margin-bottom: 16px`
* 본문 문단 간격 `margin-bottom: 12px`

---

## 4️⃣ 시각 QA 기준

다음 중 하나라도 있으면 실패:

* 보고서마다 제목 크기가 다름
* 어떤 보고서는 답답 / 어떤 보고서는 성긴 느낌
* 표 스타일이 서로 다름
* "웹페이지처럼 보임"

---

## 5️⃣ 실행 단계

1. **Step 1:** unified_report_theme.css 생성
2. **Step 2:** 6종 보고서에서 <style> 태그 모두 제거
3. **Step 3:** CSS 링크 추가
4. **Step 4:** HTML 구조 통일 (h2 페이지 구분, KPI 카드 위치)
5. **Step 5:** 6종 보고서 생성 후 육안 비교

---

## 🔚 출력 규칙

성공 시

```
DESIGN UNIFICATION COMPLETE
All 6 reports share identical layout and typography
```

실패 시

```
FAILED
Reason: (report_type / font_or_layout_issue)
```
```

---

## 🎯 [②] 데이터 연동만 수정 프롬프트

> **👉 다음 세션에서 아래 전체를 복사-붙여넣기**

```
당신은 이제 **디자인을 만지지 않는 데이터 바인딩 QA 엔지니어**다.
이번 작업의 목적은 다음 하나다.

> **M2~M6 모든 모듈 데이터가
> 실제 canonical_summary 값으로 100% 표시되도록 만든다.**

---

## 🔒 절대 금지

* CSS / 레이아웃 / HTML 구조
* 문단 텍스트
* 계산 로직
* canonical_summary 생성 방식

👉 **허용 범위: 값 가져오는 부분만**

---

## 1️⃣ 전면 금지 패턴

```python
module.get("value")
m5["npv"]
value or "산출 중"
```

---

## 2️⃣ 유일하게 허용되는 접근 방식

```python
from app.utils.report_value_resolver import resolve_scalar
from app.utils.present import present_currency, present_percent
```

```python
npv = resolve_scalar(
    canonical_summary["M5"]["summary"].get("npv_public_krw")
)
npv_display = present_currency(npv)
```

❌ dict 직접 출력 금지
❌ 문자열 "산출 중" 하드코딩 금지

---

## 3️⃣ 반드시 연결되어야 할 핵심 데이터

| 항목 | canonical_summary 경로 |
|------|------------------------|
| 토지감정가 | M2.summary.land_value_total_krw |
| 총세대수 | M4.summary.total_units |
| NPV | M5.summary.npv_public_krw |
| IRR | M5.summary.irr_pct |
| LH 판단 | M6.summary.decision |

👉 Data Signature 값 = 본문 KPI 값 = 카드 KPI 값
(하나라도 다르면 실패)

---

## 4️⃣ 확인 방법

* 6종 보고서 모두:
  * "산출 중" / None / null → **0건**
  * 숫자 KPI 천단위 콤마 적용
  * 보고서 간 동일 수치 일치

---

## 5️⃣ 실행 단계

1. **Step 1:** 6종 보고서 코드에서 데이터 접근 부분 찾기
2. **Step 2:** dict 직접 접근을 resolve_scalar로 교체
3. **Step 3:** present_currency/present_percent로 포맷팅
4. **Step 4:** "산출 중" 하드코딩 제거
5. **Step 5:** Data Signature ↔ 본문 KPI 값 일치 확인

---

## 🔚 출력 규칙

성공 시

```
DATA BINDING COMPLETE
All M2–M6 module values correctly resolved
```

실패 시

```
FAILED
Reason: (report_type / module / missing_or_mismatched_value)
```
```

---

## 📋 [③] LH 제출용 최종 검수 체크리스트

> **사람이 육안으로 확인하는 기준**

### 📄 전체 인상

* [ ] 웹페이지처럼 보이지 않는다
* [ ] 공공기관 보고서 느낌이다
* [ ] 한 회사, 한 템플릿처럼 보인다

---

### 🔠 폰트·가독성

* [ ] 제목이 크지만 과하지 않다
* [ ] 본문이 빽빽하지 않고 읽기 편하다
* [ ] 줄 간격이 안정적이다

---

### 📊 표·KPI

* [ ] 모든 숫자가 한눈에 들어온다
* [ ] "산출 중 / 미확정" 없음
* [ ] 표 아래 충분한 여백이 있다

---

### 📑 구조

* [ ] 페이지 시작이 명확하다
* [ ] 섹션 흐름이 자연스럽다
* [ ] 중간에 갑자기 끝난 느낌 없음

---

### 🚫 즉시 탈락 사유

* [ ] `{}` 가 보인다
* [ ] `_module_id` 같은 내부 코드 노출
* [ ] 보고서마다 디자인이 다르다
* [ ] 모바일 화면처럼 압축돼 있다

---

### 🎯 최종 합격 기준

> **"LH 실무자가 출력해서 결재선에 올려도
> 부끄럽지 않은가?"**

YES → 통과  
NO → 수정 필요

---

## 🚀 다음 세션 사용 방법

### 1단계: 프롬프트 선택
위의 3가지 옵션 중 하나를 선택:
- **[통합]** - 디자인+데이터 한 번에
- **[①디자인만]** - 레이아웃 우선
- **[②데이터만]** - 값 연동 우선

### 2단계: 복사-붙여넣기
선택한 프롬프트의 내용 전체를 다음 세션 첫 메시지로 붙여넣기

### 3단계: 실행 대기
시스템이 자동으로:
1. 파일 읽기
2. 문제 진단
3. 수정 실행
4. 검증
5. 결과 출력

### 4단계: 검증
출력된 결과에 따라:
- **SUCCESS** → Git commit & PR update
- **FAILED** → 원인 확인 후 재실행

---

## 📚 참고 문서

### 관련 파일
- 이 문서: `/home/user/webapp/FIX_REPORTS_DESIGN_DATA_NEXT_SESSION.md`
- 보고서 구현: `/home/user/webapp/backend/reports/`
- 유틸리티: `/home/user/webapp/app/utils/`

### 기존 문서
- `ALL_IN_ONE_IMPLEMENTATION_COMPLETE.md` - all_in_one 완료 상태
- `SESSION_COMPLETE_SUMMARY.md` - 이전 세션 요약
- `canonical_summary_structure.txt` - 데이터 구조

---

## ⚠️ 주의사항

### 수정 금지 영역
- **계산 엔진:** M2-M6 모듈의 계산 로직
- **API 라우팅:** 엔드포인트 정의
- **데이터 생성:** canonical_summary 생성 과정
- **유틸리티 내부:** resolve_scalar, present 함수 내부 구현

### 수정 허용 영역
- **CSS 스타일:** 폰트, 레이아웃, 여백
- **HTML 구조:** 태그, 클래스, 구조
- **데이터 접근:** canonical_summary에서 값 가져오는 방식
- **포맷팅:** present 함수 호출 방식

---

## 🎯 예상 결과

### 디자인 통합 후
- 6개 PDF를 나란히 놓았을 때 구분 불가
- 동일한 폰트 크기, 여백, 표 스타일
- 전문적인 보고서 느낌

### 데이터 연동 후
- "산출 중" / "미확정" 완전 제거
- 모든 KPI 실제 숫자 표시
- Data Signature ↔ 본문 KPI 100% 일치

### 최종 상태
- LH 제출 가능한 품질
- 6종 보고서 일관성 확보
- 데이터 신뢰성 확보

---

**작성일:** 2025-12-25  
**상태:** ✅ READY FOR NEXT SESSION  
**사용 준비:** 완료

---

**END OF DOCUMENT**
