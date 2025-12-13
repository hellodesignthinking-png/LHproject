# ZeroSite v29.0 - Hardcoded Value Audit Report
**Date**: 2025-12-13  
**Mission**: Remove ALL hardcoded fixed values, ensure 100% dynamic calculation

---

## 🔍 PHASE 1: COMPREHENSIVE AUDIT

### 1. zone_type Hardcodes
**Files to check**:
- `app/api/v24_1/api_router.py` (Line 52, 110)
- `app/services/ultimate_appraisal_pdf_generator.py`
- `app/engines/**/*.py`
- `public/dashboard.html`

**Found**:
```python
# api_router.py Line 52
zone_type: str = Field(..., description="Zoning type", example="제3종일반주거지역")

# api_router.py Line 110
zone_type: Optional[str] = Field("제2종일반주거지역", description="Zoning type (auto-detected if not provided)", example="제3종일반주거지역")
```

**❌ PROBLEM**: Default value `"제2종일반주거지역"` is hardcoded
**✅ SOLUTION**: Remove default, force API call to vworld zoning API


### 2. individual_land_price Hardcodes
**Files to check**:
- `app/engines/appraisal_engine_v241.py` (Line 116, 174)
- `app/services/**/*.py`

**Found**:
```python
# appraisal_engine_v241.py Line 116
LH_CONSTRUCTION_COST_PER_SQM = 3_500_000  # ₩/㎡ (2024 standard)

# appraisal_engine_v241.py Line 174
if individual_land_price == 0:
    individual_land_price = self._estimate_individual_land_price(zone_type, location_factor)
```

**❌ PROBLEM**: Fallback estimation used instead of REAL API call
**✅ SOLUTION**: Call NLIS public land price API, NEVER estimate


### 3. Premium Score Hardcodes
**Files to check**:
- `app/api/v24_1/api_router.py` (Lines 86-104)
- `app/services/premium_calculator.py`

**Found**:
```python
# PremiumFactors model - ALL have default=0
land_shape: float = Field(default=0, description="Land shape premium %", example=15)
land_slope: float = Field(default=0, description="Land slope premium %", example=15)
direction: float = Field(default=0, description="Direction premium %", example=12)
road_facing: float = Field(default=0, description="Road facing premium %", example=25)
subway_distance: float = Field(default=0, description="Subway distance premium %", example=30)
```

**❌ PROBLEM**: All premium factors default to 0 if not provided
**✅ SOLUTION**: Auto-detect from address using PremiumAutoDetector


### 4. Distance Calculation Hardcodes
**Files to check**:
- `app/services/comprehensive_transaction_collector.py` (Line 260, 378)
- `app/services/final_appraisal_pdf_generator.py` (Lines 271, 389-393)

**Found**:
```python
# comprehensive_transaction_collector.py Line 260
distance = round(random.uniform(0.2, 2.0), 2)  # ❌ FAKE RANDOM DISTANCE

# comprehensive_transaction_collector.py Line 378
distance = round(random.uniform(0.15, 1.95), 2)  # ❌ FAKE RANDOM DISTANCE
```

**❌ PROBLEM**: Random fake distances instead of real Haversine calculation
**✅ SOLUTION**: Use real lat/lon from Kakao API + Haversine formula


### 5. road_grade Hardcodes
**Files to check**:
- `app/services/comprehensive_transaction_collector.py`
- `app/services/ultimate_appraisal_pdf_generator.py`

**Found**:
```python
# Need to verify road_classes hardcode in enhanced fallback
road_classes = [
    {"name": "대로", "type": "daero", "weight": 1.2, "probability": 0.15},
    {"name": "로", "type": "ro", "weight": 1.0, "probability": 0.50},
    {"name": "길", "type": "gil", "weight": 0.95, "probability": 0.35}
]
```

**❌ PROBLEM**: Road grades randomly assigned instead of queried
**✅ SOLUTION**: Use road name address API to get REAL road width/grade

---

## 📋 HARDCODE REMOVAL CHECKLIST

### Critical Files to Modify:
- [ ] `app/api/v24_1/api_router.py` - Remove zone_type default
- [ ] `app/engines/appraisal_engine_v241.py` - Remove price estimation fallback
- [ ] `app/services/comprehensive_transaction_collector.py` - Remove fake distance/road
- [ ] `app/services/ultimate_appraisal_pdf_generator.py` - Remove fallback hardcodes
- [ ] `app/services/premium_calculator.py` - Add auto-detection
- [ ] `public/dashboard.html` - Remove zone_type dropdown defaults
- [ ] `public/js/appraisal.js` - Force API calls for all data

### API Integration Requirements:
- [ ] **NLIS API**: Get real individual_land_price (개별공시지가)
- [ ] **vworld Zoning API**: Get real zone_type (용도지역)
- [ ] **Road Name Address API**: Get road width/grade
- [ ] **Kakao Geocoding API**: Get lat/lon for Haversine distance
- [ ] **MOLIT Transaction API**: Get real transaction cases

---

## 🎯 SUCCESS CRITERIA

### Test with 4 Critical Addresses:

#### Address 1: 강남구 테헤란로 427
**Expected**:
- `zone_type`: "준주거지역" (NOT "제3종일반주거지역")
- `individual_land_price`: ~22,000,000 원/㎡ (NOT estimated)
- `transactions`: DIFFERENT from other addresses
- `road_grade`: "대로" (from API, not random)

#### Address 2: 마포구 월드컵북로 120
**Expected**:
- `zone_type`: "제3종일반주거지역" (NOT same as above)
- `individual_land_price`: ~15,000,000 원/㎡ (REAL API)
- `transactions`: 마포구 specific (NOT 강남구 data)
- `road_grade`: "북로" grade from API

#### Address 3: 송파구 잠실동 19-1
**Expected**:
- `zone_type`: DIFFERENT from above 2
- `individual_land_price`: ~18,000,000 원/㎡ (REAL)
- `transactions`: 송파구 specific
- `road_grade`: "동" suffix road grade

#### Address 4: 고양시 일산서구 대화동 2223
**Expected**:
- `zone_type`: Goyang-specific zoning (NOT Seoul)
- `individual_land_price`: ~5,000,000 원/㎡ (much lower than Seoul)
- `transactions`: Goyang-specific (NOT Seoul data)
- `road_grade`: Goyang road system

**🎯 FINAL VERIFICATION**: Run same address twice → EXACT SAME RESULTS  
Run 4 different addresses → 4 COMPLETELY DIFFERENT RESULTS

