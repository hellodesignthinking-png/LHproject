#!/usr/bin/env python3
"""
Apply Data Integrity Fixes to Final Report Assemblers
======================================================

This script applies the following fixes:
1. P0: Module Completion Gate (base_assembler.py)
2. P0: QA KPI Validator (qa_validator.py)  
3. P1: Enhanced Extractor (all 6 assemblers)
4. P1: Complete KPI Binding (all 6 assemblers)

CRITICAL: This enforces ZERO N/A policy for core KPIs
"""

import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def apply_module_gate_to_base_assembler():
    """Add module completion validation to base_assembler.py"""
    file_path = Path("/home/user/webapp/app/services/final_report_assembly/base_assembler.py")
    
    logger.info(f"[P0] Patching {file_path.name} with module completion gate...")
    
    content = file_path.read_text()
    
    # Add Tuple import if not present
    if "from typing import" in content and "Tuple" not in content:
        content = re.sub(
            r'from typing import ([^\\n]+)',
            r'from typing import \1, Tuple',
            content
        )
    
    # Add validate_module_completeness method before assemble() method
    gate_method = '''
    def validate_module_completeness(self) -> Tuple[bool, List[str]]:
        """
        [P0 FIX] Validate that all required modules have complete data
        
        Returns:
            (is_complete, list_of_missing_items)
        """
        required = self.get_required_modules()
        missing_items = []
        
        for module_id in required:
            try:
                html = self.load_module_html(module_id)
                
                # Check for N/A indicators
                if any([
                    "N/A" in html,
                    "데이터 없음" in html,
                    "분석 미완료" in html,
                    "검증 필요" in html
                ]):
                    missing_items.append(f"{module_id}: 분석 미완료")
                
                # Check for minimum content
                if len(html.strip()) < 200:
                    missing_items.append(f"{module_id}: 내용 부족")
                
            except Exception as e:
                missing_items.append(f"{module_id}: 로드 실패 ({e})")
        
        is_complete = (len(missing_items) == 0)
        
        return is_complete, missing_items
    
'''
    
    # Insert before @abstractmethod\n    def assemble
    insertion_point = re.search(r'(@abstractmethod\s+def assemble)', content)
    
    if insertion_point:
        content = content[:insertion_point.start()] + gate_method + content[insertion_point.start():]
        file_path.write_text(content)
        logger.info(f"✅ Added validate_module_completeness() to base_assembler.py")
        return True
    else:
        logger.error(f"❌ Could not find insertion point in base_assembler.py")
        return False


def apply_enhanced_extractor_to_assembler(assembler_file: Path):
    """Replace _extract_module_data() with enhanced version"""
    logger.info(f"[P1] Patching {assembler_file.name} with enhanced extractor...")
    
    content = assembler_file.read_text()
    
    # Read enhanced extractor template
    extractor_template = Path("/home/user/webapp/data_integrity_patches/enhanced_extractor.py").read_text()
    
    # Find existing _extract_module_data method
    pattern = r'def _extract_module_data\(self, module_htmls: Dict\[str, str\]\) -> Dict:.*?(?=\n    def |\nclass |\Z)'
    
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Replace with enhanced version
        content = content[:match.start()] + extractor_template.strip() + "\n    " + content[match.end():]
        
        # Add bs4 import if not present
        if "from bs4 import BeautifulSoup" not in content:
            # Add after other imports
            import_section = re.search(r'(from typing import.*?\n)', content)
            if import_section:
                insertion_point = import_section.end()
                content = content[:insertion_point] + "from bs4 import BeautifulSoup\n" + content[insertion_point:]
        
        assembler_file.write_text(content)
        logger.info(f"✅ Enhanced extractor applied to {assembler_file.name}")
        return True
    else:
        logger.warning(f"⚠️  No _extract_module_data found in {assembler_file.name}")
        return False


def add_kpi_completeness_validation_to_assemblers(assembler_file: Path):
    """Add KPI validation check in assemble() method"""
    logger.info(f"[P1] Adding KPI validation to {assembler_file.name}...")
    
    content = assembler_file.read_text()
    
    # Find the generate_and_insert_qa_summary call
    pattern = r'(html_with_qa, qa_result = self\.generate_and_insert_qa_summary\([^)]+\))'
    
    match = re.search(pattern, content)
    
    if not match:
        logger.warning(f"⚠️  No QA summary insertion found in {assembler_file.name}")
        return False
    
    # Insert KPI validation RIGHT AFTER QA summary generation
    validation_code = '''
        
        # [P0 FIX] Validate KPI completeness - FAIL if any core KPI is N/A
        from app.services.final_report_assembly.qa_validator import FinalReportQAValidator
        
        kpi_valid, na_kpis = FinalReportQAValidator.validate_kpi_completeness(
            kpi_html=html_with_qa,
            report_type=self.report_type
        )
        
        if not kpi_valid:
            logger.error(
                f"[{self.report_type}] KPI validation FAILED: {', '.join(na_kpis)}"
            )
            qa_result["status"] = "FAIL"
            qa_result["errors"].append(f"Core KPIs contain N/A: {', '.join(na_kpis)}")
'''
    
    # Insert after qa_result assignment
    insertion_point = match.end()
    content = content[:insertion_point] + validation_code + content[insertion_point:]
    
    assembler_file.write_text(content)
    logger.info(f"✅ KPI validation added to {assembler_file.name}")
    return True


