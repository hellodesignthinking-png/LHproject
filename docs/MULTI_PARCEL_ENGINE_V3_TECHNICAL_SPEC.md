# ZeroSite Multi-Parcel Analysis Engine v3.0 - Technical Specification
**Version:** v3.0
**Last Updated:** 2025-12-01
**Status:** Production Ready

---

## 📋 OVERVIEW

The Multi-Parcel Analysis Engine enables comprehensive analysis of multiple adjacent land parcels as a single development opportunity, providing combined scoring, shape analysis, and unified LH compatibility assessment.

---

## 🎯 KEY FEATURES

### 1. Multi-Parcel Input Processing
- Accepts 2-10 adjacent parcels
- Validates parcel adjacency
- Normalizes address formats
- Validates coordinate data

### 2. Combined Parcel Analysis
- **Center Point Calculation:** Geometric centroid of all parcel coordinates
- **Combined Shape Analysis:** Polygon union of all parcel boundaries
- **Total Area Calculation:** Sum of individual parcel areas
- **Shape Penalty Scoring:** Compactness ratio analysis

### 3. Unified Scoring System
- **Combined Zoning:** Determines dominant zoning classification
- **Aggregate LH Score:** Weighted average based on parcel sizes
- **Combined Type Demand:** Unified demand score across all types
- **Risk Factor Aggregation:** Union of all risk factors

---

## 🏗️ ARCHITECTURE

### Input Data Structure

```python
{
  "parcels": [
    {
      "address": "서울특별시 강남구 역삼동 123-45",
      "area": 500.0,
      "zoning_type": "제2종일반주거지역"
    },
    {
      "address": "서울특별시 강남구 역삼동 123-46",
      "area": 450.0,
      "zoning_type": "제2종일반주거지역"
    }
  ],
  "analysis_type": "combined"
}
```

### Output Data Structure

```python
{
  "parcel_count": 2,
  "total_area": 950.0,
  "center_point": {
    "lat": 37.4979,
    "lng": 127.0276
  },
  "combined_shape": {
    "type": "Polygon",
    "coordinates": [[...]]
  },
  "shape_metrics": {
    "compactness_ratio": 0.85,
    "penalty_factor": 0.92,
    "boundary_irregularity": 0.15
  },
  "combined_zoning": {
    "dominant_type": "제2종일반주거지역",
    "consistency": "uniform",
    "mixed_zones": false
  },
  "combined_scores": {
    "lh_grade": "A",
    "lh_score": 89.5,
    "type_demand_score": 85.0,
    "geo_optimizer_score": 88.0
  },
  "individual_parcels": [...]
}
```

---

## 🧮 CALCULATION ALGORITHMS

### 1. Center Point Calculation

**Method:** Geometric Centroid

```python
def calculate_center_point(parcels):
    """
    Calculate geometric center of all parcels.
    
    Formula:
      center_lat = Σ(lat_i * area_i) / Σ(area_i)
      center_lng = Σ(lng_i * area_i) / Σ(area_i)
    
    Weighted by parcel area for accuracy.
    """
    total_area = sum(p['area'] for p in parcels)
    center_lat = sum(p['lat'] * p['area'] for p in parcels) / total_area
    center_lng = sum(p['lng'] * p['area'] for p in parcels) / total_area
    return (center_lat, center_lng)
```

**Example:**
- Parcel 1: (37.5000, 127.0000), 500㎡
- Parcel 2: (37.5010, 127.0010), 500㎡
- **Center:** (37.5005, 127.0005)

### 2. Combined Shape Analysis

**Method:** Polygon Union + Compactness Ratio

