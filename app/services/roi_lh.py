"""
LH 매입단가 기반 ROI 계산 모듈
LH Purchase Price-Based ROI Calculator

연도별(2024/2025/2026) 및 세대유형별 LH 매입단가를 기반으로 사업성 분석
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


# LH 매입단가 데이터 (원/㎡) - 연도별, 유형별
LH_PURCHASE_PRICES = {
    "2024": {
        "청년": 4_200_000,  # 420만원/㎡
        "신혼·신생아 I": 4_500_000,  # 450만원/㎡
        "신혼·신생아 II": 4_500_000,
        "고령자": 4_800_000,  # 480만원/㎡
        "다자녀": 4_600_000,
        "다문화": 4_400_000,
        "장애인": 4_700_000
    },
    "2025": {
        "청년": 4_300_000,
        "신혼·신생아 I": 4_600_000,
        "신혼·신생아 II": 4_600_000,
        "고령자": 4_900_000,
        "다자녀": 4_700_000,
        "다문화": 4_500_000,
        "장애인": 4_800_000
    },
    "2026": {
        "청년": 4_400_000,
        "신혼·신생아 I": 4_700_000,
        "신혼·신생아 II": 4_700_000,
        "고령자": 5_000_000,
        "다자녀": 4_800_000,
        "다문화": 4_600_000,
        "장애인": 4_900_000
    }
}


@dataclass
class LHROIResult:
    """LH 단가 기반 ROI 계산 결과"""
    total_purchase_price: float  # 총 LH 매입금액 (원)
    total_project_cost: float  # 총 사업비 (원)
    construction_cost: float  # 공사비 (원)
    other_costs: float  # 기타비용 (원)
    roi_percentage: float  # ROI (%)
    profit: float  # 예상 수익 (원)
    is_feasible: bool  # 사업 적합 여부
    lh_unit_price: float  # 적용된 LH 단가 (원/㎡)
    year: str  # 적용 연도
    unit_type: str  # 세대유형
    comment: str  # 종합 평가
    recommendations: list  # 추천사항


def calculate_lh_roi(
    units: int,  # 세대수
    unit_area: float,  # 전용면적 (㎡)
    construction_cost_per_sqm: float,  # ㎡당 공사비 (원/㎡)
    total_floor_area: float,  # 연면적 (㎡)
    year: str = "2024",  # LH 단가 적용 연도
    unit_type: str = "청년",  # 세대유형
    other_cost_ratio: float = 0.10  # 기타비용 비율 (공사비 대비 %)
) -> LHROIResult:
    """
    LH 매입단가 기반 ROI 계산
    
    공식:
    1. 총 LH 매입금액 = 세대수 × 전용면적 × LH 단가(㎡)
    2. 공사비 = 연면적 × ㎡당 공사비
    3. 기타비용 = 공사비 × 기타비용 비율
    4. 총사업비 = 공사비 + 기타비용
    5. ROI = (총매입금액 - 총사업비) / 총사업비 × 100
    
    Args:
        units: 세대수
        unit_area: 전용면적 (㎡)
        construction_cost_per_sqm: ㎡당 공사비 (원/㎡)
        total_floor_area: 연면적 (㎡)
        year: LH 단가 적용 연도 (2024/2025/2026)
        unit_type: 세대유형
        other_cost_ratio: 기타비용 비율 (기본 10%)
    
    Returns:
        LHROIResult 객체
    """
    
    # 1. LH 단가 조회
    lh_unit_price = _get_lh_unit_price(year, unit_type)
    
    # 2. 총 LH 매입금액 계산
    total_purchase_price = units * unit_area * lh_unit_price
    
    # 3. 공사비 계산
    construction_cost = total_floor_area * construction_cost_per_sqm
    
    # 4. 기타비용 계산 (설계비, 감리비, 금융비용 등)
    other_costs = construction_cost * other_cost_ratio
    
    # 5. 총사업비
    total_project_cost = construction_cost + other_costs
    
    # 6. ROI 계산
    profit = total_purchase_price - total_project_cost
    
    if total_project_cost > 0:
        roi_percentage = (profit / total_project_cost) * 100
    else:
        roi_percentage = 0.0
    
    # 7. 사업 적합성 판단
    is_feasible = roi_percentage >= 10.0  # 10% 이상이면 적합
    
    # 8. 종합 평가 생성
    comment = _generate_lh_comment(roi_percentage, is_feasible, profit)
    
    # 9. 추천사항 생성
    recommendations = _generate_lh_recommendations(
        roi_percentage, is_feasible, 
        construction_cost_per_sqm, other_cost_ratio
    )
    
    return LHROIResult(
        total_purchase_price=total_purchase_price,
        total_project_cost=total_project_cost,
        construction_cost=construction_cost,
        other_costs=other_costs,
        roi_percentage=round(roi_percentage, 2),
        profit=profit,
        is_feasible=is_feasible,
        lh_unit_price=lh_unit_price,
        year=year,
        unit_type=unit_type,
        comment=comment,
        recommendations=recommendations
    )


def _get_lh_unit_price(year: str, unit_type: str) -> float:
    """
    연도 및 세대유형별 LH 매입단가 조회
    
    Args:
        year: 연도 (2024/2025/2026)
        unit_type: 세대유형
    
    Returns:
        LH 단가 (원/㎡)
    """
    # 연도 검증
    if year not in LH_PURCHASE_PRICES:
        logger.warning(f"⚠️ 연도 {year}가 없어 2024년 단가 적용")
        year = "2024"
    
    year_prices = LH_PURCHASE_PRICES[year]
    
    # 세대유형 검증 (부분 매칭)
    matched_type = None
    for key in year_prices.keys():
        if unit_type in key or key in unit_type:
            matched_type = key
            break
    
    if matched_type:
        return year_prices[matched_type]
    else:
        logger.warning(f"⚠️ 세대유형 '{unit_type}'이 없어 청년형 단가 적용")
        return year_prices["청년"]


def _generate_lh_comment(
    roi: float,
    is_feasible: bool,
    profit: float
) -> str:
    """LH 모델 종합 평가 생성"""
    
    profit_billion = profit / 100_000_000  # 억원 단위
    
    if roi >= 20:
        return f"LH 매입 사업 적합. ROI {roi:.1f}%로 높은 수익성 예상. 예상 수익 {profit_billion:.1f}억원."
    elif roi >= 10:
        return f"LH 매입 사업 가능. ROI {roi:.1f}%로 적정 수익 확보. 예상 수익 {profit_billion:.1f}억원."
    elif roi >= 5:
        return f"LH 매입 사업 신중 검토 필요. ROI {roi:.1f}%로 낮은 수익률. 예상 수익 {profit_billion:.1f}억원."
    else:
        return f"LH 매입 사업 부적합. ROI {roi:.1f}%로 수익성 미흡. 예상 손실 위험."


def _generate_lh_recommendations(
    roi: float,
    is_feasible: bool,
    construction_cost_per_sqm: float,
    other_cost_ratio: float
) -> list:
    """LH 모델 추천사항 생성"""
    
    recommendations = []
    
    if roi >= 15:
        recommendations.append("✅ 우수한 수익성, 적극 사업 추진 권장")
        recommendations.append("✅ LH 매입 협상 시 유리한 위치")
    elif roi >= 10:
        recommendations.append("✅ 적정 수익성 확보, 사업 진행 가능")
        recommendations.append("⚠️ 공사비 절감 방안 검토로 수익성 개선 가능")
    elif roi >= 5:
        recommendations.append("⚠️ 낮은 수익률, 신중한 검토 필요")
        recommendations.append("⚠️ 공사비 및 기타비용 대폭 절감 필수")
        recommendations.append("⚠️ LH 매입단가 상향 협상 필요")
    else:
        recommendations.append("❌ 수익성 미흡, 사업 재검토 권장")
        recommendations.append("❌ 사업비 구조 전면 재검토 필요")
    
    # 공사비 관련
    if construction_cost_per_sqm > 3_500_000:
        recommendations.append("⚠️ 공사비가 높음 - VE(가치공학) 적용 검토")
    
    # 기타비용 관련
    if other_cost_ratio > 0.12:
        recommendations.append("⚠️ 기타비용 비율이 높음 - 금융비용 절감 방안 필요")
    
    return recommendations


def format_lh_result_for_report(result: LHROIResult) -> Dict[str, Any]:
    """
    보고서용 LH ROI 결과 포맷팅
    
    Args:
        result: LHROIResult 객체
    
    Returns:
        보고서용 딕셔너리
    """
    return {
        "model_type": "LH 매입단가 기반",
        "total_cost": {
            "value": result.total_project_cost,
            "formatted": f"{result.total_project_cost / 100_000_000:.1f}억원"
        },
        "revenue": {
            "value": result.total_purchase_price,
            "formatted": f"{result.total_purchase_price / 100_000_000:.1f}억원"
        },
        "roi": {
            "value": result.roi_percentage,
            "formatted": f"{result.roi_percentage:.1f}%"
        },
        "feasibility": "적합" if result.is_feasible else "부적합",
        "details": {
            "lh_unit_price": f"{result.lh_unit_price:,.0f}원/㎡",
            "year": result.year,
            "unit_type": result.unit_type,
            "construction_cost": f"{result.construction_cost / 100_000_000:.1f}억원",
            "other_costs": f"{result.other_costs / 100_000_000:.1f}억원",
            "profit": f"{result.profit / 100_000_000:.1f}억원"
        },
        "comment": result.comment,
        "recommendations": result.recommendations
    }
