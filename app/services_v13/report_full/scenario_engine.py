"""
ZeroSite v23 - A/B Scenario Comparison Engine
============================================
Production-Grade A/B Scenario Engine for LH Land Acquisition Report

This engine calculates and compares two scenarios (A: Youth, B: Newlywed) 
based on single land input, providing:
- Detailed scenario calculations
- Comparison tables
- Comparative summary
- Professional recommendations

Author: ZeroSite v23 Development Team
Version: 23.0.0
Date: 2025-12-10
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.utils.zoning_classifier import ZoningClassifier
from app.utils.market_data_processor import MarketDataProcessor


@dataclass
class ScenarioResult:
    """Standardized scenario result data structure"""
    supply_type: str
    far_legal: float
    far_relaxation: float
    far_final: float
    bcr: float
    buildable_area: float
    unit_count: int
    land_cost: float
    construction_cost: float
    design_cost: float
    total_capex: float
    lh_purchase_price: float
    profit: float
    roi: float
    irr: float
    npv: float
    avg_rent: float
    demand_score: float
    market_score: float
    risk_score: float
    decision: str
    payback_period: float


class ABScenarioEngine:
    """
    A/B Scenario Comparison Engine for ZeroSite v23
    
    Compares Youth (청년) vs Newlywed (신혼부부) scenarios on the same land,
    providing comprehensive financial, policy, and strategic comparisons.
    """
    
    def __init__(self):
        """Initialize the A/B Scenario Engine with required processors"""
        self.zoning_classifier = ZoningClassifier()
        self.market_processor = MarketDataProcessor()
        
        # Standard constants
        self.CONSTRUCTION_COST_PER_SQM = 2_100_000  # ₩2.1M/㎡
        self.DESIGN_COST_RATIO = 0.074  # 7.4% of construction
        self.LH_APPRAISAL_RATE = 0.95  # 95% of total CAPEX
        self.LH_MARGIN = 0.10  # 10% margin
        
        # Supply type configurations
        self.SUPPLY_CONFIG = {
            "청년": {
                "avg_unit_sqm": 30.0,
                "avg_rent_monthly": 350_000,
                "demand_score": 78.0,
                "market_score": 82.0,
                "risk_score": 65.0
            },
            "신혼부부": {
                "avg_unit_sqm": 36.0,
                "avg_rent_monthly": 420_000,
                "demand_score": 74.0,
                "market_score": 79.0,
                "risk_score": 62.0
            },
            "일반": {
                "avg_unit_sqm": 42.0,
                "avg_rent_monthly": 480_000,
                "demand_score": 70.0,
                "market_score": 75.0,
                "risk_score": 68.0
            },
            "행복주택": {
                "avg_unit_sqm": 33.0,
                "avg_rent_monthly": 380_000,
                "demand_score": 76.0,
                "market_score": 80.0,
                "risk_score": 64.0
            }
        }
    
    def generate_scenario_A(self, address: str, land_area_sqm: float) -> ScenarioResult:
        """
        Generate Scenario A: Youth Housing (청년)
        
        Args:
            address: Land address
            land_area_sqm: Land area in square meters
        
        Returns:
            ScenarioResult with all calculated metrics
        """
        return self._generate_scenario(address, land_area_sqm, "청년")
    
    def generate_scenario_B(self, address: str, land_area_sqm: float) -> ScenarioResult:
        """
        Generate Scenario B: Newlywed Housing (신혼부부)
        
        Args:
            address: Land address
            land_area_sqm: Land area in square meters
        
        Returns:
            ScenarioResult with all calculated metrics
        """
        return self._generate_scenario(address, land_area_sqm, "신혼부부")
    
    def _generate_scenario(self, address: str, land_area_sqm: float, supply_type: str) -> ScenarioResult:
        """
        Internal method to generate a complete scenario
        
        Args:
            address: Land address
            land_area_sqm: Land area in square meters
            supply_type: Supply type (청년, 신혼부부, 일반, 행복주택)
        
        Returns:
            ScenarioResult with all calculated metrics
        """
        try:
            # 1. Zoning Classification
            context = {
                "supply_type": supply_type,
                "address": address,
                "land_area_sqm": land_area_sqm
            }
            zoning_result = self.zoning_classifier.classify(
                address=address,
                context=context
            )
            
            far_legal = zoning_result['far_legal']
            far_relaxation = zoning_result['far_relaxation']
            far_final = zoning_result['far_final']
            bcr = zoning_result['bcr_final']
            
            # 2. Building calculations
            buildable_area = land_area_sqm * (far_final / 100)
            
            # 3. Unit calculations
            config = self.SUPPLY_CONFIG.get(supply_type, self.SUPPLY_CONFIG["일반"])
            avg_unit_sqm = config['avg_unit_sqm']
            unit_count = int(buildable_area / avg_unit_sqm)
            
            # 4. Market data
            market_data = self.market_processor.get_market_data_with_fallback(address)
            avg_land_price_per_sqm = market_data.get('avg_price_per_sqm', 12_860_000)
            
            # 5. Cost calculations
            land_cost = land_area_sqm * avg_land_price_per_sqm
            construction_cost = buildable_area * self.CONSTRUCTION_COST_PER_SQM
            design_cost = construction_cost * self.DESIGN_COST_RATIO
            total_capex = land_cost + construction_cost + design_cost
            
            # 6. LH purchase price
            lh_purchase_price = total_capex / self.LH_APPRAISAL_RATE
            
            # 7. Profitability
            profit = lh_purchase_price - total_capex
            roi = (profit / total_capex) * 100 if total_capex > 0 else 0.0
            
            # 8. IRR calculation (simplified - based on ROI and payback period)
            payback_period = 7.2  # Standard LH payback period
            irr = roi / payback_period if payback_period > 0 else 0.0
            
            # 9. NPV calculation (simplified)
            npv = profit  # Simplified NPV = Profit
            
            # 10. Policy scores
            demand_score = config['demand_score']
            market_score = config['market_score']
            risk_score = config['risk_score']
            avg_rent = config['avg_rent_monthly']
            
            # 11. Decision logic
            decision = self._calculate_decision(irr, npv, roi, demand_score)
            
            return ScenarioResult(
                supply_type=supply_type,
                far_legal=far_legal,
                far_relaxation=far_relaxation,
                far_final=far_final,
                bcr=bcr,
                buildable_area=buildable_area,
                unit_count=unit_count,
                land_cost=land_cost,
                construction_cost=construction_cost,
                design_cost=design_cost,
                total_capex=total_capex,
                lh_purchase_price=lh_purchase_price,
                profit=profit,
                roi=roi,
                irr=irr,
                npv=npv,
                avg_rent=avg_rent,
                demand_score=demand_score,
                market_score=market_score,
                risk_score=risk_score,
                decision=decision,
                payback_period=payback_period
            )
            
        except Exception as e:
            print(f"Error generating scenario for {supply_type}: {str(e)}")
            raise
    
    def _calculate_decision(self, irr: float, npv: float, roi: float, demand_score: float) -> str:
        """
        Calculate integrated decision (GO/CONDITIONAL-GO/NO-GO)
        
        Args:
            irr: Internal Rate of Return
            npv: Net Present Value
            roi: Return on Investment
            demand_score: Demand score
        
        Returns:
            Decision string
        """
        # Financial thresholds
        if irr >= 8.0 and npv > 0 and roi >= 10.0:
            financial_ok = True
        elif irr >= 6.0 and npv > -5e8 and roi >= 8.0:
            financial_conditional = True
        else:
            financial_ok = False
            financial_conditional = False
        
        # Policy thresholds
        policy_ok = demand_score >= 75.0
        policy_conditional = demand_score >= 65.0
        
        # Integrated decision
        if financial_ok and policy_ok:
            return "GO"
        elif (financial_ok and policy_conditional) or (financial_conditional and policy_ok):
            return "CONDITIONAL-GO"
        else:
            return "NO-GO"
    
    def compare_scenarios(self, scenario_a: ScenarioResult, scenario_b: ScenarioResult) -> Dict[str, Any]:
        """
        Compare Scenario A vs Scenario B
        
        Args:
            scenario_a: Youth scenario result
            scenario_b: Newlywed scenario result
        
        Returns:
            Comprehensive comparison dictionary
        """
        comparison = {
            "supply_type": {
                "A": scenario_a.supply_type,
                "B": scenario_b.supply_type,
                "winner": None
            },
            "far_final": {
                "A": scenario_a.far_final,
                "B": scenario_b.far_final,
                "diff": scenario_a.far_final - scenario_b.far_final,
                "diff_pct": ((scenario_a.far_final - scenario_b.far_final) / scenario_b.far_final * 100) if scenario_b.far_final > 0 else 0.0,
                "winner": "A" if scenario_a.far_final > scenario_b.far_final else "B"
            },
            "bcr": {
                "A": scenario_a.bcr,
                "B": scenario_b.bcr,
                "diff": scenario_a.bcr - scenario_b.bcr,
                "diff_pct": ((scenario_a.bcr - scenario_b.bcr) / scenario_b.bcr * 100) if scenario_b.bcr > 0 else 0.0,
                "winner": "A" if scenario_a.bcr > scenario_b.bcr else "B"
            },
            "buildable_area": {
                "A": scenario_a.buildable_area,
                "B": scenario_b.buildable_area,
                "diff": scenario_a.buildable_area - scenario_b.buildable_area,
                "diff_pct": ((scenario_a.buildable_area - scenario_b.buildable_area) / scenario_b.buildable_area * 100) if scenario_b.buildable_area > 0 else 0.0,
                "winner": "A" if scenario_a.buildable_area > scenario_b.buildable_area else "B"
            },
            "unit_count": {
                "A": scenario_a.unit_count,
                "B": scenario_b.unit_count,
                "diff": scenario_a.unit_count - scenario_b.unit_count,
                "diff_pct": ((scenario_a.unit_count - scenario_b.unit_count) / scenario_b.unit_count * 100) if scenario_b.unit_count > 0 else 0.0,
                "winner": "A" if scenario_a.unit_count > scenario_b.unit_count else "B"
            },
            "total_capex": {
                "A": scenario_a.total_capex,
                "B": scenario_b.total_capex,
                "diff": scenario_a.total_capex - scenario_b.total_capex,
                "diff_pct": ((scenario_a.total_capex - scenario_b.total_capex) / scenario_b.total_capex * 100) if scenario_b.total_capex > 0 else 0.0,
                "winner": "B" if scenario_a.total_capex > scenario_b.total_capex else "A"  # Lower is better
            },
            "lh_purchase_price": {
                "A": scenario_a.lh_purchase_price,
                "B": scenario_b.lh_purchase_price,
                "diff": scenario_a.lh_purchase_price - scenario_b.lh_purchase_price,
                "diff_pct": ((scenario_a.lh_purchase_price - scenario_b.lh_purchase_price) / scenario_b.lh_purchase_price * 100) if scenario_b.lh_purchase_price > 0 else 0.0,
                "winner": "A" if scenario_a.lh_purchase_price > scenario_b.lh_purchase_price else "B"
            },
            "profit": {
                "A": scenario_a.profit,
                "B": scenario_b.profit,
                "diff": scenario_a.profit - scenario_b.profit,
                "diff_pct": ((scenario_a.profit - scenario_b.profit) / scenario_b.profit * 100) if scenario_b.profit > 0 else 0.0,
                "winner": "A" if scenario_a.profit > scenario_b.profit else "B"
            },
            "roi": {
                "A": scenario_a.roi,
                "B": scenario_b.roi,
                "diff": scenario_a.roi - scenario_b.roi,
                "diff_pct": ((scenario_a.roi - scenario_b.roi) / scenario_b.roi * 100) if scenario_b.roi > 0 else 0.0,
                "winner": "A" if scenario_a.roi > scenario_b.roi else "B"
            },
            "irr": {
                "A": scenario_a.irr,
                "B": scenario_b.irr,
                "diff": scenario_a.irr - scenario_b.irr,
                "diff_pct": ((scenario_a.irr - scenario_b.irr) / scenario_b.irr * 100) if scenario_b.irr > 0 else 0.0,
                "winner": "A" if scenario_a.irr > scenario_b.irr else "B"
            },
            "npv": {
                "A": scenario_a.npv,
                "B": scenario_b.npv,
                "diff": scenario_a.npv - scenario_b.npv,
                "diff_pct": ((scenario_a.npv - scenario_b.npv) / scenario_b.npv * 100) if scenario_b.npv > 0 else 0.0,
                "winner": "A" if scenario_a.npv > scenario_b.npv else "B"
            },
            "avg_rent": {
                "A": scenario_a.avg_rent,
                "B": scenario_b.avg_rent,
                "diff": scenario_a.avg_rent - scenario_b.avg_rent,
                "diff_pct": ((scenario_a.avg_rent - scenario_b.avg_rent) / scenario_b.avg_rent * 100) if scenario_b.avg_rent > 0 else 0.0,
                "winner": "A" if scenario_a.avg_rent > scenario_b.avg_rent else "B"
            },
            "demand_score": {
                "A": scenario_a.demand_score,
                "B": scenario_b.demand_score,
                "diff": scenario_a.demand_score - scenario_b.demand_score,
                "diff_pct": ((scenario_a.demand_score - scenario_b.demand_score) / scenario_b.demand_score * 100) if scenario_b.demand_score > 0 else 0.0,
                "winner": "A" if scenario_a.demand_score > scenario_b.demand_score else "B"
            },
            "market_score": {
                "A": scenario_a.market_score,
                "B": scenario_b.market_score,
                "diff": scenario_a.market_score - scenario_b.market_score,
                "diff_pct": ((scenario_a.market_score - scenario_b.market_score) / scenario_b.market_score * 100) if scenario_b.market_score > 0 else 0.0,
                "winner": "A" if scenario_a.market_score > scenario_b.market_score else "B"
            },
            "risk_score": {
                "A": scenario_a.risk_score,
                "B": scenario_b.risk_score,
                "diff": scenario_a.risk_score - scenario_b.risk_score,
                "diff_pct": ((scenario_a.risk_score - scenario_b.risk_score) / scenario_b.risk_score * 100) if scenario_b.risk_score > 0 else 0.0,
                "winner": "B" if scenario_a.risk_score > scenario_b.risk_score else "A"  # Lower risk is better
            },
            "decision": {
                "A": scenario_a.decision,
                "B": scenario_b.decision,
                "winner": self._compare_decisions(scenario_a.decision, scenario_b.decision)
            }
        }
        
        return comparison
    
    def _compare_decisions(self, decision_a: str, decision_b: str) -> str:
        """Compare two decisions and determine winner"""
        decision_rank = {"GO": 3, "CONDITIONAL-GO": 2, "NO-GO": 1}
        rank_a = decision_rank.get(decision_a, 0)
        rank_b = decision_rank.get(decision_b, 0)
        
        if rank_a > rank_b:
            return "A"
        elif rank_b > rank_a:
            return "B"
        else:
            return "TIE"
    
    def generate_comparison_summary(
        self, 
        scenario_a: ScenarioResult, 
        scenario_b: ScenarioResult, 
        comparison: Dict[str, Any]
    ) -> str:
        """
        Generate professional comparison summary (minimum 180 characters)
        
        Args:
            scenario_a: Youth scenario result
            scenario_b: Newlywed scenario result
            comparison: Comparison dictionary
        
        Returns:
            Professional comparison summary text
        """
        # Calculate key metrics
        capex_diff_b = (scenario_a.total_capex - scenario_b.total_capex) / 1e8  # In 억원
        profit_diff_b = (scenario_a.profit - scenario_b.profit) / 1e8
        roi_diff = scenario_a.roi - scenario_b.roi
        unit_diff = scenario_a.unit_count - scenario_b.unit_count
        
        # Determine better scenario
        a_score = 0
        b_score = 0
        
        if scenario_a.profit > scenario_b.profit:
            a_score += 2
        else:
            b_score += 2
            
        if scenario_a.roi > scenario_b.roi:
            a_score += 2
        else:
            b_score += 2
            
        if scenario_a.demand_score > scenario_b.demand_score:
            a_score += 1
        else:
            b_score += 1
            
        if scenario_a.unit_count > scenario_b.unit_count:
            a_score += 1
        else:
            b_score += 1
        
        # Generate narrative
        if a_score > b_score:
            better_scenario = "A"
            better_supply = scenario_a.supply_type
            worse_supply = scenario_b.supply_type
            profit_leader = scenario_a.profit / 1e8
            roi_leader = scenario_a.roi
            unit_leader = scenario_a.unit_count
        else:
            better_scenario = "B"
            better_supply = scenario_b.supply_type
            worse_supply = scenario_a.supply_type
            profit_leader = scenario_b.profit / 1e8
            roi_leader = scenario_b.roi
            unit_leader = scenario_b.unit_count
        
        summary = f"""
