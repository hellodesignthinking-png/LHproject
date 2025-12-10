# ZeroSite Expert Edition v3 + GenSpark AI Enhanced

**Powered by ZeroSite | Enhanced with GenSpark AI Backend Services**

## 🎉 What's New in Expert Edition v3

### **GenSpark AI Integration** ✨ NEW
- **Dynamic Transaction Generation**: Algorithmic comparable generation (not static data)
- **Professional 4-Factor Adjustment**: Distance (35%), Time (25%), Size (25%), Zone (15%)
- **Advanced Confidence Scoring**: 4-factor weighted algorithm (30/30/25/15%)
- **Land Valuation Engine v9.1**: Standalone professional appraisal engine

### **Test Results** ✅
```
✅ Enhanced Services: 4/4 tests passed
✅ Integrated Engine: 1/1 test passed  
✅ Total: 5/5 tests passed (100%)
🎉 GenSpark AI Integration is FULLY FUNCTIONAL!
```

---

## 📋 프로젝트 개요

ZeroSite Land Report는 LH 신축매입임대주택 사업을 위한 토지 적합성을 자동으로 진단하고, 
전문 컨설팅 수준의 분석 보고서를 생성하는 AI 기반 통합 플랫폼입니다.

**Expert Edition v3**는 GenSpark AI의 최적화된 백엔드 서비스를 통합하여 더욱 정확하고 
전문적인 토지 감정평가 기능을 제공합니다.

## 🎯 핵심 기능 (v5.0 + v3 API)

### 1. **Land Report API v3** ✨ NEW
   - RESTful API로 토지감정평가 서비스 제공
   - Dynamic Transaction Generation (10건 자동 생성)
   - 4-Factor Price Adjustment (거리/시점/규모/용도)
   - Advanced Confidence Scoring (통계적 신뢰도)
   - Financial Analysis & 3 Negotiation Strategies
   
### 2. **유형별 수요점수 완전 분리**
   - 청년, 신혼·신생아 I/II, 다자녀, 고령자 독립 점수
   - UI에서 유형별 색상 강조 표시
   
### 3. **다중 필지 분석**
   - 최대 10개 필지 동시 분석
   - 필지별 독립 결과 및 비교 분석
   
### 4. **AI Auto Corrector**
   - 주소 자동 보정
   - 토지면적 자동 추정
   - 임대료 예측
   
### 5. **Geo Optimizer (거리 기반 최적 부지 추천)**
   - POI 기반 입지 분석 (500m, 1km, 2km)
   - 유형별 가중치 적용
   - Top-N 최적 부지 추천
   
### 6. **Parcel Clustering (지도 기반 필지 클러스터링)**
   - K-Means & DBSCAN 알고리즘
   - Leaflet 히트맵 시각화
   - 클러스터 통계 자동 생성
   
### 7. **Google Drive LH 공고문 자동 수집**
   - PDF 자동 파싱 및 규칙 추출
   - 버전 관리 자동화
   - 실시간 공고문 업데이트

### 8. **Visual Dashboard**
   - Chart.js 기반 수요점수 비교
   - Leaflet 지도 기반 히트맵
   - 3D POI 분석 시각화

### 9. **전문가급 PDF/HTML 보고서**
   - ZeroSite 워터마크
   - 600자 AI 분석 문단
   - LH 공식 양식 적용

## 🚀 GenSpark AI 사용 방법

### **Python 코드에서 직접 사용**

```python
from app.engines_v9.land_valuation_engine_v9_1 import LandValuationEngineV91

# 엔진 초기화 (Enhanced 모드)
engine = LandValuationEngineV91(use_enhanced_services=True)

# 감정평가 실행
result = engine.evaluate_land(
    address="서울특별시 강남구 역삼동 123-45",
    land_size_sqm=1000.0,
    zone_type="제2종일반주거지역",
    asking_price=10_000_000_000
)

# 결과 확인
print(f"예상가: ₩{result['prediction']['avg']:,.0f}")
print(f"신뢰도: {result['prediction']['confidence']:.0%}")
print(f"거래사례: {len(result['comparables'])}건")
```

### **테스트 실행**

