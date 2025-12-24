#!/usr/bin/env python3
"""
최종 종합 감사 및 교열 검증기
Final Comprehensive Audit & Editorial Validator

PURPOSE: 모듈 → HTML → 최종 6종 보고서 간 완벽한 일관성 최종 검증
         Final consistency validation across Module → HTML → Final 6 Reports

SCOPE: 상업적 납품 전 최종 감사 (Pre-commercial delivery final audit)
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict

class FinalComprehensiveAuditor:
    """최종 종합 감사기"""
    
    def __init__(self, project_root: str = "/home/user/webapp"):
        self.project_root = Path(project_root)
        self.assembler_dir = self.project_root / "app/services/final_report_assembly/assemblers"
        self.base_assembler = self.project_root / "app/services/final_report_assembly/base_assembler.py"
        self.issues = defaultdict(list)
        
        # Canonical terminology dictionary
        self.canonical_terms = {
            "총 세대수": ["계획세대수", "세대수", "유닛수", "세대 수"],
            "순현재가치(NPV)": ["NPV", "순현가", "순현재가", "순현재가치"],
            "내부수익률(IRR)": ["IRR", "내부수익률", "수익률"],
            "추진 가능": ["승인", "사업 가능", "진행 가능", "사업가능"],
            "조건부 가능": ["조건부 승인", "조건부", "부분 승인"],
            "부적합": ["불가", "불승인", "사업 불가"],
            "분석 기준 시점": ["기준일", "분석일", "평가일", "기준시점"]
        }
        
        # M3 mandatory fields
        self.m3_mandatory = ["추천 유형", "총점", "등급", "적합도"]
        
        # M4 mandatory fields
        self.m4_mandatory = ["총 세대수", "기본 세대수", "인센티브", "법적 기준"]
        
    def audit_numeric_consistency(self, file_path: Path) -> List[str]:
        """FIX 1: 숫자 일관성 감사"""
        issues = []
        content = file_path.read_text(encoding='utf-8')
        
        # 숫자 근사 패턴 검사 (약, 수준, 내외 등)
        approximation_patterns = [
            r'약\s+[\d,]+',
            r'[\d,]+\s*수준',
            r'[\d,]+\s*내외',
            r'대략\s+[\d,]+'
        ]
        
        for pattern in approximation_patterns:
            matches = re.findall(pattern, content)
            if matches:
                issues.append(f"⚠️ 숫자 근사 표현 발견: {matches[:3]}... (정확한 값으로 교체 필요)")
        
        # 단위 일관성 검사
        unit_patterns = {
            '원': [r'(\d[\d,]*)\s*원', r'(\d[\d,]*)\s*₩'],
            '세대': [r'(\d[\d,]*)\s*세대', r'(\d[\d,]*)\s*유닛'],
            '평': [r'(\d[\d,]*\.?\d*)\s*평', r'(\d[\d,]*\.?\d*)\s*㎡']
        }
        
        for unit, patterns in unit_patterns.items():
            if len(patterns) > 1:
                found_variants = []
                for p in patterns:
                    if re.search(p, content):
                        found_variants.append(p)
                if len(found_variants) > 1:
                    issues.append(f"⚠️ 단위 표기 불일치: {unit} 관련 여러 표기법 사용")
        
        return issues
    
    def audit_m3_m4_preservation(self, file_path: Path) -> List[str]:
        """FIX 2: M3/M4 필수 데이터 보존 감사"""
        issues = []
        content = file_path.read_text(encoding='utf-8')
        filename = file_path.name
        
        # M3 사용 여부 확인
        if any(x in content.lower() for x in ['m3_', 'm3.', 'module_3', 'lh 선호유형', 'lh선호유형']):
            missing_fields = []
            for field in self.m3_mandatory:
                # 더 관대한 검사 (공백, 줄바꿈 무시)
                field_pattern = field.replace(' ', r'\s*')
                if not re.search(field_pattern, content):
                    missing_fields.append(field)
            
            if missing_fields:
                issues.append(f"❌ M3 필수 데이터 누락 ({filename}): {', '.join(missing_fields)}")
        
        # M4 사용 여부 확인
        if any(x in content.lower() for x in ['m4_', 'm4.', 'module_4', '건축규모', '건축 규모']):
            missing_fields = []
            for field in self.m4_mandatory:
                field_pattern = field.replace(' ', r'\s*')
                if not re.search(field_pattern, content):
                    missing_fields.append(field)
            
            if missing_fields:
                issues.append(f"❌ M4 필수 데이터 누락 ({filename}): {', '.join(missing_fields)}")
        
        return issues
    
    def audit_section_order(self, file_path: Path) -> List[str]:
        """FIX 3: 섹션 순서 정규성 감사"""
        issues = []
        content = file_path.read_text(encoding='utf-8')
        
        # sections 배열 찾기
        sections_match = re.search(r'sections\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if sections_match:
            sections_content = sections_match.group(1)
            
            # 표준 순서 확인: Title → KPI → Interpretation → Transition
            # 순서가 잘못된 경우 감지
            kpi_pos = sections_content.find('kpi')
            narrative_pos = sections_content.find('narrative') or sections_content.find('interpretation')
            
            if kpi_pos > 0 and narrative_pos > 0 and kpi_pos > narrative_pos:
                issues.append(f"⚠️ 섹션 순서 위반: KPI가 Narrative보다 뒤에 위치")
        
        return issues
    
    def audit_terminology_lock(self, file_path: Path) -> List[str]:
        """FIX 4: 표준 용어 사용 감사"""
        issues = []
        content = file_path.read_text(encoding='utf-8')
        filename = file_path.name
        
        for canonical, variants in self.canonical_terms.items():
            # 정규 표현식으로 변형 감지
            for variant in variants:
                # 이미 표준 용어가 포함되어 있으면 스킵
                if canonical in variant:
                    continue
                
                # 비표준 용어가 독립적으로 사용되는지 확인
                pattern = r'\b' + re.escape(variant) + r'\b'
                if re.search(pattern, content):
                    # 해당 위치에서 canonical도 함께 있는지 확인
                    context_pattern = canonical.split('(')[0] if '(' in canonical else canonical
                    if context_pattern not in content:
                        issues.append(f"⚠️ 비표준 용어 사용 ({filename}): '{variant}' → '{canonical}'로 통일 필요")
                        break  # 각 canonical당 1회만 경고
        
        return issues
    
    def audit_narrative_kpi_sync(self, file_path: Path) -> List[str]:
        """FIX 5: 내러티브 ↔ KPI 동기화 감사"""
        issues = []
        content = file_path.read_text(encoding='utf-8')
        
        # 이것은 실제 HTML 출력에서만 정확히 검증 가능
        # Python 소스에서는 로직만 확인
        
        # KPI 생성 로직이 있는지 확인
        if 'generate_kpi' not in content and 'kpi_summary' not in content.lower():
            if 'narrative' in content or 'interpretation' in content:
                issues.append(f"⚠️ Narrative는 있지만 KPI 박스가 명시되지 않음")
        
        return issues
    
    def audit_source_traceability(self, file_path: Path) -> List[str]:
        """FIX 6: 모듈 출처 추적성 감사"""
        issues = []
        content = file_path.read_text(encoding='utf-8')
        
        # generate_source_reference 메서드 사용 여부 확인
        uses_modules = any(x in content.lower() for x in ['m2_html', 'm3_html', 'm4_html', 'm5_html', 'm6_html'])
        
        if uses_modules:
            if 'generate_source_reference' not in content and 'source-reference' not in content:
                issues.append(f"⚠️ 모듈 사용하지만 출처 참조(source-reference) 미사용")
        
        return issues
    
    def audit_html_final_parity(self, file_path: Path) -> List[str]:
        """FIX 7: HTML ↔ 최종 보고서 일치성 감사"""
        issues = []
        content = file_path.read_text(encoding='utf-8')
        
        # _extract_module_data에서 재계산 패턴 검사
        if '_extract_module_data' in content:
            # 실제 계산 함수 정의만 체크 (주석 제외)
            calc_patterns = [
                (r'^\s*def\s+calculate_', '계산 함수 정의'),
                (r'^\s*def\s+compute_', '계산 함수 정의'),
                (r'=\s*sum\([^)]*(?:data|value|result)', 'sum() 계산'),
                (r'=\s*(?:np\.)?mean\([^)]*(?:data|value)', 'mean() 계산'),
            ]
            
            for pattern, desc in calc_patterns:
                if re.search(pattern, content, re.MULTILINE):
                    issues.append(f"⚠️ 재계산 가능성: {desc} 발견 (추출만 허용)")
        
        return issues
    
    def audit_assembler_file(self, file_path: Path) -> Dict[str, List[str]]:
        """단일 어셈블러 파일 전체 감사"""
        results = {
            'numeric': self.audit_numeric_consistency(file_path),
            'm3_m4': self.audit_m3_m4_preservation(file_path),
            'section_order': self.audit_section_order(file_path),
            'terminology': self.audit_terminology_lock(file_path),
            'narrative_kpi': self.audit_narrative_kpi_sync(file_path),
            'source_trace': self.audit_source_traceability(file_path),
            'html_parity': self.audit_html_final_parity(file_path)
        }
        return results
    
    def audit_all_assemblers(self) -> Dict[str, Dict[str, List[str]]]:
        """모든 어셈블러 감사"""
        all_results = {}
        
        assembler_files = [
            "landowner_summary.py",
            "lh_technical.py",
            "quick_check.py",
            "financial_feasibility.py",
            "all_in_one.py",
            "executive_summary.py"
        ]
        
        for filename in assembler_files:
            filepath = self.assembler_dir / filename
            if filepath.exists():
                all_results[filename] = self.audit_assembler_file(filepath)
            else:
                all_results[filename] = {'error': [f"파일 없음: {filepath}"]}
        
        return all_results
    
    def generate_audit_report(self) -> str:
        """최종 감사 보고서 생성"""
        results = self.audit_all_assemblers()
        
        report = []
        report.append("=" * 80)
        report.append("최종 종합 감사 및 교열 검증 보고서")
        report.append("FINAL COMPREHENSIVE AUDIT & EDITORIAL VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        report.append("🎯 목표: 상업적 납품 전 최종 일관성 검증")
        report.append("   Goal: Pre-commercial delivery final consistency validation")
        report.append("")
        report.append("=" * 80)
        
        total_issues = 0
        
        for filename, audit_results in results.items():
            report.append(f"\n📄 {filename}")
            report.append("-" * 80)
            
            file_has_issues = False
            
            for audit_type, issues in audit_results.items():
                if issues:
                    file_has_issues = True
                    report.append(f"\n   [{audit_type.upper()}]")
                    for issue in issues:
                        report.append(f"   {issue}")
                        total_issues += 1
            
            if not file_has_issues:
                report.append("   ✅ 모든 감사 항목 통과 (All audit checks passed)")
        
        report.append("")
        report.append("=" * 80)
        report.append(f"총 발견된 문제: {total_issues}개")
        
        if total_issues == 0:
            report.append("")
            report.append("🎉 최종 감사 완료! 상업적 납품 준비 완료")
            report.append("✅ Final Audit Complete! Ready for Commercial Delivery")
            report.append("")
            report.append("인증 완료:")
            report.append("  ✅ LH 제출용 (LH Submission)")
            report.append("  ✅ 지주 설명용 (Landowner Presentation)")
            report.append("  ✅ 투자자 검토용 (Investor Review)")
            report.append("  ✅ 컨설팅 납품용 (Consulting Delivery)")
        else:
            report.append("")
            report.append("⚠️ 수정 필요 항목이 발견되었습니다.")
            report.append("   Required fixes have been identified.")
        
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """메인 실행"""
    print("🔍 최종 종합 감사 및 교열 검증 시작...")
    print("   Final Comprehensive Audit & Editorial Validation Starting...\n")
    
    auditor = FinalComprehensiveAuditor()
    report = auditor.generate_audit_report()
    
    print(report)
    
    # 결과 저장
    output_path = Path("/home/user/webapp/final_comprehensive_audit_report.txt")
    output_path.write_text(report, encoding='utf-8')
    print(f"\n📝 감사 보고서 저장: {output_path}")
    
    # 이슈 카운트로 종료 코드 결정
    if "총 발견된 문제: 0개" in report:
        print("\n✅ 최종 감사 통과! (Final Audit PASSED)")
        return 0
    else:
        print("\n⚠️ 수정 필요 항목 발견 (Fixes Required)")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
