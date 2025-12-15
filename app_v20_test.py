"""
ZeroSite v20 Test Web Service
==============================

Simple Flask app for testing v20 reports

Author: Na TaiHeum (나태흠)
Organization: Antenna Holdings
"""

from flask import Flask, render_template_string, request, jsonify
from app.services_v13.report_full.report_context_builder import ReportContextBuilder
import json

app = Flask(__name__)

# HTML Template for the test interface
TEST_INTERFACE_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZeroSite v20 테스트</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 16px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            font-size: 36px;
            font-weight: 900;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 16px;
            color: #666;
        }
        
        .test-form {
            background: white;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .form-group {
            margin-bottom: 24px;
        }
        
        .form-group label {
            display: block;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 16px 40px;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .results {
            background: white;
            border-radius: 16px;
            padding: 40px;
            margin-top: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: none;
        }
        
        .results.show {
            display: block;
        }
        
        .result-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
        }
        
        .result-card h3 {
            color: #667eea;
            margin-bottom: 16px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            font-weight: 600;
            color: #666;
        }
        
        .metric-value {
            font-weight: 700;
            color: #333;
        }
        
        .decision-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 14px;
        }
        
        .decision-go {
            background: #22c55e;
            color: white;
        }
        
        .decision-conditional {
            background: #f59e0b;
            color: white;
        }
        
        .decision-no {
            background: #ef4444;
            color: white;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ ZeroSite v20 테스트</h1>
            <p>LH 신축매입임대 사업성 분석 시스템 | Author: Na TaiHeum (나태흠)</p>
        </div>
        
        <div class="test-form">
            <h2 style="margin-bottom: 24px;">테스트 주소 입력</h2>
            
            <div class="form-group">
                <label>주소</label>
                <select id="address" onchange="updateAddress()">
                    <option value="서울특별시 마포구 월드컵북로 120">서울 마포구 (도심 핵심)</option>
                    <option value="서울특별시 강남구 역삼동 123">서울 강남구 (프리미엄)</option>
                    <option value="경기도 성남시 분당구 정자동 178-1">경기 성남 분당 (1기 신도시)</option>
                    <option value="경기도 고양시 일산동구 장항동 906">경기 고양 일산 (1기 신도시)</option>
                    <option value="경기도 화성시 동탄기흥로 160">경기 화성 동탄 (2기 신도시)</option>
                    <option value="인천광역시 남동구 구월동 1470">인천 남동구</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>토지 면적 (㎡)</label>
                <input type="number" id="land_area" value="660" step="10">
            </div>
            
            <div class="form-group">
                <label>감정평가 단가 (원/㎡)</label>
                <input type="number" id="appraisal" value="10000000" step="1000000">
            </div>
            
            <button class="btn" onclick="runTest()">분석 시작</button>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>분석 중입니다... (약 5초 소요)</p>
        </div>
        
        <div class="results" id="results">
            <h2 style="margin-bottom: 24px;">분석 결과</h2>
            
            <div class="result-card">
                <h3>💰 재무 분석</h3>
                <div class="metric">
                    <span class="metric-label">총 사업비 (CAPEX)</span>
                    <span class="metric-value" id="capex">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">LH 매입가</span>
                    <span class="metric-value" id="purchase">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">예상 수익</span>
                    <span class="metric-value" id="profit">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">ROI</span>
                    <span class="metric-value" id="roi">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">IRR</span>
                    <span class="metric-value" id="irr">-</span>
                </div>
            </div>
            
            <div class="result-card">
                <h3>🎯 의사결정</h3>
                <div class="metric">
                    <span class="metric-label">최종 판단</span>
                    <span class="metric-value" id="decision">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">재무적 기준</span>
                    <span class="metric-value" id="financial">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">정책적 기준</span>
                    <span class="metric-value" id="policy">-</span>
                </div>
            </div>
            
            <div class="result-card">
                <h3>📊 v20 통합 상태</h3>
                <div id="v20-status"></div>
            </div>
        </div>
    </div>
    
    <script>
        function updateAddress() {
            const select = document.getElementById('address');
            const value = select.value;
            
            // Update suggested values based on address
            if (value.includes('강남')) {
                document.getElementById('appraisal').value = '15000000';
                document.getElementById('land_area').value = '500';
            } else if (value.includes('분당')) {
                document.getElementById('appraisal').value = '8000000';
                document.getElementById('land_area').value = '700';
            } else {
                document.getElementById('appraisal').value = '10000000';
                document.getElementById('land_area').value = '660';
            }
        }
        
        async function runTest() {
            const address = document.getElementById('address').value;
            const land_area = parseFloat(document.getElementById('land_area').value);
            const appraisal = parseFloat(document.getElementById('appraisal').value);
            
            // Show loading
            document.getElementById('loading').classList.add('show');
            document.getElementById('results').classList.remove('show');
            
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
                    displayResults(data.result);
                } else {
                    alert('분석 실패: ' + data.error);
                }
            } catch (error) {
                alert('오류: ' + error.message);
            } finally {
                document.getElementById('loading').classList.remove('show');
            }
        }
        
        function displayResults(result) {
            const v20 = result.v19_finance;  // It's actually v20
            
            // Financial metrics
            const profit = v20.profit_calculation;
            document.getElementById('capex').textContent = profit.total_capex_krw;
            document.getElementById('purchase').textContent = profit.lh_purchase_price_krw;
            document.getElementById('profit').textContent = profit.profit_krw;
            document.getElementById('roi').textContent = profit.roi_pct.toFixed(2) + '%';
            document.getElementById('irr').textContent = profit.irr_pct.toFixed(2) + '%';
            
            // Decision
            const decision = v20.decision;
            const decisionClass = decision.decision === 'GO' ? 'decision-go' : 
                                 decision.decision.includes('CONDITIONAL') ? 'decision-conditional' : 
                                 'decision-no';
            
            document.getElementById('decision').innerHTML = 
                `<span class="decision-badge ${decisionClass}">${decision.decision}</span>`;
            document.getElementById('financial').textContent = decision.financial_criterion;
            document.getElementById('policy').textContent = decision.policy_criterion;
            
            // v20 Status
            const status = v20.v20_status || {};
            let statusHtml = '';
            for (const [key, value] of Object.entries(status)) {
                const icon = value ? '✅' : '❌';
                statusHtml += `<div class="metric">
                    <span class="metric-label">${key}</span>
                    <span class="metric-value">${icon}</span>
                </div>`;
            }
            document.getElementById('v20-status').innerHTML = statusHtml;
            
            // Show results
            document.getElementById('results').classList.add('show');
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main test interface"""
    return render_template_string(TEST_INTERFACE_HTML)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API endpoint for analysis"""
    try:
        data = request.json
        
        address = data.get('address', '서울특별시 마포구 월드컵북로 120')
        land_area_sqm = data.get('land_area_sqm', 660.0)
        appraisal_price = data.get('appraisal_price', 10_000_000)
        
        # Build context
        builder = ReportContextBuilder()
        context = builder.build_context(
            address=address,
            land_area_sqm=land_area_sqm,
            coordinates=None,
            multi_parcel=False,
            parcels=None,
            additional_params={'appraisal_price': appraisal_price}
        )
        
        return jsonify({
            'success': True,
            'result': {
                'v19_finance': context.get('v19_finance', {}),
                'metadata': context.get('metadata', {})
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 ZeroSite v20 Test Server Starting...")
    print("=" * 80)
    print()
    print("📍 Access URL will be provided by GetServiceUrl tool")
    print()
    app.run(host='0.0.0.0', port=5555, debug=False)
