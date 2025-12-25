"""
Value Resolver - Safe data extraction from canonical_summary
"""
from typing import Any, Optional


def get_by_path(data: dict, path: str) -> Optional[Any]:
    """
    Safely get value by dot-separated path
    Example: get_by_path(cs, "M2.summary.land_value_total_krw")
    """
    if not data:
        return None
    
    parts = path.split(".")
    current = data
    
    for part in parts:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
        if current is None:
            return None
    
    return current


def resolve_scalar(modules_data: dict, module_id: str, key: str = None) -> Optional[Any]:
    """
    Extract scalar value from modules_data safely
    Returns None if value is dict/list/None
    
    Args:
        modules_data: dict containing module data (e.g. {"M2": {...}, "M5": {...}})
        module_id: module identifier (e.g. "M2", "M5")
        key: optional key to extract from module (e.g. "npv", "land_value_total")
             if None, returns the whole module dict (for backward compatibility)
        
    Returns:
        Scalar value or None
    """
    if not modules_data or not isinstance(modules_data, dict):
        return None
    
    module = modules_data.get(module_id)
    if module is None:
        return None
    
    # If no key specified, this is legacy usage - return None to avoid dict exposure
    if key is None:
        return None
    
    # Get value from module
    value = module.get(key) if isinstance(module, dict) else None
    
    if value is None:
        return None
    
    # Block dict/list exposure
    if isinstance(value, (dict, list)):
        return None
    
    # Block internal metadata
    if isinstance(value, str) and (value.startswith("_") or value == "N/A"):
        return None
    
    return value


def present_money_krw(v: Any) -> str:
    """Format money in KRW with commas"""
    if not isinstance(v, (int, float)):
        return "산출 중"
    return f"{int(round(v)):,}원"


def present_int(v: Any) -> str:
    """Format integer with commas"""
    if not isinstance(v, (int, float)):
        return "산출 중"
    return f"{int(round(v)):,}"


def present_pct(v: Any) -> str:
    """Format percentage"""
    if not isinstance(v, (int, float)):
        return "산출 중"
    return f"{v:.2f}%"


def present_text(v: Any) -> str:
    """Present text safely"""
    if v is None:
        return "산출 중"
    if isinstance(v, (dict, list)):
        return "산출 중"
    return str(v)
