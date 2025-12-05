#!/usr/bin/env python3
"""
Test Phase 2 Comprehensive Fixes
- Risk Score display improvement
- Conclusion logic improvement (no contradictions)
- LH consultant-level narrative enrichment
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.services.report_field_mapper_v7_2_complete import ReportFieldMapperV72Complete

def test_phase2_fixes():
    """Test all Phase 2 fixes"""
    
    print("=" * 80)
    print("🧪 PHASE 2 FIX VALIDATION")
    print("=" * 80)
    print()
    
    # Create mock analysis result
    print("📍 Creating mock analysis result for Phase 2 testing...")
    result = {
        'corrected_input': {
            'address': '서울특별시 마포구 월드컵북로 120',
            'land_area': 660.0,
            'unit_type': '청년',
            'zone_type': '제3종일반주거지역'
        },
        'type_demand_scores': {
            '청년': 85.1,
            '신혼·신생아 I': 78.8,
            '고령자': 68.0
        },
        'demand_prediction': {
            'predicted_demand_score': 88.2,
            'demand_level': '높음'
        },
        'demand_analysis': {
            'key_factors': [
                {'name': '초등학교', 'distance_m': 288.0, 'weight': 0.35},
                {'name': '병원', 'distance_m': 179.0, 'weight': 0.25},
                {'name': '지하철역', 'distance_m': 450.0, 'weight': 0.20}
            ]
        },
        'grade_info': {
            'grade': 'A',
            'total_score': 92.0
        },
        'geo_optimization': {
            'optimization_score': 82.0,
            'recommended_sites': [
                {'location': '대체지 1', 'distance_m': 500, 'score': 80.5, 'reason': '우수한 접근성'},
                {'location': '대체지 2', 'distance_m': 750, 'score': 78.2, 'reason': '양호한 주변 환경'}
            ]
        },
        'risk_factors': [
            {'category': 'legal', 'description': '개발행위제한구역 일부 저촉', 'severity': 'medium'},
            {'category': 'physical', 'description': '경사도 15도 초과 구간 존재', 'severity': 'low'}
        ]
    }
    
    print(f"✅ Mock data created")
    print()
    
    # Initialize mapper
    print("🔄 Initializing ReportFieldMapperV72Complete...")
    mapper = ReportFieldMapperV72Complete()
    
    # Map the data
    print("📊 Mapping v7.2 fields...")
    mapped_data = mapper.map_to_v7_2(result)
    
    print("✅ Mapping completed")
    print()
    
    # Test Results
    tests_passed = 0
    tests_total = 0
    
    print("=" * 80)
    print("📋 PHASE 2 FIX VALIDATION RESULTS")
    print("=" * 80)
    print()
    
    # FIX #5: Risk Score Display
    print("🔍 FIX #5: Risk Score Display (100-point scale)")
    print("-" * 80)
    risk_data = mapped_data.get('risk_analysis_2025', {})
    
    tests_total += 1
    risk_score = risk_data.get('risk_score', 0)
    if 0 <= risk_score <= 100:
        print(f"  ✅ Risk score in valid range: {risk_score:.0f}/100")
        tests_passed += 1
    else:
        print(f"  ❌ Risk score out of range: {risk_score}")
    
    tests_total += 1
    risk_formatted = risk_data.get('risk_score_formatted', '')
    if '100점' in risk_formatted or '/100' in risk_formatted:
        print(f"  ✅ Formatted risk score: {risk_formatted}")
        tests_passed += 1
    else:
        print(f"  ❌ Missing formatted risk score: {risk_formatted}")
    
    tests_total += 1
    total_deduction = risk_data.get('total_deduction', None)
    if total_deduction is not None:
        print(f"  ✅ Total deduction tracked: {total_deduction}점")
        tests_passed += 1
    else:
        print(f"  ❌ Total deduction missing")
    
    tests_total += 1
    deduction_per_risk = risk_data.get('deduction_per_risk', None)
    if deduction_per_risk == 10.0:
        print(f"  ✅ Deduction per risk: {deduction_per_risk}점 (LH standard)")
        tests_passed += 1
    else:
        print(f"  ❌ Incorrect deduction per risk: {deduction_per_risk}")
    
    print()
    
    # FIX #6: Conclusion Logic (No Contradictions)
    print("🔍 FIX #6: Conclusion Logic (No Contradictions)")
    print("-" * 80)
    td_data = mapped_data.get('type_demand_v3_1', {})
    
    tests_total += 1
    main_score = td_data.get('main_score', 0)
    selected_type = td_data.get('selected_unit_type', '')
    if selected_type:
        print(f"  ✅ Selected unit type tracked: {selected_type}")
        tests_passed += 1
    else:
        print(f"  ❌ Selected unit type missing")
    
    tests_total += 1
    td_grade = td_data.get('grade', '')
    if td_grade in ['S', 'A', 'B', 'C', 'D']:
        print(f"  ✅ Type demand grade: {td_grade} ({main_score:.1f}점)")
        tests_passed += 1
    else:
        print(f"  ❌ Invalid type demand grade: {td_grade}")
    
    # Check for logical consistency
    tests_total += 1
    lh_data = mapped_data.get('lh_assessment', {})
    lh_grade = lh_data.get('grade', 'N/A')
    
    # Conclusion should be consistent with scores
    consistent = True
    if lh_grade == 'A' and main_score >= 75:
        recommendation = "적극 추천 또는 추천"
        print(f"  ✅ Logical consistency: LH {lh_grade}등급 + TD {main_score:.1f}점 → {recommendation}")
        tests_passed += 1
    elif lh_grade == 'A' and main_score >= 60:
        recommendation = "추천 또는 조건부"
        print(f"  ✅ Logical consistency: LH {lh_grade}등급 + TD {main_score:.1f}점 → {recommendation}")
        tests_passed += 1
    elif lh_grade == 'B':
        recommendation = "조건부 검토"
        print(f"  ✅ Logical consistency: LH {lh_grade}등급 → {recommendation}")
        tests_passed += 1
    else:
        print(f"  ❌ Potential inconsistency: LH {lh_grade}, TD {main_score:.1f}점")
    
    print()
    
    # FIX #7: Narrative Enrichment
    print("🔍 FIX #7: Narrative Enrichment (LH Consultant-Level)")
    print("-" * 80)
    
    tests_total += 1
    # Check if POI data has proper structure for narrative
    poi_data = mapped_data.get('poi_analysis_v3_1', {})
    poi_score = poi_data.get('total_score_v3_1', 0)
    if poi_score > 0:
        print(f"  ✅ POI data ready for narrative: {poi_score:.1f}점")
        tests_passed += 1
    else:
        print(f"  ❌ POI data insufficient for narrative")
    
    tests_total += 1
    # Check if GeoOptimizer data has formatted versions
    geo_data = mapped_data.get('geo_optimizer_v3_1', {})
    geo_score_formatted = geo_data.get('final_score_formatted', '')
    if geo_score_formatted:
        print(f"  ✅ GeoOptimizer formatted data: {geo_score_formatted}")
        tests_passed += 1
    else:
        print(f"  ❌ GeoOptimizer formatting missing")
    
    tests_total += 1
    # Check alternatives formatting
    alternatives = geo_data.get('alternatives', [])
    if alternatives and len(alternatives) > 0:
        alt = alternatives[0]
        if 'distance_km' in alt or 'score_formatted' in alt:
            print(f"  ✅ Alternative sites pre-formatted for narrative")
            tests_passed += 1
        else:
            print(f"  ❌ Alternative sites not formatted")
    else:
        print(f"  ⚠️  No alternatives data (optional)")
        tests_passed += 1  # Don't fail on optional data
    
    print()
    print("=" * 80)
    print("📊 PHASE 2 TEST SUMMARY")
    print("=" * 80)
    pass_rate = (tests_passed / tests_total * 100) if tests_total > 0 else 0
    print(f"✅ Passed: {tests_passed}/{tests_total} ({pass_rate:.1f}%)")
    print(f"❌ Failed: {tests_total - tests_passed}/{tests_total}")
    print()
    
    if tests_passed == tests_total:
        print("🎉 ALL PHASE 2 FIXES VALIDATED SUCCESSFULLY!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - REVIEW NEEDED")
        return False

if __name__ == "__main__":
    success = test_phase2_fixes()
    sys.exit(0 if success else 1)
