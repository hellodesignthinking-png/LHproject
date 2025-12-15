"""
ZeroSite v37.0 - Parcel-Specific Data Database (PNU-Based)
필지별 정확 데이터 (PNU 코드 기반)

Author: Antenna Holdings Development Team
Date: 2025-12-14
Purpose: Precise parcel-level data for accurate appraisals
"""

from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# PNU-Based Parcel Database (필지별 데이터베이스)
# PNU = 19-digit Parcel Number Unique Code
# Format: SIDO(2) + SIGUNGU(3) + DONG(3) + LAND_TYPE(1) + JIBUN_MAIN(4) + JIBUN_SUB(4) + EXTRA(2)
# ============================================================================

PARCEL_DATABASE = {
    # 서울특별시 강남구 역삼동 680-11 (PNU: 1168010100106800011)
    # 상업지역, 강남 핵심지 → 높은 공시지가
    "1168010100106800011": {
        "address": "서울특별시 강남구 역삼동 680-11",
        "official_land_price_per_sqm": 27200000,  # 2,720만원/㎡
        "zone_type": "제3종일반주거지역",
        "road_width": 25,  # 도로폭 25m
        "land_shape": "정형",  # 정형지
        "topography": "평지",
        "use_situation": "대",  # 대지
        "note": "강남역 인근 핵심 상업지역"
    },
    
    # 서울특별시 마포구 성산동 250-40 (PNU: 1144010800102500040)
    "1144010800102500040": {
        "address": "서울특별시 마포구 성산동 250-40",
        "official_land_price_per_sqm": 5893000,  # 589만원/㎡
        "zone_type": "제2종일반주거지역",
        "road_width": 12,
        "land_shape": "정형",
        "topography": "평지",
        "use_situation": "대",
        "note": "마포구 일반주거지역"
    },
    
    # 서울특별시 관악구 신림동 1524-8 (PNU: 1162010100115240008)
    "1162010100115240008": {
        "address": "서울특별시 관악구 신림동 1524-8",
        "official_land_price_per_sqm": 9039000,  # 904만원/㎡
        "zone_type": "준주거지역",
        "road_width": 15,
        "land_shape": "정형",
        "topography": "평지",
        "use_situation": "대",
        "note": "신림역 인근 준주거지역"
    },
    
    # 경기도 성남시 분당구 정자동 100-1 (PNU: 4113510300101000001)
    "4113510300101000001": {
        "address": "경기도 성남시 분당구 정자동 100-1",
        "official_land_price_per_sqm": 18500000,  # 1,850만원/㎡
        "zone_type": "제1종일반주거지역",
        "road_width": 20,
        "land_shape": "정형",
        "topography": "평지",
        "use_situation": "대",
        "note": "분당 신도시 정자동 고급주택지"
    },
    
    # 부산광역시 해운대구 우동 1500-1 (PNU: 2647010100115000001)
    "2647010100115000001": {
        "address": "부산광역시 해운대구 우동 1500-1",
        "official_land_price_per_sqm": 18500000,  # 1,850만원/㎡
        "zone_type": "제2종일반주거지역",
        "road_width": 20,
        "land_shape": "정형",
        "topography": "평지",
        "use_situation": "대",
        "note": "센텀시티 인근 고급주거지역"
    },
    
    # 서울특별시 강남구 역삼동 111 (PNU: 1168010100100110000)
    # 다른 지번 → 약간 다른 용도지역
    "1168010100100110000": {
        "address": "서울특별시 강남구 역삼동 111",
        "official_land_price_per_sqm": 27200000,  # 2,720만원/㎡
        "zone_type": "근린상업지역",
        "road_width": 30,
        "land_shape": "정형",
        "topography": "평지",
        "use_situation": "상업용지",
        "note": "강남역 상권 중심부"
    },
    
    # 부산광역시 해운대구 우동 1500-2 (PNU: 2647010100115000002)
    # 같은 동네, 다른 지번 → 약간 다른 공시지가
    "2647010100115000002": {
        "address": "부산광역시 해운대구 우동 1500-2",
        "official_land_price_per_sqm": 17800000,  # 1,780만원/㎡ (조금 낮음)
        "zone_type": "제2종일반주거지역",
        "road_width": 15,
        "land_shape": "정형",
        "topography": "평지",
        "use_situation": "대",
        "note": "센텀시티 인근 (1500-1보다 후면)"
    },
    
    # 경기도 성남시 분당구 정자동 200-1 (PNU: 4113510300102000001)
    "4113510300102000001": {
        "address": "경기도 성남시 분당구 정자동 200-1",
        "official_land_price_per_sqm": 17500000,  # 1,750만원/㎡
        "zone_type": "제2종일반주거지역",  # 정자동 내에서도 지번마다 다름
        "road_width": 15,
        "land_shape": "정형",
        "topography": "평지",
        "use_situation": "대",
        "note": "분당 정자동 일반주거지역"
    },
}

