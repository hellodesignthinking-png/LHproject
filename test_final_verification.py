#!/usr/bin/env python3
"""
🎯 ZeroSite 최종 검증 스크립트
Issue #19 (데이터 정확성) & Issue #20 (20페이지 PDF) 완전 검증
"""

import requests
import PyPDF2
import json
import sys
from typing import Dict, List, Tuple

# API Base URL
BASE_URL = "https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v30"

class Colors:
    """터미널 색상"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """헤더 출력"""
    print("\n" + "=" * 80)
    print(f"{Colors.BOLD}{text}{Colors.END}")
    print("=" * 80)

def print_success(text: str):
    """성공 메시지"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    """에러 메시지"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str):
    """경고 메시지"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text: str):
    """정보 메시지"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

# Test Cases
TEST_ADDRESSES = [
    {
        "name": "신림동 1524-8",
        "address": "서울특별시 관악구 신림동 1524-8",
        "land_area": 450,
        "expected": {
            "zone_type": "준주거지역",
            "official_price": 9039000,
            "price_tolerance": 10000  # ±10,000원 허용
        }
    },
    {
        "name": "성산동 250-40",
        "address": "서울특별시 마포구 성산동 250-40",
        "land_area": 300,
        "expected": {
            "zone_type": "제2종일반주거지역",
            "official_price": 5893000,
            "price_tolerance": 10000
        }
    },
    {
        "name": "역삼동 680-11",
        "address": "서울특별시 강남구 역삼동 680-11",
        "land_area": 500,
        "expected": {
            "zone_type": "제3종일반주거지역",
            "official_price": 27200000,
            "price_tolerance": 100000
        }
    }
]

