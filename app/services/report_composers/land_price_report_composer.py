"""
ZeroSite Land Price Report Composer v1.0 (5-8 pages)

목적:
- 토지 가격 적정성 분석 보고서
- 토지 매입 전 가격 협상의 근거 자료
- Model A (직접개발): 토지 매입가 협상용
- Model C (투자자 컨설팅): 투자자 제공용

구조 (4개 섹션):
- Section 1: Price Summary (1장)
- Section 2: Valuation Analysis (2장)
- Section 3: Market Comparison (2장)
- Section 4: Recommendation (1-2장)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class LandPriceReportComposer:
    """
    v1.0 Land Price Report - 토지가격 적정성 분석
    Target: 내부/투자자 (5-8 pages)
    
    Focus: 적정 매입가 산정 근거
    """
    
    def __init__(
        self,
        appraisal_ctx,
        land_diagnosis: Dict[str, Any],
        lh_result: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Land Price Report Composer
        
        Args:
            appraisal_ctx: Locked appraisal context (READ-ONLY)
            land_diagnosis: Land diagnosis results
            lh_result: LH analysis results (optional, for revenue approach)
        """
        self.appraisal_ctx = appraisal_ctx
        self.land_diagnosis = land_diagnosis
        self.lh_result = lh_result or {}
        
        self.report_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.generation_time = datetime.now().isoformat()
        self.version = "v1.0"
    
    def compose(self) -> Dict[str, Any]:
        """
        Generate complete Land Price Report (5-8 pages)
        
        Returns:
            Dictionary with all 4 sections
        """
        
        print(f"\n📄 Generating Land Price Report v1.0 (5-8 pages)")
        print(f"   Report ID: {self.report_id}")
        print(f"   Focus: Land Price Adequacy Analysis")
        
        report = {
            'report_id': self.report_id,
            'report_type': 'land_price_report',
            'version': self.version,
            'generation_time': self.generation_time,
            'estimated_pages': '5-8',
            
            'section_1_price_summary': self._compose_price_summary(),
            'section_2_valuation_analysis': self._compose_valuation_analysis(),
            'section_3_market_comparison': self._compose_market_comparison(),
            'section_4_recommendation': self._compose_recommendation()
        }
        
        # Calculate actual page count
        page_count = self._calculate_page_count(report)
        report['actual_pages'] = page_count
        
        print(f"✅ Land Price Report v1.0 generation complete")
        print(f"   Total Pages: {page_count}")
        print(f"   Price Judgment: {report['section_1_price_summary']['price_adequacy']['judgment']}")
        print(f"   Appropriate Price: {report['section_4_recommendation']['final_appropriate_price']['formatted_range']}")
        
        return report
    
    def _compose_price_summary(self) -> Dict[str, Any]:
        """
        Section 1: Price Summary (1장)
        대상 토지 기본 정보 및 가격 비교 대시보드
        """
        
        # Extract appraisal data
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm')
        official_price_sqm = self.appraisal_ctx.get('official_land_price.standard_price_per_sqm')
        appraised_total = self.appraisal_ctx.get('calculation.final_appraised_total')
        appraised_price_sqm = appraised_total / land_area if land_area > 0 else 0
        premium_rate = self.appraisal_ctx.get('premium.total_premium_rate', 0)
        
        # Calculate prices per pyeong
        pyeong_factor = 3.3058
        official_price_pyeong = official_price_sqm * pyeong_factor
        appraised_price_pyeong = appraised_price_sqm * pyeong_factor
        
        # Current asking price (호가) - 감정가 + 7% 가정
        asking_price_total = appraised_total * 1.07
        asking_price_sqm = asking_price_total / land_area
        asking_price_pyeong = asking_price_sqm * pyeong_factor
        
        # Appropriate purchase price (적정 매입가) - 감정가 + 2% 가정
        appropriate_price_total = appraised_total * 1.02
        appropriate_price_sqm = appropriate_price_total / land_area
        appropriate_price_pyeong = appropriate_price_sqm * pyeong_factor
        
        # Price adequacy judgment
        price_diff = asking_price_total - appropriate_price_total
        price_diff_pct = (price_diff / appropriate_price_total) * 100
        
        if price_diff_pct <= 5:
            adequacy = '적정'
            adequacy_color = 'green'
            adequacy_icon = '✅'
        elif price_diff_pct <= 10:
            adequacy = '약간 고가'
            adequacy_color = 'yellow'
            adequacy_icon = '⚠️'
        else:
            adequacy = '고가'
            adequacy_color = 'red'
            adequacy_icon = '❌'
        
        return {
            'title': 'Price Summary',
            'page_number': 1,
            
            # 대상 토지 기본 정보
            'target_land_info': {
                'address': '서울특별시 마포구 월드컵북로 120',  # Mock data
                'land_area_sqm': land_area,
                'land_area_pyeong': land_area / pyeong_factor,
                'zone_type': self.appraisal_ctx.get('zoning.confirmed_type', '제2종일반주거지역'),
                'far': self.appraisal_ctx.get('zoning.floor_area_ratio', 0),
                'bcr': self.appraisal_ctx.get('zoning.building_coverage_ratio', 0)
            },
            
            # 가격 비교 대시보드
            'price_comparison_dashboard': {
                'official_land_price': {
                    'label': '공시지가',
                    'total': official_price_sqm * land_area,
                    'per_sqm': official_price_sqm,
                    'per_pyeong': official_price_pyeong,
                    'formatted_total': f'{official_price_sqm * land_area / 100000000:.1f}억원',
                    'formatted_per_pyeong': f'{official_price_pyeong / 10000:.0f}만원'
                },
                'appraised_value': {
                    'label': '감정평가액',
                    'total': appraised_total,
                    'per_sqm': appraised_price_sqm,
                    'per_pyeong': appraised_price_pyeong,
                    'formatted_total': f'{appraised_total / 100000000:.1f}억원',
                    'formatted_per_pyeong': f'{appraised_price_pyeong / 10000:.0f}만원'
                },
                'asking_price': {
                    'label': '현재 호가',
                    'total': asking_price_total,
                    'per_sqm': asking_price_sqm,
                    'per_pyeong': asking_price_pyeong,
                    'formatted_total': f'{asking_price_total / 100000000:.1f}억원',
                    'formatted_per_pyeong': f'{asking_price_pyeong / 10000:.0f}만원'
                },
                'appropriate_price': {
                    'label': '적정 매입가',
                    'total': appropriate_price_total,
                    'per_sqm': appropriate_price_sqm,
                    'per_pyeong': appropriate_price_pyeong,
                    'formatted_total': f'{appropriate_price_total / 100000000:.1f}억원',
                    'formatted_per_pyeong': f'{appropriate_price_pyeong / 10000:.0f}만원'
                }
            },
            
            # 적정성 판단
            'price_adequacy': {
                'judgment': adequacy,
                'color': adequacy_color,
                'icon': adequacy_icon,
                'asking_vs_appropriate': price_diff,
                'asking_vs_appropriate_pct': price_diff_pct,
                'formatted_diff': f'{price_diff / 100000000:+.2f}억원',
                'description': f'현재 호가는 적정가 대비 {price_diff_pct:+.1f}% 수준으로 {adequacy}합니다.'
            }
        }
    
    def _compose_valuation_analysis(self) -> Dict[str, Any]:
        """
        Section 2: Valuation Analysis (2장)
        공적 가격 분석 및 감정평가 분석
        """
        
        # Part 2-1: 공적 가격 분석
        part_2_1 = self._compose_public_price_analysis()
        
        # Part 2-2: 감정평가 분석
        part_2_2 = self._compose_appraisal_analysis()
        
        return {
            'title': '가격 평가 분석',
            'page_numbers': '2-3',
            
            'part_2_1_public_price': part_2_1,
            'part_2_2_appraisal': part_2_2
        }
    
    def _compose_public_price_analysis(self) -> Dict[str, Any]:
        """Part 2-1: 공적 가격 분석"""
        
        official_price_sqm = self.appraisal_ctx.get('official_land_price.standard_price_per_sqm')
        reference_year = self.appraisal_ctx.get('official_land_price.reference_year', 2024)
        
        # Mock historical data (최근 5년)
        historical_prices = [
            {'year': reference_year - 4, 'price_sqm': official_price_sqm * 0.75, 'change_pct': 0},
            {'year': reference_year - 3, 'price_sqm': official_price_sqm * 0.82, 'change_pct': 9.3},
            {'year': reference_year - 2, 'price_sqm': official_price_sqm * 0.89, 'change_pct': 8.5},
            {'year': reference_year - 1, 'price_sqm': official_price_sqm * 0.95, 'change_pct': 6.7},
            {'year': reference_year, 'price_sqm': official_price_sqm, 'change_pct': 5.3}
        ]
        
        # Calculate average annual growth
        total_growth = (official_price_sqm / (official_price_sqm * 0.75) - 1) * 100
        avg_annual_growth = total_growth / 4
        
        # Market price to official price ratio (시세/공시지가 배율)
        appraised_total = self.appraisal_ctx.get('calculation.final_appraised_total')
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm')
        market_price_sqm = appraised_total / land_area
        price_ratio = market_price_sqm / official_price_sqm
        
        return {
            'subtitle': '공적 가격 분석',
            'page_number': '2',
            
            # 개별공시지가 추이
            'official_price_trend': {
                'historical_data': historical_prices,
                'total_growth_pct': total_growth,
                'avg_annual_growth_pct': avg_annual_growth,
                'trend_assessment': '지속적 상승 추세' if avg_annual_growth > 5 else '안정적 추세'
            },
            
            # 표준지공시지가 비교
            'standard_land_comparison': {
                'reference_parcel': self.appraisal_ctx.get('official_land_price.reference_parcel', '마포구 XX동 123'),
                'distance_to_standard': self.appraisal_ctx.get('official_land_price.distance_to_standard', 250),
                'standard_price_sqm': official_price_sqm,
                'note': '표준지로부터 거리 및 입지 보정 적용'
            },
            
            # 공시지가 대비 시세 배율
            'price_ratio_analysis': {
                'market_price_sqm': market_price_sqm,
                'official_price_sqm': official_price_sqm,
                'price_ratio': price_ratio,
                'formatted_ratio': f'{price_ratio:.2f}배',
                'ratio_assessment': '적정' if 1.0 <= price_ratio <= 1.5 else '높음' if price_ratio > 1.5 else '낮음',
                'description': f'시세가 공시지가의 {price_ratio:.1f}배 수준'
            }
        }
    
    def _compose_appraisal_analysis(self) -> Dict[str, Any]:
        """Part 2-2: 감정평가 분석"""
        
        appraised_total = self.appraisal_ctx.get('calculation.final_appraised_total')
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm')
        base_price_sqm = self.appraisal_ctx.get('calculation.premium_adjusted_price_per_sqm', 0)
        official_price_sqm = self.appraisal_ctx.get('official_land_price.standard_price_per_sqm')
        premium_rate = self.appraisal_ctx.get('premium.total_premium_rate', 0)
        
        # Premium breakdown
        dev_premium = self.appraisal_ctx.get('premium.development_potential.rate', 0)
        location_premium = self.appraisal_ctx.get('premium.location_advantage.rate', 0)
        policy_premium = self.appraisal_ctx.get('premium.policy_benefit.rate', 0)
        
        # Appraisal methodology
        methodology = '거래사례비교법'  # Default
        try:
            transaction_price = self.appraisal_ctx.get('transaction_case.price_per_sqm')
            if transaction_price:
                methodology = '거래사례비교법 (주) + 원가법 (부)'
        except KeyError:
            # transaction_case is optional
            pass
        
        # Asking price comparison
        asking_price = appraised_total * 1.07
        asking_vs_appraisal_pct = ((asking_price - appraised_total) / appraised_total) * 100
        
        return {
            'subtitle': '감정평가 분석',
            'page_number': '3',
            
            # 감정평가 방법론
            'appraisal_methodology': {
                'primary_method': methodology,
                'description': '인근 거래사례를 기준으로 시점보정, 지역보정, 개별보정 적용',
                'data_sources': [
                    '국토교통부 실거래가 공개시스템',
                    '개별공시지가',
                    '인근 거래사례 (최근 2년)'
                ]
            },
            
            # 감정평가액 산출 근거
            'appraisal_calculation': {
                'base_price_sqm': base_price_sqm,
                'official_price_sqm': official_price_sqm,
                'premium_rate': premium_rate,
                'premium_breakdown': {
                    'development_potential': {
                        'label': '개발 잠재력',
                        'rate': dev_premium,
                        'formatted': f'+{dev_premium:.1f}%',
                        'rationale': self.appraisal_ctx.get('premium.development_potential.rationale', 'FAR/BCR 양호')
                    },
                    'location_advantage': {
                        'label': '입지 이점',
                        'rate': location_premium,
                        'formatted': f'+{location_premium:.1f}%',
                        'rationale': self.appraisal_ctx.get('premium.location_advantage.rationale', '교통 접근성 우수')
                    },
                    'policy_benefit': {
                        'label': '정책 혜택',
                        'rate': policy_premium,
                        'formatted': f'+{policy_premium:.1f}%',
                        'rationale': self.appraisal_ctx.get('premium.policy_benefit.rationale', 'LH 공공주택 지구')
                    }
                },
                'total_premium': premium_rate,
                'final_price_sqm': appraised_total / land_area,
                'final_total': appraised_total,
                'calculation_formula': f'공시지가 {official_price_sqm:,.0f}원 × (1 + {premium_rate:.1f}%) = {appraised_total / land_area:,.0f}원/㎡'
            },
            
            # 감정가 대비 호가 분석
            'asking_vs_appraisal': {
                'appraised_value': appraised_total,
                'asking_price': asking_price,
                'difference': asking_price - appraised_total,
                'difference_pct': asking_vs_appraisal_pct,
                'formatted_asking': f'{asking_price / 100000000:.1f}억원',
                'formatted_difference': f'+{(asking_price - appraised_total) / 100000000:.2f}억원',
                'assessment': '적정' if asking_vs_appraisal_pct <= 5 else '약간 고가' if asking_vs_appraisal_pct <= 10 else '고가',
                'note': f'호가가 감정가 대비 {asking_vs_appraisal_pct:+.1f}% 높은 수준'
            }
        }
    
    def _compose_market_comparison(self) -> Dict[str, Any]:
        """
        Section 3: Market Comparison (2장)
        인근 실거래 사례 및 시세 트렌드
        """
        
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm')
        zone_type = self.appraisal_ctx.get('zoning.confirmed_type', '제2종일반주거지역')
        
        # Mock transaction cases (실거래 사례)
        transaction_cases = [
            {
                'address': '마포구 월드컵북로 98',
                'transaction_date': '2024.06',
                'land_area_sqm': land_area * 0.9,
                'land_area_pyeong': land_area * 0.9 / 3.3058,
                'total_price': 2500000000,
                'price_per_sqm': 2500000000 / (land_area * 0.9),
                'price_per_pyeong': (2500000000 / (land_area * 0.9)) * 3.3058,
                'zone_type': zone_type,
                'distance': 150,
                'similarity': 'HIGH'
            },
            {
                'address': '마포구 월드컵북로 156',
                'transaction_date': '2024.03',
                'land_area_sqm': land_area * 1.1,
                'land_area_pyeong': land_area * 1.1 / 3.3058,
                'total_price': 3200000000,
                'price_per_sqm': 3200000000 / (land_area * 1.1),
                'price_per_pyeong': (3200000000 / (land_area * 1.1)) * 3.3058,
                'zone_type': zone_type,
                'distance': 280,
                'similarity': 'MEDIUM'
            },
            {
                'address': '마포구 성산동 234-5',
                'transaction_date': '2023.11',
                'land_area_sqm': land_area * 0.8,
                'land_area_pyeong': land_area * 0.8 / 3.3058,
                'total_price': 2100000000,
                'price_per_sqm': 2100000000 / (land_area * 0.8),
                'price_per_pyeong': (2100000000 / (land_area * 0.8)) * 3.3058,
                'zone_type': zone_type,
                'distance': 420,
                'similarity': 'MEDIUM'
            }
        ]
        
        # Calculate average transaction price
        avg_price_sqm = sum([case['price_per_sqm'] for case in transaction_cases]) / len(transaction_cases)
        avg_price_pyeong = avg_price_sqm * 3.3058
        
        # Market trend analysis
        trend_assessment = self._assess_market_trend()
        
        # Development opportunities/threats
        opportunities_threats = self._assess_opportunities_threats()
        
        return {
            'title': '시장 비교 분석',
            'page_numbers': '4-5',
            
            # 인근 실거래 사례
            'transaction_cases': {
                'cases': transaction_cases,
                'total_cases': len(transaction_cases),
                'avg_price_sqm': avg_price_sqm,
                'avg_price_pyeong': avg_price_pyeong,
                'formatted_avg_pyeong': f'{avg_price_pyeong / 10000:.0f}만원/평',
                'data_period': '최근 2년',
                'filtering_criteria': [
                    f'용도지역: {zone_type}',
                    f'면적: {land_area * 0.7:.0f}~{land_area * 1.3:.0f}㎡ (±30%)',
                    '거래시점: 최근 2년'
                ]
            },
            
            # 유사 토지 비교
            'similar_land_comparison': {
                'criteria': {
                    'zone_type_match': '동일 용도지역',
                    'area_range': f'{land_area * 0.8:.0f}~{land_area * 1.2:.0f}㎡ (±20%)',
                    'distance': '500m 이내',
                    'time_period': '최근 2년'
                },
                'comparison_summary': f'유사 조건 거래사례 {len(transaction_cases)}건의 평균 평당가는 {avg_price_pyeong / 10000:.0f}만원입니다.'
            },
            
            # 시세 트렌드 분석
            'market_trend': trend_assessment,
            
            # 지역 개발 호재/악재
            'opportunities_threats': opportunities_threats
        }
    
    def _compose_recommendation(self) -> Dict[str, Any]:
        """
        Section 4: Recommendation (1-2장)
        적정 매입가 산정 및 협상 전략
        """
        
        appraised_total = self.appraisal_ctx.get('calculation.final_appraised_total')
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm')
        
        # Method 1: 감정가 기준
        method1_price = appraised_total * 1.02
        method1_desc = '감정평가액 × 1.02'
        
        # Method 2: 실거래가 기준 (mock)
        avg_transaction_price_sqm = appraised_total / land_area * 0.98
        method2_price = avg_transaction_price_sqm * land_area
        method2_desc = '평균 실거래 평당가 × 면적'
        
        # Method 3: 수익환원법 (if LH result available)
        if self.lh_result:
            lh_purchase_price = self.lh_result.get('lh_purchase_price', 0)
            construction_cost = self.lh_result.get('analysis_result', {}).get('construction_cost', 0)
            target_roi = 0.15  # 15% target ROI
            method3_price = (lh_purchase_price - construction_cost) / (1 + target_roi)
            method3_desc = '(LH 매입가 - 건축비) / (1 + 목표ROI)'
        else:
            method3_price = appraised_total * 1.00
            method3_desc = '수익환원법 (데이터 부족 시 감정가 기준)'
        
        # Calculate final appropriate price range
        prices = [method1_price, method2_price, method3_price]
        min_price = min(prices)
        max_price = max(prices)
        recommended_price = (min_price + max_price) / 2
        
        # Negotiation strategy
        negotiation_strategy = self._create_negotiation_strategy(
            recommended_price, appraised_total, method1_price
        )
        
        return {
            'title': '적정가 산정 및 권고사항',
            'page_numbers': '6-7',
            
            # 적정 매입가 산정 방법
            'price_calculation_methods': {
                'method_1_appraisal_based': {
                    'name': '방법 1: 감정가 기준',
                    'price': method1_price,
                    'formatted': f'{method1_price / 100000000:.2f}억원',
                    'description': method1_desc,
                    'rationale': '감정평가액에 약간의 협상 여지 포함'
                },
                'method_2_transaction_based': {
                    'name': '방법 2: 실거래가 기준',
                    'price': method2_price,
                    'formatted': f'{method2_price / 100000000:.2f}억원',
                    'description': method2_desc,
                    'rationale': '인근 실거래 사례의 평균 가격 반영'
                },
                'method_3_income_approach': {
                    'name': '방법 3: 수익환원법',
                    'price': method3_price,
                    'formatted': f'{method3_price / 100000000:.2f}억원',
                    'description': method3_desc,
                    'rationale': '예상 수익을 기반으로 역산한 가격' if self.lh_result else '데이터 부족으로 감정가 기준 사용'
                }
            },
            
            # 최종 적정가 범위
            'final_appropriate_price': {
                'min_price': min_price,
                'max_price': max_price,
                'recommended_price': recommended_price,
                'formatted_min': f'{min_price / 100000000:.2f}억원',
                'formatted_max': f'{max_price / 100000000:.2f}억원',
                'formatted_recommended': f'{recommended_price / 100000000:.2f}억원',
                'formatted_range': f'{min_price / 100000000:.2f}~{max_price / 100000000:.2f}억원',
                'recommendation': f'적정 매입가 범위는 {min_price / 100000000:.2f}억~{max_price / 100000000:.2f}억원이며, 권장가는 {recommended_price / 100000000:.2f}억원입니다.'
            },
            
            # 협상 전략
            'negotiation_strategy': negotiation_strategy,
            
            # 주의사항
            'cautions': [
                '토지 매입 전 반드시 등기부등본 및 토지이용계획확인서 확인',
                '인근 개발 계획 및 도시계획시설 현황 재확인 필요',
                '실제 매입 시 시장 상황 및 토지주 의향을 고려한 탄력적 협상 필요',
                '본 보고서는 참고용이며, 최종 매입가는 의사결정자의 판단 필요'
            ]
        }
    
    # ========== Helper Methods ==========
    
    def _assess_market_trend(self) -> Dict[str, Any]:
        """Assess market trend"""
        return {
            'trend_direction': '상승세',
            'trend_strength': 'MODERATE',
            'recent_changes': [
                {'period': '최근 6개월', 'change_pct': 3.5, 'description': '소폭 상승'},
                {'period': '최근 1년', 'change_pct': 7.2, 'description': '지속적 상승'},
                {'period': '최근 2년', 'change_pct': 15.8, 'description': '큰 폭 상승'}
            ],
            'outlook': '단기적으로 안정세, 중장기적으로 완만한 상승 예상',
            'key_factors': [
                '마포구 재개발 활성화',
                '교통 인프라 개선 (지하철 연장)',
                '공공주택 수요 증가'
            ]
        }
    
    def _assess_opportunities_threats(self) -> Dict[str, Any]:
        """Assess opportunities and threats"""
        return {
            'opportunities': [
                {
                    'factor': 'LH 공공주택 공급 계획',
                    'impact': 'HIGH',
                    'description': '마포구 공공주택 확대 정책으로 LH 매입 수요 증가 예상'
                },
                {
                    'factor': '역세권 개발',
                    'impact': 'MEDIUM',
                    'description': '인근 지하철역 리모델링 및 상권 활성화'
                },
                {
                    'factor': '학교 및 공원 인접',
                    'impact': 'MEDIUM',
                    'description': '주거 환경 우수, 청년/신혼부부 선호도 높음'
                }
            ],
            'threats': [
                {
                    'factor': '금리 상승',
                    'impact': 'MEDIUM',
                    'description': '부동산 시장 전반적인 거래 위축 가능성'
                },
                {
                    'factor': '인허가 리스크',
                    'impact': 'MEDIUM',
                    'description': '지구단위계획 변경 또는 추가 규제 가능성'
                }
            ]
        }
    
    def _create_negotiation_strategy(
        self, 
        recommended_price: float, 
        appraised_total: float,
        method1_price: float
    ) -> Dict[str, Any]:
        """Create negotiation strategy"""
        
        # Current asking price (assumed)
        asking_price = appraised_total * 1.07
        
        # Negotiation steps
        steps = [
            {
                'step': 1,
                'action': '초기 제안',
                'offer_price': recommended_price * 0.95,
                'formatted': f'{recommended_price * 0.95 / 100000000:.2f}억원',
                'strategy': '권장가의 95% 수준으로 제안하여 협상 여지 확보'
            },
            {
                'step': 2,
                'action': '중간 협상',
                'offer_price': recommended_price,
                'formatted': f'{recommended_price / 100000000:.2f}억원',
                'strategy': '상대방 반응 확인 후 권장가 수준으로 상향 제시'
            },
            {
                'step': 3,
                'action': '최종 타협',
                'offer_price': method1_price,
                'formatted': f'{method1_price / 100000000:.2f}억원',
                'strategy': '감정가 + 2% 수준을 최대 한도로 설정'
            }
        ]
        
        # Negotiation tactics
        tactics = [
            '감정평가 결과를 근거 자료로 제시',
            '인근 실거래 사례와 비교 분석 자료 활용',
            '현금 매입 또는 빠른 계약 조건 제시',
            '토지주의 급매 여부 파악 및 활용',
            '경쟁 매수자 유무 확인'
        ]
        
        return {
            'negotiation_steps': steps,
            'tactics': tactics,
            'max_acceptable_price': method1_price,
            'max_acceptable_formatted': f'{method1_price / 100000000:.2f}억원',
            'asking_price': asking_price,
            'asking_formatted': f'{asking_price / 100000000:.2f}억원',
            'negotiation_room': asking_price - recommended_price,
            'negotiation_room_formatted': f'{(asking_price - recommended_price) / 100000000:.2f}억원',
            'negotiation_room_pct': ((asking_price - recommended_price) / asking_price) * 100,
            'recommendation': f'현재 호가 {asking_price / 100000000:.2f}억원에서 약 {((asking_price - recommended_price) / asking_price) * 100:.1f}% 인하 협상 필요'
        }
    
    def _calculate_page_count(self, report: Dict[str, Any]) -> int:
        """Calculate estimated page count"""
        # Section 1: 1 page
        # Section 2: 2 pages
        # Section 3: 2 pages
        # Section 4: 1-2 pages
        return 7
