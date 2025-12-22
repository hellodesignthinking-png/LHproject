"""
ZeroSite v4.3 Risk Master Application Rules Engine
===================================================

리스크 마스터 적용 규칙 엔진: 보고서 타입별로 어떤 리스크를 어떤 강도로 적용할지 정의

핵심 원칙:
1. 보고서 타입에 따라 리스크 선택/강도 자동 결정
2. 일관성 100% 보장 (규칙 코드화)
3. 톤 변환 자동화 (친화적/객관적/분석적)

Version: 1.0
Date: 2025-12-22
Author: Claude AI Assistant
"""

from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel


class RiskType(str, Enum):
    """6개 리스크 타입 (RISK_MASTER_V4.2 기준)"""
    R1_POLICY_CHANGE = "R1_정책_제도_변동"
    R2_LH_REVIEW = "R2_LH_심사_기준"
    R3_LAND_PRICE = "R3_토지_가격_변동"
    R4_BUILDING_SCALE = "R4_건축_규모_법규"
    R5_FINANCIAL = "R5_재무_구조"
    R6_SCHEDULE_DELAY = "R6_사업_일정_지연"


class RiskLevel(str, Enum):
    """리스크 서술 강도"""
    CRITICAL = "최우선"       # ⭐⭐⭐ 매우 상세, 시나리오 포함
    HIGH = "중요"             # ⭐⭐ 상세, 대응 전략 포함
    MEDIUM = "모니터링"        # ⭐ 요약만
    OMIT = "생략"             # 언급 안 함


class RiskTone(str, Enum):
    """리스크 서술 톤"""
    FRIENDLY = "친화적"           # 토지주용: "관리 가능한", "함께 대응"
    OBJECTIVE = "객관적"          # LH용: "검토됨", "고려됨"
    ANALYTICAL = "분석적"         # 투자자용: "NPV 영향", "IRR 변화"
    SUMMARY = "요약"              # Quick Check용: 핵심만
    COMPREHENSIVE = "종합"        # All-in-One용: 전체 상세


class ReportTypeRiskMapping(BaseModel):
    """보고서 타입별 리스크 적용 규칙"""
    report_type: str
    risks: Dict[str, str]  # RiskType.value -> RiskLevel.value
    tone: RiskTone


# ============================================================================
# 보고서 타입별 리스크 매핑 정의
# ============================================================================

RISK_MAPPINGS = {
    "landowner_summary": ReportTypeRiskMapping(
        report_type="landowner_summary",
        risks={
            RiskType.R1_POLICY_CHANGE.value: RiskLevel.MEDIUM.value,
            RiskType.R2_LH_REVIEW.value: RiskLevel.MEDIUM.value,
            RiskType.R3_LAND_PRICE.value: RiskLevel.HIGH.value,       # 토지주는 가격에 민감
            RiskType.R4_BUILDING_SCALE.value: RiskLevel.HIGH.value,
            RiskType.R5_FINANCIAL.value: RiskLevel.MEDIUM.value,
            RiskType.R6_SCHEDULE_DELAY.value: RiskLevel.MEDIUM.value,
        },
        tone=RiskTone.FRIENDLY
    ),
    
    "lh_technical": ReportTypeRiskMapping(
        report_type="lh_technical",
        risks={
            RiskType.R1_POLICY_CHANGE.value: RiskLevel.HIGH.value,
            RiskType.R2_LH_REVIEW.value: RiskLevel.HIGH.value,
            RiskType.R3_LAND_PRICE.value: RiskLevel.HIGH.value,
            RiskType.R4_BUILDING_SCALE.value: RiskLevel.CRITICAL.value,  # LH는 법규 중시
            RiskType.R5_FINANCIAL.value: RiskLevel.HIGH.value,
            RiskType.R6_SCHEDULE_DELAY.value: RiskLevel.HIGH.value,
        },
        tone=RiskTone.OBJECTIVE
    ),
    
    "financial_feasibility": ReportTypeRiskMapping(
        report_type="financial_feasibility",
        risks={
            RiskType.R1_POLICY_CHANGE.value: RiskLevel.MEDIUM.value,
            RiskType.R2_LH_REVIEW.value: RiskLevel.MEDIUM.value,
            RiskType.R3_LAND_PRICE.value: RiskLevel.CRITICAL.value,    # 투자자는 수익성 중시
            RiskType.R4_BUILDING_SCALE.value: RiskLevel.HIGH.value,
            RiskType.R5_FINANCIAL.value: RiskLevel.CRITICAL.value,
            RiskType.R6_SCHEDULE_DELAY.value: RiskLevel.CRITICAL.value,
        },
        tone=RiskTone.ANALYTICAL
    ),
    
    "quick_check": ReportTypeRiskMapping(
        report_type="quick_check",
        risks={
            RiskType.R1_POLICY_CHANGE.value: RiskLevel.OMIT.value,
            RiskType.R2_LH_REVIEW.value: RiskLevel.MEDIUM.value,
            RiskType.R3_LAND_PRICE.value: RiskLevel.CRITICAL.value,
            RiskType.R4_BUILDING_SCALE.value: RiskLevel.MEDIUM.value,
            RiskType.R5_FINANCIAL.value: RiskLevel.CRITICAL.value,
            RiskType.R6_SCHEDULE_DELAY.value: RiskLevel.CRITICAL.value,
        },
        tone=RiskTone.SUMMARY
    ),
    
    "all_in_one": ReportTypeRiskMapping(
        report_type="all_in_one",
        risks={
            RiskType.R1_POLICY_CHANGE.value: RiskLevel.CRITICAL.value,
            RiskType.R2_LH_REVIEW.value: RiskLevel.CRITICAL.value,
            RiskType.R3_LAND_PRICE.value: RiskLevel.CRITICAL.value,
            RiskType.R4_BUILDING_SCALE.value: RiskLevel.CRITICAL.value,
            RiskType.R5_FINANCIAL.value: RiskLevel.CRITICAL.value,
            RiskType.R6_SCHEDULE_DELAY.value: RiskLevel.CRITICAL.value,
        },
        tone=RiskTone.COMPREHENSIVE
    ),
    
    "presentation": ReportTypeRiskMapping(
        report_type="presentation",
        risks={
            RiskType.R1_POLICY_CHANGE.value: RiskLevel.OMIT.value,
            RiskType.R2_LH_REVIEW.value: RiskLevel.OMIT.value,
            RiskType.R3_LAND_PRICE.value: RiskLevel.HIGH.value,
            RiskType.R4_BUILDING_SCALE.value: RiskLevel.MEDIUM.value,
            RiskType.R5_FINANCIAL.value: RiskLevel.HIGH.value,
            RiskType.R6_SCHEDULE_DELAY.value: RiskLevel.HIGH.value,
        },
        tone=RiskTone.SUMMARY
    ),
}


