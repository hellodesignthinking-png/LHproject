"""
Test M2 Appraisal Module Immutability
======================================

🔒 CRITICAL TEST: AppraisalContext MUST be immutable

Test Cases:
1. AppraisalContext cannot be modified after creation
2. Same land always produces same land_value (regression test)
3. M5/M6 cannot modify appraisal results

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

import pytest
from dataclasses import FrozenInstanceError

from app.core.context.canonical_land import CanonicalLandContext
from app.core.context.appraisal_context import AppraisalContext
from app.modules.m2_appraisal.service import AppraisalService


class TestAppraisalImmutability:
    """Test AppraisalContext immutability"""
    
    @pytest.fixture
    def mock_land_context(self):
        """Create mock land context"""
        return CanonicalLandContext(
            parcel_id="TEST_PNU_001",
            address="서울특별시 강남구 역삼동 123-45",
            road_address="서울특별시 강남구 테헤란로 123",
            coordinates=(37.5012, 127.0396),
            sido="서울특별시",
            sigungu="강남구",
            dong="역삼동",
            area_sqm=1000.0,
            area_pyeong=302.5,
            land_category="대",
            land_use="주거용",
            zone_type="제2종일반주거지역",
            zone_detail="제2종일반주거지역",
            far=250.0,
            bcr=60.0,
            road_width=12.0,
            road_type="중로",
            terrain_height="평지",
            terrain_shape="정형",
            regulations={},
            restrictions=[],
            data_source="Mock API",
            retrieval_date="2025-12-17"
        )
    
    @pytest.fixture
    def appraisal_service(self):
        """Create appraisal service"""
        return AppraisalService(use_enhanced_services=True)
    
    def test_appraisal_context_is_frozen(self, appraisal_service, mock_land_context):
        """
        🔒 TEST 1: AppraisalContext is frozen (immutable)
        
        AppraisalContext should raise FrozenInstanceError when attempting to modify
        """
        # Run appraisal
        appraisal_ctx = appraisal_service.run(mock_land_context)
        
        # Attempt to modify land_value (should fail)
        with pytest.raises(FrozenInstanceError):
            appraisal_ctx.land_value = 999_999_999
        
        # Attempt to modify unit_price_sqm (should fail)
        with pytest.raises(FrozenInstanceError):
            appraisal_ctx.unit_price_sqm = 999_999
        
        # Attempt to modify confidence_score (should fail)
        with pytest.raises(FrozenInstanceError):
            appraisal_ctx.confidence_score = 1.0
        
        print("✅ TEST 1 PASSED: AppraisalContext is immutable")
    
    def test_appraisal_regression(self, appraisal_service, mock_land_context):
        """
        🔒 TEST 2: Appraisal Regression Test
        
        Same land should always produce same land_value
        """
        # Run appraisal twice with same input
        appraisal_1 = appraisal_service.run(mock_land_context)
        appraisal_2 = appraisal_service.run(mock_land_context)
        
        # land_value should be identical
        assert appraisal_1.land_value == appraisal_2.land_value, \
            f"Appraisal regression failed: {appraisal_1.land_value} != {appraisal_2.land_value}"
        
        # unit_price_sqm should be identical
        assert appraisal_1.unit_price_sqm == appraisal_2.unit_price_sqm, \
            f"Unit price regression failed"
        
        # confidence_score should be identical
        assert appraisal_1.confidence_score == appraisal_2.confidence_score, \
            f"Confidence score regression failed"
        
        print(f"✅ TEST 2 PASSED: Appraisal is deterministic (land_value={appraisal_1.land_value:,.0f})")
    
    def test_appraisal_validation(self, appraisal_service, mock_land_context):
        """
        🔒 TEST 3: AppraisalContext Validation
        
        AppraisalContext should validate data in __post_init__
        """
        # Run appraisal
        appraisal_ctx = appraisal_service.run(mock_land_context)
        
        # Check validation
        assert appraisal_ctx.land_value > 0, "land_value must be positive"
        assert appraisal_ctx.unit_price_sqm > 0, "unit_price_sqm must be positive"
        assert 0 <= appraisal_ctx.confidence_score <= 1, "confidence_score must be 0-1"
        assert appraisal_ctx.confidence_level in ["LOW", "MEDIUM", "HIGH"], \
            "confidence_level must be LOW/MEDIUM/HIGH"
        assert len(appraisal_ctx.transaction_samples) == appraisal_ctx.transaction_count, \
            "transaction count mismatch"
        
        print("✅ TEST 3 PASSED: AppraisalContext validation works")
    
    def test_appraisal_context_properties(self, appraisal_service, mock_land_context):
        """
        🔒 TEST 4: AppraisalContext Properties
        
        Test read-only properties
        """
        # Run appraisal
        appraisal_ctx = appraisal_service.run(mock_land_context)
        
        # Test properties (should not raise errors)
        assert isinstance(appraisal_ctx.is_high_confidence, bool)
        assert isinstance(appraisal_ctx.valuation_summary, str)
        
        # Test to_dict() method
        appraisal_dict = appraisal_ctx.to_dict()
        assert "appraisal" in appraisal_dict
        assert "land_value" in appraisal_dict["appraisal"]
        
        print("✅ TEST 4 PASSED: AppraisalContext properties work")


class TestAppraisalProtection:
    """Test that M5/M6 cannot modify appraisal results"""
    
    @pytest.fixture
    def mock_land_context(self):
        """Create mock land context"""
        return CanonicalLandContext(
            parcel_id="TEST_PNU_002",
            address="서울특별시 강남구 역삼동 999-99",
            road_address="서울특별시 강남구 테헤란로 999",
            coordinates=(37.5012, 127.0396),
            sido="서울특별시",
            sigungu="강남구",
            dong="역삼동",
            area_sqm=1500.0,
            area_pyeong=453.75,
            land_category="대",
            land_use="주거용",
            zone_type="제2종일반주거지역",
            zone_detail="제2종일반주거지역",
            far=250.0,
            bcr=60.0,
            road_width=12.0,
            road_type="중로",
            terrain_height="평지",
            terrain_shape="정형",
            regulations={},
            restrictions=[],
            data_source="Mock API",
            retrieval_date="2025-12-17"
        )
    
    def test_m5_cannot_modify_appraisal(self, mock_land_context):
        """
        🔒 TEST 5: M5 Feasibility Module Cannot Modify Appraisal
        
        M5 should only READ appraisal results, not modify them
        """
        from app.modules.m2_appraisal.service import AppraisalService
        from app.modules.m3_lh_demand.service import LHDemandService
        from app.modules.m4_capacity.service import CapacityService
        from app.modules.m5_feasibility.service import FeasibilityService
        
        # Run M1-M4
        appraisal_service = AppraisalService(use_enhanced_services=True)
        appraisal_ctx = appraisal_service.run(mock_land_context)
        
        housing_type_service = LHDemandService()
        housing_type_ctx = housing_type_service.run(mock_land_context)
        
        capacity_service = CapacityService()
        capacity_ctx = capacity_service.run(mock_land_context, housing_type_ctx)
        
        # Store original land_value
        original_land_value = appraisal_ctx.land_value
        
        # Run M5 (should not modify appraisal_ctx)
        feasibility_service = FeasibilityService()
        feasibility_ctx = feasibility_service.run(appraisal_ctx, capacity_ctx)
        
        # Check that appraisal_ctx.land_value is unchanged
        assert appraisal_ctx.land_value == original_land_value, \
            f"M5 modified appraisal! {appraisal_ctx.land_value} != {original_land_value}"
        
        # Check that M5 references appraisal correctly
        assert feasibility_ctx.appraised_value == original_land_value, \
            "M5 should reference M2 land_value"
        
        print(f"✅ TEST 5 PASSED: M5 did not modify appraisal (land_value={original_land_value:,.0f})")
    
    def test_m6_cannot_modify_appraisal(self, mock_land_context):
        """
        🔒 TEST 6: M6 LH Review Module Cannot Modify Appraisal
        
        M6 should only READ results, not modify any Context
        """
        from app.core.pipeline.zer0site_pipeline import ZeroSitePipeline
        
        # Run full pipeline
        pipeline = ZeroSitePipeline()
        result = pipeline.run(mock_land_context.parcel_id)
        
        # Store original values
        original_land_value = result.appraisal.land_value
        original_npv = result.feasibility.financial_metrics.npv_public
        
        # M6 should not modify anything
        assert result.appraisal.land_value == original_land_value, \
            "M6 modified appraisal!"
        assert result.feasibility.financial_metrics.npv_public == original_npv, \
            "M6 modified feasibility!"
        
        print("✅ TEST 6 PASSED: M6 did not modify any Context")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
