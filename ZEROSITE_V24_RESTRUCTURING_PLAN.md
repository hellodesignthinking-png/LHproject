# 🟣 ZeroSite v24 - 전체 프로젝트 재구성 계획

**작성일**: 2025-12-12  
**현재 버전**: v3.3.0 → v24.0.0 전환  
**목표**: 기획서 기반 모듈화 + 체계적 아키텍처 재설계

---

## 📌 Executive Summary

현재 ZeroSite v3.3.0은 **Expert Edition A/B Comparison** 중심으로 개발되어 있으나,
최종 기획서에서 제시한 **ZeroSite v24 Full Specification**과는 구조적 차이가 있습니다.

이 문서는:
1. **현재 시스템 분석** (v3.3.0)
2. **기획서 기반 목표 구조** (v24.0.0)
3. **모듈별 재구성 계획**
4. **마이그레이션 로드맵**

을 제공합니다.

---

## 🔍 PART 1: 현재 시스템 분석 (v3.3.0)

### 1.1 현재 구조
```
/home/user/webapp/
├── backend/services_v9/          # 백엔드 엔진 (7개)
│   ├── financial_analysis_engine.py
│   ├── cost_estimation_engine.py
│   ├── market_data_processor.py
│   ├── ab_scenario_engine.py
│   ├── expert_v3_generator.py
│   ├── expert_v3_pdf_generator.py
│   └── genspark_prompt_generator.py
├── app/services_v13/report_full/ # v23 리포트 스타일
│   ├── section_03_1_ab_comparison.html
│   └── v3_2_ab_comparison.css
├── public/reports/                # 생성된 리포트
├── v23_server.py                 # FastAPI 서버
└── TEST_V33_QA.sh                # QA 스크립트
```

### 1.2 현재 구현된 엔진 (7개)
1. ✅ Financial Analysis Engine v3.2
2. ✅ Cost Estimation Engine v3.2
3. ✅ Market Data Processor v3.2
4. ✅ A/B Scenario Engine v3.2
5. ✅ GenSpark Prompt Generator
6. ✅ FAR Chart Generator
7. ✅ Market Histogram Generator

### 1.3 누락된 엔진 (기획서 기준)
1. ❌ Zoning Engine (용도지역 분류)
2. ❌ FAR Engine (용적률 계산)
3. ❌ Relaxation Engine (완화 규정)
4. ❌ **Capacity Engine (건축물 규모 검토)** ← v24 핵심
5. ❌ Unit Type Engine (유형 추천)
6. ❌ Appraisal Engine (감정평가)
7. ❌ Risk Engine (리스크 분석)
8. ❌ Multi-Parcel Engine (합필 분석)
9. ❌ Alias Engine (보고서 alias)

### 1.4 현재 보고서
- ✅ Expert v3.2 Report (HTML + PDF)
- ✅ A/B Comparison Report (Section 03-1)
- ❌ Landowner Brief (3p)
- ❌ LH Submission (8-12p)
- ❌ Policy Impact (15p)
- ❌ Developer Feasibility (15-20p)

---

## 🎯 PART 2: 목표 구조 (v24.0.0)

