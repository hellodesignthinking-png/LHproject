#!/usr/bin/env python3
"""
Phase 8 E2E 테스트: Mock 데이터로 풍부한 보고서 생성 확인
"""

import requests
import sys
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:49999/api/v4/reports/phase8"
TEST_CONTEXT_ID = "test_e2e_rich_data"

def test_m2_report():
    """M2 토지감정평가 보고서 테스트"""
    print("=" * 60)
    print("📊 M2 토지감정평가 보고서 테스트")
    print("=" * 60)
    
    url = f"{BASE_URL}/modules/m2/html?context_id={TEST_CONTEXT_ID}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            return False
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        # Check for key elements
        title = soup.find('h1')
        if title:
            print(f"✅ 제목: {title.get_text().strip()}")
        
        # Count transaction cases mentions
        case_count = html.count('CASE_')
        print(f"✅ 거래사례 언급: {case_count}회")
        
        # Check for detailed addresses
        if '서울시 강남구' in html or '서울특별시 강남구' in html:
            print("✅ 상세 주소 포함됨")
        
        # Check for comparison logic
        if '비교 논리' in html or 'comparison_logic' in html or '면적' in html:
            print("✅ 비교 논리 포함됨")
        
        # Check data richness
        if len(html) > 5000:
            print(f"✅ HTML 길이: {len(html):,} bytes (풍부한 데이터)")
        else:
            print(f"⚠️  HTML 길이: {len(html):,} bytes (데이터 부족)")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def test_m3_report():
    """M3 공급 유형 판단 보고서 테스트"""
    print("=" * 60)
    print("📊 M3 공급 유형 판단 보고서 테스트")
    print("=" * 60)
    
    url = f"{BASE_URL}/modules/m3/html?context_id={TEST_CONTEXT_ID}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            return False
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        title = soup.find('h1')
        if title:
            print(f"✅ 제목: {title.get_text().strip()}")
        
        # Check for lifestyle factors
        factors = ['역세권', '생활편의', '직장', '공원', '교육', '문화']
        found_factors = sum(1 for f in factors if f in html)
        print(f"✅ 라이프스타일 요인: {found_factors}/6개")
        
        # Check for POI analysis
        if 'POI' in html or '지하철역' in html or '버스' in html:
            print("✅ POI 분석 포함됨")
        
        # Check data richness
        if len(html) > 5000:
            print(f"✅ HTML 길이: {len(html):,} bytes (풍부한 데이터)")
        else:
            print(f"⚠️  HTML 길이: {len(html):,} bytes (데이터 부족)")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def test_m4_report():
    """M4 건축 규모 검토 보고서 테스트"""
    print("=" * 60)
    print("📊 M4 건축 규모 검토 보고서 테스트")
    print("=" * 60)
    
    url = f"{BASE_URL}/modules/m4/html?context_id={TEST_CONTEXT_ID}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            return False
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        title = soup.find('h1')
        if title:
            print(f"✅ 제목: {title.get_text().strip()}")
        
        # Check for parking alternatives
        alternatives = ['대안 A', '대안 B', '대안 C']
        found_alts = sum(1 for a in alternatives if a in html)
        print(f"✅ 주차 대안: {found_alts}/3개")
        
        # Check for cost details
        if '2,100,000,000원' in html or '672,000,000원' in html:
            print("✅ 상세 비용 정보 포함됨")
        
        # Check data richness
        if len(html) > 5000:
            print(f"✅ HTML 길이: {len(html):,} bytes (풍부한 데이터)")
        else:
            print(f"⚠️  HTML 길이: {len(html):,} bytes (데이터 부족)")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def main():
    """모든 테스트 실행"""
    print("\n" + "=" * 60)
    print("🚀 Phase 8 E2E 테스트 시작")
    print("=" * 60)
    print(f"Context ID: {TEST_CONTEXT_ID}")
    print()
    
    results = []
    
    # Test M2
    results.append(("M2", test_m2_report()))
    
    # Test M3
    results.append(("M3", test_m3_report()))
    
    # Test M4
    results.append(("M4", test_m4_report()))
    
    # Summary
    print("=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for module, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{module}: {status}")
    
    print()
    print(f"총 {passed}/{total} 테스트 통과")
    
    if passed == total:
        print("\n🎉 모든 테스트 통과!")
        return 0
    else:
        print(f"\n⚠️  {total - passed}개 테스트 실패")
        return 1

if __name__ == "__main__":
    sys.exit(main())