A/B 시나리오 종합 분석 결과, **시나리오 {better_scenario} ({better_supply})** 가 전반적으로 우수한 것으로 분석되었습니다. 

**재무적 우위**: {better_supply}은(는) 사업 수익 {profit_leader:.2f}억원, ROI {roi_leader:.2f}%로 {worse_supply} 대비 {abs(profit_diff_b):.2f}억원({abs(roi_diff):.2f}%p) 높은 수익성을 보입니다. 
총 사업비는 시나리오 A가 {scenario_a.total_capex/1e8:.2f}억원, 시나리오 B가 {scenario_b.total_capex/1e8:.2f}억원으로 {abs(capex_diff_b):.2f}억원 차이가 있습니다.

**공급 효율성**: {better_supply}은(는) 총 {unit_leader}세대를 공급하여 {worse_supply} 대비 {abs(unit_diff)}세대 {'많은' if unit_diff > 0 and better_scenario == "A" else '적은' if unit_diff < 0 and better_scenario == "A" else '많은'} 공급이 가능합니다.
용적률 완화 적용 시 시나리오 A는 {scenario_a.far_final}%, 시나리오 B는 {scenario_b.far_final}%로 설정됩니다.

**정책 적합성**: 수요 점수는 시나리오 A {scenario_a.demand_score}점, 시나리오 B {scenario_b.demand_score}점으로 {'시나리오 A' if scenario_a.demand_score > scenario_b.demand_score else '시나리오 B'}가 더 높습니다.
시장 점수는 시나리오 A {scenario_a.market_score}점, 시나리오 B {scenario_b.market_score}점이며, 위험 점수는 시나리오 A {scenario_a.risk_score}점, 시나리오 B {scenario_b.risk_score}점입니다.

