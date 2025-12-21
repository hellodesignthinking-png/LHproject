"""
ZeroSite v4.0 Final Report HTML Renderer
========================================

목적: 6종 최종보고서 통합 HTML 템플릿 렌더링

핵심 원칙:
1. 단일 템플릿 + 조건 분기 (report_type별 섹션 선택)
2. 방어적 렌더링 (None → "N/A (검증 필요)", 숫자는 단위 필수)
3. 데이터 부족 시 경고 박스 출력
4. QA Status 푸터 필수
5. Pretendard 폰트, Accent Blue (#3B82F6) 제목

Version: 1.0
Date: 2025-12-21
"""

from typing import Dict, Any, Optional
from datetime import datetime


# ============================================================================
# 공통 스타일 & 레이아웃
# ============================================================================

def get_common_styles() -> str:
    """공통 CSS 스타일 (Pretendard 폰트, 컬러 스킴)"""
    return """
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #374151;
            background: #F9FAFB;
            padding: 40px 20px;
        }
        
        .report-container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        
        /* 헤더 */
        .report-header {
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .report-title {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 12px;
        }
        
        .report-subtitle {
            font-size: 16px;
            opacity: 0.9;
            font-weight: 400;
        }
        
        .report-meta {
            margin-top: 20px;
            font-size: 13px;
            opacity: 0.8;
        }
        
        /* 컨텐츠 영역 */
        .report-content {
            padding: 40px;
        }
        
        /* 섹션 */
        .section {
            margin-bottom: 40px;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 700;
            color: #3B82F6;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3B82F6;
        }
        
        .section-subtitle {
            font-size: 15px;
            font-weight: 600;
            color: #1F2937;
            margin: 20px 0 12px 0;
        }
        
        /* 데이터 카드 */
        .data-card {
            background: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 16px;
        }
        
        .data-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #E5E7EB;
        }
        
        .data-row:last-child {
            border-bottom: none;
        }
        
        .data-label {
            font-weight: 600;
            color: #6B7280;
            font-size: 13px;
        }
        
        .data-value {
            font-weight: 700;
            color: #1F2937;
            font-size: 15px;
            text-align: right;
        }
        
        .data-value.na {
            color: #9CA3AF;
            font-style: italic;
        }
        
        /* 경고 박스 */
        .warning-box {
            background: #FEF3C7;
            border: 2px solid #F59E0B;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 24px;
            display: flex;
            align-items: flex-start;
        }
        
        .warning-icon {
            font-size: 20px;
            margin-right: 12px;
        }
        
        .warning-text {
            font-size: 14px;
            color: #92400E;
            line-height: 1.5;
        }
        
        /* 의사결정 카드 (Executive Summary) */
        .decision-card {
            background: linear-gradient(135deg, #10B981 0%, #059669 100%);
            color: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .decision-card.conditional {
            background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        }
        
        .decision-card.negative {
            background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        }
        
        .decision-title {
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 16px;
        }
        
        .decision-details {
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
        }
        
        .decision-metric {
            text-align: center;
        }
        
        .decision-metric-label {
            font-size: 12px;
            opacity: 0.8;
            margin-bottom: 8px;
        }
        
        .decision-metric-value {
            font-size: 24px;
            font-weight: 700;
        }
        
        /* 리스트 */
        .report-list {
            list-style: none;
            padding-left: 0;
        }
        
        .report-list li {
            padding: 10px 0;
            padding-left: 24px;
            position: relative;
        }
        
        .report-list li:before {
            content: "•";
            position: absolute;
            left: 8px;
            color: #3B82F6;
            font-weight: bold;
        }
        
        /* 체크리스트 (Quick Check용) */
        .checklist-item {
            display: flex;
            align-items: center;
            padding: 12px;
            background: #F9FAFB;
            border-radius: 6px;
            margin-bottom: 10px;
        }
        
        .checklist-icon {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 16px;
            flex-shrink: 0;
        }
        
        .checklist-icon.ok {
            background: #10B981;
            color: white;
        }
        
        .checklist-icon.check {
            background: #F59E0B;
            color: white;
        }
        
        .checklist-icon.pending {
            background: #9CA3AF;
            color: white;
        }
        
        .checklist-content {
            flex: 1;
        }
        
        .checklist-title {
            font-weight: 600;
            color: #1F2937;
            margin-bottom: 4px;
        }
        
        .checklist-note {
            font-size: 13px;
            color: #6B7280;
        }
        
        /* 슬라이드 (Presentation용) */
        .slide {
            page-break-inside: avoid;
            margin-bottom: 40px;
            border: 2px solid #E5E7EB;
            border-radius: 12px;
            padding: 30px;
            background: white;
        }
        
        .slide-number {
            font-size: 12px;
            color: #9CA3AF;
            margin-bottom: 16px;
        }
        
        .slide-title {
            font-size: 24px;
            font-weight: 700;
            color: #3B82F6;
            margin-bottom: 24px;
        }
        
        /* 푸터 (QA Status) */
        .report-footer {
            background: #F3F4F6;
            padding: 30px 40px;
            border-top: 2px solid #E5E7EB;
        }
        
        .qa-status-title {
            font-size: 15px;
            font-weight: 700;
            color: #6B7280;
            margin-bottom: 16px;
        }
        
        .qa-status-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }
        
        .qa-status-item {
            background: white;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }
        
        .qa-status-label {
            font-size: 12px;
            color: #6B7280;
            margin-bottom: 8px;
        }
        
        .qa-status-value {
            font-size: 14px;
            font-weight: 600;
        }
        
        /* 인쇄용 */
        @media print {
            body {
                background: white;
                padding: 0;
            }
            
            .report-container {
                box-shadow: none;
            }
            
            .section {
                page-break-inside: avoid;
            }
        }
    </style>
    """


