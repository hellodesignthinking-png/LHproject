# ZeroSite v4.0 M1-M6 Pipeline Flow Specification
**Date:** 2025-12-17  
**Status:** ✅ PRODUCTION READY  
**Version:** 4.0

---

## 📋 Executive Summary

This document specifies the **complete M1→M6 pipeline flow** for ZeroSite v4.0, ensuring a seamless, automatic user experience from land data input to final report generation.

### 🎯 Core Principle
> **"One Landing Input → Automatic M1-M6 Execution → 6 Reports"**

**No manual navigation between M1-M6 modules. M6 is the FIRST decision point.**

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    PipelineOrchestrator                          │
│                   (Unified Entry Point)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  STAGE 1: M1 Input (8 Steps)       │
         │  ───────────────────────────────   │
         │  STEP 0: Start                     │
         │  STEP 1: Address Search            │
         │  STEP 2: Location Verification     │
         │  STEP 3: Cadastral Data            │
         │  STEP 4: Legal Info (Zoning)       │
         │  STEP 5: Road Access               │
         │  STEP 6: Market Data               │
         │  STEP 7: Review & Verify           │
         │  STEP 8: Context Freeze (🔒 LOCK)  │
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  STAGE 2: M1 Frozen                │
         │  ───────────────────────────────   │
         │  - Context ID generated            │
         │  - Parcel ID generated             │
         │  - Frozen=true (immutable)         │
         │  - Stored in Redis + memory        │
         └────────────────────────────────────┘
                              │
                              ▼ (AUTOMATIC)
         ┌────────────────────────────────────┐
         │  STAGE 3: Pipeline Running         │
         │  ───────────────────────────────   │
         │  M2: Appraisal (감정평가)           │
         │  M3: Housing Type (주택유형)        │
         │  M4: Capacity (규모분석)            │
         │  M5: Feasibility (사업성)           │
         │  M6: LH Review (LH심사)             │
         │                                    │
         │  API: POST /api/v4/pipeline/analyze│
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  STAGE 4: Results Ready            │
         │  ───────────────────────────────   │
         │  Display all M2-M6 results         │
         │  - M2: Land Value, Confidence      │
         │  - M3: LH Type, Demand             │
         │  - M4: Legal/Incentive + Alt A/B   │
         │  - M5: NPV, IRR                    │
         │  - M6: Decision, Score (GO/NO-GO)  │
         └────────────────────────────────────┘
                              │
                              ▼ (USER ACTION)
         ┌────────────────────────────────────┐
         │  STAGE 5: Reports Generated        │
         │  ───────────────────────────────   │
         │  6 Types of Reports:               │
         │  1. 사전검토보고서                   │
         │  2. 감정평가서                       │
         │  3. LH심사예측                       │
         │  4. 사업성분석                       │
         │  5. 종합보고서                       │
         │  6. 요약보고서                       │
         │                                    │
         │  API: POST /api/v4/pipeline/reports│
         └────────────────────────────────────┘
```

---

## 🔑 Critical UX/Flow Rules

### Rule 1: No "Next Step Selection" Between M1-M6
**❌ WRONG:**
```
M1 Complete → [User selects M2 or M3 or M4...]
```

**✅ CORRECT:**
```
M1 Complete (Lock) → Automatic M2→M3→M4→M5→M6
```

**Implementation:**
- After STEP 8 "분석 시작 (M1 Lock)" button click
- `onContextFreezeComplete` callback triggers
- `POST /api/v4/pipeline/analyze` called immediately
- User sees loading screen, then results

---

### Rule 2: M4 Shows BOTH Alternatives (Comparison Only)

**❌ WRONG:**
```
M4 Screen:
[ ] Alternative A (FAR MAX)
[ ] Alternative B (Parking Priority)
[Select One] button
```

**✅ CORRECT:**
```
M4 Screen:
┌──────────────────────────────────────────┐
│ Legal FAR    │ Incentive FAR             │
│ 500 units    │ 600 units                 │
├──────────────────────────────────────────┤
│ Alt A (FAR MAX) │ Alt B (Parking Priority)│
│ 300 spaces    │ 400 spaces              │
└──────────────────────────────────────────┘

⚠️ This is a COMPARISON view. No selection needed.
    M5 uses BOTH alternatives automatically.
