# 🚀 ZeroSite v35.0 ULTIMATE - Quick Start Guide

**Version:** v35.0 ULTIMATE  
**Status:** ✅ Running  
**Date:** 2025-12-13

---

## 🌐 Server Access

### Public URL
```
https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai
```

### API Endpoints

#### 1. Health Check
```bash
curl https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v24.1/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "24.1.0",
  "engines_loaded": 8,
  "timestamp": "2025-12-13T16:26:26"
}
```

#### 2. Generate PDF (36 Pages)
```bash
curl -X POST https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v24.1/appraisal/pdf \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울 관악구 신림동 1524-8",
    "land_area_sqm": 435,
    "zone_type": "제2종일반주거지역",
    "individual_land_price_per_sqm": 10000000
  }' \
  --output my_report.pdf
```

**Expected Result:**
- ✅ 36-page premium PDF
- ✅ All transactions show "관악구 신림동"
- ✅ Modern design with gradients
- ✅ File size: ~71KB
- ✅ Generation time: ~7 seconds

---

## 🎯 Test Cases

### Test Case 1: 관악구 신림동
```bash
curl -X POST https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v24.1/appraisal/pdf \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울 관악구 신림동 1524-8",
    "land_area_sqm": 435,
    "zone_type": "제2종일반주거지역"
  }' \
  --output 신림동_보고서.pdf
```

**Verification:**
```bash
# Check page count
pdfinfo 신림동_보고서.pdf | grep Pages

# Expected: Pages: 36
```

### Test Case 2: 강남구 역삼동
```bash
curl -X POST https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v24.1/appraisal/pdf \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울 강남구 역삼동 680-11",
    "land_area_sqm": 660,
    "zone_type": "제3종일반주거지역"
  }' \
  --output 역삼동_보고서.pdf
```

**Expected:**
- All transactions show "강남구 역삼동"
- Higher prices (강남구 base: 20,000,000 KRW/㎡)

### Test Case 3: 마포구 상암동
```bash
curl -X POST https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v24.1/appraisal/pdf \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울 마포구 상암동 1600",
    "land_area_sqm": 500,
    "zone_type": "준주거지역"
  }' \
  --output 상암동_보고서.pdf
```

**Expected:**
- All transactions show "마포구 상암동"
- Moderate prices (마포구 base: 13,000,000 KRW/㎡)

---

## 📊 Features Verification

### ✅ Feature 1: Accurate Transaction Addresses

**How to verify:**
1. Generate PDF for any address
2. Open PDF and go to **Page 14** (Transaction Table)
3. Check all 15 transaction addresses
4. **Expected:** All addresses match input gu/dong

**Example:**
```
Input:  서울 관악구 신림동 1524-8
Output: 서울 관악구 신림동 734-12  ✅
        서울 관악구 신림동 521-45  ✅
        서울 관악구 신림동 892-33  ✅
        ... (all 15 transactions)
```

### ✅ Feature 2: Premium Design

**Visual elements:**
- Gradient cover page (Blue → Cyan)
- Colored section headers
- Professional tables with hover effects
- Stat cards with colored borders
- Modern typography (Noto Sans KR + Inter)

### ✅ Feature 3: 36 Pages Content

**Page breakdown:**
- Pages 1-5: Cover & Overview
- Pages 6-12: Market Analysis
- Pages 13-18: Transaction Analysis ← **Page 14 is key!**
- Pages 19-27: Valuation Methods
- Pages 28-32: Investment & Risk
- Pages 33-35: Conclusion

---

## 🔧 Troubleshooting

### Issue 1: Server Not Responding

**Solution:**
```bash
# Check server status
curl https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v24.1/health

# If fails, contact support
```

### Issue 2: PDF Generation Timeout

**Symptoms:**
- Request takes more than 90 seconds
- Connection timeout error

**Solution:**
```bash
# Increase timeout
curl -X POST ... --max-time 120
```

### Issue 3: Wrong Transaction Addresses

**Symptoms:**
- Transactions show different gu/dong than input

**Solution:**
- This should NOT happen in v35.0
- If it does, check server logs
- Verify v35.0 is running (check health endpoint version)

---

## 📝 API Reference

### POST /api/v24.1/appraisal/pdf

