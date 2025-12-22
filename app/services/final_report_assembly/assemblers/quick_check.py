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
        m5_html_raw = self.load_module_html("M5")
        m6_html_raw = self.load_module_html("M6")
        
        # [FIX 1] Sanitize module HTML (remove N/A placeholders)
        m5_html = self.sanitize_module_html(m5_html_raw, "M5")
        m6_html = self.sanitize_module_html(m6_html_raw, "M6")
        
        # [FIX 2] Generate module transition
        transition_m5_m6 = self.generate_module_transition("M5", "M6", self.report_type)
        
        modules_data = self._extract_module_data({"M5": m5_html, "M6": m6_html})
        
        # [FIX 2] Generate KPI Summary Box (Mandatory for quick_check)
        kpis = {
            "순현재가치 (NPV)": modules_data.get("M5", {}).get("npv"),
            "수익성 판단": "수익성 있음" if modules_data.get("M5", {}).get("is_profitable", False) else "수익성 부족",
            "LH 심사 결과": modules_data.get("M6", {}).get("decision", "분석 미완료")
        }
        kpi_summary = self.generate_kpi_summary_box(kpis, self.report_type)
        
        exec_summary = self.narrative.executive_summary(modules_data)
        final_judgment = self.narrative.final_judgment(modules_data)
        
        # [FIX 5] Generate Decision Block (Clear Visual Conclusion)
        judgment_text = self._determine_judgment(modules_data)
        basis = self._generate_judgment_basis(modules_data)
        actions = self._generate_next_actions(modules_data)
        decision_block = self.generate_decision_block(judgment_text, basis, actions)
        
        # [FIX 4] Generate Next Actions Section
        next_actions = self.generate_next_actions_section(modules_data, self.report_type)
        
        sections = [
            kpi_summary,  # KPI at top
            exec_summary,
            self._wrap_module_html("M5", m5_html),
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
            f"[QuickCheck] Assembly complete with QA Summary "
            f"({len(html_with_qa):,} chars, QA Status: {qa_result['status']})"
        )
        
        return {"html": html_with_qa, "qa_result": qa_result}
    
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

        
        # M5: 순현재가치(NPV) and profitability
        m5_html = module_htmls.get("M5", "")
        npv_match = re.search(r'순현재가치(NPV)[:\s]*([+-]?\d{1,3}(?:,\d{3})*?)\s*원', m5_html,
            transition_m5_m6, re.IGNORECASE)
        if npv_match:
            npv_str = npv_match.group(1).replace(",", "")
            npv_value = int(npv_str)
            modules_data["M5"] = {"npv": npv_value, "is_profitable": npv_value > 0}
        
        # M6: Decision
        m6_html = module_htmls.get("M6", "")
        for keyword in ["추진 가능", "조건부 가능", "부적합"]:
            if keyword in m6_html:
                modules_data["M6"] = {"decision": keyword}
                break
        
        return modules_data
    
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
    
    def _wrap_module_html(self, module_id: str, html: str) -> str:
        """[FIX 6] Wrap module HTML with source reference for traceability"""
        module_names = {
            "M2": "토지 평가",
            "M3": "LH 선호유형",
            "M4": "건축규모",
            "M5": "사업성 분석",
            "M6": "LH 심사 대응"
        }
        module_name = module_names.get(module_id, "분석 결과")
        source_ref = self.generate_source_reference(module_id, module_name)
        
        return f"""
        <section class="module-section" data-module="{module_id}">
            {html}
            {source_ref}
        </section>
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
        .narrative { margin: 20px 0; padding: 15px; background: #f8f9fa; }
        .module-section { margin: 30px 0; padding: 20px; border: 1px solid #dee2e6; }
        """
        
        # Add unified design + watermark + copyright CSS
        return base_css + self.get_unified_design_css() + self.get_zerosite_watermark_css() + self.get_copyright_footer_css()
