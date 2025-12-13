"""
국토부 실거래가 API 통합 프로세서
12개 API 엔드포인트를 활용한 종합 부동산 시세 분석
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from config.api_keys import APIKeys
except ImportError:
    # Fallback if config module not available
    class APIKeys:
        MOLIT_API_KEY = "5158584967f97600a71afc331e848ad6c8154524d2266a6ad62c22c5f5c9ad87"
        
        @classmethod
        def get_molit_key(cls):
            return cls.MOLIT_API_KEY

logger = logging.getLogger(__name__)

@dataclass
class Transaction:
    """실거래 데이터 표준 형식"""
    transaction_date: str          # 거래일자 (YYYY-MM-DD)
    price_per_sqm: float           # ㎡당 단가
    land_area_sqm: float           # 토지/전용면적
    total_price: float             # 총 거래가
    location: str                  # 위치 (동·리)
    building_type: str             # 건물유형 (토지/아파트/오피스텔 등)
    deal_year_month: str           # 거래년월 (YYYYMM)
    floor: Optional[int] = None    # 층수 (건물인 경우)

class MOLITRealPriceAPI:
    """
    국토부 실거래가 API 12개 통합 클래스
    """
    
    # 12개 API 엔드포인트 정의
    API_ENDPOINTS = {
        'land': {
            'name': '토지 매매',
            'url': 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/RTMSOBJSvc/getRTMSDataSvcLandTrade',
            'priority': 1
        },
        'apt_trade': {
            'name': '아파트 매매',
            'url': 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade',
            'priority': 2
        },
        'apt_trade_dev': {
            'name': '아파트 매매 상세',
            'url': 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev',
            'priority': 3
        },
        'rh_trade': {
            'name': '연립다세대 매매',
            'url': 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcRHTrade',
            'priority': 4
        },
        'offi_trade': {
            'name': '오피스텔 매매',
            'url': 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcOffiTrade',
            'priority': 5
        },
        'sh_trade': {
            'name': '단독/다가구 매매',
            'url': 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcSHTrade',
            'priority': 6
        }
    }
    
    # 서울 지역코드 매핑 (법정동코드 5자리)
    DISTRICT_CODES = {
        "강남구": "11680", "강동구": "11740", "강북구": "11305",
        "강서구": "11500", "관악구": "11620", "광진구": "11215",
        "구로구": "11530", "금천구": "11545", "노원구": "11350",
        "도봉구": "11320", "동대문구": "11230", "동작구": "11590",
        "마포구": "11440", "서대문구": "11410", "서초구": "11650",
        "성동구": "11200", "성북구": "11290", "송파구": "11710",
        "양천구": "11470", "영등포구": "11560", "용산구": "11170",
        "은평구": "11380", "종로구": "11110", "중구": "11140",
        "중랑구": "11260"
    }
    
    def __init__(self):
        self.api_key = APIKeys.get_molit_key()
        
        if not self.api_key or len(self.api_key) < 20:
            logger.error("⚠️ 유효하지 않은 국토부 API 키")
            logger.error(f"현재 키 길이: {len(self.api_key) if self.api_key else 0}")
    
    def get_comprehensive_market_data(self,
                                     address: str,
                                     land_area_sqm: float,
                                     num_months: int = 24,
                                     min_transactions: int = 5) -> Dict:
        """
        12개 API를 활용한 종합 실거래 데이터 수집
        """
        
        # Step 1: 지역코드 추출
        district = self._extract_district(address)
        district_code = self.DISTRICT_CODES.get(district)
        
        if not district_code:
            logger.warning(f"⚠️ 지역코드 찾기 실패: {district}, Fallback 사용")
            return self._generate_fallback_data(address, land_area_sqm)
        
        logger.info(f"📍 분석 지역: {district} (코드: {district_code})")
        
        # Step 2: 조회 기간 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30 * num_months)
        
        logger.info(f"📅 조회 기간: {start_date.strftime('%Y-%m')} ~ {end_date.strftime('%Y-%m')}")
        
        # Step 3: 12개 API 순차 호출
        all_transactions = []
        api_stats = {}
        
        sorted_apis = sorted(
            self.API_ENDPOINTS.items(),
            key=lambda x: x[1]['priority']
        )
        
        for api_key, api_info in sorted_apis:
            if api_info['priority'] > 6 and len(all_transactions) >= min_transactions:
                logger.info(f"⏭️  {api_info['name']} API 스킵 (충분한 데이터 확보)")
                continue
            
            logger.info(f"📡 {api_info['name']} API 호출 중...")
            
            try:
                transactions = self._fetch_api_data(
                    api_url=api_info['url'],
                    district_code=district_code,
                    start_date=start_date,
                    end_date=end_date,
                    land_area_sqm=land_area_sqm,
                    building_type=api_info['name']
                )
                
                all_transactions.extend(transactions)
                api_stats[api_key] = len(transactions)
                
                logger.info(f"   ✅ {len(transactions)}건 수집 (총 {len(all_transactions)}건)")
                
                time.sleep(0.3)  # API 호출 간 딜레이
                
            except Exception as e:
                logger.warning(f"   ⚠️ API 호출 실패: {str(e)}")
                api_stats[api_key] = 0
        
        # Step 4: 결과 평가
        if len(all_transactions) < min_transactions:
            logger.warning(f"⚠️ 거래사례 부족: {len(all_transactions)}건 (최소 {min_transactions}건)")
            logger.warning(f"📌 Fallback 데이터 사용")
            return self._generate_fallback_data(address, land_area_sqm)
        
        # Step 5: 통계 계산
        avg_price = self._calculate_time_weighted_average(all_transactions)
        
        logger.info("="*60)
        logger.info(f"✅ 종합 실거래 데이터 수집 완료")
        logger.info(f"📊 총 거래사례: {len(all_transactions)}건")
        logger.info(f"💰 평균 단가: {avg_price:,.0f}원/㎡")
        logger.info("="*60)
        
        return {
            'transactions': all_transactions,
            'count': len(all_transactions),
            'avg_price_per_sqm': avg_price,
            'data_source': 'MOLIT_COMPREHENSIVE_API',
            'confidence': self._calculate_confidence(len(all_transactions)),
            'district': district,
            'period': f"{start_date.strftime('%Y-%m')} ~ {end_date.strftime('%Y-%m')}",
            'api_stats': api_stats,
            'warning': None
        }
    
    def _fetch_api_data(self,
                       api_url: str,
                       district_code: str,
                       start_date: datetime,
                       end_date: datetime,
                       land_area_sqm: float,
                       building_type: str) -> List[Transaction]:
        """개별 API 호출 및 데이터 파싱"""
        
        transactions = []
        current_date = start_date
        
        while current_date <= end_date:
            year_month = current_date.strftime("%Y%m")
            
            try:
                params = {
                    'serviceKey': self.api_key,
                    'LAWD_CD': district_code,
                    'DEAL_YMD': year_month,
                    'numOfRows': 1000,
                    'pageNo': 1
                }
                
                response = requests.get(api_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    month_transactions = self._parse_xml_response(
                        response.text,
                        land_area_sqm,
                        building_type
                    )
                    transactions.extend(month_transactions)
                
            except Exception as e:
                logger.debug(f"   월별 조회 실패 ({year_month}): {str(e)}")
            
            current_date = current_date + timedelta(days=32)
            current_date = current_date.replace(day=1)
        
        return transactions
    
    def _parse_xml_response(self,
                           xml_text: str,
                           target_land_area: float,
                           building_type: str) -> List[Transaction]:
        """국토부 API XML 응답 파싱"""
        
        transactions = []
        
        try:
            root = ET.fromstring(xml_text)
            
            result_code = root.find('.//resultCode')
            if result_code is not None and result_code.text != '00':
                return []
            
            items = root.findall('.//item')
            
            for item in items:
                try:
                    tx = self._parse_transaction_item(item, target_land_area, building_type)
                    if tx:
                        transactions.append(tx)
                except:
                    continue
        
        except ET.ParseError:
            pass
        
        return transactions
    
    def _parse_transaction_item(self,
                                item: ET.Element,
                                target_land_area: float,
                                building_type: str) -> Optional[Transaction]:
        """개별 거래 항목 파싱"""
        
        try:
            if '토지' in building_type:
                deal_amount = item.find('dealAmount')
                land_area = item.find('landArea')
                
                if deal_amount is None or land_area is None:
                    return None
                
                total_price = float(deal_amount.text.replace(',', '').strip()) * 10000
                area_sqm = float(land_area.text.strip())
                
            else:
                deal_amount = item.find('dealAmount')
                exclusive_area = item.find('excluUseAr')
                
                if deal_amount is None or exclusive_area is None:
                    return None
                
                total_price = float(deal_amount.text.replace(',', '').strip()) * 10000
                area_sqm = float(exclusive_area.text.strip())
            
            # 유사 규모 필터링 (±50%)
            if area_sqm < target_land_area * 0.5 or area_sqm > target_land_area * 1.5:
                return None
            
            price_per_sqm = total_price / area_sqm
            
            # 비정상 거래 필터링 (㎡당 100만원 ~ 5천만원)
            if price_per_sqm < 1_000_000 or price_per_sqm > 50_000_000:
                return None
            
            year = item.find('dealYear')
            month = item.find('dealMonth')
            day = item.find('dealDay')
            
            year_str = year.text.strip() if year is not None else '2024'
            month_str = month.text.strip().zfill(2) if month is not None else '01'
            day_str = day.text.strip().zfill(2) if day is not None else '01'
            
            transaction_date = f"{year_str}-{month_str}-{day_str}"
            
            sigungu = item.find('sigungu')
            dong = item.find('dong') or item.find('umdNm')
            
            location = f"{sigungu.text if sigungu is not None else ''} {dong.text if dong is not None else ''}".strip()
            
            floor_elem = item.find('floor')
            floor = int(floor_elem.text) if floor_elem is not None else None
            
            return Transaction(
                transaction_date=transaction_date,
                price_per_sqm=price_per_sqm,
                land_area_sqm=area_sqm,
                total_price=total_price,
                location=location,
                building_type=building_type,
                deal_year_month=f"{year_str}{month_str}",
                floor=floor
            )
        
        except Exception as e:
            return None
    
    def _calculate_time_weighted_average(self, transactions: List[Transaction]) -> float:
        """시점 가중 평균 계산"""
        
        if not transactions:
            return 0
        
        now = datetime.now()
        total_weighted_price = 0
        total_weight = 0
        
        for tx in transactions:
            try:
                tx_date = datetime.strptime(tx.transaction_date, "%Y-%m-%d")
                days_ago = (now - tx_date).days
                
                # 시점 가중치
                if days_ago <= 90:
                    weight = 1.3
                elif days_ago <= 180:
                    weight = 1.1
                elif days_ago <= 365:
                    weight = 0.8
                else:
                    weight = 0.5
                
                # 토지 거래 추가 가중치
                if '토지' in tx.building_type:
                    weight *= 1.5
                
                total_weighted_price += tx.price_per_sqm * weight
                total_weight += weight
            except:
                continue
        
        return total_weighted_price / total_weight if total_weight > 0 else 0
    
    def _calculate_confidence(self, transaction_count: int) -> str:
        """데이터 신뢰도 계산"""
        if transaction_count >= 20:
            return 'HIGH'
        elif transaction_count >= 10:
            return 'MEDIUM'
        elif transaction_count >= 5:
            return 'LOW'
        else:
            return 'VERY_LOW'
    
    def _extract_district(self, address: str) -> str:
        """주소에서 구 추출 - 도로명 주소도 지원"""
        # 먼저 주소 문자열에서 직접 찾기
        for district in self.DISTRICT_CODES.keys():
            if district in address:
                return district
        
        # 도로명 주소인 경우 geocoding으로 법정동 주소 얻기
        try:
            import requests
            kakao_api_key = os.getenv("KAKAO_API_KEY")
            if not kakao_api_key:
                logger.warning("⚠️ Kakao API 키 없음, 지역 추출 실패")
                return None
            
            url = "https://dapi.kakao.com/v2/local/search/address.json"
            headers = {"Authorization": f"KakaoAK {kakao_api_key}"}
            params = {"query": address}
            
            response = requests.get(url, headers=headers, params=params, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('documents'):
                    # 법정동 주소에서 구 추출
                    address_name = data['documents'][0].get('address_name', '')
                    road_address_name = data['documents'][0].get('road_address', {}).get('address_name', '') if data['documents'][0].get('road_address') else ''
                    
                    full_address = f"{address_name} {road_address_name}"
                    
                    for district in self.DISTRICT_CODES.keys():
                        if district in full_address:
                            logger.info(f"✅ Geocoding으로 지역 찾음: {district} (입력: {address})")
                            return district
            else:
                logger.warning(f"⚠️ Kakao geocoding 실패: {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Geocoding 오류: {e}")
        
        return None
    
    def _generate_fallback_data(self, address: str, land_area_sqm: float) -> Dict:
        """Fallback 데이터 (실제 API 데이터 수집 실패 시)"""
        
        district = self._extract_district(address)
        
        # 서울 구별 2024년 추정 평균 단가 (㎡당) - 최신 시세 반영
        fallback_prices = {
            "강남구": 18_500_000, "서초구": 16_000_000, "송파구": 14_000_000,
            "용산구": 14_500_000, "성동구": 12_000_000, "마포구": 12_000_000,
            "영등포구": 10_500_000, "강서구": 9_000_000, "강동구": 9_500_000,
            "노원구": 8_000_000, "관악구": 8_500_000, "은평구": 8_200_000
        }
        
        estimated_price = fallback_prices.get(district, 10_000_000)
        
        logger.warning("="*60)
        logger.warning("⚠️⚠️⚠️ FALLBACK 데이터 사용 중 ⚠️⚠️⚠️")
        logger.warning(f"실제 국토부 API에서 데이터를 가져오지 못했습니다.")
        logger.warning(f"지역: {district}")
        logger.warning(f"추정 단가: {estimated_price:,.0f}원/㎡")
        logger.warning("="*60)
        
        return {
            'transactions': [],
            'count': 0,
            'avg_price_per_sqm': estimated_price,
            'data_source': 'FALLBACK',
            'confidence': 'VERY_LOW',
            'district': district,
            'warning': f'⚠️ 실제 거래 데이터 없음 - {district} 추정치 사용'
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    print("🔍 국토부 12개 API 통합 테스트")
    print("="*60)
    
    api = MOLITRealPriceAPI()
    
    result = api.get_comprehensive_market_data(
        address="서울특별시 강남구 역삼동",
        land_area_sqm=660.0,
        num_months=24,
        min_transactions=5
    )
    
    print(f"\n📊 결과:")
    print(f"   출처: {result['data_source']}")
    print(f"   신뢰도: {result['confidence']}")
    print(f"   거래 건수: {result['count']}건")
    print(f"   평균 단가: {result['avg_price_per_sqm']:,.0f}원/㎡")
    
    if result['count'] > 0:
        total_value = result['avg_price_per_sqm'] * 660.0
        print(f"   660㎡ 토지 시장가치: {total_value/100_000_000:.1f}억원")
