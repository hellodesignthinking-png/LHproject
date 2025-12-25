# 다음 세션 시작 가이드

## 📋 세션 목표
**all_in_one 보고서를 실제 PDF 기준 50페이지로 완성**

---

## ✅ 완료된 준비 작업

### 1. 디렉토리 구조
```
backend/reports/
├── __init__.py
├── quick_check.py          ✅ 빠른 검토 보고서
├── financial_feasibility.py ✅ 재무 타당성 보고서
├── lh_technical.py          ✅ LH 기술 심사 보고서
├── executive_summary.py     ✅ 경영진 요약 보고서
├── landowner_summary.py     ✅ 토지주 요약 보고서
└── all_in_one.py            ✅ 종합 통합 보고서 (기초 구조)
```

### 2. 데이터 구조
- ✅ `canonical_summary_structure.txt` - 표준 데이터 구조 정의
- ✅ `canonical_summary_raw.json` - 샘플 데이터

### 3. 기존 5종 보고서
모든 기본 보고서가 구현되어 있으며, `all_in_one.py`는 이들을 참조하지 않고 독립적으로 작성됨.

---

## 🎯 all_in_one.py 현재 상태

### 구현 완료
- ✅ 기본 HTML 구조
- ✅ CSS 스타일 (인쇄 최적화 포함)
- ✅ Section 1: Executive Summary (3페이지 분량)
  - 프로젝트 개요
  - 핵심 재무 지표
  - LH 심사 적격성
  - 의사결정 권고

### 구현 대기 (Placeholder)
- ⏳ Section 2: M2 토지 가치 분석 (6페이지)
- ⏳ Section 3: M4 건축·법정 검토 (6페이지)
- ⏳ Section 4: M5 사업성 분석 (10페이지)
- ⏳ Section 5: M6 LH 심사 판단 (6페이지)
- ⏳ Section 6: 이해관계자 분석 (6페이지)
- ⏳ Section 7: 리스크 종합 & 대응 전략 (5페이지)
- ⏳ Section 8: 결론 & Next Steps (4페이지)

**총 목표: 50페이지**

---

## 🚀 다음 세션에서 할 일

### 단계별 구현 순서 (변경 불가)

1. **Section 2: M2 토지 가치 분석 (6페이지)**
   - `_generate_land_value_section()` 함수 구현
   - 개별공시지가, 실거래가, 시장 보정계수 분석
   - 비교 거래 사례 분석
   - 신뢰도 평가

2. **Section 3: M4 건축·법정 검토 (6페이지)**
   - `_generate_building_review_section()` 함수 구현
   - 건폐율·용적률 검토
   - 법적 제약사항 분석
   - 건축 가능 규모 산정

3. **Section 4: M5 사업성 분석 (10페이지)**
   - `_generate_financial_analysis_section()` 함수 구현
   - 사업비 상세 분해
   - 수익 구조 분석
   - 민감도 분석
   - 시나리오 분석

4. **Section 5: M6 LH 심사 판단 (6페이지)**
   - `_generate_lh_evaluation_section()` 함수 구현
   - 세부 심사 기준별 점수
   - 리스크 요인 분석
   - 개선 권고사항

5. **Section 6: 이해관계자 분석 (6페이지)**
   - `_generate_stakeholder_section()` 함수 구현
   - 토지주 관점
   - LH 관점
   - 금융기관 관점

6. **Section 7: 리스크 종합 & 대응 전략 (5페이지)**
   - `_generate_risk_section()` 함수 구현
   - 4대 리스크 종합 평가
   - 완화 전략 상세
   - 모니터링 계획

7. **Section 8: 결론 & Next Steps (4페이지)**
   - `_generate_conclusion_section()` 함수 구현
   - 종합 판단
   - 실행 로드맵
   - 체크리스트

---

## 📝 콘텐츠 작성 규칙

### 필수 준수 사항

1. **모든 숫자 KPI에는 3가지 포함**
   - 수치의 의미
   - LH 내부 기준에서의 해석
   - 리스크 또는 보완 가능성

2. **문체 규칙 (LH 제출 톤)**
   - 판단형·검토형 문장
   - 기준·조건·전제 명확화
   - 감정·마케팅·홍보 표현 금지

3. **페이지 구성**
   - 표만 있는 페이지 금지
   - Bullet-only 페이지 금지
   - 표 : 해석 문단 비율 적절히 유지

4. **데이터 출처**
   - `canonical_summary`에 있는 데이터만 사용
   - 추측이나 가정으로 데이터 생성 금지

---

## 🔒 절대 수정 금지 영역

다음 파일들은 이미 검증 완료되었으므로 **한 줄도 수정 불가**:
- 다른 5종 보고서 파일들
- `canonical_summary_structure.txt`
- `canonical_summary_raw.json`
- CSS 스타일 (all_in_one.py 내)
- Section 1: Executive Summary (이미 구현 완료)

---

## 🎯 완료 판정 기준

다음 조건을 **모두 만족**해야 성공:

1. ✅ all_in_one PDF 단독 50페이지 이상
2. ✅ 모든 핵심 KPI에 해석 문단 존재
3. ✅ LH 실무자가 추가 질문 없이 이해 가능
4. ✅ 외관·톤·밀도 모두 "실제 제출 보고서" 수준
5. ✅ 다른 보고서와 무관하게 단독 완결

---

## 📂 참고 파일 위치

- 구현 대상: `/home/user/webapp/backend/reports/all_in_one.py`
- 데이터 구조: `/home/user/webapp/canonical_summary_structure.txt`
- 샘플 데이터: `/home/user/webapp/canonical_summary_raw.json`
- 현재 문서: `/home/user/webapp/START_NEXT_SESSION.md`

---

## 💡 구현 팁

1. 각 섹션 구현 후 즉시 PDF 미리보기로 페이지 수 확인
2. 표와 해석 문단의 균형 유지
3. LH 톤 일관성 체크
4. canonical_summary 데이터만 사용
5. 모든 숫자에 해석 추가

---

**다음 세션에서는 위 순서대로 Section 2부터 Section 8까지 순차적으로 구현합니다.**
