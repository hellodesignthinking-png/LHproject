"""
ZeroSite v24 - Base Engine Class

Base class for all ZeroSite v24 engines providing common functionality.

Author: ZeroSite Development Team
Version: 24.0.0
Date: 2025-12-12
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseEngine(ABC):
    """Base class for all ZeroSite v24 engines."""
    
    def __init__(self, engine_name: str, version: str = "24.0.0"):
        """
        Initialize base engine.
        
        Args:
            engine_name: Name of the engine
            version: Version of the engine
        """
        self.engine_name = engine_name
        self.version = version
        self.created_at = datetime.now()
        self.logger = logging.getLogger(f"zerosite.engines.{engine_name}")
        
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        
        Args:
            input_data: Dictionary containing input parameters
            
        Returns:
            Dictionary containing processing results
        """
        pass
    
    def validate_input(self, input_data: Dict[str, Any], required_fields: list) -> bool:
        """
        Validate that all required fields are present in input data.
        
        Args:
            input_data: Dictionary containing input parameters
            required_fields: List of required field names
            
        Returns:
            True if all required fields are present, False otherwise
        """
        missing_fields = [field for field in required_fields if field not in input_data]
        
        if missing_fields:
            self.logger.error(f"Missing required fields: {missing_fields}")
            return False
        
        return True
    
    def create_result(self, 
                     success: bool, 
                     data: Optional[Dict[str, Any]] = None, 
                     error: Optional[str] = None) -> Dict[str, Any]:
        """
        Create standardized result dictionary.
        
        Args:
            success: Whether the operation was successful
            data: Result data dictionary
            error: Error message if operation failed
            
        Returns:
            Standardized result dictionary
        """
        result = {
            "engine": self.engine_name,
            "version": self.version,
            "success": success,
            "timestamp": datetime.now().isoformat(),
        }
        
        if data is not None:
            result["data"] = data
        
        if error is not None:
            result["error"] = error
        
        return result
    
    def log_processing(self, input_data: Dict[str, Any]) -> None:
        """
        Log processing information.
        
        Args:
            input_data: Dictionary containing input parameters
        """
        self.logger.info(
            f"Processing with {self.engine_name} v{self.version} - "
            f"Input keys: {list(input_data.keys())}"
        )
    
    def __repr__(self) -> str:
        """String representation of the engine."""
        return f"{self.engine_name} v{self.version}"
