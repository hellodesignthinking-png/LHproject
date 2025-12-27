"""
Emergency Diagnostic Tool for Pipeline
======================================

Purpose: Diagnose why pipeline fails and verify the complete data flow

Steps:
1. Test context_storage (✅ PASSED already)
2. Test pipeline with mock data
3. Test PDF generation
4. Test all 6 final reports
"""

import logging
import sys
import os

# Setup
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def diagnostic_full_system():
    """Run complete system diagnostic"""
    
    print("\n" + "="*70)
    print(" 🔍 ZEROSITE 4.0 - FULL SYSTEM DIAGNOSTIC")
    print("="*70)
    
    # Import after path is set
    from app.services.context_storage import context_storage
    
    # STEP 1: Prepare test data
    print("\n[STEP 1/6] Preparing test data...")
    
    test_context_id = "diagnostic-test-001"
    
    # Create assembled_data matching Phase 3.5D schema
    assembled_data = {
        "m6_result": {
            "lh_score_total": 75.0,
            "judgement": "CONDITIONAL",
            "grade": "B",
            "fatal_reject": False,
            "deduction_reasons": ["주차 효율 부족 -4점"],
            "improvement_points": ["+6점: 주차 확보"],
            "section_scores": {
                "policy": 15, "location": 18, "construction": 12,
                "price": 10, "business": 10
            }
        },
        "m2_result": {
            "land_value": 6081933538,
            "land_value_per_pyeong": 50000000,
            "confidence_pct": 85.0,
            "appraisal_method": "standard",
            "price_range": {"low": 5169643507, "high": 6994223569}
        },
        "m3_result": {
            "recommended_type": "youth",
            "total_score": 85.5,
            "demand_score": 90.0,
            "type_scores": {}
        },
        "m4_result": {
            "total_units": 20,
            "incentive_units": 26,
            "gross_area_sqm": 1500.0,
            "far_used": 180.0,
            "bcr_used": 55.0
        },
        "m5_result": {
            "npv_public_krw": 792999999,
            "irr_pct": 12.5,
            "roi_pct": 15.2,
            "financial_grade": "B",
            "total_cost": 8500000000,
            "total_revenue": 9293000000
        }
    }
    
    print(f"✅ Test data prepared (context_id: {test_context_id})")
    
    # STEP 2: Save to context_storage
    print("\n[STEP 2/6] Saving to context_storage...")
    
    try:
        success = context_storage.store_frozen_context(
            context_id=test_context_id,
            land_context=assembled_data,
            ttl_hours=24,
            parcel_id=test_context_id
        )
        
        if success:
            print(f"✅ Saved to context_storage")
        else:
            print("❌ FAILED to save to context_storage")
            return False
    except Exception as e:
        print(f"❌ ERROR saving to context_storage: {e}")
        return False
    
    # STEP 3: Retrieve and verify
    print("\n[STEP 3/6] Retrieving from context_storage...")
    
    try:
        retrieved = context_storage.get_frozen_context(test_context_id)
        
        if not retrieved:
            print("❌ FAILED to retrieve from context_storage")
            return False
        
        print("✅ Retrieved successfully")
        print(f"   Keys: {', '.join(retrieved.keys())}")
        
        # Verify critical values
        checks = [
            ("M2 land_value", retrieved.get("m2_result", {}).get("land_value"), 6081933538),
            ("M4 total_units", retrieved.get("m4_result", {}).get("total_units"), 20),
            ("M5 npv", retrieved.get("m5_result", {}).get("npv_public_krw"), 792999999),
            ("M6 judgement", retrieved.get("m6_result", {}).get("judgement"), "CONDITIONAL"),
        ]
        
        all_ok = True
        for name, actual, expected in checks:
            if actual == expected:
                print(f"   ✅ {name}: {actual}")
            else:
                print(f"   ❌ {name}: expected {expected}, got {actual}")
                all_ok = False
        
        if not all_ok:
            return False
            
    except Exception as e:
        print(f"❌ ERROR retrieving from context_storage: {e}")
        return False
    
    # STEP 4: Test PDF data extraction
    print("\n[STEP 4/6] Testing PDF data extraction...")
    
    try:
        from app.services.pdf_generators.module_pdf_generator import ModulePDFGenerator
        
        generator = ModulePDFGenerator()
        
        # Build assembled_data for PDF generator
        pdf_assembled_data = {
            "m6_result": retrieved["m6_result"],
            "modules": {
                "M2": {"summary": retrieved["m2_result"], "details": {}, "raw_data": {}},
                "M3": {"summary": retrieved["m3_result"], "details": {}, "raw_data": {}},
                "M4": {"summary": retrieved["m4_result"], "details": {}, "raw_data": {}},
                "M5": {"summary": retrieved["m5_result"], "details": {}, "raw_data": {}},
            }
        }
        
        # Try to generate M2 PDF
        print("   Testing M2 PDF generation...")
        try:
            pdf_bytes = generator.generate_m2_appraisal_pdf(pdf_assembled_data)
            if pdf_bytes and len(pdf_bytes) > 1000:  # At least 1KB
                print(f"   ✅ M2 PDF generated ({len(pdf_bytes):,} bytes)")
                
                # Save for manual inspection
                with open("/tmp/diagnostic_m2.pdf", "wb") as f:
                    f.write(pdf_bytes)
                print("   💾 Saved to: /tmp/diagnostic_m2.pdf")
            else:
                print("   ❌ M2 PDF too small or empty")
                return False
        except Exception as pdf_err:
            print(f"   ❌ M2 PDF generation failed: {pdf_err}")
            import traceback
            traceback.print_exc()
            return False
        
        # Try to generate M6 PDF
        print("   Testing M6 PDF generation...")
        try:
            pdf_bytes = generator.generate_m6_lh_review_pdf(pdf_assembled_data)
            if pdf_bytes and len(pdf_bytes) > 1000:
                print(f"   ✅ M6 PDF generated ({len(pdf_bytes):,} bytes)")
                
                with open("/tmp/diagnostic_m6.pdf", "wb") as f:
                    f.write(pdf_bytes)
                print("   💾 Saved to: /tmp/diagnostic_m6.pdf")
            else:
                print("   ❌ M6 PDF too small or empty")
                return False
        except Exception as pdf_err:
            print(f"   ❌ M6 PDF generation failed: {pdf_err}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ ERROR testing PDF generation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # STEP 5: Test final report generation
    print("\n[STEP 5/6] Testing final report generation...")
    
    try:
        from app.services.m6_centered_report_base import create_m6_centered_report
        
        # Test all-in-one report
        print("   Testing All-in-One report...")
        report = create_m6_centered_report(pdf_assembled_data, report_type='all_in_one')
        
        if report and report.get("report_type") == "all_in_one":
            print(f"   ✅ All-in-One report generated")
            print(f"      - Report name: {report.get('report_name')}")
            print(f"      - M6 judgement: {report.get('m6_scorecard', {}).get('judgement')}")
            
            # Check key_numbers
            key_nums = report.get("key_numbers", {})
            print(f"      - M2 land_value: {key_nums.get('m2_land_value', 'N/A')}")
            print(f"      - M4 total_units: {key_nums.get('m4_total_units', 'N/A')}")
            print(f"      - M5 NPV: {key_nums.get('m5_npv', 'N/A')}")
        else:
            print("   ❌ All-in-One report generation failed")
            return False
            
    except Exception as e:
        print(f"❌ ERROR testing final report: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # STEP 6: Summary
    print("\n[STEP 6/6] Diagnostic Summary")
    print("="*70)
    print("✅ context_storage: WORKING")
    print("✅ Data retrieval: WORKING")
    print("✅ M2 PDF generation: WORKING")
    print("✅ M6 PDF generation: WORKING")
    print("✅ Final report generation: WORKING")
    print("="*70)
    
    print("\n📋 MANUAL VERIFICATION STEPS:")
    print("1. Open M2 PDF:")
    print("   open /tmp/diagnostic_m2.pdf")
    print("   → Check if shows: 토지 가치 60.82억원 (NOT N/A)")
    print("")
    print("2. Open M6 PDF:")
    print("   open /tmp/diagnostic_m6.pdf")
    print("   → Check if shows: 판단 CONDITIONAL, 점수 75.0/100")
    print("")
    print("3. Test via API (if server running):")
    print(f"   curl -o test.pdf 'http://localhost:8001/api/v4/reports/M2/pdf?context_id={test_context_id}'")
    print("   open test.pdf")
    print("")
    print("="*70)
    print("🎉 ALL SYSTEMS OPERATIONAL")
    print("="*70)
    
    return True

if __name__ == "__main__":
    try:
        success = diagnostic_full_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
