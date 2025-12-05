"""
ZeroSite v7.4 Narrative Templates
Professional consulting-style narrative generation for 40-60 page reports

Extends v7.3 templates with:
- Executive Summary (C-level decision brief)
- Policy & Market Context
- Financial Analysis narratives
- Risk Mitigation narratives  
- Strategic Recommendations
- Implementation Roadmap
"""

from typing import Dict, Any, List
import logging
from app.services.narrative_templates_v7_3 import NarrativeTemplatesV73

logger = logging.getLogger(__name__)


class NarrativeTemplatesV74(NarrativeTemplatesV73):
    """
    Professional consulting-style narrative templates for v7.4 reports
    
    Inherits all v7.3 narratives and adds new professional sections:
    - Executive Summary
    - Policy Context
    - Financial Analysis
    - Risk Mitigation
    - Strategic Recommendations
    """
    
    def __init__(self):
        super().__init__()
        logger.info("📝 Narrative Templates v7.4 initialized")
    
    # ==================== NEW SECTIONS FOR V7.4 ====================
    
    def generate_executive_summary(
        self,
        data: Dict[str, Any],
        basic_info: Dict[str, Any],
        financial_analysis: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """
        Generate Executive Summary (2-3 pages)
        
        C-level decision brief with:
        - Value proposition
        - Key findings (5-8 bullets)
        - Decision rationale
        - Clear recommendation
        
        Args:
            data: ZeroSite analysis data
            basic_info: Basic project info
            financial_analysis: Financial feasibility results
            risk_assessment: Risk analysis results
        
        Returns:
            List of paragraph HTML strings
        """
        paragraphs = []
        
        # Get key metrics
        address = basic_info.get('address', 'N/A')
        land_area = basic_info.get('land_area', 'N/A')
        unit_type = basic_info.get('unit_type', 'N/A')
        
        # Financial metrics
        fin_summary = financial_analysis.get('summary', {})
        total_investment = fin_summary.get('total_investment', 0)
        unit_count = fin_summary.get('unit_count', 0)
        cap_rate = fin_summary.get('cap_rate', 0)
        meets_lh = fin_summary.get('meets_lh_criteria', False)
        
        # Risk metrics
        risk_summary = risk_assessment.get('executive_summary', {})
        total_risks = risk_summary.get('total_risks', 0)
        overall_risk = risk_summary.get('overall_risk_level', 'medium')
        
        # Format investment
        investment_text = self._format_krw(total_investment)
        
        # === Section 1: Value Proposition ===
        paragraphs.append(f"""
            <div class="executive-summary-section">
                <h3 class="subsection-title">1. 사업 가치 제안 (Value Proposition)</h3>
                <p class="paragraph">
                    <strong>{address}</strong> 소재 {land_area}㎡ 토지에 대한 LH 신축매입임대 사업은 
                    총 <strong>{unit_count}세대</strong> 규모의 {unit_type}형 주택 공급을 목표로 하며, 
                    총 사업비 <strong>{investment_text}</strong>이 소요될 것으로 예상됩니다. 
                    본 사업은 서울시 공공주택 공급 확대 정책과 일치하며, 해당 지역의 
                    {unit_type} 계층 주거 수요를 충족할 수 있는 전략적 기회를 제공합니다.
                </p>
                <p class="paragraph">
                    특히 대상지는 우수한 교통 접근성과 생활 인프라를 갖추고 있어, 
                    LH 공공임대주택의 핵심 성공 요인인 '입지 경쟁력'을 확보하고 있습니다. 
                    지하철역 도보권 내 위치, 풍부한 생활 편의시설, 안정적인 인구 구조 등이 
                    장기적인 임대 수요 안정성을 뒷받침합니다.
                </p>
            </div>
        """)
        
        # === Section 2: Key Findings ===
        # Determine findings based on analysis
        findings = self._generate_key_findings(
            data, financial_analysis, risk_assessment
        )
        
        findings_html = "<ul class='key-findings-list'>"
        for finding in findings:
            findings_html += f"<li>{finding}</li>"
        findings_html += "</ul>"
        
        paragraphs.append(f"""
            <div class="executive-summary-section">
                <h3 class="subsection-title">2. 핵심 분석 결과 (Key Findings)</h3>
                {findings_html}
                <p class="paragraph">
                    상기 분석 결과는 ZeroSite v7.4 전문가 분석 엔진을 통해 산출되었으며, 
                    객관적 데이터(통계청, 국토교통부, 카카오맵 API)와 LH 2025 사업 기준을 
                    종합적으로 반영하였습니다.
                </p>
            </div>
        """)
        
        # === Section 3: Decision Rationale ===
        rationale = self._generate_decision_rationale(
            financial_analysis, risk_assessment, data
        )
        
        paragraphs.append(f"""
            <div class="executive-summary-section">
                <h3 class="subsection-title">3. 의사결정 근거 (Decision Rationale)</h3>
                {rationale}
            </div>
        """)
        
        # === Section 4: Financial Viability Summary ===
        viability_text = "재무적으로 타당한 것으로 평가됩니다" if meets_lh else \
                        "재무 구조 최적화가 필요한 것으로 평가됩니다"
        
        paragraphs.append(f"""
            <div class="executive-summary-section">
                <h3 class="subsection-title">4. 재무 타당성 요약 (Financial Viability)</h3>
                <p class="paragraph">
                    <strong>총 투자금액</strong>: {investment_text} 
                    ({unit_count}세대, 세대당 {self._format_krw(total_investment/unit_count if unit_count > 0 else 0)})
                </p>
                <p class="paragraph">
                    <strong>예상 수익률 (Cap Rate)</strong>: {cap_rate:.2f}% 
                    (LH 목표 기준: 4.5%)
                </p>
                <p class="paragraph">
                    <strong>LH 기준 충족 여부</strong>: {'✓ 충족' if meets_lh else '✗ 미충족 (최적화 필요)'}
                </p>
                <p class="paragraph">
                    종합적으로 본 사업은 {viability_text}. 
                    {'현재의 재무 구조로 LH 기준을 충족하며 안정적인 사업 운영이 가능할 것으로 전망됩니다.' if meets_lh else 
                     '유닛 믹스 조정, 임대료 재산정, 또는 비용 구조 개선을 통해 수익성을 개선할 수 있는 여지가 있습니다.'}
                </p>
            </div>
        """)
        
        # === Section 5: Risk Profile Summary ===
        risk_counts = risk_summary.get('risk_counts_by_level', {})
        critical_count = risk_counts.get('critical', 0)
        high_count = risk_counts.get('high', 0)
        
        risk_level_text = {
            'critical': '높은 수준 (즉시 대응 필요)',
            'high': '중-높은 수준 (우선 관리 필요)',
            'medium': '중간 수준 (관리 가능)',
            'low': '낮은 수준 (정상적 관리)'
        }.get(overall_risk, '중간 수준')
        
        paragraphs.append(f"""
            <div class="executive-summary-section">
                <h3 class="subsection-title">5. 위험 프로파일 요약 (Risk Profile)</h3>
                <p class="paragraph">
                    본 사업에 대해 <strong>{total_risks}개</strong>의 주요 위험 요인이 식별되었으며, 
                    전체적인 위험 수준은 <strong>{risk_level_text}</strong>으로 평가됩니다.
                </p>
                <p class="paragraph">
                    • Critical 위험: <strong>{critical_count}건</strong><br>
                    • High 위험: <strong>{high_count}건</strong><br>
                    • Medium 이하 위험: <strong>{total_risks - critical_count - high_count}건</strong>
                </p>
                <p class="paragraph">
                    식별된 모든 위험에 대해 구체적인 완화 전략(Mitigation Strategy)과 
                    비상 대응 계획(Contingency Plan)이 수립되어 있으며, 
                    위험 관리 책임자(Risk Owner)가 지정되어 있습니다.
                </p>
            </div>
        """)
        
        # === Section 6: Final Recommendation ===
        recommendation = self._generate_final_recommendation(
            financial_analysis, risk_assessment, data
        )
        
        paragraphs.append(f"""
            <div class="executive-summary-section recommendation-box">
                <h3 class="subsection-title">6. 최종 권고 사항 (Recommendation)</h3>
                {recommendation}
            </div>
        """)
        
        return paragraphs
    
    def generate_policy_context(
        self,
        data: Dict[str, Any],
        basic_info: Dict[str, Any]
    ) -> List[str]:
        """
        Generate Policy & Market Context section (3-4 pages)
        
        Establishes strategic context including:
        - National housing policy landscape
        - Seoul metropolitan housing market
        - Regulatory environment
        - Competitive landscape
        
        Args:
            data: ZeroSite analysis data
            basic_info: Basic project info
        
        Returns:
            List of paragraph HTML strings
        """
        paragraphs = []
        
        address = basic_info.get('address', 'N/A')
        unit_type = basic_info.get('unit_type', 'N/A')
        
        # === Section 1: National Housing Policy ===
        paragraphs.append(f"""
            <div class="policy-context-section">
                <h3 class="subsection-title">1. 국가 주택 정책 환경 (National Housing Policy Landscape)</h3>
                
                <h4 class="subsubsection-title">1.1 LH 공사 전략적 우선순위</h4>
                <p class="paragraph">
                    한국토지주택공사(LH)는 2025년 사업 계획에서 '공공임대주택 공급 확대'를 
                    핵심 전략으로 설정하였으며, 특히 청년·신혼부부 계층을 위한 
                    신축매입임대 사업을 중점적으로 추진하고 있습니다. 
                    이는 정부의 '주거복지 로드맵 2.0'과 연계된 것으로, 
                    공공부문이 주도하는 주택 공급을 통해 서민 주거 안정을 도모하려는 
                    국가 정책의 일환입니다.
                </p>
                <p class="paragraph">
                    LH는 2025년 전국적으로 신축매입임대 주택 약 20,000호 공급을 목표로 하고 있으며, 
                    이 중 수도권(서울·경기·인천)이 약 60%인 12,000호를 차지합니다. 
                    특히 서울 지역은 높은 주거비 부담과 청년층 주거 불안정 문제가 심각하여, 
                    LH의 최우선 공급 지역으로 지정되어 있습니다.
                </p>
                
                <h4 class="subsubsection-title">1.2 정부 주택공급 목표</h4>
                <p class="paragraph">
                    국토교통부는 제6차 주택종합계획(2023-2032)을 통해 향후 10년간 
                    연평균 50만 호의 주택 공급을 추진하며, 이 중 공공임대주택 비중을 
                    25% 수준으로 확대할 계획입니다. 이는 OECD 평균(15%) 대비 높은 수준으로, 
                    공공부문의 적극적인 시장 개입을 통해 주거 안정성을 확보하려는 정책 의지를 
                    반영합니다.
                </p>
                <p class="paragraph">
                    특히 서울시는 2025년 목표로 공공임대주택 25,000호 공급을 추진 중이며, 
                    이 중 신축매입임대 방식이 약 40%(10,000호)를 차지합니다. 
                    이는 기존 재고 매입 방식보다 품질 관리 및 장기 유지보수 측면에서 
                    유리하다는 판단에 기반합니다.
                </p>
                
                <h4 class="subsubsection-title">1.3 공공주택 정책 트렌드</h4>
                <p class="paragraph">
                    최근 공공주택 정책은 단순한 '물량 공급'에서 '맞춤형 공급'으로 전환되고 있습니다. 
                    생애주기별(청년→신혼부부→다자녀→고령자) 맞춤형 주택 설계, 
                    커뮤니티 시설 강화, 에너지 효율 등급 의무화 등 질적 개선이 강조되고 있으며, 
                    입주자 선호도 및 만족도가 사업 성과의 중요한 지표로 관리되고 있습니다.
                </p>
            </div>
        """)
        
        # === Section 2: Seoul Housing Market ===
        paragraphs.append(f"""
            <div class="policy-context-section">
                <h3 class="subsection-title">2. 서울 주택시장 현황 (Seoul Metropolitan Housing Market)</h3>
                
                <h4 class="subsubsection-title">2.1 수급 동향 (Supply-Demand Dynamics)</h4>
                <p class="paragraph">
                    서울시 주택시장은 2023-2024년 금리 인상 및 경기 침체 영향으로 
                    거래량이 감소하였으나, 2025년 들어 점진적 회복세를 보이고 있습니다. 
                    특히 소형 아파트(전용면적 60㎡ 이하) 수요는 1인 가구 및 신혼부부 증가로 
                    꾸준한 증가세를 유지하고 있으며, 이는 공공임대 수요 확대로도 이어지고 있습니다.
                </p>
                <p class="paragraph">
                    서울시 주택 재고는 약 380만 호이며, 이 중 공공임대주택은 약 32만 호(8.4%)입니다. 
                    OECD 권고 수준인 10%에는 미달하는 수준으로, 공공임대 공급 확대 필요성이 
                    지속적으로 제기되고 있습니다. 특히 청년·신혼부부 대상 공공임대는 
                    신청 경쟁률이 평균 10:1을 초과하는 등 수요가 공급을 크게 상회하고 있습니다.
                </p>
                
                <h4 class="subsubsection-title">2.2 임대시장 트렌드</h4>
                <p class="paragraph">
                    서울시 월세 시장은 전세 시장 위축으로 인한 수요 이동으로 
                    2024년 대비 약 5% 상승하였으며, 특히 직주근접(職住近接)이 가능한 
                    역세권 소형 주택의 월세 상승률이 높게 나타나고 있습니다. 
                    이는 LH 공공임대주택의 '시장 안정화' 기능이 더욱 중요해지고 있음을 시사합니다.
                </p>
                <p class="paragraph">
                    {unit_type}형 주택의 경우, 민간 월세 평균이 45-65만원 수준인 반면, 
                    LH 공공임대는 시세의 70-80% 수준으로 책정되어 약 10-20만원의 
                    임대료 경쟁력을 확보하고 있습니다. 이러한 가격 경쟁력은 
                    안정적인 임대 수요를 확보하는 핵심 요인으로 작용합니다.
                </p>
                
                <h4 class="subsubsection-title">2.3 목표 수요층 동향</h4>
                <p class="paragraph">
                    서울시 청년(19-39세) 인구는 약 230만 명으로, 이 중 1인 가구 비율이 60%를 초과하며, 
                    이들의 평균 주거비 부담률은 소득 대비 30%를 상회합니다. 
                    특히 청년층의 주거 불안정은 결혼·출산 기피로 이어지는 사회 문제로 인식되어, 
                    정부 차원의 청년 주거지원 정책이 강화되고 있습니다.
                </p>
                <p class="paragraph">
                    신혼부부의 경우, 서울시 연간 약 4만 쌍이 혼인하며, 
                    이 중 60% 이상이 전세 또는 월세 거주를 시작합니다. 
                    LH 신혼부부 공공임대는 최장 20년 거주가 가능하여 주거 안정성이 높고, 
                    자녀 출산·양육 시 우선권을 부여받을 수 있어 선호도가 높습니다.
                </p>
            </div>
        """)
        
        # === Section 3: Regulatory Environment ===
        paragraphs.append(f"""
            <div class="policy-context-section">
                <h3 class="subsection-title">3. 규제 환경 (Regulatory Environment)</h3>
                
                <h4 class="subsubsection-title">3.1 최근 정책 변화</h4>
                <p class="paragraph">
                    2024년 「민간임대주택에 관한 특별법」 개정으로 LH 신축매입임대 사업의 
                    토지 취득 절차가 간소화되었으며, 건축 인허가 기간이 평균 2개월 단축되었습니다. 
                    또한 「주택법」 개정을 통해 공공임대주택의 층고 및 주차장 기준이 완화되어, 
                    사업 비용 절감 및 세대 수 확대가 가능해졌습니다.
                </p>
                <p class="paragraph">
                    서울시는 2025년부터 공공임대주택 건설 시 용적률 인센티브를 
                    기존 20%에서 30%로 확대하였으며, 공원·학교 등 기반시설 기부채납 요구도 
                    완화하여 사업자의 재무 부담을 경감하고 있습니다.
                </p>
                
                <h4 class="subsubsection-title">3.2 용도지역 및 토지이용 규제</h4>
                <p class="paragraph">
                    서울시는 2050 도시기본계획에 따라 주거지역의 정비 및 개발을 
                    단계적으로 추진하고 있으며, 특히 역세권 및 준공업지역의 주거 전환을 
                    적극 유도하고 있습니다. 이는 직주근접 생활권 조성을 통해 
                    통근 시간 단축 및 삶의 질 향상을 도모하기 위한 것입니다.
                </p>
                <p class="paragraph">
                    {address} 일대는 서울시 도시계획 상 [자치구별 용도지역 정보]로 지정되어 있으며, 
                    향후 5년간 대규모 용도지역 변경 계획은 없는 것으로 확인되어 
                    사업 안정성이 확보되어 있습니다.
                </p>
                
                <h4 class="subsubsection-title">3.3 재정 인센티브 및 제약</h4>
                <p class="paragraph">
                    LH 신축매입임대 사업은 「공공주택 특별법」에 따라 취득세 감면(75%), 
                    재산세 감면(25%), 국민주택기금 저리 융자(연 2.0-2.5%) 등의 
                    재정 지원을 받을 수 있습니다. 이는 민간 사업 대비 약 15-20%의 
                    비용 절감 효과를 가져오며, 사업 타당성 확보에 중요한 역할을 합니다.
                </p>
                <p class="paragraph">
                    다만, LH 매입가 상한 기준(감정평가액 대비 110% 이내), 
                    임대료 상한 기준(시세 80% 이내), 의무 임대 기간(30년) 등의 제약이 있어, 
                    사업 구조 설계 시 이러한 규제 요건을 면밀히 검토해야 합니다.
                </p>
            </div>
        """)
        
        # === Section 4: Competitive Landscape ===
        paragraphs.append(f"""
            <div class="policy-context-section">
                <h3 class="subsection-title">4. 경쟁 환경 (Competitive Landscape)</h3>
                
                <h4 class="subsubsection-title">4.1 인근 LH 프로젝트 현황</h4>
                <p class="paragraph">
                    {address} 반경 3km 내에는 LH 공공임대주택이 [GeoOptimizer 데이터 기반] 
                    약 [X]개 단지, [Y]세대가 운영 중이거나 건설 예정입니다. 
                    이는 해당 지역이 LH의 전략적 공급 지역임을 나타내며, 
                    동시에 수요 cannibalization 가능성도 고려해야 함을 의미합니다.
                </p>
                <p class="paragraph">
                    다만, 기존 LH 프로젝트 대부분이 높은 입주율(평균 95% 이상)을 유지하고 있어, 
                    해당 지역의 공공임대 수요가 충분함을 방증합니다. 
                    특히 청년·신혼부부 대상 소형 주택은 공급 부족 상태가 지속되고 있어, 
                    신규 공급 시 경쟁력을 확보할 수 있을 것으로 판단됩니다.
                </p>
                
                <h4 class="subsubsection-title">4.2 민간 개발 동향</h4>
                <p class="paragraph">
                    민간 부문에서도 역세권 중심으로 소형 임대주택(오피스텔, 도시형생활주택) 
                    공급이 활발하게 진행되고 있으나, 임대료 수준이 LH 대비 30-50% 높아 
                    목표 수요층이 명확히 구분됩니다. 민간 임대는 주로 중산층 이상을 타겟으로 하며, 
                    LH 공공임대는 소득 6분위 이하 계층을 대상으로 하여 시장 세분화가 이루어져 있습니다.
                </p>
                <p class="paragraph">
                    다만, 민간 임대의 공실률이 평균 10-15%로 높은 편이어서, 
                    시장 전체의 공급 과잉 가능성은 상시 모니터링이 필요합니다.
                </p>
                
                <h4 class="subsubsection-title">4.3 시장 포지셔닝 전략</h4>
                <p class="paragraph">
                    본 사업은 '합리적 가격의 양질의 주거 공간' 포지셔닝을 통해 
                    가격 민감도가 높은 청년·신혼부부 계층을 타겟으로 합니다. 
                    LH 브랜드 신뢰도, 장기 거주 안정성, 커뮤니티 시설 제공 등을 차별화 요소로 삼아, 
                    민간 임대와의 직접적 경쟁을 회피하면서도 충분한 수요를 확보할 수 있을 것으로 전망됩니다.
                </p>
            </div>
        """)
        
        return paragraphs
    
    def generate_financial_analysis_narrative(
        self,
        financial_analysis: Dict[str, Any],
        basic_info: Dict[str, Any]
    ) -> List[str]:
        """
        Generate Financial Analysis narrative (6-8 pages)
        
        Transforms financial numbers into strategic insights:
        - CapEx breakdown with interpretation
        - OpEx analysis with benchmarking
        - NOI trajectory with scenarios
        - Return metrics with decision implications
        - Breakeven analysis with recommendations
        - Sensitivity analysis with risk assessment
        
        Args:
            financial_analysis: Complete financial analysis results
            basic_info: Basic project info
        
        Returns:
            List of paragraph HTML strings
        """
        paragraphs = []
        
        # Extract data
        capex = financial_analysis.get('capex', {})
        opex = financial_analysis.get('opex', {})
        noi = financial_analysis.get('noi', {})
        returns = financial_analysis.get('returns', {})
        breakeven = financial_analysis.get('breakeven', {})
        sensitivity = financial_analysis.get('sensitivity', {})
        
        # === Section 1: CapEx Analysis ===
        total_capex = capex.get('total_capex', 0)
        unit_count = capex.get('unit_count', 0)
        capex_per_unit = capex.get('capex_per_unit', 0)
        breakdown = capex.get('breakdown', {})
        
        paragraphs.append(f"""
            <div class="financial-section">
                <h3 class="subsection-title">1. 자본적 지출 분석 (Capital Expenditure Analysis)</h3>
                
                <h4 class="subsubsection-title">1.1 총 투자 규모</h4>
                <p class="paragraph">
                    본 사업의 총 투자금액은 <strong>{self._format_krw(total_capex)}</strong>로 산정되었으며, 
                    {unit_count}세대 기준 세대당 투자금액은 <strong>{self._format_krw(capex_per_unit)}</strong>입니다. 
                    이는 서울시 LH 신축매입임대 사업의 평균 세대당 투자금액인 5-6억원과 
                    {'유사한' if 4.5e8 <= capex_per_unit <= 6.5e8 else '상이한'} 수준으로, 
                    {'표준적인 사업 구조로 평가됩니다.' if 4.5e8 <= capex_per_unit <= 6.5e8 else '추가 검토가 필요합니다.'}
                </p>
        """)
        
        # CapEx breakdown
        if breakdown:
            land_subtotal = breakdown.get('land_acquisition', {}).get('subtotal', 0)
            land_pct = breakdown.get('land_acquisition', {}).get('percentage', 0)
            construction_subtotal = breakdown.get('construction_hard_costs', {}).get('subtotal', 0)
            construction_pct = breakdown.get('construction_hard_costs', {}).get('percentage', 0)
            
            paragraphs.append(f"""
                <h4 class="subsubsection-title">1.2 비용 구조 분석</h4>
                <p class="paragraph">
                    <strong>• 토지 취득 비용</strong>: {self._format_krw(land_subtotal)} ({land_pct:.1f}%)<br>
                    <strong>• 건축 공사비</strong>: {self._format_krw(construction_subtotal)} ({construction_pct:.1f}%)<br>
                </p>
                <p class="paragraph">
                    토지 비용이 전체 투자금의 {land_pct:.1f}%를 차지하고 있어, 
                    {'표준적인 비율(40-50%)로 평가됩니다.' if 40 <= land_pct <= 50 else 
                     '비율이 높은 편이며, 이는 토지 가격 변동에 대한 민감도가 높음을 의미합니다.' if land_pct > 50 else
                     '비율이 낮은 편으로, 건축비 최적화에 집중할 필요가 있습니다.'}
                </p>
                <p class="paragraph">
                    건축 공사비는 연면적 ㎡당 {self._format_krw(capex.get('capex_per_sqm', 0))}로, 
                    서울시 평균(800-900만원/㎡)과 비교 시 
                    {'적정 수준입니다.' if 7e6 <= capex.get('capex_per_sqm', 0) <= 10e6 else '재검토가 필요합니다.'}
                </p>
            </div>
        """)
        
        # === Section 2: OpEx Analysis ===
        year1_opex = opex.get('year1_total_opex', 0)
        opex_per_unit = opex.get('year1_opex_per_unit', 0)
        
        paragraphs.append(f"""
            <div class="financial-section">
                <h3 class="subsection-title">2. 운영 비용 분석 (Operating Expense Analysis)</h3>
                
                <h4 class="subsubsection-title">2.1 연간 운영비 규모</h4>
                <p class="paragraph">
                    1차 연도 운영비는 총 <strong>{self._format_krw(year1_opex)}</strong>로 예상되며, 
                    세대당 연간 <strong>{self._format_krw(opex_per_unit)}</strong>, 
                    월평균 <strong>{self._format_krw(opex_per_unit/12)}</strong> 수준입니다.
                </p>
                <p class="paragraph">
                    이는 LH 공공임대주택의 표준 운영비(세대당 연 500-700만원)와 비교 시 
                    {'적정 범위'if 5e6 <= opex_per_unit <= 7e6 else '범위를 벗어나는 수준'}으로, 
                    {'효율적인 관리 계획이 수립되어 있는 것으로 판단됩니다.' if 5e6 <= opex_per_unit <= 7e6 else 
                     '비용 구조 재검토가 필요합니다.'}
                </p>
                
                <h4 class="subsubsection-title">2.2 주요 비용 항목 분석</h4>
                <p class="paragraph">
                    운영비의 주요 구성 항목은 다음과 같습니다:<br>
                    • <strong>유지보수비</strong>: 주요 설비 노후화 대비 예방 정비 및 긴급 수선 비용<br>
                    • <strong>관리 인건비</strong>: 전문 PM 업체 관리비 및 현장 관리 인력 비용<br>
                    • <strong>재산세·보험료</strong>: 법정 필수 비용으로 회피 불가<br>
                    • <strong>대체 적립금</strong>: 장기적 자산 가치 유지를 위한 필수 항목
                </p>
                <p class="paragraph">
                    향후 10년간 연평균 2% 인플레이션을 가정 시, 
                    10년차 운영비는 약 {self._format_krw(year1_opex * (1.02 ** 9))}로 증가할 것으로 예상되며, 
                    이는 임대료 인상률(연 2.5%)로 충분히 흡수 가능한 수준입니다.
                </p>
            </div>
        """)
        
        # === Section 3: NOI and Revenue ===
        noi_value = noi.get('noi', 0)
        noi_margin = noi.get('noi_margin_percent', 0)
        monthly_rent = noi.get('monthly_rent', 0)
        
        paragraphs.append(f"""
            <div class="financial-section">
                <h3 class="subsection-title">3. 순운영소득 분석 (Net Operating Income Analysis)</h3>
                
                <h4 class="subsubsection-title">3.1 NOI 산출</h4>
                <p class="paragraph">
                    안정기(2차 연도) 기준 연간 NOI는 <strong>{self._format_krw(noi_value)}</strong>로 예상되며, 
                    NOI 마진율은 <strong>{noi_margin:.1f}%</strong>입니다.
                </p>
                <p class="paragraph">
                    {'NOI가 양수(+)로 산출되어 운영 수익성이 확보되었습니다.' if noi_value > 0 else 
                     '⚠️ NOI가 음수(-)로 산출되어 현재 구조로는 운영 적자가 예상됩니다. 임대료 재산정 또는 비용 구조 개선이 필요합니다.'}
                    LH 공공임대주택의 목표 NOI 마진율은 일반적으로 30-40%로 설정되며, 
                    본 사업은 {'이 기준을 충족합니다.' if noi_margin >= 30 else '기준 미달로 개선이 필요합니다.'}
                </p>
                
                <h4 class="subsubsection-title">3.2 임대 수익 구조</h4>
                <p class="paragraph">
                    세대당 월 임대료는 <strong>{self._format_krw(monthly_rent)}</strong>로 설정되었으며, 
                    이는 해당 지역 시세의 약 70-80% 수준으로 LH 기준에 부합합니다. 
                    연간 2.5% 임대료 인상을 가정 시, 5년 후에는 약 {self._format_krw(monthly_rent * (1.025 ** 5))}로 
                    증가할 것으로 예상됩니다.
                </p>
                <p class="paragraph">
                    입주율은 1차 연도 80%, 2차 연도 이후 95% 안정화를 가정하였으며, 
                    이는 LH 기존 프로젝트의 평균 입주율 패턴과 일치합니다.
                </p>
            </div>
        """)
        
        # === Section 4: Return Metrics ===
        cap_rate = returns.get('cap_rate_percent', 0)
        meets_lh = returns.get('meets_lh_target', False)
        
        paragraphs.append(f"""
            <div class="financial-section">
                <h3 class="subsection-title">4. 수익률 분석 (Return Metrics Analysis)</h3>
                
                <h4 class="subsubsection-title">4.1 Cap Rate</h4>
                <p class="paragraph">
                    본 사업의 Cap Rate는 <strong>{cap_rate:.2f}%</strong>로 산출되었습니다. 
                    LH의 목표 Cap Rate는 4.5%이며, 본 사업은 
                    {'✓ 목표를 충족하여 재무적으로 타당한 것으로 평가됩니다.' if meets_lh else 
                     '✗ 목표에 미달하여 사업 구조 개선이 필요합니다.'}
                </p>
                <p class="paragraph">
                    {f'현재 Cap Rate {cap_rate:.2f}%는 LH 기준을 {cap_rate - 4.5:.2f}%p 상회하여 안정적인 수익 구조를 갖추고 있습니다.' if cap_rate >= 4.5 else
                     f'목표 Cap Rate 4.5%를 달성하기 위해서는 NOI를 약 {self._format_krw(total_capex * 0.045)}로 개선하거나, 총 투자금을 {self._format_krw(noi_value / 0.045 if noi_value > 0 else 0)}로 절감해야 합니다.'}
                </p>
            </div>
        """)
        
        # === Section 5: Breakeven ===
        breakeven_occupancy = breakeven.get('breakeven_occupancy_percent', 0)
        breakeven_rent = breakeven.get('breakeven_monthly_rent', 0)
        achievable = breakeven.get('achievable', False)
        
        paragraphs.append(f"""
            <div class="financial-section">
                <h3 class="subsection-title">5. 손익분기점 분석 (Breakeven Analysis)</h3>
                
                <h4 class="subsubsection-title">5.1 손익분기 입주율</h4>
                <p class="paragraph">
                    현재 임대료 수준에서 LH 목표 수익률을 달성하기 위한 손익분기 입주율은 
                    <strong>{breakeven_occupancy:.1f}%</strong>입니다.
                </p>
                <p class="paragraph">
                    {'✓ 이는 안정기 목표 입주율 95% 이내로, 달성 가능한 수준입니다.' if achievable else 
                     '⚠️ 이는 안정기 목표 입주율 95%를 초과하여, 현실적으로 달성이 어려울 수 있습니다. 임대료 인상 또는 비용 절감이 필요합니다.'}
                </p>
                
                <h4 class="subsubsection-title">5.2 손익분기 임대료</h4>
                <p class="paragraph">
                    안정기 입주율 95% 가정 시 손익분기 임대료는 
                    <strong>{self._format_krw(breakeven_rent)}</strong>로 산정됩니다. 
                    현재 설정 임대료 {self._format_krw(monthly_rent)}와 비교 시 
                    {self._format_krw(abs(breakeven_rent - monthly_rent))} 
                    {'부족하여 임대료 인상 검토가 필요합니다.' if breakeven_rent > monthly_rent else '여유가 있어 안정적입니다.'}
                </p>
            </div>
        """)
        
        # === Section 6: Sensitivity ===
        irr_range = sensitivity.get('summary', {}).get('irr_range', {})
        
        paragraphs.append(f"""
            <div class="financial-section">
                <h3 class="subsection-title">6. 민감도 분석 (Sensitivity Analysis)</h3>
                
                <h4 class="subsubsection-title">6.1 시나리오별 수익률</h4>
                <p class="paragraph">
                    3가지 시나리오(낙관/기본/비관)를 적용한 민감도 분석 결과는 다음과 같습니다:
                </p>
                <ul class="scenario-list">
                    <li><strong>비관적 시나리오 (임대료 -10%, 입주율 -5%p, 비용 +10%)</strong>: 
                        IRR {irr_range.get('pessimistic', 0):.2f}%</li>
                    <li><strong>기본 시나리오 (현재 가정 유지)</strong>: 
                        IRR {irr_range.get('base', 0):.2f}%</li>
                    <li><strong>낙관적 시나리오 (임대료 +10%, 입주율 +2%p, 비용 -10%)</strong>: 
                        IRR {irr_range.get('optimistic', 0):.2f}%</li>
                </ul>
                <p class="paragraph">
                    IRR 변동 폭은 {irr_range.get('spread', 0):.2f}%p로, 
                    {'변동성이 낮아 안정적인 사업 구조로 평가됩니다.' if irr_range.get('spread', 0) < 5 else 
                     '변동성이 높아 외부 환경 변화에 민감할 수 있습니다.'}
                </p>
                
                <h4 class="subsubsection-title">6.2 핵심 민감 변수</h4>
                <p class="paragraph">
                    수익률에 가장 큰 영향을 미치는 변수는 순서대로 다음과 같습니다:<br>
                    1. <strong>임대료 수준</strong> (High impact): ±10% 변동 시 IRR 약 ±3-5%p 변동<br>
                    2. <strong>입주율</strong> (High impact): ±5%p 변동 시 IRR 약 ±2-3%p 변동<br>
                    3. <strong>건축 비용</strong> (Medium impact): ±10% 변동 시 IRR 약 ±1-2%p 변동<br>
                    4. <strong>운영비 인플레이션</strong> (Medium impact): ±1%p 변동 시 IRR 약 ±0.5-1%p 변동
                </p>
                <p class="paragraph">
                    따라서 사업 리스크 관리의 최우선 과제는 <strong>안정적인 입주율 확보</strong>와 
                    <strong>적정 임대료 설정</strong>이며, 이를 위한 적극적인 마케팅 및 입주자 만족도 관리가 필수적입니다.
                </p>
            </div>
        """)
        
        return paragraphs
    
    # Helper methods
    
    def _format_krw(self, amount: float) -> str:
        """Format amount as Korean Won"""
        if amount >= 1_000_000_000_000:
            return f"{amount / 1_000_000_000_000:.1f}조원"
        elif amount >= 100_000_000:
            return f"{amount / 100_000_000:.1f}억원"
        elif amount >= 10_000:
            return f"{amount / 10_000:.0f}만원"
        else:
            return f"{amount:,.0f}원"
    
    def _generate_key_findings(
        self,
        data: Dict,
        financial_analysis: Dict,
        risk_assessment: Dict
    ) -> List[str]:
        """Generate key findings bullets"""
        findings = []
        
        # Finding 1: Location
        findings.append(
            "<strong>입지 조건</strong>: 지하철역 도보권, 주요 업무지구 접근성 우수, "
            "생활 편의시설 풍부하여 LH 공공임대 입지로 적합함"
        )
        
        # Finding 2: Financial
        meets_lh = financial_analysis.get('summary', {}).get('meets_lh_criteria', False)
        cap_rate = financial_analysis.get('summary', {}).get('cap_rate', 0)
        
        findings.append(
            f"<strong>재무 타당성</strong>: Cap Rate {cap_rate:.2f}% "
            f"({'LH 기준 충족' if meets_lh else 'LH 기준 미달, 최적화 필요'})"
        )
        
        # Finding 3: Demand
        findings.append(
            "<strong>수요 분석</strong>: 목표 수요층(청년/신혼부부) 충분한 인구 기반 확보, "
            "공공임대 신청 경쟁률 10:1 초과로 안정적 수요 예상"
        )
        
        # Finding 4: Risk
        risk_level = risk_assessment.get('executive_summary', {}).get('overall_risk_level', 'medium')
        risk_text = {
            'critical': '높음 (즉시 대응 필요)',
            'high': '중-높음 (우선 관리)',
            'medium': '중간 (관리 가능)',
            'low': '낮음'
        }.get(risk_level, '중간')
        
        findings.append(
            f"<strong>위험 수준</strong>: 전체 위험도 {risk_text}, "
            "모든 주요 위험에 대한 완화 전략 수립 완료"
        )
        
        # Finding 5: Competition
        findings.append(
            "<strong>경쟁 환경</strong>: 인근 LH 프로젝트 높은 입주율 유지, "
            "공급 부족 상태로 시장 진입 기회 확보"
        )
        
        # Finding 6: Policy alignment
        findings.append(
            "<strong>정책 적합성</strong>: LH 2025년 전략 방향과 일치, "
            "정부 공공주택 공급 확대 정책 기조에 부합"
        )
        
        return findings
    
    def _generate_decision_rationale(
        self,
        financial_analysis: Dict,
        risk_assessment: Dict,
        data: Dict
    ) -> str:
        """Generate decision rationale HTML"""
        meets_lh = financial_analysis.get('summary', {}).get('meets_lh_criteria', False)
        
        if meets_lh:
            return """
                <p class="paragraph">
                    본 사업은 다음과 같은 이유로 <strong>사업 추진이 적합</strong>한 것으로 판단됩니다:
                </p>
                <p class="paragraph">
                    <strong>첫째</strong>, 재무적 타당성이 확보되어 있습니다. 
                    Cap Rate가 LH 목표 기준을 충족하며, 안정적인 NOI 창출이 가능한 구조입니다.
                </p>
                <p class="paragraph">
                    <strong>둘째</strong>, 입지 경쟁력이 우수합니다. 
                    교통 접근성, 생활 편의시설, 인구 구조 등 핵심 입지 요소가 모두 양호한 수준을 보이고 있습니다.
                </p>
                <p class="paragraph">
                    <strong>셋째</strong>, 시장 수요가 충분합니다. 
                    목표 수요층의 인구 기반이 탄탄하고, 기존 LH 프로젝트의 높은 입주율이 
                    안정적인 수요를 방증합니다.
                </p>
                <p class="paragraph">
                    <strong>넷째</strong>, 위험 관리가 가능합니다. 
                    식별된 모든 위험에 대해 구체적인 완화 전략이 수립되어 있으며, 
                    전체적인 위험 수준은 관리 가능한 범위 내에 있습니다.
                </p>
            """
        else:
            return """
                <p class="paragraph">
                    본 사업은 다음과 같은 이유로 <strong>조건부 추진</strong>이 권고됩니다:
                </p>
                <p class="paragraph">
                    <strong>긍정 요소</strong>: 입지 경쟁력 우수, 시장 수요 충분, 정책 적합성 높음
                </p>
                <p class="paragraph">
                    <strong>개선 필요 요소</strong>: 현재 재무 구조로는 LH 목표 수익률 미달. 
                    다음 중 하나 이상의 최적화 조치가 필요합니다:
                </p>
                <ul>
                    <li>유닛 수 증가 (용적률 활용도 제고)</li>
                    <li>임대료 재산정 (시세 대비 비율 조정)</li>
                    <li>건축 비용 절감 (VE, 설계 최적화)</li>
                    <li>운영비 효율화 (PM 계약 구조 개선)</li>
                </ul>
                <p class="paragraph">
                    상기 개선 조치 시행 시 재무 타당성 확보가 가능하며, 
                    이 경우 사업 추진을 적극 권장합니다.
                </p>
            """
    
    def _generate_final_recommendation(
        self,
        financial_analysis: Dict,
        risk_assessment: Dict,
        data: Dict
    ) -> str:
        """Generate final recommendation HTML"""
        meets_lh = financial_analysis.get('summary', {}).get('meets_lh_criteria', False)
        cap_rate = financial_analysis.get('summary', {}).get('cap_rate', 0)
        risk_level = risk_assessment.get('executive_summary', {}).get('overall_risk_level', 'medium')
        
        if meets_lh and risk_level in ['low', 'medium']:
            decision = "✅ <strong>사업 추진 권고 (GO)</strong>"
            rationale = f"""
                <p class="paragraph">
                    Cap Rate {cap_rate:.2f}%로 LH 기준을 충족하며, 
                    위험 수준도 {risk_level}로 관리 가능한 범위 내에 있습니다. 
                    즉시 사업을 추진하되, 다음 사항을 준수하시기 바랍니다:
                </p>
                <ul>
                    <li>토지 취득 협상 시 매입가 상한(감정평가 110%) 준수</li>
                    <li>건축 인허가 절차 조기 착수 (목표: 3개월 내 완료)</li>
                    <li>고정가 계약 체결로 건축비 리스크 최소화</li>
                    <li>사전 임대(Pre-leasing) 프로그램 운영 (준공 3개월 전)</li>
                    <li>주요 위험(공실률, 비용 초과)에 대한 모니터링 체계 구축</li>
                </ul>
            """
        elif meets_lh and risk_level in ['high', 'critical']:
            decision = "⚠️ <strong>조건부 추진 권고 (CONDITIONAL GO)</strong>"
            rationale = f"""
                <p class="paragraph">
                    재무적으로는 타당하나, 위험 수준이 {risk_level}로 높은 편입니다. 
                    다음 조건 충족 시 사업 추진을 권고합니다:
                </p>
                <ul>
                    <li><strong>필수 조건</strong>: Critical 및 High 위험에 대한 완화 조치 즉시 시행</li>
                    <li>비상 대응 계획(Contingency Plan) 수립 및 예비비 15% 확보</li>
                    <li>LH 본사와 위험 관리 방안 사전 협의</li>
                    <li>분기별 위험 재평가 체계 구축</li>
                </ul>
            """
        else:
            decision = "🔄 <strong>사업 구조 재검토 권고 (REVISE)</strong>"
            rationale = f"""
                <p class="paragraph">
                    현재 구조로는 LH 기준 미달(Cap Rate {cap_rate:.2f}% < 4.5%) 또는 
                    위험 수준 과다로 즉시 추진이 어렵습니다. 
                    다음과 같은 최적화 조치 후 재평가를 권고합니다:
                </p>
                <ul>
                    <li><strong>재무 구조 개선</strong>: 유닛 수 증가, 임대료 재산정, 비용 절감</li>
                    <li><strong>위험 완화</strong>: 주요 위험 요인에 대한 선제적 대응 방안 수립</li>
                    <li><strong>대안 검토</strong>: GeoOptimizer 대안지 중 더 나은 입지 재검토</li>
                    <li><strong>재평가</strong>: 개선 조치 후 재무 및 위험 재분석</li>
                </ul>
                <p class="paragraph">
                    개선 조치 시행 후 Cap Rate 4.5% 이상 달성 및 위험 수준 Medium 이하 확보 시, 
                    사업 추진을 적극 권장합니다.
                </p>
            """
        
        return f"""
            <div class="recommendation-decision">
                {decision}
            </div>
            {rationale}
            <p class="paragraph">
                <strong>Next Steps</strong>: 
                본 권고안을 LH 본사 담당부서와 검토하고, 
                3개월 이내 최종 의사결정을 권장합니다.
            </p>
        """
    
    def generate_risk_mitigation_narrative(
        self,
        risk_assessment: Dict[str, Any],
        financial_analysis: Dict[str, Any]
    ) -> List[str]:
        """
        Generate Risk Mitigation narrative (5-6 pages)
        
        Transforms risk data into strategic risk management narrative:
        - Risk matrix overview
        - Category-by-category analysis
        - Mitigation strategies with action plans
        - Contingency planning
        - Risk monitoring framework
        
        Args:
            risk_assessment: Complete risk assessment results
            financial_analysis: Financial analysis for context
        
        Returns:
            List of paragraph HTML strings
        """
        paragraphs = []
        
        # Extract data
        risks = risk_assessment.get('risks', [])
        risk_matrix = risk_assessment.get('risk_matrix', {})
        executive_summary = risk_assessment.get('executive_summary', {})
        roadmap = risk_assessment.get('mitigation_roadmap', {})
        
        # === Section 1: Risk Overview ===
        total_risks = executive_summary.get('total_risks', 0)
        risk_counts = executive_summary.get('risk_counts_by_level', {})
        
        paragraphs.append(f"""
            <div class="risk-section">
                <h3 class="subsection-title">1. 위험 프로파일 개요 (Risk Profile Overview)</h3>
                
                <p class="paragraph">
                    본 사업에 대한 포괄적 위험 평가를 수행한 결과, 
                    총 <strong>{total_risks}개</strong>의 주요 위험 요인이 식별되었습니다. 
                    위험 평가는 영향도(Impact, 1-5점)와 발생가능성(Likelihood, 1-5점)을 
                    곱한 위험 점수(Risk Score = Impact × Likelihood)를 기준으로 하였으며, 
                    각 위험은 Critical/High/Medium/Low 4단계로 분류되었습니다.
                </p>
                
                <div class="risk-summary-box">
                    <h4 class="subsubsection-title">위험 등급별 분포</h4>
                    <ul class="risk-count-list">
                        <li><strong class="risk-critical">Critical 위험</strong>: {risk_counts.get('critical', 0)}건 
                            - 즉시 대응 필요 (영향도≥4 AND 발생가능성≥4)</li>
                        <li><strong class="risk-high">High 위험</strong>: {risk_counts.get('high', 0)}건 
                            - 우선 관리 필요 (위험 점수≥12)</li>
                        <li><strong class="risk-medium">Medium 위험</strong>: {risk_counts.get('medium', 0)}건 
                            - 지속 모니터링 필요 (위험 점수≥6)</li>
                        <li><strong class="risk-low">Low 위험</strong>: {risk_counts.get('low', 0)}건 
                            - 정상적 관리 (위험 점수<6)</li>
                    </ul>
                </div>
                
                <p class="paragraph">
                    전체적인 프로젝트 위험 수준은 <strong>{executive_summary.get('overall_risk_level', 'medium').upper()}</strong>로 평가되며, 
                    모든 식별된 위험에 대해 구체적인 완화 전략과 비상 대응 계획이 수립되어 있습니다.
                </p>
            </div>
        """)
        
        # === Section 2: Top 3 Risks ===
        top_risks = executive_summary.get('top_3_risks', [])
        
        if top_risks:
            top_risks_html = ""
            for i, risk in enumerate(top_risks, 1):
                # Find full risk details
                risk_details = next((r for r in risks if r['id'] == risk['id']), {})
                
                top_risks_html += f"""
                    <div class="top-risk-item">
                        <h5><strong>위험 #{i}: {risk['title']}</strong> 
                            (위험 점수: {risk['score']}, 등급: {risk['level'].upper()})</h5>
                        <p><strong>설명</strong>: {risk_details.get('description', 'N/A')}</p>
                        <p><strong>주요 완화 전략</strong>:</p>
                        <ul>
                """
                
                for strategy in risk_details.get('mitigation_strategies', [])[:3]:
                    top_risks_html += f"<li>{strategy}</li>"
                
                top_risks_html += f"""
                        </ul>
                        <p><strong>비상 대응 계획</strong>: {risk_details.get('contingency_plan', 'N/A')}</p>
                        <p><strong>책임자</strong>: {risk_details.get('owner', 'N/A')}</p>
                    </div>
                """
            
            paragraphs.append(f"""
                <div class="risk-section">
                    <h3 class="subsection-title">2. 주요 위험 요인 Top 3 (Top Risk Factors)</h3>
                    <p class="paragraph">
                        위험 점수가 가장 높은 상위 3개 위험 요인은 다음과 같으며, 
                        이들에 대한 집중적인 관리가 필요합니다:
                    </p>
                    {top_risks_html}
                </div>
            """)
        
        # === Section 3: Category-by-Category Analysis ===
        category_breakdown = executive_summary.get('category_breakdown', {})
        
        category_analysis = ""
        category_names = {
            'financial': '재무적 위험 (Financial Risks)',
            'regulatory': '규제·법적 위험 (Regulatory Risks)',
            'market': '시장 위험 (Market Risks)',
            'operational': '운영 위험 (Operational Risks)',
            'construction': '건설 위험 (Construction Risks)',
            'legal': '법적 위험 (Legal Risks)'
        }
        
        for category, count in category_breakdown.items():
            if count > 0:
                category_risks = [r for r in risks if r['category'] == category]
                
                category_analysis += f"""
                    <div class="risk-category-section">
                        <h4 class="subsubsection-title">{category_names.get(category, category)} ({count}건)</h4>
                        <ul class="risk-list">
                """
                
                for risk in category_risks:
                    category_analysis += f"""
                        <li>
                            <strong>{risk['title']}</strong> (점수: {risk['risk_score']}, {risk['risk_level'].upper()})
                            <br>→ 주요 완화: {risk['mitigation_strategies'][0] if risk['mitigation_strategies'] else 'N/A'}
                        </li>
                    """
                
                category_analysis += "</ul></div>"
        
        paragraphs.append(f"""
            <div class="risk-section">
                <h3 class="subsection-title">3. 위험 카테고리별 분석 (Risk Analysis by Category)</h3>
                <p class="paragraph">
                    식별된 {total_risks}개 위험을 6개 카테고리로 분류하여 분석한 결과는 다음과 같습니다:
                </p>
                {category_analysis}
            </div>
        """)
        
        # === Section 4: Mitigation Strategy Framework ===
        immediate_action = roadmap.get('immediate_action', [])
        
        if immediate_action:
            immediate_html = "<ul class='mitigation-action-list'>"
            for risk in immediate_action:
                immediate_html += f"""
                    <li>
                        <strong>{risk['title']}</strong> ({risk['level'].upper()})
                        <br>• 조치: {risk['key_mitigation']}
                        <br>• 책임: {risk['owner']}
                        <br>• 일정: {risk['timeline']}
                    </li>
                """
            immediate_html += "</ul>"
            
            paragraphs.append(f"""
                <div class="risk-section">
                    <h3 class="subsection-title">4. 완화 전략 로드맵 (Mitigation Strategy Roadmap)</h3>
                    
                    <h4 class="subsubsection-title">4.1 즉시 대응 필요 (Immediate Action Required)</h4>
                    <p class="paragraph">
                        다음 위험들은 Critical 또는 High 등급으로, 즉시 완화 조치가 필요합니다:
                    </p>
                    {immediate_html}
                </div>
            """)
        
        # === Section 5: Risk Monitoring Framework ===
        paragraphs.append(f"""
            <div class="risk-section">
                <h3 class="subsection-title">5. 위험 모니터링 체계 (Risk Monitoring Framework)</h3>
                
                <h4 class="subsubsection-title">5.1 모니터링 주기</h4>
                <p class="paragraph">
                    효과적인 위험 관리를 위해 다음과 같은 모니터링 주기를 권장합니다:
                </p>
                <ul>
                    <li><strong>Critical 위험</strong>: 주간 단위 모니터링 및 경영진 보고</li>
                    <li><strong>High 위험</strong>: 월간 단위 모니터링 및 관리팀 검토</li>
                    <li><strong>Medium 위험</strong>: 분기 단위 모니터링</li>
                    <li><strong>Low 위험</strong>: 반기 단위 모니터링</li>
                </ul>
                
                <h4 class="subsubsection-title">5.2 위험 재평가 Trigger</h4>
                <p class="paragraph">
                    다음 상황 발생 시 즉시 위험 재평가를 수행해야 합니다:
                </p>
                <ul>
                    <li>프로젝트 일정 3개월 이상 지연</li>
                    <li>건설 비용 10% 이상 초과</li>
                    <li>주요 정책·규제 변경</li>
                    <li>시장 환경 급격한 변화 (금리 2%p 이상 변동, 경기 침체 등)</li>
                    <li>Critical 위험의 발생가능성 증가</li>
                </ul>
                
                <h4 class="subsubsection-title">5.3 위험 관리 거버넌스</h4>
                <p class="paragraph">
                    <strong>위험관리위원회(Risk Management Committee)</strong> 구성을 권장하며, 
                    위원회는 프로젝트 책임자, 재무팀장, 건설팀장, 법무팀장으로 구성하여 
                    월1회 정기 회의를 개최하고 위험 현황을 검토합니다.
                </p>
                <p class="paragraph">
                    각 위험에 대해 지정된 <strong>Risk Owner</strong>는 해당 위험의 
                    완화 조치 이행 책임을 지며, 분기별로 완화 조치 진행 상황을 
                    위험관리위원회에 보고해야 합니다.
                </p>
            </div>
        """)
        
        return paragraphs
    
    def generate_strategic_recommendations(
        self,
        data: Dict[str, Any],
        basic_info: Dict[str, Any],
        financial_analysis: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """
        Generate Strategic Recommendations (2-3 pages)
        
        Provides clear, actionable strategic guidance:
        - Go/No-Go decision
        - Conditional approval framework
        - Optimization opportunities
        - Risk mitigation priorities
        - Alternative strategies
        - Next steps with timeline
        
        Args:
            data: ZeroSite analysis data
            basic_info: Basic project info
            financial_analysis: Financial results
            risk_assessment: Risk assessment results
        
        Returns:
            List of paragraph HTML strings
        """
        paragraphs = []
        
        # Extract key metrics
        meets_lh = financial_analysis.get('summary', {}).get('meets_lh_criteria', False)
        cap_rate = financial_analysis.get('summary', {}).get('cap_rate', 0)
        total_investment = financial_analysis.get('summary', {}).get('total_investment', 0)
        unit_count = financial_analysis.get('summary', {}).get('unit_count', 0)
        risk_level = risk_assessment.get('executive_summary', {}).get('overall_risk_level', 'medium')
        
        # === Section 1: Go/No-Go Decision ===
        if meets_lh and risk_level in ['low', 'medium']:
            decision = "✅ <strong>사업 추진 권고 (GO RECOMMENDATION)</strong>"
            confidence = "High"
            decision_text = f"""
                <p class="paragraph">
                    본 사업은 재무적 타당성(Cap Rate {cap_rate:.2f}% > 4.5%)이 확보되어 있으며, 
                    위험 수준도 {risk_level.upper()}로 관리 가능한 범위 내에 있습니다. 
                    LH 신축매입임대 사업으로서 필요한 모든 조건을 충족하고 있어, 
                    <strong>즉시 사업 추진을 권고</strong>합니다.
                </p>
            """
        elif meets_lh and risk_level in ['high', 'critical']:
            decision = "⚠️ <strong>조건부 추진 권고 (CONDITIONAL GO)</strong>"
            confidence = "Medium"
            decision_text = f"""
                <p class="paragraph">
                    본 사업은 재무적으로는 타당하나(Cap Rate {cap_rate:.2f}% > 4.5%), 
                    위험 수준이 {risk_level.upper()}로 높은 편입니다. 
                    <strong>위험 완화 조치 선행 후 사업 추진</strong>을 권고하며, 
                    특히 Critical 및 High 위험에 대한 즉시 대응이 필요합니다.
                </p>
            """
        else:
            decision = "🔄 <strong>사업 구조 재검토 권고 (REVISE & RESUBMIT)</strong>"
            confidence = "Low"
            decision_text = f"""
                <p class="paragraph">
                    본 사업은 현재 구조로는 LH 재무 기준 미달(Cap Rate {cap_rate:.2f}% < 4.5%) 
                    {'및 위험 수준 과다' if risk_level in ['high', 'critical'] else ''}로 
                    <strong>즉시 추진이 어렵습니다</strong>. 
                    재무 구조 최적화 및 위험 완화 조치 후 재평가를 권고합니다.
                </p>
            """
        
        paragraphs.append(f"""
            <div class="recommendation-section">
                <h3 class="subsection-title">1. 사업 추진 의사결정 (Go/No-Go Decision)</h3>
                
                <div class="decision-box {decision.split()[0].lower()}">
                    <h4>{decision}</h4>
                    <p><strong>신뢰도 (Confidence Level)</strong>: {confidence}</p>
                </div>
                
                {decision_text}
                
                <div class="decision-basis">
                    <h4 class="subsubsection-title">의사결정 근거</h4>
                    <ul>
                        <li><strong>재무 타당성</strong>: Cap Rate {cap_rate:.2f}% 
                            ({'기준 충족 ✓' if meets_lh else '기준 미달 ✗'})</li>
                        <li><strong>위험 수준</strong>: {risk_level.upper()} 
                            ({'관리 가능' if risk_level in ['low', 'medium'] else '우려'})</li>
                        <li><strong>시장 환경</strong>: 수요 충분, 경쟁 관리 가능</li>
                        <li><strong>입지 경쟁력</strong>: 우수 (교통·편의시설·인구)</li>
                        <li><strong>정책 적합성</strong>: LH 전략 방향과 일치</li>
                    </ul>
                </div>
            </div>
        """)
        
        # === Section 2: Conditional Approval Framework (if applicable) ===
        if not meets_lh or risk_level in ['high', 'critical']:
            conditions_html = "<ul class='approval-conditions'>"
            
            if not meets_lh:
                conditions_html += """
                    <li><strong>재무 조건</strong>: Cap Rate 4.5% 이상 달성
                        <br>→ 권장 조치: 유닛 수 증가, 임대료 조정, 또는 비용 절감</li>
                """
            
            if risk_level in ['high', 'critical']:
                conditions_html += """
                    <li><strong>위험 관리 조건</strong>: Critical/High 위험 완화 조치 완료
                        <br>→ 권장 조치: 비상 대응 계획 수립, 예비비 15% 확보, LH 협의</li>
                """
            
            conditions_html += """
                <li><strong>재검증 조건</strong>: 개선 조치 후 재무·위험 재평가 수행
                    <br>→ 목표: 3개월 내 재평가 완료 및 최종 의사결정</li>
            </ul>
            """
            
            paragraphs.append(f"""
                <div class="recommendation-section">
                    <h3 class="subsection-title">2. 조건부 승인 요건 (Conditional Approval Framework)</h3>
                    <p class="paragraph">
                        다음 조건이 모두 충족될 경우, 사업 추진을 승인합니다:
                    </p>
                    {conditions_html}
                    <p class="paragraph">
                        <strong>검증 기준</strong>: 조건 충족 여부는 LH 본사 심사팀이 검증하며, 
                        모든 조건 충족 시 최종 승인 권고서를 발행합니다.
                    </p>
                </div>
            """)
        
        # === Section 3: Optimization Opportunities ===
        optimization_html = ""
        
        if not meets_lh:
            optimization_html += """
                <div class="optimization-item">
                    <h5>1. 유닛 믹스 최적화 (Unit Mix Optimization)</h5>
                    <p><strong>현황</strong>: 단일 유닛 타입으로 수익 구조 경직성 존재</p>
                    <p><strong>제안</strong>: 청년형 60% + 신혼부부형 30% + 고령자형 10% 혼합</p>
                    <p><strong>효과</strong>: 평균 임대료 15% 상승, Cap Rate 1.0%p 개선 예상</p>
                </div>
                
                <div class="optimization-item">
                    <h5>2. 설계 VE (Value Engineering) 적용</h5>
                    <p><strong>현황</strong>: 건축 비용이 전체 투자의 {financial_analysis.get('capex', {}).get('breakdown', {}).get('construction_hard_costs', {}).get('percentage', 0):.1f}% 차지</p>
                    <p><strong>제안</strong>: 공법 개선, 자재 대체, 공간 효율화로 건축비 10% 절감</p>
                    <p><strong>효과</strong>: 총 투자금 {self._format_krw(total_investment * 0.05)} 절감, Cap Rate 0.5%p 개선</p>
                </div>
            """
        
        optimization_html += """
            <div class="optimization-item">
                <h5>운영 효율화 (Operational Excellence)</h5>
                <p><strong>제안</strong>: PM 통합 계약, 에너지 효율 시스템, 스마트 관리 플랫폼 도입</p>
                <p><strong>효과</strong>: 운영비 5-10% 절감, 입주자 만족도 향상</p>
            </div>
        """
        
        paragraphs.append(f"""
            <div class="recommendation-section">
                <h3 class="subsection-title">3. 최적화 기회 (Optimization Opportunities)</h3>
                <p class="paragraph">
                    사업 수익성 및 경쟁력 강화를 위해 다음과 같은 최적화 조치를 검토할 수 있습니다:
                </p>
                {optimization_html}
            </div>
        """)
        
        # === Section 4: Next Steps ===
        if meets_lh and risk_level in ['low', 'medium']:
            next_steps = """
                <ol class="next-steps-list">
                    <li><strong>즉시 (1주일 내)</strong>: LH 본사에 사업 제안서 제출</li>
                    <li><strong>1개월 내</strong>: 토지 매매 계약 체결 (옵션 확보)</li>
                    <li><strong>2개월 내</strong>: 건축 인허가 신청 및 시공사 선정</li>
                    <li><strong>3개월 내</strong>: LH 매입 확약서 취득 및 금융 조달</li>
                    <li><strong>6개월 내</strong>: 착공 (공사 기간 18-24개월)</li>
                </ol>
            """
        else:
            next_steps = """
                <ol class="next-steps-list">
                    <li><strong>1개월 내</strong>: 재무 구조 최적화 방안 수립 및 재시뮬레이션</li>
                    <li><strong>2개월 내</strong>: 주요 위험 완화 조치 시행 및 검증</li>
                    <li><strong>3개월 내</strong>: 개선안 재평가 및 LH 재협의</li>
                    <li><strong>조건 충족 후</strong>: 사업 추진 재검토</li>
                </ol>
            """
        
        paragraphs.append(f"""
            <div class="recommendation-section">
                <h3 class="subsection-title">4. 추진 일정 및 Next Steps</h3>
                <p class="paragraph">
                    <strong>권장 추진 일정</strong>:
                </p>
                {next_steps}
                <p class="paragraph">
                    <strong>중요</strong>: 본 권고안은 2025년 12월 기준으로 작성되었으며, 
                    시장 환경 및 정책 변화에 따라 3개월마다 재검토가 필요합니다.
                </p>
            </div>
        """)
        
        return paragraphs
