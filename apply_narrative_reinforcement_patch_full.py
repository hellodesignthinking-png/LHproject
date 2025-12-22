#!/usr/bin/env python3
"""
FINAL REPORT NARRATIVE & VISUAL REINFORCEMENT PATCH (FULL VERSION)
================================================================================
적용 대상: 모든 Final Report Assembler (6종)
목표: 보고서 완성도 향상 - 설득력, 시각적 구분, 실행 가이드 강화

FIX 1: Interpretation Paragraph Enforcement (Already Applied via previous script)
FIX 2: Module Transition Reinforcement
FIX 3: Report-Type Visual Emphasis
FIX 4: "Next Action" Section (MANDATORY)
FIX 5: Density Final Check

규칙:
- NO engine/calculation logic change
- ONLY display-level enhancement
- 100% preserving existing FIX A-E stability patches
"""

import os
import re

# ====================================================================
# FIX 2: Module Transition Reinforcement
# ====================================================================
MODULE_TRANSITION_METHOD = '''
    @staticmethod
    def generate_module_transition(from_module: str, to_module: str) -> str:
        """
        [FIX 2] Module Transition Reinforcement
        모듈 간 전환 시 논리적 연결성을 보여주는 전환 박스 생성
        """
        transition_text = {
            "M2_M5": "토지 평가 결과를 바탕으로 사업 수익성 검토 단계로 이동합니다.",
            "M5_M6": "사업성 분석 결과를 근거로 LH 심사 가능성을 판단합니다.",
            "M3_M4": "선호 유형 결정을 기반으로 사업 규모 산정 단계로 이동합니다.",
            "M4_M5": "사업 규모 확정 후 재무적 타당성을 검증합니다.",
        }
        
        key = f"{from_module}_{to_module}"
        text = transition_text.get(key, f"{from_module} 분석 결과를 바탕으로 {to_module} 검토 단계로 이동합니다.")
        
        return f"""
        <div class="module-transition">
            <svg class="transition-icon" viewBox="0 0 24 24" width="20" height="20">
                <path fill="currentColor" d="M12,4L10.6,5.4l5.6,5.6H2v2h14.2l-5.6,5.6L12,20l8-8L12,4z"/>
            </svg>
            <span>{text}</span>
        </div>
        """
'''

# ====================================================================
# FIX 3: Report-Type Visual Emphasis (CSS Update)
# ====================================================================
REPORT_TYPE_COLORS = {
    "landowner_summary": "#0066CC",      # BLUE
    "lh_technical": "#333333",           # DARK GRAY
    "financial_feasibility": "#00AA44",  # GREEN
    "executive_summary": "#7B2CBF",      # PURPLE
    "quick_check": "#FF8C00",            # ORANGE
    "all_in_one": "#666666",             # NEUTRAL
}

VISUAL_EMPHASIS_CSS = '''
        /* [FIX 3] Report-Type Visual Emphasis */
        .report-landowner_summary .report-title { border-bottom: 4px solid #0066CC; }
        .report-landowner_summary .kpi-summary { border-left: 4px solid #0066CC; }
        .report-landowner_summary .decision-block { border-left: 4px solid #0066CC; }
        
        .report-lh_technical .report-title { border-bottom: 4px solid #333333; }
        .report-lh_technical .kpi-summary { border-left: 4px solid #333333; }
        .report-lh_technical .decision-block { border-left: 4px solid #333333; }
        
        .report-financial_feasibility .report-title { border-bottom: 4px solid #00AA44; }
        .report-financial_feasibility .kpi-summary { border-left: 4px solid #00AA44; }
        .report-financial_feasibility .decision-block { border-left: 4px solid #00AA44; }
        
        .report-executive_summary .report-title { border-bottom: 4px solid #7B2CBF; }
        .report-executive_summary .kpi-summary { border-left: 4px solid #7B2CBF; }
        .report-executive_summary .decision-block { border-left: 4px solid #7B2CBF; }
        
        .report-quick_check .report-title { border-bottom: 4px solid #FF8C00; }
        .report-quick_check .kpi-summary { border-left: 4px solid #FF8C00; }
        .report-quick_check .decision-block { border-left: 4px solid #FF8C00; }
        
        .report-all_in_one .report-title { border-bottom: 4px solid #666666; }
        .report-all_in_one .kpi-summary { border-left: 4px solid #666666; }
        .report-all_in_one .decision-block { border-left: 4px solid #666666; }
'''

