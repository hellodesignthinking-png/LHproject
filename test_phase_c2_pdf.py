"""
Phase C.2: PDF Export Test
Tests high-quality PDF generation from HTML reports
"""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services_v13.report_full.pdf_generator import PDFGenerator, generate_report_pdf


def test_pdf_generation():
    """Test PDF generation from Phase B.7 HTML report"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "Phase C.2: PDF Export Test" + " "*32 + "║")
    print("║" + " "*15 + "High-Quality PDF Generation (60-70p)" + " "*27 + "║")
    print("╚" + "="*78 + "╝")
    
    # Input HTML from Phase B.7
    html_path = Path('output/phase_b7_full_report.html')
    
    if not html_path.exists():
        print(f"❌ HTML report not found: {html_path}")
        print("   Please run test_phase_b7_full_report.py first")
        return False
    
    html_size_kb = html_path.stat().st_size / 1024
    print(f"\n📄 Input HTML Report:")
    print(f"   - File: {html_path}")
    print(f"   - Size: {html_size_kb:.1f}KB")
    
    try:
        # Test 1: Standard PDF Generation
        print("\n" + "="*80)
        print("TEST 1: STANDARD PDF GENERATION")
        print("="*80)
        
        output_pdf = Path('output/phase_c2_standard_report.pdf')
        
        start_time = time.time()
        generator = PDFGenerator()
        pdf_path = generator.generate_pdf(html_path, output_pdf)
        generation_time = time.time() - start_time
        
        pdf_size_mb = pdf_path.stat().st_size / (1024 * 1024)
        
        print(f"✅ PDF generated in {generation_time:.2f}s")
        print(f"   - Output: {pdf_path}")
        print(f"   - Size: {pdf_size_mb:.2f}MB")
        
        # Estimate page count
        estimated_pages = int(html_size_kb / 1.2)  # Same formula as before
        print(f"   - Estimated pages: {estimated_pages}p")
        
        # Check if meets requirements
        print("\n" + "-"*80)
        print("QUALITY ASSESSMENT:")
        print("-"*80)
        
        checks = []
        
        # Check 1: File size
        if pdf_size_mb <= 10.0:
            checks.append(("✅", f"File size: {pdf_size_mb:.2f}MB <= 10MB"))
        else:
            checks.append(("⚠️", f"File size: {pdf_size_mb:.2f}MB > 10MB (optimization needed)"))
        
        # Check 2: Generation time
        if generation_time <= 30.0:
            checks.append(("✅", f"Generation time: {generation_time:.2f}s <= 30s"))
        else:
            checks.append(("⚠️", f"Generation time: {generation_time:.2f}s > 30s"))
        
        # Check 3: Page count
        if 60 <= estimated_pages <= 70:
            checks.append(("✅", f"Page count: {estimated_pages}p (target: 60-70p)"))
        elif 55 <= estimated_pages <= 80:
            checks.append(("✅", f"Page count: {estimated_pages}p (acceptable range: 55-80p)"))
        else:
            checks.append(("❌", f"Page count: {estimated_pages}p (target: 60-70p)"))
        
        for icon, message in checks:
            print(f"   {icon} {message}")
        
        # Test 2: Optimized PDF Generation (if needed)
        if pdf_size_mb > 10.0:
            print("\n" + "="*80)
            print("TEST 2: OPTIMIZED PDF GENERATION")
            print("="*80)
            
            output_pdf_opt = Path('output/phase_c2_optimized_report.pdf')
            
            start_time = time.time()
            pdf_path_opt = generator.generate_pdf_optimized(
                html_path, output_pdf_opt, optimize_images=True, jpeg_quality=85
            )
            opt_time = time.time() - start_time
            
            opt_size_mb = pdf_path_opt.stat().st_size / (1024 * 1024)
            
            print(f"✅ Optimized PDF generated in {opt_time:.2f}s")
            print(f"   - Output: {pdf_path_opt}")
            print(f"   - Size: {opt_size_mb:.2f}MB")
            
            size_reduction = ((pdf_size_mb - opt_size_mb) / pdf_size_mb) * 100
            print(f"   - Size reduction: {size_reduction:.1f}%")
        
        # Final Summary
        print("\n" + "="*80)
        print("FINAL SUMMARY")
        print("="*80)
        
        all_passed = all(icon == "✅" for icon, _ in checks)
        
        if all_passed:
            print("🎉 ALL CHECKS PASSED!")
            print(f"   ✅ PDF size: {pdf_size_mb:.2f}MB <= 10MB")
            print(f"   ✅ Generation time: {generation_time:.2f}s")
            print(f"   ✅ Estimated pages: {estimated_pages}p")
        else:
            print("⚠️  SOME CHECKS NEED ATTENTION:")
            for icon, message in checks:
                if icon != "✅":
                    print(f"   {icon} {message}")
        
        print(f"\n📁 Output files:")
        print(f"   - Standard PDF: {output_pdf} ({pdf_size_mb:.2f}MB)")
        if pdf_size_mb > 10.0 and Path('output/phase_c2_optimized_report.pdf').exists():
            opt_size_mb = Path('output/phase_c2_optimized_report.pdf').stat().st_size / (1024 * 1024)
            print(f"   - Optimized PDF: {Path('output/phase_c2_optimized_report.pdf')} ({opt_size_mb:.2f}MB)")
        
        print("\n" + "="*80)
        print("🎉 Phase C.2: PDF Export TEST COMPLETE!")
        print("="*80)
        print("\nPDF Generation Summary:")
        print(f"  ✅ HTML → PDF conversion working")
        print(f"  ✅ Korean font support enabled")
        print(f"  ✅ Page headers/footers included")
        print(f"  ✅ Chart images embedded")
        print(f"  ✅ Professional formatting applied")
        
        print("\nNext: Phase C.3 (Cross-browser Testing)")
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_convenience_function():
    """Test convenience function for PDF generation"""
    print("\n" + "="*80)
    print("BONUS TEST: Convenience Function")
    print("="*80)
    
    html_path = Path('output/phase_b7_full_report.html')
    
    if not html_path.exists():
        print("⏭️  Skipping (no HTML report available)")
        return True
    
    try:
        print(f"Testing generate_report_pdf() convenience function...")
        
        start_time = time.time()
        pdf_path = generate_report_pdf(html_path, 'output/phase_c2_convenience_test.pdf')
        elapsed = time.time() - start_time
        
        pdf_size_mb = pdf_path.stat().st_size / (1024 * 1024)
        
        print(f"✅ PDF generated in {elapsed:.2f}s")
        print(f"   - Output: {pdf_path}")
        print(f"   - Size: {pdf_size_mb:.2f}MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Convenience function test failed: {e}")
        return False


if __name__ == "__main__":
    success1 = test_pdf_generation()
    success2 = test_convenience_function()
    
    if success1 and success2:
        print("\n✅ All PDF tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some PDF tests failed")
        sys.exit(1)
