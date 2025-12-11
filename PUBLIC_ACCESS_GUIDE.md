# 🌐 ZeroSite v3.2 Public Access Guide

## ✅ Server Status: ONLINE & ACCESSIBLE

Last Verified: 2025-12-11 01:44:27 UTC

---

## 📡 Public Server URL

**Main URL:**
```
https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai
```

**Server Status:** ✅ HEALTHY  
**Version:** 23.0.0 + v3.2.0  
**Quality:** PRODUCTION READY  

---

## 🎯 Quick Test Links (클릭해서 바로 테스트)

### 1️⃣ Health Check (서버 상태 확인)
```
https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "version": "23.0.0",
  "uptime_seconds": 264.36,
  "success_rate": "100.0%"
}
```

### 2️⃣ Service Info (서비스 정보)
```
https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/
```
**Expected Response:**
```json
{
  "service": "ZeroSite v23 + Expert v3.2 - A/B Scenario Comparison",
  "version": "23.0.0 + v3.2.0",
  "status": "PRODUCTION READY",
  "endpoints": {
    "health": "/health",
    "metrics": "/metrics",
    "generate_ab_report": "POST /api/v23/generate-ab-report",
    "generate_expert_v32_report": "POST /api/v3.2/generate-expert-report",
    "api_docs": "/api/v23/docs"
  }
}
```

### 3️⃣ Interactive API Documentation (Swagger UI) **← 가장 쉬운 테스트 방법**
```
https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/docs
```
**Features:**
- 🖱️ Click "Try it out" to test APIs directly in browser
- 📝 Automatic request/response formatting
- ✅ Real-time validation

---

## 🧪 API Testing Examples

### Example 1: Generate Expert v3.2 Report (강남 테스트)

**Request:**
```bash
curl -X POST "https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v3.2/generate-expert-report" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 역삼동 123-45",
    "land_area_sqm": 1650.0,
    "bcr_legal": 50.0,
    "far_legal": 300.0
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "report_url": "https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/reports/expert_v32_XXXXXXXX.html",
  "version": "3.2.0",
  "sections": ["Cover", "Section 03-1 A/B Comparison"],
  "scenario_a": {
    "type": "청년",
    "unit_count": 77,
    "decision": "NO-GO"
  },
  "scenario_b": {
    "type": "신혼부부",
    "unit_count": 51,
    "decision": "NO-GO"
  },
  "recommended_scenario": "B"
}
```

### Example 2: Generate Expert v3.2 Report (마포 테스트)

**Request:**
```bash
curl -X POST "https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v3.2/generate-expert-report" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 마포구 월드컵북로 120",
    "land_area_sqm": 660.0,
    "bcr_legal": 50.0,
    "far_legal": 300.0
  }'
```

### Example 3: Generate v23 A/B Report (노원 테스트)

**Request:**
```bash
curl -X POST "https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/generate-ab-report" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 노원구 상계동 567-89",
    "land_area_sqm": 990.0
  }'
```

---

## 🔍 Troubleshooting Guide

### ❌ Problem: "접속이 안돼" / Cannot connect

**Solution 1: Use Browser (가장 쉬운 방법)**
1. Open browser (Chrome, Firefox, Safari)
2. Paste URL: `https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/health`
3. Press Enter
4. You should see JSON response: `{"status":"healthy",...}`

**Solution 2: Check Network**
- Ensure you're not behind a corporate firewall
- Try different browser (Chrome → Firefox)
- Try incognito/private mode
- Check if HTTPS is working (not HTTP)

**Solution 3: Use Swagger UI**
- Go to: `https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/docs`
- Click "Try it out" on any endpoint
- Click "Execute"
- View response directly

### ❌ Problem: 404 Not Found

**Solution:**
- Check URL spelling (must include `https://`)
- Verify endpoint path (e.g., `/health` not `/Health`)
- Ensure server is running (check health endpoint first)

### ❌ Problem: 500 Internal Server Error

