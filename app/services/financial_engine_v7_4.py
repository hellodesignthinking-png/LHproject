"""
ZeroSite v7.4 Financial Feasibility Simulation Engine

Comprehensive financial analysis for LH Public Housing projects including:
- CapEx (Capital Expenditure) calculation
- OpEx (Operating Expense) projection
- NOI (Net Operating Income) modeling
- LH 연동형 매입가 estimation
- Breakeven analysis
- Sensitivity analysis (optimistic/base/pessimistic scenarios)
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class FinancialMetrics:
    """Container for financial analysis results"""
    total_capex: float
    annual_revenue: float
    annual_opex: float
    noi: float
    cap_rate: float
    irr: float
    npv: float
    payback_period: float
    breakeven_occupancy: float
    breakeven_rent: float


class FinancialEngine:
    """
    Financial Feasibility Simulation Engine for LH Projects
    
    Provides comprehensive financial analysis including:
    - Development costs (land acquisition, construction, soft costs)
    - Operating model (revenue, expenses, NOI)
    - Return metrics (IRR, NPV, cap rate)
    - Breakeven analysis
    - Sensitivity testing
    """
    
    # LH Standard Assumptions (2025.1 - Optimized)
    # Version: 2025.1 (Updated 2025-12-02 based on real LH project benchmarks)
    LH_ASSUMPTIONS = {
        # Land acquisition (per ㎡)
        'land_price_multiplier': {
            'seoul_gangnam': 15_000_000,  # 강남권 (원/㎡)
            'seoul_gangbuk': 11_000_000,  # 강북권 (Updated: was 10M)
            'seoul_suburban': 7_000_000,  # 외곽권
            'default': 9_000_000
        },
        
        # Acquisition costs (% of land price)
        'acquisition_tax_rate': 0.044,  # 취득세 4.4%
        'brokerage_fee_rate': 0.009,    # 중개수수료 0.9%
        'legal_due_diligence_rate': 0.005,  # 법무실사 0.5%
        
        # Construction costs (per ㎡)
        'construction_cost_per_sqm': {
            'standard': 3_500_000,  # 표준형 (원/㎡)
            'premium': 4_500_000,   # 고급형
            'economy': 3_000_000    # 저가형
        },
        
        # Soft costs (% of hard costs)
        'design_fee_rate': 0.08,        # 설계비 8%
        'permit_fee_rate': 0.02,        # 인허가비 2%
        'insurance_rate': 0.015,        # 보험료 1.5%
        'contingency_rate': 0.10,       # 예비비 10%
        
        # FF&E (per unit)
        'ffe_per_unit': 5_000_000,      # 가구/집기 500만원/세대
        
        # Unit assumptions
        'avg_unit_size': 45,            # 평균 전용면적 45㎡
        'gross_up_factor': 1.35,        # 전용→연면적 환산 (공용면적 포함) - optimized design
        'units_per_100_sqm_land': 5.0,  # 토지 100㎡당 세대수 (Updated: was 4.5, now 5.0 for high-rise)
        
        # Revenue (monthly rent per unit by type)
        # Updated 2025.1: Maximum allowable under LH policy (80% of market)
        'monthly_rent': {
            '청년': 550_000,             # 청년형 월 55만원 (80% of ~69만 market rate)
            '신혼부부 I': 650_000,       # 신혼부부 I 월 65만원 (80% of ~81만)
            '신혼부부 II': 700_000,      # 신혼부부 II 월 70만원 (80% of ~87만)
            '다자녀': 750_000,           # 다자녀 월 75만원 (80% of ~94만)
            '고령자': 580_000,           # 고령자 월 58만원 (80% of ~72만)
            'default': 600_000           # 기본 월 60만원
        },
        
        # Occupancy
        'year1_occupancy': 0.80,        # 1차년도 입주율 80%
        'stabilized_occupancy': 0.95,   # 안정기 입주율 95%
        'stabilization_year': 2,         # 안정화 시점 (2년차)
        
        # Rental escalation
        'annual_rent_increase': 0.025,  # 연간 임대료 인상 2.5%
        
        # Operating expenses (annual per unit)
        # Updated 2025.1: Optimized for scale efficiency and modern management
        'property_management_fee': 480_000,    # PM비 월 4만원 × 12 (scale efficiency)
        'maintenance_repair': 840_000,         # 유지보수 월 7만원 × 12 (modern systems)
        'utilities_common': 420_000,           # 공용 관리비 월 3.5만원 × 12 (energy efficiency)
        'property_tax_rate': 0.004,            # 재산세 0.4% (of property value)
        'insurance_annual': 360_000,           # 보험료 연 36만원/세대 (volume discount)
        'marketing_leasing': 180_000,          # 마케팅/임대 연 18만원/세대 (digital marketing)
        'reserve_for_replacement': 420_000,    # 대체 적립금 월 3.5만원 × 12
        
        # Financial assumptions
        'discount_rate': 0.06,          # 할인율 6% (NPV 계산용)
        'projection_years': 10,         # 예측 기간 10년
        'lh_target_cap_rate': 0.045,   # LH 목표 Cap Rate 4.5%
    }
    
    def __init__(self):
        """Initialize financial engine"""
        self.assumptions = self.LH_ASSUMPTIONS.copy()
        logger.info("💰 Financial Engine v7.4 initialized")
    
    def calculate_capex(
        self,
        land_area: float,
        address: str,
        construction_type: str = "standard",
        include_breakdown: bool = True,
        land_appraisal_price: float = None  # 🔥 NEW: 사용자 입력 감정평가액
    ) -> Dict[str, Any]:
        """
        Calculate total Capital Expenditure (CapEx)
        
        Args:
            land_area: Land area in ㎡
            address: Site address (to determine land price zone)
            construction_type: 'standard', 'premium', or 'economy'
            include_breakdown: Whether to include detailed breakdown
            land_appraisal_price: User-provided land appraisal price (optional)
        
        Returns:
            Dictionary with CapEx breakdown and total
        """
        logger.info(f"📊 Calculating CapEx for {land_area}㎡ site")
        
        # 1. Land Acquisition Costs
        if land_appraisal_price and land_appraisal_price > 0:
            # 🔥 사용자 입력 감정가 사용 (우선순위)
            land_purchase_price = land_appraisal_price
            land_price_zone = "user_provided"
            logger.info(f"✅ Using user-provided land appraisal: {self._format_krw(land_appraisal_price)}")
        else:
            # Determine land price zone from address (fallback)
            land_price_zone = self._determine_land_price_zone(address)
            land_price_per_sqm = self.assumptions['land_price_multiplier'][land_price_zone]
            land_purchase_price = land_area * land_price_per_sqm
            logger.info(f"📍 Using estimated land price: {land_price_zone} zone")
        acquisition_tax = land_purchase_price * self.assumptions['acquisition_tax_rate']
        brokerage_fee = land_purchase_price * self.assumptions['brokerage_fee_rate']
        legal_due_diligence = land_purchase_price * self.assumptions['legal_due_diligence_rate']
        
        total_land_cost = (
            land_purchase_price +
            acquisition_tax +
            brokerage_fee +
            legal_due_diligence
        )
        
        # 2. Calculate unit count
        unit_count = self._calculate_unit_count(land_area)
        
        # 3. Construction Costs (Hard Costs)
        avg_unit_size = self.assumptions['avg_unit_size']
        gross_up_factor = self.assumptions['gross_up_factor']
        total_gross_area = unit_count * avg_unit_size * gross_up_factor
        
        construction_cost_per_sqm = self.assumptions['construction_cost_per_sqm'][construction_type]
        hard_costs = total_gross_area * construction_cost_per_sqm
        
        # 4. Soft Costs
        design_fee = hard_costs * self.assumptions['design_fee_rate']
        permit_fee = hard_costs * self.assumptions['permit_fee_rate']
        insurance = hard_costs * self.assumptions['insurance_rate']
        contingency = hard_costs * self.assumptions['contingency_rate']
        
        total_soft_costs = design_fee + permit_fee + insurance + contingency
        
        # 5. FF&E
        ffe_costs = unit_count * self.assumptions['ffe_per_unit']
        
        # Total CapEx
        total_capex = total_land_cost + hard_costs + total_soft_costs + ffe_costs
        
        # Per-unit metrics
        capex_per_unit = total_capex / unit_count
        capex_per_sqm = total_capex / total_gross_area
        
        result = {
            'total_capex': total_capex,
            'capex_per_unit': capex_per_unit,
            'capex_per_sqm': capex_per_sqm,
            'unit_count': unit_count,
            'total_gross_area': total_gross_area,
            'land_price_zone': land_price_zone,
        }
        
        if include_breakdown:
            result['breakdown'] = {
                'land_acquisition': {
                    'purchase_price': land_purchase_price,
                    'acquisition_tax': acquisition_tax,
                    'brokerage_fee': brokerage_fee,
                    'legal_due_diligence': legal_due_diligence,
                    'subtotal': total_land_cost,
                    'percentage': (total_land_cost / total_capex) * 100
                },
                'construction_hard_costs': {
                    'total_gross_area_sqm': total_gross_area,
                    'cost_per_sqm': construction_cost_per_sqm,
                    'subtotal': hard_costs,
                    'percentage': (hard_costs / total_capex) * 100
                },
                'soft_costs': {
                    'design_fee': design_fee,
                    'permit_fee': permit_fee,
                    'insurance': insurance,
                    'contingency': contingency,
                    'subtotal': total_soft_costs,
                    'percentage': (total_soft_costs / total_capex) * 100
                },
                'ffe': {
                    'per_unit': self.assumptions['ffe_per_unit'],
                    'subtotal': ffe_costs,
                    'percentage': (ffe_costs / total_capex) * 100
                }
            }
        
        logger.info(f"✅ CapEx calculated: {self._format_krw(total_capex)} ({unit_count} units)")
        return result
    
    def project_opex(
        self,
        unit_count: int,
        total_capex: float,
        years: int = 10,
        include_annual_breakdown: bool = True
    ) -> Dict[str, Any]:
        """
        Project Operating Expenses (OpEx) over time
        
        Args:
            unit_count: Number of units
            total_capex: Total capital expenditure (for property tax calculation)
            years: Number of years to project
            include_annual_breakdown: Whether to include year-by-year breakdown
        
        Returns:
            Dictionary with OpEx projections
        """
        logger.info(f"📊 Projecting OpEx for {unit_count} units over {years} years")
        
        # Annual OpEx per unit (Year 1)
        pm_fee = self.assumptions['property_management_fee']
        maintenance = self.assumptions['maintenance_repair']
        utilities = self.assumptions['utilities_common']
        property_tax = total_capex * self.assumptions['property_tax_rate']
        property_tax_per_unit = property_tax / unit_count
        insurance = self.assumptions['insurance_annual']
        marketing = self.assumptions['marketing_leasing']
        reserves = self.assumptions['reserve_for_replacement']
        
        year1_opex_per_unit = (
            pm_fee +
            maintenance +
            utilities +
            property_tax_per_unit +
            insurance +
            marketing +
            reserves
        )
        
        year1_total_opex = year1_opex_per_unit * unit_count
        
        result = {
            'year1_total_opex': year1_total_opex,
            'year1_opex_per_unit': year1_opex_per_unit,
            'opex_components': {
                'property_management': pm_fee,
                'maintenance_repair': maintenance,
                'utilities_common': utilities,
                'property_tax': property_tax_per_unit,
                'insurance': insurance,
                'marketing_leasing': marketing,
                'reserve_for_replacement': reserves
            }
        }
        
        if include_annual_breakdown:
            annual_opex = []
            inflation_rate = 0.02
            
            for year in range(1, years + 1):
                year_opex = year1_total_opex * ((1 + inflation_rate) ** (year - 1))
                annual_opex.append({
                    'year': year,
                    'total_opex': year_opex,
                    'opex_per_unit': year_opex / unit_count
                })
            
            result['annual_breakdown'] = annual_opex
        
        logger.info(f"✅ OpEx projected: {self._format_krw(year1_total_opex)}/year")
        return result
    
    def calculate_noi(
        self,
        unit_count: int,
        unit_type: str,
        annual_opex: float,
        occupancy_rate: float = None,
        year: int = 1
    ) -> Dict[str, Any]:
        """Calculate Net Operating Income (NOI)"""
        if occupancy_rate is None:
            if year == 1:
                occupancy_rate = self.assumptions['year1_occupancy']
            else:
                occupancy_rate = self.assumptions['stabilized_occupancy']
        
        base_monthly_rent = self.assumptions['monthly_rent'].get(
            unit_type,
            self.assumptions['monthly_rent']['default']
        )
        
        escalation_rate = self.assumptions['annual_rent_increase']
        current_monthly_rent = base_monthly_rent * ((1 + escalation_rate) ** (year - 1))
        
        annual_gross_income = current_monthly_rent * 12 * unit_count
        annual_effective_income = annual_gross_income * occupancy_rate
        
        noi = annual_effective_income - annual_opex
        noi_margin = (noi / annual_effective_income) * 100 if annual_effective_income > 0 else 0
        
        return {
            'year': year,
            'gross_annual_income': annual_gross_income,
            'occupancy_rate': occupancy_rate,
            'effective_annual_income': annual_effective_income,
            'annual_opex': annual_opex,
            'noi': noi,
            'noi_margin_percent': noi_margin,
            'monthly_rent': current_monthly_rent,
            'monthly_noi': noi / 12
        }
    
    def calculate_return_metrics(
        self,
        total_capex: float,
        noi_stabilized: float,
        cash_flows: List[float] = None
    ) -> Dict[str, Any]:
        """Calculate key return metrics"""
        cap_rate = (noi_stabilized / total_capex) * 100 if total_capex > 0 else 0
        cash_on_cash = cap_rate
        
        result = {
            'cap_rate_percent': cap_rate,
            'cash_on_cash_percent': cash_on_cash,
            'lh_target_cap_rate_percent': self.assumptions['lh_target_cap_rate'] * 100,
            'meets_lh_target': cap_rate >= (self.assumptions['lh_target_cap_rate'] * 100)
        }
        
        if cash_flows and len(cash_flows) > 0:
            irr = self._calculate_irr([-total_capex] + cash_flows)
            npv = self._calculate_npv(
                [-total_capex] + cash_flows,
                self.assumptions['discount_rate']
            )
            
            result['irr_percent'] = irr * 100 if irr else 0
            result['npv'] = npv
        
        return result
    
    def calculate_breakeven(
        self,
        total_capex: float,
        unit_count: int,
        unit_type: str,
        annual_opex: float
    ) -> Dict[str, Any]:
        """Calculate breakeven metrics"""
        base_monthly_rent = self.assumptions['monthly_rent'].get(
            unit_type,
            self.assumptions['monthly_rent']['default']
        )
        
        target_cap_rate = self.assumptions['lh_target_cap_rate']
        breakeven_noi = total_capex * target_cap_rate
        breakeven_effective_income = breakeven_noi + annual_opex
        
        annual_gross_income_at_base = base_monthly_rent * 12 * unit_count
        breakeven_occupancy = (breakeven_effective_income / annual_gross_income_at_base) if annual_gross_income_at_base > 0 else 1.0
        breakeven_occupancy = min(breakeven_occupancy, 1.0)
        
        stabilized_occupancy = self.assumptions['stabilized_occupancy']
        breakeven_monthly_rent = (breakeven_effective_income / (12 * unit_count * stabilized_occupancy)) if stabilized_occupancy > 0 else 0
        
        payback_period = (total_capex / breakeven_noi) if breakeven_noi > 0 else float('inf')
        
        return {
            'breakeven_noi': breakeven_noi,
            'breakeven_occupancy_percent': breakeven_occupancy * 100,
            'breakeven_monthly_rent': breakeven_monthly_rent,
            'base_monthly_rent': base_monthly_rent,
            'rent_gap_percent': ((breakeven_monthly_rent / base_monthly_rent - 1) * 100) if base_monthly_rent > 0 else 0,
            'payback_period_years': payback_period,
            'achievable': breakeven_occupancy <= stabilized_occupancy
        }
    
    def run_sensitivity_analysis(
        self,
        land_area: float,
        address: str,
        unit_type: str,
        construction_type: str = "standard",
        land_appraisal_price: float = None  # 🔥 NEW: 사용자 입력 감정평가액
    ) -> Dict[str, Any]:
        """Run sensitivity analysis with optimistic/base/pessimistic scenarios"""
        logger.info("🔄 Running sensitivity analysis (3 scenarios)")
        
        scenarios = {}
        
        scenarios['base'] = self._run_single_scenario(
            land_area, address, unit_type, construction_type,
            scenario_name="Base Case",
            adjustments={},
            land_appraisal_price=land_appraisal_price
        )
        
        scenarios['optimistic'] = self._run_single_scenario(
            land_area, address, unit_type, construction_type,
            scenario_name="Optimistic (+10%)",
            adjustments={
                'rent_multiplier': 1.10,
                'occupancy_boost': 0.02,
                'cost_reduction': 0.90
            },
            land_appraisal_price=land_appraisal_price
        )
        
        scenarios['pessimistic'] = self._run_single_scenario(
            land_area, address, unit_type, construction_type,
            scenario_name="Pessimistic (-10%)",
            adjustments={
                'rent_multiplier': 0.90,
                'occupancy_reduction': 0.05,
                'cost_increase': 1.10
            },
            land_appraisal_price=land_appraisal_price
        )
        
        base_irr = scenarios['base']['return_metrics'].get('irr_percent', 0)
        opt_irr = scenarios['optimistic']['return_metrics'].get('irr_percent', 0)
        pes_irr = scenarios['pessimistic']['return_metrics'].get('irr_percent', 0)
        
        scenarios['summary'] = {
            'irr_range': {
                'pessimistic': pes_irr,
                'base': base_irr,
                'optimistic': opt_irr,
                'spread': opt_irr - pes_irr
            },
            'sensitivity_variables': [
                {'variable': 'Rental Rate', 'impact': 'High'},
                {'variable': 'Occupancy Rate', 'impact': 'High'},
                {'variable': 'Construction Cost', 'impact': 'Medium'},
                {'variable': 'OpEx Inflation', 'impact': 'Medium'}
            ]
        }
        
        logger.info(f"✅ Sensitivity analysis complete: IRR range {pes_irr:.1f}% - {opt_irr:.1f}%")
        return scenarios
    
    def _determine_land_price_zone(self, address: str) -> str:
        """Determine land price zone from address"""
        address_lower = address.lower()
        
        gangnam_keywords = ['강남', '서초', '송파', 'gangnam', 'seocho', 'songpa']
        if any(kw in address_lower for kw in gangnam_keywords):
            return 'seoul_gangnam'
        
        gangbuk_keywords = ['종로', '중구', '용산', '성동', '광진', '동대문', '중랑', 'jongno', 'jung', 'yongsan']
        if any(kw in address_lower for kw in gangbuk_keywords):
            return 'seoul_gangbuk'
        
        suburban_keywords = ['노원', '도봉', '강북', '은평', '서대문', '마포', '양천', '강서', '구로', '금천', '영등포', '동작', '관악']
        if any(kw in address_lower for kw in suburban_keywords):
            return 'seoul_suburban'
        
        return 'default'
    
    def _calculate_unit_count(self, land_area: float) -> int:
        """Calculate estimated unit count based on land area"""
        units_per_100 = self.assumptions['units_per_100_sqm_land']
        unit_count = int((land_area / 100) * units_per_100)
        return max(unit_count, 1)
    
    def _run_single_scenario(
        self,
        land_area: float,
        address: str,
        unit_type: str,
        construction_type: str,
        scenario_name: str,
        adjustments: Dict[str, float],
        land_appraisal_price: float = None  # 🔥 NEW: 사용자 입력 감정평가액
    ) -> Dict[str, Any]:
        """Run a single scenario with adjustments"""
        original_assumptions = self.assumptions.copy()
        
        if 'cost_reduction' in adjustments:
            for key in self.assumptions['construction_cost_per_sqm']:
                self.assumptions['construction_cost_per_sqm'][key] *= adjustments['cost_reduction']
        elif 'cost_increase' in adjustments:
            for key in self.assumptions['construction_cost_per_sqm']:
                self.assumptions['construction_cost_per_sqm'][key] *= adjustments['cost_increase']
        
        capex_result = self.calculate_capex(land_area, address, construction_type, land_appraisal_price=land_appraisal_price)
        total_capex = capex_result['total_capex']
        unit_count = capex_result['unit_count']
        
        opex_result = self.project_opex(unit_count, total_capex, years=10)
        year1_opex = opex_result['year1_total_opex']
        
        original_rent = self.assumptions['monthly_rent'].get(unit_type, self.assumptions['monthly_rent']['default'])
        if 'rent_multiplier' in adjustments:
            self.assumptions['monthly_rent'][unit_type] = original_rent * adjustments['rent_multiplier']
        
        original_occupancy = self.assumptions['stabilized_occupancy']
        if 'occupancy_boost' in adjustments:
            self.assumptions['stabilized_occupancy'] = min(original_occupancy + adjustments['occupancy_boost'], 1.0)
        elif 'occupancy_reduction' in adjustments:
            self.assumptions['stabilized_occupancy'] = max(original_occupancy - adjustments['occupancy_reduction'], 0.5)
        
        noi_result = self.calculate_noi(
            unit_count, unit_type, year1_opex,
            occupancy_rate=self.assumptions['stabilized_occupancy'],
            year=2
        )
        
        return_metrics = self.calculate_return_metrics(total_capex, noi_result['noi'])
        
        self.assumptions = original_assumptions
        
        return {
            'scenario_name': scenario_name,
            'adjustments': adjustments,
            'capex': capex_result,
            'opex': opex_result,
            'noi': noi_result,
            'return_metrics': return_metrics
        }
    
    def _calculate_irr(self, cash_flows: List[float], guess: float = 0.1) -> float:
        """Calculate Internal Rate of Return using Newton-Raphson method"""
        if not cash_flows or len(cash_flows) < 2:
            return 0.0
        
        rate = guess
        max_iterations = 100
        tolerance = 1e-6
        
        for _ in range(max_iterations):
            npv = sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cash_flows))
            npv_derivative = sum(-i * cf / ((1 + rate) ** (i + 1)) for i, cf in enumerate(cash_flows))
            
            if abs(npv) < tolerance:
                return rate
            
            if npv_derivative == 0:
                break
            
            rate = rate - npv / npv_derivative
        
        return rate if rate > -1 else 0.0
    
    def _calculate_npv(self, cash_flows: List[float], discount_rate: float) -> float:
        """Calculate Net Present Value"""
        if not cash_flows:
            return 0.0
        
        npv = sum(cf / ((1 + discount_rate) ** i) for i, cf in enumerate(cash_flows))
        return npv
    
    def _format_krw(self, amount: float) -> str:
        """Format amount as Korean Won"""
        if amount >= 1_000_000_000_000:
            return f"{amount / 1_000_000_000_000:.1f}조원"
        elif amount >= 100_000_000:
            return f"{amount / 100_000_000:.1f}억원"
        elif amount >= 10_000:
            return f"{amount / 10_000:.0f}만원"
        else:
            return f"{amount:,.0f}원"


def run_full_financial_analysis(
    land_area: float,
    address: str,
    unit_type: str,
    construction_type: str = "standard",
    land_appraisal_price: float = None  # 🔥 NEW: 사용자 입력 감정평가액
) -> Dict[str, Any]:
    """Run complete financial feasibility analysis"""
    engine = FinancialEngine()
    
    capex = engine.calculate_capex(land_area, address, construction_type, land_appraisal_price=land_appraisal_price)
    opex = engine.project_opex(capex['unit_count'], capex['total_capex'])
    noi = engine.calculate_noi(capex['unit_count'], unit_type, opex['year1_total_opex'], year=2)
    returns = engine.calculate_return_metrics(capex['total_capex'], noi['noi'])
    breakeven = engine.calculate_breakeven(
        capex['total_capex'], capex['unit_count'], unit_type, opex['year1_total_opex']
    )
    sensitivity = engine.run_sensitivity_analysis(land_area, address, unit_type, construction_type, land_appraisal_price=land_appraisal_price)
    
    return {
        'capex': capex,
        'opex': opex,
        'noi': noi,
        'returns': returns,
        'breakeven': breakeven,
        'sensitivity': sensitivity,
        'summary': {
            'total_investment': capex['total_capex'],
            'unit_count': capex['unit_count'],
            'noi_stabilized': noi['noi'],
            'cap_rate': returns['cap_rate_percent'],
            'meets_lh_criteria': returns['meets_lh_target'],
            'irr_range': sensitivity['summary']['irr_range']
        }
    }
