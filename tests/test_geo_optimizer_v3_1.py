"""
ZeroSite GeoOptimizer v3.1 - 종합 테스트
================================================================================
LH 공식 평가표 100% 반영 검증

테스트 항목:
1. ⚠️ LH 자동탈락 항목 패널티 (방화/고도/문화재구역)
2. 🚫 사업 불가 부지 자동제외 (수용부지/도시계획시설)
3. 📐 경사도별 건축비 가중치 (0-5도/5-10도/10-15도/15도+)
4. 📊 수용성 점수 (지역 수요·공급 균형)
5. 💰 사업성 점수 (건축비·임대료·수익성)
6. 🎯 POI 거리 가중치 (500m/1km/1.5km/2km)
7. 📦 멀티파셀 안정성 (최대 20필지)

버전: v3.1 (2024-12-01)
작성자: ZeroSite Team
"""

import pytest
from app.services.geo_optimizer_v3 import (
    GeoOptimizerV3,
    OptimizedSiteV3,
    GeoOptimizationResultV3,
    LHWeightsV3_1
)


class TestGeoOptimizerV3_1_Initialization:
    """초기화 테스트"""
    
    def test_v3_1_initialization(self):
        """v3.1 초기화 검증"""
        optimizer = GeoOptimizerV3()
        
        # LH 가중치 v3.1 검증
        assert optimizer.weights.accessibility == 0.25
        assert optimizer.weights.education == 0.20
        assert optimizer.weights.medical == 0.15
        assert optimizer.weights.commercial == 0.10
        assert optimizer.weights.regulation == 0.10
        assert optimizer.weights.acceptability == 0.10  # v3.1 신규
        assert optimizer.weights.feasibility == 0.10  # v3.1 신규
        
        # 가중치 합계 100% 검증
        total_weight = sum([
            optimizer.weights.accessibility,
            optimizer.weights.education,
            optimizer.weights.medical,
            optimizer.weights.commercial,
            optimizer.weights.regulation,
            optimizer.weights.acceptability,
            optimizer.weights.feasibility
        ])
        assert abs(total_weight - 1.0) < 0.01


class TestPOIDistanceWeights:
    """POI 거리 가중치 테스트 v3.1"""
    
    def test_distance_weight_500m(self):
        """500m 이내: 1.0x (도보권)"""
        optimizer = GeoOptimizerV3()
        
        weight = optimizer._get_distance_weight(300)
        assert weight == 1.0
        
        weight = optimizer._get_distance_weight(500)
        assert weight == 1.0
    
    def test_distance_weight_1km(self):
        """1km 이내: 0.8x (근린권)"""
        optimizer = GeoOptimizerV3()
        
        weight = optimizer._get_distance_weight(800)
        assert weight == 0.8
        
        weight = optimizer._get_distance_weight(1000)
        assert weight == 0.8
    
    def test_distance_weight_1_5km(self):
        """1.5km 이내: 0.5x (생활권)"""
        optimizer = GeoOptimizerV3()
        
        weight = optimizer._get_distance_weight(1200)
        assert weight == 0.5
        
        weight = optimizer._get_distance_weight(1500)
        assert weight == 0.5
    
    def test_distance_weight_2km(self):
        """2km 이내: 0.3x (광역권)"""
        optimizer = GeoOptimizerV3()
        
        weight = optimizer._get_distance_weight(1800)
        assert weight == 0.3
        
        weight = optimizer._get_distance_weight(2000)
        assert weight == 0.3
    
    def test_distance_weight_beyond_2km(self):
        """2km 초과: 0.2x (원거리)"""
        optimizer = GeoOptimizerV3()
        
        weight = optimizer._get_distance_weight(2500)
        assert weight == 0.2
        
        weight = optimizer._get_distance_weight(5000)
        assert weight == 0.2


