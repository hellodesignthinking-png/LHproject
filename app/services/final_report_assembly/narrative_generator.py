"""
Narrative Layer for Final Reports

Provides context, interpretation, and decision guidance WITHOUT calculating data.
This layer transforms "module HTML" into "decision-ready documents".

CRITICAL PRINCIPLE:
- NO calculation or data processing
- ONLY interpretation and context
- Uses module results AS-IS, adds decision framing

Author: ZeroSite Backend Team
Date: 2025-12-22
Phase: 3 (PROMPT 5 - Narrative Layer)
"""

from typing import Dict, Literal
from dataclasses import dataclass


@dataclass
class NarrativeSection:
    """A narrative section to be inserted in final report"""
    section_id: str
    title_kr: str
    content_html: str
    position: Literal["before_modules", "after_modules", "between_modules"]
    target_audience: str


class ReportNarrativeGenerator:
    """
    Generates narrative content for Final Reports
    
    This is NOT a calculator - it only provides context and interpretation
    for pre-calculated module results.
    """
    
    @staticmethod
    def generate_executive_intro(
        report_type: str,
        context_id: str,
        parcel_address: str = "해당 토지"
    ) -> NarrativeSection:
        """
        Generate executive introduction for report
        
        Args:
            report_type: Type of report being generated
            context_id: Context ID for reference
            parcel_address: Address of the parcel
            
        Returns:
            NarrativeSection with executive intro
        """
        
        intros = {
            "landowner_summary": f"""
                <div class="executive-intro">
                    <h2>Executive Summary (토지주용)</h2>
                    <p class="intro-context">
                        본 보고서는 <strong>{parcel_address}</strong>의 LH 영구임대주택 사업 타당성을 
                        <strong>토지주 관점</strong>에서 분석한 요약본입니다.
                    </p>
                    <p class="intro-purpose">
                        <strong>핵심 질문:</strong> 이 토지로 LH 사업을 진행할 경우, 
                        투자 대비 수익이 확보되는가? LH 승인 가능성은 얼마나 되는가?
                    </p>
                    <p class="intro-scope">
                        본 보고서는 토지 가치 평가(M2), 사업성 분석(M5), LH 심사 예측(M6)을 중심으로 
                        의사결정에 필요한 핵심 정보를 제공합니다.
                    </p>
                </div>
            """,
            
            "lh_technical": f"""
                <div class="executive-intro">
                    <h2>Technical Review Summary (LH 기술검토용)</h2>
                    <p class="intro-context">
                        본 보고서는 <strong>{parcel_address}</strong>의 LH 영구임대주택 사업을 
                        <strong>LH 기술 검토 기준</strong>으로 분석한 상세 보고서입니다.
                    </p>
                    <p class="intro-purpose">
                        <strong>검토 목적:</strong> LH 정책 부합성, 기술적 실현 가능성, 
                        심사 통과 가능성을 종합적으로 판단합니다.
                    </p>
                    <p class="intro-scope">
                        본 보고서는 선호 주택유형(M3), 건축 규모(M4), LH 내부 심사(M6)를 중심으로 
                        기술적 타당성을 검증합니다.
                    </p>
                </div>
            """,
            
            "quick_check": f"""
                <div class="executive-intro">
                    <h2>Quick Decision Check</h2>
                    <p class="intro-context">
                        <strong>{parcel_address}</strong> - LH 사업 GO/NO-GO 판단 (5분 검토용)
                    </p>
                    <p class="intro-purpose">
                        <strong>핵심 결론만 확인하십시오:</strong> 
                        사업성 평가 + LH 승인 가능성 = 최종 의사결정
                    </p>
                </div>
            """,
            
            "financial_feasibility": f"""
                <div class="executive-intro">
                    <h2>Financial Feasibility Analysis (사업성 중심)</h2>
                    <p class="intro-context">
                        본 보고서는 <strong>{parcel_address}</strong>의 LH 사업을 
                        <strong>재무적 관점</strong>에서 분석합니다.
                    </p>
                    <p class="intro-purpose">
                        <strong>재무 평가 핵심:</strong> 투자금 회수 가능성, 수익률(IRR), 
                        순현재가치(NPV), 리스크 요인을 종합 검토합니다.
                    </p>
                    <p class="intro-scope">
                        토지 매입가(M2), 사업 규모(M4), 재무 분석(M5)을 통해 
                        투자 의사결정을 지원합니다.
                    </p>
                </div>
            """,
            
            "all_in_one": f"""
                <div class="executive-intro">
                    <h2>Comprehensive Analysis Report (전체 통합)</h2>
                    <p class="intro-context">
                        본 보고서는 <strong>{parcel_address}</strong>의 LH 영구임대주택 사업에 대한 
                        <strong>완전한 종합 분석</strong>입니다.
                    </p>
                    <p class="intro-purpose">
                        <strong>분석 범위:</strong> 토지 가치, 선호 주택유형, 건축 규모, 사업성, 
                        LH 심사 예측을 모두 포함한 전체 분석 결과를 제공합니다.
                    </p>
                    <p class="intro-scope">
                        5개 모듈(M2~M6)의 분석 결과를 통해 사업의 모든 측면을 이해하고 
                        의사결정할 수 있도록 구성되었습니다.
                    </p>
                </div>
            """,
            
            "executive_summary": f"""
                <div class="executive-intro">
                    <h2>Executive Summary (경영진용)</h2>
                    <p class="intro-context">
                        <strong>{parcel_address}</strong> - LH 사업 투자 의사결정 보고서
                    </p>
                    <p class="intro-purpose">
                        <strong>의사결정 포인트:</strong> 투자 가치, 수익성, 승인 가능성 
                        3가지 핵심 지표를 중심으로 GO/NO-GO 판단을 지원합니다.
                    </p>
                    <p class="intro-scope">
                        토지 평가, 재무 분석, LH 승인 예측을 통해 
                        경영 의사결정에 필요한 핵심 정보를 제공합니다.
                    </p>
                </div>
            """
        }
        
        content = intros.get(report_type, intros["executive_summary"])
        
        return NarrativeSection(
            section_id="executive_intro",
            title_kr="요약",
            content_html=content,
            position="before_modules",
            target_audience=report_type
        )
    
    @staticmethod
    def generate_module_context(
        report_type: str,
        module_id: Literal["M2", "M3", "M4", "M5", "M6"]
    ) -> NarrativeSection:
        """
        Generate context/framing for a specific module in the report
        
        Args:
            report_type: Type of report
            module_id: Module being contextualized
            
        Returns:
            NarrativeSection with module context
        """
        
        # Context depends on report type and target audience
        contexts = {
            ("landowner_summary", "M2"): """
                <div class="module-context">
                    <p class="context-frame">
                        <strong>토지주 관점:</strong> 이 평가액은 LH 매입가의 기준이 됩니다. 
                        LH는 일반적으로 감정평가액의 110% 수준에서 매입하므로, 
                        아래 금액을 기준으로 실제 매각 가능 금액을 판단하십시오.
                    </p>
                </div>
            """,
            
            ("landowner_summary", "M5"): """
                <div class="module-context">
                    <p class="context-frame">
                        <strong>수익성 판단:</strong> 아래 수익률(IRR)과 순현재가치(NPV)가 
                        투자 대비 실제 수익을 의미합니다. 
                        Grade D 이상이면 사업 진행 가능, C 이하면 재검토가 필요합니다.
                    </p>
                </div>
            """,
            
            ("lh_technical", "M3"): """
                <div class="module-context">
                    <p class="context-frame">
                        <strong>LH 정책 부합성:</strong> LH가 선호하는 주택유형과 
                        본 토지의 특성이 얼마나 일치하는지 평가한 결과입니다. 
                        85점 이상이면 정책 부합도가 높다고 판단됩니다.
                    </p>
                </div>
            """,
            
            ("lh_technical", "M4"): """
                <div class="module-context">
                    <p class="context-frame">
                        <strong>기술적 실현 가능성:</strong> 법적 용적률과 인센티브를 반영한 
                        최대 건축 규모입니다. LH 사업은 최소 20세대 이상이 필요하므로, 
                        아래 세대수가 기준을 충족하는지 확인하십시오.
                    </p>
                </div>
            """,
            
            ("financial_feasibility", "M5"): """
                <div class="module-context">
                    <p class="context-frame">
                        <strong>재무 지표 해석:</strong>
                        • NPV > 0: 투자 가치 있음<br>
                        • IRR > 7%: 일반적인 LH 사업 기준 충족<br>
                        • Grade B 이상: 재무적으로 안정적<br>
                        아래 수치를 기준으로 투자 의사결정하십시오.
                    </p>
                </div>
            """,
        }
        
        context_key = (report_type, module_id)
        content = contexts.get(context_key, "")
        
        if not content:
            return None
        
        return NarrativeSection(
            section_id=f"context_{module_id}",
            title_kr=f"{module_id} 해석",
            content_html=content,
            position="before_modules",
            target_audience=report_type
        )
    
    @staticmethod
    def generate_risk_notice(report_type: str) -> NarrativeSection:
        """
        Generate standard risk notice/disclaimer
        
        Args:
            report_type: Type of report
            
        Returns:
            NarrativeSection with risk notice
        """
        
        content = """
            <div class="risk-notice">
                <h2>⚠️ 리스크 고지 (Risk Notice)</h2>
                <div class="risk-content">
                    <p><strong>본 분석 보고서는 의사결정 참고 자료이며, 다음 사항에 유의하십시오:</strong></p>
                    <ul>
                        <li>🔴 <strong>LH 정책 변동:</strong> LH 매입 정책, 심사 기준은 수시로 변경될 수 있습니다.</li>
                        <li>🔴 <strong>시장 변동:</strong> 부동산 시장, 금리, 공사비는 분석 시점 이후 변동될 수 있습니다.</li>
                        <li>🔴 <strong>규제 변경:</strong> 용도지역, 지구단위계획 등 규제는 변경될 수 있습니다.</li>
                        <li>🔴 <strong>실사 필요:</strong> 본 보고서는 개략 분석이며, 실제 투자 전 정밀 실사가 필요합니다.</li>
                        <li>🔴 <strong>LH 승인 불확실성:</strong> 본 보고서의 승인 예측이 실제 LH 심사 결과를 보장하지 않습니다.</li>
                    </ul>
                    <p class="risk-disclaimer">
                        <strong>최종 투자 의사결정은 투자자 본인의 판단과 책임하에 이루어져야 하며, 
                        본 보고서는 법적 책임을 지지 않습니다.</strong>
                    </p>
                </div>
            </div>
        """
        
        return NarrativeSection(
            section_id="risk_notice",
            title_kr="리스크 고지",
            content_html=content,
            position="after_modules",
            target_audience=report_type
        )
    
    @staticmethod
    def generate_comprehensive_summary(
        report_type: str,
        module_results_summary: Dict[str, str]
    ) -> NarrativeSection:
        """
        Generate comprehensive summary section (for all-in-one report)
        
        Args:
            report_type: Type of report
            module_results_summary: Dict of module IDs to their key findings
            
        Returns:
            NarrativeSection with comprehensive summary
        """
        
        content = """
            <div class="comprehensive-summary">
                <h2>종합 분석 결과 (Comprehensive Summary)</h2>
                <div class="summary-content">
                    <p><strong>5개 모듈 분석 결과를 종합하면:</strong></p>
                    
                    <div class="summary-grid">
                        <div class="summary-item">
                            <h3>📊 M2: 토지 가치</h3>
                            <p>감정평가를 통한 토지 매입 기준가 산정</p>
                        </div>
                        
                        <div class="summary-item">
                            <h3>🏠 M3: 선호 주택유형</h3>
                            <p>LH 정책과 지역 특성을 반영한 최적 주택유형 분석</p>
                        </div>
                        
                        <div class="summary-item">
                            <h3>🏗️ M4: 건축 규모</h3>
                            <p>법적 용적률과 인센티브를 고려한 최대 개발 규모 산정</p>
                        </div>
                        
                        <div class="summary-item">
                            <h3>💰 M5: 사업성 분석</h3>
                            <p>투자 수익률, NPV, IRR 등 재무적 타당성 검증</p>
                        </div>
                        
                        <div class="summary-item">
                            <h3>✅ M6: LH 심사 예측</h3>
                            <p>LH 내부 심사 기준 기반 승인 가능성 예측</p>
                        </div>
                    </div>
                    
                    <p class="summary-conclusion">
                        <strong>최종 판단:</strong> 위 5개 모듈의 결과를 종합하여 
                        사업 진행 여부를 결정하시기 바랍니다.
                    </p>
                </div>
            </div>
        """
        
        return NarrativeSection(
            section_id="comprehensive_summary",
            title_kr="종합 결과",
            content_html=content,
            position="after_modules",
            target_audience=report_type
        )
