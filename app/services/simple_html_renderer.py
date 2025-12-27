"""
ZeroSite 4.0 Simple HTML Renderer - Phase 3.5C Data Restoration
================================================================

Purpose: M6 중심 보고서를 실제 데이터와 함께 렌더링
Principle: 판단은 M6만, 데이터는 숨기지 않음

Version: 1.0
Date: 2025-12-27
"""

from typing import Dict, Any
from datetime import datetime

# ✅ Import unified format utilities
from app.services.format_utils import (
    format_currency_kr,
    format_percentage,
    format_area_sqm,
    format_unit_count,
    format_score
)


def get_judgement_color(judgement: str) -> str:
    """M6 판단에 따른 색상"""
    colors = {
        "GO": "#10B981",
        "CONDITIONAL": "#F59E0B",
        "NOGO": "#DC2626"
    }
    return colors.get(judgement, "#6B7280")


def render_simple_html(report_data: Dict[str, Any]) -> str:
    """
    간단한 HTML 렌더링 (Phase 3.5D FAIL FAST)
    
    Args:
        report_data: create_m6_centered_report() 결과
    
    Returns:
        HTML 문자열
    
    Raises:
        DataBindingError: 필수 데이터 누락 또는 N/A 발견 시
    """
    from app.services.data_contract import DataBindingError
    
    # 🔴 Phase 3.5D FAIL FAST: 필수 데이터 검증
    if not report_data:
        raise DataBindingError("report_data is empty. Cannot render HTML.")
    
    if 'evidence_data' not in report_data:
        raise DataBindingError("evidence_data is missing. Cannot render HTML.")
    
    # M6 결과 추출
    m6 = report_data.get('m6_scorecard', {})
    judgement = m6.get('judgement', 'N/A')
    total_score = m6.get('total_score', 0)
    grade = m6.get('grade', 'N/A')
    
    # 🔴 Phase 3.5D: N/A 체크
    if judgement == 'N/A' or grade == 'N/A':
        raise DataBindingError(f"M6 data contains N/A: judgement={judgement}, grade={grade}")
    
    # Evidence 데이터 추출
    evidence = report_data.get('evidence_data', {})
    m2 = evidence.get('m2_appraisal', {})
    m3 = evidence.get('m3_housing_type', {})
    m4 = evidence.get('m4_capacity', {})
    m5 = evidence.get('m5_feasibility', {})
    
    # 색상
    color = get_judgement_color(judgement)
    
    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZeroSite 4.0 보고서</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background: #f9fafb;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: {color};
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .header .score {{
            font-size: 48px;
            font-weight: bold;
            margin: 20px 0;
        }}
        
        .header .grade {{
            font-size: 24px;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            font-size: 24px;
            color: #111827;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e5e7eb;
        }}
        
        .data-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .data-card {{
            background: #f9fafb;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid {color};
        }}
        
        .data-card .label {{
            font-size: 14px;
            color: #6b7280;
            margin-bottom: 8px;
        }}
        
        .data-card .value {{
            font-size: 20px;
            font-weight: 600;
            color: #111827;
        }}
        
        .conclusion {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 20px;
            margin-top: 30px;
            border-radius: 8px;
        }}
        
        .conclusion strong {{
            display: block;
            margin-bottom: 10px;
            font-size: 18px;
        }}
        
        .note {{
            background: #eff6ff;
            border-left: 4px solid #3b82f6;
            padding: 15px;
            margin-top: 20px;
            border-radius: 8px;
            font-size: 14px;
            color: #1e40af;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            background: #f9fafb;
            color: #6b7280;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header: M6 판단 -->
        <div class="header">
            <h1>{report_data.get('report_name', 'ZeroSite 보고서')}</h1>
            <div class="score">{total_score:.1f}/100</div>
            <div class="grade">등급: {grade} | 판정: {judgement}</div>
        </div>
        
        <div class="content">
            <!-- Section 1: M6 결론 -->
            <div class="section">
                <h2>🎯 M6 최종 결론</h2>
                <div class="conclusion">
                    <strong>판정 결과</strong>
                    <p>{report_data.get('final_conclusion', 'N/A')}</p>
                </div>
            </div>
            
            <!-- Section 2: M2 토지 평가 -->
            <div class="section">
                <h2>📍 M2 토지 평가 (근거 데이터)</h2>
                <div class="data-grid">
                    <div class="data-card">
                        <div class="label">토지 가치</div>
                        <div class="value">{format_currency_kr(m2.get('land_value', 0))}</div>
                    </div>
                    <div class="data-card">
                        <div class="label">평당 단가</div>
                        <div class="value">{format_currency_kr(m2.get('land_value_per_pyeong', 0))}</div>
                    </div>
                    <div class="data-card">
                        <div class="label">신뢰도</div>
                        <div class="value">{format_percentage(m2.get('confidence_pct', 0))}</div>
                    </div>
                </div>
                <div class="note">
                    ℹ️ 위 데이터는 M6 판단의 근거로 사용되었습니다. 판단은 M6만 수행합니다.
                </div>
            </div>
            
            <!-- Section 3: M3 주택 유형 -->
            <div class="section">
                <h2>🏠 M3 주택 유형 분석 (근거 데이터)</h2>
                <div class="data-grid">
                    <div class="data-card">
                        <div class="label">분석 유형</div>
                        <div class="value">{m3.get('recommended_type', '데이터 없음')}</div>
                    </div>
                    <div class="data-card">
                        <div class="label">분석 점수</div>
                        <div class="value">{m3.get('total_score', 0):.1f}점</div>
                    </div>
                    <div class="data-card">
                        <div class="label">수요 지수</div>
                        <div class="value">{m3.get('demand_score', 0):.1f}점</div>
                    </div>
                </div>
                <div class="note">
                    ℹ️ 위 데이터는 M6 판단의 근거로 사용되었습니다. 판단은 M6만 수행합니다.
                </div>
            </div>
            
            <!-- Section 4: M4 용적률 분석 -->
            <div class="section">
                <h2>🏗️ M4 용적률 분석 (근거 데이터)</h2>
                <div class="data-grid">
                    <div class="data-card">
                        <div class="label">세대수</div>
                        <div class="value">{m4.get('total_units', 0)}세대</div>
                    </div>
                    <div class="data-card">
                        <div class="label">연면적</div>
                        <div class="value">{format_area_sqm(m4.get('gross_area_sqm', 0))}</div>
                    </div>
                    <div class="data-card">
                        <div class="label">주차면수</div>
                        <div class="value">{m4.get('parking_spaces', 0)}면</div>
                    </div>
                </div>
                <div class="note">
                    ℹ️ 위 데이터는 M6 판단의 근거로 사용되었습니다. 판단은 M6만 수행합니다.
                </div>
            </div>
            
            <!-- Section 5: M5 사업성 분석 -->
            <div class="section">
                <h2>💰 M5 사업성 분석 (근거 데이터)</h2>
                <div class="data-grid">
                    <div class="data-card">
                        <div class="label">NPV (순현재가치)</div>
                        <div class="value">{format_currency_kr(m5.get('npv_public_krw', 0))}</div>
                    </div>
                    <div class="data-card">
                        <div class="label">IRR (내부수익률)</div>
                        <div class="value">{format_percentage(m5.get('irr_pct', 0))}</div>
                    </div>
                    <div class="data-card">
                        <div class="label">ROI (투자수익률)</div>
                        <div class="value">{format_percentage(m5.get('roi_pct', 0))}</div>
                    </div>
                </div>
                <div class="note">
                    ℹ️ 위 수치는 M6 판단의 근거로 사용되었습니다. 수치 자체는 판단이 아닙니다.
                </div>
            </div>
            
            <!-- Section 6: 개선 포인트 -->
            <div class="section">
                <h2>📈 개선 포인트</h2>
                <ul style="list-style: none; padding-left: 0;">
    """
    
    for point in m6.get('improvement_points', []):
        html += f"                    <li style='padding: 10px; background: #f0fdf4; margin-bottom: 10px; border-left: 4px solid #10b981; border-radius: 4px;'>✓ {point}</li>\n"
    
    html += f"""
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>ZeroSite v4.0 | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p style="margin-top: 10px;">M6 Single Source of Truth — 판단은 M6만, 데이터는 숨기지 않음</p>
        </div>
    </div>
</body>
</html>
"""
    
    # 🔴 Phase 3.5D FAIL FAST: 출력물 N/A 검사
    from app.services.data_contract import check_for_na_in_output
    
    try:
        check_for_na_in_output(html)
    except Exception as e:
        # N/A 발견 시 즉시 실패
        raise DataBindingError(f"HTML output contains N/A: {str(e)}")
    
    return html


if __name__ == '__main__':
    # 테스트
    test_data = {
        'report_name': 'ZeroSite 종합 보고서',
        'report_type': 'all_in_one',
        'm6_scorecard': {
            'total_score': 75.0,
            'grade': 'B',
            'judgement': 'CONDITIONAL',
            'improvement_points': [
                '+6점: 주차 확보',
                '+4점: 차별화 전략'
            ]
        },
        'evidence_data': {
            'm2_appraisal': {
                'land_value': 6081933538,
                'land_value_per_pyeong': 50000000,
                'confidence_pct': 85.0
            },
            'm3_housing_type': {
                'recommended_type': 'youth',
                'total_score': 85.5,
                'demand_score': 90.0
            },
            'm4_capacity': {
                'legal_units': 20,
                'incentive_units': 26
            },
            'm5_feasibility': {
                'npv_public_krw': 792999999,
                'irr_pct': 12.5,
                'roi_pct': 15.2
            }
        },
        'final_conclusion': '본 사업지는 ZeroSite v4.0 M6 기준에 따라 보완 조건 충족 시 LH 매입이 가능한 사업지로 판단된다.'
    }
    
    html = render_simple_html(test_data)
    
    with open('/tmp/test_report.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✅ Test HTML generated: /tmp/test_report.html")
