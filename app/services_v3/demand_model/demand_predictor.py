"""
ZeroSite Phase 6.8: Demand Predictor

Main interface for local demand prediction integrating feature extraction and scoring.

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0
"""

from typing import Dict, Any, Tuple, Optional
import logging

from .demand_feature_engineer import DemandFeatureEngineer
from .demand_scorer import DemandScorer

logger = logging.getLogger(__name__)


class DemandPredictor:
    """
    Local demand prediction engine
    
    Predicts housing type demand based on:
    - Demographics
    - Infrastructure
    - Economic indicators
    - Competition
    
    Usage:
        predictor = DemandPredictor()
        result = predictor.predict("서울특별시 강남구", (37.5, 127.0))
        print(result['recommended_type'])  # 'youth'
        print(result['scores'])  # {'youth': 78.5, ...}
    """
    
    def __init__(
        self,
        weights_path: Optional[str] = None,
        params_path: Optional[str] = None
    ):
        """
        Initialize demand predictor
        
        Args:
            weights_path: Path to demand_weights.json
            params_path: Path to demand_parameters.json
        """
        self.feature_engineer = DemandFeatureEngineer(params_path)
        self.scorer = DemandScorer(weights_path, params_path)
        
        logger.info("✅ DemandPredictor initialized")
    
    def predict(
        self,
        address: str,
        coordinates: Tuple[float, float],
        housing_type_hint: Optional[str] = None,
        min_threshold: float = 50.0
    ) -> Dict[str, Any]:
        """
        Predict housing type demand for a location
        
        Args:
            address: Full address string
            coordinates: (latitude, longitude)
            housing_type_hint: Optional hint for housing type (for feature extraction)
            min_threshold: Minimum score threshold for recommendation
        
        Returns:
            Dictionary with:
                - recommended_type: Best housing type
                - scores: All housing type scores
                - features: Extracted features
                - description: Korean description of recommended type
                - confidence: Confidence level (high/medium/low)
        
        Example:
            >>> predictor = DemandPredictor()
            >>> result = predictor.predict("서울특별시 강남구", (37.5, 127.0))
            >>> print(result)
            {
                'recommended_type': 'youth',
                'scores': {'youth': 78.5, 'newlyweds': 62.3, ...},
                'features': {...},
                'description': '청년형 (Youth Housing)',
                'confidence': 'high'
            }
        """
        logger.info(f"🔮 Predicting demand for: {address}")
        
        # Step 1: Extract features
        features = self.feature_engineer.extract(
            address=address,
            coordinates=coordinates,
            housing_type=housing_type_hint
        )
        
        # Step 2: Calculate scores
        scores = self.scorer.score(features, housing_type_hint)
        
        # Step 3: Get recommendation
        recommended_type = self.scorer.get_recommended_type(scores, min_threshold)
        
        # Step 4: Determine confidence
        if recommended_type:
            confidence = self._calculate_confidence(scores, recommended_type)
            description = self.scorer.get_type_description(recommended_type)
        else:
            confidence = 'low'
            description = 'No suitable type found'
        
        result = {
            'recommended_type': recommended_type,
            'scores': scores,
            'features': features,
            'description': description,
            'confidence': confidence,
            'top_score': scores.get(recommended_type, 0.0) if recommended_type else 0.0,
            'score_spread': self._calculate_score_spread(scores)
        }
        
        logger.info(f"✅ Prediction complete: {recommended_type} ({confidence} confidence, {result['top_score']:.1f}/100)")
        
        return result
    
    def _calculate_confidence(
        self,
        scores: Dict[str, float],
        recommended_type: str
    ) -> str:
        """
        Calculate confidence level of recommendation
        
        Confidence levels:
        - high: Score > 70 and 15+ points ahead of second best
        - medium: Score > 60 or 10+ points ahead
        - low: Otherwise
        
        Args:
            scores: All housing type scores
            recommended_type: Recommended housing type
        
        Returns:
            'high', 'medium', or 'low'
        """
        top_score = scores.get(recommended_type, 0.0)
        
        # Get second best score
        other_scores = [v for k, v in scores.items() if k != recommended_type]
        second_best = max(other_scores) if other_scores else 0.0
        
        score_gap = top_score - second_best
        
        if top_score >= 70 and score_gap >= 15:
            return 'high'
        elif top_score >= 60 or score_gap >= 10:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_score_spread(self, scores: Dict[str, float]) -> float:
        """Calculate spread (standard deviation) of scores"""
        if not scores:
            return 0.0
        
        values = list(scores.values())
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std = variance ** 0.5
        
        return round(std, 1)
    
    def get_detailed_analysis(
        self,
        address: str,
        coordinates: Tuple[float, float],
        housing_type: str
    ) -> Dict[str, Any]:
        """
        Get detailed analysis for a specific housing type
        
        Args:
            address: Full address string
            coordinates: (latitude, longitude)
            housing_type: Housing type to analyze
        
        Returns:
            Dictionary with detailed breakdown
        """
        # Extract features
        features = self.feature_engineer.extract(address, coordinates, housing_type)
        
        # Get score breakdown
        breakdown = self.scorer.get_score_breakdown(features, housing_type)
        
        # Calculate total score
        scores = self.scorer.score(features, housing_type)
        
        return {
            'housing_type': housing_type,
            'description': self.scorer.get_type_description(housing_type),
            'total_score': scores.get(housing_type, 0.0),
            'breakdown': breakdown,
            'features': features
        }
    
    def compare_types(
        self,
        address: str,
        coordinates: Tuple[float, float],
        types_to_compare: Optional[list] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare multiple housing types for a location
        
        Args:
            address: Full address string
            coordinates: (latitude, longitude)
            types_to_compare: List of housing types to compare (None = all)
        
        Returns:
            Dictionary of housing_type -> analysis
        """
        features = self.feature_engineer.extract(address, coordinates)
        scores = self.scorer.score(features)
        
        if types_to_compare:
            types_to_analyze = types_to_compare
        else:
            types_to_analyze = list(scores.keys())
        
        comparison = {}
        for housing_type in types_to_analyze:
            if housing_type in scores:
                breakdown = self.scorer.get_score_breakdown(features, housing_type)
                comparison[housing_type] = {
                    'score': scores[housing_type],
                    'description': self.scorer.get_type_description(housing_type),
                    'breakdown': breakdown
                }
        
        return comparison


# Convenience function
def predict_demand(
    address: str,
    coordinates: Tuple[float, float],
    housing_type_hint: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to predict demand
    
    Args:
        address: Full address string
        coordinates: (latitude, longitude)
        housing_type_hint: Optional housing type hint
    
    Returns:
        Prediction result dictionary
    """
    predictor = DemandPredictor()
    return predictor.predict(address, coordinates, housing_type_hint)
