"""
ZeroSite API 키 통합 관리
"""

import os
from typing import Dict

class APIKeys:
    """
    모든 API 키를 중앙 관리
    """
    
    # 국토부 실거래가 API (12개 엔드포인트 공통 키)
    MOLIT_API_KEY = "5158584967f97600a71afc331e848ad6c8154524d2266a6ad62c22c5f5c9ad87"
    
    # 카카오 API (4개 키 전체)
    KAKAO_NATIVE_APP_KEY = "5ae18f5c9a1f273ade8f272a2d85f88a"
    KAKAO_REST_API_KEY = "1b172a21a17b8b51dd47884b45228483"
    KAKAO_JAVASCRIPT_KEY = "d38aa214f1396aa4222d3f8972ef6092"
    KAKAO_ADMIN_KEY = "6ff4cfada4e33ec48b782f78858f0c39"
    
    # 토지이용규제정보서비스 (NDSI)
    NDSI_API_KEY = "702ee13807d"
    
    # 행안부 공공데이터
    MOIS_API_KEY = "702ee13807d"
    
    # 소상공인시장진흥공단
    SEMAS_API_KEY = "5158584967f97600a71afc331e848ad6c8154524d2266a6ad62c22c5f5c9ad87"
    
    @classmethod
    def get_molit_key(cls) -> str:
        """국토부 API 키 반환"""
        return os.getenv("MOLIT_API_KEY", cls.MOLIT_API_KEY)
    
    @classmethod
    def get_kakao_key(cls, key_type: str = "rest") -> str:
        """카카오 API 키 반환
        
        Args:
            key_type: 'native', 'rest', 'javascript', 'admin' (기본값: 'rest')
        """
        key_map = {
            'native': cls.KAKAO_NATIVE_APP_KEY,
            'rest': cls.KAKAO_REST_API_KEY,
            'javascript': cls.KAKAO_JAVASCRIPT_KEY,
            'admin': cls.KAKAO_ADMIN_KEY
        }
        return os.getenv(f"KAKAO_{key_type.upper()}_API_KEY", key_map.get(key_type, cls.KAKAO_REST_API_KEY))
    
    @classmethod
    def get_kakao_rest_key(cls) -> str:
        """카카오 REST API 키 반환 (별칭 메서드)"""
        return cls.get_kakao_key('rest')
    
    @classmethod
    def validate_keys(cls) -> Dict[str, bool]:
        """모든 API 키 유효성 검사"""
        return {
            'molit': bool(cls.MOLIT_API_KEY and len(cls.MOLIT_API_KEY) > 20),
            'kakao': bool(cls.KAKAO_REST_API_KEY and len(cls.KAKAO_REST_API_KEY) > 20),
            'ndsi': bool(cls.NDSI_API_KEY),
            'mois': bool(cls.MOIS_API_KEY),
            'semas': bool(cls.SEMAS_API_KEY)
        }

# 즉시 검증
if __name__ == "__main__":
    validation = APIKeys.validate_keys()
    print("🔑 API 키 검증 결과:")
    for api, valid in validation.items():
        status = "✅" if valid else "❌"
        print(f"   {status} {api.upper()}: {'유효' if valid else '무효'}")
