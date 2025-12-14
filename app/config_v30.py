"""
ZeroSite v30.0 - Configuration & API Keys
Complete API Integration for Real National Data
"""
import os
from dotenv import load_dotenv

load_dotenv()

class ConfigV30:
    """v30.0 Configuration with all API keys"""
    
    # Kakao API
    KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", "1b172a21a17b8b51dd47884b45228483")
    KAKAO_ADMIN_KEY = os.getenv("KAKAO_ADMIN_KEY", "6ff4cfada4e33ec48b782f78858f0c39")
    
    # V-World API
    VWORLD_API_KEY = os.getenv("VWORLD_API_KEY", "B6B0B6F1-E572-304A-9742-384510D86FE4")
    
    # Data.go.kr API (MOLIT)
    DATA_GO_KR_API_KEY = os.getenv("DATA_GO_KR_API_KEY", "702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d")
    MOIS_API_KEY = os.getenv("MOIS_API_KEY", "702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d")
    
    # API Endpoints
    KAKAO_GEOCODE_URL = "https://dapi.kakao.com/v2/local/search/address.json"
    VWORLD_ADDRESS_URL = "https://api.vworld.kr/req/address"
    VWORLD_ZONING_URL = "https://api.vworld.kr/req/data"
    VWORLD_LANDPRICE_URL = "https://api.vworld.kr/req/data"
    MOLIT_TRANSACTION_URL = "https://apis.data.go.kr/1613000/RTMSDataSvcLandTrade/getRTMSDataSvcLandTrade"
    
    # Feature Flags
    USE_REAL_API = True  # Enable real API calls
    USE_FALLBACK_ON_ERROR = True  # Use fallback if API fails
    
    # Timeouts
    API_TIMEOUT = 10  # seconds
    
    DEBUG = os.getenv("DEBUG", "True") == "True"

config_v30 = ConfigV30()
