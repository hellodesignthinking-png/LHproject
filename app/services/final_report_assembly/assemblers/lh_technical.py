"""
LH Technical Review Report Assembler (PROMPT 6)
================================================

Target Audience: LH 심사역 (기술 검토자)
Goal: LH 정책 부합성 + 기술적 실현 가능성 검토
Modules: M3 (선호유형), M4 (건축규모), M6 (LH심사)

ASSEMBLY ONLY - NO CALCULATION
"""

from typing import Dict, List, Literal
import logging

from ..base_assembler import BaseFinalReportAssembler
from ..narrative_generator import NarrativeGeneratorFactory
from ..report_type_configs import REPORT_TYPE_CONFIGS

logger = logging.getLogger(__name__)


class LHTechnicalAssembler(BaseFinalReportAssembler):
    """LH Technical Review Report Assembler"""
    
    def __init__(self, context_id: str):
        super().__init__(context_id)
        self.report_type = "lh_technical"
        self.config = REPORT_TYPE_CONFIGS[self.report_type]
        self.narrative = NarrativeGeneratorFactory.get(self.report_type)
    
    def get_required_modules(self) -> List[Literal["M2", "M3", "M4", "M5", "M6"]]:
        return ["M3", "M4", "M6"]
    
    def assemble(self) -> Dict[str, str]:
        """Assemble LH Technical Report"""
        m3_html = self.load_module_html("M3")
        m4_html = self.load_module_html("M4")
        m6_html = self.load_module_html("M6")
        
        modules_data = self._extract_module_data({"M3": m3_html, "M4": m4_html, "M6": m6_html})
        
        exec_summary = self.narrative.executive_summary(modules_data)
        transition_m3_m4 = self.narrative.transitions("M3", "M4")
        transition_m4_m6 = self.narrative.transitions("M4", "M6")
        final_judgment = self.narrative.final_judgment(modules_data)
        
        sections = [
            self._generate_cover_page(),
            exec_summary,
            self._wrap_module("M3", m3_html),
            transition_m3_m4,
            self._wrap_module("M4", m4_html),
            transition_m4_m6,
            self._wrap_module("M6", m6_html),
            final_judgment,
            self._generate_footer()
        ]
        
        return {"html": self._wrap_in_document(sections)}
    
    def _extract_module_data(self, module_htmls: Dict[str, str]) -> Dict:
        import re
        modules_data = {}
        
        # M3: Extract recommended type and score
        m3_html = module_htmls.get("M3", "")
        type_keywords = ["청년형", "일반형", "신혼부부형"]
        for keyword in type_keywords:
            if keyword in m3_html:
                modules_data["M3"] = {"recommended_type": keyword}
                break
        
        score_match = re.search(r'(\d+)\s*점', m3_html)
        if score_match and "M3" in modules_data:
            modules_data["M3"]["score"] = int(score_match.group(1))
        
        # M4: Extract household count
        m4_html = module_htmls.get("M4", "")
        household_match = re.search(r'(\d+)\s*세대', m4_html)
        if household_match:
            modules_data["M4"] = {"household_count": int(household_match.group(1))}
        
        # M6: Extract decision
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
        </section>
        """
    
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
        .cover-page { text-align: center; padding: 100px 20px; border-bottom: 2px solid #007bff; }
        .narrative { margin: 20px 0; padding: 15px; background: #f8f9fa; }
        .module-section { margin: 30px 0; padding: 20px; border: 1px solid #dee2e6; }
        """
        
        # Add watermark and copyright CSS
        return base_css + self.get_zerosite_watermark_css() + self.get_copyright_footer_css()
