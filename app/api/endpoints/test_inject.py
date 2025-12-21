"""
Test Endpoint for Final Reports
DEV/TEST ONLY - Direct context injection for testing
"""

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, Any

from app.services.context_storage import context_storage

router = APIRouter(prefix="/api/test", tags=["Testing"])


@router.post("/inject-context")
async def inject_test_context(
    context_id: str,
    context_data: Dict[str, Any] = Body(...)
):
    """
    DEV/TEST ONLY: Inject test context data directly into storage
    
    This bypasses the normal M1 analysis flow and allows testing final reports
    with mock data.
    
    Example:
    ```json
    {
        "context_id": "test-001",
        "m2_result": {...},
        "m3_result": {...},
        ...
    }
    ```
    """
    try:
        # Add metadata
        context_data["_test_injected"] = True
        context_data["_injected_at"] = datetime.now().isoformat()
        context_data["context_id"] = context_id
        
        # Store in context storage
        success = context_storage.store_frozen_context(context_id, context_data)
        
        if success:
            # Verify retrieval
            retrieved = context_storage.get_frozen_context(context_id)
            return JSONResponse({
                "status": "success",
                "context_id": context_id,
                "stored_keys": list(context_data.keys()),
                "retrieved": retrieved is not None,
                "message": "✅ Test context injected successfully"
            })
        else:
            return JSONResponse({
                "status": "error",
                "context_id": context_id,
                "message": "❌ Failed to store context"
            }, status_code=500)
            
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "context_id": context_id,
            "error": str(e),
            "message": "❌ Exception during context injection"
        }, status_code=500)


@router.post("/inject-mock-canonical")
async def inject_mock_canonical():
    """
    DEV/TEST ONLY: Inject complete mock canonical M2-M6 data
    
    Returns context_id for use in testing final reports
    """
    context_id = f"test-mock-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    mock_data = {
        "context_id": context_id,
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
    
    success = context_storage.store_frozen_context(context_id, mock_data)
    
    if success:
        return JSONResponse({
            "status": "success",
            "context_id": context_id,
            "message": "✅ Mock canonical data injected successfully",
            "test_urls": {
                "all_in_one": f"/api/v4/reports/final/all_in_one/html?context_id={context_id}",
                "landowner_summary": f"/api/v4/reports/final/landowner_summary/html?context_id={context_id}",
                "lh_technical": f"/api/v4/reports/final/lh_technical/html?context_id={context_id}",
                "financial_feasibility": f"/api/v4/reports/final/financial_feasibility/html?context_id={context_id}",
                "quick_check": f"/api/v4/reports/final/quick_check/html?context_id={context_id}",
                "presentation": f"/api/v4/reports/final/presentation/html?context_id={context_id}"
            }
        })
    else:
        return JSONResponse({
            "status": "error",
            "message": "❌ Failed to store mock data"
        }, status_code=500)