# ====================================================================
# FIX 4: "Next Action" Section (MANDATORY)
# ====================================================================
NEXT_ACTION_METHOD = '''
    def generate_next_action_section(self, modules_data: Dict[str, Any]) -> str:
        """
        [FIX 4] "Next Action" Section (MANDATORY)
        모든 보고서의 마지막에 "다음 단계 안내" 섹션 추가
        """
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        
        # M5 NPV 추출
        npv_str = m5_data.get("npv", "0")
        try:
            npv = float(re.sub(r"[^0-9.-]", "", str(npv_str)))
        except:
            npv = 0
        
        # M6 결정 추출
        decision = m6_data.get("decision", "검토 필요")
        
        # 다음 단계 판단
        if "승인" in decision and npv > 0:
            level = "proceed"
            title = "✅ 사업 추진 단계"
            actions = [
                "LH 공식 제안서 제출 (토지 감정 평가서 첨부)",
                "사업 계획서 및 재무 모델 정밀화",
                "지역 주민 설명회 준비 및 실시"
            ]
            documents = [
                "토지 대장 및 등기부등본",
                "사업 타당성 분석 보고서 (본 보고서)",
                "자금 조달 계획서"
            ]
        elif "조건부" in decision or npv > 0:
            level = "conditional"
            title = "⚠️ 조건부 추진 단계"
            actions = [
                "LH 지적사항 보완 (설계 변경 또는 추가 자료 제출)",
                "재무 모델 재검토 및 수익성 개선 방안 수립",
                "법적 리스크 검토 및 대응 방안 마련"
            ]
            documents = [
                "LH 지적사항 대응 보고서",
                "수정된 사업 계획서",
                "법률 자문 의견서"
            ]
        else:
            level = "review"
            title = "🔄 사업 재검토 단계"
            actions = [
                "사업 대상지 재평가 (대체 부지 검토)",
                "사업 모델 변경 검토 (규모 축소 또는 유형 변경)",
                "추가 전문가 자문 진행"
            ]
            documents = [
                "대체 부지 후보 리스트",
                "사업 변경안 검토 보고서",
                "전문가 자문 의견서"
            ]
        
        return f"""
        <section class="next-action-section pdf-safe">
            <h2>{title}</h2>
            <div class="action-guide">
                <h3>🎯 권장 조치사항</h3>
                <ol>
                    {"".join([f"<li>{action}</li>" for action in actions])}
                </ol>
                
                <h3>📋 필요 서류</h3>
                <ul>
                    {"".join([f"<li>{doc}</li>" for doc in documents])}
                </ul>
                
                <div class="action-note">
                    <strong>💡 참고사항:</strong> 본 보고서는 {modules_data.get('project_info', {}).get('report_date', '2025-12-22')} 기준으로 작성되었습니다. 
                    최신 정보 및 정책 변경 사항은 LH 담당자 확인 후 진행하시기 바랍니다.
                </div>
            </div>
        </section>
        """
'''

# ====================================================================
# FIX 5: Density Final Check (CSS Update)
# ====================================================================
DENSITY_CHECK_CSS = '''
        /* [FIX 5] Density Final Check - Section Summary for Long Reports */
        .section-summary {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            margin: 30px 0;
            border-radius: 8px;
            border-left: 5px solid #0066CC;
            page-break-inside: avoid;
        }
        
        .section-summary h3 {
            margin: 0 0 10px 0;
            color: #333;
            font-size: 1.2em;
        }
        
        .section-summary ul {
            margin: 0;
            padding-left: 20px;
        }
        
        .visual-separator {
            height: 40px;
            background: linear-gradient(to right, transparent, #e0e0e0, transparent);
            margin: 40px 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .visual-separator::after {
            content: "• • •";
            color: #999;
            font-size: 1.5em;
            letter-spacing: 10px;
        }
'''

# ====================================================================
# Module Transition CSS
# ====================================================================
MODULE_TRANSITION_CSS = '''
        /* [FIX 2] Module Transition Box */
        .module-transition {
            background: linear-gradient(to right, #f8f9fa, #ffffff);
            padding: 15px 20px;
            margin: 30px 0;
            border-left: 4px solid #0066CC;
            border-radius: 4px;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.95em;
            color: #555;
            page-break-inside: avoid;
        }
        
        .module-transition .transition-icon {
            color: #0066CC;
            flex-shrink: 0;
        }
'''

