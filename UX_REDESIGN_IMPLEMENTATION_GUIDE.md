---
UX/DATA FLOW REDESIGN IMPLEMENTATION GUIDE
ZeroSite Address-Driven Decision OS
Date: 2026-01-11
Version: 3.0 (Human-Verified Mode)
---

# 🎯 IMPLEMENTATION OVERVIEW

## Mission
Transform ZeroSite from automated analysis tool → Trusted Decision OS with human-verified data checkpoints

## Current Problems
❌ No M1 verification gate → M2-M6 execute without data confirmation
❌ Cannot view M2 results independently
❌ Old analysis results auto-load when context changes
❌ No clear workflow: User doesn't know what to do next

## Solution Architecture
```
[Project Creation] → [M1 Collection] → [M1 Verification Gate 🔒] →
→ [M2 Execution] → [M2 Results View] → [M3-M6 Sequential] →
→ [Final Report]
```

---

# 📋 PHASE 1: Backend Infrastructure (COMPLETED ✅)

## 1.1 Analysis Status Tracking System

**File:** `app/core/analysis_status.py`

**Purpose:** Track execution and verification status for all modules

**Key Components:**
- `ModuleStatus` enum: NOT_STARTED, IN_PROGRESS, COMPLETED, VERIFIED, ERROR, INVALID
- `VerificationStatus` enum: PENDING, APPROVED, REJECTED
- `ModuleInfo`: Individual module tracking
- `AnalysisStatus`: Complete project status
- `AnalysisStatusStorage`: In-memory storage

**Key Methods:**
- `can_execute_module(module_name)` → Checks if execution is allowed
- `invalidate_downstream_modules(from_module)` → Invalidates M(n+1) to M6 when M(n) changes
- `get_next_action()` → Tells user what to do next

## 1.2 Status & Result API Endpoints

**File:** `app/api/endpoints/analysis_status_api.py`

**Endpoints:**

1. `POST /api/analysis/projects/create`
   - Creates project with unique ID
   - Initializes analysis status
   - Returns: project_id, next_action

2. `GET /api/analysis/projects/{project_id}/status`
   - Returns complete status of all modules
   - Shows progress percentage
   - Provides next recommended action

3. `POST /api/analysis/projects/{project_id}/modules/{module_name}/verify`
   - 🔒 CRITICAL: User verification gate
   - Accepts: approved (bool), comments (optional)
   - Returns: can_proceed flag, next_action

4. `GET /api/analysis/projects/{project_id}/modules/{module_name}/result`
   - Retrieves module result data
   - Shows execution status
   - Indicates if next module can run

5. `GET /api/analysis/projects`
   - Lists all projects
   - Shows progress and last activity
   - Sorted by recency

6. `DELETE /api/analysis/projects/{project_id}`
   - Deletes project and invalidates contexts

---

# 📋 PHASE 2: Backend API Enhancements (TODO)

## 2.1 Module Result Retrieval Endpoints

**Purpose:** Provide dedicated endpoints for viewing each module's results

### Required Endpoints:

```python
# M1 Result Endpoint
GET /api/analysis/projects/{project_id}/modules/m1/details
Returns:
- Land information (address, area, zoning)
- Location data (transportation, POI)
- Official land price
- Transaction cases
- Data sources and confidence
- Map visualization data

# M2 Result Endpoint
GET /api/analysis/projects/{project_id}/modules/m2/details
Returns:
- Land value (₩)
- Unit prices (m², 평)
- Transaction samples with adjustments
- Confidence score
- Premium factors
- Price range
- Comparison with official price

# M3 Result Endpoint
GET /api/analysis/projects/{project_id}/modules/m3/details
Returns:
- Selected housing type
- Selection confidence
- Demand prediction
- Strengths/weaknesses
- Rejected types with reasons
- Market analysis

# M4 Result Endpoint
GET /api/analysis/projects/{project_id}/modules/m4/details
Returns:
- Legal capacity (units, GFA, FAR)
- Incentive capacity
- Massing options (3-5)
- Unit summary
- Parking solutions (A & B)
- Schematic drawings

# M5 Result Endpoint
GET /api/analysis/projects/{project_id}/modules/m5/details
Returns:
- Financial metrics (NPV, IRR, ROI)
- Cost breakdown
- Revenue projection
- Profitability grade
- Risk assessment
- Sensitivity analysis

# M6 Result Endpoint
GET /api/analysis/projects/{project_id}/modules/m6/details
Returns:
- Final decision (GO/CONDITIONAL/NO-GO)
- Grade (A, B, C, D)
- Total score
- Score breakdown
- Strengths/weaknesses
- Recommendations
- Action items
```

