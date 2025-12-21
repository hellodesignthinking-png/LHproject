# 🚀 ZeroSite v4.0 M1+M4 Setup & Testing Guide

**Date:** 2025-12-17  
**Version:** 1.0  
**Modules:** M1 Land Information + M4 V2 Schematic Generation

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Setup](#environment-setup)
3. [Redis Installation](#redis-installation)
4. [API Key Configuration](#api-key-configuration)
5. [Testing Guide](#testing-guide)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+ (for frontend, if needed)
- Redis 6.0+
- Git

### Installation Steps

```bash
# 1. Navigate to project directory
cd /home/user/webapp

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Copy environment template
cp .env.example .env

# 4. Edit .env with your API keys
nano .env  # or use your preferred editor

# 5. Start Redis (see Redis Installation section)
redis-server

# 6. Run the application
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔧 Environment Setup

### Required API Keys

#### 1. JUSO API (행정안전부 주소정보 API)
- **Purpose:** Address search (STEP 1)
- **Get Key:** https://www.juso.go.kr/addrlink/requestAddrLinkApi.do
- **Env Variable:** `JUSO_API_KEY`

**Steps to Get Key:**
1. Visit JUSO API website
2. Register/Login
3. Apply for API key (개발자센터 → API 신청)
4. Copy your key and paste into `.env`

```bash
JUSO_API_KEY=your_actual_juso_api_key_here
```

---

#### 2. Kakao REST API (Geocoding & Local)
- **Purpose:** Geocoding (STEP 2)
- **Get Key:** https://developers.kakao.com/
- **Env Variable:** `KAKAO_REST_API_KEY`

**Steps to Get Key:**
1. Visit Kakao Developers
2. Create account/Login
3. Create new application (내 애플리케이션 → 애플리케이션 추가하기)
4. Go to "앱 설정" → "앱 키" → Copy "REST API 키"
5. Enable "Kakao Local" API (플랫폼 설정)

```bash
KAKAO_REST_API_KEY=your_actual_kakao_api_key_here
```

---

#### 3. VWorld API (국토교통부 토지이용규제)
- **Purpose:** Land use & zoning (STEP 4)
- **Get Key:** http://www.vworld.kr/
- **Env Variable:** `LAND_REGULATION_API_KEY`

**Steps to Get Key:**
1. Visit VWorld
2. Register/Login
3. Apply for API key (오픈 API → 인증키 신청)
4. Select required APIs (토지이용규제정보서비스)

```bash
LAND_REGULATION_API_KEY=your_actual_vworld_api_key_here
```

---

#### 4. Data.go.kr API (공공데이터포털)
- **Purpose:** Market data & transactions (STEP 6)
- **Get Key:** https://www.data.go.kr/
- **Env Variable:** `MOIS_API_KEY`

**Steps to Get Key:**
1. Visit data.go.kr
2. Register/Login
3. Search for "부동산 실거래가" API
4. Apply for API usage (활용신청)
5. Wait for approval (usually instant)

```bash
MOIS_API_KEY=your_actual_data_go_kr_api_key_here
```

---

## 🗄️ Redis Installation

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify installation
redis-cli ping
# Expected output: PONG
```

### macOS (with Homebrew)
```bash
brew install redis
brew services start redis

# Verify installation
redis-cli ping
# Expected output: PONG
```

### Windows (WSL recommended)
```bash
# Use WSL Ubuntu and follow Ubuntu instructions above
# Or download Redis for Windows from:
# https://github.com/microsoftarchive/redis/releases
```

### Docker (Cross-platform)
```bash
docker run --name redis -d -p 6379:6379 redis:latest
docker ps  # Verify running

# Test connection
docker exec -it redis redis-cli ping
# Expected output: PONG
```

### Redis Configuration

Default configuration in `.env`:
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://localhost:6379/0
```

**Note:** M1 uses Redis for short-term context storage (24-hour TTL).

---

## 🧪 Testing Guide

### 1. Backend Health Check

```bash
# Test M1 API health
curl http://localhost:8000/api/m1/health

# Expected response:
# {"status": "healthy", "module": "M1 Land Information API"}
```

### 2. M1 STEP-by-STEP Testing

#### STEP 1: Address Search
```bash
curl -X POST http://localhost:8000/api/m1/address/search \
  -H "Content-Type: application/json" \
  -d '{"query": "서울시 강남구 역삼동"}'

# Expected: List of address suggestions with coordinates
```

#### STEP 2: Geocoding
```bash
curl -X POST http://localhost:8000/api/m1/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "서울시 강남구 역삼동 123"}'

# Expected: Coordinates (lat, lon) and administrative divisions
```

#### STEP 3: Cadastral Data
```bash
curl -X POST http://localhost:8000/api/m1/cadastral \
  -H "Content-Type: application/json" \
  -d '{"coordinates": {"lat": 37.5665, "lon": 126.9780}}'

# Expected: bonbun, bubun, jimok, area
```

#### STEP 4: Land Use
```bash
curl -X POST http://localhost:8000/api/m1/land-use \
  -H "Content-Type: application/json" \
  -d '{"coordinates": {"lat": 37.5665, "lon": 126.9780}, "jimok": "대지"}'

# Expected: zone_type, bcr, far, regulations
```

#### STEP 5: Road Information
```bash
curl -X POST http://localhost:8000/api/m1/road-info \
  -H "Content-Type: application/json" \
  -d '{"coordinates": {"lat": 37.5665, "lon": 126.9780}, "radius": 100}'

# Expected: road_width, road_type, nearby_roads
```

#### STEP 6: Market Data
```bash
curl -X POST http://localhost:8000/api/m1/market-data \
  -H "Content-Type: application/json" \
  -d '{"coordinates": {"lat": 37.5665, "lon": 126.9780}, "area": 500, "radius": 1000}'

# Expected: official_land_price, transactions[]
```

#### STEP 8: Freeze Context
```bash
curl -X POST http://localhost:8000/api/m1/freeze-context \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울시 강남구 역삼동 123",
    "road_address": "서울시 강남구 테헤란로 123",
    "coordinates": {"lat": 37.5665, "lon": 126.9780},
    "sido": "서울시", "sigungu": "강남구", "dong": "역삼동",
    "bonbun": "10", "bubun": "1", "jimok": "대지", "area": 500,
    "zone_type": "제2종일반주거지역", "zone_detail": "",
    "bcr": 60, "far": 200, "land_use": "주거용",
    "regulations": [], "restrictions": [],
    "road_width": 12, "road_type": "소로",
    "data_sources": {}
  }'

# Expected: context_id, land_info_context, frozen: true
```

#### Get Frozen Context
```bash
# Replace {context_id} with actual ID from freeze response
curl http://localhost:8000/api/m1/context/{context_id}

# Expected: Full CanonicalLandContext
```

### 3. M4 V2 Schematic Testing

```bash
# Test M4 capacity calculation with schematic generation
curl -X POST http://localhost:8000/api/reports/v4/pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "parcel_id": "1168010100100010001",
    "context_id": "your_frozen_context_id_here"
  }'

# Expected response should include:
# - schematic_drawings_available: true
# - schematic_files: [...]
# - legal_capacity_units, incentive_capacity_units
# - parking_alt_a_spaces, parking_alt_b_spaces
```

#### View Schematics
```bash
# After pipeline completes, schematics are saved to:
ls -lh static/schematics/

# Expected files:
# - {parcel_id}_ground_layout.svg
# - {parcel_id}_standard_floor.svg
# - {parcel_id}_basement_parking.svg
# - {parcel_id}_massing_comparison.svg

# Access via browser:
# http://localhost:8000/static/schematics/{parcel_id}_ground_layout.svg
```

### 4. Redis Context Storage Testing

```bash
# Connect to Redis CLI
redis-cli

# Check stored contexts (in Redis CLI)
KEYS context:*

# Get a specific context
GET context:{context_id}

# Check TTL (time to live)
TTL context:{context_id}
# Expected: ~86400 (24 hours in seconds)

# Exit Redis CLI
EXIT
```

### 5. Frontend Testing (Manual)

1. **Start Backend:**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access M1 Landing Page:**
   ```
   http://localhost:8000/m1  # (if route configured)
   ```

3. **Test STEP 0-8 Flow:**
   - STEP 0: Click "시작하기"
   - STEP 1: Enter address "서울시 강남구 역삼동"
   - STEP 2: Verify coordinates on map
   - STEP 3: Check auto-filled cadastral data or upload PDF
   - STEP 4: Review zoning information
   - STEP 5: Check road access details
   - STEP 6: View market data and transactions
   - STEP 7: Review all collected data
   - STEP 8: Freeze context and get context_id

4. **Test M4 Schematic Viewer:**
   - Navigate to M4 results page
   - Click on "도면 보기" tab
   - View 4 schematic drawings
   - Test download functionality

---

## 🔍 Troubleshooting

### Issue: "No module named 'fastapi'"
**Solution:**
```bash
pip install fastapi uvicorn pydantic
```

### Issue: "Redis connection refused"
**Solution:**
```bash
# Check Redis status
sudo systemctl status redis-server  # Linux
brew services list  # macOS

# Restart Redis
sudo systemctl restart redis-server  # Linux
brew services restart redis  # macOS
```

### Issue: "API key invalid"
**Solution:**
1. Double-check `.env` file has correct keys
2. Verify no extra spaces around `=` sign
3. Ensure API keys are active on respective platforms
4. Check API usage quotas

### Issue: "ModuleNotFoundError" for external APIs
**Solution:**
```bash
# Install missing dependencies
pip install httpx redis pydantic-settings python-dotenv
```

### Issue: "PDF parsing failed"
**Solution:**
```bash
# Install PDF dependencies
pip install PyPDF2 google-cloud-vision pillow
```

### Issue: Schematics not generating
**Solution:**
1. Check `/static/schematics/` directory exists:
   ```bash
   mkdir -p static/schematics
   ```
2. Verify write permissions:
   ```bash
   chmod 755 static/schematics
   ```

---

## 📊 Expected Results Summary

### M1 Full Flow Test
✅ STEP 1: 3+ address suggestions returned  
✅ STEP 2: Coordinates with 6 decimal places  
✅ STEP 3: bonbun, bubun, jimok, area (sqm)  
✅ STEP 4: zone_type, bcr (%), far (%)  
✅ STEP 5: road_width (m), road_type  
✅ STEP 6: official_land_price, transactions[]  
✅ STEP 8: context_id (UUID format)  

### M4 Schematic Test
✅ 4 SVG files generated  
✅ Files size: 5-50 KB each  
✅ Viewable in browser  
✅ Download functionality works  

### Redis Storage Test
✅ Context stored with key `context:{uuid}`  
✅ TTL set to 86400 seconds (24 hours)  
✅ Data retrievable via GET endpoint  

---

## 📞 Support & Next Steps

### If All Tests Pass ✅
1. Configure `.env` with real API keys
2. Test with real address data
3. Verify M2-M6 pipeline integration
4. Run full end-to-end test

### If Tests Fail ❌
1. Check logs: `logs/zerosite.log` (if configured)
2. Review error messages in terminal
3. Verify all dependencies installed
4. Check Redis is running
5. Validate API keys in `.env`

---

## 🎉 Congratulations!

If all tests pass, your ZeroSite v4.0 M1+M4 system is **FULLY OPERATIONAL** and ready for:
- Real-world land information collection
- Automatic schematic drawing generation
- M2-M6 pipeline integration
- Production deployment

---

**Last Updated:** 2025-12-17  
**Document Version:** 1.0  
**Author:** ZeroSite Development Team
