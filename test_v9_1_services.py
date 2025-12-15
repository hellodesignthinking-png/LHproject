"""
ZeroSite v9.1 Auto Input Services Integration Test

Tests all three v9.1 automation services:
1. AddressResolverV9 - Address to coordinate conversion
2. ZoningAutoMapperV9 - Zoning standards lookup
3. UnitEstimatorV9 - Unit count estimation

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.1
"""

import asyncio
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services_v9.address_resolver_v9_0 import get_address_resolver
from app.services_v9.zoning_auto_mapper_v9_0 import get_zoning_mapper
from app.services_v9.unit_estimator_v9_0 import get_unit_estimator


async def test_address_resolver():
    """Test AddressResolverV9"""
    print("\n" + "="*80)
    print("TEST 1: AddressResolverV9 - 주소 자동 변환")
    print("="*80)
    
    resolver = get_address_resolver()
    
    # Test addresses
    test_addresses = [
        "서울 마포구 성산동 123-45",
        "서울특별시 강남구 테헤란로 123",
        "서울 송파구 잠실동 123"
    ]
    
    results = []
    
    for address in test_addresses:
        print(f"\n📍 테스트 주소: {address}")
        
        try:
            address_info = await resolver.resolve_address(address)
            
            if address_info:
                result = {
                    "input_address": address,
                    "road_address": address_info.road_address,
                    "parcel_address": address_info.parcel_address,
                    "latitude": address_info.latitude,
                    "longitude": address_info.longitude,
                    "legal_code": address_info.legal_code,
                    "status": "SUCCESS"
                }
                
                print(f"   ✅ 도로명: {address_info.road_address}")
                print(f"   ✅ 지번: {address_info.parcel_address}")
                print(f"   ✅ 좌표: ({address_info.latitude:.6f}, {address_info.longitude:.6f})")
                print(f"   ✅ 법정동코드: {address_info.legal_code}")
            else:
                result = {
                    "input_address": address,
                    "status": "FAILED"
                }
                print(f"   ❌ 주소 검색 실패")
            
            results.append(result)
        
        except Exception as e:
            result = {
                "input_address": address,
                "error": str(e),
                "status": "ERROR"
            }
            results.append(result)
            print(f"   ❌ 오류 발생: {e}")
    
    # Summary
    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    print(f"\n{'='*80}")
    print(f"AddressResolverV9 테스트 완료: {success_count}/{len(test_addresses)} 성공")
    print(f"{'='*80}")
    
    return results


def test_zoning_mapper():
    """Test ZoningAutoMapperV9"""
    print("\n" + "="*80)
    print("TEST 2: ZoningAutoMapperV9 - 용도지역 자동 설정")
    print("="*80)
    
    mapper = get_zoning_mapper()
    
    # Test zone types
    test_zones = [
        "제3종일반주거지역",
        "3종일반",  # 별칭
        "준주거지역",
        "중심상업지역",
        "준공업지역"
    ]
    
    results = []
    
    for zone_type in test_zones:
        print(f"\n📐 테스트 용도지역: {zone_type}")
        
        try:
            standards = mapper.get_zoning_standards(zone_type)
            
            if standards:
                result = {
                    "input_zone": zone_type,
                    "zone_type": standards.zone_type,
                    "building_coverage_ratio": standards.building_coverage_ratio,
                    "floor_area_ratio": standards.floor_area_ratio,
                    "parking_ratio": standards.parking_ratio,
                    "description": standards.description,
                    "status": "SUCCESS"
                }
                
                print(f"   ✅ 정규명: {standards.zone_type}")
                print(f"   ✅ 건폐율: {standards.building_coverage_ratio}%")
                print(f"   ✅ 용적률: {standards.floor_area_ratio}%")
                print(f"   ✅ 주차비율: {standards.parking_ratio}대/세대")
                print(f"   ✅ 설명: {standards.description}")
            else:
                result = {
                    "input_zone": zone_type,
                    "status": "FAILED"
                }
                print(f"   ❌ 용도지역 조회 실패")
            
            results.append(result)
        
        except Exception as e:
            result = {
                "input_zone": zone_type,
                "error": str(e),
                "status": "ERROR"
            }
            results.append(result)
            print(f"   ❌ 오류 발생: {e}")
    
    # Summary
    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    print(f"\n{'='*80}")
    print(f"ZoningAutoMapperV9 테스트 완료: {success_count}/{len(test_zones)} 성공")
    print(f"{'='*80}")
    
    return results


