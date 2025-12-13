"""
ZeroSite v24.1 - Relaxation Engine
완화 규정 6종 자동 적용 엔진

Author: ZeroSite Development Team
Version: 24.1.0
Created: 2025-12-12
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class RelaxationType(Enum):
    """완화 규정 종류"""
    DAYLIGHT = "daylight"  # 일조권 완화
    DISTRICT_UNIT = "district_unit"  # 지구단위계획구역
    PUBLIC_CONTRIBUTION = "public_contribution"  # 공공기여
    GREEN_BUILDING = "green_building"  # 녹색건축
    BARRIER_FREE = "barrier_free"  # 무장애 설계
    URBAN_REGEN = "urban_regen"  # 도시재생


@dataclass
class RelaxationResult:
    """완화 규정 적용 결과"""
    # 적용된 완화 규정
    applied_relaxations: List[str]
    
    # 완화 전/후 비교
    original_far: float
    relaxed_far: float
    far_increase: float
    far_increase_percentage: float
    
    original_bcr: float
    relaxed_bcr: float
    bcr_increase: float
    
    original_height: float
    relaxed_height: float
    height_increase: float
    
    # 세부 완화 내역
    daylight_relaxation: float  # %
    district_unit_relaxation: float  # %
    public_contribution_relaxation: float  # %
    green_building_relaxation: float  # %
    barrier_free_relaxation: float  # %
    urban_regen_relaxation: float  # %
    
    # 완화 조건 충족 여부
    daylight_qualified: bool
    district_unit_qualified: bool
    public_qualified: bool
    green_qualified: bool
    barrier_free_qualified: bool
    urban_regen_qualified: bool
    
    # 추가 정보
    total_relaxation_percentage: float
    relaxation_notes: List[str]
    compliance_issues: List[str]


class RelaxationEngineV241:
    """
    완화 규정 자동 적용 엔진
    
    기능:
    1. 6가지 완화 규정 자동 판별
    2. 조건 충족 시 용적률/건폐율/높이 완화
    3. 최종 개발 가능 규모 산출
    """
    
    def __init__(self):
        """엔진 초기화"""
        # 완화 규정별 기본 완화율 (%)
        self.relaxation_rates = {
            RelaxationType.DAYLIGHT: 10.0,  # 일조권 완화: 최대 10%
            RelaxationType.DISTRICT_UNIT: 20.0,  # 지구단위: 최대 20%
            RelaxationType.PUBLIC_CONTRIBUTION: 15.0,  # 공공기여: 최대 15%
            RelaxationType.GREEN_BUILDING: 5.0,  # 녹색건축: 최대 5%
            RelaxationType.BARRIER_FREE: 5.0,  # 무장애: 최대 5%
            RelaxationType.URBAN_REGEN: 15.0  # 도시재생: 최대 15%
        }
        
        # 지역별 완화 가능 여부
        self.zone_relaxation_allowed = {
            "제1종일반주거지역": ["daylight", "public_contribution", "green_building"],
            "제2종일반주거지역": ["daylight", "district_unit", "public_contribution", "green_building", "barrier_free"],
            "제3종일반주거지역": ["daylight", "district_unit", "public_contribution", "green_building", "barrier_free", "urban_regen"],
            "준주거지역": ["daylight", "district_unit", "public_contribution", "green_building", "barrier_free", "urban_regen"]
        }
    
    def apply_relaxation(
        self,
        zone_type: str,
        original_far: float,
        original_bcr: float,
        original_height: float,
        land_area: float,
        is_district_unit: bool = False,
        public_contribution_area: float = 0.0,
        is_green_building: bool = True,
        is_barrier_free: bool = True,
        is_urban_regen_area: bool = False
    ) -> RelaxationResult:
        """
        완화 규정 적용
        
        Args:
            zone_type: 용도지역
            original_far: 법정 용적률 (%)
            original_bcr: 법정 건폐율 (%)
            original_height: 법정 높이 제한 (m)
            land_area: 대지면적 (㎡)
            is_district_unit: 지구단위계획구역 여부
            public_contribution_area: 공공기여 면적 (㎡)
            is_green_building: 녹색건축 인증 여부
            is_barrier_free: 무장애 설계 여부
            is_urban_regen_area: 도시재생구역 여부
        
        Returns:
            RelaxationResult: 완화 적용 결과
        """
        
        # 적용 가능한 완화 규정 확인
        allowed_relaxations = self.zone_relaxation_allowed.get(zone_type, [])
        
        applied_relaxations = []
        relaxation_notes = []
        compliance_issues = []
        
        # 완화율 초기화
        total_far_increase = 0.0
        total_bcr_increase = 0.0
        total_height_increase = 0.0
        
        # 각 완화 규정별 적용 여부 및 완화율
        daylight_relax = 0.0
        daylight_qualified = False
        
        district_unit_relax = 0.0
        district_unit_qualified = False
        
        public_contrib_relax = 0.0
        public_qualified = False
        
        green_relax = 0.0
        green_qualified = False
        
        barrier_free_relax = 0.0
        barrier_free_qualified = False
        
        urban_regen_relax = 0.0
        urban_regen_qualified = False
        
        # 1. 일조권 완화 (대지면적 > 1000㎡)
        if "daylight" in allowed_relaxations and land_area > 1000:
            daylight_relax = self.relaxation_rates[RelaxationType.DAYLIGHT]
            total_far_increase += daylight_relax
            daylight_qualified = True
            applied_relaxations.append("일조권 완화")
            relaxation_notes.append(f"일조권 완화: +{daylight_relax}% (대지면적 {land_area:.0f}㎡ > 1000㎡)")
        
        # 2. 지구단위계획구역
        if "district_unit" in allowed_relaxations and is_district_unit:
            district_unit_relax = self.relaxation_rates[RelaxationType.DISTRICT_UNIT]
            total_far_increase += district_unit_relax
            district_unit_qualified = True
            applied_relaxations.append("지구단위계획구역 완화")
            relaxation_notes.append(f"지구단위계획 완화: +{district_unit_relax}%")
        
        # 3. 공공기여 (기여면적 > 대지면적의 10%)
        if "public_contribution" in allowed_relaxations and public_contribution_area > (land_area * 0.1):
            public_contrib_relax = self.relaxation_rates[RelaxationType.PUBLIC_CONTRIBUTION]
            contribution_ratio = (public_contribution_area / land_area) * 100
            actual_relaxation = min(public_contrib_relax, contribution_ratio * 0.5)
            total_far_increase += actual_relaxation
            public_qualified = True
            applied_relaxations.append("공공기여 완화")
            relaxation_notes.append(f"공공기여 완화: +{actual_relaxation:.1f}% (기여 {contribution_ratio:.1f}%)")
        
        # 4. 녹색건축 인증
        if "green_building" in allowed_relaxations and is_green_building:
            green_relax = self.relaxation_rates[RelaxationType.GREEN_BUILDING]
            total_far_increase += green_relax
            total_height_increase += 3.0  # 3m 추가
            green_qualified = True
            applied_relaxations.append("녹색건축 인증")
            relaxation_notes.append(f"녹색건축 완화: +{green_relax}% 및 높이 +3m")
        
        # 5. 무장애 설계
        if "barrier_free" in allowed_relaxations and is_barrier_free:
            barrier_free_relax = self.relaxation_rates[RelaxationType.BARRIER_FREE]
            total_far_increase += barrier_free_relax
            barrier_free_qualified = True
            applied_relaxations.append("무장애 설계")
            relaxation_notes.append(f"무장애 설계 완화: +{barrier_free_relax}%")
        
        # 6. 도시재생구역
        if "urban_regen" in allowed_relaxations and is_urban_regen_area:
            urban_regen_relax = self.relaxation_rates[RelaxationType.URBAN_REGEN]
            total_far_increase += urban_regen_relax
            total_height_increase += 5.0  # 5m 추가
            urban_regen_qualified = True
            applied_relaxations.append("도시재생구역")
            relaxation_notes.append(f"도시재생 완화: +{urban_regen_relax}% 및 높이 +5m")
        
        # 완화 적용 후 최종 값 계산
        relaxed_far = original_far * (1 + total_far_increase / 100)
        relaxed_bcr = original_bcr * (1 + total_bcr_increase / 100)
        relaxed_height = original_height + total_height_increase
        
        # 상한선 적용 (용도지역별 최대 완화율)
        max_far_by_zone = {
            "제1종일반주거지역": 200,
            "제2종일반주거지역": 250,
            "제3종일반주거지역": 300,
            "준주거지역": 500
        }
        
        max_allowed_far = max_far_by_zone.get(zone_type, original_far * 1.5)
        if relaxed_far > max_allowed_far:
            compliance_issues.append(f"완화 후 용적률({relaxed_far:.1f}%)이 상한({max_allowed_far}%)을 초과하여 조정됨")
            relaxed_far = max_allowed_far
        
        return RelaxationResult(
            applied_relaxations=applied_relaxations,
            original_far=original_far,
            relaxed_far=relaxed_far,
            far_increase=relaxed_far - original_far,
            far_increase_percentage=((relaxed_far - original_far) / original_far) * 100 if original_far > 0 else 0,
            original_bcr=original_bcr,
            relaxed_bcr=relaxed_bcr,
            bcr_increase=relaxed_bcr - original_bcr,
            original_height=original_height,
            relaxed_height=relaxed_height,
            height_increase=total_height_increase,
            daylight_relaxation=daylight_relax,
            district_unit_relaxation=district_unit_relax,
            public_contribution_relaxation=public_contrib_relax,
            green_building_relaxation=green_relax,
            barrier_free_relaxation=barrier_free_relax,
            urban_regen_relaxation=urban_regen_relax,
            daylight_qualified=daylight_qualified,
            district_unit_qualified=district_unit_qualified,
            public_qualified=public_qualified,
            green_qualified=green_qualified,
            barrier_free_qualified=barrier_free_qualified,
            urban_regen_qualified=urban_regen_qualified,
            total_relaxation_percentage=total_far_increase,
            relaxation_notes=relaxation_notes,
            compliance_issues=compliance_issues
        )
    
    def get_available_relaxations(self, zone_type: str) -> List[str]:
        """해당 용도지역에서 적용 가능한 완화 규정 목록 반환"""
        return self.zone_relaxation_allowed.get(zone_type, [])
    
    def estimate_max_relaxation(self, zone_type: str, original_far: float) -> Dict[str, Any]:
        """
        이론적 최대 완화율 계산
        (모든 완화 조건을 만족했을 때)
        """
        allowed = self.get_available_relaxations(zone_type)
        max_relaxation = sum(self.relaxation_rates[RelaxationType[r.upper()]] for r in allowed)
        max_far = original_far * (1 + max_relaxation / 100)
        
        return {
            "zone_type": zone_type,
            "original_far": original_far,
            "max_relaxation_percentage": max_relaxation,
            "theoretical_max_far": max_far,
            "available_relaxations": allowed,
            "relaxation_count": len(allowed)
        }


# 테스트 코드
if __name__ == "__main__":
    engine = RelaxationEngineV241()
    
    # 테스트: 제3종일반주거지역, 대지면적 1500㎡
    result = engine.apply_relaxation(
        zone_type="제3종일반주거지역",
        original_far=200.0,
        original_bcr=60.0,
        original_height=50.0,
        land_area=1500.0,
        is_district_unit=True,
        public_contribution_area=200.0,
        is_green_building=True,
        is_barrier_free=True,
        is_urban_regen_area=False
    )
    
    print("=" * 60)
    print("완화 규정 적용 결과")
    print("=" * 60)
    print(f"적용된 완화: {', '.join(result.applied_relaxations)}")
    print(f"\n용적률:")
    print(f"  원래: {result.original_far}%")
    print(f"  완화: {result.relaxed_far:.1f}%")
    print(f"  증가: +{result.far_increase:.1f}% ({result.far_increase_percentage:.1f}%)")
    print(f"\n높이:")
    print(f"  원래: {result.original_height}m")
    print(f"  완화: {result.relaxed_height:.1f}m")
    print(f"  증가: +{result.height_increase}m")
    print(f"\n완화 내역:")
    for note in result.relaxation_notes:
        print(f"  - {note}")
    
    if result.compliance_issues:
        print(f"\n주의사항:")
        for issue in result.compliance_issues:
            print(f"  ⚠️ {issue}")
