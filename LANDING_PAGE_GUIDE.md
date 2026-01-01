# ZeroSite v1.6.0 - 접속 페이지 완전 가이드

**생성일**: 2026-01-01  
**버전**: v1.6.0  
**상태**: ✅ Production Ready

---

## 📋 목차

1. [개요](#개요)
2. [접속 URL](#접속-url)
3. [주요 기능](#주요-기능)
4. [사용 방법](#사용-방법)
5. [테스트 시나리오](#테스트-시나리오)
6. [API 엔드포인트](#api-엔드포인트)
7. [기술 구현](#기술-구현)

---

## 개요

ZeroSite v1.6.0 접속 페이지는 **모든 기능을 한 곳에서 테스트**할 수 있는 통합 플랫폼입니다.

### 핵심 가치
- 🔍 **주소로 토지 검색**: 실제 주소를 입력하여 RUN_ID 조회
- 📊 **실시간 통계**: 총 RUN_ID 수, 활성 상태, 지역별 분포
- 👥 **역할별 테스트**: 5개 역할(ADMIN, INTERNAL, LANDOWNER, LH, INVESTOR)별 대시보드
- 📈 **접근 로그**: ADMIN 전용 접근 로그 및 통계 대시보드
- 🚀 **즉시 사용**: 별도 설정 없이 바로 테스트 가능

---

## 접속 URL

### Production 환경
```
Base URL: https://8000-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai
Landing Page: https://8000-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/
```

### 주요 페이지
| 페이지 | URL | 설명 |
|-------|-----|------|
| 접속 페이지 | `/` | 메인 랜딩 페이지 (주소 검색 + 통계) |
| ADMIN 대시보드 | `/dashboard?user=admin@zerosite.com` | 모든 보고서 접근 |
| 접근 로그 | `/access-logs?user=admin@zerosite.com` | ADMIN 전용 로그 대시보드 |
| API 문서 | `/docs` | Swagger UI |

---

## 주요 기능

### 1. 🔍 주소 검색 기능

#### 기능 설명
- 주소, RUN_ID, PNU로 토지 검색
- 부분 매칭 지원 (예: "서울", "강남", "TEST")
- 실시간 검색 결과 표시

#### 사용 가능한 검색어 예시
```
✅ 주소: 서울시 강남구, 경기도 성남시, 인천시
✅ RUN_ID: TEST_6REPORT, RUN_20260101_SAMPLE_A
✅ PNU: 1168010100
✅ 키워드: 강남, 서초, 판교
```

#### 검색 결과 표시 정보
- **RUN_ID**: 보고서 식별자
- **주소**: 전체 지번 주소
- **면적**: 토지 면적 (㎡)
- **용도지역**: 제2종일반주거지역 등
- **PNU**: 필지 고유번호

#### 검색 후 액션
- "대시보드 열기" 버튼 클릭 → 해당 RUN_ID의 ADMIN 대시보드로 이동
- 6개 보고서 전체 확인 가능

---

### 2. 📊 실시간 통계 카드

페이지 로드 시 자동으로 표시되는 4개 통계:

| 통계 | 설명 | 데이터 소스 |
|-----|------|-----------|
| **총 RUN_ID** | 전체 RUN_ID 개수 | `/api/v4/run-ids/statistics` |
| **활성 상태** | ACTIVE 상태 RUN_ID 수 | 동일 API |
| **보고서 유형** | 6개 고정 (A~F) | 하드코딩 |
| **사용자 역할** | 5개 고정 | 하드코딩 |

#### 통계 API 응답 예시
```json
{
  "total_count": 5,
  "active_count": 5,
  "by_status": {
    "ACTIVE": 5
  },
  "by_region": {
    "서울시": 2,
    "경기도": 1,
    "인천시": 1,
    "대전시": 1
  },
  "recent": [
    "TEST_6REPORT",
    "RUN_20260101_SAMPLE_A",
    "RUN_20260101_SAMPLE_B",
    "RUN_20260101_SAMPLE_C",
    "RUN_20260101_SAMPLE_D"
  ]
}
```

---

### 3. 👥 역할별 대시보드 바로가기

5개 역할별 빠른 테스트 링크 제공:

#### ADMIN (관리자)
- **권한**: A/B/C/D/E/F (모든 보고서)
- **링크**: `/dashboard?user=admin@zerosite.com`
- **추가 기능**: 접근 로그 대시보드 (`/access-logs`)

#### INTERNAL (내부 직원)
- **권한**: A/B/C/D
- **링크**: `/dashboard?user=internal@zerosite.com`
- **특징**: 외부 공유 가능 (B, D)

#### LANDOWNER (지주)
- **권한**: B/D (제한적)
- **링크**: `/dashboard?user=landowner@example.com`
- **특징**: 본인 관련 보고서만

#### LH (LH 공사)
- **권한**: C/D/E
- **링크**: `/dashboard?user=lh@example.com`
- **특징**: 기술검토 중심

#### INVESTOR (투자자)
- **권한**: B/D/F
- **링크**: `/dashboard?user=investor@example.com`
- **특징**: 투자 분석 중심

---

### 4. 🆕 v1.6.0 신규 기능

#### 접근 로그 대시보드 (ADMIN Only)
- **URL**: `/access-logs?user=admin@zerosite.com`
- **기능**:
  - 실시간 접근 로그
  - 다운로드 횟수 추적
  - 액션별 통계 (HTML 보기, PDF 다운로드, 공유 링크 생성)
  - 보고서 타입별 통계
  - 사용자별 활동 내역

#### 다운로드 제한
- 보고서당 **10회** 다운로드 제한
- 사용자/토큰 단위로 추적
- 초과 시 HTTP 429 응답

#### IP 화이트리스트
- ADMIN만 관리 가능
- 특정 IP에서만 접근 허용
- API를 통한 추가/삭제

#### Report C (LH 기술검토)
- LH 기술검토 보고서 신규 추가
- HTML/PDF 지원
- ADMIN, INTERNAL, LH 역할만 접근

#### RUN_ID 데이터 연동
- Database + DEV 테스트 데이터
- 주소/PNU/RUN_ID 검색
- 통계 및 최근 RUN_ID 조회

---

## 사용 방법

### 방법 1: 주소로 검색하여 보고서 보기

1. 접속 페이지 접속
   ```
   https://8000-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/
   ```

2. 검색창에 주소 입력
   ```
   예시: 서울시 강남구
   예시: TEST
   예시: 경기도
   ```

3. "검색" 버튼 클릭

4. 검색 결과에서 원하는 토지 선택

5. "대시보드 열기" 버튼 클릭

6. 6개 보고서 중 필요한 보고서 HTML/PDF 버튼 클릭

---

### 방법 2: 역할별로 바로 테스트

1. 접속 페이지에서 원하는 역할 카드 선택

2. "대시보드 열기" 버튼 클릭

3. 해당 역할로 대시보드 접속됨

4. 권한이 있는 보고서만 활성화됨

5. HTML/PDF 버튼으로 보고서 확인

---

### 방법 3: 접근 로그 확인 (ADMIN Only)

1. ADMIN 카드에서 "접근 로그 (ADMIN Only)" 버튼 클릭

2. 또는 직접 접속:
   ```
   /access-logs?user=admin@zerosite.com
   ```

3. 실시간 통계 카드 확인:
   - 총 액세스 수
   - 고유 사용자 수
   - HTML 보기 수
   - PDF 다운로드 수

4. 차트 확인:
   - 액션별 분포
   - 보고서 타입별 분포

5. 접근 로그 테이블 확인:
   - 시간, 사용자, 액션, 보고서 타입, 응답 시간

---

## 테스트 시나리오

### Scenario 1: 신규 사용자 온보딩

**목표**: 처음 방문한 사용자가 시스템 이해

1. 접속 페이지 접속
2. 통계 카드 확인 (5개 RUN_ID 존재)
3. "서울" 검색
4. TEST_6REPORT 선택하여 대시보드 열기
5. ADMIN으로 모든 보고서 확인
6. HTML 버튼으로 Report A 보기
7. PDF 버튼으로 Report B 다운로드

**예상 결과**:
- ✅ 검색 결과 2건 (서울시 2개)
- ✅ 대시보드에서 6개 보고서 모두 활성화
- ✅ HTML 새 창에서 열림
- ✅ PDF 파일 다운로드 시작

---

### Scenario 2: 지주(LANDOWNER) 권한 테스트

**목표**: 제한된 권한 확인

1. 접속 페이지에서 LANDOWNER 카드 클릭
2. 대시보드에서 권한 확인
3. Report B (Landowner) HTML 보기
4. Report D (Market Analysis) PDF 다운로드
5. Report A 접근 시도 (비활성화 확인)

**예상 결과**:
- ✅ B, D만 활성화 (나머지는 "접근 불가")
- ✅ HTML/PDF 정상 작동
- ✅ 다른 보고서 버튼 비활성화

---

### Scenario 3: 접근 로그 모니터링 (ADMIN)

**목표**: 시스템 사용 현황 파악

1. ADMIN 대시보드 접속
2. Report A HTML 보기
3. Report B PDF 다운로드
4. 접근 로그 대시보드 접속
5. 방금 전 액션 로그 확인
6. 통계 차트 확인

**예상 결과**:
- ✅ 최근 활동에 2개 로그 추가
- ✅ HTML 보기 수 +1
- ✅ PDF 다운로드 수 +1
- ✅ 차트에 반영됨

---

### Scenario 4: 외부 공유 테스트

**목표**: 비인증 사용자와 안전하게 공유

1. INTERNAL로 대시보드 접속
2. Report B에서 "공유 링크 생성" 클릭
3. 생성된 토큰 URL 복사
4. 익명 창에서 토큰 URL 접속
5. Report B HTML 확인
6. 만료 시간 확인

**예상 결과**:
- ✅ 공유 링크 생성 성공
- ✅ 익명 사용자도 Report B 접근 가능
- ✅ 만료 시간까지만 유효

---

### Scenario 5: 다운로드 제한 테스트

**목표**: 10회 제한 동작 확인

1. ADMIN으로 대시보드 접속
2. Report A PDF를 10번 다운로드
3. 11번째 다운로드 시도

**예상 결과**:
- ✅ 1~10회: 정상 다운로드
- ✅ 11회: HTTP 429 (Too Many Requests)
- ✅ 오류 메시지: "다운로드 횟수 초과"

---

## API 엔드포인트

### RUN_ID 검색 및 조회

#### 1. RUN_ID 검색
```http
GET /api/v4/run-ids/search?q={검색어}
Headers:
  X-User-Email: admin@zerosite.com
```

**응답 예시**:
```json
{
  "run_ids": [
    {
      "run_id": "TEST_6REPORT",
      "address": "서울시 강남구 테헤란로 123",
      "pnu": "1168010100",
      "land_area": 500.0,
      "zone": "제2종일반주거지역",
      "created_at": "2026-01-01T10:00:00",
      "status": "ACTIVE",
      "has_data": true
    }
  ],
  "total_count": 1,
  "page": 1,
  "page_size": 20
}
```

#### 2. RUN_ID 통계
```http
GET /api/v4/run-ids/statistics
Headers:
  X-User-Email: admin@zerosite.com
```

**응답 예시**:
```json
{
  "total_count": 5,
  "active_count": 5,
  "by_status": {
    "ACTIVE": 5
  },
  "by_region": {
    "서울시": 2,
    "경기도": 1,
    "인천시": 1,
    "대전시": 1
  },
  "recent": [
    "TEST_6REPORT",
    "RUN_20260101_SAMPLE_A"
  ]
}
```

#### 3. RUN_ID 목록 조회
```http
GET /api/v4/run-ids/list?page=1&page_size=20
Headers:
  X-User-Email: admin@zerosite.com
```

#### 4. 특정 RUN_ID 조회
```http
GET /api/v4/run-ids/{run_id}
Headers:
  X-User-Email: admin@zerosite.com
```

---

### 접근 로그 API

#### 1. 접근 로그 조회
```http
GET /api/v4/access-logs/logs?limit=50
Headers:
  X-User-Email: admin@zerosite.com
```

#### 2. 접근 통계
```http
GET /api/v4/access-logs/statistics
Headers:
  X-User-Email: admin@zerosite.com
```

#### 3. 다운로드 제한 확인
```http
GET /api/v4/access-logs/download-limit
Headers:
  X-User-Email: admin@zerosite.com
```

#### 4. 최근 활동
```http
GET /api/v4/access-logs/recent-activity?limit=10
Headers:
  X-User-Email: admin@zerosite.com
```

---

## 기술 구현

### Frontend 구조

```javascript
// DEV 모드 헤더 자동 추가
const DEV_HEADERS = {
    'X-User-Email': 'admin@zerosite.com',
    'Content-Type': 'application/json'
};

// 통계 로드
async function loadStatistics() {
    const response = await fetch('/api/v4/run-ids/statistics', {
        headers: DEV_HEADERS
    });
    const stats = await response.json();
    // DOM 업데이트
}

// 검색
async function searchLand() {
    const query = document.getElementById('searchInput').value.trim();
    const response = await fetch(`/api/v4/run-ids/search?q=${encodeURIComponent(query)}`, {
        headers: DEV_HEADERS
    });
    const data = await response.json();
    // 결과 표시
}
```

### Backend 서비스

#### RunIdDataService
```python
class RunIdDataService:
    """RUN_ID 데이터 통합 서비스"""
    
    def get_all_run_ids(self, status=None, limit=100):
        """모든 RUN_ID 조회"""
        # 1. Database 조회
        # 2. DEV 테스트 데이터 추가
        # 3. 중복 제거 및 정렬
        pass
    
    def search_run_ids(self, query, limit=20):
        """RUN_ID 검색 (주소/PNU/RUN_ID)"""
        # 부분 매칭 지원
        pass
```

### 데이터 소스

1. **Database (ContextSnapshot)**
   - 실제 저장된 RUN_ID
   - context_data에서 주소/PNU/면적 추출

2. **DEV 테스트 데이터**
   - TEST_6REPORT
   - RUN_20260101_SAMPLE_A
   - RUN_20260101_SAMPLE_B
   - RUN_20260101_SAMPLE_C
   - RUN_20260101_SAMPLE_D

3. **Redis Cache (향후)**
   - 성능 최적화
   - TTL 기반 캐싱

---

## 다음 단계 (v1.7.0 계획)

### 1. 주소 자동완성
- Kakao/Naver 주소 API 연동
- 실시간 주소 제안

### 2. 지도 뷰
- 검색 결과를 지도에 표시
- 클러스터링 지원

### 3. 고급 필터
- 면적 범위 필터
- 용도지역 필터
- 날짜 범위 필터

### 4. 즐겨찾기
- 자주 조회하는 RUN_ID 저장
- 사용자별 관리

### 5. 실시간 알림
- 새 보고서 생성 알림
- 다운로드 제한 도달 알림

---

## 문의 및 지원

- **GitHub**: https://github.com/hellodesignthinking-png/LHproject
- **API 문서**: https://8000-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/docs
- **버전**: v1.6.0
- **업데이트**: 2026-01-01

---

## 변경 이력

### v1.6.0 (2026-01-01)
- ✅ 주소 검색 기능 추가
- ✅ 실시간 통계 카드
- ✅ 역할별 대시보드 링크
- ✅ 접근 로그 대시보드
- ✅ v1.6.0 신규 기능 섹션

### v1.5.1 (이전)
- Dashboard 인증 수정
- DEV 모드 지원

### v1.5.0 (이전)
- 권한 기반 접근 제어
- PDF 워터마크

### v1.4.0 (이전)
- Dashboard UX
- 6개 보고서 통합

### v1.3.0 (이전)
- 외부 공유 시스템

---

**상태**: ✅ Production Ready  
**최종 업데이트**: 2026-01-01  
**버전**: v1.6.0
