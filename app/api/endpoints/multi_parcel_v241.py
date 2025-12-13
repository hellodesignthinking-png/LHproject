"""
ZeroSite v24.1 - Multi-Parcel Optimization API
FastAPI endpoints for multi-parcel analysis

Author: ZeroSite Development Team
Version: v24.1.0
Created: 2025-12-12
"""

from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.engines.multi_parcel_optimizer_v241 import MultiParcelOptimizerV241
from app.engines.multi_parcel_optimizer import ParcelData

router = APIRouter(
    prefix="/api/v24.1/multi-parcel",
    tags=["multi-parcel-v24.1"]
)


# Request/Response Models

class ParcelInput(BaseModel):
    """Single parcel input data"""
    id: str = Field(..., description="Parcel unique identifier")
    area_sqm: float = Field(..., gt=0, description="Parcel area in square meters")
    max_far: float = Field(..., ge=0, le=1000, description="Maximum FAR allowed (%)")
    price_per_sqm: float = Field(..., gt=0, description="Price per square meter (KRW)")
    shape_regularity: float = Field(default=0.7, ge=0, le=1, description="Shape regularity score (0-1)")
    accessibility_score: float = Field(default=0.7, ge=0, le=1, description="Accessibility score (0-1)")
    development_difficulty: float = Field(default=0.3, ge=0, le=1, description="Development difficulty (0-1)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "parcel_001",
                "area_sqm": 500.0,
                "max_far": 200.0,
                "price_per_sqm": 3000000,
                "shape_regularity": 0.8,
                "accessibility_score": 0.9,
                "development_difficulty": 0.2
            }
        }


class MultiParcelOptimizeRequest(BaseModel):
    """Multi-parcel optimization request"""
    parcels: List[ParcelInput] = Field(..., min_length=2, max_length=50, description="List of parcels to analyze")
    target_area_min: float = Field(default=500.0, gt=0, description="Minimum target combined area (sqm)")
    max_parcels_in_combination: int = Field(default=5, ge=2, le=10, description="Maximum parcels in combination")
    
    class Config:
        json_schema_extra = {
            "example": {
                "parcels": [
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
                    }
                ],
                "target_area_min": 1000.0,
                "max_parcels_in_combination": 3
            }
        }


class CombinationScore(BaseModel):
    """Combination scoring result"""
    area_score: float
    far_score: float
    cost_score: float
    shape_score: float
    synergy_score: float
    total_score: float


class ParcelCombinationResult(BaseModel):
    """Single combination result"""
    parcel_ids: List[str]
    total_area: float
    combined_far: float
    total_cost: float
    average_price_per_sqm: float
    scores: CombinationScore
    rank: int


class MultiParcelOptimizeResponse(BaseModel):
    """Multi-parcel optimization response"""
    success: bool
    message: str
    total_parcels: int
    total_combinations_evaluated: int
    optimal_combination: ParcelCombinationResult
    top_10_combinations: List[ParcelCombinationResult]
    pareto_optimal_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Optimization completed successfully",
                "total_parcels": 5,
                "total_combinations_evaluated": 25,
                "optimal_combination": {
                    "parcel_ids": ["parcel_001", "parcel_002"],
                    "total_area": 1100.0,
                    "combined_far": 225.0,
                    "total_cost": 3650000000,
                    "average_price_per_sqm": 3318181.82,
                    "scores": {
                        "area_score": 0.85,
                        "far_score": 0.90,
                        "cost_score": 0.75,
                        "shape_score": 0.80,
                        "synergy_score": 0.88,
                        "total_score": 0.836
                    },
                    "rank": 1
                },
                "top_10_combinations": [],
                "pareto_optimal_count": 3
            }
        }


class ParetoVisualizationRequest(BaseModel):
    """Pareto front visualization request"""
    parcels: List[ParcelInput]
    target_area_min: float = Field(default=500.0, gt=0)
    max_parcels_in_combination: int = Field(default=5, ge=2, le=10)
    view_type: str = Field(default="2d", description="Visualization type: '2d' or '3d'")


class ParetoVisualizationResponse(BaseModel):
    """Pareto front visualization response"""
    success: bool
    message: str
    image_base64: str = Field(..., description="Base64-encoded PNG image")
    pareto_optimal_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Pareto front visualization generated",
                "image_base64": "iVBORw0KGgoAAAANSUhEUgA...",
                "pareto_optimal_count": 5
            }
        }


class SynergyHeatmapRequest(BaseModel):
    """Synergy heatmap request"""
    parcels: List[ParcelInput]


class SynergyHeatmapResponse(BaseModel):
    """Synergy heatmap response"""
    success: bool
    message: str
    image_base64: str = Field(..., description="Base64-encoded PNG heatmap image")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Synergy heatmap generated",
                "image_base64": "iVBORw0KGgoAAAANSUhEUgA..."
            }
        }


# API Endpoints

