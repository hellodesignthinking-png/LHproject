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
        m3_html_raw = self.load_module_html("M3")
        m4_html_raw = self.load_module_html("M4")
        m6_html_raw = self.load_module_html("M6")

        # [FIX 1] Sanitize module HTML (remove N/A placeholders)
        m3_html = self.sanitize_module_html(m3_html_raw, "M3")
        m4_html = self.sanitize_module_html(m4_html_raw, "M4")
        m6_html = self.sanitize_module_html(m6_html_raw, "M6")
                
        modules_data = self._extract_module_data({"M3": m3_html, "M4": m4_html, "M6": m6_html})
        
        # [FIX 2] Generate KPI Summary Box (Mandatory for lh_technical)
        kpis = {
            "선호 유형": modules_data.get("M3", {}).get("recommended_type", "분석 미완료"),
            "계획 세대수": modules_data.get("M4", {}).get("household_count"),
            "LH 심사 결과": modules_data.get("M6", {}).get("decision", "분석 미완료")
        }
        kpi_summary = self.generate_kpi_summary_box(kpis, self.report_type)
        
        exec_summary = self.narrative.executive_summary(modules_data)
        transition_m3_m4 = self.narrative.transitions("M3", "M4")
        transition_m4_m6 = self.narrative.transitions("M4", "M6")
        final_judgment = self.narrative.final_judgment(modules_data)
        
        # [FIX 5] Generate Decision Block (Clear Visual Conclusion)
        judgment_text = self._determine_judgment(modules_data)
        basis = self._generate_judgment_basis(modules_data)
        actions = self._generate_next_actions(modules_data)
        decision_block = self.generate_decision_block(judgment_text, basis, actions)
        
        
        sections = [
            self._generate_cover_page(),
            kpi_summary,  # KPI at top
            exec_summary,
            self._wrap_module_html("M3", m3_html),
            transition_m3_m4,
            self._wrap_module_html("M4", m4_html),
            transition_m4_m6,
            self._wrap_module_html("M6", m6_html),
            final_judgment,
            decision_block,  # Visual decision at bottom
            self._generate_footer()
        ]
        
        # Wrap in HTML document
        html_content = self._wrap_in_document(sections)
        
        # [PROMPT 3.5-3] Insert QA Summary Page
        html_with_qa, qa_result = self.generate_and_insert_qa_summary(
            html_content=html_content,
            report_type=self.report_type,
            modules_data=modules_data
        )
        
        logger.info(
            f"[LHTechnical] Assembly complete with QA Summary "
            f"({len(html_with_qa):,} chars, QA Status: {qa_result['status']})"
        )
        
        return {"html": html_with_qa, "qa_result": qa_result}
    
    def _determine_judgment(self, modules_data: Dict) -> str:
        """Determine final judgment text based on module data"""
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        
        is_profitable = m5_data.get("is_profitable", False)
        lh_decision = m6_data.get("decision", "")
        
        if is_profitable and "승인" in lh_decision:
            return "사업 추진 권장"
        elif "조건부" in lh_decision:
            return "조건부 사업 추진"
        elif not is_profitable:
            return "사업 재검토 필요"
        else:
            return "추가 분석 필요"
    
    def _generate_judgment_basis(self, modules_data: Dict) -> list:
        """Generate judgment basis points"""
        basis = []
        
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        
        # Profitability
        npv = m5_data.get("npv")
        if npv and npv > 0:
            basis.append(f"수익성: NPV {self.format_number(npv, 'currency')} (양호)")
        elif npv and npv <= 0:
            basis.append(f"수익성: NPV {self.format_number(npv, 'currency')} (부정적)")
        else:
            basis.append("수익성: 분석 데이터 부족")
        
        # LH Decision
        lh_decision = m6_data.get("decision", "분석 미완료")
        basis.append(f"LH 승인 가능성: {lh_decision}")
        
        # Risk assessment
        basis.append("주요 리스크: 시장 변동성, 인허가 지연 가능성")
        
        return basis
    
    def _generate_next_actions(self, modules_data: Dict) -> list:
        """Generate next action items"""
        actions = []
        
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        
        is_profitable = m5_data.get("is_profitable", False)
        lh_decision = m6_data.get("decision", "")
        
        if is_profitable and "승인" in lh_decision:
            actions.append("LH 사전 협의 진행")
            actions.append("설계 용역 발주 준비")
        elif "조건부" in lh_decision:
            actions.append("LH 지적 사항 보완")
            actions.append("재분석 후 재제출 검토")
        else:
            actions.append("사업 계획 전면 재검토")
            actions.append("대안 부지 탐색")
        
        return actions


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
        """[FIX 4] Report CSS with unified design system"""
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
        return base_css + self.get_unified_design_css() + self.get_zerosite_watermark_css() + self.get_copyright_footer_css()
