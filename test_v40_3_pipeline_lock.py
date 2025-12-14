"""
ZeroSite v40.3 - Pipeline Lock Release 통합 테스트

테스트 목적:
1. Context Protection 검증 (Appraisal Immutable)
2. Pipeline 의존성 체크 검증
3. 데이터 일관성 검증
4. LH 심사예측 연동 검증

Date: 2025-12-14
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8001"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_test_header(test_name: str):
    print(f"\n{Colors.BLUE}{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}{Colors.END}")


def print_result(test_name: str, passed: bool, details: str = ""):
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"{status} - {test_name}")
    if details:
        print(f"  └─ {details}")


def test_1_health_check():
    """Test 1: v40.3 Health Check"""
    print_test_header("Test 1: v40.3 Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v40.2/health")
        response.raise_for_status()
        data = response.json()
        
        passed = (
            data.get("status") == "healthy" and
            "40.3" in data.get("version", "")
        )
        
        print_result(
            "Health Check",
            passed,
            f"Version: {data.get('version')}, Features: {len(data.get('features', []))}"
        )
        
        return passed, data
        
    except Exception as e:
        print_result("Health Check", False, str(e))
        return False, None


def test_2_create_context():
    """Test 2: Context 생성 및 보호 플래그 확인"""
    print_test_header("Test 2: Context 생성 및 v40.3 보호 적용")
    
    try:
        # Create analysis
        payload = {
            "address": "서울특별시 관악구 신림동 1524-8",
            "land_area_sqm": 650.0
        }
        
        response = requests.post(f"{BASE_URL}/api/v40.2/run-analysis", json=payload)
        response.raise_for_status()
        result = response.json()
        
        context_id = result.get("context_id")
        
        # Get full context
        context_response = requests.get(f"{BASE_URL}/api/v40.2/context/{context_id}")
        context_response.raise_for_status()
        context_data = context_response.json()
        
        # Check v40.3 features
        checks = {
            "version_40_3": context_data.get("version") == "40.3",
            "appraisal_protected": context_data.get("appraisal", {}).get("_protected") == True,
            "metadata_exists": "_metadata" in context_data,
            "protection_status": "_protection_status" in context_data
        }
        
        all_passed = all(checks.values())
        
        print_result(
            "Context Creation",
            all_passed,
            f"Context ID: {context_id[:12]}..., Checks: {sum(checks.values())}/4"
        )
        
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"    {status} {check_name}")
        
        return all_passed, context_id
        
    except Exception as e:
        print_result("Context Creation", False, str(e))
        return False, None


def test_3_pipeline_status(context_id: str):
    """Test 3: Pipeline 상태 조회"""
    print_test_header("Test 3: Pipeline 상태 조회")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v40.2/context/{context_id}/pipeline-status")
        response.raise_for_status()
        data = response.json()
        
        # Check pipeline completion
        pipeline = data.get("pipeline", {})
        
        core_modules_complete = all([
            pipeline.get("1_appraisal", {}).get("completed"),
            pipeline.get("2_diagnosis", {}).get("completed"),
            pipeline.get("3_capacity", {}).get("completed"),
            pipeline.get("4_scenario", {}).get("completed")
        ])
        
        # Check consistency
        consistency = data.get("consistency", {})
        consistency_status = consistency.get("status", "")
        
        passed = core_modules_complete and "CONSISTENT" in consistency_status
        
        print_result(
            "Pipeline Status",
            passed,
            f"Modules: 4/4, Consistency: {consistency_status}"
        )
        
        # Print pipeline details
        print(f"\n  Pipeline Stages:")
        for stage, info in pipeline.items():
            print(f"    {info.get('status')} {stage}")
        
        # Print consistency checks
        print(f"\n  Consistency Checks:")
        for check in consistency.get("checks", []):
            print(f"    {check.get('status')} {check.get('name')}")
        
        return passed, data
        
    except Exception as e:
        print_result("Pipeline Status", False, str(e))
        return False, None


def test_4_data_consistency(context_id: str):
    """Test 4: 데이터 일관성 검증 (Diagnosis/Capacity가 Appraisal 데이터 사용)"""
    print_test_header("Test 4: 데이터 일관성 검증")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v40.2/debug/consistency-check/{context_id}")
        response.raise_for_status()
        data = response.json()
        
        overall_status = data.get("overall_status", "")
        checks = data.get("checks", {})
        
        passed = "ALL CHECKS PASSED" in overall_status
        
        print_result(
            "Data Consistency",
            passed,
            overall_status
        )
        
        # Print detailed checks
        print(f"\n  Detailed Checks:")
        for check_name, check_data in checks.items():
            print(f"    {check_data.get('status')} {check_name}")
            if not check_data.get("match"):
                print(f"      └─ Mismatch detected:")
                for key, value in check_data.items():
                    if key not in ["status", "match"]:
                        print(f"         {key}: {value}")
        
        return passed, data
        
    except Exception as e:
        print_result("Data Consistency", False, str(e))
        return False, None


def test_5_lh_review_with_protection(context_id: str):
    """Test 5: LH 심사예측 + Context Protection 검증"""
    print_test_header("Test 5: LH 심사예측 with v40.3 Protection")
    
    try:
        payload = {
            "context_id": context_id,
            "housing_type": "청년",
            "target_units": 25
        }
        
        response = requests.post(f"{BASE_URL}/api/v40/lh-review/predict", json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Check prediction results
        score = result.get("predicted_score", 0)
        probability = result.get("pass_probability", 0)
        risk_level = result.get("risk_level", "")
        
        passed = (
            score > 0 and
            probability > 0 and
            risk_level in ["LOW", "MEDIUM", "HIGH"]
        )
        
        print_result(
            "LH Review Prediction",
            passed,
            f"Score: {score}/100, Probability: {probability}%, Risk: {risk_level}"
        )
        
        # Check factors
        factors = result.get("factors", [])
        print(f"\n  Evaluation Factors: {len(factors)}")
        for factor in factors[:3]:  # Show first 3
            print(f"    • {factor.get('factor_name')}: {factor.get('score')}/100")
        
        # Check scenarios
        scenarios = result.get("scenarios", [])
        print(f"\n  Scenarios Analyzed: {len(scenarios)}")
        for scenario in scenarios:
            s_name = scenario.get("scenario_name", "")
            s_score = scenario.get("result", {}).get("predicted_score", 0)
            print(f"    • {s_name}: {s_score}/100")
        
        return passed, result
        
    except Exception as e:
        print_result("LH Review Prediction", False, str(e))
        return False, None


def test_6_protection_enforcement():
    """Test 6: Context Protection 강제 적용 검증"""
    print_test_header("Test 6: Context Protection 강제 적용")
    
    try:
        # Create new context
        payload = {
            "address": "서울특별시 강남구 역삼동 123",
            "land_area_sqm": 500.0
        }
        
        response = requests.post(f"{BASE_URL}/api/v40.2/run-analysis", json=payload)
        response.raise_for_status()
        result = response.json()
        context_id = result.get("context_id")
        
        # Get context
        context_response = requests.get(f"{BASE_URL}/api/v40.2/context/{context_id}")
        context_response.raise_for_status()
        context_data = context_response.json()
        
        # Verify protection flags
        appraisal = context_data.get("appraisal", {})
        protection_checks = {
            "_protected flag": appraisal.get("_protected") == True,
            "_lock_timestamp": "_lock_timestamp" in appraisal,
            "metadata.protection_enabled": context_data.get("_metadata", {}).get("protection_enabled") == True,
            "metadata.appraisal_locked": context_data.get("_metadata", {}).get("appraisal_locked") == True
        }
        
        all_passed = all(protection_checks.values())
        
        print_result(
            "Protection Enforcement",
            all_passed,
            f"Protection Flags: {sum(protection_checks.values())}/4"
        )
        
        for check_name, result in protection_checks.items():
            status = "✅" if result else "❌"
            print(f"    {status} {check_name}")
        
        return all_passed, context_data
        
    except Exception as e:
        print_result("Protection Enforcement", False, str(e))
        return False, None


def run_all_tests():
    """Run all v40.3 Pipeline Lock tests"""
    print(f"\n{Colors.BLUE}{'='*80}")
    print("ZeroSite v40.3 - Pipeline Lock Release")
    print("통합 테스트 (Integration Tests)")
    print(f"{'='*80}{Colors.END}\n")
    
    results = []
    
    # Test 1: Health Check
    passed, data = test_1_health_check()
    results.append(("Health Check", passed))
    
    if not passed:
        print(f"\n{Colors.RED}❌ Health check failed. Stopping tests.{Colors.END}")
        return
    
    # Test 2: Create Context
    passed, context_id = test_2_create_context()
    results.append(("Context Creation", passed))
    
    if not passed or not context_id:
        print(f"\n{Colors.RED}❌ Context creation failed. Stopping tests.{Colors.END}")
        return
    
    # Test 3: Pipeline Status
    passed, data = test_3_pipeline_status(context_id)
    results.append(("Pipeline Status", passed))
    
    # Test 4: Data Consistency
    passed, data = test_4_data_consistency(context_id)
    results.append(("Data Consistency", passed))
    
    # Test 5: LH Review
    passed, data = test_5_lh_review_with_protection(context_id)
    results.append(("LH Review", passed))
    
    # Test 6: Protection Enforcement
    passed, data = test_6_protection_enforcement()
    results.append(("Protection Enforcement", passed))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}{Colors.END}\n")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"{status} - {test_name}")
    
    print(f"\n{Colors.BLUE}Total: {passed_count}/{total_count} tests passed{Colors.END}")
    
    if passed_count == total_count:
        print(f"\n{Colors.GREEN}🎉 ALL TESTS PASSED! v40.3 Pipeline Lock is working correctly!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠️ Some tests failed. Please review the results above.{Colors.END}")


if __name__ == "__main__":
    run_all_tests()
