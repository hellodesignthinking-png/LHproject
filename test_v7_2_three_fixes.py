"""
ZeroSite v7.2 Three Critical Fixes Validation
Tests Fix 1, Fix 2, and Fix 3
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.analysis_engine import AnalysisEngine
from app.services.report_engine_v7_2 import ReportEngineV72
from app.schemas import LandAnalysisRequest
import asyncio


def test_three_fixes():
    """
    Test Fix 1: Zoning v7.2 fallback visibility (all 23 fields displayed)
    Test Fix 2: GeoOptimizer alternative 1~3 output (guaranteed 3 alternatives)
    Test Fix 3: Type Demand v7.2 grading enforcement (S/A/B/C/D with Korean text)
    """
    
    print("\n" + "="*80)
    print("ZeroSite v7.2 Three Critical Fixes - Validation Test")
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
    print("🔄 Step 3: Generating v7.2 report with 3 fixes...")
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
    
    # Validate all 3 fixes
    print("🔄 Step 4: Validating 3 critical fixes...")
    print("-" * 80)
    
    content = report_result['content']
    report_data = report_result['report_data']
    
    fixes_validated = []
    
    # FIX 1: Zoning v7.2 fallback visibility
    print("\n✓ FIX 1: Zoning v7.2 fallback visibility")
    print("   Checking: All 23 zoning fields displayed with explicit fallback/error labels")
    
    zoning_fields_numbered = [
        "1. 용도지역", "2. 건폐율", "3. 용적률", "4. 높이 제한",
        "5. 중첩 용도지역", "6. 지구단위계획구역", "7. 경관지구",
        "8. 개발제한사항", "9. 환경규제", "10. 문화재보호구역", "11. 군사시설보호구역",
        "12. 도로 너비", "13. 도로 상태", "14. 상수도", "15. 하수도", "16. 전기", "17. 가스",
        "18. 도시계획구역", "19. 재개발구역", "20. 특별계획구역",
        "21. 주차 요구사항", "22. 녹지비율", "23. 건축선 후퇴"
    ]
    
    # Check numbered fields
    zoning_count = sum(field in content for field in zoning_fields_numbered)
    
    # Check fallback labels
    fallback_indicators = ["**(fallback)**", "**(API 오류)**"]
    has_fallback_labels = any(indicator in content for indicator in fallback_indicators)
    
    fix1_valid = zoning_count == 23 and has_fallback_labels
    print(f"   Zoning fields found: {zoning_count}/23")
    print(f"   Fallback labels present: {has_fallback_labels}")
    print(f"   Numbered fields format: {'✓' if '1. 용도지역' in content else '✗'}")
    fixes_validated.append(("FIX 1: Zoning Fallback Visibility", fix1_valid))
    
    # FIX 2: GeoOptimizer alternative 1~3 output
    print("\n✓ FIX 2: GeoOptimizer alternative 1~3 output")
    print("   Checking: Guaranteed 3 alternatives in report")
    
    geo_data = report_data.get('geo_optimizer_v3_1', {})
    alternatives = geo_data.get('alternatives', [])
    
    # Check for alternative markers in text
    alt_markers = ["대안1", "대안 1", "대안2", "대안 2", "대안3", "대안 3"]
    alt_in_text = sum(marker in content for marker in alt_markers)
    
    fix2_valid = len(alternatives) == 3 and alt_in_text >= 3
    print(f"   Alternatives in data: {len(alternatives)}/3")
    print(f"   Alternative markers in text: {alt_in_text}/6 markers")
    if alternatives:
        for i, alt in enumerate(alternatives[:3], 1):
            print(f"      대안 {i}: {alt.get('location', 'N/A')[:40]}...")
    fixes_validated.append(("FIX 2: GeoOptimizer 3 Alternatives", fix2_valid))
    
    # FIX 3: Type Demand v7.2 grading scale enforcement
    print("\n✓ FIX 3: Type Demand v7.2 grading scale enforcement")
    print("   Checking: S/A/B/C/D grades with Korean text (매우 높음, 높음, 보통, 낮음, 매우 낮음)")
    
    type_demand_data = report_data.get('type_demand_v3_1', {})
    type_scores = type_demand_data.get('type_scores', {})
    
    # Check for v7.2 grade letters
    grade_letters = ["S (", "A (", "B (", "C (", "D ("]
    grades_in_text = sum(grade in content for grade in grade_letters)
    
    # Check for v7.2 Korean descriptions
    korean_grades = ["매우 높음", "높음", "보통", "낮음", "매우 낮음"]
    korean_in_text = sum(grade in content for grade in korean_grades)
    
    # Check grade fields in data
    has_grade_fields = False
    if type_scores:
        first_type = list(type_scores.values())[0]
        has_grade_fields = 'grade' in first_type and 'grade_text' in first_type
    
    # Check v7.2 grading scale table
    has_grading_table = "v7.2 등급 기준" in content
    
    fix3_valid = (grades_in_text >= 1 and korean_in_text >= 3 and 
                  has_grade_fields and has_grading_table)
    
    print(f"   Grade letters (S/A/B/C/D) in text: {grades_in_text}")
    print(f"   Korean grade text in content: {korean_in_text}/5")
    print(f"   Grade fields in data: {has_grade_fields}")
    print(f"   v7.2 grading table: {has_grading_table}")
    
    # Print sample grades
    if type_scores:
        print(f"   Sample type grades:")
        for type_name, scores in list(type_scores.items())[:3]:
            grade = scores.get('grade', 'N/A')
            grade_text = scores.get('grade_text', 'N/A')
            final_score = scores.get('final_score', 0)
            print(f"      {type_name}: {final_score:.1f}점 → {grade} ({grade_text})")
    
    fixes_validated.append(("FIX 3: Type Demand v7.2 Grading", fix3_valid))
    
    # Summary
    print("\n" + "="*80)
    print("📊 VALIDATION SUMMARY")
    print("="*80)
    
    for fix_name, is_valid in fixes_validated:
        status = "✅ PASS" if is_valid else "❌ FAIL"
        print(f"{status} | {fix_name}")
    
    total_valid = sum(1 for _, valid in fixes_validated if valid)
    total_fixes = len(fixes_validated)
    
    print(f"\n📈 Overall: {total_valid}/{total_fixes} fixes validated")
    
    # Save report
    output_path = "/tmp/v7_2_three_fixes_report.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n💾 Report saved: {output_path}")
    
    # Save data
    data_path = "/tmp/v7_2_three_fixes_data.json"
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    print(f"💾 Data saved: {data_path}")
    
    # Detailed verification
    print("\n" + "="*80)
    print("🔍 DETAILED VERIFICATION")
    print("="*80)
    
    # Check specific requirements
    print("\n✓ Requirement 1: All 23 zoning fields always display a value")
    print(f"   Result: {zoning_count}/23 fields displayed")
    
    print("\n✓ Requirement 2: Alternatives 1~3 printed")
    print(f"   Result: {len(alternatives)} alternatives guaranteed")
    
    print("\n✓ Requirement 3: Type Demand text correctly graded")
    demand_level = type_demand_data.get('demand_level', 'N/A')
    print(f"   Demand Level: {demand_level}")
    print(f"   Is v7.2 Korean text: {demand_level in korean_grades}")
    
    # Final verdict
    print("\n" + "="*80)
    if total_valid == total_fixes:
        print("✅ ALL 3 FIXES VALIDATED - PRODUCTION READY")
    elif total_valid >= 2:
        print("⚠️ PARTIALLY VALIDATED - MINOR ISSUES")
    else:
        print("❌ VALIDATION FAILED - REQUIRES FIXES")
    print("="*80 + "\n")
    
    return total_valid == total_fixes


if __name__ == "__main__":
    success = test_three_fixes()
    sys.exit(0 if success else 1)
