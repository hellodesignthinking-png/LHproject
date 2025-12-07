"""
ZeroSite Phase 6.8: Demand Feature Engineer

Extracts and processes features for local demand prediction.

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DemandFeatureEngineer:
    """
    Feature extraction and engineering for demand prediction
    
    Extracts features from:
    - Address and coordinates
    - Demographics (age, family structure)
    - Infrastructure (schools, hospitals, facilities)
    - Economic indicators (income, rent burden)
    - Competition (supply, vacancy)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize feature engineer with configuration
        
        Args:
            config_path: Path to demand_parameters.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent.parent / "config" / "demand_model" / "demand_parameters.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.feature_ranges = self.config['feature_ranges']
        self.mock_data = self.config['mock_data']
        self.use_mock = self.mock_data.get('enabled', True)
        
        logger.info(f"✅ DemandFeatureEngineer initialized (mock_mode={self.use_mock})")
    
    def extract(
        self,
        address: str,
        coordinates: Tuple[float, float],
        housing_type: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Extract all features for demand prediction
        
        Args:
            address: Full address string
            coordinates: (latitude, longitude)
            housing_type: Optional housing type hint
        
        Returns:
            Dictionary of feature_name -> feature_value
        
        Example:
            >>> features = engineer.extract("서울특별시 강남구", (37.5, 127.0))
            >>> print(features['age_20_34_ratio'])
            0.35
        """
        logger.info(f"🔧 Extracting features for: {address}")
        
        # Determine region from address for mock data lookup
        region = self._extract_region(address)
        
        if self.use_mock:
            features = self._extract_mock_features(region, housing_type)
        else:
            features = self._extract_real_features(address, coordinates, housing_type)
        
        logger.info(f"✅ Extracted {len(features)} features")
        return features
    
    def _extract_region(self, address: str) -> str:
        """Extract region code from address for mock data lookup"""
        address_lower = address.lower()
        
        # Gangnam area
        if any(kw in address_lower for kw in ['강남', '서초', '송파', 'gangnam']):
            return 'gangnam'
        
        # Bundang area
        if any(kw in address_lower for kw in ['분당', '판교', '수지', 'bundang']):
            return 'bundang'
        
        # Gyeongbuk area
        if any(kw in address_lower for kw in ['경북', '경상북도', 'gyeongbuk']):
            return 'gyeongbuk'
        
        # Default to gangnam for unknown regions
        return 'gangnam'
    
    def _extract_mock_features(
        self,
        region: str,
        housing_type: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Extract features from mock data
        
        Args:
            region: Region code (gangnam, bundang, gyeongbuk)
            housing_type: Optional housing type hint
        
        Returns:
            Feature dictionary with mock values
        """
        regions = self.mock_data.get('regions', {})
        region_data = regions.get(region, regions.get('gangnam', {}))
        
        # Fill missing features with defaults (conservative approach)
        all_features = {}
        for feature_name in self.feature_ranges.keys():
            if feature_name in region_data:
                all_features[feature_name] = region_data[feature_name]
            else:
                # Default to mid-range or zero based on feature type
                feature_config = self.feature_ranges[feature_name]
                if feature_config.get('inverse', False):
                    # For inverse features (lower is better), default to mid-high
                    all_features[feature_name] = (feature_config['min'] + feature_config['max']) * 0.6
                else:
                    # For normal features, default to mid-low
                    all_features[feature_name] = (feature_config['min'] + feature_config['max']) * 0.4
        
        logger.info(f"📊 Mock features extracted for region: {region}")
        return all_features
    
    def _extract_real_features(
        self,
        address: str,
        coordinates: Tuple[float, float],
        housing_type: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Extract features from real external APIs
        
        TODO: Implement real API calls to:
        - Statistics Korea (demographics)
        - MOLIT (housing data)
        - Seoul Open Data (facilities)
        - KOSIS (economic data)
        
        For now, falls back to mock data
        """
        logger.warning("⚠️ Real API extraction not implemented, falling back to mock data")
        region = self._extract_region(address)
        return self._extract_mock_features(region, housing_type)
    
    def normalize_feature(
        self,
        feature_name: str,
        value: float
    ) -> float:
        """
        Normalize feature value to 0-1 range
        
        Args:
            feature_name: Name of feature
            value: Raw feature value
        
        Returns:
            Normalized value in [0, 1]
        
        Example:
            >>> engineer.normalize_feature('age_20_34_ratio', 0.35)
            0.875  # (0.35 - 0.0) / (0.40 - 0.0)
        """
        if feature_name not in self.feature_ranges:
            logger.warning(f"Unknown feature: {feature_name}, returning 0.5")
            return 0.5
        
        config = self.feature_ranges[feature_name]
        min_val = config['min']
        max_val = config['max']
        
        # Clip to range
        value = max(min_val, min(max_val, value))
        
        # Normalize to [0, 1]
        if max_val == min_val:
            normalized = 0.5
        else:
            normalized = (value - min_val) / (max_val - min_val)
        
        # Invert if inverse feature (lower is better)
        if config.get('inverse', False):
            normalized = 1.0 - normalized
        
        return normalized
    
    def get_feature_description(self, feature_name: str) -> str:
        """Get human-readable description of feature"""
        if feature_name in self.feature_ranges:
            return self.feature_ranges[feature_name].get('description', feature_name)
        return feature_name


# Convenience function
def extract_demand_features(
    address: str,
    coordinates: Tuple[float, float],
    housing_type: Optional[str] = None
) -> Dict[str, float]:
    """
    Convenience function to extract demand features
    
    Args:
        address: Full address string
        coordinates: (latitude, longitude)
        housing_type: Optional housing type hint
    
    Returns:
        Dictionary of features
    """
    engineer = DemandFeatureEngineer()
    return engineer.extract(address, coordinates, housing_type)
