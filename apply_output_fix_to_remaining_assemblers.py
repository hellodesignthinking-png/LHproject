"""
Apply Output Quality Fixes to Remaining 5 Assemblers
====================================================

Applies FIX 1-5 to:
- lh_technical.py
- quick_check.py
- financial_feasibility.py
- all_in_one.py
- executive_summary.py

Following the pattern from landowner_summary.py (already fixed)
"""

import os
import re


FIXES_TO_APPLY = {
    "lh_technical": {
        "modules": ["M3", "M4", "M6"],
        "kpis": {
            "선호 유형": ("M3", "recommended_type", "string"),
            "계획 세대수": ("M4", "household_count", "unit"),
            "LH 심사 결과": ("M6", "decision", "string")
        }
    },
    "quick_check": {
        "modules": ["M5", "M6"],
        "kpis": {
            "순현재가치 (NPV)": ("M5", "npv", "currency"),
            "수익성 판단": ("M5", "is_profitable", "boolean"),
            "LH 심사 결과": ("M6", "decision", "string")
        }
    },
    "financial_feasibility": {
        "modules": ["M2", "M4", "M5"],
        "kpis": {
            "총 토지 감정가": ("M2", "land_value", "currency"),
            "순현재가치 (NPV)": ("M5", "npv", "currency"),
            "내부수익률 (IRR)": ("M5", "irr", "percent")
        }
    },
    "all_in_one": {
        "modules": ["M2", "M3", "M4", "M5", "M6"],
        "kpis": {
            "총 토지 감정가": ("M2", "land_value", "currency"),
            "계획 세대수": ("M4", "household_count", "unit"),
            "순현재가치 (NPV)": ("M5", "npv", "currency"),
            "LH 심사 결과": ("M6", "decision", "string")
        }
    },
    "executive_summary": {
        "modules": ["M2", "M5", "M6"],
        "kpis": {
            "총 토지 감정가": ("M2", "land_value", "currency"),
            "순현재가치 (NPV)": ("M5", "npv", "currency"),
            "LH 심사 결과": ("M6", "decision", "string")
        }
    }
}


