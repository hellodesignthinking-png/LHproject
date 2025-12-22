"""
Quick Check Report Assembler (PROMPT 6)
========================================

Target Audience: 의사결정권자 (빠른 GO/NO-GO 판단)
Goal: 5분 내 핵심 결론 확인
Modules: M5 (사업성), M6 (LH심사)

ASSEMBLY ONLY - NO CALCULATION
"""

from typing import Dict, List, Literal
import logging

from ..base_assembler import BaseFinalReportAssembler
from ..narrative_generator import NarrativeGeneratorFactory
from ..report_type_configs import REPORT_TYPE_CONFIGS

logger = logging.getLogger(__name__)


class QuickCheckAssembler(BaseFinalReportAssembler):
    """Quick Check Report Assembler - Minimal, Fast Decision"""
    
    def __init__(self, context_id: str):
        super().__init__(context_id)
        self.report_type = "quick_check"
        self.config = REPORT_TYPE_CONFIGS[self.report_type]
        self.narrative = NarrativeGeneratorFactory.get(self.report_type)
    
    def get_required_modules(self) -> List[Literal["M2", "M3", "M4", "M5", "M6"]]:
        return ["M5", "M6"]
    
    def assemble(self) -> Dict[str, str]:
        """Assemble Quick Check Report (Minimal)"""
        m5_html = self.load_module_html("M5")
        m6_html = self.load_module_html("M6")
        
        modules_data = self._extract_module_data({"M5": m5_html, "M6": m6_html})
        
        exec_summary = self.narrative.executive_summary(modules_data)
        final_judgment = self.narrative.final_judgment(modules_data)
        
        sections = [
            exec_summary,
            self._wrap_module("M5", m5_html),
            self._wrap_module("M6", m6_html),
            final_judgment,
            self._generate_footer()
        ]
        
        return {"html": self._wrap_in_document(sections)}
    
    def _extract_module_data(self, module_htmls: Dict[str, str]) -> Dict:
        import re
        modules_data = {}
        
        # M5: NPV
        m5_html = module_htmls.get("M5", "")
        npv_match = re.search(r'NPV[:\s]*([+-]?\d{1,3}(?:,\d{3})*)', m5_html, re.IGNORECASE)
        if npv_match:
            npv_str = npv_match.group(1).replace(",", "")
            modules_data["M5"] = {"npv": int(npv_str)}
        
        # M6: Decision
        m6_html = module_htmls.get("M6", "")
        for keyword in ["승인", "조건부 승인", "부적합"]:
            if keyword in m6_html:
                modules_data["M6"] = {"decision": keyword}
                break
        
        return modules_data
    
    def _wrap_module(self, module_id: str, html: str) -> str:
        return f'<section class="module-section" data-module="{module_id}">{html}</section>'
    
    def _generate_footer(self) -> str:
        """[PROMPT 3.5-2] ZEROSITE Copyright Footer"""
        return self.get_zerosite_copyright_footer(
            report_type=self.report_type,
            context_id=self.context_id
        )
    
    def _wrap_in_document(self, sections: List[str]) -> str:
        return f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>{self.config.name_kr}</title>
            <style>
            {self._get_report_css()}
            </style>
        </head>
        <body class="final-report {self.report_type}">
            {"".join(sections)}
        </body>
        </html>
        """
    
    def _get_report_css(self) -> str:
        """[PROMPT 3.5-2] Report CSS with watermark and copyright"""
        base_css = """
        body.final-report {
            font-family: 'Noto Sans KR', sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .narrative { margin: 20px 0; padding: 15px; background: #f8f9fa; }
        .module-section { margin: 30px 0; padding: 20px; border: 1px solid #dee2e6; }
        """
        
        # Add watermark and copyright CSS
        return base_css + self.get_zerosite_watermark_css() + self.get_copyright_footer_css()