### 2.1 ZeroSite v24 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    ZeroSite v24 OS                          │
│          LH 신축매입임대 토지진단 자동화 플랫폼                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   INPUT LAYER (입력)                         │
│  - 주소 (address)                                            │
│  - 토지면적 (land_area_sqm)                                  │
│  - 용도지역 (zone_type)                                      │
│  - BCR/FAR Legal (bcr_legal, far_legal)                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              CORE ENGINE LAYER (엔진 13종)                   │
│                                                             │
│  [1] Zoning Engine        - 용도지역 자동 분류                │
│  [2] FAR Engine           - 법정/완화/최종 용적률 계산         │
│  [3] Relaxation Engine    - 완화 규정 6종 자동 적용           │
│  [4] Capacity Engine      - 건축물 규모 검토 (v24 핵심)        │
│  [5] Unit Type Engine     - 청년/신혼/고령 유형 추천           │
│  [6] Market Engine        - 실거래가 분석                     │
│  [7] Appraisal Engine     - 토지 감정평가                     │
│  [8] Verified Cost Engine - LH 기준 공사비 산정               │
│  [9] Financial Engine     - ROI/IRR/NPV 계산                │
│  [10] Risk Engine         - 5대 리스크 평가                   │
│  [11] Scenario Engine     - A/B/C 시나리오 비교              │
│  [12] Multi-Parcel Engine - 합필 분석                        │
│  [13] Alias Engine        - 보고서 alias 150개               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           VISUALIZATION LAYER (시각화 6종)                   │
│                                                             │
│  [1] FAR Change Chart         - 용적률 변화 그래프            │
│  [2] Market Histogram         - 시장 분포 히스토그램          │
│  [3] Financial Waterfall      - 재무 폭포 차트               │
│  [4] Risk Heatmap            - 리스크 히트맵                 │
│  [5] Type Distribution       - 유형 분포 차트                │
│  [6] Capacity Simulation     - 건축물 규모 시뮬레이션         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              REPORT LAYER (보고서 5종)                       │
│                                                             │
│  [1] Landowner Brief          - 3페이지 (토지주용)           │
│  [2] LH Submission            - 8-12페이지 (LH 제출용)       │
│  [3] Extended Professional    - 25-40페이지 (전문가용)       │
│  [4] Policy Impact            - 15페이지 (정책 효과)         │
│  [5] Developer Feasibility    - 15-20페이지 (개발자용)       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 API LAYER (FastAPI v24)                     │
│                                                             │
│  POST /api/v24/diagnose-land       - 토지 진단              │
│  POST /api/v24/capacity            - 건축물 규모 검토        │
│  POST /api/v24/appraisal           - 감정평가               │
│  POST /api/v24/scenario            - A/B/C 시나리오         │
│  POST /api/v24/report              - 보고서 생성            │
│  GET  /api/v24/health              - 서버 상태              │
│  GET  /api/v24/docs                - API 문서               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              DASHBOARD LAYER (UI)                           │
│                                                             │
│  - 토지 진단하기                                              │
│  - 건축물 규모 검토                                           │
│  - 토지 감정평가                                              │
│  - 시나리오 비교 A/B/C                                        │
│  - 보고서 다운로드                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 목표 폴더 구조 (v24.0.0)