def format_currency(value: Optional[int]) -> str:
    """원화 포맷팅 (방어적 렌더링)"""
    if value is None:
        return '<span class="data-value na">N/A (검증 필요)</span>'
    return f'<span class="data-value">{value:,}원</span>'


def format_percentage(value: Optional[float]) -> str:
    """퍼센트 포맷팅 (방어적 렌더링)"""
    if value is None:
        return '<span class="data-value na">N/A (검증 필요)</span>'
    return f'<span class="data-value">{value}%</span>'


def format_units(value: Optional[int]) -> str:
    """세대수 포맷팅 (방어적 렌더링)"""
    if value is None:
        return '<span class="data-value na">N/A (검증 필요)</span>'
    return f'<span class="data-value">{value}세대</span>'


def format_generic(value: Optional[Any], suffix: str = "") -> str:
    """일반 값 포맷팅 (방어적 렌더링)"""
    if value is None or value == "":
        return '<span class="data-value na">N/A (검증 필요)</span>'
    return f'<span class="data-value">{value}{suffix}</span>'


def render_data_shortage_warning(missing_modules: list) -> str:
    """데이터 부족 경고 박스"""
    if not missing_modules:
        return ""
    
    module_names = {
        "M2": "토지가치 평가",
        "M3": "주택유형 분석",
        "M4": "개발규모 산정",
        "M5": "사업성 분석",
        "M6": "LH 승인 예측"
    }
    
    missing_text = ", ".join([module_names.get(m, m) for m in missing_modules])
    
    return f"""
    <div class="warning-box">
        <div class="warning-icon">⚠️</div>
        <div class="warning-text">
            <strong>데이터 부족으로 일부 항목은 참고용입니다</strong><br>
            누락된 분석: {missing_text}<br>
            완전한 보고서를 위해 모든 분석을 완료해주세요.
        </div>
    </div>
    """


def render_qa_status_footer(qa_status: Dict[str, str]) -> str:
    """QA Status 푸터"""
    return f"""
    <div class="report-footer">
        <div class="qa-status-title">📊 보고서 품질 상태 (QA Status)</div>
        <div class="qa-status-grid">
            <div class="qa-status-item">
                <div class="qa-status-label">Data Binding</div>
                <div class="qa-status-value">{qa_status.get('data_binding', 'N/A')}</div>
            </div>
            <div class="qa-status-item">
                <div class="qa-status-label">Content Completeness</div>
                <div class="qa-status-value">{qa_status.get('content_completeness', 'N/A')}</div>
            </div>
            <div class="qa-status-item">
                <div class="qa-status-label">Ready for Submission</div>
                <div class="qa-status-value">{qa_status.get('ready_for_submission', 'N/A')}</div>
            </div>
        </div>
    </div>
    """


