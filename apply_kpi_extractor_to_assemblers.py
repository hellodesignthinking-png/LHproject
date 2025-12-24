"""
Phase 3.10 Final Lock: Apply KPIExtractor to All Assemblers
Automated script to update all 6 assemblers with new KPI extraction pipeline
"""

from pathlib import Path
import re

ASSEMBLERS_DIR = Path("/home/user/webapp/app/services/final_report_assembly/assemblers")

NEW_IMPORTS = """from ..base_assembler import BaseFinalReportAssembler, get_report_brand_class
from ..narrative_generator import NarrativeGeneratorFactory
from ..report_type_configs import REPORT_TYPE_CONFIGS, get_mandatory_kpi

# [Phase 3.10 Final Lock] KPI Extractor
from ..kpi_extractor import KPIExtractor, validate_mandatory_kpi, log_kpi_pipeline, FinalReportAssemblyError"""

NEW_EXTRACT_METHOD = '''    def _extract_module_data(self, module_htmls: Dict[str, str], mandatory_kpi: Dict[str, List[str]]) -> Dict:
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
        
        return modules_data'''

def update_assembler_imports(file_path: Path) -> bool:
    """Update imports in assembler file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Pattern to find old imports
    old_import_patterns = [
        r'from \.\.kpi_hard_fail_enforcement import.*?\n',
        r'from app\.services\.final_report_assembly\.kpi_extraction_vlast import.*?\n',
    ]
    
    for pattern in old_import_patterns:
        content = re.sub(pattern, '', content)
    
    # Update base_assembler import to include get_mandatory_kpi
    content = re.sub(
        r'from \.\.report_type_configs import REPORT_TYPE_CONFIGS\n',
        'from ..report_type_configs import REPORT_TYPE_CONFIGS, get_mandatory_kpi\n',
        content
    )
    
    # Add new KPI extractor import after report_type_configs
    if '# [Phase 3.10 Final Lock] KPI Extractor' not in content:
        content = re.sub(
            r'(from \.\.report_type_configs import.*?\n)',
            r'\1\n# [Phase 3.10 Final Lock] KPI Extractor\n'
            r'from ..kpi_extractor import KPIExtractor, validate_mandatory_kpi, log_kpi_pipeline, FinalReportAssemblyError\n',
            content
        )
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def update_assembler_extract_call(file_path: Path) -> bool:
    """Update extract_module_data call in assemble() method"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Pattern to find old extraction + hard-fail block
    old_pattern = r'''        # Extract module data.*?
        modules_data = self\._extract_module_data\(\{.*?\}\)
        
        # \[Phase 3\.10\] HARD-FAIL:.*?
        try:
            bound_kpis = enforce_kpi_binding\(self\.report_type, modules_data\)
            kpi_summary = self\.generate_kpi_summary_box\(bound_kpis, self\.report_type\)
        except \(KPIBindingError, FinalReportGenerationError\) as e:
            logger\.error\(f"\[.*?\]"\)
            return \{
                "html": f"<html>.*?</html>",
                "qa_result": \{
                    .*?
                \}
            \}'''
    
    # This is complex, let's just check if the new pattern exists
    if '# [Phase 3.10 Final Lock] Extract KPI using new extractor' in content:
        return False  # Already updated
    
    # Try simpler replacement
    if 'modules_data = self._extract_module_data({' in content and 'enforce_kpi_binding' in content:
        print(f"  ⚠️  {file_path.name}: Manual update needed for extraction block")
    
    return False

def main():
    assembler_files = [
        "quick_check.py",
        "financial_feasibility.py",
        "lh_technical.py",
        "all_in_one.py",
        "executive_summary.py"
    ]
    
    print("=" * 80)
    print("Phase 3.10 Final Lock: Updating Assemblers")
    print("=" * 80)
    
    for filename in assembler_files:
        file_path = ASSEMBLERS_DIR / filename
        if not file_path.exists():
            print(f"\n❌ {filename}: Not found")
            continue
        
        print(f"\n📄 {filename}")
        
        # Update imports
        imports_updated = update_assembler_imports(file_path)
        if imports_updated:
            print("  ✅ Imports updated")
        else:
            print("  ℹ️  Imports already correct")
        
        # Check extraction block
        update_assembler_extract_call(file_path)
    
    print("\n" + "=" * 80)
    print("✅ Phase 3.10 Import Updates Complete")
    print("=" * 80)
    print("\nℹ️  Note: Extraction block updates require manual review")
    print("    Each assembler's assemble() method needs the new extraction pattern")

if __name__ == "__main__":
    main()
