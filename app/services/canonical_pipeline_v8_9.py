"""
ZeroSite v8.9 Canonical Pipeline Integration

Purpose:
- Enforce FACT → INTERPRETATION → JUDGMENT flow
- Prevent intermediate recalculation of appraisal values
- Guarantee immutability at API level

Usage in main.py:
    from app.services.canonical_pipeline_v8_9 import CanonicalPipeline
    
    pipeline = CanonicalPipeline()
    result = await pipeline.run_full_analysis(request)
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib

from app.services.canonical_flow_adapter import CanonicalFlowAdapter
from app.services.lh_analysis_canonical import LHAnalysisCanonical
from app.services.report_generator_v8_8 import ReportGeneratorV88
from app.services.appraisal_context import AppraisalContextLock


class AppraisalImmutabilityViolation(Exception):
    """Raised when appraisal immutability is violated"""
    pass


class CanonicalPipeline:
    """
    ZeroSite v8.9 Canonical Pipeline
    
    Enforces strict FACT → INTERPRETATION → JUDGMENT flow:
    1. Appraisal (FACT) - creates AppraisalContextLock
    2. Land Diagnosis (INTERPRETATION) - reads locked context only
    3. LH Analysis (JUDGMENT) - reads locked context only
    4. Report Generation - uses locked context
    
    Key Principle: Appraisal value NEVER recalculated after Step 1
    """
    
    VERSION = "v8.9"
    
    def __init__(self):
        self.adapter = CanonicalFlowAdapter()
        self.lh_analyzer = LHAnalysisCanonical()
    
    async def run_full_analysis(
        self,
        analysis_engine_result: Dict[str, Any],
        land_area: float,
        official_price: float,
        premium_rate: Optional[float] = None,
        transaction_price: Optional[float] = None,
        expected_units: Optional[int] = None,
        unit_type: str = '청년형'
    ) -> Dict[str, Any]:
        """
        Run complete canonical pipeline
        
        Args:
            analysis_engine_result: Output from AnalysisEngine.analyze_land()
            land_area: Land area in sqm
            official_price: Official land price per sqm
            premium_rate: Premium rate (optional, will calculate if None)
            transaction_price: Transaction price per sqm (optional)
            expected_units: Expected number of units
            unit_type: Housing unit type
        
        Returns:
            Complete analysis result with immutability guarantees
        
        Raises:
            AppraisalImmutabilityViolation: If appraisal value changes
        """
        
        # Generate unique pipeline execution ID
        pipeline_id = self._generate_pipeline_id()
        
        print(f"\n{'='*80}")
        print(f"🔒 ZeroSite {self.VERSION} Canonical Pipeline")
        print(f"   Pipeline ID: {pipeline_id}")
        print(f"   Execution Time: {datetime.now().isoformat()}")
        print(f"{'='*80}\n")
        
        # STEP 1: Create Appraisal Context (FACT) - IMMUTABLE
        print("📍 STEP 1: Creating Appraisal Context (FACT)")
        print("   ⚠️  This value will be LOCKED and IMMUTABLE")
        
        appraisal_ctx = self.adapter.create_appraisal_context(
            analysis_result=analysis_engine_result,
            land_area=land_area,
            official_price=official_price,
            transaction_price=transaction_price,
            premium_rate=premium_rate
        )
        
        # Extract and lock appraisal value
        locked_appraisal_value = appraisal_ctx.get('calculation.final_appraised_total')
        locked_at = appraisal_ctx.get_locked_at()
        context_hash = self._calculate_context_hash(appraisal_ctx)
        
        print(f"   ✅ Appraisal Context LOCKED")
        print(f"      Locked Value: {locked_appraisal_value:,.0f}원")
        print(f"      Locked At: {locked_at}")
        print(f"      Context Hash: {context_hash}")
        print(f"      Premium Rate: {appraisal_ctx.get('premium.total_premium_rate'):.1%}")
        
        # STEP 2: Land Diagnosis (INTERPRETATION) - READ ONLY
        print(f"\n📍 STEP 2: Land Diagnosis (INTERPRETATION)")
        print(f"   ⚠️  Using locked appraisal value: {locked_appraisal_value:,.0f}원")
        print(f"   ⚠️  NO RECALCULATION ALLOWED")
        
        # Verify hash before diagnosis
        self._verify_context_integrity(appraisal_ctx, context_hash, "before Land Diagnosis")
        
        diagnosis_data = self.adapter.extract_for_land_diagnosis(
            appraisal_ctx, 
            analysis_engine_result
        )
        
        print(f"   ✅ Land Diagnosis Complete (READ-ONLY)")
        print(f"      Appraisal Value Confirmed: {appraisal_ctx.get('calculation.final_appraised_total'):,.0f}원")
        
        # Verify hash after diagnosis
        self._verify_context_integrity(appraisal_ctx, context_hash, "after Land Diagnosis")
        
        # STEP 3: LH Analysis (JUDGMENT) - READ ONLY
        print(f"\n📍 STEP 3: LH Analysis (JUDGMENT)")
        print(f"   ⚠️  Using locked appraisal value: {locked_appraisal_value:,.0f}원")
        print(f"   ⚠️  NO RECALCULATION ALLOWED")
        
        # Verify hash before LH analysis
        self._verify_context_integrity(appraisal_ctx, context_hash, "before LH Analysis")
        
        # Calculate total floor area
        far = appraisal_ctx.get('zoning.floor_area_ratio') / 100
        total_floor_area = land_area * far
        
        # Use provided expected_units or calculate default
        if expected_units is None:
            expected_units = int(total_floor_area / 45)  # 45㎡ per unit default
        
        lh_result = self.lh_analyzer.analyze(
            appraisal_ctx=appraisal_ctx,
            expected_units=expected_units,
            total_floor_area=total_floor_area,
            unit_type=unit_type,
            address=analysis_engine_result.get('address')
        )
        
        print(f"   ✅ LH Analysis Complete (READ-ONLY)")
        print(f"      Appraisal Value Confirmed: {lh_result.get('land_appraisal', 0):,.0f}원")
        print(f"      ROI: {lh_result.get('roi', 0):.2f}%")
        print(f"      Decision: {lh_result.get('decision', 'N/A')}")
        
        # Verify hash after LH analysis
        self._verify_context_integrity(appraisal_ctx, context_hash, "after LH Analysis")
        
        # STEP 4: Final Verification
        print(f"\n📍 STEP 4: Final Immutability Verification")
        
        final_appraisal_value = appraisal_ctx.get('calculation.final_appraised_total')
        
        if final_appraisal_value != locked_appraisal_value:
            raise AppraisalImmutabilityViolation(
                f"CRITICAL: Appraisal value changed! "
                f"Original: {locked_appraisal_value:,.0f}원, "
                f"Final: {final_appraisal_value:,.0f}원"
            )
        
        print(f"   ✅ IMMUTABILITY VERIFIED")
        print(f"      Initial Value: {locked_appraisal_value:,.0f}원")
        print(f"      Final Value: {final_appraisal_value:,.0f}원")
        print(f"      Status: IDENTICAL ✅")
        
        # Compile complete result
        result = {
            'pipeline_id': pipeline_id,
            'pipeline_version': self.VERSION,
            'execution_timestamp': datetime.now().isoformat(),
            
            # Appraisal (FACT)
            'appraisal': {
                'context_id': pipeline_id,
                'locked_value': locked_appraisal_value,
                'locked_at': locked_at,
                'context_hash': context_hash,
                'premium_rate': appraisal_ctx.get('premium.total_premium_rate'),
                'confidence': appraisal_ctx.get('confidence.score'),
                'full_context': appraisal_ctx.to_json()
            },
            
            # Diagnosis (INTERPRETATION)
            'diagnosis': diagnosis_data,
            
            # LH Analysis (JUDGMENT)
            'lh_analysis': lh_result,
            
            # Metadata
            'metadata': {
                'immutability_verified': True,
                'context_hash': context_hash,
                'pipeline_version': self.VERSION
            }
        }
        
        print(f"\n{'='*80}")
        print(f"✅ Canonical Pipeline Complete")
        print(f"   Appraisal: {locked_appraisal_value:,.0f}원 (LOCKED)")
        print(f"   ROI: {lh_result.get('roi', 0):.2f}%")
        print(f"   Decision: {lh_result.get('decision', 'N/A')}")
        print(f"   Immutability: VERIFIED ✅")
        print(f"{'='*80}\n")
        
        return result
    
    def _generate_pipeline_id(self) -> str:
        """Generate unique pipeline execution ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_suffix = str(uuid.uuid4())[:8]
        return f"pipeline_{timestamp}_{unique_suffix}"
    
    def _calculate_context_hash(self, appraisal_ctx: AppraisalContextLock) -> str:
        """
        Calculate hash of critical appraisal data
        
        Used to detect any changes to locked appraisal values
        """
        critical_data = {
            'final_appraised_total': appraisal_ctx.get('calculation.final_appraised_total'),
            'premium_rate': appraisal_ctx.get('premium.total_premium_rate'),
            'land_area': appraisal_ctx.get('calculation.land_area_sqm'),
            'locked_at': appraisal_ctx.get_locked_at()
        }
        
        data_str = str(sorted(critical_data.items()))
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def _verify_context_integrity(
        self, 
        appraisal_ctx: AppraisalContextLock, 
        expected_hash: str,
        stage: str
    ):
        """
        Verify that appraisal context has not been modified
        
        Args:
            appraisal_ctx: Appraisal context to verify
            expected_hash: Expected hash value
            stage: Stage name for error messages
        
        Raises:
            AppraisalImmutabilityViolation: If hash mismatch detected
        """
        current_hash = self._calculate_context_hash(appraisal_ctx)
        
        if current_hash != expected_hash:
            raise AppraisalImmutabilityViolation(
                f"Context integrity violation detected {stage}! "
                f"Expected hash: {expected_hash}, Current hash: {current_hash}"
            )
    
    def generate_report(
        self,
        appraisal_ctx: AppraisalContextLock,
        analysis_data: Dict[str, Any],
        lh_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate 60-page report using canonical data
        
        Args:
            appraisal_ctx: Locked appraisal context
            analysis_data: Land analysis data
            lh_result: LH analysis result
        
        Returns:
            Complete 60-page report
        """
        report_gen = ReportGeneratorV88(
            appraisal_ctx=appraisal_ctx,
            analysis_data=analysis_data,
            lh_analysis_result=lh_result
        )
        
        return report_gen.generate()


__all__ = [
    'CanonicalPipeline',
    'AppraisalImmutabilityViolation'
]
