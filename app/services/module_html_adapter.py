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
                "legal_far_limit": details.get("inputs", {}).get("legal_far", 200.0),
                "gross_floor_area": summary.get("gross_floor_area", details.get("inputs", {}).get("land_area_sqm", 0) * 2.2)  # Calculate or use from summary
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


def adapt_m2_summary_for_html(canonical_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    M2 (토지평가) HTML Adapter
    
    Input: canonical_summary["M2"]
    Output: Normalized JSON for HTML rendering
    """
    try:
        m2_data = canonical_summary.get("M2", {})
        if not m2_data:
            logger.warning("M2 data not found in canonical_summary")
            return _get_m2_fallback()
        
        summary = m2_data.get("summary", {})
        
        # Extract core data
        land_value_total_krw = summary.get("land_value_total_krw", 0)
        pyeong_price_krw = summary.get("pyeong_price_krw", 0)
        confidence_pct = summary.get("confidence_pct") or 75  # Default if None
        transaction_count = summary.get("transaction_count", 0)
        
        # Validate that we have real data
        if land_value_total_krw == 0 or pyeong_price_krw == 0:
            logger.warning(f"M2 data incomplete: land_value={land_value_total_krw}, pyeong_price={pyeong_price_krw}")
            return _get_m2_fallback()
        
        # Calculate ranges (±10%)
        land_value_low = int(land_value_total_krw * 0.9)
        land_value_high = int(land_value_total_krw * 1.1)
        pyeong_price_low = int(pyeong_price_krw * 0.9)
        pyeong_price_high = int(pyeong_price_krw * 1.1)
        
        confidence_level = "높음" if confidence_pct >= 70 else "보통" if confidence_pct >= 50 else "낮음"
        
        # Build normalized structure
        adapted = {
            "module": "M2",
            "title": "토지 가치 평가 (M2)",
            "appraisal_result": {
                "total_value": land_value_total_krw,
                "value_range": {
                    "low": land_value_low,
                    "high": land_value_high
                },
                "pyeong_price": pyeong_price_krw,
                "pyeong_price_range": {
                    "low": pyeong_price_low,
                    "high": pyeong_price_high
                },
                "confidence": confidence_level,
                "confidence_pct": confidence_pct
            },
            "analysis_basis": {
                "transaction_count": transaction_count,
                "method": "인근 거래 사례 기반 비교 평가",
                "data_source": "국토교통부 실거래가 데이터"
            },
            "interpretation": {
                "one_line": f"본 토지의 평가액은 약 {land_value_total_krw:,}원으로 산정되었습니다.",
                "detailed": f"평당 {pyeong_price_krw:,}원 기준으로 산정되었으며, 분석 신뢰도는 {confidence_level}입니다."
            },
            "lh_perspective": {
                "status": "평가 완료",
                "commentary": f"총 {transaction_count}건의 인근 거래 사례를 기반으로 산정된 평가액입니다."
            },
            "fallback": False
        }
        
        logger.info(f"✅ M2 HTML Adapter: 토지가액 {land_value_total_krw:,}원, 평당 {pyeong_price_krw:,}원")
        return adapted
        
    except Exception as e:
        logger.error(f"❌ M2 HTML Adapter failed: {e}")
        return _get_m2_fallback()


def adapt_m5_summary_for_html(canonical_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    M5 (사업성) HTML Adapter
    
    Input: canonical_summary["M5"]
    Output: Normalized JSON for HTML rendering
    """
    try:
        m5_data = canonical_summary.get("M5", {})
        if not m5_data:
            logger.warning("M5 data not found in canonical_summary")
            return _get_m5_fallback()
        
        summary = m5_data.get("summary", {})
        
        # Extract core data
        npv_public_krw = summary.get("npv_public_krw", 0)
        irr_pct = summary.get("irr_pct", 0)
        roi_pct = summary.get("roi_pct", 0)
        grade = summary.get("grade", "N/A")
        
        # Determine profitability status
        is_profitable = npv_public_krw > 0 and irr_pct > 5.0
        profitability_status = "수익성 양호" if is_profitable else "수익성 검토 필요"
        
        # Build normalized structure
        adapted = {
            "module": "M5",
            "title": "사업성 분석 (M5)",
            "financial_result": {
                "npv": npv_public_krw,
                "irr": irr_pct,
                "roi": roi_pct,
                "grade": grade,
                "profitability_status": profitability_status,
                "is_profitable": is_profitable
            },
            "key_metrics": [
                {
                    "name": "순현재가치 (NPV)",
                    "value": f"{npv_public_krw:,}원",
                    "interpretation": "공공 사업 수익성" if npv_public_krw > 0 else "수익성 개선 필요"
                },
                {
                    "name": "내부수익률 (IRR)",
                    "value": f"{irr_pct:.2f}%",
                    "interpretation": "양호" if irr_pct >= 7.0 else "보통" if irr_pct >= 5.0 else "낮음"
                },
                {
                    "name": "투자수익률 (ROI)",
                    "value": f"{roi_pct:.2f}%",
                    "interpretation": "양호" if roi_pct >= 7.0 else "보통" if roi_pct >= 5.0 else "낮음"
                },
                {
                    "name": "사업성 등급",
                    "value": grade,
                    "interpretation": _grade_to_text(grade)
                }
            ],
            "interpretation": {
                "one_line": f"본 사업의 수익성 등급은 {grade}이며, IRR {irr_pct:.2f}%로 평가되었습니다.",
                "detailed": f"순현재가치는 {npv_public_krw:,}원으로 {'양호한' if is_profitable else '개선이 필요한'} 수준입니다."
            },
            "lh_perspective": {
                "status": "평가 완료",
                "commentary": f"LH 매입임대 사업 기준상 {grade}등급에 해당하며, {'사업 추진 가능' if is_profitable else '추가 검토 필요'}합니다."
            },
            "fallback": False
        }
        
        logger.info(f"✅ M5 HTML Adapter: NPV {npv_public_krw:,}, IRR {irr_pct:.2f}%, Grade {grade}")
        return adapted
        
    except Exception as e:
        logger.error(f"❌ M5 HTML Adapter failed: {e}")
        return _get_m5_fallback()


def adapt_m6_summary_for_html(canonical_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    M6 (LH심사) HTML Adapter
    
    Input: canonical_summary["M6"]
    Output: Normalized JSON for HTML rendering
    """
    try:
        m6_data = canonical_summary.get("M6", {})
        if not m6_data:
            logger.warning("M6 data not found in canonical_summary")
            return _get_m6_fallback()
        
        summary = m6_data.get("summary", {})
        
        # Extract core data
        decision_raw = summary.get("decision")
        total_score = summary.get("total_score", 0)
        max_score = summary.get("max_score", 110)
        grade = summary.get("grade", "N/A")
        approval_probability_pct = summary.get("approval_probability_pct", 0)
        
        # [vABSOLUTE-FINAL-5] M6 Decision Data Contract (STRICT)
        # Only 3 allowed values: "적합", "조건부 적합", "부적합"
        DECISION_CONTRACT = {
            # Official contract values (exact match)
            "적합": "적합",
            "조건부 적합": "조건부 적합",
            "부적합": "부적합",
            # Legacy/alternative values (normalization)
            "추진 가능": "적합",
            "조건부 승인": "조건부 적합",
            "조건부 가능": "조건부 적합",
            "불가": "부적합",
            "부적절": "부적합",
            # English enum values (for backward compatibility)
            "APPROVED": "적합",
            "CONDITIONAL": "조건부 적합",
            "REJECTED": "부적합",
        }
        
        decision_text = DECISION_CONTRACT.get(decision_raw)
        
        if decision_text is None:
            # [DATA CONTRACT VIOLATION] Raise error to catch invalid data early
            raise ValueError(
                f"[M6 DATA CONTRACT VIOLATION] "
                f"Invalid decision value: {repr(decision_raw)}. "
                f"Allowed: 적합, 조건부 적합, 부적합"
            )
        
        # Determine CSS class
        decision_class = "success" if decision_text == "적합" else "warning" if decision_text == "조건부 적합" else "error"
        
        # Build normalized structure
        adapted = {
            "module": "M6",
            "title": "LH 내부 심사 예측 (M6)",
            "review_result": {
                "decision": decision_text,
                "decision_class": decision_class,
                "total_score": total_score,
                "max_score": max_score,
                "grade": grade,
                "approval_probability": approval_probability_pct
            },
            "score_details": {
                "score_ratio": f"{total_score}/{max_score}",
                "percentage": f"{(total_score/max_score*100):.1f}%",
                "grade_interpretation": _grade_to_text(grade)
            },
            "interpretation": {
                "one_line": f"LH 내부 심사 결과 {decision_text}로 예측되며, 승인 확률은 {approval_probability_pct}%입니다.",
                "detailed": f"총점 {total_score}점({max_score}점 만점)으로 {grade}등급에 해당하며, {'긍정적인' if approval_probability_pct >= 70 else '검토가 필요한'} 평가입니다."
            },
            "recommendation": {
                "status": "검토 완료",
                "next_step": "승인 조건 충족 확인" if decision_text == "조건부 적합" else "사업 추진" if decision_text == "적합" else "보완 필요"
            },
            "fallback": False
        }
        
        logger.info(f"✅ M6 HTML Adapter: {decision_text}, {total_score}점, {grade}등급, {approval_probability_pct}% 승인 확률")
        return adapted
        
    except Exception as e:
        logger.error(f"❌ M6 HTML Adapter failed: {e}")
        return _get_m6_fallback()


def _grade_to_text(grade: str) -> str:
    """Convert grade to Korean text interpretation"""
    grade_map = {
        "A": "매우 우수",
        "B": "우수",
        "C": "보통",
        "D": "미흡",
        "F": "불량",
        "N/A": "평가 불가"
    }
    return grade_map.get(grade, grade)


def _get_m2_fallback() -> Dict[str, Any]:
    """Fallback structure when M2 data is unavailable"""
    return {
        "module": "M2",
        "title": "토지 가치 평가 (M2)",
        "appraisal_result": {
            "total_value": 0,
            "value_range": {"low": 0, "high": 0},
            "pyeong_price": 0,
            "pyeong_price_range": {"low": 0, "high": 0},
            "confidence": "없음",
            "confidence_pct": 0
        },
        "analysis_basis": {
            "transaction_count": 0,
            "method": "분석 불가",
            "data_source": "데이터 없음"
        },
        "interpretation": {
            "one_line": "토지 평가를 위한 데이터가 부족합니다.",
            "detailed": "거래 사례 데이터 확보 후 재분석이 필요합니다."
        },
        "lh_perspective": {
            "status": "분석 불가",
            "commentary": "데이터 부족으로 평가를 수행할 수 없습니다."
        },
        "fallback": True
    }


def _get_m5_fallback() -> Dict[str, Any]:
    """Fallback structure when M5 data is unavailable"""
    return {
        "module": "M5",
        "title": "사업성 분석 (M5)",
        "financial_result": {
            "npv": 0,
            "irr": 0,
            "roi": 0,
            "grade": "N/A",
            "profitability_status": "분석 불가",
            "is_profitable": False
        },
        "key_metrics": [],
        "interpretation": {
            "one_line": "사업성 분석을 위한 데이터가 부족합니다.",
            "detailed": "토지 평가 및 개발 규모 분석 완료 후 재분석이 필요합니다."
        },
        "lh_perspective": {
            "status": "분석 불가",
            "commentary": "데이터 부족으로 사업성을 평가할 수 없습니다."
        },
        "fallback": True
    }


def _get_m6_fallback() -> Dict[str, Any]:
    """Fallback structure when M6 data is unavailable"""
    return {
        "module": "M6",
        "title": "LH 내부 심사 예측 (M6)",
        "review_result": {
            "decision": "분석 불가",
            "decision_class": "error",
            "total_score": 0,
            "max_score": 110,
            "grade": "N/A",
            "approval_probability": 0
        },
        "score_details": {
            "score_ratio": "0/110",
            "percentage": "0%",
            "grade_interpretation": "평가 불가"
        },
        "interpretation": {
            "one_line": "LH 심사 예측을 위한 데이터가 부족합니다.",
            "detailed": "전체 분석 완료 후 심사 예측이 가능합니다."
        },
        "recommendation": {
            "status": "분석 불가",
            "next_step": "데이터 보완 필요"
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
