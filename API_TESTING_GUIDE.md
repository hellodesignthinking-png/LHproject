# 🧪 API Testing Guide - M1 v2.0 with Real Keys

**Created:** 2025-12-17  
**Purpose:** Comprehensive testing procedures for M1 v2.0 with real API keys

---

## 📋 Pre-Testing Checklist

Before running tests, ensure:

- [ ] ✅ Real API keys configured in `.env`
- [ ] ✅ Backend running on port 8000
- [ ] ✅ Frontend running on port 3001
- [ ] ✅ No 401/403 errors in backend logs

**Quick Health Check:**
```bash
cd /home/user/webapp
curl -s http://localhost:8000/api/m1/health | python3 -m json.tool
```

Expected: `"status": "healthy"`, `"version": "2.0"`

---

## 🎯 Test Suite Overview

| Test # | Endpoint | Purpose | Critical? |
|--------|----------|---------|-----------|
| **1** | `/address/search` | Address autocomplete | 🔴 YES |
| **2** | `/geocode` | Address → Coordinates | 🔴 YES |
| **3** | `/collect-all` | Unified data collection | 🔴 YES |
| **4** | Frontend E2E | Complete UI flow | 🟡 Important |

---

## Test 1: Address Search (Kakao API)

### 🎯 Purpose
Test real address search with Kakao API autocomplete.

### 📝 Test Cases

#### **Test 1.1: General Address Search**

```bash
curl -X POST http://localhost:8000/api/m1/address/search \
  -H "Content-Type: application/json" \
  -d '{"query": "서울특별시 강남구 테헤란로 521"}' | python3 -m json.tool
```

**Expected Results:**
```json
{
  "success": true,
  "suggestions": [
    {
      "road_address": "서울특별시 강남구 테헤란로 521",
      "jibun_address": "서울 강남구 삼성동 143",
      "coordinates": {
        "lat": 37.5084448,
        "lon": 127.0626804
      },
      "sido": "서울특별시",
      "sigungu": "강남구",
      "dong": "삼성동",
      "building_name": "파르나스타워"
    }
  ]
}
```

**Validation Criteria:**
- ✅ `success` is `true`
- ✅ `suggestions` array has 1+ items
- ✅ Coordinates are valid (lat: 33-43, lon: 124-132)
- ✅ `building_name` contains real building name
- ✅ NOT generic mock data (테스트빌딩, etc.)

---

#### **Test 1.2: Partial Address Search**

```bash
curl -X POST http://localhost:8000/api/m1/address/search \
  -H "Content-Type: application/json" \
  -d '{"query": "강남구 테헤란로"}' | python3 -m json.tool
```

**Expected:** Multiple suggestions (5-10) with different building numbers

---

#### **Test 1.3: Jibun Address Search**

```bash
curl -X POST http://localhost:8000/api/m1/address/search \
  -H "Content-Type: application/json" \
  -d '{"query": "서울 강남구 역삼동 737"}' | python3 -m json.tool
```

**Expected:** Address suggestions including "강남파이낸스센터"

---

#### **Test 1.4: Invalid Address (Error Handling)**

```bash
curl -X POST http://localhost:8000/api/m1/address/search \
  -H "Content-Type: application/json" \
  -d '{"query": "INVALID_ADDRESS_XYZ123"}' | python3 -m json.tool
```

**Expected:**
```json
{
  "success": true,
  "suggestions": []
}
```

**Validation:** Empty array, no 500 error, no mock fallback

---

### 🐛 Troubleshooting Test 1

| Issue | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Invalid Kakao key | Verify key at https://developers.kakao.com/ |
| `500 Internal Server Error` | Backend crash | Check `backend.log` for stack trace |
| Empty `suggestions` | API quota exceeded | Check Kakao console for quota limits |
| Mock data returned | Key not loaded | Restart backend: `./restart_backend.sh` |

---

## Test 2: Geocoding (Kakao API)

### 🎯 Purpose
Test address-to-coordinates conversion with administrative divisions.

### 📝 Test Cases

#### **Test 2.1: Road Address Geocoding**

```bash
curl -X POST http://localhost:8000/api/m1/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 강남구 테헤란로 521"}' | python3 -m json.tool
```

**Expected Results:**
```json
{
  "success": true,
  "coordinates": {
    "lat": 37.5084448,
    "lon": 127.0626804
  },
  "sido": "서울특별시",
  "sigungu": "강남구",
  "dong": "삼성동",
  "beopjeong_dong": "삼성1동"
}
```

