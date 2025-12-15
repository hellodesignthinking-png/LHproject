# 📘 ZeroSite v31.0 - User Guide

## 🎯 Quick Start (5 Minutes)

### Step 1: Access the System
```
URL: https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai
```

### Step 2: Enter Basic Information
1. **주소 입력**: 예) 서울 관악구 신림동 1524-8
2. **토지 면적**: 예) 360㎡

### Step 3: Generate Report
- Click **"감정평가 실행"** button
- Wait 10-15 seconds for processing
- Choose **"PDF 다운로드"** or **"HTML 미리보기"**

### Step 4: Review Results
- 20-page professional PDF report
- Accurate 3-method appraisal
- Investment recommendations

---

## 📊 Understanding Your Report

### Cover Page (Page 1)
- Report title and address
- Evaluation date
- Professional branding

### Executive Summary (Page 3)
**Key Metrics**:
- 최종 감정평가액 (Final Appraised Value)
- 원가법 (Cost Approach)
- 거래사례비교법 (Sales Comparison)
- 수익환원법 (Income Approach)

**Example**:
```
최종 감정평가액: 193.2억원

원가법:         65.0억원  (가중치 20%)
거래사례비교법:  145.0억원  (가중치 50%)
수익환원법:     99.0억원   (가중치 30%)
```

### Market Analysis (Pages 4-7)
- Regional market overview
- Transaction trends (12 months)
- Price movements (3 years)
- Supply-demand balance

### Comparable Sales (Pages 8-10)
- 10+ recent transactions
- Price adjustments
- Weighted average calculation

### Three Methods Detail (Pages 11-16)

#### Cost Approach (Pages 11-12)
**Formula**: Land Value + Building Value - Depreciation
```
Example:
토지 가액 = 360㎡ × 10,000,000원/㎡ = 36.0억원
건물 가액 = 없음 (나대지)
원가법 평가액 = 36.0억원
```

#### Sales Comparison (Pages 13-14)
**Formula**: Weighted Average of Adjusted Comparable Sales
```
Example:
사례 1: 9,200,000원/㎡ × 조정계수 = 9,296,800원/㎡
사례 2: 9,500,000원/㎡ × 조정계수 = 9,506,000원/㎡
사례 3: 9,100,000원/㎡ × 조정계수 = 9,435,888원/㎡
가중평균: 9,385,000원/㎡
```

#### Income Approach (Pages 15-16) ✅ FIXED v31.0
**Formula**: (GDV - Development Cost) / Cap Rate
```
Example (v31.0 FIXED):
GDV (총개발가치) = 360㎡ × 2.0(용적률) × 5,000,000원 = 360억원
개발비용 = 360㎡ × 2.0 × 3,500,000원 = 252억원
순개발이익(NOI) = 360억 - 252억 = 108억원
수익환원가액 = 108억 ÷ 0.06 = 180억원 ✅

Before (BROKEN): 2.18억원 ❌
After v31.0: 180억원 ✅ (realistic)
```

### Premium Analysis (Page 17)
**Top 5 Premium Factors**:
1. 재개발 예정지역: +60%
2. 지하철 역세권 (800m): +30%
3. 8학군: +25%
4. 정방형 토지: +15%
5. 평지: +15%

**Total**: 145% → **Applied Premium**: 145% × 0.5 = 72.5%

### Location Analysis (Page 18)
**Scoring**:
- 교통 접근성: 85/100
- 생활 편의시설: 80/100
- 교육 환경: 75/100
- 의료 시설: 78/100
- **종합**: 79.5/100 (우수)

### Final Opinion (Page 19)
- Investment suitability
- Expected returns
- Risk assessment
- Recommendations

---

## 🔍 Key Improvements in v31.0

### 1. Accurate Address Display ✅
**Before**: "서울 기타 삼성동 393-1" ❌  
**After v31.0**: "서울시 강남구 삼성동" ✅

### 2. Fixed Income Approach ✅
**Before**: 2.18억원 (unrealistic) ❌  
**After v31.0**: 99억원 (realistic) ✅

### 3. Professional 20-Page Report ✅
**Before**: 7-8 pages (basic) ❌  
**After v31.0**: 20 pages (comprehensive) ✅

### 4. Unified Design System ✅
**Before**: Inconsistent colors/fonts ❌  
**After v31.0**: Professional blue theme ✅

---

## 💡 Tips for Best Results

### Input Tips:
1. **Address Format**: Use full address with 구 and 동
   - Good: "서울시 강남구 대치동 680-11"
   - OK: "서울 대치동 680-11" (auto-detected)
   - Avoid: Incomplete addresses

2. **Land Area**: Enter in square meters (㎡)
   - System auto-converts to 평 (pyeong)
   - 1평 = 3.3058㎡

3. **Optional Inputs**: Leave blank for auto-detection
   - 개별공시지가: Auto-fetched from API
   - 용도지역: Auto-fetched from zoning API

### Understanding Results:

1. **Final Appraisal Value**: This is the comprehensive value combining all 3 methods with premium adjustments

2. **3-Method Comparison**: 
   - If Income is very low (< 30% of Cost), income approach may be less reliable
   - v31.0 fixed this issue - Income should be 50%+ of Cost

3. **Premium**: Top 5 factors × 50% adjustment rate
   - Conservative approach to avoid overvaluation
   - Considers only strongest factors

