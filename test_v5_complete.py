"""
ZeroSite Land Report v5.0 - 전체 시스템 테스트
ZeroSite

모든 핵심 기능이 정상 작동하는지 검증합니다.
"""

import asyncio
import json
from typing import Dict, Any

# 테스트 결과 저장
test_results = []


def test_result(test_name: str, passed: bool, message: str = ""):
    """테스트 결과 기록"""
    status = "✅ PASS" if passed else "❌ FAIL"
    result = f"{status} | {test_name}"
    if message:
        result += f" | {message}"
    test_results.append((test_name, passed, message))
    print(result)


async def test_type_demand_scores():
    """[1] 유형별 수요점수 독립 계산 테스트"""
    print("\n" + "="*60)
    print("TEST 1: 유형별 수요점수 독립 계산")
    print("="*60)
    
    from app.services.analysis_engine import AnalysisEngine
    from app.schemas import LandAnalysisRequest, UnitType, Coordinates, DemographicInfo
    
    try:
        engine = AnalysisEngine()
        
        # 테스트용 데이터 생성
        test_accessibility = {
            "accessibility_score": 75,
            "nearest_subway_distance": 450,
            "nearest_school_distance": 350,
            "nearest_hospital_distance": 600
        }
        
        test_demographic = DemographicInfo(
            population=50000,
            youth_ratio=30.0,
            elderly_ratio=12.0,
            household_count=25000
        )
        
        test_coords = Coordinates(latitude=37.5665, longitude=126.9780)
        
        from app.utils.calculations import BuildingCalculator
        from app.schemas import ZoneInfo
        
        zone_info = ZoneInfo(
            zone_type="제2종일반주거지역",
            building_coverage_ratio=60,
            floor_area_ratio=200
        )
        
        calculator = BuildingCalculator()
        building_capacity = calculator.calculate_building_capacity(
            land_area=500,
            zone_info=zone_info,
            unit_type=UnitType.YOUTH
        )
        
        # 유형별 점수 계산
        scores = engine._calculate_type_demand_scores(
            demographic_info=test_demographic,
            accessibility=test_accessibility,
            coordinates=test_coords,
            building_capacity=building_capacity,
            zone_info=zone_info
        )
        
        # 검증 1: 5개 유형 모두 점수 존재
        expected_types = ["청년", "신혼·신생아 I", "신혼·신생아 II", "다자녀", "고령자"]
        all_types_present = all(t in scores for t in expected_types)
        test_result("유형별 점수 - 5개 유형 존재", all_types_present)
        
        # 검증 2: 모든 점수가 서로 다른 값
        unique_scores = len(set(scores.values()))
        scores_are_unique = unique_scores == len(scores)
        test_result(
            "유형별 점수 - 독립성 (서로 다른 값)",
            scores_are_unique,
            f"고유 점수 개수: {unique_scores}/{len(scores)}"
        )
        
        # 검증 3: 점수 범위 (0-100)
        valid_range = all(0 <= score <= 100 for score in scores.values())
        test_result("유형별 점수 - 유효 범위 (0-100)", valid_range)
        
        # 점수 출력
        print("\n📊 계산된 유형별 점수:")
        for unit_type, score in scores.items():
            print(f"  {unit_type}: {score:.1f}점")
        
        return all_types_present and scores_are_unique and valid_range
        
    except Exception as e:
        test_result("유형별 수요점수 계산", False, f"오류: {e}")
        return False


async def test_ai_auto_corrector():
    """[2] AI Auto Corrector 테스트"""
    print("\n" + "="*60)
    print("TEST 2: AI Auto Corrector")
    print("="*60)
    
    from app.services.ai_auto_corrector import get_auto_corrector
    
    try:
        corrector = get_auto_corrector()
        
        # 테스트 케이스 1: 주소 교정
        result = corrector.correct_input(
            address="서울  마포구   월드컵북로120 ",
            land_area=500.0000001
        )
        
        addr_corrected = result.corrected_address is not None
        area_corrected = result.corrected_land_area is not None
        
        test_result("AI Auto Corrector - 주소 교정", addr_corrected)
        test_result("AI Auto Corrector - 면적 정규화", area_corrected)
        
        print(f"\n원본 주소: '{result.original_address}'")
        print(f"교정 주소: '{result.corrected_address}'")
        print(f"원본 면적: {result.original_land_area}")
        print(f"교정 면적: {result.corrected_land_area}")
        print(f"교정 내역: {len(result.corrections_made)}건")
        
        return True
        
    except Exception as e:
        test_result("AI Auto Corrector", False, f"오류: {e}")
        return False


