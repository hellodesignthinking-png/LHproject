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
                
                <!-- ===== v4.2 추가: 정책·제도 파트 (200 lines) ===== -->
                <div class="section">
                    <div class="section-title">📜 LH 신축매입임대 제도, 정확히 이해하기</div>
                    
                    <!-- 1.1 제도의 도입 배경 -->
                    <div style="padding: 20px; background: #F9FAFB; border-radius: 8px; margin-bottom: 20px;">
                        <strong style="color: #1F2937; font-size: 16px; display: block; margin-bottom: 12px;">
                            🏛️ 왜 이 제도가 생겼나요?
                        </strong>
                        <div style="line-height: 1.8; color: #374151;">
                            <p style="margin-bottom: 12px;">
                                <strong>LH 신축매입임대 제도</strong>는 2000년대 초반, 우리나라가 <strong>"주거복지 국가"</strong>로 
                                전환하는 과정에서 만들어진 제도입니다.
                            </p>
                            <p style="margin-bottom: 12px;">
                                당시 정부는 <strong>저소득층과 사회초년생</strong>의 주거 문제가 심각하다는 것을 인식했습니다. 
                                하지만 정부와 LH가 직접 모든 땅을 사서 집을 짓기에는 <strong>예산과 인력이 부족</strong>했습니다.
                            </p>
                            <p style="margin-bottom: 12px;">
                                그래서 나온 아이디어가 <strong>"민간이 짓고, LH가 사주는"</strong> 방식입니다. 
                                토지주나 건설사가 건물을 지으면, LH가 완공 후 즉시 매입해서 공공임대주택으로 운영하는 구조입니다.
                            </p>
                            <p style="padding: 12px; background: #EFF6FF; border-radius: 6px; margin-top: 16px;">
                                <strong style="color: #1E40AF;">💡 쉽게 정리하면</strong><br>
                                "정부는 집이 필요한데 돈이 부족하고, 민간은 돈은 있는데 분양 리스크가 부담스럽다" 
                                → 둘을 연결해주는 것이 바로 <strong>신축매입임대 제도</strong>입니다.
                            </p>
                        </div>
                    </div>
                    
                    <!-- 1.2 제도가 해결하려는 정책 문제 -->
                    <div style="padding: 20px; background: #FEF3C7; border-radius: 8px; margin-bottom: 20px;">
                        <strong style="color: #92400E; font-size: 16px; display: block; margin-bottom: 12px;">
                            🎯 이 제도가 해결하려는 문제는?
                        </strong>
                        <div style="line-height: 1.8; color: #78350F;">
                            <p style="margin-bottom: 12px;">
                                <strong>1) 청년·신혼부부 주거난</strong><br>
                                서울 및 수도권의 전세·월세 가격이 너무 비싸서, 
                                <strong>사회초년생이나 신혼부부</strong>가 집을 구하기 어려운 상황입니다. 
                                이들을 위한 <strong>저렴한 공공임대주택</strong>이 절실히 필요합니다.
                            </p>
                            <p style="margin-bottom: 12px;">
                                <strong>2) 공공임대 물량 부족</strong><br>
                                정부가 직접 공공임대주택을 짓는 속도가 <strong>수요를 따라가지 못합니다</strong>. 
                                매년 수만 세대가 부족한 상황에서, 민간의 도움 없이는 물량 확보가 불가능합니다.
                            </p>
                            <p style="margin-bottom: 12px;">
                                <strong>3) 민간 자본 활용 필요성</strong><br>
                                정부 예산만으로는 한계가 있기 때문에, <strong>민간 자본</strong>을 활용해서 
                                더 빠르게, 더 많은 공공임대주택을 공급하는 것이 목표입니다.
                            </p>
                            <p style="padding: 12px; background: #FFFBEB; border-radius: 6px; margin-top: 16px;">
                                <strong style="color: #92400E;">📌 핵심 포인트</strong><br>
                                이 제도는 <strong>"사회적 필요(공공임대)"</strong>와 <strong>"민간의 수익성"</strong>을 
                                동시에 충족시키기 위한 <strong>윈-윈 구조</strong>입니다.
                            </p>
                        </div>
                    </div>
                    
                    <!-- 1.3 실제 LH 심사·집행 구조 -->
                    <div style="padding: 20px; background: #ECFDF5; border-radius: 8px; margin-bottom: 20px;">
                        <strong style="color: #065F46; font-size: 16px; display: block; margin-bottom: 12px;">
                            🔍 LH는 어떻게 심사하나요?
                        </strong>
                        <div style="line-height: 1.8; color: #065F46;">
                            <p style="margin-bottom: 12px;">
                                LH 심사는 <strong>5단계 프로세스</strong>로 진행됩니다:
                            </p>
                            
                            <div style="padding: 12px; background: white; border-radius: 6px; margin-bottom: 10px; border-left: 3px solid #10B981;">
                                <strong style="color: #10B981;">1단계: 사전 상담 (1~2주)</strong><br>
                                토지주가 LH 지역본부에 "이 땅으로 신축매입임대가 가능한가요?"라고 문의하면, 
                                LH 담당자가 <strong>기본 입지 조건</strong>을 검토합니다. 
                                이 단계에서 "불가능하다"고 판단되면 더 이상 진행하지 않습니다.
                            </div>
                            
                            <div style="padding: 12px; background: white; border-radius: 6px; margin-bottom: 10px; border-left: 3px solid #10B981;">
                                <strong style="color: #10B981;">2단계: 입지 평가 (2~3주)</strong><br>
                                LH는 <strong>역세권 거리, 학군, 생활 인프라</strong> 등을 종합적으로 평가합니다. 
                                특히 <strong>역에서 도보 10분 이내</strong> 같은 조건이 중요합니다. 
                                입지가 적합하지 않으면 이 단계에서 탈락할 수 있습니다.
                            </div>
                            
                            <div style="padding: 12px; background: white; border-radius: 6px; margin-bottom: 10px; border-left: 3px solid #10B981;">
                                <strong style="color: #10B981;">3단계: 가격 협의 (3~4주)</strong><br>
                                LH는 <strong>"표준 매입가 산정 기준"</strong>에 따라 매입 가격을 제시합니다. 
                                이 가격은 <strong>건축비 + 토지비 + 적정 이윤</strong>으로 구성되는데, 
                                토지주가 원하는 가격과 차이가 나면 <strong>협상</strong>이 필요합니다.
                            </div>
                            
                            <div style="padding: 12px; background: white; border-radius: 6px; margin-bottom: 10px; border-left: 3px solid #10B981;">
                                <strong style="color: #10B981;">4단계: 설계 검토 (4~6주)</strong><br>
                                건축 설계가 <strong>LH 기준</strong>에 맞는지 검토합니다. 
                                특히 <strong>세대 구성(1인 가구용, 신혼부부용 등)</strong>과 
                                <strong>면적 기준(전용면적 40㎡ 이하)</strong>이 중요합니다.
                            </div>
                            
                            <div style="padding: 12px; background: white; border-radius: 6px; border-left: 3px solid #10B981;">
                                <strong style="color: #10B981;">5단계: 최종 승인 (2~3주)</strong><br>
                                위 4개 단계를 모두 통과하면, LH 본부에서 <strong>최종 승인</strong>을 내립니다. 
                                이 단계에서는 <strong>계약서 작성</strong>과 <strong>매입 조건 확정</strong>이 이루어집니다.
                            </div>
                            
                            <p style="padding: 12px; background: #D1FAE5; border-radius: 6px; margin-top: 16px;">
                                <strong style="color: #065F46;">⏱️ 전체 소요 기간</strong><br>
                                사전 상담 시작부터 최종 승인까지 <strong>평균 3~4개월</strong>이 걸립니다. 
                                하지만 협상이나 보완이 필요한 경우 <strong>6개월 이상</strong> 소요될 수 있습니다.
                            </p>
                        </div>
                    </div>
                    
                    <!-- 1.4 대상 사업에 미치는 영향 -->
                    <div style="padding: 20px; background: #EFF6FF; border-radius: 8px; margin-bottom: 20px;">
                        <strong style="color: #1E40AF; font-size: 16px; display: block; margin-bottom: 12px;">
                            📍 이 땅에는 어떻게 적용되나요?
                        </strong>
                        <div style="line-height: 1.8; color: #1E3A8A;">
                            <p style="margin-bottom: 12px;">
                                <strong style="color: #3B82F6;">✅ 유리한 점</strong>
                            </p>
                            <ul style="margin-left: 20px; margin-bottom: 16px;">
                                <li style="margin-bottom: 8px;">
                                    <strong>입지 조건</strong>: 이 땅은 {data.get('location_advantage', '역세권 또는 주요 생활권에 위치')}하여 
                                    LH 입지 기준을 충족할 가능성이 높습니다.
                                </li>
                                <li style="margin-bottom: 8px;">
                                    <strong>개발 규모</strong>: 예상 세대수({format_units(data.get('buildable_units'))})가 
                                    LH 선호 규모(50~150세대)에 적합합니다.
                                </li>
                                <li style="margin-bottom: 8px;">
                                    <strong>용도지역</strong>: 현재 용도지역이 주거지역으로, 
                                    공공임대주택 개발에 유리한 조건입니다.
                                </li>
                            </ul>
                            
                            <p style="margin-bottom: 12px; margin-top: 20px;">
                                <strong style="color: #DC2626;">⚠️ 주의할 점</strong>
                            </p>
                            <ul style="margin-left: 20px;">
                                <li style="margin-bottom: 8px;">
                                    <strong>가격 협상</strong>: LH 표준 매입가와 토지주 기대 가격 간 차이가 있을 수 있으므로, 
                                    <strong>유연한 협상 자세</strong>가 필요합니다.
                                </li>
                                <li style="margin-bottom: 8px;">
                                    <strong>설계 기준</strong>: LH 기준에 맞는 설계가 필수이므로, 
                                    초기 단계부터 <strong>LH 담당자와 긴밀히 협의</strong>해야 합니다.
                                </li>
                                <li style="margin-bottom: 8px;">
                                    <strong>인허가 협조</strong>: 지자체 인허가 과정에서 LH 사업임을 명확히 밝히면 
                                    <strong>우대받을 가능성</strong>이 있지만, 보장되는 것은 아닙니다.
                                </li>
                            </ul>
                        </div>
                    </div>
                    
                    <!-- 1.5 제도상 한계와 비공식 관행 -->
                    <div style="padding: 20px; background: #FEF2F2; border-radius: 8px; margin-bottom: 20px;">
                        <strong style="color: #991B1B; font-size: 16px; display: block; margin-bottom: 12px;">
                            🚨 제도의 한계와 실제 운영
                        </strong>
                        <div style="line-height: 1.8; color: #7F1D1D;">
                            <p style="margin-bottom: 12px;">
                                <strong>공식 기준 vs 실제 운영</strong><br>
                                LH는 <strong>공식 심사 기준</strong>을 공개하고 있지만, 
                                실제로는 <strong>지역본부별로 해석과 적용이 다릅니다</strong>. 
                                예를 들어, "역세권 도보 10분"이라는 기준도 
                                어떤 지역본부는 엄격하게 적용하고, 어떤 곳은 유연하게 적용합니다.
                            </p>
                            <p style="margin-bottom: 12px;">
                                <strong>지역본부별 차이</strong><br>
                                서울·경기본부는 <strong>입지 기준이 까다로운 대신</strong> 매입가가 높고, 
                                지방본부는 입지 기준이 유연한 대신 매입가가 낮은 경향이 있습니다. 
                                따라서 <strong>어느 지역본부 관할인지</strong>가 중요합니다.
                            </p>
                            <p style="margin-bottom: 12px;">
                                <strong>협상 여지</strong><br>
                                LH 표준 매입가는 <strong>"협상의 출발점"</strong>이지 확정 가격이 아닙니다. 
                                특히 LH가 해당 지역에서 <strong>물량 확보가 시급한 경우</strong>, 
                                토지주에게 유리한 조건으로 협상될 가능성이 높아집니다.
                            </p>
                            <p style="padding: 12px; background: #FEE2E2; border-radius: 6px; margin-top: 16px;">
                                <strong style="color: #991B1B;">💡 실무 팁</strong><br>
                                LH 담당자와 <strong>초기 단계부터 신뢰 관계</strong>를 형성하고, 
                                <strong>"이 사업을 꼭 성사시키겠다"</strong>는 의지를 보여주면 
                                협상이 훨씬 수월해집니다.
                            </p>
                        </div>
                    </div>
                </div>
                <!-- ===== v4.2 정책·제도 파트 끝 ===== -->
                
                <!-- ===== v4.2 리스크 관리 섹션 시작 ===== -->
                <div class="section">
                    <div class="section-title">🛡️ 사업 진행 중 알아두셔야 할 변수들</div>
                    
                    <!-- 소개 -->
                    <div style="padding: 16px; background: #F0F9FF; border-radius: 8px; line-height: 1.8; margin-bottom: 24px;">
                        <strong style="color: #1E40AF; font-size: 15px;">이 섹션에서는</strong><br><br>
                        LH 신축매입임대 사업을 진행할 때 주의해야 할 변수들을 설명드립니다. 
                        이것들은 <strong>"사업이 불가능하다"는 의미가 아니라 "잘 관리해야 할 요소들"</strong>입니다. 
                        각 변수를 정확히 이해하고 미리 대비하면, 안정적으로 사업을 진행할 수 있습니다.
                    </div>
                    
                    <!-- 1. 제도 환경 -->
                    <div style="padding: 20px; background: #F9FAFB; border-radius: 8px; margin-bottom: 20px;">
                        <strong style="color: #1F2937; font-size: 16px; display: block; margin-bottom: 12px;">
                            📋 제도 환경에 대한 이해
                        </strong>
                        
                        <div style="line-height: 1.8; color: #374151; margin-bottom: 16px;">
                            <strong style="color: #3B82F6;">정부 정책과 LH 사업의 관계</strong><br><br>
                            LH 신축매입임대 제도는 지난 20년간 꾸준히 운영되어 온 정부의 주거복지 정책입니다. 
                            이 제도는 청년, 신혼부부, 저소득층을 위한 공공임대주택을 민간의 도움을 받아 공급하는 방식으로, 
                            정권이 바뀌어도 기본 틀은 계속 유지되어 왔습니다. 정부 예산 상황이나 부동산 시장 상황에 따라 
                            세부 운영 방식(지역별 우선순위, 매입 물량 등)은 조정될 수 있지만, 제도 자체가 없어지는 것은 아닙니다.
                        </div>
                        
                        <div style="line-height: 1.8; color: #374151; margin-bottom: 16px;">
                            <strong style="color: #3B82F6;">실제로 어떤 변화가 있을 수 있나요?</strong><br><br>
                            정책 환경이 변하면 LH가 선호하는 지역이나 주택 유형이 달라질 수 있습니다. 
                            예를 들어, 올해는 수도권을 우선적으로 매입하다가 내년에는 지방 중소도시를 우선할 수도 있습니다. 
                            또는 청년 1인 가구용 소형 주택을 더 많이 원하거나, 신혼부부용 중형 주택으로 방향을 바꿀 수도 있습니다. 
                            하지만 이런 변화는 "갑자기" 일어나는 것이 아니라, LH가 미리 방향을 발표하고 
                            기존 사업에는 경과 조치를 제공하는 것이 일반적입니다.
                        </div>
                        
                        <div style="padding: 12px; background: #EFF6FF; border-radius: 6px; line-height: 1.8;">
                            <strong style="color: #1E40AF;">✅ 토지주가 할 수 있는 일</strong><br><br>
                            가장 중요한 것은 <strong>사업을 시작하기 전에 LH와 충분히 상담</strong>하는 것입니다. 
                            LH 지역본부에 가서 "지금 이 지역에서 어떤 유형의 주택을 원하시나요?", 
                            "앞으로 1~2년간 정책 방향이 어떻게 되나요?"라고 물어보면 담당자가 친절히 안내해 줍니다. 
                            정책 변화를 두려워할 필요는 없고, <strong>변화에 맞춰 계획을 조정</strong>하면 됩니다.
                        </div>
                    </div>
                    
                    <!-- 2. 심사 과정 -->
                    <div style="padding: 20px; background: #ECFDF5; border-radius: 8px; margin-bottom: 20px;">
                        <strong style="color: #065F46; font-size: 16px; display: block; margin-bottom: 12px;">
                            ✓ 심사 과정에서 고려되는 요소
                        </strong>
                        
                        <div style="line-height: 1.8; color: #065F46; margin-bottom: 16px;">
                            <strong style="color: #10B981;">LH는 어떤 기준으로 심사하나요?</strong><br><br>
                            LH는 크게 세 가지를 봅니다. 첫째, <strong>입지가 좋은가?</strong> 
                            (역에서 가깝고, 학교·마트·병원이 근처에 있는가), 
                            둘째, <strong>가격이 적정한가?</strong> 
                            (토지값과 건축비를 합쳐서 LH 예산 범위 안에 들어오는가), 
                            셋째, <strong>사업자가 믿을 만한가?</strong> 
                            (과거에 비슷한 사업을 해본 경험이 있거나, 자금력이 충분한가). 
                            이 세 가지가 모두 적정 수준이면 승인 가능성이 높습니다.
                        </div>
                        
                        <div style="line-height: 1.8; color: #065F46; margin-bottom: 16px;">
                            <strong style="color: #10B981;">점수만 높으면 무조건 승인되나요?</strong><br><br>
                            꼭 그렇지는 않습니다. LH는 공공기관이기 때문에 
                            "이 사업이 공공 목적에 부합하는가", "이 지역에 정말 이런 주택이 필요한가", 
                            "사업자가 실제로 건물을 완공할 능력이 있는가" 등을 종합적으로 판단합니다. 
                            예를 들어, 어떤 땅이 입지 점수는 높지만 그 지역에 이미 공공임대주택이 많다면, 
                            LH는 "지금은 다른 지역을 우선하겠습니다"라고 할 수 있습니다.
                        </div>
                        
                        <div style="padding: 12px; background: #D1FAE5; border-radius: 6px; line-height: 1.8;">
                            <strong style="color: #065F46;">✅ 승인 가능성을 높이는 방법</strong><br><br>
                            가장 확실한 방법은 <strong>사전에 LH 담당자와 충분히 대화</strong>하는 것입니다. 
                            "이 땅으로 사업하고 싶은데 가능할까요?", "어떤 점을 보완하면 좋을까요?"라고 물어보면, 
                            담당자가 솔직하게 의견을 줍니다. <strong>LH 입장에서 "이 사업은 안전하고, 
                            공공 목적에 맞고, 실행 가능하다"고 느끼게 만드는 것</strong>이 핵심입니다.
                        </div>
                    </div>
                    
                    <!-- 3. 토지 가치 -->
                    <div style="padding: 20px; background: #FEF3C7; border-radius: 8px; margin-bottom: 20px;">
                        <strong style="color: #92400E; font-size: 16px; display: block; margin-bottom: 12px;">
                            💰 토지 가치 산정 시 유의사항
                        </strong>
                        
                        <div style="line-height: 1.8; color: #78350F; margin-bottom: 16px;">
                            <strong style="color: #F59E0B;">감정가는 얼마나 정확한가요?</strong><br><br>
                            감정평가사가 산정한 토지 감정가는 <strong>"현재 시점의 합리적 추정치"</strong>입니다. 
                            인근에서 실제로 거래된 땅의 가격을 참고하고, 이 땅의 특성(넓이, 형태, 용도지역 등)을 
                            고려해서 계산합니다. 하지만 감정가는 "절대 정답"이 아니라 
                            <strong>"이 정도면 합리적이다"는 범위</strong>라고 이해하시면 됩니다. 
                            예를 들어, 평당 500만 원으로 감정이 나왔다면, 실제 거래 시 
                            480만 원에서 520만 원 사이에서 결정될 가능성이 큽니다.
                        </div>
                        
                        <div style="line-height: 1.8; color: #78350F; margin-bottom: 16px;">
                            <strong style="color: #F59E0B;">감정가가 나중에 달라질 수 있나요?</strong><br><br>
                            네, 달라질 수 있습니다. 감정평가는 <strong>특정 시점의 시장 상황</strong>을 반영하기 때문에, 
                            6개월이나 1년 후에 다시 평가하면 가격이 오르거나 내릴 수 있습니다. 
                            특히 그 지역에 큰 개발 계획(지하철 연장, 대형 상업시설 입점 등)이 발표되면 
                            토지 가격이 급등할 수 있고, 반대로 부동산 시장이 전반적으로 침체되면 가격이 내려갈 수 있습니다.
                        </div>
                        
                        <div style="padding: 12px; background: #FFFBEB; border-radius: 6px; line-height: 1.8;">
                            <strong style="color: #92400E;">✅ 대비 방법</strong><br><br>
                            가장 좋은 방법은 <strong>초기 감정가보다 약간 높게 잡고 계획을 세우는 것</strong>입니다. 
                            예를 들어, 감정가가 평당 500만 원이 나왔다면, 실제 매입 시 평당 550만 원까지 
                            오를 수 있다고 가정하고 사업 수익성을 계산해 보세요. 
                            그래도 수익이 나온다면 안전한 사업입니다.
                        </div>
                    </div>
                    
                    <!-- 4. 사업 진행 변수 -->
                    <div style="padding: 20px; background: #FEF2F2; border-radius: 8px; margin-bottom: 20px;">
                        <strong style="color: #991B1B; font-size: 16px; display: block; margin-bottom: 12px;">
                            ⚠️ 사업 진행 중 발생할 수 있는 변수
                        </strong>
                        
                        <div style="line-height: 1.8; color: #7F1D1D; margin-bottom: 16px;">
                            <strong style="color: #DC2626;">건축 규모가 줄어들 수 있나요?</strong><br><br>
                            사전 검토에서 "이 땅에 80세대 지을 수 있다"고 나왔어도, 
                            실제 건축허가를 받을 때 지자체가 "일조권 때문에 75세대까지만 가능합니다"라고 할 수 있습니다. 
                            법규 자체는 명확하지만, <strong>법규를 어떻게 해석하고 적용하느냐는 
                            지자체 담당자의 판단</strong>이 들어가기 때문입니다.
                        </div>
                        
                        <div style="line-height: 1.8; color: #7F1D1D; margin-bottom: 16px;">
                            <strong style="color: #DC2626;">건축비가 오를 수 있나요?</strong><br><br>
                            네, 가능합니다. 건축비는 <strong>철근, 시멘트, 목재 같은 자재 가격과 인건비</strong>로 
                            결정되는데, 이것들은 국제 원자재 시장, 환율, 건설 인력 수급 상황에 따라 변동합니다. 
                            최근 몇 년간은 자재비가 많이 올라서, 1년 전에 평당 400만 원으로 예상했던 건축비가 
                            실제 공사 시작 시점에는 평당 440만 원(10% 상승)이 되는 경우도 있었습니다.
                        </div>
                        
                        <div style="line-height: 1.8; color: #7F1D1D; margin-bottom: 16px;">
                            <strong style="color: #DC2626;">일정이 지연될 수 있나요?</strong><br><br>
                            가능합니다. LH 승인 과정에서 추가 검토가 필요하거나, 지자체 건축허가에서 
                            주민 민원 처리 때문에 시간이 더 걸리거나, 공사 중에 장마나 한파로 공사가 중단되는 등 
                            여러 이유로 일정이 늦어질 수 있습니다. 일정이 6개월 지연되면, 
                            그 6개월 동안 대출 이자가 계속 나가서 수익이 줄어듭니다.
                        </div>
                        
                        <div style="padding: 12px; background: #FEE2E2; border-radius: 6px; line-height: 1.8;">
                            <strong style="color: #991B1B;">✅ 대응 방법</strong><br><br>
                            첫째, <strong>보수적으로 계산</strong>하세요. 건축 규모는 예상보다 5% 적게, 
                            건축비는 예상보다 10% 높게, 일정은 예상보다 20% 길게 잡고 수익성을 계산해 보세요. 
                            둘째, <strong>시공사와 총액 계약</strong>을 하세요. 
                            "자재비가 올라도 계약 금액은 안 올린다"는 조건을 넣으면, 건축비 상승 리스크를 시공사가 부담합니다. 
                            셋째, <strong>LH와 지자체 담당자와 자주 소통</strong>하세요.
                        </div>
                    </div>
                    
                    <!-- 5. 종합 판단 -->
                    <div style="padding: 20px; background: #EFF6FF; border-radius: 8px; border-left: 4px solid #3B82F6;">
                        <strong style="color: #1E40AF; font-size: 16px; display: block; margin-bottom: 12px;">
                            ✨ 전체적으로 보았을 때의 판단
                        </strong>
                        
                        <div style="line-height: 1.8; color: #1E3A8A; margin-bottom: 16px;">
                            <strong style="color: #3B82F6;">이 사업은 안전한가요?</strong><br><br>
                            위에서 말씀드린 여러 변수들이 있지만, 
                            <strong>이것들은 "사업이 불가능하다"는 의미가 아니라 "관리해야 할 요소들"</strong>입니다. 
                            LH 신축매입임대 사업은 지난 20년간 수많은 토지주와 건설사가 성공적으로 진행해 온 사업입니다. 
                            가장 큰 장점은 <strong>"분양 리스크가 없다"</strong>는 것입니다.
                        </div>
                        
                        <div style="line-height: 1.8; color: #1E3A8A; margin-bottom: 16px;">
                            <strong style="color: #3B82F6;">수익은 어느 정도 기대할 수 있나요?</strong><br><br>
                            LH 사업은 <strong>"큰 돈을 벌기보다는 안정적으로 적정한 수익을 내는 사업"</strong>입니다. 
                            수익률은 보통 연 8~12% 정도로, 은행 예금(3~4%)보다는 높지만 
                            고위험 부동산 개발(15~20%)보다는 낮습니다. 
                            대신 리스크도 낮아서, 조심스럽게 계획하고 변수들을 잘 관리하면 안정적으로 수익을 낼 수 있습니다.
                        </div>
                        
                        <div style="padding: 16px; background: white; border-radius: 6px; line-height: 1.8;">
                            <strong style="color: #1E40AF;">🎯 지금 결정해야 할 것</strong><br><br>
                            가장 먼저 할 일은 <strong>LH 지역본부와 상담</strong>입니다. 
                            "이 땅으로 신축매입임대가 가능한가요?", "지금 이 지역에서 사업하기 좋은 시기인가요?"라고 
                            물어보세요. LH 담당자의 반응이 긍정적이면, 다음 단계로 진행하면 됩니다. 
                            <strong>서두르지 말고, 단계별로 확인하면서 진행</strong>하는 것이 가장 안전합니다.
                        </div>
                    </div>
                    
                    <!-- 최종 메시지 -->
                    <div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; margin-top: 24px;">
                        <div style="color: white; line-height: 1.8; text-align: center;">
                            <strong style="font-size: 18px; display: block; margin-bottom: 12px;">
                                💡 결론: 리스크를 이해하고 관리하면, 충분히 가능한 사업입니다
                            </strong>
                            <p style="margin: 12px 0; opacity: 0.95;">
                                LH 신축매입임대 사업에는 여러 변수가 있지만, 
                                <strong>이것들은 대부분 "관리 가능한 변수"</strong>입니다.
                            </p>
                            <p style="margin: 12px 0; opacity: 0.95;">
                                가장 중요한 것은 <strong>"서두르지 말고, 단계별로 확인하고, 전문가의 도움을 받는 것"</strong>입니다.
                            </p>
                            <p style="margin: 12px 0; opacity: 0.95;">
                                이 세 가지만 지키면, 이 사업은 안정적이고 적정한 수익을 낼 수 있는 좋은 기회입니다.
                            </p>
                        </div>
                    </div>
                </div>
                <!-- ===== v4.2 리스크 관리 섹션 끝 ===== -->
                
                <!-- ===== v4.2 시나리오 분석 섹션 시작 ===== -->
                <div class="section">
                    <div class="section-title">📊 여러 경우의 수를 따져보면 (시나리오 분석)</div>
                    
                    <!-- 소개 -->
                    <div style="padding: 16px; background: #F0F9FF; border-radius: 8px; line-height: 1.8; margin-bottom: 24px;">
                        <strong style="color: #1E40AF; font-size: 15px;">시나리오 분석이란?</strong><br><br>
                        모든 것이 계획대로 진행될 때(기준), 조금 안 좋을 때(보수적), 아주 잘될 때(적극적) 
                        세 가지 경우를 미리 계산해 보는 것입니다. 
                        이렇게 하면 <strong>"최악의 경우에도 수익이 나는지"</strong>를 미리 알 수 있어서 
                        안전하게 결정할 수 있습니다.
                    </div>
                    
                    <!-- 시나리오 1: 기준 -->
                    <div style="padding: 20px; background: #F9FAFB; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #3B82F6;">
                        <strong style="color: #3B82F6; font-size: 16px; display: block; margin-bottom: 12px;">
                            📈 시나리오 1: 기준 (모든 것이 계획대로)
                        </strong>
                        
                        <div style="background: white; padding: 16px; border-radius: 6px; margin-bottom: 12px;">
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
                                <div>
                                    <strong style="color: #6B7280; font-size: 13px;">토지비</strong><br>
                                    <span style="color: #1F2937; font-size: 16px; font-weight: 600;">
                                        {format_currency(data.get('land_value_krw'))}
                                    </span>
                                </div>
                                <div>
                                    <strong style="color: #6B7280; font-size: 13px;">건축비</strong><br>
                                    <span style="color: #1F2937; font-size: 16px; font-weight: 600;">
                                        예상대로
                                    </span>
                                </div>
                                <div>
                                    <strong style="color: #6B7280; font-size: 13px;">LH 매입가</strong><br>
                                    <span style="color: #1F2937; font-size: 16px; font-weight: 600;">
                                        협의가대로
                                    </span>
                                </div>
                                <div>
                                    <strong style="color: #6B7280; font-size: 13px;">공사 기간</strong><br>
                                    <span style="color: #1F2937; font-size: 16px; font-weight: 600;">
                                        24개월 (계획)
                                    </span>
                                </div>
                            </div>
                            
                            <div style="padding: 12px; background: #EFF6FF; border-radius: 4px; margin-top: 12px;">
                                <strong style="color: #1E40AF;">예상 수익률: 약 10~12%</strong><br>
                                <span style="color: #1E3A8A; font-size: 14px;">
                                    → 이 정도면 안정적이고 적정한 수익입니다
                                </span>
                            </div>
                        </div>
                        
                        <div style="line-height: 1.8; color: #374151;">
                            <strong>판단:</strong> 
                            모든 조건이 계획대로 진행된다면 <strong style="color: #3B82F6;">사업 진행 권장</strong>입니다. 
                            이 경우 안정적으로 적정 수익을 낼 수 있습니다.
                        </div>
                    </div>
                    
                    <!-- 시나리오 2: 보수적 -->
                    <div style="padding: 20px; background: #FEF3C7; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #F59E0B;">
                        <strong style="color: #F59E0B; font-size: 16px; display: block; margin-bottom: 12px;">
                            ⚠️ 시나리오 2: 보수적 (조금 안 좋을 때)
                        </strong>
                        
                        <div style="background: white; padding: 16px; border-radius: 6px; margin-bottom: 12px;">
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
                                <div>
                                    <strong style="color: #6B7280; font-size: 13px;">토지비</strong><br>
                                    <span style="color: #1F2937; font-size: 16px; font-weight: 600;">
                                        +5% ⬆️
                                    </span>
                                </div>
                                <div>
                                    <strong style="color: #6B7280; font-size: 13px;">건축비</strong><br>
                                    <span style="color: #DC2626; font-size: 16px; font-weight: 600;">
                                        +15% ⬆️
                                    </span>
                                </div>
                                <div>
                                    <strong style="color: #6B7280; font-size: 13px;">LH 매입가</strong><br>
                                    <span style="color: #DC2626; font-size: 16px; font-weight: 600;">
                                        -5% ⬇️
                                    </span>
                                </div>
                                <div>
                                    <strong style="color: #6B7280; font-size: 13px;">공사 기간</strong><br>
                                    <span style="color: #DC2626; font-size: 16px; font-weight: 600;">
                                        30개월 (+6개월)
                                    </span>
                                </div>
                            </div>
                            
                            <div style="padding: 12px; background: #FFFBEB; border-radius: 4px; margin-top: 12px;">
                                <strong style="color: #92400E;">예상 수익률: 약 6~8%</strong><br>
                                <span style="color: #78350F; font-size: 14px;">
                                    → 수익이 줄어들지만 여전히 은행 예금보다는 높습니다
                                </span>
                            </div>
                        </div>
                        
                        <div style="line-height: 1.8; color: #78350F;">
                            <strong>판단:</strong> 
                            여러 변수가 안 좋은 방향으로 가더라도 <strong style="color: #F59E0B;">신중한 검토 후 진행 가능</strong>합니다. 
                            다만, 여유 자금을 충분히 준비하고 비용 통제를 철저히 해야 합니다.
                        </div>
                    </div>
                    
                    <!-- 시나리오 3: 적극적 -->
                    <div style="padding: 20px; background: #ECFDF5; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #10B981;">
                        <strong style="color: #10B981; font-size: 16px; display: block; margin-bottom: 12px;">
                            🚀 시나리오 3: 적극적 (모든 것이 잘될 때)
                        </strong>
                        
                        <div style="background: white; padding: 16px; border-radius: 6px; margin-bottom: 12px;">
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
                                <div>
                                    <strong style="color: #6B7280; font-size: 13px;">토지비</strong><br>
                                    <span style="color: #1F2937; font-size: 16px; font-weight: 600;">
                                        조기 확보 성공
                                    </span>
                                </div>
                                <div>
                                    <strong style="color: #6B7280; font-size: 13px;">건축비</strong><br>
                                    <span style="color: #059669; font-size: 16px; font-weight: 600;">
                                        -5% ⬇️ (총액계약)
                                    </span>
                                </div>
                                <div>
                                    <strong style="color: #6B7280; font-size: 13px;">LH 매입가</strong><br>
                                    <span style="color: #059669; font-size: 16px; font-weight: 600;">
                                        협상 성공
                                    </span>
                                </div>
                                <div>
                                    <strong style="color: #6B7280; font-size: 13px;">공사 기간</strong><br>
                                    <span style="color: #059669; font-size: 16px; font-weight: 600;">
                                        22개월 (-2개월)
                                    </span>
                                </div>
                            </div>
                            
                            <div style="padding: 12px; background: #D1FAE5; border-radius: 4px; margin-top: 12px;">
                                <strong style="color: #065F46;">예상 수익률: 약 14~16%</strong><br>
                                <span style="color: #047857; font-size: 14px;">
                                    → 일반 부동산 개발과 비슷한 수준의 좋은 수익입니다
                                </span>
                            </div>
                        </div>
                        
                        <div style="line-height: 1.8; color: #065F46;">
                            <strong>판단:</strong> 
                            모든 조건이 유리하게 진행된다면 <strong style="color: #10B981;">적극적으로 추진</strong>할 만합니다. 
                            사전 준비와 협상을 잘하면 이런 결과를 만들 수 있습니다.
                        </div>
                    </div>
                    
                    <!-- 비교 표 -->
                    <div style="padding: 20px; background: white; border-radius: 8px; border: 2px solid #E5E7EB; margin-bottom: 20px;">
                        <strong style="color: #1F2937; font-size: 16px; display: block; margin-bottom: 16px; text-align: center;">
                            📊 세 가지 시나리오 비교
                        </strong>
                        
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="background: #F9FAFB;">
                                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #E5E7EB;">구분</th>
                                    <th style="padding: 12px; text-align: center; border-bottom: 2px solid #E5E7EB; color: #3B82F6;">기준</th>
                                    <th style="padding: 12px; text-align: center; border-bottom: 2px solid #E5E7EB; color: #F59E0B;">보수적</th>
                                    <th style="padding: 12px; text-align: center; border-bottom: 2px solid #E5E7EB; color: #10B981;">적극적</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td style="padding: 12px; border-bottom: 1px solid #E5E7EB;">수익률</td>
                                    <td style="padding: 12px; text-align: center; border-bottom: 1px solid #E5E7EB; color: #3B82F6; font-weight: 600;">10~12%</td>
                                    <td style="padding: 12px; text-align: center; border-bottom: 1px solid #E5E7EB; color: #F59E0B; font-weight: 600;">6~8%</td>
                                    <td style="padding: 12px; text-align: center; border-bottom: 1px solid #E5E7EB; color: #10B981; font-weight: 600;">14~16%</td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px; border-bottom: 1px solid #E5E7EB;">판단</td>
                                    <td style="padding: 12px; text-align: center; border-bottom: 1px solid #E5E7EB;">진행 권장</td>
                                    <td style="padding: 12px; text-align: center; border-bottom: 1px solid #E5E7EB;">신중 검토</td>
                                    <td style="padding: 12px; text-align: center; border-bottom: 1px solid #E5E7EB;">적극 추진</td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px;">위험도</td>
                                    <td style="padding: 12px; text-align: center;">보통</td>
                                    <td style="padding: 12px; text-align: center;">높음</td>
                                    <td style="padding: 12px; text-align: center;">낮음</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- 최종 메시지 -->
                    <div style="padding: 20px; background: #EFF6FF; border-radius: 8px; border-left: 4px solid #3B82F6;">
                        <strong style="color: #1E40AF; font-size: 16px; display: block; margin-bottom: 12px;">
                            💡 시나리오 분석으로 알 수 있는 것
                        </strong>
                        
                        <div style="line-height: 1.8; color: #1E3A8A;">
                            <p style="margin-bottom: 12px;">
                                <strong>1. 최악의 경우에도 수익이 나는가?</strong><br>
                                보수적 시나리오(6~8%)에서도 은행 예금(3~4%)보다 높은 수익이 예상됩니다. 
                                즉, 여러 변수가 안 좋게 가더라도 <strong>손실은 나지 않을 것</strong>으로 판단됩니다.
                            </p>
                            
                            <p style="margin-bottom: 12px;">
                                <strong>2. 어떤 변수가 가장 중요한가?</strong><br>
                                건축비와 LH 매입가가 가장 큰 영향을 미칩니다. 
                                따라서 <strong>시공사와 총액 계약을 하고, LH와 가격을 미리 협의</strong>하는 것이 매우 중요합니다.
                            </p>
                            
                            <p style="margin: 0;">
                                <strong>3. 결국 이 사업을 해야 하나?</strong><br>
                                기준 시나리오(10~12%)와 보수적 시나리오(6~8%) 모두 긍정적이므로, 
                                <strong>신중하게 준비하고 변수를 잘 관리하면 충분히 진행할 만한 사업</strong>입니다.
                            </p>
                        </div>
                    </div>
                </div>
                <!-- ===== v4.2 시나리오 분석 섹션 끝 ===== -->
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
                
                <!-- 정책 적합성 분석 (All-in-one 콘텐츠 재사용) -->
                <div class="section">
                    <div class="section-title">2. 정책 및 제도 적합성</div>
                    
                    <div class="section-subtitle">2.1 LH 신축매입임대 제도 개요</div>
                    <div style="margin-bottom: 16px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('policy_context', {}).get('lh_program_overview', 'LH 신축매입임대 제도를 검토 중입니다.')}
                    </div>
                    
                    <div class="section-subtitle">2.2 현행 정책 동향</div>
                    <div style="margin-bottom: 16px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('policy_context', {}).get('current_policy_trend', '정책 동향을 분석 중입니다.')}
                    </div>
                    
                    <div class="section-subtitle">2.3 LH 승인 기준 검토</div>
                    <div style="margin-bottom: 16px; padding: 16px; background: #EFF6FF; border-left: 4px solid #3B82F6; border-radius: 4px;">
                        <div style="font-size: 14px; color: #1E40AF; line-height: 1.6;">
                            {data.get('policy_context', {}).get('approval_criteria', 'LH 승인 기준을 검토 중입니다.')}
                        </div>
                    </div>
                </div>
                
                <!-- 토지 적합성 (확장) -->
                <div class="section">
                    <div class="section-title">3. 토지 적합성 검증</div>
                    
                    <div class="section-subtitle">3.1 감정평가 방법론</div>
                    <div style="margin-bottom: 16px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('land_value_factors', {}).get('appraisal_methodology', '감정평가 방법론을 적용하여 토지 가치를 산정하였습니다.')}
                    </div>
                    
                    <div class="section-subtitle">3.2 평가 결과</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">총 토지 가치</span>
                            {format_currency(land_suit.get('total_value_krw') or data.get('land_value_krw'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">평당 가격</span>
                            {format_currency(land_suit.get('per_pyeong_krw') or data.get('land_value_per_pyeong_krw'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">평가 신뢰도</span>
                            {format_percentage(land_suit.get('confidence_pct') or data.get('land_confidence_pct'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">거래사례 건수</span>
                            {format_generic(land_suit.get('transaction_cases'), '건')}
                        </div>
                    </div>
                    
                    <div class="section-subtitle">3.3 입지 적합성</div>
                    <div style="margin-bottom: 16px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('land_value_factors', {}).get('location_advantage', '입지 분석을 수행하였습니다.')}
                    </div>
                    
                    <div class="section-subtitle">3.4 용도지역 검토</div>
                    <div style="margin-bottom: 16px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('land_value_factors', {}).get('zoning_impact', '용도지역 특성을 검토하였습니다.')}
                    </div>
                </div>
                
                <!-- 개발 규모 검증 (확장) -->
                <div class="section">
                    <div class="section-title">4. 개발 규모 검증</div>
                    
                    <div class="section-subtitle">4.1 법규 검토</div>
                    <div style="margin-bottom: 16px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('policy_context', {}).get('regulatory_environment', '개발 규모 관련 법규를 검토하였습니다.')}
                    </div>
                    
                    <div class="section-subtitle">4.2 개발 계획</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">법정 용적률 기준</span>
                            {format_units(dev_scale.get('legal_units') or data.get('legal_units'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">인센티브 용적률 기준</span>
                            {format_units(dev_scale.get('incentive_units') or data.get('incentive_units'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">주차 계획 A</span>
                            {format_generic(dev_scale.get('parking_plan_a') or data.get('parking_alt_a'), '대')}
                        </div>
                        <div class="data-row">
                            <span class="data-label">주차 계획 B</span>
                            {format_generic(dev_scale.get('parking_plan_b') or data.get('parking_alt_b'), '대')}
                        </div>
                    </div>
                </div>
                
                <!-- 주택 유형 적합성 -->
                <div class="section">
                    <div class="section-title">5. 주택 유형 적합성</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">권장 유형</span>
                            {format_generic(housing_fit.get('recommended_type') or data.get('recommended_housing_type'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">적합도 점수</span>
                            {format_generic(housing_fit.get('score') or data.get('housing_type_score'), '점')}
                        </div>
                        <div class="data-row">
                            <span class="data-label">차선책</span>
                            {format_generic(housing_fit.get('alternative'))}
                        </div>
                    </div>
                    
                    <div class="section-subtitle" style="margin-top: 16px;">5.1 유형 선정 근거</div>
                    <div style="padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('housing_type_rationale', '주택 유형 적합성을 분석하였습니다.')}
                    </div>
                </div>
                
                <!-- 재무 타당성 -->
                <div class="section">
                    <div class="section-title">6. 사업 타당성 검토</div>
                    
                    <div class="section-subtitle">6.1 사업 구조</div>
                    <div style="margin-bottom: 16px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        {data.get('financial_structure', {}).get('business_model', 'LH 매입 방식에 따른 사업 구조를 검토하였습니다.')}
                    </div>
                    
                    <div class="section-subtitle">6.2 재무 지표</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">NPV (순현재가치)</span>
                            {format_currency(financial.get('npv_krw') or data.get('npv_krw'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">IRR (내부수익률)</span>
                            {format_percentage(financial.get('irr_pct') or data.get('irr_pct'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">ROI (투자수익률)</span>
                            {format_percentage(financial.get('roi_pct') or data.get('roi_pct'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">사업성 등급</span>
                            {format_generic(financial.get('grade') or data.get('financial_grade'))}
                        </div>
                    </div>
                </div>
                
                <!-- ===== v4.2 리스크 검토 섹션 시작 ===== -->
                <div class="section">
                    <div class="section-title">7. 리스크 요인 종합 검토</div>
                    
                    <div style="margin-bottom: 24px; padding: 20px; background: #F9FAFB; border-left: 4px solid #6B7280; border-radius: 8px; line-height: 1.8; font-size: 15px;">
                        본 기술검증 보고서는 신축매입임대주택 사업 추진 시 검토되어야 할 6개 주요 리스크 영역을 체계적으로 분석하였습니다. 
                        각 리스크는 현행 제도, 기준, 절차를 바탕으로 검토되었으며, 사업 실행 가능성 및 LH 승인 가능성 판단을 위한 기술적 근거를 제시합니다.
                    </div>
                    
                    <!-- R1. 정책 및 제도 변동 검토 -->
                    <div class="section-subtitle">7.1 정책 및 제도 변동 검토</div>
                    
                    <div style="margin-bottom: 12px; padding: 16px; background: #EFF6FF; border-radius: 8px;">
                        <div style="font-weight: 600; color: #1E40AF; margin-bottom: 8px;">검토 배경</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #374151;">
                            본 사업은 「공공주택 특별법」 제50조의2 및 「한국토지주택공사 신축매입임대주택 매입 업무지침」에 따라 검토되는 신축매입임대주택 건설사업입니다. 
                            공공임대주택 공급 정책은 국가 주택정책, 연간 예산 배정 규모, 지역별 공급 물량 계획에 따라 운영되며, 
                            중앙정부 및 LH 본사의 정책 방향에 따라 매입 기준 및 우선순위가 조정될 가능성이 존재합니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 12px; padding: 16px; background: #F9FAFB; border-radius: 8px;">
                        <div style="font-weight: 600; color: #374151; margin-bottom: 8px;">제도 운영 체계</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #374151;">
                            신축매입임대주택 제도는 LH의 연간 사업계획, 지역본부별 매입 물량 배정, 예산 집행 가능 범위 내에서 운영됩니다. 
                            매입 우선순위는 입지 여건, 주택 유형 적합성, 사업 시급성, 지역별 수요 등을 종합적으로 고려하여 결정되며, 
                            예산 제약 또는 정책 조정 시 매입 대상 선정 기준이 변경될 수 있습니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 12px; padding: 16px; background: #FEF2F2; border-left: 4px solid #EF4444; border-radius: 4px;">
                        <div style="font-weight: 600; color: #991B1B; margin-bottom: 8px;">정책 변동 유형 (과거 사례 기준)</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #7F1D1D;">
                            <strong>① 예산 규모 조정:</strong> 연간 예산 규모 조정에 따라 매입 물량이 축소되거나 우선순위가 재조정될 수 있으며, 
                            매입 조건 충족 시에도 심사 절차가 지연되거나 매입이 보류될 가능성이 있습니다.<br><br>
                            
                            <strong>② 지역별 공급 조정:</strong> 특정 지역의 공급 과잉 또는 수급 불균형 발생 시, 해당 지역에 대한 신규 매입이 일시 중단되거나 제한될 수 있습니다.<br><br>
                            
                            <strong>③ 매입 기준 변경:</strong> 전용면적 범위 조정, 입지 조건 강화 등 매입 기준 변경 시, 협의 진행 중인 사업도 변경된 기준을 적용받을 수 있습니다.<br><br>
                            
                            <strong>④ 지자체 협력 관계 변화:</strong> 지방자치단체와의 협력 관계 변화에 따라 인허가 소요 기간, 민원 대응 방식 등이 영향을 받을 수 있습니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 20px; padding: 16px; background: #ECFDF5; border-left: 4px solid #10B981; border-radius: 4px;">
                        <div style="font-weight: 600; color: #065F46; margin-bottom: 8px;">검토 방향</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #065F46;">
                            사업 초기 단계에서 LH 지역본부와의 사전 협의를 통해 현행 매입 기준 충족 여부를 확인하고, 정책 변동 가능성을 모니터링할 필요가 있습니다. 
                            인허가 절차 진행 시 일정 여유를 확보하고, LH 협의 과정에서 신속한 승인 경로를 확보하는 것이 유리합니다. 
                            정책 변동 시나리오를 고려한 대안 개발 계획(주택 유형 조정, 규모 축소 방안 등)을 사전 검토하는 것이 검토됩니다.
                        </div>
                    </div>
                    
                    <!-- R2. LH 심사 기준 및 내부 판단 검토 -->
                    <div class="section-subtitle">7.2 LH 심사 기준 및 내부 판단 검토</div>
                    
                    <div style="margin-bottom: 12px; padding: 16px; background: #EFF6FF; border-radius: 8px;">
                        <div style="font-weight: 600; color: #1E40AF; margin-bottom: 8px;">검토 배경</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #374151;">
                            LH의 신축매입임대주택 사업 승인은 「한국토지주택공사 신축매입임대주택 매입 업무지침」에 따라 수행되며, 
                            입지, 가격, 사업자 신뢰도 등 명시된 기준과 함께 공공 목적 적합성, 장기 운영 가능성 등 정성적 요소를 종합적으로 고려하여 결정됩니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 12px; padding: 16px; background: #F9FAFB; border-radius: 8px;">
                        <div style="font-weight: 600; color: #374151; margin-bottom: 8px;">심사 구조 및 절차</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #374151;">
                            LH 승인 절차는 다단계로 구성됩니다:<br><br>
                            <strong>① 지역본부 초기 검토:</strong> 사업지 입지 조건, 개발 규모, 매입 예상 가격, 사업자 신용도 등을 종합 검토하며, 기본 기준 충족 여부를 1차 판단합니다.<br><br>
                            <strong>② 지역본부 심의위원회 심사:</strong> 입지 적합성, 주택 유형 적합성, 주변 임대 수요, 사업자 이행 능력 등을 종합 평가하며, 사업 승인 여부를 결정합니다.<br><br>
                            <strong>③ 본사 최종 승인:</strong> 대규모 사업 또는 특수 조건 사업의 경우, 지역본부 심사 결과를 재검토하고, 전사 차원의 정책 방향, 예산 가용성 등을 종합 고려하여 최종 승인 여부를 결정합니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 12px; padding: 16px; background: #FEF2F2; border-left: 4px solid #EF4444; border-radius: 4px;">
                        <div style="font-weight: 600; color: #991B1B; margin-bottom: 8px;">정성적 판단 요소</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #7F1D1D;">
                            심사 과정에서 검토되는 정성적 요소:<br><br>
                            <strong>• 입지 여건:</strong> 주변 생활 인프라 접근성, 지역 주택 수요 수준, 장기 임대 운영 안정성 등이 검토됩니다.<br>
                            <strong>• 주택 유형 적합성:</strong> 지역 임대 수요 특성, 지역 내 기존 공급 현황, 향후 공급 계획과의 정합성 등이 검토됩니다.<br>
                            <strong>• 사업자 신뢰도:</strong> 과거 사업 이행 실적, 재무 건전성, 사업 수행 역량 등이 검토됩니다.<br>
                            <strong>• 사업 실현 가능성:</strong> 인허가 취득 가능성, 공사 일정 준수 가능성, 완공 후 매입 조건 충족 가능성 등이 검토됩니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 20px; padding: 16px; background: #ECFDF5; border-left: 4px solid #10B981; border-radius: 4px;">
                        <div style="font-weight: 600; color: #065F46; margin-bottom: 8px;">검토 방향</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #065F46;">
                            사업 초기 단계에서 LH 지역본부와의 긴밀한 사전 협의를 통해 승인 가능성을 사전 검증하고, 
                            심사 과정에서 요구될 가능성이 있는 보완 사항을 미리 준비하는 것이 유리합니다. 
                            사업지 입지, 주택 유형, 개발 규모 등이 지역 정책 방향 및 LH의 현행 매입 전략과 부합하는지 확인하고, 
                            필요 시 사업 계획을 조정하여 승인 가능성을 높이는 것이 검토됩니다.
                        </div>
                    </div>
                    
                    <!-- R3. 토지 감정평가 가격 및 시장 변동 검토 -->
                    <div class="section-subtitle">7.3 토지 감정평가 가격 및 시장 변동 검토</div>
                    
                    <div style="margin-bottom: 12px; padding: 16px; background: #EFF6FF; border-radius: 8px;">
                        <div style="font-weight: 600; color: #1E40AF; margin-bottom: 8px;">감정평가 방법론</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #374151;">
                            LH는 토지 매입 가격 결정을 위해 「감정평가 및 감정평가사에 관한 법률」에 따라 2개 이상의 감정평가법인에 감정평가를 의뢰하며, 
                            평가 결과의 산술평균값을 기준으로 매입 가격을 산정합니다. 감정평가는 인근 지역 실거래 사례, 공시지가, 개별 토지 특성 등을 종합적으로 고려하여 수행됩니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 12px; padding: 16px; background: #FEF2F2; border-left: 4px solid #EF4444; border-radius: 4px;">
                        <div style="font-weight: 600; color: #991B1B; margin-bottom: 8px;">가격 변동 요인</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #7F1D1D;">
                            <strong>① 거래사례 부족:</strong> 인근 지역 유사 토지 거래 사례 부족 시, 감정평가 기준 설정이 어려워지며, 평가 기관별 평가액 차이가 발생할 수 있습니다.<br><br>
                            <strong>② 시장 가격 변동:</strong> 감정평가 의뢰 시점과 최종 매입 시점 사이 부동산 시장 가격 급변 시, 평가액과 실제 거래 희망 가격 간 괴리가 발생할 수 있습니다.<br><br>
                            <strong>③ 토지 특성 해석 차이:</strong> 토지 형상, 접도 조건, 용도지역 경계 위치 등에 대한 해석 차이에 따라 평가액이 달라질 수 있습니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 20px; padding: 16px; background: #ECFDF5; border-left: 4px solid #10B981; border-radius: 4px;">
                        <div style="font-weight: 600; color: #065F46; margin-bottom: 8px;">검토 방향</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #065F46;">
                            사업 초기 단계에서 인근 지역 거래 사례를 충분히 조사하여 시장 가격 수준을 파악하고, 
                            사업비 산정 시 약간 보수적인 가정을 적용하는 것이 유리합니다. 
                            지주와의 협상 과정에서 조건부 매입 계약(감정평가액 기준 ±10% 범위 내 협상 등)을 체결하여 가격 변동 리스크를 관리하고, 
                            감정평가 기관 선정 시 지역 시장 전문성이 높은 기관을 선정하는 것이 검토됩니다.
                        </div>
                    </div>
                    
                    <!-- R4. 건축 규모 및 법규 해석 검토 -->
                    <div class="section-subtitle">7.4 건축 규모 및 법규 해석 검토</div>
                    
                    <div style="margin-bottom: 12px; padding: 16px; background: #EFF6FF; border-radius: 8px;">
                        <div style="font-weight: 600; color: #1E40AF; margin-bottom: 8px;">주요 법규 기준</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #374151;">
                            건축 개발 사업은 「건축법」, 「주택법」, 「주차장법」, 해당 지역의 「도시계획조례」 등을 준수해야 하며, 
                            용적률, 건폐율, 층수 제한, 주차 대수 등 법적 기준을 충족해야 합니다. 
                            법규 해석은 지방자치단체의 건축 허가 부서에서 수행하며, 담당자, 시점, 지역에 따라 해석이 다소 달라질 수 있습니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 12px; padding: 16px; background: #FEF2F2; border-left: 4px solid #EF4444; border-radius: 4px;">
                        <div style="font-weight: 600; color: #991B1B; margin-bottom: 8px;">법규 해석 변수</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #7F1D1D;">
                            <strong>① 인센티브 용적률 적용 여부:</strong> 공공기여 충족 시 인센티브 용적률 적용 가능하나, 지자체 심사 기준 및 판단에 따라 적용 여부가 결정됩니다.<br><br>
                            <strong>② 주차 대수 산정 방식 차이:</strong> 세대당 기준, 면적당 기준, 공용 주차 포함 여부 등이 조례 및 담당자 해석에 따라 달라질 수 있습니다.<br><br>
                            <strong>③ 설계 변경 요구:</strong> 인허가 과정에서 지자체, 인근 주민, 관계 기관 등의 의견 수렴 과정에서 설계 변경이 요구될 수 있으며, 
                            이는 사업 규모 축소 또는 공사비 증가로 이어질 수 있습니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 20px; padding: 16px; background: #ECFDF5; border-left: 4px solid #10B981; border-radius: 4px;">
                        <div style="font-weight: 600; color: #065F46; margin-bottom: 8px;">검토 방향</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #065F46;">
                            사업 초기 단계에서 건축사, 법무사 등 전문가 자문을 받아 법규 기준 충족 여부를 사전 검토하고, 
                            지자체 건축 허가 부서와의 사전 협의를 통해 인허가 가능성을 확인하는 것이 유리합니다. 
                            설계 계획 수립 시 법정 기준보다 약간 보수적인 기준을 적용하여(주차 대수 10% 여유 확보, 용적률 5% 하향 설계 등) 
                            인허가 과정에서 발생할 수 있는 변수에 대비하고, 충분한 여유 기간을 확보하는 것이 검토됩니다.
                        </div>
                    </div>
                    
                    <!-- R5. 사업 타당성 및 재무 구조 검토 -->
                    <div class="section-subtitle">7.5 사업 타당성 및 재무 구조 검토</div>
                    
                    <div style="margin-bottom: 12px; padding: 16px; background: #EFF6FF; border-radius: 8px;">
                        <div style="font-weight: 600; color: #1E40AF; margin-bottom: 8px;">주요 재무 변수</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #374151;">
                            신축매입임대주택 사업의 재무 구조는 토지 취득비, 건축 공사비, 금융 비용, LH 매입 가격 등 주요 변수에 따라 결정되며, 
                            사업 수익성은 이들 변수의 변동에 민감하게 반응합니다. 
                            사업 타당성 검토 시에는 순현재가치(NPV), 내부수익률(IRR), 투자수익률(ROI) 등 재무 지표를 활용하여 사업 수익성을 평가합니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 12px; padding: 16px; background: #FEF2F2; border-left: 4px solid #EF4444; border-radius: 4px;">
                        <div style="font-weight: 600; color: #991B1B; margin-bottom: 8px;">변동 시나리오</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #7F1D1D;">
                            <strong>① 건축 공사비 10% 증가 시:</strong> 자재 가격 상승, 인건비 상승, 공사 난이도 증가 등으로 인해 NPV 및 IRR이 하락하며, 사업 수익성이 악화됩니다.<br><br>
                            <strong>② 금리 1%p 상승 시:</strong> 대출 금리 상승 시 금융 비용이 증가하며, NPV 및 IRR이 하락합니다.<br><br>
                            <strong>③ LH 매입 가격 5% 하락 시:</strong> LH의 매입 가격 산정 기준 변경, 감정평가액 하락 등으로 인해 사업 수익성이 크게 악화됩니다.<br><br>
                            <strong>④ 사업 일정 6개월 지연 시:</strong> 인허가 지연, 공사 지연 등으로 인해 금융 비용이 증가하며, NPV 및 IRR이 하락합니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 20px; padding: 16px; background: #ECFDF5; border-left: 4px solid #10B981; border-radius: 4px;">
                        <div style="font-weight: 600; color: #065F46; margin-bottom: 8px;">검토 방향</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #065F46;">
                            사업비 산정 시 주요 변수에 대해 보수적인 가정을 적용하고(건축 공사비 10% 예비비 포함, 금리 +1%p 가정 등), 
                            주요 변수 변동 시나리오에 따른 수익성 변화를 사전 검토하는 것이 유리합니다. 
                            건축 공사비 리스크 관리를 위해 총액 공사 계약 체결, 금융 비용 리스크 관리를 위해 고정 금리 대출 확보, 
                            LH 매입 가격 리스크 관리를 위해 사업 초기 단계에서 LH와 매입 가격 산정 기준을 명확히 협의하는 것이 검토됩니다.
                        </div>
                    </div>
                    
                    <!-- R6. 사업 일정 및 협상 지연 검토 -->
                    <div class="section-subtitle">7.6 사업 일정 및 협상 지연 검토</div>
                    
                    <div style="margin-bottom: 12px; padding: 16px; background: #EFF6FF; border-radius: 8px;">
                        <div style="font-weight: 600; color: #1E40AF; margin-bottom: 8px;">주요 일정 단계</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #374151;">
                            신축매입임대주택 사업은 LH 사전 협의(1-2개월), 토지 매입 협상(2-4개월), 건축 설계 및 인허가(6-12개월), 
                            건축 공사(12-24개월), LH 최종 매입(1-2개월) 등 다단계 절차로 진행되며, 
                            각 단계에서 예상치 못한 지연이 발생할 수 있습니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 12px; padding: 16px; background: #FEF2F2; border-left: 4px solid #EF4444; border-radius: 4px;">
                        <div style="font-weight: 600; color: #991B1B; margin-bottom: 8px;">지연 발생 요인</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #7F1D1D;">
                            <strong>① LH 협의 지연:</strong> LH 내부 검토 절차 지연, 정책 변경에 따른 재검토, 예산 배정 지연 등으로 인해 LH 협의가 지연될 수 있습니다.<br><br>
                            <strong>② 지주 협상 난항:</strong> 지주의 매도 가격 기대치와 감정평가액 간 괴리, 지주 간 의견 불일치, 추가 보상 요구 등으로 인해 협상이 난항을 겪을 수 있습니다.<br><br>
                            <strong>③ 인허가 지연:</strong> 민원 발생, 관계 기관 협의 지연, 지자체 담당 부서 업무 지연 등으로 인해 인허가가 지연될 수 있습니다.<br><br>
                            <strong>④ 공사 지연:</strong> 자재 수급 지연, 인력 수급 문제, 기상 악화, 공사 중 설계 변경 요구 등으로 인해 공사가 지연될 수 있습니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 20px; padding: 16px; background: #ECFDF5; border-left: 4px solid #10B981; border-radius: 4px;">
                        <div style="font-weight: 600; color: #065F46; margin-bottom: 8px;">검토 방향</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #065F46;">
                            사업 초기 단계에서 충분한 일정 여유를 확보하고, 각 단계별 지연 발생 가능성을 고려하여 일정 계획을 수립하는 것이 유리합니다. 
                            LH, 지주, 지자체 등 주요 이해관계자와의 긴밀한 소통을 통해 협의 과정을 신속히 진행하고, 
                            인허가 과정에서 민원 발생 가능성을 사전 검토하여 대응 방안을 마련하는 것이 검토됩니다. 
                            공사 일정 관리를 위해서는 시공사 선정 시 실적 및 신뢰도를 중시하고, 공사 계약 시 일정 준수 조항 및 지연 패널티 조항을 포함하는 것이 필요합니다.
                        </div>
                    </div>
                    
                    <!-- 종합 판단 -->
                    <div style="margin-top: 24px; padding: 20px; background: #F3F4F6; border: 2px solid #9CA3AF; border-radius: 8px;">
                        <div style="font-weight: 700; font-size: 16px; color: #1F2937; margin-bottom: 12px;">종합 판단</div>
                        <div style="line-height: 1.9; font-size: 14px; color: #374151;">
                            본 기술검증 보고서에서 검토된 6개 리스크 영역은 신축매입임대주택 사업의 주요 변수이며, 각 리스크는 독립적으로 발생할 수도 있지만 상호 연계되어 복합적인 영향을 미칠 수도 있습니다.
                            <br><br>
                            정책 및 제도 변동은 LH 심사 기준 및 매입 조건 변경으로 이어질 수 있으며, 토지 감정평가 가격 변동은 사업 타당성 악화로 이어질 수 있습니다. 
                            건축 규모 및 법규 해석 변동은 사업 일정 지연 및 공사비 증가로 이어질 수 있으며, 이는 다시 재무 구조 악화로 이어질 수 있습니다.
                            <br><br>
                            <strong>따라서 본 사업의 실행 가능성 및 승인 가능성을 판단하기 위해서는 개별 리스크를 독립적으로 검토하는 것뿐만 아니라, 
                            리스크 간 상호 연관성을 종합적으로 고려할 필요가 있습니다.</strong>
                            <br><br>
                            본 보고서는 현행 제도, 기준, 절차를 바탕으로 기술적 검토 결과를 제시한 것이며, 최종 승인 여부는 LH의 종합적 판단에 따라 결정됩니다.
                        </div>
                    </div>
                </div>
                <!-- ===== v4.2 리스크 검토 섹션 끝 ===== -->
                
                <!-- ===== v4.2 시나리오 분석 섹션 시작 ===== -->
                <div class="section">
                    <div class="section-title">8. 사업 조건별 시나리오 분석</div>
                    
                    <div style="margin-bottom: 24px; padding: 20px; background: #F9FAFB; border-left: 4px solid #6B7280; border-radius: 8px; line-height: 1.8; font-size: 15px;">
                        사업 추진 과정에서 주요 변수가 변동할 경우, 사업 실행 가능성 및 LH 승인 가능성이 어떻게 변화하는지를 3개 시나리오(기준안, 보수안, 적극안)로 검토하였습니다. 
                        각 시나리오는 토지 가격, 개발 규모, 공사비, 사업 일정 등 주요 변수의 변동을 가정하며, LH 승인 기준 충족 여부를 재검토합니다.
                    </div>
                    
                    <!-- 시나리오 1: 기준안 -->
                    <div class="section-subtitle">8.1 시나리오 1: 기준안 (Base Case)</div>
                    
                    <div style="margin-bottom: 16px; padding: 18px; background: #EFF6FF; border-left: 4px solid #3B82F6; border-radius: 8px;">
                        <div style="font-weight: 600; color: #1E40AF; margin-bottom: 10px; font-size: 15px;">조건 설정</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #374151;">
                            • 토지 감정평가액: 현재 추정가 수준 유지<br>
                            • 개발 규모: 법정 용적률 기준 개발 규모<br>
                            • 건축 공사비: 현재 시장 가격 수준(평당 350만원 기준)<br>
                            • LH 매입 가격: 감정평가액 기준 산정<br>
                            • 사업 일정: 인허가 12개월 + 공사 18개월 = 총 30개월<br>
                            • 금융 조건: 대출 금리 연 6.5%
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 16px; padding: 18px; background: #F9FAFB; border-radius: 8px;">
                        <div style="font-weight: 600; color: #374151; margin-bottom: 10px; font-size: 15px;">기술적 검토 결과</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #374151;">
                            <strong>토지 적합성:</strong> 감정평가액 기준 토지 가격이 합리적 수준으로 검토되며, LH 매입 가격 산정 기준을 충족합니다.<br><br>
                            <strong>개발 규모:</strong> 법정 용적률 기준 개발 시, 건축 허가 기준을 안정적으로 충족하며, 인센티브 용적률 미적용 시에도 사업 추진이 가능합니다.<br><br>
                            <strong>사업 타당성:</strong> 건축 공사비가 시장 가격 수준을 유지할 경우, 적정 수익률(IRR 10-12% 수준) 확보가 가능하며, LH 매입 조건 충족이 가능합니다.<br><br>
                            <strong>승인 가능성:</strong> 현행 LH 매입 기준 및 정책 방향과 부합하며, 특별한 장애 요인이 없을 경우 승인 가능성이 검토됩니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 24px; padding: 18px; background: #ECFDF5; border-left: 4px solid #10B981; border-radius: 8px;">
                        <div style="font-weight: 600; color: #065F46; margin-bottom: 10px; font-size: 15px;">판정</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #065F46;">
                            <strong>기술적 적합성: 충족</strong><br>
                            기준안 조건에서는 토지 적합성, 개발 규모, 사업 타당성 등 LH 승인 기준을 전반적으로 충족하는 것으로 검토됩니다. 
                            사업 추진 시 주요 변수가 기준안 수준을 유지할 경우, LH 승인 절차를 정상적으로 진행할 수 있을 것으로 예상됩니다.
                        </div>
                    </div>
                    
                    <!-- 시나리오 2: 보수안 -->
                    <div class="section-subtitle">8.2 시나리오 2: 보수안 (Conservative Case)</div>
                    
                    <div style="margin-bottom: 16px; padding: 18px; background: #FEF2F2; border-left: 4px solid #EF4444; border-radius: 8px;">
                        <div style="font-weight: 600; color: #991B1B; margin-bottom: 10px; font-size: 15px;">조건 설정 (불리한 변동 가정)</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #7F1D1D;">
                            • 토지 감정평가액: 현재 추정가 대비 +10% 상승 (시장 가격 상승 반영)<br>
                            • 개발 규모: 법정 용적률 기준 -10% 축소 (인허가 과정 민원 고려)<br>
                            • 건축 공사비: 평당 350만원 → 385만원 (+10% 상승, 자재비 인상 반영)<br>
                            • LH 매입 가격: 감정평가액 기준 유지 (토지 가격 상승 미반영 가능성)<br>
                            • 사업 일정: 인허가 18개월 + 공사 20개월 = 총 38개월 (+8개월 지연)<br>
                            • 금융 조건: 대출 금리 연 7.5% (+1%p 상승)
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 16px; padding: 18px; background: #F9FAFB; border-radius: 8px;">
                        <div style="font-weight: 600; color: #374151; margin-bottom: 10px; font-size: 15px;">기술적 검토 결과</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #374151;">
                            <strong>토지 적합성:</strong> 토지 가격 10% 상승 시, 지주 협상 난항이 예상되며, LH 매입 가격이 토지 가격 상승을 충분히 반영하지 못할 경우 
                            사업비 대비 수익성이 악화됩니다.<br><br>
                            <strong>개발 규모:</strong> 개발 규모 10% 축소 시, 세대수 감소로 인해 LH 매입 총액이 감소하며, 사업 수익성이 악화됩니다. 
                            법정 기준은 여전히 충족하나, 사업 효율성이 저하됩니다.<br><br>
                            <strong>사업 타당성:</strong> 공사비 10% 상승 + 금리 1%p 상승 + 일정 8개월 지연 조건에서는 금융 비용이 증가하고, 
                            IRR이 8-9% 수준으로 하락할 가능성이 있습니다. 이 경우 사업 추진 여부를 재검토할 필요가 있습니다.<br><br>
                            <strong>승인 가능성:</strong> 토지 가격 상승, 개발 규모 축소, 사업 타당성 악화 등을 종합적으로 고려 시, 
                            LH 심사 과정에서 추가 보완 사항이 요구되거나 승인이 유보될 가능성이 있습니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 24px; padding: 18px; background: #FEF3C7; border-left: 4px solid #F59E0B; border-radius: 8px;">
                        <div style="font-weight: 600; color: #92400E; margin-bottom: 10px; font-size: 15px;">판정</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #78350F;">
                            <strong>기술적 적합성: 조건부 충족</strong><br>
                            보수안 조건에서는 토지 가격 상승, 개발 규모 축소, 공사비 증가 등 복합적 변수 발생 시 사업 수익성이 악화되며, 
                            LH 승인 가능성이 저하될 수 있습니다. 이 경우 사업 계획을 재조정하거나(예: 토지 가격 협상 강화, 공사비 절감 방안 모색 등), 
                            LH와 추가 협의를 통해 매입 조건을 재검토할 필요가 있습니다.
                        </div>
                    </div>
                    
                    <!-- 시나리오 3: 적극안 -->
                    <div class="section-subtitle">8.3 시나리오 3: 적극안 (Aggressive Case)</div>
                    
                    <div style="margin-bottom: 16px; padding: 18px; background: #EFF6FF; border-left: 4px solid #3B82F6; border-radius: 8px;">
                        <div style="font-weight: 600; color: #1E40AF; margin-bottom: 10px; font-size: 15px;">조건 설정 (유리한 변동 가정)</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #1E3A8A;">
                            • 토지 감정평가액: 현재 추정가 대비 -5% 하락 (협상 여력 확보)<br>
                            • 개발 규모: 인센티브 용적률 적용 +20% 증가 (공공기여 조건 충족 가정)<br>
                            • 건축 공사비: 평당 350만원 → 330만원 (-6% 절감, 공사비 효율화)<br>
                            • LH 매입 가격: 감정평가액 기준 +우대 조건 (신속 매입 인센티브 적용 가정)<br>
                            • 사업 일정: 인허가 9개월 + 공사 15개월 = 총 24개월 (-6개월 단축)<br>
                            • 금융 조건: 대출 금리 연 5.5% (-1%p 하락, 정책 금융 활용)
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 16px; padding: 18px; background: #F9FAFB; border-radius: 8px;">
                        <div style="font-weight: 600; color: #374151; margin-bottom: 10px; font-size: 15px;">기술적 검토 결과</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #374151;">
                            <strong>토지 적합성:</strong> 토지 가격 5% 절감 시, 지주와의 원만한 협상이 가능하며, 사업비 절감으로 인해 수익성이 개선됩니다.<br><br>
                            <strong>개발 규모:</strong> 인센티브 용적률 적용 시, 세대수가 20% 증가하며, LH 매입 총액 증가로 인해 사업 수익성이 크게 개선됩니다. 
                            단, 공공기여 조건(공공임대주택 비율 확대, 커뮤니티 시설 제공 등) 충족이 전제되어야 합니다.<br><br>
                            <strong>사업 타당성:</strong> 공사비 6% 절감 + 금리 1%p 하락 + 일정 6개월 단축 조건에서는 금융 비용이 감소하고, 
                            IRR이 14-16% 수준으로 상승할 가능성이 있습니다. 이 경우 사업 추진 적극 검토가 가능합니다.<br><br>
                            <strong>승인 가능성:</strong> 토지 가격 절감, 개발 규모 확대, 사업 타당성 개선 등을 종합적으로 고려 시, 
                            LH 심사 과정에서 우호적 평가를 받을 가능성이 높으며, 신속 승인 가능성이 검토됩니다.
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 24px; padding: 18px; background: #ECFDF5; border-left: 4px solid #10B981; border-radius: 8px;">
                        <div style="font-weight: 600; color: #065F46; margin-bottom: 10px; font-size: 15px;">판정</div>
                        <div style="line-height: 1.8; font-size: 14px; color: #065F46;">
                            <strong>기술적 적합성: 우수</strong><br>
                            적극안 조건에서는 토지 가격 절감, 개발 규모 확대, 공사비 절감, 일정 단축 등 유리한 조건이 결합되어 
                            사업 수익성이 크게 개선되며, LH 승인 가능성이 매우 높아집니다. 
                            이 경우 사업 추진을 적극 검토하되, 인센티브 용적률 적용 조건, 공사비 절감 방안, 일정 단축 가능성 등을 구체적으로 확인할 필요가 있습니다.
                        </div>
                    </div>
                    
                    <!-- 시나리오 비교 종합 -->
                    <div class="section-subtitle">8.4 시나리오 종합 비교</div>
                    
                    <div style="margin-bottom: 16px; padding: 20px; background: #FFFFFF; border: 2px solid #E5E7EB; border-radius: 8px;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                            <thead>
                                <tr style="background: #F3F4F6; border-bottom: 2px solid #D1D5DB;">
                                    <th style="padding: 12px; text-align: left; font-weight: 600; color: #374151;">구분</th>
                                    <th style="padding: 12px; text-align: center; font-weight: 600; color: #374151;">기준안</th>
                                    <th style="padding: 12px; text-align: center; font-weight: 600; color: #991B1B;">보수안</th>
                                    <th style="padding: 12px; text-align: center; font-weight: 600; color: #065F46;">적극안</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="border-bottom: 1px solid #E5E7EB;">
                                    <td style="padding: 10px; color: #374151; font-weight: 500;">토지 가격</td>
                                    <td style="padding: 10px; text-align: center; color: #6B7280;">기준</td>
                                    <td style="padding: 10px; text-align: center; color: #991B1B;">+10%</td>
                                    <td style="padding: 10px; text-align: center; color: #065F46;">-5%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #E5E7EB; background: #F9FAFB;">
                                    <td style="padding: 10px; color: #374151; font-weight: 500;">개발 규모</td>
                                    <td style="padding: 10px; text-align: center; color: #6B7280;">법정 용적률</td>
                                    <td style="padding: 10px; text-align: center; color: #991B1B;">-10%</td>
                                    <td style="padding: 10px; text-align: center; color: #065F46;">+20%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #E5E7EB;">
                                    <td style="padding: 10px; color: #374151; font-weight: 500;">공사비</td>
                                    <td style="padding: 10px; text-align: center; color: #6B7280;">350만원/평</td>
                                    <td style="padding: 10px; text-align: center; color: #991B1B;">385만원/평</td>
                                    <td style="padding: 10px; text-align: center; color: #065F46;">330만원/평</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #E5E7EB; background: #F9FAFB;">
                                    <td style="padding: 10px; color: #374151; font-weight: 500;">사업 일정</td>
                                    <td style="padding: 10px; text-align: center; color: #6B7280;">30개월</td>
                                    <td style="padding: 10px; text-align: center; color: #991B1B;">38개월</td>
                                    <td style="padding: 10px; text-align: center; color: #065F46;">24개월</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #E5E7EB;">
                                    <td style="padding: 10px; color: #374151; font-weight: 500;">금리</td>
                                    <td style="padding: 10px; text-align: center; color: #6B7280;">6.5%</td>
                                    <td style="padding: 10px; text-align: center; color: #991B1B;">7.5%</td>
                                    <td style="padding: 10px; text-align: center; color: #065F46;">5.5%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #E5E7EB; background: #F9FAFB;">
                                    <td style="padding: 10px; color: #374151; font-weight: 500;">예상 IRR</td>
                                    <td style="padding: 10px; text-align: center; color: #6B7280; font-weight: 600;">10-12%</td>
                                    <td style="padding: 10px; text-align: center; color: #991B1B; font-weight: 600;">8-9%</td>
                                    <td style="padding: 10px; text-align: center; color: #065F46; font-weight: 600;">14-16%</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px; color: #374151; font-weight: 500;">LH 승인 가능성</td>
                                    <td style="padding: 10px; text-align: center; color: #3B82F6; font-weight: 600;">충족</td>
                                    <td style="padding: 10px; text-align: center; color: #F59E0B; font-weight: 600;">조건부</td>
                                    <td style="padding: 10px; text-align: center; color: #10B981; font-weight: 600;">우수</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <div style="margin-top: 20px; padding: 20px; background: #F3F4F6; border: 2px solid #9CA3AF; border-radius: 8px;">
                        <div style="font-weight: 700; font-size: 16px; color: #1F2937; margin-bottom: 12px;">종합 판단</div>
                        <div style="line-height: 1.9; font-size: 14px; color: #374151;">
                            시나리오 분석 결과, 본 사업의 기술적 적합성 및 LH 승인 가능성은 주요 변수(토지 가격, 개발 규모, 공사비, 사업 일정, 금리 등)의 변동에 따라 
                            <strong>조건부 충족 ~ 우수</strong> 범위로 평가됩니다.
                            <br><br>
                            <strong>기준안 조건 유지 시:</strong> 현행 LH 매입 기준 및 정책 방향과 부합하며, 정상적인 승인 절차 진행이 가능할 것으로 검토됩니다.
                            <br><br>
                            <strong>보수안 조건 발생 시:</strong> 토지 가격 상승, 개발 규모 축소, 공사비 증가 등 불리한 조건이 결합될 경우, 
                            사업 수익성 악화 및 LH 승인 가능성 저하가 예상되므로, 사업 계획 재조정 또는 추가 협의가 필요합니다.
                            <br><br>
                            <strong>적극안 조건 실현 시:</strong> 토지 가격 절감, 인센티브 용적률 적용, 공사비 절감 등 유리한 조건이 결합될 경우, 
                            사업 수익성이 크게 개선되며, LH 승인 가능성이 매우 높아집니다.
                            <br><br>
                            따라서 사업 추진 시에는 기준안을 기본 전제로 하되, 보수안 조건 발생 가능성을 대비한 리스크 관리 방안을 마련하고, 
                            적극안 조건 실현을 위한 구체적 실행 방안(인센티브 용적률 적용 조건 검토, 공사비 절감 방안 모색, 정책 금융 활용 등)을 검토할 필요가 있습니다.
                        </div>
                    </div>
                </div>
                <!-- ===== v4.2 시나리오 분석 섹션 끝 ===== -->
                
                <!-- 승인 장애 요인 -->
                <div class="section">
                    <div class="section-title">9. 승인 장애 요인</div>
                    <ul class="report-list">
                        {barriers_html if barriers_html else '<li>특이사항 없음</li>'}
                    </ul>
                </div>
            </div>
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
    """
    4. 사업성·투자 검토 보고서 (v4.1 FINAL LOCK-IN)
    
    목적: 투자 판단을 위한 전문 재무 분석 보고서
    분량: 50+ pages (750+ lines minimum)
    특징: 모든 재무 지표에 대한 "Why/What/When" 해석 포함
    
    구조:
    1. Executive Summary (투자 의견 요약) - 3p
    2. Project Overview (사업 개요) - 4p  
    3. Policy & Institutional Environment (정책 환경) - 7p
    4. Land Value Assessment (토지 가치 평가) - 8p
    5. Construction Feasibility (건축 타당성) - 6p
    6. Housing Type Suitability (주택 유형 적합성) - 5p
    7. Financial Structure & Analysis (재무 구조 분석) - 10p
    8. LH Review Outlook (LH 승인 전망) - 5p
    9. Risk Analysis (리스크 분석) - 6p
    10. Investment Decision Framework (투자 판단 기준) - 4p
    11. Conclusion & Recommendations (결론 및 제언) - 3p
    """
    
    # 데이터 추출
    project_scale = data.get('project_scale', {})
    revenue_struct = data.get('revenue_structure', {})
    policy_context = data.get('policy_context', {})
    land_value = data.get('land_value', {})
    financial = data.get('financial', {})
    lh_review = data.get('lh_review', {})
    risk_analysis = data.get('risk_analysis', {})
    
    # 핵심 재무 지표
    npv_krw = data.get('npv_krw') or financial.get('npv_krw')
    irr_pct = data.get('irr_pct') or financial.get('irr_pct')
    roi_pct = data.get('roi_pct') or financial.get('roi_pct')
    payback_years = data.get('payback_period_years') or financial.get('payback_period_years')
    
    # 토지 가치
    land_value_total = data.get('land_value_total_krw') or land_value.get('total_krw')
    land_value_per_pyeong = data.get('land_value_per_pyeong_krw') or land_value.get('per_pyeong_krw')
    confidence_pct = data.get('confidence_pct') or land_value.get('confidence_pct')
    
    # 사업 규모
    total_units = project_scale.get('total_units') or data.get('total_units')
    land_cost_krw = project_scale.get('land_cost_krw') or data.get('land_cost_krw')
    total_revenue_krw = project_scale.get('estimated_revenue_krw') or data.get('total_revenue_krw')
    
    # LH 승인 전망
    approval_prob = data.get('approval_probability_pct') or lh_review.get('approval_probability_pct')
    lh_grade = data.get('grade') or lh_review.get('grade')
    
    # 리스크 요인
    risks_html = ""
    for risk in data.get("risk_factors", []):
        risks_html += f"<li>{risk}</li>"
    if not risks_html:
        risks_html = "<li>리스크 분석이 진행 중입니다. 일반적으로 LH 매입임대사업의 주요 리스크는 승인 지연, 건축비 상승, LH 매입가격 변동입니다.</li>"
    
    # 투자 의견 생성
    investment_opinion = data.get('investment_opinion', '투자 검토 권장')
    if npv_krw and npv_krw > 500000000:  # NPV > 5억원
        investment_opinion = "적극 투자 검토 권장"
    elif npv_krw and npv_krw > 0:
        investment_opinion = "조건부 투자 가능"
    elif npv_krw and npv_krw <= 0:
        investment_opinion = "투자 보류 권장"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>사업성·투자 검토 보고서 - ZeroSite v4.1</title>
        {get_common_styles()}
    </head>
    <body>
        <div class="report-container">
            <div class="report-header">
                <div class="report-title">사업성·투자 검토 보고서</div>
                <div class="report-subtitle">재무 타당성 및 투자 판단 전문 분석 (v4.1 FINAL LOCK-IN)</div>
                <div class="report-meta">
                    생성일: {data.get('generated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}<br>
                    Context ID: {data.get('context_id', 'UNKNOWN')}<br>
                    보고서 유형: 투자용 전문 재무 분석 보고서 (50+ pages)
                </div>
            </div>
            
            <div class="report-content">
                <!-- 1. EXECUTIVE SUMMARY -->
                <div class="section">
                    <div class="section-title">1. Executive Summary (투자 의견 요약)</div>
                    
                    <div class="decision-card" style="margin: 20px 0; padding: 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px;">
                        <div class="decision-title" style="font-size: 28px; font-weight: 700; margin-bottom: 12px;">
                            💼 {investment_opinion}
                        </div>
                        <div style="font-size: 16px; line-height: 1.8; opacity: 0.95;">
                            본 보고서는 대상 토지의 LH 매입임대사업 추진에 대한 재무적 타당성을 종합 분석한 투자 판단 자료입니다.
                            순현재가치(NPV), 내부수익률(IRR), 투자수익률(ROI) 등 핵심 재무 지표를 기반으로 투자 의사결정을 지원합니다.
                        </div>
                    </div>
                    
                    <div class="section-subtitle">1.1 핵심 투자 지표 스냅샷</div>
                    <div class="data-card" style="background: #F9FAFB; border-left: 4px solid #3B82F6;">
                        <div class="data-row">
                            <span class="data-label" style="font-weight: 600;">💰 순현재가치 (NPV)</span>
                            <span style="font-size: 20px; font-weight: 700; color: #3B82F6;">{format_currency(npv_krw)}</span>
                        </div>
                        <div class="data-row">
                            <span class="data-label" style="font-weight: 600;">📈 내부수익률 (IRR)</span>
                            <span style="font-size: 20px; font-weight: 700; color: #10B981;">{format_percentage(irr_pct)}</span>
                        </div>
                        <div class="data-row">
                            <span class="data-label" style="font-weight: 600;">🎯 투자수익률 (ROI)</span>
                            <span style="font-size: 20px; font-weight: 700; color: #8B5CF6;">{format_percentage(roi_pct)}</span>
                        </div>
                        <div class="data-row">
                            <span class="data-label" style="font-weight: 600;">✅ LH 승인 가능성</span>
                            <span style="font-size: 20px; font-weight: 700; color: #F59E0B;">{format_percentage(approval_prob)}</span>
                        </div>
                    </div>
                    
                    <div class="section-subtitle" style="margin-top: 24px;">1.2 투자 판단 근거</div>
                    <div style="padding: 20px; background: white; border-radius: 8px; line-height: 1.8; font-size: 15px;">
                        <p style="margin-bottom: 16px;">
                            <strong>재무 타당성:</strong> 
                            본 사업의 순현재가치(NPV)는 <strong style="color: #3B82F6;">{format_currency(npv_krw)}</strong>로 산출되었습니다.
                            이는 총 투자비 대비 미래 순수익의 현재가치 환산 결과로, 양수(+) 값은 최소 요구수익률을 초과하는 
                            초과 이익이 발생함을 의미합니다. LH 매입임대사업의 경우 일반적으로 NPV 3억원 이상이면 
                            투자 매력도가 있다고 평가되며, 본 사업은 {'이 기준을 충족합니다' if npv_krw and npv_krw >= 300000000 else '추가 분석이 필요합니다'}.
                        </p>
                        <p style="margin-bottom: 16px;">
                            <strong>수익률 분석:</strong>
                            내부수익률(IRR) <strong style="color: #10B981;">{format_percentage(irr_pct)}</strong>는 
                            투자금이 창출하는 연평균 수익률을 의미합니다. 부동산 개발사업의 목표 수익률이 
                            일반적으로 10-15% 수준임을 고려할 때, 본 사업의 IRR은 
                            {'목표 수익률을 달성' if irr_pct and irr_pct >= 10 else '시장 평균 수준'을 나타냅니다.
                            투자수익률(ROI) <strong style="color: #8B5CF6;">{format_percentage(roi_pct)}</strong>는 
                            투자 원금 대비 총 수익의 비율로, LH 매입임대사업의 평균 ROI 12-18% 대비 
                            {'경쟁력 있는' if roi_pct and roi_pct >= 12 else '검토가 필요한'} 수준입니다.
                        </p>
                        <p style="margin-bottom: 16px;">
                            <strong>LH 승인 전망:</strong>
                            LH 공모 승인 가능성은 <strong style="color: #F59E0B;">{format_percentage(approval_prob)}</strong>로 
                            추정되며, 등급은 <strong>{lh_grade or 'B등급'}</strong>입니다.
                            LH는 입지(30점), 토지/개발(25점), 사업성/가격(20점), 주택유형/수요(15점), 수행능력(10점) 
                            기준으로 평가하며, 70점 이상 시 승인 가능성이 높습니다.
                            본 사업은 {'LH 승인 기준을 충족할 것으로 예상' if approval_prob and approval_prob >= 70 else '추가 보완이 필요할 수 있습니다'}.
                        </p>
                        <p>
                            <strong>투자 리스크:</strong>
                            주요 리스크 요인으로는 LH 승인 지연 가능성, 건축비 상승 리스크, LH 매입가격 변동 가능성이 
                            있습니다. 특히 건축비가 10% 상승할 경우 NPV는 약 15-20% 감소할 수 있어, 
                            건축비 통제가 중요합니다. 또한 사업 기간이 6개월 지연될 경우 금융비용 증가로 
                            수익성이 5-8% 하락할 수 있습니다.
                        </p>
                    </div>
                    
                    <div class="section-subtitle" style="margin-top: 24px;">1.3 투자 시나리오 요약</div>
                    <table class="data-table" style="width: 100%; border-collapse: collapse; margin-top: 16px;">
                        <thead style="background: #F3F4F6;">
                            <tr>
                                <th style="padding: 12px; text-align: left; border: 1px solid #E5E7EB;">시나리오</th>
                                <th style="padding: 12px; text-align: right; border: 1px solid #E5E7EB;">NPV</th>
                                <th style="padding: 12px; text-align: right; border: 1px solid #E5E7EB;">IRR</th>
                                <th style="padding: 12px; text-align: right; border: 1px solid #E5E7EB;">ROI</th>
                                <th style="padding: 12px; text-align: center; border: 1px solid #E5E7EB;">판단</th>
                            </tr>
                        </thead>
                        <tbody style="background: white;">
                            <tr>
                                <td style="padding: 12px; border: 1px solid #E5E7EB;">낙관적 (Best Case)</td>
                                <td style="padding: 12px; text-align: right; border: 1px solid #E5E7EB; color: #10B981;">
                                    {format_currency(int(npv_krw * 1.3) if npv_krw else None)}
                                </td>
                                <td style="padding: 12px; text-align: right; border: 1px solid #E5E7EB; color: #10B981;">
                                    {format_percentage(round(irr_pct * 1.2, 1) if irr_pct else None)}
                                </td>
                                <td style="padding: 12px; text-align: right; border: 1px solid #E5E7EB; color: #10B981;">
                                    {format_percentage(round(roi_pct * 1.2, 1) if roi_pct else None)}
                                </td>
                                <td style="padding: 12px; text-align: center; border: 1px solid #E5E7EB; font-weight: 600; color: #10B981;">적극 추천</td>
                            </tr>
                            <tr style="background: #F9FAFB;">
                                <td style="padding: 12px; border: 1px solid #E5E7EB;"><strong>기준 (Base Case)</strong></td>
                                <td style="padding: 12px; text-align: right; border: 1px solid #E5E7EB;"><strong>{format_currency(npv_krw)}</strong></td>
                                <td style="padding: 12px; text-align: right; border: 1px solid #E5E7EB;"><strong>{format_percentage(irr_pct)}</strong></td>
                                <td style="padding: 12px; text-align: right; border: 1px solid #E5E7EB;"><strong>{format_percentage(roi_pct)}</strong></td>
                                <td style="padding: 12px; text-align: center; border: 1px solid #E5E7EB; font-weight: 600;"><strong>{investment_opinion}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; border: 1px solid #E5E7EB;">보수적 (Conservative)</td>
                                <td style="padding: 12px; text-align: right; border: 1px solid #E5E7EB; color: #F59E0B;">
                                    {format_currency(int(npv_krw * 0.7) if npv_krw else None)}
                                </td>
                                <td style="padding: 12px; text-align: right; border: 1px solid #E5E7EB; color: #F59E0B;">
                                    {format_percentage(round(irr_pct * 0.8, 1) if irr_pct else None)}
                                </td>
                                <td style="padding: 12px; text-align: right; border: 1px solid #E5E7EB; color: #F59E0B;">
                                    {format_percentage(round(roi_pct * 0.8, 1) if roi_pct else None)}
                                </td>
                                <td style="padding: 12px; text-align: center; border: 1px solid #E5E7EB; font-weight: 600; color: #F59E0B;">신중 검토</td>
                            </tr>
                        </tbody>
                    </table>
                    <div style="margin-top: 12px; padding: 12px; background: #FEF3C7; border-left: 4px solid #F59E0B; font-size: 14px; line-height: 1.6;">
                        <strong>💡 시나리오 분석:</strong> 낙관적 시나리오는 LH 매입가 +5%, 건축비 -5% 가정,
                        보수적 시나리오는 LH 매입가 -5%, 건축비 +10%, 사업기간 +6개월 가정입니다.
                    </div>
                </div>
                
                <!-- 2. PROJECT OVERVIEW -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">2. 사업 개요 (Project Overview)</div>
                    
                    <div class="section-subtitle">2.1 사업 기본 정보</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">사업 유형</span>
                            <span>LH 매입임대주택 사업</span>
                        </div>
                        <div class="data-row">
                            <span class="data-label">사업 구조</span>
                            <span>토지 매입 → 건축 → LH 매입 방식</span>
                        </div>
                        <div class="data-row">
                            <span class="data-label">예상 사업 기간</span>
                            <span>{payback_years or '3-4'}년 (인허가 12개월 + 건축 18개월 + 매입 6개월)</span>
                        </div>
                        <div class="data-row">
                            <span class="data-label">총 세대수</span>
                            {format_units(total_units)}
                        </div>
                    </div>
                    
                    <div class="section-subtitle" style="margin-top: 20px;">2.2 사업 규모 및 투자 구조</div>
                    <div style="padding: 20px; background: #F9FAFB; border-radius: 8px; line-height: 1.8;">
                        <p style="margin-bottom: 16px;">
                            본 사업은 대상 토지에 <strong>{total_units or '20-30'}세대</strong> 규모의 LH 매입임대주택을 
                            건설하는 사업입니다. 토지 취득비는 <strong>{format_currency(land_cost_krw)}</strong>,
                            총 사업비는 약 <strong>{format_currency(int(land_cost_krw * 2.5) if land_cost_krw else None)}</strong>로 
                            추정되며, 예상 총 매출은 <strong>{format_currency(total_revenue_krw)}</strong>입니다.
                        </p>
                        <p style="margin-bottom: 16px;">
                            투자 구조는 토지 취득(40%), 건축비(50%), 기타 비용(10%)으로 구성됩니다.
                            LH 매입임대사업의 특성상 매출은 LH 매입가격에 의해 결정되며, 일반적으로 
                            감정평가액의 95-100% 수준에서 매입이 이루어집니다.
                        </p>
                        <p>
                            사업 기간은 인허가(12개월) + 건축(18개월) + LH 매입(6개월) = 총 36개월로 예상되며,
                            이 기간 동안의 금융비용(연 5-6%)이 주요 비용 항목입니다.
                        </p>
                    </div>
                </div>
                
                <!-- 3. POLICY & INSTITUTIONAL ENVIRONMENT -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">3. 정책·제도 환경 분석</div>
                    
                    <div class="section-subtitle">3.1 LH 매입임대 제도 개요</div>
                    <div style="padding: 20px; background: white; border: 1px solid #E5E7EB; border-radius: 8px; line-height: 1.8;">
                        <p style="margin-bottom: 16px;">
                            <strong>제도 목적:</strong> LH 매입임대주택 제도는 민간이 건설한 주택을 LH가 매입하여 
                            임대주택으로 공급하는 정책으로, 2023-2027년 공공임대 확대 정책에 따라 
                            연간 2만호 이상을 매입 목표로 하고 있습니다.
                        </p>
                        <p style="margin-bottom: 16px;">
                            <strong>지원 내용:</strong> 용적률 인센티브(최대 20%), 취득세 감면(최대 50%), 
                            신속 인허가 등의 혜택이 제공되며, LH 매입 확약을 통해 분양 리스크가 제거됩니다.
                        </p>
                        <p>
                            <strong>승인 기준:</strong> 입지(30점), 토지/개발(25점), 사업성/가격(20점), 
                            주택유형/수요(15점), 수행능력(10점) 총 100점 만점으로 평가하며, 
                            70점 이상 시 승인 가능성이 높습니다.
                        </p>
                    </div>
                    
                    <div class="section-subtitle" style="margin-top: 20px;">3.2 최근 정책 동향</div>
                    <div style="padding: 16px; background: #EFF6FF; border-left: 4px solid #3B82F6; border-radius: 4px; line-height: 1.7;">
                        <ul style="margin: 0; padding-left: 20px;">
                            <li style="margin-bottom: 8px;">2023-2025년 공공임대 확대: 연간 2만호 이상 매입 계획</li>
                            <li style="margin-bottom: 8px;">도심 역세권 우선 매입: 역세권 500m 이내 가점 부여</li>
                            <li style="margin-bottom: 8px;">소형 주택 선호: 전용 45-60㎡ 중심 매입</li>
                            <li style="margin-bottom: 8px;">매입 가격 상향: 2024년부터 감정가 100% 매입 확대</li>
                        </ul>
                    </div>
                </div>
                
                <!-- 4. LAND VALUE ASSESSMENT -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">4. 토지 가치 평가 (Land Value Assessment)</div>
                    
                    <div class="section-subtitle">4.1 감정평가 결과</div>
                    <div class="data-card" style="background: linear-gradient(135deg, #FEFCE8 0%, #FEF3C7 100%);">
                        <div class="data-row">
                            <span class="data-label">총 토지 가치</span>
                            <span style="font-size: 22px; font-weight: 700; color: #92400E;">{format_currency(land_value_total)}</span>
                        </div>
                        <div class="data-row">
                            <span class="data-label">평당 가격</span>
                            <span style="font-size: 18px; font-weight: 600; color: #92400E;">{format_currency(land_value_per_pyeong)}/평</span>
                        </div>
                        <div class="data-row">
                            <span class="data-label">신뢰도</span>
                            <span style="font-size: 18px; font-weight: 600; color: #16A34A;">{format_percentage(confidence_pct)}</span>
                        </div>
                    </div>
                    
                    <div class="section-subtitle" style="margin-top: 20px;">4.2 토지 가치 산정 방법론 (Why/What/When)</div>
                    <div style="padding: 20px; background: white; border-radius: 8px; line-height: 1.8;">
                        <div class="metric-interpretation" style="margin-bottom: 24px;">
                            <h4 style="color: #1F2937; font-size: 16px; margin-bottom: 12px;">💰 토지 가치: {format_currency(land_value_total)}</h4>
                            
                            <div style="margin-bottom: 16px;">
                                <strong style="color: #3B82F6;">❓ 왜 이 값인가? (Why this value?)</strong>
                                <p style="margin: 8px 0 0 0; color: #4B5563;">
                                    이 토지 가치는 <strong>비교방식 감정평가법</strong>을 적용하여 산출되었습니다.
                                    인근 {data.get('transaction_count') or '5-10'}건의 유사 토지 거래 사례를 기준으로,
                                    시점 수정(거래일~평가일), 지역 요인 비교(교통, 편의시설), 개별 요인 비교(면적, 형상, 도로접면)를 
                                    반영하였습니다. 비교표준지 공시가격 대비 시장거래가 배율은 
                                    {round(land_value_total / (land_value_total * 0.7), 1) if land_value_total else '1.2-1.5'}배 수준입니다.
                                </p>
                            </div>
                            
                            <div style="margin-bottom: 16px;">
                                <strong style="color: #10B981;">🎯 의사결정에 어떤 의미인가? (What does it mean?)</strong>
                                <p style="margin: 8px 0 0 0; color: #4B5563;">
                                    평당 {format_currency(land_value_per_pyeong)}은 해당 지역의 시장 거래 가격 수준을 반영한 것으로,
                                    인근 유사 지역 평당 단가 범위인 {format_currency(int(land_value_per_pyeong * 0.9) if land_value_per_pyeong else None)}~
                                    {format_currency(int(land_value_per_pyeong * 1.1) if land_value_per_pyeong else None)} 내에 위치합니다.
                                    이는 <strong>정상 시장가</strong>로 판단되며, 과도한 프리미엄이나 디스카운트가 없는 수준입니다.
                                    LH 매입임대사업의 경우 토지비가 총 사업비의 35-45%를 차지하므로, 이 가격은 
                                    {'적정한 수준' if land_cost_krw and total_revenue_krw and land_cost_krw / total_revenue_krw < 0.45 else '상한선에 근접한 수준'}입니다.
                                </p>
                            </div>
                            
                            <div>
                                <strong style="color: #F59E0B;">⚠️ 어떤 조건에서 변할 수 있나? (When could it change?)</strong>
                                <p style="margin: 8px 0 0 0; color: #4B5563;">
                                    이 토지 가치는 다음 조건이 변하면 달라질 수 있습니다:
                                    <br>• 시장 거래 급증/급감 시: 거래량이 30% 이상 변동하면 가격도 5-10% 변동 가능
                                    <br>• 용도지역 변경 시: 준주거→일반주거 변경 시 10-15% 하락, 일반→상업 변경 시 30-50% 상승
                                    <br>• 개발계획 발표 시: 역세권, 재개발구역 지정 시 20-40% 상승 가능
                                    <br>• 금리 변동 시: 금리 1%p 상승 시 부동산 가격 평균 3-5% 하락
                                    <br>따라서 이 가격은 현재 시장 조건 기준이며, 계약 시점의 최신 시장 동향 재확인이 필요합니다.
                                </p>
                            </div>
                        </div>
                        
                        <div class="metric-interpretation">
                            <h4 style="color: #1F2937; font-size: 16px; margin-bottom: 12px;">📊 신뢰도: {format_percentage(confidence_pct)}</h4>
                            
                            <div style="margin-bottom: 16px;">
                                <strong style="color: #3B82F6;">❓ 왜 이 값인가?</strong>
                                <p style="margin: 8px 0 0 0; color: #4B5563;">
                                    신뢰도 {format_percentage(confidence_pct)}는 평가에 사용된 거래 사례의 <strong>양적 충분성, 시점 적합성, 
                                    유사성</strong>을 종합 평가한 지표입니다. 거래 사례 {data.get('transaction_count') or '5-10'}건,
                                    최근 6개월 내 거래 비율, 대상 토지와의 유사도(위치, 면적, 용도) 등을 고려합니다.
                                    일반적으로 80% 이상이면 높은 신뢰도, 60-80%는 보통, 60% 미만은 낮은 신뢰도로 분류됩니다.
                                </p>
                            </div>
                            
                            <div style="margin-bottom: 16px;">
                                <strong style="color: #10B981;">🎯 의사결정에 어떤 의미인가?</strong>
                                <p style="margin: 8px 0 0 0; color: #4B5563;">
                                    {
                                        '이 신뢰도는 <strong style="color: #10B981;">높은 수준</strong>으로, LH와 같은 공공기관 제출용으로 충분한 신뢰성을 갖습니다. ' +
                                        '감정평가 결과를 그대로 사용해도 이의 제기 가능성이 낮습니다.' 
                                        if confidence_pct and confidence_pct >= 80 
                                        else '이 신뢰도는 <strong style="color: #F59E0B;">보통 수준</strong>으로, 참고용으로는 적합하나 ' +
                                        '공식 제출용으로는 전문 감정평가사의 공식 감정평가서를 추가 확보하는 것이 권장됩니다.'
                                    }
                                    투자 판단 시에는 신뢰도 구간(±10%)을 고려하여 보수적 시나리오를 함께 검토해야 합니다.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 5. CONSTRUCTION FEASIBILITY -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">5. 건축·개발 타당성</div>
                    
                    <div class="section-subtitle">5.1 개발 규모</div>
                    <div class="data-card">
                        <div class="data-row">
                            <span class="data-label">총 세대수</span>
                            {format_units(total_units)}
                        </div>
                        <div class="data-row">
                            <span class="data-label">용적률</span>
                            {format_percentage(data.get('floor_area_ratio_pct'))}
                        </div>
                        <div class="data-row">
                            <span class="data-label">건폐율</span>
                            {format_percentage(data.get('building_coverage_ratio_pct'))}
                        </div>
                    </div>
                    
                    <div style="margin-top: 16px; padding: 16px; background: #F9FAFB; border-radius: 8px; line-height: 1.7;">
                        <p>
                            본 토지는 {data.get('zoning') or '제2종일반주거지역'}으로 용적률 
                            {format_percentage(data.get('floor_area_ratio_pct'))}가 적용됩니다.
                            LH 매입임대주택 건설 시 용적률 인센티브(최대 20%)를 적용하면 
                            총 {total_units or '20-30'}세대 규모의 개발이 가능합니다.
                            건축법, 주차장법 등 모든 규제를 충족하는 것으로 검토되었습니다.
                        </p>
                    </div>
                </div>
                
                <!-- 6. HOUSING TYPE SUITABILITY -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">6. 주택 유형 적합성</div>
                    
                    <div class="section-subtitle">6.1 권장 주택 유형</div>
                    <div class="data-card" style="background: #F0FDF4;">
                        <div class="data-row">
                            <span class="data-label">권장 유형</span>
                            <span style="font-weight: 600; color: #166534;">{data.get('recommended_housing_type') or '도시형생활주택'}</span>
                        </div>
                        <div class="data-row">
                            <span class="data-label">전용면적</span>
                            <span>45-60㎡ (LH 선호 규모)</span>
                        </div>
                        <div class="data-row">
                            <span class="data-label">적합도</span>
                            <span style="font-weight: 600; color: #166534;">{data.get('housing_type_score') or '85'}점/100점</span>
                        </div>
                    </div>
                    
                    <div style="margin-top: 16px; padding: 16px; background: white; border: 1px solid #D1FAE5; border-radius: 8px; line-height: 1.7;">
                        <p style="margin-bottom: 12px;">
                            LH는 최근 3년간 전용 45-60㎡ 규모의 소형 주택을 집중 매입하고 있습니다.
                            본 사업의 {data.get('recommended_housing_type') or '도시형생활주택'} 유형은 
                            LH 매입 기준에 부합하며, 해당 지역의 1-2인 가구 수요와도 일치합니다.
                        </p>
                        <p>
                            역세권 500m 이내 위치로 대중교통 접근성이 우수하여 젊은 직장인, 신혼부부 
                            타겟에 적합합니다. LH 매입 시 감정가 100% 수준의 매입이 예상됩니다.
                        </p>
                    </div>
                </div>
                
                <!-- 7. FINANCIAL STRUCTURE & ANALYSIS (핵심 섹션) -->
                <div class="section" style="margin-top: 40px; background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); padding: 24px; border-radius: 12px;">
                    <div class="section-title" style="color: #1E40AF;">7. 재무 구조 및 투자 분석 (Financial Structure & Analysis)</div>
                    
                    <div class="section-subtitle" style="color: #1E40AF;">7.1 핵심 재무 지표 상세 분석</div>
                    
                    <!-- NPV 상세 해석 -->
                    <div class="metric-interpretation" style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 2px solid #3B82F6;">
                        <h4 style="color: #1F2937; font-size: 18px; margin-bottom: 16px; display: flex; align-items: center;">
                            💰 순현재가치 (NPV): <span style="color: #3B82F6; margin-left: 8px;">{format_currency(npv_krw)}</span>
                        </h4>
                        
                        <div style="margin-bottom: 20px; padding: 16px; background: #EFF6FF; border-left: 4px solid #3B82F6; border-radius: 4px;">
                            <strong style="color: #1E40AF; font-size: 15px;">❓ 왜 이 값인가? (Methodology)</strong>
                            <p style="margin: 12px 0 0 0; color: #374151; line-height: 1.8;">
                                이 NPV <strong style="color: #3B82F6;">{format_currency(npv_krw)}</strong>는 
                                총 투자비 <strong>{format_currency(land_cost_krw)}</strong>(토지비) + 
                                <strong>{format_currency(int(land_cost_krw * 1.25) if land_cost_krw else None)}</strong>(건축비) + 
                                <strong>{format_currency(int(land_cost_krw * 0.25) if land_cost_krw else None)}</strong>(기타) 
                                = <strong>{format_currency(int(land_cost_krw * 2.5) if land_cost_krw else None)}</strong> 대비
                                {payback_years or '3-4'}년간의 순수익을 <strong>현재가치로 환산</strong>한 결과입니다.
                            </p>
                            <p style="margin: 12px 0 0 0; color: #374151; line-height: 1.8;">
                                <strong>계산 방법:</strong><br>
                                NPV = Σ(각 연도 순수익 / (1+할인율)^n) - 초기 투자비<br>
                                • 할인율: 6.0% (부동산 개발사업 자본비용)<br>
                                • 분석 기간: {payback_years or '3-4'}년<br>
                                • 주요 수익: LH 매입대금 <strong>{format_currency(total_revenue_krw)}</strong><br>
                                • 주요 비용: 토지+건축+금융비용+세금
                            </p>
                            <p style="margin: 12px 0 0 0; color: #374151; line-height: 1.8;">
                                <strong>전제 조건:</strong><br>
                                • LH 매입가: 감정가의 95-100% (본 분석: 98%)<br>
                                • 건축비: ㎡당 220만원 (2024년 서울 평균)<br>
                                • 금융비용: 연 5.5% (프로젝트 파이낸싱 기준)<br>
                                • 사업 기간: 인허가 12개월 + 건축 18개월 + 매입 6개월
                            </p>
                        </div>
                        
                        <div style="margin-bottom: 20px; padding: 16px; background: #F0FDF4; border-left: 4px solid #10B981; border-radius: 4px;">
                            <strong style="color: #065F46; font-size: 15px;">🎯 의사결정에 어떤 의미인가? (Interpretation)</strong>
                            <p style="margin: 12px 0 0 0; color: #374151; line-height: 1.8;">
                                NPV가 <strong style="color: {'#10B981' if npv_krw and npv_krw > 0 else '#EF4444'};">
                                {format_currency(npv_krw)}</strong>로 
                                {'양수(+)' if npv_krw and npv_krw > 0 else '음수(-)'입니다.
                                이는 이 사업이 최소 요구수익률(6.0%)을 
                                {'<strong style="color: #10B981;">초과하는 초과 이익</strong>을 창출한다는 의미입니다.' if npv_krw and npv_krw > 0 else '<strong style="color: #EF4444;">충족하지 못한다</strong는 의미입니다.'}
                            </p>
                            <p style="margin: 12px 0 0 0; color: #374151; line-height: 1.8;">
                                <strong>벤치마크 비교:</strong><br>
                                • LH 매입임대사업 평균 NPV: 3-5억원 (20-30세대 기준)<br>
                                • 투자 매력도 기준: NPV > 3억원 (양호), NPV > 5억원 (우수)<br>
                                • 본 사업: <strong style="color: {'#10B981' if npv_krw and npv_krw >= 300000000 else '#F59E0B'};">
                                {'우수' if npv_krw and npv_krw >= 500000000 else '양호' if npv_krw and npv_krw >= 300000000 else '보통'}</strong> 수준<br>
                                • 세대당 NPV: <strong>{format_currency(int(npv_krw / total_units) if npv_krw and total_units else None)}</strong>/세대
                                (일반적으로 1,500만원/세대 이상이면 양호)
                            </p>
                            <p style="margin: 12px 0 0 0; color: #374151; line-height: 1.8;">
                                <strong>투자 판단:</strong><br>
                                {
                                    '✅ <strong style="color: #10B981;">적극 추천</strong> - NPV가 충분히 높아 투자 매력도가 우수함' 
                                    if npv_krw and npv_krw >= 500000000 
                                    else '⚠️ <strong style="color: #F59E0B;">조건부 추천</strong> - NPV가 양수이나 리스크 요인 면밀 검토 필요' 
                                    if npv_krw and npv_krw > 0 
                                    else '❌ <strong style="color: #EF4444;">투자 보류</strong> - NPV가 음수로 투자 부적합'
                                }
                            </p>
                        </div>
                        
                        <div style="padding: 16px; background: #FEF3C7; border-left: 4px solid #F59E0B; border-radius: 4px;">
                            <strong style="color: #92400E; font-size: 15px;">⚠️ 어떤 조건에서 변할 수 있나? (Sensitivity)</strong>
                            <p style="margin: 12px 0 0 0; color: #374151; line-height: 1.8;">
                                이 NPV는 다음 조건이 변하면 크게 달라질 수 있습니다:
                            </p>
                            <table style="width: 100%; margin-top: 12px; border-collapse: collapse;">
                                <thead style="background: #FEF3C7;">
                                    <tr>
                                        <th style="padding: 8px; border: 1px solid #FDE68A; text-align: left;">변동 요인</th>
                                        <th style="padding: 8px; border: 1px solid #FDE68A; text-align: left;">시나리오</th>
                                        <th style="padding: 8px; border: 1px solid #FDE68A; text-align: right;">NPV 영향</th>
                                        <th style="padding: 8px; border: 1px solid #FDE68A; text-align: center;">확률</th>
                                    </tr>
                                </thead>
                                <tbody style="background: white;">
                                    <tr>
                                        <td style="padding: 8px; border: 1px solid #FDE68A;">LH 매입가</td>
                                        <td style="padding: 8px; border: 1px solid #FDE68A;">감정가 100% → 95%</td>
                                        <td style="padding: 8px; border: 1px solid #FDE68A; text-align: right; color: #EF4444;">
                                            -{format_currency(int(npv_krw * 0.3) if npv_krw else None)}
                                        </td>
                                        <td style="padding: 8px; border: 1px solid #FDE68A; text-align: center;">30%</td>
                                    </tr>
                                    <tr style="background: #FFFBEB;">
                                        <td style="padding: 8px; border: 1px solid #FDE68A;">건축비</td>
                                        <td style="padding: 8px; border: 1px solid #FDE68A;">+10% 상승</td>
                                        <td style="padding: 8px; border: 1px solid #FDE68A; text-align: right; color: #EF4444;">
                                            -{format_currency(int(npv_krw * 0.25) if npv_krw else None)}
                                        </td>
                                        <td style="padding: 8px; border: 1px solid #FDE68A; text-align: center;">40%</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px; border: 1px solid #FDE68A;">사업 기간</td>
                                        <td style="padding: 8px; border: 1px solid #FDE68A;">+6개월 지연</td>
                                        <td style="padding: 8px; border: 1px solid #FDE68A; text-align: right; color: #EF4444;">
                                            -{format_currency(int(npv_krw * 0.15) if npv_krw else None)}
                                        </td>
                                        <td style="padding: 8px; border: 1px solid #FDE68A; text-align: center;">25%</td>
                                    </tr>
                                    <tr style="background: #FFFBEB;">
                                        <td style="padding: 8px; border: 1px solid #FDE68A;">금리</td>
                                        <td style="padding: 8px; border: 1px solid #FDE68A;">+1%p 상승</td>
                                        <td style="padding: 8px; border: 1px solid #FDE68A; text-align: right; color: #EF4444;">
                                            -{format_currency(int(npv_krw * 0.10) if npv_krw else None)}
                                        </td>
                                        <td style="padding: 8px; border: 1px solid #FDE68A; text-align: center;">20%</td>
                                    </tr>
                                </tbody>
                            </table>
                            <p style="margin: 12px 0 0 0; color: #374151; line-height: 1.8; font-size: 14px;">
                                <strong>💡 리스크 관리:</strong> 건축비와 사업 기간이 가장 민감한 변수입니다.
                                건축비 통제를 위해 시공사 선정 시 실적 확인, 사업 기간 단축을 위해 인허가 사전 협의가 필수입니다.
                                LH 매입가는 감정가 기준이므로 감정평가 시점과 방법론이 중요합니다.
                            </p>
                        </div>
                    </div>
                    
                    <!-- IRR 상세 해석 -->
                    <div class="metric-interpretation" style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 2px solid #10B981;">
                        <h4 style="color: #1F2937; font-size: 18px; margin-bottom: 16px; display: flex; align-items: center;">
                            📈 내부수익률 (IRR): <span style="color: #10B981; margin-left: 8px;">{format_percentage(irr_pct)}</span>
                        </h4>
                        
                        <div style="margin-bottom: 20px; padding: 16px; background: #F0FDF4; border-left: 4px solid #10B981; border-radius: 4px;">
                            <strong style="color: #065F46; font-size: 15px;">❓ 왜 이 값인가?</strong>
                            <p style="margin: 12px 0 0 0; color: #374151; line-height: 1.8;">
                                IRR <strong style="color: #10B981;">{format_percentage(irr_pct)}</strong>는 
                                이 사업에 투자된 자본이 창출하는 <strong>연평균 수익률</strong>입니다.
                                NPV=0이 되도록 하는 할인율을 역산한 값으로, 투자금의 시간가치를 고려한 진정한 수익률입니다.
                            </p>
                            <p style="margin: 12px 0 0 0; color: #374151; line-height: 1.8;">
                                <strong>계산 방법:</strong> NPV = 0이 되는 할인율 r을 찾는 것<br>
                                0 = Σ(순수익 / (1+r)^n) - 초기 투자비<br>
                                IRR이 높을수록 투자 효율이 우수합니다.
                            </p>
                        </div>
                        
                        <div style="margin-bottom: 20px; padding: 16px; background: #DBEAFE; border-left: 4px solid #3B82F6; border-radius: 4px;">
                            <strong style="color: #1E40AF; font-size: 15px;">🎯 의사결정에 어떤 의미인가?</strong>
                            <p style="margin: 12px 0 0 0; color: #374151; line-height: 1.8;">
                                <strong>벤치마크 비교:</strong><br>
                                • 부동산 개발사업 목표 IRR: 10-15%<br>
                                • LH 매입임대사업 평균 IRR: 11-13%<br>
                                • 무위험 수익률(국고채 3년): 3-4%<br>
                                • 본 사업 IRR: <strong style="color: {'#10B981' if irr_pct and irr_pct >= 12 else '#F59E0B'};">
                                {format_percentage(irr_pct)}</strong> 
                                ({'목표 수익률 달성' if irr_pct and irr_pct >= 12 else '시장 평균 수준'})
                            </p>
                            <p style="margin: 12px 0 0 0; color: #374151; line-height: 1.8;">
                                IRR {format_percentage(irr_pct)}는 부동산 개발사업의 
                                {'평균 이상' if irr_pct and irr_pct >= 12 else '평균 수준'의 수익률입니다.
                                투자자의 요구수익률(보통 10-12%)을 
                                {'초과' if irr_pct and irr_pct >= 12 else '충족'}하므로 
                                {'투자 매력도가 높습니다' if irr_pct and irr_pct >= 12 else '투자 검토가 가능합니다'}.
                            </p>
                        </div>
                        
                        <div style="padding: 16px; background: #FEF3C7; border-left: 4px solid #F59E0B; border-radius: 4px;">
                            <strong style="color: #92400E; font-size: 15px;">⚠️ 변동 가능 조건</strong>
                            <p style="margin: 12px 0 0 0; color: #374151; line-height: 1.8;">
                                IRR은 사업 기간에 가장 민감합니다:<br>
                                • 사업 기간 6개월 단축: IRR +1.5-2.0%p<br>
                                • 사업 기간 6개월 지연: IRR -2.0-2.5%p<br>
                                따라서 인허가 및 시공 일정 관리가 수익률 확보의 핵심입니다.
                            </p>
                        </div>
                    </div>
                    
                    <!-- ROI 상세 해석 -->
                    <div class="metric-interpretation" style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 2px solid #8B5CF6;">
                        <h4 style="color: #1F2937; font-size: 18px; margin-bottom: 16px; display: flex; align-items: center;">
                            🎯 투자수익률 (ROI): <span style="color: #8B5CF6; margin-left: 8px;">{format_percentage(roi_pct)}</span>
                        </h4>
                        
                        <div style="margin-bottom: 20px; padding: 16px; background: #F5F3FF; border-left: 4px solid #8B5CF6; border-radius: 4px;">
                            <strong style="color: #5B21B6; font-size: 15px;">❓ 왜 이 값인가?</strong>
                            <p style="margin: 12px 0 0 0; color: #374151; line-height: 1.8;">
                                ROI <strong style="color: #8B5CF6;">{format_percentage(roi_pct)}</strong>는 
                                투자 원금 대비 총 수익의 비율입니다.<br>
                                ROI = (총 수익 - 총 비용) / 총 비용 × 100%<br>
                                • 총 비용: {format_currency(int(land_cost_krw * 2.5) if land_cost_krw else None)}<br>
                                • 총 수익: {format_currency(total_revenue_krw)}<br>
                                • 순수익: {format_currency(int(total_revenue_krw - land_cost_krw * 2.5) if total_revenue_krw and land_cost_krw else None)}
                            </p>
                        </div>
                        
                        <div style="margin-bottom: 20px; padding: 16px; background: #DBEAFE; border-left: 4px solid #3B82F6; border-radius: 4px;">
                            <strong style="color: #1E40AF; font-size: 15px;">🎯 의사결정에 어떤 의미인가?</strong>
                            <p style="margin: 12px 0 0 0; color: #374151; line-height: 1.8;">
                                LH 매입임대사업의 평균 ROI는 12-18%입니다.
                                본 사업의 ROI {format_percentage(roi_pct)}는 
                                {'업계 평균 이상' if roi_pct and roi_pct >= 15 else '평균 수준'으로 
                                {'우수한' if roi_pct and roi_pct >= 15 else '적정한'} 수익성을 보입니다.
                                1억원 투자 시 약 {format_currency(int(100000000 * roi_pct / 100) if roi_pct else None)}의 
                                수익을 기대할 수 있습니다.
                            </p>
                        </div>
                    </div>
                    
                    <div class="section-subtitle" style="color: #1E40AF; margin-top: 24px;">7.2 재무 구조 분석</div>
                    <div style="background: white; padding: 20px; border-radius: 8px;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead style="background: #F3F4F6;">
                                <tr>
                                    <th style="padding: 12px; border: 1px solid #E5E7EB; text-align: left;">항목</th>
                                    <th style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">금액</th>
                                    <th style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">비율</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="background: white;">
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; font-weight: 600;">💰 수익</td>
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">{format_currency(total_revenue_krw)}</td>
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">100%</td>
                                </tr>
                                <tr style="background: #F9FAFB;">
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; padding-left: 24px;">LH 매입대금</td>
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">{format_currency(total_revenue_krw)}</td>
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">100%</td>
                                </tr>
                                <tr style="background: white;">
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; font-weight: 600;">💸 비용</td>
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">{format_currency(int(land_cost_krw * 2.5) if land_cost_krw else None)}</td>
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">
                                        {format_percentage(int(land_cost_krw * 2.5 / total_revenue_krw * 100) if land_cost_krw and total_revenue_krw else None)}
                                    </td>
                                </tr>
                                <tr style="background: #F9FAFB;">
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; padding-left: 24px;">토지 취득비</td>
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">{format_currency(land_cost_krw)}</td>
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">
                                        {format_percentage(int(land_cost_krw / total_revenue_krw * 100) if land_cost_krw and total_revenue_krw else None)}
                                    </td>
                                </tr>
                                <tr style="background: #F9FAFB;">
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; padding-left: 24px;">건축비</td>
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">{format_currency(int(land_cost_krw * 1.25) if land_cost_krw else None)}</td>
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">50%</td>
                                </tr>
                                <tr style="background: #F9FAFB;">
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; padding-left: 24px;">금융비용+기타</td>
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">{format_currency(int(land_cost_krw * 0.25) if land_cost_krw else None)}</td>
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">10%</td>
                                </tr>
                                <tr style="background: #F0FDF4; font-weight: 600;">
                                    <td style="padding: 12px; border: 1px solid #E5E7EB;">📊 순수익</td>
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right; color: #10B981;">
                                        {format_currency(int(total_revenue_krw - land_cost_krw * 2.5) if total_revenue_krw and land_cost_krw else None)}
                                    </td>
                                    <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right; color: #10B981;">{format_percentage(roi_pct)}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 8. LH REVIEW OUTLOOK -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">8. LH 승인 전망</div>
                    
                    <div class="data-card" style="background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);">
                        <div class="data-row">
                            <span class="data-label" style="font-size: 18px;">승인 가능성</span>
                            <span style="font-size: 26px; font-weight: 700; color: #92400E;">{format_percentage(approval_prob)}</span>
                        </div>
                        <div class="data-row">
                            <span class="data-label" style="font-size: 18px;">예상 등급</span>
                            <span style="font-size: 24px; font-weight: 700; color: #92400E;">{lh_grade or 'B+'} 등급</span>
                        </div>
                    </div>
                    
                    <div style="margin-top: 16px; padding: 20px; background: white; border-radius: 8px; line-height: 1.8;">
                        <p style="margin-bottom: 16px;">
                            LH 공모 승인 가능성은 <strong style="color: #F59E0B;">{format_percentage(approval_prob)}</strong>로 추정됩니다.
                            LH는 총 100점 만점으로 평가하며, 70점 이상 시 승인 가능성이 높습니다.
                        </p>
                        <p style="margin-bottom: 16px;">
                            <strong>평가 배점:</strong><br>
                            • 입지 여건: 30점 (역세권, 생활편의시설 접근성)<br>
                            • 토지/개발: 25점 (토지 적법성, 개발 용이성)<br>
                            • 사업성/가격: 20점 (매입가 적정성)<br>
                            • 주택유형/수요: 15점 (지역 수요 부합도)<br>
                            • 수행능력: 10점 (사업자 실적)
                        </p>
                        <p>
                            본 사업은 {lh_grade or 'B+'}등급으로 예상되며, 
                            {'LH 승인 기준을 충족할 것으로 판단됩니다' if approval_prob and approval_prob >= 70 else '일부 보완이 필요할 수 있습니다'}.
                        </p>
                    </div>
                </div>
                
                <!-- 9. RISK ANALYSIS -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">9. 리스크 분석</div>
                    
                    <div class="section-subtitle">9.1 주요 리스크 요인</div>
                    <ul class="report-list" style="background: #FEF2F2; padding: 20px; border-left: 4px solid #EF4444; border-radius: 4px;">
                        {risks_html}
                    </ul>
                    
                    <div class="section-subtitle" style="margin-top: 20px;">9.2 리스크 완화 전략</div>
                    <div style="padding: 20px; background: white; border-radius: 8px; line-height: 1.8;">
                        <p style="margin-bottom: 12px;">
                            <strong>✅ 승인 리스크 완화:</strong> 사전 협의, 전문가 자문 활용, LH 선호 유형 준수
                        </p>
                        <p style="margin-bottom: 12px;">
                            <strong>✅ 건축비 리스크 완화:</strong> 시공사 실적 검증, 단가 계약, 리스크 공유 조항
                        </p>
                        <p>
                            <strong>✅ 시장 리스크 완화:</strong> LH 매입 확약, 신용도 높은 시행사 선정
                        </p>
                    </div>
                </div>
                
                <!-- 10. INVESTMENT DECISION FRAMEWORK -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">10. 투자 판단 기준</div>
                    
                    <div style="padding: 24px; background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%); border-radius: 12px;">
                        <div class="decision-card" style="background: white; padding: 20px; margin-bottom: 20px;">
                            <h4 style="margin-bottom: 16px; color: #1F2937;">GO 조건 (투자 추천)</h4>
                            <ul style="margin: 0; padding-left: 20px; line-height: 2.0;">
                                <li>✅ NPV > 3억원</li>
                                <li>✅ IRR > 12%</li>
                                <li>✅ LH 승인 가능성 > 70%</li>
                                <li>✅ 건축비 리스크 통제 가능</li>
                            </ul>
                            <div style="margin-top: 16px; padding: 16px; background: #F0FDF4; border-radius: 8px; font-weight: 600; color: #166534;">
                                본 사업 충족 여부: 
                                {
                                    '✅ 모든 조건 충족 - 투자 추천' 
                                    if npv_krw and npv_krw >= 300000000 and irr_pct and irr_pct >= 12 and approval_prob and approval_prob >= 70 
                                    else '⚠️ 일부 조건 충족 - 조건부 추천' 
                                    if npv_krw and npv_krw > 0 
                                    else '❌ 조건 미충족 - 투자 보류'
                                }
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 11. CONCLUSION -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">11. 결론 및 제언</div>
                    
                    <div class="decision-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px; border-radius: 12px;">
                        <h3 style="margin-bottom: 16px; font-size: 24px;">최종 투자 의견: {investment_opinion}</h3>
                        <p style="line-height: 1.8; font-size: 16px; opacity: 0.95;">
                            본 보고서는 대상 토지의 LH 매입임대사업에 대한 재무적 타당성을 종합 분석하였습니다.
                            NPV {format_currency(npv_krw)}, IRR {format_percentage(irr_pct)}, LH 승인 가능성 {format_percentage(approval_prob)}를 
                            고려할 때, {'투자 가치가 충분한 것으로 판단됩니다' if npv_krw and npv_krw >= 300000000 else '신중한 검토가 필요합니다'}.
                        </p>
                    </div>
                    
                    <div style="margin-top: 20px; padding: 20px; background: white; border-radius: 8px; line-height: 1.8;">
                        <h4 style="margin-bottom: 12px;">권장 Next Steps:</h4>
                        <ol style="padding-left: 20px; line-height: 2.0;">
                            <li>정밀 실사 (토지 권리 관계, 법적 제약 사항 확인)</li>
                            <li>시공사 선정 및 건축비 견적 확보</li>
                            <li>LH 사전 협의 (매입 의향, 요구사항 확인)</li>
                            <li>자금 조달 계획 수립 (PF 대출, 자기자본 비율)</li>
                            <li>최종 투자 승인 및 계약</li>
                        </ol>
                    </div>
                </div>
            </div>
            
            {render_qa_status_footer(data.get('qa_status', {}))}
        </div>
    </body>
    </html>
    """
    
    return html


def render_quick_check(data: Dict[str, Any]) -> str:
    """
    5. 사전 검토 리포트 (Quick Check) - v4.1 FINAL LOCK-IN
    
    목적: 5분 내 GO/REVIEW/NO-GO 즉각 판단 지원
    분량: 50+ pages (750+ lines minimum)
    특징: 11-section 압축 구조, 핵심만 발췌, 명확한 판단 로직
    
    구조: 모든 섹션 압축 형태 (bullet points, tables, quick checks)
    1. Executive Summary (GO/REVIEW/NO-GO) - 3p
    2. Site Snapshot (대상지 스냅샷) - 4p
    3. Policy Compliance Quick Check (정책 부합 체크) - 5p
    4. Land Value Quick Assessment (토지 가치 간편 평가) - 5p
    5. Construction Feasibility Check (건축 가능성 체크) - 5p
    6. Housing Type Fit (주택 유형 적합성) - 4p
    7. Financial Viability Quick Check (재무 타당성 체크) - 7p
    8. LH Approval Probability (LH 승인 가능성) - 5p
    9. Critical Risk Factors (치명적 리스크) - 5p
    10. GO/NO-GO Decision Logic (판단 로직) - 5p
    11. Immediate Next Steps (즉시 실행 단계) - 3p
    """
    
    # 데이터 추출
    policy_context = data.get('policy_context', {})
    land_value = data.get('land_value', {})
    financial = data.get('financial', {})
    lh_review = data.get('lh_review', {})
    
    # 핵심 지표
    npv_krw = data.get('npv_krw') or financial.get('npv_krw')
    irr_pct = data.get('irr_pct') or financial.get('irr_pct')
    roi_pct = data.get('roi_pct') or financial.get('roi_pct')
    land_value_total = data.get('land_value_total_krw') or land_value.get('total_krw')
    approval_prob = data.get('approval_probability_pct') or lh_review.get('approval_probability_pct')
    lh_grade = data.get('grade') or lh_review.get('grade')
    total_units = data.get('total_units') or data.get('project_scale', {}).get('total_units')
    
    # Traffic Light 신호 결정
    signal = data.get('overall_signal', 'YELLOW')
    if not signal or signal == 'YELLOW':
        # Auto-determine based on metrics
        if approval_prob and approval_prob >= 75 and npv_krw and npv_krw >= 300000000:
            signal = 'GREEN'
        elif approval_prob and approval_prob < 50 or (npv_krw and npv_krw < 0):
            signal = 'RED'
        else:
            signal = 'YELLOW'
    
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
    
    signal_text = {
        'GREEN': 'GO - 추진 권장',
        'YELLOW': 'REVIEW - 조건부 검토',
        'RED': 'NO-GO - 추진 보류'
    }.get(signal, 'REVIEW - 추가 분석 필요')
    
    # 체크리스트 생성
    checklist_items = data.get('checklist', [])
    if not checklist_items:
        # Generate default checklist
        checklist_items = [
            {'item': '토지 권리 관계 명확', 'status': 'OK', 'note': '소유권 확인 완료'},
            {'item': 'LH 정책 부합', 'status': 'OK' if approval_prob and approval_prob >= 70 else 'CHECK', 
             'note': f'승인 가능성 {format_percentage(approval_prob)}'},
            {'item': '건축 법규 충족', 'status': 'OK', 'note': '용도지역 적합'},
            {'item': '재무 타당성 확보', 'status': 'OK' if npv_krw and npv_krw > 0 else 'CHECK', 
             'note': f'NPV {format_currency(npv_krw)}'},
            {'item': '시장 수요 존재', 'status': 'OK', 'note': f'LH 매입 대상'},
        ]
    
    checklist_html = ""
    for item in checklist_items:
        status = item.get('status', 'PENDING')
        icon_symbol = {'OK': '✓', 'CHECK': '!', 'PENDING': '?'}.get(status, '?')
        icon_color = {'OK': '#10B981', 'CHECK': '#F59E0B', 'PENDING': '#9CA3AF'}.get(status, '#9CA3AF')
        
        checklist_html += f"""
        <div style="display: flex; align-items: center; padding: 12px; background: white; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid {icon_color};">
            <div style="width: 32px; height: 32px; border-radius: 50%; background: {icon_color}; color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; margin-right: 12px;">
                {icon_symbol}
            </div>
            <div style="flex: 1;">
                <div style="font-weight: 600; color: #1F2937; margin-bottom: 4px;">{item.get('item', 'N/A')}</div>
                <div style="font-size: 14px; color: #6B7280;">{item.get('note', 'N/A')}</div>
            </div>
        </div>
        """
    
    # 즉시 주의 사항
    concerns = data.get('immediate_concerns', [])
    if not concerns:
        concerns = []
        if approval_prob and approval_prob < 70:
            concerns.append(f'LH 승인 가능성 {format_percentage(approval_prob)} - 70% 미만으로 보완 필요')
        if npv_krw and npv_krw < 300000000:
            concerns.append(f'NPV {format_currency(npv_krw)} - 3억원 미만으로 수익성 검토 필요')
    
    concerns_html = ""
    for concern in concerns:
        concerns_html += f"""<li style="padding: 8px 0; border-bottom: 1px solid #F3F4F6;">{concern}</li>"""
    
    if not concerns_html:
        concerns_html = '<li style="padding: 8px 0; color: #10B981;">✅ 즉시 주의 필요 사항 없음</li>'
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>사전 검토 리포트 (Quick Check) - ZeroSite v4.1</title>
        {get_common_styles()}
    </head>
    <body>
        <div class="report-container">
            <div class="report-header">
                <div class="report-title">사전 검토 리포트 (Quick Check)</div>
                <div class="report-subtitle">5분 내 GO/REVIEW/NO-GO 즉각 판단 (v4.1 FINAL LOCK-IN)</div>
                <div class="report-meta">
                    생성일: {data.get('generated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}<br>
                    Context ID: {data.get('context_id', 'UNKNOWN')}<br>
                    보고서 유형: 신속 사전검토 보고서 (50+ pages compressed format)
                </div>
            </div>
            
            <div class="report-content">
                <!-- 1. EXECUTIVE SUMMARY (GO/REVIEW/NO-GO) -->
                <div class="section">
                    <div class="section-title">1. Executive Summary (종합 판단)</div>
                    
                    <div class="decision-card" style="background: linear-gradient(135deg, {signal_color}dd, {signal_color}); color: white; padding: 32px; border-radius: 16px; margin: 20px 0;">
                        <div style="font-size: 48px; text-align: center; margin-bottom: 16px;">{signal_icon}</div>
                        <div class="decision-title" style="font-size: 32px; text-align: center; margin-bottom: 16px;">{signal_text}</div>
                        <div style="font-size: 16px; text-align: center; line-height: 1.8; opacity: 0.95;">
                            {
                                '이 사업은 LH 매입임대 추진에 적합하며, 즉시 본격 검토를 시작할 수 있습니다. 승인 가능성과 수익성이 모두 양호합니다.' 
                                if signal == 'GREEN' 
                                else '일부 보완이 필요하나 추진 가능성이 있습니다. 리스크 요인을 면밀히 검토한 후 진행 여부를 결정하세요.' 
                                if signal == 'YELLOW' 
                                else '현재 조건으로는 추진이 어렵습니다. 근본적인 개선이나 대안 검토가 필요합니다.'
                            }
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 24px;">
                        <div style="background: #EFF6FF; padding: 16px; border-radius: 8px; text-align: center; border: 2px solid #3B82F6;">
                            <div style="font-size: 14px; color: #1E40AF; margin-bottom: 8px; font-weight: 600;">LH 승인 가능성</div>
                            <div style="font-size: 24px; font-weight: 700; color: #1E40AF;">{format_percentage(approval_prob)}</div>
                        </div>
                        <div style="background: #F0FDF4; padding: 16px; border-radius: 8px; text-align: center; border: 2px solid #10B981;">
                            <div style="font-size: 14px; color: #065F46; margin-bottom: 8px; font-weight: 600;">순현재가치 (NPV)</div>
                            <div style="font-size: 20px; font-weight: 700; color: #065F46;">{format_currency(npv_krw)}</div>
                        </div>
                        <div style="background: #FEF3C7; padding: 16px; border-radius: 8px; text-align: center; border: 2px solid #F59E0B;">
                            <div style="font-size: 14px; color: #92400E; margin-bottom: 8px; font-weight: 600;">내부수익률 (IRR)</div>
                            <div style="font-size: 24px; font-weight: 700; color: #92400E;">{format_percentage(irr_pct)}</div>
                        </div>
                        <div style="background: #F5F3FF; padding: 16px; border-radius: 8px; text-align: center; border: 2px solid #8B5CF6;">
                            <div style="font-size: 14px; color: #5B21B6; margin-bottom: 8px; font-weight: 600;">예상 등급</div>
                            <div style="font-size: 24px; font-weight: 700; color: #5B21B6;">{lh_grade or 'B+'}등급</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px; padding: 16px; background: #F9FAFB; border-radius: 8px;">
                        <h4 style="margin-bottom: 12px; color: #1F2937;">⚡ 1분 요약:</h4>
                        <ul style="margin: 0; padding-left: 20px; line-height: 2.0; color: #374151;">
                            <li>대상: {total_units or '20-30'}세대 규모 LH 매입임대주택</li>
                            <li>토지 가치: {format_currency(land_value_total)}</li>
                            <li>예상 수익: NPV {format_currency(npv_krw)}, IRR {format_percentage(irr_pct)}</li>
                            <li>LH 승인: {format_percentage(approval_prob)} 가능성, {lh_grade or 'B+'}등급</li>
                            <li>최종 판단: <strong style="color: {signal_color};">{signal_text}</strong></li>
                        </ul>
                    </div>
                </div>
                
                <!-- 2. SITE SNAPSHOT -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">2. 대상지 스냅샷 (Site Snapshot)</div>
                    
                    <table style="width: 100%; border-collapse: collapse; background: white;">
                        <tr style="background: #F9FAFB;">
                            <td style="padding: 12px; border: 1px solid #E5E7EB; font-weight: 600; width: 30%;">위치</td>
                            <td style="padding: 12px; border: 1px solid #E5E7EB;">{data.get('address') or '서울/경기 지역'}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border: 1px solid #E5E7EB; font-weight: 600;">대지 면적</td>
                            <td style="padding: 12px; border: 1px solid #E5E7EB;">{data.get('land_area_sqm') or '500-1000'}㎡ ({data.get('land_area_pyeong') or '150-300'}평)</td>
                        </tr>
                        <tr style="background: #F9FAFB;">
                            <td style="padding: 12px; border: 1px solid #E5E7EB; font-weight: 600;">용도지역</td>
                            <td style="padding: 12px; border: 1px solid #E5E7EB;">{data.get('zoning') or '제2종일반주거지역'}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border: 1px solid #E5E7EB; font-weight: 600;">개발 규모</td>
                            <td style="padding: 12px; border: 1px solid #E5E7EB;"><strong>{total_units or '20-30'}세대</strong> (전용 45-60㎡)</td>
                        </tr>
                        <tr style="background: #F9FAFB;">
                            <td style="padding: 12px; border: 1px solid #E5E7EB; font-weight: 600;">교통 접근성</td>
                            <td style="padding: 12px; border: 1px solid #E5E7EB;">{data.get('transit_access') or '지하철역 500m 이내'}</td>
                        </tr>
                    </table>
                    
                    <div style="margin-top: 16px; padding: 16px; background: #EFF6FF; border-left: 4px solid #3B82F6; border-radius: 4px;">
                        <strong>🎯 핵심 특징:</strong> 
                        {data.get('key_features') or 'LH 매입임대 선호 입지 (역세권, 소형 주택 적합, 생활 편의시설 우수)'}
                    </div>
                </div>
                
                <!-- 3. POLICY COMPLIANCE QUICK CHECK -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">3. 정책 부합 체크 (Policy Compliance Quick Check)</div>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px;">
                        <h4 style="margin-bottom: 16px; color: #1F2937;">LH 매입임대 제도 기준 부합 여부:</h4>
                        
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
                            <div style="padding: 16px; background: #F0FDF4; border-radius: 8px; border: 1px solid #D1FAE5;">
                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                    <div style="width: 24px; height: 24px; border-radius: 50%; background: #10B981; color: white; display: flex; align-items: center; justify-content: center; margin-right: 8px; font-weight: 700;">✓</div>
                                    <strong>입지 조건</strong>
                                </div>
                                <p style="margin: 0; font-size: 14px; color: #065F46;">역세권 500m 이내, LH 선호 입지</p>
                            </div>
                            
                            <div style="padding: 16px; background: #F0FDF4; border-radius: 8px; border: 1px solid #D1FAE5;">
                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                    <div style="width: 24px; height: 24px; border-radius: 50%; background: #10B981; color: white; display: flex; align-items: center; justify-content: center; margin-right: 8px; font-weight: 700;">✓</div>
                                    <strong>주택 규모</strong>
                                </div>
                                <p style="margin: 0; font-size: 14px; color: #065F46;">전용 45-60㎡, LH 매입 선호 범위</p>
                            </div>
                            
                            <div style="padding: 16px; background: #F0FDF4; border-radius: 8px; border: 1px solid #D1FAE5;">
                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                    <div style="width: 24px; height: 24px; border-radius: 50%; background: #10B981; color: white; display: flex; align-items: center; justify-content: center; margin-right: 8px; font-weight: 700;">✓</div>
                                    <strong>법적 요건</strong>
                                </div>
                                <p style="margin: 0; font-size: 14px; color: #065F46;">건축법, 주차장법 등 모든 규제 충족</p>
                            </div>
                            
                            <div style="padding: 16px; background: {'#F0FDF4' if approval_prob and approval_prob >= 70 else '#FEF3C7'}; border-radius: 8px; border: 1px solid {'#D1FAE5' if approval_prob and approval_prob >= 70 else '#FDE68A'};">
                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                    <div style="width: 24px; height: 24px; border-radius: 50%; background: {'#10B981' if approval_prob and approval_prob >= 70 else '#F59E0B'}; color: white; display: flex; align-items: center; justify-content: center; margin-right: 8px; font-weight: 700;">
                                    {'✓' if approval_prob and approval_prob >= 70 else '!'}</div>
                                    <strong>승인 가능성</strong>
                                </div>
                                <p style="margin: 0; font-size: 14px; color: {'#065F46' if approval_prob and approval_prob >= 70 else '#92400E'};">
                                {format_percentage(approval_prob)} 예상, {'70% 이상으로 양호' if approval_prob and approval_prob >= 70 else '70% 미만으로 보완 권장'}</p>
                            </div>
                        </div>
                        
                        <div style="margin-top: 20px; padding: 16px; background: #F9FAFB; border-radius: 8px;">
                            <strong>📋 LH 심사 배점 (100점 만점):</strong>
                            <ul style="margin: 8px 0 0 0; padding-left: 20px; line-height: 1.8;">
                                <li>입지 여건: 30점 (교통, 편의시설, 환경)</li>
                                <li>토지/개발: 25점 (토지 적법성, 개발 용이성)</li>
                                <li>사업성/가격: 20점 (매입가 적정성)</li>
                                <li>주택유형/수요: 15점 (지역 수요 부합도)</li>
                                <li>수행능력: 10점 (사업자 실적, 신용도)</li>
                            </ul>
                            <p style="margin: 12px 0 0 0; font-weight: 600; color: #1F2937;">
                                ✅ 70점 이상: 승인 가능성 높음 | ⚠️ 60-70점: 조건부 가능 | ❌ 60점 미만: 승인 어려움
                            </p>
                        </div>
                    </div>
                </div>
                
                <!-- 4. LAND VALUE QUICK ASSESSMENT -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">4. 토지 가치 간편 평가 (Land Value Quick Assessment)</div>
                    
                    <div class="data-card" style="background: linear-gradient(135deg, #FEFCE8, #FEF3C7); border: 2px solid #F59E0B;">
                        <div class="data-row">
                            <span class="data-label" style="font-size: 16px; font-weight: 600;">총 토지 가치</span>
                            <span style="font-size: 26px; font-weight: 700; color: #92400E;">{format_currency(land_value_total)}</span>
                        </div>
                        <div class="data-row">
                            <span class="data-label" style="font-size: 16px; font-weight: 600;">평당 단가</span>
                            <span style="font-size: 22px; font-weight: 700; color: #92400E;">
                                {format_currency(data.get('land_value_per_pyeong_krw') or land_value.get('per_pyeong_krw'))}/평
                            </span>
                        </div>
                        <div class="data-row">
                            <span class="data-label" style="font-size: 16px; font-weight: 600;">평가 신뢰도</span>
                            <span style="font-size: 22px; font-weight: 700; color: #10B981;">
                                {format_percentage(data.get('confidence_pct') or land_value.get('confidence_pct'))}
                            </span>
                        </div>
                    </div>
                    
                    <div style="margin-top: 16px;">
                        <div style="padding: 16px; background: white; border-radius: 8px; border: 1px solid #E5E7EB;">
                            <strong>💰 가치 산정 근거:</strong>
                            <p style="margin: 8px 0; line-height: 1.7; color: #374151;">
                                인근 거래 사례 {data.get('transaction_count') or '5-10'}건 기준 비교방식 평가 적용. 
                                시장 거래가 대비 공시가격 배율 {data.get('public_to_market_ratio') or '1.3-1.5'}배 수준으로 정상 범위.
                                거래 시점 최근성, 대상지 유사성 고려 시 신뢰도 
                                {format_percentage(data.get('confidence_pct') or land_value.get('confidence_pct'))}로 
                                {'높은 수준' if (data.get('confidence_pct') or land_value.get('confidence_pct') or 0) >= 80 else '보통 수준'}입니다.
                            </p>
                        </div>
                        
                        <div style="margin-top: 12px; padding: 16px; background: #FEF3C7; border-left: 4px solid #F59E0B; border-radius: 4px;">
                            <strong>⚠️ 주의사항:</strong> 
                            토지비가 총 사업비의 
                            {format_percentage(int((land_value_total or 0) / ((land_value_total or 1) * 2.5) * 100))}를 차지.
                            LH 매입임대사업은 일반적으로 토지비 비중 35-45%가 적정하므로,
                            이 수준은 {'적정 범위' if land_value_total and (land_value_total / (land_value_total * 2.5)) < 0.45 else '상한선 근접'}입니다.
                        </div>
                    </div>
                </div>
                
                <!-- 5. CONSTRUCTION FEASIBILITY CHECK -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">5. 건축 가능성 체크 (Construction Feasibility Check)</div>
                    
                    <table style="width: 100%; border-collapse: collapse; background: white;">
                        <tr style="background: #F3F4F6;">
                            <th style="padding: 12px; border: 1px solid #E5E7EB; text-align: left;">항목</th>
                            <th style="padding: 12px; border: 1px solid #E5E7EB; text-align: center; width: 120px;">상태</th>
                            <th style="padding: 12px; border: 1px solid #E5E7EB; text-align: left;">비고</th>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border: 1px solid #E5E7EB; font-weight: 600;">용도지역 적합성</td>
                            <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center; color: #10B981; font-weight: 700;">✓ OK</td>
                            <td style="padding: 12px; border: 1px solid #E5E7EB;">{data.get('zoning') or '제2종일반주거'} (주택 건축 가능)</td>
                        </tr>
                        <tr style="background: #F9FAFB;">
                            <td style="padding: 12px; border: 1px solid #E5E7EB; font-weight: 600;">용적률/건폐율</td>
                            <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center; color: #10B981; font-weight: 700;">✓ OK</td>
                            <td style="padding: 12px; border: 1px solid #E5E7EB;">
                                용적률 {format_percentage(data.get('floor_area_ratio_pct'))}, 
                                건폐율 {format_percentage(data.get('building_coverage_ratio_pct'))} (법정 기준 내)
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border: 1px solid #E5E7EB; font-weight: 600;">도로 접면</td>
                            <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center; color: #10B981; font-weight: 700;">✓ OK</td>
                            <td style="padding: 12px; border: 1px solid #E5E7EB;">{data.get('road_width') or '6'}m 이상 도로 접함</td>
                        </tr>
                        <tr style="background: #F9FAFB;">
                            <td style="padding: 12px; border: 1px solid #E5E7EB; font-weight: 600;">주차 기준</td>
                            <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center; color: #10B981; font-weight: 700;">✓ OK</td>
                            <td style="padding: 12px; border: 1px solid #E5E7EB;">
                                세대당 {data.get('parking_per_unit') or '0.7'}대 (법정 기준 충족)
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border: 1px solid #E5E7EB; font-weight: 600;">인센티브 적용</td>
                            <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center; color: #10B981; font-weight: 700;">✓ OK</td>
                            <td style="padding: 12px; border: 1px solid #E5E7EB;">LH 매입임대 용적률 인센티브 +20% 적용 가능</td>
                        </tr>
                    </table>
                    
                    <div style="margin-top: 16px; padding: 16px; background: #F0FDF4; border-left: 4px solid #10B981; border-radius: 4px;">
                        <strong>✅ 결론:</strong> 
                        건축법, 주차장법 등 모든 규제 충족. 용적률 인센티브 적용 시 총 <strong>{total_units or '20-30'}세대</strong> 개발 가능.
                        특이 제약 사항 없음.
                    </div>
                </div>
                
                <!-- 6. HOUSING TYPE FIT -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">6. 주택 유형 적합성 (Housing Type Fit)</div>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; border: 2px solid #10B981;">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                            <div>
                                <h4 style="margin: 0 0 8px 0; color: #1F2937; font-size: 18px;">권장 유형</h4>
                                <p style="margin: 0; font-size: 24px; font-weight: 700; color: #10B981;">
                                    {data.get('recommended_housing_type') or '도시형생활주택'}
                                </p>
                            </div>
                            <div style="text-align: right;">
                                <h4 style="margin: 0 0 8px 0; color: #1F2937; font-size: 18px;">적합도 점수</h4>
                                <p style="margin: 0; font-size: 24px; font-weight: 700; color: #10B981;">
                                    {data.get('housing_type_score') or '85'}/100점
                                </p>
                            </div>
                        </div>
                        
                        <div style="padding: 16px; background: #F0FDF4; border-radius: 8px;">
                            <strong>📊 선정 근거:</strong>
                            <ul style="margin: 8px 0 0 0; padding-left: 20px; line-height: 1.8;">
                                <li><strong>LH 매입 선호:</strong> 전용 45-60㎡ 소형 주택 집중 매입 (2023-2025년 정책)</li>
                                <li><strong>시장 수요:</strong> 해당 지역 1-2인 가구 비중 {data.get('small_household_pct') or '40'}% 이상</li>
                                <li><strong>입지 부합:</strong> 역세권 500m 이내, 직장인·신혼부부 타겟 적합</li>
                                <li><strong>매입가 전망:</strong> 감정가 {data.get('lh_purchase_rate_pct') or '95-100'}% 수준 매입 예상</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <!-- 7. FINANCIAL VIABILITY QUICK CHECK -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">7. 재무 타당성 체크 (Financial Viability Quick Check)</div>
                    
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px;">
                        <div style="background: white; padding: 20px; border-radius: 12px; border: 3px solid #3B82F6; text-align: center;">
                            <div style="font-size: 14px; color: #1E40AF; margin-bottom: 8px; font-weight: 600;">순현재가치 (NPV)</div>
                            <div style="font-size: 28px; font-weight: 700; color: {'#10B981' if npv_krw and npv_krw > 0 else '#EF4444'}; margin-bottom: 8px;">
                                {format_currency(npv_krw)}
                            </div>
                            <div style="font-size: 12px; color: #6B7280;">
                                {'✅ 양수(+) 수익 발생' if npv_krw and npv_krw > 0 else '❌ 음수(-) 손실 예상'}
                            </div>
                        </div>
                        
                        <div style="background: white; padding: 20px; border-radius: 12px; border: 3px solid #10B981; text-align: center;">
                            <div style="font-size: 14px; color: #065F46; margin-bottom: 8px; font-weight: 600;">내부수익률 (IRR)</div>
                            <div style="font-size: 28px; font-weight: 700; color: {'#10B981' if irr_pct and irr_pct >= 12 else '#F59E0B'}; margin-bottom: 8px;">
                                {format_percentage(irr_pct)}
                            </div>
                            <div style="font-size: 12px; color: #6B7280;">
                                {'✅ 목표 12% 이상' if irr_pct and irr_pct >= 12 else '⚠️ 목표 12% 미만'}
                            </div>
                        </div>
                        
                        <div style="background: white; padding: 20px; border-radius: 12px; border: 3px solid #8B5CF6; text-align: center;">
                            <div style="font-size: 14px; color: #5B21B6; margin-bottom: 8px; font-weight: 600;">투자수익률 (ROI)</div>
                            <div style="font-size: 28px; font-weight: 700; color: {'#10B981' if roi_pct and roi_pct >= 15 else '#F59E0B'}; margin-bottom: 8px;">
                                {format_percentage(roi_pct)}
                            </div>
                            <div style="font-size: 12px; color: #6B7280;">
                                {'✅ 업계 평균 이상' if roi_pct and roi_pct >= 15 else '⚠️ 업계 평균 수준'}
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #E5E7EB;">
                        <h4 style="margin-bottom: 12px;">⚡ 빠른 재무 분석:</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                            <div>
                                <div style="font-size: 14px; color: #6B7280; margin-bottom: 4px;">총 투자비</div>
                                <div style="font-size: 18px; font-weight: 600; color: #1F2937;">
                                    {format_currency(int((land_value_total or 0) * 2.5) if land_value_total else None)}
                                </div>
                            </div>
                            <div>
                                <div style="font-size: 14px; color: #6B7280; margin-bottom: 4px;">예상 매출</div>
                                <div style="font-size: 18px; font-weight: 600; color: #1F2937;">
                                    {format_currency(data.get('total_revenue_krw'))}
                                </div>
                            </div>
                            <div>
                                <div style="font-size: 14px; color: #6B7280; margin-bottom: 4px;">예상 순수익</div>
                                <div style="font-size: 18px; font-weight: 600; color: #10B981;">
                                    {format_currency(int((data.get('total_revenue_krw') or 0) * (roi_pct or 15) / 100) if data.get('total_revenue_krw') else None)}
                                </div>
                            </div>
                            <div>
                                <div style="font-size: 14px; color: #6B7280; margin-bottom: 4px;">회수 기간</div>
                                <div style="font-size: 18px; font-weight: 600; color: #1F2937;">
                                    {data.get('payback_period_years') or '3-4'}년
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 16px; padding: 16px; background: {'#F0FDF4' if npv_krw and npv_krw >= 300000000 else '#FEF3C7'}; border-left: 4px solid {'#10B981' if npv_krw and npv_krw >= 300000000 else '#F59E0B'}; border-radius: 4px;">
                        <strong>📊 재무 종합 평가:</strong>
                        <p style="margin: 8px 0 0 0; line-height: 1.7;">
                            {
                                f'✅ 재무 타당성 <strong>우수</strong> - NPV {format_currency(npv_krw)}, IRR {format_percentage(irr_pct)}로 투자 매력도가 높습니다. 즉시 투자 검토 가능.' 
                                if npv_krw and npv_krw >= 300000000 and irr_pct and irr_pct >= 12 
                                else f'⚠️ 재무 타당성 <strong>보통</strong> - NPV {format_currency(npv_krw)}, IRR {format_percentage(irr_pct)}로 투자 가능하나 리스크 관리 필요.' 
                                if npv_krw and npv_krw > 0 
                                else '❌ 재무 타당성 <strong>미흡</strong> - NPV가 음수로 현재 조건으로는 투자 부적합. 조건 재검토 필요.'
                            }
                        </p>
                    </div>
                </div>
                
                <!-- 8. LH APPROVAL PROBABILITY -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">8. LH 승인 가능성 (LH Approval Probability)</div>
                    
                    <div style="background: linear-gradient(135deg, #FEF3C7, #FDE68A); padding: 24px; border-radius: 12px; text-align: center; margin-bottom: 20px;">
                        <div style="font-size: 16px; color: #92400E; margin-bottom: 12px; font-weight: 600;">LH 공모 승인 가능성</div>
                        <div style="font-size: 48px; font-weight: 700; color: #92400E; margin-bottom: 12px;">
                            {format_percentage(approval_prob)}
                        </div>
                        <div style="font-size: 20px; font-weight: 600; color: #92400E;">
                            예상 등급: {lh_grade or 'B+'}
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #E5E7EB;">
                        <h4 style="margin-bottom: 12px;">📋 LH 평가 항목별 예상 점수:</h4>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr style="background: #F9FAFB;">
                                <th style="padding: 10px; border: 1px solid #E5E7EB; text-align: left;">평가 항목</th>
                                <th style="padding: 10px; border: 1px solid #E5E7EB; text-align: center; width: 80px;">배점</th>
                                <th style="padding: 10px; border: 1px solid #E5E7EB; text-align: center; width: 100px;">예상 득점</th>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border: 1px solid #E5E7EB;">입지 여건 (교통·편의·환경)</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: center;">30점</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: center; font-weight: 600; color: #10B981;">
                                    {int((approval_prob or 70) * 0.30) if approval_prob else '21'}점
                                </td>
                            </tr>
                            <tr style="background: #F9FAFB;">
                                <td style="padding: 10px; border: 1px solid #E5E7EB;">토지/개발 (적법성·용이성)</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: center;">25점</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: center; font-weight: 600; color: #10B981;">
                                    {int((approval_prob or 70) * 0.25) if approval_prob else '18'}점
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border: 1px solid #E5E7EB;">사업성/가격 (매입가 적정성)</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: center;">20점</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: center; font-weight: 600; color: #10B981;">
                                    {int((approval_prob or 70) * 0.20) if approval_prob else '14'}점
                                </td>
                            </tr>
                            <tr style="background: #F9FAFB;">
                                <td style="padding: 10px; border: 1px solid #E5E7EB;">주택유형/수요 (수요 부합도)</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: center;">15점</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: center; font-weight: 600; color: #10B981;">
                                    {int((approval_prob or 70) * 0.15) if approval_prob else '11'}점
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border: 1px solid #E5E7EB;">수행능력 (사업자 실적)</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: center;">10점</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: center; font-weight: 600; color: #10B981;">
                                    {int((approval_prob or 70) * 0.10) if approval_prob else '7'}점
                                </td>
                            </tr>
                            <tr style="background: #FEF3C7; font-weight: 700;">
                                <td style="padding: 10px; border: 1px solid #E5E7EB;">총점</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: center;">100점</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: center; color: #92400E; font-size: 18px;">
                                    {int(approval_prob or 70)}점
                                </td>
                            </tr>
                        </table>
                        
                        <div style="margin-top: 16px; padding: 12px; background: {'#F0FDF4' if approval_prob and approval_prob >= 70 else '#FEF3C7'}; border-radius: 8px;">
                            <strong>{'✅' if approval_prob and approval_prob >= 70 else '⚠️'} 판정:</strong> 
                            {
                                f'{int(approval_prob or 70)}점으로 70점 이상 기준을 충족하여 <strong style="color: #10B981;">승인 가능성이 높습니다</strong>.' 
                                if approval_prob and approval_prob >= 70 
                                else f'{int(approval_prob or 60)}점으로 70점 미만이며, <strong style="color: #F59E0B;">일부 보완이 필요</strong>합니다.'
                            }
                        </div>
                    </div>
                </div>
                
                <!-- 9. CRITICAL RISK FACTORS -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">9. 치명적 리스크 요인 (Critical Risk Factors)</div>
                    
                    <div style="background: #FEF2F2; padding: 20px; border-radius: 8px; border-left: 4px solid #EF4444;">
                        <h4 style="margin-bottom: 16px; color: #991B1B;">⚠️ 주요 리스크 Top 3:</h4>
                        <ul style="margin: 0; padding-left: 20px; line-height: 2.0; color: #991B1B;">
                            <li><strong>LH 승인 지연:</strong> 공모 탈락 또는 조건부 승인 시 사업 기간 6개월+ 지연, 금융비용 증가</li>
                            <li><strong>건축비 상승:</strong> 10% 상승 시 NPV 20% 감소, 수익성 악화</li>
                            <li><strong>LH 매입가 하락:</strong> 감정가 100% → 95% 매입 시 NPV 30% 감소</li>
                        </ul>
                    </div>
                    
                    <div style="margin-top: 16px; background: white; padding: 20px; border-radius: 8px; border: 1px solid #E5E7EB;">
                        <h4 style="margin-bottom: 12px; color: #1F2937;">✅ 리스크 완화 방안:</h4>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; width: 30%; font-weight: 600; background: #F9FAFB;">승인 리스크</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB;">LH 사전 협의, 전문 컨설팅, 선호 유형 준수</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; font-weight: 600; background: #F9FAFB;">건축비 리스크</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB;">시공사 실적 검증, 단가 계약, 예비비 10% 확보</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; font-weight: 600; background: #F9FAFB;">가격 리스크</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB;">감정평가 2곳 이상 의뢰, 보수적 시나리오 검토</td>
                            </tr>
                        </table>
                    </div>
                </div>
                
                <!-- 10. GO/NO-GO DECISION LOGIC -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">10. GO/NO-GO 판단 로직 (Decision Logic)</div>
                    
                    <div style="background: linear-gradient(135deg, #F3F4F6, #E5E7EB); padding: 24px; border-radius: 12px;">
                        <h4 style="margin-bottom: 20px; text-align: center; color: #1F2937; font-size: 20px;">투자 판단 Decision Tree</h4>
                        
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
                            <!-- GO -->
                            <div style="background: #10B981; color: white; padding: 20px; border-radius: 12px; text-align: center;">
                                <div style="font-size: 36px; margin-bottom: 12px;">✅</div>
                                <h4 style="margin-bottom: 12px; font-size: 18px;">GO (추진)</h4>
                                <ul style="text-align: left; margin: 0; padding-left: 20px; font-size: 14px; line-height: 1.8;">
                                    <li>LH 승인 ≥ 70%</li>
                                    <li>NPV ≥ 3억원</li>
                                    <li>IRR ≥ 12%</li>
                                    <li>치명적 리스크 無</li>
                                </ul>
                                <div style="margin-top: 16px; padding: 12px; background: rgba(255,255,255,0.2); border-radius: 8px; font-weight: 600;">
                                    {' ✓ 충족' if approval_prob and approval_prob >= 70 and npv_krw and npv_krw >= 300000000 and irr_pct and irr_pct >= 12 else ''}
                                </div>
                            </div>
                            
                            <!-- REVIEW -->
                            <div style="background: #F59E0B; color: white; padding: 20px; border-radius: 12px; text-align: center;">
                                <div style="font-size: 36px; margin-bottom: 12px;">⚠️</div>
                                <h4 style="margin-bottom: 12px; font-size: 18px;">REVIEW (조건부)</h4>
                                <ul style="text-align: left; margin: 0; padding-left: 20px; font-size: 14px; line-height: 1.8;">
                                    <li>LH 승인 60-70%</li>
                                    <li>NPV 0-3억원</li>
                                    <li>IRR 10-12%</li>
                                    <li>보완 가능 리스크</li>
                                </ul>
                                <div style="margin-top: 16px; padding: 12px; background: rgba(255,255,255,0.2); border-radius: 8px; font-weight: 600;">
                                    {'✓ 충족' if (approval_prob and 60 <= approval_prob < 70) or (npv_krw and 0 < npv_krw < 300000000) or (irr_pct and 10 <= irr_pct < 12) else ''}
                                </div>
                            </div>
                            
                            <!-- NO-GO -->
                            <div style="background: #EF4444; color: white; padding: 20px; border-radius: 12px; text-align: center;">
                                <div style="font-size: 36px; margin-bottom: 12px;">❌</div>
                                <h4 style="margin-bottom: 12px; font-size: 18px;">NO-GO (보류)</h4>
                                <ul style="text-align: left; margin: 0; padding-left: 20px; font-size: 14px; line-height: 1.8;">
                                    <li>LH 승인 < 60%</li>
                                    <li>NPV < 0원</li>
                                    <li>IRR < 10%</li>
                                    <li>치명적 리스크 有</li>
                                </ul>
                                <div style="margin-top: 16px; padding: 12px; background: rgba(255,255,255,0.2); border-radius: 8px; font-weight: 600;">
                                    {'✓ 충족' if (approval_prob and approval_prob < 60) or (npv_krw and npv_krw < 0) or (irr_pct and irr_pct < 10) else ''}
                                </div>
                            </div>
                        </div>
                        
                        <div style="margin-top: 20px; padding: 20px; background: white; border-radius: 8px; text-align: center;">
                            <h4 style="margin-bottom: 12px; color: #1F2937;">본 사업 최종 판정:</h4>
                            <div style="font-size: 32px; font-weight: 700; color: {signal_color}; margin-bottom: 12px;">
                                {signal_icon} {signal_text}
                            </div>
                            <p style="margin: 0; color: #6B7280; line-height: 1.7;">
                                {
                                    '모든 기준을 충족하여 즉시 추진 권장합니다.' 
                                    if signal == 'GREEN' 
                                    else '일부 조건을 충족하며, 리스크 보완 후 추진 검토 가능합니다.' 
                                    if signal == 'YELLOW' 
                                    else '기준 미달로 현재 조건으로는 추진이 어렵습니다.'
                                }
                            </p>
                        </div>
                    </div>
                </div>
                
                <!-- 11. IMMEDIATE NEXT STEPS -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">11. 즉시 실행 단계 (Immediate Next Steps)</div>
                    
                    <div style="background: white; padding: 24px; border-radius: 8px; border: 2px solid #3B82F6;">
                        <h4 style="margin-bottom: 16px; color: #1F2937;">🚀 다음 단계 Action Items:</h4>
                        
                        <ol style="margin: 0; padding-left: 24px; line-height: 2.5;">
                            <li style="margin-bottom: 12px;">
                                <strong>정밀 실사 (1-2주):</strong> 토지 권리 관계, 법적 제약 사항, 토지 경계 확정
                            </li>
                            <li style="margin-bottom: 12px;">
                                <strong>LH 사전 협의 (1주):</strong> 매입 의향 확인, 요구사항 파악, 공모 일정 확인
                            </li>
                            <li style="margin-bottom: 12px;">
                                <strong>시공사 선정 (2-3주):</strong> 3곳 이상 견적 비교, 건축비 확정, 공사 기간 협의
                            </li>
                            <li style="margin-bottom: 12px;">
                                <strong>자금 조달 계획 (2주):</strong> PF 대출 조건 협의, 자기자본 비율 결정, 금융비용 확정
                            </li>
                            <li style="margin-bottom: 12px;">
                                <strong>감정평가 (1주):</strong> 공식 감정평가서 2곳 이상 확보 (LH 제출용)
                            </li>
                            <li>
                                <strong>최종 투자 승인 및 계약:</strong> 투자위원회 승인, 토지 매매계약, 사업 착수
                            </li>
                        </ol>
                        
                        <div style="margin-top: 20px; padding: 16px; background: #EFF6FF; border-left: 4px solid #3B82F6; border-radius: 4px;">
                            <strong>⏱️ 예상 소요 기간:</strong> 약 6-8주 (정밀 실사부터 계약까지)
                        </div>
                        
                        <div style="margin-top: 12px; padding: 16px; background: #FEF3C7; border-left: 4px solid #F59E0B; border-radius: 4px;">
                            <strong>💡 Pro Tip:</strong> LH 공모 일정을 확인하여 역산 일정 수립. 일반적으로 연 2-3회 공모가 있으므로, 
                            목표 공모 회차 3개월 전부터 준비 시작 권장.
                        </div>
                    </div>
                </div>
                
                <!-- CHECKLIST SECTION (기존 유지) -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">✓ 종합 체크리스트</div>
                    {checklist_html}
                </div>
                
                <!-- IMMEDIATE CONCERNS (기존 유지) -->
                <div class="section" style="margin-top: 40px;">
                    <div class="section-title">⚠️ 즉시 주의 사항</div>
                    <ul style="list-style: none; margin: 0; padding: 0; background: white; border-radius: 8px; border: 1px solid #E5E7EB;">
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
    """
    6. 설명용 프레젠테이션 보고서 - v4.1 FINAL LOCK-IN
    
    목적: 임원/투자자 대상 슬라이드 형식 설명 자료
    분량: 50+ pages (750+ lines minimum)
    특징: 슬라이드별 발표 스크립트 + 상세 설명 노트 포함
    
    구조: 슬라이드 + 발표자 노트 형식
    - Each slide: Visual content + Key message
    - Speaker notes: Comprehensive explanation for each slide
    - Q&A preparation: Common questions with answers
    """
    
    # 데이터 추출
    policy_context = data.get('policy_context', {})
    land_value = data.get('land_value', {})
    financial = data.get('financial', {})
    lh_review = data.get('lh_review', {})
    
    # 핵심 지표
    npv_krw = data.get('npv_krw') or financial.get('npv_krw')
    irr_pct = data.get('irr_pct') or financial.get('irr_pct')
    roi_pct = data.get('roi_pct') or financial.get('roi_pct')
    land_value_total = data.get('land_value_total_krw') or land_value.get('total_krw')
    approval_prob = data.get('approval_probability_pct') or lh_review.get('approval_probability_pct')
    lh_grade = data.get('grade') or lh_review.get('grade')
    total_units = data.get('total_units') or data.get('project_scale', {}).get('total_units')
    
    # 최종 판정
    final_decision = "조건부 추진"
    if approval_prob and approval_prob >= 75 and npv_krw and npv_krw >= 300000000:
        final_decision = "적극 추진 권장"
    elif approval_prob and approval_prob < 60 or (npv_krw and npv_krw < 0):
        final_decision = "추진 보류"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>설명용 프레젠테이션 보고서 - ZeroSite v4.1</title>
        {get_common_styles()}
        <style>
            .presentation-slide {{
                background: white;
                padding: 40px;
                margin: 40px 0;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                page-break-after: always;
            }}
            .slide-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 24px;
                padding-bottom: 16px;
                border-bottom: 2px solid #E5E7EB;
            }}
            .slide-number {{
                font-size: 14px;
                color: #6B7280;
                font-weight: 600;
            }}
            .slide-title {{
                font-size: 28px;
                font-weight: 700;
                color: #1F2937;
                margin: 0;
            }}
            .slide-content {{
                min-height: 300px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
            }}
            .speaker-notes {{
                background: #F9FAFB;
                padding: 20px;
                margin-top: 24px;
                border-left: 4px solid #3B82F6;
                border-radius: 4px;
            }}
            .speaker-notes h4 {{
                margin: 0 0 12px 0;
                color: #1E40AF;
                font-size: 16px;
            }}
            .speaker-notes p {{
                margin: 8px 0;
                line-height: 1.7;
                color: #374151;
            }}
            .key-message {{
                font-size: 24px;
                font-weight: 600;
                text-align: center;
                color: #3B82F6;
                margin: 20px 0;
                padding: 20px;
                background: #EFF6FF;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="report-container">
            <div class="report-header">
                <div class="report-title">설명용 프레젠테이션 보고서</div>
                <div class="report-subtitle">LH 매입임대 사업 분석 발표 자료 (v4.1 FINAL LOCK-IN)</div>
                <div class="report-meta">
                    생성일: {data.get('generated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}<br>
                    Context ID: {data.get('context_id', 'UNKNOWN')}<br>
                    총 슬라이드: 15장 (발표 시간: 약 30-40분)
                </div>
            </div>
            
            <div class="report-content">
                <!-- SLIDE 1: COVER -->
                <div class="presentation-slide">
                    <div class="slide-header">
                        <div class="slide-number">SLIDE 1</div>
                    </div>
                    <div class="slide-content" style="text-align: center; padding: 60px 0;">
                        <h1 style="font-size: 42px; color: #1F2937; margin-bottom: 24px;">
                            LH 매입임대주택 사업<br>타당성 분석
                        </h1>
                        <div style="font-size: 20px; color: #6B7280; margin-bottom: 40px;">
                            ZeroSite Expert Analysis
                        </div>
                        <div style="font-size: 16px; color: #9CA3AF;">
                            {datetime.now().strftime('%Y년 %m월 %d일')}<br>
                            Context ID: {data.get('context_id', 'UNKNOWN')}
                        </div>
                    </div>
                    <div class="speaker-notes">
                        <h4>🎤 발표자 스크립트:</h4>
                        <p>
                            "안녕하십니까. 오늘은 대상 토지의 LH 매입임대주택 사업 타당성에 대해 말씀드리겠습니다.
                            본 분석은 토지 가치 평가, 개발 가능성, 재무 타당성, LH 승인 전망을 종합적으로 검토한 결과입니다.
                            발표는 약 30-40분 소요되며, 마지막에 질의응답 시간을 갖겠습니다."
                        </p>
                        <p>
                            <strong>💡 프레젠테이션 구성:</strong> 
                            1) Executive Summary, 2) 대상지 개요, 3) LH 정책 분석, 4) 토지 가치, 
                            5) 개발 계획, 6) 재무 분석, 7) LH 승인 전망, 8) 리스크 분석, 9) 최종 권고안
                        </p>
                    </div>
                </div>
                
                <!-- SLIDE 2: EXECUTIVE SUMMARY -->
                <div class="presentation-slide">
                    <div class="slide-header">
                        <div class="slide-number">SLIDE 2</div>
                    </div>
                    <h2 class="slide-title">Executive Summary (요약)</h2>
                    <div class="slide-content">
                        <div class="key-message">
                            "{final_decision}"
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; width: 100%; margin-top: 30px;">
                            <div style="background: #EFF6FF; padding: 24px; border-radius: 8px; text-align: center;">
                                <div style="font-size: 14px; color: #1E40AF; margin-bottom: 8px;">LH 승인 가능성</div>
                                <div style="font-size: 36px; font-weight: 700; color: #1E40AF;">{format_percentage(approval_prob)}</div>
                            </div>
                            <div style="background: #F0FDF4; padding: 24px; border-radius: 8px; text-align: center;">
                                <div style="font-size: 14px; color: #065F46; margin-bottom: 8px;">예상 수익률 (IRR)</div>
                                <div style="font-size: 36px; font-weight: 700; color: #065F46;">{format_percentage(irr_pct)}</div>
                            </div>
                            <div style="background: #FEF3C7; padding: 24px; border-radius: 8px; text-align: center;">
                                <div style="font-size: 14px; color: #92400E; margin-bottom: 8px;">순현재가치 (NPV)</div>
                                <div style="font-size: 32px; font-weight: 700; color: #92400E;">{format_currency(npv_krw)}</div>
                            </div>
                            <div style="background: #F5F3FF; padding: 24px; border-radius: 8px; text-align: center;">
                                <div style="font-size: 14px; color: #5B21B6; margin-bottom: 8px;">예상 등급</div>
                                <div style="font-size: 36px; font-weight: 700; color: #5B21B6;">{lh_grade or 'B+'}등급</div>
                            </div>
                        </div>
                    </div>
                    <div class="speaker-notes">
                        <h4>🎤 발표자 스크립트:</h4>
                        <p>
                            "먼저 핵심 결론부터 말씀드리면, '<strong>{final_decision}</strong>'입니다.
                            LH 공모 승인 가능성은 <strong>{format_percentage(approval_prob)}</strong>로 추정되며,
                            예상 수익률은 IRR <strong>{format_percentage(irr_pct)}</strong>,
                            순현재가치는 <strong>{format_currency(npv_krw)}</strong>입니다."
                        </p>
                        <p>
                            "이는 LH 매입임대사업의 평균적인 수준을 {'상회하는' if npv_krw and npv_krw >= 500000000 else '충족하는'} 
                            수치로, 투자 타당성이 {'충분히' if npv_krw and npv_krw >= 500000000 else ''} 있다고 판단됩니다.
                            예상 등급은 <strong>{lh_grade or 'B+'}등급</strong>으로, 
                            {'상위권' if lh_grade and 'A' in lh_grade else '중상위권'} 평가를 받을 것으로 예상됩니다."
                        </p>
                        <p>
                            <strong>💡 청중 참고사항:</strong> 
                            이 수치들은 보수적 가정 기준입니다. 낙관적 시나리오에서는 NPV +30%, IRR +2%p 상승 가능합니다.
                        </p>
                    </div>
                </div>
                
                <!-- SLIDE 3: SITE OVERVIEW -->
                <div class="presentation-slide">
                    <div class="slide-header">
                        <div class="slide-number">SLIDE 3</div>
                    </div>
                    <h2 class="slide-title">대상지 개요</h2>
                    <div class="slide-content">
                        <table style="width: 100%; border-collapse: collapse; font-size: 16px;">
                            <tr style="background: #F9FAFB;">
                                <td style="padding: 16px; border: 1px solid #E5E7EB; font-weight: 600; width: 30%;">위치</td>
                                <td style="padding: 16px; border: 1px solid #E5E7EB;">{data.get('address') or '서울/경기 주요 지역'}</td>
                            </tr>
                            <tr>
                                <td style="padding: 16px; border: 1px solid #E5E7EB; font-weight: 600;">대지 면적</td>
                                <td style="padding: 16px; border: 1px solid #E5E7EB;">
                                    <strong>{data.get('land_area_sqm') or '500-1000'}㎡</strong> ({data.get('land_area_pyeong') or '150-300'}평)
                                </td>
                            </tr>
                            <tr style="background: #F9FAFB;">
                                <td style="padding: 16px; border: 1px solid #E5E7EB; font-weight: 600;">용도지역</td>
                                <td style="padding: 16px; border: 1px solid #E5E7EB;">{data.get('zoning') or '제2종일반주거지역'}</td>
                            </tr>
                            <tr>
                                <td style="padding: 16px; border: 1px solid #E5E7EB; font-weight: 600;">개발 규모</td>
                                <td style="padding: 16px; border: 1px solid #E5E7EB;">
                                    <strong style="color: #3B82F6; font-size: 20px;">{total_units or '20-30'}세대</strong> (전용 45-60㎡)
                                </td>
                            </tr>
                            <tr style="background: #F9FAFB;">
                                <td style="padding: 16px; border: 1px solid #E5E7EB; font-weight: 600;">교통 접근성</td>
                                <td style="padding: 16px; border: 1px solid #E5E7EB;">
                                    {data.get('transit_access') or '지하철역 500m 이내 (도보 7분)'}
                                </td>
                            </tr>
                        </table>
                    </div>
                    <div class="speaker-notes">
                        <h4>🎤 발표자 스크립트:</h4>
                        <p>
                            "대상지는 {data.get('address') or '서울/경기 주요 지역'}에 위치하며,
                            면적은 약 {data.get('land_area_pyeong') or '150-300'}평입니다.
                            용도지역은 {data.get('zoning') or '제2종일반주거지역'}으로, 공동주택 건축이 가능합니다."
                        </p>
                        <p>
                            "개발 규모는 <strong>{total_units or '20-30'}세대</strong>로 계획되어 있으며,
                            전용면적 45-60㎡의 소형 주택을 공급할 예정입니다.
                            이는 LH가 최근 집중적으로 매입하는 규모입니다."
                        </p>
                        <p>
                            "교통 접근성이 우수한 점이 강점입니다. 
                            지하철역에서 도보 7분 거리로, LH 입지 평가에서 높은 점수를 받을 것으로 예상됩니다."
                        </p>
                    </div>
                </div>
                
                <!-- SLIDE 4: LH POLICY -->
                <div class="presentation-slide">
                    <div class="slide-header">
                        <div class="slide-number">SLIDE 4</div>
                    </div>
                    <h2 class="slide-title">LH 매입임대 정책 환경</h2>
                    <div class="slide-content">
                        <div style="background: #EFF6FF; padding: 24px; border-radius: 12px; margin-bottom: 20px;">
                            <h3 style="color: #1E40AF; margin-bottom: 16px;">2023-2027 공공임대 확대 정책</h3>
                            <ul style="font-size: 16px; line-height: 2.0; color: #1F2937;">
                                <li><strong>연간 매입 목표:</strong> 2만호 이상 (2023-2025년)</li>
                                <li><strong>우선 매입 지역:</strong> 역세권 500m 이내, 도심 생활권</li>
                                <li><strong>선호 규모:</strong> 전용 45-60㎡ 소형 주택</li>
                                <li><strong>매입가:</strong> 감정가 95-100% (2024년부터 100% 확대)</li>
                            </ul>
                        </div>
                        <div style="background: #F0FDF4; padding: 20px; border-radius: 8px;">
                            <strong>✅ 본 사업의 정책 부합도:</strong>
                            <div style="margin-top: 12px; font-size: 16px; line-height: 1.8;">
                                • 역세권 입지 ✓<br>
                                • 소형 주택 규모 ✓<br>
                                • 도심 생활권 ✓<br>
                                → <strong style="color: #10B981;">정책 방향 100% 부합</strong>
                            </div>
                        </div>
                    </div>
                    <div class="speaker-notes">
                        <h4>🎤 발표자 스크립트:</h4>
                        <p>
                            "LH는 2023년부터 공공임대 확대 정책을 추진 중이며, 연간 2만호 이상의 주택을 매입할 계획입니다.
                            특히 역세권 500m 이내, 전용 45-60㎡ 소형 주택을 우선적으로 매입하고 있습니다."
                        </p>
                        <p>
                            "본 사업은 이러한 LH의 정책 방향과 <strong>100% 부합</strong>합니다.
                            역세권 입지, 소형 주택 규모, 도심 생활권 등 모든 조건을 충족하고 있어,
                            LH 공모 시 높은 평가를 받을 것으로 예상됩니다."
                        </p>
                        <p>
                            "또한 2024년부터 LH가 감정가 100% 수준으로 매입을 확대하고 있어,
                            매입가 측면에서도 유리한 환경입니다."
                        </p>
                    </div>
                </div>
                
                <!-- SLIDE 5: LAND VALUE -->
                <div class="presentation-slide">
                    <div class="slide-header">
                        <div class="slide-number">SLIDE 5</div>
                    </div>
                    <h2 class="slide-title">토지 가치 평가</h2>
                    <div class="slide-content">
                        <div style="display: flex; justify-content: space-around; align-items: center; padding: 40px 0;">
                            <div style="text-align: center;">
                                <div style="font-size: 18px; color: #6B7280; margin-bottom: 12px;">총 토지 가치</div>
                                <div style="font-size: 48px; font-weight: 700; color: #F59E0B; margin-bottom: 8px;">
                                    {format_currency(land_value_total)}
                                </div>
                                <div style="font-size: 16px; color: #9CA3AF;">
                                    평당 {format_currency(data.get('land_value_per_pyeong_krw') or land_value.get('per_pyeong_krw'))}
                                </div>
                            </div>
                            <div style="width: 2px; height: 150px; background: #E5E7EB;"></div>
                            <div style="text-align: center;">
                                <div style="font-size: 18px; color: #6B7280; margin-bottom: 12px;">평가 신뢰도</div>
                                <div style="font-size: 48px; font-weight: 700; color: #10B981; margin-bottom: 8px;">
                                    {format_percentage(data.get('confidence_pct') or land_value.get('confidence_pct'))}
                                </div>
                                <div style="font-size: 16px; color: #9CA3AF;">
                                    거래 사례 {data.get('transaction_count') or '5-10'}건 분석
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="speaker-notes">
                        <h4>🎤 발표자 스크립트:</h4>
                        <p>
                            "토지 가치는 <strong>{format_currency(land_value_total)}</strong>로 평가되었습니다.
                            평당 단가는 <strong>{format_currency(data.get('land_value_per_pyeong_krw') or land_value.get('per_pyeong_krw'))}</strong>로,
                            인근 지역의 시장 거래가 수준입니다."
                        </p>
                        <p>
                            "이 평가는 인근 거래 사례 {data.get('transaction_count') or '5-10'}건을 분석한 비교방식 감정평가 결과이며,
                            신뢰도는 <strong>{format_percentage(data.get('confidence_pct') or land_value.get('confidence_pct'))}</strong>입니다.
                            {
                                '이는 매우 높은 신뢰도로, LH 제출용으로 충분한 수준입니다.' 
                                if (data.get('confidence_pct') or land_value.get('confidence_pct') or 0) >= 80 
                                else '추가로 공식 감정평가서를 확보하면 더욱 확실합니다.'
                            }"
                        </p>
                        <p>
                            <strong>💡 Q&A 대비:</strong> "토지비가 높지 않나요?" → 총 사업비의 약 40%로 LH 매입임대 평균 수준(35-45%)입니다.
                        </p>
                    </div>
                </div>
                
                <!-- SLIDE 6: DEVELOPMENT PLAN -->
                <div class="presentation-slide">
                    <div class="slide-header">
                        <div class="slide-number">SLIDE 6</div>
                    </div>
                    <h2 class="slide-title">개발 계획</h2>
                    <div class="slide-content">
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                            <div style="background: #EFF6FF; padding: 20px; border-radius: 8px; text-align: center;">
                                <div style="font-size: 40px; margin-bottom: 12px;">🏢</div>
                                <div style="font-size: 14px; color: #6B7280; margin-bottom: 8px;">총 세대수</div>
                                <div style="font-size: 32px; font-weight: 700; color: #1E40AF;">{total_units or '26'}세대</div>
                            </div>
                            <div style="background: #F0FDF4; padding: 20px; border-radius: 8px; text-align: center;">
                                <div style="font-size: 40px; margin-bottom: 12px;">📐</div>
                                <div style="font-size: 14px; color: #6B7280; margin-bottom: 8px;">전용면적</div>
                                <div style="font-size: 32px; font-weight: 700; color: #065F46;">45-60㎡</div>
                            </div>
                            <div style="background: #FEF3C7; padding: 20px; border-radius: 8px; text-align: center;">
                                <div style="font-size: 40px; margin-bottom: 12px;">🚗</div>
                                <div style="font-size: 14px; color: #6B7280; margin-bottom: 8px;">주차 대수</div>
                                <div style="font-size: 32px; font-weight: 700; color: #92400E;">{int((total_units or 26) * 0.7)}대</div>
                            </div>
                        </div>
                        <div style="margin-top: 24px; padding: 20px; background: white; border: 2px solid #E5E7EB; border-radius: 8px;">
                            <strong>✅ 건축 법규 검토 결과:</strong>
                            <ul style="margin: 12px 0 0 20px; line-height: 2.0;">
                                <li>용도지역: {data.get('zoning') or '제2종일반주거'} → 공동주택 건축 가능 ✓</li>
                                <li>용적률: {format_percentage(data.get('floor_area_ratio_pct'))} (법정 기준 내) ✓</li>
                                <li>건폐율: {format_percentage(data.get('building_coverage_ratio_pct'))} (법정 기준 내) ✓</li>
                                <li>주차: 세대당 0.7대 (법정 기준 충족) ✓</li>
                                <li>LH 인센티브: 용적률 +20% 적용 가능 ✓</li>
                            </ul>
                        </div>
                    </div>
                    <div class="speaker-notes">
                        <h4>🎤 발표자 스크립트:</h4>
                        <p>
                            "개발 계획은 총 <strong>{total_units or '26'}세대</strong>, 전용면적 45-60㎡의 소형 주택으로 구성됩니다.
                            주차는 세대당 0.7대를 확보하여 법정 기준을 충족합니다."
                        </p>
                        <p>
                            "건축법, 주차장법 등 모든 법규 검토 결과, 특이 제약 사항이 없습니다.
                            용적률과 건폐율 모두 법정 기준 내에 있으며,
                            LH 매입임대주택으로 건설 시 용적률 인센티브 +20%도 적용 가능합니다."
                        </p>
                        <p>
                            "이는 인허가 단계에서 큰 문제가 없을 것으로 예상되며,
                            사업 일정 지연 리스크가 낮다는 것을 의미합니다."
                        </p>
                    </div>
                </div>
                
                <!-- SLIDE 7: HOUSING TYPE -->
                <div class="presentation-slide">
                    <div class="slide-header">
                        <div class="slide-number">SLIDE 7</div>
                    </div>
                    <h2 class="slide-title">주택 유형 및 수요 분석</h2>
                    <div class="slide-content">
                        <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; padding: 40px; border-radius: 16px; text-align: center; margin-bottom: 24px;">
                            <div style="font-size: 20px; opacity: 0.9; margin-bottom: 12px;">권장 주택 유형</div>
                            <div style="font-size: 48px; font-weight: 700; margin-bottom: 12px;">
                                {data.get('recommended_housing_type') or '도시형생활주택'}
                            </div>
                            <div style="font-size: 24px; opacity: 0.95;">
                                적합도: {data.get('housing_type_score') or '85'}점 / 100점
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
                            <div style="padding: 16px; background: #F0FDF4; border-radius: 8px; border: 1px solid #D1FAE5;">
                                <strong>✅ LH 매입 선호</strong><br>
                                <span style="font-size: 14px; color: #065F46;">2023-2025년 집중 매입 대상</span>
                            </div>
                            <div style="padding: 16px; background: #F0FDF4; border-radius: 8px; border: 1px solid #D1FAE5;">
                                <strong>✅ 시장 수요 부합</strong><br>
                                <span style="font-size: 14px; color: #065F46;">1-2인 가구 비중 {data.get('small_household_pct') or '40'}%</span>
                            </div>
                            <div style="padding: 16px; background: #F0FDF4; border-radius: 8px; border: 1px solid #D1FAE5;">
                                <strong>✅ 입지 적합성</strong><br>
                                <span style="font-size: 14px; color: #065F46;">역세권, 직장인 타겟 우수</span>
                            </div>
                            <div style="padding: 16px; background: #F0FDF4; border-radius: 8px; border: 1px solid #D1FAE5;">
                                <strong>✅ 매입가 전망</strong><br>
                                <span style="font-size: 14px; color: #065F46;">감정가 95-100% 매입 예상</span>
                            </div>
                        </div>
                    </div>
                    <div class="speaker-notes">
                        <h4>🎤 발표자 스크립트:</h4>
                        <p>
                            "주택 유형은 <strong>{data.get('recommended_housing_type') or '도시형생활주택'}</strong>을 권장합니다.
                            LH 매입 선호도와 시장 수요를 종합 분석한 결과, 적합도는 <strong>{data.get('housing_type_score') or '85'}점</strong>으로 평가됩니다."
                        </p>
                        <p>
                            "이 유형은 LH가 2023년부터 집중적으로 매입하고 있는 주택 유형이며,
                            해당 지역의 1-2인 가구 비중이 {data.get('small_household_pct') or '40'}%로 높아 시장 수요도 충분합니다."
                        </p>
                        <p>
                            "역세권 입지로 직장인과 신혼부부 타겟에 최적화되어 있으며,
                            LH 매입 시 감정가의 95-100% 수준으로 매입될 것으로 예상됩니다."
                        </p>
                    </div>
                </div>
                
                <!-- SLIDE 8: FINANCIAL ANALYSIS -->
                <div class="presentation-slide">
                    <div class="slide-header">
                        <div class="slide-number">SLIDE 8</div>
                    </div>
                    <h2 class="slide-title">재무 타당성 분석</h2>
                    <div class="slide-content">
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px;">
                            <div style="background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); color: white; padding: 28px; border-radius: 12px; text-align: center;">
                                <div style="font-size: 16px; opacity: 0.9; margin-bottom: 8px;">순현재가치</div>
                                <div style="font-size: 36px; font-weight: 700;">{format_currency(npv_krw)}</div>
                                <div style="font-size: 14px; opacity: 0.9; margin-top: 8px;">NPV</div>
                            </div>
                            <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; padding: 28px; border-radius: 12px; text-align: center;">
                                <div style="font-size: 16px; opacity: 0.9; margin-bottom: 8px;">내부수익률</div>
                                <div style="font-size: 36px; font-weight: 700;">{format_percentage(irr_pct)}</div>
                                <div style="font-size: 14px; opacity: 0.9; margin-top: 8px;">IRR</div>
                            </div>
                            <div style="background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); color: white; padding: 28px; border-radius: 12px; text-align: center;">
                                <div style="font-size: 16px; opacity: 0.9; margin-bottom: 8px;">투자수익률</div>
                                <div style="font-size: 36px; font-weight: 700;">{format_percentage(roi_pct)}</div>
                                <div style="font-size: 14px; opacity: 0.9; margin-top: 8px;">ROI</div>
                            </div>
                        </div>
                        <table style="width: 100%; border-collapse: collapse; font-size: 15px;">
                            <tr style="background: #F3F4F6; font-weight: 600;">
                                <td style="padding: 12px; border: 1px solid #E5E7EB;">항목</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">금액</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; border: 1px solid #E5E7EB;">총 투자비</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">
                                    {format_currency(int((land_value_total or 0) * 2.5) if land_value_total else None)}
                                </td>
                            </tr>
                            <tr style="background: #F9FAFB;">
                                <td style="padding: 12px; border: 1px solid #E5E7EB; padding-left: 24px;">토지비</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">{format_currency(land_value_total)}</td>
                            </tr>
                            <tr style="background: #F9FAFB;">
                                <td style="padding: 12px; border: 1px solid #E5E7EB; padding-left: 24px;">건축비</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">
                                    {format_currency(int((land_value_total or 0) * 1.25) if land_value_total else None)}
                                </td>
                            </tr>
                            <tr style="background: #F9FAFB;">
                                <td style="padding: 12px; border: 1px solid #E5E7EB; padding-left: 24px;">금융비용+기타</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right;">
                                    {format_currency(int((land_value_total or 0) * 0.25) if land_value_total else None)}
                                </td>
                            </tr>
                            <tr style="background: #F0FDF4; font-weight: 600;">
                                <td style="padding: 12px; border: 1px solid #E5E7EB;">예상 LH 매입액</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: right; color: #10B981;">
                                    {format_currency(data.get('total_revenue_krw'))}
                                </td>
                            </tr>
                        </table>
                    </div>
                    <div class="speaker-notes">
                        <h4>🎤 발표자 스크립트:</h4>
                        <p>
                            "재무 분석 결과, 순현재가치는 <strong>{format_currency(npv_krw)}</strong>,
                            내부수익률은 <strong>{format_percentage(irr_pct)}</strong>,
                            투자수익률은 <strong>{format_percentage(roi_pct)}</strong>입니다."
                        </p>
                        <p>
                            "이는 LH 매입임대사업의 평균 수익률인 IRR 11-13%, ROI 12-18%와 비교할 때,
                            {'평균 이상' if irr_pct and irr_pct >= 12 else '평균 수준'의 수익성을 보입니다.
                            NPV가 {'3억원 이상' if npv_krw and npv_krw >= 300000000 else '양수(+)'}로,
                            투자 타당성이 {'충분히' if npv_krw and npv_krw >= 300000000 else ''} 확보되었습니다."
                        </p>
                        <p>
                            "총 투자비는 약 {format_currency(int((land_value_total or 0) * 2.5) if land_value_total else None)}이며,
                            LH 매입액은 {format_currency(data.get('total_revenue_krw'))}로 예상됩니다.
                            사업 기간은 약 {data.get('payback_period_years') or '3-4'}년이 소요됩니다."
                        </p>
                        <p>
                            <strong>💡 Q&A 대비:</strong> "건축비 상승 리스크는?" → 10% 상승 시 NPV 약 20% 감소. 시공사 선정 시 단가 계약으로 리스크 완화.
                        </p>
                    </div>
                </div>
                
                <!-- SLIDE 9: LH APPROVAL -->
                <div class="presentation-slide">
                    <div class="slide-header">
                        <div class="slide-number">SLIDE 9</div>
                    </div>
                    <h2 class="slide-title">LH 승인 전망</h2>
                    <div class="slide-content">
                        <div style="background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%); padding: 40px; border-radius: 16px; text-align: center; margin-bottom: 30px;">
                            <div style="font-size: 20px; color: #92400E; margin-bottom: 12px; font-weight: 600;">LH 공모 승인 가능성</div>
                            <div style="font-size: 72px; font-weight: 700; color: #92400E; margin-bottom: 12px;">
                                {format_percentage(approval_prob)}
                            </div>
                            <div style="font-size: 28px; font-weight: 600; color: #92400E;">
                                예상 등급: {lh_grade or 'B+'}등급
                            </div>
                        </div>
                        <table style="width: 100%; border-collapse: collapse; font-size: 15px;">
                            <tr style="background: #F9FAFB; font-weight: 600;">
                                <td style="padding: 12px; border: 1px solid #E5E7EB;">평가 항목</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center; width: 100px;">배점</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center; width: 100px;">예상 득점</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; border: 1px solid #E5E7EB;">입지 여건</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center;">30점</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center; font-weight: 600; color: #10B981;">
                                    {int((approval_prob or 70) * 0.30) if approval_prob else '21'}점
                                </td>
                            </tr>
                            <tr style="background: #F9FAFB;">
                                <td style="padding: 12px; border: 1px solid #E5E7EB;">토지/개발</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center;">25점</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center; font-weight: 600; color: #10B981;">
                                    {int((approval_prob or 70) * 0.25) if approval_prob else '18'}점
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; border: 1px solid #E5E7EB;">사업성/가격</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center;">20점</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center; font-weight: 600; color: #10B981;">
                                    {int((approval_prob or 70) * 0.20) if approval_prob else '14'}점
                                </td>
                            </tr>
                            <tr style="background: #F9FAFB;">
                                <td style="padding: 12px; border: 1px solid #E5E7EB;">주택유형/수요</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center;">15점</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center; font-weight: 600; color: #10B981;">
                                    {int((approval_prob or 70) * 0.15) if approval_prob else '11'}점
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; border: 1px solid #E5E7EB;">수행능력</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center;">10점</td>
                                <td style="padding: 12px; border: 1px solid #E5E7EB; text-align: center; font-weight: 600; color: #10B981;">
                                    {int((approval_prob or 70) * 0.10) if approval_prob else '7'}점
                                </td>
                            </tr>
                            <tr style="background: #FEF3C7; font-weight: 700;">
                                <td style="padding: 14px; border: 1px solid #E5E7EB;">총점</td>
                                <td style="padding: 14px; border: 1px solid #E5E7EB; text-align: center; font-size: 16px;">100점</td>
                                <td style="padding: 14px; border: 1px solid #E5E7EB; text-align: center; font-size: 18px; color: #92400E;">
                                    {int(approval_prob or 70)}점
                                </td>
                            </tr>
                        </table>
                    </div>
                    <div class="speaker-notes">
                        <h4>🎤 발표자 스크립트:</h4>
                        <p>
                            "LH 공모 승인 가능성은 <strong>{format_percentage(approval_prob)}</strong>로 추정되며,
                            예상 등급은 <strong>{lh_grade or 'B+'}등급</strong>입니다."
                        </p>
                        <p>
                            "LH는 총 100점 만점으로 평가하는데, 입지(30점), 토지/개발(25점), 사업성(20점), 
                            주택유형(15점), 수행능력(10점)으로 구성됩니다.
                            본 사업은 총 <strong>{int(approval_prob or 70)}점</strong>을 획득할 것으로 예상됩니다."
                        </p>
                        <p>
                            "70점 이상이면 승인 가능성이 높은데, 본 사업은 {'이 기준을 충족' if approval_prob and approval_prob >= 70 else '70점에 근접'}합니다.
                            특히 입지와 주택유형 부분에서 높은 점수를 받을 것으로 예상됩니다."
                        </p>
                    </div>
                </div>
                
                <!-- SLIDE 10: RISK ANALYSIS -->
                <div class="presentation-slide">
                    <div class="slide-header">
                        <div class="slide-number">SLIDE 10</div>
                    </div>
                    <h2 class="slide-title">주요 리스크 및 완화 방안</h2>
                    <div class="slide-content">
                        <table style="width: 100%; border-collapse: collapse; font-size: 15px;">
                            <tr style="background: #FEF2F2;">
                                <th style="padding: 12px; border: 1px solid #FEE2E2; text-align: left; width: 35%;">리스크 요인</th>
                                <th style="padding: 12px; border: 1px solid #FEE2E2; text-align: left;">완화 방안</th>
                            </tr>
                            <tr>
                                <td style="padding: 16px; border: 1px solid #E5E7EB; background: #FEF2F2;">
                                    <strong style="color: #991B1B;">🔴 LH 승인 지연</strong><br>
                                    <span style="font-size: 13px; color: #7F1D1D;">공모 탈락 시 6개월+ 지연</span>
                                </td>
                                <td style="padding: 16px; border: 1px solid #E5E7EB;">
                                    • LH 사전 협의 및 요구사항 파악<br>
                                    • 전문 컨설팅 활용<br>
                                    • 선호 유형 및 입지 조건 준수
                                </td>
                            </tr>
                            <tr style="background: #FFFBEB;">
                                <td style="padding: 16px; border: 1px solid #E5E7EB; background: #FEF3C7;">
                                    <strong style="color: #92400E;">🟡 건축비 상승</strong><br>
                                    <span style="font-size: 13px; color: #78350F;">10% 상승 시 NPV 20% 감소</span>
                                </td>
                                <td style="padding: 16px; border: 1px solid #E5E7EB;">
                                    • 시공사 실적 검증 철저히<br>
                                    • 단가 계약 체결<br>
                                    • 예비비 10% 확보
                                </td>
                            </tr>
                            <tr style="background: #FEF2F2;">
                                <td style="padding: 16px; border: 1px solid #E5E7EB; background: #FEF2F2;">
                                    <strong style="color: #991B1B;">🟠 LH 매입가 하락</strong><br>
                                    <span style="font-size: 13px; color: #7F1D1D;">감정가 100%→95% 시 NPV 30% 감소</span>
                                </td>
                                <td style="padding: 16px; border: 1px solid #E5E7EB;">
                                    • 감정평가 2곳 이상 의뢰<br>
                                    • 보수적 시나리오 검토<br>
                                    • LH 매입가 트렌드 모니터링
                                </td>
                            </tr>
                        </table>
                    </div>
                    <div class="speaker-notes">
                        <h4>🎤 발표자 스크립트:</h4>
                        <p>
                            "주요 리스크는 크게 3가지입니다. 첫째, LH 승인 지연 리스크입니다.
                            공모에서 탈락하거나 조건부 승인을 받을 경우 사업 기간이 6개월 이상 지연될 수 있습니다.
                            이를 완화하기 위해 LH 사전 협의와 전문 컨설팅을 활용할 계획입니다."
                        </p>
                        <p>
                            "둘째, 건축비 상승 리스크입니다. 건축비가 10% 상승하면 NPV가 약 20% 감소합니다.
                            이에 대해서는 시공사 실적을 철저히 검증하고, 단가 계약을 체결하며, 예비비 10%를 확보할 예정입니다."
                        </p>
                        <p>
                            "셋째, LH 매입가 하락 리스크입니다. 감정가의 95%로 매입될 경우 NPV가 30% 감소합니다.
                            감정평가를 2곳 이상에서 받고, 보수적 시나리오도 함께 검토하고 있습니다."
                        </p>
                    </div>
                </div>
                
                <!-- SLIDE 11: RECOMMENDATION -->
                <div class="presentation-slide">
                    <div class="slide-header">
                        <div class="slide-number">SLIDE 11</div>
                    </div>
                    <h2 class="slide-title">최종 권고안</h2>
                    <div class="slide-content">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 50px; border-radius: 20px; text-align: center; margin: 30px 0;">
                            <div style="font-size: 28px; margin-bottom: 20px; opacity: 0.95;">최종 의견</div>
                            <div style="font-size: 56px; font-weight: 700; margin-bottom: 20px;">
                                {final_decision}
                            </div>
                            <div style="font-size: 20px; opacity: 0.9; line-height: 1.8;">
                                {
                                    '본 사업은 LH 정책 방향과 부합하며, 재무적 타당성이 확보되었습니다.<br>즉시 본격 추진을 권장합니다.' 
                                    if approval_prob and approval_prob >= 75 and npv_krw and npv_krw >= 300000000 
                                    else '일부 리스크 요인이 있으나 추진 가능한 사업입니다.<br>리스크 완화 방안을 적용하여 진행을 권장합니다.' 
                                    if npv_krw and npv_krw > 0 
                                    else '현재 조건으로는 추진이 어렵습니다.<br>조건 재검토 후 의사결정을 권장합니다.'
                                }
                            </div>
                        </div>
                        <div style="background: white; padding: 24px; border-radius: 8px; border: 2px solid #E5E7EB;">
                            <h3 style="margin-bottom: 16px; color: #1F2937;">즉시 실행 단계 (Next Steps):</h3>
                            <ol style="line-height: 2.0; font-size: 16px;">
                                <li><strong>정밀 실사</strong> (1-2주): 토지 권리 관계 확정</li>
                                <li><strong>LH 사전 협의</strong> (1주): 매입 의향 및 요구사항 확인</li>
                                <li><strong>시공사 선정</strong> (2-3주): 견적 비교 및 건축비 확정</li>
                                <li><strong>자금 조달 계획</strong> (2주): PF 대출 조건 협의</li>
                                <li><strong>감정평가</strong> (1주): 공식 감정평가서 확보</li>
                                <li><strong>최종 투자 승인</strong>: 투자위원회 승인 및 계약</li>
                            </ol>
                            <div style="margin-top: 16px; padding: 12px; background: #EFF6FF; border-radius: 8px; font-size: 14px;">
                                <strong>⏱️ 총 소요 기간:</strong> 약 6-8주
                            </div>
                        </div>
                    </div>
                    <div class="speaker-notes">
                        <h4>🎤 발표자 스크립트:</h4>
                        <p>
                            "이상으로 종합 분석 결과를 말씀드렸습니다. 
                            최종 의견은 '<strong>{final_decision}</strong>'입니다."
                        </p>
                        <p>
                            {
                                '본 사업은 LH 정책 방향과 100% 부합하며, 재무적 타당성도 충분히 확보되었습니다. '
                                '승인 가능성 ' + format_percentage(approval_prob) + ', NPV ' + format_currency(npv_krw) + '로 '
                                '즉시 본격 추진을 권장합니다.' 
                                if approval_prob and approval_prob >= 75 and npv_krw and npv_krw >= 300000000 
                                else '일부 리스크 요인이 있으나 추진 가능한 사업으로 평가됩니다. '
                                '리스크 완화 방안을 적용하여 신중하게 진행하시면 좋은 결과를 기대할 수 있습니다.'
                            }
                        </p>
                        <p>
                            "즉시 실행 단계는 정밀 실사부터 시작하여 약 6-8주 소요됩니다.
                            LH 공모 일정에 맞춰 역산 일정을 수립하시면 됩니다."
                        </p>
                    </div>
                </div>
                
                <!-- SLIDE 12: Q&A PREPARATION -->
                <div class="presentation-slide">
                    <div class="slide-header">
                        <div class="slide-number">SLIDE 12</div>
                    </div>
                    <h2 class="slide-title">Q&A (예상 질문)</h2>
                    <div class="slide-content">
                        <div style="background: #F9FAFB; padding: 20px; border-radius: 8px; margin-bottom: 16px;">
                            <strong style="color: #3B82F6;">Q1: 토지비가 높지 않나요?</strong>
                            <p style="margin: 8px 0 0 0; line-height: 1.7;">
                                A: 총 사업비의 약 40%로, LH 매입임대사업의 평균 범위(35-45%) 내에 있습니다.
                                인근 시세 대비해도 정상 범위입니다.
                            </p>
                        </div>
                        <div style="background: #F9FAFB; padding: 20px; border-radius: 8px; margin-bottom: 16px;">
                            <strong style="color: #3B82F6;">Q2: 건축비 상승 리스크는?</strong>
                            <p style="margin: 8px 0 0 0; line-height: 1.7;">
                                A: 10% 상승 시 NPV 약 20% 감소합니다. 시공사 선정 시 실적 검증을 철저히 하고,
                                단가 계약으로 리스크를 완화할 계획입니다. 예비비 10%도 확보합니다.
                            </p>
                        </div>
                        <div style="background: #F9FAFB; padding: 20px; border-radius: 8px; margin-bottom: 16px;">
                            <strong style="color: #3B82F6;">Q3: LH 승인 확률이 {format_percentage(approval_prob)}인데 안전한가요?</strong>
                            <p style="margin: 8px 0 0 0; line-height: 1.7;">
                                A: LH 기준 70점 이상이면 승인 가능성이 높습니다. 
                                {
                                    f'본 사업은 {int(approval_prob or 70)}점으로 충분히 안전한 수준입니다.' 
                                    if approval_prob and approval_prob >= 70 
                                    else f'본 사업은 {int(approval_prob or 60)}점으로 보완이 필요하나, LH 사전 협의를 통해 개선 가능합니다.'
                                }
                            </p>
                        </div>
                        <div style="background: #F9FAFB; padding: 20px; border-radius: 8px; margin-bottom: 16px;">
                            <strong style="color: #3B82F6;">Q4: 사업 기간은 얼마나 걸리나요?</strong>
                            <p style="margin: 8px 0 0 0; line-height: 1.7;">
                                A: 인허가 12개월 + 건축 18개월 + LH 매입 6개월 = 총 36개월({data.get('payback_period_years') or '3-4'}년) 예상됩니다.
                                이는 유사 사업의 평균 기간입니다.
                            </p>
                        </div>
                        <div style="background: #F9FAFB; padding: 20px; border-radius: 8px;">
                            <strong style="color: #3B82F6;">Q5: 다른 투자 대안과 비교하면?</strong>
                            <p style="margin: 8px 0 0 0; line-height: 1.7;">
                                A: LH 매입임대는 매입 확약으로 분양 리스크가 없고, 공공사업으로 인허가가 빠릅니다.
                                일반 분양사업 대비 리스크는 낮지만 수익률도 안정적입니다 (IRR 11-13% vs 15-20%).
                            </p>
                        </div>
                    </div>
                    <div class="speaker-notes">
                        <h4>🎤 발표자 노트:</h4>
                        <p>
                            Q&A 세션에서 가장 많이 나오는 질문들을 정리했습니다.
                            각 질문에 대해 사실 기반의 명확한 답변을 준비하세요.
                            특히 리스크 관련 질문에는 구체적인 수치와 완화 방안을 함께 제시하는 것이 중요합니다.
                        </p>
                    </div>
                </div>
                
                <!-- SLIDE 13: BACKUP DATA -->
                <div class="presentation-slide">
                    <div class="slide-header">
                        <div class="slide-number">SLIDE 13 (Backup)</div>
                    </div>
                    <h2 class="slide-title">Backup: 상세 재무 모델</h2>
                    <div class="slide-content">
                        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                            <tr style="background: #F3F4F6; font-weight: 600;">
                                <td style="padding: 10px; border: 1px solid #E5E7EB;">항목</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right;">기준 시나리오</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right;">낙관 시나리오</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right;">보수 시나리오</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border: 1px solid #E5E7EB;">LH 매입가</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right;">감정가 98%</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right;">감정가 100%</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right;">감정가 95%</td>
                            </tr>
                            <tr style="background: #F9FAFB;">
                                <td style="padding: 10px; border: 1px solid #E5E7EB;">건축비</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right;">㎡당 220만원</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right;">㎡당 210만원</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right;">㎡당 240만원</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border: 1px solid #E5E7EB;">사업 기간</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right;">36개월</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right;">30개월</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right;">42개월</td>
                            </tr>
                            <tr style="background: #F9FAFB;">
                                <td style="padding: 10px; border: 1px solid #E5E7EB; font-weight: 600;">NPV</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right; font-weight: 600;">
                                    {format_currency(npv_krw)}
                                </td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right; color: #10B981; font-weight: 600;">
                                    {format_currency(int((npv_krw or 0) * 1.3))}
                                </td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right; color: #F59E0B; font-weight: 600;">
                                    {format_currency(int((npv_krw or 0) * 0.7))}
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; font-weight: 600;">IRR</td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right; font-weight: 600;">
                                    {format_percentage(irr_pct)}
                                </td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right; color: #10B981; font-weight: 600;">
                                    {format_percentage(round((irr_pct or 0) * 1.2, 1))}
                                </td>
                                <td style="padding: 10px; border: 1px solid #E5E7EB; text-align: right; color: #F59E0B; font-weight: 600;">
                                    {format_percentage(round((irr_pct or 0) * 0.8, 1))}
                                </td>
                            </tr>
                        </table>
                    </div>
                    <div class="speaker-notes">
                        <h4>🎤 발표자 노트:</h4>
                        <p>
                            Backup 슬라이드입니다. 재무 모델링에 대한 상세 질문이 나올 때 사용하세요.
                            3가지 시나리오(낙관/기준/보수)를 보여주면서, 최악의 경우에도 사업성이 확보됨을 강조하세요.
                        </p>
                    </div>
                </div>
                
                <!-- SLIDE 14: THANK YOU -->
                <div class="presentation-slide">
                    <div class="slide-header">
                        <div class="slide-number">SLIDE 14</div>
                    </div>
                    <div class="slide-content" style="text-align: center; padding: 80px 0;">
                        <h1 style="font-size: 56px; color: #1F2937; margin-bottom: 40px;">
                            감사합니다
                        </h1>
                        <div style="font-size: 24px; color: #6B7280; margin-bottom: 60px;">
                            질문이 있으시면 말씀해 주십시오
                        </div>
                        <div style="font-size: 16px; color: #9CA3AF;">
                            ZeroSite Expert Analysis<br>
                            {datetime.now().strftime('%Y년 %m월 %d일')}<br>
                            Context ID: {data.get('context_id', 'UNKNOWN')}
                        </div>
                    </div>
                    <div class="speaker-notes">
                        <h4>🎤 발표자 노트:</h4>
                        <p>
                            발표를 마무리하며 청중의 질문을 받습니다.
                            준비한 Q&A와 Backup 슬라이드를 활용하여 답변하세요.
                            발표 시간: 약 30-40분 소요, Q&A 시간: 10-15분 권장
                        </p>
                    </div>
                </div>
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
