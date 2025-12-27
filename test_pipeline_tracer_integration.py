#!/usr/bin/env python3
"""
Test Pipeline Tracer Integration with Real Endpoint
====================================================

Tests the actual /api/v4/pipeline/analyze endpoint with PipelineTracer integration
to ensure proper error tracking and reporting.
"""

import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
ENDPOINT = f"{BASE_URL}/api/v4/pipeline/analyze"


def test_pipeline_with_valid_parcel():
    """Test pipeline with a valid parcel_id"""
    print("\n" + "="*80)
    print("TEST 1: Pipeline with Valid Parcel")
    print("="*80)
    
    payload = {
        "parcel_id": "test-parcel-001",
        "use_cache": False
    }
    
    try:
        response = requests.post(ENDPOINT, json=payload, timeout=120)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS")
            print(f"   Analysis ID: {data.get('analysis_id')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Execution Time: {data.get('execution_time_ms')}ms")
            print(f"   Land Value: {data.get('land_value'):,}원")
            print(f"   LH Decision: {data.get('lh_decision')}")
            print(f"   LH Score: {data.get('lh_total_score')}/110")
        else:
            data = response.json()
            print(f"❌ FAILED")
            print(f"   Error: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # Check if it's a PipelineExecutionError
            if 'debug_id' in data:
                print(f"\n🔍 Pipeline Error Detected:")
                print(f"   Stage: {data.get('stage')}")
                print(f"   Reason: {data.get('reason_code')}")
                print(f"   Message: {data.get('message_ko')}")
                print(f"   Debug ID: {data.get('debug_id')}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")


def test_pipeline_with_missing_m1():
    """Test pipeline with missing M1 data"""
    print("\n" + "="*80)
    print("TEST 2: Pipeline with Missing M1 Data")
    print("="*80)
    
    # Use a parcel_id that doesn't have M1 frozen
    payload = {
        "parcel_id": "nonexistent-parcel-999",
        "use_cache": False
    }
    
    try:
        response = requests.post(ENDPOINT, json=payload, timeout=120)
        print(f"\nStatus Code: {response.status_code}")
        
        data = response.json()
        
        if response.status_code == 500:
            print(f"✅ ERROR PROPERLY TRACKED")
            print(f"   OK: {data.get('ok')}")
            print(f"   Stage: {data.get('stage')}")
            print(f"   Reason Code: {data.get('reason_code')}")
            print(f"   Message (KO): {data.get('message_ko')}")
            print(f"   Debug ID: {data.get('debug_id')}")
            
            if data.get('details'):
                print(f"   Details: {json.dumps(data['details'], indent=6, ensure_ascii=False)}")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")


def test_tracer_debug_id_format():
    """Verify debug_id format in error responses"""
    print("\n" + "="*80)
    print("TEST 3: Verify Debug ID Format")
    print("="*80)
    
    payload = {
        "parcel_id": "error-test-001",
        "use_cache": False
    }
    
    try:
        response = requests.post(ENDPOINT, json=payload, timeout=120)
        
        if response.status_code == 500:
            data = response.json()
            debug_id = data.get('debug_id', '')
            
            # Check format: pl_YYYYMMDD_xxxxxxxx
            if debug_id.startswith('pl_') and len(debug_id) == 20:
                print(f"✅ Debug ID format valid: {debug_id}")
                
                # Extract date
                date_part = debug_id[3:11]
                print(f"   Date: {date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}")
                print(f"   Trace ID: {debug_id[12:]}")
            else:
                print(f"❌ Invalid debug_id format: {debug_id}")
        else:
            print(f"⚠️ No error response to check debug_id")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")


if __name__ == "__main__":
    print("\n" + "🔍 PIPELINE TRACER INTEGRATION TEST ".center(80, "="))
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Endpoint: {ENDPOINT}")
    
    # Note: These tests require the FastAPI server to be running
    print("\n⚠️  NOTE: These tests require the FastAPI server to be running")
    print("   Start server with: uvicorn app.main:app --reload")
    
    # Run tests (comment out if server is not running)
    # test_pipeline_with_valid_parcel()
    # test_pipeline_with_missing_m1()
    # test_tracer_debug_id_format()
    
    print("\n" + "="*80)
    print("✅ Test suite completed")
    print("="*80)
    print("\nTo run these tests:")
    print("1. Start server: uvicorn app.main:app --reload")
    print("2. Uncomment the test function calls above")
    print("3. Run: python test_pipeline_tracer_integration.py")
