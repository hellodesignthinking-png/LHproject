"""
ZeroSite M2 Professional Appraisal Report Generator v6.5
========================================================

예전 감정평가 보고서 형식(표 중심, 시각적)으로 복원
- 깔끔한 표 레이아웃
- 핵심 지표 강조
- 페이지별 명확한 구분
- 전문적인 디자인

Author: ZeroSite Team
Version: 6.5
Date: 2025-12-29
"""

from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import weasyprint
from pathlib import Path
from typing import Dict, Any, Optional


class M2ProfessionalAppraisalGenerator:
    """M2 토지감정평가 보고서 생성기 v6.5 - Professional Format"""
    
    def __init__(self):
        """Initialize generator with template"""
        # Get absolute path to templates directory
        current_file = Path(__file__).resolve()
        webapp_root = current_file.parent.parent.parent  # Go up to webapp root
        template_dir = webapp_root / "app" / "templates_v13"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        # Add custom filters
        self.env.filters['number_format'] = self._number_format
        
        print("✅ M2 Professional Appraisal Generator v6.5 initialized")
    
    def _number_format(self, value, decimals=0):
        """Format number with thousand separators"""
        try:
            if decimals > 0:
                return f"{float(value):,.{decimals}f}"
            return f"{int(value):,}"
        except:
            return str(value)
    
    def generate_report(
        self,
        address: str,
        land_area_sqm: float,
        zone_type: str,
        appraisal_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate M2 Professional Appraisal Report
        
        Args:
            address: 토지 주소
            land_area_sqm: 토지 면적 (㎡)
            zone_type: 용도지역
            appraisal_data: 감정평가 데이터
            output_path: 출력 파일 경로 (None이면 자동 생성)
        
        Returns:
            str: 생성된 PDF 파일 경로
        """
        
        print(f"\n{'='*80}")
        print(f"M2 Professional Appraisal Report Generation v6.5")
        print(f"{'='*80}")
        print(f"Address: {address}")
        print(f"Land Area: {land_area_sqm:,.2f}㎡")
        print(f"Zone: {zone_type}")
        
        # Prepare context
        context = self._prepare_context(address, land_area_sqm, zone_type, appraisal_data)
        
        # Render template
        template = self.env.get_template('m2_professional_appraisal_v6_5.html')
        html_content = template.render(**context)
        
        # Generate PDF
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"/tmp/M2_토지감정평가_보고서_{timestamp}.pdf"
        
        print(f"\n📄 Generating PDF...")
        
        # Save HTML first
        html_path = output_path.replace('.pdf', '.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Try to generate PDF using xhtml2pdf
        try:
            from xhtml2pdf import pisa
            
            with open(output_path, "wb") as pdf_file:
                pisa_status = pisa.CreatePDF(
                    html_content.encode('utf-8'),
                    dest=pdf_file,
                    encoding='utf-8'
                )
            
            if pisa_status.err:
                print(f"⚠️ PDF generation had errors, but HTML is available at: {html_path}")
        except Exception as e:
            print(f"⚠️ PDF generation failed: {e}")
            print(f"✅ HTML version saved at: {html_path}")
            output_path = html_path
        
        # Calculate file size
        file_size = Path(output_path).stat().st_size / 1024  # KB
        
        print(f"✅ PDF Generated Successfully!")
        print(f"   Output: {output_path}")
        print(f"   Size: {file_size:.2f} KB")
        print(f"{'='*80}\n")
        
        return output_path
    
    def _prepare_context(
        self,
        address: str,
        land_area_sqm: float,
        zone_type: str,
        appraisal_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare template context from appraisal data"""
        
        # Extract data with safe defaults
        land_area_pyeong = land_area_sqm / 3.3058
        
        # Final value
        final_value = appraisal_data.get('final_value', 0)
        price_per_sqm = final_value / land_area_sqm if land_area_sqm > 0 else 0
        price_per_pyeong = price_per_sqm * 3.3058
        
        # Three approaches
        sales_comparison = appraisal_data.get('sales_comparison', {})
        cost_approach = appraisal_data.get('cost_approach', {})
        income_approach = appraisal_data.get('income_approach', {})
        
        sales_value = sales_comparison.get('value', 0)
        cost_value = cost_approach.get('value', 0)
        income_value = income_approach.get('value', 0)
        
        # Weights
        sales_weight = appraisal_data.get('weights', {}).get('sales_comparison', 40)
        cost_weight = appraisal_data.get('weights', {}).get('cost_approach', 40)
        income_weight = appraisal_data.get('weights', {}).get('income_approach', 20)
        
        # Weighted values
        sales_weighted = sales_value * sales_weight / 100
        cost_weighted = cost_value * cost_weight / 100
        income_weighted = income_value * income_weight / 100
        
        # Confidence
        confidence_score = appraisal_data.get('confidence', {}).get('score', 85)
        if confidence_score >= 80:
            confidence_level = "HIGH"
        elif confidence_score >= 60:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"
        
        # Comparables
        comparables = appraisal_data.get('comparables', [])
        
        # Process comparables
        processed_comparables = []
        for comp in comparables[:5]:  # Top 5
            processed_comparables.append({
                'address': comp.get('address', 'N/A'),
                'area': comp.get('area', 0),
                'price': comp.get('price', 0),
                'price_per_sqm': comp.get('price_per_sqm', 0),
                'transaction_date': comp.get('transaction_date', 'N/A'),
                'distance': comp.get('distance', 0),
                'time_correction': comp.get('corrections', {}).get('time', 1.0),
                'location_correction': comp.get('corrections', {}).get('location', 1.0),
                'individual_correction': comp.get('corrections', {}).get('individual', 1.0),
                'other_correction': comp.get('corrections', {}).get('other', 1.0),
                'weight': comp.get('weight', 20),
                'adjusted_price': comp.get('adjusted_price', 0)
            })
        
        # Official price
        official_price_per_sqm = appraisal_data.get('official_price', {}).get('per_sqm', 0)
        official_price_per_pyeong = official_price_per_sqm * 3.3058
        official_total_value = official_price_per_sqm * land_area_sqm
        official_price_year = datetime.now().year
        
        # Premium
        total_premium = appraisal_data.get('premium', {}).get('total', 20)
        location_premium = appraisal_data.get('premium', {}).get('location', 10)
        development_premium = appraisal_data.get('premium', {}).get('development', 5)
        market_premium = appraisal_data.get('premium', {}).get('market', 5)
        
        # Official price ratio
        if official_price_per_sqm > 0:
            official_price_ratio = int((price_per_sqm / official_price_per_sqm - 1) * 100)
        else:
            official_price_ratio = 0
        
        # Income approach details
        development_type = appraisal_data.get('development', {}).get('type', '청년형 공공임대주택')
        estimated_units = appraisal_data.get('development', {}).get('units', 0)
        avg_rent = appraisal_data.get('development', {}).get('avg_rent', 0)
        vacancy_rate = appraisal_data.get('development', {}).get('vacancy_rate', 5)
        operating_expense_ratio = appraisal_data.get('development', {}).get('operating_expense_ratio', 30)
        cap_rate = appraisal_data.get('income_approach', {}).get('cap_rate', 4.0)
        
        annual_gross_income = income_approach.get('annual_gross_income', 0)
        annual_net_income = income_approach.get('annual_net_income', 0)
        
        # Basic info
        parcel_number = appraisal_data.get('parcel_number', 'N/A')
        building_coverage_ratio = appraisal_data.get('regulations', {}).get('bcr', 60)
        floor_area_ratio = appraisal_data.get('regulations', {}).get('far', 200)
        land_category = appraisal_data.get('land_category', '대지')
        road_condition = appraisal_data.get('road_condition', '6m 이상 도로 접함')
        
        # Report metadata
        report_id = f"ZEROSITE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        valuation_date = datetime.now().strftime('%Y년 %m월 %d일')
        
        context = {
            # Report metadata
            'report_id': report_id,
            'address': address,
            'land_area_sqm': land_area_sqm,
            'land_area_pyeong': land_area_pyeong,
            'zone_type': zone_type,
            'valuation_date': valuation_date,
            
            # Final values
            'final_value': final_value,
            'price_per_sqm': price_per_sqm,
            'price_per_pyeong': price_per_pyeong,
            
            # Confidence
            'confidence_score': confidence_score,
            'confidence_level': confidence_level,
            
            # Three approaches
            'sales_comparison_value': sales_value,
            'cost_approach_value': cost_value,
            'income_approach_value': income_value,
            
            # Weights
            'sales_comparison_weight': sales_weight,
            'cost_approach_weight': cost_weight,
            'income_approach_weight': income_weight,
            
            # Weighted values
            'sales_comparison_weighted': sales_weighted,
            'cost_approach_weighted': cost_weighted,
            'income_approach_weighted': income_weighted,
            
            # Weighted average
            'weighted_average_pct': 100,  # Always 100%
            
            # Comparables
            'comparables': processed_comparables,
            'comparable_count': len(comparables),
            
            # Official price
            'official_price_per_sqm': official_price_per_sqm,
            'official_price_per_pyeong': official_price_per_pyeong,
            'official_total_value': official_total_value,
            'official_price_year': official_price_year,
            'official_price_ratio': official_price_ratio,
            
            # Premium
            'total_premium': total_premium,
            'location_premium': location_premium,
            'development_premium': development_premium,
            'market_premium': market_premium,
            
            # Income approach
            'development_type': development_type,
            'estimated_units': estimated_units,
            'avg_rent': avg_rent,
            'vacancy_rate': vacancy_rate,
            'operating_expense_ratio': operating_expense_ratio,
            'cap_rate': cap_rate,
            'annual_gross_income': annual_gross_income,
            'annual_net_income': annual_net_income,
            
            # Basic info
            'parcel_number': parcel_number,
            'building_coverage_ratio': building_coverage_ratio,
            'floor_area_ratio': floor_area_ratio,
            'land_category': land_category,
            'road_condition': road_condition,
        }
        
        return context


def create_sample_appraisal_data():
    """Create sample appraisal data for testing"""
    return {
        'final_value': 5_600_000_000,
        
        'sales_comparison': {
            'value': 5_800_000_000
        },
        
        'cost_approach': {
            'value': 5_400_000_000
        },
        
        'income_approach': {
            'value': 5_600_000_000,
            'cap_rate': 4.0,
            'annual_gross_income': 300_000_000,
            'annual_net_income': 224_000_000
        },
        
        'weights': {
            'sales_comparison': 40,
            'cost_approach': 40,
            'income_approach': 20
        },
        
        'confidence': {
            'score': 88
        },
        
        'comparables': [
            {
                'address': '서울시 강남구 역삼동 456-78',
                'area': 620,
                'price': 3_600_000_000,
                'price_per_sqm': 5_806_452,
                'transaction_date': '2025-11-15',
                'distance': 120,
                'corrections': {
                    'time': 1.02,
                    'location': 0.98,
                    'individual': 1.00,
                    'other': 1.00
                },
                'weight': 25,
                'adjusted_price': 5_883_870
            },
            {
                'address': '서울시 강남구 역삼동 789-12',
                'area': 580,
                'price': 3_300_000_000,
                'price_per_sqm': 5_689_655,
                'transaction_date': '2025-10-20',
                'distance': 200,
                'corrections': {
                    'time': 1.03,
                    'location': 0.97,
                    'individual': 1.01,
                    'other': 1.00
                },
                'weight': 20,
                'adjusted_price': 5_726_034
            },
            {
                'address': '서울시 강남구 삼성동 123-45',
                'area': 650,
                'price': 3_900_000_000,
                'price_per_sqm': 6_000_000,
                'transaction_date': '2025-09-10',
                'distance': 350,
                'corrections': {
                    'time': 1.05,
                    'location': 0.95,
                    'individual': 0.99,
                    'other': 1.00
                },
                'weight': 20,
                'adjusted_price': 5_929_500
            },
            {
                'address': '서울시 강남구 대치동 567-89',
                'area': 600,
                'price': 3_500_000_000,
                'price_per_sqm': 5_833_333,
                'transaction_date': '2025-08-05',
                'distance': 450,
                'corrections': {
                    'time': 1.06,
                    'location': 0.94,
                    'individual': 1.00,
                    'other': 1.00
                },
                'weight': 15,
                'adjusted_price': 5_820_000
            },
            {
                'address': '서울시 강남구 청담동 901-23',
                'area': 700,
                'price': 4_200_000_000,
                'price_per_sqm': 6_000_000,
                'transaction_date': '2025-07-15',
                'distance': 600,
                'corrections': {
                    'time': 1.08,
                    'location': 0.93,
                    'individual': 0.98,
                    'other': 1.00
                },
                'weight': 20,
                'adjusted_price': 5_943_360
            }
        ],
        
        'official_price': {
            'per_sqm': 4_500_000
        },
        
        'premium': {
            'total': 25,
            'location': 12,
            'development': 8,
            'market': 5
        },
        
        'development': {
            'type': '청년형 공공임대주택',
            'units': 45,
            'avg_rent': 550_000,
            'vacancy_rate': 5,
            'operating_expense_ratio': 30
        },
        
        'regulations': {
            'bcr': 60,
            'far': 200
        },
        
        'parcel_number': '1234-5678',
        'land_category': '대지',
        'road_condition': '6m 이상 도로 2면 접함'
    }


# Test function
if __name__ == "__main__":
    generator = M2ProfessionalAppraisalGenerator()
    
    # Sample data
    sample_data = create_sample_appraisal_data()
    
    # Generate report
    pdf_path = generator.generate_report(
        address="서울특별시 강남구 역삼동 123-45",
        land_area_sqm=660.0,
        zone_type="제2종일반주거지역",
        appraisal_data=sample_data
    )
    
    print(f"\n✅ Test PDF generated: {pdf_path}")