# ============================================================================
# Expanded Parcel Database (추가 47개 필지 - v38+)
# ============================================================================

# Import expanded data
try:
    from app.data.parcel_database_expanded import EXPANDED_PARCEL_DATABASE
    PARCEL_DATABASE.update(EXPANDED_PARCEL_DATABASE)
    logger.info(f"✅ Expanded parcel database: {len(PARCEL_DATABASE)} total parcels")
except ImportError:
    logger.warning("⚠️ Expanded parcel database not available")

# ============================================================================
# Zone Type Map (지역별 용도지역 매핑)
# 특정 주소의 PNU를 모를 때 사용하는 폴백 데이터
# ============================================================================

ZONE_TYPE_MAP = {
    # 서울특별시 강남구
    ("서울특별시", "강남구", "역삼동"): {
        "default_zone": "제3종일반주거지역",
        "variations": {
            "상업지역": ["역삼로", "강남대로", "테헤란로"],  # 주요 도로변
            "근린상업지역": ["역삼역", "강남역"],  # 역 인근
            "제2종일반주거지역": ["내부주택가"]  # 이면도로
        }
    },
    ("서울특별시", "강남구", "삼성동"): {
        "default_zone": "제3종일반주거지역",
        "variations": {}
    },
    ("서울특별시", "강남구", "대치동"): {
        "default_zone": "제2종일반주거지역",  # 학군지 주거지역
        "variations": {}
    },
    
    # 서울특별시 마포구
    ("서울특별시", "마포구", "성산동"): {
        "default_zone": "제2종일반주거지역",
        "variations": {}
    },
    ("서울", "마포구", "성산동"): {
        "default_zone": "제2종일반주거지역",
        "variations": {}
    },
    ("서울특별시", "마포구", "연남동"): {
        "default_zone": "제2종일반주거지역",
        "variations": {}
    },
    ("서울특별시", "마포구", "서교동"): {
        "default_zone": "준주거지역",
        "variations": {}
    },
    
    # 서울특별시 관악구
    ("서울특별시", "관악구", "신림동"): {
        "default_zone": "준주거지역",  # 대학가 특성
        "variations": {
            "제2종일반주거지역": ["내부주택가"]
        }
    },
    ("서울", "관악구", "신림동"): {
        "default_zone": "준주거지역",  # 대학가 특성
        "variations": {
            "제2종일반주거지역": ["내부주택가"]
        }
    },
    ("서울특별시", "관악구", "봉천동"): {
        "default_zone": "제2종일반주거지역",
        "variations": {}
    },
    
    # 부산광역시 해운대구
    ("부산광역시", "해운대구", "우동"): {
        "default_zone": "제2종일반주거지역",
        "variations": {
            "준주거지역": ["센텀시티", "재송"],  # 신도시지역
            "근린상업지역": ["센텀역"]  # 역 인근
        }
    },
    ("부산광역시", "해운대구", "좌동"): {
        "default_zone": "제2종일반주거지역",
        "variations": {}
    },
    
    # 경기도 성남시 분당구
    ("경기도", "성남시 분당구", "정자동"): {
        "default_zone": "제1종일반주거지역",  # 신도시 계획지역
        "variations": {
            "제2종일반주거지역": ["정자역", "불정로"]
        }
    },
    ("경기", "성남시 분당구", "정자동"): {
        "default_zone": "제1종일반주거지역",  # 신도시 계획지역
        "variations": {
            "제2종일반주거지역": ["정자역", "불정로"]
        }
    },
    ("경기도", "성남시", "정자동"): {
        "default_zone": "제1종일반주거지역",
        "variations": {}
    },
    ("경기", "성남시", "정자동"): {
        "default_zone": "제1종일반주거지역",
        "variations": {}
    },
    ("경기도", "성남시 분당구", "야탑동"): {
        "default_zone": "제2종일반주거지역",
        "variations": {}
    },
    ("경기도", "성남시 분당구", "서현동"): {
        "default_zone": "제2종일반주거지역",
        "variations": {}
    },
    
    # 인천광역시 연수구
    ("인천광역시", "연수구", "송도동"): {
        "default_zone": "제2종일반주거지역",
        "variations": {
            "근린상업지역": ["센트럴파크", "송도역"],
            "준주거지역": ["국제업무단지"]
        }
    },
    ("인천", "연수구", "송도동"): {
        "default_zone": "제2종일반주거지역",
        "variations": {}
    },
    
    # 대구광역시 수성구
    ("대구광역시", "수성구", "범어동"): {
        "default_zone": "제2종일반주거지역",
        "variations": {}
    },
    ("대구", "수성구", "범어동"): {
        "default_zone": "제2종일반주거지역",
        "variations": {}
    },
    
    # 광주광역시 서구
    ("광주광역시", "서구", "치평동"): {
        "default_zone": "제2종일반주거지역",
        "variations": {}
    },
    ("광주", "서구", "치평동"): {
        "default_zone": "제2종일반주거지역",
        "variations": {}
    },
    
    # 대전광역시 유성구
    ("대전광역시", "유성구", "봉명동"): {
        "default_zone": "제2종일반주거지역",
        "variations": {}
    },
    ("대전", "유성구", "봉명동"): {
        "default_zone": "제2종일반주거지역",
        "variations": {}
    },
    
    # 제주특별자치도
    ("제주특별자치도", "제주시", "연동"): {
        "default_zone": "계획관리지역",
        "variations": {}
    },
    ("제주", "제주시", "연동"): {
        "default_zone": "계획관리지역",
        "variations": {}
    },
}