@router.post("/optimize", response_model=MultiParcelOptimizeResponse)
async def optimize_parcels(request: MultiParcelOptimizeRequest):
    """
    Optimize multi-parcel combinations
    
    Analyzes all possible parcel combinations and returns the optimal set
    based on multi-criteria scoring (area, FAR, cost, shape, synergy).
    
    Args:
        request: Multi-parcel optimization request with parcel data
        
    Returns:
        Optimization results with optimal combination and top 10 alternatives
        
    Raises:
        HTTPException: If optimization fails
    """
    try:
        # Convert input parcels to ParcelData objects
        parcels = [
            ParcelData(
                id=p.id,
                area_sqm=p.area_sqm,
                max_far=p.max_far,
                price_per_sqm=p.price_per_sqm,
                shape_regularity=p.shape_regularity,
                accessibility_score=p.accessibility_score,
                development_difficulty=p.development_difficulty
            )
            for p in request.parcels
        ]
        
        # Initialize optimizer
        optimizer = MultiParcelOptimizerV241(
            max_parcels=request.max_parcels_in_combination,
            target_area_min=request.target_area_min
        )
        
        # Run optimization
        result = optimizer.optimize(parcels)
        
        # Convert result to response format
        optimal = result.optimal_combination
        optimal_result = ParcelCombinationResult(
            parcel_ids=optimal.parcel_ids,
            total_area=optimal.total_area,
            combined_far=optimal.combined_far,
            total_cost=optimal.total_cost,
            average_price_per_sqm=optimal.average_price_per_sqm,
            scores=CombinationScore(
                area_score=optimal.scores.area_score,
                far_score=optimal.scores.far_score,
                cost_score=optimal.scores.cost_score,
                shape_score=optimal.scores.shape_score,
                synergy_score=optimal.scores.synergy_score,
                total_score=optimal.scores.total_score
            ),
            rank=1
        )
        
        # Top 10 combinations
        top_10 = [
            ParcelCombinationResult(
                parcel_ids=combo.parcel_ids,
                total_area=combo.total_area,
                combined_far=combo.combined_far,
                total_cost=combo.total_cost,
                average_price_per_sqm=combo.average_price_per_sqm,
                scores=CombinationScore(
                    area_score=combo.scores.area_score,
                    far_score=combo.scores.far_score,
                    cost_score=combo.scores.cost_score,
                    shape_score=combo.scores.shape_score,
                    synergy_score=combo.scores.synergy_score,
                    total_score=combo.scores.total_score
                ),
                rank=i+2
            )
            for i, combo in enumerate(result.top_combinations[:10])
        ]
        
        return MultiParcelOptimizeResponse(
            success=True,
            message="Optimization completed successfully",
            total_parcels=len(request.parcels),
            total_combinations_evaluated=result.total_combinations_evaluated,
            optimal_combination=optimal_result,
            top_10_combinations=top_10,
            pareto_optimal_count=len(result.pareto_optimal_set)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization failed: {str(e)}"
        )


@router.post("/pareto", response_model=ParetoVisualizationResponse)
async def generate_pareto_front(request: ParetoVisualizationRequest):
    """
    Generate Pareto front visualization
    
    Creates a 2D or 3D scatter plot showing Pareto-optimal combinations
    based on Total Cost, Combined FAR, and Synergy Score.
    
    Args:
        request: Pareto visualization request
        
    Returns:
        Base64-encoded PNG image of Pareto front
        
    Raises:
        HTTPException: If visualization generation fails
    """
    try:
        # Convert input parcels
        parcels = [
            ParcelData(
                id=p.id,
                area_sqm=p.area_sqm,
                max_far=p.max_far,
                price_per_sqm=p.price_per_sqm,
                shape_regularity=p.shape_regularity,
                accessibility_score=p.accessibility_score,
                development_difficulty=p.development_difficulty
            )
            for p in request.parcels
        ]
        
        # Initialize optimizer
        optimizer = MultiParcelOptimizerV241(
            max_parcels=request.max_parcels_in_combination,
            target_area_min=request.target_area_min
        )
        
        # Generate Pareto front visualization
        image_base64 = optimizer.visualize_pareto_front(
            parcels,
            view_type=request.view_type
        )
        
        # Get result for Pareto count
        result = optimizer.optimize(parcels)
        
        return ParetoVisualizationResponse(
            success=True,
            message="Pareto front visualization generated successfully",
            image_base64=image_base64,
            pareto_optimal_count=len(result.pareto_optimal_set)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pareto visualization failed: {str(e)}"
        )


@router.post("/heatmap", response_model=SynergyHeatmapResponse)
async def generate_synergy_heatmap(request: SynergyHeatmapRequest):
    """
    Generate synergy heatmap
    
    Creates a heatmap showing synergy scores between all parcel pairs.
    Higher scores indicate better combination potential.
    
    Args:
        request: Synergy heatmap request
        
    Returns:
        Base64-encoded PNG heatmap image
        
    Raises:
        HTTPException: If heatmap generation fails
    """
    try:
        # Convert input parcels
        parcels = [
            ParcelData(
                id=p.id,
                area_sqm=p.area_sqm,
                max_far=p.max_far,
                price_per_sqm=p.price_per_sqm,
                shape_regularity=p.shape_regularity,
                accessibility_score=p.accessibility_score,
                development_difficulty=p.development_difficulty
            )
            for p in request.parcels
        ]
        
        # Initialize optimizer
        optimizer = MultiParcelOptimizerV241()
        
        # Generate synergy heatmap
        image_base64 = optimizer.generate_synergy_heatmap(parcels)
        
        return SynergyHeatmapResponse(
            success=True,
            message="Synergy heatmap generated successfully",
            image_base64=image_base64
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Heatmap generation failed: {str(e)}"
        )


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "multi-parcel-optimizer-v24.1",
        "version": "24.1.0"
    }
