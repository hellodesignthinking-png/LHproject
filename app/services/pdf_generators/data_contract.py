"""
ZeroSite PDF Data Contract & Validation System
================================================

Purpose: Ensure data integrity and prevent silent failures (0/None/N/A) 
across M2-M6 PDF generation pipeline.

Author: ZeroSite AI Development Team
Date: 2025-12-19
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    ERROR = "error"  # Block report generation
    WARNING = "warning"  # Generate report but flag issue
    INFO = "info"  # Informational only


@dataclass
class ValidationIssue:
    """Single validation issue"""
    field_path: str
    severity: ValidationSeverity
    message: str
    current_value: Any = None
    expected_type: Optional[type] = None


@dataclass
class ValidationResult:
    """Result of data validation"""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    
    def add_error(self, field_path: str, message: str, current_value: Any = None):
        """Add error-level issue (blocks generation)"""
        self.is_valid = False
        self.issues.append(ValidationIssue(
            field_path=field_path,
            severity=ValidationSeverity.ERROR,
            message=message,
            current_value=current_value
        ))
    
    def add_warning(self, field_path: str, message: str, current_value: Any = None):
        """Add warning-level issue (allows generation with flag)"""
        self.issues.append(ValidationIssue(
            field_path=field_path,
            severity=ValidationSeverity.WARNING,
            message=message,
            current_value=current_value
        ))
    
    def get_error_summary(self) -> str:
        """Get formatted error summary"""
        errors = [issue for issue in self.issues if issue.severity == ValidationSeverity.ERROR]
        if not errors:
            return ""
        
        summary = f"\n❌ Data Validation Failed ({len(errors)} errors):\n"
        for issue in errors:
            summary += f"  • {issue.field_path}: {issue.message}"
            if issue.current_value is not None:
                summary += f" (current: {issue.current_value})"
            summary += "\n"
        return summary


class DataContract:
    """
    Data contract validator for M2-M6 modules
    
    Enforces:
    1. Required fields must exist and have valid values (not 0/None for numeric fields)
    2. Numeric fields have proper types and ranges
    3. Cross-module dependencies are satisfied
    """
    
    # M4 Required Fields (Critical for M5)
    M4_REQUIRED_FIELDS = {
        'selected_scenario_id': (str, "Must specify which scenario is selected"),
        'legal_capacity.far_max': (float, "Legal FAR must be > 0"),
        'legal_capacity.bcr_max': (float, "Legal BCR must be > 0"),
        'legal_capacity.total_units': (int, "Total units must be > 0"),
        'legal_capacity.gross_floor_area': (float, "Gross floor area must be > 0"),
    }
    
    # M5 Required Fields (Critical for M6)
    M5_REQUIRED_FIELDS = {
        'total_cost': (float, "Total project cost must be > 0"),
        'lh_purchase_price': (float, "LH purchase price must be > 0"),
        'profit': (float, "Profit can be negative but must exist"),
        'profit_rate': (float, "Profit rate can be negative but must exist"),
        'household_count': (int, "Household count must be > 0"),
    }
    
    # M6 Required Fields
    M6_REQUIRED_FIELDS = {
        'total_score': (float, "Total score must exist"),
        'approval_rate': (float, "Approval rate must exist (0-100)"),
        'grade': (str, "Grade must be specified"),
        'decision': (str, "Decision (GO/CONDITIONAL/NO-GO) must be specified"),
    }
    
    @staticmethod
    def _get_nested_value(data: Dict[str, Any], path: str) -> Any:
        """Get nested dictionary value using dot notation"""
        keys = path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    @staticmethod
    def _validate_field(
        data: Dict[str, Any], 
        field_path: str, 
        expected_type: type,
        description: str,
        allow_zero: bool = False
    ) -> Optional[ValidationIssue]:
        """Validate a single field"""
        value = DataContract._get_nested_value(data, field_path)
        
        # Check existence
        if value is None:
            return ValidationIssue(
                field_path=field_path,
                severity=ValidationSeverity.ERROR,
                message=f"Missing required field. {description}",
                current_value=None,
                expected_type=expected_type
            )
        
        # Check type
        if not isinstance(value, expected_type):
            return ValidationIssue(
                field_path=field_path,
                severity=ValidationSeverity.ERROR,
                message=f"Type mismatch. {description}",
                current_value=value,
                expected_type=expected_type
            )
        
        # Check zero for numeric fields
        if not allow_zero and expected_type in (int, float):
            if value == 0 or value == 0.0:
                return ValidationIssue(
                    field_path=field_path,
                    severity=ValidationSeverity.ERROR,
                    message=f"Value cannot be zero. {description}",
                    current_value=value,
                    expected_type=expected_type
                )
        
        return None
    
    @classmethod
    def validate_m4_data(cls, data: Dict[str, Any]) -> ValidationResult:
        """Validate M4 building scale data"""
        result = ValidationResult(is_valid=True)
        
        for field_path, (expected_type, description) in cls.M4_REQUIRED_FIELDS.items():
            issue = cls._validate_field(data, field_path, expected_type, description)
            if issue:
                result.is_valid = False
                result.issues.append(issue)
        
        # Additional M4-specific validations
        far_max = cls._get_nested_value(data, 'legal_capacity.far_max')
        if far_max and far_max > 500:
            result.add_warning(
                'legal_capacity.far_max',
                f"FAR {far_max}% seems unusually high (typical range: 100-400%)",
                far_max
            )
        
        # Validate scenarios array
        scenarios = data.get('scenarios', [])
        if not scenarios or len(scenarios) == 0:
            result.add_error('scenarios', "At least one scenario must be provided", scenarios)
        else:
            for idx, scenario in enumerate(scenarios):
                if scenario.get('household_count', 0) == 0:
                    result.add_error(
                        f'scenarios[{idx}].household_count',
                        f"Scenario {scenario.get('id', idx)} has 0 households",
                        0
                    )
        
        return result
    
    @classmethod
    def validate_m5_data(cls, data: Dict[str, Any]) -> ValidationResult:
        """Validate M5 feasibility analysis data"""
        result = ValidationResult(is_valid=True)
        
        for field_path, (expected_type, description) in cls.M5_REQUIRED_FIELDS.items():
            # Profit can be negative, so allow zero
            allow_zero = 'profit' in field_path
            issue = cls._validate_field(data, field_path, expected_type, description, allow_zero)
            if issue:
                result.is_valid = False
                result.issues.append(issue)
        
        # Validate LH purchase price calculation inputs
        household_count = data.get('household_count', 0)
        avg_unit_area = data.get('avg_unit_area_m2', 0)
        lh_unit_price = data.get('lh_unit_price', 0)
        
        if household_count == 0:
            result.add_error(
                'household_count',
                "Household count is 0. Check M4 scenario selection.",
                household_count
            )
        
        if avg_unit_area == 0:
            result.add_error(
                'avg_unit_area_m2',
                "Average unit area is 0. Check M4 GFA breakdown.",
                avg_unit_area
            )
        
        if lh_unit_price == 0:
            result.add_warning(
                'lh_unit_price',
                "LH unit price is 0. Using estimation formula or manual input required.",
                lh_unit_price
            )
        
        return result
    
    @classmethod
    def validate_m6_data(cls, data: Dict[str, Any]) -> ValidationResult:
        """Validate M6 LH review prediction data"""
        result = ValidationResult(is_valid=True)
        
        for field_path, (expected_type, description) in cls.M6_REQUIRED_FIELDS.items():
            issue = cls._validate_field(data, field_path, expected_type, description, allow_zero=True)
            if issue:
                result.is_valid = False
                result.issues.append(issue)
        
        # Validate approval rate range
        approval_rate = data.get('approval_rate', -1)
        if approval_rate < 0 or approval_rate > 100:
            result.add_error(
                'approval_rate',
                f"Approval rate must be 0-100%, got {approval_rate}%",
                approval_rate
            )
        
        # Validate decision consistency
        decision = data.get('decision', '')
        valid_decisions = ['GO', 'CONDITIONAL_GO', 'NO_GO']
        if decision not in valid_decisions:
            result.add_error(
                'decision',
                f"Decision must be one of {valid_decisions}, got '{decision}'",
                decision
            )
        
        return result


class ContextSnapshot:
    """
    Single Source of Truth (SSOT) for cross-module data
    
    Created once at M1 lock, used by M2-M6 consistently.
    """
    
    def __init__(self, project_id: str, site_info: Dict[str, Any]):
        self.project_id = project_id
        self.site_info = site_info
        self.m2_results: Optional[Dict[str, Any]] = None
        self.m3_results: Optional[Dict[str, Any]] = None
        self.m4_results: Optional[Dict[str, Any]] = None
        self.m5_results: Optional[Dict[str, Any]] = None
        self.m6_results: Optional[Dict[str, Any]] = None
    
    def set_m2_results(self, results: Dict[str, Any]):
        """Store M2 land value results"""
        self.m2_results = results
    
    def set_m3_results(self, results: Dict[str, Any]):
        """Store M3 preferred type results"""
        self.m3_results = results
    
    def set_m4_results(self, results: Dict[str, Any]):
        """Store M4 building scale results (with validation)"""
        validation = DataContract.validate_m4_data(results)
        if not validation.is_valid:
            raise ValueError(f"M4 data validation failed: {validation.get_error_summary()}")
        self.m4_results = results
    
    def set_m5_results(self, results: Dict[str, Any]):
        """Store M5 feasibility results (with validation)"""
        validation = DataContract.validate_m5_data(results)
        if not validation.is_valid:
            raise ValueError(f"M5 data validation failed: {validation.get_error_summary()}")
        self.m5_results = results
    
    def set_m6_results(self, results: Dict[str, Any]):
        """Store M6 review prediction results (with validation)"""
        validation = DataContract.validate_m6_data(results)
        if not validation.is_valid:
            raise ValueError(f"M6 data validation failed: {validation.get_error_summary()}")
        self.m6_results = results
    
    def get_m5_inputs(self) -> Dict[str, Any]:
        """
        Get M5 input data from M4 results
        
        Returns consolidated data needed for M5 feasibility analysis
        """
        if not self.m4_results:
            raise ValueError("M4 results not available. Cannot generate M5 inputs.")
        
        # Extract selected scenario
        selected_id = self.m4_results.get('selected_scenario_id', '')
        scenarios = self.m4_results.get('scenarios', [])
        selected_scenario = next((s for s in scenarios if s.get('id') == selected_id), None)
        
        if not selected_scenario:
            raise ValueError(f"Selected scenario '{selected_id}' not found in M4 results")
        
        return {
            'scenario_id': selected_id,
            'household_count': selected_scenario.get('household_count', 0),
            'total_gfa_m2': selected_scenario.get('total_gfa_m2', 0),
            'avg_unit_area_m2': selected_scenario.get('avg_unit_area_m2', 0),
            'parking_required': selected_scenario.get('parking_required', 0),
            'parking_provided': selected_scenario.get('parking_provided', 0),
            'parking_type': selected_scenario.get('parking_type', ''),
            'construction_cost': selected_scenario.get('construction_cost', 0),
            'extra_costs': selected_scenario.get('extra_costs', {}),
        }
    
    def get_m6_inputs(self) -> Dict[str, Any]:
        """
        Get M6 input data from M4 + M5 results
        
        Returns consolidated data needed for M6 review prediction
        """
        if not self.m4_results or not self.m5_results:
            raise ValueError("M4 and M5 results required for M6 inputs")
        
        return {
            'from_m4': {
                'selected_scenario_id': self.m4_results.get('selected_scenario_id', ''),
                'household_count': self.m5_results.get('household_count', 0),
                'total_gfa_m2': self.m5_results.get('total_gfa_m2', 0),
                'parking_provided': self.m5_results.get('parking_provided', 0),
            },
            'from_m5': {
                'total_cost': self.m5_results.get('total_cost', 0),
                'lh_purchase_price': self.m5_results.get('lh_purchase_price', 0),
                'profit': self.m5_results.get('profit', 0),
                'profit_rate': self.m5_results.get('profit_rate', 0),
                'roi': self.m5_results.get('roi', 0),
            }
        }


def safe_get(data: Dict[str, Any], path: str, default: Any = None, error_if_zero: bool = False) -> Tuple[Any, Optional[str]]:
    """
    Safely get nested dictionary value with detailed error reporting
    
    Args:
        data: Source dictionary
        path: Dot-notation path (e.g., 'legal_capacity.far_max')
        default: Default value if not found
        error_if_zero: If True, treat 0 as error for numeric fields
    
    Returns:
        Tuple of (value, error_message)
        - If successful: (value, None)
        - If error: (default, error_message)
    """
    keys = path.split('.')
    value = data
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
            if value is None:
                return (default, f"Missing key '{key}' in path '{path}'")
        else:
            return (default, f"Cannot traverse non-dict at '{key}' in path '{path}'")
    
    # Check for zero if requested
    if error_if_zero and isinstance(value, (int, float)) and value == 0:
        return (default, f"Value at '{path}' is 0 (not allowed)")
    
    return (value, None)


# Export all public classes
__all__ = [
    'ValidationSeverity',
    'ValidationIssue',
    'ValidationResult',
    'DataContract',
    'ContextSnapshot',
    'safe_get',
]
