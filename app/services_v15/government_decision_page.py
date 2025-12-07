"""
ZeroSite v15 Phase 2 - Government Decision Page Generator
==========================================================

1-Page Executive Summary for Government Decision-Makers

Purpose: Distill 100-page report into 1-page actionable summary
Output: High-density decision page with key metrics and recommendations

Sections:
1. Project Overview (3 lines)
2. GO/NO-GO Decision (prominent)
3. Key Financial Metrics (4 KPIs)
4. Risk Assessment (traffic light)
5. Approval Probability
6. 3-Scenario Comparison
7. Immediate Actions Required
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class GovernmentDecisionPageGenerator:
    """Generate 1-page executive decision summary"""
    
    def generate_decision_page(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive 1-page decision summary"""
        logger.info("📄 Generating Government Decision Page...")
        
        # Extract all necessary data
        site = context.get('site', {})
        finance = context.get('finance', {})
        demand = context.get('demand', {})
        market = context.get('market', {})
        
        # Get v15 Phase 2 data
        simulation = context.get('v15_simulation', {})
        sensitivity = context.get('v15_sensitivity', {})
        approval_model = context.get('v15_approval', {})
        
        # Build decision page
        return {
            'project_overview': self._generate_overview(site, demand),
            'decision_banner': self._generate_decision_banner(finance, approval_model),
            'key_metrics': self._generate_key_metrics(finance, demand, market),
            'risk_dashboard': self._generate_risk_dashboard(sensitivity, simulation),
            'approval_assessment': self._extract_approval_info(approval_model),
            'scenario_comparison': self._extract_scenario_comparison(simulation),
            'immediate_actions': self._generate_immediate_actions(simulation, approval_model),
            'recommendation_box': self._generate_final_recommendation(
                finance, approval_model, simulation
            )
        }
    
    def _generate_overview(self, site: Dict, demand: Dict) -> Dict[str, str]:
        """Generate 3-line project overview"""
        address = site.get('address', '미정')
        land_area = site.get('land_area_sqm', 0)
        housing_type = demand.get('recommended_type_kr', demand.get('recommended_type', '청년형'))
        units = demand.get('recommended_units', 0)
        
        return {
            'line1': f"📍 사업지: {address}",
            'line2': f"📏 대지면적: {land_area:.0f}㎡ ({land_area/3.3058:.0f}평)",
            'line3': f"🏠 제안 주택유형: {housing_type} {units}세대"
        }
    
    def _generate_decision_banner(self, finance: Dict, approval: Dict) -> Dict[str, Any]:
        """Generate prominent GO/NO-GO banner"""
        npv = finance.get('npv_public', 0)
        irr = finance.get('irr_public_pct', 0)
        approval_prob = approval.get('approval_probability', 0) if approval else 0
        
        # Decision logic
        if npv > 0 and isinstance(irr, (int, float)) and irr > 4.5 and approval_prob > 70:
            decision = "GO"
            decision_kr = "실행 권고"
            color = "#28a745"
            icon = "✓"
        elif npv > 0 and approval_prob > 60:
            decision = "CONDITIONAL"
            decision_kr = "조건부 실행"
            color = "#ffc107"
            icon = "⚠"
        else:
            decision = "NO-GO"
            decision_kr = "재검토 권고"
            color = "#dc3545"
            icon = "✗"
        
        return {
            'decision': decision,
            'decision_kr': decision_kr,
            'color': color,
            'icon': icon,
            'confidence': f"{approval_prob:.0f}%" if approval else "N/A"
        }
    
    def _generate_key_metrics(self, finance: Dict, demand: Dict, market: Dict) -> List[Dict]:
        """Generate 4 key metrics for dashboard"""
        npv = finance.get('npv_public', 0) / 100_000_000
        irr = finance.get('irr_public_pct', 0)
        demand_score = demand.get('overall_score', 0)
        market_signal = market.get('signal', 'N/A')
        
        return [
            {
                'label': 'NPV (공공)',
                'value': f"{npv:.0f}",
                'unit': '억원',
                'status': 'good' if npv > 0 else 'bad'
            },
            {
                'label': 'IRR (공공)',
                'value': f"{irr:.1f}" if isinstance(irr, (int, float)) else 'N/A',
                'unit': '%',
                'status': 'good' if isinstance(irr, (int, float)) and irr > 4.5 else 'bad'
            },
            {
                'label': '수요 점수',
                'value': f"{demand_score:.0f}",
                'unit': '/100',
                'status': 'good' if demand_score > 70 else 'medium' if demand_score > 60 else 'bad'
            },
            {
                'label': '시장 신호',
                'value': market_signal,
                'unit': '',
                'status': 'good' if market_signal == 'UNDERVALUED' else 'medium'
            }
        ]
    
    def _generate_risk_dashboard(self, sensitivity: Dict, simulation: Dict) -> Dict[str, Any]:
        """Generate traffic-light risk dashboard"""
        if not sensitivity or not simulation:
            return {'level': 'UNKNOWN', 'color': '#6c757d'}
        
        # Get risk indicators
        sensitivity_risk = sensitivity.get('interpretation', {}).get('risk_level', 'MEDIUM')
        simulation_metrics = simulation.get('decision_metrics', {})
        downside_risk = simulation_metrics.get('downside_risk', 0) if simulation_metrics else 0
        
        # Combined risk assessment
        if sensitivity_risk == 'HIGH' or downside_risk > 0.25:
            level = 'HIGH'
            level_kr = '높음'
            color = '#dc3545'
        elif sensitivity_risk == 'MEDIUM' or downside_risk > 0.15:
            level = 'MEDIUM'
            level_kr = '중간'
            color = '#ffc107'
        else:
            level = 'LOW'
            level_kr = '낮음'
            color = '#28a745'
        
        return {
            'level': level,
            'level_kr': level_kr,
            'color': color,
            'downside_risk_pct': f"{downside_risk * 100:.0f}%"
        }
    
    def _extract_approval_info(self, approval: Dict) -> Dict[str, Any]:
        """Extract approval probability info"""
        if not approval:
            return {
                'probability': 0,
                'probability_pct': 'N/A',
                'level': 'UNKNOWN',
                'level_kr': '미산출'
            }
        
        return {
            'probability': approval.get('approval_probability', 0),
            'probability_pct': approval.get('probability_pct', 'N/A'),
            'level': approval.get('interpretation', {}).get('level', 'UNKNOWN'),
            'level_kr': approval.get('interpretation', {}).get('level_kr', '미정'),
            'color': approval.get('interpretation', {}).get('color', '#6c757d')
        }
    
    def _extract_scenario_comparison(self, simulation: Dict) -> List[Dict]:
        """Extract 3-scenario comparison"""
        if not simulation or 'scenarios' not in simulation:
            return []
        
        scenarios = simulation['scenarios']
        comparison = []
        
        for key in ['base', 'optimistic', 'pessimistic']:
            if key in scenarios:
                s = scenarios[key]
                comparison.append({
                    'name': s.get('name_kr', key.upper()),
                    'probability': f"{s.get('probability', 0) * 100:.0f}%",
                    'npv_krw': s.get('npv', {}).get('value_krw', 0),
                    'irr': s.get('irr', {}).get('percentage', 0)
                })
        
        return comparison
    
    def _generate_immediate_actions(
        self,
        simulation: Dict,
        approval: Dict
    ) -> List[str]:
        """Generate top 3 immediate actions"""
        actions = []
        
        # From simulation recommendation
        if simulation and 'recommendation' in simulation:
            sim_actions = simulation['recommendation'].get('key_actions', [])
            actions.extend(sim_actions[:2])
        
        # From approval recommendations
        if approval and 'recommendation' in approval:
            approval_actions = approval.get('recommendation', [])
            if isinstance(approval_actions, list):
                actions.extend(approval_actions[:1])
        
        # Default actions if none provided
        if not actions:
            actions = [
                'LH 협의 개시',
                '재무 구조 최적화',
                '위험 관리 계획 수립'
            ]
        
        return actions[:3]
    
    def _generate_final_recommendation(
        self,
        finance: Dict,
        approval: Dict,
        simulation: Dict
    ) -> Dict[str, str]:
        """Generate final recommendation box"""
        npv = finance.get('npv_public', 0)
        approval_prob = approval.get('approval_probability', 0) if approval else 0
        
        if npv > 0 and approval_prob > 75:
            title = "✅ 즉시 실행 권고"
            message = "모든 지표가 양호합니다. LH 협의를 즉시 개시하십시오."
            color = "#28a745"
        elif npv > 0 and approval_prob > 60:
            title = "⚠️ 조건부 실행 권고"
            message = "조건 충족 시 실행 가능합니다. 위험 관리 계획을 수립하십시오."
            color = "#ffc107"
        else:
            title = "❌ 재검토 권고"
            message = "현재 구조로는 승인 가능성이 낮습니다. 구조 개선이 필요합니다."
            color = "#dc3545"
        
        return {
            'title': title,
            'message': message,
            'color': color
        }


_gov_decision_page_generator = None

def get_government_decision_page_generator() -> GovernmentDecisionPageGenerator:
    """Get singleton instance"""
    global _gov_decision_page_generator
    if _gov_decision_page_generator is None:
        _gov_decision_page_generator = GovernmentDecisionPageGenerator()
    return _gov_decision_page_generator
