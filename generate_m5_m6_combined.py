#!/usr/bin/env python3
"""M5/M6 Combined Generator - REAL APPRAISAL STANDARD"""
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

def generate_m5():
    env = Environment(loader=FileSystemLoader("app/templates_v13"))
    env.filters['number_format'] = lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else str(x)
    template = env.get_template('m5_feasibility_format.html')
    
    context = {
        'report_id': f"ZS-M5-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'project_address': '서울특별시 강남구 역삼동 1234',
        'project_scale': '총 150세대, 주차 120대',
        'analysis_date': datetime.now().strftime("%Y년 %m월 %d일"),
        'feasibility_result': 'PASS (실행 가능)',
        'executive_conclusion': '본 사업은 LH 일괄매입 구조 기준에서 재무적 실행 가능성이 확보됩니다.',
        'total_cost': 85000,
        'lh_purchase_price': 92000,
        'profit_rate': 8.2,
        'cost_breakdown': [
            {'item': '토지비', 'amount': 42000, 'ratio': 49.4},
            {'item': '건축비', 'amount': 32000, 'ratio': 37.6},
            {'item': '기타비용', 'amount': 11000, 'ratio': 12.9}
        ],
        'lh_structure_score': 90,
        'financial_score': 85,
        'risk_score': 75,
        'total_score': 85.5,
        'final_opinion': '본 사업은 LH 일괄매입 구조에서 재무적 실행 가능성이 확보되었습니다. 종합 점수 85.5점으로 사업 추진을 권고합니다.'
    }
    
    html = template.render(**context)
    output = Path("generated_reports/M5_Feasibility_FINAL.html")
    output.write_text(html, encoding='utf-8')
    print(f"✅ M5: {output}")
    return str(output)

def generate_m6():
    # M6는 간단한 요약 버전으로 생성
    html_m6 = '''<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><title>M6: LH 종합 판단</title>
<style>
body{font-family:'Malgun Gothic';padding:40px;color:#333}
.header{text-align:center;margin-bottom:40px}
.title{font-size:36pt;color:#2c3e50;margin-bottom:10px}
.result{background:#d4edda;border:3px solid #0066cc;padding:30px;text-align:center;margin:30px 0}
.result-text{font-size:32pt;color:#0066cc;font-weight:bold}
table{width:100%;border-collapse:collapse;margin:20px 0}
th{background:#2c3e50;color:white;padding:12px}
td{padding:10px;border:1px solid #ddd}
.pass{background:#d4edda;font-weight:bold}
</style>
</head>
<body>
<div class="header">
<div style="font-size:20pt;letter-spacing:8px;color:#2c3e50;margin-bottom:20px">ANTENNA HOLDINGS</div>
<div class="title">LH 종합 판단 보고서</div>
</div>
<div class="result">
<div style="font-size:18pt;margin-bottom:15px">최종 판단</div>
<div class="result-text">PASS (매입 가능)</div>
</div>
<table>
<tr><th>모듈</th><th>점수</th><th>결과</th></tr>
<tr><td>M3: 공급 유형</td><td>80.3점</td><td>신혼희망타운 선정</td></tr>
<tr><td>M4: 건축 규모</td><td>86.5점</td><td>150세대 적정</td></tr>
<tr><td>M5: 사업성</td><td>85.5점</td><td>실행 가능</td></tr>
<tr class="pass"><td><strong>종합 점수</strong></td><td><strong>84.1점</strong></td><td><strong>PASS</strong></td></tr>
</table>
<div style="margin-top:60px;text-align:right">
<p style="font-size:12pt">작성 주체: ZeroSite Analysis Engine</p>
<p style="font-size:11pt;color:#6c757d">Antenna Holdings Co., Ltd.</p>
</div>
</body>
</html>'''
    
    output = Path("generated_reports/M6_Comprehensive_FINAL.html")
    output.write_text(html_m6, encoding='utf-8')
    print(f"✅ M6: {output}")
    return str(output)

if __name__ == "__main__":
    print("🚀 Generating M5 & M6...")
    generate_m5()
    generate_m6()
    print("✅ All done!")
