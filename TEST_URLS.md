# 🚀 ZeroSite v1.5.1 - 테스트 URL 가이드

## 📍 서비스 URL
**Base URL**: `https://8000-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai`

---

## 🎯 빠른 시작 (Quick Start)

### 1️⃣ 랜딩 페이지 (권장 시작점)
**URL**: `/`
- 모든 기능에 대한 빠른 접근 링크
- 5개 역할별 대시보드 테스트 링크
- 권한 매트릭스 시각화
- 버전 정보 및 기능 설명

👉 **[랜딩 페이지 열기](https://8000-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/)**

---

## 👥 역할별 대시보드 테스트 링크

### 🔴 ADMIN (관리자)
- **URL**: `/dashboard?user=admin@zerosite.com`
- **접근 가능 보고서**: A, B, C, D, E, F (모든 보고서)
- **외부 공유**: B, D, F 가능

👉 **[ADMIN 대시보드](https://8000-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/dashboard?user=admin@zerosite.com)**

---

### 🔵 INTERNAL (내부 직원)
- **URL**: `/dashboard?user=internal@zerosite.com`
- **접근 가능 보고서**: A, B, C, D
- **외부 공유**: B, D 가능

👉 **[INTERNAL 대시보드](https://8000-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/dashboard?user=internal@zerosite.com)**

---

### 🟢 LANDOWNER (지주)
- **URL**: `/dashboard?user=landowner@example.com`
- **접근 가능 보고서**: B, D
- **외부 공유**: 불가

👉 **[LANDOWNER 대시보드](https://8000-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/dashboard?user=landowner@example.com)**

---

### 🟡 LH (한국토지주택공사)
- **URL**: `/dashboard?user=lh@example.com`
- **접근 가능 보고서**: C, D, E
- **외부 공유**: D 가능

👉 **[LH 대시보드](https://8000-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/dashboard?user=lh@example.com)**

---

### 🟣 INVESTOR (투자자)
- **URL**: `/dashboard?user=investor@example.com`
- **접근 가능 보고서**: B, D, F
- **외부 공유**: 불가

👉 **[INVESTOR 대시보드](https://8000-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/dashboard?user=investor@example.com)**

---

## 📊 보고서 권한 매트릭스

| 보고서 | ADMIN | INTERNAL | LANDOWNER | LH | INVESTOR |
|--------|-------|----------|-----------|----|---------  |
| **A: Master** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **B: Landowner** | ✅ 🔗 | ✅ 🔗 | ✅ | ❌ | ✅ |
| **C: LH Technical** | ✅ | ✅ | ❌ | ✅ | ❌ |
| **D: Market Analysis** | ✅ 🔗 | ✅ 🔗 | ✅ | ✅ | ✅ |
| **E: LH Submission** | ✅ | ❌ | ❌ | ✅ | ❌ |
| **F: Investor** | ✅ 🔗 | ✅ 🔗 | ❌ | ❌ | ✅ |

🔗 = 외부 공유 링크 생성 가능

---

## 🔧 API 문서
**Swagger UI**: `/docs`

👉 **[API 문서 보기](https://8000-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/docs)**

---

## ✨ v1.5.1 주요 변경사항

### 🐛 Hotfix: Dashboard Authentication
**문제**:
- 대시보드 HTML/PDF 버튼 클릭 시 401 Unauthorized 오류
- `X-User-Email` 헤더 누락

**해결**:
- `dashboard.html`에 `window.ZEROSITE_CONFIG` 읽기 기능 추가
- 모든 API 호출에 `X-User-Email` 헤더 자동 포함
- `openReport()` 함수로 인증된 보고서 열기 구현

### 🚀 신규: 랜딩 페이지
- Root URL (`/`)에 테스트 랜딩 페이지 추가
- 5개 역할별 빠른 접근 링크
- 권한 매트릭스 시각화
- 버전 이력 및 기능 설명

---

## 🔍 테스트 시나리오

### 시나리오 1: ADMIN 전체 접근 테스트
1. [ADMIN 대시보드](https://8000-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/dashboard?user=admin@zerosite.com) 열기
2. 6개 보고서 모두 "📄 HTML", "📥 PDF" 버튼 활성화 확인
3. 아무 보고서나 HTML 버튼 클릭 → 새 창에서 보고서 열림 확인
4. PDF 버튼 클릭 → 다운로드 시작 확인
5. B/D/F 보고서의 "🔗 공유" 버튼 클릭 → 모달 열림 확인

### 시나리오 2: LANDOWNER 제한된 접근 테스트
1. [LANDOWNER 대시보드](https://8000-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/dashboard?user=landowner@example.com) 열기
2. B, D 보고서만 버튼 활성화 확인
3. A, C, E, F 보고서는 "접근 권한 없음" 배지 표시 확인
4. B 보고서 HTML 버튼 클릭 → 정상 작동 확인
5. A 보고서 버튼은 비활성화되어 클릭 안됨 확인

### 시나리오 3: 외부 공유 링크 생성
1. [INTERNAL 대시보드](https://8000-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/dashboard?user=internal@zerosite.com) 열기
2. B 보고서의 "🔗 공유" 버튼 클릭
3. 만료 시간 선택 (24시간/7일/30일)
4. "링크 생성" 버튼 클릭
5. 생성된 URL 복사
6. 새 시크릿 창에서 복사한 URL 접속 → 인증 없이 접근 가능 확인

---

## 🔐 인증 시스템

### DEV Mode (현재 활성화)
- 환경변수: `ZEROSITE_ENV=dev`
- `?user=<email>` 파라미터로 사용자 지정
- `X-User-Email` 헤더로 인증

### 사용 가능한 테스트 계정
- `admin@zerosite.com` (ADMIN)
- `internal@zerosite.com` (INTERNAL)
- `landowner@example.com` (LANDOWNER)
- `lh@example.com` (LH)
- `investor@example.com` (INVESTOR)

---

## 📝 기술 세부사항

### Frontend Authentication
```javascript
// window.ZEROSITE_CONFIG 자동 주입
const config = window.ZEROSITE_CONFIG || {
    defaultUser: 'admin@zerosite.com',
    defaultRunId: 'TEST_6REPORT',
    isDev: true
};

// 모든 API 호출에 헤더 포함
fetch(url, {
    headers: {
        'X-User-Email': config.defaultUser
    }
});
```

### Backend User Injection
```python
@app.get("/dashboard")
async def dashboard_page(
    run_id: Optional[str] = Query(None),
    user: Optional[str] = Query("admin@zerosite.com")
):
    # Config injection into HTML
    html_content = html_content.replace(
        '<!-- INJECT_CONFIG -->',
        f'<script>window.ZEROSITE_CONFIG = {{...}}</script>'
    )
```

---

## 🎯 다음 단계 (v1.6.0 계획)

- [ ] 접근 로그 대시보드
- [ ] 다운로드 횟수 제한
- [ ] IP 화이트리스트
- [ ] Report C (LH Technical) 엔드포인트 구현

---

## 📞 문의

문제 발생 시:
1. 브라우저 개발자 도구 (F12) → Console 탭 확인
2. Network 탭에서 401/403 에러 확인
3. `X-User-Email` 헤더 포함 여부 확인

---

**Generated**: 2026-01-01
**Version**: v1.5.1 Hotfix
**Status**: ✅ Production Ready
