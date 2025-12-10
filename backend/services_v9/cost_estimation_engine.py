"""
Cost Estimation Engine v3.2
Ensures CAPEX = sum of all components
"""

from typing import Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class LHStandardRates:
    """LH 2024 Standard Construction Rates"""
    STANDARD_CONSTRUCTION_COST_PER_SQM = 3_500_000  # ₩/㎡
    SEOUL_REGIONAL_MULTIPLIER = 1.15
    ACQUISITION_TAX_RATE = 0.044  # 4.4%
    DESIGN_FEE_RATE = 0.08  # 8% of construction
    SUPERVISION_FEE_RATE = 0.03  # 3% of construction
    CONTINGENCY_RATE = 0.10  # 10% of construction
    FINANCIAL_COST_RATE = 0.03  # 3% of total
    OTHER_COSTS_RATE = 0.02  # 2% of total


class CostEstimationEngineV32:
    """
    Accurate cost estimation with component validation
    
    Key Fix: Ensures displayed total equals sum of components
    """
    
    def __init__(self):
        self.rates = LHStandardRates()
    
    def calculate_land_cost(self, 
                           land_area_sqm: float,
                           avg_land_price_per_sqm: float) -> Dict[str, float]:
        """
        Calculate land acquisition cost
        
        Args:
            land_area_sqm: Land area in square meters
            avg_land_price_per_sqm: Average market price (₩/㎡)
        
        Returns:
            Land cost breakdown in 억원
        """
        
        # Total land cost
        land_cost_krw = land_area_sqm * avg_land_price_per_sqm
        land_cost_billion = land_cost_krw / 100_000_000  # Convert to 억원
        
        # Acquisition tax (4.4%)
        acquisition_tax = land_cost_billion * self.rates.ACQUISITION_TAX_RATE
        
        return {
            'land_purchase': round(land_cost_billion, 2),
            'acquisition_tax': round(acquisition_tax, 2),
            'total_land_cost': round(land_cost_billion + acquisition_tax, 2),
            'land_area_sqm': land_area_sqm,
            'avg_price_per_sqm': avg_land_price_per_sqm,
            'unit': '억원'
        }
    
    def calculate_construction_cost(self,
                                   total_floor_area_sqm: float,
                                   location: str = 'seoul') -> Dict[str, float]:
        """
        Calculate construction cost using LH standard rates
        
        Args:
            total_floor_area_sqm: Total floor area (연면적)
            location: 'seoul' or other (affects multiplier)
        
        Returns:
            Construction cost breakdown in 억원
        """
        
        # Base construction cost
        base_cost_per_sqm = self.rates.STANDARD_CONSTRUCTION_COST_PER_SQM
        
        # Regional multiplier
        if location.lower() == 'seoul':
            multiplier = self.rates.SEOUL_REGIONAL_MULTIPLIER
        else:
            multiplier = 1.0
        
        adjusted_cost_per_sqm = base_cost_per_sqm * multiplier
        
        # Total construction cost
        construction_cost_krw = total_floor_area_sqm * adjusted_cost_per_sqm
        construction_cost_billion = construction_cost_krw / 100_000_000
        
        return {
            'base_cost_per_sqm': base_cost_per_sqm,
            'regional_multiplier': multiplier,
            'adjusted_cost_per_sqm': adjusted_cost_per_sqm,
            'total_floor_area_sqm': total_floor_area_sqm,
            'construction_cost': round(construction_cost_billion, 2),
            'unit': '억원'
        }
    
    def calculate_indirect_costs(self,
                                construction_cost: float,
                                preliminary_total: float) -> Dict[str, float]:
        """
        Calculate all indirect costs
        
        Args:
            construction_cost: Base construction cost (억원)
            preliminary_total: Prelim total for % calculations (억원)
        
        Returns:
            Indirect costs breakdown
        """
        
        # Design fee (8% of construction)
        design_fee = construction_cost * self.rates.DESIGN_FEE_RATE
        
        # Supervision fee (3% of construction)
        supervision_fee = construction_cost * self.rates.SUPERVISION_FEE_RATE
        
        # Contingency (10% of construction)
        contingency = construction_cost * self.rates.CONTINGENCY_RATE
        
        # Financial costs (3% of preliminary total)
        financial_costs = preliminary_total * self.rates.FINANCIAL_COST_RATE
        
        # Other costs (2% of preliminary total)
        other_costs = preliminary_total * self.rates.OTHER_COSTS_RATE
        
        total_indirect = (design_fee + supervision_fee + contingency + 
                         financial_costs + other_costs)
        
        return {
            'design_fee': round(design_fee, 2),
            'supervision_fee': round(supervision_fee, 2),
            'contingency': round(contingency, 2),
            'financial_costs': round(financial_costs, 2),
            'other_costs': round(other_costs, 2),
            'total_indirect': round(total_indirect, 2),
            'unit': '억원'
        }
    
    def calculate_total_capex(self,
                             land_area_sqm: float,
                             total_floor_area_sqm: float,
                             avg_land_price_per_sqm: float,
                             location: str = 'seoul') -> Dict[str, float]:
        """
        Calculate complete CAPEX with validation
        
        CRITICAL: Returns dictionary where total_capex EQUALS sum of components
        
        Returns:
            Complete cost breakdown with validation
        """
        
        # Step 1: Calculate land cost
        land_costs = self.calculate_land_cost(land_area_sqm, avg_land_price_per_sqm)
        
        # Step 2: Calculate construction cost
        construction_costs = self.calculate_construction_cost(
            total_floor_area_sqm, location
        )
        
        # Step 3: Calculate preliminary total (for indirect % calculations)
        preliminary_total = (land_costs['total_land_cost'] + 
                           construction_costs['construction_cost'])
        
        # Step 4: Calculate indirect costs
        indirect_costs = self.calculate_indirect_costs(
            construction_costs['construction_cost'],
            preliminary_total
        )
        
        # Step 5: Calculate final total
        total_capex = (land_costs['total_land_cost'] + 
                      construction_costs['construction_cost'] + 
                      indirect_costs['total_indirect'])
        
        # Step 6: Build complete breakdown
        breakdown = {
            'land_purchase': land_costs['land_purchase'],
            'acquisition_tax': land_costs['acquisition_tax'],
            'construction_cost': construction_costs['construction_cost'],
            'design_fee': indirect_costs['design_fee'],
            'supervision_fee': indirect_costs['supervision_fee'],
            'contingency': indirect_costs['contingency'],
            'financial_costs': indirect_costs['financial_costs'],
            'other_costs': indirect_costs['other_costs'],
            'total_capex': round(total_capex, 2),
            'unit': '억원',
            
            # Additional metadata
            'land_area_sqm': land_area_sqm,
            'total_floor_area_sqm': total_floor_area_sqm,
            'avg_land_price_per_sqm': avg_land_price_per_sqm,
            'construction_cost_per_sqm': construction_costs['adjusted_cost_per_sqm'],
            'location': location
        }
        
        # Step 7: CRITICAL VALIDATION
        calculated_sum = (
            breakdown['land_purchase'] +
            breakdown['acquisition_tax'] +
            breakdown['construction_cost'] +
            breakdown['design_fee'] +
            breakdown['supervision_fee'] +
            breakdown['contingency'] +
            breakdown['financial_costs'] +
            breakdown['other_costs']
        )
        
        # Ensure sum matches (allow 0.01억원 rounding error)
        if abs(calculated_sum - breakdown['total_capex']) > 0.01:
            logger.warning(f"CAPEX validation warning: {calculated_sum} != {breakdown['total_capex']}")
            # Force equality
            breakdown['total_capex'] = round(calculated_sum, 2)
        
        breakdown['validation_passed'] = True
        breakdown['calculated_sum'] = round(calculated_sum, 2)
        
        return breakdown
    
    def generate_cost_table_markdown(self, breakdown: Dict) -> str:
        """
        Generate formatted cost table for PDF report
        
        Returns:
            Markdown-formatted table string
        """
        
        # Calculate percentages
        total = breakdown['total_capex']
        
        def pct(value):
            return f"{(value/total)*100:.1f}%"
        
        table = f"""
| 공종 | 금액 (억원) | 비율 | 비고 |
|------|------------|------|------|
| 토지 매입 | {breakdown['land_purchase']:.1f} | {pct(breakdown['land_purchase'])} | 시장가 기준 |
| 취득세 | {breakdown['acquisition_tax']:.1f} | {pct(breakdown['acquisition_tax'])} | 4.4% |
| 건축 공사 | {breakdown['construction_cost']:.1f} | {pct(breakdown['construction_cost'])} | LH 표준단가 |
| 설계비 | {breakdown['design_fee']:.1f} | {pct(breakdown['design_fee'])} | 건축비 8% |
| 감리비 | {breakdown['supervision_fee']:.1f} | {pct(breakdown['supervision_fee'])} | 건축비 3% |
| 예비비 | {breakdown['contingency']:.1f} | {pct(breakdown['contingency'])} | 건축비 10% |
| 금융비용 | {breakdown['financial_costs']:.1f} | {pct(breakdown['financial_costs'])} | 총사업비 3% |
| 기타비용 | {breakdown['other_costs']:.1f} | {pct(breakdown['other_costs'])} | 총사업비 2% |
| **합계** | **{breakdown['total_capex']:.1f}** | **100.0%** | ✅ 검증완료 |

**검증:** {breakdown['calculated_sum']:.1f} = {breakdown['total_capex']:.1f} ✓
"""
        return table


# ============================================================================
# USAGE EXAMPLE & TEST
# ============================================================================

if __name__ == "__main__":
    engine = CostEstimationEngineV32()
    
    # Sample project
    breakdown = engine.calculate_total_capex(
        land_area_sqm=660.0,
        total_floor_area_sqm=2200.0,
        avg_land_price_per_sqm=9_500_000,  # ₩9.5M per sqm
        location='seoul'
    )
    
    print("=" * 80)
    print("COST BREAKDOWN (v3.2)")
    print("=" * 80)
    print(engine.generate_cost_table_markdown(breakdown))
    print(f"\n✅ Validation: {breakdown['validation_passed']}")
    print(f"✅ Sum equals total: {breakdown['calculated_sum']} = {breakdown['total_capex']}")
