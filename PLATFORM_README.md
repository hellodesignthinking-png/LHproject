# 🏢 공공정책 기반 민간개발 매니지먼트 플랫폼 (PPDMP)

## Public-Private Development Management Platform

> **공공정책 + 민간개발 리스크관리 + 사회적 가치 창출**을 통합한 차세대 부동산 개발 플랫폼

---

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [핵심 기능](#핵심-기능)
3. [시스템 아키텍처](#시스템-아키텍처)
4. [API 문서](#api-문서)
5. [설치 및 실행](#설치-및-실행)
6. [사용 예시](#사용-예시)
7. [비즈니스 모델](#비즈니스-모델)

---

## 🎯 프로젝트 개요

### 플랫폼의 목적

LH 신축매입임대주택 사업을 중심으로, **정책 변화 모니터링**, **토지진단 자동화**, **프로젝트 관리**, **사업성 분석**을 하나의 플랫폼에서 제공하는 통합 솔루션입니다.

### 해결하는 문제

1. **정책 정보의 비대칭**: LH 및 국토부 정책 변화를 실시간으로 추적하지 못함
2. **비효율적 의사결정**: 수작업 기반의 토지 분석 및 사업성 검토
3. **분산된 프로젝트 관리**: 여러 도구와 엑셀 파일로 산재된 프로젝트 정보
4. **리스크 관리 부재**: 사전 리스크 예측 및 대응 체계 미흡

### 차별화 포인트

✅ **실시간 정책 반영** - 자동 크롤링 + AI 분석  
✅ **데이터 기반 의사결정** - 직관 → 정량화  
✅ **통합 관리 플랫폼** - 기획 → 매입까지 전 과정 추적  
✅ **공공성 측정 가능** - ESG 지표 정량화  
✅ **확장 가능한 아키텍처** - 모듈형 설계 + API 제공

---

## 🚀 핵심 기능

### 1️⃣ LH 정책 모니터링 시스템

**자동 데이터 수집**
- LH 공사 홈페이지 공고 자동 크롤링
- 국토교통부 보도자료 모니터링
- 정책 변화 감지 및 알림

**지능형 분석**
- AI 기반 정책 변화 분석
- 중요도 자동 분류 (high/medium/low)
- 주간/월간 리포트 자동 생성

**API 엔드포인트**
```
GET  /api/policy/updates           # 정책 업데이트 목록
GET  /api/policy/updates/latest    # 최신 정책
GET  /api/policy/updates/important # 중요 정책
GET  /api/policy/changes            # 정책 변화 감지
GET  /api/policy/report             # 정책 리포트 생성
POST /api/policy/parse              # 정책 문서 파싱
```

---

### 2️⃣ 토지진단 자동화 시스템

**종합 분석 기능**
- 카카오맵 API 연동 (좌표 변환, 주변 시설)
- 토지규제정보 API (용도지역, 규제사항)
- 행정안전부 API (인구통계, 가구 정보)

**자동 진단 항목**
- LH 공고문 탈락 사유 자동 검토
- 건축 규모 자동 산정 (세대수/층수/주차대수)
- 입지 및 수요 분석
- 리스크 요인 탐지

**API 엔드포인트**
```
POST /api/analyze-land          # 토지 종합 분석
POST /api/generate-report       # 전문가급 보고서 생성
```

---

### 3️⃣ 프로젝트 관리 시스템 (PM Dashboard)

**프로젝트 라이프사이클 관리**
- 프로젝트 생성/수정/삭제 (CRUD)
- 상태별 관리 (기획 → 매입까지 10단계)
- 실시간 진행률 추적

**마일스톤 추적**
- 10개 기본 마일스톤 자동 생성
- 진행 상태 관리 (미시작/진행중/완료/지연)
- 체크리스트 기능

**리스크 관리**
- 리스크 식별 및 등록
- 레벨별 분류 (낮음/보통/높음/심각)
- 완화 계획 및 비상 계획 수립

**문서 관리**
- 프로젝트 관련 문서 업로드/관리
- 버전 관리
- 문서 유형별 분류

**API 엔드포인트**
```
# 프로젝트
POST   /api/projects                    # 프로젝트 생성
GET    /api/projects                    # 프로젝트 목록
GET    /api/projects/{id}               # 프로젝트 상세
PUT    /api/projects/{id}               # 프로젝트 수정
DELETE /api/projects/{id}               # 프로젝트 삭제

# 마일스톤
GET    /api/projects/{id}/milestones   # 마일스톤 목록
POST   /api/projects/{id}/milestones   # 마일스톤 생성
PATCH  /api/projects/{id}/milestones/{milestone_id}  # 상태 업데이트

# 리스크
GET    /api/projects/{id}/risks         # 리스크 목록
POST   /api/projects/{id}/risks         # 리스크 추가

# 문서
GET    /api/projects/{id}/documents     # 문서 목록
POST   /api/projects/{id}/documents     # 문서 추가

# 대시보드
GET    /api/projects/dashboard/summary  # 대시보드 요약
GET    /api/projects/{id}/progress      # 프로젝트 진행률
GET    /api/projects/{id}/timeline      # 프로젝트 타임라인
```

---

### 4️⃣ 대시보드 및 통계

**실시간 현황 대시보드**
- 총 프로젝트 수 / 진행중 / 완료
- 상태별 프로젝트 분포
- 유형별 프로젝트 분포 (청년형/신혼부부형/고령자형)
- 총 예상 사업비 및 세대수

**리스크 현황**
- 고위험 프로젝트 수
- 지연된 마일스톤 수

**최근 활동**
- 프로젝트 생성/수정 이력
- 마일스톤 진행 상황
- 리스크 식별 내역

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer (React)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   대시보드    │  │ 프로젝트 관리 │  │   리포트     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API
┌──────────────────────────┴──────────────────────────────────┐
│                   Backend Layer (FastAPI)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 토지진단 API  │  │  정책 모니터  │  │ PM 시스템    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 사업성 분석   │  │  ESG 평가    │  │  리포트 생성  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                    Data Collection Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ LH 크롤러     │  │ 국토부 API   │  │ 카카오맵 API  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                  Database Layer (PostgreSQL)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  정책 DB     │  │ 프로젝트 DB   │  │  분석 이력    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 기술 스택

### Backend
- **Framework**: FastAPI 0.104.1
- **Language**: Python 3.11+
- **Async**: aiohttp, asyncio
- **API Integration**: Kakao Maps, Land Regulation, MOIS

### Data Collection
- **Web Crawling**: BeautifulSoup4, aiohttp
- **Parsing**: Regular expressions, NLP

### Frontend (예정)
- **Framework**: React 18
- **Language**: TypeScript
- **UI Library**: Tailwind CSS, shadcn/ui
- **State Management**: React Query, Zustand
- **Charts**: Recharts

### Database (예정)
- **RDBMS**: PostgreSQL + PostGIS
- **ORM**: SQLAlchemy
- **Migration**: Alembic

---

## 📦 설치 및 실행

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd webapp

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일 생성:

```env
# API Keys
KAKAO_REST_API_KEY=your_kakao_key
LAND_REGULATION_API_KEY=your_land_regulation_key
MOIS_API_KEY=your_mois_key

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### 3. 서버 실행

```bash
# 개발 서버
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. API 문서 확인

브라우저에서 아래 URL 접속:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🎨 사용 예시

### 1. 정책 모니터링

**최신 정책 업데이트 조회**
```bash
curl -X GET "http://localhost:8000/api/policy/updates/latest?limit=5"
```

**정책 변화 감지**
```bash
curl -X GET "http://localhost:8000/api/policy/changes?days=7"
```

**정책 리포트 생성**
```bash
curl -X GET "http://localhost:8000/api/policy/report?days=30"
```

---

### 2. 토지 분석

**토지 종합 분석**
```bash
curl -X POST "http://localhost:8000/api/analyze-land" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 역삼동 679",
    "land_area": 500,
    "unit_type": "청년형"
  }'
```

---

### 3. 프로젝트 관리

**프로젝트 생성**
```bash
curl -X POST "http://localhost:8000/api/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "서울 강남 역삼동 프로젝트",
    "address": "서울특별시 강남구 역삼동 679",
    "land_area": 500.0,
    "unit_type": "청년형",
    "estimated_units": 34,
    "estimated_cost": 2500000000,
    "project_manager": "김철수"
  }'
```

**프로젝트 목록 조회**
```bash
curl -X GET "http://localhost:8000/api/projects"
```

**대시보드 요약**
```bash
curl -X GET "http://localhost:8000/api/projects/dashboard/summary"
```

---

## 💰 비즈니스 모델

### 수익 구조

#### 1. 컨설팅 + 플랫폼 번들
- 프로젝트당 300-500만원
- 플랫폼 이용권 포함

#### 2. SaaS 구독
- **Basic**: 월 50만원
  - 토지진단 + 정책모니터
- **Pro**: 월 100만원  
  - + 프로젝트관리 + 사업성분석
- **Enterprise**: 월 200만원  
  - + ESG평가 + 전문컨설팅

#### 3. 성과 연동
- LH 매입 확정 시 매입가의 1-2% 수수료

#### 4. 데이터/리포트 판매
- 정책 트렌드 리포트: 50만원
- 입지 분석 리포트: 30만원
- API 사용료: 건당 5만원

---

## 📊 현재 구현 상태

### ✅ 완료된 기능 (v2.0)

1. **플랫폼 아키텍처 설계** ✅
2. **LH 정책 모니터링 시스템** ✅
   - 크롤러 (LH, 국토부)
   - 정책 파서
   - 정책 분석기
   - 알림 시스템
3. **프로젝트 관리 시스템** ✅
   - CRUD API
   - 마일스톤 관리
   - 리스크 관리
   - 문서 관리
   - 대시보드
4. **토지진단 API** ✅ (기존 기능)
5. **API 문서 자동화** ✅

### 🔄 개발 중

6. **사업성 시뮬레이션 툴**
   - 건축비 자동 산정
   - LH 매입가 시뮬레이션
   - ROI/IRR 계산

7. **React 프론트엔드**
   - 대시보드 UI
   - 프로젝트 관리 페이지
   - 분석 결과 시각화

8. **데이터베이스 연동**
   - PostgreSQL 스키마
   - ORM 설정
   - 데이터 마이그레이션

### 📝 계획 중

9. **ESG & 사회적가치 평가**
10. **AI 기반 리포트 생성**
11. **모바일 앱**

---

## 📁 프로젝트 구조

```
webapp/
├── app/
│   ├── main.py                         # FastAPI 메인 앱
│   ├── config.py                       # 설정 관리
│   ├── schemas.py                      # Pydantic 스키마
│   │
│   ├── api/
│   │   └── endpoints/
│   │       ├── policy.py               # 정책 모니터링 API
│   │       ├── projects.py             # 프로젝트 관리 API
│   │       └── analysis.py             # 토지분석 API
│   │
│   ├── modules/
│   │   ├── policy_monitor/             # 정책 모니터링 모듈
│   │   │   ├── crawler.py
│   │   │   ├── parser.py
│   │   │   ├── analyzer.py
│   │   │   └── notifier.py
│   │   │
│   │   ├── project_management/         # 프로젝트 관리 모듈
│   │   │   ├── models.py
│   │   │   └── service.py
│   │   │
│   │   ├── business_simulation/        # 사업성 분석 (예정)
│   │   └── esg_evaluation/             # ESG 평가 (예정)
│   │
│   ├── services/                       # 외부 API 서비스
│   │   ├── kakao_service.py
│   │   ├── land_regulation_service.py
│   │   ├── mois_service.py
│   │   └── analysis_engine.py
│   │
│   └── utils/                          # 유틸리티
│       └── calculations.py
│
├── frontend/                           # React 프론트엔드 (예정)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
│
├── database/                           # 데이터베이스 (예정)
│   ├── migrations/
│   └── seeds/
│
├── docs/                               # 문서
│   ├── PLATFORM_ARCHITECTURE.md
│   └── API_GUIDE.md
│
├── tests/                              # 테스트
├── .env                                # 환경 변수
├── requirements.txt                    # Python 의존성
└── README.md                           # 프로젝트 설명
```

---

## 🌐 라이브 데모

### 현재 실행 중인 서버

**API 서버**: https://8000-iadrkxedqg14xkst1ju95-b9b802c4.sandbox.novita.ai

**API 문서**:
- Swagger UI: https://8000-iadrkxedqg14xkst1ju95-b9b802c4.sandbox.novita.ai/docs
- ReDoc: https://8000-iadrkxedqg14xkst1ju95-b9b802c4.sandbox.novita.ai/redoc

**Health Check**: https://8000-iadrkxedqg14xkst1ju95-b9b802c4.sandbox.novita.ai/health

---

## 🤝 기여 방법

이슈 및 PR을 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 라이선스

MIT License

---

## 👥 Contact

프로젝트 관련 문의: 

**개발팀**: Neil

---

## 📈 로드맵

### Phase 1: MVP (완료) ✅
- 정책 모니터링 크롤러
- 프로젝트 관리 시스템
- 토지진단 API

### Phase 2: 고도화 (진행중) 🔄
- 사업성 시뮬레이션
- React 프론트엔드
- 데이터베이스 연동

### Phase 3: 확장 (계획중) 📋
- ESG 평가
- AI 리포트
- 모바일 앱

### Phase 4: 플랫폼화 (장기) 🚀
- SaaS 모델 전환
- API 마켓플레이스
- 파트너 에코시스템

---

**Last Updated**: 2025-11-10  
**Version**: 2.0.0  
**Status**: Active Development 🚧
