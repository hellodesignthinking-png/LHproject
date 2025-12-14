"""
ZeroSite v38 - HTML Preview API
Generate interactive HTML preview of appraisal reports
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json

router = APIRouter(prefix="/api/v38", tags=["v38-preview"])


class AppraisalRequest(BaseModel):
    """Appraisal request schema"""
    address: str
    land_area_sqm: float
    zone_type: Optional[str] = None
    asking_price: Optional[float] = None


def generate_html_report(data: Dict[str, Any]) -> str:
    """Generate HTML report from appraisal data"""
    
    # Extract data
    land_info = data.get('land_info', {})
    appraisal = data.get('appraisal', {})
    comparables = data.get('comparables', [])[:5]  # Top 5
    
    address = land_info.get('address', 'N/A')
    land_area = land_info.get('land_area_sqm', 0)
    zone_type = land_info.get('zone_type', 'N/A')
    official_price = land_info.get('official_land_price_per_sqm', 0)
    
    final_value = appraisal.get('final_value', 0)
    cost_value = appraisal.get('cost_approach', {}).get('value', 0)
    sales_value = appraisal.get('sales_comparison', {}).get('value', 0)
    income_value = appraisal.get('income_approach', {}).get('value', 0)
    
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>토지 감정평가 보고서 - {address}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, #1A237E 0%, #3949AB 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .value-box {{
            background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
            border-left: 5px solid #03A9F4;
            padding: 30px;
            margin: 30px 0;
            border-radius: 5px;
        }}
        
        .value-box .label {{
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
        }}
        
        .value-box .value {{
            font-size: 36px;
            color: #1A237E;
            font-weight: bold;
        }}
        
        .section {{
            margin: 40px 0;
        }}
        
        .section-header {{
            background: #E8EAF6;
            color: #1A237E;
            padding: 15px 20px;
            font-size: 18px;
            font-weight: bold;
            border-left: 5px solid #3949AB;
            margin-bottom: 20px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th {{
            background: #E8EAF6;
            color: #1A237E;
            padding: 12px;
            text-align: left;
            font-weight: bold;
            border: 1px solid #BDBDBD;
        }}
        
        td {{
            padding: 10px 12px;
            border: 1px solid #BDBDBD;
        }}
        
        tr:nth-child(even) {{
            background: #F5F5F5;
        }}
        
        tr:hover {{
            background: #E3F2FD;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .info-card {{
            background: #F5F5F5;
            padding: 20px;
            border-radius: 5px;
            border-left: 3px solid #03A9F4;
        }}
        
        .info-card .title {{
            font-size: 12px;
            color: #666;
            margin-bottom: 8px;
        }}
        
        .info-card .value {{
            font-size: 20px;
            color: #1A237E;
            font-weight: bold;
        }}
        
        .chart-placeholder {{
            background: #F5F5F5;
            padding: 60px;
            text-align: center;
            color: #999;
            border: 2px dashed #DDD;
            margin: 20px 0;
        }}
        
        .footer {{
            background: #F5F5F5;
            padding: 30px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }}
        
        .badge-high {{
            background: #4CAF50;
            color: white;
        }}
        
        .badge-medium {{
            background: #FF9800;
            color: white;
        }}
        
        .badge-low {{
            background: #F44336;
            color: white;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
            }}
            
            .header {{
                background: #1A237E;
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }}
            
            @page {{
                margin: 1cm;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>토지 감정평가 보고서</h1>
            <div class="subtitle">Land Appraisal Report</div>
            <div class="subtitle" style="margin-top: 10px;">ZeroSite v38.0 Professional Edition</div>
        </div>
        
        <!-- Content -->
        <div class="content">
            <!-- Final Value -->
            <div class="value-box">
                <div class="label">최종 감정가액 / Final Appraised Value</div>
                <div class="value">₩ {final_value:,.0f}</div>
                <div class="label" style="margin-top: 10px;">
                    평당 가격: ₩ {final_value/land_area*3.3058:,.0f} / 평 | 
                    평방미터당: ₩ {final_value/land_area:,.0f} / ㎡
                </div>
            </div>
            
            <!-- Property Overview -->
            <div class="section">
                <div class="section-header">부동산 개요 / Property Overview</div>
                
                <div class="info-grid">
                    <div class="info-card">
                        <div class="title">소재지</div>
                        <div class="value" style="font-size: 16px;">{address}</div>
                    </div>
                    
                    <div class="info-card">
                        <div class="title">대지면적</div>
                        <div class="value">{land_area:.1f} ㎡</div>
                        <div class="title">({land_area * 0.3025:.1f} 평)</div>
                    </div>
                    
                    <div class="info-card">
                        <div class="title">용도지역</div>
                        <div class="value" style="font-size: 16px;">{zone_type}</div>
                    </div>
                    
                    <div class="info-card">
                        <div class="title">개별공시지가</div>
                        <div class="value">{official_price:,.0f}</div>
                        <div class="title">원/㎡</div>
                    </div>
                </div>
            </div>
            
            <!-- Valuation Methods -->
            <div class="section">
                <div class="section-header">평가 방법별 산출가액 / Valuation by Method</div>
                
                <table>
                    <thead>
                        <tr>
                            <th>평가 방법</th>
                            <th>산출가액 (원)</th>
                            <th>평당 가격 (원/평)</th>
                            <th>가중치</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>원가방식 (Cost Approach)</strong></td>
                            <td>{cost_value:,.0f}</td>
                            <td>{cost_value/land_area*3.3058:,.0f}</td>
                            <td>30%</td>
                        </tr>
                        <tr>
                            <td><strong>거래사례비교법 (Sales Comparison)</strong></td>
                            <td>{sales_value:,.0f}</td>
                            <td>{sales_value/land_area*3.3058:,.0f}</td>
                            <td>50%</td>
                        </tr>
                        <tr>
                            <td><strong>수익환원법 (Income Approach)</strong></td>
                            <td>{income_value:,.0f}</td>
                            <td>{income_value/land_area*3.3058:,.0f}</td>
                            <td>20%</td>
                        </tr>
                        <tr style="background: #E8EAF6; font-weight: bold;">
                            <td><strong>최종 감정가액 (Final Value)</strong></td>
                            <td style="color: #1A237E;">{final_value:,.0f}</td>
                            <td style="color: #1A237E;">{final_value/land_area*3.3058:,.0f}</td>
                            <td>100%</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- Comparable Transactions -->
            <div class="section">
                <div class="section-header">거래사례 비교 / Comparable Transactions (Top 5)</div>
                
                <table>
                    <thead>
                        <tr>
                            <th>번호</th>
                            <th>소재지</th>
                            <th>면적 (㎡)</th>
                            <th>거래가 (원)</th>
                            <th>단가 (원/㎡)</th>
                            <th>거리 (km)</th>
                            <th>거래일</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    # Add comparable transactions
    for idx, comp in enumerate(comparables, 1):
        html += f"""
                        <tr>
                            <td>{idx}</td>
                            <td>{comp.get('address', 'N/A')}</td>
                            <td>{comp.get('area_sqm', 0):.1f}</td>
                            <td>{comp.get('price_total', 0):,.0f}</td>
                            <td>{comp.get('price_per_sqm', 0):,.0f}</td>
                            <td>{comp.get('distance_km', 0):.2f}</td>
                            <td>{comp.get('date', 'N/A')}</td>
                        </tr>
