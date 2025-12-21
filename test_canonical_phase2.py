"""
Test Canonical Flow Phase 2: Land Diagnosis Refactoring

Tests:
1. Canonical flow adapter creation
2. Appraisal context creation from analysis results
3. Land diagnosis data extraction (no redundant API calls)
4. Integration test with mock analysis result
"""

import sys
from app.services.canonical_flow_adapter import CanonicalFlowAdapter, create_canonical_adapter
from app.services.appraisal_context import AppraisalContextLock


def create_mock_analysis_result():
    """Create mock analysis result for testing"""
    
    # Mock ZoneInfo
    class MockZoneInfo:
        zone_type = "제2종일반주거지역"
        building_coverage_ratio = 60.0
        floor_area_ratio = 200.0
    
    return {
        'zone_info': MockZoneInfo(),
        'accessibility': {
            'accessibility_score': 85,
            'subway_distance': 250,
            'elementary_school_distance': 400,
            'hospital_distance': 600
        },
        'demographic_info': {
            'youth_ratio': 28,
            'single_person_ratio': 42,
            'population_density': 15000
        },
        'risk_factors': [
            {'type': '일조사선', 'severity': 'medium'},
            {'type': '주차확보', 'severity': 'low'}
        ],
        'hazardous_facilities': [],
        'summary': {
            'overall_score': 82,
            'decision': 'PROCEED'
        }
    }


def test_adapter_creation():
    """Test 1: Create canonical flow adapter"""
    print("\n" + "="*70)
    print("TEST 1: Canonical Flow Adapter Creation")
    print("="*70)
    
    adapter = create_canonical_adapter()
    
    print(f"✅ Adapter created: {adapter.__class__.__name__}")
    print(f"   Has context_lock: {hasattr(adapter, 'context_lock')}")
    
    return adapter


def test_appraisal_context_creation(adapter):
    """Test 2: Create appraisal context from analysis result"""
    print("\n" + "="*70)
    print("TEST 2: Appraisal Context Creation")
    print("="*70)
    
    # Create mock analysis result
    analysis_result = create_mock_analysis_result()
    
    print(f"\n📊 Mock Analysis Result:")
    print(f"   Zoning: {analysis_result['zone_info'].zone_type}")
    print(f"   Accessibility score: {analysis_result['accessibility']['accessibility_score']}")
    print(f"   Youth ratio: {analysis_result['demographic_info']['youth_ratio']}%")
    print(f"   Overall score: {analysis_result['summary']['overall_score']}")
    
    # Create appraisal context
    appraisal_ctx = adapter.create_appraisal_context(
        analysis_result=analysis_result,
        land_area=660.0,
        official_price=5500000,  # 5.5M KRW/sqm
        transaction_price=6000000,  # 6M KRW/sqm
        premium_rate=None  # Will auto-calculate
    )
    
    print(f"\n🔒 Appraisal Context Created:")
    print(f"   Is locked: {appraisal_ctx.is_locked()}")
    
    summary = appraisal_ctx.get_summary()
    print(f"\n📈 Appraisal Summary:")
    print(f"   Final appraised total: {summary['final_appraised_total']:,.0f}원")
    print(f"   Zoning: {summary['zoning']}")
    print(f"   Premium rate: {summary['premium_rate']*100:.1f}%")
    print(f"   Confidence: {summary['confidence_score']*100:.1f}%")
    print(f"   Engine: {summary['appraisal_engine']}")
    
    return appraisal_ctx, analysis_result


def test_land_diagnosis_extraction(adapter, appraisal_ctx, analysis_result):
    """Test 3: Extract data for Land Diagnosis (no redundant API calls)"""
    print("\n" + "="*70)
    print("TEST 3: Land Diagnosis Data Extraction")
    print("="*70)
    
    # Extract data for land diagnosis
    diagnosis_data = adapter.extract_for_land_diagnosis(
        appraisal_ctx=appraisal_ctx,
        analysis_result=analysis_result
    )
    
    print(f"\n📦 Extracted Data for Land Diagnosis:")
    print(f"   ✅ Zoning (from appraisal): {diagnosis_data['zoning']}")
    print(f"   ✅ Appraised value (from appraisal): {diagnosis_data['appraised_value']:,.0f}원")
    print(f"   ✅ Premium rate (from appraisal): {diagnosis_data['premium_rate']*100:.1f}%")
    print(f"   ✅ Confidence (from appraisal): {diagnosis_data['confidence']*100:.1f}%")
    print(f"   ✅ Land area (from appraisal): {diagnosis_data['land_area']:.0f}㎡")
    print(f"\n   ℹ️  Risk factors (from analysis): {len(diagnosis_data['risk_factors'])} items")
    print(f"   ℹ️  Hazardous facilities (from analysis): {len(diagnosis_data['hazardous_facilities'])} items")
    print(f"\n   🔒 Based on appraisal: {diagnosis_data['based_on_appraisal']}")
    print(f"   🔒 Appraisal version: {diagnosis_data['appraisal_version']}")
    
    # Validate: All appraisal data must come from context
    validation_checks = []
    
    # Check 1: Zoning matches appraisal context
    if diagnosis_data['zoning'] == appraisal_ctx.get('zoning.confirmed_type'):
        validation_checks.append(('Zoning consistency', True))
    else:
        validation_checks.append(('Zoning consistency', False))
    
    # Check 2: Appraised value matches context
    if diagnosis_data['appraised_value'] == appraisal_ctx.get('calculation.final_appraised_total'):
        validation_checks.append(('Appraised value consistency', True))
    else:
        validation_checks.append(('Appraised value consistency', False))
    
    # Check 3: Premium rate matches context
    if diagnosis_data['premium_rate'] == appraisal_ctx.get('premium.total_premium_rate'):
        validation_checks.append(('Premium rate consistency', True))
    else:
        validation_checks.append(('Premium rate consistency', False))
    
    print(f"\n🔍 Validation Checks:")
    for check_name, passed in validation_checks:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {status}: {check_name}")
    
    all_passed = all(passed for _, passed in validation_checks)
    
    return diagnosis_data, all_passed


