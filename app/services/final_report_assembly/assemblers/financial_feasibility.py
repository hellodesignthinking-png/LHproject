"""
Financial Feasibility Report Assembler (PROMPT 6)
==================================================

Target Audience: 투자자 / 재무 담당자
Goal: 재무적 타당성 검토 (ROI, 순현재가치(NPV), IRR)
Modules: M2 (토지가치), M4 (사업규모), M5 (사업성)

ASSEMBLY ONLY - NO CALCULATION
"""

from typing import Dict, List, Literal
import logging
import re

from ..base_assembler import BaseFinalReportAssembler, get_report_brand_class, translate_decision_to_korean
from ..narrative_generator import NarrativeGeneratorFactory
from ..report_type_configs import REPORT_TYPE_CONFIGS, get_mandatory_kpi, get_critical_kpi

# [Phase 3.10 Final Lock + vPOST-FINAL] KPI Extractor with operational safety
from ..kpi_extractor import (
    KPIExtractor, 
    validate_mandatory_kpi, 
    validate_kpi_with_safe_gate,
    log_kpi_pipeline, 
    FinalReportAssemblyError
)

# [Phase 3.10] Hard-Fail KPI Binding


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
        m2_html_raw = self.load_module_html("M2")
        m4_html_raw = self.load_module_html("M4")
        m5_html_raw = self.load_module_html("M5")

        # [FIX 1] Sanitize module HTML (remove N/A placeholders)
        m2_html = self.sanitize_module_html(m2_html_raw, "M2")
        m4_html = self.sanitize_module_html(m4_html_raw, "M4")
        m5_html = self.sanitize_module_html(m5_html_raw, "M5")
                
        # [Phase 3.10 Final Lock + vPOST-FINAL] Extract KPI using SAFE-GATE
        mandatory_kpi = get_mandatory_kpi(self.report_type)
        critical_kpi = get_critical_kpi(self.report_type)
        modules_data = self._extract_module_data(
            {"M2": m2_html, "M4": m4_html, "M5": m5_html},
            mandatory_kpi
        )
        
        # [vPOST-FINAL] SAFE-GATE Validation: Critical vs Soft failures
        validation_result = validate_kpi_with_safe_gate(
            self.report_type, 
            modules_data, 
            {self.report_type: mandatory_kpi},
            {self.report_type: critical_kpi}
        )
        
        critical_missing = validation_result["critical_missing"]
        soft_missing = validation_result["soft_missing"]
        
        # Hard-Fail ONLY if CRITICAL KPI is missing
        if critical_missing:
            error_msg = f"[BLOCKED] Missing CRITICAL KPI: {', '.join(critical_missing)}"
            logger.error(f"[{self.report_type}] {error_msg}")
            return {
                "html": f"<html><body><h1>🚫 Report Generation Blocked</h1><pre>{error_msg}</pre><p>These KPIs are critical for decision-making and must be present.</p></body></html>",
                "qa_result": {
                    "status": "FAIL",
                    "errors": [error_msg],
                    "warnings": [f"Soft KPI missing: {', '.join(soft_missing)}"] if soft_missing else [],
                    "blocking": True,
                    "reason": "Hard-Fail: Critical KPI missing"
                }
            }
        
        # Generate data completeness panel if soft KPIs are missing
        data_completeness_panel = self.generate_data_completeness_panel(soft_missing)
        
                # [vABSOLUTE-FINAL-9] Generate DATA SIGNATURE for content verification
        import hashlib
        import json
        
        # Create deterministic data signature from modules_data
        data_for_signature = {
            module_id: {
                k: str(v) for k, v in data.items() 
                if not k.startswith('_')  # Exclude metadata
            }
            for module_id, data in modules_data.items()
        }
        data_signature = hashlib.sha1(
            json.dumps(data_for_signature, sort_keys=True).encode()
        ).hexdigest()[:12]
        
        # Extract key input values for display
        land_area = modules_data.get("M2") or {}.get("land_value_total", "N/A")
        total_units = modules_data.get("M4") or {}.get("total_units", "N/A") if "M4" in modules_data else modules_data.get("M5") or {}.get("total_units", "N/A")
        lh_decision = translate_decision_to_korean((modules_data.get("M6") or {}).get("decision") or "N/A")
        npv = modules_data.get("M5") or {}.get("npv", "N/A")
        
        # Format values safely
        def format_value(val, fmt=",.0f", unit=""):
            if val is None or val == "N/A" or (isinstance(val, str) and val.upper() == "N/A"):
                return "N/A"
            try:
                if isinstance(val, (int, float)):
                    return f"{val:{fmt}}{unit}"
                return str(val)
            except:
                return str(val)
        
        land_area_str = format_value(land_area, unit="원")
        total_units_str = format_value(total_units, unit="세대")
        npv_str = format_value(npv, unit="원")
        lh_decision_str = str(lh_decision) if lh_decision else "N/A"
        
        # Generate DATA SIGNATURE panel
        data_signature_panel = f"""
        <div style="
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 12px;
            margin: 20px 0;
            font-size: 11px;
            color: #495057;
        ">
            <div style="font-weight: bold; margin-bottom: 8px; color: #212529;">
                📊 Data Signature (데이터 시그니처)
            </div>
            <div style="font-family: monospace; color: #6c757d; margin-bottom: 8px;">
                {data_signature}
            </div>
            <div style="font-size: 10px; color: #6c757d; line-height: 1.6;">
                • 토지감정가: {land_area_str}<br/>
                • 총세대수: {total_units_str}<br/>
                • NPV: {npv_str}<br/>
                • LH 판단: {lh_decision_str}
            </div>
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #dee2e6; font-size: 9px; color: #adb5bd;">
                ※ 데이터 시그니처가 다르면 입력값이 변경되었음을 의미합니다.
            </div>
        </div>
        """
        
        logger.info(f"[{self.report_type}] DATA SIGNATURE: {data_signature}")
        
