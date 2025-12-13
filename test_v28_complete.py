"""
v28.0 Complete System Test
Tests the three critical fixes:
1. Address parsing: 월드컵북로 120 → 마포구
2. Real market prices: 12-15M/㎡ for Mapo-gu
3. Complete transaction data
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.advanced_address_parser import get_address_parser
from app.services.seoul_market_prices import SeoulMarketPrices
from app.services.comprehensive_transaction_collector import get_transaction_collector

def test_v28_system():
    """Test v28.0 complete system"""
    
    print("=" * 80)
    print("🧪 v28.0 Complete System Test")
    print("=" * 80)
    
    # Test Case: 월드컵북로 120 (Mapo-gu)
    test_address = "서울 마포구 월드컵북로 120"
    test_area = 660.0
    
    print(f"\n📍 Test Address: {test_address}")
    print(f"📐 Test Area: {test_area}㎡")
    
    # Step 1: Address Parsing
    print("\n" + "=" * 80)
    print("STEP 1: Address Parsing")
    print("=" * 80)
    
    parser = get_address_parser()
    parsed = parser.parse(test_address)
    
    print(f"✅ Gu: {parsed['gu']}")
    print(f"✅ Dong: {parsed['dong']}")
    print(f"✅ Road: {parsed['road_name']}")
    print(f"✅ Success: {parsed['success']}")
    print(f"✅ Method: {parsed['method']}")
    
    # Validate
    assert parsed['success'] == True, "❌ Address parsing failed"
    assert parsed['gu'] == '마포구', f"❌ Wrong gu: {parsed['gu']}"
    
    # Step 2: Market Prices
    print("\n" + "=" * 80)
    print("STEP 2: Market Prices")
    print("=" * 80)
    
    sqm_price = SeoulMarketPrices.get_price(parsed['gu'], parsed['dong'])
    pyeong_price = SeoulMarketPrices.get_pyeong_price(parsed['gu'], parsed['dong'])
    
    print(f"✅ {parsed['gu']} {parsed['dong']}")
    print(f"✅ ㎡당: {sqm_price:,}원")
    print(f"✅ 평당: {pyeong_price:,}원")
    
    # Validate (Mapo-gu should be 12-16M/㎡)
    assert 12000000 <= sqm_price <= 16000000, f"❌ Price out of range: {sqm_price}"
    
    # Step 3: Transaction Collection
    print("\n" + "=" * 80)
    print("STEP 3: Transaction Collection")
    print("=" * 80)
    
    collector = get_transaction_collector()
    transactions = collector.collect_nearby_transactions(
        address=test_address,
        land_area_sqm=test_area,
        max_distance_km=2.0,
        num_months=24,
        min_count=10,
        max_count=15
    )
    
    print(f"\n✅ Total Transactions: {len(transactions)}")
    print(f"✅ First Transaction:")
    print(f"   Date: {transactions[0]['transaction_date']}")
    print(f"   Address: {transactions[0]['address']}")
    print(f"   Area: {transactions[0]['land_area_sqm']:.1f}㎡")
    print(f"   Price: {transactions[0]['price_per_sqm']:,}원/㎡")
    print(f"   Distance: {transactions[0]['distance_km']}km")
    
    # Calculate average
    avg_price = sum(tx['price_per_sqm'] for tx in transactions) / len(transactions)
    
    print(f"\n💰 Average Price: {avg_price:,.0f}원/㎡")
    print(f"💰 Expected for 마포구: 12,000,000-15,000,000원/㎡")
    print(f"💰 Accuracy: {(avg_price / 13000000 * 100):.1f}%")
    
    # Validate
    assert len(transactions) >= 10, f"❌ Too few transactions: {len(transactions)}"
    assert 10000000 <= avg_price <= 16000000, f"❌ Average price out of range: {avg_price}"
    
    # Check addresses contain 마포구
    mapo_count = sum(1 for tx in transactions if '마포구' in tx['address'])
    print(f"\n📍 Addresses with 마포구: {mapo_count}/{len(transactions)}")
    assert mapo_count >= len(transactions) * 0.8, "❌ Too few 마포구 addresses"
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - v28.0 System Working!")
    print("=" * 80)
    
    # Final appraisal estimate
    total_value = avg_price * test_area
    print(f"\n💰 Final Appraisal Estimate:")
    print(f"   {avg_price:,.0f}원/㎡ × {test_area}㎡")
    print(f"   = {total_value:,.0f}원")
    print(f"   = {total_value/100000000:.2f}억원")
    
    return {
        'parsed': parsed,
        'sqm_price': sqm_price,
        'pyeong_price': pyeong_price,
        'transactions': transactions,
        'avg_price': avg_price,
        'total_value': total_value
    }

if __name__ == '__main__':
    try:
        result = test_v28_system()
        print("\n✅ Test completed successfully")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
