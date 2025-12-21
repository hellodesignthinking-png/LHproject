# M1 Integration Tests - Quick Reference

**Purpose**: Verify M1 Lock validation and API failure bypass  
**Duration**: ~15 minutes for all 5 tests  
**Prerequisites**: Backend + Frontend running

---

## 🚀 Setup

### **Backend**
```bash
cd /home/user/webapp
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Verify**: http://localhost:8000/health → `{"status": "healthy"}`

### **Frontend**
```bash
cd /home/user/webapp/frontend
npm run dev
```

**Verify**: http://localhost:3000/pipeline → M1 Landing Page loads

---

## 🧪 Test Case 1: Happy Path (API Success)

**Goal**: Verify complete M1 Lock flow with API success

**Steps**:
1. Open http://localhost:3000/pipeline
2. **STEP 1**: Enter address → Select from dropdown
3. **STEP 2**: Verify geocoding → Coordinates shown
4. **STEP 3**: Verify cadastral data loaded automatically
5. **STEP 4**: Verify land use data loaded
6. **STEP 5**: Verify road info loaded
7. **STEP 6**: Check market data (optional)
8. **STEP 7**: Review data summary
9. **STEP 8**: Verify Lock button **ENABLED** (purple gradient)
10. Click "🔒 분석 시작 (M1 Lock)"

**Expected Results**:
- ✅ All steps complete without errors
- ✅ Step 8 shows complete data summary
- ✅ Lock button enabled (purple gradient)
- ✅ Success message: "분석용 컨텍스트가 확정되었습니다"
- ✅ Context ID + Parcel ID displayed
- ✅ Confidence score shown (e.g., 85%)
- ✅ Pipeline diagram shown
- ✅ Button: "M2 감정평가 시작 →"

**Pass Criteria**: All ✅ above met

---

## 🧪 Test Case 2: Missing Required Fields

**Goal**: Verify Lock button disabled when fields missing

**Steps**:
1. Open http://localhost:3000/pipeline
2. **STEP 1**: Enter address → Select
3. **STEP 2**: Verify geocoding
4. **SKIP STEP 3-6**: Don't fill any data
5. Go directly to **STEP 8**

**Expected Results**:
- ❌ Error box shown (orange background)
- ❌ Title: "필수 항목 누락"
- ❌ Missing fields list shown (e.g., "본번", "토지면적", "용도지역", "FAR", "BCR", "도로 폭")
- ❌ Lock button **DISABLED** (gray)
- ❌ Button text: "❌ 입력 완료 필요"
- ⚠️ Tooltip on hover shows missing fields

**Pass Criteria**: Lock button disabled, error box clear

---

## 🧪 Test Case 3: Invalid Values (Zero)

**Goal**: Verify backend rejects invalid values

**Steps**:
1. Open http://localhost:3000/pipeline
2. Complete STEP 1-2 normally
3. **STEP 3**: Manually enter:
   - bonbun: "100"
   - bubun: "1"
   - jimok: "대지"
   - area: "0" ← **INVALID**
4. Complete STEP 4-6 normally
5. Go to STEP 8
6. Try to click Lock button

**Expected Results**:
- ❌ Lock button **DISABLED** (gray)
- ❌ Error: "토지면적" in missing fields list
- ❌ Button text: "❌ 입력 완료 필요"

**Alternative**: If Lock button is enabled (frontend bug), backend should reject:
```bash
# Direct API test
curl -X POST http://localhost:8000/api/m1/freeze-context-v2 \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울 강남구", "road_address": "테헤란로 123",
    "coordinates": {"lat": 37.5, "lon": 127.0},
    "sido": "서울", "sigungu": "강남구", "dong": "역삼동",
    "bonbun": "100", "bubun": "1", "jimok": "대지", 
    "area": 0,
    "zone_type": "제2종일반주거지역", "land_use": "주거용",
    "far": 200, "bcr": 60, "road_width": 8, "road_type": "중로"
  }'
