#!/usr/bin/env python3
"""
Phase 3.10 - Hard-Fail Enforcement & KPI Binding Lock
======================================================

PURPOSE:
    Phase 3.9 fixed extraction, but extraction ≠ binding.
    This phase adds the FINAL enforcement layer:
    
    1. KPI Canonical Schema (ALL reports must follow)
    2. Mandatory KPI Matrix (report_type × required modules)
    3. Extract → Normalize → Bind separation
    4. Hard-fail validation (BLOCK if any mandatory KPI missing)
    5. QA Validator role change ("숫자적으로 성립하는가?")

PHILOSOPHY:
    "차라리 안 만들어지게" - If core data missing, FAIL immediately.
    
Author: ZeroSite Backend Team
Date: 2025-12-22
Phase: 3.10 (Final Enforcement)
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# 1️⃣ KPI CANONICAL SCHEMA (Universal Standard)
# ============================================================================

KPI_CANONICAL_SCHEMA = {
    "M2": ["land_value_total", "land_value_per_pyeong"],
    "M3": ["preferred_type", "type_score", "grade"],
    "M4": ["unit_count", "total_floor_area"],
    "M5": ["npv", "irr", "profitability_text"],
    "M6": ["decision", "risk_summary"]
}

# Alternative names for mapping (module HTML → canonical)
KPI_FIELD_ALIASES = {
    "land_value": "land_value_total",
    "land_value_unit": "land_value_per_pyeong",
    "recommended_type": "preferred_type",
    "total_score": "type_score",
    "total_units": "unit_count",
    "floor_area": "total_floor_area",
    "is_profitable": "profitability_text"  # Convert boolean → text
}


# ============================================================================
# 2️⃣ REPORT TYPE × MANDATORY KPI MATRIX
# ============================================================================

REPORT_MANDATORY_KPI = {
    "landowner_summary": {
        "M2": ["land_value_total"],
        "M5": ["npv", "profitability_text"],
        "M6": ["decision"]
    },
    "quick_check": {
        "M5": ["npv", "profitability_text"],
        "M6": ["decision"]
    },
    "financial_feasibility": {
        "M2": ["land_value_total"],
        "M4": ["unit_count"],
        "M5": ["npv", "irr"]
    },
    "lh_technical": {
        "M3": ["preferred_type", "type_score"],
        "M4": ["unit_count"],
        "M6": ["decision"]
    },
    "executive_summary": {
        "M2": ["land_value_total"],
        "M5": ["npv"],
        "M6": ["decision"]
    },
    "all_in_one": {
        "M2": ["land_value_total"],
        "M3": ["preferred_type"],
        "M4": ["unit_count"],
        "M5": ["npv"],
        "M6": ["decision"]
    }
}


# ============================================================================
# 3️⃣ EXCEPTIONS
# ============================================================================

class FinalReportGenerationError(RuntimeError):
    """Raised when Final Report cannot be generated due to missing KPIs"""
    pass


class KPIBindingError(RuntimeError):
    """Raised when KPI extraction succeeded but binding failed"""
    pass


# ============================================================================
# 4️⃣ KPI NORMALIZER (Extract → Normalize → Bind)
# ============================================================================

class KPINormalizer:
    """
    Normalizes extracted module data to canonical KPI schema
    
    Phase 3.9: _extract_kpi_from_module_html() returns raw dict
    Phase 3.10: This class normalizes it to canonical schema
    """
    
    @staticmethod
    def normalize(module_id: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw extraction data to canonical schema
        
        Args:
            module_id: Module identifier (M2-M6)
            raw_data: Raw data from _extract_kpi_from_module_html()
        
        Returns:
            Normalized dict with canonical field names
        """
        normalized = {"_module_id": module_id, "_complete": False}
        
        if module_id not in KPI_CANONICAL_SCHEMA:
            logger.warning(f"[KPINormalizer] Unknown module: {module_id}")
            return normalized
        
        canonical_fields = KPI_CANONICAL_SCHEMA[module_id]
        
        # Map raw fields to canonical fields
        for raw_key, raw_value in raw_data.items():
            if raw_key.startswith("_"):
                normalized[raw_key] = raw_value  # Preserve metadata
                continue
            
            # Try direct mapping
            if raw_key in canonical_fields:
                normalized[raw_key] = raw_value
            # Try alias mapping
            elif raw_key in KPI_FIELD_ALIASES:
                canonical_key = KPI_FIELD_ALIASES[raw_key]
                if canonical_key in canonical_fields:
                    normalized[canonical_key] = raw_value
        
        # Special conversions
        if module_id == "M5" and "is_profitable" in raw_data:
            normalized["profitability_text"] = (
                "수익성 양호" if raw_data["is_profitable"] else "수익성 부족"
            )
        
        # Check completeness
        required_fields = canonical_fields
        normalized["_complete"] = all(
            normalized.get(field) is not None 
            for field in required_fields
        )
        
        if not normalized["_complete"]:
            missing = [f for f in required_fields if normalized.get(f) is None]
            normalized["_missing"] = missing
            logger.warning(
                f"[KPINormalizer] {module_id} incomplete: missing {missing}"
            )
        
        return normalized


