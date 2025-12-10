"""
Comprehensive Integration Tests for Land Report API v3

Tests all endpoints of the Land Report API including:
- POST /api/v3/land-report (report generation)
- GET /api/v3/land-report/{report_id} (cached report retrieval)
- POST /api/v3/land-report/compare (enhanced vs legacy comparison)
- GET /api/v3/health (health check)

Author: ZeroSite Development Team + GenSpark AI
Date: 2025-12-10
Version: v3.0
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ==================== TEST DATA ====================

VALID_REQUEST_DATA = {
    "address": "서울특별시 강남구 역삼동 123-45",
    "land_size_sqm": 1000.0,
    "zone_type": "제2종일반주거지역",
    "asking_price": 10000000000,
    "generate_pdf": False
}

VALID_REQUEST_DATA_2 = {
    "address": "서울특별시 서초구 서초동 100-5",
    "land_size_sqm": 500.0,
    "zone_type": "제1종일반주거지역",
    "asking_price": 5000000000
}

# ==================== HEALTH CHECK TESTS ====================

def test_health_endpoint():
    """Test Land Report API health check"""
    response = client.get("/api/v3/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["api_version"] == "v3.0"
    assert "engine" in data
    assert "cache" in data
    assert "features" in data
    
    # Check engine status
    engine_data = data["engine"]
    assert engine_data["name"] == "Land Valuation Engine v9.1"
    assert engine_data["enhanced_services"] is True
    
    # Check features
    expected_features = [
        "Dynamic Transaction Generation",
        "4-Factor Price Adjustment",
        "Advanced Confidence Scoring",
        "Financial Analysis",
        "Negotiation Strategies"
    ]
    for feature in expected_features:
        assert feature in data["features"]
    
    print("✅ Health check test passed")


# ==================== REPORT GENERATION TESTS ====================

def test_generate_land_report_basic():
    """Test basic land report generation"""
    response = client.post("/api/v3/land-report", json=VALID_REQUEST_DATA)
    assert response.status_code == 200
    
    data = response.json()
    
    # Check response structure
    assert "report_id" in data
    assert "timestamp" in data
    assert "input" in data
    assert "valuation" in data
    assert "financial" in data
    assert "negotiation" in data
    assert "recommendation" in data
    assert "comparables" in data
    
    # Check report_id format
    assert data["report_id"].startswith("rpt_")
    
    # Check input data
    input_data = data["input"]
    assert input_data["address"] == VALID_REQUEST_DATA["address"]
    assert input_data["land_size_sqm"] == VALID_REQUEST_DATA["land_size_sqm"]
    
    # Check valuation results
    valuation = data["valuation"]
    assert valuation["estimated_price_krw"] > 0
    assert valuation["price_per_sqm_krw"] > 0
    assert 0 <= valuation["confidence_score"] <= 1
    assert valuation["confidence_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert valuation["transaction_count"] > 0
    
    # Check price range
    price_range = valuation["price_range"]
    assert price_range["low"] > 0
    assert price_range["avg"] > 0
    assert price_range["high"] > 0
    assert price_range["low"] < price_range["avg"] < price_range["high"]
    
    # Check coordinates
    coordinate = valuation["coordinate"]
    assert "lat" in coordinate
    assert "lng" in coordinate
    
    # Check enhanced features
    enhanced = valuation["enhanced_features"]
    assert enhanced["dynamic_transactions"] is True
    assert enhanced["weighted_adjustments"] is True
    assert enhanced["advanced_confidence"] is True
    
    # Check comparables
    comparables = data["comparables"]
    assert len(comparables) > 0
    assert len(comparables) <= 5  # Should return top 5
    
    print(f"✅ Basic report generation test passed")
    print(f"   ├─ Report ID: {data['report_id']}")
    print(f"   ├─ Estimated Price: ₩{valuation['estimated_price_krw']:,.0f}")
    print(f"   ├─ Confidence: {valuation['confidence_score']:.1%}")
    print(f"   └─ Transactions: {valuation['transaction_count']}")
    
    return data["report_id"]


def test_generate_land_report_different_zone():
    """Test land report generation with different zone type"""
    response = client.post("/api/v3/land-report", json=VALID_REQUEST_DATA_2)
    assert response.status_code == 200
    
    data = response.json()
    assert data["input"]["zone_type"] == "제1종일반주거지역"
    assert data["valuation"]["estimated_price_krw"] > 0
    
    print("✅ Different zone test passed")


def test_generate_land_report_no_asking_price():
    """Test land report generation without asking price"""
    request_data = {
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_size_sqm": 1000.0,
        "zone_type": "제2종일반주거지역"
    }
    response = client.post("/api/v3/land-report", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["input"]["asking_price"] is None
    assert data["valuation"]["estimated_price_krw"] > 0
    
    print("✅ No asking price test passed")


# ==================== REPORT RETRIEVAL TESTS ====================

def test_get_cached_report():
    """Test cached report retrieval"""
    # First generate a report
    gen_response = client.post("/api/v3/land-report", json=VALID_REQUEST_DATA)
    assert gen_response.status_code == 200
    report_id = gen_response.json()["report_id"]
    
    # Then retrieve it
    get_response = client.get(f"/api/v3/land-report/{report_id}")
    assert get_response.status_code == 200
    
    cached_data = get_response.json()
    assert cached_data["report_id"] == report_id
    assert "valuation" in cached_data
    
    print(f"✅ Cached report retrieval test passed (ID: {report_id})")


def test_get_nonexistent_report():
    """Test retrieval of non-existent report"""
    fake_id = "rpt_19990101_fakeid"
    response = client.get(f"/api/v3/land-report/{fake_id}")
    assert response.status_code == 404
    
    error_data = response.json()
    assert "not found" in error_data["detail"].lower()
    
    print("✅ Non-existent report test passed")


# ==================== COMPARISON MODE TESTS ====================

def test_compare_valuation_modes():
    """Test enhanced vs legacy comparison"""
    response = client.post("/api/v3/land-report/compare", json=VALID_REQUEST_DATA)
    assert response.status_code == 200
    
    data = response.json()
    
    # Check response structure
    assert "report_id" in data
    assert "timestamp" in data
    assert "enhanced_result" in data
    assert "legacy_result" in data
    assert "comparison" in data
    
    # Check comparison data
    comparison = data["comparison"]
    assert "price_difference_krw" in comparison
    assert "price_difference_pct" in comparison
    assert "confidence_improvement" in comparison
    assert "enhanced_features" in comparison
    
    # Verify enhanced features list
    assert len(comparison["enhanced_features"]) > 0
    assert "Dynamic Transaction Generation" in comparison["enhanced_features"]
    
    print("✅ Comparison mode test passed")
    print(f"   ├─ Price Diff: ₩{comparison['price_difference_krw']:,.0f}")
    print(f"   ├─ Price Diff %: {comparison['price_difference_pct']:.2f}%")
    print(f"   └─ Confidence Improvement: +{comparison['confidence_improvement']:.2f}%")


# ==================== VALIDATION TESTS ====================

def test_invalid_land_size():
    """Test validation with invalid land size"""
    invalid_request = {
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_size_sqm": -100,  # Invalid: negative
        "zone_type": "제2종일반주거지역"
    }
    response = client.post("/api/v3/land-report", json=invalid_request)
    assert response.status_code == 422  # Validation error
    
    print("✅ Invalid land size validation test passed")


def test_missing_required_field():
    """Test validation with missing required field"""
    invalid_request = {
        "land_size_sqm": 1000.0,
        "zone_type": "제2종일반주거지역"
        # Missing address
    }
    response = client.post("/api/v3/land-report", json=invalid_request)
    assert response.status_code == 422  # Validation error
    
    print("✅ Missing field validation test passed")


# ==================== PERFORMANCE TESTS ====================

def test_response_time():
    """Test API response time"""
    import time
    
    start_time = time.time()
    response = client.post("/api/v3/land-report", json=VALID_REQUEST_DATA)
    end_time = time.time()
    
    assert response.status_code == 200
    
    response_time = end_time - start_time
    assert response_time < 5.0  # Should respond within 5 seconds
    
    print(f"✅ Response time test passed ({response_time:.2f}s)")


def test_concurrent_requests():
    """Test handling of multiple concurrent requests"""
    import concurrent.futures
    
    def make_request(request_data):
        return client.post("/api/v3/land-report", json=request_data)
    
    # Prepare different requests
    requests = [VALID_REQUEST_DATA, VALID_REQUEST_DATA_2, VALID_REQUEST_DATA]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(make_request, req) for req in requests]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    # All requests should succeed
    for result in results:
        assert result.status_code == 200
    
    print(f"✅ Concurrent requests test passed ({len(results)} requests)")


# ==================== CONFIDENCE SCORING TESTS ====================

def test_confidence_levels():
    """Test confidence level categorization"""
    response = client.post("/api/v3/land-report", json=VALID_REQUEST_DATA)
    assert response.status_code == 200
    
    data = response.json()
    confidence_score = data["valuation"]["confidence_score"]
    confidence_level = data["valuation"]["confidence_level"]
    
    # Verify level matches score
    if confidence_score >= 0.8:
        assert confidence_level == "HIGH"
    elif confidence_score >= 0.6:
        assert confidence_level in ["MEDIUM", "HIGH"]
    else:
        assert confidence_level in ["LOW", "MEDIUM"]
    
    print(f"✅ Confidence level test passed ({confidence_score:.1%} = {confidence_level})")


# ==================== RUN ALL TESTS ====================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 Land Report API v3 - Comprehensive Test Suite")
    print("="*60 + "\n")
    
    # Health check tests
    print("📋 Health Check Tests:")
    test_health_endpoint()
    print()
    
    # Report generation tests
    print("📊 Report Generation Tests:")
    test_generate_land_report_basic()
    test_generate_land_report_different_zone()
    test_generate_land_report_no_asking_price()
    print()
    
    # Report retrieval tests
    print("💾 Report Retrieval Tests:")
    test_get_cached_report()
    test_get_nonexistent_report()
    print()
    
    # Comparison mode tests
    print("🔬 Comparison Mode Tests:")
    test_compare_valuation_modes()
    print()
    
    # Validation tests
    print("✅ Validation Tests:")
    test_invalid_land_size()
    test_missing_required_field()
    print()
    
    # Performance tests
    print("⚡ Performance Tests:")
    test_response_time()
    test_concurrent_requests()
    print()
    
    # Confidence scoring tests
    print("🎯 Confidence Scoring Tests:")
    test_confidence_levels()
    print()
    
    print("="*60)
    print("✅ ALL TESTS PASSED - API v3 FULLY OPERATIONAL")
    print("="*60)
