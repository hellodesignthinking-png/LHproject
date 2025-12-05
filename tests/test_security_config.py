"""
ZeroSite v7.1 - Security Configuration Tests
Test API key security, environment validation, and configuration management
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from app.config import (
    Settings,
    get_settings,
    reload_settings,
    mask_api_key,
    validate_environment
)


class TestSettings:
    """Test Settings class"""
    
    def test_settings_requires_api_keys(self):
        """Test that API keys are required"""
        with pytest.raises(ValidationError):
            Settings(
                kakao_rest_api_key="",  # Empty key should fail
                land_regulation_api_key="valid_key",
                mois_api_key="valid_key"
            )
    
    def test_settings_rejects_placeholder_keys(self):
        """Test that placeholder keys are rejected"""
        with pytest.raises(ValidationError):
            Settings(
                kakao_rest_api_key="your_kakao_api_key_here",  # Placeholder
                land_regulation_api_key="valid_key",
                mois_api_key="valid_key"
            )
    
    def test_settings_accepts_valid_keys(self):
        """Test that valid keys are accepted"""
        settings = Settings(
            kakao_rest_api_key="1b172a21a17b8b51dd47884b45228483",
            land_regulation_api_key="702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d",
            mois_api_key="702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d"
        )
        assert settings.kakao_rest_api_key is not None
    
    def test_optional_keys_can_be_empty(self):
        """Test that optional keys can be empty"""
        settings = Settings(
            kakao_rest_api_key="valid_key_12345678901234567890",
            land_regulation_api_key="valid_key_12345678901234567890",
            mois_api_key="valid_key_12345678901234567890",
            openai_api_key=""  # Optional
        )
        assert settings.openai_api_key == ""
    
    def test_log_level_validation(self):
        """Test log level validation"""
        settings = Settings(
            kakao_rest_api_key="valid_key_12345678901234567890",
            land_regulation_api_key="valid_key_12345678901234567890",
            mois_api_key="valid_key_12345678901234567890",
            log_level="DEBUG"
        )
        assert settings.log_level == "DEBUG"
        
        with pytest.raises(ValidationError):
            Settings(
                kakao_rest_api_key="valid_key_12345678901234567890",
                land_regulation_api_key="valid_key_12345678901234567890",
                mois_api_key="valid_key_12345678901234567890",
                log_level="INVALID"
            )
    
    def test_port_validation(self):
        """Test port number validation"""
        # Valid port
        settings = Settings(
            kakao_rest_api_key="valid_key_12345678901234567890",
            land_regulation_api_key="valid_key_12345678901234567890",
            mois_api_key="valid_key_12345678901234567890",
            port=8000
        )
        assert settings.port == 8000
        
        # Invalid port
        with pytest.raises(ValidationError):
            Settings(
                kakao_rest_api_key="valid_key_12345678901234567890",
                land_regulation_api_key="valid_key_12345678901234567890",
                mois_api_key="valid_key_12345678901234567890",
                port=70000  # Out of range
            )


class TestSettingsMethods:
    """Test Settings helper methods"""
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings for testing"""
        return Settings(
            kakao_rest_api_key="test_kakao_key_1234567890",
            land_regulation_api_key="test_vworld_key_1234567890",
            mois_api_key="test_mois_key_1234567890",
            openai_api_key="sk-test_openai_key",
            google_places_api_key="AIza_test_google_key_12345678901234",
            debug=False
        )
    
    def test_is_production(self, mock_settings):
        """Test production mode detection"""
        assert mock_settings.is_production() is True
        
        mock_settings.debug = True
        assert mock_settings.is_production() is False
    
    def test_validate_api_keys(self, mock_settings):
        """Test API key validation"""
        status = mock_settings.validate_api_keys()
        
        assert status["kakao"] == "configured"
        assert status["land_regulation"] == "configured"
        assert status["mois"] == "configured"
        assert status["openai"] == "configured"
        assert status["google_places"] == "configured"
    
    def test_get_enabled_features(self, mock_settings):
        """Test enabled features retrieval"""
        mock_settings.enable_multi_parcel_analysis = True
        mock_settings.enable_geo_optimization = True
        mock_settings.enable_lh_notice_loader = False
        
        features = mock_settings.get_enabled_features()
        
        assert "multi_parcel_analysis" in features
        assert "geo_optimization" in features
        assert "lh_notice_loader" not in features
    
    def test_cors_origins_list(self, mock_settings):
        """Test CORS origins parsing"""
        mock_settings.cors_origins = "http://localhost:3000,https://example.com,http://localhost:8000"
        
        origins = mock_settings.cors_origins_list
        
        assert len(origins) == 3
        assert "http://localhost:3000" in origins
        assert "https://example.com" in origins


class TestSecurityUtilities:
    """Test security utility functions"""
    
    def test_mask_api_key(self):
        """Test API key masking"""
        # Normal key
        key = "1b172a21a17b8b51dd47884b45228483"
        masked = mask_api_key(key, show_chars=4)
        assert masked == "1b17************************8483"
        
        # Short key
        short_key = "short"
        masked_short = mask_api_key(short_key)
        assert masked_short == "****"
        
        # Empty key
        empty_key = ""
        masked_empty = mask_api_key(empty_key)
        assert masked_empty == "****"
    
    def test_mask_api_key_different_show_chars(self):
        """Test API key masking with different show_chars"""
        key = "1b172a21a17b8b51dd47884b45228483"
        
        # Show 2 chars
        masked_2 = mask_api_key(key, show_chars=2)
        assert masked_2 == "1b****************************83"
        
        # Show 6 chars
        masked_6 = mask_api_key(key, show_chars=6)
        assert masked_6 == "1b172a********************228483"


