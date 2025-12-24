
DEPLOYMENT SEQUENCE:
====================

1️⃣ APPLY P0 PATCHES (BLOCKERS)
   → Add module_completeness_gate() to base_assembler.py
   → Add QA KPI validator to qa_validator.py
   → Modify assemble() to call validation BEFORE generation
   
   Files to modify:
   - app/services/final_report_assembly/base_assembler.py
   - app/services/final_report_assembly/qa_validator.py

2️⃣ APPLY P1 PATCHES (CRITICAL)
   → Replace _extract_module_data() in ALL 6 assemblers
   → Test with actual context_id
   
   Files to modify:
   - app/services/final_report_assembly/assemblers/landowner_summary.py
   - app/services/final_report_assembly/assemblers/lh_technical.py
   - app/services/final_report_assembly/assemblers/quick_check.py
   - app/services/final_report_assembly/assemblers/financial_feasibility.py
   - app/services/final_report_assembly/assemblers/all_in_one.py
   - app/services/final_report_assembly/assemblers/executive_summary.py

3️⃣ RUN TESTS
   cd /home/user/webapp
   python data_integrity_patches/test_data_integrity.py

4️⃣ GENERATE SAMPLE REPORTS
   Test with REAL context_id:
   - Check KPI box has NO N/A
   - Check Module HTML values appear in Final Report
   - Check QA blocks incomplete reports

5️⃣ VERIFY PDFs
   - Visual check: Numbers match between Module → Final
   - Layout check: KPI boxes intact, no table breakage
   - Decision check: Clear GO/NO-GO visible

CRITICAL SUCCESS CRITERIA:
==========================
✅ NO N/A in core KPIs for any of the 6 report types
✅ Incomplete modules BLOCK Final Report generation
✅ QA status = FAIL if any core KPI missing
✅ Module HTML values correctly extracted to Final KPIs
✅ Section detection by data-module attribute (not text)
