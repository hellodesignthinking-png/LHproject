"""
Landowner Summary Report Assembler (PROMPT 6)
==============================================

Target Audience: 토지주 (일반인)
Goal: 사업 추진 여부 의사결정 지원
Modules: M2 (토지평가), M5 (사업성), M6 (LH심사)

ASSEMBLY ONLY - NO CALCULATION
"""

from typing import Dict, List, Literal
import logging

from ..base_assembler import BaseFinalReportAssembler
from ..narrative_generator import NarrativeGeneratorFactory
from ..report_type_configs import REPORT_TYPE_CONFIGS

logger = logging.getLogger(__name__)


class LandownerSummaryAssembler(BaseFinalReportAssembler):
    """
    Landowner Summary Report Assembler
    
    Assembles: Executive Summary + M2 + M5 + M6 + Final Judgment
    
    PROMPT 6 Requirements:
    - Use NarrativeGenerator for story elements
    - Load module HTML (no calculation)
    - Assemble in fixed order
    - ~100 lines total
    """
    
    def __init__(self, context_id: str):
        super().__init__(context_id)
        self.report_type = "landowner_summary"
        self.config = REPORT_TYPE_CONFIGS[self.report_type]
        self.narrative = NarrativeGeneratorFactory.get(self.report_type)
        
        logger.info(f"[LandownerSummary] Initialized for context {context_id}")
    
    def get_required_modules(self) -> List[Literal["M2", "M3", "M4", "M5", "M6"]]:
        """Required modules: M2, M5, M6"""
        return ["M2", "M5", "M6"]
    
    def assemble(self) -> Dict[str, str]:
        """
        Assemble Landowner Summary Report
        
        Order:
        1. Cover Page
        2. Executive Summary (Narrative)
        3. M2 (토지평가)
        4. Transition (M2 → M5)
        5. M5 (사업성)
        6. Transition (M5 → M6)
        7. M6 (LH심사)
        8. Final Judgment (Narrative)
        9. Footer
        """
        logger.info(f"[LandownerSummary] Starting assembly for {self.context_id}")
        
        # Load module HTML fragments
        m2_html = self.load_module_html("M2")
        m5_html = self.load_module_html("M5")
        m6_html = self.load_module_html("M6")
        
        # Extract module data for narrative generation
        modules_data = self._extract_module_data({"M2": m2_html, "M5": m5_html, "M6": m6_html})
        
        # Generate narrative elements
        exec_summary = self.narrative.executive_summary(modules_data)
        transition_m2_m5 = self.narrative.transitions("M2", "M5")
        transition_m5_m6 = self.narrative.transitions("M5", "M6")
        final_judgment = self.narrative.final_judgment(modules_data)
        
        # Assemble sections
        sections = [
            self._generate_cover_page(),
            exec_summary,
            self._wrap_module_html("M2", m2_html),
            transition_m2_m5,
            self._wrap_module_html("M5", m5_html),
            transition_m5_m6,
            self._wrap_module_html("M6", m6_html),
            final_judgment,
            self._generate_footer()
        ]
        
        # Wrap in HTML document
        html_content = self._wrap_in_document(sections)
        
        logger.info(f"[LandownerSummary] Assembly complete ({len(html_content):,} chars)")
        
        return {"html": html_content}
    
    def _extract_module_data(self, module_htmls: Dict[str, str]) -> Dict:
        """
        Extract minimal data from module HTML for narrative generation
        
        NOTE: This is NOT calculation - just extracting displayed values
        """
        import re
        
        modules_data = {}
        
        # Extract M2 land value
        m2_html = module_htmls.get("M2", "")
        land_value_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*원', m2_html)
        if land_value_match:
            land_value_str = land_value_match.group(1).replace(",", "")
            modules_data["M2"] = {"land_value": int(land_value_str)}
        
        # Extract M5 data
        m5_html = module_htmls.get("M5", "")
        npv_match = re.search(r'NPV[:\s]*([+-]?\d{1,3}(?:,\d{3})*)\s*원', m5_html, re.IGNORECASE)
        if npv_match:
            npv_str = npv_match.group(1).replace(",", "")
            modules_data["M5"] = {"npv": int(npv_str), "is_profitable": int(npv_str) > 0}
        
        # Extract M6 decision
        m6_html = module_htmls.get("M6", "")
        decision_keywords = ["승인", "조건부 승인", "부적합", "탈락"]
        for keyword in decision_keywords:
            if keyword in m6_html:
                modules_data["M6"] = {"decision": keyword}
                break
        
        return modules_data
    
    def _generate_cover_page(self) -> str:
        """Generate title page"""
        return f"""
        <section class="cover-page">
            <h1>{self.config.name_kr}</h1>
            <p class="subtitle">{self.config.description}</p>
            <p class="meta">분석 ID: {self.context_id}</p>
            <p class="meta">대상: {self.config.target_audience}</p>
        </section>
        """
    
    def _wrap_module_html(self, module_id: str, html: str) -> str:
        """Wrap module HTML in section container"""
        return f"""
        <section class="module-section" data-module="{module_id}">
            {html}
        </section>
        """
    
    def _generate_footer(self) -> str:
        """Standard disclaimer"""
        return """
        <footer class="report-footer">
            <p class="disclaimer">
                본 보고서는 ZeroSite 시스템에 의해 자동 생성되었습니다.
                최종 의사결정 시 전문가 자문을 권장합니다.
            </p>
        </footer>
        """
    
    def _wrap_in_document(self, sections: List[str]) -> str:
        """Wrap all sections in HTML document"""
        return f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>{self.config.name_kr}</title>
            <style>{self._get_report_css()}</style>
        </head>
        <body class="final-report {self.report_type}">
            {"".join(sections)}
        </body>
        </html>
        """
    
    def _get_report_css(self) -> str:
        """Report-specific CSS"""
        return """
        body.final-report {
            font-family: 'Noto Sans KR', sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .cover-page {
            text-align: center;
            padding: 100px 20px;
            border-bottom: 2px solid #007bff;
        }
        .narrative {
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
        }
        .executive-summary {
            background: #e3f2fd;
            padding: 30px;
            border-left: 4px solid #007bff;
        }
        .final-judgment {
            background: #fff3cd;
            padding: 30px;
            border-left: 4px solid #ffc107;
        }
        .judgment {
            font-size: 1.2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .module-section {
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #dee2e6;
        }
        .transition {
            font-style: italic;
            color: #666;
            margin: 20px 0;
        }
        .report-footer {
            margin-top: 50px;
            padding: 20px;
            text-align: center;
            color: #999;
            border-top: 1px solid #ddd;
        }
        """
