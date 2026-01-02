#!/usr/bin/env python3
"""
실제 API 키로 Kakao 주소 검색 테스트
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

KAKAO_API_KEY = os.getenv("KAKAO_REST_API_KEY")

def test_kakao_api(address: str):
    """Test Kakao address search API"""
    print(f"\n🔍 Testing Kakao API with address: {address}")
    print(f"📝 API Key: {KAKAO_API_KEY[:10]}...")
    
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }
    params = {
        "query": address
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("documents"):
            doc = data["documents"][0]
            print(f"\n✅ Success!")
            print(f"📍 Address: {doc.get('address_name', 'N/A')}")
            print(f"🗺️  Latitude: {doc.get('y', 'N/A')}")
            print(f"🗺️  Longitude: {doc.get('x', 'N/A')}")
            
            # Check for road address
            if doc.get("road_address"):
                road = doc["road_address"]
                print(f"🛣️  Road Address: {road.get('address_name', 'N/A')}")
                print(f"🏛️  B-Code: {road.get('building_name', 'N/A')}")
            
            return True
        else:
            print(f"\n⚠️  No results found for: {address}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Test addresses
    test_addresses = [
        "서울특별시 강남구 테헤란로 152",
        "서울특별시 강남구 역삼동 823",
        "서울시 종로구 세종대로 175"
    ]
    
    print("=" * 60)
    print("🧪 Kakao API Test with Real API Key")
    print("=" * 60)
    
    results = []
    for addr in test_addresses:
        success = test_kakao_api(addr)
        results.append((addr, success))
        print("-" * 60)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    success_count = sum(1 for _, success in results if success)
    print(f"✅ Successful: {success_count}/{len(results)}")
    print(f"❌ Failed: {len(results) - success_count}/{len(results)}")
    
    if success_count == len(results):
        print("\n🎉 All tests passed! Kakao API is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check API key and network.")
        sys.exit(1)
