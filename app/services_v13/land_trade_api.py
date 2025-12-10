"""
ZeroSite v23 - Real Land Value Engine
실거래가 API 통합 모듈

국토부 실거래가 API를 통해 토지 거래 정보를 조회하고
Market Land Value를 계산하는 핵심 모듈

Author: ZeroSite AI Analysis System
Version: v23
Date: 2025-12-10
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from xml.etree import ElementTree as ET

# Logging setup
logger = logging.getLogger(__name__)

# 국토부 API 키
API_KEY = "5158584967f97600a71afc331e848ad6c8154524d2266a6ad62c22c5f5c9ad87"

# API Endpoints
API_ENDPOINTS = {
    'land_trade': 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/RTMSDataSvcLandTrade/getRTMSDataSvcLandTrade',
    'house_single': 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSSvc/getRTMSDataSvcSHTrade',
    'house_multi': 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSSvc/getRTMSDataSvcRHTrade',
    'commercial': 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSSvc/getRTMSDataSvcNrgTrade'
}


class LandTradeAPI:
    """국토부 실거래가 API 클라이언트"""
    
    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key
        
    def _call_api(self, endpoint: str, params: dict) -> Optional[ET.Element]:
        """
        API 호출 공통 함수
        
        Args:
            endpoint: API URL
            params: 요청 파라미터
            
        Returns:
            XML 응답 Element 또는 None
        """
        try:
            params['serviceKey'] = self.api_key
            
            logger.info(f"API 호출: {endpoint}")
            logger.debug(f"파라미터: {params}")
            
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            # XML 파싱
            root = ET.fromstring(response.content)
            
            # 결과 코드 확인
            result_code = root.find('.//resultCode')
            if result_code is not None and result_code.text != '00':
                result_msg = root.find('.//resultMsg')
                logger.error(f"API 오류: {result_msg.text if result_msg is not None else 'Unknown error'}")
                return None
                
            return root
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API 요청 실패: {str(e)}")
            return None
        except ET.ParseError as e:
            logger.error(f"XML 파싱 실패: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"예상치 못한 오류: {str(e)}")
            return None
    
    def get_recent_months(self, count: int = 12) -> List[str]:
        """
        최근 N개월의 YYYYMM 리스트 생성
        
        Args:
            count: 개월 수 (기본 12개월)
            
        Returns:
            ['202512', '202511', ...] 형식의 리스트
        """
        today = datetime.now()
        months = []
        
        for i in range(count):
            date = today - timedelta(days=30 * i)
            months.append(date.strftime('%Y%m'))
            
        return months
    
    def get_land_trades(
        self, 
        lawd_cd: str,
        months: int = 12,
        min_area: float = 0,
        max_area: float = float('inf')
    ) -> List[Dict]:
        """
        토지 실거래가 조회
        
        Args:
            lawd_cd: 법정동 코드 (5자리, 예: 11680)
            months: 조회 개월 수
            min_area: 최소 면적(㎡)
            max_area: 최대 면적(㎡)
            
        Returns:
            거래 정보 리스트
        """
        all_trades = []
        
        for deal_ymd in self.get_recent_months(months):
            params = {
                'LAWD_CD': lawd_cd,
                'DEAL_YMD': deal_ymd,
                'numOfRows': '100'
            }
            
            root = self._call_api(API_ENDPOINTS['land_trade'], params)
            if root is None:
                continue
            
            # items 추출
            items = root.findall('.//item')
            
            for item in items:
                try:
                    # XML에서 필요한 데이터 추출
                    trade = {
                        'deal_date': self._get_text(item, 'dealYear') + '-' + 
                                   self._get_text(item, 'dealMonth').zfill(2) + '-' + 
                                   self._get_text(item, 'dealDay').zfill(2),
                        'deal_amount': self._parse_number(self._get_text(item, 'dealAmount')),  # 만원
                        'land_area': float(self._get_text(item, 'landArea', '0')),  # ㎡
                        'land_type': self._get_text(item, 'landType'),
                        'district': self._get_text(item, 'sggNm'),
                        'dong': self._get_text(item, 'umdNm'),
                        'jibun': self._get_text(item, 'jibun'),
                        'building_purpose': self._get_text(item, 'buildingPurpose', ''),
                    }
                    
                    # 면적 필터링
                    if min_area <= trade['land_area'] <= max_area:
                        # 단가 계산 (만원/㎡)
                        if trade['land_area'] > 0:
                            trade['price_per_sqm'] = round(trade['deal_amount'] / trade['land_area'], 1)
                        else:
                            trade['price_per_sqm'] = 0
                        
                        all_trades.append(trade)
                        
                except (ValueError, TypeError) as e:
                    logger.warning(f"거래 데이터 파싱 실패: {str(e)}")
                    continue
        
        # 최신순 정렬
        all_trades.sort(key=lambda x: x['deal_date'], reverse=True)
        
        logger.info(f"총 {len(all_trades)}건의 거래 조회 완료")
        return all_trades
    
    def _get_text(self, element: ET.Element, tag: str, default: str = '') -> str:
        """XML element에서 텍스트 추출"""
        child = element.find(tag)
        return child.text.strip() if child is not None and child.text else default
    
    def _parse_number(self, text: str) -> float:
        """숫자 문자열 파싱 (쉼표 제거)"""
        try:
            return float(text.replace(',', ''))
        except (ValueError, AttributeError):
            return 0.0


class LandValueCalculator:
    """토지가격 계산 엔진"""
    
    def __init__(self):
        self.api = LandTradeAPI()
    
    def calculate_market_value(
        self,
        address: str,
        lawd_cd: str,
        land_area_sqm: float,
        target_area_sqm: Optional[float] = None,
        months: int = 12
    ) -> Dict:
        """
        시장 토지가치 계산
        
        Args:
            address: 주소
            lawd_cd: 법정동 코드
            land_area_sqm: 대상 토지 면적(㎡)
            target_area_sqm: 유사 거래 필터링용 면적(없으면 land_area_sqm 사용)
            months: 조회 개월 수
            
        Returns:
            {
                'trades': 거래 리스트,
                'avg_price_per_sqm': 평균 단가(만원/㎡),
                'median_price_per_sqm': 중앙값 단가(만원/㎡),
                'market_land_value_eok': 시장 토지가치(억원),
                'reliability': 신뢰도 ('HIGH', 'MEDIUM', 'LOW'),
                'data_source': 데이터 소스 설명
            }
        """
        if target_area_sqm is None:
            target_area_sqm = land_area_sqm
        
        # 유사 거래 면적 범위 (±30%)
        min_area = target_area_sqm * 0.7
        max_area = target_area_sqm * 1.3
        
        # 실거래가 조회
        trades = self.api.get_land_trades(
            lawd_cd=lawd_cd,
            months=months,
            min_area=min_area,
            max_area=max_area
        )
        
        # Case A: 거래 10건 이상
        if len(trades) >= 10:
            selected_trades = trades[:10]
            reliability = 'HIGH'
            data_source = f'최근 {months}개월 실거래가 {len(selected_trades)}건 평균'
            
        # Case B: 거래 1~9건
        elif len(trades) > 0:
            selected_trades = trades
            reliability = 'MEDIUM'
            data_source = f'최근 {months}개월 실거래가 {len(selected_trades)}건 평균 (데이터 부족)'
            
        # Case C: 거래 0건 - 확장 조회 시도
        else:
            logger.warning(f"거래 데이터 없음. 조건 완화 시도...")
            
            # 면적 제한 없이 재조회
            trades_all = self.api.get_land_trades(
                lawd_cd=lawd_cd,
                months=months,
                min_area=0,
                max_area=float('inf')
            )
            
            if len(trades_all) > 0:
                selected_trades = trades_all[:10]
                reliability = 'LOW'
                data_source = f'최근 {months}개월 전체 거래 {len(selected_trades)}건 평균 (면적 무관)'
            else:
                # 완전 실패 - Fallback 필요
                return {
                    'trades': [],
                    'avg_price_per_sqm': 0,
                    'median_price_per_sqm': 0,
                    'market_land_value_eok': 0,
                    'reliability': 'NONE',
                    'data_source': 'CAPEX Fallback 적용 필요'
                }
        
        # 평균/중앙값 계산
        prices = [t['price_per_sqm'] for t in selected_trades]
        avg_price = sum(prices) / len(prices)
        median_price = sorted(prices)[len(prices) // 2]
        
        # 시장 토지가치 (억원)
        market_value_eok = round(avg_price * land_area_sqm / 10000, 2)
        
        return {
            'trades': selected_trades,
            'avg_price_per_sqm': round(avg_price, 1),
            'median_price_per_sqm': round(median_price, 1),
            'market_land_value_eok': market_value_eok,
            'market_land_value_won': avg_price * land_area_sqm * 10000,
            'reliability': reliability,
            'data_source': data_source,
            'trade_count': len(selected_trades)
        }
    
    def calculate_lh_appraisal(
        self,
        market_land_value_won: float,
        gross_floor_area: float,
        appraisal_rate: float = 0.92,
        standard_cost_per_sqm: float = 3500000
    ) -> Dict:
        """
        LH 감정평가 계산
        
        Args:
            market_land_value_won: 시장 토지가치(원)
            gross_floor_area: 연면적(㎡)
            appraisal_rate: 감정평가율 (기본 92%)
            standard_cost_per_sqm: LH 표준건축비(원/㎡, 기본 350만원)
            
        Returns:
            {
                'land_appraisal_won': 토지 감정가(원),
                'land_appraisal_eok': 토지 감정가(억원),
                'building_appraisal_won': 건물 감정가(원),
                'building_appraisal_eok': 건물 감정가(억원),
                'total_appraisal_won': 총 감정가(원),
                'total_appraisal_eok': 총 감정가(억원),
                'purchase_price_eok': LH 매입가(억원)
            }
        """
        # 토지 감정가
        land_appraisal_won = market_land_value_won * appraisal_rate
        land_appraisal_eok = round(land_appraisal_won / 1e8, 2)
        
        # 건물 감정가
        building_appraisal_won = standard_cost_per_sqm * gross_floor_area
        building_appraisal_eok = round(building_appraisal_won / 1e8, 2)
        
        # 총 감정가
        total_appraisal_won = land_appraisal_won + building_appraisal_won
        total_appraisal_eok = round(total_appraisal_won / 1e8, 2)
        
        # LH 매입가 (신축매입임대는 100%)
        purchase_price_eok = total_appraisal_eok
        
        return {
            'land_appraisal_won': land_appraisal_won,
            'land_appraisal_eok': land_appraisal_eok,
            'building_appraisal_won': building_appraisal_won,
            'building_appraisal_eok': building_appraisal_eok,
            'total_appraisal_won': total_appraisal_won,
            'total_appraisal_eok': total_appraisal_eok,
            'purchase_price_won': total_appraisal_won,
            'purchase_price_eok': purchase_price_eok,
            'appraisal_rate': appraisal_rate,
            'standard_cost_per_sqm': standard_cost_per_sqm
        }
    
    def calculate_capex_land_cost(
        self,
        capex_won: float,
        market_land_value_won: float = 0,
        use_dynamic_ratio: bool = True
    ) -> Dict:
        """
        CAPEX 토지비 계산 (Fallback)
        
        Args:
            capex_won: 총 사업비(원)
            market_land_value_won: 시장 토지가치(원, 있으면 동적 비율 계산)
            use_dynamic_ratio: 동적 비율 사용 여부
            
        Returns:
            {
                'land_cost_won': 토지비(원),
                'land_cost_eok': 토지비(억원),
                'land_cost_ratio': 토지비 비율,
                'calculation_method': 계산 방식
            }
        """
        if use_dynamic_ratio and market_land_value_won > 0:
            # 동적 비율 계산
            ratio = market_land_value_won / capex_won
            
            # 최소 15%, 최대 50%로 제한
            ratio = max(0.15, min(0.50, ratio))
            
            land_cost_won = capex_won * ratio
            method = f'시장가 기반 동적 비율 ({ratio*100:.1f}%)'
            
        else:
            # 고정 비율 25% (기존 방식)
            ratio = 0.25
            land_cost_won = capex_won * ratio
            method = '고정 비율 (25%)'
        
        land_cost_eok = round(land_cost_won / 1e8, 2)
        
        return {
            'land_cost_won': land_cost_won,
            'land_cost_eok': land_cost_eok,
            'land_cost_ratio': ratio,
            'land_cost_ratio_pct': round(ratio * 100, 1),
            'calculation_method': method
        }
    
    def calculate_all(
        self,
        address: str,
        lawd_cd: str,
        land_area_sqm: float,
        gross_floor_area: float,
        capex_won: float,
        appraisal_price_manwon: Optional[float] = None
    ) -> Dict:
        """
        통합 토지가격 계산 (3계층)
        
        Args:
            address: 주소
            lawd_cd: 법정동 코드
            land_area_sqm: 토지 면적(㎡)
            gross_floor_area: 연면적(㎡)
            capex_won: 총 사업비(원)
            appraisal_price_manwon: Fallback 감정평가액(만원/㎡)
            
        Returns:
            Complete land value data
        """
        result = {}
        
        # Layer 1: 시장 거래가
        market_data = self.calculate_market_value(
            address=address,
            lawd_cd=lawd_cd,
            land_area_sqm=land_area_sqm
        )
        result['market'] = market_data
        
        # Layer 2: LH 감정평가
        if market_data['market_land_value_won'] > 0:
            lh_data = self.calculate_lh_appraisal(
                market_land_value_won=market_data['market_land_value_won'],
                gross_floor_area=gross_floor_area
            )
            result['lh_appraisal'] = lh_data
        else:
            # Fallback: 감정평가액 기반
            if appraisal_price_manwon:
                fallback_value_won = appraisal_price_manwon * 10000 * land_area_sqm
                lh_data = self.calculate_lh_appraisal(
                    market_land_value_won=fallback_value_won,
                    gross_floor_area=gross_floor_area
                )
                result['lh_appraisal'] = lh_data
                result['lh_appraisal']['fallback'] = True
            else:
                result['lh_appraisal'] = None
        
        # Layer 3: CAPEX 토지비
        capex_data = self.calculate_capex_land_cost(
            capex_won=capex_won,
            market_land_value_won=market_data.get('market_land_value_won', 0),
            use_dynamic_ratio=True
        )
        result['capex'] = capex_data
        
        # 메타데이터
        result['metadata'] = {
            'calculation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'address': address,
            'lawd_cd': lawd_cd,
            'land_area_sqm': land_area_sqm,
            'gross_floor_area': gross_floor_area,
            'capex_eok': round(capex_won / 1e8, 2)
        }
        
        return result


# 편의 함수
def get_lawd_code_from_address(address: str) -> Optional[str]:
    """
    주소에서 법정동 코드 추출
    
    임시 구현: 주요 서울 지역 매핑
    실제로는 카카오 API 또는 행정안전부 API 사용 필요
    """
    region_codes = {
        '강남구': '11680',
        '서초구': '11650',
        '송파구': '11710',
        '마포구': '11440',
        '성동구': '11200',
        '용산구': '11170',
        '영등포구': '11560',
        '광진구': '11215',
        '동작구': '11590',
        '종로구': '11110'
    }
    
    for region, code in region_codes.items():
        if region in address:
            return code
    
    # 기본값: 강남구
    logger.warning(f"주소에서 지역 코드 찾기 실패. 강남구 코드 사용: {address}")
    return '11680'


if __name__ == '__main__':
    # 테스트 코드
    logging.basicConfig(level=logging.INFO)
    
    calculator = LandValueCalculator()
    
    # 강남 테스트
    result = calculator.calculate_all(
        address='서울특별시 강남구 역삼동 825',
        lawd_cd='11680',
        land_area_sqm=1100,
        gross_floor_area=2200,
        capex_won=30000000000,  # 300억원
        appraisal_price_manwon=2200
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
