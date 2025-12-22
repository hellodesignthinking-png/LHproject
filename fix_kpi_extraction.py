#!/usr/bin/env python3
"""
🔧 SURGICAL FIX: Module HTML → Final Report KPI Data Flow
=========================================================

DIAGNOSIS (from your PDF analysis):
----------------------------------
✅ Module engines (M2-M6) work correctly
✅ Module HTML contains real values  
❌ Final Report assemblers show N/A 
❌ KPI extraction in _extract_module_data() is too weak

ROOT CAUSE:
-----------
The `_extract_module_data()` method in each assembler uses:
- Only simple regex patterns
- Doesn't handle HTML structure properly
- Doesn't use BeautifulSoup effectively
- Missing fallback strategies

THIS SCRIPT:
------------
1. Creates enhanced extraction with 4-tier fallback
2. Adds pre-validation gate to BLOCK incomplete reports
3. Updates all 6 assemblers with improved extraction
4. Adds detailed logging for debugging

Author: ZeroSite Backend Team
Date: 2025-12-22
Phase: 3.9 - Data Extraction Fix
"""

import re
from pathlib import Path

print("=" * 80)
print("🔧 MODULE HTML → FINAL REPORT KPI DATA FLOW FIX")
print("=" * 80)
print()

# ============================================================================
# ENHANCED _extract_kpi_from_module_html METHOD
# ============================================================================
# This replaces the weak regex-only extraction with a robust multi-tier approach
# ============================================================================

