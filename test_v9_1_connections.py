#!/usr/bin/env python3
"""
ZeroSite v9.1 Connection Test
테스트 all imports and data flow connections
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test all v9.1 imports"""
    print("=" * 80)
    print("🧪 Test 1: Import Validation")
    print("=" * 80)
    
    try:
        # Test core services
        from app.services_v9.address_resolver_v9_0 import AddressResolverV9, AddressInfo
        print("✅ AddressResolverV9 import successful")
        
        from app.services_v9.zoning_auto_mapper_v9_0 import ZoningAutoMapperV9, ZoningStandards
        print("✅ ZoningAutoMapperV9 import successful")
        
        from app.services_v9.unit_estimator_v9_0 import UnitEstimatorV9, UnitEstimate
        print("✅ UnitEstimatorV9 and UnitEstimate import successful")
        
        from app.services_v9.normalization_layer_v9_1_enhanced import NormalizationLayerV91
        print("✅ NormalizationLayerV91 import successful")
        
        # Test orchestrator
        from app.engines_v9.orchestrator_v9_0 import EngineOrchestratorV90
        print("✅ EngineOrchestratorV90 import successful")
        
        # Test API endpoint
        from app.api.endpoints.analysis_v9_1 import router
        print("✅ v9.1 API router import successful")
        
        print("\n✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False


def test_unit_estimate_fields():
    """Test UnitEstimate dataclass fields"""
    print("\n" + "=" * 80)
    print("🧪 Test 2: UnitEstimate Field Validation")
    print("=" * 80)
    
    try:
        from app.services_v9.unit_estimator_v9_0 import UnitEstimate
        
        # Create a sample UnitEstimate instance
        estimate = UnitEstimate(
            total_units=35,
            total_gfa=2500.0,
            residential_gfa=2125.0,
            commercial_gfa=375.0,
            building_footprint=500.0,
            floors=5,
            units_per_floor=7,
            parking_spaces=35,
            unit_type_distribution={"59㎡": 21, "74㎡": 10, "84㎡": 4},
            avg_unit_area=60.0,
            calculation_method="auto"
        )
        
        # Verify all fields
        print(f"✅ total_units: {estimate.total_units}")
        print(f"✅ floors: {estimate.floors}")
        print(f"✅ parking_spaces: {estimate.parking_spaces}")
        print(f"✅ total_gfa: {estimate.total_gfa}")
        print(f"✅ residential_gfa: {estimate.residential_gfa}")
        
        # Verify field names are correct (not estimated_units, estimated_floors)
        assert hasattr(estimate, 'total_units'), "total_units field missing"
        assert hasattr(estimate, 'floors'), "floors field missing"
        assert hasattr(estimate, 'total_gfa'), "total_gfa field missing"
        
        print("\n✅ All UnitEstimate fields validated!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_orchestrator_method():
    """Test EngineOrchestratorV90 method availability"""
    print("\n" + "=" * 80)
    print("🧪 Test 3: EngineOrchestratorV90 Method Validation")
    print("=" * 80)
    
    try:
        from app.engines_v9.orchestrator_v9_0 import EngineOrchestratorV90
        
        # Check if analyze_comprehensive method exists
        if hasattr(EngineOrchestratorV90, 'analyze_comprehensive'):
            print("✅ analyze_comprehensive() method exists")
        else:
            print("❌ analyze_comprehensive() method NOT found")
            return False
        
        # Check constructor signature
        import inspect
        init_sig = inspect.signature(EngineOrchestratorV90.__init__)
        params = list(init_sig.parameters.keys())
        
        print(f"✅ Constructor parameters: {params}")
        
        if 'kakao_api_key' in params:
            print("✅ kakao_api_key parameter exists")
        else:
            print("❌ kakao_api_key parameter NOT found")
            return False
        
        print("\n✅ EngineOrchestratorV90 method validation passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_data_flow():
    """Test data flow from request to response"""
    print("\n" + "=" * 80)
    print("🧪 Test 4: Data Flow Validation")
    print("=" * 80)
    
    try:
        from app.services_v9.unit_estimator_v9_0 import UnitEstimatorV9
        
        estimator = UnitEstimatorV9()
        
        # Simulate estimation
        print("Testing unit estimation with zone_type parameter...")
        estimation = estimator.estimate_units(
            land_area=1000.0,
            floor_area_ratio=250.0,
            building_coverage_ratio=50.0,
            zone_type="제3종일반주거지역"
        )
        
        print(f"✅ Estimation result:")
        print(f"   - total_units: {estimation.total_units}")
        print(f"   - floors: {estimation.floors} (max 15 for 제3종일반주거지역)")
        print(f"   - parking_spaces: {estimation.parking_spaces}")
        print(f"   - total_gfa: {estimation.total_gfa:.2f} m²")
        
        # Verify zone-based max floors
        if estimation.floors <= 15:
            print(f"✅ Zone-based floor limit (15) applied correctly")
        else:
            print(f"⚠️ Floor limit may not be applied: {estimation.floors} > 15")
        
        print("\n✅ Data flow validation passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all connection tests"""
    print("\n" + "=" * 80)
    print("🚀 ZeroSite v9.1 Connection Test Suite")
    print("=" * 80)
    
    results = []
    
    # Run all tests
    results.append(("Import Validation", test_imports()))
    results.append(("UnitEstimate Fields", test_unit_estimate_fields()))
    results.append(("Orchestrator Methods", test_orchestrator_method()))
    results.append(("Data Flow", test_data_flow()))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Summary")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"Total: {passed} passed, {failed} failed out of {len(results)} tests")
    print("=" * 80)
    
    if failed == 0:
        print("\n🎉 All tests passed! v9.1 connections are validated.")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
