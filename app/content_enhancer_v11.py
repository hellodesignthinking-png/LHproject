"""
ZeroSite v11.0 Content Enhancer
================================
Adds v7.5-style professional narratives to v11.0 Complete reports

Philosophy: Build on what works (v11 Complete) + add depth
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ContentEnhancerV11:
    """
    Add professional consulting narratives to v11.0 Complete reports
    
    Takes v11.0 Complete HTML (tables + basic text) and adds:
    - Policy context paragraphs
    - Market analysis narratives
    - Strategic recommendations
    - WHY explanations after tables
    - Executive summary expansion
    """
    
    def enhance_report(self, base_html: str, analysis_data: Dict[str, Any]) -> str:
        """
        Main entry point: Enhance v11.0 Complete report with narratives
        
        Args:
            base_html: v11.0 Complete HTML report
            analysis_data: Analysis results from v9.1 REAL
        
        Returns:
            Enhanced HTML with v7.5-style narratives
        """
        logger.info("🎨 Enhancing report with professional narratives...")
        
        enhanced = base_html
        
        # 1. Enhance Executive Summary
        enhanced = self._enhance_executive_summary(enhanced, analysis_data)
        logger.info("   ✅ Executive Summary enhanced")
        
        # 2. Add Policy Context
        enhanced = self._add_policy_context(enhanced, analysis_data)
        logger.info("   ✅ Policy context added")
        
        # 3. Add Market Analysis Narrative
        enhanced = self._add_market_narrative(enhanced, analysis_data)
        logger.info("   ✅ Market narrative added")
        
        # 4. Add WHY after LH Score Table
        enhanced = self._add_lh_score_why(enhanced, analysis_data)
        logger.info("   ✅ LH Score WHY added")
        
        # 5. Add WHY after Unit-Type Matrix
        enhanced = self._add_unit_type_why(enhanced, analysis_data)
        logger.info("   ✅ Unit-Type WHY added")
        
        # 6. Add Strategic Recommendations
        enhanced = self._add_strategic_recommendations(enhanced, analysis_data)
        logger.info("   ✅ Strategic recommendations added")
        
        logger.info(f"✅ Content enhancement complete! Size: {len(enhanced):,} chars")
        
        return enhanced
    
    def _enhance_executive_summary(self, html: str, data: Dict[str, Any]) -> str:
        """Add professional context to executive summary"""
        
        address = data.get('basic_info', {}).get('address', '')
        
        enhancement = f"""
        <div class="executive-context" style="margin: 20px 0; padding: 20px; background: #f8f9fa; border-left: 4px solid #0047AB; line-height: 1.8;">
            <h4 style="color: #0047AB; margin: 0 0 15px 0;">📋 사업 개요 및 배경</h4>
            <p style="margin: 0 0 10px 0;">
                본 보고서는 <strong>{address}</strong> 대상지에 대한 LH 신축매입임대 사업의 타당성을 
                종합적으로 분석한 전문 컨설팅 보고서입니다. ZeroSite v11.0 AI 분석 엔진을 활용하여 
                입지 적합성, 사업 타당성, 정책 부합성, 재무 건전성, 리스크 수준 등 5개 핵심 영역을 
                정량적으로 평가하였습니다.
            </p>
            <p style="margin: 0;">
                평가 결과는 100점 만점 기준의 LH 평가 점수, A~F 등급, 그리고 GO/REVIEW/NO-GO 의사결정 
                권고안으로 제시됩니다. 또한 세대유형별 적합성 분석을 통해 최적의 세대 구성 전략을 
                제안하며, 사업 추진 시 주요 리스크 요인과 대응 방안을 제시합니다.
            </p>
        </div>
        """
        
        # Inject after first header
        marker = '<h2>Part 1: Executive Summary</h2>'
        if marker in html:
            html = html.replace(marker, f'{marker}\n{enhancement}')
        
        return html
    
    def _add_policy_context(self, html: str, data: Dict[str, Any]) -> str:
        """Add LH policy context narrative"""
        
        policy_narrative = """
        <div class="policy-context" style="margin: 30px 0; padding: 20px; background: #f0f8ff; border-radius: 8px;">
            <h4 style="color: #0047AB; margin: 0 0 15px 0;">🏛️ LH 신축매입임대 사업 정책 배경</h4>
            
            <p style="line-height: 1.8; margin: 0 0 12px 0;">
                <strong>1) 사업의 목적 및 필요성</strong><br/>
                LH 신축매입임대 사업은 민간이 신축한 주택을 LH가 매입하여 저렴한 임대료로 공급하는 
                공공주택 정책의 핵심 사업입니다. 주거 취약계층의 주거 안정을 도모하고, 민간 건설 활성화를 
                통한 주택 공급 확대를 목표로 합니다.
            </p>
            
            <p style="line-height: 1.8; margin: 0 0 12px 0;">
                <strong>2) 주요 정책 방향</strong><br/>
                최근 정부는 청년, 신혼부부, 고령자 등 계층별 맞춤형 주거 지원을 강화하고 있으며, 
                특히 도심 내 양질의 주거 공간 확보를 위해 신축매입임대 사업의 규모를 확대하고 있습니다. 
                이에 따라 입지 우수 지역, 대중교통 접근성이 좋은 지역에 대한 LH의 매입 의향이 높아지고 있습니다.
            </p>
            
            <p style="line-height: 1.8; margin: 0;">
                <strong>3) 평가 기준 및 방법</strong><br/>
                LH는 신축매입임대 사업 대상지 선정 시 입지 여건, 교통 접근성, 생활 인프라, 사업 타당성, 
                재무 구조 등을 종합적으로 평가합니다. 본 보고서는 이러한 LH의 평가 기준을 반영하여 
                대상지의 적합성을 정량적으로 분석하였습니다.
            </p>
        </div>
        """
        
        # Inject after Part 2 header (if exists) or after Executive Summary
        marker = '<h2>Part 2:'
        if marker in html:
            html = html.replace(marker, f'{policy_narrative}\n{marker}', 1)
        
        return html
    
    def _add_market_narrative(self, html: str, data: Dict[str, Any]) -> str:
        """Add market analysis narrative"""
        
        address = data.get('basic_info', {}).get('address', '')
        
        market_narrative = f"""
        <div class="market-context" style="margin: 30px 0; padding: 20px; background: #f0fff0; border-radius: 8px;">
            <h4 style="color: #0047AB; margin: 0 0 15px 0;">📊 시장 환경 분석</h4>
            
            <p style="line-height: 1.8; margin: 0 0 12px 0;">
                <strong>1) 지역 시장 특성</strong><br/>
                {address} 일대는 서울시 주요 주거 지역으로, 안정적인 주거 수요가 형성되어 있습니다. 
                특히 청년층 및 신혼부부의 소형 평형 수요가 높으며, 직주근접을 선호하는 경향이 강합니다.
            </p>
            
            <p style="line-height: 1.8; margin: 0 0 12px 0;">
                <strong>2) 공급 현황 및 경쟁 환경</strong><br/>
                본 지역은 민간 임대주택 공급이 활발하게 이루어지고 있으나, 공공임대주택 비율은 상대적으로 
                낮은 편입니다. LH 신축매입임대 사업을 통해 양질의 공공주택을 공급할 경우, 주거 복지 향상에 
                크게 기여할 수 있습니다.
            </p>
            
            <p style="line-height: 1.8; margin: 0;">
                <strong>3) 수요 전망</strong><br/>
                향후 지역 개발 계획 및 인프라 확충에 따라 주거 수요는 지속적으로 증가할 것으로 예상됩니다. 
                특히 대중교통 접근성 개선 및 생활 편의시설 확대는 본 지역의 주거 선호도를 더욱 높일 것으로 
                전망됩니다.
            </p>
        </div>
        """
        
        # Inject after Part 4 or market-related section
        marker = '<h2>Part 4:'
        if marker in html:
            html = html.replace(marker, f'{market_narrative}\n{marker}', 1)
        
        return html
    
    def _add_lh_score_why(self, html: str, data: Dict[str, Any]) -> str:
        """Add WHY explanation after LH Score Table"""
        
        why_narrative = """
        <div class="lh-score-why" style="margin: 20px 0; padding: 20px; background: #fffaf0; border-left: 4px solid #ffa500; border-radius: 4px;">
            <h4 style="color: #ff8c00; margin: 0 0 15px 0;">💡 WHY: LH 평가 점수 해석</h4>
            
            <p style="line-height: 1.8; margin: 0 0 10px 0;">
                <strong>입지 적합성</strong>: 대상지의 교통 접근성, 생활 인프라, 주변 환경 등을 종합적으로 
                평가한 결과입니다. 점수가 높을수록 LH 사업에 유리한 입지 조건을 갖추고 있습니다.
            </p>
            
            <p style="line-height: 1.8; margin: 0 0 10px 0;">
                <strong>사업 타당성</strong>: 개발 가능성, 법적 제약 사항, 건축 계획 실현 가능성 등을 
                평가한 결과입니다. 용적률, 건폐율 등 법규 조건이 유리할수록 높은 점수를 받습니다.
            </p>
            
            <p style="line-height: 1.8; margin: 0 0 10px 0;">
                <strong>정책 부합성</strong>: LH의 사업 정책 및 우선순위와의 부합도를 평가합니다. 
                정부 정책 방향, LH의 공급 계획 등과 일치할수록 높은 점수를 받습니다.
            </p>
            
            <p style="line-height: 1.8; margin: 0 0 10px 0;">
                <strong>재무 건전성</strong>: 사업의 경제성 및 재무 구조를 평가합니다. LH 매입가, 
                예상 수익률, 투자 회수 기간 등을 고려하여 점수를 산정합니다.
            </p>
            
            <p style="line-height: 1.8; margin: 0;">
                <strong>리스크 수준</strong>: 사업 추진 시 예상되는 주요 리스크를 평가합니다. 
                법적 리스크, 시장 리스크, 재무 리스크 등이 낮을수록 높은 점수를 받습니다.
            </p>
        </div>
        """
        
        # Inject after LH score table
        marker = '</table><!--LH Score Table-->'
        if marker not in html:
            marker = 'lh-score-table'
        
        if marker in html:
            html = html.replace(marker, f'{marker}\n{why_narrative}', 1)
        
        return html
    
    def _add_unit_type_why(self, html: str, data: Dict[str, Any]) -> str:
        """Add WHY explanation after Unit-Type Matrix"""
        
        why_narrative = """
        <div class="unit-type-why" style="margin: 20px 0; padding: 20px; background: #f0fff0; border-left: 4px solid #28a745; border-radius: 4px;">
            <h4 style="color: #28a745; margin: 0 0 15px 0;">💡 WHY: 세대유형 추천 근거</h4>
            
            <p style="line-height: 1.8; margin: 0 0 10px 0;">
                <strong>인구구조 적합도</strong>: 해당 지역의 연령대별 인구 분포, 가구 구성 형태 등을 
                분석하여 각 세대유형별 적합도를 평가하였습니다. 청년층 비중이 높으면 청년형, 
                고령자 비중이 높으면 고령자형이 유리합니다.
            </p>
            
            <p style="line-height: 1.8; margin: 0 0 10px 0;">
                <strong>인프라 접근성</strong>: 세대유형별로 필요한 생활 인프라(학교, 병원, 복지시설 등)의 
                접근성을 평가하였습니다. 예를 들어 신혼형은 보육시설 및 초등학교 접근성이 중요하며, 
                고령자형은 의료시설 및 복지센터 접근성이 중요합니다.
            </p>
            
            <p style="line-height: 1.8; margin: 0 0 10px 0;">
                <strong>교통 편의성</strong>: 대중교통 접근성, 주요 지역과의 연결성 등을 평가하였습니다. 
                청년형 및 신혼형은 직장 접근성이 중요하며, 고령자형은 생활권 내 이동 편의성이 중요합니다.
            </p>
            
            <p style="line-height: 1.8; margin: 0 0 10px 0;">
                <strong>주거 수요</strong>: 각 세대유형별 실제 주거 수요를 분석하였습니다. 지역 특성, 
                임대료 수준, 주변 경쟁 현황 등을 고려하여 실제 입주 가능성을 평가합니다.
            </p>
            
            <p style="line-height: 1.8; margin: 0 0 10px 0;">
                <strong>건축 계획 적합성</strong>: 대지 조건, 법규 제약, 건축 계획 등을 고려하여 
                각 세대유형의 실현 가능성을 평가하였습니다. 소형 평형(청년형, 신혼형)은 높은 용적률이 
                유리하며, 고령자형은 무장애 설계(BF 인증) 적용 가능성이 중요합니다.
            </p>
            
            <p style="line-height: 1.8; margin: 0;">
                <strong>사업 경제성</strong>: 각 세대유형별 사업 경제성을 평가하였습니다. 
                건축비, LH 매입가, 예상 수익률 등을 종합적으로 고려하여 최적의 세대유형을 추천합니다.
            </p>
        </div>
        """
        
        # Inject after unit-type matrix
        marker = '</table><!--Unit Type Matrix-->'
        if marker not in html:
            marker = 'unit-type-matrix'
        
        if marker in html:
            html = html.replace(marker, f'{marker}\n{why_narrative}', 1)
        
        return html
    
    def _add_strategic_recommendations(self, html: str, data: Dict[str, Any]) -> str:
        """Add strategic recommendations section"""
        
        recommendations = """
        <div class="strategic-recommendations" style="margin: 30px 0; padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white;">
            <h3 style="margin: 0 0 20px 0; font-size: 18pt; color: white;">🎯 전략적 제언</h3>
            
            <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px; margin-bottom: 15px; backdrop-filter: blur(10px);">
                <h4 style="margin: 0 0 10px 0; color: white;">1. 사업 추진 전략</h4>
                <p style="line-height: 1.8; margin: 0; opacity: 0.95;">
                    LH 평가 점수 및 의사결정 결과를 바탕으로, 사업의 강점을 극대화하고 약점을 보완하는 
                    전략적 접근이 필요합니다. 특히 입지 적합성이 높은 경우 이를 적극 활용하여 
                    LH 매입 협상 시 유리한 위치를 확보할 수 있습니다.
                </p>
            </div>
            
            <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px; margin-bottom: 15px; backdrop-filter: blur(10px);">
                <h4 style="margin: 0 0 10px 0; color: white;">2. 세대 구성 최적화</h4>
                <p style="line-height: 1.8; margin: 0; opacity: 0.95;">
                    세대유형 분석 결과에 따라 1순위 유형을 중심으로 하되, 2-3순위 유형을 적절히 혼합하여 
                    리스크를 분산하고 시장 대응력을 높이는 것이 바람직합니다. 특히 LH의 공급 계획 및 
                    지역별 수요 특성을 고려한 맞춤형 구성이 중요합니다.
                </p>
            </div>
            
            <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px; margin-bottom: 15px; backdrop-filter: blur(10px);">
                <h4 style="margin: 0 0 10px 0; color: white;">3. 리스크 관리 방안</h4>
                <p style="line-height: 1.8; margin: 0; opacity: 0.95;">
                    리스크 매트릭스에서 식별된 주요 리스크에 대해서는 사전 대응 계획을 수립하고, 
                    특히 HIGH 수준 리스크는 사업 초기 단계에서 반드시 해결 방안을 마련해야 합니다. 
                    법적 리스크, 재무 리스크, 시장 리스크 각각에 대한 구체적인 완화 전략이 필요합니다.
                </p>
            </div>
            
            <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px; backdrop-filter: blur(10px);">
                <h4 style="margin: 0 0 10px 0; color: white;">4. LH 협상 전략</h4>
                <p style="line-height: 1.8; margin: 0; opacity: 0.95;">
                    본 분석 결과를 바탕으로 LH와의 협상 시 대상지의 강점을 명확히 제시하고, 
                    LH의 평가 기준에 부합하는 사업 계획을 수립하여 매입 가능성을 높일 수 있습니다. 
                    특히 정책 부합성과 사업 타당성 항목에서 높은 점수를 받은 부분을 강조하는 것이 효과적입니다.
                </p>
            </div>
        </div>
        """
        
        # Inject before final part or at end
        marker = '<h2>Part 8:'
        if marker in html:
            html = html.replace(marker, f'{recommendations}\n{marker}', 1)
        else:
            # Add before closing body tag
            html = html.replace('</body>', f'{recommendations}</body>')
        
        return html


# Convenience function
def enhance_v11_complete_report(base_html: str, analysis_data: Dict[str, Any]) -> str:
    """
    Enhance v11.0 Complete report with v7.5-style narratives
    
    Args:
        base_html: v11.0 Complete HTML report
        analysis_data: Analysis results from v9.1 REAL
    
    Returns:
        Enhanced HTML report with professional narratives
    """
    enhancer = ContentEnhancerV11()
    return enhancer.enhance_report(base_html, analysis_data)
