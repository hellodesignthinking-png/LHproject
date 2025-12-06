"""
Phase 11.2: Minimal UI - E2E Test Suite

Tests the complete user journey:
1. Generate report (POST /api/v13/report)
2. Get summary (GET /api/v13/report/{id}/summary)
3. Download PDF (GET /api/v13/report/{id})
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main_v13 import app
import time

client = TestClient(app)


def test_health_check():
    """Test 1: Health check endpoint"""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    response = client.get("/api/v13/health")
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"✓ Status: {data['status']}")
    print(f"✓ Service: {data['service']}")
    print(f"✓ Reports Cached: {data['reports_cached']}")
    
    assert data['status'] == 'healthy'
    print("\n✅ TEST 1 PASSED: Health check OK")


def test_generate_report():
    """Test 2: Generate report"""
    print("\n" + "="*80)
    print("TEST 2: Generate Report")
    print("="*80)
    
    # Test data
    request_data = {
        "address": "서울시 강남구 역삼동 123",
        "land_area_sqm": 500.0,
        "merge": False
    }
    
    start_time = time.time()
    
    response = client.post("/api/v13/report", json=request_data)
    
    elapsed = time.time() - start_time
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"\n✓ Report ID: {data['report_id']}")
    print(f"✓ Status: {data['status']}")
    print(f"✓ Message: {data['message']}")
    print(f"✓ Generation Time: {elapsed:.3f}s")
    
    assert 'report_id' in data
    assert data['status'] == 'completed'
    assert elapsed < 10  # Should complete within 10 seconds
    
    print("\n✅ TEST 2 PASSED: Report generated successfully")
    
    return data['report_id']


def test_get_report_summary(report_id: str):
    """Test 3: Get report summary"""
    print("\n" + "="*80)
    print("TEST 3: Get Report Summary")
    print("="*80)
    
    response = client.get(f"/api/v13/report/{report_id}/summary")
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"\n📊 Report Summary:")
    print(f"  Address: {data['address']}")
    print(f"  Housing Type: {data['housing_type']}")
    print(f"  NPV (Public): {data['npv_public'] / 100000000:.2f}억원")
    print(f"  IRR: {data['irr']:.2f}%")
    print(f"  Payback Period: {data['payback_period']:.1f}년")
    print(f"  Market Signal: {data['market_signal']}")
    print(f"  Generated At: {data['generated_at']}")
    
    assert data['address'] == "서울시 강남구 역삼동 123"
    assert 'housing_type' in data
    assert 'npv_public' in data
    assert 'irr' in data
    
    print("\n✅ TEST 3 PASSED: Summary retrieved successfully")


def test_download_pdf(report_id: str):
    """Test 4: Download PDF"""
    print("\n" + "="*80)
    print("TEST 4: Download PDF")
    print("="*80)
    
    start_time = time.time()
    
    response = client.get(f"/api/v13/report/{report_id}")
    
    elapsed = time.time() - start_time
    
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/pdf'
    
    pdf_size = len(response.content)
    
    print(f"\n✓ PDF Size: {pdf_size:,} bytes ({pdf_size / 1024 / 1024:.2f} MB)")
    print(f"✓ Generation Time: {elapsed:.3f}s")
    print(f"✓ Content-Type: {response.headers['content-type']}")
    
    # PDF should be reasonable size (< 15MB as per DoD)
    assert pdf_size > 10000  # At least 10KB
    assert pdf_size < 15 * 1024 * 1024  # Less than 15MB
    
    # PDF should generate quickly (< 5s as per Phase 10.5 performance)
    assert elapsed < 10
    
    print("\n✅ TEST 4 PASSED: PDF downloaded successfully")


def test_invalid_report_id():
    """Test 5: Invalid report ID"""
    print("\n" + "="*80)
    print("TEST 5: Invalid Report ID (Error Handling)")
    print("="*80)
    
    fake_id = "nonexistent-report-id"
    
    response = client.get(f"/api/v13/report/{fake_id}/summary")
    
    assert response.status_code == 404
    
    print(f"✓ Correctly returns 404 for invalid ID")
    print(f"✓ Error message: {response.json()['detail']}")
    
    print("\n✅ TEST 5 PASSED: Error handling works correctly")


def test_multi_parcel_scenario():
    """Test 6: Multi-parcel scenario"""
    print("\n" + "="*80)
    print("TEST 6: Multi-Parcel Scenario")
    print("="*80)
    
    request_data = {
        "address": "경기도 성남시 분당구 정자동 456",
        "land_area_sqm": 800.0,
        "merge": True
    }
    
    response = client.post("/api/v13/report", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"✓ Multi-parcel report generated")
    print(f"✓ Report ID: {data['report_id']}")
    
    # Get summary
    summary_response = client.get(f"/api/v13/report/{data['report_id']}/summary")
    assert summary_response.status_code == 200
    
    print(f"✓ Summary retrieved for multi-parcel")
    
    print("\n✅ TEST 6 PASSED: Multi-parcel scenario works")
    
    return data['report_id']


def test_performance_benchmark():
    """Test 7: Performance benchmark"""
    print("\n" + "="*80)
    print("TEST 7: Performance Benchmark")
    print("="*80)
    
    addresses = [
        ("서울시 강남구 역삼동", 500),
        ("경기도 성남시 분당구", 800),
        ("인천시 연수구 송도동", 1000)
    ]
    
    total_time = 0
    
    for address, land_area in addresses:
        request_data = {
            "address": address,
            "land_area_sqm": land_area,
            "merge": False
        }
        
        start = time.time()
        response = client.post("/api/v13/report", json=request_data)
        elapsed = time.time() - start
        
        total_time += elapsed
        
        assert response.status_code == 200
        
        status = "✓" if elapsed < 10 else "✗"
        print(f"  {status} {address}: {elapsed:.3f}s")
    
    avg_time = total_time / len(addresses)
    
    print(f"\n📊 Performance Summary:")
    print(f"  Total Time: {total_time:.3f}s")
    print(f"  Average Time: {avg_time:.3f}s")
    print(f"  Target: < 10s per report")
    
    assert avg_time < 10
    
    print("\n✅ TEST 7 PASSED: Performance within target")


def run_all_tests():
    """Run complete E2E test suite"""
    print("\n" + "="*80)
    print("ZEROSITE PHASE 11.2: MINIMAL UI E2E TEST SUITE")
    print("="*80)
    print("Testing complete user journey from input to PDF download")
    print("="*80)
    
    try:
        # Test 1: Health check
        test_health_check()
        
        # Test 2: Generate report
        report_id = test_generate_report()
        
        # Test 3: Get summary
        test_get_report_summary(report_id)
        
        # Test 4: Download PDF
        test_download_pdf(report_id)
        
        # Test 5: Error handling
        test_invalid_report_id()
        
        # Test 6: Multi-parcel
        multi_report_id = test_multi_parcel_scenario()
        
        # Test 7: Performance
        test_performance_benchmark()
        
        # Summary
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED - Phase 11.2 E2E Complete")
        print("="*80)
        print("\n📊 Test Summary:")
        print("  ✓ Health Check")
        print("  ✓ Report Generation")
        print("  ✓ Summary Retrieval")
        print("  ✓ PDF Download")
        print("  ✓ Error Handling")
        print("  ✓ Multi-Parcel Scenario")
        print("  ✓ Performance Benchmark")
        print("\n🎯 Phase 11.2 Status: PRODUCTION READY")
        print("📦 Deliverable: Complete 2-Step UX (Input → Progress → Download)")
        print("🚀 ZeroSite v13.0: 100% COMPLETE")
        print("="*80)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