```bash
# GenSpark AI 통합 테스트
cd /home/user/webapp
python tests/test_genspark_integration.py

# 예상 결과:
# ✅ Enhanced Services: 4/4 tests passed
# ✅ Integrated Engine: 1/1 test passed
# 🎉 GenSpark AI Integration is FULLY FUNCTIONAL!
```

### **단독 실행 (데모)**

```bash
# Land Valuation Engine v9.1 직접 실행
python app/engines_v9/land_valuation_engine_v9_1.py

# 출력:
# 🏠 주소: 서울특별시 강남구 역삼동 123-45
# 💰 예상가: ₩11,599,313,759 (₩11.6억)
# 📊 신뢰도: 87% (HIGH)
# 📋 거래사례: 10건 동적 생성
# 🎯 협상전략: 3가지 자동 생성
```

---

## 🌐 Land Report API v3 (토지감정평가)

### **REST API 사용법** ✨ NEW

Expert Edition v3는 RESTful API를 통해 토지감정평가 서비스를 제공합니다.

#### **API 엔드포인트**

```bash
# 1. Health Check
curl http://localhost:8080/api/v3/health

# 2. 토지감정평가 보고서 생성 (JSON)
curl -X POST http://localhost:8080/api/v3/land-report \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 역삼동 123-45",
    "land_size_sqm": 1000.0,
    "zone_type": "제2종일반주거지역",
    "asking_price": 10000000000
  }'

# 3. 캐시된 보고서 조회
curl http://localhost:8080/api/v3/land-report/{report_id}

# 4. Enhanced vs Legacy 비교
curl -X POST http://localhost:8080/api/v3/land-report/compare \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 역삼동 123-45",
    "land_size_sqm": 1000.0,
    "zone_type": "제2종일반주거지역"
  }'
```

#### **API 응답 예시**

```json
{
  "report_id": "rpt_20251210_abc123",
  "timestamp": "2025-12-10T10:30:00",
  "valuation": {
    "estimated_price_krw": 12546748607,
    "price_per_sqm_krw": 12546749,
    "confidence_score": 0.83,
    "confidence_level": "HIGH",
    "transaction_count": 10,
    "price_range": {
      "low": 11000000000,
      "avg": 12546748607,
      "high": 14000000000
    }
  },
  "recommendation": {
    "status": "저가 (매수 추천)",
    "difference_pct": -20.30,
    "emoji": "🔵"
  },
  "comparables": [...] // Top 5 거래사례
}
```

#### **API 테스트**

```bash
# 전체 API 테스트 실행
cd /home/user/webapp
PYTHONPATH=/home/user/webapp python tests/test_land_report_api.py

# 예상 결과:
# ✅ Health Check Tests
# ✅ Report Generation Tests
# ✅ Report Retrieval Tests
# ✅ Comparison Mode Tests
# ✅ Validation Tests
# ✅ Performance Tests
# ✅ Confidence Scoring Tests
# 🎉 ALL TESTS PASSED (13/13)
```

---

## 🏗️ 시스템 아키텍처

### **통합 아키텍처 (Expert Edition v3 + GenSpark AI)**

```
┌─────────────────────────────────────────────┐
│      Frontend (Expert Edition v3 UI)       │
│             Port 8080                       │
└─────────────────────────────────────────────┘
                 ↓ HTTP
┌─────────────────────────────────────────────┐
│         Backend API (FastAPI)               │
│             Port 5000                       │
├─────────────────────────────────────────────┤
│  ✨ GenSpark AI Enhanced Services:         │
│  ├─ Enhanced Geocoding Service             │
│  ├─ Dynamic Transaction Generator          │
│  ├─ Professional Price Adjuster            │
│  └─ Advanced Confidence Calculator         │
├─────────────────────────────────────────────┤
│  🔧 Land Valuation Engine v9.1:            │
│  ├─ 9-Step Valuation Pipeline              │
│  ├─ Financial Analysis                     │
│  └─ Negotiation Strategies                 │
├─────────────────────────────────────────────┤
│  📊 v7.5 FINAL Report Generator:           │
│  └─ 60+ Page Expert Reports (5-6 MB)       │
└─────────────────────────────────────────────┘
```

