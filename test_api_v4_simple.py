#!/usr/bin/env python3
"""
Simple API v4.0 Integration Test (No FastAPI dependency)
=========================================================

Direct testing of 6-MODULE Pipeline API endpoints

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.pipeline.zer0site_pipeline import ZeroSitePipeline
from app.api.endpoints.pipeline_reports_v4 import (
    pipeline_result_to_dict,
    generate_analysis_id,
    results_cache
)


def test_pipeline_direct():
    """Test pipeline directly (no HTTP)"""
    print("\n" + "="*80)
    print("🧪 Testing 6-MODULE Pipeline (Direct)")
    print("="*80 + "\n")
    
    # Initialize pipeline
    pipeline = ZeroSitePipeline()
    parcel_id = "1168010100100010001"
    
    # Run pipeline
    print(f"🚀 Running pipeline for parcel: {parcel_id}")
    result = pipeline.run(parcel_id)
    
    # Check results
    assert result.success, "Pipeline should succeed"
    assert result.land is not None, "Land context should exist"
    assert result.appraisal is not None, "Appraisal context should exist"
    assert result.housing_type is not None, "Housing type context should exist"
    assert result.capacity is not None, "Capacity context should exist"
    assert result.feasibility is not None, "Feasibility context should exist"
    assert result.lh_review is not None, "LH review context should exist"
    
    print("\n✅ All contexts created successfully")
    
    # Display key results
    print(f"\n📊 Key Results:")
    print(f"   Land Value: ₩{result.appraisal.land_value:,.0f}")
    print(f"   Confidence: {result.appraisal.confidence_metrics.score:.2f}")
    print(f"   Housing Type: {result.housing_type.selected_type}")
    print(f"   Recommended Units: {result.capacity.unit_plan.recommended_units}")
    print(f"   NPV (Public): ₩{result.feasibility.financial_metrics.npv_public:,.0f}")
    print(f"   LH Decision: {result.lh_review.decision}")
    print(f"   LH Score: {result.lh_review.total_score:.1f}/110")
    
    return result


def test_pipeline_result_conversion():
    """Test pipeline result to dict conversion"""
    print("\n" + "="*80)
    print("🧪 Testing Pipeline Result Conversion")
    print("="*80 + "\n")
    
    # Run pipeline
    pipeline = ZeroSitePipeline()
    result = pipeline.run("1168010100100010001")
    
    # Convert to dict
    result_dict = pipeline_result_to_dict(result)
    
    # Check structure
    assert "land" in result_dict, "Should have land data"
    assert "appraisal" in result_dict, "Should have appraisal data"
    assert "housing_type" in result_dict, "Should have housing_type data"
    assert "capacity" in result_dict, "Should have capacity data"
    assert "feasibility" in result_dict, "Should have feasibility data"
    assert "lh_review" in result_dict, "Should have lh_review data"
    
    print("✅ Result conversion successful")
    print(f"   Keys: {list(result_dict.keys())}")
    
    return result_dict


def test_cache_functionality():
    """Test cache functionality"""
    print("\n" + "="*80)
    print("🧪 Testing Cache Functionality")
    print("="*80 + "\n")
    
    parcel_id = "1168010100100010001"
    pipeline = ZeroSitePipeline()
    
    # Clear cache first
    if parcel_id in results_cache:
        del results_cache[parcel_id]
    
    # Run pipeline and cache
    result1 = pipeline.run(parcel_id)
    results_cache[parcel_id] = result1
    
    print(f"✅ Cached result for {parcel_id}")
    
    # Retrieve from cache
    cached_result = results_cache.get(parcel_id)
    
    assert cached_result is not None, "Should retrieve cached result"
    assert cached_result.appraisal.land_value == result1.appraisal.land_value, \
        "Cached values should match"
    
    print(f"✅ Retrieved cached result")
    print(f"   Cache size: {len(results_cache)}")
    print(f"   Cached parcel IDs: {list(results_cache.keys())}")
    
    return cached_result


def test_analysis_id_generation():
    """Test analysis ID generation"""
    print("\n" + "="*80)
    print("🧪 Testing Analysis ID Generation")
    print("="*80 + "\n")
    
    parcel_id = "1168010100100010001"
    
    # Generate IDs
    id1 = generate_analysis_id(parcel_id)
    id2 = generate_analysis_id(parcel_id)
    
    # Check format
    assert id1.startswith("analysis_"), "ID should start with 'analysis_'"
    assert parcel_id in id1, "ID should contain parcel_id"
    assert id1 != id2, "IDs should be unique"
    
    print(f"✅ Generated unique IDs:")
    print(f"   ID 1: {id1}")
    print(f"   ID 2: {id2}")


def test_immutability_protection():
    """Test that M2 appraisal is protected"""
    print("\n" + "="*80)
    print("🧪 Testing M2 Immutability Protection")
    print("="*80 + "\n")
    
    pipeline = ZeroSitePipeline()
    result = pipeline.run("1168010100100010001")
    
    # Try to modify M2 appraisal (should fail)
    try:
        result.appraisal.land_value = 999999999
        print("❌ FAILED: Should not be able to modify land_value")
        assert False, "Modification should have raised an error"
    except Exception as e:
        print(f"✅ M2 immutability protected: {type(e).__name__}")
        assert "frozen" in str(e).lower() or "immutable" in str(e).lower() or \
               "cannot" in str(e).lower(), "Should be frozen/immutable error"


def run_all_tests():
    """Run all tests"""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "🎯 API v4.0 INTEGRATION TESTS" + " "*29 + "║")
    print("╚" + "="*78 + "╝")
    
    tests = [
        ("Pipeline Direct Execution", test_pipeline_direct),
        ("Pipeline Result Conversion", test_pipeline_result_conversion),
        ("Cache Functionality", test_cache_functionality),
        ("Analysis ID Generation", test_analysis_id_generation),
        ("M2 Immutability Protection", test_immutability_protection),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ Test Failed: {test_name}")
            print(f"   Error: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"\n💥 Test Error: {test_name}")
            print(f"   Error: {type(e).__name__}: {str(e)}")
            failed += 1
    
    # Summary
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"   Total Tests: {total}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   Success Rate: {success_rate:.1f}%")
    print("="*80 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
