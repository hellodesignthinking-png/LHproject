"""
ZeroSite Final Report - Narrative Generator (PROMPT 5 + vABSOLUTE-FINAL-10)
============================================================================

PURPOSE:
    Transform "module HTML listing" → "decision-ready story document"
    
    Provides:
    1. Executive Summary (CRITICAL for QA)
    2. Module transitions (context between sections)
    3. Final judgment (CRITICAL for QA - must include decision keywords)
    
CRITICAL RULES (PROMPT 5):
    ❌ NO calculation / compute / analyze
    ❌ NO canonical_summary access
    ❌ NO number generation/transformation
    ✅ ONLY HTML fragments
    ✅ ONLY interpretation of pre-calculated module results
    
    Violation of these rules → RuntimeError

[vABSOLUTE-FINAL-10] NEW MANDATE - ACTUAL VALUES ENFORCEMENT:
=============================================================

❗️ABSOLUTE REQUIREMENT: ALL NARRATIVES MUST USE ACTUAL DATA FROM modules_data

**THE RULE:**
    When modules_data provides a value → USE IT IN THE NARRATIVE
    When modules_data has NO value → Say "산출 진행 중" (NOT "N/A 검증 필요")

**FORBIDDEN PATTERNS:**
    ❌ "NPV는 N/A (검증 필요)입니다"
    ❌ "토지 가치: N/A"  
    ❌ "검증이 필요합니다"
    ❌ Generic templates without referencing actual numbers

**REQUIRED PATTERNS:**
    ✅ "순현재가치(NPV)는 약 4.2억 원으로 산출되었습니다"
    ✅ "내부수익률(IRR) 13.2%로 투자 수익성이 양호합니다"
    ✅ "LH 심사 결과 '조건부 적합' (등급: B+)로 예측됩니다"
    ✅ "예상 {actual_units}세대 규모로 사업성이 확보됩니다"

**DATA EXTRACTION PATTERN:**
    ```python
    # Multiple fallback keys for robustness
    npv = m5_data.get("npv", m5_data.get("NPV", 0))
    land_value = m2_data.get("land_value_total", 
                            m2_data.get("total_land_value", 
                                      m2_data.get("land_value", 0)))
    
    # Safe formatting with actual values
    npv_str = f"{int(npv):,}원" if npv and npv != 0 else "산출 진행 중"
    
    # USE IN NARRATIVE
    return f"본 사업의 NPV는 {npv_str}로..."
    ```

**VERIFICATION TEST:**
    After each narrative update:
    1. Generate report with test data
    2. Search PDF for "N/A" - should find ZERO matches
    3. Search PDF for actual numbers - should find MULTIPLE matches
    4. Compare with previous version - text should be DIFFERENT

VERSION: 2.0 (vABSOLUTE-FINAL-10 Update)
DATE: 2025-12-24
PHASE: 3.10 (Final Lock + Content Verification)
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


# ========== BASE NARRATIVE GENERATOR (ABSTRACT) ==========

class BaseNarrativeGenerator(ABC):
    """
    Base class for all Narrative Generators
    
    Role:
    - Explains module results (no calculation)
    - Provides decision-making context
    - Satisfies QA Validator requirements
    
    PROMPT 5 Requirements:
    ----------------------
    1. executive_summary() - BLOCKING if missing
    2. transitions() - Connects modules narratively
    3. final_judgment() - BLOCKING if missing judgment keywords
    """
    
    def __init__(self):
        self.report_type = "unknown"
        self._validate_no_forbidden_methods()
    
    def _validate_no_forbidden_methods(self):
        """
        Runtime check: Ensure no forbidden operations
        """
        forbidden = ["calculate", "compute", "analyze", "access_canonical_summary"]
        
        for method_name in dir(self):
            if any(forbidden_word in method_name.lower() for forbidden_word in forbidden):
                raise RuntimeError(
                    f"FORBIDDEN: Narrative Generator has method '{method_name}' "
                    f"which suggests calculation/analysis. "
                    f"Narrative Generators MUST ONLY interpret pre-calculated data."
                )
    
    @abstractmethod
    def executive_summary(self, modules_data: Dict) -> str:
        """
        Generate Executive Summary section
        
        CRITICAL: QA Validator BLOCKS PDF if this is missing.
        
        Args:
            modules_data: Dict of module data (e.g., {"M2": {...}, "M5": {...}})
        
        Returns:
            HTML fragment with:
            - <section class="narrative executive-summary">
            - Multiple <p class="narrative"> paragraphs
            - Clear context for decision-making
        """
        pass
    
    @abstractmethod
    def transitions(self, from_module: str, to_module: str) -> str:
        """
        Generate narrative transition between modules
        
        Args:
            from_module: Module ID (e.g., "M2")
            to_module: Module ID (e.g., "M5")
        
        Returns:
            HTML fragment: <p class="narrative transition">...</p>
            or empty string if no transition needed
        """
        pass
    
    @abstractmethod
    def final_judgment(self, modules_data: Dict) -> str:
        """
        Generate final judgment/recommendation section
        
        CRITICAL: QA Validator BLOCKS PDF if judgment keywords are missing.
        
        Required keywords (at least one):
        - "추천합니다", "부적합", "조건부 승인", "추진 가능", "추진 곤란"
        
        Args:
            modules_data: Dict of module data
        
        Returns:
            HTML fragment with:
            - <section class="narrative final-judgment">
            - <p class="judgment"> with decision keyword
        """
        pass


# ========== LANDOWNER NARRATIVE GENERATOR ==========

class LandownerNarrativeGenerator(BaseNarrativeGenerator):
    """
    Narrative Generator for Landowner Summary Report
    
    Target Audience: 토지주 (일반인)
    Focus: 사업 수익성 + LH 승인 가능성
    
    QA Requirements:
    - Narrative paragraphs ≥ 3
    - Judgment keywords present
    - Executive summary exists
    """
    
    def __init__(self):
        super().__init__()
        self.report_type = "landowner_summary"
    
    def executive_summary(self, modules_data: Dict) -> str:
        """
        [vABSOLUTE-FINAL-10] Executive Summary for Landowner - ACTUAL VALUES ONLY
        """
        m2_data = modules_data.get("M2", {})
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        m4_data = modules_data.get("M4", {})
        
        # Extract with multiple fallback keys
        land_value = m2_data.get("land_value_total", m2_data.get("total_land_value", m2_data.get("land_value", 0)))
        npv = m5_data.get("npv", m5_data.get("NPV", 0))
        irr = m5_data.get("irr", m5_data.get("IRR", 0))
        lh_decision = m6_data.get("decision", m6_data.get("Decision", "검토 중"))
        lh_grade = m6_data.get("grade", m6_data.get("Grade", ""))
        total_units = m4_data.get("total_units", m5_data.get("total_units", 0))
        
        # Format numbers safely
        land_str = f"{int(land_value):,}원" if land_value and land_value != 0 else "평가 진행 중"
        npv_str = f"{int(npv):,}원" if npv and npv != 0 else "산출 진행 중"
        irr_str = f"{float(irr)*100:.2f}%" if irr and irr != 0 else "산출 진행 중"
        units_str = f"{int(total_units)}세대" if total_units and total_units != 0 else "미확정"
        
        return f"""
        <section class="narrative executive-summary">
            <h2>📌 종합 검토 요약 (Executive Summary)</h2>
            
            <p class="narrative">
                본 보고서는 귀하의 토지에 대한 <strong>LH 공공기여형 민간임대주택 사업</strong>의 
                타당성을 검토한 결과입니다. 토지주 관점에서 가장 중요한 
                <strong>수익성</strong>과 <strong>LH 승인 가능성</strong>을 중심으로 분석했습니다.
            </p>
            
            <p class="narrative">
                <strong>1. 토지 가치 평가:</strong> 대상 토지의 감정가는 <strong>{land_str}</strong>로 
                평가되었으며, 예상 건축 규모는 <strong>{units_str}</strong>입니다.
            </p>
            
            <p class="narrative">
                <strong>2. 사업 수익성:</strong> 이 토지를 활용한 LH 사업의 순현재가치(NPV)는 
                <strong>{npv_str}</strong>, 내부수익률(IRR)은 <strong>{irr_str}</strong>로 
                산출되었습니다. 이는 사업의 재무적 타당성을 나타내는 핵심 지표입니다.
            </p>
            
            <p class="narrative">
                <strong>3. LH 승인 전망:</strong> LH 사전 심사 기준에 따른 검토 결과, 
                본 사업은 <strong>"{lh_decision}"</strong> (예상 등급: <strong>{lh_grade}</strong>) 
                판정을 받았습니다. 이는 토지의 입지 조건, 건축 규모, 정책 부합도를 
                종합적으로 고려한 결과입니다.
            </p>
        </section>
        """
    
    def transitions(self, from_module: str, to_module: str) -> str:
        """
        Narrative transitions for Landowner Report
        """
        transition_map = {
            ("M2", "M5"): """
                <p class="narrative transition">
                    토지 가치 평가를 바탕으로, 이제 이 토지로 실제 사업을 진행했을 때 
                    얼마나 수익이 나는지 재무 분석 결과를 살펴보겠습니다.
                </p>
            """,
            ("M5", "M6"): """
                <p class="narrative transition">
                    사업성 분석 결과를 확인했으니, 이제 LH가 이 사업을 실제로 
                    승인할 가능성이 얼마나 되는지 심사 예측 결과를 검토하겠습니다.
                </p>
            """
        }
        
        text = transition_map.get((from_module, to_module))
        return text if text else ""
    
    def final_judgment(self, modules_data: Dict) -> str:
        """
        Final judgment for Landowner Report
        
        Decision logic:
        - If M5 profitable AND M6 not rejected → 추천합니다
        - If M5 profitable BUT M6 conditional → 조건부 승인
        - If M5 not profitable → 부적합
        """
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        
        npv = m5_data.get("npv", 0)
        is_profitable = npv > 0
        lh_decision = m6_data.get("decision", "")
        
        # Decision logic
        if is_profitable and lh_decision not in ["부적합", "탈락"]:
            judgment = """
                ✅ 본 사업은 현재 조건에서 <strong>추진을 추천합니다</strong>.
            """
            reason = """
                재무적으로 수익성이 확보되었으며, LH 심사 기준도 통과 가능한 
                수준으로 평가되었습니다. 다만, 최종 투자 결정 전에 
                LH와의 사전 협의를 권장합니다.
            """
        elif is_profitable:
            judgment = """
                ⚠️ 수익성은 확보되었으나, <strong>조건부 승인</strong>을 권장합니다.
            """
            reason = """
                재무적으로는 수익이 발생하지만, LH 심사에서 일부 보완이 필요한 
                사항이 있습니다. LH와 협의하여 보완 가능한 부분을 검토하신 후 
                최종 결정하시기 바랍니다.
            """
        else:
            judgment = """
                ❌ 현 조건에서는 사업 추진이 <strong>부적합</strong>합니다.
            """
            reason = """
                재무 분석 결과 투자 대비 수익성이 확보되지 않았습니다. 
                사업 조건 변경(공사비 절감, 임대료 상승 등) 또는 
                토지 용도 재검토를 권장합니다.
            """
        
        return f"""
        <section class="narrative final-judgment">
            <h2>🧾 최종 의견 (Final Judgment)</h2>
            
            <div class="judgment-box">
                <p class="judgment">{judgment}</p>
                <p class="narrative reason">{reason}</p>
            </div>
            
            <div class="disclaimer">
                <p class="narrative">
                    <strong>주의사항:</strong> 본 의견은 분석 시점의 데이터를 기반으로 한 
                    참고 자료입니다. LH 정책, 시장 상황 변동에 따라 실제 결과는 
                    달라질 수 있으므로, 최종 투자 결정은 전문가 자문 후 
                    신중하게 내리시기 바랍니다.
                </p>
            </div>
        </section>
        """


# ========== LH TECHNICAL NARRATIVE GENERATOR ==========

class LHTechnicalNarrativeGenerator(BaseNarrativeGenerator):
    """
    Narrative Generator for LH Technical Review Report
    
    Target Audience: LH 심사역 (기술 검토자)
    Focus: LH 정책 부합성 + 기술적 실현 가능성
    """
    
    def __init__(self):
        super().__init__()
        self.report_type = "lh_technical"
    
    def executive_summary(self, modules_data: Dict) -> str:
        """
        [vABSOLUTE-FINAL-10] LH Technical - Add FAR, BCR, scoring details
        """
        m3_data = modules_data.get("M3", {})
        m4_data = modules_data.get("M4", {})
        m6_data = modules_data.get("M6", {})
        
        recommended_type = m3_data.get("recommended_type", "미확정")
        type_score = m3_data.get("total_score", m3_data.get("type_score", 0))
        
        total_units = m4_data.get("total_units", m4_data.get("household_count", 0))
        far = m4_data.get("floor_area_ratio", m4_data.get("far", 0))
        bcr = m4_data.get("building_coverage_ratio", m4_data.get("bcr", 0))
        
        lh_decision = m6_data.get("decision", "검토 필요")
        total_score = m6_data.get("total_score", 0)
        
        # Format safely
        units_str = f"{int(total_units):,}세대" if total_units and total_units != 0 else "미확정"
        far_str = f"{float(far):.1f}%" if far and far != 0 else "산출 불가"
        bcr_str = f"{float(bcr):.1f}%" if bcr and bcr != 0 else "산출 불가"
        type_score_str = f"{float(type_score):.0f}점" if type_score and type_score != 0 else "미산정"
        lh_score_str = f"{float(total_score):.0f}점" if total_score and total_score != 0 else "미산정"
        
        return f"""
        <section class="narrative executive-summary">
            <h2>📋 기술 검토 요약 (Technical Review Summary)</h2>
            
            <p class="narrative">
                본 보고서는 LH 공공기여형 민간임대주택 사업의 기술적 타당성을 
                LH 내부 심사 기준에 따라 검토한 결과입니다.
            </p>
            
            <p class="narrative">
                <strong>주택유형 분석 (M3):</strong><br/>
                • 선호 유형: <strong>{recommended_type}</strong><br/>
                • 유형 점수: <strong>{type_score_str}</strong>
            </p>
            
            <p class="narrative">
                <strong>건축 규모 (M4):</strong><br/>
                • 건축 세대수: <strong>{units_str}</strong><br/>
                • 용적률: <strong>{far_str}</strong><br/>
                • 건폐율: <strong>{bcr_str}</strong>
            </p>
            
            <p class="narrative">
                <strong>LH 심사 예측 (M6):</strong><br/>
                • 종합 판단: <strong>{lh_decision}</strong><br/>
                • 종합 점수: <strong>{lh_score_str}</strong>
            </p>
            
            <p class="narrative">
                아래 상세 분석에서는 주택유형 선정 근거, 건축 규모 산정 과정, 
                LH 심사 항목별 평가 결과를 제시합니다.
            </p>
        </section>
        """
    
    def transitions(self, from_module: str, to_module: str) -> str:
        transition_map = {
            ("M3", "M4"): """
                <p class="narrative transition">
                    선호 주택유형이 결정되었으므로, 이제 실제 건축 가능한 
                    규모를 법적 용적률과 인센티브를 고려하여 산정합니다.
                </p>
            """,
            ("M4", "M6"): """
                <p class="narrative transition">
                    건축 규모가 확정되었으니, LH 심사 기준에 따라 
                    본 사업의 심사 통과 가능성을 종합적으로 평가합니다.
                </p>
            """
        }
        
        text = transition_map.get((from_module, to_module))
        return text if text else ""
    
    def final_judgment(self, modules_data: Dict) -> str:
        m6_data = modules_data.get("M6", {})
        lh_decision = m6_data.get("decision", "")
        total_score = m6_data.get("total_score", 0)
        
        if lh_decision in ["승인", "적합"]:
            judgment = "✅ 기술적으로 <strong>승인</strong> 가능하며, 사업 <strong>추진을 권장</strong>합니다."
            reason = f"LH 심사 기준 총점 {total_score}점으로 승인 기준을 충족합니다."
        elif lh_decision == "조건부 승인":
            judgment = "⚠️ <strong>조건부 승인</strong>이 예상됩니다."
            reason = "일부 항목에서 보완이 필요하나, 전체적으로 승인 가능한 수준입니다."
        else:
            judgment = "❌ 기술적으로 <strong>부적합</strong> 판정입니다."
            reason = "LH 심사 기준에 미달하는 항목이 있어 재검토가 필요합니다."
        
        return f"""
        <section class="narrative final-judgment">
            <h2>🔍 기술 검토 결론 (Technical Conclusion)</h2>
            
            <div class="judgment-box">
                <p class="judgment">{judgment}</p>
                <p class="narrative reason">{reason}</p>
            </div>
        </section>
        """


# ========== FINANCIAL FEASIBILITY NARRATIVE GENERATOR ==========

class FinancialFeasibilityNarrativeGenerator(BaseNarrativeGenerator):
    """
    Narrative Generator for Financial Feasibility Report
    
    Target Audience: 투자자 / 재무 담당자
    Focus: ROI, NPV, IRR, 수익성
    """
    
    def __init__(self):
        super().__init__()
        self.report_type = "financial_feasibility"
    
    def executive_summary(self, modules_data: Dict) -> str:
        m2_data = modules_data.get("M2", {})
        m5_data = modules_data.get("M5", {})
        
        land_value = m2_data.get("land_value", 0)
        npv = m5_data.get("npv", 0)
        irr = m5_data.get("irr", 0)
        roi = m5_data.get("roi", 0)
        
        return f"""
        <section class="narrative executive-summary">
            <h2>💰 재무 타당성 분석 요약 (Financial Feasibility Summary)</h2>
            
            <p class="narrative">
                본 보고서는 LH 공공기여형 민간임대주택 사업의 재무적 타당성을 
                투자자 관점에서 분석한 결과입니다.
            </p>
            
            <p class="narrative">
                토지 매입가는 <strong>{land_value:,}원</strong> 기준이며, 
                이를 포함한 총 투자 대비 순현재가치(NPV)는 
                <strong>{npv:,}원</strong>으로 산출되었습니다.
            </p>
            
            <p class="narrative">
                내부수익률(IRR)은 <strong>{irr:.2f}%</strong>, 
                투자수익률(ROI)은 <strong>{roi:.2f}%</strong> 수준이며, 
                이는 일반적인 LH 사업 기준과 비교하여 
                {'양호한' if irr > 7 else '검토가 필요한'} 수준입니다.
            </p>
            
            <p class="narrative">
                아래 상세 분석에서는 투자금 구조, 수익 예측, 
                리스크 요인을 포함한 종합적인 재무 평가를 제공합니다.
            </p>
        </section>
        """
    
    def transitions(self, from_module: str, to_module: str) -> str:
        transition_map = {
            ("M2", "M4"): """
                <p class="narrative transition">
                    토지 매입가를 확인했으니, 건축 규모에 따른 총 사업비를 산정합니다.
                </p>
            """,
            ("M4", "M5"): """
                <p class="narrative transition">
                    건축 규모가 정해졌으므로, 이제 총 투자금 대비 
                    예상 수익을 재무 지표로 분석합니다.
                </p>
            """
        }
        
        text = transition_map.get((from_module, to_module))
        return text if text else ""
    
    def final_judgment(self, modules_data: Dict) -> str:
        m5_data = modules_data.get("M5", {})
        npv = m5_data.get("npv", 0)
        irr = m5_data.get("irr", 0)
        
        if npv > 0 and irr > 7:
            judgment = "✅ 재무적으로 투자를 <strong>추천합니다</strong>."
            reason = f"NPV가 양수({npv:,}원)이고 IRR이 {irr:.2f}%로 기준을 충족합니다."
        elif npv > 0:
            judgment = "⚠️ <strong>조건부 승인</strong>을 권장합니다."
            reason = "NPV는 양수이나 IRR이 낮아 추가 검토가 필요합니다."
        else:
            judgment = "❌ 재무적으로 <strong>부적합</strong>합니다."
            reason = f"NPV가 음수({npv:,}원)로 투자 가치가 없습니다."
        
        return f"""
        <section class="narrative final-judgment">
            <h2>📊 재무 의견 (Financial Opinion)</h2>
            
            <div class="judgment-box">
                <p class="judgment">{judgment}</p>
                <p class="narrative reason">{reason}</p>
            </div>
        </section>
        """


# ========== QUICK CHECK NARRATIVE GENERATOR ==========

class QuickCheckNarrativeGenerator(BaseNarrativeGenerator):
    """
    Narrative Generator for Quick Check Report
    
    Target Audience: 의사결정권자 (빠른 GO/NO-GO 판단)
    Focus: 최소한의 narrative, 결론 중심
    """
    
    def __init__(self):
        super().__init__()
        self.report_type = "quick_check"
    
    def executive_summary(self, modules_data: Dict) -> str:
        """
        [vABSOLUTE-FINAL-10] FORCE ACTUAL VALUES - NO MORE N/A
        
        CRITICAL RULE: ALL numbers MUST come from modules_data
        NO generic templates, NO "N/A (검증 필요)" fallbacks
        """
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        m2_data = modules_data.get("M2", {})
        m4_data = modules_data.get("M4", {})
        
        # Extract actual values with proper fallbacks
        npv = m5_data.get("npv", m5_data.get("NPV", 0))
        irr = m5_data.get("irr", m5_data.get("IRR", 0))
        roi = m5_data.get("roi", m5_data.get("ROI", 0))
        lh_decision = m6_data.get("decision", m6_data.get("Decision", "검토 중"))
        lh_grade = m6_data.get("grade", m6_data.get("Grade", "등급 산정 중"))
        total_units = m4_data.get("total_units", m5_data.get("total_units", 0))
        land_value = m2_data.get("land_value_total", m2_data.get("total_land_value", 0))
        
        # Format numbers
        npv_str = f"{int(npv):,}원" if npv and npv != 0 else "산출 불가"
        irr_str = f"{float(irr)*100:.2f}%" if irr and irr != 0 else "산출 불가"
        roi_str = f"{float(roi)*100:.2f}%" if roi and roi != 0 else "산출 불가"
        units_str = f"{int(total_units)}세대" if total_units and total_units != 0 else "미확정"
        land_str = f"{int(land_value):,}원" if land_value and land_value != 0 else "평가 중"
        
        # Generate decision summary based on actual NPV and decision
        if npv and float(npv) > 0:
            if "승인" in str(lh_decision) or "적합" in str(lh_decision):
                decision_text = "본 사업은 재무적 타당성과 LH 승인 가능성을 모두 충족하는 것으로 분석되었습니다."
                recommendation = "즉시 추진 권장"
            else:
                decision_text = "재무적으로는 타당하나 LH 승인 기준에 대한 추가 보완이 필요합니다."
                recommendation = "조건부 추진 검토"
        else:
            decision_text = "현재 조건에서는 재무적 타당성이 미흡한 것으로 평가됩니다."
            recommendation = "사업 조건 재검토 필요"
        
        return f"""
        <section class="narrative executive-summary">
            <h2>⚡ 핵심 결론 (Quick Decision Check)</h2>
            
            <p class="narrative">
                <strong>1. 재무 분석 결과:</strong><br/>
                본 사업의 순현재가치(NPV)는 <strong>{npv_str}</strong>로 산출되었으며,
                내부수익률(IRR)은 <strong>{irr_str}</strong>, 
                투자수익률(ROI)은 <strong>{roi_str}</strong>입니다.
            </p>
            
            <p class="narrative">
                <strong>2. 개발 규모:</strong><br/>
                예상 건축 세대수는 <strong>{units_str}</strong>이며,
                토지 가치는 <strong>{land_str}</strong>로 평가됩니다.
            </p>
            
            <p class="narrative">
                <strong>3. LH 승인 전망:</strong><br/>
                LH 심사 결과는 <strong>{lh_decision}</strong> (예상 등급: <strong>{lh_grade}</strong>)로 예측됩니다.
            </p>
            
            <p class="narrative">
                <strong>종합 판단:</strong> {decision_text}
                <br/><strong>권장 액션:</strong> {recommendation}
            </p>
        </section>
        """
    
    def transitions(self, from_module: str, to_module: str) -> str:
        # Quick check는 transition 최소화
        return ""
    
    def final_judgment(self, modules_data: Dict) -> str:
        """
        [vABSOLUTE-FINAL-10] DETAILED FINAL JUDGMENT WITH ACTUAL VALUES
        
        CRITICAL: Must reference specific numbers from modules_data
        NO generic "추진 가능" without supporting evidence
        """
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        m2_data = modules_data.get("M2", {})
        m4_data = modules_data.get("M4", {})
        
        npv = m5_data.get("npv", m5_data.get("NPV", 0))
        irr = m5_data.get("irr", m5_data.get("IRR", 0))
        lh_decision = m6_data.get("decision", m6_data.get("Decision", "검토 중"))
        lh_grade = m6_data.get("grade", m6_data.get("Grade", ""))
        total_units = m4_data.get("total_units", m5_data.get("total_units", 0))
        confidence = m2_data.get("confidence", m2_data.get("Confidence", 0))
        
        # Format numbers
        npv_str = f"{int(npv):,}원" if npv and npv != 0 else "산출 불가"
        irr_pct = float(irr) * 100 if irr else 0
        
        # Determine judgment based on actual data
        if npv and float(npv) > 0 and "승인" in str(lh_decision).lower() or "적합" in str(lh_decision):
            judgment_emoji = "✅"
            judgment_text = "GO - 즉시 추진 권장"
            reason = f"""
                <strong>추진 근거:</strong><br/>
                • 순현재가치(NPV) {npv_str}로 재무적 타당성 확보<br/>
                • 내부수익률(IRR) {irr_pct:.2f}%로 투자 수익성 양호<br/>
                • LH 심사 결과 '{lh_decision}' (등급: {lh_grade})로 승인 가능성 높음<br/>
                • 예상 {total_units}세대 규모로 사업성 확보 가능<br/>
                <strong>권장 사항:</strong> 즉시 사업 추진 및 LH 공모 참여를 권장합니다.
            """
        elif npv and float(npv) > 0:
            judgment_emoji = "⚠️"
            judgment_text = "CONDITIONAL - 조건부 추진 검토"
            reason = f"""
                <strong>검토 필요 사항:</strong><br/>
                • 순현재가치(NPV) {npv_str}로 재무적으로는 타당하나<br/>
                • LH 승인 기준 '{lh_decision}'로 추가 보완 필요<br/>
                • 내부수익률(IRR) {irr_pct:.2f}%를 감안한 리스크 관리 필요<br/>
                <strong>권장 사항:</strong> LH 승인 기준 보완 후 추진을 검토하시기 바랍니다.
            """
        else:
            judgment_emoji = "❌"
            judgment_text = "NO-GO - 추진 재검토 필요"
            reason = f"""
                <strong>재검토 사유:</strong><br/>
                • 순현재가치(NPV) {npv_str}로 재무적 타당성 미흡<br/>
                • LH 심사 예측 결과: {lh_decision}<br/>
                • 현재 조건에서는 수익성 확보 어려움<br/>
                <strong>권장 사항:</strong> 사업 조건 재검토 또는 대안 모색이 필요합니다.
            """
        
        return f"""
        <section class="narrative final-judgment">
            <h2>🎯 최종 결정 (Final Decision)</h2>
            <div class="judgment-box" style="
                background: #f8f9fa;
                border-left: 4px solid #0d6efd;
                padding: 20px;
                margin: 20px 0;
            ">
                <p class="judgment" style="font-size: 20px; font-weight: bold; color: #212529;">
                    {judgment_emoji} {judgment_text}
                </p>
                <div style="margin-top: 15px; color: #495057; line-height: 1.8;">
                    {reason}
                </div>
            </div>
        </section>
        """


# ========== ALL-IN-ONE NARRATIVE GENERATOR ==========

class AllInOneNarrativeGenerator(BaseNarrativeGenerator):
    """
    Narrative Generator for All-in-One Comprehensive Report
    
    Target Audience: 전체 (종합 보고서)
    Focus: 모든 모듈 포괄, 상세 설명
    """
    
    def __init__(self):
        super().__init__()
        self.report_type = "all_in_one"
    
    def executive_summary(self, modules_data: Dict) -> str:
        """
        [vABSOLUTE-FINAL-10] All-in-One MUST show actual KPI values
        """
        # Extract actual values
        m2_data = modules_data.get("M2", {})
        m4_data = modules_data.get("M4", {})
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        
        land_value = m2_data.get("land_value_total", m2_data.get("total_land_value", 0))
        total_units = m4_data.get("total_units", m5_data.get("total_units", 0))
        npv = m5_data.get("npv", m5_data.get("NPV", 0))
        irr = m5_data.get("irr", m5_data.get("IRR", 0))
        roi = m5_data.get("roi", m5_data.get("ROI", 0))
        lh_decision = m6_data.get("decision", m6_data.get("Decision", ""))
        
        # Format safely
        land_str = f"{int(land_value):,}원" if land_value and land_value != 0 else "평가 불가"
        units_str = f"{int(total_units)}세대" if total_units and total_units != 0 else "미확정"
        npv_str = f"{int(npv):,}원" if npv and npv != 0 else "산출 불가"
        irr_str = f"{float(irr)*100:.2f}%" if irr and irr != 0 else "산출 불가"
        roi_str = f"{float(roi)*100:.2f}%" if roi and roi != 0 else "산출 불가"
        lh_str = str(lh_decision) if lh_decision else "심사 대기"
        
        return f"""
        <section class="narrative executive-summary">
            <h2>📚 종합 분석 보고서 (Comprehensive Report)</h2>
            
            <p class="narrative">
                본 보고서는 LH 공공기여형 민간임대주택 사업에 대한 
                <strong>완전한 종합 분석</strong> 결과입니다.
            </p>
            
            <p class="narrative">
                <strong>핵심 분석 결과:</strong><br/>
                • 토지 가치: <strong>{land_str}</strong><br/>
                • 건축 규모: <strong>{units_str}</strong><br/>
                • 순현재가치(NPV): <strong>{npv_str}</strong><br/>
                • 내부수익률(IRR): <strong>{irr_str}</strong><br/>
                • 투자수익률(ROI): <strong>{roi_str}</strong><br/>
                • LH 심사 전망: <strong>{lh_str}</strong>
            </p>
            
            <p class="narrative">
                토지 가치 평가(M2), LH 선호 주택유형(M3), 건축 규모 결정(M4), 
                사업성 분석(M5), LH 심사 예측(M6) 등 5개 모듈의 
                분석 결과를 모두 포함하고 있습니다.
            </p>
            
            <p class="narrative">
                상세 내용은 아래 5개 모듈 분석 결과를 참고하시기 바라며, 
                최종 의사결정은 전문가 자문 후 신중하게 내리시기 바랍니다.
            </p>
        </section>
        """
    
    def transitions(self, from_module: str, to_module: str) -> str:
        # Comprehensive report는 각 모듈 간 연결 강조
        transition_map = {
            ("M2", "M3"): "토지 가치를 확인했으니, LH가 선호하는 주택유형을 분석합니다.",
            ("M3", "M4"): "선호 유형이 결정되었으므로, 건축 가능한 규모를 산정합니다.",
            ("M4", "M5"): "건축 규모를 바탕으로 사업의 재무 타당성을 검토합니다.",
            ("M5", "M6"): "사업성 결과를 확인했으니, LH 심사 통과 가능성을 예측합니다."
        }
        
        text = transition_map.get((from_module, to_module))
        if not text:
            return ""
        
        return f'<p class="narrative transition">{text}</p>'
    
    def final_judgment(self, modules_data: Dict) -> str:
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        
        npv = m5_data.get("npv", 0)
        lh_decision = m6_data.get("decision", "")
        
        if npv > 0 and lh_decision not in ["부적합", "탈락"]:
            judgment = "✅ 종합적으로 사업 <strong>추진을 추천합니다</strong>."
        elif npv > 0:
            judgment = "⚠️ <strong>조건부 추진</strong>을 권장합니다."
        else:
            judgment = "❌ 현 조건에서는 사업 추진이 <strong>부적합</strong>합니다."
        
        return f"""
        <section class="narrative final-judgment">
            <h2>🎯 종합 의견 (Comprehensive Opinion)</h2>
            
            <div class="judgment-box">
                <p class="judgment">{judgment}</p>
                <p class="narrative">
                    위 의견은 5개 모듈의 종합 분석 결과를 기반으로 하며, 
                    최종 투자 결정은 전문가와 협의 후 내리시기 바랍니다.
                </p>
            </div>
        </section>
        """


# ========== EXECUTIVE SUMMARY NARRATIVE GENERATOR ==========

class ExecutiveSummaryNarrativeGenerator(BaseNarrativeGenerator):
    """
    Narrative Generator for Executive Summary Report
    
    Target Audience: 경영진 (2페이지 요약)
    Focus: 핵심 지표, 간결한 결론
    """
    
    def __init__(self):
        super().__init__()
        self.report_type = "executive_summary"
    
    def executive_summary(self, modules_data: Dict) -> str:
        """
        [vABSOLUTE-FINAL-10] Executive Summary - Use correct key names
        """
        m2_data = modules_data.get("M2", {})
        m4_data = modules_data.get("M4", {})
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        
        # Use correct key names with fallbacks
        land_value = m2_data.get("land_value_total", m2_data.get("total_land_value", 0))
        total_units = m4_data.get("total_units", m5_data.get("total_units", 0))
        npv = m5_data.get("npv", m5_data.get("NPV", 0))
        irr = m5_data.get("irr", m5_data.get("IRR", 0))
        lh_decision = m6_data.get("decision", m6_data.get("Decision", ""))
        
        # Format safely
        land_str = f"{int(land_value):,}원" if land_value and land_value != 0 else "평가 불가"
        units_str = f"{int(total_units):,}세대" if total_units and total_units != 0 else "미확정"
        npv_str = f"{int(npv):,}원" if npv and npv != 0 else "산출 불가"
        irr_str = f"{float(irr)*100:.2f}%" if irr and irr != 0 else "산출 불가"
        npv_status = "수익 가능" if npv and float(npv) > 0 else "손실 예상" if npv and float(npv) < 0 else "미확정"
        lh_str = str(lh_decision) if lh_decision else "심사 대기"
        
        return f"""
        <section class="narrative executive-summary">
            <h2>📌 Executive Summary (경영진용)</h2>
            
            <p class="narrative">
                <strong>투자 대상:</strong> 토지 가치 <strong>{land_str}</strong>
            </p>
            
            <p class="narrative">
                <strong>개발 규모:</strong> 총 <strong>{units_str}</strong>
            </p>
            
            <p class="narrative">
                <strong>재무 평가:</strong> NPV <strong>{npv_str}</strong> ({npv_status})<br/>
                IRR <strong>{irr_str}</strong>
            </p>
            
            <p class="narrative">
                <strong>LH 승인 전망:</strong> <strong>{lh_str}</strong>
            </p>
        </section>
        """
    
    def transitions(self, from_module: str, to_module: str) -> str:
        # Executive summary는 transition 최소화
        return ""
    
    def final_judgment(self, modules_data: Dict) -> str:
        m5_data = modules_data.get("M5", {})
        npv = m5_data.get("npv", 0)
        
        if npv > 0:
            judgment = "✅ <strong>추천합니다</strong>"
        else:
            judgment = "❌ 투자 <strong>부적합</strong>"
        
        return f"""
        <section class="narrative final-judgment">
            <h2>🎯 의사결정 (Decision)</h2>
            <p class="judgment">{judgment}</p>
        </section>
        """


# ========== NARRATIVE GENERATOR FACTORY ==========

class NarrativeGeneratorFactory:
    """
    Factory for creating Narrative Generators by report type
    """
    
    _generators = {
        "landowner_summary": LandownerNarrativeGenerator,
        "lh_technical": LHTechnicalNarrativeGenerator,
        "financial_feasibility": FinancialFeasibilityNarrativeGenerator,
        "quick_check": QuickCheckNarrativeGenerator,
        "all_in_one": AllInOneNarrativeGenerator,
        "executive_summary": ExecutiveSummaryNarrativeGenerator,
    }
    
    @staticmethod
    def get(report_type: str) -> BaseNarrativeGenerator:
        """
        Get Narrative Generator for report type
        
        Args:
            report_type: One of the 6 final report types
        
        Returns:
            Concrete NarrativeGenerator instance
        
        Raises:
            ValueError: If report_type is unknown
        """
        generator_class = NarrativeGeneratorFactory._generators.get(report_type)
        
        if not generator_class:
            raise ValueError(
                f"Unknown report type: {report_type}. "
                f"Valid types: {list(NarrativeGeneratorFactory._generators.keys())}"
            )
        
        logger.info(f"[NarrativeFactory] Creating {generator_class.__name__} for {report_type}")
        return generator_class()
    
    @staticmethod
    def list_available_types() -> list:
        """Get list of available report types"""
        return list(NarrativeGeneratorFactory._generators.keys())
