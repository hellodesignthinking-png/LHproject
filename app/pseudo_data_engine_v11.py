"""
ZeroSite v11.0 - Pseudo-Data Auto-Fill Engine
==============================================
실제와 유사한 시설·인구통계·거리 데이터를 자동 생성하는 엔진

주요 기능:
1. 주소 기반 주변 시설 자동 생성 (학교, 병원, 편의시설 등)
2. 인구통계 데이터 생성 (연령대별, 가구유형별)
3. 거리 매트릭스 생성 (시설까지의 거리)
4. 교통 접근성 데이터 생성 (지하철역, 버스정류장)
5. 생활권 분석 데이터 (10분 생활권, 30분 출퇴근권)
"""

from typing import Dict, Any, List, Tuple
import random
import math


class PseudoDataEngine:
    """실제와 유사한 데이터 자동 생성 엔진"""
    
    def __init__(self, address: str, coord: Dict[str, float]):
        self.address = address
        self.latitude = coord.get("latitude", 37.5665)
        self.longitude = coord.get("longitude", 126.9780)
        self._region_type = self._classify_region(address)
    
    def _classify_region(self, address: str) -> str:
        """지역 분류 (도심/부도심/외곽)"""
        if any(district in address for district in ["강남", "서초", "송파", "종로", "중구", "용산"]):
            return "도심"
        elif any(district in address for district in ["마포", "성동", "영등포", "동작", "관악"]):
            return "부도심"
        else:
            return "외곽"
    
    # ============================================================
    # 1. 교육 시설 생성
    # ============================================================
    
    def generate_education_facilities(self) -> Dict[str, Any]:
        """교육 시설 데이터 생성"""
        region_multiplier = {
            "도심": 1.2,
            "부도심": 1.0,
            "외곽": 0.7
        }[self._region_type]
        
        # 초등학교
        elementary_count = int(random.randint(3, 7) * region_multiplier)
        elementary_list = [
            f"{self._get_district()}초등학교", f"{self._get_district()}제{i}초등학교"
            for i in range(1, elementary_count)
        ][:elementary_count]
        
        # 중학교
        middle_count = int(random.randint(2, 5) * region_multiplier)
        middle_list = [
            f"{self._get_district()}중학교", f"{self._get_district()}제{i}중학교"
            for i in range(1, middle_count)
        ][:middle_count]
        
        # 고등학교
        high_count = int(random.randint(1, 4) * region_multiplier)
        high_list = [
            f"{self._get_district()}고등학교", f"{self._get_district()}제{i}고등학교"
            for i in range(1, high_count)
        ][:high_count]
        
        # 대학교 (특정 지역만)
        universities = []
        if "마포" in self.address or "서대문" in self.address:
            universities = ["홍익대학교", "서강대학교", "연세대학교"]
        elif "강남" in self.address:
            universities = ["건국대학교", "한양대학교"]
        elif "성북" in self.address or "동대문" in self.address:
            universities = ["고려대학교", "한국외국어대학교", "경희대학교"]
        
        return {
            "elementary": {
                "count": elementary_count,
                "names": elementary_list,
                "nearest_distance": f"{random.randint(300, 800)}m",
                "avg_distance": f"{random.randint(500, 1200)}m"
            },
            "middle": {
                "count": middle_count,
                "names": middle_list,
                "nearest_distance": f"{random.randint(400, 1000)}m",
                "avg_distance": f"{random.randint(600, 1500)}m"
            },
            "high": {
                "count": high_count,
                "names": high_list,
                "nearest_distance": f"{random.randint(500, 1200)}m",
                "avg_distance": f"{random.randint(800, 2000)}m"
            },
            "university": {
                "count": len(universities),
                "names": universities,
                "nearest_distance": f"{random.randint(1000, 3000)}m" if universities else "N/A",
                "avg_distance": f"{random.randint(2000, 5000)}m" if universities else "N/A"
            }
        }
    
    # ============================================================
    # 2. 의료 시설 생성
    # ============================================================
    
    def generate_medical_facilities(self) -> Dict[str, Any]:
        """의료 시설 데이터 생성"""
        region_multiplier = {
            "도심": 1.5,
            "부도심": 1.0,
            "외곽": 0.6
        }[self._region_type]
        
        # 종합병원
        hospital_count = int(random.randint(1, 4) * region_multiplier)
        hospital_list = []
        
        if self._region_type == "도심":
            hospital_list = ["서울대병원", "삼성서울병원", "아산병원", "세브란스병원"][:hospital_count]
        elif self._region_type == "부도심":
            hospital_list = [f"{self._get_district()}병원", f"{self._get_district()}의료원", "○○성모병원"][:hospital_count]
        else:
            hospital_list = [f"{self._get_district()}병원", f"{self._get_district()}보건소"][:hospital_count]
        
        # 의원/클리닉
        clinic_count = int(random.randint(15, 35) * region_multiplier)
        
        # 약국
        pharmacy_count = int(random.randint(10, 25) * region_multiplier)
        
        # 노인복지시설
        senior_facility_count = int(random.randint(2, 6) * region_multiplier)
        senior_facilities = [
            f"{self._get_district()}노인복지관", f"{self._get_district()}경로당", 
            f"{self._get_district()}데이케어센터", "실버타운"
        ][:senior_facility_count]
        
        return {
            "general_hospitals": {
                "count": hospital_count,
                "names": hospital_list,
                "nearest_distance": f"{random.randint(800, 2500)}m",
                "avg_distance": f"{random.randint(1500, 4000)}m"
            },
            "clinics": {
                "count": clinic_count,
                "nearest_distance": f"{random.randint(100, 400)}m",
                "avg_distance": f"{random.randint(200, 800)}m"
            },
            "pharmacies": {
                "count": pharmacy_count,
                "nearest_distance": f"{random.randint(150, 500)}m",
                "avg_distance": f"{random.randint(300, 900)}m"
            },
            "senior_care": {
                "count": senior_facility_count,
                "names": senior_facilities,
                "nearest_distance": f"{random.randint(500, 1500)}m",
                "avg_distance": f"{random.randint(1000, 2500)}m"
            }
        }
    
    # ============================================================
    # 3. 교통 시설 생성
    # ============================================================
    
    def generate_transportation(self) -> Dict[str, Any]:
        """교통 시설 데이터 생성"""
        # 지하철역
        subway_lines = []
        if "강남" in self.address:
            subway_lines = ["2호선", "신분당선", "9호선"]
        elif "마포" in self.address:
            subway_lines = ["2호선", "5호선", "6호선", "경의중앙선"]
        elif "용산" in self.address:
            subway_lines = ["1호선", "4호선", "경의중앙선"]
        else:
            available_lines = ["1호선", "2호선", "3호선", "4호선", "5호선", "6호선", "7호선", "8호선"]
            subway_lines = random.sample(available_lines, k=min(2, len(available_lines)))
        
        nearest_station = f"{self._get_district()}역" if random.random() > 0.3 else f"{self._get_district()}시장역"
        station_distance = random.randint(300, 1200)
        
        # 버스 노선
        bus_count = random.randint(15, 35)
        bus_types = {
            "간선": random.randint(5, 12),
            "지선": random.randint(4, 10),
            "광역": random.randint(2, 8),
            "마을": random.randint(1, 5)
        }
        
        # 버스 정류장
        bus_stop_count = random.randint(8, 15)
        nearest_bus_stop = f"{self._get_district()}사거리"
        
        return {
            "subway": {
                "lines": subway_lines,
                "nearest_station": nearest_station,
                "distance": f"{station_distance}m",
                "walking_time": f"{int(station_distance / 70)}분"  # 보행 속도 70m/분
            },
            "bus": {
                "total_routes": bus_count,
                "types": bus_types,
                "nearest_stop": nearest_bus_stop,
                "distance": f"{random.randint(100, 400)}m",
                "stops_within_500m": random.randint(3, 8)
            },
            "accessibility_score": self._calculate_transport_score(subway_lines, bus_count, station_distance)
        }
    
    def _calculate_transport_score(self, subway_lines: List[str], bus_count: int, station_distance: int) -> int:
        """교통 접근성 점수 계산"""
        score = 0
        
        # 지하철 노선 수 (최대 40점)
        score += min(len(subway_lines) * 15, 40)
        
        # 버스 노선 수 (최대 30점)
        score += min(bus_count * 1, 30)
        
        # 역 거리 (최대 30점)
        if station_distance <= 500:
            score += 30
        elif station_distance <= 800:
            score += 20
        elif station_distance <= 1200:
            score += 10
        
        return min(score, 100)
    
    # ============================================================
    # 4. 생활편의시설 생성
    # ============================================================
    
    def generate_convenience_facilities(self) -> Dict[str, Any]:
        """생활편의시설 데이터 생성"""
        region_multiplier = {
            "도심": 1.5,
            "부도심": 1.0,
            "외곽": 0.7
        }[self._region_type]
        
        # 대형마트
        mart_count = int(random.randint(1, 4) * region_multiplier)
        mart_list = []
        if mart_count >= 1:
            mart_chains = ["이마트", "롯데마트", "홈플러스", "코스트코"]
            mart_list = random.sample(mart_chains, k=min(mart_count, len(mart_chains)))
        
        # 편의점
        convenience_count = int(random.randint(20, 50) * region_multiplier)
        
        # 카페/식당
        cafe_count = int(random.randint(30, 80) * region_multiplier)
        restaurant_count = int(random.randint(50, 150) * region_multiplier)
        
        # 문화시설
        cinema_count = int(random.randint(1, 4) * region_multiplier)
        library_count = int(random.randint(1, 3) * region_multiplier)
        
        # 공원/체육시설
        park_count = int(random.randint(3, 10) * region_multiplier)
        gym_count = int(random.randint(2, 8) * region_multiplier)
        
        return {
            "shopping": {
                "large_marts": {"count": mart_count, "names": mart_list, "nearest": f"{random.randint(500, 2000)}m"},
                "convenience_stores": {"count": convenience_count, "nearest": f"{random.randint(50, 200)}m"},
                "traditional_market": {"exists": random.random() > 0.4, "distance": f"{random.randint(800, 1500)}m"}
            },
            "dining": {
                "cafes": {"count": cafe_count, "nearest": f"{random.randint(100, 400)}m"},
                "restaurants": {"count": restaurant_count, "nearest": f"{random.randint(100, 300)}m"}
            },
            "culture": {
                "cinemas": {"count": cinema_count, "nearest": f"{random.randint(1000, 3000)}m"},
                "libraries": {"count": library_count, "nearest": f"{random.randint(500, 1500)}m"}
            },
            "recreation": {
                "parks": {"count": park_count, "nearest": f"{random.randint(300, 1000)}m"},
                "sports_facilities": {"count": gym_count, "nearest": f"{random.randint(400, 1200)}m"}
            }
        }
    
    # ============================================================
    # 5. 인구통계 생성
    # ============================================================
    
    def generate_demographics(self) -> Dict[str, Any]:
        """인구통계 데이터 생성"""
        # 지역별 특성 반영
        if self._region_type == "도심":
            youth_ratio = random.uniform(28, 35)
            newlywed_ratio = random.uniform(20, 26)
            senior_ratio = random.uniform(10, 15)
        elif self._region_type == "부도심":
            youth_ratio = random.uniform(22, 28)
            newlywed_ratio = random.uniform(18, 23)
            senior_ratio = random.uniform(14, 18)
        else:  # 외곽
            youth_ratio = random.uniform(15, 22)
            newlywed_ratio = random.uniform(14, 19)
            senior_ratio = random.uniform(18, 25)
        
        general_ratio = 100 - youth_ratio - newlywed_ratio - senior_ratio
        
        # 가구 구조
        single_household = random.uniform(30, 40)
        couple_household = random.uniform(15, 22)
        nuclear_family = random.uniform(25, 32)
        extended_family = 100 - single_household - couple_household - nuclear_family
        
        # 소득 수준
        if self._region_type == "도심":
            median_income = random.randint(5500, 7000)
        elif self._region_type == "부도심":
            median_income = random.randint(4500, 5800)
        else:
            median_income = random.randint(3800, 5000)
        
        return {
            "age_distribution": {
                "youth_19_34": round(youth_ratio, 1),
                "newlywed_estimated": round(newlywed_ratio, 1),
                "senior_65_plus": round(senior_ratio, 1),
                "general_other": round(general_ratio, 1)
            },
            "household_structure": {
                "single_household": round(single_household, 1),
                "couple_household": round(couple_household, 1),
                "nuclear_family": round(nuclear_family, 1),
                "extended_family": round(extended_family, 1),
                "avg_household_size": round(random.uniform(2.1, 2.6), 1)
            },
            "economic_status": {
                "median_monthly_income": f"{median_income}만원",
                "low_income_ratio": round(random.uniform(12, 22), 1),
                "middle_income_ratio": round(random.uniform(55, 68), 1),
                "high_income_ratio": round(random.uniform(15, 25), 1)
            }
        }
    
    # ============================================================
    # 6. 청년 특화 시설 생성
    # ============================================================
    
    def generate_youth_facilities(self) -> Dict[str, Any]:
        """청년 특화 시설 데이터 생성"""
        has_youth_hub = random.random() > 0.6
        
        youth_centers = []
        if has_youth_hub:
            if "마포" in self.address:
                youth_centers = ["마포청년나루", "서울청년센터"]
            elif "강남" in self.address:
                youth_centers = ["강남청년센터", "서초청년센터"]
            else:
                youth_centers = [f"{self._get_district()}청년센터"]
        
        # IT/스타트업 밸리
        has_startup_valley = False
        startup_areas = []
        if "강남" in self.address or "테헤란" in self.address:
            has_startup_valley = True
            startup_areas = ["테헤란로 스타트업 밸리", "역삼 IT 클러스터"]
        elif "마포" in self.address:
            has_startup_valley = True
            startup_areas = ["상암 디지털미디어시티", "홍대 스타트업 거리"]
        
        return {
            "youth_support": {
                "youth_centers": youth_centers,
                "count": len(youth_centers),
                "nearest_distance": f"{random.randint(1000, 3000)}m" if youth_centers else "N/A"
            },
            "job_opportunities": {
                "startup_valley": has_startup_valley,
                "areas": startup_areas,
                "major_employers": random.randint(50, 200) if has_startup_valley else 0
            },
            "cultural_spots": {
                "cinemas": random.randint(3, 8),
                "concert_halls": random.randint(1, 4),
                "art_galleries": random.randint(2, 6)
            }
        }
    
    # ============================================================
    # 7. 고령자 특화 시설 생성
    # ============================================================
    
    def generate_senior_facilities(self) -> Dict[str, Any]:
        """고령자 특화 시설 데이터 생성"""
        region_multiplier = {
            "도심": 1.2,
            "부도심": 1.0,
            "외곽": 1.3  # 외곽일수록 고령자 시설 많음
        }[self._region_type]
        
        # 노인복지관
        welfare_center_count = int(random.randint(2, 5) * region_multiplier)
        welfare_centers = [f"{self._get_district()}노인복지관{i if i > 1 else ''}" for i in range(1, welfare_center_count + 1)]
        
        # 경로당
        senior_hall_count = int(random.randint(8, 20) * region_multiplier)
        
        # 데이케어센터
        daycare_count = int(random.randint(3, 8) * region_multiplier)
        
        return {
            "welfare_facilities": {
                "welfare_centers": {"count": welfare_center_count, "names": welfare_centers},
                "senior_halls": {"count": senior_hall_count},
                "daycare_centers": {"count": daycare_count},
                "nearest_distance": f"{random.randint(400, 1200)}m"
            },
            "medical_accessibility": {
                "hospitals_with_geriatrics": random.randint(1, 4),
                "senior_clinics": random.randint(5, 15),
                "nearest_distance": f"{random.randint(500, 1500)}m"
            },
            "barrier_free": {
                "accessible_sidewalks": random.randint(70, 95),  # %
                "elevator_buildings": random.randint(60, 85),  # %
                "senior_friendly_score": random.randint(72, 92)
            }
        }
    
    # ============================================================
    # 헬퍼 메서드
    # ============================================================
    
    def _get_district(self) -> str:
        """주소에서 구 이름 추출"""
        districts = ["강남구", "서초구", "송파구", "강동구", "마포구", "용산구", 
                    "성동구", "광진구", "노원구", "강북구", "도봉구", "은평구"]
        
        for district in districts:
            if district in self.address:
                return district.replace("구", "")
        
        # 기본값
        return "○○"
    
    # ============================================================
    # 종합 리포트 생성
    # ============================================================
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """모든 데이터를 종합하여 리포트 생성"""
        return {
            "education": self.generate_education_facilities(),
            "medical": self.generate_medical_facilities(),
            "transportation": self.generate_transportation(),
            "convenience": self.generate_convenience_facilities(),
            "demographics": self.generate_demographics(),
            "youth_specific": self.generate_youth_facilities(),
            "senior_specific": self.generate_senior_facilities(),
            "region_type": self._region_type
        }


# ============================================================
# 사용 예시
# ============================================================

if __name__ == "__main__":
    # 테스트
    engine = PseudoDataEngine(
        address="서울특별시 마포구 월드컵북로 120",
        coord={"latitude": 37.563945, "longitude": 126.913344}
    )
    
    report = engine.generate_comprehensive_report()
    
    import json
    print(json.dumps(report, ensure_ascii=False, indent=2))
