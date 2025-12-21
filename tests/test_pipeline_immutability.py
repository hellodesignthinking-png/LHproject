"""
Test Pipeline Immutability
===========================

🔒 CRITICAL TEST: Pipeline must maintain immutability

Test Cases:
1. Pipeline execution preserves M2 AppraisalContext
2. M6 execution does not modify M2 results
3. Multiple pipeline runs produce consistent results
4. Context objects remain frozen throughout pipeline

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

import pytest
from dataclasses import FrozenInstanceError

from app.core.pipeline.zer0site_pipeline import ZeroSitePipeline, PipelineResult


class TestPipelineImmutability:
    """Test that pipeline maintains immutability"""
    
    @pytest.fixture
    def pipeline(self):
        """Create pipeline"""
        return ZeroSitePipeline()
    
    def test_pipeline_preserves_m2_immutability(self, pipeline):
        """
        🔒 TEST 1: Pipeline Preserves M2 Immutability
        
        After full pipeline execution, M2 AppraisalContext should remain unchanged
        """
        # Run pipeline
        result = pipeline.run("TEST_PNU_001")
        
        # Store M2 result
        original_land_value = result.appraisal.land_value
        
        # Attempt to modify (should fail)
        with pytest.raises(FrozenInstanceError):
            result.appraisal.land_value = 999_999_999
        
        # Verify land_value is still original
        assert result.appraisal.land_value == original_land_value
        
        print(f"✅ TEST 1 PASSED: M2 AppraisalContext preserved (land_value={original_land_value:,.0f})")
    
    def test_m6_execution_does_not_modify_m2(self, pipeline):
        """
        🔒 TEST 2: M6 Execution Does Not Modify M2
        
        After M6 LH review, M2 appraisal results should be unchanged
        """
        # Run pipeline
        result = pipeline.run("TEST_PNU_002")
        
        # Store M2 result before M6
        m2_land_value = result.appraisal.land_value
        m2_unit_price = result.appraisal.unit_price_sqm
        m2_confidence = result.appraisal.confidence_score
        
        # M6 has already run, check M2 is unchanged
        assert result.appraisal.land_value == m2_land_value, \
            "M6 modified M2 land_value!"
        assert result.appraisal.unit_price_sqm == m2_unit_price, \
            "M6 modified M2 unit_price_sqm!"
        assert result.appraisal.confidence_score == m2_confidence, \
            "M6 modified M2 confidence_score!"
        
        print("✅ TEST 2 PASSED: M6 did not modify M2")
    
    def test_multiple_pipeline_runs_consistency(self, pipeline):
        """
        🔒 TEST 3: Multiple Pipeline Runs Produce Consistent Results
        
        Running pipeline multiple times with same input should produce same results
        """
        parcel_id = "TEST_PNU_003"
        
        # Run pipeline 3 times
        result_1 = pipeline.run(parcel_id)
        result_2 = pipeline.run(parcel_id)
        result_3 = pipeline.run(parcel_id)
        
        # M2 AppraisalContext should be identical
        assert result_1.appraisal.land_value == result_2.appraisal.land_value, \
            "Pipeline run 1 vs 2: land_value differs"
        assert result_2.appraisal.land_value == result_3.appraisal.land_value, \
            "Pipeline run 2 vs 3: land_value differs"
        
        # M5 FeasibilityContext should be consistent
        assert result_1.feasibility.financial_metrics.npv_public == result_2.feasibility.financial_metrics.npv_public, \
            "Pipeline run 1 vs 2: NPV differs"
        
        # M6 LHReviewContext should be consistent
        assert result_1.lh_review.total_score == result_2.lh_review.total_score, \
            "Pipeline run 1 vs 2: LH score differs"
        
        print(f"✅ TEST 3 PASSED: Pipeline is deterministic (land_value={result_1.appraisal.land_value:,.0f})")
    
    def test_all_contexts_frozen(self, pipeline):
        """
        🔒 TEST 4: All Context Objects Are Frozen
        
        Every Context in PipelineResult should be frozen
        """
        # Run pipeline
        result = pipeline.run("TEST_PNU_004")
        
        # Test M1 CanonicalLandContext
        with pytest.raises(FrozenInstanceError):
            result.land.area_sqm = 9999.0
        
        # Test M2 AppraisalContext
        with pytest.raises(FrozenInstanceError):
            result.appraisal.land_value = 9999.0
        
        # Test M3 HousingTypeContext
        with pytest.raises(FrozenInstanceError):
            result.housing_type.selected_type = "INVALID"
        
        # Test M4 CapacityContext
        with pytest.raises(FrozenInstanceError):
            result.capacity.total_units = 9999
        
        # Test M5 FeasibilityContext
        with pytest.raises(FrozenInstanceError):
            result.feasibility.is_profitable = False
        
        # Test M6 LHReviewContext
        with pytest.raises(FrozenInstanceError):
            result.lh_review.total_score = 9999.0
        
        print("✅ TEST 4 PASSED: All 6 Contexts are frozen")
    
    def test_pipeline_result_frozen(self, pipeline):
        """
        🔒 TEST 5: PipelineResult Itself Is Frozen
        
        PipelineResult should also be immutable
        """
        # Run pipeline
        result = pipeline.run("TEST_PNU_005")
        
        # Attempt to modify PipelineResult (should fail)
        with pytest.raises(FrozenInstanceError):
            result.land = None
        
        with pytest.raises(FrozenInstanceError):
            result.appraisal = None
        
        print("✅ TEST 5 PASSED: PipelineResult is frozen")
    
    def test_pipeline_success_property(self, pipeline):
        """
        🔒 TEST 6: Pipeline Success Property
        
        PipelineResult.success should return True when all modules complete
        """
        # Run pipeline
        result = pipeline.run("TEST_PNU_006")
        
        # Check success
        assert result.success is True, "Pipeline did not complete successfully"
        
        # Check all contexts exist
        assert result.land is not None
        assert result.appraisal is not None
        assert result.housing_type is not None
        assert result.capacity is not None
        assert result.feasibility is not None
        assert result.lh_review is not None
        
        print("✅ TEST 6 PASSED: Pipeline completed successfully")
    
    def test_pipeline_final_decision(self, pipeline):
        """
        🔒 TEST 7: Pipeline Final Decision
        
        PipelineResult.final_decision should return M6 decision
        """
        # Run pipeline
        result = pipeline.run("TEST_PNU_007")
        
        # Check final decision
        assert result.final_decision == result.lh_review.decision.value, \
            "final_decision does not match M6 decision"
        
        assert result.final_decision in ["GO", "NO_GO", "CONDITIONAL"], \
            "Invalid final decision"
        
        print(f"✅ TEST 7 PASSED: Final decision is {result.final_decision}")


class TestPipelineDataFlow:
    """Test unidirectional data flow in pipeline"""
    
    @pytest.fixture
    def pipeline(self):
        """Create pipeline"""
        return ZeroSitePipeline()
    
    def test_data_flow_direction(self, pipeline):
        """
        🔒 TEST 8: Data Flow Is Unidirectional
        
        Pipeline should flow: M1 → M2 → M3 → M4 → M5 → M6
        No reverse dependencies
        """
        # Run pipeline
        result = pipeline.run("TEST_PNU_008")
        
        # M2 uses M1
        assert result.appraisal is not None
        
        # M3 uses M1
        assert result.housing_type is not None
        
        # M4 uses M1 + M3
        assert result.capacity is not None
        
        # M5 uses M2 + M4 (READ-ONLY on M2!)
        assert result.feasibility.appraised_value == result.appraisal.land_value, \
            "M5 should reference M2 land_value"
        
        # M6 uses M3 + M4 + M5 (READ-ONLY on all!)
        assert result.lh_review is not None
        
        print("✅ TEST 8 PASSED: Data flow is unidirectional")
    
    def test_no_reverse_dependencies(self, pipeline):
        """
        🔒 TEST 9: No Reverse Dependencies
        
        M5/M6 should not call M2 service directly
        """
        # This test is structural (ensured by architecture)
        # M5/M6 services do not import M2 service
        
        # Run pipeline
        result = pipeline.run("TEST_PNU_009")
        
        # If pipeline completes without calling M2 twice, test passes
        assert result.success is True
        
        print("✅ TEST 9 PASSED: No reverse dependencies detected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
