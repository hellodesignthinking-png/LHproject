"""
M4 Capacity Service V2
======================

건축규모검토 서비스 V2 - 완전 재구현

핵심 원칙:
1. INTERPRETATION 모듈 - 물리적 규모 산출만
2. 판단/사업성/감정평가 절대 금지
3. 용적률 MAX vs 주차 가능 대안 동시 제시

Author: ZeroSite Architecture Team
Date: 2025-12-17
Version: 2.0
"""

import logging
import math
from datetime import datetime
from typing import Dict, List, Tuple

from app.core.context.canonical_land import CanonicalLandContext
from app.core.context.housing_type_context import HousingTypeContext
from app.core.context.capacity_context_v2 import (
    CapacityContextV2,
    CapacityScale,
    GFABreakdown,
    MassingOption,
    ParkingSolution,
    RampCondition,
    UnitSummary,
    RampFeasibility,
    ParkingType
)
from app.modules.m4_capacity.schematic_generator import SchematicDrawingGenerator

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 내부 상수 (Internal Presets)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class M4Constants:
    """M4 계산 상수"""
    
    # GFA 분해 비율 (내부 Preset)
    NIA_RATIO = 0.60           # 전용면적 60%
    COMMON_CORE_RATIO = 0.15   # 코어 15%
    COMMON_CORRIDOR_RATIO = 0.10  # 복도 10%
    COMMON_SHARED_RATIO = 0.05    # 공용공간 5%
    MECHANICAL_RATIO = 0.06       # 기계실 6%
    LOSS_RATIO = 0.04             # 손실 4%
    
    # 주차 기준
    PARKING_RATIO_DEFAULT = 0.6   # 세대당 0.6대 (기본)
    PARKING_RATIO_URBAN = 0.5     # 세대당 0.5대 (도심)
    PARKING_RATIO_SUBURBAN = 0.8  # 세대당 0.8대 (외곽)
    
    # 램프 최소 기준
    RAMP_MIN_WIDTH_ONEWAY = 3.3   # 일방향 최소폭 (m)
    RAMP_MIN_WIDTH_TWOWAY = 5.5   # 양방향 최소폭 (m)
    RAMP_MIN_LENGTH = 6.0         # 직선구간 최소 (m)
    RAMP_MIN_TURNING_RADIUS = 6.0 # 회전반경 최소 (m)
    
    # 지하주차 효율
    PARKING_AREA_PER_SPACE = 27.5  # 대당 소요면적 (㎡)
    BASEMENT_HEIGHT = 2.3          # 지하층고 (m)
    
    # LH 유형별 표준 면적 (㎡)
    LH_UNIT_AREAS = {
        "youth": 30.0,              # 청년형
        "newlywed_1": 45.0,         # 신혼·신생아 I형
        "newlywed_2": 60.0,         # 신혼·신생아 II형
        "multi_child": 85.0,        # 다자녀형
        "senior": 40.0              # 고령자형
    }


