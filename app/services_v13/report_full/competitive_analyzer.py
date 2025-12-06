"""
Competitive Analysis Engine
============================

Phase 2, Task 2.1: Competitive Analysis (3-5 projects within 1km)

This module analyzes competitive projects within 1km radius:
- Identify 3-5 comparable LH rental housing projects
- Compare key metrics: location, price, units, amenities
- Calculate competitive positioning scores
- Generate differentiation recommendations

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0 (Phase 2)
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import math

logger = logging.getLogger(__name__)


@dataclass
class CompetitiveProject:
    """Data structure for a competitive project"""
    name: str
    distance_km: float
    housing_type: str  # 'youth', 'newlyweds', etc.
    total_units: int
    avg_rent_per_sqm: float  # 원/㎡
    avg_unit_size_sqm: float
    occupancy_rate: float  # 0-100%
    completion_year: int
    amenities_score: int  # 0-100
    transportation_score: int  # 0-100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'distance_km': self.distance_km,
            'housing_type': self.housing_type,
            'housing_type_kr': self._translate_type(),
            'total_units': self.total_units,
            'avg_rent_per_sqm': self.avg_rent_per_sqm,
            'avg_rent_per_sqm_kr': f"{self.avg_rent_per_sqm:,.0f}원/㎡",
            'avg_unit_size_sqm': self.avg_unit_size_sqm,
            'occupancy_rate': self.occupancy_rate,
            'completion_year': self.completion_year,
            'amenities_score': self.amenities_score,
            'transportation_score': self.transportation_score,
            'age_years': datetime.now().year - self.completion_year
        }
    
    def _translate_type(self) -> str:
        """Translate housing type to Korean"""
        type_map = {
            'youth': '청년형',
            'newlyweds': '신혼부부형',
            'newlyweds_growth': '신혼부부 성장형',
            'multichild': '다자녀형',
            'senior': '고령자형'
        }
        return type_map.get(self.housing_type, self.housing_type)


class CompetitiveAnalyzer:
    """
    Analyze competitive projects within 1km radius
    
    Phase 2, Task 2.1: Competitive Analysis
    """
    
    def __init__(self):
        """Initialize competitive analyzer"""
        self.search_radius_km = 1.0  # 1km radius
        logger.info("✅ CompetitiveAnalyzer initialized")
    
    def analyze_competition(
        self,
        address: str,
        coordinates: Optional[Tuple[float, float]],
        project_housing_type: str,
        project_avg_rent: float
    ) -> Dict[str, Any]:
        """
        Analyze competitive projects within 1km
        
        Args:
            address: Project address
            coordinates: (lat, lon) tuple
            project_housing_type: Our project's housing type
            project_avg_rent: Our project's average rent per sqm
        
        Returns:
            Competitive analysis results with 3-5 projects
        """
        logger.info(f"🔍 Analyzing competition for {address}")
        
        # Step 1: Find competitive projects within 1km
        # In production, this would query a database or API
        competitive_projects = self._find_nearby_projects(
            address, 
            coordinates, 
            project_housing_type
        )
        
        # Step 2: Calculate competitive metrics
        analysis = {
            'total_competitors': len(competitive_projects),
            'projects': [proj.to_dict() for proj in competitive_projects],
            'market_statistics': self._calculate_market_stats(competitive_projects),
            'positioning': self._calculate_positioning(
                project_avg_rent,
                project_housing_type,
                competitive_projects
            ),
            'competitive_intensity': self._assess_competitive_intensity(
                competitive_projects
            ),
            'recommendations': self._generate_recommendations(
                project_avg_rent,
                project_housing_type,
                competitive_projects
            )
        }
        
        logger.info(f"✅ Competition analysis complete: {len(competitive_projects)} competitors found")
        return analysis
    
    def _find_nearby_projects(
        self,
        address: str,
        coordinates: Optional[Tuple[float, float]],
        housing_type: str
    ) -> List[CompetitiveProject]:
        """
        Find 3-5 competitive projects within 1km
        
        In production, this would:
        1. Query LH public housing database
        2. Filter by distance (1km radius)
        3. Filter by housing type (same or similar)
        4. Rank by relevance
        
        For now, generate realistic mock data
        """
        # Extract region from address
        region = self._extract_region(address)
        
        # Generate 3-5 realistic competitive projects
        # In production: Replace with actual API/database query
        projects = []
        
        # Project 1: Nearby Youth Housing
        if housing_type in ['youth', 'newlyweds']:
            projects.append(CompetitiveProject(
                name=f"{region} LH 청년주택 A동",
                distance_km=0.3,
                housing_type='youth',
                total_units=120,
                avg_rent_per_sqm=8500,
                avg_unit_size_sqm=36.0,
                occupancy_rate=96.5,
                completion_year=2021,
                amenities_score=78,
                transportation_score=85
            ))
        
        # Project 2: Similar Type Housing
        projects.append(CompetitiveProject(
            name=f"{region} LH {self._translate_type(housing_type)} B동",
            distance_km=0.6,
            housing_type=housing_type,
            total_units=95,
            avg_rent_per_sqm=9200,
            avg_unit_size_sqm=42.0,
            occupancy_rate=92.3,
            completion_year=2020,
            amenities_score=72,
            transportation_score=80
        ))
        
        # Project 3: Older Competitor
        projects.append(CompetitiveProject(
            name=f"{region} LH 매입임대 C동",
            distance_km=0.8,
            housing_type=housing_type,
            total_units=78,
            avg_rent_per_sqm=7800,
            avg_unit_size_sqm=38.0,
            occupancy_rate=88.7,
            completion_year=2018,
            amenities_score=65,
            transportation_score=75
        ))
        
        # Project 4: Premium Competitor (if applicable)
        if region in ['서울', '서울시']:
            projects.append(CompetitiveProject(
                name=f"{region} LH 신축매입임대 D동",
                distance_km=0.9,
                housing_type=housing_type,
                total_units=140,
                avg_rent_per_sqm=10500,
                avg_unit_size_sqm=45.0,
                occupancy_rate=97.8,
                completion_year=2022,
                amenities_score=88,
                transportation_score=92
            ))
        
        # Limit to 3-5 projects
        return projects[:5] if len(projects) > 5 else projects
    
    def _calculate_market_stats(
        self, 
        projects: List[CompetitiveProject]
    ) -> Dict[str, Any]:
        """Calculate market-level statistics"""
        if not projects:
            return {}
        
        rents = [p.avg_rent_per_sqm for p in projects]
        occupancy_rates = [p.occupancy_rate for p in projects]
        unit_sizes = [p.avg_unit_size_sqm for p in projects]
        
        return {
            'avg_rent_per_sqm': sum(rents) / len(rents),
            'avg_rent_per_sqm_kr': f"{sum(rents) / len(rents):,.0f}원/㎡",
            'min_rent_per_sqm': min(rents),
            'max_rent_per_sqm': max(rents),
            'avg_occupancy_rate': sum(occupancy_rates) / len(occupancy_rates),
            'avg_unit_size_sqm': sum(unit_sizes) / len(unit_sizes),
            'total_competing_units': sum(p.total_units for p in projects),
            'market_saturation': self._calculate_saturation(projects)
        }
    
    def _calculate_saturation(self, projects: List[CompetitiveProject]) -> str:
        """Calculate market saturation level"""
        total_units = sum(p.total_units for p in projects)
        avg_occupancy = sum(p.occupancy_rate for p in projects) / len(projects) if projects else 0
        
        if total_units < 200 and avg_occupancy >= 95:
            return "LOW"  # Under-supplied
        elif total_units < 400 and avg_occupancy >= 90:
            return "MEDIUM"  # Balanced
        else:
            return "HIGH"  # Over-supplied
    
    def _calculate_positioning(
        self,
        project_rent: float,
        project_type: str,
        competitors: List[CompetitiveProject]
    ) -> Dict[str, Any]:
        """Calculate our project's competitive positioning"""
        if not competitors:
            return {
                'price_position': 'UNKNOWN',
                'percentile': 50.0,
                'description': '경쟁 정보 부족'
            }
        
        market_avg_rent = sum(p.avg_rent_per_sqm for p in competitors) / len(competitors)
        
        # Price position
        rent_ratio = project_rent / market_avg_rent if market_avg_rent > 0 else 1.0
        
        if rent_ratio < 0.90:
            price_position = 'ECONOMY'
            price_desc = '저가형 (시장 대비 10% 이상 저렴)'
        elif rent_ratio < 0.98:
            price_position = 'VALUE'
            price_desc = '가치형 (시장 대비 약간 저렴)'
        elif rent_ratio <= 1.02:
            price_position = 'MARKET'
            price_desc = '시장가형 (시장 평균 수준)'
        elif rent_ratio <= 1.10:
            price_position = 'PREMIUM'
            price_desc = '프리미엄형 (시장 대비 약간 비쌈)'
        else:
            price_position = 'LUXURY'
            price_desc = '고급형 (시장 대비 10% 이상 비쌈)'
        
        # Calculate percentile (where do we rank?)
        all_rents = sorted([p.avg_rent_per_sqm for p in competitors] + [project_rent])
        our_rank = all_rents.index(project_rent)
        percentile = (our_rank / len(all_rents)) * 100
        
        return {
            'price_position': price_position,
            'price_position_kr': price_desc,
            'market_avg_rent': market_avg_rent,
            'market_avg_rent_kr': f"{market_avg_rent:,.0f}원/㎡",
            'our_rent': project_rent,
            'our_rent_kr': f"{project_rent:,.0f}원/㎡",
            'rent_ratio': rent_ratio,
            'rent_difference_pct': (rent_ratio - 1.0) * 100,
            'percentile': percentile,
            'rank': f"{our_rank + 1}/{len(all_rents)}",
            'description': f"시장 내 {percentile:.0f} 퍼센타일 위치"
        }
    
    def _assess_competitive_intensity(
        self, 
        competitors: List[CompetitiveProject]
    ) -> Dict[str, Any]:
        """Assess overall competitive intensity"""
        if not competitors:
            return {
                'level': 'LOW',
                'score': 30.0,
                'description': '경쟁 미미'
            }
        
        # Factors for intensity score
        competitor_count_score = min(len(competitors) * 15, 50)  # Max 50 points
        
        avg_occupancy = sum(p.occupancy_rate for p in competitors) / len(competitors)
        occupancy_score = avg_occupancy / 2  # 0-50 points
        
        # Recent competitors (built after 2020)
        recent_competitors = sum(1 for p in competitors if p.completion_year >= 2020)
        recency_score = recent_competitors * 10  # Max 50 points
        
        intensity_score = (competitor_count_score + occupancy_score + recency_score) / 3
        
        if intensity_score >= 70:
            level = 'VERY_HIGH'
            description = '매우 높은 경쟁 강도 - 시장 진입 어려움 예상'
        elif intensity_score >= 55:
            level = 'HIGH'
            description = '높은 경쟁 강도 - 차별화 전략 필수'
        elif intensity_score >= 40:
            level = 'MEDIUM'
            description = '중간 경쟁 강도 - 적절한 시장 경쟁'
        else:
            level = 'LOW'
            description = '낮은 경쟁 강도 - 시장 진입 유리'
        
        return {
            'level': level,
            'level_kr': description,
            'score': round(intensity_score, 1),
            'factors': {
                'competitor_count': len(competitors),
                'avg_occupancy': round(avg_occupancy, 1),
                'recent_competitors': recent_competitors
            }
        }
    
    def _generate_recommendations(
        self,
        project_rent: float,
        project_type: str,
        competitors: List[CompetitiveProject]
    ) -> List[str]:
        """Generate competitive strategy recommendations"""
        if not competitors:
            return [
                "경쟁사 정보 부족으로 세부 전략 수립 제한",
                "시장 조사를 통한 경쟁 현황 파악 필요",
                "1km 반경 내 LH 매입임대 프로젝트 조사 권장"
            ]
        
        recommendations = []
        
        market_avg = sum(p.avg_rent_per_sqm for p in competitors) / len(competitors)
        rent_ratio = project_rent / market_avg if market_avg > 0 else 1.0
        
        # Recommendation 1: Price Strategy
        if rent_ratio < 0.95:
            recommendations.append(
                f"가격 경쟁력 우수 (시장 대비 {(1-rent_ratio)*100:.1f}% 저렴). "
                f"가성비 마케팅 전략 추진 권장"
            )
        elif rent_ratio > 1.05:
            recommendations.append(
                f"가격이 시장 대비 높음 ({(rent_ratio-1)*100:.1f}% 프리미엄). "
                f"프리미엄 서비스 또는 차별화된 가치 제공 필수"
            )
        else:
            recommendations.append(
                "시장 평균 가격대. 서비스 품질과 편의시설로 차별화 필요"
            )
        
        # Recommendation 2: Occupancy Analysis
        avg_occupancy = sum(p.occupancy_rate for p in competitors) / len(competitors)
        if avg_occupancy >= 95:
            recommendations.append(
                f"높은 시장 입주율 ({avg_occupancy:.1f}%). 수요가 충분하여 성공 가능성 높음"
            )
        elif avg_occupancy >= 90:
            recommendations.append(
                f"양호한 시장 입주율 ({avg_occupancy:.1f}%). 안정적인 수요 예상"
            )
        else:
            recommendations.append(
                f"낮은 시장 입주율 ({avg_occupancy:.1f}%). 공급 과잉 우려, 차별화 전략 필수"
            )
        
        # Recommendation 3: Competitive Differentiation
        high_quality_competitors = [p for p in competitors if p.amenities_score >= 80]
        if high_quality_competitors:
            recommendations.append(
                f"고품질 경쟁사 {len(high_quality_competitors)}개 존재. "
                f"편의시설 및 주거 서비스 강화 필요"
            )
        else:
            recommendations.append(
                "경쟁사 대비 편의시설 차별화 기회 존재. 우수한 커뮤니티 시설 확보 권장"
            )
        
        return recommendations
    
    def _translate_type(self, housing_type: str) -> str:
        """Translate housing type to Korean"""
        type_map = {
            'youth': '청년주택',
            'newlyweds': '신혼부부주택',
            'newlyweds_growth': '신혼부부 성장형',
            'multichild': '다자녀주택',
            'senior': '고령자주택'
        }
        return type_map.get(housing_type, housing_type)
    
    def _extract_region(self, address: str) -> str:
        """Extract region name from address"""
        if '서울' in address:
            # Extract district (구)
            parts = address.split()
            for part in parts:
                if '구' in part:
                    return part.replace('구', '')
            return '서울'
        elif '경기' in address:
            return '경기'
        elif '인천' in address:
            return '인천'
        else:
            return '기타'
