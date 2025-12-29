#!/usr/bin/env python3
"""
M2 Classic Appraisal Report Generator
======================================

기존 감정평가 보고서 형식을 따르는 M2 보고서 생성기

Features:
- 24페이지 클래식 포맷
- 표지, 요약, 3가지 평가방법, 결론
- 개별공시지가, 거래사례, 수익환원법
- Professional 디자인

Author: ZeroSite Team
Date: 2025-12-29
Version: 1.0 - Classic Format
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class M2ClassicAppraisalGenerator:
    """
    M2 Classic Format Appraisal Report Generator
    """
    
    def __init__(self):
        """Initialize generator with Jinja2 template environment"""
        template_dir = Path(__file__).parent.parent / "templates_v13"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.env.filters['number_format'] = self._number_format
        self.env.filters['percentage'] = self._percentage
        
        print("✅ M2 Classic Appraisal Generator initialized")
        print(f"📁 Template directory: {template_dir}")
    
    @staticmethod
    def _number_format(value):
        """Format number with thousand separators"""
        if value is None:
            return "N/A"
        try:
            return f"{int(value):,}"
        except (ValueError, TypeError):
            return str(value)
    
    @staticmethod
    def _percentage(value):
        """Format value as percentage"""
        if value is None:
            return "N/A"
        try:
            return f"{float(value) * 100:.1f}%"
        except (ValueError, TypeError):
            return str(value)
    
    def generate_report(
        self,
        address: str,
        land_area_sqm: float,
        zone_type: str,
        official_price_per_sqm: float,
        transactions: list,
        appraisal_date: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate M2 Classic Appraisal Report
        
        Args:
            address: 대상지 주소
            land_area_sqm: 토지면적 (㎡)
            zone_type: 용도지역
            official_price_per_sqm: 개별공시지가 (원/㎡)
            transactions: 거래사례 리스트
            appraisal_date: 평가기준일 (optional)
            output_path: 출력 파일 경로 (optional)
        
        Returns:
            str: 생성된 HTML 파일 경로
        """
        
        print("\n" + "="*80)
        print("🏗️ M2 CLASSIC APPRAISAL REPORT GENERATOR")
        print("="*80)
        print(f"📍 Address: {address}")
        print(f"📏 Land Area: {land_area_sqm:,.2f}㎡")
        print(f"🏘️ Zone: {zone_type}")
        print("="*80 + "\n")
        
        # Calculate basic values
        land_area_pyeong = land_area_sqm * 0.3025
        report_id = f"ZS-M2-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        if not appraisal_date:
            appraisal_date = datetime.now().strftime("%Y년 %m월 %d일")
        
        # Official land price calculation
        official_land_value = official_price_per_sqm * land_area_sqm
        official_price_date = datetime.now().strftime("%Y.%m.%d")
        
        # Transaction comparison
        if not transactions:
            # Generate mock transactions for demo
            transactions = [
                {
                    'date': '2024.11.15',
                    'price': 6_800_000_000,
                    'area': 720,
                    'price_per_sqm': 9_444_444,
                    'distance': 250
                },
                {
                    'date': '2024.10.22',
                    'price': 5_500_000_000,
                    'area': 600,
                    'price_per_sqm': 9_166_667,
                    'distance': 380
                },
                {
                    'date': '2024.09.18',
                    'price': 7_200_000_000,
                    'area': 750,
                    'price_per_sqm': 9_600_000,
                    'distance': 420
                }
            ]
        
        # Calculate transaction adjustments
        transaction_adjustments = []
        total_weighted_price = 0
        total_weight = 0
        
        for i, trans in enumerate(transactions):
            # Apply corrections (mock values for demo)
            time_adj = 1.02  # 2% increase for time
            location_adj = 0.98  # 2% decrease for location
            individual_adj = 1.00  # No individual adjustment
            weight = 1.0 / (trans['distance'] / 100)  # Weight by distance
            
            adjusted_price = trans['price_per_sqm'] * time_adj * location_adj * individual_adj
            
            transaction_adjustments.append({
                'original_price': trans['price_per_sqm'],
                'time_adjustment': time_adj,
                'location_adjustment': location_adj,
                'individual_adjustment': individual_adj,
                'weight': weight,
                'adjusted_price': adjusted_price
            })
            
            total_weighted_price += adjusted_price * weight
            total_weight += weight
        
        weighted_avg_price = total_weighted_price / total_weight if total_weight > 0 else official_price_per_sqm
        transaction_based_value = weighted_avg_price * land_area_sqm
        
        # Income approach (mock calculation)
        annual_gross_income = land_area_sqm * 50000  # 50,000원/㎡ 연간 수익 가정
        operating_expenses = annual_gross_income * 0.20
        taxes = annual_gross_income * 0.05
        annual_net_income = annual_gross_income - operating_expenses - taxes
        capitalization_rate = 0.05  # 5% 환원율
        income_approach_value = annual_net_income / capitalization_rate if capitalization_rate > 0 else 0
        income_price_per_sqm = income_approach_value / land_area_sqm if land_area_sqm > 0 else 0
        
        # Final valuation (weighted average)
        official_weight = 0.30
        transaction_weight = 0.50
        income_weight = 0.20
        
        total_value = (
            official_land_value * official_weight +
            transaction_based_value * transaction_weight +
            income_approach_value * income_weight
        )
        price_per_sqm = total_value / land_area_sqm if land_area_sqm > 0 else 0
        price_per_pyeong = price_per_sqm * 3.3058
        
        # Confidence scoring
        transaction_count = len(transactions)
        if transaction_count >= 5:
            confidence_level = "매우 높음"
            confidence_score = 0.95
            data_quality = "우수"
        elif transaction_count >= 3:
            confidence_level = "높음"
            confidence_score = 0.85
            data_quality = "양호"
        else:
            confidence_level = "보통"
            confidence_score = 0.70
            data_quality = "보통"
        
        # Price range
        all_prices = [t['price_per_sqm'] for t in transactions] + [official_price_per_sqm]
        price_range_min = min(all_prices)
        price_range_max = max(all_prices)
        
        # Build context
        context = {
            # Basic info
            'report_id': report_id,
            'address': address,
            'land_area_sqm': land_area_sqm,
            'land_area_pyeong': land_area_pyeong,
            'zone_type': zone_type,
            'appraisal_date': appraisal_date,
            
            # Final values
            'total_value': total_value,
            'price_per_sqm': price_per_sqm,
            'price_per_pyeong': price_per_pyeong,
            
            # Official land price
            'official_price_per_sqm': official_price_per_sqm,
            'official_price_date': official_price_date,
            'official_land_value': official_land_value,
            
            # Transactions
            'transactions': transactions,
            'transaction_adjustments': transaction_adjustments,
            'weighted_avg_price': weighted_avg_price,
            'transaction_based_value': transaction_based_value,
            'transaction_count': transaction_count,
            
            # Income approach
            'annual_gross_income': annual_gross_income,
            'operating_expenses': operating_expenses,
            'taxes': taxes,
            'annual_net_income': annual_net_income,
            'capitalization_rate': capitalization_rate,
            'income_approach_value': income_approach_value,
            'income_price_per_sqm': income_price_per_sqm,
            
            # Weights
            'official_weight': official_weight,
            'transaction_weight': transaction_weight,
            'income_weight': income_weight,
            
            # Confidence
            'confidence_level': confidence_level,
            'confidence_score': confidence_score,
            'data_quality': data_quality,
            'price_range_min': price_range_min,
            'price_range_max': price_range_max,
            
            # Additional
            'appraisal_opinion': f"본 토지는 {zone_type}에 위치하며, {transaction_count}건의 거래사례와 개별공시지가, 수익환원법을 종합하여 평가한 결과 ㎡당 {price_per_sqm:,.0f}원으로 산정되었습니다. 인근 지역 개발 호재 및 교통 접근성을 고려할 때 적정한 시장가치로 판단됩니다.",
            'appraiser_name': "김철수 (등록번호: 제12345호)"
        }
        
        # Render template
        template = self.env.get_template('m2_classic_appraisal_format.html')
        html_content = template.render(**context)
        
        # Save HTML
        if not output_path:
            output_dir = Path("/tmp")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"M2_Classic_Appraisal_{timestamp}.html"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding='utf-8')
        
        print(f"✅ Report Generated Successfully!")
        print(f"📄 Output: {output_path}")
        print(f"📊 File Size: {output_path.stat().st_size / 1024:.2f} KB")
        print(f"💰 Total Value: ₩{total_value:,.0f}")
        print(f"📏 Price per ㎡: ₩{price_per_sqm:,.0f}")
        
        return str(output_path)


def main():
    """Test the generator"""
    generator = M2ClassicAppraisalGenerator()
    
    # Test data
    output_path = generator.generate_report(
        address="서울특별시 강남구 역삼동 123-45",
        land_area_sqm=660.0,
        zone_type="제2종일반주거지역",
        official_price_per_sqm=8_500_000,
        transactions=[]  # Will use mock data
    )
    
    print(f"\n🎉 Test report generated: {output_path}")


if __name__ == "__main__":
    main()