class CapacityServiceV2:
    """
    건축규모검토 서비스 V2
    
    입력: CanonicalLandContext (M1), HousingTypeContext (M3)
    출력: CapacityContextV2 (6가지 필수 산출물)
    """
    
    def __init__(self):
        """서비스 초기화"""
        self.constants = M4Constants()
        self.schematic_generator = SchematicDrawingGenerator()
        logger.info("✅ M4 Capacity Service V2 initialized")
    
    def run(
        self,
        land_ctx: CanonicalLandContext,
        housing_type_ctx: HousingTypeContext
    ) -> CapacityContextV2:
        """
        건축규모 검토 실행
        
        Args:
            land_ctx: M1 토지정보 (READ-ONLY)
            housing_type_ctx: M3 주택유형 (READ-ONLY)
        
        Returns:
            CapacityContextV2 (frozen=True)
        """
        
        logger.info("="*80)
        logger.info("🏗️ M4 CAPACITY MODULE V2 - Physical Building Scale Analysis")
        logger.info(f"   Land: {land_ctx.area_sqm:,.1f}㎡ ({land_ctx.area_pyeong:,.1f}평)")
        logger.info(f"   Zone: {land_ctx.zone_type}")
        logger.info(f"   Legal FAR/BCR: {land_ctx.far}% / {land_ctx.bcr}%")
        logger.info(f"   Housing Type: {housing_type_ctx.selected_type_name}")
        logger.info("="*80)
        
        # Step 1: 법정 용적률 규모 산정
        legal_capacity = self._calculate_capacity_scale(
            land_ctx=land_ctx,
            housing_type_ctx=housing_type_ctx,
            target_far=land_ctx.far,
            target_bcr=land_ctx.bcr,
            scale_type="legal"
        )
        logger.info(f"✅ Legal Capacity: {legal_capacity.total_units}세대")
        
        # Step 2: 인센티브 용적률 규모 산정
        incentive_far = self._calculate_incentive_far(land_ctx)
        incentive_capacity = self._calculate_capacity_scale(
            land_ctx=land_ctx,
            housing_type_ctx=housing_type_ctx,
            target_far=incentive_far,
            target_bcr=land_ctx.bcr,
            scale_type="incentive"
        )
        logger.info(f"✅ Incentive Capacity: {incentive_capacity.total_units}세대")
        
        # Step 3: 물리적 매싱 대안 생성 (3~5개)
        massing_options = self._generate_massing_options(
            land_ctx=land_ctx,
            capacity_scale=incentive_capacity
        )
        logger.info(f"✅ Generated {len(massing_options)} massing options")
        
        # Step 4: 세대 구성 요약
        unit_summary = self._create_unit_summary(
            housing_type_ctx=housing_type_ctx,
            total_units=incentive_capacity.total_units
        )
        logger.info(f"✅ Unit Summary: {unit_summary.total_units}세대")
        
        # Step 5: 주차 해결안 (Alternative A & B)
        parking_solutions = self._generate_parking_solutions(
            land_ctx=land_ctx,
            incentive_capacity=incentive_capacity,
            unit_summary=unit_summary
        )
        logger.info(f"✅ Parking Solutions: A & B generated")
        
        # Step 6: 스키매틱 도면 생성
        from dataclasses import asdict
        context_data = {
            'site_area': land_ctx.area_sqm,
            'legal_bcr': land_ctx.bcr,
            'massing_options': [asdict(opt) for opt in massing_options],
            'unit_summary': asdict(unit_summary),
            'avg_unit_area': incentive_capacity.average_unit_area_sqm,
            'parking_solutions': {
                'alternative_A': asdict(parking_solutions['alternative_A']),
                'alternative_B': asdict(parking_solutions['alternative_B'])
            }
        }
        schematic_paths = self._prepare_schematic_paths(land_ctx.parcel_id, context_data)
        
        # 최종 Context 생성
        capacity_context = CapacityContextV2(
            legal_capacity=legal_capacity,
            incentive_capacity=incentive_capacity,
            massing_options=massing_options,
            unit_summary=unit_summary,
            parking_solutions=parking_solutions,
            schematic_drawing_paths=schematic_paths,
            calculation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            input_land_area_sqm=land_ctx.area_sqm,
            input_legal_far=land_ctx.far,
            input_incentive_far=incentive_far,
            input_housing_type=housing_type_ctx.selected_type_name,
            assumptions={
                "nia_ratio": self.constants.NIA_RATIO,
                "parking_ratio": self.constants.PARKING_RATIO_DEFAULT,
                "basement_efficiency": 0.85
            },
            constraints=[
                f"법정 건폐율: {land_ctx.bcr}%",
                f"법정 용적률: {land_ctx.far}%",
                f"도로폭: {land_ctx.road_width}m"
            ],
            calculation_notes=[
                "M4는 물리적 건축 규모만 산출합니다",
                "사업성 판단은 M5에서 수행합니다",
                "LH 의사결정은 M6에서 수행합니다"
            ]
        )
        
        logger.info("="*80)
        logger.info("✅ M4 CAPACITY CALCULATION COMPLETE")
        logger.info(f"   Legal: {legal_capacity.total_units}세대 / {legal_capacity.applied_far}%")
        logger.info(f"   Incentive: {incentive_capacity.total_units}세대 / {incentive_capacity.applied_far}%")
        logger.info(f"   Alternative A: {parking_solutions['alternative_A'].total_parking_spaces}대 주차")
        logger.info(f"   Alternative B: {parking_solutions['alternative_B'].total_parking_spaces}대 주차")
        logger.info("="*80)
        
        return capacity_context
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 내부 계산 메서드
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _calculate_incentive_far(self, land_ctx: CanonicalLandContext) -> float:
        """
        인센티브 용적률 계산
        
        일반적으로 법정 용적률 + 20~30% 완화
        (실제로는 지자체 조례 확인 필요)
        """
        base_far = land_ctx.far
        
        # 간단한 인센티브 로직 (실제로는 복잡)
        if base_far <= 200:
            incentive_far = base_far * 1.3  # +30%
        elif base_far <= 250:
            incentive_far = base_far * 1.25  # +25%
        else:
            incentive_far = base_far * 1.2   # +20%
        
        return round(incentive_far, 1)
    
    def _calculate_capacity_scale(
        self,
        land_ctx: CanonicalLandContext,
        housing_type_ctx: HousingTypeContext,
        target_far: float,
        target_bcr: float,
        scale_type: str
    ) -> CapacityScale:
        """
        용적률 기준 규모 산정
        
        Step 1: 최대 건축면적 = 대지면적 × BCR
        Step 2: 목표 연면적 = 대지면적 × FAR
        Step 3: GFA 분해 (NIA, 공용, 기계/손실)
        Step 4: 세대수 = NIA / 세대당 면적
        Step 5: 주차대수 = 세대수 × 주차비율
        """
        
        site_area = land_ctx.area_sqm
        
        # Step 1: 최대 건축면적
        max_footprint = site_area * (target_bcr / 100)
        
        # Step 2: 목표 연면적
        target_gfa = site_area * (target_far / 100)
        
        # Step 3: GFA 분해
        gfa_breakdown = self._breakdown_gfa(target_gfa)
        
        # Step 4: 세대수 산정
        unit_area = self.constants.LH_UNIT_AREAS.get(
            housing_type_ctx.selected_type,
            30.0  # 기본값
        )
        
        total_units = int(gfa_breakdown.nia_sqm / unit_area)
        
        # 세대 구성 (간단 버전 - 실제로는 M3 mix_ratio 사용)
        unit_type_dist = {
            f"{housing_type_ctx.selected_type_name}": total_units
        }
        
        # Step 5: 주차대수
        parking_ratio = self._determine_parking_ratio(land_ctx)
        required_parking = int(total_units * parking_ratio)
        
        return CapacityScale(
            applied_far=target_far,
            applied_bcr=target_bcr,
            max_footprint_sqm=max_footprint,
            target_gfa_sqm=target_gfa,
            gfa_breakdown=gfa_breakdown,
            total_units=total_units,
            unit_type_distribution=unit_type_dist,
            average_unit_area_sqm=unit_area,
            required_parking_spaces=required_parking,
            parking_ratio=parking_ratio
        )
    
    def _breakdown_gfa(self, total_gfa: float) -> GFABreakdown:
        """
        연면적 상세 분해
        
        Preset 비율:
        - NIA: 60%
        - 공용(코어/복도/공용): 15% + 10% + 5% = 30%
        - 기계/손실: 6% + 4% = 10%
        """
        c = self.constants
        
        nia_sqm = total_gfa * c.NIA_RATIO
        
        common_core = total_gfa * c.COMMON_CORE_RATIO
        common_corridor = total_gfa * c.COMMON_CORRIDOR_RATIO
        common_shared = total_gfa * c.COMMON_SHARED_RATIO
        common_total = common_core + common_corridor + common_shared
        
        mechanical = total_gfa * c.MECHANICAL_RATIO
        loss = total_gfa * c.LOSS_RATIO
        
        return GFABreakdown(
            total_gfa_sqm=total_gfa,
            nia_sqm=nia_sqm,
            nia_ratio=c.NIA_RATIO * 100,
            common_core_sqm=common_core,
            common_corridor_sqm=common_corridor,
            common_shared_sqm=common_shared,
            common_total_sqm=common_total,
            common_ratio=(c.COMMON_CORE_RATIO + c.COMMON_CORRIDOR_RATIO + c.COMMON_SHARED_RATIO) * 100,
            mechanical_sqm=mechanical,
            loss_sqm=loss,
            mechanical_loss_ratio=(c.MECHANICAL_RATIO + c.LOSS_RATIO) * 100
        )
    
    def _determine_parking_ratio(self, land_ctx: CanonicalLandContext) -> float:
        """
        주차 비율 결정
        
        도심/외곽에 따라 다름
        """
        # 간단 로직: 서울 주요 구는 0.5, 그 외 0.6
        urban_districts = ["강남구", "서초구", "송파구", "영등포구", "마포구"]
        
        if land_ctx.sigungu in urban_districts:
            return self.constants.PARKING_RATIO_URBAN
        else:
            return self.constants.PARKING_RATIO_DEFAULT
    
    def _generate_massing_options(
        self,
        land_ctx: CanonicalLandContext,
        capacity_scale: CapacityScale
    ) -> List[MassingOption]:
        """
        물리적 매싱 대안 생성 (3~5개)
        
        예시:
        - Option A: 2개동 × 15층
        - Option B: 3개동 × 10층
        - Option C: 1개동 × 20층
        - Option D: 4개동 × 8층
        """
        
        target_gfa = capacity_scale.target_gfa_sqm
        target_units = capacity_scale.total_units
        site_area = land_ctx.area_sqm
        
        options = []
        
        # Option 1: 2개동 × 중층
        opt1_buildings = 2
        opt1_floors = max(10, int(target_gfa / (capacity_scale.max_footprint_sqm * opt1_buildings)))
        opt1_floor_area = capacity_scale.max_footprint_sqm / opt1_buildings
        opt1_units_per_floor = int(target_units / (opt1_buildings * opt1_floors))
        
        options.append(MassingOption(
            option_id="A",
            option_name="2개동 중층형",
            building_count=opt1_buildings,
            floors_per_building=opt1_floors,
            standard_floor_area_sqm=opt1_floor_area,
            units_per_floor=opt1_units_per_floor,
            achieved_gfa_sqm=opt1_floor_area * opt1_floors * opt1_buildings,
            achieved_far=capacity_scale.applied_far * 0.95,
            far_achievement_rate=0.95,
            site_coverage_ratio=30.0,
            open_space_ratio=70.0,
            buildability_score=85.0,
            efficiency_score=90.0,
            remarks=["균형잡힌 배치", "시공성 양호"]
        ))
        
        # Option 2: 3개동 × 저층
        opt2_buildings = 3
        opt2_floors = max(8, int(target_gfa / (capacity_scale.max_footprint_sqm * opt2_buildings)))
        opt2_floor_area = capacity_scale.max_footprint_sqm / opt2_buildings
        opt2_units_per_floor = int(target_units / (opt2_buildings * opt2_floors))
        
        options.append(MassingOption(
            option_id="B",
            option_name="3개동 저층형",
            building_count=opt2_buildings,
            floors_per_building=opt2_floors,
            standard_floor_area_sqm=opt2_floor_area,
            units_per_floor=opt2_units_per_floor,
            achieved_gfa_sqm=opt2_floor_area * opt2_floors * opt2_buildings,
            achieved_far=capacity_scale.applied_far * 0.90,
            far_achievement_rate=0.90,
            site_coverage_ratio=35.0,
            open_space_ratio=65.0,
            buildability_score=90.0,
            efficiency_score=85.0,
            remarks=["저층 개발", "오픈스페이스 확보"]
        ))
        
        # Option 3: 1개동 × 고층
        opt3_buildings = 1
        opt3_floors = max(15, int(target_gfa / capacity_scale.max_footprint_sqm))
        opt3_floor_area = capacity_scale.max_footprint_sqm
        opt3_units_per_floor = int(target_units / opt3_floors)
        
        options.append(MassingOption(
            option_id="C",
            option_name="1개동 고층형",
            building_count=opt3_buildings,
            floors_per_building=opt3_floors,
            standard_floor_area_sqm=opt3_floor_area,
            units_per_floor=opt3_units_per_floor,
            achieved_gfa_sqm=opt3_floor_area * opt3_floors,
            achieved_far=capacity_scale.applied_far * 0.98,
            far_achievement_rate=0.98,
            site_coverage_ratio=20.0,
            open_space_ratio=80.0,
            buildability_score=75.0,
            efficiency_score=95.0,
            remarks=["용적률 극대화", "타워형 배치"]
        ))
        
        # Option 4: 4개동 × 초저층 (선택적)
        if site_area > 3000:  # 충분한 면적이 있을 때만
            opt4_buildings = 4
            opt4_floors = max(6, int(target_gfa / (capacity_scale.max_footprint_sqm * opt4_buildings)))
            opt4_floor_area = capacity_scale.max_footprint_sqm / opt4_buildings
            opt4_units_per_floor = int(target_units / (opt4_buildings * opt4_floors))
            
            options.append(MassingOption(
                option_id="D",
                option_name="4개동 초저층형",
                building_count=opt4_buildings,
                floors_per_building=opt4_floors,
                standard_floor_area_sqm=opt4_floor_area,
                units_per_floor=opt4_units_per_floor,
                achieved_gfa_sqm=opt4_floor_area * opt4_floors * opt4_buildings,
                achieved_far=capacity_scale.applied_far * 0.85,
                far_achievement_rate=0.85,
                site_coverage_ratio=40.0,
                open_space_ratio=60.0,
                buildability_score=95.0,
                efficiency_score=80.0,
                remarks=["저층 밀집", "마을형 배치"]
            ))
        
        return options[:5]  # 최대 5개
    
    def _create_unit_summary(
        self,
        housing_type_ctx: HousingTypeContext,
        total_units: int
    ) -> UnitSummary:
        """
        세대 구성 요약
        
        M3에서 받은 preferred_unit_type과 unit_mix_ratio 기반
        (현재는 단순화 - 실제로는 M3 데이터 활용)
        """
        
        # M3에서 받은 선호 유형
        preferred_type = housing_type_ctx.selected_type
        unit_area = self.constants.LH_UNIT_AREAS.get(preferred_type, 30.0)
        
        # 간단한 믹스 (실제로는 M3에서 unit_mix_ratio 활용)
        unit_mix_ratio = {
            f"{int(unit_area)}㎡": 1.0  # 100% 단일 타입 (간단화)
        }
        
        unit_count_by_type = {
            f"{int(unit_area)}㎡": total_units
        }
        
        unit_area_by_type = {
            f"{int(unit_area)}㎡": unit_area
        }
        
        return UnitSummary(
            total_units=total_units,
            preferred_unit_type=housing_type_ctx.selected_type_name,
            unit_mix_ratio=unit_mix_ratio,
            unit_count_by_type=unit_count_by_type,
            unit_area_by_type=unit_area_by_type,
            min_unit_area_sqm=unit_area,
            max_unit_area_sqm=unit_area,
            average_unit_area_sqm=unit_area
        )
    
    def _generate_parking_solutions(
        self,
        land_ctx: CanonicalLandContext,
        incentive_capacity: CapacityScale,
        unit_summary: UnitSummary
    ) -> Dict[str, ParkingSolution]:
        """
        주차 해결안 생성
        
        Alternative A: 용적률 최대화 → 주차 대응
        Alternative B: 주차 우선 → 용적률 조정
        """
        
        total_units = incentive_capacity.total_units
        required_parking = incentive_capacity.required_parking_spaces
        
        # ─────────────────────────────────────────────────
        # Alternative A: 용적률 최대화
        # ─────────────────────────────────────────────────
        
        # 필요한 지하 층수
        basement_floors_a = math.ceil(
            required_parking * self.constants.PARKING_AREA_PER_SPACE / 
            incentive_capacity.max_footprint_sqm
        )
        
        # 램프 조건 검토
        ramp_cond_a = self._check_ramp_conditions(
            land_ctx=land_ctx,
            basement_floors=basement_floors_a,
            required_parking=required_parking
        )
        
        alt_a = ParkingSolution(
            solution_type="alternative_A",
            solution_name="Alternative A: 용적률 최대화",
            parking_type=ParkingType.SELF_PARKING,
            total_parking_spaces=required_parking,
            self_parking_spaces=required_parking,
            basement_floors=basement_floors_a,
            ramp_condition=ramp_cond_a,
            mechanical_parking_spaces=0,
            mechanical_type=None,
            adjusted_total_units=None,
            adjusted_floors=None,
            adjusted_gfa_sqm=None,
            far_sacrifice_ratio=None,
            parking_achievability_score=self._calculate_parking_achievability(ramp_cond_a),
            remarks=[
                "인센티브 용적률 100% 활용",
                f"지하 {basement_floors_a}개층 필요",
                f"램프 상태: {ramp_cond_a.feasibility.value}"
            ]
        )
        
        # ─────────────────────────────────────────────────
        # Alternative B: 주차 우선
        # ─────────────────────────────────────────────────
        
        # 현실적 지하층수 제한 (예: 최대 2층)
        max_basement_floors = 2
        feasible_parking = int(
            (max_basement_floors * incentive_capacity.max_footprint_sqm) / 
            self.constants.PARKING_AREA_PER_SPACE * 0.85  # 효율 85%
        )
        
        # 주차 가능한 세대수로 역산 (feasible_parking이 required_parking보다 작으면 세대수 감소)
        if feasible_parking < required_parking:
            # 주차가 부족하면 세대수를 줄여야 함
            adjusted_units = int(feasible_parking / incentive_capacity.parking_ratio)
            adjusted_units = min(adjusted_units, total_units)  # 원래보다 많아질 수 없음
        else:
            # 주차가 충분하면 세대수 유지
            adjusted_units = total_units
            feasible_parking = required_parking
        
        # 용적률 희생
        far_sacrifice = 1.0 - (adjusted_units / total_units) if total_units > 0 else 0.0
        
        # 램프 조건 (더 유리)
        ramp_cond_b = self._check_ramp_conditions(
            land_ctx=land_ctx,
            basement_floors=max_basement_floors,
            required_parking=feasible_parking
        )
        
        alt_b = ParkingSolution(
            solution_type="alternative_B",
            solution_name="Alternative B: 주차 우선",
            parking_type=ParkingType.SELF_PARKING,
            total_parking_spaces=feasible_parking,
            self_parking_spaces=feasible_parking,
            basement_floors=max_basement_floors,
            ramp_condition=ramp_cond_b,
            mechanical_parking_spaces=0,
            mechanical_type=None,
            adjusted_total_units=adjusted_units,
            adjusted_floors=int(incentive_capacity.total_units / adjusted_units * 
                               (incentive_capacity.target_gfa_sqm / incentive_capacity.max_footprint_sqm)),
            adjusted_gfa_sqm=incentive_capacity.target_gfa_sqm * (adjusted_units / total_units),
            far_sacrifice_ratio=far_sacrifice,
            parking_achievability_score=self._calculate_parking_achievability(ramp_cond_b),
            remarks=[
                f"현실적 지하 {max_basement_floors}개층",
                f"세대수 {total_units} → {adjusted_units} (조정)",
                f"용적률 {far_sacrifice*100:.1f}% 희생",
                f"램프 상태: {ramp_cond_b.feasibility.value}"
            ]
        )
        
        return {
            "alternative_A": alt_a,
            "alternative_B": alt_b
        }
    
    def _check_ramp_conditions(
        self,
        land_ctx: CanonicalLandContext,
        basement_floors: int,
        required_parking: int
    ) -> RampCondition:
        """
        램프 물리적 조건 검토
        
        최소 기준:
        - 폭: 3.3m (일방향) or 5.5m (양방향)
        - 길이: 6m 이상
        - 회전반경: 6m 이상
        """
        
        # 간단한 추정 로직
        site_area = land_ctx.area_sqm
        frontage = land_ctx.road_width
        
        # 람프 폭 (면적에 따라)
        if site_area > 3000:
            ramp_width = self.constants.RAMP_MIN_WIDTH_TWOWAY
        else:
            ramp_width = self.constants.RAMP_MIN_WIDTH_ONEWAY
        
        # 램프 길이 (깊이에 비례)
        ramp_length = max(
            self.constants.RAMP_MIN_LENGTH,
            basement_floors * 3.0  # 층당 3m
        )
        
        # 회전반경 (부지 형태 고려)
        turning_radius = min(
            math.sqrt(site_area) * 0.3,
            15.0  # 최대 15m
        )
        
        # 비주거 면적 (램프 + 진입부)
        non_residential = ramp_width * ramp_length * 1.5
        
        # 판정
        issues = []
        
        if ramp_width < self.constants.RAMP_MIN_WIDTH_ONEWAY:
            issues.append("램프 폭 부족")
        
        if ramp_length < self.constants.RAMP_MIN_LENGTH:
            issues.append("램프 길이 부족")
        
        if turning_radius < self.constants.RAMP_MIN_TURNING_RADIUS:
            issues.append("회전반경 부족")
        
        if basement_floors > 4:
            issues.append("지하층수 과다")
        
        # 가능성 판정
        if len(issues) == 0:
            feasibility = RampFeasibility.FEASIBLE
        elif len(issues) <= 2:
            feasibility = RampFeasibility.MARGINAL
        else:
            feasibility = RampFeasibility.NOT_FEASIBLE
        
        return RampCondition(
            ramp_width_m=ramp_width,
            ramp_length_m=ramp_length,
            turning_radius_m=turning_radius,
            non_residential_area_sqm=non_residential,
            feasibility=feasibility,
            constraint_issues=issues
        )
    
    def _calculate_parking_achievability(self, ramp_cond: RampCondition) -> float:
        """
        주차 실현가능성 점수 (0-100)
        
        램프 조건 기반
        """
        if ramp_cond.feasibility == RampFeasibility.FEASIBLE:
            return 90.0
        elif ramp_cond.feasibility == RampFeasibility.MARGINAL:
            return 70.0
        else:
            return 40.0
    
    def _prepare_schematic_paths(self, parcel_id: str, context_data: Dict) -> Dict[str, str]:
        """
        스키매틱 도면 생성 및 경로 반환
        
        실제 SVG 생성 수행
        
        Args:
            parcel_id: Parcel identifier
            context_data: Data to generate schematics from
        
        Returns:
            Dict with paths to generated schematic files
        """
        try:
            # Generate all schematic drawings
            paths = self.schematic_generator.generate_all(
                capacity_data=context_data,
                parcel_id=parcel_id
            )
            
            logger.info(f"✅ Generated 4 schematic drawings for {parcel_id}")
            return paths
            
        except Exception as e:
            logger.error(f"⚠️ Schematic generation failed: {e}")
            # Return placeholder paths on failure
            base_path = f"/schematics/{parcel_id}"
            return {
                "ground_layout": f"{base_path}/ground_layout.svg",
                "standard_floor": f"{base_path}/standard_floor.svg",
                "basement_parking": f"{base_path}/basement_parking.svg",
                "massing_comparison": f"{base_path}/massing_comparison.svg"
            }


__all__ = ["CapacityServiceV2", "M4Constants"]