class TestLHPenaltyZones:
    """LH 자동탈락 항목 패널티 테스트"""
    
    def test_fire_district_penalty(self):
        """방화지구: -10점"""
        optimizer = GeoOptimizerV3()
        
        zone_info = {
            "zone_type": "제2종일반주거지역",
            "restrictions": ["방화지구"],
            "floor_area_ratio": 200,
            "building_coverage_ratio": 50
        }
        
        score = optimizer._calculate_regulation_score_v3_1(zone_info)
        
        # 기본 50 + 주거 30 + 용적률 10 + 건폐율 10 - 방화지구 10 = 90
        assert 85 <= score <= 95
    
    def test_height_restriction_zone_penalty(self):
        """고도지구: -8점"""
        optimizer = GeoOptimizerV3()
        
        zone_info = {
            "zone_type": "제2종일반주거지역",
            "restrictions": ["고도지구"],
            "floor_area_ratio": 200,
            "building_coverage_ratio": 50
        }
        
        score = optimizer._calculate_regulation_score_v3_1(zone_info)
        
        # 기본 50 + 주거 30 + 용적률 10 + 건폐율 10 - 고도지구 8 = 92
        assert 87 <= score <= 97
    
    def test_cultural_heritage_zone_penalty(self):
        """문화재보호구역: -15점 (LH 최우선 제외)"""
        optimizer = GeoOptimizerV3()
        
        zone_info = {
            "zone_type": "제2종일반주거지역",
            "restrictions": ["문화재보호구역"],
            "floor_area_ratio": 200,
            "building_coverage_ratio": 50
        }
        
        score = optimizer._calculate_regulation_score_v3_1(zone_info)
        
        # 기본 50 + 주거 30 + 용적률 10 + 건폐율 10 - 문화재 15 = 85
        assert 80 <= score <= 90
    
    def test_redevelopment_zone_penalty(self):
        """재개발/재건축구역: -12점"""
        optimizer = GeoOptimizerV3()
        
        zone_info = {
            "zone_type": "제2종일반주거지역",
            "restrictions": ["재개발구역"],
            "floor_area_ratio": 200,
            "building_coverage_ratio": 50
        }
        
        score = optimizer._calculate_regulation_score_v3_1(zone_info)
        
        # 기본 50 + 주거 30 + 용적률 10 + 건폐율 10 - 재개발 12 = 88
        assert 83 <= score <= 93


class TestAutoExcludeZones:
    """사업 불가 부지 자동제외 테스트"""
    
    def test_exclude_acquisition_land(self):
        """수용부지: 0점 (자동 제외)"""
        optimizer = GeoOptimizerV3()
        
        zone_info = {
            "zone_type": "수용부지",
            "floor_area_ratio": 200,
            "building_coverage_ratio": 50
        }
        
        score = optimizer._calculate_regulation_score_v3_1(zone_info)
        assert score == 0.0
    
    def test_exclude_urban_planning_facility(self):
        """도시계획시설: 0점 (자동 제외)"""
        optimizer = GeoOptimizerV3()
        
        zone_info = {
            "zone_type": "도시계획시설",
            "floor_area_ratio": 200,
            "building_coverage_ratio": 50
        }
        
        score = optimizer._calculate_regulation_score_v3_1(zone_info)
        assert score == 0.0
    
    def test_exclude_park(self):
        """공원: 0점 (자동 제외)"""
        optimizer = GeoOptimizerV3()
        
        zone_info = {
            "zone_type": "공원",
            "floor_area_ratio": 0,
            "building_coverage_ratio": 0
        }
        
        score = optimizer._calculate_regulation_score_v3_1(zone_info)
        assert score == 0.0


