"""
Value Presenter - Single Filter for ALL Output Values
BLOCKS internal data structure exposure
"""
from typing import Any, Union


def present(value: Any, unit: str = "") -> str:
    """
    Present ANY value in human-readable format
    BLOCKS dict/list/None exposure completely
    
    Args:
        value: Any value to present
        unit: Optional unit suffix (원, 세대, %, etc.)
        
    Returns:
        Human-readable string (NEVER dict/list/None)
    """
    # Block None
    if value is None:
        return "산출 진행 중"
    
    # Block dict/list (CRITICAL)
    if isinstance(value, (dict, list)):
        return "산출 진행 중"
    
    # Block empty string
    if isinstance(value, str) and not value.strip():
        return "산출 진행 중"
    
    # Format number with commas
    if isinstance(value, (int, float)):
        formatted = f"{value:,.0f}" if isinstance(value, float) and value.is_integer() else f"{value:,.2f}"
        return f"{formatted}{unit}"
    
    # String passthrough (clean)
    return f"{str(value)}{unit}"


def present_soft_kpi(value: Any) -> str:
    """
    Present Soft KPI with explanatory sentence
    Used when value is incomplete/pending
    
    Args:
        value: Soft KPI value
        
    Returns:
        Explanatory sentence
    """
    if value is None or isinstance(value, (dict, list)) or (isinstance(value, str) and not value.strip()):
        return "해당 항목은 현재 산출 중이며, 상세 설계 확정 시 구체화됩니다."
    
    return present(value)


def format_currency(value: Any) -> str:
    """Format currency with 원 unit"""
    return present(value, "원")


def format_units(value: Any) -> str:
    """Format housing units with 세대 unit"""
    return present(value, "세대")


def format_percentage(value: Any) -> str:
    """Format percentage with % unit"""
    return present(value, "%")
