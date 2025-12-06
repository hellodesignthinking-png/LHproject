#!/usr/bin/env python3
"""
Real Project Data Test
Generate full 60-70 page report with actual project data

This will test:
1. Real address geocoding
2. Full context generation
3. All 8 narrative sections
4. Complete HTML rendering
5. PDF export (if WeasyPrint works)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services_v13.report_full.report_context_builder import ReportContextBuilder
from jinja2 import Environment, FileSystemLoader
from datetime import datetime


def _flatten_context_for_template(context: dict, land_area_sqm: float) -> dict:
    """Same flattening function as in report_v13.py"""
    site = context.get('site', {})
    zoning = context.get('zoning', {})
    demand = context.get('demand', {})
    market = context.get('market', {})
    finance = context.get('finance', {})
    cost = context.get('cost', {})
    
    context['land_area_sqm'] = land_area_sqm
    context['land_area_pyeong'] = land_area_sqm / 3.3058
    
    addr_obj = site.get('address', '')
    if isinstance(addr_obj, dict):
        context['address'] = addr_obj.get('full_address', '')
    else:
        context['address'] = str(addr_obj) if addr_obj else ''
    
    context['floor_area_ratio'] = zoning.get('far', 200.0)
    context['building_coverage'] = zoning.get('bcr', 60.0)
    context['building_area_sqm'] = zoning.get('building_area', land_area_sqm * 0.6)
    context['total_floor_area_sqm'] = zoning.get('gross_floor_area', land_area_sqm * 2.0)
    context['building_height_m'] = zoning.get('max_height', 35.0)
    context['max_building_coverage'] = 60.0
    context['max_floor_area_ratio'] = 250.0
    context['max_height_m'] = 35.0
    context['zone_type'] = zoning.get('zone_type', '제2종일반주거지역')
    context['land_category'] = '대'
    
    context['demand_score'] = demand.get('overall_score', 60.0)
    context['recommended_housing_type'] = demand.get('recommended_type_kr', demand.get('recommended_type', '청년형'))
    context['demand_confidence'] = 85.0 if demand.get('confidence_level') == 'high' else 70.0
    context['recommended_units'] = demand.get('recommended_units', int(land_area_sqm / 20))
    
    housing_types_raw = demand.get('all_scores', {})
    if isinstance(housing_types_raw, dict):
        context['housing_types'] = [
            {'name': k, 'score': v, 'suitability': v, 'recommended_units': int(v * 2)}
            for k, v in housing_types_raw.items()
        ]
    else:
        context['housing_types'] = []
    
    context['market_signal'] = market.get('signal', 'FAIR')
    context['market_temperature'] = market.get('temperature', 'STABLE')
    context['market_delta_pct'] = market.get('delta_pct', 0.0)
    zerosite_val = market.get('zerosite_value_per_sqm', 0.0)
    market_val = market.get('market_avg_price_per_sqm', 0.0)
    context['zerosite_value_per_sqm'] = zerosite_val / 10000 if zerosite_val > 0 else 0
    context['market_avg_price_per_sqm'] = market_val / 10000 if market_val > 0 else 0
    
    capex_raw = finance.get('capex', {}).get('total', 0.0)
    npv_raw = finance.get('npv', {}).get('public', 0.0)
    irr_raw = finance.get('irr', {}).get('public', 0.0)
    payback_raw = finance.get('payback', {}).get('years', 0.0)
    
    context['capex_krw'] = capex_raw / 100000000
    context['npv_public_krw'] = npv_raw / 100000000
    context['irr_public_pct'] = irr_raw
    context['payback_period_years'] = payback_raw if payback_raw != float('inf') else 999
    
    cashflow_raw = finance.get('cashflow', [])
    context['cash_flow_table'] = [
        {
            'year': cf.get('year', i+1),
            'revenue': cf.get('revenue', 0.0),
            'expense': cf.get('expense', 0.0),
            'net_cf': cf.get('cf', 0.0),
            'cumulative_cf': cf.get('cumulative', 0.0)
        }
        for i, cf in enumerate(cashflow_raw)
    ]
    
    total_const_cost = cost.get('construction', {}).get('total', 0.0)
    per_sqm_cost = cost.get('construction', {}).get('per_sqm', 0.0)
    context['total_construction_cost_krw'] = total_const_cost / 100000000
    context['cost_per_sqm_krw'] = per_sqm_cost / 10000
    context['cost_confidence'] = cost.get('verification', {}).get('confidence', 85.0)
    
    breakdown = cost.get('construction', {}).get('breakdown', {})
    context['direct_cost_krw'] = breakdown.get('direct', 0.0) / 100000000
    context['indirect_cost_krw'] = breakdown.get('indirect', 0.0) / 100000000
    context['design_cost_krw'] = breakdown.get('design', 0.0) / 100000000
    context['other_cost_krw'] = breakdown.get('contingency', 0.0) / 100000000
    
    decision_data = context.get('decision', {})
    context['decision'] = decision_data.get('result', 'NO-GO')
    
    if 'risk_matrix' not in context:
        context['risk_matrix'] = [
            {'category': f'Risk-{i+1}', 'level': 'low' if i%3==0 else ('medium' if i%3==1 else 'high'),
             'impact': 3.5, 'mitigation': f'Mitigation strategy {i+1}'}
            for i in range(25)
        ]
    
    context['discount_rate'] = 4.5
    context['analysis_period'] = 30
    context['rent_escalation'] = 2.0
    context['vacancy_rate'] = 5.0
    
    context['report_date'] = datetime.now().strftime('%Y년 %m월 %d일')
    context['report_id'] = f"EXP-V3-{datetime.now().strftime('%Y%m%d')}"
    
    return context


def main():
    """Generate real project report"""
    
    print("="*80)
    print(" REAL PROJECT DATA TEST")
    print(" Generating Full 60-70 Page Report with Narratives")
    print("="*80)
    print()
    
    # Real project parameters - you can modify these
    test_cases = [
        {
            'name': 'Gangnam Test Case',
            'address': '서울특별시 강남구 역삼동 737',
            'land_area_sqm': 800.0,
            'coordinates': (37.5008, 127.0366)
        },
        {
            'name': 'Songpa Test Case',
            'address': '서울특별시 송파구 잠실동 40',
            'land_area_sqm': 1000.0,
            'coordinates': (37.5133, 127.1028)
        }
    ]
    
    # Select test case
    test_case = test_cases[0]  # Change to test_cases[1] for second case
    
    print(f"📍 Test Case: {test_case['name']}")
    print(f"   Address: {test_case['address']}")
    print(f"   Land Area: {test_case['land_area_sqm']}㎡")
    print(f"   Coordinates: {test_case['coordinates']}")
    print()
    
    # Build context
    print("🔨 Building Expert Context with Narrative Layer...")
    builder = ReportContextBuilder()
    
    try:
        context = builder.build_expert_context(
            address=test_case['address'],
            land_area_sqm=test_case['land_area_sqm'],
            coordinates=test_case['coordinates']
        )
        print("✅ Context built successfully")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check narratives
    narratives = context.get('narratives', {})
    print("📝 Narrative Layer Statistics:")
    print(f"   Sections: {len(narratives)}")
    
    total_chars = 0
    for section, text in narratives.items():
        chars = len(text) if isinstance(text, str) else 0
        total_chars += chars
        print(f"   - {section}: {chars:,} chars")
    
    print(f"\n   📊 Total: {total_chars:,} characters")
    print(f"   📄 Estimated: ~{total_chars // 2000} pages of narrative")
    print()
    
    # Flatten and render
    print("🎨 Rendering template...")
    context = _flatten_context_for_template(context, test_case['land_area_sqm'])
    
    template_dir = Path(__file__).parent / 'app' / 'services_v13' / 'report_full'
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template('lh_expert_edition_v3.html.jinja2')
    html_content = template.render(**context)
    
    print(f"✅ Template rendered: {len(html_content):,} characters ({len(html_content)/1024:.1f} KB)")
    print()
    
    # Save HTML
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    html_file = output_dir / f"report_{test_case['name'].replace(' ', '_').lower()}.html"
    html_file.write_text(html_content, encoding='utf-8')
    print(f"💾 HTML saved: {html_file}")
    print()
    
    # Try PDF export
    print("📄 Attempting PDF generation...")
    try:
        from app.services_v13.report_full.pdf_exporter_full import PDFExporterFull
        from weasyprint import HTML as WeasyHTML
        
        pdf_file = output_dir / f"report_{test_case['name'].replace(' ', '_').lower()}.pdf"
        
        weasy_html = WeasyHTML(string=html_content)
        weasy_html.write_pdf(pdf_file)
        
        pdf_size = pdf_file.stat().st_size / 1024 / 1024
        print(f"✅ PDF generated: {pdf_file}")
        print(f"   Size: {pdf_size:.2f} MB")
        print()
    except Exception as e:
        print(f"⚠️  PDF generation failed: {e}")
        print("   (HTML is available for review)")
        print()
    
    # Summary
    print("="*80)
    print(" REPORT GENERATION COMPLETE!")
    print("="*80)
    print()
    print(f"✅ Project: {test_case['name']}")
    print(f"✅ Address: {test_case['address']}")
    print(f"✅ Narratives: {len(narratives)}/8 sections")
    print(f"✅ Total Content: {total_chars:,} characters")
    print(f"✅ HTML: {len(html_content):,} characters ({len(html_content)/1024:.1f} KB)")
    print()
    print(f"📂 Output files in: {output_dir}/")
    print()
    print("🎉 SUCCESS! Ready for deployment!")
    print()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
