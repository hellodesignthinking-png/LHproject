# 🔑 Real API Keys Setup Guide for M1 v2.0

**Created:** 2025-12-17  
**Purpose:** Production-ready testing with real Korean land information APIs

---

## 📋 Required API Keys Overview

For full M1 v2.0 functionality, you need **4 essential API keys**:

| API | Provider | Purpose | Free Tier | Priority |
|-----|----------|---------|-----------|----------|
| **Kakao REST API** | Kakao Developers | Address search & Geocoding | ✅ Yes | 🔴 **CRITICAL** |
| **VWorld API** | 국토교통부 | Cadastral data & Land use | ✅ Yes | 🔴 **CRITICAL** |
| **Data.go.kr API** | 공공데이터포털 | Market data & Transactions | ✅ Yes | 🟡 Important |
| **JUSO API** | 행정안전부 | Address verification | ✅ Yes | 🟢 Optional |

---

## 1️⃣ Kakao REST API Key (CRITICAL)

### 📍 What it does
- **STEP 1:** Address search with autocomplete
- **STEP 2:** Geocoding (address → lat/lon)
- **STEP 3:** Reverse geocoding (lat/lon → administrative divisions)

### 🔗 Registration Process

#### **Step A: Create Kakao Account**
1. Go to: https://developers.kakao.com/
2. Click `시작하기` (Get Started)
3. Sign up with email/phone or use existing Kakao account

#### **Step B: Create Application**
1. Log in to Kakao Developers Console
2. Click `내 애플리케이션` (My Applications)
3. Click `애플리케이션 추가하기` (Add Application)
4. Fill in:
   - **앱 이름:** `ZeroSite M1 Land Information`
   - **사업자명:** Your name or company
   - **카테고리:** 부동산/건설 (Real Estate/Construction)
5. Click `저장` (Save)

#### **Step C: Get REST API Key**
1. In your app dashboard, find **앱 키** (App Keys) section
2. Copy the **REST API 키** (REST API Key)
   - Format: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (32 characters)
3. **Save this key!**

#### **Step D: Enable Required APIs**
1. Go to `제품 설정` → `Local` (지도/로컬)
2. Enable:
   - ✅ 주소 검색 (Address Search)
   - ✅ 좌표→주소 변환 (Coord to Address)
   - ✅ 주소→좌표 변환 (Address to Coord)
3. Click `설정 저장` (Save Settings)

#### **Step E: Configure Platform**
1. Go to `플랫폼` (Platform) tab
2. Click `Web 플랫폼 등록` (Register Web Platform)
3. Add your domain:
   ```
   http://localhost:3000
   http://localhost:3001
   https://3001-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai
   ```
4. Click `저장` (Save)

### ✅ Testing Your Kakao Key

```bash
# Test address search
curl -X GET "https://dapi.kakao.com/v2/local/search/address.json?query=서울특별시%20강남구%20역삼동" \
  -H "Authorization: KakaoAK YOUR_KAKAO_REST_API_KEY"

# Expected response: JSON with address results
```

---

## 2️⃣ VWorld API Key (CRITICAL)

### 📍 What it does
- **STEP 3:** Cadastral data (PNU, lot number, land area)
- **STEP 4:** Land use regulations (용도지역, 지구단위계획)
- **STEP 4:** Zoning info (FAR, BCR)

### 🔗 Registration Process

#### **Step A: Join VWorld**
1. Go to: http://www.vworld.kr/
2. Click `회원가입` (Sign Up) in top-right
3. Fill in registration form:
   - **이름:** Your name
   - **이메일:** Your email
   - **휴대폰:** Your phone number
4. Verify email and complete registration

#### **Step B: Apply for API Key**
1. Log in to VWorld
2. Click `오픈API` (Open API) in top menu
3. Click `인증키 신청` (Apply for API Key)
4. Fill in application:
   - **서비스명:** `ZeroSite M1 Land Information Service`
   - **서비스 URL:** `http://localhost:3000`
   - **서비스 설명:** `부동산 분석을 위한 토지 정보 수집 서비스`
   - **용도:** 개인/학습용 또는 사업용 (select appropriate)
