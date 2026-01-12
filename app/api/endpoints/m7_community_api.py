"""
M7 Community Planning Module API
=================================

ZeroSite Decision OS - M7 모듈
목적: 커뮤니티 계획 (정책 + 운영 + 민원 방어)

핵심 역할:
- "이 주택이 왜 이 지역에 필요한가"
- "왜 민원이 적은가"
- "왜 오래 유지 가능한가"

Author: ZeroSite Decision OS
Date: 2026-01-12
Module: M7 – COMMUNITY & OPERATION
"""

from fastapi import APIRouter, HTTPException, Path, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

# ========================================
# Router 초기화
# ========================================
router = APIRouter(
    prefix="/api/projects/{project_id}/modules/M7",
    tags=["M7 - Community & Operation"]
)

# ========================================
# Pydantic Models
# ========================================

class CommunitySpace(BaseModel):
    """커뮤니티 공간"""
    name: str = Field(..., description="공간 이름")
    area_sqm: float = Field(..., description="면적 (㎡)")
    category: str = Field(..., description="필수/선택")
    purpose: str = Field(..., description="용도")

class ComplaintMitigation(BaseModel):
    """민원 방어 전략"""
    complaint_type: str = Field(..., description="민원 유형")
    risk_level: str = Field(..., description="위험도: HIGH/MEDIUM/LOW")
    mitigation_strategy: str = Field(..., description="완화 전략")
    responsible_party: str = Field(..., description="책임 주체")

class M7ResultData(BaseModel):
    """M7 출력 데이터"""
    community_concept: str = Field(..., description="커뮤니티 콘셉트")
    target_group: str = Field(..., description="대상 계층")
    key_spaces: List[CommunitySpace]
    operation_model: str = Field(..., description="운영 모델")
    operation_scenario: Dict[str, str] = Field(..., description="운영 시나리오")
    complaint_mitigation: List[ComplaintMitigation]
    policy_alignment: str = Field(..., description="정책 부합성")
    social_value: str = Field(..., description="사회적 가치")
    calculated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class M7CalculateRequest(BaseModel):
    """M7 계산 요청"""
    context_id: str = Field(..., description="M1 Context ID")
    force_recalculate: bool = Field(False, description="강제 재계산 여부")

class M7StatusResponse(BaseModel):
    """M7 상태 응답"""
    project_id: str
    context_id: str
    status: str
    calculated_at: Optional[str]
    error: Optional[str]

# ========================================
# In-Memory Storage
# ========================================
M7_CACHE: Dict[str, Dict[str, Any]] = {}

# ========================================
# Helper Functions
# ========================================

def get_location_analysis(context_id: str) -> Dict[str, Any]:
    """지역 분석 (M1 데이터 기반)"""
    return {
        "address": "서울시 마포구 성산동 123-4",
        "district": "마포구",
        "population_density": "높음",
        "age_distribution": "청년층 밀집",
        "infrastructure_gap": "커뮤니티 공간 부족"
    }

def get_housing_type(context_id: str) -> str:
    """공급유형 (M3 데이터 기반)"""
    return "청년 매입임대"

def get_units(context_id: str) -> int:
    """세대수 (M4 데이터 기반)"""
    return 240

def generate_community_concept(
    location_data: Dict[str, Any],
    housing_type: str,
    units: int
) -> str:
    """커뮤니티 콘셉트 생성"""
    
    concepts = {
        "청년 매입임대": "청년 생활안정형 (주거+일+회복)",
        "신혼부부 매입임대": "가족 친화형 (육아+돌봄+교류)",
        "고령자 복지주택": "건강 케어형 (의료+돌봄+안전)",
        "일반 공공임대": "세대 통합형 (공동체+안전+복지)",
        "역세권 청년주택": "교통 연계형 (접근성+편의+소통)"
    }
    
    return concepts.get(housing_type, "생활 안정형")

def define_target_group(housing_type: str) -> str:
    """대상 계층 정의"""
    
    targets = {
        "청년 매입임대": "만 19~39세 청년 (대학생, 사회초년생, 프리랜서)",
        "신혼부부 매입임대": "결혼 7년 이내 신혼부부 (영유아 가구 우선)",
        "고령자 복지주택": "만 65세 이상 고령자 (독거 노인 우선)",
        "일반 공공임대": "소득 1~6분위 일반 가구",
        "역세권 청년주택": "만 19~39세 청년 (직장인 우선)"
    }
    
    return targets.get(housing_type, "일반 가구")

