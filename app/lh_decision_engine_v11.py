"""
ZeroSite v11.0 - LH Decision Engine
====================================
LH 점수/등급 기반 GO/NO-GO 의사결정 엔진

의사결정 기준:
1. GO (사업 추진 권장)
   - 총점 80점 이상 AND 등급 A/B
   - 치명적 리스크 없음
   - 재무 건전성 양호

2. REVIEW (조건부 추진 / 개선 후 재검토)
   - 총점 70-79점 AND 등급 C
   - 일부 리스크 존재하나 완화 가능
   - 재무 구조 개선 필요

3. NO-GO (사업 추진 불가 / 포기 권장)
   - 총점 70점 미만 AND 등급 D/F
   - 치명적 리스크 존재
   - 재무 구조 불건전
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

from app.lh_score_mapper_v11 import LHScoreBreakdown, LHGrade


class DecisionType(Enum):
    """의사결정 유형"""
    GO = "GO"  # 추진 권장
    REVIEW = "REVIEW"  # 조건부 추진
    NO_GO = "NO_GO"  # 추진 불가


class RiskLevel(Enum):
    """리스크 수준"""
    CRITICAL = "CRITICAL"  # 치명적
    HIGH = "HIGH"  # 높음
    MEDIUM = "MEDIUM"  # 보통
    LOW = "LOW"  # 낮음


@dataclass
class CriticalRisk:
    """치명적 리스크 항목"""
    category: str
    description: str
    impact: str
    mitigation: str


@dataclass
class DecisionResult:
    """의사결정 결과"""
    decision: DecisionType
    confidence: float  # 0-100%
    
    # 근거
    primary_reason: str
    supporting_reasons: List[str]
    
    # 리스크 분석
    critical_risks: List[CriticalRisk]
    risk_level: RiskLevel
    
    # 재무 분석
    financial_viability: str
    irr_assessment: str
    roi_assessment: str
    
    # 개선 전략
    improvement_strategies: List[str]
    priority_actions: List[str]
    
    # 최종 권고
    executive_summary: str
    next_steps: List[str]


class LHDecisionEngine:
    """LH 의사결정 엔진"""
    
    def __init__(self):
        self.decision_thresholds = {
            "go": 80,
            "review": 70,
            "no_go": 70
        }
    
    def make_decision(self,
                     lh_score: LHScoreBreakdown,
                     analysis_result: Dict[str, Any],
                     feasibility_result: Dict[str, Any]) -> DecisionResult:
        """
        종합 의사결정 수행
        
        Args:
            lh_score: LH 점수 분석 결과
            analysis_result: v9.1 분석 결과
            feasibility_result: 현실성 검증 결과
            
        Returns:
            DecisionResult: 의사결정 결과
        """
        
        total_score = lh_score.total_score
        grade = lh_score.grade
        
        # 1. 치명적 리스크 탐지
        critical_risks = self._detect_critical_risks(lh_score, analysis_result, feasibility_result)
        risk_level = self._assess_risk_level(critical_risks, lh_score)
        
        # 2. 재무 건전성 평가
        financial_viability = self._assess_financial_viability(lh_score, analysis_result)
        irr_assessment = self._assess_irr(analysis_result)
        roi_assessment = self._assess_roi(analysis_result)
        
        # 3. 의사결정 로직
        decision, confidence, primary_reason, supporting_reasons = self._decide(
            total_score, grade, critical_risks, financial_viability, lh_score
        )
        
        # 4. 개선 전략 생성
        improvement_strategies = self._generate_improvement_strategies(
            lh_score, critical_risks, decision
        )
        priority_actions = self._generate_priority_actions(
            lh_score, critical_risks, decision
        )
        
        # 5. 최종 권고 생성
        executive_summary = self._generate_executive_summary(
            decision, total_score, grade, critical_risks, financial_viability
        )
        next_steps = self._generate_next_steps(decision, improvement_strategies)
        
        return DecisionResult(
            decision=decision,
            confidence=confidence,
            primary_reason=primary_reason,
            supporting_reasons=supporting_reasons,
            critical_risks=critical_risks,
            risk_level=risk_level,
            financial_viability=financial_viability,
            irr_assessment=irr_assessment,
            roi_assessment=roi_assessment,
            improvement_strategies=improvement_strategies,
            priority_actions=priority_actions,
            executive_summary=executive_summary,
            next_steps=next_steps
        )
    
    # ============================================================
    # 리스크 탐지
    # ============================================================
    
    def _detect_critical_risks(self,
                               lh_score: LHScoreBreakdown,
                               analysis_result: Dict,
                               feasibility_result: Dict) -> List[CriticalRisk]:
        """치명적 리스크 탐지"""
        critical_risks = []
        
        # 1. 법규 리스크
        if lh_score.legal_risk < 2:
            critical_risks.append(CriticalRisk(
                category="법규 리스크",
                description="용도지역 또는 건축 규제상 제약 존재",
                impact="사업 진행 불가 또는 대폭 축소",
                mitigation="용도지역 변경 신청 또는 개발 계획 전면 수정"
            ))
        
        # 2. 현실성 검증 실패
        feasibility_status = feasibility_result.get("feasibility_status", "PASS")
        if feasibility_status == "FAIL":
            critical_risks.append(CriticalRisk(
                category="현실성 검증 실패",
                description="추천 세대유형이 부지 조건에 부적합",
                impact="계획된 세대유형 구현 불가",
                mitigation=f"대안 유형 검토: {', '.join([alt['type'] for alt in feasibility_result.get('alternative_types', [])])}"
            ))
        
        # 3. 토지 가격 역전
        land_info = analysis_result.get("land_info", {})
        financial = analysis_result.get("financial_result", {})
        
        land_price = land_info.get("land_appraisal_price", 0)
        total_investment = financial.get("total_investment", 0)
        
        if total_investment > 0 and land_price / total_investment > 0.6:
            critical_risks.append(CriticalRisk(
                category="토지비 과다",
                description=f"토지비가 총 투자액의 {land_price/total_investment*100:.1f}% (60% 초과)",
                impact="수익성 심각하게 저하, LH 매입가 역전 가능",
                mitigation="토지 매입가 재협상 또는 용적률 상향 검토"
            ))
        
        # 4. 재무 건전성 불량
        irr = financial.get("irr_10yr", 0)
        if irr < 2:
            critical_risks.append(CriticalRisk(
                category="낮은 수익성",
                description=f"10년 IRR {irr:.2f}% (2% 미만)",
                impact="투자 매력도 없음, 자금 조달 불가",
                mitigation="건축비 절감, 세대수 증가, 또는 대체 부지 검토"
            ))
        
        # 5. 세대수 부족
        dev_plan = analysis_result.get("development_plan", {})
        unit_count = dev_plan.get("unit_count", 0)
        
        if unit_count < 10:
            critical_risks.append(CriticalRisk(
                category="세대수 부족",
                description=f"계획 세대수 {unit_count}세대 (LH 최소 기준 미달)",
                impact="LH 매입 대상 부적격",
                mitigation="용적률 상향 또는 세대 면적 축소 검토"
            ))
        
        return critical_risks
    
    def _assess_risk_level(self, critical_risks: List[CriticalRisk], lh_score: LHScoreBreakdown) -> RiskLevel:
        """전체 리스크 수준 평가"""
        if len(critical_risks) >= 3:
            return RiskLevel.CRITICAL
        elif len(critical_risks) >= 2:
            return RiskLevel.HIGH
        elif len(critical_risks) >= 1:
            return RiskLevel.MEDIUM
        elif lh_score.risk_total < 7:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    # ============================================================
    # 재무 평가
    # ============================================================
    
    def _assess_financial_viability(self, lh_score: LHScoreBreakdown, analysis_result: Dict) -> str:
        """재무 건전성 종합 평가"""
        financial_score = lh_score.financial_total
        
        if financial_score >= 12:
            return "재무 구조 우수 - 안정적 수익 창출 가능"
        elif financial_score >= 10:
            return "재무 구조 양호 - 적정 수익 기대 가능"
        elif financial_score >= 8:
            return "재무 구조 보통 - 개선 여지 있음"
        else:
            return "재무 구조 취약 - 대폭 개선 필요"
    
    def _assess_irr(self, analysis_result: Dict) -> str:
        """IRR 평가"""
        financial = analysis_result.get("financial_result", {})
        irr = financial.get("irr_10yr", 0)
        
        if irr >= 5:
            return f"IRR {irr:.2f}% - 매우 우수 (5% 이상)"
        elif irr >= 4:
            return f"IRR {irr:.2f}% - 우수 (4% 이상)"
        elif irr >= 3:
            return f"IRR {irr:.2f}% - 양호 (3% 이상)"
        elif irr >= 2:
            return f"IRR {irr:.2f}% - 보통 (2% 이상)"
        else:
            return f"IRR {irr:.2f}% - 부족 (2% 미만, 개선 필요)"
    
    def _assess_roi(self, analysis_result: Dict) -> str:
        """ROI 평가"""
        financial = analysis_result.get("financial_result", {})
        roi = financial.get("roi", 0)
        
        if roi >= 40:
            return f"ROI {roi:.2f}% - 매우 우수 (40% 이상)"
        elif roi >= 30:
            return f"ROI {roi:.2f}% - 우수 (30% 이상)"
        elif roi >= 20:
            return f"ROI {roi:.2f}% - 양호 (20% 이상)"
        elif roi >= 10:
            return f"ROI {roi:.2f}% - 보통 (10% 이상)"
        else:
            return f"ROI {roi:.2f}% - 부족 (10% 미만, 개선 필요)"
    
    # ============================================================
    # 의사결정 로직
    # ============================================================
    
    def _decide(self,
                total_score: float,
                grade: LHGrade,
                critical_risks: List[CriticalRisk],
                financial_viability: str,
                lh_score: LHScoreBreakdown) -> Tuple[DecisionType, float, str, List[str]]:
        """의사결정 수행"""
        
        # 치명적 리스크가 3개 이상 → 무조건 NO-GO
        if len(critical_risks) >= 3:
            return (
                DecisionType.NO_GO,
                95.0,
                "치명적 리스크 3개 이상 존재",
                [
                    f"총 {len(critical_risks)}개의 치명적 리스크 탐지",
                    "사업 추진 시 실패 가능성 매우 높음",
                    "대체 부지 검토 권장"
                ]
            )
        
        # 등급 F → 무조건 NO-GO
        if grade == LHGrade.F:
            return (
                DecisionType.NO_GO,
                90.0,
                "LH 평가 등급 F (부적합)",
                [
                    f"총점 {total_score:.1f}점으로 최소 기준(60점) 미달",
                    "전면적인 계획 수정 또는 포기 필요",
                    lh_score.weaknesses[0] if lh_score.weaknesses else "전반적 개선 필요"
                ]
            )
        
        # 등급 A/B + 치명적 리스크 없음 → GO
        if grade in [LHGrade.A, LHGrade.B] and len(critical_risks) == 0:
            return (
                DecisionType.GO,
                90.0 if grade == LHGrade.A else 85.0,
                f"LH 평가 등급 {grade.value} (우수) + 치명적 리스크 없음",
                [
                    f"총점 {total_score:.1f}점으로 우수한 평가",
                    "재무 건전성 및 사업성 확인",
                    "사업 추진 적극 권장"
                ]
            )
        
        # 등급 B + 치명적 리스크 1개 → REVIEW
        if grade == LHGrade.B and len(critical_risks) == 1:
            return (
                DecisionType.REVIEW,
                75.0,
                "LH 평가 B등급이나 일부 리스크 존재",
                [
                    f"총점 {total_score:.1f}점으로 양호한 수준",
                    "1개 치명적 리스크 완화 시 추진 가능",
                    "개선 방안 수립 후 재검토 권장"
                ]
            )
        
        # 등급 C → REVIEW
        if grade == LHGrade.C:
            return (
                DecisionType.REVIEW,
                70.0,
                "LH 평가 C등급 (조건부 추진 가능)",
                [
                    f"총점 {total_score:.1f}점으로 보통 수준",
                    "일부 항목 개선 시 사업성 확보 가능",
                    "개선 계획 수립 후 재평가 필요"
                ]
            )
        
        # 등급 D 또는 치명적 리스크 2개 → NO-GO
        if grade == LHGrade.D or len(critical_risks) >= 2:
            return (
                DecisionType.NO_GO,
                85.0,
                "LH 평가 D등급 또는 다수 치명적 리스크",
                [
                    f"총점 {total_score:.1f}점으로 기준 미달",
                    f"{len(critical_risks)}개 치명적 리스크 존재",
                    "전면 재검토 또는 포기 권장"
                ]
            )
        
        # 기본값: REVIEW
        return (
            DecisionType.REVIEW,
            65.0,
            "종합적 검토 필요",
            [
                f"총점 {total_score:.1f}점, 등급 {grade.value}",
                "추가 분석 및 개선 방안 검토 필요",
                "조건부 추진 가능"
            ]
        )
    
    # ============================================================
    # 개선 전략
    # ============================================================
    
    def _generate_improvement_strategies(self,
                                        lh_score: LHScoreBreakdown,
                                        critical_risks: List[CriticalRisk],
                                        decision: DecisionType) -> List[str]:
        """개선 전략 생성"""
        strategies = []
        
        # 약점 기반 전략
        for weakness in lh_score.weaknesses:
            if "입지" in weakness:
                strategies.append("🎯 입지 개선: 교통 인프라 보강, 커뮤니티 시설 확충 계획 수립")
            elif "타당성" in weakness:
                strategies.append("🎯 사업성 개선: 용적률 최적화, 세대 구성 조정, 평면 효율화")
            elif "정책" in weakness:
                strategies.append("🎯 정책 부합: 청년/신혼/고령자 등 정책 우선 유형 전환 검토")
            elif "재무" in weakness:
                strategies.append("🎯 재무 개선: 건축비 절감, 수익성 제고 방안 마련")
            elif "리스크" in weakness:
                strategies.append("🎯 리스크 완화: 법규 정밀 검토, 리스크 관리 체계 구축")
        
        # 치명적 리스크 기반 전략
        for risk in critical_risks:
            strategies.append(f"🎯 {risk.category} 해결: {risk.mitigation}")
        
        # 점수대별 전략
        if lh_score.total_score < 70:
            strategies.append("🎯 전면 재설계: 컨셉부터 재검토, 대체 방안 수립")
        elif lh_score.total_score < 80:
            strategies.append("🎯 부분 개선: 취약 영역 집중 보완")
        
        return strategies[:5]  # 최대 5개
    
    def _generate_priority_actions(self,
                                  lh_score: LHScoreBreakdown,
                                  critical_risks: List[CriticalRisk],
                                  decision: DecisionType) -> List[str]:
        """우선 실행 과제 생성"""
        actions = []
        
        if decision == DecisionType.NO_GO:
            actions.append("1️⃣ 즉시: 사업 중단 및 대체 방안 검토")
            actions.append("2️⃣ 1주 내: 손실 최소화 방안 수립")
            actions.append("3️⃣ 2주 내: 대체 부지 탐색 시작")
        
        elif decision == DecisionType.REVIEW:
            actions.append("1️⃣ 즉시: 취약 항목 정밀 분석")
            actions.append("2️⃣ 1주 내: 개선 방안 구체화")
            actions.append("3️⃣ 2주 내: 개선 후 재평가 실시")
            actions.append("4️⃣ 1개월 내: GO/NO-GO 최종 결정")
        
        else:  # GO
            actions.append("1️⃣ 즉시: 사업 추진 착수")
            actions.append("2️⃣ 1주 내: 상세 실행 계획 수립")
            actions.append("3️⃣ 2주 내: LH 협의 시작")
            actions.append("4️⃣ 1개월 내: 인허가 절차 개시")
        
        # 치명적 리스크 대응
        for i, risk in enumerate(critical_risks[:3], 1):
            actions.insert(i, f"🔴 긴급: {risk.category} 해결 ({risk.mitigation})")
        
        return actions[:6]  # 최대 6개
    
    # ============================================================
    # 최종 요약
    # ============================================================
    
    def _generate_executive_summary(self,
                                    decision: DecisionType,
                                    total_score: float,
                                    grade: LHGrade,
                                    critical_risks: List[CriticalRisk],
                                    financial_viability: str) -> str:
        """경영진 요약 생성"""
        
        decision_text = {
            DecisionType.GO: "✅ 사업 추진 권장 (GO)",
            DecisionType.REVIEW: "⚠️ 조건부 추진 (REVIEW)",
            DecisionType.NO_GO: "🛑 사업 추진 불가 (NO-GO)"
        }
        
        summary = f"""
{decision_text[decision]}

