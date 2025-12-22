"""
Phase 3: Final Report Assembly - Architecture Principles

This module enforces the strict separation between:
- MODULE LEVEL: Calculation engines (M2-M6) - COMPLETE & LOCKED
- REPORT LEVEL: Assembly engines (Final Reports) - THIS PHASE

CRITICAL PRINCIPLES (ENFORCED AT RUNTIME):
1. Final Reports NEVER calculate or recalculate data
2. Final Reports NEVER directly access canonical_summary
3. Final Reports ONLY assemble pre-generated module HTML fragments
4. Final Reports are "HTML Assemblers", NOT "Data Engines"
5. Violations raise RuntimeError immediately

Author: ZeroSite Backend Team
Date: 2025-12-22
Phase: 3 (Final Report Assembly)
"""

from typing import Dict, List, Literal, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class FinalReportAssemblyError(RuntimeError):
    """Raised when Final Report Assembly principles are violated"""
    pass


class BaseFinalReportAssembler(ABC):
    """
    Base class for all Final Report Assemblers
    
    ENFORCES PHASE 3 PRINCIPLES:
    - No calculation logic allowed
    - No direct canonical_summary access
    - Only HTML fragment assembly
    
    All subclasses MUST follow these rules or raise FinalReportAssemblyError
    """
    
    # 🔒 ALLOWED OPERATIONS
    ALLOWED_OPERATIONS = {
        "load_module_html",      # Load pre-generated module HTML
        "assemble_sections",     # Combine HTML fragments
        "apply_report_styling",  # Add report-specific CSS
        "generate_cover_page",   # Create report cover
        "generate_summary",      # Create executive summary
        "validate_completeness", # Check all required modules present
    }
    
    # ❌ FORBIDDEN OPERATIONS (Will raise error if detected)
    FORBIDDEN_OPERATIONS = {
        "calculate",
        "recalculate", 
        "compute",
        "analyze",
        "process_data",
        "extract_from_canonical",
        "access_canonical_summary",
        "load_canonical_summary",
    }
    
    def __init__(self, context_id: str):
        """
        Initialize Final Report Assembler
        
        Args:
            context_id: Context ID for which to generate final report
        """
        self.context_id = context_id
        self._module_html_cache: Dict[str, str] = {}
        self._validate_initialization()
    
    def _validate_initialization(self):
        """Validate that subclass doesn't violate Phase 3 principles"""
        # Check class name doesn't imply calculation
        class_name = self.__class__.__name__.lower()
        forbidden_keywords = ["calculator", "engine", "processor", "analyzer"]
        
        for keyword in forbidden_keywords:
            if keyword in class_name:
                raise FinalReportAssemblyError(
                    f"❌ PHASE 3 VIOLATION: Class name '{self.__class__.__name__}' "
                    f"contains forbidden keyword '{keyword}'. "
                    f"Final Report Assemblers should be named '*Assembler' or '*Builder'."
                )
        
        logger.info(f"✅ Phase 3 Assembler initialized: {self.__class__.__name__}")
        logger.info(f"   Context ID: {self.context_id}")
        logger.info(f"   Mode: ASSEMBLY ONLY (no calculation)")
    
    def _enforce_no_calculation(self, method_name: str):
        """
        Enforce that no calculation methods are called
        
        Raises:
            FinalReportAssemblyError: If method name suggests calculation
        """
        method_lower = method_name.lower()
        
        for forbidden in self.FORBIDDEN_OPERATIONS:
            if forbidden in method_lower:
                raise FinalReportAssemblyError(
                    f"❌ PHASE 3 VIOLATION: Method '{method_name}' suggests calculation/data processing. "
                    f"Final Reports must ONLY assemble pre-generated HTML fragments. "
                    f"Use load_module_html() instead."
                )
    
    def _block_canonical_summary_access(self):
        """
        Block any attempt to access canonical_summary directly
        
        This is enforced at runtime to prevent bypassing module HTML fragments
        """
        raise FinalReportAssemblyError(
            "❌ PHASE 3 VIOLATION: Direct canonical_summary access is FORBIDDEN. "
            "Final Reports must use pre-generated module HTML fragments only. "
            "Use load_module_html('M2'...'M6') instead."
        )
    
    @abstractmethod
    def assemble(self) -> Dict[str, str]:
        """
        Assemble final report from module HTML fragments
        
        Returns:
            Dict with 'html' and 'pdf' keys
            
        MUST ONLY:
        - Load module HTML fragments
        - Combine them in specified order
        - Apply report-specific styling
        - Generate cover/summary pages
        
        MUST NOT:
        - Calculate any data
        - Access canonical_summary directly
        - Recalculate module results
        """
        pass
    
    @abstractmethod
    def get_required_modules(self) -> List[Literal["M2", "M3", "M4", "M5", "M6"]]:
        """
        Return list of required modules for this report type
        
        Returns:
            List of module IDs (e.g., ["M2", "M3", "M5"])
        """
        pass
    
    def load_module_html(self, module: Literal["M2", "M3", "M4", "M5", "M6"]) -> str:
        """
        Load pre-generated HTML for specified module
        
        This is the ONLY allowed way to get module content in Phase 3
        
        Args:
            module: Module ID (M2-M6)
            
        Returns:
            Pre-generated HTML fragment for the module
            
        Raises:
            FinalReportAssemblyError: If module HTML not available
        """
        # Check cache first
        if module in self._module_html_cache:
            logger.debug(f"✅ Module {module} HTML loaded from cache")
            return self._module_html_cache[module]
        
        # Load from module HTML renderer (Phase 1 output)
        try:
            # Import here to avoid circular dependency
            from app.services.module_html_renderer import (
                render_m2_html,
                render_m3_html,
                render_m4_html,
                render_m5_html,
                render_m6_html,
            )
            from app.services.module_html_adapter import (
                adapt_m2_summary_for_html,
                adapt_m3_summary_for_html,
                adapt_m4_summary_for_html,
                adapt_m5_summary_for_html,
                adapt_m6_summary_for_html,
            )
            from app.services.context_storage import context_storage
            
            # Load frozen context
            frozen_context = context_storage.get_frozen_context(self.context_id)
            if not frozen_context:
                raise FinalReportAssemblyError(
                    f"Context {self.context_id} not found. Cannot assemble report."
                )
            
            canonical_summary = frozen_context.get("canonical_summary", {})
            
            # Get adapter and renderer for the module
            adapter_map = {
                "M2": adapt_m2_summary_for_html,
                "M3": adapt_m3_summary_for_html,
                "M4": adapt_m4_summary_for_html,
                "M5": adapt_m5_summary_for_html,
                "M6": adapt_m6_summary_for_html,
            }
            
            renderer_map = {
                "M2": render_m2_html,
                "M3": render_m3_html,
                "M4": render_m4_html,
                "M5": render_m5_html,
                "M6": render_m6_html,
            }
            
            # Adapt and render
            adapter = adapter_map.get(module)
            renderer = renderer_map.get(module)
            
            if not adapter or not renderer:
                raise FinalReportAssemblyError(f"No adapter/renderer found for {module}")
            
            normalized_data = adapter(canonical_summary)
            html_fragment = renderer(normalized_data)
            
            # Cache for reuse
            self._module_html_cache[module] = html_fragment
            
            logger.info(f"✅ Module {module} HTML loaded successfully")
            logger.info(f"   Fragment size: {len(html_fragment)} chars")
            
            return html_fragment
            
        except Exception as e:
            logger.error(f"❌ Failed to load {module} HTML: {e}")
            raise FinalReportAssemblyError(
                f"Cannot load module {module} HTML for context {self.context_id}: {e}"
            )
    
    def validate_all_modules_available(self) -> Dict[str, bool]:
        """
        Validate that all required modules have HTML available
        
        Returns:
            Dict mapping module ID to availability status
        """
        required = self.get_required_modules()
        availability = {}
        
        for module in required:
            try:
                self.load_module_html(module)
                availability[module] = True
            except Exception as e:
                logger.error(f"❌ Module {module} not available: {e}")
                availability[module] = False
        
        return availability


