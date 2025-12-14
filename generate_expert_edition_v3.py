"""
ZeroSite Expert Edition v3 - PDF Generator
Academic Research-Grade Report (50-60 pages)

Target Output:
- 50-60 pages
- 500-700KB PDF
- <6 seconds generation time
- LH submission quality
"""

from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import sys

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services_v13.report_full.report_context_builder import ReportContextBuilder
from app.services_v13.report_full.pdf_exporter_full import PDFExporterFull


def generate_expert_edition_v3(
    address: str,
    land_area_sqm: float,
    zone_type: str = "제2종일반주거지역",
    output_dir: str = "/tmp"
):
    """
    Generate Expert Edition v3 PDF Report
    
    Args:
        address: 대상지 주소
        land_area_sqm: 대지면적 (㎡)
        zone_type: 용도지역
        output_dir: PDF 저장 경로
    
    Returns:
        dict: {
            'success': bool,
            'pdf_path': str,
            'html_path': str,
            'context': dict,
            'generation_time_ms': int,
            'file_size_kb': int,
            'page_count_estimate': int
        }
    """
    
    start_time = datetime.now()
    
    print("="*80)
    print("🚀 ZeroSite Expert Edition v3 - PDF Generator")
    print("="*80)
    print(f"📍 Address: {address}")
    print(f"📐 Land Area: {land_area_sqm:.2f}㎡")
    print(f"🏘️ Zone Type: {zone_type}")
    print()
    
    # ============================================================
    # STEP 1: Build Expert Context (using build_expert_context)
    # ============================================================
    print("⏳ Step 1/4: Building Expert Context (Phase 2.5/6.8/7.7 + Policy/Roadmap/Academic)...")
    
    builder = ReportContextBuilder()
    
    try:
        # Use the new build_expert_context method
        context = builder.build_expert_context(
            address=address,
            land_area_sqm=land_area_sqm
        )
        
        print("✅ Expert Context Built Successfully!")
        print(f"   - Sections: {len(context.keys())}")
        print(f"   - Policy Framework: {'✓' if 'policy_framework' in context else '✗'}")
        print(f"   - Implementation Roadmap: {'✓' if 'implementation_roadmap' in context else '✗'}")
        print(f"   - Academic Conclusion: {'✓' if 'academic_conclusion' in context else '✗'}")
        print()
        
    except Exception as e:
        print(f"❌ Expert Context Build Failed: {e}")
        print("   Falling back to Full Edition context...")
        context = builder.build_context(
            address=address,
            land_area_sqm=land_area_sqm
        )
        print()
    
    # ============================================================
    # STEP 2: Render HTML using Expert Edition Template
    # ============================================================
    print("⏳ Step 2/4: Rendering Expert Edition HTML Template...")
    
    # Setup Jinja2 environment
    template_dir = Path(__file__).parent / "app" / "services_v13" / "report_full"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    # Load Expert Edition v3 template
    template = env.get_template("lh_expert_edition_v3.html.jinja2")
    
    # Add report metadata
    context['report_date'] = datetime.now().strftime("%Y년 %m월 %d일")
    context['report_id'] = f"EXP-V3-{datetime.now().strftime('%Y%m%d')}-001"
    
    # Add missing template variables with defaults
    context['land_area_sqm'] = land_area_sqm
    context['land_area_pyeong'] = land_area_sqm / 3.3058
    context['address'] = address
    
    # Extract nested data for easier template access
    site = context.get('site', {})
    zoning = context.get('zoning', {})
    demand = context.get('demand', {})
    market = context.get('market', {})
    finance = context.get('finance', {})
    cost = context.get('cost', {})
    
    # FIX: Use CORRECT keys from zoning section
    # zoning section has: bcr, far, building_area, gross_floor_area, max_height
    context['floor_area_ratio'] = zoning.get('far', 200.0)  # FIX: was site.get('floor_area_ratio')
    context['building_coverage'] = zoning.get('bcr', 60.0)  # FIX: was site.get('building_coverage')
    context['building_area_sqm'] = zoning.get('building_area', land_area_sqm * 0.6)  # FIX
    context['total_floor_area_sqm'] = zoning.get('gross_floor_area', land_area_sqm * 2.0)  # FIX
    context['building_height_m'] = zoning.get('max_height', 35.0)  # FIX
    context['max_building_coverage'] = 60.0  # Legal limit for Type 2 Residential
    context['max_floor_area_ratio'] = 250.0  # Legal limit for Type 2 Residential
    context['max_height_m'] = 35.0  # Legal limit
    context['zone_type'] = zoning.get('zone_type', zone_type)  # FIX: get from context first
    context['land_category'] = '대'
    
    # Demand metrics (Phase 6.8)
    context['demand_score'] = demand.get('overall_score', 60.0)  # FIX: default to 60 not 0
    context['recommended_housing_type'] = demand.get('recommended_type_kr', demand.get('recommended_type', '청년형'))
    context['demand_confidence'] = 85.0 if demand.get('confidence_level') == 'high' else 70.0  # FIX: confidence_level not confidence
    context['recommended_units'] = demand.get('recommended_units', int(land_area_sqm / 20))  # Estimate from area
    # Fix housing_types structure
    housing_types_raw = demand.get('all_scores', {})
    if isinstance(housing_types_raw, dict):
        context['housing_types'] = [
            {'name': k, 'score': v, 'suitability': v, 'recommended_units': int(v * 2)}
            for k, v in housing_types_raw.items()
        ]
    else:
        context['housing_types'] = []
    
    # Market metrics (Phase 7.7)
    context['market_signal'] = market.get('signal', 'FAIR')
    context['market_temperature'] = market.get('temperature', 'STABLE')
    context['market_delta_pct'] = market.get('delta_pct', 0.0)
    # Market values are already per sqm, convert KRW → 만원 (divide by 10000)
    zerosite_val = market.get('zerosite_value_per_sqm', 0.0)
    market_val = market.get('market_avg_price_per_sqm', 0.0)
    context['zerosite_value_per_sqm'] = zerosite_val / 10000 if zerosite_val > 0 else 0
    context['market_avg_price_per_sqm'] = market_val / 10000 if market_val > 0 else 0
    
    # Financial metrics (ALL values from engine are in KRW, convert to 억원)
    # 1억원 = 100,000,000 KRW
    capex_raw = finance.get('capex', {}).get('total', 0.0)
    npv_raw = finance.get('npv', {}).get('public', 0.0)
    irr_raw = finance.get('irr', {}).get('public', 0.0)
    payback_raw = finance.get('payback', {}).get('years', 0.0)
    
    # Convert KRW → 억원 (always divide by 100000000)
    context['capex_krw'] = capex_raw / 100000000  # FIX: always convert
    context['npv_public_krw'] = npv_raw / 100000000  # FIX: always convert
    context['irr_public_pct'] = irr_raw  # Already in percentage
    context['payback_period_years'] = payback_raw if payback_raw != float('inf') else 999  # FIX: inf → 999
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
    
    # Cost metrics (Phase 8) - ALL values in KRW, convert to 억원 and 만원/㎡
    total_const_cost = cost.get('construction', {}).get('total', 0.0)
    per_sqm_cost = cost.get('construction', {}).get('per_sqm', 0.0)
    context['total_construction_cost_krw'] = total_const_cost / 100000000  # KRW → 억원
    context['cost_per_sqm_krw'] = per_sqm_cost / 10000  # KRW/㎡ → 만원/㎡
    context['cost_confidence'] = cost.get('verification', {}).get('confidence', 85.0)
    
    # Cost breakdown (all in 억원)
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
    
    # Render HTML
    html_content = template.render(**context)
    
    # Save HTML
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    html_filename = "expert_edition_v3.html"
    html_path = output_path / html_filename
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML Rendered: {html_path}")
    print(f"   - File size: {len(html_content)/1024:.1f} KB")
    print()
    
    # ============================================================
    # STEP 3: Convert HTML to PDF
    # ============================================================
    print("⏳ Step 3/4: Converting HTML to PDF (WeasyPrint)...")
    
    pdf_exporter = PDFExporterFull()
    
    # Generate safe filename
    safe_address = address.replace(" ", "_").replace("/", "_")
    pdf_filename = f"zerosite_expert_v3_{safe_address}_{datetime.now().strftime('%Y%m%d')}.pdf"
    pdf_path = output_path / pdf_filename
    
    try:
        pdf_exporter.export_to_pdf(
            html_content=html_content,
            output_path=pdf_path  # Pass Path object, not string
        )
        
        # Get file size
        file_size_kb = pdf_path.stat().st_size / 1024
        
        print(f"✅ PDF Generated: {pdf_path}")
        print(f"   - File size: {file_size_kb:.1f} KB")
        print()
        
    except Exception as e:
        print(f"❌ PDF Generation Failed: {e}")
        pdf_path = None
        file_size_kb = 0
    
    # ============================================================
    # STEP 4: Calculate Metrics
    # ============================================================
    end_time = datetime.now()
    generation_time_ms = int((end_time - start_time).total_seconds() * 1000)
    
    # Estimate page count (HTML lines / 30 ≈ pages)
    page_count_estimate = len(html_content.split('\n')) // 30
    
    print("="*80)
    print("✅ Expert Edition v3 Generation Complete!")
    print("="*80)
    print(f"⏱️  Generation Time: {generation_time_ms}ms ({generation_time_ms/1000:.2f}s)")
    print(f"📄 Estimated Pages: {page_count_estimate} pages")
    print(f"📦 PDF Size: {file_size_kb:.1f} KB")
    print(f"🎯 Target Met: {'✅' if 500 <= file_size_kb <= 700 and generation_time_ms < 6000 else '⚠️'}")
    print()
    
    return {
        'success': pdf_path is not None,
        'pdf_path': str(pdf_path) if pdf_path else None,
        'html_path': str(html_path),
        'context': context,
        'generation_time_ms': generation_time_ms,
        'file_size_kb': file_size_kb,
        'page_count_estimate': page_count_estimate
    }


