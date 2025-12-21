"""
Enhanced Transaction Generator for ZeroSite Expert v3

Dynamic algorithmic generation of comparable transactions
Replaces static mock data with realistic price gradients
"""

import math
import random
from datetime import datetime, timedelta
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class Transaction:
    """Land transaction record"""
    address: str
    lat: float
    lng: float
    size_sqm: float
    price_per_sqm: float
    total_price: float
    zone_type: str
    transaction_date: datetime
    distance_km: float
    days_since_transaction: int


class EnhancedTransactionGenerator:
    """
    Dynamic transaction generator using price gradient algorithms
    
    Improvements over existing:
    - Algorithmic generation (not static data)
    - Distance-based price gradients
    - Time-based price decay
    - Realistic variations
    """
    
    # Regional base prices (₩ per m²)
    REGIONAL_BASE_PRICES = {
        "서울특별시": {
            "강남구": 15_000_000,
            "서초구": 14_000_000,
            "송파구": 12_000_000,
            "강동구": 11_000_000,
            "마포구": 11_000_000,
            "용산구": 13_000_000,
            "영등포구": 10_000_000,
            "강서구": 8_000_000,
            "구로구": 9_000_000,
            "관악구": 8_500_000,
            "default": 10_000_000
        },
        "경기도": {
            "성남시": 8_000_000,
            "용인시": 7_000_000,
            "화성시": 6_000_000,
            "수원시": 7_500_000,
            "고양시": 7_000_000,
            "남양주시": 6_000_000,
            "평택시": 5_500_000,
            "default": 5_000_000
        },
        "인천광역시": {
            "연수구": 6_000_000,
            "남동구": 5_500_000,
            "서구": 5_000_000,
            "default": 5_000_000
        },
        "부산광역시": {
            "해운대구": 7_000_000,
            "수영구": 6_500_000,
            "default": 5_000_000
        },
        "default": {
            "default": 4_000_000
        }
    }
    
    ZONE_TYPES = [
        "제1종일반주거지역",
        "제2종일반주거지역",
        "제3종일반주거지역",
        "준주거지역",
        "준공업지역"
    ]
    
    def generate_comparables(
        self,
        center_lat: float,
        center_lng: float,
        region: str,
        district: str,
        target_zone: str,
        target_size_sqm: float,
        radius_km: float = 1.5,
        count: int = 10,
        seed: int = None  # 🔧 NEW: Seed for deterministic generation
    ) -> List[Transaction]:
        """
        Generate N comparable transactions dynamically
        
        Algorithm:
        1. Generate random points within radius (polar coordinates)
        2. Calculate distance-based price gradient
        3. Apply time-based price decay
        4. Add realistic random variations
        
        Args:
            center_lat: Target location latitude
            center_lng: Target location longitude
            region: Administrative region
            district: District name
            target_zone: Target zone type
            target_size_sqm: Target land size
            radius_km: Search radius
            count: Number of transactions
        
        Returns:
            List of Transaction objects sorted by distance
        """
        # 🔧 Set random seed for deterministic generation
        if seed is not None:
            random.seed(seed)
        
        base_price = self._get_base_price(region, district)
        transactions = []
        
        for i in range(count):
            # Generate random location within radius
            distance_km, lat, lng = self._random_point_in_circle(
                center_lat, center_lng, radius_km
            )
            
            # Distance gradient: closer = higher price
            # Linear decrease: -15% over full radius
            distance_factor = 1.0 - (distance_km / radius_km) * 0.15
            
            # Time decay: older = lower price
            days_ago = random.randint(30, 720)  # 1 month ~ 2 years
            time_factor = 1.0 - (days_ago / 730) * 0.12  # -12% over 2 years
            
            # Size variation
            size_variation = random.uniform(0.5, 1.5)
            size_sqm = target_size_sqm * size_variation
            
            # Size premium/discount
            if size_sqm < target_size_sqm * 0.7:
                size_factor = 1.05  # Small parcels cost more per m²
            elif size_sqm > target_size_sqm * 1.3:
                size_factor = 0.95  # Large parcels cost less per m²
            else:
                size_factor = 1.0
            
            # Final price with noise
            price_per_sqm = base_price * distance_factor * time_factor * size_factor
            price_per_sqm *= random.uniform(0.90, 1.10)  # ±10% noise
            price_per_sqm = int(price_per_sqm)
            
            # Total price
            total_price = price_per_sqm * size_sqm
            
            # Transaction date
            transaction_date = datetime.now() - timedelta(days=days_ago)
            
            # Zone (70% same, 30% different)
            zone_type = target_zone if random.random() < 0.7 else random.choice(self.ZONE_TYPES)
            
            # Create transaction
            transaction = Transaction(
                address=self._generate_address(lat, lng, region, district),
                lat=lat,
                lng=lng,
                size_sqm=round(size_sqm, 1),
                price_per_sqm=price_per_sqm,
                total_price=total_price,
                zone_type=zone_type,
                transaction_date=transaction_date,
                distance_km=round(distance_km, 2),
                days_since_transaction=days_ago
            )
            
            transactions.append(transaction)
        
        # Sort by distance (closest first)
        transactions.sort(key=lambda t: t.distance_km)
        
        return transactions
    
    def _get_base_price(self, region: str, district: str) -> float:
        """Get regional base price per m²"""
        if region in self.REGIONAL_BASE_PRICES:
            region_prices = self.REGIONAL_BASE_PRICES[region]
            return region_prices.get(district, region_prices["default"])
        return self.REGIONAL_BASE_PRICES["default"]["default"]
    
    def _random_point_in_circle(
        self, center_lat: float, center_lng: float, radius_km: float
    ) -> Tuple[float, float, float]:
        """
        Generate random point within circle (uniform area distribution)
        
        Returns: (distance_km, lat, lng)
        """
        # Use sqrt for uniform area distribution
        u = random.random()
        distance_km = radius_km * math.sqrt(u)
        
        # Random angle
        angle = random.uniform(0, 2 * math.pi)
        
        # Convert to lat/lng offset
        lat_offset = (distance_km / 111.0) * math.cos(angle)
        lng_offset = (distance_km / (111.0 * math.cos(math.radians(center_lat)))) * math.sin(angle)
        
        lat = center_lat + lat_offset
        lng = center_lng + lng_offset
        
        return distance_km, lat, lng
    
    def _generate_address(self, lat: float, lng: float, region: str, district: str) -> str:
        """Generate mock Korean address"""
        dong_names = ["역삼동", "삼성동", "논현동", "신사동", "청담동", "대치동"]
        dong = random.choice(dong_names)
        
        # Generate lot number from coordinates
        lot_main = int(abs(lat + lng) * 1000) % 500 + 1
        lot_sub = int(abs(lat * lng) * 10000) % 100
        
        lot_number = f"{lot_main}-{lot_sub}" if lot_sub > 0 else str(lot_main)
        
        return f"{region} {district} {dong} {lot_number}"


# Test
if __name__ == "__main__":
    generator = EnhancedTransactionGenerator()
    
    txns = generator.generate_comparables(
        center_lat=37.5172,
        center_lng=127.0473,
        region="서울특별시",
        district="강남구",
        target_zone="제2종일반주거지역",
        target_size_sqm=1000.0,
        radius_km=1.5,
        count=10
    )
    
    print("Enhanced Transaction Generator Test\n" + "="*50)
    print(f"\nGenerated {len(txns)} transactions:")
    
    for i, txn in enumerate(txns, 1):
        print(f"\n{i}. {txn.address}")
        print(f"   Distance: {txn.distance_km}km | Size: {txn.size_sqm:,.0f}m²")
        print(f"   Price: ₩{txn.price_per_sqm:,}/m² | Total: ₩{txn.total_price:,.0f}")
