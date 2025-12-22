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
import re

from ..base_assembler import BaseFinalReportAssembler
from ..narrative_generator import NarrativeGeneratorFactory
from ..report_type_configs import REPORT_TYPE_CONFIGS

# [Phase 3.10] Hard-Fail KPI Binding
from ..kpi_hard_fail_enforcement import enforce_kpi_binding, KPIBindingError, FinalReportGenerationError
from app.services.final_report_assembly.kpi_extraction_vlast import extract_module_kpis


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
        m2_html_raw = self.load_module_html("M2")
        m5_html_raw = self.load_module_html("M5")
        m6_html_raw = self.load_module_html("M6")
        
        # [FIX 1] Sanitize module HTML (remove N/A placeholders)
        m2_html = self.sanitize_module_html(m2_html_raw, "M2")
        m5_html = self.sanitize_module_html(m5_html_raw, "M5")
        m6_html = self.sanitize_module_html(m6_html_raw, "M6")
        
        # Extract module data for narrative generation + KPI
        modules_data = self._extract_module_data({"M2": m2_html, "M5": m5_html, "M6": m6_html})
        
        # [Phase 3.10] HARD-FAIL: Normalize → Bind → Validate
        try:
            bound_kpis = enforce_kpi_binding(self.report_type, modules_data)
            kpi_summary = self.generate_kpi_summary_box(bound_kpis, self.report_type)
        except (KPIBindingError, FinalReportGenerationError) as e:
            logger.error(f"[{self.report_type}] KPI binding FAILED: {e}")
            return {
                "html": f"<html><body><h1>❌ Report Generation Blocked</h1><pre>{str(e)}</pre></body></html>",
                "qa_result": {
                    "status": "FAIL",
                    "errors": [str(e)],
                    "warnings": [],
                    "blocking": True,
                    "reason": "KPI binding hard-fail - missing mandatory data"
                }
            }
        
        # Generate narrative elements
        exec_summary = self.narrative.executive_summary(modules_data)
        transition_m2_m5 = self.generate_module_transition("M2", "M5", self.report_type)
        transition_m5_m6 = self.generate_module_transition("M5", "M6", self.report_type)
        final_judgment_narrative = self.narrative.final_judgment(modules_data)
        
        # [FIX 5] Generate Decision Block (Clear Visual Conclusion)
        judgment_text = self._determine_judgment(modules_data)
        basis = self._generate_judgment_basis(modules_data)
        actions = self._generate_next_actions(modules_data)
        decision_block = self.generate_decision_block(judgment_text, basis, actions)
        
        # [FIX 4] Generate Next Actions Section
        next_actions = self.generate_next_actions_section(modules_data, self.report_type)
        
        # Assemble sections
        sections = [
            self._generate_cover_page(),
            kpi_summary,  # KPI at top
            exec_summary,
            self._wrap_module_html("M2", m2_html),
            transition_m2_m5,
            self._wrap_module_html("M5", m5_html),
            transition_m5_m6,
            self._wrap_module_html("M6", m6_html),
            final_judgment_narrative,
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
        
        # [P0 FIX] Validate KPI completeness - FAIL if any core KPI is N/A
        # [vLAST] OLD validator removed - Phase 3.10 Hard-Fail handles validation
        logger.info(
            f"[LandownerSummary] Assembly complete with QA Summary "
            f"({len(html_with_qa):,} chars, QA Status: {qa_result['status']})"
        )
        
        return {"html": html_with_qa, "qa_result": qa_result}
    
    
    def _extract_kpi_from_module_html(self, module_id: str, html: str) -> Dict[str, any]:
        """
        [P1 CRITICAL FIX] Enhanced KPI extraction with 4-tier fallback
        
        PROBLEM: Original _extract_module_data() only used simple regex
        SOLUTION: Multi-tier extraction strategy:
        
        Tier 1: data-* attributes (most reliable)
        Tier 2: HTML table extraction (<th> + <td>)
        Tier 3: Regex patterns on text content
        Tier 4: Fallback to "any number" heuristics
        
        Returns:
            Dict with extracted KPIs + _complete flag
        """
        from bs4 import BeautifulSoup
        import logging
        
        logger = logging.getLogger(__name__)
        soup = BeautifulSoup(html, 'html.parser')
        kpis = {"_module_id": module_id, "_complete": False, "_extraction_method": None}
        
        # ===== M2: LAND APPRAISAL (토지 평가) =====
        if module_id == "M2":
            # Tier 1: data-* attribute
            elem = soup.find(attrs={"data-land-value": True})
            if elem:
                try:
                    value = elem.get("data-land-value", "").replace(",", "")
                    kpis["land_value"] = int(value)
                    kpis["_complete"] = True
                    kpis["_extraction_method"] = "data-attribute"
                    logger.info(f"[M2] Extracted land_value via data-attribute: {kpis['land_value']:,}원")
                    return kpis
                except (ValueError, AttributeError) as e:
                    logger.warning(f"[M2] data-attribute parsing failed: {e}")
            
            # Tier 2: Table extraction (look for <th> with "감정가" keyword)
            for tr in soup.find_all('tr'):
                th = tr.find('th')
                td = tr.find('td')
                if th and td:
                    th_text = th.get_text().strip()
                    if any(keyword in th_text for keyword in ["감정가", "토지가치", "평가액", "기준가"]):
                        td_text = td.get_text().strip()
                        match = re.search(r'([\d,]+)\s*원', td_text)
                        if match:
                            kpis["land_value"] = int(match.group(1).replace(",", ""))
                            kpis["_complete"] = True
                            kpis["_extraction_method"] = "table-extraction"
                            logger.info(f"[M2] Extracted land_value via table: {kpis['land_value']:,}원")
                            return kpis
            
            # Tier 3: Regex on full HTML text
            patterns = [
                r'(?:감정가|토지가치|평가액|기준가)[:\s]*([\d,]+)\s*원',
                r'<strong>([\d,]+)</strong>\s*원',  # Bold numbers with 원
                r'([\d,]{10,})\s*원'  # Any large number (10+ digits) with 원
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html)
                if match:
                    kpis["land_value"] = int(match.group(1).replace(",", ""))
                    kpis["_complete"] = True
                    kpis["_extraction_method"] = f"regex-{pattern[:30]}"
                    logger.info(f"[M2] Extracted land_value via regex: {kpis['land_value']:,}원")
                    return kpis
            
            logger.warning("[M2] ALL extraction tiers failed for land_value")
        
        # ===== M3: LH PREFERRED TYPE (LH 선호 유형) =====
        elif module_id == "M3":
            # Extract type
            type_patterns = [
                r'추천\s*유형[:\s]*([가-힣]+)',
                r'선호\s*유형[:\s]*([가-힣]+)',
                r'유형[:\s]*([가-힣]+)'
            ]
            for pattern in type_patterns:
                match = re.search(pattern, html)
                if match:
                    kpis["recommended_type"] = match.group(1).strip()
                    break
            
            # Extract score
            score_patterns = [
                r'총점[:\s]*(\d+\.?\d*)',
                r'점수[:\s]*(\d+\.?\d*)',
                r'(\d+\.?\d*)\s*점'
            ]
            for pattern in score_patterns:
                match = re.search(pattern, html)
                if match:
                    kpis["total_score"] = float(match.group(1))
                    break
            
            # Extract grade
            grade_match = re.search(r'등급[:\s]*([A-F등급]+)', html)
            if grade_match:
                kpis["grade"] = grade_match.group(1)
            
            kpis["_complete"] = all(k in kpis for k in ["recommended_type", "total_score"])
            kpis["_extraction_method"] = "regex-multi-pattern"
            
            if kpis["_complete"]:
                logger.info(f"[M3] Extracted type={kpis['recommended_type']}, score={kpis['total_score']}")
        
        # ===== M4: BUILDING SCALE (건축 규모) =====
        elif module_id == "M4":
            # Total units - try multiple patterns
            units_patterns = [
                r'총\s*세대수[:\s]*(\d[\d,]*)',
                r'전체\s*세대수[:\s]*(\d[\d,]*)',
                r'세대수[:\s]*(\d[\d,]*)',
                r'(\d{3,})\s*세대'
            ]
            
            for pattern in units_patterns:
                match = re.search(pattern, html)
                if match:
                    kpis["total_units"] = int(match.group(1).replace(",", ""))
                    break
            
            # Floor area
            area_patterns = [
                r'연면적[:\s]*([\d,]+\.?\d*)\s*㎡',
                r'총\s*연면적[:\s]*([\d,]+\.?\d*)\s*㎡'
            ]
            
            for pattern in area_patterns:
                match = re.search(pattern, html)
                if match:
                    kpis["floor_area"] = float(match.group(1).replace(",", ""))
                    break
            
            kpis["_complete"] = ("total_units" in kpis)
            kpis["_extraction_method"] = "regex-multi-pattern"
            
            if kpis["_complete"]:
                logger.info(f"[M4] Extracted total_units={kpis.get('total_units', 'N/A')}")
        
        # ===== M5: FEASIBILITY (사업성 분석) =====
        elif module_id == "M5":
            # NPV - most critical metric
            npv_patterns = [
                r'순현재가치\s*\(NPV\)[:\s]*([+-]?\d{1,3}(?:,\d{3})*)',
                r'순현재가치[:\s]*([+-]?\d{1,3}(?:,\d{3})*)',
                r'NPV[:\s]*([+-]?\d{1,3}(?:,\d{3})*)',
            ]
            
            for pattern in npv_patterns:
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    npv_value = int(match.group(1).replace(",", ""))
                    kpis["npv"] = npv_value
                    kpis["is_profitable"] = (npv_value > 0)
                    break
            
            # IRR
            irr_patterns = [
                r'내부수익률\s*\(IRR\)[:\s]*(\d+\.?\d*)\s*%',
                r'IRR[:\s]*(\d+\.?\d*)\s*%',
                r'내부수익률[:\s]*(\d+\.?\d*)\s*%'
            ]
            
            for pattern in irr_patterns:
                match = re.search(pattern, html, re.DOTALL)
                if match:
                    kpis["irr"] = float(match.group(1))
                    break
            
            kpis["_complete"] = ("npv" in kpis)
            kpis["_extraction_method"] = "regex-multi-pattern"
            
            if kpis["_complete"]:
                logger.info(f"[M5] Extracted NPV={kpis['npv']:,}원, profitable={kpis.get('is_profitable')}")
        
        # ===== M6: LH REVIEW (LH 심사) =====
        elif module_id == "M6":
            # Decision keywords (order matters - most specific first)
            if re.search(r'추진\s*가능', html) or "GO" in html.upper():
                kpis["decision"] = "추진 가능"
            elif re.search(r'조건부', html) or "CONDITIONAL" in html.upper():
                kpis["decision"] = "조건부 가능"
            elif re.search(r'부적합|불가', html) or "NO-GO" in html.upper():
                kpis["decision"] = "부적합"
            else:
                kpis["decision"] = "판정 미확정"
            
            kpis["_complete"] = (kpis["decision"] != "판정 미확정")
            kpis["_extraction_method"] = "keyword-search"
            
            logger.info(f"[M6] Extracted decision={kpis['decision']}")
        
        return kpis

    def _extract_module_data(self, module_htmls: Dict[str, str]) -> Dict:
        """
        [UPDATED] Extract module data using enhanced KPI extractor
        
        This method now calls _extract_kpi_from_module_html() for each module,
        which provides robust multi-tier extraction instead of weak regex-only.
        """
        modules_data = {}
        
        for module_id, html in module_htmls.items():
            if not html or html.strip() == "":
                modules_data[module_id] = {"status": "empty", "_complete": False}
                continue
            
            # Use the enhanced extractor
            kpis = extract_module_kpis(html, module_id)
            modules_data[module_id] = kpis
        
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
        """Wrap module HTML in section container with source reference"""
        # [FIX 6] 모듈 출처 참조 추가 (Module Source Traceability)
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
        """[PROMPT 3.5-2] ZEROSITE Copyright Footer"""
        return self.get_zerosite_copyright_footer(
            report_type=self.report_type,
            context_id=self.context_id
        )
    
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
        <body class="final-report report-color-landowner {self.report_type}">
            {"".join(sections)}
        </body>
        </html>
        """
    
    def _get_report_css(self) -> str:
        """[FIX 4] Report CSS with unified design system"""
        base_css = """
        body.final-report {
            font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px;
            color: #333;
        }
        .cover-page {
            text-align: center;
            padding: 100px 20px;
            border-bottom: 2px solid #007bff;
            page-break-after: always;
        }
        .narrative {
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .executive-summary {
            background: #e3f2fd;
            padding: 30px;
            border-left: 4px solid #007bff;
            margin: 30px 0;
            page-break-after: always;
        }
        .final-judgment {
            background: #fff3cd;
            padding: 30px;
            border-left: 4px solid #ffc107;
            margin: 30px 0;
        }
        .judgment {
            font-size: 1.2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .module-section {
            margin: 40px 0;
            padding: 30px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            page-break-inside: avoid;
        }
        .transition {
            font-style: italic;
            color: #666;
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-left: 3px solid #ccc;
        }
        """
        
        # Add unified design CSS + watermark + copyright
        return base_css + self.get_unified_design_css() + self.get_zerosite_watermark_css() + self.get_copyright_footer_css()
