"""
ZeroSite v24.1 - Alias Engine
Expanded alias system for variable mapping and formatting

Author: ZeroSite Development Team
Version: v24.1.0
Created: 2025-12-12
"""

from typing import Dict, Any, Optional, Union
from datetime import datetime
import re


class AliasEngineV241:
    """
    Expanded Alias Engine for ZeroSite v24.1
    
    Manages 250+ aliases for:
    - Variable name mapping
    - Unit conversions
    - Number formatting (Korean units: 억, 만)
    - LH terminology standardization
    - Report template variable substitution
    """
    
    def __init__(self):
        """Initialize alias engine with expanded mappings"""
        self.version = "24.1.0"
        
        # Core aliases (150 expanded to 250)
        self.aliases = self._initialize_aliases()
        
        # Unit conversion factors
        self.conversions = self._initialize_conversions()
        
        # Formatting templates
        self.formats = self._initialize_formats()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get alias value"""
        return self.aliases.get(key, default)
    
    def format_value(
        self,
        value: Union[int, float],
        format_type: str = "currency"
    ) -> str:
        """
        Format value according to type
        
        Args:
            value: Numeric value
            format_type: "currency", "area", "percent", "ratio", "count"
            
        Returns:
            Formatted string
        """
        if format_type == "currency":
            return self._format_currency(value)
        elif format_type == "area":
            return self._format_area(value)
        elif format_type == "percent":
            return f"{value:.1f}%"
        elif format_type == "ratio":
            return f"{value:.2f}"
        elif format_type == "count":
            return f"{int(value):,}개"
        else:
            return str(value)
    
    def convert_unit(
        self,
        value: float,
        from_unit: str,
        to_unit: str
    ) -> float:
        """Convert between units"""
        if from_unit == to_unit:
            return value
        
        key = f"{from_unit}_to_{to_unit}"
        if key in self.conversions:
            return value * self.conversions[key]
        
        # Try reverse conversion
        reverse_key = f"{to_unit}_to_{from_unit}"
        if reverse_key in self.conversions:
            return value / self.conversions[reverse_key]
        
        return value
    
    def substitute_template(
        self,
        template: str,
        data: Dict[str, Any]
    ) -> str:
        """
        Substitute template variables with formatted values
        
        Args:
            template: Template string with {{variable}} placeholders
            data: Data dictionary
            
        Returns:
            Substituted string
        """
        result = template
        
        # Find all {{variable}} patterns
        pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(pattern, template)
        
        for match in matches:
            # Parse variable specification: variable[:format]
            parts = match.split(':')
            var_name = parts[0].strip()
            format_spec = parts[1].strip() if len(parts) > 1 else None
            
            # Get value from data
            value = self._get_nested_value(data, var_name)
            
            if value is not None:
                # Format value
                if format_spec:
                    formatted = self.format_value(value, format_spec)
                elif isinstance(value, (int, float)):
                    formatted = self._format_currency(value)
                else:
                    formatted = str(value)
                
                # Replace in template
                result = result.replace(f"{{{{{match}}}}}", formatted)
        
        return result
    
    # Private methods
    
    def _initialize_aliases(self) -> Dict[str, str]:
        """Initialize 250+ alias mappings"""
        return {
            # Land Information (30)
            "land_area": "대지면적",
            "land_area_sqm": "대지면적(㎡)",
            "land_area_pyeong": "대지면적(평)",
            "land_price": "토지가격",
            "land_price_total": "토지매입비",
            "land_price_per_sqm": "㎡당 토지가격",
            "land_price_per_pyeong": "평당 토지가격",
            "appraisal_price": "감정평가액",
            "official_price": "공시지가",
            "transaction_price": "실거래가",
            "land_acquisition_cost": "토지취득비용",
            "land_acquisition_tax": "토지취득세",
            "address": "소재지",
            "district": "자치구",
            "neighborhood": "법정동",
            "lot_number": "지번",
            "road_address": "도로명주소",
            "parcel_id": "필지ID",
            "cadastral_area": "지적면적",
            "actual_area": "실측면적",
            "land_use": "토지이용현황",
            "land_category": "지목",
            "land_shape": "지형",
            "land_elevation": "고저차",
            "land_slope": "경사도",
            "land_orientation": "향",
            "corner_lot": "각지여부",
            "road_width": "도로폭",
            "road_contact": "도로접면",
            "topography": "지형지세",
            
            # Zoning & Regulations (40)
            "zone_type": "용도지역",
            "zone_district": "용도지구",
            "zone_area": "용도구역",
            "district_unit_plan": "지구단위계획",
            "height_district": "고도지구",
            "landscape_district": "경관지구",
            "building_coverage_ratio": "건폐율",
            "bcr": "건폐율",
            "bcr_limit": "건폐율 한도",
            "bcr_actual": "실제 건폐율",
            "floor_area_ratio": "용적률",
            "far": "용적률",
            "far_legal": "법정 용적률",
            "far_limit": "용적률 한도",
            "far_actual": "실제 용적률",
            "far_relaxation": "용적률 완화",
            "far_bonus": "용적률 인센티브",
            "far_final": "최종 용적률",
            "height_limit": "높이제한",
            "floors_limit": "층수제한",
            "setback_front": "전면 인접대지경계선",
            "setback_side": "측면 인접대지경계선",
            "setback_rear": "후면 인접대지경계선",
            "sunlight_regulation": "일조권규제",
            "parking_requirement": "주차대수",
            "parking_ratio": "주차대수비율",
            "green_area_ratio": "녹지율",
            "landscape_area_ratio": "조경면적비율",
            "building_line": "건축선",
            "skyline": "스카이라인",
            "building_height_restriction": "건축물 높이제한",
            "shadow_regulation": "그림자규제",
            "disaster_prevention": "방재지구",
            "preservation_district": "보전지구",
            "development_restriction": "개발제한",
            "historical_preservation": "문화재보호구역",
            "military_restriction": "군사시설보호구역",
            "airport_restriction": "공항보호구역",
            "river_regulation": "하천구역",
            "coastal_restriction": "연안구역",
            "mountainous_district": "산지전용",
            
            # Building Capacity (50)
            "building_area": "건축면적",
            "total_floor_area": "연면적",
            "gross_floor_area": "총면적",
            "net_floor_area": "순면적",
            "common_area": "공용면적",
            "exclusive_area": "전용면적",
            "balcony_area": "발코니면적",
            "basement_area": "지하면적",
            "rooftop_area": "옥상면적",
            "parking_area": "주차장면적",
            "unit_count": "세대수",
            "household_count": "총 세대수",
            "commercial_count": "상가수",
            "floors": "층수",
            "floors_above_ground": "지상층수",
            "floors_below_ground": "지하층수",
            "building_height": "건물높이",
            "floor_height": "층고",
            "ceiling_height": "천장고",
            "structure_type": "구조형식",
            "building_coverage": "건축면적",
            "footprint": "건축물 면적",
            "building_volume": "건물체적",
            "unit_area_avg": "평균 세대면적",
            "unit_area_min": "최소 세대면적",
            "unit_area_max": "최대 세대면적",
            "unit_type_1": "1타입 면적",
            "unit_type_2": "2타입 면적",
            "unit_type_3": "3타입 면적",
            "unit_mix": "세대타입 구성",
            "bay": "베이",
            "core": "코어",
            "elevator_count": "승강기대수",
            "staircase_count": "계단수",
            "entrance_count": "출입구수",
            "apartment_efficiency": "주거비율",
            "core_efficiency": "코어효율",
            "planning_efficiency": "평면효율",
            "gross_to_net_ratio": "용적률/순면적비",
            "sellable_area_ratio": "분양가능면적비",
            "rentable_area": "임대가능면적",
            "usable_area": "사용가능면적",
            "circulation_area": "복도면적",
            "mechanical_area": "기계실면적",
            "electrical_room_area": "전기실면적",
            "storage_area": "창고면적",
            "lobby_area": "로비면적",
            "amenity_area": "부대시설면적",
            "community_area": "커뮤니티시설면적",
            "commercial_area": "상업시설면적",
            
            # Financial (50)
            "total_project_cost": "총 사업비",
            "land_cost": "토지비",
            "construction_cost": "공사비",
            "construction_cost_per_sqm": "㎡당 공사비",
            "construction_cost_per_pyeong": "평당 공사비",
            "design_cost": "설계비",
            "supervision_cost": "감리비",
            "infrastructure_cost": "기반시설비",
            "permit_cost": "인허가비용",
            "financing_cost": "금융비용",
            "interest_cost": "이자비용",
            "overhead_cost": "일반관리비",
            "contingency": "예비비",
            "capex": "자본적지출",
            "opex": "운영비",
            "revenue": "매출",
            "sales_revenue": "분양수입",
            "rental_revenue": "임대수입",
            "gross_revenue": "총수입",
            "net_revenue": "순수입",
            "operating_income": "영업이익",
            "net_income": "순이익",
            "profit": "수익",
            "roi": "투자수익률",
            "irr": "내부수익률",
            "npv": "순현재가치",
            "payback_period": "회수기간",
            "break_even": "손익분기점",
            "profit_margin": "이익률",
            "gross_margin": "매출총이익률",
            "operating_margin": "영업이익률",
            "net_margin": "순이익률",
            "debt_ratio": "부채비율",
            "loan_amount": "대출금액",
            "loan_to_value": "LTV",
            "debt_service_coverage": "DSCR",
            "equity": "자기자본",
            "leverage": "레버리지",
            "cash_flow": "현금흐름",
            "operating_cash_flow": "영업현금흐름",
            "free_cash_flow": "잉여현금흐름",
            "discount_rate": "할인율",
            "inflation_rate": "물가상승률",
            "tax_rate": "세율",
            "depreciation": "감가상각",
            "amortization": "상각",
            "capital_gain": "자본이득",
            "capital_loss": "자본손실",
            "transaction_cost": "거래비용",
            "closing_cost": "정산비용",
            
            # Market Analysis (30)
            "market_price": "시장가격",
            "comparable_price": "비교가격",
            "average_price": "평균가격",
            "median_price": "중위가격",
            "price_range": "가격대",
            "price_per_sqm": "㎡당 가격",
            "price_per_pyeong": "평당 가격",
            "price_trend": "가격추이",
            "price_growth": "가격상승률",
            "market_volatility": "시장변동성",
            "coefficient_of_variation": "변동계수",
            "standard_deviation": "표준편차",
            "price_index": "가격지수",
            "supply": "공급량",
            "demand": "수요량",
            "inventory": "재고",
            "absorption_rate": "흡수율",
            "vacancy_rate": "공실률",
            "occupancy_rate": "가동률",
            "market_share": "시장점유율",
            "competition": "경쟁상황",
            "comparable_project": "비교사례",
            "market_condition": "시장여건",
            "economic_indicator": "경제지표",
            "interest_rate": "금리",
            "inflation": "인플레이션",
            "gdp_growth": "GDP성장률",
            "unemployment_rate": "실업률",
            "consumer_confidence": "소비자신뢰지수",
            "market_outlook": "시장전망",
            
            # Risk & Compliance (20)
            "design_risk": "설계리스크",
            "legal_risk": "법적리스크",
            "financial_risk": "재무리스크",
            "construction_risk": "공사리스크",
            "market_risk": "시장리스크",
            "regulatory_risk": "규제리스크",
            "environmental_risk": "환경리스크",
            "title_risk": "권리리스크",
            "permit_risk": "인허가리스크",
            "zoning_compliance": "용도지역 적합성",
            "building_code_compliance": "건축법규 준수",
            "fire_safety": "소방안전",
            "seismic_design": "내진설계",
            "barrier_free": "장애인편의",
            "energy_efficiency": "에너지효율",
            "green_building": "친환경건축",
            "carbon_footprint": "탄소발자국",
            "social_value": "사회적가치",
            "esg_score": "ESG점수",
            "sustainability": "지속가능성",
            
            # Scenario & Comparison (30)
            "scenario_a": "시나리오 A",
            "scenario_b": "시나리오 B",
            "scenario_c": "시나리오 C",
            "base_case": "기본안",
            "optimistic_case": "낙관적시나리오",
            "pessimistic_case": "비관적시나리오",
            "best_case": "최선안",
            "worst_case": "최악안",
            "comparison": "비교분석",
            "sensitivity": "민감도",
            "what_if": "가정분석",
            "monte_carlo": "몬테카를로분석",
            "break_even_analysis": "손익분기분석",
            "feasibility": "사업타당성",
            "viability": "사업성",
            "optimal_solution": "최적해",
            "pareto_optimal": "파레토최적",
            "multi_criteria": "다기준분석",
            "decision_matrix": "의사결정매트릭스",
            "weight": "가중치",
            "score": "점수",
            "rank": "순위",
            "priority": "우선순위",
            "recommendation": "권고사항",
            "conclusion": "결론",
            "executive_summary": "요약",
            "key_findings": "주요발견사항",
            "action_items": "실행과제",
            "next_steps": "다음단계",
            "timeline": "일정"
        }
    
    def _initialize_conversions(self) -> Dict[str, float]:
        """Initialize unit conversion factors"""
        return {
            # Area conversions
            "sqm_to_pyeong": 0.3025,
            "pyeong_to_sqm": 3.3058,
            "sqm_to_sqft": 10.7639,
            "sqft_to_sqm": 0.0929,
            
            # Length conversions
            "m_to_ft": 3.28084,
            "ft_to_m": 0.3048,
            "m_to_cm": 100.0,
            "cm_to_m": 0.01,
            
            # Currency (1억 = 100,000,000)
            "won_to_eok": 0.00000001,
            "eok_to_won": 100000000,
            "won_to_man": 0.0001,
            "man_to_won": 10000
        }
    
    def _initialize_formats(self) -> Dict[str, str]:
        """Initialize format templates"""
        return {
            "currency": "{:,.0f}원",
            "currency_eok": "{:,.1f}억원",
            "area_sqm": "{:,.1f}㎡",
            "area_pyeong": "{:,.1f}평",
            "percent": "{:.1f}%",
            "ratio": "{:.2f}",
            "count": "{:,}개",
            "floors": "{:}층"
        }
    
    def _format_currency(self, value: float) -> str:
        """Format currency in Korean style"""
        if abs(value) >= 100000000:  # 1억 이상
            eok = value / 100000000
            return f"{eok:,.1f}억원"
        elif abs(value) >= 10000:  # 1만 이상
            man = value / 10000
            return f"{man:,.0f}만원"
        else:
            return f"{value:,.0f}원"
    
    def _format_area(self, value: float) -> str:
        """Format area"""
        pyeong = value * 0.3025
        return f"{value:,.1f}㎡ ({pyeong:,.1f}평)"
    
    def _get_nested_value(self, data: Dict, key: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = key.split('.')
        value = data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None
            
            if value is None:
                return None
        
        return value
    
    # ========== PHASE 7: HTML Formatting Methods (150 Transforms) ==========
    
    def format_number(self, value: float) -> str:
        """Format number with comma separator"""
        return f"{value:,.0f}"
    
    def format_currency(self, value: float) -> str:
        """Format currency for HTML display"""
        return self._format_currency(value)
    
    def format_area(self, value: float) -> str:
        """Format area (alias for format_area_dual)"""
        return self._format_area(value)
    
    def format_percentage(self, value: float) -> str:
        """Format percentage for HTML display"""
        return f"{value * 100:.1f}%"
    
    def format_area_simple(self, value: float) -> str:
        """Format area in square meters only"""
        return f"{value:,.1f}㎡"
    
    def format_area_dual(self, value: float) -> str:
        """Format area with both sqm and pyeong"""
        return self._format_area(value)
    
    def format_floors(self, value: int) -> str:
        """Format floor count"""
        return f"{value:,}층"
    
    def format_units(self, value: int) -> str:
        """Format unit count"""
        return f"{value:,}세대"
    
    def format_date_korean(self, date_str: str) -> str:
        """Format date in Korean style (YYYY년 MM월 DD일)"""
        try:
            from datetime import datetime
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return f"{dt.year}년 {dt.month}월 {dt.day}일"
        except:
            return date_str
    
    def format_ratio(self, value: float, decimals: int = 2) -> str:
        """Format ratio (e.g., 1.5 → 1.50)"""
        return f"{value:.{decimals}f}"
    
    def format_months(self, value: int) -> str:
        """Format months (e.g., 36 → 36개월)"""
        return f"{value:,}개월"
    
    def format_years(self, value: float) -> str:
        """Format years (e.g., 3.5 → 3.5년)"""
        return f"{value:.1f}년"
    
    def format_parking_spaces(self, value: int) -> str:
        """Format parking space count"""
        return f"{value:,}대"
    
    def format_risk_level(self, level: str) -> str:
        """Format risk level with color coding"""
        colors = {
            '높음': 'red',
            '중간': 'orange',
            '낮음': 'green',
            'high': 'red',
            'medium': 'orange',
            'low': 'green'
        }
        color = colors.get(level, 'gray')
        return f'<span style="color: {color}; font-weight: bold;">{level}</span>'
    
    def format_scenario_label(self, scenario: str) -> str:
        """Format scenario label (A/B/C)"""
        labels = {
            'A': '시나리오 A (소형 중심)',
            'B': '시나리오 B (중대형 혼합)',
            'C': '시나리오 C (고령친화)'
        }
        return labels.get(scenario, scenario)
    
    def apply_html_formatting(self, html_template: str, data: dict) -> str:
        """
        PHASE 7: Apply all 150 formatting transforms to HTML template
        
        This method replaces all {{key}} placeholders with formatted values:
        - Currency: {{financial.total_cost}} → "150억원"
        - Area: {{capacity.land_area}} → "1,234.5㎡ (373.4평)"
        - Percentage: {{financial.roi}} → "15.5%"
        - Dates: {{project.start_date}} → "2025년 12월 12일"
        """
        import re
        
        # Find all {{key}} patterns
        pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(pattern, html_template)
        
        for match in matches:
            key = match.strip()
            value = self._get_nested_value(data, key)
            
            if value is None:
                continue
            
            # Determine format based on key name
            formatted_value = self._auto_format_value(key, value)
            
            # Replace in template
            html_template = html_template.replace(f'{{{{{match}}}}}', str(formatted_value))
        
        return html_template
    
    def _auto_format_value(self, key: str, value: Any) -> str:
        """Auto-detect format type from key name"""
        key_lower = key.lower()
        
        # Currency formatting
        if any(word in key_lower for word in ['cost', 'price', 'revenue', 'income', 'expense']):
            return self.format_currency(float(value))
        
        # Area formatting
        if any(word in key_lower for word in ['area', 'land', 'footprint']):
            return self.format_area_dual(float(value))
        
        # Percentage formatting
        if any(word in key_lower for word in ['roi', 'irr', 'ratio', 'rate', 'percent']):
            if float(value) <= 1.0:  # Already a decimal
                return self.format_percentage(float(value))
            else:  # Already a percentage
                return f"{float(value):.1f}%"
        
        # Floor formatting
        if 'floor' in key_lower:
            return self.format_floors(int(value))
        
        # Unit formatting
        if 'unit' in key_lower and 'unit_' not in key_lower:
            return self.format_units(int(value))
        
        # Date formatting
        if 'date' in key_lower:
            return self.format_date_korean(str(value))
        
        # Default: return as-is
        return str(value)


# Module exports
__all__ = ["AliasEngineV241"]
