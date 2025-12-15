"""
ZeroSite v37.0 ULTIMATE - API Keys Configuration
중앙 집중식 API 키 관리

Author: Antenna Holdings Development Team
Date: 2025-12-13
Purpose: Centralized API key management for all external services
"""

class APIKeys:
    """모든 API 키 중앙 관리"""
    
    # ========================================
    # 카카오 API
    # ========================================
    KAKAO_REST_API_KEY = "1b172a21a17b8b51dd47884b45228483"
    KAKAO_JAVASCRIPT_KEY = "d38aa214f1396aa4222d3f8972ef6092"
    KAKAO_ADMIN_KEY = "6ff4cfada4e33ec48b782f78858f0c39"
    KAKAO_NATIVE_APP_KEY = "5ae18f5c9a1f273ade8f272a2d85f88a"
    
    # ========================================
    # 국토교통부 / 행정안전부 공통 키
    # ========================================
    MOLIT_API_KEY = "702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d"
    
    # ========================================
    # V-World
    # ========================================
    VWORLD_API_KEY = "B6B0B6F1-E572-304A-9742-384510D86FE4"
    
    @classmethod
    def get_kakao_headers(cls):
        """카카오 REST API 헤더"""
        return {
            "Authorization": f"KakaoAK {cls.KAKAO_REST_API_KEY}"
        }
    
    @classmethod
    def get_all_keys(cls):
        """모든 키 반환 (디버깅용)"""
        return {
            "kakao_rest": cls.KAKAO_REST_API_KEY[:20] + "...",
            "kakao_js": cls.KAKAO_JAVASCRIPT_KEY[:20] + "...",
            "molit": cls.MOLIT_API_KEY[:20] + "...",
            "vworld": cls.VWORLD_API_KEY[:20] + "..."
        }


# Singleton instance
_api_keys = APIKeys()


def get_api_keys() -> APIKeys:
    """API 키 싱글톤 반환"""
    return _api_keys


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ZeroSite v37.0 API Keys Configuration")
    print("=" * 60)
    
    keys = APIKeys()
    
    print("\n✅ Configured API Keys:")
    for name, key in keys.get_all_keys().items():
        print(f"  {name}: {key}")
    
    print("\n✅ Kakao Headers:")
    print(f"  {keys.get_kakao_headers()}")
    
    print("\n" + "=" * 60)
    print("Configuration Complete")
    print("=" * 60)
