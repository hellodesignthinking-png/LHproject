"""
Financial Engine Output Schema
===============================

JSON 기반 입출력 스키마 정의
보고서 생성과 완전 분리

Author: ZeroSite Development Team
Date: 2025-12-06
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from enum import Enum


class CalculationMode(str, Enum):
    """계산 모드"""
    COST_INDEX = "cost_index"              # 공사비연동제
    GENERAL_CONSTRUCTION = "general"       # 민간 건축
    DEVELOPER_FEASIBILITY = "developer"    # IRR/ROI 분석


class FinancialInput(BaseModel):
    """
    사업성 분석 입력 데이터
    
    Phase 1 (Land + Scale)의 출력을 그대로 받음
    """
    # From Phase 1
    land_area: float = Field(..., description="대지면적 (m²)")
    gross_floor_area: float = Field(..., description="총 연면적 (m²)")
    residential_gfa: float = Field(..., description="주거 연면적 (m²)")
    unit_count: int = Field(..., description="세대수")
    parking_count: int = Field(..., description="주차대수")
    zone_type: str = Field(..., description="용도지역")
    
    # Additional inputs
    land_appraisal_price: Optional[float] = Field(None, description="토지 감정가")
    construction_period: int = Field(default=24, description="공사기간 (개월)")
    calculation_mode: CalculationMode = Field(
        default=CalculationMode.COST_INDEX,
        description="계산 모드"
    )
    
    # Location
    region: str = Field(default="서울", description="지역 (서울/경기/지방)")


class CAPEXBreakdown(BaseModel):
    """총 투자비 상세"""
    direct_construction: float = Field(..., description="직접 공사비")
    indirect_cost: float = Field(..., description="간접비")
    finance_cost: float = Field(..., description="금융비용")
    land_cost: float = Field(..., description="토지비")
    total_capex: float = Field(..., description="총 투자비")
    
    # Details
    construction_unit_price: float = Field(..., description="공사비 단가 (원/m²)")
    regional_coefficient: float = Field(..., description="지역 계수")
    cost_index: float = Field(..., description="공사비 연동지수")


class OPEXBreakdown(BaseModel):
    """운영비 상세"""
    maintenance: float = Field(..., description="유지보수비")
    management: float = Field(..., description="관리비")
    utilities: float = Field(..., description="공과금")
    insurance: float = Field(..., description="보험료")
    other: float = Field(..., description="기타")
    total_opex: float = Field(..., description="총 운영비 (연간)")


class RevenueBreakdown(BaseModel):
    """수익 구조"""
    rent_per_unit: float = Field(..., description="세대당 임대료 (월)")
    total_units: int = Field(..., description="총 세대수")
    occupancy_rate: float = Field(..., description="입주율")
    gross_income: float = Field(..., description="총 수입 (연간)")
    net_operating_income: float = Field(..., description="순운영수익 (NOI)")


class FinancialMetrics(BaseModel):
    """재무 지표"""
    roi: float = Field(..., description="투자수익률 (ROI)")
    irr_10yr: float = Field(..., description="10년 내부수익률 (IRR)")
    cap_rate: float = Field(..., description="자본환원율 (Cap Rate)")
    payback_period: float = Field(..., description="투자회수기간 (년)")
    debt_service_coverage: Optional[float] = Field(None, description="부채상환비율 (DSCR)")


class LHGapAnalysis(BaseModel):
    """LH 매입가 갭 분석"""
    estimated_lh_price: float = Field(..., description="예상 LH 매입가")
    total_project_cost: float = Field(..., description="총 사업비")
    gap_amount: float = Field(..., description="갭 금액 (LH가 - 사업비)")
    gap_ratio: float = Field(..., description="갭 비율 (%)")
    is_profitable: bool = Field(..., description="수익성 여부")
    
    # LH Purchase Price Calculation
    lh_base_price: float = Field(..., description="LH 기준단가")
    lh_regional_factor: float = Field(..., description="LH 지역계수")
    lh_calculation_method: str = Field(..., description="LH 산정방식")


class FinancialResult(BaseModel):
    """
    사업성 분석 최종 결과 (JSON Only)
    
    이 데이터를 Phase 3 (LH Decision Engine)에 전달
    """
    # Metadata
    calculation_mode: CalculationMode = Field(..., description="계산 모드")
    calculation_timestamp: str = Field(..., description="계산 시각")
    
    # Input Echo
    input_data: FinancialInput = Field(..., description="입력 데이터")
    
    # CAPEX
    capex: CAPEXBreakdown = Field(..., description="총 투자비 상세")
    
    # OPEX
    opex: OPEXBreakdown = Field(..., description="운영비 상세")
    
    # Revenue
    revenue: RevenueBreakdown = Field(..., description="수익 구조")
    
    # Financial Metrics
    metrics: FinancialMetrics = Field(..., description="재무 지표")
    
    # LH Gap Analysis
    lh_gap: LHGapAnalysis = Field(..., description="LH 갭 분석")
    
    # Summary
    is_feasible: bool = Field(..., description="사업 타당성")
    risk_level: str = Field(..., description="리스크 수준 (LOW/MEDIUM/HIGH)")
    recommendation: str = Field(..., description="추천 의견 (GO/REVIEW/NO-GO)")
    
    # Additional Context
    assumptions: Dict[str, Any] = Field(
        default_factory=dict,
        description="계산 가정 사항"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "calculation_mode": "cost_index",
                "capex": {
                    "total_capex": 19500000000,
                    "direct_construction": 14000000000,
                    "indirect_cost": 2400000000,
                    "finance_cost": 3100000000,
                    "land_cost": 0
                },
                "metrics": {
                    "roi": 0.049,
                    "irr_10yr": 0.076,
                    "cap_rate": 0.045
                },
                "lh_gap": {
                    "gap_amount": -3500000000,
                    "is_profitable": False
                },
                "is_feasible": True,
                "recommendation": "REVIEW"
            }
        }


class FinancialEngineResponse(BaseModel):
    """API Response Wrapper"""
    ok: bool = Field(default=True)
    result: FinancialResult = Field(...)
    execution_time_ms: int = Field(...)
    errors: Optional[list] = Field(default=None)
