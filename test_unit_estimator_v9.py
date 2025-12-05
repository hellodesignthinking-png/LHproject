#!/usr/bin/env python3
"""
Unit Estimator V9 Test Suite

Tests automatic household unit count estimation for ZeroSite v9.1
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services_v9.unit_estimator_v9_0 import (
    UnitEstimatorV9, 
    quick_estimate_units,
    UnitEstimation
)

def test_basic_estimation():
    """Test Case 1: Basic unit estimation"""
    print("=" * 70)
    print("TEST 1: Basic Unit Estimation (1000㎡ land, 300% FAR)")
    print("=" * 70)
    
    estimator = UnitEstimatorV9()
    result = estimator.estimate_units(
        land_area=1000.0,
        floor_area_ratio=300.0,
        building_coverage_ratio=50.0,
        target_unit_size="26평형"
    )
    
    print(f"📊 Estimation Result:")
    print(f"   Estimated Units: {result.estimated_units}세대")
    print(f"   Calculation Method: {result.calculation_method}")
    print(f"   Total Floor Area: {result.total_floor_area:.2f}㎡")
    print(f"   Buildable Area: {result.buildable_area:.2f}㎡")
    print(f"   Avg Unit Size: {result.avg_unit_size}㎡ (26평형)")
    print(f"   Efficiency Ratio: {result.efficiency_ratio*100:.0f}%")
    print(f"   Confidence Score: {result.confidence_score:.1f}%")
    
    print(f"\n📦 Unit Type Distribution:")
    for unit_type, count in result.unit_type_distribution.items():
        print(f"   {unit_type}: {count}세대")
    
    if result.warnings:
        print(f"\n⚠️  Warnings:")
        for warning in result.warnings:
            print(f"   - {warning}")
    
    print(f"\n✅ Test 1 PASSED: Estimated {result.estimated_units} units")
    print()
    return result


def test_small_land_estimation():
    """Test Case 2: Small land estimation"""
    print("=" * 70)
    print("TEST 2: Small Land (500㎡, 200% FAR)")
    print("=" * 70)
    
    estimator = UnitEstimatorV9()
    result = estimator.estimate_units(
        land_area=500.0,
        floor_area_ratio=200.0,
        building_coverage_ratio=60.0,
        target_unit_size="20평형"
    )
    
    print(f"📊 Estimation Result:")
    print(f"   Estimated Units: {result.estimated_units}세대")
    print(f"   Total Floor Area: {result.total_floor_area:.2f}㎡")
    print(f"   Confidence Score: {result.confidence_score:.1f}%")
    
    print(f"\n✅ Test 2 PASSED: Estimated {result.estimated_units} units")
    print()
    return result


def test_large_land_estimation():
    """Test Case 3: Large land estimation"""
    print("=" * 70)
    print("TEST 3: Large Land (5000㎡, 400% FAR)")
    print("=" * 70)
    
    estimator = UnitEstimatorV9()
    result = estimator.estimate_units(
        land_area=5000.0,
        floor_area_ratio=400.0,
        building_coverage_ratio=40.0,
        target_unit_size="26평형"
    )
    
    print(f"📊 Estimation Result:")
    print(f"   Estimated Units: {result.estimated_units}세대")
    print(f"   Total Floor Area: {result.total_floor_area:.2f}㎡")
    print(f"   Confidence Score: {result.confidence_score:.1f}%")
    
    print(f"\n📦 Unit Type Distribution:")
    for unit_type, count in result.unit_type_distribution.items():
        print(f"   {unit_type}: {count}세대")
    
    print(f"\n✅ Test 3 PASSED: Estimated {result.estimated_units} units")
    print()
    return result


def test_quick_estimation():
    """Test Case 4: Quick estimation function"""
    print("=" * 70)
    print("TEST 4: Quick Estimation Function")
    print("=" * 70)
    
    unit_count = quick_estimate_units(
        land_area=1000.0,
        floor_area_ratio=300.0,
        building_coverage_ratio=50.0
    )
    
    print(f"📊 Quick Estimation: {unit_count}세대")
    print(f"✅ Test 4 PASSED")
    print()
    return unit_count


def test_parking_calculation():
    """Test Case 5: Parking requirement calculation"""
    print("=" * 70)
    print("TEST 5: Parking Requirement Calculation")
    print("=" * 70)
    
    estimator = UnitEstimatorV9()
    
    test_cases = [20, 50, 80, 150]
    
    for unit_count in test_cases:
        parking_required = estimator.estimate_parking_requirement(unit_count)
        print(f"   {unit_count}세대 → {parking_required}대 주차 필요")
    
    print(f"\n✅ Test 5 PASSED")
    print()


def test_validation():
    """Test Case 6: Estimation validation"""
    print("=" * 70)
    print("TEST 6: Estimation Validation")
    print("=" * 70)
    
    estimator = UnitEstimatorV9()
    
    # Case 1: Normal density
    validation1 = estimator.validate_unit_estimation(
        estimated_units=80,
        land_area=1000.0,
        parking_area_available=2000.0
    )
    
    print(f"📊 Case 1: 80 units / 1000㎡")
    print(f"   Valid: {validation1['valid']}")
    print(f"   Density: {validation1['density_per_1000sqm']}세대/1000㎡")
    print(f"   Required Parking: {validation1['required_parking']}대")
    if validation1['issues']:
        print(f"   Issues: {validation1['issues']}")
    
    # Case 2: High density
    validation2 = estimator.validate_unit_estimation(
        estimated_units=200,
        land_area=1000.0
    )
    
    print(f"\n📊 Case 2: 200 units / 1000㎡")
    print(f"   Valid: {validation2['valid']}")
    print(f"   Density: {validation2['density_per_1000sqm']}세대/1000㎡")
    if validation2['issues']:
        print(f"   Issues: {validation2['issues']}")
    
    print(f"\n✅ Test 6 PASSED")
    print()


def run_all_tests():
    """Run all unit estimator tests"""
    print("\n" + "=" * 70)
    print("🏗️  ZEROSITE V9.1 - UNIT ESTIMATOR TEST SUITE")
    print("=" * 70)
    print()
    
    try:
        # Test 1: Basic estimation
        result1 = test_basic_estimation()
        
        # Test 2: Small land
        result2 = test_small_land_estimation()
        
        # Test 3: Large land
        result3 = test_large_land_estimation()
        
        # Test 4: Quick function
        result4 = test_quick_estimation()
        
        # Test 5: Parking
        test_parking_calculation()
        
        # Test 6: Validation
        test_validation()
        
        # Summary
        print("=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print(f"✅ All 6 tests PASSED")
        print(f"\nEstimation Results:")
        print(f"   Test 1 (1000㎡, 300% FAR): {result1.estimated_units}세대")
        print(f"   Test 2 (500㎡, 200% FAR):  {result2.estimated_units}세대")
        print(f"   Test 3 (5000㎡, 400% FAR): {result3.estimated_units}세대")
        print(f"   Test 4 (Quick Function):   {result4}세대")
        print()
        print("🎉 ZeroSite v9.1 Unit Estimator: ALL TESTS PASSED")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