## 2.2 Execution Control Integration

**Update existing endpoints to check execution permission:**

### M1 Freeze Context
```python
# app/api/endpoints/m1_context_freeze_v2.py
POST /api/m1/freeze-context-v2

Enhancement:
1. Check if project_id provided
2. Update analysis_status: M1 = IN_PROGRESS → COMPLETED
3. Store context_id in module status
4. Set verification_status = PENDING
5. Return: "M1 completed - awaiting user verification"
```

### Pipeline Execution
```python
# app/core/pipeline/zer0site_pipeline.py
def run(parcel_id, asking_price, project_id)

Enhancement:
1. Accept project_id parameter
2. Before each module:
   - Check can_execute_module(module_name)
   - If blocked, raise error with reason
3. After each module:
   - Update module status to COMPLETED
   - Store result_summary
4. If module fails:
   - Set status to ERROR
   - Store error_message
```

## 2.3 Context Invalidation Logic

**When context changes, invalidate downstream modules:**

```python
# Example: User re-collects M1 data

1. New M1 context created (new context_id)
2. Call analysis_status.invalidate_downstream_modules("M1")
3. M2, M3, M4, M5, M6 → status = INVALID
4. UI hides/grays out invalid results
5. User must re-execute M2-M6 sequentially
```

---

# 📋 PHASE 3: Frontend Pages (CRITICAL)

## 3.1 Project Creation Page (NEW)

**Route:** `/projects/create`

**Purpose:** Entry point for new analysis

### UI Components:

```
[Header: Create New Project]

Input Fields:
┌─────────────────────────────────────┐
│ Project Name: [________________]    │
│                                     │
│ Address: [_____________________]    │
│                                     │
│ Reference Info (Optional):          │
│ [________________________________]  │
│                                     │
│ [Cancel]  [Create & Start Analysis]│
└─────────────────────────────────────┘

Actions:
- [Create] → POST /api/analysis/projects/create
- Navigate to M1 collection page
```

## 3.2 M1 Verification Page (CRITICAL - TOP PRIORITY)

**Route:** `/projects/{project_id}/modules/m1/verify`

**Purpose:** 🔒 MANDATORY checkpoint before M2-M6

### Page Structure:

```
╔══════════════════════════════════════════════════════════════╗
║ M1 토지정보 확인                                              ║
║ Project: {project_name}                                      ║
║ Address: {address}                                           ║
║ Context ID: {context_id} | Date: {date}                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║ 🏠 1. 기본 토지 정보                                          ║
║ ┌────────────────────────────────────────────────────────┐  ║
║ │ 주소: 서울특별시 강남구 테헤란로 518                      │  ║
║ │ 지번주소: 대치동 157-29                                  │  ║
║ │ 면적: 500.0m² (151.25평)                                │  ║
║ │ 용도지역: 제2종일반주거지역                               │  ║
║ │ 건폐율: 60% | 용적률: 200%                              │  ║
║ │ 도로폭: 25.0m                                           │  ║
║ │ 데이터 출처: VWorld API ✅                               │  ║
║ └────────────────────────────────────────────────────────┘  ║
║                                                              ║
║ 🚇 2. 위치·입지 데이터                                        ║
║ ┌────────────────────────────────────────────────────────┐  ║
║ │ 지하철: 삼성역 500m (도보 7분) 🟢                        │  ║
║ │ 버스: 5개 노선 (200m 이내)                              │  ║
║ │ 초등학교: 대치초 800m                                    │  ║
║ │ 편의시설: 편의점 3개, 은행 5개                          │  ║
║ │ [지도 보기] 📍                                          │  ║
║ └────────────────────────────────────────────────────────┘  ║
║                                                              ║
║ 💰 3. 공시지가 & 규제                                         ║
║ ┌────────────────────────────────────────────────────────┐  ║
║ │ 공시지가: ₩15,000,000/m² (2024-01-01 기준)             │  ║
║ │ 규제 사항: 건축선 후퇴 3m, 주차장 설치 의무             │  ║
║ │ 데이터 출처: MOLIT API ✅                                │  ║
║ └────────────────────────────────────────────────────────┘  ║
║                                                              ║
║ 📊 4. 주변 거래사례 (최근 6개월)                              ║
║ ┌────────────────────────────────────────────────────────┐  ║
║ │ # | 날짜       | 면적  | 거래가       | 거리  | 비고   │  ║
║ │ 1 | 2024-11-15 | 500m² | ₩6,000,000,000 | 150m | 정상 │  ║
║ │ 2 | 2024-10-20 | 480m² | ₩5,800,000,000 | 200m | 정상 │  ║
║ │ 3 | 2024-09-15 | 520m² | ₩6,200,000,000 | 180m | 정상 │  ║
║ │                                                          │  ║
║ │ ⚠️ 이상치 감지: 없음                                      │  ║
║ └────────────────────────────────────────────────────────┘  ║
║                                                              ║
║ ⚠️ IMPORTANT:                                                ║
║ 위 데이터가 정확한지 확인해주세요.                            ║
║ M2~M6 분석은 이 데이터를 기반으로 진행됩니다.                 ║
║                                                              ║
║ ┌────────────────────────────────────────────────────────┐  ║
║ │ [❌ 데이터 수정 필요 / 주소 재입력]                       │  ║
║ │                                                          │  ║
║ │ [✅ M1 데이터 확인 완료 → M2~M6 분석 진행]                │  ║
║ └────────────────────────────────────────────────────────┘  ║
╚══════════════════════════════════════════════════════════════╝

Status Bar (Bottom):
┌──────────────────────────────────────────────────────────────┐
│ Progress: [M1 ✅] [M2 ⏸️] [M3 ⏸️] [M4 ⏸️] [M5 ⏸️] [M6 ⏸️]  │
│ Next Action: Verify M1 data before proceeding               │
└──────────────────────────────────────────────────────────────┘
```

### Buttons Actions:

**[❌ 데이터 수정 필요]**
```javascript
- POST /api/analysis/projects/{project_id}/modules/M1/verify
  { approved: false, comments: "주소 오류" }
- Navigate back to project input
- Allow re-collection
```

**[✅ M1 데이터 확인 완료]**
```javascript
- POST /api/analysis/projects/{project_id}/modules/M1/verify
  { approved: true }
- Response: { can_proceed: true, next_action: "Execute M2" }
- Navigate to M2 execution/results page
```

## 3.3 M2 Results Page (NEW - HIGH PRIORITY)

**Route:** `/projects/{project_id}/modules/m2/results`

**Purpose:** View land appraisal results

### Page Structure:

```
╔══════════════════════════════════════════════════════════════╗
║ M2 토지가치 · 시장 분석                                       ║
║ Project: {project_name} | Address: {address}                ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║ 💰 1. 토지가치 산출 결과                                      ║
║ ┌────────────────────────────────────────────────────────┐  ║
║ │ 토지가치: ₩6,081,933,539                                │  ║
║ │ 단위면적당: ₩12,163,867/m² (₩40,211,312/평)            │  ║
║ │                                                          │  ║
║ │ 산출방법: 거래사례비교법 (4-Factor Enhanced)             │  ║
║ │ 신뢰도: 78% (HIGH) ✅                                     │  ║
║ │ 데이터 범위: 2024-06 ~ 2024-12                          │  ║
║ └────────────────────────────────────────────────────────┘  ║
║                                                              ║
║ 📊 2. 거래사례 분석 (10건)                                    ║
║ ┌────────────────────────────────────────────────────────┐  ║
║ │ # | 거래일 | 면적 | 거래가 | 거리 | 조정률 | 조정가   │  ║
║ │ 1 | 241115 | 500m²| ₩6.0B  | 150m | +2.3% | ₩6.14B  │  ║
║ │ 2 | 241020 | 480m²| ₩5.8B  | 200m | +4.1% | ₩6.04B  │  ║
║ │ ... (show all 10 samples)                              │  ║
║ │                                                          │  ║
║ │ 평균 조정가: ₩6,081,933,539                             │  ║
║ │ 표준편차: ₩120,000,000 (1.97%)                         │  ║
║ └────────────────────────────────────────────────────────┘  ║
║                                                              ║
║ 🏷️ 3. 공시지가 비교                                          ║
║ ┌────────────────────────────────────────────────────────┐  ║
║ │ 공시지가: ₩15,000,000/m²                                │  ║
║ │ 시장가치: ₩12,163,867/m²                                │  ║
║ │ 배율: 0.81 (시장가가 공시지가 대비 81%)                  │  ║
║ └────────────────────────────────────────────────────────┘  ║
║                                                              ║
║ 📈 4. 프리미엄 요소                                           ║
║ ┌────────────────────────────────────────────────────────┐  ║
║ │ 각지 프리미엄: +3.5%                                     │  ║
║ │ 역세권 (500m 이내): +5.2%                               │  ║
║ │ 학군 (대치초): +2.8%                                     │  ║
║ └────────────────────────────────────────────────────────┘  ║
║                                                              ║
║ ℹ️ 이 데이터로 M3~M6 분석을 진행합니다.                      ║
║                                                              ║
║ ┌────────────────────────────────────────────────────────┐  ║
║ │ [◀ M1으로 돌아가기]  [M2 확인 완료 → M3 진행 ▶]         │  ║
║ └────────────────────────────────────────────────────────┘  ║
╚══════════════════════════════════════════════════════════════╝
```

## 3.4 M3-M6 Results Pages (Similar Structure)

**Routes:**
- `/projects/{project_id}/modules/m3/results`
- `/projects/{project_id}/modules/m4/results`
- `/projects/{project_id}/modules/m5/results`
- `/projects/{project_id}/modules/m6/results`

**Common Elements:**
1. Project header (name, address, context ID, date)
2. Module-specific results display
3. Navigation buttons: [◀ Previous] [Next ▶]
4. Status bar showing progress

---

# 📋 PHASE 4: Navigation & User Flow

## 4.1 Top Navigation Bar (All Pages)

```
┌──────────────────────────────────────────────────────────────┐
│ ZeroSite | Project: {project_name}                           │
│ {address} | Context: {context_id}                            │
│                                                               │
│ Modules: [M1 ✅] [M2 ✅] [M3 🔄] [M4 ⏸️] [M5 ⏸️] [M6 ⏸️]      │
│                                                               │
│ Status Icons:                                                 │
│ ✅ Completed & Verified                                       │
│ 🔄 In Progress                                                │
│ ⏸️ Not Started (Locked)                                       │
│ ❌ Error / Invalid                                            │
│ ⚠️ Awaiting Verification                                      │
└──────────────────────────────────────────────────────────────┘
```

**Click Behavior:**
- Completed modules: Navigate to results page
- In progress: Show current status
- Locked modules: Show tooltip "Complete M{n} first"
- Invalid modules: Show tooltip "Data changed - re-execute required"

## 4.2 User Flow Diagram

```
[Start]
   ↓
[Create Project] (/projects/create)
   ↓
[M1 Collection] (Automatic)
   ↓
[M1 Verification Page] (/projects/{id}/modules/m1/verify)
   ↓
   ├─ [❌ Reject] → Back to [Create Project]
   │
   └─ [✅ Approve] → [Execute M2]
                        ↓
                    [M2 Results Page] (/projects/{id}/modules/m2/results)
                        ↓
                    [M3 Execution & Results]
                        ↓
                    [M4 Execution & Results]
                        ↓
                    [M5 Execution & Results]
                        ↓
                    [M6 Execution & Results]
                        ↓
                    [Final Report]
```

---

# 📋 PHASE 5: Data Flow Control (CRITICAL)

## 5.1 Execution Gate Rules

```python
# Enforced at API level

Rule 1: M1 Verification Required
- M2 cannot execute until M1.verification_status == APPROVED
- Error: "M1 must be verified before M2 execution"

Rule 2: Sequential Completion
- M3 requires M2.status == COMPLETED
- M4 requires M3.status == COMPLETED
- M5 requires M4.status == COMPLETED
- M6 requires M5.status == COMPLETED

Rule 3: Context Validity
- All modules must use same context_id
- If context changes, downstream modules become INVALID
- User must re-execute from the changed module

Rule 4: No Old Data Auto-Load
- UI fetches data using:
  GET /api/analysis/projects/{project_id}/modules/{module}/result
- Data tied to current context_id only
- Old contexts cannot be accessed
```

