# ZeroSite v7.1 - Security Setup Guide

**Status**: 🔐 **PRODUCTION-READY SECURITY**  
**Last Updated**: 2024-12-01  
**Task**: API Key Security Hardening (Task 1)

---

## 🎯 Overview

This guide covers the complete security setup for ZeroSite v7.1, including:
- API key management
- Environment variable configuration
- Git-secrets integration
- Key rotation procedures
- Security best practices

---

## 📋 Prerequisites

Before starting, ensure you have:
- [ ] Python 3.8+ installed
- [ ] Git installed
- [ ] Access to required API keys (Kakao, VWorld, MOIS)
- [ ] Text editor (VS Code, Vim, etc.)

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Copy Environment Template
```bash
cd /home/user/webapp
cp .env.example .env
```

### Step 2: Edit .env File
```bash
nano .env  # or use your preferred editor
```

### Step 3: Fill in Required API Keys
```bash
KAKAO_REST_API_KEY=your_actual_kakao_key
LAND_REGULATION_API_KEY=your_actual_vworld_key
MOIS_API_KEY=your_actual_mois_key
```

### Step 4: Verify Configuration
```bash
python -c "from app.config import get_settings; settings = get_settings(); print('✅ Configuration valid!')"
```

---

## 🔑 API Key Registration Guide

### 1. Kakao REST API Key

**Purpose**: Address geocoding, POI search, local business data

