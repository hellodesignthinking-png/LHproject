# 🏢 공공정책 기반 민간개발 매니지먼트 플랫폼 아키텍처

## 📋 시스템 개요

**플랫폼 이름**: Public-Private Development Management Platform (PPDMP)

**핵심 가치**:
- 공공정책 + 민간개발 리스크관리 + 사회적 가치 창출
- 데이터 기반 의사결정
- 실시간 정책 반영
- 지속가능한 개발 지원

---

## 🏗️ 전체 시스템 아키텍처

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

## 📦 모듈 구성

### 1. **기존 모듈 (완료)**
- ✅ 토지진단 자동화 (Land Analysis)
- ✅ 외부 API 통합 (Kakao, 토지규제, 행정안전부)
- ✅ 건축 규모 계산
- ✅ 리스크 요인 분석

### 2. **신규 모듈 (개발 예정)**

#### Module A: 정책 모니터링 시스템
```python
app/modules/policy_monitor/
├── __init__.py
├── crawler.py           # LH/국토부 크롤러
├── parser.py            # 공고문 파싱
├── analyzer.py          # 정책 변화 분석
├── notifier.py          # 알림 시스템
└── models.py            # 정책 데이터 모델
```

**기능:**
- LH 홈페이지 공고 자동 수집
- 국토부 보도자료 모니터링
- 정책 변화 감지 및 알림
- 주간/월간 리포트 생성

#### Module B: 프로젝트 관리 시스템
```python
app/modules/project_management/
├── __init__.py
├── project.py           # 프로젝트 CRUD
├── workflow.py          # 워크플로우 관리
├── milestone.py         # 마일스톤 추적
├── document.py          # 서류 관리
└── models.py            # 프로젝트 데이터 모델
```

**기능:**
- 프로젝트 생성/수정/삭제
- 사업 단계별 체크리스트
- 진행 상황 추적
- 서류 업로드 및 관리

#### Module C: 사업성 시뮬레이션
```python
app/modules/business_simulation/
├── __init__.py
├── financial.py         # 재무 모델
├── construction_cost.py # 건축비 산정
├── purchase_price.py    # 매입가 시뮬레이션
├── roi_calculator.py    # 수익률 계산
└── models.py            # 사업성 데이터 모델
```

**기능:**
- 건축비 자동 산정
- LH 매입가 시뮬레이션
- 수익성 분석 (ROI, IRR)
- 민감도 분석

#### Module D: ESG & 사회적가치 평가
```python
app/modules/esg_evaluation/
├── __init__.py
├── environmental.py     # 환경 지표
├── social.py            # 사회 지표
├── governance.py        # 거버넌스 지표
├── calculator.py        # ESG 점수 계산
└── models.py            # ESG 데이터 모델
```

**기능:**
- 친환경 설계 평가
- 지역 고용 창출 측정
- 사회적 효과 정량화
- ESG 리포트 생성

---

## 🗄️ 데이터베이스 스키마

### 주요 테이블

#### 1. projects (프로젝트)
```sql
- id: UUID (PK)
- name: VARCHAR
- address: TEXT
- land_area: FLOAT
- unit_type: VARCHAR
- status: ENUM (기획, 진행중, 완료)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### 2. policy_updates (정책 업데이트)
```sql
- id: SERIAL (PK)
- source: VARCHAR (LH, 국토부 등)
- title: TEXT
- content: TEXT
- category: VARCHAR
- published_at: TIMESTAMP
- collected_at: TIMESTAMP
```

#### 3. analysis_results (분석 결과)
```sql
- id: UUID (PK)
- project_id: UUID (FK)
- analysis_type: VARCHAR
- result_data: JSONB
- score: FLOAT
- created_at: TIMESTAMP
```

#### 4. business_simulations (사업성 분석)
```sql
- id: UUID (PK)
- project_id: UUID (FK)
- construction_cost: FLOAT
- purchase_price: FLOAT
- roi: FLOAT
- irr: FLOAT
- created_at: TIMESTAMP
```

#### 5. esg_evaluations (ESG 평가)
```sql
- id: UUID (PK)
- project_id: UUID (FK)
- environmental_score: FLOAT
- social_score: FLOAT
- governance_score: FLOAT
- total_score: FLOAT
- created_at: TIMESTAMP
```

---

## 🎨 Frontend 구조 (React)

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/           # 재사용 컴포넌트
│   │   ├── Dashboard/
│   │   ├── ProjectCard/
│   │   ├── Chart/
│   │   └── Layout/
│   ├── pages/               # 페이지
│   │   ├── Dashboard.tsx    # 메인 대시보드
│   │   ├── Projects.tsx     # 프로젝트 목록
│   │   ├── Analysis.tsx     # 분석 결과
│   │   ├── Policy.tsx       # 정책 모니터
│   │   └── Reports.tsx      # 리포트
│   ├── services/            # API 클라이언트
│   │   ├── api.ts
│   │   ├── projectService.ts
│   │   └── analysisService.ts
│   ├── utils/               # 유틸리티
│   ├── types/               # TypeScript 타입
│   ├── App.tsx
│   └── index.tsx
└── package.json
```

