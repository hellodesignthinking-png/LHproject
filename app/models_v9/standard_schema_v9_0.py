"""
ZeroSite v9.0 Standard Data Schema
표준 분석 출력 스키마 - 모든 Engine이 이 구조를 준수
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


# ===== Enums =====

class AnalysisMode(str, Enum):
    """분석 모드"""
    STANDARD = "STANDARD"  # 50세대 미만
    LH_LINKED = "LH_LINKED"  # 50세대 이상 (LH 연동)


class ProjectGrade(str, Enum):
    """프로젝트 등급 (110점 기준)"""
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


class RiskSeverity(str, Enum):
    """리스크 심각도"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RiskStatus(str, Enum):
    """리스크 상태"""
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


class RiskCategory(str, Enum):
    """리스크 카테고리"""
    LEGAL = "LEGAL"  # 법률
    FINANCIAL = "FINANCIAL"  # 재무
    TECHNICAL = "TECHNICAL"  # 기술
    MARKET = "MARKET"  # 시장


# ===== Site Information =====

class SiteInfo(BaseModel):
    """토지 기본 정보 (정규화)"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    address: str = Field(..., description="도로명 주소")
    land_area: float = Field(..., description="대지 면적 (m²)", gt=0)
    zone_type: str = Field(..., description="용도지역")
    land_appraisal_price: float = Field(..., description="감정평가액 (원/m²)", gt=0)
    total_land_price: float = Field(..., description="총 토지가격 (원)", gt=0)
    
    # GIS 좌표
    latitude: Optional[float] = Field(None, description="위도")
    longitude: Optional[float] = Field(None, description="경도")
    
    # 법규 정보
    building_coverage_ratio: float = Field(..., description="건폐율 (%)", ge=0, le=100)
    floor_area_ratio: float = Field(..., description="용적률 (%)", ge=0, le=1000)
    height_limit: Optional[float] = Field(None, description="높이 제한 (m)")


# ===== GIS & Accessibility =====

class POIDistance(BaseModel):
    """POI 거리 정보 (정규화)"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    category: str = Field(..., description="POI 카테고리 (예: elementary_school)")
    name: str = Field(..., description="시설명")
    distance_m: float = Field(..., description="직선 거리 (m)", ge=0)
    distance_display: str = Field(..., description="표시용 거리 (예: 1.2km)")
    walk_time_min: Optional[int] = Field(None, description="도보 시간 (분)", ge=0)
    drive_time_min: Optional[int] = Field(None, description="차량 시간 (분)", ge=0)
    accessibility_score: float = Field(..., description="접근성 점수 (0-10)", ge=0, le=10)
    interpretation: str = Field(..., description="해석 (예: 우수)")


class GISResult(BaseModel):
    """GIS 분석 결과 (정규화)"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    elementary_schools: List[POIDistance] = Field(default_factory=list)
    middle_schools: List[POIDistance] = Field(default_factory=list)
    high_schools: List[POIDistance] = Field(default_factory=list)
    subway_stations: List[POIDistance] = Field(default_factory=list)
    bus_stops: List[POIDistance] = Field(default_factory=list)
    hospitals: List[POIDistance] = Field(default_factory=list)
    supermarkets: List[POIDistance] = Field(default_factory=list)
    parks: List[POIDistance] = Field(default_factory=list)
    
    # 종합 접근성 점수
    overall_accessibility_score: float = Field(..., description="종합 접근성 점수 (0-100)", ge=0, le=100)
    accessibility_grade: str = Field(..., description="등급 (S/A/B/C/D/F)")


# ===== Financial Analysis =====

class FinancialResult(BaseModel):
    """재무 분석 결과 (v9.0 완전 정규화)"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # 기본 투자 정보
    total_land_price: float = Field(..., description="총 토지가격 (원)", ge=0)
    construction_cost_per_sqm: float = Field(..., description="단위 공사비 (원/m²)", ge=0)
    total_construction_cost: float = Field(..., description="총 공사비 (원)", ge=0)
    total_capex: float = Field(..., description="총 투자액 (CAPEX, 원)", ge=0)
    
    # LH 연동 (50세대 이상인 경우)
    analysis_mode: AnalysisMode = Field(..., description="분석 모드")
    lh_purchase_price: Optional[float] = Field(None, description="LH 매입가 (원)", ge=0)
    lh_purchase_price_per_sqm: Optional[float] = Field(None, description="LH 매입가 (원/m²)", ge=0)
    verified_cost: Optional[float] = Field(None, description="검증된 공사비 (LH 기준, 원)", ge=0)
    
    # 수익성 지표
    annual_noi: float = Field(..., description="연간 순운영수익 (NOI, 원)")
    cap_rate: float = Field(..., description="Cap Rate (%)")
    roi_10yr: float = Field(..., description="10년 ROI (%)")
    irr_10yr: float = Field(..., description="10년 IRR (%)")
    
    # 세대 정보
    unit_count: int = Field(..., description="총 세대수", ge=0)
    unit_type_distribution: Dict[str, int] = Field(default_factory=dict, description="유형별 세대수")
    
    # 평가
    overall_grade: str = Field(..., description="재무 종합 등급 (S/A/B/C/D/F)")
    breakeven_year: Optional[int] = Field(None, description="손익분기년도", ge=0)


