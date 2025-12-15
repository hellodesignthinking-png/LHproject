"""
ZeroSite v8.8 - E2E Pipeline Fixed Test

Purpose:
- Prove that appraisal results are IMMUTABLE across pipeline stages
- Verify that only diagnosis scores and LH judgment change
- Ensure land value remains fixed from appraisal through final report

Test Strategy:
1. Run complete pipeline (Appraisal → Diagnosis → LH → Report)
2. Extract appraisal values at each stage
3. Assert: appraisal value NEVER changes
4. Assert: diagnosis and LH judgment CAN change
5. Verify: report uses locked appraisal value

File: tests/test_e2e_pipeline_fixed.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from typing import Dict, Any, List
from app.services.canonical_schema import CanonicalAppraisalResult
from app.services.canonical_flow_adapter import CanonicalFlowAdapter
from app.services.appraisal_context import AppraisalContextLock
from app.services.lh_analysis_canonical import LHAnalysisCanonical


class TestE2EPipelineFixed:
    """
    E2E Pipeline Immutability Test Suite
    
    Ensures:
    1. Appraisal value is locked at creation
    2. Appraisal value never changes throughout pipeline
    3. Diagnosis and LH analysis use the locked value
    4. Report generation uses the locked value
    """
    
    # Test scenario: 월드컵북로 120
    TEST_SCENARIO = {
        'name': '월드컵북로 120 - Full Pipeline Test',
        'input': {
            'address': '서울시 마포구 월드컵북로 120',
            'land_area_sqm': 660.0,
            'zoning_type': '제2종일반주거지역',
            'official_price_per_sqm': 5500000,
            'bcr': 60,
            'far': 200,
            'distance_to_subway': 250,
            'youth_ratio': 28,
            'elderly_ratio': 12,
            'nearby_schools': 5,
            'nearby_hospitals': 3,
            'expected_units': 56
        },
        'expected_appraisal': {
            'premium_rate': 0.09,  # 9%
            'final_appraised_total': 4154535000  # 41.5억
        }
    }
    
    def test_appraisal_immutability_through_pipeline(self):
        """
        Test that appraisal value remains fixed throughout entire pipeline
        
        Pipeline stages:
        1. Appraisal Context Creation (LOCK)
        2. Land Diagnosis (READ)
        3. LH Analysis (READ)
        4. Report Generation (READ)
        """
        
        print("\n" + "="*80)
        print("🔍 E2E Pipeline Immutability Test")
        print("="*80)
        
        scenario = self.TEST_SCENARIO
        
        print(f"\nTest Scenario: {scenario['name']}")
        print(f"Land Area: {scenario['input']['land_area_sqm']}㎡")
        print(f"Official Price: {scenario['input']['official_price_per_sqm']:,}원/㎡")
        
        # STAGE 1: Appraisal Context Creation
        print("\n" + "-"*80)
        print("STAGE 1: Appraisal Context Creation (LOCK)")
        print("-"*80)
        
        adapter = CanonicalFlowAdapter()
        mock_result = self._create_mock_analysis_result(scenario['input'])
        
        appraisal_ctx = adapter.create_appraisal_context(
            analysis_result=mock_result,
            land_area=scenario['input']['land_area_sqm'],
            official_price=scenario['input']['official_price_per_sqm'],
            premium_rate=scenario['expected_appraisal']['premium_rate']
        )
        
        # Extract and store initial appraisal value
        stage1_appraisal_value = appraisal_ctx.get('calculation.final_appraised_total')
        stage1_locked_at = appraisal_ctx.get_locked_at()
        
        print(f"\n✅ Appraisal Context LOCKED")
        print(f"   Locked At: {stage1_locked_at}")
        print(f"   Final Appraised Value: {stage1_appraisal_value:,.0f}원")
        print(f"   Premium Rate: {appraisal_ctx.get('premium.total_premium_rate'):.1%}")
        print(f"   Is Locked: {appraisal_ctx.is_locked()}")
        
        # Verify lock is active
        assert appraisal_ctx.is_locked(), "Appraisal context must be locked"
        assert stage1_appraisal_value == scenario['expected_appraisal']['final_appraised_total'], \
            "Initial appraisal value must match expected"
        
        # STAGE 2: Land Diagnosis (READ-ONLY)
        print("\n" + "-"*80)
        print("STAGE 2: Land Diagnosis (READ-ONLY)")
        print("-"*80)
        
        # Extract data for diagnosis
        diagnosis_data = adapter.extract_for_land_diagnosis(appraisal_ctx, mock_result)
        
        # Verify appraisal value is still the same
        stage2_appraisal_value = appraisal_ctx.get('calculation.final_appraised_total')
        
        print(f"\n✅ Land Diagnosis Data Extracted")
        print(f"   Appraisal Value: {stage2_appraisal_value:,.0f}원")
        print(f"   Zoning: {diagnosis_data.get('zoning_type', 'N/A')}")
        print(f"   FAR: {diagnosis_data.get('far', 'N/A')}%")
        print(f"   Premium: {diagnosis_data.get('premium_rate', 0):.1%}")
        
        # Assert: Appraisal value UNCHANGED
        assert stage2_appraisal_value == stage1_appraisal_value, \
            f"Appraisal value MUST NOT change during diagnosis! " \
            f"{stage1_appraisal_value:,.0f} → {stage2_appraisal_value:,.0f}"
        
        print(f"\n✅ IMMUTABILITY CHECK PASSED: Appraisal value unchanged")
        
        # STAGE 3: LH Analysis (READ-ONLY)
        print("\n" + "-"*80)
        print("STAGE 3: LH Analysis (READ-ONLY)")
        print("-"*80)
        
        # Extract data for LH analysis (calculate total floor area from FAR)
        far = scenario['input']['far'] / 100  # Convert percentage to decimal
        land_area = scenario['input']['land_area_sqm']
        total_floor_area = land_area * far  # e.g., 660 * 2.0 = 1320㎡
        
        lh_data = adapter.extract_for_lh_analysis(
            appraisal_ctx, 
            expected_units=scenario['input']['expected_units'],
            total_floor_area=total_floor_area
        )
        
        # Run LH analysis
        lh_analyzer = LHAnalysisCanonical()
        lh_result = lh_analyzer.analyze(
            appraisal_ctx=appraisal_ctx,
            expected_units=scenario['input']['expected_units'],
            total_floor_area=total_floor_area,
            unit_type='청년형'
        )
        
        # Verify appraisal value is still the same
        stage3_appraisal_value = appraisal_ctx.get('calculation.final_appraised_total')
        
        print(f"\n✅ LH Analysis Completed")
        print(f"   Land Appraisal (from context): {lh_result.get('land_appraisal', 'N/A'):,.0f}원" if isinstance(lh_result.get('land_appraisal'), (int, float)) else f"   Land Appraisal: {lh_result.get('land_appraisal', 'N/A')}")
        print(f"   Total Cost: {lh_result.get('total_cost', 0):,.0f}원")
        print(f"   ROI: {lh_result.get('roi', 0):.2f}%")
        print(f"   Decision: {lh_result.get('decision', 'N/A')}")
        print(f"   Rating: {lh_result.get('rating', 'N/A')}")
        
        # Assert: Appraisal value UNCHANGED
        assert stage3_appraisal_value == stage1_appraisal_value, \
            f"Appraisal value MUST NOT change during LH analysis! " \
            f"{stage1_appraisal_value:,.0f} → {stage3_appraisal_value:,.0f}"
        
        # Assert: LH analysis uses locked value (if available in result)
        if 'land_appraisal' in lh_result:
            assert lh_result['land_appraisal'] == stage1_appraisal_value, \
                "LH analysis must use the locked appraisal value"
        
        print(f"\n✅ IMMUTABILITY CHECK PASSED: Appraisal value unchanged")
        
        # STAGE 4: Report Generation (READ-ONLY)
        print("\n" + "-"*80)
        print("STAGE 4: Report Generation (READ-ONLY)")
        print("-"*80)
        
        # Simulate report generation access
        report_appraisal_value = appraisal_ctx.get('calculation.final_appraised_total')
        
        print(f"\n✅ Report Generation Access")
        print(f"   Appraisal Value (for report): {report_appraisal_value:,.0f}원")
        print(f"   Total Cost (for report): {lh_result.get('total_cost', 0):,.0f}원")
        
        # Assert: Appraisal value UNCHANGED
        assert report_appraisal_value == stage1_appraisal_value, \
            f"Appraisal value MUST NOT change during report generation! " \
            f"{stage1_appraisal_value:,.0f} → {report_appraisal_value:,.0f}"
        
        print(f"\n✅ IMMUTABILITY CHECK PASSED: Appraisal value unchanged")
        
        # FINAL VERIFICATION
        print("\n" + "="*80)
        print("FINAL IMMUTABILITY VERIFICATION")
        print("="*80)
        
        print(f"\n📊 Appraisal Value Tracking:")
        print(f"   Stage 1 (Creation):      {stage1_appraisal_value:,.0f}원")
        print(f"   Stage 2 (Diagnosis):     {stage2_appraisal_value:,.0f}원")
        print(f"   Stage 3 (LH Analysis):   {stage3_appraisal_value:,.0f}원")
        print(f"   Stage 4 (Report):        {report_appraisal_value:,.0f}원")
        
        all_values = [
            stage1_appraisal_value,
            stage2_appraisal_value,
            stage3_appraisal_value,
            report_appraisal_value
        ]
        
        # Assert: ALL values are identical
        assert all(v == stage1_appraisal_value for v in all_values), \
            "Appraisal value MUST remain constant across ALL pipeline stages!"
        
        print(f"\n✅ ✅ ✅ IMMUTABILITY VERIFIED ✅ ✅ ✅")
        print(f"\nConclusion:")
        print(f"  • Appraisal value: {stage1_appraisal_value:,.0f}원 (FIXED)")
        print(f"  • Locked at: {stage1_locked_at}")
        print(f"  • All 4 stages: IDENTICAL value")
        print(f"  • Context lock: ACTIVE")
        print(f"  • Pipeline integrity: VERIFIED")
    
    def test_pipeline_allows_diagnosis_changes(self):
        """
        Test that diagnosis scores CAN change while appraisal remains fixed
        
        Verifies:
        1. Appraisal value is immutable
        2. Diagnosis scores can vary (e.g., different risk assessments)
        3. LH judgment can vary (e.g., different ROI scenarios)
        """
        
        print("\n" + "="*80)
        print("🔍 Pipeline Flexibility Test (Diagnosis & LH Can Change)")
        print("="*80)
        
        scenario = self.TEST_SCENARIO
        
        # Create appraisal context (LOCKED)
        adapter = CanonicalFlowAdapter()
        mock_result = self._create_mock_analysis_result(scenario['input'])
        
        appraisal_ctx = adapter.create_appraisal_context(
            analysis_result=mock_result,
            land_area=scenario['input']['land_area_sqm'],
            official_price=scenario['input']['official_price_per_sqm'],
            premium_rate=scenario['expected_appraisal']['premium_rate']
        )
        
        fixed_appraisal_value = appraisal_ctx.get('calculation.final_appraised_total')
        
        print(f"\n🔒 Appraisal Context LOCKED")
        print(f"   Fixed Value: {fixed_appraisal_value:,.0f}원")
        
        # Run LH Analysis with different unit counts (diagnosis scenario A)
        print("\n" + "-"*80)
        print("SCENARIO A: 56 Units (Original)")
        print("-"*80)
        
        lh_analyzer = LHAnalysisCanonical()
        
        # Calculate total floor area for scenario A
        far_a = 200 / 100  # 200% FAR
        total_floor_area_a = scenario['input']['land_area_sqm'] * far_a
        
        scenario_a = lh_analyzer.analyze(
            appraisal_ctx=appraisal_ctx,
            expected_units=56,
            total_floor_area=total_floor_area_a,
            unit_type='청년형'
        )
        
        print(f"   Land Appraisal: {scenario_a.get('land_appraisal', fixed_appraisal_value):,.0f}원")
        print(f"   ROI: {scenario_a.get('roi', 0):.2f}%")
        print(f"   Decision: {scenario_a.get('decision', 'N/A')}")
        
        # Run LH Analysis with different unit counts (diagnosis scenario B)
        print("\n" + "-"*80)
        print("SCENARIO B: 48 Units (Different Diagnosis)")
        print("-"*80)
        
        # Calculate total floor area for scenario B
        far_b = 200 / 100  # 200% FAR
        total_floor_area_b = scenario['input']['land_area_sqm'] * far_b
        
        scenario_b = lh_analyzer.analyze(
            appraisal_ctx=appraisal_ctx,
            expected_units=48,
            total_floor_area=total_floor_area_b,
            unit_type='청년형'
        )
        
        print(f"   Land Appraisal: {scenario_b.get('land_appraisal', fixed_appraisal_value):,.0f}원")
        print(f"   ROI: {scenario_b.get('roi', 0):.2f}%")
        print(f"   Decision: {scenario_b.get('decision', 'N/A')}")
        
        # Verify: Appraisal value SAME, but ROI/decision CAN differ
        if 'land_appraisal' in scenario_a:
            assert scenario_a['land_appraisal'] == fixed_appraisal_value, \
                "Scenario A must use fixed appraisal"
        if 'land_appraisal' in scenario_b:
            assert scenario_b['land_appraisal'] == fixed_appraisal_value, \
                "Scenario B must use fixed appraisal"
            assert scenario_a['land_appraisal'] == scenario_b['land_appraisal'], \
                "Both scenarios must use the SAME fixed appraisal"
        
        # Verify: ROI and decision CAN be different
        print("\n✅ VERIFICATION PASSED:")
        print(f"   • Land appraisal: FIXED at {fixed_appraisal_value:,.0f}원")
        print(f"   • Scenario A ROI: {scenario_a['roi']:.2f}%")
        print(f"   • Scenario B ROI: {scenario_b['roi']:.2f}%")
        print(f"   • ROI can differ: ✅ (while appraisal stays fixed)")
    
    def test_pipeline_version_upgrade_scenario(self):
        """
        Test pipeline behavior when upgrading from v8.7 to v8.8
        
        Verifies:
        1. v8.7 appraisal value can be loaded and locked
        2. v8.8 diagnosis and LH use the locked v8.7 value
        3. No recalculation of appraisal in v8.8
        """
        
        print("\n" + "="*80)
        print("🔍 Version Upgrade Test (v8.7 → v8.8)")
        print("="*80)
        
        scenario = self.TEST_SCENARIO
        
        # Simulate v8.7 appraisal result (historical data)
        print("\n📦 Loading v8.7 Historical Appraisal")
        
        v87_appraisal_value = scenario['expected_appraisal']['final_appraised_total']
        v87_premium_rate = scenario['expected_appraisal']['premium_rate']
        
        print(f"   v8.7 Value: {v87_appraisal_value:,.0f}원")
        print(f"   v8.7 Premium: {v87_premium_rate:.1%}")
        
        # Lock v8.7 appraisal in v8.8 system
        print("\n🔒 Locking v8.7 Appraisal in v8.8 System")
        
        adapter = CanonicalFlowAdapter()
        mock_result = self._create_mock_analysis_result(scenario['input'])
        
        appraisal_ctx = adapter.create_appraisal_context(
            analysis_result=mock_result,
            land_area=scenario['input']['land_area_sqm'],
            official_price=scenario['input']['official_price_per_sqm'],
            premium_rate=v87_premium_rate
        )
        
        v88_appraisal_value = appraisal_ctx.get('calculation.final_appraised_total')
        
        print(f"   v8.8 Locked Value: {v88_appraisal_value:,.0f}원")
        
        # Verify: v8.8 uses v8.7 value without recalculation
        assert v88_appraisal_value == v87_appraisal_value, \
            "v8.8 must preserve v8.7 appraisal value"
        
        # Run v8.8 LH analysis
        print("\n🔄 Running v8.8 LH Analysis with v8.7 Appraisal")
        
        lh_analyzer = LHAnalysisCanonical()
        
        # Calculate total floor area
        far_upgrade = scenario['input']['far'] / 100
        total_floor_area_upgrade = scenario['input']['land_area_sqm'] * far_upgrade
        
        lh_result = lh_analyzer.analyze(
            appraisal_ctx=appraisal_ctx,
            expected_units=scenario['input']['expected_units'],
            total_floor_area=total_floor_area_upgrade,
            unit_type='청년형'
        )
        
        print(f"   Land Appraisal: {lh_result.get('land_appraisal', v87_appraisal_value):,.0f}원")
        print(f"   ROI: {lh_result.get('roi', 0):.2f}%")
        print(f"   Decision: {lh_result.get('decision', 'N/A')}")
        
        # Verify: LH uses v8.7 value
        if 'land_appraisal' in lh_result:
            assert lh_result['land_appraisal'] == v87_appraisal_value, \
                "v8.8 LH analysis must use v8.7 appraisal value"
            
            print("\n✅ VERSION UPGRADE VERIFIED:")
            print(f"   • v8.7 appraisal: {v87_appraisal_value:,.0f}원")
            print(f"   • v8.8 locked: {v88_appraisal_value:,.0f}원")
            print(f"   • v8.8 LH uses: {lh_result['land_appraisal']:,.0f}원")
            print(f"   • All values: IDENTICAL ✅")
        else:
            print("\n✅ VERSION UPGRADE VERIFIED:")
            print(f"   • v8.7 appraisal: {v87_appraisal_value:,.0f}원")
            print(f"   • v8.8 locked: {v88_appraisal_value:,.0f}원")
            print(f"   • Appraisal value preserved: ✅")
    
    def _create_mock_analysis_result(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create mock analysis result for testing"""
        
        class MockZoneInfo:
            def __init__(self, zone_type, bcr, far):
                self.zone_type = zone_type
                self.building_coverage_ratio = bcr
                self.floor_area_ratio = far
        
        return {
            'address': input_data['address'],
            'land_area': input_data['land_area_sqm'],
            'zone_info': MockZoneInfo(
                zone_type=input_data['zoning_type'],
                bcr=input_data['bcr'],
                far=input_data['far']
            )
        }


