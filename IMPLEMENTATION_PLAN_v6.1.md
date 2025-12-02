# ZeroSite v6.0 → v6.1 Implementation Plan
## Comprehensive Bug Fixes & Feature Completion

**Date**: 2025-12-01  
**Status**: In Progress  
**Priority**: CRITICAL (Production Blockers)

---

## 🚨 CRITICAL BUGS (Must Fix First)

### Bug #1: type_demand_scores All Identical
**Symptom**: All 5 housing types (청년, 신혼I, 신혼II, 다자녀, 고령자) show same score  
**Root Cause**: `demand_score` overwrites `type_demand_scores` dict  
**Location**: `demand_prediction.py` lines 92-110  
**Fix Strategy**:
1. Remove dict comprehension that causes overwrite
2. Calculate each type independently with type-specific weights
3. Ensure weights differ by type:
   - 청년: subway 40%, cafe 30%, convenience 20%
   - 신혼I: kindergarten 35%, elementary 30%, park 25%
   - 신혼II: elementary 30%, middle 25%, mart 25%
   - 다자녀: schools 40%, academy 25%, health 20%
   - 고령자: hospital 45%, pharmacy 25%, welfare 20%

### Bug #2: POI Distance Calculation Error
**Symptom**: Schools/hospitals show "far" when actually near  
**Root Causes**:
1. Coordinate system mismatch (WGS84 vs UTMK)
2. Haversine formula using wrong order (lat, lon)
3. Gaussian decay threshold misaligned
4. min(distances) not properly selected from POI list

**Fix Strategy**:
1. Add debug logging for raw API responses
2. Verify Haversine: `asin(sqrt(sin²(Δlat/2) + cos(lat1)·cos(lat2)·sin²(Δlon/2)))`
3. Normalize all coordinates to WGS84 (EPSG:4326)
4. Adjust thresholds:
   - Schools: 0-400m (excellent), 400-800m (good), 800m+ (fair)
   - Hospitals: 0-500m (excellent), 500-1200m (good), 1200m+ (fair)
5. Add `debug_poi=True` parameter to output raw POI lists

---

## 📦 DELIVERABLES (New Files to Create)

### 1. PDF/HTML Template v1.0
**File**: `templates/report_template_v6.html`  
**Features**:
- A4 size (210mm × 297mm)
- ZeroSite watermark (bottom-right, 15% opacity)
- Auto page numbers (footer center)
- Custom header/footer
- Table styles (striped rows, borders)
- TOC auto-generation
- LH submission format compliant

### 2. Report Generator
**File**: `scripts/generate_report_v6.py`  
**Workflow**:
```
JSON analysis result → Markdown template → Jinja2 rendering → HTML → WeasyPrint → PDF
```

### 3. ZeroSite CLI v1.0
**File**: `scripts/zerosite_cli.py`  
**Commands**:
```bash
zerosite analyze --address="..." --area=800 --type="청년"
zerosite generate-report --input=analysis.json --output=report.pdf
zerosite sync-lh-notices --year=2025
zerosite multi-parcel --parcels=parcel1.json,parcel2.json
```

### 4. Report Expansion (45.5p → 55p)
**Target**: Add ~10 pages  
**Sections to Expand**:
- ESG Strategy (add 2 pages): ZEB scenarios, LCA 30% reduction details
- Risk Management (add 2 pages): 30+ exclusion criteria response strategies
- Policy Analysis (add 2 pages): 2024-2025 legal/institutional changes with citations
- Case Integration (add 3 pages): Embed 3 case studies (Seoul/Gwangmyeong/Busan)
- ASCII diagrams (add 3 diagrams): Multi-parcel flow, ESG scoring tree, Finance waterfall

### 5. Investor Pitch Deck (20 Slides)
**File**: `reports_v6/ppt_outline/ZeroSite_Pitch_Deck_20slides.md`  
**Slides**:
1. Cover (ZeroSite logo, tagline)
2. Problem (Manual LH analysis: 20h, 67.9% approval, 2M KRW)
3. Solution (AI automation: 6min, 82.3% approval, 200K KRW)
4. Market Size (3,000 projects/year, 5T KRW market)
5. ZeroSite Engine (7 core modules)
6. Technology Stack (Microservices, AI, APIs)
7. Competitive Advantage (99.5% faster, 14.4%p higher approval)
8. Case Study 1: Seoul Youth (LH 322, ROI 8.3%)
9. Case Study 2: Gwangmyeong Newlywed (LH 308, ROI 8.1%)
10. Case Study 3: Busan Senior (LH 295, ROI 7.8%)
11. Business Model (SaaS subscription + API licensing)
12. Revenue Model (Starter 500K/Pro 1.5M/Enterprise)
13. Go-to-Market Strategy (Pilot → SaaS → API)
14. Roadmap (v6.0 → v6.5 → v7.0)
15. Team (CEO/CTO/Product)
16. Financials (MRR 0 → 200M in 6 months)
17. Traction (45.5-page report, 3 case studies, v6.0 tech docs)
18. Investment Ask (290M KRW for 6 months)
19. Use of Funds (40% R&D, 30% Sales, 30% Ops)
20. Contact & Q&A