**Validation Criteria:**
- ✅ Coordinates match real location (verify on Kakao Map)
- ✅ `sido` / `sigungu` / `dong` are real administrative units
- ✅ `beopjeong_dong` is legal dong name (법정동)
- ✅ NOT mock coordinates (37.5012, 127.0396)

---

#### **Test 2.2: Jibun Address Geocoding**

```bash
curl -X POST http://localhost:8000/api/m1/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "서울 강남구 삼성동 143"}' | python3 -m json.tool
```

**Expected:** Same coordinates as Test 2.1 (파르나스타워)

---

#### **Test 2.3: Building Name Geocoding**

```bash
curl -X POST http://localhost:8000/api/m1/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "파르나스타워"}' | python3 -m json.tool
```

**Expected:** Geocoding works if building name is unique enough

---

### 🐛 Troubleshooting Test 2

| Issue | Cause | Solution |
|-------|-------|----------|
| Mock coordinates returned | Kakao API failed | Check `backend.log` for 401 error |
| Wrong coordinates | Address ambiguous | Use full road address format |
| `beopjeong_dong` missing | VWorld API needed | This is normal, used in Step 3 |

---

## Test 3: Unified Data Collection (All APIs)

### 🎯 Purpose
Test complete data collection from all external APIs in one call.

### 📝 Test Cases

#### **Test 3.1: Complete Data Collection**

```bash
curl -X POST http://localhost:8000/api/m1/collect-all \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 테헤란로 521",
    "lat": 37.5084448,
    "lon": 127.0626804
  }' | python3 -m json.tool > test_result.json
```

**Expected Results Structure:**

```json
{
  "success": true,
  "land_bundle": {
    "cadastral": {
      "pnu": "1168010400101430000",  // Real 19-digit PNU
      "address": "서울특별시 강남구 삼성동 143",
      "area": 15234.5,
      "jimok": "대",
      "bonbun": "143",
      "bubun": "0"
    },
    "legal": {
      "use_zone": "일반상업지역",  // Real zoning
      "use_district": "중심상업지역",
      "land_use_plan": "도시지역",
      "floor_area_ratio": 1000,
      "building_coverage_ratio": 60
    },
    "road": {
      "road_contact": "15m 도로 접함",
      "road_side": "북측",
      "road_width": 15.0,
      "road_type": "일반도로"
    },
    "market": {
      "official_land_price": 125000000,  // Real 공시지가
      "price_per_area": 8200000,
      "transaction_date": "2024-03-15",
      "recent_transaction_price": 180000000
    }
  },
  "collection_errors": [],  // Should be EMPTY for all real keys
  "data_complete": true
}
```

---

### 🎯 Validation Criteria by Section

#### **✅ Cadastral Data Validation**

| Field | Validation | Example |
|-------|------------|---------|
| `pnu` | 19 digits, format: BBBBB-DDDDD-C-NNNN-MMMM | "1168010400101430000" |
| `address` | Real jibun address | "서울특별시 강남구 삼성동 143" |
| `area` | Positive number (㎡) | 15234.5 |
| `jimok` | Valid land category | "대", "전", "답", "임야" |

**Red Flags:** 
- ❌ PNU = "1168010100107090001" (generic mock)
- ❌ Area = 500.0 (too generic)
- ❌ Jimok = "대지" (should be single char: "대")

---

#### **✅ Legal Data Validation**

| Field | Validation | Example |
|-------|------------|---------|
| `use_zone` | Official Korean planning zone | "일반상업지역", "제2종일반주거지역" |
| `floor_area_ratio` | Realistic % (100-1500) | 1000 |
| `building_coverage_ratio` | Realistic % (20-70) | 60 |

**Red Flags:**
- ❌ use_zone = "주거지역" (too generic, should be specific type)
- ❌ FAR = 200 (same as BCR mock pattern)

---

#### **✅ Road Data Validation**

| Field | Validation | Example |
|-------|------------|---------|
| `road_contact` | Descriptive Korean text | "15m 도로 접함" |
| `road_width` | Realistic meters (4-50) | 15.0 |
| `road_type` | Valid road classification | "일반도로", "보조간선도로" |

---

#### **✅ Market Data Validation**

| Field | Validation | Example |
|-------|------------|---------|
| `official_land_price` | Realistic KRW (>1,000,000) | 125000000 |
| `price_per_area` | Matches division | 125000000 / 15234.5 ≈ 8200000 |
| `transaction_date` | Recent date (YYYY-MM-DD) | "2024-03-15" |

