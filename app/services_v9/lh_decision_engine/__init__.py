"""
ZeroSite LH Decision Engine
===========================

독립 LH 심사 모듈

Input: Phase 1 (Land + Scale) + Phase 2 (Financial)
Output: LH Score (100점) + Grade + Decision + Proposals

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 3.0 - Modular Architecture

Usage:
    from app.services_v9.lh_decision_engine import run_lh_decision_engine, LHDecisionInput
    
    input_data = LHDecisionInput(
        land_area=850,
        gross_floor_area=2125,
        unit_count=30,
        zone_type="제2종일반주거지역",
        building_coverage_ratio=60.0,
        floor_area_ratio=250.0,
        total_capex=13377400690,
        noi=264392500,
        roi=1.98,
        irr=-1.19,
        lh_gap_amount=-8184431940,
        lh_gap_ratio=-61.18,
        address="서울특별시 강남구 테헤란로 123"
    )
    
    result = run_lh_decision_engine(input_data)
    print(f"Decision: {result.decision}")  # GO / REVIEW / NO-GO
    print(f"Score: {result.score.total_score}/100")
    print(f"Grade: {result.score.grade}")
"""

from .core_scorer import LHDecisionEngineCore, run_lh_decision_engine
from .output_schema import (
    LHDecisionInput,
    LHDecisionResult,
    LHScoreBreakdown,
    DecisionType,
    ImprovementProposal,
    DecisionRationale
)
from .config import (
    LH_SCORING_WEIGHTS,
    LH_DECISION_THRESHOLDS,
    LH_CRITERIA_DATA
)

__all__ = [
    # Main Engine
    "LHDecisionEngineCore",
    "run_lh_decision_engine",
    
    # Input/Output Schemas
    "LHDecisionInput",
    "LHDecisionResult",
    "LHScoreBreakdown",
    "DecisionType",
    "ImprovementProposal",
    "DecisionRationale",
    
    # Config
    "LH_SCORING_WEIGHTS",
    "LH_DECISION_THRESHOLDS",
    "LH_CRITERIA_DATA",
]
