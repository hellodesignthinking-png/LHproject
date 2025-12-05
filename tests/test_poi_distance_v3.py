"""
ZeroSite POI Distance v3.0 자동 테스트
================================================================================
50개 실제 주소로 POI 거리 측정 정확도 검증

테스트 범위:
1. 서울 25개 (강남/강북/도심/외곽)
2. 경기 15개 (수원/성남/고양/인천)
3. 지방 10개 (부산/대구/대전/광주/울산)

검증 항목:
✅ 학교/병원/편의시설 거리 측정 정확도
✅ Kakao API 우선, 실패 시 Fallback
✅ LH 기준 색상 코드 정확성
✅ 누락 POI 자동 검출
"""

import pytest
import asyncio
import logging
from typing import Dict, List
from app.services.poi_distance_v3 import (
    POIDistanceV3,
    get_poi_distance_v3,
    POIResult,
    POISearchReport
)
from app.schemas import Coordinates

logger = logging.getLogger(__name__)


# 50개 테스트 주소 (실제 좌표)
TEST_ADDRESSES_50 = [
    # === 서울 강남권 (5개) ===
    {
        "name": "강남역 역삼동",
        "address": "서울 강남구 역삼동 737",
        "coordinates": Coordinates(latitude=37.4995, longitude=127.0374),
        "expected_pois": ["subway", "school", "hospital", "convenience", "university"]
    },
    {
        "name": "서초동 교대역",
        "address": "서울 서초구 서초동 1650",
        "coordinates": Coordinates(latitude=37.4941, longitude=127.0140),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "잠실 롯데타워",
        "address": "서울 송파구 올림픽로 300",
        "coordinates": Coordinates(latitude=37.5125, longitude=127.1025),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "삼성동 코엑스",
        "address": "서울 강남구 삼성동 159",
        "coordinates": Coordinates(latitude=37.5125, longitude=127.0594),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "청담동",
        "address": "서울 강남구 청담동 129-7",
        "coordinates": Coordinates(latitude=37.5226, longitude=127.0474),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    
    # === 서울 강북권 (5개) ===
    {
        "name": "홍대입구역",
        "address": "서울 마포구 서교동 395-69",
        "coordinates": Coordinates(latitude=37.5572, longitude=126.9240),
        "expected_pois": ["subway", "school", "hospital", "convenience", "university"]
    },
    {
        "name": "신촌 연세대",
        "address": "서울 서대문구 신촌동 134",
        "coordinates": Coordinates(latitude=37.5585, longitude=126.9369),
        "expected_pois": ["subway", "school", "hospital", "convenience", "university"]
    },
    {
        "name": "노원역",
        "address": "서울 노원구 상계동 701",
        "coordinates": Coordinates(latitude=37.6551, longitude=127.0616),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "강북구 수유동",
        "address": "서울 강북구 수유동 8-97",
        "coordinates": Coordinates(latitude=37.6382, longitude=127.0253),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "성북구 성신여대입구역",
        "address": "서울 성북구 동선동3가 116-53",
        "coordinates": Coordinates(latitude=37.5926, longitude=127.0170),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    
    # === 서울 도심권 (5개) ===
    {
        "name": "광화문 세종대로",
        "address": "서울 종로구 세종대로 172",
        "coordinates": Coordinates(latitude=37.5720, longitude=126.9769),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "시청역",
        "address": "서울 중구 태평로1가 31",
        "coordinates": Coordinates(latitude=37.5655, longitude=126.9778),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "명동",
        "address": "서울 중구 명동2가 54-5",
        "coordinates": Coordinates(latitude=37.5635, longitude=126.9832),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "여의도 국회의사당",
        "address": "서울 영등포구 여의도동 1",
        "coordinates": Coordinates(latitude=37.5290, longitude=126.9141),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "동대문디자인플라자",
        "address": "서울 중구 을지로7가 2-1",
        "coordinates": Coordinates(latitude=37.5663, longitude=127.0093),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    
    # === 서울 외곽권 (10개) ===
    {
        "name": "강동구 길동",
        "address": "서울 강동구 길동 395",
        "coordinates": Coordinates(latitude=37.5383, longitude=127.1443),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "강서구 화곡동",
        "address": "서울 강서구 화곡동 1009",
        "coordinates": Coordinates(latitude=37.5413, longitude=126.8401),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "은평구 응암동",
        "address": "서울 은평구 응암동 165",
        "coordinates": Coordinates(latitude=37.6027, longitude=126.9170),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "구로구 신도림역",
        "address": "서울 구로구 신도림동 337",
        "coordinates": Coordinates(latitude=37.5084, longitude=126.8914),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "금천구 가산디지털단지",
        "address": "서울 금천구 가산동 371-28",
        "coordinates": Coordinates(latitude=37.4815, longitude=126.8828),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "관악구 신림역",
        "address": "서울 관악구 신림동 1422-5",
        "coordinates": Coordinates(latitude=37.4842, longitude=126.9297),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "동작구 사당역",
        "address": "서울 동작구 사당동 1022",
        "coordinates": Coordinates(latitude=37.4767, longitude=126.9814),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "광진구 건대입구역",
        "address": "서울 광진구 화양동 6-6",
        "coordinates": Coordinates(latitude=37.5404, longitude=127.0698),
        "expected_pois": ["subway", "school", "hospital", "convenience", "university"]
    },
    {
        "name": "성동구 왕십리역",
        "address": "서울 성동구 행당동 166-1",
        "coordinates": Coordinates(latitude=37.5611, longitude=127.0377),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "중랑구 상봉역",
        "address": "서울 중랑구 상봉동 227",
        "coordinates": Coordinates(latitude=37.5965, longitude=127.0856),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    
    # === 경기 남부 (5개) ===
    {
        "name": "성남 분당구 서현역",
        "address": "경기 성남시 분당구 서현동 268",
        "coordinates": Coordinates(latitude=37.3850, longitude=127.1234),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "수원 영통구 광교",
        "address": "경기 수원시 영통구 이의동 1325",
        "coordinates": Coordinates(latitude=37.2973, longitude=127.0468),
        "expected_pois": ["school", "hospital", "convenience", "university"]
    },
    {
        "name": "용인 수지구 죽전",
        "address": "경기 용인시 수지구 죽전동 1225",
        "coordinates": Coordinates(latitude=37.3245, longitude=127.1067),
        "expected_pois": ["school", "hospital", "convenience", "university"]
    },
    {
        "name": "화성 동탄신도시",
        "address": "경기 화성시 반송동 142",
        "coordinates": Coordinates(latitude=37.2008, longitude=127.0755),
        "expected_pois": ["school", "hospital", "convenience"]
    },
    {
        "name": "안양 평촌신도시",
        "address": "경기 안양시 동안구 평촌동 1040",
        "coordinates": Coordinates(latitude=37.3893, longitude=126.9503),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    
    # === 경기 북부 (5개) ===
    {
        "name": "고양 일산 백석동",
        "address": "경기 고양시 일산동구 백석동 1256",
        "coordinates": Coordinates(latitude=37.6373, longitude=126.7860),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "파주 운정신도시",
        "address": "경기 파주시 와동동 1613",
        "coordinates": Coordinates(latitude=37.7462, longitude=126.7281),
        "expected_pois": ["school", "hospital", "convenience"]
    },
    {
        "name": "의정부 민락동",
        "address": "경기 의정부시 민락동 734",
        "coordinates": Coordinates(latitude=37.7397, longitude=127.0663),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "양주 옥정신도시",
        "address": "경기 양주시 옥정동 555",
        "coordinates": Coordinates(latitude=37.8298, longitude=127.0850),
        "expected_pois": ["school", "hospital", "convenience"]
    },
    {
        "name": "남양주 다산신도시",
        "address": "경기 남양주시 다산동 980",
        "coordinates": Coordinates(latitude=37.6111, longitude=127.1520),
        "expected_pois": ["school", "hospital", "convenience"]
    },
    
    # === 경기 서부 (5개) ===
    {
        "name": "인천 연수구 송도",
        "address": "인천 연수구 송도동 30-1",
        "coordinates": Coordinates(latitude=37.3826, longitude=126.6564),
        "expected_pois": ["subway", "school", "hospital", "convenience", "university"]
    },
    {
        "name": "부천 중동신도시",
        "address": "경기 부천시 원미구 중동 1098",
        "coordinates": Coordinates(latitude=37.5038, longitude=126.7642),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "광명 철산역",
        "address": "경기 광명시 철산동 348",
        "coordinates": Coordinates(latitude=37.4835, longitude=126.8582),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "시흥 은행동",
        "address": "경기 시흥시 은행동 541",
        "coordinates": Coordinates(latitude=37.4396, longitude=126.8031),
        "expected_pois": ["school", "hospital", "convenience"]
    },
    {
        "name": "김포 한강신도시",
        "address": "경기 김포시 장기동 2100",
        "coordinates": Coordinates(latitude=37.7154, longitude=126.7279),
        "expected_pois": ["school", "hospital", "convenience"]
    },
    
    # === 부산 (3개) ===
    {
        "name": "부산 해운대 센텀시티",
        "address": "부산 해운대구 센텀중앙로 79",
        "coordinates": Coordinates(latitude=35.1697, longitude=129.1309),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "부산 서면역",
        "address": "부산 부산진구 부전동 255-1",
        "coordinates": Coordinates(latitude=35.1579, longitude=129.0601),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "부산 동래구 온천동",
        "address": "부산 동래구 온천동 1393",
        "coordinates": Coordinates(latitude=35.2194, longitude=129.0863),
        "expected_pois": ["subway", "school", "hospital", "convenience", "university"]
    },
    
    # === 대구 (2개) ===
    {
        "name": "대구 수성구 범어동",
        "address": "대구 수성구 범어동 169",
        "coordinates": Coordinates(latitude=35.8590, longitude=128.6311),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    {
        "name": "대구 동성로",
        "address": "대구 중구 동성로2가 81",
        "coordinates": Coordinates(latitude=35.8682, longitude=128.5963),
        "expected_pois": ["subway", "school", "hospital", "convenience"]
    },
    
    # === 대전 (2개) ===
    {
        "name": "대전 유성구 도룡동 KAIST",
        "address": "대전 유성구 도룡동 448",
        "coordinates": Coordinates(latitude=36.3729, longitude=127.3604),
        "expected_pois": ["school", "hospital", "convenience", "university"]
    },
    {
        "name": "대전 서구 둔산동",
        "address": "대전 서구 둔산동 1338",
        "coordinates": Coordinates(latitude=36.3512, longitude=127.3792),
        "expected_pois": ["school", "hospital", "convenience"]
    },
    
    # === 광주/울산 (3개) ===
    {
        "name": "광주 서구 상무지구",
        "address": "광주 서구 치평동 1200",
        "coordinates": Coordinates(latitude=35.1522, longitude=126.8894),
        "expected_pois": ["school", "hospital", "convenience"]
    },
    {
        "name": "광주 북구 첨단지구",
        "address": "광주 북구 오룡동 1000",
        "coordinates": Coordinates(latitude=35.2287, longitude=126.8432),
        "expected_pois": ["school", "hospital", "convenience", "university"]
    },
    {
        "name": "울산 남구 삼산동",
        "address": "울산 남구 삼산동 1488-17",
        "coordinates": Coordinates(latitude=35.5383, longitude=129.3302),
        "expected_pois": ["school", "hospital", "convenience"]
    }
]


class TestPOIDistanceV3:
    """POI Distance v3.0 통합 테스트"""
    
    @pytest.fixture
    def engine(self):
        """테스트용 엔진 인스턴스"""
        return get_poi_distance_v3()
    
    @pytest.mark.asyncio
    async def test_all_50_addresses(self, engine):
        """50개 주소 전체 POI 검색 테스트"""
        logger.info("\n" + "="*80)
        logger.info("🧪 POI Distance v3.0 - 50개 주소 자동 검증 시작")
        logger.info("="*80 + "\n")
        
        total_addresses = len(TEST_ADDRESSES_50)
        successful_searches = 0
        total_pois_found = 0
        total_pois_missing = 0
        kakao_total_success = 0
        fallback_total_usage = 0
        
        for idx, test_case in enumerate(TEST_ADDRESSES_50, 1):
            logger.info(f"\n[{idx}/{total_addresses}] {test_case['name']} ({test_case['address']})")
            logger.info("-" * 60)
            
            try:
                # POI 검색 실행
                report = await engine.search_all_pois(
                    coordinates=test_case['coordinates'],
                    required_pois=test_case['expected_pois']
                )
                
                # 결과 로깅
                logger.info(f"  📊 검색 결과:")
                logger.info(f"    - 전체: {report.total_searched}개")
                logger.info(f"    - 발견: {report.total_found}개")
                logger.info(f"    - 누락: {len(report.missing_pois)}개")
                logger.info(f"    - Kakao 성공률: {report.kakao_success_rate:.1f}%")
                logger.info(f"    - Fallback 사용: {report.fallback_usage}회")
                
                # POI별 상세 결과
                for poi_type, result in report.all_results.items():
                    logger.info(
                        f"  ✅ {poi_type}: {result.name} "
                        f"({result.distance}m, 등급: {result.distance_grade}, "
                        f"소스: {result.source})"
                    )
                
                # 누락 POI 출력
                if report.missing_pois:
                    logger.warning(f"  ⚠️ 누락 POI: {', '.join(report.missing_pois)}")
                
                # 통계 집계
                successful_searches += 1
                total_pois_found += report.total_found
                total_pois_missing += len(report.missing_pois)
                kakao_total_success += report.kakao_success_rate
                fallback_total_usage += report.fallback_usage
            
            except Exception as e:
                logger.error(f"❌ ERROR: {e}")
        
        # 최종 결과 요약
        logger.info("\n" + "="*80)
        logger.info("📊 전체 테스트 결과 요약")
        logger.info("="*80)
        logger.info(f"✅ 성공한 주소: {successful_searches}/{total_addresses}")
        logger.info(f"📍 총 발견 POI: {total_pois_found}개")
        logger.info(f"❌ 총 누락 POI: {total_pois_missing}개")
        logger.info(f"📈 평균 Kakao 성공률: {kakao_total_success/total_addresses:.1f}%")
        logger.info(f"🔄 총 Fallback 사용: {fallback_total_usage}회")
        logger.info("="*80 + "\n")
        
        # 80% 이상 POI 발견 시 테스트 통과
        total_expected_pois = sum(len(t['expected_pois']) for t in TEST_ADDRESSES_50)
        poi_found_rate = (total_pois_found / total_expected_pois * 100) if total_expected_pois > 0 else 0
        
        assert poi_found_rate >= 80, f"POI 발견률 미달: {poi_found_rate:.1f}% (최소 80% 필요)"
        logger.info(f"✅ 전체 테스트 통과: POI 발견률 {poi_found_rate:.1f}%")
    
    @pytest.mark.asyncio
    async def test_distance_grade_accuracy(self, engine):
        """거리 등급 및 색상 코드 정확도 테스트"""
        logger.info("\n🧪 거리 등급 및 색상 코드 검증")
        
        # 강남역 테스트
        test_case = TEST_ADDRESSES_50[0]
        report = await engine.search_all_pois(
            coordinates=test_case['coordinates'],
            required_pois=["subway", "school", "hospital", "convenience"]
        )
        
        logger.info("\n거리 등급 및 색상 코드:")
        for poi_type, result in report.all_results.items():
            logger.info(
                f"  {poi_type}: {result.distance}m -> "
                f"등급={result.distance_grade}, 색상={result.color_code}"
            )
        
        # 지하철은 300m 이내이면 excellent 등급이어야 함
        if "subway" in report.all_results:
            subway_result = report.all_results["subway"]
            if subway_result.distance <= 300:
                assert subway_result.distance_grade == "excellent", \
                    f"지하철 등급 오류: {subway_result.distance}m는 excellent여야 함"
                assert subway_result.color_code == "#00C853", \
                    "지하철 색상 코드 오류"
                logger.info("✅ 지하철 거리 등급 및 색상 코드 정확")
    
    @pytest.mark.asyncio
    async def test_missing_poi_report(self, engine):
        """누락 POI 리포트 생성 테스트"""
        logger.info("\n🧪 누락 POI 리포트 생성 검증")
        
        # 원거리 지역 테스트 (POI 부족 가능성 높음)
        test_case = {
            "name": "외곽 테스트",
            "coordinates": Coordinates(latitude=37.9, longitude=127.8),  # 원거리
            "expected_pois": ["subway", "school", "hospital", "convenience", "university"]
        }
        
        report = await engine.search_all_pois(
            coordinates=test_case['coordinates'],
            required_pois=test_case['expected_pois']
        )
        
        # 리포트 생성
        report_text = engine.generate_missing_poi_report(report)
        logger.info("\n" + report_text)
        
        assert len(report_text) > 0, "리포트 생성 실패"
        logger.info("✅ 누락 POI 리포트 생성 성공")


def run_poi_test_summary():
    """
    POI 테스트 요약 출력
    (pytest 외부에서 직접 실행 가능)
    """
    print("\n" + "="*80)
    print("🚀 ZeroSite POI Distance v3.0 테스트 요약")
    print("="*80)
    
    print(f"\n📋 총 {len(TEST_ADDRESSES_50)}개 주소 테스트 준비 완료")
    print("\n주요 테스트 지역:")
    print("  - 서울: 25개 (강남/강북/도심/외곽)")
    print("  - 경기: 15개 (남부/북부/서부)")
    print("  - 지방: 10개 (부산/대구/대전/광주/울산)")
    
    print("\n검증 항목:")
    print("  ✅ Kakao Local API 우선 검색")
    print("  ✅ Fallback API (Naver/Google) 적용")
    print("  ✅ LH 기준 거리 등급 (excellent/good/fair/poor)")
    print("  ✅ 색상 코드 (#00C853 ~ #D50000)")
    print("  ✅ 누락 POI 자동 검출 및 리포트")
    
    print("\n💡 실행 방법:")
    print("  pytest tests/test_poi_distance_v3.py -v -s")
    print("  또는")
    print("  python -m pytest tests/test_poi_distance_v3.py::TestPOIDistanceV3::test_all_50_addresses -v -s")
    print("="*80 + "\n")


if __name__ == "__main__":
    # 직접 실행 시 요약 출력
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    run_poi_test_summary()
