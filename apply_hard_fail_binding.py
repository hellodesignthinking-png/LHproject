#!/usr/bin/env python3
"""
Apply Hard-Fail KPI Binding to All Assemblers
==============================================

This script integrates the Phase 3.10 enforcement layer into all 6 assemblers.

Changes:
1. Import enforce_kpi_binding from kpi_hard_fail_enforcement
2. Replace manual KPI dict creation with enforce_kpi_binding()
3. Add try/except for KPIBindingError and FinalReportGenerationError
4. Return FAIL result immediately if validation fails

Author: ZeroSite Backend Team
Date: 2025-12-22
"""

import re
from pathlib import Path

project_root = Path(__file__).parent

print("=" * 80)
print("🔒 APPLYING HARD-FAIL KPI BINDING TO ASSEMBLERS")
print("=" * 80)
print()

# ============================================================================
# PATCH CODE
# ============================================================================

# Import statement to add at top of each assembler
IMPORT_STATEMENT = """
# [Phase 3.10] Hard-Fail KPI Binding
from ..kpi_hard_fail_enforcement import enforce_kpi_binding, KPIBindingError, FinalReportGenerationError
"""

# Updated assemble() method segment (replace KPI generation)
UPDATED_KPI_GENERATION = '''        # [Phase 3.10] Extract module data
        modules_data = self._extract_module_data({"M2": m2_html, "M5": m5_html, "M6": m6_html})
        
        # [Phase 3.10] HARD-FAIL: Normalize → Bind → Validate
        try:
            bound_kpis = enforce_kpi_binding(self.report_type, modules_data)
            kpi_summary = self.generate_kpi_summary_box(bound_kpis, self.report_type)
        except (KPIBindingError, FinalReportGenerationError) as e:
            logger.error(f"[{self.report_type}] KPI binding FAILED: {e}")
            return {
                "html": self._generate_error_placeholder(str(e)),
                "qa_result": {
                    "status": "FAIL",
                    "errors": [str(e)],
                    "warnings": [],
                    "blocking": True,
                    "reason": "KPI binding hard-fail"
                }
            }
'''

# ============================================================================
# APPLY TO ASSEMBLERS
# ============================================================================

assembler_files = [
    "app/services/final_report_assembly/assemblers/landowner_summary.py",
    "app/services/final_report_assembly/assemblers/quick_check.py",
    "app/services/final_report_assembly/assemblers/financial_feasibility.py",
    "app/services/final_report_assembly/assemblers/lh_technical.py",
    "app/services/final_report_assembly/assemblers/all_in_one.py",
    "app/services/final_report_assembly/assemblers/executive_summary.py"
]

print("📝 Step 1: Add import statement to each assembler")
print()

for assembler_file in assembler_files:
    filepath = project_root / assembler_file
    
    if not filepath.exists():
        print(f"⚠️  SKIP: {assembler_file} (not found)")
        continue
    
    content = filepath.read_text(encoding='utf-8')
    
    # Check if already has import
    if "from ..kpi_hard_fail_enforcement import" in content:
        print(f"✓ SKIP: {Path(assembler_file).name} (already has import)")
        continue
    
    # Add import after existing imports
    # Find the last import line
    import_pattern = r'(from \.\.[^\n]+\n)'
    matches = list(re.finditer(import_pattern, content))
    
    if matches:
        last_import_pos = matches[-1].end()
        content = (
            content[:last_import_pos] +
            IMPORT_STATEMENT +
            content[last_import_pos:]
        )
        
        filepath.write_text(content, encoding='utf-8')
        print(f"✅ {Path(assembler_file).name}: Added import")
    else:
        print(f"⚠️  {Path(assembler_file).name}: Could not find import section")

print()
print("📝 Step 2: Update KPI generation logic")
print("(Manual review required - this is a template)")
print()

print("""
MANUAL UPDATE REQUIRED FOR EACH ASSEMBLER:
------------------------------------------

Find the section that looks like:

    # [FIX 2] Generate KPI Summary Box
    kpis = {
        "총 토지 감정가": modules_data.get("M2", {}).get("land_value"),
        "순현재가치 (NPV)": modules_data.get("M5", {}).get("npv"),
        "LH 심사 결과": modules_data.get("M6", {}).get("decision", "분석 미완료")
    }
    kpi_summary = self.generate_kpi_summary_box(kpis, self.report_type)

Replace with:

    # [Phase 3.10] Extract module data
    modules_data = self._extract_module_data({...module_htmls...})
    
    # [Phase 3.10] HARD-FAIL: Normalize → Bind → Validate
    try:
        bound_kpis = enforce_kpi_binding(self.report_type, modules_data)
        kpi_summary = self.generate_kpi_summary_box(bound_kpis, self.report_type)
    except (KPIBindingError, FinalReportGenerationError) as e:
        logger.error(f"[{self.report_type}] KPI binding FAILED: {e}")
        return {
            "html": self._generate_error_placeholder(str(e)),
            "qa_result": {
                "status": "FAIL",
                "errors": [str(e)],
                "warnings": [],
                "blocking": True,
                "reason": "KPI binding hard-fail"
            }
        }

This ensures:
✅ Canonical schema enforcement
✅ Mandatory KPI validation
✅ Hard-fail on missing data
✅ Clear error messages
""")

print()
print("=" * 80)
print("📊 SUMMARY")
print("=" * 80)
print("✅ Phase 3.10 enforcement layer created")
print("✅ Import statements added to assemblers")
print("⏳ Manual KPI generation replacement required")
print()
print("Next steps:")
print("1. Review each assembler's assemble() method")
print("2. Replace manual KPI dict with enforce_kpi_binding()")
print("3. Add try/except for hard-fail exceptions")
print("4. Test with incomplete module data to verify blocking")
print()
print("=" * 80)
