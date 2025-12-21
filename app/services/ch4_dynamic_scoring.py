"""
CH4 Dynamic Demand Scoring Module
Generates dynamic, differentiated scores for each housing type based on type_demand_scores

Version: v8.7
Date: 2025-12-15

Problem Addressed:
- Previously: All unit types showed uniform scores (13 points)
- Now: Each type has distinct scores based on actual demand analysis

Scoring Factors:
- 청년형 (Youth): Subway/university access, youth population ratio
- 신혼부부 I (Newlywed Small): School/childcare access, affordable pricing
- 신혼부부 II (Newlywed Large): School quality, family amenities
- 다자녀형 (Multi-child): School + hospital access, community facilities
"""

from typing import Dict, List, Any, Optional


class CH4DynamicScorer:
    """
    CH4 수요분석 동적 점수 생성기
    
    각 주거 유형별로 차별화된 점수를 생성하여 보고서 CH4에 반영
    """
    
    # Housing type Korean names
    TYPE_NAMES = {
        'youth': '청년형',
        'newlywed_1': '신혼부부 I',
        'newlywed_2': '신혼부부 II',
        'multichild': '다자녀형',
        'elderly': '고령자형'
    }
    
    def __init__(self):
        """Initialize CH4 dynamic scorer"""
        pass
    
    def generate_demand_scores(
        self,
        type_demand_scores: Dict[str, float],
        demographic_info: Dict[str, Any],
        accessibility: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate dynamic demand scores for each housing type
        
        Args:
            type_demand_scores: Raw scores from analysis engine (e.g., {'청년': 88.5, '신혼부부 I': 85.2})
            demographic_info: Demographic data (population, youth ratio, etc.)
            accessibility: Location accessibility data (subway, school, etc.)
        
        Returns:
            Dictionary with detailed scores per type:
            {
                '청년형': {
                    'total_score': 18,  # 0-20 points
                    'raw_score': 88.5,
                    'factors': {
                        'location': 9,
                        'demographics': 6,
                        'amenities': 3
                    },
                    'strength': 'high',  # high/medium/low
                    'rationale': '지하철 300m, 청년인구 28%'
                }
            }
        """
        
        result = {}
        
        for type_key, type_name in self.TYPE_NAMES.items():
            # Find matching score from type_demand_scores
            raw_score = self._find_matching_score(type_name, type_demand_scores)
            
            if raw_score is None:
                continue
            
            # Convert 0-100 score to 0-20 points
            total_score = self._convert_to_20_point_scale(raw_score)
            
            # Calculate factor breakdown
            factors = self._calculate_factor_breakdown(
                type_key=type_key,
                raw_score=raw_score,
                demographic_info=demographic_info,
                accessibility=accessibility
            )
            
            # Determine strength level
            strength = self._determine_strength(total_score)
            
            # Generate rationale
            rationale = self._generate_rationale(
                type_key=type_key,
                factors=factors,
                demographic_info=demographic_info,
                accessibility=accessibility
            )
            
            result[type_name] = {
                'total_score': total_score,
                'raw_score': raw_score,
                'factors': factors,
                'strength': strength,
                'rationale': rationale
            }
        
        return result
    
    def _find_matching_score(self, type_name: str, type_demand_scores: Dict[str, float]) -> Optional[float]:
        """Find matching score from type_demand_scores dict"""
        
        # Direct match
        if type_name in type_demand_scores:
            return type_demand_scores[type_name]
        
        # Fuzzy match (handle variations like '청년' vs '청년형')
        for key, value in type_demand_scores.items():
            if type_name in key or key in type_name:
                return value
        
        return None
    
    def _convert_to_20_point_scale(self, raw_score: float) -> int:
        """
        Convert 0-100 raw score to 0-20 point scale
        
        Formula: (raw_score / 100) * 20
        """
        return int((raw_score / 100.0) * 20)
    
    def _calculate_factor_breakdown(
        self,
        type_key: str,
        raw_score: float,
        demographic_info: Dict[str, Any],
        accessibility: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Calculate factor breakdown for score
        
        Factors:
        - location: Accessibility to transportation, amenities
        - demographics: Population structure, target group ratio
        - amenities: Nearby facilities (school, hospital, etc.)
        """
        
        # Base allocation based on raw score
        total_points = int((raw_score / 100.0) * 20)
        
        # Type-specific factor weights
        weights = self._get_type_weights(type_key)
        
        # Calculate points per factor
        location_points = int(total_points * weights['location'])
        demographics_points = int(total_points * weights['demographics'])
        amenities_points = total_points - location_points - demographics_points
        
        return {
            'location': location_points,
            'demographics': demographics_points,
            'amenities': amenities_points
        }
    
    def _get_type_weights(self, type_key: str) -> Dict[str, float]:
        """Get factor weights for each housing type"""
        
        weights = {
            'youth': {
                'location': 0.50,  # 50% location (subway access critical)
                'demographics': 0.30,  # 30% demographics (youth ratio)
                'amenities': 0.20  # 20% amenities (cafes, entertainment)
            },
            'newlywed_1': {
                'location': 0.40,  # 40% location (commute to work)
                'demographics': 0.30,  # 30% demographics (young families)
                'amenities': 0.30  # 30% amenities (childcare, schools)
            },
            'newlywed_2': {
                'location': 0.35,  # 35% location
                'demographics': 0.25,  # 25% demographics
                'amenities': 0.40  # 40% amenities (schools, parks)
            },
            'multichild': {
                'location': 0.25,  # 25% location
                'demographics': 0.25,  # 25% demographics
                'amenities': 0.50  # 50% amenities (schools, hospitals critical)
            },
            'elderly': {
                'location': 0.30,  # 30% location (mobility)
                'demographics': 0.30,  # 30% demographics (elderly population)
                'amenities': 0.40  # 40% amenities (hospitals, welfare)
            }
        }
        
        return weights.get(type_key, {'location': 0.33, 'demographics': 0.33, 'amenities': 0.34})
    
    def _determine_strength(self, total_score: int) -> str:
        """
        Determine demand strength level
        
        - high: 16-20 points (80%+)
        - medium: 11-15 points (55-79%)
        - low: 0-10 points (<55%)
        """
        if total_score >= 16:
            return 'high'
        elif total_score >= 11:
            return 'medium'
        else:
            return 'low'
    
    def _generate_rationale(
        self,
        type_key: str,
        factors: Dict[str, int],
        demographic_info: Dict[str, Any],
        accessibility: Dict[str, Any]
    ) -> str:
        """
        Generate human-readable rationale for the score
        
        Returns:
            String explaining why this score was given
        """
        
        rationale_parts = []
        
        # Type-specific rationale
        if type_key == 'youth':
            subway_dist = accessibility.get('subway_distance', 9999)
            if subway_dist < 500:
                rationale_parts.append(f"지하철 {int(subway_dist)}m")
            
            youth_ratio = demographic_info.get('youth_ratio', 0)
            if youth_ratio > 0:
                rationale_parts.append(f"청년인구 {youth_ratio:.0f}%")
        
        elif type_key in ['newlywed_1', 'newlywed_2']:
            school_dist = accessibility.get('elementary_school_distance', 9999)
            if school_dist < 800:
                rationale_parts.append(f"초등학교 {int(school_dist)}m")
            
            single_ratio = demographic_info.get('single_person_ratio', 0)
            if single_ratio > 0:
                rationale_parts.append(f"1-2인 가구 {single_ratio:.0f}%")
        
        elif type_key == 'multichild':
            school_dist = accessibility.get('elementary_school_distance', 9999)
            hospital_dist = accessibility.get('hospital_distance', 9999)
            
            if school_dist < 800:
                rationale_parts.append(f"초등학교 {int(school_dist)}m")
            if hospital_dist < 1000:
                rationale_parts.append(f"병원 {int(hospital_dist)}m")
        
        elif type_key == 'elderly':
            hospital_dist = accessibility.get('hospital_distance', 9999)
            if hospital_dist < 1000:
                rationale_parts.append(f"병원 {int(hospital_dist)}m")
        
        # Default rationale if no specific factors
        if not rationale_parts:
            if factors['location'] >= 8:
                rationale_parts.append("우수한 입지")
            if factors['demographics'] >= 5:
                rationale_parts.append("적합한 인구구조")
        
        return ', '.join(rationale_parts) if rationale_parts else "종합 평가"
    
    def format_for_report(self, demand_scores: Dict[str, Dict[str, Any]]) -> str:
        """
        Format demand scores for report display
        
        Returns:
            Formatted string for report chapter
        """
        
        lines = []
        lines.append("\n### 4.2 유형별 수요 점수")
        lines.append("\n**수요분석 결과 (0-20점 만점):**\n")
        
        for type_name, data in demand_scores.items():
            strength_emoji = {
                'high': '🔥',
                'medium': '✓',
                'low': '△'
            }.get(data['strength'], '•')
            
            lines.append(f"**{strength_emoji} {type_name}**: {data['total_score']}점")
            lines.append(f"  - 입지: {data['factors']['location']}점")
            lines.append(f"  - 인구구조: {data['factors']['demographics']}점")
            lines.append(f"  - 편의시설: {data['factors']['amenities']}점")
            lines.append(f"  - 근거: {data['rationale']}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def get_summary_table(self, demand_scores: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get summary table data for visualization
        
        Returns:
            List of dicts suitable for table rendering
        """
        
        table_data = []
        
        for type_name, data in demand_scores.items():
            table_data.append({
                '유형': type_name,
                '총점': f"{data['total_score']}/20",
                '입지': data['factors']['location'],
                '인구': data['factors']['demographics'],
                '편의': data['factors']['amenities'],
                '수요강도': data['strength'],
                '근거': data['rationale']
            })
        
        return table_data


def create_ch4_scorer() -> CH4DynamicScorer:
    """
    Factory function to create CH4 dynamic scorer
    
    Returns:
        CH4DynamicScorer instance
    """
    return CH4DynamicScorer()


__all__ = [
    'CH4DynamicScorer',
    'create_ch4_scorer'
]