```
/home/user/webapp/
├── app/
│   ├── engines/                    # 엔진 13종
│   │   ├── __init__.py
│   │   ├── zoning_engine.py        # [NEW]
│   │   ├── far_engine.py           # [NEW]
│   │   ├── relaxation_engine.py    # [NEW]
│   │   ├── capacity_engine.py      # [NEW] ★ v24 핵심
│   │   ├── unit_type_engine.py     # [NEW]
│   │   ├── market_engine.py        # [MIGRATE] from market_data_processor
│   │   ├── appraisal_engine.py     # [NEW]
│   │   ├── verified_cost_engine.py # [MIGRATE] from cost_estimation_engine
│   │   ├── financial_engine.py     # [MIGRATE] from financial_analysis_engine
│   │   ├── risk_engine.py          # [NEW]
│   │   ├── scenario_engine.py      # [MIGRATE] from ab_scenario_engine
│   │   ├── multiparcel_engine.py   # [NEW]
│   │   └── alias_engine.py         # [NEW]
│   │
│   ├── visualization/              # 시각화 6종
│   │   ├── __init__.py
│   │   ├── far_chart.py           # [MIGRATE]
│   │   ├── market_histogram.py    # [MIGRATE]
│   │   ├── financial_waterfall.py # [NEW]
│   │   ├── risk_heatmap.py        # [NEW]
│   │   ├── type_distribution.py   # [NEW]
│   │   └── capacity_simulation.py # [NEW]
│   │
│   ├── report/                     # 보고서 5종
│   │   ├── templates/
│   │   │   ├── cover.html
│   │   │   ├── layout_brief.html         # [NEW] Report 1
│   │   │   ├── layout_lh.html            # [NEW] Report 2
│   │   │   ├── layout_extended.html      # [NEW] Report 3
│   │   │   ├── layout_policy.html        # [NEW] Report 4
│   │   │   └── layout_developer.html     # [NEW] Report 5
│   │   ├── css/
│   │   │   ├── report_base.css
│   │   │   ├── lh_blue.css
│   │   │   └── v24_design_system.css     # [NEW]
│   │   └── generators/
│   │       ├── brief_generator.py
│   │       ├── lh_generator.py
│   │       ├── extended_generator.py
│   │       ├── policy_generator.py
│   │       └── developer_generator.py
│   │
│   └── api/                        # API Layer
│       ├── v24_server.py           # [NEW] FastAPI 서버
│       ├── routers/
│       │   ├── land.py             # 토지 진단 API
│       │   ├── capacity.py         # 건축물 규모 API
│       │   ├── appraisal.py        # 감정평가 API
│       │   ├── scenario.py         # 시나리오 API
│       │   └── report.py           # 보고서 API
│       └── middleware/
│           ├── error_handler.py
│           └── logging.py
│
├── public/                         # Frontend
│   ├── dashboard.html              # [NEW] 메인 대시보드
│   ├── test.html                   # [KEEP] 테스트 페이지
│   ├── styles.css
│   ├── script.js
│   └── reports/                    # 생성된 보고서
│
├── backend/                        # Legacy (v3.3.0)
│   └── services_v9/                # [DEPRECATED] 이전 버전
│
├── tests/                          # 테스트 코드
│   ├── test_engines.py
│   ├── test_visualization.py
│   ├── test_reports.py
│   └── test_api.py
│
├── docs/                           # 문서
│   ├── MASTER_DEVELOPMENT_PLAN.md
│   ├── PROJECT_STATUS_SUMMARY.md
│   ├── EXECUTIVE_BRIEFING.md
│   ├── ZEROSITE_V24_FULL_SPEC.md   # [NEW] 기획서
│   └── API_DOCUMENTATION.md
│
├── config/                         # 설정
│   ├── settings.py
│   └── constants.py
│
├── requirements.txt
├── README.md
└── v24_server.py                   # [NEW] 메인 서버
```

---

## 🔧 PART 3: 모듈별 재구성 계획

### 3.1 Core Engines (13개 모듈)

#### Module 1: Zoning Engine
**파일**: `app/engines/zoning_engine.py`  
**목적**: 용도지역 자동 분류 및 BCR/FAR 기본값 반환  
**상태**: 신규 개발 필요

**요구사항**:
```python
class ZoningEngine:
    def classify_zone(self, zone_input: str) -> dict:
        """
        용도지역 분류
        Input: "제1종일반주거지역"
        Output: {
            "zone_type": "residential_1",
            "bcr": 60,
            "far_legal": 150
        }
        """
        pass
    
    def get_base_regulations(self, zone_type: str) -> dict:
        """
        용도지역별 기본 규제 반환
        """
        pass
```

**우선순위**: HIGH (다른 엔진의 기반)

---

#### Module 2: FAR Engine
**파일**: `app/engines/far_engine.py`  
**목적**: 법정/완화/최종 용적률 계산  
**상태**: 신규 개발 필요

**요구사항**:
```python
class FAREngine:
    def calculate_legal_far(self, zone_type: str) -> float:
        """법정 용적률"""
        pass
    
    def calculate_relaxed_far(self, legal_far: float, relaxations: list) -> float:
        """완화된 용적률"""
        pass
    
    def calculate_final_far(self, legal_far: float, relaxations: list) -> dict:
        """
        Output: {
            "far_legal": 200,
            "far_relaxation": 50,
            "far_final": 250
        }
        """
        pass
```

**우선순위**: HIGH (Capacity Engine 전제조건)

---

#### Module 3: Relaxation Engine
**파일**: `app/engines/relaxation_engine.py`  
**목적**: 용적률 완화 규정 6종 자동 적용  
**상태**: 신규 개발 필요

