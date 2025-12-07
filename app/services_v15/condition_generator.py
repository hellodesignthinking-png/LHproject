"""
Condition Generator for ZeroSite v15 Phase 1
Generates C1-C4 condition table for CONDITIONAL-GO decisions

Purpose:
- Define specific conditions for policy approval
- Assign responsibility and timeline
- Link to policy requirements and financial impact

Author: ZeroSite Development Team
Date: 2025-12-07
Version: v15 Phase 1
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ConditionGenerator:
    """
    Generates condition table (C1-C4) for CONDITIONAL-GO decisions
    
    Each condition includes:
    - ID: C1, C2, C3, C4
    - Description: What needs to happen
    - Responsible: Who is accountable
    - Timeline: When it should be completed
    - Policy Link: Related policy framework
    - Impact: Expected financial/policy impact
    """
    
    def __init__(self):
        self.condition_templates = self._init_condition_templates()
    
    def _init_condition_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize condition templates based on common LH requirements"""
        return {
            'financing': {
                'id': 'C1',
                'title': '정책금융 적용',
                'description': 'LH 공급금융 2.62% 적용',
                'responsible': 'LH 한국토지주택공사',
                'timeline': '사업 승인 즉시',
                'policy_link': 'LH 신축매입임대 금융지원 지침',
                'impact': 'IRR +0.8%p, NPV +8~12억원',
                'priority': 'HIGH',
                'verification': 'LH 금융약정서'
            },
            'appraisal': {
                'id': 'C2',
                'title': '감정평가 기준 적용',
                'description': '감정평가 92% 룰 (공사비 연동형)',
                'responsible': '공인 감정평가사',
                'timeline': '착공 60일 전',
                'policy_link': '감정평가에 관한 규칙 제10조',
                'impact': 'NPV +6~10억원, 매입가 안정화',
                'priority': 'HIGH',
                'verification': '감정평가서'
            },
            'cost_optimization': {
                'id': 'C3',
                'title': 'CAPEX 절감',
                'description': 'CAPEX 15% 절감 (VE 적용)',
                'responsible': '시공사 / 설계사',
                'timeline': '기본설계 단계',
                'policy_link': 'LH Value Engineering 가이드라인',
                'impact': 'NPV +10~15억원, IRR +1.2%p',
                'priority': 'MEDIUM',
                'verification': 'VE 보고서'
            },
            'housing_type': {
                'id': 'C4',
                'title': '공급대상 유형 확정',
                'description': '청년/신혼부부형 공급 (정책 우선순위)',
                'responsible': '지자체 / LH',
                'timeline': '사전협의 단계',
                'policy_link': '제4차 장기 공공주택 종합계획',
                'impact': '정책 점수 +15점, 사회적 ROI +0.3%',
                'priority': 'MEDIUM',
                'verification': '사업계획서'
            }
        }
    
    def generate(self, context: Dict[str, Any], decision_tree: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate condition table based on decision tree
        
        Args:
            context: Report context
            decision_tree: Decision tree output
            
        Returns:
            List of condition dicts (C1-C4)
        """
        logger.info("Generating condition table...")
        
        # Only generate if CONDITIONAL-GO
        policy_decision = decision_tree.get('policy', {}).get('decision', '')
        if policy_decision != 'CONDITIONAL-GO':
            logger.info(f"No conditions needed for decision: {policy_decision}")
            return []
        
        # Select conditions based on gaps
        gaps = decision_tree.get('gaps', [])
        conditions = self._select_conditions(gaps, context)
        
        # Customize conditions based on context
        conditions = self._customize_conditions(conditions, context, decision_tree)
        
        logger.info(f"Generated {len(conditions)} conditions")
        
        return conditions
    
    def _select_conditions(self, gaps: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Select which conditions to include based on financial gaps
        
        Priority:
        1. C1 (Financing) - Always include if CONDITIONAL-GO
        2. C2 (Appraisal) - Include if NPV gap exists
        3. C3 (Cost) - Include if CAPEX is high or IRR gap exists
        4. C4 (Housing Type) - Include if demand target is youth/newlyweds
        """
        conditions = []
        
        # C1: Always include for CONDITIONAL-GO
        conditions.append(self.condition_templates['financing'].copy())
        
        # C2: Include if NPV gap
        if any(g['metric'] == 'NPV' for g in gaps):
            conditions.append(self.condition_templates['appraisal'].copy())
        
        # C3: Include if IRR gap or high CAPEX
        finance = context.get('finance', {})
        capex = finance.get('capex', {}).get('total_krw', 0)
        if any(g['metric'] == 'IRR' for g in gaps) or capex > 200:
            conditions.append(self.condition_templates['cost_optimization'].copy())
        
        # C4: Include if housing type is youth/newlyweds
        demand = context.get('demand', {})
        housing_type = demand.get('recommended_type', '')
        if housing_type in ['youth', 'newlyweds']:
            conditions.append(self.condition_templates['housing_type'].copy())
        
        return conditions
    
    def _customize_conditions(
        self, 
        conditions: List[Dict[str, Any]], 
        context: Dict[str, Any],
        decision_tree: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Customize condition details based on specific project context
        """
        finance = context.get('finance', {})
        demand = context.get('demand', {})
        gaps = decision_tree.get('gaps', [])
        
        for condition in conditions:
            cid = condition['id']
            
            # Customize C1 (Financing)
            if cid == 'C1':
                current_irr = decision_tree.get('metrics', {}).get('irr', 0)
                if current_irr < 0:
                    condition['description'] = 'LH 공급금융 2.62% 적용 (현재: 민간 PF 4.5%)'
                    condition['impact'] = 'IRR 음수 → 양수 전환 가능, NPV +10~15억원'
            
            # Customize C2 (Appraisal)
            if cid == 'C2':
                npv_gap = next((g for g in gaps if g['metric'] == 'NPV'), None)
                if npv_gap:
                    gap_amount = npv_gap.get('gap', '').replace('억원 필요', '').replace('+', '')
                    condition['description'] = f'감정평가 92% 룰 적용 (예상 상향: {gap_amount}억원)'
            
            # Customize C3 (Cost Optimization)
            if cid == 'C3':
                capex = finance.get('capex', {}).get('total_krw', 1000)
                target_reduction = capex * 0.15
                condition['description'] = f'CAPEX 15% 절감 (목표: {target_reduction:.0f}억원 ↓)'
            
            # Customize C4 (Housing Type)
            if cid == 'C4':
                housing_type_kr = demand.get('recommended_type_kr', demand.get('recommended_type', '청년형'))
                condition['description'] = f'{housing_type_kr} 공급 (정책 우선순위 부합)'
                demand_score = demand.get('overall_score', 0)
                condition['impact'] = f'정책 점수 +15점 (현재: {demand_score:.1f}점), 사회적 IRR +0.3%p'
        
        return conditions
    
    def generate_summary(self, conditions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary of conditions for executive display
        
        Returns:
            Summary dict with:
            - total_conditions: Number of conditions
            - high_priority_count: Number of HIGH priority conditions
            - responsible_parties: List of responsible organizations
            - timeline_summary: Key timeline milestones
        """
        if not conditions:
            return {
                'total_conditions': 0,
                'high_priority_count': 0,
                'responsible_parties': [],
                'timeline_summary': '조건 없음'
            }
        
        high_priority = [c for c in conditions if c.get('priority') == 'HIGH']
        responsible_parties = list(set(c.get('responsible', '') for c in conditions))
        
        # Timeline summary
        timelines = [c.get('timeline', '') for c in conditions]
        earliest = min(timelines, key=lambda x: self._timeline_to_days(x))
        
        return {
            'total_conditions': len(conditions),
            'high_priority_count': len(high_priority),
            'responsible_parties': responsible_parties,
            'timeline_summary': f'{earliest}부터 순차 충족',
            'expected_impact': self._calculate_total_impact(conditions)
        }
    
    def _timeline_to_days(self, timeline: str) -> int:
        """Convert timeline string to approximate days for sorting"""
        timeline_map = {
            '즉시': 0,
            '사전': 10,
            '60일': 60,
            '기본설계': 90,
            '착공': 180
        }
        
        for key, days in timeline_map.items():
            if key in timeline:
                return days
        
        return 999
    
    def _calculate_total_impact(self, conditions: List[Dict[str, Any]]) -> str:
        """Calculate estimated total impact of all conditions"""
        # Extract NPV and IRR impacts
        npv_impacts = []
        irr_impacts = []
        
        for condition in conditions:
            impact = condition.get('impact', '')
            
            # Parse NPV impact (e.g., "NPV +8~12억원")
            if 'NPV' in impact:
                import re
                match = re.search(r'(\d+)~(\d+)억원', impact)
                if match:
                    avg_npv = (int(match.group(1)) + int(match.group(2))) / 2
                    npv_impacts.append(avg_npv)
            
            # Parse IRR impact (e.g., "IRR +0.8%p")
            if 'IRR' in impact:
                import re
                match = re.search(r'(\d+\.?\d*)%p', impact)
                if match:
                    irr_impacts.append(float(match.group(1)))
        
        total_npv = sum(npv_impacts)
        total_irr = sum(irr_impacts)
        
        if total_npv > 0 and total_irr > 0:
            return f"예상 개선: NPV +{total_npv:.0f}억원, IRR +{total_irr:.1f}%p"
        elif total_npv > 0:
            return f"예상 개선: NPV +{total_npv:.0f}억원"
        elif total_irr > 0:
            return f"예상 개선: IRR +{total_irr:.1f}%p"
        else:
            return "정책 목적 부합"


# Export
__all__ = ['ConditionGenerator']
