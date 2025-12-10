# 🔗 ZeroSite v3.2 Access Guide

**Last Updated**: 2025-12-10 23:30 KST  
**Phase**: Phase 1 Complete ✅ | Phase 2 Ready ⏳

---

## 🌐 **Primary Access Points**

### **1. Live Server (Production)**
```
🔗 Public URL: https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai
📊 API Docs: https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/docs
🔌 Port: 8041
🟢 Status: RUNNING (v23.1)
```

### **2. Health Check**
```bash
curl https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "version": "23.0.0",
  "timestamp": "2025-12-10T23:30:00+09:00",
  "uptime_seconds": 3600.0
}
```

---

## 📋 **API Endpoints (Sequential Order)**

### **Endpoint 1: Generate A/B Report (v23.1)**
**Method:** `POST`  
**URL:** `/api/v23/generate-ab-report`  
**Full URL:** `https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/generate-ab-report`

**Request Body:**
```json
{
  "address": "서울특별시 강남구 역삼동 123-45",
  "land_area_sqm": 1650.0
}
```

**cURL Example:**
```bash
curl -X POST \
  https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/generate-ab-report \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 역삼동 123-45",
    "land_area_sqm": 1650.0
  }'
```

**Response Example:**
```json
{
  "status": "success",
  "report_url": "http://localhost:8041/reports/ab_scn_bbfb3f6f_20251210_230022.html",
  "scenario_a_decision": "NO-GO",
  "scenario_b_decision": "NO-GO",
  "recommended_scenario": "B",
  "generation_time_seconds": 0.65
}
```

---

### **Endpoint 2: List Reports**
**Method:** `GET`  
**URL:** `/api/v23/list-reports`  
**Full URL:** `https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/list-reports`

**cURL Example:**
```bash
curl https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/list-reports
```

**Response Example:**
```json
{
  "status": "success",
  "reports": [
    {
      "filename": "ab_scn_bbfb3f6f_20251210_230022.html",
      "url": "/reports/ab_scn_bbfb3f6f_20251210_230022.html",
      "size_bytes": 234567,
      "created_at": "2025-12-10T23:00:22+09:00"
    }
  ],
  "total_count": 4
}
```

---

### **Endpoint 3: Download Report**
**Method:** `GET`  
**URL:** `/api/v23/download-report/{filename}`  
**Full URL:** `https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/download-report/ab_scn_bbfb3f6f_20251210_230022.html`

**cURL Example:**
```bash
curl -O https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/download-report/ab_scn_bbfb3f6f_20251210_230022.html
```

---

## 📊 **Sample Reports (Live Links)**

### **Report 1: Gangnam (강남구) - High Value Area**
```
📍 Address: 서울특별시 강남구 역삼동 123-45
📐 Land Area: 1,650㎡
🔗 URL: https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/reports/ab_scn_bbfb3f6f_20251210_230022.html
📊 Decision: Scenario A (NO-GO), Scenario B (NO-GO), Recommended: B
💰 Market Price: ₩14,216,206/㎡ (HIGH confidence)
```

### **Report 2: Songpa (송파구) - Mid-High Value Area**
```
📍 Address: 서울특별시 송파구 잠실동 456-78
📐 Land Area: 1,800㎡
🔗 URL: https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/reports/ab_scn_f5e85e22_20251210_230023.html
📊 Decision: Scenario A (NO-GO), Scenario B (NO-GO), Recommended: B
💰 Market Price: ~₩12,000,000/㎡ (estimated)
```

### **Report 3: Nowon (노원구) - Mid Value Area**
```
📍 Address: 서울특별시 노원구 상계동 789-12
📐 Land Area: 2,000㎡
🔗 URL: https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/reports/ab_scn_47e7dce0_20251210_230024.html
📊 Decision: Scenario A (NO-GO), Scenario B (NO-GO), Recommended: B
💰 Market Price: ₩6,393,743/㎡ (MEDIUM confidence)
```

---

## 🧪 **Testing Workflow (Sequential Steps)**

### **Step 1: Health Check**
```bash
curl https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/health
```
✅ **Expected:** Status 200, "status": "healthy"