**요구사항**:
```python
class RelaxationEngine:
    RELAXATION_RULES = {
        "subway_proximity": 20,    # 역세권 +20%p
        "youth_housing": 20,       # 청년주택 +20%p
        "newlywed_housing": 15,    # 신혼부부 +15%p
        "happiness_housing": 30,   # 행복주택 +30%p
        "semi_residential": 50,    # 준주거 특례 +50%p
        "public_contribution": 10  # 공공기여 +10%p
    }
    
    def apply_relaxations(self, base_far: float, applicable_rules: list) -> dict:
        """
        완화 규정 적용
        """
        pass
```

**우선순위**: HIGH

---

#### Module 4: Capacity Engine ★ (v24 핵심)
**파일**: `app/engines/capacity_engine.py`  
**목적**: 건축물 규모 검토 (연면적, 층수, 세대수, 주차 등)  
**상태**: **신규 개발 필요 (v24 최우선 과제)**

**요구사항**:
```python
class CapacityEngine:
    def calculate_buildable_area(self, land_area: float, far: float) -> float:
        """연면적 = 토지면적 × 용적률"""
        return land_area * (far / 100)
    
    def suggest_floors(self, buildable_area: float, footprint: float) -> int:
        """층수 자동 제안 (5/7/10층 중 선택)"""
        pass
    
    def suggest_buildings(self, land_area: float, regulations: dict) -> int:
        """동수 자동 제안"""
        pass
    
    def calculate_unit_count(
        self, 
        buildable_area: float, 
        unit_type: str
    ) -> int:
        """
        세대수 자동 산출
        유형별 평균 전용면적:
        - 청년: 36㎡
        - 신혼: 46㎡
        - 고령: 40㎡
        """
        pass
    
    def calculate_parking(self, unit_count: int, zone_type: str) -> int:
        """주차대수 자동 계산"""
        pass
    
    def check_daylight(self, floors: int, building_distance: float) -> str:
        """일조권 간이 체크"""
        pass
    
    def generate_capacity_report(self, land_area: float, far: float, unit_type: str) -> dict:
        """
        종합 건축물 규모 검토 보고서
        
        Output: {
            "buildable_area": 4982.3,
            "floors": 7,
            "buildings": 1,
            "unit_count": 63,
            "parking_required": 32,
            "daylight_check": "OK",
            "bcr_used": 58.3,
            "far_used": 248.7
        }
        """
        pass
```

**우선순위**: **CRITICAL** (v24의 핵심 기능)

---

#### Module 5: Unit Type Engine
**파일**: `app/engines/unit_type_engine.py`  
**목적**: 청년/신혼/고령/고시원/일반 5종 유형 추천  
**상태**: 신규 개발 필요

**요구사항**:
```python
class UnitTypeEngine:
    UNIT_TYPES = {
        "youth": {"area": 36, "weight": 1.2},
        "newlywed": {"area": 46, "weight": 1.5},
        "elderly": {"area": 40, "weight": 1.0},
        "gosiwon": {"area": 14, "weight": 0.8},
        "general": {"area": 59, "weight": 1.0}
    }
    
    def calculate_type_score(self, land_area: float, location: dict) -> dict:
        """유형별 점수 계산 (0-100점)"""
        pass
    
    def recommend_type(self, scores: dict) -> str:
        """최적 유형 추천"""
        pass
```

**우선순위**: MEDIUM

---

#### Module 6: Market Engine
**파일**: `app/engines/market_engine.py`  
**목적**: 실거래가 분석 및 시장 통계  
**상태**: **마이그레이션 필요** (from `backend/services_v9/market_data_processor.py`)

**요구사항**:
```python
class MarketEngine:
    def fetch_transaction_data(self, address: str, radius: int) -> list:
        """실거래 데이터 수집"""
        pass
    
    def calculate_statistics(self, transactions: list) -> dict:
        """
        Output: {
            "mean": 15000000,
            "median": 14500000,
            "std_dev": 2500000,
            "cv": 0.167,
            "confidence": "HIGH"
        }
        """
        pass
    
    def generate_fallback_data(self, district: str) -> dict:
        """데이터 없을 경우 합성 데이터 생성"""
        pass
```

