#!/usr/bin/env python3
"""
_wrap_module_html에 출처 참조 추가
Add source references to _wrap_module_html method
"""

import re
from pathlib import Path

def add_source_reference_to_wrap(content: str) -> str:
    """_wrap_module_html 메서드에 출처 참조 추가"""
    
    # 기존 _wrap_module_html 메서드를 찾아서 source reference 추가
    old_pattern = r'''def _wrap_module_html\(self, module_id: str, html: str\) -> str:
        """Wrap module HTML in section container"""
        return f"""
        <section class="module-section" data-module="{module_id}">
            {html}
        </section>
        """'''
    
    new_pattern = '''def _wrap_module_html(self, module_id: str, html: str) -> str:
        """Wrap module HTML in section container with source reference"""
        # [FIX 6] 모듈 출처 참조 추가 (Module Source Traceability)
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
        """'''
    
    # 정규식으로 매칭 (공백 무시)
    pattern = r'def _wrap_module_html\(self, module_id: str, html: str\) -> str:\s*"""Wrap module HTML in section container"""\s*return f"""\s*<section class="module-section" data-module="\{module_id\}">\s*\{html\}\s*</section>\s*"""'
    
    if re.search(pattern, content, re.DOTALL):
        # 더 간단한 교체 방식 사용
        content = re.sub(
            r'(def _wrap_module_html\(self, module_id: str, html: str\) -> str:)\s*("""Wrap module HTML in section container""")',
            r'\1\n        """Wrap module HTML in section container with source reference"""',
            content
        )
        
        # return문 앞에 source reference 생성 로직 추가
        content = re.sub(
            r'(def _wrap_module_html\(self, module_id: str, html: str\) -> str:\s*"""[^"]*"""\s*)return f"""',
            r'''\1# [FIX 6] 모듈 출처 참조 추가 (Module Source Traceability)
        module_names = {
            "M2": "토지 평가",
            "M3": "LH 선호유형",
            "M4": "건축규모",
            "M5": "사업성 분석",
            "M6": "LH 심사 대응"
        }
        module_name = module_names.get(module_id, "분석 결과")
        source_ref = self.generate_source_reference(module_id, module_name)
        
        return f"""''',
            content,
            count=1
        )
        
        # HTML 템플릿에 source_ref 추가
        content = re.sub(
            r'(<section class="module-section" data-module="\{module_id\}">\s*\{html\}\s*)(</section>)',
            r'\1{source_ref}\n            \2',
            content,
            count=1
        )
    
    return content

def main():
    """메인 실행"""
    print("=" * 80)
    print("_wrap_module_html에 출처 참조 추가")
    print("ADD SOURCE REFERENCES TO _wrap_module_html")
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
        
        try:
            content = filepath.read_text(encoding='utf-8')
            original = content
            
            # 이미 module_names 딕셔너리가 있으면 스킵
            if 'module_names = {' in content and '"M2": "토지 평가"' in content:
                print(f"   ℹ️ 이미 출처 참조 로직 존재")
                continue
            
            content = add_source_reference_to_wrap(content)
            
            if content != original:
                filepath.write_text(content, encoding='utf-8')
                print(f"   ✅ 출처 참조 추가 완료")
                success_count += 1
            else:
                print(f"   ℹ️ 변경사항 없음")
                
        except Exception as e:
            print(f"   ❌ 오류: {e}")
    
    print("\n" + "=" * 80)
    print(f"✅ 성공: {success_count}/{len(assembler_files)} 파일")
    print("=" * 80)
    
    if success_count > 0:
        print("\n🎉 출처 참조 추가 완료!")
        return 0
    else:
        print("\nℹ️ 모든 파일이 이미 최신 상태")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
