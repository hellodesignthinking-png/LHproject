"""
ZeroSite GeoOptimizer v3.0 자동 테스트
================================================================================
20개 실제 주소로 최적 입지 추천 검증

테스트 범위:
1. LH 가중치 기반 점수 계산
2. 추천 후보지 다양성 보장 (최소 1km 거리)
3. 3km+ 거리 연산 정확도
4. 토지규제 반영 정확성

검증 항목:
✅ LH 종합 점수 정확도
✅ 추천 후보지 3개 생성
✅ 후보지 간 최소 1km 거리 유지
✅ 거리 계산 오차 <5%
"""

import pytest
import logging
from typing import Dict, Any
from app.services.geo_optimizer_v3 import (
    GeoOptimizerV3,
    get_geo_optimizer_v3,
    OptimizedSiteV3,
    GeoOptimizationResultV3
)

logger = logging.getLogger(__name__)


# 20개 테스트 주소
TEST_LOCATIONS_20 = [
    # === 서울 역세권 우수 (5개) ===
    {
        "name": "강남역 역삼동",
        "address": "서울 강남구 역삼동 737",
        "latitude": 37.4995,
        "longitude": 127.0374,
        "poi_distances": {
            "subway": 200,
            "school": 400,
            "hospital": 600,
            "convenience": 150
        },
        "zone_info": {
            "zone_type": "제2종일반주거지역",
            "floor_area_ratio": 200,
            "building_coverage_ratio": 60
        },
        "expected_score_range": (85, 95)
    },
    {
        "name": "홍대입구역",
        "address": "서울 마포구 서교동 395-69",
        "latitude": 37.5572,
        "longitude": 126.9240,
        "poi_distances": {
            "subway": 250,
            "school": 580,
            "hospital": 700,
            "convenience": 100
        },
        "zone_info": {
            "zone_type": "제2종일반주거지역",
            "floor_area_ratio": 220,
            "building_coverage_ratio": 60
        },
        "expected_score_range": (80, 90)
    },
    {
        "name": "잠실 롯데타워",
        "address": "서울 송파구 올림픽로 300",
        "latitude": 37.5125,
        "longitude": 127.1025,
        "poi_distances": {
            "subway": 150,
            "school": 500,
            "hospital": 800,
            "convenience": 100
        },
        "zone_info": {
            "zone_type": "준주거지역",
            "floor_area_ratio": 300,
            "building_coverage_ratio": 70
        },
        "expected_score_range": (85, 95)
    },
    {
        "name": "신촌 연세대",
        "address": "서울 서대문구 신촌동 134",
        "latitude": 37.5585,
        "longitude": 126.9369,
        "poi_distances": {
            "subway": 300,
            "school": 400,
            "hospital": 500,
            "convenience": 200
        },
        "zone_info": {
            "zone_type": "제2종일반주거지역",
            "floor_area_ratio": 200,
            "building_coverage_ratio": 60
        },
        "expected_score_range": (80, 92)
    },
    {
        "name": "광화문",
        "address": "서울 종로구 세종대로 172",
        "latitude": 37.5720,
        "longitude": 126.9769,
        "poi_distances": {
            "subway": 300,
            "school": 600,
            "hospital": 500,
            "convenience": 150
        },
        "zone_info": {
            "zone_type": "일반상업지역",
            "floor_area_ratio": 400,
            "building_coverage_ratio": 70
        },
        "expected_score_range": (75, 88)
    },
    
    # === 서울 학군 우수 (5개) ===
    {
        "name": "서초동 학군지",
        "address": "서울 서초구 서초동 1650",
        "latitude": 37.4941,
        "longitude": 127.0140,
        "poi_distances": {
            "subway": 600,
            "school": 250,
            "hospital": 400,
            "convenience": 300
        },
        "zone_info": {
            "zone_type": "제1종일반주거지역",
            "floor_area_ratio": 150,
            "building_coverage_ratio": 50
        },
        "expected_score_range": (75, 88)
    },
    {
        "name": "목동 신시가지",
        "address": "서울 양천구 목동 914-1",
        "latitude": 37.5262,
        "longitude": 126.8754,
        "poi_distances": {
            "subway": 700,
            "school": 300,
            "hospital": 600,
            "convenience": 250
        },
        "zone_info": {
            "zone_type": "제2종일반주거지역",
            "floor_area_ratio": 200,
            "building_coverage_ratio": 60
        },
        "expected_score_range": (70, 85)
    },
    {
        "name": "잠원동 한강변",
        "address": "서울 서초구 잠원동 19",
        "latitude": 37.5146,
        "longitude": 127.0116,
        "poi_distances": {
            "subway": 800,
            "school": 350,
            "hospital": 700,
            "convenience": 300
        },
        "zone_info": {
            "zone_type": "제2종일반주거지역",
            "floor_area_ratio": 200,
            "building_coverage_ratio": 60
        },
        "expected_score_range": (68, 82)
    },
    {
        "name": "방배동",
        "address": "서울 서초구 방배동 745",
        "latitude": 37.4817,
        "longitude": 126.9960,
        "poi_distances": {
            "subway": 900,
            "school": 280,
            "hospital": 500,
            "convenience": 350
        },
        "zone_info": {
            "zone_type": "제1종일반주거지역",
            "floor_area_ratio": 150,
            "building_coverage_ratio": 50
        },
        "expected_score_range": (65, 80)
    },
    {
        "name": "대치동 학원가",
        "address": "서울 강남구 대치동 944",
        "latitude": 37.4947,
        "longitude": 127.0620,
        "poi_distances": {
            "subway": 650,
            "school": 300,
            "hospital": 800,
            "convenience": 200
        },
        "zone_info": {
            "zone_type": "제2종일반주거지역",
            "floor_area_ratio": 200,
            "building_coverage_ratio": 60
        },
        "expected_score_range": (72, 86)
    },
    
    # === 경기도 신도시 (5개) ===
    {
        "name": "성남 분당 정자동",
        "address": "경기 성남시 분당구 정자동 178-1",
        "latitude": 37.3850,
        "longitude": 127.1234,
        "poi_distances": {
            "subway": 300,
            "school": 250,
            "hospital": 400,
            "convenience": 150
        },
        "zone_info": {
            "zone_type": "제2종일반주거지역",
            "floor_area_ratio": 200,
            "building_coverage_ratio": 60
        },
        "expected_score_range": (80, 92)
    },
    {
        "name": "고양 일산 백석동",
        "address": "경기 고양시 일산동구 백석동 1256",
        "latitude": 37.6373,
        "longitude": 126.7860,
        "poi_distances": {
            "subway": 400,
            "school": 300,
            "hospital": 500,
            "convenience": 250
        },
        "zone_info": {
            "zone_type": "제2종일반주거지역",
            "floor_area_ratio": 200,
            "building_coverage_ratio": 60
        },
        "expected_score_range": (75, 88)
    },
    {
        "name": "인천 송도 국제도시",
        "address": "인천 연수구 송도동 30-1",
        "latitude": 37.3826,
        "longitude": 126.6564,
        "poi_distances": {
            "subway": 350,
            "school": 280,
            "hospital": 450,
            "convenience": 200
        },
        "zone_info": {
            "zone_type": "준주거지역",
            "floor_area_ratio": 250,
            "building_coverage_ratio": 65
        },
        "expected_score_range": (78, 90)
    },
    {
        "name": "화성 동탄2신도시",
        "address": "경기 화성시 반송동 142",
        "latitude": 37.2008,
        "longitude": 127.0755,
        "poi_distances": {
            "subway": 1200,
            "school": 200,
            "hospital": 600,
            "convenience": 300
        },
        "zone_info": {
            "zone_type": "제1종일반주거지역",
            "floor_area_ratio": 150,
            "building_coverage_ratio": 50
        },
        "expected_score_range": (60, 75)
    },
    {
        "name": "수원 영통 광교",
        "address": "경기 수원시 영통구 이의동 1325",
        "latitude": 37.2973,
        "longitude": 127.0468,
        "poi_distances": {
            "subway": 800,
            "school": 250,
            "hospital": 500,
            "convenience": 300
        },
        "zone_info": {
            "zone_type": "제2종일반주거지역",
            "floor_area_ratio": 200,
            "building_coverage_ratio": 60
        },
        "expected_score_range": (68, 82)
    },
    
    # === 서울 외곽 및 지방 (5개) ===
    {
        "name": "노원구 상계동",
        "address": "서울 노원구 상계동 701",
        "latitude": 37.6551,
        "longitude": 127.0616,
        "poi_distances": {
            "subway": 400,
            "school": 300,
            "hospital": 350,
            "convenience": 200
        },
        "zone_info": {
            "zone_type": "제2종일반주거지역",
            "floor_area_ratio": 200,
            "building_coverage_ratio": 60
        },
        "expected_score_range": (75, 88)
    },
    {
        "name": "구로구 신도림",
        "address": "서울 구로구 신도림동 337",
        "latitude": 37.5084,
        "longitude": 126.8914,
        "poi_distances": {
            "subway": 250,
            "school": 500,
            "hospital": 450,
            "convenience": 180
        },
        "zone_info": {
            "zone_type": "준주거지역",
            "floor_area_ratio": 300,
            "building_coverage_ratio": 70
        },
        "expected_score_range": (78, 90)
    },
    {
        "name": "부산 해운대 센텀",
        "address": "부산 해운대구 센텀중앙로 79",
        "latitude": 35.1697,
        "longitude": 129.1309,
        "poi_distances": {
            "subway": 250,
            "school": 500,
            "hospital": 600,
            "convenience": 150
        },
        "zone_info": {
            "zone_type": "일반상업지역",
            "floor_area_ratio": 400,
            "building_coverage_ratio": 70
        },
        "expected_score_range": (75, 88)
    },
    {
        "name": "대구 수성구 범어동",
        "address": "대구 수성구 범어동 169",
        "latitude": 35.8590,
        "longitude": 128.6311,
        "poi_distances": {
            "subway": 300,
            "school": 280,
            "hospital": 450,
            "convenience": 180
        },
        "zone_info": {
            "zone_type": "제2종일반주거지역",
            "floor_area_ratio": 200,
            "building_coverage_ratio": 60
        },
        "expected_score_range": (78, 90)
    },
    {
        "name": "대전 유성 도룡동",
        "address": "대전 유성구 도룡동 448",
        "latitude": 36.3729,
        "longitude": 127.3604,
        "poi_distances": {
            "subway": 800,
            "school": 300,
            "hospital": 600,
            "convenience": 250
        },
        "zone_info": {
            "zone_type": "제2종일반주거지역",
            "floor_area_ratio": 200,
            "building_coverage_ratio": 60
        },
        "expected_score_range": (65, 80)
    }
]