# ============================================================================
# Helper Functions
# ============================================================================

def get_parcel_data(pnu: str) -> Optional[Dict]:
    """
    PNU 코드로 필지 데이터 조회
    
    Args:
        pnu: 19자리 PNU 코드 (예: "1168010100106800011")
    
    Returns:
        필지 데이터 dict 또는 None
    """
    if pnu in PARCEL_DATABASE:
        logger.info(f"✅ PNU found: {pnu}")
        return PARCEL_DATABASE[pnu].copy()
    
    logger.warning(f"⚠️ PNU not found: {pnu}")
    return None


def get_zone_by_region(
    sido: str,
    sigungu: str,
    dong: str,
    detail: Optional[str] = None
) -> str:
    """
    주소 기반 용도지역 조회 (PNU 모를 때 폴백)
    
    Args:
        sido: 시/도 (예: "서울특별시")
        sigungu: 시/군/구 (예: "강남구")
        dong: 읍/면/동 (예: "역삼동")
        detail: 상세주소 (예: "강남대로", "역삼역 인근")
    
    Returns:
        추정 용도지역
    """
    key = (sido, sigungu, dong)
    
    if key in ZONE_TYPE_MAP:
        zone_info = ZONE_TYPE_MAP[key]
        
        # 상세주소로 변형 확인
        if detail and "variations" in zone_info:
            for var_zone, keywords in zone_info["variations"].items():
                for keyword in keywords:
                    if keyword in detail:
                        logger.info(f"📍 Zone variation found: {var_zone} (keyword: {keyword})")
                        return var_zone
        
        # 기본 용도지역 반환
        default = zone_info["default_zone"]
        logger.info(f"📍 Default zone: {default} for {sido} {sigungu} {dong}")
        return default
    
    # 폴백: 지역별 기본값
    logger.warning(f"⚠️ Zone not found for {sido} {sigungu} {dong}, using default")
    
    # 서울/광역시 → 제2종일반주거지역
    if any(x in sido for x in ["서울", "부산", "인천", "대구", "광주", "대전", "울산"]):
        return "제2종일반주거지역"
    
    # 경기도 신도시 → 제1종일반주거지역
    if "경기도" in sido and any(x in sigungu for x in ["분당구", "판교", "일산"]):
        return "제1종일반주거지역"
    
    # 그 외 → 제2종일반주거지역 (가장 일반적)
    return "제2종일반주거지역"