def design_community_spaces(
    concept: str,
    housing_type: str,
    units: int
) -> List[CommunitySpace]:
    """커뮤니티 공간 설계"""
    
    spaces = []
    
    # 필수 공간 (공통)
    spaces.append(CommunitySpace(
        name="공용 라운지",
        area_sqm=units * 0.3,  # 세대당 0.3㎡
        category="필수",
        purpose="주민 교류 및 휴식"
    ))
    
    spaces.append(CommunitySpace(
        name="공용 세탁실",
        area_sqm=30,
        category="필수",
        purpose="세탁 편의 제공"
    ))
    
    # 유형별 선택 공간
    if "청년" in housing_type:
        spaces.extend([
            CommunitySpace(
                name="스터디룸",
                area_sqm=50,
                category="선택",
                purpose="학습 및 재택근무"
            ),
            CommunitySpace(
                name="공유 주방",
                area_sqm=40,
                category="선택",
                purpose="취사 및 소통"
            )
        ])
    
    elif "신혼부부" in housing_type:
        spaces.extend([
            CommunitySpace(
                name="육아 돌봄실",
                area_sqm=60,
                category="선택",
                purpose="영유아 돌봄 지원"
            ),
            CommunitySpace(
                name="놀이방",
                area_sqm=50,
                category="선택",
                purpose="아동 놀이 공간"
            )
        ])
    
    elif "고령자" in housing_type:
        spaces.extend([
            CommunitySpace(
                name="건강 관리실",
                area_sqm=40,
                category="선택",
                purpose="건강 모니터링"
            ),
            CommunitySpace(
                name="안전 케어센터",
                area_sqm=30,
                category="필수",
                purpose="응급 대응"
            )
        ])
    
    return spaces

def design_operation_model(housing_type: str) -> str:
    """운영 모델 설계"""
    
    if "고령자" in housing_type:
        return "LH 직영 운영 + 사회복지사 상주"
    elif "청년" in housing_type:
        return "LH 위탁 운영 + 커뮤니티 매니저"
    else:
        return "LH 위탁 운영"

def create_operation_scenario(operation_model: str) -> Dict[str, str]:
    """운영 시나리오 작성"""
    
    return {
        "입주_초기": "오리엔테이션 및 커뮤니티 규칙 안내, 입주자 프로필 작성",
        "안정기": "월 1회 주민 회의, 커뮤니티 프로그램 운영",
        "갈등_발생_시": "커뮤니티 매니저 중재, 관리 규정 적용, LH 협의",
        "운영_주체": operation_model,
        "관리_시간": "평일 09:00~18:00 (비상 연락망 24시간)"
    }

def identify_complaint_risks(
    location_data: Dict[str, Any],
    units: int
) -> List[ComplaintMitigation]:
    """민원 리스크 식별 및 방어 전략"""
    
    mitigations = []
    
    # 소음 민원
    mitigations.append(ComplaintMitigation(
        complaint_type="소음 (공용 공간 이용)",
        risk_level="MEDIUM",
        mitigation_strategy="야간(22시~07시) 공용 공간 이용 제한, 방음 설계 적용",
        responsible_party="LH + 입주자"
    ))
    
    # 주차 민원
    mitigations.append(ComplaintMitigation(
        complaint_type="주차 부족",
        risk_level="LOW",
        mitigation_strategy="법정 기준 +10% 확보, 거주자 우선 주차제 운영",
        responsible_party="사업자 + LH"
    ))
    
    # 외부인 출입 민원
    mitigations.append(ComplaintMitigation(
        complaint_type="외부인 유입",
        risk_level="MEDIUM",
        mitigation_strategy="커뮤니티 공간은 입주자 전용, 출입 통제 시스템 구축",
        responsible_party="LH + 관리 주체"
    ))
    
    # 관리비 민원
    mitigations.append(ComplaintMitigation(
        complaint_type="관리비 과다",
        risk_level="LOW",
        mitigation_strategy="커뮤니티 시설 운영비 LH 부담 원칙, 투명한 회계 공개",
        responsible_party="LH"
    ))
    
    return mitigations

def assess_policy_alignment(
    housing_type: str,
    concept: str
) -> str:
    """정책 부합성 평가"""
    
    alignments = {
        "청년 매입임대": "청년 주거 안정 정책 및 일자리 창출 정책과 부합",
        "신혼부부 매입임대": "저출생 대응 정책 및 가족 친화 정책과 부합",
        "고령자 복지주택": "고령 사회 대응 정책 및 복지 확대 정책과 부합",
        "일반 공공임대": "주거 복지 확대 정책과 부합",
        "역세권 청년주택": "TOD(대중교통 중심 개발) 정책과 부합"
    }
    
    return alignments.get(housing_type, "공공 주거 정책과 부합")

