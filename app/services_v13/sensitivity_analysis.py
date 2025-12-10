"""
ZeroSite v23 - Sensitivity Analysis Module
==========================================

민감도 분석 모듈: CAPEX ±10%, 감정평가율 ±5% 시나리오

Author: ZeroSite AI Analysis System
Date: 2025-12-10
Version: v23
"""

from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SensitivityAnalyzer:
    """
    민감도 분석 엔진
    
    분석 변수:
    - CAPEX: -10%, 0%, +10%
    - 감정평가율: -5%, 0%, +5%
    
    총 9개 시나리오 (3 × 3)
    """
    
    def __init__(self):
        """Initialize Sensitivity Analyzer"""
        logger.info("💡 Sensitivity Analyzer v23 초기화")
    
    def analyze_comprehensive(
        self,
        base_capex: float,
        base_appraisal_rate: float,
        market_land_value: float,
        gross_floor_area: float,
        lh_standard_cost_per_sqm: float = 3500000
    ) -> Dict:
        """
        종합 민감도 분석
        
        Args:
            base_capex: 기본 CAPEX (원)
            base_appraisal_rate: 기본 감정평가율 (0.92)
            market_land_value: 시장 토지가 (원)
            gross_floor_area: 연면적 (㎡)
            lh_standard_cost_per_sqm: LH 표준건축비 (원/㎡)
        
        Returns:
            {
                'scenarios': List[Dict],
                'summary': Dict,
                'tornado_data': Dict
            }
        """
        logger.info(f"📊 민감도 분석 시작: CAPEX {base_capex/1e8:.0f}억, 감정평가율 {base_appraisal_rate*100:.0f}%")
        
        # Variation ranges
        capex_variations = [-0.10, 0.0, 0.10]  # -10%, 0%, +10%
        appraisal_variations = [-0.05, 0.0, 0.05]  # -5%, 0%, +5%
        
        scenarios = []
        
        # Generate 9 scenarios (3 × 3)
        for capex_var in capex_variations:
            for appraisal_var in appraisal_variations:
                scenario = self._calculate_scenario(
                    base_capex=base_capex,
                    base_appraisal_rate=base_appraisal_rate,
                    market_land_value=market_land_value,
                    gross_floor_area=gross_floor_area,
                    lh_standard_cost_per_sqm=lh_standard_cost_per_sqm,
                    capex_variation=capex_var,
                    appraisal_variation=appraisal_var
                )
                scenarios.append(scenario)
        
        # Calculate summary statistics
        summary = self._calculate_summary(scenarios)
        
        # Generate tornado diagram data
        tornado_data = self._generate_tornado_data(scenarios)
        
        logger.info(f"✅ 민감도 분석 완료: {len(scenarios)}개 시나리오")
        
        return {
            'scenarios': scenarios,
            'summary': summary,
            'tornado_data': tornado_data,
            'analysis_date': '2025-12-10',
            'methodology': 'CAPEX ±10%, 감정평가율 ±5% (9개 시나리오)'
        }
    
    def _calculate_scenario(
        self,
        base_capex: float,
        base_appraisal_rate: float,
        market_land_value: float,
        gross_floor_area: float,
        lh_standard_cost_per_sqm: float,
        capex_variation: float,
        appraisal_variation: float
    ) -> Dict:
        """
        개별 시나리오 계산
        """
        # Adjusted values
        adjusted_capex = base_capex * (1 + capex_variation)
        adjusted_appraisal_rate = base_appraisal_rate * (1 + appraisal_variation)
        
        # LH Appraisal calculation
        lh_land_appraisal = market_land_value * adjusted_appraisal_rate
        lh_building_appraisal = lh_standard_cost_per_sqm * gross_floor_area
        lh_total_appraisal = lh_land_appraisal + lh_building_appraisal
        lh_purchase_price = lh_total_appraisal  # 100% for 신축매입임대
        
        # Financial metrics
        profit = lh_purchase_price - adjusted_capex
        roi_pct = (profit / adjusted_capex * 100) if adjusted_capex > 0 else 0.0
        
        # Simple IRR estimation (construction period = 2.5 years)
        construction_period = 2.5
        irr_pct = roi_pct / construction_period
        
        # Decision
        policy_threshold = 2.0  # 2.0% for policy projects
        private_threshold = 8.0  # 8.0% for private projects
        
        if irr_pct >= private_threshold:
            decision = 'GO (Private)'
            decision_status = 'excellent'
        elif irr_pct >= policy_threshold:
            decision = 'GO (Policy)'
            decision_status = 'good'
        else:
            decision = 'NO-GO'
            decision_status = 'poor'
        
        # Scenario label
        capex_label = f"CAPEX {capex_variation:+.0%}"
        appraisal_label = f"감정평가율 {appraisal_variation:+.0%}"
        
        if capex_variation == 0 and appraisal_variation == 0:
            scenario_name = "Base (기준)"
        else:
            scenario_name = f"{capex_label}, {appraisal_label}"
        
        return {
            'scenario_name': scenario_name,
            'capex_variation_pct': capex_variation * 100,
            'appraisal_variation_pct': appraisal_variation * 100,
            'adjusted_capex_won': adjusted_capex,
            'adjusted_capex_eok': round(adjusted_capex / 1e8, 2),
            'adjusted_appraisal_rate': adjusted_appraisal_rate,
            'adjusted_appraisal_rate_pct': round(adjusted_appraisal_rate * 100, 2),
            'lh_land_appraisal_eok': round(lh_land_appraisal / 1e8, 2),
            'lh_building_appraisal_eok': round(lh_building_appraisal / 1e8, 2),
            'lh_purchase_price_won': lh_purchase_price,
            'lh_purchase_price_eok': round(lh_purchase_price / 1e8, 2),
            'profit_won': profit,
            'profit_eok': round(profit / 1e8, 2),
            'roi_pct': round(roi_pct, 2),
            'irr_pct': round(irr_pct, 2),
            'decision': decision,
            'decision_status': decision_status
        }
    
    def _calculate_summary(self, scenarios: List[Dict]) -> Dict:
        """
        시나리오 요약 통계
        """
        profits = [s['profit_eok'] for s in scenarios]
        roi_values = [s['roi_pct'] for s in scenarios]
        irr_values = [s['irr_pct'] for s in scenarios]
        
        # Find best/worst scenarios
        best_scenario = max(scenarios, key=lambda x: x['profit_eok'])
        worst_scenario = min(scenarios, key=lambda x: x['profit_eok'])
        
        # Count decisions
        go_count = sum(1 for s in scenarios if 'GO' in s['decision'])
        no_go_count = sum(1 for s in scenarios if 'NO-GO' in s['decision'])
        
        return {
            'profit_min_eok': min(profits),
            'profit_max_eok': max(profits),
            'profit_range_eok': max(profits) - min(profits),
            'roi_min_pct': min(roi_values),
            'roi_max_pct': max(roi_values),
            'roi_range_pct': max(roi_values) - min(roi_values),
            'irr_min_pct': min(irr_values),
            'irr_max_pct': max(irr_values),
            'irr_range_pct': max(irr_values) - min(irr_values),
            'best_scenario': best_scenario['scenario_name'],
            'best_profit_eok': best_scenario['profit_eok'],
            'worst_scenario': worst_scenario['scenario_name'],
            'worst_profit_eok': worst_scenario['profit_eok'],
            'go_count': go_count,
            'no_go_count': no_go_count,
            'go_probability_pct': round(go_count / len(scenarios) * 100, 1)
        }
    
    def _generate_tornado_data(self, scenarios: List[Dict]) -> Dict:
        """
        Tornado 다이어그램 데이터 생성
        
        각 변수의 영향력을 측정
        """
        # Find base scenario
        base = next(s for s in scenarios if s['scenario_name'] == "Base (기준)")
        base_profit = base['profit_eok']
        
        # CAPEX impact
        capex_neg10 = next(s for s in scenarios 
                          if s['capex_variation_pct'] == -10 and s['appraisal_variation_pct'] == 0)
        capex_pos10 = next(s for s in scenarios 
                          if s['capex_variation_pct'] == 10 and s['appraisal_variation_pct'] == 0)
        
        capex_impact_neg = capex_neg10['profit_eok'] - base_profit
        capex_impact_pos = capex_pos10['profit_eok'] - base_profit
        capex_total_range = abs(capex_impact_pos) + abs(capex_impact_neg)
        
        # Appraisal rate impact
        appraisal_neg5 = next(s for s in scenarios 
                             if s['capex_variation_pct'] == 0 and s['appraisal_variation_pct'] == -5)
        appraisal_pos5 = next(s for s in scenarios 
                             if s['capex_variation_pct'] == 0 and s['appraisal_variation_pct'] == 5)
        
        appraisal_impact_neg = appraisal_neg5['profit_eok'] - base_profit
        appraisal_impact_pos = appraisal_pos5['profit_eok'] - base_profit
        appraisal_total_range = abs(appraisal_impact_pos) + abs(appraisal_impact_neg)
        
        # Sort by impact (larger range = more sensitive)
        factors = [
            {
                'factor': 'CAPEX',
                'variation': '±10%',
                'impact_negative': capex_impact_neg,
                'impact_positive': capex_impact_pos,
                'total_range': capex_total_range,
                'rank': 1 if capex_total_range >= appraisal_total_range else 2
            },
            {
                'factor': '감정평가율',
                'variation': '±5%',
                'impact_negative': appraisal_impact_neg,
                'impact_positive': appraisal_impact_pos,
                'total_range': appraisal_total_range,
                'rank': 1 if appraisal_total_range >= capex_total_range else 2
            }
        ]
        
        # Sort by total_range (descending)
        factors.sort(key=lambda x: x['total_range'], reverse=True)
        
        return {
            'base_profit_eok': base_profit,
            'factors': factors,
            'most_sensitive': factors[0]['factor'],
            'interpretation': self._interpret_tornado(factors)
        }
    
    def _interpret_tornado(self, factors: List[Dict]) -> str:
        """
        Tornado 다이어그램 해석
        """
        most_sensitive = factors[0]
        
        interpretation = f"""
민감도 분석 결과, 프로젝트 수익성에 가장 큰 영향을 미치는 요인은 '{most_sensitive['factor']}'입니다.

• {most_sensitive['factor']} {most_sensitive['variation']} 변동 시:
  - 최대 영향: {most_sensitive['total_range']:.2f}억원 (수익 변동폭)
  - 음의 영향: {most_sensitive['impact_negative']:.2f}억원
  - 양의 영향: {most_sensitive['impact_positive']:.2f}억원

• 두 번째 민감 요인: {factors[1]['factor']}
  - 최대 영향: {factors[1]['total_range']:.2f}억원

결론: {most_sensitive['factor']} 관리가 사업성 확보의 핵심입니다.
""".strip()
        
        return interpretation


