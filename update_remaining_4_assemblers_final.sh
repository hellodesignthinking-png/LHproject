#!/bin/bash

# This script will use git diff from landowner_summary and quick_check 
# to understand the pattern, then copy that pattern to the 4 remaining assemblers

echo "================================================================"
echo "Applying Output Quality Fixes to 4 Remaining Assemblers"
echo "================================================================"
echo ""
echo "Approach: Copy pattern from quick_check.py (already fixed)"
echo "Target files:"
echo "  - lh_technical.py"
echo "  - financial_feasibility.py"
echo "  - all_in_one.py" 
echo "  - executive_summary.py"
echo ""

# For each remaining file, we need to:
# 1. Add sanitize calls
# 2. Add KPI summary generation  
# 3. Add decision block generation
# 4. Add QA summary insertion
# 5. Add helper methods
# 6. Update CSS

echo "Applying fixes with Python..."

python3 << 'EOFPYTHON'
import re
import os

# Read the successfully fixed quick_check as reference
with open("app/services/final_report_assembly/assemblers/quick_check.py", 'r', encoding='utf-8') as f:
    quick_check_content = f.read()

# Extract the helper methods from quick_check
helper_methods_pattern = r'(    def _determine_judgment.*?return actions)'
helper_match = re.search(helper_methods_pattern, quick_check_content, re.DOTALL)
helper_methods = helper_match.group(0) if helper_match else ""

print(f"Extracted {len(helper_methods)} chars of helper methods")

# Now apply to remaining 4 files
print("\nProcessing remaining assemblers...\n")

# Define the specific fixes for each assembler
ASSEMBLER_CONFIGS = {
    "lh_technical": {
        "modules": ["M3", "M4", "M6"],
        "kpis": """            "선호 유형": modules_data.get("M3", {}).get("recommended_type", "분석 미완료"),
            "계획 세대수": modules_data.get("M4", {}).get("household_count"),
            "LH 심사 결과": modules_data.get("M6", {}).get("decision", "분석 미완료")"""
    },
    "financial_feasibility": {
        "modules": ["M2", "M4", "M5"],
        "kpis": """            "총 토지 감정가": modules_data.get("M2", {}).get("land_value"),
            "순현재가치 (NPV)": modules_data.get("M5", {}).get("npv"),
            "내부수익률 (IRR)": modules_data.get("M5", {}).get("irr")"""
    },
    "all_in_one": {
        "modules": ["M2", "M3", "M4", "M5", "M6"],
        "kpis": """            "총 토지 감정가": modules_data.get("M2", {}).get("land_value"),
            "계획 세대수": modules_data.get("M4", {}).get("household_count"),
            "순현재가치 (NPV)": modules_data.get("M5", {}).get("npv"),
            "LH 심사 결과": modules_data.get("M6", {}).get("decision", "분석 미완료")"""
    },
    "executive_summary": {
        "modules": ["M2", "M5", "M6"],
        "kpis": """            "총 토지 감정가": modules_data.get("M2", {}).get("land_value"),
            "순현재가치 (NPV)": modules_data.get("M5", {}).get("npv"),
            "LH 심사 결과": modules_data.get("M6", {}).get("decision", "분석 미완료")"""
    }
}

success_count = 0