**Registration**:
1. Visit [Kakao Developers](https://developers.kakao.com/)
2. Sign up / Log in
3. Create new application
4. Go to "Settings" → "General"
5. Copy "REST API Key"
6. Add to `.env` as `KAKAO_REST_API_KEY`

**Platforms**: Kakao Local API, Kakao Map API

---

### 2. VWorld Land Regulation API Key

**Purpose**: Land use regulations, zoning information, building restrictions

**Registration**:
1. Visit [VWorld](https://www.vworld.kr/)
2. Sign up / Log in
3. Go to "Open API" → "Manage Keys"
4. Request new API key
5. Select "Land Information Service"
6. Wait for approval (usually instant)
7. Copy API key
8. Add to `.env` as `LAND_REGULATION_API_KEY`

**Platforms**: VWorld Open API

---

### 3. MOIS API Key (Ministry of Interior and Safety)

**Purpose**: Demographics, population statistics, household data

**Registration**:
1. Visit [공공데이터포털](https://www.data.go.kr/)
2. Sign up / Log in
3. Search for "주택인구통계" (House Population Statistics)
4. Click "활용신청" (Request Usage)
5. Fill in application form
6. Wait for approval (usually 1-2 hours)
7. Check email for API key
8. Add to `.env` as `MOIS_API_KEY`

**Platforms**: 공공데이터포털 (Public Data Portal)

---

### 4. Optional API Keys

#### Google Places API (Fallback POI)
```bash
GOOGLE_PLACES_API_KEY=your_google_key
```
Register at: https://console.cloud.google.com/

#### Naver API (Fallback POI)
```bash
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret
```
Register at: https://developers.naver.com/

#### OpenAI API (AI Features)
```bash
OPENAI_API_KEY=sk-your_openai_key
```
Register at: https://platform.openai.com/

---

## 🔐 Git-Secrets Setup

### Installation

#### macOS (Homebrew)
```bash
brew install git-secrets
```

#### Ubuntu/Debian
```bash
sudo apt-get install git-secrets
```

#### Manual Installation
```bash
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets
sudo make install
```

### Configuration

```bash
# Navigate to project root
cd /home/user/webapp

# Install git-secrets hooks
git secrets --install

# Register AWS patterns (built-in)
git secrets --register-aws

# Add custom patterns from .gitsecrets file
git secrets --add-provider -- cat .gitsecrets

# Scan entire repository
git secrets --scan

# Scan commits
git secrets --scan-history
```

### Pre-commit Hook

Git-secrets will automatically scan commits before they're pushed:

```bash
# This will now be checked automatically
git add .
git commit -m "feat: add new feature"
# If API keys are detected, commit will be rejected!
```

---

## 🔄 API Key Rotation Procedure

### When to Rotate Keys
- Every 90 days (recommended)
- Immediately if key is compromised
- After team member departure
- After security incident

### Rotation Steps

#### 1. Generate New Keys
Register new API keys following the guides above.

#### 2. Update .env File
```bash
# Backup old .env
cp .env .env.backup

# Update keys in .env
nano .env
```

#### 3. Test Configuration
```bash
# Verify new keys work
python -c "from app.config import reload_settings; reload_settings()"

# Run integration tests
pytest tests/integration/
```

#### 4. Update Production
```bash
# Update production environment variables
# (specific steps depend on your deployment platform)

# For Docker:
docker-compose down
docker-compose up -d

# For systemd:
sudo systemctl restart zerosite
```

#### 5. Revoke Old Keys
- Kakao: Go to application settings → Deactivate key
- VWorld: Go to key management → Delete key
- MOIS: Contact support to revoke

---

## 🛡️ Security Best Practices

### DO's ✅

1. **Always use .env files**
   - Never hardcode API keys in source code
   - Use `.env` for local development
   - Use platform-specific secrets for production

2. **Keep .env secure**
   ```bash
   chmod 600 .env  # Only owner can read/write
   ```

3. **Use different keys for different environments**
   - Development: Test keys with limited quotas
   - Staging: Separate keys from production
   - Production: High-quota, monitored keys

4. **Monitor API usage**
   - Set up alerts for unusual activity
   - Review usage logs weekly
   - Track quota consumption

5. **Backup configuration**
   ```bash
   # Securely backup .env (encrypted)
   gpg -c .env  # Creates .env.gpg
   ```

### DON'Ts ❌

1. **Never commit .env to Git**
   ```bash
   # Verify .env is in .gitignore
   grep ".env" .gitignore
   ```

2. **Never share API keys via**
   - Email
   - Slack/Discord
   - Screenshots
   - Code comments

3. **Never use production keys in development**
   - Use separate test keys
   - Limit test key quotas

4. **Never log API keys**
   ```python
   # Bad
   logger.info(f"Using API key: {api_key}")
   
   # Good
   logger.info(f"Using API key: {mask_api_key(api_key)}")
   ```

---

## 🔍 Security Verification Checklist

### Pre-Production Checklist

- [ ] All API keys moved to .env
- [ ] .env.example has no real keys
- [ ] .env is in .gitignore
- [ ] git-secrets is installed and configured
- [ ] Repository scanned for secrets (`git secrets --scan-history`)
- [ ] API key validators pass
- [ ] Environment validation passes
- [ ] Different keys for dev/staging/prod
- [ ] API usage monitoring enabled
- [ ] Key rotation schedule created
- [ ] Team trained on security procedures

### Automated Security Checks

Run these commands before deployment:

```bash
# 1. Check for hardcoded secrets
python scripts/check_secrets.py

# 2. Scan git history
git secrets --scan-history

# 3. Verify environment
python -c "from app.config import validate_environment; validate_environment()"

# 4. Run security tests
pytest tests/security/

# 5. Check file permissions
ls -la .env
# Should show: -rw------- (600)
```

---

## 🚨 Incident Response

### If API Key is Compromised

#### Immediate Actions (Within 5 Minutes)

1. **Revoke compromised key**
   - Kakao: Deactivate immediately
   - VWorld: Delete key
   - MOIS: Contact support

2. **Generate new key**
   - Follow registration guides above
   - Use different key if possible

3. **Update all environments**
   ```bash
   # Update .env
   nano .env
   
   # Restart services
   sudo systemctl restart zerosite
   ```

4. **Notify team**
   - Send alert to all developers
   - Document incident
   - Review access logs

#### Post-Incident Review (Within 24 Hours)

1. **Identify source of compromise**
   - Review git history
   - Check logs
   - Audit team access

2. **Implement preventive measures**
   - Update git-secrets patterns
   - Enhance monitoring
   - Additional training

3. **Document incident**
   - Root cause analysis
   - Timeline of events
   - Lessons learned

---

## 📊 Configuration Validation

### Automatic Validation

The application automatically validates configuration on startup:

```python
from app.config import get_settings, validate_environment

# Get settings (validates automatically)
settings = get_settings()

# Check API key status
api_status = settings.validate_api_keys()
print(api_status)
# {'kakao': 'configured', 'land_regulation': 'configured', ...}

# Validate entire environment
is_valid = validate_environment()
print(f"Environment valid: {is_valid}")
```

### Manual Validation

```bash
# Run validation script
python scripts/validate_config.py

# Expected output:
# ✅ Settings loaded successfully
# ✅ Kakao API key: configured
# ✅ Land Regulation API key: configured
# ✅ MOIS API key: configured
# ✅ Environment validation passed
```

---

## 🔧 Troubleshooting

### Issue: "kakao_rest_api_key is required"

**Cause**: API key not set in .env or using placeholder value

**Solution**:
```bash
# Check .env file
cat .env | grep KAKAO_REST_API_KEY

# Should NOT be:
KAKAO_REST_API_KEY=your_kakao_api_key_here  # ❌

# Should be:
KAKAO_REST_API_KEY=1b172a21a17b8b51dd47884b45228483  # ✅ (example)
```

### Issue: "git secrets --scan fails"

**Cause**: Secrets detected in codebase

**Solution**:
```bash
# Find problematic files
git secrets --scan

# Remove secrets from files
# Then re-scan
git secrets --scan
```

### Issue: ".env file not found"

**Cause**: .env not created from .env.example

**Solution**:
```bash
cp .env.example .env
nano .env  # Add your keys
```

---

## 📚 Additional Resources

### Documentation
- [Kakao Developers Guide](https://developers.kakao.com/docs)
- [VWorld API Documentation](https://www.vworld.kr/dev/v4dv_2ddataguide2_s001.do)
- [공공데이터포털 Guide](https://www.data.go.kr/ugs/selectPublicDataUseGuideView.do)

### Security Tools
- [git-secrets](https://github.com/awslabs/git-secrets)
- [trufflehog](https://github.com/trufflesecurity/trufflehog)
- [detect-secrets](https://github.com/Yelp/detect-secrets)

### Best Practices
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [12-Factor App - Config](https://12factor.net/config)

---

## 📞 Support

### Security Issues
- **Report to**: security@zerosite.com (if applicable)
- **Response Time**: Within 24 hours
- **Severity Levels**: Critical, High, Medium, Low

### Configuration Help
- **Documentation**: This file (SECURITY_SETUP.md)
- **Validation Script**: `python scripts/validate_config.py`
- **Community**: GitHub Issues

---

**Last Updated**: 2024-12-01  
**Version**: 7.1.0  
**Status**: ✅ Production-Ready  
**Security Level**: 🔐 Enterprise-Grade
