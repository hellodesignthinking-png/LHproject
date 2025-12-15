#!/usr/bin/env python3
"""
ZeroSite v40.2 - LH 심사예측 통합 테스트
LH AI Judge Integration Test (End-to-End)

Test Steps:
1. Health Check - LH 엔진 상태 확인
2. Context 생성 - v40.2 분석 실행 (서울 관악구 신림동 1524-8)
3. LH 예측 실행 - 청년 주택 20세대 기준
4. 결과 검증 - 점수, 확률, 리스크, Factor, 제안 검증
5. 시나리오 비교 - A/B/C 합격 확률 비교
6. 캐시 조회 - 저장된 예측 결과 재조회

Author: ZeroSite AI Development Team
Date: 2025-12-14
"""

import requests
import json
from typing import Dict, Any
import sys

# API Base URL
BASE_URL = "http://localhost:8001"

def print_section(title: str):
    """섹션 제목 출력"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_result(test_name: str, passed: bool, details: str = ""):
    """테스트 결과 출력"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"    {details}")

def test_lh_health_check() -> bool:
    """Test 1: LH 엔진 Health Check"""
    print_section("Test 1: LH 엔진 Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v40/lh-review/health", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # 검증
        passed = (
            data.get("status") == "healthy" and
            data.get("version") == "1.0.0" and
            data.get("model_type") == "Rule-Based (Baseline)"
        )
        
        print_result(
            "LH 엔진 Health Check",
            passed,
            f"Status: {data.get('status')}, Version: {data.get('version')}"
        )
        
        if passed:
            print(f"    Features: {', '.join(data.get('features', []))}")
        
        return passed
    
    except Exception as e:
        print_result("LH 엔진 Health Check", False, f"Error: {e}")
        return False

def test_create_context() -> str:
    """Test 2: v40.2 분석 Context 생성"""
    print_section("Test 2: v40.2 분석 Context 생성")
    
    try:
        # 서울 관악구 신림동 1524-8 (450.5㎡)
        payload = {
            "address": "서울특별시 관악구 신림동 1524-8",
            "land_area_sqm": 450.5
        }
        
        print(f"📍 주소: {payload['address']}")
        print(f"📏 면적: {payload['land_area_sqm']}㎡")
        
        response = requests.post(
            f"{BASE_URL}/api/v40.2/run-analysis",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        context_id = data.get("context_id")
        
        passed = bool(context_id)
        
        print_result(
            "Context 생성",
            passed,
            f"Context ID: {context_id}"
        )
        
        if passed:
            # 주요 데이터 출력
            appraisal = data.get("appraisal", {})
            print(f"    감정가: ₩{appraisal.get('appraised_land_value', 0):,.0f}")
            print(f"    용도지역: {appraisal.get('zone_type', 'N/A')}")
            print(f"    공시지가: ₩{appraisal.get('official_land_price_per_sqm', 0):,.0f}/㎡")
        
        return context_id if passed else None
    
    except Exception as e:
        print_result("Context 생성", False, f"Error: {e}")
        return None

def test_lh_prediction(context_id: str) -> Dict[str, Any]:
    """Test 3: LH 심사 예측 실행"""
    print_section("Test 3: LH 심사 예측 실행")
    
    try:
        payload = {
            "context_id": context_id,
            "housing_type": "청년",
            "target_units": 20
        }
        
        print(f"🏠 주택 유형: {payload['housing_type']}")
        print(f"🏘️ 목표 세대수: {payload['target_units']}세대")
        
        response = requests.post(
            f"{BASE_URL}/api/v40/lh-review/predict",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        # 기본 검증
        passed = (
            "predicted_score" in data and
            "pass_probability" in data and
            "risk_level" in data and
            "factors" in data
        )
        
        print_result("LH 예측 실행", passed)
        
        if passed:
            print(f"\n📊 예측 결과:")
            print(f"    종합 점수: {data.get('predicted_score')}/100")
            print(f"    합격 확률: {data.get('pass_probability')}%")
            print(f"    리스크: {data.get('risk_level')}")
        
        return data if passed else None
    
    except Exception as e:
        print_result("LH 예측 실행", False, f"Error: {e}")
        return None

def test_factor_analysis(prediction_data: Dict[str, Any]) -> bool:
    """Test 4: Factor 분석 검증"""
    print_section("Test 4: Factor 분석 검증")
    
    try:
        factors = prediction_data.get("factors", [])
        
        # 6개 Factor 존재 여부
        expected_factors = [
            "입지 점수",
            "용도지역 적합성",
            "토지가격 합리성",
            "용적률/건폐율 실현가능성",
            "리스크 수준",
            "시나리오 안정성"
        ]
        
        passed = len(factors) == 6
        
        print_result(
            "Factor 개수",
            passed,
            f"{len(factors)}/6개 Factor 존재"
        )
        
        if passed:
            print(f"\n📋 Factor별 점수:")
            for factor in factors:
                name = factor.get("factor_name")
                score = factor.get("score")
                impact = factor.get("impact")
                reason = factor.get("reason")
                weight = factor.get("weight")
                
                print(f"    • {name}: {score}/100 ({impact})")
                print(f"      가중치: {weight*100:.0f}% | {reason}")
        
        # 각 Factor에 필수 필드 존재 여부
        all_factors_valid = all(
            "factor_name" in f and
            "score" in f and
            "impact" in f and
            "reason" in f and
            "weight" in f
            for f in factors
        )
        
        print_result(
            "Factor 필드 검증",
            all_factors_valid,
            "모든 Factor에 필수 필드 존재" if all_factors_valid else "일부 Factor 필드 누락"
        )
        
        return passed and all_factors_valid
    
    except Exception as e:
        print_result("Factor 분석 검증", False, f"Error: {e}")
        return False

def test_suggestions(prediction_data: Dict[str, Any]) -> bool:
    """Test 5: 개선 제안 검증"""
    print_section("Test 5: 개선 제안 검증")
    
    try:
        suggestions = prediction_data.get("suggestions", [])
        
        passed = len(suggestions) > 0
        
        print_result(
            "개선 제안 생성",
            passed,
            f"{len(suggestions)}개 제안 생성됨"
        )
        
        if passed:
            print(f"\n💡 개선 제안:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"    {i}. {suggestion}")
        
        return passed
    
    except Exception as e:
        print_result("개선 제안 검증", False, f"Error: {e}")
        return False

def test_scenario_comparison(prediction_data: Dict[str, Any]) -> bool:
    """Test 6: 시나리오 A/B/C 비교 검증"""
    print_section("Test 6: 시나리오 A/B/C 비교 검증")
    
    try:
        scenario_comparison = prediction_data.get("scenario_comparison", [])
        
        passed = len(scenario_comparison) >= 1  # 최소 1개 시나리오
        
        print_result(
            "시나리오 비교",
            passed,
            f"{len(scenario_comparison)}개 시나리오 예측됨"
        )
        
        if passed:
            print(f"\n🎯 시나리오별 합격 확률:")
            for scenario in scenario_comparison:
                name = scenario.get("scenario_name")
                units = scenario.get("total_units")
                probability = scenario.get("pass_probability")
                recommended = scenario.get("is_recommended")
                
                marker = "⭐ 추천" if recommended else ""
                print(f"    • {name}: {probability}% ({units}세대) {marker}")
        
        # 추천 시나리오 존재 여부
        has_recommended = any(s.get("is_recommended") for s in scenario_comparison)
        
        print_result(
            "추천 시나리오",
            has_recommended,
            "추천 시나리오 존재" if has_recommended else "추천 시나리오 없음"
        )
        
        return passed
    
    except Exception as e:
        print_result("시나리오 비교 검증", False, f"Error: {e}")
        return False

def test_cached_retrieval(context_id: str) -> bool:
    """Test 7: 캐시된 예측 결과 조회"""
    print_section("Test 7: 캐시된 예측 결과 조회")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v40/lh-review/context/{context_id}",
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        
        passed = (
            data.get("context_id") == context_id and
            "predicted_score" in data
        )
        
        print_result(
            "캐시 조회",
            passed,
            f"Context: {context_id[:8]}... (점수: {data.get('predicted_score')}/100)"
        )
        
        return passed
    
    except Exception as e:
        print_result("캐시 조회", False, f"Error: {e}")
        return False

def test_housing_types() -> bool:
    """Test 8: LH 주택 유형 조회"""
    print_section("Test 8: LH 주택 유형 조회")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v40/lh-review/housing-types", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        housing_types = data.get("housing_types", {})
        
        passed = len(housing_types) == 7  # LH 공식 7개 유형
        
        print_result(
            "주택 유형 조회",
            passed,
            f"{len(housing_types)}/7개 유형"
        )
        
        if passed:
            print(f"\n🏠 LH 주택 유형:")
            for type_name, info in housing_types.items():
                print(f"    • {type_name}: {info.get('size')} ({info.get('평')})")
        
        return passed
    
    except Exception as e:
        print_result("주택 유형 조회", False, f"Error: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("="*60)
    print("  ZeroSite v40.2 - LH 심사예측 통합 테스트")
    print("  LH AI Judge Integration Test (End-to-End)")
    print("="*60)
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"🔍 Testing LH 심사예측 API...")
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_lh_health_check()))
    
    # Test 2: Context 생성
    context_id = test_create_context()
    results.append(("Context 생성", bool(context_id)))
    
    if not context_id:
        print("\n❌ Context 생성 실패 - 이후 테스트 중단")
        sys.exit(1)
    
    # Test 3: LH 예측 실행
    prediction_data = test_lh_prediction(context_id)
    results.append(("LH 예측 실행", bool(prediction_data)))
    
    if not prediction_data:
        print("\n❌ LH 예측 실패 - 이후 테스트 중단")
        sys.exit(1)
    
    # Test 4: Factor 분석
    results.append(("Factor 분석", test_factor_analysis(prediction_data)))
    
    # Test 5: 개선 제안
    results.append(("개선 제안", test_suggestions(prediction_data)))
    
    # Test 6: 시나리오 비교
    results.append(("시나리오 비교", test_scenario_comparison(prediction_data)))
    
    # Test 7: 캐시 조회
    results.append(("캐시 조회", test_cached_retrieval(context_id)))
    
    # Test 8: 주택 유형 조회
    results.append(("주택 유형 조회", test_housing_types()))
    
    # 최종 결과
    print_section("최종 결과")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\n📊 테스트 결과: {passed_count}/{total_count} 통과")
    
    for test_name, passed in results:
        status = "✅" if passed else "❌"
        print(f"    {status} {test_name}")
    
    if passed_count == total_count:
        print("\n✅ 모든 테스트 통과! LH 심사예측 API가 정상 작동합니다.")
        print("\n🔗 수동 테스트 URL:")
        print(f"    Health Check: {BASE_URL}/api/v40/lh-review/health")
        print(f"    주택 유형: {BASE_URL}/api/v40/lh-review/housing-types")
        print(f"    Factor 가중치: {BASE_URL}/api/v40/lh-review/factors/weights")
        print(f"    API 문서: {BASE_URL}/docs#/LH%20%EC%8B%AC%EC%82%AC%EC%98%88%EC%B8%A1%20(AI%20Judge)")
        return 0
    else:
        print(f"\n❌ {total_count - passed_count}개 테스트 실패")
        return 1

if __name__ == "__main__":
    sys.exit(main())
