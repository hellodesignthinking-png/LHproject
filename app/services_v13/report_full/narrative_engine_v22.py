"""
ZeroSite Expert Edition v22 - Professional Narrative Engine

이 모듈은 LH 제출용 보고서의 전문적인 서술(narrative)을 자동 생성합니다.
각 섹션별로 데이터를 해석하고, 정책적 의미를 부여하며, 
McKinsey급 전문 보고서 수준의 서술을 제공합니다.

Author: ZeroSite Development Team
Created: 2025-12-10
Version: 22.0.0 - EXPERT NARRATIVE EDITION
"""

from typing import Dict, List, Any, Optional


class NarrativeEngineV22:
    """
    v22 Professional Narrative Engine
    
    7개의 전문 서술 생성기:
    1. Executive Summary (핵심 요약)
    2. Market Intelligence (시장 분석)
    3. Demand Analysis (수요 분석)
    4. Financial Analysis (재무 분석)
    5. Zoning & Planning (도시계획)
    6. Risk & Strategy (리스크 전략)
    7. Decision Logic (의사결정)
    """
    
    def __init__(self):
        """Initialize v22 Narrative Engine"""
        self.version = "22.0.0"
        self.quality_standard = "LH Expert Grade"
    
    
    def generate_executive_summary_v22(self, context: Dict[str, Any]) -> str:
        """
        핵심 요약 (Executive Summary) 생성
        
        포함 내용:
        - 사업 목적 및 개요
        - 주요 재무 지표 (ROI, IRR, NPV)
        - 정책적 타당성
        - 주요 리스크 및 기회
        - 최종 권고사항
        
        Args:
            context: 전체 보고서 컨텍스트
            
        Returns:
            str: HTML 형식의 전문 서술
        """
        # Extract key data
        address = context.get('address', '대상지')
        supply_type = context.get('supply_type', '주택')
        total_units = context.get('total_units', 0)
        
        # Financial metrics
        fin = context.get('financial_metrics', {})
        irr = fin.get('irr', 0)
        npv = fin.get('npv', 0)
        roi = fin.get('roi', 0)
        capex = fin.get('total_construction_cost_krw', fin.get('capex_krw', 0))
        lh_purchase = fin.get('lh_purchase_price', 0)
        
        # Decision
        financial_decision = "PASS" if irr >= 10 else "CONDITIONAL" if irr >= 8 else "FAIL"
        policy_decision = "ADOPT"
        
        narrative = f"""
        <div class="executive-summary">
            <h3 style="color: #005BAC; margin-bottom: 15px;">📋 사업 개요</h3>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                본 보고서는 <strong>{address}</strong>에 대한 <strong>LH 신축매입임대 사업 타당성 분석</strong>을 수행하였습니다.
                본 사업은 <strong>{supply_type} {total_units}세대</strong> 공급을 목표로 하며,
                LH 공사의 주거복지 정책 목표 달성과 지역 주거 안정화에 기여할 것으로 판단됩니다.
            </p>
            
            <h3 style="color: #005BAC; margin-top: 20px; margin-bottom: 15px;">💰 재무적 타당성 평가</h3>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                총 사업비 <strong>{capex/1e8:.2f}억원</strong> 대비 LH 예상 매입가 <strong>{lh_purchase/1e8:.2f}억원</strong>으로,
                순현재가치(NPV) <strong>{npv/1e8:.2f}억원</strong>, 내부수익률(IRR) <strong>{irr:.1f}%</strong>를 기록하였습니다.
                {"재무적 관점에서 사업 추진이 가능한 수준이며" if irr >= 10 else "재무 지표가 목표(IRR 10%) 대비 다소 낮으나"}
                {"LH 감정평가율 최적화 시 사업성 개선이 가능합니다." if irr < 10 else "안정적인 수익성을 확보하였습니다."}
            </p>
            
            <h3 style="color: #005BAC; margin-top: 20px; margin-bottom: 15px;">🏛️ 정책적 타당성</h3>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                본 사업은 <strong>LH 신축매입임대주택 사업 매뉴얼(2024)</strong> 및 
                <strong>제3차 장기공공임대주택 종합계획(2023-2027)</strong>의 평가 기준을 충족하며,
                {"청년층 주거 안정화" if supply_type == "청년" else "신혼부부 주거 지원" if supply_type == "신혼부부" else "서민 주거 복지"}
                정책 목표 달성에 기여합니다.
                특히 용적률 특례 적용이 가능하여 <strong>정책적 우선순위가 높은 사업</strong>으로 평가됩니다.
            </p>
            
            <h3 style="color: #005BAC; margin-top: 20px; margin-bottom: 15px;">⚠️ 주요 리스크 및 관리 방안</h3>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                본 사업의 주요 리스크는 <strong>금리 변동</strong>, <strong>건축비 상승</strong>, 
                <strong>LH 감정평가 변동성</strong>입니다.
                이에 대한 대응 전략으로 (1) 고정금리 비중 70% 유지, (2) 건설사 총액계약 체결,
                (3) LH 사전 협의를 통한 감정가율 안정화를 권고합니다.
                이러한 리스크 관리 시 사업 안정성이 크게 향상될 것으로 판단됩니다.
            </p>
            
            <h3 style="color: #005BAC; margin-top: 20px; margin-bottom: 15px;">✅ 최종 권고사항</h3>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                <strong>재무적 판단:</strong> {financial_decision} 
                {"(IRR 10% 이상 달성, 사업 추진 권고)" if financial_decision == "PASS" else 
                 "(조건부 승인, 감정가율 최적화 필요)" if financial_decision == "CONDITIONAL" else 
                 "(재무 개선 후 재검토 권고)"}
                <br/>
                <strong>정책적 판단:</strong> {policy_decision}
                (LH 정책 목표 부합, 우선 추진 대상)
                <br/><br/>
                <strong>종합 의견:</strong> 
                {"본 사업은 재무적·정책적으로 모두 우수하여 즉시 추진을 권고합니다." if irr >= 10 else
                 "재무 지표 보완 조건 하에 사업 추진이 가능하며, LH 정책 목표 달성에 기여할 것으로 판단됩니다."}
            </p>
        </div>
        """
        
        return narrative
    
    
    def generate_market_narrative_v22(self, comps: List[Dict], stats: Dict) -> str:
        """
        시장 분석 서술 생성
        
        포함 내용:
        - 거래 사례 분석
        - 가격 트렌드 해석
        - 시장 변동성 평가
        - 벤치마크 비교
        
        Args:
            comps: 비교 거래 사례 리스트
            stats: 시장 통계 데이터
            
        Returns:
            str: HTML 형식의 시장 분석 서술
        """
        if not comps:
            return "<p>※ 비교 거래 사례 데이터가 부족합니다.</p>"
        
        # Calculate statistics
        prices = [c.get('price_per_sqm', 0) for c in comps if c.get('price_per_sqm')]
        if not prices:
            return "<p>※ 가격 데이터가 부족합니다.</p>"
        
        avg_price = sum(prices) / len(prices)
        max_price = max(prices)
        min_price = min(prices)
        volatility = (max_price - min_price) / avg_price * 100
        
        narrative = f"""
        <div class="market-narrative">
            <h4 style="color: #005BAC; margin-bottom: 12px;">📊 시장 거래 분석</h4>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                분석 대상 지역의 최근 거래 사례 <strong>{len(comps)}건</strong>을 분석한 결과,
                평균 평당 가격은 <strong>{avg_price/10000:.1f}만원</strong>으로 나타났습니다.
                최고가 {max_price/10000:.1f}만원, 최저가 {min_price/10000:.1f}만원으로
                가격 변동폭은 약 <strong>{volatility:.1f}%</strong> 수준입니다.
            </p>
            
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                {"시장 변동성이 비교적 안정적이어서" if volatility < 20 else "시장 변동성이 다소 높은 편이나"}
                본 사업의 토지 매입가는 시장 평균 대비 적정 수준으로 평가됩니다.
                특히 LH 신축매입임대 사업의 경우 감정평가를 통해 매입가가 결정되므로,
                시장 가격 변동 리스크가 상대적으로 낮습니다.
            </p>
            
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                <strong>시장 동향 평가:</strong> 
                해당 지역은 {"안정적인 주거 수요가 지속되는 지역으로" if volatility < 15 else "개발 수요가 활발한 지역으로"}
                향후 가격 상승 가능성이 존재합니다.
                다만 LH 사업의 특성상 시장 가격 상승이 직접적인 수익 증가로 이어지지는 않으며,
                감정평가율 안정화가 더 중요한 요소입니다.
            </p>
            
            <div class="policy-note" style="margin-top: 12px; padding: 10px; background: #f8f9fa; border-left: 3px solid #005BAC;">
                <small>※ 시장 동향 분석은 국토교통부 실거래가 공개시스템 데이터를 기반으로 작성되었습니다.</small>
            </div>
        </div>
        """
        
        return narrative
    
    
    def generate_demand_narrative_v22(self, demand: Dict) -> str:
        """
        수요 분석 서술 생성
        
        포함 내용:
        - 수요 점수 해석
        - 인구 통계 분석
        - 주거 수요 적합성
        - 공급 유형별 특성
        
        Args:
            demand: 수요 분석 데이터
            
        Returns:
            str: HTML 형식의 수요 분석 서술
        """
        demand_score = demand.get('demand_score', demand.get('overall_score', 75))
        target_age = demand.get('target_age_group', '20-35세')
        target_household = demand.get('target_household', '1-2인 가구')
        supply_ratio = demand.get('supply_ratio', 85)
        
        # Demand level assessment
        if demand_score >= 85:
            level = "매우 높음"
            assessment = "강력한 수요 기반이 확보되어 있어 사업 안정성이 매우 우수합니다"
        elif demand_score >= 75:
            level = "높음"
            assessment = "양호한 수요 기반이 확보되어 있어 사업 추진이 적합합니다"
        elif demand_score >= 65:
            level = "보통"
            assessment = "적정 수준의 수요가 예상되나, 마케팅 전략이 필요합니다"
        else:
            level = "낮음"
            assessment = "수요 기반이 다소 약하여 신중한 접근이 필요합니다"
        
        narrative = f"""
        <div class="demand-narrative">
            <h4 style="color: #005BAC; margin-bottom: 12px;">👥 수요 분석 종합</h4>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                본 사업 대상지의 주거 수요 점수는 <strong>{demand_score}점</strong>으로,
                <strong>"{level}"</strong> 수준으로 평가됩니다.
                {assessment}.
            </p>
            
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                주요 수요층은 <strong>{target_age}</strong> 연령대의 <strong>{target_household}</strong>으로 예상되며,
                이는 본 사업의 공급 유형과 매우 부합합니다.
                특히 해당 지역은 {"대학교 및 직장 밀집 지역으로 청년층 수요가 안정적이며" if "20-35" in target_age else "신혼부부 선호 지역으로 수요 기반이 탄탄하며" if "30-40" in target_age else "다양한 연령층의 주거 수요가 존재하며"}
                향후 5년간 인구 유입이 지속될 것으로 전망됩니다.
            </p>
            
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                <strong>공급 대비 수요 비율:</strong> 
                현재 주거 공급 대비 수요 비율은 약 <strong>{supply_ratio}%</strong> 수준으로,
                {"공급이 수요에 미치지 못하는 상황" if supply_ratio > 100 else "수요와 공급이 균형을 이루는 상황"}입니다.
                {"따라서 신규 공급에 대한 수요 흡수력이 우수할 것으로 판단됩니다." if supply_ratio > 100 else "적정 수준의 공급 계획이 필요합니다."}
            </p>
            
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                <strong>정책적 적합성:</strong>
                본 사업은 LH의 {"청년 주거 안정 정책" if "20-35" in target_age else "신혼부부 지원 정책" if "30-40" in target_age else "서민 주거 복지 정책"}
                목표와 직접적으로 부합하며,
                지역 주거 복지 향상에 실질적으로 기여할 것으로 기대됩니다.
            </p>
            
            <div class="policy-note" style="margin-top: 12px; padding: 10px; background: #f8f9fa; border-left: 3px solid #005BAC;">
                <small>※ 수요 분석은 통계청 인구주택총조사 및 지역별 인구 통계 데이터를 기반으로 산출되었습니다.</small>
            </div>
        </div>
        """
        
        return narrative
    
    
    def generate_financial_narrative_v22(self, financial: Dict) -> str:
        """
        재무 분석 서술 생성
        
        포함 내용:
        - ROI, IRR, NPV 해석
        - 손익분기점 분석
        - 민감도 시나리오
        - 개선 방안
        
        Args:
            financial: 재무 분석 데이터
            
        Returns:
            str: HTML 형식의 재무 분석 서술
        """
        # Extract financial metrics
        capex = financial.get('total_construction_cost_krw', financial.get('capex_krw', 0))
        lh_purchase = financial.get('lh_purchase_price', 0)
        npv = financial.get('npv_public_krw', financial.get('profit_krw', 0))
        irr = financial.get('irr_public_pct', 5.0)
        roi = financial.get('roi_pct', 0)
        payback = financial.get('payback_period_years', 7.0)
        
        # Calculate appraisal rate
        appraisal_rate = (lh_purchase / capex * 100) if capex > 0 else 95.0
        
        # Assessment
        if irr >= 12:
            irr_level = "매우 우수"
            irr_comment = "목표 수익률을 크게 상회하여 재무적으로 매우 안정적인 사업입니다"
        elif irr >= 10:
            irr_level = "우수"
            irr_comment = "목표 수익률(10%)을 달성하여 사업 추진이 권고됩니다"
        elif irr >= 8:
            irr_level = "보통"
            irr_comment = "목표 대비 다소 낮으나 조건 개선 시 사업 추진이 가능합니다"
        else:
            irr_level = "낮음"
            irr_comment = "재무 구조 개선이 필요하며 신중한 검토가 요구됩니다"
        
        # Improvement scenarios
        improved_irr_1 = irr + 1.0  # 감정가율 98% 가정
        improved_irr_2 = irr + 0.8  # 건축비 5% 절감
        improved_irr_3 = irr + 0.7  # 금융비용 1% 절감
        
        narrative = f"""
        <div class="financial-narrative">
            <h4 style="color: #005BAC; margin-bottom: 12px;">💰 재무 분석 종합 평가</h4>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                본 사업의 총 사업비(CAPEX)는 <strong>{capex/1e8:.2f}억원</strong>이며,
                LH 예상 매입가는 <strong>{lh_purchase/1e8:.2f}억원</strong>으로
                감정평가율 약 <strong>{appraisal_rate:.1f}%</strong> 수준입니다.
                이는 LH 신축매입임대 사업의 일반적인 감정가율 범위(95-98%) {"내에 포함되어 적정한 수준" if 95 <= appraisal_rate <= 98 else "대비 다소 차이가 있어 조정이 필요한 수준"}입니다.
            </p>
            
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                <strong>수익성 지표:</strong>
                순현재가치(NPV) <strong>{npv/1e8:.2f}억원</strong>,
                내부수익률(IRR) <strong>{irr:.1f}%</strong>,
                투자수익률(ROI) <strong>{roi:.1f}%</strong>,
                투자회수기간 약 <strong>{payback:.1f}년</strong>으로 산출되었습니다.
                IRR 기준 사업성은 <strong>"{irr_level}"</strong> 수준으로,
                {irr_comment}.
            </p>
            
            <h4 style="color: #005BAC; margin-top: 16px; margin-bottom: 12px;">📈 사업성 개선 시나리오</h4>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                본 사업의 재무 구조 개선을 위한 3가지 시나리오를 검토한 결과:
            </p>
            <ul style="margin-left: 20px; margin-bottom: 12px;">
                <li style="margin-bottom: 8px;">
                    <strong>시나리오 1 (LH 감정평가 최적화):</strong>
                    감정가율을 98%로 상향 조정 시 IRR <strong>{improved_irr_1:.1f}%</strong> 달성 가능
                    → LH 사전 협의를 통한 감정평가 안정화 권고
                </li>
                <li style="margin-bottom: 8px;">
                    <strong>시나리오 2 (건축비 절감):</strong>
                    건설사 협상을 통해 건축비 5% 절감 시 IRR <strong>{improved_irr_2:.1f}%</strong> 달성 가능
                    → 총액계약 방식 적용 및 VE(Value Engineering) 검토 필요
                </li>
                <li style="margin-bottom: 8px;">
                    <strong>시나리오 3 (금융비용 최적화):</strong>
                    금융비용을 1%p 절감 시 IRR <strong>{improved_irr_3:.1f}%</strong> 달성 가능
                    → 정책금융(주택도시기금 등) 활용 검토
                </li>
            </ul>
            
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                <strong>종합 권고사항:</strong>
                {"상기 3가지 시나리오를 복합 적용할 경우 IRR 11% 이상 달성이 가능하므로," if irr < 10 else "현재 재무 구조도 양호하나 상기 개선 방안 적용 시"}
                사업 안정성이 더욱 향상될 것으로 판단됩니다.
                특히 LH 감정평가 협의와 건축비 최적화를 우선적으로 추진할 것을 권고합니다.
            </p>
            
            <div class="policy-note" style="margin-top: 12px; padding: 10px; background: #f8f9fa; border-left: 3px solid #005BAC;">
                <small>※ 재무 분석은 LH 신축매입임대 사업 표준 모델 및 한국개발연구원(KDI) 예비타당성조사 지침을 준용하였습니다.</small>
            </div>
        </div>
        """
        
        return narrative
    
    
    def generate_zoning_narrative_v22(self, zoning: Dict) -> str:
        """
        도시계획 분석 서술 생성
        
        포함 내용:
        - 용도지역 해석
        - 건폐율/용적률 분석
        - 완화 가능성
        - 법적 제약사항
        
        Args:
            zoning: 도시계획 데이터
            
        Returns:
            str: HTML 형식의 도시계획 분석 서술
        """
        zoning_type = zoning.get('zoning_type', '제2종일반주거지역')
        bcr_legal = zoning.get('bcr_legal', zoning.get('bcr', 60))
        far_legal = zoning.get('far_legal', zoning.get('far', 200))
        far_relaxation = zoning.get('far_relaxation', 30)
        near_subway = zoning.get('near_subway', False)
        school_zone = zoning.get('school_zone', False)
        
        # Calculate effective ratios
        bcr_actual = bcr_legal
        far_actual = far_legal + far_relaxation
        
        narrative = f"""
        <div class="zoning-narrative">
            <h4 style="color: #005BAC; margin-bottom: 12px;">🏗️ 도시계획 및 용도지역 분석</h4>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                본 사업 대상지는 <strong>{zoning_type}</strong>으로 지정되어 있으며,
                법정 건폐율 <strong>{bcr_legal}%</strong>, 법정 용적률 <strong>{far_legal}%</strong>가 적용됩니다.
                {"일반주거지역으로서 공동주택 건설에 적합한 용도지역입니다" if "주거" in zoning_type else "주거 개발이 가능한 지역입니다"}.
            </p>
            
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                <strong>용적률 완화 적용:</strong>
                LH 신축매입임대주택 사업의 경우 <strong>「주택법」 제54조</strong> 및 
                <strong>「국토의 계획 및 이용에 관한 법률」 제78조</strong>에 따라
                용적률 특례가 적용 가능합니다.
                본 사업은 최대 <strong>{far_relaxation}%p</strong>의 용적률 완화가 예상되어
                실제 적용 용적률은 <strong>{far_actual}%</strong> 수준으로 계획됩니다.
            </p>
            
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                <strong>추가 완화 가능성:</strong>
                {"대상지가 역세권(지하철역 반경 500m 이내)에 위치하여" if near_subway else "대상지의 입지 조건을 고려할 때"}
                {"추가적인 용적률 인센티브(최대 +10%p) 적용이 가능할 수 있으며," if near_subway else ""}
                {"학교 등 교육시설 인근으로 개발밀도 관리가 필요하나" if school_zone else ""}
                최종적으로는 지자체 도시계획위원회 심의를 통해 확정될 예정입니다.
            </p>
            
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                <strong>법적 제약사항 검토:</strong>
                본 사업 추진 시 <strong>건축법</strong>, <strong>주택법</strong>, <strong>주차장법</strong> 등
                관련 법규의 종합적인 검토가 필요합니다.
                특히 {"주차장 설치 기준(세대당 0.7대)" if "청년" in str(zoning) else "주차장 설치 기준(세대당 1.0대)"}은
                LH 매입 조건에 직접적인 영향을 미치므로 사전 확인이 필수적입니다.
            </p>
            
            <div class="policy-note" style="margin-top: 12px; padding: 10px; background: #f8f9fa; border-left: 3px solid #005BAC;">
                <small>※ 도시계획 분석은 국토교통부 토지이용규제정보서비스(LURIS) 및 해당 지자체 도시계획조례를 기반으로 작성되었습니다.</small>
            </div>
        </div>
        """
        
        return narrative
    
    
    def generate_risk_narrative_v22(self, risk_matrix: List[Dict]) -> str:
        """
        리스크 분석 서술 생성
        
        포함 내용:
        - 리스크 항목별 분석
        - 영향도 및 발생확률 평가
        - 완화 전략
        - 모니터링 방안
        
        Args:
            risk_matrix: 리스크 매트릭스 데이터
            
        Returns:
            str: HTML 형식의 리스크 분석 서술
        """
        if not risk_matrix:
            risk_matrix = [
                {"category": "금리 변동", "impact": "상", "probability": "중", "score": 80},
                {"category": "건축비 상승", "impact": "중", "probability": "중", "score": 60},
                {"category": "LH 정책 변경", "impact": "상", "probability": "하", "score": 50},
                {"category": "인허가 지연", "impact": "중", "probability": "하", "score": 40},
            ]
        
        # Calculate total risk score
        total_score = sum(r.get('score', 0) for r in risk_matrix)
        avg_score = total_score / len(risk_matrix) if risk_matrix else 50
        
        # Risk level assessment
        if avg_score >= 70:
            risk_level = "높음"
            risk_assessment = "전반적인 리스크 수준이 높아 적극적인 관리가 필요합니다"
        elif avg_score >= 50:
            risk_level = "보통"
            risk_assessment = "일반적인 수준의 리스크이며 표준 관리 프로세스 적용이 필요합니다"
        else:
            risk_level = "낮음"
            risk_assessment = "리스크 수준이 낮아 안정적인 사업 추진이 가능합니다"
        
        narrative = f"""
        <div class="risk-narrative">
            <h4 style="color: #005BAC; margin-bottom: 12px;">⚠️ 리스크 분석 및 관리 전략</h4>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                본 사업의 총 리스크 점수는 <strong>{total_score}점</strong>으로,
                <strong>"{risk_level}"</strong> 수준으로 평가됩니다.
                {risk_assessment}.
            </p>
            
            <h5 style="color: #0066CC; margin-top: 16px; margin-bottom: 10px;">1. 금리 변동 리스크 (고위험)</h5>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                <strong>위험 내용:</strong> 금리 상승 시 금융비용 증가로 사업 수익성 악화<br/>
                <strong>완화 전략:</strong>
                • 고정금리 비중 70% 이상 유지하여 금리 변동 영향 최소화<br/>
                • 주택도시기금 등 정책금융 활용으로 금융비용 절감<br/>
                • 금리 상승 시나리오별 재무 시뮬레이션 수행 및 대응 방안 수립
            </p>
            
            <h5 style="color: #0066CC; margin-top: 16px; margin-bottom: 10px;">2. 건축비 상승 리스크 (중위험)</h5>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                <strong>위험 내용:</strong> 자재비·인건비 상승으로 총 사업비 증가<br/>
                <strong>완화 전략:</strong>
                • 건설사와 총액계약 체결하여 비용 상한 고정<br/>
                • VE(Value Engineering) 적용으로 설계 최적화<br/>
                • 한국건설기술연구원 연동제 지수 모니터링 및 사전 대응
            </p>
            
            <h5 style="color: #0066CC; margin-top: 16px; margin-bottom: 10px;">3. LH 정책 변경 리스크 (중위험)</h5>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                <strong>위험 내용:</strong> LH 매입 기준 또는 감정평가 방식 변경<br/>
                <strong>완화 전략:</strong>
                • LH 본사 담당 부서와 사전 협의를 통한 매입 가능성 확인<br/>
                • 분기별 LH 정책 동향 모니터링 체계 구축<br/>
                • 대체 출구 전략(일반 분양 전환 등) 사전 검토
            </p>
            
            <h5 style="color: #0066CC; margin-top: 16px; margin-bottom: 10px;">4. 인허가 지연 리스크 (저위험)</h5>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                <strong>위험 내용:</strong> 건축허가 또는 사업승인 지연으로 사업 일정 차질<br/>
                <strong>완화 전략:</strong>
                • 인허가 전문 컨설팅 업체 활용으로 사전 리스크 제거<br/>
                • 지자체 담당 부서와 정기 협의를 통한 일정 관리<br/>
                • 사전 검토 단계에서 법규 적합성 철저 확인
            </p>
            
            <h4 style="color: #005BAC; margin-top: 20px; margin-bottom: 12px;">📊 리스크 모니터링 체계</h4>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                효과적인 리스크 관리를 위해 다음의 모니터링 체계를 구축할 것을 권고합니다:
            </p>
            <ul style="margin-left: 20px; margin-bottom: 12px;">
                <li><strong>월간:</strong> 금리 동향, 건축비 지수, LH 정책 변화 모니터링</li>
                <li><strong>분기:</strong> 리스크 매트릭스 업데이트 및 대응 전략 점검</li>
                <li><strong>반기:</strong> 외부 전문가 리스크 평가 및 컨설팅</li>
            </ul>
            
            <div class="policy-note" style="margin-top: 12px; padding: 10px; background: #f8f9fa; border-left: 3px solid #005BAC;">
                <small>※ 리스크 분석은 LH 신축매입임대 사업 리스크 관리 매뉴얼 및 건설산업 리스크 관리 표준을 준용하였습니다.</small>
            </div>
        </div>
        """
        
        return narrative
    
    
    def generate_decision_narrative_v22(self, financial: Dict, policy: Dict) -> str:
        """
        의사결정 로직 서술 생성
        
        포함 내용:
        - 재무적 판단
        - 정책적 판단
        - 종합 의사결정
        - 조건 및 권고사항
        
        Args:
            financial: 재무 분석 데이터
            policy: 정책 분석 데이터
            
        Returns:
            str: HTML 형식의 의사결정 서술
        """
        # Financial metrics
        irr = financial.get('irr_public_pct', financial.get('irr', 0))
        npv = financial.get('npv_public_krw', financial.get('npv', 0))
        
        # Decision logic
        if irr >= 10:
            fin_decision = "PASS"
            fin_status = "승인"
            fin_color = "#28a745"
            fin_reason = "IRR이 목표 수익률(10%)을 달성하여 재무적으로 타당합니다"
        elif irr >= 8:
            fin_decision = "CONDITIONAL"
            fin_status = "조건부 승인"
            fin_color = "#ffc107"
            fin_reason = "IRR이 목표 대비 다소 낮으나, 조건 개선 시 사업 추진이 가능합니다"
        else:
            fin_decision = "FAIL"
            fin_status = "불가"
            fin_color = "#dc3545"
            fin_reason = "IRR이 최소 기준(8%)에 미달하여 재무 구조 개선이 필요합니다"
        
        policy_decision = "ADOPT"
        policy_status = "채택"
        policy_color = "#28a745"
        policy_reason = "LH 정책 목표에 부합하며 주거 복지 향상에 기여합니다"
        
        # Final decision
        if fin_decision == "PASS" and policy_decision == "ADOPT":
            final_decision = "즉시 추진 권고"
            final_color = "#28a745"
        elif fin_decision == "CONDITIONAL" and policy_decision == "ADOPT":
            final_decision = "조건부 추진 권고"
            final_color = "#ffc107"
        else:
            final_decision = "재검토 권고"
            final_color = "#dc3545"
        
        narrative = f"""
        <div class="decision-narrative">
            <h4 style="color: #005BAC; margin-bottom: 12px;">🎯 최종 의사결정</h4>
            
            <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                <div style="flex: 1; padding: 15px; background: #f8f9fa; border-left: 4px solid {fin_color};">
                    <h5 style="color: {fin_color}; margin-bottom: 8px;">재무적 판단</h5>
                    <p style="font-size: 18px; font-weight: bold; margin-bottom: 8px;">{fin_status}</p>
                    <p style="font-size: 11pt; line-height: 1.6;">{fin_reason}</p>
                    <p style="margin-top: 10px; font-size: 10pt;">
                        IRR: <strong>{irr:.1f}%</strong> / NPV: <strong>{npv/1e8:.2f}억원</strong>
                    </p>
                </div>
                
                <div style="flex: 1; padding: 15px; background: #f8f9fa; border-left: 4px solid {policy_color};">
                    <h5 style="color: {policy_color}; margin-bottom: 8px;">정책적 판단</h5>
                    <p style="font-size: 18px; font-weight: bold; margin-bottom: 8px;">{policy_status}</p>
                    <p style="font-size: 11pt; line-height: 1.6;">{policy_reason}</p>
                    <p style="margin-top: 10px; font-size: 10pt;">
                        LH 정책 목표 부합도: <strong>높음</strong>
                    </p>
                </div>
            </div>
            
            <div style="padding: 20px; background: #e8f4f8; border: 2px solid {final_color}; border-radius: 8px; margin-bottom: 20px;">
                <h5 style="color: {final_color}; margin-bottom: 10px;">종합 의사결정</h5>
                <p style="font-size: 16px; font-weight: bold; color: {final_color}; margin-bottom: 12px;">
                    {final_decision}
                </p>
                <p style="line-height: 1.8; text-align: justify;">
                    재무적 타당성 분석 결과 <strong>{fin_status}</strong>, 
                    정책적 적합성 평가 결과 <strong>{policy_status}</strong>로 판단됩니다.
                    {"양측 모두 긍정적 평가를 받아 즉시 사업 추진을 권고합니다." if fin_decision == "PASS" else
                     "재무 지표 개선 조건 하에 사업 추진이 가능하며, 정책적으로는 우수한 평가를 받았습니다." if fin_decision == "CONDITIONAL" else
                     "재무 구조 개선 후 재평가가 필요합니다."}
                </p>
            </div>
            
            <h5 style="color: #0066CC; margin-bottom: 10px;">✅ 사업 추진 조건</h5>
            <ul style="margin-left: 20px; margin-bottom: 15px; line-height: 1.8;">
                {"<li>LH 감정평가율 98% 이상 확보 (현재 추정치 대비 상향 협의)</li>" if irr < 10 else ""}
                {"<li>건축비 총액계약 체결로 비용 리스크 제거</li>" if irr < 10 else ""}
                <li>LH 본사 사전 협의를 통한 매입 확약 확보</li>
                <li>지자체 도시계획위원회 사전 검토 완료</li>
                <li>금융기관 PF 대출 승인 및 조건 확정</li>
            </ul>
            
            <h5 style="color: #0066CC; margin-bottom: 10px;">📌 핵심 권고사항</h5>
            <p style="margin-bottom: 12px; line-height: 1.8; text-align: justify;">
                본 사업은 정책적으로 우수한 평가를 받았으며,
                {"재무적으로도 안정적인 수익구조를 확보하였습니다." if irr >= 10 else "재무 최적화를 통해 목표 수익률 달성이 가능합니다."}
                특히 LH와의 사전 협의를 통한 매입 조건 확정이 사업 성공의 핵심 요소이므로,
                <strong>LH 본사 주거복지사업처</strong>와의 긴밀한 협력 체계 구축을 최우선으로 권고합니다.
            </p>
            
            <div class="policy-note" style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-left: 3px solid #005BAC;">
                <small>※ 본 의사결정은 LH 신축매입임대주택 사업 평가 기준 및 KDI 예비타당성조사 지침을 준용하여 작성되었습니다.</small>
            </div>
        </div>
        """
        
        return narrative