---

## 🏗️ 기존 시스템 아키텍처

```
┌─────────────┐
│   사용자    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│      FastAPI Backend (v5.0)         │
│  ┌────────────────────────────────┐ │
│  │  Analysis Engine               │ │
│  │  • Type Demand Scores          │ │
│  │  • Multi-Parcel Analysis       │ │
│  │  • AI Auto Corrector           │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │  Geo Services                  │ │
│  │  • Geo Optimizer               │ │
│  │  • Parcel Clustering           │ │
│  │  • Heatmap Generator           │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │  LH Notice Manager             │ │
│  │  • Drive Sync                  │ │
│  │  • PDF Parser                  │ │
│  │  • Version Manager             │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │  Dashboard Builder             │ │
│  │  • Chart.js Integration        │ │
│  │  • Leaflet Maps                │ │
│  │  • 3D Visualization            │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│   External APIs                     │
│   • Kakao Map                       │
│   • 토지이용규제정보                   │
│   • 행정안전부 공공데이터                │
│   • Google Drive API                │
└─────────────────────────────────────┘
```

## 🔧 기술 스택

- **Backend**: FastAPI (Python 3.11+)
- **AI**: OpenAI GPT-4
- **Visualization**: 
  - Chart.js (차트)
  - Leaflet.js (지도)
  - Mapbox GL JS (3D 지도)
- **PDF**: WeasyPrint + ZeroSite 워터마크
- **External APIs**:
  - Kakao Map API
  - 토지이용규제정보 API
  - 행정안전부 공공데이터 API
  - Google Drive API

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

# Google Drive (LH 공고문 자동 수집)
GOOGLE_DRIVE_FOLDER_ID=13luANIq_cQ7KbzxVqb4QyG2r_q8-KaVv
GOOGLE_SHEETS_CREDENTIALS_PATH=./google_credentials.json
```

### 3. 서버 실행

```bash
# 개발 서버
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 서버
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🚀 API 엔드포인트 (v5.0)

### 토지 분석

```bash
POST /api/analyze-land
# 단일 필지 분석 (유형별 수요점수 포함)

POST /api/analyze-multi-parcel
# 다중 필지 동시 분석 (최대 10개)

POST /api/analyze-optimized-site
# Geo Optimizer 기반 최적 부지 추천
```

### LH 공고문 관리

```bash
POST /api/lh-notices/sync
# Google Drive에서 신규 공고문 자동 수집

GET /api/lh-rules/latest
# 최신 LH 심사 기준 조회

GET /api/lh-rules/versions
# 전체 버전 목록
```

### Dashboard

```bash
GET /api/dashboard-data
# 시각화용 대시보드 데이터
# - 수요점수 차트
# - 히트맵 데이터
# - POI 분석
# - Top-N 추천
```

### 보고서 생성

```bash
POST /api/generate-report
# PDF/HTML 보고서 생성 (ZeroSite 워터마크)

POST /api/export-to-google-docs
# Google Docs로 내보내기
```

## 📁 프로젝트 구조 (v5.0)

```
webapp/
├── app/
│   ├── main.py                          # FastAPI 앱 + v5.0 API 엔드포인트
│   ├── config.py                        # 설정
│   ├── schemas.py                       # Pydantic 스키마
│   └── services/
│       ├── analysis_engine.py           # ✨ 유형별 수요점수 분리
│       ├── ai_auto_corrector.py         # ✨ AI 자동 보정
│       ├── geo_optimizer.py             # ✨ 거리 기반 최적화
│       ├── parcel_cluster.py            # ✨ 필지 클러스터링
│       ├── lh_notice_loader.py          # ✨ LH 공고문 자동 수집
│       ├── lh_version_manager.py        # ✨ 버전 관리
│       ├── dashboard_builder.py         # ✨ Dashboard 생성
│       ├── kakao_service.py             # 카카오맵 API
│       ├── land_regulation_service.py   # 토지규제 API
│       ├── mois_service.py              # 행정안전부 API
│       ├── lh_official_report_generator.py  # PDF 생성
│       └── google_docs_service.py       # Google Docs 연동
├── static/
│   ├── index.html                       # ✨ v5.0 UI (유형별 점수, 다중필지, 지도)
│   ├── css/
│   └── js/
├── data/
│   ├── lh_rules_auto/                   # ✨ 자동 수집된 LH 규칙
│   └── lh_notices/                      # ✨ 공고문 저장소
├── tests/
│   ├── test_type_demand_scores_v6.py    # 유형별 점수 테스트
│   ├── test_multi_parcel_ui_v6.py       # 다중 필지 테스트
│   ├── test_ai_auto_corrector.py        # AI Corrector 테스트
│   ├── test_geo_optimizer.py            # Geo Optimizer 테스트
│   ├── test_parcel_cluster.py           # Clustering 테스트
│   └── test_lh_notice_loader.py         # Notice Loader 테스트
├── V7_FULL_SYSTEM_REPORT.md             # ✨ 전체 시스템 보고서
├── README.md                            # 이 파일
└── requirements.txt
```

