"""
LH Decision Engine Core Scorer
================================

Phase 3: LH Decision Engine - Core Scoring Logic
100점 만점 평가 + GO/REVIEW/NO-GO 결정

Author: ZeroSite Development Team
Date: 2025-12-06
"""

import time
from datetime import datetime
from typing import List, Tuple

from .output_schema import (
    LHDecisionInput,
    LHDecisionResult,
    LHScoreBreakdown,
    DecisionRationale,
    ImprovementProposal,
    DecisionType
)
from .config import (
    LH_SCORING_WEIGHTS,
    LH_DECISION_THRESHOLDS,
    get_region_from_address,
    get_lh_acquisition_price,
    validate_critical_blockers
)


class LHDecisionEngineCore:
    """
    LH Decision Engine 핵심 엔진
    
    역할:
    1. Phase 1 + Phase 2 JSON 입력
    2. 100점 만점 LH 평가
    3. GO/REVIEW/NO-GO 결정
    4. JSON 출력 (NO HTML/PDF)
    """
    
    def __init__(self):
        self.scoring_weights = LH_SCORING_WEIGHTS
        self.thresholds = LH_DECISION_THRESHOLDS
    
    def evaluate(self, input_data: LHDecisionInput) -> LHDecisionResult:
        """
        메인 평가 함수
        
        Args:
            input_data: Phase 1 + Phase 2 통합 데이터
        
        Returns:
            LHDecisionResult: 최종 평가 결과 (JSON)
        """
        start_time = time.time()
        
        # Step 1: Critical Blocker 검증
        is_blocked, blocker_reasons = self._check_critical_blockers(input_data)
        
        if is_blocked:
            return self._create_blocked_result(input_data, blocker_reasons, start_time)
        
        # Step 2: 100점 평가
        score_breakdown = self._calculate_score(input_data)
        
        # Step 3: 의사결정
        decision = self._determine_decision(score_breakdown.total_score)
        confidence = self._calculate_confidence(score_breakdown, input_data)
        
        # Step 4: SWOT 분석
        rationale = self._generate_rationale(input_data, score_breakdown)
        
        # Step 5: 개선 제안
        improvement_proposals = self._generate_improvement_proposals(
            input_data, score_breakdown, decision
        )
        
        # Step 6: 리스크 평가
        risk_level = self._assess_risk(score_breakdown, input_data)
        critical_risks = self._identify_critical_risks(input_data, score_breakdown)
        
        # Step 7: 종합 의견
        executive_summary = self._generate_executive_summary(
            decision, score_breakdown, input_data
        )
        
        # Step 8: 핵심 권장사항
        key_recommendations = self._generate_key_recommendations(
            decision, improvement_proposals
        )
        
        # Step 9: 다음 단계
        next_steps = self._generate_next_steps(decision, improvement_proposals)
        
        # Final Result
        result = LHDecisionResult(
            calculation_timestamp=datetime.now().isoformat(),
            input_data=input_data,
            score=score_breakdown,
            decision=decision,
            confidence=confidence,
            rationale=rationale,
            improvement_proposals=improvement_proposals,
            executive_summary=executive_summary,
            key_recommendations=key_recommendations,
            risk_level=risk_level,
            critical_risks=critical_risks,
            next_steps=next_steps
        )
        
        return result
    
    # ==================
    # Critical Blockers
    # ==================
    
    def _check_critical_blockers(
        self, input_data: LHDecisionInput
    ) -> Tuple[bool, List[str]]:
        """Critical Blocker 검증"""
        parking_ratio = 0.0
        if input_data.unit_count > 0:
            # 주차대수 계산 (단순 추정: GFA 기반)
            # 실제로는 Phase 1에서 전달받아야 함
            estimated_parking = input_data.gross_floor_area / 25  # 25㎡당 1대
            parking_ratio = estimated_parking / input_data.unit_count
        
        construction_cost_per_sqm = 0.0
        if input_data.gross_floor_area > 0:
            construction_cost_per_sqm = input_data.total_capex / input_data.gross_floor_area
        
        return validate_critical_blockers(
            financial_gap_ratio=input_data.lh_gap_ratio,
            parking_ratio=parking_ratio,
            construction_cost_per_sqm=construction_cost_per_sqm
        )
    
    def _create_blocked_result(
        self, 
        input_data: LHDecisionInput,
        blocker_reasons: List[str],
        start_time: float
    ) -> LHDecisionResult:
        """Critical Blocker 발생시 NO-GO 결과 생성"""
        
        # 0점 처리
        score_breakdown = LHScoreBreakdown(
            location_score=0.0,
            transportation_access=0.0,
            living_convenience=0.0,
            education_environment=0.0,
            feasibility_score=0.0,
            far_bcr_adequacy=0.0,
            unit_count_adequacy=0.0,
            land_price_adequacy=0.0,
            market_score=0.0,
            demand_potential=0.0,
            competition_level=0.0,
            price_competitiveness=0.0,
            financial_score=0.0,
            profitability=0.0,
            lh_purchase_gap=0.0,
            regulatory_score=0.0,
            legal_compliance=0.0,
            lh_policy_fit=0.0,
            total_score=0.0,
            grade="F"
        )
        
        rationale = DecisionRationale(
            strengths=[],
            weaknesses=blocker_reasons,
            opportunities=[],
            threats=["Critical Blocker 발생으로 사업 진행 불가"]
        )
        
        return LHDecisionResult(
            calculation_timestamp=datetime.now().isoformat(),
            input_data=input_data,
            score=score_breakdown,
            decision=DecisionType.NO_GO,
            confidence=1.0,
            rationale=rationale,
            improvement_proposals=[],
            executive_summary=f"사업 진행 불가 (Critical Blocker): {', '.join(blocker_reasons)}",
            key_recommendations=["사업 재검토 필요"],
            risk_level="CRITICAL",
            critical_risks=blocker_reasons,
            next_steps=["Critical Blocker 해소 방안 검토", "사업 구조 전면 재설계 필요"]
        )
    
    # ==================
    # Scoring System
    # ==================
    
    def _calculate_score(self, input_data: LHDecisionInput) -> LHScoreBreakdown:
        """100점 만점 평가 계산"""
        
        # 1. 입지 적합성 (25점)
        location_result = self._score_location(input_data)
        
        # 2. 사업 타당성 (30점)
        feasibility_result = self._score_feasibility(input_data)
        
        # 3. 시장 경쟁력 (25점)
        market_result = self._score_market(input_data)
        
        # 4. 재무 건전성 (10점)
        financial_result = self._score_financial(input_data)
        
        # 5. 법규 적합성 (10점)
        regulatory_result = self._score_regulatory(input_data)
        
        # 총점 계산
        total_score = (
            location_result["score"] +
            feasibility_result["score"] +
            market_result["score"] +
            financial_result["score"] +
            regulatory_result["score"]
        )
        
        # 등급 계산
        grade = self._calculate_grade(total_score)
        
        return LHScoreBreakdown(
            # Location (25점)
            location_score=location_result["score"],
            transportation_access=location_result["transportation_access"],
            living_convenience=location_result["living_convenience"],
            education_environment=location_result["education_environment"],
            
            # Feasibility (30점)
            feasibility_score=feasibility_result["score"],
            far_bcr_adequacy=feasibility_result["far_bcr_adequacy"],
            unit_count_adequacy=feasibility_result["unit_count_adequacy"],
            land_price_adequacy=feasibility_result["land_price_adequacy"],
            
            # Market (25점)
            market_score=market_result["score"],
            demand_potential=market_result["demand_potential"],
            competition_level=market_result["competition_level"],
            price_competitiveness=market_result["price_competitiveness"],
            
            # Financial (10점)
            financial_score=financial_result["score"],
            profitability=financial_result["profitability"],
            lh_purchase_gap=financial_result["lh_purchase_gap"],
            
            # Regulatory (10점)
            regulatory_score=regulatory_result["score"],
            legal_compliance=regulatory_result["legal_compliance"],
            lh_policy_fit=regulatory_result["lh_policy_fit"],
            
            # Total
            total_score=total_score,
            grade=grade
        )
    
    def _score_location(self, input_data: LHDecisionInput) -> dict:
        """입지 적합성 평가 (25점)"""
        # 현재는 단순 추정 (Phase 1에서 실제 데이터 받아야 함)
        # 서울/경기 우대
        region = get_region_from_address(input_data.address or "")
        
        if region in ["서울", "경기"]:
            base_score = 20.0
        elif region in ["인천", "부산", "대전"]:
            base_score = 16.0
        else:
            base_score = 12.0
        
        # 세부 점수
        transportation_access = base_score * 0.4  # 40%
        living_convenience = base_score * 0.35    # 35%
        education_environment = base_score * 0.25  # 25%
        
        return {
            "score": base_score,
            "transportation_access": transportation_access,
            "living_convenience": living_convenience,
            "education_environment": education_environment
        }
    
    def _score_feasibility(self, input_data: LHDecisionInput) -> dict:
        """사업 타당성 평가 (30점)"""
        score = 0.0
        
        # 1. FAR/BCR 적정성 (12점)
        far_bcr_score = 0.0
        if "일반주거" in input_data.zone_type:
            # 제2종일반주거: 용적률 150~250% 적정
            if 150 <= input_data.floor_area_ratio <= 250:
                far_bcr_score = 12.0
            elif 100 <= input_data.floor_area_ratio < 150:
                far_bcr_score = 8.0
            else:
                far_bcr_score = 5.0
        else:
            far_bcr_score = 10.0  # 기타 용도지역
        
        # 2. 세대수 적정성 (10점)
        unit_count_score = 0.0
        if 20 <= input_data.unit_count <= 50:
            unit_count_score = 10.0  # 최적 규모
        elif 15 <= input_data.unit_count < 20 or 50 < input_data.unit_count <= 70:
            unit_count_score = 7.0
        else:
            unit_count_score = 4.0
        
        # 3. 토지가 적정성 (8점)
        # LH Gap이 양수면 토지가가 적정함
        land_price_score = 0.0
        if input_data.lh_gap_ratio > 0:
            land_price_score = 8.0
        elif input_data.lh_gap_ratio > -10:
            land_price_score = 6.0
        elif input_data.lh_gap_ratio > -20:
            land_price_score = 4.0
        else:
            land_price_score = 2.0
        
        score = far_bcr_score + unit_count_score + land_price_score
        
        return {
            "score": score,
            "far_bcr_adequacy": far_bcr_score,
            "unit_count_adequacy": unit_count_score,
            "land_price_adequacy": land_price_score
        }
    
    def _score_market(self, input_data: LHDecisionInput) -> dict:
        """시장 경쟁력 평가 (25점)"""
        region = get_region_from_address(input_data.address or "")
        
        # 수요 잠재력 (12점)
        if region in ["서울", "경기"]:
            demand_score = 10.0
        elif region in ["인천", "부산", "대전"]:
            demand_score = 7.0
        else:
            demand_score = 5.0
        
        # 경쟁 수준 (7점) - 중소형 평수 우대
        if input_data.unit_count <= 50:
            competition_score = 6.0
        else:
            competition_score = 4.0
        
        # 가격 경쟁력 (6점) - ROI 기반
        if input_data.roi > 3.0:
            price_score = 6.0
        elif input_data.roi > 1.5:
            price_score = 4.0
        else:
            price_score = 2.0
        
        score = demand_score + competition_score + price_score
        
        return {
            "score": score,
            "demand_potential": demand_score,
            "competition_level": competition_score,
            "price_competitiveness": price_score
        }
    
    def _score_financial(self, input_data: LHDecisionInput) -> dict:
        """재무 건전성 평가 (10점)"""
        
        # 수익성 (6점) - ROI + IRR
        profitability_score = 0.0
        if input_data.roi > 3.0 and input_data.irr > 5.0:
            profitability_score = 6.0
        elif input_data.roi > 2.0 and input_data.irr > 3.0:
            profitability_score = 4.5
        elif input_data.roi > 1.0 and input_data.irr > 0:
            profitability_score = 3.0
        else:
            profitability_score = 1.0
        
        # LH 매입가 갭 (4점)
        gap_score = 0.0
        if input_data.lh_gap_ratio > 10:
            gap_score = 4.0  # 갭이 크면 좋음
        elif input_data.lh_gap_ratio > 0:
            gap_score = 3.0
        elif input_data.lh_gap_ratio > -10:
            gap_score = 2.0
        elif input_data.lh_gap_ratio > -20:
            gap_score = 1.0
        else:
            gap_score = 0.0
        
        score = profitability_score + gap_score
        
        return {
            "score": score,
            "profitability": profitability_score,
            "lh_purchase_gap": gap_score
        }
    
    def _score_regulatory(self, input_data: LHDecisionInput) -> dict:
        """법규 적합성 평가 (10점)"""
        
        # 법규 준수 (6점)
        legal_score = 6.0  # 기본적으로 법규 준수 가정
        
        # LH 정책 부합도 (4점)
        policy_score = 0.0
        if "일반주거" in input_data.zone_type or "준주거" in input_data.zone_type:
            policy_score = 4.0
        else:
            policy_score = 2.0
        
        score = legal_score + policy_score
        
        return {
            "score": score,
            "legal_compliance": legal_score,
            "lh_policy_fit": policy_score
        }
    
    def _calculate_grade(self, total_score: float) -> str:
        """등급 계산"""
        if total_score >= 90:
            return "A"
        elif total_score >= 80:
            return "B"
        elif total_score >= 70:
            return "C"
        elif total_score >= 60:
            return "D"
        else:
            return "F"
    
    # ==================
    # Decision Logic
    # ==================
    
    def _determine_decision(self, total_score: float) -> DecisionType:
        """의사결정"""
        if total_score >= self.thresholds.go_threshold:
            return DecisionType.GO
        elif total_score >= self.thresholds.review_threshold:
            return DecisionType.REVIEW
        else:
            return DecisionType.NO_GO
    
    def _calculate_confidence(
        self, score: LHScoreBreakdown, input_data: LHDecisionInput
    ) -> float:
        """신뢰도 계산"""
        # 극단값이면 신뢰도 높음
        if score.total_score >= 85 or score.total_score <= 40:
            return 0.95
        elif score.total_score >= 75 or score.total_score <= 50:
            return 0.85
        else:
            return 0.70
    
    # ==================
    # Analysis Modules
    # ==================
    
    def _generate_rationale(
        self, input_data: LHDecisionInput, score: LHScoreBreakdown
    ) -> DecisionRationale:
        """SWOT 분석"""
        strengths = []
        weaknesses = []
        opportunities = []
        threats = []
        
        # Strengths
        if score.location_score >= 18:
            strengths.append("우수한 입지 조건 (교통/생활 편의성)")
        if input_data.lh_gap_ratio > 0:
            strengths.append("LH 매입가 대비 경쟁력 확보")
        if input_data.roi > 3.0:
            strengths.append("높은 투자수익률 (ROI > 3%)")
        
        # Weaknesses
        if score.location_score < 15:
            weaknesses.append("입지 조건 미흡")
        if input_data.lh_gap_ratio < -20:
            weaknesses.append("LH 매입가 대비 경제성 부족")
        if input_data.roi < 2.0:
            weaknesses.append("낮은 투자수익률")
        
        # Opportunities
        region = get_region_from_address(input_data.address or "")
        if region in ["서울", "경기"]:
            opportunities.append("수도권 지역 수요 안정적")
        if input_data.unit_count <= 50:
            opportunities.append("중소형 개발로 리스크 관리 용이")
        
        # Threats
        if input_data.total_capex > 15000000000:  # 150억 초과
            threats.append("대규모 자본 투입으로 재무 리스크 높음")
        if input_data.lh_gap_ratio < -10:
            threats.append("LH 매입가 갭으로 인한 사업성 리스크")
        
        return DecisionRationale(
            strengths=strengths if strengths else ["해당 없음"],
            weaknesses=weaknesses if weaknesses else ["해당 없음"],
            opportunities=opportunities if opportunities else ["해당 없음"],
            threats=threats if threats else ["해당 없음"]
        )
    
    def _generate_improvement_proposals(
        self,
        input_data: LHDecisionInput,
        score: LHScoreBreakdown,
        decision: DecisionType
    ) -> List[ImprovementProposal]:
        """개선 제안"""
        proposals = []
        
        # 재무 건전성 개선
        if score.financial_score < 7:
            proposals.append(ImprovementProposal(
                category="재무 건전성",
                current_issue=f"ROI {input_data.roi:.2f}%, IRR {input_data.irr:.2f}%로 수익성 낮음",
                proposal="공사비 절감 방안 검토 (설계 최적화, VE 적용)",
                expected_impact="ROI 1~2% 개선 예상",
                priority="HIGH"
            ))
        
        # 사업 타당성 개선
        if score.feasibility_score < 20:
            proposals.append(ImprovementProposal(
                category="사업 타당성",
                current_issue="용적률/세대수 최적화 부족",
                proposal="설계 변경을 통한 세대수 증가 검토",
                expected_impact="사업성 5~10점 개선",
                priority="HIGH"
            ))
        
        # LH 갭 개선
        if input_data.lh_gap_ratio < -10:
            proposals.append(ImprovementProposal(
                category="LH 매입가 갭",
                current_issue=f"LH 갭 {input_data.lh_gap_ratio:.1f}%로 수익성 부족",
                proposal="토지 매입가 재협상 또는 사업 구조 변경",
                expected_impact="갭 10~20% 개선 가능",
                priority="CRITICAL" if input_data.lh_gap_ratio < -20 else "HIGH"
            ))
        
        return proposals
    
    def _assess_risk(
        self, score: LHScoreBreakdown, input_data: LHDecisionInput
    ) -> str:
        """리스크 수준 평가"""
        if score.total_score >= 80:
            return "LOW"
        elif score.total_score >= 70:
            return "MEDIUM"
        elif score.total_score >= 55:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _identify_critical_risks(
        self, input_data: LHDecisionInput, score: LHScoreBreakdown
    ) -> List[str]:
        """주요 리스크 식별"""
        risks = []
        
        if input_data.lh_gap_ratio < -20:
            risks.append("LH 매입가 대비 사업비 초과 (갭 -20% 이상)")
        
        if input_data.roi < 2.0:
            risks.append("낮은 투자수익률 (ROI < 2%)")
        
        if input_data.irr < 0:
            risks.append("마이너스 내부수익률 (IRR < 0%)")
        
        if score.location_score < 15:
            risks.append("입지 조건 미흡으로 분양/임대 리스크")
        
        return risks if risks else ["주요 리스크 없음"]
    
    def _generate_executive_summary(
        self, decision: DecisionType, score: LHScoreBreakdown, input_data: LHDecisionInput
    ) -> str:
        """종합 의견"""
        if decision == DecisionType.GO:
            return f"""
본 사업은 총 {score.total_score:.1f}점으로 '{score.grade}' 등급을 획득하여 **사업 추진 가능** 판정입니다.
입지({score.location_score:.1f}점), 사업성({score.feasibility_score:.1f}점), 
시장경쟁력({score.market_score:.1f}점) 모두 양호하며, LH 정책에 부합합니다.
{input_data.unit_count}세대 규모의 안정적 사업 추진이 예상됩니다.
            """.strip()
        
        elif decision == DecisionType.REVIEW:
            return f"""
본 사업은 총 {score.total_score:.1f}점으로 '{score.grade}' 등급을 획득하여 **조건부 사업 추진** 판정입니다.
재무건전성({score.financial_score:.1f}점/10점) 및 사업성({score.feasibility_score:.1f}점/30점) 
개선이 필요하며, LH 갭 {input_data.lh_gap_ratio:.1f}% 해소 방안 검토가 필수입니다.
개선 후 재평가를 권장합니다.
            """.strip()
        
        else:  # NO-GO
            return f"""
본 사업은 총 {score.total_score:.1f}점으로 '{score.grade}' 등급을 획득하여 **사업 보류** 판정입니다.
LH 갭 {input_data.lh_gap_ratio:.1f}%, ROI {input_data.roi:.2f}%로 경제성이 부족하며,
현재 조건으로는 사업 추진이 어렵습니다. 전면 재검토가 필요합니다.
            """.strip()
    
    def _generate_key_recommendations(
        self, decision: DecisionType, proposals: List[ImprovementProposal]
    ) -> List[str]:
        """핵심 권장사항"""
        recommendations = []
        
        if decision == DecisionType.GO:
            recommendations.append("사업 추진 승인 권장")
            recommendations.append("상세 설계 및 인허가 절차 진행")
            recommendations.append("LH 매입 협의 개시")
        
        elif decision == DecisionType.REVIEW:
            recommendations.append("개선 방안 이행 후 재평가 필요")
            for proposal in proposals:
                if proposal.priority in ["CRITICAL", "HIGH"]:
                    recommendations.append(f"{proposal.category}: {proposal.proposal}")
        
        else:  # NO-GO
            recommendations.append("현 시점 사업 추진 보류")
            recommendations.append("사업 구조 전면 재검토 필요")
            recommendations.append("대안 부지 검토 권장")
        
        return recommendations
    
    def _generate_next_steps(
        self, decision: DecisionType, proposals: List[ImprovementProposal]
    ) -> List[str]:
        """다음 단계"""
        steps = []
        
        if decision == DecisionType.GO:
            steps.append("1. LH 매입 가격 공식 협의")
            steps.append("2. 건축 설계 및 인허가 준비")
            steps.append("3. 시공사 선정 및 공사 계약")
            steps.append("4. 금융 조달 계획 수립")
        
        elif decision == DecisionType.REVIEW:
            steps.append("1. 개선 제안사항 이행 계획 수립")
            for i, proposal in enumerate(proposals[:3], start=2):
                if proposal.priority in ["CRITICAL", "HIGH"]:
                    steps.append(f"{i}. {proposal.proposal}")
            steps.append(f"{len(proposals) + 2}. 개선 후 재평가 수행")
        
        else:  # NO-GO
            steps.append("1. 사업 중단 결정 승인")
            steps.append("2. 대안 부지 탐색")
            steps.append("3. 사업 구조 재설계 검토")
        
        return steps


# ======================
# Convenience Function
# ======================

def run_lh_decision_engine(input_data: LHDecisionInput) -> LHDecisionResult:
    """
    LH Decision Engine 실행 (편의 함수)
    
    Usage:
        from app.services_v9.lh_decision_engine import run_lh_decision_engine, LHDecisionInput
        
        input_data = LHDecisionInput(
            land_area=850,
            gross_floor_area=2125,
            unit_count=30,
            zone_type="제2종일반주거지역",
            ...
        )
        
        result = run_lh_decision_engine(input_data)
        print(result.decision)  # GO / REVIEW / NO-GO
        print(result.score.total_score)  # 72.5
    """
    engine = LHDecisionEngineCore()
    return engine.evaluate(input_data)


__all__ = ['LHDecisionEngineCore', 'run_lh_decision_engine']