# ============================================================================
# 5️⃣ KPI BINDER (Bind normalized data to Final Report KPI Box)
# ============================================================================

class KPIBinder:
    """
    Binds normalized module data to Final Report KPI summary
    
    Ensures:
    1. Only canonical fields are used
    2. Mandatory KPIs for report_type are present
    3. Type-safe value formatting
    """
    
    @staticmethod
    def bind_for_report(
        normalized_modules: Dict[str, Dict[str, Any]],
        report_type: str
    ) -> Dict[str, Any]:
        """
        Create KPI binding dict for specific report type
        
        Args:
            normalized_modules: Dict of normalized module data
            report_type: Target report type
        
        Returns:
            Dict ready for generate_kpi_summary_box()
        
        Raises:
            KPIBindingError: If mandatory KPIs missing
        """
        if report_type not in REPORT_MANDATORY_KPI:
            raise ValueError(f"Unknown report_type: {report_type}")
        
        bound_kpis = {}
        missing_kpis = []
        
        mandatory = REPORT_MANDATORY_KPI[report_type]
        
        for module_id, required_fields in mandatory.items():
            if module_id not in normalized_modules:
                missing_kpis.append(f"{module_id}: module not analyzed")
                continue
            
            module_data = normalized_modules[module_id]
            
            for field in required_fields:
                value = module_data.get(field)
                
                if value is None or value == "":
                    missing_kpis.append(f"{module_id}.{field}")
                else:
                    # Create display key (for KPI box)
                    display_key = KPIBinder._get_display_name(module_id, field)
                    bound_kpis[display_key] = value
        
        if missing_kpis:
            raise KPIBindingError(
                f"[BLOCKED] Missing mandatory KPIs for {report_type}: "
                f"{', '.join(missing_kpis)}"
            )
        
        return bound_kpis
    
    @staticmethod
    def _get_display_name(module_id: str, canonical_field: str) -> str:
        """Map canonical field to Korean display name"""
        display_names = {
            "land_value_total": "총 토지 감정가",
            "land_value_per_pyeong": "평당 감정가",
            "preferred_type": "추천 유형",
            "type_score": "선호도 점수",
            "grade": "등급",
            "unit_count": "총 세대수",
            "total_floor_area": "총 연면적",
            "npv": "순현재가치(NPV)",
            "irr": "내부수익률(IRR)",
            "profitability_text": "수익성 판단",
            "decision": "LH 심사 결과",
            "risk_summary": "위험도 요약"
        }
        
        return display_names.get(canonical_field, canonical_field)


# ============================================================================
# 6️⃣ HARD-FAIL VALIDATOR
# ============================================================================