5. Select required APIs:
   - ✅ 토지(임야)대장정보 조회 (Land Register Info)
   - ✅ 지적도 조회 (Cadastral Map)
   - ✅ 용도지역지구 조회 (Land Use Zone)
   - ✅ 건축물대장 조회 (Building Register)
6. Submit application

#### **Step C: Get API Key**
- Processing time: **Immediate** to 1 business day
- Check `마이페이지` → `인증키 관리` (My API Keys)
- Copy your API key (36-40 characters)

### ✅ Testing Your VWorld Key

```bash
# Test cadastral data query
curl "http://api.vworld.kr/req/data?service=data&request=GetFeature&data=LP_PA_CBND_BUBUN&key=YOUR_VWORLD_API_KEY&domain=http://localhost:3000&attrFilter=pnu:like:1168010100"

# Expected response: XML/JSON with cadastral data
```

---

## 3️⃣ Data.go.kr API Key (Important)

### 📍 What it does
- **STEP 6:** Real estate market data
- **STEP 6:** Transaction history (매매가, 전월세)
- **STEP 6:** Official land prices (공시지가)

### 🔗 Registration Process

#### **Step A: Create Account**
1. Go to: https://www.data.go.kr/
2. Click `회원가입` (Sign Up)
3. Choose:
   - 개인회원 (Individual) for personal use
   - 기관회원 (Organization) for business use
4. Complete registration with email/phone verification

#### **Step B: Find Required APIs**
Search and activate these APIs:

**A. 국토교통부 실거래가 정보 (Transaction Prices)**
1. Search: `국토교통부 아파트 실거래가`
2. Click on service
3. Click `활용신청` (Apply for Use)
4. Purpose: `부동산 분석 서비스` (Real estate analysis)
5. Wait for approval (usually instant)

**B. 국토교통부 공시지가 정보 (Official Land Prices)**
1. Search: `개별공시지가 조회`
2. Click on service
3. Click `활용신청` (Apply for Use)
4. Wait for approval

#### **Step C: Get API Key**
1. Go to `마이페이지` → `오픈API` → `개발계정`
2. Find your **일반 인증키 (Decoding)** 
3. This key works for ALL activated Data.go.kr APIs
4. Copy the key (long alphanumeric string)

### ✅ Testing Your Data.go.kr Key

```bash
# Test official land price API
curl "http://apis.data.go.kr/1611000/nsdi/IndvdLandPriceService/attr/getIndvdLandPriceAttr?serviceKey=YOUR_DATA_GO_KR_API_KEY&pnu=1168010100&stdrYear=2024&format=json"

# Expected response: JSON with land price data
```

---

## 4️⃣ JUSO API Key (Optional)

### 📍 What it does
- Alternative address search
- Address standardization
- Detailed administrative division info

### 🔗 Registration Process

#### **Step A: Register**
1. Go to: https://www.juso.go.kr/addrlink/requestAddrLinkApi.do
2. Click `신청하기` (Apply)
3. Fill in:
   - **사용 목적:** 부동산 정보 시스템
   - **URL:** http://localhost:3000
4. Submit application

#### **Step B: Get API Key**
- Approval time: 1-2 business days
- Check your email for approval
- Log in and get your API key from dashboard

---

## 🚀 Quick Setup Script

Once you have all API keys, run this script:

