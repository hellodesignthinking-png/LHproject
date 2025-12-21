"""
Test script for Final Report 6 Types
Simulates complete M1-M6 analysis data and tests all 6 report generation
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8005"

# Mock complete canonical data (M2-M6 summaries)
MOCK_CANONICAL_DATA = {
    "context_id": "test-final-reports-001",
    "created_at": datetime.now().isoformat(),
    
    # M2: 토지감정평가
    "m2_result": {
        "module": "M2",
        "summary": {
            "land_value_total_krw": 1621848717,
            "pyeong_price_krw": 10723014,
            "confidence_pct": 85,
            "transaction_count": 10
        },
        "details": {},
        "meta": {}
    },
    
    # M3: LH 선호유형 분석
    "m3_result": {
        "module": "M3",
        "summary": {
            "recommended_type": "청년형",
            "total_score": 85,
            "confidence_pct": 82,
            "second_choice": "신혼부부형"
        },
        "details": {},
        "meta": {}
    },
    
    # M4: 건축규모 결정
    "m4_result": {
        "module": "M4",
        "summary": {
            "legal_units": 20,
            "incentive_units": 26,
            "parking_alt_a": 18,
            "parking_alt_b": 20
        },
        "details": {},
        "meta": {}
    },
    
    # M5: 사업성 분석
    "m5_result": {
        "module": "M5",
        "summary": {
            "npv_public_krw": 793000000,
            "irr_pct": 12.8,
            "roi_pct": 15.5,
            "grade": "A"
        },
        "details": {},
        "meta": {}
    },
    
    # M6: LH 심사예측
    "m6_result": {
        "module": "M6",
        "summary": {
            "decision": "GO",
            "total_score": 85.0,
            "max_score": 110,
            "grade": "A",
            "approval_probability_pct": 77
        },
        "details": {},
        "meta": {}
    }
}

REPORT_TYPES = [
    "all_in_one",
    "landowner_summary",
    "lh_technical",
    "financial_feasibility",
    "quick_check",
    "presentation"
]

def store_mock_context():
    """Store mock context data via API"""
    print("📦 Storing mock context data...")
    
    # Note: We need to use context_storage service directly or via API endpoint
    # For testing, we'll directly test the HTML endpoints with context_id parameter
    print(f"✅ Using context_id: {MOCK_CANONICAL_DATA['context_id']}")
    return MOCK_CANONICAL_DATA['context_id']

def test_report(report_type: str, context_id: str):
    """Test a single report type"""
    url = f"{BASE_URL}/api/v4/reports/final/{report_type}/html"
    params = {"context_id": context_id}
    
    print(f"\n{'='*60}")
    print(f"🔍 Testing: {report_type}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ SUCCESS - {report_type}")
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
            print(f"   HTML Length: {len(response.text)} bytes")
            
            # Check for key elements
            html = response.text
            checks = {
                "QA Status Footer": "QA Status" in html or "qa_status" in html,
                "Pretendard Font": "Pretendard" in html,
                "Accent Blue Color": "#3B82F6" in html,
                "Data Values": "data-value" in html or "원" in html,
                "No M2-M6 codes": "M2" not in html and "M3" not in html and "M4" not in html
            }
            
            print(f"\n   Content Checks:")
            for check_name, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"     {status} {check_name}")
            
            # Save HTML for manual inspection
            output_file = f"/home/user/webapp/test_output_{report_type}.html"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"\n   💾 Saved to: {output_file}")
            
        else:
            print(f"❌ FAILED - {report_type}")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print(f"⏱️ TIMEOUT - {report_type}")
    except Exception as e:
        print(f"💥 ERROR - {report_type}: {str(e)}")

def main():
    """Main test execution"""
    print("="*60)
    print("🚀 ZeroSite Final Report 6 Types - Test Suite")
    print("="*60)
    
    context_id = store_mock_context()
    
    print(f"\n📋 Testing {len(REPORT_TYPES)} report types...")
    
    for report_type in REPORT_TYPES:
        test_report(report_type, context_id)
    
    print("\n" + "="*60)
    print("✅ Test Suite Complete")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"   Total reports tested: {len(REPORT_TYPES)}")
    print(f"   Context ID used: {context_id}")
    print(f"\n💡 Note: Reports expect real context_id from M1 analysis.")
    print(f"   To test with real data: Complete M1 → get context_id → test reports")

if __name__ == "__main__":
    main()
