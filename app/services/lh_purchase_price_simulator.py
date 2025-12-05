"""
ZeroSite v7.5 LH Purchase Price Simulator
Simulates LH (Korea Land & Housing Corporation) acquisition price models

Purpose:
- Model LH's standardized purchase price calculation
- Analyze profitability gap between market value and LH price
- Provide strategic recommendations for price negotiation

LH Purchase Price Model:
- Based on construction cost + land value + reasonable profit margin
- Capped by LH's internal valuation standards
- Subject to public housing policy constraints
- Typically 85-95% of market value

Key Outputs:
- Standard LH acquisition price estimate
- Market value comparison
- Profitability gap analysis
- Strategic recommendation (GO/NEGOTIATE/NO-GO)
"""

from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class LHPurchasePriceSimulator:
    """
    LH (Korea Land & Housing Corporation) Purchase Price Simulation Engine
    
    Simulates LH's standardized acquisition pricing for new-build rental housing
    """
    
    # LH pricing policy parameters (2025 standards)
    LH_PARAMETERS = {
        'land_acquisition_cap': 0.90,  # LH pays up to 90% of assessed land value
        'construction_markup': 1.08,    # 8% markup on construction costs
        'developer_profit_margin': 0.05,  # 5% developer profit cap
        'appraisal_discount': 0.92,     # LH uses 92% of market appraisal
        'typical_purchase_ratio': 0.88,  # LH typically pays 88% of market value
        
        # Price per unit caps (KRW, varies by unit type)
        'price_caps': {
            '청년': 120_000_000,      # 120M KRW per youth unit
            '신혼부부 I': 150_000_000,  # 150M KRW per newlywed I unit
            '신혼부부 II': 180_000_000, # 180M KRW per newlywed II unit
            '다자녀': 200_000_000,     # 200M KRW per multi-child family unit
            'default': 150_000_000      # 150M KRW default
        },
        
        # LH quality/location premiums
        'location_premiums': {
            'gangnam': 1.15,  # 15% premium for Gangnam
            'gangbuk': 1.05,  # 5% premium for central Gangbuk
            'gangbuk_west': 1.03,  # 3% premium for western Gangbuk
            'gangbuk_south': 1.00,  # No premium for southern areas
            'default': 1.00
        }
    }
    
    def __init__(self):
        logger.info("💰 LH Purchase Price Simulator v7.5 initialized")
    
    def simulate_lh_purchase_price(
        self,
        financial_analysis: Dict[str, Any],
        basic_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main simulation: Calculate LH's expected acquisition price
        
        Args:
            financial_analysis: Financial feasibility results from v7.4 engine
            basic_info: Basic project information
            
        Returns:
            Dict containing:
                - lh_purchase_price: Estimated LH acquisition price
                - market_value: Estimated market value
                - gap_amount: Price gap (market - LH)
                - gap_percentage: Gap as % of market value
                - profitability_score: Score (0-100)
                - recommendation: GO/NEGOTIATE/REVISE/NO-GO
                - explanation: Detailed reasoning
        """
        address = basic_info.get('address', '')
        unit_type = basic_info.get('unit_type', 'default')
        land_area = basic_info.get('land_area', 0)
        
        # Extract financial metrics
        fin_summary = financial_analysis.get('summary', {})
        total_capex = fin_summary.get('total_investment', 0)
        unit_count = fin_summary.get('unit_count', 0)
        cap_rate = fin_summary.get('cap_rate', 0)
        
        # Calculate LH purchase price
        lh_price, lh_breakdown = self._calculate_lh_price(
            total_capex, unit_count, unit_type, address
        )
        
        # Estimate market value
        market_value = self._estimate_market_value(
            total_capex, unit_count, address
        )
        
        # Calculate gap
        gap_amount = market_value - lh_price
        gap_percentage = (gap_amount / market_value * 100) if market_value > 0 else 0
        
        # Calculate profitability score
        profitability_score = self._calculate_profitability_score(
            gap_percentage, cap_rate
        )
        
        # Generate recommendation
        recommendation, explanation = self._generate_recommendation(
            gap_percentage, profitability_score, cap_rate, unit_count
        )
        
        result = {
            'lh_purchase_price': lh_price,
            'lh_price_breakdown': lh_breakdown,
            'market_value': market_value,
            'gap_amount': gap_amount,
            'gap_percentage': gap_percentage,
            'profitability_score': profitability_score,
            'recommendation': recommendation,
            'explanation': explanation,
            'metadata': {
                'unit_count': unit_count,
                'price_per_unit_lh': lh_price / unit_count if unit_count > 0 else 0,
                'price_per_unit_market': market_value / unit_count if unit_count > 0 else 0,
                'lh_price_cap': self.LH_PARAMETERS['price_caps'].get(unit_type, 150_000_000)
            }
        }
        
        logger.info(f"✅ LH Price Simulation complete: {lh_price:,.0f} KRW (Gap: {gap_percentage:.1f}%)")
        return result
    
    def _calculate_lh_price(
        self,
        total_capex: float,
        unit_count: int,
        unit_type: str,
        address: str
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate LH's standardized purchase price
        
        Returns:
            (lh_price, breakdown_dict)
        """
        # Base calculation: CapEx + markup
        base_price = total_capex * self.LH_PARAMETERS['construction_markup']
        
        # Apply location premium
        location_key = self._get_location_category(address)
        location_premium = self.LH_PARAMETERS['location_premiums'].get(location_key, 1.0)
        adjusted_price = base_price * location_premium
        
        # Apply LH's typical discount
        lh_price = adjusted_price * self.LH_PARAMETERS['appraisal_discount']
        
        # Check against per-unit cap
        price_per_unit = lh_price / unit_count if unit_count > 0 else 0
        price_cap = self.LH_PARAMETERS['price_caps'].get(unit_type, 150_000_000)
        
        if price_per_unit > price_cap:
            # Apply cap
            lh_price_capped = price_cap * unit_count
            capped = True
        else:
            lh_price_capped = lh_price
            capped = False
        
        breakdown = {
            'base_capex': total_capex,
            'construction_markup': total_capex * (self.LH_PARAMETERS['construction_markup'] - 1),
            'location_premium_amount': adjusted_price - base_price,
            'lh_discount_amount': adjusted_price - lh_price,
            'final_lh_price': lh_price_capped,
            'capped': capped,
            'cap_applied': price_cap if capped else None
        }
        
        return lh_price_capped, breakdown
    
    def _estimate_market_value(
        self,
        total_capex: float,
        unit_count: int,
        address: str
    ) -> float:
        """
        Estimate market value (what a private buyer would pay)
        
        Returns:
            Estimated market value in KRW
        """
        # Market value typically includes higher profit margins
        developer_profit_market = 0.12  # 12% profit margin for private market
        
        market_value = total_capex * (1 + developer_profit_market)
        
        # Adjust for location
        location_key = self._get_location_category(address)
        location_factor = {
            'gangnam': 1.20,
            'gangbuk': 1.10,
            'gangbuk_west': 1.05,
            'gangbuk_south': 1.00
        }.get(location_key, 1.00)
        
        market_value *= location_factor
        
        return market_value
    
    def _calculate_profitability_score(
        self,
        gap_percentage: float,
        cap_rate: float
    ) -> int:
        """
        Calculate profitability score (0-100)
        
        Args:
            gap_percentage: Price gap as % (lower is better)
            cap_rate: Capitalization rate (higher is better)
            
        Returns:
            Score from 0 (worst) to 100 (best)
        """
        # Gap score: Lower gap = higher score
        # 0% gap = 100 points, 20%+ gap = 0 points
        gap_score = max(0, 100 - (gap_percentage * 5))
        
        # Cap rate score: Higher cap rate = higher score
        # 6% cap rate = 100 points, 3% = 0 points, LH target is 4.5%
        cap_rate_score = min(100, max(0, (cap_rate - 3.0) * 33.33))
        
        # Weighted average (60% gap, 40% cap rate)
        total_score = int(gap_score * 0.60 + cap_rate_score * 0.40)
        
        return total_score
    
    def _generate_recommendation(
        self,
        gap_percentage: float,
        profitability_score: int,
        cap_rate: float,
        unit_count: int
    ) -> Tuple[str, str]:
        """
        Generate strategic recommendation
        
        Returns:
            (recommendation_code, explanation_text)
        """
        # Decision matrix
        if gap_percentage <= 8.0 and cap_rate >= 4.5:
            recommendation = "GO"
            explanation = (
                f"<strong>✅ 매입 추천 (GO)</strong><br/>"
                f"LH 매입가와 시장가치 간 Gap이 {gap_percentage:.1f}%로 매우 낮으며, "
                f"Cap Rate {cap_rate:.2f}%가 LH 목표 기준(4.5%)을 충족합니다. "
                f"수익성 점수 {profitability_score}/100으로 우수한 사업성을 나타냅니다. "
                f"<br/><strong>권고사항</strong>: 즉시 사업 추진 가능. "
                f"LH와의 매입 협의 진행을 권장합니다."
            )
        
        elif gap_percentage <= 12.0 and cap_rate >= 4.0:
            recommendation = "CONDITIONAL"
            explanation = (
                f"<strong>⚠️ 조건부 승인 (CONDITIONAL)</strong><br/>"
                f"LH 매입가 Gap {gap_percentage:.1f}% 및 Cap Rate {cap_rate:.2f}%는 "
                f"수용 가능한 수준이나 개선 여지가 있습니다. "
                f"수익성 점수 {profitability_score}/100. "
                f"<br/><strong>권고사항</strong>: "
                f"(1) 건축비 5-10% 절감을 통한 Gap 축소, "
                f"(2) 설계 최적화를 통한 세대수 증가({unit_count}세대 → {int(unit_count * 1.08)}세대), "
                f"(3) LH와 가격 협상 후 재평가 필요."
            )
        
        elif gap_percentage <= 15.0 or cap_rate >= 3.5:
            recommendation = "REVISE"
            explanation = (
                f"<strong>🔄 설계 재검토 필요 (REVISE)</strong><br/>"
                f"LH 매입가 Gap {gap_percentage:.1f}% 또는 Cap Rate {cap_rate:.2f}%가 "
                f"목표 기준에 미달합니다. 수익성 점수 {profitability_score}/100. "
                f"<br/><strong>권고사항</strong>: "
                f"(1) 전면적인 설계 재검토 (건축비 15% 절감 목표), "
                f"(2) 토지 매입가 재협상, "
                f"(3) 대안 입지 탐색 및 비교 분석, "
                f"(4) 수익성 개선 후 재평가 필수."
            )
        
        else:
            recommendation = "NO-GO"
            explanation = (
                f"<strong>❌ 매입 비추천 (NO-GO)</strong><br/>"
                f"LH 매입가 Gap {gap_percentage:.1f}% 및 Cap Rate {cap_rate:.2f}%가 "
                f"사업성 최소 기준에 미달합니다. 수익성 점수 {profitability_score}/100으로 불량. "
                f"<br/><strong>권고사항</strong>: "
                f"(1) 현재 조건에서는 사업 추진 불가, "
                f"(2) 대안 입지 탐색 필수, "
                f"(3) 토지 매입가가 20% 이상 하락하지 않는 한 재검토 불필요."
            )
        
        return recommendation, explanation
    
    def _get_location_category(self, address: str) -> str:
        """
        Categorize location for premium calculation
        
        Returns:
            Location category key
        """
        if any(gu in address for gu in ['강남구', '서초구', '송파구', '강동구']):
            return 'gangnam'
        elif any(gu in address for gu in ['종로구', '중구', '용산구', '성동구', '광진구']):
            return 'gangbuk'
        elif any(gu in address for gu in ['은평구', '서대문구', '마포구']):
            return 'gangbuk_west'
        elif any(gu in address for gu in ['영등포구', '동작구', '관악구', '금천구', '구로구', '양천구', '강서구']):
            return 'gangbuk_south'
        else:
            return 'default'
    
    def format_currency(self, amount: float) -> str:
        """Format currency in Korean style"""
        if amount >= 100_000_000:  # 억 (hundred million)
            eok = amount / 100_000_000
            return f"{eok:.1f}억원"
        elif amount >= 10_000:  # 만 (ten thousand)
            man = amount / 10_000
            return f"{man:,.0f}만원"
        else:
            return f"{amount:,.0f}원"
    
    def generate_detailed_table(self, simulation_result: Dict[str, Any]) -> str:
        """
        Generate detailed HTML table for report
        
        Args:
            simulation_result: Output from simulate_lh_purchase_price()
            
        Returns:
            HTML table string
        """
        lh_price = simulation_result['lh_purchase_price']
        market_value = simulation_result['market_value']
        gap_amount = simulation_result['gap_amount']
        gap_pct = simulation_result['gap_percentage']
        score = simulation_result['profitability_score']
        recommendation = simulation_result['recommendation']
        
        metadata = simulation_result['metadata']
        unit_count = metadata['unit_count']
        price_per_unit_lh = metadata['price_per_unit_lh']
        price_per_unit_market = metadata['price_per_unit_market']
        
        # Color coding for recommendation
        rec_colors = {
            'GO': '#28a745',
            'CONDITIONAL': '#ffc107',
            'REVISE': '#fd7e14',
            'NO-GO': '#dc3545'
        }
        rec_color = rec_colors.get(recommendation, '#6c757d')
        
        table_html = f"""
        <table class="data-table" style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <thead>
                <tr style="background-color: #0047AB; color: white;">
                    <th style="padding: 12px; text-align: left; width: 40%;">항목</th>
                    <th style="padding: 12px; text-align: right; width: 30%;">금액 (KRW)</th>
                    <th style="padding: 12px; text-align: right; width: 30%;">세대당 금액</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 10px;"><strong>시장 가치 (Market Value)</strong></td>
                    <td style="padding: 10px; text-align: right;">{self.format_currency(market_value)}</td>
                    <td style="padding: 10px; text-align: right;">{self.format_currency(price_per_unit_market)}</td>
                </tr>
                <tr>
                    <td style="padding: 10px;"><strong>LH 예상 매입가</strong></td>
                    <td style="padding: 10px; text-align: right; color: #0047AB;"><strong>{self.format_currency(lh_price)}</strong></td>
                    <td style="padding: 10px; text-align: right; color: #0047AB;"><strong>{self.format_currency(price_per_unit_lh)}</strong></td>
                </tr>
                <tr style="background-color: #fff3cd;">
                    <td style="padding: 10px;"><strong>가격 Gap (Market - LH)</strong></td>
                    <td style="padding: 10px; text-align: right; color: #856404;"><strong>{self.format_currency(gap_amount)}</strong></td>
                    <td style="padding: 10px; text-align: right; color: #856404;"><strong>{gap_pct:.1f}%</strong></td>
                </tr>
                <tr style="background-color: #e7f3ff;">
                    <td style="padding: 10px;"><strong>수익성 점수</strong></td>
                    <td style="padding: 10px; text-align: right;" colspan="2"><strong>{score}/100</strong></td>
                </tr>
                <tr style="background-color: {rec_color}; color: white;">
                    <td style="padding: 12px;"><strong>최종 권고안</strong></td>
                    <td style="padding: 12px; text-align: right;" colspan="2"><strong>{recommendation}</strong></td>
                </tr>
            </tbody>
        </table>
        
        <div style="margin-top: 10px; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #0047AB;">
            <p style="margin: 0; line-height: 1.6;">
                <strong>📊 분석 근거</strong>: 총 {unit_count}세대 기준, LH 매입가는 시장가치 대비 
                {100 - gap_pct:.1f}% 수준으로 산정됩니다. 수익성 점수 {score}/100은 
                {'우수한' if score >= 70 else '양호한' if score >= 50 else '개선 필요한'} 사업성을 나타냅니다.
            </p>
        </div>
        """
        
        return table_html


def test_lh_simulator():
    """Test the LH price simulator with sample data"""
    simulator = LHPurchasePriceSimulator()
    
    # Sample financial analysis results
    financial_analysis = {
        'summary': {
            'total_investment': 10_500_000_000,  # 105억원
            'unit_count': 60,
            'cap_rate': 4.65
        }
    }
    
    basic_info = {
        'address': '서울특별시 마포구 월드컵북로 120',
        'unit_type': '신혼부부 I',
        'land_area': 1200.0
    }
    
    result = simulator.simulate_lh_purchase_price(financial_analysis, basic_info)
    
    print("=" * 80)
    print("LH Purchase Price Simulator Test")
    print("=" * 80)
    print(f"\n📍 Project: {basic_info['address']}")
    print(f"🏢 Units: {result['metadata']['unit_count']}")
    print(f"🏗️  Total CapEx: {simulator.format_currency(financial_analysis['summary']['total_investment'])}")
    print("\n" + "=" * 80)
    print("SIMULATION RESULTS:")
    print("=" * 80)
    print(f"\n💰 Market Value:      {simulator.format_currency(result['market_value'])}")
    print(f"💰 LH Purchase Price: {simulator.format_currency(result['lh_purchase_price'])}")
    print(f"📊 Gap:               {simulator.format_currency(result['gap_amount'])} ({result['gap_percentage']:.1f}%)")
    print(f"⭐ Profitability:     {result['profitability_score']}/100")
    print(f"✅ Recommendation:    {result['recommendation']}")
    print(f"\n{result['explanation']}")
    
    print("\n" + "=" * 80)
    print("DETAILED TABLE:")
    print("=" * 80)
    print(simulator.generate_detailed_table(result))
    
    return result


if __name__ == "__main__":
    test_lh_simulator()
