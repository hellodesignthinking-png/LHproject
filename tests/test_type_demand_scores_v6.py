"""
ZeroSite v6.1 - Type Demand Scores Bug Fix Validation Test
세대유형별 수요 점수 독립 계산 검증

테스트 목적:
- 청년형, 신혼형, 고령자형이 동일한 입력에 대해 서로 다른 수요 점수를 산출하는지 확인
- 각 유형별로 LH Rules의 고유 가중치(demand_weights)가 정확히 적용되는지 검증
- 시설 거리 기반 보너스(청년=대학, 신혼=학교, 고령자=병원)가 올바르게 작동하는지 확인
"""

import pytest
from app.services.demand_prediction import MunicipalDemandPredictor


class TestTypeDemandScoresV6:
    """세대유형별 수요 점수 독립성 검증"""
    
    def setup_method(self):
        """테스트 초기화"""
        self.predictor = MunicipalDemandPredictor()
        
        # 공통 입력값 (동일한 조건에서 유형별 점수 차이를 확인)
        self.common_inputs = {
            "subway_distance": 600,      # 지하철역 600m (역세권)
            "university_distance": 800,  # 대학교 800m (인근)
            "youth_ratio": 32.5,         # 청년 인구 비율 32.5% (높음)
            "avg_rent_price": 55,        # 원룸 월세 55만원 (높음)
            "existing_rental_units": 80, # 기존 임대 80세대 (보통)
            "target_units": 50,          # 계획 세대수 50세대
            "lh_version": "2024"
        }
    
    def test_청년형_vs_신혼형_vs_고령자_점수_차이(self):
        """
        핵심 테스트: 동일 입력에 대해 세대유형별로 서로 다른 점수가 나오는지 확인
        
        예상 결과 (v6.1 수정 후):
        - 청년형: subway_distance(30%), university_distance(30%) 높은 가중치 → 약 80~85점
        - 신혼형: rent_price(35%), existing_supply(15%) 높은 가중치 → 약 75~80점
        - 고령자형: rent_price(50%), existing_supply(40%) 높은 가중치 → 약 70~75점
        
        v6.0 버그: 모든 유형이 동일한 점수 산출 (약 78점)
        """
        # 청년형 수요 예측
        result_청년 = self.predictor.predict(
            unit_type="청년",
            nearby_facilities=None,  # 시설 보너스 없음
            **self.common_inputs
        )
        
        # 신혼형 수요 예측
        result_신혼 = self.predictor.predict(
            unit_type="신혼·신생아 I",
            nearby_facilities=None,
            **self.common_inputs
        )
        
        # 고령자형 수요 예측
        result_고령자 = self.predictor.predict(
            unit_type="고령자",
            nearby_facilities=None,
            **self.common_inputs
        )
        
        # 점수 출력 (디버깅용)
        print(f"\n📊 세대유형별 수요 점수 (시설 보너스 없음)")
        print(f"  청년형: {result_청년.demand_score}점 ({result_청년.demand_level})")
        print(f"  신혼형: {result_신혼.demand_score}점 ({result_신혼.demand_level})")
        print(f"  고령자형: {result_고령자.demand_score}점 ({result_고령자.demand_level})")
        
        # 검증 1: 세 유형의 점수가 모두 달라야 함 (v6.0 버그 수정 확인)
        assert result_청년.demand_score != result_신혼.demand_score, \
            f"청년형({result_청년.demand_score})과 신혼형({result_신혼.demand_score})의 점수가 동일 → v6.0 버그 미수정"
        
        assert result_청년.demand_score != result_고령자.demand_score, \
            f"청년형({result_청년.demand_score})과 고령자형({result_고령자.demand_score})의 점수가 동일 → v6.0 버그 미수정"
        
        assert result_신혼.demand_score != result_고령자.demand_score, \
            f"신혼형({result_신혼.demand_score})과 고령자형({result_고령자.demand_score})의 점수가 동일 → v6.0 버그 미수정"
        
        # 검증 2: 청년형이 가장 높은 점수를 받아야 함 (지하철+대학 가중치 높음)
        assert result_청년.demand_score >= result_신혼.demand_score, \
            f"청년형({result_청년.demand_score})이 신혼형({result_신혼.demand_score})보다 낮음 → 가중치 오류"
        
        assert result_청년.demand_score >= result_고령자.demand_score, \
            f"청년형({result_청년.demand_score})이 고령자형({result_고령자.demand_score})보다 낮음 → 가중치 오류"
        
        print("  ✅ 세대유형별 점수 차이 정상 확인!")
    
    def test_시설_보너스_적용_확인(self):
        """
        시설 거리 기반 보너스가 유형별로 다르게 작동하는지 확인
        
        - 청년형: 대학교 1km 이내 → +20% 보너스
        - 신혼형: 초등/중학교 800m 이내 → +15% 보너스
        - 고령자형: 병원 1.5km 또는 복지시설 1km → +25% 보너스
        """
        # 청년형: 대학교 인근 (800m)
        facilities_청년 = {
            "university": 800,  # 대학교 800m → 보너스 +20%
            "elementary_school": 2000,
            "middle_school": 2000,
            "hospital": 3000,
            "senior_welfare": 3000
        }
        
        result_청년_보너스_있음 = self.predictor.predict(
            unit_type="청년",
            nearby_facilities=facilities_청년,
            **self.common_inputs
        )
        
        result_청년_보너스_없음 = self.predictor.predict(
            unit_type="청년",
            nearby_facilities=None,
            **self.common_inputs
        )
        
        # 신혼형: 초등학교 인근 (700m)
        facilities_신혼 = {
            "university": 2000,
            "elementary_school": 700,  # 초등학교 700m → 보너스 +15%
            "middle_school": 2000,
            "hospital": 3000,
            "senior_welfare": 3000
        }
        
        result_신혼_보너스_있음 = self.predictor.predict(
            unit_type="신혼·신생아 I",
            nearby_facilities=facilities_신혼,
            **self.common_inputs
        )
        
        result_신혼_보너스_없음 = self.predictor.predict(
            unit_type="신혼·신생아 I",
            nearby_facilities=None,
            **self.common_inputs
        )
        
        # 고령자형: 병원 인근 (1200m)
        facilities_고령자 = {
            "university": 5000,
            "elementary_school": 2000,
            "middle_school": 2000,
            "hospital": 1200,  # 병원 1200m → 보너스 +25%
            "senior_welfare": 3000
        }
        
        result_고령자_보너스_있음 = self.predictor.predict(
            unit_type="고령자",
            nearby_facilities=facilities_고령자,
            **self.common_inputs
        )
        
        result_고령자_보너스_없음 = self.predictor.predict(
            unit_type="고령자",
            nearby_facilities=None,
            **self.common_inputs
        )
        
        # 결과 출력
        print(f"\n📊 시설 보너스 적용 전후 비교")
        print(f"  청년형: {result_청년_보너스_없음.demand_score}점 → {result_청년_보너스_있음.demand_score}점 (대학 800m)")
        print(f"  신혼형: {result_신혼_보너스_없음.demand_score}점 → {result_신혼_보너스_있음.demand_score}점 (초등학교 700m)")
        print(f"  고령자형: {result_고령자_보너스_없음.demand_score}점 → {result_고령자_보너스_있음.demand_score}점 (병원 1200m)")
        
        # 검증: 시설 보너스 적용 시 점수가 증가해야 함
        assert result_청년_보너스_있음.demand_score > result_청년_보너스_없음.demand_score, \
            "청년형 대학교 보너스 미적용"
        
        assert result_신혼_보너스_있음.demand_score > result_신혼_보너스_없음.demand_score, \
            "신혼형 학교 보너스 미적용"
        
        assert result_고령자_보너스_있음.demand_score > result_고령자_보너스_없음.demand_score, \
            "고령자형 병원 보너스 미적용"
        
        # 고령자 보너스(+25%)가 가장 커야 함
        청년_증가율 = (result_청년_보너스_있음.demand_score - result_청년_보너스_없음.demand_score) / result_청년_보너스_없음.demand_score
        신혼_증가율 = (result_신혼_보너스_있음.demand_score - result_신혼_보너스_없음.demand_score) / result_신혼_보너스_없음.demand_score
        고령자_증가율 = (result_고령자_보너스_있음.demand_score - result_고령자_보너스_없음.demand_score) / result_고령자_보너스_없음.demand_score
        
        print(f"  증가율: 청년 {청년_증가율*100:.1f}%, 신혼 {신혼_증가율*100:.1f}%, 고령자 {고령자_증가율*100:.1f}%")
        
        assert 고령자_증가율 > 청년_증가율, "고령자 보너스가 청년 보너스보다 작음 (설정 오류)"
        assert 고령자_증가율 > 신혼_증가율, "고령자 보너스가 신혼 보너스보다 작음 (설정 오류)"
        
        print("  ✅ 시설 보너스 적용 정상 확인!")
    
    def test_household_type_scores_모든_유형_포함(self):
        """
        DemandPredictionResult.household_type_scores에 청년/신혼/고령자 3가지 유형이 모두 포함되는지 확인
        """
        result = self.predictor.predict(
            unit_type="청년",
            nearby_facilities=None,
            **self.common_inputs
        )
        
        print(f"\n📊 household_type_scores: {result.household_type_scores}")
        
        # 검증: 3가지 유형 모두 존재해야 함
        assert result.household_type_scores is not None, "household_type_scores가 None"
        assert "청년" in result.household_type_scores, "청년형 점수 누락"
        assert "신혼" in result.household_type_scores, "신혼형 점수 누락"
        assert "고령자" in result.household_type_scores, "고령자형 점수 누락"
        
        # 3가지 점수가 모두 다른지 확인
        assert result.household_type_scores["청년"] != result.household_type_scores["신혼"], \
            "청년/신혼 점수 동일 (독립 계산 실패)"
        
        assert result.household_type_scores["청년"] != result.household_type_scores["고령자"], \
            "청년/고령자 점수 동일 (독립 계산 실패)"
        
        print("  ✅ household_type_scores 정상 확인!")


if __name__ == "__main__":
    """직접 실행 시 테스트 수행"""
    pytest.main([__file__, "-v", "-s"])
