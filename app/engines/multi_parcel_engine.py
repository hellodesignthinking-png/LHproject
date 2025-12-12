"""
Multi-Parcel Engine v24.0
다필지 결합 분석 엔진 for ZeroSite v24

Features:
- 필지 결합 분석
- 최적 조합 도출
- 결합 후 FAR/BCR 계산
- 비용-편익 분석

Author: ZeroSite v24 Team
Date: 2025-12-12
"""

from typing import Dict, List
import logging
from .base_engine import BaseEngine

logger = logging.getLogger(__name__)


class MultiParcelEngine(BaseEngine):
    """다필지 결합 분석 엔진"""
    
    def __init__(self):
        super().__init__(engine_name="MultiParcelEngine", version="24.0")
    
    @property
    def timestamp(self):
        return self.created_at.isoformat()
    
    def process(self, input_data: Dict) -> Dict:
        """Main processing"""
        self.validate_input(input_data, ['parcels'])
        
        parcels = input_data['parcels']
        
        # Analyze individual parcels
        individual_analysis = self._analyze_individual_parcels(parcels)
        
        # Analyze combined parcels
        combined_analysis = self._analyze_combined_parcels(parcels)
        
        # Calculate synergy effects
        synergy = self._calculate_synergy(individual_analysis, combined_analysis)
        
        # Cost-benefit analysis
        cost_benefit = self._analyze_cost_benefit(parcels, synergy)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(synergy, cost_benefit)
        
        result = {
            'success': True,
            'parcel_count': len(parcels),
            'individual_analysis': individual_analysis,
            'combined_analysis': combined_analysis,
            'synergy_effects': synergy,
            'cost_benefit': cost_benefit,
            'recommendation': recommendation
        }
        
        self.logger.info(f"Multi-parcel analysis complete: {len(parcels)} parcels, synergy {synergy['total_benefit_percent']}%")
        return result
    
    def _analyze_individual_parcels(self, parcels: List[Dict]) -> Dict:
        """Analyze parcels individually"""
        total_area = sum(p.get('area_sqm', 0) for p in parcels)
        total_far = sum(p.get('area_sqm', 0) * p.get('max_far', 200) / 100 for p in parcels)
        
        return {
            'total_land_area_sqm': round(total_area, 2),
            'total_buildable_area_sqm': round(total_far, 2),
            'average_far_percent': round((total_far / total_area * 100) if total_area > 0 else 0, 1),
            'parcel_details': [
                {
                    'id': i+1,
                    'area_sqm': p.get('area_sqm', 0),
                    'max_far': p.get('max_far', 200),
                    'buildable_sqm': round(p.get('area_sqm', 0) * p.get('max_far', 200) / 100, 2)
                }
                for i, p in enumerate(parcels)
            ]
        }
    
    def _analyze_combined_parcels(self, parcels: List[Dict]) -> Dict:
        """Analyze parcels when combined"""
        total_area = sum(p.get('area_sqm', 0) for p in parcels)
        
        # Combined FAR bonus (typically 10-20% for large sites)
        bonus_far = 15.0 if total_area > 1000 else 10.0
        
        avg_far = sum(p.get('max_far', 200) for p in parcels) / len(parcels)
        combined_far = avg_far + bonus_far
        
        combined_buildable = total_area * combined_far / 100
        
        return {
            'total_land_area_sqm': round(total_area, 2),
            'base_far_percent': round(avg_far, 1),
            'bonus_far_percent': bonus_far,
            'combined_far_percent': round(combined_far, 1),
            'total_buildable_area_sqm': round(combined_buildable, 2),
            'shape_improvement': self._calculate_shape_improvement(parcels)
        }
    
    def _calculate_shape_improvement(self, parcels: List[Dict]) -> str:
        """Calculate shape regularity improvement"""
        if len(parcels) >= 3:
            return "대폭 개선 (정형지 조성 가능)"
        elif len(parcels) == 2:
            return "개선 (접합면 최적화)"
        else:
            return "해당없음"
    
    def _calculate_synergy(self, individual: Dict, combined: Dict) -> Dict:
        """Calculate synergy effects"""
        individual_buildable = individual['total_buildable_area_sqm']
        combined_buildable = combined['total_buildable_area_sqm']
        
        synergy_area = combined_buildable - individual_buildable
        synergy_percent = (synergy_area / individual_buildable * 100) if individual_buildable > 0 else 0
        
        return {
            'additional_buildable_sqm': round(synergy_area, 2),
            'total_benefit_percent': round(synergy_percent, 1),
            'far_bonus_percent': combined['bonus_far_percent'],
            'shape_benefit': combined['shape_improvement']
        }
    
    def _analyze_cost_benefit(self, parcels: List[Dict], synergy: Dict) -> Dict:
        """Analyze cost-benefit"""
        total_area = sum(p.get('area_sqm', 0) for p in parcels)
        
        # Estimated acquisition cost per sqm
        avg_price = sum(p.get('price_per_sqm', 10000000) for p in parcels) / len(parcels)
        total_acquisition_cost = (total_area * avg_price) / 100_000_000  # 억원
        
        # Transaction costs (약 5%)
        transaction_cost = total_acquisition_cost * 0.05
        
        # Additional benefit from synergy
        additional_buildable = synergy['additional_buildable_sqm']
        estimated_value_per_sqm = 5_000_000  # 연면적당 가치
        additional_value = (additional_buildable * estimated_value_per_sqm) / 100_000_000
        
        net_benefit = additional_value - transaction_cost
        roi = (net_benefit / total_acquisition_cost * 100) if total_acquisition_cost > 0 else 0
        
        return {
            'total_acquisition_cost_billion': round(total_acquisition_cost, 2),
            'transaction_cost_billion': round(transaction_cost, 2),
            'additional_value_billion': round(additional_value, 2),
            'net_benefit_billion': round(net_benefit, 2),
            'roi_percent': round(roi, 1)
        }
    
    def _generate_recommendation(self, synergy: Dict, cost_benefit: Dict) -> str:
        """Generate recommendation"""
        if cost_benefit['roi_percent'] > 10:
            return f"✅ 적극 권장: 결합 시 ROI {cost_benefit['roi_percent']}%, 시너지 효과 {synergy['total_benefit_percent']}%"
        elif cost_benefit['roi_percent'] > 5:
            return f"⚠️ 조건부 권장: ROI {cost_benefit['roi_percent']}%, 거래비용 대비 편익 검토 필요"
        elif cost_benefit['roi_percent'] > 0:
            return f"🔴 신중 검토: ROI {cost_benefit['roi_percent']}%, 시너지 효과 제한적"
        else:
            return f"❌ 비권장: ROI {cost_benefit['roi_percent']}%, 결합 시 손실 예상"


