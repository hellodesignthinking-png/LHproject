"""
ZeroSite v18 Phase 4 - Cache System Test
=========================================
실거래가 API 캐싱 기능 검증
"""

import asyncio
import time
from app.services.real_transaction_api import RealTransactionAPI
from app.services.real_transaction_cache import get_cache

async def main():
    print("\n" + "=" * 80)
    print("ZeroSite v18 Phase 4 - Real Transaction Cache Test")
    print("=" * 80 + "\n")
    
    # Initialize API with caching enabled
    api = RealTransactionAPI(enable_cache=True)
    cache = get_cache()
    
    # Test address
    test_address = "서울특별시 마포구 월드컵북로 120"
    test_lawd_cd = "11"  # 서울
    test_deal_ymd = "202412"  # December 2024
    
    print(f"📍 Test Address: {test_address}")
    print(f"📅 Deal Period: {test_deal_ymd}")
    print(f"🔍 Region Code: {test_lawd_cd}\n")
    
    # Test 1: First fetch (cache miss - should hit API)
    print("=" * 80)
    print("TEST 1: First Fetch (Cache MISS expected)")
    print("=" * 80)
    
    start_time = time.time()
    land_txns, building_txns = await api.fetch_comparables(
        address=test_address,
        lawd_cd=test_lawd_cd,
        radius_m=1000
    )
    first_duration = time.time() - start_time
    
    print(f"\n⏱️  Duration: {first_duration:.2f}s")
    print(f"🏞️  Land transactions: {len(land_txns)}")
    print(f"🏢 Building transactions: {len(building_txns)}")
    
    if land_txns:
        avg_land = sum(t.unit_krw_m2 for t in land_txns) / len(land_txns)
        print(f"📊 Average land price: {avg_land/10000:.1f}만원/㎡")
    
    if building_txns:
        avg_building = sum(t.unit_krw_m2 for t in building_txns) / len(building_txns)
        print(f"📊 Average building price: {avg_building/10000:.1f}만원/㎡")
    
    # Wait a moment
    await asyncio.sleep(2)
    
    # Test 2: Second fetch (cache hit - should be instant)
    print("\n" + "=" * 80)
    print("TEST 2: Second Fetch (Cache HIT expected)")
    print("=" * 80)
    
    start_time = time.time()
    land_txns_2, building_txns_2 = await api.fetch_comparables(
        address=test_address,
        lawd_cd=test_lawd_cd,
        radius_m=1000
    )
    second_duration = time.time() - start_time
    
    print(f"\n⏱️  Duration: {second_duration:.2f}s")
    print(f"⚡ Speed improvement: {first_duration/second_duration:.1f}x faster")
    print(f"🏞️  Land transactions: {len(land_txns_2)}")
    print(f"🏢 Building transactions: {len(building_txns_2)}")
    
    # Test 3: Cache statistics
    print("\n" + "=" * 80)
    print("TEST 3: Cache Statistics")
    print("=" * 80)
    
    cache.print_stats()
    
    # Test 4: Test with different region (cache miss)
    print("=" * 80)
    print("TEST 4: Different Region (Cache MISS expected)")
    print("=" * 80)
    
    test_address_2 = "경기도 성남시 분당구 정자동"
    test_lawd_cd_2 = "41"  # 경기
    
    print(f"📍 Test Address: {test_address_2}")
    
    start_time = time.time()
    land_txns_3, building_txns_3 = await api.fetch_comparables(
        address=test_address_2,
        lawd_cd=test_lawd_cd_2,
        radius_m=1000
    )
    third_duration = time.time() - start_time
    
    print(f"\n⏱️  Duration: {third_duration:.2f}s")
    print(f"🏞️  Land transactions: {len(land_txns_3)}")
    print(f"🏢 Building transactions: {len(building_txns_3)}")
    
    # Final cache statistics
    print("\n" + "=" * 80)
    print("FINAL Cache Statistics")
    print("=" * 80)
    
    cache.print_stats()
    
    print("=" * 80)
    print("✅ Cache Test Complete!")
    print("=" * 80)
    print(f"\nPerformance Summary:")
    print(f"  - First fetch: {first_duration:.2f}s (cache miss)")
    print(f"  - Second fetch: {second_duration:.2f}s (cache hit)")
    print(f"  - Speed improvement: {first_duration/second_duration:.1f}x")
    print(f"  - Cache entries: {len(cache.metadata)}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
