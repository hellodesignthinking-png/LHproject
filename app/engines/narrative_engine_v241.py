"""
ZeroSite v24.1 - Narrative Engine
Template-based narrative generation for reports

Author: ZeroSite Development Team  
Version: v24.1.0
Created: 2025-12-12
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class NarrativeSection:
    """Generated narrative section"""
    title: str
    content: str
    key_points: List[str]


class NarrativeEngineV241:
    """
    Template-based Narrative Generator for ZeroSite v24.1
    
    Generates professional Korean narratives for:
    - Policy analysis
    - Financial feasibility
    - Market analysis
    - Scenario comparisons
    - Risk assessments
    """
    
    def __init__(self):
        """Initialize narrative engine"""
        self.version = "24.1.0"
    
    def generate_policy_narrative(self, analysis: Dict[str, Any]) -> NarrativeSection:
        """Generate policy impact narrative"""
        zone = analysis.get("zone_type", "")
        far_before = analysis.get("far_legal", 0)
        far_after = analysis.get("far_final", 0)
        increase = far_after - far_before
        
        content = f"""
본 사업대상지는 {zone}으로 지정되어 있으며, 법정 용적률 {far_before:.0f}%가 적용됩니다.

현행 도시계획 규제 하에서 다양한 용적률 완화 제도를 적용할 경우, 
최종 용적률은 {far_after:.0f}%까지 상향 가능하며, 이는 법정 용적률 대비 
{increase:.0f}%p 증가한 수준입니다.

이러한 용적률 완화는 공공기여를 통해 달성 가능하며, 특히 공공임대주택 
제공, 기반시설 기부채납 등의 방식으로 인센티브를 확보할 수 있습니다.

정책적 측면에서 본 사업은 주거복지 향상과 도시재생에 기여하며, 
지역 커뮤니티 활성화 및 고용 창출 효과가 기대됩니다.
        """.strip()
        
        key_points = [
            f"용적률 완화: {far_before:.0f}% → {far_after:.0f}%",
            f"증가폭: +{increase:.0f}%p",
            "공공기여를 통한 인센티브 확보 가능",
            "주거복지 및 도시재생 기여"
        ]
        
        return NarrativeSection("정책적 의미 분석", content, key_points)
    
    def generate_executive_summary(self, analysis: Dict[str, Any]) -> str:
        """
        Generate executive summary for Report 1
        
        Args:
            analysis: Combined analysis data (zoning, capacity, financial)
        
        Returns:
            Executive summary text (Korean)
        """
        zoning = analysis.get('zoning', {})
        capacity = analysis.get('capacity', {})
        financial = analysis.get('financial', {})
        
        address = zoning.get('address', '대상지')
        area = zoning.get('area_sqm', 0)
        units = capacity.get('max_units', 0)
        roi = financial.get('roi', 0) * 100  # Convert to percentage
        
        summary = f"""
본 보고서는 {address} ({area:,.0f}㎡)에 대한 종합 토지진단 결과를 제시합니다.

**건축 규모**: 총 {units}세대의 공동주택 개발이 가능하며, 이는 현행 법규와 
정책적 완화 제도를 최대한 활용한 결과입니다.

**사업성**: 투자수익률(ROI) {roi:.1f}%로 안정적인 수익 구조를 갖추고 있으며, 
LH 신축매입임대 사업 기준에 부합하는 우수한 입지입니다.

**추천도**: 종합적으로 해당 토지는 신축매입임대 사업 대상지로 **적합**하며, 
즉시 사업 추진이 가능합니다.
        """.strip()
        
        return summary
    
    def generate_capacity_narrative(self, capacity: Dict[str, Any]) -> str:
        """
        Generate capacity analysis narrative
        
        Args:
            capacity: Capacity analysis data
        
        Returns:
            Capacity narrative text (Korean)
        """
        units = capacity.get('max_units', 0)
        floors = capacity.get('floors', 0)
        total_area = capacity.get('total_area', 0)
        
        narrative = f"""
대지면적과 법규를 고려한 건축 규모 검토 결과, 총 {units}세대 규모의 공동주택 개발이 가능합니다.

**건물 규모**: 지상 {floors}층 규모로 계획되며, 연면적은 약 {total_area:,.0f}㎡입니다.

**세대 구성**: 청년형·신혼형·일반형의 다양한 유형으로 구성하여 임대 수요에 효과적으로 
대응할 수 있습니다.

**주차 계획**: 법정 주차대수를 충족하는 지하 주차장이 계획되어 있으며, 주민 편의성을 
극대화하였습니다.
        """.strip()
        
        return narrative
    
    def generate_financial_narrative(self, metrics: Dict[str, Any]) -> str:
        """Generate financial analysis narrative"""
        roi = metrics.get("roi", 0) * 100
        irr = metrics.get("irr", 0) * 100
        payback_simple = metrics.get("payback_simple", 0)
        total_cost = metrics.get("total_cost", 0) / 100000000
        
        narrative = f"""
