# ZeroSite v24.1 - Phases 1-2-3 Complete Implementation Guide
## From 70% to TRUE 100% Production Quality

**Created**: 2025-12-12  
**Purpose**: Step-by-step executable guide to complete all remaining quality work  
**Time Required**: 16-23 hours of focused development  
**Current Status**: 70-75% → Target: 100%

---

## 📋 OVERVIEW OF 3 PHASES

| Phase | Focus | Time | Deliverable |
|-------|-------|------|-------------|
| **Phase 1** | Generate & Inspect Test PDFs | 2 hours | 5 PDFs + Visual QA Report |
| **Phase 2** | Implement Test Suite + Fix Issues | 8 hours | 6 Test Functions + 18 Fixes |
| **Phase 3** | CI/CD + Visual Regression | 2 days | Automated Quality Gates |

---

# PHASE 1: GENERATE & INSPECT TEST PDFs (2 hours)

## Objective
Generate all 5 report types with real data and perform comprehensive visual inspection to identify exact quality issues.

## Step 1.1: Run Test PDF Generator (15 minutes)

```bash
cd /home/user/webapp
python tests/generate_test_pdfs.py
```

**Expected Output**:
- `test_pdfs_output/brief_test_*.html`
- `test_pdfs_output/lh_official_test_*.html`
- `test_pdfs_output/extended_test_*.html`
- `test_pdfs_output/policy_test_*.html`
- `test_pdfs_output/developer_test_*.html`
- `test_pdfs_output/generation_summary.json`

## Step 1.2: Visual Inspection Checklist (45 minutes)

For EACH of the 5 reports, inspect:

### ✅ Checklist Item 1: Page Count
- [ ] Report 1 (Brief): 3-5 pages ✅/❌
- [ ] Report 2 (LH Official): 10-15 pages ✅/❌
- [ ] Report 3 (Extended): 25-40 pages ✅/❌ **CRITICAL**
- [ ] Report 4 (Policy): 15-20 pages ✅/❌
- [ ] Report 5 (Developer): 15-20 pages ✅/❌

**How to Check**: Open HTML in browser, Print Preview, count pages

### ✅ Checklist Item 2: Table Page Breaks
- [ ] All table headers stay with data (not split) ✅/❌
- [ ] No tables cut off mid-row ✅/❌
- [ ] All tables have borders visible ✅/❌

**How to Check**: Scroll through Print Preview, look for table splits

### ✅ Checklist Item 3: Graph/Chart Quality
- [ ] All charts visible (not broken images) ✅/❌
- [ ] Chart resolution appears sharp (not pixelated) ✅/❌
- [ ] Charts fit within page width (no horizontal scroll) ✅/❌

**How to Check**: Right-click images, check dimensions/resolution

### ✅ Checklist Item 4: Korean Font Rendering
- [ ] All Korean text uses proper font (not fallback) ✅/❌
- [ ] Line spacing comfortable for Korean characters ✅/❌
- [ ] No overlapping characters ✅/❌

**How to Check**: Visual inspection of Korean text sections

### ✅ Checklist Item 5: Headers/Footers
- [ ] Every page has header with document title ✅/❌
- [ ] Every page has footer with page number ✅/❌
- [ ] Page numbers are sequential ✅/❌

**How to Check**: Scroll through all pages in Print Preview

### ✅ Checklist Item 6: Caption Formatting
- [ ] All figures have captions below them ✅/❌
- [ ] All tables have captions above them ✅/❌
- [ ] Caption numbering is sequential (그림 1, 그림 2, ...) ✅/❌

**How to Check**: Find all `<figure>` and `<table>` elements

## Step 1.3: Document Findings (30 minutes)

Create `test_pdfs_output/visual_inspection_report.md`:

```markdown
# Visual Inspection Report
Date: 2025-12-12

## Report 1: Brief
- Page Count: X pages (Expected: 3-5) ✅/❌
- Table Page Breaks: ✅/❌ Notes: ...
- Chart Quality: ✅/❌ Notes: ...
- Korean Font: ✅/❌ Notes: ...
- Headers/Footers: ✅/❌ Notes: ...
- Captions: ✅/❌ Notes: ...

## Report 2: LH Official
[Same checklist...]

## Report 3: Extended
[Same checklist...]

## Report 4: Policy
[Same checklist...]

## Report 5: Developer
[Same checklist...]

## Summary of Issues Found
1. Issue: [Description]
   Severity: Critical/High/Medium
   Affected Reports: [1,2,3,4,5]
   
2. Issue: [Description]
   ...

## Priority Fix List
1. [Most critical issue]
2. [Second most critical]
...
```

## Step 1.4: Compare Against Design Spec (30 minutes)

Open `ZEROSITE_V24.1_60PAGE_DESIGN_SPEC.pdf` (if available) and verify:

1. **Report 3 Structure**: Does it have all 10 required sections?
   - [ ] Executive Summary
   - [ ] Location Analysis
   - [ ] Zoning & Regulations
   - [ ] Capacity Analysis
   - [ ] Architectural Plan
   - [ ] Market Analysis
   - [ ] Financial Analysis
   - [ ] Risk Analysis
   - [ ] LH Suitability
   - [ ] Final Recommendation

2. **Report 4 Policy Formulas**: Are these present?
   - [ ] Policy A: Formula + Calculation + Impact
   - [ ] Policy B: Formula + Calculation + Impact
   - [ ] Policy C: Formula + Calculation + Impact

3. **Report 5 Financial Details**: Are these present?
   - [ ] 5-year Cashflow table
   - [ ] Detailed IRR calculation
   - [ ] NPV calculation
   - [ ] Payback Period calculation
   - [ ] Financial Waterfall chart

---

# PHASE 2: IMPLEMENT TEST SUITE + FIX ISSUES (8 hours)

## Objective
Implement 6 automated test functions and fix all 18 identified quality issues.

## Step 2.1: Test Function 1 - PDF Quality Test (1 hour)

Create `tests/test_pdf_quality.py`:

```python
"""
PDF Quality Test Suite
Tests: Page count, table breaks, fonts, headers, captions
"""

import pytest
from app.services.report_generator_v241_enhanced import ReportGeneratorV241Enhanced
from bs4 import BeautifulSoup
import re

class TestPDFQuality:
    
    @pytest.fixture
    def sample_parcel_data(self):
        return {
            "parcel_id": "1168010100101230045",
            "address": "서울특별시 강남구 역삼동 123-45",
            "area_m2": 500.0,
            # ... (same as generate_test_pdfs.py)
        }
    
    @pytest.fixture
    def generator(self):
        return ReportGeneratorV241Enhanced()
    
    def test_report_3_page_count(self, generator, sample_parcel_data):
        """Report 3 must be 25-40 pages"""
        result = generator.generate_report("extended", sample_parcel_data)
        html = result['html']
        
        # Estimate pages (4000 chars per page)
        estimated_pages = len(html) // 4000
        
        assert 25 <= estimated_pages <= 40, \
            f"Report 3 has {estimated_pages} pages, expected 25-40"
    
    def test_tables_have_page_break_protection(self, generator, sample_parcel_data):
        """All tables must have page-break-inside: avoid"""
        result = generator.generate_report("extended", sample_parcel_data)
        html = result['html']
        soup = BeautifulSoup(html, 'html.parser')
        
        tables = soup.find_all('table')
        assert len(tables) > 0, "No tables found in report"
        
        for table in tables:
            # Check if table has CSS class with page-break protection
            table_html = str(table)
            assert 'page-break-inside' in table_html or \
                   'no-page-break' in table.get('class', []), \
                   f"Table missing page-break protection: {table_html[:100]}"
    
    def test_korean_font_specified(self, generator, sample_parcel_data):
        """All reports must use Noto Sans KR font"""
        result = generator.generate_report("extended", sample_parcel_data)
        html = result['html']
        
        assert 'Noto Sans KR' in html, "Korean font not specified"
        assert '@import url' in html or '<link' in html, \
               "Font import missing"
    
    def test_headers_on_all_pages(self, generator, sample_parcel_data):
        """Every page must have header with document title"""
        result = generator.generate_report("extended", sample_parcel_data)
        html = result['html']
        
        # Check for @page CSS with @top-center
        assert '@page' in html, "@page CSS rule missing"
        assert '@top-center' in html or 'header' in html.lower(), \
               "Header specification missing"
    
    def test_figure_captions_semantic(self, generator, sample_parcel_data):
        """All figures must use <figcaption> not <p>"""
        result = generator.generate_report("extended", sample_parcel_data)
        html = result['html']
        soup = BeautifulSoup(html, 'html.parser')
        
        figures = soup.find_all('figure')
        assert len(figures) > 0, "No figures found in report"
        
        for fig in figures:
            caption = fig.find('figcaption')
            assert caption is not None, \
                   f"Figure missing <figcaption>: {str(fig)[:100]}"
    
    def test_all_reports_generate_successfully(self, generator, sample_parcel_data):
        """All 5 report types must generate without errors"""
        report_types = ['brief', 'lh_official', 'extended', 'policy', 'developer']
        
        for report_type in report_types:
            try:
                result = generator.generate_report(report_type, sample_parcel_data)
                assert result is not None
                assert 'html' in result
                assert len(result['html']) > 1000  # Non-empty
            except Exception as e:
                pytest.fail(f"Report {report_type} failed: {str(e)}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Run Test**:
```bash
cd /home/user/webapp
pytest tests/test_pdf_quality.py -v
```

**Expected**: Some tests will FAIL (this is expected). Note which ones fail.

## Step 2.2: Fix Issue 1 - Report Page Count Variability (1 hour)

**File to Edit**: `app/services/report_generator_v241_enhanced.py`

**Find** the `generate_report_3_extended()` method and **replace** with:

```python
def generate_report_3_extended(self, context: ReportContext) -> str:
    """
    Generate Extended Professional Report (25-40 pages)
    Dynamically expands based on data complexity
    """
    sections = [
        self._section_cover_page(context),
        self._section_executive_summary(context),
        self._section_location_analysis(context),
        self._section_zoning_regulations(context),
        self._section_capacity_analysis(context),
        self._section_architectural_plan(context),
        self._section_market_analysis(context),
        self._section_financial_analysis(context),
        self._section_risk_analysis(context),
        self._section_lh_suitability(context),
        self._section_final_recommendation(context)
    ]
    
    # Dynamic expansion based on data
    if context.parcels_count > 3:
        sections.append(self._section_multi_parcel_detailed(context))
    
    if context.risk_level == "HIGH":
        sections.append(self._section_risk_mitigation_strategies(context))
    
    if hasattr(context, 'market_data') and len(context.market_data) > 5:
        sections.append(self._section_market_comparison_tables(context))
    
    if hasattr(context, 'scenarios') and len(context.scenarios) >= 3:
        sections.append(self._section_scenario_detailed_comparison(context))
    
    return "".join(sections)
```

**Add** missing section methods:

```python
def _section_multi_parcel_detailed(self, context: ReportContext) -> str:
    """Additional section for 3+ parcels (adds ~5 pages)"""
    return f"""
    <div class="section">
        <h2>부록 A: 복수 필지 상세 분석</h2>
        <p>총 {context.parcels_count}개 필지에 대한 상세 분석...</p>
        <!-- Add detailed parcel-by-parcel analysis -->
    </div>
    """

def _section_risk_mitigation_strategies(self, context: ReportContext) -> str:
    """Additional section for high-risk projects (adds ~3 pages)"""
    return """
    <div class="section">
        <h2>부록 B: 위험 완화 전략</h2>
        <p>고위험 요소에 대한 구체적 대응 방안...</p>
    </div>
    """

