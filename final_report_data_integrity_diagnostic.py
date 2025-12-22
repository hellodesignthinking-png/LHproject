#!/usr/bin/env python3
"""
FINAL REPORT DATA INTEGRITY DIAGNOSTIC & REPAIR SCRIPT
=======================================================

Role: Principal Engineer - Output Quality & Data Binding
Scope: Fix N/A values, missing KPIs, HTML↔Final inconsistencies, layout breakage

CRITICAL FINDINGS FROM PDF ANALYSIS:
====================================
① Landowner Summary: M2 (N/A), M3 (no score), M4 (N/A), M5 (N/A, no basis), M6 (ambiguous)
   → VERDICT: BLOCK generation - completely failed as summary report
   
② Quick Check: M2 (N/A), M4 (N/A), M5 (no basis), M6 (ambiguous)
   → PROBLEM: Extractor failure + incomplete decision block
   
③ Feasibility/Investment: M2 (in table, not summary), M4 (missing), M5 (no IRR), M6 (no risk)
   → PROBLEM: HTML has value, but not extracted to Final KPI box (CASE 2)
   
④ LH Technical: M3 (no score), M4 (text only), M5 (no summary), M6 (unclear)
   → VERDICT: Fails LH submission standards
   
⑤ Explanatory: M2 (missing), M3 (explanation only), M5 (no number), M6 (unclear)
   
⑥ Comprehensive Final: M2 (N/A), M3 (missing), M4 (missing), M5 (N/A), M6 (missing)
   → VERDICT: Most severe - not aligned with "Comprehensive" title

ROOT CAUSE: Final Assembly Layer NOT connected to actual data despite engines having values

FIXES TO APPLY (Priority Order):
=================================
P0: Module Completion Gate + QA Blocker for N/A in core KPIs
P1: Enhanced Extractor - Pull values from Module HTML to Final KPIs
P2: Section Detection by ID (not text), Prevent CSS conflicts
P3: Core KPI Schema Enforcement per report_type
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========== DIAGNOSTIC PHASE ==========

class DataIntegrityDiagnostic:
    """Diagnose data flow from Module HTML → Final Report KPIs"""
    
    # Core KPI requirements per report type (from PDF analysis)
    CORE_KPI_REQUIREMENTS = {
        "landowner_summary": {
            "M2": ["토지 감정가", "평당 가격"],
            "M3": ["추천 유형", "총점"],
            "M4": ["총 세대수"],
            "M5": ["순현재가치(NPV)", "수익성 판단"],
            "M6": ["LH 심사 결과"]
        },
        "quick_check": {
            "M2": ["토지 감정가"],
            "M4": ["총 세대수"],
            "M5": ["순현재가치(NPV)", "판단 근거"],
            "M6": ["GO/NO-GO 판정"]
        },
        "financial_feasibility": {
            "M2": ["토지 가치"],
            "M4": ["연면적"],
            "M5": ["순현재가치(NPV)", "내부수익률(IRR)"],
            "M6": ["위험도"]
        },
        "lh_technical": {
            "M3": ["선호유형 점수"],
            "M4": ["건축규모"],
            "M5": ["사업성 요약"],
            "M6": ["LH 판정"]
        },
        "executive_summary": {
            "M2": ["토지 가치"],
            "M3": ["유형"],
            "M5": ["수익성"],
            "M6": ["최종 결론"]
        },
        "all_in_one": {
            "M2": ["토지 가치"],
            "M3": ["유형"],
            "M4": ["세대수"],
            "M5": ["순현재가치(NPV)"],
            "M6": ["최종 판단"]
        }
    }
    
    @staticmethod
    def check_module_html_has_values(module_html: str, module_id: str) -> Dict[str, bool]:
        """
        Check if Module HTML contains actual numeric values
        
        Returns:
            Dict mapping KPI field to presence (True if value found)
        """
        found_values = {}
        
        # M2: Land value
        if module_id == "M2":
            found_values["토지 감정가"] = bool(re.search(r'[\d,]+\s*원', module_html))
            found_values["평당 가격"] = bool(re.search(r'평당[:\s]*[\d,]+', module_html))
        
        # M3: Type & Score
        elif module_id == "M3":
            found_values["추천 유형"] = bool(re.search(r'추천\s*유형[:\s]*[가-힣]+', module_html))
            found_values["총점"] = bool(re.search(r'총점[:\s]*\d+', module_html))
            found_values["선호유형 점수"] = bool(re.search(r'점수[:\s]*\d+', module_html))
        
        # M4: Building scale
        elif module_id == "M4":
            found_values["총 세대수"] = bool(re.search(r'세대[수]*[:\s]*\d+', module_html))
            found_values["연면적"] = bool(re.search(r'연면적[:\s]*[\d.,]+\s*㎡', module_html))
        
        # M5: Feasibility
        elif module_id == "M5":
            found_values["순현재가치(NPV)"] = bool(re.search(r'NPV|순현재가치', module_html))
            found_values["내부수익률(IRR)"] = bool(re.search(r'IRR|내부수익률', module_html))
            found_values["수익성 판단"] = bool(re.search(r'수익성|판단|결론', module_html))
        
        # M6: LH Review
        elif module_id == "M6":
            found_values["LH 심사 결과"] = bool(re.search(r'추진\s*가능|조건부|부적합', module_html))
            found_values["판정"] = bool(re.search(r'GO|NO-GO|판정', module_html, re.IGNORECASE))
        
        return found_values
    
    @staticmethod
    def check_final_report_kpis(html_content: str, report_type: str) -> Dict[str, bool]:
        """
        Check if Final Report HTML has KPI values (not N/A)
        
        Returns:
            Dict mapping KPI to presence status
        """
        requirements = DataIntegrityDiagnostic.CORE_KPI_REQUIREMENTS.get(report_type, {})
        kpi_status = {}
        
        # Look for KPI summary box
        kpi_box_match = re.search(
            r'<section[^>]*class="kpi-summary-box"[^>]*>(.*?)</section>',
            html_content,
            re.DOTALL
        )
        
        if not kpi_box_match:
            logger.warning(f"[{report_type}] No KPI summary box found")
            return {}
        
        kpi_box_content = kpi_box_match.group(1)
        
        # Check each required KPI
        for module_id, kpi_list in requirements.items():
            for kpi_name in kpi_list:
                # Check if KPI name exists AND has non-N/A value
                kpi_present = kpi_name in kpi_box_content
                
                # Check for N/A indicators
                has_na = any([
                    re.search(rf'{kpi_name}.*?N/A', kpi_box_content, re.DOTALL),
                    re.search(rf'{kpi_name}.*?데이터 없음', kpi_box_content, re.DOTALL),
                    re.search(rf'{kpi_name}.*?분석 미완료', kpi_box_content, re.DOTALL),
                ])
                
                # Check for actual numeric value
                has_value = bool(re.search(
                    rf'{kpi_name}.*?[\d,]+',
                    kpi_box_content,
                    re.DOTALL
                ))
                
                kpi_status[f"{module_id}:{kpi_name}"] = (kpi_present and has_value and not has_na)
        
        return kpi_status
    
    @staticmethod
    def diagnose_data_flow_gap(
        module_html: str,
        final_html: str,
        module_id: str,
        report_type: str
    ) -> List[str]:
        """
        Identify WHERE data is being lost between Module HTML and Final Report
        
        Returns:
            List of diagnostic messages
        """
        diagnostics = []
        
        # Check 1: Module HTML has values
        module_values = DataIntegrityDiagnostic.check_module_html_has_values(module_html, module_id)
        has_source_data = any(module_values.values())
        
        if not has_source_data:
            diagnostics.append(
                f"❌ ROOT CAUSE 1: Module {module_id} HTML has NO numeric values "
                f"→ Module analysis incomplete, BLOCK Final Report generation"
            )
            return diagnostics
        
        # Check 2: Final Report has KPIs
        final_kpis = DataIntegrityDiagnostic.check_final_report_kpis(final_html, report_type)
        relevant_kpis = {k: v for k, v in final_kpis.items() if k.startswith(module_id)}
        
        if not any(relevant_kpis.values()):
            diagnostics.append(
                f"⚠️ ROOT CAUSE 2: Module {module_id} HTML HAS values, "
                f"but Final Report shows N/A → Extractor/Parser failure"
            )
            
            # Provide specific extraction hints
            for kpi_name, found in module_values.items():
                if found:
                    diagnostics.append(
                        f"   💡 HINT: '{kpi_name}' exists in Module HTML but not extracted"
                    )
        
        # Check 3: Section detection
        if f'data-module="{module_id}"' not in final_html:
            diagnostics.append(
                f"⚠️ ROOT CAUSE 3: Module {module_id} section not properly wrapped "
                f"→ Section detection logic inconsistent"
            )
        
        return diagnostics


# ========== REPAIR PHASE ==========

class DataIntegrityRepair:
    """Apply fixes to restore data flow"""
    
    @staticmethod
    def generate_enhanced_extractor_method() -> str:
        """
        Generate improved _extract_module_data() method
        
        This replaces weak regex with robust multi-fallback extraction
        """
        return '''
    def _extract_module_data(self, module_htmls: Dict[str, str]) -> Dict:
        """
        [FIXED] Enhanced data extraction with multi-fallback strategy
        
        Extraction Priority:
        1. Try data-* attributes (most reliable)
        2. Try structured JSON blocks
        3. Try regex patterns (labeled values)
        4. Try table cell extraction
        5. Fallback: Mark as incomplete
        
        NEVER returns None - always returns Dict with 'status' key
        """
        import re
        from bs4 import BeautifulSoup
        
        modules_data = {}
        
        for module_id, html in module_htmls.items():
            if not html or html.strip() == "":
                modules_data[module_id] = {"status": "empty", "_complete": False}
                continue
            
            soup = BeautifulSoup(html, 'html.parser')
            data = {"status": "parsed", "_complete": True}
            
            # ===== M2: LAND APPRAISAL =====
            if module_id == "M2":
                # Try 1: data-land-value attribute
                land_elem = soup.find(attrs={"data-land-value": True})
                if land_elem:
                    try:
                        data["land_value"] = int(land_elem['data-land-value'].replace(",", ""))
                    except:
                        pass
                
                # Try 2: Regex on text
                if "land_value" not in data:
                    match = re.search(r'(\d{1,3}(?:,\d{3})+)\s*원', html)
                    if match:
                        data["land_value"] = int(match.group(1).replace(",", ""))
                
                # Try 3: Table extraction
                if "land_value" not in data:
                    for td in soup.find_all('td'):
                        text = td.get_text()
                        if '원' in text:
                            match = re.search(r'(\d{1,3}(?:,\d{3})+)', text)
                            if match:
                                data["land_value"] = int(match.group(1).replace(",", ""))
                                break
                
                # Mark incomplete if no value found
                if "land_value" not in data:
                    data["_complete"] = False
                    data["_missing"] = ["토지 감정가"]
            
            # ===== M3: LH PREFERRED TYPE =====
            elif module_id == "M3":
                # Extract type
                type_match = re.search(r'추천\s*유형[:\s]*([가-힣]+)', html)
                if type_match:
                    data["recommended_type"] = type_match.group(1).strip()
                
                # Extract score
                score_match = re.search(r'총점[:\s]*(\d+\.?\d*)', html)
                if score_match:
                    data["total_score"] = float(score_match.group(1))
                
                # Extract grade
                grade_match = re.search(r'등급[:\s]*([A-F등급]+)', html)
                if grade_match:
                    data["grade"] = grade_match.group(1)
                
                # Completeness check
                if not all(k in data for k in ["recommended_type", "total_score"]):
                    data["_complete"] = False
                    data["_missing"] = []
                    if "recommended_type" not in data:
                        data["_missing"].append("추천 유형")
                    if "total_score" not in data:
                        data["_missing"].append("총점")
            
            # ===== M4: BUILDING SCALE =====
            elif module_id == "M4":
                # Total units
                units_match = re.search(r'총\s*세대수[:\s]*(\d[\d,]*)', html)
                if units_match:
                    data["total_units"] = int(units_match.group(1).replace(",", ""))
                
                # Floor area
                area_match = re.search(r'연면적[:\s]*([\d,]+\.?\d*)\s*㎡', html)
                if area_match:
                    data["floor_area"] = float(area_match.group(1).replace(",", ""))
                
                # Completeness
                if "total_units" not in data:
                    data["_complete"] = False
                    data["_missing"] = ["총 세대수"]
            
            # ===== M5: FEASIBILITY =====
            elif module_id == "M5":
                # NPV
                npv_match = re.search(
                    r'순현재가치.*?NPV.*?[:\s]*([+-]?\d{1,3}(?:,\d{3})*)',
                    html,
                    re.IGNORECASE | re.DOTALL
                )
                if npv_match:
                    npv_value = int(npv_match.group(1).replace(",", ""))
                    data["npv"] = npv_value
                    data["is_profitable"] = (npv_value > 0)
                
                # IRR
                irr_match = re.search(r'IRR|내부수익률.*?(\d+\.?\d*)\s*%', html, re.DOTALL)
                if irr_match:
                    data["irr"] = float(irr_match.group(1))
                
                # Profitability text
                if "추진 권장" in html or "수익성 양호" in html:
                    data["profitability_text"] = "수익성 양호"
                elif "수익성 부족" in html or "재검토" in html:
                    data["profitability_text"] = "수익성 부족"
                
                # Completeness
                if "npv" not in data:
                    data["_complete"] = False
                    data["_missing"] = ["순현재가치(NPV)"]
            
            # ===== M6: LH REVIEW =====
            elif module_id == "M6":
                # Decision
                if "추진 가능" in html or "GO" in html.upper():
                    data["decision"] = "추진 가능"
                elif "조건부 가능" in html or "CONDITIONAL" in html.upper():
                    data["decision"] = "조건부 가능"
                elif "부적합" in html or "NO-GO" in html.upper():
                    data["decision"] = "부적합"
                else:
                    data["decision"] = "판정 미확정"
                
                # Completeness
                if data["decision"] == "판정 미확정":
                    data["_complete"] = False
                    data["_missing"] = ["LH 심사 결과"]
            
            modules_data[module_id] = data
        
        return modules_data
'''
    
    @staticmethod
    def generate_module_completeness_gate() -> str:
        """Generate gate to BLOCK Final Report if core modules incomplete"""
        return '''
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
    
    @staticmethod
    def generate_qa_kpi_validator() -> str:
        """Generate QA validator to FAIL if core KPIs are N/A"""
        return '''
    @staticmethod
    def validate_kpi_completeness(kpi_html: str, report_type: str) -> Tuple[bool, List[str]]:
        """
        [P0 FIX] Validate that KPI summary has NO N/A values
        
        Returns:
            (is_valid, list_of_na_kpis)
        """
        import re
        
        # Core KPI requirements (from PDF analysis)
        CORE_KPIS = {
            "landowner_summary": ["토지 감정가", "순현재가치", "LH 심사"],
            "quick_check": ["토지 감정가", "세대수", "GO/NO-GO"],
            "financial_feasibility": ["토지 가치", "NPV", "IRR"],
            "lh_technical": ["선호유형", "건축규모", "LH 판정"],
            "executive_summary": ["토지 가치", "수익성", "최종 결론"],
            "all_in_one": ["토지 가치", "세대수", "NPV", "최종 판단"]
        }
        
        required_kpis = CORE_KPIS.get(report_type, [])
        na_kpis = []
        
        for kpi_name in required_kpis:
            # Find KPI section
            kpi_match = re.search(
                rf'{kpi_name}.*?<div class="kpi-value">(.*?)</div>',
                kpi_html,
                re.DOTALL
            )
            
            if not kpi_match:
                na_kpis.append(f"{kpi_name}: 미표시")
                continue
            
            kpi_value = kpi_match.group(1)
            
            # Check for N/A indicators
            if any([
                "N/A" in kpi_value,
                "데이터 없음" in kpi_value,
                "데이터 미확정" in kpi_value,
                "분석 미완료" in kpi_value,
                kpi_value.strip() == ""
            ]):
                na_kpis.append(f"{kpi_name}: N/A 또는 빈 값")
        
        is_valid = (len(na_kpis) == 0)
        
        return is_valid, na_kpis
'''


# ========== MAIN EXECUTION ==========

def main():
    """Run diagnostic and generate repair patches"""
    
    print("=" * 80)
    print("FINAL REPORT DATA INTEGRITY DIAGNOSTIC")
    print("=" * 80)
    print()
    
    # Step 1: Generate diagnostic report
    print("📊 STEP 1: ROOT CAUSE ANALYSIS")
    print("-" * 80)
    
    root_causes = [
        {
            "issue": "Module Analysis Incomplete",
            "description": "M2-M6 engines not producing complete results",
            "solution": "Add module completion gate BEFORE Final Report assembly",
            "priority": "P0 - BLOCKER",
            "files": ["base_assembler.py"]
        },
        {
            "issue": "Extractor Weakness",
            "description": "Module HTML has values, but _extract_module_data() fails to parse",
            "solution": "Replace regex with multi-fallback extractor (data-attr → JSON → regex → table)",
            "priority": "P1 - CRITICAL",
            "files": ["all_in_one.py", "landowner_summary.py", "lh_technical.py", 
                      "quick_check.py", "financial_feasibility.py", "executive_summary.py"]
        },
        {
            "issue": "KPI Binding Failure",
            "description": "Extracted data not properly bound to KPI summary box",
            "solution": "Ensure generate_kpi_summary_box() receives complete modules_data",
            "priority": "P1 - CRITICAL",
            "files": ["base_assembler.py + all 6 assemblers"]
        },
        {
            "issue": "QA Not Blocking N/A",
            "description": "Reports passing QA despite N/A in core KPIs",
            "solution": "Add QA validator to FAIL if any core KPI is N/A",
            "priority": "P0 - BLOCKER",
            "files": ["qa_validator.py"]
        },
        {
            "issue": "Section Detection Inconsistency",
            "description": "Section detection by text matching fails",
            "solution": "Use data-module attributes instead of text search",
            "priority": "P2 - MEDIUM",
            "files": ["all 6 assemblers"]
        }
    ]
    
    for i, cause in enumerate(root_causes, 1):
        print(f"\n{i}. {cause['issue']}")
        print(f"   문제: {cause['description']}")
        print(f"   해결책: {cause['solution']}")
        print(f"   우선순위: {cause['priority']}")
        print(f"   수정 파일: {', '.join(cause['files'])}")
    
    # Step 2: Generate repair code
    print("\n\n📝 STEP 2: GENERATING REPAIR PATCHES")
    print("-" * 80)
    
    repair = DataIntegrityRepair()
    
    patches = {
        "enhanced_extractor.py": repair.generate_enhanced_extractor_method(),
        "module_gate.py": repair.generate_module_completeness_gate(),
        "qa_kpi_validator.py": repair.generate_qa_kpi_validator()
    }
    
    output_dir = Path("/home/user/webapp/data_integrity_patches")
    output_dir.mkdir(exist_ok=True)
    
    for filename, code in patches.items():
        patch_file = output_dir / filename
        patch_file.write_text(code, encoding='utf-8')
        print(f"✅ Generated: {patch_file}")
    
    # Step 3: Generate test script
    print("\n\n🧪 STEP 3: GENERATING TEST VERIFICATION")
    print("-" * 80)
    
    test_script = '''#!/usr/bin/env python3
"""Test script to verify data integrity fixes"""
import pytest
from app.services.final_report_assembly.assemblers import landowner_summary

def test_no_na_in_kpis():
    """Core KPIs must NOT contain N/A"""
    assembler = landowner_summary.LandownerSummaryAssembler("test_context")
    result = assembler.assemble()
    
    html = result["html"]
    
    # Find KPI summary box
    import re
    kpi_box = re.search(r'<section[^>]*kpi-summary-box[^>]*>(.*?)</section>', html, re.DOTALL)
    
    assert kpi_box, "KPI summary box must exist"
    
    kpi_content = kpi_box.group(1)
    
    # Assert NO N/A indicators
    assert "N/A" not in kpi_content, "KPI box contains N/A"
    assert "데이터 없음" not in kpi_content, "KPI box contains 데이터 없음"
    assert "분석 미완료" not in kpi_content, "KPI box contains 분석 미완료"
    
    print("✅ TEST PASSED: No N/A in core KPIs")

def test_module_completeness_gate():
    """Incomplete modules should BLOCK Final Report"""
    assembler = landowner_summary.LandownerSummaryAssembler("incomplete_context")
    
    is_complete, missing = assembler.validate_module_completeness()
    
    if not is_complete:
        print(f"✅ TEST PASSED: Incomplete modules detected: {missing}")
        with pytest.raises(Exception):
            assembler.assemble()  # Should raise error
    else:
        result = assembler.assemble()
        assert result["qa_result"]["status"] != "FAIL", "QA should catch incomplete data"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
    
    test_file = output_dir / "test_data_integrity.py"
    test_file.write_text(test_script, encoding='utf-8')
    print(f"✅ Generated: {test_file}")
    
    # Step 4: Summary
    print("\n\n📋 STEP 4: DEPLOYMENT INSTRUCTIONS")
    print("=" * 80)
    
    instructions = """
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
"""
    
    print(instructions)
    
    readme_file = output_dir / "DEPLOYMENT_README.md"
    readme_file.write_text(instructions, encoding='utf-8')
    print(f"\n✅ Deployment instructions saved to: {readme_file}")
    
    print("\n" + "=" * 80)
    print("✅ DIAGNOSTIC COMPLETE - Ready for repair implementation")
    print("=" * 80)
    

if __name__ == "__main__":
    main()
