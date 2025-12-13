#!/usr/bin/env python3
"""
v28.0 최종 검증 스크립트
3개 주소로 완전한 테스트 수행
"""

import sys
import time
sys.path.insert(0, '/home/user/webapp')

from app.services.advanced_address_parser import get_address_parser
from app.services.seoul_market_prices import SeoulMarketPrices
from app.services.comprehensive_transaction_collector import get_transaction_collector

def test_complete_system():
    """Complete v28.0 system validation"""
    
    print("=" * 80)
    print("🔍 ZeroSite v28.0 - Final Validation Test")
    print("=" * 80)
    
    test_cases = [
        {
            'name': '마포구 월드컵북로',
            'address': '서울 마포구 월드컵북로 120',
            'area': 660.0,
            'expected_gu': '마포구',
            'expected_dong': '상암동',
            'expected_price_min': 12000000,
            'expected_price_max': 16000000,
        },
        {
            'name': '강남구 테헤란로',
            'address': '서울 강남구 테헤란로 427',
            'area': 500.0,
            'expected_gu': '강남구',
            'expected_dong': '역삼동',
            'expected_price_min': 20000000,
            'expected_price_max': 24000000,
        },
        {
            'name': '서초구 서초대로',
            'address': '서울 서초구 서초대로 78길 22',
            'area': 400.0,
            'expected_gu': '서초구',
            'expected_dong': '서초동',
            'expected_price_min': 18000000,
            'expected_price_max': 22000000,
        }
    ]
    
    parser = get_address_parser()
    collector = get_transaction_collector()
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"📍 Test {i}: {test['name']}")
        print(f"{'='*80}")
        print(f"Address: {test['address']}")
        print(f"Area: {test['area']}㎡")
        
        # Step 1: Address Parsing
        print(f"\n🔍 Step 1: Address Parsing")
        parsed = parser.parse(test['address'])
        
        gu_ok = parsed['gu'] == test['expected_gu']
        dong_ok = parsed['dong'] == test['expected_dong']
        
        print(f"   Gu: {parsed['gu']} {'✅' if gu_ok else '❌ Expected: ' + test['expected_gu']}")
        print(f"   Dong: {parsed['dong']} {'✅' if dong_ok else '❌ Expected: ' + test['expected_dong']}")
        print(f"   Road: {parsed['road_name']}")
        print(f"   Method: {parsed['method']}")
        
        if not (gu_ok and dong_ok):
            all_passed = False
            print(f"\n❌ FAILED: Address parsing incorrect")
            continue
        
        # Step 2: Market Prices
        print(f"\n💰 Step 2: Market Prices")
        price = SeoulMarketPrices.get_price(parsed['gu'], parsed['dong'])
        pyeong_price = SeoulMarketPrices.get_pyeong_price(parsed['gu'], parsed['dong'])
        
        price_ok = test['expected_price_min'] <= price <= test['expected_price_max']
        
        print(f"   ㎡당: {price:,}원 {'✅' if price_ok else '❌'}")
        print(f"   평당: {pyeong_price:,}원")
        print(f"   Expected: {test['expected_price_min']:,}~{test['expected_price_max']:,}원/㎡")
        
        if not price_ok:
            all_passed = False
            print(f"\n❌ FAILED: Price out of expected range")
            continue
        
        # Step 3: Transaction Collection
        print(f"\n📊 Step 3: Transaction Collection")
        transactions = collector.collect_nearby_transactions(
            address=test['address'],
            land_area_sqm=test['area'],
            max_distance_km=2.0,
            num_months=24,
            min_count=10,
            max_count=15
        )
        
        count_ok = len(transactions) >= 10
        print(f"   Transactions: {len(transactions)} {'✅' if count_ok else '❌ (need ≥10)'}")
        
        if not count_ok:
            all_passed = False
            print(f"\n❌ FAILED: Too few transactions")
            continue
        
        # Validate addresses
        correct_gu_count = sum(1 for tx in transactions if test['expected_gu'] in tx['address'])
        gu_accuracy = correct_gu_count / len(transactions) * 100
        
        print(f"   Correct Gu: {correct_gu_count}/{len(transactions)} ({gu_accuracy:.0f}%)")
        
        # Validate prices
        avg_price = sum(tx['price_per_sqm'] for tx in transactions) / len(transactions)
        price_range_ok = test['expected_price_min'] * 0.8 <= avg_price <= test['expected_price_max'] * 1.2
        
        print(f"   Avg Price: {avg_price:,.0f}원/㎡ {'✅' if price_range_ok else '❌'}")
        print(f"   Range: {min(tx['price_per_sqm'] for tx in transactions):,}~{max(tx['price_per_sqm'] for tx in transactions):,}원/㎡")
        
        # Check for "기타"
        has_gita = any('기타' in tx['address'] for tx in transactions)
        if has_gita:
            print(f"   ❌ CRITICAL: Found '서울 기타' in transactions!")
            all_passed = False
            continue
        else:
            print(f"   ✅ No '서울 기타' addresses")
        
        # Final judgment
        test_ok = gu_ok and dong_ok and price_ok and count_ok and price_range_ok and not has_gita
        
        if test_ok:
            print(f"\n🎉 Test {i} PASSED")
        else:
            print(f"\n❌ Test {i} FAILED")
            all_passed = False
    
    # Final Results
    print(f"\n{'='*80}")
    print(f"📊 FINAL RESULTS")
    print(f"{'='*80}")
    
    if all_passed:
        print(f"✅✅✅ ALL TESTS PASSED! v28.0 is PRODUCTION READY! ✅✅✅")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED - Need fixes")
        return 1

if __name__ == '__main__':
    sys.exit(test_complete_system())
