"""
PDF Generation using Playwright (Alternative to WeasyPrint)
============================================================
Use Playwright's headless Chrome for PDF generation
"""

from pathlib import Path
import asyncio
import time

# Test if Playwright is available
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

HTML_FILES = [
    "output/v17_FINAL_TEST.html",
    "output/v16_COMPLETE.html",
]


async def generate_pdf_with_playwright(html_path: Path) -> dict:
    """Generate PDF using Playwright"""
    if not html_path.exists():
        return {"status": "failed", "error": "HTML file not found"}
    
    print(f"\n📄 Converting: {html_path.name}")
    
    pdf_path = html_path.parent / html_path.name.replace('.html', '.pdf')
    
    try:
        start_time = time.time()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Load HTML file
            await page.goto(f"file://{html_path.absolute()}")
            
            # Wait for page to fully load
            await page.wait_for_load_state('networkidle')
            
            # Generate PDF
            await page.pdf(
                path=str(pdf_path),
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
        
        duration = time.time() - start_time
        
        if pdf_path.exists():
            file_size_kb = pdf_path.stat().st_size / 1024
            file_size_mb = file_size_kb / 1024
            
            print(f"   ✅ PDF created: {pdf_path.name}")
            print(f"   📊 Size: {file_size_kb:.1f} KB ({file_size_mb:.2f} MB)")
            print(f"   ⏱️  Duration: {duration:.2f}s")
            
            return {
                "status": "success",
                "path": pdf_path,
                "size_kb": file_size_kb,
                "duration": duration
            }
        else:
            return {"status": "failed", "error": "PDF not created"}
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return {"status": "failed", "error": str(e)}


async def main():
    print("\n" + "=" * 80)
    print("🎭 PDF Generation Test - Using Playwright")
    print("=" * 80)
    
    if not PLAYWRIGHT_AVAILABLE:
        print("\n❌ Playwright not available")
        print("Install with: pip install playwright && playwright install chromium")
        return False
    
    print("\n✅ Playwright is available")
    print(f"📋 Testing {len(HTML_FILES)} HTML files\n")
    
    results = []
    
    for html_file in HTML_FILES:
        html_path = Path(html_file)
        
        if not html_path.exists():
            print(f"❌ File not found: {html_file}")
            results.append({"status": "failed", "html": html_file, "error": "File not found"})
            continue
        
        result = await generate_pdf_with_playwright(html_path)
        result['html'] = html_path.name
        results.append(result)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 CONVERSION SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = len(results) - successful
    
    print(f"\nTotal Files: {len(results)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    
    if successful > 0:
        print("\n" + "-" * 80)
        print(f"{'HTML File':<40} {'PDF Size':<15} {'Duration':<12}")
        print("-" * 80)
        
        for r in results:
            if r['status'] == 'success':
                print(f"{r['html']:<40} {r['size_kb']:>10.1f} KB {r['duration']:>9.2f}s")
        
        print("-" * 80)
        
        avg_size = sum(r['size_kb'] for r in results if r['status'] == 'success') / successful
        avg_duration = sum(r['duration'] for r in results if r['status'] == 'success') / successful
        
        print(f"\n📊 Average PDF Size: {avg_size:.1f} KB ({avg_size/1024:.2f} MB)")
        print(f"⏱️  Average Duration: {avg_duration:.2f}s")
    
    print("\n" + "=" * 80)
    if successful == len(results):
        print("🎉 ALL PDF CONVERSIONS SUCCESSFUL! ✅")
    elif successful > 0:
        print(f"⚠️  PARTIAL SUCCESS: {successful}/{len(results)} PDFs created")
    else:
        print("❌ ALL CONVERSIONS FAILED")
    print("=" * 80 + "\n")
    
    return successful > 0


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
