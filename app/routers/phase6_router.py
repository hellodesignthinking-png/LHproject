"""
Phase 6 API 라우터: 피드백 & 벤치마킹 시스템
==========================================

입주자 피드백 수집 및 벤치마킹 기반 M7 개선

Version: 1.0
Date: 2026-01-10
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from app.models.feedback_system import (
    ResidentFeedback,
    FeedbackAnalysis,
    M7UpdateProposal,
    analyze_feedback,
    generate_m7_update_suggestions
)
from app.models.benchmarking_system import (
    BenchmarkingCase,
    BenchmarkingRecommendation,
    find_similar_cases,
    generate_benchmarking_recommendations,
    create_sample_benchmarking_cases
)

router = APIRouter(prefix="/api/v4/phase6", tags=["Phase 6: Feedback & Benchmarking"])
logger = logging.getLogger(__name__)

# 임시 저장소 (실제 구현에서는 DB 사용)
feedback_storage: Dict[str, ResidentFeedback] = {}
analysis_storage: Dict[str, FeedbackAnalysis] = {}
benchmarking_cases: List[BenchmarkingCase] = create_sample_benchmarking_cases()


@router.post("/feedback/submit")
async def submit_resident_feedback(feedback: ResidentFeedback):
    """
    입주자 피드백 제출
    
    **입주 후 6개월 경과 시 피드백 수집**
    
    Args:
        feedback: 입주자 피드백 데이터
    
    Returns:
        제출 확인 및 분석 ID
    """
    try:
        logger.info(f"📊 피드백 수집: {feedback.feedback_id} (컨텍스트: {feedback.context_id})")
        
        # 피드백 저장
        feedback_storage[feedback.feedback_id] = feedback
        
        # 자동 분석 수행
        analysis = analyze_feedback(feedback)
        analysis_storage[analysis.analysis_id] = analysis
        
        logger.info(f"✅ 피드백 분석 완료: {analysis.analysis_id}")
        logger.info(f"   - 평균 만족도: {analysis.average_satisfaction:.1f}점")
        logger.info(f"   - 참여율: {analysis.participation_rate:.1f}%")
        logger.info(f"   - 개선 필요 영역: {len(analysis.improvement_areas)}개")
        
        return {
            "success": True,
            "feedback_id": feedback.feedback_id,
            "analysis_id": analysis.analysis_id,
            "message": "✅ 피드백이 성공적으로 제출되었습니다",
            "summary": {
                "average_satisfaction": analysis.average_satisfaction,
                "participation_rate": analysis.participation_rate,
                "engagement_score": analysis.engagement_score,
                "improvement_areas_count": len(analysis.improvement_areas),
                "success_factors_count": len(analysis.success_factors)
            }
        }
    
    except Exception as e:
        logger.error(f"❌ 피드백 제출 오류: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/analysis/{analysis_id}")
async def get_feedback_analysis(analysis_id: str):
    """
    피드백 분석 결과 조회
    
    Args:
        analysis_id: 분석 ID
    
    Returns:
        분석 결과 및 M7 업데이트 제안
    """
    if analysis_id not in analysis_storage:
        raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다")
    
    analysis = analysis_storage[analysis_id]
    
    return {
        "success": True,
        "analysis": analysis.model_dump(),
        "insights": {
            "overall_health": "양호" if analysis.average_satisfaction >= 70 else "개선 필요",
            "top_improvement_areas": analysis.improvement_areas[:3],
            "top_success_factors": analysis.success_factors[:3]
        }
    }


@router.get("/feedback/context/{context_id}")
async def get_feedback_by_context(context_id: str):
    """
    컨텍스트별 피드백 조회
    
    Args:
        context_id: M7 컨텍스트 ID
    
    Returns:
        해당 컨텍스트의 모든 피드백 및 분석
    """
    context_feedbacks = [
        fb for fb in feedback_storage.values()
        if fb.context_id == context_id
    ]
    
    if not context_feedbacks:
        return {
            "success": True,
            "context_id": context_id,
            "feedback_count": 0,
            "message": "아직 수집된 피드백이 없습니다",
            "feedbacks": []
        }
    
    # 최신 피드백 기준 분석
    latest_feedback = max(context_feedbacks, key=lambda x: x.collection_date)
    
    # 해당 피드백의 분석 찾기
    related_analyses = [
        analysis for analysis in analysis_storage.values()
        if analysis.context_id == context_id
    ]
    
    return {
        "success": True,
        "context_id": context_id,
        "feedback_count": len(context_feedbacks),
        "latest_feedback": latest_feedback.model_dump(),
        "analyses": [a.model_dump() for a in related_analyses],
        "trend": {
            "satisfaction_trend": [fb.overall_satisfaction for fb in context_feedbacks],
            "collection_dates": [fb.collection_date for fb in context_feedbacks]
        }
    }


@router.post("/m7/update-proposal")
async def create_m7_update_proposal(
    context_id: str = Query(..., description="M7 컨텍스트 ID"),
    feedback_id: str = Query(..., description="기반 피드백 ID")
):
    """
    M7 업데이트 제안 생성
    
    **피드백 분석 결과를 기반으로 M7 개선안 자동 생성**
    
    Args:
        context_id: M7 컨텍스트 ID
        feedback_id: 피드백 ID
    
    Returns:
        M7 업데이트 제안
    """
    try:
        # 피드백 및 분석 조회
        if feedback_id not in feedback_storage:
            raise HTTPException(status_code=404, detail="피드백을 찾을 수 없습니다")
        
        feedback = feedback_storage[feedback_id]
        
        # 분석 찾기
        analysis_id = f"analysis_{feedback_id}"
        if analysis_id not in analysis_storage:
            # 분석 수행
            analysis = analyze_feedback(feedback)
            analysis_storage[analysis_id] = analysis
        else:
            analysis = analysis_storage[analysis_id]
        
        # M7 업데이트 제안 생성
        proposal = M7UpdateProposal(
            proposal_id=f"proposal_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            context_id=context_id,
            based_on_feedback_id=feedback_id,
            space_adjustments=analysis.m7_update_suggestions.get("space_updates", []),
            program_adjustments=analysis.m7_update_suggestions.get("program_updates", []),
            operation_adjustments=analysis.m7_update_suggestions.get("operation_updates", {}),
            priority=analysis.m7_update_suggestions.get("priority", "MEDIUM"),
            expected_impact=f"만족도 향상 예상: {analysis.average_satisfaction:.1f}점 → {min(analysis.average_satisfaction + 15, 95):.1f}점"
        )
        
        logger.info(f"✅ M7 업데이트 제안 생성: {proposal.proposal_id}")
        logger.info(f"   - 우선순위: {proposal.priority}")
        logger.info(f"   - 공간 조정: {len(proposal.space_adjustments)}개")
        logger.info(f"   - 프로그램 조정: {len(proposal.program_adjustments)}개")
        
        return {
            "success": True,
            "proposal": proposal.model_dump(),
            "preview": {
                "space_changes": len(proposal.space_adjustments),
                "program_changes": len(proposal.program_adjustments),
                "operation_changes": bool(proposal.operation_adjustments),
                "priority": proposal.priority
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ M7 업데이트 제안 생성 오류: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarking/cases")
async def get_benchmarking_cases(
    housing_type: Optional[str] = Query(None, description="주택 유형 (청년형, 신혼부부형 등)"),
    min_household_count: Optional[int] = Query(None, description="최소 세대 수"),
    max_household_count: Optional[int] = Query(None, description="최대 세대 수")
):
    """
    벤치마킹 사례 조회
    
    **LH 공공임대 커뮤니티 운영 사례 데이터베이스**
    
    Args:
        housing_type: 주택 유형 필터
        min_household_count: 최소 세대 수
        max_household_count: 최대 세대 수
    
    Returns:
        필터링된 벤치마킹 사례 목록
    """
    filtered_cases = benchmarking_cases
    
    # 주택 유형 필터
    if housing_type:
        filtered_cases = [c for c in filtered_cases if c.housing_type == housing_type]
    
    # 세대 수 필터
    if min_household_count:
        filtered_cases = [c for c in filtered_cases if c.household_count >= min_household_count]
    if max_household_count:
        filtered_cases = [c for c in filtered_cases if c.household_count <= max_household_count]
    
    return {
        "success": True,
        "total_cases": len(benchmarking_cases),
        "filtered_cases": len(filtered_cases),
        "cases": [
            {
                "case_id": c.case_id,
                "case_name": c.case_name,
                "location": c.location,
                "housing_type": c.housing_type,
                "household_count": c.household_count,
                "operation_model": c.operation_model,
                "success_metrics": c.success_metrics,
                "cost_per_household_monthly": c.cost_per_household_monthly
            }
            for c in filtered_cases
        ]
    }


@router.get("/benchmarking/recommendations")
async def get_benchmarking_recommendations(
    context_id: str = Query(..., description="M7 컨텍스트 ID"),
    housing_type: str = Query(..., description="주택 유형"),
    household_count: int = Query(..., description="세대 수"),
    address: str = Query(..., description="주소")
):
    """
    벤치마킹 기반 추천
    
    **유사 지역 사례를 분석하여 M7 계획에 적용 가능한 추천 제공**
    
    Args:
        context_id: M7 컨텍스트 ID
        housing_type: 주택 유형
        household_count: 세대 수
        address: 주소
    
    Returns:
        벤치마킹 기반 추천 (공간, 프로그램, 예산)
    """
    try:
        # 대상 위치 정보 구성
        target_location = {
            "address": address,
            "district": address.split()[1] if len(address.split()) > 1 else "unknown"
        }
        
        # 유사 사례 검색
        similar_cases = find_similar_cases(
            target_location=target_location,
            housing_type=housing_type,
            household_count=household_count,
            all_cases=benchmarking_cases,
            top_n=5
        )
        
        if not similar_cases:
            return {
                "success": False,
                "message": "유사한 벤치마킹 사례를 찾을 수 없습니다",
                "recommendations": None
            }
        
        # 추천 생성
        target_context = {
            "context_id": context_id,
            "housing_type": housing_type,
            "household_count": household_count,
            "location": target_location
        }
        
        recommendations = generate_benchmarking_recommendations(target_context, similar_cases)
        
        logger.info(f"✅ 벤치마킹 추천 생성: {recommendations.recommendation_id}")
        logger.info(f"   - 유사 사례: {len(recommendations.recommended_cases)}개")
        logger.info(f"   - 공간 추천: {len(recommendations.space_recommendations)}개")
        logger.info(f"   - 프로그램 추천: {len(recommendations.program_recommendations)}개")
        
        return {
            "success": True,
            "recommendations": recommendations.model_dump(),
            "summary": {
                "similar_cases_count": len(recommendations.recommended_cases),
                "space_recommendations_count": len(recommendations.space_recommendations),
                "program_recommendations_count": len(recommendations.program_recommendations),
                "average_monthly_cost": recommendations.budget_benchmark.get("average_monthly_cost_per_household", 0)
            }
        }
    
    except Exception as e:
        logger.error(f"❌ 벤치마킹 추천 생성 오류: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarking/case/{case_id}")
async def get_benchmarking_case_detail(case_id: str):
    """
    벤치마킹 사례 상세 조회
    
    Args:
        case_id: 사례 ID
    
    Returns:
        사례 상세 정보 (공간, 프로그램, 성과, 교훈)
    """
    case = next((c for c in benchmarking_cases if c.case_id == case_id), None)
    
    if not case:
        raise HTTPException(status_code=404, detail="사례를 찾을 수 없습니다")
    
    return {
        "success": True,
        "case": case.model_dump()
    }


@router.get("/health")
async def phase6_health_check():
    """Phase 6 시스템 상태 확인"""
    return {
        "status": "healthy",
        "phase": "Phase 6: Feedback & Benchmarking System",
        "features": {
            "feedback_collection": "enabled",
            "feedback_analysis": "enabled",
            "m7_update_proposal": "enabled",
            "benchmarking_database": "enabled",
            "similarity_matching": "enabled"
        },
        "statistics": {
            "feedback_count": len(feedback_storage),
            "analysis_count": len(analysis_storage),
            "benchmarking_cases_count": len(benchmarking_cases)
        },
        "timestamp": datetime.now().isoformat()
    }