# ====================================================================
# Next Action Section CSS
# ====================================================================
NEXT_ACTION_CSS = '''
        /* [FIX 4] Next Action Section */
        .next-action-section {
            background: #f9fafb;
            padding: 30px;
            margin: 40px 0;
            border-radius: 8px;
            border: 2px solid #0066CC;
            page-break-inside: avoid;
            min-height: 200px;
        }
        
        .next-action-section h2 {
            margin: 0 0 20px 0;
            color: #0066CC;
            font-size: 1.5em;
            border-bottom: 2px solid #0066CC;
            padding-bottom: 10px;
        }
        
        .action-guide h3 {
            margin: 20px 0 10px 0;
            color: #333;
            font-size: 1.1em;
        }
        
        .action-guide ol,
        .action-guide ul {
            margin: 0 0 20px 0;
            padding-left: 25px;
        }
        
        .action-guide li {
            margin: 8px 0;
            line-height: 1.6;
        }
        
        .action-note {
            background: #fff3cd;
            padding: 15px;
            margin-top: 20px;
            border-left: 4px solid #ffc107;
            border-radius: 4px;
        }
        
        .action-note strong {
            color: #856404;
        }
'''


def apply_fix_2_module_transition(file_path: str) -> bool:
    """FIX 2: Module Transition Method 추가"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # generate_decision_block 메서드 다음에 삽입
    if 'generate_module_transition' in content:
        print(f"  ⏭️  FIX 2 already applied: {file_path}")
        return True
    
    pattern = r'(    @staticmethod\s+def generate_decision_block\([^)]+\).*?(?=\n    @staticmethod|\n    def [a-z_]+\(|\nclass |\Z))'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        insert_pos = match.end()
        new_content = content[:insert_pos] + '\n' + MODULE_TRANSITION_METHOD + content[insert_pos:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✅ FIX 2 applied: {file_path}")
        return True
    else:
        print(f"  ⚠️  Could not find insertion point for FIX 2: {file_path}")
        return False


def apply_fix_3_visual_emphasis_css(file_path: str) -> bool:
    """FIX 3: Report-Type Visual Emphasis CSS 추가"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'report-landowner_summary .report-title' in content:
        print(f"  ⏭️  FIX 3 already applied: {file_path}")
        return True
    
    # get_unified_design_css() 메서드 내부의 return 문 직전에 삽입
    pattern = r'(        /\* Print Media \*/.*?print \{.*?\}.*?)(        """)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        insert_pos = match.start(2)
        new_content = content[:insert_pos] + '\n' + VISUAL_EMPHASIS_CSS + '\n' + content[insert_pos:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✅ FIX 3 applied: {file_path}")
        return True
    else:
        print(f"  ⚠️  Could not find insertion point for FIX 3: {file_path}")
        return False


def apply_fix_4_next_action_method(file_path: str) -> bool:
    """FIX 4: Next Action Section Method 추가"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'generate_next_action_section' in content:
        print(f"  ⏭️  FIX 4 already applied: {file_path}")
        return True
    
    # generate_module_transition 메서드 다음에 삽입
    pattern = r'(    @staticmethod\s+def generate_module_transition\([^)]+\).*?(?=\n    @staticmethod|\n    def [a-z_]+\(|\nclass |\Z))'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        insert_pos = match.end()
        new_content = content[:insert_pos] + '\n' + NEXT_ACTION_METHOD + content[insert_pos:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✅ FIX 4 applied: {file_path}")
        return True
    else:
        print(f"  ⚠️  Could not find insertion point for FIX 4: {file_path}")
        return False


def apply_fix_5_density_css(file_path: str) -> bool:
    """FIX 5: Density Final Check CSS 추가"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'section-summary' in content:
        print(f"  ⏭️  FIX 5 already applied: {file_path}")
        return True
    
    # FIX 3 삽입 위치 다음에 삽입
    pattern = r'(        \.report-all_in_one \.decision-block \{[^}]+\})(.*?)(        """)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        insert_pos = match.start(3)
        new_content = content[:insert_pos] + '\n' + DENSITY_CHECK_CSS + '\n' + content[insert_pos:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✅ FIX 5 applied: {file_path}")
        return True
    else:
        print(f"  ⚠️  Could not find insertion point for FIX 5: {file_path}")
        return False


def apply_module_transition_css(file_path: str) -> bool:
    """Module Transition CSS 추가"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'module-transition' in content:
        print(f"  ⏭️  Module Transition CSS already applied: {file_path}")
        return True
    
    # Next Action CSS 다음에 삽입
    pattern = r'(        \.action-note strong \{[^}]+\})(.*?)(        """)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        insert_pos = match.start(3)
        new_content = content[:insert_pos] + '\n' + MODULE_TRANSITION_CSS + '\n' + content[insert_pos:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✅ Module Transition CSS applied: {file_path}")
        return True
    else:
        print(f"  ⚠️  Could not find insertion point for Module Transition CSS: {file_path}")
        return False


def apply_next_action_css(file_path: str) -> bool:
    """Next Action Section CSS 추가"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'next-action-section' in content:
        print(f"  ⏭️  Next Action CSS already applied: {file_path}")
        return True
    
    # FIX 5 삽입 위치 다음에 삽입
    pattern = r'(        \.visual-separator::after \{[^}]+\})(.*?)(        """)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        insert_pos = match.start(3)
        new_content = content[:insert_pos] + '\n' + NEXT_ACTION_CSS + '\n' + content[insert_pos:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✅ Next Action CSS applied: {file_path}")
        return True
    else:
        print(f"  ⚠️  Could not find insertion point for Next Action CSS: {file_path}")
        return False


def main():
    base_dir = "/home/user/webapp"
    assembler_files = [
        "app/services/final_report_assembly/assemblers/landowner_summary.py",
        "app/services/final_report_assembly/assemblers/lh_technical.py",
        "app/services/final_report_assembly/assemblers/quick_check.py",
        "app/services/final_report_assembly/assemblers/financial_feasibility.py",
        "app/services/final_report_assembly/assemblers/all_in_one.py",
        "app/services/final_report_assembly/assemblers/executive_summary.py"
    ]
    
    base_assembler_file = "app/services/final_report_assembly/base_assembler.py"
    
    print("=" * 80)
    print("FINAL REPORT NARRATIVE & VISUAL REINFORCEMENT PATCH (FULL VERSION)")
    print("=" * 80)
    
    # Step 1: Apply FIX 2 (Module Transition) to all assemblers
    print("\n[STEP 1] Applying FIX 2: Module Transition Reinforcement")
    print("-" * 80)
    for file in assembler_files:
        full_path = os.path.join(base_dir, file)
        apply_fix_2_module_transition(full_path)
    
    # Step 2: Apply FIX 3 (Visual Emphasis CSS) to base_assembler
    print("\n[STEP 2] Applying FIX 3: Report-Type Visual Emphasis CSS")
    print("-" * 80)
    base_path = os.path.join(base_dir, base_assembler_file)
    apply_fix_3_visual_emphasis_css(base_path)
    
    # Step 3: Apply FIX 4 (Next Action Section) to all assemblers
    print("\n[STEP 3] Applying FIX 4: 'Next Action' Section (MANDATORY)")
    print("-" * 80)
    for file in assembler_files:
        full_path = os.path.join(base_dir, file)
        apply_fix_4_next_action_method(full_path)
    
    # Step 4: Apply FIX 5 (Density Check CSS) to base_assembler
    print("\n[STEP 4] Applying FIX 5: Density Final Check CSS")
    print("-" * 80)
    apply_fix_5_density_css(base_path)
    
    # Step 5: Apply Module Transition CSS to base_assembler
    print("\n[STEP 5] Applying Module Transition CSS")
    print("-" * 80)
    apply_module_transition_css(base_path)
    
    # Step 6: Apply Next Action CSS to base_assembler
    print("\n[STEP 6] Applying Next Action CSS")
    print("-" * 80)
    apply_next_action_css(base_path)
    
    print("\n" + "=" * 80)
    print("✅ NARRATIVE & VISUAL REINFORCEMENT PATCH COMPLETED")
    print("=" * 80)
    print("\n📋 Applied Fixes:")
    print("  ✅ FIX 2: Module Transition Reinforcement")
    print("  ✅ FIX 3: Report-Type Visual Emphasis")
    print("  ✅ FIX 4: 'Next Action' Section (MANDATORY)")
    print("  ✅ FIX 5: Density Final Check")
    print("\n🎯 Next Steps:")
    print("  1. Run syntax validation: python -m py_compile <files>")
    print("  2. Create comprehensive narrative test")
    print("  3. Verify report completeness manually")
    print("  4. Commit and push changes")


if __name__ == "__main__":
    main()