"""
    
    html += """
                    </tbody>
                </table>
            </div>
            
            <!-- Market Analysis Placeholder -->
            <div class="section">
                <div class="section-header">시장 분석 / Market Analysis</div>
                <div class="chart-placeholder">
                    📈 3년 가격 추세 그래프<br>
                    (PDF 버전에서 확인 가능)
                </div>
                <div class="chart-placeholder">
                    📊 월별 거래량 분석<br>
                    (PDF 버전에서 확인 가능)
                </div>
            </div>
            
            <!-- Print Button -->
            <div style="text-align: center; margin: 40px 0;">
                <button onclick="window.print()" style="
                    background: #1A237E;
                    color: white;
                    border: none;
                    padding: 15px 40px;
                    font-size: 16px;
                    border-radius: 5px;
                    cursor: pointer;
                ">
                    🖨️ 인쇄하기 / Print
                </button>
                
                <button onclick="downloadPDF()" style="
                    background: #03A9F4;
                    color: white;
                    border: none;
                    padding: 15px 40px;
                    font-size: 16px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin-left: 10px;
                ">
                    📄 PDF 다운로드 / Download PDF
                </button>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p><strong>ZeroSite Professional Edition v38.0</strong></p>
            <p>이 보고서는 ZeroSite 감정평가 시스템에 의해 자동 생성되었습니다.</p>
            <p>생성 일시: """ + f"{data.get('metadata', {}).get('timestamp', 'N/A')}" + """</p>
            <p style="margin-top: 20px; font-size: 12px; color: #999;">
                본 보고서는 참고용으로 작성되었으며, 법적 효력이 있는 공식 감정평가서가 아닙니다.
            </p>
        </div>
    </div>
    
    <script>
        function downloadPDF() {
            // Redirect to PDF generation endpoint
            const address = '""" + address + """';
            const landArea = """ + str(land_area) + """;
            
            alert('PDF 다운로드 기능은 /api/v30/appraisal/pdf 엔드포인트를 사용하세요.');
            
            // In production, you would:
            // window.location.href = '/api/v30/appraisal/pdf?address=' + encodeURIComponent(address) + '&land_area_sqm=' + landArea;
        }
    </script>
