"""
Final Report Type Mappings and Configurations

Defines what modules are included in each of the 6 final report types.

IMPORTANT: These are ASSEMBLY instructions, not calculation specifications.
Each report type simply selects and orders which module HTML fragments to include.

Author: ZeroSite Backend Team
Date: 2025-12-22
Phase: 3 (PROMPT 3 - Report Type Mapping)
"""

from typing import List, Dict, Literal
from dataclasses import dataclass


@dataclass
class ReportTypeConfig:
    """Configuration for a specific report type"""
    report_id: str
    name_kr: str
    name_en: str
    description: str
    included_modules: List[Literal["M2", "M3", "M4", "M5", "M6"]]
    excluded_modules: List[Literal["M2", "M3", "M4", "M5", "M6"]]
    emphasis: str  # What to emphasize in narrative
    target_pages: str  # Target page count range
    target_audience: str
    cover_color: str  # Hex color for cover page


# 🔹 REPORT TYPE 1: Landowner Summary (토지주용 요약본)
LANDOWNER_SUMMARY = ReportTypeConfig(
    report_id="landowner_summary",
    name_kr="토지주용 요약본",
    name_en="Landowner Summary Report",
    description="토지주가 빠르게 검토할 수 있도록 핵심 내용만 요약",
    included_modules=["M2", "M5", "M6"],  # Land value, Feasibility, LH review
    excluded_modules=["M3", "M4"],  # Skip detailed housing type and scale
    emphasis="투자 수익성과 LH 승인 가능성에 집중",
    target_pages="5-8 pages",
    target_audience="토지 소유주, 투자자",
    cover_color="#2C5F2D"  # Green for landowner
)

# 🔹 REPORT TYPE 2: LH Technical Review (LH 기술검토용)
LH_TECHNICAL = ReportTypeConfig(
    report_id="lh_technical",
    name_kr="LH 기술검토용",
    name_en="LH Technical Review Report",
    description="LH 실무진이 기술적으로 검토할 수 있는 상세 보고서",
    included_modules=["M3", "M4", "M6"],  # Housing type, Scale, LH review
    excluded_modules=["M2", "M5"],  # Skip land value and financial details
    emphasis="LH 정책 부합성과 기술적 타당성에 집중",
    target_pages="10-15 pages",
    target_audience="LH 실무진, 기술 검토자",
    cover_color="#003D82"  # Blue for technical
)

# 🔹 REPORT TYPE 3: Quick Check (빠른 검토용)
QUICK_CHECK = ReportTypeConfig(
    report_id="quick_check",
    name_kr="빠른 검토용",
    name_en="Quick Check Report",
    description="5분 안에 핵심만 파악할 수 있는 초간단 버전",
    included_modules=["M5", "M6"],  # Only feasibility and final decision
    excluded_modules=["M2", "M3", "M4"],  # Skip all details
    emphasis="결론과 최종 판단만 제시",
    target_pages="2-3 pages",
    target_audience="의사결정권자, 임원진",
    cover_color="#FF6B35"  # Orange for quick
)

# 🔹 REPORT TYPE 4: Financial Feasibility (사업성 중심)
FINANCIAL_FEASIBILITY = ReportTypeConfig(
    report_id="financial_feasibility",
    name_kr="사업성 중심 보고서",
    name_en="Financial Feasibility Report",
    description="재무적 타당성에 초점을 맞춘 보고서",
    included_modules=["M2", "M4", "M5"],  # Land value, Scale, Feasibility
    excluded_modules=["M3", "M6"],  # Skip housing type preference and LH review
    emphasis="투자 수익률, NPV, IRR 등 재무 지표에 집중",
    target_pages="8-12 pages",
    target_audience="재무 담당자, CFO, 투자심사역",
    cover_color="#1A5490"  # Dark blue for financial
)

