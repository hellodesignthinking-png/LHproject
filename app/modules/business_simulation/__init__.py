"""
사업성 시뮬레이션 모듈

건축비 산정, LH 매입가 시뮬레이션, ROI/IRR 분석, 민감도 분석 등
"""

from .construction_cost import calculate_construction_cost
from .purchase_price import calculate_lh_purchase
from .roi_calculator import calculate_roi_irr
from .sensitivity import analyze_sensitivity
from .service import analyze_comprehensive

# Alias for compatibility
simulate_lh_purchase = calculate_lh_purchase

__all__ = [
    "calculate_construction_cost",
    "calculate_lh_purchase",
    "simulate_lh_purchase",
    "calculate_roi_irr",
    "analyze_sensitivity",
    "analyze_comprehensive",
]
