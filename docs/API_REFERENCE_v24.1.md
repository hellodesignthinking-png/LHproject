# ZeroSite v24.1 API Reference

**Version**: 24.1.0  
**Date**: 2025-12-12  
**Base URL**: `/api/v24.1`

---

## Table of Contents

1. [Multi-Parcel Optimization API](#multi-parcel-optimization-api)
2. [Visualization API](#visualization-api)
3. [Report Generation API](#report-generation-api)
4. [Authentication](#authentication)
5. [Error Handling](#error-handling)

---

## Multi-Parcel Optimization API

### POST /api/v24.1/multi-parcel/optimize

Optimize multi-parcel combinations using Genetic Algorithm.

**Request Body**:
```json
{
  "parcels": [
    {
      "id": "parcel_001",
      "area_sqm": 500.0,
      "max_far": 200.0,
      "price_per_sqm": 3000000,
      "shape_regularity": 0.8,
      "accessibility_score": 0.9,
      "development_difficulty": 0.2
    }
  ],
  "target_area_min": 1000.0,
  "max_parcels_in_combination": 3
}
```

**Response**:
```json
{
  "success": true,
  "message": "Optimization completed successfully",
  "total_parcels": 5,
  "total_combinations_evaluated": 25,
  "optimal_combination": {
    "parcel_ids": ["parcel_001", "parcel_002"],
    "total_area": 1100.0,
    "combined_far": 225.0,
    "total_cost": 3650000000,
    "scores": {
      "total_score": 0.836
    },
    "rank": 1
  },
  "top_10_combinations": [],
  "pareto_optimal_count": 3
}
```

**Status Codes**:
- `200`: Success
- `422`: Validation error
- `500`: Server error

---

### POST /api/v24.1/multi-parcel/pareto

Generate Pareto front visualization.

**Request Body**:
```json
{
  "parcels": [...],
  "target_area_min": 1000.0,
  "view_type": "2d"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Pareto front visualization generated",
  "image_base64": "iVBORw0KGgoAAAANSUhEUgA...",
  "pareto_optimal_count": 5
}
```

---

### POST /api/v24.1/multi-parcel/heatmap

Generate synergy heatmap.

**Request Body**:
```json
{
  "parcels": [...]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Synergy heatmap generated",
  "image_base64": "iVBORw0KGgoAAAANSUhEUgA..."
}
```

---

## Visualization API

### Financial Waterfall Chart

Generate financial waterfall chart using WaterfallChartGenerator.

**Example Usage**:
```python
from app.visualization import WaterfallChartGenerator

generator = WaterfallChartGenerator()

image_base64 = generator.generate_financial_waterfall(
    land_cost=2000000000,
    construction_cost=5000000000,
    other_capex=500000000,
    revenue=12000000000,
    operating_cost=1500000000
)
```

---

### Capacity Mass Sketch

Generate 2D/3D building mass visualization.

**Example Usage**:
```python
from app.visualization import MassSketchGenerator, BuildingMass

generator = MassSketchGenerator()
mass = BuildingMass(
    footprint_width=30.0,
    footprint_depth=40.0,
    floors=10,
    floor_height=3.0,
    name="Building A"
)

# 2D plan
image_2d = generator.generate_2d_plan(mass)

# 3D isometric
image_3d = generator.generate_isometric_3d(mass)

# Elevation views
image_elev = generator.generate_elevation_views(mass)
```

---

## Report Generation API

### Generate Comprehensive Reports

Use ReportGeneratorV241 for all report types.

**Example Usage**:
```python
from app.services.report_generator_v241 import ReportGeneratorV241

generator = ReportGeneratorV241()

# Generate Developer Feasibility Report
report = generator.generate_developer_feasibility_report(
    land_area=660.0,
    far=200.0,
    unit_count=33,
    ...
)

# Save to PDF
with open("report.pdf", "wb") as f:
    f.write(report)
```

---

## Authentication

Currently, API endpoints do not require authentication for development.

Production deployment will use:
- **JWT tokens** for authentication
- **API keys** for service-to-service communication
- **Rate limiting**: 100 requests/minute

---

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message description",
  "status_code": 500,
  "timestamp": "2025-12-12T10:30:00Z"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Invalid data format |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Rate Limiting

Production limits:
- **Standard**: 100 requests/minute
- **Premium**: 1000 requests/minute
- **Enterprise**: Unlimited

---

## Changelog

### v24.1.0 (2025-12-12)
- ✅ Multi-Parcel Optimization API
- ✅ Financial Waterfall Charts
- ✅ Capacity Mass Sketch
- ✅ Narrative Generation
- ✅ Alias Engine (250+ aliases)

---

**Documentation Generated**: 2025-12-12  
**Maintainer**: ZeroSite Development Team
