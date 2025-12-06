# ZeroSite MVP Implementation Guide

## 🎯 Overview

Complete implementation of the ZeroSite MVP (Minimum Viable Product) for single-parcel land analysis.

**Flow**: Land Input → Building Scale → Unit Analysis → LH Evaluation → PDF Report

**Status**: ✅ **Fully Functional**

---

## 📁 File Structure

```
app/
├── config/
│   └── mvp_config.py                    # ⭐ Externalized configuration
├── services/
│   └── mvp_orchestrator.py              # ⭐ MVP orchestration service
├── api/endpoints/
│   └── mvp_analyze.py                   # ⭐ MVP API endpoint
└── main.py                               # Updated with MVP router

static/
└── mvp.html                              # ⭐ Frontend UI

docs/
├── MVP_IMPLEMENTATION.md                 # This file
├── LAND_BUILD_SUMMARY.md                 # Configuration reference
└── LAND_BUILD_QUICK_REF.md               # Quick modification guide
```

---

## 🚀 Quick Start

### 1. Start Server

```bash
cd /home/user/webapp
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8003
```

### 2. Access UI

Open browser:
```
http://localhost:8003/static/mvp.html
```

### 3. API Endpoint

```
POST /api/mvp/analyze
```

---

## 📊 API Documentation

### Request

```json
{
  "address": "서울특별시 강남구 테헤란로 123",
  "land_area": 850,
  "land_appraisal_price": 4500000,
  "zone_type": "제2종일반주거지역",
  "output_format": "json"
}
```

**Fields**:
- `address` (required): Property address
- `land_area` (required): Land area in m² (min: 100)
- `land_appraisal_price` (optional): Appraisal price
- `zone_type` (optional): Auto-detected if not provided
- `output_format`: "json" or "pdf"

### Response (JSON)

```json
{
  "ok": true,
  "data": {
    "land_input": {
      "address": "...",
      "land_area": 850,
      "land_appraisal_price": 4500000,
      "zone_type": "제2종일반주거지역"
    },
    "coordinates": {
      "latitude": 37.5065,
      "longitude": 127.0536,
      "legal_code": "1168000000"
    },
    "zoning_info": {
      "zone_type": "제2종일반주거지역",
      "building_coverage_ratio": 60.0,
      "floor_area_ratio": 250.0,
      "parking_ratio": 1.0
    },
    "building_scale": {
      "total_gross_area": 2125.0,
      "residential_gfa": 1806.25,
      "commercial_gfa": 318.75,
      "building_footprint": 510.0,
      "max_units": 30,
      "floor_count": 4,
      "units_per_floor": 7,
      "parking_required": 30,
      "building_coverage_ratio": 60.0,
      "floor_area_ratio": 250.0,
      "unit_area_used": 60.0,
      "residential_ratio": 0.85,
      "parking_ratio": 1.0
    },
    "unit_analysis": {
      "recommended_type": "신혼·신생아 I",
      "score_matrix": {...},
      "reasoning": "..."
    },
    "lh_evaluation": {
      "total_score": 72.5,
      "grade": "C",
      "breakdown": {...},
      "decision": "REVIEW",
      "confidence": 0.75,
      "key_reasons": "..."
    },
    "timestamp": "2025-12-06T10:30:00Z",
    "calculation_time_ms": 1250
  },
  "execution_time_ms": 1250
}
```

---

## 🔧 Configuration

### Externalized Parameters

All key parameters are externalized in `app/config/mvp_config.py`:

```python
# Unit Area
default_unit_area: 60.0  # m²

# GFA Distribution
residential_ratio: 0.85  # 85%
commercial_ratio: 0.15   # 15%

# Parking Ratios by Zone
parking_ratios: {
    "제1종일반주거지역": 0.8,
    "제2종일반주거지역": 1.0,
    "제3종일반주거지역": 1.0,
    ...
}

# Max Floors by Zone
max_floors_by_zone: {
    "제1종일반주거지역": 4,
    "제2종일반주거지역": 7,
    "제3종일반주거지역": 15,
    ...
}

# Minimum Requirements
min_units: 10
min_floors: 2
```

### Get Configuration

```bash
curl http://localhost:8003/api/mvp/config
```

### Update Configuration

```bash
curl -X POST http://localhost:8003/api/mvp/config/update \
  -H "Content-Type: application/json" \
  -d '{
    "building__default_unit_area": 50.0,
    "building__residential_ratio": 0.80
  }'
```

---

