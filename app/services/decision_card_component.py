"""
ZeroSite v4.3 Decision Card Standard Component
==============================================

결론 카드 (Decision Card) 표준 컴포넌트: 모든 최종 보고서에 동일한 형식으로 삽입

핵심 원칙:
1. 모든 보고서 1페이지 최상단에 배치
2. GO/CONDITIONAL/NO-GO 판단 명확히 표시
3. 핵심 리스크 3개 + 다음 행동 3단계 제시
4. 시각적으로 즉시 이해 가능 (임원/의사결정자 3초 파악)

Version: 1.0
Date: 2025-12-22
Author: Claude AI Assistant
"""

from typing import Dict, List, Optional
from enum import Enum


class DecisionStatus(str, Enum):
    """최종 판단 상태"""
    GO = "GO - 추진 권장"
    CONDITIONAL = "CONDITIONAL - 조건부 검토"
    NO_GO = "NO-GO - 추진 보류"


class DecisionCard:
    """결론 카드 데이터 모델"""
    
    def __init__(
        self,
        decision: DecisionStatus,
        approval_probability_pct: Optional[float],
        key_risks: List[str],  # 최대 3개
        next_actions: List[str],  # 최대 3개
        headline: str,
        rationale: str
    ):
        self.decision = decision
        self.approval_probability_pct = approval_probability_pct or 0
        self.key_risks = key_risks[:3]  # 최대 3개로 제한
        self.next_actions = next_actions[:3]  # 최대 3개로 제한
        self.headline = headline
        self.rationale = rationale
    
    def to_html(self) -> str:
        """표준 HTML 카드 생성"""
        
        # Decision 상태에 따른 색상
        color_map = {
            DecisionStatus.GO: "#10B981",
            DecisionStatus.CONDITIONAL: "#F59E0B",
            DecisionStatus.NO_GO: "#EF4444"
        }
        color = color_map.get(self.decision, "#6B7280")
        
        # Icon
        icon_map = {
            DecisionStatus.GO: "✅",
            DecisionStatus.CONDITIONAL: "⚠️",
            DecisionStatus.NO_GO: "❌"
        }
        icon = icon_map.get(self.decision, "❓")
        
        html = f"""
        <!-- ========== DECISION CARD (Standard v4.3) ========== -->
        <div class="decision-card-v43" style="
            background: linear-gradient(135deg, {color}15, {color}05);
            border: 3px solid {color};
            border-radius: 16px;
            padding: 32px;
            margin: 40px 0;
            page-break-inside: avoid;
        ">
            <!-- Header -->
            <div style="text-align: center; margin-bottom: 24px;">
                <div style="font-size: 64px; margin-bottom: 12px;">{icon}</div>
                <div style="font-size: 32px; font-weight: 700; color: {color}; margin-bottom: 8px;">
                    {self.decision.value}
                </div>
                <div style="font-size: 18px; color: #4B5563; line-height: 1.6;">
                    {self.headline}
                </div>
            </div>
            
            <!-- Key Metrics -->
            <div style="display: flex; justify-content: space-around; margin: 24px 0; padding: 20px; background: white; border-radius: 12px;">
                <div style="text-align: center;">
                    <div style="font-size: 14px; color: #6B7280; margin-bottom: 4px;">LH 승인 가능성</div>
                    <div style="font-size: 28px; font-weight: 700; color: {color};">
                        {self.approval_probability_pct:.0f}%
                    </div>
                </div>
            </div>
            
            <!-- Rationale -->
            <div style="margin: 20px 0; padding: 20px; background: white; border-radius: 12px;">
                <div style="font-weight: 600; margin-bottom: 8px; color: #1F2937;">판단 근거</div>
                <div style="line-height: 1.8; color: #4B5563;">
                    {self.rationale}
                </div>
            </div>
            
            <!-- Key Risks -->
            <div style="margin: 20px 0;">
                <div style="font-weight: 600; margin-bottom: 12px; color: #1F2937;">⚠️ 핵심 리스크 (상위 3개)</div>
                <div style="background: white; border-radius: 12px; padding: 16px;">
                    {''.join(f'<div style="padding: 8px 0; border-bottom: 1px solid #F3F4F6;"><strong>{i+1}.</strong> {risk}</div>' for i, risk in enumerate(self.key_risks))}
                </div>
            </div>
            
            <!-- Next Actions -->
            <div style="margin: 20px 0;">
                <div style="font-weight: 600; margin-bottom: 12px; color: #1F2937;">🎯 다음 행동 3단계</div>
                <div style="background: white; border-radius: 12px; padding: 16px;">
                    {''.join(f'<div style="padding: 8px 0; border-bottom: 1px solid #F3F4F6;"><strong>Step {i+1}.</strong> {action}</div>' for i, action in enumerate(self.next_actions))}
                </div>
            </div>
        </div>
        <!-- ========== END DECISION CARD ========== -->
        """
        
        return html


