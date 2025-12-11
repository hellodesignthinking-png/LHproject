#!/usr/bin/env python3
"""
A/B Scenario Engine for ZeroSite v3.2
=====================================
Compares Youth (청년) vs. Newlywed (신혼부부) housing scenarios

Author: ZeroSite v3.2 Development Team
Version: 3.2.0
Date: 2025-12-11
"""

from typing import Dict, List, Tuple
import math


class ABScenarioEngine:
    """
    A/B Scenario Comparison Engine
    
    Compares two housing scenarios:
    - Scenario A: Youth Housing (청년)
    - Scenario B: Newlywed Housing (신혼부부)
    
    Based on single land input, generates comprehensive comparison
    including financial, architectural, and policy metrics.
    """
    
    # Housing type specifications (LH 2024 standards)
    YOUTH_UNIT_SIZE_SQM = 60.0  # 18.1평
    NEWLYWED_UNIT_SIZE_SQM = 85.0  # 25.7평
    
    # FAR relaxation policies (LH 2024)
    YOUTH_FAR_RELAXATION = 50.0  # +50%p
    NEWLYWED_FAR_RELAXATION = 30.0  # +30%p
    
    # Financial thresholds (LH criteria)
    ROI_THRESHOLD = 5.0  # 5% ROI minimum for GO decision
    IRR_THRESHOLD = 7.0  # 7% IRR minimum
    
    def __init__(self):
        """Initialize A/B Scenario Engine"""
        self.version = "3.2.0"
    
    def compare_scenarios(self,
                         land_area_sqm: float,
                         bcr_legal: float,
                         far_legal: float,
                         avg_land_price_per_sqm: float) -> Dict:
        """
        Run complete A/B scenario comparison
        
        Args:
            land_area_sqm: Land area in square meters
            bcr_legal: Legal building coverage ratio (%)
            far_legal: Legal floor area ratio (%)
            avg_land_price_per_sqm: Average land price per sqm (KRW)
        
        Returns:
            Complete comparison data dictionary
        """
        
        # Calculate Scenario A (Youth)
        scenario_a = self._calculate_scenario(
            scenario_type='youth',
            land_area_sqm=land_area_sqm,
            bcr_legal=bcr_legal,
            far_legal=far_legal,
            avg_land_price_per_sqm=avg_land_price_per_sqm
        )
        
        # Calculate Scenario B (Newlywed)
        scenario_b = self._calculate_scenario(
            scenario_type='newlywed',
            land_area_sqm=land_area_sqm,
            bcr_legal=bcr_legal,
            far_legal=far_legal,
            avg_land_price_per_sqm=avg_land_price_per_sqm
        )
        
        # Generate comparison table (15 metrics)
        comparison_table = self._generate_comparison_table(scenario_a, scenario_b)
        
        # Determine winner
        recommendation = self._generate_recommendation(scenario_a, scenario_b)
        
        return {
            'scenario_a': scenario_a,
            'scenario_b': scenario_b,
            'comparison_table': comparison_table,
            'recommendation': recommendation,
            'version': self.version,
        }
    
    def _calculate_scenario(self,
                           scenario_type: str,
                           land_area_sqm: float,
                           bcr_legal: float,
                           far_legal: float,
                           avg_land_price_per_sqm: float) -> Dict:
        """Calculate metrics for single scenario"""
        
        # Unit specifications
        if scenario_type == 'youth':
            unit_size_sqm = self.YOUTH_UNIT_SIZE_SQM
            far_relaxation = self.YOUTH_FAR_RELAXATION
            target_group = "청년 (19-39세)"
            scenario_name = "Scenario A: Youth"
        else:
            unit_size_sqm = self.NEWLYWED_UNIT_SIZE_SQM
            far_relaxation = self.NEWLYWED_FAR_RELAXATION
            target_group = "신혼부부 (혼인 7년 이하)"
            scenario_name = "Scenario B: Newlywed"
        
        # Calculate FAR
        far_final = far_legal + far_relaxation
        
        # Calculate buildable area
        total_floor_area_sqm = land_area_sqm * (far_final / 100.0)
        
        # Calculate units (80% efficiency for common areas)
        net_residential_area = total_floor_area_sqm * 0.80
        total_units = int(net_residential_area / unit_size_sqm)
        
        # Calculate floors (assume 3.5m per floor, BCR-based footprint)
        building_footprint = land_area_sqm * (bcr_legal / 100.0)
        floor_area_per_floor = building_footprint * 0.85  # 85% efficiency
        floors = math.ceil(total_floor_area_sqm / floor_area_per_floor)
        
        # Calculate CAPEX (simplified using v3.2 engine logic)
        land_cost = land_area_sqm * avg_land_price_per_sqm
        acquisition_tax = land_cost * 0.046  # 4.6%
        
        # Construction cost (LH 2024 standard)
        construction_cost_per_sqm = 4_025_000  # ₩/㎡ (Seoul)
        construction_cost = total_floor_area_sqm * construction_cost_per_sqm
        
        design_fee = construction_cost * 0.08
        supervision_fee = construction_cost * 0.03
        contingency = construction_cost * 0.10
        
        total_capex = (land_cost + acquisition_tax + construction_cost +
                      design_fee + supervision_fee + contingency)
        
        # Calculate LH purchase price (85% appraisal method)
        lh_appraisal_per_unit = 800_000_000  # 8억원 (simplified)
        if scenario_type == 'youth':
            lh_appraisal_per_unit = 650_000_000  # 6.5억원 (smaller units)
        
        lh_purchase_price = total_units * lh_appraisal_per_unit
        
        # Calculate financial metrics
        profit = lh_purchase_price - total_capex
        roi_percent = (profit / total_capex) * 100 if total_capex > 0 else 0
        
        # IRR (simplified: assume 2.5 year project)
        if profit > 0:
            irr_percent = ((lh_purchase_price / total_capex) ** (1/2.5) - 1) * 100
        else:
            irr_percent = -10.0  # Negative IRR for loss
        
        # Decision logic
        decision = "GO" if roi_percent >= self.ROI_THRESHOLD and irr_percent >= self.IRR_THRESHOLD else "NO-GO"
        
        # AI demand score (simplified placeholder)
        ai_demand_score = 75.0 if scenario_type == 'youth' else 82.0
        
        # Expected occupancy
        expected_occupancy_rate = 92.0 if scenario_type == 'newlywed' else 88.0
        
        # Monthly rent (placeholder)
        monthly_rent_per_unit = 350_000 if scenario_type == 'youth' else 450_000
        
        return {
            'scenario_name': scenario_name,
            'scenario_type': scenario_type,
            'target_group': target_group,
            
            # Unit specs
            'unit_size_sqm': unit_size_sqm,
            'unit_size_pyeong': round(unit_size_sqm / 3.3058, 1),
            'total_units': total_units,
            
            # Architectural metrics
            'far_legal': far_legal,
            'far_final': far_final,
            'far_relaxation': far_relaxation,
            'bcr_legal': bcr_legal,
            'floors': floors,
            'total_floor_area_sqm': round(total_floor_area_sqm, 1),
            'building_footprint_sqm': round(building_footprint, 1),
            
            # Financial metrics
            'land_cost': land_cost,
            'acquisition_tax': acquisition_tax,
            'construction_cost': construction_cost,
            'design_fee': design_fee,
            'supervision_fee': supervision_fee,
            'contingency': contingency,
            'total_capex': total_capex,
            'lh_purchase_price': lh_purchase_price,
            'profit': profit,
            'roi_percent': round(roi_percent, 2),
            'irr_percent': round(irr_percent, 2),
            
            # Policy metrics
            'ai_demand_score': ai_demand_score,
            'expected_occupancy_rate': expected_occupancy_rate,
            'monthly_rent_per_unit': monthly_rent_per_unit,
            
            # Decision
            'decision': decision,
        }
    
    def _generate_comparison_table(self, scenario_a: Dict, scenario_b: Dict) -> List[Dict]:
        """Generate 15-metric comparison table"""
        
        metrics = [
            # Financial (1-6)
            {
                'id': 1,
                'category': 'Financial',
                'name': '총 사업비 (CAPEX)',
                'value_a': scenario_a['total_capex'],
                'value_b': scenario_b['total_capex'],
                'unit': '원',
                'format': 'currency',
                'winner': 'A' if scenario_a['total_capex'] < scenario_b['total_capex'] else 'B',
            },
            {
                'id': 2,
                'category': 'Financial',
                'name': 'LH 매입가',
                'value_a': scenario_a['lh_purchase_price'],
                'value_b': scenario_b['lh_purchase_price'],
                'unit': '원',
                'format': 'currency',
                'winner': 'A' if scenario_a['lh_purchase_price'] > scenario_b['lh_purchase_price'] else 'B',
            },
            {
                'id': 3,
                'category': 'Financial',
                'name': '사업 수익',
                'value_a': scenario_a['profit'],
                'value_b': scenario_b['profit'],
                'unit': '원',
                'format': 'currency',
                'winner': 'A' if scenario_a['profit'] > scenario_b['profit'] else 'B',
            },
            {
                'id': 4,
                'category': 'Financial',
                'name': 'ROI (투자수익률)',
                'value_a': scenario_a['roi_percent'],
                'value_b': scenario_b['roi_percent'],
                'unit': '%',
                'format': 'percent',
                'winner': 'A' if scenario_a['roi_percent'] > scenario_b['roi_percent'] else 'B',
            },
            {
                'id': 5,
                'category': 'Financial',
                'name': 'IRR (내부수익률)',
                'value_a': scenario_a['irr_percent'],
                'value_b': scenario_b['irr_percent'],
                'unit': '%',
                'format': 'percent',
                'winner': 'A' if scenario_a['irr_percent'] > scenario_b['irr_percent'] else 'B',
            },
            {
                'id': 6,
                'category': 'Financial',
                'name': 'NPV (순현재가치)',
                'value_a': scenario_a['profit'] * 0.85,  # Simplified NPV
                'value_b': scenario_b['profit'] * 0.85,
                'unit': '원',
                'format': 'currency',
                'winner': 'A' if scenario_a['profit'] > scenario_b['profit'] else 'B',
            },
            
            # Architectural (7-10)
            {
                'id': 7,
                'category': 'Architectural',
                'name': '법정 용적률',
                'value_a': scenario_a['far_legal'],
                'value_b': scenario_b['far_legal'],
                'unit': '%',
                'format': 'percent',
                'winner': 'Equal',
            },
            {
                'id': 8,
                'category': 'Architectural',
                'name': '완화 후 용적률',
                'value_a': scenario_a['far_final'],
                'value_b': scenario_b['far_final'],
                'unit': '%',
                'format': 'percent',
                'winner': 'A' if scenario_a['far_final'] > scenario_b['far_final'] else 'B',
            },
            {
                'id': 9,
                'category': 'Architectural',
                'name': '연면적',
                'value_a': scenario_a['total_floor_area_sqm'],
                'value_b': scenario_b['total_floor_area_sqm'],
                'unit': '㎡',
                'format': 'number',
                'winner': 'A' if scenario_a['total_floor_area_sqm'] > scenario_b['total_floor_area_sqm'] else 'B',
            },
            {
                'id': 10,
                'category': 'Architectural',
                'name': '세대수',
                'value_a': scenario_a['total_units'],
                'value_b': scenario_b['total_units'],
                'unit': '세대',
                'format': 'number',
                'winner': 'A' if scenario_a['total_units'] > scenario_b['total_units'] else 'B',
            },
            
            # Market & Policy (11-13)
            {
                'id': 11,
                'category': 'Market',
                'name': 'AI 수요 점수',
                'value_a': scenario_a['ai_demand_score'],
                'value_b': scenario_b['ai_demand_score'],
                'unit': '점',
                'format': 'score',
                'winner': 'A' if scenario_a['ai_demand_score'] > scenario_b['ai_demand_score'] else 'B',
            },
            {
                'id': 12,
                'category': 'Market',
                'name': '예상 입주율',
                'value_a': scenario_a['expected_occupancy_rate'],
                'value_b': scenario_b['expected_occupancy_rate'],
                'unit': '%',
                'format': 'percent',
                'winner': 'A' if scenario_a['expected_occupancy_rate'] > scenario_b['expected_occupancy_rate'] else 'B',
            },
            {
                'id': 13,
                'category': 'Policy',
                'name': '월 임대료',
                'value_a': scenario_a['monthly_rent_per_unit'],
                'value_b': scenario_b['monthly_rent_per_unit'],
                'unit': '원',
                'format': 'currency',
                'winner': 'B' if scenario_a['monthly_rent_per_unit'] < scenario_b['monthly_rent_per_unit'] else 'A',
            },
            
            # Decision (14-15)
            {
                'id': 14,
                'category': 'Decision',
                'name': '재무 판정',
                'value_a': scenario_a['decision'],
                'value_b': scenario_b['decision'],
                'unit': '',
                'format': 'text',
                'winner': 'A' if scenario_a['decision'] == 'GO' else ('B' if scenario_b['decision'] == 'GO' else 'Equal'),
            },
            {
                'id': 15,
                'category': 'Decision',
                'name': '종합 점수',
                'value_a': self._calculate_composite_score(scenario_a),
                'value_b': self._calculate_composite_score(scenario_b),
                'unit': '점',
                'format': 'score',
                'winner': 'A' if self._calculate_composite_score(scenario_a) > self._calculate_composite_score(scenario_b) else 'B',
            },
        ]
        
        return metrics
    
    def _calculate_composite_score(self, scenario: Dict) -> float:
        """Calculate composite score (0-100) for scenario"""
        
        # Weighted scoring
        financial_score = 50.0 if scenario['decision'] == 'GO' else 20.0
        demand_score = scenario['ai_demand_score'] * 0.3
        occupancy_score = scenario['expected_occupancy_rate'] * 0.2
        
        composite = financial_score + demand_score + occupancy_score
        
        return min(100.0, composite)
    
    def _generate_recommendation(self, scenario_a: Dict, scenario_b: Dict) -> Dict:
        """Generate final recommendation"""
        
        score_a = self._calculate_composite_score(scenario_a)
        score_b = self._calculate_composite_score(scenario_b)
        
        if score_a > score_b:
            recommended = 'A'
            recommended_name = 'Scenario A (청년 주택)'
            reasoning = f"청년 주택이 종합 점수 {score_a:.1f}점으로 신혼부부 {score_b:.1f}점 대비 우수합니다."
        elif score_b > score_a:
            recommended = 'B'
            recommended_name = 'Scenario B (신혼부부 주택)'
            reasoning = f"신혼부부 주택이 종합 점수 {score_b:.1f}점으로 청년 {score_a:.1f}점 대비 우수합니다."
        else:
            recommended = 'Equal'
            recommended_name = '동등 (추가 분석 필요)'
            reasoning = f"두 시나리오가 동점 ({score_a:.1f}점)으로 추가 분석이 필요합니다."
        
        caveats = [
            "본 분석은 2024년 LH 정책 기준을 적용하였습니다.",
            "실제 사업 시 최신 정책 변동을 확인하시기 바랍니다.",
            "본 분석은 의사결정 참고자료이며, 최종 책임은 사업 주체에 있습니다.",
        ]
        
        return {
            'recommended_scenario': recommended,
            'recommended_name': recommended_name,
            'score_a': round(score_a, 1),
            'score_b': round(score_b, 1),
            'reasoning': reasoning,
            'caveats': caveats,
        }


