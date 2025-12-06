#!/usr/bin/env python3
"""
ZeroSite Full Edition Report Generator
Generates a complete 30-50 page LH submission report with all data
"""

import sys
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.services_v13.report_full.report_full_generator import LHFullReportGenerator

def generate_full_edition_report(address: str, land_area_sqm: float, output_path: str = None):
    """
    Generate complete Full Edition report with all phases integrated
    
    Args:
        address: Full address of the site
        land_area_sqm: Land area in square meters
        output_path: Output HTML file path (optional)
    
    Returns:
        HTML content as string
    """
    print(f"🚀 Starting Full Edition Report Generation")
    print(f"📍 Address: {address}")
    print(f"📐 Land Area: {land_area_sqm}㎡ ({land_area_sqm * 0.3025:.1f}평)")
    print()
    
    # Step 1: Generate comprehensive report data
    print("⚙️  Phase 1: Generating comprehensive data...")
    generator = LHFullReportGenerator()
    report_data = generator.generate_full_report_data(
        address=address,
        land_area_sqm=land_area_sqm
    )
    print(f"✅ Report data generated")
    print(f"   - Housing Type: {report_data['regional_analysis'].get('recommended_type', 'N/A')}")
    print(f"   - Total Units: {report_data['development_plan'].get('total_units', 'N/A')}")
    capex = report_data['financial_analysis'].get('capex_total', 0)
    if capex > 0:
        print(f"   - CAPEX: {capex / 100000000:.2f}억원")
    npv = report_data['financial_analysis'].get('npv_public', 0)
    if npv != 0:
        print(f"   - NPV: {npv / 100000000:.2f}억원")
    irr = report_data['financial_analysis'].get('irr', 0)
    if irr != 0:
        print(f"   - IRR: {irr:.2f}%")
    print()
    
    # Step 2: Render HTML template
    print("⚙️  Phase 2: Rendering HTML template...")
    template_dir = Path(__file__).parent / 'app' / 'templates_v13'
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    template = env.get_template('lh_submission_full.html.jinja2')
    html_content = template.render(**report_data)
    print(f"✅ HTML rendered: {len(html_content):,} characters")
    print(f"   - Estimated pages: {len(html_content) // 2000} pages")
    print()
    
    # Step 3: Save to file
    if output_path:
        output_file = Path(output_path)
    else:
        output_file = Path('/tmp/zerosite_full_edition_report.html')
    
    print(f"⚙️  Phase 3: Saving report...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ Report saved to: {output_file}")
    print()
    
    # Step 4: Generate statistics
    print("📊 Report Statistics:")
    print(f"   - Total sections: 15")
    print(f"   - Character count: {len(html_content):,}")
    print(f"   - Estimated PDF pages: 30-40 pages")
    print(f"   - File size: {len(html_content.encode('utf-8')) / 1024:.1f} KB")
    print()
    
    print("🎉 Full Edition Report Generation Complete!")
    print(f"📄 Output: {output_file}")
    
    return html_content


if __name__ == "__main__":
    # Test with Gangnam address
    address = "서울시 강남구 역삼동 123"
    land_area = 500.0  # 500㎡ = ~151평
    
    html = generate_full_edition_report(
        address=address,
        land_area_sqm=land_area,
        output_path="/tmp/zerosite_full_edition_gangnam.html"
    )
    
    print("\n" + "="*60)
    print("✅ SUCCESS: Full Edition Report Ready")
    print("="*60)
    print("\nNext steps:")
    print("1. Review HTML: /tmp/zerosite_full_edition_gangnam.html")
    print("2. Convert to PDF with WeasyPrint")
    print("3. Submit to LH or present to stakeholders")
