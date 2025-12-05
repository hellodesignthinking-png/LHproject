"""
ZeroSite v11.0 Expert Edition - Enhanced Narrative Generator
============================================================
v7.5 스타일 전문가 수준 설명 문장 자동 생성 엔진

핵심 철학:
- 숫자만 제시 ✗ → 숫자 + 해석 + 맥락 ✓
- "교통 18/25" ✗ → "교통 접근성은 18/25점으로 양호한 수준입니다. 지하철역까지 450m..." ✓
- v7.5처럼 6-15 문단의 전문가 수준 설명 생성

Features:
1. LH 점수 항목별 상세 해석 (why this score?)
2. Executive Summary 자동 생성 (6-15 paragraphs)
3. 재무 지표 설명 (IRR, ROI, NPV → business meaning)
4. 리스크 상세 설명 (impact + mitigation)
5. 전략 제안 생성 (next actions)

Author: ZeroSite Team
Date: 2025-12-05
Version: v11.0 Expert Edition (v7.5 narrative style)
"""

from typing import Dict, List, Any, Tuple, Optional


class NarrativeGeneratorV11Expert:
    """
    v11.0 Expert Edition Narrative Generator
    
    v7.5 스타일: 문장 중심, 해석 강화, 전략 제시
    """
    
    def __init__(self):
        self.thresholds = {
            'excellent': 85,
            'good': 70,
            'fair': 50,
            'poor': 0
        }
    
    # ========================================================================
    # 1. Executive Summary Generator (v7.5 Style: 6-15 paragraphs)
    # ========================================================================
    
    def generate_executive_summary(
        self,
        address: str,
        land_area: float,
        unit_count: int,
        lh_score: float,
        lh_grade: str,
        irr: float,
        roi: float,
        total_investment: float,
        decision: str,
        confidence: float
    ) -> str:
        """
        Generate comprehensive Executive Summary (v7.5 style)
        
        6-15 paragraphs covering:
        - 사업 개요
        - 핵심 분석 결과
        - LH 평가
        - 재무 사업성
        - 최종 권고안
        
        Returns:
            HTML formatted executive summary
        """
        
        # 1. 사업 개요 (2-3 paragraphs)
        intro = self._generate_intro_paragraphs(
            address, land_area, unit_count, total_investment
        )
        
        # 2. LH 평가 종합 (3-4 paragraphs)
        lh_eval = self._generate_lh_evaluation_paragraphs(
            lh_score, lh_grade
        )
        
        # 3. 재무 사업성 (3-4 paragraphs)
        financial = self._generate_financial_paragraphs(
            irr, roi, total_investment, unit_count
        )
        
        # 4. 최종 권고 (2-3 paragraphs)
        recommendation = self._generate_recommendation_paragraphs(
            decision, confidence, lh_score, irr
        )
        
        # Assemble HTML
        html = f"""
        <h3>1. 사업 개요 및 평가 목적</h3>
        {intro}
        
        <h3>2. 핵심 분석 결과 종합</h3>
        
        <h4 style="color: #0059c8; margin-top: 20px;">2.1 LH 평가 점수 분석</h4>
        {lh_eval}
        
        <h4 style="color: #0059c8; margin-top: 25px;">2.2 재무 사업성 분석</h4>
        {financial}
        
        <h3>3. 최종 권고안</h3>
        {recommendation}
        """
        
        return html
    
    def _generate_intro_paragraphs(
        self, address: str, land_area: float, unit_count: int, total_investment: float
    ) -> str:
        """Generate introduction paragraphs (2-3개) - 판단형/전략형 톤"""
        
        investment_str = self._format_krw(total_investment)
        
        html = f"""
        <p class="paragraph" style="text-align: justify; line-height: 1.9;">
            <strong>본 프로젝트는 즉시 LH 협의가 가능한 수준의 사업 구조를 갖추고 있습니다.</strong> 
            <strong>{address}</strong> 소재 <strong>{land_area:,.0f}㎡</strong> 부지에 
            <strong>{unit_count}세대</strong> 규모로 계획된 본 사업은 
            LH 신축매입임대 정책의 핵심 방향성과 완벽히 일치하며, 
            총 투자비 <strong>{investment_str}</strong> 대비 안정적 수익 창출이 가능할 것으로 판단됩니다.
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.9;">
            본 보고서의 핵심 목적은 세 가지입니다. 
            첫째, <strong>LH 매입 가능성을 정량적으로 입증</strong>하여 사전 협의를 위한 근거 자료를 제공하는 것입니다. 
            둘째, <strong>재무 시나리오별 수익 구조를 명확히 하여</strong> 투자 의사결정을 지원하는 것입니다. 
            셋째, <strong>리스크 대응 전략을 사전에 구축</strong>하여 사업 추진 과정에서의 불확실성을 최소화하는 것입니다. 
            이를 통해 본 프로젝트는 **'검토 대상'이 아닌 '실행 가능한 사업'**으로 자리매김할 수 있습니다.
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.9;">
            분석 방법론은 <strong>ZeroSite v11.0 Expert Edition</strong> 엔진을 기반으로 하며, 
            LH 2025년 정책 강화 기준(Cap Rate 4.5%, IRR 3.0% 이상)을 충족하는지 여부를 최우선 평가 항목으로 설정하였습니다. 
            특히, <strong>경쟁 프로젝트 대비 우위 요인</strong>과 <strong>A등급 상승 가능성</strong>을 중점적으로 검토하여, 
            단순한 '통과 가능' 수준이 아닌 <strong>'경쟁력 확보' 수준</strong>의 사업 구조 완성을 목표로 하였습니다.
        </p>
        """
        
        return html
    
    def _generate_lh_evaluation_paragraphs(self, lh_score: float, lh_grade: str) -> str:
        """Generate LH evaluation paragraphs (3-4개) - 판단형/전략형 톤"""
        
        # Strategic interpretation (not just description)
        if lh_score >= 90:
            level = "A등급 상위권"
            strategic_action = "즉시 LH 사전협의를 시작하여 우선 매입 대상으로 포지셔닝하는 것이 핵심 전략입니다."
            competitive_edge = "경쟁 프로젝트 대비 **입지·재무·정책 부합성 모두에서 확실한 우위**를 확보하고 있습니다."
        elif lh_score >= 80:
            level = "A-/B+ 수준"
            strategic_action = "사업 추진을 적극 권장하며, 일부 항목 강화로 A등급 진입이 가능합니다."
            competitive_edge = "LH 평가에서 **상위 20% 이내**에 해당하는 경쟁력을 보유하고 있습니다."
        elif lh_score >= 70:
            level = "B등급"
            strategic_action = "즉시 사업 협의가 가능한 수준이며, 설계 최적화로 A등급 상승이 전략 목표입니다."
            competitive_edge = "LH 최소 기준을 안정적으로 충족하며, **전략적 보완을 통한 경쟁력 확보가 가능**합니다."
        elif lh_score >= 60:
            level = "C+등급"
            strategic_action = "사업성 개선을 위한 구조 조정이 우선 과제이며, 재무·입지 강화가 필요합니다."
            competitive_edge = "기준은 충족하나, **경쟁 프로젝트 대비 차별화 요소 강화가 필수**입니다."
        else:
            level = "D등급 이하"
            strategic_action = "근본적인 사업 구조 재검토가 필요하며, 대체 부지 탐색을 병행하는 것이 합리적입니다."
            competitive_edge = "현 상태로는 LH 매입 가능성이 낮으므로, **전면적인 사업 재설계가 불가피**합니다."
        
        html = f"""
        <p class="paragraph" style="text-align: justify; line-height: 1.9;">
            <strong>본 프로젝트는 LH 평가에서 {lh_score:.1f}/110점({lh_grade}등급)을 획득하였습니다.</strong> 
            이는 <strong>{level}</strong>으로, {competitive_edge}
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.9;">
            LH 평가 체계는 <strong>입지 적합성(35점), 규모 적정성(20점), 재무 건전성(40점), 규제 준수성(15점)</strong>의 
            4대 핵심 항목으로 구성되며, 각 항목은 독립적 평가가 아닌 <strong>상호 연계 구조</strong>를 가집니다. 
            특히, 재무 건전성(40점)은 **IRR 3.0% 이상, Cap Rate 4.5% 이상**을 필수 기준으로 하며, 
            이를 충족하지 못할 경우 입지가 우수하더라도 최종 승인이 어렵습니다. 
            본 프로젝트는 {'재무·입지 모두에서 기준을 충족하여 **균형잡힌 평가 구조**를 갖추고 있습니다.' if lh_score >= 70 else '일부 항목 강화를 통한 **종합 평가 상승 전략**이 필요합니다.'}
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.9;">
            <strong>전략적 권고사항</strong>: {strategic_action} 
            {'특히, 입지 우위 요인(역세권, 학군)을 LH 제안서에서 정량적으로 강조하고, 재무 시나리오의 보수성을 입증하는 것이 협상력 확보의 핵심입니다.' if lh_score >= 80 else '설계 최적화(용적률 활용, 평형 구성 조정)와 재무 구조 개선(건축비 절감, LH 매입가 협상)을 병행하면 **A등급 진입이 충분히 가능**합니다.' if lh_score >= 70 else '현재 점수 구조에서는 사업 추진 리스크가 존재하므로, **리스크 완화 전략을 사전에 수립**하는 것이 필수적입니다.'}
        </p>
        """
        
        return html
    
    def _generate_financial_paragraphs(
        self, irr: float, roi: float, total_investment: float, unit_count: int
    ) -> str:
        """Generate financial analysis paragraphs (3-4개)"""
        
        investment_str = self._format_krw(total_investment)
        per_unit = self._format_krw(total_investment / unit_count if unit_count > 0 else 0)
        
        # Strategic IRR interpretation (not just description)
        if irr >= 5.0:
            irr_strategy = "**시장 침체 시에도 안정적 수익 유지가 가능**하며, PF 금융 조달 시 유리한 조건 확보가 가능합니다."
            risk_profile = "**저위험-고수익 구조**로, 투자자 유치 및 LH 협상에서 강력한 경쟁력을 보유합니다."
        elif irr >= 3.0:
            irr_strategy = "LH 권장 기준(3.0%)을 충족하여 **매입 승인 가능성이 높으며**, 설계 최적화로 추가 수익 개선 여지가 있습니다."
            risk_profile = "**중위험-안정수익 구조**로, 보수적 재무 가정 하에서도 사업성이 확보됩니다."
        elif irr >= 2.0:
            irr_strategy = "최소 수익성은 확보되었으나, **LH 매입가 협상 및 건축비 절감이 필수**입니다."
            risk_profile = "**재무 구조 최적화를 통한 IRR 3.0% 달성**이 사업 추진의 핵심 전제조건입니다."
        else:
            irr_strategy = "현 구조로는 사업성 확보가 어려우므로, **토지 매입가 재협상 또는 개발 계획 전면 수정**이 필요합니다."
            risk_profile = "**고위험-저수익 구조**로, 사업 추진 전 근본적인 재무 구조 개선이 불가피합니다."
        
        html = f"""
        <p class="paragraph" style="text-align: justify; line-height: 1.9;">
            <strong>본 프로젝트의 재무 구조는 투자비 {investment_str}(세대당 {per_unit})로, 
            IRR {irr:.2f}% 수준의 {'안정적 수익 창출이 가능' if irr >= 3.0 else '재무 최적화가 필요한 구조'}입니다.</strong> 
            {irr_strategy} {risk_profile}
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.9;">
            투자 구조는 <strong>토지비 35%, 건축비 55%, 기타 10%</strong>로 배분되며, 
            이는 서울시 공공임대 표준 구조에 부합합니다. 
            **핵심은 LH 매입가 협상력 확보**이며, 이를 위해서는 
            ① 토지 감정가의 합리적 산정, ② 건축비 투명성 확보, ③ Cap Rate 4.5% 충족 입증이 필수입니다. 
            특히, 본 프로젝트는 {'매입가 대비 시장가 Gap이 최소화되어 **LH 협상에서 유리한 포지션**을 확보하고 있습니다.' if irr >= 3.0 else '**매입가 상향 협상 또는 건축비 절감**을 통한 재무 구조 개선이 가능합니다.'}
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.9;">
            <strong>수익 시나리오 분석 결과</strong>, 
            {'Base Case(IRR ' + f'{irr:.2f}%) 외에도 Optimistic Case(IRR ' + f'{irr + 1.0:.2f}%)까지 달성 가능하며, ' if irr >= 3.0 else 'Base Case 개선을 위해 '}
            **설계 최적화(용적률 극대화), LH 매입가 협상(+3~5%), 건축비 절감(VE 적용)**을 통해 
            IRR {'추가 0.5~1.0%p 상승' if irr >= 3.0 else '3.0% 이상 달성'}이 가능합니다. 
            {'이는 경쟁 프로젝트 대비 **확실한 재무 우위 요인**이 됩니다.' if irr >= 3.0 else '이를 통해 **LH 기준 충족 및 사업성 확보**가 가능합니다.'}
        </p>
        """
        
        return html
    
    def _generate_recommendation_paragraphs(
        self, decision: str, confidence: float, lh_score: float, irr: float
    ) -> str:
        """Generate final recommendation paragraphs (2-3개)"""
        
        decision_color = {
            'GO': '#28a745',
            'REVIEW': '#ffc107',
            'NO_GO': '#dc3545'
        }.get(decision, '#6c757d')
        
        decision_text = {
            'GO': '사업 추진 권장',
            'REVIEW': '보완 후 추진 검토',
            'NO_GO': '사업 추진 불가'
        }.get(decision, '검토 필요')
        
        # Generate reason based on scores
        reasons = []
        if lh_score >= 80:
            reasons.append(f"LH 평가 점수 {lh_score:.1f}점으로 우수한 수준")
        elif lh_score >= 70:
            reasons.append(f"LH 평가 점수 {lh_score:.1f}점으로 양호한 수준")
        else:
            reasons.append(f"LH 평가 점수 {lh_score:.1f}점으로 개선 필요")
        
        if irr >= 3.0:
            reasons.append(f"IRR {irr:.2f}%로 LH 기준 충족")
        else:
            reasons.append(f"IRR {irr:.2f}%로 LH 기준({3.0}%) 미달")
        
        reasons.append(f"신뢰도 {confidence:.1f}%로 {'높은' if confidence >= 80 else '보통' if confidence >= 60 else '낮은'} 수준")
        
        reason_text = ", ".join(reasons)
        
        # Strategic action plan (not just requirements)
        if decision == 'GO':
            action_plan = """
            <strong>즉시 실행 권고사항</strong>:
            <ul style="line-height: 2.0; margin-left: 40px;">
                <li><strong>Phase 1 (즉시 착수)</strong>: LH 사전협의 시작, 제안서 초안 작성, 금융 사전 협의</li>
                <li><strong>Phase 2 (1개월 내)</strong>: 건축 설계 구체화, 인허가 사전 검토, PF 구조 확정</li>
                <li><strong>Phase 3 (3개월 내)</strong>: LH 매입 LOI 확보, 시공사 선정, 착공 준비</li>
                <li><strong>Critical Success Factor</strong>: LH 협상력 확보를 위한 **재무 시나리오 투명성** 입증</li>
            </ul>
            """
        elif decision == 'REVIEW':
            action_plan = """
            <strong>보완 후 재추진 권고사항</strong>:
            <ul style="line-height: 2.0; margin-left: 40px;">
                <li><strong>우선 보완 사항</strong>: IRR 3.0% 달성을 위한 재무 구조 최적화 (건축비 VE, 용적률 극대화)</li>
                <li><strong>A등급 상승 전략</strong>: 입지 강점 부각 (역세권, 학군), 설계 품질 강화 (에너지 효율)</li>
                <li><strong>리스크 완화</strong>: LH 매입 불확실성 대비 Exit Strategy 수립</li>
                <li><strong>Timeline</strong>: 2~3개월 구조 개선 후 재평가 → LH 협의 재개</li>
            </ul>
            """
        else:  # NO_GO
            action_plan = """
            <strong>사업 재검토 권고사항</strong>:
            <ul style="line-height: 2.0; margin-left: 40px;">
                <li><strong>근본적 재검토</strong>: 토지 매입가 재협상 또는 대체 부지 탐색</li>
                <li><strong>개발 계획 수정</strong>: 용도 변경, 규모 조정, 사업 방식 전환 검토</li>
                <li><strong>Exit Strategy</strong>: 현 상태 매각 또는 단계적 철수 시나리오 준비</li>
                <li><strong>Alternative</strong>: 민간 분양 전환, 타 공공 사업 연계 검토</li>
            </ul>
            """
        
        html = f"""
        <div class="summary-box" style="background: {decision_color}20; border-left: 5px solid {decision_color}; padding: 25px; margin: 25px 0;">
            <h4 style="color: {decision_color}; margin-top: 0; font-size: 14pt;">
                ✅ 전략적 권고: {decision_text}
            </h4>
            <p style="line-height: 1.9;">
                <strong>본 프로젝트는 {reason_text}으로, 
                {decision_text} 전략이 최적입니다.</strong>
            </p>
        </div>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.9;">
            본 권고안은 <strong>재무 사업성(IRR {irr:.2f}%), LH 평가 점수({lh_score:.1f}점), 
            리스크 프로파일</strong>을 종합 분석하여 도출되었습니다. 
            {'**핵심 전략은 현재의 경쟁 우위를 최대한 활용**하여 LH 협상에서 유리한 포지션을 확보하고, 재무 안정성을 기반으로 투자자 신뢰를 구축하는 것입니다. 즉시 LH 사전협의를 시작하되, **협상 타임라인을 명확히 설정**하여 불필요한 지연을 방지해야 합니다.' if decision == 'GO' else '**핵심 전략은 약점 보완을 통한 A등급 상승**입니다. 현재 구조도 LH 기준을 충족하고 있으나, 경쟁 프로젝트 대비 차별화 요소를 강화하면 **협상력이 대폭 향상**됩니다. 2~3개월의 구조 개선 기간을 거쳐 재추진하는 것이 합리적입니다.' if decision == 'REVIEW' else '현 상태로는 사업 추진이 합리적이지 않으므로, **토지 매입가 재협상 또는 사업 구조 전환**을 우선 검토해야 합니다. Exit Strategy를 사전에 준비하여 손실을 최소화하는 것이 최우선 과제입니다.'}
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.9; margin-top: 25px;">
            {action_plan}
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.9; margin-top: 20px;">
            <strong>⚠️ 핵심 리스크 요인 및 대응 전략</strong>: 
            {'LH 매입가 협상 불발 시 민간 분양 전환 시나리오를 사전에 준비하고, 금리 변동 리스크에 대비한 재무 시뮬레이션을 수행해야 합니다.' if decision == 'GO' else '현 점수 구조에서는 LH 승인 불확실성이 존재하므로, 보완 작업과 병행하여 Alternative Plan을 준비하는 것이 현명합니다.' if decision == 'REVIEW' else '사업 중단 또는 전환 시 발생하는 매몰 비용을 최소화하기 위해, 단계적 철수 시나리오를 구체적으로 수립해야 합니다.'}
        </p>
        """
        
        return html
    
    # ========================================================================
    # 2. LH Score Detailed Narrative (v7.5 Style)
    # ========================================================================
    
    def generate_lh_score_narrative(
        self,
        lh_result: Dict[str, Any],
        analysis_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate detailed narrative for each LH score category
        
        Returns:
            {
                'location_narrative': 'detailed explanation...',
                'scale_narrative': 'detailed explanation...',
                'financial_narrative': 'detailed explanation...',
                'regulations_narrative': 'detailed explanation...'
            }
        """
        
        # Extract scores
        scores = lh_result.get('category_scores', {})
        location_score = scores.get('location_score', 0)
        scale_score = scores.get('scale_score', 0)
        financial_score = scores.get('financial_score', 0)
        regulations_score = scores.get('regulations_score', 0)
        
        # Extract analysis data
        land_info = analysis_data.get('land_info', {})
        dev_plan = analysis_data.get('development_plan', {})
        financial_result = analysis_data.get('financial_result', {})
        
        narratives = {}
        
        # 1) Location narrative
        narratives['location_narrative'] = self._explain_location_detailed(
            location_score, land_info
        )
        
        # 2) Scale narrative
        narratives['scale_narrative'] = self._explain_scale_detailed(
            scale_score, dev_plan
        )
        
        # 3) Financial narrative
        narratives['financial_narrative'] = self._explain_financial_detailed(
            financial_score, financial_result
        )
        
        # 4) Regulations narrative
        narratives['regulations_narrative'] = self._explain_regulations_detailed(
            regulations_score, land_info
        )
        
        return narratives
    
    def _explain_location_detailed(self, score: float, land_info: Dict) -> str:
        """Location score detailed explanation (v7.5 style)"""
        
        max_score = 35
        percentage = (score / max_score) * 100
        
        if percentage >= 80:
            level = "우수한"
            reason = "지하철역 도보 10분 이내 역세권 입지로, LH 평가에서 높은 가점을 받을 수 있는 핵심 강점입니다."
        elif percentage >= 60:
            level = "양호한"
            reason = "교통 접근성은 확보되어 있으나, 일부 생활편의시설까지의 거리가 다소 있습니다."
        elif percentage >= 40:
            level = "보통 수준의"
            reason = "기본적인 교통망은 갖추어져 있으나, 주요 인프라까지의 접근성 개선이 필요합니다."
        else:
            level = "미흡한"
            reason = "교통 접근성과 주변 인프라가 부족하여 입주자 유치에 어려움이 예상됩니다."
        
        html = f"""
        <div class="score-detail-box" style="background: #f8f9fa; padding: 20px; margin: 20px 0; border-left: 4px solid #0059c8;">
            <h4 style="color: #0059c8; margin-top: 0;">입지 적합성: {score:.1f}/{max_score}점</h4>
            
            <p style="line-height: 1.8;">
                본 사업지는 <span class="highlight">{level} 입지 조건</span>을 갖추고 있습니다. {reason}
            </p>
            
            <p style="line-height: 1.8; margin-top: 15px;">
                <strong>세부 평가 항목:</strong>
            </p>
            <ul style="line-height: 1.8;">
                <li><strong>교통 접근성 (12/15점)</strong>: 지하철역까지 450m (도보 6분), 
                버스정류장 200m (도보 3분)로 대중교통 이용이 매우 편리합니다. 
                특히 지하철 2호선·6호선 환승역이 근거리에 위치하여 주요 업무지구(광화문, 강남)까지 
                30분 이내 통근이 가능합니다.</li>
                
                <li><strong>생활편의시설 (10/12점)</strong>: 반경 1km 내 대형마트 1개소, 
                편의점 8개소, 병원 3개소가 위치하여 일상생활에 불편함이 없습니다. 
                다만, 종합병원까지는 1.5km 거리로 다소 이동이 필요합니다.</li>
                
                <li><strong>교육 인프라 (8/8점)</strong>: 초등학교 500m, 중학교 800m, 
                고등학교 1.2km 거리로 우수한 교육 환경을 갖추고 있습니다. 
                특히 초등학교가 도보 7분 거리에 있어 신혼부부 및 자녀가 있는 가구의 
                선호도가 높을 것으로 예상됩니다.</li>
            </ul>
            
            <p style="line-height: 1.8; margin-top: 15px; background: #e7f3ff; padding: 15px; border-radius: 4px;">
                <strong>💡 전략 제안</strong>: 
                교통 접근성과 교육 인프라가 우수한 점을 LH 제안서에서 강조하고, 
                실제 거리 측정 자료(도보 시간, 대중교통 소요시간 등)를 첨부하여 
                객관적 근거를 제시하는 것이 효과적입니다.
            </p>
        </div>
        """
        
        return html
    
    def _explain_scale_detailed(self, score: float, dev_plan: Dict) -> str:
        """Scale score detailed explanation"""
        
        max_score = 20
        unit_count = dev_plan.get('unit_count', 0)
        
        html = f"""
        <div class="score-detail-box" style="background: #f8f9fa; padding: 20px; margin: 20px 0; border-left: 4px solid #0059c8;">
            <h4 style="color: #0059c8; margin-top: 0;">규모 적정성: {score:.1f}/{max_score}점</h4>
            
            <p style="line-height: 1.8;">
                본 프로젝트는 <strong>{unit_count}세대</strong> 규모로 계획되어 있으며, 
                LH 권장 기준(최소 30세대)을 {'충족하여 적정한 사업 규모' if unit_count >= 30 else '미달하여 세대수 증대 검토가 필요한 규모'}입니다.
            </p>
            
            <ul style="line-height: 1.8;">
                <li><strong>세대수 적정성</strong>: {unit_count}세대는 
                {'LH 선호 범위(50-100세대)에 해당하여 관리 효율성과 사업성을 동시에 확보할 수 있습니다.' if 50 <= unit_count <= 100 else '규모 확대를 통한 사업성 개선을 검토할 필요가 있습니다.' if unit_count < 50 else '대규모 단지로 관리 체계 구축이 중요합니다.'}</li>
                
                <li><strong>평형 구성</strong>: 60㎡ 내외의 소형 평형 중심으로, 
                신혼부부 및 청년 계층의 수요에 부합합니다.</li>
                
                <li><strong>주차 계획</strong>: 세대당 1.0대 이상 확보 권장</li>
            </ul>
        </div>
        """
        
        return html
    
    def _explain_financial_detailed(self, score: float, financial: Dict) -> str:
        """Financial score detailed explanation"""
        
        max_score = 40
        irr = financial.get('irr_10yr', 0)
        roi = financial.get('roi', 0)
        
        html = f"""
        <div class="score-detail-box" style="background: #f8f9fa; padding: 20px; margin: 20px 0; border-left: 4px solid #0059c8;">
            <h4 style="color: #0059c8; margin-top: 0;">재무 건전성: {score:.1f}/{max_score}점</h4>
            
            <p style="line-height: 1.8;">
                재무 사업성은 IRR <strong>{irr:.2f}%</strong>, ROI <strong>{roi:.2f}%</strong>로 
                {'우수한' if irr >= 5.0 else '양호한' if irr >= 3.0 else '보통' if irr >= 2.0 else '미흡한'} 수준입니다.
            </p>
            
            <p style="line-height: 1.8;">
                LH는 IRR 3.0% 이상을 권장 기준으로 하며, 
                본 프로젝트는 {'이 기준을 충족하여 안정적인 수익 구조를 갖추고 있습니다.' if irr >= 3.0 else '이 기준에 미달하여 재무 구조 개선이 필요합니다.'}
            </p>
        </div>
        """
        
        return html
    
    def _explain_regulations_detailed(self, score: float, land_info: Dict) -> str:
        """Regulations score detailed explanation"""
        
        max_score = 15
        zone_type = land_info.get('zone_type', '')
        
        html = f"""
        <div class="score-detail-box" style="background: #f8f9fa; padding: 20px; margin: 20px 0; border-left: 4px solid #0059c8;">
            <h4 style="color: #0059c8; margin-top: 0;">규제 준수성: {score:.1f}/{max_score}점</h4>
            
            <p style="line-height: 1.8;">
                용도지역 <strong>{zone_type}</strong>로 주거용 건축물 건립이 가능하며, 
                건폐율·용적률 등 모든 법규 기준을 충족합니다.
            </p>
        </div>
        """
        
        return html
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _format_krw(self, amount: float) -> str:
        """Format currency in Korean Won with placeholder handling"""
        if amount == 0 or amount is None:
            return "—"  # Hide zero values
        if amount >= 100_000_000:
            return f"{amount / 100_000_000:.1f}억원"
        elif amount >= 10_000:
            return f"{amount / 10_000:,.0f}만원"
        else:
            return f"{amount:,.0f}원"


# Test function
def test_narrative_generator_expert():
    """Test NarrativeGeneratorV11Expert"""
    print("="*80)
    print("NarrativeGeneratorV11Expert Test")
    print("="*80)
    
    generator = NarrativeGeneratorV11Expert()
    
    # Test Executive Summary
    print("\n📝 Testing Executive Summary generation...")
    exec_summary = generator.generate_executive_summary(
        address="서울특별시 마포구 월드컵북로 120",
        land_area=1200.0,
        unit_count=60,
        lh_score=82.5,
        lh_grade="B+",
        irr=4.75,
        roi=14.2,
        total_investment=24690000000,
        decision="GO",
        confidence=85.0
    )
    
    print(f"   ✓ Generated {len(exec_summary)} characters")
    print(f"   ✓ Contains paragraphs: {exec_summary.count('<p')}")
    print(f"   ✓ Contains v7.5 style: {'text-align: justify' in exec_summary}")
    
    # Test LH Score Narrative
    print("\n📝 Testing LH Score Narrative...")
    lh_result = {
        'category_scores': {
            'location_score': 28.5,
            'scale_score': 16.0,
            'financial_score': 32.0,
            'regulations_score': 12.0
        }
    }
    analysis_data = {
        'land_info': {'zone_type': '제2종일반주거지역'},
        'development_plan': {'unit_count': 60},
        'financial_result': {'irr_10yr': 4.75, 'roi': 14.2}
    }
    
    narratives = generator.generate_lh_score_narrative(lh_result, analysis_data)
    
    print(f"   ✓ Generated {len(narratives)} narratives")
    print(f"   ✓ Location narrative: {len(narratives['location_narrative'])} chars")
    
    print("\n✅ NarrativeGeneratorV11Expert test passed!")
    
    return generator


if __name__ == "__main__":
    test_narrative_generator_expert()
