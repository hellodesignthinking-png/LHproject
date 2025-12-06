"""
Quick API Integration Test Script
Test the production API v13 endpoint to ensure it returns real values
"""

import requests
import json
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change to your production URL
TEST_CASES = [
    {
        "name": "Seoul Gangnam Test",
        "address": "서울특별시 강남구 역삼동 123",
        "land_area_sqm": 500.0
    },
    {
        "name": "Seoul Mapo Test",
        "address": "서울특별시 마포구 월드컵북로 120",
        "land_area_sqm": 660.0
    },
    {
        "name": "Small Land Test",
        "address": "서울특별시 송파구 잠실동 456",
        "land_area_sqm": 300.0
    }
]

def test_health_endpoint():
    """Test API health check"""
    print("\n" + "="*80)
    print("🏥 Testing Health Endpoint")
    print("="*80)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v13/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data.get('status', 'unknown')}")
            print(f"📊 Service: {data.get('service', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_report_generation(test_case):
    """Test report generation with a specific case"""
    print("\n" + "="*80)
    print(f"🧪 Testing: {test_case['name']}")
    print("="*80)
    print(f"📍 Address: {test_case['address']}")
    print(f"📐 Land Area: {test_case['land_area_sqm']}㎡")
    
    # Step 1: Generate report
    print("\n⏳ Step 1: Generating report...")
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/api/v13/report",
            json={
                "address": test_case['address'],
                "land_area_sqm": test_case['land_area_sqm'],
                "merge": False
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Report generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        data = response.json()
        report_id = data.get('report_id')
        generation_time = time.time() - start_time
        
        print(f"✅ Report generated!")
        print(f"   Report ID: {report_id}")
        print(f"   Time: {generation_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return False
    
    # Step 2: Get report summary
    print("\n⏳ Step 2: Fetching report summary...")
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v13/report/{report_id}/summary",
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get summary: {response.status_code}")
            return False
        
        summary = response.json()
        
        print(f"✅ Summary retrieved!")
        print(f"\n📊 Financial Metrics:")
        
        # Extract and validate values
        npv_krw = summary.get('npv_krw', 0)
        irr_pct = summary.get('irr_pct', 0)
        market_signal = summary.get('market_signal', 'UNKNOWN')
        
        # Convert to 억원
        npv_100m = npv_krw / 100_000_000 if npv_krw else 0
        
        print(f"   NPV: {npv_100m:.2f}억원")
        print(f"   IRR: {irr_pct:.2f}%")
        print(f"   Market Signal: {market_signal}")
        
        # Validation
        validation_passed = True
        
        if npv_krw == 0:
            print(f"\n⚠️  WARNING: NPV is 0 - might indicate issue")
            validation_passed = False
        else:
            print(f"\n✅ NPV is non-zero: PASS")
        
        if market_signal in ['UNKNOWN', 'missing', None]:
            print(f"⚠️  WARNING: Market signal missing")
            validation_passed = False
        else:
            print(f"✅ Market signal present: PASS")
        
        return validation_passed
        
    except Exception as e:
        print(f"❌ Error getting summary: {e}")
        return False

def test_report_download(test_case):
    """Test downloading the generated PDF"""
    print("\n⏳ Step 3: Testing PDF download...")
    
    try:
        # Generate report first
        response = requests.post(
            f"{API_BASE_URL}/api/v13/report",
            json={
                "address": test_case['address'],
                "land_area_sqm": test_case['land_area_sqm']
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Could not generate report for download test")
            return False
        
        report_id = response.json().get('report_id')
        
        # Try to download
        download_response = requests.get(
            f"{API_BASE_URL}/api/v13/report/{report_id}",
            timeout=30
        )
        
        if download_response.status_code == 200:
            content_type = download_response.headers.get('Content-Type', '')
            if 'pdf' in content_type.lower():
                pdf_size = len(download_response.content) / 1024  # KB
                print(f"✅ PDF download successful!")
                print(f"   Size: {pdf_size:.1f} KB")
                print(f"   Content-Type: {content_type}")
                return True
            else:
                print(f"⚠️  Downloaded file is not PDF: {content_type}")
                return False
        else:
            print(f"❌ Download failed: {download_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing download: {e}")
        return False

def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*80)
    print("🚀 Production API v13 - Integration Test Suite")
    print("="*80)
    print(f"Base URL: {API_BASE_URL}")
    print(f"Test Cases: {len(TEST_CASES)}")
    
    results = {
        'health': False,
        'generation': [],
        'download': False
    }
    
    # Test 1: Health check
    results['health'] = test_health_endpoint()
    
    if not results['health']:
        print("\n❌ Health check failed - server may not be running")
        print(f"   Try: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return results
    
    # Test 2: Report generation for each case
    print("\n" + "="*80)
    print("📊 Testing Report Generation")
    print("="*80)
    
    for test_case in TEST_CASES:
        passed = test_report_generation(test_case)
        results['generation'].append({
            'name': test_case['name'],
            'passed': passed
        })
        time.sleep(1)  # Small delay between tests
    
    # Test 3: PDF download
    print("\n" + "="*80)
    print("📄 Testing PDF Download")
    print("="*80)
    results['download'] = test_report_download(TEST_CASES[0])
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    print(f"\n✅ Health Check: {'PASS' if results['health'] else 'FAIL'}")
    
    print(f"\n📊 Report Generation:")
    passed_count = sum(1 for r in results['generation'] if r['passed'])
    for result in results['generation']:
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"   {status} - {result['name']}")
    print(f"   Total: {passed_count}/{len(TEST_CASES)} passed")
    
    print(f"\n📄 PDF Download: {'✅ PASS' if results['download'] else '❌ FAIL'}")
    
    # Overall result
    all_passed = (
        results['health'] and
        all(r['passed'] for r in results['generation']) and
        results['download']
    )
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL TESTS PASSED - Production Ready!")
    else:
        print("⚠️  SOME TESTS FAILED - Review above for details")
    print("="*80)
    
    return results

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║              Production API v13 - Integration Test Suite                  ║
║                                                                            ║
║  This script tests the upgraded API to ensure it returns REAL values      ║
║  instead of 0.00억원 for all financial metrics.                           ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Run tests
    results = run_all_tests()
    
    # Exit code
    all_passed = all(r['passed'] for r in results['generation'])
    exit(0 if all_passed else 1)