# ============================================================================
# Public API Functions
# ============================================================================

def get_risk_mapping(report_type: str) -> ReportTypeRiskMapping:
    """
    보고서 타입에 따른 리스크 적용 규칙 반환
    
    Args:
        report_type: 보고서 타입 (landowner_summary, lh_technical, etc.)
    
    Returns:
        해당 보고서 타입의 리스크 매핑 규칙
    """
    if report_type not in RISK_MAPPINGS:
        # 기본값: All-in-One과 동일 (모든 리스크 포함)
        return RISK_MAPPINGS["all_in_one"]
    
    return RISK_MAPPINGS[report_type]


def should_include_risk(report_type: str, risk_type: RiskType) -> bool:
    """
    특정 보고서 타입에서 특정 리스크를 포함해야 하는지 판단
    
    Args:
        report_type: 보고서 타입
        risk_type: 리스크 타입
    
    Returns:
        True if 포함, False if 생략
    """
    mapping = get_risk_mapping(report_type)
    level = mapping.risks.get(risk_type.value, RiskLevel.OMIT.value)
    return level != RiskLevel.OMIT.value


def get_risk_detail_level(report_type: str, risk_type: RiskType) -> RiskLevel:
    """
    특정 보고서 타입에서 특정 리스크의 서술 상세도 반환
    
    Args:
        report_type: 보고서 타입
        risk_type: 리스크 타입
    
    Returns:
        RiskLevel enum (CRITICAL, HIGH, MEDIUM, OMIT)
    """
    mapping = get_risk_mapping(report_type)
    level_str = mapping.risks.get(risk_type.value, RiskLevel.OMIT.value)
    return RiskLevel(level_str)


def get_risk_tone(report_type: str) -> RiskTone:
    """
    보고서 타입에 따른 리스크 서술 톤 반환
    
    Args:
        report_type: 보고서 타입
    
    Returns:
        RiskTone enum (FRIENDLY, OBJECTIVE, ANALYTICAL, etc.)
    """
    mapping = get_risk_mapping(report_type)
    return mapping.tone


def get_all_applicable_risks(report_type: str) -> Dict[RiskType, RiskLevel]:
    """
    특정 보고서 타입에 적용 가능한 모든 리스크 반환
    
    Args:
        report_type: 보고서 타입
    
    Returns:
        Dict[RiskType, RiskLevel] - 적용 가능한 리스크와 레벨
    """
    mapping = get_risk_mapping(report_type)
    applicable_risks = {}
    
    for risk_type in RiskType:
        level_str = mapping.risks.get(risk_type.value, RiskLevel.OMIT.value)
        level = RiskLevel(level_str)
        if level != RiskLevel.OMIT:
            applicable_risks[risk_type] = level
    
    return applicable_risks
