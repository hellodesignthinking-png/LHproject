"""
ZeroSite v30.0 - HTML Generator
Generate HTML preview of appraisal report
"""
from typing import Dict


class HTMLGeneratorV30:
    """Generate HTML preview"""
    
    def generate(self, appraisal_data: Dict) -> str:
        """Generate HTML from appraisal data"""
        
        land_info = appraisal_data['land_info']
        appraisal = appraisal_data['appraisal']
        comps = appraisal_data['comparable_sales']
        
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>토지 감정평가 보고서 - {land_info['address']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f7fa;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #005BAC 0%, #003d7a 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        .header .version {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .section {{
            padding: 30px 40px;
            border-bottom: 1px solid #e1e4e8;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section-title {{
            font-size: 24px;
            color: #005BAC;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #005BAC;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }}
        .info-item {{
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .info-label {{
            font-size: 13px;
            color: #666;
            margin-bottom: 5px;
        }}
        .info-value {{
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }}
        .highlight-box {{
            background: #e8f4fd;
            border-left: 4px solid #005BAC;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .final-value {{
            font-size: 36px;
            font-weight: 700;
            color: #005BAC;
            text-align: center;
            margin: 20px 0;
        }}
        .approaches-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 20px 0;
        }}
        .approach-card {{
            background: white;
            border: 2px solid #e1e4e8;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        .approach-card.active {{
            border-color: #005BAC;
            background: #f8fbff;
        }}
        .approach-title {{
            font-size: 16px;
            font-weight: 600;
            color: #005BAC;
            margin-bottom: 10px;
        }}
        .approach-value {{
            font-size: 24px;
            font-weight: 700;
            color: #333;
            margin: 10px 0;
        }}
        .approach-weight {{
            font-size: 14px;
            color: #666;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e1e4e8;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-high {{
            background: #d4edda;
            color: #155724;
        }}
        .badge-medium {{
            background: #fff3cd;
            color: #856404;
        }}
        .badge-low {{
            background: #f8d7da;
            color: #721c24;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏘️ 토지 감정평가 보고서</h1>
            <p class="version">{appraisal_data['version']} | {appraisal_data['timestamp']}</p>
        </div>
        
        <div class="section">
            <h2 class="section-title">📍 대상 토지 정보</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">소재지</div>
                    <div class="info-value">{land_info['address']}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">토지 면적</div>
                    <div class="info-value">{land_info['land_area_sqm']:,.1f} ㎡</div>
                </div>
                <div class="info-item">
                    <div class="info-label">용도지역</div>
                    <div class="info-value">{land_info['zone_type']}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">개별공시지가 ({land_info['official_price_year']}년)</div>
                    <div class="info-value">₩{land_info['official_land_price_per_sqm']:,}/㎡</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">💰 최종 감정평가액</h2>
            <div class="highlight-box">
                <div class="final-value">₩{appraisal['final_value']:,}</div>
                <p style="text-align: center; color: #666; font-size: 18px;">
                    (₩{appraisal['value_per_sqm']:,}/㎡)
                </p>
                <p style="text-align: center; margin-top: 10px;">
                    <span class="badge {'badge-high' if appraisal['confidence_level'] == '높음' else 'badge-medium' if appraisal['confidence_level'] == '중간' else 'badge-low'}">
                        신뢰도: {appraisal['confidence_level']}
                    </span>
                </p>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">📊 3가지 평가 방법</h2>
            <div class="approaches-grid">
                <div class="approach-card">
                    <div class="approach-title">원가법</div>
                    <div class="approach-value">₩{appraisal['approaches']['cost']['value']:,}</div>
                    <div class="approach-weight">가중치: {appraisal['weights']['cost']*100:.0f}%</div>
                </div>
                <div class="approach-card active">
                    <div class="approach-title">거래사례비교법</div>
                    <div class="approach-value">₩{appraisal['approaches']['sales_comparison']['value']:,}</div>
                    <div class="approach-weight">가중치: {appraisal['weights']['sales']*100:.0f}%</div>
                </div>
                <div class="approach-card">
                    <div class="approach-title">수익환원법</div>
                    <div class="approach-value">₩{appraisal['approaches']['income']['value']:,}</div>
                    <div class="approach-weight">가중치: {appraisal['weights']['income']*100:.0f}%</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">⭐ 프리미엄 분석</h2>
            <div class="highlight-box">
                <p style="font-size: 20px; font-weight: 600; color: #005BAC;">
                    총 프리미엄: +{appraisal['premium']['percentage']}%
                </p>
                <table>
                    <thead>
                        <tr>
                            <th>요인</th>
                            <th style="text-align: right;">영향도</th>
                        </tr>
                    </thead>
                    <tbody>
                        {self._generate_premium_rows(appraisal['premium']['factors'])}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">🔍 유사 거래사례 ({comps['total_count']}건)</h2>
            <table>
                <thead>
                    <tr>
                        <th>주소</th>
                        <th>면적</th>
                        <th style="text-align: right;">거래가격/㎡</th>
                        <th>거리</th>
                        <th>거래일</th>
                    </tr>
                </thead>
                <tbody>
                    {self._generate_transaction_rows(comps['transactions'])}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    def _generate_premium_rows(self, factors: list) -> str:
        """Generate premium factor rows"""
        rows = []
        for factor in factors:
            rows.append(f"""
                        <tr>
                            <td>{factor['factor']}</td>
                            <td style="text-align: right; color: #005BAC; font-weight: 600;">+{factor['impact']}%</td>
                        </tr>
            """)
        return '\n'.join(rows)
    
    def _generate_transaction_rows(self, transactions: list) -> str:
        """Generate transaction rows"""
        rows = []
        for trans in transactions:
            rows.append(f"""
                        <tr>
                            <td>{trans['address']}</td>
                            <td>{trans['size_sqm']:,.1f} ㎡</td>
                            <td style="text-align: right;">₩{trans['price_per_sqm']:,.0f}</td>
                            <td>{trans['distance_km']} km</td>
                            <td>{trans['transaction_date']}</td>
                        </tr>
            """)
        return '\n'.join(rows)
