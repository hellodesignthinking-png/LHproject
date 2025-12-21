# Image Page Data Linking Issues - Analysis Report

**Date:** 2025-12-19 07:30 UTC  
**Status:** 🔍 INVESTIGATING

---

## 📊 Identified Issues

### Issue #1: M4 Bar Chart - Incorrect Delta Calculation
**Location:** Line 1682-1710 in `module_pdf_generator.py`  
**Module:** M4 (Building Capacity Analysis)  
**Chart Type:** Bar chart comparing 법정 vs 인센티브 용적률

**Problem:**
```python
# Line 1697 - Incorrect delta calculation
ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.02,
       f'{v}세대\n({v - legal_units:+d})',  # ❌ BUG!
       ha='center', va='bottom', fontsize=11, fontweight='bold')
```

**What's Wrong:**
- For the **first bar** (법정 용적률): Shows `{20세대\n(+0)}` - Correct
- For the **second bar** (인센티브 용적률): Shows `{26세대\n(+6)}` - **INCORRECT!**
  - It's calculating `26 - 20 = +6` (difference from legal units)
  - But the label appears on BOTH bars, so:
    - First bar: `20 - 20 = 0` ✓ Correct
    - Second bar: `26 - 20 = +6` ✓ Correct for incentive
    - **BUT**: The logic is confusing and error-prone

**Expected Behavior:**
- First bar should show: `20세대` (no delta)
- Second bar should show: `26세대\n(법정 대비 +6)`

**Impact:** MEDIUM - Confusing chart labels, delta calculation may show wrong values

---

### Issue #2: M5 Cost/Revenue Chart - Zero Value Handling
**Location:** Line 2476-2514 in `module_pdf_generator.py`  
**Module:** M5 (Feasibility Analysis)  
**Chart Type:** Pie chart (costs) + Bar chart (revenue vs cost)

**Problem:**
```python
# Line 2498-2502 - Text label positioning
for bar, v in zip(bars, values):
    if v > 0:  # ✓ Checks for zero
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.02,
                f'{v:,.0f}원', ha='center', fontsize=9)
```

**What's Wrong:**
- If `costs.get('total', 0)` or `revenues.get('total', 0)` returns 0, the bar appears but has no label
- User sees empty bars with no explanation
- The pie chart (line 2485) checks `if sum(cost_values) > 0` but doesn't show a message when all are 0

**Expected Behavior:**
- If total cost or revenue is 0, show:
  - Bar with "N/A (데이터 없음)" label
  - Or don't render that bar at all
- If pie chart data is all 0, show message: "비용 데이터 불충분"

**Impact:** MEDIUM - Empty charts when data is 0, confusing for users

---

### Issue #3: M6 Radar Chart - Incorrect Max Score Mapping
**Location:** Line 2670-2708 in `module_pdf_generator.py`  
**Module:** M6 (LH Review Prediction)  
**Chart Type:** Polar radar chart

**Problem:**
```python
# Line 2672-2680 - Category and max score definition
categories = ['입지\n적정성', '사업\n타당성', '수요\n분석', '건축\n계획', '기타']
values = [
    scores.get('location', 0),      # 입지 적정성
    scores.get('feasibility', 0),   # 사업 타당성
    scores.get('demand', 0),        # 수요 분석
    scores.get('capacity', 0),      # 건축 계획 (capacity?)
    scores.get('other', 0)          # 기타
]
max_scores = [30, 25, 20, 20, 15]   # Total: 110
```

**What's Wrong:**
1. **Mismatched keys**: Chart categories don't match M6 scoring system
   - M6 actual scoring (from earlier code, line 2619-2628):
     - `location`: 35점 (not 30)
     - `scale`: 15점 (missing!)
     - `feasibility`: 40점 (not 25)
     - `compliance`: 20점 (missing!)
   - Chart uses: 30 + 25 + 20 + 20 + 15 = 110
   - Actual scoring: 35 + 15 + 40 + 20 = 110
   
2. **Wrong data keys**: 
   - Chart uses `scores.get('demand')` but M6 doesn't have a 'demand' field
   - Chart uses `scores.get('capacity')` but M6 scoring uses 'scale', 'compliance', not 'capacity'

3. **Category names misleading**:
   - "건축 계획" implies architectural design, but the data key is 'capacity' (규모?)
   - "수요 분석" suggests demand analysis, but there's no 'demand' in M6 scoring

**Expected Behavior:**
```python
# Should match M6 actual scoring system
categories = ['입지\n조건', '규모', '사업성', '준수성', '기타']
values = [
    scores.get('location', 0),      # 입지 (35점)
    scores.get('scale', 0),         # 규모 (15점)
    scores.get('feasibility', 0),   # 사업성 (40점)
    scores.get('compliance', 0),    # 준수성 (20점)
    0                                # 기타 removed or properly defined
]
max_scores = [35, 15, 40, 20, 0]  # Or remove '기타' entirely
```

**Impact:** HIGH - Chart shows completely wrong data, misleading for decision-making

---

## 🎯 Summary of Data Linking Issues

