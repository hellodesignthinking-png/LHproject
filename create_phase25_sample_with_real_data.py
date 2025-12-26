#!/usr/bin/env python3
"""
실제 데이터로 Phase 2.5 샘플 보고서 생성
업로드된 PDF의 데이터를 기반으로 Phase 2.5 스타일 적용
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.final_report_html_renderer import render_final_report_html
from datetime import datetime

# 업로드된 PDF의 실제 데이터
REAL_DATA_FROM_PDF = {
    'context_id': '116801010001230045',
    'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    
    # 실제 데이터 (PDF에서 확인됨)
    'land_value_krw': 1621848717,  # 토지감정가
    'npv_krw': 793000000,  # NPV
    'irr_pct': None,  # IRR 산출 불가 (PDF에서 확인)
    'roi_pct': None,  # ROI 산출 불가
    'legal_units': 26,  # 총 세대수 (전체 통합 보고서에서 확인)
    'recommended_housing_type': '산출 진행 중',  # 주택 유형
    'final_decision': '적합',  # LH 판단
    'grade': '등급 산정 중',
    
    # 추가 데이터 (보고서 생성용)
    'approval_probability_pct': 75,  # 추정값
    'zoning': '제2종일반주거지역',
    'address': '서울/경기 지역',
    'land_area_sqm': 500,
    'land_area_pyeong': 151,
    'transit_access': '지하철역 500m 이내',
    
    # 빈 구조 (기본값)
    'policy_context': {},
    'land_value': {'total_krw': 1621848717},
    'financial': {
        'npv_krw': 793000000
    },
    'lh_review': {
        'grade': '등급 산정 중'
    },
    'project_scale': {
        'total_units': 26
    }
}

def generate_phase25_reports():
    """Phase 2.5 스타일로 보고서 생성"""
    
    print("=" * 80)
    print("🎨 Phase 2.5 스타일 보고서 생성 (실제 데이터)")
    print("=" * 80)
    print()
    
    report_types = [
        ('all_in_one', '전체 통합 보고서'),
        ('financial_feasibility', '사업성 중심 보고서'),
        ('executive_summary', '경영진용 요약본')
    ]
    
    output_dir = '/home/user/webapp/final_reports_phase25'
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    for report_type, korean_name in report_types:
        print(f"📄 생성 중: {korean_name} ({report_type})...")
        
        try:
            # Phase 2.5 HTML 렌더링
            html = render_final_report_html(report_type, REAL_DATA_FROM_PDF)
            
            # 파일 저장
            output_path = f'{output_dir}/{report_type}_phase25_real_data.html'
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            size = len(html)
            
            # Phase 2.5 검증
            has_kpi_card = 'kpi-summary-card' in html
            has_profitability = 'profitability-conclusion' in html
            has_final_conclusion = 'final-decision-highlight' in html
            na_old_count = html.count('N/A (검증 필요)')
            
            result = {
                'type': report_type,
                'name': korean_name,
                'size': size,
                'path': output_path,
                'kpi_card': has_kpi_card,
                'profitability': has_profitability,
                'final_conclusion': has_final_conclusion,
                'na_old': na_old_count
            }
            results.append(result)
            
            print(f"   ✅ 완료: {size:,} chars")
            print(f"   📁 {output_path}")
            print(f"   🎨 KPI 카드: {'✅' if has_kpi_card else '❌'}")
            if report_type == 'financial_feasibility':
                print(f"   💰 수익성 결론: {'✅' if has_profitability else '❌'}")
            if report_type == 'all_in_one':
                print(f"   🏁 최종 결론 강조: {'✅' if has_final_conclusion else '❌'}")
            print(f"   📊 N/A (구형): {na_old_count}개")
            print()
            
        except Exception as e:
            print(f"   ❌ 실패: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    # 요약
    print("=" * 80)
    print("📋 생성 결과")
    print("=" * 80)
    print()
    
    total_size = sum(r['size'] for r in results)
    kpi_count = sum(1 for r in results if r['kpi_card'])
    
    print(f"✅ 생성된 보고서: {len(results)}개")
    print(f"📊 총 크기: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    print(f"🎨 Phase 2.5 KPI 카드: {kpi_count}/{len(results)}")
    print()
    
    for r in results:
        kpi_icon = '✅' if r['kpi_card'] else '❌'
        print(f"   {kpi_icon} {r['name']:20s} | {r['size']:>10,} bytes")
    
    print()
    print("📥 다운로드 경로: /home/user/webapp/final_reports_phase25/")
    print()
    print("=" * 80)

if __name__ == '__main__':
    generate_phase25_reports()

# 나머지 3개 보고서 생성
def generate_remaining_reports():
    """나머지 3종 보고서 생성"""
    
    report_types = [
        ('quick_check', '빠른 검토용'),
        ('lh_technical', 'LH 기술검토용'),
        ('landowner_summary', '토지주용 요약본')
    ]
    
    output_dir = '/home/user/webapp/final_reports_phase25'
    
    print("\n" + "=" * 80)
    print("🎨 나머지 3종 보고서 생성")
    print("=" * 80)
    print()
    
    results = []
    
    for report_type, korean_name in report_types:
        print(f"📄 생성 중: {korean_name} ({report_type})...")
        
        try:
            html = render_final_report_html(report_type, REAL_DATA_FROM_PDF)
            
            output_path = f'{output_dir}/{report_type}_phase25_real_data.html'
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            size = len(html)
            has_kpi_card = 'kpi-summary-card' in html
            na_old_count = html.count('N/A (검증 필요)')
            
            result = {
                'type': report_type,
                'name': korean_name,
                'size': size,
                'kpi_card': has_kpi_card,
                'na_old': na_old_count
            }
            results.append(result)
            
            print(f"   ✅ 완료: {size:,} chars")
            print(f"   📁 {output_path}")
            print(f"   🎨 KPI 카드: {'✅' if has_kpi_card else '❌'}")
            print(f"   📊 N/A (구형): {na_old_count}개")
            print()
            
        except Exception as e:
            print(f"   ❌ 실패: {e}")
            print()
    
    # 최종 요약
    print("=" * 80)
    print("📋 전체 6종 보고서 완성!")
    print("=" * 80)
    print()
    
    total_size = sum(r['size'] for r in results)
    kpi_count = sum(1 for r in results if r['kpi_card'])
    
    print(f"✅ 추가 생성: {len(results)}개")
    print(f"📊 총 크기: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    print(f"🎨 Phase 2.5 KPI 카드: {kpi_count}/{len(results)}")
    print()
    
    for r in results:
        kpi_icon = '✅' if r['kpi_card'] else '❌'
        print(f"   {kpi_icon} {r['name']:20s} | {r['size']:>10,} bytes")
    
    print()

if __name__ == '__main__':
    generate_remaining_reports()
