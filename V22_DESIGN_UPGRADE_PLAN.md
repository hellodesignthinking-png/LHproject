# ZeroSite v22 - McKinsey/BCG Design Upgrade Plan

## Current Status: Phase 3.1 COMPLETE ✅

**Date**: 2025-12-08  
**Objective**: Transform v21 (KDI academic style) → v22 (McKinsey/BCG consulting style)  
**Progress**: CSS Design System Added (30% complete)

---

## ✅ Completed Work (Phase 3.1)

### 1. McKinsey/BCG CSS Design System Added
**File Modified**: `app/services_v13/report_full/lh_expert_edition_v3.html.jinja2`

**Added Components**:
- ✅ McKinsey Color Palette (9 colors: text-black, paragraph, caption, highlight, borders)
- ✅ Pretendard + Inter font imports
- ✅ McKinsey Typography System (22px title, 14px subtitle, 12.5px body)
- ✅ Grid Layout System (12-column, 1fr + 1fr split)
- ✅ Logic Box Component (white background, subtle borders)
- ✅ Highlight Box Component (blue background for insights)
- ✅ PDF Print Optimization
- ✅ Responsive fallback for mobile

**CSS Added**: ~170 lines of professional consulting-grade design system

---

## 🎯 Design Principles (McKinsey/BCG Style)

### Visual Philosophy
- **Minimal**: Almost no decorative elements
- **Grid-Based**: Logic-driven 2-column layout
- **Modern Sans Serif**: Pretendard (KR) + Inter (EN)
- **Logic Flow**: What → So What → Why structure
- **Highlight Boxes**: Key insights emphasized

### Color Strategy
```
Primary Text: #2B2B2B (near black)
Paragraph: #4F4F4F (dark gray)
Caption: #7A7A7A (medium gray)
Highlight: #C4D3F6 (soft blue)
Border: #AEB7C3 (light gray)
Background: #FDFDFD (off-white)
```

### Typography Hierarchy
```
Section Title: 22px, SemiBold
Subtitle (H4): 14px, SemiBold  
Body Text: 12.5px, Regular
Line Height: 1.65
Letter Spacing: -0.3px
```

### Layout Structure
```
+------------------+------------------+
|   LOGIC LEFT     |   LOGIC RIGHT    |
|   (What/So/Why)  |  (Insight/Policy)|
+------------------+------------------+
```

---

## 📋 Remaining Work (70% to complete v22)

### Phase 3.2: Template Structure Implementation

**6 Sections to Redesign**:
1. Section 3.2: What-So What-Why (Demand Analysis)
2. Section 4.2: Market Intelligence Narrative
3. Section 6.3: NPV/IRR + Policy Interpretation
4. Section 8.0: Policy Framework Analysis
5. Section 9.0: 36-month Implementation Roadmap
6. Section 10.2: Risk Analysis Narrative

**Template Structure** (same for all 6 sections):
```html
<section class="logic-section">
  <div class="section-title">
    {{ section_number }} {{ section_name }}
  </div>
  
  <div class="logic-grid">
    <div class="logic-left">
      <div class="logic-box">
        <h4>What</h4>
        <p>{{ narrative_what }}</p>
      </div>
      
      <div class="logic-box">
        <h4>So What</h4>
        <p>{{ narrative_so_what }}</p>
      </div>
      
      <div class="logic-box">
        <h4>Why</h4>
        <p>{{ narrative_why }}</p>
      </div>
    </div>
    
    <div class="logic-right">
      <div class="highlight-box">
        <h4>Insight</h4>
        <p>{{ narrative_insight }}</p>
      </div>
      
      <div class="highlight-box">
        <h4>Policy Implication</h4>
        <p>{{ narrative_policy }}</p>
      </div>
      
      <div class="highlight-box">
        <h4>Conclusion</h4>
        <p>{{ narrative_conclusion }}</p>
      </div>
    </div>
  </div>
</section>
```

---

## 🛠️ Implementation Steps (Detailed)

### Step 1: Enhance v21 Narrative Generator (v21_narrative_generator.py)

**Add new functions** to split existing narratives into What/So What/Why structure:

```python
def split_demand_narrative_mckinsey(context: Dict[str, Any]) -> Dict[str, str]:
    """
    Split demand interpretation into McKinsey 6-box structure
    Returns: {what, so_what, why, insight, policy, conclusion}
    """
    demand_score = context.get('demand_score', 50)
    recommended_type = context.get('recommended_housing_type', '도시근로자')
    
    return {
        'what': f"AI 기반 수요 예측 결과, 대상지의 수요 점수는 {demand_score:.1f}점입니다.",
        'so_what': f"{'수요가 충분히 확보될 것으로' if demand_score >= 70 else '적정 수준의 수요가 예상되며'} 판단됩니다.",
        'why': f"{recommended_type} 계층을 대상으로 한 맞춤형 주택 공급이 효과적일 것입니다.",
        'insight': f"수요 점수 {demand_score:.1f}점은 {'상위 20%' if demand_score >= 80 else '중상위권'}에 해당합니다.",
        'policy': f"LH 정책 목표 달성에 {'크게 기여' if demand_score >= 75 else '기여'}할 수 있는 입지입니다.",
        'conclusion': f"수요 분석 결과, 세대수 및 평형 구성 결정 시 {recommended_type} 선호를 반영하시기 바랍니다."
    }
```

**Similar functions needed for**:
- `split_market_narrative_mckinsey()`
- `split_financial_narrative_mckinsey()`
- `split_policy_narrative_mckinsey()`
- `split_roadmap_narrative_mckinsey()`
- `split_risk_narrative_mckinsey()`

### Step 2: Update Context Builder (app_v20_complete_service.py)

**Add to `add_v21_narratives()` function**:

```python
# McKinsey-style structured narratives (v22)
from app.services_v13.report_full.v21_narrative_generator import (
    V21NarrativeGenerator,
    split_demand_narrative_mckinsey,
    split_market_narrative_mckinsey,
    # ... other split functions
)

# Generate McKinsey-structured narratives
mckinsey_demand = split_demand_narrative_mckinsey(ctx)
ctx['demand_what'] = mckinsey_demand['what']
ctx['demand_so_what'] = mckinsey_demand['so_what']
ctx['demand_why'] = mckinsey_demand['why']
ctx['demand_insight'] = mckinsey_demand['insight']
ctx['demand_policy'] = mckinsey_demand['policy']
ctx['demand_conclusion'] = mckinsey_demand['conclusion']

# Repeat for all 6 sections...
```

### Step 3: Update Template Sections

**Section 3.2** (line ~2740):
```html
<section class="logic-section">
  <div class="section-title">3.2 What-So What-Why 분석</div>
  
  <div class="logic-grid">
    <div class="logic-left">
      <div class="logic-box">
        <h4>What (현황 분석)</h4>
        <p>{{ demand_what }}</p>
      </div>
      
      <div class="logic-box">
        <h4>So What (시사점)</h4>
        <p>{{ demand_so_what }}</p>
      </div>
      
      <div class="logic-box">
        <h4>Why (근거)</h4>
        <p>{{ demand_why }}</p>
      </div>
    </div>
    
    <div class="logic-right">
      <div class="highlight-box">
        <h4>Insight</h4>
        <p>{{ demand_insight }}</p>
      </div>
      
      <div class="highlight-box">
        <h4>Policy Implication</h4>
        <p>{{ demand_policy }}</p>
      </div>
      
      <div class="highlight-box">
        <h4>Conclusion</h4>
        <p>{{ demand_conclusion }}</p>
      </div>
    </div>
  </div>
</section>
```

**Repeat for**:
- Section 4.2: Market Intelligence
- Section 6.3: Financial Interpretation
- Section 8.0: Policy Framework
- Section 9.0: Implementation Roadmap
- Section 10.2: Risk Analysis

---

## 📊 Expected Results

### Visual Impact
| Aspect | Before (v21) | After (v22) |
|--------|-------------|-------------|
| **Style** | KDI academic | McKinsey consulting |
| **Layout** | Single column | 2-column grid |
| **Font** | Noto Sans KR | Pretendard + Inter |
| **Structure** | Paragraph-based | Box-based logic |
| **Emphasis** | Bold text | Highlight boxes |
| **Professionalism** | Government report | Global consulting |

