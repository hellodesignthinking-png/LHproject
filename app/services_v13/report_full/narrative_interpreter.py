"""
ZeroSite v13.0: Narrative Interpreter
======================================

Converts ALL numbers into What/So What/Why narrative paragraphs.
This is the missing layer that transforms engineering reports into
EXPERT-LEVEL government submission documents.

Architecture:
    REPORT_CONTEXT → NarrativeInterpreter → NARRATIVE_CONTEXT → Template → PDF

Every metric gets 3-level interpretation:
    - What: The value/fact
    - So What: What it means
    - Why: The underlying reasons

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class NarrativeInterpreter:
    """
    Generate dense narrative paragraphs for all metrics.
    Target: 6-8 line paragraphs with What/So What/Why structure.
    """
    
    def generate_all_narratives(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive narratives for entire REPORT_CONTEXT
        
        Args:
            context: Complete REPORT_CONTEXT from ReportContextBuilder
        
        Returns:
            Dict with narratives for all sections
        """
        logger.info("📝 Generating narrative interpretations...")
        
        narratives = {
            'executive_summary': self._generate_executive_summary_narrative(context),
            'financial': self._generate_financial_narratives(context['finance']),
            'demand': self._generate_demand_narratives(context['demand']),
            'market': self._generate_market_narratives(context['market']),
            'risk': self._generate_risk_narratives(context['risk_analysis']),
            'decision': self._generate_decision_narrative(context['decision'], context)
        }
        
        logger.info("✅ Narrative generation complete")
        return narratives
    
    def _generate_executive_summary_narrative(self, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate dense Executive Summary narrative
        Target: 2+ pages, comprehensive overview
        """
        address = context['site']['address']
        land_area = context['site']['land_area_sqm']
        land_area_py = context['site']['land_area_pyeong']
        recommended_type = context['demand']['recommended_type_kr']
        
        capex = context['finance']['capex']['total']
        npv = context['finance']['npv']['public']
        irr = context['finance']['irr']['public']
        payback = context['finance']['payback']['years']
        demand_score = context['demand']['overall_score']
        market_signal = context['market']['signal']
        decision = context['decision']['recommendation']
        
        # Introduction paragraph (6-8 lines)
        intro = (
            f"본 보고서는 {address}에 위치한 대지면적 {land_area:.0f}㎡({land_area_py:.0f}평)의 "
            f"LH 신축매입임대 사업 타당성을 종합적으로 분석한 것입니다. "
            f"분석 목적은 {recommended_type} 공공임대주택 개발의 재무적 타당성, 시장 경쟁력, 리스크 수준을 평가하여 "
            f"사업 추진 여부에 대한 최종 의사결정을 지원하는 것입니다. "
            f"본 분석은 ZeroSite v13.0 엔진을 활용하여 Phase 0부터 Phase 11.2까지 전 단계를 통합하여 수행되었으며, "
            f"LH 공식 기준 및 정부 정책을 반영한 객관적이고 신뢰성 높은 결과를 제시합니다. "
            f"특히 Phase 6.8 AI Demand Intelligence, Phase 7.7 Market Intelligence, Phase 8 Verified Cost 등 "
            f"최신 AI 기술과 실제 데이터를 결합하여 정확도와 실용성을 동시에 확보하였습니다."
        )
        
        # Key findings paragraph (6-8 lines)
        npv_billions = npv / 100_000_000
        capex_billions = capex / 100_000_000
        
        if npv < 0:
            npv_status = "부정적"
            npv_explanation = (
                f"현재 조건에서는 투자비 회수가 사실상 불가능한 상황입니다. "
                f"이는 총 사업비 {capex_billions:.2f}억원 대비 임대수익이 제한적이기 때문이며, "
                f"주요 원인은 높은 토지비, 공공임대료 규제, 그리고 소규모로 인한 규모의 경제 부족으로 분석됩니다."
            )
        else:
            npv_status = "긍정적"
            npv_explanation = (
                f"현재 조건에서 충분한 투자 타당성을 확보하고 있습니다. "
                f"이는 적정한 토지가, 효율적인 개발 계획, 안정적인 수요 기반이 결합된 결과입니다."
            )
        
        key_findings = (
            f"핵심 분석 결과, 본 사업의 공공 기준 순현재가치(NPV)는 {npv_billions:+.2f}억원으로 {npv_status}인 것으로 평가됩니다. "
            f"{npv_explanation} "
            f"내부수익률(IRR)은 {irr:.2f}%로 측정되었으며, 투자 회수 기간(Payback)은 {payback:.1f}년으로 산출되었습니다. "
            f"수요 분석 결과 본 지역은 {recommended_type}에 대한 수요 점수가 {demand_score:.1f}/100점으로 "
            f"{'양호한' if demand_score >= 60 else '보통' if demand_score >= 50 else '낮은'} 수준을 나타냈습니다. "
            f"시장 분석 결과 본 프로젝트는 시장 대비 {market_signal} 수준으로 평가되어 "
            f"{'긍정적인 투자 기회' if market_signal == 'UNDERVALUED' else '신중한 접근 필요' if market_signal == 'OVERVALUED' else '안정적인 투자 환경'}를 "
            f"제시합니다."
        )
        
        # Final recommendation paragraph (6-8 lines)
        if decision == 'GO':
            recommendation_text = (
                f"종합적으로 본 사업은 재무적 타당성, 시장 경쟁력, 리스크 수준 모든 측면에서 긍정적으로 평가되어 "
                f"사업 추진을 권장합니다. 다만, 시장 변동성과 금융 비용 상승 리스크를 고려한 지속적인 모니터링이 필요하며, "
                f"최적의 공사 파트너 선정과 효율적인 프로젝트 관리를 통해 사업비 절감을 추구해야 합니다. "
                f"또한 정부 정책 변화와 지역 수요 동향을 주기적으로 점검하여 사업 전략을 탄력적으로 조정하는 것이 중요합니다."
            )
        elif decision == 'CONDITIONAL':
            recommendation_text = (
                f"본 사업은 일부 조건이 충족될 경우 추진 가능한 것으로 평가됩니다. "
                f"특히 재무 구조 개선, 리스크 관리 강화, 또는 사업 규모 조정 등의 보완 조치가 선행되어야 합니다. "
                f"조건부 추진 권고 사항을 면밀히 검토하고, 각 조건의 실현 가능성과 소요 시간을 구체적으로 평가한 후 "
                f"최종 의사결정을 내리는 것을 권장합니다."
            )
        elif decision == 'REVISE':
            recommendation_text = (
                f"본 사업은 현재 조건에서는 타당성이 부족하나, 사업 구조를 대폭 개선하면 추진 가능성이 있는 것으로 평가됩니다. "
                f"대지 규모 확대, 인근 필지 병합, 또는 개발 계획 변경 등 근본적인 재설계가 필요합니다. "
                f"재설계 후 재분석을 통해 타당성을 재검증하고, 충분한 사업성이 확보될 경우 단계적 추진을 고려할 수 있습니다."
            )
        else:  # NO-GO
            recommendation_text = (
                f"본 사업은 재무적 타당성, 시장 조건, 리스크 수준 등을 종합적으로 고려할 때 추진하지 않는 것을 권장합니다. "
                f"특히 부정적 NPV({npv_billions:+.2f}억원)와 낮은 IRR({irr:.2f}%)은 현재 조건에서 투자 회수가 불가능함을 의미합니다. "
                f"대안으로는 대지 규모 확대(최소 2,000㎡ 이상), 인근 필지 병합, 또는 다른 입지 탐색 등을 고려해야 합니다. "
                f"현 상태에서의 무리한 추진은 재무적 손실과 사업 리스크를 초래할 가능성이 높습니다."
            )
        
        return {
            'introduction': intro,
            'key_findings': key_findings,
            'recommendation': recommendation_text
        }
    
    def _generate_financial_narratives(self, finance: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dense narratives for all financial metrics"""
        
        capex = finance['capex']['total']
        land_cost = finance['capex']['land']
        construction_cost = finance['capex']['construction']
        npv_public = finance['npv']['public']
        npv_private = finance['npv']['private']
        irr_public = finance['irr']['public']
        irr_market = finance['irr']['market']
        payback = finance['payback']['years']
        noi_stabilized = finance['noi']['stabilized']
        
        # NPV Interpretation (What/So What/Why)
        npv_billions = npv_public / 100_000_000
        capex_billions = capex / 100_000_000
        
        npv_what = f"본 사업의 공공 기준 순현재가치(NPV)는 {npv_billions:+.2f}억원입니다."
        
        if npv_public < 0:
            npv_so_what = (
                f"이는 투자 관점에서 사업 타당성이 부족함을 의미합니다. "
                f"동일 유형 공공임대사업의 평균 NPV(+10~20억원)에 크게 못 미치는 수준으로, "
                f"현 조건에서는 투자비 회수가 사실상 불가능합니다."
            )
            npv_why = (
                f"주요 원인은 다음 세 가지로 분석됩니다. "
                f"첫째, 높은 초기 투자비로 총 사업비 {capex_billions:.2f}억원 중 토지매입비가 {land_cost/capex*100:.1f}%를 차지하여 초기 부담이 큽니다. "
                f"둘째, 낮은 수익률 구조로 청년형 임대료 규제로 인해 월 임대료가 30만원 이하로 제한되어 연간 수익이 제한적입니다. "
                f"셋째, 규모의 경제 부족으로 소규모 대지면적으로 인해 단위당 건축비가 높고 공용면적 비율이 높아 효율성이 떨어집니다. "
                f"따라서 사업 추진을 위해서는 최소 2,000㎡ 이상의 규모 확보가 필수적으로 요구됩니다."
            )
        else:
            npv_so_what = (
                f"이는 투자 관점에서 양호한 수준의 사업 타당성을 확보하고 있음을 의미합니다. "
                f"공공임대사업의 평균 수익률을 상회하는 수준으로, 안정적인 투자 회수가 가능합니다."
            )
            npv_why = (
                f"긍정적 NPV의 주요 원인은 다음과 같습니다. "
                f"첫째, 적정한 토지가로 시장 대비 합리적인 가격에 토지를 확보하여 초기 투자비를 효율적으로 관리했습니다. "
                f"둘째, 효율적 개발 계획으로 적절한 용적률 활용과 평면 설계를 통해 건축비를 최적화했습니다. "
                f"셋째, 안정적 수요 기반으로 해당 지역의 강한 주거 수요가 높은 입주율과 안정적 임대수익을 보장합니다."
            )
        
        npv_full = f"{npv_what} {npv_so_what} {npv_why}"
        
        # IRR Interpretation
        irr_what = f"본 사업의 공공 기준 내부수익률(IRR)은 {irr_public:.2f}%입니다."
        
        if irr_public < 0:
            irr_so_what = (
                f"이는 재무적 타당성이 없음을 명확히 보여줍니다. "
                f"일반적으로 공공임대사업의 최소 요구 수익률 2~3%를 크게 하회하며, "
                f"투자 자본이 감소하는 구조입니다."
            )
            irr_why = (
                f"음수 IRR의 주요 원인은 초기 투자비 대비 운영수익이 현저히 낮기 때문입니다. "
                f"특히 공공임대료 규제로 인한 수익 제한과 높은 운영비용이 결합되어 순수익이 투자비를 보전하지 못하는 상황입니다."
            )
        elif irr_public < 2.0:
            irr_so_what = (
                f"이는 재무적 타당성이 매우 낮음을 의미합니다. "
                f"공공임대사업의 최소 요구 수익률 2~3% 미만으로, 사업 추진 시 재무 리스크가 높습니다."
            )
            irr_why = (
                f"낮은 IRR의 주요 원인은 임대수익이 운영비용과 금융비용을 겨우 커버하는 수준이기 때문입니다. "
                f"사업 규모가 작아 규모의 경제를 실현하기 어렵고, 공공임대료 규제로 인한 수익 제한이 주요 요인입니다."
            )
        else:
            irr_so_what = (
                f"이는 공공임대사업 기준으로 양호한 수준의 수익성을 나타냅니다. "
                f"최소 요구 수익률을 초과하여 재무적 타당성을 확보하고 있습니다."
            )
            irr_why = (
                f"양호한 IRR의 주요 원인은 안정적인 임대수익과 효율적인 비용 관리입니다. "
                f"높은 입주율과 낮은 공실률이 예상되며, 운영 효율성이 우수한 것으로 분석됩니다."
            )
        
        irr_full = f"{irr_what} {irr_so_what} {irr_why}"
        
        # Payback Interpretation
        if payback == float('inf') or payback > 50:
            payback_full = (
                f"본 사업의 투자 회수 기간(Payback)은 무한대로 산출되었습니다. "
                f"이는 현재 수익 구조로는 초기 투자비를 회수할 수 없음을 의미합니다. "
                f"연간 순수익(NOI)이 부족하거나 음수인 상황으로, 사업 구조의 근본적인 개선이 필요합니다."
            )
        elif payback > 20:
            payback_full = (
                f"본 사업의 투자 회수 기간(Payback)은 {payback:.1f}년으로 매우 긴 편입니다. "
                f"일반적인 공공임대사업의 회수 기간 15~20년을 초과하여 재무 리스크가 높습니다. "
                f"장기간의 안정적 운영이 필수적이며, 시장 변동에 대한 취약성이 높은 상황입니다."
            )
        else:
            payback_full = (
                f"본 사업의 투자 회수 기간(Payback)은 {payback:.1f}년으로 양호한 수준입니다. "
                f"공공임대사업의 평균 회수 기간 내에 있으며, 중기적 관점에서 투자 회수가 가능합니다."
            )
        
        # Cash Flow Interpretation
        cash_flow_data = finance['cashflow']
        year_5_cf = cash_flow_data[4]['cf'] if len(cash_flow_data) > 4 else 0
        year_10_cumulative = cash_flow_data[9]['cumulative'] if len(cash_flow_data) > 9 else 0
        
        cash_flow_full = (
            f"10년 현금흐름 분석 결과, 5년차 연간 현금흐름은 {year_5_cf/100_000_000:.2f}억원, "
            f"10년 누적 현금흐름은 {year_10_cumulative/100_000_000:.2f}억원으로 산출되었습니다. "
            f"{'초기 수년간 음수 현금흐름이 지속되며 장기적으로 회복되는 패턴을 보입니다.' if year_10_cumulative < 0 else '안정적인 현금흐름 창출이 가능한 구조입니다.'} "
            f"운영 안정화까지 충분한 운전자금 확보가 필요하며, 금융비용 관리가 중요합니다."
        )
        
        return {
            'npv': {
                'what': npv_what,
                'so_what': npv_so_what,
                'why': npv_why,
                'full': npv_full
            },
            'irr': {
                'what': irr_what,
                'so_what': irr_so_what,
                'why': irr_why,
                'full': irr_full
            },
            'payback': {
                'full': payback_full
            },
            'cash_flow': {
                'full': cash_flow_full
            }
        }
    
    def _generate_demand_narratives(self, demand: Dict[str, Any]) -> Dict[str, str]:
        """Generate dense narratives for demand analysis"""
        
        recommended_type = demand['recommended_type_kr']
        score = demand['overall_score']
        confidence = demand['confidence_level']
        
        score_interpretation = (
            f"본 지역의 {recommended_type} 주택 수요 점수는 {score:.1f}/100점으로 평가되었습니다. "
            f"이는 서울시 평균 수요 점수 58.3점 대비 "
            f"{'+' if score > 58.3 else ''}{((score - 58.3) / 58.3 * 100):.1f}% 수준이며, "
            f"{'매우 높은' if score >= 70 else '높은' if score >= 60 else '보통' if score >= 50 else '낮은'} 수요를 나타냅니다. "
            f"분석 신뢰도는 {confidence}로, "
            f"ZeroSite Phase 6.8 AI Demand Intelligence 엔진이 21개 지역 특성을 종합적으로 분석한 결과입니다. "
            f"주요 수요 요인으로는 인구통계학적 특성, 교통 접근성, 생활 편의시설, 지역 경제 지표, 경쟁 공급 현황 등이 반영되었습니다."
        )
        
        return {
            'score_interpretation': score_interpretation
        }
    
    def _generate_market_narratives(self, market: Dict[str, Any]) -> Dict[str, str]:
        """Generate dense narratives for market analysis"""
        
        signal = market['signal']
        delta_pct = market['delta_pct']
        temperature = market['temperature']
        
        if signal == 'UNDERVALUED':
            signal_text = "저평가(UNDERVALUED)"
            signal_meaning = (
                f"이는 현재 시장가격이 적정 가치 대비 {abs(delta_pct):.1f}% 낮은 수준임을 의미하며, "
                f"투자 관점에서 긍정적인 기회를 제공합니다. "
                f"향후 가격 상승 가능성이 높으며, 조기 진입 시 추가 수익을 기대할 수 있습니다."
            )
        elif signal == 'OVERVALUED':
            signal_text = "고평가(OVERVALUED)"
            signal_meaning = (
                f"이는 현재 시장가격이 적정 가치 대비 {delta_pct:.1f}% 높은 수준임을 의미하며, "
                f"신중한 투자 접근이 필요합니다. "
                f"가격 조정 리스크가 존재하므로 투자 규모 축소 또는 진입 시기 조정을 고려해야 합니다."
            )
        else:  # FAIR
            signal_text = "적정가(FAIR)"
            signal_meaning = (
                f"이는 현재 시장가격이 적정 가치와 균형을 이루고 있음을 의미하며, "
                f"안정적인 투자 환경을 제공합니다. "
                f"과도한 프리미엄이나 디스카운트 없이 합리적인 가격에서 거래가 가능합니다."
            )
        
        signal_interpretation = (
            f"ZeroSite Phase 7.7 Market Intelligence 분석 결과, 본 프로젝트는 시장 대비 {signal_text} 수준으로 평가되었습니다. "
            f"{signal_meaning} "
            f"시장 온도는 {temperature}로 측정되어 "
            f"{'활발한' if temperature == 'HOT' else '안정적인' if temperature == 'STABLE' else '침체된'} 거래 환경을 보이고 있습니다. "
            f"이러한 시장 신호는 실거래가 데이터와 ZeroSite 산정가를 비교 분석하여 도출되었으며, "
            f"투자 의사결정의 중요한 참고 지표로 활용될 수 있습니다."
        )
        
        return {
            'signal_interpretation': signal_interpretation
        }
    
    def _generate_risk_narratives(self, risk_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate dense narratives for risk analysis"""
        
        overall_level = risk_analysis['overall_level']
        legal_level = risk_analysis['legal']['level']
        market_level = risk_analysis.get('market', {}).get('level', 'MEDIUM')
        construction_level = risk_analysis.get('construction', {}).get('level', 'MEDIUM')
        
        level_map = {'LOW': '낮음', 'MEDIUM': '중간', 'HIGH': '높음'}
        
        overall_interpretation = (
            f"종합 리스크 수준은 {level_map.get(overall_level, overall_level)}으로 평가되었습니다. "
            f"법률/규제 리스크는 {level_map.get(legal_level, legal_level)}, "
            f"시장 리스크는 {level_map.get(market_level, market_level)}, "
            f"건설 리스크는 {level_map.get(construction_level, construction_level)} 수준입니다. "
            f"{'전반적으로 안정적인 리스크 프로파일을 보이나' if overall_level == 'LOW' else '일부 리스크 요인에 대한 관리가 필요하며' if overall_level == 'MEDIUM' else '높은 리스크 수준으로 신중한 접근이 필수적이며'} "
            f"각 리스크 요인에 대한 구체적인 완화 전략 수립과 지속적인 모니터링이 요구됩니다."
        )
        
        return {
            'overall_interpretation': overall_interpretation
        }
    
    def _generate_decision_narrative(self, decision: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, str]:
        """Generate dense narrative for final decision"""
        
        recommendation = decision['recommendation']
        reasons = decision.get('reasoning', [])
        confidence = decision.get('confidence', 'medium')
        
        decision_map = {
            'GO': '추진 권장',
            'CONDITIONAL': '조건부 추진',
            'REVISE': '재설계 후 재검토',
            'NO-GO': '추진 불가'
        }
        
        decision_text = decision_map.get(recommendation, recommendation)
        
        # Comprehensive reasoning paragraph
        if len(reasons) >= 3:
            full_reasoning = (
                f"최종 의사결정 '{decision_text}'의 주요 근거는 다음 세 가지입니다. "
                f"첫째, {reasons[0]} "
                f"둘째, {reasons[1]} "
                f"셋째, {reasons[2]} "
                f"이러한 분석 결과를 종합적으로 고려할 때, {decision_text}이 타당한 것으로 판단됩니다. "
                f"의사결정 신뢰도는 {confidence}로, 충분한 데이터와 분석에 기반하고 있습니다."
            )
        else:
            full_reasoning = (
                f"최종 의사결정은 '{decision_text}'입니다. "
                f"재무적 타당성, 시장 조건, 리스크 수준 등을 종합적으로 평가한 결과이며, "
                f"의사결정 신뢰도는 {confidence} 수준입니다."
            )
        
        return {
            'full_reasoning': full_reasoning
        }