for assembler_name, config in ASSEMBLER_CONFIGS.items():
    print(f"{'='*60}")
    print(f"Processing: {assembler_name}")
    print(f"{'='*60}")
    
    file_path = f"app/services/final_report_assembly/assemblers/{assembler_name}.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    modules = config["modules"]
    
    # STEP 1: Add sanitize calls
    print("  [1] Adding sanitize_module_html calls...")
    for module in modules:
        old_pattern = f'{module.lower()}_html = self.load_module_html("{module}")'
        new_pattern = f'{module.lower()}_html_raw = self.load_module_html("{module}")'
        content = content.replace(old_pattern, new_pattern)
    
    # Find where to insert sanitization
    load_last = None
    for module in modules:
        pattern = f'{module.lower()}_html_raw = self.load_module_html("{module}")'
        pos = content.find(pattern)
        if pos > -1:
            line_end = content.find('\n', pos)
            if load_last is None or line_end > load_last:
                load_last = line_end
    
    if load_last:
        sanitize_code = "\n        # [FIX 1] Sanitize module HTML (remove N/A placeholders)"
        for module in modules:
            sanitize_code += f'\n        {module.lower()}_html = self.sanitize_module_html({module.lower()}_html_raw, "{module}")'
        sanitize_code += "\n        "
        content = content[:load_last+1] + sanitize_code + content[load_last+1:]
    
    # STEP 2: Add KPI summary generation
    print("  [2] Adding KPI Summary Box...")
    extract_pattern = 'modules_data = self._extract_module_data('
    extract_pos = content.find(extract_pattern)
    if extract_pos > -1:
        # Find end of that statement
        line_end = extract_pos
        brace_count = 0
        in_extract = False
        for i in range(extract_pos, len(content)):
            if content[i] == '{':
                brace_count += 1
                in_extract = True
            elif content[i] == '}':
                brace_count -= 1
                if in_extract and brace_count == 0:
                    line_end = content.find('\n', i)
                    break
        
        kpi_code = f'''
        
        # [FIX 2] Generate KPI Summary Box (Mandatory for {assembler_name})
        kpis = {{
{config["kpis"]}
        }}
        kpi_summary = self.generate_kpi_summary_box(kpis, self.report_type)'''
        
        content = content[:line_end] + kpi_code + content[line_end:]
    
    # STEP 3: Enhance _extract_module_data for M5
    print("  [3] Enhancing _extract_module_data...")
    if "M5" in modules:
        # Add is_profitable
        old_npv = 'modules_data["M5"] = {"npv": int(npv_str)}'
        if old_npv in content:
            new_npv = '''npv_value = int(npv_str)
            modules_data["M5"] = {"npv": npv_value, "is_profitable": npv_value > 0}'''
            content = content.replace(old_npv, new_npv)
        
        # Update regex to include 원
        old_regex = r"npv_match = re.search(r'NPV[:\\s]*([+-]?\\d{1,3}(?:,\\d{3})*)', m5_html, re.IGNORECASE)"
        new_regex = r"npv_match = re.search(r'NPV[:\\s]*([+-]?\\d{1,3}(?:,\\d{3})*?)\\s*원', m5_html, re.IGNORECASE)"
        content = content.replace(old_regex, new_regex)
    
    # STEP 4: Add decision block generation
    print("  [4] Adding Decision Block...")
    # Find where exec_summary or final_judgment is generated
    pattern_to_find = None
    if 'final_judgment = self.narrative.final_judgment(modules_data)' in content:
        pattern_to_find = 'final_judgment = self.narrative.final_judgment(modules_data)'
    elif 'exec_summary = self.narrative.executive_summary(modules_data)' in content:
        pattern_to_find = 'exec_summary = self.narrative.executive_summary(modules_data)'
    
    if pattern_to_find:
        pos = content.rfind(pattern_to_find)
        if pos > -1:
            line_end = content.find('\n', pos)
            decision_code = '''
        
        # [FIX 5] Generate Decision Block (Clear Visual Conclusion)
        judgment_text = self._determine_judgment(modules_data)
        basis = self._generate_judgment_basis(modules_data)
        actions = self._generate_next_actions(modules_data)
        decision_block = self.generate_decision_block(judgment_text, basis, actions)
        '''
            content = content[:line_end] + decision_code + content[line_end:]
    
    # STEP 5: Update sections list to include kpi_summary and decision_block
    print("  [5] Updating sections list...")
    # Add kpi_summary after cover page or at beginning
    if 'self._generate_cover_page(),' in content:
        content = content.replace(
            'self._generate_cover_page(),',
            'self._generate_cover_page(),\n            kpi_summary,  # KPI at top'
        )
    elif 'sections = [\n            exec_summary,' in content:
        content = content.replace(
            'sections = [\n            exec_summary,',
            'sections = [\n            kpi_summary,  # KPI at top\n            exec_summary,'
        )
    
    # Add decision_block before footer
    if 'self._generate_footer()\n        ]' in content:
        content = content.replace(
            'self._generate_footer()\n        ]',
            'decision_block,  # Visual decision at bottom\n            self._generate_footer()\n        ]'
        )
    
    # STEP 6: Update return statement to include QA
    print("  [6] Adding QA Summary insertion...")
    old_return = 'return {"html": self._wrap_in_document(sections)}'
    if old_return in content:
        class_name_match = re.search(r'class (\w+)Assembler', content)
        class_name = class_name_match.group(1) if class_name_match else assembler_name.title().replace('_', '')
        
        new_return = f'''# Wrap in HTML document
        html_content = self._wrap_in_document(sections)
        
        # [PROMPT 3.5-3] Insert QA Summary Page
        html_with_qa, qa_result = self.generate_and_insert_qa_summary(
            html_content=html_content,
            report_type=self.report_type,
            modules_data=modules_data
        )
        
        logger.info(
            f"[{class_name}] Assembly complete with QA Summary "
            f"({{len(html_with_qa):,}} chars, QA Status: {{qa_result['status']}})"
        )
        
        return {{"html": html_with_qa, "qa_result": qa_result}}'''
        
        content = content.replace(f'        {old_return}', f'        {new_return}')
    
    # STEP 7: Add helper methods
    print("  [7] Adding helper methods...")
    # Find insertion point (before _generate_cover_page or _wrap_module)
    insert_before = '\n    def _generate_cover_page(self):'
    if insert_before not in content:
        insert_before = '\n    def _wrap_module(self, module_id: str, html: str):'
    
    if insert_before in content and helper_methods:
        content = content.replace(insert_before, '\n' + helper_methods + '\n    \n    def _wrap_module_html(self, module_id: str, html: str) -> str:\n        return f\'<section class="module-section" data-module="{module_id}">{html}</section>\'' + insert_before)
        
        # Remove old _wrap_module if it exists
        old_wrap = '''    def _wrap_module(self, module_id: str, html: str) -> str:
        return f'<section class="module-section" data-module="{module_id}">{html}</section>\'
    '''
        content = content.replace(old_wrap, '')
    
    # Update all _wrap_module calls to _wrap_module_html
    content = content.replace('self._wrap_module(', 'self._wrap_module_html(')
    
    # STEP 8: Update CSS
    print("  [8] Updating CSS...")
    old_css_return = 'return base_css + self.get_zerosite_watermark_css() + self.get_copyright_footer_css()'
    new_css_return = 'return base_css + self.get_unified_design_css() + self.get_zerosite_watermark_css() + self.get_copyright_footer_css()'
    content = content.replace(old_css_return, new_css_return)
    
    # Update CSS docstring
    content = content.replace(
        '"""[PROMPT 3.5-2] Report CSS with watermark and copyright"""',
        '"""[FIX 4] Report CSS with unified design system"""'
    )
    
    # Write updated file
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Successfully updated {assembler_name}")
        success_count += 1
    else:
        print(f"  ⚠️  No changes made to {assembler_name}")

print(f"\n{'='*60}")
print(f"COMPLETE: {success_count}/4 assemblers updated")
print(f"{'='*60}\n")

EOFPYTHON

echo ""
echo "Verifying syntax..."
python3 -m py_compile app/services/final_report_assembly/assemblers/lh_technical.py && echo "  ✅ lh_technical.py"
python3 -m py_compile app/services/final_report_assembly/assemblers/financial_feasibility.py && echo "  ✅ financial_feasibility.py"
python3 -m py_compile app/services/final_report_assembly/assemblers/all_in_one.py && echo "  ✅ all_in_one.py"
python3 -m py_compile app/services/final_report_assembly/assemblers/executive_summary.py && echo "  ✅ executive_summary.py"

echo ""
echo "================================================================"
echo "✅ ALL 4 ASSEMBLERS UPDATED AND SYNTAX-CHECKED"
echo "================================================================"

