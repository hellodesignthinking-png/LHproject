"""
Transaction Data Service - RTMS API Integration
국토교통부 실거래가 API 연동 서비스

주요 기능:
1. 주소 -> 좌표 변환 (Geocoding)
2. RTMS API 호출 (토지 실거래가 조회)
3. 거리 계산 (Haversine Formula)
4. 데이터 표준화 및 정렬
"""

import os
import logging
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import requests
from urllib.parse import quote

logger = logging.getLogger(__name__)


class TransactionDataService:
    """국토교통부 실거래가 API 연동 서비스"""
    
    def __init__(self):
        """초기화"""
        # MOLIT API 키 (환경변수에서 로드)
        self.rtms_api_key = os.getenv('MOLIT_API_KEY', 'YOUR_API_KEY_HERE')
        
        # Kakao API 키 (주소 -> 좌표 변환용)
        self.kakao_api_key = os.getenv('KAKAO_API_KEY', 'YOUR_KAKAO_KEY')
        
        # API 엔드포인트
        self.rtms_api_url = "http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/RTMSOBJSvc/getRTMSDataSvcLandTrade"
        self.kakao_geocode_url = "https://dapi.kakao.com/v2/local/search/address.json"
        
        logger.info("✅ TransactionDataService initialized")
    
    
    def get_nearby_transactions(
        self,
        address: str,
        radius_km: float = 2.0,
        months_back: int = 24,
        max_results: int = 15
    ) -> List[Dict]:
        """
        주변 토지 실거래가 조회
        
        Args:
            address: 검색 기준 주소 (예: "서울시 강남구 역삼동 123-4")
            radius_km: 검색 반경 (기본: 2km)
            months_back: 과거 검색 개월수 (기본: 24개월)
            max_results: 최대 결과 개수 (기본: 15개)
            
        Returns:
            실거래 데이터 리스트 (거리순 정렬)
        """
        logger.info(f"🔍 Fetching transactions for: {address} (radius: {radius_km}km)")
        
        # 1. 주소 -> 좌표 변환
        coords = self._geocode_address(address)
        if not coords:
            logger.warning(f"⚠️ Geocoding failed for: {address}, using fallback data")
            return self._generate_fallback_data(address, max_results)
        
        lat, lon = coords
        logger.info(f"📍 Coordinates: ({lat}, {lon})")
        
        # 2. 주소 파싱 (시군구 추출)
        parsed = self._parse_address(address)
        if not parsed:
            logger.warning(f"⚠️ Address parsing failed, using fallback data")
            return self._generate_fallback_data(address, max_results)
        
        # 3. RTMS API 호출
        transactions = []
        
        # 최근 24개월 동안 월별로 조회
        end_date = datetime.now()
        for i in range(months_back):
            target_date = end_date - timedelta(days=30 * i)
            year_month = target_date.strftime('%Y%m')
            
            monthly_data = self._fetch_rtms_data(
                year_month=year_month,
                sigungu_code=parsed['sigungu_code'],
                dong=parsed['dong']
            )
            
            if monthly_data:
                transactions.extend(monthly_data)
                logger.info(f"   📅 {year_month}: {len(monthly_data)} transactions found")
        
        if not transactions:
            logger.warning(f"⚠️ No RTMS transactions found within {radius_km}km, using fallback data")
            return self._generate_fallback_data(address, max_results)
        
        # 4. 거리 계산 및 필터링
        filtered_transactions = []
        for tx in transactions:
            tx_coords = self._geocode_address(tx['address_full'])
            if tx_coords:
                distance = self._calculate_distance(lat, lon, tx_coords[0], tx_coords[1])
                
                if distance <= radius_km:
                    tx['distance_km'] = round(distance, 2)
                    tx['lat'] = tx_coords[0]
                    tx['lon'] = tx_coords[1]
                    filtered_transactions.append(tx)
        
        logger.info(f"✅ Found {len(filtered_transactions)} transactions within {radius_km}km")
        
        # 5. 정렬 (거리순)
        filtered_transactions.sort(key=lambda x: x['distance_km'])
        
        # 6. 최대 개수 제한
        result = filtered_transactions[:max_results]
        
        logger.info(f"📊 Returning {len(result)} transactions (sorted by distance)")
        
        return result
    
    
    def _geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        주소 -> 좌표 변환 (Kakao API)
        
        Returns:
            (latitude, longitude) 또는 None
        """
        try:
            headers = {'Authorization': f'KakaoAK {self.kakao_api_key}'}
            params = {'query': address}
            
            response = requests.get(
                self.kakao_geocode_url,
                headers=headers,
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('documents'):
                    doc = data['documents'][0]
                    lat = float(doc['y'])
                    lon = float(doc['x'])
                    return (lat, lon)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Geocoding error: {e}")
            return None
    
    
    def _parse_address(self, address: str) -> Optional[Dict]:
        """
        주소 파싱 (시군구 코드, 동 추출)
        
        Returns:
            {'sigungu_code': str, 'dong': str} 또는 None
        """
        # 서울시 구 코드 매핑
        sigungu_codes = {
            '강남구': '11680', '강동구': '11740', '강북구': '11305',
            '강서구': '11500', '관악구': '11620', '광진구': '11215',
            '구로구': '11530', '금천구': '11545', '노원구': '11350',
            '도봉구': '11320', '동대문구': '11230', '동작구': '11590',
            '마포구': '11440', '서대문구': '11410', '서초구': '11650',
            '성동구': '11200', '성북구': '11290', '송파구': '11710',
            '양천구': '11470', '영등포구': '11560', '용산구': '11170',
            '은평구': '11380', '종로구': '11110', '중구': '11140',
            '중랑구': '11260'
        }
        
        # 구 이름 추출
        gu_name = None
        for gu in sigungu_codes.keys():
            if gu in address:
                gu_name = gu
                break
        
        if not gu_name:
            return None
        
        # 동 이름 추출 (간단한 패턴 매칭)
        parts = address.split()
        dong = None
        for part in parts:
            if '동' in part and part != gu_name:
                dong = part.replace('동', '').strip()
                break
        
        if not dong:
            # 기본값 설정
            dong = ''
        
        return {
            'sigungu_code': sigungu_codes[gu_name],
            'dong': dong,
            'gu_name': gu_name
        }
    
    
    def _fetch_rtms_data(
        self,
        year_month: str,
        sigungu_code: str,
        dong: str = ''
    ) -> List[Dict]:
        """
        RTMS API 호출 (토지 실거래가)
        
        Args:
            year_month: YYYYMM 형식 (예: "202312")
            sigungu_code: 시군구 코드 (예: "11680")
            dong: 법정동 (예: "역삼")
            
        Returns:
            실거래 데이터 리스트
        """
        try:
            params = {
                'serviceKey': self.rtms_api_key,
                'LAWD_CD': sigungu_code,
                'DEAL_YMD': year_month,
                'numOfRows': 100,
                'pageNo': 1
            }
            
            response = requests.get(
                self.rtms_api_url,
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning(f"⚠️ RTMS API error: {response.status_code}")
                return []
            
            # XML 파싱 (실제 구현 시 xml.etree.ElementTree 사용)
            # 여기서는 간단히 처리
            data = response.text
            
            # TODO: XML 파싱 로직 구현
            # 현재는 빈 리스트 반환 (fallback 데이터 사용)
            
            return []
            
        except Exception as e:
            logger.error(f"❌ RTMS API fetch error: {e}")
            return []
    
    
    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        두 좌표 간 거리 계산 (Haversine Formula)
        
        Returns:
            거리 (km)
        """
        R = 6371  # 지구 반경 (km)
        
        # 라디안 변환
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine Formula
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) *
            math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance
    
    
    def _generate_fallback_data(self, address: str, max_results: int) -> List[Dict]:
        """
        Fallback 더미 데이터 생성 (API 실패 시)
        
        Note:
            실제 RTMS API 데이터 형식과 동일하게 생성
        """
        logger.warning("⚠️ Using fallback dummy transaction data")
        
        from app.services.real_transaction_generator import get_transaction_generator
        
        generator = get_transaction_generator()
        transactions = generator.generate_transactions(
            address=address,
            land_area_sqm=660,
            num_transactions=max_results
        )
        
        # 표준 형식으로 변환
        standardized = []
        for tx in transactions:
            standardized.append({
                'deal_date': tx.get('transaction_date', '2024-01-01'),
                'address_jibun': tx.get('location', '서울 강남구 역삼동 123번지'),
                'address_full': tx.get('location', '서울 강남구 역삼동 123번지'),
                'price_per_sqm': tx.get('unit_price_sqm', 10000000),
                'price_total': tx.get('total_price', 6600000000),
                'area_sqm': tx.get('land_area_sqm', 660),
                'distance_km': tx.get('distance_km', 0.5),
                'road_name': tx.get('road_name', '테헤란로'),
                'road_grade': tx.get('road_grade', '대로'),
                'lat': 37.4979,
                'lon': 127.0276
            })
        
        return standardized


# Singleton instance
_transaction_service = None


def get_transaction_service() -> TransactionDataService:
    """TransactionDataService 싱글톤 인스턴스 반환"""
    global _transaction_service
    if _transaction_service is None:
        _transaction_service = TransactionDataService()
    return _transaction_service
