"""
Test API v4.0 Integration
==========================

Tests for 6-MODULE Pipeline API endpoints

Test Coverage:
- Pipeline analysis endpoint
- Report generation endpoint
- Health check endpoint
- Cache management
- Error handling

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestPipelineAPIv4:
    """Test 6-MODULE Pipeline API v4.0"""
    
    def test_health_check(self):
        """Test /api/v4/pipeline/health endpoint"""
        response = client.get("/api/v4/pipeline/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "status" in data
        assert "version" in data
        assert "pipeline_version" in data
        assert "services" in data
        
        # Check version info
        assert data["version"] == "v4.0"
        assert data["pipeline_version"] == "6-MODULE"
        
        # Check services
        services = data["services"]
        assert "pipeline" in services
        assert "m1_land_info" in services
        assert "m2_appraisal" in services
        assert "m3_lh_demand" in services
        assert "m4_capacity" in services
        assert "m5_feasibility" in services
        assert "m6_lh_review" in services
        
        print(f"✅ Health check passed: {data['status']}")
    
    def test_pipeline_analysis(self):
        """Test /api/v4/pipeline/analyze endpoint"""
        request_data = {
            "parcel_id": "1168010100100010001",
            "use_cache": False,
            "metadata": {
                "test": "api_integration"
            }
        }
        
        response = client.post("/api/v4/pipeline/analyze", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "parcel_id" in data
        assert "analysis_id" in data
        assert "status" in data
        assert "execution_time_ms" in data
        assert "modules_executed" in data
        
        # Check status
        assert data["status"] == "success"
        assert data["parcel_id"] == request_data["parcel_id"]
        assert data["modules_executed"] == 6
        
        # Check key outputs
        assert "land_value" in data
        assert "confidence_score" in data
        assert "selected_housing_type" in data
        assert "recommended_units" in data
        assert "npv_public" in data
        assert "lh_decision" in data
        assert "lh_total_score" in data
        
        # Validate data types
        assert isinstance(data["land_value"], (int, float))
        assert isinstance(data["confidence_score"], (int, float))
        assert isinstance(data["recommended_units"], int)
        assert isinstance(data["lh_total_score"], (int, float))
        
        # Check confidence score range
        assert 0 <= data["confidence_score"] <= 1
        
        # Check LH score range
        assert 0 <= data["lh_total_score"] <= 110
        
        print(f"✅ Pipeline analysis completed in {data['execution_time_ms']:.0f}ms")
        print(f"   Land Value: ₩{data['land_value']:,.0f}")
        print(f"   Confidence: {data['confidence_score']:.2f}")
        print(f"   LH Decision: {data['lh_decision']}")
        print(f"   LH Score: {data['lh_total_score']:.1f}/110")
    
    def test_pipeline_analysis_with_cache(self):
        """Test pipeline analysis with caching"""
        parcel_id = "1168010100100010001"
        
        # First request (no cache)
        request_data = {
            "parcel_id": parcel_id,
            "use_cache": False
        }
        
        response1 = client.post("/api/v4/pipeline/analyze", json=request_data)
        assert response1.status_code == 200
        data1 = response1.json()
        time1 = data1["execution_time_ms"]
        
        # Second request (with cache)
        request_data["use_cache"] = True
        
        response2 = client.post("/api/v4/pipeline/analyze", json=request_data)
        assert response2.status_code == 200
        data2 = response2.json()
        time2 = data2["execution_time_ms"]
        
        # Cache should be much faster (0ms vs original time)
        assert time2 == 0  # Cached response
        
        # Results should be identical
        assert data1["land_value"] == data2["land_value"]
        assert data1["confidence_score"] == data2["confidence_score"]
        
        print(f"✅ Caching works: {time1:.0f}ms → {time2:.0f}ms (cached)")
    
    def test_get_cached_results(self):
        """Test /api/v4/pipeline/results/{parcel_id} endpoint"""
        parcel_id = "1168010100100010001"
        
        # First, run analysis to populate cache
        request_data = {"parcel_id": parcel_id, "use_cache": False}
        client.post("/api/v4/pipeline/analyze", json=request_data)
        
        # Then, get cached results
        response = client.get(f"/api/v4/pipeline/results/{parcel_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "parcel_id" in data
        assert "status" in data
        assert "results" in data
        assert data["status"] == "success"
        assert data["parcel_id"] == parcel_id
        
        # Check results structure
        results = data["results"]
        assert "land" in results
        assert "appraisal" in results
        assert "housing_type" in results
        assert "capacity" in results
        assert "feasibility" in results
        assert "lh_review" in results
        
        print(f"✅ Cached results retrieved for {parcel_id}")
    
    def test_get_nonexistent_results(self):
        """Test getting results for non-analyzed parcel"""
        nonexistent_parcel = "0000000000000000000"
        
        response = client.get(f"/api/v4/pipeline/results/{nonexistent_parcel}")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        
        print(f"✅ 404 error correctly returned for non-existent parcel")
    
    def test_comprehensive_report_generation(self):
        """Test /api/v4/pipeline/reports/comprehensive endpoint"""
        parcel_id = "1168010100100010001"
        
        # First, run analysis
        analysis_request = {"parcel_id": parcel_id, "use_cache": False}
        client.post("/api/v4/pipeline/analyze", json=analysis_request)
        
        # Then, generate report
        report_request = {
            "parcel_id": parcel_id,
            "report_type": "comprehensive",
            "output_format": "json",
            "target_audience": "landowner"
        }
        
        response = client.post("/api/v4/pipeline/reports/comprehensive", json=report_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "report_id" in data
        assert "parcel_id" in data
        assert "report_type" in data
        assert "status" in data
        assert "data" in data
        
        assert data["status"] == "success"
        assert data["parcel_id"] == parcel_id
        assert data["report_type"] == "comprehensive"
        
        # Check report data structure
        report_data = data["data"]
        assert "executive_summary" in report_data
        assert "detailed_analysis" in report_data
        
        # Check executive summary
        summary = report_data["executive_summary"]
        assert "land_value" in summary
        assert "confidence_level" in summary
        assert "lh_decision" in summary
        assert "lh_score" in summary
        
        print(f"✅ Comprehensive report generated (ID: {data['report_id']})")
        print(f"   Generation time: {data['generation_time_ms']:.0f}ms")
    
    def test_report_generation_without_analysis(self):
        """Test report generation without prior analysis"""
        nonexistent_parcel = "9999999999999999999"
        
        report_request = {
            "parcel_id": nonexistent_parcel,
            "report_type": "comprehensive",
            "output_format": "json"
        }
        
        response = client.post("/api/v4/pipeline/reports/comprehensive", json=report_request)
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        
        print(f"✅ 404 error correctly returned for report without analysis")
    
    def test_clear_cache_for_parcel(self):
        """Test /api/v4/pipeline/cache/{parcel_id} DELETE endpoint"""
        parcel_id = "1168010100100010001"
        
        # First, run analysis to populate cache
        request_data = {"parcel_id": parcel_id, "use_cache": False}
        client.post("/api/v4/pipeline/analyze", json=request_data)
        
        # Then, clear cache
        response = client.delete(f"/api/v4/pipeline/cache/{parcel_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        print(f"✅ Cache cleared for {parcel_id}")
    
    def test_pipeline_stats(self):
        """Test /api/v4/pipeline/stats endpoint"""
        response = client.get("/api/v4/pipeline/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "cached_results" in data
        assert "parcel_ids" in data
        assert "pipeline_version" in data
        assert "architecture" in data
        
        assert data["pipeline_version"] == "v4.0"
        assert data["architecture"] == "6-MODULE"
        
        print(f"✅ Pipeline stats: {data['cached_results']} cached results")


class TestAPIv4ErrorHandling:
    """Test API error handling"""
    
    def test_invalid_parcel_id_format(self):
        """Test with invalid parcel ID format"""
        # This will still work with mock data, but test the error path
        request_data = {
            "parcel_id": "INVALID"
        }
        
        # Should not crash, may return results or error depending on implementation
        response = client.post("/api/v4/pipeline/analyze", json=request_data)
        
        # Either success or error, but should not be 500
        assert response.status_code in [200, 400, 404]
        
        print(f"✅ Invalid parcel ID handled gracefully: {response.status_code}")
    
    def test_missing_required_fields(self):
        """Test with missing required fields"""
        request_data = {}  # Missing parcel_id
        
        response = client.post("/api/v4/pipeline/analyze", json=request_data)
        
        # Should return 422 (Validation Error)
        assert response.status_code == 422
        
        print(f"✅ Missing field validation works: {response.status_code}")


# Run tests if executed directly
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 Running API v4.0 Integration Tests")
    print("="*80 + "\n")
    
    pytest.main([__file__, "-v", "--tb=short"])