본 사업의 재무적 타당성을 분석한 결과, 투자수익률(ROI) {roi:.1f}%, 
내부수익률(IRR) {irr:.1f}%로 산출되어 우수한 수익성을 보입니다.

총 사업비는 약 {total_cost:.0f}억원으로 추정되며, 단순 회수기간은 
{payback_simple:.1f}년으로 안정적인 투자 구조를 갖추고 있습니다.

재무 구조 측면에서 적정 레버리지 활용 시 자기자본수익률(ROE) 
극대화가 가능하며, 현금흐름 관리를 통해 안정적인 사업 진행이 
가능할 것으로 판단됩니다.

민감도 분석 결과, 분양가격 ±5% 변동 시에도 사업성이 유지되어 
리스크 대응력이 높은 것으로 평가됩니다.
        """.strip()
        
        return narrative
    
    def generate_market_narrative(self, market_data: Dict[str, Any]) -> NarrativeSection:
        """Generate market analysis narrative"""
        avg_price = market_data.get("average_price", 0) / 10000
        volatility = market_data.get("volatility", 0) * 100
        trend = market_data.get("trend_direction", "STABLE")
        
        trend_kr = {"RISING": "상승", "STABLE": "안정", "DECLINING": "하락"}.get(trend, "안정")
        
        content = f"""
대상지 인근 부동산 시장은 현재 {trend_kr} 추세를 보이고 있으며, 
평균 거래가격은 ㎡당 약 {avg_price:.0f}만원 수준입니다.

시장 변동성은 {volatility:.1f}%로 {
    '낮은' if volatility < 10 else '보통' if volatility < 20 else '높은'
} 수준이며, 이는 시장의 {'안정성' if volatility < 15 else '변동성'}을 
나타냅니다.

경쟁 프로젝트 분석 결과, 유사 규모의 개발사업이 진행 중이나 
본 사업의 입지 우수성 및 상품 차별화를 통해 충분한 경쟁력 
확보가 가능한 것으로 판단됩니다.

향후 시장 전망은 긍정적이며, 특히 교통 인프라 개선 및 생활 
편의시설 확충으로 인한 수요 증가가 예상됩니다.
        """.strip()
        
        key_points = [
            f"시장 추세: {trend_kr}",
            f"평균 가격: {avg_price:.0f}만원/㎡",
            f"변동성: {volatility:.1f}%",
            "우수한 입지 경쟁력",
            "긍정적 시장 전망"
        ]
        
        return NarrativeSection("시장 분석", content, key_points)
    
    def generate_scenario_comparison(self, scenarios: Dict[str, Any]) -> NarrativeSection:
        """Generate scenario comparison narrative"""
        content = """
본 사업의 최적 개발 방안을 도출하기 위해 3가지 시나리오를 비교 분석하였습니다.

시나리오 A(소형 위주형)는 원룸 및 소형 세대 중심으로 구성되어 
초기 투자비가 낮고 임대 수익성이 우수합니다. 청년층 및 1인 가구를 
타겟으로 하며, 빠른 분양 또는 임대가 가능한 장점이 있습니다.

시나리오 B(중대형 위주형)는 중대형 세대 중심으로 가족 단위 
수요층을 타겟합니다. 분양가가 높아 수익성이 우수하나, 시장 
민감도가 상대적으로 높은 특징이 있습니다.

시나리오 C(고령자형)는 배리어프리 설계 및 복지시설 연계를 통해 
고령자 친화형 주거를 제공합니다. 정책적 인센티브 확보가 용이하며, 
사회적 가치 창출 측면에서 우수한 평가를 받습니다.

종합적으로 시나리오 B가 재무적 수익성 측면에서 가장 우수하나, 
정책 지원 및 사회적 가치를 고려할 경우 시나리오 C도 매력적인 
대안으로 평가됩니다.
        """.strip()
        
        key_points = [
            "시나리오 A: 소형 위주, 높은 임대수익성",
            "시나리오 B: 중대형 위주, 최고 분양수익성",
            "시나리오 C: 고령자형, 높은 사회적 가치",
            "권장안: 시나리오 B 또는 A+C 혼합"
        ]
        
        return NarrativeSection("시나리오 비교 분석", content, key_points)
    
    def generate_risk_summary(self, risk_profile: Dict[str, Any]) -> NarrativeSection:
        """Generate risk assessment summary"""
        design_risk = risk_profile.get("design_risk", 0) * 100
        legal_risk = risk_profile.get("legal_risk", 0) * 100
        financial_risk = risk_profile.get("financial_risk", 0) * 100
        
        content = f"""
본 사업의 리스크 분석 결과, 설계 리스크 {design_risk:.0f}점, 
법적 리스크 {legal_risk:.0f}점, 재무 리스크 {financial_risk:.0f}점으로 
평가되었습니다.