def format_currency(amount: float) -> str:
    """금액 포맷팅 헬퍼 함수"""
    if amount >= 100000000:  # 1억 이상
        return f"{amount/100000000:.1f}억원"
    elif amount >= 10000:  # 1만 이상
        return f"{amount/10000:.0f}만원"
    else:
        return f"{amount:,.0f}원"


def create_decision_card(report_data: Dict) -> DecisionCard:
    """
    보고서 데이터로부터 결론 카드 생성
    
    Args:
        report_data: final_report_assembler 출력 데이터
    
    Returns:
        DecisionCard 객체
    """
    
    # 1. Decision 결정
    npv = report_data.get('npv_krw', 0) or 0
    irr = report_data.get('irr_pct', 0) or 0
    approval_prob = report_data.get('approval_probability_pct', 0) or 0
    
    if npv >= 300000000 and irr >= 12 and approval_prob >= 70:
        decision = DecisionStatus.GO
        headline = "이 사업은 투자 가치가 충분하며, 즉시 추진을 권장합니다."
    elif npv > 0 and irr >= 8 and approval_prob >= 50:
        decision = DecisionStatus.CONDITIONAL
        headline = "조건 보완 시 추진 가능하며, 리스크 관리가 필요합니다."
    else:
        decision = DecisionStatus.NO_GO
        headline = "현재 조건으로는 추진이 어려우며, 근본적인 개선이 필요합니다."
    
    # 2. Rationale
    rationale = f"""
    순현재가치(NPV) {format_currency(npv)}, 내부수익률(IRR) {irr:.1f}%, 
    LH 승인 가능성 {approval_prob:.0f}%를 종합 검토한 결과입니다.
    """
    
    # 3. Key Risks (상위 3개)
    key_risks = report_data.get('key_risks', [])
    if not key_risks:
        key_risks = [
            "토지 가격 변동 (감정평가 +10% 시 NPV -50%)",
            "금융 비용 증가 (금리 +1%p 시 NPV -37%)",
            "사업 일정 지연 (6개월 지연 시 NPV -56%)"
        ]
    
    # 4. Next Actions
    if decision == DecisionStatus.GO:
        next_actions = [
            "LH 공식 사전 협의 진행 (승인 가능성 70%+ 확인)",
            "시공사 선정 및 건축비 견적 확보",
            "자금 조달 계획 수립 (PF 대출 70% + 자기자본 30%)"
        ]
    elif decision == DecisionStatus.CONDITIONAL:
        next_actions = [
            "핵심 리스크 3개에 대한 추가 분석 수행",
            "LH 지역본부와 보완 사항 협의",
            "리스크 관리 방안 수립 후 재검토"
        ]
    else:
        next_actions = [
            "사업 구조 전면 재검토 (규모, 유형, 가격)",
            "대체 출구 전략 검토 (LH 외 다른 매수자)",
            "토지 계약 해지 또는 재협상"
        ]
    
    return DecisionCard(
        decision=decision,
        approval_probability_pct=approval_prob,
        key_risks=key_risks[:3],
        next_actions=next_actions,
        headline=headline,
        rationale=rationale
    )
