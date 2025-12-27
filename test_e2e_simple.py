#!/usr/bin/env python3
"""
ZeroSite 4.0 Simplified E2E Test
================================
Tests the critical data flow: Pipeline → context_storage → PDFs

Author: ZeroSite Backend Team
Date: 2025-12-27
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.context_storage import context_storage
from app.services.pdf_generators.module_pdf_generator import ModulePDFGenerator


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_simple_e2e():
    """Test simplified E2E: assembled_data → storage → PDF"""
    
    print_header("ZeroSite 4.0 Simplified E2E Test")
    print("Testing: assembled_data → context_storage → Module PDFs")
    
    context_id = "simple-e2e-test"
    
    # ========== STEP 1: Create Phase 3.5D assembled_data ==========
    print("\n[STEP 1/4] Creating Phase 3.5D assembled_data")
    print("-" * 60)
    
    assembled_data = {
        "m6_result": {
            "lh_score_total": 75.0,
            "judgement": "CONDITIONAL",
            "grade": "B+",
            "fatal_reject": False,
            "deduction_reasons": ["일부 기준 미달"],
            "improvement_points": ["도로 폭 확보 필요"],
            "section_scores": {
                "policy": 15,
                "location": 18,
                "construction": 12,
                "price": 10,
                "business": 10
            },
        },
        "modules": {
            "M2": {
                "summary": {
                    "land_value": 6081933539,
                    "land_value_per_pyeong": 50000000,
                    "confidence_pct": 85.0,
                    "appraisal_method": "시세비교법",
                    "price_range": {
                        "low": 5169643308,
                        "high": 6994223770,
                    }
                },
                "details": {},
                "raw_data": {}
            },
            "M3": {
                "summary": {
                    "recommended_type": "youth",
                    "total_score": 85.5,
                    "demand_score": 90.0,
                },
                "details": {},
                "raw_data": {}
            },
            "M4": {
                "summary": {
                    "total_units": 20,
                    "incentive_units": 26,
                    "gross_area_sqm": 1680,
                    "far_used": 2.3,
                    "bcr_used": 0.55,
                },
                "details": {},
                "raw_data": {}
            },
            "M5": {
                "summary": {
                    "npv_public_krw": 792999999,
                    "irr_pct": 12.5,
                    "roi_pct": 18.7,
                    "financial_grade": "B+",
                    "total_cost": 3964999995,
                    "total_revenue": 4757999994,
                },
                "details": {},
                "raw_data": {}
            },
            "M6": {
                "summary": {
                    "lh_score_total": 75.0,
                    "judgement": "CONDITIONAL",
                    "grade": "B+",
                },
                "details": {},
                "raw_data": {}
            }
        },
        "_frozen": True,
        "_context_id": context_id,
    }
    
    print(f"✓ assembled_data created")
    print(f"  - Context ID: {context_id}")
    print(f"  - M6 Judgement: {assembled_data['m6_result']['judgement']}")
    print(f"  - M6 Score: {assembled_data['m6_result']['lh_score_total']}/100")
    print(f"  - M2 Land Value: {assembled_data['modules']['M2']['summary']['land_value']:,}원")
    print(f"  - M4 Units: {assembled_data['modules']['M4']['summary']['total_units']}세대")
    print(f"  - M5 NPV: {assembled_data['modules']['M5']['summary']['npv_public_krw']:,}원")
    
    # ========== STEP 2: Save to context_storage ==========
    print("\n[STEP 2/4] Saving to context_storage")
    print("-" * 60)
    
    try:
        context_storage.store_frozen_context(
            context_id=context_id,
            land_context=assembled_data,
            ttl_hours=24,
            parcel_id=context_id
        )
        print(f"✓ Saved to context_storage")
    except Exception as e:
        print(f"✗ Failed to save: {e}")
        return False
    
    # ========== STEP 3: Retrieve from context_storage ==========
    print("\n[STEP 3/4] Retrieving from context_storage")
    print("-" * 60)
    
    try:
        retrieved = context_storage.get_frozen_context(context_id)
        if not retrieved:
            print(f"✗ Failed to retrieve context")
            return False
        
        print(f"✓ Retrieved successfully")
        print(f"  - Keys: {list(retrieved.keys())}")
        print(f"  - M2 land_value: {retrieved['modules']['M2']['summary']['land_value']:,}원")
        print(f"  - M6 judgement: {retrieved['m6_result']['judgement']}")
        
    except Exception as e:
        print(f"✗ Retrieval failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ========== STEP 4: Generate PDFs ==========
    print("\n[STEP 4/4] Generating Module PDFs (M2, M6)")
    print("-" * 60)
    
    try:
        pdf_gen = ModulePDFGenerator()
        
        # Generate M2 PDF
        print("\nGenerating M2 PDF...")
        m2_pdf = pdf_gen.generate_m2_appraisal_pdf(retrieved)
        print(f"✓ M2 PDF: {len(m2_pdf):,} bytes")
        Path("/tmp/simple_m2.pdf").write_bytes(m2_pdf)
        print(f"  → Saved to /tmp/simple_m2.pdf")
        
        # Generate M6 PDF
        print("\nGenerating M6 PDF...")
        m6_pdf = pdf_gen.generate_m6_lh_review_pdf(retrieved)
        print(f"✓ M6 PDF: {len(m6_pdf):,} bytes")
        Path("/tmp/simple_m6.pdf").write_bytes(m6_pdf)
        print(f"  → Saved to /tmp/simple_m6.pdf")
        
    except Exception as e:
        print(f"✗ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ========== SUMMARY ==========
    print_header("✅ ALL TESTS PASSED")
    
    print("Data Flow Verified:")
    print("  1. assembled_data created ✓")
    print("  2. Saved to context_storage ✓")
    print("  3. Retrieved from context_storage ✓")
    print("  4. PDFs generated ✓")
    
    print("\nExpected Values:")
    print(f"  ✓ 토지 가치: 60.82억원")
    print(f"  ✓ 평당 단가: 5,000만원")
    print(f"  ✓ 세대수: 20세대")
    print(f"  ✓ NPV: 7.93억원")
    print(f"  ✓ M6 판단: CONDITIONAL")
    print(f"  ✓ M6 점수: 75.0/100")
    
    print("\nManual Verification:")
    print("  1. Open /tmp/simple_m2.pdf")
    print("     → Check 토지 가치: 60.82억원")
    print("     → Check 평당 단가: 5,000만원")
    print("     → Check 신뢰도: 85.0%")
    print("")
    print("  2. Open /tmp/simple_m6.pdf")
    print("     → Check M6 판단: CONDITIONAL")
    print("     → Check M6 점수: 75.0/100")
    print("     → Check M6 등급: B+")
    
    return True


if __name__ == "__main__":
    try:
        success = test_simple_e2e()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