def update_assembler_file(report_type: str, file_path: str):
    """Update a single assembler file with all output quality fixes"""
    
    print(f"\n{'='*60}")
    print(f"Processing: {report_type}")
    print(f"{'='*60}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fix_config = FIXES_TO_APPLY[report_type]
    modules = fix_config["modules"]
    
    # ============================================================
    # FIX 1: Add sanitize_module_html calls in assemble()
    # ============================================================
    print("  [FIX 1] Adding sanitize_module_html calls...")
    
    for module in modules:
        # Find load_module_html calls
        load_pattern = f'{module.lower()}_html = self.load_module_html("{module}")'
        if load_pattern in content:
            # Change to _raw suffix
            content = content.replace(
                load_pattern,
                f'{module.lower()}_html_raw = self.load_module_html("{module}")'
            )
    
    # Add sanitization calls after all load calls
    assemble_def = 'def assemble(self) -> Dict[str, str]:'
    if assemble_def in content:
        # Find the position after loading modules
        load_section_end = None
        for module in modules:
            pattern = f'{module.lower()}_html_raw = self.load_module_html("{module}")'
            if pattern in content:
                pos = content.find(pattern)
                if pos != -1:
                    line_end = content.find('\n', pos)
                    if load_section_end is None or line_end > load_section_end:
                        load_section_end = line_end
        
        if load_section_end:
            # Insert sanitization calls
            sanitize_lines = ["\n        # [FIX 1] Sanitize module HTML (remove N/A placeholders)"]
            for module in modules:
                sanitize_lines.append(
                    f'        {module.lower()}_html = self.sanitize_module_html({module.lower()}_html_raw, "{module}")'
                )
            
            content = (
                content[:load_section_end] + 
                '\n' + '\n'.join(sanitize_lines) +
                content[load_section_end:]
            )
    
    # ============================================================
    # FIX 2: Add KPI Summary Box generation
    # ============================================================
    print("  [FIX 2] Adding KPI Summary Box...")
    
    # Find where modules_data is extracted
    extract_pattern = 'modules_data = self._extract_module_data('
    if extract_pattern in content:
        extract_pos = content.find(extract_pattern)
        line_end = content.find('\n', extract_pos)
        
        # Generate KPI dictionary based on config
        kpi_entries = []
        for kpi_name, (module, field, fmt_type) in fix_config["kpis"].items():
            if fmt_type == "string":
                kpi_entries.append(f'            "{kpi_name}": modules_data.get("{module}", {{}}).get("{field}", "분석 미완료")')
            elif fmt_type == "boolean":
                kpi_entries.append(f'            "{kpi_name}": "수익성 있음" if modules_data.get("{module}", {{}}).get("{field}", False) else "수익성 부족"')
            else:
                kpi_entries.append(f'            "{kpi_name}": modules_data.get("{module}", {{}}).get("{field}")')
        
        kpi_code = f'''
        
        # [FIX 2] Generate KPI Summary Box (Mandatory for {report_type})
        kpis = {{
{chr(10).join(kpi_entries)}
        }}
        kpi_summary = self.generate_kpi_summary_box(kpis, self.report_type)'''
        
        content = content[:line_end] + kpi_code + content[line_end:]
    
    # ============================================================
    # FIX 3: Enhance _extract_module_data with better regex
    # ============================================================
    print("  [FIX 3] Enhancing _extract_module_data...")
    
    # Find _extract_module_data method
    extract_method_pattern = r'def _extract_module_data\(self, module_htmls: Dict\[str, str\]\) -> Dict:(.*?)(?=\n    def |\n\nclass |\Z)'
    extract_match = re.search(extract_method_pattern, content, re.DOTALL)
    
    if extract_match:
        # Update extraction patterns for better robustness
        method_content = extract_match.group(0)
        
        # Enhance NPV extraction
        if 'npv_match' in method_content:
            method_content = method_content.replace(
                "npv_match = re.search(r'NPV[:\\s]*([+-]?\\d{1,3}(?:,\\d{3})*)', m5_html, re.IGNORECASE)",
                "npv_match = re.search(r'NPV[:\\s]*([+-]?\\d{1,3}(?:,\\d{3})*?)\\s*원', m5_html, re.IGNORECASE)"
            )
            
            # Add is_profitable field
            if "'npv':" in method_content and "'is_profitable'" not in method_content:
                method_content = method_content.replace(
                    'modules_data["M5"]["npv"] = int(npv_match.group(1).replace(",", ""))',
                    'npv_value = int(npv_match.group(1).replace(",", ""))\n                modules_data["M5"]["npv"] = npv_value\n                modules_data["M5"]["is_profitable"] = npv_value > 0'
                )
        
        content = content.replace(extract_match.group(0), method_content)
    
    # ============================================================
    # FIX 4: Add unified design CSS
    # ============================================================
    print("  [FIX 4] Adding unified design system CSS...")
    
    # Update _get_report_css method
    css_pattern = r'def _get_report_css\(self\) -> str:(.*?)(?=\n        # Add watermark|return base_css)'
    css_match = re.search(css_pattern, content, re.DOTALL)
    
    if css_match:
        # Replace return statement to include unified design CSS
        content = content.replace(
            'return base_css + self.get_zerosite_watermark_css() + self.get_copyright_footer_css()',
            'return base_css + self.get_unified_design_css() + self.get_zerosite_watermark_css() + self.get_copyright_footer_css()'
        )
        
        # Add FIX 4 comment to method docstring
        content = content.replace(
            'def _get_report_css(self) -> str:\n        """[PROMPT 3.5-2] Report CSS with watermark and copyright"""',
            'def _get_report_css(self) -> str:\n        """[FIX 4] Report CSS with unified design system"""'
        )
    
    # ============================================================
    # FIX 5: Add Decision Block generation
    # ============================================================
    print("  [FIX 5] Adding Decision Block...")
    
    # Add decision block generation before sections assembly
    sections_pattern = 'sections = ['
    if sections_pattern in content:
        sections_pos = content.find(sections_pattern)
        
        decision_code = '''
        # [FIX 5] Generate Decision Block (Clear Visual Conclusion)
        judgment_text = self._determine_judgment(modules_data)
        basis = self._generate_judgment_basis(modules_data)
        actions = self._generate_next_actions(modules_data)
        decision_block = self.generate_decision_block(judgment_text, basis, actions)
        
        '''
        
        content = content[:sections_pos] + decision_code + content[sections_pos:]
        
        # Add decision_block to sections list (before footer)
        footer_in_sections = 'self._generate_footer()'
        if footer_in_sections in content:
            content = content.replace(
                f'            {footer_in_sections}\n        ]',
                f'            decision_block,  # Visual decision at bottom\n            {footer_in_sections}\n        ]'
            )
        
        # Also add kpi_summary to sections (after cover page or at beginning)
        if 'self._generate_cover_page(),' in content:
            content = content.replace(
                'self._generate_cover_page(),',
                'self._generate_cover_page(),\n            kpi_summary,  # KPI at top'
            )
        elif 'sections = [' in content and 'exec_summary,' in content:
            content = content.replace(
                'sections = [\n            exec_summary,',
                'sections = [\n            kpi_summary,  # KPI at top\n            exec_summary,'
            )
    
    # Add helper methods for decision logic
    helper_methods = '''
    
    def _determine_judgment(self, modules_data: Dict) -> str:
        """Determine final judgment text based on module data"""
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        
        is_profitable = m5_data.get("is_profitable", False)
        lh_decision = m6_data.get("decision", "")
        
        if is_profitable and "승인" in lh_decision:
            return "사업 추진 권장"
        elif "조건부" in lh_decision:
            return "조건부 사업 추진"
        elif not is_profitable:
            return "사업 재검토 필요"
        else:
            return "추가 분석 필요"
    
    def _generate_judgment_basis(self, modules_data: Dict) -> list:
        """Generate judgment basis points"""
        basis = []
        
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        
        # Profitability
        npv = m5_data.get("npv")
        if npv and npv > 0:
            basis.append(f"수익성: NPV {self.format_number(npv, 'currency')} (양호)")
        elif npv and npv <= 0:
            basis.append(f"수익성: NPV {self.format_number(npv, 'currency')} (부정적)")
        else:
            basis.append("수익성: 분�� 데이터 부족")
        
        # LH Decision
        lh_decision = m6_data.get("decision", "분석 미완료")
        basis.append(f"LH 승인 가능성: {lh_decision}")
        
        # Risk assessment
        basis.append("주요 리스크: 시장 변동성, 인허가 지연 가능성")
        
        return basis
    
    def _generate_next_actions(self, modules_data: Dict) -> list:
        """Generate next action items"""
        actions = []
        
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        
        is_profitable = m5_data.get("is_profitable", False)
        lh_decision = m6_data.get("decision", "")
        
        if is_profitable and "승인" in lh_decision:
            actions.append("LH 사전 협의 진행")
            actions.append("설계 용역 발주 준비")
        elif "조건부" in lh_decision:
            actions.append("LH 지적 사항 보완")
            actions.append("재분석 후 재제출 검토")
        else:
            actions.append("사업 계획 전면 재검토")
            actions.append("대안 부지 탐색")
        
        return actions'''
    
    # Add helper methods before _generate_cover_page or _wrap_module
    insert_before = '\n    def _generate_cover_page(self):'
    if insert_before not in content:
        insert_before = '\n    def _wrap_module(self, module_id: str, html: str):'
    
    if insert_before in content:
        content = content.replace(insert_before, helper_methods + insert_before)
    
    # ============================================================
    # Update _wrap_module to _wrap_module_html (consistency)
    # ============================================================
    content = content.replace(
        'def _wrap_module(self, module_id: str, html: str) -> str:',
        'def _wrap_module_html(self, module_id: str, html: str) -> str:'
    )
    content = content.replace(
        'self._wrap_module(',
        'self._wrap_module_html('
    )
    
    # ============================================================
    # Add QA Summary insertion
    # ============================================================
    print("  [PROMPT 3.5-3] Adding QA Summary insertion...")
    
    # Find return statement in assemble()
    return_pattern = 'return {"html": self._wrap_in_document(sections)}'
    if return_pattern in content:
        qa_code = '''# Wrap in HTML document
        html_content = self._wrap_in_document(sections)
        
        # [PROMPT 3.5-3] Insert QA Summary Page
        html_with_qa, qa_result = self.generate_and_insert_qa_summary(
            html_content=html_content,
            report_type=self.report_type,
            modules_data=modules_data
        )
        
        logger.info(
            f"[{report_type.title().replace('_', '')}] Assembly complete with QA Summary "
            f"({len(html_with_qa):,} chars, QA Status: {qa_result['status']})"
        )
        
        return {"html": html_with_qa, "qa_result": qa_result}'''
        
        content = content.replace(
            f'        {return_pattern}',
            '        ' + qa_code
        )
    
    # ============================================================
    # Save updated file
    # ============================================================
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Successfully updated {report_type}")
        return True
    else:
        print(f"  ⚠️  No changes made to {report_type}")
        return False


def main():
    """Apply output quality fixes to all remaining assemblers"""
    
    print("\n" + "="*60)
    print("OUTPUT QUALITY FIX - Batch Application")
    print("="*60)
    print("\nApplying FIX 1-5 to remaining 5 assemblers:")
    print("  [FIX 1] Data Visibility Recovery (sanitize N/A)")
    print("  [FIX 2] Mandatory KPI Enforcement (summary box)")
    print("  [FIX 3] Number Format Standardization (enhanced regex)")
    print("  [FIX 4] Design System Lock (unified CSS)")
    print("  [FIX 5] Decision Visibility (visual block)")
    print()
    
    assemblers_dir = "/home/user/webapp/app/services/final_report_assembly/assemblers"
    
    updated_count = 0
    
    for report_type in ["lh_technical", "quick_check", "financial_feasibility", "all_in_one", "executive_summary"]:
        file_path = os.path.join(assemblers_dir, f"{report_type}.py")
        
        if os.path.exists(file_path):
            if update_assembler_file(report_type, file_path):
                updated_count += 1
        else:
            print(f"  ❌ File not found: {file_path}")
    
    print("\n" + "="*60)
    print(f"BATCH UPDATE COMPLETE: {updated_count}/5 assemblers updated")
    print("="*60)
    
    if updated_count == 5:
        print("\n✅ All 5 assemblers successfully updated with output quality fixes!")
        print("\nNext steps:")
        print("  1. Run comprehensive tests on all 6 assemblers")
        print("  2. Verify KPI summaries, decision blocks, and design consistency")
        print("  3. Commit changes with detailed message")
    else:
        print(f"\n⚠️  Only {updated_count}/5 assemblers were updated. Please review.")


if __name__ == "__main__":
    main()