---

## 🔌 API 엔드포인트 설계

### 기존 API
- `POST /api/analyze-land` - 토지 분석

### 신규 API

#### 정책 모니터링
- `GET /api/policies` - 정책 목록
- `GET /api/policies/{id}` - 정책 상세
- `GET /api/policies/latest` - 최신 정책

#### 프로젝트 관리
- `GET /api/projects` - 프로젝트 목록
- `POST /api/projects` - 프로젝트 생성
- `GET /api/projects/{id}` - 프로젝트 상세
- `PUT /api/projects/{id}` - 프로젝트 수정
- `DELETE /api/projects/{id}` - 프로젝트 삭제

#### 사업성 분석
- `POST /api/simulations` - 사업성 시뮬레이션
- `GET /api/simulations/{project_id}` - 시뮬레이션 결과

#### ESG 평가
- `POST /api/esg/evaluate` - ESG 평가
- `GET /api/esg/{project_id}` - ESG 평가 결과

#### 리포트
- `GET /api/reports/{project_id}/comprehensive` - 종합 리포트
- `GET /api/reports/{project_id}/pdf` - PDF 다운로드

---

## 🚀 개발 로드맵

### Phase 1: 백엔드 확장 (2주)
- [x] 디렉토리 구조 설계
- [ ] 정책 모니터링 크롤러
- [ ] 프로젝트 관리 API
- [ ] 사업성 시뮬레이션 API
- [ ] ESG 평가 API
- [ ] 데이터베이스 스키마 구축

### Phase 2: 프론트엔드 개발 (3주)
- [ ] React 프로젝트 초기화
- [ ] 대시보드 UI
- [ ] 프로젝트 관리 페이지
- [ ] 분석 결과 시각화
- [ ] 리포트 뷰어

### Phase 3: 통합 및 테스트 (1주)
- [ ] 통합 테스트
- [ ] 성능 최적화
- [ ] 문서화
- [ ] 배포

---

## 💻 기술 스택

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL + PostGIS
- **ORM**: SQLAlchemy
- **Task Queue**: Celery + Redis
- **Crawler**: Selenium, BeautifulSoup4

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **UI Library**: Tailwind CSS, shadcn/ui
- **State Management**: React Query, Zustand
- **Charts**: Recharts, Chart.js
- **Maps**: Kakao Maps API

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions
- **Hosting**: AWS / GCP

---

## 📊 비즈니스 모델

### 수익 구조

#### 1. 컨설팅 + 플랫폼 번들
- 프로젝트당 300-500만원
- 플랫폼 이용권 포함

#### 2. SaaS 구독
- Basic: 월 50만원 (토지진단 + 정책모니터)
- Pro: 월 100만원 (+ 프로젝트관리 + 사업성분석)
- Enterprise: 월 200만원 (+ ESG평가 + 전문컨설팅)

#### 3. 성과 연동
- LH 매입 확정 시 매입가의 1-2% 수수료

#### 4. 데이터/리포트 판매
- 정책 트렌드 리포트: 50만원
- 입지 분석 리포트: 30만원
- API 사용료: 건당 5만원

---

## 🎯 차별화 포인트

1. **실시간 정책 반영**
   - 자동 크롤링 + AI 분석
   - 경쟁사 대비 정보 우위

2. **데이터 기반 의사결정**
   - 직관 → 정량화
   - 리스크 사전 예측

3. **통합 관리 플랫폼**
   - 기획 → 인허가 → 시공 → 매입
   - 전 과정 추적 가능

4. **공공성 측정 가능**
   - ESG 지표 정량화
   - 사회적 가치 증명

5. **확장 가능한 아키텍처**
   - 모듈형 설계
   - API 제공 가능

---

## 📝 다음 단계

1. **정책 모니터링 크롤러 개발** 시작
2. **데이터베이스 스키마** 구현
3. **프로젝트 관리 API** 구축
4. **React 프론트엔드** 초기화

---

**작성일**: 2024-11-10  
**버전**: 2.0.0  
**상태**: 설계 완료, 개발 진행 중
