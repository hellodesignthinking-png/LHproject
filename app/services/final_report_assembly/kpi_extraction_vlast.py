"""
FINAL FIX vLAST: KPI Extraction → Normalization → Binding Pipeline
===================================================================

This is the LAST surgical fix to complete the data flow:
Module HTML → Final Report KPI Box

CRITICAL CHANGES:
1. Unified module root selector (data-module only)
2. Single data-* attribute extraction function
3. Forced key mapping to FINAL_KPI_SCHEMA
4. Hard-fail validation at binding stage
5. M3/M4 special handling

Author: ZeroSite Backend Team
Date: 2025-12-22
Version: vLAST
"""

from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# STEP 1: Module Root Selector (UNIFIED)
# ============================================================================

def get_module_root(soup: BeautifulSoup, module_id: str):
    """
    Find module root element by data-module attribute
    
    Args:
        soup: BeautifulSoup parsed HTML
        module_id: Module identifier (M2-M6)
        
    Returns:
        Module root element
        
    Raises:
        ValueError: If data-module not found
    """
    # Try direct data-module attribute
    root = soup.find(attrs={"data-module": module_id})
    
    if not root:
        raise ValueError(
            f"[BLOCKED] data-module='{module_id}' not found in module HTML. "
            f"Module HTML must include <div data-module=\"{module_id}\"> element."
        )
    
    logger.info(f"✅ Found module root for {module_id}: <{root.name}>")
    return root


# ============================================================================
# STEP 2: data-* Attribute Extraction (SINGLE FUNCTION)
# ============================================================================

def extract_from_data_attributes(module_root) -> Dict[str, str]:
    """
    Extract ALL data-* attributes from module root and its children
    
    Args:
        module_root: BeautifulSoup element with data-module
        
    Returns:
        Dict with normalized keys (data-foo-bar → foo_bar)
    """
    raw_data = {}
    
    # Extract from root element
    for attr, value in module_root.attrs.items():
        if attr.startswith("data-") and attr != "data-module":
            key = attr.replace("data-", "").replace("-", "_")
            raw_data[key] = value
    
    # Also check immediate children with data-* attributes
    for child in module_root.find_all(True):  # Find all tags
        if not hasattr(child, 'attrs'):
            continue
        for attr, value in child.attrs.items():
            if attr.startswith("data-") and attr != "data-module":
                key = attr.replace("data-", "").replace("-", "_")
                # Don't override if already exists
                if key not in raw_data:
                    raw_data[key] = value
    
    logger.info(f"Extracted {len(raw_data)} data-* attributes: {list(raw_data.keys())}")
    return raw_data


# ============================================================================
# STEP 3: Number Parsing Helper
# ============================================================================

def parse_number(value: Any) -> Optional[float]:
    """
    Parse number from string, handling various formats
    
    Args:
        value: String or number value
        
    Returns:
        Parsed number or None if parsing fails
    """
    if value is None:
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Remove commas and whitespace
        cleaned = value.replace(",", "").replace(" ", "").strip()
        
        # Handle boolean strings for M5
        if cleaned.lower() in ("true", "yes", "양호", "적합"):
            return 1.0
        if cleaned.lower() in ("false", "no", "부족", "부적합"):
            return 0.0
        
        # Try parsing as number
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    return None


# ============================================================================
# STEP 4: KPI Schema Normalization (FORCED MAPPING)
# ============================================================================

# Define FINAL_KPI_SCHEMA (matches Phase 3.10)
FINAL_KPI_SCHEMA = {
    "M2": ["land_value_total", "land_value_per_pyeong"],
    "M3": ["preferred_type", "type_score", "grade"],
    "M4": ["unit_count", "total_floor_area"],
    "M5": ["npv", "irr", "profitability_text"],
    "M6": ["decision", "risk_summary"]
}

# Key aliases for mapping
KEY_ALIASES = {
    "land_value": "land_value_total",
    "land_value_unit": "land_value_per_pyeong",
    "recommended_type": "preferred_type",
    "total_score": "type_score",
    "total_units": "unit_count",
    "floor_area": "total_floor_area",
    "is_profitable": "profitability_text",
    "lh_decision": "decision"
}


