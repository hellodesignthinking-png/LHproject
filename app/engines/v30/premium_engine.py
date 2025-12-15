"""
ZeroSite v30.0 - Premium Engine
Analyze location premiums and factors
Input: address, zone, nearby facilities
Output: premium_percentage, top_factors[]
"""
from typing import List, Dict, Tuple


class PremiumEngineV30:
    """Location premium analysis"""
    
    def __init__(self):
        self.premium_factors = {
            # Infrastructure
            '지하철 역세권 (300m 이내)': 15.0,
            '지하철 역세권 (500m 이내)': 8.0,
            '버스정류장 인접': 3.0,
            '주요 도로 접근성 우수': 7.0,
            
            # Commercial
            '상업지구 중심': 12.0,
            '대형 쇼핑몰 인접': 6.0,
            '편의시설 밀집': 5.0,
            
            # Education
            '학군 우수 지역': 10.0,
            '대학교 인접': 7.0,
            
            # Environment
            '공원 인접': 4.0,
            '한강 조망': 8.0,
            '저층 개발': -3.0,
            
            # Development
            '재개발/재건축 예정지': 20.0,
            '신규 개발지구': 15.0,
            
            # Corporate
            '대기업 본사 인접': 9.0,
            '업무지구 중심': 11.0,
        }
        
    def analyze_premium(self, si: str, gu: str, dong: str, 
                       zone_type: str, lat: float, lng: float) -> Dict[str, any]:
        """
        Analyze location premium
        
        Returns:
            {
                'premium_percentage': float,  # Total premium %
                'top_5_factors': List[{'factor': str, 'impact': float}],
                'total_factors': int
            }
        """
        detected_factors = self._detect_factors(si, gu, dong, zone_type)
        
        # Calculate total premium
        total_premium = sum(factor['impact'] for factor in detected_factors)
        
        # Cap premium at reasonable levels
        total_premium = min(total_premium, 50.0)  # Max 50%
        total_premium = max(total_premium, -10.0)  # Min -10%
        
        # Get top 5
        top_5 = sorted(detected_factors, key=lambda x: abs(x['impact']), reverse=True)[:5]
        
        return {
            'premium_percentage': round(total_premium, 1),
            'top_5_factors': top_5,
            'total_factors': len(detected_factors)
        }
    
    def _detect_factors(self, si: str, gu: str, dong: str, zone_type: str) -> List[Dict]:
        """Detect applicable premium factors"""
        factors = []
        
        # Zone-based factors
        if '상업' in zone_type:
            factors.append({'factor': '상업지구 중심', 'impact': 12.0})
            factors.append({'factor': '편의시설 밀집', 'impact': 5.0})
        
        if '주거' in zone_type:
            factors.append({'factor': '주거환경 양호', 'impact': 4.0})
        
        # Region-specific factors
        if si == '서울특별시':
            factors.append({'factor': '서울 프리미엄', 'impact': 8.0})
            
            if gu == '강남구':
                factors.append({'factor': '강남 프리미엄', 'impact': 15.0})
                factors.append({'factor': '학군 우수 지역', 'impact': 10.0})
                factors.append({'factor': '지하철 역세권 (300m 이내)', 'impact': 15.0})
                factors.append({'factor': '업무지구 중심', 'impact': 11.0})
                factors.append({'factor': '대기업 본사 인접', 'impact': 9.0})
            
            elif gu == '마포구' and dong == '상암동':
                factors.append({'factor': '신규 개발지구', 'impact': 15.0})
                factors.append({'factor': '지하철 역세권 (300m 이내)', 'impact': 15.0})
                factors.append({'factor': '한강 조망', 'impact': 8.0})
            
            elif gu == '송파구' and dong == '잠실동':
                factors.append({'factor': '지하철 역세권 (300m 이내)', 'impact': 15.0})
                factors.append({'factor': '대형 쇼핑몰 인접', 'impact': 6.0})
                factors.append({'factor': '한강 조망', 'impact': 8.0})
            
            elif gu == '관악구':
                factors.append({'factor': '대학교 인접', 'impact': 7.0})
                factors.append({'factor': '지하철 역세권 (500m 이내)', 'impact': 8.0})
        
        elif si == '부산광역시':
            factors.append({'factor': '부산 프리미엄', 'impact': 5.0})
            
            if gu == '해운대구':
                factors.append({'factor': '해안 조망', 'impact': 12.0})
                factors.append({'factor': '관광지구', 'impact': 8.0})
                factors.append({'factor': '지하철 역세권 (300m 이내)', 'impact': 15.0})
        
        elif '경기도' in si:
            if gu == '성남시':
                factors.append({'factor': '수도권 프리미엄', 'impact': 6.0})
                factors.append({'factor': '신규 개발지구', 'impact': 15.0})
        
        elif '제주' in si:
            factors.append({'factor': '관광 특구', 'impact': 10.0})
            factors.append({'factor': '환경 프리미엄', 'impact': 7.0})
        
        return factors


# Test function
if __name__ == "__main__":
    engine = PremiumEngineV30()
    
    test_cases = [
        ('서울특별시', '강남구', '역삼동', '근린상업지역', 37.5172, 127.0473),
        ('서울특별시', '관악구', '신림동', '제2종일반주거지역', 37.4784, 126.9516),
        ('부산광역시', '해운대구', '우동', '근린상업지역', 35.1631, 129.1635),
    ]
    
    for si, gu, dong, zone, lat, lng in test_cases:
        result = engine.analyze_premium(si, gu, dong, zone, lat, lng)
        print(f"{si} {gu} {dong}:")
        print(f"  Premium: +{result['premium_percentage']}%")
        print(f"  Top factors:")
        for factor in result['top_5_factors']:
            print(f"    - {factor['factor']}: +{factor['impact']}%")
        print()
