"""
Complete ZeroSite v7.2 PDF Report Test
Tests full pipeline: Analysis → Mapping → HTML → PDF
"""

import sys
import os
import asyncio
from datetime import datetime

sys.path.insert(0, '/home/user/webapp')

from app.services.analysis_engine import AnalysisEngine
from app.schemas import LandAnalysisRequest
from app.services.report_field_mapper_v7_2_complete import ReportFieldMapperV72Complete
from app.services.lh_report_generator_v7_2 import LHReportGeneratorV72


async def test_complete_pdf_generation():
    """Test complete PDF generation pipeline"""
    
    print("="*80)
    print("ZeroSite v7.2 Complete PDF Report Test")
    print("="*80)
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    # Test parameters
    test_address = "월드컵북로 120"
    test_land_area = 660.0
    test_unit_type = "청년"
    
    print(f"Test Parameters:")
    print(f"  Address: {test_address}")
    print(f"  Land Area: {test_land_area}㎡")
    print(f"  Unit Type: {test_unit_type}\n")
    
    # Step 1: Run analysis
    print("="*80)
    print("STEP 1: Running Land Analysis with v7.2 Engine")
    print("="*80)
    
    try:
        engine = AnalysisEngine()
        request = LandAnalysisRequest(
            address=test_address,
            land_area=test_land_area,
            user_type=test_unit_type
        )
        analysis_result = await engine.analyze_land(request)
        print("\n✅ Analysis completed successfully\n")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        return 1
    
    # Step 2: Map to v7.2 fields
    print("="*80)
    print("STEP 2: Mapping to v7.2 Fields")
    print("="*80)
    
    try:
        mapper = ReportFieldMapperV72Complete()
        report_data = mapper.map_analysis_output_to_report(analysis_result)
        print(f"\n✅ Field mapping completed")
        print(f"   Sections mapped: {len(report_data.keys())}\n")
    except Exception as e:
        print(f"\n❌ Field mapping failed: {e}")
        return 1
    
    # Step 3: Generate HTML Report
    print("="*80)
    print("STEP 3: Generating HTML Report (v7.2)")
    print("="*80)
    
    try:
        lh_generator = LHReportGeneratorV72()
        html_report = lh_generator.generate_html_report(report_data)
        
        # Save HTML
        html_path = '/tmp/complete_lh_report_v7_2.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        html_size = len(html_report)
        print(f"\n✅ HTML Report generated successfully")
        print(f"   File: {html_path}")
        print(f"   Size: {html_size:,} bytes ({html_size/1024:.1f} KB)\n")
        
    except Exception as e:
        print(f"\n❌ HTML Report generation failed: {e}")
        return 1
    
    # Step 4: Generate PDF Report
    print("="*80)
    print("STEP 4: Generating PDF Report (v7.2)")
    print("="*80)
    
    try:
        pdf_path = '/tmp/complete_lh_report_v7_2.pdf'
        result = lh_generator.generate_pdf_report(report_data, pdf_path)
        
        if result['success']:
            print(f"\n✅ PDF Report generated successfully")
            print(f"   File: {result['file_path']}")
            print(f"   Size: {result['file_size']:,} bytes ({result['file_size']/1024:.1f} KB)")
            print(f"   Generated at: {result['generated_at']}\n")
        else:
            print(f"\n❌ PDF generation failed: {result.get('error')}")
            return 1
            
    except Exception as e:
        print(f"\n❌ PDF generation exception: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 5: Validate PDF Content
    print("="*80)
    print("STEP 5: Validating PDF Content")
    print("="*80)
    
    validation_checks = []
    
    # Check 1: File size reasonable (>50KB for comprehensive report)
    if result['file_size'] > 50000:
        print(f"   ✅ CHECK 1: PDF file size reasonable ({result['file_size']:,} bytes)")
        validation_checks.append(True)
    else:
        print(f"   ❌ CHECK 1: PDF file size too small ({result['file_size']:,} bytes)")
        validation_checks.append(False)
    
    # Check 2: HTML contains v7.2 markers
    v7_2_markers = html_report.count('v7.2') + html_report.count('v3.1') + html_report.count('v2025')
    if v7_2_markers >= 10:
        print(f"   ✅ CHECK 2: v7.2 version markers present ({v7_2_markers} occurrences)")
        validation_checks.append(True)
    else:
        print(f"   ❌ CHECK 2: Not enough v7.2 markers ({v7_2_markers})")
        validation_checks.append(False)
    
    # Check 3: NO 5.0 scale system
    if '5.0 만점' not in html_report and '5점 만점' not in html_report:
        print(f"   ✅ CHECK 3: NO 5.0 scale system found")
        validation_checks.append(True)
    else:
        print(f"   ❌ CHECK 3: 5.0 scale system still present")
        validation_checks.append(False)
    
    # Check 4: Radar chart present
    if 'radar' in html_report.lower() or 'data:image/png;base64' in html_report:
        print(f"   ✅ CHECK 4: Radar chart present")
        validation_checks.append(True)
    else:
        print(f"   ❌ CHECK 4: Radar chart missing")
        validation_checks.append(False)
    
    # Check 5: NO dummy population
    if '500,000' not in html_report and '500000' not in html_report:
        print(f"   ✅ CHECK 5: NO dummy population data")
        validation_checks.append(True)
    else:
        print(f"   ❌ CHECK 5: Dummy population data present")
        validation_checks.append(False)
    
    # Check 6: S/A/B/C/D grading
    grade_count = html_report.count('score-') + html_report.count('등급')
    if grade_count >= 10:
        print(f"   ✅ CHECK 6: S/A/B/C/D grading present ({grade_count} occurrences)")
        validation_checks.append(True)
    else:
        print(f"   ❌ CHECK 6: Grading insufficient ({grade_count})")
        validation_checks.append(False)
    
    # Check 7: Risk score displayed
    if '/20점' in html_report or '/20' in html_report:
        print(f"   ✅ CHECK 7: Risk score displayed")
        validation_checks.append(True)
    else:
        print(f"   ❌ CHECK 7: Risk score not displayed")
        validation_checks.append(False)
    
    # Check 8: ZeroSite branding
    zerosite_count = html_report.count('ZeroSite') + html_report.count('zerosite')
    if zerosite_count >= 3:
        print(f"   ✅ CHECK 8: ZeroSite branding present ({zerosite_count} occurrences)")
        validation_checks.append(True)
    else:
        print(f"   ❌ CHECK 8: ZeroSite branding insufficient")
        validation_checks.append(False)
    
    # Check 9: 23 zoning fields
    if '23 fields' in html_report or '23개 필드' in html_report:
        print(f"   ✅ CHECK 9: 23 zoning fields declared")
        validation_checks.append(True)
    else:
        print(f"   ❌ CHECK 9: 23 zoning fields not declared")
        validation_checks.append(False)
    
    # Check 10: GeoOptimizer alternatives
    if '대안 후보지' in html_report or 'Alternative' in html_report:
        print(f"   ✅ CHECK 10: GeoOptimizer alternatives present")
        validation_checks.append(True)
    else:
        print(f"   ❌ CHECK 10: GeoOptimizer alternatives missing")
        validation_checks.append(False)
    
    print()
    
    # Final Summary
    print("="*80)
    print("FINAL VALIDATION SUMMARY")
    print("="*80)
    
    passed_count = sum(validation_checks)
    total_count = len(validation_checks)
    pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\nResults: {passed_count}/{total_count} checks passed ({pass_rate:.1f}%)\n")
    
    print(f"📄 Generated Files:")
    print(f"   HTML: /tmp/complete_lh_report_v7_2.html ({html_size/1024:.1f} KB)")
    print(f"   PDF:  /tmp/complete_lh_report_v7_2.pdf ({result['file_size']/1024:.1f} KB)\n")
    
    if passed_count == total_count:
        print("🎉 ALL VALIDATION CHECKS PASSED - PDF GENERATION COMPLETE")
        print("="*80)
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED - REVIEW REQUIRED")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_complete_pdf_generation())
    sys.exit(exit_code)
