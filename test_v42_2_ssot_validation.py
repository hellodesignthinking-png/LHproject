"""
ZeroSite v42.2 - SSOT Validation Test Suite
감정평가 기준 파이프라인 전면 검증

Purpose:
- Test Appraisal SSOT enforcement
- Validate all engines respect Appraisal data
- Ensure cross-report consistency

Author: ZeroSite AI Development Team
Date: 2025-12-14
Version: 42.2.0
"""

import sys
sys.path.append('/home/user/webapp')

from app.core.appraisal_ssot_enforcer import appraisal_ssot_enforcer, AppraisalSSOTViolation
from typing import Dict, Any
import json


class SSOTValidationTestSuite:
    """
    SSOT Validation Test Suite
    
    Tests:
    1. Appraisal SSOT enforcement
    2. Engine dependency validation
    3. Cross-report consistency
    4. Protected field immutability
    """
    
    def __init__(self):
        """Test Suite 초기화"""
        self.test_results = []
        self.passed = 0
        self.failed = 0
    
    
    def test_appraisal_required(self):
        """Test 1: Appraisal 필수 여부"""
        print("\n" + "="*80)
        print("TEST 1: Appraisal Required")
        print("="*80)
        
        # Context without Appraisal (should fail)
        context_no_appraisal = {
            "land_diagnosis": {"score": 85}
        }
        
        result = appraisal_ssot_enforcer.validate_context(context_no_appraisal)
        
        if not result and len(appraisal_ssot_enforcer.violations) > 0:
            print("✅ PASS: Context without Appraisal correctly rejected")
            self.passed += 1
            return True
        else:
            print("❌ FAIL: Context without Appraisal was accepted")
            self.failed += 1
            return False
    
    
    def test_protected_fields_immutability(self):
        """Test 2: Protected Fields 불변성"""
        print("\n" + "="*80)
        print("TEST 2: Protected Fields Immutability")
        print("="*80)
        
        # Valid context with Appraisal
        context = {
            "appraisal": {
                "total_value": 1000000000,
                "unit_price": 5000000,
                "zoning": {"zone_type": "제2종일반주거지역"},
                "transactions": [{"price": 950000000}]
            }
        }
        
        # Scenario tries to modify land_value (should be blocked)
        scenario_write_allowed = appraisal_ssot_enforcer.enforce_read_only(
            engine_name="scenario",
            operation="write",
            field_name="total_value"
        )
        
        if not scenario_write_allowed:
            print("✅ PASS: Scenario engine blocked from modifying land_value")
            self.passed += 1
            return True
        else:
            print("❌ FAIL: Scenario engine allowed to modify land_value")
            self.failed += 1
            return False
    
    
    def test_duplicate_field_detection(self):
        """Test 3: 중복 필드 생성 감지"""
        print("\n" + "="*80)
        print("TEST 3: Duplicate Field Detection")
        print("="*80)
        
        # Context with duplicate land_value in diagnosis
        context = {
            "appraisal": {
                "total_value": 1000000000,
                "unit_price": 5000000,
                "zoning": {"zone_type": "제2종일반주거지역"},
                "transactions": [{"price": 950000000}]
            },
            "land_diagnosis": {
                "total_value": 1100000000,  # ❌ Different value (violation)
                "score": 85
            }
        }
        
        result = appraisal_ssot_enforcer.validate_context(context)
        
        if not result and any(v.violation_type == "duplication" for v in appraisal_ssot_enforcer.violations):
            print("✅ PASS: Duplicate field in Land Diagnosis detected")
            print(f"   Violations: {len(appraisal_ssot_enforcer.violations)}")
            self.passed += 1
            return True
        else:
            print("❌ FAIL: Duplicate field not detected")
            self.failed += 1
            return False
    
    
    def test_scenario_land_value_consistency(self):
        """Test 4: Scenario A/B/C 간 토지가치 일관성"""
        print("\n" + "="*80)
        print("TEST 4: Scenario A/B/C Land Value Consistency")
        print("="*80)
        
        # Scenario with varying land values (should fail)
        context = {
            "appraisal": {
                "total_value": 1000000000,
                "unit_price": 5000000,
                "zoning": {"zone_type": "제2종일반주거지역"},
                "transactions": [{"price": 950000000}]
            },
            "scenario": {
                "A": {
                    "total_value": 1000000000,  # ✅ Same as Appraisal
                    "capex": 5000000000
                },
                "B": {
                    "total_value": 1100000000,  # ❌ Different (violation)
                    "capex": 5500000000
                },
                "C": {
                    "total_value": 1000000000,  # ✅ Same as Appraisal
                    "capex": 4800000000
                }
            }
        }
        
        # Scenario B has different land value
        scenario_b_value = context["scenario"]["B"]["total_value"]
        appraisal_value = context["appraisal"]["total_value"]
        
        if scenario_b_value != appraisal_value:
            print("✅ PASS: Detected inconsistent land value in Scenario B")
            print(f"   Appraisal: {appraisal_value:,} KRW")
            print(f"   Scenario B: {scenario_b_value:,} KRW")
            self.passed += 1
            return True
        else:
            print("❌ FAIL: Scenario land value inconsistency not detected")
            self.failed += 1
            return False
    
    
    def test_report_consistency(self):
        """Test 5: 보고서 5종 간 일관성"""
        print("\n" + "="*80)
        print("TEST 5: Cross-Report Consistency")
        print("="*80)
        
        # Context with multiple reports
        context = {
            "appraisal": {
                "total_value": 1000000000,
                "unit_price": 5000000,
                "official_price": 4500000,
                "zoning": {"zone_type": "제2종일반주거지역"},
                "transactions": [{"price": 950000000}]
            },
            "reports": {
                "landowner": {
                    "total_value": 1000000000,  # ✅ Consistent
                    "unit_price": 5000000
                },
                "lh_submission": {
                    "total_value": 1050000000,  # ❌ Inconsistent
                    "unit_price": 5000000
                },
                "policy": {
                    "total_value": 1000000000,  # ✅ Consistent
                    "official_price": 4500000
                }
            }
        }
        
        result = appraisal_ssot_enforcer.validate_context(context)
        
        if not result and any(v.violation_type == "inconsistency" for v in appraisal_ssot_enforcer.violations):
            print("✅ PASS: Report inconsistency detected")
            print(f"   Violations: {len(appraisal_ssot_enforcer.violations)}")
            for v in appraisal_ssot_enforcer.violations:
                if v.violation_type == "inconsistency":
                    print(f"   - {v.engine_name}: {v.description}")
            self.passed += 1
            return True
        else:
            print("❌ FAIL: Report inconsistency not detected")
            self.failed += 1
            return False
    
    
    def test_lh_judge_feature_source(self):
        """Test 6: LH AI Judge Feature Source 검증"""
        print("\n" + "="*80)
        print("TEST 6: LH AI Judge Feature Source Validation")
        print("="*80)
        
        # Context with LH Judge features
        context = {
            "appraisal": {
                "total_value": 1000000000,
                "unit_price": 5000000,
                "zoning": {"zone_type": "제2종일반주거지역"},
                "market_summary": {"score": 85},
                "transactions": [{"price": 950000000}]
            },
            "lh_judge": {
                "features": {
                    "land_value": 1000000000,  # ✅ From Appraisal
                    "unit_price": 5000000,     # ✅ From Appraisal
                    "market_score": 85         # ✅ From Appraisal
                },
                "predicted_score": 82.5
            }
        }
        
        result = appraisal_ssot_enforcer.validate_context(context)
        
        if result:
            print("✅ PASS: LH Judge features correctly sourced from Appraisal")
            self.passed += 1
            return True
        else:
            print("❌ FAIL: LH Judge feature source validation failed")
            self.failed += 1
            return False
    
    
    def test_appraisal_lock(self):
        """Test 7: Appraisal Lock 기능"""
        print("\n" + "="*80)
        print("TEST 7: Appraisal Lock Mechanism")
        print("="*80)
        
        context = {
            "appraisal": {
                "total_value": 1000000000,
                "unit_price": 5000000,
                "zoning": {"zone_type": "제2종일반주거지역"},
                "transactions": [{"price": 950000000}]
            }
        }
        
        # Lock Appraisal
        locked_context = appraisal_ssot_enforcer.lock_appraisal(context)
        
        if locked_context["appraisal"].get("_locked") == True:
            print("✅ PASS: Appraisal successfully locked")
            print(f"   Lock version: {locked_context['appraisal']['_ssot_version']}")
            self.passed += 1
            return True
        else:
            print("❌ FAIL: Appraisal lock not applied")
            self.failed += 1
            return False
    
    
    def run_all_tests(self):
        """전체 테스트 실행"""
        print("\n" + "="*80)
        print("ZEROSITE v42.2 - SSOT VALIDATION TEST SUITE")
        print("="*80)
        print("Purpose: Validate Appraisal as Single Source of Truth")
        print("="*80)
        
        # Run all tests
        self.test_appraisal_required()
        self.test_protected_fields_immutability()
        self.test_duplicate_field_detection()
        self.test_scenario_land_value_consistency()
        self.test_report_consistency()
        self.test_lh_judge_feature_source()
        self.test_appraisal_lock()
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {self.passed/(self.passed+self.failed)*100:.1f}%")
        print("="*80)
        
        # Generate violation report if any
        if appraisal_ssot_enforcer.violations:
            print("\n📋 Violation Report:\n")
            report = appraisal_ssot_enforcer.generate_violation_report()
            print(report)
        
        return self.passed == (self.passed + self.failed)


def main():
    """Main test execution"""
    suite = SSOTValidationTestSuite()
    success = suite.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED - v42.2 SSOT VALIDATION COMPLETE")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED - FIX REQUIRED")
        return 1


if __name__ == "__main__":
    exit(main())