```

**Implementation:**
- `M4ResultsDisplay` component shows side-by-side comparison
- No checkboxes, no radio buttons, no selection UI
- Both alternatives displayed simultaneously with metrics
- Warning message: "비교 목적이며, 사용자가 대안을 선택하지 않습니다"

---

### Rule 3: M6 is the FIRST Decision Point

**Decision Flow:**
```
M1 (Input) → M2 (Auto) → M3 (Auto) → M4 (Auto, 2 alternatives) 
           → M5 (Auto, uses both) → M6 (FIRST GO/NO-GO)
```

**M6 Shows:**
- LH Review Decision: "통과 예상" / "불통과 예상"
- Total Score: 85.5/110
- Risk factors and recommendations

**User Actions at M6:**
- ✅ Generate 6 reports (if satisfied)
- 🔄 Start new analysis (if not satisfied)

**No decisions before M6:**
- M1-M5 are automatic
- User only inputs data in M1, then waits
- Results displayed together after M2-M6 complete

---

### Rule 4: M5 Uses BOTH M4 Alternatives Automatically

**M5 Feasibility Calculation:**
```python
# Backend pseudo-code
m5_result = {
    "alternative_A_feasibility": calculate_npv(m4_alt_A),
    "alternative_B_feasibility": calculate_npv(m4_alt_B),
    "recommended_alternative": "A" if npv_A > npv_B else "B"
}
```

**No user selection required.**

M5 automatically:
1. Calculates NPV for Alt A (FAR MAX)
2. Calculates NPV for Alt B (Parking Priority)
3. Compares and recommends
4. Both calculations fed into M6

---

## 📊 Data Flow Details

### M1 → M2 Data Contract

**M1 Frozen Context (6 Categories):**
```typescript
{
  // Category 1: Land Info
  land_info: {
    address_info: {...},
    coordinates: {...},
    cadastral_info: {...},
    zoning_info: {...},
    road_access: {...},
    terrain: {...}
  },
  
  // Category 2: Appraisal Inputs (M2 전용)
  appraisal_inputs: {
    official_price: {...},
    transaction_cases_for_appraisal: [...]  // MAX 5 cases
    premium_factors: {...}
  },
  
  // Category 3: Demand Inputs (M3 전용)
  demand_inputs: {
    region_characteristics: {...},
    competition: {...}
  },
  
  // Category 4: Building Constraints (M4 전용)
  building_constraints: {
    legal_constraints: {...},
    lh_incentive: {...}
  },
  
  // Category 5: Financial Inputs (M5 전용)
  financial_inputs: {
    construction_cost: {...},
    linkage: {...}
  },
  
  // Category 6: Metadata
  metadata: {
    context_id: "...",
    parcel_id: "...",
    frozen: true,
    confidence_score: 0.95,
    ...
  }
}
```

**Key Points:**
- All 6 categories frozen after STEP 8
- M2-M6 read-only access
- No modifications allowed
- Stored in Redis (primary) + memory (fallback)

---

### M4 → M5 Data Contract

**M4 Output (CapacityContextV2):**
```typescript
{
  // 1. Legal/Incentive FAR Capacity
  legal_capacity: {
    total_units: 500,
    applied_far: 200,
    target_gfa_sqm: 10000,
    ...
  },
  incentive_capacity: {
    total_units: 600,
    applied_far: 250,
    target_gfa_sqm: 12500,
    ...
  },
  
  // 2. Parking Solutions (2 alternatives)
  parking_solutions: {
    alternative_A: {  // FAR MAX
      solution_type: "alternative_A",
      total_parking_spaces: 300,
      parking_type: "self_parking",
      ...
    },
    alternative_B: {  // Parking Priority
      solution_type: "alternative_B",
      total_parking_spaces: 400,
      adjusted_total_units: 550,  // Reduced from 600
      far_sacrifice_ratio: 0.08,  // 8% FAR sacrificed
      ...
    }
  },
  
  // 3. Massing Options (3-5 alternatives)
  massing_options: [
    { option_id: "A", building_count: 2, floors: 15, ... },
    { option_id: "B", building_count: 3, floors: 10, ... },
    ...
  ],
  
  // 4. Unit Summary
  unit_summary: {...},
  
  // 5. Schematic Drawings (4 types)
  schematic_drawing_paths: {
    "ground_layout": "/path/to/ground.svg",
    "standard_floor": "/path/to/floor.svg",
    "section": "/path/to/section.svg",
    "3d_massing": "/path/to/3d.svg"
  }
}
```

**M5 Consumes:**
- Both `alternative_A` and `alternative_B`
- Calculates NPV for each
- No user selection required

---

## 🎨 Frontend Components

### PipelineOrchestrator.tsx
**Location:** `frontend/src/components/pipeline/PipelineOrchestrator.tsx`

**Responsibilities:**
1. Manage pipeline stage state (`M1_INPUT` → `M1_FROZEN` → `PIPELINE_RUNNING` → `RESULTS_READY` → `REPORTS_GENERATED`)
2. Render appropriate component for each stage
3. Handle M1 context freeze callback
4. Trigger automatic M2-M6 pipeline execution
5. Display results from all modules
6. Trigger report generation

**Key Methods:**
```typescript
handleM1FreezeComplete(contextId: string, parcelId: string): void
  → Calls POST /api/v4/pipeline/analyze
  → Sets stage to PIPELINE_RUNNING
  → Displays loading animation
  → On success: RESULTS_READY

