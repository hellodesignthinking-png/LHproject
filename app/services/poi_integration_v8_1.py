#!/usr/bin/env python3
"""
ZeroSite v8.1 - Enhanced POI (Point of Interest) Integration Service
====================================================================

Comprehensive local facility analysis for LH feasibility reports:
- Educational facilities (schools, kindergartens)
- Transportation (bus stops, subway stations)
- Healthcare (hospitals, clinics, pharmacies)
- Commercial (supermarkets, convenience stores, shopping)
- Cultural (libraries, parks, community centers)
- Infrastructure scoring and accessibility analysis

Author: ZeroSite Development Team
Date: 2025-12-02
Version: v8.1
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import asyncio
import statistics
from datetime import datetime

from app.services.kakao_service import KakaoService
from app.schemas import Coordinates


@dataclass
class POICategory:
    """POI 카테고리 정의"""
    name: str
    search_keywords: List[str]
    search_radius: int  # meters
    weight: float  # 점수 가중치
    ideal_distance: int  # 이상적인 거리 (m)
    max_distance: int  # 최대 허용 거리 (m)


@dataclass
class FacilityScore:
    """시설 점수"""
    category: str
    count: int
    nearest_distance: float
    score: float  # 0-100
    facilities: List[Dict]
    analysis: str


@dataclass
class POIAnalysisV81:
    """v8.1 POI 종합 분석 결과"""
    
    # 교육 시설
    elementary_schools: FacilityScore
    middle_schools: FacilityScore
    high_schools: FacilityScore
    kindergartens: FacilityScore
    academies: FacilityScore
    education_score: float  # 0-100
    
    # 교통 시설
    subway_stations: FacilityScore
    bus_stops: FacilityScore
    taxi_stands: FacilityScore
    transportation_score: float  # 0-100
    
    # 의료 시설
    hospitals: FacilityScore
    clinics: FacilityScore
    pharmacies: FacilityScore
    healthcare_score: float  # 0-100
    
    # 상업 시설
    supermarkets: FacilityScore
    convenience_stores: FacilityScore
    shopping_malls: FacilityScore
    restaurants: FacilityScore
    commercial_score: float  # 0-100
    
    # 문화/여가 시설
    parks: FacilityScore
    libraries: FacilityScore
    community_centers: FacilityScore
    gyms: FacilityScore
    cultural_score: float  # 0-100
    
    # 종합 평가
    overall_infrastructure_score: float  # 0-100
    livability_grade: str  # A+/A/B+/B/C/D/F
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]


class POIIntegrationV81:
    """v8.1 Enhanced POI Integration Service"""
    
    # POI 카테고리 정의
    POI_CATEGORIES = {
        # 교육 시설
        "elementary_schools": POICategory(
            name="초등학교",
            search_keywords=["초등학교"],
            search_radius=1500,
            weight=0.25,
            ideal_distance=500,
            max_distance=1000
        ),
        "middle_schools": POICategory(
            name="중학교",
            search_keywords=["중학교"],
            search_radius=2000,
            weight=0.20,
            ideal_distance=800,
            max_distance=1500
        ),
        "high_schools": POICategory(
            name="고등학교",
            search_keywords=["고등학교"],
            search_radius=2500,
            weight=0.15,
            ideal_distance=1000,
            max_distance=2000
        ),
        "kindergartens": POICategory(
            name="유치원",
            search_keywords=["유치원", "어린이집"],
            search_radius=1000,
            weight=0.20,
            ideal_distance=300,
            max_distance=800
        ),
        "academies": POICategory(
            name="학원",
            search_keywords=["학원"],
            search_radius=1500,
            weight=0.10,
            ideal_distance=500,
            max_distance=1000
        ),
        
        # 교통 시설
        "subway_stations": POICategory(
            name="지하철역",
            search_keywords=["지하철역", "전철역"],
            search_radius=2000,
            weight=0.50,
            ideal_distance=500,
            max_distance=1500
        ),
        "bus_stops": POICategory(
            name="버스정류장",
            search_keywords=["버스정류장"],
            search_radius=500,
            weight=0.30,
            ideal_distance=200,
            max_distance=400
        ),
        "taxi_stands": POICategory(
            name="택시승강장",
            search_keywords=["택시승강장"],
            search_radius=1000,
            weight=0.10,
            ideal_distance=300,
            max_distance=800
        ),
        
        # 의료 시설
        "hospitals": POICategory(
            name="종합병원",
            search_keywords=["종합병원", "병원"],
            search_radius=3000,
            weight=0.40,
            ideal_distance=1000,
            max_distance=2500
        ),
        "clinics": POICategory(
            name="의원",
            search_keywords=["의원", "내과", "소아과"],
            search_radius=1500,
            weight=0.30,
            ideal_distance=500,
            max_distance=1000
        ),
        "pharmacies": POICategory(
            name="약국",
            search_keywords=["약국"],
            search_radius=1000,
            weight=0.20,
            ideal_distance=300,
            max_distance=800
        ),
        
        # 상업 시설
        "supermarkets": POICategory(
            name="대형마트",
            search_keywords=["이마트", "롯데마트", "홈플러스", "대형마트"],
            search_radius=2000,
            weight=0.30,
            ideal_distance=800,
            max_distance=1500
        ),
        "convenience_stores": POICategory(
            name="편의점",
            search_keywords=["편의점", "CU", "GS25", "세븐일레븐"],
            search_radius=500,
            weight=0.25,
            ideal_distance=200,
            max_distance=400
        ),
        "shopping_malls": POICategory(
            name="쇼핑몰",
            search_keywords=["쇼핑몰", "백화점"],
            search_radius=3000,
            weight=0.20,
            ideal_distance=1500,
            max_distance=2500
        ),
        "restaurants": POICategory(
            name="음식점",
            search_keywords=["음식점", "식당"],
            search_radius=1000,
            weight=0.15,
            ideal_distance=300,
            max_distance=800
        ),
        
        # 문화/여가 시설
        "parks": POICategory(
            name="공원",
            search_keywords=["공원"],
            search_radius=2000,
            weight=0.30,
            ideal_distance=500,
            max_distance=1500
        ),
        "libraries": POICategory(
            name="도서관",
            search_keywords=["도서관"],
            search_radius=2500,
            weight=0.25,
            ideal_distance=1000,
            max_distance=2000
        ),
        "community_centers": POICategory(
            name="주민센터",
            search_keywords=["주민센터", "행정복지센터"],
            search_radius=2000,
            weight=0.20,
            ideal_distance=800,
            max_distance=1500
        ),
        "gyms": POICategory(
            name="체육시설",
            search_keywords=["체육관", "헬스장", "수영장"],
            search_radius=1500,
            weight=0.15,
            ideal_distance=500,
            max_distance=1000
        ),
    }
    
    def __init__(self):
        """Initialize POI Integration Service"""
        self.kakao_service = KakaoService()
    
    async def analyze_comprehensive_poi(
        self,
        coordinates: Coordinates,
        address: str
    ) -> POIAnalysisV81:
        """
        종합 POI 분석 수행
        
        Args:
            coordinates: 대상지 좌표
            address: 대상지 주소
            
        Returns:
            POIAnalysisV81 종합 분석 결과
        """
        print(f"\n{'='*80}")
        print(f"🏙️  ZeroSite v8.1 - Comprehensive POI Analysis")
        print(f"{'='*80}")
        print(f"📍 Address: {address}")
        print(f"🌐 Coordinates: ({coordinates.latitude:.6f}, {coordinates.longitude:.6f})")
        print()
        
        # 1. 모든 카테고리별 시설 검색
        print("📊 Step 1: Searching all POI categories...")
        facility_scores = {}
        
        for category_key, category_config in self.POI_CATEGORIES.items():
            print(f"   🔍 Searching: {category_config.name}...")
            facility_score = await self._search_and_score_category(
                coordinates,
                category_config
            )
            facility_scores[category_key] = facility_score
        
        # 2. 카테고리별 종합 점수 계산
        print("\n📊 Step 2: Calculating category scores...")
        education_score = self._calculate_education_score(facility_scores)
        transportation_score = self._calculate_transportation_score(facility_scores)
        healthcare_score = self._calculate_healthcare_score(facility_scores)
        commercial_score = self._calculate_commercial_score(facility_scores)
        cultural_score = self._calculate_cultural_score(facility_scores)
        
        print(f"   ✅ Education Score: {education_score:.1f}/100")
        print(f"   ✅ Transportation Score: {transportation_score:.1f}/100")
        print(f"   ✅ Healthcare Score: {healthcare_score:.1f}/100")
        print(f"   ✅ Commercial Score: {commercial_score:.1f}/100")
        print(f"   ✅ Cultural Score: {cultural_score:.1f}/100")
        
        # 3. 전체 인프라 점수 계산
        print("\n📊 Step 3: Calculating overall infrastructure score...")
        overall_score = (
            education_score * 0.25 +
            transportation_score * 0.25 +
            healthcare_score * 0.20 +
            commercial_score * 0.15 +
            cultural_score * 0.15
        )
        
        livability_grade = self._calculate_livability_grade(overall_score)
        
        print(f"   🎯 Overall Infrastructure Score: {overall_score:.1f}/100")
        print(f"   📊 Livability Grade: {livability_grade}")
        
        # 4. 강점/약점/권고사항 분석
        print("\n📊 Step 4: Analyzing strengths and weaknesses...")
        strengths, weaknesses, recommendations = self._analyze_swot(
            facility_scores,
            education_score,
            transportation_score,
            healthcare_score,
            commercial_score,
            cultural_score
        )
        
        print(f"   ✅ Strengths: {len(strengths)}")
        print(f"   ⚠️  Weaknesses: {len(weaknesses)}")
        print(f"   💡 Recommendations: {len(recommendations)}")
        
        # 5. 결과 생성
        return POIAnalysisV81(
            # 교육 시설
            elementary_schools=facility_scores["elementary_schools"],
            middle_schools=facility_scores["middle_schools"],
            high_schools=facility_scores["high_schools"],
            kindergartens=facility_scores["kindergartens"],
            academies=facility_scores["academies"],
            education_score=education_score,
            
            # 교통 시설
            subway_stations=facility_scores["subway_stations"],
            bus_stops=facility_scores["bus_stops"],
            taxi_stands=facility_scores["taxi_stands"],
            transportation_score=transportation_score,
            
            # 의료 시설
            hospitals=facility_scores["hospitals"],
            clinics=facility_scores["clinics"],
            pharmacies=facility_scores["pharmacies"],
            healthcare_score=healthcare_score,
            
            # 상업 시설
            supermarkets=facility_scores["supermarkets"],
            convenience_stores=facility_scores["convenience_stores"],
            shopping_malls=facility_scores["shopping_malls"],
            restaurants=facility_scores["restaurants"],
            commercial_score=commercial_score,
            
            # 문화/여가 시설
            parks=facility_scores["parks"],
            libraries=facility_scores["libraries"],
            community_centers=facility_scores["community_centers"],
            gyms=facility_scores["gyms"],
            cultural_score=cultural_score,
            
            # 종합 평가
            overall_infrastructure_score=overall_score,
            livability_grade=livability_grade,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        )
    
    async def _search_and_score_category(
        self,
        coordinates: Coordinates,
        category: POICategory
    ) -> FacilityScore:
        """
        특정 카테고리의 시설 검색 및 점수 계산
        """
        all_facilities = []
        
        # 여러 키워드로 검색
        for keyword in category.search_keywords:
            facilities = await self.kakao_service.search_nearby_facilities(
                coordinates,
                keyword,
                category.search_radius
            )
            
            # 중복 제거 (이름 기준)
            for facility in facilities:
                if not any(f.name == facility.name for f in all_facilities):
                    all_facilities.append({
                        "name": facility.name,
                        "distance": facility.distance,
                        "address": facility.address,
                        "category": facility.category
                    })
        
        # 거리순 정렬
        all_facilities.sort(key=lambda x: x["distance"])
        
        # 점수 계산
        if not all_facilities:
            score = 0.0
            nearest_distance = 9999.0
            analysis = f"{category.name}이(가) 반경 {category.search_radius}m 내에 없습니다."
        else:
            nearest_distance = all_facilities[0]["distance"]
            count = len(all_facilities)
            
            # 거리 점수 (0-70점)
            if nearest_distance <= category.ideal_distance:
                distance_score = 70
            elif nearest_distance <= category.max_distance:
                distance_score = 70 * (1 - (nearest_distance - category.ideal_distance) / 
                                      (category.max_distance - category.ideal_distance))
            else:
                distance_score = 0
            
            # 개수 점수 (0-30점)
            if count >= 5:
                count_score = 30
            elif count >= 3:
                count_score = 25
            elif count >= 2:
                count_score = 20
            else:
                count_score = 15
            
            score = distance_score + count_score
            
            # 분석 텍스트
            if score >= 80:
                analysis = f"{category.name} 접근성이 매우 우수합니다. (최단거리: {nearest_distance:.0f}m, {count}개소)"
            elif score >= 60:
                analysis = f"{category.name} 접근성이 양호합니다. (최단거리: {nearest_distance:.0f}m, {count}개소)"
            elif score >= 40:
                analysis = f"{category.name} 접근성이 보통입니다. (최단거리: {nearest_distance:.0f}m, {count}개소)"
            else:
                analysis = f"{category.name} 접근성이 부족합니다. (최단거리: {nearest_distance:.0f}m, {count}개소)"
        
        return FacilityScore(
            category=category.name,
            count=len(all_facilities),
            nearest_distance=nearest_distance,
            score=score,
            facilities=all_facilities[:10],  # 상위 10개만
            analysis=analysis
        )
    
    def _calculate_education_score(self, facility_scores: Dict) -> float:
        """교육 시설 종합 점수"""
        weights = {
            "elementary_schools": 0.30,
            "middle_schools": 0.25,
            "high_schools": 0.20,
            "kindergartens": 0.15,
            "academies": 0.10
        }
        
        total_score = sum(
            facility_scores[key].score * weight
            for key, weight in weights.items()
        )
        
        return min(100, total_score)
    
    def _calculate_transportation_score(self, facility_scores: Dict) -> float:
        """교통 시설 종합 점수"""
        weights = {
            "subway_stations": 0.50,
            "bus_stops": 0.35,
            "taxi_stands": 0.15
        }
        
        total_score = sum(
            facility_scores[key].score * weight
            for key, weight in weights.items()
        )
        
        return min(100, total_score)
    
    def _calculate_healthcare_score(self, facility_scores: Dict) -> float:
        """의료 시설 종합 점수"""
        weights = {
            "hospitals": 0.40,
            "clinics": 0.35,
            "pharmacies": 0.25
        }
        
        total_score = sum(
            facility_scores[key].score * weight
            for key, weight in weights.items()
        )
        
        return min(100, total_score)
    
    def _calculate_commercial_score(self, facility_scores: Dict) -> float:
        """상업 시설 종합 점수"""
        weights = {
            "supermarkets": 0.30,
            "convenience_stores": 0.30,
            "shopping_malls": 0.20,
            "restaurants": 0.20
        }
        
        total_score = sum(
            facility_scores[key].score * weight
            for key, weight in weights.items()
        )
        
        return min(100, total_score)
    
    def _calculate_cultural_score(self, facility_scores: Dict) -> float:
        """문화/여가 시설 종합 점수"""
        weights = {
            "parks": 0.30,
            "libraries": 0.30,
            "community_centers": 0.25,
            "gyms": 0.15
        }
        
        total_score = sum(
            facility_scores[key].score * weight
            for key, weight in weights.items()
        )
        
        return min(100, total_score)
    
    def _calculate_livability_grade(self, score: float) -> str:
        """거주 적합도 등급 계산"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C"
        elif score >= 40:
            return "D"
        else:
            return "F"
    
    def _analyze_swot(
        self,
        facility_scores: Dict,
        education_score: float,
        transportation_score: float,
        healthcare_score: float,
        commercial_score: float,
        cultural_score: float
    ) -> Tuple[List[str], List[str], List[str]]:
        """강점/약점/권고사항 분석"""
        strengths = []
        weaknesses = []
        recommendations = []
        
        # 강점 분석
        if education_score >= 70:
            strengths.append(f"교육 인프라 우수 ({education_score:.1f}점) - 학교 접근성이 뛰어남")
        if transportation_score >= 70:
            strengths.append(f"교통 인프라 우수 ({transportation_score:.1f}점) - 대중교통 이용 편리")
        if healthcare_score >= 70:
            strengths.append(f"의료 인프라 우수 ({healthcare_score:.1f}점) - 의료시설 접근 용이")
        if commercial_score >= 70:
            strengths.append(f"상업 인프라 우수 ({commercial_score:.1f}점) - 생활 편의시설 풍부")
        if cultural_score >= 70:
            strengths.append(f"문화/여가 인프라 우수 ({cultural_score:.1f}점) - 여가생활 여건 양호")
        
        # 약점 분석 및 권고사항
        if education_score < 60:
            weaknesses.append(f"교육 인프라 부족 ({education_score:.1f}점)")
            recommendations.append("인근 학교 통학버스 운영 또는 교육시설 유치 검토 필요")
        
        if transportation_score < 60:
            weaknesses.append(f"교통 인프라 부족 ({transportation_score:.1f}점)")
            recommendations.append("셔틀버스 운영 또는 주차공간 확보를 통한 접근성 개선 필요")
        
        if healthcare_score < 60:
            weaknesses.append(f"의료 인프라 부족 ({healthcare_score:.1f}점)")
            recommendations.append("입주민 대상 건강검진 프로그램 또는 의료시설 유치 고려")
        
        if commercial_score < 60:
            weaknesses.append(f"상업 인프라 부족 ({commercial_score:.1f}점)")
            recommendations.append("단지 내 편의시설 또는 커뮤니티 상가 조성 검토")
        
        if cultural_score < 60:
            weaknesses.append(f"문화/여가 인프라 부족 ({cultural_score:.1f}점)")
            recommendations.append("단지 내 커뮤니티 센터, 도서관, 체육시설 등 조성 필요")
        
        # 기본 강점이 없으면 추가
        if not strengths:
            strengths.append("개발 잠재력 있는 지역으로 향후 인프라 개선 기대")
        
        # 기본 권고사항
        if not recommendations:
            recommendations.append("현재 인프라 수준 유지 및 정기적 모니터링 필요")
        
        return strengths, weaknesses, recommendations


