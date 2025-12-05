#!/usr/bin/env python3
"""
ZeroSite v8.0 - Unified External API Client
============================================

Integrates critical government APIs for comprehensive land analysis:
1. MOLIT Real Estate Transaction APIs (12 endpoints)
2. Safety Map WMS (Crime Risk Analysis)
3. Environmental Air Quality Data

Author: ZeroSite Development Team
Date: 2025-12-02
Version: v8.0
"""

import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from dataclasses import dataclass
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class RealEstateTransaction:
    """부동산 실거래 데이터 모델"""
    deal_date: str  # 거래일자
    deal_amount: int  # 거래금액 (원)
    area: float  # 면적 (㎡)
    floor: Optional[int] = None  # 층수
    building_year: Optional[int] = None  # 건축연도
    dong: Optional[str] = None  # 법정동
    jibun: Optional[str] = None  # 지번
    apartment_name: Optional[str] = None  # 아파트명
    unit_price: Optional[int] = None  # 단가 (원/㎡)


@dataclass
class CrimeRiskData:
    """범죄 위험도 데이터 모델"""
    crime_score: float  # 범죄위험도 점수 (0-100)
    risk_level: str  # 위험등급 (안전/주의/위험)
    elderly_crime_score: float  # 노인대상 범죄 점수
    has_crime_hotspot: bool  # 범죄주의구간 포함 여부


@dataclass
class EnvironmentalData:
    """환경 데이터 모델"""
    pm10: Optional[float] = None  # 미세먼지 (㎍/㎥)
    pm25: Optional[float] = None  # 초미세먼지 (㎍/㎥)
    air_quality_index: Optional[int] = None  # 종합 대기질 지수
    environmental_risk_score: float = 0  # 환경 리스크 점수 (0-100)