def test_data_accuracy(test_case: Dict) -> Tuple[bool, Dict]:
    """
    Issue #19: 데이터 정확성 테스트
    
    Returns:
        (success, result_data)
    """
    print(f"\n📍 테스트: {test_case['name']}")
    print(f"   주소: {test_case['address']}")
    
    try:
        # API 호출
        response = requests.post(
            f"{BASE_URL}/appraisal",
            json={
                "address": test_case['address'],
                "land_area_pyeong": test_case['land_area']
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print_error(f"API 호출 실패: {response.status_code}")
            return False, {}
        
        data = response.json()
        land_info = data['land_info']
        
        # 용도지역 검증
        actual_zone = land_info['zone_type']
        expected_zone = test_case['expected']['zone_type']
        
        zone_correct = actual_zone == expected_zone
        
        if zone_correct:
            print_success(f"용도지역: {actual_zone}")
        else:
            print_error(f"용도지역: {actual_zone} (예상: {expected_zone})")
        
        # 공시지가 검증
        actual_price = land_info['official_land_price_per_sqm']
        expected_price = test_case['expected']['official_price']
        tolerance = test_case['expected']['price_tolerance']
        
        price_diff = abs(actual_price - expected_price)
        price_correct = price_diff <= tolerance
        
        if price_correct:
            print_success(f"공시지가: {actual_price:,}원/㎡")
        else:
            print_error(f"공시지가: {actual_price:,}원/㎡ (예상: {expected_price:,}원/㎡, 차이: {price_diff:,}원)")
        
        # 추가 정보
        print(f"   평가액: {data['appraisal']['final_value']:,.0f}원")
        print(f"   거래사례: {data['comparable_sales']['total_count']}건")
        
        return zone_correct and price_correct, data
        
    except Exception as e:
        print_error(f"오류: {str(e)}")
        return False, {}

def test_pdf_generation(test_case: Dict) -> Tuple[bool, str]:
    """
    Issue #20: 20페이지 PDF 생성 테스트
    
    Returns:
        (success, pdf_path)
    """
    print(f"\n📄 PDF 생성: {test_case['name']}")
    
    try:
        # PDF 생성 요청
        response = requests.post(
            f"{BASE_URL}/appraisal/pdf",
            json={
                "address": test_case['address'],
                "land_area_pyeong": test_case['land_area']
            },
            timeout=60
        )
        
        if response.status_code != 200:
            print_error(f"PDF 생성 실패: {response.status_code}")
            return False, ""
        
        # PDF 저장
        pdf_path = f"/tmp/test_{test_case['name'].replace(' ', '_')}.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        
        # PDF 검증
        import os
        file_size = os.path.getsize(pdf_path)
        
        if file_size < 10000:
            print_error(f"PDF 크기 이상: {file_size} bytes")
            return False, pdf_path
        
        print_success(f"PDF 생성 완료: {file_size:,} bytes")
        
        # 페이지 수 확인
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            page_count = len(pdf_reader.pages)
        
        if page_count == 20:
            print_success(f"페이지 수: {page_count} (정확)")
        else:
            print_error(f"페이지 수: {page_count} (예상: 20)")
            return False, pdf_path
        
        # 첫 페이지 내용 확인
        try:
            first_page_text = pdf_reader.pages[0].extract_text()
            if test_case['address'] in first_page_text or test_case['name'] in first_page_text:
                print_success("주소 확인 완료")
            else:
                print_warning("주소 확인 불가")
        except Exception:
            print_warning("주소 추출 오류 (PDF는 정상)")
        
        return True, pdf_path
        
    except Exception as e:
        print_error(f"오류: {str(e)}")
        return False, ""

def test_transaction_data_preservation(test_case: Dict) -> bool:
    """
    거래사례 데이터 보존 확인
    """
    print(f"\n🔍 거래사례 확인: {test_case['name']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/appraisal",
            json={
                "address": test_case['address'],
                "land_area_pyeong": test_case['land_area']
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print_error("API 호출 실패")
            return False
        
        data = response.json()
        transactions = data['comparable_sales']['transactions']
        
        if len(transactions) > 0:
            print_success(f"거래사례: {len(transactions)}건")
            
            # 첫 3건 출력
            for i, tx in enumerate(transactions[:3], 1):
                try:
                    address = tx.get('address', tx.get('dong', 'N/A'))
                    price = tx.get('price_sqm', tx.get('price', 0))
                    print(f"   {i}. {address} - {price:,}원/㎡")
                except Exception as e:
                    print(f"   {i}. [표시 오류]")
            
            return True
        else:
            print_warning("거래사례 없음")
            return False
            
    except Exception as e:
        print_error(f"오류: {str(e)}")
        return False

def main():
    """메인 테스트 실행"""
    
    print_header("🎯 ZeroSite 최종 검증 - Issue #19 & #20")
    
    print_info(f"API 엔드포인트: {BASE_URL}")
    print_info(f"테스트 케이스: {len(TEST_ADDRESSES)}개")
    
    # 결과 저장
    results = {
        "data_accuracy": [],
        "pdf_generation": [],
        "transaction_preservation": []
    }
    
    # Issue #19: 데이터 정확성 테스트
    print_header("Issue #19: 데이터 정확성 테스트")
    
    for test_case in TEST_ADDRESSES:
        success, data = test_data_accuracy(test_case)
        results["data_accuracy"].append({
            "name": test_case['name'],
            "success": success
        })
    
    # Issue #20: PDF 생성 테스트
    print_header("Issue #20: 20페이지 PDF 생성 테스트")
    
    for test_case in TEST_ADDRESSES[:2]:  # 처음 2개만 테스트
        success, pdf_path = test_pdf_generation(test_case)
        results["pdf_generation"].append({
            "name": test_case['name'],
            "success": success,
            "path": pdf_path
        })
    
    # 거래사례 보존 테스트
    print_header("거래사례 데이터 보존 확인")
    
    for test_case in TEST_ADDRESSES:
        success = test_transaction_data_preservation(test_case)
        results["transaction_preservation"].append({
            "name": test_case['name'],
            "success": success
        })
    
    # 최종 결과
    print_header("🏁 최종 결과")
    
    # Issue #19 결과
    data_success_count = sum(1 for r in results["data_accuracy"] if r["success"])
    data_total = len(results["data_accuracy"])
    
    print(f"\n✅ Issue #19 (데이터 정확성): {data_success_count}/{data_total} 통과")
    for r in results["data_accuracy"]:
        status = "✅" if r["success"] else "❌"
        print(f"   {status} {r['name']}")
    
    # Issue #20 결과
    pdf_success_count = sum(1 for r in results["pdf_generation"] if r["success"])
    pdf_total = len(results["pdf_generation"])
    
    print(f"\n✅ Issue #20 (20페이지 PDF): {pdf_success_count}/{pdf_total} 통과")
    for r in results["pdf_generation"]:
        status = "✅" if r["success"] else "❌"
        print(f"   {status} {r['name']}")
        if r.get("path"):
            print(f"      경로: {r['path']}")
    
    # 거래사례 결과
    tx_success_count = sum(1 for r in results["transaction_preservation"] if r["success"])
    tx_total = len(results["transaction_preservation"])
    
    print(f"\n✅ 거래사례 보존: {tx_success_count}/{tx_total} 통과")
    for r in results["transaction_preservation"]:
        status = "✅" if r["success"] else "❌"
        print(f"   {status} {r['name']}")
    
    # 전체 성공 여부
    all_success = (
        data_success_count == data_total and
        pdf_success_count == pdf_total and
        tx_success_count == tx_total
    )
    
    print("\n" + "=" * 80)
    if all_success:
        print_success("🎉 모든 테스트 통과! 시스템 정상 작동 중")
        print_success("Issue #19 & #20 완전 해결 확인!")
        return 0
    else:
        print_error("⚠️  일부 테스트 실패")
        return 1

if __name__ == "__main__":
    sys.exit(main())
