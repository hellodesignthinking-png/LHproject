# ✅ 6종 보고서 수정 가이드 준비 완료

**날짜:** 2025-12-25  
**목적:** 다음 세션에서 6종 보고서 디자인·데이터 문제 즉시 수정  
**상태:** ✅ READY - 복사-붙여넣기 가능

---

## 📋 준비된 것

### 1. 실행 가능한 3가지 프롬프트
- **[통합]** 디자인 + 데이터 동시 수정
- **[①디자인만]** 레이아웃 통일 우선
- **[②데이터만]** 값 연동 우선

### 2. 상세 실행 가이드
- 수정 범위 명확화
- 금지 사항 명시
- 단계별 실행 절차
- 검증 방법

### 3. 문서화
- **메인 문서:** `FIX_REPORTS_DESIGN_DATA_NEXT_SESSION.md` (9.8KB)
- Git 커밋 완료: `3c8207c`
- Push 완료: `feature/expert-report-generator`

---

## 🎯 식별된 문제점

### 디자인 불일치 문제
1. **폰트 크기 불일치**
   - 6종 보고서별로 H1/H2/H3 크기 제각각
   - 일관성 없는 line-height
   - 표 폰트 크기 차이

2. **레이아웃 불일치**
   - 여백이 보고서마다 다름
   - 표 스타일 불일치
   - 페이지 구분이 명확하지 않음

3. **시각적 품질**
   - 일부 보고서는 웹페이지처럼 보임
   - 같은 회사 문서로 보이지 않음
   - 전문성 부족

### 데이터 연동 문제
1. **"산출 중" 노출**
   - KPI 영역에 "산출 중" 문자열
   - "미확정", "None" 표시
   - 빈 값 처리 미흡

2. **데이터 불일치**
   - Data Signature ≠ 본문 KPI
   - 보고서 간 동일 수치가 다름
   - canonical_summary 미사용

3. **잘못된 접근 패턴**
   - dict 직접 접근 (`m5["npv"]`)
   - resolve_scalar 미사용
   - present 함수 미사용

---

## 📁 준비된 파일

### 실행 가이드
```
/home/user/webapp/FIX_REPORTS_DESIGN_DATA_NEXT_SESSION.md
```

**내용:**
- 3가지 실행 프롬프트 (복사-붙여넣기 가능)
- 문제 진단 요약
- 수정 범위 정의
- 단계별 실행 가이드
- 검증 체크리스트
- 예상 결과

**크기:** 9,834 bytes  
**섹션:**
- 현재 상태 요약
- [통합] 프롬프트 (디자인+데이터)
- [①] 디자인만 프롬프트
- [②] 데이터만 프롬프트
- [③] LH 제출 체크리스트
- 사용 방법
- 참고 문서

---

## 🔧 수정 계획

### Phase 1: CSS 통합 (디자인)
**생성 파일:**
- `/home/user/webapp/static/unified_report_theme.css`

**수정 파일:**
- `backend/reports/quick_check.py`
- `backend/reports/financial_feasibility.py`
- `backend/reports/lh_technical.py`
- `backend/reports/executive_summary.py`
- `backend/reports/landowner_summary.py`
- `backend/reports/all_in_one.py`

**수정 내용:**
- inline `<style>` 태그 제거
- CSS 링크로 교체
- HTML 구조 통일

### Phase 2: 데이터 바인딩 (데이터)
**수정 파일:** (Phase 1과 동일)

**수정 내용:**
- dict 직접 접근 → resolve_scalar
- "산출 중" 하드코딩 제거
- present 함수 사용
- Data Signature 일치 확인

---

## 🎯 목표 상태

### 디자인 목표
- ✅ 6개 PDF 나란히 놓았을 때 구분 불가
- ✅ 동일한 폰트, 여백, 표 스타일
- ✅ 전문적인 공공기관 보고서 느낌
- ✅ LH 제출 가능한 품질

### 데이터 목표
- ✅ "산출 중" / "미확정" 완전 제거
- ✅ 모든 KPI 실제 숫자 표시
- ✅ Data Signature ↔ 본문 100% 일치
- ✅ 보고서 간 수치 일관성

---

## 🚀 다음 세션 실행 방법

### Step 1: 문서 읽기
다음 세션 시작 시 아래 명령으로 가이드 확인:
```bash
cat /home/user/webapp/FIX_REPORTS_DESIGN_DATA_NEXT_SESSION.md
```

### Step 2: 프롬프트 선택
3가지 옵션 중 선택:

| 옵션 | 추천 상황 | 소요 시간 |
|------|----------|----------|
| **[통합]** | 한 번에 해결하고 싶을 때 | 중간 |
| **[①디자인만]** | 레이아웃부터 정리 | 짧음 |
| **[②데이터만]** | 값 연동부터 해결 | 짧음 |

### Step 3: 복사-붙여넣기
선택한 프롬프트를 **전체 복사**하여 다음 세션 첫 메시지로 붙여넣기

### Step 4: 자동 실행
시스템이 자동으로:
1. 현재 파일 분석
2. 문제점 진단
3. 수정 실행
4. 검증
5. 결과 출력

### Step 5: 검증 및 커밋
- 성공 시: Git commit & PR update
- 실패 시: 원인 확인 후 재실행

---

## 📊 수정 규격 요약

### CSS 규격 (6종 공통)
```css
h1 { font-size: 22px; }
h2 { font-size: 18px; }
h3 { font-size: 15px; }
body { font-size: 14px; line-height: 1.6; }
table { font-size: 13px; }
```

