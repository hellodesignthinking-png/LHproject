# ZeroSite v9.0 Implementation Guide

## 문서 개요
- **작성일**: 2025-12-04
- **버전**: v9.0 Part 5
- **목적**: 개발자가 v9.0을 처음부터 구현하기 위한 완전한 가이드
- **대상**: 개발팀 (Backend, Frontend, DevOps)

---

## Part 5: 구현 가이드 (Implementation Guide)

### 목차
1. [전체 파일 구조](#1-전체-파일-구조)
2. [구현 순서 (Phase별)](#2-구현-순서-phase별)
3. [핵심 파일 구현 예시](#3-핵심-파일-구현-예시)
4. [테스트 전략](#4-테스트-전략)
5. [배포 및 운영](#5-배포-및-운영)
6. [마이그레이션 가이드 (v8.6 → v9.0)](#6-마이그레이션-가이드-v86--v90)

---

## 1. 전체 파일 구조

### 1.1 프로젝트 디렉토리 (v9.0)

```
zerosite_v9_0/
├── app/
│   ├── __init__.py
│   ├── main.py                           # FastAPI 메인 앱
│   │
│   ├── models/                           # Pydantic 모델
│   │   ├── __init__.py
│   │   ├── standard_schema_v9_0.py       # 표준 데이터 스키마
│   │   └── api_models.py                 # API Request/Response 모델
│   │
│   ├── engines/                          # 핵심 분석 엔진
│   │   ├── __init__.py
│   │   ├── gis_engine_v9_0.py            # GIS & POI 분석
│   │   ├── financial_engine_v9_0.py      # 재무 분석 (공사비 연동)
│   │   ├── lh_evaluation_engine_v9_0.py  # LH 110점 평가
│   │   ├── risk_engine_v9_0.py           # 25개 리스크 체크
│   │   └── demand_engine_v9_0.py         # 수요 분석
│   │
│   ├── services/                         # 서비스 레이어
│   │   ├── __init__.py
│   │   ├── normalization_layer_v9_0.py   # 데이터 정규화
│   │   ├── ai_report_writer_v9_0.py      # AI 보고서 Writer
│   │   ├── pdf_renderer_v9_0.py          # PDF Renderer
│   │   ├── pdf_engine_weasy.py           # WeasyPrint 엔진
│   │   ├── pdf_engine_playwright.py      # Playwright 엔진
│   │   ├── visualization_embedder_v9_0.py
│   │   ├── chart_generator_v9_0.py
│   │   ├── tone_selector_v9_0.py
│   │   │
│   │   └── ai_writers/                   # AI Writer 모듈
│   │       ├── __init__.py
│   │       ├── executive_summary_writer.py
│   │       ├── site_overview_writer.py
│   │       ├── gis_accessibility_writer.py
│   │       ├── location_metrics_writer.py
│   │       ├── demand_analysis_writer.py
│   │       ├── regulation_review_writer.py
│   │       ├── construction_feasibility_writer.py
│   │       ├── financial_analysis_writer.py
│   │       ├── lh_evaluation_writer.py
│   │       ├── risk_review_writer.py
│   │       ├── final_decision_writer.py
│   │       └── appendix_writer.py
│   │
│   ├── templates/pdf_v9_0/               # Jinja2 템플릿
│   │   ├── master.html
│   │   ├── sections/                     # 12개 섹션
│   │   │   ├── cover.html
│   │   │   ├── executive_summary.html
│   │   │   ├── site_overview.html
│   │   │   ├── gis_accessibility.html
│   │   │   ├── location_metrics.html
│   │   │   ├── demand_analysis.html
│   │   │   ├── regulation_review.html
│   │   │   ├── construction_feasibility.html
│   │   │   ├── financial_analysis.html
│   │   │   ├── lh_evaluation.html
│   │   │   ├── risk_review.html
│   │   │   ├── final_decision.html
│   │   │   └── appendix.html
│   │   ├── components/                   # 재사용 컴포넌트
│   │   │   ├── table.html
│   │   │   ├── chart.html
│   │   │   ├── kpi_card.html
│   │   │   └── risk_badge.html
│   │   └── styles/
│   │       ├── main.css
│   │       ├── print.css
│   │       └── fonts/
│   │           └── NanumGothic.ttf
│   │
│   ├── api/                              # API 라우터
│   │   ├── __init__.py
│   │   ├── analyze.py                    # /api/analyze-land
│   │   ├── report.py                     # /api/generate-report
│   │   └── health.py                     # /health
│   │
│   ├── utils/                            # 유틸리티
│   │   ├── __init__.py
│   │   ├── kakao_api.py                  # Kakao Maps API
│   │   ├── mois_api.py                   # 국토부 API
│   │   └── helpers.py                    # 헬퍼 함수
│   │
│   └── tests/                            # 테스트
│       ├── __init__.py
│       ├── test_gis_engine_v9_0.py
│       ├── test_financial_engine_v9_0.py
│       ├── test_lh_evaluation_v9_0.py
│       ├── test_ai_report_writer_v9_0.py
│       ├── test_pdf_renderer_v9_0.py
│       └── test_e2e_v9_0.py              # End-to-End 테스트
│
├── static/                               # 정적 파일
│   ├── index.html                        # Frontend UI
│   ├── css/
│   ├── js/
│   └── images/
│
├── docs/                                 # 문서
│   ├── ZEROSITE_V9_0_COMPLETE_ARCHITECTURE.md
│   ├── ZEROSITE_V9_0_ENGINES_SPECIFICATION.md
│   ├── ZEROSITE_V9_0_AI_REPORT_WRITER.md
│   ├── ZEROSITE_V9_0_PDF_RENDERER.md
│   ├── ZEROSITE_V9_0_IMPLEMENTATION_GUIDE.md
│   └── ZEROSITE_V9_0_API_SPECIFICATION.md
│
├── .env                                  # 환경 변수
├── requirements.txt                      # Python 의존성
├── pyproject.toml                        # Poetry 설정 (선택)
├── pytest.ini                            # Pytest 설정
├── README.md
└── docker-compose.yml                    # Docker 배포 (선택)
```

### 1.2 requirements.txt

```txt
# FastAPI & Server
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Pydantic
pydantic==2.5.0
pydantic-settings==2.1.0

# Database (if needed)
sqlalchemy==2.0.23
alembic==1.13.0

# HTTP Clients
httpx==0.25.1
requests==2.31.0

# Data Processing
pandas==2.1.3
numpy==1.26.2

# GIS & Maps
geopy==2.4.0

# PDF Generation
weasyprint==60.1
playwright==1.40.0

# Visualization
matplotlib==3.8.2
plotly==5.18.0

# Templates
jinja2==3.1.2

# AI/LLM (선택)
openai==1.3.7
anthropic==0.7.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.1  # for TestClient

# Utils
python-dotenv==1.0.0
pyyaml==6.0.1
```

---

## 2. 구현 순서 (Phase별)

### Phase 1: 인프라 및 표준 스키마 (1-2일)

**목표**: 프로젝트 기반 구축 및 표준 데이터 모델 정의

#### 작업 항목
1. ✅ 프로젝트 디렉토리 구조 생성
2. ✅ `requirements.txt` 설치
3. ✅ `app/models/standard_schema_v9_0.py` 작성
4. ✅ `app/main.py` 기본 FastAPI 앱 구성
5. ✅ `.env` 파일 및 환경 변수 설정
6. ✅ `/health` 엔드포인트 구현

#### 검증 기준
- `uvicorn app.main:app --reload` 실행 성공
- `http://localhost:8000/health` 응답 200 OK
- `StandardAnalysisOutput` 모델 import 성공

---

### Phase 2: Core Engines 구현 (5-7일)

**목표**: 5개 핵심 분석 엔진 개발

#### 2.1 GIS Engine v9.0 (1일)

```python
# app/engines/gis_engine_v9_0.py 구현
- Kakao Maps API 연동
- POI 거리 계산 (직선 + 도보/차량 시간)
- 접근성 점수 산정 (0-10점)
- 해석 텍스트 생성 ("매우 우수" 등)
```

**테스트**:
```bash
pytest app/tests/test_gis_engine_v9_0.py -v
```

#### 2.2 Financial Engine v9.0 (2일)

```python
# app/engines/financial_engine_v9_0.py 구현
- 토지비 계산: land_appraisal_price × land_area
- 공사비 계산: construction_cost_per_sqm × total_floor_area
- LH 매입가 계산 (50세대 이상): verified_cost + land_price
- Cap Rate, ROI, IRR 계산
- 분석 모드 자동 결정 (LH_LINKED vs STANDARD)
```

**테스트**:
```bash
pytest app/tests/test_financial_engine_v9_0.py -v
```

#### 2.3 LH Evaluation Engine v9.0 (1.5일)

```python
# app/engines/lh_evaluation_engine_v9_0.py 구현
- 110점 만점 체계
  - 입지 (35점)
  - 규모 (20점)
  - 사업성 (40점)
  - 법규 (15점)
- 등급 산정 (S/A/B/C/D/F)
```

#### 2.4 Risk Engine v9.0 (1일)

```python
# app/engines/risk_engine_v9_0.py 구현
- 25개 리스크 항목 체크
  - LEGAL (법률): 6개
  - FINANCIAL (재무): 7개
  - TECHNICAL (기술): 6개
  - MARKET (시장): 6개
- PASS/WARNING/FAIL 판정
```

#### 2.5 Demand Engine v9.0 (0.5일)

```python
# app/engines/demand_engine_v9_0.py 구현
- 인구 데이터 수집 (국토부 API)
- 타겟 가구 수 추정
- 수요 점수 산정 (0-100점)
```

#### 검증 기준
- 각 Engine별 단위 테스트 PASS
- `StandardAnalysisOutput` 형식으로 출력
- 무한대/NaN 값 ZERO

---

### Phase 3: Normalization Layer & AI Writer (3-4일)

**목표**: 데이터 정규화 및 AI 보고서 생성

#### 3.1 Normalization Layer (1일)

```python
# app/services/normalization_layer_v9_0.py 구현
- 각 Engine 출력 → 표준 스키마 변환
- KeyError 방지 로직
- 기본값 처리 (fallback)
```

#### 3.2 AI Report Writer (2-3일)

```python
# app/services/ai_report_writer_v9_0.py 구현
# app/services/ai_writers/*.py 구현 (12개 Writer)

- LLM API 연동 (GPT-4 / Claude)
- 프롬프트 엔지니어링
- 톤 & 스타일 적용
```

#### 검증 기준
- 12개 챕터 모두 텍스트 생성 성공
- 전문적이고 읽기 쉬운 문장
- 데이터 정확히 반영

---

### Phase 4: PDF Renderer (3-4일)

**목표**: 12-Section 모듈형 PDF 생성

#### 4.1 HTML 템플릿 작성 (2일)

```
app/templates/pdf_v9_0/ 구현
- master.html
- sections/*.html (12개)
- components/*.html
- styles/*.css
```

#### 4.2 PDF 엔진 구현 (1일)

```python
# app/services/pdf_renderer_v9_0.py
# app/services/pdf_engine_weasy.py
# app/services/pdf_engine_playwright.py
```

#### 4.3 시각화 통합 (1일)

```python
# app/services/chart_generator_v9_0.py
# app/services/visualization_embedder_v9_0.py

- CAPEX Pie Chart
- 10년 현금흐름 Chart
- 민감도 히트맵
- LH 점수 Radar Chart
```

#### 검증 기준
- PDF 생성 성공 (60+ 페이지)
- KeyError ZERO
- 한글 폰트 정상 표시
- 시각화 자동 삽입

---

### Phase 5: API & Integration (2-3일)

**목표**: REST API 구현 및 전체 통합

#### 5.1 API 엔드포인트 구현 (1일)

```python
# app/api/analyze.py
@router.post("/api/analyze-land")
async def analyze_land(request: LandAnalysisRequest):
    # 1. GIS Engine
    # 2. Financial Engine
    # 3. LH Evaluation Engine
    # 4. Risk Engine
    # 5. Demand Engine
    # 6. Normalization Layer
    return StandardAnalysisOutput

# app/api/report.py
@router.post("/api/generate-report")
async def generate_report(request: ReportRequest):
    # 1. AI Report Writer
    # 2. PDF Renderer
    return {"pdf_url": "...", "html": "..."}
```

#### 5.2 End-to-End 테스트 (1-2일)

```python
# app/tests/test_e2e_v9_0.py

def test_full_workflow():
    # API → Engine → Normalization → AI Writer → PDF
    response = client.post("/api/analyze-land", json={...})
    assert response.status_code == 200
    
    report_response = client.post("/api/generate-report", json={...})
    assert report_response.status_code == 200
    assert "pdf_url" in report_response.json()
```

#### 검증 기준
- `/api/analyze-land` 성공
- `/api/generate-report` 성공
- 전체 프로세스 5분 이내 완료

---

### Phase 6: Frontend UI 업데이트 (2일)

**목표**: UI를 v9.0 JSON 구조에 맞게 재구성

#### 작업 항목
1. `static/index.html` 수정
   - v8.5/v9.0 API 응답 구조 반영
   - `unit_count`, `analysis_mode`, `lh_scores` 표시
   - POI 거리 (`distance_display`) 표시
2. v7.5 dummy 데이터 완전 제거
3. 실시간 분석 결과 바인딩

#### 검증 기준
- UI에 v9.0 실제 데이터 표시
- v7.5 흔적 ZERO

---

### Phase 7: 테스트 & QA (3일)

**목표**: 전체 시스템 안정성 검증

#### 7.1 단위 테스트 (1일)
```bash
pytest app/tests/ -v --cov=app --cov-report=html
# 목표: Coverage 80% 이상
```

#### 7.2 통합 테스트 (1일)
- 다양한 주소 입력 테스트 (서울, 경기, 부산, ...)
- 50세대 이상/미만 케이스
- POI 거리 정확성
- 재무 지표 검증

#### 7.3 성능 테스트 (1일)
- 분석 속도: < 30초 목표
- PDF 생성 속도: < 2분 목표
- 동시 요청 처리: 5-10 req/sec

---

### Phase 8: 배포 (1일)

**목표**: 프로덕션 배포

#### 작업 항목
1. Docker 이미지 빌드
2. 환경 변수 설정 (`.env.production`)
3. 서버 배포 (AWS / GCP / Azure)
4. HTTPS 설정
5. 모니터링 설정

---

## 3. 핵심 파일 구현 예시

### 3.1 app/main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import analyze, report, health
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ZeroSite v9.0 Ultra-Pro",
    description="LH 신축매입임대 토지진단 자동화 시스템",
    version="9.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(health.router, tags=["Health"])
app.include_router(analyze.router, tags=["Analysis"])
app.include_router(report.router, tags=["Report"])

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 ZeroSite v9.0 Ultra-Pro 시작")
    logger.info("✅ 모든 엔진 초기화 완료")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 ZeroSite v9.0 종료")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3.2 app/api/analyze.py

```python
from fastapi import APIRouter, HTTPException
from app.models.api_models import LandAnalysisRequest, LandAnalysisResponse
from app.models.standard_schema_v9_0 import StandardAnalysisOutput
from app.engines.gis_engine_v9_0 import GISEngineV90
from app.engines.financial_engine_v9_0 import FinancialEngineV90
from app.engines.lh_evaluation_engine_v9_0 import LHEvaluationEngineV90
from app.engines.risk_engine_v9_0 import RiskEngineV90
from app.engines.demand_engine_v9_0 import DemandEngineV90
from app.services.normalization_layer_v9_0 import NormalizationLayerV90
import logging
from datetime import datetime
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/api/analyze-land", response_model=LandAnalysisResponse)
async def analyze_land(request: LandAnalysisRequest):
    """
    토지 분석 API (v9.0)
    
    - GIS 분석
    - 재무 분석 (공사비 연동제 포함)
    - LH 평가 (110점)
    - 리스크 평가 (25개 항목)
    - 수요 분석
    """
    try:
        analysis_id = str(uuid.uuid4())
        logger.info(f"[{analysis_id}] 분석 시작: {request.address}")
        
        # 1. GIS Engine
        logger.info(f"[{analysis_id}] GIS 분석 시작")
        gis_engine = GISEngineV90()
        gis_raw = gis_engine.analyze(
            address=request.address,
            latitude=request.latitude,
            longitude=request.longitude
        )
        
        # 2. Financial Engine
        logger.info(f"[{analysis_id}] 재무 분석 시작")
        financial_engine = FinancialEngineV90()
        financial_raw = financial_engine.analyze(
            land_area=request.land_area,
            land_appraisal_price=request.land_appraisal_price,
            zone_type=request.zone_type,
            unit_type=request.unit_type
        )
        
        # 3. LH Evaluation Engine
        logger.info(f"[{analysis_id}] LH 평가 시작")
        lh_engine = LHEvaluationEngineV90()
        lh_raw = lh_engine.evaluate(
            gis_data=gis_raw,
            financial_data=financial_raw,
            site_info={
                "address": request.address,
                "land_area": request.land_area,
                "zone_type": request.zone_type
            }
        )
        
        # 4. Risk Engine
        logger.info(f"[{analysis_id}] 리스크 평가 시작")
        risk_engine = RiskEngineV90()
        risk_raw = risk_engine.assess(
            financial_data=financial_raw,
            lh_data=lh_raw,
            site_info={...}
        )
        
        # 5. Demand Engine
        logger.info(f"[{analysis_id}] 수요 분석 시작")
        demand_engine = DemandEngineV90()
        demand_raw = demand_engine.analyze(
            address=request.address,
            unit_type=request.unit_type
        )
        
        # 6. Normalization Layer (표준 스키마 변환)
        logger.info(f"[{analysis_id}] 데이터 정규화 시작")
        normalizer = NormalizationLayerV90()
        
        standard_output = StandardAnalysisOutput(
            analysis_id=analysis_id,
            version="v9.0",
            timestamp=datetime.now().isoformat(),
            site_info=normalizer.normalize_site_info(request),
            gis_result=normalizer.normalize_gis_output(gis_raw),
            financial_result=normalizer.normalize_financial_output(
                financial_raw, 
                unit_count=financial_raw.get("unit_count", 0)
            ),
            lh_scores=normalizer.normalize_lh_scores(lh_raw),
            risk_assessment=normalizer.normalize_risk_assessment(risk_raw),
            demand_result=normalizer.normalize_demand(demand_raw),
            final_recommendation=normalizer.generate_recommendation(
                lh_raw, financial_raw, risk_raw
            )
        )
        
        logger.info(f"[{analysis_id}] 분석 완료")
        return LandAnalysisResponse(
            success=True,
            data=standard_output
        )
        
    except Exception as e:
        logger.error(f"분석 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

### 3.3 app/api/report.py

```python
from fastapi import APIRouter, HTTPException
from app.models.api_models import ReportRequest, ReportResponse
from app.services.ai_report_writer_v9_0 import AIReportWriterV90
from app.services.pdf_renderer_v9_0 import PDFRendererV90
from app.services.chart_generator_v9_0 import ChartGeneratorV90
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/api/generate-report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """
    보고서 생성 API (v9.0)
    
    - AI Writer로 텍스트 생성
    - 시각화 차트 생성
    - 12-Section PDF 렌더링
    """
    try:
        logger.info(f"보고서 생성 시작: {request.analysis_id}")
        
        # 1. AI Report Writer
        logger.info("AI 텍스트 생성 중...")
        ai_writer = AIReportWriterV90(
            llm_provider="gpt-4",
            tone=request.tone or "professional"
        )
        ai_text = ai_writer.generate_full_report(request.data)
        
        # 2. 시각화 생성
        logger.info("시각화 차트 생성 중...")
        chart_gen = ChartGeneratorV90()
        visualizations = chart_gen.generate_all_charts(request.data)
        
        # 3. PDF 렌더링
        logger.info("PDF 렌더링 중...")
        pdf_renderer = PDFRendererV90()
        html_content = pdf_renderer.render_full_report(
            data=request.data,
            ai_text=ai_text,
            visualizations=visualizations
        )
        
        # 4. PDF 파일 생성
        pdf_path = f"/tmp/reports/{request.analysis_id}.pdf"
        pdf_renderer.generate_pdf(html_content, pdf_path)
        
        logger.info(f"보고서 생성 완료: {pdf_path}")
        return ReportResponse(
            success=True,
            pdf_url=f"/api/reports/{request.analysis_id}.pdf",
            html=html_content,
            metadata={
                "analysis_id": request.analysis_id,
                "version": "v9.0",
                "pages": 60,  # estimate
                "size_kb": 5120  # estimate
            }
        )
        
    except Exception as e:
        logger.error(f"보고서 생성 중 오류: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 4. 테스트 전략

### 4.1 테스트 피라미드

```
       /\
      /E2E\        (10%) - End-to-End 테스트
     /------\
    /Integr-\     (30%) - 통합 테스트
   /----------\
  /Unit  Tests \  (60%) - 단위 테스트
 /--------------\
```

### 4.2 단위 테스트 예시

```python
# app/tests/test_financial_engine_v9_0.py

import pytest
from app.engines.financial_engine_v9_0 import FinancialEngineV90

def test_lh_linked_mode_detection():
    """50세대 이상 → LH_LINKED 모드 자동 감지"""
    engine = FinancialEngineV90()
    result = engine.analyze(
        land_area=1000,
        land_appraisal_price=5000000,
        zone_type="제3종일반주거지역",
        unit_type="든든전세"
    )
    
    # 60세대 건설 가능한 경우
    if result["unit_count"] >= 50:
        assert result["analysis_mode"] == "LH_LINKED"
        assert "lh_purchase_price" in result
        assert "verified_cost" in result
    else:
        assert result["analysis_mode"] == "STANDARD"

def test_land_price_calculation():
    """토지가격 = 감정평가액 × 면적"""
    engine = FinancialEngineV90()
    result = engine.analyze(
        land_area=660.0,
        land_appraisal_price=5000000,
        zone_type="제3종일반주거지역",
        unit_type="든든전세"
    )
    
    expected_land_price = 660.0 * 5000000
    assert result["total_land_price"] == pytest.approx(expected_land_price)

def test_no_infinity_values():
    """무한대 값 발생 금지"""
    engine = FinancialEngineV90()
    result = engine.analyze(
        land_area=500,
        land_appraisal_price=3000000,
        zone_type="제2종일반주거지역",
        unit_type="통합공공임대"
    )
    
    for key, value in result.items():
        if isinstance(value, (int, float)):
            assert not math.isinf(value), f"{key} has infinity value"
            assert not math.isnan(value), f"{key} has NaN value"
```

### 4.3 통합 테스트 예시

```python
# app/tests/test_integration_v9_0.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analyze_land_integration():
    """토지 분석 API 통합 테스트"""
    response = client.post("/api/analyze-land", json={
        "address": "서울시 마포구 월드컵북로 120",
        "land_area": 660.0,
        "land_appraisal_price": 5000000,
        "zone_type": "제3종일반주거지역",
        "unit_type": "든든전세"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["version"] == "v9.0"
    
    # 핵심 필드 존재 확인
    assert "site_info" in data["data"]
    assert "gis_result" in data["data"]
    assert "financial_result" in data["data"]
    assert "lh_scores" in data["data"]
    assert "risk_assessment" in data["data"]
    
    # LH 점수 범위 검증
    lh_scores = data["data"]["lh_scores"]
    assert 0 <= lh_scores["total_score"] <= 110

def test_generate_report_integration():
    """보고서 생성 통합 테스트"""
    # 1. 먼저 분석 수행
    analyze_response = client.post("/api/analyze-land", json={...})
    analysis_data = analyze_response.json()["data"]
    
    # 2. 보고서 생성
    report_response = client.post("/api/generate-report", json={
        "analysis_id": analysis_data["analysis_id"],
        "data": analysis_data,
        "tone": "professional"
    })
    
    assert report_response.status_code == 200
    report = report_response.json()
    
    assert report["success"] is True
    assert "pdf_url" in report
    assert "html" in report
    assert len(report["html"]) > 10000  # 충분한 길이의 HTML
```

---

## 5. 배포 및 운영

### 5.1 Docker 배포

```dockerfile
# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치 (WeasyPrint 의존성)
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libjpeg-dev \
    libopenjp2-7-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml

version: '3.8'

services:
  zerosite:
    build: .
    ports:
      - "8000:8000"
    environment:
      - KAKAO_API_KEY=${KAKAO_API_KEY}
      - MOIS_API_KEY=${MOIS_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./reports:/app/reports
    restart: unless-stopped
```

### 5.2 모니터링

```python
# app/middleware/monitoring.py

from fastapi import Request
import time
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.2f}s "
        f"with status {response.status_code}"
    )
    
    return response
```

---

## 6. 마이그레이션 가이드 (v8.6 → v9.0)

### 6.1 데이터 호환성

| v8.6 필드 | v9.0 필드 | 변환 로직 |
|-----------|-----------|----------|
| `financial_result.price_per_unit_lh` | `financial_result.lh_purchase_price_per_sqm` | 직접 대체 |
| `financial_result.gap_percentage` | (삭제) | v9.0에서 제거됨 |
| `accessibility.elementary_school_distance` | `gis_result.elementary_schools[0].distance_display` | 포맷 변경 |
| `lh_scores_v85` | `lh_scores` | 구조 동일 |

### 6.2 마이그레이션 스크립트

```python
# scripts/migrate_v86_to_v90.py

def migrate_analysis_data(v86_data: dict) -> dict:
    """v8.6 분석 데이터 → v9.0 포맷 변환"""
    
    v90_data = {
        "analysis_id": v86_data["analysis_id"],
        "version": "v9.0",
        "timestamp": v86_data["timestamp"],
        
        "site_info": {
            "address": v86_data["address"],
            "land_area": v86_data["land_area"],
            # ... (매핑 계속)
        },
        
        "financial_result": {
            "total_capex": v86_data["financial_result"]["total_capex"],
            # v8.6의 price_per_unit_lh → v9.0의 lh_purchase_price_per_sqm
            "lh_purchase_price_per_sqm": v86_data["financial_result"].get("price_per_unit_lh"),
            # gap_percentage는 제거
        },
        
        # ... (나머지 필드 매핑)
    }
    
    return v90_data
```

---

## 7. 체크리스트 (최종 배포 전)

### 7.1 기능 체크리스트

- [ ] GIS Engine: POI 거리 정확, 무한대 값 ZERO
- [ ] Financial Engine: 공사비 연동제 적용, LH 매입가 정확
- [ ] LH Evaluation: 110점 평가 정확
- [ ] Risk Engine: 25개 항목 체크 완료
- [ ] AI Writer: 12개 챕터 모두 생성
- [ ] PDF Renderer: KeyError ZERO, 한글 폰트 정상
- [ ] API: `/api/analyze-land`, `/api/generate-report` 정상 작동
- [ ] Frontend UI: v9.0 데이터 정확히 표시

### 7.2 성능 체크리스트

- [ ] 분석 속도: < 30초
- [ ] PDF 생성 속도: < 2분
- [ ] 메모리 사용량: < 2GB
- [ ] 동시 요청 처리: 5+ req/sec

### 7.3 보안 체크리스트

- [ ] API 키 환경 변수 처리
- [ ] SQL Injection 방지
- [ ] CORS 설정 적절
- [ ] HTTPS 적용

---

## 다음 단계: Part 6 (API Specification)

Part 5에서는 **전체 구현 순서 및 파일 구조**를 완성했습니다.
Part 6에서는 **REST API 전체 명세서**를 작성합니다.

---

**문서 종료**
