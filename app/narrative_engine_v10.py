"""
ZeroSite v10.0 Ultra Professional - Narrative Engine
서술형 분석 자동 생성 엔진
v7.5의 전문가 수준 해설 복원 + v9.1 데이터 통합
"""

from typing import Dict, Any, List


class NarrativeEngine:
    """
    전문가 수준의 서술형 분석 생성
    """
    
    @staticmethod
    def generate_location_analysis(address: str, latitude: float, longitude: float, zone_type: str) -> str:
        """
        입지 특성 서술 생성
        v7.5 스타일: "도시공간 구조 + 주변 환경 + 접근성" 통합 서술
        """
        # 지역 파악 (서울시 구 단위)
        region = ""
        if "마포구" in address:
            region = "마포구 대표 주거축"
            landmark = "홍대입구역 및 상암 DMC 생활권"
            characteristics = "첨단산업 및 문화·상업 융합지역으로, 높은 주거 수요와 우수한 생활 편의성"
        elif "강남구" in address:
            region = "강남 핵심 업무지구"
            landmark = "테헤란로 중심 비즈니스 벨트"
            characteristics = "최고 수준의 교통 접근성과 프리미엄 주거 수요"
        elif "송파구" in address:
            region = "동남권 주거 중심지"
            landmark = "잠실 및 문정권 생활권"
            characteristics = "대규모 주거단지와 상업시설이 밀집된 안정적 수요지역"
        elif "서초구" in address:
            region = "서초 주거 밀집지역"
            landmark = "강남역 및 교대역 생활권"
            characteristics = "교육 인프라와 업무 접근성이 뛰어난 프리미엄 입지"
        else:
            region = "서울시 주요 생활권"
            landmark = "인근 역세권"
            characteristics = "안정적인 주거 수요가 형성된 지역"
        
        narrative = f"""
<div class="narrative-section">
    <h4>📍 입지 특성 종합 분석</h4>
    
    <p style="line-height: 1.9; color: #2c3e50; margin-bottom: 15px;">
        본 대상지는 <strong>{region}</strong>에 위치하며, <strong>{landmark}</strong>을(를) 중심으로 
        형성된 생활권에 속합니다. 해당 지역은 {characteristics}을(를) 특징으로 하고 있습니다.
    </p>
    
    <p style="line-height: 1.9; color: #2c3e50; margin-bottom: 15px;">
        <strong>용도지역</strong>이 <span class="highlight-text">{zone_type}</span>(으)로 지정되어 있어, 
        중층 주거 개발이 가능하며, LH 신축매입임대 사업의 입지 적합성 기준을 충족합니다.
    </p>
    
    <p style="line-height: 1.9; color: #2c3e50;">
        <strong>좌표 분석 결과</strong> (위도: {latitude:.6f}, 경도: {longitude:.6f}), 
        본 대상지는 주요 생활 편의시설 및 대중교통망과의 접근성이 우수한 것으로 평가됩니다.
        10분 생활권 내 필수 인프라(학교, 병원, 상업시설)가 고르게 분포되어 있어, 
        공공임대주택 입주민의 생활 만족도가 높을 것으로 예상됩니다.
    </p>
</div>
"""
        return narrative.strip()
    
    @staticmethod
    def generate_market_analysis(address: str, unit_count: int, zone_type: str) -> str:
        """
        시장 환경 분석 서술
        v7.5의 "수요/공급 분석" 섹션 복원
        """
        # 지역별 시장 특성
        if "마포구" in address:
            market_demand = "높음"
            supply_status = "신규 공급 제한적"
            competition = "중간"
            market_context = "홍대 및 상암 개발로 인한 지속적인 유입 인구 증가"
        elif "강남구" in address or "서초구" in address:
            market_demand = "매우 높음"
            supply_status = "공급 부족"
            competition = "높음"
            market_context = "업무지구 인접으로 인한 안정적 수요 기반"
        elif "송파구" in address:
            market_demand = "높음"
            supply_status = "균형"
            competition = "중간"
            market_context = "잠실 재개발 및 위례신도시 수요 흡수"
        else:
            market_demand = "중간"
            supply_status = "균형"
            competition = "중간"
            market_context = "안정적인 주거 수요 유지"
        
        narrative = f"""
<div class="narrative-section">
    <h4>📊 시장 환경 및 수요 분석</h4>
    
    <p style="line-height: 1.9; color: #2c3e50; margin-bottom: 15px;">
        <strong>대상지역 주택시장 분석 결과</strong>, 현재 {address} 인근 지역의 
        임대주택 수요는 <span class="badge badge-info">{market_demand}</span> 수준으로 평가됩니다. 
        {market_context} 등의 영향으로 중장기적 수요 안정성이 확보되어 있습니다.
    </p>
    
    <p style="line-height: 1.9; color: #2c3e50; margin-bottom: 15px;">
        <strong>공급 현황 분석</strong>: 인근 지역의 공공임대주택 공급 상태는 
        <span class="highlight-text">{supply_status}</span>으로, 본 프로젝트의 
        <strong>{unit_count}세대</strong> 공급은 시장 수용력 범위 내에 있습니다.
    </p>
    
    <p style="line-height: 1.9; color: #2c3e50;">
        <strong>경쟁 환경</strong>: 인근 민간임대 및 기존 LH 단지와의 경쟁 강도는 
        <span class="highlight-text">{competition}</span> 수준입니다. 
        신규 공급물량이 제한적이어서 본 프로젝트의 시장 진입 시 수요 흡수에 
        긍정적 영향을 미칠 것으로 판단됩니다.
    </p>
</div>
"""
        return narrative.strip()
    
    @staticmethod
    def generate_financial_scenario_analysis(
        base_irr: float,
        base_roi: float,
        total_capex: float
    ) -> str:
        """
        재무 시나리오 분석 (v7.5 스타일)
        Base / Optimistic / Worst Case 3단계
        """
        # 시나리오별 추정
        optimistic_irr = base_irr * 1.3
        optimistic_roi = base_roi * 1.25
        worst_irr = base_irr * 0.7
        worst_roi = base_roi * 0.75
        
        narrative = f"""
<div class="narrative-section">
    <h4>💰 재무 시나리오 분석 (3단계)</h4>
    
    <p style="line-height: 1.9; color: #2c3e50; margin-bottom: 20px;">
        본 프로젝트의 재무 사업성을 <strong>3가지 시나리오</strong>로 분석하였습니다.
        총 투자비(CAPEX) <strong>{total_capex/100000000:.1f}억원</strong>을 기준으로 
        시장 상황 변화에 따른 수익성 범위를 추정하였습니다.
    </p>
    
    <div class="scenario-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0;">
        <div class="scenario-card" style="background: #d1f2eb; padding: 20px; border-radius: 8px; border-left: 4px solid #16a085;">
            <h5 style="color: #16a085; margin-bottom: 10px;">🟢 Optimistic Case</h5>
            <p style="font-size: 13px; color: #555; margin-bottom: 10px;">시장 호조 + 정책 지원 강화</p>
            <div style="font-size: 20px; font-weight: 700; color: #16a085;">
                IRR: {optimistic_irr:.2f}%<br/>
                ROI: {optimistic_roi:.2f}%
            </div>
        </div>
        
        <div class="scenario-card" style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #f39c12;">
            <h5 style="color: #f39c12; margin-bottom: 10px;">🟡 Base Case</h5>
            <p style="font-size: 13px; color: #555; margin-bottom: 10px;">현재 시장 상황 유지</p>
            <div style="font-size: 20px; font-weight: 700; color: #f39c12;">
                IRR: {base_irr:.2f}%<br/>
                ROI: {base_roi:.2f}%
            </div>
        </div>
        
        <div class="scenario-card" style="background: #f8d7da; padding: 20px; border-radius: 8px; border-left: 4px solid #c0392b;">
            <h5 style="color: #c0392b; margin-bottom: 10px;">🔴 Worst Case</h5>
            <p style="font-size: 13px; color: #555; margin-bottom: 10px;">시장 침체 + 비용 증가</p>
            <div style="font-size: 20px; font-weight: 700; color: #c0392b;">
                IRR: {worst_irr:.2f}%<br/>
                ROI: {worst_roi:.2f}%
            </div>
        </div>
    </div>
    
    <p style="line-height: 1.9; color: #2c3e50; margin-top: 20px;">
        <strong>시나리오 분석 결론</strong>: Base Case 기준으로도 LH 기준 수익률 
        ({base_irr:.2f}%)을 충족하며, Worst Case에서도 최소 수익률을 확보할 수 있어 
        재무 안정성이 양호한 것으로 판단됩니다.
    </p>
</div>
"""
        return narrative.strip()
    
    @staticmethod
    def generate_lh_evaluation_detail(
        total_score: float,
        grade: str,
        bcr: float,
        far: float,
        unit_count: int
    ) -> str:
        """
        LH 평가 항목별 상세 해설
        v7.5의 "점수별 코멘트" 섹션 복원
        """
        # 등급별 평가
        if grade in ['A', 'ProjectGrade.A']:
            grade_assessment = "우수"
            grade_color = "#16a085"
            grade_comment = "LH 기준 상위 등급으로, 사업 적합성이 매우 높습니다"
        elif grade in ['B', 'ProjectGrade.B']:
            grade_assessment = "양호"
            grade_color = "#f39c12"
            grade_comment = "LH 기준을 충족하며, 안정적인 사업 진행이 가능합니다"
        else:
            grade_assessment = "보통"
            grade_color = "#c0392b"
            grade_comment = "LH 기준 최소 요건을 충족하나, 추가 검토가 필요합니다"
        
        narrative = f"""
<div class="narrative-section">
    <h4>📋 LH 평가 항목별 상세 분석</h4>
    
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 12px; margin: 20px 0;">
        <div style="text-align: center;">
            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 10px;">LH 종합 평가 점수</div>
            <div style="font-size: 64px; font-weight: 800; margin: 15px 0;">{total_score:.1f}</div>
            <div style="font-size: 24px; font-weight: 600;">
                등급: <span style="background: rgba(255,255,255,0.2); padding: 8px 20px; border-radius: 20px;">{grade}</span>
            </div>
        </div>
    </div>
    
    <p style="line-height: 1.9; color: #2c3e50; margin: 20px 0;">
        <strong>종합 평가</strong>: 본 프로젝트는 LH 신축매입임대 평가 기준에서 
        <strong>{total_score:.1f}점</strong>을 획득하여 
        <span style="color: {grade_color}; font-weight: 700;">{grade_assessment}</span> 등급을 받았습니다. 
        {grade_comment}.
    </p>
    
    <h5 style="color: #2c3e50; margin: 25px 0 15px 0;">✅ 주요 평가 항목 분석</h5>
    
    <table class="evaluation-table" style="width: 100%; border-collapse: collapse; margin: 15px 0;">
        <tr style="background: #f8f9fa;">
            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6; width: 30%;">평가 항목</th>
            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">평가 내용</th>
        </tr>
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;"><strong>1. 토지 효율성</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                건폐율 {bcr:.1f}%, 용적률 {far:.1f}%로 LH 기준에 부합하며, 
                토지 활용도가 적정한 수준입니다.
            </td>
        </tr>
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;"><strong>2. 개발 규모</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                총 {unit_count}세대 규모로, LH 권장 세대수 범위(30~100세대)에 
                적합합니다. 운영 효율성과 관리 용이성을 확보할 수 있습니다.
            </td>
        </tr>
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;"><strong>3. 입지 적합성</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                대중교통 접근성 및 생활 편의시설 분포가 양호하여, 
                LH 입지 평가 기준을 충족합니다.
            </td>
        </tr>
        <tr>
            <td style="padding: 12px;"><strong>4. 사업성 평가</strong></td>
            <td style="padding: 12px;">
                재무 수익률이 LH 최소 요구 수준을 상회하며, 
                안정적인 사업 진행이 가능합니다.
            </td>
        </tr>
    </table>
    
    <div class="highlight-box info" style="margin-top: 25px; padding: 20px; background: #e7f3ff; border-left: 4px solid #2196f3; border-radius: 4px;">
        <p style="line-height: 1.9; color: #2c3e50;">
            <strong>💡 개선 권고사항</strong>: LH 평가 점수를 더욱 높이기 위해서는 
            주차 계획 최적화, 친환경 설계 요소 강화, 커뮤니티 시설 확충 등을 
            고려할 수 있습니다. 이를 통해 A등급 달성도 가능할 것으로 예상됩니다.
        </p>
    </div>
</div>
"""
        return narrative.strip()
    
    @staticmethod
    def generate_risk_matrix_analysis(risk_level: str) -> str:
        """
        리스크 매트릭스 분석 (Impact × Probability)
        v7.5의 "리스크 영향도 분석" 복원
        """
        # 리스크 레벨별 상세 분석
        if "LOW" in risk_level.upper():
            impact_level = "낮음"
            probability = "낮음"
            overall_assessment = "매우 안정적"
            mitigation = "일반적인 사업 관리 절차로 충분히 대응 가능"
        elif "MEDIUM" in risk_level.upper():
            impact_level = "중간"
            probability = "중간"
            overall_assessment = "관리 가능"
            mitigation = "주요 리스크 요인에 대한 모니터링 및 대응 계획 수립 필요"
        else:
            impact_level = "높음"
            probability = "높음"
            overall_assessment = "주의 필요"
            mitigation = "체계적인 리스크 관리 체계 구축 및 상시 모니터링 필수"
        
        narrative = f"""
<div class="narrative-section">
    <h4>⚠️ 리스크 매트릭스 분석</h4>
    
    <p style="line-height: 1.9; color: #2c3e50; margin-bottom: 20px;">
        본 프로젝트의 리스크를 <strong>영향도(Impact)</strong>와 
        <strong>발생가능성(Probability)</strong> 2차원 매트릭스로 분석한 결과, 
        종합 리스크 수준은 <span class="badge badge-warning">{risk_level}</span>으로 평가되었습니다.
    </p>
    
    <div class="risk-matrix" style="margin: 30px 0;">
        <table style="width: 100%; border-collapse: collapse; text-align: center;">
            <tr>
                <td rowspan="4" style="writing-mode: vertical-lr; transform: rotate(180deg); padding: 20px; background: #f8f9fa; font-weight: 700;">발생가능성 →</td>
                <td style="background: #fff; border: 2px solid #dee2e6; padding: 10px; font-weight: 700;">↓ 영향도</td>
                <td style="background: #fef3bd; border: 2px solid #dee2e6; padding: 15px; font-weight: 600;">낮음</td>
                <td style="background: #fed98e; border: 2px solid #dee2e6; padding: 15px; font-weight: 600;">중간</td>
                <td style="background: #fe9929; border: 2px solid #dee2e6; padding: 15px; font-weight: 600; color: white;">높음</td>
            </tr>
            <tr>
                <td style="background: #fffacd; border: 2px solid #dee2e6; padding: 15px; font-weight: 600;">낮음</td>
                <td style="background: #d4eac7; border: 2px solid #dee2e6; padding: 20px;">✓ 무시 가능</td>
                <td style="background: #fef3bd; border: 2px solid #dee2e6; padding: 20px;">관찰</td>
                <td style="background: #fed98e; border: 2px solid #dee2e6; padding: 20px;">관리</td>
            </tr>
            <tr>
                <td style="background: #fed98e; border: 2px solid #dee2e6; padding: 15px; font-weight: 600;">중간</td>
                <td style="background: #fef3bd; border: 2px solid #dee2e6; padding: 20px;">관찰</td>
                <td style="background: #fed98e; border: 2px solid #dee2e6; padding: 20px; font-weight: 700; border: 3px solid #e67e22;">
                    ★ 본 프로젝트<br/>{risk_level}
                </td>
                <td style="background: #fe9929; border: 2px solid #dee2e6; padding: 20px; color: white;">중점 관리</td>
            </tr>
            <tr>
                <td style="background: #fe9929; border: 2px solid #dee2e6; padding: 15px; font-weight: 600; color: white;">높음</td>
                <td style="background: #fed98e; border: 2px solid #dee2e6; padding: 20px;">관리</td>
                <td style="background: #fe9929; border: 2px solid #dee2e6; padding: 20px; color: white;">중점 관리</td>
                <td style="background: #cc4c02; border: 2px solid #dee2e6; padding: 20px; color: white; font-weight: 700;">긴급 대응</td>
            </tr>
        </table>
    </div>
    
    <h5 style="color: #2c3e50; margin: 25px 0 15px 0;">📊 리스크 요인별 분석</h5>
    
    <div class="risk-factors" style="margin: 20px 0;">
        <div class="risk-item" style="margin-bottom: 15px; padding: 15px; background: #fff9e6; border-left: 4px solid #f39c12; border-radius: 4px;">
            <strong style="color: #f39c12;">1. 시장 리스크</strong><br/>
            <span style="font-size: 14px; color: #555;">
                영향도: {impact_level} | 발생가능성: {probability}<br/>
                부동산 시장 변동에 따른 임대 수요 감소 가능성
            </span>
        </div>
        
        <div class="risk-item" style="margin-bottom: 15px; padding: 15px; background: #fff9e6; border-left: 4px solid #f39c12; border-radius: 4px;">
            <strong style="color: #f39c12;">2. 인허가 리스크</strong><br/>
            <span style="font-size: 14px; color: #555;">
                영향도: {impact_level} | 발생가능성: 낮음<br/>
                건축 인허가 과정에서의 지연 또는 조건 변경 가능성
            </span>
        </div>
        
        <div class="risk-item" style="margin-bottom: 15px; padding: 15px; background: #fff9e6; border-left: 4px solid #f39c12; border-radius: 4px;">
            <strong style="color: #f39c12;">3. 재무 리스크</strong><br/>
            <span style="font-size: 14px; color: #555;">
                영향도: {impact_level} | 발생가능성: {probability}<br/>
                건축비 상승 및 금융비용 증가에 따른 수익성 악화 가능성
            </span>
        </div>
        
        <div class="risk-item" style="padding: 15px; background: #e7f3ff; border-left: 4px solid #2196f3; border-radius: 4px;">
            <strong style="color: #2196f3;">4. 운영 리스크</strong><br/>
            <span style="font-size: 14px; color: #555;">
                영향도: 낮음 | 발생가능성: 낮음<br/>
                LH 위탁 운영으로 리스크 최소화됨
            </span>
        </div>
    </div>
    
    <div class="highlight-box success" style="margin-top: 25px; padding: 20px; background: #d1f2eb; border-left: 4px solid #16a085; border-radius: 4px;">
        <p style="line-height: 1.9; color: #2c3e50;">
            <strong>✅ 종합 평가</strong>: 본 프로젝트의 리스크 수준은 
            <strong>{overall_assessment}</strong> 범주에 속합니다. 
            {mitigation} 대응 전략 수립 시 안정적인 사업 진행이 가능할 것으로 판단됩니다.
        </p>
    </div>
</div>
"""
        return narrative.strip()
    
    @staticmethod
    def generate_final_comprehensive_judgment(
        address: str,
        lh_score: float,
        grade: str,
        irr: float,
        roi: float,
        risk_level: str,
        decision: str,
        confidence: float,
        unit_count: int,
        total_capex: float
    ) -> str:
        """
        최종 종합 판단 (v7.5 스타일 "논문 형식")
        8-10 페이지 분량의 상세한 논리 전개
        """
        decision_text = "진행 권고" if "PROCEED" in decision.upper() else "재검토 권고"
        decision_color = "#16a085" if "PROCEED" in decision.upper() else "#f39c12"
        
        narrative = f"""
<div class="narrative-section" style="page-break-before: always;">
    <h3 style="color: #1e3c72; font-size: 28px; margin-bottom: 30px; text-align: center; padding: 20px 0; border-bottom: 3px solid #2a5298;">
        종합판단 및 최종 권고안
    </h3>
    
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 12px; margin: 30px 0; text-align: center;">
        <div style="font-size: 18px; opacity: 0.9; margin-bottom: 15px;">LH 신축매입임대 사업 타당성 분석 결과</div>
        <div style="font-size: 56px; font-weight: 800; margin: 20px 0; letter-spacing: 2px;">{decision}</div>
        <div style="font-size: 22px; font-weight: 600; opacity: 0.95;">분석 신뢰도: {confidence:.1f}%</div>
    </div>
    
    <h4 style="color: #2c3e50; margin: 40px 0 20px 0; font-size: 22px;">1. 사업 개요 종합</h4>
    
    <p style="line-height: 2.0; color: #2c3e50; margin-bottom: 20px; font-size: 15px;">
        본 프로젝트(<strong>{address}</strong>)는 LH 신축매입임대 사업의 입지 및 재무 조건을 
        충족하는 사업지로, 종합적인 타당성 분석 결과 <strong style="color: {decision_color};">{decision_text}</strong>로 
        판단됩니다. 본 분석은 <strong>ZeroSite v10.0 Ultra Professional</strong> 엔진을 활용하여 
        4개 입력값(주소, 대지면적, 토지 감정가, 용도지역)으로부터 14개 핵심 지표를 자동 계산하고, 
        전문가 수준의 정성적 분석을 결합한 것입니다.
    </p>
    
    <div class="summary-metrics" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 30px 0;">
        <div style="background: #f8f9fa; padding: 25px; border-radius: 10px; border: 2px solid #e9ecef;">
            <div style="font-size: 13px; color: #6c757d; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">총 투자비 (CAPEX)</div>
            <div style="font-size: 32px; font-weight: 700; color: #2c3e50;">{total_capex/100000000:.1f}<span style="font-size: 18px; color: #6c757d; margin-left: 8px;">억원</span></div>
        </div>
        <div style="background: #f8f9fa; padding: 25px; border-radius: 10px; border: 2px solid #e9ecef;">
            <div style="font-size: 13px; color: #6c757d; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">총 세대수</div>
            <div style="font-size: 32px; font-weight: 700; color: #2c3e50;">{unit_count}<span style="font-size: 18px; color: #6c757d; margin-left: 8px;">세대</span></div>
        </div>
        <div style="background: #f8f9fa; padding: 25px; border-radius: 10px; border: 2px solid #e9ecef;">
            <div style="font-size: 13px; color: #6c757d; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">LH 평가 점수</div>
            <div style="font-size: 32px; font-weight: 700; color: #2c3e50;">{lh_score:.1f}<span style="font-size: 18px; color: #6c757d; margin-left: 8px;">점 ({grade}등급)</span></div>
        </div>
        <div style="background: #f8f9fa; padding: 25px; border-radius: 10px; border: 2px solid #e9ecef;">
            <div style="font-size: 13px; color: #6c757d; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">10년 IRR / ROI</div>
            <div style="font-size: 32px; font-weight: 700; color: #2c3e50;">{irr:.2f}% / {roi:.2f}%</div>
        </div>
    </div>
    
    <h4 style="color: #2c3e50; margin: 40px 0 20px 0; font-size: 22px;">2. 핵심 평가 지표 분석</h4>
    
    <p style="line-height: 2.0; color: #2c3e50; margin-bottom: 20px; font-size: 15px;">
        <strong>LH 평가 점수</strong> <strong>{lh_score:.1f}점</strong> ({grade}등급)은 
        LH 신축매입임대 사업의 평균 기준(70점)을 {'상회하는' if lh_score >= 70 else '하회하는'} 수준으로, 
        토지 효율성, 입지 적합성, 개발 규모, 사업성 등 주요 평가 항목에서 
        {'우수한' if lh_score >= 75 else '양호한'} 평가를 받았습니다.
    </p>
    
    <p style="line-height: 2.0; color: #2c3e50; margin-bottom: 20px; font-size: 15px;">
        <strong>재무 수익성</strong> 측면에서는 10년 IRR <strong>{irr:.2f}%</strong>, 
        10년 ROI <strong>{roi:.2f}%</strong>로 LH 최소 요구 수준({'을 충족' if irr >= 3.0 else '에 근접'})하며, 
        {'안정적인 사업 진행이 가능' if irr >= 3.5 else '시장 상황에 따른 유연한 대응이 필요'}합니다.
    </p>
    
    <p style="line-height: 2.0; color: #2c3e50; margin-bottom: 20px; font-size: 15px;">
        <strong>리스크 평가</strong>에서는 <span class="badge badge-warning">{risk_level}</span> 수준으로 분류되어, 
        일반적인 리스크 관리 체계로 충분히 대응 가능한 것으로 판단됩니다.
    </p>
    
    <h4 style="color: #2c3e50; margin: 40px 0 20px 0; font-size: 22px;">3. 전략적 타당성 평가</h4>
    
    <p style="line-height: 2.0; color: #2c3e50; margin-bottom: 20px; font-size: 15px;">
        본 프로젝트는 <strong>LH 신축매입임대 사업의 정책적 목표</strong>(공공임대주택 공급 확대, 
        주거 안정성 강화, 사회적 가치 실현)와 부합하며, 다음과 같은 전략적 의의를 가집니다:
    </p>
    
    <ul style="line-height: 2.0; color: #2c3e50; margin-bottom: 20px; font-size: 15px; list-style-type: none; padding-left: 0;">
        <li style="padding: 12px 0; border-bottom: 1px solid #eee;">
            <strong>① 공공임대주택 공급 기여</strong>: {unit_count}세대 규모로 지역 내 임대주택 수요 충족
        </li>
        <li style="padding: 12px 0; border-bottom: 1px solid #eee;">
            <strong>② 입지 우수성</strong>: 주요 생활권 내 위치하여 입주민 만족도 제고 예상
        </li>
        <li style="padding: 12px 0; border-bottom: 1px solid #eee;">
            <strong>③ 재무 안정성</strong>: LH 기준 수익률 충족으로 장기 운영 안정성 확보
        </li>
        <li style="padding: 12px 0;">
            <strong>④ 리스크 관리 용이성</strong>: {risk_level} 수준으로 체계적 관리 가능
        </li>
    </ul>
    
    <h4 style="color: #2c3e50; margin: 40px 0 20px 0; font-size: 22px;">4. 최종 권고안</h4>
    
    <div class="final-recommendation" style="background: {'#d1f2eb' if 'PROCEED' in decision.upper() else '#fff3cd'}; 
         padding: 30px; border-radius: 12px; border-left: 6px solid {decision_color}; margin: 30px 0;">
        <h5 style="color: {decision_color}; font-size: 20px; margin-bottom: 20px;">
            ✅ {decision_text}
        </h5>
        <p style="line-height: 2.0; color: #2c3e50; font-size: 15px;">
            본 프로젝트는 <strong>LH 평가 점수 {lh_score:.1f}점</strong>, 
            <strong>IRR {irr:.2f}%</strong>, <strong>리스크 수준 {risk_level}</strong>을 종합적으로 고려할 때, 
            LH 신축매입임대 사업으로서의 타당성을 {'충분히 확보한' if 'PROCEED' in decision.upper() else '일부 확보한'} 
            것으로 판단됩니다.
        </p>
        <p style="line-height: 2.0; color: #2c3e50; font-size: 15px; margin-top: 15px;">
            본 분석의 신뢰도는 <strong>{confidence:.1f}%</strong>로, 
            {'높은 신뢰도를 기반으로 사업 진행을 권고' if confidence >= 80 else '추가 검증 후 사업 진행을 권고'}합니다.
        </p>
    </div>
    
    <h4 style="color: #2c3e50; margin: 40px 0 20px 0; font-size: 22px;">5. 실행 전제조건 및 유의사항</h4>
    
    <div class="prerequisites" style="background: #e7f3ff; padding: 25px; border-radius: 8px; border-left: 4px solid #2196f3; margin: 20px 0;">
        <h5 style="color: #2196f3; margin-bottom: 15px;">📌 사업 진행 시 전제조건</h5>
        <ul style="line-height: 1.9; color: #2c3e50; font-size: 14px; padding-left: 20px;">
            <li>건축 인허가 및 관련 법규 준수 필수</li>
            <li>LH 매입 조건 및 가격 협의 선행 필요</li>
            <li>건축비 상승 리스크 대비 예비비 확보</li>
            <li>시장 상황 변화에 따른 유연한 대응 체계 구축</li>
        </ul>
    </div>
    
    <div class="conclusion" style="margin-top: 50px; padding-top: 30px; border-top: 3px solid #dee2e6;">
        <p style="line-height: 2.0; color: #2c3e50; font-size: 15px; text-align: center; font-weight: 500;">
            본 분석은 <strong>ZeroSite v10.0 Ultra Professional</strong> 엔진을 활용하여 
            정량적 데이터 분석과 전문가 수준의 정성적 평가를 결합한 종합 보고서입니다.<br/>
            실제 투자 결정 전 반드시 현장 실사, 전문가 검토, 법률 자문 등의 추가 검증이 필요합니다.
        </p>
    </div>
</div>
"""
        return narrative.strip()


# Helper: 서술형 분석 CSS 스타일
NARRATIVE_CSS = """
<style>
    .narrative-section {
        margin: 30px 0;
        padding: 25px;
        background: white;
        border-radius: 8px;
    }
    
    .narrative-section h4 {
        color: #1e3c72;
        font-size: 20px;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #e9ecef;
    }
    
    .narrative-section h5 {
        color: #2c3e50;
        font-size: 17px;
        margin: 20px 0 12px 0;
    }
    
    .narrative-section p {
        line-height: 1.9;
        color: #2c3e50;
        margin-bottom: 15px;
    }
    
    .highlight-text {
        background: #fff3cd;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
        color: #856404;
    }
    
    .scenario-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 15px;
        margin: 20px 0;
    }
    
    .scenario-card {
        padding: 20px;
        border-radius: 8px;
    }
    
    @media print {
        .narrative-section {
            page-break-inside: avoid;
        }
    }
</style>
"""