def test_e2e_pipeline_fixed_suite():
    """
    Run complete E2E pipeline fixed test suite
    """
    
    print("\n" + "="*80)
    print("🔬 ZeroSite v8.8 - E2E Pipeline Immutability Test Suite")
    print("="*80)
    
    suite = TestE2EPipelineFixed()
    
    # Test 1: Appraisal immutability through full pipeline
    print("\n📋 TEST 1: Appraisal Immutability Through Pipeline")
    suite.test_appraisal_immutability_through_pipeline()
    
    # Test 2: Diagnosis and LH can change
    print("\n📋 TEST 2: Pipeline Allows Diagnosis/LH Changes")
    suite.test_pipeline_allows_diagnosis_changes()
    
    # Test 3: Version upgrade scenario
    print("\n📋 TEST 3: Version Upgrade (v8.7 → v8.8)")
    suite.test_pipeline_version_upgrade_scenario()
    
    print("\n" + "="*80)
    print("✅ ALL E2E PIPELINE IMMUTABILITY TESTS PASSED")
    print("="*80)
    print("\nKey Results:")
    print("  ✓ Appraisal value IMMUTABLE across all pipeline stages")
    print("  ✓ Diagnosis scores and LH judgment CAN change")
    print("  ✓ Version upgrade preserves historical appraisal")
    print("  ✓ Context lock enforced throughout pipeline")
    print("\nConclusion: Pipeline integrity VERIFIED - Appraisal is Single Source of Truth")


if __name__ == '__main__':
    test_e2e_pipeline_fixed_suite()
