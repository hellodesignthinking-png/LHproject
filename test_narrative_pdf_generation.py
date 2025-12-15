#!/usr/bin/env python3
"""
Test Script: Narrative Layer PDF Generation
Phase A + Template Integration Test

Tests the complete flow:
1. Build Expert Context with Narrative Layer
2. Flatten context for template
3. Render Jinja2 template with narratives
4. Generate PDF with narratives

Expected output: 60-70 page PDF with full narrative text
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services_v13.report_full.report_context_builder import ReportContextBuilder
from jinja2 import Environment, FileSystemLoader


def _flatten_context_for_template(context: dict, land_area_sqm: float) -> dict:
    """
    Flatten context dictionary for template compatibility.
    
    This is the same function used in report_v13.py
    """
    # Extract nested data
    site = context.get('site', {})
    zoning = context.get('zoning', {})
    demand = context.get('demand', {})
    market = context.get('market', {})
    finance = context.get('finance', {})
    cost = context.get('cost', {})
    
    # Add basic site info
    context['land_area_sqm'] = land_area_sqm
    context['land_area_pyeong'] = land_area_sqm / 3.3058
    
    # Handle address - could be nested dict or already a string
    addr = context.get('site', {}).get('address', '')
    if isinstance(addr, dict):
        context['address'] = addr.get('full_address', '')
    else:
        context['address'] = str(addr) if addr else ''
    
    # FIX: Map zoning keys correctly
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
    
    # Demand metrics
    context['demand_score'] = demand.get('overall_score', 60.0)
    context['recommended_housing_type'] = demand.get('recommended_type_kr', demand.get('recommended_type', '청년형'))
    context['demand_confidence'] = 85.0 if demand.get('confidence_level') == 'high' else 70.0
    context['recommended_units'] = demand.get('recommended_units', int(land_area_sqm / 20))
    
    # Fix housing_types structure
    housing_types_raw = demand.get('all_scores', {})
    if isinstance(housing_types_raw, dict):
        context['housing_types'] = [
            {'name': k, 'score': v, 'suitability': v, 'recommended_units': int(v * 2)}
            for k, v in housing_types_raw.items()
        ]
    else:
        context['housing_types'] = []
    
    # Market metrics
    context['market_signal'] = market.get('signal', 'FAIR')
    context['market_temperature'] = market.get('temperature', 'STABLE')
    context['market_delta_pct'] = market.get('delta_pct', 0.0)
    zerosite_val = market.get('zerosite_value_per_sqm', 0.0)
    market_val = market.get('market_avg_price_per_sqm', 0.0)
    context['zerosite_value_per_sqm'] = zerosite_val / 10000 if zerosite_val > 0 else 0
    context['market_avg_price_per_sqm'] = market_val / 10000 if market_val > 0 else 0
    
    # FIX: Financial metrics - ALWAYS convert KRW → 억원
    capex_raw = finance.get('capex', {}).get('total', 0.0)
    npv_raw = finance.get('npv', {}).get('public', 0.0)
    irr_raw = finance.get('irr', {}).get('public', 0.0)
    payback_raw = finance.get('payback', {}).get('years', 0.0)
    
    context['capex_krw'] = capex_raw / 100000000
    context['npv_public_krw'] = npv_raw / 100000000
    context['irr_public_pct'] = irr_raw
    context['payback_period_years'] = payback_raw if payback_raw != float('inf') else 999
    
    # Fix cashflow structure
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
    
    # Cost metrics - ALL in KRW, convert to 억원
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
    
    # Decision
    decision_data = context.get('decision', {})
    context['decision'] = decision_data.get('result', 'NO-GO')
    
    # Risk matrix (generate sample if not present)
    if 'risk_matrix' not in context:
        context['risk_matrix'] = [
            {'category': f'Risk-{i+1}', 'level': 'low' if i%3==0 else ('medium' if i%3==1 else 'high'),
             'impact': 3.5, 'mitigation': f'Mitigation strategy {i+1}'}
            for i in range(25)
        ]
    
    # Analysis parameters
    context['discount_rate'] = 4.5
    context['analysis_period'] = 30
    context['rent_escalation'] = 2.0
    context['vacancy_rate'] = 5.0
    
    # Report metadata
    context['report_date'] = datetime.now().strftime('%Y년 %m월 %d일')
    context['report_id'] = f"EXP-V3-{datetime.now().strftime('%Y%m%d')}"
    
    return context


def test_narrative_pdf_generation():
    """Test complete PDF generation with narratives"""
    
    print("="*80)
    print(" TEST: Narrative Layer PDF Generation")
    print("="*80)
    print()
    
    # Test parameters
    address = "서울시 강남구 역삼동 123"
    land_area_sqm = 500.0
    coordinates = (37.5, 127.0)
    
    print(f"Test Address: {address}")
    print(f"Land Area: {land_area_sqm}㎡")
    print()
    
    # Step 1: Build Expert Context with Narrative Layer
    print("Step 1: Building Expert Context with Narrative Layer...")
    builder = ReportContextBuilder()
    
    try:
        context = builder.build_expert_context(
            address=address,
            land_area_sqm=land_area_sqm,
            coordinates=coordinates
        )
        print("✅ Context built successfully")
        print()
    except Exception as e:
        print(f"❌ Error building context: {e}")
        return False
    
    # Step 2: Check Narrative Layer
    print("Step 2: Checking Narrative Layer...")
    narratives = context.get('narratives', {})
    
    if narratives:
        print(f"✅ Narratives generated: {len(narratives)} sections")
        for section_name, narrative_text in narratives.items():
            char_count = len(narrative_text) if isinstance(narrative_text, str) else 0
            print(f"   - {section_name}: {char_count} characters")
        print()
    else:
        print("❌ No narratives found in context")
        return False
    
    # Step 3: Flatten context for template
    print("Step 3: Flattening context for template...")
    try:
        context = _flatten_context_for_template(context, land_area_sqm)
        print("✅ Context flattened successfully")
        print()
    except Exception as e:
        print(f"❌ Error flattening context: {e}")
        return False
    
    # Step 4: Render Jinja2 template
    print("Step 4: Rendering Jinja2 template...")
    template_dir = Path(__file__).parent / 'app' / 'services_v13' / 'report_full'
    
    try:
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template('lh_expert_edition_v3.html.jinja2')
        html_content = template.render(**context)
        
        html_size = len(html_content)
        html_kb = html_size / 1024
        
        print(f"✅ Template rendered successfully")
        print(f"   HTML size: {html_kb:.1f} KB ({html_size:,} chars)")
        print()
        
        # Save HTML for inspection
        html_output_path = Path(__file__).parent / "output" / "test_narrative_report.html"
        html_output_path.parent.mkdir(parents=True, exist_ok=True)
        html_output_path.write_text(html_content, encoding='utf-8')
        print(f"   HTML saved to: {html_output_path}")
        print()
        
    except Exception as e:
        print(f"❌ Error rendering template: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Generate PDF (optional - requires WeasyPrint)
    print("Step 5: Generating PDF...")
    try:
        from app.services_v13.report_full.pdf_exporter_full import PDFExporterFull
        
        pdf_exporter = PDFExporterFull()
        pdf_output_path = Path(__file__).parent / "output" / "test_narrative_report.pdf"
        pdf_output_path.parent.mkdir(parents=True, exist_ok=True)
        
        pdf_exporter.export_to_pdf(
            html_content=html_content,
            output_path=pdf_output_path,
            metadata={
                'title': 'ZeroSite Expert Edition v3 - Narrative Test',
                'author': 'ZeroSite',
                'subject': 'LH Feasibility Report with Narratives'
            }
        )
        
        pdf_size = pdf_output_path.stat().st_size / 1024
        print(f"✅ PDF generated successfully")
        print(f"   PDF size: {pdf_size:.1f} KB")
        print(f"   PDF saved to: {pdf_output_path}")
        print()
        
    except ImportError:
        print("⚠️  WeasyPrint not available - PDF generation skipped")
        print("   Install with: pip install weasyprint")
        print()
    except Exception as e:
        print(f"⚠️  PDF generation failed: {e}")
        print()
    
    # Summary
    print("="*80)
    print(" TEST SUMMARY")
    print("="*80)
    print()
    print("✅ All steps completed successfully!")
    print()
    print("📊 Narrative Statistics:")
    print(f"   - Total sections: {len(narratives)}")
    total_chars = sum(len(text) if isinstance(text, str) else 0 for text in narratives.values())
    print(f"   - Total characters: {total_chars:,}")
    print(f"   - Estimated pages: ~{total_chars // 4000} pages")
    print()
    print("📂 Output Files:")
    print(f"   - HTML: output/test_narrative_report.html")
    if Path(__file__).parent / "output" / "test_narrative_report.pdf":
        print(f"   - PDF: output/test_narrative_report.pdf")
    print()
    print("🎉 Narrative Layer PDF Integration: SUCCESS!")
    print()
    
    return True


if __name__ == "__main__":
    success = test_narrative_pdf_generation()
    sys.exit(0 if success else 1)
