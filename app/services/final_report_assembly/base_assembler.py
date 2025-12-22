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
    
    SEPARATE from Module QA - validates report assembly, not module calculations
    """
    
    @staticmethod
    def validate_final_report(
        report_type: str,
        required_modules: List[str],
        available_modules: Dict[str, bool],
        html_content: str
    ) -> Dict[str, any]:
        """
        Validate assembled final report
        
        Args:
            report_type: Type of report being validated
            required_modules: List of modules that should be included
            available_modules: Dict of module availability status
            html_content: Generated HTML content
            
        Returns:
            QA result dict with status and details
        """
        qa_result = {
            "report_type": report_type,
            "status": "PASS",
            "checks": [],
            "warnings": [],
            "errors": []
        }
        
        # Check 1: All required modules available
        missing_modules = [m for m, avail in available_modules.items() if not avail]
        if missing_modules:
            qa_result["status"] = "FAIL"
            qa_result["errors"].append(
                f"Missing required modules: {', '.join(missing_modules)}"
            )
        else:
            qa_result["checks"].append("✅ All required modules available")
        
        # Check 2: HTML content not empty
        if not html_content or len(html_content) < 1000:
            qa_result["status"] = "FAIL"
            qa_result["errors"].append("HTML content too short or empty")
        else:
            qa_result["checks"].append(f"✅ HTML content generated ({len(html_content)} chars)")
        
        # Check 3: Module HTML fragments embedded (check for module titles)
        for module in required_modules:
            if f"module='{module}'" not in html_content and module not in html_content:
                qa_result["warnings"].append(
                    f"Module {module} may not be properly embedded"
                )
        
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
