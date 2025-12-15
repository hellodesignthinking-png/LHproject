"""
ZeroSite v40.2 - LH 심사예측 Schema
LH 공공주택 사전심사 AI 예측 Pydantic Models

Author: ZeroSite AI Development Team
Date: 2025-12-14
Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum


class RiskLevel(str, Enum):
    """리스크 레벨"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class FactorAnalysis(BaseModel):
    """개별 Factor 분석 결과"""
    factor_name: str = Field(..., description="Factor 이름 (예: 입지 점수)")
    score: float = Field(..., ge=0, le=100, description="Factor 점수 (0-100)")
    impact: str = Field(..., description="영향도 (매우 긍정적/긍정적/보통/부정적)")
    reason: str = Field(..., description="판단 근거")
    weight: float = Field(..., ge=0, le=1, description="가중치 (0-1)")


class ScenarioPrediction(BaseModel):
    """시나리오별 합격 확률 예측"""
    scenario_name: str = Field(..., description="시나리오 이름 (SCENARIO A/B/C)")
    total_units: int = Field(..., description="총 세대수")
    pass_probability: float = Field(..., ge=0, le=100, description="합격 확률 (%)")
    is_recommended: bool = Field(..., description="추천 시나리오 여부")


class LHReviewRequest(BaseModel):
    """LH 심사예측 요청"""
    context_id: str = Field(..., description="분석 완료된 Context UUID")
    housing_type: str = Field(..., description="LH 주택 유형 (청년, 신혼·신생아 I, 다자녀 등)")
    target_units: int = Field(..., ge=1, description="목표 세대수")


class LHReviewResponse(BaseModel):
    """LH 심사예측 응답"""
    context_id: str = Field(..., description="Context UUID")
    housing_type: str = Field(..., description="LH 주택 유형")
    target_units: int = Field(..., description="목표 세대수")
    
    # 예측 결과
    predicted_score: float = Field(..., ge=0, le=100, description="예상 종합 점수 (0-100)")
    pass_probability: float = Field(..., ge=0, le=100, description="합격 확률 (%)")
    risk_level: RiskLevel = Field(..., description="전체 리스크 레벨")
    
    # 상세 분석
    factors: List[FactorAnalysis] = Field(..., description="6개 Factor별 분석 결과")
    suggestions: List[str] = Field(..., description="개선 제안 목록")
    scenario_comparison: List[ScenarioPrediction] = Field(..., description="시나리오 A/B/C 비교")


class LHReviewHealthResponse(BaseModel):
    """LH 심사예측 엔진 Health Check 응답"""
    status: str = Field(..., description="상태 (healthy/unhealthy)")
    version: str = Field(..., description="엔진 버전")
    model_type: str = Field(..., description="모델 타입")
    features: List[str] = Field(default_factory=list, description="지원 기능 목록")