def test_unit_estimator():
    """Test UnitEstimatorV9"""
    print("\n" + "="*80)
    print("TEST 3: UnitEstimatorV9 - 세대수 자동 계산")
    print("="*80)
    
    estimator = get_unit_estimator()
    
    # Test scenarios
    test_cases = [
        {
            "name": "중규모 제3종일반주거지역",
            "land_area": 1000.0,
            "floor_area_ratio": 300.0,
            "building_coverage_ratio": 50.0
        },
        {
            "name": "소규모 제2종일반주거지역",
            "land_area": 660.0,
            "floor_area_ratio": 250.0,
            "building_coverage_ratio": 60.0
        },
        {
            "name": "대규모 준주거지역",
            "land_area": 2000.0,
            "floor_area_ratio": 500.0,
            "building_coverage_ratio": 70.0
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🏢 테스트 케이스: {test_case['name']}")
        print(f"   대지면적: {test_case['land_area']:.2f} m²")
        print(f"   용적률: {test_case['floor_area_ratio']:.1f}%")
        print(f"   건폐율: {test_case['building_coverage_ratio']:.1f}%")
        
        try:
            estimate = estimator.estimate_units(
                land_area=test_case["land_area"],
                floor_area_ratio=test_case["floor_area_ratio"],
                building_coverage_ratio=test_case["building_coverage_ratio"]
            )
            
            result = {
                "test_case": test_case["name"],
                "input": test_case,
                "total_units": estimate.total_units,
                "total_gfa": estimate.total_gfa,
                "residential_gfa": estimate.residential_gfa,
                "floors": estimate.floors,
                "units_per_floor": estimate.units_per_floor,
                "parking_spaces": estimate.parking_spaces,
                "unit_type_distribution": estimate.unit_type_distribution,
                "status": "SUCCESS"
            }
            
            print(f"   ✅ 총 세대수: {estimate.total_units}세대")
            print(f"   ✅ 연면적: {estimate.total_gfa:.2f} m²")
            print(f"   ✅ 주거 전용 면적: {estimate.residential_gfa:.2f} m²")
            print(f"   ✅ 층수: {estimate.floors}층")
            print(f"   ✅ 층별 세대수: {estimate.units_per_floor}세대/층")
            print(f"   ✅ 주차 대수: {estimate.parking_spaces}대")
            print(f"   ✅ 세대 유형 배분: {estimate.unit_type_distribution}")
            
            # Validation
            validation = estimator.validate_estimate(estimate)
            if validation["is_valid"]:
                print(f"   ✅ 검증 통과")
            else:
                print(f"   ⚠️ 검증 경고: {validation}")
            
            results.append(result)
        
        except Exception as e:
            result = {
                "test_case": test_case["name"],
                "input": test_case,
                "error": str(e),
                "status": "ERROR"
            }
            results.append(result)
            print(f"   ❌ 오류 발생: {e}")
    
    # Summary
    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    print(f"\n{'='*80}")
    print(f"UnitEstimatorV9 테스트 완료: {success_count}/{len(test_cases)} 성공")
    print(f"{'='*80}")
    
    return results


async def test_integrated_flow():
    """Test integrated flow: Address → Zoning → Units"""
    print("\n" + "="*80)
    print("TEST 4: 통합 플로우 - 주소 → 용도지역 → 세대수")
    print("="*80)
    
    resolver = get_address_resolver()
    mapper = get_zoning_mapper()
    estimator = get_unit_estimator()
    
    # Test scenario: 최소 입력 4개
    test_input = {
        "address": "서울특별시 강남구 테헤란로 123",
        "land_area": 1000.0,
        "zone_type": "제3종일반주거지역",
        "total_land_price": 5000000000.0  # 50억원
    }
    
    print(f"\n📝 사용자 입력 (4개):")
    print(f"   주소: {test_input['address']}")
    print(f"   대지면적: {test_input['land_area']} m²")
    print(f"   용도지역: {test_input['zone_type']}")
    print(f"   토지가격: {test_input['total_land_price']:,}원")
    
    result = {
        "input": test_input,
        "auto_calculated": {}
    }
    
    try:
        # Step 1: Address Resolution
        print(f"\n📍 Step 1: 주소 자동 변환")
        address_info = await resolver.resolve_address(test_input["address"])
        
        if address_info:
            result["auto_calculated"]["latitude"] = address_info.latitude
            result["auto_calculated"]["longitude"] = address_info.longitude
            result["auto_calculated"]["road_address"] = address_info.road_address
            
            print(f"   ✅ 좌표: ({address_info.latitude:.6f}, {address_info.longitude:.6f})")
        else:
            print(f"   ❌ 주소 변환 실패")
            result["status"] = "FAILED"
            return result
        
        # Step 2: Zoning Standards
        print(f"\n📐 Step 2: 용도지역 기준 자동 설정")
        standards = mapper.get_zoning_standards(test_input["zone_type"])
        
        if standards:
            result["auto_calculated"]["building_coverage_ratio"] = standards.building_coverage_ratio
            result["auto_calculated"]["floor_area_ratio"] = standards.floor_area_ratio
            result["auto_calculated"]["parking_ratio"] = standards.parking_ratio
            
            print(f"   ✅ 건폐율: {standards.building_coverage_ratio}%")
            print(f"   ✅ 용적률: {standards.floor_area_ratio}%")
        else:
            print(f"   ❌ 용도지역 조회 실패")
            result["status"] = "FAILED"
            return result
        
        # Step 3: Unit Estimation
        print(f"\n🏢 Step 3: 세대수 자동 계산")
        estimate = estimator.estimate_units(
            land_area=test_input["land_area"],
            floor_area_ratio=standards.floor_area_ratio,
            building_coverage_ratio=standards.building_coverage_ratio,
            parking_ratio=standards.parking_ratio
        )
        
        result["auto_calculated"]["unit_count"] = estimate.total_units
        result["auto_calculated"]["floors"] = estimate.floors
        result["auto_calculated"]["parking_spaces"] = estimate.parking_spaces
        result["auto_calculated"]["total_gfa"] = estimate.total_gfa
        
        print(f"   ✅ 세대수: {estimate.total_units}세대")
        print(f"   ✅ 층수: {estimate.floors}층")
        print(f"   ✅ 주차대수: {estimate.parking_spaces}대")
        
        result["status"] = "SUCCESS"
        
        # Final Summary
        print(f"\n{'='*80}")
        print(f"✅ 통합 플로우 성공")
        print(f"{'='*80}")
        print(f"\n📊 최종 결과:")
        print(f"   사용자 입력: 4개 필드")
        print(f"   자동 계산: {len(result['auto_calculated'])}개 필드")
        print(f"\n자동 계산된 값:")
        for key, value in result["auto_calculated"].items():
            print(f"   - {key}: {value}")
        
        return result
    
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
        print(f"\n❌ 통합 플로우 실패: {e}")
        return result


async def main():
    """Run all tests"""
    print("="*80)
    print("ZeroSite v9.1 Auto Input Services - 통합 테스트")
    print("="*80)
    print(f"날짜: 2025-12-04")
    print(f"버전: v9.1")
    print("="*80)
    
    all_results = {}
    
    try:
        # Test 1: AddressResolver
        all_results["address_resolver"] = await test_address_resolver()
        
        # Test 2: ZoningMapper
        all_results["zoning_mapper"] = test_zoning_mapper()
        
        # Test 3: UnitEstimator
        all_results["unit_estimator"] = test_unit_estimator()
        
        # Test 4: Integrated Flow
        all_results["integrated_flow"] = await test_integrated_flow()
        
        # Final Summary
        print("\n" + "="*80)
        print("전체 테스트 결과 요약")
        print("="*80)
        
        total_tests = 0
        total_success = 0
        
        for test_name, results in all_results.items():
            if isinstance(results, list):
                test_count = len(results)
                success_count = sum(1 for r in results if r.get("status") == "SUCCESS")
            elif isinstance(results, dict):
                test_count = 1
                success_count = 1 if results.get("status") == "SUCCESS" else 0
            else:
                continue
            
            total_tests += test_count
            total_success += success_count
            
            status_icon = "✅" if success_count == test_count else "⚠️"
            print(f"{status_icon} {test_name}: {success_count}/{test_count} 성공")
        
        success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{'='*80}")
        print(f"전체: {total_success}/{total_tests} 성공 ({success_rate:.1f}%)")
        print(f"{'='*80}")
        
        # Save results to JSON
        output_file = "test_v9_1_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 테스트 결과 저장: {output_file}")
        
        return success_rate >= 80.0
    
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
