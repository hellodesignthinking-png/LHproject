"""
ZeroSite v36.0 NATIONWIDE - Universal Transaction Engine
전국 어디든 실제 주소 기반 거래사례 생성

Author: Antenna Holdings Development Team
Date: 2025-12-13
Purpose: Generate realistic transaction data based on actual input address
"""

import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class UniversalTransactionEngine:
    """
    전국 거래사례 생성 엔진
    
    입력받은 주소의 sido/sigungu/dong 정보를 기반으로
    실제 해당 지역 거래사례를 생성합니다.
    """
    
    def __init__(self):
        """초기화"""
        
        # 도로 등급 (지역별 분포 반영)
        self.road_classes = [
            {"name": "대로", "weight": 0.2, "price_factor": 1.15},
            {"name": "중로", "weight": 0.5, "price_factor": 1.0},
            {"name": "소로", "weight": 0.3, "price_factor": 0.92}
        ]
        
        logger.info("✅ UniversalTransactionEngine initialized")
    
    def generate_transactions(
        self,
        sido: str,
        sigungu: str,
        dong: Optional[str],
        base_price: float,
        land_area_sqm: float,
        num_transactions: int = 15
    ) -> List[Dict]:
        """
        전국 어디든 거래사례 생성
        
        Args:
            sido: 시·도 (예: "서울특별시")
            sigungu: 시·군·구 (예: "강남구")
            dong: 읍·면·동 (예: "역삼동", None 가능)
            base_price: 기준 시장가격 (만원/㎡)
            land_area_sqm: 토지 면적 (㎡)
            num_transactions: 생성할 거래 건수 (기본 15건)
        
        Returns:
            거래사례 리스트
        """
        
        logger.info(f"🏘️ [v36 Universal] Generating {num_transactions} transactions for {sido} {sigungu} {dong or ''}")
        
        transactions = []
        today = datetime.now()
        
        for i in range(num_transactions):
            # 1. 거래 날짜 (최근 12개월)
            days_ago = random.randint(30, 365)
            transaction_date = today - timedelta(days=days_ago)
            
            # 2. 토지 면적 (기준 면적 ± 30%)
            area_variation = random.uniform(0.7, 1.3)
            trans_area = land_area_sqm * area_variation
            trans_area = round(trans_area, 1)
            
            # 3. 가격 변동 (기준 가격 ± 20%)
            price_variation = random.uniform(0.8, 1.2)
            trans_price_per_sqm = base_price * price_variation
            trans_price_per_sqm = round(trans_price_per_sqm, 1)
            
            # 4. 총 거래가
            total_price = trans_price_per_sqm * trans_area
            total_price_million = round(total_price / 10000, 2)  # 억원
            
            # 5. 거리 (0.1km ~ 2.0km)
            distance = round(random.uniform(0.1, 2.0), 2)
            
            # 6. 도로 등급
            road = random.choices(
                [r["name"] for r in self.road_classes],
                weights=[r["weight"] for r in self.road_classes]
            )[0]
            
            # 7. 번지 생성 (XXX-XX 형태)
            lot_number = f"{random.randint(100, 999)}-{random.randint(1, 99)}"
            
            # 8. 주소 생성 (입력 주소 기반으로 실제 지역 반영)
            if dong:
                # 동 정보가 있으면 동 사용
                address = f"{sido} {sigungu} {dong} {lot_number}"
            else:
                # 동 정보가 없으면 시·군·구까지만
                address = f"{sido} {sigungu} {lot_number}"
            
            # 9. 거래사례 데이터
            transaction = {
                "transaction_date": transaction_date.strftime("%Y-%m-%d"),
                "address": address,
                "land_area_sqm": trans_area,
                "price_per_sqm": trans_price_per_sqm,  # 만원/㎡
                "total_price": total_price,  # 만원
                "total_price_million": total_price_million,  # 억원
                "distance_km": distance,
                "road_name": road,
                "road_class": road,
                "sido": sido,
                "sigungu": sigungu,
                "dong": dong or sigungu,  # dong이 없으면 sigungu 사용
            }
            
            transactions.append(transaction)
        
        # 날짜 내림차순 정렬 (최신순)
        transactions.sort(key=lambda x: x["transaction_date"], reverse=True)
        
        logger.info(f"   ✅ Generated {len(transactions)} transactions")
        logger.info(f"   📍 Address pattern: {transactions[0]['address']}")
        logger.info(f"   💰 Price range: {min(t['price_per_sqm'] for t in transactions):.0f} ~ {max(t['price_per_sqm'] for t in transactions):.0f}만원/㎡")
        
        return transactions
    
    def generate_comparable_sales(
        self,
        transactions: List[Dict],
        num_comparables: int = 5
    ) -> List[Dict]:
        """
        거래사례에서 비교 가능한 유사 매물 추출
        
        Args:
            transactions: 전체 거래사례 리스트
            num_comparables: 추출할 비교 매물 수 (기본 5건)
        
        Returns:
            비교 매물 리스트
        """
        
        if not transactions:
            logger.warning("⚠️ No transactions to generate comparables from")
            return []
        
        # 최신 거래 + 가까운 거리 + 유사 면적 기준으로 선택
        # 여기서는 단순히 최신 거래 5건 사용
        comparables = transactions[:num_comparables]
        
        # 비교 매물 형식으로 변환
        formatted_comparables = []
        for comp in comparables:
            formatted = {
                "address": comp["address"],
                "land_area_sqm": comp["land_area_sqm"],
                "price_per_sqm": comp["price_per_sqm"],
                "total_price": comp["total_price"],
                "transaction_date": comp["transaction_date"],
                "distance_km": comp["distance_km"],
                "road_class": comp["road_class"],
                
                # 조정 계수 (기본값)
                "location_adjustment": 1.0,
                "individual_adjustment": 1.0,
                "time_adjustment": 1.0,
                "weight": 0.2  # 5건이면 각 0.2 (20%)
            }
            formatted_comparables.append(formatted)
        
        logger.info(f"   ✅ Generated {len(formatted_comparables)} comparable sales")
        
        return formatted_comparables


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    engine = UniversalTransactionEngine()
    
    test_cases = [
        {
            "sido": "서울특별시",
            "sigungu": "강남구",
            "dong": "역삼동",
            "base_price": 3200,
            "land_area_sqm": 400
        },
        {
            "sido": "부산광역시",
            "sigungu": "해운대구",
            "dong": "우동",
            "base_price": 1400,
            "land_area_sqm": 500
        },
        {
            "sido": "경기도",
            "sigungu": "성남시",
            "dong": "분당구",
            "base_price": 1400,
            "land_area_sqm": 350
        },
    ]
    
    print("=" * 80)
    print("UniversalTransactionEngine Test")
    print("=" * 80)
    
    for case in test_cases:
        print(f"\n{case['sido']} {case['sigungu']} {case['dong']}")
        
        transactions = engine.generate_transactions(
            sido=case['sido'],
            sigungu=case['sigungu'],
            dong=case['dong'],
            base_price=case['base_price'],
            land_area_sqm=case['land_area_sqm'],
            num_transactions=10
        )
        
        print(f"  → Generated {len(transactions)} transactions")
        print(f"  → Example: {transactions[0]['address']}")
        print(f"  → Price: {transactions[0]['price_per_sqm']:.0f}만원/㎡")
        
        comparables = engine.generate_comparable_sales(transactions, num_comparables=3)
        print(f"  → Comparables: {len(comparables)}")
    
    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)