## 🧪 테스트

```bash
# 전체 테스트 실행
python test_type_demand_scores_v6.py
python test_multi_parcel_ui_v6.py
python test_ai_auto_corrector.py
python test_geo_optimizer.py
python test_parcel_cluster.py

# 통합 테스트
pytest tests/ --cov=app
```

## 🎨 UI 기능 (v5.0)

### 1. 유형별 수요점수 표시
- 5가지 주거 유형별 독립 점수
- 색상 강조 (청년: 파랑, 신혼I: 분홍, 신혼II: 보라, 다자녀: 초록, 고령자: 주황)

### 2. 다중 필지 분석
- 최대 10개 필지 입력
- 필지별 결과 카드 렌더링
- 에러 필지 별도 표시

### 3. 지도 시각화
- Leaflet 기반 히트맵
- 클러스터 원형 표시
- Geo Optimizer 추천 지점 마커

### 4. Dashboard
- 수요점수 비교 차트
- POI 분석 3D 바 차트
- Top-N 추천 부지 순위

## 🌐 Google Drive LH 공고문 자동 수집

### Drive 폴더
```
https://drive.google.com/drive/folders/13luANIq_cQ7KbzxVqb4QyG2r_q8-KaVv
```

### 파일명 인식 패턴 (v2.0)
- 패턴 1: `서울25-8차민간신축매입약정방식공고문.pdf`
- 패턴 2: `LH2025_신축매입사업_공고문.pdf`
- 패턴 3: `대구28-1차민간매입약정공고문_최종.pdf`

### 자동 처리 프로세스
1. Google Drive API로 신규 파일 감지
2. PDF → Text 변환 (pdfplumber)
3. 주거 유형별 규칙 추출 (정규식)
4. `/data/lh_rules_auto/{year}_{round}.json` 생성
5. LH Version Manager에 자동 등록

## 📝 개발 로드맵

### v5.0 (현재) ✅
- [x] 유형별 수요점수 완전 분리
- [x] 다중 필지 분석
- [x] AI Auto Corrector
- [x] Geo Optimizer
- [x] Parcel Clustering
- [x] LH 공고문 자동 수집
- [x] Dashboard 시각화
- [x] ZeroSite 워터마크

### v5.1 (계획)
- [ ] 실시간 알림 시스템
- [ ] 모바일 앱 지원
- [ ] 머신러닝 기반 수요 예측 고도화
- [ ] 다국어 지원

## 📄 문서

- [V7_FULL_SYSTEM_REPORT.md](./V7_FULL_SYSTEM_REPORT.md) - 전체 시스템 아키텍처 및 구현 상세
- [GOOGLE_DOCS_SETUP.md](./GOOGLE_DOCS_SETUP.md) - Google Docs 연동 가이드
- [TESTING_GUIDE.md](./TESTING_GUIDE.md) - 테스트 가이드
- [USAGE.md](./USAGE.md) - 사용 가이드

## 📄 라이선스

MIT License

Copyright (c) 2025 ZeroSite

## 👥 기여

이슈 및 PR을 환영합니다!

---

**ZeroSite Land Report v5.0** - Powered by ZeroSite
