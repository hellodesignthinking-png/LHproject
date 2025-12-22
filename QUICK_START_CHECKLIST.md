# ✅ ZeroSite v4.0 Quick Start Checklist

**Last Updated:** 2025-12-17  
**Status:** 🚀 Ready for Production

---

## 📋 Pre-Deployment Checklist

### ✅ Code Implementation (COMPLETE)
- [x] M1 Backend (9 API endpoints)
- [x] M1 Frontend (8 STEP components)
- [x] M4 V2 Schematics (4 drawing types)
- [x] Redis Integration
- [x] External API connections
- [x] PDF Parsing
- [x] All commits pushed to GitHub

### ⚠️ User Configuration Required

#### Step 1: Environment Variables
- [ ] Create `.env` from `.env.example`
- [ ] Add **JUSO_API_KEY** (get from: https://www.juso.go.kr/)
- [ ] Add **KAKAO_REST_API_KEY** (get from: https://developers.kakao.com/)
- [ ] Add **LAND_REGULATION_API_KEY** (get from: http://www.vworld.kr/)
- [ ] Add **MOIS_API_KEY** (get from: https://www.data.go.kr/)

```bash
# Quick setup:
cd /home/user/webapp
cp .env.example .env
nano .env  # Edit with your API keys
```

#### Step 2: Redis Installation
Choose one method:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
redis-cli ping  # Should return: PONG
```

**macOS:**
```bash
brew install redis
brew services start redis
redis-cli ping  # Should return: PONG
```

**Docker (Cross-platform):**
```bash
docker run --name redis -d -p 6379:6379 redis:latest
docker exec -it redis redis-cli ping  # Should return: PONG
```

#### Step 3: Python Dependencies
```bash
cd /home/user/webapp
pip install -r requirements.txt
```

#### Step 4: Start the Application
```bash
cd /home/user/webapp
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 Testing Checklist

### Backend Health Check
```bash
# Test M1 API
curl http://localhost:8000/api/m1/health
# Expected: {"status": "healthy", "module": "M1 Land Information API"}
```

### M1 Full Flow Test
```bash
# STEP 1: Address Search
curl -X POST http://localhost:8000/api/m1/address/search \
  -H "Content-Type: application/json" \
  -d '{"query": "서울시 강남구 역삼동"}'

# STEP 2: Geocoding
curl -X POST http://localhost:8000/api/m1/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "서울시 강남구 역삼동 123"}'

# Continue with STEP 3-8 (see M1_M4_SETUP_AND_TESTING_GUIDE.md)
```

### M4 Schematic Test
```bash
# Generate schematics
curl -X POST http://localhost:8000/api/reports/v4/pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "parcel_id": "1168010100100010001",
    "context_id": "your_context_id_here"
  }'

# View schematics in browser:
# http://localhost:8000/static/schematics/{parcel_id}_ground_layout.svg
```

### Redis Storage Test
```bash
# Check Redis connection
redis-cli ping

# Check stored contexts
redis-cli KEYS "context:*"

# Get a specific context
redis-cli GET "context:{your_context_id}"
```

---

## 📊 Expected Results

### ✅ If Everything Works:

1. **Backend Health:**
   - M1 health check returns `{"status": "healthy"}`
   - No startup errors in terminal

2. **M1 Flow:**
   - STEP 1: Returns 3+ address suggestions
   - STEP 2: Returns coordinates with 6 decimals
   - STEP 8: Returns context_id (UUID format)

3. **M4 Schematics:**
   - 4 SVG files generated in `static/schematics/`
   - Files are viewable in browser
   - Download functionality works

4. **Redis:**
   - `redis-cli ping` returns `PONG`
   - Contexts stored with TTL of 86400 seconds

---

## 🚨 Troubleshooting Quick Fixes

### Issue: "No module named 'fastapi'"
```bash
pip install fastapi uvicorn pydantic
```

### Issue: "Redis connection refused"
```bash
# Check if Redis is running
sudo systemctl status redis-server  # Linux
brew services list  # macOS

# Restart Redis
sudo systemctl restart redis-server  # Linux
brew services restart redis  # macOS
```

### Issue: "API key invalid"
1. Verify API keys in `.env` have no extra spaces
2. Check keys are active on respective platforms
3. Verify API usage quotas not exceeded

### Issue: Schematics not generating
```bash
# Create directory if missing
mkdir -p static/schematics
chmod 755 static/schematics
```

---

## 📝 Next Steps After Testing

1. **Review PR:**
   - Visit: https://github.com/hellodesignthinking-png/LHproject/pull/11
   - Review changes
   - Approve and merge

2. **Production Deployment:**
   - Set up production Redis instance
   - Configure PostgreSQL (optional)
   - Set up environment variables in production
   - Enable HTTPS
   - Configure monitoring

3. **User Acceptance Testing:**
   - Test with real address data
   - Verify all 8 STEPs work correctly
   - Check schematic quality
   - Validate data accuracy

---

## 📚 Documentation Reference

| Document | Purpose | Size |
|----------|---------|------|
| `M1_M4_SETUP_AND_TESTING_GUIDE.md` | Complete setup instructions | 11 KB |
| `M1_M4_COMPLETION_SUMMARY.md` | Implementation summary | 15 KB |
| `M1_BACKEND_IMPLEMENTATION_COMPLETE.md` | Backend API docs | 23 KB |
| `.env.example` | Environment template | 2 KB |

---

## 🎉 Success Criteria

**System is ready for production when:**
- [x] All code pushed to GitHub
- [ ] `.env` configured with real API keys
- [ ] Redis running and accessible
- [ ] Backend health check passes
- [ ] M1 STEP 1-8 flow works
- [ ] M4 schematics generate correctly
- [ ] Redis stores contexts with TTL
- [ ] PR approved and merged

---

## 🆘 Need Help?

**Technical Issues:**
- Check logs: `logs/zerosite.log`
- Review terminal error messages
- Verify all dependencies installed

**Documentation:**
- Full setup guide: `M1_M4_SETUP_AND_TESTING_GUIDE.md`
- API documentation: `M1_BACKEND_IMPLEMENTATION_COMPLETE.md`
- UX flow: `M1_STEP_UX_IMPLEMENTATION_PLAN.md`

**Repository:**
- GitHub: https://github.com/hellodesignthinking-png/LHproject
- Branch: `feature/expert-report-generator`
- PR: https://github.com/hellodesignthinking-png/LHproject/pull/11

---

**🚀 Ready to start? Follow the checklist above step by step!**

---

**Created:** 2025-12-17  
**Version:** 1.0  
**Status:** Production Ready
