#!/usr/bin/env python3
"""
Test full pipeline with report generation
===========================================

This test demonstrates the complete workflow:
1. Run M1-M6 pipeline analysis
2. Generate canonical_summary
3. Generate all 6 report types

DATE: 2025-12-24
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8005"

def test_complete_workflow():
    """Test complete workflow from pipeline to reports"""
    
    print("\n" + "="*80)
    print("FULL PIPELINE + REPORTS TEST")
    print("="*80)
    
    # Step 1: Run M1-M6 pipeline analysis
    print("\n📋 STEP 1: Run M1-M6 Pipeline Analysis")
    print("-" * 80)
    
    parcel_id = "test-full-workflow-20251224"
    
    # Mock land data for testing
    mock_land_data = {
        "address": "서울시 강남구 역삼동 123-45",
        "coordinates": {"lat": 37.5665, "lng": 127.0471},
        "land_area_sqm": 500,
        "official_land_price_krw": 10000000,
        "zone_type": "제2종일반주거지역",
        "far_legal": 200,
        "bcr_legal": 60,
        "road_contact_m": 15,
        "road_width_m": 8
    }
    
    payload = {
        "parcel_id": parcel_id,
        "mock_land_data": mock_land_data
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v4/pipeline/analyze",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Pipeline analysis completed")
            print(f"   Context ID: {result.get('context_id')}")
            print(f"   Parcel ID: {result.get('parcel_id')}")
            print(f"   Canonical Summary: {'✅ Generated' if result.get('canonical_summary') else '❌ Missing'}")
            
            context_id = result.get('context_id')
            
            # Step 2: Generate all 6 report types
            print("\n📋 STEP 2: Generate All 6 Report Types")
            print("-" * 80)
            
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
                print(f"\n📄 Testing {report_type}...")
                
                try:
                    report_response = requests.get(
                        f"{BASE_URL}/api/v4/final-report/{report_type}/html",
                        params={"context_id": context_id},
                        timeout=30
                    )
                    
                    if report_response.status_code == 200:
                        html = report_response.text
                        
                        # Check for key indicators
                        has_build_sig = "BUILD_SIGNATURE" in html
                        has_data_sig = "DATA_SIGNATURE" in html
                        has_npv = "NPV" in html or "420,000,000" in html
                        na_count = html.count("N/A")
                        
                        results[report_type] = {
                            "status": "✅ SUCCESS",
                            "html_size": len(html),
                            "has_build_sig": has_build_sig,
                            "has_data_sig": has_data_sig,
                            "has_npv": has_npv,
                            "na_count": na_count
                        }
                        
                        print(f"  ✅ Generated ({len(html):,} bytes)")
                        print(f"     BUILD_SIGNATURE: {'✅' if has_build_sig else '❌'}")
                        print(f"     DATA_SIGNATURE: {'✅' if has_data_sig else '❌'}")
                        print(f"     NPV rendered: {'✅' if has_npv else '❌'}")
                        print(f"     N/A count: {na_count}")
                    else:
                        results[report_type] = {
                            "status": f"❌ FAILED ({report_response.status_code})",
                            "error": report_response.text[:200]
                        }
                        print(f"  ❌ Failed: {report_response.status_code}")
                        
                except Exception as e:
                    results[report_type] = {
                        "status": "❌ ERROR",
                        "error": str(e)
                    }
                    print(f"  ❌ Error: {e}")
            
            # Summary
            print("\n" + "="*80)
            print("FINAL RESULTS")
            print("="*80)
            
            success_count = sum(1 for r in results.values() if r.get("status") == "✅ SUCCESS")
            print(f"\n✅ {success_count}/6 reports generated successfully")
            
            if success_count == 6:
                print("\n🎉 100% COMPLETE - ALL 6 REPORTS GENERATED SUCCESSFULLY!")
                print(f"\n📋 Context ID: {context_id}")
                print(f"📋 Parcel ID: {parcel_id}")
                print(f"\n🔗 Test URLs:")
                for report_type in report_types:
                    print(f"   {BASE_URL}/api/v4/final-report/{report_type}/html?context_id={context_id}")
                return True
            else:
                print("\n⚠️ Some reports failed to generate")
                return False
                
        else:
            print(f"❌ Pipeline analysis failed: {response.status_code}")
            print(f"   Error: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_complete_workflow()
    exit(0 if success else 1)
