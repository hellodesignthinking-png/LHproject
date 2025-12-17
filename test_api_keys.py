#!/usr/bin/env python3
"""
API 키 연동 테스트 스크립트
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, '/home/user/LHproject')

from app.services.land_data_service import LandDataService

def main():
    print("=" * 60)
    print("🔑 ZeroSite v3.4 - API 키 연동 테스트")
    print("=" * 60)
    print()

    # 서비스 초기화
    service = LandDataService()
    print()

    # 테스트 주소
    test_address = "서울특별시 강남구 역삼동 858"
    print(f"📍 테스트 주소: {test_address}")
    print()

    # 데이터 조회
    print("🔄 토지 데이터 조회 중...")
    print()

    result = service.fetch_all_by_address(test_address)

    print()
    print("=" * 60)
    print("📊 조회 결과")
    print("=" * 60)
    print()

    if result["success"]:
        print(f"✅ 조회 성공!")
        print(f"📦 데이터 출처: {result.get('data_source', 'unknown')}")
        print()

        if result.get('data_source') == 'mock':
            print("⚠️  경고: Mock 데이터 사용중")
            print("   → API 연결에 실패하여 테스트 데이터를 반환합니다")
            if 'warning' in result:
                print(f"   → {result['warning']}")
            if 'api_key_status' in result:
                print("\n   API 키 상태:")
                for key, status in result['api_key_status'].items():
                    print(f"   - {key}: {status}")
        else:
            print("✅ 실제 API 데이터 사용중")

        print()
        print("📋 기본 정보:")
        basic = result.get("basic_info")
        if basic:
            print(f"   - PNU: {basic.pnu}")
            print(f"   - 면적: {basic.area:,.2f} ㎡ ({basic.area/3.3058:.1f} 평)")
            print(f"   - 지목: {basic.land_category}")
            print(f"   - 용도지역: {basic.land_use_zone}")
            print(f"   - 이용상황: {basic.land_use_situation}")
            print(f"   - 도로접면: {basic.road_side}")
            print(f"   - 지형형상: {basic.terrain_shape}")

        print()
        print("💰 가격 정보:")
        price = result.get("price_info")
        if price:
            print(f"   - 개별공시지가: {price.official_price:,} 원/㎡")
            print(f"   - 총 공시지가: {price.total_price:,} 원 ({price.total_price/100000000:.2f} 억원)")
            print(f"   - 기준년도: {price.base_year}")

        print()
        print("📏 규제 정보:")
        regulation = result.get("regulation_info")
        if regulation:
            print(f"   - 용도지역: {regulation.use_zone}")
            print(f"   - 용적률: {regulation.floor_area_ratio}%")
            print(f"   - 건폐율: {regulation.building_coverage_ratio}%")
            if regulation.regulations:
                print(f"   - 규제: {', '.join(regulation.regulations)}")

        print()
        print(f"📈 거래사례: {len(result.get('transactions', []))}건")

        # AppraisalContext 변환 테스트
        print()
        print("🔄 AppraisalContext 변환 테스트...")
        appraisal = service.to_appraisal_context(result)
        calc = appraisal.get('calculation', {})
        print(f"   - 감정평가액: {calc.get('final_appraised_total', 0):,} 원")
        print(f"   - 신뢰도: {calc.get('confidence_level', 'N/A')}")

    else:
        print(f"❌ 조회 실패")
        print(f"   오류: {result.get('error', 'Unknown error')}")

    print()
    print("=" * 60)
    print("✅ 테스트 완료")
    print("=" * 60)

if __name__ == "__main__":
    main()