def format_sensitivity_report(analysis_result: Dict) -> str:
    """
    민감도 분석 리포트 포맷팅
    """
    scenarios = analysis_result['scenarios']
    summary = analysis_result['summary']
    tornado = analysis_result['tornado_data']
    
    report = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZeroSite v23 - 민감도 분석 리포트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

분석 방법: {analysis_result['methodology']}
분석 일자: {analysis_result['analysis_date']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 9개 시나리오 분석 결과
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌────────────────────────────┬──────┬──────┬──────┬────────┐
│ 시나리오                    │ CAPEX│ Profit│ ROI  │ 의사결정│
│                            │ (억) │ (억)  │ (%)  │        │
├────────────────────────────┼──────┼──────┼──────┼────────┤
"""
    
    for s in scenarios:
        status_icon = "✅" if "GO" in s['decision'] else "❌"
        report += f"│ {s['scenario_name']:<26} │ {s['adjusted_capex_eok']:>5.0f}│ {s['profit_eok']:>6.2f}│ {s['roi_pct']:>5.2f}│ {status_icon} {s['decision']:<6}│\n"
    
    report += f"""└────────────────────────────┴──────┴──────┴──────┴────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 요약 통계
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

수익 (Profit):
  • 최소: {summary['profit_min_eok']:.2f}억원 ({summary['worst_scenario']})
  • 최대: {summary['profit_max_eok']:.2f}억원 ({summary['best_scenario']})
  • 변동폭: {summary['profit_range_eok']:.2f}억원

ROI (투자수익률):
  • 최소: {summary['roi_min_pct']:.2f}%
  • 최대: {summary['roi_max_pct']:.2f}%
  • 변동폭: {summary['roi_range_pct']:.2f}%p

IRR (내부수익률):
  • 최소: {summary['irr_min_pct']:.2f}%
  • 최대: {summary['irr_max_pct']:.2f}%
  • 변동폭: {summary['irr_range_pct']:.2f}%p

의사결정:
  • GO 시나리오: {summary['go_count']}개 ({summary['go_probability_pct']:.1f}%)
  • NO-GO 시나리오: {summary['no_go_count']}개

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Tornado 다이어그램 (민감도 순위)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

기준 수익: {tornado['base_profit_eok']:.2f}억원

"""
    
    for i, factor in enumerate(tornado['factors'], 1):
        report += f"""
{i}위. {factor['factor']} ({factor['variation']})
  • 변동폭: {factor['total_range']:.2f}억원
  • 음의 영향: {factor['impact_negative']:.2f}억원
  • 양의 영향: {factor['impact_positive']:.2f}억원
"""
    
    report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 해석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{tornado['interpretation']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return report


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO)
    
    analyzer = SensitivityAnalyzer()
    
    result = analyzer.analyze_comprehensive(
        base_capex=30000000000,  # 300억
        base_appraisal_rate=0.92,
        market_land_value=24200000000,  # 242억
        gross_floor_area=2200
    )
    
    print(format_sensitivity_report(result))