【종합 평가】
• LH 평가 점수: {total_score:.1f}/100점 (등급 {grade.value})
• 재무 건전성: {financial_viability}
• 치명적 리스크: {len(critical_risks)}건 탐지

【핵심 판단 근거】
"""
        
        if decision == DecisionType.GO:
            summary += f"""
• 우수한 LH 평가 점수 ({total_score:.1f}점)
• 치명적 리스크 없음 또는 완화 가능
• 재무적으로 건전하고 수익성 확보
• 정책 방향과 부합

👉 사업 추진을 적극 권장하며, 조속한 LH 협의를 통해 사업을 개시하시기 바랍니다.
"""
        
        elif decision == DecisionType.REVIEW:
            summary += f"""
• LH 평가 점수 보통 수준 ({total_score:.1f}점)
• 일부 리스크 존재하나 완화 가능
• 재무 구조 개선 여지 있음
• 부분적 수정으로 사업성 확보 가능

👉 취약 항목을 집중 개선한 후 재평가를 실시하여 최종 GO/NO-GO를 결정하시기 바랍니다.
"""
        
        else:  # NO_GO
            summary += f"""
• LH 평가 점수 부족 ({total_score:.1f}점)
• 치명적 리스크 다수 존재 ({len(critical_risks)}건)
• 재무 구조 불건전 또는 수익성 미흡
• 사업 추진 시 실패 가능성 높음

