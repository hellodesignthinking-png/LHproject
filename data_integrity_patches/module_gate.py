
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
