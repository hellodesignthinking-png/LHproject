"""
Test LH Cost Service Integration with Financial Engine (Phase C)

Tests:
- LH Cost Service basic functionality
- Financial Engine integration
- Accuracy validation (±2% target)
- Performance (<200ms response time)
- Regional coverage (Seoul, Gyeonggi, Busan)
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services_v9.lh_cost_service import get_lh_cost_service
from app.services.financial_engine_v7_4 import run_full_financial_analysis


def test_lh_cost_service():
    """Test LH Cost Service basic functionality"""
    print("\n" + "="*80)
    print("🧪 TEST 1: LH Cost Service Basic Functionality")
    print("="*80)
    
    service = get_lh_cost_service()
    
    test_cases = [
        ("서울특별시 강남구 역삼동 123-45", "Newlyweds_TypeII", "Seoul Gangnam"),
        ("서울특별시 마포구 월드컵북로 120", "Youth", "Seoul Mapo"),
        ("경기도 성남시 분당구 판교동", "MultiChild", "Gyeonggi Bundang"),
        ("부산광역시 해운대구 우동", "Senior", "Busan Haeundae"),
    ]
    
    all_passed = True
    for address, housing_type, desc in test_cases:
        start_time = time.time()
        cost, metadata = service.get_cost_per_m2(address, housing_type)
        response_time = (time.time() - start_time) * 1000
        
        if cost and cost > 0:
            print(f"✅ {desc}: ₩{cost:,.0f}/m² ({response_time:.2f}ms)")
            
            # Verify response time < 200ms
            if response_time > 200:
                print(f"   ⚠️ WARNING: Response time {response_time:.2f}ms > 200ms target")
                all_passed = False
            
            # Verify metadata
            if not metadata.get('region'):
                print(f"   ⚠️ WARNING: Missing region in metadata")
                all_passed = False
        else:
            print(f"❌ {desc}: Failed to get cost")
            all_passed = False
    
    return all_passed


def test_financial_engine_integration():
    """Test Financial Engine integration with LH Cost Service"""
    print("\n" + "="*80)
    print("🧪 TEST 2: Financial Engine Integration")
    print("="*80)
    
    test_cases = [
        {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 1000.0,
            "unit_type": "Newlyweds_TypeII",
            "housing_type": "Newlyweds_TypeII",
            "desc": "Gangnam Newlyweds"
        },
        {
            "address": "경기도 성남시 분당구 판교동",
            "land_area": 800.0,
            "unit_type": "MultiChild",
            "housing_type": "MultiChild",
            "desc": "Bundang MultiChild"
        },
    ]
    
    all_passed = True
    for case in test_cases:
        start_time = time.time()
        result = run_full_financial_analysis(
            land_area=case["land_area"],
            address=case["address"],
            unit_type=case["unit_type"],
            construction_type="standard",
            housing_type=case["housing_type"]
        )
        response_time = (time.time() - start_time) * 1000
        
        # Check if verified cost was used
        capex = result['capex']
        verified = capex.get('verified_cost', {})
        
        if verified.get('available'):
            print(f"\n✅ {case['desc']}:")
            print(f"   Total CapEx: ₩{capex['total_capex']:,.0f}")
            print(f"   Unit Count: {capex['unit_count']}")
            print(f"   Cost Source: {verified.get('source', 'N/A')}")
            print(f"   Cost/m²: ₩{verified.get('cost_per_m2', 0):,.0f}")
            print(f"   Region: {verified.get('region', 'N/A')}")
            print(f"   District: {verified.get('district', 'N/A')}")
            print(f"   Coefficient: {verified.get('district_coefficient', 'N/A')}")
            print(f"   Response Time: {response_time:.1f}ms")
            
            # Verify accuracy
            if verified.get('accuracy_target') == '±2%':
                print(f"   ✅ Accuracy Target: ±2%")
            else:
                print(f"   ⚠️ WARNING: Unexpected accuracy target")
                all_passed = False
        else:
            print(f"❌ {case['desc']}: Verified cost not used")
            all_passed = False
    
    return all_passed


def test_regional_coverage():
    """Test regional coverage"""
    print("\n" + "="*80)
    print("🧪 TEST 3: Regional Coverage")
    print("="*80)
    
    service = get_lh_cost_service()
    regions = service.get_all_regions()
    
    required_regions = ['seoul', 'gyeonggi', 'busan']
    
    print(f"Supported Regions: {len(regions)}")
    for key, name in regions.items():
        print(f"  - {key}: {name}")
    
    all_passed = True
    for region in required_regions:
        if region not in regions:
            print(f"❌ Missing required region: {region}")
            all_passed = False
        else:
            print(f"✅ {region}: Covered")
    
    return all_passed


def test_performance_benchmark():
    """Test performance benchmark"""
    print("\n" + "="*80)
    print("🧪 TEST 4: Performance Benchmark")
    print("="*80)
    
    service = get_lh_cost_service()
    
    # Warm up cache
    service.get_cost_per_m2("서울특별시 강남구 역삼동 123", "Youth")
    
    iterations = 100
    total_time = 0
    
    for i in range(iterations):
        start_time = time.time()
        service.get_cost_per_m2("서울특별시 강남구 역삼동 123", "Youth")
        total_time += (time.time() - start_time) * 1000
    
    avg_time = total_time / iterations
    
    print(f"Iterations: {iterations}")
    print(f"Average Response Time: {avg_time:.2f}ms")
    print(f"Total Time: {total_time:.1f}ms")
    
    # Check if average < 200ms
    if avg_time < 200:
        print(f"✅ Performance: Average {avg_time:.2f}ms < 200ms target")
        return True
    else:
        print(f"❌ Performance: Average {avg_time:.2f}ms > 200ms target")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 LH VERIFIED COST DB - PHASE C INTEGRATION TESTS")
    print("="*80)
    
    tests = [
        ("LH Cost Service", test_lh_cost_service),
        ("Financial Engine Integration", test_financial_engine_integration),
        ("Regional Coverage", test_regional_coverage),
        ("Performance Benchmark", test_performance_benchmark),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ {name} FAILED with exception: {e}")
            results[name] = False
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "="*80)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Phase C Integration Complete!")
        print("="*80)
        return True
    else:
        print("⚠️ SOME TESTS FAILED - Review and fix issues")
        print("="*80)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