# 🔹 REPORT TYPE 5: All-in-One (전체 통합본)
ALL_IN_ONE = ReportTypeConfig(
    report_id="all_in_one",
    name_kr="전체 통합 보고서",
    name_en="All-in-One Comprehensive Report",
    description="모든 모듈을 포함한 완전한 종합 보고서",
    included_modules=["M2", "M3", "M4", "M5", "M6"],  # Everything
    excluded_modules=[],  # Nothing excluded
    emphasis="모든 분석 결과를 빠짐없이 제공",
    target_pages="20-30 pages",
    target_audience="전체 이해관계자, 아카이브용",
    cover_color="#1F2A44"  # Deep navy for comprehensive
)

# 🔹 REPORT TYPE 6: Executive Summary (경영진용 요약)
EXECUTIVE_SUMMARY = ReportTypeConfig(
    report_id="executive_summary",
    name_kr="경영진용 요약본",
    name_en="Executive Summary Report",
    description="경영진이 의사결정에 필요한 핵심 정보만 제공",
    included_modules=["M2", "M5", "M6"],  # Land value, Feasibility, Decision
    excluded_modules=["M3", "M4"],  # Skip technical details
    emphasis="투자 가치와 최종 의사결정 근거에 집중",
    target_pages="6-10 pages",
    target_audience="CEO, 경영진, 이사회",
    cover_color="#8B1538"  # Burgundy for executive
)


# 🗺️ REPORT TYPE REGISTRY
REPORT_TYPE_CONFIGS: Dict[str, ReportTypeConfig] = {
    "landowner_summary": LANDOWNER_SUMMARY,
    "lh_technical": LH_TECHNICAL,
    "quick_check": QUICK_CHECK,
    "financial_feasibility": FINANCIAL_FEASIBILITY,
    "all_in_one": ALL_IN_ONE,
    "executive_summary": EXECUTIVE_SUMMARY,
}


def get_report_config(report_type: str) -> ReportTypeConfig:
    """
    Get configuration for specified report type
    
    Args:
        report_type: Report type ID
        
    Returns:
        ReportTypeConfig for the report
        
    Raises:
        ValueError: If report type not found
    """
    if report_type not in REPORT_TYPE_CONFIGS:
        valid_types = list(REPORT_TYPE_CONFIGS.keys())
        raise ValueError(
            f"Unknown report type: {report_type}. "
            f"Valid types: {', '.join(valid_types)}"
        )
    
    return REPORT_TYPE_CONFIGS[report_type]


def list_report_types() -> List[str]:
    """Get list of all available report types"""
    return list(REPORT_TYPE_CONFIGS.keys())


def get_required_modules(report_type: str) -> List[str]:
    """
    Get list of required modules for a report type
    
    Args:
        report_type: Report type ID
        
    Returns:
        List of module IDs required for this report
    """
    config = get_report_config(report_type)
    return config.included_modules


# 📊 SECTION ORDER MAPPING
# Defines the standard order in which modules should appear in each report

SECTION_ORDER: Dict[str, List[str]] = {
    "landowner_summary": [
        "cover",
        "executive_intro",
        "M2",  # Land value first (what they own)
        "M5",  # Then feasibility (what they can make)
        "M6",  # Then LH decision (will it be approved)
        "risk_notice",
        "qa_metadata"
    ],
    
    "lh_technical": [
        "cover",
        "executive_intro",
        "M3",  # Housing type (policy compliance)
        "M4",  # Building scale (technical specs)
        "M6",  # LH review result
        "risk_notice",
        "qa_metadata"
    ],
    
    "quick_check": [
        "cover",
        "M5",  # Feasibility only
        "M6",  # Decision only
        "qa_metadata"
    ],
    
    "financial_feasibility": [
        "cover",
        "executive_intro",
        "M2",  # Land value (starting point)
        "M4",  # Scale (unit count drives revenue)
        "M5",  # Feasibility (financial analysis)
        "risk_notice",
        "qa_metadata"
    ],
    
    "all_in_one": [
        "cover",
        "executive_intro",
        "M2",  # Sequential order
        "M3",
        "M4",
        "M5",
        "M6",
        "comprehensive_summary",
        "risk_notice",
        "qa_metadata"
    ],
    
    "executive_summary": [
        "cover",
        "executive_intro",
        "M2",  # Investment value
        "M5",  # ROI analysis
        "M6",  # Decision recommendation
        "risk_notice",
        "qa_metadata"
    ]
}


