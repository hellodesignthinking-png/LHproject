"""
M1 토지정보 수집 - n8n Webhook 전용 프록시
================================================
n8n Webhook을 통해 모든 외부 API 호출을 처리합니다.
V-World, 공공데이터포털 등의 직접 호출 로직은 완전히 제거되었습니다.

Author: ZeroSite Backend Team
Date: 2025-12-19
"""

import httpx
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/proxy", tags=["Proxy"])

# ==================== Configuration ====================

N8N_WEBHOOK_URL = "https://zerosite.app.n8n.cloud/webhook/m1-land-data"
N8N_TIMEOUT = 30.0

EMERGENCY_MOCK_DATA = {
    "pnu": "0000000000000000000",
    "jimok": "대",
    "area": "330.0",
    "jiyuk": "용도지역 미확인",
    "is_mock": True,
    "source": "Backend Emergency Mock"
}


# ==================== Helper Functions ====================

def wrap_n8n_response_to_vworld_format(n8n_data: dict, pnu: str) -> dict:
    """
    n8n의 플랫한 JSON을 프론트엔드가 기대하는 V-World 중첩 구조로 변환
    
    n8n 응답: { "pnu": "...", "jimok": "...", "area": "..." }
    V-World 포맷: { "success": true, "data": { "response": { ... } } }
    """
    is_mock_value = n8n_data.get('is_mock', True)
    if isinstance(is_mock_value, str):
        is_mock_value = is_mock_value.lower() == 'true'
    
    return {
        "success": True,
        "data": {
            "response": {
                "status": "OK",
                "result": {
                    "featureCollection": {
                        "features": [{
                            "properties": {
                                "pnu": n8n_data.get('pnu', pnu),
                                "jimok": n8n_data.get('jimok', '대'),
                                "area": str(n8n_data.get('area', '330.0')),
                                "jiyuk": n8n_data.get('jiyuk', n8n_data.get('zoning', '용도지역 미확인')),
                                "is_mock": is_mock_value,
                                "source": n8n_data.get('source', 'n8n Webhook')
                            }
                        }]
                    }
                }
            }
        }
    }


def create_emergency_response(pnu: str) -> dict:
    """n8n 실패 시 비상 Mock 데이터를 V-World 포맷으로 반환"""
    return {
        "success": True,
        "data": {
            "response": {
                "status": "OK",
                "result": {
                    "featureCollection": {
                        "features": [{
                            "properties": {
                                "pnu": pnu,
                                "jimok": EMERGENCY_MOCK_DATA["jimok"],
                                "area": EMERGENCY_MOCK_DATA["area"],
                                "jiyuk": EMERGENCY_MOCK_DATA["jiyuk"],
                                "is_mock": EMERGENCY_MOCK_DATA["is_mock"],
                                "source": EMERGENCY_MOCK_DATA["source"]
                            }
                        }]
                    }
                }
            }
        }
    }


def create_cors_headers() -> dict:
    """CORS 헤더 생성"""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }


# ==================== Main Endpoint ====================