# ============================================================================
# 보고서별 HTML 렌더링
# ============================================================================

def render_all_in_one_report(data: Dict[str, Any]) -> str:
    """1. 종합 최종보고서"""
    
    # 데이터 부족 체크
    missing = []
    if data.get("land_value_krw") is None:
        missing.append("M2")
    if data.get("recommended_housing_type") is None:
        missing.append("M3")
    if data.get("legal_units") is None:
        missing.append("M4")
    if data.get("npv_krw") is None:
        missing.append("M5")
    if data.get("final_decision") == "검토 필요":
        missing.append("M6")
    
    warning_html = render_data_shortage_warning(missing)
    
    # Executive Summary 카드
    decision_class = ""
    if "추진 권장" in data.get("final_decision", ""):
        decision_class = ""
    elif "조건부" in data.get("final_decision", ""):
        decision_class = "conditional"
    else:
        decision_class = "negative"
    
    executive_card = f"""
    <div class="decision-card {decision_class}">
        <div class="decision-title">{data.get('final_decision', '검토 필요')}</div>
        <div class="decision-details">
            <div class="decision-metric">
                <div class="decision-metric-label">승인 가능성</div>
                <div class="decision-metric-value">
                    {data.get('approval_probability_pct', 'N/A')}{"%" if data.get('approval_probability_pct') else ""}
                </div>
            </div>
            <div class="decision-metric">
                <div class="decision-metric-label">종합 등급</div>
                <div class="decision-metric-value">{data.get('grade', 'N/A')}</div>
            </div>
        </div>
    </div>
    """
    
    # 주요 리스크
    risks_html = ""
    for risk in data.get("key_risks", []):
        risks_html += f"<li>{risk}</li>"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>종합 최종보고서 - ZeroSite</title>
        {get_common_styles()}
    </head>
    <body>
        <div class="report-container">
            <div class="report-header">
                <div class="report-title">종합 최종보고서</div>
                <div class="report-subtitle">LH 공공임대 토지 종합 분석</div>
                <div class="report-meta">
                    생성일: {data.get('generated_at', 'N/A')}<br>
                    Context ID: {data.get('context_id', 'N/A')}
                </div>
            </div>
            
            <div class="report-content">
                {warning_html}
                
                <!-- 1. 최종 판정 -->
                <div class="section">
                    <div class="section-title">1. 최종 판정 (Executive Summary)</div>
                    {executive_card}
                    
                    <div class="section-subtitle">주요 리스크 요인</div>
                    <ul class="report-list">
                        {risks_html}
                    </ul>
                </div>
                
                <!-- 2. 토지 가치 평가 -->
                <div class="section">
                    <div class="section-title">2. 토지 가치 평가</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">총 토지 가치</span>
                            {format_currency(data.get('land_value_krw'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">평당 가격</span>
                            {format_currency(data.get('land_value_per_pyeong_krw'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">평가 신뢰도</span>
                            {format_percentage(data.get('land_confidence_pct'))}
                        </div>
                    </div>
                </div>
                
                <!-- 3. 개발 규모 -->
                <div class="section">
                    <div class="section-title">3. 개발 규모</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">법정 용적률 기준</span>
                            {format_units(data.get('legal_units'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">인센티브 용적률 기준</span>
                            {format_units(data.get('incentive_units'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">주차 대수</span>
                            {format_generic(data.get('parking_spaces'), '대')}
                        </div>
                    </div>
                </div>
                
                <!-- 4. 주택 유형 -->
                <div class="section">
                    <div class="section-title">4. 주택 유형 (LH 선호유형 분석)</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">추천 유형</span>
                            {format_generic(data.get('recommended_housing_type'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">적합도 점수</span>
                            {format_generic(data.get('housing_type_score'), '점')}
                        </div>
                    </div>
                </div>
                
                <!-- 5. 사업성 지표 -->
                <div class="section">
                    <div class="section-title">5. 사업성 지표</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">순현재가치 (NPV)</span>
                            {format_currency(data.get('npv_krw'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">내부수익률 (IRR)</span>
                            {format_percentage(data.get('irr_pct'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">투자수익률 (ROI)</span>
                            {format_percentage(data.get('roi_pct'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">사업성 등급</span>
                            {format_generic(data.get('financial_grade'))}
                        </div>
                    </div>
                </div>
            </div>
            
            {render_qa_status_footer(data.get('qa_status', {}))}
        </div>
    </body>
    </html>
    """
    
    return html


def render_landowner_summary(data: Dict[str, Any]) -> str:
    """2. 토지주 제출용 요약보고서"""
    
    # 다음 단계 리스트
    next_steps_html = ""
    for step in data.get("next_steps", []):
        next_steps_html += f"<li>{step}</li>"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>토지주 제출용 요약보고서 - ZeroSite</title>
        {get_common_styles()}
    </head>
    <body>
        <div class="report-container">
            <div class="report-header">
                <div class="report-title">토지주 제출용 요약보고서</div>
                <div class="report-subtitle">쉽고 명확한 분석 요약</div>
                <div class="report-meta">
                    생성일: {data.get('generated_at', 'N/A')}<br>
                    Context ID: {data.get('context_id', 'N/A')}
                </div>
            </div>
            
            <div class="report-content">
                <!-- 한 줄 요약 -->
                <div class="section">
                    <div class="decision-card">
                        <div class="decision-title">{data.get('summary_sentence', '분석 중입니다')}</div>
                    </div>
                </div>
                
                <!-- 토지 가치 -->
                <div class="section">
                    <div class="section-title">💰 토지 가치</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">총 토지 가치</span>
                            {format_currency(data.get('land_value_krw'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">평당 가격</span>
                            {format_currency(data.get('land_value_per_pyeong_krw'))}
                        </div>
                    </div>
                </div>
                
                <!-- 개발 가능 규모 -->
                <div class="section">
                    <div class="section-title">🏘️ 개발 가능 규모</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">건축 가능 세대수</span>
                            {format_units(data.get('buildable_units'))}
                        </div>
                    </div>
                </div>
                
                <!-- 예상 수익성 -->
                <div class="section">
                    <div class="section-title">📊 예상 수익성</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">수익성 평가</span>
                            {format_generic(data.get('expected_profit'))}
                        </div>
                    </div>
                </div>
                
                <!-- 다음 단계 -->
                <div class="section">
                    <div class="section-title">✅ 다음 단계</div>
                    <ul class="report-list">
                        {next_steps_html}
                    </ul>
                </div>
            </div>
            
            {render_qa_status_footer(data.get('qa_status', {}))}
        </div>
    </body>
    </html>
    """
    
    return html


def render_lh_technical(data: Dict[str, Any]) -> str:
    """3. LH 제출용 기술검증 보고서"""
    
    land_suit = data.get('land_suitability', {})
    dev_scale = data.get('development_scale', {})
    housing_fit = data.get('housing_type_fit', {})
    financial = data.get('financial_viability', {})
    
    # 승인 장애 요인
    barriers_html = ""
    for barrier in data.get("approval_barriers", []):
        barriers_html += f"<li>{barrier}</li>"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LH 제출용 기술검증 보고서 - ZeroSite</title>
        {get_common_styles()}
    </head>
    <body>
        <div class="report-container">
            <div class="report-header">
                <div class="report-title">LH 제출용 기술검증 보고서</div>
                <div class="report-subtitle">LH 공모 심사 기술 자료</div>
                <div class="report-meta">
                    생성일: {data.get('generated_at', 'N/A')}<br>
                    Context ID: {data.get('context_id', 'N/A')}
                </div>
            </div>
            
            <div class="report-content">
                <!-- 종합 평가 -->
                <div class="section">
                    <div class="section-title">1. 종합 평가</div>
                    <div class="decision-card">
                        <div class="decision-title">{data.get('overall_assessment', '검토 중')}</div>
                        <div class="decision-details">
                            <div class="decision-metric">
                                <div class="decision-metric-label">LH 승인 가능성</div>
                                <div class="decision-metric-value">
                                    {data.get('approval_probability_pct', 'N/A')}{"%" if data.get('approval_probability_pct') else ""}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 토지 적합성 -->
                <div class="section">
                    <div class="section-title">2. 토지 적합성</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">총 토지 가치</span>
                            {format_currency(land_suit.get('total_value_krw'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">평당 가격</span>
                            {format_currency(land_suit.get('per_pyeong_krw'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">평가 신뢰도</span>
                            {format_percentage(land_suit.get('confidence_pct'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">거래사례 건수</span>
                            {format_generic(land_suit.get('transaction_cases'), '건')}
                        </div>
                    </div>
                </div>
                
                <!-- 개발 규모 검증 -->
                <div class="section">
                    <div class="section-title">3. 개발 규모 검증</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">법정 용적률 기준</span>
                            {format_units(dev_scale.get('legal_units'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">인센티브 용적률 기준</span>
                            {format_units(dev_scale.get('incentive_units'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">주차 대안 A</span>
                            {format_generic(dev_scale.get('parking_plan_a'), '대')}
                        </div>
                        <div class="data-row">
                            <span class="data-label">주차 대안 B</span>
                            {format_generic(dev_scale.get('parking_plan_b'), '대')}
                        </div>
                    </div>
                </div>
                
                <!-- 주택 유형 적합성 -->
                <div class="section">
                    <div class="section-title">4. 주택 유형 적합성</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">추천 유형</span>
                            {format_generic(housing_fit.get('recommended_type'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">적합도 점수</span>
                            {format_generic(housing_fit.get('score'), '점')}
                        </div>
                        <div class="data-row">
                            <span class="data-label">신뢰도</span>
                            {format_percentage(housing_fit.get('confidence_pct'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">차선책</span>
                            {format_generic(housing_fit.get('alternative'))}
                        </div>
                    </div>
                </div>
                
                <!-- 재무 타당성 -->
                <div class="section">
                    <div class="section-title">5. 재무 타당성</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">순현재가치 (NPV)</span>
                            {format_currency(financial.get('npv_krw'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">내부수익률 (IRR)</span>
                            {format_percentage(financial.get('irr_pct'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">투자수익률 (ROI)</span>
                            {format_percentage(financial.get('roi_pct'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">사업성 등급</span>
                            {format_generic(financial.get('grade'))}
                        </div>
                    </div>
                </div>
                
                <!-- 승인 장애 요인 -->
                <div class="section">
                    <div class="section-title">6. 승인 장애 요인</div>
                    <ul class="report-list">
                        {barriers_html if barriers_html else '<li>특이사항 없음</li>'}
                    </ul>
                </div>
            </div>
            
            {render_qa_status_footer(data.get('qa_status', {}))}
        </div>
    </body>
    </html>
    """
    
    return html


def render_financial_feasibility(data: Dict[str, Any]) -> str:
    """4. 사업성·투자 검토 보고서"""
    
    project_scale = data.get('project_scale', {})
    revenue_struct = data.get('revenue_structure', {})
    
    # 리스크 요인
    risks_html = ""
    for risk in data.get("risk_factors", []):
        risks_html += f"<li>{risk}</li>"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>사업성·투자 검토 보고서 - ZeroSite</title>
        {get_common_styles()}
    </head>
    <body>
        <div class="report-container">
            <div class="report-header">
                <div class="report-title">사업성·투자 검토 보고서</div>
                <div class="report-subtitle">재무 타당성 및 투자 판단 자료</div>
                <div class="report-meta">
                    생성일: {data.get('generated_at', 'N/A')}<br>
                    Context ID: {data.get('context_id', 'N/A')}
                </div>
            </div>
            
            <div class="report-content">
                <!-- 투자 의견 -->
                <div class="section">
                    <div class="section-title">1. 투자 의견</div>
                    <div class="decision-card">
                        <div class="decision-title">{data.get('investment_opinion', '분석 중')}</div>
                    </div>
                </div>
                
                <!-- 핵심 재무 지표 -->
                <div class="section">
                    <div class="section-title">2. 핵심 재무 지표</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">순현재가치 (NPV)</span>
                            {format_currency(data.get('npv_krw'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">내부수익률 (IRR)</span>
                            {format_percentage(data.get('irr_pct'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">투자수익률 (ROI)</span>
                            {format_percentage(data.get('roi_pct'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">회수 기간</span>
                            {format_generic(data.get('payback_period_years'), '년')}
                        </div>
                    </div>
                </div>
                
                <!-- 사업 규모 -->
                <div class="section">
                    <div class="section-title">3. 사업 규모</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">총 세대수</span>
                            {format_units(project_scale.get('total_units'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">토지 취득비</span>
                            {format_currency(project_scale.get('land_cost_krw'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">예상 총 매출</span>
                            {format_currency(project_scale.get('estimated_revenue_krw'))}
                        </div>
                    </div>
                </div>
                
                <!-- 수익 구조 -->
                <div class="section">
                    <div class="section-title">4. 수익 구조</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">주택 유형</span>
                            {format_generic(revenue_struct.get('housing_type'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">임대 수익 전망</span>
                            {format_generic(revenue_struct.get('rental_income_projection'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">분양 가격 전망</span>
                            {format_generic(revenue_struct.get('sales_price_projection'))}
                        </div>
                    </div>
                </div>
                
                <!-- 리스크 분석 -->
                <div class="section">
                    <div class="section-title">5. 리스크 분석</div>
                    <ul class="report-list">
                        {risks_html}
                    </ul>
                </div>
            </div>
            
            {render_qa_status_footer(data.get('qa_status', {}))}
        </div>
    </body>
    </html>
    """
    
    return html


def render_quick_check(data: Dict[str, Any]) -> str:
    """5. 사전 검토 리포트 (Quick Check)"""
    
    # Traffic Light 신호
    signal = data.get('overall_signal', 'YELLOW')
    signal_color = {
        'GREEN': '#10B981',
        'YELLOW': '#F59E0B',
        'RED': '#EF4444'
    }.get(signal, '#9CA3AF')
    
    signal_icon = {
        'GREEN': '✅',
        'YELLOW': '⚠️',
        'RED': '❌'
    }.get(signal, '❓')
    
    # 체크리스트
    checklist_html = ""
    for item in data.get('checklist', []):
        status = item.get('status', 'PENDING')
        icon_class = status.lower()
        icon_symbol = {
            'OK': '✓',
            'CHECK': '!',
            'PENDING': '?'
        }.get(status, '?')
        
        checklist_html += f"""
        <div class="checklist-item">
            <div class="checklist-icon {icon_class}">{icon_symbol}</div>
            <div class="checklist-content">
                <div class="checklist-title">{item.get('item', 'N/A')}</div>
                <div class="checklist-note">{item.get('note', 'N/A')}</div>
            </div>
        </div>
        """
    
    # 즉시 주의 사항
    concerns_html = ""
    for concern in data.get('immediate_concerns', []):
        concerns_html += f"<li>{concern}</li>"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>사전 검토 리포트 - ZeroSite</title>
        {get_common_styles()}
    </head>
    <body>
        <div class="report-container">
            <div class="report-header">
                <div class="report-title">사전 검토 리포트 (Quick Check)</div>
                <div class="report-subtitle">5분 내 GO/NO-GO 판단</div>
                <div class="report-meta">
                    생성일: {data.get('generated_at', 'N/A')}<br>
                    Context ID: {data.get('context_id', 'N/A')}
                </div>
            </div>
            
            <div class="report-content">
                <!-- 종합 신호 -->
                <div class="section">
                    <div class="decision-card" style="background: {signal_color};">
                        <div class="decision-title">{signal_icon} {data.get('signal_text', '검토 필요')}</div>
                    </div>
                </div>
                
                <!-- 체크리스트 -->
                <div class="section">
                    <div class="section-title">✓ 체크리스트</div>
                    {checklist_html}
                </div>
                
                <!-- 즉시 주의 사항 -->
                <div class="section">
                    <div class="section-title">⚠️ 즉시 주의 사항</div>
                    <ul class="report-list">
                        {concerns_html}
                    </ul>
                </div>
            </div>
            
            {render_qa_status_footer(data.get('qa_status', {}))}
        </div>
    </body>
    </html>
    """
    
    return html


def render_presentation_report(data: Dict[str, Any]) -> str:
    """6. 설명용 프레젠테이션 보고서"""
    
    # 슬라이드 렌더링
    slides_html = ""
    for slide in data.get('slides', []):
        slide_type = slide.get('type', 'data')
        slide_content = slide.get('content', {})
        
        if slide_type == 'cover':
            content_html = f"""
            <div style="text-align: center; padding: 40px;">
                <div style="font-size: 20px; color: #6B7280; margin-bottom: 20px;">
                    {slide_content.get('subtitle', 'ZeroSite Expert Analysis')}
                </div>
                <div style="font-size: 16px; color: #9CA3AF;">
                    {slide_content.get('date', 'N/A')}<br>
                    Context ID: {slide_content.get('context_id', 'N/A')}
                </div>
            </div>
            """
        elif slide_type == 'summary':
            content_html = f"""
            <div class="data-card">
                <div class="data-row">
                    <span class="data-label">최종 판정</span>
                    <span class="data-value">{slide_content.get('decision', 'N/A')}</span>
                </div>
                <div class="data-row">
                    <span class="data-label">승인 가능성</span>
                    <span class="data-value">{slide_content.get('approval_probability', 'N/A')}</span>
                </div>
                <div class="data-row">
                    <span class="data-label">종합 등급</span>
                    <span class="data-value">{slide_content.get('grade', 'N/A')}</span>
                </div>
            </div>
            """
        elif slide_type == 'data':
            content_html = '<div class="data-card">'
            for key, value in slide_content.items():
                label = key.replace('_', ' ').title()
                content_html += f"""
                <div class="data-row">
                    <span class="data-label">{label}</span>
                    <span class="data-value">{value}</span>
                </div>
                """
            content_html += '</div>'
        elif slide_type == 'financial':
            content_html = f"""
            <div class="data-card">
                <div class="data-row">
                    <span class="data-label">순현재가치 (NPV)</span>
                    <span class="data-value">{slide_content.get('npv', 'N/A')}</span>
                </div>
                <div class="data-row">
                    <span class="data-label">내부수익률 (IRR)</span>
                    <span class="data-value">{slide_content.get('irr', 'N/A')}</span>
                </div>
                <div class="data-row">
                    <span class="data-label">투자수익률 (ROI)</span>
                    <span class="data-value">{slide_content.get('roi', 'N/A')}</span>
                </div>
                <div class="data-row">
                    <span class="data-label">사업성 등급</span>
                    <span class="data-value">{slide_content.get('grade', 'N/A')}</span>
                </div>
            </div>
            """
        elif slide_type == 'risk':
            risks = slide_content.get('risks', [])
            risk_items = "".join([f"<li>{r}</li>" for r in risks])
            content_html = f'<ul class="report-list">{risk_items}</ul>'
        elif slide_type == 'action':
            actions = slide_content.get('actions', [])
            action_items = "".join([f"<li>{a}</li>" for a in actions])
            content_html = f'<ul class="report-list">{action_items}</ul>'
        else:
            content_html = '<p>Content not available</p>'
        
        slides_html += f"""
        <div class="slide">
            <div class="slide-number">Slide {slide.get('slide_number', 'N/A')}</div>
            <div class="slide-title">{slide.get('title', 'Untitled')}</div>
            {content_html}
        </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>설명용 프레젠테이션 보고서 - ZeroSite</title>
        {get_common_styles()}
    </head>
    <body>
        <div class="report-container">
            <div class="report-header">
                <div class="report-title">설명용 프레젠테이션 보고서</div>
                <div class="report-subtitle">시각적 요약 및 회의 자료</div>
                <div class="report-meta">
                    생성일: {data.get('generated_at', 'N/A')}<br>
                    Context ID: {data.get('context_id', 'N/A')}<br>
                    총 슬라이드: {data.get('total_slides', 0)}장
                </div>
            </div>
            
            <div class="report-content">
                {slides_html}
            </div>
            
            {render_qa_status_footer(data.get('qa_status', {}))}
        </div>
    </body>
    </html>
    """
    
    return html


# ============================================================================
# 메인 엔트리 포인트
# ============================================================================

def render_final_report_html(report_type: str, data: Dict[str, Any]) -> str:
    """
    최종보고서 HTML 렌더링 (메인 진입점)
    
    Args:
        report_type: 보고서 유형
        data: assemble_final_report() 결과
    
    Returns:
        완전한 HTML 문자열
    """
    
    renderers = {
        "all_in_one": render_all_in_one_report,
        "landowner_summary": render_landowner_summary,
        "lh_technical": render_lh_technical,
        "financial_feasibility": render_financial_feasibility,
        "quick_check": render_quick_check,
        "presentation": render_presentation_report
    }
    
    renderer = renderers.get(report_type)
    if not renderer:
        raise ValueError(f"Unknown report type: {report_type}")
    
    return renderer(data)