👉 현 상태로는 사업 추진이 불가하며, 전면 재검토 또는 대체 방안을 모색하시기 바랍니다.
"""
        
        return summary.strip()
    
    def _generate_next_steps(self, decision: DecisionType, improvement_strategies: List[str]) -> List[str]:
        """다음 단계 생성"""
        
        if decision == DecisionType.GO:
            return [
                "✅ LH 공사 협의 일정 확정",
                "✅ 상세 설계 착수",
                "✅ 인허가 서류 준비",
                "✅ 자금 조달 계획 확정",
                "✅ 시공사 선정 절차 개시"
            ]
        
        elif decision == DecisionType.REVIEW:
            return [
                "⚠️ 취약 항목 개선 방안 수립 (1주)",
                "⚠️ 개선 방안 실행 (2주)",
                "⚠️ LH 점수 재평가 (3주)",
                "⚠️ 최종 GO/NO-GO 결정 (4주)",
                "⚠️ 결정에 따른 후속 조치"
            ]
        
        else:  # NO_GO
            return [
                "🛑 사업 중단 공식화",
                "🛑 손실 최소화 방안 실행",
                "🛑 대체 부지 탐색",
                "🛑 교훈 정리 및 문서화",
                "🛑 차기 프로젝트 준비"
            ]


# ============================================================
# 사용 예시
# ============================================================

if __name__ == "__main__":
    from app.lh_score_mapper_v11 import LHScoreMapper, LHScoreBreakdown, LHGrade
    
    # 테스트 데이터
    test_lh_score = LHScoreBreakdown(
        location_total=20.5,
        transportation_access=9.0,
        living_convenience=7.0,
        education_environment=4.5,
        
        feasibility_total=24.0,
        far_bcr_adequacy=8.0,
        unit_count_adequacy=6.0,
        land_price_adequacy=10.0,
        
        policy_total=16.0,
        zone_suitability=7.0,
        housing_policy_alignment=7.0,
        unit_type_suitability=2.0,
        
        financial_total=11.0,
        irr_roi_level=6.0,
        payback_period=3.0,
        financing_feasibility=2.0,
        
        risk_total=8.0,
        legal_risk=3.5,
        market_risk=2.5,
        construction_risk=2.0,
        
        total_score=79.5,
        grade=LHGrade.C,
        
        strengths=["✅ 우수한 입지 조건 (20.5/25점)"],
        weaknesses=["⚠️ 재무 구조 개선 필요 (11.0/15점)"],
        recommendations=["💡 재무 구조 개선 및 리스크 완화 전략 수립"]
    )
    
    test_analysis = {
        "land_info": {"land_area": 1000, "land_appraisal_price": 9000000000},
        "development_plan": {"unit_count": 42},
        "financial_result": {"irr_10yr": 3.6, "roi": 37.11, "total_investment": 16500000000}
    }
    
    test_feasibility = {
        "feasibility_status": "PASS",
        "alternative_types": []
    }
    
    engine = LHDecisionEngine()
    result = engine.make_decision(test_lh_score, test_analysis, test_feasibility)
    
    print("=" * 60)
    print("LH Decision Engine Test Result")
    print("=" * 60)
    print(f"의사결정: {result.decision.value}")
    print(f"신뢰도: {result.confidence:.1f}%")
    print(f"\n주요 근거: {result.primary_reason}")
    print(f"\n치명적 리스크: {len(result.critical_risks)}건")
    
    print(f"\n{result.executive_summary}")
    
    print(f"\n개선 전략:")
    for strategy in result.improvement_strategies[:3]:
        print(f"  {strategy}")
    
    print(f"\n우선 실행:")
    for action in result.priority_actions[:3]:
        print(f"  {action}")