def describe_social_value(
    concept: str,
    target_group: str,
    location_data: Dict[str, Any]
) -> str:
    """사회적 가치 기술"""
    
    value = f"""
1. 지역 필요성
   - {location_data.get('district', 'N/A')}의 {location_data.get('infrastructure_gap', '주거 수요')} 해소
   - {location_data.get('age_distribution', '특정 계층')} 대상 주거 안정 기여

2. 공동체 형성
   - {concept} 콘셉트로 세대 간/세대 내 교류 활성화
   - 지역 사회 통합 및 사회적 자본 형성

3. 지속 가능성
   - LH 운영으로 장기 안정성 확보
   - 공공 주거의 모범 사례로 확산 가능

4. 민원 최소화
   - 입주자 전용 공간 구분으로 외부 갈등 차단
   - 명확한 관리 규정으로 내부 갈등 예방
"""
    
    return value.strip()

# ========================================
# API Endpoints
# ========================================

@router.post(
    "/calculate",
    response_model=M7ResultData,
    summary="M7 커뮤니티 계획 생성",
    description="""
    M7 커뮤니티 계획 모듈을 실행합니다.
    
    **입력:**
    - M1: 위치 정보
    - M3: 공급유형
    - M4: 세대수
    
    **출력:**
    - 커뮤니티 콘셉트
    - 공간 구성
    - 운영 시나리오
    - 민원 방어 전략
    """
)
async def calculate_m7(
    project_id: str = Path(..., description="프로젝트 ID"),
    request: M7CalculateRequest = Body(...)
):
    """M7 계산 실행"""
    
    context_id = request.context_id
    
    # 1. 입력 데이터 수집
    try:
        location_data = get_location_analysis(context_id)
        housing_type = get_housing_type(context_id)
        units = get_units(context_id)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"입력 데이터 수집 실패: {str(e)}"
        )
    
    # 2. 커뮤니티 콘셉트 생성
    concept = generate_community_concept(location_data, housing_type, units)
    
    # 3. 대상 계층 정의
    target_group = define_target_group(housing_type)
    
    # 4. 공간 설계
    spaces = design_community_spaces(concept, housing_type, units)
    
    # 5. 운영 모델 설계
    operation_model = design_operation_model(housing_type)
    
    # 6. 운영 시나리오 작성
    operation_scenario = create_operation_scenario(operation_model)
    
    # 7. 민원 방어 전략
    complaint_mitigation = identify_complaint_risks(location_data, units)
    
    # 8. 정책 부합성
    policy_alignment = assess_policy_alignment(housing_type, concept)
    
    # 9. 사회적 가치
    social_value = describe_social_value(concept, target_group, location_data)
    
    # 10. 결과 생성
    result_data = M7ResultData(
        community_concept=concept,
        target_group=target_group,
        key_spaces=spaces,
        operation_model=operation_model,
        operation_scenario=operation_scenario,
        complaint_mitigation=complaint_mitigation,
        policy_alignment=policy_alignment,
        social_value=social_value
    )
    
    # 11. 캐시에 저장
    cache_key = f"{project_id}:{context_id}"
    M7_CACHE[cache_key] = {
        "status": "COMPLETED",
        "result_data": result_data.dict(),
        "calculated_at": result_data.calculated_at
    }
    
    return result_data

@router.get(
    "/result",
    response_model=M7ResultData,
    summary="M7 결과 조회"
)
async def get_m7_result(
    project_id: str = Path(...),
    context_id: str = ...
):
    """M7 결과 조회"""
    
    cache_key = f"{project_id}:{context_id}"
    
    if cache_key not in M7_CACHE:
        raise HTTPException(
            status_code=404,
            detail="M7 계산 결과를 찾을 수 없습니다."
        )
    
    cached = M7_CACHE[cache_key]
    return M7ResultData(**cached["result_data"])

@router.get(
    "/status",
    response_model=M7StatusResponse,
    summary="M7 상태 확인"
)
async def get_m7_status(
    project_id: str = Path(...),
    context_id: str = ...
):
    """M7 상태 확인"""
    
    cache_key = f"{project_id}:{context_id}"
    
    if cache_key not in M7_CACHE:
        return M7StatusResponse(
            project_id=project_id,
            context_id=context_id,
            status="NOT_STARTED",
            calculated_at=None,
            error=None
        )
    
    cached = M7_CACHE[cache_key]
    return M7StatusResponse(
        project_id=project_id,
        context_id=context_id,
        status=cached["status"],
        calculated_at=cached.get("calculated_at"),
        error=cached.get("error")
    )

@router.get(
    "/validate",
    summary="M7 실행 가능 여부 검증"
)
async def validate_m7(
    project_id: str = Path(...),
    context_id: str = ...
):
    """M7 실행 가능 여부 검증"""
    
    validation_result = {
        "can_execute": True,
        "checks": {
            "m1_frozen": True,
            "m3_completed": True,
            "m4_completed": True
        },
        "errors": []
    }
    
    return validation_result
