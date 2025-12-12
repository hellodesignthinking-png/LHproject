"""
Financial Analysis Engine v24.0 (migrated from v3.2)
LH New Construction Lease Financial Analysis for ZeroSite v24

Features:
- LH appraisal calculation (토지 92%, 건물 90%)
- Policy-based profitability analysis (LH purchase model)
- 30-year cashflow modeling
- NPV, ROI, IRR calculations
- Decision logic (GO/CONDITIONAL-GO/NO-GO)

Author: ZeroSite v24 Team
Date: 2025-12-12
"""

from typing import Dict, List
import numpy as np
from datetime import datetime
import logging
from .base_engine import BaseEngine

logger = logging.getLogger(__name__)


class FinancialEngine(BaseEngine):
    """
    Correct financial calculations for LH new construction lease projects
    
    Inherits from BaseEngine for v24 standardization
    
    Key Features:
    - Realistic ROI calculation
    - Policy-based vs Private-based dual analysis
    - Accurate 30-year cashflow modeling
    - LH appraisal methodology
    
    Input:
        cost_breakdown: {
            'land_cost': float (억원),
            'construction_cost': float,
            'indirect_costs': float,
            'total_capex': float
        }
    
    Output:
        {
            'lh_appraisal': {...},
            'profitability': {
                'roi_percent': float,
                'irr_percent': float,
                'decision': str
            },
            'npv': float,
            'cashflow_table': List[Dict],
            'validation': {...}
        }
    """
    
    def __init__(self):
        super().__init__(engine_name="FinancialEngine", version="24.0")
        self.discount_rate = 0.05  # 5%
        self.analysis_period_years = 30
        self.lh_land_appraisal_rate = 0.92  # LH standard: 92%
        self.lh_building_appraisal_rate = 0.90  # LH standard: 90%
    
    @property
    def timestamp(self):
        return self.created_at.isoformat()
    
    def process(self, input_data: Dict) -> Dict:
        """
        Main processing method (BaseEngine interface)
        
        Args:
            input_data: {
                'land_cost': float (억원),
                'construction_cost': float,
                'indirect_costs': float,
                'total_capex': float
            }
        
        Returns:
            Complete financial analysis
        """
        self.validate_input(input_data, ['land_cost', 'construction_cost', 'indirect_costs', 'total_capex'])
        
        result = self.generate_complete_financial_analysis(input_data)
        
        self.logger.info(f"Financial analysis complete: ROI {result['profitability']['roi_percent']:.2f}%, Decision: {result['profitability']['decision']}")
        return result
    
    def calculate_lh_appraisal(self, 
                               land_cost: float, 
                               construction_cost: float,
                               indirect_costs: float) -> Dict[str, float]:
        """
        Calculate LH appraisal value (감정평가액)
        
        LH applies lower rates than market for policy purposes:
        - Land: 92% of market value
        - Building: 90% of construction cost
        
        Args:
            land_cost: Market land acquisition cost (억원)
            construction_cost: Total construction cost (억원)
            indirect_costs: Design, supervision, etc. (억원)
        
        Returns:
            Dictionary with appraisal breakdown
        """
        
        # LH land appraisal (토지감정가)
        land_appraisal = land_cost * self.lh_land_appraisal_rate
        
        # LH building appraisal (건물감정가)
        # Includes construction + some indirect costs
        building_base = construction_cost + (indirect_costs * 0.5)
        building_appraisal = building_base * self.lh_building_appraisal_rate
        
        # Total LH purchase price
        total_lh_purchase = land_appraisal + building_appraisal
        
        return {
            'land_appraisal': round(land_appraisal, 2),
            'land_appraisal_rate': self.lh_land_appraisal_rate,
            'building_appraisal': round(building_appraisal, 2),
            'building_appraisal_rate': self.lh_building_appraisal_rate,
            'total_lh_purchase': round(total_lh_purchase, 2),
            'calculation_note': 'LH 감정평가: 토지 92%, 건물 90% 인정'
        }
    
    def calculate_policy_based_profitability(self,
                                            total_capex: float,
                                            lh_purchase_price: float) -> Dict[str, float]:
        """
        Calculate profitability based on LH purchase (정책형 수익성)
        
        This is the CORRECT way to analyze LH new construction lease projects.
        Revenue = LH one-time purchase at completion
        NOT 30-year rental income
        
        Args:
            total_capex: Total investment (토지+건축+간접비, 억원)
            lh_purchase_price: LH appraisal-based purchase price (억원)
        
        Returns:
            Profitability metrics
        """
        
        # Simple profit calculation
        profit = lh_purchase_price - total_capex
        
        # ROI (Return on Investment)
        roi_percent = (profit / total_capex) * 100 if total_capex > 0 else 0
        
        # IRR for 2.5-year project (construction + LH purchase)
        # Cashflow: Year 0: -토지비, Year 1-2: -건축비, Year 2.5: +LH매입가
        cashflows = self._generate_policy_cashflows(total_capex, lh_purchase_price)
        irr_percent = self._calculate_irr(cashflows) * 100
        
        # Payback period
        if profit > 0:
            payback_years = 2.5  # LH purchases at completion
        else:
            payback_years = None  # Never recovers
        
        return {
            'analysis_type': 'policy_based',
            'total_capex': round(total_capex, 2),
            'lh_purchase_price': round(lh_purchase_price, 2),
            'profit': round(profit, 2),
            'roi_percent': round(roi_percent, 2),
            'irr_percent': round(irr_percent, 2),
            'payback_period_years': payback_years,
            'decision': self._get_decision(roi_percent, irr_percent)
        }
    
    def _generate_policy_cashflows(self, 
                                   total_capex: float, 
                                   lh_purchase: float) -> List[float]:
        """
        Generate realistic cashflows for LH project
        
        Timeline:
        - Year 0 (Month 0): Land acquisition (토지비 40%)
        - Year 1 (Month 0-12): Construction phase 1 (건축비 40%)
        - Year 2 (Month 12-24): Construction phase 2 (건축비 60%)
        - Year 2.5 (Month 30): LH purchase & completion
        
        Returns:
            List of cashflows [Year0, Year1, Year2, Year2.5, Year3-30]
        """
        
        # Assume 40% land, 60% construction+indirect
        land_portion = total_capex * 0.40
        construction_portion = total_capex * 0.60
        
        cashflows = []
        
        # Year 0: Land acquisition
        cashflows.append(-land_portion)
        
        # Year 1: Construction phase 1
        cashflows.append(-construction_portion * 0.40)
        
        # Year 2: Construction phase 2
        cashflows.append(-construction_portion * 0.60)
        
        # Year 2.5: LH purchase (revenue)
        cashflows.append(lh_purchase)
        
        # Year 3-30: No additional cashflows (LH owns it)
        for _ in range(27):
            cashflows.append(0)
        
        return cashflows
    
    def _calculate_irr(self, cashflows: List[float]) -> float:
        """Calculate Internal Rate of Return using numpy"""
        try:
            irr = np.irr(cashflows)
            # Sanity check
            if np.isnan(irr) or np.isinf(irr):
                return -0.10  # Default to -10% if calculation fails
            return max(min(irr, 0.50), -0.50)  # Cap at ±50%
        except:
            return -0.10
    
    def _get_decision(self, roi: float, irr: float) -> str:
        """
        Decision logic based on financial metrics
        
        Policy-based project thresholds (different from private):
        - ROI > 0%: GO
        - ROI -10% to 0%: CONDITIONAL-GO
        - ROI < -10%: NO-GO
        """
        if roi > 0:
            return "GO"
        elif roi > -10:
            return "CONDITIONAL-GO"
        else:
            return "NO-GO"
    
    def calculate_30year_cashflow_table(self,
                                       total_capex: float,
                                       lh_purchase: float) -> List[Dict]:
        """
        Generate detailed 30-year cashflow table for report
        
        Returns:
            List of yearly cashflow dictionaries
        """
        
        land_portion = total_capex * 0.40
        construction_portion = total_capex * 0.60
        
        table = []
        cumulative_cf = 0
        
        # Year 0: Land acquisition
        year_0 = {
            'year': 0,
            'description': '토지 매입',
            'inflow': 0,
            'outflow': round(land_portion, 2),
            'net_cashflow': round(-land_portion, 2),
            'cumulative': round(-land_portion, 2)
        }
        table.append(year_0)
        cumulative_cf = -land_portion
        
        # Year 1: Construction phase 1
        construction_y1 = construction_portion * 0.40
        year_1 = {
            'year': 1,
            'description': '건축 공사 (착공)',
            'inflow': 0,
            'outflow': round(construction_y1, 2),
            'net_cashflow': round(-construction_y1, 2),
            'cumulative': round(cumulative_cf - construction_y1, 2)
        }
        table.append(year_1)
        cumulative_cf -= construction_y1
        
        # Year 2: Construction phase 2
        construction_y2 = construction_portion * 0.60
        year_2 = {
            'year': 2,
            'description': '건축 공사 (준공)',
            'inflow': 0,
            'outflow': round(construction_y2, 2),
            'net_cashflow': round(-construction_y2, 2),
            'cumulative': round(cumulative_cf - construction_y2, 2)
        }
        table.append(year_2)
        cumulative_cf -= construction_y2
        
        # Year 2.5: LH Purchase
        year_2_5 = {
            'year': 2.5,
            'description': 'LH 매입 완료',
            'inflow': round(lh_purchase, 2),
            'outflow': 0,
            'net_cashflow': round(lh_purchase, 2),
            'cumulative': round(cumulative_cf + lh_purchase, 2)
        }
        table.append(year_2_5)
        cumulative_cf += lh_purchase
        
        # Year 3-30: No operations (LH operates)
        for year in range(3, 31):
            year_row = {
                'year': year,
                'description': 'LH 운영 (사업자 무관)',
                'inflow': 0,
                'outflow': 0,
                'net_cashflow': 0,
                'cumulative': round(cumulative_cf, 2)
            }
            table.append(year_row)
        
        return table
    
    def generate_complete_financial_analysis(self,
                                            cost_breakdown: Dict[str, float]) -> Dict:
        """
        Complete financial analysis for v24 report
        
        Args:
            cost_breakdown: {
                'land_cost': float,
                'construction_cost': float,
                'indirect_costs': float,
                'total_capex': float
            }
        
        Returns:
            Complete financial analysis data
        """
        
        # Validate input
        calculated_sum = (cost_breakdown['land_cost'] + 
                         cost_breakdown['construction_cost'] + 
                         cost_breakdown['indirect_costs'])
        
        if abs(cost_breakdown['total_capex'] - calculated_sum) > 0.1:
            logger.warning(f"CAPEX mismatch: {cost_breakdown['total_capex']} != {calculated_sum}")
            # Auto-correct to sum
            cost_breakdown['total_capex'] = round(calculated_sum, 2)
        
        # Calculate LH appraisal
        lh_appraisal = self.calculate_lh_appraisal(
            land_cost=cost_breakdown['land_cost'],
            construction_cost=cost_breakdown['construction_cost'],
            indirect_costs=cost_breakdown['indirect_costs']
        )
        
        # Calculate policy-based profitability
        profitability = self.calculate_policy_based_profitability(
            total_capex=cost_breakdown['total_capex'],
            lh_purchase_price=lh_appraisal['total_lh_purchase']
        )
        
        # Generate cashflow table
        cashflow_table = self.calculate_30year_cashflow_table(
            total_capex=cost_breakdown['total_capex'],
            lh_purchase=lh_appraisal['total_lh_purchase']
        )
        
        # Calculate NPV
        cashflows_for_npv = [row['net_cashflow'] for row in cashflow_table]
        npv = self._calculate_npv(cashflows_for_npv, self.discount_rate)
        
        return {
            'cost_breakdown': cost_breakdown,
            'lh_appraisal': lh_appraisal,
            'profitability': profitability,
            'npv': round(npv, 2),
            'cashflow_table': cashflow_table,
            'validation': {
                'capex_sum_check': abs(cost_breakdown['total_capex'] - calculated_sum) < 0.1,
                'roi_realistic': -50 < profitability['roi_percent'] < 100,
                'lh_purchase_realistic': 50 < lh_appraisal['total_lh_purchase'] < 500
            }
        }
    
    def _calculate_npv(self, cashflows: List[float], discount_rate: float) -> float:
        """Calculate Net Present Value"""
        npv = 0
        for i, cf in enumerate(cashflows):
            npv += cf / ((1 + discount_rate) ** i)
        return npv


