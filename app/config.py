"""
애플리케이션 설정 관리
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # API Keys
    kakao_rest_api_key: str
    land_regulation_api_key: str
    mois_api_key: str
    openai_api_key: str = ""
    
    # Database
    database_url: str = "sqlite:///./lh_analysis.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Application
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Report Settings
    reports_output_dir: str = "./output/reports"
    max_analysis_workers: int = 4
    
    # API Endpoints
    kakao_api_base_url: str = "https://dapi.kakao.com"
    land_regulation_api_base_url: str = "http://apis.data.go.kr/1613000/LandInfoService"
    mois_api_base_url: str = "http://apis.data.go.kr/1741000/HousePopulationInformationService"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 인스턴스 반환"""
    return Settings()