handleGenerateReports(): void
  → Calls POST /api/v4/pipeline/reports/comprehensive
  → Downloads 6 types of reports
```

---

### M1LandingPage.tsx
**Location:** `frontend/src/components/m1/M1LandingPage.tsx`

**Updated for Pipeline Integration:**
```typescript
interface M1LandingPageProps {
  onContextFreezeComplete?: (contextId: string, parcelId: string) => void;
}

// When used standalone: shows alert
// When used in PipelineOrchestrator: triggers callback
```

---

### Step8ContextFreeze.tsx
**Location:** `frontend/src/components/m1/Step8ContextFreeze.tsx`

**Updated for V2 API:**
```typescript
interface Step8Props {
  formData: M1FormData;
  onComplete: (frozenContext: { context_id: string; parcel_id: string }) => void;
  onBack: () => void;
}

// Calls POST /api/m1/freeze-context-v2
// Passes full frozen context to parent
```

---

### M4ResultsDisplay.tsx
**Location:** `frontend/src/components/pipeline/M4ResultsDisplay.tsx`

**Displays:**
1. Legal FAR vs Incentive FAR (side-by-side)
2. Alternative A vs Alternative B (side-by-side)
3. Schematic drawings (4 types, clickable)
4. Warning: "비교 목적이며, 사용자가 대안을 선택하지 않습니다"

**No Selection UI:**
- No checkboxes
- No radio buttons
- No "Select" button
- Pure comparison view

---

## 🚀 Backend Endpoints

### POST /api/m1/freeze-context-v2
**Purpose:** Freeze M1 data into immutable context

**Request:**
```json
{
  "address": "...",
  "coordinates": {...},
  "cadastral": {...},
  // ... all STEP 1-8 data
}
```

**Response:**
```json
{
  "context_id": "ctx_...",
  "parcel_id": "1168010100100010001",
  "frozen": true,
  "frozen_at": "2025-12-17T10:30:00Z",
  "confidence_score": 0.95,
  "missing_fields": [],
  "message": "M1 context frozen successfully"
}
```

---

### POST /api/v4/pipeline/analyze
**Purpose:** Execute complete M2→M6 pipeline

**Request:**
```json
{
  "parcel_id": "1168010100100010001",
  "use_cache": false
}
```

**Response:**
```json
{
  "parcel_id": "1168010100100010001",
  "analysis_id": "analysis_...",
  "status": "success",
  "version": "v4.0",
  "execution_time_ms": 3500,
  "modules_executed": 6,
  "results": {
    "land": {...},      // M1
    "appraisal": {...}, // M2
    "housing_type": {...}, // M3
    "capacity": {...},  // M4 V2 (with alternatives)
    "feasibility": {...}, // M5
    "lh_review": {...}  // M6
  },
  // Key outputs extracted
  "land_value": 5000000000,
  "confidence_score": 0.95,
  "selected_housing_type": "청년형 30㎡",
  "recommended_units": 600,
  "npv_public": 2500000000,
  "lh_decision": "통과 예상",
  "lh_total_score": 85.5
}
```

---

### POST /api/v4/pipeline/reports/comprehensive
**Purpose:** Generate 6 types of reports

**Request:**
```json
{
  "parcel_id": "1168010100100010001",
  "report_type": "comprehensive",
  "output_format": "json"
}
```

**Response:**
```json
{
  "report_id": "report_...",
  "parcel_id": "1168010100100010001",
  "status": "success",
  "data": {
    "executive_summary": {...},
    "detailed_analysis": {...}
  },
  "html_url": "/downloads/report.html",
  "pdf_url": "/downloads/report.pdf",
  "generated_at": "2025-12-17T10:35:00Z"
}
```

---

## ✅ Testing Checklist

### Manual Flow Test

**Test 1: Complete M1→M6 Flow**
1. Navigate to PipelineOrchestrator
2. Complete M1 STEP 0-7 (minimal data input)
3. Click "🔒 분석 시작 (M1 Lock)" in STEP 8
4. **Verify:** Context freeze successful
5. **Verify:** Automatic M2-M6 pipeline triggered (no user action)
6. **Verify:** Loading screen shows "M2→M6 파이프라인 실행 중..."
7. **Verify:** Results displayed after ~3-5 seconds
8. **Verify:** All 6 modules show results (M1-M6)

**Test 2: M4 Comparison View**
1. After pipeline completes, check M4 results
2. **Verify:** Legal FAR and Incentive FAR shown side-by-side
3. **Verify:** Alternative A and Alternative B shown side-by-side
4. **Verify:** No selection UI (checkboxes/radio buttons)
5. **Verify:** Warning message displayed
6. **Verify:** Schematic drawings clickable (4 types)

**Test 3: M6 Decision Point**
1. Check M6 results card
2. **Verify:** Decision shown ("통과 예상" / "불통과 예상")
3. **Verify:** Total score shown (e.g., "85.5/110")
4. **Verify:** "6종 보고서 생성" button visible
5. Click report button
6. **Verify:** 6 report types displayed

**Test 4: Error Handling**
1. Test with invalid parcel_id
2. **Verify:** Error message displayed
3. **Verify:** "다시 시도" and "새로운 분석 시작" buttons visible
4. Click "다시 시도"
5. **Verify:** Pipeline re-executed

---

## 📚 Documentation Files

**Related Documents:**
1. `M1_FINAL_CONTEXT_SCHEMA.md` - M1→M2 API contract (6 categories)
2. `M1_BACKEND_IMPLEMENTATION_COMPLETE.md` - M1 API implementation
3. `M1_M4_COMPLETION_SUMMARY.md` - M1+M4 completion summary
4. `M1_M4_SETUP_AND_TESTING_GUIDE.md` - Setup and testing guide
5. `QUICK_START_CHECKLIST.md` - Quick deployment checklist
6. `IMPLEMENTATION_STATUS_2025-12-17.md` - Phase-by-phase status

---

## 🎯 Success Criteria

**Definition of Done:**

✅ **Flow Completeness:**
- Single landing page → M1 input → Automatic M2-M6 → Reports
- No manual navigation between M1-M6
- M6 is first decision point

✅ **M4 Display:**
- Legal/Incentive FAR shown simultaneously
- Alt A/B shown simultaneously
- No selection UI present
- Warning message displayed

✅ **Immutability:**
- M1 context frozen after STEP 8
- frozen=true in all contexts
- M2-M6 read-only access

✅ **Pipeline Integration:**
- PipelineOrchestrator orchestrates complete flow
- M1LandingPage triggers pipeline via callback
- M4ResultsDisplay shows comparison view
- Report generation works end-to-end

---

## 🚀 Deployment

**Frontend:**
```bash
cd frontend
npm install
npm run build
# Deploy build/ to static hosting
```

**Backend:**
```bash
cd /home/user/webapp
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Redis:**
```bash
redis-server --port 6379
```

**Environment:**
```bash
# .env
JUSO_API_KEY=...
KAKAO_API_KEY=...
VWORLD_API_KEY=...
DATA_GO_KR_API_KEY=...
REDIS_HOST=localhost
REDIS_PORT=6379
DATABASE_URL=...
```

---

## 📞 Support

**Questions?**
- Technical: ZeroSite Engineering Team
- Business: Product Management Team

**Repository:** https://github.com/hellodesignthinking-png/LHproject  
**PR:** #11 (feature/expert-report-generator)

---

**🎉 This pipeline is PRODUCTION READY as of 2025-12-17!**
