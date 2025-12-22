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
        transition_m3_m4 = self.generate_module_transition("M3", "M4", self.report_type)
        transition_m4_m6 = self.generate_module_transition("M4", "M6", self.report_type)
        final_judgment = self.narrative.final_judgment(modules_data)
        
        # [FIX 5] Generate Decision Block (Clear Visual Conclusion)
        judgment_text = self._determine_judgment(modules_data)
        basis = self._generate_judgment_basis(modules_data)
        actions = self._generate_next_actions(modules_data)
        decision_block = self.generate_decision_block(judgment_text, basis, actions)
        
        # [FIX 4] Generate Next Actions Section
        next_actions = self.generate_next_actions_section(modules_data, self.report_type)
        
        
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
            next_actions,
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
        
        if is_profitable and "추진 가능" in lh_decision:
            return "사업 추진 권장"
        elif "조건부 가능" in lh_decision:
            return "조건부 가능 사업 추진"
        elif not is_profitable:
            return "사업 재검토 필요"
        else:
            return "추가 분석 필요"
    
    def _generate_judgment_basis(self, modules_data: Dict) -> list:
        """[FIX D] Generate judgment basis with explicit numeric evidence"""
        basis = []
        
        m2_data = modules_data.get("M2", {})
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        
        # [FIX D] Profitability with explicit 순현재가치(NPV)
        npv = m5_data.get("npv")
        if npv and npv > 0:
            basis.append(f"✅ 수익성 양호: 순현재가치(NPV) {self.format_number(npv, 'currency')}")
        elif npv and npv <= 0:
            basis.append(f"❌ 수익성 부정적: 순현재가치(NPV) {self.format_number(npv, 'currency')}")
        else:
            basis.append("⚠️ 수익성: 분석 데이터 부족")
        
        # [FIX D] LH Decision with explicit status
        lh_decision = m6_data.get("decision", "분석 미완료")
        if "추진 가능" in lh_decision:
            basis.append(f"✅ LH 심사: {lh_decision}")
        elif "조건부 가능" in lh_decision:
            basis.append(f"⚠️ LH 심사: {lh_decision}")
        else:
            basis.append(f"❌ LH 심사: {lh_decision}")
        
        # [FIX D] Land value reference (if available)
        land_value = m2_data.get("land_value")
        if land_value and land_value > 0:
            basis.append(f"📊 토지 기준가: {self.format_number(land_value, 'currency')}")
        
        return basis
    
    def _generate_next_actions(self, modules_data: Dict) -> list:
        """Generate next action items"""
        actions = []
        
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        
        is_profitable = m5_data.get("is_profitable", False)
        lh_decision = m6_data.get("decision", "")
        
        if is_profitable and "추진 가능" in lh_decision:
            actions.append("LH 사전 협의 진행")
            actions.append("설계 용역 발주 준비")
        elif "조건부 가능" in lh_decision:
            actions.append("LH 지적 사항 보완")
            actions.append("재분석 후 재제출 검토")
        else:
            actions.append("사업 계획 전면 재검토")
            actions.append("대안 부지 탐색")
        
        return actions


    def _extract_module_data(self, module_htmls: Dict[str, str]) -> Dict:
        """
        [FIX 1, 2, 3] Extract data from module HTML with strict consistency rules:
        
        1. NEVER recalculate - extract EXACT displayed values
        2. Preserve ALL core M3/M4 data (even in summary reports)
        3. Apply terminology normalization for consistency
        4. Match units and rounding from source module
        
        NOTE: This is NOT calculation - just extracting displayed values
        """
        import re
        modules_data = {}
        # [FIX 2] M3 필수 데이터 추출 (Mandatory M3 Core Data Extraction)
        if "m3_" in html:
            # 추천 유형
            m3_type_match = re.search(r'추천\s*유형[:\s]*([^<]+)', html)
            if m3_type_match:
                data["m3_recommended_type"] = m3_type_match.group(1).strip()
            
            # 총점 & 등급
            m3_score_match = re.search(r'총점[:\s]*(\d+\.?\d*)\s*점', html)
            if m3_score_match:
                data["m3_total_score"] = m3_score_match.group(1)
                
            m3_grade_match = re.search(r'등급[:\s]*([A-F등급]+)', html)
            if m3_grade_match:
                data["m3_grade"] = m3_grade_match.group(1).strip()
            
            # 적합도
            m3_suit_match = re.search(r'적합도[:\s]*(\d+\.?\d*)%', html)
            if m3_suit_match:
                data["m3_suitability"] = m3_suit_match.group(1)

        # [FIX 2] M4 필수 데이터 추출 (Mandatory M4 Core Data Extraction)
        if "m4_" in html:
            # 총 세대수
            m4_total_match = re.search(r'총\s*세대수[:\s]*(\d[\d,]*)', html)
            if m4_total_match:
                data["m4_total_units"] = m4_total_match.group(1)
            
            # 기본 세대수
            m4_basic_match = re.search(r'기본\s*세대수[:\s]*(\d[\d,]*)', html)
            if m4_basic_match:
                data["m4_basic_units"] = m4_basic_match.group(1)
            
            # 인센티브
            m4_incentive_match = re.search(r'인센티브[:\s]*(\d[\d,]*)', html)
            if m4_incentive_match:
                data["m4_incentive_units"] = m4_incentive_match.group(1)
            
            # 법적 기준
            m4_legal_match = re.search(r'법적\s*기준[:\s]*([^<]+)', html)
            if m4_legal_match:
                data["m4_legal_basis"] = m4_legal_match.group(1).strip()

        
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
        for keyword in ["추진 가능", "조건부 가능", "부적합"]:
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
        <body class="final-report report-color-lh_technical {self.report_type}">
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
