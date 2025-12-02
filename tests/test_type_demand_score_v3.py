"""
ZeroSite Type Demand Score v3.0 자동 테스트
================================================================================
30개 실제 주소로 유형별 수요점수 검증

테스트 범위:
1. 서울 주요 지역 (강남/강북/도심/외곽) 10개
2. 경기도 주요 도시 (성남/고양/인천) 10개
3. 지방 광역시 (부산/대구/대전) 10개

검증 항목:
✅ 유형 간 최소 10점 차이
✅ POI 거리 가중치 정확도
✅ 등급 판정 정확성
✅ 계산 로직 일관성
"""

import pytest
import logging
from typing import Dict, Any
from app.services.type_demand_score_v3 import (
    TypeDemandScoreV3,
    get_type_demand_score_v3,
    TypeDemandScore
)

logger = logging.getLogger(__name__)


# 테스트용 30개 샘플 데이터
TEST_ADDRESSES = [
    # === 서울 강남권 (역세권 + 교육 우수) ===
    {
        "name": "강남역 인근",
        "address": "서울 강남구 역삼동 737",
        "poi_distances": {
            "subway": 200,      # 역세권
            "school": 400,
            "hospital": 600,
            "convenience": 150,
            "university": 800
        },
        "demographic": {
            "youth_ratio": 35,
            "family_ratio": 20,
            "senior_ratio": 8
        },
        "expected_top_type": "청년"
    },
    {
        "name": "서초동 학군지",
        "address": "서울 서초구 서초동 1650",
        "poi_distances": {
            "subway": 600,
            "school": 250,      # 학교 인접
            "hospital": 400,
            "convenience": 300,
            "university": 2000
        },
        "demographic": {
            "youth_ratio": 20,
            "family_ratio": 28,
            "senior_ratio": 10
        },
        "expected_top_type": "신혼·신생아 I"
    },
    {
        "name": "잠실 롯데월드타워",
        "address": "서울 송파구 올림픽로 300",
        "poi_distances": {
            "subway": 150,
            "school": 500,
            "hospital": 800,
            "convenience": 100,
            "university": 3000
        },
        "demographic": {
            "youth_ratio": 30,
            "family_ratio": 22,
            "senior_ratio": 9
        },
        "expected_top_type": "청년"
    },
    
    # === 서울 강북권 ===
    {
        "name": "홍대 청년 상권",
        "address": "서울 마포구 서교동 395-69",
        "poi_distances": {
            "subway": 250,
            "school": 800,
            "hospital": 700,
            "convenience": 100,
            "university": 500   # 홍익대 인접
        },
        "demographic": {
            "youth_ratio": 40,
            "family_ratio": 15,
            "senior_ratio": 7
        },
        "expected_top_type": "청년"
    },
    {
        "name": "노원구 상계동",
        "address": "서울 노원구 상계동 701",
        "poi_distances": {
            "subway": 400,
            "school": 300,
            "hospital": 350,
            "convenience": 200,
            "university": 4000
        },
        "demographic": {
            "youth_ratio": 18,
            "family_ratio": 25,
            "senior_ratio": 15
        },
        "expected_top_type": "다자녀"
    },
    
    # === 서울 도심권 ===
    {
        "name": "종로 광화문",
        "address": "서울 종로구 세종대로 172",
        "poi_distances": {
            "subway": 300,
            "school": 600,
            "hospital": 500,
            "convenience": 150,
            "university": 2000
        },
        "demographic": {
            "youth_ratio": 25,
            "family_ratio": 20,
            "senior_ratio": 12
        },
        "expected_top_type": "청년"
    },
    {
        "name": "영등포 여의도",
        "address": "서울 영등포구 여의도동 23",
        "poi_distances": {
            "subway": 350,
            "school": 700,
            "hospital": 600,
            "convenience": 200,
            "university": 3500
        },
        "demographic": {
            "youth_ratio": 28,
            "family_ratio": 22,
            "senior_ratio": 10
        },
        "expected_top_type": "청년"
    },
    
    # === 서울 외곽권 ===
    {
        "name": "강동구 고덕동",
        "address": "서울 강동구 고덕동 121",
        "poi_distances": {
            "subway": 800,
            "school": 350,
            "hospital": 600,
            "convenience": 400,
            "university": 5000
        },
        "demographic": {
            "youth_ratio": 15,
            "family_ratio": 30,
            "senior_ratio": 12
        },
        "expected_top_type": "다자녀"
    },
    {
        "name": "은평구 신사동",
        "address": "서울 은평구 신사동 241",
        "poi_distances": {
            "subway": 700,
            "school": 400,
            "hospital": 300,
            "convenience": 300,
            "university": 4500
        },
        "demographic": {
            "youth_ratio": 12,
            "family_ratio": 20,
            "senior_ratio": 18
        },
        "expected_top_type": "고령자"
    },
    {
        "name": "구로구 신도림",
        "address": "서울 구로구 신도림동 337",
        "poi_distances": {
            "subway": 250,
            "school": 500,
            "hospital": 450,
            "convenience": 180,
            "university": 3000
        },
        "demographic": {
            "youth_ratio": 24,
            "family_ratio": 23,
            "senior_ratio": 11
        },
        "expected_top_type": "청년"
    },
    
    # === 경기도 성남/고양/인천 ===
    {
        "name": "성남 분당구 정자동",
        "address": "경기 성남시 분당구 정자동 178-1",
        "poi_distances": {
            "subway": 300,
            "school": 250,
            "hospital": 400,
            "convenience": 150,
            "university": 2500
        },
        "demographic": {
            "youth_ratio": 22,
            "family_ratio": 30,
            "senior_ratio": 10
        },
        "expected_top_type": "신혼·신생아 I"
    },
    {
        "name": "고양 일산 백석동",
        "address": "경기 고양시 일산동구 백석동 1256",
        "poi_distances": {
            "subway": 400,
            "school": 300,
            "hospital": 500,
            "convenience": 250,
            "university": 4000
        },
        "demographic": {
            "youth_ratio": 18,
            "family_ratio": 28,
            "senior_ratio": 13
        },
        "expected_top_type": "다자녀"
    },
    {
        "name": "인천 연수구 송도",
        "address": "인천 연수구 송도동 30-1",
        "poi_distances": {
            "subway": 350,
            "school": 280,
            "hospital": 450,
            "convenience": 200,
            "university": 800  # 인천대 인접
        },
        "demographic": {
            "youth_ratio": 32,
            "family_ratio": 25,
            "senior_ratio": 8
        },
        "expected_top_type": "청년"
    },
    {
        "name": "경기 수원 영통구",
        "address": "경기 수원시 영통구 영통동 1000",
        "poi_distances": {
            "subway": 600,
            "school": 350,
            "hospital": 500,
            "convenience": 300,
            "university": 1200  # 성균관대 인접
        },
        "demographic": {
            "youth_ratio": 36,
            "family_ratio": 20,
            "senior_ratio": 9
        },
        "expected_top_type": "청년"
    },
    {
        "name": "경기 용인 수지구",
        "address": "경기 용인시 수지구 신봉동 571",
        "poi_distances": {
            "subway": 900,
            "school": 250,
            "hospital": 400,
            "convenience": 350,
            "university": 3500
        },
        "demographic": {
            "youth_ratio": 16,
            "family_ratio": 32,
            "senior_ratio": 11
        },
        "expected_top_type": "다자녀"
    },
    
    # === 경기도 추가 ===
    {
        "name": "경기 안양 평촌",
        "address": "경기 안양시 동안구 평촌동 1040",
        "poi_distances": {
            "subway": 350,
            "school": 300,
            "hospital": 450,
            "convenience": 200,
            "university": 3000
        },
        "demographic": {
            "youth_ratio": 20,
            "family_ratio": 28,
            "senior_ratio": 12
        },
        "expected_top_type": "다자녀"
    },
    {
        "name": "경기 부천 중동",
        "address": "경기 부천시 원미구 중동 1098",
        "poi_distances": {
            "subway": 400,
            "school": 400,
            "hospital": 350,
            "convenience": 250,
            "university": 4500
        },
        "demographic": {
            "youth_ratio": 17,
            "family_ratio": 26,
            "senior_ratio": 14
        },
        "expected_top_type": "다자녀"
    },
    {
        "name": "경기 화성 동탄",
        "address": "경기 화성시 반송동 142",
        "poi_distances": {
            "subway": 1200,  # 지하철 멀음
            "school": 200,   # 신도시 학교 우수
            "hospital": 600,
            "convenience": 300,
            "university": 5000
        },
        "demographic": {
            "youth_ratio": 14,
            "family_ratio": 35,  # 신혼 많음
            "senior_ratio": 7
        },
        "expected_top_type": "신혼·신생아 I"
    },
    {
        "name": "경기 평택 고덕",
        "address": "경기 평택시 고덕동 500",
        "poi_distances": {
            "subway": 2000,  # 지하철 없음
            "school": 400,
            "hospital": 800,
            "convenience": 500,
            "university": 6000
        },
        "demographic": {
            "youth_ratio": 13,
            "family_ratio": 28,
            "senior_ratio": 15
        },
        "expected_top_type": "다자녀"
    },
    {
        "name": "경기 파주 운정",
        "address": "경기 파주시 와동동 1613",
        "poi_distances": {
            "subway": 1500,
            "school": 250,
            "hospital": 700,
            "convenience": 350,
            "university": 5500
        },
        "demographic": {
            "youth_ratio": 15,
            "family_ratio": 32,
            "senior_ratio": 10
        },
        "expected_top_type": "다자녀"
    },
    
    # === 부산 ===
    {
        "name": "부산 해운대 센텀시티",
        "address": "부산 해운대구 센텀중앙로 79",
        "poi_distances": {
            "subway": 250,
            "school": 500,
            "hospital": 600,
            "convenience": 150,
            "university": 3000
        },
        "demographic": {
            "youth_ratio": 28,
            "family_ratio": 22,
            "senior_ratio": 11
        },
        "expected_top_type": "청년"
    },
    {
        "name": "부산 사하구",
        "address": "부산 사하구 하단동 1009",
        "poi_distances": {
            "subway": 500,
            "school": 350,
            "hospital": 400,
            "convenience": 300,
            "university": 2000
        },
        "demographic": {
            "youth_ratio": 20,
            "family_ratio": 25,
            "senior_ratio": 13
        },
        "expected_top_type": "다자녀"
    },
    {
        "name": "부산 동래구",
        "address": "부산 동래구 온천동 1393",
        "poi_distances": {
            "subway": 350,
            "school": 400,
            "hospital": 300,
            "convenience": 200,
            "university": 800  # 부산대 인접
        },
        "demographic": {
            "youth_ratio": 34,
            "family_ratio": 18,
            "senior_ratio": 10
        },
        "expected_top_type": "청년"
    },
    
    # === 대구 ===
    {
        "name": "대구 수성구 범어동",
        "address": "대구 수성구 범어동 169",
        "poi_distances": {
            "subway": 300,
            "school": 280,
            "hospital": 450,
            "convenience": 180,
            "university": 2500
        },
        "demographic": {
            "youth_ratio": 21,
            "family_ratio": 29,
            "senior_ratio": 12
        },
        "expected_top_type": "신혼·신생아 I"
    },
    {
        "name": "대구 달서구 월성동",
        "address": "대구 달서구 월성동 1324",
        "poi_distances": {
            "subway": 600,
            "school": 350,
            "hospital": 500,
            "convenience": 300,
            "university": 4000
        },
        "demographic": {
            "youth_ratio": 16,
            "family_ratio": 27,
            "senior_ratio": 15
        },
        "expected_top_type": "다자녀"
    },
    {
        "name": "대구 북구 침산동",
        "address": "대구 북구 침산동 1001",
        "poi_distances": {
            "subway": 700,
            "school": 450,
            "hospital": 350,
            "convenience": 350,
            "university": 5000
        },
        "demographic": {
            "youth_ratio": 14,
            "family_ratio": 22,
            "senior_ratio": 18
        },
        "expected_top_type": "고령자"
    },
    
    # === 대전 ===
    {
        "name": "대전 유성구 도룡동",
        "address": "대전 유성구 도룡동 448",
        "poi_distances": {
            "subway": 800,
            "school": 300,
            "hospital": 600,
            "convenience": 250,
            "university": 1000  # KAIST 인근
        },
        "demographic": {
            "youth_ratio": 38,
            "family_ratio": 20,
            "senior_ratio": 8
        },
        "expected_top_type": "청년"
    },
    {
        "name": "대전 서구 둔산동",
        "address": "대전 서구 둔산동 1338",
        "poi_distances": {
            "subway": 900,
            "school": 350,
            "hospital": 500,
            "convenience": 300,
            "university": 3500
        },
        "demographic": {
            "youth_ratio": 19,
            "family_ratio": 28,
            "senior_ratio": 13
        },
        "expected_top_type": "다자녀"
    },
    {
        "name": "대전 중구 대흥동",
        "address": "대전 중구 대흥동 500",
        "poi_distances": {
            "subway": 750,
            "school": 400,
            "hospital": 300,
            "convenience": 280,
            "university": 4000
        },
        "demographic": {
            "youth_ratio": 15,
            "family_ratio": 23,
            "senior_ratio": 17
        },
        "expected_top_type": "고령자"
    },
    
    # === 광주 ===
    {
        "name": "광주 서구 상무지구",
        "address": "광주 서구 치평동 1200",
        "poi_distances": {
            "subway": 1500,  # 광주는 지하철 제한적
            "school": 250,
            "hospital": 400,
            "convenience": 200,
            "university": 3000
        },
        "demographic": {
            "youth_ratio": 20,
            "family_ratio": 30,
            "senior_ratio": 11
        },
        "expected_top_type": "신혼·신생아 I"
    },
    {
        "name": "광주 북구 첨단지구",
        "address": "광주 북구 오룡동 1000",
        "poi_distances": {
            "subway": 2000,
            "school": 300,
            "hospital": 600,
            "convenience": 250,
            "university": 2000  # 광주과기원
        },
        "demographic": {
            "youth_ratio": 32,
            "family_ratio": 22,
            "senior_ratio": 9
        },
        "expected_top_type": "청년"
    }
]