**Red Flags:**
- ❌ official_land_price = 50000000 (too low for Gangnam)
- ❌ transaction_date = "" (missing)

---

#### **✅ Collection Errors Validation**

**Expected with Real Keys:**
```json
"collection_errors": []
```

**If errors present:**
```json
"collection_errors": [
  {
    "source": "VWorld Cadastral API",
    "error": "401 Unauthorized",
    "details": "Invalid API key"
  }
]
```

**Action Plan:**
1. Check which API failed
2. Verify that specific API key in `.env`
3. Check API key activation status in provider console
4. Review API quota/limits

---

#### **Test 3.2: Different Address Types**

Test with various real addresses to verify data quality:

**Commercial Zone:**
```bash
curl -X POST http://localhost:8000/api/m1/collect-all \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 종로구 세종대로 175", "lat": 37.5719, "lon": 126.9769}' \
  | python3 -m json.tool
```

**Residential Zone:**
```bash
curl -X POST http://localhost:8000/api/m1/collect-all \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 강남구 도곡동 467-1", "lat": 37.4860, "lon": 127.0516}' \
  | python3 -m json.tool
```

**Industrial Zone:**
```bash
curl -X POST http://localhost:8000/api/m1/collect-all \
  -H "Content-Type: application/json" \
  -d '{"address": "경기도 수원시 영통구 덕영대로 1556", "lat": 37.2686, "lon": 127.0373}' \
  | python3 -m json.tool
```

---

### 🐛 Troubleshooting Test 3

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| All data mock | No real API keys | Run `./setup_real_keys.sh` |
| Some fields real, some mock | Partial key configuration | Check `collection_errors` field |
| `data_complete: false` | One or more APIs failed | Review individual API test results |
| Empty PNU | Coordinates outside Korea | Verify lat/lon values |
| Wrong land use zone | VWorld key inactive | Check VWorld console activation |
| No market data | Data.go.kr API not activated | Activate specific market data APIs |

---

## Test 4: Frontend E2E Test

### 🎯 Purpose
Test complete user flow with real APIs through the frontend UI.

### 📝 Test Procedure

#### **Step 0: Open Frontend**
```
URL: https://3001-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai/pipeline
```

#### **Step 1: Click "M1 시작하기"**
- ✅ Page transitions to address input

#### **Step 2: Enter Address**
- **Input:** `서울특별시 강남구 테헤란로 521`
- **Click:** `검색` button
- ✅ **Expected:** Dropdown shows 5-10 real suggestions
- ✅ **Verify:** Suggestions include building names (파르나스타워, etc.)
- ❌ **Red Flag:** Only 2 suggestions with "테스트빌딩" → Mock data still active

#### **Step 3: Select Address**
- **Click:** First suggestion
- ✅ Address field populates
- **Click:** `다음` button

#### **Step 4: Verify Location**
- ✅ **Expected:** Coordinates shown (37.5084, 127.0626)
- ✅ **Verify:** Administrative divisions (서울특별시, 강남구, 삼성동)
- ❌ **Red Flag:** Coordinates = (37.5012, 127.0396) → Generic mock
- **Click:** `다음` button

#### **Step 5: Review Collected Data** ⭐ NEW in v2.0
**This is the critical ReviewScreen test!**

**Expected UI Sections:**

1. **📍 Cadastral Data (지적 정보)**
   - ✅ PNU: 19 digits (e.g., "1168010400101430000")
   - ✅ Land Area: Realistic value (e.g., "15,234.5 ㎡")
   - ✅ Jimok: Single Korean char (대, 전, 답)
   - ✅ Lot Numbers: Bonbun/Bubun (143-0)

2. **🏛️ Legal Info (법적 정보)**
   - ✅ Use Zone: Specific type (일반상업지역)
   - ✅ FAR: Realistic % (1000%)
   - ✅ BCR: Realistic % (60%)
   - ✅ Regulations: Detailed text (not "규제사항 없음")

3. **🛣️ Road Info (도로 정보)**
   - ✅ Road Contact: Descriptive (15m 도로 접함)
   - ✅ Road Width: Number with unit (15.0m)
   - ✅ Road Type: Classification (일반도로)

4. **💰 Market Data (시장 정보)**
   - ✅ Official Price: Large KRW (125,000,000원)
   - ✅ Price per ㎡: Calculated value
   - ✅ Transaction Date: Recent date
   - ✅ Recent Transaction: Realistic price

**API Status Indicators:**
- ✅ All badges show `✓ Kakao API`, `✓ VWorld API`, `✓ Data.go.kr API`
- ❌ **Red Flag:** Badges show `⚠ Mock API v1.0`

