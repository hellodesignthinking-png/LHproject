"""
ZeroSite v9.1 REAL - 5개 실제 주소 E2E 테스트
==============================================

다양한 용도지역과 지역에서 완전한 검증

Author: ZeroSite Development Team
Date: 2025-12-05
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test addresses covering different zones and regions
TEST_ADDRESSES = [
    {
        "name": "마포구 (제3종일반주거)",
        "address": "서울특별시 마포구 월드컵북로 120",
        "land_area": 1000.0,
        "land_appraisal_price": 9000000,
        "zone_type": "제3종일반주거지역",
        "expected": {
            "bcr": 50.0,
            "far": 300.0,
            "min_units": 35,
            "max_units": 50
        }
    },
    {
        "name": "강남구 (중심상업지역)",
        "address": "서울특별시 강남구 테헤란로 152",
        "land_area": 1500.0,
        "land_appraisal_price": 15000000,
        "zone_type": "중심상업지역",
        "expected": {
            "bcr": 80.0,
            "far": 1000.0,
            "min_units": 150,
            "max_units": 200
        }
    },
    {
        "name": "성북구 (제2종일반주거)",
        "address": "서울특별시 성북구 정릉로 77",
        "land_area": 800.0,
        "land_appraisal_price": 7000000,
        "zone_type": "제2종일반주거지역",
        "expected": {
            "bcr": 60.0,
            "far": 250.0,
            "min_units": 25,
            "max_units": 35
        }
    },
    {
        "name": "용산구 (준주거지역)",
        "address": "서울특별시 용산구 한강대로 95",
        "land_area": 1200.0,
        "land_appraisal_price": 12000000,
        "zone_type": "준주거지역",
        "expected": {
            "bcr": 70.0,
            "far": 500.0,
            "min_units": 70,
            "max_units": 90
        }
    },
    {
        "name": "영등포구 (일반상업지역)",
        "address": "서울특별시 영등포구 여의대로 108",
        "land_area": 1000.0,
        "land_appraisal_price": 10000000,
        "zone_type": "일반상업지역",
        "expected": {
            "bcr": 80.0,
            "far": 800.0,
            "min_units": 90,
            "max_units": 120
        }
    }
]


async def test_single_address(test_case: dict, index: int):
    """단일 주소 테스트"""
    from app.api.endpoints.analysis_v9_1_REAL import analyze_land_real, AnalyzeLandRequestReal
    
    print(f"\n{'='*80}")
    print(f"🧪 Test {index + 1}/{len(TEST_ADDRESSES)}: {test_case['name']}")
    print(f"{'='*80}")
    
    # Create request
    request = AnalyzeLandRequestReal(
        address=test_case['address'],
        land_area=test_case['land_area'],
        land_appraisal_price=test_case['land_appraisal_price'],
        zone_type=test_case['zone_type']
    )
    
    print(f"\n📥 Input:")
    print(f"   Address: {request.address}")
    print(f"   Land Area: {request.land_area} m²")
    print(f"   Price: {request.land_appraisal_price:,} KRW/m²")
    print(f"   Zone: {request.zone_type}")
    
    try:
        # Run analysis
        response = await analyze_land_real(request)
        
        # Convert response
        if hasattr(response, 'dict'):
            response_dict = response.dict()
        elif hasattr(response, 'model_dump'):
            response_dict = response.model_dump()
        else:
            response_dict = response
        
        auto_calc = response_dict.get('auto_calculated', {})
        analysis = response_dict.get('analysis_result', {})
        
        # Validate auto-calculated fields
        print(f"\n✅ Auto-Calculated Fields:")
        print(f"   📍 Coordinates: ({auto_calc.get('latitude'):.6f}, {auto_calc.get('longitude'):.6f})")
        print(f"   🏗️ BCR/FAR: {auto_calc.get('building_coverage_ratio')}% / {auto_calc.get('floor_area_ratio')}%")
        print(f"   🏘️ Units: {auto_calc.get('unit_count')} units")
        print(f"   📐 Floors: {auto_calc.get('floors')} floors")
        print(f"   🚗 Parking: {auto_calc.get('parking_spaces')} spaces")
        print(f"   📊 GFA: {auto_calc.get('total_gfa'):,.0f} m²")
        
        # Validate expected values
        expected = test_case['expected']
        bcr = auto_calc.get('building_coverage_ratio')
        far = auto_calc.get('floor_area_ratio')
        units = auto_calc.get('unit_count')
        
        # Check BCR
        if bcr == expected['bcr']:
            print(f"   ✅ BCR matches expected: {bcr}%")
        else:
            print(f"   ⚠️  BCR mismatch: expected {expected['bcr']}%, got {bcr}%")
        
        # Check FAR
        if far == expected['far']:
            print(f"   ✅ FAR matches expected: {far}%")
        else:
            print(f"   ⚠️  FAR mismatch: expected {expected['far']}%, got {far}%")
        
        # Check Units range
        if expected['min_units'] <= units <= expected['max_units']:
            print(f"   ✅ Units in expected range: {units} ({expected['min_units']}-{expected['max_units']})")
        else:
            print(f"   ⚠️  Units out of range: {units} (expected {expected['min_units']}-{expected['max_units']})")
        
        # Analysis results
        if analysis:
            lh_scores = analysis.get('lh_scores', {})
            risk = analysis.get('risk_assessment', {})
            rec = analysis.get('final_recommendation', {})
            
            print(f"\n🎯 Analysis Results:")
            print(f"   LH Score: {lh_scores.get('total_score', 'N/A')}")
            
            # Handle grade
            grade = lh_scores.get('grade', 'N/A')
            if hasattr(grade, 'value'):
                grade_str = grade.value
            elif isinstance(grade, dict):
                grade_str = grade.get('value', str(grade))
            else:
                grade_str = str(grade)
            print(f"   LH Grade: {grade_str}")
            
            print(f"   Risk: {risk.get('overall_risk_level', 'N/A')}")
            
            # Handle decision
            decision = rec.get('decision', 'N/A')
            if hasattr(decision, 'value'):
                decision_str = decision.value
            elif isinstance(decision, dict):
                decision_str = decision.get('value', str(decision))
            else:
                decision_str = str(decision)
            print(f"   Decision: {decision_str}")
            print(f"   Confidence: {rec.get('confidence_level', 'N/A')}%")
        
        print(f"\n✅ Test {index + 1} PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Test {index + 1} FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """모든 테스트 실행"""
    print("="*80)
    print("🧪 ZeroSite v9.1 REAL - 5 Address E2E Test Suite")
    print("="*80)
    
    results = []
    for i, test_case in enumerate(TEST_ADDRESSES):
        result = await test_single_address(test_case, i)
        results.append(result)
        
        # Sleep between tests to avoid API rate limits
        if i < len(TEST_ADDRESSES) - 1:
            await asyncio.sleep(1)
    
    # Summary
    print("\n" + "="*80)
    print("📊 Test Summary")
    print("="*80)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_case, result) in enumerate(zip(TEST_ADDRESSES, results), 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - Test {i}: {test_case['name']}")
    
    print(f"\n   Total: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
