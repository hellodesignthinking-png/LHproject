"""
ZeroSite v40.3 - LH 심사예측 API Router (Pipeline Lock Release)
LH 공공주택 사전심사 AI 예측 API

v40.3 업데이트:
- Context Protection 적용 (Appraisal READ-ONLY 강제)
- Pipeline 의존성 체크 강화
- 데이터 일관성 검증 추가

Features:
- POST /api/v40/lh-review/predict - LH 심사 예측 실행
- GET /api/v40/lh-review/context/{context_id} - 저장된 예측 결과 조회
- GET /api/v40/lh-review/health - Health Check

Author: ZeroSite AI Development Team
Date: 2025-12-14
Version: 1.0.1 (v40.3)
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional
import logging

from app.schemas_lh import (
    LHReviewRequest,
    LHReviewResponse,
    LHReviewHealthResponse
)
from app.services.lh_review_engine import lh_review_engine

# v40.2 Context Storage에서 데이터 가져오기
from app.api.v40.router_v40_2 import CONTEXT_STORAGE

# v40.3 Context Protection 추가
from app.core.context_protector import (
    ContextProtector,
    ensure_appraisal_first,
    check_pipeline_dependency
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v40/lh-review",
    tags=["LH 심사예측 (AI Judge)"]
)

# LH 예측 결과 저장소 (Context ID별 캐싱)
LH_PREDICTION_CACHE: Dict[str, LHReviewResponse] = {}


@router.get(
    "/health",
    response_model=LHReviewHealthResponse,
    summary="LH 심사예측 엔진 Health Check"
)
async def health_check():
    """
    LH 심사예측 엔진 상태 확인
    """
    return LHReviewHealthResponse(
        status="healthy",
        version="1.0.0",
        model_type="Rule-Based (Baseline)",
        features=[
            "Context-Based Read-Only",
            "6-Factor Weighted Scoring",
            "Explainable AI",
            "Scenario A/B/C Comparison",
            "Risk-Level Classification"
        ]
    )


@router.post(
    "/predict",
    response_model=LHReviewResponse,
    summary="LH 심사 예측 실행",
    description="""
    기존 분석 Context 기반으로 LH 공공주택 사전심사 합격 가능성 예측
    
    **입력 데이터:**
    - context_id: v40.2 분석 Context ID (필수)
    - housing_type: LH 주택 유형 (청년, 신혼·신생아 I/II, 다자녀, 고령자, 일반, 든든전세)
    - target_units: 목표 세대수
    
    **출력 데이터:**
    - predicted_score: 종합 점수 (0-100)
    - pass_probability: 합격 확률 (0-100%)
    - risk_level: 리스크 레벨 (LOW/MEDIUM/HIGH)
    - factors: 6개 평가 요소별 점수 및 근거
    - suggestions: 개선 제안
    - scenario_comparison: 시나리오 A/B/C 비교
    """
)
async def predict_lh_review(request: LHReviewRequest) -> LHReviewResponse:
    """
    LH 심사 예측 실행
    """
    logger.info(f"🔍 LH 심사예측 요청 - Context: {request.context_id}, 유형: {request.housing_type}")
    
    try:
        # Step 1: Context 데이터 조회 (v40.2 Storage에서)
        context_data = CONTEXT_STORAGE.get(request.context_id)
        if not context_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Context ID '{request.context_id}' not found. 먼저 /api/v40.2/run-analysis를 실행하세요."
            )
        
        logger.info(f"✅ Context 조회 성공 - {len(context_data)} 항목")
        
        # Step 1.5: v40.3 Pipeline Lock 검증
        # 감정평가 완료 상태 확인
        ensure_appraisal_first(context_data)
        
        # LH 심사예측을 위한 파이프라인 의존성 체크
        check_pipeline_dependency(context_data, "lh_review")
        
        # 데이터 일관성 검증
        consistency_result = ContextProtector.check_data_consistency(context_data)
        if consistency_result["status"] != "✅ ALL CONSISTENT":
            logger.warning(f"⚠️ 데이터 일관성 경고: {consistency_result}")
            # 경고만 출력, 실행은 계속
        
        logger.info("✅ v40.3 Pipeline Lock 검증 통과")
        
        # Step 2: 필수 데이터 검증 (appraisal, capacity, scenario 존재 여부)
        # (이미 check_pipeline_dependency에서 검증되었지만 추가 확인)
        required_keys = ["appraisal", "capacity", "scenario"]
        missing_keys = [key for key in required_keys if key not in context_data]
        if missing_keys:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Context에 필수 데이터 누락: {', '.join(missing_keys)}"
            )
        
        # Step 2.5: v40.2 context 구조 변환 (appraisal.zoning → top-level zoning)
        # v40.2의 appraisal 안에 zoning이 있으므로 추출
        if "zoning" in context_data.get("appraisal", {}):
            context_data["zoning"] = context_data["appraisal"]["zoning"]
        
        # risk 데이터가 없으면 기본값 설정
        if "risk" not in context_data:
            context_data["risk"] = {
                "overall_risk_level": "MEDIUM",
                "risk_factors": []
            }
        
        # Step 3: LH Review Engine 실행
        prediction_result = lh_review_engine.predict(
            context_data=context_data,
            housing_type=request.housing_type,
            target_units=request.target_units
        )
        
        # Step 4: 결과 캐싱 (재조회 가능하도록)
        LH_PREDICTION_CACHE[request.context_id] = prediction_result
        
        # Step 5: 결과를 Context에 저장 (보고서 생성용)
        if request.context_id in CONTEXT_STORAGE:
            CONTEXT_STORAGE[request.context_id]["lh_review"] = prediction_result.model_dump()
            logger.info(f"✅ LH Review 결과를 Context에 저장 완료")
        
        logger.info(
            f"✅ LH 예측 완료 - 점수: {prediction_result.predicted_score}/100, "
            f"확률: {prediction_result.pass_probability}%, 리스크: {prediction_result.risk_level}"
        )
        
        return prediction_result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ LH 심사예측 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LH 심사예측 처리 중 오류 발생: {str(e)}"
        )


@router.get(
    "/context/{context_id}",
    response_model=LHReviewResponse,
    summary="저장된 LH 예측 결과 조회",
    description="이전에 실행한 LH 심사예측 결과를 Context ID로 재조회"
)
async def get_cached_prediction(context_id: str) -> LHReviewResponse:
    """
    저장된 LH 예측 결과 조회
    """
    logger.info(f"🔍 LH 예측 결과 조회 - Context: {context_id}")
    
    if context_id not in LH_PREDICTION_CACHE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Context ID '{context_id}'에 대한 LH 예측 결과가 없습니다. 먼저 /predict를 실행하세요."
        )
    
    cached_result = LH_PREDICTION_CACHE[context_id]
    logger.info(f"✅ 캐시된 결과 반환 - 점수: {cached_result.predicted_score}/100")
    
    return cached_result


@router.get(
    "/housing-types",
    summary="LH 주택 유형 목록 조회",
    description="LH 공공주택 7대 유형 정보 반환"
)
async def get_housing_types() -> Dict[str, Any]:
    """
    LH 주택 유형 목록 및 세부 정보 반환
    """
    from app.main import HOUSING_TYPE_INFO
    
    return {
        "housing_types": HOUSING_TYPE_INFO,
        "type_count": len(HOUSING_TYPE_INFO),
        "description": "LH 공공주택 공식 7대 유형 (청년, 신혼·신생아 I/II, 다자녀, 고령자, 일반, 든든전세)"
    }


@router.get(
    "/factors/weights",
    summary="평가 요소 가중치 조회",
    description="LH 심사예측에 사용되는 6개 Factor별 가중치 정보"
)
async def get_factor_weights() -> Dict[str, Any]:
    """
    6개 평가 요소 가중치 정보 반환
    """
    return {
        "weights": lh_review_engine.WEIGHTS,
        "total": sum(lh_review_engine.WEIGHTS.values()),
        "factors": [
            {"name": "입지 점수", "weight": 0.25, "description": "교통 및 도심 접근성"},
            {"name": "용도지역 적합성", "weight": 0.20, "description": "LH 선호 용도지역 및 규제"},
            {"name": "토지가격 합리성", "weight": 0.15, "description": "공시지가 대비 감정가 적정성"},
            {"name": "용적률/건폐율 실현가능성", "weight": 0.20, "description": "법정 용적률/건폐율 적합도"},
            {"name": "리스크 수준", "weight": 0.10, "description": "전체 리스크 평가"},
            {"name": "시나리오 안정성", "weight": 0.10, "description": "목표 달성도 및 사업성"}
        ]
    }
