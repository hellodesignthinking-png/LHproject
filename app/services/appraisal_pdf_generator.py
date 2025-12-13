"""
Appraisal PDF Report Generator
Generates detailed PDF reports with calculation steps for all 3 appraisal methods
"""

from typing import Dict
from datetime import datetime
import io
import logging

logger = logging.getLogger(__name__)


class AppraisalPDFGenerator:
    """Generate detailed appraisal PDF reports"""
    
    def generate_pdf_html(self, appraisal_data: Dict) -> str:
        """
        Generate HTML content for PDF conversion
        
        Args:
            appraisal_data: Complete appraisal result from AppraisalEngineV241
        
        Returns:
            HTML string ready for WeasyPrint conversion
        """
        
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 2cm 2cm 3cm 2cm;
            @bottom-center {{
                content: "Page " counter(page) " of " counter(pages);
                font-size: 9pt;
                color: #666;
            }}
        }}
        body {{
            font-family: 'Malgun Gothic', 'Noto Sans KR', sans-serif;
            font-size: 10pt;
            line-height: 1.6;
            color: #333;
        }}
        
        /* Header with Antenna Holdings Branding */
        .header {{
            border-bottom: 4px solid #1a1a2e;
            padding-bottom: 15px;
            margin-bottom: 30px;
            position: relative;
        }}
        .header-logo {{
            width: 200px;
            height: 50px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 16pt;
            border-radius: 5px;
            padding: 10px 20px;
            letter-spacing: 3px;
        }}
        .header-subtitle {{
            color: #666;
            font-size: 9pt;
            margin-top: 5px;
        }}
        
        /* Title */
        h1 {{
            color: #1a1a2e;
            font-size: 22pt;
            font-weight: bold;
            margin: 20px 0 10px 0;
            border-bottom: 3px solid #e94560;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #1a1a2e;
            border-left: 5px solid #e94560;
            padding-left: 15px;
            margin-top: 30px;
            font-size: 16pt;
            font-weight: bold;
        }}
        h3 {{
            color: #333;
            margin-top: 20px;
            font-size: 13pt;
            font-weight: bold;
        }}
        
        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 9.5pt;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 10px;
            text-align: left;
        }}
        th {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f0f8ff;
        }}
        
        /* Summary Box */
        .summary-box {{
            background: linear-gradient(to bottom, #f5f5f5 0%, #e8e8e8 100%);
            border: 2px solid #1a1a2e;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        /* Final Value Highlight */
        .final-value {{
            font-size: 26pt;
            font-weight: bold;
            color: #1a1a2e;
            text-align: center;
            margin: 25px 0;
            padding: 20px;
            background: linear-gradient(135deg, #ffe8ec 0%, #fff0f3 100%);
            border: 3px solid #e94560;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        /* Method Box */
        .method-box {{
            background-color: #f9f9f9;
            border-left: 5px solid #e94560;
            padding: 15px 20px;
            margin: 15px 0;
            border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        
        /* Calculation Steps */
        .calculation-step {{
            padding: 5px 0 5px 20px;
            line-height: 1.8;
            font-size: 10pt;
        }}
        
        /* Badge */
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 9pt;
            font-weight: bold;
            margin: 0 5px;
        }}
        .badge-high {{
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .badge-medium {{
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeeba;
        }}
        .badge-low {{
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        
        /* Footer */
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #1a1a2e;
            font-size: 8pt;
            color: #666;
            text-align: center;
        }}
        .footer-logo {{
            color: #1a1a2e;
            font-weight: bold;
            font-size: 11pt;
            margin-bottom: 10px;
            letter-spacing: 2px;
        }}
        
        /* Watermark */
        .watermark {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 70pt;
            color: rgba(26, 26, 46, 0.03);
            font-weight: bold;
            z-index: -1;
            pointer-events: none;
            letter-spacing: 5px;
        }}
    </style>
</head>
<body>
    <!-- Watermark -->
    <div class="watermark">ANTENNA HOLDINGS</div>
    
    <!-- Header -->
    <div class="header">
        <div class="header-logo">ANTENNA HOLDINGS</div>
        <div class="header-subtitle">안테나홀딩스 · 토지 감정평가 시스템 v24.1</div>
    </div>
    
    <h1>📋 토지 감정평가 보고서</h1>
    
    <div class="summary-box">
        <h3>평가 기본 정보</h3>
        <table>
            <tr>
                <th width="30%">평가 기준일</th>
                <td>{appraisal_data['metadata']['appraisal_date']}</td>
            </tr>
            <tr>
                <th>평가 대상</th>
                <td>{appraisal_data.get('address', 'N/A')}</td>
            </tr>
            <tr>
                <th>토지 면적</th>
                <td>{appraisal_data.get('land_area', 0):,.2f} ㎡</td>
            </tr>
            <tr>
                <th>신뢰도</th>
                <td>
                    <strong>{appraisal_data['confidence_level']}</strong>
                    {'<span class="badge badge-high">높음</span>' if appraisal_data['confidence_level'] == 'HIGH' else 
                     '<span class="badge badge-medium">보통</span>' if appraisal_data['confidence_level'] == 'MEDIUM' else 
                     '<span class="badge badge-low">낮음</span>'}
                </td>
            </tr>
            <tr>
                <th>위치 보정계수</th>
                <td>{appraisal_data['location_factor']}</td>
            </tr>
        </table>
    </div>
    
    <div class="final-value">
        최종 감정평가액: {appraisal_data['final_appraisal_value']:.2f} 억원
    </div>
    
    <h2>📊 감정평가 3방식 종합</h2>
    
    <table>
        <thead>
            <tr>
                <th>평가방법</th>
                <th>평가액 (억원)</th>
                <th>가중치</th>
                <th>비고</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>원가법</strong></td>
                <td style="text-align: right;">{appraisal_data['cost_approach']:.2f}</td>
                <td style="text-align: center;">{appraisal_data['weights']['cost']*100:.0f}%</td>
                <td>재조달원가 - 감가상각</td>
            </tr>
            <tr>
                <td><strong>거래사례비교법</strong></td>
                <td style="text-align: right;">{appraisal_data['sales_comparison']:.2f}</td>
                <td style="text-align: center;">{appraisal_data['weights']['sales']*100:.0f}%</td>
                <td>시장 거래사례 분석</td>
            </tr>
            <tr>
                <td><strong>수익환원법</strong></td>
                <td style="text-align: right;">{appraisal_data['income_approach']:.2f}</td>
                <td style="text-align: center;">{appraisal_data['weights']['income']*100:.0f}%</td>
                <td>순영업소득 환원</td>
            </tr>
            <tr style="background-color: #f0f8ff;">
                <td><strong>최종 평가액 (가중평균)</strong></td>
                <td style="text-align: right;"><strong>{appraisal_data['final_appraisal_value']:.2f}</strong></td>
                <td style="text-align: center;">100%</td>
                <td><strong>종합 평가</strong></td>
            </tr>
        </tbody>
    </table>
    
    <div class="method-box">
        <strong>최종 평가액 계산식:</strong><br>
        ({appraisal_data['cost_approach']:.2f}억원 × {appraisal_data['weights']['cost']*100:.0f}%) + 
        ({appraisal_data['sales_comparison']:.2f}억원 × {appraisal_data['weights']['sales']*100:.0f}%) + 
        ({appraisal_data['income_approach']:.2f}억원 × {appraisal_data['weights']['income']*100:.0f}%) = 
        <strong>{appraisal_data['final_appraisal_value']:.2f}억원</strong>
    </div>
    
    <h2>🔵 원가법 (Cost Approach) 상세</h2>
    
    <div class="method-box">
        <h3>계산 원리</h3>
        <p>원가법은 <strong>재조달원가에서 감가상각을 차감</strong>하여 평가액을 산정합니다.</p>
        <p><strong>평가액 = 토지가액 + (건물 재조달원가 - 감가상각)</strong></p>
    </div>
    
    <div class="calculation-step">
        {'<br>'.join(appraisal_data['breakdown']['cost'].get('calculation_steps', []))}
    </div>
    
    <table>
        <thead>
            <tr>
                <th>항목</th>
                <th>금액 (억원)</th>
                <th>비고</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>토지 가액</td>
                <td style="text-align: right;">{appraisal_data['breakdown']['cost']['land_value']:.2f}</td>
                <td>개별공시지가 기준</td>
            </tr>
            <tr>
                <td>건물 재조달원가</td>
                <td style="text-align: right;">{appraisal_data['breakdown']['cost']['building_value']:.2f}</td>
                <td>{'표준 건축단가 적용' if appraisal_data['breakdown']['cost']['building_value'] > 0 else '건물 없음 (토지만 평가)'}</td>
            </tr>
            <tr>
                <td>감가상각액</td>
                <td style="text-align: right;">-{appraisal_data['breakdown']['cost']['depreciation_amount']:.2f}</td>
                <td>{'경과연수 ' + str(appraisal_data['breakdown']['cost']['building_age']) + '년, 감가율 ' + str(appraisal_data['breakdown']['cost']['depreciation_rate']*100) + '%' if appraisal_data['breakdown']['cost']['building_value'] > 0 else '해당 없음 (토지만 평가)'}</td>
            </tr>
            <tr style="background-color: #f0f8ff;">
                <td><strong>원가법 평가액</strong></td>
                <td style="text-align: right;"><strong>{appraisal_data['breakdown']['cost']['total_value']:.2f}</strong></td>
                <td><strong>최종 산정액</strong></td>
            </tr>
        </tbody>
    </table>
    
    <h2>🟢 거래사례비교법 (Sales Comparison Approach) 상세</h2>
    
    <div class="method-box">
        <h3>계산 원리</h3>
        <p>거래사례비교법은 <strong>인근 거래사례를 시점·위치·개별 요인으로 보정</strong>하여 평가액을 산정합니다.</p>
        <p><strong>평가액 = 토지면적 × (거래사례 보정단가의 가중평균)</strong></p>
    </div>
    
    <div class="method-box">
        <strong>{appraisal_data['breakdown']['sales']['method']}</strong><br>
        {appraisal_data['breakdown']['sales'].get('calculation_details', {}).get('explanation', 'N/A')}
    </div>
    
"""
        
        # 거래사례 상세 표시
        calc_details = appraisal_data['breakdown']['sales'].get('calculation_details', {})
        if 'cases' in calc_details and calc_details['cases']:
            html += """
    <h3>거래사례 보정표</h3>
    <table>
        <thead>
            <tr>
                <th>사례</th>
                <th>거래단가 (원/㎡)</th>
                <th>시점보정</th>
                <th>위치보정</th>
                <th>개별보정</th>
                <th>보정후단가 (원/㎡)</th>
                <th>가중치</th>
            </tr>
        </thead>
        <tbody>
"""
            for case in calc_details['cases']:
                html += f"""
            <tr>
                <td>사례 {case['case_num']}</td>
                <td style="text-align: right;">{case['base_price']:,.0f}</td>
                <td style="text-align: center;">{case['time_adj']:.2f}</td>
                <td style="text-align: center;">{case['location_adj']:.2f}</td>
                <td style="text-align: center;">{case['individual_adj']:.2f}</td>
                <td style="text-align: right;"><strong>{case['adjusted_price']:,.0f}</strong></td>
                <td style="text-align: center;">{case['weight']*100:.0f}%</td>
            </tr>
"""
            
            weighted_avg = calc_details.get('weighted_avg_price', 0)
            html += f"""
            <tr style="background-color: #f0f8ff;">
                <td colspan="5"><strong>가중평균 단가</strong></td>
                <td style="text-align: right;"><strong>{weighted_avg:,.0f}</strong></td>
                <td style="text-align: center;">100%</td>
            </tr>
        </tbody>
    </table>
"""
        
        html += f"""
    <table>
        <thead>
            <tr>
                <th>항목</th>
                <th>금액</th>
                <th>비고</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>최종 평가단가</td>
                <td style="text-align: right;">{appraisal_data['breakdown']['sales']['price_per_sqm']:,} 원/㎡</td>
                <td>거래사례 보정 후</td>
            </tr>
            <tr>
                <td>토지 면적</td>
                <td style="text-align: right;">{appraisal_data.get('land_area', 0):,.2f} ㎡</td>
                <td>평가 대상 토지</td>
            </tr>
            <tr style="background-color: #f0f8ff;">
                <td><strong>거래사례비교법 평가액</strong></td>
                <td style="text-align: right;"><strong>{appraisal_data['breakdown']['sales']['total_value']:.2f} 억원</strong></td>
                <td><strong>최종 산정액</strong></td>
            </tr>
        </tbody>
    </table>
    
    <h2>🟣 수익환원법 (Income Approach) 상세</h2>
    
    <div class="method-box">
        <h3>계산 원리</h3>
        <p>수익환원법은 <strong>순영업소득(NOI)을 환원율로 나누어</strong> 평가액을 산정합니다.</p>
        <p><strong>평가액 = 순영업소득(NOI) ÷ 환원율</strong></p>
        <p><strong>NOI = 총임대수익 - 공실손실 - 운영경비</strong></p>
    </div>
    
    <div class="calculation-step">
        {'<br>'.join(appraisal_data['breakdown']['income'].get('calculation_steps', []))}
    </div>
    
    <table>
        <thead>
            <tr>
                <th>항목</th>
                <th>금액 (억원)</th>
                <th>비율</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>연간 총임대수익</td>
                <td style="text-align: right;">{appraisal_data['breakdown']['income'].get('annual_rental_income', 0):.2f}</td>
                <td>100%</td>
            </tr>
            <tr>
                <td>공실손실</td>
                <td style="text-align: right;">-{appraisal_data['breakdown']['income'].get('annual_rental_income', 0) * 0.05:.2f}</td>
                <td>-5%</td>
            </tr>
            <tr>
                <td>운영경비</td>
                <td style="text-align: right;">-{appraisal_data['breakdown']['income'].get('annual_rental_income', 0) * 0.95 * 0.15:.2f}</td>
                <td>-15%</td>
            </tr>
            <tr style="background-color: #fffacd;">
                <td><strong>순영업소득(NOI)</strong></td>
                <td style="text-align: right;"><strong>{appraisal_data['breakdown']['income'].get('noi', 0):.2f}</strong></td>
                <td><strong>80%</strong></td>
            </tr>
            <tr>
                <td>환원율 (Cap Rate)</td>
                <td colspan="2" style="text-align: center;"><strong>{appraisal_data['breakdown']['income'].get('cap_rate_percentage', '4.5%')}</strong> (주거용 부동산 기준)</td>
            </tr>
            <tr style="background-color: #f0f8ff;">
                <td><strong>수익환원법 평가액</strong></td>
                <td style="text-align: right;"><strong>{appraisal_data['breakdown']['income']['total_value']:.2f}</strong></td>
                <td><strong>NOI ÷ 환원율</strong></td>
            </tr>
        </tbody>
    </table>
    
    <h2>📝 특기사항</h2>
    
    <div class="method-box">
        <ul>
"""
        
        for note in appraisal_data['notes']:
            html += f"            <li>{note}</li>\n"
        
        html += f"""
        </ul>
    </div>
    
    <div class="footer">
        <div class="footer-logo">ANTENNA HOLDINGS</div>
        <p><strong>안테나홀딩스 (Antenna Holdings Co., Ltd.)</strong></p>
        <p>서울특별시 강남구 테헤란로 427 위워크타워</p>
        <p>Tel: 02-6952-7000 | Email: appraisal@antennaholdings.com</p>
        <p style="margin-top: 15px;"><strong>본 감정평가 보고서는 ZeroSite v24.1 AI 시스템에 의해 자동 생성되었습니다.</strong></p>
        <p>본 평가는 참고용이며, 공식 감정평가는 감정평가법인에 의뢰하시기 바랍니다.</p>
        <p>생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</p>
        <p style="margin-top: 10px; color: #999; font-size: 7pt;">
            본 보고서는 「감정평가 및 감정평가사에 관한 법률」에 따른 공식 감정평가서가 아닙니다.<br>
            안테나홀딩스 내부 의사결정 참고자료로만 활용 가능합니다.
        </p>
    </div>
    
</body>
</html>
"""
        
        return html
    
    def generate_pdf_bytes(self, appraisal_data: Dict) -> bytes:
        """
        Generate PDF as bytes
        
        Args:
            appraisal_data: Complete appraisal result
        
        Returns:
            PDF file as bytes
        """
        try:
            from weasyprint import HTML
            
            html_content = self.generate_pdf_html(appraisal_data)
            pdf_bytes = HTML(string=html_content).write_pdf()
            
            return pdf_bytes
            
        except ImportError:
            # Fallback if WeasyPrint not available
            logger.warning("WeasyPrint not available, returning HTML as bytes")
            html_content = self.generate_pdf_html(appraisal_data)
            return html_content.encode('utf-8')
