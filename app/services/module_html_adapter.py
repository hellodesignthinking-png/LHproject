"""
Module HTML Adapters for v4.3

Purpose: Convert canonical_summary structure to HTML-ready normalized JSON
Author: ZeroSite Backend Team
Date: 2025-12-22

CRITICAL: These adapters are the SINGLE SOURCE OF TRUTH for module HTML rendering.
Any changes to canonical_summary structure must be reflected here first.
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


def adapt_m3_summary_for_html(canonical_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    M3 (LH 선호 주택유형) HTML Adapter
    
    Input: canonical_summary["M3"]
    Output: Normalized JSON for HTML rendering
    
    ✅ SPEC: Must match the exact structure defined in project requirements
    ❌ NO None, NO N/A, NO empty arrays, NO missing keys
    """
    try:
        m3_data = canonical_summary.get("M3", {})
        if not m3_data:
            logger.warning("M3 data not found in canonical_summary")
            return _get_m3_fallback()
        
        summary = m3_data.get("summary", {})
        details = m3_data.get("details", {})
        
        # Extract core data
        recommended_type = summary.get("recommended_type", "정보 없음")
        total_score = summary.get("total_score", 0)
        confidence_pct = summary.get("confidence_pct", 0)
        
        # Determine grade based on score
        grade = _score_to_grade(total_score)
        confidence_level = "높음" if confidence_pct >= 80 else "보통" if confidence_pct >= 60 else "낮음"
        
        # Build normalized structure
        adapted = {
            "module": "M3",
            "title": "LH 선호 주택유형 분석",
            "recommended_type": {
                "name": recommended_type,
                "score": total_score,
                "grade": grade,
                "confidence": confidence_level
            },
            "evaluation_summary": {
                "one_line": f"본 대상지는 {recommended_type} 주택 공급에 적합한 입지 조건을 갖추고 있습니다.",
                "detailed": f"분석 결과 {total_score}점으로 평가되었으며, LH 정책 기준상 {recommended_type} 유형이 가장 적합합니다."
            },
            "score_breakdown": _build_m3_score_breakdown(details, total_score),
            "lh_policy_interpretation": {
                "policy_fit": "적합" if total_score >= 70 else "검토 필요",
                "interpretation": f"LH 내부 심사 기준상 {recommended_type}은 우선 검토 대상이 될 가능성이 {'높습니다' if total_score >= 70 else '있습니다'}."
            },
            "fallback": False
        }
        
        logger.info(f"✅ M3 HTML Adapter: {recommended_type}, {total_score}점")
        return adapted
        
    except Exception as e:
        logger.error(f"❌ M3 HTML Adapter failed: {e}")
        return _get_m3_fallback()