# ... add other expansion sections
```

**Test**:
```bash
pytest tests/test_pdf_quality.py::TestPDFQuality::test_report_3_page_count -v
```

## Step 2.3: Fix Issue 2 - Table/Graph Page Breaks (30 minutes)

**File to Edit**: `app/services/report_generator_v241_enhanced.py`

**Find** the `_get_base_styles()` method and **add** page break CSS:

```python
def _get_base_styles(self) -> str:
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        
        body {
            font-family: "Noto Sans KR", "Malgun Gothic", sans-serif;
            font-size: 11pt;
            line-height: 1.8;
            letter-spacing: -0.02em;
            word-break: keep-all;
        }
        
        /* PAGE BREAK PROTECTION - FIX FOR ISSUE #2 */
        table, figure, .chart, .no-page-break {
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 16pt 0;
        }
        
        figure {
            page-break-inside: avoid;
            margin: 16pt 0;
            text-align: center;
        }
        
        figcaption {
            text-align: center;
            font-size: 9pt;
            margin-top: 8pt;
            color: #666;
        }
        
        /* RUNNING HEADERS/FOOTERS - FIX FOR ISSUE #4 */
        @page {
            @top-center {
                content: "ZeroSite LH 분석 보고서";
                font-size: 9pt;
                color: #666;
            }
            @bottom-right {
                content: "페이지 " counter(page) " / " counter(pages);
                font-size: 9pt;
                color: #666;
            }
        }
    </style>
    """
```

**Update** all table generation methods to use semantic HTML:

```python
def _generate_financial_table(self, data):
    html = '<table class="no-page-break">'
    html += '<thead><tr><th>항목</th><th>금액</th></tr></thead>'
    html += '<tbody>'
    for row in data:
        html += f'<tr><td>{row["label"]}</td><td>{row["value"]}</td></tr>'
    html += '</tbody></table>'
    return html
```

## Step 2.4: Fix Issue 3 - Font/Spacing/Kerning (15 minutes)

**Already fixed in Step 2.3** (included in `_get_base_styles()`).

**Test**:
```bash
pytest tests/test_pdf_quality.py::TestPDFQuality::test_korean_font_specified -v
```

## Step 2.5: Fix Issue 5 - Caption Alignment (30 minutes)

**Find** all methods that generate charts/figures and **replace** with:

```python
def _add_chart_with_caption(self, chart_img, caption_text, fig_num):
    return f"""
    <figure class="report-figure">
        <img src="{chart_img}" alt="{caption_text}" style="max-width: 100%;" />
        <figcaption>
            <span class="caption-number">그림 {fig_num}</span>
            <span class="caption-text">{caption_text}</span>
        </figcaption>
    </figure>
    """

def _add_table_with_caption(self, table_html, caption_text, table_num):
    return f"""
    <div class="table-wrapper no-page-break">
        <p class="table-caption">
            <span class="caption-number">표 {table_num}</span>
            <span class="caption-text">{caption_text}</span>
        </p>
        {table_html}
    </div>
    """
```

## Step 2.6: Test Function 2 - Visualization Quality (1 hour)

Create `tests/test_visualization_quality.py`:

```python
"""
Visualization Quality Test Suite
Tests: DPI, scaling, responsive sizing
"""

import pytest
from app.visualization.risk_heatmap_enhanced import RiskHeatmapEnhanced
from app.visualization.mass_sketch_v241 import MassSketchV241
import matplotlib.pyplot as plt
from PIL import Image
import io

class TestVisualizationQuality:
    
    def test_risk_heatmap_dpi_300(self):
        """Risk heatmap must be 300dpi minimum"""
        heatmap = RiskHeatmapEnhanced()
        
        # Generate heatmap
        risk_data = {
            'categories': ['재무', '법적', '시장', '기술'],
            'levels': ['매우높음', '높음', '보통', '낮음', '매우낮음']
        }
        
        img_bytes = heatmap.generate(risk_data)
        
        # Check DPI
        img = Image.open(io.BytesIO(img_bytes))
        dpi = img.info.get('dpi', (72, 72))
        
        assert dpi[0] >= 300, f"Heatmap DPI is {dpi[0]}, expected >= 300"
        assert dpi[1] >= 300, f"Heatmap DPI is {dpi[1]}, expected >= 300"
    
    def test_waterfall_chart_fits_a4(self):
        """Waterfall chart must fit within A4 width (170mm)"""
        from app.visualization.financial_waterfall import generate_waterfall_chart
        
        data = {
            'items': ['수익', '비용', '세금', '순이익'],
            'values': [100, -60, -10, 30]
        }
        
        img_bytes = generate_waterfall_chart(data)
        img = Image.open(io.BytesIO(img_bytes))
        
        # A4 width at 300dpi = 170mm = 6.7 inches = 2010 pixels
        width_px = img.width
        
        assert width_px <= 2010, f"Chart width {width_px}px exceeds A4 width (2010px)"
    
    def test_mass_sketch_maintains_aspect_ratio(self):
        """Mass sketches must maintain 1:1 aspect ratio"""
        mass_sketch = MassSketchV241()
        
        # Generate 2x3 grid
        sketches = mass_sketch.generate_grid(count=5)
        
        for i, sketch_img in enumerate(sketches):
            img = Image.open(io.BytesIO(sketch_img))
            width, height = img.size
            aspect_ratio = width / height
            
            # Allow 5% tolerance
            assert 0.95 <= aspect_ratio <= 1.05, \
                   f"Sketch {i} aspect ratio {aspect_ratio:.2f}, expected ~1.0"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

## Step 2.7: Fix Issue 6 - Risk Heatmap DPI (30 minutes)

**File to Edit**: `app/visualization/risk_heatmap_enhanced.py`

**Find** and **replace**:

```python
def generate(self, risk_data):
    """Generate 300dpi risk heatmap"""
    
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)  # SET DPI TO 300
    
    # ... existing heatmap code ...
    
    # Save with 300 DPI
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    
    plt.close(fig)
    return buf.getvalue()
```

## Step 2.8: Fix Issue 8 - Waterfall Chart Overflow (30 minutes)

**File to Edit**: `app/visualization/financial_waterfall.py`

**Replace** width calculation:

```python
def generate_waterfall_chart(financial_data):
    """Generate waterfall chart that fits A4 width"""
    
    # A4 width = 210mm - 40mm margins = 170mm ≈ 6.7 inches
    fig, ax = plt.subplots(figsize=(6.5, 4), dpi=300)
    
    # ... existing chart code ...
    
    plt.tight_layout()  # Prevent overflow
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    
    plt.close(fig)
    return buf.getvalue()
```

## Step 2.9: Test Function 3 - Policy Validation (1.5 hours)

Create `tests/test_policy_validation.py`:

```python
"""
Multi-Parcel Policy Validation Suite
Tests: FAR calculation, household count consistency
"""

import pytest
from app.engines.multi_parcel_optimizer_v241 import MultiParcelOptimizerV241
from app.engines.capacity_engine_v241 import CapacityEngineV241

class TestPolicyValidation:
    
    @pytest.fixture
    def multi_parcel_engine(self):
        return MultiParcelOptimizerV241()
    
    @pytest.fixture
    def capacity_engine(self):
        return CapacityEngineV241()
    
    def test_far_calculation_accuracy(self, multi_parcel_engine):
        """FAR calculation must match LH policy table"""
        test_cases = [
            {
                'parcels': [
                    {'area': 200, 'zoning': '제2종일반주거지역'},
                    {'area': 300, 'zoning': '제2종일반주거지역'}
                ],
                'expected_far': 250.0  # From LH policy
            },
            # Add 10+ test cases with known results
        ]
        
        for case in test_cases:
            result = multi_parcel_engine.calculate_merged_far(case['parcels'])
            assert abs(result - case['expected_far']) < 0.01, \
                   f"FAR {result} != expected {case['expected_far']}"
    
    def test_household_count_consistency(self, multi_parcel_engine, capacity_engine):
        """Household count must match between engines"""
        parcels = [
            {'area': 500, 'zoning': '제2종일반주거지역'}
        ]
        
        count_multi = multi_parcel_engine.calculate_households(parcels)
        count_capacity = capacity_engine.calculate_supplyable_units(parcels)
        
        assert count_multi == count_capacity, \
               f"Household count mismatch: {count_multi} (Multi) vs {count_capacity} (Capacity)"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

## Step 2.10: Fix Issue 9 & 10 - Cross-Engine Validation (1 hour)

**File to Edit**: `app/engines/multi_parcel_optimizer_v241.py`

**Add** cross-validation method:

```python
def calculate_merged_far_validated(self, parcels):
    """Calculate FAR with cross-validation"""
    
    # 1. Calculate using Multi-Parcel logic
    total_area = sum(p['area'] for p in parcels)
    zoning = self._get_dominant_zoning(parcels)
    far = self.zoning_rules[zoning]["max_far"]
    
    # 2. Cross-validate with Capacity Engine
    capacity_result = self.capacity_engine.analyze(parcels)
    
    if abs(far - capacity_result.far) > 0.01:
        raise PolicyViolationError(
            f"FAR mismatch: {far} (Multi-Parcel) vs {capacity_result.far} (Capacity)"
        )
    
    return far

def get_verified_household_count(self, parcels):
    """Get household count with reconciliation"""
    
    count_multi = self._calculate_households(parcels)
    count_capacity = self.capacity_engine.calculate_supplyable_units(parcels)
    
    if count_multi != count_capacity:
        logger.warning(
            f"Household count mismatch: {count_multi} (Multi) vs {count_capacity} (Capacity)"
        )
        # Use more conservative estimate
        return min(count_multi, count_capacity)
    
    return count_multi
```

## Step 2.11: Test Function 4 - Dashboard E2E (1.5 hours)

Create `tests/test_dashboard_e2e.py`:

```python
"""
Dashboard End-to-End Test Suite
Uses Selenium for full browser automation
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class TestDashboardE2E:
    
    @pytest.fixture
    def driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    def test_report_generation_flow(self, driver):
        """Test full flow: button click → PDF generation → download"""
        
        # 1. Load dashboard
        driver.get("https://8000-....sandbox.novita.ai/static/admin_dashboard.html")
        
        # 2. Fill land info
        address_field = driver.find_element(By.ID, "address")
        address_field.send_keys("서울시 강남구 역삼동 123")
        
        # 3. Click "Report 3" button
        report_btn = driver.find_element(By.ID, "btn-report-3")
        report_btn.click()
        
        # 4. Wait for loading indicator
        loading = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "loading-spinner"))
        )
        assert loading.is_displayed(), "Loading indicator not shown"
        
        # 5. Wait for PDF download link (2 min timeout for 40p report)
        pdf_link = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.ID, "pdf-download-link"))
        )
        
        assert pdf_link.is_displayed(), "PDF download link not shown"
        
        # 6. Click PDF.js viewer
        pdf_link.click()
        
        # 7. Verify PDF renders correctly
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pdf-viewer-iframe"))
        )
        
        driver.switch_to.frame(iframe)
        page_count_elem = driver.find_element(By.ID, "numPages")
        page_count = int(page_count_elem.text)
        
        assert 25 <= page_count <= 40, \
               f"Report 3 has {page_count} pages, expected 25-40"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Note**: Requires `selenium` and `chromedriver`:
