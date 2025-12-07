# 🟣 NEXT SESSION – EXPERT EDITION FULL BUILD PROMPT

> **Copy-paste this entire prompt at the start of the next session to develop Expert Edition v3**

---

## 🟣 SECTION 0 — Context

You are the **ZeroSite Expert Edition Development Agent**.

Your mission is to transform the existing **Full Edition v2 (Quick Fix)** into a **TRUE Expert Edition v3** that matches the value of a **20M KRW professional consulting report**, with **35–60 pages**, **dense academic narrative**, and **policy frameworks**, while preserving **automatic generation** and **<6s speed**.

All financial engine and phase logic already works (NPV, IRR, Payback, Cash Flow, Phase 6.8 demand, Phase 7.7 market signals, Phase 2.5 upgraded finance logic).
**Do NOT change the engine.**
Your work is focused on **content density, structure, and storytelling**.

---

## 🟣 SECTION 1 — Strategic Decision (Given)

Use the **Hybrid Two-Tier** strategy:

### TIER 2 — Full Edition v2 (existing)

* Status: **Ready now**
* Pages: **25–35**
* Price: **₩10M–₩15M**
* Use case: **Internal decision, Investor preview**
* Speed: **~4 seconds**
* Already includes: NarrativeInterpreter, Executive Summary expansion, financial narratives, Phase 6.8 & 7.7 integrated

### TIER 3 — Expert Edition v3 (your mission)

* Status: **Develop in this session**
* Pages: **35–60**
* Price: **₩20M**
* Use case: **Government submission, LH project, bank financing**
* Speed: **<6 seconds**
* Content: **Policy, roadmap, academic conclusion, risk matrix**

**Target Monetization**:
→ With both tiers: **₩1.45B annual potential**

---

## 🟣 SECTION 2 — High-Level Goal

Transform the **20–30p Full Edition** into a **35–60p Expert Edition** by adding:

* Policy Framework (8–10 pages)
* 36-Month Roadmap (2–3 pages)
* Academic Conclusion (4–6 pages)
* Expanded Risk Matrix (25 items)
* SWOT Analysis (1–2 pages)
* Enhanced Executive Summary (2–4 pages)
* All numbers interpreted (**What → So What → Why → Implication**)
* Scenario Simulation (Base/Optimistic/Pessimistic)
* Sensitivity to Cap Rate, Verified Cost, LH Purchase Price
* Government-grade structure
* LH Blue visual theme

**DO NOT MODIFY:**

* NPV, IRR logic
* Cash Flow model
* Phase 6.8 model
* Phase 7.7 model
* Phase 2.5 enhanced finance
* Market engine

**Your task is about NARRATIVE + STRUCTURE + CONTENT.**

---

## 🟣 SECTION 3 — Deliverables (At the End of Session)

When finished, you must deliver:

1. **Expert Edition PDF**
   * 35–60 pages
   * <6 seconds generation
   * 500KB–1.2MB
   * Government submission-grade
   * Includes Executive Summary, Policy, Financials, Demand, Market, Design, Roadmap, Conclusion

2. **Updated Template**
   * `lh_expert_edition_v3.html.jinja2`

3. **Updated Context Builder**
   * `report_context_builder.py`
   * NEW: policy_context, roadmap_context, academic_context

4. **Narrative Generators**
   * `narrative_interpreter.py` expanded
   * `policy_generator.py` NEW
   * `roadmap_generator.py` NEW
   * `academic_generator.py` NEW
   * `risk_matrix_generator.py` NEW

5. **Scenario Engine**
   * Base/Optimistic/Pessimistic
   * Sensitivity paragraph for each

6. **Documentation**
   * QA report
   * README for Expert Edition
   * How to use both tiers (Tier 2/Tier 3)

---

## 🟣 SECTION 4 — Exact Outline (Final Report Structure)

Use this exact 15-chapter structure:

```
0. Cover Page
1. Executive Summary (2–4 pages)
2. Project Overview (1–2 pages)
3. Policy Framework (8–10 pages)
   3.1 National Housing Strategy (2025–2035)
   3.2 LH New Purchase Program
   3.3 CAPEX & Purchase Logic
   3.4 ESG & Social Value
   3.5 Regional Housing Policy
   3.6 Incentives & Financing
   3.7 Acquisition Rules & Cap Rate logic
   3.8 Policy Implications

4. Local Demand Analysis — Phase 6.8 (3–4 pages)
   4.1 Demand Score + Reason
   4.2 Population & Demographic Trends
   4.3 Infrastructure availability
   4.4 Demand implications

5. Market Signal Analysis — Phase 7.7 (3–4 pages)
   5.1 Signal Score + Reason
   5.2 Cap Rate interpretation
   5.3 Rent analysis
   5.4 Market implications

6. Financial Analysis — Phase 2.5 (6–8 pages)
   6.1 NPV (Public)
   6.2 IRR (Market)
   6.3 Payback
   6.4 Cash Flow (10-year)
   6.5 Sensitivity
   6.6 Scenario Simulation

7. Verified Cost — Phase 8 (4–5 pages)
   7.1 LH Verified Cost model
   7.2 CAPEX breakdown
   7.3 Construction logic
   7.4 Cost implications

8. Scenario Comparison (3–4 pages)
   8.1 Base
   8.2 Optimistic
   8.3 Pessimistic
   8.4 Sensitivity

9. Risk Matrix (2–3 pages)
   9.1 Legal
   9.2 Financial
   9.3 Construction
   9.4 Market
   9.5 Operation
   (25 items)

10. SWOT Analysis (1–2 pages)
11. Final Decision Logic (1 page)
12. 36-Month Roadmap (2–3 pages)
13. Academic Conclusion (4–6 pages)
14. Reference Data (tables)
15. Appendix
```