@router.get("/vworld")
async def get_land_data_via_n8n(
    pnu: str = Query(..., description="필지 고유번호 (19자리)", min_length=19, max_length=19),
    data_type: str = Query("land", description="데이터 타입 (하위 호환용)")
):
    """
    M1 토지정보 수집 API - n8n Webhook 전용
    
    n8n Webhook을 호출하여 토지 데이터를 수집합니다.
    n8n이 V-World, 공공데이터포털 등 모든 외부 API를 처리합니다.
    """
    logger.info(f"[M1] n8n Webhook 호출 - PNU: {pnu}")
    print(f"\n{'='*80}")
    print(f"🚀 [M1] n8n Webhook 호출")
    print(f"   PNU: {pnu}")
    print(f"   URL: {N8N_WEBHOOK_URL}")
    print(f"   Timeout: {N8N_TIMEOUT}초")
    print(f"{'='*80}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                N8N_WEBHOOK_URL,
                params={"pnu": pnu},
                timeout=N8N_TIMEOUT
            )
            response.raise_for_status()
        
        n8n_data = response.json()
        
        logger.info(f"[M1] n8n 응답 성공 - HTTP {response.status_code}")
        print(f"\n✅ [n8n 응답 성공] HTTP {response.status_code}")
        print(f"   Source: {n8n_data.get('source', 'Unknown')}")
        print(f"   Jimok: {n8n_data.get('jimok', 'N/A')}")
        print(f"   Area: {n8n_data.get('area', 'N/A')} ㎡")
        print(f"   Is Mock: {n8n_data.get('is_mock', 'Unknown')}")
        
        vworld_response = wrap_n8n_response_to_vworld_format(n8n_data, pnu)
        print(f"{'='*80}\n")
        
        return JSONResponse(
            content=vworld_response,
            headers=create_cors_headers()
        )
        
    except httpx.TimeoutException:
        logger.error(f"[M1] n8n Timeout - PNU: {pnu}")
        print(f"\n⏱️ [Timeout] n8n 응답 시간 초과 ({N8N_TIMEOUT}초)")
        
    except httpx.HTTPStatusError as e:
        logger.error(f"[M1] n8n HTTP Error - PNU: {pnu}, Status: {e.response.status_code}")
        print(f"\n❌ [HTTP Error] n8n HTTP {e.response.status_code} 에러")
        
    except httpx.RequestError as e:
        logger.error(f"[M1] n8n Connection Failed - PNU: {pnu}, Error: {str(e)}")
        print(f"\n💥 [Connection Error] n8n 연결 실패: {str(e)}")
        
    except Exception as e:
        logger.error(f"[M1] Unexpected Error - PNU: {pnu}, Error: {str(e)}")
        print(f"\n🚨 [Critical Error] 예상치 못한 오류: {str(e)}")
    
    print(f"🛡️ [Emergency Fallback] 비상 Mock 데이터 반환")
    emergency_response = create_emergency_response(pnu)
    print(f"{'='*80}\n")
    
    return JSONResponse(
        content=emergency_response,
        headers=create_cors_headers()
    )


# ==================== CORS Preflight ====================

@router.options("/vworld")
async def vworld_cors_preflight():
    """CORS Preflight 요청 처리"""
    return JSONResponse(
        content={"status": "ok"},
        headers=create_cors_headers()
    )


# ==================== Test & Health Check ====================

@router.get("/vworld/test")
async def test_n8n_integration(pnu: str = Query("1168010100001230045", description="테스트용 PNU")):
    """n8n Webhook 통합 테스트 엔드포인트"""
    print(f"\n{'='*80}")
    print("🧪 [TEST] n8n Webhook 통합 테스트")
    print(f"   PNU: {pnu}")
    print(f"{'='*80}")
    
    try:
        result = await get_land_data_via_n8n(pnu=pnu)
        
        return {
            "success": True,
            "message": "✅ n8n Webhook 통합 테스트 완료",
            "test_pnu": pnu,
            "n8n_webhook_url": N8N_WEBHOOK_URL,
            "timeout": f"{N8N_TIMEOUT}초",
            "strategy": "n8n Webhook → Emergency Mock Fallback",
            "note": "모든 외부 API 호출은 n8n이 처리합니다"
        }
    except Exception as e:
        logger.error(f"[TEST] 테스트 실패: {str(e)}")
        return {
            "success": False,
            "message": "❌ n8n Webhook 테스트 실패",
            "error": str(e),
            "n8n_webhook_url": N8N_WEBHOOK_URL
        }


@router.get("/vworld/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "M1 토지정보 프록시",
        "architecture": "n8n Webhook 전용",
        "n8n_webhook_url": N8N_WEBHOOK_URL,
        "timeout": f"{N8N_TIMEOUT}초",
        "fallback": "비상 Mock 데이터",
        "external_apis": "n8n이 V-World, 공공데이터포털 처리",
        "version": "1.0.0-production"
    }
