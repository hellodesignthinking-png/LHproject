# LH 신축매입임대 토지진단 자동화 시스템

## 📋 프로젝트 개요

LH 신축매입임대주택 사업을 위한 토지 적합성을 자동으로 진단하고, 전문 컨설팅 수준의 분석 보고서를 생성하는 시스템입니다.

## 🎯 핵심 기능

1. **공고문 탈락 사유 자동 검토**
   - 유해시설, 진입도로, 법률제한 등 자동 체크
   
2. **지번 기반 건축 규모 자동 산정**
   - 용도지역, 용적률 기반 세대수/층수/주차대수 계산
   
3. **입지 및 수요 분석**
   - 청년인구 비중, 주변 시설, 임대 수요 분석
   
4. **AI 기반 전문 보고서 생성**
   - 600자 분량의 전문 분석 문단 자동 생성
   
5. **PDF 보고서 출력**
   - 디자인이 적용된 전문 보고서 PDF 생성

## 🏗️ 시스템 아키텍처

```
[사용자] → [FastAPI 백엔드] → [외부 API 통합] → [분석 엔진] → [PDF 생성]
                ↓
          [PostgreSQL DB]
```

## 🔧 기술 스택

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with PostGIS
- **Task Queue**: Celery + Redis
- **External APIs**:
  - Kakao Map API (좌표 변환, 주변 시설)
  - 토지이용규제정보 API (용도지역, 규제)
  - 행정안전부 공공데이터 API (인구통계)
- **AI**: OpenAI GPT-4
- **PDF**: WeasyPrint

## 📦 설치 및 실행

### 1. 환경 설정

```bash
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
OPENAI_API_KEY=your_openai_key

# Database
DATABASE_URL=postgresql://user:password@localhost/lh_analysis

# Redis
REDIS_URL=redis://localhost:6379
```

### 3. 서버 실행

```bash
# 개발 서버
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Celery Worker (별도 터미널)
celery -A app.tasks worker --loglevel=info
```

## 🚀 API 사용 예시

### 토지 분석 요청

```bash
curl -X POST "http://localhost:8000/api/analyze-land" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 역삼동 123-45",
    "land_area": 500,
    "unit_type": "청년형"
  }'
```

### 응답 예시

```json
{
  "status": "success",
  "analysis_id": "abc123",
  "summary": {
    "is_eligible": true,
    "estimated_units": 15,
    "demand_score": 85,
    "recommendation": "적합"
  },
  "pdf_url": "/api/reports/abc123.pdf"
}
```

## 📁 프로젝트 구조

```
webapp/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 앱
│   ├── config.py              # 설정
│   ├── models.py              # DB 모델
│   ├── schemas.py             # Pydantic 스키마
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints/
│   │       ├── analysis.py    # 분석 엔드포인트
│   │       └── reports.py     # 보고서 엔드포인트
│   ├── services/
│   │   ├── __init__.py
│   │   ├── kakao_service.py   # 카카오맵 API
│   │   ├── land_regulation_service.py  # 토지규제 API
│   │   ├── mois_service.py    # 행정안전부 API
│   │   ├── analysis_engine.py # 분석 로직
│   │   └── report_generator.py # PDF 생성
│   ├── tasks.py               # Celery 작업
│   └── utils/
│       ├── __init__.py
│       └── calculations.py    # 계산 유틸리티
├── templates/
│   └── report_template.html   # PDF 템플릿
├── static/
│   ├── css/
│   └── images/
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_services.py
├── .env.example
├── .gitignore
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest

# 커버리지 포함
pytest --cov=app tests/
```

## 📝 개발 로드맵

- [x] 프로젝트 구조 설계
- [x] 외부 API 통합 (Kakao, 토지규제, 행정안전부)
- [ ] 건축 규모 계산 엔진
- [ ] 입지 분석 모듈
- [ ] AI 보고서 생성
- [ ] PDF 템플릿 디자인
- [ ] 프론트엔드 대시보드
- [ ] 배포 및 운영

## 📄 라이선스

MIT License

## 👥 기여

이슈 및 PR을 환영합니다!
