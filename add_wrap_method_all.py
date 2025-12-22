#!/usr/bin/env python3
"""
모든 어셈블러에 _wrap_module_html with source reference 추가
Add _wrap_module_html with source reference to all assemblers
"""

import re
from pathlib import Path

WRAP_METHOD_WITH_SOURCE_REF = '''
    def _wrap_module_html(self, module_id: str, html: str) -> str:
        """[FIX 6] Wrap module HTML with source reference for traceability"""
        module_names = {
            "M2": "토지 평가",
            "M3": "LH 선호유형",
            "M4": "건축규모",
            "M5": "사업성 분석",
            "M6": "LH 심사 대응"
        }
        module_name = module_names.get(module_id, "분석 결과")
        source_ref = self.generate_source_reference(module_id, module_name)
        
        return f"""
        <section class="module-section" data-module="{module_id}">
            {html}
            {source_ref}
        </section>
        """
'''

def add_wrap_method_to_file(filepath: Path) -> bool:
    """파일에 _wrap_module_html 메서드 추가"""
    content = filepath.read_text(encoding='utf-8')
    
    # 이미 _wrap_module_html이 정의되어 있는지 확인
    if 'def _wrap_module_html' in content:
        # 이미 있지만 source_ref가 없으면 업데이트
        if 'source_ref' not in content or 'generate_source_reference' not in content:
            print(f"   ℹ️ _wrap_module_html 존재하지만 source_ref 없음 - 업데이트 필요")
            # 기존 메서드 제거하고 새 메서드 추가
            content = re.sub(
                r'def _wrap_module_html\(self, module_id: str, html: str\) -> str:.*?""".*?""".*?return f""".*?"""',
                WRAP_METHOD_WITH_SOURCE_REF.strip(),
                content,
                flags=re.DOTALL,
                count=1
            )
        else:
            print(f"   ✅ 이미 source reference 포함된 _wrap_module_html 존재")
            return False
    else:
        # 메서드가 없으면 추가 - _generate_footer 앞에 삽입
        if 'def _generate_footer' in content:
            content = content.replace(
                '    def _generate_footer',
                WRAP_METHOD_WITH_SOURCE_REF + '\n    def _generate_footer'
            )
        # 또는 _generate_cover_page 뒤에 삽입
        elif 'def _generate_cover_page' in content:
            # _generate_cover_page 메서드 끝 찾기
            pattern = r'(def _generate_cover_page\(self.*?\n\s+""")'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                # 다음 메서드 앞에 삽입
                next_method = re.search(r'\n    def ', content[match.end():])
                if next_method:
                    insert_pos = match.end() + next_method.start()
                    content = content[:insert_pos] + '\n' + WRAP_METHOD_WITH_SOURCE_REF + content[insert_pos:]
        # 또는 클래스 끝 부분에 추가
        else:
            # 마지막 메서드 뒤에 추가
            content = content.rstrip() + '\n' + WRAP_METHOD_WITH_SOURCE_REF + '\n'
    
    filepath.write_text(content, encoding='utf-8')
    return True

def main():
    """메인 실행"""
    print("=" * 80)
    print("모든 어셈블러에 _wrap_module_html with source reference 추가")
    print("=" * 80)
    
    project_root = Path("/home/user/webapp")
    assembler_dir = project_root / "app/services/final_report_assembly/assemblers"
    
    assembler_files = [
        "landowner_summary.py",
        "lh_technical.py",
        "quick_check.py",
        "financial_feasibility.py",
        "all_in_one.py",
        "executive_summary.py"
    ]
    
    success_count = 0
    
    for filename in assembler_files:
        filepath = assembler_dir / filename
        
        if not filepath.exists():
            print(f"❌ {filename}: 파일 없음")
            continue
        
        print(f"\n📝 {filename}")
        
        # 먼저 이 파일이 _wrap_module_html을 사용하는지 확인
        content = filepath.read_text(encoding='utf-8')
        if '_wrap_module_html(' not in content:
            print(f"   ℹ️ _wrap_module_html 미사용 - 스킵")
            continue
        
        try:
            if add_wrap_method_to_file(filepath):
                print(f"   ✅ _wrap_module_html with source reference 추가/업데이트 완료")
                success_count += 1
        except Exception as e:
            print(f"   ❌ 오류: {e}")
    
    print("\n" + "=" * 80)
    print(f"✅ 성공: {success_count}/{len(assembler_files)} 파일")
    print("=" * 80)
    
    if success_count > 0:
        print("\n🎉 모듈 출처 참조 통합 완료!")
        print("✅ 다음: python final_comprehensive_audit.py 재실행")
        return 0
    else:
        print("\nℹ️ 모든 파일이 이미 최신 상태")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