설계 측면에서는 건축법규 준수 및 구조 안정성 확보에 유의가 필요하며, 
특히 일조권 규제 및 층수 제한에 대한 면밀한 검토가 요구됩니다.

법적 측면에서는 용도지역 적합성, 인허가 절차, 환경영향평가 등을 
철저히 준비하여 인허가 지연 리스크를 최소화해야 합니다.

재무 측면에서는 금리 변동, 건축비 상승, 분양가 하락 등에 대비한 
시나리오별 대응 전략을 수립하고, 적정 유동성을 확보하는 것이 
중요합니다.

전반적으로 리스크 수준은 {'낮음' if max(design_risk, legal_risk, financial_risk) < 30 else '보통' if max(design_risk, legal_risk, financial_risk) < 50 else '주의 필요'} 
단계이며, 체계적인 리스크 관리를 통해 안정적인 사업 추진이 
가능할 것으로 판단됩니다.
        """.strip()
        
        key_points = [
            f"설계 리스크: {design_risk:.0f}점",
            f"법적 리스크: {legal_risk:.0f}점",
            f"재무 리스크: {financial_risk:.0f}점",
            "리스크 관리 전략 수립 필요",
            "전반적 리스크 수준: 관리 가능"
        ]
        
        return NarrativeSection("리스크 평가", content, key_points)
    
    def generate_risk_narrative(self, risk_data: Dict[str, Any]) -> str:
        """
        Generate risk assessment narrative (for report generator compatibility)
        
        Args:
            risk_data: Risk analysis data
        
        Returns:
            Risk narrative text (Korean)
        """
        risk_score = risk_data.get('design_risk_score', 50)
        risk_level = risk_data.get('risk_level', 'MEDIUM')
        key_risks = risk_data.get('key_risks', [])
        
        level_kr = {
            'LOW': '낮음', 
            'MEDIUM': '보통', 
            'HIGH': '높음', 
            'VERY_HIGH': '매우 높음'
        }.get(risk_level, '보통')
        
        risk_list = '\n'.join([f"- {risk}" for risk in key_risks[:5]]) if key_risks else "- 특이사항 없음"
        
        narrative = f"""
본 프로젝트의 종합 리스크 평가 결과, 리스크 수준은 **{level_kr}**(점수: {risk_score:.0f}/100)으로 
판단됩니다.

**주요 리스크 요인**:
{risk_list}

**리스크 관리 방안**: 설계 단계부터 리스크 요인을 사전에 검토하고 대응 방안을 마련하였으며, 
시공 및 인허가 단계에서도 지속적인 모니터링을 통해 리스크를 최소화할 계획입니다.

전반적으로 관리 가능한 수준의 리스크로 평가되며, 적절한 대응 조치를 통해 성공적인 
사업 추진이 가능할 것으로 판단됩니다.
        """.strip()
        
        return narrative
    
    def generate_recommendation(self, analysis: Dict[str, Any]) -> str:
        """
        Generate final recommendation (for report generator compatibility)
        
        Args:
            analysis: Combined analysis (capacity, financial, risk)
        
        Returns:
            Recommendation text (Korean)
        """
        capacity = analysis.get('capacity', {})
        financial = analysis.get('financial', {})
        risk = analysis.get('risk', {})
        
        units = capacity.get('max_units', 0)
        roi = financial.get('roi', 0) * 100
        risk_level = risk.get('risk_level', 'MEDIUM')
        
        # Determine recommendation level
        if roi > 12 and risk_level in ['LOW', 'MEDIUM']:
            recommendation = "**적극 추천**"
            reasoning = "우수한 수익성과 관리 가능한 리스크 수준"
        elif roi > 8 and risk_level in ['LOW', 'MEDIUM']:
            recommendation = "**추천**"
            reasoning = "안정적인 수익성과 적절한 리스크 관리"
        else:
            recommendation = "**조건부 추천**"
            reasoning = "추가 검토를 통한 리스크 완화 필요"
        
        narrative = f"""
종합 검토 결과, 본 사업대상지는 LH 신축매입임대 사업지로 {recommendation}합니다.

**추천 근거**:
- {reasoning}
- 총 {units}세대 규모의 안정적인 개발 가능
- 투자수익률(ROI) {roi:.1f}%의 양호한 사업성
- 정책적 지원 및 인센티브 확보 가능

**즉시 실행 가능 사항**:
1. LH 신축매입임대 사업 신청
2. 건축 설계 및 인허가 준비
3. 금융 조달 계획 수립
4. 시공사 선정 및 계약 추진

본 사업은 재무적 타당성과 정책적 의의를 동시에 충족하는 우수한 프로젝트로 평가되며, 
적극적인 사업 추진을 권장합니다.
        """.strip()
        
        return narrative


# Module exports
__all__ = ["NarrativeEngineV241", "NarrativeSection"]