```bash
pip install selenium
# Download chromedriver matching your Chrome version
```

## Step 2.12: Test Functions 5 & 6 - Alias & Narrative (1 hour)

Create `tests/test_alias_narrative.py`:

```python
"""
Alias Engine & Narrative Placement Test Suite
"""

import pytest
from app.engines.alias_engine_v241 import AliasEngineV241
from app.services.report_generator_v241_enhanced import ReportGeneratorV241Enhanced
from bs4 import BeautifulSoup
import re

class TestAliasNarrative:
    
    def test_no_hardcoded_formatters(self):
        """All templates must use Alias Engine, no hardcoded formatters"""
        
        template_file = "app/services/report_generator_v241_enhanced.py"
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find hardcoded number formatters
        hardcoded_patterns = [
            r'\{[^}]*:,.0f\}',  # e.g., {value:,.0f}
            r'\{[^}]*:,.2f\}',  # e.g., {value:,.2f}
        ]
        
        for pattern in hardcoded_patterns:
            matches = re.findall(pattern, content)
            assert len(matches) == 0, \
                   f"Found hardcoded formatters: {matches[:5]}"
    
    def test_narratives_placed_before_visuals(self):
        """Narratives must be placed BEFORE tables/figures, not after"""
        
        generator = ReportGeneratorV241Enhanced()
        parcel_data = {/* sample data */}
        
        result = generator.generate_report("extended", parcel_data)
        html = result['html']
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all sections with narratives + visuals
        sections = soup.find_all('div', class_='section')
        
        for section in sections:
            section_html = str(section)
            
            # Find positions of narrative and visual elements
            narrative_pos = section_html.find('class="narrative"')
            table_pos = section_html.find('<table')
            figure_pos = section_html.find('<figure')
            
            visual_pos = min([p for p in [table_pos, figure_pos] if p != -1], default=9999)
            
            if narrative_pos != -1 and visual_pos != -1:
                assert narrative_pos < visual_pos, \
                       f"Narrative after visual in section: {section_html[:200]}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

## Step 2.13: Fix Remaining Issues (1 hour)

Based on test failures, fix remaining issues systematically:

1. **Issue 12 - Alias Engine Coverage**: Replace all hardcoded formatters
2. **Issue 13 - Narrative Placement**: Implement smart insertion algorithm

---

# PHASE 3: CI/CD + VISUAL REGRESSION (2 days)

## Objective
Set up automated quality gates to prevent regressions and ensure 100% quality maintained.

## Step 3.1: GitHub Actions Workflow (2 hours)

Create `.github/workflows/quality-checks.yml`:

```yaml
name: ZeroSite Quality Checks

