"""
ZeroSite v30.0 - API Keys Configuration
Real National API Integration

API Keys Required:
1. V-World API Key (국가공간정보포털)
2. Public Data Portal API Key (공공데이터포털)
3. Kakao REST API Key (카카오)

Author: ZeroSite Development Team
Date: 2024-12-14
Version: 30.0.0
"""

import os
from typing import Optional

class APIKeysV30:
    """
    v30.0 API Keys Manager
    
    환경변수 또는 직접 설정으로 API 키 관리
    """
    
    # V-World (국가공간정보포털)
    VWORLD_API_KEY: str = os.getenv(
        "VWORLD_API_KEY",
        ""  # TODO: 실제 키 입력
    )
    
    # 공공데이터포털 (RTMS 실거래가)
    PUBLIC_DATA_API_KEY: str = os.getenv(
        "PUBLIC_DATA_API_KEY", 
        ""  # TODO: 실제 키 입력
    )
    
    # 카카오 REST API
    KAKAO_REST_API_KEY: str = os.getenv(
        "KAKAO_REST_API_KEY",
        ""  # TODO: 실제 키 입력
    )
    
    @classmethod
    def validate_keys(cls) -> dict:
        """
        API 키 유효성 검증
        
        Returns:
            dict: 각 API 키의 설정 여부
        """
        return {
            "vworld": bool(cls.VWORLD_API_KEY),
            "public_data": bool(cls.PUBLIC_DATA_API_KEY),
            "kakao": bool(cls.KAKAO_REST_API_KEY),
            "all_ready": all([
                cls.VWORLD_API_KEY,
                cls.PUBLIC_DATA_API_KEY,
                cls.KAKAO_REST_API_KEY
            ])
        }
    
    @classmethod
    def get_api_status(cls) -> dict:
        """API 키 상태 확인"""
        validation = cls.validate_keys()
        return {
            "version": "30.0.0",
            "api_keys": {
                "vworld": "✓ Configured" if validation["vworld"] else "✗ Missing",
                "public_data": "✓ Configured" if validation["public_data"] else "✗ Missing",
                "kakao": "✓ Configured" if validation["kakao"] else "✗ Missing"
            },
            "ready_for_production": validation["all_ready"],
            "fallback_mode": not validation["all_ready"]
        }


# API Endpoints
class APIEndpoints:
    """v30.0 Real API Endpoints"""
    
    # V-World APIs
    VWORLD_GEOCODING = "https://api.vworld.kr/req/address"
    VWORLD_ZONING = "https://api.vworld.kr/req/data"
    VWORLD_LANDPRICE = "https://api.vworld.kr/req/data"
    
    # 공공데이터포털
    RTMS_LAND_TRADE = "https://apis.data.go.kr/1613000/RTMSDataSvcLandTrade/getRTMSDataSvcLandTrade"
    
    # 카카오
    KAKAO_ADDRESS_SEARCH = "https://dapi.kakao.com/v2/local/search/address.json"
    KAKAO_COORD_TO_ADDRESS = "https://dapi.kakao.com/v2/local/geo/coord2address.json"


# Test
if __name__ == "__main__":
    import json
    
    print("=" * 80)
    print("ZeroSite v30.0 - API Keys Status")
    print("=" * 80)
    
    status = APIKeysV30.get_api_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    if not status["ready_for_production"]:
        print("\n⚠️  WARNING: API keys not configured!")
        print("   System will use FALLBACK mode")
        print("\nTo configure API keys:")
        print("1. Get V-World API key from https://www.vworld.kr")
        print("2. Get Public Data Portal key from https://www.data.go.kr")
        print("3. Get Kakao API key from https://developers.kakao.com")
        print("\nThen set in app/api_keys_v30.py or environment variables")
    else:
        print("\n✓ All API keys configured - Ready for production!")
