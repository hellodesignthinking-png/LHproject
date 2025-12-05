"""
ZeroSite v9.1 Ultra-Pro Report Generator
전문가급 LH 신축매입임대 타당성 분석 보고서 생성
v7.5 구조 기반: 5개 파트, 12개 섹션
"""

from datetime import datetime
from typing import Dict, Any


def generate_professional_report(
    address: str,
    auto_calculated: Dict[str, Any],
    analysis_result: Dict[str, Any]
) -> str:
    """
    ZeroSite v9.1 Ultra-Pro 전문 보고서 생성
    
    구조:
    - Part 1: Executive Summary (2 sections)
    - Part 2: Site Analysis (2 sections)
    - Part 3: Development Plan (2 sections)
    - Part 4: Financial Analysis (3 sections)
    - Part 5: Risk & Recommendation (2 sections)
    - Appendix: Methodology (1 section)
    """
    
    # 데이터 추출
    lh_scores = analysis_result.get('lh_scores', {})
    risk = analysis_result.get('risk_assessment', {})
    recommendation = analysis_result.get('final_recommendation', {})
    financial = analysis_result.get('financial_result', {})
    
    # Helper functions
    def safe_format_number(value, default='N/A', decimal=0):
        if value is None or value == 'N/A':
            return default
        try:
            if decimal > 0:
                return f"{float(value):,.{decimal}f}"
            return f"{float(value):,.0f}"
        except (ValueError, TypeError):
            return default
    
    def safe_value(value, default='N/A'):
        return value if value is not None and value != '' else default
    
    def get_decision_badge(decision):
        decision_str = str(decision).upper()
        if 'PROCEED' in decision_str or '진행' in decision_str:
            return 'PROCEED', 'success'
        elif 'REVIEW' in decision_str or '재검토' in decision_str:
            return 'REVIEW', 'warning'
        else:
            return 'REJECT', 'danger'
    
    def get_risk_badge(risk_level):
        risk_str = str(risk_level).upper()
        if 'LOW' in risk_str or '낮음' in risk_str:
            return 'LOW RISK', 'success'
        elif 'MEDIUM' in risk_str or '중간' in risk_str:
            return 'MEDIUM RISK', 'warning'
        else:
            return 'HIGH RISK', 'danger'
    
    # 데이터 준비
    generation_date = datetime.now().strftime('%Y년 %m월 %d일')
    decision_text, decision_class = get_decision_badge(recommendation.get('decision', 'REVIEW'))
    risk_text, risk_class = get_risk_badge(risk.get('overall_risk', 'MEDIUM'))
    
    lh_score = safe_value(lh_scores.get('total_score', 0))
    lh_grade = safe_value(lh_scores.get('grade', 'B'))
    
    latitude = safe_format_number(auto_calculated.get('latitude'), 'N/A', 6)
    longitude = safe_format_number(auto_calculated.get('longitude'), 'N/A', 6)
    land_area = safe_format_number(auto_calculated.get('land_area'), 'N/A', 0)
    zone_type = safe_value(auto_calculated.get('zone_type'))
    bcr = safe_format_number(auto_calculated.get('building_coverage_ratio'), 'N/A', 1)
    far = safe_format_number(auto_calculated.get('floor_area_ratio'), 'N/A', 1)
    max_height = safe_value(auto_calculated.get('max_height'), '제한 없음')
    unit_count = safe_format_number(auto_calculated.get('unit_count'), 'N/A', 0)
    floors = safe_format_number(auto_calculated.get('floors'), 'N/A', 0)
    parking = safe_format_number(auto_calculated.get('parking_spaces'), 'N/A', 0)
    total_gfa = safe_format_number(auto_calculated.get('total_gfa'), 'N/A', 0)
    residential_gfa = safe_format_number(auto_calculated.get('residential_gfa'), 'N/A', 0)
    
    land_cost = safe_format_number(auto_calculated.get('total_land_cost', 0) / 100000000, 'N/A', 1)
    construction_cost = safe_format_number(auto_calculated.get('total_construction_cost', 0) / 100000000, 'N/A', 1)
    total_capex = safe_format_number((auto_calculated.get('total_land_cost', 0) + auto_calculated.get('total_construction_cost', 0)) / 100000000, 'N/A', 1)
    
    irr_10y = safe_format_number(financial.get('irr_10_year', 0), 'N/A', 2)
    roi_10y = safe_format_number(financial.get('roi_10_year', 0), 'N/A', 2)
    
    confidence = safe_format_number(recommendation.get('confidence', 0), 'N/A', 1)
    
    # HTML 생성
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZeroSite v9.1 Ultra-Pro - LH 신축매입임대 사업 타당성 전략 분석 보고서</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Noto Sans KR', 'Malgun Gothic', Arial, sans-serif;
            line-height: 1.8;
            color: #2c3e50;
            background: #ffffff;
            font-size: 11pt;
        }}
        
        /* Cover Page */
        .cover-page {{
            page-break-after: always;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 95vh;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%);
            color: white;
            text-align: center;
            padding: 60px 40px;
        }}
        
        .cover-page h1 {{
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 30px;
            letter-spacing: -1px;
        }}
        
        .cover-page h2 {{
            font-size: 36px;
            font-weight: 600;
            margin: 20px 0;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
        }}
        
        .cover-page .subtitle {{
            font-size: 24px;
            margin: 30px 0;
            opacity: 0.95;
        }}
        
        .cover-page .decision {{
            font-size: 48px;
            font-weight: 800;
            margin: 40px 0;
            padding: 30px 60px;
            background: rgba(255, 255, 255, 0.2);
            border: 3px solid white;
            border-radius: 12px;
            letter-spacing: 2px;
        }}
        
        .cover-page .metadata {{
            margin-top: 50px;
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .cover-page .footer-note {{
            margin-top: 60px;
            font-size: 12px;
            opacity: 0.8;
        }}
        
        /* Part Divider */
        .part-divider {{
            page-break-before: always;
            page-break-after: always;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 80vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 80px 40px;
        }}
        
        .part-divider h1 {{
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 20px;
        }}
        
        .part-divider h2 {{
            font-size: 32px;
            font-weight: 400;
            opacity: 0.9;
        }}
        
        /* Content Sections */
        .content-section {{
            page-break-before: auto;
            padding: 30px 40px;
            margin-bottom: 40px;
        }}
        
        .section-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        
        .section-header h2 {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .section-header .subtitle {{
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .subsection {{
            margin: 25px 0;
        }}
        
        .subsection h3 {{
            font-size: 18px;
            color: #2c3e50;
            margin-bottom: 15px;
            padding-left: 15px;
            border-left: 4px solid #667eea;
        }}
        
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 20px 0;
        }}
        
        .metric-card {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
        }}
        
        .metric-card .label {{
            font-size: 12px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .metric-card .value {{
            font-size: 24px;
            font-weight: 700;
            color: #2c3e50;
        }}
        
        .metric-card .unit {{
            font-size: 14px;
            color: #6c757d;
            margin-left: 5px;
        }}
        
        .info-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        .info-table th,
        .info-table td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .info-table th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
            width: 35%;
        }}
        
        .info-table td {{
            color: #212529;
        }}
        
        .info-table tr:last-child th,
        .info-table tr:last-child td {{
            border-bottom: none;
        }}
        
        /* Score Box */
        .score-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            margin: 30px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .score-box .title {{
            font-size: 16px;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        
        .score-box .score {{
            font-size: 64px;
            font-weight: 800;
            margin: 20px 0;
        }}
        
        .score-box .grade {{
            font-size: 28px;
            font-weight: 600;
            opacity: 0.95;
        }}
        
        /* Badge */
        .badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .badge-success {{
            background: #10b981;
            color: white;
        }}
        
        .badge-warning {{
            background: #f59e0b;
            color: white;
        }}
        
        .badge-danger {{
            background: #ef4444;
            color: white;
        }}
        
        /* Highlight Box */
        .highlight-box {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        .highlight-box.success {{
            background: #d1e7dd;
            border-left-color: #198754;
        }}
        
        .highlight-box.danger {{
            background: #f8d7da;
            border-left-color: #dc3545;
        }}
        
        .highlight-box.info {{
            background: #cfe2ff;
            border-left-color: #0d6efd;
        }}
        
        /* Footer */
        .report-footer {{
            margin-top: 60px;
            padding-top: 30px;
            border-top: 2px solid #dee2e6;
            text-align: center;
            color: #6c757d;
            font-size: 11px;
        }}
        
        /* Print Optimization */
        @media print {{
            body {{ background: white; }}
            .content-section {{ page-break-inside: avoid; }}
            .metric-grid {{ page-break-inside: avoid; }}
            .score-box {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <!-- Cover Page -->
    <div class="cover-page">
        <h1>ZeroSite v9.1 Ultra-Pro</h1>
        <h2>LH 신축매입임대 사업<br/>타당성 전략 분석 보고서</h2>
        <h2 style="font-size: 32px; margin-top: 40px;">{address}</h2>
        <div class="subtitle">최종 권고안</div>
        <div class="decision">{decision_text}</div>
        <div class="metadata">
            <p style="font-size: 16px;">{generation_date}</p>
            <p style="margin-top: 10px;">Classification: Internal Use / LH Submission</p>
        </div>
        <div class="footer-note">
            본 보고서는 ZeroSite v9.1 Ultra-Pro 엔진을 사용하여 생성되었습니다.
        </div>
    </div>

    <!-- Part 1: Executive Summary -->
    <div class="part-divider">
        <div>
            <h1>Part 1</h1>
            <h2>Executive Summary</h2>
        </div>
    </div>

    <div class="content-section">
        <div class="section-header">
            <h2>1. 사업 개요 및 핵심 결과</h2>
            <div class="subtitle">Project Overview & Key Results</div>
        </div>
        
        <div class="subsection">
            <h3>1.1 대상지 기본정보</h3>
            <table class="info-table">
                <tr>
                    <th>프로젝트 주소</th>
                    <td>{address}</td>
                </tr>
                <tr>
                    <th>위치 좌표</th>
                    <td>위도 {latitude}, 경도 {longitude}</td>
                </tr>
                <tr>
                    <th>대지면적</th>
                    <td>{land_area} m²</td>
                </tr>
                <tr>
                    <th>용도지역</th>
                    <td>{zone_type}</td>
                </tr>
                <tr>
                    <th>건폐율 / 용적률</th>
                    <td>{bcr}% / {far}%</td>
                </tr>
            </table>
        </div>
        
        <div class="subsection">
            <h3>1.2 핵심 분석 결과</h3>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="label">LH 평가 점수</div>
                    <div class="value">{lh_score}<span class="unit">점</span></div>
                </div>
                <div class="metric-card">
                    <div class="label">평가 등급</div>
                    <div class="value">{lh_grade}<span class="unit">등급</span></div>
                </div>
                <div class="metric-card">
                    <div class="label">예상 세대수</div>
                    <div class="value">{unit_count}<span class="unit">세대</span></div>
                </div>
                <div class="metric-card">
                    <div class="label">총 투자비 (CAPEX)</div>
                    <div class="value">{total_capex}<span class="unit">억원</span></div>
                </div>
                <div class="metric-card">
                    <div class="label">10년 IRR</div>
                    <div class="value">{irr_10y}<span class="unit">%</span></div>
                </div>
                <div class="metric-card">
                    <div class="label">10년 ROI</div>
                    <div class="value">{roi_10y}<span class="unit">%</span></div>
                </div>
            </div>
        </div>
    </div>

    <div class="content-section">
        <div class="section-header">
            <h2>2. 최종 권고안 및 실행 전제조건</h2>
            <div class="subtitle">Final Recommendation & Prerequisites</div>
        </div>
        
        <div class="subsection">
            <h3>2.1 투자 결정</h3>
            <div class="score-box">
                <div class="title">최종 권고안</div>
                <div class="score">{decision_text}</div>
                <div class="grade">신뢰도: {confidence}%</div>
            </div>
        </div>
        
        <div class="subsection">
            <h3>2.2 리스크 평가</h3>
            <div class="highlight-box {risk_class}">
                <strong>전체 리스크 수준:</strong> <span class="badge badge-{risk_class}">{risk_text}</span>
                <p style="margin-top: 15px;">본 프로젝트는 {risk_text.split()[0].lower()} 수준의 리스크를 내포하고 있습니다.</p>
            </div>
        </div>
    </div>

    <!-- Part 2: Site Analysis -->
    <div class="part-divider">
        <div>
            <h1>Part 2</h1>
            <h2>Site Analysis</h2>
        </div>
    </div>

    <div class="content-section">
        <div class="section-header">
            <h2>3. 토지 개요 및 입지 분석</h2>
            <div class="subtitle">Land Overview & Location Analysis</div>
        </div>
        
        <div class="subsection">
            <h3>3.1 토지 기본정보</h3>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="label">대지면적</div>
                    <div class="value">{land_area}<span class="unit">m²</span></div>
                </div>
                <div class="metric-card">
                    <div class="label">용도지역</div>
                    <div class="value" style="font-size: 16px;">{zone_type}</div>
                </div>
                <div class="metric-card">
                    <div class="label">위도 (Latitude)</div>
                    <div class="value" style="font-size: 18px;">{latitude}</div>
                </div>
                <div class="metric-card">
                    <div class="label">경도 (Longitude)</div>
                    <div class="value" style="font-size: 18px;">{longitude}</div>
                </div>
            </div>
        </div>
    </div>

    <div class="content-section">
        <div class="section-header">
            <h2>4. 법적·규제 환경 분석</h2>
            <div class="subtitle">Legal & Regulatory Environment</div>
        </div>
        
        <div class="subsection">
            <h3>4.1 건축 규제</h3>
            <table class="info-table">
                <tr>
                    <th>건폐율</th>
                    <td>{bcr}%</td>
                </tr>
                <tr>
                    <th>용적률</th>
                    <td>{far}%</td>
                </tr>
                <tr>
                    <th>높이제한</th>
                    <td>{max_height}</td>
                </tr>
            </table>
        </div>
    </div>

    <!-- Part 3: Development Plan -->
    <div class="part-divider">
        <div>
            <h1>Part 3</h1>
            <h2>Development Plan</h2>
        </div>
    </div>

    <div class="content-section">
        <div class="section-header">
            <h2>5. 건축 계획 및 개발 규모</h2>
            <div class="subtitle">Building Plan & Development Scale</div>
        </div>
        
        <div class="subsection">
            <h3>5.1 개발 규모</h3>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="label">총 연면적</div>
                    <div class="value">{total_gfa}<span class="unit">m²</span></div>
                </div>
                <div class="metric-card">
                    <div class="label">주거 연면적</div>
                    <div class="value">{residential_gfa}<span class="unit">m²</span></div>
                </div>
                <div class="metric-card">
                    <div class="label">예상 층수</div>
                    <div class="value">{floors}<span class="unit">층</span></div>
                </div>
                <div class="metric-card">
                    <div class="label">주차 대수</div>
                    <div class="value">{parking}<span class="unit">대</span></div>
                </div>
            </div>
        </div>
    </div>

    <div class="content-section">
        <div class="section-header">
            <h2>6. 세대 구성 및 공간 계획</h2>
            <div class="subtitle">Unit Composition & Space Planning</div>
        </div>
        
        <div class="subsection">
            <h3>6.1 세대 계획</h3>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="label">총 세대수</div>
                    <div class="value">{unit_count}<span class="unit">세대</span></div>
                </div>
                <div class="metric-card">
                    <div class="label">층당 세대수</div>
                    <div class="value">{safe_format_number(float(unit_count.replace(',', '')) / float(floors.replace(',', '')) if unit_count != 'N/A' and floors != 'N/A' else 0, 'N/A', 1)}<span class="unit">세대/층</span></div>
                </div>
            </div>
        </div>
    </div>

    <!-- Part 4: Financial Analysis -->
    <div class="part-divider">
        <div>
            <h1>Part 4</h1>
            <h2>Financial Analysis</h2>
        </div>
    </div>

    <div class="content-section">
        <div class="section-header">
            <h2>7. 사업비 추정 및 투자 구조</h2>
            <div class="subtitle">Project Cost Estimation & Investment Structure</div>
        </div>
        
        <div class="subsection">
            <h3>7.1 투자비 구성</h3>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="label">토지비</div>
                    <div class="value">{land_cost}<span class="unit">억원</span></div>
                </div>
                <div class="metric-card">
                    <div class="label">건축비</div>
                    <div class="value">{construction_cost}<span class="unit">억원</span></div>
                </div>
                <div class="metric-card" style="grid-column: span 2;">
                    <div class="label">총 투자비 (CAPEX)</div>
                    <div class="value" style="font-size: 32px;">{total_capex}<span class="unit">억원</span></div>
                </div>
            </div>
        </div>
    </div>

    <div class="content-section">
        <div class="section-header">
            <h2>8. 수익성 분석 (IRR, ROI)</h2>
            <div class="subtitle">Profitability Analysis</div>
        </div>
        
        <div class="subsection">
            <h3>8.1 투자 수익률</h3>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="label">10년 IRR</div>
                    <div class="value">{irr_10y}<span class="unit">%</span></div>
                </div>
                <div class="metric-card">
                    <div class="label">10년 ROI</div>
                    <div class="value">{roi_10y}<span class="unit">%</span></div>
                </div>
            </div>
        </div>
    </div>

    <div class="content-section">
        <div class="section-header">
            <h2>9. LH 평가 및 등급</h2>
            <div class="subtitle">LH Evaluation & Rating</div>
        </div>
        
        <div class="subsection">
            <h3>9.1 LH 평가 결과</h3>
            <div class="score-box">
                <div class="title">LH 종합 평가</div>
                <div class="score">{lh_score}</div>
                <div class="grade">등급: {lh_grade}</div>
            </div>
        </div>
    </div>

    <!-- Part 5: Risk & Recommendation -->
    <div class="part-divider">
        <div>
            <h1>Part 5</h1>
            <h2>Risk & Recommendation</h2>
        </div>
    </div>

    <div class="content-section">
        <div class="section-header">
            <h2>10. 리스크 관리 및 대응 전략</h2>
            <div class="subtitle">Risk Management & Mitigation Strategy</div>
        </div>
        
        <div class="subsection">
            <h3>10.1 리스크 평가</h3>
            <div class="highlight-box {risk_class}">
                <strong>전체 리스크 수준:</strong> <span class="badge badge-{risk_class}">{risk_text}</span>
                <p style="margin-top: 15px; line-height: 1.8;">
                    종합 리스크 분석 결과, 본 프로젝트는 <strong>{risk_text.split()[0]}</strong> 수준의 리스크를 나타냅니다.
                    주요 리스크 요인을 면밀히 검토하고 적절한 대응 전략을 수립해야 합니다.
                </p>
            </div>
        </div>
    </div>

    <div class="content-section">
        <div class="section-header">
            <h2>11. 종합판단 및 최종 권고안</h2>
            <div class="subtitle">Comprehensive Judgment & Final Recommendation</div>
        </div>
        
        <div class="subsection">
            <h3>11.1 최종 투자 결정</h3>
            <div class="score-box">
                <div class="title">최종 권고안</div>
                <div class="score">{decision_text}</div>
                <div class="grade">분석 신뢰도: {confidence}%</div>
            </div>
            
            <div class="highlight-box success" style="margin-top: 30px;">
                <h4 style="margin-bottom: 15px;">✅ 종합 판단</h4>
                <p style="line-height: 1.8;">
                    LH 평가 점수 <strong>{lh_score}점</strong> ({lh_grade}등급), IRR <strong>{irr_10y}%</strong>, 
                    리스크 수준 <strong>{risk_text.split()[0]}</strong>을 종합적으로 고려한 결과, 
                    본 프로젝트에 대한 최종 권고안은 <strong>{decision_text}</strong>입니다.
                </p>
                <p style="line-height: 1.8; margin-top: 15px;">
                    본 분석은 <strong>{confidence}%</strong>의 신뢰도를 가지며, 
                    LH 신축매입임대 사업의 전략적 목적에 부합하는 프로젝트로 평가됩니다.
                </p>
            </div>
        </div>
    </div>

    <!-- Appendix -->
    <div class="part-divider">
        <div>
            <h1>Appendix</h1>
            <h2>분석 방법론</h2>
        </div>
    </div>

    <div class="content-section">
        <div class="section-header">
            <h2>12. 데이터 출처 및 분석 방법론</h2>
            <div class="subtitle">Data Sources & Analysis Methodology</div>
        </div>
        
        <div class="subsection">
            <h3>12.1 데이터 출처</h3>
            <table class="info-table">
                <tr>
                    <th>좌표 변환</th>
                    <td>Kakao Local API (주소 → 위도/경도)</td>
                </tr>
                <tr>
                    <th>용도지역 매핑</th>
                    <td>국토교통부 토지이용규제 정보서비스</td>
                </tr>
                <tr>
                    <th>건축 규제</th>
                    <td>건축법 시행령, 국토의 계획 및 이용에 관한 법률</td>
                </tr>
                <tr>
                    <th>세대수 추정</th>
                    <td>LH 공사 기준 (전용면적 59㎡ 기준)</td>
                </tr>
                <tr>
                    <th>재무 분석</th>
                    <td>LH 신축매입임대 사업 표준 분석 모델</td>
                </tr>
            </table>
        </div>
        
        <div class="subsection">
            <h3>12.2 분석 엔진</h3>
            <p style="line-height: 1.8; color: #495057;">
                본 보고서는 <strong>ZeroSite v9.1 Ultra-Pro</strong> 엔진을 사용하여 생성되었습니다.
                이 엔진은 4개의 기본 입력값(주소, 대지면적, 토지 감정가, 용도지역)을 기반으로
                14개의 핵심 지표를 자동으로 계산하고, LH 평가 기준에 따라 종합 분석을 수행합니다.
            </p>
        </div>
        
        <div class="subsection">
            <h3>12.3 분석 제약사항</h3>
            <div class="highlight-box info">
                <p style="line-height: 1.8;">
                    ⚠️ <strong>주의사항:</strong> 본 보고서는 자동 생성된 분석 결과이며, 
                    실제 투자 결정 전 반드시 전문가 검토, 현장 실사, 법률 자문 등의 
                    추가 검증 절차가 필요합니다. 시장 상황, 정책 변화 등에 따라 
                    분석 결과가 달라질 수 있습니다.
                </p>
            </div>
        </div>
    </div>

    <!-- Report Footer -->
    <div class="report-footer">
        <p><strong>ZeroSite v9.1 Ultra-Pro</strong> - LH 신축매입임대 사업 타당성 전략 분석 시스템</p>
        <p>생성일시: {generation_date} | Classification: Internal Use / LH Submission</p>
        <p style="margin-top: 10px;">본 보고서의 모든 내용은 기밀로 취급되며, 무단 복제 및 배포를 금지합니다.</p>
    </div>
</body>
</html>"""
    
    return html