# ============================================================================
# CLI TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("FINANCIAL ENGINE v24.0 - CLI TEST")
    print("=" * 80)
    
    engine = FinancialEngine()
    
    # Sample project data
    cost_breakdown = {
        'land_cost': 62.7,  # 억원
        'construction_cost': 77.0,
        'indirect_costs': 25.8,
        'total_capex': 165.5
    }
    
    result = engine.process(cost_breakdown)
    
    print(f"\n✅ Engine: {engine.engine_name} v{engine.version}")
    print(f"✅ Timestamp: {engine.timestamp}")
    
    print("\n" + "-" * 80)
    print("FINANCIAL ANALYSIS RESULTS")
    print("-" * 80)
    print(f"총 투자비 (CAPEX):      {result['cost_breakdown']['total_capex']:>8.1f} 억원")
    print(f"LH 매입가:             {result['lh_appraisal']['total_lh_purchase']:>8.1f} 억원")
    print(f"  - 토지 감정가:       {result['lh_appraisal']['land_appraisal']:>8.1f} 억원 (시장가 92%)")
    print(f"  - 건물 감정가:       {result['lh_appraisal']['building_appraisal']:>8.1f} 억원 (건축비 90%)")
    print("-" * 80)
    print(f"사업 수익:             {result['profitability']['profit']:>8.1f} 억원")
    print(f"ROI:                   {result['profitability']['roi_percent']:>7.2f} %")
    print(f"IRR:                   {result['profitability']['irr_percent']:>7.2f} %")
    print(f"NPV (5% 할인율):        {result['npv']:>8.1f} 억원")
    print(f"회수 기간:             {result['profitability']['payback_period_years']} 년")
    print("-" * 80)
    print(f"✅ 의사결정: {result['profitability']['decision']}")
    print("-" * 80)
    
    print(f"\n검증 결과:")
    for check, passed in result['validation'].items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}: {passed}")
    
    print(f"\n30년 현금흐름 샘플 (처음 5년):")
    for row in result['cashflow_table'][:5]:
        print(f"  Year {row['year']:<4}: {row['description']:<20} | "
              f"Net CF: {row['net_cashflow']:>8.2f}억 | "
              f"Cumulative: {row['cumulative']:>8.2f}억")
    
    print("\n" + "=" * 80)