**최종 의사결정**: 시나리오 A는 '{scenario_a.decision}', 시나리오 B는 '{scenario_b.decision}' 판정을 받았습니다.
종합적으로 **시나리오 {better_scenario} ({better_supply}) 우선 검토**를 권고하며, LH 정책 목표 및 지역 수요 특성을 고려한 최종 결정이 필요합니다.
        """.strip()
        
        return summary
    
    def generate_recommendation(
        self,
        scenario_a: ScenarioResult,
        scenario_b: ScenarioResult,
        comparison: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate professional recommendation with conclusion and rationale
        
        Args:
            scenario_a: Youth scenario result
            scenario_b: Newlywed scenario result
            comparison: Comparison dictionary
        
        Returns:
            Dictionary with 'conclusion' (1 line) and 'rationale' (3 lines)
        """
        # Determine recommended scenario
        a_score = 0
        b_score = 0
        
        # Financial weight: 40%
        if scenario_a.profit > scenario_b.profit:
            a_score += 2
        else:
            b_score += 2
        if scenario_a.roi > scenario_b.roi:
            a_score += 2
        else:
            b_score += 2
        
        # Policy weight: 30%
        if scenario_a.demand_score > scenario_b.demand_score:
            a_score += 1.5
        else:
            b_score += 1.5
        
        # Unit supply weight: 20%
        if scenario_a.unit_count > scenario_b.unit_count:
            a_score += 1
        else:
            b_score += 1
        
        # Risk weight: 10%
        if scenario_a.risk_score < scenario_b.risk_score:  # Lower is better
            a_score += 0.5
        else:
            b_score += 0.5
        
        if a_score > b_score:
            recommended = "A"
            recommended_supply = scenario_a.supply_type
            recommended_result = scenario_a
            other_supply = scenario_b.supply_type
        else:
            recommended = "B"
            recommended_supply = scenario_b.supply_type
            recommended_result = scenario_b
            other_supply = scenario_a.supply_type
        
        conclusion = f"**시나리오 {recommended} ({recommended_supply}) 우선 추진** 권고"
        
        rationale = f"""1. **재무 우수성**: 사업 수익 {recommended_result.profit/1e8:.2f}억원, ROI {recommended_result.roi:.2f}%, IRR {recommended_result.irr:.2f}%로 LH 기준({'>=' if recommended_result.roi >= 10.0 else '<'}10%) 충족

2. **정책 적합성**: 수요 점수 {recommended_result.demand_score}점(등급: {'우수' if recommended_result.demand_score >= 75 else '양호'}), 시장 점수 {recommended_result.market_score}점으로 {other_supply} 대비 정책 목표 부합도 높음

3. **공급 효율성**: 총 {recommended_result.unit_count}세대 공급 가능, 평균 월세 {recommended_result.avg_rent:,}원으로 임대료 경쟁력 확보 및 사회적 가치 실현
"""
        
        return {
            "conclusion": conclusion,
            "rationale": rationale.strip()
        }


