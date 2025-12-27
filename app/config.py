"""
ZeroSite v7.1 - Application Configuration
Secure settings management with environment variable loading
"""

import os
import secrets
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    ZeroSite Application Settings
    
    All sensitive configuration is loaded from environment variables (.env file).
    Never hardcode API keys or secrets in this file!
    """
    
    # ============================================
    # API Keys (REQUIRED)
    # ============================================
    
    kakao_rest_api_key: str = Field(..., description="Kakao REST API Key")
    kakao_javascript_key: Optional[str] = Field(default=None, description="Kakao JavaScript API Key (optional)")
    kakao_admin_key: Optional[str] = Field(default=None, description="Kakao Admin API Key (optional)")
    kakao_native_app_key: Optional[str] = Field(default=None, description="Kakao Native App Key (optional)")
    
    land_regulation_api_key: str = Field(..., description="VWorld Land Regulation API Key")
    vworld_api_key: Optional[str] = Field(default=None, description="VWorld API Key (optional, alias for land_regulation_api_key)")
    land_use_regulation_api_key: Optional[str] = Field(default=None, description="Land Use Regulation API Key (optional)")
    building_registry_api_key: Optional[str] = Field(default=None, description="Building Registry API Key (optional)")
    building_register_api_key: Optional[str] = Field(default=None, description="Building Register API Key (optional, alias)")
    
    mois_api_key: str = Field(..., description="MOIS Demographics API Key")
    data_go_kr_api_key: Optional[str] = Field(default=None, description="Data.go.kr API Key (optional, alias for mois_api_key)")
    
    # Optional API Keys
    openai_api_key: Optional[str] = Field(default="", description="OpenAI API Key (optional)")
    google_places_api_key: Optional[str] = Field(default=None, description="Google Places API Key (optional)")
    naver_client_id: Optional[str] = Field(default=None, description="Naver API Client ID (optional)")
    naver_client_secret: Optional[str] = Field(default=None, description="Naver API Client Secret (optional)")
    
    # ============================================
    # Redis Configuration
    # ============================================
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
    
    # ============================================
    # Database Configuration
    # ============================================
    
    database_url: str = Field(default="sqlite:///./zerosite.db", description="Database connection URL")
    
    # ============================================
    # Cache & Session
    # ============================================
    
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    session_secret_key: str = Field(default_factory=lambda: secrets.token_hex(32), description="Session secret key")
    
    # ============================================
    # Application Settings
    # ============================================
    
    debug: bool = Field(default=True, description="Debug mode")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:8000", description="CORS allowed origins")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # ============================================
    # Report Generation
    # ============================================
    
    reports_output_dir: str = Field(default="./output/reports", description="Report output directory")
    max_analysis_workers: int = Field(default=4, description="Max concurrent analysis workers")
    report_watermark: str = Field(default="ZeroSite", description="Report watermark text")
    
    # ============================================
    # Google Services (Optional)
    # ============================================
    
    google_sheets_credentials_path: str = Field(default="./google_credentials.json", description="Google Sheets credentials file")
    google_sheets_spreadsheet_id: str = Field(default="", description="Google Sheets spreadsheet ID")
    google_sheets_worksheet_name: str = Field(default="토지분석기록", description="Google Sheets worksheet name")
    
    google_docs_credentials_path: str = Field(default="./google_credentials.json", description="Google Docs credentials file")
    google_drive_folder_id: str = Field(default="", description="Google Drive folder ID")
    
    # ============================================
    # External API Endpoints
    # ============================================
    
    kakao_api_base_url: str = Field(default="https://dapi.kakao.com", description="Kakao API base URL")
    land_regulation_api_base_url: str = Field(
        default="http://apis.data.go.kr/1613000/LandInfoService",
        description="Land Regulation API base URL"
    )
    mois_api_base_url: str = Field(
        default="http://apis.data.go.kr/1741000/HousePopulationInformationService",
        description="MOIS API base URL"
    )
    
    # ============================================
    # Monitoring & Logging
    # ============================================
    
    log_level: str = Field(default="INFO", description="Logging level")
    log_file_path: str = Field(default="./logs/zerosite.log", description="Log file path")
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    
    # ============================================
    # Rate Limiting
    # ============================================
    
    api_rate_limit: int = Field(default=60, description="API rate limit (requests per minute)")
    
    # ============================================
    # Security Settings
    # ============================================
    
    jwt_secret_key: str = Field(default_factory=lambda: secrets.token_hex(32), description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_minutes: int = Field(default=1440, description="JWT expiration time in minutes (default: 24h)")
    
    # ============================================
    # Feature Flags
    # ============================================
    
    enable_multi_parcel_analysis: bool = Field(default=True, description="Enable multi-parcel analysis")
    enable_geo_optimization: bool = Field(default=True, description="Enable geo optimization")
    enable_lh_notice_loader: bool = Field(default=True, description="Enable LH notice loader")
    enable_google_sheets_export: bool = Field(default=False, description="Enable Google Sheets export")
    enable_google_docs_export: bool = Field(default=False, description="Enable Google Docs export")
    
    # ============================================
    # Performance Tuning
    # ============================================
    
    request_timeout: int = Field(default=30, description="Request timeout in seconds")
    max_upload_size_mb: int = Field(default=10, description="Max upload file size in MB")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    
    # ============================================
    # Validators
    # ============================================
    
    @field_validator('kakao_rest_api_key', 'land_regulation_api_key', 'mois_api_key')
    @classmethod
    def validate_required_api_keys(cls, v, info):
        """Validate required API keys are not placeholder values"""
        if not v or v.startswith('your_') or v.endswith('_here'):
            field_name = info.field_name if hasattr(info, 'field_name') else 'API key'
            raise ValueError(
                f"{field_name} is required! Please set it in your .env file. "
                f"See .env.example for instructions."
            )
        return v
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v):
        """Validate port number"""
        if not 1 <= v <= 65535:
            raise ValueError("port must be between 1 and 65535")
        return v
    
    # ============================================
    # Pydantic Config
    # ============================================
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    # ============================================
    # Helper Methods
    # ============================================
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.debug
    
    def get_google_credentials_path(self, service: str = "sheets") -> str:
        """Get Google service credentials path"""
        if service == "docs":
            return self.google_docs_credentials_path
        return self.google_sheets_credentials_path
    
    def validate_api_keys(self) -> dict:
        """
        Validate all API keys and return status
        
        Returns:
            dict: Status of each API key (configured/missing)
        """
        return {
            "kakao": "configured" if self.kakao_rest_api_key else "missing",
            "land_regulation": "configured" if self.land_regulation_api_key else "missing",
            "mois": "configured" if self.mois_api_key else "missing",
            "openai": "configured" if self.openai_api_key else "optional",
            "google_places": "configured" if self.google_places_api_key else "optional",
            "naver": "configured" if (self.naver_client_id and self.naver_client_secret) else "optional"
        }
    
    def get_enabled_features(self) -> List[str]:
        """Get list of enabled features"""
        features = []
        if self.enable_multi_parcel_analysis:
            features.append("multi_parcel_analysis")
        if self.enable_geo_optimization:
            features.append("geo_optimization")
        if self.enable_lh_notice_loader:
            features.append("lh_notice_loader")
        if self.enable_google_sheets_export:
            features.append("google_sheets_export")
        if self.enable_google_docs_export:
            features.append("google_docs_export")
        return features


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    
    Returns:
        Settings: Application settings singleton
    """
    try:
        settings = Settings()
        logger.info("✅ Settings loaded successfully")
        logger.info(f"🔑 API Keys status: {settings.validate_api_keys()}")
        logger.info(f"🚀 Enabled features: {settings.get_enabled_features()}")
        return settings
    except Exception as e:
        logger.error(f"❌ Failed to load settings: {e}")
        logger.error("💡 Make sure your .env file exists and contains all required values")
        logger.error("💡 Copy .env.example to .env and fill in your API keys")
        raise


def reload_settings():
    """Reload settings (clears cache)"""
    get_settings.cache_clear()
    return get_settings()


# ============================================
# Security Utilities
# ============================================

def mask_api_key(key: str, show_chars: int = 4) -> str:
    """
    Mask API key for safe logging
    
    Args:
        key: API key to mask
        show_chars: Number of characters to show at start and end
        
    Returns:
        str: Masked API key
    """
    if not key or len(key) < show_chars * 2:
        return "****"
    return f"{key[:show_chars]}{'*' * (len(key) - show_chars * 2)}{key[-show_chars:]}"


def validate_environment() -> bool:
    """
    Validate that all required environment variables are set
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        settings = get_settings()
        api_keys_status = settings.validate_api_keys()
        
        # Check required keys
        required_keys = ["kakao", "land_regulation", "mois"]
        missing_keys = [key for key in required_keys if api_keys_status.get(key) == "missing"]
        
        if missing_keys:
            logger.error(f"❌ Missing required API keys: {missing_keys}")
            return False
            
        logger.info("✅ Environment validation passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Environment validation failed: {e}")
        return False
