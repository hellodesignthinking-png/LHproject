"""
ZeroSite v42 - LH 심사예측 Engine (Weight Optimized)
LH 공공주택 사전심사 AI 예측 엔진 (Rule-Based v2.0)

v42 Changes:
- price_rationality 가중치 25% → 35% (핵심 변경)
- location 가중치 20% → 15%
- structural 가중치 15% → 10%
- Calibration: 점수 분포 40~95점으로 확대

Author: ZeroSite AI Development Team
Date: 2025-12-14
Version: 2.0.0 (v42 Weight Optimized)
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


class LHReviewEngineV42:
    """
    LH 심사예측 엔진 v42 (Weight Optimized)
    
    v42 핵심 개선사항:
    1. price_rationality 가중치 상향 (25% → 35%)
       - v41 테스트 결과: 토지가격이 가장 중요한 변수임을 확인
       - LH 벤치마크 가격 대비 비율이 승인 결정에 가장 큰 영향
    
    2. location 가중치 하향 (20% → 15%)
       - 입지는 중요하지만, 이미 공시지가에 반영됨
       - 중복 평가 방지
    
    3. structural 가중치 하향 (15% → 10%)
       - 용도지역, FAR, BCR은 기본 요건
       - 변별력 낮음
    
    4. Calibration: 점수 분포 40~95점으로 확대
       - v41 문제: 82~89점에 집중 (변별력 부족)
       - v42 해결: 가격 비율에 따라 점수 범위 확대
    """
    
    # v42 가중치 설정 (총합 = 100%)
    WEIGHTS_V42 = {
        "location": 0.15,           # 15% (↓5% from v1)
        "price_rationality": 0.35,  # 35% (↑10% from v1) ← 핵심!
        "scale": 0.15,              # 15%
        "structural": 0.10,         # 10% (↓5% from v1)
        "policy": 0.15,             # 15%
        "risk": 0.10                # 10%
    }
    
    # v1 가중치 (비교용)
    WEIGHTS_V1 = {
        "location": 0.20,
        "price_rationality": 0.25,
        "scale": 0.15,
        "structural": 0.15,
        "policy": 0.15,
        "risk": 0.10
    }
    
    # LH 선호 용도지역
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
    
    # LH 지역별 벤치마크 가격 (㎡당, 단위: 만원)
    # v42: 실제 LH 매입가 데이터 기반으로 업데이트 예정
    LH_BENCHMARK_PRICES = {
        "서울": {
            "강남구": 3500,
            "서초구": 3500,
            "송파구": 3200,
            "강동구": 2800,
            "마포구": 3000,
            "용산구": 3200,
            "성동구": 2900,
            "default": 2500
        },
        "경기": {
            "성남시": 2500,
            "고양시": 2200,
            "용인시": 2300,
            "수원시": 2400,
            "default": 2000
        },
        "default": 1800
    }
    
    def __init__(self, use_v42_weights: bool = True):
        """
        엔진 초기화
        
        Args:
            use_v42_weights: True면 v42 가중치 사용, False면 v1 가중치 사용 (A/B 테스트용)
        """
        self.weights = self.WEIGHTS_V42 if use_v42_weights else self.WEIGHTS_V1
        self.version = "v42" if use_v42_weights else "v1"
        logger.info(f"LH Review Engine {self.version} initialized (Weight Optimized)")
    
    def predict(
        self,
        context_data: Dict[str, Any],
        housing_type: str,
        target_units: int
    ) -> LHReviewResponse:
        """
        LH 심사 예측 실행 (v42)
        
        Args:
            context_data: 기존 분석 Context
            housing_type: LH 주택 유형
            target_units: 목표 세대수
            
        Returns:
            LHReviewResponse: 예측 결과
        """
        logger.info(f"🔍 LH 심사예측 시작 ({self.version}) - {housing_type} / {target_units}세대")
        
        # Step 1: Factor 별 점수 계산
        factors = self._calculate_factors_v42(context_data, housing_type, target_units)
        
        # Step 2: 종합 점수 계산 (v42 가중치 적용)
        total_score = self._calculate_total_score_v42(factors)
        
        # Step 3: Calibration 적용 (40~95점 분포)
        calibrated_score = self._apply_calibration(total_score, factors)
        
        # Step 4: 합격 확률 계산
        pass_probability = self._calculate_pass_probability_v42(calibrated_score, factors)
        
        # Step 5: 리스크 레벨 판정
        risk_level = self._determine_risk_level_v42(calibrated_score, factors)
        
        # Step 6: 개선 제안
        suggestions = self._generate_suggestions_v42(factors, context_data)
        
        # Step 7: 시나리오 비교
        scenario_predictions = self._predict_scenarios_v42(context_data, factors)
        
        logger.info(f"✅ 예측 완료 ({self.version}) - 점수: {calibrated_score}/100, 확률: {pass_probability}%")
        
        return LHReviewResponse(
            context_id=context_data.get("context_id", "unknown"),
            housing_type=housing_type,
            target_units=target_units,
            predicted_score=round(calibrated_score, 1),
            pass_probability=round(pass_probability, 1),
            risk_level=risk_level,
            factors=factors,
            suggestions=suggestions,
            scenario_comparison=scenario_predictions,
            model_version=self.version  # v42 표시
        )
    
    def _calculate_factors_v42(
        self,
        context_data: Dict[str, Any],
        housing_type: str,
        target_units: int
    ) -> List[FactorAnalysis]:
        """
        6-Factor 점수 계산 (v42)
        
        v42 변경사항:
        - price_rationality 계산 강화 (더 엄격한 평가)
        - location 계산 간소화 (중복 제거)
        """
        factors = []
        
        # Factor 1: Location Score (15%)
        location_score = self._calculate_location_score_v42(context_data)
        factors.append(FactorAnalysis(
            factor_name="입지 점수",
            score=location_score,
            weight=int(self.weights["location"] * 100),
            weighted_score=location_score * self.weights["location"],
            basis=self._get_location_basis(context_data, location_score)
        ))
        
        # Factor 2: Price Rationality (35%) ← 핵심!
        price_score = self._calculate_price_rationality_v42(context_data)
        factors.append(FactorAnalysis(
            factor_name="토지가격 합리성",
            score=price_score,
            weight=int(self.weights["price_rationality"] * 100),
            weighted_score=price_score * self.weights["price_rationality"],
            basis=self._get_price_basis(context_data, price_score)
        ))
        
        # Factor 3: Scale Adequacy (15%)
        scale_score = self._calculate_scale_adequacy_v42(context_data, housing_type, target_units)
        factors.append(FactorAnalysis(
            factor_name="개발규모 적정성",
            score=scale_score,
            weight=int(self.weights["scale"] * 100),
            weighted_score=scale_score * self.weights["scale"],
            basis=self._get_scale_basis(target_units, housing_type, scale_score)
        ))
        
        # Factor 4: Structural Validity (10%)
        structural_score = self._calculate_structural_validity_v42(context_data)
        factors.append(FactorAnalysis(
            factor_name="구조적 타당성",
            score=structural_score,
            weight=int(self.weights["structural"] * 100),
            weighted_score=structural_score * self.weights["structural"],
            basis=self._get_structural_basis(context_data, structural_score)
        ))
        
        # Factor 5: Policy Compliance (15%)
        policy_score = self._calculate_policy_compliance_v42(context_data, housing_type, target_units)
        factors.append(FactorAnalysis(
            factor_name="정책 부합도",
            score=policy_score,
            weight=int(self.weights["policy"] * 100),
            weighted_score=policy_score * self.weights["policy"],
            basis=self._get_policy_basis(housing_type, policy_score)
        ))
        
        # Factor 6: Risk Level (10%)
        risk_score = self._calculate_risk_score_v42(context_data)
        factors.append(FactorAnalysis(
            factor_name="리스크 수준",
            score=risk_score,
            weight=int(self.weights["risk"] * 100),
            weighted_score=risk_score * self.weights["risk"],
            basis=self._get_risk_basis(context_data, risk_score)
        ))
        
        return factors
    
    def _calculate_price_rationality_v42(self, context_data: Dict[str, Any]) -> float:
        """
        토지가격 합리성 계산 (v42 강화)
        
        v42 변경:
        - LH 벤치마크 가격 대비 비율 계산 강화
        - 지역별 벤치마크 적용
        - 더 엄격한 평가 기준
        """
        appraisal = context_data.get("appraisal", {})
        
        # 감정가
        value_per_sqm = appraisal.get("value_per_sqm", 0)
        
        # 주소에서 지역 추출
        address = context_data.get("land_info", {}).get("address", "")
        region, district = self._extract_region_district(address)
        
        # LH 벤치마크 가격 조회
        lh_benchmark = self._get_lh_benchmark_price(region, district)
        
        if lh_benchmark == 0:
            return 50.0  # 벤치마크 없으면 중간 점수
        
        # 비율 계산 (감정가 / LH 벤치마크)
        ratio = value_per_sqm / (lh_benchmark * 10000)  # 만원 → 원 변환
        
        # v42 점수 산출 (더 엄격)
        if ratio <= 0.80:
            score = 100.0  # 매우 저렴 (LH 최우선 선호)
        elif ratio <= 0.90:
            score = 95.0   # 저렴 (LH 선호)
        elif ratio <= 1.00:
            score = 85.0   # 적정 (LH 허용 범위)
        elif ratio <= 1.10:
            score = 70.0   # 약간 비쌈 (협상 필요)
        elif ratio <= 1.20:
            score = 50.0   # 비쌈 (승인 어려움)
        elif ratio <= 1.30:
            score = 30.0   # 매우 비쌈 (거절 가능성 높음)
        else:
            score = 10.0   # 과도하게 비쌈 (거절 거의 확실)
        
        # 거래사례 신뢰도 가산점 (최대 5점)
        transactions = appraisal.get("transactions", [])
        if len(transactions) >= 15:
            score = min(score + 5, 100)
        elif len(transactions) >= 10:
            score = min(score + 3, 100)
        elif len(transactions) >= 5:
            score = min(score + 1, 100)
        
        return round(score, 1)
    
    def _extract_region_district(self, address: str) -> tuple:
        """주소에서 지역 및 구 추출"""
        if "서울" in address:
            region = "서울"
            # 구 추출
            for gu in ["강남구", "서초구", "송파구", "강동구", "마포구", "용산구", "성동구"]:
                if gu in address:
                    return (region, gu)
            return (region, "default")
        elif "경기" in address:
            region = "경기"
            for city in ["성남시", "고양시", "용인시", "수원시"]:
                if city in address:
                    return (region, city)
            return (region, "default")
        else:
            return ("default", "default")
    
    def _get_lh_benchmark_price(self, region: str, district: str) -> float:
        """LH 벤치마크 가격 조회 (㎡당 만원)"""
        if region in self.LH_BENCHMARK_PRICES:
            region_prices = self.LH_BENCHMARK_PRICES[region]
            return region_prices.get(district, region_prices.get("default", 2000))
        else:
            return self.LH_BENCHMARK_PRICES["default"]
    
    def _calculate_location_score_v42(self, context_data: Dict[str, Any]) -> float:
        """
        입지 점수 계산 (v42 간소화)
        
        v42 변경:
        - 기본 입지 평가만 수행 (공시지가에 이미 반영되어 있음)
        - 중복 평가 제거
        """
        appraisal = context_data.get("appraisal", {})
        premium = appraisal.get("premium", {})
        factors = premium.get("factors", [])
        
        score = 50  # 기본 점수
        
        # 주요 프리미엄 요인만 평가
        if any('지하철' in f.get('factor', '') for f in factors):
            score += 20
        
        if any('학교' in f.get('factor', '') or '학군' in f.get('factor', '') for f in factors):
            score += 15
        
        if any('공원' in f.get('factor', '') or '한강' in f.get('factor', '') for f in factors):
            score += 10
        
        # 혐오시설 감점
        restrictions = appraisal.get('restrictions', [])
        if any('공장' in r or '묘지' in r for r in restrictions):
            score -= 15
        
        return min(max(score, 0), 100)
    
    def _calculate_scale_adequacy_v42(
        self,
        context_data: Dict[str, Any],
        housing_type: str,
        target_units: int
    ) -> float:
        """개발규모 적정성 계산 (v42)"""
        # LH 선호 규모 (주택유형별)
        if housing_type == "청년":
            ideal_min, ideal_max = 40, 100
        elif housing_type in ["신혼·신생아 I", "신혼·신생아 II"]:
            ideal_min, ideal_max = 30, 80
        elif housing_type == "고령자":
            ideal_min, ideal_max = 20, 60
        else:
            ideal_min, ideal_max = 30, 100
        
        if ideal_min <= target_units <= ideal_max:
            return 100.0
        elif target_units < ideal_min:
            gap = ideal_min - target_units
            return max(50.0 - gap * 2, 0)
        else:  # target_units > ideal_max
            gap = target_units - ideal_max
            return max(90.0 - gap / 10, 50)
    
    def _calculate_structural_validity_v42(self, context_data: Dict[str, Any]) -> float:
        """구조적 타당성 계산 (v42 간소화)"""
        appraisal = context_data.get("appraisal", {})
        zoning = appraisal.get("zoning", {})
        
        zone_type = context_data.get("diagnosis", {}).get("zone_type", "")
        far = zoning.get("far", 0)
        bcr = zoning.get("bcr", 0)
        
        score = 0
        
        # 용도지역 (30점)
        if "주거" in zone_type:
            score += 30
        elif "준주거" in zone_type or "상업" in zone_type:
            score += 20
        else:
            score += 10
        
        # 용적률 (40점)
        if 150 <= far <= 300:
            score += 40
        elif 100 <= far < 150:
            score += 30
        else:
            score += 20
        
        # 건폐율 (30점)
        if 50 <= bcr <= 70:
            score += 30
        else:
            score += 15
        
        return score
    
    def _calculate_policy_compliance_v42(
        self,
        context_data: Dict[str, Any],
        housing_type: str,
        target_units: int
    ) -> float:
        """정책 부합도 계산 (v42)"""
        # 2025년 LH 우선순위
        policy_priority = {
            "청년": 1.0,
            "신혼·신생아 I": 0.95,
            "신혼·신생아 II": 0.95,
            "다자녀": 0.9,
            "고령자": 0.75,
            "일반": 0.6
        }
        
        base_score = policy_priority.get(housing_type, 0.6) * 100
        
        # 규모 가산점
        if 30 <= target_units <= 100:
            base_score = min(base_score + 10, 100)
        
        return base_score
    
    def _calculate_risk_score_v42(self, context_data: Dict[str, Any]) -> float:
        """리스크 수준 계산 (v42)"""
        risk_score = 100  # 기본 100 (리스크 없음)
        
        appraisal = context_data.get("appraisal", {})
        
        # 법적 리스크
        restrictions = appraisal.get("restrictions", [])
        if len(restrictions) > 0:
            risk_score -= len(restrictions) * 10
        
        # 거래사례 부족 리스크
        transactions = appraisal.get("transactions", [])
        if len(transactions) < 5:
            risk_score -= 30
        elif len(transactions) < 10:
            risk_score -= 15
        
        # 감정평가 신뢰도
        confidence = appraisal.get("confidence_level", "")
        if confidence == "낮음":
            risk_score -= 20
        
        return max(risk_score, 0)
    
    def _calculate_total_score_v42(self, factors: List[FactorAnalysis]) -> float:
        """종합 점수 계산 (v42 가중치 적용)"""
        total = sum(f.weighted_score for f in factors)
        return round(total, 1)
    
    def _apply_calibration(self, total_score: float, factors: List[FactorAnalysis]) -> float:
        """
        Calibration 적용 (40~95점 분포)
        
        v42 핵심 개선:
        - v41 문제: 82~89점 집중 (변별력 부족)
        - v42 해결: 가격 비율에 따라 점수 범위 확대
        
        Calibration Logic:
        - 가격이 LH 벤치마크보다 낮으면 → 점수 상승
        - 가격이 LH 벤치마크보다 높으면 → 점수 하락
        """
        # price_rationality factor 찾기
        price_factor = next((f for f in factors if "가격" in f.factor_name), None)
        
        if price_factor is None:
            return total_score
        
        price_score = price_factor.score
        
        # Calibration 적용
        if price_score >= 95:
            # 가격 매우 좋음 → 점수 상승
            calibrated = total_score * 1.05
        elif price_score >= 85:
            # 가격 좋음 → 점수 유지
            calibrated = total_score
        elif price_score >= 70:
            # 가격 보통 → 점수 약간 하락
            calibrated = total_score * 0.95
        elif price_score >= 50:
            # 가격 나쁨 → 점수 하락
            calibrated = total_score * 0.85
        else:
            # 가격 매우 나쁨 → 점수 큰 폭 하락
            calibrated = total_score * 0.70
        
        # 최종 점수 범위: 40~95점
        return max(40.0, min(calibrated, 95.0))
    
    def _calculate_pass_probability_v42(self, score: float, factors: List[FactorAnalysis]) -> float:
        """합격 확률 계산 (v42)"""
        # 기본 확률 (점수 기반)
        if score >= 85:
            base_prob = 90.0
        elif score >= 75:
            base_prob = 80.0
        elif score >= 65:
            base_prob = 65.0
        elif score >= 55:
            base_prob = 45.0
        elif score >= 45:
            base_prob = 25.0
        else:
            base_prob = 10.0
        
        # 가격 요인 조정
        price_factor = next((f for f in factors if "가격" in f.factor_name), None)
        if price_factor and price_factor.score < 50:
            base_prob *= 0.80  # 가격 나쁘면 확률 20% 감소
        
        return min(base_prob, 95.0)
    
    def _determine_risk_level_v42(self, score: float, factors: List[FactorAnalysis]) -> RiskLevel:
        """리스크 레벨 판정 (v42)"""
        if score >= 75:
            return RiskLevel.LOW
        elif score >= 55:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH
    
    def _generate_suggestions_v42(
        self,
        factors: List[FactorAnalysis],
        context_data: Dict[str, Any]
    ) -> List[str]:
        """개선 제안 생성 (v42)"""
        suggestions = []
        
        # 가격 관련 제안
        price_factor = next((f for f in factors if "가격" in f.factor_name), None)
        if price_factor and price_factor.score < 70:
            suggestions.append(
                f"토지 매입가 협상 권장: 현재 가격에서 {100-price_factor.score:.0f}% 인하 필요"
            )
        
        # 규모 관련 제안
        scale_factor = next((f for f in factors if "규모" in f.factor_name), None)
        if scale_factor and scale_factor.score < 80:
            suggestions.append("개발 규모 조정 검토 (LH 선호 세대수 범위 참고)")
        
        # 입지 관련 제안
        location_factor = next((f for f in factors if "입지" in f.factor_name), None)
        if location_factor and location_factor.score < 60:
            suggestions.append("입지 개선 또는 다른 토지 검토 권장")
        
        if not suggestions:
            suggestions.append("현 상태로 LH 신청 가능 (추가 개선 불필요)")
        
        return suggestions
    
    def _predict_scenarios_v42(
        self,
        context_data: Dict[str, Any],
        factors: List[FactorAnalysis]
    ) -> List[ScenarioPrediction]:
        """시나리오 A/B/C 비교 예측 (v42)"""
        scenarios = context_data.get("scenario", {}).get("scenarios", [])
        
        predictions = []
        for scenario in scenarios[:3]:  # A, B, C만
            # 시나리오별 점수 조정 (간단 버전)
            base_score = sum(f.weighted_score for f in factors)
            
            # 정책 우선순위 반영
            unit_type = scenario.get("unit_type", "")
            if unit_type == "청년":
                adjusted_score = base_score * 1.05
            elif unit_type == "신혼부부":
                adjusted_score = base_score * 1.02
            else:
                adjusted_score = base_score * 0.98
            
            adjusted_score = max(40, min(adjusted_score, 95))
            
            predictions.append(ScenarioPrediction(
                scenario_name=scenario.get("name", "Unknown"),
                predicted_score=round(adjusted_score, 1),
                pass_probability=round(adjusted_score, 1),
                recommendation="추천" if adjusted_score >= 75 else "검토" if adjusted_score >= 60 else "비추천"
            ))
        
        return predictions
    
    # Basis 생성 메서드들
    def _get_location_basis(self, context_data: Dict[str, Any], score: float) -> str:
        """입지 점수 근거"""
        return f"입지 평가 점수: {score:.1f}점"
    
    def _get_price_basis(self, context_data: Dict[str, Any], score: float) -> str:
        """가격 합리성 근거"""
        appraisal = context_data.get("appraisal", {})
        value_per_sqm = appraisal.get("value_per_sqm", 0)
        
        address = context_data.get("land_info", {}).get("address", "")
        region, district = self._extract_region_district(address)
        lh_benchmark = self._get_lh_benchmark_price(region, district)
        
        ratio = value_per_sqm / (lh_benchmark * 10000) if lh_benchmark > 0 else 1.0
        
        return f"감정가 ㎡당 {value_per_sqm:,.0f}원 vs LH벤치마크 {lh_benchmark:,.0f}만원 (비율: {ratio:.2f})"
    
    def _get_scale_basis(self, target_units: int, housing_type: str, score: float) -> str:
        """규모 적정성 근거"""
        return f"{housing_type} {target_units}세대 (점수: {score:.1f})"
    
    def _get_structural_basis(self, context_data: Dict[str, Any], score: float) -> str:
        """구조적 타당성 근거"""
        return f"구조 평가 점수: {score:.1f}점"
    
    def _get_policy_basis(self, housing_type: str, score: float) -> str:
        """정책 부합도 근거"""
        return f"{housing_type} 정책 우선순위 반영 (점수: {score:.1f})"
    
    def _get_risk_basis(self, context_data: Dict[str, Any], score: float) -> str:
        """리스크 수준 근거"""
        return f"리스크 평가 점수: {score:.1f}점"


# v42 Engine Instance (기본)
lh_review_engine_v42 = LHReviewEngineV42(use_v42_weights=True)

# v1 Engine Instance (비교용)
lh_review_engine_v1 = LHReviewEngineV42(use_v42_weights=False)