---

### **Step 2: Generate Test Report**
```bash
curl -X POST \
  https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/generate-ab-report \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 역삼동 123-45",
    "land_area_sqm": 1650.0
  }'
```
✅ **Expected:** Status 200, "status": "success", "report_url": "..."

---

### **Step 3: Access Generated Report**
1. Copy the `report_url` from Step 2 response
2. Replace `http://localhost:8041` with `https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai`
3. Open in browser

**Example:**
```
Original: http://localhost:8041/reports/ab_scn_bbfb3f6f_20251210_230022.html
Public:   https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/reports/ab_scn_bbfb3f6f_20251210_230022.html
```

---

### **Step 4: List All Reports**
```bash
curl https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/list-reports
```
✅ **Expected:** List of all generated reports with metadata

---

### **Step 5: Download Report (Optional)**
```bash
curl -O https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/download-report/ab_scn_bbfb3f6f_20251210_230022.html
```
✅ **Expected:** HTML file downloaded to current directory

---

## 🧰 **Backend Testing (Phase 1 Engines)**

### **Test 1: Financial Analysis Engine**
```bash
cd /home/user/webapp && python3 backend/services_v9/financial_analysis_engine.py
```
✅ **Expected Output:**
```
=== Financial Analysis Results (v3.2) ===
Total Investment (CAPEX): 165.5 억원
LH Purchase Price: 138.59 억원
Project Profit: -26.91 억원
ROI: -16.26%
IRR: -10.0%
NPV: -38.35 억원
Decision: NO-GO

✅ All Validation Checks PASSED
```

---

### **Test 2: Cost Estimation Engine**
```bash
cd /home/user/webapp && python3 backend/services_v9/cost_estimation_engine.py
```
✅ **Expected Output:**
```
=== Cost Estimation Results (v3.2) ===
Total Estimated Cost: 180.3 억원

Cost Breakdown:
- Land Acquisition: 62.7 억원 (34.8%)
- Acquisition Tax: 2.8 억원 (1.5%)
- Construction: 88.5 억원 (49.1%)
- Design: 7.1 억원 (3.9%)
...

✅ Sum Verification: PASS
```

---

### **Test 3: Market Data Processor**
```bash
cd /home/user/webapp && python3 backend/services_v9/market_data_processor.py
```
✅ **Expected Output:**
```
=== Market Data Processor Test (v3.2) ===

Test 1: 마포구 (Mapo-gu)
Address: 서울특별시 마포구 월드컵북로 120
Confidence: MEDIUM (500m radius, 11 transactions)
Average Price: ₩9,486,119/㎡

Test 2: 강남구 (Gangnam-gu)
Confidence: HIGH (exact address, 9 transactions)
Average Price: ₩14,216,206/㎡
...
```

---

## 📂 **File Locations (Sequential Access)**

### **Phase 1 Backend Engines**
```
1. /home/user/webapp/backend/services_v9/financial_analysis_engine.py
2. /home/user/webapp/backend/services_v9/cost_estimation_engine.py
3. /home/user/webapp/backend/services_v9/market_data_processor.py
```

### **Documentation Files**
```
1. /home/user/webapp/PHASE_1_COMPLETE_STATUS.md (Main status report)
2. /home/user/webapp/ACCESS_GUIDE_V32.md (This file)
3. /home/user/webapp/ZEROSITE_V23_1_STATUS_REPORT.md (v23.1 details)
4. /home/user/webapp/SESSION_SUMMARY_2025_12_10.md (Session summary)
5. /home/user/webapp/QUICK_REFERENCE_V23_1.md (Quick reference)
```

### **Generated Reports**
```
/home/user/webapp/public/reports/
├── ab_scn_bbfb3f6f_20251210_230022.html (Gangnam)
├── ab_scn_f5e85e22_20251210_230023.html (Songpa)
└── ab_scn_47e7dce0_20251210_230024.html (Nowon)
```

---

## 🚀 **Quick Start (3 Commands)**

