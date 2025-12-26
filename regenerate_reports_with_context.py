#!/usr/bin/env python3
"""
ZeroSite v4.0 - 실제 Context ID로 Phase 2.5 보고서 재생성
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.final_report_assembler import assemble_final_report
from app.services.final_report_html_renderer import render_final_report_html

def regenerate_all_reports(context_id: str):
    """6종 보고서 전체 재생성"""
    
    report_types = [
        'all_in_one',
        'financial_feasibility',
        'lh_technical',
        'executive_summary',
        'landowner_summary',
        'quick_check'
    ]
    
    results = []
    
    print("=" * 80)
    print(f"🔄 6종 보고서 재생성 (Context ID: {context_id})")
    print("=" * 80)
    print()
    
    for report_type in report_types:
        print(f"📄 Generating: {report_type}...")
        
        try:
            # 1. 데이터 조립
            data = assemble_final_report(context_id, report_type)
            
            # 2. HTML 렌더링 (Phase 2.5 적용)
            html = render_final_report_html(report_type, data)
            
            # 3. 파일 저장
            output_path = f'/home/user/webapp/final_reports/{report_type}_{context_id}.html'
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            size = len(html)
            
            # 4. Phase 2.5 요소 검증
            has_kpi_card = 'kpi-summary-card' in html
            has_final_conclusion = 'final-decision-highlight' in html or '최종 결론' in html
            na_count = html.count('N/A (검증 필요)')
            
            result = {
                'report_type': report_type,
                'status': 'success',
                'size': size,
                'path': output_path,
                'phase25_kpi_card': '✅' if has_kpi_card else '❌',
                'phase25_conclusion': '✅' if (report_type == 'all_in_one' and has_final_conclusion) or report_type != 'all_in_one' else '⚠️',
                'na_count': na_count
            }
            
            results.append(result)
            
            print(f"   ✅ Success: {size:,} chars")
            print(f"   📁 Saved: {output_path}")
            print(f"   🎨 Phase 2.5 KPI Card: {result['phase25_kpi_card']}")
            print(f"   📊 N/A count: {na_count}")
            print()
            
        except Exception as e:
            result = {
                'report_type': report_type,
                'status': 'failed',
                'error': str(e)
            }
            results.append(result)
            print(f"   ❌ Failed: {e}")
            print()
    
    # 요약
    print("=" * 80)
    print("📋 재생성 결과 요약")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    total_size = sum(r.get('size', 0) for r in results if r['status'] == 'success')
    
    print(f"\n✅ 성공: {success_count}/{len(report_types)}")
    print(f"📊 총 크기: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    print()
    
    print("📁 생성된 파일:")
    for r in results:
        if r['status'] == 'success':
            print(f"   - {r['report_type']:25s} | {r['size']:>10,} bytes | KPI: {r['phase25_kpi_card']} | N/A: {r['na_count']}")
    
    print()
    
    # Phase 2.5 검증
    kpi_cards = sum(1 for r in results if r.get('phase25_kpi_card') == '✅')
    print(f"🎨 Phase 2.5 적용 확인:")
    print(f"   - KPI 카드: {kpi_cards}/{success_count}")
    
    if kpi_cards == success_count:
        print()
        print("✅ Phase 2.5 완전 적용됨!")
        print("🚀 보고서를 다운로드하여 확인하세요.")
    else:
        print()
        print("⚠️  일부 보고서에 Phase 2.5 미적용")
    
    print()
    print("=" * 80)

if __name__ == '__main__':
    context_id = '116801010001230045'
    regenerate_all_reports(context_id)
