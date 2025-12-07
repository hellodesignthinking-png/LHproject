"""
ZeroSite v20 Expert Report Generator
=====================================

Full-featured Expert Edition report generation with v20 data
Generates complete 50-60 page LH submission report

Author: Na TaiHeum (나태흠)
Organization: Antenna Holdings
Version: v20 Expert Edition
Date: 2025-12-07
"""

from flask import Flask, render_template, request, jsonify, Response
from app.services_v13.report_full.report_context_builder import ReportContextBuilder
from jinja2 import Template
import json
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Load Expert Edition template
TEMPLATE_PATH = Path("/home/user/webapp/app/services_v13/report_full/lh_expert_edition_v3.html.jinja2")

# ============================================================================
# SIMPLE WEB INTERFACE
# ============================================================================

INTERFACE_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZeroSite v20 Expert Report Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Noto Sans KR', -apple-system, sans-serif;
            background: linear-gradient(135deg, #005BAC 0%, #003D73 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }
        
        .header h1 {
            font-size: 36px;
            color: #005BAC;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 16px;
        }
        
        .form-panel {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #005BAC;
        }
        
        .quick-btns {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .quick-btn {
            padding: 10px;
            background: #f0f0f0;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .quick-btn:hover {
            background: #005BAC;
            color: white;
        }
        
        .btn-primary {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #005BAC 0%, #003D73 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 91, 172, 0.4);
        }
        
        .btn-primary:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
            background: white;
            border-radius: 20px;
            margin-top: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #005BAC;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .result {
            display: none;
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-top: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .result.show {
            display: block;
        }
        
        .result h2 {
            color: #005BAC;
            margin-bottom: 20px;
        }
        
        .download-btn {
            display: inline-block;
            padding: 16px 32px;
            background: linear-gradient(135deg, #27AE60 0%, #229954 100%);
            color: white;
            text-decoration: none;
            border-radius: 10px;
            font-weight: 700;
            font-size: 16px;
        }
        
        .download-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(39, 174, 96, 0.4);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ ZeroSite v20</h1>
            <p>Expert Edition Report Generator</p>
            <p style="font-size: 14px; margin-top: 10px; color: #999;">
                Complete 50-60 Page LH Submission Report
            </p>
        </div>
        
        <div class="form-panel">
            <h2 style="margin-bottom: 20px; color: #005BAC;">프로젝트 정보 입력</h2>
            
            <div class="quick-btns">
                <button class="quick-btn" onclick="setQuick('서울특별시 마포구 월드컵북로 120', 660, 10000000)">서울 마포구</button>
                <button class="quick-btn" onclick="setQuick('서울특별시 강남구 역삼동 123', 500, 15000000)">서울 강남구</button>
                <button class="quick-btn" onclick="setQuick('경기도 성남시 분당구 정자동 178-1', 700, 8000000)">경기 분당</button>
                <button class="quick-btn" onclick="setQuick('경기도 고양시 일산동구 장항동 906', 800, 6000000)">경기 일산</button>
            </div>
            
            <div class="form-group">
                <label>주소</label>
                <input type="text" id="address" value="서울특별시 마포구 월드컵북로 120">
            </div>
            
            <div class="form-group">
                <label>토지 면적 (㎡)</label>
                <input type="number" id="land_area" value="660" step="10">
            </div>
            
            <div class="form-group">
                <label>감정평가 단가 (원/㎡)</label>
                <input type="number" id="appraisal" value="10000000" step="1000000">
            </div>
            
            <button class="btn-primary" onclick="generateReport()" id="generateBtn">
                📄 전문가 리포트 생성
            </button>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p><strong>리포트 생성 중...</strong></p>
            <p style="font-size: 14px; color: #666; margin-top: 10px;">
                50-60 페이지 Expert Edition 생성 중 (약 10~15초 소요)
            </p>
        </div>
        
        <div class="result" id="result">
            <h2>✅ 리포트 생성 완료!</h2>
            <p style="margin-bottom: 20px; color: #666;">
                완전한 Expert Edition 보고서가 생성되었습니다.
            </p>
            <a class="download-btn" id="downloadLink" href="#" target="_blank">
                📥 Expert Report 다운로드 (50-60 페이지)
            </a>
        </div>
    </div>
    
    <script>
        function setQuick(addr, area, price) {
            document.getElementById('address').value = addr;
            document.getElementById('land_area').value = area;
            document.getElementById('appraisal').value = price;
        }
        
        async function generateReport() {
            const address = document.getElementById('address').value;
            const land_area = parseFloat(document.getElementById('land_area').value);
            const appraisal = parseFloat(document.getElementById('appraisal').value);
            
            document.getElementById('loading').classList.add('show');
            document.getElementById('result').classList.remove('show');
            document.getElementById('generateBtn').disabled = true;
            
            try {
                const response = await fetch('/api/generate_expert_report', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        address: address,
                        land_area_sqm: land_area,
                        appraisal_price: appraisal
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('downloadLink').href = data.report_url;
                    document.getElementById('result').classList.add('show');
                } else {
                    alert('오류: ' + data.error);
                }
            } catch (error) {
                alert('오류: ' + error.message);
            } finally {
                document.getElementById('loading').classList.remove('show');
                document.getElementById('generateBtn').disabled = false;
            }
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Main interface"""
    return INTERFACE_HTML


@app.route('/api/generate_expert_report', methods=['POST'])
def generate_expert_report():
    """
    Generate complete Expert Edition report with v20 data
    """
    try:
        data = request.json
        
        address = data.get('address', '서울특별시 마포구 월드컵북로 120')
        land_area_sqm = data.get('land_area_sqm', 660.0)
        appraisal_price = data.get('appraisal_price', 10_000_000)
        
        # Build v20 context
        builder = ReportContextBuilder()
        context = builder.build_context(
            address=address,
            land_area_sqm=land_area_sqm,
            coordinates=None,
            multi_parcel=False,
            parcels=None,
            additional_params={'appraisal_price': appraisal_price}
        )
        
        # Add safe defaults for undefined values
        context = add_safe_defaults(context)
        
        # Save context for later retrieval
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        context_cache[timestamp] = {
            'address': address,
            'land_area_sqm': land_area_sqm,
            'appraisal_price': appraisal_price,
            'context': context,
            'created_at': datetime.now()
        }
        
        return jsonify({
            'success': True,
            'report_url': f'/report/{timestamp}',
            'timestamp': timestamp
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


def add_safe_defaults(context):
    """
    Add safe default values for all numeric fields that might be undefined
    """
    # Ensure all numeric values have defaults
    safe_context = context.copy()
    
    # Top-level template variables (direct access in template)
    safe_context.setdefault('address', '서울특별시 마포구 월드컵북로 120')
    safe_context.setdefault('land_area_sqm', 660.0)
    safe_context.setdefault('building_coverage_ratio', 50.0)
    safe_context.setdefault('floor_area_ratio', 300.0)
    safe_context.setdefault('building_area', 330.0)
    safe_context.setdefault('gross_floor_area', 1980.0)
    safe_context.setdefault('total_units', 30)
    safe_context.setdefault('avg_unit_area', 66.0)
    
    # Site overview defaults
    if 'site_overview' not in safe_context:
        safe_context['site_overview'] = {}
    
    site = safe_context['site_overview']
    site.setdefault('address', safe_context.get('address', '서울특별시 마포구 월드컵북로 120'))
    site.setdefault('land_area_sqm', safe_context.get('land_area_sqm', 660.0))
    site.setdefault('building_area', 330.0)
    site.setdefault('gross_floor_area', 1980.0)
    site.setdefault('floor_area_ratio', 300.0)
    site.setdefault('building_coverage_ratio', 50.0)
    
    # Zoning regulations defaults
    if 'zoning_regulations' not in safe_context:
        safe_context['zoning_regulations'] = {}
    
    zoning = safe_context['zoning_regulations']
    zoning.setdefault('zone_type', '제2종일반주거지역')
    zoning.setdefault('max_floor_area_ratio', 300.0)
    zoning.setdefault('max_building_coverage', 50.0)
    zoning.setdefault('max_height', 35.0)
    
    # Financial defaults
    if 'financial_analysis' not in safe_context:
        safe_context['financial_analysis'] = {}
    
    finance = safe_context['financial_analysis']
    finance.setdefault('total_investment', 15000000000)
    finance.setdefault('land_cost', 6600000000)
    finance.setdefault('construction_cost', 6930000000)
    finance.setdefault('npv', 0)
    finance.setdefault('irr', 0)
    finance.setdefault('roi', 0)
    
    # v19_finance defaults
    if 'v19_finance' in safe_context:
        v19 = safe_context['v19_finance']
        
        if 'profit_calculation' in v19:
            profit = v19['profit_calculation']
            profit.setdefault('roi_pct', 0)
            profit.setdefault('irr_pct', 0)
            profit.setdefault('payback_years', 0)
            profit.setdefault('total_capex', 15000000000)
            profit.setdefault('lh_purchase_price', 12000000000)
            profit.setdefault('profit', -3000000000)
    
    # Construction cost defaults
    if 'construction_cost' not in safe_context:
        safe_context['construction_cost'] = {}
    
    construction = safe_context['construction_cost']
    construction.setdefault('total_cost', 6930000000)
    construction.setdefault('per_sqm', 3500000)
    
    # Metadata defaults
    if 'metadata' not in safe_context:
        safe_context['metadata'] = {}
    
    meta = safe_context['metadata']
    meta.setdefault('report_title', 'LH 신축매입임대 사업 타당성 분석 보고서')
    meta.setdefault('generated_date', '2025년 12월 07일')
    meta.setdefault('author', 'Na TaiHeum (나태흠)')
    meta.setdefault('organization', 'Antenna Holdings')
    
    return safe_context


# Cache for storing generated contexts
context_cache = {}


@app.route('/report/<timestamp>')
def view_report(timestamp):
    """
    View generated report
    """
    try:
        # Try to get cached context
        if timestamp in context_cache:
            cached = context_cache[timestamp]
            context = cached['context']
        else:
            # Generate new context with default data
            builder = ReportContextBuilder()
            context = builder.build_context(
                address='서울특별시 마포구 월드컵북로 120',
                land_area_sqm=660.0,
                coordinates=None,
                multi_parcel=False,
                parcels=None,
                additional_params={'appraisal_price': 10_000_000}
            )
            context = add_safe_defaults(context)
        
        # Deep clean context - convert all None to safe values
        context = deep_clean_context(context)
        
        # Load template
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Create Jinja2 environment with safe filters
        from jinja2 import Environment, select_autoescape
        env = Environment(
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Add safe filters
        def safe_round(value, precision=0):
            """Safely round a value, return 0 if undefined/None"""
            try:
                if value is None or value == '':
                    return 0
                return round(float(value), int(precision))
            except (ValueError, TypeError):
                return 0
        
        def safe_int(value):
            """Safely convert to int, return 0 if undefined/None"""
            try:
                if value is None or value == '':
                    return 0
                return int(float(value))
            except (ValueError, TypeError):
                return 0
        
        def safe_float(value):
            """Safely convert to float, return 0.0 if undefined/None"""
            try:
                if value is None or value == '':
                    return 0.0
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        
        env.filters['round'] = safe_round  # Override default round
        env.filters['safe_round'] = safe_round
        env.filters['safe_int'] = safe_int
        env.filters['safe_float'] = safe_float
        env.filters['int'] = safe_int  # Override default int
        env.filters['float'] = safe_float  # Override default float
        
        template = env.from_string(template_content)
        
        # Render with safe context
        html_content = template.render(**context)
        
        return Response(
            html_content,
            mimetype='text/html',
            headers={
                'Content-Disposition': f'inline; filename=zerosite_expert_v20_{timestamp}.html'
            }
        )
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"""
        <html>
        <head><title>Error</title></head>
        <body style="padding: 40px; font-family: monospace;">
            <h1 style="color: #C0392B;">Report Generation Error</h1>
            <h3>Error Message:</h3>
            <pre style="background: #f5f5f5; padding: 20px; border-radius: 8px;">{str(e)}</pre>
            <h3>Traceback:</h3>
            <pre style="background: #f5f5f5; padding: 20px; border-radius: 8px;">{error_detail}</pre>
        </body>
        </html>
        """, 500


def deep_clean_context(context):
    """
    Recursively clean context, replacing None/undefined with safe values
    """
    import copy
    cleaned = copy.deepcopy(context)
    
    def clean_value(value):
        if value is None or value == '':
            return 0
        elif isinstance(value, dict):
            return {k: clean_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [clean_value(v) for v in value]
        else:
            return value
    
    # Clean numeric fields recursively
    if isinstance(cleaned, dict):
        for key, value in cleaned.items():
            if isinstance(value, (dict, list)):
                cleaned[key] = clean_value(value)
            elif value is None or value == '':
                # Try to infer safe default based on key name
                if any(x in key.lower() for x in ['area', 'ratio', 'cost', 'price', 'value']):
                    cleaned[key] = 0
                elif 'pct' in key.lower() or 'percent' in key.lower():
                    cleaned[key] = 0.0
                else:
                    cleaned[key] = value  # Keep as is for non-numeric
    
    return cleaned


if __name__ == '__main__':
    print("=" * 80)
    print("🚀 ZeroSite v20 Expert Report Generator Starting...")
    print("=" * 80)
    print()
    print("📄 Features:")
    print("   - Complete 50-60 page Expert Edition")
    print("   - v20 data integration")
    print("   - LH submission-ready format")
    print("   - Professional academic style")
    print()
    print("📍 Server will run on port 5005")
    print()
    app.run(host='0.0.0.0', port=5005, debug=False)
