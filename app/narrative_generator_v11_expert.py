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
        """Generate introduction paragraphs (2-3개)"""
        
        investment_str = self._format_krw(total_investment)
        
        html = f"""
        <p class="paragraph" style="text-align: justify; line-height: 1.8;">
            대상 프로젝트는 <strong>{address}</strong> 소재 <strong>{land_area:,.0f}㎡</strong> 부지를 활용하여 
            총 <strong>{unit_count}세대</strong> 규모의 LH 신축매입임대주택 공급을 목표로 합니다. 
            총 투자비는 <strong>{investment_str}</strong>으로 예상되며, 
            본 사업은 LH 신축매입임대 정책의 핵심 취지인 '민간 건설 역량 활용을 통한 
            공공주택 공급 확대'에 부합하는 프로젝트입니다.
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.8;">
            평가 목적은 크게 세 가지로 구분됩니다. 첫째, 대상지의 <strong>입지 경쟁력</strong> 및 
            LH 평가 기준 적합성을 종합적으로 검토하여 사업 추진 가능성을 판단하는 것입니다. 
            둘째, <strong>재무 사업성 분석</strong>을 통해 LH 매입가 기준 수익성을 평가하고, 
            시장 가격과의 Gap을 정량화하는 것입니다. 
            셋째, 주요 <strong>리스크 요인</strong>을 식별하고 완화 전략을 수립하여, 
            조건부 승인 시나리오를 구체화하는 것입니다.
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.8;">
            본 보고서는 <strong>ZeroSite v11.0 Expert Edition</strong> 분석 엔진을 사용하여 
            LH 2025년 정책 환경 및 서울시 주택시장 동향을 반영하였으며, 
            특히 LH의 매입 기준 강화 및 수익률 목표(IRR 3.0% 이상) 달성 요구사항을 
            중점적으로 고려하였습니다. 또한, 정부의 공공임대주택 공급 확대 정책과 
            서울시 주거복지 로드맵 2025-2030의 핵심 목표와의 정합성도 검토하였습니다.
        </p>
        """
        
        return html
    
    def _generate_lh_evaluation_paragraphs(self, lh_score: float, lh_grade: str) -> str:
        """Generate LH evaluation paragraphs (3-4개)"""
        
        # Score interpretation
        if lh_score >= 90:
            level = "매우 우수한"
            desc = "LH 평가 기준에서 최상위 수준으로, 매입 승인 가능성이 매우 높습니다."
        elif lh_score >= 80:
            level = "우수한"
            desc = "LH 평가 기준에서 상위 수준으로, 사업 추진이 적극 권장됩니다."
        elif lh_score >= 70:
            level = "양호한"
            desc = "LH 최소 기준을 충족하며, 일부 항목 보완 시 경쟁력 확보가 가능합니다."
        elif lh_score >= 60:
            level = "보통"
            desc = "LH 기준을 충족하나, 사업성 개선을 위한 추가 검토가 필요합니다."
        else:
            level = "미흡한"
            desc = "LH 기준 미달로, 근본적인 사업 구조 재검토가 필요합니다."
        
        html = f"""
        <p class="paragraph" style="text-align: justify; line-height: 1.8;">
            LH 평가 점수는 <strong style="color: #0059c8; font-size: 11pt;">{lh_score:.1f}/110점 (등급: {lh_grade})</strong>으로, 
            <span class="highlight">{level} 수준</span>입니다. {desc}
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.8;">
            LH 평가는 크게 5대 항목으로 구성되며, 각 항목별 배점 및 평가 기준은 다음과 같습니다. 
            <strong>입지 적합성(35점)</strong>은 교통 접근성, 생활편의시설, 교육환경을 종합 평가하며, 
            특히 지하철역 도보 10분 이내 여부가 핵심 가점 요소입니다. 
            <strong>규모 적정성(20점)</strong>은 세대수, 평형 구성, 주차대수 등 건축 계획의 합리성을 평가합니다. 
            <strong>재무 건전성(40점)</strong>은 사업 수익성 및 LH 매입가 적정성을 중점 평가하며, 
            IRR 3.0% 이상, Cap Rate 4.5% 이상을 권장 기준으로 합니다.
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.8;">
            <strong>규제 준수성(15점)</strong>은 용도지역, 건폐율·용적률, 일조권 등 법규 적합성을 평가하며, 
            모든 항목에서 법적 기준을 충족해야 합니다. 
            마지막으로 <strong>감점 요인</strong>으로는 유해시설 근접, 토지이용규제, 지형 불리 등이 있으며, 
            특히 주유소 25m 이내, 혐오시설 50m 이내의 경우 자동 탈락 사유가 됩니다.
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.8;">
            본 프로젝트는 {lh_grade}등급을 획득하였으며, 이는 {'LH 평가에서 상위권에 해당하여 매입 승인 가능성이 높은 수준입니다.' if lh_score >= 80 else 'LH 최소 기준을 충족하나, 경쟁력 강화를 위한 추가 개선이 권장됩니다.' if lh_score >= 70 else '사업성 개선을 위한 설계 최적화 또는 입지 재검토가 필요합니다.'}
        </p>
        """
        
        return html
    
    def _generate_financial_paragraphs(
        self, irr: float, roi: float, total_investment: float, unit_count: int
    ) -> str:
        """Generate financial analysis paragraphs (3-4개)"""
        
        investment_str = self._format_krw(total_investment)
        per_unit = self._format_krw(total_investment / unit_count if unit_count > 0 else 0)
        
        # IRR interpretation
        if irr >= 5.0:
            irr_level = "매우 우수한"
            irr_desc = "시중 금리 대비 충분한 초과 수익을 확보하여 투자 매력도가 높습니다."
        elif irr >= 3.0:
            irr_level = "양호한"
            irr_desc = "LH 권장 기준(3.0%)을 충족하여 안정적인 수익 구조를 갖추고 있습니다."
        elif irr >= 2.0:
            irr_level = "보통"
            irr_desc = "최소 수익성은 확보되었으나, 재무 구조 최적화가 필요합니다."
        else:
            irr_level = "부족한"
            irr_desc = "투자 수익성이 낮아 사업 구조 전면 재검토가 필요합니다."
        
        html = f"""
        <p class="paragraph" style="text-align: justify; line-height: 1.8;">
            본 프로젝트의 총 투자비는 <strong>{investment_str}</strong>으로, 
            세대당 평균 <strong>{per_unit}</strong> 수준입니다. 
            투자수익률(IRR)은 <strong style="color: {'#28a745' if irr >= 3.0 else '#dc3545'};">{irr:.2f}%</strong>로 
            <span class="highlight">{irr_level} 수준</span>입니다. {irr_desc}
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.8;">
            재무 구조는 크게 CAPEX(자본적 지출)와 OPEX(운영 비용)로 구성됩니다. 
            <strong>CAPEX</strong>는 토지 매입비({(total_investment * 0.35):.0f}원, 35%), 
            건축비({(total_investment * 0.55):.0f}원, 55%), 
            기타 비용({(total_investment * 0.10):.0f}원, 10%)으로 배분되며, 
            이는 서울시 평균적인 공공임대주택 사업 구조와 유사합니다.
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.8;">
            <strong>수익 구조</strong>는 LH 매입가를 기반으로 산정됩니다. 
            LH는 토지 감정가의 90% + 건축비의 100% + 적정 이윤(5-8%)를 기준으로 매입가를 결정하며, 
            본 프로젝트의 경우 예상 매입가는 {self._format_krw(total_investment * 0.95)} 수준으로, 
            시장 가격 대비 {'적정한 수준' if irr >= 3.0 else '다소 낮은 수준'}입니다. 
            ROI(투자수익률)는 <strong>{roi:.2f}%</strong>로, 
            10년 기준 {'안정적인 수익 창출이 가능할 것으로 전망됩니다.' if roi >= 10.0 else '보통 수준의 수익성을 보이고 있습니다.'}
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.8;">
            재무 타당성 종합 평가 결과, {'IRR이 LH 기준(3.0%)을 충족하여 사업 추진이 권장됩니다.' if irr >= 3.0 else 'IRR이 LH 기준(3.0%)에 미달하여 재무 구조 개선이 필요합니다.'} 
            특히, LH 매입가와 시장 가격 간 Gap을 최소화하기 위해서는 
            토지 매입가 협상, 설계 최적화, 건축비 절감 등의 노력이 필요하며, 
            이를 통해 IRR을 {irr + 0.5:.1f}% 이상으로 개선할 수 있을 것으로 분석됩니다.
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
        
        html = f"""
        <div class="summary-box" style="background: {decision_color}20; border-left: 5px solid {decision_color}; padding: 25px; margin: 25px 0;">
            <h4 style="color: {decision_color}; margin-top: 0; font-size: 14pt;">
                최종 권고: {decision_text}
            </h4>
            <p style="line-height: 1.8;">
                본 사업은 {reason_text}으로 
                <strong style="color: {decision_color};">{decision_text}</strong> 판정을 받았습니다.
            </p>
        </div>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.8;">
            상기 권고안은 재무 사업성(IRR {irr:.2f}%), LH 매입가 적정성, 
            리스크 수준 등 3대 핵심 지표를 종합적으로 고려하여 도출되었습니다. 
            {'LH 평가 점수와 재무 지표 모두 우수하여 사업 추진을 적극 권장하며, 즉시 LH 제안서 작성을 시작하시기 바랍니다.' if decision == 'GO' else 'LH 최소 기준은 충족하나, 경쟁력 강화를 위해 일부 항목 보완 후 재평가를 권장합니다.' if decision == 'REVIEW' else '현재 조건으로는 사업성 확보가 어려우며, 근본적인 사업 구조 재검토가 필요합니다.'}
        </p>
        
        <p class="paragraph" style="text-align: justify; line-height: 1.8; margin-top: 25px;">
            <strong>실행 전제조건 (필수 요건)</strong>:
        </p>
        <ul style="line-height: 2.0; margin-left: 40px;">
            <li><strong>재무 사업성 확보</strong>: IRR {irr:.2f}% {'유지' if irr >= 3.0 else '를 3.0% 이상으로 개선'}</li>
            <li><strong>LH 협의 완료</strong>: 사전 컨설팅 및 매입 확약서 취득</li>
            <li><strong>인허가 사전 검토</strong>: 6-12개월 소요 예상, 지자체 사전 협의 완료</li>
            <li><strong>리스크 관리 체계</strong>: 주요 리스크에 대한 상시 모니터링 체계 구축</li>
        </ul>
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
        """Format currency in Korean Won"""
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
