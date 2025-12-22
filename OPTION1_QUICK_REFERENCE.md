# 🚀 Option 1: Real API Keys - Quick Reference Card

**Last Updated:** 2025-12-17  
**Status:** ✅ Ready to Execute  
**Estimated Time:** 75 minutes

---

## 📋 One-Page Cheat Sheet

### 🎯 Goal
Configure real Korean land information API keys for M1 v2.0 production testing.

### 📚 Documentation Files (Start Here)

| Order | File | Size | Read Time | Purpose |
|-------|------|------|-----------|---------|
| **1** | `OPTION1_REAL_API_KEYS_READY.md` | 15 KB | 10 min | **START HERE** - Execution plan |
| **2** | `REAL_API_KEYS_SETUP_GUIDE.md` | 15 KB | 15 min | API key registration guides |
| **3** | `API_TESTING_GUIDE.md` | 17 KB | 10 min | Testing procedures |
| **4** | `OPTION1_COMPLETE_SUMMARY.md` | 20 KB | 10 min | Achievement report |

---

## 🔑 API Keys You Need

| API | Provider | Free Tier | Time | Priority |
|-----|----------|-----------|------|----------|
| **Kakao REST API** | https://developers.kakao.com/ | 300K/day | 10 min | 🔴 CRITICAL |
| **VWorld API** | http://www.vworld.kr/ | 10K/day | 30 min | 🔴 CRITICAL |
| **Data.go.kr API** | https://www.data.go.kr/ | 1K/day | 30 min | 🟡 Important |
| **JUSO API** | https://www.juso.go.kr/ | 1K/day | 1-2 days | 🟢 Optional |

---

## ⚡ Quick Start (5 Commands)

```bash
# 1. Navigate to project
cd /home/user/webapp

# 2. Read execution plan (10 min)
cat OPTION1_REAL_API_KEYS_READY.md

# 3. After obtaining API keys, run setup (5 min)
./setup_real_keys.sh

# 4. Test backend (2 min)
curl -X POST http://localhost:8000/api/m1/address/search \
  -H "Content-Type: application/json" \
  -d '{"query": "서울특별시 강남구 테헤란로 521"}' | python3 -m json.tool

# 5. Test frontend (3 min)
# Open: https://3001-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai/pipeline
```

---

## 📊 Current System Status

```bash
# Backend Health
curl -s http://localhost:8000/api/m1/health | python3 -m json.tool

# Expected Output:
{
  "status": "healthy",
  "module": "M1 Unified Data Collection API",
  "version": "2.0",
  "endpoints": 10
}
```

**Service URLs:**
- 🟢 Backend: http://localhost:8000
- 🟢 Frontend: https://3001-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai/pipeline

---

## 🛠️ Essential Commands

### Setup
```bash
./setup_real_keys.sh          # Interactive setup with validation
nano .env                      # Manual edit (alternative)
./restart_backend.sh           # Restart after .env changes
```

### Testing
```bash
# Test 1: Address Search
curl -X POST http://localhost:8000/api/m1/address/search \
  -H "Content-Type: application/json" \
  -d '{"query": "서울특별시 강남구 테헤란로 521"}' | python3 -m json.tool

# Test 2: Geocoding
curl -X POST http://localhost:8000/api/m1/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 강남구 테헤란로 521"}' | python3 -m json.tool

# Test 3: Unified Collection
curl -X POST http://localhost:8000/api/m1/collect-all \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 강남구 테헤란로 521", "lat": 37.5084, "lon": 127.0627}' \
  | python3 -m json.tool
```

### Debugging
```bash
tail -f backend.log            # Backend logs
cat .env | grep API_KEY        # Check current keys
lsof -ti:8000                  # Check backend PID
```

---

## ✅ Success Checklist (Use This!)

### After Setup
- [ ] `setup_real_keys.sh` completed without errors
- [ ] `.env.backup` file created (timestamp)
- [ ] Backend restarted successfully
- [ ] Health check returns `"status": "healthy"`

### After Testing
- [ ] Address search returns 5-10 suggestions (not 2)
- [ ] No mock building names ("테스트빌딩")
- [ ] Coordinates are accurate (not 37.5012, 127.0396)
- [ ] PNU is 19 digits (not generic "1168010100107090001")
- [ ] Use zone is specific (e.g., "일반상업지역")
- [ ] `collection_errors: []` (empty array)
- [ ] API badges show real APIs (not "Mock API v1.0")

### Data Quality
- [ ] Coordinates match Kakao Map
- [ ] Market prices are realistic (>10M for Gangnam)
- [ ] All data fields populated
- [ ] Context freeze completes successfully

---

## 🚨 Common Issues (Quick Fixes)

| Issue | Quick Fix |
|-------|-----------|
| **401 Unauthorized** | Check key at provider console → Verify platform domains |
| **Empty suggestions** | Check API quota → Verify key is active |
| **Mock data persists** | `./restart_backend.sh` → Clear cache |
| **Backend won't start** | `tail -50 backend.log` → Check error messages |
| **Frontend error** | F12 → Console → Check API call details |

---

## 📖 Key Sections in Documentation

### REAL_API_KEYS_SETUP_GUIDE.md
- **Section 1:** Kakao REST API registration (Page 1)
- **Section 2:** VWorld API registration (Page 5)
- **Section 3:** Data.go.kr API registration (Page 8)
- **Testing Commands:** Page 10-12

