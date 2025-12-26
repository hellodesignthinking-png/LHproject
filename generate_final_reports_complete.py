#!/usr/bin/env python3
"""
ZeroSite v4.0 - 실제 Context ID로 Phase 2.5 보고서 100% 완성
"""

import sys
import os
sys.path.insert(0, '/home/user/webapp')

# Context 저장소에서 실제 데이터 로드
from app.services.context_storage import load_context
from app.services.final_report_assembler import assemble_final_report
from app.services.final_report_html_renderer import render_final_report_html

def generate_reports_for_context(context_id: str):
    """Context ID로 6종 보고서 생성"""
    
    print("=" * 80)
    print(f"🔄 Phase 2.5 보고서 100% 완성")
    print(f"Context ID: {context_id}")
    print("=" * 80)
    print()
    
    # 1. Context 데이터 로드
    print("📊 Step 1: Context 데이터 로드...")
    try:
        context_data = load_context(context_id)
        if not context_data:
            print(f"   ❌ Context ID '{context_id}'를 찾을 수 없습니다.")
            print(f"   💡 Context 저장소에 데이터가 있는지 확인하세요.")
            return
        print(f"   ✅ Context 데이터 로드 완료")
    except Exception as e:
        print(f"   ❌ Context 로드 실패: {e}")
        return
    
    print()
    
    # 2. Canonical 데이터 구성
    print("📦 Step 2: Canonical 데이터 구성...")
    canonical_data = context_data  # Context 데이터를 그대로 사용
    print("   ✅ Canonical 데이터 준비 완료")
    print()
    
    # 3. 6종 보고서 생성
    report_types = [
        ('all_in_one', '전체 통합 보고서'),
        ('financial_feasibility', '사업성 중심 보고서'),
        ('lh_technical', 'LH 기술검토용'),
        ('executive_summary', '경영진용 요약본'),
        ('landowner_summary', '토지주용 요약본'),
        ('quick_check', '빠른 검토용')
    ]
    
    output_dir = '/home/user/webapp/final_reports_phase25'
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    for report_type, korean_name in report_types:
        print(f"📄 Step 3.{len(results)+1}: {korean_name} ({report_type})...")
        
        try:
            # 데이터 조립
            data = assemble_final_report(report_type, canonical_data, context_id)
            
            # HTML 렌더링 (Phase 2.5 적용)
            html = render_final_report_html(report_type, data)
            
            # 파일 저장
            output_path = f'{output_dir}/{report_type}_{context_id}.html'
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            size = len(html)
            
            # Phase 2.5 검증
            has_kpi_card = 'kpi-summary-card' in html
            na_old_count = html.count('N/A (검증 필요)')
            na_new_count = html.count('본 ') + html.count('산출 진행 중')  # Phase 2.5 설명 문장
            
            result = {
                'type': report_type,
                'name': korean_name,
                'status': 'success',
                'size': size,
                'path': output_path,
                'kpi_card': has_kpi_card,
                'na_old': na_old_count,
                'na_new': na_new_count
            }
            results.append(result)
            
            print(f"   ✅ 생성 완료: {size:,} chars")
            print(f"   📁 저장: {output_path}")
            print(f"   🎨 KPI 카드: {'✅ 있음' if has_kpi_card else '❌ 없음'}")
            print(f"   📊 N/A (구): {na_old_count}개")
            
        except Exception as e:
            result = {
                'type': report_type,
                'name': korean_name,
                'status': 'failed',
                'error': str(e)
            }
            results.append(result)
            print(f"   ❌ 실패: {e}")
        
        print()
    
    # 4. 최종 요약
    print("=" * 80)
    print("📋 최종 결과 요약")
    print("=" * 80)
    print()
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    total_size = sum(r.get('size', 0) for r in results if r['status'] == 'success')
    kpi_count = sum(1 for r in results if r.get('kpi_card', False))
    
    print(f"✅ 성공: {success_count}/{len(report_types)}")
    print(f"📊 총 크기: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    print(f"🎨 Phase 2.5 KPI 카드: {kpi_count}/{success_count}")
    print()
    
    print("📁 생성된 파일:")
    for r in results:
        if r['status'] == 'success':
            kpi_icon = '✅' if r['kpi_card'] else '❌'
            print(f"   {kpi_icon} {r['name']:20s} | {r['size']:>10,} bytes | {r['path']}")
    
    print()
    
    if success_count == len(report_types) and kpi_count == success_count:
        print("🎉 Phase 2.5 보고서 100% 완성!")
        print("📥 다운로드: /home/user/webapp/final_reports_phase25/")
    else:
        print("⚠️  일부 보고서 생성 실패 또는 Phase 2.5 미적용")
    
    print()
    print("=" * 80)

if __name__ == '__main__':
    context_id = '116801010001230045'
    generate_reports_for_context(context_id)