```

**Expected Backend Response**:
```json
{
  "detail": {
    "message": "필수 입력값이 누락되었거나 유효하지 않습니다",
    "validation_errors": [
      "면적 (area)은 0보다 커야 합니다"
    ]
  }
}
```

**Pass Criteria**: Frontend blocks OR backend rejects with HTTP 400

---

## 🧪 Test Case 4: API Failure → Auto-Retry

**Goal**: Verify auto-retry mechanism (if API fails)

**Note**: This test requires simulating API failure. If all APIs succeed, this test can be SKIPPED.

**Steps** (if API fails):
1. Open http://localhost:3000/pipeline
2. Complete STEP 1-2
3. **STEP 3**: Wait for API call
4. If API fails, observe:
   - Loading indicator
   - Auto-retry after 1 second
   - If retry fails, error box appears

**Expected Results**:
- 🔄 Loading indicator shows
- 🔄 Auto-retry attempted (1 second delay)
- ⚠️ If retry fails, error box shown (orange)
- ⚠️ Error message: "API 조회 실패: [error details]"
- ⚠️ 3 bypass buttons shown:
  - 🔄 재시도 (blue)
  - 📄 PDF 업로드 (orange)
  - ✏️ 수동 입력 (purple)

**Pass Criteria**: Auto-retry attempted, bypass options shown

---

## 🧪 Test Case 5: API Failure → Bypass Options

**Goal**: Verify all 3 bypass options work

**Prerequisites**: Test Case 4 completed (API failed, bypass shown)

### **Option A: Manual Retry** 🔄

**Steps**:
1. Click "🔄 재시도" button
2. Wait for API call

**Expected**:
- ✅ API call re-attempted
- ✅ If success, data loaded
- ✅ If fail, bypass options shown again

---

### **Option B: PDF Upload** 📄

**Steps**:
1. Click "📄 PDF 업로드" button
2. Upload mode enabled
3. Select a cadastral PDF file
4. Wait for OCR processing

**Expected**:
- ✅ PDF upload input shown
- ✅ OCR extracts data (bonbun, bubun, jimok, area)
- ✅ Extracted data fills form fields
- ✅ Data source badge shows "PDF OCR"
- ✅ Confidence score shown (if available)
- ✅ Can proceed to next step

---

### **Option C: Manual Input** ✏️

**Steps**:
1. Click "✏️ 수동 입력" button
2. Manual input mode enabled
3. Fill all fields manually:
   - bonbun: "100"
   - bubun: "1"
   - jimok: Select "대지"
   - area: "500.5"
4. Click "다음" button

**Expected**:
- ✅ Manual input form shown
- ✅ All fields editable
- ✅ Data source badge shows "MANUAL"
- ✅ Can proceed to next step

---

## 📊 Test Results Template

Use this template to record test results:

```markdown
## M1 Integration Test Results

**Date**: YYYY-MM-DD  
**Tester**: [Your Name]  
**Environment**: Local / Staging / Production

| Test Case | Status | Notes |
|-----------|--------|-------|
| 1. Happy Path | ✅ PASS / ❌ FAIL | |
| 2. Missing Fields | ✅ PASS / ❌ FAIL | |
| 3. Invalid Values | ✅ PASS / ❌ FAIL | |
| 4. Auto-Retry | ✅ PASS / ❌ FAIL / ⏭️ SKIP | |
| 5. Bypass Options | ✅ PASS / ❌ FAIL / ⏭️ SKIP | |

**Overall**: ✅ ALL PASS / ❌ ISSUES FOUND

**Issues** (if any):
- [List any issues found]

**Recommendations**:
- [Any recommendations for improvement]
```

---

## 🐛 Troubleshooting

### **Issue**: Lock button always disabled
**Solution**: Check browser console for errors. Verify all required fields have non-zero values.

### **Issue**: API calls fail
**Solution**: Verify backend is running on port 8000. Check backend logs.

### **Issue**: Frontend not loading
**Solution**: Verify frontend is running on port 3000. Check for npm errors.

### **Issue**: Backend validation not working
**Solution**: Check `/api/m1/freeze-context-v2` endpoint. Verify request payload.

---

## 🎯 Success Criteria

**M1 Stabilization is successful if**:

- ✅ Test 1 (Happy Path): PASS
- ✅ Test 2 (Missing Fields): PASS
- ✅ Test 3 (Invalid Values): PASS
- ✅ Test 4 (Auto-Retry): PASS or SKIP (if API succeeds)
- ✅ Test 5 (Bypass): PASS or SKIP (if API succeeds)

**Minimum Requirement**: Tests 1, 2, 3 must PASS

---

## 📝 Next Steps After Testing

If all tests pass:
1. ✅ Mark PR #11 as ready for review
2. ✅ Deploy to staging environment
3. ✅ Conduct user acceptance testing
4. ✅ Prepare for production deployment

If issues found:
1. ❌ Document issues in PR comments
2. ❌ Fix issues and retest
3. ❌ Update PR with fixes

---

**Contact**: ZeroSite Development Team  
**Version**: 1.0  
**Last Updated**: 2025-12-17
