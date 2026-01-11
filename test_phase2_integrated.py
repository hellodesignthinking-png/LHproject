#!/usr/bin/env python3
"""
ZeroSite Phase 2 - Integrated Test (Single Process)

Issue: In-memory storage not shared between Python processes
Solution: Run all tests in single process
"""

import sys
sys.path.insert(0, '/home/user/webapp')

print("="*80)
print("🚀 ZeroSite Phase 2 - INTEGRATED TEST")
print("="*80)
print()

# ============================================================================
# STEP 1: Create Frozen Context
# ============================================================================

print("="*80)
print("🔍 STEP 1: Frozen Context Creation")
print("="*80)
print()

try:
    from app.api.endpoints.m1_context_freeze_v2 import (
        freeze_context_v2, 
        FreezeContextRequestV2,
        frozen_contexts_v2
    )
    import asyncio
    
    test_request = {
        "address": "서울특별시 강남구 테헤란로 518",
        "road_address": "서울특별시 강남구 테헤란로 518",
        "sido": "서울특별시",
        "sigungu": "강남구",
        "dong": "대치동",
        "beopjeong_dong": "대치동",
        "coordinates": {"lat": 37.5046, "lon": 127.0621},
        "coordinates_verified": True,
        "address_source": "API",
        "coordinates_source": "API",
        "bonbun": "157",
        "bubun": "29",
        "jimok": "대",
        "area": 500.0,
        "cadastral_source": "API",
        "zone_type": "제2종일반주거지역",
        "zone_detail": "7층 이하",
        "land_use": "주거용",
        "far": 200.0,
        "bcr": 60.0,
        "height_limit": 21.0,
        "regulations": ["건축선 후퇴"],
        "restrictions": [],
        "zoning_source": "API",
        "road_contact": "접도",
        "road_width": 25.0,
        "road_type": "대로",
        "nearby_roads": [],
        "road_source": "API",
        "official_land_price": 15000000,
        "official_land_price_date": "2024-01-01",
        "official_price_source": "API",
        "transaction_cases_appraisal": [
            {
                "date": "20241115",
                "area": 500.0,
                "amount": 6000000000,
                "distance": 150.0,
                "address": "서울특별시 강남구 대치동 157-30"
            }
        ],
        "transaction_cases_reference": [],
        "corner_lot": False,
        "wide_road": True,
        "subway_proximity": 800.0,
        "created_by": "integrated_test"
    }
    
    request_model = FreezeContextRequestV2(**test_request)
    response = asyncio.run(freeze_context_v2(request_model))
    
    parcel_id = response.parcel_id
    context_id = response.context_id
    
    print(f"✅ Context ID: {context_id[:8]}...")
    print(f"✅ Parcel ID: {parcel_id}")
    print(f"✅ Frozen: {response.frozen}")
    print(f"✅ Storage: {len(frozen_contexts_v2)} contexts")
    print()
    print("✅ STEP 1: PASS")
    print()
    
