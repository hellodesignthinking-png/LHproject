#!/usr/bin/env python3
"""
Test Premium Auto-Detection in API
테스트: 강남역 인근 토지에 대한 감정평가 (프리미엄 자동 감지)
"""

import requests
import json

API_URL = "http://localhost:8000/api/v24.1/appraisal"

# Test data: 강남역 인근 토지
request_data = {
    "address": "서울시 강남구 역삼동 123",
    "land_area_sqm": 660,  # 200평
    "zone_type": "제2종일반주거지역",
    "individual_land_price_per_sqm": 8000000,
    # NO premium_factors provided - should auto-detect
}

print("=" * 70)
print("🧪 Test: Premium Auto-Detection in API")
print("=" * 70)
print(f"\n📍 Address: {request_data['address']}")
print(f"📐 Land Area: {request_data['land_area_sqm']} ㎡ ({request_data['land_area_sqm']/3.3:.0f} 평)")
print(f"🏘️  Zone: {request_data['zone_type']}")
print(f"💰 Individual Price: {request_data['individual_land_price_per_sqm']:,} 원/㎡")
print(f"\n🔍 Premium Factors: NOT PROVIDED (should auto-detect)\n")

try:
    response = requests.post(API_URL, json=request_data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get('status') == 'success':
            appraisal = result.get('appraisal', {})
            
            print("✅ Appraisal Successful")
            print("-" * 70)
            print(f"💵 Final Value: {appraisal.get('final_value', 0):.2f} 억원")
            print(f"📊 Confidence: {appraisal.get('confidence', 'N/A')}")
            
            # Check if premium was detected
            if 'premium_info' in result:
                premium_info = result['premium_info']
                print(f"\n🌟 Premium Info:")
                print(f"   Has Premium: {premium_info.get('has_premium', False)}")
                
                if premium_info.get('has_premium'):
                    print(f"   Premium: {premium_info.get('premium_percentage', 0):+.1f}%")
                    print(f"   Base Value: {premium_info.get('base_value', 0):.2f} 억원")
                    print(f"   Adjusted Value: {premium_info.get('adjusted_value', 0):.2f} 억원")
                    
                    top_5 = premium_info.get('top_5_factors', [])
                    if top_5:
                        print(f"\n   🏆 Top 5 Premium Factors:")
                        for i, factor in enumerate(top_5, 1):
                            print(f"      {i}. {factor['name']}: {factor['value']:+.1f}%")
                else:
                    print("   ⚠️  NO PREMIUM DETECTED")
            else:
                print("\n⚠️  WARNING: No premium_info in response")
            
            print("\n" + "=" * 70)
            print("TEST COMPLETE")
            print("=" * 70)
        else:
            print(f"❌ API returned non-success status: {result.get('status')}")
    else:
        print(f"❌ HTTP Error {response.status_code}")
        print(response.text)

except requests.exceptions.Timeout:
    print("❌ Request timed out after 30 seconds")
except Exception as e:
    print(f"❌ Error: {e}")
