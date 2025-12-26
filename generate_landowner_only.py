#!/usr/bin/env python3
"""Generate landowner_summary report with Phase 2.5 polish"""

import sys
import os
from datetime import datetime

# Mock data based on actual PDFs
MOCK_DATA = {
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "context_id": "prod-sample-lh-001",
    "address": "서울특별시 강남구 테헤란로",
    "land_area_sqm": 1500.0,
    "land_area_pyeong": 453.75,
    "zoning": "제2종일반주거지역",
    "total_units": 26,
    "land_value_total": 1621848717,
    "land_value_per_pyeong": 3574552,
    "npv_krw": 793000000,
    "irr_pct": None,
    "roi_pct": None,
    "approval_prob": 75.0,
    "lh_grade": "B",
    "buildable_units": 26,
    "housing_types": ["청년형", "신혼부부형"],
    "transit_access": "지하철역 500m 이내",
    "what_you_can_do": "LH 매입임대주택 사업으로 안정적인 수익 확보 가능",
    "summary_sentence": "본 토지는 LH 신축매입임대 사업으로 26세대 규모의 청년형 임대주택 건설이 가능하며, 예상 NPV 약 7.9억원의 안정적인 수익이 기대됩니다."
}

def safe_value(value, default="정보 없음"):
    """안전한 값 반환"""
    if value is None:
        return default
    return value

def format_currency(value):
    """통화 포맷"""
    if value is None or value == 0:
        return "산출 중"
    if value >= 100000000:  # 1억 이상
        return f"{value/100000000:,.1f}억원"
    elif value >= 10000:  # 1만 이상
        return f"{value/10000:,.0f}만원"
    return f"{value:,.0f}원"

def format_percentage(value):
    """퍼센트 포맷"""
    if value is None:
        return "산출 중"
    return f"{value:.1f}%"

