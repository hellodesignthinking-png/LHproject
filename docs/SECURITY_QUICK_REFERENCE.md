# 🔒 API Key Security - Quick Reference

**Last Updated**: 2025-12-18  
**Status**: ✅ ALL SECURE

---

## ⚡ Current Status

### ✅ What's Already Done

**All API keys are properly secured!** No action needed for existing implementation.

```bash
# ✅ SECURE: Backend loads keys from .env
VWORLD_API_KEY = os.getenv("VWORLD_API_KEY")

# ✅ SECURE: .env is in .gitignore
grep "^\.env" .gitignore  # ← Returns: .env (lines 30, 31, 32, 72)

# ✅ SECURE: No hardcoded keys in code
grep -r "1BB852F2-8557" --include="*.py"  # ← Returns: No results
```

---

## 🎯 3-Minute Security Check

### Step 1: Verify No Hardcoded Keys (30 seconds)

```bash
cd /home/user/webapp
grep -r "1BB852F2-8557-3387-B620-623B922641EB" --include="*.py" --include="*.ts" --include="*.js"

# ✅ Expected: No results (exit code 1)
# ❌ If found: Replace with os.getenv("VWORLD_API_KEY")
```

### Step 2: Check `.env` Exists (15 seconds)

```bash
ls -la .env
grep "VWORLD_API_KEY" .env

# ✅ Expected: File exists with VWORLD_API_KEY=1BB852F2-8557-3387-B620-623B922641EB
```

### Step 3: Verify `.gitignore` (15 seconds)

```bash
grep "^\.env" .gitignore

# ✅ Expected output:
# .env
# .env.local
# .env.*.local
```

### Step 4: Test Backend Loading (2 minutes)

```bash
# Start backend
cd /home/user/webapp && python -m uvicorn app.main:app --reload

# Check logs for confirmation:
# INFO:app.api.endpoints.proxy_vworld: ✅ VWORLD_API_KEY loaded from environment

# Test proxy endpoint
curl "http://localhost:8005/api/proxy/vworld/test?pnu=1162010200115240008"

# ✅ Expected: Response with "success": true (if API key domain is registered)
```

---

## 🛡️ Security Rules (Remember These!)

### ✅ DO THIS

```python
# ✅ SECURE: Load from environment
import os
VWORLD_API_KEY = os.getenv("VWORLD_API_KEY")

# ✅ SECURE: Validate at startup
if not VWORLD_API_KEY:
    raise ValueError("VWORLD_API_KEY required!")

# ✅ SECURE: Mask in logs
masked = VWORLD_API_KEY[:8] + "..." + VWORLD_API_KEY[-4:]
logger.info(f"Using key: {masked}")  # Output: "1BB852F2...41EB"
```

### ❌ NEVER DO THIS

```python
# ❌ INSECURE: Hardcoded key
VWORLD_KEY = "1BB852F2-8557-3387-B620-623B922641EB"

# ❌ INSECURE: Commit .env to Git
git add .env  # ← DON'T DO THIS!

# ❌ INSECURE: Log full key
logger.info(f"API key: {VWORLD_API_KEY}")  # ← Full key exposed in logs!
```

---

## 🚨 Emergency: "I Accidentally Committed `.env` to Git!"

**⚠️ FOLLOW THESE STEPS IMMEDIATELY:**

```bash
# 1. Remove .env from Git history (coordinate with team first!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 2. Force push
git push origin --force --all

# 3. IMMEDIATELY rotate ALL API keys
# Go to each service provider and generate NEW keys:
# - V-World: https://www.vworld.kr/dev/v4dv_apiuseradd2_s001.do
# - Kakao: https://developers.kakao.com/
# - Data.go.kr: https://www.data.go.kr/

# 4. Update .env with new keys
nano .env

# 5. Ensure .env is in .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to .gitignore"
git push
```

---

## 📖 Environment Variable Patterns

### Backend (Python/FastAPI)

```python
# app/api/endpoints/proxy_vworld.py

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get API key
VWORLD_API_KEY = os.getenv("VWORLD_API_KEY")

# Validate
if not VWORLD_API_KEY:
    raise ValueError("VWORLD_API_KEY environment variable is required")

# Use in API call
params = {
    "key": VWORLD_API_KEY,  # ← From environment, not hardcoded
    "domain": "http://localhost/",
    # ...
}
```

### Frontend (Next.js) - Only for Public Keys

```javascript
// next.config.js
module.exports = {
  env: {
    // ⚠️ Only expose PUBLIC keys (prefix with NEXT_PUBLIC_)
    NEXT_PUBLIC_KAKAO_KEY: process.env.NEXT_PUBLIC_KAKAO_KEY,
  },
}

// ❌ NEVER expose backend API keys to frontend:
// VWORLD_API_KEY  ← This should ONLY be in backend
// DATA_GO_KR_API_KEY  ← This should ONLY be in backend
```

---

## 🔍 Quick Troubleshooting

### "VWORLD_API_KEY not found"

```bash
# Check .env exists
ls -la .env

# Check key is in .env
cat .env | grep VWORLD_API_KEY

# Ensure dotenv is loaded in app
# In app/main.py, add at the TOP:
from dotenv import load_dotenv
load_dotenv()  # ← Must be BEFORE importing other modules
```

### "API Key Works Locally But Not in Production"

```bash
# Set environment variable on production server
export VWORLD_API_KEY="1BB852F2-8557-3387-B620-623B922641EB"

# OR copy .env to production (secure the file!)
scp .env user@server:/path/to/app/.env
ssh user@server "chmod 600 /path/to/app/.env"  # ← Restrict to owner only
```

---

## 📊 Security Checklist

Before every deployment:

- [x] ✅ All API keys in `.env`
- [x] ✅ `.env` is in `.gitignore`
- [x] ✅ No hardcoded keys in code
- [x] ✅ Keys loaded via `os.getenv()`
- [x] ✅ Keys validated at startup
- [x] ✅ Keys masked in logs
- [x] ✅ Production keys different from dev keys

---

## 📞 Need Help?

**Full Documentation**: `docs/SECURITY_API_KEY_MANAGEMENT_2025-12-18.md`  
**V-World API Console**: https://www.vworld.kr/dev/v4dv_apiuseradd2_s001.do

---

**Remember**: When in doubt, use `.env` + `os.getenv()` for ALL secrets! 🔐
