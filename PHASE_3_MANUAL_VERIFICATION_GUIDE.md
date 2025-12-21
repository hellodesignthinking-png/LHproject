# 🔍 Phase 3: Manual Verification Guide

**Generated**: 2025-12-20 01:47 UTC  
**Status**: ⚠️ **USER ACTION REQUIRED**  
**Estimated Time**: 30 minutes

---

## 🌐 Service URLs

### Frontend (React UI)
```
https://3000-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai
```

### Backend (API Server)
```
https://8005-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai
```

### Test PDFs Location
```
/home/user/webapp/temp/
```

---

## 📋 Phase 3 Checklist (4 Items)

### ✅ 1. M6 Score Consistency Verification

**Objective**: Verify M6 PDF shows consistent scores (NO `0.0/110` bugs)

**Test Files**:
- `test_m6_iteration_1_1766194751.pdf` (232KB)
- `test_m6_iteration_5_1766194757.pdf` (232KB)
- `test_m6_iteration_10_1766194763.pdf` (232KB)

**What to Check**:

1. **First Page - Cover/Executive Summary**
   - [ ] "종합 점수" shows format: `X.X/110점` (e.g., `85.0/110점`)
   - [ ] Score is NOT `0.0/110` ❌
   - [ ] Score matches expected range (0-110)

2. **Internal Sections - Score Breakdown**
   - [ ] All sections reference the same total score
   - [ ] No conflicting scores (e.g., page 1 shows 85.0, page 5 shows 0.0)
   - [ ] Radar chart uses consistent values

3. **Footer Section - Final Judgment**
   - [ ] Final score summary matches cover page
   - [ ] Decision logic is based on correct score

**Expected Result**: ✅ All M6 scores are consistent throughout the PDF

**If Failed**: ❌ Report exact page numbers and conflicting values

---

### ✅ 2. M4 FAR/BCR Display Verification

**Objective**: Verify M4 PDF shows `N/A (검증 필요)` instead of `0%` for missing data

**Test Files**:
- `test_m4_iteration_1_1766194736.pdf` (171KB)
- `test_m4_iteration_5_1766194742.pdf` (171KB)
- `test_m4_iteration_10_1766194749.pdf` (171KB)

**What to Check**:

1. **Legal FAR/BCR Section** (법정 용적률/건폐율)
   - [ ] If data is missing, shows: `N/A (검증 필요)` ✅
   - [ ] Does NOT show: `0%` ❌
   - [ ] Includes explanatory text about why data is N/A

2. **Scenario Comparison Tables**
   - [ ] Missing values show `N/A` or `-` or explanatory text
   - [ ] Zero values (if meaningful) show `0%` with context
   - [ ] Clear distinction between "missing" vs "zero"

3. **Parking Analysis**
   - [ ] Parking scenarios properly displayed
   - [ ] No confusing `0` values without explanation

**Expected Result**: ✅ Missing data shows `N/A (검증 필요)`, not `0%`

**If Failed**: ❌ Screenshot the section showing `0%` and report

---

### ✅ 3. Design System Consistency

**Objective**: Verify all PDFs follow unified ZeroSite design system

**Test Files to Compare**:
- M4: `test_m4_iteration_1_1766194736.pdf`
- M6: `test_m6_iteration_1_1766194751.pdf`

**What to Check**:

1. **Typography / Fonts**
   - [ ] Both use `NanumBarunGothic` (나눔바른고딕)
   - [ ] Korean text renders properly (no � characters)
   - [ ] Font sizes are consistent (H1, H2, Body)

2. **Color Palette**
   - [ ] Primary Deep Navy: `#1E3A8A` (titles, headers)
   - [ ] Secondary Gray: `#666666`, `#999999` (body text)
   - [ ] Accent Cyan: `#06B6D4` (highlights, links)
   - [ ] Background: Light Gray `#F2F4F8` (tables, boxes)

3. **Layout & Spacing**
   - [ ] Same page margins (Top/Bottom: 25mm, Left/Right: 22mm)
   - [ ] Consistent section spacing
   - [ ] Same header/footer heights

4. **Table Styles**
   - [ ] Header background color matches
   - [ ] Border styles are identical
   - [ ] Cell padding is consistent
   - [ ] Alternating row backgrounds (if applicable)

5. **Visual Elements**
   - [ ] Both have watermark "ZEROSITE" (5-7% opacity, diagonal)
   - [ ] Same logo/branding placement
   - [ ] Consistent chart/graph styles

**Expected Result**: ✅ M4 and M6 PDFs look like they're from the same design system

**If Failed**: ❌ Note specific differences (font, color hex code, spacing)

---

### ✅ 4. Footer Verification

**Objective**: Verify correct copyright footer on all pages