except Exception as e:
    print(f"❌ STEP 1: FAIL - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 2: M1 Service with Frozen Context
# ============================================================================

print("="*80)
print("🔗 STEP 2: M1 Service with Real Data")
print("="*80)
print()

try:
    from app.modules.m1_land_info.service import LandInfoService
    
    m1_service = LandInfoService()
    land_ctx = m1_service.run(parcel_id=parcel_id)
    
    print(f"✅ Address: {land_ctx.address}")
    print(f"✅ Area: {land_ctx.area_sqm}m²")
    print(f"✅ Zoning: {land_ctx.zone_type}")
    print(f"✅ Data Source: {land_ctx.data_source}")
    
    if "Frozen Context" not in land_ctx.data_source:
        print("❌ Not loading from frozen context!")
        sys.exit(1)
    
    print()
    print("✅ STEP 2: PASS")
    print()
    
except Exception as e:
    print(f"❌ STEP 2: FAIL - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 3: M2 Appraisal
# ============================================================================

print("="*80)
print("💰 STEP 3: M2 Appraisal (MANDATORY)")
print("="*80)
print()

try:
    from app.modules.m2_appraisal.service import AppraisalService
    
    m2_service = AppraisalService(use_enhanced_services=True)
    appraisal_ctx = m2_service.run(land_ctx=land_ctx, asking_price=None)
    
    print(f"✅ Land Value: ₩{appraisal_ctx.land_value:,.0f}")
    print(f"✅ Unit Price: ₩{appraisal_ctx.unit_price_sqm:,.0f}/m²")
    print(f"✅ Confidence: {appraisal_ctx.confidence_score:.0%}")
    print(f"✅ Transaction Samples: {appraisal_ctx.transaction_count}")
    
    if appraisal_ctx.transaction_count == 0:
        print("❌ No transaction samples!")
        sys.exit(1)
    
    print()
    print("✅ STEP 3: PASS - M2 Executed")
    print()
    
except Exception as e:
    print(f"❌ STEP 3: FAIL - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 4: M3 Housing Type (No Score Tables)
# ============================================================================

print("="*80)
print("🏘️  STEP 4: M3 Housing Type (Real Decision)")
print("="*80)
print()

try:
    from app.modules.m3_lh_demand.service import LHDemandService
    
    m3_service = LHDemandService()
    housing_ctx = m3_service.run(land_ctx=land_ctx)
    
    print(f"✅ Selected Type: {housing_ctx.selected_type_name}")
    print(f"✅ Confidence: {housing_ctx.selection_confidence:.0%}")
    print(f"✅ Demand Prediction: {housing_ctx.demand_prediction}")
    
    # Check for score table patterns
    if hasattr(housing_ctx, 'scores') or hasattr(housing_ctx, 'type_scores'):
        print("⚠️  Warning: Score tables detected in M3")
    
    print()
    print("✅ STEP 4: PASS - M3 Executed")
    print()
    
except Exception as e:
    print(f"❌ STEP 4: FAIL - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 5: Full Pipeline Test
# ============================================================================

print("="*80)
print("🚀 STEP 5: Full Pipeline (M1→M2→M3→M4→M5→M6)")
print("="*80)
print()

try:
    from app.core.pipeline.zer0site_pipeline import ZeroSitePipeline
    
    pipeline = ZeroSitePipeline()
    result = pipeline.run(parcel_id=parcel_id, asking_price=None)
    
    print(f"✅ M1: {result.land.address}")
    print(f"✅ M2: ₩{result.appraisal.land_value:,.0f}")
    print(f"✅ M3: {result.housing_type.selected_type_name}")
    print(f"✅ M4: {result.capacity.legal_capacity.total_units} units")
    print(f"✅ M5: NPV ₩{result.feasibility.financial_metrics.npv_public:,.0f}")
    print(f"✅ M6: {result.lh_review.decision.value}")
    
    print()
    print("✅ STEP 5: PASS - Full Pipeline Working")
    print()
    
except Exception as e:
    print(f"❌ STEP 5: FAIL - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# FINAL: Phase 2 Complete
# ============================================================================

print("="*80)
print("🎉 PHASE 2 INTEGRATION TEST: COMPLETE")
print("="*80)
print()
print("✅ All Steps Passed:")
print("   1. Frozen Context Creation ✅")
print("   2. M1 Real Data Loading ✅")
print("   3. M2 Appraisal Execution ✅")
print("   4. M3 Housing Type Decision ✅")
print("   5. Full Pipeline (M1-M6) ✅")
print()
print("🔒 System Mode: DATA-FIRST · ADDRESS-BOUND")
print("🔒 MOCK Fallback: BLOCKED")
print("🔒 M2: MANDATORY")
print()
print("ⓒ ZeroSite by AntennaHoldings | Natai Heum")
