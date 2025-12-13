"""
Land Diagnosis PDF Report Generator
Generates detailed PDF reports for comprehensive land diagnosis
"""

from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LandDiagnosisPDFGenerator:
    """Generate detailed land diagnosis PDF reports"""
    
    def generate_pdf_html(self, diagnosis_data: Dict) -> str:
        """
        Generate HTML content for PDF conversion
        
        Args:
            diagnosis_data: Complete land diagnosis result
        
        Returns:
            HTML string ready for WeasyPrint conversion
        """
        
        # Extract data
        summary = diagnosis_data.get('summary', {})
        capacity = diagnosis_data.get('details', {}).get('capacity', {})
        financial = diagnosis_data.get('details', {}).get('financial', {})
        risk = diagnosis_data.get('details', {}).get('risk', {})
        market = diagnosis_data.get('details', {}).get('market', {})
        fallback_info = diagnosis_data.get('fallback_info', {})  # ✅ Fallback 정보 추출
        
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 2cm 2cm 3cm 2cm;
        }}
        body {{
            font-family: 'Malgun Gothic', 'Noto Sans KR', sans-serif;
            font-size: 10pt;
            line-height: 1.6;
            color: #333;
        }}
        
        .header {{
            border-bottom: 4px solid #005BAC;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}
        .header-logo {{
            width: 120px;
            height: 40px;
            background: linear-gradient(135deg, #005BAC 0%, #0073D1 100%);
            color: white;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 18pt;
            border-radius: 5px;
            padding: 10px 20px;
        }}
        .header-subtitle {{
            color: #666;
            font-size: 9pt;
            margin-top: 5px;
        }}
        
        h1 {{
            color: #005BAC;
            font-size: 22pt;
            font-weight: bold;
            margin: 20px 0 10px 0;
            border-bottom: 3px solid #FF7A00;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #005BAC;
            border-left: 5px solid #FF7A00;
            padding-left: 15px;
            margin-top: 30px;
            font-size: 16pt;
            font-weight: bold;
        }}
        
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
            background: linear-gradient(135deg, #005BAC 0%, #0073D1 100%);
            color: white;
            font-weight: bold;
        }}
        
        .summary-box {{
            background: linear-gradient(to bottom, #f0f8ff 0%, #e6f2ff 100%);
            border: 2px solid #005BAC;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .recommendation-box {{
            padding: 20px;
            margin: 25px 0;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .recommendation-suitable {{
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border: 3px solid #28a745;
        }}
        .recommendation-review {{
            background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
            border: 3px solid #ffc107;
        }}
        .recommendation-unsuitable {{
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            border: 3px solid #dc3545;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 9pt;
            font-weight: bold;
        }}
        .badge-success {{ background-color: #d4edda; color: #155724; }}
        .badge-warning {{ background-color: #fff3cd; color: #856404; }}
        .badge-danger {{ background-color: #f8d7da; color: #721c24; }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #005BAC;
            font-size: 8pt;
            color: #666;
            text-align: center;
        }}
        
        .watermark {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 80pt;
            color: rgba(0, 91, 172, 0.05);
            font-weight: bold;
            z-index: -1;
        }}
    </style>
</head>
<body>
    <div class="watermark">LH ZeroSite</div>
    
    <div class="header">
        <div class="header-logo">LH</div>
        <div class="header-subtitle">한국토지주택공사 · 신축매입임대 토지진단 시스템 v24.1</div>
    </div>
    
    <h1>🔍 토지 종합 진단 보고서</h1>
    
    <div class="summary-box">
        <h3>진단 기본 정보</h3>
        <table>
            <tr>
                <th width="30%">진단일시</th>
                <td>{diagnosis_data.get('timestamp', datetime.now().isoformat())}</td>
            </tr>
            <tr>
                <th>진단 ID</th>
                <td>{diagnosis_data.get('analysis_id', 'N/A')}</td>
            </tr>
            <tr>
                <th>대상 주소</th>
                <td>{summary.get('address', 'N/A')}</td>
            </tr>
            <tr>
                <th>토지 면적</th>
                <td>{summary.get('land_area', 0):,.2f} ㎡</td>
            </tr>
        </table>
    </div>
    
    <!-- Recommendation -->
    <div class="recommendation-box {'recommendation-suitable' if summary.get('recommendation') == '적합' else 'recommendation-review' if '검토' in summary.get('recommendation', '') else 'recommendation-unsuitable'}">
        <h2 style="margin-top: 0;">✅ 종합 판정</h2>
        <p style="font-size: 20pt; font-weight: bold; text-align: center; margin: 20px 0;">
            {summary.get('recommendation', '검토 필요')}
        </p>
    </div>
    
    <h2>📊 건축 규모 분석</h2>
    <table>
        <thead>
            <tr>
                <th>항목</th>
                <th>값</th>
                <th>비고</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>최대 세대수</td>
                <td style="text-align: right;"><strong>{capacity.get('max_units', 0):,}세대</strong></td>
                <td>건축가능 최대 규모</td>
            </tr>
            <tr>
                <td>층수</td>
                <td style="text-align: right;"><strong>{capacity.get('floors', 0):,}층</strong></td>
                <td>높이 제한 고려</td>
            </tr>
            <tr>
                <td>총 연면적</td>
                <td style="text-align: right;">{capacity.get('total_floor_area', 0):,.2f} ㎡</td>
                <td>용적률 적용</td>
            </tr>
            <tr>
                <td>주차대수</td>
                <td style="text-align: right;">{capacity.get('parking_spaces', 0):,}대</td>
                <td>법정 주차기준</td>
            </tr>
        </tbody>
    </table>
    
    <h2>💰 재무 타당성 분석</h2>
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
                <td>총 사업비</td>
                <td style="text-align: right;">{financial.get('total_cost', 0):,.2f}</td>
                <td>100%</td>
            </tr>
            <tr>
                <td>토지비</td>
                <td style="text-align: right;">{financial.get('land_cost', 0):,.2f}</td>
                <td>{(financial.get('land_cost', 0) / max(financial.get('total_cost', 1), 1) * 100):.1f}%</td>
            </tr>
            <tr>
                <td>건축비</td>
                <td style="text-align: right;">{financial.get('construction_cost', 0):,.2f}</td>
                <td>{(financial.get('construction_cost', 0) / max(financial.get('total_cost', 1), 1) * 100):.1f}%</td>
            </tr>
            <tr style="background-color: #f0f8ff;">
                <td><strong>ROI (투자수익률)</strong></td>
                <td style="text-align: right;"><strong>{financial.get('roi', 0) * 100:.2f}%</strong></td>
                <td>
                    {'<span class="badge badge-success">우수</span>' if financial.get('roi', 0) > 0.15 else 
                     '<span class="badge badge-warning">보통</span>' if financial.get('roi', 0) > 0.10 else 
                     '<span class="badge badge-danger">저조</span>'}
                </td>
            </tr>
        </tbody>
    </table>
    
    <h2>⚠️ 리스크 평가</h2>
    <table>
        <thead>
            <tr>
                <th>리스크 항목</th>
                <th>수준</th>
                <th>설명</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>종합 리스크</td>
                <td>
                    <strong>{risk.get('risk_level', 'MEDIUM')}</strong>
                    {'<span class="badge badge-success">낮음</span>' if risk.get('risk_level') == 'LOW' else 
                     '<span class="badge badge-warning">보통</span>' if risk.get('risk_level') == 'MEDIUM' else 
                     '<span class="badge badge-danger">높음</span>'}
                </td>
                <td>전체 리스크 종합 평가</td>
            </tr>
        </tbody>
    </table>
    
    <div class="summary-box">
        <h3>📌 주요 리스크 요인</h3>
        <ul>
"""
        
        # Add risk factors
        if risk.get('key_risks'):
            for risk_item in risk['key_risks'][:5]:
                html += f"            <li>{risk_item}</li>\n"
        else:
            html += "            <li>리스크 정보 없음</li>\n"
        
        html += """
        </ul>
    </div>
    
    <h2>📈 시장 분석</h2>
    <table>
        <thead>
            <tr>
                <th>항목</th>
                <th>정보</th>
            </tr>
        </thead>
        <tbody>
"""
        
        # Add market data
        if market:
            for key, value in list(market.items())[:5]:
                html += f"""
            <tr>
                <td>{key}</td>
                <td>{value}</td>
            </tr>
"""
        
        html += f"""
        </tbody>
    </table>
"""
        
        # ✅ Fallback Summary Section 추가
        if fallback_info.get('fallback_used', False):
            html += f"""
    
    <div class="summary-box" style="background: #fff3cd; border-left: 5px solid #FF7A00;">
        <h2 style="color: #FF7A00;">🔄 데이터 보정 요약</h2>
        <p style="margin-bottom: 15px;">
            사용자가 입력하지 않은 항목에 대해 시스템이 자동으로 기본값을 적용했습니다.
        </p>
        
        <table style="font-size: 9pt;">
            <thead>
                <tr style="background: #FFE5B4;">
                    <th>항목</th>
                    <th>원본값</th>
                    <th>적용값</th>
                </tr>
            </thead>
            <tbody>
"""
            
            for detail in fallback_info.get('fallback_details', []):
                html += f"""
                <tr>
                    <td><strong>{detail.get('field', 'N/A')}</strong></td>
                    <td style="color: #999;">{detail.get('original', 'N/A')}</td>
                    <td style="color: #FF7A00; font-weight: bold;">{detail.get('fallback', 'N/A')}</td>
                </tr>
"""
            
            html += f"""
            </tbody>
        </table>
        
        <p style="margin-top: 15px; color: #666; font-size: 8.5pt;">
            <strong>보정 적용 건수:</strong> {fallback_info.get('fallback_count', 0)}건<br>
            <strong>ZeroSite Fallback Engine:</strong> 활성화됨<br>
            <strong>생성 시각:</strong> {fallback_info.get('timestamp', 'N/A')}
        </p>
        
        <p style="margin-top: 10px; padding: 10px; background: #fffbea; border-radius: 5px; font-size: 8.5pt;">
            ⚠️ <strong>참고:</strong> 자동 보정된 값은 지역 평균 또는 법정 기준에 따라 산정되었습니다. 
            정확한 분석을 위해서는 실제 데이터 입력을 권장합니다.
        </p>
    </div>
"""
        
        html += f"""
    
    <div class="footer">
        <div style="color: #005BAC; font-weight: bold; font-size: 11pt; margin-bottom: 10px;">
            한국토지주택공사 (LH)
        </div>
        <p><strong>본 토지 진단 보고서는 ZeroSite v24.1 AI 시스템에 의해 자동 생성되었습니다.</strong></p>
        <p>생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</p>
        <p>ZeroSite v24.1 - LH 신축매입임대 토지진단 시스템 + Auto-Recovery Fallback Engine</p>
        <p style="margin-top: 10px; color: #999; font-size: 7pt;">
            본 보고서는 LH 내부 의사결정 참고자료로만 활용 가능합니다.
        </p>
    </div>
    
</body>
</html>
"""
        
        return html
    
    def generate_pdf_bytes(self, diagnosis_data: Dict) -> bytes:
        """
        Generate PDF as bytes
        
        Args:
            diagnosis_data: Complete land diagnosis result
        
        Returns:
            PDF file as bytes
        """
        try:
            from weasyprint import HTML
            
            html_content = self.generate_pdf_html(diagnosis_data)
            pdf_bytes = HTML(string=html_content).write_pdf()
            
            return pdf_bytes
            
        except ImportError:
            logger.warning("WeasyPrint not available, returning HTML as bytes")
            html_content = self.generate_pdf_html(diagnosis_data)
            return html_content.encode('utf-8')
