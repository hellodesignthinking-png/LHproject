"""
Test Canonical Flow Phase 3: LH Analysis Refactoring

Tests:
1. LH Analysis engine creation
2. LH-linked model calculation (50+ units, metro)
3. Standard model calculation (<50 units or non-metro)
4. Land value consistency (must match appraisal context)
5. End-to-end flow (Appraisal → Lock → LH Analysis)
"""

import sys
from app.services.canonical_schema import create_appraisal_from_analysis
from app.services.appraisal_context import AppraisalContextLock
from app.services.lh_analysis_canonical import LHAnalysisCanonical, create_lh_analysis_engine


def create_mock_appraisal_context(land_area: float, official_price: float, premium_rate: float):
    """Create and lock a mock appraisal context"""
    
    # Mock zone info
    class MockZoneInfo:
        zone_type = "제2종일반주거지역"
        building_coverage_ratio = 60.0
        floor_area_ratio = 200.0
    
    # Create canonical appraisal
    appraisal = create_appraisal_from_analysis(
        zone_info=MockZoneInfo(),
        land_area=land_area,
        official_price=official_price,
        transaction_price=official_price * 1.1,
        premium_rate=premium_rate,
        confidence_score=0.90
    )
    
    # Lock context
    ctx = AppraisalContextLock()
    ctx.lock(appraisal.to_context_dict())
    
    return ctx


def test_lh_engine_creation():
    """Test 1: Create LH analysis engine"""
    print("\n" + "="*70)
    print("TEST 1: LH Analysis Engine Creation")
    print("="*70)
    
    engine = create_lh_analysis_engine()
    
    print(f"✅ Engine created: {engine.__class__.__name__}")
    print(f"   Metro regions: {engine.METRO_REGIONS}")
    print(f"   Unit threshold: {engine.THRESHOLD_UNITS}")
    print(f"   LH standard cost: {engine.LH_STANDARD_UNIT_COST:,.0f}원/㎡")
    
    return engine


def test_lh_linked_model(engine):
    """Test 2: LH-linked model (50+ units, metro area)"""
    print("\n" + "="*70)
    print("TEST 2: LH-Linked Model (공사비 연동제)")
    print("="*70)
    
    # Create appraisal context
    print(f"\n📊 Creating appraisal context:")
    print(f"   Land area: 660㎡")
    print(f"   Official price: 5,500,000원/㎡")
    print(f"   Premium rate: 9%")
    
    appraisal_ctx = create_mock_appraisal_context(
        land_area=660.0,
        official_price=5500000,
        premium_rate=0.09
    )
    
    summary = appraisal_ctx.get_summary()
    print(f"   Final appraised total: {summary['final_appraised_total']:,.0f}원")
    
    # Run LH analysis
    print(f"\n🔄 Running LH-Linked analysis:")
    result = engine.analyze(
        appraisal_ctx=appraisal_ctx,
        expected_units=56,
        total_floor_area=2464.0,
        unit_type='신혼부부 I',
        address='서울특별시 마포구 월드컵북로 120'
    )
    
    # Validate results
    print(f"\n✅ Analysis Results:")
    print(f"   Analysis mode: {result['analysis_mode']}")
    print(f"   Land appraisal: {result['land_appraisal']:,.0f}원")
    print(f"   Verified cost: {result['verified_cost']:,.0f}원")
    print(f"   LH purchase price: {result['lh_purchase_price']:,.0f}원")
    print(f"   Total project cost: {result['total_project_cost']:,.0f}원")
    print(f"   ROI: {result['roi']:.2f}%")
    print(f"   Rating: {result['rating']}")
    print(f"   Decision: {result['decision']}")
    
    # Check land value consistency
    land_value_match = (
        result['land_appraisal'] ==
        appraisal_ctx.get('calculation.final_appraised_total')
    )
    
    print(f"\n🔍 Validation:")
    status = "✅ PASSED" if land_value_match else "❌ FAILED"
    print(f"   {status}: Land value matches appraisal context")
    
    # Check mode is correct
    mode_correct = result['analysis_mode'] == 'LH_LINKED'
    status = "✅ PASSED" if mode_correct else "❌ FAILED"
    print(f"   {status}: Correct mode (LH_LINKED)")
    
    # Check metadata
    has_metadata = result.get('based_on_appraisal') and result.get('appraisal_reference')
    status = "✅ PASSED" if has_metadata else "❌ FAILED"
    print(f"   {status}: Appraisal metadata present")
    
    return result, land_value_match and mode_correct and has_metadata


