"""
ZeroSite v20 Production Web Service
====================================

Full-featured LH submission report generation service with:
- Direct address input (any Korean address)
- Real-time analysis with v20 engine
- PDF generation and download
- LH-grade report styling

Author: Na TaiHeum (나태흠)
Organization: Antenna Holdings
Version: v20 Production
Date: 2025-12-07
"""

from flask import Flask, render_template_string, request, jsonify, send_file, Response
from app.services_v13.report_full.report_context_builder import ReportContextBuilder
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create reports directory
REPORTS_DIR = Path("/home/user/webapp/generated_reports")
REPORTS_DIR.mkdir(exist_ok=True)

# ============================================================================
# HTML TEMPLATE WITH ADDRESS INPUT + PDF DOWNLOAD
# ============================================================================

PRODUCTION_INTERFACE_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZeroSite v20 - LH 신축매입임대 사업성 분석</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #005BAC 0%, #00325A 100%);
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
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            font-size: 42px;
            font-weight: 900;
            color: #005BAC;
            margin-bottom: 10px;
            letter-spacing: -1px;
        }
        
        .header .subtitle {
            font-size: 18px;
            color: #666;
            margin-bottom: 5px;
        }
        
        .header .author {
            font-size: 14px;
            color: #999;
            margin-top: 10px;
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
            margin-bottom: 30px;
            font-size: 28px;
        }
        
        .form-group {
            margin-bottom: 24px;
        }
        
        .form-group label {
            display: block;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
            font-size: 15px;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 14px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s;
            font-family: inherit;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #005BAC;
            box-shadow: 0 0 0 3px rgba(0, 91, 172, 0.1);
        }
        
        .quick-addresses {
            margin-bottom: 20px;
        }
        
        .quick-addresses p {
            font-size: 13px;
            color: #666;
            margin-bottom: 8px;
        }
        
        .quick-btn {
            display: inline-block;
            padding: 6px 12px;
            background: #f0f0f0;
            border: none;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            margin: 4px;
            transition: all 0.2s;
        }
        
        .quick-btn:hover {
            background: #005BAC;
            color: white;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #005BAC 0%, #00325A 100%);
            color: white;
            border: none;
            padding: 18px 40px;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
            letter-spacing: 0.5px;
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
        
        .btn-download {
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            color: white;
            border: none;
            padding: 16px 32px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
            margin-top: 20px;
            display: none;
        }
        
        .btn-download:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(34, 197, 94, 0.4);
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
        
        .result-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 25px;
            border-left: 6px solid #005BAC;
        }
        
        .result-card h3 {
            color: #005BAC;
            margin-bottom: 20px;
            font-size: 22px;
            display: flex;
            align-items: center;
        }
        
        .result-card h3 .icon {
            font-size: 28px;
            margin-right: 12px;
        }
        
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .metric {
            background: white;
            padding: 16px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        
        .metric-label {
            font-size: 13px;
            font-weight: 600;
            color: #666;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: 900;
            color: #333;
        }
        
        .metric-value.positive {
            color: #22c55e;
        }
        
        .metric-value.negative {
            color: #ef4444;
        }
        
        .decision-badge {
            display: inline-block;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: 700;
            font-size: 16px;
            text-transform: uppercase;
            letter-spacing: 1px;
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
        
        .narrative-box {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-top: 16px;
            border-left: 4px solid #005BAC;
            line-height: 1.7;
            color: #444;
        }
        
        .loading {
            text-align: center;
            padding: 60px 40px;
            display: none;
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
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading p {
            font-size: 16px;
            color: #666;
        }
        
        .v20-badge {
            display: inline-block;
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            margin-left: 10px;
        }
        
        .comps-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
            font-size: 13px;
        }
        
        .comps-table th {
            background: #005BAC;
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: 600;
        }
        
        .comps-table td {
            padding: 10px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .comps-table tr:hover {
            background: #f8f9fa;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ ZeroSite v20 <span class="v20-badge">PRODUCTION</span></h1>
            <div class="subtitle">LH 신축매입임대 사업성 분석 시스템 | 거래사례 기반 CAPEX 산정</div>
            <div class="author">Author: Na TaiHeum (나태흠) | Antenna Holdings | Copyright © 2025</div>
        </div>
        
        <div class="main-content">
            <div class="input-panel">
                <h2>📍 프로젝트 정보</h2>
                
                <div class="quick-addresses">
                    <p><strong>빠른 테스트 주소:</strong></p>
                    <button class="quick-btn" onclick="setAddress('서울특별시 마포구 월드컵북로 120', 660, 10000000)">서울 마포구</button>
                    <button class="quick-btn" onclick="setAddress('서울특별시 강남구 역삼동 123', 500, 15000000)">서울 강남구</button>
                    <button class="quick-btn" onclick="setAddress('경기도 성남시 분당구 정자동 178-1', 700, 8000000)">경기 분당</button>
                    <button class="quick-btn" onclick="setAddress('경기도 고양시 일산동구 장항동 906', 800, 6000000)">경기 일산</button>
                    <button class="quick-btn" onclick="setAddress('인천광역시 남동구 구월동 1470', 750, 7000000)">인천 남동구</button>
                </div>
                
                <div class="form-group">
                    <label>📮 주소 (도로명 또는 지번)</label>
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
                    <small style="color: #999; font-size: 12px; display: block; margin-top: 5px;">
                        * 실거래가가 없을 경우 기준 단가로 사용됩니다
                    </small>
                </div>
                
                <button class="btn-primary" onclick="runAnalysis()" id="analyzeBtn">
                    🚀 분석 시작
                </button>
                
                <button class="btn-download" onclick="downloadPDF()" id="pdfBtn">
                    📄 PDF 리포트 다운로드
                </button>
            </div>
            
            <div>
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p><strong>분석 중입니다...</strong></p>
                    <p style="font-size: 14px; margin-top: 10px;">
                        실거래가 수집 및 v20 엔진 실행 중 (약 5~10초 소요)
                    </p>
                </div>
                
                <div class="results-panel" id="results">
                    <h2>📊 분석 결과</h2>
                    
                    <div class="result-card">
                        <h3><span class="icon">💰</span> 재무 분석</h3>
                        <div class="metric-grid">
                            <div class="metric">
                                <div class="metric-label">총 사업비</div>
                                <div class="metric-value" id="capex">-</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">LH 매입가</div>
                                <div class="metric-value" id="purchase">-</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">예상 수익</div>
                                <div class="metric-value" id="profit">-</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">ROI</div>
                                <div class="metric-value" id="roi">-</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">IRR</div>
                                <div class="metric-value" id="irr">-</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">회수기간</div>
                                <div class="metric-value" id="payback">-</div>
                            </div>
                        </div>
                        
                        <div class="narrative-box" id="financial-narrative">
                            재무 분석 해석이 여기에 표시됩니다.
                        </div>
                    </div>
                    
                    <div class="result-card">
                        <h3><span class="icon">🎯</span> 의사결정</h3>
                        <div style="text-align: center; padding: 20px;">
                            <div style="margin-bottom: 20px;">
                                <strong style="color: #666; font-size: 14px;">최종 판단</strong>
                                <div style="margin-top: 10px;" id="decision">-</div>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
                                <div>
                                    <div style="font-size: 13px; color: #666; margin-bottom: 5px;">재무적 기준</div>
                                    <div style="font-weight: 700; font-size: 18px;" id="financial">-</div>
                                </div>
                                <div>
                                    <div style="font-size: 13px; color: #666; margin-bottom: 5px;">정책적 기준</div>
                                    <div style="font-weight: 700; font-size: 18px;" id="policy">-</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="narrative-box" id="decision-narrative">
                            의사결정 근거가 여기에 표시됩니다.
                        </div>
                    </div>
                    
                    <div class="result-card">
                        <h3><span class="icon">🏘️</span> 실거래가 분석</h3>
                        <div id="comps-info">
                            실거래가 정보가 여기에 표시됩니다.
                        </div>
                    </div>
                    
                    <div class="result-card">
                        <h3><span class="icon">✅</span> v20 시스템 상태</h3>
                        <div id="v20-status" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentReportId = null;
        
        function setAddress(address, area, appraisal) {
            document.getElementById('address').value = address;
            document.getElementById('land_area').value = area;
            document.getElementById('appraisal').value = appraisal;
        }
        
        async function runAnalysis() {
            const address = document.getElementById('address').value;
            const land_area = parseFloat(document.getElementById('land_area').value);
            const appraisal = parseFloat(document.getElementById('appraisal').value);
            
            if (!address || !land_area || !appraisal) {
                alert('모든 필드를 입력해주세요.');
                return;
            }
            
            // Show loading
            document.getElementById('loading').classList.add('show');
            document.getElementById('results').classList.remove('show');
            document.getElementById('pdfBtn').style.display = 'none';
            document.getElementById('analyzeBtn').disabled = true;
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        address: address,
                        land_area_sqm: land_area,
                        appraisal_price: appraisal
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentReportId = data.report_id;
                    displayResults(data.result);
                    document.getElementById('pdfBtn').style.display = 'block';
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
            const v20 = result.v19_finance;
            
            // Financial metrics
            const profit = v20.profit_calculation;
            document.getElementById('capex').textContent = profit.total_capex_krw;
            document.getElementById('purchase').textContent = profit.lh_purchase_price_krw;
            
            const profitValue = profit.profit_krw;
            const profitEl = document.getElementById('profit');
            profitEl.textContent = profitValue;
            profitEl.className = 'metric-value ' + (profit.profit > 0 ? 'positive' : 'negative');
            
            const roiValue = profit.roi_pct.toFixed(2) + '%';
            const roiEl = document.getElementById('roi');
            roiEl.textContent = roiValue;
            roiEl.className = 'metric-value ' + (profit.roi_pct > 0 ? 'positive' : 'negative');
            
            document.getElementById('irr').textContent = profit.irr_pct.toFixed(2) + '%';
            document.getElementById('payback').textContent = profit.payback_years.toFixed(1) + '년';
            
            // Narratives
            if (v20.narratives) {
                document.getElementById('financial-narrative').innerHTML = 
                    v20.narratives.profit_narrative || '재무 분석 해석';
                document.getElementById('decision-narrative').innerHTML = 
                    v20.narratives.decision_narrative || '의사결정 근거';
            }
            
            // Decision
            const decision = v20.decision;
            const decisionClass = decision.decision === 'GO' ? 'decision-go' : 
                                 decision.decision.includes('CONDITIONAL') ? 'decision-conditional' : 
                                 'decision-no';
            
            document.getElementById('decision').innerHTML = 
                `<span class="decision-badge ${decisionClass}">${decision.decision}</span>`;
            document.getElementById('financial').textContent = decision.financial_criterion;
            document.getElementById('policy').textContent = decision.policy_criterion;
            
            // Comps info
            const compsInfo = v20.transaction_comps || {};
            let compsHtml = '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">';
            compsHtml += `
                <div>
                    <strong>토지 실거래:</strong> ${compsInfo.land_count || 0}건<br>
                    <small style="color: #666;">평균 단가: ${compsInfo.avg_land_price || 'N/A'}</small>
                </div>
                <div>
                    <strong>건물 실거래:</strong> ${compsInfo.building_count || 0}건<br>
                    <small style="color: #666;">평균 단가: ${compsInfo.avg_building_price || 'N/A'}</small>
                </div>
            `;
            compsHtml += '</div>';
            
            if (!compsInfo.land_count && !compsInfo.building_count) {
                compsHtml += '<div class="narrative-box" style="margin-top: 16px;">⚠️ 실거래가 데이터가 부재하여, 입력된 감정평가 단가를 기준으로 분석하였습니다.</div>';
            }
            
            document.getElementById('comps-info').innerHTML = compsHtml;
            
            // v20 Status
            const status = v20.v20_status || {};
            let statusHtml = '';
            for (const [key, value] of Object.entries(status)) {
                const icon = value ? '✅' : '❌';
                const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                statusHtml += `
                    <div style="background: white; padding: 12px; border-radius: 8px; font-size: 13px;">
                        ${icon} <strong>${label}</strong>
                    </div>
                `;
            }
            document.getElementById('v20-status').innerHTML = statusHtml;
            
            // Show results
            document.getElementById('results').classList.add('show');
            document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        function downloadPDF() {
            if (!currentReportId) {
                alert('분석을 먼저 실행해주세요.');
                return;
            }
            
            window.open(`/api/report/${currentReportId}/pdf`, '_blank');
        }
    </script>
</body>
</html>
"""


# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main production interface"""
    return render_template_string(PRODUCTION_INTERFACE_HTML)


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Full analysis endpoint with v20 engine
    
    Request:
        {
            "address": "서울특별시 마포구 월드컵북로 120",
            "land_area_sqm": 660.0,
            "appraisal_price": 10000000
        }
    
    Response:
        {
            "success": true,
            "report_id": "20251207_143022_abc123",
            "result": { v19_finance context }
        }
    """
    try:
        data = request.json
        
        address = data.get('address', '서울특별시 마포구 월드컵북로 120')
        land_area_sqm = data.get('land_area_sqm', 660.0)
        appraisal_price = data.get('appraisal_price', 10_000_000)
        
        # Build context with v20 engine
        builder = ReportContextBuilder()
        context = builder.build_context(
            address=address,
            land_area_sqm=land_area_sqm,
            coordinates=None,
            multi_parcel=False,
            parcels=None,
            additional_params={'appraisal_price': appraisal_price}
        )
        
        # Generate report ID
        report_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save context for PDF generation
        context_file = REPORTS_DIR / f"{report_id}_context.json"
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump({
                'address': address,
                'land_area_sqm': land_area_sqm,
                'appraisal_price': appraisal_price,
                'context': context
            }, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'report_id': report_id,
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


@app.route('/api/report/<report_id>/pdf')
def generate_pdf(report_id):
    """
    Generate PDF report from saved context
    
    This creates a simple HTML-based PDF for now.
    Full LH-grade PDF with WeasyPrint can be added later.
    """
    try:
        # Load saved context
        context_file = REPORTS_DIR / f"{report_id}_context.json"
        if not context_file.exists():
            return jsonify({'error': 'Report not found'}), 404
        
        with open(context_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        context = data['context']
        v20 = context.get('v19_finance', {})
        
        # Generate simple HTML report
        html = generate_report_html(data['address'], data['land_area_sqm'], 
                                    data['appraisal_price'], v20)
        
        # For now, return HTML (can be printed to PDF by browser)
        # Later: use WeasyPrint for server-side PDF generation
        
        return Response(
            html,
            mimetype='text/html',
            headers={
                'Content-Disposition': f'inline; filename=zerosite_v20_report_{report_id}.html'
            }
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generate_report_html(address, land_area, appraisal, v20_data):
    """
    Generate LH-grade HTML report
    
    This can be printed to PDF by browser or converted server-side with WeasyPrint
    """
    
    profit = v20_data.get('profit_calculation', {})
    decision = v20_data.get('decision', {})
    narratives = v20_data.get('narratives', {})
    comps = v20_data.get('transaction_comps', {})
    
    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>ZeroSite v20 분석 보고서</title>
    <style>
        @page {{
            size: A4;
            margin: 2.5cm;
        }}
        
        body {{
            font-family: 'Noto Sans KR', Arial, sans-serif;
            font-size: 12pt;
            line-height: 1.7;
            color: #333;
        }}
        
        .cover {{
            text-align: center;
            padding: 100px 0;
            border-bottom: 3px solid #005BAC;
            margin-bottom: 50px;
        }}
        
        .cover h1 {{
            font-size: 36pt;
            color: #005BAC;
            margin-bottom: 20px;
        }}
        
        .cover .subtitle {{
            font-size: 18pt;
            color: #666;
            margin-bottom: 10px;
        }}
        
        h2 {{
            color: #005BAC;
            font-size: 18pt;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 2px solid #005BAC;
            padding-bottom: 5px;
        }}
        
        h3 {{
            color: #005BAC;
            font-size: 14pt;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        table th {{
            background: #005BAC;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        table tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        .narrative {{
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #005BAC;
            margin: 20px 0;
            line-height: 1.8;
        }}
        
        .decision-box {{
            background: #fff3cd;
            border: 2px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
        }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ccc;
            font-size: 10pt;
            color: #666;
            text-align: center;
        }}
        
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 20px 0;
        }}
        
        .metric-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #005BAC;
        }}
        
        .metric-label {{
            font-size: 10pt;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .metric-value {{
            font-size: 16pt;
            font-weight: 700;
            color: #005BAC;
        }}
    </style>
</head>
<body>
    <div class="cover">
        <h1>🏗️ ZeroSite v20</h1>
        <div class="subtitle">LH 신축매입임대 사업성 분석 보고서</div>
        <div style="margin-top: 50px; font-size: 14pt; color: #666;">
            <strong>분석 대상 주소:</strong><br>
            {address}
        </div>
        <div style="margin-top: 30px; font-size: 11pt; color: #999;">
            제출자: ZeroSite / Antenna Holdings<br>
            작성자: 나태흠 (Na TaiHeum)<br>
            작성일: {datetime.now().strftime('%Y년 %m월 %d일')}
        </div>
    </div>
    
    <h2>1. 프로젝트 개요</h2>
    
    <table>
        <tr>
            <th>항목</th>
            <th>내용</th>
        </tr>
        <tr>
            <td>사업 유형</td>
            <td>LH 신축형 매입임대 (거래형)</td>
        </tr>
        <tr>
            <td>대상 주소</td>
            <td>{address}</td>
        </tr>
        <tr>
            <td>토지 면적</td>
            <td>{land_area:,.1f} ㎡</td>
        </tr>
        <tr>
            <td>감정평가 단가</td>
            <td>{appraisal:,.0f} 원/㎡</td>
        </tr>
    </table>
    
    <h2>2. 재무 분석 결과</h2>
    
    <div class="metric-grid">
        <div class="metric-item">
            <div class="metric-label">총 사업비 (CAPEX)</div>
            <div class="metric-value">{profit.get('total_capex_krw', 'N/A')}</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">LH 매입가</div>
            <div class="metric-value">{profit.get('lh_purchase_price_krw', 'N/A')}</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">예상 수익</div>
            <div class="metric-value">{profit.get('profit_krw', 'N/A')}</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">ROI</div>
            <div class="metric-value">{profit.get('roi_pct', 0):.2f}%</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">IRR</div>
            <div class="metric-value">{profit.get('irr_pct', 0):.2f}%</div>
        </div>
        <div class="metric-item">
            <div class="metric-label">회수 기간</div>
            <div class="metric-value">{profit.get('payback_years', 0):.1f}년</div>
        </div>
    </div>
    
    <div class="narrative">
        <h3>재무 분석 해석</h3>
        {narratives.get('profit_narrative', '재무 분석 데이터를 기반으로 사업성을 평가한 결과입니다.')}
    </div>
    
    <h2>3. 실거래가 분석</h2>
    
    <h3>3.1 토지 실거래</h3>
    <p>분석된 토지 거래 사례: <strong>{comps.get('land_count', 0)}건</strong></p>
    <p>평균 거래 단가: <strong>{comps.get('avg_land_price', 'N/A')}</strong></p>
    
    <h3>3.2 건물 실거래</h3>
    <p>분석된 건물 거래 사례: <strong>{comps.get('building_count', 0)}건</strong></p>
    <p>평균 거래 단가: <strong>{comps.get('avg_building_price', 'N/A')}</strong></p>
    
    {('<div class="narrative">⚠️ <strong>주의:</strong> 실거래가 데이터가 부재하여, 입력된 감정평가 단가를 기준으로 분석하였습니다.</div>' 
      if not comps.get('land_count') and not comps.get('building_count') else '')}
    
    <h2>4. 의사결정</h2>
    
    <div class="decision-box">
        <h3>최종 판단</h3>
        <p style="font-size: 18pt; font-weight: 700; color: #005BAC;">
            {decision.get('decision', 'N/A')}
        </p>
        
        <table style="margin-top: 20px;">
            <tr>
                <th>구분</th>
                <th>결과</th>
            </tr>
            <tr>
                <td>재무적 기준</td>
                <td>{decision.get('financial_criterion', 'N/A')}</td>
            </tr>
            <tr>
                <td>정책적 기준</td>
                <td>{decision.get('policy_criterion', 'N/A')}</td>
            </tr>
        </table>
    </div>
    
    <div class="narrative">
        <h3>의사결정 근거</h3>
        {narratives.get('decision_narrative', '재무적 기준과 정책적 기준을 종합하여 의사결정을 도출하였습니다.')}
    </div>
    
    <h2>5. 결론</h2>
    
    <p>
        본 보고서는 ZeroSite v20 시스템을 통해 생성된 LH 신축매입임대 사업성 분석 결과입니다.
        실거래가 데이터를 기반으로 총사업비(CAPEX)를 산정하고, LH 감정평가 메커니즘을 시뮬레이션하여
        최종 매입가와 수익성을 예측하였습니다.
    </p>
    
    <p>
        의사결정은 재무적 기준(ROI, IRR 등)과 정책적 기준(지역 우선순위, 정책 부합도 등)을 
        이중 논리로 평가하여 도출하였습니다.
    </p>
    
    <div class="footer">
        <p>
            <strong>ZeroSite v20 Production</strong> | Antenna Holdings<br>
            Author: Na TaiHeum (나태흠) | Email: taina@ant3na.com<br>
            Copyright © 2025 Antenna Holdings. All rights reserved.
        </p>
    </div>
</body>
</html>
    """
    
    return html


if __name__ == '__main__':
    print("=" * 80)
    print("🚀 ZeroSite v20 PRODUCTION Server Starting...")
    print("=" * 80)
    print()
    print("✨ Features:")
    print("   - Direct address input (any Korean address)")
    print("   - Real-time v20 analysis engine")
    print("   - PDF report generation")
    print("   - LH-grade styling")
    print()
    print("📍 Server will run on port 5000")
    print("🌐 Access URL will be provided by GetServiceUrl tool")
    print()
    app.run(host='0.0.0.0', port=5000, debug=False)
