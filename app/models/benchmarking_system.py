"""
벤치마킹 시스템 데이터 모델
==========================

지역별 LH 공공임대 사례 DB 및 M7 생성 시 자동 반영

Version: 1.0
Date: 2026-01-10
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BenchmarkSpace(BaseModel):
    """벤치마킹 공간 정보"""
    
    space_type: str = Field(..., description="공간 유형")
    space_name: str = Field(..., description="공간 이름")
    area_sqm: float = Field(..., description="면적 (㎡)")
    capacity: int = Field(..., description="수용 인원")
    equipment: List[str] = Field(default_factory=list, description="주요 장비/시설")
    utilization_rate: float = Field(..., ge=0, le=100, description="이용률 (%)")


class BenchmarkProgram(BaseModel):
    """벤치마킹 프로그램 정보"""
    
    program_name: str = Field(..., description="프로그램 이름")
    frequency: str = Field(..., description="운영 빈도 (예: 주 1회, 월 2회)")
    duration_minutes: int = Field(..., description="소요 시간 (분)")
    target_audience: str = Field(..., description="대상 (청년, 신혼부부 등)")
    participation_rate: float = Field(..., ge=0, le=100, description="참여율 (%)")
    satisfaction_score: float = Field(..., ge=0, le=100, description="만족도 점수")


class BenchmarkingCase(BaseModel):
    """벤치마킹 사례"""
    
    case_id: str = Field(..., description="사례 ID")
    case_name: str = Field(..., description="사례명")
    
    # 기본 정보
    location: Dict[str, Any] = Field(..., description="위치 정보")
    housing_type: str = Field(..., description="주택 유형 (청년형, 신혼부부형 등)")
    household_count: int = Field(..., description="세대 수")
    
    # 운영 정보
    operation_model: str = Field(..., description="운영 모델 (LH 직접, 위탁 등)")
    operation_start_date: str = Field(..., description="운영 시작일")
    operation_duration_months: int = Field(..., description="운영 기간 (개월)")
    
    # 공간 구성
    community_spaces: List[BenchmarkSpace] = Field(..., description="커뮤니티 공간")
    
    # 프로그램 구성
    programs: List[BenchmarkProgram] = Field(..., description="프로그램 목록")
    
    # 성과 지표
    success_metrics: Dict[str, Any] = Field(..., description="성과 지표")
    
    # 예산 정보
    annual_budget: int = Field(..., description="연간 예산 (원)")
    cost_per_household_monthly: int = Field(..., description="세대당 월 비용 (원)")
    
    # 교훈 및 인사이트
    lessons_learned: List[str] = Field(default_factory=list, description="교훈")
    best_practices: List[str] = Field(default_factory=list, description="모범 사례")
    challenges: List[str] = Field(default_factory=list, description="과제/어려움")
    
    # 데이터 출처
    data_source: str = Field(..., description="데이터 출처")
    last_updated: str = Field(..., description="최종 업데이트 일자")


class RegionalSimilarity(BaseModel):
    """지역 유사도"""
    
    target_location: Dict[str, Any] = Field(..., description="비교 대상 위치")
    benchmark_case_id: str = Field(..., description="벤치마킹 사례 ID")
    
    # 유사도 점수
    similarity_score: float = Field(..., ge=0, le=100, description="전체 유사도 점수")
    
    # 세부 유사도
    geographic_similarity: float = Field(..., description="지리적 유사도")
    demographic_similarity: float = Field(..., description="인구통계 유사도")
    infrastructure_similarity: float = Field(..., description="인프라 유사도")
    housing_type_similarity: float = Field(..., description="주택 유형 유사도")
    
    # 유사도 근거
    similarity_rationale: str = Field(..., description="유사도 평가 근거")


class BenchmarkingRecommendation(BaseModel):
    """벤치마킹 기반 추천"""
    
    recommendation_id: str = Field(..., description="추천 ID")
    context_id: str = Field(..., description="M7 컨텍스트 ID")
    
    # 추천 사례들
    recommended_cases: List[Dict[str, Any]] = Field(
        ...,
        description="추천 벤치마킹 사례 (유사도 순)"
    )
    
    # 공간 추천
    space_recommendations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="공간 구성 추천"
    )
    
    # 프로그램 추천
    program_recommendations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="프로그램 추천"
    )
    
    # 예산 벤치마크
    budget_benchmark: Dict[str, Any] = Field(
        default_factory=dict,
        description="예산 벤치마크"
    )
    
    # 적용 제안
    application_suggestions: str = Field(..., description="적용 방안 제안")


# 벤치마킹 헬퍼 함수

def calculate_regional_similarity(
    target_location: Dict[str, Any],
    benchmark_case: BenchmarkingCase
) -> RegionalSimilarity:
    """
    지역 유사도 계산
    
    Args:
        target_location: 비교 대상 위치 정보
        benchmark_case: 벤치마킹 사례
    
    Returns:
        지역 유사도 평가
    """
    # 지리적 유사도 (거리 기반)
    # 실제 구현에서는 좌표 기반 거리 계산
    geographic_similarity = 80.0  # Placeholder
    
    # 인구통계 유사도 (연령대, 소득 등)
    demographic_similarity = 75.0  # Placeholder
    
    # 인프라 유사도 (교통, 편의시설 등)
    infrastructure_similarity = 85.0  # Placeholder
    
    # 주택 유형 유사도
    housing_type_similarity = 90.0  # Placeholder
    
    # 가중 평균
    similarity_score = (
        geographic_similarity * 0.25 +
        demographic_similarity * 0.30 +
        infrastructure_similarity * 0.20 +
        housing_type_similarity * 0.25
    )
    
    rationale = f"""
    지리적 유사도 {geographic_similarity:.1f}점: 동일 권역 내 위치
    인구통계 유사도 {demographic_similarity:.1f}점: 유사한 연령대 분포
    인프라 유사도 {infrastructure_similarity:.1f}점: 교통 및 편의시설 수준 유사
    주택 유형 유사도 {housing_type_similarity:.1f}점: {benchmark_case.housing_type} 동일
    """
    
    return RegionalSimilarity(
        target_location=target_location,
        benchmark_case_id=benchmark_case.case_id,
        similarity_score=similarity_score,
        geographic_similarity=geographic_similarity,
        demographic_similarity=demographic_similarity,
        infrastructure_similarity=infrastructure_similarity,
        housing_type_similarity=housing_type_similarity,
        similarity_rationale=rationale.strip()
    )


def find_similar_cases(
    target_location: Dict[str, Any],
    housing_type: str,
    household_count: int,
    all_cases: List[BenchmarkingCase],
    top_n: int = 5
) -> List[Dict[str, Any]]:
    """
    유사 사례 검색
    
    Args:
        target_location: 대상 위치
        housing_type: 주택 유형
        household_count: 세대 수
        all_cases: 전체 벤치마킹 사례 목록
        top_n: 상위 N개 사례
    
    Returns:
        유사도 순으로 정렬된 사례 목록
    """
    similarities = []
    
    for case in all_cases:
        # 주택 유형 필터링
        if case.housing_type != housing_type:
            continue
        
        # 세대 수 범위 필터링 (±30%)
        if not (household_count * 0.7 <= case.household_count <= household_count * 1.3):
            continue
        
        # 유사도 계산
        similarity = calculate_regional_similarity(target_location, case)
        
        similarities.append({
            "case": case,
            "similarity": similarity,
            "similarity_score": similarity.similarity_score
        })
    
    # 유사도 순 정렬
    similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    return similarities[:top_n]


def generate_benchmarking_recommendations(
    target_context: Dict[str, Any],
    similar_cases: List[Dict[str, Any]]
) -> BenchmarkingRecommendation:
    """
    벤치마킹 기반 추천 생성
    
    Args:
        target_context: 대상 M7 컨텍스트
        similar_cases: 유사 사례 목록
    
    Returns:
        벤치마킹 추천
    """
    space_recommendations = []
    program_recommendations = []
    budget_data = []
    
    for item in similar_cases:
        case = item["case"]
        similarity_score = item["similarity_score"]
        
        # 공간 추천 수집
        for space in case.community_spaces:
            if space.utilization_rate >= 70:  # 높은 이용률 공간
                space_recommendations.append({
                    "space_name": space.space_name,
                    "space_type": space.space_type,
                    "area_sqm": space.area_sqm,
                    "utilization_rate": space.utilization_rate,
                    "source_case": case.case_name,
                    "similarity_score": similarity_score,
                    "recommendation": f"이용률 {space.utilization_rate:.1f}%로 높음"
                })
        
        # 프로그램 추천 수집
        for program in case.programs:
            if program.satisfaction_score >= 80:  # 높은 만족도 프로그램
                program_recommendations.append({
                    "program_name": program.program_name,
                    "frequency": program.frequency,
                    "participation_rate": program.participation_rate,
                    "satisfaction_score": program.satisfaction_score,
                    "source_case": case.case_name,
                    "similarity_score": similarity_score,
                    "recommendation": f"만족도 {program.satisfaction_score:.1f}점, 참여율 {program.participation_rate:.1f}%"
                })
        
        # 예산 데이터 수집
        budget_data.append({
            "case_name": case.case_name,
            "annual_budget": case.annual_budget,
            "cost_per_household_monthly": case.cost_per_household_monthly,
            "household_count": case.household_count
        })
    
    # 공간 추천 정렬 (유사도 × 이용률)
    space_recommendations.sort(
        key=lambda x: x["similarity_score"] * x["utilization_rate"],
        reverse=True
    )
    
    # 프로그램 추천 정렬 (유사도 × 만족도)
    program_recommendations.sort(
        key=lambda x: x["similarity_score"] * x["satisfaction_score"],
        reverse=True
    )
    
    # 예산 벤치마크
    avg_monthly_cost = sum(b["cost_per_household_monthly"] for b in budget_data) / len(budget_data)
    budget_benchmark = {
        "average_monthly_cost_per_household": int(avg_monthly_cost),
        "recommended_budget_range": {
            "min": int(avg_monthly_cost * 0.8),
            "max": int(avg_monthly_cost * 1.2)
        },
        "cases": budget_data
    }
    
    # 적용 제안
    application_suggestions = f"""
    📊 벤치마킹 분석 결과:
    
    1. 공간 구성:
       - 상위 {min(3, len(space_recommendations))}개 공간을 우선 검토
       - 평균 이용률: {sum(s['utilization_rate'] for s in space_recommendations[:3])/3:.1f}%
    
    2. 프로그램 구성:
       - 상위 {min(5, len(program_recommendations))}개 프로그램을 참고
       - 평균 만족도: {sum(p['satisfaction_score'] for p in program_recommendations[:5])/5:.1f}점
    
    3. 예산:
       - 세대당 월 평균 비용: {int(avg_monthly_cost):,}원
       - 권장 범위: {int(avg_monthly_cost * 0.8):,}원 ~ {int(avg_monthly_cost * 1.2):,}원
    
    4. 적용 방안:
       - 유사 사례의 성공 요인을 M7 계획에 반영
       - 지역 특성에 맞게 커스터마이징
       - 단계적 도입 및 피드백 수집
    """
    
    return BenchmarkingRecommendation(
        recommendation_id=f"bench_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        context_id=target_context.get("context_id", "unknown"),
        recommended_cases=[
            {
                "case_id": item["case"].case_id,
                "case_name": item["case"].case_name,
                "similarity_score": item["similarity_score"],
                "location": item["case"].location,
                "household_count": item["case"].household_count
            }
            for item in similar_cases
        ],
        space_recommendations=space_recommendations[:10],
        program_recommendations=program_recommendations[:10],
        budget_benchmark=budget_benchmark,
        application_suggestions=application_suggestions.strip()
    )


# 샘플 벤치마킹 데이터 생성

def create_sample_benchmarking_cases() -> List[BenchmarkingCase]:
    """샘플 벤치마킹 사례 생성 (데모용)"""
    
    cases = [
        BenchmarkingCase(
            case_id="lh_case_001",
            case_name="서울 마포구 LH 청년형 임대주택",
            location={
                "address": "서울시 마포구 상암동",
                "district": "마포구",
                "subway_distance_m": 600,
                "park_distance_m": 300
            },
            housing_type="청년형",
            household_count=30,
            operation_model="LH 직접 운영",
            operation_start_date="2023-03-01",
            operation_duration_months=21,
            community_spaces=[
                BenchmarkSpace(
                    space_type="라운지",
                    space_name="커뮤니티 라운지",
                    area_sqm=40.0,
                    capacity=20,
                    equipment=["테이블", "의자", "빔프로젝터", "화이트보드"],
                    utilization_rate=85.0
                ),
                BenchmarkSpace(
                    space_type="주방",
                    space_name="공유 주방",
                    area_sqm=25.0,
                    capacity=10,
                    equipment=["조리대", "싱크대", "전자레인지", "냉장고"],
                    utilization_rate=72.0
                )
            ],
            programs=[
                BenchmarkProgram(
                    program_name="취업 준비 세미나",
                    frequency="격주 1회",
                    duration_minutes=90,
                    target_audience="청년 입주자",
                    participation_rate=65.0,
                    satisfaction_score=88.0
                ),
                BenchmarkProgram(
                    program_name="월간 네트워킹 모임",
                    frequency="월 1회",
                    duration_minutes=120,
                    target_audience="전체 입주자",
                    participation_rate=55.0,
                    satisfaction_score=82.0
                )
            ],
            success_metrics={
                "overall_satisfaction": 83.5,
                "community_engagement": 78.0,
                "program_participation_avg": 60.0,
                "space_utilization_avg": 78.5
            },
            annual_budget=7200000,
            cost_per_household_monthly=20000,
            lessons_learned=[
                "청년 입주자는 취업/창업 관련 프로그램 선호",
                "저녁 시간대(19-21시) 프로그램 참여율 높음",
                "온라인 커뮤니티와 오프라인 행사 병행 효과적"
            ],
            best_practices=[
                "입주 초기 오리엔테이션 필수 진행",
                "입주자 자율 운영 소모임 지원",
                "분기별 만족도 조사 실시"
            ],
            challenges=[
                "직장 업무로 인한 평일 낮 시간대 이용률 저조",
                "일부 프로그램의 고정 참여자 편중"
            ],
            data_source="LH 공공임대 커뮤니티 운영 사례집 2024",
            last_updated="2024-12-31"
        ),
        BenchmarkingCase(
            case_id="lh_case_002",
            case_name="경기 성남시 LH 신혼부부형 임대주택",
            location={
                "address": "경기도 성남시 분당구",
                "district": "분당구",
                "subway_distance_m": 450,
                "park_distance_m": 200
            },
            housing_type="신혼부부형",
            household_count=45,
            operation_model="협력 운영 (지역사회 파트너)",
            operation_start_date="2022-09-01",
            operation_duration_months=28,
            community_spaces=[
                BenchmarkSpace(
                    space_type="라운지",
                    space_name="가족 라운지",
                    area_sqm=50.0,
                    capacity=25,
                    equipment=["소파", "테이블", "TV", "아동 놀이공간"],
                    utilization_rate=90.0
                ),
                BenchmarkSpace(
                    space_type="다목적실",
                    space_name="육아 정보 교류실",
                    area_sqm=30.0,
                    capacity=15,
                    equipment=["수유실", "기저귀 교환대", "유아용 의자"],
                    utilization_rate=88.0
                )
            ],
            programs=[
                BenchmarkProgram(
                    program_name="육아 정보 교류회",
                    frequency="격주 1회",
                    duration_minutes=60,
                    target_audience="신혼부부",
                    participation_rate=75.0,
                    satisfaction_score=92.0
                ),
                BenchmarkProgram(
                    program_name="아이와 함께하는 주말 활동",
                    frequency="월 2회",
                    duration_minutes=90,
                    target_audience="가족 단위",
                    participation_rate=70.0,
                    satisfaction_score=89.0
                )
            ],
            success_metrics={
                "overall_satisfaction": 88.0,
                "community_engagement": 85.0,
                "program_participation_avg": 72.5,
                "space_utilization_avg": 89.0
            },
            annual_budget=10800000,
            cost_per_household_monthly=20000,
            lessons_learned=[
                "신혼부부는 육아 관련 정보 교류 프로그램 선호",
                "아이 동반 가능한 공간 및 프로그램 필수",
                "주말 오전 시간대 가족 단위 프로그램 효과적"
            ],
            best_practices=[
                "지역 육아 커뮤니티와 연계",
                "부부 대상 재정 교육 프로그램 운영",
                "입주자 간 육아 품앗이 지원"
            ],
            challenges=[
                "영유아 소음 관련 민원 관리",
                "프로그램 시간대 조율 어려움"
            ],
            data_source="LH 공공임대 커뮤니티 운영 사례집 2024",
            last_updated="2024-12-31"
        )
    ]
    
    return cases
