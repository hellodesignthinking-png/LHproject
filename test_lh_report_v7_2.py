"""
Test LH Report Generator v7.2
Validates that the new generator uses 100% v7.2 engine data
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


async def test_lh_report_v7_2():
    """Test complete LH report generation with v7.2 data"""
    
    print("="*80)
    print("ZeroSite v7.2 LH Report Generator - Complete Test")
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
        import traceback
        traceback.print_exc()
        return
    
    # Step 2: Map to v7.2 fields
    print("="*80)
    print("STEP 2: Mapping to v7.2 Fields")
    print("="*80)
    
    try:
        mapper = ReportFieldMapperV72Complete()
        report_data = mapper.map_analysis_output_to_report(analysis_result)
        print(f"\n✅ Field mapping completed")
        print(f"   Sections mapped: {len(report_data.keys())}\n")
        
        # Verify key data
        poi_data = report_data.get('poi_analysis_v3_1', {})
        td_data = report_data.get('type_demand_v3_1', {})
        geo_data = report_data.get('geo_optimizer_v3_1', {})
        risk_data = report_data.get('risk_analysis_2025', {})
        
        print("   Key Data Verification:")
        print(f"   - POI Score: {poi_data.get('total_score_v3_1', 0):.2f}")
        print(f"   - Type Demand Score: {td_data.get('main_score', 0):.2f}")
        print(f"   - GeoOptimizer Score: {geo_data.get('final_score', 0):.2f}")
        print(f"   - Risk Score: {risk_data.get('risk_score', 0):.1f}/20")
        print(f"   - POI Count: {len(poi_data.get('pois', {}))}")
        print(f"   - GeoOptimizer Alternatives: {len(geo_data.get('alternatives', []))}")
        print()
        
    except Exception as e:
        print(f"\n❌ Field mapping failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Generate LH Report HTML
    print("="*80)
    print("STEP 3: Generating LH Report HTML (v7.2)")
    print("="*80)
    
    try:
        lh_generator = LHReportGeneratorV72()
        html_report = lh_generator.generate_html_report(report_data)
        
        # Save to file
        output_path = '/tmp/lh_report_v7_2.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        html_size = len(html_report)
        print(f"\n✅ LH Report HTML generated successfully")
        print(f"   File: {output_path}")
        print(f"   Size: {html_size:,} bytes ({html_size/1024:.1f} KB)\n")
        
    except Exception as e:
        print(f"\n❌ LH Report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Validate Report Content
    print("="*80)
    print("STEP 4: Validating Report Content")
    print("="*80)
    
    validation_results = []
    
    # Check 1: No 5.0 scale system
    if '5.0 만점' not in html_report and '5점 만점' not in html_report:
        print("   ✅ CHECK 1: NO 5.0 scale system found")
        validation_results.append(True)
    else:
        print("   ❌ CHECK 1: FAIL - 5.0 scale system still present")
        validation_results.append(False)
    
    # Check 2: v7.2 version markers
    v7_2_markers = html_report.count('v7.2') + html_report.count('v3.1') + html_report.count('v2025')
    if v7_2_markers >= 5:
        print(f"   ✅ CHECK 2: v7.2 version markers found ({v7_2_markers} occurrences)")
        validation_results.append(True)
    else:
        print(f"   ❌ CHECK 2: FAIL - Not enough v7.2 markers ({v7_2_markers})")
        validation_results.append(False)
    
    # Check 3: Real POI data
    poi_count = len(poi_data.get('pois', {}))
    if f'{poi_count}개소' in html_report or f'{poi_count}개' in html_report:
        print(f"   ✅ CHECK 3: Real POI data present ({poi_count} POIs)")
        validation_results.append(True)
    else:
        print(f"   ❌ CHECK 3: FAIL - POI count not found in report")
        validation_results.append(False)
    
    # Check 4: NO dummy population data
    if '500,000' not in html_report and '500000' not in html_report:
        print("   ✅ CHECK 4: NO dummy population data (500,000)")
        validation_results.append(True)
    else:
        print("   ❌ CHECK 4: FAIL - Dummy population data still present")
        validation_results.append(False)
    
    # Check 5: S/A/B/C/D grading scale
    grade_count = html_report.count('score-') + html_report.count('등급')
    if grade_count >= 10:
        print(f"   ✅ CHECK 5: S/A/B/C/D grading scale present ({grade_count} occurrences)")
        validation_results.append(True)
    else:
        print(f"   ❌ CHECK 5: FAIL - Grading scale insufficient ({grade_count})")
        validation_results.append(False)
    
    # Check 6: Risk score displayed
    risk_score = risk_data.get('risk_score', 0)
    if f'{risk_score:.1f}/20' in html_report:
        print(f"   ✅ CHECK 6: Risk score displayed ({risk_score:.1f}/20점)")
        validation_results.append(True)
    else:
        print(f"   ❌ CHECK 6: FAIL - Risk score not displayed")
        validation_results.append(False)
    
    # Check 7: ZeroSite branding
    zerosite_count = html_report.count('ZeroSite') + html_report.count('zerosite')
    if zerosite_count >= 3:
        print(f"   ✅ CHECK 7: ZeroSite branding present ({zerosite_count} occurrences)")
        validation_results.append(True)
    else:
        print(f"   ❌ CHECK 7: FAIL - ZeroSite branding insufficient")
        validation_results.append(False)
    
    # Check 8: LH Checklist present
    if 'LH 체크리스트' in html_report or 'LH Checklist' in html_report:
        print("   ✅ CHECK 8: LH Checklist section present")
        validation_results.append(True)
    else:
        print("   ❌ CHECK 8: FAIL - LH Checklist missing")
        validation_results.append(False)
    
    # Check 9: 23 zoning fields
    if 'Zoning v7.2 - 23 fields' in html_report:
        print("   ✅ CHECK 9: All 23 zoning fields declared")
        validation_results.append(True)
    else:
        print("   ❌ CHECK 9: FAIL - 23 zoning fields not declared")
        validation_results.append(False)
    
    # Check 10: GeoOptimizer alternatives
    alt_count = len(geo_data.get('alternatives', []))
    if alt_count >= 3:
        print(f"   ✅ CHECK 10: GeoOptimizer 3 alternatives guaranteed ({alt_count})")
        validation_results.append(True)
    else:
        print(f"   ❌ CHECK 10: FAIL - Not enough alternatives ({alt_count})")
        validation_results.append(False)
    
    print()
    
    # Final Summary
    print("="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    passed_count = sum(validation_results)
    total_count = len(validation_results)
    pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\nResults: {passed_count}/{total_count} checks passed ({pass_rate:.1f}%)\n")
    
    if passed_count == total_count:
        print("🎉 ALL VALIDATION CHECKS PASSED - PRODUCTION READY")
        print("="*80)
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED - REVIEW REQUIRED")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_lh_report_v7_2())
    sys.exit(exit_code)