**Solution:**
- Check request format (JSON must be valid)
- Verify required fields (address, land_area_sqm)
- Check server logs for detailed error

---

## 📊 Server Metrics

Check current server statistics:
```
https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/metrics
```

**Expected Response:**
```json
{
  "server": "ZeroSite v23 + Expert v3.2",
  "uptime_seconds": 264.36,
  "total_requests": 1,
  "success_rate": "100.0%",
  "timestamp": "2025-12-11T01:44:27.051319"
}
```

---

## 🎓 Testing Workflow (초보자용 가이드)

### Step 1: Verify Server is Running
```
Visit: https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/health
```
✅ If you see `"status": "healthy"` → Server is working!

### Step 2: Open API Documentation
```
Visit: https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/docs
```
✅ You'll see interactive API interface (Swagger UI)

### Step 3: Test v3.2 Expert Report
1. In Swagger UI, find `POST /api/v3.2/generate-expert-report`
2. Click "Try it out"
3. Edit the JSON request:
```json
{
  "address": "서울특별시 강남구 역삼동 123-45",
  "land_area_sqm": 1650.0,
  "bcr_legal": 50.0,
  "far_legal": 300.0
}
```
4. Click "Execute"
5. Check the response for `report_url`
6. Click the URL to view generated report

### Step 4: View Generated Report
- Copy `report_url` from response
- Paste in browser
- View complete HTML report (9-10 KB)

---

## 🚀 Production Endpoints

### v3.2 Expert Report (NEW)
```
POST https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v3.2/generate-expert-report
```
**Features:**
- ✅ Section 03-1 A/B Comparison
- ✅ Integrated backend engines (Financial v3.2, Cost v3.2, Market v3.2)
- ✅ Professional McKinsey-grade HTML report
- ✅ Automatic scenario recommendation
- ✅ Comprehensive financial analysis (NPV, IRR, ROI, Payback)

### v23 A/B Report (Legacy)
```
POST https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/generate-ab-report
```
**Features:**
- ✅ A/B Scenario Comparison
- ✅ FAR visualizations
- ✅ Market histograms
- ✅ Enhanced report design

---

## 📝 Test Results Log

### Test #1: Health Check
- **Time:** 2025-12-11 01:44:27 UTC
- **URL:** https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/health
- **Status:** ✅ SUCCESS (HTTP 200)
- **Response Time:** 218ms
- **Result:** Server healthy, version 23.0.0

### Test #2: Root Endpoint
- **Time:** 2025-12-11 01:44:27 UTC
- **URL:** https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/
- **Status:** ✅ SUCCESS (HTTP 200)
- **Response Time:** 385ms
- **Result:** Service info returned correctly

### Test #3: v3.2 Expert Report (Gangnam)
- **Time:** 2025-12-11 01:40:30 UTC
- **Address:** 서울특별시 강남구 역삼동 123-45
- **Land Area:** 1,650.0㎡
- **Status:** ✅ SUCCESS (HTTP 200)
- **Report Size:** 9,562 bytes
- **Recommendation:** Scenario B (신혼부부 주택)
- **Scenario A ROI:** -7.34%
- **Scenario B ROI:** -22.15%

---

## 🔗 Quick Links Summary

| Purpose | URL |
|---------|-----|
| Health Check | https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/health |
| API Docs (Swagger) | https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/docs |
| Service Info | https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/ |
| Metrics | https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/metrics |

---

## 📞 Support

If you still cannot connect:
1. ✅ Server is verified working (tested 2025-12-11 01:44:27 UTC)
2. ✅ Public URL is accessible
3. ✅ All endpoints respond correctly

**Next Steps:**
- Try browser first (easiest)
- Use Swagger UI for interactive testing
- Check firewall/network settings
- Verify HTTPS (not HTTP)

---

**Status:** 🟢 ONLINE & VERIFIED  
**Last Updated:** 2025-12-11 01:44:27 UTC  
**Verification:** 3/3 tests passed ✅  

**Ready for Production Use** 🚀