def test_standard_model(engine):
    """Test 3: Standard model (<50 units or non-metro)"""
    print("\n" + "="*70)
    print("TEST 3: Standard Model (비연동제)")
    print("="*70)
    
    # Create appraisal context (smaller project)
    print(f"\n📊 Creating appraisal context (small project):")
    print(f"   Land area: 350㎡")
    print(f"   Official price: 4,000,000원/㎡")
    print(f"   Premium rate: 5%")
    
    appraisal_ctx = create_mock_appraisal_context(
        land_area=350.0,
        official_price=4000000,
        premium_rate=0.05
    )
    
    summary = appraisal_ctx.get_summary()
    print(f"   Final appraised total: {summary['final_appraised_total']:,.0f}원")
    
    # Run LH analysis (< 50 units, should use STANDARD)
    print(f"\n🔄 Running Standard analysis:")
    result = engine.analyze(
        appraisal_ctx=appraisal_ctx,
        expected_units=30,  # < 50 units
        total_floor_area=1320.0,
        unit_type='청년',
        address='서울특별시 강남구 테헤란로 152'  # Metro, but < 50 units
    )
    
    # Validate results
    print(f"\n✅ Analysis Results:")
    print(f"   Analysis mode: {result['analysis_mode']}")
    print(f"   Land appraisal: {result['land_appraisal']:,.0f}원")
    print(f"   Construction cost: {result['construction_cost']:,.0f}원")
    print(f"   Total project cost: {result['total_project_cost']:,.0f}원")
    print(f"   ROI: {result['roi']:.2f}%")
    print(f"   Rating: {result['rating']}")
    print(f"   Decision: {result['decision']}")
    
    # Check mode is correct (STANDARD because < 50 units)
    mode_correct = result['analysis_mode'] == 'STANDARD'
    status = "✅ PASSED" if mode_correct else "❌ FAILED"
    print(f"\n🔍 Validation:")
    print(f"   {status}: Correct mode (STANDARD for < 50 units)")
    
    return result, mode_correct


def test_land_value_integrity():
    """Test 4: Land value must never be recalculated"""
    print("\n" + "="*70)
    print("TEST 4: Land Value Integrity (No Recalculation)")
    print("="*70)
    
    engine = create_lh_analysis_engine()
    
    # Test Case 1: High premium (20%)
    ctx1 = create_mock_appraisal_context(660.0, 5000000, 0.20)
    result1 = engine.analyze(ctx1, 56, 2464.0, address='서울특별시 마포구')
    
    expected_land_value_1 = ctx1.get('calculation.final_appraised_total')
    actual_land_value_1 = result1['land_appraisal']
    
    match1 = expected_land_value_1 == actual_land_value_1
    
    print(f"\n   Test Case 1 (Premium 20%):")
    print(f"      Expected land value: {expected_land_value_1:,.0f}원")
    print(f"      Actual land value: {actual_land_value_1:,.0f}원")
    status = "✅ PASSED" if match1 else "❌ FAILED"
    print(f"      {status}: Values match")
    
    # Test Case 2: Low premium (5%)
    ctx2 = create_mock_appraisal_context(660.0, 5000000, 0.05)
    result2 = engine.analyze(ctx2, 56, 2464.0, address='서울특별시 마포구')
    
    expected_land_value_2 = ctx2.get('calculation.final_appraised_total')
    actual_land_value_2 = result2['land_appraisal']
    
    match2 = expected_land_value_2 == actual_land_value_2
    
    print(f"\n   Test Case 2 (Premium 5%):")
    print(f"      Expected land value: {expected_land_value_2:,.0f}원")
    print(f"      Actual land value: {actual_land_value_2:,.0f}원")
    status = "✅ PASSED" if match2 else "❌ FAILED"
    print(f"      {status}: Values match")
    
    # Verify different premiums give different results
    values_different = expected_land_value_1 != expected_land_value_2
    status = "✅ PASSED" if values_different else "❌ FAILED"
    print(f"\n   {status}: Different premiums → different land values (as expected)")
    
    return match1 and match2 and values_different


