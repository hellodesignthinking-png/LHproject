# 🎯 M1 Complete Redesign Plan - "Address-Based Data Collection Hub"

**Date:** 2025-12-17  
**Status:** 🚧 IN PROGRESS  
**Goal:** Transform M1 from step-by-step input to unified data collection + review

---

## 🔍 Problem Analysis (Root Cause)

### Current Issues

1. **Mock Data Problem**
   - Address search always returns 강남 2 fixed addresses
   - Real Kakao API results are ignored
   - Coordinates are fake → All M2-M6 calculations fail

2. **UX Confusion**
   - Users must input same "land address" across 6 different steps
   - UI is organized by "data source" instead of "user task"
   - Button flow is confusing and repetitive

3. **Final Report Failure**
   - Fake coordinates → Invalid PNU
   - Invalid PNU → No public price data
   - Missing data → M4/M5 calculation errors
   - Calculation errors → Report generation fails

---

## ✅ Solution: New M1 Architecture

### Design Philosophy

> **Address is singular, data is auto-collected, user only reviews/adjusts**

### New Flow

```
STEP 0: Start
  ↓
STEP 1: Address Input + API Keys (one-time)
  ↓
STEP 2: Address → Coordinates (Kakao Geocoding) [MANDATORY]
  ↓
STEP 3: Coordinates → Auto Data Collection
        - Cadastral (지번, 면적, 지목)
        - Legal (용도지역, 규제)
        - Road (도로접면, 폭)
        - Market (공시지가, 거래사례)
  ↓
STEP 4: **Single Review Screen** (통합 검토 화면)
        - Show all collected data
        - User can edit/override
        - Manual input for failed API calls
  ↓
STEP 5: M1 Lock (Context Freeze)
        - Validation: coordinates + essential data
        - No changes after lock
```

---

## 🔧 Technical Implementation

### Backend Changes

#### 1. Create `collect_land_bundle()` Function

```python
async def collect_land_bundle(lat: float, lon: float, address: str) -> Dict[str, Any]:
    """
    Unified data collection based on coordinates
    
    Collects:
    - Cadastral data (PNU, area, jimok)
    - Legal information (zone, regulations)
    - Road conditions
    - Market data (public price, transactions)
    
    Returns comprehensive LandDataBundle with:
    - All collected data
    - API success/failure status for each
    - Confidence scores
    """
```

#### 2. Remove Mock Fallback

```python
# BEFORE (❌ Bad):
except Exception as e:
    return mock_data  # Always returns 강남 addresses

# AFTER (✅ Good):
except Exception as e:
    return {
        "success": False,
        "error": str(e),
        "suggestions": []  # Empty if API fails
    }
```

#### 3. New Endpoint: `/collect-all`

```python
@router.post("/collect-all")
async def collect_all_land_data(
    lat: float,
    lon: float,
    address: str,
    api_keys: Optional[Dict] = None
) -> LandDataBundleResponse:
    """
    One-shot data collection for all M1 requirements
    """
```

### Frontend Changes

#### 1. Merge Steps 3-6 into Single Review Screen

**Old Structure:**
```
Step 1: Address Input
Step 2: Location Verification
Step 3: Cadastral Data Input
Step 4: Land Use Input
Step 5: Road Info Input
Step 6: Market Data Input
Step 7: Review All
Step 8: Lock
```

**New Structure:**
```
Step 1: Address Input
Step 2: Coordinates Confirmation
Step 3: AUTO Data Collection (Backend)
Step 4: **Review & Adjust Screen** (Single unified UI)
  - Cadastral section (editable)
  - Legal section (editable)
  - Road section (editable)
  - Market section (editable)
Step 5: Lock
```

#### 2. Review Screen UI Design