---

## 🔧 CODE FIXES (Engine Updates)

### Fix 1: demand_prediction.py
**Lines to Change**: 92-139  
**New Logic**:
```python
# 각 타입별 독립 계산 (overwrite 방지)
household_type_scores = {}

# 청년형: 지하철 40%, 대학 20%, 카페 20%, 편의점 10%, 공원 10%
if nearby_facilities:
    청년_score = (
        subway_score * 0.40 +
        university_score * 0.20 +
        nearby_facilities.get('cafe_score', 50) * 0.20 +
        nearby_facilities.get('convenience_score', 50) * 0.10 +
        nearby_facilities.get('park_score', 50) * 0.10
    )
    household_type_scores["청년"] = round(청년_score, 1)
    
# 신혼I형: 어린이집 35%, 초등학교 30%, 공원 20%, 병원 15%
# ... (similar for all 5 types)
```

### Fix 2: kakao_service.py (POI Distance)
**Add Debug Function**:
```python
def get_nearby_pois_debug(self, lat: float, lon: float, category: str, radius: int = 1000) -> Dict:
    """POI 검색 with raw response debugging"""
    response = requests.get(
        "https://dapi.kakao.com/v2/local/search/category.json",
        headers={"Authorization": f"KakaoAK {self.api_key}"},
        params={"category_group_code": category, "x": lon, "y": lat, "radius": radius}
    )
    
    raw_data = response.json()
    
    # Calculate distances using corrected Haversine
    pois_with_distance = []
    for poi in raw_data.get("documents", []):
        poi_lat = float(poi["y"])
        poi_lon = float(poi["x"])
        distance = self._haversine(lat, lon, poi_lat, poi_lon)
        pois_with_distance.append({
            "name": poi["place_name"],
            "distance": round(distance, 1),
            "raw_x": poi_lon,
            "raw_y": poi_lat
        })
    
    return {
        "pois": sorted(pois_with_distance, key=lambda x: x["distance"]),
        "min_distance": min([p["distance"] for p in pois_with_distance]) if pois_with_distance else None,
        "count": len(pois_with_distance)
    }
```

---

## ✅ TEST FILES

### test_type_demand_scores_v6.py
```python
import pytest
from app.services.demand_prediction import MunicipalDemandPredictor

def test_type_demand_scores_differ():
    """Test that all 5 housing types have different scores"""
    predictor = MunicipalDemandPredictor()
    
    result = predictor.predict(
        subway_distance=500,
        university_distance=1000,
        youth_ratio=25.0,
        avg_rent_price=50,
        existing_rental_units=100,
        nearby_facilities={
            "kindergarten_distance": 300,
            "elementary_distance": 400,
            "hospital_distance": 600,
            "cafe_distance": 200
        }
    )
    
    scores = result.household_type_scores
    assert scores is not None, "household_type_scores should not be None"
    
    # All 5 types should have different scores
    unique_scores = set(scores.values())
    assert len(unique_scores) == 5, f"Expected 5 unique scores, got {len(unique_scores)}: {scores}"
    
    # 청년 should favor subway + cafe
    assert scores["청년"] > scores["고령자"], "Youth should score higher with nearby subway and cafe"
```

### test_geooptimizer_poi_distance.py
```python
import pytest
from app.services.kakao_service import KakaoService

def test_poi_distance_accuracy():
    """Test POI distance calculation accuracy"""
    kakao = KakaoService()
    
    # Known location: Seoul City Hall (서울특별시청)
    lat, lon = 37.5665, 126.9780
    
    # Get nearby schools (should find several within 1km)
    result = kakao.get_nearby_pois_debug(lat, lon, "SC4", radius=1000)
    
    assert result["count"] > 0, "Should find at least one school within 1km of City Hall"
    assert result["min_distance"] < 1000, f"Min distance {result['min_distance']}m exceeds 1000m radius"
    
    # Verify distance calculation (should use Haversine)
    first_poi = result["pois"][0]
    calculated_distance = kakao._haversine(lat, lon, first_poi["raw_y"], first_poi["raw_x"])
    
    assert abs(calculated_distance - first_poi["distance"]) < 1, "Distance mismatch in Haversine calculation"
```

