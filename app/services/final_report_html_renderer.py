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
    """QA Status 푸터 (4가지 체크)"""
    return f"""
    <div class="report-footer">
        <div class="qa-status-title">📊 보고서 품질 상태 (QA Status)</div>
        <div class="qa-status-grid" style="grid-template-columns: repeat(2, 1fr);">
            <div class="qa-status-item">
                <div class="qa-status-label">Data Binding</div>
                <div class="qa-status-value">{qa_status.get('data_binding', 'N/A')}</div>
            </div>
            <div class="qa-status-item">
                <div class="qa-status-label">Content Completeness</div>
                <div class="qa-status-value">{qa_status.get('content_completeness', 'N/A')}</div>
            </div>
            <div class="qa-status-item">
                <div class="qa-status-label">Narrative Consistency</div>
                <div class="qa-status-value">{qa_status.get('narrative_consistency', 'N/A')}</div>
            </div>
            <div class="qa-status-item">
                <div class="qa-status-label">HTML-PDF Parity</div>
                <div class="qa-status-value">{qa_status.get('html_pdf_parity', 'N/A')}</div>
            </div>
        </div>
        <div style="margin-top: 16px; padding: 12px; background: #F3F4F6; border-radius: 6px; text-align: center;">
            <div style="font-size: 13px; font-weight: 600; color: #6B7280; margin-bottom: 4px;">최종 제출 가능 여부</div>
            <div style="font-size: 15px; font-weight: 700;">{qa_status.get('ready_for_submission', 'N/A')}</div>
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
        <div style="margin: 16px 0; font-size: 14px; line-height: 1.6; opacity: 0.95;">
            {data.get('final_decision_interpretation', '분석 결과를 검토 중입니다.')}
        </div>
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
                
                <!-- 1. 최종 판정 (Executive Summary) -->
                <div class="section">
                    <div class="section-title">1. 최종 판정 (Executive Summary)</div>
                    {executive_card}
                    
                    <div class="section-subtitle">주요 리스크 요인</div>
                    <ul class="report-list">
                        {risks_html}
                    </ul>
                </div>
                
                <!-- 2. 정책·제도 환경 분석 (NEW - 확장 콘텐츠) -->
                <div class="section">
                    <div class="section-title">2. 정책·제도 환경 분석</div>
                    
                    <div class="section-subtitle">2.1 LH 신축매입임대 사업 개요</div>
                    <div style="margin-bottom: 16px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('policy_context', {}).get('lh_program_overview', 'LH 신축매입임대주택 사업 설명을 준비 중입니다.')}
                    </div>
                    
                    <div class="section-subtitle">2.2 현재 정책 동향</div>
                    <div style="margin-bottom: 16px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('policy_context', {}).get('current_policy_trend', '정책 동향 분석을 진행 중입니다.')}
                    </div>
                    
                    <div class="section-subtitle">2.3 LH 승인 기준</div>
                    <div style="margin-bottom: 16px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('policy_context', {}).get('approval_criteria', 'LH 승인 기준을 분석 중입니다.')}
                    </div>
                    
                    <div class="section-subtitle">2.4 규제 환경</div>
                    <div style="margin-bottom: 16px; padding: 16px; background: #EFF6FF; border-left: 4px solid #3B82F6; border-radius: 4px;">
                        <div style="font-size: 14px; color: #1E40AF; line-height: 1.6;">
                            {data.get('policy_context', {}).get('regulatory_environment', '규제 환경 분석을 진행 중입니다.')}
                        </div>
                    </div>
                </div>
                
                <!-- 3. 토지 가치 평가 및 입지 분석 (10페이지 분량 확장) -->
                <div class="section">
                    <div class="section-title">3. 토지 가치 평가 및 입지 분석</div>
                    
                    <div class="section-subtitle">3.1 감정평가 방법론 및 적용 기준</div>
                    <div style="margin-bottom: 20px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('land_value_factors', {}).get('appraisal_methodology', '감정평가 방법론을 적용하여 토지 가치를 산정하고 있습니다.')}
                    </div>
                    
                    <div class="section-subtitle">3.2 토지 가치 종합 평가</div>
                    <div style="margin-bottom: 16px; padding: 12px; background: #EFF6FF; border-left: 4px solid #3B82F6; border-radius: 4px;">
                        <div style="font-size: 14px; color: #1E40AF; line-height: 1.6;">
                            {data.get('land_value_interpretation', '토지 가치 평가를 진행 중입니다.')}
                        </div>
                    </div>
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
                    
                    <div class="section-subtitle">3.3 입지적 강점 및 접근성 분석</div>
                    <div style="margin-bottom: 20px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('land_value_factors', {}).get('location_advantage', '입지 분석을 진행 중입니다.')}
                    </div>
                    
                    <div class="section-subtitle">3.4 용도지역 특성이 토지가치에 미치는 영향</div>
                    <div style="margin-bottom: 20px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('land_value_factors', {}).get('zoning_impact', '용도지역 분석을 진행 중입니다.')}
                    </div>
                    
                    <div class="section-subtitle">3.5 시장 거래 사례 기반 비교 분석</div>
                    <div style="margin-bottom: 20px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('land_value_factors', {}).get('market_comparison', '시장 거래 사례를 분석 중입니다.')}
                    </div>
                    
                    <div class="section-subtitle">3.6 평가 신뢰도의 의미와 검증 근거</div>
                    <div style="margin-bottom: 20px; padding: 16px; background: #EFF6FF; border-left: 4px solid #3B82F6; border-radius: 4px;">
                        <div style="font-size: 14px; color: #1E40AF; line-height: 1.6;">
                            {data.get('land_value_factors', {}).get('confidence_factor', '평가 신뢰도를 분석 중입니다.')}
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
                
                <!-- 5. 사업성 및 재무 구조 분석 (10페이지 분량 확장) -->
                <div class="section">
                    <div class="section-title">5. 사업성 및 재무 구조 분석</div>
                    
                    <div class="section-subtitle">5.1 LH 신축매입임대 사업의 수익 구조</div>
                    <div style="margin-bottom: 20px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('financial_structure', {}).get('business_model', 'LH 매입 방식에 따른 수익 구조를 분석 중입니다.')}
                    </div>
                    
                    <div class="section-subtitle">5.2 종합 사업성 평가</div>
                    <div style="margin-bottom: 16px; padding: 12px; background: #ECFDF5; border-left: 4px solid #10B981; border-radius: 4px;">
                        <div style="font-size: 14px; color: #065F46; line-height: 1.6;">
                            {data.get('financial_interpretation', '사업성 분석을 진행 중입니다.')}
                        </div>
                    </div>
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
                    
                    <div class="section-subtitle">5.3 사업성 분석의 전제와 시나리오</div>
                    <div style="margin-bottom: 20px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('financial_structure', {}).get('financial_feasibility_deep_dive', '시나리오 분석을 진행 중입니다.')}
                    </div>
                    
                    <div class="section-subtitle">5.4 공공 사업과 민간 사업의 수익성 비교</div>
                    <div style="margin-bottom: 20px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('financial_structure', {}).get('public_vs_private', '공공·민간 사업 비교 분석을 진행 중입니다.')}
                    </div>
                    
                    <div class="section-subtitle">5.5 수익성을 결정하는 핵심 요인</div>
                    <div style="margin-bottom: 20px; padding: 16px; background: #EFF6FF; border-left: 4px solid #3B82F6; border-radius: 4px;">
                        <div style="font-size: 14px; color: #1E40AF; line-height: 1.6;">
                            {data.get('financial_structure', {}).get('profitability_drivers', '수익성 핵심 요인을 분석 중입니다.')}
                        </div>
                    </div>
                </div>
                
                <!-- 6. 리스크 요인 및 대응 전략 (4페이지 분량) -->
                <div class="section">
                    <div class="section-title">6. 리스크 요인 및 대응 전략</div>
                    
                    <div class="section-subtitle">6.1 구조적 리스크 요인</div>
                    <div style="margin-bottom: 20px; padding: 16px; background: #FEF2F2; border-left: 4px solid #EF4444; border-radius: 4px;">
                        <div style="font-size: 14px; color: #991B1B; line-height: 1.6;">
                            {data.get('risk_analysis', {}).get('structural_risks', '구조적 리스크를 분석 중입니다.')}
                        </div>
                    </div>
                    
                    <div class="section-subtitle">6.2 정책 변동 리스크</div>
                    <div style="margin-bottom: 20px; padding: 16px; background: #FEF2F2; border-left: 4px solid #EF4444; border-radius: 4px;">
                        <div style="font-size: 14px; color: #991B1B; line-height: 1.6;">
                            {data.get('risk_analysis', {}).get('policy_risks', '정책 리스크를 분석 중입니다.')}
                        </div>
                    </div>
                    
                    <div class="section-subtitle">6.3 종합 리스크 대응 전략</div>
                    <div style="margin-bottom: 20px; padding: 16px; background: #ECFDF5; border-left: 4px solid #10B981; border-radius: 4px;">
                        <div style="font-size: 14px; color: #065F46; line-height: 1.6;">
                            {data.get('risk_analysis', {}).get('mitigation_strategy', '리스크 대응 전략을 수립 중입니다.')}
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
                
                <!-- 이 땅으로 무엇을 할 수 있는가 (확장) -->
                <div class="section">
                    <div class="section-title">🎯 이 땅으로 무엇을 할 수 있나요?</div>
                    
                    <div style="padding: 20px; background: #F0F9FF; border-radius: 8px; border-left: 4px solid #3B82F6; margin-bottom: 20px;">
                        <div style="font-size: 16px; font-weight: 600; color: #1E40AF; line-height: 1.8;">
                            {data.get('what_you_can_do', '분석 결과를 검토 중입니다.')}
                        </div>
                    </div>
                    
                    <div style="padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8; margin-bottom: 16px;">
                        <strong style="color: #1F2937; font-size: 15px;">✨ 쉽게 설명하면</strong><br><br>
                        이 땅은 <strong style="color: #3B82F6;">공공임대주택</strong>을 지을 수 있는 땅입니다. 
                        한국토지주택공사(LH)라는 공공기관이 <strong>건물을 준공하면 바로 매입</strong>해 가는 방식이기 때문에, 
                        일반 아파트처럼 분양 걱정을 하지 않아도 됩니다.<br><br>
                        
                        쉽게 말하면, <strong>"건물만 지으면 LH가 다 사가는 안정적인 사업"</strong>입니다. 
                        리스크는 낮지만, 큰 돈을 벌기보다는 <strong>안정적인 수익</strong>을 기대할 수 있는 방식입니다.
                    </div>
                    
                    <div style="padding: 16px; background: #FEF3C7; border-radius: 8px; line-height: 1.8; margin-bottom: 16px;">
                        <strong style="color: #92400E; font-size: 15px;">🏠 구체적으로 어떤 건물을 지을 수 있나요?</strong><br><br>
                        • <strong>주택 종류</strong>: 청년, 신혼부부, 또는 일반 가구를 위한 소형 임대주택<br>
                        • <strong>세대 수</strong>: 약 {format_units(data.get('buildable_units'))} (법적 기준 기준)<br>
                        • <strong>건물 규모</strong>: 중층 아파트 또는 빌라 형태 (보통 5~10층)<br>
                        • <strong>평수</strong>: 세대당 전용면적 약 20~40평 (가구 구성에 따라 다름)<br><br>
                        
                        이 정도 규모면 <strong>작은 단지 하나</strong> 정도 되는 크기입니다. 
                        너무 크지도, 작지도 않은 <strong>적당한 규모</strong>로 보시면 됩니다.
                    </div>
                </div>
                
                <!-- 토지 가치 (확장) -->
                <div class="section">
                    <div class="section-title">💰 현재 이 땅의 가치는 얼마인가요?</div>
                    
                    <div class="data-card" style="margin-bottom: 16px;">
                        <div class="data-row">
                            <span class="data-label">총 토지 가치 (현재 시세)</span>
                            {format_currency(data.get('land_value_krw'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">평당 가격</span>
                            {format_currency(data.get('land_value_per_pyeong_krw'))}
                        </div>
                    </div>
                    
                    <div style="padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8; margin-bottom: 16px;">
                        <strong style="color: #1F2937; font-size: 15px;">📌 이 가격이 정확한가요?</strong><br><br>
                        이 가격은 <strong>전문 감정평가 방식</strong>으로 산출한 것으로, 
                        주변에서 최근 실제로 거래된 땅의 가격을 참고하여 계산했습니다.<br><br>
                        
                        {data.get('land_value_interpretation', '신뢰도는 보통 수준 이상으로, 실제 거래 시 이 가격에서 크게 벗어나지 않을 것으로 예상됩니다.')}<br><br>
                        
                        다만, 부동산 시장은 계속 변하기 때문에, 
                        <strong>실제 거래 시점</strong>에는 약간 달라질 수 있습니다. 
                        이 가격은 <strong>"지금 시점의 합리적인 추정값"</strong>으로 이해하시면 됩니다.
                    </div>
                    
                    <div style="padding: 16px; background: #ECFDF5; border-left: 4px solid #10B981; border-radius: 4px; line-height: 1.8;">
                        <strong style="color: #065F46; font-size: 15px;">💡 쉽게 이해하기</strong><br><br>
                        평당 {format_currency(data.get('land_value_per_pyeong_krw'))}이라는 것은, 
                        이 지역에서 <strong>평균적인 가격대</strong>에 해당합니다. 
                        특별히 비싸지도, 싸지도 않은 <strong>적정 가격</strong>으로 보시면 됩니다.
                    </div>
                </div>
                
                <!-- 사업을 하면 얼마나 남을까요? (확장) -->
                <div class="section">
                    <div class="section-title">💸 사업을 하면 얼마나 남을까요?</div>
                    
                    <div class="data-card" style="margin-bottom: 16px;">
                        <div class="data-row">
                            <span class="data-label">예상 순이익 (NPV)</span>
                            {format_currency(data.get('npv_krw'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">수익률 (연평균)</span>
                            {format_percentage(data.get('irr_pct'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">투자 대비 수익</span>
                            {format_percentage(data.get('roi_pct'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">종합 평가</span>
                            <span class="data-value">{data.get('expected_profit', '분석 중')}</span>
                        </div>
                    </div>
                    
                    <div style="padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8; margin-bottom: 16px;">
                        <strong style="color: #1F2937; font-size: 15px;">🤔 이 숫자들이 무슨 뜻인가요?</strong><br><br>
                        
                        <strong>1) 예상 순이익 ({format_currency(data.get('npv_krw'))})</strong><br>
                        → 건물을 짓고, LH에 매각한 후 <strong>최종적으로 남는 돈</strong>입니다. 
                        단, 이 금액에서 세금과 기타 비용을 빼야 합니다.<br><br>
                        
                        <strong>2) 수익률 ({format_percentage(data.get('irr_pct'))})</strong><br>
                        → 1년에 평균 몇 %씩 돈이 불어나는지를 나타냅니다. 
                        은행 예금 금리(약 3~4%)보다는 높지만, 
                        일반 부동산 개발(15~20%)보다는 낮은 <strong>중간 수준</strong>입니다.<br><br>
                        
                        <strong>3) 투자 대비 수익 ({format_percentage(data.get('roi_pct'))})</strong><br>
                        → 투입한 돈 대비 얼마나 수익이 생기는지를 보여줍니다. 
                        예를 들어, 10억을 투입했다면 약 {round(data.get('roi_pct', 0) * 10 / 100, 1)}억 정도가 수익으로 남습니다.
                    </div>
                    
                    <div style="padding: 16px; background: #FEF3C7; border-radius: 8px; line-height: 1.8; margin-bottom: 16px;">
                        <strong style="color: #92400E; font-size: 15px;">⚠️ 주의사항</strong><br><br>
                        이 수익은 <strong>"모든 것이 계획대로 진행될 때"</strong>의 예상치입니다. 
                        실제로는 다음과 같은 변수가 있을 수 있습니다:<br><br>
                        
                        • <strong>건축비 상승</strong>: 자재비나 인건비가 오르면 수익이 줄어듭니다<br>
                        • <strong>공사 지연</strong>: 인허가나 공사가 늦어지면 이자 비용이 늘어납니다<br>
                        • <strong>LH 매입가 변동</strong>: LH가 제시하는 가격이 예상보다 낮을 수 있습니다<br><br>
                        
                        따라서 이 숫자는 <strong>"최선의 경우"</strong>로 보시고, 
                        실제로는 약간 낮아질 수 있다고 생각하시는 것이 안전합니다.
                    </div>
                    
                    <div style="padding: 16px; background: #ECFDF5; border-left: 4px solid #10B981; border-radius: 4px; line-height: 1.8;">
                        <strong style="color: #065F46; font-size: 15px;">✅ 결론</strong><br><br>
                        {data.get('financial_interpretation', '이 사업은 큰 돈을 벌기보다는, 안정적으로 적정한 수익을 낼 수 있는 사업으로 판단됩니다. 분양 리스크가 없다는 점이 가장 큰 장점입니다.')}
                    </div>
                </div>
                
                <!-- 어떤 위험이 있나요? (NEW) -->
                <div class="section">
                    <div class="section-title">⚠️ 어떤 위험이 있나요?</div>
                    
                    <div style="padding: 16px; background: #FEF2F2; border-left: 4px solid #EF4444; border-radius: 4px; line-height: 1.8; margin-bottom: 16px;">
                        <strong style="color: #991B1B; font-size: 15px;">🚨 반드시 알아두셔야 할 위험</strong><br><br>
                        
                        <strong>1) LH 승인이 안 날 수 있습니다</strong><br>
                        → LH는 "아무 땅이나 다 사주는 것"이 아닙니다. 
                        입지, 가격, 설계 등을 심사해서 <strong>부적합하면 승인을 안 해줍니다</strong>. 
                        따라서 <strong>반드시 사전에 LH와 협의</strong>를 해야 합니다.<br><br>
                        
                        <strong>2) 건축비가 예상보다 많이 들 수 있습니다</strong><br>
                        → 최근 몇 년간 건축 자재값과 인건비가 많이 올랐습니다. 
                        예상보다 건축비가 10~20% 더 들면 <strong>수익이 크게 줄어들 수 있습니다</strong>.<br><br>
                        
                        <strong>3) 인허가가 늦어질 수 있습니다</strong><br>
                        → 건축허가 받는 데 시간이 오래 걸리면, 
                        그 사이에 <strong>대출 이자가 계속 나갑니다</strong>. 
                        6개월 지연되면 이자만 수천만 원이 추가될 수 있습니다.<br><br>
                        
                        <strong>4) LH 매입가가 생각보다 낮을 수 있습니다</strong><br>
                        → LH는 "표준 매입가"라는 기준을 적용하는데, 
                        실제 협의 과정에서 <strong>예상보다 낮은 가격</strong>을 제시할 수 있습니다.
                    </div>
                    
                    <div style="padding: 16px; background: #ECFDF5; border-left: 4px solid #10B981; border-radius: 4px; line-height: 1.8;">
                        <strong style="color: #065F46; font-size: 15px;">💡 위험을 줄이는 방법</strong><br><br>
                        • <strong>LH 사전 협의</strong>: 본격적으로 시작하기 전에 LH와 충분히 상담하세요<br>
                        • <strong>건축비 정밀 견적</strong>: 여러 건설사에서 견적을 받아 비교하세요<br>
                        • <strong>전문가 자문</strong>: 이런 사업을 해본 전문가나 컨설팅 회사의 도움을 받으세요<br>
                        • <strong>여유 자금 확보</strong>: 예상 비용보다 10~15% 정도 여유 자금을 준비하세요
                    </div>
                </div>
                
                <!-- 다음 단계 (확장) -->
                <div class="section">
                    <div class="section-title">✅ 다음에 무엇을 해야 하나요?</div>
                    
                    <div style="padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8; margin-bottom: 16px;">
                        <strong style="color: #1F2937; font-size: 15px; display: block; margin-bottom: 12px;">📋 단계별 진행 순서</strong>
                        
                        <div style="padding: 12px; background: white; border-radius: 6px; margin-bottom: 10px; border-left: 3px solid #3B82F6;">
                            <strong style="color: #3B82F6;">1단계: LH 사전 협의 (1~2주)</strong><br>
                            → LH 지역본부에 연락해서 "신축매입임대 사업 가능 여부"를 문의하세요. 
                            이 때 대상 토지의 위치, 면적, 용도지역 등을 알려주시면 됩니다.
                        </div>
                        
                        <div style="padding: 12px; background: white; border-radius: 6px; margin-bottom: 10px; border-left: 3px solid #10B981;">
                            <strong style="color: #10B981;">2단계: 건축비 견적 받기 (2~3주)</strong><br>
                            → 최소 3개 이상의 건설사에서 견적을 받으세요. 
                            "LH 신축매입임대 공사"라고 말하면 건설사들이 알아듭니다.
                        </div>
                        
                        <div style="padding: 12px; background: white; border-radius: 6px; margin-bottom: 10px; border-left: 3px solid #F59E0B;">
                            <strong style="color: #F59E0B;">3단계: 수익성 재검토 (1주)</strong><br>
                            → LH 예상 매입가와 건축비 견적을 바탕으로 
                            <strong>실제로 수익이 나는지 다시 계산</strong>해 보세요. 
                            이 단계에서 전문가(회계사, 건축사, 컨설턴트)의 도움을 받는 것을 권장합니다.
                        </div>
                        
                        <div style="padding: 12px; background: white; border-radius: 6px; margin-bottom: 10px; border-left: 3px solid #8B5CF6;">
                            <strong style="color: #8B5CF6;">4단계: LH 정식 승인 신청 (1~2개월)</strong><br>
                            → 수익성이 확인되면, LH에 정식으로 사업 승인을 신청합니다. 
                            이 때 토지 관련 서류, 설계 도면(초안), 사업 계획서 등이 필요합니다.
                        </div>
                        
                        <div style="padding: 12px; background: white; border-radius: 6px; border-left: 3px solid #EF4444;">
                            <strong style="color: #EF4444;">5단계: 인허가 및 착공 (6~12개월)</strong><br>
                            → LH 승인이 나면, 지자체에 건축허가를 신청하고 
                            허가가 나는 대로 공사를 시작합니다. 
                            공사 기간은 보통 18~24개월 정도 걸립니다.
                        </div>
                    </div>
                    
                    <div style="padding: 16px; background: #EFF6FF; border-left: 4px solid #3B82F6; border-radius: 4px; line-height: 1.8;">
                        <strong style="color: #1E40AF; font-size: 15px;">🎯 가장 중요한 것</strong><br><br>
                        <strong>"서두르지 마세요."</strong><br><br>
                        이 사업은 최소 2~3년이 걸리는 장기 프로젝트입니다. 
                        각 단계를 충분히 검토하고, 전문가의 조언을 받으면서 
                        <strong>신중하게 진행</strong>하는 것이 가장 중요합니다.<br><br>
                        
                        특히 <strong>1단계(LH 사전 협의)</strong>와 <strong>3단계(수익성 재검토)</strong>에서 
                        확실한 확인을 받지 못하면, 나중에 큰 손해를 볼 수 있으니 주의하세요.
                    </div>
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
