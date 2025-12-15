"""
Test Canonical Flow Phase 1: AppraisalContextLock + Canonical Schema

Tests:
1. Canonical Schema creation
2. AppraisalContextLock functionality
3. Data integrity validation
4. Read-only enforcement
"""

import sys
from datetime import datetime
from app.services.canonical_schema import (
    CanonicalAppraisalResult,
    ZoningInfo,
    OfficialLandPrice,
    TransactionCase,
    PremiumInfo,
    PremiumDetail,
    CalculationInfo,
    ConfidenceInfo,
    ConfidenceFactors,
    MetadataInfo,
    create_appraisal_from_analysis
)
from app.services.appraisal_context import AppraisalContextLock


def test_canonical_schema_creation():
    """Test 1: Create a canonical appraisal result"""
    print("\n" + "="*70)
    print("TEST 1: Canonical Schema Creation")
    print("="*70)
    
    # Create a complete canonical result
    appraisal_result = CanonicalAppraisalResult(
        version="v8.7",
        zoning=ZoningInfo(
            confirmed_type="제2종일반주거지역",
            building_coverage_ratio=60.0,
            floor_area_ratio=200.0,
            source="국토부 API"
        ),
        official_land_price=OfficialLandPrice(
            standard_price_per_sqm=5500000,
            reference_year=2024,
            reference_parcel="서울특별시 마포구 월드컵북로 120",
            distance_to_standard=0.0
        ),
        transaction_cases=[
            TransactionCase(
                price_per_sqm=6000000,
                transaction_date="2024-10-15",
                distance_m=100,
                area_sqm=660,
                similarity_score=0.95
            )
        ],
        premium=PremiumInfo(
            development_potential=PremiumDetail(
                rate=0.04,
                rationale="역세권 개발 가능성"
            ),
            location_premium=PremiumDetail(
                rate=0.03,
                rationale="지하철 300m 이내"
            ),
            policy_benefit=PremiumDetail(
                rate=0.02,
                rationale="LH 우선 매입 지역"
            ),
            total_premium_rate=0.09
        ),
        calculation=CalculationInfo(
            base_price_per_sqm=5775000,  # 5,500,000 * 1.05
            premium_adjusted_per_sqm=6294750,  # 5,775,000 * 1.09
            land_area_sqm=660.0,
            final_appraised_total=4154535000  # 6,294,750 * 660
        ),
        confidence=ConfidenceInfo(
            score=0.92,
            factors=ConfidenceFactors(
                data_completeness=0.95,
                case_similarity=0.95,
                time_relevance=0.90
            )
        ),
        metadata=MetadataInfo(
            appraisal_engine="ZeroSite v8.7",
            calculation_method="비교방식",
            appraiser_note="거래사례 1건 기준, 프리미엄 9% 적용"
        )
    )
    
    print(f"✅ Canonical appraisal result created")
    print(f"   Final appraised total: {appraisal_result.calculation.final_appraised_total:,.0f}원")
    print(f"   Zoning: {appraisal_result.zoning.confirmed_type}")
    print(f"   Premium rate: {appraisal_result.premium.total_premium_rate*100:.1f}%")
    print(f"   Confidence: {appraisal_result.confidence.score*100:.1f}%")
    
    return appraisal_result


def test_appraisal_context_lock(appraisal_result):
    """Test 2: Lock appraisal context and test read-only"""
    print("\n" + "="*70)
    print("TEST 2: AppraisalContextLock Functionality")
    print("="*70)
    
    # Create context lock
    ctx = AppraisalContextLock()
    
    print(f"\n📍 Before locking:")
    print(f"   Is locked: {ctx.is_locked()}")
    
    # Lock the context
    ctx.lock(appraisal_result.to_context_dict())
    
    print(f"\n🔒 After locking:")
    print(f"   Is locked: {ctx.is_locked()}")
    print(f"   Locked at: {ctx.get_locked_at()}")
    
    # Test reading locked data
    print(f"\n📖 Reading locked data:")
    final_value = ctx.get('calculation.final_appraised_total')
    zoning = ctx.get('zoning.confirmed_type')
    premium = ctx.get('premium.total_premium_rate')
    
    print(f"   ✓ Final appraised total: {final_value:,.0f}원")
    print(f"   ✓ Zoning: {zoning}")
    print(f"   ✓ Premium rate: {premium*100:.1f}%")
    
    # Test trying to lock again (should fail)
    print(f"\n🚫 Testing double-lock prevention:")
    try:
        ctx.lock(appraisal_result.to_context_dict())
        print("   ❌ FAILED: Double lock was allowed!")
        return False
    except ValueError as e:
        print(f"   ✅ PASSED: Double lock prevented: {str(e)[:50]}...")
    
    return ctx


