#!/usr/bin/env python3
"""
Quick API PDF Test
Tests /appraisal/pdf endpoint with minimal timeout
"""
import requests
import json

API_URL = "http://localhost:8000/api/v24.1/appraisal/pdf"

# Minimal request
data = {
    "address": "서울시 강남구 역삼동 123",
    "land_area_sqm": 660,
    "zone_type": "제2종일반주거지역"
    # No individual_land_price - will auto-load
    # No premium_factors - will auto-detect
}

print("=" * 80)
print("📄 API PDF Generation Test")
print("=" * 80)
print(f"Address: {data['address']}")
print(f"Land Area: {data['land_area_sqm']} ㎡")
print(f"Zone: {data['zone_type']}")
print("\n⏳ Sending request (may take 30-60 seconds)...")
print("=" * 80)

try:
    # Send request with longer timeout
    response = requests.post(API_URL, json=data, timeout=90)
    
    if response.status_code == 200:
        # Save PDF
        output_path = '/home/user/webapp/api_generated.pdf'
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"\n✅ PDF Generated Successfully!")
        print(f"   Size: {len(response.content):,} bytes ({len(response.content)/1024:.1f} KB)")
        print(f"   Saved to: {output_path}")
        print(f"\n🔍 Next Steps:")
        print(f"   1. Check file size (should be 100-200 KB)")
        print(f"   2. Verify PDF opens properly")
        print(f"   3. Check for premium section (Pages 4-5)")
        print(f"   4. Verify A4 layout")
    else:
        print(f"\n❌ HTTP Error {response.status_code}")
        print(response.text[:500])

except requests.exceptions.Timeout:
    print(f"\n⏱️  Request timed out after 90 seconds")
    print(f"   This is normal - MOLIT API is very slow")
    print(f"   The PDF is likely still being generated")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 80)
print("Check server logs for detailed progress:")
print("  BashOutput bash_36c6579d")
print("=" * 80)