## 🧪 Test Cases

### Test Case 1: Standard Residential

```bash
curl -X POST "http://localhost:8003/api/mvp/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 테헤란로 123",
    "land_area": 850,
    "land_appraisal_price": 4500000,
    "zone_type": "제2종일반주거지역"
  }' | jq
```

**Expected**:
- BCR: 60%
- FAR: 250%
- Total GFA: ~2,125 m²
- Units: ~28-30
- Floors: 4-7
- LH Score: 60-80 (Grade C-B)

### Test Case 2: High-Density Zone

```bash
curl -X POST "http://localhost:8003/api/mvp/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 마포구 월드컵북로 120",
    "land_area": 1200,
    "zone_type": "제3종일반주거지역"
  }' | jq
```

**Expected**:
- BCR: 50%
- FAR: 300%
- Total GFA: ~3,600 m²
- Units: ~48-51
- Floors: 6-15
- LH Score: varies

### Test Case 3: PDF Generation

```bash
curl -X POST "http://localhost:8003/api/mvp/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 테헤란로 123",
    "land_area": 850,
    "land_appraisal_price": 4500000,
    "zone_type": "제2종일반주거지역",
    "output_format": "pdf"
  }' > report.html
```

---

## 🏗️ Architecture

### MVP Orchestrator Flow

```
MVPOrchestrator.analyze()
    ↓
1. _resolve_address()
   → Kakao API
   → Returns: latitude, longitude, legal_code
    ↓
2. _get_zoning_info()
   → ZoningAutoMapperV9
   → Returns: BCR, FAR, parking_ratio
    ↓
3. _calculate_building_scale()
   → Flexity-style calculation
   → Returns: GFA, units, floors, parking
    ↓
4. run_v11_engines()
   → Unit Analysis (v11.0)
   → LH Evaluation (v11.0)
    ↓
5. (Optional) PDF Generation
   → LHReportGeneratorV75Final
   → v7.5 design + v11.0 data
    ↓
Return: MVPAnalysisResult
```

### Key Components

1. **MVPConfig** (`mvp_config.py`)
   - Centralized configuration
   - All parameters externalized
   - Easy to modify without code changes

2. **MVPOrchestrator** (`mvp_orchestrator.py`)
   - Core orchestration logic
   - Steps 1-3: Land + Building Scale
   - Prepares data for v11.0 engines

3. **MVP API** (`mvp_analyze.py`)
   - FastAPI endpoint
   - Request/response models
   - Integration with v11.0 engines
   - PDF generation

4. **Frontend UI** (`mvp.html`)
   - Simple single-page form
   - Real-time results display
   - PDF download

---

## 🎨 Building Scale Calculation (Flexity-style)

### Formula

```python
# 1. Total GFA
total_gfa = land_area × (FAR / 100)

# 2. Building Footprint
building_footprint = land_area × (BCR / 100)

# 3. Floor Count
floor_count = total_gfa / building_footprint
floor_count = min(floor_count, max_floors_for_zone)

# 4. Residential GFA
residential_gfa = total_gfa × 0.85  # 85%

# 5. Max Units
max_units = residential_gfa / unit_area  # default 60m²

# 6. Parking
parking = max_units × parking_ratio  # by zone
```

### Example

Input:
- Land Area: 850 m²
- Zone: 제2종일반주거지역
- BCR: 60%
- FAR: 250%

Calculation:
```
total_gfa = 850 × 2.5 = 2,125 m²
building_footprint = 850 × 0.6 = 510 m²
floor_count = 2,125 / 510 = 4.16 → 4 floors
residential_gfa = 2,125 × 0.85 = 1,806 m²
max_units = 1,806 / 60 = 30 units
parking = 30 × 1.0 = 30 spaces
```

---

## 🔄 Integration with v11.0 Engines

The MVP seamlessly integrates with existing v11.0 engines:

### 1. Unit Type Analysis

```python
from app.report_generator_v11_complete import run_v11_engines

v11_result = run_v11_engines(
    address=address,
    land_area=land_area,
    land_appraisal_price=land_appraisal_price,
    zone_type=zone_type,
    analysis_result={
        # MVP building scale results
        "unit_count": mvp_result.building_scale.max_units,
        "floors": mvp_result.building_scale.floor_count,
        "total_gfa": mvp_result.building_scale.total_gross_area,
        ...
    }
)
```

### 2. LH Score & Decision

