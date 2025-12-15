"""
ZeroSite v40.2 - LH 심사예측 Engine
LH 공공주택 사전심사 AI 예측 엔진 (Rule-Based v1.0)

Features:
- Context-Based Read-Only Data 사용
- Rule-Based Pre-check Filter (하드 조건)
- Weighted Score Calculation (6개 factor)
- Explainable AI (각 factor별 근거 제공)
- 시나리오 A/B/C 비교 예측

Author: ZeroSite AI Development Team
Date: 2025-12-14
Version: 1.0.0 (Rule-Based Baseline)
"""

from typing import Dict, Any, List, Optional
from decimal import Decimal
import logging

from app.schemas_lh import (
    LHReviewRequest,
    LHReviewResponse,
    FactorAnalysis,
    ScenarioPrediction,
    RiskLevel
)

logger = logging.getLogger(__name__)


class LHReviewEngine:
    """
    LH 심사예측 엔진
    
    핵심 원칙:
    1. 기존 Context 데이터 READ-ONLY 사용 (appraisal, zoning, capacity, scenario, risk)
    2. Non-Breaking: 기존 모듈 수정 없음
    3. Explainability: 모든 판단 근거 명시
    """
    
    # 가중치 설정 (총합 = 100%)
    WEIGHTS = {
        "location_score": 0.25,      # 25% - 입지 점수
        "zoning_compatibility": 0.20, # 20% - 용도지역 적합성
        "land_price_fairness": 0.15,  # 15% - 토지가격 합리성
        "capacity_feasibility": 0.20, # 20% - 용적률/건폐율 실현가능성
        "risk_level": 0.10,           # 10% - 리스크 수준
        "scenario_stability": 0.10    # 10% - 시나리오 안정성
    }
    
    # LH 선호 용도지역 (점수화)
    PREFERRED_ZONES = {
        "제1종일반주거지역": 90,
        "제2종일반주거지역": 95,
        "제3종일반주거지역": 85,
        "준주거지역": 80,
        "제1종전용주거지역": 70,
        "제2종전용주거지역": 75,
        "상업지역": 60,
        "준공업지역": 50
    }
    
    # 규제 지역 리스크 (감점)
    REGULATION_RISK = {
        "투기과열지구": -20,
        "조정대상지역": -15,
        "투기지역": -25,
        "없음": 0
    }
    
    def __init__(self):
        """엔진 초기화"""
        logger.info("LH Review Engine v1.0 initialized (Rule-Based)")
    
    def predict(
        self,
        context_data: Dict[str, Any],
        housing_type: str,
        target_units: int
    ) -> LHReviewResponse:
        """
        LH 심사 예측 실행
        
        Args:
            context_data: 기존 분석 Context (appraisal, zoning, capacity, scenario, risk)
            housing_type: LH 주택 유형 (청년, 신혼·신생아 I, 다자녀 등)
            target_units: 목표 세대수
            
        Returns:
            LHReviewResponse: 예측 결과
        """
        logger.info(f"🔍 LH 심사예측 시작 - {housing_type} / {target_units}세대")
        
        # Step 1: Rule-Based Pre-check (하드 조건 검증)
        pre_check_result = self._rule_based_precheck(context_data, housing_type, target_units)
        if not pre_check_result["pass"]:
            return self._create_rejection_response(pre_check_result["reason"])
        
        # Step 2: Factor 별 점수 계산
        factors = self._calculate_factors(context_data, housing_type, target_units)
        
        # Step 3: 종합 점수 계산
        total_score = self._calculate_total_score(factors)
        
        # Step 4: 합격 확률 계산
        pass_probability = self._calculate_pass_probability(total_score, factors)
        
        # Step 5: 리스크 레벨 판정
        risk_level = self._determine_risk_level(total_score, factors)
        
        # Step 6: 개선 제안
        suggestions = self._generate_suggestions(factors, context_data)
        
        # Step 7: 시나리오 A/B/C 비교 예측
        scenario_predictions = self._predict_scenarios(context_data, factors)
        
        logger.info(f"✅ 예측 완료 - 점수: {total_score}/100, 확률: {pass_probability}%")
        
        return LHReviewResponse(
            context_id=context_data.get("context_id", "unknown"),
            housing_type=housing_type,
            target_units=target_units,
            predicted_score=round(total_score, 1),
            pass_probability=round(pass_probability, 1),
            risk_level=risk_level,
            factors=factors,
            suggestions=suggestions,
            scenario_comparison=scenario_predictions
        )
    
    def _rule_based_precheck(
        self,
        context_data: Dict[str, Any],
        housing_type: str,
        target_units: int
    ) -> Dict[str, Any]:
        """
        Rule-Based 사전 조건 검증
        
        하드 조건:
        1. 용도지역: 주거지역 또는 상업지역 필수
        2. 토지면적: 최소 500㎡ 이상
        3. FAR: 200% 이상
        4. 시나리오 존재 여부
        """
        # 용도지역 검증
        zoning = context_data.get("zoning", {})
        zone_type = zoning.get("zone_type", "")
        if "주거지역" not in zone_type and "상업지역" not in zone_type:
            return {"pass": False, "reason": f"용도지역 부적합: {zone_type} (주거/상업지역 필수)"}
        
        # 토지면적 검증 (v40.2 구조: capacity.land_area 또는 input.land_area_sqm)
        capacity = context_data.get("capacity", {})
        input_data = context_data.get("input", {})
        land_area = capacity.get("land_area", input_data.get("land_area_sqm", 0))
        if land_area < 300:  # 최소 300㎡로 완화 (청년 주택 고려)
            return {"pass": False, "reason": f"토지면적 부족: {land_area}㎡ (최소 300㎡ 필요)"}
        
        # FAR 검증 (v40.2 구조: capacity.far)
        capacity = context_data.get("capacity", {})
        legal_far = capacity.get("far", 0)
        if legal_far < 200:
            return {"pass": False, "reason": f"용적률 부족: {legal_far}% (최소 200% 필요)"}
        
        # 시나리오 존재 검증 (v40.2 구조: scenario.scenarios 배열)
        scenario = context_data.get("scenario", {})
        scenarios = scenario.get("scenarios", [])
        if not scenarios or len(scenarios) == 0:
            return {"pass": False, "reason": "시나리오 분석 결과 없음"}
        
        return {"pass": True, "reason": "사전 조건 모두 충족"}
    
    def _calculate_factors(
        self,
        context_data: Dict[str, Any],
        housing_type: str,
        target_units: int
    ) -> List[FactorAnalysis]:
        """Factor별 점수 계산"""
        factors = []
        
        # Factor 1: 입지 점수 (Location)
        location_factor = self._analyze_location(context_data)
        factors.append(location_factor)
        
        # Factor 2: 용도지역 적합성
        zoning_factor = self._analyze_zoning(context_data)
        factors.append(zoning_factor)
        
        # Factor 3: 토지가격 합리성
        price_factor = self._analyze_land_price(context_data)
        factors.append(price_factor)
        
        # Factor 4: 용적률/건폐율 실현가능성
        capacity_factor = self._analyze_capacity(context_data)
        factors.append(capacity_factor)
        
        # Factor 5: 리스크 수준
        risk_factor = self._analyze_risk(context_data)
        factors.append(risk_factor)
        
        # Factor 6: 시나리오 안정성
        scenario_factor = self._analyze_scenario_stability(context_data, target_units)
        factors.append(scenario_factor)
        
        return factors
    
    def _analyze_location(self, context_data: Dict[str, Any]) -> FactorAnalysis:
        """입지 분석 (교통, 도심접근성 기반)"""
        appraisal = context_data.get("appraisal", {})
        
        # v40.2 구조: premium.percentage 사용 (0-100 범위로 정규화)
        premium = appraisal.get("premium", {})
        premium_pct = premium.get("percentage", 0)
        
        # Premium이 ±20% 범위라고 가정, 이를 0-100 점수로 변환
        # -20% → 30점, 0% → 65점, +20% → 100점
        location_score = 65 + (premium_pct * 1.75)  # 20% → +35점, -20% → -35점
        location_score = max(0, min(100, location_score))  # 0-100 범위로 제한
        
        # 판정
        if location_score >= 80:
            impact = "매우 긍정적"
            reason = "교통 및 도심 접근성 우수"
        elif location_score >= 60:
            impact = "긍정적"
            reason = "평균 이상 입지 조건"
        elif location_score >= 40:
            impact = "보통"
            reason = "입지 조건 보통 수준"
        else:
            impact = "부정적"
            reason = "입지 조건 개선 필요"
        
        return FactorAnalysis(
            factor_name="입지 점수",
            score=round(location_score, 1),
            impact=impact,
            reason=reason,
            weight=self.WEIGHTS["location_score"]
        )
    
    def _analyze_zoning(self, context_data: Dict[str, Any]) -> FactorAnalysis:
        """용도지역 적합성 분석"""
        zoning = context_data.get("zoning", {})
        zone_type = zoning.get("zone_type", "")
        regulations = zoning.get("regulations", [])
        
        # LH 선호 용도지역 점수
        base_score = self.PREFERRED_ZONES.get(zone_type, 50)
        
        # 규제지역 감점
        regulation_penalty = 0
        for reg in regulations:
            regulation_penalty += self.REGULATION_RISK.get(reg, 0)
        
        final_score = max(0, min(100, base_score + regulation_penalty))
        
        # 판정
        if final_score >= 80:
            impact = "매우 긍정적"
            reason = f"{zone_type}, 규제 최소"
        elif final_score >= 60:
            impact = "긍정적"
            reason = f"{zone_type}, 일부 규제 존재"
        else:
            impact = "부정적"
            reason = f"{zone_type}, 규제 다수 또는 부적합"
        
        return FactorAnalysis(
            factor_name="용도지역 적합성",
            score=round(final_score, 1),
            impact=impact,
            reason=reason,
            weight=self.WEIGHTS["zoning_compatibility"]
        )
    
    def _analyze_land_price(self, context_data: Dict[str, Any]) -> FactorAnalysis:
        """토지가격 합리성 분석"""
        appraisal = context_data.get("appraisal", {})
        
        # v40.2 구조: official_price와 value_per_sqm은 직접 숫자값
        official_price = appraisal.get("official_price", 0)
        appraised_value = appraisal.get("value_per_sqm", 0)
        
        if official_price == 0:
            return FactorAnalysis(
                factor_name="토지가격 합리성",
                score=50.0,
                impact="보통",
                reason="가격 정보 부족",
                weight=self.WEIGHTS["land_price_fairness"]
            )
        
        # 공시지가 대비 감정가 비율
        price_ratio = (appraised_value / official_price) * 100
        
        # 점수화: 100-120% 구간이 최적 (공정 가격)
        if 100 <= price_ratio <= 120:
            score = 100
            impact = "매우 긍정적"
            reason = f"공시지가 대비 {price_ratio:.1f}% (적정 범위)"
        elif 90 <= price_ratio < 100:
            score = 85
            impact = "긍정적"
            reason = f"공시지가 대비 {price_ratio:.1f}% (저평가)"
        elif 120 < price_ratio <= 150:
            score = 70
            impact = "보통"
            reason = f"공시지가 대비 {price_ratio:.1f}% (약간 고평가)"
        else:
            score = 40
            impact = "부정적"
            reason = f"공시지가 대비 {price_ratio:.1f}% (과도한 가격)"
        
        return FactorAnalysis(
            factor_name="토지가격 합리성",
            score=round(score, 1),
            impact=impact,
            reason=reason,
            weight=self.WEIGHTS["land_price_fairness"]
        )
    
    def _analyze_capacity(self, context_data: Dict[str, Any]) -> FactorAnalysis:
        """용적률/건폐율 실현가능성 분석"""
        capacity = context_data.get("capacity", {})
        
        # v40.2 구조: far/bcr (not legal_far_pct/legal_bcr_pct)
        legal_far = capacity.get("far", 0)
        legal_bcr = capacity.get("bcr", 0)
        
        # FAR 적합성 (200-300%가 LH에게 최적)
        if 200 <= legal_far <= 300:
            far_score = 100
            far_reason = f"용적률 {legal_far}% (최적 범위)"
        elif 150 <= legal_far < 200:
            far_score = 75
            far_reason = f"용적률 {legal_far}% (다소 낮음)"
        elif 300 < legal_far <= 400:
            far_score = 85
            far_reason = f"용적률 {legal_far}% (높음, 사업성 우수)"
        else:
            far_score = 50
            far_reason = f"용적률 {legal_far}% (부적합)"
        
        # BCR 적합성 (40-60%가 적정)
        if 40 <= legal_bcr <= 60:
            bcr_score = 100
        elif 30 <= legal_bcr < 40 or 60 < legal_bcr <= 70:
            bcr_score = 80
        else:
            bcr_score = 60
        
        # 종합 점수
        final_score = (far_score * 0.7) + (bcr_score * 0.3)
        
        if final_score >= 85:
            impact = "매우 긍정적"
        elif final_score >= 70:
            impact = "긍정적"
        elif final_score >= 50:
            impact = "보통"
        else:
            impact = "부정적"
        
        return FactorAnalysis(
            factor_name="용적률/건폐율 실현가능성",
            score=round(final_score, 1),
            impact=impact,
            reason=far_reason,
            weight=self.WEIGHTS["capacity_feasibility"]
        )
    
    def _analyze_risk(self, context_data: Dict[str, Any]) -> FactorAnalysis:
        """리스크 수준 분석"""
        risk = context_data.get("risk", {})
        
        # 리스크 레벨 (HIGH/MEDIUM/LOW)
        risk_level = risk.get("overall_risk_level", "MEDIUM")
        risk_count = len(risk.get("risk_factors", []))
        
        # 점수화 (리스크가 낮을수록 높은 점수)
        if risk_level == "LOW" and risk_count <= 2:
            score = 95
            impact = "매우 긍정적"
            reason = "리스크 최소 (LOW)"
        elif risk_level == "LOW" or (risk_level == "MEDIUM" and risk_count <= 3):
            score = 80
            impact = "긍정적"
            reason = "리스크 낮음 (관리 가능)"
        elif risk_level == "MEDIUM":
            score = 60
            impact = "보통"
            reason = f"중간 리스크 ({risk_count}개 요인)"
        else:
            score = 30
            impact = "부정적"
            reason = f"높은 리스크 ({risk_count}개 요인)"
        
        return FactorAnalysis(
            factor_name="리스크 수준",
            score=round(score, 1),
            impact=impact,
            reason=reason,
            weight=self.WEIGHTS["risk_level"]
        )
    
    def _analyze_scenario_stability(
        self,
        context_data: Dict[str, Any],
        target_units: int
    ) -> FactorAnalysis:
        """시나리오 안정성 분석"""
        scenario = context_data.get("scenario", {})
        scenarios = scenario.get("scenarios", [])
        
        if not scenarios or len(scenarios) == 0:
            return FactorAnalysis(
                factor_name="시나리오 안정성",
                score=50.0,
                impact="보통",
                reason="시나리오 데이터 부족",
                weight=self.WEIGHTS["scenario_stability"]
            )
        
        # v40.2 구조: 첫 번째 시나리오 사용
        scenario_a = scenarios[0]
        
        # 세대수 적합성
        units_a = scenario_a.get("unit_count", 0)
        if units_a == 0:
            return FactorAnalysis(
                factor_name="시나리오 안정성",
                score=50.0,
                impact="보통",
                reason="시나리오 데이터 부족",
                weight=self.WEIGHTS["scenario_stability"]
            )
        
        # 목표 대비 달성률
        achievement_rate = (units_a / target_units) * 100
        
        # 사업성 지표 (v40.2: irr, npv 사용, roi 없음)
        irr = scenario_a.get("irr", 0)
        roi = irr  # IRR을 ROI 대용으로 사용
        
        # 점수 계산
        if achievement_rate >= 90 and roi >= 8 and irr >= 10:
            score = 95
            impact = "매우 긍정적"
            reason = f"목표 달성 {achievement_rate:.0f}%, 사업성 우수 (ROI {roi:.1f}%)"
        elif achievement_rate >= 80 and roi >= 6:
            score = 80
            impact = "긍정적"
            reason = f"목표 달성 {achievement_rate:.0f}%, 사업성 양호"
        elif achievement_rate >= 70:
            score = 65
            impact = "보통"
            reason = f"목표 달성 {achievement_rate:.0f}%, 사업성 보통"
        else:
            score = 40
            impact = "부정적"
            reason = f"목표 달성 {achievement_rate:.0f}%, 사업성 부족"
        
        return FactorAnalysis(
            factor_name="시나리오 안정성",
            score=round(score, 1),
            impact=impact,
            reason=reason,
            weight=self.WEIGHTS["scenario_stability"]
        )
    
    def _calculate_total_score(self, factors: List[FactorAnalysis]) -> float:
        """가중 평균 점수 계산"""
        total_score = 0.0
        for factor in factors:
            total_score += factor.score * factor.weight
        return total_score
    
    def _calculate_pass_probability(
        self,
        total_score: float,
        factors: List[FactorAnalysis]
    ) -> float:
        """합격 확률 계산 (0-100%)"""
        # Base probability from score
        if total_score >= 85:
            base_prob = 90 + (total_score - 85)  # 90-100%
        elif total_score >= 70:
            base_prob = 70 + (total_score - 70)  # 70-90%
        elif total_score >= 50:
            base_prob = 40 + (total_score - 50) * 1.5  # 40-70%
        else:
            base_prob = total_score * 0.8  # 0-40%
        
        # 리스크 factor 추가 조정
        risk_factor = next((f for f in factors if f.factor_name == "리스크 수준"), None)
        if risk_factor and risk_factor.impact == "부정적":
            base_prob *= 0.9  # 10% 감소
        
        return min(100, max(0, base_prob))
    
    def _determine_risk_level(
        self,
        total_score: float,
        factors: List[FactorAnalysis]
    ) -> RiskLevel:
        """전체 리스크 레벨 판정"""
        # 부정적 factor 개수
        negative_count = sum(1 for f in factors if f.impact == "부정적")
        
        if total_score >= 80 and negative_count == 0:
            return RiskLevel.LOW
        elif total_score >= 60 and negative_count <= 1:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH
    
    def _generate_suggestions(
        self,
        factors: List[FactorAnalysis],
        context_data: Dict[str, Any]
    ) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        # Factor별 제안
        for factor in factors:
            if factor.impact == "부정적" or factor.score < 60:
                if factor.factor_name == "입지 점수":
                    suggestions.append("⚠️ 교통 접근성 개선 방안 검토 필요 (역세권 개발, 버스노선 협의)")
                elif factor.factor_name == "용도지역 적합성":
                    suggestions.append("⚠️ 용도지역 변경 또는 지구단위계획 수립 검토")
                elif factor.factor_name == "토지가격 합리성":
                    suggestions.append("⚠️ 토지 매입가격 재협상 또는 감정평가 재검토 필요")
                elif factor.factor_name == "용적률/건폐율 실현가능성":
                    suggestions.append("⚠️ 용적률 인센티브 확보 방안 검토 (기부채납, 공개공지 등)")
                elif factor.factor_name == "리스크 수준":
                    suggestions.append("⚠️ 주요 리스크 요인 해결 후 재신청 권장")
                elif factor.factor_name == "시나리오 안정성":
                    suggestions.append("⚠️ 시나리오 재검토 및 사업성 개선 방안 필요")
        
        # 긍정적인 경우
        if not suggestions:
            suggestions.append("✅ 현재 조건으로 LH 심사 통과 가능성 높음")
            suggestions.append("✅ 추가 개선 사항 없이 신청 진행 가능")
        
        return suggestions
    
    def _predict_scenarios(
        self,
        context_data: Dict[str, Any],
        factors: List[FactorAnalysis]
    ) -> List[ScenarioPrediction]:
        """시나리오 A/B/C 합격 확률 비교 예측"""
        scenario = context_data.get("scenario", {})
        scenarios = scenario.get("scenarios", [])
        base_score = self._calculate_total_score(factors)
        
        predictions = []
        
        # v40.2 구조: scenarios 배열 (최대 3개)
        for idx, scenario_data in enumerate(scenarios[:3]):  # 최대 3개만
            if not scenario_data:
                continue
            
            scenario_name = scenario_data.get("name", f"시나리오 {chr(65+idx)}")  # A, B, C
            units = scenario_data.get("unit_count", 0)
            irr = scenario_data.get("irr", 0)
            
            # 시나리오별 가산점/감산점
            if idx == 0:
                # 첫 번째 시나리오 (보통 보수적)
                adjusted_score = base_score + 3
                is_recommended = True
            elif idx == 1:
                # 두 번째 시나리오 (중간)
                adjusted_score = base_score
                is_recommended = False
            else:  # idx == 2
                # 세 번째 시나리오 (공격적)
                adjusted_score = base_score - 5
                is_recommended = False
            
            # IRR 추가 조정
            if irr >= 10:
                adjusted_score += 2
            elif irr < 7:
                adjusted_score -= 3
            
            # 확률 계산
            probability = self._calculate_pass_probability(adjusted_score, factors)
            
            predictions.append(ScenarioPrediction(
                scenario_name=f"SCENARIO {chr(65+idx)}",  # A, B, C
                total_units=units,
                pass_probability=round(probability, 1),
                is_recommended=is_recommended
            ))
        
        return predictions
    
    def _create_rejection_response(self, reason: str) -> LHReviewResponse:
        """사전 조건 불충족 시 거부 응답 생성"""
        return LHReviewResponse(
            context_id="N/A",
            housing_type="N/A",
            target_units=0,
            predicted_score=0.0,
            pass_probability=0.0,
            risk_level=RiskLevel.HIGH,
            factors=[],
            suggestions=[f"❌ 사전 조건 불충족: {reason}"],
            scenario_comparison=[]
        )


# 엔진 싱글톤 인스턴스
lh_review_engine = LHReviewEngine()
