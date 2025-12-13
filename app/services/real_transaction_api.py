"""
MOLIT Real Transaction API
국토교통부 실거래가 API 연동

API Key: 5158584967f97600a71afc331e848ad6c8154524d2266a6ad62c22c5f5c9ad87
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import time
import math

logger = logging.getLogger(__name__)


class MOLITRealTransactionAPI:
    """
    국토교통부 실거래가 API 연동
    
    주요 기능:
    1. 토지 매매 실거래가 조회 (RTMSDataSvcLandTrade)
    2. 다중 개월 데이터 수집
    3. 거리 필터링 (Haversine)
    """
    
    BASE_URL = "http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc"
    API_KEY = "5158584967f97600a71afc331e848ad6c8154524d2266a6ad62c22c5f5c9ad87"
    
    # 서울시 시군구 코드
    SIGUNGU_CODES = {
        '강남구': '11680',
        '강동구': '11740',
        '강북구': '11305',
        '강서구': '11500',
        '관악구': '11620',
        '광진구': '11215',
        '구로구': '11530',
        '금천구': '11545',
        '노원구': '11350',
        '도봉구': '11320',
        '동대문구': '11230',
        '동작구': '11590',
        '마포구': '11440',
        '서대문구': '11410',
        '서초구': '11650',
        '성동구': '11200',
        '성북구': '11290',
        '송파구': '11710',
        '양천구': '11470',
        '영등포구': '11560',
        '용산구': '11170',
        '은평구': '11380',
        '종로구': '11110',
        '중구': '11140',
        '중랑구': '11260'
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        초기화
        
        Args:
            api_key: 국토부 API 키 (없으면 기본값 사용)
        """
        self.api_key = api_key or self.API_KEY
        logger.info(f"✅ MOLIT API initialized with key: {self.api_key[:20]}...")
    
    
    def get_land_transactions(
        self,
        sigungu_code: str,
        year_month: str,
        num_rows: int = 100
    ) -> List[Dict]:
        """
        토지 매매 실거래가 조회
        
        Args:
            sigungu_code: 시군구 코드 (예: 11680 = 강남구)
            year_month: 년월 (예: 202411)
            num_rows: 조회 개수 (최대 100)
            
        Returns:
            거래 리스트
        """
        
        endpoint = f"{self.BASE_URL}/getRTMSDataSvcLandTrade"
        
        params = {
            'serviceKey': self.api_key,
            'LAWD_CD': sigungu_code,
            'DEAL_YMD': year_month,
            'numOfRows': num_rows,
            'pageNo': 1
        }
        
        try:
            logger.info(f"🔍 MOLIT API 호출: {year_month} ({self._get_sigungu_name(sigungu_code)})")
            
            response = requests.get(endpoint, params=params, timeout=15)
            
            if response.status_code != 200:
                logger.error(f"❌ API HTTP 오류: {response.status_code}")
                return []
            
            # XML 파싱
            root = ET.fromstring(response.content)
            
            # resultCode 확인
            result_code = root.find('.//resultCode')
            if result_code is not None and result_code.text != '00':
                result_msg = root.find('.//resultMsg')
                error_msg = result_msg.text if result_msg is not None else "Unknown error"
                logger.error(f"❌ API 에러: {result_code.text} - {error_msg}")
                return []
            
            # 거래 데이터 추출
            transactions = []
            
            for item in root.findall('.//item'):
                try:
                    transaction = self._parse_transaction_item(item, sigungu_code)
                    if transaction:
                        transactions.append(transaction)
                        
                except Exception as e:
                    logger.warning(f"⚠️ 거래 데이터 파싱 오류: {e}")
                    continue
            
            logger.info(f"✅ {year_month}: {len(transactions)}건 수집")
            return transactions
            
        except Exception as e:
            logger.error(f"❌ API 호출 오류: {e}", exc_info=True)
            return []
    
    
    def _parse_transaction_item(self, item: ET.Element, sigungu_code: str) -> Optional[Dict]:
        """
        XML item 요소를 거래 딕셔너리로 변환
        
        Args:
            item: XML item 요소
            sigungu_code: 시군구 코드
            
        Returns:
            거래 딕셔너리 또는 None
        """
        
        # 필수 필드 추출
        deal_amount = item.find('dealAmount')
        deal_year = item.find('dealYear') or item.find('dealingYear')
        deal_month = item.find('dealMonth') or item.find('dealingMonth')
        deal_day = item.find('dealDay') or item.find('dealingDay')
        
        area = item.find('landArea') or item.find('area')
        dong = item.find('dong') or item.find('umdNm')
        jibun = item.find('jibun') or item.find('lotNumber')
        
        # 필수 필드 검증
        if not all([deal_amount, deal_year, deal_month, deal_day, area]):
            logger.debug("필수 필드 누락")
            return None
        
        try:
            # 거래금액 (만원 → 원)
            amount_str = deal_amount.text.strip().replace(',', '').replace(' ', '')
            total_price = int(amount_str) * 10000
            
            # 면적 (㎡)
            area_str = area.text.strip().replace(',', '')
            area_sqm = float(area_str)
            
            if area_sqm <= 0:
                return None
            
            # 단가 계산
            price_per_sqm = int(total_price / area_sqm)
            
            # 거래일자
            year = deal_year.text.strip()
            month = deal_month.text.strip().zfill(2)
            day = deal_day.text.strip().zfill(2)
            transaction_date = f"{year}-{month}-{day}"
            
            # 주소 구성
            sigungu_name = self._get_sigungu_name(sigungu_code)
            dong_str = dong.text.strip() if dong is not None else ""
            jibun_str = jibun.text.strip() if jibun is not None else ""
            
            # 법정동 주소
            address_jibun = f"서울 {sigungu_name} {dong_str} {jibun_str}".strip()
            
            return {
                'transaction_date': transaction_date,
                'address': address_jibun,
                'address_jibun': address_jibun,
                'land_area_sqm': area_sqm,
                'total_price': total_price,
                'price_per_sqm': price_per_sqm,
                'dong': dong_str,
                'jibun': jibun_str,
                'sigungu': sigungu_name,
                'source': 'MOLIT_API'
            }
            
        except (ValueError, AttributeError) as e:
            logger.debug(f"데이터 변환 오류: {e}")
            return None
    
    
    def get_multi_month_transactions(
        self,
        sigungu_code: str,
        num_months: int = 24,
        delay_seconds: float = 0.5
    ) -> List[Dict]:
        """
        최근 N개월 거래 데이터 수집
        
        Args:
            sigungu_code: 시군구 코드
            num_months: 조회 개월 수 (기본: 24개월)
            delay_seconds: API 호출 간격 (초)
            
        Returns:
            전체 거래 리스트 (시간순 정렬)
        """
        
        all_transactions = []
        current_date = datetime.now()
        
        logger.info(f"📊 다중 개월 수집 시작: {num_months}개월")
        
        for i in range(num_months):
            # 날짜 계산
            target_date = current_date - timedelta(days=30 * i)
            year_month = target_date.strftime("%Y%m")
            
            # API 호출
            transactions = self.get_land_transactions(sigungu_code, year_month)
            
            if transactions:
                all_transactions.extend(transactions)
            
            # API 호출 제한 대응
            if i < num_months - 1:
                time.sleep(delay_seconds)
        
        # 날짜순 정렬 (최신순)
        all_transactions.sort(key=lambda x: x['transaction_date'], reverse=True)
        
        logger.info(f"✅ 총 {len(all_transactions)}건 수집 완료")
        
        return all_transactions
    
    
    def filter_by_distance(
        self,
        transactions: List[Dict],
        target_coords: tuple,
        max_distance_km: float = 2.0
    ) -> List[Dict]:
        """
        거리 필터링 (Haversine)
        
        Args:
            transactions: 거래 리스트
            target_coords: 대상 좌표 (위도, 경도)
            max_distance_km: 최대 거리 (km)
            
        Returns:
            필터링된 거래 리스트 (거리 포함, 거리순 정렬)
        """
        
        logger.info(f"📏 거리 필터링: 기준 좌표 {target_coords}, 최대 {max_distance_km}km")
        
        # 카카오 지오코딩 import
        try:
            from app.services.kakao_geocoding import KakaoGeocoding
            kakao = KakaoGeocoding()
        except:
            logger.warning("⚠️ 카카오 API 로드 실패, 거리 계산 불가")
            return transactions[:15]  # 최신 15건 반환
        
        filtered = []
        
        for tx in transactions:
            # 주소 → 좌표
            coords = kakao.get_coordinates(tx['address'])
            
            if not coords:
                continue
            
            # 거리 계산
            distance = self._haversine_distance(target_coords, coords)
            
            if distance <= max_distance_km:
                tx['distance_km'] = round(distance, 2)
                tx['coords'] = coords
                filtered.append(tx)
        
        # 거리순 정렬
        filtered.sort(key=lambda x: x['distance_km'])
        
        logger.info(f"✅ {len(filtered)}건이 {max_distance_km}km 이내")
        
        return filtered
    
    
    def _haversine_distance(self, coord1: tuple, coord2: tuple) -> float:
        """
        Haversine 거리 계산 (km)
        
        Args:
            coord1: (위도1, 경도1)
            coord2: (위도2, 경도2)
            
        Returns:
            거리 (km)
        """
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        R = 6371  # 지구 반지름 (km)
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(dlat / 2) ** 2 +
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
            math.sin(dlon / 2) ** 2
        )
        
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    
    def _get_sigungu_name(self, code: str) -> str:
        """시군구 코드 → 이름 변환"""
        
        for name, sigungu_code in self.SIGUNGU_CODES.items():
            if sigungu_code == code:
                return name
        
        return "알수없음"
    
    
    def extract_sigungu_code(self, address: str) -> Optional[str]:
        """
        주소에서 시군구 코드 추출
        
        Args:
            address: 주소 문자열
            
        Returns:
            시군구 코드 또는 None
        """
        
        for gu_name, code in self.SIGUNGU_CODES.items():
            if gu_name in address:
                return code
        
        return None


# Singleton instance
_molit_api = None


def get_molit_api() -> MOLITRealTransactionAPI:
    """MOLIT API 싱글톤 인스턴스 반환"""
    global _molit_api
    if _molit_api is None:
        _molit_api = MOLITRealTransactionAPI()
    return _molit_api
