#!/usr/bin/env python3
"""
ZeroSite v3.4 - Land Data API Testing Script
Tests all land data endpoints with real addresses
"""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_health_check():
    """Test 1: API Health Check"""
    print_section("Test 1: Land Data API Health Check")
    
    try:
        response = requests.get(f"{API_BASE}/api/v3/land/health", timeout=10)
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and data.get("status") == "healthy":
            print("\n✅ Health check PASSED")
            return True
        else:
            print("\n❌ Health check FAILED")
            return False
    except Exception as e:
        print(f"❌ Health check ERROR: {e}")
        return False

def test_sample_address():
    """Test 2: Sample Address Test"""
    print_section("Test 2: Sample Address (서울특별시 강남구 역삼동 858)")
    
    try:
        response = requests.post(f"{API_BASE}/api/v3/land/test", timeout=30)
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Summary:")
        print(f"  Success: {data.get('success')}")
        
        if data.get('success') and data.get('land_data'):
            land_data = data['land_data']
            basic = land_data.get('basic_info', {})
            price = land_data.get('price_info', {})
            regulation = land_data.get('regulation_info', {})
            
            print(f"\n  Basic Info:")
            print(f"    Address: {basic.get('address')}")
            print(f"    Area: {basic.get('land_area_sqm')} ㎡ ({basic.get('land_area_pyeong')}평)")
            print(f"    Category: {basic.get('land_category')}")
            
            print(f"\n  Price Info:")
            print(f"    Official Price (㎡): {price.get('official_price_per_sqm'):,}원")
            print(f"    Total Price: {price.get('total_official_price'):,}원")
            print(f"    Year: {price.get('price_year')}")
            
            print(f"\n  Regulation Info:")
            print(f"    Zone: {regulation.get('land_use_zone')}")
            print(f"    FAR: {regulation.get('floor_area_ratio')}%")
            print(f"    BCR: {regulation.get('building_coverage_ratio')}%")
            
            print(f"\n  Transactions: {len(land_data.get('transactions', []))} records")
            print(f"  Buildings: {len(land_data.get('building_info', []))} records")
            
            print("\n✅ Sample address test PASSED")
            return True
        else:
            print(f"\n❌ Sample address test FAILED: {data.get('error')}")
            print(f"Full response:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
            return False
    except Exception as e:
        print(f"❌ Sample address test ERROR: {e}")
        return False

def test_real_address(address):
    """Test 3: Real Address Fetch"""
    print_section(f"Test 3: Real Address Fetch - {address}")
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v3/land/fetch",
            json={"address": address},
            timeout=30
        )
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Summary:")
        print(f"  Success: {data.get('success')}")
        
        if data.get('success') and data.get('land_data'):
            land_data = data['land_data']
            basic = land_data.get('basic_info', {})
            price = land_data.get('price_info', {})
            regulation = land_data.get('regulation_info', {})
            
            print(f"\n  Basic Info:")
            print(f"    Address: {basic.get('address')}")
            print(f"    Area: {basic.get('land_area_sqm')} ㎡ ({basic.get('land_area_pyeong')}평)")
            print(f"    Category: {basic.get('land_category')}")
            print(f"    PNU: {basic.get('pnu_code')}")
            
            print(f"\n  Price Info:")
            print(f"    Official Price (㎡): {price.get('official_price_per_sqm'):,}원")
            print(f"    Total Price: {price.get('total_official_price'):,}원")
            print(f"    Year: {price.get('price_year')}")
            
            print(f"\n  Regulation Info:")
            print(f"    Zone: {regulation.get('land_use_zone')}")
            print(f"    FAR: {regulation.get('floor_area_ratio')}%")
            print(f"    BCR: {regulation.get('building_coverage_ratio')}%")
            print(f"    Max Height: {regulation.get('max_building_height')}m")
            
            transactions = land_data.get('transactions', [])
            print(f"\n  Transactions: {len(transactions)} records")
            if transactions:
                for i, txn in enumerate(transactions[:3], 1):
                    print(f"    {i}. {txn.get('transaction_date')}: {txn.get('transaction_amount'):,}원 ({txn.get('land_area_sqm')}㎡)")
            
            buildings = land_data.get('building_info', [])
            print(f"\n  Buildings: {len(buildings)} records")
            if buildings:
                for i, bldg in enumerate(buildings[:3], 1):
                    print(f"    {i}. {bldg.get('building_name')}: {bldg.get('total_floor_area')}㎡")
            
            # Check appraisal context
            if data.get('appraisal_context'):
                print(f"\n  ✅ Appraisal Context: Generated")
                appraisal = data['appraisal_context']
                calc = appraisal.get('calculation', {})
                print(f"    Final Appraised Total: {calc.get('final_appraised_total'):,}원")
                print(f"    Final Appraised (㎡): {calc.get('final_appraised_per_sqm'):,}원")
            
            print("\n✅ Real address test PASSED")
            return True
        else:
            print(f"\n❌ Real address test FAILED: {data.get('error')}")
            print(f"Full response:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
            return False
    except Exception as e:
        print(f"❌ Real address test ERROR: {e}")
        return False

def test_report_generation(address):
    """Test 4: Report Generation with Real Data"""
    print_section(f"Test 4: Report Generation - {address}")
    
    try:
        # First fetch land data
        print("Step 1: Fetching land data...")
        response = requests.post(
            f"{API_BASE}/api/v3/land/fetch",
            json={"address": address},
            timeout=30
        )
        data = response.json()
        
        if not data.get('success'):
            print(f"❌ Failed to fetch land data: {data.get('error')}")
            return False
        
        appraisal_context = data.get('appraisal_context')
        if not appraisal_context:
            print("❌ No appraisal context in response")
            return False
        
        print("✅ Land data fetched successfully")
        
        # Generate pre-report
        print("\nStep 2: Generating pre-report...")
        response = requests.post(
            f"{API_BASE}/api/v3/reports/pre-report",
            json={"appraisal_context": appraisal_context},
            timeout=30
        )
        result = response.json()
        
        print(f"Status Code: {response.status_code}")
        
        if result.get('report_id'):
            print(f"✅ Report generated successfully!")
            print(f"  Report ID: {result['report_id']}")
            print(f"  Type: {result.get('report_type')}")
            print(f"  Generation Time: {result.get('generation_time_ms')}ms")
            
            # Test PDF download link
            pdf_url = f"{API_BASE}/api/v3/reports/{result['report_id']}/pdf"
            print(f"\n  PDF URL: {pdf_url}")
            
            return True
        else:
            print(f"❌ Report generation failed: {result.get('error')}")
            print(f"Full response:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
            return False
    except Exception as e:
        print(f"❌ Report generation ERROR: {e}")
        return False

def main():
    """Main test runner"""
    print(f"\n{'#'*80}")
    print(f"  ZeroSite v3.4 - Land Data API Test Suite")
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*80}")
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_health_check()))
    
    # Test 2: Sample Address
    results.append(("Sample Address", test_sample_address()))
    
    # Test 3: Real Addresses
    test_addresses = [
        "서울특별시 강남구 역삼동 858",
        "서울특별시 강남구 테헤란로 123",
        "서울특별시 서초구 서초동 1234"
    ]
    
    for address in test_addresses:
        results.append((f"Real Address: {address}", test_real_address(address)))
    
    # Test 4: Report Generation
    results.append(("Report Generation", test_report_generation(test_addresses[0])))
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    print(f"\n{'='*80}")
    print(f"  Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*80}\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
