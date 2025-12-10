"""
Template Alias Generator for ZeroSite v22
==========================================

Generates 100+ template aliases with safe formatting.

Key Features:
- Comprehensive alias coverage (100+ variables)
- Safe formatting (None/0 handling)
- Unit conversion (원 → 억원, ㎡ → 평)
- Thousands separator
- Percentage formatting

Author: ZeroSite Development Team
Date: 2025-12-10
Version: v22.0.0
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import statistics


class AliasGenerator:
    """Generate comprehensive aliases for template variables"""
    
    @staticmethod
    def safe_format(
        value: Any,
        unit: str = "",
        decimals: int = 2,
        thousands: bool = False,
        multiplier: float = 1.0
    ) -> str:
        """
        Safely format any value with unit
        
        Args:
            value: Value to format
            unit: Unit string (e.g., "억원", "%", "평")
            decimals: Decimal places
            thousands: Add thousands separator
            multiplier: Multiply value before formatting
            
        Returns:
            Formatted string
        """
        if value is None or (isinstance(value, (int, float)) and value == 0):
            return f"0{unit}"
        
        try:
            if isinstance(value, str):
                value = float(value.replace(",", ""))
            
            value = float(value) * multiplier
            
            if thousands:
                formatted = f"{value:,.{decimals}f}"
            else:
                formatted = f"{value:.{decimals}f}"
            
            # Remove unnecessary decimals for integers
            if decimals == 0 or (value == int(value) and decimals <= 2):
                formatted = f"{int(value):,}" if thousands else f"{int(value)}"
            
            return f"{formatted}{unit}"
        except (ValueError, TypeError):
            return f"0{unit}"
    
    @staticmethod
    def calculate_avg_price(comps: List[Dict]) -> float:
        """Calculate average price from comps"""
        if not comps:
            return 0
        prices = [c.get("price_per_sqm", 0) for c in comps if c.get("price_per_sqm")]
        return sum(prices) / len(prices) if prices else 0
    
    @staticmethod
    def calculate_median_price(comps: List[Dict]) -> float:
        """Calculate median price from comps"""
        if not comps:
            return 0
        prices = [c.get("price_per_sqm", 0) for c in comps if c.get("price_per_sqm")]
        return statistics.median(prices) if prices else 0
    
    @staticmethod
    def calculate_std_price(comps: List[Dict]) -> float:
        """Calculate standard deviation of prices"""
        if not comps or len(comps) < 2:
            return 0
        prices = [c.get("price_per_sqm", 0) for c in comps if c.get("price_per_sqm")]
        return statistics.stdev(prices) if len(prices) > 1 else 0
    
    @staticmethod
    def classify_risk_level(score: int) -> str:
        """Classify risk level by score"""
        if score < 30:
            return "매우 낮음"
        elif score < 50:
            return "낮음"
        elif score < 60:
            return "보통"
        elif score < 75:
            return "높음"
        else:
            return "매우 높음"
    
    @staticmethod
    def generate_recommendation(context: Dict) -> str:
        """Generate overall recommendation"""
        financial = context.get("financial_decision", "REVIEW")
        policy = context.get("policy_decision", "REVIEW")
        
        if financial == "GO" and policy == "ADOPT":
            return "즉시 사업 추진 권장"
        elif financial == "CONDITIONAL-GO" and policy == "ADOPT":
            return "조건부 사업 추진 가능"
        elif financial == "GO" and policy == "REVIEW":
            return "정책 재검토 후 추진"
        elif financial == "NO-GO":
            return "사업성 개선 후 재검토"
        else:
            return "종합 재검토 필요"
    
    @classmethod
    def generate_all_aliases(cls, context: Dict) -> Dict:
        """
        Generate 100+ aliases with safe formatting
        
        Args:
            context: Raw context dict
            
        Returns:
            Dict with 100+ formatted aliases
        """
        aliases = {}
        
        # ============================================================
        # Category 1: Basic Information (10 aliases)
        # ============================================================
        aliases.update({
            "address": context.get("address", "대상지"),
            "report_date": datetime.now().strftime("%Y년 %m월 %d일"),
            "report_year": datetime.now().year,
            "report_month": datetime.now().month,
            "report_day": datetime.now().day,
            "report_timestamp": datetime.now().isoformat(),
            "supply_type": context.get("supply_type", "청년"),
            "supply_type_name": context.get("supply_type_name", context.get("supply_type", "청년")),
            "zone_type": context.get("zone_type", "제2종일반주거지역"),
            "zone_description": context.get("zone_description", "중층주택 중심의 편리한 주거환경 조성")
        })
        
        # ============================================================
        # Category 2: Financial Aliases (25 aliases)
        # ============================================================
        total_capex = context.get("total_capex", context.get("total_construction_cost_krw", 0))
        
        aliases.update({
            # CAPEX
            "capex": cls.safe_format(total_capex / 1e8, "억원", 2),
            "capex_krw": total_capex,
            "capex_billion": cls.safe_format(total_capex / 1e8, "", 2),
            "total_capex": cls.safe_format(total_capex / 1e8, "억원", 2),
            
            # Cost breakdown
            "land_cost": cls.safe_format(context.get("land_cost", 0), "억원", 2),
            "building_cost": cls.safe_format(context.get("building_cost", 0), "억원", 2),
            "design_cost": cls.safe_format(context.get("design_cost", context.get("financial_cost", 0)), "억원", 2),
            "financial_cost": cls.safe_format(context.get("financial_cost", 0), "억원", 2),
            
            # Revenue
            "lh_purchase": cls.safe_format(context.get("lh_purchase_price", 0), "억원", 2),
            "lh_purchase_krw": context.get("lh_purchase_price", 0),
            "lh_appraisal_rate": cls.safe_format(context.get("lh_appraisal_rate", 98), "%", 0),
            
            # Profitability
            "profit": cls.safe_format(context.get("npv", context.get("profit_krw", 0)) / 1e8, "억원", 2),
            "profit_krw": context.get("npv", context.get("profit_krw", 0)),
            "roi": cls.safe_format(context.get("roi", context.get("roi_pct", 0)), "%", 2),
            "roi_pct": context.get("roi", context.get("roi_pct", 0)),
            "irr": cls.safe_format(context.get("irr", context.get("irr_public_pct", 0)), "%", 2),
            "irr_pct": context.get("irr", context.get("irr_public_pct", 0)),
            "npv": cls.safe_format(context.get("npv", context.get("npv_public_krw", 0)) / 1e8, "억원", 2),
            "npv_krw": context.get("npv", context.get("npv_public_krw", 0)),
            
            # Payback
            "payback": cls.safe_format(context.get("payback_years", context.get("payback_period_years", 7.2)), "년", 1),
            "payback_years": context.get("payback_years", context.get("payback_period_years", 7.2)),
            "payback_months": cls.safe_format(context.get("payback_years", 7.2) * 12, "개월", 0),
            
            # Margin
            "profit_margin": cls.safe_format(
                (context.get("npv", 0) / total_capex * 100) if total_capex > 0 else 0,
                "%", 2
            ),
            
            # Cost ratios
            "land_cost_ratio": cls.safe_format(
                (context.get("land_cost", 0) * 1e8 / total_capex * 100) if total_capex > 0 else 0,
                "%", 1
            ),
            "building_cost_ratio": cls.safe_format(
                (context.get("building_cost", 0) * 1e8 / total_capex * 100) if total_capex > 0 else 0,
                "%", 1
            )
        })
        
        # ============================================================
        # Category 3: Area Aliases (15 aliases)
        # ============================================================
        land_area_sqm = context.get("land_area_sqm", 0)
        land_area_pyeong = context.get("land_area_pyeong", land_area_sqm * 0.3025)
        
        aliases.update({
            # Land area
            "land_area": cls.safe_format(land_area_sqm, "㎡", 1),
            "land_area_sqm": land_area_sqm,
            "land_area_pyeong": cls.safe_format(land_area_pyeong, "평", 1),
            "land_area_m2": cls.safe_format(land_area_sqm, "㎡", 1),
            
            # Building area
            "building_area": cls.safe_format(context.get("building_area", 0), "㎡", 1),
            "building_area_pyeong": cls.safe_format(context.get("building_area", 0) * 0.3025, "평", 1),
            
            # Buildable area
            "buildable_area": cls.safe_format(context.get("buildable_area", 0), "㎡", 1),
            "buildable_area_pyeong": cls.safe_format(context.get("buildable_area", 0) * 0.3025, "평", 1),
            "buildable_area_legal": cls.safe_format(context.get("buildable_area_legal", 0), "㎡", 1),
            "buildable_area_final": cls.safe_format(context.get("buildable_area_final", 0), "㎡", 1),
            
            # Units
            "total_units": context.get("total_units", 0),
            "unit_count": context.get("total_units", 0),
            "avg_unit_area": cls.safe_format(
                (context.get("buildable_area", 0) / context.get("total_units", 1)) if context.get("total_units", 0) > 0 else 0,
                "㎡", 1
            ),
            "avg_unit_pyeong": cls.safe_format(
                (context.get("buildable_area", 0) * 0.3025 / context.get("total_units", 1)) if context.get("total_units", 0) > 0 else 0,
                "평", 1
            ),
            
            # Density
            "building_coverage": cls.safe_format(
                (context.get("building_area", 0) / land_area_sqm * 100) if land_area_sqm > 0 else 0,
                "%", 1
            )
        })
        
        # ============================================================
        # Category 4: Zoning Aliases (20 aliases)
        # ============================================================
        aliases.update({
            # Legal standards
            "bcr": context.get("bcr_legal", 60),
            "far": context.get("far_legal", 200),
            "bcr_legal": context.get("bcr_legal", 60),
            "far_legal": context.get("far_legal", 200),
            "bcr_legal_pct": cls.safe_format(context.get("bcr_legal", 60), "%", 0),
            "far_legal_pct": cls.safe_format(context.get("far_legal", 200), "%", 0),
            
            # Final (with relaxations)
            "bcr_final": context.get("bcr_final", 60),
            "far_final": context.get("far_final", 240),
            "bcr_final_pct": cls.safe_format(context.get("bcr_final", 60), "%", 0),
            "far_final_pct": cls.safe_format(context.get("far_final", 240), "%", 0),
            
            # Relaxations
            "bcr_relaxation": context.get("bcr_relaxation", 0),
            "far_relaxation": context.get("far_relaxation", 40),
            "far_increase_pct": cls.safe_format(context.get("far_increase_pct", 20.0), "%", 1),
            
            # Location features
            "near_subway": "예" if context.get("near_subway") else "아니오",
            "subway_distance": cls.safe_format(context.get("subway_distance_m", 999), "m", 0),
            "subway_distance_m": context.get("subway_distance_m", 999),
            "school_zone": "예" if context.get("school_zone") else "아니오",
            "school_zone_bool": context.get("school_zone", False),
            
            # Relaxation details
            "relaxations_count": len(context.get("relaxations_applied", [])),
            "relaxations_list": ", ".join(context.get("relaxations_applied", []))
        })
        
        # ============================================================
        # Category 5: Market Aliases (20 aliases)
        # ============================================================
        comps = context.get("comps", [])
        
        aliases.update({
            # Comps
            "comps_count": len(comps),
            "has_comps": len(comps) > 0,
            
            # Price statistics
            "avg_price": cls.safe_format(cls.calculate_avg_price(comps), "원/㎡", 0, thousands=True),
            "avg_price_sqm": int(cls.calculate_avg_price(comps)),
            "median_price": cls.safe_format(cls.calculate_median_price(comps), "원/㎡", 0, thousands=True),
            "median_price_sqm": int(cls.calculate_median_price(comps)),
            "price_std": cls.safe_format(cls.calculate_std_price(comps), "원/㎡", 0, thousands=True),
            "price_std_dev": int(cls.calculate_std_price(comps)),
            
            # Price range
            "min_price": cls.safe_format(
                min([c.get("price_per_sqm", 0) for c in comps]) if comps else 0,
                "원/㎡", 0, thousands=True
            ),
            "max_price": cls.safe_format(
                max([c.get("price_per_sqm", 0) for c in comps]) if comps else 0,
                "원/㎡", 0, thousands=True
            ),
            
            # Market scores
            "market_score": context.get("market_score", 50),
            "market_level": "우수" if context.get("market_score", 50) >= 70 else "양호" if context.get("market_score", 50) >= 50 else "보통",
            
            # CV (Coefficient of Variation)
            "price_cv": cls.safe_format(
                (cls.calculate_std_price(comps) / cls.calculate_avg_price(comps) * 100) if cls.calculate_avg_price(comps) > 0 else 0,
                "%", 1
            ),
            
            # Market positioning
            "market_positioning": context.get("market_positioning", "시장 평균"),
            "price_vs_avg": cls.safe_format(context.get("price_vs_avg_pct", 0), "%", 1),
            "competitive_advantage": "있음" if context.get("competitive_advantage", False) else "없음",
            
            # Data source
            "data_source": context.get("data_source", "estimated"),
            "is_estimated": context.get("data_source") == "estimated",
            "is_real_data": context.get("data_source") == "real_transactions"
        })
        
        # ============================================================
        # Category 6: Demand Aliases (15 aliases)
        # ============================================================
        aliases.update({
            # Demand scores
            "demand_score": context.get("demand_score", 50),
            "demand_level": "우수" if context.get("demand_score", 50) >= 70 else "양호" if context.get("demand_score", 50) >= 50 else "보통",
            "demand_score_pct": cls.safe_format(context.get("demand_score", 50), "%", 0),
            
            # Target population
            "target_population": cls.safe_format(context.get("target_population", 0), "명", 0, thousands=True),
            "target_population_count": context.get("target_population", 0),
            "has_sufficient_demand": context.get("target_population", 0) >= 5000,
            
            # Demographics
            "target_age": context.get("target_age_group", context.get("target_age", "20-35세")),
            "target_household": context.get("target_household", "1-2인 가구"),
            "target_segment": context.get("target_segment", "청년 1인 가구"),
            
            # Supply
            "supply_ratio": context.get("supply_ratio", 85),
            "supply_ratio_pct": cls.safe_format(context.get("supply_ratio", 85), "%", 0),
            "supply_demand_balance": "적정" if 80 <= context.get("supply_ratio", 85) <= 90 else "과잉" if context.get("supply_ratio", 85) > 90 else "부족",
            
            # Competition
            "competition_level": "높음" if context.get("supply_ratio", 85) > 90 else "보통" if context.get("supply_ratio", 85) > 80 else "낮음",
            "market_opportunity": "우수" if context.get("demand_score", 50) >= 70 and context.get("supply_ratio", 85) < 85 else "양호"
        })
        
        # ============================================================
        # Category 7: Risk Aliases (10 aliases)
        # ============================================================
        total_risk = context.get("total_risk_score", 150)
        avg_risk = total_risk / 5 if total_risk else 50  # 5 categories
        
        aliases.update({
            # Total risk
            "total_risk_score": total_risk,
            "avg_risk_score": round(avg_risk, 1),
            "risk_level": cls.classify_risk_level(int(avg_risk)),
            "risk_level_color": "#28a745" if avg_risk < 40 else "#ffc107" if avg_risk < 60 else "#dc3545",
            
            # Individual risks
            "financial_risk": context.get("financial_risk_score", 50),
            "market_risk": context.get("market_risk_score", 50),
            "policy_risk": context.get("policy_risk_score", 35),
            "construction_risk": context.get("construction_risk_score", 45),
            "legal_risk": context.get("legal_risk_score", 40),
            
            # Assessment
            "risk_assessment": "사업 추진 가능" if avg_risk < 60 else "신중한 검토 필요"
        })
        
        # ============================================================
        # Category 8: Decision Aliases (10 aliases)
        # ============================================================
        aliases.update({
            # Financial decision
            "financial_decision": context.get("financial_decision", "REVIEW"),
            "financial_status": "통과" if context.get("financial_decision") == "GO" else "조건부" if context.get("financial_decision") == "CONDITIONAL-GO" else "재검토",
            "financial_color": "#28a745" if context.get("financial_decision") == "GO" else "#ffc107" if context.get("financial_decision") == "CONDITIONAL-GO" else "#dc3545",
            
            # Policy decision
            "policy_decision": context.get("policy_decision", "REVIEW"),
            "policy_status": "채택" if context.get("policy_decision") == "ADOPT" else "재검토",
            "policy_color": "#0066CC" if context.get("policy_decision") == "ADOPT" else "#ffc107",
            
            # Overall
            "overall_decision": cls.generate_recommendation(context),
            "overall_status": "승인" if context.get("financial_decision") == "GO" and context.get("policy_decision") == "ADOPT" else "조건부 승인" if context.get("financial_decision") != "NO-GO" else "재검토",
            "can_proceed": context.get("financial_decision") != "NO-GO",
            "recommendation_text": cls.generate_recommendation(context)
        })
        
        return aliases


# Convenience functions
def generate_aliases(context: Dict) -> Dict:
    """Generate all aliases"""
    return AliasGenerator.generate_all_aliases(context)


def safe_format(value: Any, unit: str = "", decimals: int = 2) -> str:
    """Safe format wrapper"""
    return AliasGenerator.safe_format(value, unit, decimals)
