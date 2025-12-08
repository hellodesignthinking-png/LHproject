"""
ZeroSite v15 Phase 2 - Sensitivity Chart Generator
===================================================

NPV Tornado Diagram Generator for Risk Analysis

Purpose: Visualize which variables have the greatest impact on project NPV
Output: Tornado chart data showing sensitivity ranges for key variables

Key Variables Analyzed:
1. Rental Rate (±20%)
2. Construction Cost (±15%)
3. Land Acquisition Cost (±10%)
4. Discount Rate (±1%)
5. Vacancy Rate (±5%)
6. Operating Costs (±10%)
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SensitivityVariable:
    """A single variable for sensitivity analysis"""
    name: str
    name_kr: str
    base_value: float
    variation_pct: float  # ±X%
    impact_on_npv: str  # 'positive' or 'negative'
    icon: str


class SensitivityChartGenerator:
    """
    v15 Phase 2 - NPV Sensitivity (Tornado Chart) Generator
    
    Analyzes how changes in key variables affect project NPV
    Generates data for tornado chart visualization
    """
    
    def __init__(self):
        """Initialize with standard sensitivity variables"""
        self.variables = [
            SensitivityVariable(
                name='rental_rate',
                name_kr='임대료 단가',
                base_value=0.0,  # Will be filled from context
                variation_pct=20.0,  # ±20%
                impact_on_npv='positive',
                icon='💰'
            ),
            SensitivityVariable(
                name='construction_cost',
                name_kr='건축비',
                base_value=0.0,
                variation_pct=15.0,  # ±15%
                impact_on_npv='negative',
                icon='🏗️'
            ),
            SensitivityVariable(
                name='land_cost',
                name_kr='토지비',
                base_value=0.0,
                variation_pct=10.0,  # ±10%
                impact_on_npv='negative',
                icon='🏞️'
            ),
            SensitivityVariable(
                name='discount_rate',
                name_kr='할인율',
                base_value=4.5,  # 4.5% default
                variation_pct=22.2,  # ±1 percentage point (1/4.5 = 22.2%)
                impact_on_npv='negative',
                icon='📊'
            ),
            SensitivityVariable(
                name='vacancy_rate',
                name_kr='공실률',
                base_value=5.0,  # 5% default
                variation_pct=100.0,  # ±5 percentage points (100% of 5%)
                impact_on_npv='negative',
                icon='🏚️'
            ),
            SensitivityVariable(
                name='operating_cost',
                name_kr='운영비',
                base_value=0.0,
                variation_pct=10.0,  # ±10%
                impact_on_npv='negative',
                icon='⚙️'
            )
        ]
    
    def generate_sensitivity_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive sensitivity analysis
        
        Args:
            context: Base project context from report_context_builder
            
        Returns:
            Dictionary with sensitivity results and tornado chart data
        """
        logger.info("📊 Generating NPV sensitivity analysis...")
        
        # Extract base values
        finance = context.get('finance', {})
        base_npv = finance.get('npv_public', 0)
        base_capex = finance.get('capex', {}).get('total', 0)
        base_revenue = finance.get('revenue', {}).get('annual_rental', 0)
        
        # Update variable base values
        self._update_base_values(base_capex, base_revenue)
        
        # Calculate sensitivity for each variable
        sensitivity_results = []
        for var in self.variables:
            result = self._calculate_variable_sensitivity(
                var, base_npv, base_capex, base_revenue
            )
            sensitivity_results.append(result)
        
        # Sort by absolute impact (highest to lowest)
        sensitivity_results.sort(key=lambda x: abs(x['npv_range_krw']), reverse=True)
        
        # Generate tornado chart data
        tornado_data = self._generate_tornado_data(sensitivity_results)
        
        # Calculate summary metrics
        summary = self._generate_summary(sensitivity_results, base_npv)
        
        return {
            'base_npv_krw': base_npv / 100_000_000,
            'sensitivity_results': sensitivity_results,
            'tornado_chart_data': tornado_data,
            'summary': summary,
            'interpretation': self._interpret_sensitivity(sensitivity_results)
        }
    
    def _update_base_values(self, base_capex: float, base_revenue: float):
        """Update base values for variables"""
        # Estimate component costs
        land_cost = base_capex * 0.40  # ~40% of CAPEX
        construction_cost = base_capex * 0.50  # ~50% of CAPEX
        operating_cost = base_revenue * 0.15  # ~15% of revenue
        
        for var in self.variables:
            if var.name == 'land_cost':
                var.base_value = land_cost
            elif var.name == 'construction_cost':
                var.base_value = construction_cost
            elif var.name == 'rental_rate':
                var.base_value = base_revenue
            elif var.name == 'operating_cost':
                var.base_value = operating_cost
    
    def _calculate_variable_sensitivity(
        self,
        var: SensitivityVariable,
        base_npv: float,
        base_capex: float,
        base_revenue: float
    ) -> Dict[str, Any]:
        """Calculate sensitivity for a single variable"""
        
        # Calculate high and low scenarios
        variation_amount = var.base_value * (var.variation_pct / 100)
        
        # For positive impact variables (revenue), high = +X%, low = -X%
        # For negative impact variables (costs), high = -X%, low = +X%
        if var.impact_on_npv == 'positive':
            high_value = var.base_value + variation_amount
            low_value = var.base_value - variation_amount
        else:  # negative impact
            high_value = var.base_value - variation_amount
            low_value = var.base_value + variation_amount
        
        # Estimate NPV impact
        npv_high = self._estimate_npv_with_change(
            base_npv, var.name, high_value, var.base_value, base_capex, base_revenue
        )
        npv_low = self._estimate_npv_with_change(
            base_npv, var.name, low_value, var.base_value, base_capex, base_revenue
        )
        
        npv_range = npv_high - npv_low
        
        npv_high_krw = npv_high / 100_000_000
        npv_low_krw = npv_low / 100_000_000
        npv_range_krw = npv_range / 100_000_000
        
        return {
            # Original format (for internal use)
            'name': var.name,
            'name_kr': var.name_kr,
            'icon': var.icon,
            'base_value': var.base_value,
            'variation_pct': var.variation_pct,
            'npv_base': base_npv / 100_000_000,
            'npv_high': npv_high_krw,
            'npv_low': npv_low_krw,
            'npv_range': npv_range,
            'npv_range_krw': npv_range_krw,
            'impact_label': f"±{var.variation_pct:.0f}%",
            # Template-friendly format
            'variable_name': f"{var.icon} {var.name_kr}",
            'change_pct': f"{var.variation_pct:.0f}",  # Template adds ± and %
            'low_npv': f"{npv_low_krw:+.1f}억원",
            'high_npv': f"{npv_high_krw:+.1f}억원",
            'impact_range': f"{abs(npv_range_krw):.1f}억원"
        }
    
    def _estimate_npv_with_change(
        self,
        base_npv: float,
        var_name: str,
        new_value: float,
        base_value: float,
        base_capex: float,
        base_revenue: float
    ) -> float:
        """Estimate new NPV with variable change"""
        
        # Calculate change ratio
        change_ratio = (new_value / base_value) if base_value > 0 else 1.0
        
        # Estimate NPV impact based on variable type
        if var_name == 'rental_rate':
            # Revenue impact: direct proportion to NPV
            # NPV ≈ PV(Revenues) - CAPEX
            revenue_impact = (change_ratio - 1.0) * base_revenue * 20  # 20-year PV approximation
            return base_npv + revenue_impact
            
        elif var_name in ['construction_cost', 'land_cost']:
            # Cost impact: inverse proportion to NPV
            cost_delta = new_value - base_value
            return base_npv - cost_delta
            
        elif var_name == 'discount_rate':
            # Discount rate impact: complex, use approximation
            # Higher discount rate → lower PV → lower NPV
            rate_delta = (new_value - base_value) / 100  # Convert to decimal
            # Rough approximation: -10% NPV per 1% rate increase
            return base_npv * (1 - rate_delta * 10)
            
        elif var_name == 'vacancy_rate':
            # Vacancy impact on revenue
            vacancy_delta = (new_value - base_value) / 100
            revenue_impact = -vacancy_delta * base_revenue * 20
            return base_npv + revenue_impact
            
        elif var_name == 'operating_cost':
            # OpEx impact
            cost_delta = new_value - base_value
            return base_npv - (cost_delta * 20)  # 20-year impact
        
        return base_npv
    
    def _generate_tornado_data(self, results: List[Dict]) -> List[Dict]:
        """Generate data formatted for tornado chart visualization"""
        tornado_data = []
        
        for result in results:
            # For tornado chart, we need left/right bars from center (base NPV)
            base = result['npv_base']
            high = result['npv_high']
            low = result['npv_low']
            
            tornado_data.append({
                'variable': result['name_kr'],
                'icon': result['icon'],
                'base': base,
                'high': high,
                'low': low,
                'high_delta': high - base,
                'low_delta': low - base,
                'range': abs(high - low),
                'impact_label': result['impact_label']
            })
        
        return tornado_data
    
    def _generate_summary(self, results: List[Dict], base_npv: float) -> Dict[str, Any]:
        """Generate summary statistics"""
        if not results:
            return {}
        
        # Most impactful variable
        most_impactful = results[0]
        
        # Total NPV range (best - worst case)
        all_highs = [r['npv_high'] for r in results]
        all_lows = [r['npv_low'] for r in results]
        max_npv = max(all_highs)
        min_npv = min(all_lows)
        
        return {
            'most_impactful_variable': most_impactful['name_kr'],
            'most_impactful_icon': most_impactful['icon'],
            'most_impactful_range_krw': most_impactful['npv_range_krw'],
            'max_npv_krw': max_npv / 100_000_000,
            'min_npv_krw': min_npv / 100_000_000,
            'total_npv_range_krw': (max_npv - min_npv) / 100_000_000,
            'base_npv_krw': base_npv / 100_000_000
        }
    
    def _interpret_sensitivity(self, results: List[Dict]) -> Dict[str, Any]:
        """Interpret sensitivity analysis results"""
        if not results:
            return {}
        
        top_3 = results[:3]
        
        # Classify project risk level
        top_range = top_3[0]['npv_range_krw'] if top_3 else 0
        
        if abs(top_range) > 500:  # >500억 swing
            risk_level = "HIGH"
            risk_level_kr = "높음"
            risk_color = "#dc3545"
        elif abs(top_range) > 200:  # 200-500억 swing
            risk_level = "MEDIUM"
            risk_level_kr = "중간"
            risk_color = "#ffc107"
        else:  # <200억 swing
            risk_level = "LOW"
            risk_level_kr = "낮음"
            risk_color = "#28a745"
        
        # Key insights
        insights = []
        for i, result in enumerate(top_3, 1):
            insights.append({
                'rank': i,
                'variable': result['name_kr'],
                'icon': result['icon'],
                'impact': f"±{abs(result['npv_range_krw']):.0f}억원",
                'recommendation': self._get_variable_recommendation(result['name'])
            })
        
        return {
            'risk_level': risk_level,
            'risk_level_kr': risk_level_kr,
            'risk_color': risk_color,
            'top_3_variables': [r['name_kr'] for r in top_3],
            'key_insights': insights,
            'overall_conclusion': self._generate_overall_conclusion(risk_level, top_3)
        }
    
    def _get_variable_recommendation(self, var_name: str) -> str:
        """Get recommendation for managing specific variable"""
        recommendations = {
            'rental_rate': '임대료 수준 최적화 및 시장 분석 강화',
            'construction_cost': 'VE 적용 및 시공사 경쟁 입찰',
            'land_cost': '토지 매입 협상력 강화 및 대안 입지 검토',
            'discount_rate': '정책자금(2.87%) 활용 및 금융 구조 최적화',
            'vacancy_rate': '입지 선정 및 임대 마케팅 강화',
            'operating_cost': '스마트 빌딩 시스템 도입 및 효율화'
        }
        return recommendations.get(var_name, '지속적 모니터링 필요')
    
    def _generate_overall_conclusion(self, risk_level: str, top_3: List[Dict]) -> str:
        """Generate overall conclusion for sensitivity analysis"""
        if risk_level == "HIGH":
            return f"프로젝트는 {top_3[0]['name_kr']}에 높은 민감도를 보입니다. 해당 변수의 철저한 관리가 필수적입니다."
        elif risk_level == "MEDIUM":
            return f"프로젝트는 중간 수준의 민감도를 보입니다. {top_3[0]['name_kr']} 및 {top_3[1]['name_kr']} 관리에 집중하십시오."
        else:
            return "프로젝트는 주요 변수 변동에 대해 안정적인 NPV를 유지합니다."


# Singleton instance
_sensitivity_chart_generator = None

def get_sensitivity_chart_generator() -> SensitivityChartGenerator:
    """Get singleton instance of sensitivity chart generator"""
    global _sensitivity_chart_generator
    if _sensitivity_chart_generator is None:
        _sensitivity_chart_generator = SensitivityChartGenerator()
    return _sensitivity_chart_generator