**우선순위**: MEDIUM (기존 코드 활용 가능)

---

#### Module 7: Appraisal Engine
**파일**: `app/engines/appraisal_engine.py`  
**목적**: 토지 감정평가  
**상태**: 신규 개발 필요

**요구사항**:
```python
class AppraisalEngine:
    def calculate_base_value(self, area: float, standard_price: float) -> float:
        """표준지 기반 기본 평가액"""
        pass
    
    def apply_adjustments(self, base_value: float, factors: dict) -> float:
        """
        보정 요인 적용:
        - 도로 조건
        - 형상
        - 용도지역
        - 거래 사례
        """
        pass
    
    def generate_appraisal_report(self, land_data: dict) -> dict:
        """
        Output: {
            "base_value": 1000000000,
            "adjusted_value": 1050000000,
            "confidence": "MEDIUM",
            "adjustments": [...]
        }
        """
        pass
```

**우선순위**: HIGH (LH 제출 필수)

---

#### Module 8: Verified Cost Engine
**파일**: `app/engines/verified_cost_engine.py`  
**목적**: LH 기준 공사비 산정  
**상태**: **마이그레이션 필요** (from `backend/services_v9/cost_estimation_engine.py`)

**요구사항**:
```python
class VerifiedCostEngine:
    LH_2024_UNIT_COSTS = {
        "youth": 3500000,      # ㎡당 공사비
        "newlywed": 3800000,
        "elderly": 3600000
    }
    
    def calculate_construction_cost(self, buildable_area: float, unit_type: str) -> float:
        """공사비 계산"""
        pass
    
    def calculate_indirect_costs(self, construction_cost: float) -> dict:
        """간접비 (설계비, 감리비, 제세공과금)"""
        pass
    
    def calculate_financing_costs(self, total_cost: float, duration: int) -> float:
        """금융비용"""
        pass
    
    def generate_cost_breakdown(self, land_data: dict) -> dict:
        """
        Output: {
            "land_cost": 1000000000,
            "construction_cost": 1800000000,
            "indirect_costs": 180000000,
            "financing_costs": 120000000,
            "total_capex": 3100000000
        }
        """
        pass
```

**우선순위**: HIGH (재무 분석 전제조건)

---

#### Module 9: Financial Engine
**파일**: `app/engines/financial_engine.py`  
**목적**: ROI/IRR/NPV/Payback 계산  
**상태**: **마이그레이션 필요** (from `backend/services_v9/financial_analysis_engine.py`)

**요구사항**:
```python
class FinancialEngine:
    def calculate_roi(self, profit: float, investment: float) -> float:
        """ROI (%) = (수익 / 투자) × 100"""
        pass
    
    def calculate_irr(self, cash_flows: list) -> float:
        """IRR 계산"""
        pass
    
    def calculate_npv(self, cash_flows: list, discount_rate: float) -> float:
        """NPV 계산"""
        pass
    
    def calculate_payback_period(self, investment: float, annual_cash_flow: float) -> float:
        """회수 기간"""
        pass
    
    def generate_financial_report(self, project_data: dict) -> dict:
        """
        Output: {
            "roi": 12.5,
            "irr": 8.3,
            "npv": 150000000,
            "payback_years": 7.2,
            "profitability": "MODERATE"
        }
        """
        pass
```

**우선순위**: HIGH

---

#### Module 10: Risk Engine
**파일**: `app/engines/risk_engine.py`  
**목적**: 5대 리스크 평가 (재무/시장/설계/정책/법규)  
**상태**: 신규 개발 필요

**요구사항**:
```python
class RiskEngine:
    RISK_CATEGORIES = [
        "financial",      # 재무 리스크
        "market",         # 시장 리스크
        "design",         # 설계 리스크
        "policy",         # 정책 리스크
        "regulatory"      # 법규 리스크
    ]
    
    def assess_risk(self, category: str, project_data: dict) -> dict:
        """
        개별 리스크 평가 (0-100점)
        
        Output: {
            "category": "financial",
            "score": 35,
            "level": "MEDIUM",
            "factors": [...]
        }
        """
        pass
    
    def generate_risk_heatmap(self, all_risks: dict) -> str:
        """리스크 히트맵 (base64 이미지)"""
        pass
    
    def generate_risk_report(self, project_data: dict) -> dict:
        """
        종합 리스크 보고서
        
        Output: {
            "overall_score": 42,
            "overall_level": "MEDIUM-LOW",
            "risks": {
                "financial": {...},
                "market": {...},
                ...
            },
            "heatmap": "data:image/png;base64,..."
        }
        """
        pass
```

