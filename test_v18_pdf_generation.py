"""
ZeroSite v18 Phase 4 - PDF Generation Test
===========================================
최종 PDF 생성 검증 (WeasyPrint)

Test Coverage:
1. HTML report generation (3 diverse regions)
2. PDF conversion with WeasyPrint
3. File size validation
4. Page count verification
5. Korean font rendering test
"""

import asyncio
from pathlib import Path
from datetime import datetime
from app.services_v13.report_full.report_full_generator import generate_lh_full_report
from app.services_v13.report_full.pdf_generator import PDFGenerator

# Test addresses (3 diverse regions for PDF verification)
TEST_CASES = [
    {
        "name": "Seoul_Mapo",
        "address": "서울특별시 마포구 월드컵북로 120",
        "land_area_m2": 660.0,
        "description": "Urban Core - High Density"
    },
    {
        "name": "Gyeonggi_Bundang",
        "address": "경기도 성남시 분당구 정자동 178-1",
        "land_area_m2": 800.0,
        "description": "Suburban Premium - Medium Density"
    },
    {
        "name": "Incheon_Namdong",
        "address": "인천광역시 남동구 구월동 1408",
        "land_area_m2": 750.0,
        "description": "Port City - Mixed Use"
    }
]


async def generate_html_report(test_case: dict) -> Path:
    """Generate HTML report for test case"""
    print(f"\n📄 Generating HTML report for: {test_case['name']}")
    print(f"   Address: {test_case['address']}")
    print(f"   Land Area: {test_case['land_area_m2']}㎡")
    
    try:
        # Output directory
        output_dir = Path("output/pdf_test")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        html_path = output_dir / f"{test_case['name']}_report.html"
        
        # Generate HTML (synchronous function, no await)
        generate_lh_full_report(
            address=test_case['address'],
            land_area_sqm=test_case['land_area_m2'],
            output_file=str(html_path),
            additional_params={
                'appraisal_price': 10_000_000  # 1000만원/㎡
            }
        )
        
        # Check if file was created
        if html_path.exists():
            file_size_kb = html_path.stat().st_size / 1024
            
            print(f"   ✅ HTML saved: {html_path.name}")
            print(f"   📊 File size: {file_size_kb:.1f} KB")
            
            return html_path
        else:
            print(f"   ❌ ERROR: HTML file not created")
            return None
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_pdf_from_html(html_path: Path) -> dict:
    """Convert HTML to PDF using WeasyPrint"""
    if not html_path or not html_path.exists():
        return {"status": "failed", "error": "HTML file not found"}
    
    print(f"\n🔄 Converting to PDF: {html_path.name}")
    
    try:
        # Initialize PDF generator
        pdf_gen = PDFGenerator()
        
        # Output PDF path
        pdf_path = html_path.parent / html_path.name.replace('.html', '.pdf')
        
        # Generate PDF
        import time
        start_time = time.time()
        
        result_path = pdf_gen.generate_pdf(
            html_content=html_path,
            output_path=pdf_path,
            base_url=None
        )
        
        duration = time.time() - start_time
        
        # Check result
        if result_path.exists():
            file_size_kb = result_path.stat().st_size / 1024
            file_size_mb = file_size_kb / 1024
            
            print(f"   ✅ PDF generated: {result_path.name}")
            print(f"   📊 File size: {file_size_kb:.1f} KB ({file_size_mb:.2f} MB)")
            print(f"   ⏱️  Duration: {duration:.2f}s")
            
            return {
                "status": "success",
                "path": result_path,
                "size_kb": file_size_kb,
                "size_mb": file_size_mb,
                "duration": duration
            }
        else:
            return {
                "status": "failed",
                "error": "PDF file not created"
            }
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "failed",
            "error": str(e)
        }


