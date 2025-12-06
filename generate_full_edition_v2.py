"""
Generate Full Edition LH Report v2 with Complete Template

Uses new ReportContextBuilder + Enhanced Template
"""

import sys
from pathlib import Path
from jinja2 import Template
from weasyprint import HTML, CSS
from datetime import datetime

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services_v13.report_full.report_context_builder import ReportContextBuilder


def generate_full_edition_pdf(
    address: str,
    land_area_sqm: float,
    coordinates: tuple = None,
    output_path: str = None
):
    """
    Generate Full Edition LH Report PDF
    
    Args:
        address: Target site address
        land_area_sqm: Land area in square meters
        coordinates: (lat, lon) for location analysis
        output_path: Output PDF file path
    
    Returns:
        Path to generated PDF
    """
    print("=" * 80)
    print("🚀 ZeroSite Full Edition Report Generator v2")
    print("=" * 80)
    
    # Step 1: Build REPORT_CONTEXT
    print("\n📊 Step 1: Building REPORT_CONTEXT...")
    builder = ReportContextBuilder()
    context = builder.build_context(
        address=address,
        land_area_sqm=land_area_sqm,
        coordinates=coordinates,
        multi_parcel=False,
        parcels=None,
        additional_params=None
    )
    
    print(f"  ✓ Context generated with {len(context)} sections")
    print(f"  ✓ Recommended Type: {context['demand']['recommended_type_kr']}")
    print(f"  ✓ CAPEX: {context['finance']['capex']['total'] / 1e8:.2f}억원")
    print(f"  ✓ NPV (Public): {context['finance']['npv']['public'] / 1e8:+.2f}억원")
    print(f"  ✓ Decision: {context['decision']['recommendation']}")
    
    # Step 2: Load template
    print("\n📝 Step 2: Loading Enhanced Template...")
    template_path = Path(__file__).parent / "app" / "templates_v13" / "lh_full_edition_v2.html.jinja2"
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_str = f.read()
    
    template = Template(template_str)
    print(f"  ✓ Template loaded: {len(template_str):,} characters")
    
    # Step 3: Render HTML
    print("\n🎨 Step 3: Rendering HTML...")
    html_content = template.render(**context)
    print(f"  ✓ HTML rendered: {len(html_content):,} characters")
    
    # Save HTML for inspection
    html_output_path = output_path.replace('.pdf', '.html') if output_path else '/tmp/full_edition_v2.html'
    with open(html_output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"  ✓ HTML saved: {html_output_path}")
    
    # Step 4: Generate PDF
    print("\n📄 Step 4: Generating PDF...")
    
    if not output_path:
        # Generate filename from address
        safe_address = address.replace(' ', '_').replace('/', '_')
        timestamp = datetime.now().strftime('%Y%m%d')
        output_path = f"/tmp/zerosite_full_edition_{safe_address}_{timestamp}.pdf"
    
    try:
        HTML(string=html_content).write_pdf(output_path)
        print(f"  ✓ PDF generated: {output_path}")
        
        # Get file size
        file_size = Path(output_path).stat().st_size
        print(f"  ✓ File size: {file_size / 1024:.1f} KB")
        
    except Exception as e:
        print(f"  ✗ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # Step 5: Summary
    print("\n" + "=" * 80)
    print("✅ FULL EDITION REPORT COMPLETE")
    print("=" * 80)
    print(f"\n📌 Report Summary:")
    print(f"  - Address: {address}")
    print(f"  - Land Area: {land_area_sqm:.2f}㎡ ({land_area_sqm / 3.3058:.2f}평)")
    print(f"  - Housing Type: {context['demand']['recommended_type_kr']}")
    print(f"  - CAPEX: {context['finance']['capex']['total'] / 1e8:.2f}억원")
    print(f"  - NPV (Public): {context['finance']['npv']['public'] / 1e8:+.2f}억원")
    print(f"  - IRR: {context['finance']['irr']['public']:.2f}%")
    print(f"  - Decision: {context['decision']['recommendation']}")
    print(f"  - Overall Risk: {context['risk_analysis']['overall_level']}")
    print(f"\n📁 Output Files:")
    print(f"  - HTML: {html_output_path}")
    print(f"  - PDF: {output_path} ({file_size / 1024:.1f} KB)")
    print("\n" + "=" * 80)
    
    return output_path


if __name__ == "__main__":
    # Test with Gangnam address
    address = "서울시 강남구 역삼동 123"
    land_area_sqm = 500.0
    coordinates = (37.5013, 127.0374)  # Gangnam coordinates
    
    pdf_path = generate_full_edition_pdf(
        address=address,
        land_area_sqm=land_area_sqm,
        coordinates=coordinates
    )
    
    if pdf_path:
        print(f"\n✅ SUCCESS! PDF ready at: {pdf_path}")
    else:
        print(f"\n❌ FAILED! Check errors above.")
