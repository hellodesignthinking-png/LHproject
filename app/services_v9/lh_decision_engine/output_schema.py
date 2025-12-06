"""
LH Decision Engine Output Schema
=================================

JSON 기반 입출력 스키마
100점 LH 평가 시스템

Author: ZeroSite Development Team
Date: 2025-12-06
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class DecisionType(str, Enum):
    """LH 심사 결정"""
    GO = "GO"                 # 사업 추진 가능
    REVIEW = "REVIEW"         # 조건부 추진 (개선 필요)
    NO_GO = "NO-GO"           # 사업 부적합


class LHScoreBreakdown(BaseModel):
    """
    LH 100점 평가 상세
    
    기준:
    - 입지 적합성: 25점
    - 사업 타당성: 30점
    - 시장 경쟁력: 25점
    - 재무 건전성: 10점
    - 법규 적합성: 10점
    """
    # Location Suitability (25점)
    location_score: float = Field(..., ge=0, le=25, description="입지 적합성 (25점)")
    transportation_access: float = Field(..., description="교통 접근성")
    living_convenience: float = Field(..., description="생활 편의성")
    education_environment: float = Field(..., description="교육 환경")
    
    # Business Feasibility (30점)
    feasibility_score: float = Field(..., ge=0, le=30, description="사업 타당성 (30점)")
    far_bcr_adequacy: float = Field(..., description="용적률/건폐율 적정성")
    unit_count_adequacy: float = Field(..., description="세대수 적정성")
    land_price_adequacy: float = Field(..., description="토지가 적정성")
    
    # Market Competitiveness (25점)
    market_score: float = Field(..., ge=0, le=25, description="시장 경쟁력 (25점)")
    demand_potential: float = Field(..., description="수요 잠재력")
    competition_level: float = Field(..., description="경쟁 수준")
    price_competitiveness: float = Field(..., description="가격 경쟁력")
    
    # Financial Soundness (10점)
    financial_score: float = Field(..., ge=0, le=10, description="재무 건전성 (10점)")
    profitability: float = Field(..., description="수익성 (ROI/IRR)")
    lh_purchase_gap: float = Field(..., description="LH 매입가 갭")
    
    # Regulatory Compliance (10점)
    regulatory_score: float = Field(..., ge=0, le=10, description="법규 적합성 (10점)")
    legal_compliance: float = Field(..., description="법규 준수")
    lh_policy_fit: float = Field(..., description="LH 정책 부합도")
    
    # Total
    total_score: float = Field(..., ge=0, le=100, description="총점 (100점)")
    
    # Grade
    grade: str = Field(..., description="등급 (A/B/C/D/F)")


class ImprovementProposal(BaseModel):
    """개선 제안"""
    category: str = Field(..., description="개선 분야")
    current_issue: str = Field(..., description="현재 문제점")
    proposal: str = Field(..., description="개선 제안")
    expected_impact: str = Field(..., description="기대 효과")
    priority: str = Field(..., description="우선순위 (HIGH/MEDIUM/LOW)")


class DecisionRationale(BaseModel):
    """결정 근거"""
    strengths: List[str] = Field(..., description="강점 요인")
    weaknesses: List[str] = Field(..., description="약점 요인")
    opportunities: List[str] = Field(..., description="기회 요인")
    threats: List[str] = Field(..., description="위협 요인")


class LHDecisionInput(BaseModel):
    """
    LH Decision Engine 입력
    
    Phase 1 + Phase 2 결과를 받음
    """
    # From Phase 1 (Land + Scale)
    land_area: float = Field(..., description="대지면적")
    gross_floor_area: float = Field(..., description="총 연면적")
    unit_count: int = Field(..., description="세대수")
    zone_type: str = Field(..., description="용도지역")
    building_coverage_ratio: float = Field(..., description="건폐율")
    floor_area_ratio: float = Field(..., description="용적률")
    
    # From Phase 2 (Financial)
    total_capex: float = Field(..., description="총 투자비")
    noi: float = Field(..., description="순운영수익")
    roi: float = Field(..., description="투자수익률")
    irr: float = Field(..., description="내부수익률")
    lh_gap_amount: float = Field(..., description="LH 갭 금액")
    lh_gap_ratio: float = Field(..., description="LH 갭 비율")
    
    # Location (optional)
    latitude: Optional[float] = Field(None, description="위도")
    longitude: Optional[float] = Field(None, description="경도")
    region: str = Field(default="서울", description="지역")
    
    # Additional context
    address: Optional[str] = Field(None, description="주소")


class LHDecisionResult(BaseModel):
    """
    LH Decision Engine 최종 결과 (JSON Only)
    
    Phase 4 (PDF Report)로 전달
    """
    # Metadata
    calculation_timestamp: str = Field(..., description="계산 시각")
    
    # Input Echo
    input_data: LHDecisionInput = Field(..., description="입력 데이터")
    
    # LH Score (100점)
    score: LHScoreBreakdown = Field(..., description="LH 100점 평가")
    
    # Decision
    decision: DecisionType = Field(..., description="최종 결정")
    confidence: float = Field(..., ge=0, le=1, description="신뢰도 (0-1)")
    
    # Rationale
    rationale: DecisionRationale = Field(..., description="결정 근거 (SWOT)")
    
    # Improvement Proposals
    improvement_proposals: List[ImprovementProposal] = Field(
        default_factory=list,
        description="개선 제안 사항"
    )
    
    # Summary
    executive_summary: str = Field(..., description="종합 의견")
    key_recommendations: List[str] = Field(..., description="핵심 권장사항")
    
    # Risk Assessment
    risk_level: str = Field(..., description="리스크 수준 (LOW/MEDIUM/HIGH/CRITICAL)")
    critical_risks: List[str] = Field(default_factory=list, description="주요 리스크")
    
    # Next Steps
    next_steps: List[str] = Field(..., description="다음 단계 조치사항")
    
    class Config:
        json_schema_extra = {
            "example": {
                "decision": "REVIEW",
                "confidence": 0.75,
                "score": {
                    "total_score": 72.5,
                    "grade": "C",
                    "location_score": 18.5,
                    "feasibility_score": 22.0,
                    "market_score": 19.0,
                    "financial_score": 6.0,
                    "regulatory_score": 7.0
                },
                "executive_summary": "조건부 사업 추진 가능. 재무 건전성 개선 필요.",
                "risk_level": "MEDIUM"
            }
        }


class LHDecisionEngineResponse(BaseModel):
    """API Response Wrapper"""
    ok: bool = Field(default=True)
    result: LHDecisionResult = Field(...)
    execution_time_ms: int = Field(...)
    errors: Optional[list] = Field(default=None)
