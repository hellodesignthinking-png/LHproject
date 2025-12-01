"""
지자체 수요예측 엔진 LITE 1.0
Municipal Demand Prediction Engine

LH 신축매입임대 수요를 5가지 핵심 지표로 예측
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class DemandPredictionResult:
    """수요 예측 결과"""
    demand_score: float  # 0-100점
    demand_level: str  # 높음/보통/낮음
    comment: str  # 종합 코멘트
    factor_scores: Dict[str, float]  # 요인별 점수
    recommendations: list  # 추천사항
    household_type_scores: Dict[str, float] = None  # 세대유형별 점수 (청년/신혼/고령자)


class MunicipalDemandPredictor:
    """지자체 수요예측 엔진 LITE 1.0"""
    
    # 기본 가중치 (합계 100%) - unit_type이 없을 경우 사용
    DEFAULT_WEIGHTS = {
        "subway_distance": 20,      # 지하철역 거리
        "university_distance": 20,  # 대학/산단 거리
        "youth_ratio": 20,           # 20~34세 비율
        "rent_price": 20,            # 원룸 월세 시세
        "existing_supply": 20        # 기존 임대주택 수
    }
    
    def predict(
        self,
        subway_distance: float,         # 지하철역까지 거리 (m)
        university_distance: float,     # 대학/산단까지 거리 (m)
        youth_ratio: float,             # 20~34세 인구 비율 (%)
        avg_rent_price: float,          # 평균 원룸 월세 (만원)
        existing_rental_units: int,     # 기존 임대주택 세대수
        target_units: int = 50,         # 계획 세대수
        unit_type: str = None,          # 주거 유형 (청년, 신혼·신생아 I, 등)
        lh_version: str = "2024",       # LH 규칙 버전
        nearby_facilities: Dict[str, float] = None  # 주변 시설 거리 정보
    ) -> DemandPredictionResult:
        """
        수요 예측 수행
        
        Returns:
            DemandPredictionResult 객체
        """
        
        # 유형별 가중치 로드 (LH Rules JSON 기반)
        weights = self._get_unit_type_weights(unit_type, lh_version)
        
        # 1. 지하철역 거리 점수 (가까울수록 높음)
        subway_score = self._calculate_subway_score(subway_distance)
        
        # 2. 대학/산단 거리 점수 (가까울수록 높음)
        university_score = self._calculate_university_score(university_distance)
        
        # 3. 청년 인구 비율 점수 (높을수록 높음)
        youth_score = self._calculate_youth_score(youth_ratio)
        
        # 4. 월세 시세 점수 (높을수록 높음 = 수요가 높다는 의미)
        rent_score = self._calculate_rent_score(avg_rent_price)
        
        # 5. 기존 공급 점수 (많을수록 낮음 = 경쟁 심화)
        supply_score = self._calculate_supply_score(existing_rental_units, target_units)
        
        # 요인별 점수
        factor_scores = {
            "지하철 접근성": round(subway_score, 1),
            "대학/산단 접근성": round(university_score, 1),
            "청년 인구 비율": round(youth_score, 1),
            "월세 시세": round(rent_score, 1),
            "기존 공급량": round(supply_score, 1)
        }
        
        # 기본 가중 평균 계산 (현재 unit_type의 가중치 적용)
        base_score = (
            subway_score * weights["subway_distance"] / 100 +
            university_score * weights["university_distance"] / 100 +
            youth_score * weights["youth_ratio"] / 100 +
            rent_score * weights["rent_price"] / 100 +
            supply_score * weights["existing_supply"] / 100
        )
        
        # v6.1 수정: 세대유형별 독립 점수 계산 (각 유형의 고유 가중치 + 시설 가중치)
        # 각 세대유형별로 LH Rules의 고유 demand_weights를 사용하여 differentiated scores 생성
        household_type_scores = {}
        
        # 청년형: LH Rules 청년 가중치 + 대학교 접근성 보너스
        weights_청년 = self._get_unit_type_weights("청년", lh_version)
        base_score_청년 = (
            subway_score * weights_청년["subway_distance"] / 100 +
            university_score * weights_청년["university_distance"] / 100 +
            youth_score * weights_청년["youth_ratio"] / 100 +
            rent_score * weights_청년["rent_price"] / 100 +
            supply_score * weights_청년["existing_supply"] / 100
        )
        weight_청년 = self._calculate_facility_weight("청년", nearby_facilities)
        household_type_scores["청년"] = round(base_score_청년 * weight_청년, 1)
        
        # 신혼형 (I): LH Rules 신혼 가중치 + 학교 접근성 보너스
        weights_신혼 = self._get_unit_type_weights("신혼·신생아 I", lh_version)
        base_score_신혼 = (
            subway_score * weights_신혼["subway_distance"] / 100 +
            university_score * weights_신혼["university_distance"] / 100 +
            youth_score * weights_신혼["youth_ratio"] / 100 +
            rent_score * weights_신혼["rent_price"] / 100 +
            supply_score * weights_신혼["existing_supply"] / 100
        )
        weight_신혼 = self._calculate_facility_weight("신혼·신생아 I", nearby_facilities)
        household_type_scores["신혼"] = round(base_score_신혼 * weight_신혼, 1)
        
        # 고령자형: LH Rules 고령자 가중치 + 병원/복지 접근성 보너스
        weights_고령자 = self._get_unit_type_weights("고령자", lh_version)
        base_score_고령자 = (
            subway_score * weights_고령자["subway_distance"] / 100 +
            university_score * weights_고령자["university_distance"] / 100 +
            youth_score * weights_고령자["youth_ratio"] / 100 +
            rent_score * weights_고령자["rent_price"] / 100 +
            supply_score * weights_고령자["existing_supply"] / 100
        )
        weight_고령자 = self._calculate_facility_weight("고령자", nearby_facilities)
        household_type_scores["고령자"] = round(base_score_고령자 * weight_고령자, 1)
        
        # 현재 지정된 unit_type에 해당하는 가중치 적용
        facility_weight = self._calculate_facility_weight(unit_type, nearby_facilities)
        
        # 최종 점수 = base_score × facility_weight (현재 unit_type 기준)
        total_score = base_score * facility_weight
        
        print(f"    🔍 [Type Demand Debug] 청년: {household_type_scores['청년']}점, 신혼: {household_type_scores['신혼']}점, 고령자: {household_type_scores['고령자']}점, 현재({unit_type}): {total_score:.1f}점")
        
        # 수요 수준 판정
        if total_score >= 75:
            demand_level = "높음"
        elif total_score >= 50:
            demand_level = "보통"
        else:
            demand_level = "낮음"
        
        # 종합 코멘트 생성
        comment = self._generate_comment(
            total_score, demand_level, factor_scores,
            subway_distance, youth_ratio
        )
        
        # 추천사항 생성
        recommendations = self._generate_recommendations(
            factor_scores, subway_distance, youth_ratio, 
            avg_rent_price, existing_rental_units
        )
        
        return DemandPredictionResult(
            demand_score=round(total_score, 1),
            demand_level=demand_level,
            comment=comment,
            factor_scores=factor_scores,
            recommendations=recommendations,
            household_type_scores=household_type_scores  # 세대유형별 차별화된 점수
        )
    
    def _calculate_subway_score(self, distance: float) -> float:
        """지하철역 거리 점수 (0-100)"""
        if distance <= 500:
            return 100
        elif distance <= 800:
            return 90
        elif distance <= 1000:
            return 75
        elif distance <= 1500:
            return 50
        elif distance <= 2000:
            return 30
        else:
            return 10
    
    def _calculate_university_score(self, distance: float) -> float:
        """대학/산단 거리 점수 (0-100)"""
        if distance <= 1000:
            return 100
        elif distance <= 2000:
            return 85
        elif distance <= 3000:
            return 65
        elif distance <= 5000:
            return 40
        else:
            return 20
    
    def _calculate_youth_score(self, ratio: float) -> float:
        """청년 인구 비율 점수 (0-100)"""
        if ratio >= 35:
            return 100
        elif ratio >= 30:
            return 85
        elif ratio >= 25:
            return 70
        elif ratio >= 20:
            return 50
        elif ratio >= 15:
            return 30
        else:
            return 10
    
    def _calculate_rent_score(self, rent: float) -> float:
        """월세 시세 점수 (0-100)"""
        # 원룸 월세 기준 (만원)
        if rent >= 60:
            return 100
        elif rent >= 50:
            return 85
        elif rent >= 40:
            return 70
        elif rent >= 30:
            return 50
        elif rent >= 25:
            return 30
        else:
            return 15
    
    def _calculate_supply_score(self, existing: int, target: int) -> float:
        """기존 공급 점수 (0-100) - 많을수록 낮음"""
        # 반경 2km 내 기존 임대주택 대비
        if existing == 0:
            return 100
        
        ratio = existing / max(target, 1)
        
        if ratio <= 1:
            return 100
        elif ratio <= 3:
            return 80
        elif ratio <= 5:
            return 60
        elif ratio <= 10:
            return 40
        elif ratio <= 20:
            return 20
        else:
            return 10
    
    def _generate_comment(
        self,
        total_score: float,
        demand_level: str,
        factor_scores: Dict[str, float],
        subway_distance: float,
        youth_ratio: float
    ) -> str:
        """종합 코멘트 생성"""
        
        comments = []
        
        # 주요 강점 파악
        if factor_scores["지하철 접근성"] >= 80:
            comments.append("역세권 입지로 접근성이 우수")
        
        if factor_scores["청년 인구 비율"] >= 70:
            comments.append("청년층 비중이 높아 타겟 수요 풍부")
        
        if factor_scores["월세 시세"] >= 70:
            comments.append("높은 월세 시세로 임대 수요 강함")
        
        if factor_scores["기존 공급량"] >= 70:
            comments.append("기존 공급이 적어 경쟁 우위 확보 가능")
        
        # 약점 파악
        if factor_scores["지하철 접근성"] < 50:
            comments.append("지하철 접근성 개선 필요")
        
        if factor_scores["청년 인구 비율"] < 50:
            comments.append("청년 인구 비율이 낮아 수요 제한적")
        
        if len(comments) == 0:
            comments.append(f"종합 점수 {total_score:.1f}점으로 {demand_level} 수요 예상")
        
        return f"{demand_level} 수요 예상. " + ", ".join(comments) + "."
    
    def _generate_recommendations(
        self,
        factor_scores: Dict[str, float],
        subway_distance: float,
        youth_ratio: float,
        avg_rent: float,
        existing_units: int
    ) -> list:
        """추천사항 생성"""
        
        recommendations = []
        
        # 입지 관련
        if subway_distance <= 800:
            recommendations.append("✅ 역세권 입지 강점을 마케팅에 적극 활용")
        elif subway_distance <= 1500:
            recommendations.append("⚠️ 역세권 셔틀버스 운영 검토")
        else:
            recommendations.append("❌ 교통 접근성 개선 방안 필요 (커뮤니티 버스 등)")
        
        # 수요층 관련
        if youth_ratio >= 30:
            recommendations.append("✅ 청년층 맞춤 설계 및 공유 공간 확충")
        elif youth_ratio >= 20:
            recommendations.append("⚠️ 다양한 연령대를 고려한 유닛 믹스 검토")
        else:
            recommendations.append("❌ 타겟층 다각화 필요 (신혼부부, 고령자 등)")
        
        # 가격 관련
        if avg_rent >= 50:
            recommendations.append("✅ 높은 시세 유지 가능, 프리미엄 옵션 고려")
        elif avg_rent >= 35:
            recommendations.append("⚠️ 적정 임대료 설정 중요, 시장 조사 필수")
        else:
            recommendations.append("❌ 저렴한 임대료 전략 필요, 비용 절감 방안 검토")
        
        # 공급 관련
        if existing_units <= 100:
            recommendations.append("✅ 기존 공급 부족, 선점 효과 기대")
        elif existing_units <= 300:
            recommendations.append("⚠️ 경쟁 물건 분석 및 차별화 전략 수립")
        else:
            recommendations.append("❌ 과잉 공급 우려, 신중한 사업 검토 필요")
        
        return recommendations
    
    def _calculate_facility_weight(
        self,
        unit_type: str,
        nearby_facilities: Dict[str, float] = None
    ) -> float:
        """
        세대유형별 주변 시설 거리 기반 가중치 계산
        
        요구사항:
        - 대학 1km 이내 → 청년형 +0.20 (1.20배)
        - 초등/중학교 800m 이내 → 신혼형 +0.15 (1.15배)
        - 대형병원 1.5km 또는 노인복지시설 1km → 고령자형 +0.25 (1.25배)
        
        Args:
            unit_type: 세대유형 (청년/신혼·신생아 I/고령자 등)
            nearby_facilities: 주변 시설 거리 딕셔너리
                {
                    "university": 거리(m),
                    "elementary_school": 거리(m),
                    "middle_school": 거리(m),
                    "hospital": 거리(m),
                    "senior_welfare": 거리(m)
                }
        
        Returns:
            가중치 배수 (1.0 = 기본, 1.20 = +20%)
        """
        if not unit_type or not nearby_facilities:
            return 1.0
        
        weight = 1.0
        
        # 청년형: 대학 1km 이내
        if "청년" in unit_type:
            university_dist = nearby_facilities.get("university", float('inf'))
            if university_dist <= 1000:
                weight += 0.20
                
        # 신혼형: 초등/중학교 800m 이내
        elif "신혼" in unit_type or "신생아" in unit_type:
            elem_dist = nearby_facilities.get("elementary_school", float('inf'))
            middle_dist = nearby_facilities.get("middle_school", float('inf'))
            
            if elem_dist <= 800 or middle_dist <= 800:
                weight += 0.15
                
        # 고령자형: 대형병원 1.5km 또는 노인복지시설 1km
        elif "고령자" in unit_type or "어르신" in unit_type:
            hospital_dist = nearby_facilities.get("hospital", float('inf'))
            welfare_dist = nearby_facilities.get("senior_welfare", float('inf'))
            
            if hospital_dist <= 1500 or welfare_dist <= 1000:
                weight += 0.25
        
        return weight
    
    def _get_unit_type_weights(self, unit_type: str, lh_version: str) -> Dict[str, float]:
        """
        유형별 수요 가중치 로드 (LH Rules JSON 기반)
        
        Args:
            unit_type: 주거 유형 (청년, 신혼·신생아 I, 고령자 등)
            lh_version: LH 규칙 버전
            
        Returns:
            가중치 딕셔너리 (합계 100)
        """
        if not unit_type:
            return self.DEFAULT_WEIGHTS
        
        try:
            from app.services.lh_rules import get_housing_type_info
            
            # LH Rules에서 유형 정보 로드
            type_info = get_housing_type_info(unit_type, lh_version)
            
            if type_info and "demand_weights" in type_info:
                weights = type_info["demand_weights"]
                
                # 가중치 합계 검증 (100이 아니면 정규화)
                total = sum(weights.values())
                if abs(total - 100) > 0.1:
                    # 정규화
                    normalized_weights = {k: v / total * 100 for k, v in weights.items()}
                    return normalized_weights
                
                return weights
            else:
                # demand_weights가 없으면 기본값 사용
                return self.DEFAULT_WEIGHTS
        
        except Exception as e:
            # 오류 발생 시 기본값 사용
            print(f"⚠️ 유형별 가중치 로드 실패: {e}")
            return self.DEFAULT_WEIGHTS
