"""
Test Kakao Map API Service
===========================

Quick test script for Kakao Map integration
"""

import asyncio
import sys
sys.path.append('/home/user/webapp')

from app.services.kakao.kakao_map_service import KakaoMapService


async def test_kakao_service():
    """Test Kakao Map Service"""
    
    service = KakaoMapService()
    
    # Test address
    test_address = "서울특별시 마포구 월드컵북로 120"
    
    print(f"\n🧪 Testing Kakao Map Service")
    print(f"📍 Address: {test_address}\n")
    
    # Test 1: Address to coordinates
    print("1️⃣ Converting address to coordinates...")
    coords = await service.address_to_coordinates(test_address)
    if coords:
        print(f"   ✅ Coordinates: {coords}")
    else:
        print(f"   ❌ Failed to convert address")
        return
    
    lat, lon = coords
    
    # Test 2: Collect subway stations
    print("\n2️⃣ Collecting subway stations...")
    subway_stations = await service.collect_subway_stations(test_address, radius=1000)
    print(f"   ✅ Found {len(subway_stations)} stations")
    for station in subway_stations[:3]:
        print(f"      - {station['name']} ({station['line']}) - {station['distance_m']}m")
    
    # Test 3: Collect bus stops
    print("\n3️⃣ Collecting bus stops...")
    bus_stops = await service.collect_bus_stops(test_address, radius=500)
    print(f"   ✅ Found {len(bus_stops)} stops")
    for stop in bus_stops[:3]:
        print(f"      - {stop['name']} - {stop['distance_m']}m")
    
    # Test 4: Collect schools
    print("\n4️⃣ Collecting schools...")
    schools = await service.collect_schools(test_address, radius=1000)
    print(f"   ✅ Found {len(schools)} schools")
    for school in schools[:3]:
        print(f"      - {school['name']} ({school['type']}) - {school['distance_m']}m")
    
    # Test 5: Collect commercial facilities
    print("\n5️⃣ Collecting commercial facilities...")
    commercial = await service.collect_commercial_facilities(test_address, radius=1000)
    print(f"   ✅ Found {len(commercial)} facilities")
    for facility in commercial[:5]:
        print(f"      - {facility['name']} ({facility['type']}) - {facility['distance_m']}m")
    
    # Test 6: Collect all POI
    print("\n6️⃣ Collecting all POI data...")
    all_poi = await service.collect_all_poi(test_address)
    print(f"   ✅ Complete POI data:")
    print(f"      - Subway stations: {len(all_poi['subway_stations'])}")
    print(f"      - Bus stops: {len(all_poi['bus_stops'])}")
    print(f"      - Schools: {len(all_poi['poi_schools'])}")
    print(f"      - Commercial: {len(all_poi['poi_commercial'])}")
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_kakao_service())
