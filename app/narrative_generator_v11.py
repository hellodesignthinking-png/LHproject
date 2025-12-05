"""
ZeroSite v11.0 - Narrative Generator
설명 자동 생성 엔진 (Explanation Layer)

목적: 수치 → 의미 있는 문장 변환
- Score breakdown text generator
- Reason-based decision text  
- Risk explanation text
- Strategy proposal text

Author: ZeroSite Team
Date: 2025-12-05
"""

from typing import Dict, List, Any, Tuple


class NarrativeGenerator:
    """
    수치 데이터를 전문가 수준의 설명 문장으로 변환하는 엔진
    
    주요 기능:
    1. LH 점수 항목별 해석 (왜 이 점수인가?)
    2. 의사결정 근거 설명 (GO/NO-GO 이유)
    3. 리스크 상세 설명 (각 리스크의 영향과 대응 방안)
    4. 전략 제안 생성 (다음 행동 제시)
    """
    
    def __init__(self):
        self.thresholds = {
            'excellent': 85,
            'good': 70,
            'fair': 50,
            'poor': 0
        }
    
    # ========================================================================
    # 1. LH Score Breakdown Narrative
    # ========================================================================
    
    def generate_score_narrative(self, lh_result: Dict[str, Any]) -> Dict[str, str]:
        """
        LH 점수 항목별 상세 설명 생성
        
        Args:
            lh_result: LH Score Mapper 결과
            
        Returns:
            {
                'location_narrative': '입지 점수 18/25 이유...',
                'business_narrative': '사업성 점수 23/30 이유...',
                ...
            }
        """
        scores = lh_result.get('category_scores', {})
        details = lh_result.get('score_details', {})
        
        narratives = {}
        
        # 1) 입지 적합성 (Location Suitability) 25점
        location_score = scores.get('location_suitability', 0)
        narratives['location_narrative'] = self._explain_location_score(
            location_score, details.get('location', {})
        )
        
        # 2) 사업 타당성 (Business Feasibility) 30점
        business_score = scores.get('business_feasibility', 0)
        narratives['business_narrative'] = self._explain_business_score(
            business_score, details.get('business', {})
        )
        
        # 3) 정책 부합성 (Policy Alignment) 20점
        policy_score = scores.get('policy_alignment', 0)
        narratives['policy_narrative'] = self._explain_policy_score(
            policy_score, details.get('policy', {})
        )
        
        # 4) 재무 건전성 (Financial Soundness) 15점
        financial_score = scores.get('financial_soundness', 0)
        narratives['financial_narrative'] = self._explain_financial_score(
            financial_score, details.get('financial', {})
        )
        
        # 5) 리스크 수준 (Risk Level) 10점
        risk_score = scores.get('risk_level', 0)
        narratives['risk_narrative'] = self._explain_risk_score(
            risk_score, details.get('risk', {})
        )
        
        return narratives
    
    def _explain_location_score(self, score: float, details: Dict) -> str:
        """입지 점수 해석"""
        max_score = 25
        percentage = (score / max_score) * 100
        
        if percentage >= 80:
            level = "우수한"
            reason = "주요 교통망 접근성이 뛰어나고, 도심 인프라와의 연결성이 탁월합니다."
        elif percentage >= 60:
            level = "양호한"
            reason = "교통 접근성은 확보되어 있으나, 일부 생활편의시설까지의 거리가 다소 있습니다."
        elif percentage >= 40:
            level = "보통 수준의"
            reason = "기본적인 교통망은 갖추어져 있으나, 주요 인프라까지의 접근성 개선이 필요합니다."
        else:
            level = "미흡한"
            reason = "교통 접근성과 주변 인프라가 부족하여 입주자 유치에 어려움이 예상됩니다."
        
        narrative = f"""
        <strong>입지 적합성: {score:.1f}/{max_score}점</strong>
        <p>본 사업지는 <span class="highlight">{level} 입지 조건</span>을 갖추고 있습니다. {reason}</p>
        <ul>
            <li>교통 접근성: 지하철역까지 {details.get('subway_distance', '800m')}, 버스정류장 {details.get('bus_distance', '200m')} 거리</li>
            <li>생활 인프라: 대형마트 {details.get('mart_distance', '1.2km')}, 병원 {details.get('hospital_distance', '1.5km')}</li>
            <li>교육 시설: 초등학교 {details.get('elementary_distance', '500m')}, 중학교 {details.get('middle_distance', '800m')}</li>
        </ul>
        """
        
        return narrative.strip()
    
    def _explain_business_score(self, score: float, details: Dict) -> str:
        """사업성 점수 해석"""
        max_score = 30
        percentage = (score / max_score) * 100
        
        if percentage >= 80:
            level = "높은"
            reason = "세대수, 용적률, 건폐율이 최적화되어 사업성이 우수합니다."
        elif percentage >= 60:
            level = "적정한"
            reason = "기본적인 사업성은 확보되었으나, 일부 건축 조건 최적화가 필요합니다."
        elif percentage >= 40:
            level = "제한적인"
            reason = "용적률 또는 세대수 측면에서 사업성 개선 여지가 있습니다."
        else:
            level = "낮은"
            reason = "세대수 부족 또는 건축 제약으로 사업성 확보가 어렵습니다."
        
        narrative = f"""
        <strong>사업 타당성: {score:.1f}/{max_score}점</strong>
        <p><span class="highlight">{level} 사업 타당성</span>을 보이고 있습니다. {reason}</p>
        <ul>
            <li>세대수: {details.get('unit_count', 'N/A')}세대 (LH 권장 기준: 최소 30세대)</li>
            <li>용적률: {details.get('far', 'N/A')}% (지역 평균 대비 {details.get('far_comparison', '적정')})</li>
            <li>건폐율: {details.get('bcr', 'N/A')}% (법정 한도 내 {details.get('bcr_status', '양호')})</li>
        </ul>
        """
        
        return narrative.strip()
    
    def _explain_policy_score(self, score: float, details: Dict) -> str:
        """정책 부합성 점수 해석"""
        max_score = 20
        percentage = (score / max_score) * 100
        
        if percentage >= 80:
            level = "완전히 부합"
            reason = "LH 신축매입임대 우선 공급 대상지역이며, 정책 목표와 100% 일치합니다."
        elif percentage >= 60:
            level = "대체로 부합"
            reason = "LH 정책 기준을 충족하나, 일부 우선순위 항목 보완이 권장됩니다."
        elif percentage >= 40:
            level = "부분 부합"
            reason = "기본 요건은 충족하나, 정책 우선순위 항목에서 약점이 있습니다."
        else:
            level = "미흡"
            reason = "LH 정책 우선순위에서 벗어나 있어 사업 추진이 어려울 수 있습니다."
        
        narrative = f"""
        <strong>정책 부합성: {score:.1f}/{max_score}점</strong>
        <p>LH 신축매입임대 정책에 <span class="highlight">{level}</span>합니다. {reason}</p>
        <ul>
            <li>공급 유형 적합성: {details.get('unit_type_match', '신혼형')} (LH 우선 공급 유형)</li>
            <li>지역 정책: {details.get('regional_policy', '주거복지 우선지역 해당')}</li>
            <li>공공성: {details.get('public_benefit', '중산층 주거안정 기여도 높음')}</li>
        </ul>
        """
        
        return narrative.strip()
    
    def _explain_financial_score(self, score: float, details: Dict) -> str:
        """재무 건전성 점수 해석"""
        max_score = 15
        percentage = (score / max_score) * 100
        irr = details.get('irr', 0)
        roi = details.get('roi', 0)
        
        if percentage >= 80:
            level = "우수"
            reason = f"IRR {irr:.1f}%, ROI {roi:.1f}%로 투자 수익성이 뛰어납니다."
        elif percentage >= 60:
            level = "양호"
            reason = f"IRR {irr:.1f}%, ROI {roi:.1f}%로 안정적인 수익 구조를 갖추고 있습니다."
        elif percentage >= 40:
            level = "보통"
            reason = f"IRR {irr:.1f}%로 최소 수익성은 확보되었으나, 개선 여지가 있습니다."
        else:
            level = "부족"
            reason = f"IRR {irr:.1f}%로 투자 수익성이 낮아 재무 구조 개선이 필요합니다."
        
        narrative = f"""
        <strong>재무 건전성: {score:.1f}/{max_score}점</strong>
        <p>재무 건전성은 <span class="highlight">{level}</span> 수준입니다. {reason}</p>
        <ul>
            <li>IRR (내부수익률): {irr:.2f}% (LH 기준: 최소 2.0% 이상)</li>
            <li>ROI (투자수익률): {roi:.2f}% (10년 기준)</li>
            <li>총 투자비: {details.get('total_investment', 'N/A'):,}원</li>
            <li>LH 매입가: {details.get('lh_purchase_price', 'N/A'):,}원 (감정가 기준)</li>
        </ul>
        """
        
        return narrative.strip()
    
    def _explain_risk_score(self, score: float, details: Dict) -> str:
        """리스크 점수 해석"""
        max_score = 10
        percentage = (score / max_score) * 100
        
        # 리스크는 점수가 높을수록 좋음 (리스크가 낮음)
        if percentage >= 80:
            level = "매우 낮음"
            reason = "주요 리스크 요인이 거의 없어 안정적인 사업 추진이 가능합니다."
        elif percentage >= 60:
            level = "낮음"
            reason = "일부 관리 가능한 리스크가 있으나, 전체적으로 안정적입니다."
        elif percentage >= 40:
            level = "보통"
            reason = "중요 리스크 요인이 있어 면밀한 모니터링과 대응 계획이 필요합니다."
        else:
            level = "높음"
            reason = "치명적인 리스크 요인이 있어 사업 추진 전 반드시 해결이 필요합니다."
        
        narrative = f"""
        <strong>리스크 수준: {score:.1f}/{max_score}점</strong>
        <p>사업 리스크는 <span class="highlight">{level}</span> 수준입니다. {reason}</p>
        <ul>
            <li>규제 리스크: {details.get('regulatory_risk', '없음')}</li>
            <li>재무 리스크: {details.get('financial_risk', '낮음')}</li>
            <li>시장 리스크: {details.get('market_risk', '보통')}</li>
        </ul>
        """
        
        return narrative.strip()
    
    # ========================================================================
    # 2. Decision Reason Narrative
    # ========================================================================
    
    def generate_decision_narrative(
        self, 
        decision: str, 
        lh_score: float, 
        grade: str,
        critical_risks: List[str]
    ) -> str:
        """
        GO/REVIEW/NO-GO 결정에 대한 상세 근거 설명
        
        Args:
            decision: GO/REVIEW/NO_GO
            lh_score: LH 총점
            grade: A/B/C/D/F
            critical_risks: 치명적 리스크 목록
            
        Returns:
            의사결정 근거 설명 HTML
        """
        if decision == "GO":
            return self._explain_go_decision(lh_score, grade, critical_risks)
        elif decision == "REVIEW":
            return self._explain_review_decision(lh_score, grade, critical_risks)
        else:  # NO_GO
            return self._explain_no_go_decision(lh_score, grade, critical_risks)
    
    def _explain_go_decision(self, score: float, grade: str, risks: List[str]) -> str:
        """GO 결정 근거"""
        narrative = f"""
        <div class="decision-box decision-go">
            <h3>✅ 사업 추진 권장 (GO)</h3>
            <p class="decision-summary">
                본 사업은 <strong>LH {score:.1f}점 (등급 {grade})</strong>으로 
                <span class="highlight-green">사업 추진을 적극 권장</span>합니다.
            </p>
            
            <h4>📊 주요 근거</h4>
            <ul class="decision-reasons">
                <li><strong>높은 LH 점수:</strong> {score:.1f}점은 LH 평가 기준에서 우수한 수준으로, 
                매입 승인 가능성이 매우 높습니다.</li>
                <li><strong>안정적인 등급:</strong> {grade}등급은 사업 안정성과 수익성이 확보된 수준입니다.</li>
                <li><strong>낮은 리스크:</strong> 치명적인 리스크 요인이 없어 사업 진행이 안전합니다.</li>
            </ul>
            
            <h4>🎯 권장 사항</h4>
            <ul class="recommendations">
                <li>LH 신축매입임대 제안서 작성 및 제출 진행</li>
                <li>설계 및 인허가 절차 본격 착수</li>
                <li>금융기관 PF 대출 협의 시작</li>
            </ul>
        </div>
        """
        return narrative.strip()
    
    def _explain_review_decision(self, score: float, grade: str, risks: List[str]) -> str:
        """REVIEW 결정 근거"""
        narrative = f"""
        <div class="decision-box decision-review">
            <h3>⚠️ 보완 후 추진 검토 (REVIEW)</h3>
            <p class="decision-summary">
                본 사업은 <strong>LH {score:.1f}점 (등급 {grade})</strong>으로 
                <span class="highlight-yellow">일부 항목 보완 후 추진을 권장</span>합니다.
            </p>
            
            <h4>📊 주요 근거</h4>
            <ul class="decision-reasons">
                <li><strong>적정 LH 점수:</strong> {score:.1f}점은 LH 최소 기준을 충족하나, 
                경쟁력 확보를 위해 점수 향상이 필요합니다.</li>
                <li><strong>개선 가능 등급:</strong> {grade}등급은 일부 항목 보완으로 상위 등급 도달이 가능합니다.</li>
                <li><strong>관리 가능 리스크:</strong> {len(risks)}개의 리스크 요인이 있으나, 모두 대응 가능한 수준입니다.</li>
            </ul>
            
            <h4>🔧 필수 개선 사항</h4>
            <ul class="improvements-required">
        """
        
        if risks:
            for risk in risks:
                narrative += f"<li>{risk}</li>\n"
        else:
            narrative += "<li>세대수 증대 검토 (최소 30세대 이상 권장)</li>\n"
            narrative += "<li>용적률 최적화 방안 검토</li>\n"
            narrative += "<li>재무 구조 개선 (IRR 3.0% 이상 목표)</li>\n"
        
        narrative += """
            </ul>
            
            <h4>🎯 권장 사항</h4>
            <ul class="recommendations">
                <li>상기 개선 사항 반영 후 재평가 실시</li>
                <li>LH 사전 컨설팅 요청 검토</li>
                <li>설계 변경을 통한 사업성 개선 방안 검토</li>
            </ul>
        </div>
        """
        return narrative.strip()
    
    def _explain_no_go_decision(self, score: float, grade: str, risks: List[str]) -> str:
        """NO_GO 결정 근거"""
        narrative = f"""
        <div class="decision-box decision-no-go">
            <h3>🚫 사업 보류 권장 (NO-GO)</h3>
            <p class="decision-summary">
                본 사업은 <strong>LH {score:.1f}점 (등급 {grade})</strong>으로 
                <span class="highlight-red">현 시점에서 사업 추진을 보류</span>할 것을 권장합니다.
            </p>
            
            <h4>📊 주요 근거</h4>
            <ul class="decision-reasons">
                <li><strong>낮은 LH 점수:</strong> {score:.1f}점은 LH 최소 기준에 미달하여 
                매입 승인 가능성이 낮습니다.</li>
                <li><strong>미흡한 등급:</strong> {grade}등급은 사업성과 안정성이 부족한 수준입니다.</li>
                <li><strong>높은 리스크:</strong> {len(risks)}개의 치명적 리스크 요인이 있어 
                사업 추진 시 큰 손실 위험이 있습니다.</li>
            </ul>
            
            <h4>⚠️ 주요 리스크 요인</h4>
            <ul class="critical-risks">
        """
        
        if risks:
            for risk in risks:
                narrative += f"<li><strong>❌ {risk}</strong></li>\n"
        else:
            narrative += "<li><strong>❌ 세대수 부족:</strong> LH 최소 기준 미달</li>\n"
            narrative += "<li><strong>❌ 재무 건전성:</strong> IRR 2.0% 미만</li>\n"
            narrative += "<li><strong>❌ 입지 적합성:</strong> 교통 및 인프라 접근성 부족</li>\n"
        
        narrative += """
            </ul>
            
            <h4>🎯 권장 사항</h4>
            <ul class="recommendations">
                <li>사업지 재검토 또는 대체 부지 탐색</li>
                <li>근본적인 사업 구조 재설계 필요</li>
                <li>LH 사업 외 다른 사업 모델 검토</li>
            </ul>
        </div>
        """
        return narrative.strip()
    
    # ========================================================================
    # 3. Risk Explanation Narrative
    # ========================================================================
    
    def generate_risk_explanations(self, risks: Dict[str, Any]) -> Dict[str, str]:
        """
        각 리스크 항목에 대한 상세 설명 생성
        
        Args:
            risks: Risk assessment 결과
            
        Returns:
            각 리스크 유형별 설명 딕셔너리
        """
        explanations = {}
        
        risk_types = [
            'regulatory_risk',
            'financial_risk', 
            'land_cost_risk',
            'unit_type_risk',
            'unit_count_risk',
            'other_business_risk'
        ]
        
        for risk_type in risk_types:
            risk_data = risks.get(risk_type, {})
            explanations[risk_type] = self._explain_specific_risk(risk_type, risk_data)
        
        return explanations
    
    def _explain_specific_risk(self, risk_type: str, risk_data: Dict) -> str:
        """특정 리스크 유형 설명"""
        risk_templates = {
            'regulatory_risk': {
                'title': '규제 리스크',
                'high': '용도지역 또는 건축 규제 위반 가능성이 있어 인허가가 불가능할 수 있습니다.',
                'medium': '일부 규제 기준에 근접하여 설계 변경이 필요할 수 있습니다.',
                'low': '모든 규제 기준을 충족하여 리스크가 없습니다.'
            },
            'financial_risk': {
                'title': '재무 리스크',
                'high': 'IRR 2.0% 미만으로 투자 수익성이 매우 낮아 사업 추진이 어렵습니다.',
                'medium': 'IRR이 최소 기준에 근접하여 재무 구조 개선이 필요합니다.',
                'low': 'IRR 3.0% 이상으로 안정적인 수익 구조를 확보하고 있습니다.'
            },
            'land_cost_risk': {
                'title': '토지비 리스크',
                'high': '토지비가 총 투자비의 60% 이상으로 과도하게 높아 수익성 확보가 어렵습니다.',
                'medium': '토지비 비중이 다소 높아 건축비 절감 등 대응 방안이 필요합니다.',
                'low': '토지비 비중이 적정하여 리스크가 없습니다.'
            },
            'unit_type_risk': {
                'title': '세대유형 리스크',
                'high': '추천 세대유형의 적합성이 낮아(50점 미만) 수요 확보가 어렵습니다.',
                'medium': '추천 세대유형이 적정하나, 일부 기준 보완이 필요합니다.',
                'low': '추천 세대유형이 매우 적합하여(85점 이상) 리스크가 없습니다.'
            },
            'unit_count_risk': {
                'title': '세대수 리스크',
                'high': '세대수가 30세대 미만으로 LH 최소 기준에 미달합니다.',
                'medium': '세대수가 최소 기준에 근접하여 증대 방안 검토가 필요합니다.',
                'low': '세대수가 충분하여 리스크가 없습니다.'
            },
            'other_business_risk': {
                'title': '기타 사업 리스크',
                'high': '복합적인 사업 리스크 요인이 있어 종합적인 대응 방안이 필요합니다.',
                'medium': '일부 관리 가능한 리스크 요인이 있습니다.',
                'low': '기타 사업 리스크 요인이 없습니다.'
            }
        }
        
        template = risk_templates.get(risk_type, {})
        title = template.get('title', risk_type)
        level = risk_data.get('level', 'low')
        description = template.get(level, '리스크 평가 중입니다.')
        
        return f"<strong>{title}:</strong> {description}"
    
    # ========================================================================
    # 4. Strategy Proposal Narrative
    # ========================================================================
    
    def generate_strategy_proposals(
        self, 
        lh_result: Dict[str, Any],
        decision_result: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        개선 전략 제안 생성 (다음 행동 계획)
        
        Args:
            lh_result: LH Score 결과
            decision_result: Decision Engine 결과
            
        Returns:
            전략 제안 리스트 [{'title': '', 'description': '', 'impact': '', 'priority': ''}]
        """
        proposals = []
        
        weaknesses = lh_result.get('weaknesses', [])
        current_score = lh_result.get('total_score', 0)
        grade = lh_result.get('grade', 'F')
        decision = decision_result.get('decision', 'NO_GO')
        
        # 점수 구간별 전략
        if current_score < 50:
            # Critical: 근본적인 재설계 필요
            proposals.extend(self._generate_critical_strategies(weaknesses))
        elif current_score < 70:
            # Important: 주요 항목 개선 필요
            proposals.extend(self._generate_important_strategies(weaknesses))
        else:
            # Optimization: 최적화 방안
            proposals.extend(self._generate_optimization_strategies(weaknesses))
        
        return proposals
    
    def _generate_critical_strategies(self, weaknesses: List[str]) -> List[Dict]:
        """치명적 문제 해결 전략"""
        strategies = [
            {
                'title': '🚨 사업지 재검토',
                'description': '현재 사업지는 LH 기준에 크게 미달하여, 대체 부지 탐색 또는 근본적인 사업 구조 재설계가 필요합니다.',
                'impact': '+20~30점 예상 (새로운 부지 선정 시)',
                'priority': '최우선',
                'timeline': '즉시'
            },
            {
                'title': '📐 설계 전면 재검토',
                'description': '세대수, 용적률, 동 배치 등 전체 설계안을 LH 기준에 맞춰 재설계해야 합니다.',
                'impact': '+10~15점 예상',
                'priority': '최우선',
                'timeline': '1개월 이내'
            }
        ]
        return strategies
    
    def _generate_important_strategies(self, weaknesses: List[str]) -> List[Dict]:
        """주요 개선 전략"""
        strategies = [
            {
                'title': '🏗️ 세대수 증대 방안',
                'description': '현재 설계안에서 세대수를 10~15% 증가시켜 LH 최소 기준(30세대)을 충족하고 사업성을 개선합니다.',
                'impact': '+5~8점 예상',
                'priority': '높음',
                'timeline': '2주 이내'
            },
            {
                'title': '📊 용적률 최적화',
                'description': '법정 용적률 한도 내에서 최대한 활용하여 사업성을 극대화합니다.',
                'impact': '+3~5점 예상',
                'priority': '높음',
                'timeline': '2주 이내'
            },
            {
                'title': '💰 재무 구조 개선',
                'description': '건축비 절감, 금융 조건 개선 등을 통해 IRR을 3.0% 이상으로 향상시킵니다.',
                'impact': '+4~6점 예상',
                'priority': '높음',
                'timeline': '1개월 이내'
            }
        ]
        return strategies
    
    def _generate_optimization_strategies(self, weaknesses: List[str]) -> List[Dict]:
        """최적화 전략"""
        strategies = [
            {
                'title': '✨ 세대유형 최적화',
                'description': '추천 세대유형(신혼형/청년형)에 특화된 설계 요소를 강화하여 입주자 만족도를 높입니다.',
                'impact': '+2~3점 예상',
                'priority': '보통',
                'timeline': '2주 이내'
            },
            {
                'title': '🎨 차별화 요소 추가',
                'description': '친환경 설계, 커뮤니티 시설 강화 등 차별화 요소를 추가하여 경쟁력을 확보합니다.',
                'impact': '+1~2점 예상',
                'priority': '보통',
                'timeline': '1개월 이내'
            },
            {
                'title': '📋 LH 사전 컨설팅',
                'description': 'LH에 사전 컨설팅을 요청하여 매입 가능성을 높이고 리스크를 최소화합니다.',
                'impact': '승인 가능성 +15~20%',
                'priority': '높음',
                'timeline': '즉시'
            }
        ]
        return strategies


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    print("✅ Narrative Generator v11.0 Module Loaded")
    print("="*60)
    
    # Test
    generator = NarrativeGenerator()
    
    # Test LH Score Narrative
    test_lh_result = {
        'total_score': 66.5,
        'grade': 'D',
        'category_scores': {
            'location_suitability': 18.0,
            'business_feasibility': 23.0,
            'policy_alignment': 16.0,
            'financial_soundness': 12.0,
            'risk_level': 7.0
        },
        'score_details': {
            'location': {
                'subway_distance': '800m',
                'bus_distance': '200m',
                'mart_distance': '1.2km',
                'hospital_distance': '1.5km',
                'elementary_distance': '500m',
                'middle_distance': '800m'
            },
            'business': {
                'unit_count': 45,
                'far': 180,
                'far_comparison': '적정',
                'bcr': 55,
                'bcr_status': '양호'
            },
            'financial': {
                'irr': 3.6,
                'roi': 37.11,
                'total_investment': 16500000000,
                'lh_purchase_price': 14800000000
            }
        },
        'weaknesses': ['세대수 부족', '교통 접근성']
    }
    
    narratives = generator.generate_score_narrative(test_lh_result)
    print("\n📊 Score Narratives Generated:")
    print(f"  - Location: {len(narratives['location_narrative'])} chars")
    print(f"  - Business: {len(narratives['business_narrative'])} chars")
    print(f"  - Policy: {len(narratives['policy_narrative'])} chars")
    
    # Test Decision Narrative
    decision_text = generator.generate_decision_narrative(
        'REVIEW', 66.5, 'D', ['세대수 부족', '재무 구조 개선 필요']
    )
    print(f"\n✅ Decision Narrative: {len(decision_text)} chars")
    
    # Test Strategy Proposals
    test_decision = {'decision': 'REVIEW'}
    strategies = generator.generate_strategy_proposals(test_lh_result, test_decision)
    print(f"\n🎯 Strategy Proposals: {len(strategies)} strategies generated")
    
    print("\n" + "="*60)
    print("✅ Narrative Generator Test Complete")