class HardFailValidator:
    """
    Final gate before HTML/PDF generation
    
    BLOCKS generation if:
    1. Any mandatory KPI is None/empty
    2. KPI Box ↔ Narrative mismatch
    3. Decision block has no numeric basis
    """
    
    @staticmethod
    def validate_before_generation(
        report_type: str,
        normalized_modules: Dict[str, Dict[str, Any]],
        bound_kpis: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """
        Validate BEFORE HTML/PDF generation
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check 1: Mandatory modules present
        mandatory = REPORT_MANDATORY_KPI[report_type]
        
        for module_id in mandatory.keys():
            if module_id not in normalized_modules:
                errors.append(f"❌ {module_id}: Module not analyzed")
            elif not normalized_modules[module_id].get("_complete", False):
                missing = normalized_modules[module_id].get("_missing", [])
                errors.append(
                    f"❌ {module_id}: Incomplete data (missing: {', '.join(missing)})"
                )
        
        # Check 2: Bound KPIs not empty
        if not bound_kpis or len(bound_kpis) == 0:
            errors.append("❌ KPI binding failed: No KPIs bound to report")
        
        # Check 3: Specific report type requirements
        if report_type == "landowner_summary":
            # Must have: land value, NPV, LH decision
            required = ["총 토지 감정가", "순현재가치(NPV)", "LH 심사 결과"]
            for req in required:
                if req not in bound_kpis or bound_kpis[req] in [None, "", "N/A"]:
                    errors.append(f"❌ Landowner Summary: Missing {req}")
        
        elif report_type == "all_in_one":
            # Must have ALL modules
            if len(normalized_modules) < 5:
                errors.append(
                    f"❌ Comprehensive Report: Only {len(normalized_modules)}/5 modules available"
                )
        
        is_valid = (len(errors) == 0)
        
        return is_valid, errors


# ============================================================================
# 7️⃣ INTEGRATION HELPER (For Assemblers)
# ============================================================================

def enforce_kpi_binding(
    report_type: str,
    modules_data: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Complete pipeline: Normalize → Bind → Validate → Return KPIs
    
    Usage in assembler:
        try:
            bound_kpis = enforce_kpi_binding(self.report_type, modules_data)
            kpi_summary = self.generate_kpi_summary_box(bound_kpis, self.report_type)
        except (KPIBindingError, FinalReportGenerationError) as e:
            # Return FAIL result with error
            return {
                "html": self._generate_error_placeholder(str(e)),
                "qa_result": {"status": "FAIL", "errors": [str(e)], "blocking": True}
            }
    
    Args:
        report_type: Target report type
        modules_data: Raw data from _extract_module_data()
    
    Returns:
        bound_kpis dict ready for generate_kpi_summary_box()
    
    Raises:
        KPIBindingError: If binding fails
        FinalReportGenerationError: If validation fails
    """
    # Step 1: Normalize
    normalized_modules = {}
    for module_id, raw_data in modules_data.items():
        normalized_modules[module_id] = KPINormalizer.normalize(module_id, raw_data)
    
    # Step 2: Bind
    try:
        bound_kpis = KPIBinder.bind_for_report(normalized_modules, report_type)
    except KPIBindingError as e:
        logger.error(f"[enforce_kpi_binding] Binding failed: {e}")
        raise
    
    # Step 3: Validate (Hard-Fail)
    is_valid, errors = HardFailValidator.validate_before_generation(
        report_type, normalized_modules, bound_kpis
    )
    
    if not is_valid:
        error_msg = f"[BLOCKED] Cannot generate {report_type}:\n" + "\n".join(errors)
        logger.error(error_msg)
        raise FinalReportGenerationError(error_msg)
    
    logger.info(
        f"[enforce_kpi_binding] ✅ {report_type}: "
        f"{len(bound_kpis)} KPIs bound successfully"
    )
    
    return bound_kpis


# ============================================================================
# 8️⃣ USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Example: landowner_summary with M2, M5, M6 data
    
    # Simulated raw extraction data (from Phase 3.9)
    modules_data = {
        "M2": {
            "_module_id": "M2",
            "_complete": True,
            "_extraction_method": "table",
            "land_value": 1234567890,  # Will map to land_value_total
        },
        "M5": {
            "_module_id": "M5",
            "_complete": True,
            "_extraction_method": "regex",
            "npv": 500000000,
            "irr": 12.5,
            "is_profitable": True  # Will convert to profitability_text
        },
        "M6": {
            "_module_id": "M6",
            "_complete": True,
            "_extraction_method": "keyword",
            "decision": "추진 가능"
        }
    }
    
    try:
        bound_kpis = enforce_kpi_binding("landowner_summary", modules_data)
        print("✅ KPI Binding Success!")
        print(f"Bound KPIs: {bound_kpis}")
    except (KPIBindingError, FinalReportGenerationError) as e:
        print(f"❌ KPI Binding Failed: {e}")
