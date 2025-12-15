"""
간단한 API 테스트 스크립트
"""

import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from app.services.kakao_service import KakaoService
from app.services.land_regulation_service import LandRegulationService
from app.services.mois_service import MOISService
from app.schemas import Coordinates


async def test_kakao():
    """카카오 API 테스트"""
    print("\n" + "="*60)
    print("🗺️  카카오맵 API 테스트")
    print("="*60)
    
    service = KakaoService()
    
    # 주소 → 좌표 변환 테스트
    address = "서울특별시 강남구 역삼동 679"
    print(f"\n📍 주소: {address}")
    
    coords = await service.address_to_coordinates(address)
    if coords:
        print(f"✅ 좌표 변환 성공:")
        print(f"   위도: {coords.latitude}")
        print(f"   경도: {coords.longitude}")
        
        # 주변 시설 검색 테스트
        print("\n🔍 주변 시설 검색 중...")
        accessibility = await service.analyze_location_accessibility(coords)
        
        print(f"\n📊 접근성 분석 결과:")
        print(f"   접근성 점수: {accessibility['accessibility_score']}/100")
        print(f"   지하철역 거리: {int(accessibility['nearest_subway_distance'])}m")
        print(f"   대학교 거리: {int(accessibility['nearest_university_distance'])}m")
        
        if accessibility['subway_stations']:
            print(f"\n🚇 인근 지하철역:")
            for station in accessibility['subway_stations'][:3]:
                print(f"   - {station.name} ({int(station.distance)}m)")
        
        return coords
    else:
        print("❌ 좌표 변환 실패")
        return None


async def test_land_regulation(coords: Coordinates):
    """토지규제 API 테스트"""
    print("\n" + "="*60)
    print("🏗️  토지이용규제 API 테스트")
    print("="*60)
    
    service = LandRegulationService()
    
    # 용도지역 조회
    print("\n🔍 용도지역 조회 중...")
    zone_info = await service.get_zone_info(coords)
    
    if zone_info:
        print(f"\n✅ 용도지역 정보:")
        print(f"   용도지역: {zone_info.zone_type}")
        print(f"   건폐율: {zone_info.building_coverage_ratio}%")
        print(f"   용적률: {zone_info.floor_area_ratio}%")
        if zone_info.height_limit:
            print(f"   높이제한: {zone_info.height_limit}m")
    
    # 개발 제한 확인
    print("\n🔍 개발 제한사항 확인 중...")
    restrictions = await service.check_development_restrictions(coords)
    
    if restrictions:
        print(f"\n⚠️  개발 제한사항:")
        for r in restrictions:
            print(f"   - {r}")
    else:
        print(f"\n✅ 개발 제한사항 없음")


async def test_mois():
    """행정안전부 API 테스트"""
    print("\n" + "="*60)
    print("📊 행정안전부 인구통계 API 테스트")
    print("="*60)
    
    service = MOISService()
    
    address = "서울특별시 강남구"
    coords = Coordinates(latitude=37.5172, longitude=127.0473)
    
    print(f"\n📍 지역: {address}")
    print("🔍 인구통계 조회 중...")
    
    demographic = await service.analyze_demographics(address, coords)
    
    if demographic:
        print(f"\n✅ 인구통계 정보:")
        print(f"   총 인구: {demographic.total_population:,}명")
        print(f"   청년 인구 (20-39세): {demographic.youth_population:,}명")
        print(f"   청년 비율: {demographic.youth_ratio}%")
        print(f"   1인 가구: {demographic.single_households:,}가구")
        print(f"   1인 가구 비율: {demographic.single_household_ratio}%")


async def main():
    """메인 테스트 실행"""
    print("\n")
    print("🚀 LH 토지진단 시스템 API 테스트 시작")
    print("=" * 60)
    
    try:
        # 1. 카카오 API 테스트
        coords = await test_kakao()
        
        if coords:
            # 2. 토지규제 API 테스트
            await test_land_regulation(coords)
        
        # 3. 행정안전부 API 테스트
        await test_mois()
        
        print("\n" + "="*60)
        print("✅ 모든 API 테스트 완료")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