class FinalReportQAValidator:
    """
    QA Validator specifically for Final Reports
    
    SEPARATE from Module QA - validates report assembly AND narrative quality
    
    This validator checks:
    1. Structure QA: Modules present, sections exist
    2. Narrative QA: Decision-ready content, context provided
    3. Completeness QA: All required elements for decision-making
    """
    
    # Minimum narrative requirements per report type
    MIN_NARRATIVE_PARAGRAPHS = {
        "landowner_summary": 3,
        "lh_technical": 5,
        "quick_check": 2,
        "financial_feasibility": 4,
        "all_in_one": 6,
        "executive_summary": 4,
    }
    
    # Required decision keywords (at least one must be present)
    DECISION_KEYWORDS = [
        "GO", "NO-GO", "CONDITIONAL", "조건부",
        "승인", "불가", "권장", "비권장",
        "추천", "적합", "부적합"
    ]
    
    @staticmethod
    def validate_final_report(
        report_type: str,
        required_modules: List[str],
        available_modules: Dict[str, bool],
        html_content: str,
        has_executive_intro: bool = False,
        has_narrative_sections: bool = False
    ) -> Dict[str, any]:
        """
        Validate assembled final report
        
        Args:
            report_type: Type of report being validated
            required_modules: List of modules that should be included
            available_modules: Dict of module availability status
            html_content: Generated HTML content
            has_executive_intro: Whether executive intro section exists
            has_narrative_sections: Whether narrative sections added
            
        Returns:
            QA result dict with status and details
        """
        qa_result = {
            "report_type": report_type,
            "status": "PASS",
            "checks": [],
            "warnings": [],
            "errors": [],
            "qa_category": "Final Report (Decision-Ready Document)"
        }
        
        # ========== STRUCTURE QA ==========
        
        # Check 1: All required modules available
        missing_modules = [m for m, avail in available_modules.items() if not avail]
        if missing_modules:
            qa_result["status"] = "FAIL"
            qa_result["errors"].append(
                f"Missing required modules: {', '.join(missing_modules)}"
            )
        else:
            qa_result["checks"].append(
                f"✅ Structure: All {len(required_modules)} required modules available"
            )
        
        # Check 2: HTML content not empty
        if not html_content or len(html_content) < 1000:
            qa_result["status"] = "FAIL"
            qa_result["errors"].append("HTML content too short or empty (< 1000 chars)")
        else:
            qa_result["checks"].append(
                f"✅ Structure: HTML content generated ({len(html_content):,} chars)"
            )
        
        # Check 3: Module HTML fragments embedded
        embedded_count = 0
        for module in required_modules:
            if module in html_content:
                embedded_count += 1
        
        if embedded_count < len(required_modules):
            qa_result["warnings"].append(
                f"Only {embedded_count}/{len(required_modules)} modules clearly embedded"
            )
        else:
            qa_result["checks"].append(
                f"✅ Structure: All {embedded_count} modules embedded"
            )
        
        # ========== NARRATIVE QA ==========
        
        # Check 4: Executive intro exists
        if not has_executive_intro and report_type != "quick_check":
            qa_result["status"] = "FAIL"
            qa_result["errors"].append(
                "Missing Executive Introduction section (required for decision context)"
            )
        else:
            qa_result["checks"].append("✅ Narrative: Executive intro present")
        
        # Check 5: Minimum narrative paragraphs
        min_required = FinalReportQAValidator.MIN_NARRATIVE_PARAGRAPHS.get(report_type, 3)
        # Count <p> tags or narrative sections
        narrative_count = html_content.count("<p") + html_content.count("narrative-section")
        
        if narrative_count < min_required:
            qa_result["warnings"].append(
                f"Narrative content may be insufficient: {narrative_count} paragraphs "
                f"(minimum {min_required} recommended for {report_type})"
            )
        else:
            qa_result["checks"].append(
                f"✅ Narrative: {narrative_count} narrative elements (≥{min_required} required)"
            )
        
        # Check 6: Decision keywords present
        decision_found = False
        found_keywords = []
        for keyword in FinalReportQAValidator.DECISION_KEYWORDS:
            if keyword in html_content.upper() or keyword in html_content:
                decision_found = True
                found_keywords.append(keyword)
        
        if not decision_found:
            qa_result["status"] = "FAIL"
            qa_result["errors"].append(
                "No decision indicator found (GO/NO-GO/CONDITIONAL/승인/불가 etc.). "
                "Report must provide clear decision guidance."
            )
        else:
            qa_result["checks"].append(
                f"✅ Decision: Clear decision indicators present ({', '.join(found_keywords[:2])})"
            )
        
        # ========== COMPLETENESS QA ==========
        
        # Check 7: Report-specific sections
        required_sections = ["cover", "qa_metadata"]
        missing_sections = [s for s in required_sections if s not in html_content.lower()]
        
        if missing_sections:
            qa_result["warnings"].append(
                f"Missing recommended sections: {', '.join(missing_sections)}"
            )
        else:
            qa_result["checks"].append("✅ Completeness: All standard sections present")
        
        # Check 8: Risk notice (for reports with financial content)
        if any(m in required_modules for m in ["M2", "M5"]):
            if "risk" not in html_content.lower() and "리스크" not in html_content:
                qa_result["warnings"].append(
                    "Financial reports should include risk notices"
                )
            else:
                qa_result["checks"].append("✅ Completeness: Risk notice included")
        
        # ========== FINAL STATUS ==========
        
        # Summary counts
        qa_result["summary"] = {
            "total_checks": len(qa_result["checks"]),
            "total_warnings": len(qa_result["warnings"]),
            "total_errors": len(qa_result["errors"]),
            "pass_rate": len(qa_result["checks"]) / (len(qa_result["checks"]) + len(qa_result["errors"]) + 1) * 100
        }
        
        # If we have errors, status is FAIL
        if qa_result["errors"]:
            qa_result["status"] = "FAIL"
        # If we have too many warnings, status is WARNING
        elif len(qa_result["warnings"]) > 3:
            qa_result["status"] = "WARNING"
        
        return qa_result


# Module-level validation function
def validate_phase3_compliance(func):
    """
    Decorator to validate Phase 3 compliance for methods
    
    Ensures no forbidden operations are performed
    """
    def wrapper(self, *args, **kwargs):
        # Check method name
        if hasattr(self, '_enforce_no_calculation'):
            self._enforce_no_calculation(func.__name__)
        
        # Execute
        result = func(self, *args, **kwargs)
        
        return result
    
    return wrapper