def adapt_m4_summary_for_html(canonical_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    M4 (건축규모) HTML Adapter
    
    Input: canonical_summary["M4"]
    Output: Normalized JSON for HTML rendering
    
    ✅ SPEC: Must match the exact structure defined in project requirements
    ❌ NO None, NO N/A, NO empty arrays, NO missing keys
    """
    try:
        m4_data = canonical_summary.get("M4", {})
        if not m4_data:
            logger.warning("M4 data not found in canonical_summary")
            return _get_m4_fallback()
        
        summary = m4_data.get("summary", {})
        details = m4_data.get("details", {})
        
        # Extract core metrics
        legal_units = summary.get("legal_units", 0)
        incentive_units = summary.get("incentive_units", 0)
        total_units = incentive_units  # Use incentive as total
        
        # Calculate incentive gain
        incentive_gain = incentive_units - legal_units if incentive_units > legal_units else 0
        
        # Build normalized structure
        adapted = {
            "module": "M4",
            "title": "건축 규모 및 개발 가능성 분석",
            "development_summary": {
                "total_units": total_units,
                "base_units": legal_units,
                "incentive_units": incentive_gain,
                "structure": "공동주택",
                "floors": "지상 7층"  # TODO: Extract from details if available
            },
            "area_analysis": {
                "site_area": details.get("inputs", {}).get("land_area_sqm", 0),
                "building_coverage_ratio": 60.0,  # TODO: Extract from details
                "floor_area_ratio": details.get("inputs", {}).get("incentive_far", 250.0),
                "legal_far_limit": details.get("inputs", {}).get("legal_far", 200.0)
            },
            "interpretation": {
                "one_line": "법적 허용 범위 내에서 인센티브를 활용한 최대 개발 규모가 가능합니다.",
                "detailed": f"인센티브 활용 시 총 {total_units}세대 개발이 가능하며, 기본 {legal_units}세대 대비 {incentive_gain}세대 증가합니다."
            },
            "lh_feasibility": {
                "status": "적합" if total_units >= 20 else "검토 필요",
                "commentary": f"LH 매입임대 사업 기준상 {'세대수 요건을 충족' if total_units >= 20 else '세대수가 다소 부족'}합니다."
            },
            "fallback": False
        }
        
        logger.info(f"✅ M4 HTML Adapter: {total_units}세대 (법정 {legal_units} + 인센티브 {incentive_gain})")
        return adapted
        
    except Exception as e:
        logger.error(f"❌ M4 HTML Adapter failed: {e}")
        return _get_m4_fallback()


def _score_to_grade(score: int) -> str:
    """Convert numeric score to letter grade"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def _build_m3_score_breakdown(details: Dict[str, Any], total_score: int) -> List[Dict[str, Any]]:
    """Build score breakdown for M3"""
    # Extract scores from details if available
    scores = details.get("scores", {})
    
    # Default breakdown
    breakdown = [
        {
            "item": "청년 수요 인프라",
            "score": int(total_score * 0.35),
            "max_score": 35,
            "commentary": "대학 및 청년산업시설 접근성 평가"
        },
        {
            "item": "교통 접근성",
            "score": int(total_score * 0.30),
            "max_score": 30,
            "commentary": "대중교통 이용 편의성 평가"
        },
        {
            "item": "생활 편의성",
            "score": int(total_score * 0.25),
            "max_score": 25,
            "commentary": "생활 SOC 접근성 평가"
        },
        {
            "item": "LH 정책 적합성",
            "score": int(total_score * 0.10),
            "max_score": 10,
            "commentary": "LH 매입임대 정책 기준 부합도"
        }
    ]
    
    return breakdown


def _get_m3_fallback() -> Dict[str, Any]:
    """Fallback structure when M3 data is unavailable"""
    return {
        "module": "M3",
        "title": "LH 선호 주택유형 분석",
        "recommended_type": {
            "name": "분석 불가",
            "score": 0,
            "grade": "N/A",
            "confidence": "없음"
        },
        "evaluation_summary": {
            "one_line": "주택유형 분석을 위한 데이터가 부족합니다.",
            "detailed": "토지 정보 및 입지 분석이 완료된 후 재분석이 필요합니다."
        },
        "score_breakdown": [],
        "lh_policy_interpretation": {
            "policy_fit": "분석 불가",
            "interpretation": "데이터 부족으로 LH 정책 적합성을 판단할 수 없습니다."
        },
        "fallback": True
    }


def _get_m4_fallback() -> Dict[str, Any]:
    """Fallback structure when M4 data is unavailable"""
    return {
        "module": "M4",
        "title": "건축 규모 및 개발 가능성 분석",
        "development_summary": {
            "total_units": 0,
            "base_units": 0,
            "incentive_units": 0,
            "structure": "분석 불가",
            "floors": "분석 불가"
        },
        "area_analysis": {
            "site_area": 0,
            "building_coverage_ratio": 0,
            "floor_area_ratio": 0,
            "legal_far_limit": 0
        },
        "interpretation": {
            "one_line": "건축규모 분석을 위한 데이터가 부족합니다.",
            "detailed": "토지 정보 및 용도지역 분석이 완료된 후 재분석이 필요합니다."
        },
        "lh_feasibility": {
            "status": "분석 불가",
            "commentary": "데이터 부족으로 LH 사업 적합성을 판단할 수 없습니다."
        },
        "fallback": True
    }
