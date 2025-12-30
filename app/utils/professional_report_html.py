"""
Professional HTML Report Generator for M2-M6 Modules
Generates detailed appraisal-style reports matching uploaded PDF format
"""

from datetime import datetime
from typing import Dict, Any, Optional


def format_currency(value: Optional[float]) -> str:
    """Format currency with KRW symbol and commas"""
    if value is None:
        return "N/A"
    try:
        return f"₩{int(value):,}"
    except:
        return "N/A"


def format_percentage(value: Optional[float]) -> str:
    """Format percentage with % sign"""
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.1f}%"
    except:
        return "N/A"


def generate_module_report_html(
    module_id: str,
    context_id: str,
    module_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate professional HTML report for a module
    
    Args:
        module_id: Module ID (M2-M6)
        context_id: Context ID
        module_data: Module analysis data
        
    Returns:
        Professional HTML report string
    """
    
    # Module configurations
    module_config = {
        "M2": {
            "title": "토지감정평가 보고서",
            "subtitle": "Land Appraisal Report",
            "description": "공시지가 기반 가치 평가",
            "icon": "💰"
        },
        "M3": {
            "title": "공급 유형 판단 보고서",
            "subtitle": "Housing Type Analysis Report",
            "description": "LH 공급 유형 결정 분석",
            "icon": "🏘️"
        },
        "M4": {
            "title": "건축 규모 판단 보고서",
            "subtitle": "Capacity Analysis Report",
            "description": "용적률/건폐율 기반 규모 산정",
            "icon": "🏗️"
        },
        "M5": {
            "title": "사업성 분석 보고서",
            "subtitle": "Feasibility Analysis Report",
            "description": "재무 지표 및 수익성 분석",
            "icon": "📊"
        },
        "M6": {
            "title": "LH 종합 판단 보고서",
            "subtitle": "LH Review Report",
            "description": "LH 사업성 종합 검토",
            "icon": "✅"
        }
    }
    
    config = module_config.get(module_id, {})
    report_date = datetime.now().strftime("%Y년 %m월 %d일")
    report_number = f"ZS-{module_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Extract data
    summary = module_data.get("summary", {}) if module_data else {}
    details = module_data.get("details", {}) if module_data else {}
    
    # Generate module-specific content sections
    content_sections = _generate_content_sections(module_id, summary, details)
    
    # Build professional HTML
    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{module_id}: {config['title']} - REAL APPRAISAL STANDARD</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Noto Sans KR', sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .no-print {{
                display: none !important;
            }}
            .page-break {{
                page-break-after: always;
            }}
        }}
        
        /* Cover Page */
        .cover-page {{
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 60px 20px;
        }}
        
        .logo {{
            font-size: 48px;
            font-weight: 700;
            letter-spacing: 8px;
            margin-bottom: 20px;
        }}
        
        .cover-title {{
            font-size: 42px;
            font-weight: 700;
            margin: 30px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .cover-subtitle {{
            font-size: 24px;
            font-weight: 300;
            opacity: 0.9;
            margin-bottom: 40px;
        }}
        
        .report-info {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 30px 40px;
            border-radius: 12px;
            margin: 40px 0;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .report-info-item {{
            margin: 12px 0;
            font-size: 18px;
        }}
        
        .report-info-label {{
            display: inline-block;
            width: 160px;
            font-weight: 600;
        }}
        
        .company-info {{
            margin-top: 60px;
            font-size: 16px;
            opacity: 0.8;
        }}
        
        /* Content Pages */
        .content-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            min-height: 100vh;
        }}
        
        .content-page {{
            padding: 60px 80px;
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section-title {{
            font-size: 28px;
            font-weight: 700;
            color: #2c3e50;
            border-left: 6px solid #667eea;
            padding-left: 20px;
            margin-bottom: 25px;
        }}
        
        .section-subtitle {{
            font-size: 20px;
            font-weight: 600;
            color: #34495e;
            margin: 25px 0 15px 0;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .info-card {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
        }}
        
        .info-card-title {{
            font-size: 14px;
            color: #6c757d;
            margin-bottom: 8px;
        }}
        
        .info-card-value {{
            font-size: 24px;
            font-weight: 700;
            color: #2c3e50;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .data-table th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        .data-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .data-table tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        .highlight-box {{
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            border-left: 4px solid #667eea;
            padding: 20px 25px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        
        .highlight-box h3 {{
            color: #667eea;
            margin-bottom: 12px;
            font-size: 20px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 600;
            margin: 5px 5px 5px 0;
        }}
        
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .badge-info {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .footer {{
            text-align: center;
            padding: 40px 20px;
            background: #2c3e50;
            color: white;
            margin-top: 60px;
        }}
        
        .footer-content {{
            max-width: 800px;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <!-- Cover Page -->
    <div class="cover-page page-break">
        <div class="logo">ANTENNA HOLDINGS</div>
        <div class="cover-title">{config['icon']} {config['title']}</div>
        <div class="cover-subtitle">{config['subtitle']}</div>
        <div class="cover-subtitle">{config['description']}</div>
        
        <div class="report-info">
            <div class="report-info-item">
                <span class="report-info-label">보고서 번호:</span>
                <span>{report_number}</span>
            </div>
            <div class="report-info-item">
                <span class="report-info-label">Context ID:</span>
                <span>{context_id[:24]}...</span>
            </div>
            <div class="report-info-item">
                <span class="report-info-label">분석 기준일:</span>
                <span>{report_date}</span>
            </div>
        </div>
        
        <div class="company-info">
            <strong>Antenna Holdings Co., Ltd.</strong><br>
            서울시 강남구 테헤란로 427 위워크타워<br>
            Tel: 02-3789-2000 | Email: analysis@antennaholdings.com
        </div>
    </div>
    
    <!-- Content Pages -->
    <div class="content-container">
        <div class="content-page">
            {content_sections}
        </div>
    </div>
    
    <!-- Footer -->
    <div class="footer">
        <div class="footer-content">
            <p><strong>ANTENNA HOLDINGS CO., LTD.</strong></p>
            <p>Professional Real Estate Analysis & Consulting</p>
            <p style="margin-top: 15px; font-size: 14px; opacity: 0.8;">
                본 보고서는 ZeroSite v4.0 AI 분석 시스템을 활용하여 작성되었습니다.<br>
                © {datetime.now().year} Antenna Holdings. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def _generate_content_sections(module_id: str, summary: Dict, details: Dict) -> str:
    """Generate module-specific content sections"""
    
    if module_id == "M2":
        return _generate_m2_content(summary, details)
    elif module_id == "M3":
        return _generate_m3_content(summary, details)
    elif module_id == "M4":
        return _generate_m4_content(summary, details)
    elif module_id == "M5":
        return _generate_m5_content(summary, details)
    elif module_id == "M6":
        return _generate_m6_content(summary, details)
    else:
        return "<p>보고서 데이터를 불러올 수 없습니다.</p>"


def _generate_m2_content(summary: Dict, details: Dict) -> str:
    """Generate M2 (Appraisal) report content"""
    
    land_value = summary.get("land_value_total_krw")
    pyeong_price = summary.get("pyeong_price_krw")
    confidence = summary.get("confidence_pct")
    transaction_count = summary.get("transaction_count", 0)
    
    appraisal_details = details.get("appraisal", {})
    transactions = details.get("transactions", {})
    confidence_factors = details.get("confidence", {})
    
    content = f"""
    <div class="section">
        <h2 class="section-title">📋 감정평가 요약</h2>
        <div class="highlight-box">
            <h3>총 감정가액</h3>
            <div style="font-size: 36px; font-weight: 700; color: #667eea; margin: 10px 0;">
                {format_currency(land_value)}
            </div>
            <p style="color: #666; margin-top: 10px;">
                평당 {format_currency(pyeong_price)} | 신뢰도 {format_percentage(confidence)}
            </p>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <div class="info-card-title">감정평가액</div>
                <div class="info-card-value">{format_currency(land_value)}</div>
            </div>
            <div class="info-card">
                <div class="info-card-title">평당 가격</div>
                <div class="info-card-value">{format_currency(pyeong_price)}</div>
            </div>
            <div class="info-card">
                <div class="info-card-title">신뢰도</div>
                <div class="info-card-value">{format_percentage(confidence)}</div>
            </div>
            <div class="info-card">
                <div class="info-card-title">거래사례</div>
                <div class="info-card-value">{transaction_count}건</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">📊 감정평가 근거</h2>
        <h3 class="section-subtitle">평가 방법</h3>
        <p>본 토지의 감정평가는 <strong>공시지가 기준법</strong>을 적용하여 산정하였습니다.</p>
        <p>공시지가를 기준으로 주변 거래사례, 개발 가능성, 입지 조건 등을 종합적으로 고려하여 평가하였습니다.</p>
        
        <h3 class="section-subtitle">평가 상세</h3>
        <table class="data-table">
            <tr>
                <th>구분</th>
                <th>내용</th>
            </tr>
            <tr>
                <td>평가 방법</td>
                <td>{appraisal_details.get('method', '공시지가 기준법')}</td>
            </tr>
            <tr>
                <td>기준 공시지가</td>
                <td>{format_currency(appraisal_details.get('base_price'))}</td>
            </tr>
            <tr>
                <td>평가 조정률</td>
                <td>{format_percentage(appraisal_details.get('adjustment_rate'))}</td>
            </tr>
            <tr>
                <td>최종 단가</td>
                <td>{format_currency(appraisal_details.get('unit_price'))}</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2 class="section-title">💼 거래사례 분석</h2>
        <p>주변 {transaction_count}건의 거래사례를 분석하여 시장 가격 적정성을 검증하였습니다.</p>
        
        <table class="data-table">
            <thead>
                <tr>
                    <th>거래일</th>
                    <th>거래면적</th>
                    <th>거래금액</th>
                    <th>거리</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Add transaction cases
    transaction_cases = transactions.get("cases", [])
    if transaction_cases:
        for case in transaction_cases[:5]:  # Show top 5
            content += f"""
                <tr>
                    <td>{case.get('date', 'N/A')}</td>
                    <td>{case.get('area', 'N/A')}㎡</td>
                    <td>{format_currency(case.get('amount'))}</td>
                    <td>{case.get('distance', 'N/A')}m</td>
                </tr>
            """
    else:
        content += """
                <tr>
                    <td colspan="4" style="text-align: center; color: #999;">거래사례 데이터가 없습니다</td>
                </tr>
        """
    
    content += """
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2 class="section-title">🎯 평가 신뢰도</h2>
        <div class="info-grid">
    """
    
    # Add confidence factors
    for factor, score in confidence_factors.items():
        if isinstance(score, (int, float)):
            content += f"""
            <div class="info-card">
                <div class="info-card-title">{factor}</div>
                <div class="info-card-value">{format_percentage(score)}</div>
            </div>
            """
    
    content += """
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">📝 감정평가사 의견</h2>
        <div class="highlight-box">
            <p style="line-height: 1.8;">
                본 토지는 주변 개발 여건 및 교통 접근성이 양호하며, 
                공시지가 및 주변 거래사례를 종합적으로 고려할 때 
                감정평가액은 적정한 것으로 판단됩니다.
            </p>
            <p style="margin-top: 15px; line-height: 1.8;">
                향후 지역 개발 계획 및 인프라 확충에 따라 
                토지 가치 상승 가능성이 있을 것으로 예상됩니다.
            </p>
        </div>
    </div>
    """
    
    return content


def _generate_m3_content(summary: Dict, details: Dict) -> str:
    """Generate M3 (Housing Type) report content"""
    
    selected_type = summary.get("selected_type", "N/A")
    confidence = summary.get("confidence_pct")
    demand_score = summary.get("demand_score")
    
    content = f"""
    <div class="section">
        <h2 class="section-title">🏘️ 공급 유형 판단 결과</h2>
        <div class="highlight-box">
            <h3>권장 공급 유형</h3>
            <div style="font-size: 36px; font-weight: 700; color: #667eea; margin: 15px 0;">
                {selected_type}
            </div>
            <p style="color: #666;">
                수요 점수: {demand_score or 'N/A'} | 신뢰도: {format_percentage(confidence)}
            </p>
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">📊 수요 분석</h2>
        <p>입지 특성 및 주변 인구 구조를 분석하여 최적의 공급 유형을 도출하였습니다.</p>
        
        <h3 class="section-subtitle">입지 특성 분석</h3>
        <div class="info-grid">
    """
    
    # Add location analysis
    location_analysis = details.get("location_analysis", {})
    for key, value in location_analysis.items():
        content += f"""
        <div class="info-card">
            <div class="info-card-title">{key}</div>
            <div class="info-card-value">{value}</div>
        </div>
        """
    
    content += """
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">💡 권장사항</h2>
        <div class="highlight-box">
            <p style="line-height: 1.8;">
                입지 분석 결과, <strong>""" + selected_type + """</strong> 공급이 가장 적합할 것으로 판단됩니다.
                주변 생활 패턴과 인구 구조를 고려할 때 해당 유형에 대한 수요가 높을 것으로 예상됩니다.
            </p>
        </div>
    </div>
    """
    
    return content


def _generate_m4_content(summary: Dict, details: Dict) -> str:
    """Generate M4 (Capacity) report content"""
    
    legal_units = summary.get("legal_units", "N/A")
    incentive_units = summary.get("incentive_units", "N/A")
    parking_alt_a = summary.get("parking_alt_a", "N/A")
    parking_alt_b = summary.get("parking_alt_b", "N/A")
    
    content = f"""
    <div class="section">
        <h2 class="section-title">🏗️ 건축 규모 산정 결과</h2>
        <div class="info-grid">
            <div class="info-card">
                <div class="info-card-title">법정 용적률 기준</div>
                <div class="info-card-value">{legal_units}세대</div>
            </div>
            <div class="info-card">
                <div class="info-card-title">인센티브 적용</div>
                <div class="info-card-value">{incentive_units}세대</div>
            </div>
            <div class="info-card">
                <div class="info-card-title">주차 대안 A</div>
                <div class="info-card-value">{parking_alt_a}대</div>
            </div>
            <div class="info-card">
                <div class="info-card-title">주차 대안 B</div>
                <div class="info-card-value">{parking_alt_b}대</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">📐 설계 근거</h2>
        <p>건축법, 용적률 및 건폐율 규정을 준수하며 최적의 규모를 산정하였습니다.</p>
        
        <table class="data-table">
            <tr>
                <th>구분</th>
                <th>법정 기준</th>
                <th>인센티브 적용</th>
            </tr>
            <tr>
                <td>총 세대수</td>
                <td>{legal_units}세대</td>
                <td>{incentive_units}세대</td>
            </tr>
            <tr>
                <td>주차 대수</td>
                <td>{parking_alt_a}대</td>
                <td>{parking_alt_b}대</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2 class="section-title">💡 설계 권장사항</h2>
        <div class="highlight-box">
            <p style="line-height: 1.8;">
                법적 규제를 준수하면서 최대한의 세대수를 확보할 수 있도록 계획하였습니다.
                인센티브 적용 시 추가 세대 확보가 가능합니다.
            </p>
        </div>
    </div>
    """
    
    return content


def _generate_m5_content(summary: Dict, details: Dict) -> str:
    """Generate M5 (Feasibility) report content"""
    
    npv = summary.get("npv_public_krw")
    irr = summary.get("irr_pct")
    roi = summary.get("roi_pct")
    grade = summary.get("grade", "N/A")
    
    content = f"""
    <div class="section">
        <h2 class="section-title">📊 사업성 분석 결과</h2>
        <div class="highlight-box">
            <h3>사업성 등급</h3>
            <div style="font-size: 48px; font-weight: 700; color: #667eea; margin: 15px 0;">
                {grade}등급
            </div>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <div class="info-card-title">순현재가치 (NPV)</div>
                <div class="info-card-value">{format_currency(npv)}</div>
            </div>
            <div class="info-card">
                <div class="info-card-title">내부수익률 (IRR)</div>
                <div class="info-card-value">{format_percentage(irr)}</div>
            </div>
            <div class="info-card">
                <div class="info-card-title">투자수익률 (ROI)</div>
                <div class="info-card-value">{format_percentage(roi)}</div>
            </div>
            <div class="info-card">
                <div class="info-card-title">사업성 등급</div>
                <div class="info-card-value">{grade}</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">💰 재무 분석</h2>
        <p>LH 매입 모델을 기준으로 사업성을 분석하였습니다.</p>
        
        <table class="data-table">
            <tr>
                <th>항목</th>
                <th>금액/비율</th>
            </tr>
            <tr>
                <td>순현재가치 (NPV)</td>
                <td>{format_currency(npv)}</td>
            </tr>
            <tr>
                <td>내부수익률 (IRR)</td>
                <td>{format_percentage(irr)}</td>
            </tr>
            <tr>
                <td>투자수익률 (ROI)</td>
                <td>{format_percentage(roi)}</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2 class="section-title">📝 재무 평가 의견</h2>
        <div class="highlight-box">
            <p style="line-height: 1.8;">
                본 사업은 <strong>{grade}등급</strong>의 사업성을 보유하고 있습니다.
                NPV가 {'양(+)의 값' if npv and npv > 0 else '음(-)의 값'}을 나타내어 
                {'경제적 타당성이 있는' if npv and npv > 0 else '추가 검토가 필요한'} 것으로 판단됩니다.
            </p>
        </div>
    </div>
    """
    
    return content


def _generate_m6_content(summary: Dict, details: Dict) -> str:
    """Generate M6 (LH Review) report content"""
    
    decision = summary.get("decision", "N/A")
    total_score = summary.get("total_score", 0)
    grade = summary.get("grade", "N/A")
    
    # Determine decision color
    decision_color = "#27ae60" if decision == "GO" else "#e74c3c" if decision == "NO-GO" else "#f39c12"
    
    content = f"""
    <div class="section">
        <h2 class="section-title">✅ LH 종합 판단 결과</h2>
        <div class="highlight-box">
            <h3>최종 판정</h3>
            <div style="font-size: 48px; font-weight: 700; color: {decision_color}; margin: 15px 0;">
                {decision}
            </div>
            <p style="color: #666;">
                종합 점수: {total_score}/110점 | 등급: {grade}
            </p>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <div class="info-card-title">최종 판정</div>
                <div class="info-card-value" style="color: {decision_color};">{decision}</div>
            </div>
            <div class="info-card">
                <div class="info-card-title">종합 점수</div>
                <div class="info-card-value">{total_score}점</div>
            </div>
            <div class="info-card">
                <div class="info-card-title">종합 등급</div>
                <div class="info-card-value">{grade}</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">📊 세부 평가 항목</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>평가 항목</th>
                    <th>배점</th>
                    <th>득점</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Add scoring details
    scoring_details = details.get("scoring", {})
    for category, score_data in scoring_details.items():
        if isinstance(score_data, dict):
            max_score = score_data.get("max", 0)
            actual_score = score_data.get("score", 0)
            content += f"""
                <tr>
                    <td>{category}</td>
                    <td>{max_score}점</td>
                    <td>{actual_score}점</td>
                </tr>
            """
    
    content += """
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2 class="section-title">📝 종합 의견</h2>
        <div class="highlight-box">
            <p style="line-height: 1.8;">
                종합 검토 결과, 본 사업은 <strong>""" + decision + """</strong> 판정을 받았습니다.
                총 110점 만점에 """ + str(total_score) + """점을 획득하여 <strong>""" + grade + """등급</strong>으로 평가되었습니다.
            </p>
    """
    
    if decision == "GO":
        content += """
            <p style="margin-top: 15px; line-height: 1.8;">
                사업 추진을 권장하며, 세부 실행 계획 수립을 진행하시기 바랍니다.
            </p>
        """
    elif decision == "CONDITIONAL":
        content += """
            <p style="margin-top: 15px; line-height: 1.8;">
                조건부 승인으로, 일부 보완 사항을 개선한 후 재검토를 권장합니다.
            </p>
        """
    else:
        content += """
            <p style="margin-top: 15px; line-height: 1.8;">
                현재 조건에서는 사업 추진이 어려울 것으로 판단되며, 대안 검토를 권장합니다.
            </p>
        """
    
    content += """
        </div>
    </div>
    """
    
    return content
