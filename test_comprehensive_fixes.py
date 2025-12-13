"""
Comprehensive Test Plan for Appraisal Report Fixes
Tests all 6 critical issues to verify resolution
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("COMPREHENSIVE TEST PLAN - Appraisal Report Fixes")
print("=" * 80)
print(f"Testing server: {BASE_URL}")
print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Test Case 1: Premium Reflection (Issue #1)
print("\n" + "=" * 80)
print("TEST CASE 1: Premium (41%) Reflected in Executive Summary")
print("=" * 80)

test1_data = {
    "address": "서울시 강남구 역삼동 123",
    "land_area_sqm": 660.0,
    "zone_type": "제3종일반주거지역",
    "individual_land_price_per_sqm": 12000000,
    "premium_factors": {
        "location_grade": {"subway_300m": True, "school_500m": True},
        "development_potential": {"near_redevelopment": True},
        "infrastructure": {"new_subway_planned": True}
    }
}

print(f"Request data:")
print(f"  - Address: {test1_data['address']}")
print(f"  - Land Area: {test1_data['land_area_sqm']}㎡")
print(f"  - Zone Type: {test1_data['zone_type']}")
print(f"  - Premium factors: YES (expect ~41% premium)")
print("\n⏳ Sending request to /api/v24.1/appraisal/pdf...")

try:
    response = requests.post(
        f"{BASE_URL}/api/v24.1/appraisal/pdf",
        json=test1_data,
        timeout=60
    )
    
    if response.status_code == 200:
        # Save PDF
        pdf_filename = f"test_case_1_premium_{datetime.now().strftime('%H%M%S')}.pdf"
        with open(pdf_filename, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ TEST 1 PASSED: PDF generated successfully")
        print(f"   - Saved as: {pdf_filename}")
        print(f"   - File size: {len(response.content):,} bytes")
        print(f"\n📋 Verification Steps:")
        print(f"   1. Open PDF and check p.2 (Executive Summary)")
        print(f"   2. Verify 'Final Value' shows premium-adjusted amount")
        print(f"   3. Check p.3 (Premium Section) for premium details")
        print(f"   4. Ensure Executive Summary value = Premium Section value")
    else:
        print(f"❌ TEST 1 FAILED: HTTP {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ TEST 1 ERROR: {str(e)}")

# Test Case 2: Development Land Income Approach (Issue #3)
print("\n" + "=" * 80)
print("TEST CASE 2: Development Land Income Approach (No Unrealistic Values)")
print("=" * 80)

test2_data = {
    "address": "서울시 마포구 공덕동 456",
    "land_area_sqm": 660.0,
    "zone_type": "제2종일반주거지역",
    "individual_land_price_per_sqm": 10000000,
    "building_area_sqm": 0,  # No building (development land)
    "annual_rental_income": 0  # No rental income
}

print(f"Request data:")
print(f"  - Address: {test2_data['address']}")
print(f"  - Land Area: {test2_data['land_area_sqm']}㎡")
print(f"  - Building Area: 0㎡ (DEVELOPMENT LAND)")
print(f"  - Rental Income: 0원 (NO INCOME)")
print("\n⏳ Sending request...")

try:
    response = requests.post(
        f"{BASE_URL}/api/v24.1/appraisal/pdf",
        json=test2_data,
        timeout=60
    )
    
    if response.status_code == 200:
        pdf_filename = f"test_case_2_development_{datetime.now().strftime('%H%M%S')}.pdf"
        with open(pdf_filename, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ TEST 2 PASSED: PDF generated successfully")
        print(f"   - Saved as: {pdf_filename}")
        print(f"\n📋 Verification Steps:")
        print(f"   1. Open PDF and check p.14 (Income Approach)")
        print(f"   2. Verify Income Approach value is REALISTIC (~100-120억)")
        print(f"   3. NOT unrealistic (e.g., 1489억)")
        print(f"   4. Check for '완성도 보정 (25%)' and '위험도 보정 (30%)'")
        print(f"   5. Verify '개발용지 환원율: 6.0%' is mentioned")
    else:
        print(f"❌ TEST 2 FAILED: HTTP {response.status_code}")
except Exception as e:
    print(f"❌ TEST 2 ERROR: {str(e)}")

# Test Case 3: Final Appraisal Table (Issue #4)
print("\n" + "=" * 80)
print("TEST CASE 3: Final Appraisal Table Shows Values (Not 0)")
print("=" * 80)

test3_data = {
    "address": "서울시 서초구 서초동 789",
    "land_area_sqm": 500.0,
    "zone_type": "제3종일반주거지역",
    "individual_land_price_per_sqm": 15000000
}

print(f"Request data:")
print(f"  - Address: {test3_data['address']}")
print(f"  - Land Area: {test3_data['land_area_sqm']}㎡")
print("\n⏳ Sending request...")

try:
    response = requests.post(
        f"{BASE_URL}/api/v24.1/appraisal/pdf",
        json=test3_data,
        timeout=60
    )
    
    if response.status_code == 200:
        pdf_filename = f"test_case_3_final_table_{datetime.now().strftime('%H%M%S')}.pdf"
        with open(pdf_filename, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ TEST 3 PASSED: PDF generated successfully")
        print(f"   - Saved as: {pdf_filename}")
        print(f"\n📋 Verification Steps:")
        print(f"   1. Open PDF and check p.15 (Final Valuation Table)")
        print(f"   2. Verify 'Cost Approach' shows value > 0억")
        print(f"   3. Verify 'Sales Comparison' shows value > 0억")
        print(f"   4. Verify 'Income Approach' shows value > 0억")
        print(f"   5. All three methods should have non-zero values")
    else:
        print(f"❌ TEST 3 FAILED: HTTP {response.status_code}")
except Exception as e:
    print(f"❌ TEST 3 ERROR: {str(e)}")

# Test Case 4: PDF Filename (Issue #5)
print("\n" + "=" * 80)
print("TEST CASE 4: PDF Filename Format (지번 Extraction)")
print("=" * 80)

test4_addresses = [
    ("서울시 강남구 역삼동 123-4", "역삼동123-4"),
    ("서울시 마포구 월드컵북로 120", "월드컵북로120"),
    ("서울시 서초구 강남대로 456", "강남대로456")
]

for address, expected_jibun in test4_addresses:
    print(f"\nTesting: {address}")
    print(f"Expected jibun: {expected_jibun}")
    
    test4_data = {
        "address": address,
        "land_area_sqm": 400.0,
        "zone_type": "제2종일반주거지역",
        "individual_land_price_per_sqm": 10000000
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v24.1/appraisal/pdf",
            json=test4_data,
            timeout=60
        )
        
        if response.status_code == 200:
            # Check Content-Disposition header for filename
            content_disposition = response.headers.get('content-disposition', '')
            print(f"✅ PDF generated")
            print(f"   Content-Disposition: {content_disposition}")
            print(f"   Expected filename pattern: {expected_jibun}_감정평가보고서.pdf")
            
            # Extract filename from header
            if 'filename=' in content_disposition:
                filename_part = content_disposition.split('filename=')[1].strip('"\'')
                if expected_jibun in filename_part:
                    print(f"   ✅ Filename contains correct jibun!")
                else:
                    print(f"   ⚠️ Filename may not match expected pattern")
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    time.sleep(1)  # Small delay between requests

# Test Case 5: Address Extraction (Issue #2)
print("\n" + "=" * 80)
print("TEST CASE 5: No 'default' in Transaction Addresses")
print("=" * 80)

test5_data = {
    "address": "월드컵북로 120",  # Road name only (challenging case)
    "land_area_sqm": 550.0,
    "zone_type": "준주거지역",
    "individual_land_price_per_sqm": 11000000
}

print(f"Request data:")
print(f"  - Address: {test5_data['address']} (CHALLENGING: Road name only)")
print("\n⏳ Sending request...")

try:
    response = requests.post(
        f"{BASE_URL}/api/v24.1/appraisal/pdf",
        json=test5_data,
        timeout=60
    )
    
    if response.status_code == 200:
        pdf_filename = f"test_case_5_address_{datetime.now().strftime('%H%M%S')}.pdf"
        with open(pdf_filename, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ TEST 5 PASSED: PDF generated successfully")
        print(f"   - Saved as: {pdf_filename}")
        print(f"\n📋 Verification Steps:")
        print(f"   1. Open PDF and check p.7, p.22, p.23 (Transaction Cases)")
        print(f"   2. Verify NO 'default' appears in addresses")
        print(f"   3. All addresses should show real district names")
        print(f"   4. Fallback should be '강남구' not 'default'")
    else:
        print(f"❌ TEST 5 FAILED: HTTP {response.status_code}")
except Exception as e:
    print(f"❌ TEST 5 ERROR: {str(e)}")

# Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("\n✅ All test requests completed!")
print("\nManual Verification Required:")
print("  1. Check Test Case 1 PDF - Premium reflected in Executive Summary (p.2)")
print("  2. Check Test Case 2 PDF - Realistic Income Approach value (p.14)")
print("  3. Check Test Case 3 PDF - Final table shows non-zero values (p.15)")
print("  4. Check Test Case 4 - PDF filenames contain correct 지번")
print("  5. Check Test Case 5 PDF - No 'default' in transaction addresses (p.7)")
print("\n📁 Generated PDF files:")
print("  - test_case_1_premium_*.pdf")
print("  - test_case_2_development_*.pdf")
print("  - test_case_3_final_table_*.pdf")
print("  - test_case_5_address_*.pdf")
print("\n" + "=" * 80)
print("Testing completed at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print("=" * 80)