def main():
    """Test the A/B Scenario Engine"""
    engine = ABScenarioEngine()
    
    # Test case: Gangnam land
    address = "서울특별시 강남구 역삼동 123-45"
    land_area_sqm = 1650.0
    
    print("=" * 80)
    print("ZeroSite v23 - A/B Scenario Comparison Engine Test")
    print("=" * 80)
    print(f"\n📍 Address: {address}")
    print(f"📐 Land Area: {land_area_sqm:,.0f} ㎡")
    print("\n" + "=" * 80)
    
    # Generate scenarios
    print("\n🔵 Generating Scenario A (청년)...")
    scenario_a = engine.generate_scenario_A(address, land_area_sqm)
    
    print("🟠 Generating Scenario B (신혼부부)...")
    scenario_b = engine.generate_scenario_B(address, land_area_sqm)
    
    # Compare
    print("\n📊 Comparing scenarios...")
    comparison = engine.compare_scenarios(scenario_a, scenario_b)
    
    # Generate summary
    print("\n📝 Generating comparison summary...")
    summary = engine.generate_comparison_summary(scenario_a, scenario_b, comparison)
    
    # Generate recommendation
    print("\n💡 Generating recommendation...")
    recommendation = engine.generate_recommendation(scenario_a, scenario_b, comparison)
    
    # Display results
    print("\n" + "=" * 80)
    print("📋 SCENARIO A (청년)")
    print("=" * 80)
    print(f"FAR: {scenario_a.far_legal}% → {scenario_a.far_final}% (완화: +{scenario_a.far_relaxation}%p)")
    print(f"BCR: {scenario_a.bcr}%")
    print(f"연면적: {scenario_a.buildable_area:,.2f} ㎡")
    print(f"세대수: {scenario_a.unit_count} 세대")
    print(f"총 사업비: {scenario_a.total_capex/1e8:.2f} 억원")
    print(f"LH 매입가: {scenario_a.lh_purchase_price/1e8:.2f} 억원")
    print(f"사업 수익: {scenario_a.profit/1e8:.2f} 억원")
    print(f"ROI: {scenario_a.roi:.2f}%")
    print(f"IRR: {scenario_a.irr:.2f}%")
    print(f"의사결정: {scenario_a.decision}")
    
    print("\n" + "=" * 80)
    print("📋 SCENARIO B (신혼부부)")
    print("=" * 80)
    print(f"FAR: {scenario_b.far_legal}% → {scenario_b.far_final}% (완화: +{scenario_b.far_relaxation}%p)")
    print(f"BCR: {scenario_b.bcr}%")
    print(f"연면적: {scenario_b.buildable_area:,.2f} ㎡")
    print(f"세대수: {scenario_b.unit_count} 세대")
    print(f"총 사업비: {scenario_b.total_capex/1e8:.2f} 억원")
    print(f"LH 매입가: {scenario_b.lh_purchase_price/1e8:.2f} 억원")
    print(f"사업 수익: {scenario_b.profit/1e8:.2f} 억원")
    print(f"ROI: {scenario_b.roi:.2f}%")
    print(f"IRR: {scenario_b.irr:.2f}%")
    print(f"의사결정: {scenario_b.decision}")
    
    print("\n" + "=" * 80)
    print("📊 COMPARISON SUMMARY")
    print("=" * 80)
    print(summary)
    
    print("\n" + "=" * 80)
    print("💡 RECOMMENDATION")
    print("=" * 80)
    print(recommendation['conclusion'])
    print("\n**상세 근거**:")
    print(recommendation['rationale'])
    
    print("\n" + "=" * 80)
    print("✅ Test completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
