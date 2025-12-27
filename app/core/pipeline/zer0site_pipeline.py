"""
ZeroSite 6-Module Pipeline
===========================

6모듈을 순차적으로 실행하는 단방향 파이프라인

실행 순서:
1. M1: 토지정보 (FACT)
2. M2: 토지감정평가 (FACT, 🔒 IMMUTABLE)
3. M3: LH 선호유형 (INTERPRETATION)
4. M4: 건축규모 (INTERPRETATION)
5. M5: 사업성 (JUDGMENT INPUT)
6. M6: LH 심사예측 (FINAL JUDGMENT)

⚠️ 규칙:
- M2 AppraisalContext는 생성 후 수정 불가
- 역방향 참조 금지
- Context 기반 데이터 전달만 허용

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

from typing import Optional
from dataclasses import dataclass
import logging

# Context 임포트
from app.core.context.canonical_land import CanonicalLandContext
from app.core.context.appraisal_context import AppraisalContext
from app.core.context.housing_type_context import HousingTypeContext
from app.core.context.capacity_context import CapacityContext  # V1 (legacy)
from app.core.context.capacity_context_v2 import CapacityContextV2  # V2 (new)
from app.core.context.feasibility_context import FeasibilityContext
from app.core.context.lh_review_context import LHReviewContext

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PipelineResult:
    """
    파이프라인 전체 실행 결과
    
    모든 모듈의 Context를 포함
    """
    land: CanonicalLandContext               # M1
    appraisal: AppraisalContext              # M2 🔒 IMMUTABLE
    housing_type: HousingTypeContext         # M3
    capacity: CapacityContextV2              # M4 V2 (upgraded)
    feasibility: FeasibilityContext          # M5
    lh_review: LHReviewContext               # M6
    
    @property
    def success(self) -> bool:
        """파이프라인 성공 여부"""
        return all([
            self.land is not None,
            self.appraisal is not None,
            self.housing_type is not None,
            self.capacity is not None,
            self.feasibility is not None,
            self.lh_review is not None
        ])
    
    @property
    def final_decision(self) -> str:
        """최종 LH 심사 결정"""
        return self.lh_review.decision


class ZeroSitePipeline:
    """
    ZeroSite 6-Module 파이프라인
    
    Usage:
        pipeline = ZeroSitePipeline()
        result = pipeline.run(parcel_id="1168010100100010001")
        
        print(result.appraisal.land_value)
        print(result.lh_review.decision)
    """
    
    def __init__(self):
        """파이프라인 초기화"""
        logger.info("="*80)
        logger.info("🚀 ZeroSite 6-MODULE PIPELINE initialized")
        logger.info("   Architecture: M1 → M2🔒 → M3 → M4 → M5 → M6")
        logger.info("   M2 AppraisalContext: IMMUTABLE (frozen=True)")
        logger.info("="*80)
        
        # 모듈 초기화 (lazy loading)
        self._m1_service = None
        self._m2_service = None
        self._m3_service = None
        self._m4_service = None
        self._m5_service = None
        self._m6_service = None
    
    def run(
        self,
        parcel_id: str,
        asking_price: Optional[float] = None,
        context_id: Optional[str] = None
    ) -> PipelineResult:
        """
        6모듈 파이프라인 실행
        
        Args:
            parcel_id: 필지 ID (PNU 코드)
            asking_price: 호가 (선택)
            context_id: Context ID (선택, M1 frozen context 로드용)
        
        Returns:
            PipelineResult: 전체 Context 포함
        
        Raises:
            Exception: 모듈 실행 중 오류 발생 시
        """
        
        logger.info("\n" + "="*80)
        logger.info(f"🎯 PIPELINE START: parcel_id={parcel_id}, context_id={context_id}")
        logger.info("="*80)
        
        try:
            # ===================================================================
            # M1: 토지정보 조회 (FACT)
            # ===================================================================
            logger.info("\n📍 [M1] Land Info Module - Starting...")
            
            # 🔥 FIX: Try to load M1 frozen context first if context_id is provided
            land_ctx = None
            if context_id:
                try:
                    from app.services.context_storage import context_storage
                    logger.info(f"🔍 Attempting to load M1 frozen context: {context_id}")
                    frozen_ctx = context_storage.get_frozen_context(context_id)
                    if frozen_ctx:
                        # Extract land context from frozen context
                        land_data = frozen_ctx.get('land')
                        if land_data:
                            from app.core.context.canonical_land import CanonicalLandContext
                            # Reconstruct CanonicalLandContext from dict
                            land_ctx = CanonicalLandContext(**land_data)
                            logger.info(f"✅ Loaded M1 frozen context from: {context_id}")
                            logger.info(f"   Address: {land_ctx.address}")
                            logger.info(f"   Area: {land_ctx.area_sqm:,.1f}㎡")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load M1 frozen context: {e}")
                    logger.info("   Falling back to fresh M1 execution")
            
            # If no frozen context, run M1 fresh
            if land_ctx is None:
                land_ctx = self._run_m1(parcel_id)
                logger.info(f"✅ [M1] Complete (Fresh): {land_ctx.address}")
            
            logger.info(f"   Area: {land_ctx.area_sqm:,.1f}㎡, Zone: {land_ctx.zone_type}")
            
            # ===================================================================
            # M2: 토지감정평가 (FACT, 🔒 IMMUTABLE)
            # ===================================================================
            logger.info("\n💰 [M2] Appraisal Module - Starting...")
            appraisal_ctx = self._run_m2(land_ctx, asking_price)
            logger.info(f"✅ [M2] Complete (🔒 LOCKED)")
            logger.info(f"   Land Value: ₩{appraisal_ctx.land_value:,.0f}")
            logger.info(f"   Confidence: {appraisal_ctx.confidence_level} ({appraisal_ctx.confidence_score:.0%})")
            logger.info("   ⚠️ AppraisalContext is now IMMUTABLE!")
            
            # ===================================================================
            # M3: LH 선호유형 선택 (INTERPRETATION)
            # ===================================================================
            logger.info("\n🏘️ [M3] Housing Type Module - Starting...")
            housing_type_ctx = self._run_m3(land_ctx)
            logger.info(f"✅ [M3] Complete: {housing_type_ctx.selected_type}")
            logger.info(f"   LH Demand Prediction: {housing_type_ctx.demand_prediction}")
            
            # ===================================================================
            # M4: 건축규모 검토 V2 (INTERPRETATION)
            # ===================================================================
            logger.info("\n🏗️ [M4] Capacity Module V2 - Starting...")
            capacity_ctx = self._run_m4(land_ctx, housing_type_ctx)
            logger.info(f"✅ [M4 V2] Complete")
            logger.info(f"   Legal: {capacity_ctx.legal_capacity.total_units}세대 / {capacity_ctx.legal_capacity.applied_far}%")
            logger.info(f"   Incentive: {capacity_ctx.incentive_capacity.total_units}세대 / {capacity_ctx.incentive_capacity.applied_far}%")
            logger.info(f"   Parking A/B: {capacity_ctx.far_max_alternative.total_parking_spaces}/{capacity_ctx.parking_priority_alternative.total_parking_spaces}대")
            
            # ===================================================================
            # M5: 사업성 검토 (JUDGMENT INPUT)
            # ===================================================================
            logger.info("\n📊 [M5] Feasibility Module - Starting...")
            feasibility_ctx = self._run_m5(appraisal_ctx, capacity_ctx)
            logger.info(f"✅ [M5] Complete")
            logger.info(f"   NPV: ₩{feasibility_ctx.financial_metrics.npv_public:,.0f}, IRR: {feasibility_ctx.financial_metrics.irr_public:.1f}%")
            
            # ===================================================================
            # M6: LH 심사예측 (FINAL JUDGMENT)
            # ===================================================================
            logger.info("\n⚖️ [M6] LH Review Module - Starting...")
            lh_review_ctx = self._run_m6(housing_type_ctx, capacity_ctx, feasibility_ctx)
            logger.info(f"✅ [M6] Complete")
            logger.info(f"   Decision: {lh_review_ctx.decision}")
            logger.info(f"   Total Score: {lh_review_ctx.total_score:.1f}/110")
            
            # ===================================================================
            # 파이프라인 완료
            # ===================================================================
            result = PipelineResult(
                land=land_ctx,
                appraisal=appraisal_ctx,
                housing_type=housing_type_ctx,
                capacity=capacity_ctx,
                feasibility=feasibility_ctx,
                lh_review=lh_review_ctx
            )
            
            logger.info("\n" + "="*80)
            logger.info("🎉 PIPELINE COMPLETE - All modules executed successfully")
            logger.info(f"   Final Decision: {result.final_decision}")
            logger.info(f"   Land Value (🔒): ₩{result.appraisal.land_value:,.0f}")
            logger.info("="*80 + "\n")
            
            return result
            
        except Exception as e:
            logger.error(f"\n❌ PIPELINE FAILED: {e}")
            raise
    
    def _run_m1(self, parcel_id: str) -> CanonicalLandContext:
        """M1: 토지정보 조회"""
        if self._m1_service is None:
            from app.modules.m1_land_info.service import LandInfoService
            self._m1_service = LandInfoService()
        
        return self._m1_service.run(parcel_id)
    
    def _run_m2(
        self,
        land_ctx: CanonicalLandContext,
        asking_price: Optional[float]
    ) -> AppraisalContext:
        """M2: 토지감정평가 (🔒 IMMUTABLE)"""
        if self._m2_service is None:
            from app.modules.m2_appraisal.service import AppraisalService
            self._m2_service = AppraisalService(use_enhanced_services=True)
        
        appraisal_ctx = self._m2_service.run(land_ctx, asking_price)
        
        # 🔒 IMMUTABLE 검증
        assert isinstance(appraisal_ctx, AppraisalContext), \
            "M2 must return AppraisalContext"
        
        return appraisal_ctx
    
    def _run_m3(self, land_ctx: CanonicalLandContext) -> HousingTypeContext:
        """M3: LH 선호유형 선택"""
        if self._m3_service is None:
            from app.modules.m3_lh_demand.service import LHDemandService
            self._m3_service = LHDemandService()
        
        return self._m3_service.run(land_ctx)
    
    def _run_m4(
        self,
        land_ctx: CanonicalLandContext,
        housing_type_ctx: HousingTypeContext
    ) -> CapacityContextV2:
        """M4: 건축규모 검토 (V2)"""
        if self._m4_service is None:
            from app.modules.m4_capacity.service_v2 import CapacityServiceV2
            self._m4_service = CapacityServiceV2()
        
        return self._m4_service.run(land_ctx, housing_type_ctx)
    
    def _run_m5(
        self,
        appraisal_ctx: AppraisalContext,
        capacity_ctx: CapacityContext
    ) -> FeasibilityContext:
        """M5: 사업성 검토"""
        if self._m5_service is None:
            from app.modules.m5_feasibility.service import FeasibilityService
            self._m5_service = FeasibilityService()
        
        # ⚠️ M5는 AppraisalContext를 READ-ONLY로만 사용
        return self._m5_service.run(appraisal_ctx, capacity_ctx)
    
    def _run_m6(
        self,
        housing_type_ctx: HousingTypeContext,
        capacity_ctx: CapacityContext,
        feasibility_ctx: FeasibilityContext
    ) -> LHReviewContext:
        """M6: LH 심사예측"""
        if self._m6_service is None:
            from app.modules.m6_lh_review.service import LHReviewService
            self._m6_service = LHReviewService()
        
        return self._m6_service.run(housing_type_ctx, capacity_ctx, feasibility_ctx)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*80)
    print("Testing ZeroSite 6-Module Pipeline")
    print("="*80 + "\n")
    
    try:
        pipeline = ZeroSitePipeline()
        
        result = pipeline.run(
            parcel_id="1168010100100010001",  # Mock PNU
            asking_price=10_000_000_000
        )
        
        print(f"\n{'='*80}")
        print("📊 PIPELINE RESULTS")
        print(f"{'='*80}\n")
        
        print(f"🏠 토지: {result.land.address}")
        print(f"💰 감정가 (🔒): ₩{result.appraisal.land_value:,.0f}")
        print(f"🏘️ LH 유형: {result.housing_type.selected_type}")
        print(f"🏗️ 세대수 (V2):")
        print(f"   - Legal: {result.capacity.legal_capacity.total_units}세대 / {result.capacity.legal_capacity.applied_far}%")
        print(f"   - Incentive: {result.capacity.incentive_capacity.total_units}세대 / {result.capacity.incentive_capacity.applied_far}%")
        print(f"   - Parking A/B: {result.capacity.far_max_alternative.total_parking_spaces}/{result.capacity.parking_priority_alternative.total_parking_spaces}대")
        print(f"📊 NPV: ₩{result.feasibility.financial_metrics.npv_public:,.0f}")
        print(f"⚖️ LH 심사: {result.lh_review.decision} ({result.lh_review.total_score:.1f}/110점)")
        
        print(f"\n{'='*80}")
        print("✅ Test Complete!")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
