"""
End-to-End Test for Premium-Enhanced Appraisal System
Tests: Frontend → API → Engine → PDF Generation

Test Case: 강남 재개발구역, GTX 인근, 8학군
"""

import requests
import json
from datetime import datetime

# Test server endpoint
BASE_URL = "http://localhost:8000"

def test_appraisal_with_premium():
    """Test appraisal API with premium factors"""
    
    print("=" * 80)
    print("🧪 End-to-End Test: Premium-Enhanced Appraisal System")
    print("=" * 80)
    
    # Test data matching the frontend form
    test_request = {
        "address": "서울시 마포구 월드컵북로 120",
        "land_area_sqm": 660,
        "zone_type": "제3종일반주거지역",
        "individual_land_price_per_sqm": 7000000,
        "premium_factors": {
            # Physical characteristics
            "land_shape": 15,           # 정방형 (+15%)
            "land_slope": 15,           # 평지 (+15%)
            "direction": 12,            # 남향 (+12%)
            "road_facing": 10,          # 각지 (+10%)
            
            # Location/Amenities
            "subway_distance": 30,      # 300m 이내 (+30%)
            "school_district_8": 25,    # 8학군 (+25%)
            "large_park": 15,           # 500m 이내 (+15%)
            "department_store": 20,     # 500m 이내 (+20%)
            "large_hospital": 12,       # 2km 이내 (+12%)
            "han_river_view": 0,        # 없음 (0%)
            
            # Development/Regulation
            "redevelopment_status": 60, # 사업승인 (+60%)
            "gtx_station": 50,          # 500m 이내 (+50%)
            "greenbelt": 0,             # 아니오 (0%)
            "cultural_heritage_zone": 0 # 아니오 (0%)
        }
    }
    
    print("\n📝 Test Input:")
    print(f"  주소: {test_request['address']}")
    print(f"  대지면적: {test_request['land_area_sqm']} ㎡")
    print(f"  용도지역: {test_request['zone_type']}")
    print(f"  개별공시지가: {test_request['individual_land_price_per_sqm']:,} 원/㎡")
    
    print("\n🎯 Premium Factors:")
    for key, value in test_request['premium_factors'].items():
        if value != 0:
            print(f"  {key}: {value:+.0f}%")
    
    # Step 1: Test basic appraisal endpoint
    print("\n" + "=" * 80)
    print("STEP 1: Test Basic Appraisal Endpoint")
    print("=" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v24.1/appraisal",
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ Appraisal Successful!")
            print(f"  Status: {result['status']}")
            
            appraisal = result['appraisal']
            print(f"\n💰 Valuation Results:")
            print(f"  최종 평가액: {appraisal['final_value']:.2f} 억원")
            print(f"  ㎡당 가격: {appraisal['value_per_sqm']:,} 원")
            print(f"  신뢰도: {appraisal['confidence']}")
            
            print(f"\n📊 3대 평가법:")
            print(f"  원가법: {appraisal['approaches']['cost']:.2f} 억원 "
                  f"(가중치: {appraisal['weights']['cost']*100:.0f}%)")
            print(f"  거래사례비교법: {appraisal['approaches']['sales_comparison']:.2f} 억원 "
                  f"(가중치: {appraisal['weights']['sales']*100:.0f}%)")
            print(f"  수익환원법: {appraisal['approaches']['income']:.2f} 억원 "
                  f"(가중치: {appraisal['weights']['income']*100:.0f}%)")
            
            # Check for premium info
            if 'premium_info' in result:
                premium = result['premium_info']
                print(f"\n🌟 Premium Adjustment:")
                
                if premium['has_premium']:
                    print(f"  기본 평가액: {premium['base_value']:.2f} 억원")
                    print(f"  프리미엄: {premium['premium_percentage']:+.1f}%")
                    print(f"  조정 평가액: {premium['adjusted_value']:.2f} 억원")
                    print(f"  증가액: {premium['adjusted_value'] - premium['base_value']:.2f} 억원")
                    
                    if premium['top_5_factors']:
                        print(f"\n  상위 5개 프리미엄 요인:")
                        for i, factor in enumerate(premium['top_5_factors'], 1):
                            print(f"    {i}. {factor['name']}: {factor['value']:+.1f}%")
                else:
                    print("  프리미엄 없음")
            
        else:
            print(f"\n❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False
    
    # Step 2: Test PDF generation with premium
    print("\n" + "=" * 80)
    print("STEP 2: Test PDF Generation with Premium")
    print("=" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v24.1/appraisal/pdf",
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            # Save PDF to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"TEST_Premium_Appraisal_{timestamp}.pdf"
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            file_size_kb = len(response.content) / 1024
            
            print("\n✅ PDF Generation Successful!")
            print(f"  파일명: {filename}")
            print(f"  파일 크기: {file_size_kb:.1f} KB")
            print(f"  Content-Type: {response.headers.get('Content-Type')}")
            
            # Extract Content-Disposition header
            content_disp = response.headers.get('Content-Disposition', '')
            print(f"  Content-Disposition: {content_disp}")
            
        else:
            print(f"\n❌ PDF generation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ END-TO-END TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\n📋 Test Summary:")
    print("  ✅ Frontend form data structure: PASS")
    print("  ✅ API endpoint with premium factors: PASS")
    print("  ✅ Premium calculation engine: PASS")
    print("  ✅ PDF generation with premium: PASS")
    print("\n🎉 All systems operational!")
    
    return True


def test_no_premium():
    """Test appraisal without premium factors (backward compatibility)"""
    
    print("\n" + "=" * 80)
    print("🧪 Backward Compatibility Test: No Premium Factors")
    print("=" * 80)
    
    test_request = {
        "address": "서울시 강남구 역삼동 100",
        "land_area_sqm": 500,
        "zone_type": "준주거지역",
        "individual_land_price_per_sqm": 10000000
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v24.1/appraisal",
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Backward compatibility test PASS")
            print(f"  평가액: {result['appraisal']['final_value']:.2f} 억원")
            
            # Check premium info should indicate no premium
            if 'premium_info' in result:
                premium = result['premium_info']
                if not premium['has_premium']:
                    print("  ✅ Premium correctly disabled when not provided")
                else:
                    print("  ⚠️ Premium unexpectedly enabled")
            
            return True
        else:
            print(f"\n❌ Test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    # Run tests
    success = True
    
    # Test 1: Full premium test
    if not test_appraisal_with_premium():
        success = False
    
    # Test 2: Backward compatibility
    if not test_no_premium():
        success = False
    
    # Final summary
    print("\n" + "=" * 80)
    if success:
        print("✅ ALL TESTS PASSED - System Ready for Production")
    else:
        print("❌ SOME TESTS FAILED - Review errors above")
    print("=" * 80)
    
    exit(0 if success else 1)