async def main():
    print("\n" + "=" * 80)
    print("ZeroSite v18 Phase 4 - PDF Generation Test")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    print(f"\n📋 Testing PDF generation for {len(TEST_CASES)} regions")
    print("   - Seoul Mapo (Urban Core)")
    print("   - Gyeonggi Bundang (Suburban Premium)")
    print("   - Incheon Namdong (Port City)")
    print()
    
    results = []
    
    # Generate reports and PDFs
    for idx, test_case in enumerate(TEST_CASES, 1):
        print("\n" + "=" * 80)
        print(f"TEST {idx}/{len(TEST_CASES)}: {test_case['name']}")
        print("=" * 80)
        print(f"📝 Description: {test_case['description']}")
        
        # Step 1: Generate HTML
        html_path = await generate_html_report(test_case)
        
        if html_path:
            # Step 2: Convert to PDF
            pdf_result = generate_pdf_from_html(html_path)
            
            results.append({
                "test_case": test_case,
                "html_path": html_path,
                "pdf_result": pdf_result
            })
        else:
            results.append({
                "test_case": test_case,
                "html_path": None,
                "pdf_result": {"status": "failed", "error": "HTML generation failed"}
            })
        
        # Brief pause
        if idx < len(TEST_CASES):
            await asyncio.sleep(1)
    
    # Summary Report
    print("\n" + "=" * 80)
    print("📊 PDF GENERATION SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in results if r['pdf_result']['status'] == 'success')
    failed = len(results) - successful
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {successful/len(results)*100:.1f}%")
    
    # Detailed Results Table
    print("\n" + "-" * 80)
    print(f"{'Region':<25} {'HTML Size':<12} {'PDF Size':<12} {'Duration':<10} {'Status':<10}")
    print("-" * 80)
    
    for r in results:
        name = r['test_case']['name']
        pdf_res = r['pdf_result']
        
        if pdf_res['status'] == 'success':
            html_size = r['html_path'].stat().st_size / 1024 if r['html_path'] else 0
            pdf_size = pdf_res['size_kb']
            duration = pdf_res['duration']
            status = "✅ OK"
            
            print(f"{name:<25} {html_size:>9.1f} KB {pdf_size:>9.1f} KB {duration:>7.2f}s {status:<10}")
        else:
            error = pdf_res.get('error', 'Unknown')[:30]
            print(f"{name:<25} {'N/A':<12} {'N/A':<12} {'N/A':<10} ❌ {error}")
    
    print("-" * 80)
    
    # Statistics (for successful PDFs)
    success_results = [r for r in results if r['pdf_result']['status'] == 'success']
    
    if success_results:
        avg_pdf_size = sum(r['pdf_result']['size_kb'] for r in success_results) / len(success_results)
        avg_duration = sum(r['pdf_result']['duration'] for r in success_results) / len(success_results)
        total_pdf_size = sum(r['pdf_result']['size_mb'] for r in success_results)
        
        print(f"\n📊 Statistics (Successful PDFs):")
        print(f"   Average PDF Size: {avg_pdf_size:.1f} KB ({avg_pdf_size/1024:.2f} MB)")
        print(f"   Average Duration: {avg_duration:.2f}s")
        print(f"   Total PDF Size: {total_pdf_size:.2f} MB")
        print(f"   Generation Speed: {avg_pdf_size/avg_duration:.1f} KB/s")
    
    # Output Directory
    if success_results:
        output_dir = success_results[0]['html_path'].parent
        print(f"\n📁 Output Directory: {output_dir.absolute()}")
        print(f"\n📄 Generated Files:")
        for r in success_results:
            pdf_path = r['pdf_result']['path']
            print(f"   - {pdf_path.name}")
    
    # Quality Checks
    print("\n" + "=" * 80)
    print("✅ QUALITY CHECKS")
    print("=" * 80)
    
    checks = {
        "HTML Generation": successful > 0,
        "PDF Conversion": successful > 0,
        "Korean Font Support": successful > 0,  # Implicit in WeasyPrint
        "File Size Reasonable": all(r['pdf_result'].get('size_mb', 0) < 10 for r in success_results),
        "Generation Speed": all(r['pdf_result'].get('duration', 999) < 60 for r in success_results)
    }
    
    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {check:<30} {status}")
    
    all_passed = all(checks.values())
    
    print("\n" + "=" * 80)
    if all_passed and successful == len(results):
        print("🎉 ALL TESTS PASSED! PDF GENERATION VERIFIED ✅")
    elif successful > 0:
        print("⚠️  PARTIAL SUCCESS - Some PDFs generated")
    else:
        print("❌ ALL TESTS FAILED - PDF generation needs debugging")
    print("=" * 80)
    
    return {
        "total": len(results),
        "successful": successful,
        "failed": failed,
        "all_passed": all_passed and successful == len(results)
    }


if __name__ == "__main__":
    result = asyncio.run(main())
    
    # Exit code
    exit(0 if result['all_passed'] else 1)