async def test_geo_optimizer():
    """[3] Geo Optimizer 테스트"""
    print("\n" + "="*60)
    print("TEST 3: Geo Optimizer")
    print("="*60)
    
    from app.services.geo_optimizer import get_geo_optimizer
    
    try:
        optimizer = get_geo_optimizer()
        
        test_accessibility = {
            "accessibility_score": 75,
            "nearest_subway_distance": 450,
            "nearest_school_distance": 350,
            "nearest_hospital_distance": 600
        }
        
        result = optimizer.optimize(
            latitude=37.5665,
            longitude=126.9780,
            address="서울특별시 마포구 월드컵북로 120",
            accessibility=test_accessibility
        )
        
        # 검증
        has_score = result.optimization_score > 0
        has_sites = len(result.recommended_sites) == 3
        has_strengths = len(result.current_site_strengths) > 0
        
        test_result("Geo Optimizer - 최적화 점수", has_score, f"{result.optimization_score:.1f}점")
        test_result("Geo Optimizer - 추천 사이트 3개", has_sites, f"{len(result.recommended_sites)}개")
        test_result("Geo Optimizer - 강점 분석", has_strengths)
        
        print(f"\n🗺️ 추천 대안 위치:")
        for idx, site in enumerate(result.recommended_sites, 1):
            print(f"  {idx}. {site.site_id} - {site.overall_score:.1f}점")
        
        return has_score and has_sites
        
    except Exception as e:
        test_result("Geo Optimizer", False, f"오류: {e}")
        return False


async def test_parcel_cluster():
    """[4] Parcel Cluster Analyzer 테스트"""
    print("\n" + "="*60)
    print("TEST 4: Parcel Cluster Analyzer")
    print("="*60)
    
    from app.services.parcel_cluster import get_parcel_analyzer
    
    try:
        analyzer = get_parcel_analyzer()
        
        test_parcels = [
            {
                "parcel_id": "P001",
                "address": "서울특별시 마포구 월드컵북로 120",
                "latitude": 37.5665,
                "longitude": 126.9780,
                "area": 450,
                "demand_score": 85.0,
                "building_capacity": 15
            },
            {
                "parcel_id": "P002",
                "address": "서울특별시 마포구 월드컵북로 121",
                "latitude": 37.5670,
                "longitude": 126.9785,
                "area": 500,
                "demand_score": 82.0,
                "building_capacity": 16
            }
        ]
        
        result = analyzer.analyze_parcels(
            parcels=test_parcels,
            target_area_min=500,
            target_area_max=2000
        )
        
        has_clusters = len(result.clusters) > 0
        has_stats = result.total_parcels == 2
        
        test_result("Parcel Cluster - 클러스터 생성", has_clusters, f"{len(result.clusters)}개")
        test_result("Parcel Cluster - 통계 계산", has_stats)
        
        print(f"\n🔗 클러스터 분석:")
        print(f"  총 필지: {result.total_parcels}개")
        print(f"  클러스터: {len(result.clusters)}개")
        
        return has_clusters
        
    except Exception as e:
        test_result("Parcel Cluster Analyzer", False, f"오류: {e}")
        return False


async def test_dashboard_builder():
    """[5] Dashboard Builder 테스트"""
    print("\n" + "="*60)
    print("TEST 5: Dashboard Builder")
    print("="*60)
    
    from app.services.dashboard_builder import get_dashboard_builder
    
    try:
        builder = get_dashboard_builder()
        
        test_result_data = {
            "type_demand_scores": {
                "청년": 88.5,
                "신혼·신생아 I": 85.2,
                "신혼·신생아 II": 83.7,
                "다자녀": 87.3,
                "고령자": 82.1
            },
            "grade_info": {
                "category_scores": {
                    "입지": 85.0,
                    "규모": 72.0,
                    "사업성": 80.0,
                    "법규": 90.0
                }
            },
            "coordinates": {
                "latitude": 37.5665,
                "longitude": 126.9780
            }
        }
        
        dashboard_data = builder.build_dashboard(test_result_data)
        
        has_charts = "type_demand_scores_radar" in dashboard_data.chart_configs
        has_maps = "main_location" in dashboard_data.map_data
        has_stats = dashboard_data.statistics["avg_demand_score"] > 0
        
        test_result("Dashboard Builder - 차트 생성", has_charts)
        test_result("Dashboard Builder - 지도 데이터", has_maps)
        test_result("Dashboard Builder - 통계 계산", has_stats)
        
        print(f"\n📊 생성된 대시보드 컴포넌트:")
        print(f"  차트: {len(dashboard_data.chart_configs)}개")
        print(f"  지도: {len(dashboard_data.map_data)}개")
        print(f"  평균 점수: {dashboard_data.statistics['avg_demand_score']:.1f}점")
        
        return has_charts and has_maps
        
    except Exception as e:
        test_result("Dashboard Builder", False, f"오류: {e}")
        return False