**우선순위**: MEDIUM

---

#### Module 11: Scenario Engine
**파일**: `app/engines/scenario_engine.py`  
**목적**: A/B/C 시나리오 비교 (청년/신혼/고령)  
**상태**: **마이그레이션 + 확장 필요** (from `backend/services_v9/ab_scenario_engine.py`)

**요구사항**:
```python
class ScenarioEngine:
    SCENARIOS = {
        "A": "youth",      # 청년 주택
        "B": "newlywed",   # 신혼부부 주택
        "C": "elderly"     # 고령자 주택
    }
    
    COMPARISON_METRICS = [
        "far", "buildable_area", "unit_count", "capex",
        "lh_purchase_price", "roi", "irr", "risk_score",
        "policy_fit", "market_demand", "profitability",
        "construction_period", "approval_difficulty",
        "financial_viability", "overall_score"
    ]
    
    def run_scenario(self, land_data: dict, scenario_type: str) -> dict:
        """개별 시나리오 실행"""
        pass
    
    def compare_scenarios(self, scenarios: dict) -> dict:
        """
        A/B/C 시나리오 비교
        
        Output: {
            "scenarios": {
                "A": {...15개 지표},
                "B": {...15개 지표},
                "C": {...15개 지표}
            },
            "comparison_matrix": [[...]],
            "recommended": "B",
            "reasoning": "신혼부부형이 ROI 12.5%로 최적..."
        }
        """
        pass
    
    def generate_comparison_report(self, comparison: dict) -> dict:
        """비교 보고서 생성 (HTML + 시각화)"""
        pass
```

**우선순위**: HIGH (기존 코드 활용 + 확장)

---

#### Module 12: Multi-Parcel Engine
**파일**: `app/engines/multiparcel_engine.py`  
**목적**: 합필 분석 (면적 합산, FAR 변화, 경제성 비교)  
**상태**: 신규 개발 필요

**요구사항**:
```python
class MultiParcelEngine:
    def combine_parcels(self, parcels: list) -> dict:
        """
        합필 시뮬레이션
        
        Input: [
            {"area": 1000, "zone": "residential_1"},
            {"area": 800, "zone": "residential_2"}
        ]
        
        Output: {
            "combined_area": 1800,
            "dominant_zone": "residential_1",
            "new_far": 220,
            "far_increase": 20
        }
        """
        pass
    
    def analyze_combinations(self, parcels: list) -> list:
        """
        모든 합필 조합 분석
        
        Output: [
            {"parcels": [1, 2], "unit_count": 85, "roi": 13.2},
            {"parcels": [1, 3], "unit_count": 72, "roi": 11.8},
            ...
        ]
        """
        pass
    
    def recommend_optimal_combination(self, combinations: list) -> dict:
        """최적 합필 조합 추천"""
        pass
```

**우선순위**: MEDIUM

---

#### Module 13: Alias Engine
**파일**: `app/engines/alias_engine.py`  
**목적**: 보고서용 alias 150개 생성 (금액 포맷, 단위 변환 등)  
**상태**: 신규 개발 필요

**요구사항**:
```python
class AliasEngine:
    def format_currency(self, value: float) -> str:
        """1500000000 → ₩1,500,000,000"""
        pass
    
    def format_area(self, sqm: float) -> str:
        """1650.0 → 1,650.0㎡ (499.2평)"""
        pass
    
    def format_percentage(self, value: float) -> str:
        """0.125 → 12.5%"""
        pass
    
    def format_none(self, value) -> str:
        """None → 0 or '-'"""
        pass
    
    def generate_all_aliases(self, raw_data: dict) -> dict:
        """
        150개 alias 자동 생성
        
        Output: {
            "land_price_formatted": "₩15억",
            "land_area_formatted": "1,650.0㎡ (499.2평)",
            "roi_formatted": "12.5%",
            ...
        }
        """
        pass
```