v11.0 engines automatically calculate:
- **LH Score** (100 points)
  - Location: 25 pts
  - Feasibility: 30 pts
  - Market: 25 pts
  - Financial: 10 pts
  - Regulatory: 10 pts

- **Decision**: GO / REVIEW / NO-GO
- **Grade**: A / B / C / D / F
- **Improvement Proposals**

### 3. Report Generation

```python
from app.adapters.v11_to_v75_adapter import convert_v11_analysis_to_v75_format
from app.services.lh_report_generator_v7_5_final import LHReportGeneratorV75Final

# Convert v11 → v7.5 format
v75_data = convert_v11_analysis_to_v75_format(...)

# Generate beautiful report
v75_generator = LHReportGeneratorV75Final()
report = v75_generator.run(
    option=4,  # Ultra-Professional
    pages=50,
    data=v75_data
)
```

---

## 📝 Modification Guide

### Change Default Unit Area (60m² → 50m²)

**File**: `app/config/mvp_config.py` line 24

```python
default_unit_area: float = Field(
    default=50.0,  # Changed from 60.0
    description="Default unit area in m²"
)
```

**Effect**: More units for same GFA

### Change Parking Ratio

**File**: `app/config/mvp_config.py` line 45

```python
parking_ratios: Dict[str, float] = Field(
    default={
        "제2종일반주거지역": 1.2,  # Changed from 1.0
        ...
    }
)
```

**Effect**: More parking spaces required

### Change Max Floors

**File**: `app/config/mvp_config.py` line 58

```python
max_floors_by_zone: Dict[str, int] = Field(
    default={
        "제2종일반주거지역": 10,  # Changed from 7
        ...
    }
)
```

**Effect**: Allow taller buildings

### After Modification

1. **Restart server**:
   ```bash
   pkill -9 -f "uvicorn.*8003"
   cd /home/user/webapp && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8003 &
   ```

2. **Test changes**:
   ```bash
   curl -X POST "http://localhost:8003/api/mvp/analyze" -H "Content-Type: application/json" -d '{...}' | jq
   ```

---

## 🎯 Performance

- **Analysis Time**: 1-3 seconds (JSON only)
- **PDF Generation**: 5-10 seconds (full report)
- **API Response**: < 5 seconds target
- **Caching**: Enabled for repeated requests

### Optimization

- Address resolution cached (1 hour TTL)
- Zoning data cached
- v11.0 engines optimized
- Async operations where possible

---

## 🚨 Error Handling

The MVP includes comprehensive error handling:

1. **Validation Errors** (400)
   - Land area < 100 m²
   - Invalid addresses
   - Missing required fields

2. **API Errors** (500)
   - Kakao API failures → fallback to default coordinates
   - NSDI API failures → use default zoning
   - Engine failures → detailed error logs

3. **User-Friendly Messages**
   - Clear error codes
   - Helpful error descriptions
   - Fallback values when possible

---

## 📊 Future Enhancements (Post-MVP)

### Phase 2: Multi-Parcel
- GIS polygon drawing
- Multi-parcel selection
- Batch analysis

### Phase 3: User Management
- Login system
- Project saving
- History tracking
- CRM integration

### Phase 4: Advanced Features
- Architectural plan generation
- Custom unit mix
- Construction cost linkage
- Financial modeling
- Scenario comparison

### Phase 5: Landywork Integration
- Full GIS capabilities
- Layer management
- Real-time collaboration
- Data export/import

---

## 🎓 Developer Notes

### Code Quality
- Type hints throughout
- Pydantic models for validation
- Comprehensive logging
- Error handling at each step

### Modularity
- Configuration externalized
- Services decoupled
- Easy to extend
- Clean separation of concerns

### Testing
- Test cases provided
- API documented
- Integration tested
- Performance validated

### Documentation
- API docs (Swagger)
- Code comments
- Architecture diagrams
- Usage examples

---

## 📞 Support

For questions or issues:
1. Check this documentation
2. Review `LAND_BUILD_SUMMARY.md`
3. Check API docs: http://localhost:8003/docs
4. Review code comments

---

## ✅ Checklist

- [x] Configuration externalized
- [x] MVP orchestrator service
- [x] API endpoint created
- [x] Frontend UI built
- [x] v11.0 integration complete
- [x] PDF generation working
- [x] Error handling implemented
- [x] Documentation complete
- [x] Test cases provided
- [x] Performance optimized

---

**Status**: ✅ **Production Ready**
**Last Updated**: 2025-12-06
**Version**: MVP 1.0