### API_TESTING_GUIDE.md
- **Test 1:** Address Search (Page 1)
- **Test 2:** Geocoding (Page 3)
- **Test 3:** Unified Collection (Page 5)
- **Test 4:** Frontend E2E (Page 9)
- **Validation Criteria:** Page 6-8

### OPTION1_REAL_API_KEYS_READY.md
- **Quick Start:** Page 1
- **Phase 1:** Obtain Keys (Page 2)
- **Phase 2:** Configure Keys (Page 5)
- **Phase 3:** Test (Page 6)
- **Success Criteria:** Page 8

---

## 🎯 75-Minute Timeline

```
00:00 - 00:10  Read OPTION1_REAL_API_KEYS_READY.md
00:10 - 00:20  Sign up Kakao Developers, get key
00:20 - 00:30  Sign up VWorld, apply for key
00:30 - 00:45  Sign up Data.go.kr, activate APIs
00:45 - 00:50  Run ./setup_real_keys.sh
00:50 - 00:52  Test address search
00:52 - 00:54  Test geocoding
00:54 - 00:57  Test unified collection
00:57 - 01:00  Test frontend E2E
01:00 - 01:10  Verify all success criteria
01:10 - 01:15  Document results
```

**Total:** 75 minutes

---

## 🔍 Quick Validation Commands

### Check API Key Status
```bash
cd /home/user/webapp
grep "^KAKAO_REST_API_KEY=" .env
grep "^VWORLD_API_KEY=" .env
grep "^DATA_GO_KR_API_KEY=" .env
```

### Test Each API Independently
```bash
# Kakao (direct test)
curl -H "Authorization: KakaoAK YOUR_KAKAO_KEY" \
  "https://dapi.kakao.com/v2/local/search/address.json?query=강남구"

# VWorld (direct test)
curl "http://api.vworld.kr/req/data?service=data&request=GetFeature&key=YOUR_VWORLD_KEY&domain=localhost"

# Data.go.kr (direct test)
curl "http://apis.data.go.kr/1611000/nsdi/IndvdLandPriceService/attr/getIndvdLandPriceAttr?serviceKey=YOUR_DATA_KEY&pnu=1168010100&stdrYear=2024&format=json"
```

---

## 💡 Pro Tips

1. **Start with Kakao only** - Get 60% of M1 working first
2. **Test with famous buildings** - 파르나스타워, 강남파이낸스센터
3. **Keep .env.backup** - In case you need to revert
4. **Monitor quotas** - Check each provider's console daily
5. **Use browser DevTools** - F12 → Network tab for debugging
6. **Test one API at a time** - Check `collection_errors` to isolate issues

---

## 📞 Quick Support

| Issue Type | Resource |
|------------|----------|
| **API Key Help** | `REAL_API_KEYS_SETUP_GUIDE.md` Section 10 |
| **Testing Help** | `API_TESTING_GUIDE.md` Troubleshooting sections |
| **Backend Logs** | `tail -50 backend.log` |
| **Frontend Logs** | Browser F12 → Console |
| **Kakao Support** | https://devtalk.kakao.com/ |
| **VWorld Support** | help@vworld.kr |
| **Data.go.kr Support** | 1544-3663 |

---

## 🎓 Next Steps After Success

1. ✅ Document findings
2. ✅ Test M1 → M2 integration (Option 2)
3. ✅ Enhance M1 Lock (Option 3)
4. ✅ Test 10+ real addresses
5. ✅ Monitor API usage
6. ✅ Plan production deployment

---

## 📁 File Tree

```
/home/user/webapp/
├── OPTION1_REAL_API_KEYS_READY.md    ← Start here
├── REAL_API_KEYS_SETUP_GUIDE.md      ← API registration
├── API_TESTING_GUIDE.md              ← Testing procedures
├── OPTION1_COMPLETE_SUMMARY.md       ← Achievement report
├── OPTION1_QUICK_REFERENCE.md        ← This file
├── M1_PHASE2_COMPLETE.md             ← Phase 2 report
├── setup_real_keys.sh                ← Setup script
├── restart_backend.sh                ← Restart script
├── .env                              ← Config file
└── backend.log                       ← Server logs
```

---

## 🎯 One-Sentence Summary

**Configure real Kakao, VWorld, and Data.go.kr API keys using `./setup_real_keys.sh`, then validate with the comprehensive test suite in `API_TESTING_GUIDE.md` to ensure M1 v2.0 returns production data.**

---

## ✅ Final Pre-Flight Checklist

Before you start:
- [ ] Read `OPTION1_REAL_API_KEYS_READY.md` (10 min)
- [ ] Understand what each API provides
- [ ] Have 75 minutes available
- [ ] Backend is running (`curl http://localhost:8000/api/m1/health`)
- [ ] Frontend is accessible
- [ ] Ready to sign up for API accounts

After setup:
- [ ] All keys entered in `.env`
- [ ] Backend restarted
- [ ] All tests pass
- [ ] No mock data in responses
- [ ] Success criteria met

---

**🚀 Ready? Let's go!**

```bash
cd /home/user/webapp
cat OPTION1_REAL_API_KEYS_READY.md  # Start reading
```

**Good luck! 화이팅! 🎉**

---

**Print this page and keep it handy during setup!**

---

**Last Updated:** 2025-12-17  
**Version:** 1.0  
**Status:** ✅ Ready  
**Format:** Quick Reference Card
