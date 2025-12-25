# 📌 최종 실행 프롬프트

## (6종 보고서 디자인 + 데이터 변경 검증 & 마무리)

**다음 세션에서 이 프롬프트 전체를 복사-붙여넣기하세요.**

---

당신은 이제 **6종 보고서를 최종 출고 전 검수·수정하는 QA 책임자**다.
이번 세션의 목적은 단 하나다.

> **"6종 보고서가 LH 제출 기준을 충족하는지 최종 확인하고,
> 부족한 부분을 정확히 수정한 뒤 출고 가능 상태로 만든다."**

---

## 🔒 절대 금지 (위반 시 실패)

* canonical_summary 구조 변경 ❌
* 계산 로직 / 엔진 수정 ❌
* KPI 산식 변경 ❌
* 보고서 내용(문장) 대량 추가 ❌

👉 **허용 범위는 오직**

* 디자인(CSS/HTML)
* 데이터 바인딩(resolve_scalar / present 적용 여부)
* 누락된 연결 수정

---

## 🎯 이번 세션의 최종 목표

```
6종 보고서 모두
- 디자인 완전 통일
- 데이터 100% 실연동
- LH 제출 품질 충족
```

---

## 1️⃣ 디자인 최종 검증 & 수정

### 반드시 만족해야 할 조건

* 모든 보고서가 `/static/unified_report_theme.css` **단일 CSS만 사용**
* inline style = **0건**
* report별 `<style>` 태그 = **0건**

### 폰트·사이즈 기준 (하나라도 다르면 실패)

| 항목          | 기준           |
| ----------- | ------------ |
| Font        | Noto Sans KR |
| H1          | 22px         |
| H2          | 18px         |
| H3          | 15px         |
| Body        | 14px         |
| Table       | 13px         |
| Line-height | 1.6          |

👉 **6개 PDF를 나란히 놓았을 때 구분 불가해야 한다**

---

## 2️⃣ 데이터 연동 최종 검증 (M2~M6)

### ❌ 전면 금지 패턴

```python
m5["npv"]
value or "산출 중"
dict.get("value")
```

### ✅ 유일 허용 패턴

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

---

### 반드시 값이 나와야 하는 항목

| 항목    | 값              |
| ----- | -------------- |
| 토지감정가 | 1,621,848,717원 |
| 총세대수  | 26세대           |
| NPV   | 793,000,000원   |
| IRR   | 12.81%         |
| LH 판단 | 적합             |

👉 **카드 / 본문 표 / Data Signature 값이 100% 동일해야 함**

---

## 3️⃣ 6종 보고서 개별 체크 (필수)

각 보고서에 대해 다음을 확인한다.

### 공통 체크

* `{}` 출력 ❌
* None / null / "산출 중" ❌
* 내부 키(_module_id 등) 노출 ❌

### 보고서별 핵심 확인

* **빠른 검토용** → KPI 4종 모두 표시
* **사업성 중심** → NPV·IRR 표 + 설명 정상
* **LH 기술검토** → 총세대수·법정수치 누락 없음
* **경영진용** → 숫자 + 판단 문장 연결
* **토지주용** → 금액·일정이 추상적이지 않음
* **전체 통합** → 모든 모듈 값 한 번 이상 등장

---

## 4️⃣ 최종 합격 기준 (LH 기준)

다음 질문에 **모두 YES**면 통과다.

* 이 PDF를 출력해서 바로 결재선에 올릴 수 있는가?
* 웹페이지처럼 보이지 않는가?
* "왜 이 결론인지" 숫자만 보고 이해 가능한가?
* 보고서마다 톤·디자인이 달라 보이지 않는가?

---

## 5️⃣ 실행 단계

### Step 1: 현재 상태 파악
```bash
# 6종 보고서 파일 확인
ls -la backend/reports/

# CSS 파일 확인
ls -la static/unified_report_theme.css

# 데이터 유틸리티 확인
ls -la app/utils/report_value_resolver.py
ls -la app/utils/present.py
```

### Step 2: 디자인 통합
1. unified_report_theme.css 생성 (없으면)
2. 6개 보고서에서 inline style 제거
3. CSS 링크로 교체

### Step 3: 데이터 바인딩 수정
1. dict 직접 접근 찾기
2. resolve_scalar + present 패턴으로 교체
3. "산출 중" 하드코딩 제거

### Step 4: 검증
1. 6종 보고서 생성 테스트
2. 디자인 통일성 확인
3. 데이터 값 일치성 확인
4. 육안 체크리스트 확인

### Step 5: 커밋
```bash
git add .
git commit -m "fix: Unify 6 reports design and fix data binding"
git push origin feature/expert-report-generator
```

---

## 🔚 출력 규칙

모든 조건 충족 시 **정확히 이 문장만 출력**

```
FINAL 6 REPORTS VERIFIED
Design unified, data bound correctly
Ready for LH submission
```

하나라도 실패 시

```
FAILED
Reason: (report_type / design_or_data_issue)
```

---

## 🔍 추가: 사람이 직접 보는 **최종 육안 체크 10초 리스트**

* [ ] 6개 PDF 제목 크기 동일
* [ ] 표 스타일 100% 동일
* [ ] 숫자에 콤마 있음
* [ ] "산출 중" 검색 → 0건
* [ ] 웹페이지 느낌 없음

---

## 📋 수정 대상 파일

### CSS (생성 또는 확인)
- `/home/user/webapp/static/unified_report_theme.css`

### 6종 보고서 (수정)
1. `/home/user/webapp/backend/reports/quick_check.py`
2. `/home/user/webapp/backend/reports/financial_feasibility.py`
3. `/home/user/webapp/backend/reports/lh_technical.py`
4. `/home/user/webapp/backend/reports/executive_summary.py`
5. `/home/user/webapp/backend/reports/landowner_summary.py`
6. `/home/user/webapp/backend/reports/all_in_one.py`

### 유틸리티 (확인만)
- `/home/user/webapp/app/utils/report_value_resolver.py`
- `/home/user/webapp/app/utils/present.py`

---

## 🎯 검증 명령어

### 디자인 검증
```bash
# inline style 검색
grep -r "style=" backend/reports/*.py | wc -l
# → 0이어야 함

# <style> 태그 검색
grep -r "<style>" backend/reports/*.py | wc -l
# → 0이어야 함
```

### 데이터 검증
```bash
# "산출 중" 검색
grep -r "산출 중" backend/reports/*.py | wc -l
# → 0이어야 함

# dict 직접 접근 검색
grep -r "\[\"" backend/reports/*.py | grep -v "canonical_summary" | wc -l
# → 0이어야 함
```

### 패턴 검증
```bash
# resolve_scalar 사용 확인
grep -r "resolve_scalar" backend/reports/*.py | wc -l
# → 6개 이상이어야 함

# present 함수 사용 확인
grep -r "present_" backend/reports/*.py | wc -l
# → 12개 이상이어야 함
```

---

## ✅ 완료 후 확인사항

### Git Status
```bash
git status
git log --oneline -3
git diff HEAD~1
```

### Files Changed
- [ ] unified_report_theme.css (created or modified)
- [ ] 6개 보고서 파일 (modified)
- [ ] 커밋 메시지 명확
- [ ] PR 업데이트 완료

---

**작성일:** 2025-12-25  
**사용 방법:** 다음 세션에서 이 프롬프트 전체를 복사-붙여넣기  
**예상 소요 시간:** 30-45분  
**예상 결과:** 6종 보고서 LH 제출 품질 달성

---

**END OF FINAL EXECUTION PROMPT**