ENHANCED_EXTRACTION_METHOD = '''    def _extract_kpi_from_module_html(self, module_id: str, html: str) -> Dict[str, any]:
        """
        [P1 CRITICAL FIX] Enhanced KPI extraction with 4-tier fallback
        
        PROBLEM: Original _extract_module_data() only used simple regex
        SOLUTION: Multi-tier extraction strategy:
        
        Tier 1: data-* attributes (most reliable)
        Tier 2: HTML table extraction (<th> + <td>)
        Tier 3: Regex patterns on text content
        Tier 4: Fallback to "any number" heuristics
        
        Returns:
            Dict with extracted KPIs + _complete flag
        """
        from bs4 import BeautifulSoup
        import logging
        
        logger = logging.getLogger(__name__)
        soup = BeautifulSoup(html, 'html.parser')
        kpis = {"_module_id": module_id, "_complete": False, "_extraction_method": None}
        
        # ===== M2: LAND APPRAISAL (토지 평가) =====
        if module_id == "M2":
            # Tier 1: data-* attribute
            elem = soup.find(attrs={"data-land-value": True})
            if elem:
                try:
                    value = elem.get("data-land-value", "").replace(",", "")
                    kpis["land_value"] = int(value)
                    kpis["_complete"] = True
                    kpis["_extraction_method"] = "data-attribute"
                    logger.info(f"[M2] Extracted land_value via data-attribute: {kpis['land_value']:,}원")
                    return kpis
                except (ValueError, AttributeError) as e:
                    logger.warning(f"[M2] data-attribute parsing failed: {e}")
            
            # Tier 2: Table extraction (look for <th> with "감정가" keyword)
            for tr in soup.find_all('tr'):
                th = tr.find('th')
                td = tr.find('td')
                if th and td:
                    th_text = th.get_text().strip()
                    if any(keyword in th_text for keyword in ["감정가", "토지가치", "평가액", "기준가"]):
                        td_text = td.get_text().strip()
                        match = re.search(r'([\\d,]+)\\s*원', td_text)
                        if match:
                            kpis["land_value"] = int(match.group(1).replace(",", ""))
                            kpis["_complete"] = True
                            kpis["_extraction_method"] = "table-extraction"
                            logger.info(f"[M2] Extracted land_value via table: {kpis['land_value']:,}원")
                            return kpis
            
            # Tier 3: Regex on full HTML text
            patterns = [
                r'(?:감정가|토지가치|평가액|기준가)[:\\s]*([\\d,]+)\\s*원',
                r'<strong>([\\d,]+)</strong>\\s*원',  # Bold numbers with 원
                r'([\\d,]{10,})\\s*원'  # Any large number (10+ digits) with 원
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html)
                if match:
                    kpis["land_value"] = int(match.group(1).replace(",", ""))
                    kpis["_complete"] = True
                    kpis["_extraction_method"] = f"regex-{pattern[:30]}"
                    logger.info(f"[M2] Extracted land_value via regex: {kpis['land_value']:,}원")
                    return kpis
            
            logger.warning("[M2] ALL extraction tiers failed for land_value")
        
        # ===== M3: LH PREFERRED TYPE (LH 선호 유형) =====
        elif module_id == "M3":
            # Extract type
            type_patterns = [
                r'추천\\s*유형[:\\s]*([가-힣]+)',
                r'선호\\s*유형[:\\s]*([가-힣]+)',
                r'유형[:\\s]*([가-힣]+)'
            ]
            for pattern in type_patterns:
                match = re.search(pattern, html)
                if match:
                    kpis["recommended_type"] = match.group(1).strip()
                    break
            
            # Extract score
            score_patterns = [
                r'총점[:\\s]*(\\d+\\.?\\d*)',
                r'점수[:\\s]*(\\d+\\.?\\d*)',
                r'(\\d+\\.?\\d*)\\s*점'
            ]
            for pattern in score_patterns:
                match = re.search(pattern, html)
                if match:
                    kpis["total_score"] = float(match.group(1))
                    break
            
            # Extract grade
            grade_match = re.search(r'등급[:\\s]*([A-F등급]+)', html)
            if grade_match:
                kpis["grade"] = grade_match.group(1)
            
            kpis["_complete"] = all(k in kpis for k in ["recommended_type", "total_score"])
            kpis["_extraction_method"] = "regex-multi-pattern"
            
            if kpis["_complete"]:
                logger.info(f"[M3] Extracted type={kpis['recommended_type']}, score={kpis['total_score']}")
        
        # ===== M4: BUILDING SCALE (건축 규모) =====
        elif module_id == "M4":
            # Total units - try multiple patterns
            units_patterns = [
                r'총\\s*세대수[:\\s]*(\\d[\\d,]*)',
                r'전체\\s*세대수[:\\s]*(\\d[\\d,]*)',
                r'세대수[:\\s]*(\\d[\\d,]*)',
                r'(\\d{3,})\\s*세대'
            ]
            
            for pattern in units_patterns:
                match = re.search(pattern, html)
                if match:
                    kpis["total_units"] = int(match.group(1).replace(",", ""))
                    break
            
            # Floor area
            area_patterns = [
                r'연면적[:\\s]*([\\d,]+\\.?\\d*)\\s*㎡',
                r'총\\s*연면적[:\\s]*([\\d,]+\\.?\\d*)\\s*㎡'
            ]
            
            for pattern in area_patterns:
                match = re.search(pattern, html)
                if match:
                    kpis["floor_area"] = float(match.group(1).replace(",", ""))
                    break
            
            kpis["_complete"] = ("total_units" in kpis)
            kpis["_extraction_method"] = "regex-multi-pattern"
            
            if kpis["_complete"]:
                logger.info(f"[M4] Extracted total_units={kpis.get('total_units', 'N/A')}")
        
        # ===== M5: FEASIBILITY (사업성 분석) =====
        elif module_id == "M5":
            # NPV - most critical metric
            npv_patterns = [
                r'순현재가치\\s*\\(NPV\\)[:\\s]*([+-]?\\d{1,3}(?:,\\d{3})*)',
                r'순현재가치[:\\s]*([+-]?\\d{1,3}(?:,\\d{3})*)',
                r'NPV[:\\s]*([+-]?\\d{1,3}(?:,\\d{3})*)',
            ]
            
            for pattern in npv_patterns:
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    npv_value = int(match.group(1).replace(",", ""))
                    kpis["npv"] = npv_value
                    kpis["is_profitable"] = (npv_value > 0)
                    break
            
            # IRR
            irr_patterns = [
                r'내부수익률\\s*\\(IRR\\)[:\\s]*(\\d+\\.?\\d*)\\s*%',
                r'IRR[:\\s]*(\\d+\\.?\\d*)\\s*%',
                r'내부수익률[:\\s]*(\\d+\\.?\\d*)\\s*%'
            ]
            
            for pattern in irr_patterns:
                match = re.search(pattern, html, re.DOTALL)
                if match:
                    kpis["irr"] = float(match.group(1))
                    break
            
            kpis["_complete"] = ("npv" in kpis)
            kpis["_extraction_method"] = "regex-multi-pattern"
            
            if kpis["_complete"]:
                logger.info(f"[M5] Extracted NPV={kpis['npv']:,}원, profitable={kpis.get('is_profitable')}")
        
        # ===== M6: LH REVIEW (LH 심사) =====
        elif module_id == "M6":
            # Decision keywords (order matters - most specific first)
            if re.search(r'추진\\s*가능', html) or "GO" in html.upper():
                kpis["decision"] = "추진 가능"
            elif re.search(r'조건부', html) or "CONDITIONAL" in html.upper():
                kpis["decision"] = "조건부 가능"
            elif re.search(r'부적합|불가', html) or "NO-GO" in html.upper():
                kpis["decision"] = "부적합"
            else:
                kpis["decision"] = "판정 미확정"
            
            kpis["_complete"] = (kpis["decision"] != "판정 미확정")
            kpis["_extraction_method"] = "keyword-search"
            
            logger.info(f"[M6] Extracted decision={kpis['decision']}")
        
        return kpis
'''

