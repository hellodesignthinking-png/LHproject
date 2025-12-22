"""
Module HTML Renderer for v4.3

Purpose: Render individual module HTML previews
Author: ZeroSite Backend Team
Date: 2025-12-22

CRITICAL: This is the DEDICATED renderer for module-level HTML previews.
Do NOT mix with final_report_html_renderer.py
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def render_module_html(module: str, adapted_data: Dict[str, Any]) -> str:
    """
    Render individual module HTML preview
    
    Args:
        module: Module identifier (M2, M3, M4, M5, M6)
        adapted_data: Output from module_html_adapter
        
    Returns:
        Complete HTML string ready for display
    """
    if module == "M3":
        return _render_m3_html(adapted_data)
    elif module == "M4":
        return _render_m4_html(adapted_data)
    elif module == "M2":
        return _render_m2_html(adapted_data)
    elif module == "M5":
        return _render_m5_html(adapted_data)
    elif module == "M6":
        return _render_m6_html(adapted_data)
    else:
        return _render_error_html(f"Unknown module: {module}")


def _render_m3_html(data: Dict[str, Any]) -> str:
    """Render M3 (주택유형) HTML"""
    
    if data.get("fallback", False):
        return _render_fallback_html("M3", "LH 선호 주택유형 분석", data)
    
    rec_type = data["recommended_type"]
    eval_summary = data["evaluation_summary"]
    score_breakdown = data["score_breakdown"]
    lh_policy = data["lh_policy_interpretation"]
    
    # Build score table rows
    score_rows = ""
    for item in score_breakdown:
        score_rows += f"""
        <tr>
            <td>{item['item']}</td>
            <td>{item['score']} / {item['max_score']}</td>
            <td>{item['commentary']}</td>
        </tr>
        """
    
    grade_class = f"grade-{rec_type['grade'].lower()}"
    policy_class = "success" if lh_policy['policy_fit'] == "적합" else "warning"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{data['title']} - ZeroSite</title>
        <style>
            {_get_common_styles()}
        </style>
    </head>
    <body>
        <div class="container">
            <header class="header">
                <h1>{data['title']}</h1>
                <p class="subtitle">Module {data['module']}</p>
            </header>
            
            <section class="module-section">
                <div class="key-result-card">
                    <div class="badge {grade_class}">{rec_type['grade']}등급</div>
                    <h2>추천 유형: {rec_type['name']} ({rec_type['score']}점)</h2>
                    <p class="confidence">분석 신뢰도: {rec_type['confidence']}</p>
                </div>
                
                <div class="narrative">
                    <h3>분석 요약</h3>
                    <p>{eval_summary['one_line']}</p>
                    <p>{eval_summary['detailed']}</p>
                </div>
                
                <div class="score-section">
                    <h3>평가 항목별 점수</h3>
                    <table class="score-table">
                        <thead>
                            <tr>
                                <th>평가 항목</th>
                                <th>점수</th>
                                <th>평가 내용</th>
                            </tr>
                        </thead>
                        <tbody>
                            {score_rows}
                        </tbody>
                    </table>
                </div>
                
                <div class="policy-box {policy_class}">
                    <strong>LH 정책 해석:</strong>
                    {lh_policy['interpretation']}
                </div>
            </section>
        </div>
    </body>
    </html>
    """
    
    return html


