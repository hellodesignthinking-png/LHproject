# ZeroSite v9.0 AI Report Writer & Normalization Layer Specification

## 문서 개요
- **작성일**: 2025-12-04
- **버전**: v9.0 Part 3
- **목적**: AI 기반 보고서 자동 생성 엔진 및 데이터 정규화 레이어 완전 구현 명세
- **대상**: 개발자 직접 구현용 (코드 수준 상세 명세)

---

## Part 3: AI Report Writer Engine v9.0 + Normalization Layer

### 목차
1. [Normalization Layer v9.0 설계](#1-normalization-layer-v90-설계)
2. [AI Report Writer Engine v9.0 설계](#2-ai-report-writer-engine-v90-설계)
3. [Chapter별 AI Writer 구현](#3-chapter별-ai-writer-구현)
4. [보고서 톤 & 스타일 엔진](#4-보고서-톤--스타일-엔진)
5. [구현 파일 구조](#5-구현-파일-구조)

---

## 1. Normalization Layer v9.0 설계

### 1.1 목적 및 역할

**v8.6의 한계:**
- Data Mapper v8.6은 **사후 변환(post-processing)** 방식
- Engine 출력 → Mapper → Template 순서로 처리
- KeyError 방지용 fallback 로직이 복잡하고 유지보수 어려움

**v9.0 Normalization Layer 철학:**
- **Engine 출력 단계에서 정규화된 표준 JSON 구조 생성**
- Template이 아닌 **Engine이 표준 스키마를 준수**
- Mapper는 최소한의 formatting만 담당

### 1.2 표준 데이터 스키마 v9.0

```python
# app/models/standard_schema_v9_0.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum

class AnalysisMode(str, Enum):
    """분석 모드"""
    STANDARD = "STANDARD"  # 50세대 미만
    LH_LINKED = "LH_LINKED"  # 50세대 이상 (LH 연동)

class ProjectGrade(str, Enum):
    """프로젝트 등급"""
    S = "S"  # 90점 이상
    A = "A"  # 80-89점
    B = "B"  # 70-79점
    C = "C"  # 60-69점
    D = "D"  # 50-59점
    F = "F"  # 50점 미만

class DecisionType(str, Enum):
    """최종 결정"""
    PROCEED = "PROCEED"  # 진행 추천
    PROCEED_WITH_CONDITIONS = "PROCEED_WITH_CONDITIONS"  # 조건부 진행
    REVISE = "REVISE"  # 설계 수정 필요
    NOGO = "NOGO"  # 진행 불가

# ===== 1. Site Information =====
class SiteInfo(BaseModel):
    """토지 기본 정보 (정규화)"""
    address: str = Field(..., description="도로명 주소")
    land_area: float = Field(..., description="대지 면적 (m²)")
    zone_type: str = Field(..., description="용도지역")
    land_appraisal_price: float = Field(..., description="감정평가액 (원/m²)")
    total_land_price: float = Field(..., description="총 토지가격 (원)")
    
    # GIS 좌표
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # 법규 정보
    building_coverage_ratio: float = Field(..., description="건폐율 (%)")
    floor_area_ratio: float = Field(..., description="용적률 (%)")
    height_limit: Optional[float] = Field(None, description="높이 제한 (m)")

# ===== 2. GIS & Accessibility =====
class POIDistance(BaseModel):
    """POI 거리 정보 (정규화)"""
    category: str = Field(..., description="POI 카테고리 (예: elementary_school)")
    name: str = Field(..., description="시설명")
    distance_m: float = Field(..., description="직선 거리 (m)")
    distance_display: str = Field(..., description="표시용 거리 (예: 1.2km)")
    walk_time_min: Optional[int] = Field(None, description="도보 시간 (분)")
    drive_time_min: Optional[int] = Field(None, description="차량 시간 (분)")
    accessibility_score: float = Field(..., description="접근성 점수 (0-10)")
    interpretation: str = Field(..., description="해석 (예: 우수)")

class GISResult(BaseModel):
    """GIS 분석 결과 (정규화)"""
    elementary_schools: List[POIDistance] = []
    middle_schools: List[POIDistance] = []
    subway_stations: List[POIDistance] = []
    bus_stops: List[POIDistance] = []
    hospitals: List[POIDistance] = []
    supermarkets: List[POIDistance] = []
    parks: List[POIDistance] = []
    
    # 종합 접근성 점수
    overall_accessibility_score: float = Field(..., description="종합 접근성 점수 (0-100)")
    accessibility_grade: str = Field(..., description="등급 (S/A/B/C/D)")

# ===== 3. Financial Analysis =====
class FinancialResult(BaseModel):
    """재무 분석 결과 (v9.0 완전 정규화)"""
    
    # 기본 투자 정보
    total_land_price: float = Field(..., description="총 토지가격")
    construction_cost_per_sqm: float = Field(..., description="단위 공사비 (원/m²)")
    total_construction_cost: float = Field(..., description="총 공사비")
    total_capex: float = Field(..., description="총 투자액 (CAPEX)")
    
    # LH 연동 (50세대 이상인 경우)
    analysis_mode: AnalysisMode
    lh_purchase_price: Optional[float] = Field(None, description="LH 매입가 (원)")
    lh_purchase_price_per_sqm: Optional[float] = Field(None, description="LH 매입가 (원/m²)")
    verified_cost: Optional[float] = Field(None, description="검증된 공사비 (LH 기준)")
    
    # 수익성 지표
    annual_noi: float = Field(..., description="연간 순운영수익 (NOI)")
    cap_rate: float = Field(..., description="Cap Rate (%)")
    roi_10yr: float = Field(..., description="10년 ROI (%)")
    irr_10yr: float = Field(..., description="10년 IRR (%)")
    
    # 세대 정보
    unit_count: int = Field(..., description="총 세대수")
    unit_type_distribution: Dict[str, int] = Field(default_factory=dict, description="유형별 세대수")
    
    # 평가
    financial_grade: str = Field(..., description="재무 등급 (S/A/B/C/D)")
    breakeven_year: Optional[int] = Field(None, description="손익분기년도")

# ===== 4. LH Evaluation =====
class LHScores(BaseModel):
    """LH 평가 점수 (110점 만점)"""
    location_score: float = Field(..., description="입지 점수 (35점)")
    scale_score: float = Field(..., description="규모 점수 (20점)")
    business_score: float = Field(..., description="사업성 점수 (40점)")
    regulation_score: float = Field(..., description="법규 점수 (15점)")
    total_score: float = Field(..., description="총점 (110점)")
    grade: ProjectGrade = Field(..., description="프로젝트 등급")

class RiskItem(BaseModel):
    """리스크 항목"""
    id: str
    category: str  # LEGAL / FINANCIAL / TECHNICAL / MARKET
    name: str
    severity: str  # HIGH / MEDIUM / LOW
    status: str  # PASS / WARNING / FAIL
    description: str
    mitigation: Optional[str] = None

class RiskAssessment(BaseModel):
    """리스크 평가 결과"""
    total_items: int = 25
    pass_count: int
    warning_count: int
    fail_count: int
    critical_risks: List[RiskItem] = []
    all_risks: List[RiskItem] = []
    overall_risk_level: str  # LOW / MEDIUM / HIGH / CRITICAL

# ===== 5. Demand Analysis =====
class DemandResult(BaseModel):
    """수요 분석 결과"""
    population_total: int = Field(..., description="총 인구수")
    household_count: int = Field(..., description="가구수")
    target_households: int = Field(..., description="타겟 가구수")
    demand_score: float = Field(..., description="수요 점수 (0-100)")
    demand_grade: str = Field(..., description="수요 등급")
    recommended_unit_type: str = Field(..., description="추천 주택 유형")

# ===== 6. Final Recommendation =====
class FinalRecommendation(BaseModel):
    """최종 의사결정"""
    decision: DecisionType
    confidence_level: float = Field(..., description="신뢰도 (0-100%)")
    key_strengths: List[str] = Field(default_factory=list, description="주요 강점")
    key_weaknesses: List[str] = Field(default_factory=list, description="주요 약점")
    action_items: List[str] = Field(default_factory=list, description="실행 항목")
    executive_summary: str = Field(..., description="임원 요약 (2-3문장)")

# ===== 통합 표준 출력 스키마 =====
class StandardAnalysisOutput(BaseModel):
    """표준 분석 출력 (v9.0)"""
    
    # 메타데이터
    analysis_id: str
    version: str = "v9.0"
    timestamp: str
    
    # 핵심 데이터
    site_info: SiteInfo
    gis_result: GISResult
    financial_result: FinancialResult
    lh_scores: LHScores
    risk_assessment: RiskAssessment
    demand_result: DemandResult
    final_recommendation: FinalRecommendation
    
    # 시각화 데이터 (JSON)
    visualizations: Dict[str, any] = Field(default_factory=dict)
```

### 1.3 Normalization Layer 구현

```python
# app/services/normalization_layer_v9_0.py

from typing import Dict, Any
from app.models.standard_schema_v9_0 import (
    StandardAnalysisOutput,
    SiteInfo,
    GISResult,
    POIDistance,
    FinancialResult,
    LHScores,
    RiskAssessment,
    DemandResult,
    FinalRecommendation,
    AnalysisMode,
    DecisionType
)
import logging

logger = logging.getLogger(__name__)

class NormalizationLayerV90:
    """
    v9.0 정규화 레이어
    - 각 Engine의 원시 출력을 표준 스키마로 변환
    - KeyError 방지 및 기본값 처리
    """
    
    def normalize_gis_output(self, gis_raw: Dict[str, Any]) -> GISResult:
        """GIS Engine 출력 정규화"""
        try:
            pois = []
            for category in ["elementary_schools", "middle_schools", "subway_stations", 
                            "bus_stops", "hospitals", "supermarkets", "parks"]:
                items = gis_raw.get(category, [])
                for item in items:
                    poi = POIDistance(
                        category=category,
                        name=item.get("name", "Unknown"),
                        distance_m=item.get("distance_m", 9999.0),
                        distance_display=self._format_distance(item.get("distance_m", 9999.0)),
                        walk_time_min=item.get("walk_time_min"),
                        drive_time_min=item.get("drive_time_min"),
                        accessibility_score=item.get("accessibility_score", 0.0),
                        interpretation=self._interpret_accessibility(item.get("accessibility_score", 0.0))
                    )
                    pois.append(poi)
            
            return GISResult(
                elementary_schools=[p for p in pois if p.category == "elementary_schools"],
                middle_schools=[p for p in pois if p.category == "middle_schools"],
                subway_stations=[p for p in pois if p.category == "subway_stations"],
                bus_stops=[p for p in pois if p.category == "bus_stops"],
                hospitals=[p for p in pois if p.category == "hospitals"],
                supermarkets=[p for p in pois if p.category == "supermarkets"],
                parks=[p for p in pois if p.category == "parks"],
                overall_accessibility_score=gis_raw.get("overall_score", 0.0),
                accessibility_grade=self._score_to_grade(gis_raw.get("overall_score", 0.0))
            )
        except Exception as e:
            logger.error(f"GIS normalization error: {e}")
            return self._get_default_gis_result()
    
    def normalize_financial_output(self, financial_raw: Dict[str, Any], 
                                   unit_count: int) -> FinancialResult:
        """Financial Engine 출력 정규화"""
        try:
            # 분석 모드 결정
            mode = AnalysisMode.LH_LINKED if unit_count >= 50 else AnalysisMode.STANDARD
            
            return FinancialResult(
                total_land_price=financial_raw.get("total_land_price", 0.0),
                construction_cost_per_sqm=financial_raw.get("construction_cost_per_sqm", 0.0),
                total_construction_cost=financial_raw.get("total_construction_cost", 0.0),
                total_capex=financial_raw.get("total_capex", 0.0),
                analysis_mode=mode,
                lh_purchase_price=financial_raw.get("lh_purchase_price") if mode == AnalysisMode.LH_LINKED else None,
                lh_purchase_price_per_sqm=financial_raw.get("lh_purchase_price_per_sqm") if mode == AnalysisMode.LH_LINKED else None,
                verified_cost=financial_raw.get("verified_cost") if mode == AnalysisMode.LH_LINKED else None,
                annual_noi=financial_raw.get("annual_noi", 0.0),
                cap_rate=financial_raw.get("cap_rate", 0.0),
                roi_10yr=financial_raw.get("roi_10yr", 0.0),
                irr_10yr=financial_raw.get("irr_10yr", 0.0),
                unit_count=unit_count,
                unit_type_distribution=financial_raw.get("unit_type_distribution", {}),
                financial_grade=self._score_to_grade(financial_raw.get("business_score", 0.0)),
                breakeven_year=financial_raw.get("breakeven_year")
            )
        except Exception as e:
            logger.error(f"Financial normalization error: {e}")
            return self._get_default_financial_result()
    
    def normalize_lh_scores(self, lh_raw: Dict[str, Any]) -> LHScores:
        """LH Evaluation Engine 출력 정규화"""
        try:
            total = lh_raw.get("total_score", 0.0)
            return LHScores(
                location_score=lh_raw.get("location_score", 0.0),
                scale_score=lh_raw.get("scale_score", 0.0),
                business_score=lh_raw.get("business_score", 0.0),
                regulation_score=lh_raw.get("regulation_score", 0.0),
                total_score=total,
                grade=self._total_score_to_grade(total)
            )
        except Exception as e:
            logger.error(f"LH scores normalization error: {e}")
            return LHScores(
                location_score=0.0,
                scale_score=0.0,
                business_score=0.0,
                regulation_score=0.0,
                total_score=0.0,
                grade="F"
            )
    
    def normalize_risk_assessment(self, risk_raw: Dict[str, Any]) -> RiskAssessment:
        """Risk Engine 출력 정규화"""
        try:
            all_risks = risk_raw.get("all_risks", [])
            return RiskAssessment(
                total_items=25,
                pass_count=risk_raw.get("pass_count", 0),
                warning_count=risk_raw.get("warning_count", 0),
                fail_count=risk_raw.get("fail_count", 0),
                critical_risks=[r for r in all_risks if r.get("severity") == "HIGH"],
                all_risks=all_risks,
                overall_risk_level=risk_raw.get("overall_risk_level", "UNKNOWN")
            )
        except Exception as e:
            logger.error(f"Risk assessment normalization error: {e}")
            return RiskAssessment(
                total_items=25,
                pass_count=0,
                warning_count=0,
                fail_count=0,
                critical_risks=[],
                all_risks=[],
                overall_risk_level="UNKNOWN"
            )
    
    # ===== Helper Methods =====
    
    def _format_distance(self, distance_m: float) -> str:
        """거리를 사람이 읽기 좋은 형식으로 변환"""
        if distance_m >= 10000:
            return "10km 이상"
        elif distance_m >= 2000:
            return f"{distance_m/1000:.1f}km"
        elif distance_m >= 1000:
            return f"{distance_m/1000:.2f}km"
        else:
            return f"{int(distance_m)}m"
    
    def _interpret_accessibility(self, score: float) -> str:
        """접근성 점수 해석"""
        if score >= 9.0:
            return "매우 우수"
        elif score >= 7.0:
            return "우수"
        elif score >= 5.0:
            return "보통"
        elif score >= 3.0:
            return "미흡"
        else:
            return "불량"
    
    def _score_to_grade(self, score: float) -> str:
        """점수를 등급으로 변환"""
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def _total_score_to_grade(self, total_score: float) -> str:
        """110점 만점 기준 등급 변환"""
        percentage = (total_score / 110.0) * 100
        return self._score_to_grade(percentage)
    
    def _get_default_gis_result(self) -> GISResult:
        """기본 GIS 결과"""
        return GISResult(
            overall_accessibility_score=0.0,
            accessibility_grade="F"
        )
    
    def _get_default_financial_result(self) -> FinancialResult:
        """기본 Financial 결과"""
        return FinancialResult(
            total_land_price=0.0,
            construction_cost_per_sqm=0.0,
            total_construction_cost=0.0,
            total_capex=0.0,
            analysis_mode=AnalysisMode.STANDARD,
            annual_noi=0.0,
            cap_rate=0.0,
            roi_10yr=0.0,
            irr_10yr=0.0,
            unit_count=0,
            financial_grade="F"
        )
```

---

## 2. AI Report Writer Engine v9.0 설계

### 2.1 AI Writer 아키텍처

```
Input: StandardAnalysisOutput (정규화된 JSON)
  ↓
Chapter-specific AI Writers (12개)
  ↓
Narrative Generation (GPT-4 / Claude / Local LLM)
  ↓
Output: 전문가 수준 보고서 텍스트
```

### 2.2 AI Writer 핵심 클래스

```python
# app/services/ai_report_writer_v9_0.py

from typing import Dict, Any, Optional
from app.models.standard_schema_v9_0 import StandardAnalysisOutput
import logging

logger = logging.getLogger(__name__)

class AIReportWriterV90:
    """
    v9.0 AI 보고서 작성 엔진
    - 정규화된 데이터를 전문가 수준 텍스트로 변환
    - 12개 챕터별 독립적인 Writer
    - GPT-4 / Claude 3.5 / Local LLM 지원
    """
    
    def __init__(self, llm_provider: str = "gpt-4", tone: str = "professional"):
        """
        Args:
            llm_provider: "gpt-4" / "claude-3.5" / "local-llm"
            tone: "professional" / "academic" / "lh-submission"
        """
        self.llm_provider = llm_provider
        self.tone = tone
        self.chapter_writers = {
            "executive_summary": ExecutiveSummaryWriter(self),
            "site_overview": SiteOverviewWriter(self),
            "gis_accessibility": GISAccessibilityWriter(self),
            "location_metrics": LocationMetricsWriter(self),
            "demand_analysis": DemandAnalysisWriter(self),
            "regulation_review": RegulationReviewWriter(self),
            "construction_feasibility": ConstructionFeasibilityWriter(self),
            "financial_analysis": FinancialAnalysisWriter(self),
            "lh_evaluation": LHEvaluationWriter(self),
            "risk_review": RiskReviewWriter(self),
            "final_decision": FinalDecisionWriter(self),
            "appendix": AppendixWriter(self)
        }
    
    def generate_full_report(self, data: StandardAnalysisOutput) -> Dict[str, str]:
        """
        전체 보고서 생성
        
        Returns:
            {
                "executive_summary": "...",
                "site_overview": "...",
                ...
            }
        """
        report = {}
        for chapter_id, writer in self.chapter_writers.items():
            try:
                logger.info(f"Generating chapter: {chapter_id}")
                report[chapter_id] = writer.write(data)
            except Exception as e:
                logger.error(f"Error generating {chapter_id}: {e}")
                report[chapter_id] = f"[오류: {chapter_id} 생성 실패]"
        
        return report
    
    def call_llm(self, prompt: str, max_tokens: int = 1000) -> str:
        """LLM API 호출 (추상화)"""
        if self.llm_provider == "gpt-4":
            return self._call_gpt4(prompt, max_tokens)
        elif self.llm_provider == "claude-3.5":
            return self._call_claude(prompt, max_tokens)
        else:
            return self._call_local_llm(prompt, max_tokens)
    
    def _call_gpt4(self, prompt: str, max_tokens: int) -> str:
        """GPT-4 API 호출"""
        # 실제 OpenAI API 호출 구현
        # from openai import OpenAI
        # client = OpenAI()
        # response = client.chat.completions.create(...)
        return "[GPT-4 응답]"
    
    def _call_claude(self, prompt: str, max_tokens: int) -> str:
        """Claude 3.5 API 호출"""
        return "[Claude 응답]"
    
    def _call_local_llm(self, prompt: str, max_tokens: int) -> str:
        """Local LLM 호출 (예: Ollama)"""
        return "[Local LLM 응답]"
```

---

## 3. Chapter별 AI Writer 구현

### 3.1 Executive Summary Writer

```python
# app/services/ai_writers/executive_summary_writer.py

class ExecutiveSummaryWriter:
    """임원 요약 작성"""
    
    def __init__(self, parent: 'AIReportWriterV90'):
        self.parent = parent
    
    def write(self, data: StandardAnalysisOutput) -> str:
        """
        임원 요약 생성 (1-2페이지)
        - 핵심 결론
        - 주요 지표 3-5개
        - 최종 의사결정
        """
        prompt = f"""
당신은 LH(한국토지주택공사) 신축매입임대 사업 전문 컨설턴트입니다.
아래 데이터를 바탕으로 **임원 요약(Executive Summary)**을 작성하세요.

## 분석 대상
- 주소: {data.site_info.address}
- 대지면적: {data.site_info.land_area}m²
- 용도지역: {data.site_info.zone_type}

## 핵심 지표
- 총 투자액: {data.financial_result.total_capex:,.0f}원
- 예상 세대수: {data.financial_result.unit_count}세대
- LH 평가 점수: {data.lh_scores.total_score:.1f}/110점 (등급: {data.lh_scores.grade})
- 재무 지표: Cap Rate {data.financial_result.cap_rate:.2f}%, ROI {data.financial_result.roi_10yr:.2f}%
- 최종 결정: {data.final_recommendation.decision.value}

## 요구사항
1. 2-3문단 (A4 1페이지 이내)
2. 의사결정자가 5분 내 핵심 파악 가능하도록 구조화
3. 숫자는 명확히 제시 (예: ₩138억 투자, 33세대 건설)
4. 톤: {self.parent.tone}
5. 결론부터 시작 (Bottom Line Up Front)

작성:
"""
        return self.parent.call_llm(prompt, max_tokens=800)
```

### 3.2 GIS Accessibility Writer

```python
# app/services/ai_writers/gis_accessibility_writer.py

class GISAccessibilityWriter:
    """GIS 접근성 분석 작성"""
    
    def __init__(self, parent: 'AIReportWriterV90'):
        self.parent = parent
    
    def write(self, data: StandardAnalysisOutput) -> str:
        """
        GIS 접근성 분석 챕터 (3-4페이지)
        - 교육시설 (초/중/고)
        - 교통시설 (지하철/버스)
        - 생활편의시설 (병원/마트/공원)
        - 종합 접근성 평가
        """
        gis = data.gis_result
        
        # 초등학교 정보 포맷팅
        elementary_info = "\n".join([
            f"  - {poi.name}: {poi.distance_display} ({poi.interpretation})"
            for poi in gis.elementary_schools[:3]
        ])
        
        # 지하철역 정보
        subway_info = "\n".join([
            f"  - {poi.name}: {poi.distance_display} (도보 {poi.walk_time_min}분)"
            for poi in gis.subway_stations[:3]
        ])
        
        prompt = f"""
당신은 도시계획 및 GIS 분석 전문가입니다.
아래 데이터를 바탕으로 **GIS 접근성 분석** 챕터를 작성하세요.

## 교육시설 접근성
{elementary_info}

## 교통시설 접근성
{subway_info}

## 종합 접근성
- 종합 점수: {gis.overall_accessibility_score:.1f}/100점
- 등급: {gis.accessibility_grade}

## 요구사항
1. 챕터 구조:
   - 3.1 교육시설 분석
   - 3.2 교통 접근성
   - 3.3 생활편의시설
   - 3.4 종합 평가
2. 각 POI별로 "거리 + 해석 + 입주민 관점 영향" 분석
3. 정량적 데이터 + 정성적 해석 병행
4. A4 3-4페이지 분량

작성:
"""
        return self.parent.call_llm(prompt, max_tokens=2000)
```

### 3.3 Financial Analysis Writer

```python
# app/services/ai_writers/financial_analysis_writer.py

class FinancialAnalysisWriter:
    """재무 분석 작성 (핵심 챕터)"""
    
    def __init__(self, parent: 'AIReportWriterV90'):
        self.parent = parent
    
    def write(self, data: StandardAnalysisOutput) -> str:
        """
        재무 분석 챕터 (6-8페이지)
        - CAPEX 구조
        - 공사비 연동제 적용 (50세대 이상)
        - LH 매입가 시뮬레이션
        - 수익성 지표 (Cap Rate, ROI, IRR)
        - 민감도 분석
        """
        fin = data.financial_result
        
        # LH 연동 여부
        lh_linked = fin.analysis_mode == "LH_LINKED"
        
        prompt = f"""
당신은 부동산 재무 분석 전문가 (CFA, CPM 보유)입니다.
아래 데이터를 바탕으로 **재무 분석(Financial Analysis)** 챕터를 작성하세요.

## 투자 구조
- 총 투자액(CAPEX): {fin.total_capex:,.0f}원
  - 토지비: {fin.total_land_price:,.0f}원
  - 공사비: {fin.total_construction_cost:,.0f}원 (단가: {fin.construction_cost_per_sqm:,.0f}원/m²)
- 세대수: {fin.unit_count}세대
- 분석 모드: {"LH 연동 (50세대 이상)" if lh_linked else "일반 분석"}

{"## LH 매입가 구조" if lh_linked else ""}
{"- LH 매입가: " + f"{fin.lh_purchase_price:,.0f}원 ({fin.lh_purchase_price_per_sqm:,.0f}원/m²)" if lh_linked else ""}
{"- 검증된 공사비: " + f"{fin.verified_cost:,.0f}원" if lh_linked else ""}

## 수익성 지표
- 연간 NOI: {fin.annual_noi:,.0f}원
- Cap Rate: {fin.cap_rate:.2f}%
- 10년 ROI: {fin.roi_10yr:.2f}%
- 10년 IRR: {fin.irr_10yr:.2f}%
- 손익분기년도: {fin.breakeven_year}년 (예상)

## 요구사항
1. 챕터 구조:
   - 8.1 투자 구조 (CAPEX Breakdown)
   - 8.2 {"LH 공사비 연동제 분석" if lh_linked else "공사비 산정"}
   - 8.3 수익성 분석 (Cap Rate, ROI, IRR)
   - 8.4 민감도 분석 (공사비 ±10%, 임대료 ±5%)
   - 8.5 재무 종합 평가
2. LH 기준 (50세대 이상)인 경우, "검증된 공사비 + 토지비 = LH 매입가" 구조 명확히 설명
3. IRR 계산 로직 투명하게 제시 (10년 현금흐름 기반)
4. 전문적이면서도 의사결정자가 이해하기 쉬운 언어 사용
5. A4 6-8페이지 분량

작성:
"""
        return self.parent.call_llm(prompt, max_tokens=3000)
```

### 3.4 LH Evaluation Writer

```python
# app/services/ai_writers/lh_evaluation_writer.py

class LHEvaluationWriter:
    """LH 평가 기준 작성"""
    
    def __init__(self, parent: 'AIReportWriterV90'):
        self.parent = parent
    
    def write(self, data: StandardAnalysisOutput) -> str:
        """
        LH 평가 챕터 (4-5페이지)
        - 110점 만점 체계
        - 4대 카테고리별 분석
        - 심사 체크리스트
        """
        lh = data.lh_scores
        
        prompt = f"""
당신은 LH(한국토지주택공사) 심사위원입니다.
아래 데이터를 바탕으로 **LH 평가 기준 분석** 챕터를 작성하세요.

## LH 110점 만점 평가
1. 입지 점수: {lh.location_score:.1f}/35점
2. 규모 점수: {lh.scale_score:.1f}/20점
3. 사업성 점수: {lh.business_score:.1f}/40점
4. 법규 점수: {lh.regulation_score:.1f}/15점

**총점: {lh.total_score:.1f}/110점 (등급: {lh.grade})**

## 요구사항
1. 챕터 구조:
   - 9.1 LH 평가 기준 개요
   - 9.2 입지 평가 (35점)
   - 9.3 규모 평가 (20점)
   - 9.4 사업성 평가 (40점)
   - 9.5 법규 평가 (15점)
   - 9.6 종합 평가 및 등급
2. 각 카테고리별로 "만점 조건", "현재 점수", "개선 방안" 제시
3. 등급별 의미:
   - S등급(90점 이상): 최우선 추진
   - A등급(80-89점): 적극 추진
   - B등급(70-79점): 조건부 추진
   - C등급(60-69점): 설계 보완 필요
   - D등급(50-59점): 재검토 필요
   - F등급(50점 미만): 추진 불가
4. A4 4-5페이지 분량

작성:
"""
        return self.parent.call_llm(prompt, max_tokens=2500)
```

### 3.5 Risk Review Writer

```python
# app/services/ai_writers/risk_review_writer.py

class RiskReviewWriter:
    """리스크 평가 작성"""
    
    def __init__(self, parent: 'AIReportWriterV90'):
        self.parent = parent
    
    def write(self, data: StandardAnalysisOutput) -> str:
        """
        리스크 평가 챕터 (4-5페이지)
        - 25개 리스크 항목 체크
        - 카테고리별 분석 (법률/재무/기술/시장)
        - 위험 완화 방안
        """
        risk = data.risk_assessment
        
        # Critical Risks 포맷팅
        critical_risks_text = "\n".join([
            f"  - [{r.get('severity')}] {r.get('name')}: {r.get('description')}"
            for r in risk.critical_risks[:5]
        ])
        
        prompt = f"""
당신은 리스크 관리 전문가(CRM, PRM 보유)입니다.
아래 데이터를 바탕으로 **리스크 평가(Risk Assessment)** 챕터를 작성하세요.

## 리스크 체크 현황
- 전체 항목: {risk.total_items}개
- PASS: {risk.pass_count}개
- WARNING: {risk.warning_count}개
- FAIL: {risk.fail_count}개
- **전체 위험도: {risk.overall_risk_level}**

## 주요(Critical) 리스크
{critical_risks_text}

## 요구사항
1. 챕터 구조:
   - 10.1 리스크 평가 프레임워크
   - 10.2 법률 리스크 (LEGAL)
   - 10.3 재무 리스크 (FINANCIAL)
   - 10.4 기술 리스크 (TECHNICAL)
   - 10.5 시장 리스크 (MARKET)
   - 10.6 종합 리스크 평가 및 완화 전략
2. 각 리스크별로:
   - 위험도 (HIGH/MEDIUM/LOW)
   - 발생 가능성 및 영향도
   - 완화 방안 (Mitigation Strategy)
3. FAIL 항목은 특히 상세히 분석
4. A4 4-5페이지 분량

작성:
"""
        return self.parent.call_llm(prompt, max_tokens=2500)
```

### 3.6 Final Decision Writer

```python
# app/services/ai_writers/final_decision_writer.py

class FinalDecisionWriter:
    """최종 의사결정 작성"""
    
    def __init__(self, parent: 'AIReportWriterV90'):
        self.parent = parent
    
    def write(self, data: StandardAnalysisOutput) -> str:
        """
        최종 의사결정 챕터 (2-3페이지)
        - PROCEED / REVISE / NO-GO 결정
        - 근거 및 신뢰도
        - Action Items
        """
        rec = data.final_recommendation
        
        prompt = f"""
당신은 LH 신축매입임대 사업 최종 의사결정권자(C-Level Executive)입니다.
아래 데이터를 바탕으로 **최종 의사결정(Final Recommendation)** 챕터를 작성하세요.

## 최종 결정
**{rec.decision.value}** (신뢰도: {rec.confidence_level:.1f}%)

## 주요 강점
{chr(10).join([f"  - {s}" for s in rec.key_strengths])}

## 주요 약점
{chr(10).join([f"  - {w}" for w in rec.key_weaknesses])}

## 실행 항목 (Action Items)
{chr(10).join([f"  {i+1}. {a}" for i, a in enumerate(rec.action_items)])}

## 요구사항
1. 챕터 구조:
   - 11.1 의사결정 프레임워크
   - 11.2 정량적 평가 요약
   - 11.3 정성적 판단
   - 11.4 최종 권고사항
   - 11.5 Next Steps (실행 계획)
2. 결정별 의미:
   - PROCEED: 즉시 추진 권고
   - PROCEED_WITH_CONDITIONS: 조건 충족 시 추진
   - REVISE: 설계 수정 후 재검토
   - NOGO: 추진 불가 권고
3. 신뢰도가 80% 미만인 경우, 추가 조사 필요 항목 명시
4. A4 2-3페이지 분량

작성:
"""
        return self.parent.call_llm(prompt, max_tokens=1500)
```

---

## 4. 보고서 톤 & 스타일 엔진

### 4.1 Tone Selector

```python
# app/services/tone_selector_v9_0.py

class ToneSelectorV90:
    """보고서 톤 및 스타일 관리"""
    
    TONES = {
        "professional": {
            "description": "전문적이고 객관적인 컨설팅 보고서",
            "language": "formal",
            "target_audience": "C-Level Executives, 투자자",
            "example_phrases": [
                "분석 결과에 따르면",
                "정량적 지표는 다음과 같이 나타났습니다",
                "종합적으로 판단컨대"
            ]
        },
        "academic": {
            "description": "학술적이고 연구 중심적인 보고서",
            "language": "highly_formal",
            "target_audience": "연구자, 학계",
            "example_phrases": [
                "본 연구에서는",
                "선행연구에 따르면",
                "통계적으로 유의미한"
            ]
        },
        "lh_submission": {
            "description": "LH 제출용 정부 문서 스타일",
            "language": "government_formal",
            "target_audience": "LH 심사위원, 공공기관",
            "example_phrases": [
                "LH 기준에 따라",
                "신축매입임대 사업 심사 기준",
                "검증된 공사비 기준"
            ]
        }
    }
    
    def get_tone_instructions(self, tone: str) -> str:
        """톤에 맞는 LLM 프롬프트 지침 생성"""
        if tone not in self.TONES:
            tone = "professional"
        
        tone_config = self.TONES[tone]
        
        instructions = f"""
## 보고서 작성 톤 가이드
- 스타일: {tone_config['description']}
- 언어 수준: {tone_config['language']}
- 대상: {tone_config['target_audience']}

예시 표현:
{chr(10).join([f"  - {p}" for p in tone_config['example_phrases']])}

준수사항:
- 객관적 데이터 기반 서술
- 명확한 근거 제시
- 전문 용어 사용 (단, 필요시 괄호로 설명)
- 단정적 표현 자제 (단, 최종 결론은 명확히)
"""
        return instructions
```

---

## 5. 구현 파일 구조

```
app/
├── services/
│   ├── normalization_layer_v9_0.py        # 정규화 레이어
│   ├── ai_report_writer_v9_0.py           # AI Writer 메인
│   ├── tone_selector_v9_0.py              # 톤 관리
│   └── ai_writers/                        # 챕터별 Writer
│       ├── __init__.py
│       ├── executive_summary_writer.py
│       ├── site_overview_writer.py
│       ├── gis_accessibility_writer.py
│       ├── location_metrics_writer.py
│       ├── demand_analysis_writer.py
│       ├── regulation_review_writer.py
│       ├── construction_feasibility_writer.py
│       ├── financial_analysis_writer.py
│       ├── lh_evaluation_writer.py
│       ├── risk_review_writer.py
│       ├── final_decision_writer.py
│       └── appendix_writer.py
│
├── models/
│   └── standard_schema_v9_0.py            # 표준 데이터 스키마
│
└── tests/
    └── test_ai_report_writer_v9_0.py      # AI Writer 테스트
```

---

## 6. 테스트 코드

```python
# app/tests/test_ai_report_writer_v9_0.py

import pytest
from app.services.ai_report_writer_v9_0 import AIReportWriterV90
from app.models.standard_schema_v9_0 import StandardAnalysisOutput, SiteInfo, FinancialResult

def test_executive_summary_generation():
    """Executive Summary 생성 테스트"""
    
    # Mock 데이터
    data = StandardAnalysisOutput(
        analysis_id="TEST001",
        version="v9.0",
        timestamp="2025-12-04T10:00:00",
        site_info=SiteInfo(
            address="서울시 마포구 월드컵북로 120",
            land_area=660.0,
            zone_type="제3종일반주거지역",
            land_appraisal_price=5000000,
            total_land_price=3300000000,
            building_coverage_ratio=50.0,
            floor_area_ratio=250.0
        ),
        financial_result=FinancialResult(
            total_land_price=3300000000,
            construction_cost_per_sqm=2500000,
            total_construction_cost=10000000000,
            total_capex=13894947381,
            analysis_mode="STANDARD",
            annual_noi=500000000,
            cap_rate=3.6,
            roi_10yr=-16.55,
            irr_10yr=-2.1,
            unit_count=33,
            financial_grade="D"
        ),
        # ... 나머지 필드 생략
    )
    
    writer = AIReportWriterV90(llm_provider="gpt-4", tone="professional")
    summary = writer.chapter_writers["executive_summary"].write(data)
    
    assert len(summary) > 500  # 최소 500자 이상
    assert "월드컵북로 120" in summary
    assert "33세대" in summary
    assert "138억" in summary or "13,894,947,381" in summary

def test_financial_analysis_lh_linked():
    """LH 연동 재무 분석 테스트"""
    
    data = StandardAnalysisOutput(
        # ... (50세대 이상 데이터)
        financial_result=FinancialResult(
            analysis_mode="LH_LINKED",
            unit_count=60,
            lh_purchase_price=20000000000,
            verified_cost=15000000000,
            # ...
        )
    )
    
    writer = AIReportWriterV90(llm_provider="gpt-4")
    financial_chapter = writer.chapter_writers["financial_analysis"].write(data)
    
    assert "LH 연동" in financial_chapter or "50세대 이상" in financial_chapter
    assert "검증된 공사비" in financial_chapter
    assert "공사비 연동제" in financial_chapter
```

---

## 7. 핵심 개선 사항 요약

| 항목 | v8.6 | v9.0 |
|------|------|------|
| 데이터 정규화 | Data Mapper (사후 처리) | Normalization Layer (Engine 단계) |
| 보고서 생성 | 템플릿 기반 (정적) | AI Writer (동적 텍스트 생성) |
| KeyError 처리 | Mapper의 fallback | 표준 스키마 준수 (Engine 레벨) |
| 톤 & 스타일 | 고정 | 3가지 톤 선택 가능 |
| 챕터 모듈화 | 단일 클래스 | 12개 독립 Writer |
| LLM 지원 | 없음 | GPT-4 / Claude / Local LLM |

---

## 다음 단계: Part 4 (PDF Renderer v9.0)

Part 3에서는 **AI 기반 보고서 텍스트 생성**을 완성했습니다.
Part 4에서는 이 텍스트를 **12-section 모듈형 PDF/HTML로 렌더링**하는 시스템을 설계합니다.

---

**문서 종료**
