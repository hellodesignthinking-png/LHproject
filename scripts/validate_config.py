#!/usr/bin/env python3
"""
ZeroSite v7.1 - Configuration Validation Script
Validates environment configuration and API keys
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import get_settings, validate_environment, mask_api_key
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def print_header():
    """Print validation header"""
    print("\n" + "="*60)
    print("  ZeroSite v7.1 - Configuration Validation")
    print("="*60 + "\n")


def print_section(title):
    """Print section title"""
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}\n")


def validate_api_keys(settings):
    """Validate API keys"""
    print_section("🔑 API Keys Validation")
    
    api_status = settings.validate_api_keys()
    
    status_icons = {
        "configured": "✅",
        "missing": "❌",
        "optional": "⚪"
    }
    
    for key_name, status in api_status.items():
        icon = status_icons.get(status, "❓")
        formatted_name = key_name.replace("_", " ").title()
        
        # Get masked key if configured
        if status == "configured":
            if key_name == "kakao":
                key_value = mask_api_key(settings.kakao_rest_api_key)
            elif key_name == "land_regulation":
                key_value = mask_api_key(settings.land_regulation_api_key)
            elif key_name == "mois":
                key_value = mask_api_key(settings.mois_api_key)
            elif key_name == "openai" and settings.openai_api_key:
                key_value = mask_api_key(settings.openai_api_key)
            elif key_name == "google_places" and settings.google_places_api_key:
                key_value = mask_api_key(settings.google_places_api_key)
            elif key_name == "naver" and settings.naver_client_id:
                key_value = mask_api_key(settings.naver_client_id)
            else:
                key_value = "N/A"
                
            print(f"{icon} {formatted_name:25s} {status:12s} ({key_value})")
        else:
            print(f"{icon} {formatted_name:25s} {status:12s}")


def validate_database(settings):
    """Validate database configuration"""
    print_section("💾 Database Configuration")
    
    print(f"✅ Database URL: {settings.database_url[:50]}...")
    print(f"✅ Redis URL: {settings.redis_url}")


def validate_application(settings):
    """Validate application settings"""
    print_section("⚙️  Application Settings")
    
    print(f"✅ Debug Mode: {settings.debug}")
    print(f"✅ Host: {settings.host}")
    print(f"✅ Port: {settings.port}")
    print(f"✅ Log Level: {settings.log_level}")
    print(f"✅ CORS Origins: {len(settings.cors_origins_list)} configured")


def validate_features(settings):
    """Validate feature flags"""
    print_section("🚀 Feature Flags")
    
    enabled_features = settings.get_enabled_features()
    
    all_features = {
        "multi_parcel_analysis": "Multi-Parcel Analysis",
        "geo_optimization": "Geo Optimization",
        "lh_notice_loader": "LH Notice Loader",
        "google_sheets_export": "Google Sheets Export",
        "google_docs_export": "Google Docs Export"
    }
    
    for feature_key, feature_name in all_features.items():
        if feature_key in enabled_features:
            print(f"✅ {feature_name:30s} ENABLED")
        else:
            print(f"⚪ {feature_name:30s} DISABLED")


def validate_security(settings):
    """Validate security settings"""
    print_section("🔐 Security Settings")
    
    # Check if using default secrets
    if settings.session_secret_key and len(settings.session_secret_key) >= 32:
        print(f"✅ Session Secret: Configured ({len(settings.session_secret_key)} chars)")
    else:
        print(f"⚠️  Session Secret: Using default (CHANGE IN PRODUCTION!)")
    
    if settings.jwt_secret_key and len(settings.jwt_secret_key) >= 32:
        print(f"✅ JWT Secret: Configured ({len(settings.jwt_secret_key)} chars)")
    else:
        print(f"⚠️  JWT Secret: Using default (CHANGE IN PRODUCTION!)")
    
    print(f"✅ JWT Algorithm: {settings.jwt_algorithm}")
    print(f"✅ JWT Expiration: {settings.jwt_expiration_minutes} minutes")


def check_environment_file():
    """Check if .env file exists"""
    print_section("📁 Environment File Check")
    
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    env_example_path = os.path.join(os.path.dirname(__file__), '..', '.env.example')
    
    if os.path.exists(env_path):
        print(f"✅ .env file exists: {os.path.abspath(env_path)}")
        
        # Check file permissions (Unix only)
        if os.name != 'nt':  # Not Windows
            import stat
            st = os.stat(env_path)
            mode = stat.filemode(st.st_mode)
            print(f"   Permissions: {mode}")
            
            # Check if too permissive
            if st.st_mode & stat.S_IRWXO or st.st_mode & stat.S_IRWXG:
                print(f"⚠️  WARNING: .env file has group/other permissions!")
                print(f"   Run: chmod 600 .env")
    else:
        print(f"❌ .env file NOT found!")
        if os.path.exists(env_example_path):
            print(f"💡 Copy .env.example to .env and fill in your API keys")
            print(f"   Run: cp .env.example .env")
        return False
    
    if os.path.exists(env_example_path):
        print(f"✅ .env.example exists")
    else:
        print(f"⚠️  .env.example NOT found")
    
    return True


def check_gitignore():
    """Check if .env is in .gitignore"""
    print_section("🔒 Git Security Check")
    
    gitignore_path = os.path.join(os.path.dirname(__file__), '..', '.gitignore')
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
        
        if '.env' in gitignore_content:
            print("✅ .env is in .gitignore")
        else:
            print("❌ .env is NOT in .gitignore!")
            print("💡 Add '.env' to .gitignore immediately!")
            return False
    else:
        print("⚠️  .gitignore file not found")
        return False
    
    return True


def production_readiness_check(settings):
    """Check if configuration is production-ready"""
    print_section("🏭 Production Readiness")
    
    issues = []
    warnings = []
    
    # Check debug mode
    if settings.debug:
        warnings.append("Debug mode is ENABLED (should be False in production)")
    else:
        print("✅ Debug mode: OFF (production-ready)")
    
    # Check API keys
    api_status = settings.validate_api_keys()
    required_keys = ["kakao", "land_regulation", "mois"]
    for key in required_keys:
        if api_status.get(key) != "configured":
            issues.append(f"Required API key missing: {key}")
    
    if not issues:
        print("✅ All required API keys: CONFIGURED")
    
    # Check secrets
    if len(settings.session_secret_key) < 32:
        issues.append("Session secret key too short (min 32 chars)")
    
    if len(settings.jwt_secret_key) < 32:
        issues.append("JWT secret key too short (min 32 chars)")
    
    # Print issues and warnings
    if issues:
        print(f"\n❌ CRITICAL ISSUES ({len(issues)}):")
        for issue in issues:
            print(f"   • {issue}")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"   • {warning}")
    
    if not issues and not warnings:
        print("\n✅ Configuration is PRODUCTION-READY!")
        return True
    elif not issues:
        print("\n⚠️  Configuration has warnings but is usable")
        return True
    else:
        print("\n❌ Configuration has CRITICAL ISSUES - NOT production-ready")
        return False


def main():
    """Main validation function"""
    print_header()
    
    # Check environment file
    if not check_environment_file():
        print("\n❌ Validation FAILED: .env file missing")
        sys.exit(1)
    
    # Check gitignore
    check_gitignore()
    
    try:
        # Load settings
        print_section("📦 Loading Configuration")
        settings = get_settings()
        print("✅ Settings loaded successfully\n")
        
        # Run validation checks
        validate_api_keys(settings)
        validate_database(settings)
        validate_application(settings)
        validate_features(settings)
        validate_security(settings)
        
        # Production readiness
        is_production_ready = production_readiness_check(settings)
        
        # Environment validation
        print_section("🔍 Environment Validation")
        if validate_environment():
            print("✅ Environment validation: PASSED")
        else:
            print("❌ Environment validation: FAILED")
            sys.exit(1)
        
        # Final summary
        print_section("📊 Validation Summary")
        if is_production_ready:
            print("✅ All checks PASSED")
            print("✅ Configuration is VALID and PRODUCTION-READY")
            sys.exit(0)
        else:
            print("⚠️  Some checks FAILED or have WARNINGS")
            print("💡 Review issues above and fix before deployment")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n💡 Common fixes:")
        print("   1. Make sure .env file exists (cp .env.example .env)")
        print("   2. Fill in all required API keys in .env")
        print("   3. Check for typos in key names")
        print("   4. Ensure .env file is readable")
        sys.exit(1)


if __name__ == "__main__":
    main()
