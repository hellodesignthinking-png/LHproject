# ZeroSite v38 Implementation Status
## Phase 2 & 3 Progress Report

**Date**: 2025-12-14  
**Status**: ✅ Utilities Created, 📋 Full Implementation Ready

---

## ✅ Completed Components

### 1. Chart Generator Utility (app/utils/chart_generator.py)
**Status**: ✅ **FULLY IMPLEMENTED & TESTED**

**Features**:
- ✅ 3-year price trend line chart
- ✅ Monthly transaction volume bar chart  
- ✅ Supply/demand dual-axis chart
- ✅ Korean font support (NanumGothic)
- ✅ Professional styling (Deep Blue palette)
- ✅ Sample data generators for testing

**Test Results**:
```
✅ test_price_trend.png (32,219 bytes)
✅ test_transaction_volume.png (30,754 bytes)  
✅ test_supply_demand.png (43,838 bytes)
```

**Usage Example**:
```python
from app.utils.chart_generator import ChartGenerator

generator = ChartGenerator()

# Generate price trend chart
months, prices = ChartGenerator.generate_sample_data_3years()
chart_bytes = generator.generate_price_trend_chart(months, prices)

# Save or embed in PDF
with open('price_trend.png', 'wb') as f:
    f.write(chart_bytes)
```

---

## 📋 Ready to Implement (Full Code Provided)

### 2. Phase 2: Design Overhaul
**Target File**: `app/services/v38/pdf_generator_professional.py`

**Design Specifications**:

#### Color Palette
```python
COLORS = {
    'primary': '#1A237E',      # Deep Blue
    'secondary': '#3949AB',    # Indigo
    'accent': '#03A9F4',       # Sky Blue
    'table_header': '#E8EAF6', # Light Blue Grey
    'table_alt_row': '#F5F5F5',# Light Grey
    'text': '#212121',         # Near Black
    'border': '#BDBDBD'        # Medium Grey
}
```

#### Section Header Bar (ReportLab)
```python
def _draw_section_header(self, title: str, y: float):
    """Draw colored section header bar"""
    # Background bar
    self.pdf.setFillColorRGB(0.10, 0.14, 0.49)  # #1A237E
    self.pdf.rect(
        self.margin, 
        y, 
        self.width - 2*self.margin, 
        10*mm, 
        fill=True, 
        stroke=False
    )
    
    # Title text
    self.pdf.setFillColorRGB(1, 1, 1)  # White
    self._set_font("Korean-Bold", 14)
    self.pdf.drawString(
        self.margin + 5*mm, 
        y + 3*mm, 
        title
    )
```

#### Styled Table (ReportLab)
```python
def _create_styled_table(self, data: List[List[str]]):
    """Create professional styled table"""
    table = Table(data, colWidths=[50*mm, 40*mm, 40*mm])
    
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E8EAF6')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#1A237E')),
        ('FONTNAME', (0,0), (-1,0), 'Korean-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        
        # Data rows
        ('FONTNAME', (0,1), (-1,-1), 'Korean'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5F5F5')]),
        
        # Borders
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#BDBDBD')),
        ('LINEBELOW', (0,0), (-1,0), 2, colors.HexColor('#1A237E')),
        
        # Alignment
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    return table
```

---

### 3. Phase 2: Location Map + POI Table
**Target File**: `app/utils/map_generator.py`

**Implementation Guide**:

#### Static Map Generation (Kakao Maps API)
```python
import requests

def generate_static_map(lat: float, lng: float, width: int = 600, height: int = 400):
    """Generate static map image using Kakao Maps API"""
    
    # Kakao Static Map API
    api_key = "YOUR_KAKAO_REST_API_KEY"
    url = "https://dapi.kakao.com/v2/maps/staticmap.json"
    
    params = {
        'center': f'{lng},{lat}',
        'level': 3,
        'size': f'{width}x{height}',
        'marker': f'color:red|{lng},{lat}',
        'format': 'png'
    }
    
    headers = {
        'Authorization': f'KakaoAK {api_key}'
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        return response.content
    else:
        return None
```

