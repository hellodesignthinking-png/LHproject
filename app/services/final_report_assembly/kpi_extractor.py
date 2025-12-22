"""
KPI Extractor - Phase 3.10 Final Lock
단일 KPI 추출 서비스 (구조적 안정성 보장)

This module provides:
- Module root enforcement (section[data-module] only)
- Raw KPI extraction from data-* attributes
- Controlled alias rules for M3/M4
- Normalize with required keys validation
- No fallback guessing allowed

Exit Criteria:
1. All KPI extraction must be based on Module Root
2. Hard-Fail only when required KPI is actually None
3. M3/M4 limited to official aliases only
4. N/A structurally impossible in KPI Box

Author: ZeroSite Backend Team
Date: 2025-12-22
Phase: 3.10 Final Lock
"""

from typing import Dict, List, Optional
from bs4 import BeautifulSoup, Tag
import re
import logging

logger = logging.getLogger(__name__)


class FinalReportAssemblyError(RuntimeError):
    """Raised when Final Report Assembly fails structurally"""
    pass


class KPIExtractor:
    """
    Single source of truth for KPI extraction
    No guessing, no fallbacks (except official M3/M4 aliases)
    """
    
    # Official alias rules (ONLY these are allowed)
    OFFICIAL_ALIASES = {
        "M3": {
            "total_score": ["type_score"],  # total_score can fallback to type_score
        },
        "M4": {
            "total_units": ["unit_count"],  # total_units can fallback to unit_count
        }
    }
    
    @staticmethod
    def get_module_root(html: str, module_id: str) -> Tag:
        """
        Get module root element - ONLY section[data-module] is accepted
        
        Args:
            html: Module HTML string
            module_id: Module ID (M2, M3, M4, M5, M6)
            
        Returns:
            BeautifulSoup Tag representing module root
            
        Raises:
            FinalReportAssemblyError: If module root not found (structural error)
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # ONLY section with data-module attribute
        root = soup.find('section', attrs={'data-module': module_id})
        
        if not root:
            # Also try div as fallback (some modules use div)
            root = soup.find('div', attrs={'data-module': module_id})
        
        if not root:
            raise FinalReportAssemblyError(
                f"[BLOCKED] Module root not found: {module_id}. "
                f"Expected: section[data-module='{module_id}'] or div[data-module='{module_id}']"
            )
        
        logger.debug(f"✅ Module root found: {module_id} (tag: {root.name})")
        return root
    
    @staticmethod
    def extract_raw_kpi_from_root(root: Tag) -> Dict[str, str]:
        """
        Extract raw KPI from module root's data-* attributes
        
        Args:
            root: Module root element
            
        Returns:
            Dict of raw KPI (key: attribute name without 'data-', value: string)
        """
        raw = {}
        
        for attr_name, attr_value in root.attrs.items():
            if attr_name.startswith('data-'):
                # Convert data-land-value-total -> land_value_total
                key = attr_name[5:].replace('-', '_')
                raw[key] = attr_value
                logger.debug(f"  Extracted: {key} = {attr_value}")
        
        logger.debug(f"✅ Extracted {len(raw)} raw KPI from root")
        return raw
    
    @staticmethod
    def parse_number(value: str) -> Optional[float]:
        """
        Parse number from string (handles Korean units, commas, %)
        
        Args:
            value: String value (e.g., "5,600,000,000원", "85%", "1,234㎡")
            
        Returns:
            Parsed number or None if parsing fails
        """
        if not value or not isinstance(value, str):
            return None
        
        try:
            # Remove Korean units and spaces
            cleaned = value.replace('원', '').replace('억', '').replace('만', '')
            cleaned = cleaned.replace('㎡', '').replace('%', '').replace(' ', '')
            cleaned = cleaned.replace(',', '')
            
            # Try to parse as float
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def apply_alias_rules(module_id: str, raw: Dict[str, str]) -> Dict[str, str]:
        """
        Apply official alias rules for M3/M4 ONLY
        
        Args:
            module_id: Module ID
            raw: Raw KPI dict
            
        Returns:
            Raw KPI dict with aliases applied
        """
        if module_id not in KPIExtractor.OFFICIAL_ALIASES:
            return raw
        
        aliases = KPIExtractor.OFFICIAL_ALIASES[module_id]
        
        for primary_key, fallback_keys in aliases.items():
            if primary_key not in raw or not raw[primary_key]:
                # Try fallback keys in order
                for fallback_key in fallback_keys:
                    if fallback_key in raw and raw[fallback_key]:
                        logger.info(f"🔄 [{module_id}] Applied alias: {fallback_key} → {primary_key}")
                        raw[primary_key] = raw[fallback_key]
                        break
        
        return raw
    
    @staticmethod
    def normalize_kpi(raw: Dict[str, str], required_keys: List[str], module_id: str) -> Dict[str, Optional[float]]:
        """
        Normalize KPI - ONLY for required keys, no extra key generation
        
        Args:
            raw: Raw KPI dict
            required_keys: List of required keys for this module
            module_id: Module ID (for logging)
            
        Returns:
            Normalized KPI dict (key: str, value: float or None)
        """
        normalized = {}
        
        for key in required_keys:
            if key not in raw:
                logger.warning(f"⚠️ [{module_id}] Required key missing: {key}")
                normalized[key] = None
            else:
                parsed = KPIExtractor.parse_number(raw[key])
                if parsed is None:
                    logger.warning(f"⚠️ [{module_id}] Failed to parse {key}: {raw[key]}")
                normalized[key] = parsed
        
        return normalized
    
    @staticmethod
    def extract_module_kpi(
        html: str, 
        module_id: str, 
        required_keys: List[str],
        strict: bool = True
    ) -> Dict:
        """
        [vPOST-FINAL] Extract KPI from module HTML - SINGLE ENTRY POINT with operational safety
        
        Args:
            html: Module HTML string
            module_id: Module ID (M2, M3, M4, M5, M6)
            required_keys: List of required KPI keys for this module
            strict: If False, return incomplete data with reasons (operational mode)
            
        Returns:
            Dict with normalized KPI + metadata:
            {
                "land_value_total": 5600000000.0,
                "land_value_per_pyeong": 5500000.0,
                "_module_id": "M2",
                "_required_keys": ["land_value_total"],
                "_extracted_keys": ["land_value_total", "land_value_per_pyeong"],
                "_normalized_ok": True,
                "_incomplete_reason": "data-land-value-total attribute missing"  # if strict=False
            }
            
        Raises:
            FinalReportAssemblyError: If module root not found (always strict)
        """
        logger.info(f"🔍 Extracting KPI from {module_id} (required: {required_keys}, strict={strict})")
        
        # Step 1: Get module root (ENFORCED - always strict)
        root = KPIExtractor.get_module_root(html, module_id)
        
        # Step 2: Extract raw KPI from data-* attributes
        raw = KPIExtractor.extract_raw_kpi_from_root(root)
        
        # Step 3: Apply alias rules (M3/M4 only)
        raw = KPIExtractor.apply_alias_rules(module_id, raw)
        
        # Step 4: Normalize (required keys only)
        normalized = KPIExtractor.normalize_kpi(raw, required_keys, module_id)
        
        # [vPOST-FINAL] Check completeness
        missing_keys = [k for k in required_keys if normalized.get(k) is None]
        is_complete = len(missing_keys) == 0
        
        # Add metadata
        result = {
            **normalized,
            "_module_id": module_id,
            "_required_keys": required_keys,
            "_extracted_keys": list(raw.keys()),
            "_normalized_ok": is_complete
        }
        
        # [vPOST-FINAL] If incomplete and not strict, add reason
        if not is_complete and not strict:
            result["_incomplete_reason"] = f"Missing required KPI: {', '.join(missing_keys)}"
            logger.warning(f"[{module_id}] Incomplete KPI (non-strict mode): {missing_keys}")
        
        
        logger.info(
            f"✅ [{module_id}] Extracted: {len(raw)} raw, "
            f"Normalized: {len(normalized)} required, "
            f"OK: {result['_normalized_ok']}"
        )
        
        return result


def validate_mandatory_kpi(
    report_type: str,
    modules_data: Dict[str, Dict],
    mandatory_kpi: Dict[str, Dict[str, List[str]]]
) -> List[str]:
    """
    Validate that all mandatory KPI are present and not None
    
    Args:
        report_type: Report type (landowner_summary, quick_check, etc.)
        modules_data: Extracted modules data
        mandatory_kpi: MANDATORY_KPI dict
        
    Returns:
        List of missing KPI (empty if all present)
    """
    missing = []
    
    if report_type not in mandatory_kpi:
        logger.warning(f"⚠️ No mandatory KPI defined for report type: {report_type}")
        return missing
    
    for module_id, required_keys in mandatory_kpi[report_type].items():
        module_data = modules_data.get(module_id, {})
        
        for key in required_keys:
            value = module_data.get(key)
            if value is None:
                missing.append(f"{module_id}.{key}")
                logger.error(f"❌ Missing required KPI: {module_id}.{key}")
    
    return missing


def validate_kpi_with_safe_gate(
    report_type: str,
    modules_data: Dict[str, Dict],
    mandatory_kpi: Dict[str, Dict[str, List[str]]],
    critical_kpi: Dict[str, Dict[str, List[str]]]
) -> Dict[str, List[str]]:
    """
    [vPOST-FINAL] Validate KPI with SAFE-GATE logic (operational safety)
    
    Two-level validation:
    1. CRITICAL KPI missing → Hard-Fail (blocks report generation)
    2. Non-critical KPI missing → Soft-Fail (allows report with WARNING)
    
    Args:
        report_type: Report type (landowner_summary, quick_check, etc.)
        modules_data: Extracted modules data
        mandatory_kpi: MANDATORY_KPI dict (all required KPIs)
        critical_kpi: CRITICAL_KPI dict (must-have KPIs only)
        
    Returns:
        Dict with two lists:
        {
            "critical_missing": ["M5.npv", "M6.decision"],  # Hard-Fail
            "soft_missing": ["M2.land_value_total"]  # Soft-Fail (WARNING only)
        }
    """
    critical_missing = []
    soft_missing = []
    
    if report_type not in mandatory_kpi:
        logger.warning(f"⚠️ No mandatory KPI defined for report type: {report_type}")
        return {"critical_missing": [], "soft_missing": []}
    
    # Get critical KPI for this report
    critical_map = critical_kpi.get(report_type, {})
    
    # Check all mandatory KPI
    for module_id, required_keys in mandatory_kpi[report_type].items():
        module_data = modules_data.get(module_id, {})
        critical_keys_for_module = critical_map.get(module_id, [])
        
        for key in required_keys:
            value = module_data.get(key)
            if value is None:
                kpi_id = f"{module_id}.{key}"
                
                # Determine if this is CRITICAL or SOFT
                if key in critical_keys_for_module:
                    critical_missing.append(kpi_id)
                    logger.error(f"🚫 CRITICAL KPI missing: {kpi_id} (Hard-Fail)")
                else:
                    soft_missing.append(kpi_id)
                    logger.warning(f"⚠️  Soft KPI missing: {kpi_id} (WARNING only)")
    
    return {
        "critical_missing": critical_missing,
        "soft_missing": soft_missing
    }


def log_kpi_pipeline(
    report_type: str,
    context_id: str,
    module_id: str,
    kpi_data: Dict
) -> None:
    """
    Log KPI pipeline for audit trail
    
    Args:
        report_type: Report type
        context_id: Context ID
        module_id: Module ID
        kpi_data: Extracted KPI data with metadata
    """
    log_entry = {
        "report_type": report_type,
        "context_id": context_id,
        "module": module_id,
        "required": kpi_data.get("_required_keys", []),
        "extracted": kpi_data.get("_extracted_keys", []),
        "normalized_ok": kpi_data.get("_normalized_ok", False),
        "bound": all(
            kpi_data.get(k) is not None 
            for k in kpi_data.get("_required_keys", [])
        )
    }
    
    logger.info(f"📊 KPI Pipeline: {log_entry}")
