# ZeroSite v9.0 Frontend UI

## 📖 개요

ZeroSite v9.0용 현대적인 웹 UI입니다. Alpine.js와 Tailwind CSS를 사용한 경량 SPA(Single Page Application)로 구현되었습니다.

## ✨ 주요 기능

### 1. 토지 정보 입력 폼
- 주소, 좌표 (위도/경도)
- 대지면적, 건축면적
- 세대수, 토지가격
- 용도지역, 건폐율, 용적률
- 실시간 유효성 검증

### 2. 실시간 분석 진행 표시
- 7단계 분석 파이프라인 시각화
  1. 데이터 정규화
  2. GIS 분석
  3. 재무 분석
  4. LH 평가
  5. 리스크 분석
  6. 수요 분석
  7. 최종 의사결정
- 로딩 애니메이션
- 진행 상태 표시

### 3. 분석 결과 대시보드
- **최종 의사결정**: PROCEED / REVISE / NOGO
- **핵심 지표 카드**:
  - LH 평가점수 (110점 만점)
  - IRR (10년 수익률)
  - 종합 리스크 수준
  - 수요 점수
- **탭 기반 상세 결과**:
  - 입지분석 (POI, 접근성)
  - 재무분석 (IRR, Cap Rate, ROI, 민감도 분석)
  - LH 평가 (110점 평가, 강점/약점)
  - 리스크 (25개 항목, 카테고리별)
  - 수요분석 (인구, 세대수)

### 4. 전문가 리포트 생성
- **출력 형식**: PDF / HTML / Both
- **LLM 선택**: GPT-4 Turbo / Claude 3.5 Sonnet
- **12섹션 구조화 리포트**
- 원클릭 다운로드

## 🏗️ 기술 스택

- **Frontend Framework**: Alpine.js v3 (경량 반응형 프레임워크)
- **CSS Framework**: Tailwind CSS (Utility-first CSS)
- **Charts**: Chart.js v4 (데이터 시각화)
- **Icons**: Font Awesome 6
- **Fonts**: Noto Sans KR (한글 지원)

## 📂 파일 구조

```
frontend_v9/
├── index.html          # 메인 SPA (47KB)
└── README.md           # 문서 (이 파일)
```

## 🚀 실행 방법

### 1. FastAPI 서버 시작

```bash
cd /home/user/webapp
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 브라우저 접속

- **v9.0 UI**: http://localhost:8000/ (기본)
- **v9.0 UI (명시적)**: http://localhost:8000/v9/
- **v7.0 UI (레거시)**: http://localhost:8000/v7

### 3. API 문서

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 API 연동

### v9.0 API 엔드포인트

#### 1. 토지 분석 API

```http
POST /api/v9/analyze-land
Content-Type: application/json

{
  "address": "서울특별시 강남구 역삼동 123-45",
  "latitude": 37.123456,
  "longitude": 127.123456,
  "land_area_m2": 1000,
  "building_area_m2": 800,
  "unit_count": 50,
  "land_price_100m": 50,
  "zone_type": "제3종일반주거지역",
  "building_coverage_ratio": 60,
  "floor_area_ratio": 200
}
```

**응답 구조**:
```json
{
  "normalized_data": { ... },
  "gis_analysis": {
    "poi_analysis": [...],
    "overall_accessibility_score": 85,
    "accessibility_interpretation": "..."
  },
  "financial_analysis": {
    "total_project_cost_100m": 150,
    "lh_purchase_price_100m": 180,
    "cap_rate": 0.065,
    "roi_10yr": 0.85,
    "irr_10yr": 0.12,
    "irr_sensitivity": { ... }
  },
  "lh_evaluation": {
    "total_score": 95,
    "grade": "A",
    "category_scores": { ... },
    "strengths": [...],
    "weaknesses": [...],
    "submission_ready": true
  },
  "risk_assessment": {
    "overall_risk_level": "MEDIUM",
    "overall_risk_score": 45,
    "category_risks": { ... },
    "high_priority_risks": [...]
  },
  "demand_analysis": {
    "population_1km": 15000,
    "households_1km": 6000,
    "demand_score": 75,
    "demand_grade": "B"
  },
  "final_decision": {
    "final_decision": "PROCEED",
    "confidence_score": 0.85,
    "decision_rationale": "..."
  }
}
```

#### 2. 리포트 생성 API

```http
POST /api/v9/generate-report
Content-Type: application/json

{
  "land_data": { ... },
  "output_format": "pdf",
  "llm_provider": "gpt-4"
}
```

**응답**: PDF/HTML/ZIP 파일 다운로드

## 🎨 UI 컴포넌트

### 등급 배지 (Grade Badges)
- **S급**: 보라색 그라디언트 (90+)
- **A급**: 핑크 그라디언트 (75-89)
- **B급**: 파란색 그라디언트 (60-74)
- **C급**: 녹색 그라디언트 (45-59)
- **D급**: 노란색 그라디언트 (30-44)
- **F급**: 다크 그라디언트 (<30)

### 의사결정 배지 (Decision Badges)
- **PROCEED**: 녹색 (진행 권장)
- **REVISE**: 오렌지색 (보완 필요)
- **NOGO**: 빨간색 (진행 불가)

### 리스크 레벨 (Risk Levels)
- **HIGH**: 빨간색 (높음)
- **MEDIUM**: 오렌지색 (보통)
- **LOW**: 녹색 (낮음)

## 📱 반응형 디자인

- **Desktop**: 최대 너비 7xl (1280px)
- **Tablet**: 2열 그리드 → 1열 그리드
- **Mobile**: 완전 반응형, 터치 최적화

## 🔐 보안 고려사항

- **CORS**: 운영 환경에서는 특정 도메인만 허용 필요
- **API Key**: 클라이언트에 노출되지 않음 (서버측 관리)
- **입력 검증**: 서버측 유효성 검증 필수

## 🐛 디버깅

### 브라우저 콘솔에서 Alpine.js 데이터 확인

```javascript
// Alpine.js 앱 상태 확인
Alpine.store('zerositeApp')

// 현재 결과 확인
$data.results
```

### API 호출 디버깅

```javascript
// Fetch 에러 확인
fetch('/api/v9/analyze-land', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ ... })
})
.then(res => res.json())
.then(data => console.log(data))
.catch(err => console.error(err))
```

## 📈 성능 최적화

- **CDN 사용**: Tailwind, Alpine.js, Chart.js
- **지연 로딩**: Alpine.js defer 속성
- **경량 라이브러리**: Alpine.js (15KB gzipped)
- **최소한의 의존성**: 3개 라이브러리만 사용

## 🔄 업데이트 로그

### v9.0 (2024-12-04)
- ✅ Alpine.js + Tailwind CSS 기반 SPA
- ✅ 7단계 분석 파이프라인 시각화
- ✅ 5개 탭 (GIS, Financial, LH, Risk, Demand)
- ✅ 실시간 분석 진행 표시
- ✅ PDF/HTML 리포트 생성 UI
- ✅ 완전 반응형 디자인
- ✅ v9.0 API 완전 연동

## 🤝 기여 가이드

프론트엔드 개선 제안:
1. 차트 시각화 추가 (Chart.js)
2. 지도 통합 (Kakao Maps API)
3. 애니메이션 효과 개선
4. 다국어 지원 (i18n)
5. 오프라인 모드 (PWA)

## 📞 지원

- **API 문서**: http://localhost:8000/docs
- **GitHub**: (저장소 URL)
- **이메일**: support@zerosite.com

---

**© 2024 ZeroSite v9.0 - LH 신축매입임대 토지진단 시스템**
