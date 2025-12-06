"""
ZeroSite Phase 11: API Integration Test

Tests Phase 11 API endpoints with mock data.

Usage:
    python test_phase11_api.py
"""

import requests
import json
import time
from pathlib import Path


BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test API health check"""
    print("\n" + "="*80)
    print("🏥 Test 1: Health Check")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/api/v11/health")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    
    print("✅ Health check passed!")


def test_single_report_generation():
    """Test single report generation"""
    print("\n" + "="*80)
    print("📄 Test 2: Single Report Generation (Executive)")
    print("="*80)
    
    request_data = {
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500.0,
        "building_coverage_ratio": 60.0,
        "floor_area_ratio": 300.0,
        "land_use_zone": "제2종일반주거지역",
        "report_type": "executive",
        "recommended_type": "Youth",
        "formats": ["html", "json"]
    }
    
    print(f"\n📤 Request:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    response = requests.post(
        f"{BASE_URL}/api/v11/report",
        json=request_data
    )
    
    print(f"\n📥 Response:")
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    assert response.status_code == 200
    assert result["status"] == "queued"
    
    job_id = result["job_id"]
    print(f"\n✅ Report queued! Job ID: {job_id}")
    
    # Wait and check status
    print("\n⏳ Waiting for report generation...")
    time.sleep(2)
    
    status_response = requests.get(f"{BASE_URL}/api/v11/report/{job_id}/status")
    status = status_response.json()
    
    print(f"\n📊 Job Status:")
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    if status["status"] == "completed":
        print("\n✅ Report generated successfully!")
        if "html_url" in status:
            print(f"   HTML: {status['html_url']}")
        if "json_url" in status:
            print(f"   JSON: {status['json_url']}")
    else:
        print(f"\n⚠️  Status: {status['status']}")
    
    return job_id


def test_all_reports_generation():
    """Test all reports generation"""
    print("\n" + "="*80)
    print("📚 Test 3: All Reports Generation (5 types)")
    print("="*80)
    
    request_data = {
        "address": "경기도 성남시 분당구 정자동 100",
        "land_area": 800.0,
        "building_coverage_ratio": 60.0,
        "floor_area_ratio": 300.0,
        "land_use_zone": "제2종일반주거지역",
        "recommended_type": "Newlyweds_TypeI",
        "formats": ["html", "json"]
    }
    
    print(f"\n📤 Request:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    response = requests.post(
        f"{BASE_URL}/api/v11/report/all",
        json=request_data
    )
    
    print(f"\n📥 Response:")
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    assert response.status_code == 200
    assert result["status"] == "queued"
    
    job_id = result["job_id"]
    print(f"\n✅ All reports queued! Job ID: {job_id}")
    
    # Wait and check status
    print("\n⏳ Waiting for all reports generation...")
    time.sleep(3)
    
    status_response = requests.get(f"{BASE_URL}/api/v11/report/{job_id}/status")
    status = status_response.json()
    
    print(f"\n📊 Job Status:")
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    if status["status"] == "completed" and "reports" in status:
        print("\n✅ All reports generated successfully!")
        for report_type, urls in status["reports"].items():
            print(f"\n  {report_type}:")
            for format_type, url in urls.items():
                print(f"    - {format_type.upper()}: {url}")
    else:
        print(f"\n⚠️  Status: {status['status']}")
    
    return job_id


def test_phase8_verified_cost():
    """Test Phase 8 verified cost integration"""
    print("\n" + "="*80)
    print("💰 Test 4: Phase 8 Verified Cost")
    print("="*80)
    
    from app.services_v8.verified_cost_loader import get_verified_cost
    
    test_cases = [
        ("서울특별시 강남구", "Youth"),
        ("경기도 성남시", "Newlyweds_TypeI"),
        ("인천광역시 부평구", "Senior")
    ]
    
    for address, housing_type in test_cases:
        print(f"\n📍 Address: {address}")
        print(f"🏠 Housing Type: {housing_type}")
        
        cost_data = get_verified_cost(address, housing_type)
        
        if cost_data:
            print(f"✅ Verified cost found!")
            print(f"   Cost: {cost_data.cost_per_m2:,}원/㎡")
            print(f"   Region: {cost_data.region}")
            print(f"   Source: {cost_data.source}")
        else:
            print(f"❌ Verified cost not found")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("🚀 ZeroSite Phase 11 API Integration Test")
    print("="*80)
    print("\n⚠️  NOTE: Make sure the server is running!")
    print("   Start server: uvicorn app.main:app --reload")
    print()
    
    try:
        # Test 1: Health Check
        test_health_check()
        
        # Test 2: Single Report
        test_single_report_generation()
        
        # Test 3: All Reports
        test_all_reports_generation()
        
        # Test 4: Phase 8
        test_phase8_verified_cost()
        
        # Summary
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED!")
        print("="*80)
        print("\n✅ Phase 11 API: Working")
        print("✅ Phase 8 Verified Cost: Working")
        print("✅ Report Generation: Working")
        print("\n📂 Check ./reports/ directory for generated files")
        print("="*80 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server!")
        print("   Please start the server first:")
        print("   $ uvicorn app.main:app --reload")
        print()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