# Generate KPI summary from modules_data
        kpi_summary = self.generate_kpi_summary_box(modules_data, self.report_type)
        
        exec_summary = self.narrative.executive_summary(modules_data)
        
        # Generate module transitions
        transition_m2_m4 = self.generate_module_transition("M2", "M4", self.report_type)
        transition_m4_m5 = self.generate_module_transition("M4", "M5", self.report_type)
        
        final_judgment = self.narrative.final_judgment(modules_data)
        
        # Generate Decision Block
        judgment_text = self._determine_judgment(modules_data)
        basis = self._generate_judgment_basis(modules_data)
        actions = self._generate_next_actions(modules_data)
        decision_block = self.generate_decision_block(judgment_text, basis, actions)
        
        # Generate Next Actions Section
        next_actions = self.generate_next_actions_section(modules_data, self.report_type)
        
        sections = [
            data_signature_panel,  # [vABSOLUTE-FINAL-9] Data signature first
            self._generate_cover_page(),
            data_completeness_panel,
            kpi_summary,
            exec_summary,
            self._wrap_module_html("M2", m2_html),
            transition_m2_m4,
            self._wrap_module_html("M4", m4_html),
            transition_m4_m5,
            self._wrap_module_html("M5", m5_html),
            final_judgment,
            next_actions,
            decision_block,
            self._generate_footer().replace("{data_signature}", data_signature)
        ]
        
        # Wrap in HTML document
        html_content = self._wrap_in_document(sections)
        
        # Insert QA Summary Page
        html_with_qa, qa_result = self.generate_and_insert_qa_summary(
            html_content=html_content,
            report_type=self.report_type,
            modules_data=modules_data
        )
        
        logger.info(
            f"[FinancialFeasibility] Assembly complete with QA Summary "
            f"({len(html_with_qa):,} chars, QA Status: {qa_result['status']})"
        )
        
        return {"html": html_with_qa, "qa_result": qa_result}
    
    def _extract_module_data(self, module_htmls: Dict[str, str], mandatory_kpi: Dict[str, List[str]]) -> Dict:
        """
        [Phase 3.10 Final Lock] Extract module data using KPIExtractor
        
        Args:
            module_htmls: Dict of module_id -> HTML string
            mandatory_kpi: Dict of module_id -> required KPI keys
            
        Returns:
            Dict of module_id -> extracted KPI data
        """
        modules_data = {}
        
        for module_id, html in module_htmls.items():
            if not html or html.strip() == "":
                logger.warning(f"[{module_id}] Empty HTML")
                modules_data[module_id] = {"status": "empty", "_complete": False}
                continue
            
            # Get required keys for this module
            required_keys = mandatory_kpi.get(module_id, [])
            
            try:
                # Extract KPI using new extractor (SINGLE ENTRY POINT)
                kpi_data = KPIExtractor.extract_module_kpi(html, module_id, required_keys)
                modules_data[module_id] = kpi_data
                
                # Log pipeline for audit trail
                log_kpi_pipeline(self.report_type, self.context_id, module_id, kpi_data)
                
            except FinalReportAssemblyError as e:
                logger.error(f"[{module_id}] KPI extraction failed: {e}")
                modules_data[module_id] = {
                    "status": "extraction_failed",
                    "_complete": False,
                    "error": str(e)
                }
        
        return modules_data

        
        # [FIX 2] Generate KPI Summary Box (Mandatory for financial_feasibility)
        kpis = {
            "총 토지 감정가": modules_data.get("M2") or {}.get("land_value"),
            "순현재가치 (NPV)": modules_data.get("M5") or {}.get("npv"),
            "내부내부수익률(IRR)(IRR) (IRR)": modules_data.get("M5") or {}.get("irr")
        }
        kpi_summary = self.generate_kpi_summary_box(kpis, self.report_type)
        
        exec_summary = self.narrative.executive_summary(modules_data)
        transition_m2_m4 = self.generate_module_transition("M2", "M4", self.report_type)
        transition_m4_m5 = self.generate_module_transition("M4", "M5", self.report_type)
        final_judgment = self.narrative.final_judgment(modules_data)
        
        # [FIX 5] Generate Decision Block (Clear Visual Conclusion)
        judgment_text = self._determine_judgment(modules_data)
        basis = self._generate_judgment_basis(modules_data)
        actions = self._generate_next_actions(modules_data)
        decision_block = self.generate_decision_block(judgment_text, basis, actions)
        
        # [FIX 4] Generate Next Actions Section
        next_actions = self.generate_next_actions_section(modules_data, self.report_type)
        
        
        sections = [
            data_signature_panel,  # [vABSOLUTE-FINAL-9] Data signature first
            self._generate_cover_page(),
            kpi_summary,  # KPI at top
            exec_summary,
            self._wrap_module_html("M2", m2_html),
            transition_m2_m4,
            self._wrap_module_html("M4", m4_html),
            transition_m4_m5,
            self._wrap_module_html("M5", m5_html),
            final_judgment,
            next_actions,
            decision_block,  # Visual decision at bottom
            self._generate_footer().replace("{data_signature}", data_signature)
        ]
        
        # Wrap in HTML document
        html_content = self._wrap_in_document(sections)
        
        # [PROMPT 3.5-3] Insert QA Summary Page
        html_with_qa, qa_result = self.generate_and_insert_qa_summary(
            html_content=html_content,
            report_type=self.report_type,
            modules_data=modules_data
        )
        
        # [P0 FIX] Validate KPI completeness - FAIL if any core KPI is N/A
        # [vLAST] OLD validator removed - Phase 3.10 Hard-Fail handles validation
        logger.info(
            f"[FinancialFeasibility] Assembly complete with QA Summary "
            f"({len(html_with_qa):,} chars, QA Status: {qa_result['status']})"
        )
        
        return {"html": html_with_qa, "qa_result": qa_result}
    
    def _determine_judgment(self, modules_data: Dict) -> str:
        """Determine final judgment text based on module data"""
        m5_data = modules_data.get("M5") or {}
        m6_data = modules_data.get("M6") or {}
        
        is_profitable = m5_data.get("is_profitable", False)
        lh_decision = translate_decision_to_korean(m6_data.get("decision") or "")
        
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
        
        m2_data = modules_data.get("M2") or {}
        m5_data = modules_data.get("M5") or {}
        m6_data = modules_data.get("M6") or {}
        
        # [FIX D] Profitability with explicit 순현재가치(NPV)
        npv = m5_data.get("npv")
        if npv and npv > 0:
            basis.append(f"✅ 수익성 양호: 순현재가치(NPV) {self.format_number(npv, 'currency')}")
        elif npv and npv <= 0:
            basis.append(f"❌ 수익성 부정적: 순현재가치(NPV) {self.format_number(npv, 'currency')}")
        else:
            basis.append("⚠️ 수익성: 분석 데이터 부족")
        
        # [FIX D] LH Decision with explicit status
        lh_decision = translate_decision_to_korean(m6_data.get("decision") or "분석 미완료")
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
        
        m5_data = modules_data.get("M5") or {}
        m6_data = modules_data.get("M6") or {}
        
        is_profitable = m5_data.get("is_profitable", False)
        lh_decision = translate_decision_to_korean(m6_data.get("decision") or "")
        
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

    def _generate_footer(self) -> str:
        """
        [PROMPT 3.5-2] ZEROSITE Copyright Footer
        [vABSOLUTE-FINAL-12] Add SEARCHABLE signature text for binary verification
        """
        from datetime import datetime
        
        # Searchable text block (for PDF binary search)
        searchable_signature = f"""
        <div style="
            font-size: 10px;
            color: #b00000;
            border: 1px solid #b00000;
            padding: 6px;
            margin: 12px 0;
            background: #fff8f8;
            font-family: monospace;
        ">
            <div style="font-weight: bold; margin-bottom: 4px;">
                📊 Report Verification Signature (보고서 검증 시그니처)
            </div>
            <div>
                BUILD_SIGNATURE: vABSOLUTE-FINAL-12<br/>
                BUILD_TS: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z<br/>
                REPORT: {self.report_type}<br/>
                CONTEXT: {self.context_id}<br/>
                DATA_SIGNATURE: {{data_signature}}
            </div>
            <div style="font-size: 8px; color: #666; margin-top: 4px;">
                ※ This signature is embedded as searchable text for verification purposes.
            </div>
        </div>
        """
        
        copyright = self.get_zerosite_copyright_footer(
            report_type=self.report_type,
            context_id=self.context_id
        )
        
        return searchable_signature + copyright
    
    def _wrap_in_document(self, sections: List[str]) -> str:
        # [vABSOLUTE-FINAL-7] BUILD SIGNATURE for visual verification
        from datetime import datetime
        build_signature = f"""
        <div style="
            position: fixed;
            top: 10px;
            right: 10px;
            font-size: 11px;
            color: red;
            background: rgba(255,255,255,0.9);
            padding: 8px;
            border: 2px solid red;
            z-index: 9999;
            font-family: monospace;
        ">
            ✅ BUILD: vABSOLUTE-FINAL-6<br/>
            📅 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC<br/>
            🔧 REPORT: {self.report_type}
        </div>
        """
        
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
        <body class="final-report {get_report_brand_class(self.report_type)} {self.report_type}">
            {build_signature}
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
