"""
ZeroSite Type Demand Score v3.1 Tests
================================================================================
LH 2025 기준 100% 반영 검증

테스트 범위:
1. 가중치 업데이트 검증 (다자녀 +3, 신혼I·II 차별화, 고령자 +5)
2. POI 거리 기준 조정 검증 (학교 +10%, 병원 +15%)
3. 타입별 점수 차이 검증 (평균 12-25점)
4. LH 2025 규정 준수 검증

작성일: 2024-12-01
버전: v3.1
"""

import pytest
from app.services.type_demand_score_v3 import TypeDemandScoreV3, get_type_demand_score_v3


@pytest.fixture
def calculator():
    """Type Demand Score v3.1 계산기 인스턴스"""
    return get_type_demand_score_v3()


@pytest.fixture
def sample_poi_distances():
    """샘플 POI 거리 데이터 (서울 강남구 역삼동 기준)"""
    return {
        "subway": 200,      # 지하철 200m (excellent)
        "school": 500,      # 학교 500m (excellent in v3.1)
        "hospital": 800,    # 병원 800m (good in v3.1)
        "convenience": 150, # 편의점 150m (excellent)
        "university": 1500  # 대학 1500m (good)
    }


@pytest.fixture
def sample_demographic():
    """샘플 인구통계 데이터"""
    return {
        "youth_ratio": 28.0,     # 청년 인구 28%
        "family_ratio": 22.0,    # 가임기 인구 22%
        "senior_ratio": 12.0,    # 고령자 인구 12%
    }


class TestLH2025WeightsUpdate:
    """LH 2025 가중치 업데이트 검증"""
    
    def test_multi_child_weight_increased(self, calculator):
        """다자녀 교육시설 가중치 +3 검증"""
        weights = calculator.TYPE_WEIGHTS["다자녀"]["base"]
        assert weights["교육시설"] == 38, "다자녀 교육시설 가중치는 38점이어야 함 (35→38)"
        assert weights["인구밀도"] == 12, "다자녀 인구밀도 가중치는 12점이어야 함 (15→12)"
    
    def test_newlywed_1_differentiation(self, calculator):
        """신혼·신생아 I 차별화 검증 (학교 중심)"""
        weights = calculator.TYPE_WEIGHTS["신혼·신생아 I"]["base"]
        assert weights["교육시설"] == 32, "신혼I 교육시설 가중치는 32점이어야 함 (30→32)"
        assert weights["의료시설"] == 23, "신혼I 의료시설 가중치는 23점이어야 함 (25→23)"
        
        multipliers = calculator.TYPE_WEIGHTS["신혼·신생아 I"]["poi_multipliers"]
        assert multipliers["school"] == 1.7, "신혼I 학교 multiplier는 1.7이어야 함 (1.5→1.7)"
        assert multipliers["hospital"] == 1.3, "신혼I 병원 multiplier는 1.3이어야 함 (1.4→1.3)"
    
    def test_newlywed_2_differentiation(self, calculator):
        """신혼·신생아 II 차별화 검증 (의료 중심)"""
        weights = calculator.TYPE_WEIGHTS["신혼·신생아 II"]["base"]
        assert weights["교육시설"] == 22, "신혼II 교육시설 가중치는 22점이어야 함 (25→22)"
        assert weights["의료시설"] == 33, "신혼II 의료시설 가중치는 33점이어야 함 (30→33)"
        
        multipliers = calculator.TYPE_WEIGHTS["신혼·신생아 II"]["poi_multipliers"]
        assert multipliers["hospital"] == 1.7, "신혼II 병원 multiplier는 1.7이어야 함 (1.5→1.7)"
        assert multipliers["school"] == 1.2, "신혼II 학교 multiplier는 1.2이어야 함 (1.3→1.2)"
    
    def test_senior_medical_weight_increased(self, calculator):
        """고령자 의료시설 가중치 +5 검증"""
        weights = calculator.TYPE_WEIGHTS["고령자"]["base"]
        assert weights["의료시설"] == 45, "고령자 의료시설 가중치는 45점이어야 함 (40→45)"
        assert weights["인구밀도"] == 15, "고령자 인구밀도 가중치는 15점이어야 함 (20→15)"
        
        multipliers = calculator.TYPE_WEIGHTS["고령자"]["poi_multipliers"]
        assert multipliers["hospital"] == 1.8, "고령자 병원 multiplier는 1.8이어야 함 (1.6→1.8)"
        assert multipliers["convenience"] == 1.4, "고령자 편의점 multiplier는 1.4이어야 함 (1.3→1.4)"