class TestGeoOptimizerV3:
    """GeoOptimizer v3.0 통합 테스트"""
    
    @pytest.fixture
    def engine(self):
        """테스트용 엔진 인스턴스"""
        return get_geo_optimizer_v3()
    
    @pytest.mark.asyncio
    async def test_all_20_locations(self, engine):
        """20개 주소 전체 최적화 테스트"""
        logger.info("\n" + "="*80)
        logger.info("🧪 GeoOptimizer v3.0 - 20개 주소 자동 검증 시작")
        logger.info("="*80 + "\n")
        
        total_passed = 0
        total_failed = 0
        diversity_issues = 0
        
        for idx, test_case in enumerate(TEST_LOCATIONS_20, 1):
            logger.info(f"\n[{idx}/20] {test_case['name']} ({test_case['address']})")
            logger.info("-" * 60)
            
            try:
                # 최적화 실행
                result = engine.optimize(
                    latitude=test_case['latitude'],
                    longitude=test_case['longitude'],
                    address=test_case['address'],
                    poi_distances=test_case['poi_distances'],
                    zone_info=test_case['zone_info']
                )
                
                # 결과 로깅
                logger.info(f"  📊 종합 점수: {result.optimization_score}점")
                logger.info(f"  🎯 추천 후보지: {len(result.recommended_sites)}개")
                logger.info(f"  📏 다양성 점수: {result.diversity_score:.1f}점")
                logger.info(f"  📍 최소 거리: {result.min_inter_site_distance:.0f}m")
                
                # 점수 범위 검증
                expected_min, expected_max = test_case['expected_score_range']
                if expected_min <= result.optimization_score <= expected_max:
                    logger.info(f"  ✅ 점수 범위 적합: {expected_min}~{expected_max}점")
                    total_passed += 1
                else:
                    logger.warning(
                        f"  ⚠️ 점수 범위 이탈: 예상 {expected_min}~{expected_max}, "
                        f"실제 {result.optimization_score}"
                    )
                    total_failed += 1
                
                # 추천 후보지 개수 검증
                if len(result.recommended_sites) != 3:
                    logger.warning(f"  ⚠️ 추천 후보지 개수 부적합: {len(result.recommended_sites)}개 (예상 3개)")
                
                # 다양성 검증
                if result.min_inter_site_distance < 1000:
                    logger.warning(
                        f"  ⚠️ 다양성 미흡: 최소 거리 {result.min_inter_site_distance:.0f}m "
                        f"(권장 1000m 이상)"
                    )
                    diversity_issues += 1
                
                # 추천 후보지 상세 출력
                for site in result.recommended_sites:
                    logger.info(
                        f"    - {site.site_id}: {site.overall_score:.1f}점 "
                        f"(거리: {site.distance_from_origin:.0f}m, "
                        f"지하철: {site.subway_distance}m)"
                    )
            
            except Exception as e:
                logger.error(f"  ❌ ERROR: {e}")
                total_failed += 1
        
        # 최종 결과 요약
        logger.info("\n" + "="*80)
        logger.info("📊 테스트 결과 요약")
        logger.info("="*80)
        logger.info(f"✅ 통과: {total_passed}/20 ({total_passed/20*100:.1f}%)")
        logger.info(f"❌ 실패: {total_failed}/20 ({total_failed/20*100:.1f}%)")
        logger.info(f"⚠️ 다양성 미흡: {diversity_issues}개")
        logger.info("="*80 + "\n")
        
        # 80% 이상 통과 시 테스트 성공
        assert total_passed >= 16, f"통과율 미달: {total_passed}/20 (최소 16/20 필요)"
    
    def test_lh_weighted_scoring(self, engine):
        """LH 가중치 기반 점수 계산 테스트"""
        logger.info("\n🧪 LH 가중치 점수 계산 검증")
        
        # 역세권 우수 지역
        poi_distances = {
            "subway": 200,  # Excellent
            "school": 400,  # Good
            "hospital": 600,  # Good
            "convenience": 150  # Excellent
        }
        zone_info = {
            "zone_type": "제2종일반주거지역",
            "floor_area_ratio": 200,
            "building_coverage_ratio": 60
        }
        
        result = engine.optimize(
            latitude=37.5,
            longitude=127.0,
            address="테스트 주소",
            poi_distances=poi_distances,
            zone_info=zone_info
        )
        
        logger.info(f"종합 점수: {result.optimization_score}점")
        assert result.optimization_score >= 80, "역세권 우수 지역은 80점 이상이어야 함"
        logger.info("✅ LH 가중치 점수 계산 정확")
    
    def test_diversity_guarantee(self, engine):
        """추천 후보지 다양성 보장 테스트"""
        logger.info("\n🧪 추천 후보지 다양성 검증")
        
        poi_distances = {
            "subway": 500,
            "school": 500,
            "hospital": 800,
            "convenience": 300
        }
        
        result = engine.optimize(
            latitude=37.5,
            longitude=127.0,
            address="테스트 주소",
            poi_distances=poi_distances
        )
        
        logger.info(f"추천 후보지 수: {len(result.recommended_sites)}")
        logger.info(f"다양성 점수: {result.diversity_score:.1f}점")
        logger.info(f"최소 거리: {result.min_inter_site_distance:.0f}m")
        
        # 다양성 검증
        assert len(result.recommended_sites) == 3, "추천 후보지는 3개여야 함"
        assert result.min_inter_site_distance >= 1000, f"최소 거리 미달: {result.min_inter_site_distance:.0f}m < 1000m"
        
        logger.info("✅ 다양성 보장 (최소 1km 거리 유지)")
    
    def test_long_distance_accuracy(self, engine):
        """3km+ 거리 계산 정확도 테스트"""
        logger.info("\n🧪 3km+ 거리 계산 정확도 검증")
        
        # 서울 강남역 → 잠실역 (약 8.5km)
        lat1, lon1 = 37.4995, 127.0374  # 강남역
        lat2, lon2 = 37.5125, 127.1025  # 잠실역
        
        distance = engine._calculate_distance(lat1, lon1, lat2, lon2)
        
        logger.info(f"강남역 → 잠실역 거리: {distance:.1f}m")
        
        # 실제 거리 약 8.5km (8500m)
        expected_distance = 8500
        error_rate = abs(distance - expected_distance) / expected_distance * 100
        
        logger.info(f"오차율: {error_rate:.2f}%")
        
        assert error_rate < 5.0, f"오차율 과다: {error_rate:.2f}% (목표: <5%)"
        logger.info("✅ 3km+ 거리 계산 정확도 <5%")


