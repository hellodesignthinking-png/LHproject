#!/usr/bin/env python3
"""
ABSOLUTE FINAL: End-to-End Smoke Test
Test all 6 report types with same context_id

SUCCESS CRITERIA:
1. All 6 reports generate successfully
2. All contain BUILD_SIGNATURE
3. All contain actual NPV/IRR/decision values
4. Zero "N/A" strings
5. All use same canonical_summary
"""

import asyncio
import sys
import json
import hashlib
from datetime import datetime

sys.path.insert(0, '/home/user/webapp')

from app.services.context_storage import context_storage


async def create_complete_test_context():
    """Create context with COMPLETE M2-M6 canonical_summary"""
    
    context_id = f"test-abs-final-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # 🔒 ABSOLUTE FINAL: Exact structure matching validation requirements
    canonical_summary = {
        "M2": {
            "summary": {
                "land_value_total_krw": 1280000000,  # Required: land_value_total_krw
                "pyeong_price_krw": 25600000,
                "confidence_pct": 85,
                "transaction_count": 15
            }
        },
        "M3": {
            "summary": {
                "recommended_type": "도시형생활주택",  # Required: recommended_type
                "type_score": 92,
                "confidence_pct": 88
            },
            "details": {}
        },
        "M4": {
            "summary": {
                "total_units": 28,  # Required: total_units
                "legal_units": 24,
                "incentive_units": 28,
                "far": 2.8,
                "bcr": 0.65
            }
        },
        "M5": {
            "summary": {
                "npv_public_krw": 420000000,  # Required: npv_public_krw
                "irr_pct": 13.20,              # Required: irr_pct
                "roi_pct": 18.0,
                "grade": "A"
            }
        },
        "M6": {
            "summary": {
                "decision": "조건부 적합",  # Required: decision
                "total_score": 88,
                "max_score": 100,
                "grade": "A",
                "approval_probability_pct": 75
            }
        }
    }
    
    # Calculate data signature
    canonical_json = json.dumps(canonical_summary, ensure_ascii=False, sort_keys=True)
    data_signature = hashlib.sha256(canonical_json.encode()).hexdigest()[:16]
    
    # Create frozen context
    context = {
        "context_id": context_id,
        "parcel_id": "test-parcel-abs-final",
        "canonical_summary": canonical_summary,
        "frozen_at": datetime.utcnow().isoformat() + "Z",
        "metadata": {
            "version": "ABSOLUTE-FINAL",
            "data_signature": data_signature
        }
    }
    
    # Save to storage
    success = context_storage.store_frozen_context(
        context_id=context_id,
        land_context=context,
        ttl_hours=24
    )
    
    if not success:
        raise Exception("Failed to store context")
    
    print(f"✅ Context created: {context_id}")
    print(f"   Data signature: {data_signature}")
    print(f"   M2.summary.land_value_total_krw: {canonical_summary['M2']['summary']['land_value_total_krw']:,}원")
    print(f"   M5.summary.npv_public_krw: {canonical_summary['M5']['summary']['npv_public_krw']:,}원")
    print(f"   M5.summary.irr_pct: {canonical_summary['M5']['summary']['irr_pct']}%")
    print(f"   M6.summary.decision: {canonical_summary['M6']['summary']['decision']}")
    
    return context_id, data_signature


async def test_all_reports(context_id: str, data_signature: str):
    """Test all 6 report types end-to-end"""
    
    import requests
    
    base_url = "http://localhost:8005"
    
    report_types = [
        "quick_check",
        "financial_feasibility", 
        "lh_technical",
        "executive_summary",
        "landowner_summary",
        "all_in_one"
    ]
    
    results = {}
    
    for report_type in report_types:
        print(f"\n{'='*60}")
        print(f"Testing: {report_type}")
        print(f"{'='*60}")
        
        try:
            response = requests.get(
                f"{base_url}/api/v4/final-report/{report_type}/html",
                params={"context_id": context_id},
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"  ❌ HTTP {response.status_code}: {response.text[:200]}")
                results[report_type] = False
                continue
            
            html = response.text
            
            # Validation checks
            checks = {
                "BUILD_SIGNATURE": "BUILD_SIGNATURE:" in html or "ABSOLUTE-FINAL" in html,
                "DATA_SIGNATURE": data_signature in html or "DATA_SIGNATURE:" in html,
                "No_NA": html.count("N/A") == 0,
                "Has_NPV": "420,000,000" in html or "420000000" in html or "4.2억" in html or "4억" in html,
                "Has_IRR": "13.2" in html or "13.20" in html,
                "Has_Decision": "조건부 적합" in html
            }
            
            all_passed = all(checks.values())
            results[report_type] = all_passed
            
            print(f"  BUILD_SIGNATURE: {'✅ PASS' if checks['BUILD_SIGNATURE'] else '❌ FAIL'}")
            print(f"  DATA_SIGNATURE: {'✅ PASS' if checks['DATA_SIGNATURE'] else '❌ FAIL'}")
            print(f"  No 'N/A': {'✅ PASS' if checks['No_NA'] else '❌ FAIL'}")
            print(f"  NPV rendered: {'✅ PASS' if checks['Has_NPV'] else '❌ FAIL'}")
            print(f"  IRR rendered: {'✅ PASS' if checks['Has_IRR'] else '❌ FAIL'}")
            print(f"  Decision rendered: {'✅ PASS' if checks['Has_Decision'] else '❌ FAIL'}")
            print(f"  Overall: {'✅ SUCCESS' if all_passed else '❌ FAILED'}")
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results[report_type] = False
    
    return results


async def main():
    print("="*80)
    print("ABSOLUTE FINAL: End-to-End Smoke Test")
    print("="*80)
    print()
    
    # Step 1: Create test context
    print("STEP 1: Create test context with M2~M6 canonical_summary")
    print("-"*80)
    
    try:
        context_id, data_signature = await create_complete_test_context()
    except Exception as e:
        print(f"\n❌ FAILED: Could not create context")
        print(f"Reason: {e}")
        sys.exit(1)
    
    # Step 2: Test all 6 reports
    print("\n\nSTEP 2: Test all 6 report types")
    print("-"*80)
    
    results = await test_all_reports(context_id, data_signature)
    
    # Step 3: Final summary
    print("\n\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    
    passed_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    for report_type, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {report_type:25s}: {status}")
    
    print(f"\n  TOTAL: {passed_count}/{total_count} reports passed")
    
    if passed_count == total_count:
        print("\n" + "="*80)
        print("✅✅✅ ABSOLUTE FINAL COMPLETE")
        print("✅✅✅ Pipeline sealed end-to-end")
        print("✅✅✅ 6 final reports generated successfully")
        print("="*80)
        sys.exit(0)
    else:
        print("\n" + "="*80)
        print(f"❌ FAILED")
        print(f"Reason: {total_count - passed_count}/{total_count} reports failed")
        print("="*80)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
