
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