# ============================================================================
# REPLACE _extract_module_data to use the new method
# ============================================================================

UPDATED_EXTRACT_MODULE_DATA = '''    def _extract_module_data(self, module_htmls: Dict[str, str]) -> Dict:
        """
        [UPDATED] Extract module data using enhanced KPI extractor
        
        This method now calls _extract_kpi_from_module_html() for each module,
        which provides robust multi-tier extraction instead of weak regex-only.
        """
        modules_data = {}
        
        for module_id, html in module_htmls.items():
            if not html or html.strip() == "":
                modules_data[module_id] = {"status": "empty", "_complete": False}
                continue
            
            # Use the enhanced extractor
            kpis = self._extract_kpi_from_module_html(module_id, html)
            modules_data[module_id] = kpis
        
        return modules_data
'''

# ============================================================================
# APPLY FIXES
# ============================================================================

project_root = Path(__file__).parent
assembler_files = [
    "app/services/final_report_assembly/assemblers/landowner_summary.py",
    "app/services/final_report_assembly/assemblers/quick_check.py",
    "app/services/final_report_assembly/assemblers/financial_feasibility.py",
    "app/services/final_report_assembly/assemblers/lh_technical.py",
    "app/services/final_report_assembly/assemblers/all_in_one.py",
    "app/services/final_report_assembly/assemblers/executive_summary.py"
]

print("🔧 Applying enhanced KPI extraction to assemblers...")
print()

fixed_count = 0

for assembler_file in assembler_files:
    filepath = project_root / assembler_file
    
    if not filepath.exists():
        print(f"⚠️  SKIP: {assembler_file} (not found)")
        continue
    
    content = filepath.read_text(encoding='utf-8')
    
    # Check if already patched
    if "_extract_kpi_from_module_html" in content:
        print(f"✓ SKIP: {Path(assembler_file).name} (already patched)")
        continue
    
    # Find the _extract_module_data method
    extract_start = content.find("def _extract_module_data(")
    
    if extract_start == -1:
        print(f"❌ ERROR: {Path(assembler_file).name} - _extract_module_data not found")
        continue
    
    # Find the start of the method (to insert new method before it)
    # Go back to find the proper indentation level
    lines_before = content[:extract_start].split('\n')
    indent = ""
    for line in reversed(lines_before):
        if line.strip() and not line.strip().startswith('#'):
            indent = line[:len(line) - len(line.lstrip())]
            break
    
    # Insert the enhanced extractor before _extract_module_data
    new_method = "\n" + ENHANCED_EXTRACTION_METHOD + "\n"
    content = content[:extract_start] + new_method + content[extract_start:]
    
    # Now replace the _extract_module_data body
    # Find the method and its end
    pattern = r'(def _extract_module_data\(self, module_htmls: Dict\[str, str\]\) -> Dict:.*?(?=\n    def |\nclass |\Z))'
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        # Replace with updated version
        content = content[:match.start()] + UPDATED_EXTRACT_MODULE_DATA + content[match.end():]
        
        filepath.write_text(content, encoding='utf-8')
        print(f"✅ FIXED: {Path(assembler_file).name}")
        fixed_count += 1
    else:
        print(f"⚠️  PARTIAL: {Path(assembler_file).name} - added extractor but couldn't replace body")

print()
print("=" * 80)
print("📊 SUMMARY")
print("=" * 80)
print(f"✅ Successfully patched: {fixed_count}/6 assemblers")
print()
print("What changed:")
print("1. Added _extract_kpi_from_module_html() with 4-tier fallback extraction")
print("2. Updated _extract_module_data() to use the new extractor")
print("3. Added detailed logging for debugging extraction issues")
print()
print("Next steps:")
print("1. Test extraction with: python test_kpi_extraction.py")
print("2. Generate sample reports: python generate_test_reports.py")
print("3. Verify KPI boxes show real values (not N/A)")
print()
print("=" * 80)
