"""
ZeroSite Phase 6.8: Demand Scorer

Calculates demand scores for each housing type based on weighted features.

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from .demand_feature_engineer import DemandFeatureEngineer

logger = logging.getLogger(__name__)


class DemandScorer:
    """
    Scoring engine for housing type demand prediction
    
    Calculates weighted scores for each housing type:
    - Youth (청년형)
    - Newlyweds (신혼부부형)
    - Newlyweds Growth (신혼 성장형)
    - Multi-Child (다자녀형)
    - Senior (고령자형)
    """
    
    def __init__(self, weights_path: Optional[str] = None, params_path: Optional[str] = None):
        """
        Initialize scorer with weights and parameters
        
        Args:
            weights_path: Path to demand_weights.json
            params_path: Path to demand_parameters.json
        """
        if weights_path is None:
            weights_path = Path(__file__).parent.parent.parent.parent / "config" / "demand_model" / "demand_weights.json"
        
        with open(weights_path, 'r', encoding='utf-8') as f:
            self.weights_config = json.load(f)
        
        self.housing_types = self.weights_config['housing_types']
        self.feature_engineer = DemandFeatureEngineer(params_path)
        
        logger.info(f"✅ DemandScorer initialized with {len(self.housing_types)} housing types")
    
    def score(
        self,
        features: Dict[str, float],
        housing_type: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Calculate demand scores for all or specific housing types
        
        Args:
            features: Dictionary of feature_name -> feature_value
            housing_type: Optional specific housing type to score
        
        Returns:
            Dictionary of housing_type -> score (0-100)
        
        Example:
            >>> features = {'age_20_34_ratio': 0.35, 'commute_time': 35, ...}
            >>> scores = scorer.score(features)
            >>> print(scores)
            {'youth': 78.5, 'newlyweds': 62.3, ...}
        """
        scores = {}
        
        if housing_type and housing_type in self.housing_types:
            # Score only specific housing type
            housing_types_to_score = {housing_type: self.housing_types[housing_type]}
        else:
            # Score all housing types
            housing_types_to_score = self.housing_types
        
        for type_name, type_config in housing_types_to_score.items():
            score = self._calculate_type_score(features, type_name, type_config)
            scores[type_name] = score
            logger.info(f"  {type_name}: {score:.1f}/100")
        
        return scores
    
    def _calculate_type_score(
        self,
        features: Dict[str, float],
        type_name: str,
        type_config: Dict[str, Any]
    ) -> float:
        """
        Calculate score for a specific housing type
        
        Formula:
            score = Σ (weight_i × normalized_feature_i) × 100
        
        Args:
            features: Raw feature values
            type_name: Housing type name
            type_config: Configuration for this housing type
        
        Returns:
            Score in range [0, 100]
        """
        weights = type_config['weights']
        total_score = 0.0
        
        for feature_name, weight in weights.items():
            if feature_name not in features:
                logger.warning(f"Missing feature '{feature_name}' for {type_name}, using 0")
                normalized = 0.0
            else:
                # Normalize feature to [0, 1]
                raw_value = features[feature_name]
                normalized = self.feature_engineer.normalize_feature(feature_name, raw_value)
            
            # Apply weight
            weighted_score = weight * normalized
            total_score += weighted_score
        
        # Convert to 0-100 scale
        final_score = total_score * 100
        
        # Ensure score is in valid range
        final_score = max(0.0, min(100.0, final_score))
        
        return round(final_score, 1)
    
    def get_recommended_type(
        self,
        scores: Dict[str, float],
        min_threshold: float = 50.0
    ) -> Optional[str]:
        """
        Get recommended housing type based on scores
        
        Args:
            scores: Dictionary of housing_type -> score
            min_threshold: Minimum score threshold
        
        Returns:
            Recommended housing type or None if all below threshold
        
        Example:
            >>> scores = {'youth': 78.5, 'newlyweds': 62.3, ...}
            >>> recommended = scorer.get_recommended_type(scores)
            >>> print(recommended)
            'youth'
        """
        # Filter by threshold
        viable_types = {k: v for k, v in scores.items() if v >= min_threshold}
        
        if not viable_types:
            logger.warning(f"No housing types meet threshold {min_threshold}, returning highest score")
            viable_types = scores
        
        # Get type with highest score
        recommended = max(viable_types, key=viable_types.get)
        
        logger.info(f"🎯 Recommended type: {recommended} (score: {scores[recommended]:.1f})")
        return recommended
    
    def get_type_description(self, housing_type: str) -> str:
        """Get Korean description of housing type"""
        if housing_type in self.housing_types:
            return self.housing_types[housing_type].get('description', housing_type)
        return housing_type
    
    def get_score_breakdown(
        self,
        features: Dict[str, float],
        housing_type: str
    ) -> Dict[str, Dict[str, float]]:
        """
        Get detailed breakdown of score components
        
        Args:
            features: Feature values
            housing_type: Housing type to analyze
        
        Returns:
            Dictionary with feature contributions
        
        Example:
            >>> breakdown = scorer.get_score_breakdown(features, 'youth')
            >>> print(breakdown['age_20_34_ratio'])
            {'raw': 0.35, 'normalized': 0.875, 'weight': 0.25, 'contribution': 21.875}
        """
        if housing_type not in self.housing_types:
            return {}
        
        type_config = self.housing_types[housing_type]
        weights = type_config['weights']
        breakdown = {}
        
        for feature_name, weight in weights.items():
            raw_value = features.get(feature_name, 0.0)
            normalized = self.feature_engineer.normalize_feature(feature_name, raw_value)
            contribution = weight * normalized * 100
            
            breakdown[feature_name] = {
                'raw': raw_value,
                'normalized': normalized,
                'weight': weight,
                'contribution': round(contribution, 2)
            }
        
        return breakdown


# Convenience function
def score_demand(
    features: Dict[str, float],
    housing_type: Optional[str] = None
) -> Dict[str, float]:
    """
    Convenience function to score demand
    
    Args:
        features: Feature dictionary
        housing_type: Optional specific housing type
    
    Returns:
        Dictionary of housing_type -> score
    """
    scorer = DemandScorer()
    return scorer.score(features, housing_type)
