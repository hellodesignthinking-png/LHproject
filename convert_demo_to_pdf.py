#!/usr/bin/env python3
"""
Convert demo endpoint HTML to PDF using pyppeteer
"""
import asyncio
import os
from pyppeteer import launch

async def html_to_pdf(html_content: str, output_path: str):
    """Convert HTML string to PDF"""
    browser = await launch(
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    page = await browser.newPage()
    
    # Set HTML content
    await page.setContent(html_content)
    
    # Generate PDF
    await page.pdf({
        'path': output_path,
        'format': 'A4',
        'printBackground': True,
        'margin': {
            'top': '20mm',
            'right': '15mm',
            'bottom': '20mm',
            'left': '15mm'
        }
    })
    
    await browser.close()
    
    # Check file size
    size_kb = os.path.getsize(output_path) / 1024
    return size_kb

async def main():
    reports = [
        ('M2_토지감정평가', '/tmp/m2_latest.html'),
        ('M3_공급유형', '/tmp/m3_latest.html'),
        ('M4_건축규모', '/tmp/m4_latest.html'),
        ('M5_사업성분석', '/tmp/m5_latest.html'),
        ('M6_종합판단', '/tmp/m6_latest.html'),
    ]
    
    print("=" * 80)
    print("🏗️ PDF CONVERTER - DEMO ENDPOINTS")
    print("=" * 80)
    
    output_dir = '/home/user/webapp/static/latest_reports'
    os.makedirs(output_dir, exist_ok=True)
    
    converted = []
    
    for name, html_path in reports:
        print(f"\n📋 {name}:")
        print(f"   Source: {html_path}")
        
        # Read HTML content
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Generate output path
        output_path = f"{output_dir}/{name}_최신_2025-12-29.pdf"
        print(f"   Output: {output_path}")
        
        try:
            size_kb = await html_to_pdf(html_content, output_path)
            print(f"   ✅ Success: {size_kb:.2f} KB")
            converted.append((name, output_path, size_kb))
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print(f"🎉 Conversion Complete: {len(converted)}/{len(reports)} PDFs")
    print("=" * 80)
    
    if converted:
        print("\n📁 Generated PDFs:")
        for name, path, size in converted:
            filename = os.path.basename(path)
            print(f"   - {filename} ({size:.2f} KB)")

if __name__ == "__main__":
    asyncio.run(main())