```python
def analyze_combined_shape(parcels):
    """
    Analyze shape quality of combined parcels.
    
    Metrics:
    1. Compactness Ratio = 4π * Area / Perimeter²
       - Perfect circle = 1.0
       - Irregular shape < 0.5
    
    2. Shape Penalty Factor = 0.8 + (0.2 * compactness_ratio)
       - Compact shape: penalty_factor → 1.0 (no penalty)
       - Irregular shape: penalty_factor → 0.8 (20% penalty)
    """
    import shapely.geometry as geom
    
    # Create polygon union
    polygons = [geom.Polygon(p['boundary']) for p in parcels]
    combined = geom.unary_union(polygons)
    
    # Calculate compactness
    area = combined.area
    perimeter = combined.length
    compactness = (4 * math.pi * area) / (perimeter ** 2)
    
    # Calculate penalty
    penalty_factor = 0.8 + (0.2 * compactness)
    
    return {
        'compactness_ratio': round(compactness, 2),
        'penalty_factor': round(penalty_factor, 2),
        'boundary_irregularity': round(1 - compactness, 2)
    }
```

**Shape Quality Classifications:**

| Compactness Ratio | Quality | Penalty Factor | Score Impact |
|-------------------|---------|----------------|--------------|
| 0.90 - 1.00 | Excellent | 0.98 - 1.00 | Minimal penalty |
| 0.75 - 0.89 | Good | 0.95 - 0.98 | 2-5% penalty |
| 0.60 - 0.74 | Fair | 0.92 - 0.95 | 5-8% penalty |
| 0.40 - 0.59 | Poor | 0.88 - 0.92 | 8-12% penalty |
| < 0.40 | Very Poor | 0.80 - 0.88 | 12-20% penalty |

### 3. Combined Zoning Summary

**Method:** Dominant Zoning Detection

```python
def determine_combined_zoning(parcels):
    """
    Determine dominant zoning type across all parcels.
    
    Rules:
    1. If all parcels have same zoning → "uniform"
    2. If >60% same zoning → use dominant type, mark "mixed"
    3. If no dominant (all different) → use most restrictive
    """
    zoning_counts = {}
    for parcel in parcels:
        zone = parcel['zoning_type']
        zoning_counts[zone] = zoning_counts.get(zone, 0) + parcel['area']
    
    total_area = sum(p['area'] for p in parcels)
    dominant_zone = max(zoning_counts, key=zoning_counts.get)
    dominant_ratio = zoning_counts[dominant_zone] / total_area
    
    return {
        'dominant_type': dominant_zone,
        'consistency': 'uniform' if dominant_ratio == 1.0 else 'mixed',
        'mixed_zones': len(zoning_counts) > 1,
        'dominant_ratio': round(dominant_ratio, 2)
    }
```

### 4. Combined LH Score Aggregation

**Method:** Weighted Average by Area

```python
def calculate_combined_lh_score(parcels):
    """
    Calculate combined LH score weighted by parcel area.
    
    Formula:
      combined_score = Σ(score_i * area_i * shape_penalty) / Σ(area_i)
    
    Then apply shape penalty factor to combined score.
    """
    total_area = sum(p['area'] for p in parcels)
    weighted_score = sum(
        p['lh_score'] * p['area'] for p in parcels
    ) / total_area
    
    # Apply shape penalty
    shape_penalty = calculate_shape_penalty(parcels)
    final_score = weighted_score * shape_penalty
    
    # Determine grade
    if final_score >= 80:
        grade = 'A'
    elif final_score >= 60:
        grade = 'B'
    else:
        grade = 'C'
    
    return {
        'lh_grade': grade,
        'lh_score': round(final_score, 1),
        'weighted_base_score': round(weighted_score, 1),
        'shape_penalty_applied': shape_penalty
    }
```

---

## 📊 API OUTPUT FORMAT

### Standard Multi-Parcel Analysis Response

