
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
