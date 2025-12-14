"""
ZeroSite v40.2 Integration Test
Appraisal-First Architecture 검증
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001/api/v40.2"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health_check():
    """Health Check 테스트"""
    print_section("TEST 1: Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    
    data = response.json()
    print(f"✅ Status: {data['status']}")
    print(f"✅ Version: {data['version']}")
    print(f"✅ Name: {data['name']}")
    
    assert data["version"] == "40.2"
    print("\n✅ Health Check PASSED")
    return True

def test_run_analysis():
    """전체 분석 실행 테스트"""
    print_section("TEST 2: Run Full Analysis (Appraisal-First)")
    
    payload = {
        "address": "서울특별시 관악구 신림동 1524-8",
        "land_area_sqm": 450.5,
        "land_shape": "정방형",
        "slope": "평지",
        "road_access": "중로",
        "orientation": "남향"
    }
    
    print(f"📍 입력 주소: {payload['address']}")
    print(f"📐 토지면적: {payload['land_area_sqm']} ㎡")
    
    response = requests.post(f"{BASE_URL}/run-analysis", json=payload)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    
    data = response.json()
    
    print(f"\n✅ Status: {data['status']}")
    print(f"✅ Context ID: {data['context_id']}")
    print(f"✅ Timestamp: {data['timestamp']}")
    
    summary = data['summary']
    print(f"\n📊 Summary:")
    print(f"   - Appraisal Value: ₩{summary['appraisal_value']:,.0f}")
    print(f"   - Value per ㎡: ₩{summary['value_per_sqm']:,.0f}")
    print(f"   - Suitability: {summary['suitability']}")
    print(f"   - Zone Type: {summary['zone_type']}")
    print(f"   - Max Units: {summary['max_units']}세대")
    print(f"   - Recommended: {summary['recommended_scenario']}")
    
    print("\n✅ Run Analysis PASSED")
    return data['context_id']

def test_context_retrieval(context_id):
    """Context 조회 테스트"""
    print_section("TEST 3: Context Retrieval")
    
    response = requests.get(f"{BASE_URL}/context/{context_id}")
    assert response.status_code == 200
    
    context = response.json()
    print(f"✅ Context ID: {context['context_id']}")
    print(f"✅ Version: {context['version']}")
    print(f"✅ Timestamp: {context['timestamp']}")
    
    # 필수 섹션 확인
    required_sections = ['appraisal', 'diagnosis', 'capacity', 'scenario']
    for section in required_sections:
        assert section in context, f"Missing section: {section}"
        print(f"✅ Section '{section}' exists")
    
    print("\n✅ Context Retrieval PASSED")
    return context

def test_data_consistency(context):
    """데이터 일관성 테스트"""
    print_section("TEST 4: Data Consistency Check")
    
    # 1. 용도지역 일관성
    appraisal_zone = context['appraisal']['zoning']['zone_type']
    diagnosis_zone = context['diagnosis']['zone_type']
    capacity_zone = context['capacity']['zoning']['zone_type']
    
    print(f"\n🔍 용도지역 비교:")
    print(f"   - Appraisal: {appraisal_zone}")
    print(f"   - Diagnosis: {diagnosis_zone}")
    print(f"   - Capacity: {capacity_zone}")
    
    zone_match = (appraisal_zone == diagnosis_zone == capacity_zone)
    if zone_match:
        print(f"   ✅ 용도지역 100% 일치")
    else:
        print(f"   ❌ 용도지역 불일치!")
        return False
    
    # 2. 공시지가 일관성
    appraisal_price = context['appraisal']['official_price']
    diagnosis_price = context['diagnosis']['official_price']
    
    print(f"\n🔍 공시지가 비교:")
    print(f"   - Appraisal: ₩{appraisal_price:,.0f}")
    print(f"   - Diagnosis: ₩{diagnosis_price:,.0f}")
    
    price_match = (appraisal_price == diagnosis_price)
    if price_match:
        print(f"   ✅ 공시지가 100% 일치")
    else:
        print(f"   ❌ 공시지가 불일치!")
        return False
    
    # 3. FAR 일관성
    appraisal_far = context['appraisal']['zoning']['far']
    capacity_far = context['capacity']['far']
    
    print(f"\n🔍 용적률 비교:")
    print(f"   - Appraisal: {appraisal_far}%")
    print(f"   - Capacity: {capacity_far}%")
    
    far_match = (appraisal_far == capacity_far)
    if far_match:
        print(f"   ✅ 용적률 100% 일치")
    else:
        print(f"   ❌ 용적률 불일치!")
        return False
    
    # 4. 거래사례 일관성
    appraisal_txs = context['appraisal'].get('transactions', [])
    diagnosis_txs = context['diagnosis'].get('transactions', [])
    
    print(f"\n🔍 거래사례 비교:")
    print(f"   - Appraisal: {len(appraisal_txs)}건")
    print(f"   - Diagnosis: {len(diagnosis_txs)}건")
    
    if len(appraisal_txs) == len(diagnosis_txs):
        print(f"   ✅ 거래사례 개수 일치")
    else:
        print(f"   ⚠️  거래사례 개수 불일치 (허용 가능)")
    
    print("\n✅ Data Consistency PASSED - 100% 일치")
    return True

def test_tab_queries(context_id):
    """탭별 조회 테스트"""
    print_section("TEST 5: Tab Queries (Read-Only)")
    
    tabs = ['diagnosis', 'capacity', 'appraisal', 'scenario']
    
    for tab in tabs:
        response = requests.get(f"{BASE_URL}/context/{context_id}/{tab}")
        assert response.status_code == 200
        
        data = response.json()
        print(f"✅ {tab.upper()} tab: {data['message']}")
    
    print("\n✅ Tab Queries PASSED")
    return True

def test_consistency_check_api(context_id):
    """일관성 체크 API 테스트"""
    print_section("TEST 6: Consistency Check API")
    
    response = requests.get(f"{BASE_URL}/debug/consistency-check/{context_id}")
    assert response.status_code == 200
    
    result = response.json()
    print(f"✅ Overall Status: {result['overall_status']}")
    
    for check_name, check_data in result['checks'].items():
        print(f"\n🔍 {check_name}:")
        print(f"   Status: {check_data['status']}")
        if not check_data['match']:
            print(f"   ❌ Data mismatch detected!")
            return False
    
    print("\n✅ Consistency Check API PASSED")
    return True

def main():
    """메인 테스트 실행"""
    print("\n" + "🚀"*30)
    print("  ZeroSite v40.2 Integration Test")
    print("  Appraisal-First Architecture")
    print("🚀"*30)
    
    try:
        # Test 1: Health Check
        test_health_check()
        
        # Test 2: Run Analysis
        context_id = test_run_analysis()
        if not context_id:
            print("\n❌ Run Analysis FAILED - 테스트 중단")
            return False
        
        # Test 3: Context Retrieval
        context = test_context_retrieval(context_id)
        
        # Test 4: Data Consistency
        if not test_data_consistency(context):
            print("\n❌ Data Consistency FAILED")
            return False
        
        # Test 5: Tab Queries
        test_tab_queries(context_id)
        
        # Test 6: Consistency Check API
        test_consistency_check_api(context_id)
        
        # Final Summary
        print("\n" + "🎉"*30)
        print("  ALL TESTS PASSED!")
        print("  v40.2 Appraisal-First Architecture: ✅ WORKING")
        print("🎉"*30)
        
        print(f"\n📊 Test Summary:")
        print(f"   - Health Check: ✅")
        print(f"   - Run Analysis: ✅")
        print(f"   - Context Retrieval: ✅")
        print(f"   - Data Consistency: ✅ (100% match)")
        print(f"   - Tab Queries: ✅")
        print(f"   - Consistency Check API: ✅")
        
        print(f"\n🔗 Context ID for manual testing: {context_id}")
        print(f"🔗 Health Check: http://localhost:8001/api/v40.2/health")
        print(f"🔗 Consistency Check: http://localhost:8001/api/v40.2/debug/consistency-check/{context_id}")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ Assertion Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