```jsx
<ReviewScreen data={collectedData}>
  <Section title="📍 Location">
    <Field name="coordinates" value={data.coords} readOnly />
    <Field name="address" value={data.address} editable />
  </Section>
  
  <Section title="📄 Cadastral" apiStatus={data.cadastral.status}>
    <Field name="pnu" value={data.pnu} editable />
    <Field name="area" value={data.area} editable />
    <Field name="jimok" value={data.jimok} editable />
  </Section>
  
  <Section title="⚖️ Legal" apiStatus={data.legal.status}>
    <Field name="zone" value={data.zone} editable />
    <Field name="regulations" value={data.regulations} editable />
  </Section>
  
  // ... similar for Road and Market
  
  <Button onClick={handleLock}>Confirm & Lock M1</Button>
</ReviewScreen>
```

---

## 📊 Implementation Status

### Phase 1: Backend Core ✅ IN PROGRESS

- [🔄] Create `collect_land_bundle()` function
- [ ] Remove mock fallback from address search
- [ ] Add `/collect-all` endpoint
- [ ] Enhance Kakao API integration
- [ ] Add data validation layer

### Phase 2: Frontend Redesign

- [ ] Create unified `ReviewScreen` component
- [ ] Remove individual Step 3-6 components
- [ ] Add API status indicators
- [ ] Implement edit/override functionality
- [ ] Add manual input fallback UI

### Phase 3: M1 Lock Enhancement

- [ ] Add mandatory data validation
- [ ] Implement coordinate verification
- [ ] Add PNU validation
- [ ] Create data completeness check

### Phase 4: Testing & Documentation

- [ ] Test with real Kakao API key
- [ ] Test data collection flow
- [ ] Verify M2-M6 integration
- [ ] Update user documentation

---

## 🎯 Expected Benefits

### 1. Data Accuracy ✅
- Real coordinates from Kakao API
- No mock data contamination
- Proper PNU generation
- Reliable M2-M6 calculations

### 2. User Experience ✅
- One address input instead of 6
- Clear "collect → review → confirm" flow
- Less repetition, less confusion
- Faster completion time

### 3. System Reliability ✅
- Complete M1 context guaranteed
- No "division by zero" errors
- Successful report generation
- Clean M2-M6 pipeline

### 4. ML/AI Ready ✅
- Clear feature pipeline (Address → Features)
- Data confidence tracking
- Easy to add auto-correction
- Scalable architecture

---

## 📝 API Changes Summary

### New Endpoints

```
POST /api/m1/collect-all
  Request: { lat, lon, address, api_keys? }
  Response: LandDataBundle with all sections

POST /api/m1/validate-lock
  Request: { context_data }
  Response: { valid: bool, missing_fields: [] }
```

### Modified Endpoints

```
POST /api/m1/address/search
  - Remove mock fallback
  - Return empty [] if API fails
  - Add error details

POST /api/m1/freeze-context
  - Add mandatory validation
  - Reject if coordinates invalid
  - Reject if essential data missing
```

### Deprecated Endpoints (Keep for backward compatibility)

```
POST /api/m1/geocode         → Merged into collect-all
POST /api/m1/cadastral       → Merged into collect-all
POST /api/m1/land-use        → Merged into collect-all
POST /api/m1/road-info       → Merged into collect-all
POST /api/m1/market-data     → Merged into collect-all
```

---

## 🚀 Next Actions

### Immediate (Today)

1. ✅ Create `collect_land_bundle()` function
2. ✅ Remove mock fallback
3. ✅ Add `/collect-all` endpoint
4. ✅ Test with real coordinates

### Short-term (This Week)

1. Redesign frontend ReviewScreen
2. Integrate with new backend API
3. Test complete M1 → M2 flow
4. Update documentation

### Medium-term (Next Sprint)

1. Add ML-based data validation
2. Implement auto-correction suggestions
3. Add data confidence scoring
4. Performance optimization

---

## 📚 References

- Original M1 Design: `/home/user/webapp/app/api/endpoints/m1_step_based.py`
- Land Data Service: `/home/user/webapp/app/services/land_data_service.py`
- Frontend M1 Components: `/home/user/webapp/frontend/src/components/m1/`

---

**Last Updated:** 2025-12-17 07:00 UTC  
**Tracking Document:** This file will be updated as implementation progresses