```bash
cd /home/user/webapp

# Backup current .env
cp .env .env.backup

# Update .env with your real keys
cat > .env << 'EOF'
# ============================================================================
# ZeroSite v4.0 Environment Configuration - PRODUCTION KEYS
# ============================================================================

# ----------------------------------------------------------------------------
# M1 External API Keys (Government & Public APIs)
# ----------------------------------------------------------------------------

# Kakao REST API Key (CRITICAL - Address & Geocoding)
KAKAO_REST_API_KEY=YOUR_KAKAO_REST_API_KEY_HERE

# VWorld API Key (CRITICAL - Cadastral & Land Use)
LAND_REGULATION_API_KEY=YOUR_VWORLD_API_KEY_HERE
VWORLD_API_KEY=YOUR_VWORLD_API_KEY_HERE
LAND_USE_REGULATION_API_KEY=YOUR_VWORLD_API_KEY_HERE
BUILDING_REGISTRY_API_KEY=YOUR_VWORLD_API_KEY_HERE

# Data.go.kr API Key (Important - Market Data)
MOIS_API_KEY=YOUR_DATA_GO_KR_API_KEY_HERE
DATA_GO_KR_API_KEY=YOUR_DATA_GO_KR_API_KEY_HERE

# JUSO API Key (Optional - Address Verification)
# JUSO_API_KEY=YOUR_JUSO_API_KEY_HERE

# ----------------------------------------------------------------------------
# Redis Configuration (M1 Context Storage)
# ----------------------------------------------------------------------------

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://localhost:6379/0

# ----------------------------------------------------------------------------
# Database Configuration
# ----------------------------------------------------------------------------

DATABASE_URL=sqlite:///./lh_analysis.db

# ----------------------------------------------------------------------------
# Application Configuration
# ----------------------------------------------------------------------------

SESSION_SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=true
HOST=0.0.0.0
PORT=8000

# ----------------------------------------------------------------------------
# CORS Configuration
# ----------------------------------------------------------------------------

CORS_ORIGINS=http://localhost:3000,http://localhost:8001,https://3001-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai

EOF

echo "✅ .env file updated! Now replace placeholder values with your actual API keys."
echo "📝 Edit .env file: nano .env"
```

---

## 🔄 Restart Services After Updating Keys

```bash
# Stop current backend
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Restart backend with new keys
cd /home/user/webapp && \
  source venv/bin/activate && \
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Wait for startup
sleep 5

# Test health
curl http://localhost:8000/api/m1/health | python3 -m json.tool

# Test with real address
curl -X POST http://localhost:8000/api/m1/collect-all \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 테헤란로 521",
    "lat": 37.5012345,
    "lon": 127.0396789
  }' | python3 -m json.tool
```

---

## 🧪 Testing Checklist

After adding real API keys, verify each integration:

### ✅ STEP 1: Address Search (Kakao)
```bash
curl -X POST http://localhost:8000/api/m1/address/search \
  -H "Content-Type: application/json" \
  -d '{"query": "서울특별시 강남구 테헤란로 521"}' | python3 -m json.tool
```

**Expected:** Real address suggestions from Kakao API (not mock data)

---

### ✅ STEP 2: Geocoding (Kakao)
```bash
curl -X POST http://localhost:8000/api/m1/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 강남구 테헤란로 521"}' | python3 -m json.tool
```

**Expected:** Real coordinates and administrative divisions

---

### ✅ STEP 3: Unified Data Collection (All APIs)
```bash
curl -X POST http://localhost:8000/api/m1/collect-all \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 테헤란로 521",
    "lat": 37.5012345,
    "lon": 127.0396789
  }' | python3 -m json.tool
```

**Expected Results:**
- ✅ `cadastral.pnu`: Real PNU from VWorld (e.g., "1168010100107090001")
- ✅ `legal.use_zone`: Real land use zone (e.g., "일반상업지역")
- ✅ `legal.floor_area_ratio`: Real FAR from regulations
- ✅ `road.road_contact`: Real road contact info
- ✅ `market.official_land_price`: Real 공시지가 from Data.go.kr
- ✅ `collection_errors`: Empty array (all APIs successful)

---

## 📊 API Rate Limits & Quotas

| API | Free Tier Limit | Rate Limit | Notes |
|-----|----------------|------------|-------|
| **Kakao** | 300,000 calls/day | 30 calls/sec | Per app key |
| **VWorld** | 10,000 calls/day | 1,000 calls/hour | Per API key |
| **Data.go.kr** | Varies by API | Usually 1,000/day | Per service |
| **JUSO** | 1,000 calls/day | N/A | Daily limit |

