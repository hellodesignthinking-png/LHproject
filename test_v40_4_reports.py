"""
ZeroSite v40.4 - Report Generation 통합 테스트

테스트 목적:
1. 보고서 5종 체계 검증
2. Landowner Brief (3p) 생성 테스트
3. Report Type Validation 검증
4. LH Review 통합 검증

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


def test_1_create_context_with_lh_review():
    """Test 1: Create context and run LH review"""
    print_test_header("Test 1: Context 생성 및 LH 심사예측 실행")
    
    try:
        # Step 1: Create analysis context
        payload = {
            "address": "서울특별시 관악구 신림동 1524-8",
            "land_area_sqm": 650.0
        }
        
        response = requests.post(f"{BASE_URL}/api/v40.2/run-analysis", json=payload)
        response.raise_for_status()
        result = response.json()
        
        context_id = result.get("context_id")
        
        print_result(
            "Context Creation",
            True,
            f"Context ID: {context_id[:12]}..."
        )
        
        # Step 2: Run LH Review
        lh_payload = {
            "context_id": context_id,
            "housing_type": "청년",
            "target_units": 25
        }
        
        lh_response = requests.post(f"{BASE_URL}/api/v40/lh-review/predict", json=lh_payload)
        lh_response.raise_for_status()
        lh_result = lh_response.json()
        
        score = lh_result.get('predicted_score', 0)
        probability = lh_result.get('pass_probability', 0)
        
        print_result(
            "LH Review Prediction",
            score > 0,
            f"Score: {score}/100, Probability: {probability}%"
        )
        
        # Store LH review in context (simulate)
        # In production, this would be done automatically by the API
        
        return True, context_id
        
    except Exception as e:
        print_result("Context & LH Review", False, str(e))
        return False, None


def test_2_landowner_brief_generation(context_id: str):
    """Test 2: Generate Landowner Brief (3p) report"""
    print_test_header("Test 2: Landowner Brief (3p) 보고서 생성")
    
    try:
        # Generate report
        response = requests.get(
            f"{BASE_URL}/api/v40.2/reports/{context_id}/landowner_brief"
        )
        response.raise_for_status()
        
        # Check response
        content_type = response.headers.get('Content-Type')
        content_length = len(response.content)
        
        passed = (
            content_type == 'application/pdf' and
            content_length > 10000  # At least 10KB
        )
        
        print_result(
            "Landowner Brief Generation",
            passed,
            f"Size: {content_length/1024:.1f}KB, Type: {content_type}"
        )
        
        # Save to file for manual inspection
        if passed:
            with open('/tmp/landowner_brief_test.pdf', 'wb') as f:
                f.write(response.content)
            print(f"  └─ Saved to: /tmp/landowner_brief_test.pdf")
        
        return passed, response.content
        
    except Exception as e:
        print_result("Landowner Brief Generation", False, str(e))
        return False, None


def test_3_appraisal_v39_generation(context_id: str):
    """Test 3: Generate Appraisal v39 report (backward compatibility)"""
    print_test_header("Test 3: Appraisal v39 (하위 호환) 보고서 생성")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v40.2/reports/{context_id}/appraisal_v39"
        )
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type')
        content_length = len(response.content)
        
        passed = (
            content_type == 'application/pdf' and
            content_length > 50000  # At least 50KB (larger than landowner brief)
        )
        
        print_result(
            "Appraisal v39 Generation",
            passed,
            f"Size: {content_length/1024:.1f}KB, Type: {content_type}"
        )
        
        return passed, response.content
        
    except Exception as e:
        print_result("Appraisal v39 Generation", False, str(e))
        return False, None


def test_4_invalid_report_type(context_id: str):
    """Test 4: Test invalid report type handling"""
    print_test_header("Test 4: 잘못된 보고서 타입 처리")
    
    try:
        # Try to generate a report with invalid type
        response = requests.get(
            f"{BASE_URL}/api/v40.2/reports/{context_id}/invalid_type"
        )
        
        # Should return 400 error
        passed = response.status_code == 400
        
        print_result(
            "Invalid Report Type Handling",
            passed,
            f"Status Code: {response.status_code} (Expected 400)"
        )
        
        return passed, None
        
    except Exception as e:
        # If exception is raised, check if it's the expected error
        passed = "400" in str(e) or "지원하지 않는" in str(e)
        print_result("Invalid Report Type Handling", passed, str(e))
        return passed, None


def test_5_future_report_types(context_id: str):
    """Test 5: Test future report types (not yet implemented)"""
    print_test_header("Test 5: 향후 지원 예정 보고서 타입")
    
    future_types = ["lh_submission", "policy_impact", "developer_feasibility"]
    results = []
    
    for report_type in future_types:
        try:
            response = requests.get(
                f"{BASE_URL}/api/v40.2/reports/{context_id}/{report_type}"
            )
            
            # Should return 501 (Not Implemented)
            passed = response.status_code == 501
            results.append(passed)
            
            status_text = "✅ Correct (501)" if passed else f"❌ Wrong ({response.status_code})"
            print(f"  • {report_type}: {status_text}")
            
        except Exception as e:
            passed = "501" in str(e) or "지원 예정" in str(e)
            results.append(passed)
            print(f"  • {report_type}: {'✅' if passed else '❌'}")
    
    all_passed = all(results)
    print_result(
        "Future Report Types",
        all_passed,
        f"{sum(results)}/{len(results)} types correctly handled"
    )
    
    return all_passed, None


def test_6_report_validation():
    """Test 6: Test report validation without LH review"""
    print_test_header("Test 6: LH Review 없이 보고서 요청")
    
    try:
        # Create context without LH review
        payload = {
            "address": "서울특별시 강남구 역삼동 123",
            "land_area_sqm": 500.0
        }
        
        response = requests.post(f"{BASE_URL}/api/v40.2/run-analysis", json=payload)
        response.raise_for_status()
        result = response.json()
        
        context_id = result.get("context_id")
        
        # Try to generate Landowner Brief (should still work but with warning)
        report_response = requests.get(
            f"{BASE_URL}/api/v40.2/reports/{context_id}/landowner_brief"
        )
        
        # Should succeed (LH review is optional for landowner brief)
        passed = report_response.status_code == 200
        
        print_result(
            "Report without LH Review",
            passed,
            "보고서 생성 성공 (LH Review 선택사항)"
        )
        
        return passed, context_id
        
    except Exception as e:
        print_result("Report without LH Review", False, str(e))
        return False, None


def run_all_tests():
    """Run all v40.4 report generation tests"""
    print(f"\n{Colors.BLUE}{'='*80}")
    print("ZeroSite v40.4 - Report Generation Tests")
    print("보고서 5종 체계 통합 테스트")
    print(f"{'='*80}{Colors.END}\n")
    
    results = []
    
    # Test 1: Create Context + LH Review
    passed, context_id = test_1_create_context_with_lh_review()
    results.append(("Context & LH Review", passed))
    
    if not passed or not context_id:
        print(f"\n{Colors.RED}❌ Context creation failed. Stopping tests.{Colors.END}")
        return
    
    # Test 2: Landowner Brief
    passed, _ = test_2_landowner_brief_generation(context_id)
    results.append(("Landowner Brief (3p)", passed))
    
    # Test 3: Appraisal v39 (backward compatibility)
    passed, _ = test_3_appraisal_v39_generation(context_id)
    results.append(("Appraisal v39 (하위 호환)", passed))
    
    # Test 4: Invalid report type
    passed, _ = test_4_invalid_report_type(context_id)
    results.append(("Invalid Type Handling", passed))
    
    # Test 5: Future report types
    passed, _ = test_5_future_report_types(context_id)
    results.append(("Future Types (501)", passed))
    
    # Test 6: Report without LH review
    passed, _ = test_6_report_validation()
    results.append(("Without LH Review", passed))
    
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
        print(f"\n{Colors.GREEN}🎉 ALL TESTS PASSED! v40.4 Report System is working!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠️ Some tests failed. Please review the results above.{Colors.END}")
    
    # Additional info
    print(f"\n{Colors.BLUE}📊 Report Status:{Colors.END}")
    print("  ✅ Landowner Brief (3p) - Implemented")
    print("  ⏳ LH Submission (10~15p) - v40.5 예정")
    print("  ⏳ Policy Impact (15p) - v40.5 예정")
    print("  ⏳ Developer Feasibility (15~20p) - v40.5 예정")
    print("  ⏳ Extended Professional (25~40p) - v40.5 예정")
    print("  ✅ Appraisal v39 (23~30p) - 하위 호환 유지")


if __name__ == "__main__":
    run_all_tests()