### 데이터 접근 규격 (필수 패턴)
```python
# ❌ 금지
value = m5["npv"]
value = module_result.get("npv")
value = value or "산출 중"

# ✅ 필수
from app.utils.report_value_resolver import resolve_scalar
from app.utils.present import present_currency

npv = resolve_scalar(
    canonical_summary["M5"]["summary"].get("npv_public_krw")
)
npv_display = present_currency(npv)
```

---

## ✅ 완료 검증 기준

### 디자인 검증
```bash
# 6개 보고서 HTML 생성 후 육안 비교
# → 폰트, 여백, 표 스타일 구분 불가능해야 함
```

### 데이터 검증
```bash
# "산출 중" 검색
grep -r "산출 중" backend/reports/
# → 0건

# dict 직접 접근 검색
grep -r "\[\"" backend/reports/*.py | grep -v "canonical_summary"
# → 0건
```

### 일치성 검증
```bash
# 각 보고서의 Data Signature 확인
# 본문 KPI 값과 비교
# → 100% 일치
```

---

## 🔗 관련 문서

### 준비 문서
- `FIX_REPORTS_DESIGN_DATA_NEXT_SESSION.md` - 실행 가이드 (메인)
- `REPORT_FIX_PREPARATION_COMPLETE.md` - 이 문서

### 기존 구현 문서
- `ALL_IN_ONE_IMPLEMENTATION_COMPLETE.md` - all_in_one 완료
- `SESSION_COMPLETE_SUMMARY.md` - 이전 세션 요약
- `canonical_summary_structure.txt` - 데이터 구조
- `canonical_summary_raw.json` - 샘플 데이터

### Git 정보
- **Branch:** `feature/expert-report-generator`
- **Latest Commit:** `3c8207c`
- **PR:** #11
- **Status:** OPEN

---

## 📈 예상 효과

### Before (현재)
- ❌ 6종 보고서 스타일 제각각
- ❌ "산출 중" / "None" 노출
- ❌ Data Signature ≠ 본문 KPI
- ❌ 웹페이지처럼 보임

### After (수정 후)
- ✅ 6종 보고서 완벽한 일관성
- ✅ 모든 KPI 실제 값 표시
- ✅ Data Signature = 본문 KPI
- ✅ 전문 보고서 품질

---

## ⚠️ 중요 주의사항

### 절대 수정 금지
- ❌ M2-M6 계산 엔진 로직
- ❌ canonical_summary 생성 구조
- ❌ API 라우팅/엔드포인트
- ❌ resolve_scalar/present 함수 내부

### 수정 허용 범위
- ✅ CSS 스타일시트
- ✅ HTML 구조/태그
- ✅ 데이터 접근 패턴
- ✅ 포맷팅 함수 호출

---

## 🎓 핵심 원칙

### 디자인 원칙
1. **단일 CSS 원칙:** 모든 보고서 → unified_report_theme.css
2. **폰트 고정 원칙:** H1:22px, H2:18px, H3:15px
3. **여백 통일 원칙:** 표 아래 16px, 문단 간 12px

### 데이터 원칙
1. **단일 소스 원칙:** canonical_summary만 사용
2. **안전 접근 원칙:** resolve_scalar 필수
3. **표준 포맷 원칙:** present 함수 필수
4. **일치성 원칙:** Signature = 본문 = 카드

---

## 🎯 성공 기준

### 최종 목표
> **"LH 실무자가 출력해서 결재선에 올려도
> 부끄럽지 않은 6종 보고서"**

### 구체적 기준
- [ ] 6개 PDF 육안 구분 불가
- [ ] "산출 중" 완전 제거
- [ ] Data Signature 100% 일치
- [ ] 전문적인 공공기관 보고서 품질
- [ ] LH 제출 가능한 완성도

---

## 📞 다음 세션 체크리스트

### 세션 시작 전
- [ ] 이 문서 읽기 (`REPORT_FIX_PREPARATION_COMPLETE.md`)
- [ ] 메인 가이드 확인 (`FIX_REPORTS_DESIGN_DATA_NEXT_SESSION.md`)
- [ ] 수정할 프롬프트 선택 (통합/①/②)

### 세션 중
- [ ] 선택한 프롬프트 전체 복사-붙여넣기
- [ ] 자동 실행 진행 상황 확인
- [ ] 오류 발생 시 즉시 대응

### 세션 종료 시
- [ ] 검증 체크리스트 확인
- [ ] Git commit 완료
- [ ] PR update 완료
- [ ] 결과 문서화

---

## 🎉 준비 완료

### 현재 상태: ✅ READY

모든 준비가 완료되었습니다:
- ✅ 문제점 식별 완료
- ✅ 수정 계획 수립 완료
- ✅ 실행 가이드 작성 완료
- ✅ 프롬프트 3종 준비 완료
- ✅ Git commit & push 완료

### 다음 단계
다음 세션에서:
1. `FIX_REPORTS_DESIGN_DATA_NEXT_SESSION.md` 읽기
2. 프롬프트 선택 (통합/①/②)
3. 복사-붙여넣기
4. 자동 실행
5. 검증 및 커밋

---

**준비 완료일:** 2025-12-25  
**문서 위치:** `/home/user/webapp/REPORT_FIX_PREPARATION_COMPLETE.md`  
**메인 가이드:** `/home/user/webapp/FIX_REPORTS_DESIGN_DATA_NEXT_SESSION.md`  
**Git Commit:** `3c8207c`  
**상태:** ✅ **READY FOR NEXT SESSION**

---

**END OF PREPARATION DOCUMENT**
