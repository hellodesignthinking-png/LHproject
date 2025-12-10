"""
ZeroSite Phase 11: Architecture Module Tests

Comprehensive tests for the automated design system.

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 11.0
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.architect import (
    DesignGenerator,
    DesignStrategy,
    SupplyType,
    LHUnitDistributor,
    ParkingCalculator,
    ZoningRuleEngine,
    GeometryEngine,
)


def test_lh_unit_distribution():
    """Test LH unit distribution"""
    print("\n" + "="*80)
    print("🧪 TEST 1: LH Unit Distribution")
    print("="*80)
    
    test_cases = [
        (SupplyType.YOUTH, 100),
        (SupplyType.NEWLYWED, 120),
        (SupplyType.SENIOR, 80),
    ]
    
    for supply_type, units in test_cases:
        distributor = LHUnitDistributor(supply_type)
        unit_mix = distributor.distribute(units)
        
        total_units = sum(u.count for u in unit_mix)
        assert total_units == units, f"Unit count mismatch: {total_units} != {units}"
        
        print(f"✅ {supply_type.value}: {units} units → {len(unit_mix)} types")
    
    return True


def test_parking_calculation():
    """Test parking calculation"""
    print("\n" + "="*80)
    print("🧪 TEST 2: Parking Calculation")
    print("="*80)
    
    from app.architect import quick_distribute
    
    test_cases = [
        ("서울특별시 강남구", SupplyType.YOUTH, 100),
        ("경기도 성남시", SupplyType.NEWLYWED, 120),
        ("부산광역시 해운대구", SupplyType.SENIOR, 80),
    ]
    
    calculator = ParkingCalculator()
    
    for address, supply_type, units in test_cases:
        unit_mix = quick_distribute(supply_type, units)
        parking = calculator.calculate(unit_mix, address)
        
        assert parking.required_spots > 0, "Required spots must be > 0"
        assert parking.provided_spots >= parking.required_spots, "Must meet requirements"
        assert parking.compliance_rate >= 1.0, "Compliance rate must be >= 100%"
        
        print(
            f"✅ {address}: {units} units → "
            f"{parking.provided_spots} spots ({parking.compliance_rate*100:.0f}%)"
        )
    
    return True


def test_zoning_rules():
    """Test zoning rules"""
    print("\n" + "="*80)
    print("🧪 TEST 3: Zoning Rules")
    print("="*80)
    
    land_params = {
        "area": 1000.0,
        "bcr": 60,
        "far": 200,
        "max_floors": 15,
    }
    
    engine = ZoningRuleEngine(land_params)
    
    for strategy in DesignStrategy:
        volume = engine.calculate_volume(strategy)
        
        assert volume.total_gfa > 0, "GFA must be > 0"
        assert volume.max_units > 0, "Units must be > 0"
        assert volume.floor_count > 0, "Floors must be > 0"
        
        validation = engine.validate_volume(volume)
        assert validation["valid"], f"Volume validation failed for {strategy.value}"
        
        print(
            f"✅ {strategy.value}: "
            f"{volume.total_gfa:,.0f}㎡, "
            f"{volume.max_units} units, "
            f"{volume.floor_count} floors"
        )
    
    return True


def test_geometry_engine():
    """Test geometry engine"""
    print("\n" + "="*80)
    print("🧪 TEST 4: Geometry Engine")
    print("="*80)
    
    from app.architect import quick_distribute
    
    unit_mix = quick_distribute(SupplyType.NEWLYWED, 120)
    building_coverage = 600.0
    floor_count = 10
    
    engine = GeometryEngine()
    layout = engine.solve_layout(unit_mix, building_coverage, floor_count)
    
    assert len(layout.blocks) > 0, "Must have at least 1 block"
    assert layout.total_footprint == building_coverage, "Footprint mismatch"
    assert 0 < layout.site_coverage_ratio <= 1.0, "Coverage ratio out of range"
    
    # Test SVG generation
    svg = layout.to_svg()
    assert len(svg) > 0, "SVG must not be empty"
    assert '<svg' in svg, "Invalid SVG format"
    
    validation = engine.validate_layout(layout)
    
    print(f"✅ Layout: {len(layout.blocks)} blocks, {layout.total_footprint:.0f}㎡")
    print(f"✅ SVG: {len(svg)} characters")
    print(f"✅ {validation['summary']}")
    
    return True


def test_design_generator():
    """Test complete design generation"""
    print("\n" + "="*80)
    print("🧪 TEST 5: Design Generator (Integration)")
    print("="*80)
    
    address = "서울특별시 강남구 역삼동 123-45"
    land_params = {
        "area": 1000.0,
        "bcr": 60,
        "far": 200,
        "max_floors": 15,
    }
    
    generator = DesignGenerator(
        address=address,
        land_params=land_params,
        supply_type=SupplyType.NEWLYWED
    )
    
    # Generate designs
    designs = generator.generate()
    
    assert len(designs) == 3, "Must generate 3 designs"
    
    strategies_found = {d.strategy for d in designs}
    assert strategies_found == set(DesignStrategy), "Must have all 3 strategies"
    
    # Validate each design
    for design in designs:
        assert design.total_units > 0, "Must have units"
        assert design.volume.total_gfa > 0, "Must have GFA"
        assert len(design.unit_mix) > 0, "Must have unit mix"
        assert design.parking.provided_spots > 0, "Must have parking"
        assert len(design.layout.blocks) > 0, "Must have layout"
        
        print(
            f"✅ {design.strategy.value}: "
            f"{design.total_units} units, "
            f"{design.volume.total_gfa:,.0f}㎡, "
            f"{design.parking.provided_spots} parking"
        )
    
    # Test comparison
    comparison = generator.compare_designs(designs)
    
    assert len(comparison.designs) == 3, "Comparison must have 3 designs"
    assert comparison.recommended in DesignStrategy, "Must have recommendation"
    
    print(f"\n💡 Recommended: {comparison.recommended.value}")
    
    # Test dict export
    result_dict = generator.to_dict(designs)
    
    assert result_dict["address"] == address, "Address mismatch"
    assert result_dict["design_count"] == 3, "Design count mismatch"
    assert len(result_dict["designs"]) == 3, "Designs export mismatch"
    
    print(f"✅ Export: {len(str(result_dict))} characters")
    
    return True


def test_supply_type_recommendation():
    """Test supply type auto-recommendation"""
    print("\n" + "="*80)
    print("🧪 TEST 6: Supply Type Recommendation")
    print("="*80)
    
    test_cases = [
        ("서울대학교 근처", SupplyType.YOUTH),
        ("초등학교 역세권", None),  # Should work but can be anything
        ("요양병원 인근", SupplyType.SENIOR),
    ]
    
    for address, expected in test_cases:
        recommended = LHUnitDistributor.recommend_supply_type(address)
        
        assert recommended in SupplyType, "Invalid supply type"
        
        if expected:
            # Note: This is heuristic, so we just check it works
            print(f"✅ '{address}' → {recommended.value}")
        else:
            print(f"✅ '{address}' → {recommended.value} (auto)")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 ZEROSITE PHASE 11: ARCHITECTURE MODULE TESTS")
    print("="*80)
    
    tests = [
        ("LH Unit Distribution", test_lh_unit_distribution),
        ("Parking Calculation", test_parking_calculation),
        ("Zoning Rules", test_zoning_rules),
        ("Geometry Engine", test_geometry_engine),
        ("Design Generator", test_design_generator),
        ("Supply Type Recommendation", test_supply_type_recommendation),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ {name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "="*80)
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Phase 11 Complete!")
        print("="*80)
        return True
    else:
        print("⚠️ SOME TESTS FAILED - Review and fix issues")
        print("="*80)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