def normalize_kpi(raw_data: Dict[str, str], module_id: str) -> Dict[str, Any]:
    """
    Normalize extracted data to FINAL_KPI_SCHEMA
    
    Args:
        raw_data: Raw extracted data (from data-* attributes)
        module_id: Module identifier
        
    Returns:
        Normalized dict with schema keys only
    """
    if module_id not in FINAL_KPI_SCHEMA:
        logger.warning(f"Unknown module: {module_id}")
        return {"_complete": False, "_module_id": module_id}
    
    normalized = {"_module_id": module_id, "_complete": False, "_missing": []}
    schema_keys = FINAL_KPI_SCHEMA[module_id]
    
    # M3/M4 Special Handling (text + number mixed)
    if module_id == "M3":
        # preferred_type (text)
        normalized["preferred_type"] = (
            raw_data.get("preferred_type") or 
            raw_data.get("recommended_type") or
            None
        )
        # type_score (number)
        score = (
            raw_data.get("type_score") or 
            raw_data.get("total_score") or
            None
        )
        normalized["type_score"] = parse_number(score)
        # grade (text)
        normalized["grade"] = raw_data.get("grade") or None
    
    elif module_id == "M4":
        # unit_count (number)
        units = (
            raw_data.get("unit_count") or 
            raw_data.get("total_units") or
            None
        )
        normalized["unit_count"] = parse_number(units)
        # total_floor_area (number)
        area = (
            raw_data.get("total_floor_area") or 
            raw_data.get("floor_area") or
            None
        )
        normalized["total_floor_area"] = parse_number(area)
    
    else:
        # For M2, M5, M6: Standard mapping
        for schema_key in schema_keys:
            # Try direct key
            value = raw_data.get(schema_key)
            
            # Try aliases
            if value is None:
                for alias, canonical in KEY_ALIASES.items():
                    if canonical == schema_key and alias in raw_data:
                        value = raw_data[alias]
                        break
            
            # Parse if numeric expected
            if schema_key in ["land_value_total", "land_value_per_pyeong", "npv", "irr"]:
                normalized[schema_key] = parse_number(value)
            elif schema_key == "profitability_text":
                # Convert boolean to text
                if value is not None:
                    bool_val = parse_number(value)
                    if bool_val is not None:
                        normalized[schema_key] = "수익성 양호" if bool_val > 0.5 else "수익성 부족"
                    else:
                        normalized[schema_key] = value  # Keep as text
                else:
                    normalized[schema_key] = None
            else:
                normalized[schema_key] = value
    
    # Check completeness
    missing = []
    for key in schema_keys:
        if normalized.get(key) is None:
            missing.append(key)
    
    normalized["_complete"] = (len(missing) == 0)
    normalized["_missing"] = missing
    
    if not normalized["_complete"]:
        logger.warning(f"[{module_id}] Incomplete: missing {missing}")
    else:
        logger.info(f"[{module_id}] ✅ Complete normalization")
    
    return normalized


# ============================================================================
# STEP 5: Complete Extraction Function (ALL MODULES)
# ============================================================================

def extract_module_kpis(html: str, module_id: str) -> Dict[str, Any]:
    """
    Complete KPI extraction for a module
    
    Args:
        html: Module HTML string
        module_id: Module identifier (M2-M6)
        
    Returns:
        Normalized KPI dict
        
    Raises:
        ValueError: If module root not found
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Step 1: Find module root
    module_root = get_module_root(soup, module_id)
    
    # Step 2: Extract data-* attributes
    raw_data = extract_from_data_attributes(module_root)
    
    # Step 3: Normalize to schema
    normalized = normalize_kpi(raw_data, module_id)
    
    # Debug log
    logger.info(f"""
[{module_id}] Extraction Complete:
  - Raw keys: {list(raw_data.keys())}
  - Normalized: {normalized['_complete']}
  - Missing: {normalized.get('_missing', [])}
""")
    
    return normalized


# ============================================================================
# STEP 6: Apply Fix to All Assemblers
# ============================================================================

def apply_vlast_fix_to_assembler(assembler_file_path: str):
    """
    Apply vLAST fix to an assembler file
    
    This replaces the _extract_kpi_from_module_html() method
    with the new extract_module_kpis() function
    """
    import os
    
    # Read assembler file
    with open(assembler_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already patched
    if "extract_module_kpis" in content:
        print(f"✅ {os.path.basename(assembler_file_path)}: Already patched")
        return False
    
    # Add import at top (after other imports)
    import_statement = """
# vLAST FIX: Import unified KPI extraction
from app.services.final_report_assembly.kpi_extraction_vlast import extract_module_kpis
"""
    
    # Find where to insert (after last import, before class definition)
    import_insert_pos = content.rfind("import ")
    if import_insert_pos != -1:
        # Find end of that line
        import_end = content.find("\n", import_insert_pos)
        content = content[:import_end+1] + import_statement + content[import_end+1:]
    
    # Replace _extract_kpi_from_module_html calls with extract_module_kpis
    content = content.replace(
        "self._extract_kpi_from_module_html(",
        "extract_module_kpis("
    )
    
    # Write back
    with open(assembler_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {os.path.basename(assembler_file_path)}: vLAST fix applied")
    return True


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔥 FINAL FIX vLAST - KPI Extraction Pipeline")
    print("="*80 + "\n")
    
    # Test with sample HTML
    sample_html = """
    <div class="container" data-module="M2">
        <div class="key-result-card" 
             data-land-value-total="5600000000" 
             data-land-value-per-pyeong="5500000">
            <h2>토지 평가액: 5,600,000,000원</h2>
        </div>
    </div>
    """
    
    print("Testing M2 extraction:")
    result = extract_module_kpis(sample_html, "M2")
    print(f"  Complete: {result['_complete']}")
    print(f"  land_value_total: {result.get('land_value_total')}")
    print(f"  land_value_per_pyeong: {result.get('land_value_per_pyeong')}")
    
    print("\n" + "="*80 + "\n")