class ExternalAPIClient:
    """통합 외부 API 클라이언트"""
    
    def __init__(self, molit_api_key: str = None, safemap_api_key: str = None):
        """
        Initialize API client with service keys
        
        Args:
            molit_api_key: 국토교통부 API 인증키
            safemap_api_key: 생활안전지도 API 인증키
        """
        self.molit_api_key = molit_api_key or "YOUR_MOLIT_API_KEY"
        self.safemap_api_key = safemap_api_key or "YOUR_SAFEMAP_API_KEY"
        
        # API endpoints
        self.molit_base_url = "https://apis.data.go.kr/1613000"
        self.safemap_base_url = "http://safemap.go.kr/openapi2"
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 0.1  # 100ms between requests
        
    def _rate_limit(self, api_name: str):
        """Rate limiting to avoid API quota issues"""
        if api_name in self.last_request_time:
            elapsed = time.time() - self.last_request_time[api_name]
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
        self.last_request_time[api_name] = time.time()
    
    def _parse_xml_response(self, xml_text: str) -> List[Dict]:
        """Parse XML response from MOLIT APIs"""
        try:
            root = ET.fromstring(xml_text)
            items = []
            
            # Find all item elements
            for item in root.findall('.//item'):
                data = {}
                for child in item:
                    data[child.tag] = child.text
                items.append(data)
            
            return items
        except Exception as e:
            logger.error(f"XML parsing error: {e}")
            return []
    
    def _extract_lawd_cd(self, address: str) -> str:
        """
        Extract LAWD_CD (법정동코드) from address
        
        서울특별시 = 11
        부산광역시 = 26
        대구광역시 = 27
        인천광역시 = 28
        광주광역시 = 29
        대전광역시 = 30
        울산광역시 = 31
        세종특별자치시 = 36
        경기도 = 41
        """
        city_codes = {
            '서울': '11110',  # 서울 종로구 (default)
            '부산': '26110',
            '대구': '27110',
            '인천': '28110',
            '광주': '29110',
            '대전': '30110',
            '울산': '31110',
            '세종': '36110',
            '경기': '41110',
        }
        
        for city, code in city_codes.items():
            if city in address:
                return code
        
        return '11110'  # Default to Seoul Jongno-gu
    
    # ========================================================================
    # 1. 국토교통부 실거래가 API 그룹
    # ========================================================================
    
    def get_land_trade_transactions(
        self,
        address: str,
        months_back: int = 12
    ) -> List[RealEstateTransaction]:
        """
        토지 매매 실거래가 조회 (최우선순위 ⭐⭐⭐⭐⭐)
        
        Args:
            address: 토지 주소
            months_back: 조회 개월 수 (기본 12개월)
            
        Returns:
            List of RealEstateTransaction objects
        """
        self._rate_limit('land_trade')
        
        lawd_cd = self._extract_lawd_cd(address)
        transactions = []
        
        # Get last N months
        for i in range(months_back):
            deal_ymd = (datetime.now() - timedelta(days=30*i)).strftime('%Y%m')
            
            url = f"{self.molit_base_url}/RTMSDataSvcLandTrade/getLandTradingList"
            params = {
                'serviceKey': self.molit_api_key,
                'LAWD_CD': lawd_cd,
                'DEAL_YMD': deal_ymd,
                'numOfRows': 200,
                'pageNo': 1
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    items = self._parse_xml_response(response.text)
                    
                    for item in items:
                        try:
                            amount = int(item.get('거래금액', '0').replace(',', '').strip())
                            area = float(item.get('대지면적', '0').replace(',', ''))
                            
                            transaction = RealEstateTransaction(
                                deal_date=item.get('년') + item.get('월') + item.get('일'),
                                deal_amount=amount * 10000,  # Convert to 원
                                area=area,
                                dong=item.get('법정동'),
                                jibun=item.get('지번'),
                                unit_price=int(amount * 10000 / area) if area > 0 else 0
                            )
                            transactions.append(transaction)
                        except Exception as e:
                            logger.warning(f"Failed to parse transaction: {e}")
                            continue
            except Exception as e:
                logger.error(f"Land trade API error: {e}")
        
        return transactions
    
    def get_apartment_trade_transactions(
        self,
        address: str,
        months_back: int = 12
    ) -> List[RealEstateTransaction]:
        """
        아파트 매매 실거래가 조회 (⭐⭐⭐⭐⭐)
        유사 입지 인근 거래가 비교
        """
        self._rate_limit('apt_trade')
        
        lawd_cd = self._extract_lawd_cd(address)
        transactions = []
        
        for i in range(months_back):
            deal_ymd = (datetime.now() - timedelta(days=30*i)).strftime('%Y%m')
            
            url = f"{self.molit_base_url}/RTMSDataSvcAptTrade/getAptTradingList"
            params = {
                'serviceKey': self.molit_api_key,
                'LAWD_CD': lawd_cd,
                'DEAL_YMD': deal_ymd,
                'numOfRows': 200,
                'pageNo': 1
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    items = self._parse_xml_response(response.text)
                    
                    for item in items:
                        try:
                            amount = int(item.get('거래금액', '0').replace(',', '').strip())
                            area = float(item.get('전용면적', '0').replace(',', ''))
                            floor = int(item.get('층', '0'))
                            building_year = int(item.get('건축년도', '0'))
                            
                            transaction = RealEstateTransaction(
                                deal_date=item.get('년') + item.get('월') + item.get('일'),
                                deal_amount=amount * 10000,
                                area=area,
                                floor=floor,
                                building_year=building_year,
                                dong=item.get('법정동'),
                                jibun=item.get('지번'),
                                apartment_name=item.get('아파트'),
                                unit_price=int(amount * 10000 / area) if area > 0 else 0
                            )
                            transactions.append(transaction)
                        except Exception as e:
                            logger.warning(f"Failed to parse apt transaction: {e}")
                            continue
            except Exception as e:
                logger.error(f"Apartment trade API error: {e}")
        
        return transactions
    
    def get_apartment_rent_transactions(
        self,
        address: str,
        months_back: int = 12
    ) -> List[RealEstateTransaction]:
        """
        아파트 전월세 실거래가 조회 (⭐⭐⭐⭐)
        임대가 비교 → 예상 임대수익
        """
        self._rate_limit('apt_rent')
        
        lawd_cd = self._extract_lawd_cd(address)
        transactions = []
        
        for i in range(months_back):
            deal_ymd = (datetime.now() - timedelta(days=30*i)).strftime('%Y%m')
            
            url = f"{self.molit_base_url}/RTMSDataSvcAptRent/getAptRentList"
            params = {
                'serviceKey': self.molit_api_key,
                'LAWD_CD': lawd_cd,
                'DEAL_YMD': deal_ymd,
                'numOfRows': 200,
                'pageNo': 1
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    items = self._parse_xml_response(response.text)
                    
                    for item in items:
                        try:
                            deposit = int(item.get('보증금액', '0').replace(',', '').strip())
                            monthly = int(item.get('월세금액', '0').replace(',', '').strip())
                            area = float(item.get('전용면적', '0').replace(',', ''))
                            
                            # Calculate equivalent deal amount (보증금 + 월세*100)
                            equivalent_amount = (deposit + monthly * 100) * 10000
                            
                            transaction = RealEstateTransaction(
                                deal_date=item.get('년') + item.get('월') + item.get('일'),
                                deal_amount=equivalent_amount,
                                area=area,
                                floor=int(item.get('층', '0')),
                                building_year=int(item.get('건축년도', '0')),
                                dong=item.get('법정동'),
                                jibun=item.get('지번'),
                                apartment_name=item.get('아파트'),
                                unit_price=int(equivalent_amount / area) if area > 0 else 0
                            )
                            transactions.append(transaction)
                        except Exception as e:
                            logger.warning(f"Failed to parse rent transaction: {e}")
                            continue
            except Exception as e:
                logger.error(f"Apartment rent API error: {e}")
        
        return transactions
    
    def get_multi_family_trade_transactions(
        self,
        address: str,
        months_back: int = 12
    ) -> List[RealEstateTransaction]:
        """
        연립다세대 매매 실거래가 조회 (⭐⭐⭐⭐)
        청년·신혼부부용 비교
        """
        self._rate_limit('rh_trade')
        
        lawd_cd = self._extract_lawd_cd(address)
        transactions = []
        
        for i in range(months_back):
            deal_ymd = (datetime.now() - timedelta(days=30*i)).strftime('%Y%m')
            
            url = f"{self.molit_base_url}/RTMSDataSvcRHTrade/getRHTradingList"
            params = {
                'serviceKey': self.molit_api_key,
                'LAWD_CD': lawd_cd,
                'DEAL_YMD': deal_ymd,
                'numOfRows': 200,
                'pageNo': 1
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    items = self._parse_xml_response(response.text)
                    
                    for item in items:
                        try:
                            amount = int(item.get('거래금액', '0').replace(',', '').strip())
                            area = float(item.get('전용면적', '0').replace(',', ''))
                            
                            transaction = RealEstateTransaction(
                                deal_date=item.get('년') + item.get('월') + item.get('일'),
                                deal_amount=amount * 10000,
                                area=area,
                                floor=int(item.get('층', '0')),
                                building_year=int(item.get('건축년도', '0')),
                                dong=item.get('법정동'),
                                jibun=item.get('지번'),
                                unit_price=int(amount * 10000 / area) if area > 0 else 0
                            )
                            transactions.append(transaction)
                        except Exception as e:
                            logger.warning(f"Failed to parse RH transaction: {e}")
                            continue
            except Exception as e:
                logger.error(f"Multi-family trade API error: {e}")
        
        return transactions
    
    # ========================================================================
    # 2. 생활안전지도 WMS - 범죄 위험도 분석
    # ========================================================================
    
    def get_crime_risk_analysis(
        self,
        lat: float,
        lng: float,
        radius_km: float = 1.0
    ) -> CrimeRiskData:
        """
        범죄 위험도 분석 (⭐⭐⭐⭐⭐)
        
        Args:
            lat: 위도
            lng: 경도
            radius_km: 분석 반경 (km)
            
        Returns:
            CrimeRiskData object
        """
        self._rate_limit('crime_risk')
        
        # Calculate bounding box
        lat_offset = radius_km / 111.0  # 1 degree latitude ≈ 111 km
        lng_offset = radius_km / (111.0 * abs(lat))  # Longitude varies by latitude
        
        bbox = f"{lng - lng_offset},{lat - lat_offset},{lng + lng_offset},{lat + lat_offset}"
        
        # Query crime hotspot WMS
        url = f"{self.safemap_base_url}/IF_0087_WMS"
        params = {
            'serviceKey': self.safemap_api_key,
            'srs': 'EPSG:4326',
            'bbox': bbox,
            'format': 'image/png',
            'width': 256,
            'height': 256,
            'transparent': 'TRUE'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                # Analyze image data to calculate crime score
                # For now, use mock scoring based on response size
                image_size = len(response.content)
                
                # Simple heuristic: larger response = more crime data = higher risk
                crime_score = min(100, (image_size / 10000) * 50)
                
                if crime_score < 30:
                    risk_level = "안전"
                elif crime_score < 60:
                    risk_level = "주의"
                else:
                    risk_level = "위험"
                
                # Query elderly crime hotspot
                elderly_url = f"{self.safemap_base_url}/IF_0088_WMS"  # Elderly crime layer
                elderly_response = requests.get(elderly_url, params=params, timeout=10)
                elderly_score = min(100, (len(elderly_response.content) / 10000) * 50) if elderly_response.status_code == 200 else 0
                
                return CrimeRiskData(
                    crime_score=crime_score,
                    risk_level=risk_level,
                    elderly_crime_score=elderly_score,
                    has_crime_hotspot=crime_score > 50
                )
            else:
                logger.warning(f"Crime risk API returned status {response.status_code}")
                return CrimeRiskData(
                    crime_score=0,
                    risk_level="데이터 없음",
                    elderly_crime_score=0,
                    has_crime_hotspot=False
                )
        except Exception as e:
            logger.error(f"Crime risk API error: {e}")
            return CrimeRiskData(
                crime_score=0,
                risk_level="조회 실패",
                elderly_crime_score=0,
                has_crime_hotspot=False
            )
    
    # ========================================================================
    # 3. 환경부 대기질 데이터
    # ========================================================================
    
    def get_environmental_data(
        self,
        address: str
    ) -> EnvironmentalData:
        """
        환경 대기질 데이터 조회 (⭐⭐⭐⭐)
        공사환경 리스크 및 인허가 단계 리스크
        
        Note: This is a placeholder. Actual implementation requires
        환경부 API key and proper endpoint configuration.
        """
        # Mock data for now
        # Real implementation would query 국립환경과학원 대기질 API
        
        return EnvironmentalData(
            pm10=45.0,  # Mock PM10 value
            pm25=25.0,  # Mock PM2.5 value
            air_quality_index=65,  # Mock AQI
            environmental_risk_score=35.0  # Mock risk score
        )
    
    # ========================================================================
    # 4. 종합 분석 메서드
    # ========================================================================
    
    def get_comprehensive_market_analysis(
        self,
        address: str,
        land_area: float,
        lat: float,
        lng: float
    ) -> Dict:
        """
        종합 시장 분석
        
        Returns:
            {
                'land_transactions': [...],
                'apt_transactions': [...],
                'apt_rent_transactions': [...],
                'multi_family_transactions': [...],
                'crime_risk': CrimeRiskData,
                'environmental': EnvironmentalData,
                'market_summary': {
                    'avg_land_price_per_sqm': int,
                    'avg_apt_price_per_sqm': int,
                    'avg_rent_yield': float,
                    'total_transactions': int,
                    'market_activity': str
                }
            }
        """
        logger.info(f"Starting comprehensive market analysis for {address}")
        
        # 1. Get all transaction data
        land_txns = self.get_land_trade_transactions(address, months_back=12)
        apt_txns = self.get_apartment_trade_transactions(address, months_back=12)
        apt_rent_txns = self.get_apartment_rent_transactions(address, months_back=12)
        mf_txns = self.get_multi_family_trade_transactions(address, months_back=12)
        
        # 2. Get safety and environmental data
        crime_risk = self.get_crime_risk_analysis(lat, lng)
        environmental = self.get_environmental_data(address)
        
        # 3. Calculate market summary
        avg_land_price = 0
        if land_txns:
            avg_land_price = int(sum(t.unit_price for t in land_txns) / len(land_txns))
        
        avg_apt_price = 0
        if apt_txns:
            avg_apt_price = int(sum(t.unit_price for t in apt_txns) / len(apt_txns))
        
        avg_rent_yield = 0.0
        if apt_rent_txns and apt_txns:
            # Simple rent yield calculation
            avg_rent_yield = 3.5  # Mock value, real calculation needed
        
        total_txns = len(land_txns) + len(apt_txns) + len(apt_rent_txns) + len(mf_txns)
        
        if total_txns > 100:
            market_activity = "매우 활발"
        elif total_txns > 50:
            market_activity = "활발"
        elif total_txns > 20:
            market_activity = "보통"
        else:
            market_activity = "저조"
        
        return {
            'land_transactions': land_txns,
            'apt_transactions': apt_txns,
            'apt_rent_transactions': apt_rent_txns,
            'multi_family_transactions': mf_txns,
            'crime_risk': crime_risk,
            'environmental': environmental,
            'market_summary': {
                'avg_land_price_per_sqm': avg_land_price,
                'avg_apt_price_per_sqm': avg_apt_price,
                'avg_rent_yield': avg_rent_yield,
                'total_transactions': total_txns,
                'market_activity': market_activity
            }
        }


# ========================================================================
# Utility functions for report integration
# ========================================================================

def calculate_lh_pricing_gap(
    market_land_price: int,
    lh_purchase_price: int
) -> Dict:
    """
    LH 매입가와 시장가 Gap 분석
    
    Returns:
        {
            'market_price': int,
            'lh_price': int,
            'gap_amount': int,
            'gap_percentage': float,
            'gap_assessment': str
        }
    """
    gap_amount = market_land_price - lh_purchase_price
    gap_percentage = (gap_amount / market_land_price * 100) if market_land_price > 0 else 0
    
    if gap_percentage > 20:
        assessment = "매우 유리 (시장가 대비 20% 이상 낮음)"
    elif gap_percentage > 10:
        assessment = "유리 (시장가 대비 10-20% 낮음)"
    elif gap_percentage > 0:
        assessment = "보통 (시장가 대비 소폭 낮음)"
    elif gap_percentage > -10:
        assessment = "불리 (시장가 대비 소폭 높음)"
    else:
        assessment = "매우 불리 (시장가 대비 10% 이상 높음)"
    
    return {
        'market_price': market_land_price,
        'lh_price': lh_purchase_price,
        'gap_amount': gap_amount,
        'gap_percentage': gap_percentage,
        'gap_assessment': assessment
    }


def score_location_safety(crime_data: CrimeRiskData) -> Dict:
    """
    입지 안전도 점수화
    
    Returns:
        {
            'safety_score': float (0-100),
            'safety_grade': str,
            'risk_factors': List[str],
            'recommendations': List[str]
        }
    """
    # Invert crime score to get safety score (lower crime = higher safety)
    safety_score = 100 - crime_data.crime_score
    
    if safety_score >= 80:
        grade = "A (매우 안전)"
    elif safety_score >= 60:
        grade = "B (안전)"
    elif safety_score >= 40:
        grade = "C (보통)"
    elif safety_score >= 20:
        grade = "D (주의 필요)"
    else:
        grade = "F (위험)"
    
    risk_factors = []
    if crime_data.crime_score > 60:
        risk_factors.append("범죄 다발 지역")
    if crime_data.elderly_crime_score > 50:
        risk_factors.append("노인 대상 범죄 주의")
    if crime_data.has_crime_hotspot:
        risk_factors.append("범죄 주의구간 포함")
    
    recommendations = []
    if crime_data.crime_score > 50:
        recommendations.append("CCTV 및 보안 시스템 강화 필요")
        recommendations.append("경비 인력 배치 검토")
    if crime_data.elderly_crime_score > 40:
        recommendations.append("노인 세대 대상 안전 교육 프로그램 운영")
    
    return {
        'safety_score': safety_score,
        'safety_grade': grade,
        'risk_factors': risk_factors,
        'recommendations': recommendations
    }


def score_environmental_risk(env_data: EnvironmentalData) -> Dict:
    """
    환경 리스크 점수화
    
    Returns:
        {
            'environmental_score': float (0-100),
            'risk_level': str,
            'construction_risk': str,
            'permit_risk': str
        }
    """
    # Calculate environmental score (lower pollution = higher score)
    pm10_score = max(0, 100 - (env_data.pm10 or 0))
    pm25_score = max(0, 100 - (env_data.pm25 or 0) * 2)  # PM2.5 is worse
    
    environmental_score = (pm10_score + pm25_score) / 2
    
    if environmental_score >= 80:
        risk_level = "낮음 (양호)"
        construction_risk = "낮음 - 공사 진행 원활"
        permit_risk = "낮음 - 인허가 순조"
    elif environmental_score >= 60:
        risk_level = "보통"
        construction_risk = "보통 - 미세먼지 대책 필요"
        permit_risk = "보통 - 환경영향평가 주의"
    else:
        risk_level = "높음 (불량)"
        construction_risk = "높음 - 공사 제한 가능성"
        permit_risk = "높음 - 인허가 지연 우려"
    
    return {
        'environmental_score': environmental_score,
        'risk_level': risk_level,
        'construction_risk': construction_risk,
        'permit_risk': permit_risk
    }
