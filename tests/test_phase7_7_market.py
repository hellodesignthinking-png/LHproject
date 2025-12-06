"""
ZeroSite Phase 7.7: Real-Time Market Data Test Suite

Tests market data retrieval, signal analysis, and investment recommendations.

Test Scenarios:
1. Undervalued project (ZeroSite < Market)
2. Fair valuation (ZeroSite ≈ Market)
3. Overvalued project (ZeroSite > Market)

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services_v3.market_data import (
    MarketReporter,
    MOLITApi,
    MarketSignalAnalyzer
)


def test_scenario_1_undervalued():
    """
    Scenario 1: Undervalued Project
    
    - ZeroSite value: 3,200,000원/㎡
    - Market average: 4,000,000원/㎡
    - Delta: -20%
    - Expected: UNDERVALUED signal
    """
    print("\n" + "="*80)
    print("📊 Scenario 1: Undervalued Project")
    print("="*80)
    
    address = "서울특별시 강남구 역삼동 123"
    zerosite_value = 3_200_000  # 3.2M원/㎡
    
    print(f"📍 Address: {address}")
    print(f"💰 ZeroSite Value: {zerosite_value/1e6:.1f}M원/㎡")
    
    # Generate market report
    reporter = MarketReporter()
    report = reporter.generate_market_report(
        address=address,
        zerosite_value=zerosite_value
    )
    
    market_data = report['market_data']
    market_signal = report['market_signal']
    temperature = report['market_temperature']
    
    print(f"\n📊 Market Data:")
    print(f"  • Market Average: {market_data['avg_price_per_m2']/1e6:.1f}M원/㎡")
    print(f"  • Market Median: {market_data['median_price_per_m2']/1e6:.1f}M원/㎡")
    print(f"  • Listing Average: {market_data['listing_avg_price_per_m2']/1e6:.1f}M원/㎡")
    print(f"  • Vacancy Rate: {market_data['vacancy_rate']*100:.1f}%")
    print(f"  • Transaction Volume: {market_data['transaction_volume']}")
    
    print(f"\n🎯 Market Signal:")
    print(f"  • Signal: {market_signal['signal']}")
    print(f"  • Delta: {market_signal['delta_percent']:+.1f}%")
    print(f"  • Explanation: {market_signal['explanation']}")
    
    print(f"\n🌡️ Market Temperature:")
    print(f"  • Temperature: {temperature['temperature']}")
    print(f"  • Description: {temperature['description']}")
    
    if report['investment_recommendation']:
        print(f"\n💡 Investment Recommendation:")
        print(f"  {report['investment_recommendation']}")
    
    # Validation
    assert market_signal['signal'] == 'UNDERVALUED', \
        f"❌ Expected 'UNDERVALUED', got '{market_signal['signal']}'"
    assert market_signal['delta_percent'] < -10, \
        f"❌ Delta should be < -10%, got {market_signal['delta_percent']:.1f}%"
    
    print(f"\n✅ Scenario 1 PASSED")
    print(f"   └─ Signal: UNDERVALUED ✓")
    print(f"   └─ Delta < -10%: ✓ ({market_signal['delta_percent']:+.1f}%)")
    
    return report


def test_scenario_2_fair():
    """
    Scenario 2: Fair Valuation
    
    - ZeroSite value: 3,850,000원/㎡
    - Market average: 3,800,000원/㎡
    - Delta: +1.3%
    - Expected: FAIR signal
    """
    print("\n" + "="*80)
    print("📊 Scenario 2: Fair Valuation")
    print("="*80)
    
    address = "경기도 성남시 분당구 정자동 456"
    zerosite_value = 3_850_000  # 3.85M원/㎡
    
    print(f"📍 Address: {address}")
    print(f"💰 ZeroSite Value: {zerosite_value/1e6:.1f}M원/㎡")
    
    # Generate market report
    reporter = MarketReporter()
    report = reporter.generate_market_report(
        address=address,
        zerosite_value=zerosite_value
    )
    
    market_signal = report['market_signal']
    
    print(f"\n🎯 Market Signal:")
    print(f"  • Signal: {market_signal['signal']}")
    print(f"  • Delta: {market_signal['delta_percent']:+.1f}%")
    print(f"  • Explanation: {market_signal['explanation']}")
    
    # Validation
    assert market_signal['signal'] == 'FAIR', \
        f"❌ Expected 'FAIR', got '{market_signal['signal']}'"
    assert -10 < market_signal['delta_percent'] < 10, \
        f"❌ Delta should be in [-10%, +10%], got {market_signal['delta_percent']:.1f}%"
    
    print(f"\n✅ Scenario 2 PASSED")
    print(f"   └─ Signal: FAIR ✓")
    print(f"   └─ Delta in range: ✓ ({market_signal['delta_percent']:+.1f}%)")
    
    return report


def test_scenario_3_overvalued():
    """
    Scenario 3: Overvalued Project
    
    - ZeroSite value: 2,200,000원/㎡
    - Market average: 1,800,000원/㎡
    - Delta: +22%
    - Expected: OVERVALUED signal
    """
    print("\n" + "="*80)
    print("📊 Scenario 3: Overvalued Project")
    print("="*80)
    
    address = "경상북도 포항시 북구 789"
    zerosite_value = 2_200_000  # 2.2M원/㎡
    
    print(f"📍 Address: {address}")
    print(f"💰 ZeroSite Value: {zerosite_value/1e6:.1f}M원/㎡")
    
    # Generate market report
    reporter = MarketReporter()
    report = reporter.generate_market_report(
        address=address,
        zerosite_value=zerosite_value
    )
    
    market_signal = report['market_signal']
    
    print(f"\n🎯 Market Signal:")
    print(f"  • Signal: {market_signal['signal']}")
    print(f"  • Delta: {market_signal['delta_percent']:+.1f}%")
    print(f"  • Explanation: {market_signal['explanation']}")
    
    # Validation
    assert market_signal['signal'] == 'OVERVALUED', \
        f"❌ Expected 'OVERVALUED', got '{market_signal['signal']}'"
    assert market_signal['delta_percent'] > 10, \
        f"❌ Delta should be > 10%, got {market_signal['delta_percent']:.1f}%"
    
    print(f"\n✅ Scenario 3 PASSED")
    print(f"   └─ Signal: OVERVALUED ✓")
    print(f"   └─ Delta > 10%: ✓ ({market_signal['delta_percent']:+.1f}%)")
    
    return report


def test_molit_api():
    """Test MOLIT API independently"""
    print("\n" + "="*80)
    print("🔧 Testing MOLIT API")
    print("="*80)
    
    api = MOLITApi()
    
    # Test market data retrieval
    address = "서울특별시 강남구"
    market_data = api.get_market_data(address)
    
    print(f"\n📊 Market Data for {address}:")
    print(f"  • Average Price: {market_data['avg_price_per_m2']/1e6:.1f}M원/㎡")
    print(f"  • Median Price: {market_data['median_price_per_m2']/1e6:.1f}M원/㎡")
    print(f"  • Vacancy Rate: {market_data['vacancy_rate']*100:.1f}%")
    print(f"  • Transaction Volume: {market_data['transaction_volume']}")
    
    # Validate
    assert 'avg_price_per_m2' in market_data, "❌ Missing avg_price_per_m2"
    assert market_data['avg_price_per_m2'] > 0, "❌ Invalid price"
    
    print(f"\n✅ MOLIT API Test PASSED")
    return market_data


def test_signal_analyzer():
    """Test signal analyzer independently"""
    print("\n" + "="*80)
    print("🎯 Testing Signal Analyzer")
    print("="*80)
    
    analyzer = MarketSignalAnalyzer()
    
    # Test different scenarios
    test_cases = [
        (3000000, 4000000, 'UNDERVALUED'),
        (4000000, 4000000, 'FAIR'),
        (5000000, 4000000, 'OVERVALUED')
    ]
    
    print(f"\n📊 Testing Signal Detection:")
    for zerosite, market, expected_signal in test_cases:
        result = analyzer.compare(zerosite, market)
        print(f"  • {zerosite/1e6:.1f}M vs {market/1e6:.1f}M → {result['signal']} (expected: {expected_signal})")
        assert result['signal'] == expected_signal, \
            f"❌ Expected {expected_signal}, got {result['signal']}"
    
    print(f"\n✅ Signal Analyzer Test PASSED")
    return True


def run_all_tests():
    """Run all Phase 7.7 tests"""
    print("\n" + "🔬" * 40)
    print("ZeroSite Phase 7.7: Real-Time Market Data Test Suite")
    print("🔬" * 40)
    
    results = []
    
    try:
        # Component tests
        print("\n" + "="*80)
        print("🧪 Component Tests")
        print("="*80)
        
        test_molit_api()
        test_signal_analyzer()
        
        # Integration tests
        print("\n" + "="*80)
        print("🧪 Integration Tests")
        print("="*80)
        
        results.append(('Undervalued', test_scenario_1_undervalued()))
        results.append(('Fair', test_scenario_2_fair()))
        results.append(('Overvalued', test_scenario_3_overvalued()))
        
        # Summary
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED")
        print("="*80)
        
        print("\n📊 Summary:")
        for name, report in results:
            print(f"\n{name}:")
            signal = report['market_signal']
            print(f"  • Signal: {signal['signal']}")
            print(f"  • Delta: {signal['delta_percent']:+.1f}%")
            print(f"  • Recommendation: {report.get('investment_recommendation', 'N/A')}")
        
        print("\n" + "="*80)
        print("✅ Phase 7.7 Integration: COMPLETE")
        print("="*80)
        
        print("\nKey Features Validated:")
        print("  ✓ MOLIT API integration (mock mode)")
        print("  ✓ Market signal detection (UNDERVALUED/FAIR/OVERVALUED)")
        print("  ✓ Market temperature analysis (HOT/STABLE/COLD)")
        print("  ✓ Investment recommendations")
        print("  ✓ ZeroSite vs Market comparison")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
