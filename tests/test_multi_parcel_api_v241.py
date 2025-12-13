"""
Tests for Multi-Parcel API v24.1
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import the router
from app.api.endpoints.multi_parcel_v241 import router

# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.fixture
def sample_parcels():
    """Sample parcel data for testing"""
    return [
        {
            "id": "parcel_001",
            "area_sqm": 500.0,
            "max_far": 200.0,
            "price_per_sqm": 3000000,
            "shape_regularity": 0.8,
            "accessibility_score": 0.9,
            "development_difficulty": 0.2
        },
        {
            "id": "parcel_002",
            "area_sqm": 600.0,
            "max_far": 250.0,
            "price_per_sqm": 3500000,
            "shape_regularity": 0.7,
            "accessibility_score": 0.85,
            "development_difficulty": 0.25
        },
        {
            "id": "parcel_003",
            "area_sqm": 450.0,
            "max_far": 180.0,
            "price_per_sqm": 2800000,
            "shape_regularity": 0.75,
            "accessibility_score": 0.8,
            "development_difficulty": 0.3
        }
    ]


class TestMultiParcelAPI:
    """Test Multi-Parcel API endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/v24.1/multi-parcel/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "multi-parcel-optimizer-v24.1"
        assert data["version"] == "24.1.0"
    
    def test_optimize_parcels_success(self, sample_parcels):
        """Test successful parcel optimization"""
        request_data = {
            "parcels": sample_parcels,
            "target_area_min": 1000.0,
            "max_parcels_in_combination": 3
        }
        
        response = client.post("/api/v24.1/multi-parcel/optimize", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert data["success"] is True
        assert "message" in data
        assert data["total_parcels"] == 3
        assert data["total_combinations_evaluated"] > 0
        
        # Check optimal combination
        assert "optimal_combination" in data
        optimal = data["optimal_combination"]
        assert "parcel_ids" in optimal
        assert isinstance(optimal["parcel_ids"], list)
        assert len(optimal["parcel_ids"]) >= 2
        assert optimal["total_area"] >= request_data["target_area_min"]
        
        # Check scores
        assert "scores" in optimal
        scores = optimal["scores"]
        assert 0 <= scores["total_score"] <= 1
        
        # Check top 10 combinations
        assert "top_10_combinations" in data
        assert isinstance(data["top_10_combinations"], list)
    
    def test_optimize_parcels_insufficient_parcels(self):
        """Test with insufficient parcels"""
        request_data = {
            "parcels": [{
                "id": "parcel_001",
                "area_sqm": 500.0,
                "max_far": 200.0,
                "price_per_sqm": 3000000
            }],
            "target_area_min": 500.0,
            "max_parcels_in_combination": 3
        }
        
        response = client.post("/api/v24.1/multi-parcel/optimize", json=request_data)
        
        # Should fail validation (min 2 parcels required)
        assert response.status_code == 422
    
    def test_pareto_visualization_2d(self, sample_parcels):
        """Test 2D Pareto front visualization"""
        request_data = {
            "parcels": sample_parcels,
            "target_area_min": 1000.0,
            "max_parcels_in_combination": 3,
            "view_type": "2d"
        }
        
        response = client.post("/api/v24.1/multi-parcel/pareto", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "image_base64" in data
        assert len(data["image_base64"]) > 0
        assert data["pareto_optimal_count"] >= 0
    
    def test_synergy_heatmap(self, sample_parcels):
        """Test synergy heatmap generation"""
        request_data = {
            "parcels": sample_parcels
        }
        
        response = client.post("/api/v24.1/multi-parcel/heatmap", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "image_base64" in data
        assert len(data["image_base64"]) > 0
    
    def test_optimize_invalid_data(self):
        """Test with invalid parcel data"""
        request_data = {
            "parcels": [
                {
                    "id": "parcel_001",
                    "area_sqm": -100.0,  # Invalid: negative area
                    "max_far": 200.0,
                    "price_per_sqm": 3000000
                },
                {
                    "id": "parcel_002",
                    "area_sqm": 500.0,
                    "max_far": 200.0,
                    "price_per_sqm": 3000000
                }
            ],
            "target_area_min": 500.0
        }
        
        response = client.post("/api/v24.1/multi-parcel/optimize", json=request_data)
        
        # Should fail validation
        assert response.status_code == 422


class TestAPIResponseFormat:
    """Test API response format consistency"""
    
    def test_optimize_response_format(self, sample_parcels):
        """Test optimize endpoint response format"""
        request_data = {
            "parcels": sample_parcels,
            "target_area_min": 1000.0
        }
        
        response = client.post("/api/v24.1/multi-parcel/optimize", json=request_data)
        data = response.json()
        
        # Required fields
        required_fields = [
            "success", "message", "total_parcels",
            "total_combinations_evaluated", "optimal_combination",
            "top_10_combinations", "pareto_optimal_count"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_pareto_response_format(self, sample_parcels):
        """Test Pareto endpoint response format"""
        request_data = {
            "parcels": sample_parcels,
            "view_type": "2d"
        }
        
        response = client.post("/api/v24.1/multi-parcel/pareto", json=request_data)
        data = response.json()
        
        required_fields = ["success", "message", "image_base64", "pareto_optimal_count"]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