**우선순위**: LOW (보고서 생성 시점에 개발)

---

### 3.2 Visualization Modules (6개)

#### Viz 1: FAR Change Chart
**파일**: `app/visualization/far_chart.py`  
**상태**: **마이그레이션 필요** (기존 코드 활용)

#### Viz 2: Market Histogram
**파일**: `app/visualization/market_histogram.py`  
**상태**: **마이그레이션 필요** (기존 코드 활용)

#### Viz 3: Financial Waterfall
**파일**: `app/visualization/financial_waterfall.py`  
**상태**: 신규 개발 필요

#### Viz 4: Risk Heatmap
**파일**: `app/visualization/risk_heatmap.py`  
**상태**: 신규 개발 필요

#### Viz 5: Type Distribution
**파일**: `app/visualization/type_distribution.py`  
**상태**: 신규 개발 필요

#### Viz 6: Capacity Simulation Sketch
**파일**: `app/visualization/capacity_simulation.py`  
**상태**: 신규 개발 필요 (간이 매스도)

---

### 3.3 Report Modules (5종)

#### Report 1: Landowner Brief (3p)
**템플릿**: `app/report/templates/layout_brief.html`  
**생성기**: `app/report/generators/brief_generator.py`  
**상태**: 신규 개발 필요

**구조**:
- 1페이지: 핵심 요약
- 2페이지: 그래프 2개 (FAR, Market)
- 3페이지: 의사결정 추천

---

#### Report 2: LH Submission (8-12p)
**템플릿**: `app/report/templates/layout_lh.html`  
**생성기**: `app/report/generators/lh_generator.py`  
**상태**: 신규 개발 필요

**구조**:
- LH 제출 규격 준수
- 규제/세대수/용적률/사업성 중심
- 표준 양식

---

#### Report 3: Extended Professional (25-40p)
**템플릿**: `app/report/templates/layout_extended.html`  
**생성기**: `app/report/generators/extended_generator.py`  
**상태**: **마이그레이션 필요** (기존 Expert v3.2 활용)

**구조**:
- A/B/C 비교
- 감정평가 포함
- 리스크 분석
- 시장 분석

---

#### Report 4: Policy Impact (15p)
**템플릿**: `app/report/templates/layout_policy.html`  
**생성기**: `app/report/generators/policy_generator.py`  
**상태**: 신규 개발 필요

---

#### Report 5: Developer Feasibility (15-20p)
**템플릿**: `app/report/templates/layout_developer.html`  
**생성기**: `app/report/generators/developer_generator.py`  
**상태**: 신규 개발 필요

---

### 3.4 API Layer

#### v24 Server
**파일**: `app/api/v24_server.py`  
**상태**: 신규 개발 필요

**엔드포인트**:
```
POST /api/v24/diagnose-land
POST /api/v24/capacity
POST /api/v24/appraisal
POST /api/v24/scenario
POST /api/v24/report
GET  /api/v24/health
GET  /api/v24/docs
```

---

### 3.5 Dashboard UI
**파일**: `public/dashboard.html`  
**상태**: 신규 개발 필요

**기능**:
- 5가지 주요 기능 버튼
- API 연동
- 실시간 결과 표시

---

## 📅 PART 4: 마이그레이션 로드맵

### Phase 1: 기반 구축 (1-2주)
**목표**: 폴더 구조 + 기존 코드 마이그레이션

**작업**:
1. ✅ 새 폴더 구조 생성
2. ✅ 기존 v3.3.0 코드 분석
3. ✅ 엔진 3개 마이그레이션:
   - Market Engine (from market_data_processor)
   - Verified Cost Engine (from cost_estimation_engine)
   - Financial Engine (from financial_analysis_engine)
4. ✅ 시각화 2개 마이그레이션:
   - FAR Chart
   - Market Histogram

