"""
Simple HTML to PDF test (no backend dependency)
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def test_simple_html_to_pdf():
    """
    로컬 HTML 파일을 PDF로 변환하는 최소 테스트
    """
    print("\n" + "="*80)
    print("🚀 Simple HTML to PDF Test (No Backend)")
    print("="*80 + "\n")
    
    html_file = Path("/home/user/webapp/test_simple.html")
    pdf_file = Path("/home/user/webapp/test_simple.pdf")
    
    if not html_file.exists():
        print(f"❌ HTML file not found: {html_file}")
        return False
    
    print(f"📄 HTML File: {html_file}")
    print(f"📄 PDF Output: {pdf_file}")
    print()
    
    try:
        async with async_playwright() as p:
            print("⏳ Launching Chromium...")
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            
            print("⏳ Opening HTML file...")
            page = await browser.new_page()
            await page.goto(f"file://{html_file.absolute()}")
            
            print("⏳ Generating PDF...")
            await page.pdf(
                path=str(pdf_file),
                format="A4",
                print_background=True,
                display_header_footer=True,
                header_template='<div style="font-size:9px; text-align:center; width:100%;">ZeroSite Test Report</div>',
                footer_template='<div style="font-size:9px; text-align:center; width:100%;">Page <span class="pageNumber"></span></div>',
                margin={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"}
            )
            
            await browser.close()
            
            if pdf_file.exists():
                file_size = pdf_file.stat().st_size
                print(f"\n✅ PDF Generated Successfully!")
                print(f"   - Size: {file_size:,} bytes")
                print(f"   - Location: {pdf_file}")
                print()
                print("🎉 Task 1.1 완료: Playwright PDF 엔진 작동 확인!")
                return True
            else:
                print(f"❌ PDF file not created")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_simple_html_to_pdf())
    exit(0 if success else 1)
