#!/usr/bin/env python3
"""
End-to-End Pipeline Test
=========================

Tests the complete user flow:
1. M1 Context Freeze (프론트엔드에서 "분석 시작" 버튼)
2. Pipeline Analyze (M2-M6 실행)
3. PDF Generation (보고서 생성)
"""

import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_e2e_flow():
    """Test complete end-to-end flow"""
    
    print("\n" + "="*70)
    print(" 🔍 END-TO-END PIPELINE TEST")
    print("="*70)
    
    # Step 1: Mock M1 Context Freeze
    print("\n[STEP 1/4] M1 Context Freeze (simulate user input)...")
    
    from app.services.context_storage import context_storage
    from app.core.context.m1_final_context import M1FinalContext, LandInfo, AddressInfo, CoordinatesInfo, CadastralInfo, ZoningInfo, create_parcel_id
    
    # Create a realistic M1 context
    parcel_id = create_parcel_id(
        sido="서울특별시",
        sigungu="강남구",
        dong="테헤란로",
        bonbun="123",
        bubun="0"
    )
    
    print(f"   Generated parcel_id: {parcel_id}")
    
    # Build M1FinalContext (simplified)
    m1_context_dict = {
        "context_id": "test-e2e-001",
        "parcel_id": parcel_id,
        "frozen": True,
        "land_info": {
            "address": {
                "road_address": "서울특별시 강남구 테헤란로 123",
                "jibun_address": "서울특별시 강남구 삼성동 123",
                "sido": "서울특별시",
                "sigungu": "강남구",
                "dong": "삼성동",
                "beopjeong_dong": "삼성동"
            },
            "coordinates": {
                "latitude": 37.508,
                "longitude": 127.063
            },
            "cadastral": {
                "bonbun": "123",
                "bubun": "0",
                "jimok": "대",
                "area_sqm": 1000.0,
                "area_pyeong": 302.5
            },
            "zoning": {
                "zone_type": "제2종일반주거지역",
                "zone_detail": None,
                "land_use": "주거용",
                "far": 200.0,
                "bcr": 60.0,
                "height_limit": None
            }
        }
    }
    
    # Save to context_storage
    try:
        success = context_storage.store_frozen_context(
            context_id="test-e2e-001",
            land_context=m1_context_dict,
            ttl_hours=24,
            parcel_id=parcel_id
        )
        
        if success:
            print(f"   ✅ M1 context saved: test-e2e-001")
        else:
            print("   ❌ Failed to save M1 context")
            return False
    except Exception as e:
        print(f"   ❌ Error saving M1 context: {e}")
        return False
    
    # Step 2: Run Pipeline
    print("\n[STEP 2/4] Running Pipeline (M1→M2→M3→M4→M5→M6)...")
    
    try:
        from app.core.pipeline.zer0site_pipeline import ZeroSitePipeline
        
        pipeline = ZeroSitePipeline()
        result = pipeline.run(parcel_id)
        
        print(f"   ✅ Pipeline completed")
        print(f"   - Land value: {result.appraisal.land_value:,.0f}원")
        print(f"   - Housing type: {result.housing_type.selected_type}")
        print(f"   - Units: {result.capacity.unit_summary.total_units}세대")
        print(f"   - NPV: {result.feasibility.financial_metrics.npv_public:,.0f}원")
        print(f"   - LH Decision: {result.lh_review.decision}")
        
    except Exception as e:
        print(f"   ❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Check if data saved to context_storage
    print("\n[STEP 3/4] Checking if pipeline saved data to context_storage...")
    
    try:
        # Pipeline should have saved assembled_data
        stored_data = context_storage.get_frozen_context(parcel_id)
        
        if not stored_data:
            print(f"   ❌ No data found in context_storage for parcel_id: {parcel_id}")
            print("   💡 This is the PROBLEM! Pipeline didn't save data.")
            return False
        
        # Check if it has m2_result, m4_result, etc.
        has_m2 = "m2_result" in stored_data
        has_m4 = "m4_result" in stored_data
        has_m6 = "m6_result" in stored_data
        
        print(f"   {'✅' if has_m2 else '❌'} M2 data: {has_m2}")
        print(f"   {'✅' if has_m4 else '❌'} M4 data: {has_m4}")
        print(f"   {'✅' if has_m6 else '❌'} M6 data: {has_m6}")
        
        if not (has_m2 and has_m4 and has_m6):
            print("   ⚠️ Pipeline result not in expected format")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking context_storage: {e}")
        return False
    
    # Step 4: Test PDF Generation
    print("\n[STEP 4/4] Testing PDF Generation...")
    
    try:
        from app.services.pdf_generators.module_pdf_generator import ModulePDFGenerator
        
        generator = ModulePDFGenerator()
        
        # Build assembled_data from stored data
        assembled_data = {
            "m6_result": stored_data.get("m6_result", {}),
            "modules": {
                "M2": {"summary": stored_data.get("m2_result", {}), "details": {}, "raw_data": {}},
                "M4": {"summary": stored_data.get("m4_result", {}), "details": {}, "raw_data": {}},
                "M5": {"summary": stored_data.get("m5_result", {}), "details": {}, "raw_data": {}},
            }
        }
        
        # Generate M2 PDF
        pdf_bytes = generator.generate_m2_appraisal_pdf(assembled_data)
        
        if pdf_bytes and len(pdf_bytes) > 1000:
            print(f"   ✅ M2 PDF generated: {len(pdf_bytes):,} bytes")
            
            # Save for inspection
            with open("/tmp/e2e_test_m2.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("   💾 Saved to: /tmp/e2e_test_m2.pdf")
        else:
            print("   ❌ M2 PDF generation failed or empty")
            return False
            
    except Exception as e:
        print(f"   ❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "="*70)
    print("✅ END-TO-END TEST PASSED")
    print("="*70)
    print("\n📋 Test Context:")
    print(f"   - Context ID: test-e2e-001")
    print(f"   - Parcel ID: {parcel_id}")
    print("\n📋 API Calls (equivalent):")
    print(f"   1. POST /api/m1/freeze-context-v2")
    print(f"   2. POST /api/v4/pipeline/analyze (parcel_id={parcel_id})")
    print(f"   3. GET /api/v4/reports/M2/pdf?context_id={parcel_id}")
    print("\n📋 Files Created:")
    print("   - /tmp/e2e_test_m2.pdf (open to verify)")
    
    return True

if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        success = test_e2e_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ E2E test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