def main():
    """Test Expert Edition v3 with sample data"""
    
    # Test Case: Seoul Gangnam Youth Housing
    result = generate_expert_edition_v3(
        address="서울시 강남구 역삼동 123",
        land_area_sqm=500.0,
        zone_type="제2종일반주거지역",
        output_dir="/tmp"
    )
    
    # Print summary
    print("📊 Generation Summary:")
    print(f"   Success: {result['success']}")
    print(f"   PDF: {result['pdf_path']}")
    print(f"   HTML: {result['html_path']}")
    print(f"   Time: {result['generation_time_ms']}ms")
    print(f"   Size: {result['file_size_kb']:.1f}KB")
    print(f"   Pages: {result['page_count_estimate']}")
    
    # Financial Summary (FIX: these keys are in root context, not in finance)
    ctx = result['context']
    print()
    print("💰 Financial Summary:")
    print(f"   CAPEX: {ctx.get('capex_krw', 0):.2f}억원")
    print(f"   NPV: {ctx.get('npv_public_krw', 0):.2f}억원")
    print(f"   IRR: {ctx.get('irr_public_pct', 0):.2f}%")
    
    # Decision
    decision_val = result['context'].get('decision', 'N/A')
    print()
    print("🎯 Decision:")
    if isinstance(decision_val, dict):
        print(f"   Result: {decision_val.get('result', 'N/A')}")
        print(f"   Risk: {decision_val.get('overall_risk_level', 'N/A')}")
    else:
        print(f"   Result: {decision_val}")
    
    return result


if __name__ == "__main__":
    main()
