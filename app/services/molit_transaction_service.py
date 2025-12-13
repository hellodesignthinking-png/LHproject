"""
ZeroSite v37.0 ULTIMATE - 국토부 실거래가 API
실제 토지 거래 데이터 조회

Author: Antenna Holdings Development Team
Date: 2025-12-13
Purpose: Fetch real land transaction data from MOLIT API
"""

import requests
import logging
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MOLITTransactionService:
    """국토부 토지 실거래가 조회"""
    
    # API 엔드포인트
    BASE_URL = "http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcLandTrade"
    
    def __init__(self, api_key: str):
        """
        초기화
        
        Args:
            api_key: 국토부 API 키
        """
        self.api_key = api_key
        logger.info("✅ MOLITTransactionService initialized")
    
    def get_transactions(
        self,
        lawd_cd: str,
        deal_ymd: str = None,
        num_rows: int = 100
    ) -> List[Dict]:
        """
        실거래가 조회
        
        Args:
            lawd_cd: 법정동코드 (5자리)
                예: "11680" (강남구)
            deal_ymd: 거래년월 (YYYYMM)
                예: "202401" (2024년 1월)
                None이면 현재 월
            num_rows: 조회 건수 (기본 100)
        
        Returns:
            [
                {
                    'deal_date': '2024-01-15',
                    'deal_amount': 500000000,  # 원
                    'land_area_sqm': 450.5,
                    'price_per_sqm': 1109877,
                    'address': '서울 강남구 역삼동 123-45',
                    'dong': '역삼동',
                    'jibun': '123-45',
                    'land_use': '대',  # 대지/전/답/임야
                    'transaction_type': '거래'
                },
                ...
            ]
        """
        
        try:
            # 거래년월 기본값: 현재 월
            if not deal_ymd:
                deal_ymd = datetime.now().strftime('%Y%m')
            
            logger.info(f"📊 실거래가 조회 시작")
            logger.info(f"   법정동코드: {lawd_cd}")
            logger.info(f"   거래년월: {deal_ymd}")
            
            params = {
                'serviceKey': self.api_key,
                'LAWD_CD': lawd_cd,
                'DEAL_YMD': deal_ymd,
                'numOfRows': num_rows,
                'pageNo': 1
            }
            
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=15
            )
            
            logger.debug(f"   HTTP 상태: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"❌ API 호출 실패: {response.status_code}")
                return []
            
            # XML 파싱
            root = ET.fromstring(response.content)
            
            # 결과 코드 확인
            result_code = root.find('.//resultCode')
            if result_code is not None and result_code.text != '00':
                logger.warning(f"⚠️ API 에러: {result_code.text}")
                return []
            
            # 거래 데이터 추출
            items = root.findall('.//item')
            
            if not items:
                logger.info("   ℹ️ 실거래 데이터 없음")
                return []
            
            transactions = []
            
            for item in items:
                try:
                    # 필드 추출
                    deal_year = item.find('dealYear')
                    deal_month = item.find('dealMonth')
                    deal_day = item.find('dealDay')
                    deal_amount = item.find('dealAmount')  # 천원 단위
                    area = item.find('area')  # ㎡
                    dong = item.find('umdNm')  # 읍면동
                    jibun = item.find('jibun')
                    land_use = item.find('landCd')  # 토지용도
                    
                    # 거래일
                    if all([deal_year, deal_month, deal_day]):
                        deal_date = f"{deal_year.text.strip()}-{deal_month.text.strip().zfill(2)}-{deal_day.text.strip().zfill(2)}"
                    else:
                        continue
                    
                    # 거래금액 (천원 → 원)
                    if deal_amount is not None:
                        amount_text = deal_amount.text.strip().replace(',', '')
                        amount = int(amount_text) * 1000
                    else:
                        continue
                    
                    # 면적 (㎡)
                    if area is not None:
                        area_sqm = float(area.text.strip())
                    else:
                        continue
                    
                    # ㎡당 단가
                    price_per_sqm = int(amount / area_sqm)
                    
                    # 주소 구성
                    dong_name = dong.text.strip() if dong is not None else ''
                    jibun_name = jibun.text.strip() if jibun is not None else ''
                    
                    transaction = {
                        'deal_date': deal_date,
                        'deal_amount': amount,
                        'land_area_sqm': area_sqm,
                        'price_per_sqm': price_per_sqm,
                        'dong': dong_name,
                        'jibun': jibun_name,
                        'land_use': land_use.text.strip() if land_use is not None else '',
                        'transaction_type': '거래'
                    }
                    
                    transactions.append(transaction)
                    
                except Exception as e:
                    logger.debug(f"거래 항목 파싱 오류: {e}")
                    continue
            
            logger.info(f"   ✅ 실거래 {len(transactions)}건 조회 성공")
            
            return transactions
            
        except Exception as e:
            logger.error(f"❌ 실거래가 조회 오류: {e}", exc_info=True)
            return []
    
    def get_transactions_multi_month(
        self,
        lawd_cd: str,
        months: int = 6
    ) -> List[Dict]:
        """
        최근 N개월 실거래 조회
        
        Args:
            lawd_cd: 법정동코드
            months: 조회 개월수 (기본 6개월)
        
        Returns:
            실거래 리스트
        """
        
        logger.info(f"📊 최근 {months}개월 실거래 조회")
        
        all_transactions = []
        
        for i in range(months):
            # N개월 전 계산
            date = datetime.now() - timedelta(days=30 * i)
            deal_ymd = date.strftime('%Y%m')
            
            transactions = self.get_transactions(lawd_cd, deal_ymd, num_rows=50)
            all_transactions.extend(transactions)
            
            # API 요청 간 짧은 대기 (rate limiting 방지)
            if i < months - 1:
                import time
                time.sleep(0.5)
        
        logger.info(f"   ✅ 최근 {months}개월 실거래 총 {len(all_transactions)}건")
        
        return all_transactions


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Test API key (replace with actual key)
    test_key = "702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d"
    
    service = MOLITTransactionService(test_key)
    
    print("=" * 80)
    print("MOLIT Transaction Service Test")
    print("=" * 80)
    
    # Test 1: 강남구 (11680)
    print("\n📍 Test 1: 서울 강남구")
    transactions = service.get_transactions("11680", "202411", num_rows=5)
    
    if transactions:
        print(f"✅ 조회 성공: {len(transactions)}건")
        for i, tx in enumerate(transactions[:3], 1):
            print(f"\n거래 {i}:")
            print(f"  날짜: {tx['deal_date']}")
            print(f"  면적: {tx['land_area_sqm']}㎡")
            print(f"  금액: {tx['deal_amount']:,}원")
            print(f"  단가: {tx['price_per_sqm']:,}원/㎡")
            print(f"  주소: {tx['dong']} {tx['jibun']}")
    else:
        print("❌ 조회 실패 또는 데이터 없음")
    
    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)
