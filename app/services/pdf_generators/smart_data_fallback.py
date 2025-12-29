"""
Smart Data Fallback Engine for ZeroSite
========================================

Intelligent data inference system that eliminates N/A values
by using multi-level fallback strategies.

Version: v5.0 ENHANCED
Date: 2025-12-29
"""

from typing import Dict, Any, Optional, List
import re
import logging

logger = logging.getLogger(__name__)


class SmartDataFallback:
    """Smart data fallback engine with regional defaults"""
    
    # 지역별 기본값 데이터베이스
    REGIONAL_DEFAULTS = {
        '서울': {
            'land_value_per_pyeong': 5000,  # 만원/평
            'subway_distance': 500,  # m
            'school_distance': 800,
            'hospital_distance': 600,
            'commercial_distance': 400,
            'preferred_type': '청년 1인 가구형',
            'optimal_units': 22,
            'parking_ratio': 0.7,
            'construction_cost_per_sqm': 3.5,  # 백만원/㎡
        },
        '경기': {
            'land_value_per_pyeong': 3000,
            'subway_distance': 1000,
            'school_distance': 600,
            'hospital_distance': 800,
            'commercial_distance': 600,
            'preferred_type': '신혼부부·자녀양육형',
            'optimal_units': 20,
            'parking_ratio': 0.8,
            'construction_cost_per_sqm': 3.2,
        },
        '인천': {
            'land_value_per_pyeong': 2500,
            'subway_distance': 800,
            'school_distance': 700,
            'hospital_distance': 700,
            'commercial_distance': 500,
            'preferred_type': '일반 가구형',
            'optimal_units': 25,
            'parking_ratio': 0.75,
            'construction_cost_per_sqm': 3.0,
        },
        '부산': {
            'land_value_per_pyeong': 2800,
            'subway_distance': 700,
            'school_distance': 600,
            'hospital_distance': 500,
            'commercial_distance': 400,
            'preferred_type': '청년 1인 가구형',
            'optimal_units': 23,
            'parking_ratio': 0.7,
            'construction_cost_per_sqm': 3.1,
        },
        '대구': {
            'land_value_per_pyeong': 2000,
            'subway_distance': 900,
            'school_distance': 700,
            'hospital_distance': 600,
            'commercial_distance': 500,
            'preferred_type': '일반 가구형',
            'optimal_units': 20,
            'parking_ratio': 0.8,
            'construction_cost_per_sqm': 2.8,
        },
        '광주': {
            'land_value_per_pyeong': 1800,
            'subway_distance': 1200,
            'school_distance': 800,
            'hospital_distance': 700,
            'commercial_distance': 600,
            'preferred_type': '일반 가구형',
            'optimal_units': 18,
            'parking_ratio': 0.85,
            'construction_cost_per_sqm': 2.7,
        },
        '대전': {
            'land_value_per_pyeong': 2200,
            'subway_distance': 1000,
            'school_distance': 700,
            'hospital_distance': 600,
            'commercial_distance': 500,
            'preferred_type': '신혼부부·자녀양육형',
            'optimal_units': 21,
            'parking_ratio': 0.8,
            'construction_cost_per_sqm': 2.9,
        },
        '울산': {
            'land_value_per_pyeong': 1900,
            'subway_distance': 1500,
            'school_distance': 800,
            'hospital_distance': 800,
            'commercial_distance': 700,
            'preferred_type': '일반 가구형',
            'optimal_units': 19,
            'parking_ratio': 0.9,
            'construction_cost_per_sqm': 2.8,
        },
        '세종': {
            'land_value_per_pyeong': 2500,
            'subway_distance': 2000,
            'school_distance': 500,
            'hospital_distance': 600,
            'commercial_distance': 800,
            'preferred_type': '신혼부부·자녀양육형',
            'optimal_units': 22,
            'parking_ratio': 0.9,
            'construction_cost_per_sqm': 3.0,
        },
        # 기본값 (전국 평균)
        'default': {
            'land_value_per_pyeong': 2500,
            'subway_distance': 1000,
            'school_distance': 700,
            'hospital_distance': 700,
            'commercial_distance': 600,
            'preferred_type': '일반 가구형',
            'optimal_units': 20,
            'parking_ratio': 0.8,
            'construction_cost_per_sqm': 3.0,
        }
    }
    
    @classmethod
    def extract_region_from_address(cls, address: str) -> str:
        """주소에서 지역 추출"""
        if not address:
            return 'default'
        
        # 광역시/도 추출
        regions = ['서울', '경기', '인천', '부산', '대구', '광주', '대전', '울산', '세종']
        for region in regions:
            if region in address:
                return region
        
        # 도 단위 (경기도 등)
        if '경기도' in address or '경기' in address:
            return '경기'
        
        return 'default'
    
    @classmethod
    def get_regional_default(cls, region: str, key: str) -> Any:
        """지역별 기본값 조회"""
        regional_data = cls.REGIONAL_DEFAULTS.get(region, cls.REGIONAL_DEFAULTS['default'])
        return regional_data.get(key, cls.REGIONAL_DEFAULTS['default'].get(key))
    
    @classmethod
    def infer_land_value(cls, address: str, site_area: float = None) -> Dict[str, Any]:
        """토지가치 추정"""
        region = cls.extract_region_from_address(address)
        base_price_per_pyeong = cls.get_regional_default(region, 'land_value_per_pyeong')
        
        # 평 단위 면적 (기본 300평)
        area_pyeong = (site_area / 3.3058) if site_area else 300
        
        land_value = base_price_per_pyeong * area_pyeong
        
        return {
            'land_value': land_value * 10000,  # 만원 → 원
            'land_value_per_pyeong': base_price_per_pyeong * 10000,
            'unit_price_sqm': base_price_per_pyeong * 10000 / 3.3058,
            'confidence_pct': 65,  # 추정값 신뢰도
            'low_price': land_value * 0.85 * 10000,
            'high_price': land_value * 1.15 * 10000,
            'stability_grade': 'B',
            'source': f'{region} 지역 평균값 기준 추정'
        }
    
    @classmethod
    def infer_poi_data(cls, address: str) -> Dict[str, Any]:
        """POI 데이터 추정"""
        region = cls.extract_region_from_address(address)
        
        return {
            'subway_distance': cls.get_regional_default(region, 'subway_distance'),
            'school_distance': cls.get_regional_default(region, 'school_distance'),
            'hospital_distance': cls.get_regional_default(region, 'hospital_distance'),
            'commercial_distance': cls.get_regional_default(region, 'commercial_distance'),
            'total_count': 25,
            'source': f'{region} 지역 평균 POI 거리 기준'
        }
    
    @classmethod
    def infer_preferred_type(cls, address: str, poi_data: Dict = None) -> Dict[str, Any]:
        """선호 유형 추정"""
        region = cls.extract_region_from_address(address)
        preferred_type = cls.get_regional_default(region, 'preferred_type')
        
        # POI 데이터 기반 재추정
        if poi_data:
            subway_dist = poi_data.get('subway_distance', 999999)
            school_dist = poi_data.get('school_distance', 999999)
            
            # 역세권 + 편의시설 우수 → 청년형
            if subway_dist < 500 and school_dist > 1000:
                preferred_type = "청년 1인 가구형"
            # 학교 가까움 → 신혼부부/자녀양육형
            elif school_dist < 500:
                preferred_type = "신혼부부·자녀양육형"
            # 기타 → 일반형
            elif subway_dist > 1000:
                preferred_type = "일반 가구형"
        
        return {
            'preferred_type': preferred_type,
            'confidence_score': 70,
            'stability_grade': 'B',
            'source': f'{region} 지역 특성 및 POI 패턴 기반 추정'
        }
    
    @classmethod
    def infer_building_capacity(cls, address: str, site_area: float = None, 
                                preferred_type: str = None) -> Dict[str, Any]:
        """건축 규모 추정"""
        region = cls.extract_region_from_address(address)
        optimal_units = cls.get_regional_default(region, 'optimal_units')
        parking_ratio = cls.get_regional_default(region, 'parking_ratio')
        
        # 부지 면적 기반 조정
        if site_area:
            # 1평당 약 0.06세대 (경험적 수치)
            area_pyeong = site_area / 3.3058
            estimated_units = int(area_pyeong * 0.06)
            optimal_units = max(15, min(30, estimated_units))  # 15-30세대 범위
        
        # 유형별 조정
        if preferred_type:
            if '청년' in preferred_type:
                optimal_units = min(optimal_units, 25)  # 청년형은 25세대 이하 선호
            elif '신혼' in preferred_type:
                optimal_units = min(optimal_units, 22)
        
        total_gfa = optimal_units * 30  # 세대당 30㎡ 가정
        
        return {
            'legal_capacity': {
                'total_units': optimal_units,
                'total_gfa_m2': total_gfa,
                'parking_spaces': int(optimal_units * parking_ratio),
            },
            'incentive_capacity': {
                'total_units': int(optimal_units * 1.1),  # 10% 증가
                'total_gfa_m2': total_gfa * 1.1,
                'parking_spaces': int(optimal_units * parking_ratio * 1.1),
            },
            'source': f'{region} 지역 표준 규모 및 주차 기준 적용'
        }
    
    @classmethod
    def infer_feasibility(cls, address: str, building_capacity: Dict = None,
                         land_value: float = None) -> Dict[str, Any]:
        """사업성 추정"""
        region = cls.extract_region_from_address(address)
        construction_cost_per_sqm = cls.get_regional_default(region, 'construction_cost_per_sqm')
        
        # 기본값
        units = 22
        total_gfa = 660  # 22세대 × 30㎡
        
        if building_capacity:
            units = building_capacity.get('legal_capacity', {}).get('total_units', 22)
            total_gfa = building_capacity.get('legal_capacity', {}).get('total_gfa_m2', 660)
        
        # 비용 계산
        land_cost = land_value if land_value else 100  # 억원
        construction_cost = total_gfa * construction_cost_per_sqm  # 억원
        design_cost = construction_cost * 0.04
        permit_cost = construction_cost * 0.01
        finance_cost = (land_cost + construction_cost) * 0.06 * (18/12)  # 18개월
        other_cost = construction_cost * 0.05
        
        total_cost = land_cost + construction_cost + design_cost + permit_cost + finance_cost + other_cost
        
        # LH 매입가 추정 (㎡당 450만원 가정)
        lh_price = total_gfa * 4.5
        
        profit = lh_price - total_cost
        profit_margin = (profit / total_cost * 100) if total_cost > 0 else 0
        
        return {
            'scenarios': [{
                'name': 'Scenario B (최적)',
                'units': units,
                'total_cost': total_cost,
                'lh_price': lh_price,
                'profit': profit,
                'profit_margin': profit_margin
            }],
            'costs': {
                'land': land_cost,
                'construction': construction_cost,
                'design': design_cost,
                'permit': permit_cost,
                'finance': finance_cost,
                'other': other_cost,
                'total': total_cost
            },
            'best_scenario': 'B',
            'source': f'{region} 지역 건축비 및 LH 매입 단가 기준 추정'
        }
    
    @classmethod
    def apply_smart_fallback(cls, data: Dict[str, Any], address: str = None,
                            module: str = 'M2') -> Dict[str, Any]:
        """스마트 폴백 적용"""
        
        if not address:
            address = data.get('address', '') or data.get('location', {}).get('address', '')
        
        region = cls.extract_region_from_address(address)
        logger.info(f"Smart Fallback: {module} for region '{region}'")
        
        # 모듈별 폴백 로직
        if module == 'M2':
            # 토지가치 데이터 검증 및 보완
            if not data.get('land_value') or data.get('land_value') == 0:
                site_area = data.get('site_area', 1000)
                inferred = cls.infer_land_value(address, site_area)
                data.update(inferred)
                logger.info(f"M2: Inferred land_value = {inferred['land_value']:,.0f}원")
        
        elif module == 'M3':
            # 선호 유형 데이터 검증 및 보완
            if not data.get('selected', {}).get('name') or data['selected']['name'] == 'N/A':
                poi_data = data.get('location', {}).get('poi', {})
                if not poi_data or not poi_data.get('subway_distance'):
                    poi_data = cls.infer_poi_data(address)
                    if 'location' not in data:
                        data['location'] = {}
                    data['location']['poi'] = poi_data
                
                inferred = cls.infer_preferred_type(address, poi_data)
                if 'selected' not in data:
                    data['selected'] = {}
                data['selected']['name'] = inferred['preferred_type']
                data['confidence_score'] = inferred['confidence_score']
                data['stability_grade'] = inferred['stability_grade']
                logger.info(f"M3: Inferred preferred_type = {inferred['preferred_type']}")
        
        elif module == 'M4':
            # 건축 규모 데이터 검증 및 보완
            if not data.get('legal_capacity') or not data['legal_capacity'].get('total_units'):
                site_area = data.get('site_area', 1000)
                preferred_type = data.get('preferred_type', '')
                inferred = cls.infer_building_capacity(address, site_area, preferred_type)
                data.update(inferred)
                logger.info(f"M4: Inferred units = {inferred['legal_capacity']['total_units']}")
        
        elif module == 'M5':
            # 사업성 데이터 검증 및 보완
            if not data.get('scenarios') or len(data.get('scenarios', [])) == 0:
                building_capacity = data.get('building_capacity', {})
                land_value = data.get('land_value', 0) / 100_000_000  # 원 → 억원
                inferred = cls.infer_feasibility(address, building_capacity, land_value)
                data.update(inferred)
                logger.info(f"M5: Inferred profit_margin = {inferred['scenarios'][0]['profit_margin']:.1f}%")
        
        # 모든 모듈: 추정 출처 표기
        if 'source' not in data and module in ['M2', 'M3', 'M4', 'M5']:
            data['_inferred'] = True
            data['_region'] = region
        
        return data