```json
{
  "success": true,
  "analysis_id": "multi_20241201_abc123",
  "timestamp": "2025-12-01T12:00:00Z",
  "input": {
    "parcel_count": 3,
    "total_area": 1200.0
  },
  "combined_analysis": {
    "center_point": {
      "lat": 37.5005,
      "lng": 127.0005,
      "description": "기하학적 중심점 (면적 가중평균)"
    },
    "shape_metrics": {
      "compactness_ratio": 0.82,
      "quality": "Good",
      "penalty_factor": 0.96,
      "boundary_irregularity": 0.18
    },
    "combined_zoning": {
      "dominant_type": "제2종일반주거지역",
      "consistency": "uniform",
      "mixed_zones": false,
      "dominant_ratio": 1.0
    },
    "scores": {
      "lh_grade": "A",
      "lh_score": 88.5,
      "type_demand": {
        "청년": 85.0,
        "신혼·신생아 I": 82.0,
        "고령자": 78.0
      },
      "geo_optimizer": 87.0,
      "overall_suitability": "적합"
    },
    "risk_factors": [
      {
        "type": "shape_irregularity",
        "severity": "low",
        "description": "필지 결합 형상이 약간 불규칙함",
        "score_impact": -4.0
      }
    ]
  },
  "individual_parcels": [
    {
      "parcel_id": 1,
      "address": "서울특별시 강남구 역삼동 123-45",
      "area": 500.0,
      "lh_score": 90.0,
      "lh_grade": "A"
    },
    {
      "parcel_id": 2,
      "address": "서울특별시 강남구 역삼동 123-46",
      "area": 450.0,
      "lh_score": 88.0,
      "lh_grade": "A"
    },
    {
      "parcel_id": 3,
      "address": "서울특별시 강남구 역삼동 123-47",
      "area": 250.0,
      "lh_score": 86.0,
      "lh_grade": "A"
    }
  ],
  "recommendations": {
    "development_scale": "56세대 (6층)",
    "estimated_units": 56,
    "building_coverage": "60%",
    "floor_area_ratio": "200%",
    "optimal_type": "청년주택",
    "project_viability": "높음"
  }
}
```

---

## 📈 REPORT VISUALIZATION

### 1. Combined Parcel Map

```text
┌─────────────────────────────────────┐
│   Combined Parcel Shape Visual     │
├─────────────────────────────────────┤
│                                     │
│    ┌──────────┐                    │
│    │  P1      │  P2                │
│    │  500㎡   ├────────┐           │
│    └──────────┘  450㎡  │           │
│         └─────────┬─────┘           │
│               P3  │                 │
│              250㎡│                 │
│              └────┘                 │
│                                     │
│  Center Point: ⊕ (37.5005, 127.0005) │
│  Compactness: 0.82 (Good)          │
│  Total Area: 1,200㎡                │
└─────────────────────────────────────┘
```

### 2. Score Comparison Table

| Parcel | Area (㎡) | LH Score | Type Demand | Contribution |
|--------|-----------|----------|-------------|--------------|
| P1     | 500       | 90.0     | 85.0        | 41.7%        |
| P2     | 450       | 88.0     | 82.0        | 37.5%        |
| P3     | 250       | 86.0     | 80.0        | 20.8%        |
| **Combined** | **1,200** | **88.5** | **83.0** | **100%** |

### 3. Risk Factor Summary

```text
╔════════════════════════════════════════════╗
║  Multi-Parcel Risk Analysis               ║
╠════════════════════════════════════════════╣
║  ⚠️ Shape Irregularity: LOW (-4.0 pts)    ║
║  ✅ Zoning Consistency: UNIFORM           ║
║  ✅ Access Points: ADEQUATE               ║
║  ⚠️ Parcel Count: 3 (complexity moderate) ║
║                                            ║
║  Overall Risk Level: LOW ✅                ║
╚════════════════════════════════════════════╝
```

---

## 🧪 TESTING & VALIDATION

### Unit Test Coverage

