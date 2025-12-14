#!/usr/bin/env python3
"""
주소별 개별공시지가 및 용도지역 확인 스크립트
"""
import sys
sys.path.insert(0, '/home/user/webapp')

from app.engines.v30.landprice_engine import LandPriceEngineV30
from app.engines.v30.zoning_engine import ZoningEngineV30
from app.engines.v30.official_data_scraper import OfficialDataScraper

def check_address(si, gu, dong, jibun='', lat=None, lng=None):
    """주소의 공시지가와 용도지역을 여러 소스에서 확인"""
    print("=" * 80)
    print(f"주소: {si} {gu} {dong} {jibun}")
    print("=" * 80)
    
    # 1. Land Price Engine 확인
    print("\n1️⃣ Land Price Engine (V-World API → Scraper → Fallback)")
    price_engine = LandPriceEngineV30()
    if lat and lng:
        price_result = price_engine.get_land_price(lat, lng, '', si, gu, dong, jibun)
    else:
        price_result = price_engine._get_price_fallback(si, gu, dong, jibun)
    
    print(f"   공시지가: ₩{price_result['official_price']:,}/㎡")
    print(f"   기준년도: {price_result['year']}")
    print(f"   방법: {price_result['method']}")
    
    # 2. Zoning Engine 확인
    print("\n2️⃣ Zoning Engine (V-World API → Scraper → Fallback)")
    zoning_engine = ZoningEngineV30()
    if lat and lng:
        zone_result = zoning_engine.get_zone_type(lat, lng, si, gu, dong, jibun)
    else:
        zone_result = zoning_engine._get_zone_fallback(si, gu, dong, jibun)
    
    print(f"   용도지역: {zone_result['zone_type']}")
    print(f"   방법: {zone_result['method']}")
    
    # 3. Official Data Scraper 직접 확인
    print("\n3️⃣ Official Data Scraper (PNU → Nationwide → Regional)")
    scraper = OfficialDataScraper()
    scraper_result = scraper.get_land_price_and_zoning(si, gu, dong, jibun)
    
    print(f"   공시지가: ₩{scraper_result['official_land_price_per_sqm']:,}/㎡")
    print(f"   용도지역: {scraper_result['zone_type']}")
    print(f"   소스: {scraper_result['source']}")
    print(f"   신뢰도: {scraper_result['confidence']}")
    if scraper_result.get('note'):
        print(f"   비고: {scraper_result['note']}")
    
    # 4. 비교 분석
    print("\n" + "=" * 80)
    print("📊 비교 분석")
    print("=" * 80)
    
    # 공시지가 비교
    prices = [
        ("Land Price Engine", price_result['official_price']),
        ("Official Scraper", scraper_result['official_land_price_per_sqm'])
    ]
    
    print("\n공시지가:")
    for name, price in prices:
        print(f"   {name:25s}: ₩{price:>12,}/㎡")
    
    if prices[0][1] != prices[1][1]:
        diff = abs(prices[0][1] - prices[1][1])
        pct = (diff / max(prices[0][1], prices[1][1])) * 100
        print(f"   ⚠️  차이: ₩{diff:,}/㎡ ({pct:.1f}%)")
    
    # 용도지역 비교
    zones = [
        ("Zoning Engine", zone_result['zone_type']),
        ("Official Scraper", scraper_result['zone_type'])
    ]
    
    print("\n용도지역:")
    for name, zone in zones:
        print(f"   {name:25s}: {zone}")
    
    if zones[0][1] != zones[1][1]:
        print(f"   ⚠️  불일치 발견!")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    # 테스트할 주소들
    test_addresses = [
        {
            'name': '서울 관악구 신림동 1524-8',
            'si': '서울특별시',
            'gu': '관악구',
            'dong': '신림동',
            'jibun': '1524-8',
            'lat': 37.4847,
            'lng': 126.9295
        },
        {
            'name': '서울 강남구 역삼동 680-11',
            'si': '서울특별시',
            'gu': '강남구',
            'dong': '역삼동',
            'jibun': '680-11',
            'lat': 37.5172,
            'lng': 127.0473
        },
        {
            'name': '부산 해운대구 우동 1500-1',
            'si': '부산광역시',
            'gu': '해운대구',
            'dong': '우동',
            'jibun': '1500-1',
            'lat': 35.1631,
            'lng': 129.1635
        },
        {
            'name': '경기 성남시 분당구 정자동 100-1',
            'si': '경기도',
            'gu': '성남시 분당구',
            'dong': '정자동',
            'jibun': '100-1',
            'lat': 37.3595,
            'lng': 127.1088
        }
    ]
    
    print("\n" + "🔍 " * 20)
    print("ZeroSite 주소별 데이터 소스 확인")
    print("🔍 " * 20 + "\n")
    
    for addr in test_addresses:
        check_address(
            si=addr['si'],
            gu=addr['gu'],
            dong=addr['dong'],
            jibun=addr['jibun'],
            lat=addr.get('lat'),
            lng=addr.get('lng')
        )
        print("\n")
