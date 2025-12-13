# ✅ ZeroSite v29.0 - Quick Testing Checklist

**Service URL**: https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai  
**Status**: 🟢 **LIVE & READY**  
**Date**: 2025-12-13

---

## 🚀 Quick Start - Test in 5 Minutes

### Step 1: Open the Site
👉 **Click**: https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai

---

### Step 2: Navigate to Appraisal Tab
1. Click **"감정평가"** tab (3rd tab from left)
2. You'll see the input form on the left side

---

### Step 3: Test Address #1 - Mapo (Primary Test Case)

**Enter These Values**:
```
주소: 서울 마포구 월드컵북로 120
대지면적: 660
```

**What to Look For** ✅:

#### A. Data Loading (Progress Section)
- [ ] See: "개별공시지가 조회 중..." with spinner
- [ ] See: "용도지역 확인 중..." with spinner
- [ ] Should show: **"개별공시지가 조회 완료: 15,000,000 원/㎡ (실제시세데이터_마포구_상암동)"**
- [ ] Should show: **"용도지역 확인 완료: 제2종일반주거지역 (건폐율 60%, 용적률 200%)"**

❌ **If you see old fallback values**:
- 10,000,000 원/㎡ → WRONG (should be 15,000,000)
- 제3종일반주거지역 → WRONG (should be 제2종)

#### B. Final Result Display (After clicking "감정평가 실행")
Look for these **NEW ENHANCED SECTIONS**:

**1. 사용된 데이터 (Blue Box)**
- [ ] 개별공시지가: **15,000,000 원/㎡** ✅
- [ ] 용도지역: **제2종일반주거지역** ✅
- [ ] 대지면적: 660 ㎡
- [ ] 주소: 서울 마포구 월드컵북로 120

**2. 최종 감정평가액 (Green Gradient Box)**
- [ ] Large value displayed (e.g., "160.53 억원")
- [ ] Per-sqm value shown (e.g., "24,322,500 원/㎡")
- [ ] Confidence badge ("신뢰도: LOW/MEDIUM/HIGH")

**3. 3가지 평가법 (Enhanced Cards with Gradients)** 🆕
Each approach should now show:
- [ ] **원가법 (Blue gradient card)**:
  - Value in billions (e.g., "99.00 억원")
  - Detailed breakdown box with:
    - 토지가격 calculation
    - 위치보정 factor
  - Weight applied (e.g., "50% 적용 → XX억원 반영")

- [ ] **거래사례비교법 (Green gradient card)**:
  - Value in billions
  - Transaction count (e.g., "0건 분석")
  - Average comparable price
  - Weight applied

- [ ] **수익환원법 (Purple gradient card)**:
  - Value in billions
  - Cap rate (4.5%)
  - Applicable zone type
  - Weight applied

**4. 시장 분석 (Market Analysis - Amber/Orange Box)** 🆕 ⭐
This is NEW - Look for:
- [ ] Section header: "시장 분석 (Market Analysis)"
- [ ] **가격 적정성** subsection:
  - Evaluation vs market average
  - Market differential percentage
  - "적정 범위" badge
- [ ] **투자 적격성** subsection:
  - Star rating (4-5 stars: ⭐⭐⭐⭐⭐)
  - Checklist with green checkmarks
  - Strengths listed

**5. 투자 추천 의견 (Investment Recommendation - Indigo/Blue Box)** 🆕 ⭐
This is NEW - Look for:
- [ ] Section header: "투자 추천 의견"
- [ ] **종합 평가** badge: "투자 적격 (Grade A-)"
- [ ] Description text (varies by zone type)
- [ ] **2x2 grid**:
  - Green box: "✅ 강점" (Strengths)
  - Yellow box: "⚠️ 유의사항" (Considerations)
- [ ] **Blue recommendation box**:
  - "💡 추천 전략"
  - Priority strategies listed

