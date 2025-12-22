#!/usr/bin/env python3
"""
모듈 출처 참조 추가 패치
Add Module Source References Patch

PURPOSE: FIX 6 - 모듈 출처 추적성 강화
         Enhance module source traceability for trust & audit compliance
"""

import re
from pathlib import Path

class SourceReferencePatcher:
    """출처 참조 패치 적용기"""
    
    def __init__(self, project_root: str = "/home/user/webapp"):
        self.project_root = Path(project_root)
        self.assembler_dir = self.project_root / "app/services/final_report_assembly/assemblers"
        
    def add_source_references(self, content: str, filename: str) -> str:
        """모듈 HTML 섹션 뒤에 출처 참조 추가"""
        
        # M2 출처 참조 추가
        if 'm2_html' in content:
            # M2 sanitize 뒤에 출처 추가
            content = re.sub(
                r'(self\._sanitize_module_html\(m2_html\))',
                r'\1,\n            self.generate_source_reference("M2", "토지 평가")',
                content,
                count=1
            )
        
        # M3 출처 참조 추가
        if 'm3_html' in content:
            content = re.sub(
                r'(self\._sanitize_module_html\(m3_html\))',
                r'\1,\n            self.generate_source_reference("M3", "LH 선호유형")',
                content,
                count=1
            )
        
        # M4 출처 참조 추가
        if 'm4_html' in content:
            content = re.sub(
                r'(self\._sanitize_module_html\(m4_html\))',
                r'\1,\n            self.generate_source_reference("M4", "건축규모")',
                content,
                count=1
            )
        
        # M5 출처 참조 추가
        if 'm5_html' in content:
            content = re.sub(
                r'(self\._sanitize_module_html\(m5_html\))',
                r'\1,\n            self.generate_source_reference("M5", "사업성 분석")',
                content,
                count=1
            )
        
        # M6 출처 참조 추가
        if 'm6_html' in content:
            content = re.sub(
                r'(self\._sanitize_module_html\(m6_html\))',
                r'\1,\n            self.generate_source_reference("M6", "LH 심사 대응")',
                content,
                count=1
            )
        
        return content
    
    def patch_assembler(self, filename: str) -> bool:
        """단일 어셈블러 패치"""
        filepath = self.assembler_dir / filename
        
        if not filepath.exists():
            print(f"❌ 파일 없음: {filepath}")
            return False
        
        print(f"\n📝 패치 적용 중: {filename}")
        
        try:
            content = filepath.read_text(encoding='utf-8')
            original_content = content
            
            # 이미 source_reference가 있으면 스킵
            if 'generate_source_reference' in content:
                print(f"   ℹ️ 이미 출처 참조 사용 중")
                return False
            
            # 출처 참조 추가
            content = self.add_source_references(content, filename)
            
            if content != original_content:
                filepath.write_text(content, encoding='utf-8')
                print(f"   ✅ 출처 참조 추가 완료")
                return True
            else:
                print(f"   ℹ️ 변경사항 없음")
                return False
                
        except Exception as e:
            print(f"   ❌ 오류: {e}")
            return False
    
    def patch_all_assemblers(self) -> dict:
        """모든 어셈블러 패치"""
        results = {}
        
        assembler_files = [
            "landowner_summary.py",
            "lh_technical.py",
            "quick_check.py",
            "financial_feasibility.py",
            "all_in_one.py",
            "executive_summary.py"
        ]
        
        for filename in assembler_files:
            results[filename] = self.patch_assembler(filename)
        
        return results


def main():
    """메인 실행"""
    print("=" * 80)
    print("모듈 출처 참조 추가 패치")
    print("ADD MODULE SOURCE REFERENCES PATCH")
    print("=" * 80)
    print("\n🎯 목표: FIX 6 - 모듈 출처 추적성 강화")
    print("   Goal: Enhance module source traceability\n")
    
    patcher = SourceReferencePatcher()
    results = patcher.patch_all_assemblers()
    
    success_count = sum(1 for v in results.values() if v)
    
    print("\n" + "=" * 80)
    print("패치 적용 결과")
    print("=" * 80)
    print(f"✅ 성공: {success_count}/{len(results)} 파일\n")
    
    for filename, success in results.items():
        status = "✅" if success else "ℹ️"
        print(f"{status} {filename}")
    
    print("\n" + "=" * 80)
    
    if success_count > 0:
        print("🎉 출처 참조 추가 완료!")
        print("✅ 다음: python final_comprehensive_audit.py 재실행")
        return 0
    else:
        print("ℹ️ 모든 파일이 이미 출처 참조 사용 중 또는 변경 불필요")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
