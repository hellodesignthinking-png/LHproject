"""
사업성 협상전략 자동 생성 모듈
LH 매입 협상 시 활용 가능한 전략 자동 도출
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class NegotiationStrategy:
    """협상 전략 결과"""
    strategies: List[str]  # 협상 전략 목록
    strengths: List[str]   # 협상 강점 요인
    weaknesses: List[str]  # 협상 약점 요인
    priority_actions: List[str]  # 우선 조치사항


class NegotiationStrategyGenerator:
    """사업성 협상전략 생성기"""
    
    def generate(
        self,
        units: int,                    # 세대수
        construction_cost: float,      # 건축비 (원)
        land_cost: float,              # 토지비 (원)
        business_score: float,         # 사업성 점수 (0-100)
        roi: float,                    # ROI (%)
        lh_purchase_price: float,      # LH 매입단가 (원/세대)
        actual_cost_per_unit: float,   # 실제 세대당 사업비 (원)
        parking_ratio: float,          # 주차 비율 (세대당)
        location_score: float,         # 입지 점수 (0-100)
        demand_score: float,           # 수요 점수 (0-100)
        zone_type: str = "",           # 용도지역
        checklist_pass_rate: float = 0  # 체크리스트 통과율 (%)
    ) -> NegotiationStrategy:
        """
        협상 전략 생성
        
        Returns:
            NegotiationStrategy 객체
        """
        
        strategies = []
        strengths = []
        weaknesses = []
        priority_actions = []
        
        # 1. 사업비 분석
        cost_diff = lh_purchase_price - actual_cost_per_unit
        cost_diff_ratio = (cost_diff / lh_purchase_price * 100) if lh_purchase_price > 0 else 0
        
        if cost_diff_ratio > 5:
            strategies.append(
                f"💰 사업비 대비 LH 매입가가 +{cost_diff_ratio:.1f}% 우위로 협상 여지 있음. "
                f"세대당 {int(cost_diff/10000)}만원의 협상 마진 확보."
            )
            strengths.append(f"사업비 경쟁력 우수 (+{cost_diff_ratio:.1f}%)")
        elif cost_diff_ratio > 0:
            strategies.append(
                f"⚖️ 사업비가 LH 매입가 대비 +{cost_diff_ratio:.1f}% 수준으로 적정. "
                f"추가 협상보다는 현 조건 유지 전략 권장."
            )
        elif cost_diff_ratio > -5:
            strategies.append(
                f"⚠️ 사업비가 LH 매입가 대비 {abs(cost_diff_ratio):.1f}% 초과. "
                f"설계 최적화 또는 토지비 재협상 필요."
            )
            weaknesses.append(f"사업비 초과 ({abs(cost_diff_ratio):.1f}%)")
            priority_actions.append("🔧 건축비 절감 방안 검토 (설계 최적화, VE)")
        else:
            strategies.append(
                f"❌ 사업비가 LH 매입가 대비 {abs(cost_diff_ratio):.1f}% 크게 초과. "
                f"사업 재검토 또는 대폭 비용 절감 필요."
            )
            weaknesses.append(f"사업비 대폭 초과 ({abs(cost_diff_ratio):.1f}%)")
            priority_actions.append("🚨 긴급: 사업비 구조 전면 재검토")
        
        # 2. 주차 기준 분석
        parking_standard = 0.5  # LH 기준
        if parking_ratio >= parking_standard + 0.2:
            strategies.append(
                f"🚗 주차대수가 세대당 {parking_ratio:.2f}대로 LH 기준 대비 {(parking_ratio-parking_standard):.2f}대 여유. "
                f"일부 주차장을 커뮤니티 시설로 전환 가능."
            )
            strengths.append(f"주차 여유분 확보 (+{(parking_ratio-parking_standard)*100:.0f}%)")
        elif parking_ratio >= parking_standard:
            strategies.append(
                f"✅ 주차대수가 세대당 {parking_ratio:.2f}대로 LH 기준 충족. "
                f"주차 완화 신청 시 세대수 증가 가능."
            )
        else:
            deficit = parking_standard - parking_ratio
            strategies.append(
                f"⚠️ 주차대수가 기준 대비 {deficit:.2f}대 부족. "
                f"주차 경감 신청 또는 기계식 주차 도입 검토 필요."
            )
            weaknesses.append(f"주차 기준 미달 (-{deficit*100:.0f}%)")
            priority_actions.append("🚙 주차 확보 방안 수립 (기계식, 인근 부지 활용)")
        
        # 3. 입지 및 수요 분석
        if location_score >= 80 and demand_score >= 70:
            strategies.append(
                f"🌟 입지 점수 {location_score:.0f}점, 수요 점수 {demand_score:.0f}점으로 우수. "
                f"역세권 프리미엄 및 높은 수요를 근거로 매입단가 상향 협상 가능."
            )
            strengths.append(f"우수한 입지 및 수요 (입지 {location_score:.0f}점)")
        elif location_score >= 70 or demand_score >= 60:
            strategies.append(
                f"✅ 입지/수요가 양호한 수준. "
                f"지자체 협의 시 지역 주택 공급 필요성 강조 가능."
            )
        else:
            strategies.append(
                f"⚠️ 입지 점수 {location_score:.0f}점, 수요 점수 {demand_score:.0f}점으로 보통. "
                f"가격 경쟁력으로 승부하는 전략 필요."
            )
            weaknesses.append(f"입지/수요 보통 수준")
        
        # 4. 수익성 분석
        if roi >= 10:
            strategies.append(
                f"📈 ROI {roi:.1f}%로 높은 수익성. "
                f"LH 측에 안정적 수익 구조 강조 가능."
            )
            strengths.append(f"높은 수익성 (ROI {roi:.1f}%)")
        elif roi >= 5:
            strategies.append(
                f"✅ ROI {roi:.1f}%로 적정 수익성 확보. "
                f"장기 안정성을 강조한 협상 전략 수립."
            )
        else:
            strategies.append(
                f"⚠️ ROI {roi:.1f}%로 낮은 수익성. "
                f"LH 지원 조건 개선 또는 사업비 절감 필요."
            )
            weaknesses.append(f"낮은 수익성 (ROI {roi:.1f}%)")
            priority_actions.append("💡 수익성 개선 방안 검토 (운영비 절감, 임대료 재산정)")
        
        # 5. 대지 효율성 분석
        total_cost = construction_cost + land_cost
        land_ratio = (land_cost / total_cost * 100) if total_cost > 0 else 0
        
        if 25 <= land_ratio <= 45:
            strategies.append(
                f"🏗️ 토지비 비중 {land_ratio:.1f}%로 적정. "
                f"대지 효율성이 높아 세대당 토지비 부담이 합리적."
            )
            strengths.append(f"적정한 토지비 비중 ({land_ratio:.1f}%)")
        elif land_ratio < 25:
            strategies.append(
                f"⚠️ 토지비 비중 {land_ratio:.1f}%로 낮음. "
                f"건축비 비중이 높아 설계 효율화 여지 있음."
            )
            priority_actions.append("🔍 건축비 구조 분석 및 최적화")
        else:
            strategies.append(
                f"⚠️ 토지비 비중 {land_ratio:.1f}%로 높음. "
                f"토지비 재협상 또는 용적률 상향 검토 필요."
            )
            weaknesses.append(f"높은 토지비 비중 ({land_ratio:.1f}%)")
            priority_actions.append("🏠 토지비 절감 또는 용적률 상향 협의")
        
        # 6. 규모의 경제
        if units >= 50:
            strategies.append(
                f"🏢 {units}세대 규모로 관리 효율성 우수. "
                f"규모의 경제 효과를 LH에 어필 가능."
            )
            strengths.append(f"적정 사업 규모 ({units}세대)")
        elif units >= 30:
            strategies.append(
                f"✅ {units}세대로 최소 규모 충족. "
                f"소규모 맞춤 관리의 장점 강조 가능."
            )
        else:
            strategies.append(
                f"⚠️ {units}세대로 소규모 사업. "
                f"운영 효율성 확보 방안 필요."
            )
            weaknesses.append(f"소규모 사업 ({units}세대)")
        
        # 7. 체크리스트 통과율 분석
        if checklist_pass_rate >= 90:
            strategies.append(
                f"✅ LH 기준 체크리스트 {checklist_pass_rate:.0f}% 통과. "
                f"모든 법적 요건 충족으로 신속 승인 기대."
            )
            strengths.append(f"기준 충족률 우수 ({checklist_pass_rate:.0f}%)")
        elif checklist_pass_rate >= 75:
            strategies.append(
                f"✅ LH 기준 체크리스트 {checklist_pass_rate:.0f}% 통과. "
                f"일부 보완 후 승인 가능."
            )
        else:
            strategies.append(
                f"⚠️ LH 기준 체크리스트 {checklist_pass_rate:.0f}% 통과. "
                f"미달 항목 개선 필요."
            )
            weaknesses.append(f"기준 충족률 낮음 ({checklist_pass_rate:.0f}%)")
            priority_actions.append("📋 미달 항목 개선 계획 수립")
        
        # 8. 용도지역 활용
        if "주거" in zone_type:
            strategies.append(
                f"🏘️ {zone_type}으로 주거용도에 적합. "
                f"용도지역 특성을 활용한 인허가 전략 수립."
            )
        
        # 전략이 없는 경우 기본 메시지
        if not strategies:
            strategies.append("기본적인 LH 매입 기준을 충족하고 있습니다.")
        
        return NegotiationStrategy(
            strategies=strategies,
            strengths=strengths if strengths else ["종합적으로 양호한 사업 구조"],
            weaknesses=weaknesses if weaknesses else ["특이사항 없음"],
            priority_actions=priority_actions if priority_actions else ["현 계획대로 진행"]
        )