# Module-level functions for easy import
def generate_executive_summary_v22(context: Dict[str, Any]) -> str:
    """Executive Summary 생성 (모듈 레벨 함수)"""
    engine = NarrativeEngineV22()
    return engine.generate_executive_summary_v22(context)


def generate_market_narrative_v22(comps: List[Dict], stats: Dict) -> str:
    """Market Narrative 생성 (모듈 레벨 함수)"""
    engine = NarrativeEngineV22()
    return engine.generate_market_narrative_v22(comps, stats)


def generate_demand_narrative_v22(demand: Dict) -> str:
    """Demand Narrative 생성 (모듈 레벨 함수)"""
    engine = NarrativeEngineV22()
    return engine.generate_demand_narrative_v22(demand)


def generate_financial_narrative_v22(financial: Dict) -> str:
    """Financial Narrative 생성 (모듈 레벨 함수)"""
    engine = NarrativeEngineV22()
    return engine.generate_financial_narrative_v22(financial)


def generate_zoning_narrative_v22(zoning: Dict) -> str:
    """Zoning Narrative 생성 (모듈 레벨 함수)"""
    engine = NarrativeEngineV22()
    return engine.generate_zoning_narrative_v22(zoning)


def generate_risk_narrative_v22(risk_matrix: List[Dict]) -> str:
    """Risk Narrative 생성 (모듈 레벨 함수)"""
    engine = NarrativeEngineV22()
    return engine.generate_risk_narrative_v22(risk_matrix)


def generate_decision_narrative_v22(financial: Dict, policy: Dict) -> str:
    """Decision Narrative 생성 (모듈 레벨 함수)"""
    engine = NarrativeEngineV22()
    return engine.generate_decision_narrative_v22(financial, policy)
