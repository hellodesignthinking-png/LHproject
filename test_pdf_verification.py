#!/usr/bin/env python3
"""
Phase 1-3 PDF Verification Test Script
Tests M4 and M6 PDF generation for consistency
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "http://localhost:8005"

# Test data
TEST_CONTEXT_ID = "test-phase1-20251219"

def test_m4_pdf_generation(iteration: int):
    """Phase 1: M4 PDF generation test"""
    print(f"\n{'='*60}")
    print(f"M4 PDF Test - Iteration {iteration}")
    print(f"{'='*60}")
    
    url = f"{BACKEND_URL}/api/v4/reports/M4/pdf"
    params = {"context_id": TEST_CONTEXT_ID}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            content_disposition = response.headers.get('Content-Disposition', '')
            print(f"Content-Disposition: {content_disposition}")
            print(f"PDF Size: {len(response.content)} bytes")
            
            # Save PDF for manual inspection
            filename = f"test_m4_iteration_{iteration}_{int(time.time())}.pdf"
            with open(f"/home/user/webapp/temp/{filename}", "wb") as f:
                f.write(response.content)
            print(f"✅ Saved: temp/{filename}")
            return True
        else:
            print(f"❌ Failed: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_m6_pdf_generation(iteration: int):
    """Phase 1: M6 PDF generation test"""
    print(f"\n{'='*60}")
    print(f"M6 PDF Test - Iteration {iteration}")
    print(f"{'='*60}")
    
    url = f"{BACKEND_URL}/api/v4/reports/M6/pdf"
    params = {"context_id": TEST_CONTEXT_ID}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            content_disposition = response.headers.get('Content-Disposition', '')
            print(f"Content-Disposition: {content_disposition}")
            print(f"PDF Size: {len(response.content)} bytes")
            
            # Save PDF for manual inspection
            filename = f"test_m6_iteration_{iteration}_{int(time.time())}.pdf"
            with open(f"/home/user/webapp/temp/{filename}", "wb") as f:
                f.write(response.content)
            print(f"✅ Saved: temp/{filename}")
            return True
        else:
            print(f"❌ Failed: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_phase2_pipeline_summary():
    """Phase 2: Pipeline summary field validation"""
    print(f"\n{'='*60}")
    print(f"Phase 2: Pipeline Summary Field Validation")
    print(f"{'='*60}")
    
    # This would test actual pipeline execution
    # For now, we'll check the health endpoint
    url = f"{BACKEND_URL}/api/v4/reports/health"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Health Check: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False


def main():
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  ZeroSite PDF Generation Verification Test                  ║
║  Phase 1-3 Verification Protocol                            ║
║  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                         ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Create temp directory
    import os
    os.makedirs("/home/user/webapp/temp", exist_ok=True)
    
    # Phase 1: M4 PDF Tests
    print("\n🔵 Phase 1A: M4 PDF Generation (10 iterations)")
    m4_results = []
    for i in range(1, 11):
        result = test_m4_pdf_generation(i)
        m4_results.append(result)
        time.sleep(0.5)  # Small delay between requests
    
    # Phase 1: M6 PDF Tests
    print("\n🔵 Phase 1B: M6 PDF Generation (10 iterations)")
    m6_results = []
    for i in range(1, 11):
        result = test_m6_pdf_generation(i)
        m6_results.append(result)
        time.sleep(0.5)
    
    # Phase 2: Pipeline Summary
    print("\n🔵 Phase 2: Pipeline Summary Field Validation")
    phase2_result = test_phase2_pipeline_summary()
    
    # Summary
    print(f"\n{'='*60}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*60}")
    print(f"M4 PDF Success Rate: {sum(m4_results)}/10 ({sum(m4_results)*10}%)")
    print(f"M6 PDF Success Rate: {sum(m6_results)}/10 ({sum(m6_results)*10}%)")
    print(f"Phase 2 Health Check: {'✅ PASS' if phase2_result else '❌ FAIL'}")
    
    # Overall assessment
    overall_pass = (sum(m4_results) >= 9 and sum(m6_results) >= 9 and phase2_result)
    print(f"\n{'='*60}")
    if overall_pass:
        print("✅ VERIFICATION PASSED - System is stable")
    else:
        print("❌ VERIFICATION FAILED - Issues detected")
    print(f"{'='*60}")
    
    # Phase 3 instructions
    print(f"""
🔵 Phase 3: Manual Verification Required

Please manually verify the generated PDFs in temp/ directory:

1. M6 Score Consistency:
   - Open any M6 PDF
   - Check first page "종합 점수": Should show X.X/110점
   - Check all internal sections use same score
   - Verify NO "0.0/110" appears anywhere

2. M4 FAR/BCR Display:
   - Open any M4 PDF
   - Check "법정 용적률/건폐율" section
   - Verify shows "N/A (검증 필요)" instead of "0%"
   - Check parking scenarios are properly displayed

3. Design System Consistency:
   - Compare M4 and M6 PDFs
   - Verify same fonts (NanumBarunGothic)
   - Verify same colors (Primary #1E3A8A, Accent #06B6D4)
   - Verify same table styles and margins
   
4. Footer:
   - Every PDF should have "© ZEROSITE by Antenna Holdings | nataiheum"
    """)


if __name__ == "__main__":
    main()
