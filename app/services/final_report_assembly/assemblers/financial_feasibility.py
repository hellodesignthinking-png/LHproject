"""
Financial Feasibility Report Assembler (PROMPT 6)
==================================================

Target Audience: 투자자 / 재무 담당자
Goal: 재무적 타당성 검토 (ROI, NPV, IRR)
Modules: M2 (토지가치), M4 (사업규모), M5 (사업성)

ASSEMBLY ONLY - NO CALCULATION
"""

from typing import Dict, List, Literal
import logging

from ..base_assembler import BaseFinalReportAssembler
from ..narrative_generator import NarrativeGeneratorFactory
from ..report_type_configs import REPORT_TYPE_CONFIGS

logger = logging.getLogger(__name__)


class FinancialFeasibilityAssembler(BaseFinalReportAssembler):
    """Financial Feasibility Report Assembler"""
    
    def __init__(self, context_id: str):
        super().__init__(context_id)
        self.report_type = "financial_feasibility"
        self.config = REPORT_TYPE_CONFIGS[self.report_type]
        self.narrative = NarrativeGeneratorFactory.get(self.report_type)
    
    def get_required_modules(self) -> List[Literal["M2", "M3", "M4", "M5", "M6"]]:
        return ["M2", "M4", "M5"]
    
    def assemble(self) -> Dict[str, str]:
        """Assemble Financial Feasibility Report"""
        m2_html = self.load_module_html("M2")
        m4_html = self.load_module_html("M4")
        m5_html = self.load_module_html("M5")
        
        modules_data = self._extract_module_data({"M2": m2_html, "M4": m4_html, "M5": m5_html})
        
        exec_summary = self.narrative.executive_summary(modules_data)
        transition_m2_m4 = self.narrative.transitions("M2", "M4")
        transition_m4_m5 = self.narrative.transitions("M4", "M5")
        final_judgment = self.narrative.final_judgment(modules_data)
        
        sections = [
            self._generate_cover_page(),
            exec_summary,
            self._wrap_module("M2", m2_html),
            transition_m2_m4,
            self._wrap_module("M4", m4_html),
            transition_m4_m5,
            self._wrap_module("M5", m5_html),
            final_judgment,
            self._generate_footer()
        ]
        
        return {"html": self._wrap_in_document(sections)}
    
    def _extract_module_data(self, module_htmls: Dict[str, str]) -> Dict:
        import re
        modules_data = {}
        
        # M2: Land value
        m2_html = module_htmls.get("M2", "")
        land_value_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*원', m2_html)
        if land_value_match:
            land_value_str = land_value_match.group(1).replace(",", "")
            modules_data["M2"] = {"land_value": int(land_value_str)}
        
        # M5: NPV, IRR
        m5_html = module_htmls.get("M5", "")
        npv_match = re.search(r'NPV[:\s]*([+-]?\d{1,3}(?:,\d{3})*)', m5_html, re.IGNORECASE)
        irr_match = re.search(r'IRR[:\s]*([\d.]+)\s*%', m5_html, re.IGNORECASE)
        
        if npv_match or irr_match:
            modules_data["M5"] = {}
            if npv_match:
                modules_data["M5"]["npv"] = int(npv_match.group(1).replace(",", ""))
            if irr_match:
                modules_data["M5"]["irr"] = float(irr_match.group(1))
        
        return modules_data
    
    def _generate_cover_page(self) -> str:
        return f"""
        <section class="cover-page">
            <h1>{self.config.name_kr}</h1>
            <p class="subtitle">{self.config.description}</p>
            <p class="meta">분석 ID: {self.context_id}</p>
        </section>
        """
    
    def _wrap_module(self, module_id: str, html: str) -> str:
        return f'<section class="module-section" data-module="{module_id}">{html}</section>'
    
    def _generate_footer(self) -> str:
        return '<footer class="report-footer"><p>본 보고서는 재무 분석 시스템에 의해 자동 생성되었습니다.</p></footer>'
    
    def _wrap_in_document(self, sections: List[str]) -> str:
        return f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>{self.config.name_kr}</title>
        </head>
        <body class="final-report {self.report_type}">
            {"".join(sections)}
        </body>
        </html>
        """
