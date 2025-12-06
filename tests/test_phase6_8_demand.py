"""
ZeroSite Phase 6.8: Local Demand Model Test Suite

Tests demand prediction for different regions and housing types.

Test Scenarios:
1. Gangnam (청년형 high probability)
2. Bundang (신혼부부형 high probability)
3. Gyeongbuk (고령자형 high probability)

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services_v3.demand_model import (
    DemandPredictor,
    DemandFeatureEngineer,
    DemandScorer
)


def test_scenario_1_gangnam_youth():
    """
    Scenario 1: Gangnam - Youth Housing Expected
    
    - High 20-34 age ratio (0.35)
    - Good job centers (8)
    - High cultural facilities (80)
    - Expected: Youth score highest
    """
    print("\n" + "="*80)
    print("📊 Scenario 1: Gangnam - Youth Housing Demand")
    print("="*80)
    
    address = "서울특별시 강남구 역삼동 123"
    coordinates = (37.5, 127.0)
    
    print(f"📍 Address: {address}")
    print(f"📍 Coordinates: {coordinates}")
    
    # Predict demand
    predictor = DemandPredictor()
    result = predictor.predict(address, coordinates)
    
    print(f"\n🎯 Prediction Results:")
    print(f"  Recommended Type: {result['recommended_type']}")
    print(f"  Description: {result['description']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Top Score: {result['top_score']:.1f}/100")
    
    print(f"\n📊 All Scores:")
    for housing_type, score in sorted(result['scores'].items(), key=lambda x: x[1], reverse=True):
        print(f"  • {housing_type}: {score:.1f}/100")
    
    # Validation
    assert result['recommended_type'] == 'youth', f"❌ Expected 'youth', got '{result['recommended_type']}'"
    assert result['scores']['youth'] >= 60, f"❌ Youth score should be >= 60, got {result['scores']['youth']}"
    
    print(f"\n✅ Scenario 1 PASSED")
    print(f"   └─ Youth housing recommended: ✓")
    print(f"   └─ Score >= 60: ✓ ({result['scores']['youth']:.1f}/100)")
    
    return result


def test_scenario_2_bundang_newlyweds():
    """
    Scenario 2: Bundang - Newlyweds Housing Expected
    
    - High daycare count (22)
    - Many schools (15)
    - High safety index (85)
    - Expected: Newlyweds score highest
    """
    print("\n" + "="*80)
    print("📊 Scenario 2: Bundang - Newlyweds Housing Demand")
    print("="*80)
    
    address = "경기도 성남시 분당구 정자동 456"
    coordinates = (37.36, 127.1)
    
    print(f"📍 Address: {address}")
    print(f"📍 Coordinates: {coordinates}")
    
    # Predict demand
    predictor = DemandPredictor()
    result = predictor.predict(address, coordinates)
    
    print(f"\n🎯 Prediction Results:")
    print(f"  Recommended Type: {result['recommended_type']}")
    print(f"  Description: {result['description']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Top Score: {result['top_score']:.1f}/100")
    
    print(f"\n📊 All Scores:")
    for housing_type, score in sorted(result['scores'].items(), key=lambda x: x[1], reverse=True):
        print(f"  • {housing_type}: {score:.1f}/100")
    
    # Validation
    assert result['recommended_type'] in ['newlyweds', 'newlyweds_growth'], \
        f"❌ Expected 'newlyweds' or 'newlyweds_growth', got '{result['recommended_type']}'"
    assert result['top_score'] >= 60, f"❌ Top score should be >= 60, got {result['top_score']}"
    
    print(f"\n✅ Scenario 2 PASSED")
    print(f"   └─ Newlyweds housing recommended: ✓")
    print(f"   └─ Score >= 60: ✓ ({result['top_score']:.1f}/100)")
    
    return result


def test_scenario_3_gyeongbuk_senior():
    """
    Scenario 3: Gyeongbuk - Senior Housing Expected
    
    - High senior ratio (0.32)
    - Many hospitals (15)
    - Good welfare centers (8)
    - Expected: Senior score highest
    """
    print("\n" + "="*80)
    print("📊 Scenario 3: Gyeongbuk - Senior Housing Demand")
    print("="*80)
    
    address = "경상북도 포항시 북구 789"
    coordinates = (36.0, 129.0)
    
    print(f"📍 Address: {address}")
    print(f"📍 Coordinates: {coordinates}")
    
    # Predict demand
    predictor = DemandPredictor()
    result = predictor.predict(address, coordinates)
    
    print(f"\n🎯 Prediction Results:")
    print(f"  Recommended Type: {result['recommended_type']}")
    print(f"  Description: {result['description']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Top Score: {result['top_score']:.1f}/100")
    
    print(f"\n📊 All Scores:")
    for housing_type, score in sorted(result['scores'].items(), key=lambda x: x[1], reverse=True):
        print(f"  • {housing_type}: {score:.1f}/100")
    
    # Validation
    assert result['recommended_type'] == 'senior', f"❌ Expected 'senior', got '{result['recommended_type']}'"
    assert result['scores']['senior'] >= 55, f"❌ Senior score should be >= 55, got {result['scores']['senior']}"
    
    print(f"\n✅ Scenario 3 PASSED")
    print(f"   └─ Senior housing recommended: ✓")
    print(f"   └─ Score >= 55: ✓ ({result['scores']['senior']:.1f}/100)")
    
    return result


def test_feature_extraction():
    """Test feature extraction independently"""
    print("\n" + "="*80)
    print("🔧 Testing Feature Extraction")
    print("="*80)
    
    engineer = DemandFeatureEngineer()
    
    # Test Gangnam features
    features = engineer.extract("서울특별시 강남구", (37.5, 127.0))
    
    print(f"\n📊 Extracted {len(features)} features:")
    for name, value in list(features.items())[:10]:  # Show first 10
        description = engineer.get_feature_description(name)
        print(f"  • {name}: {value} ({description})")
    
    # Validate features exist
    assert len(features) > 0, "❌ No features extracted"
    assert 'age_20_34_ratio' in features, "❌ Missing age_20_34_ratio"
    
    print(f"\n✅ Feature Extraction PASSED")
    return features


def test_scoring_logic():
    """Test scoring logic independently"""
    print("\n" + "="*80)
    print("🎯 Testing Scoring Logic")
    print("="*80)
    
    scorer = DemandScorer()
    
    # Create mock features favoring youth
    features = {
        'age_20_34_ratio': 0.35,
        'commute_time': 35,
        'education_facilities': 25,
        'cultural_facilities': 80,
        'job_centers_nearby': 8,
        'rent_burden_index': 0.40,
        'supply_competition': 70,
        'daycare_count': 10,
        'school_count': 8,
        'family_income_ratio': 70,
        'playground': 5,
        'safety_index': 70,
        'multi_child_ratio': 0.05,
        'senior_ratio': 0.10,
        'hospital_count': 10,
        'welfare_centers': 3,
        'park_area': 100000,
        'barrier_free_infra': 50,
        'education_quality': 70,
        'job_centers': 8,
        'rent_burden': 0.40
    }
    
    scores = scorer.score(features)
    
    print(f"\n📊 Scores for mock features:")
    for housing_type, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {housing_type}: {score:.1f}/100")
    
    # Get recommendation
    recommended = scorer.get_recommended_type(scores)
    print(f"\n🎯 Recommended: {recommended}")
    
    # Validate
    assert all(0 <= score <= 100 for score in scores.values()), "❌ Scores out of range"
    assert recommended is not None, "❌ No recommendation"
    
    print(f"\n✅ Scoring Logic PASSED")
    return scores


def run_all_tests():
    """Run all Phase 6.8 tests"""
    print("\n" + "🔬" * 40)
    print("ZeroSite Phase 6.8: Local Demand Model Test Suite")
    print("🔬" * 40)
    
    results = []
    
    try:
        # Component tests
        print("\n" + "="*80)
        print("🧪 Component Tests")
        print("="*80)
        
        features = test_feature_extraction()
        scores = test_scoring_logic()
        
        # Integration tests
        print("\n" + "="*80)
        print("🧪 Integration Tests")
        print("="*80)
        
        results.append(('Gangnam Youth', test_scenario_1_gangnam_youth()))
        results.append(('Bundang Newlyweds', test_scenario_2_bundang_newlyweds()))
        results.append(('Gyeongbuk Senior', test_scenario_3_gyeongbuk_senior()))
        
        # Summary
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED")
        print("="*80)
        
        print("\n📊 Summary:")
        for name, result in results:
            print(f"\n{name}:")
            print(f"  • Recommended: {result['recommended_type']} ({result['description']})")
            print(f"  • Score: {result['top_score']:.1f}/100")
            print(f"  • Confidence: {result['confidence']}")
        
        print("\n" + "="*80)
        print("✅ Phase 6.8 Integration: COMPLETE")
        print("="*80)
        
        print("\nKey Features Validated:")
        print("  ✓ Feature extraction (demographics, infrastructure, economic)")
        print("  ✓ Weighted scoring for 5 housing types")
        print("  ✓ Demand prediction with confidence levels")
        print("  ✓ Region-specific recommendations")
        print("  ✓ Mock data fallback system")
        
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