def render_landowner_summary(data):
    """토지주 요약 보고서 렌더링 (Phase 2.5 적용)"""
    
    generated_at = safe_value(data.get("generated_at"), "2025-12-26")
    context_id = safe_value(data.get("context_id"), "UNKNOWN")
    address = safe_value(data.get("address"), "서울/경기 지역")
    land_area_sqm = data.get("land_area_sqm", 0)
    land_area_pyeong = data.get("land_area_pyeong", 0)
    zoning = safe_value(data.get("zoning"), "주거지역")
    total_units = data.get("total_units", 0)
    land_value_total = data.get("land_value_total", 0)
    npv_krw = data.get("npv_krw", 0)
    approval_prob = data.get("approval_prob", 0)
    lh_grade = safe_value(data.get("lh_grade"), "C")
    summary_sentence = safe_value(data.get("summary_sentence"), "본 토지는 LH 신축매입임대 사업 추진이 가능합니다.")
    what_you_can_do = safe_value(data.get("what_you_can_do"), "LH 매입임대주택 사업으로 안정적인 수익 확보 가능")
    
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>토지주 제출용 요약보고서 - ZeroSite v4.1</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Noto Sans KR', -apple-system, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ font-size: 28px; color: #2c3e50; margin-bottom: 10px; border-bottom: 3px solid #27ae60; padding-bottom: 10px; }}
        h2 {{ font-size: 22px; color: #27ae60; margin: 30px 0 15px 0; padding-left: 10px; border-left: 4px solid #27ae60; }}
        h3 {{ font-size: 18px; color: #2c3e50; margin: 20px 0 10px 0; }}
        .header-info {{ margin: 20px 0; padding: 15px; background: #ecf0f1; border-radius: 5px; }}
        .header-info p {{ margin: 5px 0; color: #7f8c8d; font-size: 14px; }}
        
        /* Phase 2.5: KPI 요약 카드 (Green gradient for landowner) */
        .kpi-summary-card {{
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            margin: 25px 0;
            box-shadow: 0 4px 15px rgba(46, 204, 113, 0.3);
        }}
        .kpi-summary-card h3 {{
            color: white;
            border: none;
            margin: 0 0 15px 0;
            padding: 0;
            font-size: 20px;
        }}
        .kpi-summary-card p {{
            font-size: 16px;
            line-height: 1.8;
            margin: 10px 0;
        }}
        .kpi-summary-card strong {{
            font-size: 18px;
            font-weight: 700;
            text-decoration: underline;
        }}
        
        /* Phase 2.5: 토지주 관점 해석 */
        .landowner-interpretation {{
            background: #e8f5e9;
            border-left: 4px solid #27ae60;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .landowner-interpretation h4 {{
            color: #27ae60;
            margin-bottom: 10px;
            font-size: 16px;
        }}
        .landowner-interpretation p {{
            color: #2c3e50;
            line-height: 1.7;
        }}
        
        .decision-card {{
            background: #fff3cd;
            border: 2px solid #ffc107;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .decision-card h3 {{
            color: #856404;
            margin-bottom: 10px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 20px 0;
        }}
        .info-item {{
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
            border-left: 3px solid #27ae60;
        }}
        .info-item .label {{
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        .info-item .value {{
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
        }}
        .data-value {{ font-weight: 600; color: #27ae60; }}
        .data-value.na {{ color: #95a5a6; font-style: italic; }}
        ul {{ margin-left: 20px; margin-top: 10px; }}
        li {{ margin: 8px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏡 토지주 제출용 요약보고서</h1>
        <div class="header-info">
            <p><strong>생성일:</strong> {generated_at}</p>
            <p><strong>문서 ID:</strong> {context_id}</p>
        </div>
        
        <div class="decision-card">
            <h3>📋 한 줄 요약</h3>
            <p>{summary_sentence}</p>
        </div>
        
        <!-- Phase 2.5: KPI 요약 카드 (토지주 관점) -->
        <div class="kpi-summary-card">
            <h3>💰 핵심 지표 (토지주 관점)</h3>
            <p>
                귀하의 토지(<strong>{land_area_pyeong:.1f}평</strong>)는 
                LH 신축매입임대 사업으로 <strong>{total_units}세대</strong> 규모의 임대주택 건설이 가능하며,
                예상 순수익(NPV)은 약 <strong>{format_currency(npv_krw)}</strong>입니다.
            </p>
            <p>
                LH 승인 가능성은 <strong>{format_percentage(approval_prob)}</strong>이며,
                등급은 <strong>{lh_grade}등급</strong>으로 평가됩니다.
            </p>
        </div>
        
        <h2>1. 이 땅으로 무엇을 할 수 있나요?</h2>
        <p style="margin: 15px 0; font-size: 16px; line-height: 1.8;">
            {what_you_can_do}
        </p>
        
        <!-- Phase 2.5: 토지주 관점 해석 -->
        <div class="landowner-interpretation">
            <h4>💡 토지주 관점에서의 의미</h4>
            <p>
                이 사업은 토지주가 직접 건설 리스크를 부담하지 않고, 
                <strong>LH가 완공 후 건물 전체를 매입</strong>하는 구조입니다.
                따라서 일반 분양 사업보다 <strong>안정적이며 현금 흐름이 명확</strong>합니다.
            </p>
            <p style="margin-top: 10px;">
                특히 귀하의 토지는 <strong>{zoning}</strong> 지역으로, 
                LH 신축매입임대 기준을 충족하며 <strong>승인 가능성 {format_percentage(approval_prob)}</strong>로
                사업 추진이 유리합니다.
            </p>
        </div>
        
        <h2>2. 대상지 기본 정보</h2>
        <div class="info-grid">
            <div class="info-item">
                <div class="label">위치</div>
                <div class="value">{address}</div>
            </div>
            <div class="info-item">
                <div class="label">대지 면적</div>
                <div class="value">{land_area_sqm:,.0f}㎡ ({land_area_pyeong:,.1f}평)</div>
            </div>
            <div class="info-item">
                <div class="label">용도지역</div>
                <div class="value">{zoning}</div>
            </div>
            <div class="info-item">
                <div class="label">건설 가능 세대</div>
                <div class="value">{total_units}세대</div>
            </div>
        </div>
        
        <h2>3. 예상 수익</h2>
        <div class="info-grid">
            <div class="info-item">
                <div class="label">토지 감정가</div>
                <div class="value">{format_currency(land_value_total)}</div>
            </div>
            <div class="info-item">
                <div class="label">예상 순수익 (NPV)</div>
                <div class="value">{format_currency(npv_krw)}</div>
            </div>
            <div class="info-item">
                <div class="label">LH 승인 가능성</div>
                <div class="value">{format_percentage(approval_prob)}</div>
            </div>
            <div class="info-item">
                <div class="label">LH 평가 등급</div>
                <div class="value">{lh_grade}등급</div>
            </div>
        </div>
        
        <h2>4. 쉽게 설명하면</h2>
        <ul>
            <li><strong>건물 규모:</strong> 보통 5~10층 규모의 임대주택</li>
            <li><strong>세대당 면적:</strong> 20~40평대 (전용면적 기준)</li>
            <li><strong>주택 종류:</strong> 청년형, 신혼부부형, 일반 가구용 소형 임대주택</li>
            <li><strong>건설 후 매입:</strong> LH가 완공 즉시 건물 전체를 매입</li>
            <li><strong>사업 기간:</strong> 설계 + 인허가 + 건축 약 2~3년</li>
        </ul>
        
        <div class="landowner-interpretation" style="margin-top: 30px;">
            <h4>✅ 토지주에게 유리한 점</h4>
            <ul style="margin-left: 20px; margin-top: 10px;">
                <li>분양 리스크 없음 (LH가 전량 매입 보장)</li>
                <li>안정적인 현금 흐름 (완공 시점에 일괄 매각)</li>
                <li>공공사업으로 인허가 유리</li>
                <li>장기 보유 세금 부담 해소</li>
            </ul>
        </div>
        
        <h2>5. 다음 단계</h2>
        <ol style="margin-left: 20px; margin-top: 10px;">
            <li>정밀 토지 조사 (경계, 권리 관계 확인)</li>
            <li>LH 사전 협의 (매입 의향 확인)</li>
            <li>시공사 선정 및 견적</li>
            <li>사업 추진 최종 결정</li>
        </ol>
        
        <div class="decision-card" style="margin-top: 30px; background: #d4edda; border-color: #27ae60;">
            <h3 style="color: #155724;">📞 문의 및 상담</h3>
            <p style="color: #155724;">
                본 보고서는 초기 검토 단계의 분석 결과이며, 
                정확한 사업성 검토를 위해서는 전문가와의 상담이 필요합니다.
            </p>
        </div>
    </div>
</body>
</html>"""
    
    return html

# Generate report
if __name__ == "__main__":
    try:
        html = render_landowner_summary(MOCK_DATA)
        
        output_dir = "/home/user/webapp/final_reports_phase25"
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, "landowner_summary_phase25_real_data.html")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ landowner_summary generated: {output_path}")
        print(f"   Size: {len(html):,} characters")
        print(f"   KPI card: ✓")
        print(f"   Interpretation: ✓")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
