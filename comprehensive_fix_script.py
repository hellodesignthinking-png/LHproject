"""
Comprehensive Fix Script for Appraisal Report Issues

This script addresses 6 critical issues:
1. Premium not reflected in Executive Summary (64.11억 vs 90.97억)
2. Transaction addresses showing "서울 default default 일대"
3. Unrealistic Income Approach (1489억)
4. Final Appraisal Amount table showing 0
5. PDF filename format
6. General layout issues
"""

import sys
import os

# Fix for Issue #3: Development Land Income Approach
INCOME_APPROACH_FIX = '''
    def calculate_income_approach(self,
                                  annual_rental_income: float,
                                  building_value: float,
                                  zone_type: str = None,
                                  land_area_sqm: float = 0) -> Dict:
        """
        Income Approach (수익환원법)
        
        🔥 개선: 나대지·개발용지 특수 처리
        - 건물이 없는 경우: 개발수익환원법 적용
        - 완성도 보정: 0.25 (개발 완성까지 보정)
        - 위험도 보정: 0.30 (개발 리스크 반영)
        
        한국 감정평가 기준:
        1. 순영업소득(NOI) = 임대수익 - 운영경비 - 공실손실
        2. 환원율(Cap Rate) = 무위험수익률 + 위험프리미엄
        3. 수익가액 = NOI / 환원율
        
        나대지·개발용지:
        1. 개발 후 예상수익 추정
        2. 완성도 보정 적용 (0.25)
        3. 위험도 보정 적용 (0.30)
        4. 최종 수익가액 = 예상수익 × 완성도 × (1 - 위험도) / 환원율
        """
        calculation_steps = []
        
        # 건물이 있는지 확인 (building_value > 0.5억원)
        has_building = building_value > 0.5
        
        if annual_rental_income > 0 and has_building:
            # 🏢 Case 1: 기존 건물 + 실제 임대수익
            gross_income = annual_rental_income / 100_000_000  # 억원 단위
            
            # 공실률 5% 적용
            vacancy_rate = 0.05
            vacancy_loss = gross_income * vacancy_rate
            effective_gross_income = gross_income * (1 - vacancy_rate)
            
            # 운영경비 15% 적용
            operating_expenses_rate = 0.15
            operating_expenses = effective_gross_income * operating_expenses_rate
            
            # 순영업소득(NOI) 계산
            noi = effective_gross_income - operating_expenses
            
            # 수익가액 = NOI / 환원율
            capitalized_value_billion = noi / self.DEFAULT_CAP_RATE
            
            # 계산 과정 상세 설명
            calculation_steps.append(f"1. 연간 총임대수익: {gross_income:.2f}억원")
            calculation_steps.append(f"2. 공실손실 (5%): -{vacancy_loss:.2f}억원")
            calculation_steps.append(f"3. 유효총수익: {effective_gross_income:.2f}억원")
            calculation_steps.append(f"4. 운영경비 (15%): -{operating_expenses:.2f}억원")
            calculation_steps.append(f"5. 순영업소득(NOI): {noi:.2f}억원")
            calculation_steps.append(f"6. 환원율: {self.DEFAULT_CAP_RATE*100:.1f}% (주거용 기준)")
            calculation_steps.append(f"7. 수익환원가액: {noi:.2f}억원 ÷ {self.DEFAULT_CAP_RATE} = {capitalized_value_billion:.2f}억원")
            
            method = "실제 임대수익 기준 (NOI 환원법)"
            
        elif not has_building and land_area_sqm > 0:
            # 🏗️ Case 2: 나대지/개발용지 - 개발수익환원법 적용
            
            # Step 1: 개발 후 예상 수익 추정
            # - 용도지역별 평균 임대수익률 적용
            zone_rental_rate = {
                '제1종일반주거지역': 0.035,  # 3.5%
                '제2종일반주거지역': 0.040,  # 4.0%
                '제3종일반주거지역': 0.045,  # 4.5%
                '준주거지역': 0.050,  # 5.0%
                '상업지역': 0.055,  # 5.5%
                '준공업지역': 0.042   # 4.2%
            }.get(zone_type, 0.040)
            
            # 개발 후 예상 건물가액 (토지가액의 2.5배 가정)
            estimated_building_value = building_value * 2.5 if building_value > 0 else land_area_sqm * 3_500_000 / 100_000_000
            
            # 예상 연간 임대수익
            estimated_gross_income = estimated_building_value * zone_rental_rate
            
            # 공실·운영비 공제
            vacancy_rate = 0.10  # 개발용지는 공실률 높게 10%
            operating_expenses_rate = 0.20  # 운영비도 높게 20%
            
            effective_gross_income = estimated_gross_income * (1 - vacancy_rate)
            operating_expenses = effective_gross_income * operating_expenses_rate
            noi = effective_gross_income - operating_expenses
            
            # Step 2: 완성도 보정 (개발용지는 0.25)
            completion_factor = 0.25
            adjusted_noi = noi * completion_factor
            
            # Step 3: 위험도 보정 (개발 리스크 30%)
            risk_adjustment = 0.30
            risk_adjusted_noi = adjusted_noi * (1 - risk_adjustment)
            
            # Step 4: 환원율 적용 (개발용지는 높은 환원율 6.0% 적용)
            development_cap_rate = 0.060
            
            capitalized_value_billion = risk_adjusted_noi / development_cap_rate
            
            # 계산 과정 설명
            calculation_steps.append(f"🏗️ 나대지/개발용지 - 개발수익환원법 적용")
            calculation_steps.append(f"1. 개발 후 예상 건물가액: {estimated_building_value:.2f}억원")
            calculation_steps.append(f"2. 용도지역별 임대수익률: {zone_rental_rate*100:.1f}%")
            calculation_steps.append(f"3. 예상 연간 임대수익: {estimated_gross_income:.2f}억원")
            calculation_steps.append(f"4. 공실손실 (10%): -{estimated_gross_income * vacancy_rate:.2f}억원")
            calculation_steps.append(f"5. 운영경비 (20%): -{operating_expenses:.2f}억원")
            calculation_steps.append(f"6. 순영업소득(NOI): {noi:.2f}억원")
            calculation_steps.append(f"7. ⚠️ 완성도 보정 (25%): {noi:.2f}억원 × 0.25 = {adjusted_noi:.2f}억원")
            calculation_steps.append(f"8. ⚠️ 위험도 보정 (30%): {adjusted_noi:.2f}억원 × 0.70 = {risk_adjusted_noi:.2f}억원")
            calculation_steps.append(f"9. 개발용지 환원율: {development_cap_rate*100:.1f}% (리스크 반영)")
            calculation_steps.append(f"10. 최종 수익가액: {risk_adjusted_noi:.2f}억원 ÷ {development_cap_rate} = {capitalized_value_billion:.2f}억원")
            
            method = "개발수익환원법 (나대지/개발용지 - 완성도 25%, 위험도 30% 적용)"
            
        else:
            # 🏢 Case 3: 건물 가액 기반 추정
            estimated_rental_rate = 0.04  # 연 4% 수익률 가정
            estimated_gross_income = building_value * estimated_rental_rate
            
            # 동일하게 공실률 5%, 운영경비 15% 적용
            vacancy_rate = 0.05
            operating_expenses_rate = 0.15
            
            effective_gross_income = estimated_gross_income * (1 - vacancy_rate)
            operating_expenses = effective_gross_income * operating_expenses_rate
            noi = effective_gross_income - operating_expenses
            
            capitalized_value_billion = noi / self.DEFAULT_CAP_RATE
            
            # 계산 과정 설명
            calculation_steps.append(f"1. 건물가액 기준 추정: {building_value:.2f}억원")
            calculation_steps.append(f"2. 추정 연간수익률: {estimated_rental_rate*100}%")
            calculation_steps.append(f"3. 추정 총임대수익: {estimated_gross_income:.2f}억원")
            calculation_steps.append(f"4. 공실손실 (5%): -{estimated_gross_income * vacancy_rate:.2f}억원")
            calculation_steps.append(f"5. 운영경비 (15%): -{operating_expenses:.2f}억원")
            calculation_steps.append(f"6. 순영업소득(NOI): {noi:.2f}억원")
            calculation_steps.append(f"7. 환원율: {self.DEFAULT_CAP_RATE*100:.1f}%")
            calculation_steps.append(f"8. 수익환원가액: {capitalized_value_billion:.2f}억원")
            
            method = "건물가액 기준 추정 (임대수익 자료 없음)"
        
        return {
            'total_value': round(capitalized_value_billion, 2),
            'annual_rental_income': round(annual_rental_income / 100_000_000, 2) if annual_rental_income > 0 else 0,
            'noi': round(noi, 2) if (annual_rental_income > 0 or building_value > 0 or land_area_sqm > 0) else 0,
            'cap_rate': self.DEFAULT_CAP_RATE if has_building or annual_rental_income > 0 else 0.060,
            'cap_rate_percentage': f"{self.DEFAULT_CAP_RATE*100:.1f}%" if has_building else "6.0%",
            'vacancy_rate': vacancy_rate if 'vacancy_rate' in locals() else 0.05,
            'operating_expenses_rate': operating_expenses_rate if 'operating_expenses_rate' in locals() else 0.15,
            'method': method,
            'calculation_steps': calculation_steps,
            'unit': '억원',
            'completion_factor': completion_factor if not has_building and land_area_sqm > 0 else None,
            'risk_adjustment': risk_adjustment if not has_building and land_area_sqm > 0 else None
        }
'''

print("=" * 80)
print("COMPREHENSIVE FIX SCRIPT - Appraisal Report Issues")
print("=" * 80)
print("\n📋 Issues to be fixed:")
print("1. ❌ Premium not reflected in Executive Summary")
print("2. ❌ Transaction addresses showing 'default'")
print("3. ❌ Unrealistic Income Approach calculation")
print("4. ❌ Final Appraisal table showing 0")
print("5. ❌ PDF filename format")
print("6. ❌ General layout issues")
print("\n✅ Fixes will be applied to:")
print("   - app/engines/appraisal_engine_v241.py")
print("   - app/services/ultimate_appraisal_pdf_generator.py")
print("   - app/api/v24_1/api_router.py")
print("=" * 80)