def convert_address_to_pnu(
    sido: str,
    sigungu: str,
    dong: str,
    jibun: str
) -> Optional[str]:
    """
    주소를 PNU 코드로 변환 (간이 버전)
    
    Args:
        sido: 시/도
        sigungu: 시/군/구
        dong: 읍/면/동
        jibun: 지번 (예: "680-11")
    
    Returns:
        PNU 코드 (19자리) 또는 None
    
    Note:
        실제 구현에서는 행정안전부 API 또는 DB 매핑 필요
        현재는 하드코딩된 매핑만 지원
    """
    # 지번 파싱
    if "-" in jibun:
        main, sub = jibun.split("-")
    else:
        main, sub = jibun, "0"
    
    main_padded = main.zfill(4)
    sub_padded = sub.zfill(4)
    
    # 주소별 PNU 매핑 (간이 버전)
    address_to_pnu_map = {
        ("서울특별시", "강남구", "역삼동", "680-11"): "1168010100106800011",
        ("서울특별시", "마포구", "성산동", "250-40"): "1144010800102500040",
        ("서울특별시", "관악구", "신림동", "1524-8"): "1162010100115240008",
        ("경기도", "성남시 분당구", "정자동", "100-1"): "4113510300101000001",
        ("부산광역시", "해운대구", "우동", "1500-1"): "2647010100115000001",
    }
    
    key = (sido, sigungu, dong, jibun)
    if key in address_to_pnu_map:
        pnu = address_to_pnu_map[key]
        logger.info(f"✅ PNU converted: {sido} {sigungu} {dong} {jibun} → {pnu}")
        return pnu
    
    logger.warning(f"⚠️ PNU conversion failed: {sido} {sigungu} {dong} {jibun}")
    return None


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    print("=" * 80)
    print("ZeroSite v37.0 - Parcel-Specific Data Test")
    print("=" * 80)
    
    # Test 1: PNU 조회
    print("\n[ Test 1: PNU-based Lookup ]")
    test_pnus = [
        "1168010100106800011",  # 강남구 역삼동 680-11
        "1162010100115240008",  # 관악구 신림동 1524-8
        "4113510300101000001",  # 성남시 분당구 정자동 100-1
    ]
    
    for pnu in test_pnus:
        data = get_parcel_data(pnu)
        if data:
            print(f"\nPNU: {pnu}")
            print(f"  Address: {data['address']}")
            print(f"  Official Price: {data['official_land_price_per_sqm']:,}원/㎡")
            print(f"  Zone: {data['zone_type']}")
    
    # Test 2: 주소 기반 용도지역 조회
    print("\n\n[ Test 2: Address-based Zone Lookup ]")
    test_addresses = [
        ("서울특별시", "강남구", "역삼동", None),
        ("서울특별시", "관악구", "신림동", None),
        ("경기도", "성남시 분당구", "정자동", None),
        ("부산광역시", "해운대구", "우동", "센텀시티"),
    ]
    
    for sido, sigungu, dong, detail in test_addresses:
        zone = get_zone_by_region(sido, sigungu, dong, detail)
        print(f"\n{sido} {sigungu} {dong} {detail or ''}")
        print(f"  → Zone: {zone}")
    
    # Test 3: 주소 → PNU 변환
    print("\n\n[ Test 3: Address to PNU Conversion ]")
    test_conversions = [
        ("서울특별시", "강남구", "역삼동", "680-11"),
        ("부산광역시", "해운대구", "우동", "1500-1"),
    ]
    
    for sido, sigungu, dong, jibun in test_conversions:
        pnu = convert_address_to_pnu(sido, sigungu, dong, jibun)
        print(f"\n{sido} {sigungu} {dong} {jibun}")
        print(f"  → PNU: {pnu or 'Not found'}")
    
    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)