if __name__ == "__main__":
    print("="*80)
    print("MULTI-PARCEL ENGINE v24.0 - CLI TEST")
    print("="*80)
    
    engine = MultiParcelEngine()
    
    test = {
        'parcels': [
            {'area_sqm': 400, 'max_far': 200, 'price_per_sqm': 10000000},
            {'area_sqm': 350, 'max_far': 200, 'price_per_sqm': 10500000},
            {'area_sqm': 450, 'max_far': 250, 'price_per_sqm': 11000000}
        ]
    }
    
    result = engine.process(test)
    
    print(f"\n✅ Engine: {engine.engine_name} v{engine.version}")
    print(f"\n📦 필지 수: {result['parcel_count']}개")
    print(f"\n개별 분석:")
    print(f"  - 총 면적: {result['individual_analysis']['total_land_area_sqm']}㎡")
    print(f"  - 평균 FAR: {result['individual_analysis']['average_far_percent']}%")
    print(f"  - 건축 가능: {result['individual_analysis']['total_buildable_area_sqm']}㎡")
    
    print(f"\n결합 분석:")
    print(f"  - 결합 FAR: {result['combined_analysis']['combined_far_percent']}%")
    print(f"  - 건축 가능: {result['combined_analysis']['total_buildable_area_sqm']}㎡")
    print(f"  - 형상 개선: {result['combined_analysis']['shape_improvement']}")
    
    print(f"\n시너지 효과:")
    print(f"  - 추가 건축 면적: {result['synergy_effects']['additional_buildable_sqm']}㎡")
    print(f"  - 시너지 비율: {result['synergy_effects']['total_benefit_percent']}%")
    
    print(f"\n비용-편익:")
    print(f"  - 총 취득비용: {result['cost_benefit']['total_acquisition_cost_billion']}억원")
    print(f"  - 거래비용: {result['cost_benefit']['transaction_cost_billion']}억원")
    print(f"  - 추가 가치: {result['cost_benefit']['additional_value_billion']}억원")
    print(f"  - 순편익: {result['cost_benefit']['net_benefit_billion']}억원")
    print(f"  - ROI: {result['cost_benefit']['roi_percent']}%")
    
    print(f"\n{result['recommendation']}")
    print("\n" + "="*80)
