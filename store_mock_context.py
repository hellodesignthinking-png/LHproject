"""
Store mock canonical data in context storage for testing final reports
"""

import sys
sys.path.append("/home/user/webapp")

from app.services.context_storage import context_storage
import json
from datetime import datetime

# Mock complete canonical data
MOCK_DATA = {
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

def main():
    context_id = "test-final-reports-001"
    
    print("="*60)
    print("📦 Storing Mock Canonical Data")
    print("="*60)
    print(f"Context ID: {context_id}")
    print(f"Data Keys: {list(MOCK_DATA.keys())}")
    
    # Store in context storage
    success = context_storage.store_frozen_context(context_id, MOCK_DATA)
    
    if success:
        print("\n✅ Data stored successfully!")
        
        # Verify retrieval
        retrieved = context_storage.get_frozen_context(context_id)
        if retrieved:
            print("\n✅ Data retrieval verified!")
            print(f"   Retrieved keys: {list(retrieved.keys())}")
            
            # Check M2-M6 data
            for module in ["m2", "m3", "m4", "m5", "m6"]:
                module_key = f"{module}_result"
                if module_key in retrieved:
                    summary = retrieved[module_key].get("summary", {})
                    print(f"   ✅ {module.upper()} summary: {len(summary)} fields")
                else:
                    print(f"   ❌ {module.upper()} data missing")
        else:
            print("\n❌ Data retrieval failed!")
    else:
        print("\n❌ Data storage failed!")
    
    print("\n" + "="*60)
    print("Next step: Run test_final_reports.py")
    print("="*60)

if __name__ == "__main__":
    main()
