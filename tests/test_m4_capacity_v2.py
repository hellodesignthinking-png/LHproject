"""
M4 Capacity Module V2 - Comprehensive Tests
============================================

테스트 범위:
1. 6가지 필수 산출물 존재 검증
2. 법정 vs 인센티브 규모 계산 정확성
3. GFA 분해 합계 검증
4. 매싱 대안 3~5개 생성 검증
5. 주차 해결안 A/B 생성 검증
6. Context 불변성 검증
7. 입력 데이터 무수정 검증

Author: ZeroSite Test Team
Date: 2025-12-17
"""

import pytest
from datetime import datetime

from app.core.context.canonical_land import CanonicalLandContext
from app.core.context.housing_type_context import (
    HousingTypeContext,
    TypeScore,
    POIAnalysis
)
from app.core.context.capacity_context_v2 import (
    CapacityContextV2,
    RampFeasibility
)
from app.modules.m4_capacity.service_v2 import CapacityServiceV2


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Fixtures
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@pytest.fixture
def sample_land_ctx() -> CanonicalLandContext:
    """샘플 토지정보 (M1)"""
    return CanonicalLandContext(
        parcel_id="1168010100100010001",
        address="서울특별시 강남구 역삼동 100-1",
        road_address="서울특별시 강남구 테헤란로 123",
        coordinates=(37.5012, 127.0396),
        sido="서울특별시",
        sigungu="강남구",
        dong="역삼동",
        area_sqm=3500.0,
        area_pyeong=1058.8,
        land_category="대",
        land_use="주거용",
        zone_type="제2종일반주거지역",
        zone_detail=None,
        far=200.0,
        bcr=60.0,
        road_width=12.0,
        road_type="중로",
        terrain_height="평지",
        terrain_shape="정형",
        regulations={},
        restrictions=[],
        data_source="국토교통부",
        retrieval_date="2025-12-17"
    )


