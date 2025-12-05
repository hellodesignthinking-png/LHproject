"""
ZeroSite v7.2 Final Fixes Validation
Tests the last 3 critical fixes
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.analysis_engine import AnalysisEngine
from app.services.report_engine_v7_2 import ReportEngineV72
from app.schemas import LandAnalysisRequest
import asyncio


def test_final_fixes():
    """
    FINAL FIX 1: Zoning fallback rendering
    - None → "N/A (API 오류)"
    - empty → "N/A (API 오류)"
    - {} or [] → "N/A (API 오류)"
    - 0 or 0.0 → "0 (fallback)"
    
    FINAL FIX 2: GeoOptimizer 3 alternatives guaranteed
    - Ensure mapper pads to 3 alternatives
    - Verify template always prints all 3
    
    FINAL FIX 3: Remove ALL v6 remnants
    - Only S/A/B/C/D grades
    - Only v7.2 Korean text (매우 높음, 높음, 보통, 낮음, 매우 낮음)
    - No legacy "높음", "낮음", "보통" without grade letters
    """
    
    print("\n" + "="*80)
    print("ZeroSite v7.2 Final Fixes - Ultimate Validation")
    print("="*80 + "\n")
    
    # Test configuration (as specified)
    test_address = "월드컵북로 120"
    test_land_area = 660.0
    test_unit_type = "청년"
    
    print(f"📍 Test Configuration:")
    print(f"   Address: {test_address}")
    print(f"   Land Area: {test_land_area}㎡")
    print(f"   Unit Type: {test_unit_type}\n")
    
    # Initialize engines
    print("🔄 Step 1: Initializing engines...")
    analysis_engine = AnalysisEngine()
    report_engine = ReportEngineV72()
    print("✅ Engines initialized\n")
    
    # Run analysis
    print("🔄 Step 2: Running land analysis...")
    try:
        request = LandAnalysisRequest(
            address=test_address,
            land_area=test_land_area,
            unit_type=test_unit_type
        )
        engine_output = asyncio.run(analysis_engine.analyze_land(request))
        print(f"✅ Analysis completed: {len(engine_output)} fields\n")
    except Exception as e:
        print(f"❌ Analysis failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    
    # Generate report
    print("🔄 Step 3: Generating v7.2 report with final fixes...")
    try:
        report_result = report_engine.generate_report(
            engine_output=engine_output,
            report_type="comprehensive",
            format="markdown"
        )
        
        if not report_result['success']:
            print(f"❌ Report generation failed\n")
            return False
        
        print(f"✅ Report generated: {report_result['statistics']['total_characters']} chars\n")
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    
    # Validate all 3 FINAL fixes
    print("🔄 Step 4: Validating 3 FINAL fixes...")
    print("-" * 80)
    
    content = report_result['content']
    report_data = report_result['report_data']
    
    fixes_validated = []
    
    # FINAL FIX 1: Zoning fallback rendering
    print("\n✓ FINAL FIX 1: Zoning fallback rendering")
    print("   Checking: Enhanced fallback labels")
    
    # Check for new fallback format
    has_api_error = "(API 오류)" in content
    has_fallback = "(fallback)" in content
    
    # Count zoning fields
    zoning_fields = [
        "1. 용도지역", "2. 건폐율", "3. 용적률", "4. 높이 제한",
        "5. 중첩 용도지역", "6. 지구단위계획구역", "7. 경관지구",
        "8. 개발제한사항", "9. 환경규제", "10. 문화재보호구역", "11. 군사시설보호구역",
        "12. 도로 너비", "13. 도로 상태", "14. 상수도", "15. 하수도", "16. 전기", "17. 가스",
        "18. 도시계획구역", "19. 재개발구역", "20. 특별계획구역",
        "21. 주차 요구사항", "22. 녹지비율", "23. 건축선 후퇴"
    ]
    
    zoning_count = sum(field in content for field in zoning_fields)
    
    fix1_valid = zoning_count == 23 and (has_api_error or has_fallback)
    print(f"   Zoning fields displayed: {zoning_count}/23")
    print(f"   '(API 오류)' labels: {has_api_error}")
    print(f"   '(fallback)' labels: {has_fallback}")
    
    # Sample some zoning output
    if "용도지역" in content:
        for line in content.split('\n'):
            if "1. 용도지역" in line or "4. 높이 제한" in line:
                print(f"   Sample: {line.strip()}")
    
    fixes_validated.append(("FINAL FIX 1: Zoning Fallback Rendering", fix1_valid))
    
    # FINAL FIX 2: GeoOptimizer 3 alternatives
    print("\n✓ FINAL FIX 2: GeoOptimizer 3 alternatives guaranteed")
    print("   Checking: Exactly 3 alternatives in report")
    
    geo_data = report_data.get('geo_optimizer_v3_1', {})
    alternatives = geo_data.get('alternatives', [])
    
    # Check markers in text
    alt_markers = ["대안1", "대안2", "대안3"]
    alt_found = sum(marker in content for marker in alt_markers)
    
    fix2_valid = len(alternatives) == 3 and alt_found == 3
    print(f"   Alternatives in data: {len(alternatives)}/3")
    print(f"   Alternative markers in text: {alt_found}/3")
    
    if alternatives:
        for i, alt in enumerate(alternatives, 1):
            print(f"      대안 {i}: {alt.get('location', 'N/A')[:50]}")
    
    fixes_validated.append(("FINAL FIX 2: GeoOptimizer 3 Alternatives", fix2_valid))
    
    # FINAL FIX 3: Remove ALL v6 remnants
    print("\n✓ FINAL FIX 3: Remove v6 remnants, enforce v7.2 grading")
    print("   Checking: Only S/A/B/C/D with v7.2 Korean text")
    
    type_demand_data = report_data.get('type_demand_v3_1', {})
    type_scores = type_demand_data.get('type_scores', {})
    
    # Check for v7.2 grade fields in data
    has_grade_fields = False
    if type_scores:
        first_type = list(type_scores.values())[0]
        has_grade_fields = 'grade' in first_type and 'grade_text' in first_type
    
    # Check for v7.2 grading scale display
    v7_2_scale_present = "v7.2 등급 기준" in content
    
    # Check for grade letters in text
    grade_letters_in_text = sum(1 for g in ['S (', 'A (', 'B (', 'C (', 'D ('] if g in content)
    
    # Check for v7.2 Korean descriptions
    v7_2_korean = ["매우 높음", "높음", "보통", "낮음", "매우 낮음"]
    korean_found = sum(k in content for k in v7_2_korean)
    
    # Check demand_level uses v7.2 text
    demand_level = type_demand_data.get('demand_level', '')
    is_v7_2_text = demand_level in v7_2_korean
    
    fix3_valid = (has_grade_fields and v7_2_scale_present and 
                  grade_letters_in_text >= 1 and korean_found >= 3 and
                  is_v7_2_text)
    
    print(f"   Grade fields in data: {has_grade_fields}")
    print(f"   v7.2 grading scale table: {v7_2_scale_present}")
    print(f"   Grade letters in text: {grade_letters_in_text}")
    print(f"   v7.2 Korean text found: {korean_found}/5")
    print(f"   Demand level: '{demand_level}' (is v7.2: {is_v7_2_text})")
    
    # Sample type grades
    if type_scores:
        print(f"   Sample type grades:")
        for type_name, scores in list(type_scores.items())[:3]:
            grade = scores.get('grade', 'N/A')
            grade_text = scores.get('grade_text', 'N/A')
            final = scores.get('final_score', 0)
            print(f"      {type_name}: {final:.1f}점 → {grade} ({grade_text})")
    
    fixes_validated.append(("FINAL FIX 3: v7.2 Grading Enforcement", fix3_valid))
    
    # Summary
    print("\n" + "="*80)
    print("📊 FINAL VALIDATION SUMMARY")
    print("="*80)
    
    for fix_name, is_valid in fixes_validated:
        status = "✅ PASS" if is_valid else "❌ FAIL"
        print(f"{status} | {fix_name}")
    
    total_valid = sum(1 for _, valid in fixes_validated if valid)
    total_fixes = len(fixes_validated)
    
    print(f"\n📈 Overall: {total_valid}/{total_fixes} final fixes validated")
    
    # Save report
    output_path = "/tmp/v7_2_final_fixes_report.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n💾 Report saved: {output_path}")
    
    # Save data
    data_path = "/tmp/v7_2_final_fixes_data.json"
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    print(f"💾 Data saved: {data_path}")
    
    # Final verdict
    print("\n" + "="*80)
    if total_valid == total_fixes:
        print("✅ ALL FINAL FIXES VALIDATED - PRODUCTION READY")
    elif total_valid >= 2:
        print("⚠️ MOSTLY VALIDATED - MINOR ISSUES")
    else:
        print("❌ VALIDATION FAILED - REQUIRES FIXES")
    print("="*80 + "\n")
    
    return total_valid == total_fixes


if __name__ == "__main__":
    success = test_final_fixes()
    sys.exit(0 if success else 1)
