"""
M7 커뮤니티 계획 모듈 데이터 모델
=====================================

M7은 계산 모듈이 아닌 '운영·커뮤니티 계획 모듈'입니다.
M2~M6 결과를 활용하여 커뮤니티 운영 계획을 수립합니다.

Version: 1.0
Date: 2026-01-10
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ResidentType(str, Enum):
    """입주자 유형"""
    YOUTH = "청년형"
    NEWLYWED = "신혼부부형"
    SENIOR = "고령자형"
    ONE_PERSON = "1인 가구형"
    WORKING_CLASS = "직장인형"
    CREATIVE_CLASS = "창작자형"


@dataclass
class ResidentPersona:
    """입주자 페르소나"""
    primary_type: ResidentType
    secondary_type: Optional[ResidentType]
    excluded_types: List[str]
    rationale: str
    regional_connection: str
    housing_type_alignment: str


@dataclass
class CommunityGoal:
    """커뮤니티 목표"""
    # 정성 목표
    qualitative_goals: List[str]
    
    # 정량 목표
    monthly_programs_target: int  # 월간 프로그램 횟수
    participation_rate_target: float  # 입주자 참여율 목표 (%)
    space_usage_frequency: str  # 공용공간 이용 빈도 목표


@dataclass
class CommunitySpace:
    """커뮤니티 공간 정의"""
    space_name: str
    function: str
    operation_method: str
    capacity: Optional[int]
    equipment: Optional[List[str]]


@dataclass
class CommunityProgram:
    """커뮤니티 프로그램"""
    program_name: str
    frequency: str  # 예: "연 1회", "월 1회", "분기 1회"
    target_audience: str
    format: str  # 예: "워크숍", "세미나", "교류회"
    participation_type: str  # "필수", "자율", "선택"


@dataclass
class OperationStructure:
    """운영 구조"""
    operator_type: str  # "위탁", "직접", "협력"
    lh_role: str
    resident_role: str
    dispute_resolution: str
    cost_structure: Optional[str]


@dataclass
class SustainabilityPlan:
    """지속 가능성 계획"""
    overload_prevention: List[str]
    participation_guidelines: str
    budget_control: str
    contingency_plan: str


@dataclass
class M7CommunityPlan:
    """M7 커뮤니티 계획 전체 데이터 모델"""
    
    # M7-1. 전제 조건 (M1~M6에서 자동 연동)
    location_characteristics: str
    housing_type_from_m3: str
    household_composition_from_m4: int
    financial_constraints_from_m5: Optional[str]
    lh_approval_conditions_from_m6: Optional[str]
    
    # M7-2. 입주자 페르소나
    resident_persona: ResidentPersona
    
    # M7-3. 커뮤니티 목표
    community_goals: CommunityGoal
    
    # M7-4. 공간 구성
    community_spaces: List[CommunitySpace]
    
    # M7-5. 프로그램 구성
    programs: List[CommunityProgram]
    
    # M7-6. 운영 구조
    operation_structure: OperationStructure
    
    # M7-7. 지속 가능성
    sustainability_plan: SustainabilityPlan
    
    # 메타 정보
    generated_at: str
    context_id: str


# ============================================================================
# M7 Summary for Final Report Assembler
# ============================================================================

@dataclass
class M7Summary:
    """
    M7 커뮤니티 계획 요약 (최종보고서용)
    
    final_report_assembler.py에서 사용하는 표준 Summary 구조
    """
    primary_resident_type: str
    community_goal_summary: str
    key_programs_count: int
    operation_model: str
    sustainability_score: Optional[float]  # 0-100
    
    # 추가 참조 정보
    space_count: Optional[int]
    monthly_program_frequency: Optional[int]
    participation_target_pct: Optional[float]


# ============================================================================
# M7 Generator Functions
# ============================================================================

def generate_m7_from_context(
    m1_result: Dict[str, Any],
    m2_result: Optional[Dict[str, Any]],
    m3_result: Dict[str, Any],
    m4_result: Dict[str, Any],
    m5_result: Optional[Dict[str, Any]],
    m6_result: Optional[Dict[str, Any]],
    context_id: str
) -> M7CommunityPlan:
    """
    M1~M6 결과를 기반으로 M7 커뮤니티 계획을 생성합니다.
    
    **M2 연동**: 토지 가치 기반 공간 확장
    **M1 연동**: 입지 특성 기반 페르소나/프로그램
    **M5 연동**: 사업성 기반 공간 확장
    **M6 연동**: LH 심사 기준 기반 운영 모델
    
    이 함수는 실제 계산을 수행하지 않고, M2~M6의 결과를 해석하여
    운영 가능한 커뮤니티 계획을 도출합니다.
    """
    from datetime import datetime
    
    # M3에서 공급 유형 추출
    housing_type = m3_result.get("selected", {}).get("name", "청년형")
    
    # M4에서 세대수 추출
    household_count = m4_result.get("summary", {}).get("legal_units", 20)
    
    # M7-1: 전제 조건 (자동 연동)
    location = m1_result.get("address", "서울시 마포구 월드컵북로 120")
    
    # M7-2: 페르소나 정의 (M1 데이터 연동)
    persona = _define_resident_persona(housing_type, location, m1_result)
    
    # M7-3: 커뮤니티 목표
    goals = _define_community_goals(housing_type, household_count)
    
    # M7-4: 공간 구성 (M2+M5 데이터 연동)
    spaces = _define_community_spaces(household_count, m5_result, m2_result)
    
    # M7-5: 프로그램 구성 (M1 데이터 연동)
    programs = _define_community_programs(housing_type, m1_result)
    
    # M7-6: 운영 구조 (M6 데이터 연동)
    operation = _define_operation_structure(household_count, m6_result)
    
    # M7-7: 지속 가능성 (M6 데이터 연동)
    sustainability = _define_sustainability_plan(household_count, m6_result)
    
    return M7CommunityPlan(
        location_characteristics=location,
        housing_type_from_m3=housing_type,
        household_composition_from_m4=household_count,
        financial_constraints_from_m5=None,
        lh_approval_conditions_from_m6=None,
        resident_persona=persona,
        community_goals=goals,
        community_spaces=spaces,
        programs=programs,
        operation_structure=operation,
        sustainability_plan=sustainability,
        generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        context_id=context_id
    )


def _define_resident_persona(housing_type: str, location: str, m1_data: Optional[Dict] = None) -> ResidentPersona:
    """
    입주자 페르소나 정의
    
    **M1 연동 로직**:
    - 역세권 (800m 이내) → 청년형 rationale 강화
    - 생활편의시설 우수 → 신혼부부형 선호
    - 공원 접근성 우수 → 지역 연계 강조
    """
    # M1 입지 특성 분석
    is_near_station = False
    has_good_amenities = False
    station_info = ""
    amenity_info = ""
    
    if m1_data:
        # 교통 접근성
        transit = m1_data.get("transit_access", {})
        nearest_distance = transit.get("nearest_station_distance_m", 9999)
        station_name = transit.get("nearest_station_name", "인근 역")
        
        if nearest_distance <= 800:
            is_near_station = True
            walk_minutes = int(nearest_distance / 80)  # 80m/분 도보 속도
            station_info = f"{station_name} 도보 {walk_minutes}분({nearest_distance}m) 거리로 역세권 입지"
        
        # 생활편의시설
        amenities = m1_data.get("amenities", {})
        amenity_score = amenities.get("overall_score", 0)
        if amenity_score >= 70:
            has_good_amenities = True
            amenity_info = "편의점, 마트, 병원 등 생활편의시설 접근성 우수"
    
    if "청년" in housing_type:
        rationale_parts = [f"대상지({location})는"]
        
        if is_near_station:
            rationale_parts.append(station_info + "이며,")
        else:
            rationale_parts.append("직주근접성이 우수하며,")
        
        rationale_parts.append("대중교통 접근성이 양호하여 청년층 입주자에게 적합한 것으로 판단됩니다.")
        
        regional_parts = []
        if station_info:
            regional_parts.append(f"역세권 입지로 인한 높은 교통 편의성")
        regional_parts.append("주변 산업단지 및 업무지구와의 접근성이 우수하여, 해당 지역 종사 청년층의 수요가 예상됩니다")
        
        return ResidentPersona(
            primary_type=ResidentType.YOUTH,
            secondary_type=ResidentType.ONE_PERSON,
            excluded_types=["가족 단위 (4인 이상)", "고령자 (65세 이상)"],
            rationale=" ".join(rationale_parts),
            regional_connection=". ".join(regional_parts) + ".",
            housing_type_alignment="M3 분석 결과 청년형 임대주택이 최적 유형으로 도출되었으며, 이는 지역 특성 및 LH 공급 정책과 부합합니다."
        )
    elif "신혼" in housing_type:
        rationale_parts = [f"대상지는"]
        
        if has_good_amenities:
            rationale_parts.append(amenity_info + "하며,")
        
        rationale_parts.append("교육 시설 및 생활 편의시설 접근성이 우수하여 신혼부부 입주자에게 적합합니다.")
        
        return ResidentPersona(
            primary_type=ResidentType.NEWLYWED,
            secondary_type=ResidentType.WORKING_CLASS,
            excluded_types=["1인 가구", "고령자 단독"],
            rationale=" ".join(rationale_parts),
            regional_connection="초등학교 도보 10분 거리, 대형마트 접근 용이 등 자녀 양육 환경이 양호합니다.",
            housing_type_alignment="M3 분석 결과 신혼부부형이 적합 유형으로 도출되었습니다."
        )
    else:
        return ResidentPersona(
            primary_type=ResidentType.ONE_PERSON,
            secondary_type=None,
            excluded_types=[],
            rationale="일반 공공임대 입주자 특성에 부합하는 커뮤니티 계획을 수립합니다.",
            regional_connection="지역 특성을 고려한 입주자 구성이 예상됩니다.",
            housing_type_alignment=f"M3 분석 결과 {housing_type} 유형으로 판단되었습니다."
        )


def _define_community_goals(housing_type: str, household_count: int) -> CommunityGoal:
    """커뮤니티 목표 설정"""
    return CommunityGoal(
        qualitative_goals=[
            "입주자 간 고립 방지 및 안전망 구축",
            "생활 안정성 제고 및 주거 만족도 향상",
            "지역사회와의 연계를 통한 사회적 통합 증진"
        ],
        monthly_programs_target=2,
        participation_rate_target=30.0,
        space_usage_frequency="주 3회 이상"
    )


def _define_community_spaces(
    household_count: int, 
    m5_data: Optional[Dict] = None, 
    m2_data: Optional[Dict] = None
) -> List[CommunitySpace]:
    """
    공간 구성 정의
    
    **M2 연동 로직**:
    - 토지 가치 평당 1,500만원 이상 → 프리미엄 공간 (북카페, 세미나실)
    - 토지 가치 평당 1,000~1,500만원 → 표준 확장 공간
    - 토지 가치 평당 1,000만원 미만 → 기본 공간만
    
    **M5 연동 로직**:
    - NPV 3억 이상 → 추가 공간 확대 (독서실)
    - NPV 5억 이상 → 피트니스 룸 추가
    - 낮은 수익성 → 기본 공간만 구성
    
    **우선순위**: M2 토지 가치가 M5 NPV보다 우선 (입지 품질 중심)
    """
    spaces = [
        CommunitySpace(
            space_name="커뮤니티 라운지",
            function="입주자 모임, 교육 프로그램 운영",
            operation_method="예약제 (온라인 사전 신청)",
            capacity=20,
            equipment=["테이블 및 의자", "빔프로젝터", "화이트보드"]
        ),
        CommunitySpace(
            space_name="공유 주방",
            function="소규모 교류, 간단한 취사 활동",
            operation_method="시간제 이용 (2시간 단위)",
            capacity=10,
            equipment=["조리대", "싱크대", "전자레인지", "냉장고"]
        )
    ]
    
    # M2 토지 가치 분석
    land_value_per_pyeong = 0
    if m2_data:
        summary = m2_data.get("summary", {})
        land_value_per_pyeong = summary.get("pyeong_price_krw", 0)
    
    # M5 사업성 분석
    npv_krw = 0
    if m5_data:
        financials = m5_data.get("financials", {})
        npv_krw = financials.get("npv_public_krw", 0)
    
    # 세대수 기반 기본 확장
    if household_count >= 30:
        spaces.append(CommunitySpace(
            space_name="다목적 활동실",
            function="운동, 취미 활동, 세미나",
            operation_method="예약제",
            capacity=30,
            equipment=["요가 매트", "접이식 테이블", "음향 시설"]
        ))
    
    # M2 기반 프리미엄 공간 확장 (평당 1,500만원 이상)
    if land_value_per_pyeong >= 15_000_000:
        spaces.append(CommunitySpace(
            space_name="북카페 라운지",
            function="독서, 담소, 소규모 모임",
            operation_method="자유 이용 (오전 9시-오후 9시)",
            capacity=20,
            equipment=["서가", "안락 의자", "커피 머신", "조명", "Wi-Fi"]
        ))
        
        spaces.append(CommunitySpace(
            space_name="세미나실",
            function="교육, 강연, 워크숍",
            operation_method="예약제 (3일 전 신청)",
            capacity=30,
            equipment=["프로젝터", "화상회의 시스템", "화이트보드", "개별 책상"]
        ))
        
        logger.info(f"✨ M2 프리미엄 공간 추가: 평당 {land_value_per_pyeong:,}원 (북카페, 세미나실)")
    
    # M2 기반 표준 확장 (평당 1,000~1,500만원)
    elif land_value_per_pyeong >= 10_000_000:
        spaces.append(CommunitySpace(
            space_name="공유 독서실",
            function="개인 학습, 재택근무 공간",
            operation_method="자유 이용 (선착순)",
            capacity=15,
            equipment=["개인 책상", "독서등", "공용 프린터", "Wi-Fi"]
        ))
        
        logger.info(f"📚 M2 표준 공간 추가: 평당 {land_value_per_pyeong:,}원 (독서실)")
    
    # M5 기반 추가 확장 (M2가 없을 경우 대체)
    elif npv_krw >= 300_000_000 and land_value_per_pyeong < 10_000_000:
        spaces.append(CommunitySpace(
            space_name="공유 독서실",
            function="개인 학습, 재택근무 공간",
            operation_method="자유 이용 (선착순)",
            capacity=15,
            equipment=["개인 책상", "독서등", "공용 프린터", "Wi-Fi"]
        ))
        
        logger.info(f"💰 M5 기반 공간 추가: NPV {npv_krw:,}원 (독서실)")
        
        if npv_krw >= 500_000_000:
            spaces.append(CommunitySpace(
                space_name="피트니스 룸",
                function="기초 운동, 건강 관리",
                operation_method="자유 이용 (오전 6시-오후 10시)",
                capacity=10,
                equipment=["런닝머신", "사이클", "아령", "요가 매트"]
            ))
            
            logger.info(f"💪 M5 고수익 공간 추가: NPV {npv_krw:,}원 (피트니스)")
    
    return spaces


def _define_community_programs(housing_type: str, m1_data: Optional[Dict] = None) -> List[CommunityProgram]:
    """
    프로그램 구성
    
    **M1 연동 로직**:
    - 역세권 → 취업·창업 네트워킹 강화 (청년형)
    - 공원 인근 → 야외 활동 프로그램 추가
    - 상업시설 밀집 → 지역 연계 프로그램 확대
    """
    base_programs = [
        CommunityProgram(
            program_name="입주 초기 오리엔테이션",
            frequency="연 1회 (입주 시기별)",
            target_audience="신규 입주자 전체",
            format="집합 교육",
            participation_type="필수"
        ),
        CommunityProgram(
            program_name="월간 생활 워크숍",
            frequency="월 1회",
            target_audience="입주자 전체 (자율 참여)",
            format="주제별 워크숍 (예: 생활 금융, 건강 관리)",
            participation_type="자율"
        ),
        CommunityProgram(
            program_name="지역 연계 프로그램",
            frequency="분기 1회",
            target_audience="입주자 및 지역 주민",
            format="지역사회 협력 행사 (예: 벼룩시장, 재능 나눔)",
            participation_type="선택"
        )
    ]
    
    # M1 기반 프로그램 확장
    has_park_access = False
    is_near_station = False
    
    if m1_data:
        # 공원 접근성
        env = m1_data.get("environment", {})
        park_distance = env.get("nearest_park_distance_m", 9999)
        has_park_access = park_distance <= 500
        
        # 역세권 확인
        transit = m1_data.get("transit_access", {})
        station_distance = transit.get("nearest_station_distance_m", 9999)
        is_near_station = station_distance <= 800
    
    if "청년" in housing_type:
        program_format = "소규모 네트워킹 모임"
        if is_near_station:
            program_format += " (역세권 입지 활용, 외부 멘토 초청 용이)"
        
        base_programs.append(CommunityProgram(
            program_name="취업·창업 네트워킹",
            frequency="격월 1회",
            target_audience="청년 입주자",
            format=program_format,
            participation_type="자율"
        ))
        
        # 역세권 → 추가 프로그램
        if is_near_station:
            base_programs.append(CommunityProgram(
                program_name="직장인 교류회",
                frequency="격월 1회",
                target_audience="직장 생활 청년",
                format="퇴근 후 소규모 모임 (저녁 7-9시)",
                participation_type="자율"
            ))
    
    elif "신혼" in housing_type:
        base_programs.append(CommunityProgram(
            program_name="육아 정보 교류회",
            frequency="격월 1회",
            target_audience="신혼부부 입주자",
            format="육아 경험 공유 및 정보 교환",
            participation_type="자율"
        ))
    
    # 공원 인근 → 야외 활동 프로그램
    if has_park_access:
        base_programs.append(CommunityProgram(
            program_name="주말 야외 활동",
            frequency="월 1회 (주말)",
            target_audience="입주자 전체",
            format="인근 공원 활용 산책, 운동, 소규모 모임",
            participation_type="선택"
        ))
    
    return base_programs


def _define_operation_structure(household_count: int, m6_data: Optional[Dict] = None) -> OperationStructure:
    """
    운영 구조 정의
    
    **M6 연동 로직**:
    - LH 점수 80점 이상 → LH 직접 운영 (신뢰도 높음)
    - LH 점수 60-79점 → 협력 운영 (LH + 전문 운영사)
    - LH 점수 60점 미만 → 전문 위탁 운영사 (관리 강화)
    """
    # M6 LH 심사 점수
    lh_score = 0
    if m6_data:
        scores = m6_data.get("scores", {})
        lh_score = scores.get("total", 0)
    
    # LH 점수 기반 운영 모델 결정
    if lh_score >= 80:
        operator = "LH 직접 운영"
        cost_note = "공용 관리비에 포함 (LH 직영으로 인한 비용 절감)"
    elif lh_score >= 60:
        if household_count >= 50:
            operator = "협력 운영 (LH + 전문 운영사)"
        else:
            operator = "LH 협력 운영"
        cost_note = "공용 관리비에 포함 (일부 전문 운영사 지원)"
    else:
        operator = "전문 위탁 운영사"
        cost_note = "공용 관리비에 포함 (전문 운영사 관리 강화)"
    
    return OperationStructure(
        operator_type=operator,
        lh_role="운영 감독, 프로그램 승인, 예산 관리" + (", 품질 관리 강화" if lh_score < 70 else ""),
        resident_role="프로그램 참여, 공간 이용, 자율 규약 준수",
        dispute_resolution="관리 규정에 따른 조정 절차 시행, 필요 시 LH 중재",
        cost_structure=cost_note
    )


def _define_sustainability_plan(household_count: int, m6_data: Optional[Dict] = None) -> SustainabilityPlan:
    """
    지속 가능성 계획
    
    **M6 연동 로직**:
    - LH 점수 높음 → 적극적 확대 계획
    - LH 점수 중간 → 점진적 확대 계획
    - LH 점수 낮음 → 보수적 운영 + 개선 계획
    """
    # M6 LH 심사 점수
    lh_score = 0
    if m6_data:
        scores = m6_data.get("scores", {})
        lh_score = scores.get("total", 0)
    
    # 참여 강요 금지 원칙
    base_participation = "자율 참여 원칙 준수, 프로그램 참여 여부는 전적으로 입주자 의사에 따름"
    
    # 점수 기반 계획 수립
    if lh_score >= 80:
        overload_prevention = "월 2회 기본 프로그램 + 선택적 추가 프로그램 (참여 부담 최소화)"
        cost_management = f"세대당 월 2만원 이하 (공용 관리비 포함), {household_count}세대 기준 총 월 {household_count * 20000:,}원 이내"
        expansion_plan = "1년 차 안정화 후 2년 차부터 프로그램 다양화, 3년 차 지역 네트워크 확대"
        contingency = "입주율 70% 이상 유지 시 정상 운영, 이하 시 프로그램 규모 축소 및 LH 지원 요청"
    elif lh_score >= 60:
        overload_prevention = "월 2회 기본 프로그램 유지, 추가 프로그램은 입주자 수요 조사 후 결정"
        cost_management = f"세대당 월 1.5만원 이하, {household_count}세대 기준 총 월 {household_count * 15000:,}원 이내"
        expansion_plan = "1년 차 안정화 및 운영 평가, 2년 차 점진적 확대 검토"
        contingency = "입주율 저조 시 프로그램 축소 및 운영 방식 재검토"
    else:
        overload_prevention = "월 1-2회 기본 프로그램, 소규모 운영으로 부담 최소화"
        cost_management = f"세대당 월 1만원 이하, {household_count}세대 기준 총 월 {household_count * 10000:,}원 이내"
        expansion_plan = "1년 차 기본 운영 안정화 우선, 2년 차 개선 계획 수립"
        contingency = "운영 중단 시 LH 직접 관리로 전환, 기본 공간 유지 관리만 진행"
    
    return SustainabilityPlan(
        overload_prevention=overload_prevention,
        no_forced_participation=base_participation,
        cost_management=cost_management,
        expansion_plan=expansion_plan,
        contingency_plan=contingency
    )
    return SustainabilityPlan(
        overload_prevention=[
            "프로그램 참여는 자율 원칙 (강요 금지)",
            "공간 이용 예약 시스템으로 과밀 방지",
            "연간 프로그램 수를 적정 수준으로 제한"
        ],
        participation_guidelines="자율 참여 원칙하에, 최소 참여율 목표는 권장 사항으로만 운영",
        budget_control="연간 운영비는 세대당 월 2만원 이내 수준으로 제한하며, 초과 시 프로그램 축소",
        contingency_plan="운영사 교체 또는 프로그램 중단 시, LH 직접 운영 전환 또는 간소화된 기본 운영 모델 적용"
    )


def m7_to_summary(m7_plan: M7CommunityPlan) -> M7Summary:
    """M7CommunityPlan을 M7Summary로 변환"""
    return M7Summary(
        primary_resident_type=m7_plan.resident_persona.primary_type.value,
        community_goal_summary=m7_plan.community_goals.qualitative_goals[0] if m7_plan.community_goals.qualitative_goals else "커뮤니티 목표 수립 중",
        key_programs_count=len(m7_plan.programs),
        operation_model=m7_plan.operation_structure.operator_type,
        sustainability_score=None,
        space_count=len(m7_plan.community_spaces),
        monthly_program_frequency=m7_plan.community_goals.monthly_programs_target,
        participation_target_pct=m7_plan.community_goals.participation_rate_target
    )
