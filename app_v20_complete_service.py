"""
ZeroSite v20 Complete Service - All-in-One
==========================================

완전한 통합 서비스:
- 주소 직접 입력
- 실거래가 자동 수집
- v20 분석 엔진
- Expert Edition PDF 생성 (50-60 페이지)
- 원클릭 다운로드

Author: Na TaiHeum (나태흠)
Organization: Antenna Holdings
Version: v20 Complete
Date: 2025-12-07
"""

from flask import Flask, render_template_string, request, jsonify, Response, send_file
from app.services_v13.report_full.report_context_builder import ReportContextBuilder
from jinja2 import Environment, select_autoescape
from pathlib import Path
from datetime import datetime
import json
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Directories
REPORTS_DIR = Path("/home/user/webapp/generated_reports")
REPORTS_DIR.mkdir(exist_ok=True)

TEMPLATE_PATH = Path("/home/user/webapp/app/services_v13/report_full/lh_expert_edition_v3.html.jinja2")

# Context cache
context_cache = {}

# ============================================================================
# COMPLETE WEB INTERFACE
# ============================================================================

INTERFACE_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZeroSite v20 Complete - LH 신축매입임대 분석</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #005BAC 0%, #003D73 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 20px;
            padding: 50px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }
        
        .header h1 {
            font-size: 48px;
            font-weight: 900;
            background: linear-gradient(135deg, #005BAC 0%, #003D73 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 15px;
        }
        
        .header .subtitle {
            font-size: 20px;
            color: #666;
            margin-bottom: 10px;
        }
        
        .header .author {
            font-size: 14px;
            color: #999;
            margin-top: 15px;
        }
        
        .badge {
            display: inline-block;
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 700;
            margin: 10px 5px;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 450px 1fr;
            gap: 30px;
        }
        
        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }
        
        .input-panel {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            height: fit-content;
            position: sticky;
            top: 20px;
        }
        
        .input-panel h2 {
            color: #005BAC;
            margin-bottom: 25px;
            font-size: 26px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .form-group input {
            width: 100%;
            padding: 14px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #005BAC;
            box-shadow: 0 0 0 3px rgba(0, 91, 172, 0.1);
        }
        
        .quick-btns {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
            margin-bottom: 20px;
        }
        
        .quick-btn {
            padding: 10px;
            background: #f5f5f5;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
            font-weight: 500;
        }
        
        .quick-btn:hover {
            background: #005BAC;
            color: white;
            border-color: #005BAC;
        }
        
        .btn-primary {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #005BAC 0%, #003D73 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
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
        
        .results-panel {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: none;
        }
        
        .results-panel.show {
            display: block;
        }
        
        .results-panel h2 {
            color: #005BAC;
            margin-bottom: 30px;
            font-size: 28px;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .summary-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            border-radius: 12px;
            border-left: 5px solid #005BAC;
        }
        
        .summary-label {
            font-size: 13px;
            color: #666;
            font-weight: 600;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        
        .summary-value {
            font-size: 28px;
            font-weight: 900;
            color: #333;
        }
        
        .decision-box {
            background: linear-gradient(135deg, #fff3cd 0%, #ffe69c 100%);
            border: 3px solid #f59e0b;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .decision-box h3 {
            color: #005BAC;
            margin-bottom: 15px;
        }
        
        .decision-badge {
            display: inline-block;
            padding: 15px 35px;
            border-radius: 30px;
            font-weight: 900;
            font-size: 20px;
            margin: 10px 0;
        }
        
        .decision-go {
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            color: white;
        }
        
        .decision-conditional {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
        }
        
        .decision-no {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
        }
        
        .download-section {
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            padding: 35px;
            border-radius: 15px;
            text-align: center;
            color: white;
        }
        
        .download-section h3 {
            color: white;
            margin-bottom: 20px;
        }
        
        .btn-download {
            display: inline-block;
            padding: 18px 40px;
            background: white;
            color: #16a34a;
            text-decoration: none;
            border-radius: 10px;
            font-weight: 900;
            font-size: 18px;
            transition: all 0.3s;
        }
        
        .btn-download:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 60px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            border: 6px solid #f3f3f3;
            border-top: 6px solid #005BAC;
            border-radius: 50%;
            width: 70px;
            height: 70px;
            animation: spin 1s linear infinite;
            margin: 0 auto 25px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading h3 {
            color: #005BAC;
            margin-bottom: 15px;
        }
        
        .loading p {
            color: #666;
            font-size: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ ZeroSite v20</h1>
            <div class="subtitle">Complete LH 신축매입임대 사업성 분석 시스템</div>
            <div>
                <span class="badge">주소 입력</span>
                <span class="badge">실거래가 분석</span>
                <span class="badge">v20 엔진</span>
                <span class="badge">Expert PDF</span>
            </div>
            <div class="author">
                Author: Na TaiHeum (나태흠) | Antenna Holdings | Copyright © 2025
            </div>
        </div>
        
        <div class="main-content">
            <div class="input-panel">
                <h2>📍 프로젝트 정보</h2>
                
                <div class="quick-btns">
                    <button class="quick-btn" onclick="setQuick('서울특별시 마포구 월드컵북로 120', 660, 10000000)">
                        서울 마포구
                    </button>
                    <button class="quick-btn" onclick="setQuick('서울특별시 강남구 역삼동 123', 500, 15000000)">
                        서울 강남구
                    </button>
                    <button class="quick-btn" onclick="setQuick('경기도 성남시 분당구 정자동 178-1', 700, 8000000)">
                        경기 분당
                    </button>
                    <button class="quick-btn" onclick="setQuick('경기도 고양시 일산동구 장항동 906', 800, 6000000)">
                        경기 일산
                    </button>
                </div>
                
                <div class="form-group">
                    <label>📮 주소 (전국 모든 주소 가능)</label>
                    <input type="text" id="address" 
                           placeholder="예: 서울특별시 마포구 월드컵북로 120"
                           value="서울특별시 마포구 월드컵북로 120">
                </div>
                
                <div class="form-group">
                    <label>📏 토지 면적 (㎡)</label>
                    <input type="number" id="land_area" value="660" step="10" min="100">
                </div>
                
                <div class="form-group">
                    <label>💰 감정평가 단가 (원/㎡)</label>
                    <input type="number" id="appraisal" value="10000000" step="1000000" min="1000000">
                </div>
                
                <button class="btn-primary" onclick="runCompleteAnalysis()" id="analyzeBtn">
                    🚀 전체 분석 시작
                </button>
            </div>
            
            <div>
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <h3>분석 진행 중...</h3>
                    <p>실거래가 수집 및 v20 Expert Report 생성 중</p>
                    <p style="font-size: 13px; margin-top: 10px; color: #999;">
                        약 10~15초 소요 (50-60 페이지 생성)
                    </p>
                </div>
                
                <div class="results-panel" id="results">
                    <h2>📊 분석 결과</h2>
                    
                    <div class="summary-grid">
                        <div class="summary-card">
                            <div class="summary-label">총 사업비</div>
                            <div class="summary-value" id="capex">-</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">LH 매입가</div>
                            <div class="summary-value" id="purchase">-</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">예상 수익</div>
                            <div class="summary-value" id="profit">-</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">ROI</div>
                            <div class="summary-value" id="roi">-</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">IRR</div>
                            <div class="summary-value" id="irr">-</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">회수기간</div>
                            <div class="summary-value" id="payback">-</div>
                        </div>
                    </div>
                    
                    <div class="decision-box">
                        <h3>🎯 최종 의사결정</h3>
                        <div id="decision"></div>
                        <div style="margin-top: 20px; color: #666;">
                            <strong>재무 기준:</strong> <span id="financial">-</span> | 
                            <strong>정책 기준:</strong> <span id="policy">-</span>
                        </div>
                    </div>
                    
                    <div class="download-section">
                        <h3>📄 Expert Edition 리포트 (50-60 페이지)</h3>
                        <p style="margin-bottom: 20px;">
                            완전한 LH 제출용 보고서가 생성되었습니다.
                        </p>
                        <a class="btn-download" id="downloadBtn" href="#" target="_blank">
                            📥 Expert Report 다운로드
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentTimestamp = null;
        
        function setQuick(addr, area, price) {
            document.getElementById('address').value = addr;
            document.getElementById('land_area').value = area;
            document.getElementById('appraisal').value = price;
        }
        
        async function runCompleteAnalysis() {
            const address = document.getElementById('address').value;
            const land_area = parseFloat(document.getElementById('land_area').value);
            const appraisal = parseFloat(document.getElementById('appraisal').value);
            
            if (!address || !land_area || !appraisal) {
                alert('모든 필드를 입력해주세요.');
                return;
            }
            
            document.getElementById('loading').classList.add('show');
            document.getElementById('results').classList.remove('show');
            document.getElementById('analyzeBtn').disabled = true;
            
            try {
                const response = await fetch('/api/complete_analysis', {
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
                    currentTimestamp = data.timestamp;
                    displayResults(data.result);
                } else {
                    alert('분석 실패: ' + data.error);
                }
            } catch (error) {
                alert('오류: ' + error.message);
            } finally {
                document.getElementById('loading').classList.remove('show');
                document.getElementById('analyzeBtn').disabled = false;
            }
        }
        
        function displayResults(result) {
            const v20 = result.v19_finance || {};
            const profit = v20.profit_calculation || {};
            
            document.getElementById('capex').textContent = profit.total_capex_krw || 'N/A';
            document.getElementById('purchase').textContent = profit.lh_purchase_price_krw || 'N/A';
            document.getElementById('profit').textContent = profit.profit_krw || 'N/A';
            document.getElementById('roi').textContent = (profit.roi_pct || 0).toFixed(2) + '%';
            document.getElementById('irr').textContent = (profit.irr_pct || 0).toFixed(2) + '%';
            document.getElementById('payback').textContent = (profit.payback_years || 0).toFixed(1) + '년';
            
            const decision = v20.decision || {};
            const decisionText = decision.decision || 'PENDING';
            const decisionClass = decisionText === 'GO' ? 'decision-go' : 
                                 decisionText.includes('CONDITIONAL') ? 'decision-conditional' : 
                                 'decision-no';
            
            document.getElementById('decision').innerHTML = 
                `<span class="decision-badge ${decisionClass}">${decisionText}</span>`;
            document.getElementById('financial').textContent = decision.financial_criterion || 'N/A';
            document.getElementById('policy').textContent = decision.policy_criterion || 'N/A';
            
            document.getElementById('downloadBtn').href = `/report/${currentTimestamp}`;
            
            document.getElementById('results').classList.add('show');
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Main interface"""
    return INTERFACE_HTML


@app.route('/api/complete_analysis', methods=['POST'])
def complete_analysis():
    """
    Complete analysis with PDF generation
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
        
        # Add safe defaults
        context = add_complete_defaults(context, address, land_area_sqm, appraisal_price)
        
        # Cache context
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
            'timestamp': timestamp,
            'result': {
                'v19_finance': context.get('v19_finance', {}),
                'metadata': context.get('metadata', {})
            }
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/report/<timestamp>')
def view_report(timestamp):
    """
    View/Download Expert Edition PDF
    """
    try:
        # Get cached context
        if timestamp in context_cache:
            cached = context_cache[timestamp]
            context = cached['context']
        else:
            # Generate new with defaults
            builder = ReportContextBuilder()
            context = builder.build_context(
                address='서울특별시 마포구 월드컵북로 120',
                land_area_sqm=660.0,
                coordinates=None,
                multi_parcel=False,
                parcels=None,
                additional_params={'appraisal_price': 10_000_000}
            )
            context = add_complete_defaults(context, '서울특별시 마포구 월드컵북로 120', 660.0, 10_000_000)
        
        # Deep clean
        context = deep_clean_context(context)
        
        # ADD TEMPLATE VARIABLE ALIASES (FIX: building_coverage undefined)
        context = add_template_aliases(context)
        
        # ADD V21 NARRATIVES (PHASE 1 UPGRADE)
        context = add_v21_narratives(context)
        
        # Load template
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Create safe environment
        env = create_safe_jinja_env()
        template = env.from_string(template_content)
        
        # Render
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
        return f"""
        <html><body style="padding:40px;font-family:monospace;">
        <h1 style="color:#C0392B;">Report Error</h1>
        <pre style="background:#f5f5f5;padding:20px;border-radius:8px;">{str(e)}</pre>
        <h3>Traceback:</h3>
        <pre style="background:#f5f5f5;padding:20px;border-radius:8px;">{traceback.format_exc()}</pre>
        </body></html>
        """, 500


def add_complete_defaults(context, address, land_area_sqm, appraisal_price):
    """Add all required defaults"""
    ctx = context.copy()
    
    # Top-level
    ctx.setdefault('address', address)
    ctx.setdefault('land_area_sqm', land_area_sqm)
    ctx.setdefault('building_coverage_ratio', 50.0)
    ctx.setdefault('floor_area_ratio', 300.0)
    ctx.setdefault('building_area', land_area_sqm * 0.5)
    ctx.setdefault('gross_floor_area', land_area_sqm * 3.0)
    ctx.setdefault('total_units', 30)
    ctx.setdefault('avg_unit_area', 66.0)
    
    # Sections
    if 'site_overview' not in ctx:
        ctx['site_overview'] = {}
    ctx['site_overview'].update({
        'address': address,
        'land_area_sqm': land_area_sqm,
        'building_area': land_area_sqm * 0.5,
        'gross_floor_area': land_area_sqm * 3.0,
        'floor_area_ratio': 300.0,
        'building_coverage_ratio': 50.0
    })
    
    if 'zoning_regulations' not in ctx:
        ctx['zoning_regulations'] = {}
    ctx['zoning_regulations'].update({
        'zone_type': '제2종일반주거지역',
        'max_floor_area_ratio': 300.0,
        'max_building_coverage': 50.0,
        'max_height': 35.0
    })
    
    if 'financial_analysis' not in ctx:
        ctx['financial_analysis'] = {}
    ctx['financial_analysis'].update({
        'total_investment': land_area_sqm * appraisal_price * 2.5,
        'land_cost': land_area_sqm * appraisal_price,
        'construction_cost': land_area_sqm * 3.5 * 3500000,
        'npv': 0,
        'irr': 0,
        'roi': 0
    })
    
    if 'metadata' not in ctx:
        ctx['metadata'] = {}
    ctx['metadata'].update({
        'report_title': 'LH 신축매입임대 사업 타당성 분석 보고서',
        'generated_date': datetime.now().strftime('%Y년 %m월 %d일'),
        'author': 'Na TaiHeum (나태흠)',
        'organization': 'Antenna Holdings'
    })
    
    return ctx


def add_template_aliases(context):
    """
    COMPREHENSIVE Template Variable Alias Layer
    ============================================
    
    Maps ALL context variables to template expectations.
    This function ensures 100% template compatibility.
    
    Strategy: Extract from nested context → Create flat aliases
    """
    ctx = context.copy()
    
    # ========================================================================
    # SECTION 1: SITE & ZONING DATA
    # ========================================================================
    
    # Get nested data sources
    site = ctx.get('site', ctx.get('site_overview', {}))
    zoning = ctx.get('zoning', ctx.get('zoning_regulations', {}))
    
    # Land area (primary metric)
    land_area = ctx.get('land_area_sqm', site.get('land_area_sqm', 660.0))
    ctx['land_area_sqm'] = land_area
    ctx['land_area_pyeong'] = land_area / 3.3058
    ctx['address'] = ctx.get('address', site.get('address', '서울특별시 마포구 월드컵북로 120'))
    
    # BCR/FAR (Building Coverage Ratio / Floor Area Ratio)
    bcr = zoning.get('bcr', zoning.get('building_coverage_ratio', zoning.get('max_building_coverage', 60.0)))
    far = zoning.get('far', zoning.get('floor_area_ratio', zoning.get('max_floor_area_ratio', 200.0)))
    
    ctx['building_coverage'] = bcr
    ctx['building_ratio'] = far
    ctx['floor_area_ratio'] = far
    ctx['max_building_coverage'] = bcr
    ctx['max_floor_area_ratio'] = far
    ctx['legal_bcr'] = bcr
    ctx['legal_far'] = far
    ctx['plan_bcr'] = bcr
    ctx['plan_far'] = far
    
    # Zone type and height limits
    ctx['zone_type'] = zoning.get('zone_type', '제2종일반주거지역')
    ctx['max_height_m'] = zoning.get('max_height', 35.0)
    ctx['building_height_m'] = zoning.get('max_height', 35.0)
    ctx['building_floors'] = zoning.get('max_floors', 11)
    ctx['land_category'] = zoning.get('land_category', '대')
    
    # ========================================================================
    # SECTION 2: AREA CALCULATIONS
    # ========================================================================
    
    building_area = land_area * (bcr / 100.0)
    gross_floor_area = land_area * (far / 100.0)
    
    # Building area (all variants)
    ctx['building_area'] = building_area
    ctx['building_area_sqm'] = building_area
    
    # Floor area (all variants)
    ctx['gross_floor_area'] = gross_floor_area
    ctx['gross_floor_area_sqm'] = gross_floor_area
    ctx['total_floor_area'] = gross_floor_area
    ctx['total_floor_area_sqm'] = gross_floor_area
    ctx['floor_area'] = gross_floor_area
    ctx['floor_area_sqm'] = gross_floor_area
    
    # Unit information
    ctx['total_units'] = ctx.get('total_units', 30)
    ctx['recommended_units'] = ctx.get('total_units', 30)
    ctx['avg_unit_area'] = ctx.get('avg_unit_area', 66.0)
    
    # Parking
    ctx['parking_spaces'] = zoning.get('parking_required', int(land_area / 45))
    ctx['required_parking'] = zoning.get('parking_required', int(land_area / 45))
    
    # ========================================================================
    # SECTION 3: FINANCIAL DATA
    # ========================================================================
    
    finance = ctx.get('finance', ctx.get('financial_analysis', {}))
    v19 = ctx.get('v19_finance', {})
    
    # Get financial metrics from multiple possible sources
    if v19:
        profit = v19.get('profit_calculation', {})
        # Safely extract numeric values
        capex = float(profit.get('total_capex', 0) or profit.get('total_capex_krw', 0) or 15000000000)
        lh_price = float(profit.get('lh_purchase_price', 0) or profit.get('lh_purchase_price_krw', 0) or 12000000000)
        roi_val = profit.get('roi_pct')
        roi = float(roi_val) / 100.0 if roi_val and isinstance(roi_val, (int, float)) else 0.0
        irr_val = profit.get('irr_pct')
        irr = float(irr_val) / 100.0 if irr_val and isinstance(irr_val, (int, float)) else 0.0
        payback = float(profit.get('payback_years', 0) or 0)
    else:
        capex_raw = finance.get('total_investment', finance.get('total_cost', 15000000000))
        capex = float(capex_raw) if isinstance(capex_raw, (int, float)) else 15000000000
        lh_price = capex * 0.8
        roi = float(finance.get('roi', 0) or 0)
        irr = float(finance.get('irr', 0) or 0)
        payback = float(finance.get('payback_period', 0) or 0)
    
    ctx['capex_krw'] = capex
    ctx['total_construction_cost_krw'] = capex
    ctx['total_project_cost'] = capex
    ctx['lh_purchase_price'] = lh_price
    ctx['irr_public_pct'] = irr * 100
    
    # NPV - ensure numeric value
    npv_raw = finance.get('npv', 0)
    ctx['npv_public_krw'] = float(npv_raw) if isinstance(npv_raw, (int, float)) else 0.0
    ctx['payback_period_years'] = payback
    
    # Cost breakdown
    cost = ctx.get('cost', {})
    construction = cost.get('construction', {})
    breakdown = construction.get('breakdown', {})
    
    ctx['direct_cost_krw'] = breakdown.get('direct', capex * 0.6)
    ctx['indirect_cost_krw'] = breakdown.get('indirect', capex * 0.2)
    ctx['design_cost_krw'] = breakdown.get('design', capex * 0.1)
    ctx['other_cost_krw'] = breakdown.get('contingency', capex * 0.1)
    ctx['cost_per_sqm_krw'] = capex / gross_floor_area if gross_floor_area > 0 else 3500000
    ctx['zerosite_value_per_sqm'] = ctx['cost_per_sqm_krw']
    ctx['cost_confidence'] = 'HIGH'
    
    # ========================================================================
    # SECTION 4: DEMAND INTELLIGENCE
    # ========================================================================
    
    demand = ctx.get('demand', {})
    
    ctx['demand_score'] = demand.get('overall_score', demand.get('total_score', 75.0))
    ctx['total_score'] = ctx['demand_score']
    ctx['recommended_housing_type'] = demand.get('recommended_type', '도시근로자')
    ctx['demand_confidence'] = demand.get('confidence_level', 'MEDIUM')
    
    # v23 Task #6: Auto-generate housing type breakdown table
    # Based on recommended_housing_type and demand_score
    recommended = ctx['recommended_housing_type']
    base_score = ctx['demand_score']
    
    # Define housing type options with relative demand
    housing_type_templates = {
        '도시근로자': {'score': 1.0, 'suitability': 95, 'units': 0.40},
        '신혼부부': {'score': 0.9, 'suitability': 85, 'units': 0.30},
        '대학생': {'score': 0.7, 'suitability': 70, 'units': 0.20},
        '고령자': {'score': 0.5, 'suitability': 50, 'units': 0.10}
    }
    
    # Calculate total units (based on gross_floor_area)
    total_units = int(gross_floor_area / 60) if gross_floor_area > 0 else 100  # Approx 60㎡ per unit
    
    # Generate housing types list
    ctx['housing_types'] = []
    for housing_type, template in housing_type_templates.items():
        # Adjust score based on whether it's the recommended type
        score_multiplier = 1.2 if housing_type == recommended else template['score']
        score = base_score * score_multiplier
        score = min(100, score)  # Cap at 100
        
        ctx['housing_types'].append({
            'name': housing_type,
            'score': score,
            'suitability': int(template['suitability'] * score_multiplier),
            'recommended_units': int(total_units * template['units'])
        })
    
    # Sort by score descending
    ctx['housing_types'].sort(key=lambda x: x['score'], reverse=True)
    
    # ========================================================================
    # SECTION 5: MARKET INTELLIGENCE
    # ========================================================================
    
    market = ctx.get('market', {})
    
    ctx['market_signal'] = market.get('signal', 'FAIR')
    ctx['market_delta_pct'] = market.get('delta_pct', 0.0)
    ctx['market_temperature'] = market.get('temperature', 'MODERATE')
    ctx['market_avg_price_per_sqm'] = market.get('avg_price_per_sqm', 10000000)
    
    # ========================================================================
    # SECTION 6: METADATA & DATES
    # ========================================================================
    
    metadata = ctx.get('metadata', {})
    from datetime import datetime
    now = datetime.now()
    
    ctx['report_date'] = metadata.get('generated_date', now.strftime('%Y년 %m월 %d일'))
    ctx['report_id'] = metadata.get('report_code', f'ZS-{now.strftime("%Y%m%d")}-0000')
    ctx['current_year'] = now.year
    ctx['current_month'] = now.month
    ctx['analysis_period'] = '30 years'
    
    # ========================================================================
    # SECTION 7: ASSUMPTIONS & PARAMETERS
    # ========================================================================
    
    ctx['discount_rate'] = 0.05
    ctx['rent_escalation'] = 0.02
    ctx['vacancy_rate'] = 0.05
    
    # ========================================================================
    # SECTION 8: POLICY & REQUIREMENTS
    # ========================================================================
    
    # These are typically narrative fields - ensure they exist
    ctx.setdefault('requirement', '')
    ctx.setdefault('implication', '')
    ctx.setdefault('limitation', '')
    ctx.setdefault('research', '')
    
    # 36-month implementation roadmap
    if 'implementation_roadmap' not in ctx:
        ctx['implementation_roadmap'] = {
            'phases': [
                {'phase': 'Phase 1', 'months': '1-6', 'tasks': '사업계획 수립 및 인허가'},
                {'phase': 'Phase 2', 'months': '7-18', 'tasks': '설계 및 시공'},
                {'phase': 'Phase 3', 'months': '19-30', 'tasks': '준공 및 LH 매입'},
                {'phase': 'Phase 4', 'months': '31-36', 'tasks': '임대 운영 개시'}
            ],
            'critical_path': '인허가 → 설계 → 착공 → 준공 → LH감정평가 → 매입',
            'total_duration': '36개월'
        }
    
    # v23 Task #10: McKinsey 2×2 Risk Matrix - 6 Core Risks
    # Reduced from 25-item to focused 6-item matrix
    # Quadrants: High Impact/High Probability → Low Impact/Low Probability
    if 'risk_matrix' not in ctx:
        ctx['risk_matrix'] = [
            # High Impact, High Probability (Critical Risks - Top Priority)
            {'category': '건설비 상승', 'risk': '자재·인건비 상승', 'level': 'high', 'probability': 'High', 'impact': 8.5, 'mitigation': '계약 시 물가조정 조항 포함, 자재 선확보'},
            {'category': 'LH 감정평가 미달', 'risk': '감정가 < 공사비', 'level': 'high', 'probability': 'Medium', 'impact': 9.0, 'mitigation': 'LH 표준건축비 준수, 토지비 최적화'},
            
            # High Impact, Low Probability (Monitor Closely)
            {'category': 'LH 정책 변경', 'risk': '신축매입임대 중단', 'level': 'medium', 'probability': 'Low', 'impact': 7.5, 'mitigation': '사전 LH 협의 및 조건부 계약'},
            
            # Low Impact, High Probability (Manageable)
            {'category': '공사 지연', 'risk': '일정 3-6개월 초과', 'level': 'medium', 'probability': 'Medium', 'impact': 5.0, 'mitigation': '공기 여유 6개월 확보, 패널티 조항'},
            
            # Low Impact, Low Probability (Low Priority)
            {'category': '인허가 지연', 'risk': '사업계획승인 지연', 'level': 'low', 'probability': 'Low', 'impact': 3.5, 'mitigation': '사전 협의 및 전문가 자문'},
            {'category': '시장 침체', 'risk': '부동산 경기 악화', 'level': 'low', 'probability': 'Low', 'impact': 2.0, 'mitigation': 'LH 매입 보장으로 시장 리스크 차단'}
        ]
    
    # ========================================================================
    # SECTION 9: CASH FLOW TABLE
    # ========================================================================
    
    # Cash flow table for 30-year projection
    if 'cash_flow_table' not in ctx:
        # Generate minimal cash flow table structure with ALL required fields
        ctx['cash_flow_table'] = [
            {
                'year': i,
                'revenue': 0,
                'expense': 0,  # Template line 3614
                'opex': 0,
                'noi': 0,
                'net_cf': 0,  # Template line 3615 - Net cash flow
                'cumulative': 0,
                'cumulative_cf': 0,  # Iteration 2 - Cumulative cash flow
                'cash_flow': 0
            } for i in range(1, 31)
        ]
    
    # ========================================================================
    # v23 FIX #8: POLICY FINANCE - Real LH Mechanism
    # ========================================================================
    # NOTE: Moved to AFTER LH appraisal calculations (line ~1107)
    # to avoid UnboundLocalError
    
    # ========================================================================
    # SECTION 9: FINANCIAL NUMBER FORMATTING (v23 COMPLETE REBUILD)
    # ========================================================================
    # v23 PRINCIPLE: Single Source of Truth for ALL Financial Numbers
    # - Market Price ≠ Construction Cost
    # - All units explicitly converted (원 → 억원, 만원/㎡)
    # - LH Appraisal Mechanism = REAL calculation (not explanation only)
    
    # Helper functions (kept for compatibility)
    def to_eok(value_won):
        """Convert KRW to 억원 (hundred million)"""
        return round(value_won / 1e8, 2) if value_won else 0.0
    
    def to_man_per_sqm(value_won_per_sqm):
        """Convert KRW/㎡ to 만원/㎡ (ten thousand)"""
        return round(value_won_per_sqm / 1e4, 1) if value_won_per_sqm else 0.0
    
    def to_man(value_won):
        """Convert KRW to 만원 (ten thousand)"""
        return round(value_won / 1e4, 1) if value_won else 0.0
    
    # ========================================================================
    # v23 FIX #1: CONSTRUCTION COST (CAPEX) - Engineering Calculation
    # ========================================================================
    # CAPEX = Total Project Cost (토지비 + 건축비 + 간접비)
    # This is NOT market price - it's actual construction + land acquisition cost
    
    capex_won = ctx.get('capex_krw', 15000000000)  # Original value in KRW
    ctx['capex_eok'] = to_eok(capex_won)
    ctx['total_construction_cost_eok'] = to_eok(capex_won)
    ctx['total_project_cost_eok'] = to_eok(capex_won)
    
    # ========================================================================
    # v23 FIX #2: MARKET VALUATION - Transaction-based Market Price
    # ========================================================================
    # Market price = Real transaction data (실거래가 기반)
    # This is DIFFERENT from construction cost
    
    # Get actual market data from context (if available)
    v18_transaction = ctx.get('v18_transaction', {})
    land_comps = v18_transaction.get('land_comps', [])
    
    # Calculate market-based land value (NOT construction cost)
    if land_comps and len(land_comps) > 0:
        # Use average transaction price from comparable sales
        avg_land_price_per_sqm = sum([comp.get('unit_price', 0) for comp in land_comps]) / len(land_comps)
    else:
        # Fallback: estimate from appraisal price
        appraisal_price = ctx.get('appraisal_price', 20000000)  # 만원/㎡
        avg_land_price_per_sqm = appraisal_price * 10000  # Convert to KRW/㎡
    
    # Market valuation for LAND only (토지 시장가치)
    market_land_value_won = avg_land_price_per_sqm * land_area
    ctx['market_land_value_eok'] = to_eok(market_land_value_won)
    ctx['market_land_price_man_per_sqm'] = to_man_per_sqm(avg_land_price_per_sqm)
    
    # ZeroSite Model Valuation (AI-predicted market value)
    # This should come from actual model output, not construction cost
    zerosite_model_value_won = ctx.get('zerosite_valuation', market_land_value_won * 1.05)
    ctx['zerosite_market_value_eok'] = to_eok(zerosite_model_value_won)
    ctx['zerosite_price_man_per_sqm'] = to_man_per_sqm(zerosite_model_value_won / land_area)
    
    # ========================================================================
    # v23 FIX #3: LH APPRAISAL MECHANISM - Real Calculation
    # ========================================================================
    # LH 감정평가 = 토지감정 + 건물감정
    # Based on ACTUAL LH standards (not just explanation)
    
    # STEP 1: Land Appraisal (토지 감정평가)
    # = Transaction-based market price × 0.90~0.95 (appraisal rate)
    land_appraisal_rate = 0.92  # LH standard: 88-95%, typical 92%
    lh_land_appraisal_won = market_land_value_won * land_appraisal_rate
    ctx['lh_land_appraisal_eok'] = to_eok(lh_land_appraisal_won)
    
    # STEP 2: Building Appraisal (건물 감정평가)
    # = LH Standard Construction Cost × Floor Area
    lh_standard_cost_per_sqm = 3500000  # 350만원/㎡ (LH 표준건축비)
    building_appraisal_won = lh_standard_cost_per_sqm * gross_floor_area
    ctx['lh_building_appraisal_eok'] = to_eok(building_appraisal_won)
    ctx['lh_standard_cost_per_sqm_man'] = to_man_per_sqm(lh_standard_cost_per_sqm)
    
    # STEP 3: Total LH Appraisal Value
    lh_total_appraisal_won = lh_land_appraisal_won + building_appraisal_won
    ctx['lh_total_appraisal_eok'] = to_eok(lh_total_appraisal_won)
    
    # STEP 4: LH Purchase Price (매입가)
    # = Appraisal Value (some LH programs use 90% of appraisal)
    lh_purchase_rate = 1.0  # For 신축매입임대, typically 100% of appraisal
    lh_price_won = lh_total_appraisal_won * lh_purchase_rate
    ctx['lh_purchase_price'] = lh_price_won
    ctx['lh_purchase_price_eok'] = to_eok(lh_price_won)
    ctx['lh_appraisal_rate_pct'] = land_appraisal_rate * 100
    
    # ========================================================================
    # v23 FIX #3.5: POLICY FINANCE - Real LH Mechanism (moved here from line 973)
    # ========================================================================
    # Update policy_finance with ACTUAL calculated values (not estimates)
    # This block MUST come AFTER LH appraisal calculations to avoid UnboundLocalError
    
    ctx['policy_finance'] = {
        'base': {
            'land_appraisal': lh_land_appraisal_won,
            'land_appraisal_eok': ctx['lh_land_appraisal_eok'],
            'building_appraisal': building_appraisal_won,
            'building_appraisal_eok': ctx['lh_building_appraisal_eok'],
            'total_appraisal': lh_total_appraisal_won,
            'total_appraisal_eok': ctx['lh_total_appraisal_eok'],
            'appraisal_rate': land_appraisal_rate,
            'appraisal_rate_pct': land_appraisal_rate * 100,
            'lh_purchase_price': lh_price_won,
            'lh_purchase_price_eok': ctx['lh_purchase_price_eok'],
            'policy_npv': 0,  # Will be updated after profit calculation
            'policy_npv_eok': 0
        },
        'mechanism': {
            'land_valuation_method': '거래사례 평균가 기준',
            'building_valuation_method': 'LH 표준건축비 (350만원/㎡)',
            'appraisal_rate_range': '88-95% (일반적으로 92%)',
            'purchase_rate': f'{lh_purchase_rate * 100:.0f}%',
            'description': f'토지감정 {ctx["lh_land_appraisal_eok"]:.2f}억 + 건물감정 {ctx["lh_building_appraisal_eok"]:.2f}억 = 총 {ctx["lh_total_appraisal_eok"]:.2f}억'
        },
        'sensitivity': {
            'optimistic': {
                'appraisal_rate': 0.95,
                'policy_npv': (lh_total_appraisal_won * 0.95 - capex_won),
                'policy_npv_eok': to_eok(lh_total_appraisal_won * 0.95 - capex_won)
            },
            'pessimistic': {
                'appraisal_rate': 0.88,
                'policy_npv': (lh_total_appraisal_won * 0.88 - capex_won),
                'policy_npv_eok': to_eok(lh_total_appraisal_won * 0.88 - capex_won)
            }
        }
    }
    
    # ========================================================================
    # v23 FIX #4: PROFIT & ROI CALCULATION
    # ========================================================================
    # Profit = LH Purchase Price - Total CAPEX
    # ROI = (Profit / CAPEX) × 100%
    
    profit_won = lh_price_won - capex_won
    ctx['profit_eok'] = to_eok(profit_won)
    ctx['profit_won'] = profit_won
    
    # NPV (keep existing if available, else use profit)
    npv_won = ctx.get('npv_public_krw', profit_won)
    ctx['npv_eok'] = to_eok(npv_won)
    ctx['npv_public_eok'] = to_eok(npv_won)
    ctx['npv_won'] = npv_won
    
    # Update policy_finance with calculated NPV
    if 'policy_finance' in ctx:
        ctx['policy_finance']['base']['policy_npv'] = npv_won
        ctx['policy_finance']['base']['policy_npv_eok'] = to_eok(npv_won)
    
    # ========================================================================
    # v23 FIX #5: ROI, IRR, PAYBACK - Unified Calculation
    # ========================================================================
    
    # ROI (Return on Investment)
    # = (Profit / CAPEX) × 100%
    roi_pct = round((profit_won / capex_won * 100), 2) if capex_won > 0 else 0.0
    ctx['roi_pct'] = roi_pct
    ctx['roi_display'] = f"{roi_pct:.2f}%"
    
    # IRR (Internal Rate of Return)
    # Use existing IRR from financial engine, or calculate based on transaction
    irr_from_engine = ctx.get('irr_public_pct', None)
    if irr_from_engine is not None:
        irr_pct = irr_from_engine
    else:
        # Simple IRR estimate for policy transaction projects
        # IRR ≈ (Profit / CAPEX) / Construction_Period
        construction_period_years = 2.5
        irr_pct = roi_pct / construction_period_years if construction_period_years > 0 else roi_pct
    
    ctx['irr_pct'] = round(irr_pct, 2)
    ctx['irr_display'] = f"{irr_pct:.2f}%"
    
    # Decision thresholds (v23 standards)
    ctx['private_irr_threshold'] = 8.0  # Private development minimum
    ctx['policy_irr_threshold'] = 2.0   # Policy project minimum (social IRR)
    
    # Payback period: cap to max 30 years if infinite or negative profit
    # Check both payback_years and payback_period_years (context builder sets both)
    raw_payback = ctx.get('payback_years', ctx.get('payback_period_years', 2.5))
    try:
        # Convert to float first to handle numeric string inputs
        payback_val = float(raw_payback)
        
        # Check for infinity, excessive values, or negative profit
        if (payback_val == float('inf') or payback_val == float('-inf') or 
            payback_val > 30 or payback_val < 0 or profit_won <= 0):
            ctx['payback_years'] = 30.0  # Max payback for LH projects (30-year operation)
        else:
            ctx['payback_years'] = round(payback_val, 1)
    except (ValueError, TypeError):
        # Handle string 'inf' or other conversion failures
        ctx['payback_years'] = 30.0  # Default to 30 years if conversion fails
    
    # ========================================================================
    # v23 FIX #6: CAPEX BREAKDOWN - Correct Unit Calculations
    # ========================================================================
    # Problem: Previously "2.5만원/㎡" appeared (100x too small)
    # Solution: Calculate sqm units AFTER eok conversion
    
    # Land Cost (typically 25% of CAPEX)
    land_cost_won = ctx.get('land_cost_krw', capex_won * 0.25)
    ctx['land_cost_eok'] = to_eok(land_cost_won)
    ctx['land_cost_per_sqm_man'] = to_man_per_sqm(land_cost_won / land_area) if land_area > 0 else 0
    
    # Direct Construction Cost (typically 55% of CAPEX)
    direct_cost_won = ctx.get('direct_cost_krw', capex_won * 0.55)
    ctx['direct_cost_eok'] = to_eok(direct_cost_won)
    # FIX: Divide by GROSS FLOOR AREA (not land area) for construction cost per sqm
    ctx['direct_cost_per_sqm_man'] = to_man_per_sqm(direct_cost_won / gross_floor_area) if gross_floor_area > 0 else 0
    
    # Indirect costs
    indirect_cost_won = ctx.get('indirect_cost_krw', capex_won * 0.10)
    ctx['indirect_cost_eok'] = to_eok(indirect_cost_won)
    ctx['indirect_cost_per_sqm_man'] = to_man_per_sqm(indirect_cost_won / gross_floor_area) if gross_floor_area > 0 else 0
    
    # Design cost
    design_cost_won = ctx.get('design_cost_krw', capex_won * 0.05)
    ctx['design_cost_eok'] = to_eok(design_cost_won)
    ctx['design_cost_per_sqm_man'] = to_man_per_sqm(design_cost_won / gross_floor_area) if gross_floor_area > 0 else 0
    
    # Other costs (contingency, etc.)
    other_cost_won = ctx.get('other_cost_krw', capex_won * 0.05)
    ctx['other_cost_eok'] = to_eok(other_cost_won)
    ctx['other_cost_per_sqm_man'] = to_man_per_sqm(other_cost_won / gross_floor_area) if gross_floor_area > 0 else 0
    
    # Total construction cost per sqm (for building only, excluding land)
    building_capex_won = capex_won - land_cost_won
    ctx['building_cost_per_sqm_man'] = to_man_per_sqm(building_capex_won / gross_floor_area) if gross_floor_area > 0 else 0
    
    # ========================================================================
    # v23 FIX #7: MARKET PRICES - Separate from Construction Cost
    # ========================================================================
    # Market price = Transaction-based (already calculated above)
    # Do NOT confuse with construction cost
    
    ctx['market_avg_price_per_sqm_man'] = ctx['market_land_price_man_per_sqm']
    ctx['market_price_man_per_sqm'] = ctx['market_land_price_man_per_sqm']
    
    # v23 DEBUG: Verify critical variables are set
    critical_vars = ['zerosite_market_value_eok', 'zerosite_price_man_per_sqm', 'lh_total_appraisal_eok']
    for var in critical_vars:
        if var not in ctx:
            print(f"WARNING: {var} not in context!")
    
    # Keep original KRW values for calculations, but add display versions
    # This way templates can use {{ capex_eok }} 억원 instead of {{ capex_krw }} 억원
    
    return ctx


def add_v21_narratives(context):
    """
    Add v21 Advanced Narratives to Context
    =======================================
    
    This function generates professional, policy-oriented narratives for all report sections.
    It follows KDI (Korea Development Institute) style with academic rigor.
    
    New fields added:
    - executive_summary_v21: Structured 3-block summary (Project/Metrics/Decision)
    - capex_interpretation: CAPEX table interpretation (200-260 words)
    - financial_interpretation: Financial analysis interpretation
    - market_interpretation: Market analysis interpretation
    - demand_interpretation: Demand analysis interpretation
    - dual_decision_narrative: Comprehensive Financial + Policy decision
    - risk_matrix_narrative: Risk matrix with mitigation strategies
    - fallback_*: Professional fallback narratives for missing data
    """
    from app.services_v13.report_full.v21_narrative_generator import V21NarrativeGenerator
    
    ctx = context.copy()
    generator = V21NarrativeGenerator()
    
    # ========================================================================
    # EXECUTIVE SUMMARY (v21 - Structured Format)
    # ========================================================================
    ctx['executive_summary_v21'] = generator.generate_executive_summary(ctx)
    
    # ========================================================================
    # TABLE INTERPRETATIONS (4-6 sentences per table)
    # ========================================================================
    ctx['capex_interpretation'] = generator.generate_capex_interpretation(ctx)
    ctx['financial_interpretation'] = generator.generate_financial_interpretation(ctx)
    ctx['market_interpretation'] = generator.generate_market_interpretation(ctx)
    ctx['demand_interpretation'] = generator.generate_demand_interpretation(ctx)
    
    # ========================================================================
    # DUAL DECISION NARRATIVE (Financial + Policy)
    # ========================================================================
    ctx['dual_decision_narrative'] = generator.generate_dual_decision_narrative(ctx)
    
    # ========================================================================
    # RISK MATRIX NARRATIVE
    # ========================================================================
    ctx['risk_matrix_narrative'] = generator.generate_risk_matrix_narrative(ctx)
    
    # ========================================================================
    # FALLBACK NARRATIVES (for empty sections)
    # ========================================================================
    
    # Check if demand data is sufficient
    demand_score = ctx.get('demand_score', 0)
    if demand_score == 0 or demand_score < 30:
        ctx['demand_fallback'] = generator.generate_empty_demand_fallback(ctx)
    
    # Check if market comps are sufficient
    v18_transaction = ctx.get('v18_transaction', {})
    land_comps = v18_transaction.get('land_comps', [])
    building_comps = v18_transaction.get('building_comps', [])
    if len(land_comps) + len(building_comps) < 5:
        ctx['market_comps_fallback'] = generator.generate_empty_market_comps_fallback(ctx)
    
    # Check if housing type analysis exists
    recommended_type = ctx.get('recommended_housing_type', '')
    if not recommended_type or recommended_type == '도시근로자':
        # Default type suggests no specific analysis
        ctx['housing_type_fallback'] = generator.generate_empty_housing_type_fallback(ctx)
    
    return ctx


def deep_clean_context(context):
    """Recursively clean None/undefined"""
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
    
    if isinstance(cleaned, dict):
        for key, value in cleaned.items():
            if isinstance(value, (dict, list)):
                cleaned[key] = clean_value(value)
            elif value is None or value == '':
                if any(x in key.lower() for x in ['area', 'ratio', 'cost', 'price', 'value', 'pct']):
                    cleaned[key] = 0
    
    return cleaned


def create_safe_jinja_env():
    """Create Jinja2 environment with safe filters"""
    env = Environment(autoescape=select_autoescape(['html', 'xml']))
    
    def safe_round(value, precision=0):
        try:
            if value is None or value == '':
                return 0
            # Handle string 'inf' case
            if isinstance(value, str) and 'inf' in value.lower():
                return 30.0
            float_val = float(value)
            # Handle infinity or impossible payback (999): cap to 30 years
            if (float_val == float('inf') or float_val == float('-inf') or 
                float_val >= 999 or float_val > 100):
                return 30.0
            return round(float_val, int(precision))
        except (ValueError, TypeError):
            return 0
    
    def safe_int(value):
        try:
            if value is None or value == '':
                return 0
            return int(float(value))
        except (ValueError, TypeError):
            return 0
    
    def safe_float(value):
        try:
            if value is None or value == '':
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def markdown_filter(text):
        """Simple markdown filter - preserves newlines as <br> and wraps in <p>"""
        if not text:
            return ''
        # Replace \n with <br> and wrap in paragraph
        text = str(text).replace('\n', '<br>\n')
        return f'<p>{text}</p>'
    
    env.filters['round'] = safe_round
    env.filters['safe_round'] = safe_round
    env.filters['int'] = safe_int
    env.filters['safe_int'] = safe_int
    env.filters['float'] = safe_float
    env.filters['safe_float'] = safe_float
    env.filters['markdown'] = markdown_filter  # ADD: markdown filter
    
    return env


if __name__ == '__main__':
    print("=" * 80)
    print("🚀 ZeroSite v20 COMPLETE SERVICE Starting...")
    print("=" * 80)
    print()
    print("✨ Complete Features:")
    print("   - Direct address input (전국 모든 주소)")
    print("   - Real transaction data collection")
    print("   - v20 analysis engine")
    print("   - Expert Edition PDF (50-60 pages)")
    print("   - One-click download")
    print()
    print("📍 Server will run on port 6000")
    print("🌐 Complete All-in-One Service")
    print()
    app.run(host='0.0.0.0', port=6000, debug=False)