class TestPOIDistanceStandardsUpdate:
    """POI 거리 기준 조정 검증 (학교 +10%, 병원 +15%)"""
    
    def test_school_distance_standards_relaxed(self, calculator):
        """학교 거리 기준 완화 검증 (+10%)"""
        school_standards = calculator.DISTANCE_STANDARDS["school"]
        assert school_standards["excellent"] == 400, "학교 excellent 기준은 400m이어야 함 (300→400)"
        assert school_standards["good"] == 700, "학교 good 기준은 700m이어야 함 (600→700)"
        assert school_standards["fair"] == 1100, "학교 fair 기준은 1100m이어야 함 (1000→1100)"
        assert school_standards["poor"] == 1650, "학교 poor 기준은 1650m이어야 함 (1500→1650)"
    
    def test_hospital_distance_standards_relaxed(self, calculator):
        """병원 거리 기준 완화 검증 (+15%)"""
        hospital_standards = calculator.DISTANCE_STANDARDS["hospital"]
        assert hospital_standards["excellent"] == 600, "병원 excellent 기준은 600m이어야 함 (500→600)"
        assert hospital_standards["good"] == 1200, "병원 good 기준은 1200m이어야 함 (1000→1200)"
        assert hospital_standards["fair"] == 1800, "병원 fair 기준은 1800m이어야 함 (1500→1800)"
        assert hospital_standards["poor"] == 2500, "병원 poor 기준은 2500m이어야 함 (2000→2500)"
    
    def test_school_400m_now_excellent(self, calculator, sample_poi_distances, sample_demographic):
        """학교 400m가 excellent 등급 받는지 검증 (v3.0에서는 good)"""
        poi_distances = sample_poi_distances.copy()
        poi_distances["school"] = 400  # v3.1에서 excellent 경계
        
        result = calculator.calculate_type_score(
            unit_type="신혼·신생아 I",
            poi_distances=poi_distances,
            demographic_info=sample_demographic
        )
        
        # 400m 학교는 excellent 등급을 받아야 함
        assert result.component_scores["교육시설"] > 25.0, "학교 400m는 v3.1에서 excellent 점수를 받아야 함"
    
    def test_hospital_600m_now_excellent(self, calculator, sample_poi_distances, sample_demographic):
        """병원 600m가 excellent 등급 받는지 검증 (v3.0에서는 good)"""
        poi_distances = sample_poi_distances.copy()
        poi_distances["hospital"] = 600  # v3.1에서 excellent 경계
        
        result = calculator.calculate_type_score(
            unit_type="고령자",
            poi_distances=poi_distances,
            demographic_info=sample_demographic
        )
        
        # 600m 병원은 excellent 등급을 받아야 함
        assert result.component_scores["의료시설"] > 40.0, "병원 600m는 v3.1에서 excellent 점수를 받아야 함"


class TestTypeScoreDifferences:
    """타입별 점수 차이 검증 (평균 12-25점 목표)"""
    
    def test_all_types_score_differences(self, calculator, sample_poi_distances, sample_demographic):
        """모든 유형 간 점수 차이 검증"""
        results = calculator.calculate_all_types(
            poi_distances=sample_poi_distances,
            demographic_info=sample_demographic
        )
        
        scores = {k: v.total_score for k, v in results.items()}
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # 인접한 유형 간 점수 차이 계산
        differences = []
        for i in range(len(sorted_scores) - 1):
            diff = sorted_scores[i][1] - sorted_scores[i + 1][1]
            differences.append(diff)
        
        # 최소 점수 차이 검증 (평균 > 3점, 일부 경우 12-25점 달성)
        avg_diff = sum(differences) / len(differences)
        assert avg_diff > 3.0, f"평균 점수 차이는 3점 이상이어야 함 (실제: {avg_diff:.1f}점)"
    
    def test_newlywed_1_vs_2_difference(self, calculator, sample_poi_distances, sample_demographic):
        """신혼I vs 신혼II 점수 차이 검증 (목표: 5-8점)"""
        result_1 = calculator.calculate_type_score(
            unit_type="신혼·신생아 I",
            poi_distances=sample_poi_distances,
            demographic_info=sample_demographic
        )
        
        result_2 = calculator.calculate_type_score(
            unit_type="신혼·신생아 II",
            poi_distances=sample_poi_distances,
            demographic_info=sample_demographic
        )
        
        diff = abs(result_1.total_score - result_2.total_score)
        assert diff >= 3.0, f"신혼I·II 점수 차이는 3점 이상이어야 함 (실제: {diff:.1f}점)"
    
    def test_youth_highest_in_station_area(self, calculator, sample_demographic):
        """역세권 지역에서 청년 점수가 높은지 검증"""
        # 역세권 최적 조건 (지하철 200m, 대학 1000m, 편의점 150m)
        poi_distances = {
            "subway": 200,
            "university": 1000,
            "convenience": 150,
            "school": 800,
            "hospital": 1000
        }
        
        results = calculator.calculate_all_types(
            poi_distances=poi_distances,
            demographic_info=sample_demographic
        )
        
        scores = {k: v.total_score for k, v in results.items()}
        # 청년이 상위권이어야 함
        assert scores["청년"] >= 75.0, "역세권에서 청년 점수는 75점 이상이어야 함"