async def test_lh_notice_loader():
    """[6] LH Notice Loader 테스트"""
    print("\n" + "="*60)
    print("TEST 6: LH Notice Loader")
    print("="*60)
    
    from app.services.lh_notice_loader import get_notice_loader
    
    try:
        loader = get_notice_loader()
        
        # 파일명 파싱 테스트
        test_cases = [
            ("서울25-8차민간신축매입약정방식공고문.pdf", True, "2025", "8차"),
            ("경기24-3차_공고문_최종.pdf", True, "2024", "3차"),
            ("부산_2025_12차_공고.pdf", True, "2025", "12차"),
            ("invalid_filename.pdf", False, None, None)
        ]
        
        passed_count = 0
        for filename, should_parse, expected_year, expected_round in test_cases:
            result = loader.parse_filename(filename)
            
            if should_parse:
                if result and str(result["year"]) == expected_year and result["round"] == expected_round:
                    test_result(f"파일명 파싱 - {filename[:20]}...", True)
                    passed_count += 1
                else:
                    test_result(f"파일명 파싱 - {filename[:20]}...", False, f"예상: {expected_year}_{expected_round}")
            else:
                if result is None:
                    test_result(f"파일명 파싱 - {filename[:20]}...", True, "올바르게 거부됨")
                    passed_count += 1
                else:
                    test_result(f"파일명 파싱 - {filename[:20]}...", False, "유효하지 않은 파일을 허용함")
        
        print(f"\n📝 파일명 파싱 테스트: {passed_count}/{len(test_cases)} 통과")
        
        return passed_count == len(test_cases)
        
    except Exception as e:
        test_result("LH Notice Loader", False, f"오류: {e}")
        return False


async def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "="*80)
    print(" "*20 + "ZeroSite Land Report v5.0 - 전체 시스템 테스트")
    print(" "*25 + "ZeroSite")
    print("="*80)
    
    # 모든 테스트 실행
    test_functions = [
        test_type_demand_scores,
        test_ai_auto_corrector,
        test_geo_optimizer,
        test_parcel_cluster,
        test_dashboard_builder,
        test_lh_notice_loader
    ]
    
    results = []
    for test_func in test_functions:
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ 테스트 실패: {test_func.__name__} - {e}")
            results.append(False)
    
    # 최종 결과 출력
    print("\n" + "="*80)
    print(" "*30 + "📊 최종 테스트 결과")
    print("="*80)
    
    passed = sum(1 for r in test_results if r[1])
    total = len(test_results)
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n총 테스트: {total}개")
    print(f"통과: {passed}개 (✅)")
    print(f"실패: {total - passed}개 (❌)")
    print(f"통과율: {pass_rate:.1f}%\n")
    
    # 실패한 테스트 상세 정보
    failed_tests = [r for r in test_results if not r[1]]
    if failed_tests:
        print("❌ 실패한 테스트 목록:")
        for test_name, _, message in failed_tests:
            print(f"  • {test_name}")
            if message:
                print(f"    → {message}")
    else:
        print("✅ 모든 테스트 통과!")
    
    print("\n" + "="*80)
    
    # 서버 시작 안내
    print("\n📝 다음 단계:")
    print("  1. 서버 시작: uvicorn app.main:app --reload --port 8000")
    print("  2. 브라우저에서 http://localhost:8000 접속")
    print("  3. 단일 분석 테스트: 주소 입력 후 '토지 분석 시작' 클릭")
    print("  4. 다중 필지 테스트: '다중 필지 동시 분석' 섹션에서 주소 입력")
    print("  5. 지도 시각화 확인: Geo Optimization 섹션에서 Leaflet 지도 확인")
    print("  6. Debug JSON 확인: '개발자 디버그' 섹션에서 type_demand_scores 검증")
    
    print("\n🎯 ZeroSite Land Report v5.0 테스트 완료!")
    print("   ZeroSite - All Rights Reserved")
    print("="*80 + "\n")
    
    return pass_rate >= 80


if __name__ == "__main__":
    asyncio.run(run_all_tests())