**Data Source Info:**
- ✅ Timestamps are recent (within last minute)
- ✅ Confidence levels: "high" or "verified"
- ❌ **Red Flag:** Source says "Mock Data Generator"

#### **Step 6: Edit Fields (Optional)**
- **Click:** Edit icon (✏️) on any field
- **Change:** Value
- **Click:** Save (✓)
- ✅ **Expected:** Field updates, badge changes to `✓ User Input`

#### **Step 7: Complete Review**
- **Click:** `다음` button
- ✅ Transitions to Step 4 (Context Freeze)

#### **Step 8: Freeze Context**
- **Review:** Final summary
- **Click:** `M1 확정` button
- ✅ **Expected:** Success message, context ID generated

---

### 🐛 Frontend E2E Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Address search shows mock data | Backend using mock keys | Run `./setup_real_keys.sh` + restart |
| ReviewScreen shows loading forever | Backend API error | Check browser console (F12) |
| API status badges show "Mock" | Real keys not working | Test backend APIs individually |
| Edit button not working | Frontend component error | Check browser console for errors |
| Cannot freeze context | Validation failed | Check backend logs for validation errors |

---

## 📊 Test Results Template

Use this template to document your test results:

```markdown
# M1 v2.0 Real API Keys Test Report

**Date:** 2025-12-17
**Tester:** [Your Name]
**Environment:** ZeroSite M1 v2.0

## API Keys Status
- [ ] Kakao REST API: [CONFIGURED / NOT CONFIGURED]
- [ ] VWorld API: [CONFIGURED / NOT CONFIGURED]
- [ ] Data.go.kr API: [CONFIGURED / NOT CONFIGURED]

## Test Results

### Test 1: Address Search
- **Status:** [PASS / FAIL]
- **Notes:** 
  - Query: "서울특별시 강남구 테헤란로 521"
  - Suggestions returned: [Number]
  - Mock data detected: [YES / NO]

### Test 2: Geocoding
- **Status:** [PASS / FAIL]
- **Coordinates:** (lat, lon)
- **Mock coordinates detected:** [YES / NO]

### Test 3: Unified Data Collection
- **Status:** [PASS / FAIL]
- **Collection Errors:** [List any errors]
- **Data Quality:**
  - [ ] PNU: Real 19-digit format
  - [ ] Use Zone: Specific Korean planning zone
  - [ ] Market Price: Realistic value
  - [ ] All fields populated

### Test 4: Frontend E2E
- **Status:** [PASS / FAIL]
- **ReviewScreen Display:** [CORRECT / ISSUES]
- **API Status Badges:** [Real APIs / Mock APIs]
- **Data Accuracy:** [VERIFIED / NOT VERIFIED]

## Issues Found
1. [Issue description]
2. [Issue description]

## Recommendations
1. [Recommendation]
2. [Recommendation]

## Conclusion
- Overall Status: [SUCCESS / NEEDS WORK]
- Ready for Production: [YES / NO]
```

---

## 🎯 Success Criteria Summary

Your M1 v2.0 is ready for production when:

✅ **All Test 1 (Address Search) passes** with real suggestions  
✅ **Test 2 (Geocoding) returns** accurate coordinates  
✅ **Test 3 (Unified Collection)** has `collection_errors: []`  
✅ **Test 4 (Frontend E2E)** shows real data in ReviewScreen  
✅ **API status badges** all show real API names (not Mock)  
✅ **Data validation** confirms realistic values in all fields  
✅ **No 401/403 errors** in backend logs  
✅ **Context freeze** completes successfully

---

## 📚 Additional Resources

- **API Setup Guide:** `REAL_API_KEYS_SETUP_GUIDE.md`
- **Setup Script:** `./setup_real_keys.sh`
- **Restart Script:** `./restart_backend.sh`
- **Backend Logs:** `tail -f backend.log`
- **M1 Phase 2 Complete:** `M1_PHASE2_COMPLETE.md`

---

## 🆘 Getting Help

If tests fail after following all steps:

1. **Check backend logs:** `tail -50 backend.log`
2. **Check browser console:** F12 → Console tab
3. **Verify API keys:** `cat .env | grep API_KEY`
4. **Test APIs individually:** Follow Test 1, 2, 3 in order
5. **Review provider documentation:** See links in `REAL_API_KEYS_SETUP_GUIDE.md`

---

**Good luck with testing! 🚀**

**Last Updated:** 2025-12-17  
**M1 Version:** v2.0  
**Test Suite Version:** 1.0