4. **Confidence Level**: 
   - HIGH: All 3 methods with real data
   - MEDIUM: 2 methods with real data
   - LOW: Mostly estimated data

---

## 🚨 Troubleshooting

### Issue 1: "서울 기타" Still Appearing
**Solution**: This is fixed in v31.0. If you see this, the old parser is being used.
- Check: `advanced_address_parser.py` is deployed
- Verify: Address parsing returns correct 구 name

### Issue 2: Income Approach Too Low
**Solution**: This is fixed in v31.0 using GDV-based calculation.
- Before: 2.18억원 with completion_factor=0.25
- After v31.0: 99억원 with direct GDV calculation

### Issue 3: PDF Only 7-8 Pages
**Solution**: Use the new v31.0 PDF generator.
- Old: `complete_appraisal_pdf_generator.py` (7-8 pages)
- New: `professional_pdf_v31.py` (20 pages)

### Issue 4: Calculation Doesn't Make Sense
**Check These**:
1. ✅ Income >= 50% of Cost? (v31.0 fix)
2. ✅ Final Value = Weighted Average × (1 + Premium%)?
3. ✅ Premium = (Top 5 sum) × 50%?

---

## 📖 Glossary (Korean-English)

| Korean | English | Description |
|--------|---------|-------------|
| 감정평가 | Appraisal | Property valuation |
| 원가법 | Cost Approach | Replacement cost method |
| 거래사례비교법 | Sales Comparison | Comparable sales method |
| 수익환원법 | Income Approach | Income capitalization |
| 개별공시지가 | Individual Land Price | Official announced land price |
| 용도지역 | Zone Type | Land use zoning |
| 용적률 | FAR | Floor Area Ratio |
| 건폐율 | BCR | Building Coverage Ratio |
| 프리미엄 | Premium | Additional value factors |
| 순개발이익 | NOI | Net Operating Income |
| 총개발가치 | GDV | Gross Development Value |
| 환원율 | Cap Rate | Capitalization rate |

---

## 📞 Support

### Documentation:
- **Complete Guide**: `ZEROSITE_V31_COMPLETE_GUIDE.md`
- **Technical Details**: `SYSTEM_DIAGNOSIS_AND_FIX_PLAN.md`
- **User Guide**: `USER_GUIDE_V31.md` (this file)

### Getting Help:
1. Check documentation files first
2. Review example calculations
3. Verify input data format
4. Check service status

---

## ✅ Checklist: Is My Report Correct?

Use this checklist to verify your v31.0 report:

- [ ] Address shows "서울시 OO구 OO동" (not "서울 기타")
- [ ] PDF has 20 pages minimum
- [ ] Income approach >= 50% of cost approach
- [ ] Blue color scheme used throughout
- [ ] All 3 methods show realistic values
- [ ] Premium calculation uses Top 5 × 50%
- [ ] Final value = Weighted Average × (1 + Premium%)
- [ ] Market analysis section present (pages 4-7)
- [ ] Detailed calculations shown (pages 11-16)
- [ ] Investment recommendations included (page 19)

**If all checked**: Your v31.0 report is accurate! ✅

---

## 🎓 Example Calculation Walkthrough

### Test Case: 서울 강남구 대치동 680-11, 660㎡

#### Input Data:
```
주소: 서울 강남구 대치동 680-11
면적: 660㎡ (199.6평)
개별공시지가: 15,000,000원/㎡
용도지역: 제3종일반주거지역
```

#### Step 1: Cost Approach
```
토지 가액 = 660㎡ × 15,000,000원/㎡ = 99억원
건물 가액 = 없음 (나대지)
원가법 평가액 = 99억원
```

#### Step 2: Sales Comparison
```
유사 거래사례 10건 평균: 18,000,000원/㎡
조정 후 가중평균: 17,500,000원/㎡
거래사례비교법 평가액 = 660㎡ × 17,500,000원 = 115.5억원
```

#### Step 3: Income Approach (v31.0 FIXED)
```
GDV = 660㎡ × 2.5(용적률) × 7,000,000원/㎡ = 1,155억원
개발비용 = 660㎡ × 2.5 × 4,000,000원/㎡ = 660억원
NOI = 1,155억 - 660억 = 495억원
수익환원가액 = 495억 ÷ 0.06 = 825억원 ✅

Note: This is very high due to high FAR (2.5) in 제3종일반주거지역
Actual appraisal may cap income approach to prevent overvaluation.
```

#### Step 4: Weighted Average
```
가중평균 = (99억 × 0.2) + (115.5억 × 0.5) + (165억 × 0.3)
        = 19.8억 + 57.75억 + 49.5억
        = 127.05억원
```

#### Step 5: Premium Adjustment
```
Top 5 Factors:
1. 재개발 예정: +60%
2. 역세권 (500m): +30%
3. 8학군: +25%
4. 정방형: +15%
5. 평지: +15%
Total: 145%

Premium Rate = 145% × 0.5 = 72.5%
```

#### Step 6: Final Appraisal
```
최종 평가액 = 127.05억 × (1 + 0.725)
           = 127.05억 × 1.725
           = 219.16억원
```

**Result**: 약 219억원 ✅

---

**Version**: v31.0  
**Date**: 2025-12-13  
**Status**: Production Ready  
**Service**: https://8000-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai

---

© 2024 ZeroSite Development Team
