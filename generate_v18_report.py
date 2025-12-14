"""
ZeroSite v18 Report Generator
==============================
Policy Transaction Financial Engine을 사용한 완전한 보고서 생성
"""

import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.policy_transaction_financial_engine_v18 import (
    PolicyTransactionFinancialEngineV18,
    TransactionInputs
)

def generate_v18_report(address: str, land_area_m2: float, output_filename: str = "v18_REPORT.html"):
    """
    v18 엔진을 사용하여 완전한 LH 제출용 보고서 생성
    
    Args:
        address: 주소
        land_area_m2: 대지면적 (㎡)
        output_filename: 출력 파일명
    """
    print("=" * 80)
    print("🚀 ZeroSite v18 - Policy Transaction Report Generator")
    print("=" * 80)
    print()
    
    # 1. 입력 데이터 설정
    building_area_m2 = land_area_m2 * 2.5  # 용적률 250% 가정
    
    inputs = TransactionInputs(
        land_area_m2=land_area_m2,
        building_area_m2=building_area_m2,
        land_price_per_m2=10_000_000,  # 서울 평균 1천만원/㎡
        construction_cost_per_m2=3_500_000,  # 350만원/㎡
        
        # LH 감정평가 파라미터
        land_appraisal_rate=0.95,
        building_ack_rate=0.90,
        appraisal_safety_factor=0.98,
        
        # 공사비 연동제
        construction_index_rate=1.05,
    )
    
    print(f"📍 주소: {address}")
    print(f"📐 대지면적: {land_area_m2:.1f}㎡ ({land_area_m2/3.3058:.1f}평)")
    print(f"🏢 연면적: {building_area_m2:.1f}㎡")
    print()
    
    # 2. v18 엔진 실행
    print("💡 v18 Policy Transaction Engine 실행 중...")
    engine = PolicyTransactionFinancialEngineV18(inputs)
    result = engine.evaluate()
    sensitivity = engine.sensitivity_analysis()
    
    # 3. Context 생성 (템플릿 친화적 구조)
    context = {
        # 메타데이터
        'metadata': {
            'report_title': 'LH 신축매입임대 사업 타당성 분석 보고서',
            'address': address,
            'generated_date': datetime.now().strftime('%Y년 %m월 %d일'),
            'version': 'ZeroSite v18.0',
            'submitter': 'ZeroSite / Antenna Holdings',
            'author': '나태흠 (Na Tae-heum)',
            'author_email': 'taina@ant3na.com',
            'copyright': '© 2025 Antenna Holdings. All rights reserved.',
        },
        
        # 사이트 정보
        'site': {
            'address': address,
            'land_area_sqm': land_area_m2,
            'land_area_pyeong': land_area_m2 / 3.3058,
            'building_area_sqm': building_area_m2,
            'building_area_pyeong': building_area_m2 / 3.3058,
        },
        
        # 재무 분석 (v18)
        'financial': {
            # 총사업비 수지표
            'capex_table': [
                {'name': '토지비', 'value': result.capex.land_cost, 'value_krw': f"{result.capex.land_cost/1e8:.2f}"},
                {'name': '취득세', 'value': result.capex.land_acquisition_tax, 'value_krw': f"{result.capex.land_acquisition_tax/1e8:.2f}"},
                {'name': '건설비(연동제)', 'value': result.capex.indexed_construction_cost, 'value_krw': f"{result.capex.indexed_construction_cost/1e8:.2f}"},
                {'name': '설계비', 'value': result.capex.design_cost, 'value_krw': f"{result.capex.design_cost/1e8:.2f}"},
                {'name': '감리비', 'value': result.capex.supervision_cost, 'value_krw': f"{result.capex.supervision_cost/1e8:.2f}"},
                {'name': '인허가비', 'value': result.capex.permit_cost, 'value_krw': f"{result.capex.permit_cost/1e8:.2f}"},
                {'name': '예비비', 'value': result.capex.contingency_cost, 'value_krw': f"{result.capex.contingency_cost/1e8:.2f}"},
                {'name': '금융비용', 'value': result.capex.financing_cost, 'value_krw': f"{result.capex.financing_cost/1e8:.2f}"},
                {'name': '기타비용', 'value': result.capex.misc_cost, 'value_krw': f"{result.capex.misc_cost/1e8:.2f}"},
            ],
            'capex_total': result.capex.total_capex,
            'capex_total_krw': f"{result.capex.total_capex/1e8:.2f}",
            
            # LH 감정평가
            'land_appraisal_value': result.appraisal.land_appraised_value,
            'land_appraisal_value_krw': f"{result.appraisal.land_appraised_value/1e8:.2f}",
            'building_appraisal_value': result.appraisal.building_appraised_value,
            'building_appraisal_value_krw': f"{result.appraisal.building_appraised_value/1e8:.2f}",
            'indexing_adjustment': result.appraisal.indexing_adjustment,
            'indexing_adjustment_krw': f"{result.appraisal.indexing_adjustment/1e8:.2f}",
            'lh_purchase_price': result.appraisal.final_appraisal_value,
            'lh_purchase_price_krw': f"{result.appraisal.final_appraisal_value/1e8:.2f}",
            
            # 사업 수익성
            'profit': result.profit,
            'profit_krw': f"{result.profit/1e8:+.2f}",
            'roi_pct': f"{result.roi_pct:+.2f}",
            'irr_pct': f"{result.irr_pct:+.2f}",
            'payback_years': result.payback_years,
            
            # 의사결정
            'decision': result.decision,
            'decision_reason': result.decision_reason,
            'conditional_requirements': result.conditional_requirements,
            
            # 민감도 분석 (List 형태로 변환)
            'sensitivity_table': [
                {'variable': '토지비 -10%', 'roi': f"{sensitivity['scenarios']['land_-10%']['roi']:+.2f}", 'decision': sensitivity['scenarios']['land_-10%']['decision']},
                {'variable': '토지비 +0%', 'roi': f"{sensitivity['scenarios']['land_+0%']['roi']:+.2f}", 'decision': sensitivity['scenarios']['land_+0%']['decision']},
                {'variable': '토지비 +10%', 'roi': f"{sensitivity['scenarios']['land_+10%']['roi']:+.2f}", 'decision': sensitivity['scenarios']['land_+10%']['decision']},
                {'variable': '공사비 -15%', 'roi': f"{sensitivity['scenarios']['construction_-15%']['roi']:+.2f}", 'decision': sensitivity['scenarios']['construction_-15%']['decision']},
                {'variable': '공사비 +0%', 'roi': f"{sensitivity['scenarios']['construction_+0%']['roi']:+.2f}", 'decision': sensitivity['scenarios']['construction_+0%']['decision']},
                {'variable': '공사비 +15%', 'roi': f"{sensitivity['scenarios']['construction_+15%']['roi']:+.2f}", 'decision': sensitivity['scenarios']['construction_+15%']['decision']},
                {'variable': '감정평가율 85%', 'roi': f"{sensitivity['scenarios']['appraisal_85%']['roi']:+.2f}", 'decision': sensitivity['scenarios']['appraisal_85%']['decision']},
                {'variable': '감정평가율 90%', 'roi': f"{sensitivity['scenarios']['appraisal_90%']['roi']:+.2f}", 'decision': sensitivity['scenarios']['appraisal_90%']['decision']},
                {'variable': '감정평가율 95%', 'roi': f"{sensitivity['scenarios']['appraisal_95%']['roi']:+.2f}", 'decision': sensitivity['scenarios']['appraisal_95%']['decision']},
            ],
        },
    }
    
    # 4. 간단한 HTML 템플릿 생성
    html_template = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ metadata.report_title }}</title>
    <style>
        @page { margin: 2cm; }
        body { font-family: 'Malgun Gothic', sans-serif; font-size: 12pt; line-height: 1.6; color: #333; }
        .header { text-align: center; margin-bottom: 40px; padding: 20px; background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%); color: white; }
        .header h1 { font-size: 24pt; margin: 0; }
        .header .meta { font-size: 10pt; margin-top: 10px; opacity: 0.9; }
        .section { margin: 30px 0; page-break-inside: avoid; }
        .section-title { font-size: 18pt; font-weight: bold; color: #1976d2; border-bottom: 3px solid #1976d2; padding-bottom: 10px; margin-bottom: 20px; }
        .subsection-title { font-size: 14pt; font-weight: bold; color: #333; margin: 20px 0 10px 0; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th { background: #1976d2; color: white; padding: 12px; text-align: left; font-weight: 600; }
        td { padding: 10px; border-bottom: 1px solid #ddd; }
        tr:nth-child(even) { background: #f8f9fa; }
        .total-row { font-weight: bold; background: #e3f2fd !important; font-size: 13pt; }
        .decision-box { padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 5px solid #f57c00; background: #fff3e0; }
        .decision-box .label { font-weight: bold; font-size: 14pt; color: #e65100; }
        .decision-box .value { font-size: 16pt; font-weight: 900; margin: 10px 0; }
        .positive { color: #43a047; }
        .negative { color: #d32f2f; }
        .footer { margin-top: 50px; padding: 20px; background: #f5f5f5; border-top: 2px solid #1976d2; font-size: 10pt; color: #666; }
        .footer .info { margin: 5px 0; }
        .key-metric { display: inline-block; padding: 15px 25px; margin: 10px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; }
        .key-metric .label { font-size: 10pt; color: #666; margin-bottom: 5px; }
        .key-metric .value { font-size: 20pt; font-weight: 900; }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <h1>{{ metadata.report_title }}</h1>
        <div class="meta">
            {{ metadata.address }} | {{ metadata.generated_date }} | {{ metadata.version }}
        </div>
    </div>
    
    <!-- Section 1: 사이트 개요 -->
    <div class="section">
        <div class="section-title">1. 사이트 개요</div>
        <table>
            <tr><td><strong>주소</strong></td><td>{{ site.address }}</td></tr>
            <tr><td><strong>대지면적</strong></td><td>{{ site.land_area_sqm | round(1) }}㎡ ({{ site.land_area_pyeong | round(1) }}평)</td></tr>
            <tr><td><strong>연면적</strong></td><td>{{ site.building_area_sqm | round(1) }}㎡ ({{ site.building_area_pyeong | round(1) }}평)</td></tr>
        </table>
    </div>
    
    <!-- Section 6: 총사업비 및 사업수지 분석 -->
    <div class="section">
        <div class="section-title">6. 총사업비 및 사업수지 분석</div>
        
        <div class="subsection-title">6.1 총사업비 산출표</div>
        <table>
            <thead>
                <tr>
                    <th>항목</th>
                    <th style="text-align: right;">금액 (억원)</th>
                </tr>
            </thead>
            <tbody>
                {% for row in financial.capex_table %}
                <tr>
                    <td>{{ row.name }}</td>
                    <td style="text-align: right;">{{ row.value_krw }}</td>
                </tr>
                {% endfor %}
                <tr class="total-row">
                    <td>합계</td>
                    <td style="text-align: right;">{{ financial.capex_total_krw }}</td>
                </tr>
            </tbody>
        </table>
        
        <div class="subsection-title">6.2 LH 예상 매입가</div>
        <table>
            <tr><td><strong>토지 감정가액</strong></td><td style="text-align: right;">{{ financial.land_appraisal_value_krw }}억원</td></tr>
            <tr><td><strong>건물 감정가액</strong></td><td style="text-align: right;">{{ financial.building_appraisal_value_krw }}억원</td></tr>
            <tr><td><strong>연동제 조정</strong></td><td style="text-align: right;">{{ financial.indexing_adjustment_krw }}억원</td></tr>
            <tr class="total-row"><td><strong>LH 최종 매입가</strong></td><td style="text-align: right;">{{ financial.lh_purchase_price_krw }}억원</td></tr>
        </table>
        
        <div class="subsection-title">6.3 사업 수익성 분석</div>
        <div style="text-align: center; margin: 30px 0;">
            <div class="key-metric">
                <div class="label">사업이익 (Profit)</div>
                <div class="value {{ 'positive' if financial.profit >= 0 else 'negative' }}">{{ financial.profit_krw }}억원</div>
            </div>
            <div class="key-metric">
                <div class="label">ROI</div>
                <div class="value {{ 'positive' if financial.roi_pct|float >= 0 else 'negative' }}">{{ financial.roi_pct }}%</div>
            </div>
            <div class="key-metric">
                <div class="label">IRR (2.5년)</div>
                <div class="value {{ 'positive' if financial.irr_pct|float >= 0 else 'negative' }}">{{ financial.irr_pct }}%</div>
            </div>
        </div>
        
        <div class="subsection-title">6.4 민감도 분석</div>
        <table>
            <thead>
                <tr>
                    <th>시나리오</th>
                    <th style="text-align: right;">ROI</th>
                    <th>판단</th>
                </tr>
            </thead>
            <tbody>
                {% for row in financial.sensitivity_table %}
                <tr>
                    <td>{{ row.variable }}</td>
                    <td style="text-align: right;" class="{{ 'positive' if row.roi|float >= 0 else 'negative' }}">{{ row.roi }}%</td>
                    <td>{{ row.decision }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="subsection-title">6.5 최종 판단</div>
        <div class="decision-box">
            <div class="label">판단</div>
            <div class="value">{{ financial.decision }}</div>
            <div style="margin-top: 15px; font-size: 12pt; line-height: 1.7;">
                <strong>근거:</strong> {{ financial.decision_reason }}
            </div>
            {% if financial.conditional_requirements %}
            <div style="margin-top: 15px;">
                <strong>조건부 개선 방안:</strong>
                <ul>
                    {% for req in financial.conditional_requirements %}
                    <li>{{ req }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
        </div>
    </div>
    
    <!-- Footer -->
    <div class="footer">
        <div class="info"><strong>제출자:</strong> {{ metadata.submitter }}</div>
        <div class="info"><strong>작성자:</strong> {{ metadata.author }} ({{ metadata.author_email }})</div>
        <div class="info">{{ metadata.copyright }}</div>
    </div>
</body>
</html>
"""
    
    # 5. 템플릿 렌더링
    from jinja2 import Template
    template = Template(html_template)
    html_content = template.render(**context)
    
    # 6. 파일 저장
    output_path = Path('output') / output_filename
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(html_content, encoding='utf-8')
    
    print()
    print("=" * 80)
    print("✅ ZeroSite v18 보고서 생성 완료!")
    print("=" * 80)
    print()
    print(f"📄 파일: {output_path}")
    print(f"📊 총사업비: {result.capex.total_capex/1e8:.2f}억원")
    print(f"💰 LH 매입가: {result.appraisal.final_appraisal_value/1e8:.2f}억원")
    print(f"{'📗' if result.profit >= 0 else '📕'} 사업이익: {result.profit/1e8:+.2f}억원")
    print(f"{'✅' if result.roi_pct >= 0 else '❌'} ROI: {result.roi_pct:+.2f}%")
    print(f"📊 IRR: {result.irr_pct:+.2f}%")
    print(f"🎯 판단: {result.decision}")
    print()
    
    return str(output_path)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("사용법: python generate_v18_report.py <주소> <대지면적(㎡)> [출력파일명.html]")
        print("예시: python generate_v18_report.py '서울특별시 마포구 월드컵북로 120' 660 'v18_FINAL.html'")
        sys.exit(1)
    
    address = sys.argv[1]
    land_area = float(sys.argv[2])
    output_file = sys.argv[3] if len(sys.argv) > 3 else "v18_REPORT.html"
    
    generate_v18_report(address, land_area, output_file)
