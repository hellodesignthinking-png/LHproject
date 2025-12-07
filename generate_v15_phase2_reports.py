#!/usr/bin/env python3
"""
ZeroSite v15 Phase 2 (S-Grade) - Full HTML Report Generator
Generates complete HTML reports with all Phase 1 + Phase 2 components
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services_v13.report_full.report_context_builder import ReportContextBuilder
from app.routers.report_v13 import _flatten_context_for_template
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

def generate_v15_phase2_report(address: str, land_area_sqm: float, output_filename: str):
    """Generate a single v15 Phase 2 report"""
    
    print(f"\n🔧 Generating: {output_filename}")
    print(f"   📍 Address: {address}")
    print(f"   📏 Area: {land_area_sqm:.1f}㎡")
    
    # Build context with Phase 2 enabled
    builder = ReportContextBuilder()
    context = builder.build_expert_context(
        address=address,
        land_area_sqm=land_area_sqm,
        additional_params={'include_v15_phase2': True}  # Enable Phase 2 components
    )
    
    # Verify Phase 2 components
    phase2_components = {
        'v15_simulation': context.get('v15_simulation') is not None,
        'v15_sensitivity': context.get('v15_sensitivity') is not None,
        'v15_approval': context.get('v15_approval') is not None,
        'v15_government_page': context.get('v15_government_page') is not None
    }
    
    print(f"   🎯 Phase 2 Components:")
    for comp, present in phase2_components.items():
        status = "✅" if present else "❌"
        print(f"      {status} {comp}")
    
    # Flatten context for template rendering
    print(f"   🔧 Flattening context for template...")
    flattened = _flatten_context_for_template(context, land_area_sqm)
    
    # Add v15 Phase 1 components
    flattened['v15_decision_tree'] = context.get('v15_decision_tree')
    flattened['v15_condition_table'] = context.get('v15_condition_table')
    flattened['v15_risk_response'] = context.get('v15_risk_response')
    flattened['v15_kpi_cards'] = context.get('v15_kpi_cards')
    
    # Add v15 Phase 2 components
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
    
    # Render HTML
    html_output = template.render(**flattened)
    
    # Save to file
    output_path = f'output/{output_filename}'
    os.makedirs('output', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    file_size_kb = len(html_output) / 1024
    print(f"   ✅ Saved: {output_path} ({file_size_kb:.1f} KB)")
    
    # Show key metrics
    if 'v15_approval' in context and context['v15_approval']:
        approval_prob = context['v15_approval'].get('probability_pct', 'N/A')
        print(f"   📊 LH Approval Probability: {approval_prob}")
    
    if 'v15_simulation' in context and context['v15_simulation']:
        expected_npv = context['v15_simulation'].get('expected_values', {}).get('npv', 'N/A')
        print(f"   💰 Expected NPV: {expected_npv}")
    
    return output_path, file_size_kb

def main():
    """Generate all v15 Phase 2 test reports"""
    
    print("="*80)
    print("🚀 ZeroSite v15 Phase 2 (S-Grade 100%) - HTML Report Generator")
    print("="*80)
    
    test_cases = [
        {
            'name': 'Seoul Gangnam',
            'address': '서울특별시 강남구 역삼동 737',
            'region': 'seoul',
            'land_area_sqm': 800.0,
            'output_file': 'v15_phase2_gangnam.html'
        },
        {
            'name': 'Bundang',
            'address': '경기도 성남시 분당구 정자동 178',
            'region': 'gyeonggi',
            'land_area_sqm': 650.0,
            'output_file': 'v15_phase2_bundang.html'
        },
        {
            'name': 'Busan Haeundae',
            'address': '부산광역시 해운대구 우동 1234',
            'region': 'busan',
            'land_area_sqm': 700.0,
            'output_file': 'v15_phase2_busan.html'
        }
    ]
    
    generated_files = []
    
    for tc in test_cases:
        try:
            output_path, file_size = generate_v15_phase2_report(
                address=tc['address'],
                land_area_sqm=tc['land_area_sqm'],
                output_filename=tc['output_file']
            )
            generated_files.append((tc['name'], output_path, file_size))
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*80)
    print("📊 Generation Summary")
    print("="*80)
    for name, path, size in generated_files:
        print(f"✅ {name:20s} → {path:50s} ({size:.1f} KB)")
    
    print(f"\n🎉 Generated {len(generated_files)}/{len(test_cases)} reports successfully!")
    print("\n📡 Access reports at:")
    print("   https://8080-i65g3ela1oephi4loymka-ad490db5.sandbox.novita.ai/")
    print("="*80)

if __name__ == "__main__":
    main()
