# 🔑 Option 1: Real API Keys Setup - READY TO START

**Date:** 2025-12-17  
**M1 Version:** v2.0  
**Status:** ✅ Documentation Complete, Ready for Configuration

---

## 📊 Current Status

### ✅ What's Complete

| Component | Status | Details |
|-----------|--------|---------|
| **M1 Backend v2.0** | ✅ Running | Port 8000, Unified Data Collection API |
| **M1 Frontend v2.0** | ✅ Running | Port 3001, ReviewScreen Integrated |
| **API Keys Documentation** | ✅ Complete | 4 guides created |
| **Setup Scripts** | ✅ Ready | Interactive configuration tools |
| **Testing Guide** | ✅ Complete | 15+ test cases documented |

### 🔧 Current API Configuration

```bash
# Current .env Status (as of setup):
KAKAO_REST_API_KEY=test_kakao_key_for_development       [MOCK]
VWORLD_API_KEY=your_vworld_api_key_here                 [MOCK]
DATA_GO_KR_API_KEY=your_data_go_kr_api_key_here         [MOCK]
```

**Result:** Backend returns mock data with fallback logic

---

## 🎯 Your Mission: Configure Real API Keys

### Phase 1: Obtain API Keys (15-60 minutes)

#### **🔴 CRITICAL: Kakao REST API Key**
- **Provider:** Kakao Developers (https://developers.kakao.com/)
- **Purpose:** Address search + Geocoding
- **Time to Obtain:** 5-10 minutes
- **Free Tier:** 300,000 calls/day
- **Difficulty:** ⭐ Easy

**Quick Steps:**
1. Sign up at Kakao Developers
2. Create new application
3. Copy REST API key (32 characters)
4. Enable Local API services
5. Register platform domain

📖 **Detailed Guide:** `REAL_API_KEYS_SETUP_GUIDE.md` → Section 1

---

#### **🔴 CRITICAL: VWorld API Key**
- **Provider:** VWorld (http://www.vworld.kr/)
- **Purpose:** Cadastral data + Land use regulations
- **Time to Obtain:** 10-30 minutes (includes approval wait)
- **Free Tier:** 10,000 calls/day
- **Difficulty:** ⭐⭐ Moderate

**Quick Steps:**
1. Register at VWorld
2. Apply for API key
3. Wait for approval (usually instant to 1 day)
4. Activate required services
5. Copy API key (36-40 characters)

📖 **Detailed Guide:** `REAL_API_KEYS_SETUP_GUIDE.md` → Section 2

---

#### **🟡 IMPORTANT: Data.go.kr API Key**
- **Provider:** 공공데이터포털 (https://www.data.go.kr/)
- **Purpose:** Market data + Transaction history
- **Time to Obtain:** 15-30 minutes
- **Free Tier:** Varies by API (usually 1,000/day)
- **Difficulty:** ⭐⭐⭐ Advanced

**Quick Steps:**
1. Register at Data.go.kr
2. Search for "국토교통부 실거래가" APIs
3. Apply for each required API
4. Wait for approval (usually instant)
5. Get unified API key (long encoded string)

📖 **Detailed Guide:** `REAL_API_KEYS_SETUP_GUIDE.md` → Section 3

---

#### **🟢 OPTIONAL: JUSO API Key**
- **Provider:** 행정안전부 (https://www.juso.go.kr/)
- **Purpose:** Alternative address search
- **Time to Obtain:** 1-2 business days
- **Free Tier:** 1,000 calls/day
- **Difficulty:** ⭐⭐ Moderate

**Note:** Not required for M1 v2.0. Kakao API covers address search.

---

### Phase 2: Configure Keys (5 minutes)

#### **Method 1: Interactive Setup Script** ⭐ Recommended

```bash
cd /home/user/webapp

# Run interactive setup
./setup_real_keys.sh
```

**Features:**
- ✅ Guided key entry with validation
- ✅ Automatic .env backup
- ✅ Format validation (key length, format)
- ✅ Backend restart option
- ✅ Automatic health check
- ✅ Initial API test

**Expected Flow:**
```
[STEP 1] Backing up current .env file
✅ Backup created: .env.backup.20251217_152030

[STEP 2] Checking current API key status
Current Keys:
---------------------------------------------------
Kakao REST API:  test_kakao_key_for_development    [MOCK]
VWorld API:      your_vworld_api_key_here          [MOCK]
Data.go.kr API:  your_data_go_kr_api_key_here      [MOCK]
---------------------------------------------------

[STEP 3] API Key Configuration
Do you want to update API keys now? (y/n): y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔑 Kakao REST API Key
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Purpose: Address search & Geocoding (CRITICAL)
Get it from: https://developers.kakao.com/
Current: test_kakao_key_for_development

Enter Kakao REST API Key (or press Enter to skip): [YOUR_KEY_HERE]
✅ Kakao API key updated

[Continue for VWorld and Data.go.kr...]

[STEP 4] Updating .env file
✅ .env file updated successfully

[STEP 5] Updated API Key Status
Updated Keys:
---------------------------------------------------
Kakao REST API:  1234567890abcdef1234567890abcdef  [REAL KEY]
VWorld API:      12345678-ABCD-1234-ABCD-12345678  [REAL KEY]
Data.go.kr API:  veryLongEncodedString%3D%3D       [REAL KEY]
---------------------------------------------------

[STEP 6] Restart Backend Service
Do you want to restart the backend now? (y/n): y
✅ Backend started (PID: 12345)
✅ Backend is healthy!

Health Check Response:
{
    "status": "healthy",
    "module": "M1 Unified Data Collection API",
    "version": "2.0"
}

[STEP 7] Testing API Keys (Optional)
Do you want to test API keys now? (y/n): y
✅ Address search API test PASSED!
```

---

#### **Method 2: Manual Configuration**

```bash
cd /home/user/webapp

# Backup current .env
cp .env .env.backup

# Edit .env file
nano .env

# Update these lines:
KAKAO_REST_API_KEY=your_real_kakao_key_here
VWORLD_API_KEY=your_real_vworld_key_here
DATA_GO_KR_API_KEY=your_real_data_go_kr_key_here

# Save: Ctrl+X, then Y, then Enter

# Restart backend
./restart_backend.sh
```

---

### Phase 3: Test Configuration (10 minutes)

Follow the comprehensive testing guide:

```bash
# Open testing documentation
cat API_TESTING_GUIDE.md

# Quick test sequence:
# Test 1: Address Search
curl -X POST http://localhost:8000/api/m1/address/search \
  -H "Content-Type: application/json" \
  -d '{"query": "서울특별시 강남구 테헤란로 521"}' | python3 -m json.tool

# Test 2: Geocoding
curl -X POST http://localhost:8000/api/m1/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 강남구 테헤란로 521"}' | python3 -m json.tool

# Test 3: Unified Data Collection
curl -X POST http://localhost:8000/api/m1/collect-all \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 테헤란로 521",
    "lat": 37.5084448,
    "lon": 127.0626804
  }' | python3 -m json.tool

# Test 4: Frontend E2E
# Open: https://3001-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai/pipeline
```

📖 **Full Testing Guide:** `API_TESTING_GUIDE.md` (15+ test cases)

---

## 📚 Documentation Reference

| Document | Purpose | Location |
|----------|---------|----------|
| **REAL_API_KEYS_SETUP_GUIDE.md** | How to obtain each API key | `/home/user/webapp/` |
| **API_TESTING_GUIDE.md** | Testing procedures & validation | `/home/user/webapp/` |
| **M1_PHASE2_COMPLETE.md** | Phase 2 completion report | `/home/user/webapp/` |
| **setup_real_keys.sh** | Interactive setup script | `/home/user/webapp/` |
| **restart_backend.sh** | Backend restart script | `/home/user/webapp/` |

---

## 🎯 Success Criteria

You'll know you're successful when:

### ✅ Backend Tests
- [ ] Address search returns 5-10 real suggestions (not 2 mock)
- [ ] Geocoding returns accurate coordinates (not 37.5012, 127.0396)
- [ ] Unified collection has `collection_errors: []`
- [ ] PNU is 19-digit format (not generic "1168010100107090001")
- [ ] Land use zone is specific (e.g., "일반상업지역" not "주거지역")
- [ ] Market prices are realistic (>10,000,000 KRW for Gangnam)

### ✅ Frontend Tests
- [ ] Address autocomplete shows real buildings
- [ ] ReviewScreen displays real data (not mock)
- [ ] API status badges show "✓ Kakao API" (not "⚠ Mock API")
- [ ] All data fields are populated
- [ ] Context freeze completes successfully

### ✅ Data Quality
- [ ] Coordinates match real location on Kakao Map
- [ ] PNU matches government cadastral records
- [ ] Land use zones match urban planning maps
- [ ] Market prices match recent transaction data

---

## 🐛 Common Issues & Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| **401 Unauthorized (Kakao)** | Check key in Kakao console, verify platform domains |
| **Empty suggestions** | Verify API key is active, check quota limits |
| **Mock data still appearing** | Run `./restart_backend.sh` to reload .env |
| **VWorld API timeout** | Check VWorld console for API activation status |
| **Data.go.kr 403 error** | Use "일반 인증키 (Decoding)" not "서비스 인증키" |
| **Backend won't start** | Check `backend.log`: `tail -50 backend.log` |
| **Frontend shows error** | Check browser console (F12) for details |

---

## 🚀 Quick Start Command Summary

```bash
# Navigate to project
cd /home/user/webapp

# 1. Read setup guide
cat REAL_API_KEYS_SETUP_GUIDE.md | less

# 2. Run interactive setup
./setup_real_keys.sh

# 3. Test backend APIs
curl -s http://localhost:8000/api/m1/health | python3 -m json.tool

# 4. Run test suite
# Follow: API_TESTING_GUIDE.md

# 5. Test frontend
# Open: https://3001-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai/pipeline

# 6. Check logs if needed
tail -f backend.log
```

---

## 📊 Expected Results Comparison

### Before (Mock Data) ❌

```json
{
  "success": true,
  "land_bundle": {
    "cadastral": {
      "pnu": "1168010100107090001",
      "address": "서울특별시 강남구 역삼동 123-45",
      "area": 500.0,
      "jimok": "대"
    },
    "legal": {
      "use_zone": "제2종일반주거지역",
      "floor_area_ratio": 200,
      "building_coverage_ratio": 60
    },
    "market": {
      "official_land_price": 50000000
    }
  },
  "collection_errors": []
}
```

**Red Flags:**
- ❌ Generic PNU
- ❌ Round numbers (500.0, 200, 60)
- ❌ Low price (50M for Gangnam)
- ❌ Data source: "Mock API v1.0"

---

### After (Real Keys) ✅

```json
{
  "success": true,
  "land_bundle": {
    "cadastral": {
      "pnu": "1168010400101430000",
      "address": "서울특별시 강남구 삼성동 143",
      "area": 15234.5,
      "jimok": "대"
    },
    "legal": {
      "use_zone": "일반상업지역",
      "floor_area_ratio": 1000,
      "building_coverage_ratio": 60
    },
    "market": {
      "official_land_price": 125000000
    }
  },
  "collection_errors": []
}
```

**Green Flags:**
- ✅ Real 19-digit PNU from VWorld
- ✅ Realistic area (15,234.5 ㎡)
- ✅ Specific use zone (일반상업지역)
- ✅ High FAR (1000% for commercial)
- ✅ Realistic price (125M for Gangnam commercial)
- ✅ Data source: "VWorld Cadastral API v2.0", "Kakao Maps API", etc.

---

## 🎓 Learning Resources

### API Provider Documentation
- **Kakao Developers:** https://developers.kakao.com/docs
- **VWorld:** http://www.vworld.kr/dev/
- **Data.go.kr:** https://www.data.go.kr/support

### API Support
- **Kakao:** https://devtalk.kakao.com/ (Developer Forum)
- **VWorld:** help@vworld.kr
- **Data.go.kr:** 1544-3663 (Korean support line)

---

## 💡 Pro Tips

1. **Start with Kakao key only**  
   Test address search + geocoding first. This covers 60% of M1 functionality.

2. **Test with known addresses**  
   Use famous buildings (파르나스타워, 강남파이낸스센터) to verify accuracy.

3. **Monitor API quotas**  
   Check your usage in each provider's console to avoid hitting limits.

4. **Keep mock keys as backup**  
   Save `.env.backup` in case you need to revert.

5. **Test one API at a time**  
   If something fails, isolate which API by checking `collection_errors`.

6. **Use browser dev tools**  
   F12 → Network tab shows exact API responses from frontend.

---

## 🎯 Next Steps After Setup

Once real keys are configured and tested:

1. **✅ Document findings** - Note any data discrepancies or issues
2. **✅ Test M1 → M2 integration** - Verify M1 data flows to M2 Appraisal
3. **✅ Enhance M1 Lock** - Add mandatory data validation (Option 3)
4. **✅ Test with 10+ real addresses** - Build confidence in data quality
5. **✅ Monitor API usage** - Track quota consumption
6. **✅ Plan for production** - Consider premium tiers if needed

---

## 📞 Support

If you encounter issues during setup:

1. **Check documentation:**  
   - `REAL_API_KEYS_SETUP_GUIDE.md` (API key help)
   - `API_TESTING_GUIDE.md` (Testing help)

2. **Review logs:**
   ```bash
   # Backend logs
   tail -50 backend.log
   
   # Frontend console
   # Open browser F12 → Console
   ```

3. **Test individual APIs:**
   ```bash
   # Kakao test
   curl -H "Authorization: KakaoAK YOUR_KEY" \
     "https://dapi.kakao.com/v2/local/search/address.json?query=강남구"
   
   # VWorld test
   curl "http://api.vworld.kr/req/data?service=data&request=GetFeature&key=YOUR_KEY"
   ```

4. **Contact API providers:**  
   See support links in `REAL_API_KEYS_SETUP_GUIDE.md`

---

## ✅ Checklist for Today

- [ ] Read `REAL_API_KEYS_SETUP_GUIDE.md` (15 min)
- [ ] Sign up for Kakao Developers (5 min)
- [ ] Get Kakao REST API key (5 min)
- [ ] Sign up for VWorld (10 min)
- [ ] Apply for VWorld API key (5 min)
- [ ] Sign up for Data.go.kr (10 min)
- [ ] Activate required Data.go.kr APIs (5 min)
- [ ] Run `./setup_real_keys.sh` (5 min)
- [ ] Test address search (2 min)
- [ ] Test unified collection (3 min)
- [ ] Test frontend E2E (5 min)
- [ ] Document results (10 min)

**Total Time:** ~75 minutes (including API approval wait time)

---

## 🎉 Ready to Start!

**Your mission is clear:**
1. 📖 Read `REAL_API_KEYS_SETUP_GUIDE.md`
2. 🔑 Obtain API keys from each provider
3. 🛠️ Run `./setup_real_keys.sh`
4. 🧪 Follow `API_TESTING_GUIDE.md`
5. ✅ Verify success criteria

**You have everything you need:**
- ✅ Complete documentation (4 guides)
- ✅ Automated setup scripts
- ✅ Comprehensive test suite
- ✅ Troubleshooting guides
- ✅ Working M1 v2.0 system

**Current Services:**
- 🟢 Backend: http://localhost:8000 (Running)
- 🟢 Frontend: https://3001-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai/pipeline (Running)

---

**🚀 Let's get those real API keys configured and see M1 v2.0 shine with production data!**

**Good luck! 화이팅! 🎊**

---

**Last Updated:** 2025-12-17  
**Status:** ✅ Ready to Start  
**Estimated Time:** 75 minutes  
**Success Rate:** High (with good documentation!)
