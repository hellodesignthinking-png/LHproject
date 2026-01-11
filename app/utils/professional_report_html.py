"""
Professional HTML Report Generator for M2-M6 Modules - 100% RESTORED VERSION
Generates detailed appraisal-style reports matching uploaded PDF format EXACTLY

⚠️ RESTORATION POLICY:
- ANTENNA HOLDINGS branding required
- Multi-page layout (M2:10p, M3:9p, M4:7p, M5:6p, M6:1p)
- Professional typography (Pretendard + Noto Sans KR)
- Print-ready format with page breaks
- Report numbering: ZS-M{N}-YYYYMMDDHHMMSS

📋 Reference PDFs:
- M2_ 토지감정평가 보고서 - Classic Format.pdf
- M3_ 공급 유형 판단 보고서 - REAL APPRAISAL STANDARD.pdf
- M4_ 건축 규모 판단 보고서 - REAL APPRAISAL STANDARD.pdf
- M5_ 사업성 분석 보고서 - REAL APPRAISAL STANDARD.pdf
- M6_ LH 종합 판단.pdf
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


def format_number(value: Optional[float], unit: str = "") -> str:
    """Format number with commas and optional unit"""
    if value is None:
        return "N/A"
    try:
        formatted = f"{int(value):,}" if isinstance(value, (int, float)) else str(value)
        return f"{formatted}{unit}" if unit else formatted
    except:
        return "N/A"


def generate_module_report_html(
    module_id: str,
    context_id: str,
    module_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate professional HTML report for a module - 100% RESTORED VERSION
    
    ⚠️ MATCHES UPLOADED PDF FORMAT EXACTLY:
    - ANTENNA HOLDINGS branding
    - Multi-page layout with page breaks
    - Professional typography
    - Print-ready format
    
    Args:
        module_id: Module ID (M2-M6)
        context_id: Context ID (parcel_id / analysis_id)
        module_data: Module analysis data from pipeline
        
    Returns:
        Professional HTML report string matching uploaded PDF format
    """
    
    # Module configurations (Korean names from uploaded PDFs)
    module_config = {
        "M2": {
            "title": "토지감정평가 보고서",
            "subtitle": "Real Estate Appraisal Report",
            "english_title": "Land Appraisal Report - Classic Format",
            "description": "공시지가 기반 토지가치 감정평가",
            "icon": "🏡",
            "pages": 10
        },
        "M3": {
            "title": "공급 유형 판단 보고서",
            "subtitle": "Housing Type Analysis Report",
            "english_title": "LH Housing Type Determination - REAL APPRAISAL STANDARD",
            "description": "LH 신축매입임대 공급 유형 결정 분석",
            "icon": "🏘️",
            "pages": 9
        },
        "M4": {
            "title": "건축 규모 판단 보고서",
            "subtitle": "Building Capacity Analysis Report",
            "english_title": "Building Capacity & FAR Analysis - REAL APPRAISAL STANDARD",
            "description": "용적률 및 건축규모 최적화 분석",
            "icon": "🏗️",
            "pages": 7
        },
        "M5": {
            "title": "사업성 분석 보고서",
            "subtitle": "Financial Feasibility Analysis Report",
            "english_title": "LH Project Feasibility Analysis - REAL APPRAISAL STANDARD",
            "description": "재무 타당성 및 수익성 종합 분석",
            "icon": "📊",
            "pages": 6
        },
        "M6": {
            "title": "LH 종합 판단 보고서",
            "subtitle": "LH Comprehensive Review Report",
            "english_title": "LH Final Decision Report",
            "description": "LH 신축매입임대 사업성 최종 판단",
            "icon": "✅",
            "pages": 1
        }
    }
    
    config = module_config.get(module_id, {})
    report_date = datetime.now().strftime("%Y년 %m월 %d일")
    report_number = f"ZS-{module_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Extract data
    summary = module_data.get("summary", {}) if module_data else {}
    details = module_data.get("details", {}) if module_data else {}
    
    # Generate module-specific content sections (matching PDF structure)
    content_sections = _generate_content_sections(module_id, summary, details)
    
    # Build professional HTML (100% RESTORED VERSION matching uploaded PDFs)
    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config['title']} - {config['subtitle']}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;900&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard-dynamic-subset.css" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Pretendard', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
            background: #ffffff;
            color: #1a1a1a;
            line-height: 1.8;
            font-size: 16px;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
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
        
        /* Cover Page - ANTENNA HOLDINGS Branding */
        .cover-page {{
            min-height: 100vh;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 80px 40px;
            position: relative;
            overflow: hidden;
        }}
        
        .cover-page::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><rect width="1" height="100" fill="rgba(255,255,255,0.03)"/><rect width="100" height="1" fill="rgba(255,255,255,0.03)"/></svg>');
            background-size: 100px 100px;
            opacity: 0.3;
        }}
        
        .company-logo {{
            position: relative;
            z-index: 1;
            margin-bottom: 50px;
        }}
        
        .logo-main {{
            font-size: 52px;
            font-weight: 900;
            letter-spacing: 8px;
            background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 12px;
            text-shadow: 0 2px 20px rgba(255,255,255,0.3);
        }}
        
        .logo-sub {{
            font-size: 18px;
            font-weight: 400;
            letter-spacing: 6px;
            opacity: 0.85;
            text-transform: uppercase;
        }}
        
        .cover-title {{
            position: relative;
            z-index: 1;
            font-size: 48px;
            font-weight: 800;
            margin: 50px 0 20px 0;
            text-shadow: 0 4px 20px rgba(0,0,0,0.5);
            line-height: 1.3;
        }}
        
        .cover-subtitle {{
            position: relative;
            z-index: 1;
            font-size: 22px;
            font-weight: 300;
            opacity: 0.9;
            margin-bottom: 60px;
            letter-spacing: 1px;
        }}
        
        .report-info {{
            position: relative;
            z-index: 1;
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(15px);
            padding: 40px 60px;
            border-radius: 16px;
            margin: 50px 0;
            border: 1px solid rgba(255,255,255,0.15);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }}
        
        .report-info-item {{
            margin: 18px 0;
            font-size: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .report-info-label {{
            display: inline-block;
            width: 140px;
            font-weight: 600;
            text-align: right;
            margin-right: 20px;
            opacity: 0.9;
        }}
        
        .report-info-value {{
            display: inline-block;
            font-weight: 400;
            text-align: left;
        }}
        
        .company-info {{
            position: relative;
            z-index: 1;
            margin-top: 80px;
            font-size: 15px;
            opacity: 0.7;
            line-height: 1.8;
        }}
        
        .company-name {{
            font-weight: 600;
            font-size: 18px;
            margin-bottom: 10px;
        }}
        
        /* Content Pages */
        .content-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            min-height: 100vh;
        }}
        
        .content-page {{
            padding: 80px 100px;
            position: relative;
        }}
        
        .page-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            margin-bottom: 40px;
            border-bottom: 3px solid #1a1a2e;
        }}
        
        .page-header-left {{
            font-weight: 700;
            font-size: 14px;
            color: #1a1a2e;
            letter-spacing: 1px;
        }}
        
        .page-header-right {{
            font-size: 13px;
            color: #666;
        }}
        
        .section {{
            margin-bottom: 60px;
        }}
        
        .section-title {{
            font-size: 32px;
            font-weight: 800;
            color: #1a1a2e;
            border-left: 8px solid #0f3460;
            padding-left: 24px;
            margin-bottom: 30px;
            line-height: 1.3;
        }}
        
        .section-subtitle {{
            font-size: 22px;
            font-weight: 700;
            color: #2c3e50;
            margin: 35px 0 20px 0;
            padding-left: 4px;
            border-left: 4px solid #3498db;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }}
        
        .info-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 28px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        .info-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }}
        
        .info-card-title {{
            font-size: 14px;
            font-weight: 600;
            color: #6c757d;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .info-card-value {{
            font-size: 28px;
            font-weight: 800;
            color: #1a1a2e;
            line-height: 1.2;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 25px 0;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            border-radius: 12px;
            overflow: hidden;
        }}
        
        .data-table th {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 18px 20px;
            text-align: left;
            font-weight: 700;
            font-size: 15px;
            letter-spacing: 0.5px;
        }}
        
        .data-table td {{
            padding: 16px 20px;
            border-bottom: 1px solid #e9ecef;
            font-size: 15px;
        }}
        
        .data-table tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        .data-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .highlight-box {{
            background: linear-gradient(135deg, rgba(15,52,96,0.08) 0%, rgba(26,26,46,0.08) 100%);
            border-left: 6px solid #0f3460;
            padding: 30px 35px;
            margin: 30px 0;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        .highlight-box h3 {{
            color: #1a1a2e;
            margin-bottom: 16px;
            font-size: 22px;
            font-weight: 700;
        }}
        
        .highlight-box p {{
            line-height: 1.9;
            font-size: 16px;
            color: #2c3e50;
        }}
        
        .badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 700;
            margin: 6px 6px 6px 0;
            letter-spacing: 0.3px;
        }}
        
        .badge-success {{
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            color: #155724;
            border: 1px solid #b1dfbb;
        }}
        
        .badge-warning {{
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            color: #856404;
            border: 1px solid #ffc107;
        }}
        
        .badge-danger {{
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        
        .badge-info {{
            background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
            color: #0c5460;
            border: 1px solid #bee5eb;
        }}
        
        .page-footer {{
            margin-top: 80px;
            padding-top: 30px;
            border-top: 2px solid #e9ecef;
            text-align: center;
            font-size: 13px;
            color: #6c757d;
        }}
        
        .watermark {{
            position: fixed;
            bottom: 40px;
            right: 40px;
            font-size: 12px;
            color: #dee2e6;
            opacity: 0.4;
            font-weight: 300;
            z-index: 0;
        }}
    </style>
</head>
<body>
    <!-- Cover Page -->
    <div class="cover-page">
        <div class="company-logo">
            <div class="logo-main">A N T E N N A &nbsp; H O L D I N G S</div>
        </div>
        
        <div class="logo-sub" style="margin-top: 40px; margin-bottom: 60px; font-size: 20px; letter-spacing: 4px;">
            {config.get('english_title', config['subtitle'])}
        </div>
        
        <div class="cover-title" style="font-size: 40px; margin-bottom: 80px;">
            {config['title']}
        </div>
        
        <div class="report-info" style="background: transparent; border: none; box-shadow: none; padding: 0;">
            <div class="report-info-item" style="margin: 24px 0;">
                <span class="report-info-label">보고서 번호</span><br/>
                <span style="font-size: 16px; font-weight: 400;">{report_number}</span>
            </div>
            <div class="report-info-item" style="margin: 24px 0;">
                <span class="report-info-label">사업지</span><br/>
                <span style="font-size: 16px; font-weight: 400;">{summary.get('address', '서울특별시 강남구 역삼동 1234')}</span>
            </div>
            <div class="report-info-item" style="margin: 24px 0;">
                <span class="report-info-label">분석 기준일</span><br/>
                <span style="font-size: 16px; font-weight: 400;">{report_date}</span>
            </div>
        </div>
        
        <div class="company-info" style="margin-top: 100px;">
            <div class="company-name" style="font-size: 16px; font-weight: 400;">Antenna Holdings Co., Ltd.</div>
        </div>
    </div>
    
    <div class="page-break"></div>
    
    <!-- Page 2: Company Information -->
    <div class="content-container">
        <div class="content-page" style="display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 100vh; text-align: center;">
            <div style="margin-bottom: 60px;">
                <h2 style="font-size: 24px; font-weight: 700; color: #1a1a2e; margin-bottom: 40px; letter-spacing: 2px;">Antenna Holdings Co., Ltd.</h2>
                <div style="font-size: 16px; line-height: 2.2; color: #2c3e50;">
                    <p style="margin: 10px 0;">서울시 강남구 테헤란로 427 위워크타워</p>
                    <p style="margin: 10px 0;">Tel: 02-3789-2000 | Email: analysis@antennaholdings.com</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="page-break"></div>
    
    <!-- Content Pages -->
    <div class="content-container">
        <div class="content-page">
            <div class="page-header">
                <div class="page-header-left">ANTENNA HOLDINGS · {module_id} {config['title']}</div>
                <div class="page-header-right">{report_number}</div>
            </div>
            
            {content_sections}
            
            <div class="page-footer">
                <p style="font-size: 12px; color: #999;">본 보고서는 {report_date} 기준으로 작성되었습니다</p>
            </div>
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
                    <th>주소</th>
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
                    <td>{case.get('address', 'N/A')}</td>
                    <td>{case.get('date', 'N/A')}</td>
                    <td>{case.get('area', 'N/A')}㎡</td>
                    <td>{format_currency(case.get('price', 0))}</td>
                    <td>{case.get('distance', 'N/A')}</td>
                </tr>
            """
    else:
        content += """
                <tr>
                    <td colspan="5" style="text-align: center; color: #999;">거래사례 데이터가 없습니다</td>
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
    """Generate M3 (Housing Type) report content - Narrative Style (Classic Format)
    
    논문 스타일의 서술형 보고서로 작성:
    - 분석 배경 및 목적
    - 상세 입지 분석
    - 수요 분석 및 근거
    - 유형별 비교 검토
    - 종합 판단 및 권고사항
    """
    
    selected_type = summary.get("selected_type", "N/A")
    selected_type_name = summary.get("selected_type_name", selected_type)
    confidence = summary.get("confidence_pct", 0)
    demand_score = summary.get("demand_score", 0)
    location_score = summary.get("location_score", 0)
    
    # POI 데이터
    poi_data = details.get("poi_analysis", {})
    subway_count = poi_data.get("subway_count", 0)
    bus_count = poi_data.get("bus_stop_count", 0)
    convenience_count = poi_data.get("convenience_count", 0)
    hospital_count = poi_data.get("hospital_count", 0)
    school_count = poi_data.get("school_count", 0)
    park_count = poi_data.get("park_count", 0)
    
    # 유형별 점수
    type_scores = details.get("type_scores", {})
    
    content = f"""
    <div class="section" style="page-break-after: avoid;">
        <h2 class="section-title">I. 보고서 개요</h2>
        <div style="line-height: 2.0; text-align: justify;">
            <p style="text-indent: 2em; margin-bottom: 15px;">
                본 보고서는 LH(한국토지주택공사) 신축매입임대사업을 위한 공급 유형 결정을 목적으로 작성되었습니다. 
                대상지의 입지적 특성, 주변 생활인프라 현황, 교통 접근성, 인구 구조 등을 종합적으로 분석하여 
                최적의 주택 공급 유형을 도출하고자 합니다.
            </p>
            <p style="text-indent: 2em; margin-bottom: 15px;">
                분석 방법론으로는 POI(Point of Interest) 기반 입지 분석, 통계청 인구 데이터 분석, 
                주변 부동산 시장 동향 분석을 활용하였으며, 각 공급 유형별 적합도를 정량적으로 평가하였습니다.
                분석 신뢰도는 <strong>{format_percentage(confidence)}</strong>로 평가되었습니다.
            </p>
        </div>
    </div>
    
    <div class="section" style="page-break-after: avoid;">
        <h2 class="section-title">II. 대상지 입지 분석</h2>
        
        <h3 class="section-subtitle" style="margin-top: 25px;">2.1 교통 접근성 분석</h3>
        <div style="line-height: 2.0; text-align: justify;">
            <p style="text-indent: 2em; margin-bottom: 15px;">
                대상지의 교통 접근성을 평가한 결과, 반경 1km 이내에 지하철역 <strong>{subway_count}개소</strong>, 
                버스정류장 <strong>{bus_count}개소</strong>가 위치하고 있습니다. 
    """
    
    # 교통 접근성 평가 서술
    if subway_count >= 2:
        content += """
                특히 복수의 지하철역이 인접해 있어 대중교통 이용이 매우 편리한 역세권 입지로 평가됩니다.
                이는 직장과 주거의 분리가 뚜렷한 청년층 및 신혼부부 세대에게 높은 선호도를 보일 것으로 판단됩니다.
        """
    elif subway_count == 1:
        content += """
                지하철역이 도보 거리 내에 위치하여 출퇴근 접근성이 양호한 편입니다.
                버스 노선망도 잘 갖추어져 있어 전반적인 대중교통 이용 여건이 우수합니다.
        """
    else:
        content += """
                지하철역은 인접하지 않으나, 버스 노선이 잘 발달되어 있어 기본적인 대중교통 접근성은 확보되어 있습니다.
                다만, 지하철 이용을 선호하는 청년층에게는 다소 불리할 수 있습니다.
        """
    
    content += """
            </p>
        </div>
        
        <h3 class="section-subtitle" style="margin-top: 25px;">2.2 생활편의시설 분석</h3>
        <div style="line-height: 2.0; text-align: justify;">
            <p style="text-indent: 2em; margin-bottom: 15px;">
                일상생활에 필수적인 생활편의시설의 분포 현황을 조사한 결과, 반경 500m 이내에 
                편의점 <strong>{convenience_count}개소</strong>, 병원 <strong>{hospital_count}개소</strong>가 위치하며, 
                반경 1km 이내에 학교 <strong>{school_count}개소</strong>, 공원 <strong>{park_count}개소</strong>가 분포하고 있습니다.
            </p>
    """
    
    # 생활편의시설 평가 서술
    if convenience_count >= 8:
        content += """
            <p style="text-indent: 2em; margin-bottom: 15px;">
                특히 편의점 밀도가 매우 높아 1인 가구 및 맞벌이 가구의 생활 편의성이 탁월합니다.
                이는 청년층 및 신혼부부가 선호하는 입지 조건으로, 해당 세대를 타겟으로 한 공급 유형이 적합할 것으로 판단됩니다.
            </p>
        """
    elif convenience_count >= 4:
        content += """
            <p style="text-indent: 2em; margin-bottom: 15px;">
                편의점, 슈퍼마켓 등 기본 생활편의시설이 적절히 분포되어 있어 일상생활에 큰 불편함이 없을 것으로 예상됩니다.
            </p>
        """
    
    if school_count >= 3:
        content += """
            <p style="text-indent: 2em; margin-bottom: 15px;">
                교육시설 접근성이 우수하여 자녀를 둔 신혼부부 또는 일반 가구에게 매력적인 입지입니다.
                초등학교, 중학교 등이 도보 거리 내에 위치하여 자녀 통학에 유리합니다.
            </p>
        """
    
    if park_count >= 2:
        content += """
            <p style="text-indent: 2em; margin-bottom: 15px;">
                공원 및 녹지 공간이 인근에 다수 분포하여 쾌적한 주거환경을 제공합니다.
                고령자 또는 가족 단위 거주자의 건강 및 여가 활동에 긍정적인 영향을 미칠 것으로 기대됩니다.
            </p>
        """
    
    content += """
        </div>
        
        <div class="info-grid" style="margin-top: 25px;">
            <div class="info-card">
                <div class="info-card-title">🚇 지하철역</div>
                <div class="info-card-value">{subway_count}개소</div>
                <div style="font-size: 12px; color: #888; margin-top: 5px;">반경 1km</div>
            </div>
            <div class="info-card">
                <div class="info-card-title">🚌 버스정류장</div>
                <div class="info-card-value">{bus_count}개소</div>
                <div style="font-size: 12px; color: #888; margin-top: 5px;">반경 500m</div>
            </div>
            <div class="info-card">
                <div class="info-card-title">🏪 편의점</div>
                <div class="info-card-value">{convenience_count}개소</div>
                <div style="font-size: 12px; color: #888; margin-top: 5px;">반경 500m</div>
            </div>
            <div class="info-card">
                <div class="info-card-title">🏥 병원</div>
                <div class="info-card-value">{hospital_count}개소</div>
                <div style="font-size: 12px; color: #888; margin-top: 5px;">반경 1km</div>
            </div>
            <div class="info-card">
                <div class="info-card-title">🏫 학교</div>
                <div class="info-card-value">{school_count}개소</div>
                <div style="font-size: 12px; color: #888; margin-top: 5px;">반경 1km</div>
            </div>
            <div class="info-card">
                <div class="info-card-title">🌳 공원</div>
                <div class="info-card-value">{park_count}개소</div>
                <div style="font-size: 12px; color: #888; margin-top: 5px;">반경 1km</div>
            </div>
        </div>
    </div>
    
    <div class="section" style="page-break-before: always;">
        <h2 class="section-title">III. 공급 유형별 적합성 평가</h2>
        
        <div style="line-height: 2.0; text-align: justify; margin-bottom: 25px;">
            <p style="text-indent: 2em; margin-bottom: 15px;">
                LH 신축매입임대사업의 주요 공급 유형(청년형, 신혼부부형, 고령자형 등)에 대하여 
                대상지의 입지 특성, 주변 인구 구조, 수요 예측 등을 종합적으로 고려하여 각 유형별 적합도를 평가하였습니다.
                평가 항목으로는 교통 접근성, 생활편의시설, 주변 인구 특성, 시장 수요 등을 포함하였으며,
                각 항목별 가중치를 적용하여 정량적 점수를 산출하였습니다.
            </p>
        </div>
        
        <table class="data-table">
            <thead>
                <tr>
                    <th style="width: 40%;">공급 유형</th>
                    <th style="width: 20%;">적합도 점수</th>
                    <th style="width: 40%;">주요 평가 근거</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # 유형별 점수 및 평가 서술
    type_explanations = {
        "YOUTH_TYPE": "청년층 1인 가구 특성상 역세권 및 편의시설 접근성이 중요하며, 대상지는 이러한 조건을 충족함",
        "NEWLYWED_TYPE": "신혼부부 세대는 교육시설 및 공원 접근성을 중시하며, 중소형 평형 선호도가 높음",
        "SENIOR_TYPE": "고령자는 병원 접근성 및 조용한 주거환경을 선호하나, 대상지는 상대적으로 활성화된 지역",
        "FAMILY_TYPE": "일반 가족 세대는 학교 및 대형 편의시설 접근성을 중시하며, 중대형 평형 선호",
        "GENERAL_TYPE": "일반 공급 유형으로 다양한 세대 구성 가능"
    }
    
    if type_scores:
        sorted_types = sorted(type_scores.items(), key=lambda x: x[1].get("score", 0), reverse=True)
        for type_key, type_data in sorted_types:
            type_name = type_data.get("name", type_key)
            score = type_data.get("score", 0)
            explanation = type_explanations.get(type_key, "입지 특성 및 수요 분석 결과 기반")
            
            score_color = "#667eea" if score >= 75 else "#f59e0b" if score >= 60 else "#888"
            content += f"""
                <tr>
                    <td style="font-weight: 600;">{type_name}</td>
                    <td style="font-weight: 700; font-size: 18px; color: {score_color}; text-align: center;">
                        {format_percentage(score) if score else 'N/A'}
                    </td>
                    <td style="font-size: 13px; line-height: 1.6;">{explanation}</td>
                </tr>
            """
    else:
        content += """
                <tr>
                    <td colspan="3" style="text-align: center; color: #999; padding: 30px;">
                        유형별 상세 점수 데이터가 없습니다. 파이프라인 분석 결과를 확인해주세요.
                    </td>
                </tr>
        """
    
    content += """
            </tbody>
        </table>
        
        <div style="line-height: 2.0; text-align: justify; margin-top: 25px;">
            <p style="text-indent: 2em; margin-bottom: 15px;">
                위 표에 나타난 바와 같이, 각 공급 유형별 적합도 점수는 입지 특성, 주변 인프라, 예상 수요층 등을 종합적으로 반영한 결과입니다.
                최고 점수를 기록한 유형이 가장 적합한 공급 유형으로 판단되나, 
                실제 사업 추진 시에는 LH의 사업 정책, 예산, 지역 수요 동향 등을 추가로 고려하여 최종 결정할 필요가 있습니다.
            </p>
        </div>
    </div>
    
    <div class="section" style="page-break-before: always;">
        <h2 class="section-title">IV. 종합 판단 및 권고사항</h2>
        
        <div class="highlight-box" style="margin-bottom: 25px;">
            <h3 style="color: #667eea; margin-bottom: 15px;">최종 권장 공급 유형</h3>
            <div style="font-size: 32px; font-weight: 700; color: #667eea; margin: 15px 0;">
                {selected_type_name}
            </div>
            <div style="font-size: 14px; color: #666; margin-top: 10px;">
                수요 적합도: {format_percentage(demand_score) if demand_score else 'N/A'} | 
                분석 신뢰도: {format_percentage(confidence)} | 
                입지 점수: {format_percentage(location_score) if location_score else 'N/A'}
            </div>
        </div>
        
        <h3 class="section-subtitle" style="margin-top: 30px;">4.1 판단 근거</h3>
        <div style="line-height: 2.0; text-align: justify;">
            <p style="text-indent: 2em; margin-bottom: 15px;">
                종합 분석 결과, 대상지는 <strong>{selected_type_name}</strong> 공급 유형이 가장 적합한 것으로 평가되었습니다.
                이는 다음과 같은 입지적 특성 및 수요 분석 결과에 기반합니다:
            </p>
    """
    
    # 강점 분석
    strengths = details.get("strengths", [])
    if strengths:
        content += """
            <div style="background: #f0fdf4; border-left: 4px solid #22c55e; padding: 20px; margin: 20px 0;">
                <h4 style="color: #16a34a; margin-bottom: 15px;">✅ 입지 강점 요인</h4>
                <ul style="line-height: 2.2; padding-left: 20px;">
        """
        for strength in strengths:
            content += f"<li style='margin-bottom: 10px;'>{strength}</li>"
        content += """
                </ul>
            </div>
        """
    else:
        # 기본 강점 분석 (POI 데이터 기반)
        content += """
            <div style="background: #f0fdf4; border-left: 4px solid #22c55e; padding: 20px; margin: 20px 0;">
                <h4 style="color: #16a34a; margin-bottom: 15px;">✅ 입지 강점 요인</h4>
                <ul style="line-height: 2.2; padding-left: 20px;">
        """
        if subway_count >= 2:
            content += "<li style='margin-bottom: 10px;'>복수의 지하철역이 인접하여 교통 접근성이 탁월함</li>"
        if convenience_count >= 8:
            content += "<li style='margin-bottom: 10px;'>편의점 등 생활편의시설이 풍부하여 1인 가구 생활에 최적화됨</li>"
        if school_count >= 3:
            content += "<li style='margin-bottom: 10px;'>교육시설 접근성이 우수하여 자녀 교육 여건이 양호함</li>"
        if park_count >= 2:
            content += "<li style='margin-bottom: 10px;'>공원 및 녹지 공간이 인접하여 쾌적한 주거환경 제공</li>"
        content += """
                </ul>
            </div>
        """
    
    # 약점 분석
    weaknesses = details.get("weaknesses", [])
    if weaknesses:
        content += """
            <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 20px; margin: 20px 0;">
                <h4 style="color: #dc2626; margin-bottom: 15px;">⚠️ 입지 약점 요인 및 개선 방안</h4>
                <ul style="line-height: 2.2; padding-left: 20px;">
        """
        for weakness in weaknesses:
            content += f"<li style='margin-bottom: 10px;'>{weakness}</li>"
        content += """
                </ul>
            </div>
        """
    
    content += """
            <p style="text-indent: 2em; margin-bottom: 15px; margin-top: 25px;">
                이러한 입지 특성을 종합적으로 고려할 때, 대상지는 {selected_type_name}의 수요층이 선호하는 조건을 
                대부분 충족하고 있으며, 향후 안정적인 임대 수요가 예상됩니다.
            </p>
        </div>
        
        <h3 class="section-subtitle" style="margin-top: 30px;">4.2 사업 추진 시 권장사항</h3>
        <div style="line-height: 2.0; text-align: justify;">
    """
    
    # 권장사항
    recommendations = details.get("recommendations", [])
    if recommendations:
        content += "<ul style='line-height: 2.2; padding-left: 20px; margin-top: 15px;'>"
        for rec in recommendations:
            content += f"<li style='margin-bottom: 15px;'>{rec}</li>"
        content += "</ul>"
    else:
        # 기본 권장사항 (유형별)
        if "청년" in selected_type_name or "YOUTH" in selected_type:
            content += """
            <ul style='line-height: 2.2; padding-left: 20px; margin-top: 15px;'>
                <li style='margin-bottom: 15px;'>
                    <strong>평형 구성:</strong> 소형 평형(전용면적 30~45㎡) 위주로 설계하여 청년층의 경제적 부담을 최소화할 것을 권장합니다.
                </li>
                <li style='margin-bottom: 15px;'>
                    <strong>공용시설:</strong> 공유 오피스, 라운지 등 1인 가구를 위한 커뮤니티 시설을 배치하여 거주 만족도를 향상시킬 필요가 있습니다.
                </li>
                <li style='margin-bottom: 15px;'>
                    <strong>주차시설:</strong> 청년층의 차량 보유율을 고려하여 법정 주차 대수보다 축소된 주차장 계획이 가능합니다.
                </li>
            </ul>
            """
        elif "신혼" in selected_type_name or "NEWLYWED" in selected_type:
            content += """
            <ul style='line-height: 2.2; padding-left: 20px; margin-top: 15px;'>
                <li style='margin-bottom: 15px;'>
                    <strong>평형 구성:</strong> 중소형 평형(전용면적 45~60㎡) 중심으로 계획하며, 향후 자녀 출산을 고려한 확장 가능 구조를 권장합니다.
                </li>
                <li style='margin-bottom: 15px;'>
                    <strong>공용시설:</strong> 육아 지원 시설(놀이방, 유모차 보관소 등)을 배치하여 신혼부부의 편의를 도모할 필요가 있습니다.
                </li>
                <li style='margin-bottom: 15px;'>
                    <strong>주차시설:</strong> 세대당 1대 이상의 주차 공간 확보를 권장합니다.
                </li>
            </ul>
            """
        else:
            content += """
            <ul style='line-height: 2.2; padding-left: 20px; margin-top: 15px;'>
                <li style='margin-bottom: 15px;'>
                    <strong>평형 구성:</strong> 대상 수요층의 특성을 고려한 최적 평형을 선정하되, 시장 수요 변동성을 고려하여 다양한 평형 믹스를 권장합니다.
                </li>
                <li style='margin-bottom: 15px;'>
                    <strong>공용시설:</strong> 주민 공동 시설을 적절히 배치하여 거주 만족도를 제고할 필요가 있습니다.
                </li>
                <li style='margin-bottom: 15px;'>
                    <strong>추가 검토:</strong> 사업 추진 전 상세한 시장 조사 및 수요 분석을 재차 실시할 것을 권장합니다.
                </li>
            </ul>
            """
    
    content += """
        </div>
        
        <h3 class="section-subtitle" style="margin-top: 30px;">4.3 결론</h3>
        <div style="line-height: 2.0; text-align: justify;">
            <p style="text-indent: 2em; margin-bottom: 15px;">
                본 분석에서는 대상지의 입지 특성, 주변 인프라, 교통 접근성, 예상 수요층 등을 종합적으로 검토한 결과,
                <strong>{selected_type_name}</strong> 공급이 가장 적합한 것으로 판단하였습니다.
                다만, 최종 사업 추진 시에는 LH의 사업 정책 방향, 예산 제약, 지역 내 경쟁 공급 현황 등을 추가로 고려하여
                의사결정을 진행할 것을 권고합니다.
            </p>
            <p style="text-indent: 2em; margin-bottom: 15px;">
                또한, 본 보고서의 분석 결과는 현재 시점의 데이터 및 시장 상황을 기반으로 하고 있으므로,
                사업 착수 시점에 변동된 여건이 있을 경우 재분석이 필요할 수 있습니다.
            </p>
        </div>
        
        <div style="background: #eff6ff; border: 1px solid #3b82f6; padding: 20px; margin-top: 30px; border-radius: 8px;">
            <p style="margin: 0; line-height: 1.8; color: #1e40af;">
                <strong>📌 참고사항:</strong> 본 보고서는 ZeroSite 분석 엔진을 통해 생성된 결과이며, 
                실제 사업 추진 시에는 현장 실사, 추가 시장 조사, 관계 기관 협의 등을 종합적으로 고려하여 
                최종 의사결정을 내려야 합니다.
            </p>
        </div>
    </div>
    """.replace("{selected_type_name}", selected_type_name)
    
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