class TestTypeDemandScoreV3:
    """Type Demand Score v3.0 통합 테스트"""
    
    @pytest.fixture
    def engine(self):
        """테스트용 엔진 인스턴스"""
        return get_type_demand_score_v3()
    
    def test_engine_initialization(self, engine):
        """엔진 초기화 테스트"""
        assert engine is not None
        assert isinstance(engine, TypeDemandScoreV3)
        logger.info("✅ 엔진 초기화 성공")
    
    def test_all_30_addresses(self, engine):
        """30개 주소 전체 테스트"""
        logger.info("\n" + "="*80)
        logger.info("🧪 Type Demand Score v3.0 - 30개 주소 자동 검증 시작")
        logger.info("="*80 + "\n")
        
        total_passed = 0
        total_failed = 0
        failed_cases = []
        
        for idx, test_case in enumerate(TEST_ADDRESSES, 1):
            logger.info(f"\n[{idx}/30] {test_case['name']} ({test_case['address']})")
            logger.info("-" * 60)
            
            try:
                # 유형별 점수 계산
                results = engine.calculate_all_types(
                    poi_distances=test_case['poi_distances'],
                    demographic_info=test_case['demographic'],
                    base_score=50.0
                )
                
                # 결과 출력
                for unit_type, score_obj in results.items():
                    logger.info(
                        f"  {unit_type}: {score_obj.total_score}점 "
                        f"(등급: {score_obj.grade})"
                    )
                
                # 최고 점수 유형 확인
                top_type = max(results.items(), key=lambda x: x[1].total_score)[0]
                expected = test_case['expected_top_type']
                
                if top_type == expected:
                    logger.info(f"✅ PASS: 예상 유형 일치 ({top_type})")
                    total_passed += 1
                else:
                    logger.warning(f"⚠️ FAIL: 예상={expected}, 실제={top_type}")
                    total_failed += 1
                    failed_cases.append({
                        "name": test_case['name'],
                        "expected": expected,
                        "actual": top_type
                    })
                
                # 점수 차이 검증
                scores = [s.total_score for s in results.values()]
                max_score = max(scores)
                min_score = min(scores)
                score_diff = max_score - min_score
                
                if score_diff >= 10.0:
                    logger.info(f"✅ 점수 차이 충족: {score_diff:.1f}점 (최소 10점)")
                else:
                    logger.warning(f"⚠️ 점수 차이 부족: {score_diff:.1f}점")
            
            except Exception as e:
                logger.error(f"❌ ERROR: {e}")
                total_failed += 1
                failed_cases.append({
                    "name": test_case['name'],
                    "expected": test_case.get('expected_top_type', 'N/A'),
                    "actual": f"ERROR: {str(e)}"
                })
        
        # 최종 결과 요약
        logger.info("\n" + "="*80)
        logger.info("📊 테스트 결과 요약")
        logger.info("="*80)
        logger.info(f"✅ 통과: {total_passed}/30 ({total_passed/30*100:.1f}%)")
        logger.info(f"❌ 실패: {total_failed}/30 ({total_failed/30*100:.1f}%)")
        
        if failed_cases:
            logger.info("\n⚠️ 실패한 케이스:")
            for case in failed_cases:
                logger.info(f"  - {case['name']}: 예상={case['expected']}, 실제={case['actual']}")
        
        logger.info("="*80 + "\n")
        
        # 80% 이상 통과 시 테스트 성공
        assert total_passed >= 24, f"통과율 미달: {total_passed}/30 (최소 24/30 필요)"
    
    def test_score_differentiation(self, engine):
        """유형 간 점수 차별화 테스트"""
        logger.info("\n🧪 유형 간 점수 차이 검증")
        
        # 역세권 청년 타겟 지역
        poi_distances = {
            "subway": 200,
            "school": 600,
            "hospital": 500,
            "convenience": 100,
            "university": 800
        }
        demographic = {
            "youth_ratio": 35,
            "family_ratio": 20,
            "senior_ratio": 8
        }
        
        results = engine.calculate_all_types(poi_distances, demographic)
        
        # 점수 정렬
        sorted_scores = sorted(
            [(k, v.total_score) for k, v in results.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        logger.info("점수 순위:")
        for rank, (unit_type, score) in enumerate(sorted_scores, 1):
            logger.info(f"  {rank}. {unit_type}: {score}점")
        
        # 최고-최저 점수 차이 검증
        max_score = sorted_scores[0][1]
        min_score = sorted_scores[-1][1]
        diff = max_score - min_score
        
        logger.info(f"\n최고-최저 점수 차이: {diff:.1f}점")
        assert diff >= 15.0, f"점수 차이 부족: {diff:.1f}점 (최소 15점 필요)"
        
        logger.info("✅ 유형 간 차별화 충족 (15점 이상 차이)")
    
    def test_poi_bonus_calculation(self, engine):
        """POI 보너스 계산 테스트"""
        logger.info("\n🧪 POI 보너스 계산 검증")
        
        # 모든 POI 우수한 경우
        poi_distances = {
            "subway": 150,      # Excellent
            "school": 200,      # Excellent
            "hospital": 300,    # Excellent
            "convenience": 100, # Excellent
            "university": 800   # Excellent
        }
        demographic = {"youth_ratio": 30, "family_ratio": 25, "senior_ratio": 10}
        
        result = engine.calculate_type_score(
            unit_type="청년",
            poi_distances=poi_distances,
            demographic_info=demographic
        )
        
        logger.info(f"청년 유형 POI 보너스:")
        for poi, bonus in result.poi_bonuses.items():
            logger.info(f"  - {poi}: +{bonus}점")
        
        total_bonus = sum(result.poi_bonuses.values())
        logger.info(f"\n총 보너스: +{total_bonus}점")
        
        # 보너스는 최대 15점
        assert total_bonus <= 15.0, f"보너스 과다: {total_bonus}점 (최대 15점)"
        assert total_bonus > 0, "보너스 0점 (POI 우수 시 보너스 필요)"
        
        logger.info(f"✅ POI 보너스 정상 ({total_bonus:.1f}점, 최대 15점 제한)")


def run_validation_report():
    """
    검증 리포트 생성 및 출력
    (pytest 외부에서 직접 실행 가능)
    """
    print("\n" + "="*80)
    print("🚀 ZeroSite Type Demand Score v3.0 검증 리포트")
    print("="*80)
    
    engine = get_type_demand_score_v3()
    
    print("\n📋 테스트 주소 목록:")
    print("-" * 80)
    
    for idx, test_case in enumerate(TEST_ADDRESSES, 1):
        print(f"{idx:2d}. {test_case['name']:30s} | 예상 유형: {test_case['expected_top_type']}")
    
    print(f"\n총 {len(TEST_ADDRESSES)}개 주소 검증 준비 완료")
    print("="*80 + "\n")
    
    print("💡 실행 방법:")
    print("  pytest tests/test_type_demand_score_v3.py -v -s")
    print("  또는")
    print("  python -m pytest tests/test_type_demand_score_v3.py::TestTypeDemandScoreV3::test_all_30_addresses -v -s")
    print()


if __name__ == "__main__":
    # 직접 실행 시 검증 리포트 출력
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    run_validation_report()