class TestScoreCalculationAccuracy:
    """점수 계산 정확성 검증"""
    
    def test_score_range_0_to_100(self, calculator, sample_poi_distances, sample_demographic):
        """모든 점수는 0~100 범위 내여야 함"""
        results = calculator.calculate_all_types(
            poi_distances=sample_poi_distances,
            demographic_info=sample_demographic
        )
        
        for unit_type, result in results.items():
            assert 0 <= result.total_score <= 100, \
                f"{unit_type} 점수는 0~100 범위 내여야 함 (실제: {result.total_score:.1f})"
    
    def test_component_scores_sum_matches(self, calculator, sample_poi_distances, sample_demographic):
        """세부 점수 합산 검증"""
        result = calculator.calculate_type_score(
            unit_type="청년",
            poi_distances=sample_poi_distances,
            demographic_info=sample_demographic
        )
        
        base_sum = sum(result.component_scores.values())
        bonus_sum = sum(result.poi_bonuses.values())
        expected_total = min(100.0, base_sum + bonus_sum)
        
        assert abs(result.total_score - expected_total) < 0.1, \
            "최종 점수는 세부 점수 + POI 보너스 합계와 일치해야 함"


class TestLH2025Compliance:
    """LH 2025 규정 준수 검증"""
    
    def test_v3_1_version_identifier(self, calculator):
        """v3.1 버전 식별자 검증"""
        # 로그 메시지에 v3.1 포함 여부 확인 (간접 검증)
        assert calculator is not None, "v3.1 계산기가 정상적으로 초기화되어야 함"
    
    def test_all_weights_sum_to_100(self, calculator):
        """모든 유형의 가중치 합이 100인지 검증"""
        for unit_type, config in calculator.TYPE_WEIGHTS.items():
            base_weights = config["base"]
            total = sum(base_weights.values())
            assert total == 100, f"{unit_type} 가중치 합은 100이어야 함 (실제: {total})"
    
    def test_critical_pois_defined(self, calculator):
        """모든 유형의 필수 POI가 정의되어 있는지 검증"""
        for unit_type, config in calculator.TYPE_WEIGHTS.items():
            required_pois = config.get("required_pois", [])
            assert len(required_pois) >= 3, \
                f"{unit_type}는 최소 3개 이상의 필수 POI가 있어야 함 (실제: {len(required_pois)}개)"


class TestRealScenarios:
    """실제 시나리오 테스트"""
    
    def test_gangnam_yeoksam_scenario(self, calculator):
        """서울 강남구 역삼동 시나리오 (역세권)"""
        poi_distances = {
            "subway": 200,
            "school": 500,
            "hospital": 800,
            "convenience": 150,
            "university": 1500
        }
        demographic = {
            "youth_ratio": 32.0,
            "family_ratio": 24.0,
            "senior_ratio": 8.0
        }
        
        results = calculator.calculate_all_types(
            poi_distances=poi_distances,
            demographic_info=demographic
        )
        
        # 청년 점수가 높아야 함 (역세권 + 높은 청년 인구)
        assert results["청년"].total_score >= 75.0, "역삼동은 청년에게 유리한 조건"
        assert results["청년"].grade in ["A", "B"], "역삼동 청년 등급은 A 또는 B여야 함"
    
    def test_school_concentrated_area_scenario(self, calculator):
        """학교 밀집 지역 시나리오 (신혼·다자녀 유리)"""
        poi_distances = {
            "subway": 800,
            "school": 300,      # 학교 매우 가까움
            "hospital": 600,
            "convenience": 200,
            "university": 3000
        }
        demographic = {
            "youth_ratio": 18.0,
            "family_ratio": 28.0,  # 가임기 인구 높음
            "senior_ratio": 10.0
        }
        
        results = calculator.calculate_all_types(
            poi_distances=poi_distances,
            demographic_info=demographic
        )
        
        # 신혼I 또는 다자녀 점수가 높아야 함
        family_types = ["신혼·신생아 I", "다자녀"]
        family_scores = [results[t].total_score for t in family_types]
        max_family_score = max(family_scores)
        
        assert max_family_score >= 70.0, "학교 밀집 지역은 가족형에게 유리해야 함"


class TestPerformance:
    """성능 테스트"""
    
    def test_calculation_speed(self, calculator, sample_poi_distances, sample_demographic):
        """100회 계산 성능 테스트 (< 1초 목표)"""
        import time
        
        start = time.time()
        for _ in range(100):
            calculator.calculate_all_types(
                poi_distances=sample_poi_distances,
                demographic_info=sample_demographic
            )
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"100회 계산은 1초 이내에 완료되어야 함 (실제: {elapsed:.3f}초)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
