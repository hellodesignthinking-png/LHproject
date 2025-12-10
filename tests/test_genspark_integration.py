"""
ZeroSite Expert v3 - GenSpark AI Integration Tests

Comprehensive tests for all GenSpark AI enhanced components
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from backend.services.geocoding import EnhancedGeocodingService
from backend.services.transaction_generator import EnhancedTransactionGenerator
from backend.services.price_adjuster import EnhancedPriceAdjuster
from backend.services.confidence_calculator import EnhancedConfidenceCalculator
from app.engines_v9.land_valuation_engine_v9_1 import LandValuationEngineV91


class TestEnhancedServices:
    """Test enhanced backend services"""
    
    def test_geocoding_service(self):
        """Test enhanced geocoding"""
        print("\n🧪 Testing Enhanced Geocoding Service...")
        service = EnhancedGeocodingService()
        
        # Test multiple addresses
        test_cases = [
            ("서울특별시 강남구 역삼동 123-45", "서울특별시", "강남구"),
            ("경기도 성남시 분당구 정자동 100-1", "경기도", "성남시"),
            ("인천광역시 연수구 송도동 50-3", "인천광역시", "연수구")
        ]
        
        for address, expected_region, expected_district in test_cases:
            coords = service.geocode(address)
            
            assert coords.lat is not None, f"Latitude should not be None for {address}"
            assert coords.lng is not None, f"Longitude should not be None for {address}"
            assert coords.region == expected_region, f"Region mismatch for {address}"
            assert expected_district in coords.district or coords.district == "중심지", \
                f"District mismatch for {address}"
            
            print(f"   ✓ {address}")
            print(f"     → ({coords.lat:.6f}, {coords.lng:.6f}) - {coords.region} {coords.district}")
        
        print("   ✅ Geocoding service test PASSED")
    
    def test_transaction_generator(self):
        """Test dynamic transaction generation"""
        print("\n🧪 Testing Enhanced Transaction Generator...")
        generator = EnhancedTransactionGenerator()
        
        transactions = generator.generate_comparables(
            center_lat=37.5172,
            center_lng=127.0473,
            region="서울특별시",
            district="강남구",
            target_zone="제2종일반주거지역",
            target_size_sqm=1000.0,
            radius_km=1.5,
            count=10
        )
        
        assert len(transactions) == 10, "Should generate exactly 10 transactions"
        assert all(t.distance_km <= 1.5 for t in transactions), "All transactions should be within radius"
        assert transactions[0].distance_km <= transactions[-1].distance_km, "Should be sorted by distance"
        
        # Check price variation
        prices = [t.price_per_sqm for t in transactions]
        avg_price = sum(prices) / len(prices)
        assert avg_price > 0, "Average price should be positive"
        
        print(f"   ✓ Generated {len(transactions)} transactions")
        print(f"   ✓ Distance range: {transactions[0].distance_km:.2f}km ~ {transactions[-1].distance_km:.2f}km")
        print(f"   ✓ Price range: ₩{min(prices):,.0f} ~ ₩{max(prices):,.0f}/m²")
        print(f"   ✓ Average price: ₩{avg_price:,.0f}/m²")
        print("   ✅ Transaction generator test PASSED")
    
    def test_price_adjuster(self):
        """Test 4-factor price adjustment"""
        print("\n🧪 Testing Enhanced Price Adjuster...")
        
        # Generate test transactions
        gen = EnhancedTransactionGenerator()
        txns = gen.generate_comparables(
            center_lat=37.5172,
            center_lng=127.0473,
            region="서울특별시",
            district="강남구",
            target_zone="제2종일반주거지역",
            target_size_sqm=1000.0,
            radius_km=1.5,
            count=10
        )
        
        # Apply adjustments
        adjuster = EnhancedPriceAdjuster()
        adjusted = adjuster.adjust_transactions(
            transactions=txns,
            target_size_sqm=1000.0,
            target_zone="제2종일반주거지역"
        )
        
        assert len(adjusted) == 10, "Should adjust all transactions"
        
        # Check adjustment factors
        for adj in adjusted:
            factors = adj.factors
            assert -0.15 <= factors.total <= 0.0, "Total adjustment should be between -15% and 0%"
            assert -0.12 <= factors.distance <= 0.0, "Distance adjustment out of range"
            assert -0.12 <= factors.time <= 0.0, "Time adjustment out of range"
            assert -0.08 <= factors.size <= 0.0, "Size adjustment out of range"
            assert -0.05 <= factors.zone <= 0.0, "Zone adjustment out of range"
        
        # Verify weights sum to 1.0
        weights_sum = sum(adjuster.WEIGHTS.values())
        assert abs(weights_sum - 1.0) < 0.01, f"Weights should sum to 1.0, got {weights_sum}"
        
        # Calculate average adjustment
        avg_total_adj = sum(adj.factors.total for adj in adjusted) / len(adjusted)
        
        print(f"   ✓ Adjusted {len(adjusted)} transactions")
        print(f"   ✓ Weights: Distance {adjuster.WEIGHTS['distance']*100:.0f}%, "
              f"Time {adjuster.WEIGHTS['time']*100:.0f}%, "
              f"Size {adjuster.WEIGHTS['size']*100:.0f}%, "
              f"Zone {adjuster.WEIGHTS['zone']*100:.0f}%")
        print(f"   ✓ Average total adjustment: {avg_total_adj*100:.1f}%")
        print("   ✅ Price adjuster test PASSED")
    
    def test_confidence_calculator(self):
        """Test confidence scoring"""
        print("\n🧪 Testing Enhanced Confidence Calculator...")
        calc = EnhancedConfidenceCalculator()
        
        # Verify weights sum to 1.0
        weights_sum = sum(calc.WEIGHTS.values())
        assert abs(weights_sum - 1.0) < 0.01, f"Weights should sum to 1.0, got {weights_sum}"
        
        # Test scenarios
        test_scenarios = [
            {
                "name": "High Confidence",
                "transaction_count": 10,
                "adjusted_prices": [9.5e6, 9.6e6, 9.55e6, 9.58e6, 9.52e6,
                                  9.56e6, 9.54e6, 9.57e6, 9.53e6, 9.59e6],
                "average_price": 9.56e6,
                "distances_km": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.2, 0.4],
                "days_since_transactions": [45, 60, 75, 80, 90, 100, 110, 120, 50, 70],
                "expected_level": "HIGH",
                "min_score": 0.75
            },
            {
                "name": "Medium Confidence",
                "transaction_count": 7,
                "adjusted_prices": [9.0e6, 9.8e6, 9.4e6, 9.6e6, 9.2e6, 9.7e6, 9.3e6],
                "average_price": 9.43e6,
                "distances_km": [1.2, 1.5, 1.8, 1.3, 1.6, 1.4, 1.7],
                "days_since_transactions": [200, 250, 280, 220, 260, 240, 230],
                "expected_level": "MEDIUM",
                "min_score": 0.50
            }
        ]
        
        for scenario in test_scenarios:
            score, level = calc.calculate_confidence(**{k: v for k, v in scenario.items() 
                                                        if k not in ["name", "expected_level", "min_score"]})
            
            assert 0.0 <= score <= 1.0, f"Score should be between 0 and 1, got {score}"
            assert level.value in ["HIGH", "MEDIUM", "LOW"], f"Invalid level: {level}"
            assert score >= scenario["min_score"], \
                f"{scenario['name']} scenario should have score >= {scenario['min_score']}, got {score}"
            
            print(f"   ✓ {scenario['name']}: {score:.0%} ({level.value})")
        
        print(f"   ✓ Weights: Sample {calc.WEIGHTS['sample_size']*100:.0f}%, "
              f"Variance {calc.WEIGHTS['price_variance']*100:.0f}%, "
              f"Distance {calc.WEIGHTS['distance']*100:.0f}%, "
              f"Recency {calc.WEIGHTS['recency']*100:.0f}%")
        print("   ✅ Confidence calculator test PASSED")


class TestIntegratedEngine:
    """Test integrated valuation engine"""
    
    def test_enhanced_mode_full_pipeline(self):
        """Test full valuation with enhanced services"""
        print("\n🧪 Testing Land Valuation Engine v9.1 (Full Pipeline)...")
        
        engine = LandValuationEngineV91(use_enhanced_services=True)
        
        result = engine.evaluate_land(
            address="서울특별시 강남구 역삼동 123-45",
            land_size_sqm=1000.0,
            zone_type="제2종일반주거지역",
            asking_price=10_000_000_000,
            contract_months=6
        )
        
        # Verify structure
        required_keys = ['address', 'coordinates', 'prediction', 'comparables', 
                        'financial', 'strategies', 'mode', 'version']
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
        
        # Verify prediction
        pred = result['prediction']
        assert pred['avg'] > 0, "Average price should be positive"
        assert pred['low'] < pred['avg'] < pred['high'], "Price range should be valid"
        assert 0 <= pred['confidence'] <= 1, "Confidence should be between 0 and 1"
        assert pred['confidence_level'] in ['HIGH', 'MEDIUM', 'LOW'], "Invalid confidence level"
        
        # Verify comparables
        assert len(result['comparables']) == 10, "Should have 10 comparables"
        for comp in result['comparables']:
            assert 'address' in comp
            assert 'distance_km' in comp
            assert 'adjustments' in comp
            assert 'adjusted_price_per_sqm' in comp
        
        # Verify financial
        fin = result['financial']
        assert fin['total_cost'] > fin['land_price'], "Total cost should be > land price"
        assert fin['loan_amount'] > 0, "Loan amount should be positive"
        assert fin['equity_required'] > 0, "Equity required should be positive"
        
        # Verify strategies
        assert len(result['strategies']) == 3, "Should have 3 negotiation strategies"
        for strategy in result['strategies']:
            assert 'name' in strategy
            assert 'price' in strategy
            assert 'rationale' in strategy
        
        # Verify mode and version
        assert result['mode'] == 'enhanced', "Should be in enhanced mode"
        assert result['version'] == 'v9.1', "Should be version 9.1"
        
        # Verify enhanced features
        assert 'enhanced_features' in result
        features = result['enhanced_features']
        assert features['dynamic_transactions'] == True
        assert features['weighted_adjustments'] == True
        assert features['advanced_confidence'] == True
        
        print(f"\n   📊 RESULTS:")
        print(f"   ✓ Address: {result['address']}")
        print(f"   ✓ Coordinates: ({result['coordinates']['lat']}, {result['coordinates']['lng']})")
        print(f"   ✓ Region: {result['coordinates']['region']} {result['coordinates']['district']}")
        print(f"   ✓ Predicted price: ₩{pred['avg']:,.0f}")
        print(f"   ✓ Price range: ₩{pred['low']:,.0f} ~ ₩{pred['high']:,.0f}")
        print(f"   ✓ Confidence: {pred['confidence']:.0%} ({pred['confidence_level']})")
        print(f"   ✓ Comparables: {len(result['comparables'])} transactions")
        print(f"   ✓ Total cost: ₩{fin['total_cost']:,.0f}")
        print(f"   ✓ Strategies: {len(result['strategies'])} negotiation strategies")
        print(f"   ✓ Mode: {result['mode']} (v{result['version']})")
        print("   ✅ Full pipeline test PASSED")
        
        return result


def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("\n" + "="*80)
    print("🎯 ZeroSite Expert v3 - GenSpark AI Integration Tests")
    print("="*80)
    
    try:
        # Test enhanced services
        print("\n📦 PHASE 1: Enhanced Services Tests")
        print("-"*80)
        
        test_services = TestEnhancedServices()
        test_services.test_geocoding_service()
        test_services.test_transaction_generator()
        test_services.test_price_adjuster()
        test_services.test_confidence_calculator()
        
        # Test integrated engine
        print("\n🔧 PHASE 2: Integrated Engine Tests")
        print("-"*80)
        
        test_engine = TestIntegratedEngine()
        result = test_engine.test_enhanced_mode_full_pipeline()
        
        # Final summary
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        
        print("\n📊 SUMMARY:")
        print(f"   ✓ Enhanced Services: 4/4 tests passed")
        print(f"   ✓ Integrated Engine: 1/1 test passed")
        print(f"   ✓ Total: 5/5 tests passed (100%)")
        
        print("\n🎉 GenSpark AI Integration is FULLY FUNCTIONAL!")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
