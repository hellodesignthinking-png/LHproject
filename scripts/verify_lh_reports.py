#!/usr/bin/env python3
"""
LH 기술검증 보고서 실데이터 검증 스크립트
- 실제 RUN_ID 기반 HTML/PDF 생성
- 데이터 일관성 검증
- 주소/PNU/수치 검증
"""

import sys
import requests
import hashlib
import json
from typing import List, Dict, Any
from datetime import datetime

# Test RUN_IDs
TEST_RUN_IDS = [
    "RUN_116801010001230045_1767167669855",
    "RUN_116801010001230045_1767167675689",
    "RUN_116801010001230045_1767167682325"
]

BASE_URL = "http://localhost:8091"

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def verify_html_generation(run_id: str) -> Dict[str, Any]:
    """Verify HTML generation for a given RUN_ID"""
    print_info(f"Testing HTML generation for {run_id}")
    
    url = f"{BASE_URL}/api/v4/reports/lh/technical/html"
    params = {"context_id": run_id}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Verify key elements
            checks = {
                "주소 포함": "서울특별시 마포구 월드컵북로 120" in html_content,
                "PNU 포함": "116801010001230045" in html_content,
                "제목 포함": "LH 매입임대 대상지" in html_content,
                "RUN_ID 포함": run_id in html_content,
                "대상지 식별정보": "대상지 주소" in html_content,
            }
            
            # Calculate content hash
            content_hash = hashlib.md5(html_content.encode()).hexdigest()[:8]
            
            all_passed = all(checks.values())
            
            result = {
                "status": "success" if all_passed else "partial",
                "checks": checks,
                "content_length": len(html_content),
                "content_hash": content_hash,
                "error": None
            }
            
            if all_passed:
                print_success(f"HTML generation OK (hash: {content_hash}, size: {len(html_content)} bytes)")
            else:
                print_warning("HTML generation partial - some checks failed")
                for check, passed in checks.items():
                    if not passed:
                        print_error(f"  Failed: {check}")
            
            return result
            
        else:
            print_error(f"HTTP {response.status_code}: {response.text[:200]}")
            return {
                "status": "error",
                "error": f"HTTP {response.status_code}",
                "checks": {},
                "content_length": 0,
                "content_hash": None
            }
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "checks": {},
            "content_length": 0,
            "content_hash": None
        }

def verify_pdf_generation(run_id: str) -> Dict[str, Any]:
    """Verify PDF generation for a given RUN_ID"""
    print_info(f"Testing PDF generation for {run_id}")
    
    url = f"{BASE_URL}/api/v4/reports/lh/technical/pdf"
    params = {"context_id": run_id}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            pdf_content = response.content
            
            # Basic PDF validation
            is_pdf = pdf_content.startswith(b'%PDF')
            pdf_size = len(pdf_content)
            
            # Calculate content hash
            content_hash = hashlib.md5(pdf_content).hexdigest()[:8]
            
            result = {
                "status": "success" if is_pdf else "error",
                "is_pdf": is_pdf,
                "size": pdf_size,
                "content_hash": content_hash,
                "error": None if is_pdf else "Invalid PDF format"
            }
            
            if is_pdf:
                print_success(f"PDF generation OK (hash: {content_hash}, size: {pdf_size} bytes)")
            else:
                print_error("Generated content is not a valid PDF")
            
            return result
            
        else:
            print_error(f"HTTP {response.status_code}")
            return {
                "status": "error",
                "error": f"HTTP {response.status_code}",
                "is_pdf": False,
                "size": 0,
                "content_hash": None
            }
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "is_pdf": False,
            "size": 0,
            "content_hash": None
        }

def verify_consistency(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify consistency across multiple RUN_IDs"""
    print_header("일관성 검증 (Consistency Check)")
    
    html_results = [r['html'] for r in results if r['html']['status'] == 'success']
    pdf_results = [r['pdf'] for r in results if r['pdf']['status'] == 'success']
    
    consistency_checks = {
        "HTML 생성 성공률": len(html_results) == len(TEST_RUN_IDS),
        "PDF 생성 성공률": len(pdf_results) == len(TEST_RUN_IDS),
        "주소 일관성": all(r['html']['checks'].get("주소 포함", False) for r in results if r['html']['status'] == 'success'),
        "PNU 일관성": all(r['html']['checks'].get("PNU 포함", False) for r in results if r['html']['status'] == 'success'),
    }
    
    # Check if content is deterministic (should be different for different RUN_IDs due to timestamps)
    html_hashes = [r['content_hash'] for r in html_results]
    pdf_hashes = [r['content_hash'] for r in pdf_results]
    
    print_info(f"HTML hashes: {html_hashes}")
    print_info(f"PDF hashes: {pdf_hashes}")
    
    all_passed = all(consistency_checks.values())
    
    for check, passed in consistency_checks.items():
        if passed:
            print_success(check)
        else:
            print_error(check)
    
    return {
        "all_passed": all_passed,
        "checks": consistency_checks,
        "html_success_rate": f"{len(html_results)}/{len(TEST_RUN_IDS)}",
        "pdf_success_rate": f"{len(pdf_results)}/{len(TEST_RUN_IDS)}"
    }

def main():
    print_header("🔒 LH 기술검증 보고서 실데이터 검증")
    
    print(f"검증 대상 RUN_ID: {len(TEST_RUN_IDS)}개")
    print(f"베이스 URL: {BASE_URL}")
    print(f"검증 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    for i, run_id in enumerate(TEST_RUN_IDS, 1):
        print_header(f"RUN_ID {i}/{len(TEST_RUN_IDS)}: {run_id}")
        
        html_result = verify_html_generation(run_id)
        pdf_result = verify_pdf_generation(run_id)
        
        results.append({
            "run_id": run_id,
            "html": html_result,
            "pdf": pdf_result
        })
        
        print()  # Empty line between tests
    
    # Verify consistency
    consistency_result = verify_consistency(results)
    
    # Final summary
    print_header("📊 최종 검증 결과")
    
    total_html_success = sum(1 for r in results if r['html']['status'] == 'success')
    total_pdf_success = sum(1 for r in results if r['pdf']['status'] == 'success')
    
    print(f"HTML 생성 성공: {total_html_success}/{len(TEST_RUN_IDS)}")
    print(f"PDF 생성 성공: {total_pdf_success}/{len(TEST_RUN_IDS)}")
    print(f"일관성 검증: {'✅ PASS' if consistency_result['all_passed'] else '❌ FAIL'}")
    
    # Save results to file
    output_file = f"/home/user/webapp/lh_verification_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "test_run_ids": TEST_RUN_IDS,
            "results": results,
            "consistency": consistency_result
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n검증 결과 저장: {output_file}")
    
    # Exit code
    if consistency_result['all_passed']:
        print_success("\n🎉 모든 검증 통과!")
        return 0
    else:
        print_error("\n❌ 일부 검증 실패")
        return 1

if __name__ == "__main__":
    sys.exit(main())
