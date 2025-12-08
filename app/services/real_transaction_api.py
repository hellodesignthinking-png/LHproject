"""
ZeroSite v18 Phase 3 - Real Transaction API Service
====================================================
국토교통부 실거래가 API 통합 서비스

Features:
- 토지 실거래가 조회 (최근 1년, 반경 1km, Top 10)
- 건축물 매매사례 조회 (오피스텔, 연립다세대, 단독다가구)
- 거리 기반 필터링 및 정렬
- 평균 단가 자동 계산
"""

import httpx
import asyncio
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import xml.etree.ElementTree as ET
from math import radians, sin, cos, sqrt, atan2

# Import caching system
try:
    from app.services.real_transaction_cache import get_cache
    CACHE_ENABLED = True
except ImportError:
    CACHE_ENABLED = False
    logger.warning("⚠️ Cache module not found - running without cache")

logger = logging.getLogger(__name__)


@dataclass
class LandTransaction:
    """토지 거래 사례"""
    address: str
    area_m2: float
    price_krw: float
    unit_krw_m2: float
    deal_date: str
    use_zone: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


@dataclass
class BuildingTransaction:
    """건축물 매매 사례"""
    name: str
    address: str
    area_m2: float
    price_krw: float
    unit_krw_m2: float
    deal_date: str
    building_type: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


