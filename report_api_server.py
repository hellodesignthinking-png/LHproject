#!/usr/bin/env python3
"""
ZeroSite v15 Phase 2 - Simple API Server for Report Generation
포트 8081에서 실행되는 간단한 Flask 서버
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
import re

sys.path.insert(0, '/home/user/webapp')

from app.services_v13.report_full.report_context_builder import ReportContextBuilder
from app.routers.report_v13 import _flatten_context_for_template
from jinja2 import Environment, FileSystemLoader, select_autoescape

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

OUTPUT_DIR = '/home/user/webapp/output'

@app.route('/api/generate', methods=['POST'])
def generate_report():
    """Generate report from address and area"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        address = data.get('address')
        land_area_sqm = data.get('land_area_sqm')
        
        if not address or not land_area_sqm:
            return jsonify({
                'success': False,
                'message': '주소와 면적을 입력해주세요'
            }), 400
        
        land_area_sqm = float(land_area_sqm)
        
        if land_area_sqm < 100:
            return jsonify({
                'success': False,
                'message': '대지면적은 100㎡ 이상이어야 합니다'
            }), 400
        
        print(f"\n{'='*80}")
        print(f"🚀 Generating report for: {address}")
        print(f"   Area: {land_area_sqm}㎡")
        print(f"{'='*80}\n")
        
        # Generate filename
        sanitized = re.sub(r'[^\w\s가-힣]', '', address)
        parts = sanitized.split()
        if len(parts) >= 2:
            filename_base = f"{parts[0]}_{parts[1]}"
        else:
            filename_base = "custom_report"
        output_filename = f"v15_phase2_{filename_base}.html"
        
        # Build context
        print("🔨 Building context...")
        builder = ReportContextBuilder()
        context = builder.build_expert_context(
            address=address,
            land_area_sqm=land_area_sqm,
            additional_params={'include_v15_phase2': True}
        )
        
        # Flatten context
        print("🎨 Flattening context...")
        flattened = _flatten_context_for_template(context, land_area_sqm)
        
        # Add v15 components
        flattened['v15_decision_tree'] = context.get('v15_decision_tree')
        flattened['v15_condition_table'] = context.get('v15_condition_table')
        flattened['v15_risk_response'] = context.get('v15_risk_response')
        flattened['v15_kpi_cards'] = context.get('v15_kpi_cards')
        flattened['v15_simulation'] = context.get('v15_simulation')
        flattened['v15_sensitivity'] = context.get('v15_sensitivity')
        flattened['v15_approval'] = context.get('v15_approval')
        flattened['v15_government_page'] = context.get('v15_government_page')
        
        # Render template
        print("📄 Rendering template...")
        env = Environment(
            loader=FileSystemLoader('app/services_v13/report_full'),
            autoescape=select_autoescape(['html', 'xml', 'jinja2'])
        )
        template = env.get_template('lh_expert_edition_v3.html.jinja2')
        html_output = template.render(**flattened)
        
        # Save file
        print("💾 Saving report...")
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        file_size = len(html_output) / 1024
        print(f"✅ Report saved: {output_filename} ({file_size:.1f} KB)")
        
        # Get key metrics
        approval_prob = 'N/A'
        expected_npv = 'N/A'
        demand_score = 0
        market_signal = 'N/A'
        
        if 'v15_approval' in context and context['v15_approval']:
            approval_prob = context['v15_approval'].get('probability_pct', 'N/A')
        
        if 'v15_simulation' in context and context['v15_simulation']:
            expected_values = context['v15_simulation'].get('expected_values', {})
            expected_npv = expected_values.get('npv', 'N/A')
        
        demand_ctx = context.get('demand', {})
        market_ctx = context.get('market', {})
        demand_score = demand_ctx.get('overall_score', 0)
        market_signal = market_ctx.get('signal', 'N/A')
        
        print(f"\n📊 Report Summary:")
        print(f"   LH 승인확률: {approval_prob}")
        print(f"   Expected NPV: {expected_npv}")
        print(f"   수요 점수: {demand_score:.1f}/100")
        print(f"   시장 신호: {market_signal}")
        print(f"\n{'='*80}\n")
        
        # Return success
        return jsonify({
            'success': True,
            'report_url': output_filename,
            'approval_probability': approval_prob,
            'expected_npv': str(expected_npv),
            'demand_score': f"{demand_score:.1f}",
            'market_signal': market_signal,
            'file_size_kb': f"{file_size:.1f}",
            'message': '리포트 생성 완료'
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'오류: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'ZeroSite v15 Phase 2 API Server',
        'version': 'v15.2.0'
    })

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'ZeroSite v15 Phase 2 API Server',
        'endpoints': {
            'generate': 'POST /api/generate',
            'health': 'GET /api/health'
        }
    })

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 ZeroSite v15 Phase 2 - Report Generation API Server")
    print("="*80)
    print("\n📡 Starting server on port 8081...")
    print("   API endpoint: http://localhost:8081/api/generate")
    print("   Health check: http://localhost:8081/api/health")
    print("\n   Press Ctrl+C to stop\n")
    print("="*80 + "\n")
    
    app.run(host='0.0.0.0', port=8081, debug=False)