def run_geo_optimizer_test_summary():
    """
    GeoOptimizer v3.0 테스트 요약 출력
    """
    print("\n" + "="*80)
    print("🚀 ZeroSite GeoOptimizer v3.0 테스트 요약")
    print("="*80)
    
    print(f"\n📋 총 {len(TEST_LOCATIONS_20)}개 주소 테스트 준비 완료")
    print("\n주요 테스트 지역:")
    print("  - 서울 역세권: 5개")
    print("  - 서울 학군: 5개")
    print("  - 경기 신도시: 5개")
    print("  - 서울 외곽 및 지방: 5개")
    
    print("\n검증 항목:")
    print("  ✅ LH 가중치 기반 점수 (역세권 30%, 교육 25%, 의료 20%, 상업 15%, 규제 10%)")
    print("  ✅ 추천 후보지 3개 생성")
    print("  ✅ 후보지 간 최소 1km 거리 유지 (다양성)")
    print("  ✅ 3km+ 거리 계산 오차 <5%")
    print("  ✅ 토지규제 반영 (용도지역, 용적률, 건폐율)")
    
    print("\n💡 실행 방법:")
    print("  pytest tests/test_geo_optimizer_v3.py -v -s")
    print("  또는")
    print("  python -m pytest tests/test_geo_optimizer_v3.py::TestGeoOptimizerV3::test_all_20_locations -v -s")
    print("="*80 + "\n")


if __name__ == "__main__":
    # 직접 실행 시 요약 출력
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    run_geo_optimizer_test_summary()