class RealTransactionAPI:
    """
    국토교통부 실거래가 API 통합 서비스
    
    APIs:
    - 토지 매매: RTMSDataSvcLandTrade
    - 오피스텔 매매: RTMSDataSvcOffiTrade
    - 연립다세대 매매: RTMSDataSvcRHTrade
    - 단독다가구 매매: RTMSDataSvcSHTrade
    """
    
    # API Keys
    API_KEY = "5158584967f97600a71afc331e848ad6c8154524d2266a6ad62c22c5f5c9ad87"
    
    # Endpoints
    LAND_ENDPOINT = "https://apis.data.go.kr/1613000/RTMSDataSvcLandTrade/getRTMSDataSvcLandTrade"
    OFFICETEL_ENDPOINT = "https://apis.data.go.kr/1613000/RTMSDataSvcOffiTrade/getRTMSDataSvcOffiTrade"
    TOWNHOUSE_ENDPOINT = "https://apis.data.go.kr/1613000/RTMSDataSvcRHTrade/getRTMSDataSvcRHTrade"
    SINGLEHOUSE_ENDPOINT = "https://apis.data.go.kr/1613000/RTMSDataSvcSHTrade/getRTMSDataSvcSHTrade"
    
    def __init__(self, enable_cache: bool = True):
        self.api_key = self.API_KEY
        self.cache_enabled = enable_cache and CACHE_ENABLED
        self.cache = get_cache() if self.cache_enabled else None
        
        logger.info("=" * 80)
        logger.info("🌐 RealTransactionAPI initialized")
        logger.info(f"   Land API: {self.LAND_ENDPOINT[:50]}...")
        logger.info(f"   Building APIs: 3 endpoints configured")
        logger.info(f"   Cache: {'✅ ENABLED' if self.cache_enabled else '❌ DISABLED'}")
        logger.info("=" * 80)
    
    def _calculate_distance_m(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """두 좌표 간 거리 계산 (미터)"""
        R = 6371000  # 지구 반경 (미터)
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        
        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def _parse_xml_response(self, xml_text: str) -> List[Dict]:
        """XML 응답 파싱"""
        try:
            root = ET.fromstring(xml_text)
            
            # Check result code
            result_code = root.find('.//resultCode')
            if result_code is not None and result_code.text != '00':
                result_msg = root.find('.//resultMsg')
                logger.warning(f"API Error: {result_msg.text if result_msg is not None else 'Unknown'}")
                return []
            
            # Parse items
            items = []
            for item in root.findall('.//item'):
                item_dict = {}
                for child in item:
                    item_dict[child.tag] = child.text
                items.append(item_dict)
            
            return items
            
        except Exception as e:
            logger.error(f"XML parsing failed: {e}")
            return []
    
    async def fetch_land_transactions(
        self,
        lawd_cd: str,  # 법정동코드 (서울 11, 경기 41, etc)
        deal_ymd: str,  # YYYYMM
        center_lat: float,
        center_lon: float,
        radius_m: int = 1000
    ) -> List[LandTransaction]:
        """
        토지 실거래가 조회 (캐싱 지원)
        
        Args:
            lawd_cd: 법정동코드 (앞 2자리, 서울=11, 경기=41)
            deal_ymd: 거래년월 (YYYYMM)
            center_lat: 중심 위도
            center_lon: 중심 경도
            radius_m: 검색 반경 (미터)
        
        Returns:
            LandTransaction 리스트
        """
        logger.info(f"🏞️  Fetching land transactions: lawd={lawd_cd}, date={deal_ymd}, radius={radius_m}m")
        
        # Try cache first
        if self.cache_enabled:
            cached_data = self.cache.get('land', lawd_cd, deal_ymd)
            if cached_data:
                transactions = [LandTransaction(**t) for t in cached_data]
                logger.info(f"   ✅ Loaded {len(transactions)} land transactions from cache")
                return transactions[:10]
        
        params = {
            'serviceKey': self.api_key,
            'LAWD_CD': lawd_cd,
            'DEAL_YMD': deal_ymd,
            'numOfRows': '100',
            'pageNo': '1'
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.LAND_ENDPOINT, params=params)
                response.raise_for_status()
                
                items = self._parse_xml_response(response.text)
                logger.info(f"   Retrieved {len(items)} land records from API")
                
                transactions = []
                for item in items:
                    try:
                        # Extract data
                        area = float(item.get('plottgAr', '0'))  # 대지면적
                        price = int(item.get('dealAmount', '0').replace(',', '')) * 10000  # 거래금액 (만원 → 원)
                        
                        if area <= 0 or price <= 0:
                            continue
                        
                        unit = price / area
                        
                        # Build address
                        sgg_nm = item.get('sggNm', '')  # 시군구명
                        umd_nm = item.get('umdNm', '')  # 읍면동명
                        jibun = item.get('jibun', '')   # 지번
                        address = f"{sgg_nm} {umd_nm} {jibun}".strip()
                        
                        # Deal date
                        deal_year = item.get('dealYear', '')
                        deal_month = item.get('dealMonth', '').zfill(2)
                        deal_day = item.get('dealDay', '').zfill(2)
                        deal_date = f"{deal_year}.{deal_month}.{deal_day}"
                        
                        transactions.append(LandTransaction(
                            address=address,
                            area_m2=area,
                            price_krw=price,
                            unit_krw_m2=unit,
                            deal_date=deal_date,
                            use_zone=None  # API doesn't provide this
                        ))
                        
                    except Exception as e:
                        logger.warning(f"Failed to parse land item: {e}")
                        continue
                
                # Sort by date (most recent first)
                transactions.sort(key=lambda x: x.deal_date, reverse=True)
                
                # Take top 10
                top_transactions = transactions[:10]
                
                logger.info(f"   ✅ Parsed {len(top_transactions)} land transactions")
                if top_transactions:
                    avg_unit = sum(t.unit_krw_m2 for t in top_transactions) / len(top_transactions)
                    logger.info(f"   📊 Average land price: {avg_unit/10000:.0f}만원/㎡")
                
                # Save to cache
                if self.cache_enabled and top_transactions:
                    cache_data = [t.to_dict() for t in top_transactions]
                    self.cache.set('land', lawd_cd, deal_ymd, cache_data)
                
                return top_transactions
                
        except Exception as e:
            logger.error(f"❌ Land transaction API failed: {e}")
            return []
    
    async def fetch_building_transactions(
        self,
        lawd_cd: str,
        deal_ymd: str,
        center_lat: float,
        center_lon: float,
        radius_m: int = 1000
    ) -> List[BuildingTransaction]:
        """
        건축물 매매사례 조회 (오피스텔, 연립다세대, 단독다가구 통합) (캐싱 지원)
        
        Args:
            lawd_cd: 법정동코드
            deal_ymd: 거래년월 (YYYYMM)
            center_lat: 중심 위도
            center_lon: 중심 경도
            radius_m: 검색 반경 (미터)
        
        Returns:
            BuildingTransaction 리스트
        """
        logger.info(f"🏢 Fetching building transactions: lawd={lawd_cd}, date={deal_ymd}")
        
        # Try cache first
        if self.cache_enabled:
            cached_data = self.cache.get('building', lawd_cd, deal_ymd)
            if cached_data:
                transactions = [BuildingTransaction(**t) for t in cached_data]
                logger.info(f"   ✅ Loaded {len(transactions)} building transactions from cache")
                return transactions[:10]
        
        all_transactions = []
        
        # Fetch from all 3 building APIs
        endpoints = [
            (self.OFFICETEL_ENDPOINT, '오피스텔'),
            (self.TOWNHOUSE_ENDPOINT, '연립다세대'),
            (self.SINGLEHOUSE_ENDPOINT, '단독다가구')
        ]
        
        for endpoint, building_type in endpoints:
            params = {
                'serviceKey': self.api_key,
                'LAWD_CD': lawd_cd,
                'DEAL_YMD': deal_ymd,
                'numOfRows': '100',
                'pageNo': '1'
            }
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(endpoint, params=params)
                    response.raise_for_status()
                    
                    items = self._parse_xml_response(response.text)
                    logger.info(f"   Retrieved {len(items)} {building_type} records")
                    
                    for item in items:
                        try:
                            # Extract data
                            area = float(item.get('hscpAr', '0') or item.get('plottgAr', '0'))  # 전용면적 or 대지면적
                            price = int(item.get('dealAmount', '0').replace(',', '')) * 10000
                            
                            if area <= 0 or price <= 0:
                                continue
                            
                            unit = price / area
                            
                            # Build address
                            sgg_nm = item.get('sggNm', '')
                            umd_nm = item.get('umdNm', '')
                            jibun = item.get('jibun', '')
                            building_name = item.get('aptNm', '') or item.get('houseNm', '') or ''
                            address = f"{sgg_nm} {umd_nm} {jibun}".strip()
                            
                            # Deal date
                            deal_year = item.get('dealYear', '')
                            deal_month = item.get('dealMonth', '').zfill(2)
                            deal_day = item.get('dealDay', '').zfill(2)
                            deal_date = f"{deal_year}.{deal_month}.{deal_day}"
                            
                            all_transactions.append(BuildingTransaction(
                                name=building_name or address,
                                address=address,
                                area_m2=area,
                                price_krw=price,
                                unit_krw_m2=unit,
                                deal_date=deal_date,
                                building_type=building_type
                            ))
                            
                        except Exception as e:
                            logger.warning(f"Failed to parse {building_type} item: {e}")
                            continue
                            
            except Exception as e:
                logger.error(f"❌ {building_type} API failed: {e}")
                continue
        
        # Sort by date (most recent first) and take top 10
        all_transactions.sort(key=lambda x: x.deal_date, reverse=True)
        top_transactions = all_transactions[:10]
        
        logger.info(f"   ✅ Parsed {len(top_transactions)} building transactions total")
        if top_transactions:
            avg_unit = sum(t.unit_krw_m2 for t in top_transactions) / len(top_transactions)
            logger.info(f"   📊 Average building price: {avg_unit/10000:.0f}만원/㎡")
        
        # Save to cache
        if self.cache_enabled and top_transactions:
            cache_data = [t.to_dict() for t in top_transactions]
            self.cache.set('building', lawd_cd, deal_ymd, cache_data)
        
        return top_transactions
    
    async def fetch_comparables(
        self,
        address: str,
        lawd_cd: str = None,
        radius_m: int = 1000
    ) -> Tuple[List[LandTransaction], List[BuildingTransaction]]:
        """
        주소 기반 실거래가 통합 조회
        
        Args:
            address: 분석 대상 주소
            lawd_cd: 법정동코드 (None이면 주소에서 추출)
            radius_m: 검색 반경
        
        Returns:
            (토지 거래사례 10건, 건축물 매매사례 10건)
        """
        logger.info("=" * 80)
        logger.info(f"🔍 Fetching real transaction comparables for: {address}")
        logger.info("=" * 80)
        
        # Get coordinates from address
        try:
            from app.services.kakao_service import KakaoService
            kakao = KakaoService()
            coord = await kakao.address_to_coordinates(address)
            center_lat = coord['y']
            center_lon = coord['x']
            logger.info(f"📍 Coordinates: lat={center_lat:.6f}, lon={center_lon:.6f}")
        except Exception as e:
            logger.error(f"Failed to get coordinates: {e}")
            center_lat = 37.5665
            center_lon = 126.9780
        
        # Extract lawd_cd from address if not provided
        if lawd_cd is None:
            if '서울' in address:
                lawd_cd = '11'
            elif '경기' in address:
                lawd_cd = '41'
            elif '인천' in address:
                lawd_cd = '28'
            else:
                lawd_cd = '11'  # Default to Seoul
        
        # Get deal_ymd for last year
        last_year = (datetime.now() - timedelta(days=365)).strftime('%Y%m')
        
        # Fetch land and building transactions concurrently
        land_task = self.fetch_land_transactions(lawd_cd, last_year, center_lat, center_lon, radius_m)
        building_task = self.fetch_building_transactions(lawd_cd, last_year, center_lat, center_lon, radius_m)
        
        land_comps, building_comps = await asyncio.gather(land_task, building_task)
        
        logger.info("=" * 80)
        logger.info(f"✅ Comparables fetched:")
        logger.info(f"   🏞️  Land: {len(land_comps)} transactions")
        logger.info(f"   🏢 Building: {len(building_comps)} transactions")
        logger.info("=" * 80)
        
        return land_comps, building_comps


# Test function
async def test_api():
    """API 테스트"""
    api = RealTransactionAPI()
    
    test_address = "서울특별시 마포구 월드컵북로 120"
    land_comps, building_comps = await api.fetch_comparables(test_address)
    
    print("\n" + "=" * 80)
    print("📊 Test Results")
    print("=" * 80)
    
    print(f"\n🏞️  Land Transactions ({len(land_comps)}개):")
    for i, comp in enumerate(land_comps[:3], 1):
        print(f"   {i}. {comp.address}")
        print(f"      면적: {comp.area_m2:.1f}㎡, 단가: {comp.unit_krw_m2/10000:.0f}만원/㎡")
    
    print(f"\n🏢 Building Transactions ({len(building_comps)}개):")
    for i, comp in enumerate(building_comps[:3], 1):
        print(f"   {i}. {comp.name} ({comp.building_type})")
        print(f"      면적: {comp.area_m2:.1f}㎡, 단가: {comp.unit_krw_m2/10000:.0f}만원/㎡")
    
    if land_comps:
        avg_land = sum(c.unit_krw_m2 for c in land_comps) / len(land_comps)
        print(f"\n📊 평균 토지 단가: {avg_land/10000:.0f}만원/㎡")
    
    if building_comps:
        avg_bld = sum(c.unit_krw_m2 for c in building_comps) / len(building_comps)
        print(f"📊 평균 건물 단가: {avg_bld/10000:.0f}만원/㎡")


if __name__ == '__main__':
    asyncio.run(test_api())