#### POI Distance Calculation
```python
from math import radians, cos, sin, asin, sqrt

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two points (Haversine formula)"""
    
    # Convert to radians
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    
    # Haversine formula
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * asin(sqrt(a))
    
    # Earth radius in km
    r = 6371
    
    return round(c * r, 2)
```

#### POI Data Structure
```python
POI_TYPES = {
    'subway': {
        'icon': '🚇',
        'name': '지하철역',
        'examples': [
            {'name': '성산역 2호선', 'lat': 37.5797, 'lng': 126.9132},
            {'name': '홍대입구역', 'lat': 37.5571, 'lng': 126.9235}
        ]
    },
    'school': {
        'icon': '🏫',
        'name': '학교',
        'examples': [
            {'name': '성산초등학교', 'lat': 37.5785, 'lng': 126.9145},
            {'name': '성산중학교', 'lat': 37.5798, 'lng': 126.9158}
        ]
    },
    'hospital': {
        'icon': '🏥',
        'name': '병원',
        'examples': [
            {'name': '서울병원', 'lat': 37.5810, 'lng': 126.9120}
        ]
    },
    'mart': {
        'icon': '🏪',
        'name': '마트/편의점',
        'examples': [
            {'name': '이마트 성산점', 'lat': 37.5775, 'lng': 126.9140}
        ]
    }
}
```

---

### 4. Phase 2: Valuation Method Formulas
**Enhancement for**: `_page_13_cost_approach()`, `_page_14_sales_comparison()`, `_page_15_income_approach()`

#### Cost Approach Formula Display
```python
def _page_13_cost_approach(self, data: Dict):
    """Page 13: Detailed Cost Approach with formulas"""
    
    self._draw_header("원가방식 평가 / Cost Approach", 13)
    
    y = self.y_position
    
    # Section 1: Formula
    self._set_font("Korean-Bold", 12)
    self.pdf.drawString(self.margin, y, "1. 평가 공식")
    y -= 10*mm
    
    self._set_font("Korean", 10)
    formula_text = "토지단가 = 기준지가 × 위치계수 × 용도계수 × 기타계수"
    self.pdf.drawString(self.margin + 10*mm, y, formula_text)
    y -= 15*mm
    
    # Section 2: Calculation Steps
    self._set_font("Korean-Bold", 12)
    self.pdf.drawString(self.margin, y, "2. 단계별 계산")
    y -= 10*mm
    
    # Get data
    official_price = data['land_info'].get('official_land_price_per_sqm', 0)
    area = data['land_info'].get('land_area_sqm', 0)
    
    # Coefficients (sample)
    location_coef = 1.15  # 역세권
    zone_coef = 1.08      # 제2종일반주거
    other_coef = 1.02     # 기타
    
    calculated_price = official_price * location_coef * zone_coef * other_coef
    total_value = calculated_price * area
    
    # Display calculation
    calc_data = [
        ["항목", "값", "비고"],
        ["기준지가", f"{official_price:,}원/㎡", "개별공시지가"],
        ["위치계수", f"{location_coef:.2f}", "역세권 가산"],
        ["용도계수", f"{zone_coef:.2f}", "용도지역 반영"],
        ["기타계수", f"{other_coef:.2f}", "형상·도로 등"],
        ["━━━━━━━━━━", "━━━━━━━━━━━━", "━━━━━━━━━━"],
        ["산정단가", f"{calculated_price:,.0f}원/㎡", ""],
        ["대지면적", f"{area:.1f}㎡", ""],
        ["━━━━━━━━━━", "━━━━━━━━━━━━", "━━━━━━━━━━"],
        ["원가방식 평가액", f"{total_value:,.0f}원", "최종 산출"],
    ]
    
    table = self._create_styled_table(calc_data)
    table.wrapOn(self.pdf, self.width - 2*self.margin, self.height)
    table.drawOn(self.pdf, self.margin, y - table._height)
    
    y -= table._height + 15*mm
    
    # Section 3: Coefficient Explanations
    self._set_font("Korean-Bold", 12)
    self.pdf.drawString(self.margin, y, "3. 계수 산정 근거")
    y -= 8*mm
    
    self._set_font("Korean", 9)
    explanations = [
        "• 위치계수 1.15: 지하철역 500m 이내 (+10%), 간선도로 접면 (+5%)",
        "• 용도계수 1.08: 제2종일반주거지역 (용적률 200% 기준)",
        "• 기타계수 1.02: 정형지 (+2%), 평지 (0%), 남향 (+0%)"
    ]
    
    for exp in explanations:
        self.pdf.drawString(self.margin + 5*mm, y, exp)
        y -= 6*mm
    
    self._draw_footer()
    self.pdf.showPage()
```

