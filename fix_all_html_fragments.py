#!/usr/bin/env python3
"""
Fix ALL module HTML renderers to return ONLY <section> fragments
NO full HTML documents, NO <!DOCTYPE>, NO <html><body> wrappers

This is the FINAL fix for vABSOLUTE-FINAL-17: HTML MODULE ROOT CONTRACT
"""

import re

def fix_html_renderer():
    """Remove ALL HTML document wrappers from module renderers"""
    
    file_path = "app/services/module_html_renderer.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Fixing HTML Fragment Contract...")
    print("=" * 60)
    
    # Pattern 1: Remove full HTML document headers (<!DOCTYPE html> through <body>)
    # M2 has this pattern (lines 227-237)
    pattern_full_header = re.compile(
        r'html = f"""[\s\r\n]*<!DOCTYPE html>.*?<body>[\s\r\n]*(<section data-module="M\d+")',
        re.DOTALL
    )
    
    def replace_full_header(match):
        section_tag = match.group(1)
        return f'html = f"""\n    {section_tag}'
    
    content_before = content
    content = pattern_full_header.sub(replace_full_header, content)
    
    if content != content_before:
        print("✅ Removed full HTML headers (<!DOCTYPE> + <head> + <body>)")
    
    # Pattern 2: Remove closing </body></html> tags
    # All modules (M2, M3, M4, M5, M6) have this
    pattern_closing_tags = re.compile(
        r'(</section>[\s\r\n]*</div>)[\s\r\n]*</body>[\s\r\n]*</html>[\s\r\n]*"""',
        re.DOTALL
    )
    
    def replace_closing_tags(match):
        section_close = match.group(1)
        return f'{section_close}\n    """'
    
    content_before = content
    content = pattern_closing_tags.sub(replace_closing_tags, content)
    
    if content != content_before:
        print("✅ Removed closing </body></html> tags")
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("=" * 60)
    print("✅ HTML Fragment Contract FIXED")
    print("   All M2-M6 renderers now return ONLY <section> fragments")
    
    # Verification
    print("\n🔍 Verification:")
    doctype_count = content.count('<!DOCTYPE html>')
    html_tag_count = content.count('<html lang="ko">')
    body_tag_count = content.count('<body>')
    
    print(f"   <!DOCTYPE html> occurrences: {doctype_count}")
    print(f"   <html lang='ko'> occurrences: {html_tag_count}")
    print(f"   <body> occurrences: {body_tag_count}")
    
    if doctype_count == 0 and html_tag_count == 0 and body_tag_count == 0:
        print("   ✅ SUCCESS: NO full HTML document wrappers remain")
        return True
    else:
        print("   ⚠️  WARNING: Some HTML wrappers may still exist")
        return False

if __name__ == "__main__":
    success = fix_html_renderer()
    exit(0 if success else 1)
