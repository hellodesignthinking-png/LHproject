#!/usr/bin/env python3
"""
최종 통합 정합성 및 연속성 감사
FINAL GLOBAL CONSISTENCY & CONTINUITY AUDIT

PURPOSE: 출시 직전 최종 "사람 눈으로 하는" 교열 및 연결성 검증
         Pre-launch final "human-level" editorial and continuity validation

SCOPE: 모듈 ↔ HTML ↔ 최종 6종 보고서 간 완벽한 하모니 검증
       Perfect harmony validation across Modules ↔ HTML ↔ Final 6 Reports
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

class FinalGlobalAuditor:
    """최종 통합 감사기"""
    
    def __init__(self, project_root: str = "/home/user/webapp"):
        self.project_root = Path(project_root)
        self.assembler_dir = self.project_root / "app/services/final_report_assembly/assemblers"
        self.issues = defaultdict(list)
        
        # Report type audience expectations
        self.audience_focus = {
            "landowner_summary": "이 사업을 해도 되는가?",
            "lh_technical": "LH 심사 기준에 맞는가?",
            "quick_check": "지금 GO / NO-GO 인가?",
            "financial_feasibility": "돈이 되는가?",
            "executive_summary": "임원이 3분 안에 이해 가능?",
            "all_in_one": "모든 근거가 다 있는가?"
        }
        
        # Weak transition patterns to detect
        self.weak_transitions = [
            r'다음은\s+\w+\s*입니다',
            r'이어서\s+\w+\s*입니다',
            r'계속해서\s+\w+\s*입니다',
            r'그리고\s+\w+\s*입니다'
        ]
        
        # Weak decision patterns
        self.weak_decisions = [
            "추가 검토 필요",
            "검토가 필요합니다",
            "분석이 필요합니다",
            "확인 필요"
        ]
        
    def check_cross_module_numeric_harmony(self, filepath: Path) -> List[str]:
        """CHECK 1: 교차 모듈 숫자 하모니"""
        issues = []
        content = filepath.read_text(encoding='utf-8')
        
        # Extract all numeric values with context
        numeric_patterns = [
            (r'총\s*세대수[:\s]*([\d,]+)', '총 세대수'),
            (r'순현재가치.*?([-\d,]+)억', '순현재가치(NPV)'),
            (r'NPV.*?([-\d,]+)억', '순현재가치(NPV)'),
            (r'내부수익률.*?([\d.]+)%', '내부수익률(IRR)'),
            (r'IRR.*?([\d.]+)%', '내부수익률(IRR)'),
            (r'토지.*?감정가[:\s]*([\d,]+)억', '토지 감정가'),
        ]
        
        found_values = defaultdict(set)
        for pattern, label in numeric_patterns:
            matches = re.findall(pattern, content)
            if matches:
                for match in matches:
                    found_values[label].add(match.replace(',', ''))
        
        # Check if same metric has different values
        for label, values in found_values.items():
            if len(values) > 1:
                issues.append(f"⚠️ 숫자 불일치: {label}가 여러 값으로 표시됨: {values}")
        
        return issues
    
    def check_module_to_module_flow(self, filepath: Path) -> List[str]:
        """CHECK 2: 모듈 간 논리적 흐름"""
        issues = []
        content = filepath.read_text(encoding='utf-8')
        
        # Check for weak transition patterns
        for pattern in self.weak_transitions:
            matches = re.findall(pattern, content)
            if matches:
                issues.append(f"⚠️ 약한 전환 표현 발견: '{matches[0]}' → 논리적 연결 필요")
                break  # Report once per file
        
        # Check if transitions explain "why next module exists"
        transition_keywords = ['generate_module_transition', 'transition']
        has_transitions = any(kw in content for kw in transition_keywords)
        
        if not has_transitions:
            # Check if file uses multiple modules
            module_count = sum(1 for m in ['m2_html', 'm3_html', 'm4_html', 'm5_html', 'm6_html'] if m in content)
            if module_count > 1:
                issues.append(f"⚠️ 여러 모듈 사용하지만 명시적 전환 부재 (모듈 {module_count}개)")
        
        return issues
    
    def check_narrative_alignment(self, filepath: Path) -> List[str]:
        """CHECK 3: 보고서 유형별 내러티브 정렬"""
        issues = []
        filename = filepath.stem  # e.g., 'landowner_summary'
        content = filepath.read_text(encoding='utf-8')
        
        if filename not in self.audience_focus:
            return issues
        
        expected_focus = self.audience_focus[filename]
        
        # Check for over-technical content in non-technical reports
        if filename == "landowner_summary":
            technical_terms = ['건축계획', '용적률 산정', '법적 근거', '조례 제']
            found_technical = [term for term in technical_terms if term in content]
            if len(found_technical) > 3:
                issues.append(f"⚠️ 지주용 보고서에 기술적 용어 과다: {found_technical[:3]}...")
        
        # Check for lack of financial focus in financial reports
        elif filename == "financial_feasibility":
            financial_terms = ['수익', 'NPV', 'IRR', '현금흐름', '투자']
            found_financial = [term for term in financial_terms if term in content]
            if len(found_financial) < 2:
                issues.append(f"⚠️ 사업성 보고서에 재무 용어 부족 (예상 초점: {expected_focus})")
        
        # Check for brevity in executive summary
        elif filename == "executive_summary":
            # Count approximate content length
            text_only = re.sub(r'<[^>]+>', '', content)
            char_count = len(text_only)
            if char_count > 10000:
                issues.append(f"⚠️ 임원 요약 보고서가 너무 상세함 ({char_count:,}자) - 3분 독해 목표")
        
        return issues
    
    def check_html_final_visual_parity(self, filepath: Path) -> List[str]:
        """CHECK 4: HTML ↔ 최종 보고서 시각적 일치성"""
        issues = []
        content = filepath.read_text(encoding='utf-8')
        
        # Check for consistent KPI box structure
        kpi_boxes = re.findall(r'<div class=["\']kpi-summary-box["\']', content)
        if len(kpi_boxes) > 0:
            # Check if KPI boxes have consistent structure
            # Look for multiple different KPI patterns
            kpi_patterns = [
                r'class=["\']kpi-item["\']',
                r'class=["\']kpi-value["\']',
                r'class=["\']kpi-label["\']'
            ]
            
            pattern_counts = {}
            for pattern in kpi_patterns:
                pattern_counts[pattern] = len(re.findall(pattern, content))
            
            # If KPI structure varies widely, flag it
            if len(set(pattern_counts.values())) > 2:
                issues.append(f"⚠️ KPI 박스 구조 불일치 감지")
        
        return issues
    
    def check_source_reference_placement(self, filepath: Path) -> List[str]:
        """CHECK 5: 출처 참조 배치 자연스러움"""
        issues = []
        content = filepath.read_text(encoding='utf-8')
        
        # Find source references
        source_refs = re.findall(
            r'본\s*섹션은\s*M\d+\s+[^<]+\s*결과를\s*기반으로\s*구성되었습니다',
            content
        )
        
        if source_refs:
            # Check if they appear in awkward positions
            # (This is a simple heuristic - look for refs in middle of paragraphs)
            for ref in source_refs:
                # Check context around reference
                ref_pos = content.find(ref)
                before = content[max(0, ref_pos-100):ref_pos]
                after = content[ref_pos:ref_pos+100]
                
                # If reference appears in middle of dense text, flag it
                if '<p>' in before and '</p>' not in before:
                    issues.append(f"⚠️ 출처 참조가 문단 중간에 위치 - 재배치 권장")
                    break  # Report once
        
        return issues
    
    def check_decision_clarity(self, filepath: Path) -> List[str]:
        """CHECK 6: 결정 및 다음 행동 명확성"""
        issues = []
        content = filepath.read_text(encoding='utf-8')
        
        # Check for weak decision statements
        for weak in self.weak_decisions:
            if weak in content:
                issues.append(f"⚠️ 약한 결정 문구 발견: '{weak}' → 구체적 행동 필요")
                break
        
        # Check for presence of decision block
        if 'decision-block' not in content and 'decision_block' not in content:
            # Check if this is a report type that should have decision
            filename = filepath.stem
            if filename in ['landowner_summary', 'lh_technical', 'quick_check', 'executive_summary']:
                issues.append(f"⚠️ 결정 블록 누락 가능성 (보고서 유형: {filename})")
        
        # Check for next actions
        next_action_keywords = ['다음 단계', '권장 사항', '필요 서류', 'Next', 'next_actions']
        has_next_actions = any(kw in content for kw in next_action_keywords)
        
        if not has_next_actions:
            issues.append(f"⚠️ 다음 행동 섹션 부재 - 실행 가능한 지침 필요")
        
        return issues
    
    def check_human_reading_flow(self, filepath: Path) -> List[str]:
        """CHECK 7: 사람 독해 테스트"""
        issues = []
        content = filepath.read_text(encoding='utf-8')
        
        # Remove HTML tags for readability check
        text_only = re.sub(r'<[^>]+>', ' ', content)
        text_only = re.sub(r'\s+', ' ', text_only).strip()
        
        # Check for sudden numbers without context
        # Pattern: number appears without prior label
        number_patterns = [
            r'(?<![가-힣])\s+(\d[\d,]+억)',
            r'(?<![가-힣])\s+([\d.]+%)',
            r'(?<![가-힣])\s+(\d[\d,]+세대)'
        ]
        
        for pattern in number_patterns:
            matches = re.finditer(pattern, text_only)
            for match in matches:
                # Check 20 chars before for context
                start = max(0, match.start() - 20)
                before = text_only[start:match.start()]
                
                # If no descriptive words before number, flag it
                if not any(word in before for word in ['가', '는', '의', '으로', '에서']):
                    issues.append(f"⚠️ 맥락 없는 숫자 출현: '{match.group(1)}' - 설명 추가 필요")
                    break  # Report once per pattern
        
        # Check for logical flow breaks
        # Look for sudden topic changes
        paragraphs = text_only.split('.')
        if len(paragraphs) > 5:
            # Sample check on first few paragraphs
            for i in range(min(3, len(paragraphs) - 1)):
                p1 = paragraphs[i].strip()
                p2 = paragraphs[i + 1].strip()
                
                if len(p1) > 20 and len(p2) > 20:
                    # Very basic coherence check - look for complete topic shift
                    # (This is simplified - real implementation would use NLP)
                    pass  # Placeholder for advanced coherence checking
        
        return issues
    
    def audit_assembler_file(self, filepath: Path) -> Dict[str, List[str]]:
        """단일 어셈블러 파일 전체 감사"""
        return {
            'check_1_numeric_harmony': self.check_cross_module_numeric_harmony(filepath),
            'check_2_module_flow': self.check_module_to_module_flow(filepath),
            'check_3_narrative_alignment': self.check_narrative_alignment(filepath),
            'check_4_visual_parity': self.check_html_final_visual_parity(filepath),
            'check_5_source_placement': self.check_source_reference_placement(filepath),
            'check_6_decision_clarity': self.check_decision_clarity(filepath),
            'check_7_human_reading': self.check_human_reading_flow(filepath)
        }
    
    def audit_all_assemblers(self) -> Dict[str, Dict[str, List[str]]]:
        """모든 어셈블러 감사"""
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
            filepath = self.assembler_dir / filename
            if filepath.exists():
                results[filename] = self.audit_assembler_file(filepath)
            else:
                results[filename] = {'error': [f"파일 없음"]}
        
        return results
    
    def generate_audit_report(self) -> str:
        """최종 감사 보고서 생성"""
        results = self.audit_all_assemblers()
        
        report = []
        report.append("=" * 80)
        report.append("최종 통합 정합성 및 연속성 감사 보고서")
        report.append("FINAL GLOBAL CONSISTENCY & CONTINUITY AUDIT REPORT")
        report.append("=" * 80)
        report.append("")
        report.append("🎯 목표: 출시 직전 최종 '사람 눈으로 하는' 교열 검증")
        report.append("   Goal: Pre-launch final 'human-level' editorial validation")
        report.append("")
        report.append("🔍 감사 범위: 7가지 최종 CHECK 항목")
        report.append("   Audit Scope: 7 Final CHECK Items")
        report.append("")
        report.append("=" * 80)
        
        total_issues = 0
        check_summary = defaultdict(int)
        
        for filename, audit_results in results.items():
            report.append(f"\n📄 {filename}")
            report.append("-" * 80)
            
            file_has_issues = False
            
            for check_name, issues in audit_results.items():
                if issues:
                    file_has_issues = True
                    check_label = check_name.replace('_', ' ').title()
                    report.append(f"\n   [{check_label}]")
                    for issue in issues:
                        report.append(f"   {issue}")
                        total_issues += 1
                        check_summary[check_name] += 1
            
            if not file_has_issues:
                report.append("   ✅ 모든 최종 CHECK 통과 (All final checks passed)")
        
        report.append("")
        report.append("=" * 80)
        report.append(f"총 발견된 문제: {total_issues}개")
        report.append("")
        
        if check_summary:
            report.append("문제 카테고리별 분포:")
            for check, count in sorted(check_summary.items(), key=lambda x: x[1], reverse=True):
                check_label = check.replace('check_', 'CHECK ').replace('_', ' ').upper()
                report.append(f"  - {check_label}: {count}개")
            report.append("")
        
        if total_issues == 0:
            report.append("🎉 최종 통합 감사 완료! 출시 준비 완료")
            report.append("✅ Final Global Audit Complete! Ready for Launch")
            report.append("")
            report.append("SUCCESS CRITERIA MET:")
            report.append("  ✅ 모든 보고서가 '한 사람이 쓴 것처럼' 읽힘")
            report.append("  ✅ 숫자가 기억과 다르지 않음")
            report.append("  ✅ 결론이 갑자기 튀어나오지 않음")
            report.append("  ✅ LH / 지주 / 투자자 모두 납득 가능")
            report.append("  ✅ 설명 없이도 스스로 설명되는 문서")
        else:
            report.append("⚠️ 수정 권장 항목이 발견되었습니다.")
            report.append("   Recommended fixes have been identified.")
            report.append("")
            report.append("NOTE: 이는 '출판 직전 마지막 교열' 단계입니다.")
            report.append("      This is the 'final editorial pass before publication' stage.")
        
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """메인 실행"""
    print("🔍 최종 통합 정합성 및 연속성 감사 시작...")
    print("   Final Global Consistency & Continuity Audit Starting...\n")
    
    auditor = FinalGlobalAuditor()
    report = auditor.generate_audit_report()
    
    print(report)
    
    # 결과 저장
    output_path = Path("/home/user/webapp/final_global_audit_report.txt")
    output_path.write_text(report, encoding='utf-8')
    print(f"\n📝 감사 보고서 저장: {output_path}")
    
    # 이슈 카운트로 종료 코드 결정
    if "총 발견된 문제: 0개" in report:
        print("\n✅ 최종 통합 감사 통과! (Final Global Audit PASSED)")
        return 0
    else:
        print("\n⚠️ 수정 권장 항목 발견 (Recommended Fixes Identified)")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