</body>
</html>
"""
    
    return html


@router.post("/appraisal/html-preview", response_class=HTMLResponse)
async def generate_html_preview(request: AppraisalRequest):
    """
    Generate HTML preview of appraisal report
    
    This endpoint provides a fast, interactive HTML preview
    before generating the full PDF report.
    """
    
    try:
        # Import the appraisal engine
        from app.engines.v30.appraisal_engine import AppraisalEngineV30
        
        # Run appraisal
        engine = AppraisalEngineV30()
        result = engine.appraise(
            address=request.address,
            land_area_sqm=request.land_area_sqm
        )
        
        # Check if appraisal was successful
        if not result.get('success', False):
            raise HTTPException(
                status_code=400,
                detail=f"Appraisal failed: {result.get('error', 'Unknown error')}"
            )
        
        # Generate HTML
        html_content = generate_html_report(result)
        
        return HTMLResponse(content=html_content)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate HTML preview: {str(e)}"
        )


@router.get("/appraisal/html-preview/sample", response_class=HTMLResponse)
async def get_sample_html_preview():
    """
    Get a sample HTML preview with mock data
    """
    
    # Mock data for demo
    sample_data = {
        "success": True,
        "land_info": {
            "address": "서울특별시 강남구 역삼동 680-11",
            "land_area_sqm": 661.16,
            "zone_type": "제3종일반주거지역",
            "official_land_price_per_sqm": 27200000
        },
        "appraisal": {
            "final_value": 29242731756,
            "cost_approach": {"value": 25000000000},
            "sales_comparison": {"value": 31000000000},
            "income_approach": {"value": 28000000000}
        },
        "comparables": [
            {
                "address": "서울특별시 강남구 역삼동 123-45",
                "area_sqm": 645.3,
                "price_total": 28500000000,
                "price_per_sqm": 44157000,
                "distance_km": 0.45,
                "date": "2024-11"
            },
            {
                "address": "서울특별시 강남구 역삼동 234-56",
                "area_sqm": 680.2,
                "price_total": 30200000000,
                "price_per_sqm": 44400000,
                "distance_km": 0.67,
                "date": "2024-10"
            },
            {
                "address": "서울특별시 강남구 역삼동 345-67",
                "area_sqm": 625.8,
                "price_total": 27800000000,
                "price_per_sqm": 44420000,
                "distance_km": 0.89,
                "date": "2024-09"
            }
        ],
        "metadata": {
            "timestamp": "2025-12-14 15:00:00"
        }
    }
    
    html_content = generate_html_report(sample_data)
    return HTMLResponse(content=html_content)
