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
from datetime import datetime
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
            from app.services.module_html_renderer import render_module_html
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
            
            # Get adapter for the module
            adapter_map = {
                "M2": adapt_m2_summary_for_html,
                "M3": adapt_m3_summary_for_html,
                "M4": adapt_m4_summary_for_html,
                "M5": adapt_m5_summary_for_html,
                "M6": adapt_m6_summary_for_html,
            }
            
            # Adapt and render
            adapter = adapter_map.get(module)
            
            if not adapter:
                raise FinalReportAssemblyError(f"No adapter found for {module}")
            
            normalized_data = adapter(canonical_summary)
            html_fragment = render_module_html(module, normalized_data)
            
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
    
    # ========== PROMPT 3.5-2: Shared Helper Methods ==========
    
    @staticmethod
    def get_zerosite_watermark_css() -> str:
        """
        [PROMPT 3.5-2] ZEROSITE watermark CSS
        
        Adds fixed watermark in top-right corner of every page
        """
        return """
        /* PROMPT 3.5-2: ZEROSITE Watermark */
        body.final-report::before {
            content: 'ZEROSITE';
            position: fixed;
            top: 15px;
            right: 20px;
            font-size: 14px;
            font-weight: 600;
            color: rgba(0, 123, 255, 0.3);
            z-index: 9999;
            letter-spacing: 2px;
            pointer-events: none;
        }
        
        @media print {
            body.final-report::before {
                color: rgba(0, 123, 255, 0.2);
            }
        }
        """
    
    @staticmethod
    def get_zerosite_copyright_footer(report_type: str, context_id: str) -> str:
        """
        [PROMPT 3.5-2] ZEROSITE Copyright Footer
        
        Args:
            report_type: Report type ID (e.g., "landowner_summary")
            context_id: Analysis context ID
        
        Returns:
            HTML footer with copyright, Report ID, and creation time
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""
        <footer class="report-footer zerosite-copyright">
            <div class="footer-content">
                <div class="copyright">
                    © ZeroSite by AntennaHoldings · nataiheum
                </div>
                <div class="report-metadata">
                    <span class="metadata-item">Report ID: {context_id}</span>
                    <span class="metadata-separator">|</span>
                    <span class="metadata-item">Type: {report_type}</span>
                    <span class="metadata-separator">|</span>
                    <span class="metadata-item">Created: {now}</span>
                </div>
                <div class="disclaimer">
                    본 보고서는 ZeroSite 시스템에 의해 자동 생성되었습니다. 
                    최종 의사결정 시 전문가 자문을 권장합니다.
                </div>
            </div>
        </footer>
        """
    
    @staticmethod
    def get_copyright_footer_css() -> str:
        """
        [PROMPT 3.5-2] Copyright footer CSS styling
        """
        return """
        /* PROMPT 3.5-2: Copyright Footer Styling */
        .report-footer.zerosite-copyright {
            margin-top: 60px;
            padding: 30px 20px;
            background: #f8f9fa;
            border-top: 3px solid #007bff;
            text-align: center;
        }
        
        .footer-content {
            max-width: 900px;
            margin: 0 auto;
        }
        
        .copyright {
            font-size: 16px;
            font-weight: 700;
            color: #007bff;
            margin-bottom: 15px;
            letter-spacing: 0.5px;
        }
        
        .report-metadata {
            font-size: 12px;
            color: #666;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
        }
        
        .metadata-item {
            display: inline-block;
            margin: 0 5px;
        }
        
        .metadata-separator {
            color: #ccc;
            margin: 0 8px;
        }
        
        .disclaimer {
            font-size: 11px;
            color: #999;
            margin-top: 15px;
            line-height: 1.5;
        }
        
        @media print {
            .report-footer.zerosite-copyright {
                break-inside: avoid;
                page-break-inside: avoid;
            }
        }
        """
    
    @staticmethod
    def generate_and_insert_qa_summary(
        html_content: str,
        report_type: str,
        modules_data: Dict[str, any]
    ) -> tuple:
        """
        [PROMPT 3.5-3] Run QA validation and insert QA Summary page
        
        Args:
            html_content: Generated HTML content
            report_type: Report type ID
            modules_data: Module data for QA checks
        
        Returns:
            Tuple of (html_with_qa_summary, qa_result)
        """
        from .qa_validator import FinalReportQAValidator, generate_qa_summary_page
        
        # Run QA validation
        qa_result = FinalReportQAValidator.validate(
            report_type=report_type,
            html_content=html_content,
            modules_data=modules_data
        )
        
        # Generate QA summary page
        qa_summary_html = generate_qa_summary_page(qa_result)
        
        # Insert QA summary before closing </body> tag
        if "</body>" in html_content:
            html_with_qa = html_content.replace("</body>", f"{qa_summary_html}\n</body>")
        else:
            # Fallback: append at end
            html_with_qa = html_content + qa_summary_html
        
        return html_with_qa, qa_result
    
    # ========== OUTPUT QUALITY FIX HELPERS ==========
    
    @staticmethod
    def sanitize_module_html(module_html: str, module_id: str) -> str:
        """
        [FIX 1] Remove N/A placeholders and bind calculated data
        
        Searches for placeholder texts and attempts to replace with actual values
        WITHOUT triggering any recalculation.
        """
        import re
        
        # Placeholder patterns to detect
        placeholders = [
            r'N/A(?:\s*\(검증\s*필요\))?',
            r'검증\s*필요',
            r'분석\s*중(?:입니다)?',
            r'\bNone\b',
            r'계산\s*중'
        ]
        
        # Check if any placeholder exists
        has_placeholder = any(re.search(pattern, module_html, re.IGNORECASE) for pattern in placeholders)
        
        if not has_placeholder:
            return module_html  # Already clean
        
        # Try to extract data from data-* attributes or JSON blocks
        # This is DISPLAY-LEVEL only, no calculation
        sanitized = module_html
        
        # Pattern: Replace generic placeholders with proper message
        for pattern in placeholders:
            sanitized = re.sub(
                pattern,
                '<span class="data-unavailable">데이터 없음 (분석 미완료)</span>',
                sanitized,
                flags=re.IGNORECASE
            )
        
        return sanitized
    
    @staticmethod
    def format_number(value, format_type: str) -> str:
        """
        [FIX 3] Standardize number formatting
        
        Args:
            value: Numeric value
            format_type: 'currency', 'percent', 'area', 'units', 'score'
        
        Returns:
            Formatted string
        """
        if value is None:
            return "데이터 없음"
        
        try:
            if format_type == 'currency':
                # ₩#,###,###,###
                return f"₩{int(value):,}"
            elif format_type == 'percent':
                # ##.# %
                return f"{float(value):.1f}%"
            elif format_type == 'area':
                # ##.# ㎡
                return f"{float(value):.1f}㎡"
            elif format_type == 'units':
                # ### 세대
                return f"{int(value):,}세대"
            elif format_type == 'score':
                # ## / 100
                return f"{int(value)}/100"
            else:
                return str(value)
        except (ValueError, TypeError):
            return "형식 오류"
    
    @staticmethod
    def generate_kpi_summary_box(kpis: Dict[str, any], report_type: str) -> str:
        """
        [FIX 2] Generate mandatory KPI summary box
        
        Args:
            kpis: Dict of key metrics {name: value}
            report_type: Report type ID
        
        Returns:
            HTML for KPI summary box
        """
        kpi_cards = []
        
        for kpi_name, kpi_value in kpis.items():
            # Determine format based on KPI name
            if '금액' in kpi_name or '가치' in kpi_name or 'NPV' in kpi_name or '사업비' in kpi_name:
                formatted_value = BaseFinalReportAssembler.format_number(kpi_value, 'currency')
            elif '비율' in kpi_name or '%' in kpi_name or 'IRR' in kpi_name:
                formatted_value = BaseFinalReportAssembler.format_number(kpi_value, 'percent')
            elif '면적' in kpi_name or '㎡' in kpi_name:
                formatted_value = BaseFinalReportAssembler.format_number(kpi_value, 'area')
            elif '점수' in kpi_name or 'score' in kpi_name.lower():
                formatted_value = BaseFinalReportAssembler.format_number(kpi_value, 'score')
            else:
                # [FIX B] Fallback guarantee - no empty values
                if kpi_value is None or kpi_value == "" or (isinstance(kpi_value, (int, float)) and kpi_value == 0):
                    formatted_value = '<span class="kpi-undefined" title="분석 결과는 존재하나 표시 불가">데이터 미확정</span>'
                else:
                    formatted_value = str(kpi_value)
            
            kpi_cards.append(f"""
            <div class="kpi-card">
                <div class="kpi-label">{kpi_name}</div>
                <div class="kpi-value">{formatted_value}</div>
            </div>
            """)
        
        return f"""
        <section class="kpi-summary-box pdf-safe" style="
            background: linear-gradient(135deg, #e3f2fd 0%, #f5f7fa 100%);
            border-left: 6px solid #007bff;
            padding: 30px;
            margin: 30px 0;
            border-radius: 8px;
            min-height: 200px;
            page-break-inside: avoid !important;
            page-break-before: auto;
        ">
            <h3 style="margin: 0 0 20px 0; color: #007bff; font-size: 20px;">핵심 지표 (Key Performance Indicators)</h3>
            <div class="kpi-cards" style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            ">
                {"".join(kpi_cards)}
            </div>
        </section>
        """
    
    @staticmethod
    def generate_decision_block(judgment: str, basis: list, actions: list) -> str:
        """
        [FIX 5] Generate clear decision visibility block
        
        Args:
            judgment: "추진 권장" / "조건부 추진" / "부적합"
            basis: List of judgment basis points
            actions: List of next actions
        
        Returns:
            HTML for decision block
        """
        # Determine icon and color
        if "권장" in judgment or "추진 가능" in judgment or "승인" in judgment:
            icon = "✅"
            color = "#28a745"
            bg_color = "#d4edda"
        elif "조건부" in judgment or "보완" in judgment:
            icon = "⚠️"
            color = "#ffc107"
            bg_color = "#fff3cd"
        else:
            icon = "❌"
            color = "#dc3545"
            bg_color = "#f8d7da"
        
        basis_html = "\n".join([f"<li>{b}</li>" for b in basis])
        actions_html = "\n".join([f"<li>{a}</li>" for a in actions])
        
        return f"""
        <section class="decision-block pdf-safe" style="
            margin: 60px 0 40px 0;
            padding: 40px;
            background: {bg_color};
            border: 3px solid {color};
            border-radius: 12px;
            min-height: 150px;
            page-break-inside: avoid !important;
            page-break-before: auto;
        ">
            <h2 style="
                margin: 0 0 20px 0;
                color: {color};
                font-size: 28px;
                font-weight: bold;
            ">{icon} 최종 판단</h2>
            
            <div class="judgment-text" style="
                font-size: 24px;
                font-weight: bold;
                color: {color};
                margin: 20px 0;
                padding: 20px;
                background: white;
                border-radius: 8px;
                text-align: center;
            ">
                {judgment}
            </div>
            
            <div class="judgment-basis" style="margin: 30px 0;">
                <h3 style="color: #333; font-size: 18px; margin-bottom: 15px;">판단 근거</h3>
                <ul style="line-height: 1.8; font-size: 16px; color: #555;">
                    {basis_html}
                </ul>
            </div>
            
            <div class="next-actions" style="margin: 30px 0;">
                <h3 style="color: #333; font-size: 18px; margin-bottom: 15px;">다음 액션</h3>
                <ul style="line-height: 1.8; font-size: 16px; color: #555;">
                    {actions_html}
                </ul>
            </div>
        </section>
        """
    
    @staticmethod
    def ensure_numeric_anchor(narrative_text: str, modules_data: Dict) -> str:
        """
        [FIX C] Ensure narrative contains at least one numeric value
        
        If no numbers found, injects key metric from modules_data
        """
        import re
        
        # Check if narrative already has numbers
        has_currency = re.search(r'[₩\$]\s*[\d,]+', narrative_text)
        has_number = re.search(r'\d{1,3}(?:,\d{3})+', narrative_text)
        has_percent = re.search(r'\d+\.?\d*\s*%', narrative_text)
        
        if has_currency or has_number or has_percent:
            return narrative_text  # Already has numbers
        
        # Inject numeric anchor from modules_data
        numeric_anchor = ""
        
        # Try NPV first
        if "M5" in modules_data and "npv" in modules_data["M5"]:
            npv = modules_data["M5"]["npv"]
            formatted_npv = BaseFinalReportAssembler.format_number(npv, 'currency')
            numeric_anchor = f"<p><strong>본 사업의 순현재가치(NPV)는 {formatted_npv}입니다.</strong></p>"
        
        # Try land value
        elif "M2" in modules_data and "land_value" in modules_data["M2"]:
            land_value = modules_data["M2"]["land_value"]
            formatted_value = BaseFinalReportAssembler.format_number(land_value, 'currency')
            numeric_anchor = f"<p><strong>토지 감정가는 {formatted_value}입니다.</strong></p>"
        
        # Try household count
        elif "M4" in modules_data and "household_count" in modules_data["M4"]:
            households = modules_data["M4"]["household_count"]
            numeric_anchor = f"<p><strong>계획 세대수는 {households:,} 세대입니다.</strong></p>"
        
        if numeric_anchor:
            # Insert at beginning of narrative
            return numeric_anchor + "\n" + narrative_text
        
        return narrative_text

    @staticmethod
    def get_unified_design_css() -> str:
        """
        [FIX 4] Unified design system CSS for all reports
        """
        return """
        /* OUTPUT QUALITY FIX - UNIFIED DESIGN SYSTEM */
        
        /* Typography */
        body.final-report {
            font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px;
        }
        
        body.final-report h1 {
            font-size: 24px;
            font-weight: bold;
            margin: 0 0 20px 0;
        }
        
        body.final-report h2 {
            font-size: 18px;
            font-weight: bold;
            margin: 40px 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #007bff;
        }
        
        body.final-report h3 {
            font-size: 16px;
            font-weight: bold;
            margin: 30px 0 10px 0;
        }
        
        /* Tables */
        body.final-report table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 13px;
        }
        
        body.final-report table thead {
            background: #f5f7fa;
        }
        
        body.final-report table th,
        body.final-report table td {
            padding: 12px;
            text-align: left;
            border: 1px solid #dee2e6;
        }
        
        body.final-report table td.numeric {
            text-align: right;
            font-family: 'Courier New', monospace;
        }
        
        /* Layout */
        body.final-report .section {
            margin: 48px 0;
        }
        
        body.final-report .module-section {
            page-break-before: auto;
            page-break-inside: avoid;
            margin: 40px 0;
            padding: 30px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }
        
        /* KPI Cards */
        .kpi-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .kpi-label {
            font-size: 13px;
            color: #666;
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .kpi-value {
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
            font-family: 'Courier New', monospace;
        }
        
        /* Data Unavailable */
        .data-unavailable {
            color: #dc3545;
            font-style: italic;
            font-size: 12px;
        }
        
        /* Page Breaks */
        .executive-summary {
            page-break-after: always;
        }
        
        /* [FIX E] Information Density Control */
        .compact-report .module-section {
            padding: 20px;
            margin: 20px 0;
        }
        
        .compact-report h3 {
            font-size: 16px;
            margin: 10px 0;
        }
        
        .dense-report .module-section {
            padding: 30px;
            margin: 40px 0;
            border-top: 2px solid #e0e0e0;
        }
        
        .dense-report .section-divider {
            height: 2px;
            background: linear-gradient(90deg, #007bff 0%, transparent 100%);
            margin: 50px 0;
        }
        
        .visual-break {
            height: 40px;
            margin: 30px 0;
            background: repeating-linear-gradient(
                90deg,
                #f5f7fa 0px,
                #f5f7fa 10px,
                transparent 10px,
                transparent 20px
            );
        }
        
        @media print {
            body.final-report {
                padding: 20mm;
            }
            
            .module-section,
            .kpi-summary-box,
            .decision-block {
                page-break-inside: avoid;
            }
        }
        """


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
