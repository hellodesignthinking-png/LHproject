"""
All-in-One Comprehensive Report Assembler (PROMPT 6)
=====================================================

Target Audience: 전체 (종합 보고서)
Goal: 모든 모듈 포괄적 분석
Modules: M2, M3, M4, M5, M6 (ALL)

ASSEMBLY ONLY - NO CALCULATION
"""

from typing import Dict, List, Literal
import logging

from ..base_assembler import BaseFinalReportAssembler
from ..narrative_generator import NarrativeGeneratorFactory
from ..report_type_configs import REPORT_TYPE_CONFIGS

logger = logging.getLogger(__name__)


class AllInOneAssembler(BaseFinalReportAssembler):
    """All-in-One Comprehensive Report Assembler"""
    
    def __init__(self, context_id: str):
        super().__init__(context_id)
        self.report_type = "all_in_one"
        self.config = REPORT_TYPE_CONFIGS[self.report_type]
        self.narrative = NarrativeGeneratorFactory.get(self.report_type)
    
    def get_required_modules(self) -> List[Literal["M2", "M3", "M4", "M5", "M6"]]:
        return ["M2", "M3", "M4", "M5", "M6"]
    
    def assemble(self) -> Dict[str, str]:
        """Assemble All-in-One Comprehensive Report"""
        m2_html = self.load_module_html("M2")
        m3_html = self.load_module_html("M3")
        m4_html = self.load_module_html("M4")
        m5_html = self.load_module_html("M5")
        m6_html = self.load_module_html("M6")
        
        modules_data = self._extract_module_data({
            "M2": m2_html, "M3": m3_html, "M4": m4_html,
            "M5": m5_html, "M6": m6_html
        })
        
        exec_summary = self.narrative.executive_summary(modules_data)
        transitions = {
            "M2_M3": self.narrative.transitions("M2", "M3"),
            "M3_M4": self.narrative.transitions("M3", "M4"),
            "M4_M5": self.narrative.transitions("M4", "M5"),
            "M5_M6": self.narrative.transitions("M5", "M6")
        }
        final_judgment = self.narrative.final_judgment(modules_data)
        
        sections = [
            self._generate_cover_page(),
            exec_summary,
            self._wrap_module("M2", m2_html),
            transitions["M2_M3"],
            self._wrap_module("M3", m3_html),
            transitions["M3_M4"],
            self._wrap_module("M4", m4_html),
            transitions["M4_M5"],
            self._wrap_module("M5", m5_html),
            transitions["M5_M6"],
            self._wrap_module("M6", m6_html),
            final_judgment,
            self._generate_footer()
        ]
        
        return {"html": self._wrap_in_document(sections)}
    
    def _extract_module_data(self, module_htmls: Dict[str, str]) -> Dict:
        import re
        modules_data = {}
        
        # Extract minimal data from each module
        m5_html = module_htmls.get("M5", "")
        npv_match = re.search(r'NPV[:\s]*([+-]?\d{1,3}(?:,\d{3})*)', m5_html, re.IGNORECASE)
        if npv_match:
            modules_data["M5"] = {"npv": int(npv_match.group(1).replace(",", ""))}
        
        m6_html = module_htmls.get("M6", "")
        for keyword in ["승인", "조건부 승인", "부적합"]:
            if keyword in m6_html:
                modules_data["M6"] = {"decision": keyword}
                break
        
        return modules_data
    
    def _generate_cover_page(self) -> str:
        return f"""
        <section class="cover-page">
            <h1>{self.config.name_kr}</h1>
            <p class="subtitle">{self.config.description}</p>
            <p class="meta">분석 ID: {self.context_id}</p>
            <p class="meta">포함 모듈: M2, M3, M4, M5, M6 (전체)</p>
        </section>
        """
    
    def _wrap_module(self, module_id: str, html: str) -> str:
        return f'<section class="module-section" data-module="{module_id}">{html}</section>'
    
    def _generate_footer(self) -> str:
        return '<footer class="report-footer"><p>본 보고서는 종합 분석 시스템에 의해 자동 생성되었습니다.</p></footer>'
    
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
