"""
시장기반(Real Market) ROI 계산 모듈
Market-Based ROI Calculator

실거래 토지가, 시장 건축비, 신축 시세를 기반으로 한 실제 시장 사업성 분석
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


# 지역별 실거래가 기준 단가 (원/㎡) - 토지
REGIONAL_LAND_PRICES = {
    "서울": 5_500_000,  # 550만원/㎡
    "경기": 2_800_000,  # 280만원/㎡
    "인천": 2_800_000,
    "부산": 2_200_000,
    "대구": 1_900_000,
    "광주": 1_800_000,
    "대전": 1_900_000,
    "울산": 2_000_000,
    "세종": 2_500_000,
    "기타": 1_500_000  # 기타 지방
}

# 지역별 신축 시세 (원/㎡) - 전용면적 기준
REGIONAL_NEW_APARTMENT_PRICES = {
    "서울": 12_000_000,  # 1,200만원/㎡
    "경기": 7_500_000,   # 750만원/㎡
    "인천": 7_000_000,
    "부산": 6_500_000,
    "대구": 5_500_000,
    "광주": 5_000_000,
    "대전": 5_500_000,
    "울산": 6_000_000,
    "세종": 7_000_000,
    "기타": 4_500_000
}

# 건축 난이도 보정 계수
CONSTRUCTION_DIFFICULTY_FACTORS = {
    "평지": 1.0,      # 기본
    "경사지": 1.15,    # +15%
    "도심지": 1.20,    # +20% (소음, 접근성 등)
    "협소지": 1.25     # +25%
}


@dataclass
class MarketROIResult:
    """시장기반 ROI 계산 결과"""
    total_revenue: float  # 매각가 (원)
    total_project_cost: float  # 총 사업비 (원)
    land_cost: float  # 토지비 (원)
    construction_cost: float  # 공사비 (원)
    other_costs: float  # 기타비용 (원)
    roi_percentage: float  # ROI (%)
    profit: float  # 예상 수익 (원)
    is_feasible: bool  # 사업 가능 여부
    land_unit_price: float  # 토지 단가 (원/㎡)
    sale_unit_price: float  # 매각 단가 (원/㎡)
    region: str  # 지역
    comment: str  # 종합 평가
    recommendations: list  # 추천사항


def calculate_market_roi(
    land_area: float,  # 대지면적 (㎡)
    total_floor_area: float,  # 연면적 (㎡)
    units: int,  # 세대수
    unit_area: float,  # 전용면적 (㎡)
    construction_cost_per_pyeong: float,  # 평당 건축비 (원/평)
    region: str = "서울",  # 지역
    difficulty: str = "평지",  # 난이도
    other_cost_ratio: float = 0.10,  # 기타비용 비율 (공사비 대비)
    sale_discount: float = 0.85,  # 매각 할인율 (85%)
    custom_land_price: Optional[float] = None,  # 사용자 지정 토지 단가 (원/㎡)
    custom_sale_price: Optional[float] = None  # 사용자 지정 매각 단가 (원/㎡)
) -> MarketROIResult:
    """
    시장기반(Real Market) ROI 계산
    
    공식:
    1. 토지비 = 대지면적 × 지역 실거래가
    2. 공사비 = 연면적 × (평당 건축비 / 3.3058) × 난이도 보정
    3. 기타비용 = 공사비 × (8~12%)
    4. 매각가 = 세대수 × 전용면적 × 신축 시세 × 0.85
    5. ROI = (매각가 - 총사업비) / 총사업비 × 100
    
    Args:
        land_area: 대지면적 (㎡)
        total_floor_area: 연면적 (㎡)
        units: 세대수
        unit_area: 전용면적 (㎡)
        construction_cost_per_pyeong: 평당 건축비 (원/평)
        region: 지역 (서울, 경기, 부산 등)
        difficulty: 건축 난이도 (평지, 경사지, 도심지, 협소지)
        other_cost_ratio: 기타비용 비율
        sale_discount: 매각 할인율
        custom_land_price: 사용자 지정 토지 단가 (없으면 지역 기준 사용)
        custom_sale_price: 사용자 지정 매각 단가 (없으면 지역 기준 사용)
    
    Returns:
        MarketROIResult 객체
    """
    
    # 1. 토지비 계산
    land_unit_price = custom_land_price if custom_land_price else _get_land_price(region)
    land_cost = land_area * land_unit_price
    
    # 2. 공사비 계산 (평당 → ㎡당 변환 후 난이도 보정)
    construction_cost_per_sqm = construction_cost_per_pyeong / 3.3058
    difficulty_factor = CONSTRUCTION_DIFFICULTY_FACTORS.get(difficulty, 1.0)
    construction_cost = total_floor_area * construction_cost_per_sqm * difficulty_factor
    
    # 3. 기타비용 계산 (설계, 감리, 금융, 인입비 등)
    other_costs = construction_cost * other_cost_ratio
    
    # 4. 총사업비
    total_project_cost = land_cost + construction_cost + other_costs
    
    # 5. 매각가 계산
    sale_unit_price = custom_sale_price if custom_sale_price else _get_sale_price(region)
    total_revenue = units * unit_area * sale_unit_price * sale_discount
    
    # 6. ROI 계산
    profit = total_revenue - total_project_cost
    
    if total_project_cost > 0:
        roi_percentage = (profit / total_project_cost) * 100
    else:
        roi_percentage = 0.0
    
    # 7. 사업 가능성 판단
    is_feasible = roi_percentage >= 15.0  # 시장 모델은 15% 이상
    
    # 8. 종합 평가 생성
    comment = _generate_market_comment(roi_percentage, is_feasible, profit)
    
    # 9. 추천사항 생성
    recommendations = _generate_market_recommendations(
        roi_percentage, is_feasible,
        land_cost / total_project_cost,  # 토지비 비중
        construction_cost / total_project_cost,  # 공사비 비중
        difficulty
    )
    
    return MarketROIResult(
        total_revenue=total_revenue,
        total_project_cost=total_project_cost,
        land_cost=land_cost,
        construction_cost=construction_cost,
        other_costs=other_costs,
        roi_percentage=round(roi_percentage, 2),
        profit=profit,
        is_feasible=is_feasible,
        land_unit_price=land_unit_price,
        sale_unit_price=sale_unit_price * sale_discount,
        region=region,
        comment=comment,
        recommendations=recommendations
    )


def _get_land_price(region: str) -> float:
    """지역별 토지 실거래가 조회"""
    # 지역명에서 키워드 추출
    for key in REGIONAL_LAND_PRICES.keys():
        if key in region:
            return REGIONAL_LAND_PRICES[key]
    
    logger.warning(f"⚠️ 지역 '{region}'에 대한 토지가 없어 기타 지역 적용")
    return REGIONAL_LAND_PRICES["기타"]


def _get_sale_price(region: str) -> float:
    """지역별 신축 시세 조회"""
    for key in REGIONAL_NEW_APARTMENT_PRICES.keys():
        if key in region:
            return REGIONAL_NEW_APARTMENT_PRICES[key]
    
    logger.warning(f"⚠️ 지역 '{region}'에 대한 시세 없어 기타 지역 적용")
    return REGIONAL_NEW_APARTMENT_PRICES["기타"]


def _generate_market_comment(
    roi: float,
    is_feasible: bool,
    profit: float
) -> str:
    """시장 모델 종합 평가 생성"""
    
    profit_billion = profit / 100_000_000  # 억원 단위
    
    if roi >= 25:
        return f"시장 매각 사업 매우 적합. ROI {roi:.1f}%로 우수한 수익성. 예상 수익 {profit_billion:.1f}억원."
    elif roi >= 15:
        return f"시장 매각 사업 가능. ROI {roi:.1f}%로 적정 수익 확보. 예상 수익 {profit_billion:.1f}억원."
    elif roi >= 10:
        return f"시장 매각 사업 신중 검토. ROI {roi:.1f}%로 낮은 수익률. 예상 수익 {profit_billion:.1f}억원."
    else:
        return f"시장 매각 사업 불가. ROI {roi:.1f}%로 수익성 미흡. 예상 손실 위험."


def _generate_market_recommendations(
    roi: float,
    is_feasible: bool,
    land_cost_ratio: float,
    construction_cost_ratio: float,
    difficulty: str
) -> list:
    """시장 모델 추천사항 생성"""
    
    recommendations = []
    
    if roi >= 20:
        recommendations.append("✅ 우수한 시장 수익성, 적극 추진 권장")
        recommendations.append("✅ 분양가 상향 여력 있음")
    elif roi >= 15:
        recommendations.append("✅ 적정 수익성 확보, 사업 진행 가능")
        recommendations.append("⚠️ 시장 변동성 모니터링 필요")
    elif roi >= 10:
        recommendations.append("⚠️ 낮은 수익률, 신중한 검토 필요")
        recommendations.append("⚠️ 사업비 절감 및 분양가 상향 필수")
    else:
        recommendations.append("❌ 수익성 미흡, 사업 재검토 권장")
        recommendations.append("❌ 토지비 또는 공사비 대폭 절감 필요")
    
    # 토지비 비중 분석
    if land_cost_ratio > 0.50:
        recommendations.append("⚠️ 토지비 비중이 높음 (50% 초과) - 매입가 재협상 검토")
    
    # 공사비 비중 분석
    if construction_cost_ratio > 0.40:
        recommendations.append("⚠️ 공사비 비중이 높음 (40% 초과) - VE 적용 필요")
    
    # 난이도별 추천
    if difficulty in ["경사지", "협소지"]:
        recommendations.append("⚠️ 시공 난이도 높음 - 전문 시공사 선정 중요")
    
    return recommendations


def format_market_result_for_report(result: MarketROIResult) -> Dict[str, Any]:
    """
    보고서용 시장 ROI 결과 포맷팅
    
    Args:
        result: MarketROIResult 객체
    
    Returns:
        보고서용 딕셔너리
    """
    return {
        "model_type": "시장기반(Real Market)",
        "total_cost": {
            "value": result.total_project_cost,
            "formatted": f"{result.total_project_cost / 100_000_000:.1f}억원"
        },
        "revenue": {
            "value": result.total_revenue,
            "formatted": f"{result.total_revenue / 100_000_000:.1f}억원"
        },
        "roi": {
            "value": result.roi_percentage,
            "formatted": f"{result.roi_percentage:.1f}%"
        },
        "feasibility": "가능" if result.is_feasible else "불가",
        "details": {
            "land_cost": f"{result.land_cost / 100_000_000:.1f}억원",
            "construction_cost": f"{result.construction_cost / 100_000_000:.1f}억원",
            "other_costs": f"{result.other_costs / 100_000_000:.1f}억원",
            "profit": f"{result.profit / 100_000_000:.1f}억원",
            "land_unit_price": f"{result.land_unit_price:,.0f}원/㎡",
            "sale_unit_price": f"{result.sale_unit_price:,.0f}원/㎡",
            "region": result.region
        },
        "comment": result.comment,
        "recommendations": result.recommendations
    }