# 테스트 실행
async def test_poi_integration():
    """POI Integration 테스트"""
    print("="*80)
    print("🧪 Testing POI Integration v8.1")
    print("="*80)
    
    # 테스트 좌표 (서울 강남구 역삼동)
    test_coords = Coordinates(latitude=37.5006, longitude=127.0366)
    test_address = "서울특별시 강남구 역삼동 123-45"
    
    # POI 분석 실행
    poi_service = POIIntegrationV81()
    result = await poi_service.analyze_comprehensive_poi(test_coords, test_address)
    
    # 결과 출력
    print("\n" + "="*80)
    print("📊 POI Analysis Results")
    print("="*80)
    print(f"\n🎓 Education Score: {result.education_score:.1f}/100")
    print(f"   - Elementary Schools: {result.elementary_schools.count}개 (최단거리: {result.elementary_schools.nearest_distance:.0f}m)")
    print(f"   - Middle Schools: {result.middle_schools.count}개 (최단거리: {result.middle_schools.nearest_distance:.0f}m)")
    
    print(f"\n🚇 Transportation Score: {result.transportation_score:.1f}/100")
    print(f"   - Subway Stations: {result.subway_stations.count}개 (최단거리: {result.subway_stations.nearest_distance:.0f}m)")
    print(f"   - Bus Stops: {result.bus_stops.count}개 (최단거리: {result.bus_stops.nearest_distance:.0f}m)")
    
    print(f"\n🏥 Healthcare Score: {result.healthcare_score:.1f}/100")
    print(f"   - Hospitals: {result.hospitals.count}개 (최단거리: {result.hospitals.nearest_distance:.0f}m)")
    
    print(f"\n🛒 Commercial Score: {result.commercial_score:.1f}/100")
    print(f"   - Supermarkets: {result.supermarkets.count}개 (최단거리: {result.supermarkets.nearest_distance:.0f}m)")
    
    print(f"\n🎭 Cultural Score: {result.cultural_score:.1f}/100")
    print(f"   - Parks: {result.parks.count}개 (최단거리: {result.parks.nearest_distance:.0f}m)")
    
    print(f"\n🎯 Overall Infrastructure Score: {result.overall_infrastructure_score:.1f}/100")
    print(f"📊 Livability Grade: {result.livability_grade}")
    
    print(f"\n✅ Strengths ({len(result.strengths)}):")
    for strength in result.strengths:
        print(f"   • {strength}")
    
    print(f"\n⚠️  Weaknesses ({len(result.weaknesses)}):")
    for weakness in result.weaknesses:
        print(f"   • {weakness}")
    
    print(f"\n💡 Recommendations ({len(result.recommendations)}):")
    for recommendation in result.recommendations:
        print(f"   • {recommendation}")
    
    print("\n" + "="*80)
    print("✅ POI Integration Test Complete!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_poi_integration())
