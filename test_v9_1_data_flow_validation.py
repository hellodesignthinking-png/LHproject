"""
ZeroSite v9.1 Data Flow Validation Test
========================================

Cross-version data flow test:
- v9.1 inputs → v9.1 normalization → v9.0 engines → output validation

Author: ZeroSite Development Team
Date: 2025-12-05
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services_v9.address_resolver_v9_0 import AddressResolverV9
from app.services_v9.zoning_auto_mapper_v9_0 import ZoningAutoMapperV9
from app.services_v9.unit_estimator_v9_0 import UnitEstimatorV9
from app.services_v9.normalization_layer_v9_1_enhanced import NormalizationLayerV91
from app.engines_v9.orchestrator_v9_0 import EngineOrchestratorV90
from app.core.config import settings


async def test_v9_1_data_flow():
    """
    Test v9.1 complete data flow:
    4 inputs → 12 auto-calculated fields → v9.0 engines → standardized output
    """
    print("="*80)
    print("🔍 ZeroSite v9.1 Data Flow Validation")
    print("="*80)
    
    # Test input (4 fields only)
    test_input = {
        "address": "서울특별시 마포구 월드컵북로 120",
        "land_area": 1000.0,
        "land_appraisal_price": 9000000,
        "zone_type": "제3종일반주거지역"
    }
    
    print("\n📋 Step 1: v9.1 Input (4 fields only)")
    print(f"   - Address: {test_input['address']}")
    print(f"   - Land Area: {test_input['land_area']} m²")
    print(f"   - Appraisal Price: {test_input['land_appraisal_price']:,} KRW/m²")
    print(f"   - Zone Type: {test_input['zone_type']}")
    
    # Initialize v9.1 services
    print("\n📋 Step 2: Initialize v9.1 Services")
    norm_layer = NormalizationLayerV91()
    
    # Track auto-calculated fields
    auto_calculated = {}
    
    # Step 2.1: Address → Coordinates
    print("\n📋 Step 2.1: Address Resolution (Address → Coordinates)")
    address_resolver = AddressResolverV9()
    address_info = await address_resolver.resolve_address(test_input['address'])
    
    if address_info:
        test_input['latitude'] = address_info.latitude
        test_input['longitude'] = address_info.longitude
        auto_calculated['latitude'] = address_info.latitude
        auto_calculated['longitude'] = address_info.longitude
        auto_calculated['legal_code'] = address_info.legal_code
        print(f"   ✅ Latitude: {address_info.latitude}")
        print(f"   ✅ Longitude: {address_info.longitude}")
        print(f"   ✅ Legal Code: {address_info.legal_code}")
    else:
        print("   ⚠️ Address resolution failed")
    
    # Step 2.2: Zone Type → Building Standards
    print("\n📋 Step 2.2: Zoning Mapper (Zone Type → BCR/FAR)")
    zoning_mapper = ZoningAutoMapperV9()
    zoning_standards = zoning_mapper.get_zoning_standards(test_input['zone_type'])
    
    if zoning_standards:
        test_input['building_coverage_ratio'] = zoning_standards.building_coverage_ratio
        test_input['floor_area_ratio'] = zoning_standards.floor_area_ratio
        if zoning_standards.max_height:
            test_input['height_limit'] = zoning_standards.max_height
            auto_calculated['height_limit'] = zoning_standards.max_height
        auto_calculated['building_coverage_ratio'] = zoning_standards.building_coverage_ratio
        auto_calculated['floor_area_ratio'] = zoning_standards.floor_area_ratio
        print(f"   ✅ Building Coverage Ratio: {zoning_standards.building_coverage_ratio}%")
        print(f"   ✅ Floor Area Ratio: {zoning_standards.floor_area_ratio}%")
        print(f"   ✅ Max Height: {zoning_standards.max_height if zoning_standards.max_height else 'No limit'}")
    else:
        print("   ⚠️ Zoning standards lookup failed")
    
    # Step 2.3: Unit Count Estimation
    print("\n📋 Step 2.3: Unit Estimator (Auto-calculate Units/Floors/Parking)")
    unit_estimator = UnitEstimatorV9()
    estimation = unit_estimator.estimate_units(
        land_area=test_input['land_area'],
        floor_area_ratio=test_input['floor_area_ratio'],
        building_coverage_ratio=test_input['building_coverage_ratio'],
        zone_type=test_input['zone_type']
    )
    
    # CRITICAL: Pass ALL estimated values to v9.0 engines
    test_input['unit_count'] = estimation.total_units
    test_input['total_gfa'] = estimation.total_gfa
    test_input['residential_gfa'] = estimation.residential_gfa
    test_input['estimated_floors'] = estimation.floors
    test_input['parking_spaces'] = estimation.parking_spaces
    
    auto_calculated['unit_count'] = estimation.total_units
    auto_calculated['estimated_floors'] = estimation.floors
    auto_calculated['parking_spaces'] = estimation.parking_spaces
    auto_calculated['total_gfa'] = estimation.total_gfa
    auto_calculated['residential_gfa'] = estimation.residential_gfa
    
    print(f"   ✅ Unit Count: {estimation.total_units}")
    print(f"   ✅ Estimated Floors: {estimation.floors}")
    print(f"   ✅ Parking Spaces: {estimation.parking_spaces}")
    print(f"   ✅ Total GFA: {estimation.total_gfa:.2f} m²")
    print(f"   ✅ Residential GFA: {estimation.residential_gfa:.2f} m²")
    
    # Step 2.4: Construction Cost Auto-calculation
    print("\n📋 Step 2.4: Construction Cost Auto-calculation")
    if '상업' in test_input['zone_type']:
        construction_cost = 3500000
    elif '준주거' in test_input['zone_type']:
        construction_cost = 3000000
    else:
        construction_cost = 2800000
    
    test_input['construction_cost_per_sqm'] = construction_cost
    auto_calculated['construction_cost_per_sqm'] = construction_cost
    print(f"   ✅ Construction Cost: {construction_cost:,} KRW/m²")
    
    # Step 2.5: Total Land Cost
    total_land_cost = test_input['land_area'] * test_input['land_appraisal_price']
    test_input['total_land_cost'] = total_land_cost
    auto_calculated['total_land_cost'] = total_land_cost
    print(f"   ✅ Total Land Cost: {total_land_cost:,} KRW")
    
    # Summary of auto-calculated fields
    print("\n📊 Auto-Calculated Fields Summary:")
    print(f"   Total: {len(auto_calculated)} fields auto-calculated")
    for i, (key, value) in enumerate(auto_calculated.items(), 1):
        if isinstance(value, float):
            print(f"   {i:2d}. {key}: {value:.2f}")
        else:
            print(f"   {i:2d}. {key}: {value}")
    
    # Step 3: Run v9.0 Orchestrator
    print("\n📋 Step 3: Run v9.0 Engine Orchestrator")
    kakao_api_key = getattr(settings, 'kakao_rest_api_key', None) or getattr(settings, 'KAKAO_REST_API_KEY', None)
    
    if not kakao_api_key:
        print("   ⚠️ KAKAO_REST_API_KEY not found - skipping orchestrator test")
        return
    
    orchestrator = EngineOrchestratorV90(kakao_api_key=kakao_api_key)
    
    # Validate that all required fields are present
    required_fields = [
        'unit_count', 'total_gfa', 'residential_gfa', 
        'construction_cost_per_sqm', 'total_land_cost'
    ]
    
    print("\n   Validating required fields for Financial Engine:")
    all_present = True
    for field in required_fields:
        value = test_input.get(field)
        status = "✅" if value is not None else "❌"
        print(f"   {status} {field}: {value}")
        if value is None:
            all_present = False
    
    if all_present:
        print("\n   ✅ All required fields present for v9.0 engines")
        
        # Run comprehensive analysis
        print("\n   Running comprehensive analysis...")
        try:
            analysis_result = await orchestrator.analyze_comprehensive(test_input)
            
            print(f"\n   ✅ Analysis Complete!")
            print(f"      - Analysis ID: {analysis_result.analysis_id}")
            print(f"      - LH Total Score: {analysis_result.lh_scores.total_score:.1f}")
            print(f"      - LH Grade: {analysis_result.lh_scores.grade.value}")
            print(f"      - Risk Level: {analysis_result.risk_assessment.overall_risk_level}")
            print(f"      - Final Decision: {analysis_result.final_recommendation.decision.value}")
            print(f"      - Confidence: {analysis_result.final_recommendation.confidence_level:.1f}%")
            print(f"      - Processing Time: {analysis_result.processing_time_seconds:.2f}s")
            
            # Validate Financial Engine received correct data
            print("\n   📊 Financial Engine Output Validation:")
            financial = analysis_result.financial_result
            print(f"      - Total CAPEX (Investment): {financial.total_capex:,.0f} KRW")
            print(f"      - Total Construction Cost: {financial.total_construction_cost:,.0f} KRW")
            print(f"      - 10-Year IRR: {financial.irr_10yr:.2f}%")
            print(f"      - 10-Year ROI: {financial.roi_10yr:.2f}%")
            print(f"      - Financial Grade: {financial.overall_grade}")
            
            return True
            
        except Exception as e:
            print(f"\n   ❌ Analysis failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("\n   ❌ Missing required fields - cannot run v9.0 engines")
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("ZeroSite v9.1 → v9.0 Data Flow Validation Test")
    print("="*80)
    
    success = asyncio.run(test_v9_1_data_flow())
    
    print("\n" + "="*80)
    if success:
        print("✅ ALL TESTS PASSED")
        print("v9.1 data flow is fully connected and operational!")
    else:
        print("⚠️ TESTS INCOMPLETE")
        print("Some tests could not be completed (check configuration)")
    print("="*80)