**결과물**:
- `/app/engines/` 폴더 구조
- 3개 엔진 작동
- 2개 시각화 작동

---

### Phase 2: 핵심 엔진 개발 (2-3주)
**목표**: v24 핵심 기능 구현

**작업**:
1. ✅ **Capacity Engine 개발** ★ 최우선
2. ✅ Zoning Engine 개발
3. ✅ FAR Engine 개발
4. ✅ Relaxation Engine 개발
5. ✅ Unit Type Engine 개발
6. ✅ Appraisal Engine 개발

**결과물**:
- Capacity Engine 완성
- 토지 진단 파이프라인 작동

---

### Phase 3: 시나리오 + 보고서 (2-3주)
**목표**: A/B/C 비교 + 보고서 5종

**작업**:
1. ✅ Scenario Engine 확장 (A/B → A/B/C)
2. ✅ Risk Engine 개발
3. ✅ Multi-Parcel Engine 개발
4. ✅ Report 5종 템플릿 개발
5. ✅ 시각화 4종 추가 개발

**결과물**:
- A/B/C 시나리오 비교 작동
- 보고서 5종 PDF 생성

---

### Phase 4: API + Dashboard (1-2주)
**목표**: API 통합 + UI 구현

**작업**:
1. ✅ v24_server.py 개발
2. ✅ 라우터 5개 개발
3. ✅ Dashboard UI 개발
4. ✅ 테스트 페이지 개발

**결과물**:
- API 6개 작동
- Dashboard 완성

---

### Phase 5: 테스트 + 문서화 (1주)
**목표**: QA + 문서 완성

**작업**:
1. ✅ 테스트 코드 작성
2. ✅ API 문서 생성
3. ✅ 사용자 가이드 작성
4. ✅ 배포 준비

**결과물**:
- 95% 이상 QA 통과
- 완전한 문서화
- Production Ready

---

## 🎯 PART 5: 즉시 실행 가능한 액션 아이템

### 우선순위 1 (CRITICAL) - 이번 주
- [ ] 새 폴더 구조 생성
- [ ] **Capacity Engine 개발 착수**
- [ ] Zoning Engine 개발
- [ ] FAR Engine 개발
- [ ] 기존 엔진 3개 마이그레이션

### 우선순위 2 (HIGH) - 다음 주
- [ ] Relaxation Engine 개발
- [ ] Unit Type Engine 개발
- [ ] Appraisal Engine 개발
- [ ] Scenario Engine 확장 (A/B/C)

### 우선순위 3 (MEDIUM) - 3주차
- [ ] Risk Engine 개발
- [ ] Multi-Parcel Engine 개발
- [ ] 보고서 템플릿 5종 개발
- [ ] 시각화 6종 완성

### 우선순위 4 (LOW) - 4주차
- [ ] API 서버 v24 개발
- [ ] Dashboard UI 개발
- [ ] 테스트 + 문서화
- [ ] 배포 준비

---

## 📊 PART 6: 성공 지표

### 기술 지표
- ✅ 엔진 13종 모두 작동
- ✅ 보고서 5종 PDF 생성
- ✅ API 6개 정상 작동
- ✅ QA 통과율 95% 이상
- ✅ 응답 속도 < 2초

### 비즈니스 지표
- ✅ 토지주용 보고서 생성 가능
- ✅ LH 제출 가능한 보고서 생성
- ✅ 건축물 규모 자동 검토 가능
- ✅ A/B/C 시나리오 비교 가능
- ✅ 합필 분석 가능

---

## 🎉 최종 목표

**"ZeroSite v24.0.0: LH 신축매입임대 토지진단 자동화 OS 완성"**

- 엔진 13종
- 보고서 5종
- API 6개
- Dashboard 1개
- Production Ready

**예상 완성 시점**: 2025년 1월 말 (약 6-8주)

---

**문서 버전**: v1.0  
**작성일**: 2025-12-12  
**작성자**: ZeroSite Development Team  
**다음 단계**: Phase 1 실행 (폴더 구조 + 마이그레이션)