def _render_m4_html(data: Dict[str, Any]) -> str:
    """Render M4 (건축규모) HTML"""
    
    if data.get("fallback", False):
        return _render_fallback_html("M4", "건축 규모 및 개발 가능성 분석", data)
    
    dev_summary = data["development_summary"]
    area_analysis = data["area_analysis"]
    interpretation = data["interpretation"]
    lh_feasibility = data["lh_feasibility"]
    
    feasibility_class = "success" if lh_feasibility['status'] == "적합" else "warning"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{data['title']} - ZeroSite</title>
        <style>
            {_get_common_styles()}
        </style>
    </head>
    <body>
        <div class="container">
            <header class="header">
                <h1>{data['title']}</h1>
                <p class="subtitle">Module {data['module']}</p>
            </header>
            
            <section class="module-section">
                <div class="key-metrics-grid">
                    <div class="metric">
                        <span class="label">총 세대수</span>
                        <span class="value">{dev_summary['total_units']}세대</span>
                    </div>
                    <div class="metric">
                        <span class="label">기본 세대수</span>
                        <span class="value">{dev_summary['base_units']}세대</span>
                    </div>
                    <div class="metric highlight">
                        <span class="label">인센티브 세대</span>
                        <span class="value">{dev_summary['incentive_units']}세대</span>
                    </div>
                    <div class="metric">
                        <span class="label">건축 규모</span>
                        <span class="value">{dev_summary['floors']}</span>
                    </div>
                </div>
                
                <div class="narrative">
                    <h3>개발 규모 분석</h3>
                    <p>{interpretation['one_line']}</p>
                    <p>{interpretation['detailed']}</p>
                </div>
                
                <div class="ratio-section">
                    <h3>용적률 및 건폐율</h3>
                    <table class="ratio-table">
                        <tr>
                            <th>항목</th>
                            <th>계획</th>
                            <th>법적 기준</th>
                        </tr>
                        <tr>
                            <td>대지면적</td>
                            <td>{area_analysis['site_area']:.1f}㎡</td>
                            <td>-</td>
                        </tr>
                        <tr>
                            <td>건폐율</td>
                            <td>{area_analysis['building_coverage_ratio']:.1f}%</td>
                            <td>-</td>
                        </tr>
                        <tr>
                            <td>용적률</td>
                            <td>{area_analysis['floor_area_ratio']:.1f}%</td>
                            <td>{area_analysis['legal_far_limit']:.1f}%</td>
                        </tr>
                    </table>
                </div>
                
                <div class="policy-box {feasibility_class}">
                    <strong>LH 사업 적합성:</strong>
                    {lh_feasibility['commentary']}
                </div>
            </section>
        </div>
    </body>
    </html>
    """
    
    return html


def _render_m2_html(data: Dict[str, Any]) -> str:
    """Render M2 (토지평가) HTML - Placeholder"""
    return f"<html><body><h1>M2 Renderer (TODO)</h1><pre>{data}</pre></body></html>"


def _render_m5_html(data: Dict[str, Any]) -> str:
    """Render M5 (사업성) HTML - Placeholder"""
    return f"<html><body><h1>M5 Renderer (TODO)</h1><pre>{data}</pre></body></html>"


def _render_m6_html(data: Dict[str, Any]) -> str:
    """Render M6 (LH심사) HTML - Placeholder"""
    return f"<html><body><h1>M6 Renderer (TODO)</h1><pre>{data}</pre></body></html>"


def _render_fallback_html(module: str, title: str, data: Dict[str, Any]) -> str:
    """Render fallback HTML when data is unavailable"""
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>{title} - 데이터 없음</title>
        <style>{_get_common_styles()}</style>
    </head>
    <body>
        <div class="container">
            <header class="header error">
                <h1>{title}</h1>
                <p class="subtitle">Module {module}</p>
            </header>
            <div class="error-message">
                <h2>⚠️ 분석 데이터 부족</h2>
                <p>현재 이 모듈의 분석 결과가 없습니다.</p>
                <p>토지 분석(M1)을 완료한 후 다시 시도해 주세요.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def _render_error_html(error_message: str) -> str:
    """Render error HTML"""
    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>오류</title>
    </head>
    <body>
        <h1>오류 발생</h1>
        <p>{error_message}</p>
    </body>
    </html>
    """


def _get_common_styles() -> str:
    """Common CSS styles for module HTML"""
    return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
            color: white;
            padding: 30px 40px;
            text-align: center;
        }
        
        .header.error {
            background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 8px;
        }
        
        .subtitle {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .module-section {
            padding: 40px;
        }
        
        .key-result-card {
            background: #F0F9FF;
            border: 2px solid #3B82F6;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 12px;
        }
        
        .badge.grade-a { background: #10B981; color: white; }
        .badge.grade-b { background: #3B82F6; color: white; }
        .badge.grade-c { background: #F59E0B; color: white; }
        .badge.grade-d { background: #EF4444; color: white; }
        .badge.grade-f { background: #6B7280; color: white; }
        
        .key-result-card h2 {
            font-size: 20px;
            color: #1F2937;
            margin-bottom: 8px;
        }
        
        .confidence {
            font-size: 13px;
            color: #6B7280;
        }
        
        .narrative {
            background: #F9FAFB;
            border-left: 4px solid #3B82F6;
            padding: 20px;
            margin: 30px 0;
        }
        
        .narrative h3 {
            font-size: 16px;
            color: #1F2937;
            margin-bottom: 12px;
        }
        
        .narrative p {
            margin-bottom: 10px;
            line-height: 1.8;
        }
        
        .score-section, .ratio-section {
            margin: 30px 0;
        }
        
        .score-section h3, .ratio-section h3 {
            font-size: 16px;
            color: #1F2937;
            margin-bottom: 16px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
        }
        
        table th {
            background: #F3F4F6;
            padding: 12px;
            text-align: left;
            font-size: 13px;
            font-weight: 600;
            color: #374151;
            border-bottom: 2px solid #E5E7EB;
        }
        
        table td {
            padding: 12px;
            border-bottom: 1px solid #E5E7EB;
            font-size: 13px;
        }
        
        .policy-box {
            background: #F0FDF4;
            border: 1px solid #10B981;
            border-radius: 6px;
            padding: 16px;
            margin-top: 30px;
        }
        
        .policy-box.success {
            background: #F0FDF4;
            border-color: #10B981;
        }
        
        .policy-box.warning {
            background: #FEF3C7;
            border-color: #F59E0B;
        }
        
        .policy-box strong {
            color: #065F46;
            margin-right: 8px;
        }
        
        .key-metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 30px;
        }
        
        .metric {
            background: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 6px;
            padding: 16px;
            text-align: center;
        }
        
        .metric.highlight {
            background: #FEF3C7;
            border-color: #F59E0B;
        }
        
        .metric .label {
            display: block;
            font-size: 12px;
            color: #6B7280;
            margin-bottom: 8px;
        }
        
        .metric .value {
            display: block;
            font-size: 18px;
            font-weight: bold;
            color: #1F2937;
        }
        
        .error-message {
            padding: 60px 40px;
            text-align: center;
        }
        
        .error-message h2 {
            color: #EF4444;
            margin-bottom: 16px;
        }
        
        .error-message p {
            color: #6B7280;
            margin-bottom: 8px;
        }
    """