on:
  push:
    branches: [ v24.1_gap_closing, main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov selenium
    
    - name: Run PDF Quality Tests
      run: |
        pytest tests/test_pdf_quality.py -v --cov=app/services
    
    - name: Run Visualization Tests
      run: |
        pytest tests/test_visualization_quality.py -v
    
    - name: Run Policy Validation Tests
      run: |
        pytest tests/test_policy_validation.py -v
    
    - name: Generate Test PDFs
      run: |
        python tests/generate_test_pdfs.py
    
    - name: Upload Test Artifacts
      uses: actions/upload-artifact@v3
      with:
        name: test-pdfs
        path: test_pdfs_output/
    
    - name: Check Coverage
      run: |
        pytest --cov=app --cov-report=html
        coverage_pct=$(coverage report | grep TOTAL | awk '{print $NF}' | sed 's/%//')
        if [ $coverage_pct -lt 90 ]; then
          echo "Coverage $coverage_pct% is below 90% threshold"
          exit 1
        fi
```

## Step 3.2: Visual Regression Testing with Percy (4 hours)

Install Percy:
```bash
npm install --save-dev @percy/cli @percy/webdriver-utils
```

Create `tests/test_visual_regression.py`:

```python
"""
Visual Regression Testing using Percy
Captures screenshots and compares against baseline
"""

from selenium import webdriver
from percy import percy_snapshot
import pytest

class TestVisualRegression:
    
    @pytest.fixture
    def driver(self):
        driver = webdriver.Chrome()
        yield driver
        driver.quit()
    
    def test_report_1_visual(self, driver):
        """Visual regression test for Report 1"""
        driver.get("http://localhost:8000/test_pdfs_output/brief_test_*.html")
        percy_snapshot(driver, 'Report 1 - Brief')
    
    def test_report_3_visual(self, driver):
        """Visual regression test for Report 3"""
        driver.get("http://localhost:8000/test_pdfs_output/extended_test_*.html")
        percy_snapshot(driver, 'Report 3 - Extended')
    
    # ... repeat for all 5 reports
```

Run visual tests:
```bash
export PERCY_TOKEN=your_percy_token
npx percy exec -- pytest tests/test_visual_regression.py
```

## Step 3.3: Pre-Commit Hooks (1 hour)

Install pre-commit:
```bash
pip install pre-commit
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  
  - repo: local
    hooks:
      - id: pdf-quality-tests
        name: PDF Quality Tests
        entry: pytest tests/test_pdf_quality.py -v
        language: system
        pass_filenames: false
      
      - id: no-hardcoded-formatters
        name: Check for hardcoded formatters
        entry: pytest tests/test_alias_narrative.py::TestAliasNarrative::test_no_hardcoded_formatters -v
        language: system
        pass_filenames: false
```

Install hooks:
```bash
pre-commit install
```

## Step 3.4: Quality Gate Dashboard (3 hours)

Create `quality_dashboard.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>ZeroSite v24.1 Quality Dashboard</title>
    <style>
        .metric { display: inline-block; margin: 20px; padding: 20px; border: 2px solid #ccc; }
        .pass { border-color: green; }
        .fail { border-color: red; }
    </style>
</head>
<body>
    <h1>ZeroSite v24.1 Quality Dashboard</h1>
    
    <div class="metric pass">
        <h3>Test Coverage</h3>
        <p id="coverage">98%</p>
    </div>
    
    <div class="metric pass">
        <h3>PDF Quality Tests</h3>
        <p id="pdf-tests">6/6 Passing</p>
    </div>
    
    <div class="metric pass">
        <h3>Visual Regression</h3>
        <p id="visual-tests">5/5 Reports OK</p>
    </div>
    
    <div class="metric pass">
        <h3>Policy Validation</h3>
        <p id="policy-tests">10/10 Test Cases OK</p>
    </div>
    
    <script>
        // Auto-refresh from CI/CD results
        setInterval(fetchResults, 60000);
        
        function fetchResults() {
            fetch('/api/quality-metrics')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('coverage').textContent = data.coverage + '%';
                    // ... update other metrics
                });
        }
    </script>
