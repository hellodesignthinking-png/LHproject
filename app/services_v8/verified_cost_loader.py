"""
ZeroSite Phase 8: Verified Cost Loader

Loads LH official construction cost data from database.

Features:
    - Region-based cost lookup
    - Housing type-based cost variations
    - Year-based cost index
    - Fallback mechanism for missing data
    - Address-to-region mapping

Architecture:
    Mock DB (JSON) → VerifiedCostLoader → Phase 2 Financial Engine
    
    In production:
    LH API → VerifiedCostLoader → Phase 2 Financial Engine
"""

from typing import Optional, Dict, Any
from pathlib import Path
import json
import re


class VerifiedCostData:
    """Verified cost data structure"""
    
    def __init__(
        self,
        cost_per_m2: float,
        year: int,
        region: str,
        housing_type: str,
        source: str = "LH Official",
        description: Optional[str] = None,
        includes: Optional[list] = None
    ):
        self.cost_per_m2 = cost_per_m2
        self.year = year
        self.region = region
        self.housing_type = housing_type
        self.source = source
        self.description = description
        self.includes = includes or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "cost_per_m2": self.cost_per_m2,
            "year": self.year,
            "region": self.region,
            "housing_type": self.housing_type,
            "source": self.source,
            "description": self.description,
            "includes": self.includes
        }


class VerifiedCostLoader:
    """
    Loads verified construction cost from LH database
    
    Two-layer cost model:
        1. Verified Cost (LH Official) - preferred
        2. Estimated Cost (Phase 2) - fallback
    
    Usage:
        loader = VerifiedCostLoader()
        cost_data = loader.get_cost(
            address="서울특별시 강남구",
            housing_type="Youth",
            year=2025
        )
        
        if cost_data:
            capex = cost_data.cost_per_m2 * total_area
    """
    
    def __init__(self, data_path: Path = None):
        """
        Initialize loader
        
        Args:
            data_path: Path to verified cost JSON file
        """
        self.data_path = data_path or Path("./app/data/verified_cost/mock_verified_cost.json")
        self.data = None
        self._load_data()
    
    def _load_data(self):
        """Load verified cost data from JSON"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Verified cost data not found at {self.data_path}")
            self.data = None
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in verified cost data: {e}")
            self.data = None
    
    def _extract_region_from_address(self, address: str) -> Optional[str]:
        """
        Extract region from address string
        
        Examples:
            "서울특별시 강남구" → "seoul"
            "경기도 성남시" → "gyeonggi"
            "인천광역시 부평구" → "incheon"
        
        Args:
            address: Full address string
        
        Returns:
            Region code or None
        """
        if not self.data or "region_mapping" not in self.data:
            return None
        
        # Try direct mapping
        for key, region_code in self.data["region_mapping"].items():
            if key in address:
                return region_code
        
        # Try partial matching
        if "서울" in address:
            return "seoul"
        elif "경기" in address:
            return "gyeonggi"
        elif "인천" in address:
            return "incheon"
        elif "부산" in address:
            return "busan"
        elif "대구" in address:
            return "daegu"
        elif "광주" in address:
            return "gwangju"
        
        return None
    
    def get_cost(
        self,
        address: str,
        housing_type: str,
        year: int = 2025
    ) -> Optional[VerifiedCostData]:
        """
        Get verified cost for given parameters
        
        Args:
            address: Full address (will extract region)
            housing_type: Housing type (Youth, Newlyweds_TypeI, etc.)
            year: Cost year
        
        Returns:
            VerifiedCostData or None if not found
        """
        if not self.data:
            return None
        
        # Check year match
        if self.data.get("year") != year:
            print(f"Warning: Cost data is for year {self.data.get('year')}, requested {year}")
            # Continue anyway - close enough
        
        # Extract region from address
        region_code = self._extract_region_from_address(address)
        if not region_code:
            print(f"Warning: Could not determine region from address: {address}")
            return None
        
        # Get region data
        regions = self.data.get("regions", {})
        if region_code not in regions:
            print(f"Warning: Region '{region_code}' not found in database")
            return None
        
        region_data = regions[region_code]
        
        # Get housing type data
        housing_types = region_data.get("housing_types", {})
        if housing_type not in housing_types:
            print(f"Warning: Housing type '{housing_type}' not found for region '{region_code}'")
            return None
        
        type_data = housing_types[housing_type]
        
        # Create verified cost data
        return VerifiedCostData(
            cost_per_m2=type_data["cost_per_m2"],
            year=year,
            region=region_data["region_name"],
            housing_type=housing_type,
            source="LH Official (Mock)",
            description=type_data.get("description"),
            includes=type_data.get("includes", [])
        )
    
    def get_cost_by_region_code(
        self,
        region_code: str,
        housing_type: str,
        year: int = 2025
    ) -> Optional[VerifiedCostData]:
        """
        Get verified cost by region code directly
        
        Args:
            region_code: Region code (seoul, gyeonggi, etc.)
            housing_type: Housing type
            year: Cost year
        
        Returns:
            VerifiedCostData or None
        """
        if not self.data:
            return None
        
        regions = self.data.get("regions", {})
        if region_code not in regions:
            return None
        
        region_data = regions[region_code]
        housing_types = region_data.get("housing_types", {})
        
        if housing_type not in housing_types:
            return None
        
        type_data = housing_types[housing_type]
        
        return VerifiedCostData(
            cost_per_m2=type_data["cost_per_m2"],
            year=year,
            region=region_data["region_name"],
            housing_type=housing_type,
            source="LH Official (Mock)",
            description=type_data.get("description"),
            includes=type_data.get("includes", [])
        )
    
    def list_available_regions(self) -> list:
        """List all available regions"""
        if not self.data:
            return []
        
        regions = self.data.get("regions", {})
        return [
            {
                "code": code,
                "name": data["region_name"]
            }
            for code, data in regions.items()
        ]
    
    def list_available_housing_types(self, region_code: str) -> list:
        """List available housing types for a region"""
        if not self.data:
            return []
        
        regions = self.data.get("regions", {})
        if region_code not in regions:
            return []
        
        return list(regions[region_code].get("housing_types", {}).keys())
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get summary of available cost data"""
        if not self.data:
            return {"available": False}
        
        return {
            "available": True,
            "version": self.data.get("version"),
            "year": self.data.get("year"),
            "last_updated": self.data.get("last_updated"),
            "source": self.data.get("source"),
            "regions_count": len(self.data.get("regions", {})),
            "regions": self.list_available_regions()
        }


# Convenience functions
def get_verified_cost(
    address: str,
    housing_type: str,
    year: int = 2025
) -> Optional[VerifiedCostData]:
    """
    Convenience function to get verified cost
    
    Usage:
        cost_data = get_verified_cost(
            address="서울특별시 강남구 역삼동 123-45",
            housing_type="Youth"
        )
        
        if cost_data:
            print(f"Cost: {cost_data.cost_per_m2:,}원/㎡")
    """
    loader = VerifiedCostLoader()
    return loader.get_cost(address, housing_type, year)


def has_verified_cost(address: str, housing_type: str) -> bool:
    """Check if verified cost is available"""
    cost_data = get_verified_cost(address, housing_type)
    return cost_data is not None