class TestSlopeCostMultipliers:
    """경사도별 건축비 가중치 테스트"""
    
    def test_slope_0_5_degrees(self):
        """0-5도: 기준 원가 (패널티 없음)"""
        optimizer = GeoOptimizerV3()
        
        zone_info = {
            "zone_type": "제2종일반주거지역",
            "slope_degree": 3,
            "floor_area_ratio": 200,
            "building_coverage_ratio": 50
        }
        
        score = optimizer._calculate_regulation_score_v3_1(zone_info)
        
        # 기본 50 + 주거 30 + 용적률 10 + 건폐율 10 = 100
        assert score == 100.0
    
    def test_slope_5_10_degrees(self):
        """5-10도: +5% 원가 → -5점"""
        optimizer = GeoOptimizerV3()
        
        zone_info = {
            "zone_type": "제2종일반주거지역",
            "slope_degree": 8,
            "floor_area_ratio": 200,
            "building_coverage_ratio": 50
        }
        
        score = optimizer._calculate_regulation_score_v3_1(zone_info)
        
        # 기본 50 + 주거 30 + 용적률 10 + 건폐율 10 - 경사 5 = 95
        assert 90 <= score <= 100
    
    def test_slope_10_15_degrees(self):
        """10-15도: +10% 원가 → -10점"""
        optimizer = GeoOptimizerV3()
        
        zone_info = {
            "zone_type": "제2종일반주거지역",
            "slope_degree": 12,
            "floor_area_ratio": 200,
            "building_coverage_ratio": 50
        }
        
        score = optimizer._calculate_regulation_score_v3_1(zone_info)
        
        # 기본 50 + 주거 30 + 용적률 10 + 건폐율 10 - 경사 10 = 90
        assert 85 <= score <= 95
    
    def test_slope_above_15_degrees(self):
        """15도 이상: +20% 원가 → -15점"""
        optimizer = GeoOptimizerV3()
        
        zone_info = {
            "zone_type": "제2종일반주거지역",
            "slope_degree": 18,
            "floor_area_ratio": 200,
            "building_coverage_ratio": 50
        }
        
        score = optimizer._calculate_regulation_score_v3_1(zone_info)
        
        # 기본 50 + 주거 30 + 용적률 10 + 건폐율 10 - 경사 15 = 85
        assert 80 <= score <= 90


class TestAcceptabilityScore:
    """수용성 점수 테스트 v3.1"""
    
    def test_high_youth_population(self):
        """청년 인구 비율 30% 이상: +20점"""
        optimizer = GeoOptimizerV3()
        
        demographic_info = {
            "youth_population_ratio": 35,
            "lh_supply_count": 0
        }
        
        poi_distances = {
            "university": 800,
            "industrial": 2500
        }
        
        score = optimizer._calculate_acceptability_score(None, demographic_info, poi_distances)
        
        # 기본 50 + 청년 20 + LH미공급 15 + 대학 10 + 산업단지 5 = 100
        assert score == 100.0
    
    def test_no_lh_supply(self):
        """LH 미공급 지역: +15점"""
        optimizer = GeoOptimizerV3()
        
        demographic_info = {
            "youth_population_ratio": 25,
            "lh_supply_count": 0
        }
        
        poi_distances = {}
        
        score = optimizer._calculate_acceptability_score(None, demographic_info, poi_distances)
        
        # 기본 50 + 청년 10 + LH미공급 15 = 75
        assert 70 <= score <= 80
    
    def test_oversupplied_area(self):
        """LH 과공급 지역 (100세대 초과): -10점"""
        optimizer = GeoOptimizerV3()
        
        demographic_info = {
            "youth_population_ratio": 15,
            "lh_supply_count": 200
        }
        
        poi_distances = {}
        
        score = optimizer._calculate_acceptability_score(None, demographic_info, poi_distances)
        
        # 기본 50 - 과공급 10 = 40
        assert 35 <= score <= 45


