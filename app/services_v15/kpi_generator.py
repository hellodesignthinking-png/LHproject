"""
KPI Generator for ZeroSite v15 Phase 1
Generates 4 key KPI cards for Executive Summary

Purpose:
- Quantify project impact in simple metrics
- Show government evaluators tangible outcomes
- Support policy justification with numbers

KPIs:
1. 주택 공급 (Housing Supply)
2. 인구 유입 (Population Influx)
3. 고용 효과 (Employment Impact)
4. 생활권 확장 (Community Expansion)

Author: ZeroSite Development Team
Date: 2025-12-07
Version: v15 Phase 1
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class KPIGenerator:
    """
    Generates 4 KPI cards showing project impact
    
    Each KPI includes:
    - Metric name
    - Value (number with unit)
    - Comparison (vs baseline or target)
    - Icon/emoji for visualization
    """
    
    def __init__(self):
        self.multipliers = {
            'population_per_unit': 2.3,  # Average persons per household
            'jobs_per_100_units': 13,    # Construction + operations jobs
            'community_threshold': 30     # Units needed for new community
        }
    
    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate all 4 KPIs
        
        Args:
            context: Report context with site, demand, finance data
            
        Returns:
            Dict with 4 KPIs:
            - housing_supply
            - population_influx
            - employment_impact
            - community_expansion
        """
        logger.info("Generating KPI cards...")
        
        kpis = {
            'housing_supply': self._calculate_housing_supply(context),
            'population_influx': self._calculate_population_influx(context),
            'employment_impact': self._calculate_employment(context),
            'community_expansion': self._calculate_community(context)
        }
        
        logger.info(f"KPIs generated: {kpis['housing_supply']['value']}호, {kpis['population_influx']['value']}명, {kpis['employment_impact']['value']}명, {kpis['community_expansion']['value']}")
        
        return kpis
    
    def _calculate_housing_supply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        KPI 1: Housing Supply (주택 공급)
        
        Calculates:
        - Total units based on land area and FAR
        - Increase vs baseline (if applicable)
        """
        site = context.get('site', {})
        zoning = context.get('zoning', {})
        
        land_area = site.get('land_area_sqm', 500)
        far = zoning.get('far', 200.0) / 100.0  # Convert % to decimal
        
        # Estimate units (assuming 40㎡ per unit average)
        avg_unit_size = 40  # sqm
        total_floor_area = land_area * far
        estimated_units = int(total_floor_area / avg_unit_size)
        
        # Calculate increase (assuming area was undeveloped or underutilized)
        baseline_units = 0  # Conservative assumption
        increase_pct = 100 if baseline_units == 0 else int((estimated_units - baseline_units) / baseline_units * 100)
        
        return {
            'name': '주택 공급',
            'name_en': 'Housing Supply',
            'value': estimated_units,
            'unit': '호',
            'comparison': f'+{increase_pct}%' if increase_pct > 0 else '신규',
            'baseline': baseline_units,
            'icon': '🏘️',
            'description': f'신규 공급 {estimated_units}호 (공공임대)'
        }
    
    def _calculate_population_influx(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        KPI 2: Population Influx (인구 유입)
        
        Calculates:
        - Expected population based on units × household size
        - Target demographic (youth/newlyweds)
        """
        housing_units = self._calculate_housing_supply(context)['value']
        demand = context.get('demand', {})
        
        # Average household size for target demographic
        housing_type = demand.get('recommended_type', 'youth')
        if housing_type == 'youth':
            household_size = 1.5  # Singles + couples
        elif housing_type == 'newlyweds':
            household_size = 2.5  # Couples + children
        elif housing_type == 'elderly':
            household_size = 1.8  # Elderly couples
        else:
            household_size = 2.3  # General
        
        population_influx = int(housing_units * household_size)
        
        return {
            'name': '인구 유입',
            'name_en': 'Population Influx',
            'value': population_influx,
            'unit': '명',
            'comparison': demand.get('recommended_type_kr', '청년·신혼부부'),
            'icon': '👥',
            'description': f'{demand.get("recommended_type_kr", "청년·신혼부부")} 중심 {population_influx}명 유입'
        }
    
    def _calculate_employment(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        KPI 3: Employment Impact (고용 효과)
        
        Calculates:
        - Direct jobs (construction)
        - Indirect jobs (operations, services)
        """
        housing_units = self._calculate_housing_supply(context)['value']
        
        # Employment multiplier: ~13 jobs per 100 units
        # - Construction: ~8 jobs per 100 units (temporary)
        # - Operations: ~3 jobs per 100 units (permanent)
        # - Indirect: ~2 jobs per 100 units (services)
        
        total_jobs = int(housing_units * self.multipliers['jobs_per_100_units'] / 100)
        
        # Split into construction and permanent
        construction_jobs = int(total_jobs * 0.6)
        permanent_jobs = int(total_jobs * 0.4)
        
        return {
            'name': '고용 효과',
            'name_en': 'Employment Impact',
            'value': total_jobs,
            'unit': '명',
            'comparison': f'건설 {construction_jobs}명 + 운영 {permanent_jobs}명',
            'icon': '💼',
            'description': f'직·간접 고용 {total_jobs}명 (건설+운영+서비스)',
            'breakdown': {
                'construction': construction_jobs,
                'permanent': permanent_jobs
            }
        }
    
    def _calculate_community(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        KPI 4: Community Expansion (생활권 확장)
        
        Calculates:
        - Number of new community centers/facilities
        - Neighborhood impact
        """
        housing_units = self._calculate_housing_supply(context)['value']
        site = context.get('site', {})
        
        # Community facility threshold: 30 units per facility
        community_facilities = int(housing_units / self.multipliers['community_threshold'])
        
        # Minimum 1 facility
        if community_facilities == 0:
            community_facilities = 1
        
        # Types of facilities
        facility_types = []
        if housing_units >= 30:
            facility_types.append('커뮤니티센터')
        if housing_units >= 50:
            facility_types.append('육아시설')
        if housing_units >= 80:
            facility_types.append('공유오피스')
        
        if not facility_types:
            facility_types = ['주민시설']
        
        return {
            'name': '생활권 확장',
            'name_en': 'Community Expansion',
            'value': community_facilities,
            'unit': '개소',
            'comparison': ' + '.join(facility_types),
            'icon': '🏢',
            'description': f'{community_facilities}개 커뮤니티 시설 ({", ".join(facility_types)})',
            'facility_types': facility_types
        }
    
    def generate_summary_text(self, kpis: Dict[str, Any]) -> str:
        """
        Generate one-line summary of all KPIs for executive display
        
        Example: "48호 공급 → 92명 유입 → 26명 고용 → 2개소 커뮤니티"
        """
        housing = kpis['housing_supply']
        population = kpis['population_influx']
        employment = kpis['employment_impact']
        community = kpis['community_expansion']
        
        return (
            f"{housing['value']}{housing['unit']} 공급 → "
            f"{population['value']}{population['unit']} 유입 → "
            f"{employment['value']}{employment['unit']} 고용 → "
            f"{community['value']}{community['unit']} 커뮤니티"
        )
    
    def calculate_total_impact_score(self, kpis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall impact score based on KPIs
        
        Returns:
            Dict with:
            - score: 0-100
            - grade: S/A/B/C
            - summary: Text description
        """
        housing = kpis['housing_supply']['value']
        population = kpis['population_influx']['value']
        employment = kpis['employment_impact']['value']
        
        # Scoring logic (weights)
        score = 0
        score += min(housing / 50 * 30, 30)      # Max 30 points for housing
        score += min(population / 100 * 30, 30)  # Max 30 points for population
        score += min(employment / 30 * 20, 20)   # Max 20 points for employment
        score += 20  # Base 20 points for community impact
        
        score = int(score)
        
        # Grade
        if score >= 85:
            grade = 'S'
        elif score >= 70:
            grade = 'A'
        elif score >= 55:
            grade = 'B'
        else:
            grade = 'C'
        
        return {
            'score': score,
            'grade': grade,
            'summary': f'사회경제적 영향 {grade}등급 ({score}점)'
        }


# Export
__all__ = ['KPIGenerator']