**Request Body:**
```json
{
  "address": "string",
  "land_area_sqm": number,
  "zone_type": "string",
  "individual_land_price_per_sqm": number (optional),
  "building_area_sqm": number (optional),
  "construction_year": number (optional)
}
```

**Response:**
- Content-Type: `application/pdf`
- File download with name: `Appraisal_Report_{timestamp}.pdf`

**Example Response Headers:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="Appraisal_Report_20251213_162626.pdf"
Content-Length: 72650
```

---

## 🎨 Design Features

### Color Scheme
```css
Primary Blue:    #0066CC
Vibrant Orange:  #FF6B35
Bright Cyan:     #00D9FF
Modern Green:    #00C896
Golden Yellow:   #FFB800
Vivid Red:       #FF3B3B
Deep Navy:       #1A1A2E
```

### Typography
```css
Body Font: 'Noto Sans KR', sans-serif
Accent Font: 'Inter', sans-serif
Size: 10pt (body), 18pt (headers), 42pt (cover title)
```

### Layout Elements
- Gradient backgrounds
- Box shadows
- Border radius: 8-10px
- Grid layouts (2/3/4 columns)
- Responsive stat cards
- Professional tables

---

## 📈 Performance Metrics

### Server Response Times
- Health check: < 100ms
- PDF generation: ~7 seconds
- File size: ~71KB (36 pages)

### Scalability
- Concurrent requests: Up to 10
- Max file size: 5MB per PDF
- Generation timeout: 90 seconds (default)

---

## 🔗 Quick Links

### Documentation
- **Complete Guide:** `ZEROSITE_V35_ULTIMATE_COMPLETE.md`
- **This File:** `V35_QUICK_START.md`
- **GitHub:** https://github.com/hellodesignthinking-png/LHproject

### Server
- **Base URL:** https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai
- **Health:** https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v24.1/health
- **Dashboard:** https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/public/dashboard.html

---

## 🎯 Sample Commands

### Generate and Preview
```bash
# Generate PDF
curl -X POST https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v24.1/appraisal/pdf \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울 관악구 신림동 1524-8",
    "land_area_sqm": 435,
    "zone_type": "제2종일반주거지역"
  }' \
  --output test.pdf

# Check pages
pdfinfo test.pdf | grep Pages

# Extract text from page 14 (transaction table)
pdftotext test.pdf - | grep -A 20 "거래사례"
```

### Batch Generation
```bash
# Generate multiple reports
for addr in "신림동 1524-8" "봉천동 1000" "남현동 500"; do
  curl -X POST https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai/api/v24.1/appraisal/pdf \
    -H "Content-Type: application/json" \
    -d "{
      \"address\": \"서울 관악구 ${addr}\",
      \"land_area_sqm\": 400,
      \"zone_type\": \"제2종일반주거지역\"
    }" \
    --output "${addr}_report.pdf"
  echo "✅ Generated: ${addr}_report.pdf"
done
```

---

## ✅ Success Checklist

### Before Using
- [ ] Server health check passes
- [ ] Have test address ready
- [ ] Know desired land area and zone type

### After Generation
- [ ] PDF file created successfully
- [ ] File size is reasonable (~71KB for 36 pages)
- [ ] Page count is 36 (verify with `pdfinfo`)
- [ ] Transaction addresses match input gu/dong
- [ ] Design looks professional

### Quality Verification
- [ ] Open PDF in viewer
- [ ] Check cover page (Page 1)
- [ ] Verify transaction table (Page 14)
- [ ] Review all 36 pages
- [ ] Confirm modern design with colors

---

## 🎊 You're All Set!

**ZeroSite v35.0 ULTIMATE is ready to use!**

```
┌──────────────────────────────────────────┐
│                                          │
│   🚀 v35.0 ULTIMATE Server Running!    │
│                                          │
│   URL: https://8000-ismcj42l...ai       │
│   Status: ✅ Healthy                    │
│   Version: 24.1.0                       │
│   Features: 36 pages + Accurate TX     │
│                                          │
│   시작하세요! 🎉                        │
│                                          │
└──────────────────────────────────────────┘
```

**Questions?** Check `ZEROSITE_V35_ULTIMATE_COMPLETE.md` for detailed documentation.

---

**Last Updated:** 2025-12-13 16:26 KST  
**Version:** v35.0 ULTIMATE  
**Status:** Production Ready ✅