### **Option A: Test Everything**
```bash
# 1. Check server health
curl https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/health

# 2. Generate a report
curl -X POST \
  https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/generate-ab-report \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 강남구 역삼동 123-45", "land_area_sqm": 1650.0}'

# 3. List all reports
curl https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/list-reports
```

---

### **Option B: View Sample Reports (Browser)**
```
1. Open: https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/reports/ab_scn_bbfb3f6f_20251210_230022.html
2. Review: A/B Scenario Comparison for Gangnam
3. Check: FAR Chart, Market Histogram, Financial Analysis
```

---

### **Option C: Test Backend Engines (Terminal)**
```bash
# Navigate to webapp
cd /home/user/webapp

# Test all 3 engines sequentially
python3 backend/services_v9/financial_analysis_engine.py
python3 backend/services_v9/cost_estimation_engine.py
python3 backend/services_v9/market_data_processor.py
```

---

## 🔍 **Troubleshooting**

### **Issue 1: Connection Timeout**
**Solution:** Check if server is running
```bash
cd /home/user/webapp && ps aux | grep v23_server
```
**Expected:** Process with `python3 v23_server.py` should be running

---

### **Issue 2: Report URL Returns 404**
**Solution:** Replace localhost with public URL
```
❌ Wrong: http://localhost:8041/reports/...
✅ Correct: https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/reports/...
```

---

### **Issue 3: API Returns 500 Error**
**Solution:** Check server logs
```bash
cd /home/user/webapp && tail -n 50 logs/v23_1_server.log
```

---

## 📋 **Phase Status Overview**

| Phase | Status | Duration | Completion Date |
|-------|--------|----------|-----------------|
| **Phase 1: Backend Fixes** | ✅ COMPLETE | 10 hours | 2025-12-10 |
| **Phase 2: v23 Integration** | ⏳ READY | 10 hours | TBD |
| **Phase 3: GenSpark AI** | ⏳ PLANNED | 10 hours | TBD |

**Total Progress:** 33% (1/3 phases complete)

---

## 🎯 **Next Steps for User**

### **Option 1: Review Phase 1 Results**
1. ✅ Test all 3 backend engines (financial, cost, market)
2. ✅ Review sample reports (Gangnam, Songpa, Nowon)
3. ✅ Verify calculations are realistic (ROI, CAPEX, market data)
4. ✅ Provide feedback on accuracy and completeness

---

### **Option 2: Approve Phase 2 Start**
1. ⏳ Confirm Phase 1 results meet expectations
2. ⏳ Approve start of Phase 2 (A/B template + v23.1 charts)
3. ⏳ Estimated time: 10 hours (1-1.5 days)
4. ⏳ Expected completion: 2025-12-11 or 2025-12-12

---

### **Option 3: Request Modifications**
1. ⏳ Identify specific improvements needed
2. ⏳ Prioritize modifications (critical vs. nice-to-have)
3. ⏳ Provide feedback on Phase 1 implementation
4. ⏳ Suggest timeline adjustments if needed

---

## 📞 **Support & Resources**

- **Project Repository**: https://github.com/hellodesignthinking-png/LHproject
- **Branch**: `genspark_ai_developer`
- **Commit**: `6c15b03` (Phase 1 Complete)
- **Documentation**: See `/home/user/webapp/PHASE_1_COMPLETE_STATUS.md`
- **API Docs**: https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/docs

---

## ⚡ **Key Improvements in Phase 1**

| Metric | Before (v3.0) | After (v3.2 Phase 1) | Status |
|--------|---------------|----------------------|--------|
| ROI Calculation | ❌ 790,918% | ✅ -16.26% | Fixed |
| Market Data | ❌ 0건 | ✅ 9-11 transactions | Fixed |
| Construction Cost | ❌ 300만원/㎡ | ✅ 402.5만원/㎡ | Fixed |
| Cash Flow | ❌ All zeros | ✅ 30-year projection | Fixed |
| CAPEX Consistency | ❌ No validation | ✅ Sum verified | Fixed |

---

**END OF ACCESS GUIDE**

**🔗 Quick Access:** https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai  
**📊 API Docs:** https://8041-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v23/docs  
**✅ Phase 1:** COMPLETE | **⏳ Phase 2:** READY TO START
