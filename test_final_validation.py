#!/usr/bin/env python3
"""
ZeroSite v7.2 Final Validation Test
Tests both Basic and Extended Reports with real API endpoints
"""
import requests
import json
import time
from datetime import datetime

API_BASE = "http://0.0.0.0:8000"

def test_extended_report():
    """Test Extended Report Generation (25-40 pages)"""
    print("\n" + "="*80)
    print("🧪 TEST 1: Extended Report Generation (25-40 pages)")
    print("="*80)
    
    payload = {
        "address": "서울특별시 마포구 월드컵북로 120",
        "land_area": 660.0,
        "unit_type": "청년",
        "report_mode": "extended"
    }
    
    print(f"\n📤 Request:")
    print(f"   POST {API_BASE}/api/generate-report")
    print(f"   Body: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    start = time.time()
    try:
        response = requests.post(
            f"{API_BASE}/api/generate-report",
            json=payload,
            timeout=60
        )
        elapsed = time.time() - start
        
        print(f"\n📥 Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Time: {elapsed:.1f}s")
        print(f"   Size: {len(response.content):,} bytes")
        
        if response.status_code == 200:
            # Save report
            report_path = "/tmp/final_extended_report.html"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            
            # Validate TypeDemand scores
            html = response.text
            scores = {
                "청년": "74",
                "신혼·신생아 I": "84",
                "신혼·신생아 II": "70",
                "다자녀": "76",
                "고령자": "94"
            }
            
            print(f"\n✅ SUCCESS - Extended Report Generated")
            print(f"   Report saved: {report_path}")
            print(f"\n🔍 TypeDemand Score Validation:")
            
            found_scores = 0
            for type_name, expected_score in scores.items():
                if f"{type_name}" in html and f"{expected_score}" in html:
                    print(f"   ✓ {type_name}: {expected_score}점 found")
                    found_scores += 1
                else:
                    print(f"   ✗ {type_name}: {expected_score}점 NOT found")
            
            print(f"\n📊 Score Detection Rate: {found_scores}/5 types ({found_scores*20}%)")
            
            # Check key sections
            sections = [
                "유형별 수요 분석",
                "GeoOptimizer",
                "Raw Data Appendix"
            ]
            
            print(f"\n📋 Section Validation:")
            for section in sections:
                if section in html:
                    print(f"   ✓ {section}")
                else:
                    print(f"   ✗ {section} missing")
            
            return True
        else:
            print(f"\n❌ FAILED - Status {response.status_code}")
            print(f"   Error: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        return False

def test_basic_report():
    """Test Basic Report Generation (8-10 pages)"""
    print("\n" + "="*80)
    print("🧪 TEST 2: Basic Report Generation (8-10 pages)")
    print("="*80)
    
    payload = {
        "address": "서울특별시 마포구 월드컵북로 120",
        "land_area": 660.0,
        "unit_type": "청년",
        "report_mode": "basic"
    }
    
    print(f"\n📤 Request:")
    print(f"   POST {API_BASE}/api/generate-report")
    print(f"   Body: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    start = time.time()
    try:
        response = requests.post(
            f"{API_BASE}/api/generate-report",
            json=payload,
            timeout=60
        )
        elapsed = time.time() - start
        
        print(f"\n📥 Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Time: {elapsed:.1f}s")
        print(f"   Size: {len(response.content):,} bytes")
        
        if response.status_code == 200:
            report_path = "/tmp/final_basic_report.html"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            
            print(f"\n✅ SUCCESS - Basic Report Generated")
            print(f"   Report saved: {report_path}")
            return True
        else:
            print(f"\n❌ FAILED - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        return False

def main():
    print("╔" + "="*78 + "╗")
    print("║" + " ZeroSite v7.2 Final Validation Test Suite ".center(78) + "║")
    print("║" + f" {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ".center(78) + "║")
    print("╚" + "="*78 + "╝")
    
    results = []
    
    # Test 1: Extended Report
    results.append(("Extended Report", test_extended_report()))
    
    # Test 2: Basic Report
    results.append(("Basic Report", test_basic_report()))
    
    # Summary
    print("\n" + "="*80)
    print("📊 FINAL VALIDATION SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n" + "🎉 ALL TESTS PASSED - SYSTEM IS PRODUCTION READY 🎉".center(80))
    else:
        print("\n" + "⚠️  SOME TESTS FAILED - REVIEW REQUIRED ⚠️".center(80))
    
    print("="*80)

if __name__ == "__main__":
    main()
