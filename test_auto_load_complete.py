#!/usr/bin/env python3
"""
Test Complete Auto-Load Functionality
개별공시지가 + 프리미엄 요인 자동 로드 테스트
"""

import requests
import json

API_URL = "http://localhost:8000/api/v24.1/appraisal"

# Minimal request - ONLY address, land_area, zone_type
# No individual_land_price, No premium_factors, No comparable_sales
request_data = {
    "address": "서울시 강남구 역삼동 123",
    "land_area_sqm": 660,  # 200평
    "zone_type": "제2종일반주거지역",
    # individual_land_price_per_sqm: NOT PROVIDED - should auto-load
    # premium_factors: NOT PROVIDED - should auto-detect
    # comparable_sales: NOT PROVIDED - should auto-fetch
}

print("=" * 80)
print("🧪 Test: Complete Auto-Load Functionality")
print("=" * 80)
print(f"\n📍 Address: {request_data['address']}")
print(f"📐 Land Area: {request_data['land_area_sqm']} ㎡ ({request_data['land_area_sqm']/3.3:.0f} 평)")
print(f"🏘️  Zone: {request_data['zone_type']}")
print(f"\n❌ Individual Land Price: NOT PROVIDED (should auto-load)")
print(f"❌ Premium Factors: NOT PROVIDED (should auto-detect)")
print(f"❌ Comparable Sales: NOT PROVIDED (should auto-fetch)")
print("\n" + "=" * 80)
print("🚀 Sending request to API...")
print("=" * 80 + "\n")

try:
    response = requests.post(API_URL, json=request_data, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get('status') == 'success':
            appraisal = result.get('appraisal', {})
            
            print("✅ Appraisal Successful!\n")
            print("=" * 80)
            print("📊 APPRAISAL RESULTS")
            print("=" * 80)
            print(f"💵 Final Value: {appraisal.get('final_value', 0):.2f} 억원")
            print(f"📏 Value per ㎡: {appraisal.get('value_per_sqm', 0):,} 원/㎡")
            print(f"📐 Value per pyeong: {appraisal.get('value_per_sqm', 0) * 3.3:,.0f} 원/평")
            print(f"🎯 Confidence: {appraisal.get('confidence', 'N/A')}")
            
            print("\n" + "=" * 80)
            print("⚖️  APPRAISAL METHODS")
            print("=" * 80)
            approaches = appraisal.get('approaches', {})
            print(f"🏗️  Cost Approach: {approaches.get('cost', 0):.2f} 억원")
            print(f"💰 Sales Comparison: {approaches.get('sales_comparison', 0):.2f} 억원")
            print(f"💼 Income Approach: {approaches.get('income', 0):.2f} 억원")
            
            weights = appraisal.get('weights', {})
            print("\n📊 Weights:")
            print(f"   Cost: {weights.get('cost', 0)*100:.0f}%")
            print(f"   Sales: {weights.get('sales', 0)*100:.0f}%")
            print(f"   Income: {weights.get('income', 0)*100:.0f}%")
            
            print("\n" + "=" * 80)
            print("✅ AUTO-LOAD VERIFICATION")
            print("=" * 80)
            
            # Check metadata for auto-loaded values
            metadata = result.get('metadata', {})
            land_price = metadata.get('individual_land_price_per_sqm', 0)
            
            if land_price > 0:
                print(f"✅ Individual Land Price: {land_price:,} 원/㎡ (LOADED)")
            else:
                print(f"❌ Individual Land Price: NOT LOADED")
            
            # Check breakdown for auto-fetched comparables
            breakdown = result.get('breakdown', {})
            sales_breakdown = breakdown.get('sales', {})
            num_comparables = len(sales_breakdown.get('comparable_sales', []))
            
            if num_comparables > 0:
                print(f"✅ Comparable Sales: {num_comparables} cases (FETCHED)")
            else:
                print(f"⚠️  Comparable Sales: Using fallback data")
            
            # Note: Premium info is in engine result but not exposed in API response
            # We need to check the server logs for premium detection
            print(f"\n💡 Check server logs for premium factor auto-detection details")
            
            print("\n" + "=" * 80)
            print("TEST COMPLETE ✅")
            print("=" * 80)
        else:
            print(f"❌ API returned non-success status: {result.get('status')}")
            print(f"Details: {result}")
    else:
        print(f"❌ HTTP Error {response.status_code}")
        print(response.text)

except requests.exceptions.Timeout:
    print("❌ Request timed out after 60 seconds")
    print("💡 This is likely due to MOLIT API being slow")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("Check server logs for detailed auto-load information:")
print("  tail -50 server_new.log")
print("=" * 80)
