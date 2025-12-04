"""
ZeroSite v9.0 - Integration Tests
==================================

전체 파이프라인 통합 테스트

테스트 시나리오:
1. Orchestrator 초기화
2. Raw Data 입력
3. 전체 엔진 실행
4. StandardAnalysisOutput 검증
5. KeyError 제로 확인

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.0
"""

import pytest
import asyncio
from typing import Dict, Any

from app.engines_v9.orchestrator_v9_0 import EngineOrchestratorV90
from app.models_v9.standard_schema_v9_0 import (
    StandardAnalysisOutput,
    DecisionType,
    ProjectGrade
)


# Mock Kakao API Key (테스트용)
MOCK_KAKAO_API_KEY = "test_kakao_api_key_mock"


def get_test_raw_data() -> Dict[str, Any]:
    """테스트용 원시 데이터"""
    return {
        # 토지 기본 정보
        "address": "서울특별시 마포구 월드컵북로 120",
        "land_area": 660.0,
        "zone_type": "제3종일반주거지역",
        "land_appraisal_price": 5000000,  # 원/m²
        "building_coverage_ratio": 55.0,  # %
        "floor_area_ratio": 250.0,  # %
        "height_limit": 35.0,  # m
        
        # 좌표
        "latitude": 37.5666,
        "longitude": 126.9784,
        
        # 프로젝트 정보
        "unit_count": 33,
        "unit_type_distribution": {
            "59A": 20,
            "84B": 13
        },
        
        # 재무 정보
        "construction_cost_per_sqm": 2800000,  # 원/m²
    }


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Orchestrator 초기화 테스트"""
    orchestrator = EngineOrchestratorV90(kakao_api_key=MOCK_KAKAO_API_KEY)
    
    assert orchestrator is not None
    assert orchestrator.normalizer is not None
    assert orchestrator.gis_engine is not None
    assert orchestrator.financial_engine is not None
    assert orchestrator.lh_engine is not None
    assert orchestrator.risk_engine is not None
    assert orchestrator.demand_engine is not None
    
    print("✅ Orchestrator 초기화 성공")


@pytest.mark.asyncio
async def test_full_pipeline():
    """전체 파이프라인 테스트"""
    # 1. Orchestrator 생성
    orchestrator = EngineOrchestratorV90(kakao_api_key=MOCK_KAKAO_API_KEY)
    
    # 2. Raw Data 준비
    raw_data = get_test_raw_data()
    
    # 3. 종합 분석 실행 (KeyError 발생 시 실패)
    try:
        result = await orchestrator.analyze_comprehensive(raw_data)
    except KeyError as e:
        pytest.fail(f"❌ KeyError 발생: {e}")
    except Exception as e:
        pytest.fail(f"❌ 예외 발생: {e}")
    
    # 4. 결과 검증
    assert isinstance(result, StandardAnalysisOutput)
    assert result.analysis_id is not None
    assert result.version == "v9.0"
    assert result.timestamp is not None
    
    # 5. 각 엔진 결과 검증
    assert result.site_info is not None
    assert result.gis_result is not None
    assert result.financial_result is not None
    assert result.lh_scores is not None
    assert result.risk_assessment is not None
    assert result.demand_result is not None
    assert result.final_recommendation is not None
    
    # 6. 점수 범위 검증
    assert 0 <= result.lh_scores.total_score <= 110
    assert 0 <= result.lh_scores.location_score <= 35
    assert 0 <= result.lh_scores.scale_score <= 20
    assert 0 <= result.lh_scores.business_score <= 40
    assert 0 <= result.lh_scores.regulation_score <= 15
    
    # 7. 리스크 검증
    assert result.risk_assessment.total_items == 25
    assert result.risk_assessment.overall_risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    # 8. 최종 결정 검증
    assert result.final_recommendation.decision in [
        DecisionType.PROCEED,
        DecisionType.PROCEED_WITH_CONDITIONS,
        DecisionType.REVISE,
        DecisionType.NOGO
    ]
    assert 0 <= result.final_recommendation.confidence_level <= 100
    
    # 9. 처리 시간 검증
    assert result.processing_time_seconds > 0
    
    print("✅ 전체 파이프라인 테스트 성공")
    print(f"   Analysis ID: {result.analysis_id}")
    print(f"   LH Score: {result.lh_scores.total_score:.1f}/110 (Grade: {result.lh_scores.grade.value})")
    print(f"   Risk Level: {result.risk_assessment.overall_risk_level}")
    print(f"   Decision: {result.final_recommendation.decision.value}")
    print(f"   Confidence: {result.final_recommendation.confidence_level:.0f}%")
    print(f"   Processing Time: {result.processing_time_seconds:.2f}s")


@pytest.mark.asyncio
async def test_keyerror_zero():
    """KeyError 제로 테스트"""
    orchestrator = EngineOrchestratorV90(kakao_api_key=MOCK_KAKAO_API_KEY)
    
    # 불완전한 데이터 (많은 필드 누락)
    incomplete_data = {
        "address": "서울시 강남구",
        "land_area": 500.0,
        # 나머지 필드 누락
    }
    
    try:
        result = await orchestrator.analyze_comprehensive(incomplete_data)
        
        # KeyError 없이 완료되어야 함
        assert result is not None
        assert result.analysis_id is not None
        
        print("✅ KeyError 제로 테스트 성공 (불완전한 데이터 처리 완료)")
        
    except KeyError as e:
        pytest.fail(f"❌ KeyError 발생 (제로 달성 실패): {e}")


@pytest.mark.asyncio
async def test_multiple_scenarios():
    """여러 시나리오 테스트"""
    orchestrator = EngineOrchestratorV90(kakao_api_key=MOCK_KAKAO_API_KEY)
    
    scenarios = [
        # 시나리오 1: 대규모 프로젝트 (LH_LINKED)
        {
            "name": "대규모 (100세대)",
            "data": {
                **get_test_raw_data(),
                "unit_count": 100,
                "land_area": 2000.0,
                "floor_area_ratio": 300.0
            }
        },
        # 시나리오 2: 소규모 프로젝트 (STANDARD)
        {
            "name": "소규모 (20세대)",
            "data": {
                **get_test_raw_data(),
                "unit_count": 20,
                "land_area": 400.0,
                "floor_area_ratio": 200.0
            }
        },
        # 시나리오 3: 용도지역 부적합
        {
            "name": "용도지역 부적합",
            "data": {
                **get_test_raw_data(),
                "zone_type": "공업지역"
            }
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        try:
            result = await orchestrator.analyze_comprehensive(scenario["data"])
            results.append({
                "name": scenario["name"],
                "lh_score": result.lh_scores.total_score,
                "risk_level": result.risk_assessment.overall_risk_level,
                "decision": result.final_recommendation.decision.value
            })
        except Exception as e:
            pytest.fail(f"❌ 시나리오 '{scenario['name']}' 실패: {e}")
    
    # 결과 출력
    print("✅ 여러 시나리오 테스트 성공")
    for r in results:
        print(f"   [{r['name']}] LH {r['lh_score']:.1f}, Risk {r['risk_level']}, Decision {r['decision']}")


def test_sync_wrapper():
    """비동기 테스트를 동기로 실행"""
    asyncio.run(test_orchestrator_initialization())
    asyncio.run(test_full_pipeline())
    asyncio.run(test_keyerror_zero())
    asyncio.run(test_multiple_scenarios())


if __name__ == "__main__":
    print("="*80)
    print("ZeroSite v9.0 - Integration Tests")
    print("="*80)
    
    # 테스트 실행
    test_sync_wrapper()
    
    print("\n" + "="*80)
    print("✅ 모든 통합 테스트 통과!")
    print("="*80)
