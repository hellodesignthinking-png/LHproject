"""
ZeroSite v34.0 - Smart Transaction Collector
Dynamically generates transaction data based on actual address parsing
"""

import random
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt

logger = logging.getLogger(__name__)


class SmartTransactionCollectorV34:
    """
    Smart transaction collector that generates realistic transaction data
    based on actual gu/dong from address parsing
    """
    
    def __init__(self):
        """Initialize with real market prices by district"""
        
        # Real market prices by gu (2024 baseline, KRW per sqm)
        self.MARKET_PRICES = {
            '강남구': {
                'base': 20000000,
                'dongs': {
                    '역삼동': 22000000,
                    '삼성동': 21000000,
                    '대치동': 19000000,
                    '청담동': 24000000,
                    '압구정동': 23000000,
                    '논현동': 18000000,
                    '신사동': 19000000,
                    '개포동': 17000000,
                    '일원동': 16000000
                }
            },
            '서초구': {
                'base': 18000000,
                'dongs': {
                    '서초동': 20000000,
                    '잠원동': 19000000,
                    '반포동': 21000000,
                    '방배동': 16000000,
                    '양재동': 15000000,
                    '내곡동': 14000000
                }
            },
            '송파구': {
                'base': 16000000,
                'dongs': {
                    '잠실동': 18000000,
                    '신천동': 17000000,
                    '풍납동': 14000000,
                    '송파동': 15000000,
                    '가락동': 14500000,
                    '문정동': 16000000
                }
            },
            '마포구': {
                'base': 13000000,
                'dongs': {
                    '상암동': 15000000,
                    '공덕동': 16000000,
                    '서교동': 14000000,
                    '합정동': 13500000,
                    '연남동': 13000000,
                    '망원동': 11000000,
                    '성산동': 12000000
                }
            },
            '관악구': {
                'base': 9000000,
                'dongs': {
                    '신림동': 10000000,
                    '봉천동': 9000000,
                    '남현동': 8500000
                }
            },
            '영등포구': {
                'base': 14000000,
                'dongs': {
                    '여의도동': 18000000,
                    '영등포동': 13000000,
                    '당산동': 14000000,
                    '양평동': 12000000
                }
            },
            '강서구': {
                'base': 10000000,
                'dongs': {
                    '화곡동': 11000000,
                    '등촌동': 10000000,
                    '발산동': 10500000
                }
            },
            '양천구': {
                'base': 11500000,
                'dongs': {
                    '목동': 13000000,
                    '신정동': 11000000,
                    '신월동': 10500000
                }
            },
            '구로구': {
                'base': 9000000,
                'dongs': {
                    '구로동': 9500000,
                    '신도림동': 10000000,
                    '가리봉동': 8500000
                }
            },
            '동작구': {
                'base': 11000000,
                'dongs': {
                    '상도동': 11500000,
                    '흑석동': 10500000,
                    '노량진동': 11000000
                }
            },
            '용산구': {
                'base': 17000000,
                'dongs': {
                    '한남동': 20000000,
                    '이촌동': 18000000,
                    '용산동': 16000000
                }
            },
            '성동구': {
                'base': 13000000,
                'dongs': {
                    '성수동': 14000000,
                    '금호동': 12000000,
                    '옥수동': 13000000
                }
            },
            '광진구': {
                'base': 12000000,
                'dongs': {
                    '자양동': 13000000,
                    '구의동': 12000000,
                    '광장동': 11500000
                }
            },
            '중구': {
                'base': 15000000,
                'dongs': {
                    '을지로동': 16000000,
                    '명동': 18000000,
                    '장충동': 14000000
                }
            },
            '종로구': {
                'base': 14000000,
                'dongs': {
                    '청운동': 15000000,
                    '사직동': 14000000,
                    '평창동': 16000000
                }
            }
        }
    
    def collect_transactions(
        self,
        address: str,
        gu: str,
        dong: str,
        land_area_sqm: float,
        num_transactions: int = 15
    ) -> List[Dict]:
        """
        Collect (generate) transaction data based on actual gu/dong
        
        Args:
            address: Original address string
            gu: Parsed gu name (e.g., "관악구")
            dong: Parsed dong name (e.g., "신림동")
            land_area_sqm: Land area in square meters
            num_transactions: Number of transactions to generate
            
        Returns:
            List of transaction dictionaries with:
            - transaction_date: Date string (YYYY-MM-DD)
            - address: Full address using actual gu/dong
            - land_area_sqm: Land area
            - price_per_sqm: Price per square meter
            - total_price: Total transaction price
            - distance_km: Distance from subject property
            - road_name: Road name
            - road_class: Road classification
            - gu: Gu name
            - dong: Dong name
        """
        
        logger.info(f"🔍 Collecting transactions for: {gu} {dong}, Area: {land_area_sqm}㎡")
        
        # Get base price for this gu/dong
        base_price = self._get_base_price(gu, dong)
        
        logger.info(f"💰 Base price for {gu} {dong}: {base_price:,} KRW/㎡")
        
        # Generate transactions
        transactions = []
        
        for i in range(num_transactions):
            # Transaction date (within last 24 months)
            days_ago = random.randint(30, 730)
            tx_date = datetime.now() - timedelta(days=days_ago)
            
            # Area (±30% variation from subject property)
            area = land_area_sqm * random.uniform(0.7, 1.3)
            
            # Price per sqm (±15% variation from base)
            price = base_price * random.uniform(0.85, 1.15)
            
            # Distance (200m to 2km)
            distance = round(random.uniform(0.2, 2.0), 2)
            
            # Generate jibun (lot number)
            jibun = f"{random.randint(100, 999)}-{random.randint(1, 50)}"
            
            # Create full address using ACTUAL gu and dong
            full_address = f"서울 {gu} {dong} {jibun}"
            
            # Generate road name based on dong
            dong_base = dong.replace('동', '')
            road_options = [
                f"{dong_base}로",
                f"{dong_base}대로",
                f"{dong_base}길",
                f"{dong_base}중앙로"
            ]
            road_name = random.choice(road_options)
            
            # Road classification
            if '대로' in road_name:
                road_class = '대로'
            elif '로' in road_name:
                road_class = '중로'
            else:
                road_class = '소로'
            
            transactions.append({
                'transaction_date': tx_date.strftime('%Y-%m-%d'),
                'address': full_address,
                'land_area_sqm': round(area, 1),
                'price_per_sqm': int(price),
                'total_price': int(area * price),
                'distance_km': distance,
                'road_name': road_name,
                'road_class': road_class,
                'gu': gu,
                'dong': dong
            })
        
        # Sort by distance (nearest first)
        transactions.sort(key=lambda x: x['distance_km'])
        
        logger.info(f"✅ Generated {len(transactions)} transactions for {gu} {dong}")
        
        return transactions
    
    def _get_base_price(self, gu: str, dong: str) -> int:
        """
        Get base price for specific gu/dong
        
        Args:
            gu: Gu name
            dong: Dong name
            
        Returns:
            Base price per square meter (KRW)
        """
        
        if gu not in self.MARKET_PRICES:
            logger.warning(f"⚠️ No price data for {gu}, using default")
            return 9000000  # Default fallback
        
        gu_data = self.MARKET_PRICES[gu]
        
        # If dong-specific price exists, use it
        if dong and dong in gu_data['dongs']:
            return gu_data['dongs'][dong]
        
        # Otherwise, use gu average
        return gu_data['base']
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        
        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate
            
        Returns:
            Distance in kilometers
        """
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Earth radius in kilometers
        r = 6371
        
        return c * r
