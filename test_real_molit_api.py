#!/usr/bin/env python3
"""
Test MOLIT API + Kakao Geocoding + Comprehensive Collector
실제 API 연동 테스트
"""

import sys
sys.path.insert(0, '/home/user/webapp')

import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("=" * 100)
print("🧪 MOLIT API + Kakao + Comprehensive Collector 테스트")
print("=" * 100)

# Test 1: MOLIT API
print("\n" + "=" * 100)
print("TEST 1: MOLIT API 단독 테스트")
print("=" * 100)

from app.services.real_transaction_api import get_molit_api

molit = get_molit_api()

# 강남구 2024년 11월 데이터
print("\n📊 2024년 11월 강남구 토지 거래 조회...")
transactions = molit.get_land_transactions(
    sigungu_code='11680',  # 강남구
    year_month='202411'
)

print(f"\n✅ 조회 결과: {len(transactions)}건")

if transactions:
    print(f"\n📄 샘플 데이터 (최신 3건):")
    for i, tx in enumerate(transactions[:3], 1):
        print(f"\n{i}. {tx['transaction_date']} | {tx['address']}")
        print(f"   면적: {tx['land_area_sqm']}㎡")
        print(f"   단가: {tx['price_per_sqm']:,}원/㎡")
        print(f"   총액: {tx['total_price']:,}원 ({tx['total_price']/100000000:.2f}억원)")

# Test 2: Kakao Geocoding
print("\n" + "=" * 100)
print("TEST 2: Kakao Geocoding 테스트")
print("=" * 100)

from app.services.kakao_geocoding import get_kakao_geocoding

kakao = get_kakao_geocoding()

test_addresses = [
    "서울 강남구 역삼동 123-4",
    "서울 마포구 월드컵북로 120",
    "서울 강남구 테헤란로 152"
]

for addr in test_addresses:
    coords = kakao.get_coordinates(addr)
    road_name = kakao.get_road_name(addr)
    road_grade = kakao.classify_road_grade(road_name)
    
    print(f"\n📍 {addr}")
    print(f"   좌표: {coords}")
    print(f"   도로명: {road_name}")
    print(f"   등급: {road_grade}")

# Test 3: Comprehensive Collector
print("\n" + "=" * 100)
print("TEST 3: Comprehensive Transaction Collector")
print("=" * 100)

from app.services.comprehensive_transaction_collector import get_transaction_collector

collector = get_transaction_collector()

test_cases = [
    {
        'address': '서울 강남구 역삼동 123-4',
        'area': 660
    },
    {
        'address': '서울 마포구 공덕동 100',
        'area': 500
    }
]

for test in test_cases:
    print(f"\n{'='*100}")
    print(f"TEST CASE: {test['address']} ({test['area']}㎡)")
    print('='*100)
    
    result = collector.collect_nearby_transactions(
        address=test['address'],
        land_area_sqm=test['area'],
        max_distance_km=2.0,
        num_months=6,  # 6개월 (빠른 테스트)
        min_count=10,
        max_count=15
    )
    
    print(f"\n✅ 최종 결과: {len(result)}건")
    
    if result:
        print(f"\n📊 상세 정보:")
        
        # 통계
        api_count = len([tx for tx in result if tx.get('source') == 'MOLIT_API'])
        fallback_count = len([tx for tx in result if tx.get('source') == 'FALLBACK'])
        
        print(f"   - MOLIT API: {api_count}건")
        print(f"   - Fallback: {fallback_count}건")
        
        # 평균 단가
        avg_price = sum([tx['price_per_sqm'] for tx in result]) / len(result)
        print(f"   - 평균 단가: {avg_price:,.0f}원/㎡")
        
        # 상위 5건
        print(f"\n📄 거래사례 (상위 5건):")
        for i, tx in enumerate(result[:5], 1):
            source_badge = "🟢 API" if tx.get('source') == 'MOLIT_API' else "🔵 Fallback"
            print(f"\n{i}. [{source_badge}] {tx['transaction_date']} | {tx['address']}")
            print(f"   거리: {tx['distance_km']}km | 면적: {tx['land_area_sqm']}㎡")
            print(f"   도로: {tx['road_name']} [{tx['road_grade']}]")
            print(f"   단가: {tx['price_per_sqm']:,}원/㎡ | 총액: {tx['total_price']/100000000:.2f}억원")

print("\n" + "=" * 100)
print("🎉 모든 테스트 완료!")
print("=" * 100)