### Business Value
- ✅ **Higher perceived quality**: Consulting-grade design
- ✅ **Better readability**: Grid layout separates logic from evidence
- ✅ **Professional credibility**: McKinsey/BCG visual language
- ✅ **Clearer logic flow**: What → So What → Why structure
- ✅ **Premium positioning**: Elevates ZeroSite brand

---

## ⏱️ Time Estimate

| Task | Estimated Time |
|------|----------------|
| Phase 3.1: CSS Design System | ✅ DONE (30 min) |
| Phase 3.2: Split Functions | 1-2 hours |
| Phase 3.3-3.8: Template Updates | 2-3 hours |
| Phase 3.9: Testing & Refinement | 1 hour |
| Phase 3.10: Documentation | 30 min |
| **Total Remaining** | **4-6 hours** |

---

## 🚀 Quick Start Guide (For Next Developer)

### 1. Test Current Progress
```bash
cd /home/user/webapp
curl -s https://6000-i65g3ela1oephi4loymka-ad490db5.sandbox.novita.ai/report/[latest_timestamp]
```

### 2. Add Split Functions to v21_narrative_generator.py
- Copy the template function `split_demand_narrative_mckinsey()`
- Create 5 more for market, financial, policy, roadmap, risk

### 3. Update Context Builder
- Modify `add_v21_narratives()` in `app_v20_complete_service.py`
- Add 36 new context variables (6 sections × 6 variables each)

### 4. Update Template Sections
- Find each of the 6 sections in `lh_expert_edition_v3.html.jinja2`
- Replace old structure with `<section class="logic-section">` template
- Use new variables: `{{ section_what }}`, `{{ section_so_what }}`, etc.

### 5. Test & Iterate
- Generate test report
- Check grid layout rendering
- Verify all 6 sections display correctly
- Adjust box sizes if needed

### 6. Commit v22
```bash
git add -A
git commit -m "feat(v22): McKinsey/BCG design upgrade - consulting-grade layout"
git push origin genspark_ai_developer
```

---

## 📝 Notes

### Current State
- ✅ CSS design system is production-ready
- ⏳ Template structures need implementation
- ⏳ Narrative splitting functions need creation
- ⏳ Context variables need population

### Design Decisions Made
1. **Grid Layout**: 2-column split (Left: Logic, Right: Insights)
2. **Typography**: Pretendard + Inter for international feel
3. **Colors**: Minimal gray palette with blue highlights
4. **Structure**: Reusable `.logic-section` component
5. **Print**: Full PDF optimization included

### Why This Approach Works
- **Consistency**: Same structure for all 6 sections
- **Scalability**: Easy to add more sections later
- **Maintainability**: CSS in one place, content in variables
- **Flexibility**: Can switch between v21 (academic) and v22 (consulting) styles

---

## 🎯 Success Criteria

### When v22 is Complete
- [ ] All 6 sections use McKinsey grid layout
- [ ] Pretendard font displays correctly
- [ ] Logic boxes render with proper borders
- [ ] Highlight boxes have blue background
- [ ] PDF prints correctly with grid layout
- [ ] All narratives split into What/So What/Why structure
- [ ] Report looks like McKinsey presentation book

### Quality Checks
- [ ] Visual consistency across all sections
- [ ] Text alignment and spacing perfect
- [ ] No CSS conflicts with existing styles
- [ ] Print preview matches screen preview
- [ ] All boxes are page-break-safe
- [ ] Grid layout works on A4 paper size

---

## 🔗 Related Documents

- **V21_COMPLETE.md**: v21 completion report
- **V21_PHASE1_COMPLETE.md**: Phase 1 narrative generation
- **v21_narrative_generator.py**: Current narrative engine (to be extended)
- **lh_expert_edition_v3.html.jinja2**: Template file (CSS added, HTML pending)

---

**Status**: Phase 3.1 COMPLETE, Phases 3.2-3.10 PENDING  
**Next Action**: Implement split functions in v21_narrative_generator.py  
**Blocker**: None (CSS system ready, just needs implementation)  
**ETA for v22 Complete**: 4-6 hours of focused development  

---

**Author**: ZeroSite Development Team  
**Date**: 2025-12-08  
**Version**: v22 (In Progress)  
**Design Style**: McKinsey/BCG Consulting Grade  