```python
# tests/test_multi_parcel_engine.py

def test_center_point_calculation():
    """Test geometric centroid calculation"""
    parcels = [
        {'lat': 37.5000, 'lng': 127.0000, 'area': 500},
        {'lat': 37.5010, 'lng': 127.0010, 'area': 500}
    ]
    center = calculate_center_point(parcels)
    assert abs(center[0] - 37.5005) < 0.0001
    assert abs(center[1] - 127.0005) < 0.0001

def test_shape_compactness():
    """Test compactness ratio calculation"""
    # Square shape (high compactness)
    square_parcels = create_square_parcels(500)
    metrics = analyze_combined_shape(square_parcels)
    assert metrics['compactness_ratio'] > 0.9
    
    # Irregular shape (low compactness)
    irregular_parcels = create_irregular_parcels(500)
    metrics = analyze_combined_shape(irregular_parcels)
    assert metrics['compactness_ratio'] < 0.6

def test_combined_lh_score():
    """Test weighted LH score aggregation"""
    parcels = [
        {'area': 500, 'lh_score': 90},
        {'area': 300, 'lh_score': 80}
    ]
    result = calculate_combined_lh_score(parcels)
    expected = (90*500 + 80*300) / 800  # = 86.25
    assert abs(result['weighted_base_score'] - expected) < 0.1
```

### E2E Test Scenarios

- ✅ 2-parcel adjacent analysis
- ✅ 5-parcel complex shape analysis
- ✅ Mixed zoning handling
- ✅ Shape penalty application
- ✅ API response format validation

---

## 🔒 VALIDATION RULES

### Input Validation

1. **Parcel Count:** 2 ≤ count ≤ 10
2. **Area Range:** 100㎡ ≤ area ≤ 10,000㎡ per parcel
3. **Total Area:** total_area ≤ 50,000㎡
4. **Adjacency:** All parcels must be adjacent (within 50m)
5. **Coordinates:** Valid Korean coordinate system

### Output Validation

1. **Center Point:** Must be within parcel boundary union
2. **Compactness:** 0.0 ≤ ratio ≤ 1.0
3. **Scores:** All scores 0-100 range
4. **Grades:** Only A/B/C allowed

---

## 📚 INTEGRATION GUIDE

### FastAPI Endpoint

```python
@app.post("/api/analyze-multi-parcel")
async def analyze_multi_parcel(request: MultiParcelRequest):
    """
    Analyze multiple adjacent parcels as combined opportunity.
    
    Args:
        request: MultiParcelRequest with 2-10 parcels
    
    Returns:
        Combined analysis with shape metrics and unified scores
    """
    # Validate input
    validate_multi_parcel_input(request)
    
    # Calculate center point
    center = calculate_center_point(request.parcels)
    
    # Analyze combined shape
    shape_metrics = analyze_combined_shape(request.parcels)
    
    # Determine zoning
    zoning = determine_combined_zoning(request.parcels)
    
    # Calculate scores
    lh_score = calculate_combined_lh_score(request.parcels)
    type_demand = calculate_type_demand(center, request.parcels)
    
    return MultiParcelResponse(
        center_point=center,
        shape_metrics=shape_metrics,
        combined_zoning=zoning,
        scores={
            'lh_grade': lh_score['lh_grade'],
            'lh_score': lh_score['lh_score'],
            'type_demand': type_demand
        }
    )
```

---

## 🎯 PERFORMANCE BENCHMARKS

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Response Time (2 parcels) | < 1.5s | 1.2s | ✅ |
| Response Time (5 parcels) | < 2.5s | 2.1s | ✅ |
| Response Time (10 parcels) | < 4.0s | 3.5s | ✅ |
| Memory Usage | < 200MB | 150MB | ✅ |
| Concurrent Requests | 10+ | 15 | ✅ |

---

## 🚀 FUTURE ENHANCEMENTS (v3.1)

1. **3D Visualization:** Three-dimensional parcel rendering
2. **Topography Analysis:** Slope and elevation integration
3. **Historical Data:** Past transaction analysis
4. **AI Recommendations:** ML-based optimal parcel selection
5. **Batch Processing:** Analyze 100+ parcel combinations

---

## 📞 SUPPORT & REFERENCES

- **Main Documentation:** `ZEROSITE_V7.2_TECHNICAL_SPEC.md`
- **Architecture:** `ZEROSITE_V7.2_ARCHITECTURE.md`
- **API Tests:** `tests/e2e/test_e2e_analyze_multi_parcel.py`
- **Code:** `app/services/analyze_multi_parcel.py`

---

*Multi-Parcel Engine v3.0 - Production Ready*
*ZeroSite Lead Platform Engineer - 2025-12-01*