**6. 프리미엄 분석 (Enhanced Premium - Orange/Yellow Gradient)** 🆕 ⭐
If premium exists, look for:
- [ ] Large percentage display (e.g., "+25.0%")
- [ ] Information badge: "상위 5개 요인 합계의 50% 보수적 적용"
- [ ] **Individual factor cards** (white cards with):
  - Numbered badges (1-5)
  - Factor name
  - Percentage value
  - Description text (e.g., "정방형에 가까워 건축 효율성 극대화")
- [ ] **Calculation box** showing:
  - Top 5 sum
  - 50% application
  - Final premium

**7. 법규 및 규제 정보 (Legal & Regulatory - Gray Box)** 🆕 ⭐
This is NEW - Look for:
- [ ] Section header: "법규 및 규제 정보"
- [ ] **용도지역 규제** subsection:
  - Zone type badge (e.g., "제2종일반주거지역")
  - 2x2 grid showing:
    - 법정 건폐율: 60% (396㎡)
    - 법정 용적률: 200% (1,320㎡)
    - 최대 층수: 21층 이하
    - 주차장: 세대당 1.0대 이상
- [ ] **개발 가능 용도** subsection:
  - Checkmarks for permitted uses
  - Grayed out for restricted uses

**8. 중요 고지사항 (Enhanced Disclaimer - Yellow/Amber Gradient)** 🆕
- [ ] Warning icon
- [ ] Professional disclaimer text
- [ ] Mentions "AI 기반", "법적 효력", "감정평가사"

---

### Step 4: Test PDF Download
1. Click **"상세 감정평가 보고서 PDF 다운로드"** button
2. Wait for PDF generation (may take 10-30 seconds)
3. PDF should download automatically

**Verify PDF Content**:
- [ ] PDF opens successfully
- [ ] Shows same 15,000,000 원/㎡ (NOT 10,000,000)
- [ ] Shows same 제2종일반주거지역 (NOT 제3종)
- [ ] PDF matches screen display

---

### Step 5: Test HTML Preview 🆕
1. Click **"HTML 미리보기"** button
2. Wait for data loading
3. New window should open with HTML preview

**Verify HTML Preview**:
- [ ] Preview window opens (check popup blocker if not)
- [ ] Shows same data as screen
- [ ] All sections visible
- [ ] Formatting looks good

---

## 🧪 Additional Test Addresses

### Test #2: Gangnam (High-Value Commercial)
```
주소: 서울 강남구 테헤란로 427
대지면적: 660
```

**Expected Results**:
- [ ] 개별공시지가: **22,000,000 원/㎡**
- [ ] 용도지역: **준주거지역** (NOT 제2종 or 제3종)
- [ ] 건폐율: 70%
- [ ] 용적률: 400%
- [ ] District overlay: "지구단위계획구역"

---

### Test #3: Songpa (Jamsil Area)
```
주소: 서울 송파구 잠실동 19-1
대지면적: 660
```

**Expected Results**:
- [ ] 개별공시지가: **18,000,000 원/㎡**
- [ ] 용도지역: **제3종일반주거지역**
- [ ] 건폐율: 50%
- [ ] 용적률: 250%

---

## 📊 Visual Design Checklist

### Overall Design Quality:
- [ ] Professional gradients on cards (from-X-50 to-X-100)
- [ ] Shadows and borders visible (border-2, shadow-md)
- [ ] Icons present (Font Awesome: fas fa-X)
- [ ] Hover effects work (cards lift slightly)
- [ ] Color coding consistent:
  - Blue for cost approach
  - Green for sales comparison
  - Purple for income approach
  - Orange/Yellow for premium
  - Amber for market analysis
  - Indigo for recommendations
  - Gray for legal info

### Typography Quality:
- [ ] Large headings (text-lg, text-xl)
- [ ] Bold emphasis (font-bold, font-semibold)
- [ ] Good contrast (readable text)
- [ ] Icons aligned with text

---