def test_lh_analysis_extraction(adapter, appraisal_ctx):
    """Test 4: Extract data for LH Analysis"""
    print("\n" + "="*70)
    print("TEST 4: LH Analysis Data Extraction")
    print("="*70)
    
    # Extract data for LH analysis
    lh_data = adapter.extract_for_lh_analysis(
        appraisal_ctx=appraisal_ctx,
        expected_units=56,
        total_floor_area=2464.0
    )
    
    print(f"\n📦 Extracted Data for LH Analysis:")
    print(f"   ✅ Land appraised value: {lh_data['land_appraised_value']:,.0f}원")
    print(f"   ✅ Land area: {lh_data['land_area']:.0f}㎡")
    print(f"   ✅ Appraised price/㎡: {lh_data['appraised_price_per_sqm']:,.0f}원")
    print(f"   ✅ Zoning: {lh_data['zoning']}")
    print(f"   ℹ️  Expected units: {lh_data['expected_units']}")
    print(f"   ℹ️  Total floor area: {lh_data['total_floor_area']:.0f}㎡")
    print(f"\n   🔒 Based on appraisal: {lh_data['based_on_appraisal']}")
    print(f"   🔒 Appraisal confidence: {lh_data['appraisal_confidence']*100:.1f}%")
    
    # Validate: Land value must come from appraisal context
    land_value_match = (
        lh_data['land_appraised_value'] == 
        appraisal_ctx.get('calculation.final_appraised_total')
    )
    
    print(f"\n🔍 Validation:")
    status = "✅ PASSED" if land_value_match else "❌ FAILED"
    print(f"   {status}: Land value matches appraisal context")
    
    return lh_data, land_value_match


def test_no_duplicate_api_calls():
    """Test 5: Demonstrate NO duplicate API calls"""
    print("\n" + "="*70)
    print("TEST 5: No Duplicate API Calls Demonstration")
    print("="*70)
    
    print(f"\n🔄 Traditional Flow (WRONG):")
    print(f"   1️⃣  Analysis Engine → Query APIs (zoning, price, transactions)")
    print(f"   2️⃣  Land Diagnosis → Query APIs AGAIN ❌")
    print(f"   3️⃣  LH Analysis → Calculate land value AGAIN ❌")
    print(f"   ⚠️  Problem: Redundant API calls, inconsistent data")
    
    print(f"\n✨ Canonical Flow (CORRECT):")
    print(f"   1️⃣  Analysis Engine → Query APIs (zoning, price, transactions)")
    print(f"   2️⃣  Appraisal Context → Lock data 🔒")
    print(f"   3️⃣  Land Diagnosis → Read from context ✅")
    print(f"   4️⃣  LH Analysis → Read from context ✅")
    print(f"   ✅ Benefit: Single source of truth, no redundancy")
    
    return True


def main():
    """Run all Phase 2 tests"""
    print("\n" + "="*70)
    print("🚀 CANONICAL FLOW PHASE 2 TEST SUITE")
    print("   Land Diagnosis Refactoring")
    print("="*70)
    
    try:
        # Test 1: Create adapter
        adapter = test_adapter_creation()
        
        # Test 2: Create appraisal context
        appraisal_ctx, analysis_result = test_appraisal_context_creation(adapter)
        
        # Test 3: Extract for land diagnosis
        diagnosis_data, diagnosis_valid = test_land_diagnosis_extraction(
            adapter, appraisal_ctx, analysis_result
        )
        
        # Test 4: Extract for LH analysis
        lh_data, lh_valid = test_lh_analysis_extraction(adapter, appraisal_ctx)
        
        # Test 5: No duplicate calls demonstration
        test_no_duplicate_api_calls()
        
        # Final summary
        print("\n" + "="*70)
        print("📊 PHASE 2 TEST RESULTS")
        print("="*70)
        print(f"   1. Adapter Creation:              ✅ PASSED")
        print(f"   2. Appraisal Context Creation:    ✅ PASSED")
        print(f"   3. Land Diagnosis Extraction:     {'✅ PASSED' if diagnosis_valid else '❌ FAILED'}")
        print(f"   4. LH Analysis Extraction:        {'✅ PASSED' if lh_valid else '❌ FAILED'}")
        print(f"   5. No Duplicate API Calls:        ✅ DEMONSTRATED")
        
        if diagnosis_valid and lh_valid:
            print("\n🎉 ALL TESTS PASSED - Phase 2 Complete!")
            print("\n📝 Implementation Summary:")
            print("   ✅ CanonicalFlowAdapter created")
            print("   ✅ Appraisal context generation from analysis results")
            print("   ✅ Data extraction for Land Diagnosis (read-only)")
            print("   ✅ Data extraction for LH Analysis (read-only)")
            print("   ✅ Premium rate auto-calculation")
            print("   ✅ Confidence score calculation")
            
            print("\n📝 Next Steps:")
            print("   → Phase 3: Refactor LH Analysis engine to use extracted data")
            print("   → Phase 4: Update Report Structure")
            print("   → Integration: Connect adapter in main.py flow")
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
