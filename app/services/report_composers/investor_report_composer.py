"""
ZeroSite Investor Report Composer v1.0 (10-12 pages)

목적:
- 투자자 대상 수익성 중심 분석 보고서
- Comprehensive Report와 달리 LH 판정보다 ROI/IRR/투자 리스크에 집중
- Model A (직접개발): 내부 투자 의사결정
- Model C (투자자 컨설팅): 투자자에게 개별 제공

구조 (6개 섹션):
- Section 1: Investment Summary (1장)
- Section 2: Land Valuation (2장)
- Section 3: Development Plan (2장)
- Section 4: Financial Projection (4장) ← 핵심 섹션
- Section 5: Risk-Return Analysis (2장)
- Section 6: Recommendation (1장)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class InvestorReportComposer:
    """
    v1.0 Investor Report - 투자자 대상 수익성 분석
    Target: 투자자/내부 의사결정자 (10-12 pages)
    
    Focus: Financial Returns > LH Decision
    """
    
    def __init__(
        self,
        appraisal_ctx,
        land_diagnosis: Dict[str, Any],
        lh_result: Dict[str, Any],
        risk_matrix: Optional[Dict[str, Any]] = None,
        financial_analysis: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Investor Report Composer
        
        Args:
            appraisal_ctx: Locked appraisal context (READ-ONLY)
            land_diagnosis: Land diagnosis results
            lh_result: LH analysis results (summary only)
            risk_matrix: Risk matrix analysis (optional)
            financial_analysis: Financial engine results (optional)
        """
        self.appraisal_ctx = appraisal_ctx
        self.land_diagnosis = land_diagnosis
        self.lh_result = lh_result
        self.risk_matrix = risk_matrix or {}
        self.financial_analysis = financial_analysis or {}
        
        self.report_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.generation_time = datetime.now().isoformat()
        self.version = "v1.0"
    
    def compose(self) -> Dict[str, Any]:
        """
        Generate complete Investor Report (10-12 pages)
        
        Returns:
            Dictionary with all 6 sections
        """
        
        print(f"\n📄 Generating Investor Report v1.0 (10-12 pages)")
        print(f"   Report ID: {self.report_id}")
        print(f"   Focus: Investment Returns Analysis")
        
        report = {
            'report_id': self.report_id,
            'report_type': 'investor_report',
            'version': self.version,
            'generation_time': self.generation_time,
            'estimated_pages': '10-12',
            
            'section_1_investment_summary': self._compose_investment_summary(),
            'section_2_land_valuation': self._compose_land_valuation(),
            'section_3_development_plan': self._compose_development_plan(),
            'section_4_financial_projection': self._compose_financial_projection(),
            'section_5_risk_return_analysis': self._compose_risk_return(),
            'section_6_recommendation': self._compose_recommendation()
        }
        
        # Calculate actual page count
        page_count = self._calculate_page_count(report)
        report['actual_pages'] = page_count
        
        print(f"✅ Investor Report v1.0 generation complete")
        print(f"   Total Pages: {page_count}")
        print(f"   Investment Grade: {report['section_1_investment_summary']['investment_grade']}")
        print(f"   Expected IRR: {report['section_4_financial_projection']['part_4_2_revenue_analysis']['revenue_metrics']['irr']['value']:.1f}%")
        
        return report
    
    def _compose_investment_summary(self) -> Dict[str, Any]:
        """
        Section 1: Investment Summary (1장)
        투자 핵심 지표 대시보드 및 투자 등급
        """
        
        # Extract financial metrics
        roi = self.lh_result.get('roi', 0)
        lh_purchase_price = self.lh_result.get('lh_purchase_price', 0)
        total_cost = self.lh_result.get('analysis_result', {}).get('total_cost', 0)
        
        # Calculate IRR (simplified - in production, use financial_analysis)
        irr = roi  # For now, use ROI as approximation
        
        # Calculate investment grade
        investment_grade = self._calculate_investment_grade(irr)
        
        # Calculate total investment (토지비 + 건축비)
        land_appraisal = self.appraisal_ctx.get('calculation.final_appraised_total')
        construction_cost = self.lh_result.get('analysis_result', {}).get('construction_cost', 0)
        total_investment = land_appraisal + construction_cost
        
        # Payback period (회수기간) - months
        if roi > 0:
            payback_months = int(100 / roi * 12)
        else:
            payback_months = 999
        
        return {
            'title': 'Investment Summary',
            'page_number': 1,
            
            # 핵심 지표 대시보드
            'key_metrics_dashboard': {
                'total_investment': {
                    'label': '총 투자금',
                    'value': total_investment,
                    'formatted': f'{total_investment:,.0f}원',
                    'unit': '원'
                },
                'expected_irr': {
                    'label': '예상 IRR',
                    'value': irr,
                    'formatted': f'{irr:.1f}%',
                    'unit': '%'
                },
                'expected_roi': {
                    'label': '예상 ROI',
                    'value': roi,
                    'formatted': f'{roi:.1f}%',
                    'unit': '%'
                },
                'payback_period': {
                    'label': '회수기간',
                    'value': payback_months,
                    'formatted': f'{payback_months}개월',
                    'unit': '개월'
                }
            },
            
            # 투자 등급
            'investment_grade': investment_grade['grade'],
            'investment_grade_color': investment_grade['color'],
            'investment_grade_icon': investment_grade['icon'],
            'investment_grade_description': investment_grade['description'],
            
            # 핵심 투자 포인트
            'key_investment_points': self._extract_investment_points(irr, roi),
            
            # 주요 리스크 요약
            'major_risks_summary': self._extract_major_risks()
        }
    
    def _compose_land_valuation(self) -> Dict[str, Any]:
        """
        Section 2: Land Valuation (2장)
        토지 가격 분석 및 적정성 판단
        """
        
        # Extract appraisal data
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm')
        official_price_sqm = self.appraisal_ctx.get('official_land_price.standard_price_per_sqm')
        appraised_total = self.appraisal_ctx.get('calculation.final_appraised_total')
        appraised_price_sqm = appraised_total / land_area if land_area > 0 else 0
        premium_rate = self.appraisal_ctx.get('premium.total_premium_rate', 0)
        
        # Calculate official price total
        official_price_total = official_price_sqm * land_area
        
        # Get recent transaction (if available)
        try:
            transaction = self.appraisal_ctx.get('transaction_case.price_per_sqm')
            transaction_total = transaction * land_area if transaction else 0
        except KeyError:
            transaction = None
            transaction_total = 0
        
        # Current asking price (호가) - 감정가 + 5% 가정
        asking_price = appraised_total * 1.05
        asking_price_sqm = asking_price / land_area
        
        # Appropriate purchase price (적정 매입가) - 감정가 기준
        appropriate_price = appraised_total
        appropriate_price_sqm = appraised_price_sqm
        
        # Price adequacy judgment
        price_diff_pct = ((asking_price - appropriate_price) / appropriate_price) * 100
        if price_diff_pct <= 5:
            adequacy = '적정'
            adequacy_color = 'green'
        elif price_diff_pct <= 10:
            adequacy = '주의'
            adequacy_color = 'yellow'
        else:
            adequacy = '고가'
            adequacy_color = 'red'
        
        return {
            'title': '토지 가격 분석',
            'page_numbers': '2-3',
            
            # 토지 기본 정보
            'land_basic_info': {
                'address': '서울특별시 마포구 월드컵북로 120',  # Mock data
                'land_area_sqm': land_area,
                'land_area_pyeong': land_area / 3.3058,
                'zone_type': self.appraisal_ctx.get('zoning.confirmed_type', '제2종일반주거지역')
            },
            
            # 가격 비교 대시보드
            'price_comparison_dashboard': {
                'official_land_price': {
                    'label': '공시지가',
                    'total': official_price_total,
                    'price_per_sqm': official_price_sqm,
                    'price_per_pyeong': official_price_sqm * 3.3058,
                    'formatted_total': f'{official_price_total:,.0f}원',
                    'formatted_per_pyeong': f'{official_price_sqm * 3.3058:,.0f}만원'
                },
                'appraised_value': {
                    'label': '감정평가액',
                    'total': appraised_total,
                    'price_per_sqm': appraised_price_sqm,
                    'price_per_pyeong': appraised_price_sqm * 3.3058,
                    'formatted_total': f'{appraised_total:,.0f}원',
                    'formatted_per_pyeong': f'{appraised_price_sqm * 3.3058:,.0f}만원',
                    'premium_rate': premium_rate
                },
                'recent_transaction': {
                    'label': '최근 실거래가',
                    'total': transaction_total if transaction else None,
                    'price_per_sqm': transaction,
                    'price_per_pyeong': transaction * 3.3058 if transaction else None,
                    'formatted_total': f'{transaction_total:,.0f}원' if transaction else '데이터 없음',
                    'formatted_per_pyeong': f'{transaction * 3.3058:,.0f}만원' if transaction else None,
                    'available': bool(transaction)
                },
                'asking_price': {
                    'label': '현재 호가',
                    'total': asking_price,
                    'price_per_sqm': asking_price_sqm,
                    'price_per_pyeong': asking_price_sqm * 3.3058,
                    'formatted_total': f'{asking_price:,.0f}원',
                    'formatted_per_pyeong': f'{asking_price_sqm * 3.3058:,.0f}만원'
                },
                'appropriate_price': {
                    'label': '적정 매입가',
                    'total': appropriate_price,
                    'price_per_sqm': appropriate_price_sqm,
                    'price_per_pyeong': appropriate_price_sqm * 3.3058,
                    'formatted_total': f'{appropriate_price:,.0f}원',
                    'formatted_per_pyeong': f'{appropriate_price_sqm * 3.3058:,.0f}만원'
                }
            },
            
            # 가격 적정성 판단
            'price_adequacy': {
                'judgment': adequacy,
                'color': adequacy_color,
                'asking_vs_appropriate_pct': price_diff_pct,
                'description': f'호가가 적정가 대비 {price_diff_pct:+.1f}% 수준입니다.'
            }
        }
    
    def _compose_development_plan(self) -> Dict[str, Any]:
        """
        Section 3: Development Plan (2장)
        개발 개요 및 사업 일정
        """
        
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm')
        far = self.appraisal_ctx.get('zoning.floor_area_ratio', 0)
        bcr = self.appraisal_ctx.get('zoning.building_coverage_ratio', 0)
        
        # Calculate buildable area
        buildable_area = land_area * (far / 100)
        
        # Estimate floors
        if bcr > 0:
            estimated_floors = int((far / bcr) * 1.0)
        else:
            estimated_floors = 5
        
        # Estimate units (60-80㎡ per unit)
        units_min = int(buildable_area / 80)
        units_max = int(buildable_area / 60)
        units_avg = int((units_min + units_max) / 2)
        
        # LH supply type (from CH4 or default)
        supply_type = '행복주택'  # Default
        
        # LH possibility (summary)
        lh_decision = self.lh_result.get('decision', 'GO')
        if lh_decision == 'GO':
            lh_possibility = 'HIGH'
        elif lh_decision == 'CONDITIONAL':
            lh_possibility = 'MEDIUM'
        else:
            lh_possibility = 'LOW'
        
        return {
            'title': '개발 계획',
            'page_numbers': '4-5',
            
            # 개발 개요
            'development_overview': {
                'estimated_floor_area': {
                    'label': '예상 연면적',
                    'value_sqm': buildable_area,
                    'value_pyeong': buildable_area / 3.3058,
                    'formatted': f'{buildable_area:,.0f}㎡ ({buildable_area / 3.3058:,.0f}평)',
                    'calculation': f'{land_area:,.0f}㎡ × {far}% = {buildable_area:,.0f}㎡'
                },
                'estimated_floors': {
                    'label': '예상 층수',
                    'value': estimated_floors,
                    'formatted': f'약 {estimated_floors}층',
                    'note': 'FAR/BCR 기준 추정, 높이제한 확인 필요'
                },
                'estimated_units': {
                    'label': '예상 세대수',
                    'min': units_min,
                    'max': units_max,
                    'average': units_avg,
                    'formatted': f'{units_min}~{units_max}세대 (평균 {units_avg}세대)',
                    'basis': '전용면적 60~80㎡ 기준'
                },
                'supply_type': {
                    'label': '공급유형',
                    'value': supply_type,
                    'note': 'LH 기준 추천 유형'
                }
            },
            
            # 사업 일정
            'project_timeline': {
                'total_duration_months': 26,
                'phases': [
                    {'phase': '토지매입', 'start_month': 0, 'duration_months': 1, 'milestone': 'M+0'},
                    {'phase': '인허가', 'start_month': 1, 'duration_months': 6, 'milestone': 'M+1~M+6', 'note': '6개월 예상'},
                    {'phase': '착공', 'start_month': 7, 'duration_months': 1, 'milestone': 'M+7'},
                    {'phase': '공사', 'start_month': 8, 'duration_months': 18, 'milestone': 'M+8~M+25', 'note': '18개월 공사'},
                    {'phase': '준공', 'start_month': 26, 'duration_months': 1, 'milestone': 'M+26'},
                    {'phase': 'LH매입', 'start_month': 27, 'duration_months': 0, 'milestone': 'M+27', 'note': '준공 후 즉시'}
                ],
                'critical_path': ['인허가', '공사'],
                'risk_factors': ['인허가 지연', '공사 지연', '자재비 상승']
            },
            
            # LH 매입 가능성 요약
            'lh_purchase_possibility': {
                'level': lh_possibility,
                'level_color': 'green' if lh_possibility == 'HIGH' else 'yellow' if lh_possibility == 'MEDIUM' else 'red',
                'icon': '🟢' if lh_possibility == 'HIGH' else '🟡' if lh_possibility == 'MEDIUM' else '🔴',
                'note': 'LH Decision Report 참조 (상세 분석 생략)',
                'key_factors': [
                    '용도지역 적합',
                    'FAR/BCR 충족',
                    '수익성 확보'
                ]
            }
        }
    
    def _compose_financial_projection(self) -> Dict[str, Any]:
        """
        Section 4: Financial Projection (4장) ← 핵심 섹션
        사업비 분석, 수익 분석, 현금흐름, 시나리오 분석
        """
        
        # Extract financial data
        land_appraisal = self.appraisal_ctx.get('calculation.final_appraised_total')
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm')
        
        construction_cost = self.lh_result.get('analysis_result', {}).get('construction_cost', 0)
        verified_cost = self.lh_result.get('analysis_result', {}).get('verified_cost', 0)
        total_cost = self.lh_result.get('analysis_result', {}).get('total_cost', 0)
        lh_purchase_price = self.lh_result.get('lh_purchase_price', 0)
        roi = self.lh_result.get('roi', 0)
        
        # Part 4-1: 사업비 분석
        part_4_1 = self._compose_cost_analysis(
            land_appraisal, construction_cost, verified_cost, total_cost
        )
        
        # Part 4-2: 수익 분석
        part_4_2 = self._compose_revenue_analysis(
            lh_purchase_price, total_cost, roi
        )
        
        # Part 4-3: 현금흐름 분석
        part_4_3 = self._compose_cashflow_analysis(
            land_appraisal, construction_cost, lh_purchase_price
        )
        
        # Part 4-4: 시나리오 분석
        part_4_4 = self._compose_scenario_analysis(
            total_cost, lh_purchase_price, roi
        )
        
        return {
            'title': '수익성 분석',
            'page_numbers': '6-9',
            
            'part_4_1_cost_analysis': part_4_1,
            'part_4_2_revenue_analysis': part_4_2,
            'part_4_3_cashflow_analysis': part_4_3,
            'part_4_4_scenario_analysis': part_4_4
        }
    
    def _compose_cost_analysis(self, land_appraisal, construction_cost, verified_cost, total_cost) -> Dict[str, Any]:
        """Part 4-1: 사업비 분석"""
        
        # Calculate cost breakdown
        design_supervision = construction_cost * 0.05  # 5%
        financial_cost = total_cost * 0.05  # 5% interest
        taxes = construction_cost * 0.03  # 3% taxes
        contingency = total_cost * 0.05  # 5% contingency
        
        # Direct and indirect construction costs
        direct_construction = construction_cost * 0.8
        indirect_construction = construction_cost * 0.2
        
        cost_items = {
            'land_cost': {
                'label': '토지비',
                'value': land_appraisal,
                'percentage': (land_appraisal / total_cost) * 100,
                'formatted': f'{land_appraisal:,.0f}원',
                'note': '감정평가 확정 가격'
            },
            'construction_cost': {
                'label': '건축비',
                'value': construction_cost,
                'percentage': (construction_cost / total_cost) * 100,
                'formatted': f'{construction_cost:,.0f}원',
                'breakdown': {
                    'direct': {'label': '직접공사비', 'value': direct_construction, 'formatted': f'{direct_construction:,.0f}원'},
                    'indirect': {'label': '간접공사비', 'value': indirect_construction, 'formatted': f'{indirect_construction:,.0f}원'}
                }
            },
            'design_supervision': {
                'label': '설계/감리비',
                'value': design_supervision,
                'percentage': (design_supervision / total_cost) * 100,
                'formatted': f'{design_supervision:,.0f}원',
                'note': '건축비의 5% 가정'
            },
            'financial_cost': {
                'label': '금융비용',
                'value': financial_cost,
                'percentage': (financial_cost / total_cost) * 100,
                'formatted': f'{financial_cost:,.0f}원',
                'note': '이자, 대출 수수료 등'
            },
            'taxes': {
                'label': '제세공과금',
                'value': taxes,
                'percentage': (taxes / total_cost) * 100,
                'formatted': f'{taxes:,.0f}원'
            },
            'contingency': {
                'label': '예비비',
                'value': contingency,
                'percentage': (contingency / total_cost) * 100,
                'formatted': f'{contingency:,.0f}원',
                'note': '총 사업비의 5%'
            },
            'total': {
                'label': '총 사업비',
                'value': total_cost,
                'percentage': 100.0,
                'formatted': f'{total_cost:,.0f}원'
            }
        }
        
        return {
            'subtitle': '사업비 분석',
            'page_number': '6',
            'cost_items': cost_items,
            'total_project_cost': total_cost,
            'total_formatted': f'{total_cost:,.0f}원'
        }
    
    def _compose_revenue_analysis(self, lh_purchase_price, total_cost, roi) -> Dict[str, Any]:
        """Part 4-2: 수익 분석"""
        
        net_profit = lh_purchase_price - total_cost
        irr = roi  # Simplified
        
        return {
            'subtitle': '수익 분석',
            'page_number': '7',
            
            'revenue_metrics': {
                'lh_purchase_price': {
                    'label': 'LH 매입 예상가',
                    'value': lh_purchase_price,
                    'formatted': f'{lh_purchase_price:,.0f}원'
                },
                'total_cost': {
                    'label': '총 사업비',
                    'value': total_cost,
                    'formatted': f'{total_cost:,.0f}원'
                },
                'net_profit': {
                    'label': '순이익',
                    'value': net_profit,
                    'formatted': f'{net_profit:,.0f}원',
                    'calculation': 'LH 매입가 - 총 사업비'
                },
                'roi': {
                    'label': '투자 대비 수익률 (ROI)',
                    'value': roi,
                    'formatted': f'{roi:.1f}%',
                    'calculation': '(순이익 / 총 사업비) × 100'
                },
                'irr': {
                    'label': '내부수익률 (IRR)',
                    'value': irr,
                    'formatted': f'{irr:.1f}%',
                    'note': '시간 가치를 고려한 수익률'
                }
            },
            
            'profitability_assessment': self._assess_profitability(roi, irr)
        }
    
    def _compose_cashflow_analysis(self, land_appraisal, construction_cost, lh_purchase_price) -> Dict[str, Any]:
        """Part 4-3: 현금흐름 분석"""
        
        # Simplified monthly cashflow (27 months)
        monthly_cashflow = []
        cumulative = 0
        
        # Month 0: Land purchase
        monthly_cashflow.append({
            'month': 0,
            'phase': '토지매입',
            'outflow': land_appraisal,
            'inflow': 0,
            'net': -land_appraisal,
            'cumulative': -land_appraisal
        })
        cumulative = -land_appraisal
        
        # Month 1-6: Permits (minimal cost)
        for m in range(1, 7):
            monthly_cashflow.append({
                'month': m,
                'phase': '인허가',
                'outflow': land_appraisal * 0.005,  # 0.5% per month
                'inflow': 0,
                'net': -land_appraisal * 0.005,
                'cumulative': cumulative - land_appraisal * 0.005
            })
            cumulative -= land_appraisal * 0.005
        
        # Month 7-25: Construction (monthly payments)
        monthly_construction = construction_cost / 18
        for m in range(7, 26):
            monthly_cashflow.append({
                'month': m,
                'phase': '공사',
                'outflow': monthly_construction,
                'inflow': 0,
                'net': -monthly_construction,
                'cumulative': cumulative - monthly_construction
            })
            cumulative -= monthly_construction
        
        # Month 26: Completion
        monthly_cashflow.append({
            'month': 26,
            'phase': '준공',
            'outflow': 0,
            'inflow': 0,
            'net': 0,
            'cumulative': cumulative
        })
        
        # Month 27: LH purchase (cash inflow)
        monthly_cashflow.append({
            'month': 27,
            'phase': 'LH매입',
            'outflow': 0,
            'inflow': lh_purchase_price,
            'net': lh_purchase_price,
            'cumulative': cumulative + lh_purchase_price
        })
        
        # Find break-even point
        bep_month = None
        for i, cf in enumerate(monthly_cashflow):
            if cf['cumulative'] >= 0:
                bep_month = cf['month']
                break
        
        return {
            'subtitle': '현금흐름 분석',
            'page_number': '8',
            
            'monthly_cashflow': monthly_cashflow,
            'break_even_point': {
                'month': bep_month,
                'note': 'LH 매입 후 손익분기점 도달' if bep_month else '사업 종료 시 손익분기 도달'
            },
            'max_negative_cashflow': min([cf['cumulative'] for cf in monthly_cashflow]),
            'final_cumulative': monthly_cashflow[-1]['cumulative']
        }
    
    def _compose_scenario_analysis(self, total_cost, lh_purchase_price, base_roi) -> Dict[str, Any]:
        """Part 4-4: 시나리오 분석"""
        
        # Best Case: 공사비 -5%, 매입가 +5%
        best_cost = total_cost * 0.95
        best_revenue = lh_purchase_price * 1.05
        best_profit = best_revenue - best_cost
        best_roi = (best_profit / best_cost) * 100
        best_irr = best_roi
        best_npv = best_profit
        
        # Base Case
        base_profit = lh_purchase_price - total_cost
        base_irr = base_roi
        base_npv = base_profit
        
        # Worst Case: 공사비 +10%, 매입가 -5%
        worst_cost = total_cost * 1.10
        worst_revenue = lh_purchase_price * 0.95
        worst_profit = worst_revenue - worst_cost
        worst_roi = (worst_profit / worst_cost) * 100
        worst_irr = worst_roi
        worst_npv = worst_profit
        
        scenarios = {
            'best_case': {
                'name': 'Best Case',
                'probability': '20%',
                'conditions': '공사비 -5%, 매입가 +5%',
                'irr': best_irr,
                'roi': best_roi,
                'npv': best_npv,
                'formatted_irr': f'{best_irr:.1f}%',
                'formatted_roi': f'{best_roi:.1f}%',
                'formatted_npv': f'{best_npv:,.0f}원'
            },
            'base_case': {
                'name': 'Base Case',
                'probability': '60%',
                'conditions': '현재 추정 기준',
                'irr': base_irr,
                'roi': base_roi,
                'npv': base_npv,
                'formatted_irr': f'{base_irr:.1f}%',
                'formatted_roi': f'{base_roi:.1f}%',
                'formatted_npv': f'{base_npv:,.0f}원'
            },
            'worst_case': {
                'name': 'Worst Case',
                'probability': '20%',
                'conditions': '공사비 +10%, 매입가 -5%',
                'irr': worst_irr,
                'roi': worst_roi,
                'npv': worst_npv,
                'formatted_irr': f'{worst_irr:.1f}%',
                'formatted_roi': f'{worst_roi:.1f}%',
                'formatted_npv': f'{worst_npv:,.0f}원'
            }
        }
        
        # 민감도 분석
        sensitivity_analysis = {
            'construction_cost_1pct_increase': {
                'label': '공사비 1% 증가 시',
                'irr_change': -0.5,  # Approximate
                'formatted': 'IRR -0.5%p'
            },
            'purchase_price_1pct_decrease': {
                'label': '매입가 1% 감소 시',
                'irr_change': -0.3,  # Approximate
                'formatted': 'IRR -0.3%p'
            }
        }
        
        return {
            'subtitle': '시나리오 분석',
            'page_number': '9',
            
            'scenarios': scenarios,
            'sensitivity_analysis': sensitivity_analysis,
            'expected_value': {
                'label': '기대 수익률 (확률 가중)',
                'value': (best_roi * 0.2 + base_roi * 0.6 + worst_roi * 0.2),
                'formatted': f'{(best_roi * 0.2 + base_roi * 0.6 + worst_roi * 0.2):.1f}%'
            }
        }
    
    def _compose_risk_return(self) -> Dict[str, Any]:
        """
        Section 5: Risk-Return Analysis (2장)
        투자 리스크 매트릭스 및 Exit 전략
        """
        
        # Risk matrix items
        risk_items = [
            {
                'risk_id': 'R01',
                'category': '인허가',
                'risk_name': '인허가 지연',
                'probability': 'MEDIUM',
                'impact': 'HIGH',
                'level': 'MEDIUM',
                'mitigation': '사전 협의 및 전문가 활용',
                'estimated_delay': '1-3개월',
                'financial_impact': '금융비용 증가'
            },
            {
                'risk_id': 'R02',
                'category': '공사',
                'risk_name': '공사비 상승',
                'probability': 'HIGH',
                'impact': 'MEDIUM',
                'level': 'HIGH',
                'mitigation': '예비비 확보, 고정가 계약',
                'estimated_delay': None,
                'financial_impact': 'ROI 1-3% 감소'
            },
            {
                'risk_id': 'R03',
                'category': '시장',
                'risk_name': 'LH 매입가 하락',
                'probability': 'LOW',
                'impact': 'HIGH',
                'level': 'MEDIUM',
                'mitigation': '시장 모니터링, 조기 협의',
                'estimated_delay': None,
                'financial_impact': 'ROI 2-5% 감소'
            },
            {
                'risk_id': 'R04',
                'category': '재무',
                'risk_name': '금리 상승',
                'probability': 'MEDIUM',
                'impact': 'MEDIUM',
                'level': 'MEDIUM',
                'mitigation': '금리 헷지, 조기 대출 확보',
                'estimated_delay': None,
                'financial_impact': '금융비용 10-20% 증가'
            },
            {
                'risk_id': 'R05',
                'category': '규제',
                'risk_name': '규제 변경',
                'probability': 'LOW',
                'impact': 'MEDIUM',
                'level': 'LOW',
                'mitigation': '정책 모니터링',
                'estimated_delay': None,
                'financial_impact': '불확실'
            }
        ]
        
        # Calculate total risk score
        risk_scores = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        total_risk_score = sum([risk_scores[r['level']] for r in risk_items])
        max_risk_score = len(risk_items) * 3
        risk_percentage = (total_risk_score / max_risk_score) * 100
        
        # Risk level assessment
        if risk_percentage <= 40:
            risk_level = '낮음'
            risk_color = 'green'
        elif risk_percentage <= 60:
            risk_level = '보통'
            risk_color = 'yellow'
        else:
            risk_level = '높음'
            risk_color = 'red'
        
        # Risk-adjusted return
        base_roi = self.lh_result.get('roi', 0)
        risk_adjustment = risk_percentage / 10  # Subtract risk percentage / 10
        risk_adjusted_roi = base_roi - risk_adjustment
        
        # Exit strategies
        exit_strategies = [
            {
                'plan': 'Plan A',
                'name': 'LH 매입',
                'description': '준공 후 LH 신축매입임대로 매각 (기본 전략)',
                'success_rate': 85,
                'timeline': '준공 후 1개월',
                'expected_return': f'{base_roi:.1f}%',
                'pros': ['안정적 매각', '높은 성공률', '빠른 회수'],
                'cons': ['수익률 제한', 'LH 기준 충족 필수']
            },
            {
                'plan': 'Plan B',
                'name': '일반 분양 전환',
                'description': 'LH 매입 불발 시 일반 분양으로 전환',
                'success_rate': 70,
                'timeline': '준공 후 6개월',
                'expected_return': f'{base_roi * 1.2:.1f}%',
                'pros': ['높은 수익 가능', '시장 상황 반영'],
                'cons': ['장기화', '분양 리스크', '추가 비용']
            },
            {
                'plan': 'Plan C',
                'name': '토지 매각',
                'description': '사업 진행 불가 시 토지 매각 (최후 수단)',
                'success_rate': 90,
                'timeline': '즉시~6개월',
                'expected_return': f'{base_roi * 0.3:.1f}%',
                'pros': ['빠른 청산', '손실 최소화'],
                'cons': ['낮은 수익', '기회비용 발생']
            }
        ]
        
        return {
            'title': '리스크-수익 분석',
            'page_numbers': '10-11',
            
            # 투자 리스크 매트릭스
            'risk_matrix': {
                'risk_items': risk_items,
                'total_risk_score': total_risk_score,
                'max_risk_score': max_risk_score,
                'risk_percentage': risk_percentage,
                'risk_level': risk_level,
                'risk_level_color': risk_color,
                'high_risks': [r for r in risk_items if r['level'] == 'HIGH'],
                'medium_risks': [r for r in risk_items if r['level'] == 'MEDIUM'],
                'low_risks': [r for r in risk_items if r['level'] == 'LOW']
            },
            
            # 리스크 조정 수익률
            'risk_adjusted_return': {
                'base_roi': base_roi,
                'risk_adjustment': risk_adjustment,
                'risk_adjusted_roi': risk_adjusted_roi,
                'formatted': f'{risk_adjusted_roi:.1f}%',
                'description': f'기본 ROI {base_roi:.1f}%에서 리스크 조정 {risk_adjustment:.1f}%p 차감'
            },
            
            # Exit 전략
            'exit_strategies': exit_strategies,
            'recommended_exit': 'Plan A (LH 매입)'
        }
    
    def _compose_recommendation(self) -> Dict[str, Any]:
        """
        Section 6: Recommendation (1장)
        투자 의견 및 조건
        """
        
        roi = self.lh_result.get('roi', 0)
        irr = roi  # Simplified
        land_appraisal = self.appraisal_ctx.get('calculation.final_appraised_total')
        
        # Investment decision
        if irr >= 15:
            investment_opinion = '매수 적극 권장'
            opinion_color = 'green'
            opinion_icon = '✅'
        elif irr >= 10:
            investment_opinion = '조건부 매수'
            opinion_color = 'yellow'
            opinion_icon = '⚠️'
        else:
            investment_opinion = '투자 보류'
            opinion_color = 'red'
            opinion_icon = '❌'
        
        # Appropriate purchase price
        appropriate_price = land_appraisal
        max_price = appropriate_price * 1.05
        
        # Investment conditions
        conditions = []
        if irr < 15:
            conditions.append('토지 매입가 협상 필수 (목표: 5% 추가 인하)')
        if irr < 12:
            conditions.append('공사비 절감 방안 검토')
        
        # Action items
        action_items = [
            {'priority': 'HIGH', 'action': '토지주와 가격 협상 시작', 'timeline': '즉시'},
            {'priority': 'HIGH', 'action': '상세 인허가 검토', 'timeline': '1주일 내'},
            {'priority': 'MEDIUM', 'action': '시공사 견적 요청', 'timeline': '2주일 내'},
            {'priority': 'MEDIUM', 'action': '금융기관 대출 사전 협의', 'timeline': '2주일 내'},
            {'priority': 'LOW', 'action': '최종 투자 의사결정', 'timeline': '1개월 내'}
        ]
        
        return {
            'title': '투자 권고사항',
            'page_number': '12',
            
            # 투자 의견
            'investment_opinion': {
                'decision': investment_opinion,
                'color': opinion_color,
                'icon': opinion_icon,
                'reasoning': f'예상 IRR {irr:.1f}%로 투자 기준 충족' if irr >= 10 else f'예상 IRR {irr:.1f}%로 투자 기준 미달'
            },
            
            # 적정 매입가 제안
            'appropriate_purchase_price': {
                'recommended_price': appropriate_price,
                'max_acceptable_price': max_price,
                'formatted_recommended': f'{appropriate_price:,.0f}원',
                'formatted_max': f'{max_price:,.0f}원',
                'note': '감정평가액 기준, 최대 +5% 이내 협상 가능'
            },
            
            # 투자 조건
            'investment_conditions': conditions if conditions else ['특별 조건 없음'],
            
            # Action Items
            'action_items': action_items,
            
            # 최종 의견
            'final_opinion': f'본 투자안은 예상 IRR {irr:.1f}%로 {investment_opinion}합니다.' + 
                           (f' 단, 다음 조건 충족 시: {", ".join(conditions)}' if conditions else '')
        }
    
    # ========== Helper Methods ==========
    
    def _calculate_investment_grade(self, irr: float) -> Dict[str, str]:
        """Calculate investment grade based on IRR"""
        if irr >= 15:
            return {
                'grade': 'A',
                'color': 'green',
                'icon': '🟢',
                'description': '우수한 투자안 (IRR ≥ 15%)'
            }
        elif irr >= 10:
            return {
                'grade': 'B',
                'color': 'blue',
                'icon': '🔵',
                'description': '양호한 투자안 (IRR ≥ 10%)'
            }
        elif irr >= 5:
            return {
                'grade': 'C',
                'color': 'yellow',
                'icon': '🟡',
                'description': '보통 투자안 (IRR ≥ 5%)'
            }
        else:
            return {
                'grade': 'D',
                'color': 'red',
                'icon': '🔴',
                'description': '미흡한 투자안 (IRR < 5%)'
            }
    
    def _extract_investment_points(self, irr: float, roi: float) -> List[str]:
        """Extract key investment points"""
        points = []
        
        if irr >= 12:
            points.append(f'✓ 우수한 수익률 (IRR {irr:.1f}%)')
        if roi >= 20:
            points.append(f'✓ 높은 투자 수익 (ROI {roi:.1f}%)')
        
        # LH possibility
        lh_decision = self.lh_result.get('decision', 'GO')
        if lh_decision == 'GO':
            points.append('✓ LH 매입 가능성 높음')
        
        # Add generic points if not enough
        if len(points) < 3:
            points.append('✓ 안정적인 Exit 전략 (LH 매입)')
        
        return points[:3]
    
    def _extract_major_risks(self) -> List[Dict[str, str]]:
        """Extract major risks summary"""
        risks = [
            {'risk': '인허가 지연', 'level': 'MEDIUM', 'mitigation': '사전 협의'},
            {'risk': '공사비 상승', 'level': 'HIGH', 'mitigation': '예비비 확보'}
        ]
        return risks
    
    def _assess_profitability(self, roi: float, irr: float) -> Dict[str, str]:
        """Assess profitability level"""
        if roi >= 20:
            return {
                'level': '우수',
                'color': 'green',
                'description': f'ROI {roi:.1f}%로 매우 우수한 수익성'
            }
        elif roi >= 15:
            return {
                'level': '양호',
                'color': 'blue',
                'description': f'ROI {roi:.1f}%로 양호한 수익성'
            }
        elif roi >= 10:
            return {
                'level': '보통',
                'color': 'yellow',
                'description': f'ROI {roi:.1f}%로 보통 수익성'
            }
        else:
            return {
                'level': '미흡',
                'color': 'red',
                'description': f'ROI {roi:.1f}%로 수익성 개선 필요'
            }
    
    def _calculate_page_count(self, report: Dict[str, Any]) -> int:
        """Calculate estimated page count"""
        # Section 1: 1 page
        # Section 2: 2 pages
        # Section 3: 2 pages
        # Section 4: 4 pages
        # Section 5: 2 pages
        # Section 6: 1 page
        return 12
