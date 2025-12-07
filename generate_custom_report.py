#!/usr/bin/env python3
"""
ZeroSite v15 Phase 2 - Custom Report Generator
사용자가 입력한 주소와 면적으로 실시간 리포트 생성
"""

import sys
import os
sys.path.insert(0, '/home/user/webapp')

from app.services_v13.report_full.report_context_builder import ReportContextBuilder
from app.routers.report_v13 import _flatten_context_for_template
from jinja2 import Environment, FileSystemLoader, select_autoescape

def generate_custom_report(address: str, land_area_sqm: float, output_filename: str = None):
    """
    사용자 정의 주소로 v15 Phase 2 리포트 생성
    
    Args:
        address: 대상 주소 (예: "서울특별시 강남구 역삼동 737")
        land_area_sqm: 대지면적 (㎡)
        output_filename: 출력 파일명 (기본값: auto-generated)
    
    Returns:
        tuple: (output_path, file_size_kb)
    """
    
    print("=" * 80)
    print("🚀 ZeroSite v15 Phase 2 (S-Grade) - Custom Report Generator")
    print("=" * 80)
    print(f"\n📍 주소: {address}")
    print(f"📏 대지면적: {land_area_sqm:.1f}㎡ ({land_area_sqm / 3.3058:.1f}평)")
    print()
    
    # Auto-generate filename if not provided
    if not output_filename:
        import re
        # Extract key parts from address
        sanitized = re.sub(r'[^\w\s가-힣]', '', address)
        parts = sanitized.split()
        if len(parts) >= 2:
            filename_base = f"{parts[0]}_{parts[1]}"
        else:
            filename_base = "custom_report"
        output_filename = f"v15_phase2_{filename_base}.html"
    
    print(f"📄 출력 파일: {output_filename}")
    print()
    
    try:
        # Step 1: Build context
        print("🔨 Step 1/4: Building expert context...")
        builder = ReportContextBuilder()
        context = builder.build_expert_context(
            address=address,
            land_area_sqm=land_area_sqm,
            additional_params={'include_v15_phase2': True}
        )
        print("   ✅ Context built successfully")
        
        # Step 2: Verify Phase 2 components
        print("\n🔍 Step 2/4: Verifying Phase 2 components...")
        phase2_components = {
            'v15_simulation': context.get('v15_simulation') is not None,
            'v15_sensitivity': context.get('v15_sensitivity') is not None,
            'v15_approval': context.get('v15_approval') is not None,
            'v15_government_page': context.get('v15_government_page') is not None
        }
        
        for comp, present in phase2_components.items():
            status = "✅" if present else "❌"
            print(f"   {status} {comp}")
        
        if not all(phase2_components.values()):
            print("\n⚠️  Warning: Some Phase 2 components are missing!")
        
        # Step 3: Flatten and render
        print("\n🎨 Step 3/4: Rendering HTML template...")
        flattened = _flatten_context_for_template(context, land_area_sqm)
        
        # Add all v15 components
        flattened['v15_decision_tree'] = context.get('v15_decision_tree')
        flattened['v15_condition_table'] = context.get('v15_condition_table')
        flattened['v15_risk_response'] = context.get('v15_risk_response')
        flattened['v15_kpi_cards'] = context.get('v15_kpi_cards')
        flattened['v15_simulation'] = context.get('v15_simulation')
        flattened['v15_sensitivity'] = context.get('v15_sensitivity')
        flattened['v15_approval'] = context.get('v15_approval')
        flattened['v15_government_page'] = context.get('v15_government_page')
        
        # Load template
        env = Environment(
            loader=FileSystemLoader('app/services_v13/report_full'),
            autoescape=select_autoescape(['html', 'xml', 'jinja2'])
        )
        template = env.get_template('lh_expert_edition_v3.html.jinja2')
        html_output = template.render(**flattened)
        print("   ✅ Template rendered successfully")
        
        # Step 4: Save file
        print("\n💾 Step 4/4: Saving report...")
        output_path = f'output/{output_filename}'
        os.makedirs('output', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        file_size_kb = len(html_output) / 1024
        print(f"   ✅ Report saved: {output_path} ({file_size_kb:.1f} KB)")
        
        # Show key results
        print("\n" + "=" * 80)
        print("📊 리포트 요약")
        print("=" * 80)
        
        if 'v15_approval' in context and context['v15_approval']:
            approval_prob = context['v15_approval'].get('probability_pct', 'N/A')
            print(f"✅ LH 승인 확률: {approval_prob}")
        
        if 'v15_simulation' in context and context['v15_simulation']:
            expected_npv = context['v15_simulation'].get('expected_values', {}).get('npv', 'N/A')
            print(f"💰 Expected NPV: {expected_npv}")
        
        demand_ctx = context.get('demand', {})
        market_ctx = context.get('market', {})
        finance_ctx = context.get('finance', {})
        
        print(f"📈 수요 점수: {demand_ctx.get('overall_score', 0):.1f}/100")
        print(f"📊 시장 신호: {market_ctx.get('signal', 'N/A')}")
        print(f"💵 NPV (Public): {finance_ctx.get('npv_public', 0) / 100_000_000:.1f} 억원")
        
        print("\n🌐 웹 접속 URL:")
        print(f"   https://8080-i65g3ela1oephi4loymka-ad490db5.sandbox.novita.ai/{output_filename}")
        print("=" * 80)
        
        return output_path, file_size_kb
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, 0

def main():
    """메인 함수 - 명령행 인자 또는 대화형 입력"""
    
    if len(sys.argv) >= 3:
        # Command line arguments
        address = sys.argv[1]
        land_area_sqm = float(sys.argv[2])
        output_filename = sys.argv[3] if len(sys.argv) > 3 else None
    else:
        # Interactive input
        print("=" * 80)
        print("🏗️  ZeroSite v15 Phase 2 - 사용자 정의 리포트 생성")
        print("=" * 80)
        print()
        address = input("📍 주소를 입력하세요: ")
        land_area_sqm = float(input("📏 대지면적(㎡)을 입력하세요: "))
        output_filename = None
    
    # Generate report
    result = generate_custom_report(address, land_area_sqm, output_filename)
    
    if result[0]:
        print("\n✅ 리포트 생성 완료!")
    else:
        print("\n❌ 리포트 생성 실패")
        sys.exit(1)

if __name__ == "__main__":
    main()