def add_kpi_validator_to_qa_validator():
    """Add validate_kpi_completeness static method to qa_validator.py"""
    file_path = Path("/home/user/webapp/app/services/final_report_assembly/qa_validator.py")
    
    logger.info(f"[P0] Adding KPI validator to {file_path.name}...")
    
    if not file_path.exists():
        logger.error(f"❌ {file_path} not found")
        return False
    
    content = file_path.read_text()
    
    # Read KPI validator template
    kpi_validator = Path("/home/user/webapp/data_integrity_patches/qa_kpi_validator.py").read_text()
    
    # Find FinalReportQAValidator class
    class_pattern = r'(class FinalReportQAValidator.*?)(\n    @staticmethod\s+def validate)'
    
    match = re.search(class_pattern, content, re.DOTALL)
    
    if match:
        # Insert before first @staticmethod
        insertion_point = match.end(1)
        content = content[:insertion_point] + "\n" + kpi_validator + "\n" + content[insertion_point:]
        
        file_path.write_text(content)
        logger.info(f"✅ KPI validator added to {file_path.name}")
        return True
    else:
        logger.warning(f"⚠️  Could not find insertion point in {file_path.name}")
        return False


def main():
    """Apply all patches"""
    print("=" * 80)
    print("APPLYING DATA INTEGRITY FIXES")
    print("=" * 80)
    print()
    
    success_count = 0
    total_count = 0
    
    # P0-1: Module completion gate
    print("📦 [P0-1] Module Completion Gate")
    print("-" * 80)
    total_count += 1
    if apply_module_gate_to_base_assembler():
        success_count += 1
    print()
    
    # P0-2: QA KPI Validator
    print("📦 [P0-2] QA KPI Validator")
    print("-" * 80)
    total_count += 1
    if add_kpi_validator_to_qa_validator():
        success_count += 1
    print()
    
    # P1: Enhanced extractors for all 6 assemblers
    print("📦 [P1] Enhanced Extractors (6 assemblers)")
    print("-" * 80)
    
    assemblers_dir = Path("/home/user/webapp/app/services/final_report_assembly/assemblers")
    
    assembler_files = [
        "landowner_summary.py",
        "lh_technical.py",
        "quick_check.py",
        "financial_feasibility.py",
        "all_in_one.py",
        "executive_summary.py"
    ]
    
    for assembler_name in assembler_files:
        assembler_path = assemblers_dir / assembler_name
        total_count += 1
        
        if assembler_path.exists():
            if apply_enhanced_extractor_to_assembler(assembler_path):
                success_count += 1
        else:
            logger.error(f"❌ {assembler_path} not found")
    
    print()
    
    # P1-2: Add KPI validation to assemblers
    print("📦 [P1-2] KPI Validation Integration (6 assemblers)")
    print("-" * 80)
    
    for assembler_name in assembler_files:
        assembler_path = assemblers_dir / assembler_name
        total_count += 1
        
        if assembler_path.exists():
            if add_kpi_completeness_validation_to_assemblers(assembler_path):
                success_count += 1
        else:
            logger.error(f"❌ {assembler_path} not found")
    
    print()
    print("=" * 80)
    print(f"✅ PATCH COMPLETE: {success_count}/{total_count} patches applied successfully")
    print("=" * 80)
    print()
    
    if success_count == total_count:
        print("🎉 ALL PATCHES APPLIED SUCCESSFULLY!")
        print()
        print("Next steps:")
        print("1. Run syntax check: cd /home/user/webapp && python -m py_compile app/services/final_report_assembly/*.py")
        print("2. Run tests: python data_integrity_patches/test_data_integrity.py")
        print("3. Generate sample report and verify KPIs")
        return 0
    else:
        print(f"⚠️  {total_count - success_count} patches failed")
        print("Review error messages above")
        return 1


if __name__ == "__main__":
    exit(main())
