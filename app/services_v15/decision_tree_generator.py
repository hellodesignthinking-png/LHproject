"""
Decision Tree Generator for ZeroSite v15 Phase 1
Generates transparent decision logic for government submission

Purpose:
- Visualize GO/NO-GO/CONDITIONAL decision structure
- Show reasoning for each path (민간/정책)
- Display conditions for approval

Author: ZeroSite Development Team
Date: 2025-12-07
Version: v15 Phase 1
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class DecisionTreeGenerator:
    """
    Generates decision tree structure showing:
    1. Private sector decision (민간)
    2. Policy decision (정책)
    3. Conditions for approval
    4. Financial thresholds
    """
    
    def __init__(self):
        self.thresholds = {
            'npv_positive': 0,
            'irr_minimum': 5.0,
            'payback_maximum': 15,
            'social_irr_minimum': 2.0,
            'demand_score_minimum': 60.0
        }
    
    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete decision tree structure
        
        Args:
            context: Report context with financial, demand, market data
            
        Returns:
            Dict containing:
            - private_decision: GO/NO-GO with reasons
            - policy_decision: GO/CONDITIONAL-GO/NO-GO with reasons
            - conditions_required: List of conditions if CONDITIONAL
            - financial_gaps: What needs to improve for GO
        """
        logger.info("Generating decision tree...")
        
        # Extract key metrics
        finance = context.get('finance', {})
        demand = context.get('demand', {})
        market = context.get('market', {})
        
        npv_value = self._extract_npv(finance)
        irr_value = self._extract_irr(finance)
        payback = self._extract_payback(finance)
        demand_score = demand.get('overall_score', 0)
        
        # Calculate social IRR (estimated)
        social_irr = self._estimate_social_irr(context)
        
        # Private sector decision
        private_decision = self._evaluate_private(npv_value, irr_value, payback)
        
        # Policy decision
        policy_decision = self._evaluate_policy(
            npv_value, irr_value, social_irr, demand_score, context
        )
        
        # Financial gaps
        gaps = self._calculate_gaps(npv_value, irr_value, payback)
        
        # Build tree structure
        tree = {
            'private': private_decision,
            'policy': policy_decision,
            'gaps': gaps,
            'thresholds': self.thresholds,
            'social_irr': social_irr,
            'metrics': {
                'npv': npv_value,
                'irr': irr_value,
                'payback': payback,
                'demand_score': demand_score
            }
        }
        
        logger.info(f"Decision tree generated: Private={private_decision['decision']}, Policy={policy_decision['decision']}")
        
        return tree
    
    def _extract_npv(self, finance: Dict[str, Any]) -> float:
        """Extract NPV value, handling validated negative cases"""
        npv = finance.get('npv_public_krw', 0)
        
        # Handle string case from validator ('<0')
        if isinstance(npv, str):
            return -999  # Indicator of negative case
        
        return npv if npv is not None else 0
    
    def _extract_irr(self, finance: Dict[str, Any]) -> float:
        """Extract IRR value, handling validated negative cases"""
        irr = finance.get('irr_public_pct', 0)
        
        # Handle string case from validator ('<0')
        if isinstance(irr, str) or irr is None:
            return -999  # Indicator of negative case
        
        return irr
    
    def _extract_payback(self, finance: Dict[str, Any]) -> float:
        """Extract payback period, handling 'Not achievable' cases"""
        payback = finance.get('payback_period_years', 999)
        
        # Handle string case from validator
        if isinstance(payback, str):
            return 999  # Indicator of not achievable
        
        return payback if payback is not None else 999
    
    def _estimate_social_irr(self, context: Dict[str, Any]) -> float:
        """
        Estimate social IRR based on policy value indicators
        
        Factors:
        - Housing supply to target demographic
        - Location accessibility
        - Policy alignment
        """
        demand = context.get('demand', {})
        
        # Base social IRR
        base_social_irr = 2.0
        
        # Boost if target is youth/newlyweds (high policy priority)
        housing_type = demand.get('recommended_type', '')
        if housing_type in ['youth', 'newlyweds']:
            base_social_irr += 0.3
        
        # Boost if high demand score
        demand_score = demand.get('overall_score', 0)
        if demand_score >= 70:
            base_social_irr += 0.2
        elif demand_score >= 60:
            base_social_irr += 0.1
        
        return round(base_social_irr, 2)
    
    def _evaluate_private(self, npv: float, irr: float, payback: float) -> Dict[str, Any]:
        """
        Evaluate from private sector perspective
        
        Rules:
        - GO if: NPV > 0 AND IRR >= 5% AND Payback <= 15 years
        - NO-GO otherwise
        """
        reasons = []
        
        # Check NPV
        if npv <= 0:
            reasons.append(f"NPV {npv:.1f}억원 (음수, 수익성 부족)")
        else:
            reasons.append(f"NPV {npv:.1f}억원 (양수)")
        
        # Check IRR
        if irr < 0:
            reasons.append("IRR <0% (음수 현금흐름)")
        elif irr < self.thresholds['irr_minimum']:
            reasons.append(f"IRR {irr:.2f}% (최소 기준 {self.thresholds['irr_minimum']}% 미달)")
        else:
            reasons.append(f"IRR {irr:.2f}% (양호)")
        
        # Check Payback
        if payback >= 100:
            reasons.append("회수기간 산출 불가")
        elif payback > self.thresholds['payback_maximum']:
            reasons.append(f"회수기간 {payback:.1f}년 (기준 {self.thresholds['payback_maximum']}년 초과)")
        else:
            reasons.append(f"회수기간 {payback:.1f}년 (적정)")
        
        # Decision
        if npv > 0 and irr >= self.thresholds['irr_minimum'] and payback <= self.thresholds['payback_maximum']:
            decision = 'GO'
            summary = "민간 사업성 확보 - 즉시 실행 가능"
        else:
            decision = 'NO-GO'
            summary = "민간 사업성 부족 - 민간 투자 불가"
        
        return {
            'decision': decision,
            'reasons': reasons,
            'summary': summary
        }
    
    def _evaluate_policy(
        self, npv: float, irr: float, social_irr: float, 
        demand_score: float, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate from policy (LH) perspective
        
        Rules:
        - GO if: Private GO (already profitable)
        - CONDITIONAL-GO if: Private NO-GO BUT social_irr >= 2.0% AND demand >= 60
        - NO-GO otherwise
        """
        reasons = []
        
        # Check if private is already GO
        if npv > 0 and irr >= self.thresholds['irr_minimum']:
            return {
                'decision': 'GO',
                'reasons': ['민간 사업성 확보'],
                'summary': '민간 사업 진행 권장',
                'conditions': []
            }
        
        # Check policy viability
        policy_viable = (
            social_irr >= self.thresholds['social_irr_minimum'] and
            demand_score >= self.thresholds['demand_score_minimum']
        )
        
        if policy_viable:
            reasons.append(f"사회적 IRR {social_irr:.1}% (기준 {self.thresholds['social_irr_minimum']}% 충족)")
            reasons.append(f"수요 점수 {demand_score:.1f}점 (기준 {self.thresholds['demand_score_minimum']}점 충족)")
            reasons.append("주거복지 정책 목적 부합")
            
            return {
                'decision': 'CONDITIONAL-GO',
                'reasons': reasons,
                'summary': 'LH 신축매입임대 사업으로 조건부 실행 가능',
                'conditions_required': True
            }
        else:
            reasons.append(f"사회적 IRR {social_irr:.1}% 미흡")
            reasons.append(f"수요 점수 {demand_score:.1f}점 미흡")
            
            return {
                'decision': 'NO-GO',
                'reasons': reasons,
                'summary': '정책 사업으로도 추진 불가 - 재검토 필요',
                'conditions_required': False
            }
    
    def _calculate_gaps(self, npv: float, irr: float, payback: float) -> List[Dict[str, Any]]:
        """
        Calculate what needs to improve for GO decision
        
        Returns list of gaps with improvement targets
        """
        gaps = []
        
        # NPV gap
        if npv <= 0:
            required_improvement = abs(npv) + 10  # Need to be positive + 10억 buffer
            gaps.append({
                'metric': 'NPV',
                'current': f"{npv:.1f}억원",
                'target': "0억원 이상",
                'gap': f"+{required_improvement:.1f}억원 필요",
                'methods': [
                    'CAPEX 15% 절감 (토지비/건축비)',
                    '임대료 수익 10% 증대',
                    'LH 공급금융 2.62% 활용'
                ]
            })
        
        # IRR gap
        if irr < self.thresholds['irr_minimum']:
            irr_gap = self.thresholds['irr_minimum'] - irr
            gaps.append({
                'metric': 'IRR',
                'current': f"{irr:.2f}%" if irr > -100 else "<0%",
                'target': f"{self.thresholds['irr_minimum']}% 이상",
                'gap': f"+{irr_gap:.2f}%p 필요",
                'methods': [
                    '감정평가 92% 룰 적용',
                    '공사비 Value Engineering',
                    '운영 효율화 (공실률 ↓)'
                ]
            })
        
        # Payback gap
        if payback > self.thresholds['payback_maximum'] and payback < 100:
            payback_gap = payback - self.thresholds['payback_maximum']
            gaps.append({
                'metric': '회수기간',
                'current': f"{payback:.1f}년",
                'target': f"{self.thresholds['payback_maximum']}년 이내",
                'gap': f"{payback_gap:.1f}년 단축 필요",
                'methods': [
                    '초기 현금흐름 개선',
                    '분양전환 옵션 검토',
                    '운영비 절감'
                ]
            })
        
        return gaps


# Export
__all__ = ['DecisionTreeGenerator']