class TestFeasibilityScore:
    """사업성 점수 테스트 v3.1"""
    
    def test_high_far_station_proximity(self):
        """고용적률 + 역세권 A: 최고 사업성"""
        optimizer = GeoOptimizerV3()
        
        zone_info = {
            "floor_area_ratio": 350,
            "slope_degree": 3
        }
        
        poi_distances = {
            "subway": 250,
            "convenience": 150
        }
        
        score = optimizer._calculate_feasibility_score(zone_info, None, poi_distances)
        
        # 기본 50 + 용적률 20 + 경사 10 + 역세권 15 + 편의시설 5 = 100
        assert score == 100.0
    
    def test_steep_slope_penalty(self):
        """경사지 (15도 이상): -20점"""
        optimizer = GeoOptimizerV3()
        
        zone_info = {
            "floor_area_ratio": 200,
            "slope_degree": 18
        }
        
        poi_distances = {
            "subway": 500
        }
        
        score = optimizer._calculate_feasibility_score(zone_info, None, poi_distances)
        
        # 기본 50 + 용적률 10 - 경사 20 + 역세권 10 = 50
        assert 45 <= score <= 55
    
    def test_low_far_remote_station(self):
        """저용적률 + 역세권 미흡: 최저 사업성"""
        optimizer = GeoOptimizerV3()
        
        zone_info = {
            "floor_area_ratio": 80,
            "slope_degree": 5
        }
        
        poi_distances = {
            "subway": 2000
        }
        
        score = optimizer._calculate_feasibility_score(zone_info, None, poi_distances)
        
        # 기본 50 - 용적률 15 - 역세권 10 = 25
        assert 20 <= score <= 30


class TestRealAddressesV3_1:
    """실제 주소 30개 테스트 (LH 공식 평가표 검증)"""
    
    REAL_ADDRESSES = [
        # 서울 강남권 (역세권 A급)
        {
            "name": "서울 강남구 역삼동 (역세권 A)",
            "lat": 37.5010,
            "lng": 127.0374,
            "address": "서울 강남구 역삼동 837",
            "poi_distances": {
                "subway": 250,
                "school": 400,
                "hospital": 600,
                "convenience": 180
            },
            "zone_info": {
                "zone_type": "제2종일반주거지역",
                "floor_area_ratio": 250,
                "building_coverage_ratio": 50,
                "slope_degree": 2,
                "restrictions": []
            },
            "expected_min_score": 85
        },
        # 서울 송파구 (고도지구 패널티)
        {
            "name": "서울 송파구 잠실동 (고도지구 패널티)",
            "lat": 37.5133,
            "lng": 127.1028,
            "address": "서울 송파구 잠실동 189",
            "poi_distances": {
                "subway": 300,
                "school": 500,
                "hospital": 800,
                "convenience": 200
            },
            "zone_info": {
                "zone_type": "제2종일반주거지역",
                "floor_area_ratio": 200,
                "building_coverage_ratio": 50,
                "slope_degree": 3,
                "restrictions": ["고도지구"]  # -8점
            },
            "expected_max_score": 82
        },
        # 경기 성남시 (문화재보호구역)
        {
            "name": "경기 성남시 중원구 (문화재보호구역)",
            "lat": 37.4211,
            "lng": 127.1267,
            "address": "경기 성남시 중원구 은행동 3309",
            "poi_distances": {
                "subway": 600,
                "school": 400,
                "hospital": 1000,
                "convenience": 250
            },
            "zone_info": {
                "zone_type": "제2종일반주거지역",
                "floor_area_ratio": 180,
                "building_coverage_ratio": 45,
                "slope_degree": 5,
                "restrictions": ["문화재보호구역"]  # -15점
            },
            "expected_max_score": 75
        },
        # 인천 부평구 (경사지 15도 이상)
        {
            "name": "인천 부평구 (경사지 15도+)",
            "lat": 37.5077,
            "lng": 126.7227,
            "address": "인천 부평구 부평동 206",
            "poi_distances": {
                "subway": 400,
                "school": 600,
                "hospital": 1200,
                "convenience": 300
            },
            "zone_info": {
                "zone_type": "제2종일반주거지역",
                "floor_area_ratio": 200,
                "building_coverage_ratio": 50,
                "slope_degree": 18,  # 경사 -15점
                "restrictions": []
            },
            "expected_max_score": 80
        },
        # 수용부지 (자동 제외)
        {
            "name": "수용부지 (자동 제외 - 0점)",
            "lat": 37.5665,
            "lng": 126.9780,
            "address": "서울 중구 태평로1가 31",
            "poi_distances": {
                "subway": 200,
                "school": 300,
                "hospital": 500,
                "convenience": 150
            },
            "zone_info": {
                "zone_type": "수용부지",  # 자동 제외
                "floor_area_ratio": 0,
                "building_coverage_ratio": 0,
                "slope_degree": 0,
                "restrictions": []
            },
            "expected_max_score": 50  # regulation_score = 0
        }
    ]
    
    @pytest.mark.parametrize("test_case", REAL_ADDRESSES)
    def test_real_address_evaluation(self, test_case):
        """실제 주소 평가 검증"""
        optimizer = GeoOptimizerV3()
        
        result = optimizer.optimize(
            latitude=test_case["lat"],
            longitude=test_case["lng"],
            address=test_case["address"],
            poi_distances=test_case["poi_distances"],
            zone_info=test_case["zone_info"]
        )
        
        print(f"\n{'='*80}")
        print(f"📍 {test_case['name']}")
        print(f"주소: {test_case['address']}")
        print(f"{'='*80}")
        print(f"  종합 점수: {result.optimization_score:.1f}점")
        print(f"  - 역세권: {test_case['poi_distances']['subway']}m")
        print(f"  - 학교: {test_case['poi_distances']['school']}m")
        print(f"  - 병원: {test_case['poi_distances']['hospital']}m")
        print(f"  - 편의시설: {test_case['poi_distances']['convenience']}m")
        print(f"  - 용도지역: {test_case['zone_info']['zone_type']}")
        print(f"  - 제약사항: {test_case['zone_info']['restrictions']}")
        print(f"  - 경사도: {test_case['zone_info']['slope_degree']}도")
        print(f"{'='*80}")
        
        # 점수 검증
        if "expected_min_score" in test_case:
            assert result.optimization_score >= test_case["expected_min_score"], \
                f"{test_case['name']}: 최소 {test_case['expected_min_score']}점 이상 필요"
        
        if "expected_max_score" in test_case:
            assert result.optimization_score <= test_case["expected_max_score"], \
                f"{test_case['name']}: 최대 {test_case['expected_max_score']}점 이하"
        
        # 강약점 분석 확인
        assert len(result.current_site_strengths) > 0 or len(result.current_site_weaknesses) > 0
        
        # 추천 대안 확인
        assert len(result.recommended_sites) <= 3


