#!/usr/bin/env python3
"""
Convert HTML reports to PDF using Playwright
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def convert_html_to_pdf(html_path: str, output_path: str = None):
    """Convert HTML file to PDF using Playwright"""
    if not os.path.exists(html_path):
        print(f"❌ Error: HTML file not found: {html_path}")
        return False
    
    # Generate output path if not provided
    if output_path is None:
        output_path = html_path.replace('.html', '.pdf')
    
    try:
        print(f"📄 Converting: {Path(html_path).name}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Load HTML file
            await page.goto(f'file://{os.path.abspath(html_path)}')
            
            # Wait for content to load
            await page.wait_for_load_state('networkidle')
            
            # Generate PDF
            await page.pdf(
                path=output_path,
                format='A4',
                print_background=True,
                margin={
                    'top': '20mm',
                    'right': '15mm',
                    'bottom': '20mm',
                    'left': '15mm'
                }
            )
            
            await browser.close()
        
        # Check file size
        size_kb = os.path.getsize(output_path) / 1024
        print(f"✅ PDF Generated: {Path(output_path).name} ({size_kb:.2f} KB)")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    # Get report directory
    reports_dir = Path(__file__).parent / "generated_reports"
    
    # Get latest M2, M3, M4 reports
    reports = {
        'M2_토지감정평가': list(reports_dir.glob('M2_Classic_202512*_*.html')),
        'M3_LH선호유형': list(reports_dir.glob('M3_SupplyType_202512*_*.html')),
        'M4_건축규모': list(reports_dir.glob('M4_BuildingScale_202512*_*.html')),
    }
    
    print("=" * 80)
    print("🏗️ HTML TO PDF CONVERTER (Playwright)")
    print("=" * 80)
    
    converted = 0
    for module, files in reports.items():
        if not files:
            print(f"⚠️ No {module} reports found")
            continue
        
        # Get the latest file
        latest = max(files, key=os.path.getmtime)
        
        # Generate Korean filename for output
        output_name = f"{module}_보고서_최신_{Path(latest).stem.split('_')[-1]}.pdf"
        output_path = str(reports_dir / output_name)
        
        print(f"\n📋 {module} Report:")
        
        if await convert_html_to_pdf(str(latest), output_path):
            converted += 1
    
    print("\n" + "=" * 80)
    print(f"🎉 Conversion Complete: {converted} PDFs generated")
    print("=" * 80)
    
    # List generated PDFs
    print("\n📁 Generated PDFs:")
    for pdf in sorted(reports_dir.glob('*_최신_*.pdf')):
        size_kb = os.path.getsize(pdf) / 1024
        print(f"   - {pdf.name} ({size_kb:.2f} KB)")

if __name__ == "__main__":
    asyncio.run(main())
