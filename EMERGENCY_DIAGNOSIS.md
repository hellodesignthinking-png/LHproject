# 🚨 EMERGENCY DIAGNOSIS: WHY PDFs SHOW N/A

**Date**: 2025-12-27  
**Issue**: Module PDFs show "N/A" for all values  
**Context ID**: 116801010001230045

---

## 🔍 **ROOT CAUSE IDENTIFIED**

### **The Data Flow**

```
User Request → /api/v4/reports/M2/html?context_id=116801010001230045
              ↓
pdf_download_standardized.py (Line 913)
              ↓
frozen_context = context_storage.get_frozen_context(context_id)
              ↓
assembled_data built from frozen_context.get('m2_result', {})  ← 🔴 THIS RETURNS {}
              ↓
PDF Generator receives EMPTY DATA
              ↓
Result: "N/A" everywhere
```

---

## ❌ **PROBLEM**

**Line 964-979** in `pdf_download_standardized.py`:

```python
assembled_data = {
    "m6_result": m6_result,
    "modules": {
        "M2": {
            "summary": frozen_context.get('m2_result', {}),  # ← Returns {}
            "details": {},
            "raw_data": {}
        },
        # ... same for M3, M4, M5
    }
}
```

**Why is `frozen_context.get('m2_result', {})` empty?**

### **Possible Causes:**

1. **Context Not Saved Properly**
   - M2-M6 pipeline ran, but results weren't saved to `context_storage`
   - `context_storage.save_context()` wasn't called

2. **Wrong Key Names**
   - frozen_context uses different keys (e.g., `"M2"` instead of `"m2_result"`)
   - Need to check actual frozen_context structure

3. **Context Expired/Lost**
   - Redis TTL expired
   - Database connection lost
   - Context ID doesn't match

---

## ✅ **SOLUTION STEPS**

### **STEP 1: Add Logging to Understand frozen_context**

Add diagnostic logging before building assembled_data:

```python
# In pdf_download_standardized.py, after line 929
logger.info(f"🔍 DIAGNOSIS: frozen_context keys: {list(frozen_context.keys())}")
logger.info(f"🔍 m2_result exists: {'m2_result' in frozen_context}")
logger.info(f"🔍 m2_result value: {frozen_context.get('m2_result', 'NOT FOUND')}")
```

### **STEP 2: Fix Key Mapping**

If frozen_context uses different keys, update the mapping:

```python
# Check if keys are uppercase
"M2": {
    "summary": frozen_context.get('M2', frozen_context.get('m2_result', {})),
    ...
}
```

### **STEP 3: Ensure Pipeline Saves Data**

Check `pipeline_reports_v4.py` to ensure it saves M2-M5 results:

```python
# After M2 runs
context_storage.save_context(context_id, {
    "m2_result": m2_analysis_result,
    ...
})
```

### **STEP 4: Add FAIL FAST Validation**

Before building assembled_data, validate frozen_context:

```python
# After line 929
required_keys = ['m2_result', 'm3_result', 'm4_result', 'm5_result', 'm6_result']
missing_keys = [k for k in required_keys if not frozen_context.get(k)]

if missing_keys:
    raise HTTPException(
        status_code=400,
        detail=f"필수 분석 데이터가 누락되었습니다: {missing_keys}. M2-M6 파이프라인을 완료해주세요."
    )
```

---

## 🎯 **IMMEDIATE ACTION**

1. **Check actual frozen_context structure**
   - Add logging (STEP 1)
   - Generate a new report
   - Check logs to see what keys exist

2. **Fix key mapping** (STEP 2)
   - Update pdf_download_standardized.py lines 964-979

3. **Ensure pipeline saves data** (STEP 3)
   - Check pipeline_reports_v4.py
   - Verify context_storage.save_context() is called

4. **Add validation** (STEP 4)
   - Prevent generating PDFs with empty data

---

## 📋 **VERIFICATION CHECKLIST**

After fixes:
- [ ] Generate new report with context_id
- [ ] Check logs show non-empty m2_result
- [ ] Download M2 PDF
- [ ] Verify PDF shows actual values (not N/A)
- [ ] Repeat for M3, M4, M5, M6

---

**Status**: DIAGNOSIS COMPLETE  
**Next**: Implement fixes in order (STEP 1 → 2 → 3 → 4)