# Test function
if __name__ == "__main__":
    print("=" * 80)
    print("A/B SCENARIO ENGINE TEST (v3.2)")
    print("=" * 80)
    
    engine = ABScenarioEngine()
    
    # Test case: Mapo-gu
    result = engine.compare_scenarios(
        land_area_sqm=660.0,
        bcr_legal=50.0,
        far_legal=300.0,
        avg_land_price_per_sqm=9_500_000
    )
    
    print("\n📊 Scenario A (Youth):")
    print(f"   Units: {result['scenario_a']['total_units']}")
    print(f"   FAR: {result['scenario_a']['far_final']}%")
    print(f"   CAPEX: {result['scenario_a']['total_capex']/100000000:.1f}억원")
    print(f"   ROI: {result['scenario_a']['roi_percent']:.2f}%")
    print(f"   Decision: {result['scenario_a']['decision']}")
    
    print("\n📊 Scenario B (Newlywed):")
    print(f"   Units: {result['scenario_b']['total_units']}")
    print(f"   FAR: {result['scenario_b']['far_final']}%")
    print(f"   CAPEX: {result['scenario_b']['total_capex']/100000000:.1f}억원")
    print(f"   ROI: {result['scenario_b']['roi_percent']:.2f}%")
    print(f"   Decision: {result['scenario_b']['decision']}")
    
    print("\n🎯 Recommendation:")
    print(f"   Winner: {result['recommendation']['recommended_name']}")
    print(f"   Score A: {result['recommendation']['score_a']}")
    print(f"   Score B: {result['recommendation']['score_b']}")
    print(f"   Reasoning: {result['recommendation']['reasoning']}")
    
    print("\n✅ A/B Scenario Engine Test Complete")