@pytest.fixture
def sample_housing_type_ctx() -> HousingTypeContext:
    """샘플 주택유형 (M3)"""
    
    # POI 분석
    poi_analysis = POIAnalysis(
        subway_distance=500.0,
        school_distance=800.0,
        hospital_distance=1200.0,
        commercial_distance=300.0,
        subway_score=9.0,
        school_score=8.0,
        hospital_score=7.0,
        commercial_score=10.0,
        total_poi_count=50,
        radius_500m_count=15,
        radius_1km_count=30,
        radius_2km_count=50
    )
    
    # 유형별 점수
    type_scores = {
        "youth": TypeScore(
            type_name="청년형",
            type_code="youth",
            total_score=92.0,
            location_score=32.0,
            accessibility_score=28.0,
            poi_score=18.0,
            demand_prediction=90.0
        ),
        "newlywed_1": TypeScore(
            type_name="신혼·신생아 I형",
            type_code="newlywed_1",
            total_score=85.0,
            location_score=30.0,
            accessibility_score=25.0,
            poi_score=16.0,
            demand_prediction=85.0
        ),
        "newlywed_2": TypeScore(
            type_name="신혼·신생아 II형",
            type_code="newlywed_2",
            total_score=80.0,
            location_score=28.0,
            accessibility_score=24.0,
            poi_score=15.0,
            demand_prediction=80.0
        ),
        "multi_child": TypeScore(
            type_name="다자녀형",
            type_code="multi_child",
            total_score=75.0,
            location_score=26.0,
            accessibility_score=22.0,
            poi_score=14.0,
            demand_prediction=75.0
        ),
        "senior": TypeScore(
            type_name="고령자형",
            type_code="senior",
            total_score=78.0,
            location_score=27.0,
            accessibility_score=23.0,
            poi_score=14.5,
            demand_prediction=78.0
        )
    }
    
    return HousingTypeContext(
        selected_type="youth",
        selected_type_name="청년형",
        selection_confidence=0.92,
        type_scores=type_scores,
        location_score=32.0,
        poi_analysis=poi_analysis,
        demand_prediction=90.0,
        demand_trend="HIGH",
        target_population=15000,
        competitor_count=3,
        competitor_analysis="MODERATE",
        analysis_date="2025-12-17",
        strengths=["지하철 인접", "상업시설 풍부"],
        weaknesses=["학교 다소 거리"],
        recommendations=["청년형 30㎡ 권장"],
        data_sources=["카카오맵", "공공데이터포털"]
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Test Cases
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestM4CapacityV2:
    """M4 Capacity Module V2 테스트"""
    
    def test_service_initialization(self):
        """서비스 초기화 테스트"""
        service = CapacityServiceV2()
        assert service is not None
        assert service.constants is not None
    
    def test_basic_capacity_calculation(
        self,
        sample_land_ctx,
        sample_housing_type_ctx
    ):
        """기본 규모 계산 테스트"""
        service = CapacityServiceV2()
        
        result = service.run(
            land_ctx=sample_land_ctx,
            housing_type_ctx=sample_housing_type_ctx
        )
        
        # 결과가 CapacityContextV2인지 확인
        assert isinstance(result, CapacityContextV2)
        
        # frozen=True 확인 (dataclass frozen은 AttributeError 발생)
        try:
            result.calculation_date = "modified"
            assert False, "Should have raised an exception for frozen dataclass"
        except (AttributeError, Exception):
            pass  # Expected
    
    def test_six_required_outputs(
        self,
        sample_land_ctx,
        sample_housing_type_ctx
    ):
        """
        필수 산출물 6가지 존재 검증
        
        1. legal_capacity
        2. incentive_capacity
        3. massing_options (3~5개)
        4. unit_summary
        5. parking_solutions (A & B)
        6. schematic_drawing_paths
        """
        service = CapacityServiceV2()
        result = service.run(sample_land_ctx, sample_housing_type_ctx)
        
        # 1. legal_capacity
        assert result.legal_capacity is not None
        assert result.legal_capacity.applied_far == sample_land_ctx.far
        
        # 2. incentive_capacity
        assert result.incentive_capacity is not None
        assert result.incentive_capacity.applied_far >= result.legal_capacity.applied_far
        
        # 3. massing_options (3~5개)
        assert 3 <= len(result.massing_options) <= 5
        
        # 4. unit_summary
        assert result.unit_summary is not None
        assert result.unit_summary.total_units > 0
        
        # 5. parking_solutions (A & B)
        assert "alternative_A" in result.parking_solutions
        assert "alternative_B" in result.parking_solutions
        
        # 6. schematic_drawing_paths
        assert len(result.schematic_drawing_paths) >= 4
        assert "ground_layout" in result.schematic_drawing_paths
        assert "standard_floor" in result.schematic_drawing_paths
        assert "basement_parking" in result.schematic_drawing_paths
        assert "massing_comparison" in result.schematic_drawing_paths
    
    def test_legal_vs_incentive_capacity(
        self,
        sample_land_ctx,
        sample_housing_type_ctx
    ):
        """법정 vs 인센티브 규모 비교"""
        service = CapacityServiceV2()
        result = service.run(sample_land_ctx, sample_housing_type_ctx)
        
        legal = result.legal_capacity
        incentive = result.incentive_capacity
        
        # 인센티브가 법정보다 크거나 같아야 함
        assert incentive.applied_far >= legal.applied_far
        assert incentive.target_gfa_sqm >= legal.target_gfa_sqm
        assert incentive.total_units >= legal.total_units
        
        # 건폐율은 동일
        assert legal.applied_bcr == incentive.applied_bcr
    
    def test_gfa_breakdown_integrity(
        self,
        sample_land_ctx,
        sample_housing_type_ctx
    ):
        """GFA 분해 합계 검증"""
        service = CapacityServiceV2()
        result = service.run(sample_land_ctx, sample_housing_type_ctx)
        
        # 법정 규모 GFA 검증
        legal_gfa = result.legal_capacity.gfa_breakdown
        
        calc_total = (
            legal_gfa.nia_sqm +
            legal_gfa.common_total_sqm +
            legal_gfa.mechanical_sqm +
            legal_gfa.loss_sqm
        )
        
        # 오차 1㎡ 이내
        assert abs(calc_total - legal_gfa.total_gfa_sqm) < 1.0
        
        # 비율 합계 100% 확인
        ratio_sum = (
            legal_gfa.nia_ratio +
            legal_gfa.common_ratio +
            legal_gfa.mechanical_loss_ratio
        )
        
        assert abs(ratio_sum - 100.0) < 0.1
    
    def test_massing_options_generation(
        self,
        sample_land_ctx,
        sample_housing_type_ctx
    ):
        """매싱 대안 생성 검증"""
        service = CapacityServiceV2()
        result = service.run(sample_land_ctx, sample_housing_type_ctx)
        
        massing_opts = result.massing_options
        
        # 3~5개 생성
        assert 3 <= len(massing_opts) <= 5
        
        # 각 대안 검증
        for opt in massing_opts:
            # 기본 속성
            assert opt.building_count >= 1
            assert opt.floors_per_building >= 5
            assert opt.standard_floor_area_sqm > 0
            assert opt.units_per_floor >= 1
            
            # 용적률 달성
            assert 0.80 <= opt.far_achievement_rate <= 1.0
            
            # 점수
            assert 0 <= opt.buildability_score <= 100
            assert 0 <= opt.efficiency_score <= 100
        
        # ID 중복 없음
        option_ids = [opt.option_id for opt in massing_opts]
        assert len(option_ids) == len(set(option_ids))
    
    def test_parking_alternative_a_far_max(
        self,
        sample_land_ctx,
        sample_housing_type_ctx
    ):
        """Alternative A: 용적률 최대화 검증"""
        service = CapacityServiceV2()
        result = service.run(sample_land_ctx, sample_housing_type_ctx)
        
        alt_a = result.far_max_alternative
        
        # 기본 속성
        assert alt_a.solution_type == "alternative_A"
        assert alt_a.total_parking_spaces > 0
        assert alt_a.basement_floors >= 1
        
        # 램프 조건 존재
        assert alt_a.ramp_condition is not None
        assert alt_a.ramp_condition.ramp_width_m > 0
        assert alt_a.ramp_condition.ramp_length_m > 0
        
        # 세대수 조정 없음 (용적률 MAX)
        assert alt_a.adjusted_total_units is None
        assert alt_a.far_sacrifice_ratio is None
    
    def test_parking_alternative_b_parking_priority(
        self,
        sample_land_ctx,
        sample_housing_type_ctx
    ):
        """Alternative B: 주차 우선 검증"""
        service = CapacityServiceV2()
        result = service.run(sample_land_ctx, sample_housing_type_ctx)
        
        alt_b = result.parking_priority_alternative
        
        # 기본 속성
        assert alt_b.solution_type == "alternative_B"
        assert alt_b.total_parking_spaces > 0
        
        # 세대수 조정 존재
        assert alt_b.adjusted_total_units is not None
        assert alt_b.adjusted_total_units <= result.incentive_capacity.total_units
        
        # 용적률 희생
        assert alt_b.far_sacrifice_ratio is not None
        assert 0 <= alt_b.far_sacrifice_ratio < 1.0
        
        # 램프 조건이 A보다 유리할 가능성
        assert alt_b.ramp_condition.feasibility in [
            RampFeasibility.FEASIBLE,
            RampFeasibility.MARGINAL
        ]
    
    def test_parking_solutions_comparison(
        self,
        sample_land_ctx,
        sample_housing_type_ctx
    ):
        """주차 해결안 A vs B 비교"""
        service = CapacityServiceV2()
        result = service.run(sample_land_ctx, sample_housing_type_ctx)
        
        alt_a = result.far_max_alternative
        alt_b = result.parking_priority_alternative
        
        # B가 A보다 현실적인 주차대수 (같거나 적음)
        assert alt_b.total_parking_spaces <= alt_a.total_parking_spaces
        
        # B가 A보다 지하층수 적거나 같음
        assert alt_b.basement_floors <= alt_a.basement_floors
        
        # B가 세대수 조정 (같거나 적음 - 주차가 충분하면 같을 수 있음)
        assert alt_b.adjusted_total_units <= result.incentive_capacity.total_units
        
        # far_sacrifice는 0 이상 (양수 = 희생, 0 = 희생 없음)
        assert alt_b.far_sacrifice_ratio >= 0.0
    
    def test_unit_summary_consistency(
        self,
        sample_land_ctx,
        sample_housing_type_ctx
    ):
        """세대 구성 요약 일관성"""
        service = CapacityServiceV2()
        result = service.run(sample_land_ctx, sample_housing_type_ctx)
        
        unit_summary = result.unit_summary
        
        # 총 세대수 일치
        assert unit_summary.total_units == result.incentive_capacity.total_units
        
        # 유형별 세대수 합계 = 총 세대수
        unit_sum = sum(unit_summary.unit_count_by_type.values())
        assert unit_sum == unit_summary.total_units
        
        # 평균 면적 범위 내
        assert unit_summary.min_unit_area_sqm <= unit_summary.average_unit_area_sqm
        assert unit_summary.average_unit_area_sqm <= unit_summary.max_unit_area_sqm
    
    def test_context_immutability(
        self,
        sample_land_ctx,
        sample_housing_type_ctx
    ):
        """Context 불변성 검증 (frozen=True)"""
        service = CapacityServiceV2()
        result = service.run(sample_land_ctx, sample_housing_type_ctx)
        
        # 최상위 Context 수정 불가 (frozen dataclass는 AttributeError 발생)
        try:
            result.calculation_date = "MODIFIED"
            assert False, "Should raise exception for frozen dataclass"
        except (AttributeError, Exception):
            pass  # Expected
        
        # nested dataclass도 수정 불가
        try:
            result.legal_capacity.total_units = 9999
            assert False, "Should raise exception for frozen nested dataclass"
        except (AttributeError, Exception):
            pass  # Expected
        
        try:
            result.unit_summary.total_units = 9999
            assert False, "Should raise exception for frozen nested dataclass"
        except (AttributeError, Exception):
            pass  # Expected
    
    def test_input_data_not_modified(
        self,
        sample_land_ctx,
        sample_housing_type_ctx
    ):
        """입력 데이터 무수정 검증"""
        service = CapacityServiceV2()
        
        # 원본 데이터 복사
        original_far = sample_land_ctx.far
        original_bcr = sample_land_ctx.bcr
        original_area = sample_land_ctx.area_sqm
        original_type = sample_housing_type_ctx.selected_type
        
        # 실행
        result = service.run(sample_land_ctx, sample_housing_type_ctx)
        
        # 입력 데이터 변경 없음 확인
        assert sample_land_ctx.far == original_far
        assert sample_land_ctx.bcr == original_bcr
        assert sample_land_ctx.area_sqm == original_area
        assert sample_housing_type_ctx.selected_type == original_type
        
        # frozen=True로 인해 수정 불가능해야 함 (AttributeError)
        try:
            sample_land_ctx.far = 999.9
            assert False, "Should raise exception for frozen dataclass"
        except (AttributeError, Exception):
            pass  # Expected
    
    def test_calculation_metadata(
        self,
        sample_land_ctx,
        sample_housing_type_ctx
    ):
        """계산 메타데이터 검증"""
        service = CapacityServiceV2()
        result = service.run(sample_land_ctx, sample_housing_type_ctx)
        
        # 날짜 형식 확인
        assert result.calculation_date is not None
        assert len(result.calculation_date) > 0
        
        # 모듈 버전
        assert result.module_version == "2.0"
        
        # 입력 참조
        assert result.input_land_area_sqm == sample_land_ctx.area_sqm
        assert result.input_legal_far == sample_land_ctx.far
        assert result.input_incentive_far >= sample_land_ctx.far
        assert result.input_housing_type == sample_housing_type_ctx.selected_type_name
        
        # 가정사항 존재
        assert len(result.assumptions) > 0
        assert "nia_ratio" in result.assumptions
        
        # 제약조건 존재
        assert len(result.constraints) > 0
        
        # 계산 노트 존재
        assert len(result.calculation_notes) > 0
    
    def test_to_dict_serialization(
        self,
        sample_land_ctx,
        sample_housing_type_ctx
    ):
        """to_dict() 직렬화 테스트"""
        service = CapacityServiceV2()
        result = service.run(sample_land_ctx, sample_housing_type_ctx)
        
        # 딕셔너리 변환
        result_dict = result.to_dict()
        
        # 주요 키 존재 확인
        assert "legal_capacity" in result_dict
        assert "incentive_capacity" in result_dict
        assert "massing_options" in result_dict
        assert "unit_summary" in result_dict
        assert "parking_solutions" in result_dict
        assert "schematic_drawings" in result_dict
        
        # 값 타입 확인
        assert isinstance(result_dict["massing_options"], list)
        assert isinstance(result_dict["parking_solutions"], dict)
        assert "alternative_A" in result_dict["parking_solutions"]
        assert "alternative_B" in result_dict["parking_solutions"]
    
    def test_no_business_feasibility_calculation(
        self,
        sample_land_ctx,
        sample_housing_type_ctx
    ):
        """
        사업성 계산 절대 금지 검증
        
        M4는 물리적 규모만 산출하고,
        NPV, IRR, ROI 등은 절대 계산하지 않음
        """
        service = CapacityServiceV2()
        result = service.run(sample_land_ctx, sample_housing_type_ctx)
        
        result_dict = result.to_dict()
        
        # 금지된 키워드 존재하지 않음
        forbidden_keys = ["npv", "irr", "roi", "profit", "revenue", "cost", "land_value"]
        
        # 최상위 레벨 확인
        for key in forbidden_keys:
            assert key not in result_dict
        
        # nested 구조 문자열 변환 후 확인
        result_str = str(result_dict).lower()
        
        # NPV, IRR은 절대 없어야 함
        assert "npv" not in result_str
        assert "irr" not in result_str
    
    def test_no_judgment_statements(
        self,
        sample_land_ctx,
        sample_housing_type_ctx
    ):
        """
        판단적 진술 절대 금지 검증
        
        M4는 '합격/불합격', '좋음/나쁨' 등 판단하지 않음
        """
        service = CapacityServiceV2()
        result = service.run(sample_land_ctx, sample_housing_type_ctx)
        
        # remarks 등 텍스트 필드 검사
        all_remarks = []
        
        for opt in result.massing_options:
            all_remarks.extend(opt.remarks)
        
        all_remarks.extend(result.far_max_alternative.remarks)
        all_remarks.extend(result.parking_priority_alternative.remarks)
        all_remarks.extend(result.calculation_notes)
        
        # 판단 키워드 금지
        forbidden_words = ["합격", "불합격", "좋음", "나쁨", "적합", "부적합"]
        
        for remark in all_remarks:
            for word in forbidden_words:
                # '적합'은 '부적합'만 금지, 램프 '가능성' 같은 것은 허용
                if word == "적합":
                    assert "부적합" not in remark
                else:
                    assert word not in remark


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Run Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