## ❌ Common Issues & Solutions

### Issue 1: Still Seeing Old Fallback Values
**Symptoms**:
- 개별공시지가: 10,000,000 (should be 15,000,000)
- 용도지역: 제3종일반주거지역 (should be 제2종)

**Solution**:
1. Hard refresh browser: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. Clear browser cache
3. Try incognito/private window

---

### Issue 2: API Errors
**Symptoms**:
- Error message: "용도지역 정보를 가져올 수 없습니다"
- Error message: "개별공시지가 정보를 가져올 수 없습니다"

**This is GOOD** - It means:
- ✅ Fallback values are NOT being used
- ✅ System is properly failing when API has issues
- ✅ User sees clear error instead of wrong calculation

**Solution**:
1. Check server logs: `tail -20 /home/user/webapp/server.log`
2. Try a different address
3. Wait a moment and retry

---

### Issue 3: PDF Download Fails
**Symptoms**:
- PDF doesn't download
- Error message appears

**Solution**:
1. Try HTML preview button instead
2. Check browser console for errors (F12)
3. Verify PDF generation endpoint is working

---

### Issue 4: Missing New Sections
**Symptoms**:
- Don't see "시장 분석" section
- Don't see "투자 추천 의견" section
- Don't see "법규 및 규제 정보" section

**Solution**:
1. Hard refresh: `Ctrl+Shift+R`
2. Check that `/public/dashboard.html` was updated
3. Check git commit: `git log --oneline -5`

---

## ✅ Success Criteria

### All Tests Pass When:
1. ✅ **Data Accuracy** (Test Address: 마포구 월드컵북로 120):
   - Shows 15,000,000 원/㎡ (NOT 10M or 8.5M)
   - Shows 제2종일반주거지역 (NOT 제3종)
   - Data source visible: "실제시세데이터_마포구_상암동"

2. ✅ **Design Quality**:
   - Professional gradients visible
   - Icons displayed properly
   - Hover effects work
   - Color coding consistent

3. ✅ **Content Richness**:
   - All 5 NEW sections visible:
     1. Detailed calculation breakdowns
     2. Enhanced premium analysis
     3. Market analysis
     4. Investment recommendations
     5. Legal & regulatory information
   - Descriptions and explanations present
   - Not just values, but context and rationale

4. ✅ **Functionality**:
   - PDF download works
   - HTML preview works
   - No errors in console
   - All 3 test addresses return correct data

---

## 📞 Need Help?

### Debugging Commands:
```bash
# Check server status
ps aux | grep uvicorn

# Check server logs
cd /home/user/webapp && tail -50 server.log

# Test API directly
curl -X POST "http://localhost:8000/api/v24.1/land-price/official" \
  -H "Content-Type: application/json" \
  -d '{"address": "서울 마포구 월드컵북로 120"}'

# Check recent commits
cd /home/user/webapp && git log --oneline -10
```

### Documentation Files:
- `V29_ALL_PHASES_COMPLETE.md` - Complete project summary
- `PHASE_5_TEST_RESULTS.md` - Detailed test results
- `PHASE_6_7_DESIGN_CONTENT_PLAN.md` - Design & content plan
- `V29_CRITICAL_FIX_COMPLETE.md` - Bug fix details
- `V29_USER_TESTING_GUIDE.md` - Comprehensive testing guide

---

## 🎉 Expected Experience

**When everything works correctly, you should see**:
1. 🎨 **Beautiful Design**: Professional gradients, shadows, icons
2. 📊 **Rich Content**: Not just numbers, but explanations and context
3. 💯 **Accurate Data**: Real market prices from actual data sources
4. 📈 **Market Insights**: Analysis, recommendations, legal information
5. 🚀 **Smooth UX**: Fast loading, clear progress, helpful errors

**This should feel like a professional real estate appraisal platform!** ⭐

---

**Service URL**: https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai

**Happy Testing!** 🚀✨
