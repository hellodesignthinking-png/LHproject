"""
Kakao Map API Service
=====================

Collects location-based data using Kakao Map REST API.
"""

import logging
import aiohttp
from typing import Dict, List, Optional, Tuple
import math

logger = logging.getLogger(__name__)


class KakaoMapService:
    """Kakao Map API integration service"""
    
    # Kakao API Keys
    REST_API_KEY = "1b172a21a17b8b51dd47884b45228483"
    ADMIN_KEY = "6ff4cfada4e33ec48b782f78858f0c39"
    
    BASE_URL = "https://dapi.kakao.com"
    
    # Category codes for places search
    CATEGORIES = {
        'subway': 'SW8',      # 지하철역
        'bus': 'BUS',         # 버스정류장  
        'school': 'SC4',      # 학교
        'elementary': 'SC4',  # 초등학교
        'middle': 'SC4',      # 중학교  
        'high': 'SC4',        # 고등학교
        'university': 'SC4',  # 대학교
        'mart': 'MT1',        # 대형마트
        'convenience': 'CS2', # 편의점
        'hospital': 'HP8',    # 병원
        'pharmacy': 'PM9',    # 약국
        'bank': 'BK9',        # 은행
        'park': 'PK6',        # 공원
        'cafe': 'CE7',        # 카페
    }
    
    def __init__(self):
        """Initialize Kakao Map Service"""
        self.headers = {
            'Authorization': f'KakaoAK {self.REST_API_KEY}'
        }
    
    async def address_to_coordinates(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates (latitude, longitude)
        
        Args:
            address: Korean address string
            
        Returns:
            Tuple of (latitude, longitude) or None
        """
        url = f"{self.BASE_URL}/v2/local/search/address.json"
        params = {'query': address}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('documents'):
                            doc = data['documents'][0]
                            lat = float(doc['y'])
                            lon = float(doc['x'])
                            logger.info(f"✅ Converted address to coordinates: {address} → ({lat}, {lon})")
                            return (lat, lon)
                        else:
                            logger.warning(f"⚠️ No coordinates found for address: {address}")
                            return None
                    else:
                        logger.error(f"❌ Kakao API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"❌ Failed to convert address to coordinates: {e}")
            return None
    
    async def search_nearby_places(
        self, 
        lat: float, 
        lon: float, 
        category: str,
        radius: int = 1000,
        limit: int = 15
    ) -> List[Dict]:
        """
        Search nearby places by category
        
        Args:
            lat: Latitude
            lon: Longitude
            category: Category code or name
            radius: Search radius in meters (max 20000)
            limit: Maximum number of results (max 15)
            
        Returns:
            List of place information dictionaries
        """
        # Get category code
        category_code = self.CATEGORIES.get(category, category)
        
        url = f"{self.BASE_URL}/v2/local/search/category.json"
        params = {
            'category_group_code': category_code,
            'x': lon,
            'y': lat,
            'radius': min(radius, 20000),
            'size': min(limit, 15),
            'sort': 'distance'  # Sort by distance
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        places = data.get('documents', [])
                        
                        logger.info(f"✅ Found {len(places)} {category} nearby")
                        return places
                    else:
                        logger.error(f"❌ Kakao API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"❌ Failed to search nearby places: {e}")
            return []
    
    async def search_by_keyword(
        self,
        lat: float,
        lon: float,
        keyword: str,
        radius: int = 1000,
        limit: int = 15
    ) -> List[Dict]:
        """
        Search places by keyword
        
        Args:
            lat: Latitude
            lon: Longitude
            keyword: Search keyword
            radius: Search radius in meters
            limit: Maximum number of results
            
        Returns:
            List of place information dictionaries
        """
        url = f"{self.BASE_URL}/v2/local/search/keyword.json"
        params = {
            'query': keyword,
            'x': lon,
            'y': lat,
            'radius': min(radius, 20000),
            'size': min(limit, 15),
            'sort': 'distance'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        places = data.get('documents', [])
                        
                        logger.info(f"✅ Found {len(places)} results for '{keyword}'")
                        return places
                    else:
                        logger.error(f"❌ Kakao API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"❌ Failed to search by keyword: {e}")
            return []
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> int:
        """
        Calculate distance between two coordinates using Haversine formula
        
        Returns:
            Distance in meters
        """
        R = 6371000  # Earth radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2)**2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return int(R * c)
    
    def calculate_walk_time(self, distance_m: int) -> int:
        """
        Calculate walking time in minutes
        Average walking speed: 80 m/min (4.8 km/h)
        
        Args:
            distance_m: Distance in meters
            
        Returns:
            Walking time in minutes
        """
        return int(distance_m / 80)
    
    async def collect_subway_stations(
        self,
        address: str,
        radius: int = 1000
    ) -> List[Dict]:
        """
        Collect nearby subway stations
        
        Returns:
            List of subway station info with structure:
            {
                'name': str,
                'line': str,
                'distance_m': int,
                'walk_time_min': int
            }
        """
        # Get coordinates from address
        coords = await self.address_to_coordinates(address)
        if not coords:
            logger.warning(f"⚠️ Cannot collect subway stations: address conversion failed")
            return []
        
        lat, lon = coords
        
        # Search subway stations
        places = await self.search_nearby_places(lat, lon, 'subway', radius=radius)
        
        stations = []
        for place in places:
            place_lat = float(place['y'])
            place_lon = float(place['x'])
            distance = self.calculate_distance(lat, lon, place_lat, place_lon)
            
            # Extract line information from place name
            name = place['place_name']
            line = self._extract_subway_line(name)
            
            stations.append({
                'name': name,
                'line': line,
                'distance_m': distance,
                'walk_time_min': self.calculate_walk_time(distance)
            })
        
        logger.info(f"✅ Collected {len(stations)} subway stations")
        return stations
    
    def _extract_subway_line(self, name: str) -> str:
        """Extract subway line from station name"""
        # Common subway line patterns
        lines = [
            '1호선', '2호선', '3호선', '4호선', '5호선',
            '6호선', '7호선', '8호선', '9호선',
            '경의중앙선', '분당선', '신분당선', '경춘선',
            '공항철도', '인천1호선', '인천2호선',
            '수인선', '의정부경전철', '용인경전철'
        ]
        
        for line in lines:
            if line in name:
                return line
        
        # If no line found, try to extract from parentheses
        if '(' in name and ')' in name:
            start = name.index('(') + 1
            end = name.index(')')
            return name[start:end]
        
        return '정보없음'
    
    async def collect_bus_stops(
        self,
        address: str,
        radius: int = 500
    ) -> List[Dict]:
        """
        Collect nearby bus stops
        
        Returns:
            List of bus stop info with structure:
            {
                'name': str,
                'distance_m': int,
                'routes': str
            }
        """
        coords = await self.address_to_coordinates(address)
        if not coords:
            logger.warning(f"⚠️ Cannot collect bus stops: address conversion failed")
            return []
        
        lat, lon = coords
        
        # Search bus stops by keyword (category code BUS may not work well)
        places = await self.search_by_keyword(lat, lon, '버스정류장', radius=radius)
        
        stops = []
        for place in places:
            place_lat = float(place['y'])
            place_lon = float(place['x'])
            distance = self.calculate_distance(lat, lon, place_lat, place_lon)
            
            stops.append({
                'name': place['place_name'],
                'distance_m': distance,
                'routes': place.get('category_name', '정보없음')
            })
        
        logger.info(f"✅ Collected {len(stops)} bus stops")
        return stops
    
    async def collect_schools(
        self,
        address: str,
        radius: int = 1000
    ) -> List[Dict]:
        """
        Collect nearby schools
        
        Returns:
            List of school info with structure:
            {
                'name': str,
                'type': str,  # 초등학교, 중학교, 고등학교, 대학교
                'distance_m': int
            }
        """
        coords = await self.address_to_coordinates(address)
        if not coords:
            logger.warning(f"⚠️ Cannot collect schools: address conversion failed")
            return []
        
        lat, lon = coords
        
        # Search schools
        places = await self.search_nearby_places(lat, lon, 'school', radius=radius)
        
        schools = []
        for place in places:
            place_lat = float(place['y'])
            place_lon = float(place['x'])
            distance = self.calculate_distance(lat, lon, place_lat, place_lon)
            
            name = place['place_name']
            school_type = self._classify_school_type(name)
            
            schools.append({
                'name': name,
                'type': school_type,
                'distance_m': distance
            })
        
        logger.info(f"✅ Collected {len(schools)} schools")
        return schools
    
    def _classify_school_type(self, name: str) -> str:
        """Classify school type from name"""
        if '초등학교' in name or '초' in name:
            return '초등학교'
        elif '중학교' in name or '중' in name:
            return '중학교'
        elif '고등학교' in name or '고' in name:
            return '고등학교'
        elif '대학교' in name or '대학' in name:
            return '대학교'
        else:
            return '학교'
    
    async def collect_commercial_facilities(
        self,
        address: str,
        radius: int = 1000
    ) -> List[Dict]:
        """
        Collect nearby commercial facilities
        
        Returns:
            List of facility info with structure:
            {
                'name': str,
                'type': str,
                'distance_m': int
            }
        """
        coords = await self.address_to_coordinates(address)
        if not coords:
            logger.warning(f"⚠️ Cannot collect commercial facilities: address conversion failed")
            return []
        
        lat, lon = coords
        
        # Search multiple categories
        categories = ['mart', 'convenience', 'hospital', 'pharmacy', 'bank']
        all_facilities = []
        
        for category in categories:
            places = await self.search_nearby_places(lat, lon, category, radius=radius, limit=5)
            
            for place in places:
                place_lat = float(place['y'])
                place_lon = float(place['x'])
                distance = self.calculate_distance(lat, lon, place_lat, place_lon)
                
                all_facilities.append({
                    'name': place['place_name'],
                    'type': self._get_facility_type_kr(category),
                    'distance_m': distance
                })
        
        # Sort by distance and limit to top 15
        all_facilities.sort(key=lambda x: x['distance_m'])
        all_facilities = all_facilities[:15]
        
        logger.info(f"✅ Collected {len(all_facilities)} commercial facilities")
        return all_facilities
    
    def _get_facility_type_kr(self, category: str) -> str:
        """Get Korean name for facility type"""
        type_map = {
            'mart': '대형마트',
            'convenience': '편의점',
            'hospital': '병원',
            'pharmacy': '약국',
            'bank': '은행',
            'park': '공원',
            'cafe': '카페'
        }
        return type_map.get(category, category)
    
    async def collect_all_poi(
        self,
        address: str,
        subway_radius: int = 1000,
        bus_radius: int = 500,
        school_radius: int = 1000,
        commercial_radius: int = 1000
    ) -> Dict:
        """
        Collect all POI (Point of Interest) data
        
        Returns:
            Dictionary with all POI data:
            {
                'subway_stations': [],
                'bus_stops': [],
                'poi_schools': [],
                'poi_commercial': []
            }
        """
        logger.info(f"🗺️ Collecting POI data for: {address}")
        
        # Collect all data concurrently
        import asyncio
        
        subway_task = self.collect_subway_stations(address, subway_radius)
        bus_task = self.collect_bus_stops(address, bus_radius)
        school_task = self.collect_schools(address, school_radius)
        commercial_task = self.collect_commercial_facilities(address, commercial_radius)
        
        subway_stations, bus_stops, schools, commercial = await asyncio.gather(
            subway_task, bus_task, school_task, commercial_task
        )
        
        result = {
            'subway_stations': subway_stations,
            'bus_stops': bus_stops,
            'poi_schools': schools,
            'poi_commercial': commercial
        }
        
        logger.info(f"✅ POI collection complete:")
        logger.info(f"   - Subway: {len(subway_stations)}")
        logger.info(f"   - Bus: {len(bus_stops)}")
        logger.info(f"   - Schools: {len(schools)}")
        logger.info(f"   - Commercial: {len(commercial)}")
        
        return result