def test_end_to_end_flow():
    """Test 5: End-to-end canonical flow"""
    print("\n" + "="*70)
    print("TEST 5: End-to-End Canonical Flow")
    print("="*70)
    
    print(f"\n🔄 Complete Flow Demonstration:")
    print(f"   Step 1: Create Appraisal (FACT)")
    print(f"   Step 2: Lock Context 🔒")
    print(f"   Step 3: LH Analysis (JUDGMENT)")
    
    # Step 1 & 2: Create and lock appraisal
    appraisal_ctx = create_mock_appraisal_context(
        land_area=660.0,
        official_price=5500000,
        premium_rate=0.09
    )
    
    print(f"\n   ✅ Step 1-2 Complete:")
    print(f"      Appraisal locked: {appraisal_ctx.is_locked()}")
    print(f"      Final value: {appraisal_ctx.get('calculation.final_appraised_total'):,.0f}원")
    
    # Step 3: LH Analysis
    engine = create_lh_analysis_engine()
    result = engine.analyze(
        appraisal_ctx=appraisal_ctx,
        expected_units=56,
        total_floor_area=2464.0,
        address='서울특별시 마포구 월드컵북로 120'
    )
    
    print(f"\n   ✅ Step 3 Complete:")
    print(f"      Based on appraisal: {result['based_on_appraisal']}")
    print(f"      Appraisal version: {result['appraisal_reference']['appraisal_version']}")
    print(f"      Appraisal confidence: {result['appraisal_reference']['appraisal_confidence']*100:.0f}%")
    
    # Verify flow correctness
    flow_correct = (
        appraisal_ctx.is_locked() and
        result['based_on_appraisal'] and
        result['land_appraisal'] == appraisal_ctx.get('calculation.final_appraised_total')
    )
    
    print(f"\n   🔍 Flow Validation:")
    status = "✅ PASSED" if flow_correct else "❌ FAILED"
    print(f"      {status}: Complete canonical flow executed correctly")
    
    return flow_correct


def main():
    """Run all Phase 3 tests"""
    print("\n" + "="*70)
    print("🚀 CANONICAL FLOW PHASE 3 TEST SUITE")
    print("   LH Analysis Refactoring")
    print("="*70)
    
    try:
        # Test 1: Engine creation
        engine = test_lh_engine_creation()
        
        # Test 2: LH-linked model
        lh_result, lh_valid = test_lh_linked_model(engine)
        
        # Test 3: Standard model
        std_result, std_valid = test_standard_model(engine)
        
        # Test 4: Land value integrity
        integrity_valid = test_land_value_integrity()
        
        # Test 5: End-to-end flow
        flow_valid = test_end_to_end_flow()
        
        # Final summary
        print("\n" + "="*70)
        print("📊 PHASE 3 TEST RESULTS")
        print("="*70)
        print(f"   1. Engine Creation:           ✅ PASSED")
        print(f"   2. LH-Linked Model:           {'✅ PASSED' if lh_valid else '❌ FAILED'}")
        print(f"   3. Standard Model:            {'✅ PASSED' if std_valid else '❌ FAILED'}")
        print(f"   4. Land Value Integrity:      {'✅ PASSED' if integrity_valid else '❌ FAILED'}")
        print(f"   5. End-to-End Flow:           {'✅ PASSED' if flow_valid else '❌ FAILED'}")
        
        if all([lh_valid, std_valid, integrity_valid, flow_valid]):
            print("\n🎉 ALL TESTS PASSED - Phase 3 Complete!")
            print("\n📝 Implementation Summary:")
            print("   ✅ LHAnalysisCanonical engine created")
            print("   ✅ LH-linked model (공사비 연동제) implemented")
            print("   ✅ Standard model (비연동제) implemented")
            print("   ✅ Land value from appraisal context ONLY")
            print("   ✅ NO land value recalculation")
            print("   ✅ ROI-based rating and decision making")
            print("   ✅ Complete canonical flow validated")
            
            print("\n📝 Next Steps:")
            print("   → Phase 4: Update Report Structure")
            print("   → v8.7: Implement CH4 dynamic scoring")
            print("   → v8.7: Implement CH3.3 ROI-based feasibility scoring")
            print("   → v8.7: Add image generation")
            print("   → Integration: Connect all components in main.py")
            return 0
        else:
            print("\n⚠️  SOME TESTS FAILED - Review implementation")
            return 1
            
    except Exception as e:
        print(f"\n❌ ERROR during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