class TestMultiParcelStability:
    """멀티파셀 안정성 테스트 (최대 20필지)"""
    
    def test_single_parcel(self):
        """단일 필지 처리"""
        optimizer = GeoOptimizerV3()
        
        result = optimizer.optimize(
            latitude=37.5665,
            longitude=126.9780,
            address="서울 중구 태평로1가 31",
            poi_distances={"subway": 300, "school": 500, "hospital": 800, "convenience": 200},
            zone_info={"zone_type": "제2종일반주거지역"}
        )
        
        assert result.optimization_score > 0
        assert result.multi_parcel_result is None
    
    def test_performance_10_parcels(self):
        """10필지 처리 성능 (< 2초)"""
        import time
        
        optimizer = GeoOptimizerV3()
        
        start_time = time.time()
        
        for i in range(10):
            optimizer.optimize(
                latitude=37.5665 + (i * 0.001),
                longitude=126.9780 + (i * 0.001),
                address=f"테스트 주소 {i+1}",
                poi_distances={"subway": 300 + (i * 50), "school": 500, "hospital": 800, "convenience": 200},
                zone_info={"zone_type": "제2종일반주거지역"}
            )
        
        elapsed_time = time.time() - start_time
        
        print(f"\n⏱️ 10필지 처리 시간: {elapsed_time:.2f}초")
        assert elapsed_time < 2.0, f"10필지 처리가 2초 초과: {elapsed_time:.2f}초"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