## 5.2 Context Change Handling

```
Scenario: User re-collects M1 data

1. New M1 context created
   - Old context_id: abc123
   - New context_id: xyz789

2. Update analysis status:
   - M1: status = COMPLETED, context_id = xyz789
   - M2-M6: status = INVALID (call invalidate_downstream_modules)

3. UI behavior:
   - M2-M6 results pages show warning:
     "⚠️ Data has changed. Previous results are no longer valid."
   - [Re-execute] button enabled
   - Old results grayed out or hidden

4. User must:
   - Verify new M1 data
   - Re-execute M2-M6 sequentially
```

## 5.3 Error Handling

```
If module execution fails:
1. Set module.status = ERROR
2. Store error_message
3. UI shows error page with:
   - Error description
   - [Retry] button
   - [Contact Support] link
4. Downstream modules remain LOCKED
```

---

# 📋 PHASE 6: Final Report & Export

## 6.1 Conditions for Final Report

```
Final report available when:
- M1.verification_status == APPROVED
- M2.status == COMPLETED
- M3.status == COMPLETED
- M4.status == COMPLETED
- M5.status == COMPLETED
- M6.status == COMPLETED
- All modules use same context_id
```

## 6.2 Report Page

**Route:** `/projects/{project_id}/report/final`

**Sections:**
1. Project Overview
2. M1 Summary (verified data)
3. M2 Land Value
4. M3 Housing Type
5. M4 Building Scale
6. M5 Feasibility
7. M6 LH Review & Decision
8. Risks & Recommendations

**Export Options:**
- [Download PDF]
- [Export Excel]
- [Share Link]

---

# 📋 IMPLEMENTATION PRIORITY

## 🔴 PHASE 1: CRITICAL (Do First)
1. ✅ Backend status tracking system
2. ✅ Status API endpoints
3. 🔄 M1 verification page (frontend)
4. 🔄 M2 results page (frontend)
5. 🔄 Top navigation bar

## 🟡 PHASE 2: HIGH (Do Next)
6. Module result endpoints (M1-M6 details)
7. M3-M6 results pages
8. Execution control integration
9. Context invalidation logic

## 🟢 PHASE 3: MEDIUM (Do After)
10. Project list page
11. Final report page
12. Export functionality
13. Error handling UI

---

# 🔐 SYSTEM PRINCIPLES (PERMANENT)

1. **Data First, Judgment Second**
   - Always verify data before analysis
   - Human confirmation required at critical points

2. **No Automatic Overrides**
   - System cannot skip verification gates
   - API enforces execution rules

3. **Context Integrity**
   - One context ID = One complete analysis
   - Context change = Downstream invalidation

4. **User Trust Through Transparency**
   - Show data sources
   - Explain calculations
   - Allow review before proceeding

5. **No Old Data Auto-Load**
   - Always fetch current context
   - Previous analyses separate
   - Clear indication of data freshness

---

# 🔔 SYSTEM DECLARATION

```
본 분석은 사용자가 직접 확인한 M1 데이터를 기반으로
M2~M6 분석이 순차적으로 수행되었습니다.

ZeroSite는 주소 기반 실데이터만을 사용하며,
모든 판단은 인간의 검증을 거칩니다.

System Mode: DATA-FIRST · HUMAN-VERIFIED 🔒

© ZeroSite by AntennaHoldings | Natai Heum
Date: 2026-01-11
```

---

# 📝 NEXT STEPS

## Immediate Actions (Today):
1. Register new API routers in main app
2. Create M1 verification frontend page
3. Create M2 results frontend page
4. Test end-to-end flow

## This Week:
1. Complete all module results pages
2. Implement navigation bar
3. Add execution control to pipeline
4. Test context invalidation

## Next Week:
1. Final report page
2. Export functionality
3. UI/UX polish
4. Full system testing

---

**END OF IMPLEMENTATION GUIDE**
