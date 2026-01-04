#!/usr/bin/env python3
"""
Convert HTML reports to PDF using WeasyPrint
"""
import os
import sys
from weasyprint import HTML, CSS
from pathlib import Path

def convert_html_to_pdf(html_path: str, output_path: str = None):
    """Convert HTML file to PDF"""
    if not os.path.exists(html_path):
        print(f"❌ Error: HTML file not found: {html_path}")
        return False
    
    # Generate output path if not provided
    if output_path is None:
        output_path = html_path.replace('.html', '.pdf')
    
    try:
        print(f"📄 Converting: {html_path}")
        print(f"📝 Output: {output_path}")
        
        # Convert HTML to PDF
        html = HTML(filename=html_path)
        html.write_pdf(target=output_path)
        
        # Check file size
        size_kb = os.path.getsize(output_path) / 1024
        print(f"✅ PDF Generated: {size_kb:.2f} KB")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Get report directory
    reports_dir = Path(__file__).parent / "generated_reports"
    
    # Get latest M2, M3, M4 reports
    reports = {
        'M2': list(reports_dir.glob('M2_Classic_202512*_*.html')),
        'M3': list(reports_dir.glob('M3_SupplyType_202512*_*.html')),
        'M4': list(reports_dir.glob('M4_BuildingScale_202512*_*.html')),
    }
    
    print("=" * 80)
    print("🏗️ HTML TO PDF CONVERTER")
    print("=" * 80)
    
    converted = 0
    for module, files in reports.items():
        if not files:
            print(f"⚠️ No {module} reports found")
            continue
        
        # Get the latest file
        latest = max(files, key=os.path.getmtime)
        print(f"\n📋 {module} Report:")
        
        if convert_html_to_pdf(str(latest)):
            converted += 1
    
    print("\n" + "=" * 80)
    print(f"🎉 Conversion Complete: {converted} PDFs generated")
    print("=" * 80)