</body>
</html>
```

## Step 3.5: Monitoring & Alerts (2 hours)

Set up Sentry for error tracking:

```python
# app/__init__.py
import sentry_sdk

sentry_sdk.init(
    dsn="your_sentry_dsn",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)
```

Add performance monitoring:

```python
# app/api/v24_1/main.py
from sentry_sdk import start_transaction

@app.post("/report-generate")
async def generate_report(request: ReportRequest):
    with start_transaction(op="report", name="generate_report"):
        result = generator.generate_report(
            report_type=request.report_type,
            parcel_data=request.parcel_data
        )
        return result
```

---

# FINAL CHECKLIST

After completing all 3 phases, verify:

## Phase 1 Completion ✅
- [ ] All 5 test PDFs generated
- [ ] Visual inspection report documented
- [ ] Priority fix list created

## Phase 2 Completion ✅
- [ ] All 6 test functions implemented
- [ ] `pytest tests/ -v` shows 100% pass rate
- [ ] All 18 issues fixed and verified
- [ ] Report 3 generates 25-40 pages
- [ ] All charts at 300dpi
- [ ] Korean fonts render correctly
- [ ] Headers/footers on all pages

## Phase 3 Completion ✅
- [ ] GitHub Actions workflow passing
- [ ] Visual regression tests baseline captured
- [ ] Pre-commit hooks active
- [ ] Quality dashboard deployed
- [ ] Sentry monitoring active
- [ ] Coverage ≥ 90%

---

# SUCCESS CRITERIA

**TRUE 100% Production Quality Achieved When:**

1. ✅ All pytest tests pass (0 failures)
2. ✅ Test coverage ≥ 90%
3. ✅ Visual regression tests show 0 differences
4. ✅ Manual QA checklist 100% ✅
5. ✅ Report 3 consistently generates 25-40 pages
6. ✅ All visualizations at 300dpi
7. ✅ Zero hardcoded formatters (100% Alias Engine)
8. ✅ Dashboard E2E flow completes in < 2 minutes
9. ✅ CI/CD pipeline green on all checks
10. ✅ Stakeholder approval on sample PDFs

---

**END OF IMPLEMENTATION GUIDE**

**Estimated Total Time**: 16-23 hours  
**Current Progress**: 70% → **100%** (after completion)  
**Next Action**: Start with Phase 1, Step 1.1

**Repository**: https://github.com/hellodesignthinking-png/LHproject  
**Branch**: v24.1_gap_closing

**Document Status**: ✅ Complete Implementation Plan  
**Purpose**: Enable next developer to execute all remaining work systematically

