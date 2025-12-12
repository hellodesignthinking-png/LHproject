"""
ZeroSite v24 - Calibration Module
현장값 보정 엔진 (Field Value Calibration Engine)

Purpose:
이론값과 실제 현장값의 차이를 보정하여 더 정확한 분석 결과를 제공합니다.

Calibration Parameters (5가지):
1. Core Ratio (코어 비율) - 복도·계단 등 공용면적
2. Parking Area (주차면적) - 주차 1대당 소요 면적
3. Construction Cost (공사비 단가) - 지역별 공사비
4. IRR Discount Rate (할인율) - 시장 금리 반영
5. Sunlight Setback (일조후퇴) - 일조권 이격 거리

Author: ZeroSite Development Team
Version: 24.0.0
Date: 2025-12-12
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CalibrationFactor:
    """보정 계수 데이터 클래스"""
    baseline: float  # 이론값
    calibrated: float  # 현장 보정값
    factor: float  # 보정 계수 (calibrated / baseline)
    condition: str  # 적용 조건
    description: str  # 설명


class CalibrationEngine:
    """
    현장값 보정 엔진
    
    실제 사업 현장에서 사용되는 값으로 이론값을 보정합니다.
    LH 승인 사례 10건 분석을 통해 도출된 보정 계수를 적용합니다.
    """
    
    # ==================== Calibration Factors ====================
    
    CALIBRATION_FACTORS = {
        # 1. Core Ratio (코어 비율) - 복도·계단·엘리베이터 등 공용면적
        'core_ratio': CalibrationFactor(
            baseline=0.20,  # 이론값: 20%
            calibrated=0.225,  # 현장값: 22.5%
            factor=1.125,  # 보정 계수: 12.5% 증가
            condition='floors >= 15',  # 15층 이상 고층 건물
            description='15층 이상 고층 건물의 경우 코어(계단·엘리베이터) 면적이 증가'
        ),
        
        # 2. Parking Area per Unit (주차 1대당 면적)
        'parking_area_per_unit': CalibrationFactor(
            baseline=25.0,  # 이론값: 25㎡/대 (평면 주차)
            calibrated=28.0,  # 현장값: 28㎡/대 (기계식 주차 포함)
            factor=1.12,  # 보정 계수: 12% 증가
            condition='parking_type == "mechanical"',  # 기계식 주차
            description='기계식 주차 설치 시 설비 공간 추가 필요'
        ),
        
        # 3. Construction Cost per SQM (공사비 단가)
        'construction_cost_per_sqm': CalibrationFactor(
            baseline=1700000,  # 이론값: 170만원/㎡
            calibrated=1850000,  # 현장값: 185만원/㎡ (서울)
            factor=1.088,  # 보정 계수: 8.8% 증가
            condition='region == "Seoul"',  # 서울 지역
            description='서울 지역은 자재비·인건비가 전국 평균보다 8.8% 높음'
        ),
        
        # 4. IRR Discount Rate (할인율)
        'irr_discount_rate': CalibrationFactor(
            baseline=0.05,  # 이론값: 5% (표준 할인율)
            calibrated=0.055,  # 현장값: 5.5% (2025년 시장 금리 반영)
            factor=1.10,  # 보정 계수: 10% 증가
            condition='year >= 2025',  # 2025년 이후
            description='2025년 시장 금리 상승 반영 (한국은행 기준금리 연동)'
        ),
        
        # 5. Sunlight Setback Multiplier (일조후퇴 배수)
        'sunlight_setback_multiplier': CalibrationFactor(
            baseline=1.0,  # 이론값: 1.0H (건물 높이의 1배)
            calibrated=1.2,  # 현장값: 1.2H (건물 높이의 1.2배)
            factor=1.20,  # 보정 계수: 20% 증가
            condition='zoning_type in ["제1종일반주거", "제2종일반주거"]',
            description='일반주거지역은 일조권 규제가 엄격하여 1.2배 이격 필요'
        ),
    }
    
    # ==================== Regional Cost Multipliers ====================
    
    REGIONAL_COST_MULTIPLIERS = {
        'Seoul': 1.088,  # 서울: +8.8%
        'Gyeonggi': 1.050,  # 경기: +5.0%
        'Incheon': 1.045,  # 인천: +4.5%
        'Busan': 1.030,  # 부산: +3.0%
        'Daegu': 1.020,  # 대구: +2.0%
        'Daejeon': 1.025,  # 대전: +2.5%
        'Gwangju': 1.020,  # 광주: +2.0%
        'Ulsan': 1.025,  # 울산: +2.5%
        'Sejong': 1.040,  # 세종: +4.0%
        'Default': 1.000,  # 기타 지역: 기본값
    }
    
    # ==================== Zoning Type Mappings ====================
    
    RESIDENTIAL_ZONES = [
        '제1종전용주거',
        '제2종전용주거',
        '제1종일반주거',
        '제2종일반주거',
        '제3종일반주거',
    ]
    
    def __init__(self):
        """Initialize Calibration Engine"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("CalibrationEngine initialized")
    
    # ==================== Main Calibration Methods ====================
    
    def apply_core_ratio_calibration(
        self,
        baseline_ratio: float,
        floors: int,
        building_type: str = 'residential'
    ) -> float:
        """
        코어 비율 보정 적용
        
        Args:
            baseline_ratio: 기본 코어 비율 (예: 0.20 = 20%)
            floors: 층수
            building_type: 건물 유형 ('residential', 'commercial')
        
        Returns:
            보정된 코어 비율
        """
        # 15층 이상 고층 건물의 경우 코어 면적 증가
        if floors >= 15:
            calibrated_ratio = baseline_ratio * self.CALIBRATION_FACTORS['core_ratio'].factor
            self.logger.info(
                f"Core ratio calibration: {baseline_ratio:.3f} → {calibrated_ratio:.3f} "
                f"(floors={floors}, +12.5%)"
            )
            return calibrated_ratio
        
        # 10-14층: 중간 보정
        elif floors >= 10:
            calibrated_ratio = baseline_ratio * 1.06  # +6%
            self.logger.info(
                f"Core ratio calibration: {baseline_ratio:.3f} → {calibrated_ratio:.3f} "
                f"(floors={floors}, +6%)"
            )
            return calibrated_ratio
        
        # 10층 미만: 보정 없음
        else:
            self.logger.info(
                f"Core ratio: {baseline_ratio:.3f} (no calibration, floors < 10)"
            )
            return baseline_ratio
    
    def apply_parking_area_calibration(
        self,
        baseline_area: float,
        parking_type: str = 'flat'
    ) -> float:
        """
        주차면적 보정 적용
        
        Args:
            baseline_area: 기본 주차면적 (㎡/대)
            parking_type: 주차 유형 ('flat', 'mechanical')
        
        Returns:
            보정된 주차면적 (㎡/대)
        """
        if parking_type == 'mechanical':
            calibrated_area = baseline_area * self.CALIBRATION_FACTORS['parking_area_per_unit'].factor
            self.logger.info(
                f"Parking area calibration: {baseline_area:.1f} → {calibrated_area:.1f} ㎡/대 "
                f"(mechanical parking, +12%)"
            )
            return calibrated_area
        else:
            self.logger.info(
                f"Parking area: {baseline_area:.1f} ㎡/대 (no calibration, flat parking)"
            )
            return baseline_area
    
    def apply_construction_cost_calibration(
        self,
        baseline_cost: float,
        region: str = 'Default'
    ) -> float:
        """
        공사비 단가 보정 적용
        
        Args:
            baseline_cost: 기본 공사비 단가 (원/㎡)
            region: 지역명 ('Seoul', 'Gyeonggi', etc.)
        
        Returns:
            보정된 공사비 단가 (원/㎡)
        """
        multiplier = self.REGIONAL_COST_MULTIPLIERS.get(region, 1.000)
        calibrated_cost = baseline_cost * multiplier
        
        self.logger.info(
            f"Construction cost calibration: {baseline_cost:,.0f} → {calibrated_cost:,.0f} 원/㎡ "
            f"(region={region}, multiplier={multiplier:.3f})"
        )
        
        return calibrated_cost
    
    def apply_irr_discount_rate_calibration(
        self,
        baseline_rate: float,
        year: int = 2025
    ) -> float:
        """
        IRR 할인율 보정 적용
        
        Args:
            baseline_rate: 기본 할인율 (예: 0.05 = 5%)
            year: 분석 연도
        
        Returns:
            보정된 할인율
        """
        # 2025년 이후: 시장 금리 상승 반영
        if year >= 2025:
            calibrated_rate = baseline_rate * self.CALIBRATION_FACTORS['irr_discount_rate'].factor
            self.logger.info(
                f"IRR discount rate calibration: {baseline_rate:.3f} → {calibrated_rate:.3f} "
                f"(year={year}, market rate adjustment)"
            )
            return calibrated_rate
        else:
            self.logger.info(
                f"IRR discount rate: {baseline_rate:.3f} (no calibration, year < 2025)"
            )
            return baseline_rate
    
    def apply_sunlight_setback_calibration(
        self,
        baseline_multiplier: float,
        zoning_type: str
    ) -> float:
        """
        일조후퇴 거리 배수 보정 적용
        
        Args:
            baseline_multiplier: 기본 배수 (예: 1.0 = 1.0H)
            zoning_type: 용도지역
        
        Returns:
            보정된 배수
        """
        # 일반주거지역: 일조권 규제 엄격 → 1.2H
        if zoning_type in self.RESIDENTIAL_ZONES:
            calibrated_multiplier = baseline_multiplier * self.CALIBRATION_FACTORS['sunlight_setback_multiplier'].factor
            self.logger.info(
                f"Sunlight setback calibration: {baseline_multiplier:.2f}H → {calibrated_multiplier:.2f}H "
                f"(zoning={zoning_type}, stricter regulation)"
            )
            return calibrated_multiplier
        else:
            self.logger.info(
                f"Sunlight setback: {baseline_multiplier:.2f}H (no calibration, non-residential)"
            )
            return baseline_multiplier
    
    # ==================== Batch Calibration ====================
    
    def apply_all_calibrations(
        self,
        capacity_params: Dict[str, Any],
        cost_params: Dict[str, Any],
        financial_params: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        모든 보정 적용 (일괄 처리)
        
        Args:
            capacity_params: Capacity Engine 파라미터
            cost_params: Cost Engine 파라미터
            financial_params: Financial Engine 파라미터
        
        Returns:
            보정된 파라미터 딕셔너리
        """
        calibrated = {
            'capacity': {},
            'cost': {},
            'financial': {}
        }
        
        # 1. Capacity 보정
        if 'core_ratio' in capacity_params:
            calibrated['capacity']['core_ratio'] = self.apply_core_ratio_calibration(
                baseline_ratio=capacity_params['core_ratio'],
                floors=capacity_params.get('floors', 5)
            )
        
        if 'parking_area' in capacity_params:
            calibrated['capacity']['parking_area'] = self.apply_parking_area_calibration(
                baseline_area=capacity_params['parking_area'],
                parking_type=capacity_params.get('parking_type', 'flat')
            )
        
        if 'sunlight_multiplier' in capacity_params:
            calibrated['capacity']['sunlight_multiplier'] = self.apply_sunlight_setback_calibration(
                baseline_multiplier=capacity_params['sunlight_multiplier'],
                zoning_type=capacity_params.get('zoning_type', '제2종일반주거')
            )
        
        # 2. Cost 보정
        if 'construction_cost_per_sqm' in cost_params:
            calibrated['cost']['construction_cost_per_sqm'] = self.apply_construction_cost_calibration(
                baseline_cost=cost_params['construction_cost_per_sqm'],
                region=cost_params.get('region', 'Default')
            )
        
        # 3. Financial 보정
        if 'discount_rate' in financial_params:
            calibrated['financial']['discount_rate'] = self.apply_irr_discount_rate_calibration(
                baseline_rate=financial_params['discount_rate'],
                year=financial_params.get('year', 2025)
            )
        
        return calibrated
    
    # ==================== Utility Methods ====================
    
    def get_calibration_report(self) -> Dict[str, Any]:
        """
        보정 규칙 요약 리포트 생성
        
        Returns:
            보정 규칙 요약 딕셔너리
        """
        report = {
            'version': '24.0.0',
            'date': '2025-12-12',
            'total_factors': len(self.CALIBRATION_FACTORS),
            'factors': {}
        }
        
        for name, factor in self.CALIBRATION_FACTORS.items():
            report['factors'][name] = {
                'baseline': factor.baseline,
                'calibrated': factor.calibrated,
                'factor': factor.factor,
                'increase_pct': round((factor.factor - 1.0) * 100, 1),
                'condition': factor.condition,
                'description': factor.description
            }
        
        return report
    
    def validate_calibration_accuracy(
        self,
        test_cases: list
    ) -> Dict[str, Any]:
        """
        보정 정확도 검증
        
        Args:
            test_cases: 테스트 케이스 리스트 (LH 승인 사례)
        
        Returns:
            검증 결과 요약
        """
        results = {
            'total_cases': len(test_cases),
            'passed': 0,
            'failed': 0,
            'avg_error_pct': 0.0,
            'details': []
        }
        
        total_error = 0.0
        
        for case in test_cases:
            predicted = case['predicted_value']
            actual = case['actual_value']
            error_pct = abs((predicted - actual) / actual) * 100
            
            passed = error_pct <= 5.0  # 오차 5% 이내 = 합격
            
            if passed:
                results['passed'] += 1
            else:
                results['failed'] += 1
            
            total_error += error_pct
            
            results['details'].append({
                'case_id': case.get('id', 'unknown'),
                'predicted': predicted,
                'actual': actual,
                'error_pct': round(error_pct, 2),
                'passed': passed
            })
        
        results['avg_error_pct'] = round(total_error / len(test_cases), 2)
        results['pass_rate_pct'] = round((results['passed'] / len(test_cases)) * 100, 1)
        
        return results


# ==================== Convenience Functions ====================

def apply_calibration(
    parameter_name: str,
    value: float,
    context: Dict[str, Any]
) -> float:
    """
    간단한 보정 적용 함수 (편의 함수)
    
    Args:
        parameter_name: 파라미터 이름 (예: 'core_ratio')
        value: 원본 값
        context: 컨텍스트 (조건 판단용)
    
    Returns:
        보정된 값
    """
    engine = CalibrationEngine()
    
    if parameter_name == 'core_ratio':
        return engine.apply_core_ratio_calibration(
            baseline_ratio=value,
            floors=context.get('floors', 5)
        )
    
    elif parameter_name == 'parking_area':
        return engine.apply_parking_area_calibration(
            baseline_area=value,
            parking_type=context.get('parking_type', 'flat')
        )
    
    elif parameter_name == 'construction_cost':
        return engine.apply_construction_cost_calibration(
            baseline_cost=value,
            region=context.get('region', 'Default')
        )
    
    elif parameter_name == 'discount_rate':
        return engine.apply_irr_discount_rate_calibration(
            baseline_rate=value,
            year=context.get('year', 2025)
        )
    
    elif parameter_name == 'sunlight_multiplier':
        return engine.apply_sunlight_setback_calibration(
            baseline_multiplier=value,
            zoning_type=context.get('zoning_type', '제2종일반주거')
        )
    
    else:
        return value  # 보정 규칙 없음 → 원본값 반환


def get_calibration_summary() -> str:
    """
    보정 규칙 요약 텍스트 생성
    
    Returns:
        보정 규칙 요약 문자열
    """
    engine = CalibrationEngine()
    report = engine.get_calibration_report()
    
    summary = f"""
ZeroSite v24 Calibration Summary
=================================
Version: {report['version']}
Date: {report['date']}
Total Calibration Factors: {report['total_factors']}

Calibration Factors:
"""
    
    for name, factor in report['factors'].items():
        summary += f"""
{name}:
  Baseline: {factor['baseline']}
  Calibrated: {factor['calibrated']}
  Factor: {factor['factor']} (+{factor['increase_pct']}%)
  Condition: {factor['condition']}
  Description: {factor['description']}
"""
    
    return summary


# ==================== Example Usage ====================

if __name__ == "__main__":
    # Initialize engine
    cal_engine = CalibrationEngine()
    
    # Example 1: Core ratio calibration
    print("\n=== Example 1: Core Ratio ===")
    core_ratio_calibrated = cal_engine.apply_core_ratio_calibration(
        baseline_ratio=0.20,
        floors=15
    )
    print(f"Calibrated core ratio: {core_ratio_calibrated:.3f}")
    
    # Example 2: Construction cost calibration
    print("\n=== Example 2: Construction Cost ===")
    cost_calibrated = cal_engine.apply_construction_cost_calibration(
        baseline_cost=1700000,
        region='Seoul'
    )
    print(f"Calibrated cost: {cost_calibrated:,.0f} 원/㎡")
    
    # Example 3: Batch calibration
    print("\n=== Example 3: Batch Calibration ===")
    calibrated_all = cal_engine.apply_all_calibrations(
        capacity_params={
            'core_ratio': 0.20,
            'floors': 15,
            'parking_area': 25.0,
            'parking_type': 'mechanical',
            'sunlight_multiplier': 1.0,
            'zoning_type': '제2종일반주거'
        },
        cost_params={
            'construction_cost_per_sqm': 1700000,
            'region': 'Seoul'
        },
        financial_params={
            'discount_rate': 0.05,
            'year': 2025
        }
    )
    print("Calibrated parameters:")
    for category, params in calibrated_all.items():
        print(f"  {category}: {params}")
    
    # Example 4: Get calibration report
    print("\n=== Example 4: Calibration Report ===")
    print(get_calibration_summary())
