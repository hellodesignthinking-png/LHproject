#!/usr/bin/env python3
"""
[CRITICAL FIX] Add BUILD/DATA SIGNATURE as searchable text in PDF

Problem: Signatures exist only as visual watermarks, not searchable text
Solution: Add signature block as TEXT in body + footer

This ensures PDF binary search can find these strings.
"""

import re
import sys

ASSEMBLERS = [
    "app/services/final_report_assembly/assemblers/quick_check.py",
    "app/services/final_report_assembly/assemblers/landowner_summary.py",
    "app/services/final_report_assembly/assemblers/financial_feasibility.py",
    "app/services/final_report_assembly/assemblers/lh_technical.py",
    "app/services/final_report_assembly/assemblers/all_in_one.py",
    "app/services/final_report_assembly/assemblers/executive_summary.py",
]

def add_searchable_signature_block(file_path: str) -> bool:
    """
    Add searchable text signature block to _generate_footer()
    
    Returns:
        True if modification was made, False if already exists
    """
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has searchable signature
    if 'SEARCHABLE_BUILD_SIGNATURE' in content:
        print(f"  ⏭️  Already has searchable signature: {file_path}")
        return False
    
    # Find _generate_footer() method
    footer_pattern = r'(    def _generate_footer\(self\) -> str:.*?return self\.get_zerosite_copyright_footer\(.*?\))'
    
    match = re.search(footer_pattern, content, re.DOTALL)
    if not match:
        print(f"  ⚠️  Could not find _generate_footer(): {file_path}")
        return False
    
    old_footer = match.group(0)
    
    # Create new footer with searchable signature
    new_footer = '''    def _generate_footer(self) -> str:
        """
        [PROMPT 3.5-2] ZEROSITE Copyright Footer
        [vABSOLUTE-FINAL-12] Add SEARCHABLE signature text for binary verification
        """
        from datetime import datetime
        
        # Searchable text block (for PDF binary search)
        searchable_signature = f"""
        <div style="
            font-size: 10px;
            color: #b00000;
            border: 1px solid #b00000;
            padding: 6px;
            margin: 12px 0;
            background: #fff8f8;
            font-family: monospace;
        ">
            <div style="font-weight: bold; margin-bottom: 4px;">
                📊 Report Verification Signature (보고서 검증 시그니처)
            </div>
            <div>
                BUILD_SIGNATURE: vABSOLUTE-FINAL-12<br/>
                BUILD_TS: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z<br/>
                REPORT: {self.report_type}<br/>
                CONTEXT: {self.context_id}<br/>
                DATA_SIGNATURE: {{data_signature}}
            </div>
            <div style="font-size: 8px; color: #666; margin-top: 4px;">
                ※ This signature is embedded as searchable text for verification purposes.
            </div>
        </div>
        """
        
        copyright = self.get_zerosite_copyright_footer(
            report_type=self.report_type,
            context_id=self.context_id
        )
        
        return searchable_signature + copyright'''
    
    # Replace old footer with new one
    content = content.replace(old_footer, new_footer)
    
    # Backup
    with open(file_path + '.backup_sig', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Write new content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ Added searchable signature: {file_path}")
    return True

def update_assemblers_to_pass_data_signature():
    """
    Update assemble() methods to pass data_signature to footer
    """
    print("\n🔧 Step 2: Update assemble() to pass data_signature...")
    
    for file_path in ASSEMBLERS:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if already updated
            if 'data_signature_panel' in content and 'data_signature =' in content:
                # Find where footer is called
                if 'self._generate_footer()' in content:
                    # Replace footer call to pass data_signature
                    content = content.replace(
                        'self._generate_footer()',
                        'self._generate_footer().replace("{data_signature}", data_signature)'
                    )
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"  ✅ Updated footer call: {file_path}")
                else:
                    print(f"  ⚠️  No footer call found: {file_path}")
            else:
                print(f"  ⏭️  No data_signature variable: {file_path}")
        
        except Exception as e:
            print(f"  ❌ Error: {file_path} - {e}")

if __name__ == "__main__":
    print("="*60)
    print("🎯 Adding SEARCHABLE BUILD/DATA SIGNATURE to all assemblers")
    print("="*60)
    
    print("\n🔧 Step 1: Modify _generate_footer() in all assemblers...")
    
    modified_count = 0
    for file_path in ASSEMBLERS:
        try:
            if add_searchable_signature_block(file_path):
                modified_count += 1
        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
    
    print(f"\n✅ Modified {modified_count}/{len(ASSEMBLERS)} assemblers")
    
    # Step 2: Update assemble() calls
    update_assemblers_to_pass_data_signature()
    
    print("\n" + "="*60)
    print("✅ COMPLETE: Searchable signatures added!")
    print("="*60)
    print("\n📍 What changed:")
    print("  1. _generate_footer() now includes searchable text block")
    print("  2. BUILD_SIGNATURE: vABSOLUTE-FINAL-12 (as plain text)")
    print("  3. DATA_SIGNATURE: {data_signature} (will be filled)")
    print("  4. PDF binary search will now find these strings")
    print("\n🔍 Verify with:")
    print("  strings report.pdf | grep 'BUILD_SIGNATURE'")
    print("  strings report.pdf | grep 'DATA_SIGNATURE'")
