# 🤝 클라우드 AI 개발자 협업 가이드

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [현재 개발 상태](#현재-개발-상태)
3. [Git 저장소 정보](#git-저장소-정보)
4. [필수 공유 항목](#필수-공유-항목)
5. [API 엔드포인트](#api-엔드포인트)
6. [환경 설정](#환경-설정)
7. [데이터베이스 스키마](#데이터베이스-스키마)
8. [외부 API 키](#외부-api-키)
9. [배포 정보](#배포-정보)
10. [협업 워크플로우](#협업-워크플로우)

---

## 📌 프로젝트 개요

**프로젝트명**: LH 신축매입임대 토지진단 자동화 시스템

**목적**: LH 신축매입임대주택 사업을 위한 토지 적합성 자동 진단 및 전문 보고서 생성

**주요 기능**:
- 토지 분석 (용도지역, 건축 규모, 리스크 요인)
- 7가지 유형별 수요 점수 비교 및 추천
- LH 공식 양식 보고서 생성 (HTML)
- Google Docs 자동 내보내기
- Google Sheets 분석 이력 저장
- 컨설턴트 정보 관리

---

## 🚀 현재 개발 상태

### 완료된 기능

#### Phase 1-5: 기본 시스템
- ✅ FastAPI 백엔드 구조
- ✅ Kakao Maps API 통합 (주소 → 좌표, 주변 시설 검색)
- ✅ 정부 공공데이터 API 통합 (용도지역, 인구통계)
- ✅ 건축 규모 자동 산정 (세대수, 층수, 주차대수)
- ✅ 리스크 요인 분석 (LH 매입 제외 사유 체크)
- ✅ 7가지 유형 자동 분석 및 추천
- ✅ 프론트엔드 UI (토지 분석, 결과 표시)

#### Phase 6: 고급 기능 (최근 완료)
- ✅ LH 공식 양식 보고서 생성 (A4 10페이지 이상)
- ✅ 인쇄 최적화 CSS (페이지 나누기, 레이아웃)
- ✅ 컨설턴트 정보 입력 및 표시
- ✅ Google Sheets 분석 이력 저장
- ✅ 레이더 차트 시각화 (matplotlib)
- ✅ Google Docs 자동 내보내기
- ✅ 토지 감정평가액 사용자 입력 반영
- ✅ 건축 데이터 정확성 개선

### 진행 중
- 🔄 정부 API 재신청 (현재 500 에러)
- 🔄 Kakao Static Map API 대체 방안

### Git 브랜치

- `main`: 안정 버전
- `feature/expert-report-generator`: 최신 개발 브랜치 ⭐ **현재 작업 브랜치**

**최근 커밋 (feature/expert-report-generator)**:
```
2579f81 docs(google-docs): add comprehensive setup guide and improve error messages
e6cd172 fix(ui): remove display:none from Google Docs button
53e6cb3 fix(ui): show Google Docs button immediately after analysis
b48872f feat(export): add Google Docs export functionality
2a14df3 fix(report): convert all html blocks to f-strings for proper variable interpolation
e4d16b9 feat(report): add print-optimized CSS and consultant info display
54eeeaf fix(report): Fix land appraisal price and building data not reflecting in reports
```

---

## 🔗 Git 저장소 정보

### 원격 저장소 URL

```bash
# Git 저장소 확인
git remote -v

# 일반적으로
origin  https://github.com/username/lh-land-analysis.git (fetch)
origin  https://github.com/username/lh-land-analysis.git (push)
```

### 브랜치 구조

```
main (안정 버전)
  └── feature/expert-report-generator (최신 개발) ⭐
```

### 클론 및 설정

```bash
# 1. 저장소 클론
git clone <repository-url>
cd lh-land-analysis

# 2. 개발 브랜치로 체크아웃
git checkout feature/expert-report-generator

# 3. 최신 변경사항 가져오기
git pull origin feature/expert-report-generator
```

---

## 📦 필수 공유 항목

### 1. 소스 코드

**공유 방법**:
- ✅ **Git 저장소 액세스 권한** (가장 추천)
- 또는 ZIP 파일 전달

**중요 파일**:
```
webapp/
├── app/
│   ├── main.py                          # FastAPI 메인 앱
│   ├── config.py                        # 설정 관리
│   ├── schemas.py                       # Pydantic 스키마
│   └── services/
│       ├── analysis_engine.py           # 토지 분석 엔진
│       ├── lh_official_report_generator.py  # LH 보고서 생성
│       ├── google_docs_service.py       # Google Docs 통합
│       ├── sheets_service.py            # Google Sheets 통합
│       ├── chart_service.py             # 차트 생성
│       ├── kakao_service.py             # Kakao API
│       ├── land_regulation_service.py   # 정부 API
│       └── mois_service.py              # 행정안전부 API
├── static/
│   ├── index.html                       # 메인 프론트엔드
│   └── share.html                       # 공유 페이지
└── requirements.txt                     # Python 의존성
```

### 2. 환경 변수 (.env)

```env
# ⚠️ 실제 값은 보안을 위해 별도 공유 (암호화된 채널)

# API Keys
KAKAO_REST_API_KEY=your_kakao_api_key_here
LAND_REGULATION_API_KEY=your_land_regulation_api_key_here
MOIS_API_KEY=your_mois_api_key_here

# Google Services (선택사항)
GOOGLE_SHEETS_CREDENTIALS_PATH=./google_credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here
GOOGLE_SHEETS_WORKSHEET_NAME=토지분석기록
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here

# Application
DEBUG=true
LOG_LEVEL=INFO

# Database (미래 사용)
# DATABASE_URL=postgresql://user:password@localhost/lh_analysis
```

### 3. Google Credentials (선택사항)

**파일**: `google_credentials.json`

**내용**: Google Cloud 서비스 계정 JSON 키

**공유 방법**:
- ❌ Git에 커밋하지 않음 (.gitignore에 포함됨)
- ✅ 안전한 채널로 별도 전달 (암호화된 파일 공유)
- ✅ 또는 클라우드 AI 개발자가 자체 생성 (GOOGLE_DOCS_SETUP.md 참조)

### 4. 문서

**필수 문서**:
- `README.md` - 프로젝트 개요 및 설치 방법
- `QUICKSTART.md` - 빠른 시작 가이드
- `USAGE.md` - 사용 방법
- `WEB_GUIDE.md` - 웹 인터페이스 가이드
- `GOOGLE_DOCS_SETUP.md` - Google Docs 설정
- `Google_Sheets_연동가이드.md` - Google Sheets 설정
- `정부API재신청가이드.md` - 정부 API 신청 방법
- `COLLABORATION_GUIDE.md` - 이 문서 ⭐

---

## 🌐 API 엔드포인트

### 현재 서버 URL

**개발 서버**: https://8020-i87ydg8bwr1e34immrcp6-cc2fbc16.sandbox.novita.ai

### 주요 엔드포인트

#### 1. 토지 분석

```http
POST /api/analyze-land
Content-Type: application/json

{
  "address": "서울특별시 강남구 역삼동 123-45",
  "land_area": 500,
  "unit_type": "청년",  // 또는 null (자동 분석)
  "zone_type": "제3종일반주거지역",  // 선택사항
  "land_status": "나대지",  // 선택사항
  "land_appraisal_price": 5000000,  // 선택사항 (원/㎡)
  "consultant": {  // 선택사항
    "name": "홍길동",
    "phone": "010-1234-5678",
    "department": "영업팀",
    "email": "hong@example.com"
  }
}
```

**응답**:
```json
{
  "status": "success",
  "analysis_id": "abc123",
  "address": "서울특별시 강남구 역삼동 123-45",
  "coordinates": { "lat": 37.123, "lng": 127.456 },
  "zone_info": {
    "zone_type": "제3종일반주거지역",
    "building_coverage_ratio": 50,
    "floor_area_ratio": 250
  },
  "building_capacity": {
    "units": 42,
    "floors": 6,
    "building_area": 250.5,
    "total_floor_area": 1252.5,
    "parking_spaces": 34
  },
  "demand_analysis": {
    "demand_score": 75.5,
    "key_factors": ["청년인구 비율 높음", "교통 접근성 우수"],
    "nearby_facilities": [...]
  },
  "risk_factors": [...],
  "summary": {
    "is_eligible": true,
    "recommendation": "적합"
  },
  "all_types_scores": [...]  // 7가지 유형 점수
}
```

#### 2. LH 공식 보고서 생성

```http
POST /api/generate-report
Content-Type: application/json

{
  // analyze-land와 동일한 요청 본문
}
```

**응답**:
```json
{
  "status": "success",
  "analysis_id": "abc123",
  "report": "<html>...</html>",  // HTML 보고서
  "format": "html",
  "generated_at": "2025-11-12T10:30:00",
  "has_map_image": true
}
```

#### 3. Google Docs 내보내기

```http
POST /api/generate-google-docs
Content-Type: application/json

{
  // analyze-land와 동일한 요청 본문
}
```

**응답**:
```json
{
  "status": "success",
  "analysis_id": "abc123",
  "google_docs": {
    "document_id": "1a2b3c4d5e6f7g8h9i",
    "document_url": "https://docs.google.com/document/d/...",
    "title": "LH토지진단_주소_청년_20251112_103000"
  },
  "generated_at": "2025-11-12T10:30:00"
}
```

#### 4. 정적 파일

```http
GET /                    # 메인 페이지
GET /share              # 공유 페이지 (자동 리다이렉트)
GET /static/index.html  # 메인 UI
```

---

## ⚙️ 환경 설정

### 1. Python 환경

**버전**: Python 3.11+

**의존성 설치**:
```bash
pip install -r requirements.txt
```

**주요 패키지**:
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
httpx==0.25.1
gspread==5.12.0
google-api-python-client==2.187.0
matplotlib==3.8.2
beautifulsoup4==4.13.4
```

### 2. 서버 실행

**개발 모드**:
```bash
cd /home/user/webapp
python -m uvicorn app.main:app --host 0.0.0.0 --port 8020 --reload
```

**프로덕션 모드**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8020 --workers 4
```

### 3. 환경 변수

`.env` 파일 생성 (`.env.example` 참조):
```bash
cp .env.example .env
# 실제 API 키 입력
```

---

## 🗄️ 데이터베이스 스키마

**현재 상태**: 데이터베이스 미사용 (인메모리 처리)

**향후 계획**: PostgreSQL 사용 예정

**예상 스키마**:
```sql
-- 분석 결과 저장
CREATE TABLE land_analysis (
    id SERIAL PRIMARY KEY,
    analysis_id VARCHAR(50) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    land_area FLOAT NOT NULL,
    unit_type VARCHAR(50),
    zone_type VARCHAR(100),
    demand_score FLOAT,
    is_eligible BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    consultant_name VARCHAR(100),
    consultant_phone VARCHAR(20),
    raw_data JSONB  -- 전체 분석 결과
);

-- 인덱스
CREATE INDEX idx_analysis_address ON land_analysis(address);
CREATE INDEX idx_analysis_created_at ON land_analysis(created_at);
```

**Google Sheets 대체**: 현재 Google Sheets를 간이 DB로 사용 중

---

## 🔑 외부 API 키

### 필요한 API 키

#### 1. Kakao REST API Key

**용도**: 주소 → 좌표 변환, 주변 시설 검색

**신청 방법**:
1. https://developers.kakao.com/ 접속
2. 내 애플리케이션 → 애플리케이션 추가
3. REST API 키 복사

**환경 변수**:
```env
KAKAO_REST_API_KEY=your_key_here
```

**현재 상태**: ✅ 정상 작동

#### 2. 토지이용규제정보 API Key

**용도**: 용도지역, 개발제한구역 조회

**신청 방법**:
1. https://www.data.go.kr/ 접속
2. "토지이용규제정보" 검색
3. 활용신청

**환경 변수**:
```env
LAND_REGULATION_API_KEY=your_key_here
```

**현재 상태**: ⚠️ 500 에러 (재신청 필요)

#### 3. 행정안전부 인구통계 API Key

**용도**: 인구통계, 가구정보 조회

**신청 방법**:
1. https://www.data.go.kr/ 접속
2. "주택 인구정보" 검색
3. 활용신청

**환경 변수**:
```env
MOIS_API_KEY=your_key_here
```

**현재 상태**: ⚠️ 500 에러 (재신청 필요)

#### 4. Google Cloud (선택사항)

**용도**: Google Docs, Google Sheets

**신청 방법**: `GOOGLE_DOCS_SETUP.md` 참조

**환경 변수**:
```env
GOOGLE_SHEETS_CREDENTIALS_PATH=./google_credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
```

**현재 상태**: 설정 시 작동 (선택사항)

---

## 🚀 배포 정보

### 현재 배포 환경

**플랫폼**: Novita AI Sandbox

**URL**: https://8020-i87ydg8bwr1e34immrcp6-cc2fbc16.sandbox.novita.ai

**포트**: 8020

### 권장 배포 옵션

#### Option 1: Docker

**Dockerfile** (생성 필요):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8020"]
```

**docker-compose.yml** (생성 필요):
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8020:8020"
    env_file:
      - .env
    volumes:
      - ./google_credentials.json:/app/google_credentials.json:ro
```

#### Option 2: 클라우드 플랫폼

- **Vercel/Netlify**: 프론트엔드 정적 배포
- **Heroku/Railway**: 백엔드 배포
- **AWS/GCP/Azure**: 전체 스택 배포

---

## 🤝 협업 워크플로우

### 1. 코드 동기화

```bash
# 최신 코드 가져오기
git fetch origin
git checkout feature/expert-report-generator
git pull origin feature/expert-report-generator

# 작업 브랜치 생성
git checkout -b feature/your-new-feature

# 개발 후 커밋
git add .
git commit -m "feat: your feature description"

# 푸시
git push origin feature/your-new-feature

# Pull Request 생성
# GitHub에서 feature/your-new-feature → feature/expert-report-generator
```

### 2. 개발 환경 설정

```bash
# 1. 저장소 클론
git clone <repo-url>
cd lh-land-analysis

# 2. 브랜치 체크아웃
git checkout feature/expert-report-generator

# 3. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 4. 의존성 설치
pip install -r requirements.txt

# 5. 환경 변수 설정
cp .env.example .env
# .env 파일 편집하여 API 키 입력

# 6. 서버 실행
python -m uvicorn app.main:app --reload --port 8020

# 7. 브라우저에서 접속
# http://localhost:8020
```

### 3. API 키 공유

**보안 방법**:
1. ✅ **1Password/LastPass** 같은 비밀번호 관리자
2. ✅ 암호화된 메시지 (Signal, Telegram Secret Chat)
3. ✅ 환경 변수 관리 서비스 (Doppler, Vault)
4. ❌ 이메일/일반 메신저 (비추천)

**공유 항목**:
```
KAKAO_REST_API_KEY=실제_키_값
LAND_REGULATION_API_KEY=실제_키_값
MOIS_API_KEY=실제_키_값
```

### 4. Google Credentials 공유

**방법 1**: 파일 공유
```bash
# 암호화하여 공유
zip -e google_credentials.zip google_credentials.json
# 비밀번호 별도 전달
```

**방법 2**: 자체 생성
- 클라우드 AI 개발자가 자체 Google Cloud 프로젝트 생성
- `GOOGLE_DOCS_SETUP.md` 가이드 참조

### 5. 테스트

```bash
# API 테스트
curl -X POST "http://localhost:8020/api/analyze-land" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 역삼동 123-45",
    "land_area": 500,
    "unit_type": "청년"
  }'

# 웹 UI 테스트
# http://localhost:8020 접속
```

---

## 📞 연락 및 지원

### 문서 위치

프로젝트 루트의 다음 문서들 참조:
- `README.md` - 전체 개요
- `QUICKSTART.md` - 빠른 시작
- `GOOGLE_DOCS_SETUP.md` - Google Docs 설정
- `정부API재신청가이드.md` - 정부 API 신청

### 주요 이슈

현재 알려진 문제:
1. ⚠️ 정부 API 500 에러 (재신청 필요)
2. ⚠️ Kakao Static Map API 404 (대체 방안 검토)

### 개선 사항

향후 개발 계획:
- [ ] PostgreSQL 데이터베이스 통합
- [ ] 사용자 인증 시스템
- [ ] 보고서 템플릿 커스터마이징
- [ ] 배치 분석 기능
- [ ] 모바일 반응형 개선

---

## ✅ 체크리스트

클라우드 AI 개발자에게 공유할 항목:

- [ ] Git 저장소 액세스 권한
- [ ] `.env` 파일 (API 키 포함)
- [ ] `google_credentials.json` (선택사항)
- [ ] 이 문서 (COLLABORATION_GUIDE.md)
- [ ] 개발 서버 URL
- [ ] Slack/Discord 채널 초대 (있는 경우)
- [ ] 프로젝트 관리 도구 액세스 (Jira/Trello 등)

---

**이 가이드로 클라우드 AI 개발자가 즉시 프로젝트에 참여할 수 있습니다!** 🚀
