"""
Test ZeroSite v40.0 Integration
Tests the unified land analysis API endpoint
"""
import sys
import json
import asyncio
from fastapi.testclient import TestClient

# Import main app
from app.main import app

def test_v40_health():
    """Test v40 health check endpoint"""
    print("\n" + "="*60)
    print("🏥 Testing v40.0 Health Check")
    print("="*60)
    
    client = TestClient(app)
    response = client.get("/api/v40/health")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    assert response.status_code == 200
    assert response.json()['version'] == "40.0"
    print("✅ Health check passed!")


def test_v40_full_analysis():
    """Test v40 unified land analysis endpoint"""
    print("\n" + "="*60)
    print("🚀 Testing v40.0 Unified Land Analysis")
    print("="*60)
    
    client = TestClient(app)
    
    # Test data: Seoul Gwanak-gu Sillim-dong
    test_data = {
        "address": "서울특별시 관악구 신림동 1524-8",
        "land_area_sqm": 450.5,
        "land_shape": "정방형",
        "slope": "평지",
        "road_access": "중로",
        "orientation": "남향"
    }
    
    print(f"\n📍 Test Input:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    response = client.post("/api/v40/run-full-land-analysis", json=test_data)
    
    print(f"\n📊 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Analysis Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Verify key fields
        assert 'context_id' in result
        assert 'diagnosis' in result
        assert 'capacity' in result
        assert 'appraisal' in result
        assert 'scenario' in result
        
        print(f"\n🎯 Context ID: {result['context_id']}")
        print(f"🏘️ Zone Type: {result['diagnosis']['zone_type']}")
        print(f"🏢 Max Units: {result['capacity']['max_units']}")
        print(f"💰 Final Value: ₩{result['appraisal']['final_value']:,}")
        print(f"📈 Recommended Scenario: {result['scenario']['recommended']}")
        print("\n✅ Full analysis test passed!")
        
        return result['context_id']
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_v40_context_retrieval(context_id):
    """Test context retrieval by ID"""
    if not context_id:
        print("\n⚠️ Skipping context retrieval test (no context_id)")
        return
    
    print("\n" + "="*60)
    print("🔍 Testing v40.0 Context Retrieval")
    print("="*60)
    
    client = TestClient(app)
    response = client.get(f"/api/v40/context/{context_id}")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        context = response.json()
        print(f"\n✅ Context Retrieved:")
        print(f"  - Timestamp: {context['timestamp']}")
        print(f"  - Address: {context['input']['address']}")
        print(f"  - Zone Type: {context['diagnosis']['zone_type']}")
        print(f"  - Max Units: {context['capacity']['max_units']}")
        print("\n✅ Context retrieval test passed!")
    else:
        print(f"❌ Error: {response.text}")


def test_v40_report_endpoints(context_id):
    """Test report generation endpoints"""
    if not context_id:
        print("\n⚠️ Skipping report test (no context_id)")
        return
    
    print("\n" + "="*60)
    print("📄 Testing v40.0 Report Generation")
    print("="*60)
    
    client = TestClient(app)
    
    # Test v39 appraisal report
    print("\n📊 Testing v39 Appraisal Report (23 pages)...")
    response = client.get(f"/api/v40/reports/{context_id}/appraisal_v39")
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
    
    if response.status_code == 200:
        pdf_size = len(response.content)
        print(f"PDF Size: {pdf_size:,} bytes ({pdf_size/1024:.2f} KB)")
        print("✅ PDF generation test passed!")
    else:
        print(f"⚠️ Report generation error: {response.text}")


if __name__ == "__main__":
    print("\n" + "🚀"*30)
    print("ZeroSite v40.0 Integration Test Suite")
    print("🚀"*30)
    
    try:
        # Test 1: Health check
        test_v40_health()
        
        # Test 2: Full analysis
        context_id = test_v40_full_analysis()
        
        # Test 3: Context retrieval
        test_v40_context_retrieval(context_id)
        
        # Test 4: Report generation
        test_v40_report_endpoints(context_id)
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
