"""
Simple PDF Conversion Test
Convert existing HTML reports to PDF
"""

from pathlib import Path
from app.services_v13.report_full.pdf_generator import PDFGenerator
import time

# Test with existing HTML files
HTML_FILES = [
    "output/v17_FINAL_TEST.html",
    "output/v16_COMPLETE.html",
    "output/v15_phase2_마포구_COMPLETE.html"
]

def test_pdf_conversion():
    print("\n" + "=" * 80)
    print("🔄 PDF Conversion Test - Using Existing HTML Files")
    print("=" * 80 + "\n")
    
    pdf_gen = PDFGenerator()
    results = []
    
    for html_file in HTML_FILES:
        html_path = Path(html_file)
        
        if not html_path.exists():
            print(f"❌ File not found: {html_file}")
            continue
        
        print(f"📄 Converting: {html_path.name}")
        
        # PDF output path
        pdf_path = html_path.parent / html_path.name.replace('.html', '.pdf')
        
        try:
            start_time = time.time()
            
            result = pdf_gen.generate_pdf(
                html_content=html_path,
                output_path=pdf_path
            )
            
            duration = time.time() - start_time
            
            if result.exists():
                file_size_kb = result.stat().st_size / 1024
                file_size_mb = file_size_kb / 1024
                
                print(f"   ✅ PDF created: {result.name}")
                print(f"   📊 Size: {file_size_kb:.1f} KB ({file_size_mb:.2f} MB)")
                print(f"   ⏱️  Duration: {duration:.2f}s\n")
                
                results.append({
                    "status": "success",
                    "html": html_path.name,
                    "pdf": result.name,
                    "size_kb": file_size_kb,
                    "duration": duration
                })
            else:
                print(f"   ❌ PDF not created\n")
                results.append({
                    "status": "failed",
                    "html": html_path.name,
                    "error": "PDF not created"
                })
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}\n")
            results.append({
                "status": "failed",
                "html": html_path.name,
                "error": str(e)
            })
    
    # Summary
    print("=" * 80)
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
    
    return successful == len(results)

if __name__ == "__main__":
    success = test_pdf_conversion()
    exit(0 if success else 1)
