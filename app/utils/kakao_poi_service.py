"""
Kakao Local API - POI (Point of Interest) Service
실제 POI 데이터 조회 서비스
"""

import requests
from typing import List, Dict, Optional
from app.config_v30 import config_v30


class KakaoPOIService:
    """Kakao Local API를 사용한 POI 검색"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config_v30.KAKAO_REST_API_KEY
        self.search_url = "https://dapi.kakao.com/v2/local/search/category.json"
        
        # POI 카테고리 코드 (Kakao API 표준)
        self.categories = {
            "subway": "SW8",  # 지하철역
            "bus": "BK9",  # 버스정류장
            "school_elementary": "SC4",  # 초등학교
            "school_middle": "SC5",  # 중학교
            "school_high": "SC6",  # 고등학교
            "hospital": "HP8",  # 병원
            "pharmacy": "PM9",  # 약국
            "mart": "MT1",  # 대형마트
            "convenience": "CS2",  # 편의점
            "cafe": "CE7",  # 카페
            "bank": "BK9",  # 은행
            "park": "AT4",  # 공원
        }
    
    def search_nearby_poi(
        self,
        lat: float,
        lng: float,
        category: str,
        radius: int = 1000,
        limit: int = 5
    ) -> List[Dict]:
        """
        주변 POI 검색
        
        Args:
            lat: 위도
            lng: 경도
            category: 카테고리 (subway, hospital, school_elementary 등)
            radius: 반경 (미터, 최대 20000)
            limit: 결과 수 (최대 15)
        
        Returns:
            List of POI dicts with name, address, distance, lat, lng
        """
        
        category_code = self.categories.get(category)
        if not category_code:
            print(f"⚠️ Unknown category: {category}")
            return []
        
        headers = {
            "Authorization": f"KakaoAK {self.api_key}"
        }
        
        params = {
            "category_group_code": category_code,
            "x": lng,
            "y": lat,
            "radius": min(radius, 20000),
            "size": min(limit, 15),
            "sort": "distance"  # 거리순 정렬
        }
        
        try:
            response = requests.get(
                self.search_url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get('documents', [])
                
                results = []
                for doc in documents:
                    results.append({
                        "name": doc.get('place_name', ''),
                        "address": doc.get('address_name', ''),
                        "road_address": doc.get('road_address_name', ''),
                        "distance": int(doc.get('distance', 0)),  # 미터
                        "lat": float(doc.get('y', 0)),
                        "lng": float(doc.get('x', 0)),
                        "category": category
                    })
                
                return results
            else:
                print(f"❌ Kakao POI API error: {response.status_code}")
                return []
        
        except Exception as e:
            print(f"❌ Kakao POI API exception: {e}")
            return []
    
    def get_comprehensive_poi_analysis(
        self,
        lat: float,
        lng: float
    ) -> Dict[str, List[Dict]]:
        """
        포괄적 POI 분석 (주요 시설 모두 조회)
        
        Returns:
            Dict with category keys and POI lists
        """
        
        results = {}
        
        # 주요 카테고리만 조회 (API 호출 최소화)
        key_categories = [
            ("subway", 2000, 3),  # 지하철역 2km 내 3개
            ("school_elementary", 1000, 2),  # 초등학교 1km 내 2개
            ("hospital", 1500, 2),  # 병원 1.5km 내 2개
            ("mart", 2000, 2),  # 마트 2km 내 2개
            ("convenience", 500, 3),  # 편의점 500m 내 3개
        ]
        
        for category, radius, limit in key_categories:
            pois = self.search_nearby_poi(lat, lng, category, radius, limit)
            if pois:
                results[category] = pois
        
        return results


def generate_poi_table_data(poi_analysis: Dict[str, List[Dict]]) -> List[Dict]:
    """
    POI 분석 결과를 테이블 형식으로 변환
    
    Returns:
        List of dicts with category, name, distance, walking_time
    """
    
    category_names = {
        "subway": "🚇 지하철역",
        "school_elementary": "🏫 초등학교",
        "hospital": "🏥 병원",
        "mart": "🏪 마트",
        "convenience": "🏬 편의점"
    }
    
    table_data = []
    
    for category, pois in poi_analysis.items():
        for poi in pois:
            # 도보 시간 계산 (80m/분 기준)
            distance_m = poi['distance']
            walking_time = int(distance_m / 80)
            
            table_data.append({
                "category": category_names.get(category, category),
                "name": poi['name'],
                "distance_m": distance_m,
                "distance_km": round(distance_m / 1000, 2),
                "walking_time": walking_time,
                "address": poi.get('address', '')
            })
    
    return table_data


# Example usage
if __name__ == "__main__":
    service = KakaoPOIService()
    
    # Test coordinates (서울특별시 강남구 역삼동)
    lat, lng = 37.497942, 127.027619
    
    print(f"\n{'='*60}")
    print(f"Kakao Local API POI Test")
    print(f"{'='*60}")
    print(f"Coordinates: {lat}, {lng}")
    
    # Search subway stations
    subways = service.search_nearby_poi(lat, lng, "subway", radius=2000, limit=3)
    
    if subways:
        print(f"\n✅ Found {len(subways)} subway stations:")
        for s in subways:
            print(f"   - {s['name']}: {s['distance']}m")
    else:
        print(f"\n❌ No subway stations found")
    
    # Comprehensive analysis
    poi_analysis = service.get_comprehensive_poi_analysis(lat, lng)
    
    if poi_analysis:
        print(f"\n✅ Comprehensive POI Analysis:")
        for category, pois in poi_analysis.items():
            print(f"   {category}: {len(pois)} places")
    
    print(f"\n{'='*60}\n")