| Issue | Module | Chart Type | Severity | Description |
|-------|--------|-----------|----------|-------------|
| #1 | M4 | Bar Chart | 🟡 MEDIUM | Confusing delta calculation on both bars |
| #2 | M5 | Pie + Bar | 🟡 MEDIUM | Zero values show empty charts with no explanation |
| #3 | M6 | Radar Chart | 🔴 HIGH | Wrong data keys and max scores, chart misleading |

---

## 🔧 Recommended Fixes

### Fix #1: M4 Bar Chart Delta
```python
# Current (line 1694-1698)
for bar, v in zip(bars, values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.02,
           f'{v}세대\n({v - legal_units:+d})',  # ❌ Wrong for both bars
           ha='center', va='bottom', fontsize=11, fontweight='bold')

# Recommended fix
for i, (bar, v) in enumerate(zip(bars, values)):
    height = bar.get_height()
    if i == 0:  # Legal capacity (first bar)
        label_text = f'{v}세대\n(법정 기준)'
    else:  # Incentive capacity (second bar)
        delta = v - legal_units
        label_text = f'{v}세대\n(법정 대비 {delta:+d})'
    
    ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.02,
           label_text, ha='center', va='bottom', fontsize=11, fontweight='bold')
```

---

### Fix #2: M5 Zero Value Handling
```python
# Current (line 2476-2514)
# Add checks before rendering

# For pie chart (add after line 2485)
if sum(cost_values) > 0:
    ax1.pie(cost_values, labels=cost_labels, autopct='%1.1f%%', 
            colors=['#F44336', '#FF9800', '#FFC107'], textprops={'fontsize': 9})
    ax1.set_title('비용 구성', fontsize=12, fontweight='bold')
else:
    # Show message instead of empty chart
    ax1.text(0.5, 0.5, '비용 데이터 불충분\n(N/A)', 
            ha='center', va='center', fontsize=12, color='gray')
    ax1.set_title('비용 구성', fontsize=12, fontweight='bold')
    ax1.axis('off')

# For bar chart (modify line 2498-2502)
for bar, v in zip(bars, values):
    height = bar.get_height()
    if v > 0:
        ax2.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.02,
                f'{v:,.0f}원', ha='center', fontsize=9)
    else:
        # Show N/A label for zero values
        ax2.text(bar.get_x() + bar.get_width()/2., 0.1,
                'N/A', ha='center', fontsize=9, color='gray')
```

---

### Fix #3: M6 Radar Chart Data Keys (CRITICAL)
```python
# Current (line 2672-2680) - WRONG!
categories = ['입지\n적정성', '사업\n타당성', '수요\n분석', '건축\n계획', '기타']
values = [
    scores.get('location', 0),
    scores.get('feasibility', 0),
    scores.get('demand', 0),        # ❌ Doesn't exist in M6
    scores.get('capacity', 0),      # ❌ Wrong key
    scores.get('other', 0)
]
max_scores = [30, 25, 20, 20, 15]  # ❌ Doesn't match M6 scoring

# Recommended fix - Match M6 actual scoring system
categories = ['입지\n(Location)', '규모\n(Scale)', '사업성\n(Feasibility)', '준수성\n(Compliance)']
values = [
    scores.get('location', 0),      # 35점
    scores.get('scale', 0),         # 15점
    scores.get('feasibility', 0),   # 40점
    scores.get('compliance', 0)     # 20점
]
max_scores = [35, 15, 40, 20]  # Total: 110

# Or if M6 uses different scoring internally:
# Check actual M6 data structure and use correct keys
```

---

## 🧪 Testing Requirements

### Test Case 1: M4 Chart
**Input:**
```python
{
    "legal_capacity": {"total_units": 20},
    "incentive_capacity": {"total_units": 26}
}
```
**Expected Output:**
- First bar label: "20세대\n(법정 기준)"
- Second bar label: "26세대\n(법정 대비 +6)"

---

### Test Case 2: M5 Chart with Zero Values
**Input:**
```python
{
    "costs": {"land": 0, "construction": 0, "other": 0, "total": 0},
    "revenues": {"total": 0}
}
```
**Expected Output:**
- Pie chart shows: "비용 데이터 불충분 (N/A)"
- Bar chart shows: "N/A" labels on bars

---

### Test Case 3: M6 Radar Chart
**Input:**
```python
{
    "scores": {
        "location": 25,
        "scale": 12,
        "feasibility": 35,
        "compliance": 18
    }
}
```
**Expected Output:**
- 4 categories (not 5)
- Max scores: [35, 15, 40, 20]
- Values correctly mapped to categories

---

## 📋 Priority Order

1. **CRITICAL**: Fix #3 (M6 Radar Chart) - Wrong data keys, misleading chart
2. **MEDIUM**: Fix #2 (M5 Zero Values) - Better UX for missing data
3. **MEDIUM**: Fix #1 (M4 Delta Labels) - Clearer labeling

---

## ✅ Action Items

- [ ] Investigate M6 actual scoring system structure
- [ ] Verify data keys used in M6 scoring vs radar chart
- [ ] Fix M6 radar chart category/key mapping
- [ ] Add zero-value handling for M5 charts
- [ ] Improve M4 bar chart delta labels
- [ ] Add comprehensive chart tests
- [ ] Update test suite to verify chart data

---

**Next Steps:** Awaiting user confirmation on which issue(s) to fix first, or proceed with all 3 fixes?