class TestEnvironmentValidation:
    """Test environment validation"""
    
    @patch('app.config.get_settings')
    def test_validate_environment_success(self, mock_get_settings):
        """Test successful environment validation"""
        # Mock settings with all required keys
        mock_settings = MagicMock()
        mock_settings.validate_api_keys.return_value = {
            "kakao": "configured",
            "land_regulation": "configured",
            "mois": "configured"
        }
        mock_get_settings.return_value = mock_settings
        
        assert validate_environment() is True
    
    @patch('app.config.get_settings')
    def test_validate_environment_missing_keys(self, mock_get_settings):
        """Test environment validation with missing keys"""
        # Mock settings with missing required keys
        mock_settings = MagicMock()
        mock_settings.validate_api_keys.return_value = {
            "kakao": "missing",  # Missing key
            "land_regulation": "configured",
            "mois": "configured"
        }
        mock_get_settings.return_value = mock_settings
        
        assert validate_environment() is False
    
    @patch('app.config.get_settings')
    def test_validate_environment_exception(self, mock_get_settings):
        """Test environment validation with exception"""
        mock_get_settings.side_effect = Exception("Settings load failed")
        
        assert validate_environment() is False


class TestSettingsCaching:
    """Test settings caching"""
    
    def test_get_settings_is_cached(self):
        """Test that get_settings returns cached instance"""
        settings1 = get_settings()
        settings2 = get_settings()
        
        # Should return same instance
        assert settings1 is settings2
    
    def test_reload_settings_clears_cache(self):
        """Test that reload_settings clears cache"""
        settings1 = get_settings()
        
        # Reload should clear cache
        settings2 = reload_settings()
        
        # Should be different instances
        assert settings1 is not settings2


class TestFeatureFlags:
    """Test feature flags"""
    
    @pytest.fixture
    def settings_with_features(self):
        """Create settings with specific feature flags"""
        return Settings(
            kakao_rest_api_key="test_key_12345678901234567890",
            land_regulation_api_key="test_key_12345678901234567890",
            mois_api_key="test_key_12345678901234567890",
            enable_multi_parcel_analysis=True,
            enable_geo_optimization=False,
            enable_lh_notice_loader=True,
            enable_google_sheets_export=False,
            enable_google_docs_export=False
        )
    
    def test_feature_flags_properly_set(self, settings_with_features):
        """Test that feature flags are properly set"""
        assert settings_with_features.enable_multi_parcel_analysis is True
        assert settings_with_features.enable_geo_optimization is False
        assert settings_with_features.enable_lh_notice_loader is True
        assert settings_with_features.enable_google_sheets_export is False
    
    def test_get_enabled_features_returns_correct_list(self, settings_with_features):
        """Test that get_enabled_features returns correct list"""
        features = settings_with_features.get_enabled_features()
        
        assert "multi_parcel_analysis" in features
        assert "lh_notice_loader" in features
        assert "geo_optimization" not in features
        assert "google_sheets_export" not in features
        assert len(features) == 2


class TestDefaultValues:
    """Test default configuration values"""
    
    def test_default_values(self):
        """Test default values are set correctly"""
        settings = Settings(
            kakao_rest_api_key="test_key_12345678901234567890",
            land_regulation_api_key="test_key_12345678901234567890",
            mois_api_key="test_key_12345678901234567890"
        )
        
        # Application defaults
        assert settings.debug is True
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        
        # Database defaults
        assert settings.database_url == "sqlite:///./lh_analysis.db"
        assert settings.redis_url == "redis://localhost:6379/0"
        
        # Report defaults
        assert settings.reports_output_dir == "./output/reports"
        assert settings.max_analysis_workers == 4
        assert settings.report_watermark == "ZeroSite"
        
        # Security defaults
        assert settings.jwt_algorithm == "HS256"
        assert settings.jwt_expiration_minutes == 1440
        
        # Performance defaults
        assert settings.request_timeout == 30
        assert settings.cache_ttl == 3600


@pytest.mark.integration
class TestIntegrationWithEnvFile:
    """Integration tests with actual .env file"""
    
    def test_load_from_env_file(self, tmp_path):
        """Test loading settings from .env file"""
        # Create temporary .env file
        env_content = """
KAKAO_REST_API_KEY=test_kakao_key_1234567890
LAND_REGULATION_API_KEY=test_vworld_key_1234567890
MOIS_API_KEY=test_mois_key_1234567890
DEBUG=False
PORT=9000
        """
        
        env_file = tmp_path / ".env"
        env_file.write_text(env_content.strip())
        
        # Load settings with custom env_file
        with patch('app.config.Settings.Config.env_file', str(env_file)):
            settings = Settings(_env_file=str(env_file))
            
            assert settings.kakao_rest_api_key == "test_kakao_key_1234567890"
            assert settings.debug is False
            assert settings.port == 9000


# Test summary fixture
@pytest.fixture(scope="module", autouse=True)
def test_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("  ZeroSite v7.1 - Security Configuration Tests")
    print("="*60)
    yield
    print("\n" + "="*60)
    print("  Security tests completed")
    print("="*60 + "\n")