**Test Files**:
- Any M4 PDF
- Any M6 PDF

**What to Check**:

1. **Footer Text** (모든 페이지 하단)
   - [ ] Shows: `© ZEROSITE by Antenna Holdings | nataiheum` ✅
   - [ ] Does NOT show: `Na Tae-heum` ❌ (old incorrect name)

2. **Footer Placement**
   - [ ] Appears on all pages (including cover)
   - [ ] Consistent position (center or left/right)
   - [ ] Readable font size

3. **Footer Styling**
   - [ ] Subtle color (e.g., gray)
   - [ ] Does not obscure content
   - [ ] Professional appearance

**Expected Result**: ✅ Footer shows `nataiheum` on all pages

**If Failed**: ❌ Screenshot any page showing incorrect name

---

## 🔧 How to Access Test PDFs

### Method 1: Download from Backend API (Recommended)

Open in browser:
```
https://8005-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai/api/v4/reports/M4/pdf?context_id=test-phase1-20251219

https://8005-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai/api/v4/reports/M6/pdf?context_id=test-phase1-20251219
```

This will download fresh PDFs using the current test data.

### Method 2: Access Pre-Generated PDFs

If you have SSH/terminal access:
```bash
cd /home/user/webapp/temp
ls -lh test_m*.pdf

# Open specific file
open test_m4_iteration_1_1766194736.pdf
open test_m6_iteration_1_1766194751.pdf
```

### Method 3: Use Frontend UI (Full Integration Test)

1. Open frontend: `https://3000-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai`
2. Navigate to Pipeline page
3. Click "Generate 6 Reports" button
4. After generation, click individual PDF download buttons (M2-M6)
5. Verify downloaded PDFs match the checklist

---

## 📊 Verification Results Template

Copy and fill out this template after testing:

```markdown
## Phase 3 Manual Verification Results

**Tester**: [Your Name]  
**Date**: 2025-12-20  
**Duration**: [Actual time spent]

### 1. M6 Score Consistency
- [ ] ✅ PASS / [ ] ❌ FAIL
- Notes: 

### 2. M4 FAR/BCR Display
- [ ] ✅ PASS / [ ] ❌ FAIL
- Notes:

### 3. Design System Consistency
- [ ] ✅ PASS / [ ] ❌ FAIL
- Notes:

### 4. Footer Verification
- [ ] ✅ PASS / [ ] ❌ FAIL
- Notes:

### Overall Assessment
- [ ] ✅ ALL TESTS PASSED - Ready for PR merge
- [ ] ❌ ISSUES FOUND - Requires fixes

### Issues/Screenshots
[Paste screenshots or detailed descriptions of any issues]
```

---

## 🚨 Common Issues to Watch For

### M6 Score Issues
- ❌ `0.0/110점` appears anywhere
- ❌ Conflicting scores (e.g., cover shows 85, detail shows 0)
- ❌ Score exceeds 110 points
- ❌ Negative scores

### M4 Display Issues
- ❌ `0%` shown for missing FAR/BCR data
- ❌ `0세대` shown without explanation
- ❌ Parking calculations show `0대` without context

### Design Issues
- ❌ Different fonts between M4 and M6
- ❌ Misaligned tables or text
- ❌ Wrong colors (not matching theme)
- ❌ Missing watermark

### Footer Issues
- ❌ Old name `Na Tae-heum` still appears
- ❌ Footer missing on some pages
- ❌ Incorrect company name

---

## ✅ Success Criteria

**ALL 4 items must PASS** to proceed to PR merge:

1. ✅ M6 scores are consistent (no `0.0/110`)
2. ✅ M4 shows `N/A` for missing data (not `0%`)
3. ✅ Design system is unified (fonts, colors, layout)
4. ✅ Footer shows correct name (`nataiheum`)

**If ANY item FAILS**: Report to development team with screenshots

---

## 📞 Support

If you encounter issues during verification:

1. **Take Screenshots**: Capture exact page and section showing the issue
2. **Note Page Numbers**: Specify which page has the problem
3. **Report Context**: Include context_id and module (M4/M6)
4. **Expected vs Actual**: Describe what you expected vs what you saw

**GitHub Issue**: Create issue in https://github.com/hellodesignthinking-png/LHproject/issues  
**PR Comments**: Comment directly on PR #11

---

## 🎯 After Verification

Once ALL 4 items PASS:

1. ✅ Update PR #11 with verification results
2. ✅ Approve PR for merge
3. ✅ Notify team that Phase 3 is complete
4. ⏭️ Proceed to PR merge and deployment

---

**© ZEROSITE by Antenna Holdings | nataiheum**  
**Document Version**: 1.0  
**Status**: ⚠️ **PENDING USER VERIFICATION**  
**Last Updated**: 2025-12-20 01:47 UTC