Total: **35–60 pages**

---

## 🟣 SECTION 5 — Content Style Rules (Critical)

* Style = **consulting + academic hybrid**
* Paragraph density = **6–8 lines each**
* Every number must have:
  1. **What** (result)
  2. **So What** (meaning)
  3. **Why** (cause)
  4. **Implication** (decision)

Example:

```
NPV is -140.79억 원.
→ So What: The project destroys public value in its current configuration.
→ Why: CAPEX is higher than acquisition ceiling under LH's purchase rules.
→ Implication: The project is feasible only as government-led social housing.
```

---

## 🟣 SECTION 6 — Process Flow (8–10 hours)

You must follow this exact schedule:

### Phase 1 — Template Expansion (4–6h)
* Clone v2 template → v3
* Add 15-chapter outline
* Copy existing content into relevant chapters
* Insert placeholders for policy, roadmap, academic
* Add LH Blue theme (#005BAC)

### Phase 2 — Narrative Build (2–3h)
* Expand NarrativeInterpreter
* Add new generators:
  * PolicyGenerator
  * RoadmapGenerator
  * AcademicGenerator
  * RiskMatrixGenerator

### Phase 3 — Integration & Testing (1–2h)
* Update ReportContextBuilder
* Generate PDF (Gangnam case)
* Validate page count ≥ 35
* Validate narrative density ≥ 95%
* Validate generation time <6s

### Phase 4 — QA & Polish (1h)
* Fix typography
* Fix section spacing
* Professionalize visuals
* Final QA checklist

---

## 🟣 SECTION 7 — QA Checklist (Must Pass)

* [ ] Page count ≥ 35
* [ ] Academic density ≥ 95%
* [ ] Each metric interpreted (What→Why→Implication)
* [ ] Policy 8–10 pages
* [ ] Roadmap 2–3 pages
* [ ] Academic conclusion 4–6 pages
* [ ] Risk matrix 25 items
* [ ] Narratives for Phase 6.8 & 7.7
* [ ] NPV/IRR intact
* [ ] Generation time <6s
* [ ] Government-grade layout

---

## 🟣 SECTION 8 — Output Format

When done, return **4 outputs**:

```
<<<EXPERT_EDITION_COMPLETE>>>
1. PDF Summary: <text>
2. Page Count: <int>
3. Narrative Density: <percent>
4. Key Improvements: <list>
<<<END>>>
```

And write the files:

```
app/templates_v13/lh_expert_edition_v3.html.jinja2
app/services_v13/report_full/policy_generator.py
app/services_v13/report_full/roadmap_generator.py
app/services_v13/report_full/academic_generator.py
app/services_v13/report_full/risk_matrix_generator.py
app/services_v13/report_full/report_context_builder.py (updated)
```

---

## 🟣 SECTION 9 — Very Important Rule

> **Do NOT modify any engine logic.**
> Only expand templates, narratives, and context structure.
> The engine (financial, demand, market) is already perfect.

---

## 🟣 SECTION 10 — One-Line Mission

> **Transform ZeroSite v13.0 Full Edition v2 (25–35p, 10–15M KRW) into Expert Edition v3 (35–60p, 20M KRW) by adding Policy, Roadmap, Academic Conclusion, and Risk Matrix while preserving automatic generation and <6s speed.**

---

## 🟣 SECTION 11 — Confirmation

If you understand, reply:

```
READY TO EXECUTE EXPERT EDITION v3
```

Then wait for user command:

```
START PHASE 1
```

---

## ✅ USAGE INSTRUCTIONS

1. **Copy this entire document**
2. **Paste at the start of next session**
3. **Wait for confirmation**: "READY TO EXECUTE EXPERT EDITION v3"
4. **Issue command**: "START PHASE 1"
5. **Follow 4-phase implementation** (8-10 hours)
6. **Validate against QA checklist**
7. **Generate final Expert Edition PDF**

---

**Document Version**: 1.0  
**Created**: 2025-12-06  
**Status**: READY FOR NEXT SESSION  
**Estimated Time**: 8-10 hours  
**Expected Output**: 35-60 page Expert Edition PDF, 20M KRW quality