def test_data_integrity(ctx):
    """Test 3: Validate data integrity"""
    print("\n" + "="*70)
    print("TEST 3: Data Integrity Validation")
    print("="*70)
    
    is_valid = ctx.validate_integrity()
    print(f"   Data integrity: {'✅ VALID' if is_valid else '❌ INVALID'}")
    
    summary = ctx.get_summary()
    print(f"\n📊 Context Summary:")
    print(f"   Locked: {summary['locked']}")
    print(f"   Final appraised total: {summary['final_appraised_total']:,.0f}원")
    print(f"   Zoning: {summary['zoning']}")
    print(f"   Premium rate: {summary['premium_rate']*100:.1f}%")
    print(f"   Confidence: {summary['confidence_score']*100:.1f}%")
    print(f"   Engine: {summary['appraisal_engine']}")
    print(f"   Transaction cases: {summary['transaction_cases_count']}")
    
    return is_valid


def test_read_only_enforcement(ctx):
    """Test 4: Ensure read-only enforcement"""
    print("\n" + "="*70)
    print("TEST 4: Read-Only Enforcement")
    print("="*70)
    
    # Get full context
    full_context = ctx.get_full_context()
    
    print(f"   Original final value: {full_context['calculation']['final_appraised_total']:,.0f}원")
    
    # Try to modify (should not affect the locked context)
    full_context['calculation']['final_appraised_total'] = 999999
    
    # Read again - should still be original value
    new_value = ctx.get('calculation.final_appraised_total')
    
    if new_value == 999999:
        print(f"   ❌ FAILED: Data was modified (read-only not enforced)")
        return False
    else:
        print(f"   ✅ PASSED: Data unchanged ({new_value:,.0f}원) - read-only enforced via deep copy")
        return True


def test_helper_function():
    """Test 5: Test helper function for conversion"""
    print("\n" + "="*70)
    print("TEST 5: Helper Function (create_appraisal_from_analysis)")
    print("="*70)
    
    # Mock zone info
    class MockZoneInfo:
        zone_type = "제2종일반주거지역"
        building_coverage_ratio = 60.0
        floor_area_ratio = 200.0
    
    zone_info = MockZoneInfo()
    
    # Create appraisal using helper
    appraisal = create_appraisal_from_analysis(
        zone_info=zone_info,
        land_area=660.0,
        official_price=5500000,
        transaction_price=6000000,
        premium_rate=0.09,
        confidence_score=0.92
    )
    
    print(f"✅ Appraisal created via helper function")
    print(f"   Final appraised total: {appraisal.calculation.final_appraised_total:,.0f}원")
    print(f"   Base price: {appraisal.calculation.base_price_per_sqm:,.0f}원/㎡")
    print(f"   Premium adjusted: {appraisal.calculation.premium_adjusted_per_sqm:,.0f}원/㎡")
    print(f"   Zoning: {appraisal.zoning.confirmed_type}")
    
    return appraisal


def main():
    """Run all Phase 1 tests"""
    print("\n" + "="*70)
    print("🚀 CANONICAL FLOW PHASE 1 TEST SUITE")
    print("   AppraisalContextLock + Canonical Schema")
    print("="*70)
    
    try:
        # Test 1: Create canonical schema
        appraisal_result = test_canonical_schema_creation()
        
        # Test 2: Lock context
        ctx = test_appraisal_context_lock(appraisal_result)
        
        # Test 3: Validate integrity
        is_valid = test_data_integrity(ctx)
        
        # Test 4: Read-only enforcement
        is_readonly = test_read_only_enforcement(ctx)
        
        # Test 5: Helper function
        helper_appraisal = test_helper_function()
        
        # Final summary
        print("\n" + "="*70)
        print("📊 PHASE 1 TEST RESULTS")
        print("="*70)
        print(f"   1. Canonical Schema Creation:     ✅ PASSED")
        print(f"   2. Context Lock Functionality:    ✅ PASSED")
        print(f"   3. Data Integrity Validation:     {'✅ PASSED' if is_valid else '❌ FAILED'}")
        print(f"   4. Read-Only Enforcement:         {'✅ PASSED' if is_readonly else '❌ FAILED'}")
        print(f"   5. Helper Function:               ✅ PASSED")
        
        if is_valid and is_readonly:
            print("\n🎉 ALL TESTS PASSED - Phase 1 Complete!")
            print("\n📝 Next Steps:")
            print("   → Phase 2: Refactor Land Diagnosis to use AppraisalContextLock")
            print("   → Phase 3: Refactor LH Analysis to use AppraisalContextLock")
            print("   → Phase 4: Update Report Structure with canonical data")
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