---

## 🔄 BRAND UPDATE

**Task**: Replace all occurrences of "사회적기업(주)안테나" → "ZeroSite"  
**Files to Update**:
- All markdown reports in `reports_*/`
- All Python docstrings in `app/`
- All HTML templates in `templates/`
- README files

**Command**:
```bash
find /home/user/webapp -type f \( -name "*.md" -o -name "*.py" -o -name "*.html" \) \
  -exec sed -i 's/사회적기업(주)안테나/ZeroSite/g' {} +
```

---

## 📝 CHANGELOG v6.0 → v6.1

```markdown
# Changelog: ZeroSite v6.0 → v6.1

## [v6.1.0] - 2025-12-01

### 🐛 CRITICAL BUG FIXES
- **Fixed**: type_demand_scores showing identical values for all housing types
  - Root cause: dict overwrite in demand_prediction.py
  - Solution: Independent calculation for each of 5 types with type-specific weights
  - Impact: 청년/신혼/고령자 scores now correctly differentiated

- **Fixed**: POI distance calculation error (schools/hospitals showing "far" when near)
  - Root causes: Coordinate mismatch, Haversine formula error, wrong threshold
  - Solution: Normalized to WGS84, corrected Haversine, adjusted thresholds
  - Added: debug_poi parameter for raw POI list output

### ✨ NEW FEATURES
- **Added**: PDF/HTML Report Template v1.0 (A4, watermark, auto page numbers)
- **Added**: generate_report_v6.py (JSON→MD→HTML→PDF automation)
- **Added**: zerosite_cli.py v1.0 (4 commands: analyze, generate-report, sync, multi-parcel)
- **Added**: 20-slide Investor Pitch Deck (Markdown format)

### 📚 DOCUMENTATION
- **Expanded**: Report from 45.5 to 55+ pages
  - Added: 2 pages ESG strategy details
  - Added: 2 pages risk management & exclusion criteria
  - Added: 2 pages 2024-2025 policy changes with citations
  - Added: 3 pages case study integration
  - Added: 3 ASCII diagrams
- **Updated**: All brand mentions from "사회적기업(주)안테나" to "ZeroSite"

### 🧪 TESTING
- **Added**: test_type_demand_scores_v6.py (validates 5 unique scores)
- **Added**: test_geooptimizer_poi_distance.py (validates distance accuracy)

### 🔧 TECHNICAL IMPROVEMENTS
- Improved: Haversine distance calculation accuracy
- Improved: Type-specific facility weight calculation
- Improved: Error handling in POI search
- Improved: Debug logging for distance calculations

---

## Migration Guide

No breaking changes. Existing code continues to work.  
To use new features:
```bash
# Install CLI tool
python scripts/zerosite_cli.py --version

# Generate report from analysis
python scripts/generate_report_v6.py --input=analysis.json --output=report.pdf
```
```

---

## 🎯 IMPLEMENTATION ORDER

1. **Phase 1: Critical Bug Fixes** (2 hours)
   - [ ] Fix type_demand_scores (demand_prediction.py)
   - [ ] Fix POI distance calculation (kakao_service.py)
   - [ ] Write test files (pytest)
   - [ ] Run tests and verify fixes

2. **Phase 2: Core Deliverables** (3 hours)
   - [ ] Create PDF/HTML template
   - [ ] Create generate_report_v6.py
   - [ ] Create zerosite_cli.py
   - [ ] Test report generation pipeline

3. **Phase 3: Documentation** (2 hours)
   - [ ] Expand report to 55+ pages
   - [ ] Create 20-slide pitch deck
   - [ ] Brand update (안테나 → ZeroSite)
   - [ ] Write CHANGELOG

4. **Phase 4: Integration & Deployment** (1 hour)
   - [ ] Update all engine files
   - [ ] Commit all changes
   - [ ] Update PR with v6.1 notes
   - [ ] Create v6.1 release tag

**Total Estimated Time**: 8 hours  
**Priority**: CRITICAL (blocks production use)

---

**Status**: Ready to implement  
**Approval**: Pending

© 2025 ZeroSite (ZeroSite). All Rights Reserved.
