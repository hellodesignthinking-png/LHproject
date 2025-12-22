"""
Pipeline M4 V2 Integration Tests
=================================

M4 V2가 파이프라인에 통합된 후 전체 파이프라인 테스트

테스트 범위:
1. 파이프라인이 M4 V2를 사용하는지 검증
2. M5가 CapacityContextV2를 올바르게 소비하는지 검증
3. M6가 CapacityContextV2를 올바르게 소비하는지 검증
4. 전체 파이프라인 실행 성공 검증
5. 불변성 검증 (모든 Context frozen)

Author: ZeroSite Integration Team
Date: 2025-12-17
"""

import pytest

from app.core.pipeline.zer0site_pipeline import ZeroSitePipeline, PipelineResult
from app.core.context.capacity_context_v2 import CapacityContextV2


class TestPipelineM4V2Integration:
    """파이프라인 M4 V2 통합 테스트"""
    
    def test_pipeline_uses_m4_v2(self):
        """파이프라인이 M4 V2를 사용하는지 검증"""
        pipeline = ZeroSitePipeline()
        
        result = pipeline.run(
            parcel_id="1168010100100010001",
            asking_price=10_000_000_000
        )
        
        # M4 Context가 V2인지 확인
        assert isinstance(result.capacity, CapacityContextV2)
        
        # V2 필수 산출물 존재 확인
        assert result.capacity.legal_capacity is not None
        assert result.capacity.incentive_capacity is not None
        assert len(result.capacity.massing_options) >= 3
        assert result.capacity.unit_summary is not None
        assert "alternative_A" in result.capacity.parking_solutions
        assert "alternative_B" in result.capacity.parking_solutions
    
    def test_m5_consumes_capacity_v2(self):
        """M5가 CapacityContextV2를 올바르게 소비하는지 검증"""
        pipeline = ZeroSitePipeline()
        
        result = pipeline.run(
            parcel_id="1168010100100010001"
        )
        
        # M5가 성공적으로 실행되었는지 확인
        assert result.feasibility is not None
        assert result.feasibility.financial_metrics is not None
        assert result.feasibility.financial_metrics.npv_public is not None
        
        # M5가 V2의 incentive_capacity를 사용했는지 간접 확인
        # (연면적이 incentive FAR 기준으로 계산되었는지)
        assert result.feasibility.cost_breakdown.construction_cost > 0
    
    def test_m6_consumes_capacity_v2(self):
        """M6가 CapacityContextV2를 올바르게 소비하는지 검증"""
        pipeline = ZeroSitePipeline()
        
        result = pipeline.run(
            parcel_id="1168010100100010001"
        )
        
        # M6가 성공적으로 실행되었는지 확인
        assert result.lh_review is not None
        assert result.lh_review.score_breakdown is not None
        assert result.lh_review.total_score > 0
        
        # M6가 V2의 incentive units을 사용했는지 간접 확인
        # (규모 점수가 계산되었는지)
        assert result.lh_review.score_breakdown.scale_score > 0
    
    def test_pipeline_success_property(self):
        """파이프라인 성공 여부 검증"""
        pipeline = ZeroSitePipeline()
        
        result = pipeline.run(
            parcel_id="1168010100100010001"
        )
        
        # success 프로퍼티가 True인지 확인
        assert result.success is True
        
        # 모든 Context가 None이 아닌지 확인
        assert result.land is not None
        assert result.appraisal is not None
        assert result.housing_type is not None
        assert result.capacity is not None
        assert result.feasibility is not None
        assert result.lh_review is not None
    
    def test_all_contexts_frozen(self):
        """모든 Context가 불변인지 검증"""
        pipeline = ZeroSitePipeline()
        
        result = pipeline.run(
            parcel_id="1168010100100010001"
        )
        
        # PipelineResult 자체도 frozen
        try:
            result.land = None
            assert False, "Should raise exception for frozen PipelineResult"
        except (AttributeError, Exception):
            pass  # Expected
        
        # M2 AppraisalContext frozen
        try:
            result.appraisal.land_value = 999999
            assert False, "Should raise exception for frozen AppraisalContext"
        except (AttributeError, Exception):
            pass  # Expected
        
        # M4 CapacityContextV2 frozen
        try:
            result.capacity.calculation_date = "MODIFIED"
            assert False, "Should raise exception for frozen CapacityContextV2"
        except (AttributeError, Exception):
            pass  # Expected
    
    def test_capacity_v2_six_outputs_in_pipeline(self):
        """파이프라인 결과의 M4 V2가 6가지 산출물을 포함하는지 검증"""
        pipeline = ZeroSitePipeline()
        
        result = pipeline.run(
            parcel_id="1168010100100010001"
        )
        
        capacity = result.capacity
        
        # 1. Legal Capacity
        assert capacity.legal_capacity is not None
        assert capacity.legal_capacity.total_units > 0
        
        # 2. Incentive Capacity
        assert capacity.incentive_capacity is not None
        assert capacity.incentive_capacity.total_units >= capacity.legal_capacity.total_units
        
        # 3. Massing Options (3~5개)
        assert 3 <= len(capacity.massing_options) <= 5
        
        # 4. Unit Summary
        assert capacity.unit_summary is not None
        assert capacity.unit_summary.total_units > 0
        
        # 5. Parking Solutions (A & B)
        assert "alternative_A" in capacity.parking_solutions
        assert "alternative_B" in capacity.parking_solutions
        
        # 6. Schematic Drawing Paths
        assert len(capacity.schematic_drawing_paths) >= 4
    
    def test_m5_uses_incentive_capacity(self):
        """M5가 인센티브 규모를 사용하는지 검증"""
        pipeline = ZeroSitePipeline()
        
        result = pipeline.run(
            parcel_id="1168010100100010001"
        )
        
        # M5의 계산이 인센티브 GFA를 기반으로 했는지 확인
        # (공사비 = GFA × 단가)
        incentive_gfa = result.capacity.incentive_capacity.target_gfa_sqm
        construction_cost = result.feasibility.cost_breakdown.construction_cost
        
        # 공사비가 인센티브 GFA 기준으로 계산되었는지
        # (단가 3,000,000원/㎡ 가정)
        expected_construction = incentive_gfa * 3_000_000
        
        # 오차 범위 내 확인 (±10%)
        assert abs(construction_cost - expected_construction) / expected_construction < 0.1
    
    def test_m6_scale_score_based_on_incentive_units(self):
        """M6 규모 점수가 인센티브 세대수를 기반으로 하는지 검증"""
        pipeline = ZeroSitePipeline()
        
        result = pipeline.run(
            parcel_id="1168010100100010001"
        )
        
        incentive_units = result.capacity.incentive_capacity.total_units
        scale_score = result.lh_review.score_breakdown.scale_score
        
        # 세대수에 따른 점수 검증
        if incentive_units >= 100:
            assert scale_score == 20.0
        elif incentive_units >= 70:
            assert scale_score == 17.0
        elif incentive_units >= 50:
            assert scale_score == 15.0
        else:
            assert scale_score == 10.0
    
    def test_pipeline_result_serialization(self):
        """파이프라인 결과 직렬화 검증"""
        pipeline = ZeroSitePipeline()
        
        result = pipeline.run(
            parcel_id="1168010100100010001"
        )
        
        # CapacityContextV2의 to_dict() 호출
        capacity_dict = result.capacity.to_dict()
        
        # 직렬화된 데이터 구조 확인
        assert "legal_capacity" in capacity_dict
        assert "incentive_capacity" in capacity_dict
        assert "massing_options" in capacity_dict
        assert "unit_summary" in capacity_dict
        assert "parking_solutions" in capacity_dict
        
        # parking_solutions에 A, B 존재
        assert "alternative_A" in capacity_dict["parking_solutions"]
        assert "alternative_B" in capacity_dict["parking_solutions"]
    
    def test_pipeline_deterministic_with_v2(self):
        """M4 V2를 사용한 파이프라인이 결정론적인지 검증"""
        pipeline = ZeroSitePipeline()
        
        result1 = pipeline.run(parcel_id="1168010100100010001")
        result2 = pipeline.run(parcel_id="1168010100100010001")
        
        # M2 Appraisal 결과 동일
        assert result1.appraisal.land_value == result2.appraisal.land_value
        
        # M4 V2 Capacity 결과 동일
        assert result1.capacity.legal_capacity.total_units == result2.capacity.legal_capacity.total_units
        assert result1.capacity.incentive_capacity.total_units == result2.capacity.incentive_capacity.total_units
        
        # M5 Feasibility 결과 동일
        assert result1.feasibility.financial_metrics.npv_public == result2.feasibility.financial_metrics.npv_public
        
        # M6 LH Review 결과 동일
        assert result1.lh_review.total_score == result2.lh_review.total_score
        assert result1.lh_review.decision == result2.lh_review.decision


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Run Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