**Tip:** For production use beyond free tier, apply for premium tier at each provider.

---

## ⚠️ Common Issues & Solutions

### Issue 1: Kakao API 401 Unauthorized
**Cause:** Invalid API key or platform not registered  
**Solution:**
1. Verify key is correct (32 chars)
2. Check platform settings in Kakao console
3. Ensure domain is whitelisted

### Issue 2: VWorld API No Response
**Cause:** API key not activated or domain not allowed  
**Solution:**
1. Check API activation status in VWorld console
2. Verify domain in API key settings
3. Try without domain parameter first

### Issue 3: Data.go.kr API 403 Forbidden
**Cause:** API not activated or key needs decoding  
**Solution:**
1. Ensure you activated the specific API service
2. Use **일반 인증키 (Decoding)** not 서비스 인증키
3. Check activation status in MyPage

### Issue 4: Mock Data Still Appearing
**Cause:** Backend not restarted or keys not loaded  
**Solution:**
1. Restart backend: `lsof -ti:8000 | xargs kill -9 && sleep 2`
2. Check `.env` file is in project root
3. Verify keys loaded: `cd /home/user/webapp && grep KAKAO_REST_API_KEY .env`

---

## 🎯 Expected Improvements with Real Keys

### Before (Mock Data) ❌
- Fixed Gangnam coordinates (37.5012, 127.0396)
- Generic PNU: "1168010100107090001"
- Mock land use: "제2종일반주거지역"
- No real market prices
- All data sources: "Mock API v1.0"

### After (Real Keys) ✅
- **Actual coordinates** for queried address
- **Real PNU** from cadastral database
- **Official land use zones** from regulations
- **Current market prices** from transactions
- Data sources show real API versions and timestamps

---

## 📞 API Provider Support

| Provider | Support | Documentation |
|----------|---------|---------------|
| **Kakao** | https://devtalk.kakao.com/ | https://developers.kakao.com/docs |
| **VWorld** | help@vworld.kr | http://www.vworld.kr/dev/ |
| **Data.go.kr** | 1544-3663 | https://www.data.go.kr/support |
| **JUSO** | help@juso.go.kr | https://www.juso.go.kr/addrlink/devAddrLinkRequestGuide.do |

---

## 🎓 Next Steps After Key Setup

1. **Test individual endpoints** (address search → geocode → collect-all)
2. **Test full M1 flow** in frontend UI
3. **Verify data accuracy** with known addresses
4. **Test error handling** (invalid addresses, API failures)
5. **Monitor API usage** (check quotas in each console)
6. **Document findings** in project wiki

---

## 🏆 Success Criteria

You'll know real API keys are working when:

✅ Address search returns **multiple real suggestions** (not just 2 mock addresses)  
✅ Coordinates match actual locations on map  
✅ PNU format is valid (19 digits: AAAAA-BBBBB-C-DDDD-EEEE)  
✅ Land use zones are official Korean planning zones  
✅ Market prices are in realistic KRW ranges  
✅ `collection_errors` array is empty  
✅ Data sources show real API names (not "Mock API v1.0")

---

## 📝 Quick Reference: API Key Format

```bash
# Kakao REST API Key
KAKAO_REST_API_KEY=1234567890abcdef1234567890abcdef  # 32 chars

# VWorld API Key
VWORLD_API_KEY=12345678-ABCD-1234-ABCD-1234567890AB  # UUID format

# Data.go.kr API Key (Decoding)
DATA_GO_KR_API_KEY=very_long_encoded_string_with_special_chars%3D%3D  # Long string

# JUSO API Key
JUSO_API_KEY=U01TX0FVVEgyMDI0MTIxNzE2MzQ1NjEwNTI5Mzg%3D  # Encoded string
```

---

**🎉 Good luck with your API key setup!**

For any issues, refer to the official documentation or contact the respective API provider support teams.

---

**Last Updated:** 2025-12-17  
**M1 Version:** v2.0  
**Status:** Ready for production testing
