#!/usr/bin/env python3
"""
Add _extract_module_data method to all assemblers
"""

extraction_method = '''
    def _extract_module_data(self, module_htmls: Dict[str, str], mandatory_kpi: Dict[str, List[str]]) -> Dict:
        """
        [Phase 3.10 Final Lock] Extract module data using KPIExtractor
        
        Args:
            module_htmls: Dict of module_id -> HTML string
            mandatory_kpi: Dict of module_id -> required KPI keys
            
        Returns:
            Dict of module_id -> extracted KPI data
        """
        modules_data = {}
        
        for module_id, html in module_htmls.items():
            if not html or html.strip() == "":
                logger.warning(f"[{module_id}] Empty HTML")
                modules_data[module_id] = {"status": "empty", "_complete": False}
                continue
            
            # Get required keys for this module
            required_keys = mandatory_kpi.get(module_id, [])
            
            try:
                # Extract KPI using new extractor (SINGLE ENTRY POINT)
                kpi_data = KPIExtractor.extract_module_kpi(html, module_id, required_keys)
                modules_data[module_id] = kpi_data
                
                # Log pipeline for audit trail
                log_kpi_pipeline(self.report_type, self.context_id, module_id, kpi_data)
                
            except FinalReportAssemblyError as e:
                logger.error(f"[{module_id}] KPI extraction failed: {e}")
                modules_data[module_id] = {
                    "status": "extraction_failed",
                    "_complete": False,
                    "error": str(e)
                }
        
        return modules_data
'''

files = [
    "app/services/final_report_assembly/assemblers/quick_check.py",
    "app/services/final_report_assembly/assemblers/financial_feasibility.py",
    "app/services/final_report_assembly/assemblers/lh_technical.py",
    "app/services/final_report_assembly/assemblers/all_in_one.py",
    "app/services/final_report_assembly/assemblers/executive_summary.py",
]

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if method already exists
    if "def _extract_module_data" in content:
        print(f"⚠️  {filepath.split('/')[-1]} - method exists, skipping")
        continue
    
    # Find the assemble method end and insert before it
    # Look for the class definition end marker (next method or end of class)
    import re
    
    # Find last method before end of class
    # Insert before the last non-private method or at end of class
    match = re.search(r'(\n\nclass \w+.*?def assemble\(.*?\n.*?return \{[^}]*\}[^}]*\})', content, re.DOTALL)
    
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + "\n" + extraction_method + content[insert_pos:]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {filepath.split('/')[-1]}")
    else:
        print(f"❌ {filepath.split('/')[-1]} - could not find insertion point")

print("\n✅ Extraction method added to all assemblers")