def get_section_order(report_type: str) -> List[str]:
    """
    Get the section order for a report type
    
    Args:
        report_type: Report type ID
        
    Returns:
        List of section IDs in order
    """
    if report_type not in SECTION_ORDER:
        raise ValueError(f"No section order defined for report type: {report_type}")
    
    return SECTION_ORDER[report_type]


# ================================================================
# Phase 3.10 Final Lock: MANDATORY KPI Declaration
# ================================================================

MANDATORY_KPI = {
    "landowner_summary": {
        "M2": ["land_value_total"],
        "M4": ["total_units"],
        "M5": ["npv"],
        "M6": ["decision"]
    },
    "quick_check": {
        "M5": ["npv", "irr"],
        "M6": ["decision"]
    },
    "executive_summary": {
        "M2": ["land_value_total"],
        "M5": ["npv"],
        "M6": ["decision"]
    },
    "lh_technical": {
        "M3": ["total_score"],
        "M4": ["total_units"],
        "M6": ["decision"]
    },
    "financial_feasibility": {
        "M5": ["npv", "irr"],
        "M2": ["land_value_total"]
    },
    "all_in_one": {
        "M2": ["land_value_total"],
        "M3": ["total_score"],
        "M4": ["total_units"],
        "M5": ["npv"],
        "M6": ["decision"]
    }
}


# ================================================================
# vPOST-FINAL: CRITICAL KPI Declaration (Operational Safety)
# ================================================================
# KPIs that MUST be present for report generation (Hard-Fail)
# Missing CRITICAL KPI → Report generation blocked
# Missing non-critical KPI → Report generated with WARNING panel

CRITICAL_KPI = {
    "landowner_summary": {
        "M5": ["npv"],  # Profitability is critical for landowner decision
        "M6": ["decision"]  # LH decision is must-have
    },
    "quick_check": {
        "M5": ["npv"],  # Quick decision needs profitability
        "M6": ["decision"]  # LH decision is critical
    },
    "executive_summary": {
        "M5": ["npv"],  # Investment decision requires NPV
        "M6": ["decision"]  # LH approval status is critical
    },
    "lh_technical": {
        "M6": ["decision"]  # LH review result is the core output
    },
    "financial_feasibility": {
        "M5": ["npv", "irr"]  # Financial analysis core metrics
    },
    "all_in_one": {
        "M5": ["npv"],  # Comprehensive report needs profitability
        "M6": ["decision"]  # Final decision must be present
    }
}


def get_mandatory_kpi(report_type: str) -> Dict[str, List[str]]:
    """
    Get mandatory KPI for a report type
    
    Args:
        report_type: Report type ID
        
    Returns:
        Dict mapping module_id to list of mandatory KPI keys
    """
    if report_type not in MANDATORY_KPI:
        return {}
    
    return MANDATORY_KPI[report_type]


def get_critical_kpi(report_type: str) -> Dict[str, List[str]]:
    """
    [vPOST-FINAL] Get CRITICAL KPI for a report type
    
    CRITICAL KPIs are those that MUST be present for report generation.
    Missing CRITICAL KPI → Hard-Fail (report blocked)
    Missing non-critical KPI → Soft-Fail (report generated with WARNING)
    
    Args:
        report_type: Report type ID
        
    Returns:
        Dict mapping module_id to list of CRITICAL KPI keys
    """
    if report_type not in CRITICAL_KPI:
        return {}
    
    return CRITICAL_KPI[report_type]
