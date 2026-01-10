"""
피드백 시스템 데이터 모델
========================

입주 후 6개월 피드백 수집 및 M7 자동 업데이트

Version: 1.0
Date: 2026-01-10
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SpaceFeedback(BaseModel):
    """공간별 만족도 피드백"""
    
    space_name: str = Field(..., description="공간 이름 (예: 커뮤니티 라운지)")
    usage_frequency: int = Field(..., ge=0, le=30, description="월 평균 이용 횟수 (0-30)")
    satisfaction_score: float = Field(..., ge=0, le=100, description="만족도 점수 (0-100)")
    issues: List[str] = Field(default_factory=list, description="개선 필요 사항")
    strengths: List[str] = Field(default_factory=list, description="만족스러운 점")


class ProgramFeedback(BaseModel):
    """프로그램별 참여도 및 만족도"""
    
    program_name: str = Field(..., description="프로그램 이름")
    participation_rate: float = Field(..., ge=0, le=100, description="참여율 (%)")
    satisfaction_score: float = Field(..., ge=0, le=100, description="만족도 점수 (0-100)")
    attendance_count: int = Field(..., ge=0, description="평균 참석 인원")
    suggestions: List[str] = Field(default_factory=list, description="개선 제안")


class CommunityEngagement(BaseModel):
    """커뮤니티 참여도 평가"""
    
    overall_engagement: float = Field(..., ge=0, le=100, description="전체 참여도 (0-100)")
    neighbor_interaction: float = Field(..., ge=0, le=100, description="이웃 간 교류 (0-100)")
    event_participation: float = Field(..., ge=0, le=100, description="행사 참여율 (0-100)")
    online_community_activity: float = Field(..., ge=0, le=100, description="온라인 커뮤니티 활동도 (0-100)")


class ResidentFeedback(BaseModel):
    """입주자 피드백 데이터"""
    
    feedback_id: str = Field(..., description="피드백 고유 ID")
    context_id: str = Field(..., description="연결된 M7 컨텍스트 ID")
    collection_date: str = Field(..., description="수집 일자 (YYYY-MM-DD)")
    months_after_move_in: int = Field(..., ge=1, le=24, description="입주 후 경과 개월 수")
    
    # 공간 피드백
    space_feedback: List[SpaceFeedback] = Field(..., description="공간별 피드백")
    
    # 프로그램 피드백
    program_feedback: List[ProgramFeedback] = Field(..., description="프로그램별 피드백")
    
    # 커뮤니티 참여도
    community_engagement: CommunityEngagement = Field(..., description="커뮤니티 참여도")
    
    # 전체 만족도
    overall_satisfaction: float = Field(..., ge=0, le=100, description="전체 만족도 (0-100)")
    
    # 자유 의견
    open_comments: List[str] = Field(default_factory=list, description="자유 의견")
    
    # 메타데이터
    respondent_count: int = Field(..., ge=1, description="응답자 수")
    total_household_count: int = Field(..., ge=1, description="전체 세대 수")


class FeedbackAnalysis(BaseModel):
    """피드백 분석 결과"""
    
    analysis_id: str = Field(..., description="분석 ID")
    context_id: str = Field(..., description="컨텍스트 ID")
    analysis_date: str = Field(..., description="분석 일자")
    
    # 핵심 지표
    average_satisfaction: float = Field(..., description="평균 만족도")
    participation_rate: float = Field(..., description="전체 참여율")
    engagement_score: float = Field(..., description="참여도 점수")
    
    # 개선 필요 영역
    improvement_areas: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="개선 필요 영역 (우선순위별)"
    )
    
    # 성공 요인
    success_factors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="성공 요인"
    )
    
    # M7 업데이트 제안
    m7_update_suggestions: Dict[str, Any] = Field(
        default_factory=dict,
        description="M7 업데이트 제안 사항"
    )


class M7UpdateProposal(BaseModel):
    """M7 자동 업데이트 제안"""
    
    proposal_id: str = Field(..., description="제안 ID")
    context_id: str = Field(..., description="컨텍스트 ID")
    based_on_feedback_id: str = Field(..., description="기반 피드백 ID")
    
    # 공간 조정 제안
    space_adjustments: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="공간 구성 조정 제안"
    )
    
    # 프로그램 조정 제안
    program_adjustments: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="프로그램 조정 제안"
    )
    
    # 운영 모델 조정
    operation_adjustments: Optional[Dict[str, Any]] = Field(
        None,
        description="운영 모델 조정 제안"
    )
    
    # 적용 우선순위
    priority: str = Field(..., description="우선순위 (HIGH/MEDIUM/LOW)")
    
    # 예상 효과
    expected_impact: str = Field(..., description="예상 효과 설명")
    
    # 승인 여부
    approved: bool = Field(default=False, description="승인 여부")
    approved_at: Optional[str] = Field(None, description="승인 일시")


# 피드백 분석 헬퍼 함수

def analyze_feedback(feedback: ResidentFeedback) -> FeedbackAnalysis:
    """
    피드백 데이터를 분석하여 인사이트 추출
    
    Args:
        feedback: 입주자 피드백 데이터
    
    Returns:
        분석 결과
    """
    # 평균 만족도 계산
    space_scores = [s.satisfaction_score for s in feedback.space_feedback]
    program_scores = [p.satisfaction_score for p in feedback.program_feedback]
    all_scores = space_scores + program_scores + [feedback.overall_satisfaction]
    avg_satisfaction = sum(all_scores) / len(all_scores) if all_scores else 0
    
    # 참여율 계산
    program_participation = [p.participation_rate for p in feedback.program_feedback]
    avg_participation = sum(program_participation) / len(program_participation) if program_participation else 0
    
    # 참여도 점수
    engagement = feedback.community_engagement
    engagement_score = (
        engagement.overall_engagement * 0.4 +
        engagement.neighbor_interaction * 0.3 +
        engagement.event_participation * 0.2 +
        engagement.online_community_activity * 0.1
    )
    
    # 개선 필요 영역 식별
    improvement_areas = []
    
    # 낮은 만족도 공간
    for space in feedback.space_feedback:
        if space.satisfaction_score < 60:
            improvement_areas.append({
                "type": "space",
                "name": space.space_name,
                "score": space.satisfaction_score,
                "issues": space.issues,
                "priority": "HIGH" if space.satisfaction_score < 40 else "MEDIUM"
            })
    
    # 낮은 참여율 프로그램
    for program in feedback.program_feedback:
        if program.participation_rate < 30:
            improvement_areas.append({
                "type": "program",
                "name": program.program_name,
                "participation_rate": program.participation_rate,
                "suggestions": program.suggestions,
                "priority": "HIGH" if program.participation_rate < 15 else "MEDIUM"
            })
    
    # 우선순위 정렬
    improvement_areas.sort(key=lambda x: 0 if x["priority"] == "HIGH" else 1)
    
    # 성공 요인 식별
    success_factors = []
    
    # 높은 만족도 공간
    for space in feedback.space_feedback:
        if space.satisfaction_score >= 80:
            success_factors.append({
                "type": "space",
                "name": space.space_name,
                "score": space.satisfaction_score,
                "strengths": space.strengths
            })
    
    # 높은 참여율 프로그램
    for program in feedback.program_feedback:
        if program.participation_rate >= 50:
            success_factors.append({
                "type": "program",
                "name": program.program_name,
                "participation_rate": program.participation_rate
            })
    
    # M7 업데이트 제안 생성
    m7_suggestions = generate_m7_update_suggestions(feedback, improvement_areas, success_factors)
    
    return FeedbackAnalysis(
        analysis_id=f"analysis_{feedback.feedback_id}",
        context_id=feedback.context_id,
        analysis_date=datetime.now().strftime("%Y-%m-%d"),
        average_satisfaction=avg_satisfaction,
        participation_rate=avg_participation,
        engagement_score=engagement_score,
        improvement_areas=improvement_areas,
        success_factors=success_factors,
        m7_update_suggestions=m7_suggestions
    )


def generate_m7_update_suggestions(
    feedback: ResidentFeedback,
    improvement_areas: List[Dict[str, Any]],
    success_factors: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """M7 업데이트 제안 생성"""
    
    suggestions = {
        "space_updates": [],
        "program_updates": [],
        "operation_updates": {},
        "priority": "MEDIUM",
        "rationale": []
    }
    
    # 공간 조정 제안
    for area in improvement_areas:
        if area["type"] == "space" and area["priority"] == "HIGH":
            suggestions["space_updates"].append({
                "action": "reduce_or_repurpose",
                "space_name": area["name"],
                "reason": f"만족도 {area['score']:.1f}점으로 낮음",
                "recommendation": "용도 변경 또는 개선 방안 검토"
            })
            suggestions["priority"] = "HIGH"
    
    # 프로그램 조정 제안
    for area in improvement_areas:
        if area["type"] == "program" and area["priority"] == "HIGH":
            suggestions["program_updates"].append({
                "action": "revise_or_replace",
                "program_name": area["name"],
                "reason": f"참여율 {area['participation_rate']:.1f}%로 낮음",
                "recommendation": "프로그램 내용 개선 또는 대체 프로그램 검토"
            })
            suggestions["priority"] = "HIGH"
    
    # 성공 요인 강화 제안
    for factor in success_factors:
        if factor["type"] == "program":
            suggestions["program_updates"].append({
                "action": "expand_or_replicate",
                "program_name": factor["name"],
                "reason": f"참여율 {factor['participation_rate']:.1f}%로 높음",
                "recommendation": "유사 프로그램 추가 또는 빈도 증가 검토"
            })
    
    # 운영 모델 조정
    if feedback.overall_satisfaction < 50:
        suggestions["operation_updates"] = {
            "current_model": "현재 운영 모델",
            "suggested_change": "운영 주체 변경 또는 관리 강화",
            "reason": f"전체 만족도 {feedback.overall_satisfaction:.1f}점으로 낮음"
        }
        suggestions["priority"] = "HIGH"
    
    return suggestions
