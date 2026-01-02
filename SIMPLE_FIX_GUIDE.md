# 🔧 간단한 수정 가이드

## 현재 상황

원래 작동하던 시스템이 있습니다 (포트 49999). 하지만:
1. Mock 데이터 사용
2. 일부 보고서 (C, E, F) 500 오류

## 해결 방안

### ✅ 올바른 URL 사용

**원래 서버 (작동함)**:
```
https://49999-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai
```

**주요 페이지**:
- API 문서: https://49999-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/docs
- 대시보드: https://49999-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/dashboard
- 분석 페이지: https://49999-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/analyze

### Mock 데이터 문제

**현재**: `DIRECT_20260102_xxx` RUN_ID는 Mock 데이터를 사용합니다.

**해결책**: 실제 Kakao API 키 적용
1. `.env` 파일 수정:
   ```bash
   KAKAO_REST_API_KEY=실제_API_키
   ```

2. Kakao Developers에서 API 키 발급:
   - https://developers.kakao.com/
   - 애플리케이션 생성
   - REST API 키 복사
   - 로컬 주소 API 활성화

### 보고서 오류 (C, E, F)

**문제**: LH 기술검증 (C), 사전 검토 (E), 프레젠테이션 (F) 보고서가 500 오류

**원인**: 템플릿 파일 누락 또는 데이터 형식 불일치

**임시 해결책**: 보고서 A, B, D만 사용
- A. 종합 최종보고서 ✅
- B. 토지주 제출용 ✅
- D. 사업성 투자검토 ✅

## 🚀 즉시 사용 가능한 방법

### 1. 주소 분석 시작

```
https://49999-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/analyze
```

1. 주소 입력
2. "직접 입력" 또는 "주소 검색" 선택
3. 분석 시작
4. RUN_ID 생성 (DIRECT_20260102_xxx)
5. 자동으로 대시보드 이동

### 2. 대시보드에서 보고서 확인

- 보고서 A (종합) ✅
- 보고서 B (토지주용) ✅
- 보고서 D (사업성) ✅

**주의**: C, E, F는 현재 오류 발생 (템플릿 수정 필요)

### 3. API 직접 호출

```bash
# 주소 분석
curl -X POST "https://49999-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/m1/analyze-direct" \
  -H "Content-Type: application/json" \
  -H "X-User-Email: admin@zerosite.com" \
  -d '{"address":"서울특별시 강남구 테헤란로 152"}'

# 보고서 A 조회
curl "https://49999-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/reports/six-types/A/html?context_id=DIRECT_20260102_xxx" \
  -H "X-User-Email: admin@zerosite.com"
```

## 📊 예상 플로우

```
사용자 → /analyze
       ↓
주소 입력: "서울특별시 강남구 테헤란로 152"
       ↓
POST /api/m1/analyze-direct
       ↓
RUN_ID 생성: DIRECT_20260102_9fd236ae
       ↓
자동 이동: /dashboard?run_id=DIRECT_20260102_9fd236ae
       ↓
보고서 A, B, D 사용 가능 ✅
보고서 C, E, F는 오류 ⚠️
```

## 🔧 보고서 C, E, F 수정 (선택)

보고서 템플릿이 없거나 손상되었습니다. 수정 방법:

1. 템플릿 확인:
   ```bash
   ls -la app/templates_v13/
   ```

2. 누락된 템플릿 생성:
   - `lh_technical_report.html` (C)
   - `quick_review_report.html` (E)
   - `presentation_report.html` (F)

3. 또는 간단히 A, B, D만 사용

## 🎯 권장 사항

**지금 즉시 사용**:
1. https://49999-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/analyze 접속
2. 주소 입력하여 분석
3. 보고서 A, B, D 확인 (작동함)

**나중에 개선**:
1. Kakao API 키 적용 (Mock 제거)
2. 보고서 C, E, F 템플릿 수정
3. 외부 API 연동 (VWorld, Data.go.kr)

---

**핵심**: 원래 서버 (포트 49999)를 사용하면 기본 기능은 작동합니다!