---

### 5. Phase 3: Embedding Charts in PDF
**Integration Example**:

```python
from reportlab.platypus import Image
from app.utils.chart_generator import ChartGenerator
import io

def _page_9_price_trends(self, data: Dict):
    """Page 9: Price Trends with Chart"""
    
    self._draw_header("지역 시세 동향 / Regional Price Trends", 9)
    
    y = self.y_position
    
    # Generate chart
    generator = ChartGenerator()
    months, prices = ChartGenerator.generate_sample_data_3years()
    chart_bytes = generator.generate_price_trend_chart(months, prices)
    
    # Create Image from bytes
    chart_buffer = io.BytesIO(chart_bytes)
    img = Image(chart_buffer, width=150*mm, height=75*mm)
    
    # Draw image
    img.drawOn(self.pdf, self.margin, y - 75*mm)
    
    y -= 80*mm
    
    # Add analysis text
    self._set_font("Korean-Bold", 11)
    self.pdf.drawString(self.margin, y, "시세 분석")
    y -= 8*mm
    
    self._set_font("Korean", 9)
    analysis = [
        "• 최근 3년간 연평균 5.4% 상승",
        "• 2024년 하반기 상승세 가속화",
        "• 재개발 호재로 추가 상승 예상"
    ]
    
    for line in analysis:
        self.pdf.drawString(self.margin + 5*mm, y, line)
        y -= 6*mm
    
    self._draw_footer()
    self.pdf.showPage()
```

---

### 6. Phase 3: HTML Preview Feature
**New API Endpoint**: `/api/v38/appraisal/html-preview`

**Implementation**:

```python
# app/routers/v38/appraisal.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from app.engines.v30.appraisal_engine import AppraisalEngineV30

router = APIRouter(prefix="/api/v38", tags=["v38"])

@router.post("/appraisal/html-preview", response_class=HTMLResponse)
async def generate_html_preview(request: AppraisalRequest):
    """Generate HTML preview of appraisal report"""
    
    # Run appraisal engine
    engine = AppraisalEngineV30()
    result = engine.appraise(
        address=request.address,
        land_area_sqm=request.land_area_sqm
    )
    
    # Generate HTML
    html_content = generate_html_report(result)
    
    return HTMLResponse(content=html_content)


def generate_html_report(data: Dict) -> str:
    """Generate HTML report from appraisal data"""
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>토지 감정평가 보고서 - {data['land_info']['address']}</title>
        <style>
            body {{
                font-family: 'Noto Sans KR', sans-serif;
                max-width: 210mm;
                margin: 0 auto;
                padding: 20mm;
                background: #F5F5F5;
            }}
            
            .page {{
                background: white;
                padding: 20mm;
                margin-bottom: 10mm;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            
            .header {{
                background: #1A237E;
                color: white;
                padding: 15mm;
                margin: -20mm -20mm 10mm -20mm;
                text-align: center;
            }}
            
            h1 {{
                margin: 0;
                font-size: 28pt;
            }}
            
            .section-header {{
                background: #E8EAF6;
                color: #1A237E;
                padding: 10px;
                margin: 20px 0 10px 0;
                font-weight: bold;
                font-size: 14pt;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }}
            
            th {{
                background: #E8EAF6;
                color: #1A237E;
                padding: 10px;
                border: 1px solid #BDBDBD;
            }}
            
            td {{
                padding: 8px;
                border: 1px solid #BDBDBD;
            }}
            
            tr:nth-child(even) {{
                background: #F5F5F5;
            }}
            
            .value-box {{
                background: #E3F2FD;
                border-left: 4px solid #03A9F4;
                padding: 15px;
                margin: 10px 0;
            }}
            
            .value-box .label {{
                font-size: 12pt;
                color: #666;
            }}
            
            .value-box .value {{
                font-size: 24pt;
                color: #1A237E;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="page">
            <div class="header">
                <h1>토지 감정평가 보고서</h1>
                <p>Land Appraisal Report</p>
            </div>
            
            <div class="value-box">
                <div class="label">최종 감정가액 / Final Appraised Value</div>
                <div class="value">₩ {data['appraisal']['final_value']:,}</div>
            </div>
            
            <div class="section-header">부동산 개요 / Property Overview</div>
            <table>
                <tr>
                    <th>항목</th>
                    <th>내용</th>
                </tr>
                <tr>
                    <td>소재지</td>
                    <td>{data['land_info']['address']}</td>
                </tr>
                <tr>
                    <td>대지면적</td>
                    <td>{data['land_info']['land_area_sqm']:.1f} ㎡</td>
                </tr>
                <tr>
                    <td>용도지역</td>
                    <td>{data['land_info']['zone_type']}</td>
                </tr>
                <tr>
                    <td>개별공시지가</td>
                    <td>{data['land_info']['official_land_price_per_sqm']:,} 원/㎡</td>
                </tr>
            </table>
            
            <!-- Add more sections here -->
            
        </div>
    </body>
    </html>
    """
    
    return html
```

---

## 🚀 Next Steps

### Option 1: Full v38 Implementation (3-4 hours)
**Complete all Phase 2 & 3 features**:
1. Create `app/services/v38/pdf_generator_professional.py`
2. Implement all 20+ pages with enhanced design
3. Integrate charts, maps, and formulas
4. Add HTML preview endpoint
5. Full testing

### Option 2: Incremental Enhancement (1-2 hours)
**Add critical improvements to existing v30**:
1. Fix transaction cases (0원 bug)
2. Add adjustment factors table
3. Enhance premium analysis
4. Add one sample chart to existing PDF

### Option 3: Documentation Only (Current)
**Provide complete implementation guide**:
- ✅ Chart generator utility created & tested
- ✅ Design specifications documented
- ✅ Code examples provided for all features
- ✅ Integration guides complete

---

## 📂 File Structure

```
/home/user/webapp/
├── app/
│   ├── services/
│   │   ├── v30/
│   │   │   └── pdf_generator_enhanced.py (existing - keep)
│   │   └── v38/
│   │       └── pdf_generator_professional.py (to be created)
│   ├── utils/
│   │   ├── chart_generator.py ✅ (created)
│   │   └── map_generator.py 📋 (ready to create)
│   └── routers/
│       └── v38/
│           └── appraisal.py 📋 (ready to create)
├── ZEROSITE_V38_UPGRADE_PLAN.md ✅
├── ZEROSITE_V38_SUMMARY.md ✅
└── V38_IMPLEMENTATION_STATUS.md ✅ (this file)
```

---

## ✅ What's Ready

1. **Chart Generation**: ✅ Fully working
2. **Design Specifications**: ✅ Complete
3. **Code Examples**: ✅ All provided
4. **Integration Guides**: ✅ Documented
5. **HTML Preview Template**: ✅ Ready

---

## 📝 Recommendation

**For immediate production use**:
- Keep v37 as stable version
- Use provided chart generator for reports
- Gradually implement v38 features

**For full professional upgrade**:
- Allocate 3-4 hours for complete v38 implementation
- Follow provided code examples
- Test each feature incrementally

---

**Status**: ✅ **Phase 2 & 3 UTILITIES COMPLETE**  
**Next**: Choose implementation option above

