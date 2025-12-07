"""
Risk Response Generator for ZeroSite v15 Phase 1
Generates risk mitigation strategy matrix for government submission

Purpose:
- Map risks to specific mitigation strategies
- Link to policy support mechanisms
- Prioritize response actions
- Show proactive risk management

Author: ZeroSite Development Team
Date: 2025-12-07
Version: v15 Phase 1
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class RiskResponseGenerator:
    """
    Generates Risk → Response Matrix showing:
    1. Risk identification (from existing risk analysis)
    2. Mitigation strategy
    3. Policy support mechanism
    4. Responsible party
    5. Implementation timeline
    """
    
    def __init__(self):
        self.response_templates = self._init_response_templates()
    
    def _init_response_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize response strategy templates for common LH risks"""
        return {
            'financial_feasibility': {
                'risk': '재무 타당성',
                'description': 'NPV 음수, IRR 미달, 투자 회수 불확실',
                'impact': 'HIGH',
                'response': {
                    'strategy': 'LH 공급금융 2.62% 적용 + VE를 통한 CAPEX 15% 절감',
                    'actions': [
                        'LH 정책금융 사전 협의 및 약정',
                        'Value Engineering 전문가 자문',
                        '단계별 비용 최적화 (설계/시공)'
                    ]
                },
                'policy_support': 'LH 신축매입임대 금융지원 지침',
                'responsible': 'LH / 시공사',
                'timeline': '사업 초기 (착수~6개월)',
                'expected_outcome': 'NPV 양수 전환, IRR 5% 이상 달성'
            },
            'appraisal_risk': {
                'risk': '감정평가 하향',
                'description': '시장가 대비 낮은 감정평가로 매입가 부족',
                'impact': 'HIGH',
                'response': {
                    'strategy': '감정평가 92% 룰 적용 + 공사비 연동형 평가 요청',
                    'actions': [
                        'LH 감정평가 기준 사전 협의',
                        '공사비 산정 투명화 (견적서)',
                        '유사 사례 벤치마킹 자료 제출'
                    ]
                },
                'policy_support': '감정평가에 관한 규칙 제10조',
                'responsible': '감정평가사 / LH',
                'timeline': '착공 60일 전',
                'expected_outcome': '예상 매입가 92% 이상 확보'
            },
            'interest_rate': {
                'risk': '금리 상승',
                'description': '시장 금리 상승으로 인한 재무비용 증가',
                'impact': 'MEDIUM',
                'response': {
                    'strategy': 'LH 공급금융 고정금리 + 금리 헤지 상품 활용',
                    'actions': [
                        'LH 공급금융 우선 확보 (2.62% 고정)',
                        '민간 PF 비중 최소화',
                        '금리 스왑 또는 Cap 계약 검토'
                    ]
                },
                'policy_support': 'LH 공급금융 프로그램',
                'responsible': 'LH / 금융기관',
                'timeline': '사업 초기 (금융 약정 시)',
                'expected_outcome': '금융비용 고정, IRR 변동성 최소화'
            },
            'construction_cost': {
                'risk': '건설비 상승',
                'description': '자재비/인건비 상승으로 공사비 초과',
                'impact': 'MEDIUM',
                'response': {
                    'strategy': 'VE 적용 + LH 표준 자재 활용 + 고정가 계약',
                    'actions': [
                        'Value Engineering 통한 8~12% 절감',
                        'LH 표준 자재 리스트 활용',
                        '시공사 고정가 도급 계약',
                        '자재 선(先) 확보 전략'
                    ]
                },
                'policy_support': 'LH Value Engineering 가이드라인',
                'responsible': '시공사 / 설계사',
                'timeline': '설계 단계 (착수 후 3~6개월)',
                'expected_outcome': 'CAPEX 목표 범위 내 통제'
            },
            'permit_delay': {
                'risk': '인허가 지연',
                'description': '건축 심의/허가 지연으로 사업 일정 차질',
                'impact': 'MEDIUM',
                'response': {
                    'strategy': 'LH-지자체 협력 체계 + 사전 협의 강화',
                    'actions': [
                        'LH를 통한 지자체 사전 협의',
                        '건축심의 사전 검토 (전문가)',
                        '인허가 일정 Buffer 확보 (2개월)',
                        '조건부 계약 체결 (허가 전제)'
                    ]
                },
                'policy_support': 'LH-지자체 협력 프로그램',
                'responsible': '지자체 / LH',
                'timeline': '사업 초기~인허가 단계',
                'expected_outcome': '인허가 6개월 내 완료'
            },
            'rent_regulation': {
                'risk': '임대료 제한',
                'description': '임대료 규제 강화로 수익성 저하',
                'impact': 'LOW',
                'response': {
                    'strategy': '공공지원 주거복지 사업 구조 + 보조금 활용',
                    'actions': [
                        'LH 신축매입임대 프로그램 적용',
                        '주거복지 예산 연계 검토',
                        '운영효율화 (관리비 최소화)'
                    ]
                },
                'policy_support': '주거복지 로드맵 (국토부)',
                'responsible': 'LH / 국토부',
                'timeline': '운영 단계 (준공 후)',
                'expected_outcome': '임대료 규제 내에서 안정적 운영'
            },
            'market_downturn': {
                'risk': '시장 침체',
                'description': '부동산 시장 하락으로 자산가치 하락',
                'impact': 'LOW',
                'response': {
                    'strategy': 'LH 매입 확정 계약 + 장기 임대 구조',
                    'actions': [
                        'LH 조건부 매입 계약 사전 체결',
                        '시장 변동성 무관한 구조',
                        '30년 장기 임대로 안정성 확보'
                    ]
                },
                'policy_support': 'LH 신축매입임대 사업 매뉴얼',
                'responsible': 'LH',
                'timeline': '계약 단계',
                'expected_outcome': '시장 리스크 LH 이관'
            }
        }
    
    def generate(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate risk response matrix
        
        Args:
            context: Report context including risk_analysis
            
        Returns:
            List of risk response dicts sorted by impact (HIGH → MEDIUM → LOW)
        """
        logger.info("Generating risk response matrix...")
        
        # Get existing risks from context
        existing_risks = context.get('risk_analysis', {})
        
        # Map to response strategies
        risk_responses = self._map_risks_to_responses(existing_risks, context)
        
        # Sort by impact priority
        risk_responses = self._sort_by_priority(risk_responses)
        
        logger.info(f"Generated {len(risk_responses)} risk responses")
        
        return risk_responses
    
    def _map_risks_to_responses(
        self, 
        existing_risks: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Map existing risks to response strategies
        
        Strategy:
        1. Use existing risk categorization if available
        2. Otherwise, infer risks from context (finance, market, etc.)
        3. Apply appropriate response templates
        """
        responses = []
        
        # Check if we have enhanced risk analysis (from v13 risk enhancer)
        if 'enhanced' in existing_risks:
            top_risks = existing_risks['enhanced'].get('top_10_risks', [])
            for risk in top_risks[:5]:  # Top 5 only
                response = self._create_response_from_risk(risk, context)
                if response:
                    responses.append(response)
        
        # If no enhanced risks, use context-based inference
        if not responses:
            responses = self._infer_risks_from_context(context)
        
        # Ensure we have at least top 5 risks
        if len(responses) < 5:
            responses.extend(self._get_default_responses(5 - len(responses)))
        
        return responses[:5]  # Return top 5
    
    def _create_response_from_risk(self, risk: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create response structure from existing risk data"""
        risk_name = risk.get('name', '').lower()
        
        # Match to response template
        if '재무' in risk_name or 'financial' in risk_name:
            template = self.response_templates['financial_feasibility']
        elif '감정' in risk_name or 'appraisal' in risk_name:
            template = self.response_templates['appraisal_risk']
        elif '금리' in risk_name or 'interest' in risk_name:
            template = self.response_templates['interest_rate']
        elif '공사' in risk_name or 'construction' in risk_name:
            template = self.response_templates['construction_cost']
        elif '인허가' in risk_name or 'permit' in risk_name:
            template = self.response_templates['permit_delay']
        else:
            template = self.response_templates['financial_feasibility']  # Default
        
        return template.copy()
    
    def _infer_risks_from_context(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Infer risks from financial/market context"""
        responses = []
        
        finance = context.get('finance', {})
        market = context.get('market', {})
        
        # Financial risk (always include if NPV negative)
        npv = finance.get('npv_public_krw', 0)
        if npv <= 0:
            responses.append(self.response_templates['financial_feasibility'].copy())
        
        # Appraisal risk (always include for LH projects)
        responses.append(self.response_templates['appraisal_risk'].copy())
        
        # Interest rate risk (include if CAPEX is high)
        capex = finance.get('capex', {}).get('total_krw', 0)
        if capex > 150:
            responses.append(self.response_templates['interest_rate'].copy())
        
        # Construction cost risk (include if construction budget is significant)
        responses.append(self.response_templates['construction_cost'].copy())
        
        # Permit delay risk (always relevant for new construction)
        responses.append(self.response_templates['permit_delay'].copy())
        
        return responses
    
    def _get_default_responses(self, count: int) -> List[Dict[str, Any]]:
        """Get default responses to fill up to required count"""
        defaults = [
            self.response_templates['rent_regulation'].copy(),
            self.response_templates['market_downturn'].copy()
        ]
        return defaults[:count]
    
    def _sort_by_priority(self, responses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort responses by impact priority (HIGH → MEDIUM → LOW)"""
        priority_map = {'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        
        return sorted(
            responses, 
            key=lambda x: priority_map.get(x.get('impact', 'MEDIUM'), 2)
        )
    
    def generate_summary(self, risk_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary of risk mitigation approach
        
        Returns:
            Summary dict with:
            - total_risks: Number of risks addressed
            - high_risk_count: Number of HIGH impact risks
            - mitigation_coverage: % of risks with clear mitigation
            - policy_support_count: Number of policy-backed responses
        """
        if not risk_responses:
            return {
                'total_risks': 0,
                'high_risk_count': 0,
                'mitigation_coverage': '0%',
                'policy_support_count': 0
            }
        
        high_risks = [r for r in risk_responses if r.get('impact') == 'HIGH']
        policy_backed = [r for r in risk_responses if r.get('policy_support')]
        
        return {
            'total_risks': len(risk_responses),
            'high_risk_count': len(high_risks),
            'mitigation_coverage': '100%',  # All risks have responses
            'policy_support_count': len(policy_backed),
            'key_strategies': [r['response']['strategy'] for r in high_risks]
        }


# Export
__all__ = ['RiskResponseGenerator']