# ===== LH Evaluation =====

class LHScores(BaseModel):
    """LH 평가 점수 (110점 만점)"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    location_score: float = Field(..., description="입지 점수 (35점 만점)", ge=0, le=35)
    scale_score: float = Field(..., description="규모 점수 (20점 만점)", ge=0, le=20)
    business_score: float = Field(..., description="사업성 점수 (40점 만점)", ge=0, le=40)
    regulation_score: float = Field(..., description="법규 점수 (15점 만점)", ge=0, le=15)
    total_score: float = Field(..., description="총점 (110점 만점)", ge=0, le=110)
    grade: ProjectGrade = Field(..., description="프로젝트 등급")


class RiskItem(BaseModel):
    """리스크 항목"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str = Field(..., description="리스크 ID (예: FIN-003)")
    category: RiskCategory = Field(..., description="카테고리")
    name: str = Field(..., description="리스크 명")
    severity: RiskSeverity = Field(..., description="심각도")
    status: RiskStatus = Field(..., description="상태")
    description: str = Field(..., description="설명")
    mitigation: Optional[str] = Field(None, description="완화 방안")


class RiskAssessment(BaseModel):
    """리스크 평가 결과"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    total_items: int = Field(25, description="전체 리스크 항목 수")
    pass_count: int = Field(..., description="통과 항목 수", ge=0, le=25)
    warning_count: int = Field(..., description="경고 항목 수", ge=0, le=25)
    fail_count: int = Field(..., description="실패 항목 수", ge=0, le=25)
    critical_risks: List[RiskItem] = Field(default_factory=list, description="중요 리스크 목록")
    all_risks: List[RiskItem] = Field(default_factory=list, description="전체 리스크 목록")
    overall_risk_level: str = Field(..., description="전체 위험도 (LOW/MEDIUM/HIGH/CRITICAL)")


# ===== Demand Analysis =====

class DemandResult(BaseModel):
    """수요 분석 결과"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    population_total: int = Field(..., description="총 인구수", ge=0)
    household_count: int = Field(..., description="가구수", ge=0)
    target_households: int = Field(..., description="타겟 가구수", ge=0)
    demand_score: float = Field(..., description="수요 점수 (0-100)", ge=0, le=100)
    demand_grade: str = Field(..., description="수요 등급")
    recommended_unit_type: str = Field(..., description="추천 주택 유형")


# ===== Final Recommendation =====

class FinalRecommendation(BaseModel):
    """최종 의사결정"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    decision: DecisionType = Field(..., description="최종 결정")
    confidence_level: float = Field(..., description="신뢰도 (0-100%)", ge=0, le=100)
    key_strengths: List[str] = Field(default_factory=list, description="주요 강점")
    key_weaknesses: List[str] = Field(default_factory=list, description="주요 약점")
    action_items: List[str] = Field(default_factory=list, description="실행 항목")
    executive_summary: str = Field(..., description="임원 요약 (2-3문장)")


# ===== Main Output Schema =====

class StandardAnalysisOutput(BaseModel):
    """
    표준 분석 출력 (v9.0)
    모든 Engine의 출력은 이 스키마를 따름
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "analysis_id": "anlz_abc123def456",
                "version": "v9.0",
                "timestamp": "2025-12-04T16:30:00Z",
                "site_info": {
                    "address": "서울시 마포구 월드컵북로 120",
                    "land_area": 660.0,
                    "zone_type": "제3종일반주거지역",
                    "land_appraisal_price": 5000000,
                    "total_land_price": 3300000000,
                    "building_coverage_ratio": 50.0,
                    "floor_area_ratio": 250.0
                }
            }
        }
    )
    
    # 메타데이터
    analysis_id: str = Field(..., description="분석 ID (UUID)")
    version: str = Field(default="v9.0", description="버전")
    timestamp: str = Field(..., description="생성 시간 (ISO 8601)")
    
    # 핵심 데이터
    site_info: SiteInfo
    gis_result: GISResult
    financial_result: FinancialResult
    lh_scores: LHScores
    risk_assessment: RiskAssessment
    demand_result: DemandResult
    final_recommendation: FinalRecommendation
    
    # 시각화 데이터 (JSON/Base64)
    visualizations: Dict[str, Any] = Field(default_factory=dict, description="시각화 데이터")
    
    # 추가 메타데이터
    processing_time_seconds: Optional[float] = Field(None, description="처리 시간 (초)")
