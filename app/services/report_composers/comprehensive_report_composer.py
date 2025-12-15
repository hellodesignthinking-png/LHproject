"""
ZeroSite Comprehensive Report Composer v3.3 (15-20 pages)

목적:
- 정식계약 후 제공하는 핵심 컨설팅 상품
- LH Decision Report + Investor Report + Risk Matrix 통합
- 토지주/투자자 맞춤형 강조 가능

구조 (7개 섹션):
- Section 1: Executive Summary (1장)
- Section 2: 토지 개요 (2장)
- Section 3: LH 사업 적합성 분석 (4장) ← LH Decision 통합
- Section 4: 개발 타당성 분석 (3장)
- Section 5: 수익성 분석 (3장) ← Investor 핵심 통합
- Section 6: 리스크 매트릭스 (2장)
- Section 7: 결론 및 권고사항 (1장)
- Appendix: 부록
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class ComprehensiveReportComposer:
    """
    v3.3 Comprehensive Report - 정식계약 후 종합보고서
    Target: 토지주/투자자 (15-20 pages)
    
    Integrates: LH Decision + Investor Analysis + Risk Matrix
    """
    
    def __init__(
        self,
        appraisal_ctx,
        land_diagnosis: Dict[str, Any],
        lh_result: Dict[str, Any],
        ch3_scores: Optional[Dict[str, Any]] = None,
        ch4_scores: Optional[Dict[str, Any]] = None,
        risk_matrix: Optional[Dict[str, Any]] = None,
        financial_analysis: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Comprehensive Report Composer
        
        Args:
            appraisal_ctx: Locked appraisal context (READ-ONLY)
            land_diagnosis: Land diagnosis results
            lh_result: LH analysis results
            ch3_scores: CH3 feasibility scores (optional)
            ch4_scores: CH4 demand scores (optional)
            risk_matrix: Risk matrix analysis (optional)
            financial_analysis: Financial engine results (optional)
        """
        self.appraisal_ctx = appraisal_ctx
        self.land_diagnosis = land_diagnosis
        self.lh_result = lh_result
        self.ch3_scores = ch3_scores or {}
        self.ch4_scores = ch4_scores or {}
        self.risk_matrix = risk_matrix or {}
        self.financial_analysis = financial_analysis or {}
        
        self.report_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.generation_time = datetime.now().isoformat()
        self.version = "v3.3"
    
    def compose(self, target_audience: str = "landowner") -> Dict[str, Any]:
        """
        Generate complete Comprehensive Report (15-20 pages)
        
        Args:
            target_audience: "landowner" (LH 강조) or "investor" (수익성 강조)
        
        Returns:
            Dictionary with all 7 sections + appendix
        """
        
        print(f"\n📄 Generating Comprehensive Report v3.3 (15-20 pages)")
        print(f"   Report ID: {self.report_id}")
        print(f"   Target Audience: {target_audience}")
        
        report = {
            'report_id': self.report_id,
            'report_type': 'comprehensive_report',
            'version': self.version,
            'generation_time': self.generation_time,
            'target_audience': target_audience,
            'estimated_pages': '15-20',
            
            'section_1_executive_summary': self._compose_executive_summary(),
            'section_2_land_overview': self._compose_land_overview(),
            'section_3_lh_analysis': self._compose_lh_analysis(),
            'section_4_development_feasibility': self._compose_development(),
            'section_5_financial_analysis': self._compose_financial(),
            'section_6_risk_matrix': self._compose_risk_matrix(),
            'section_7_conclusion': self._compose_conclusion(),
            'appendix': self._compose_appendix()
        }
        
        # Calculate actual page count
        page_count = self._calculate_page_count(report)
        report['actual_pages'] = page_count
        
        print(f"✅ Comprehensive Report generation complete")
        print(f"   Total Pages: {page_count}")
        print(f"   Final Judgment: {report['section_7_conclusion']['final_judgment'][:80]}...")
        
        return report
    
    def _compose_executive_summary(self) -> Dict[str, Any]:
        """
        Section 1: Executive Summary (1장)
        
        포함 내용:
        - 핵심 결론 1문장
        - 주요 지표 대시보드 (LH 가능성, 예상 세대수, IRR, 총 리스크 점수)
        - 권고사항 bullet 3개
        """
        
        # 핵심 지표 추출
        lh_possibility = self._calculate_lh_possibility()
        estimated_units = self._calculate_estimated_units()
        irr = self.financial_analysis.get('irr', self.lh_result.get('roi', 0))
        total_risk_score = self._calculate_total_risk_score()
        
        # 핵심 결론 생성
        key_conclusion = self._generate_key_conclusion(lh_possibility, irr)
        
        # 권고사항 생성
        recommendations = self._generate_top_recommendations()
        
        return {
            'title': 'Executive Summary',
            'page_number': 1,
            
            # 핵심 결론 1문장
            'key_conclusion': key_conclusion,
            
            # 주요 지표 대시보드
            'key_metrics_dashboard': {
                'lh_possibility': {
                    'label': 'LH 가능성',
                    'value': lh_possibility,
                    'color': self._get_possibility_color(lh_possibility),
                    'icon': self._get_possibility_icon(lh_possibility)
                },
                'estimated_units': {
                    'label': '예상 세대수',
                    'value': estimated_units,
                    'unit': '세대'
                },
                'irr': {
                    'label': 'IRR',
                    'value': round(irr, 2),
                    'unit': '%',
                    'color': 'green' if irr >= 15 else 'yellow' if irr >= 10 else 'red'
                },
                'total_risk_score': {
                    'label': '총 리스크 점수',
                    'value': total_risk_score,
                    'max': 100,
                    'level': '낮음' if total_risk_score <= 30 else '보통' if total_risk_score <= 60 else '높음'
                }
            },
            
            # 권고사항 bullet 3개
            'recommendations': recommendations
        }
    
    def _compose_land_overview(self) -> Dict[str, Any]:
        """
        Section 2: 토지 개요 (2장)
        
        포함 내용:
        - 위치 및 기본 정보 (주소, 면적, 지목, 용도지역)
        - 공법 규제 현황 (건폐율, 용적률, 높이제한, 일조권 등)
        - 감정평가 요약 (공시지가, 감정가, 최근 실거래가)
        - 위치도/지적도 (시각화)
        
        데이터 소스: appraisal_context (FACT Layer - 수정 불가)
        """
        
        # 기본 정보 추출 (FACT Layer - READ ONLY)
        address = self.land_diagnosis.get('address', 'N/A')
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm', 0)
        zone_type = self.appraisal_ctx.get('zoning.confirmed_type', 'N/A')
        far = self.appraisal_ctx.get('zoning.floor_area_ratio', 0)
        bcr = self.appraisal_ctx.get('zoning.building_coverage_ratio', 0)
        
        # 감정평가 정보
        official_price = self.appraisal_ctx.get('official_land_price.standard_price_per_sqm', 0)
        final_appraised = self.appraisal_ctx.get('calculation.final_appraised_total', 0)
        premium_rate = self.appraisal_ctx.get('premium.total_premium_rate', 0)
        
        return {
            'title': '토지 개요',
            'page_numbers': '2-3',
            
            # Part 1: 위치 및 기본 정보
            'location_and_basic_info': {
                'address': address,
                'land_area_sqm': land_area,
                'land_area_pyeong': round(land_area / 3.3058, 1),
                'land_category': '대지',  # 실제로는 지목 정보 필요
                'zone_type': zone_type,
                'zone_type_description': f'{zone_type} - LH 공공주택 개발 {"적합" if "주거" in zone_type else "검토 필요"}'
            },
            
            # Part 2: 공법 규제 현황
            'regulations': {
                'building_coverage_ratio': {
                    'value': bcr,
                    'unit': '%',
                    'description': '건축 가능한 대지면적의 비율'
                },
                'floor_area_ratio': {
                    'value': far,
                    'unit': '%',
                    'description': '건축 가능한 연면적의 비율'
                },
                'height_limit': {
                    'value': '없음',  # 실제로는 regulations에서 가져와야 함
                    'note': '일조권 및 경관 규제 확인 필요'
                },
                'other_restrictions': [
                    '지구단위계획구역 여부 확인 필요',
                    '문화재 보호구역 확인 필요',
                    '도로 접면 조건 확인 필요'
                ]
            },
            
            # Part 3: 감정평가 요약
            'appraisal_summary': {
                'official_land_price': {
                    'price_per_sqm': official_price,
                    'total': official_price * land_area,
                    'reference_year': self.appraisal_ctx.get('official_land_price.reference_year', 2024),
                    'note': '국토교통부 표준지공시지가 기준'
                },
                'appraised_value': {
                    'price_per_sqm': round(final_appraised / land_area, 0) if land_area > 0 else 0,
                    'total': final_appraised,
                    'premium_rate': premium_rate * 100,
                    'note': f'프리미엄 {premium_rate * 100:.1f}% 적용 (개발 잠재력, 입지, 정책 혜택)'
                },
                'recent_transactions': {
                    'available': len(self.appraisal_ctx.get('transaction_cases', [])) > 0,
                    'note': '최근 거래사례 참고 (시점 보정 및 위치 보정 반영)'
                }
            },
            
            # Part 4: 위치도/지적도 (시각화)
            'visualization': {
                'location_map': {
                    'latitude': 37.5665,  # 실제로는 분석 데이터에서
                    'longitude': 126.9780,
                    'zoom': 15,
                    'note': 'Kakao Map API 기반'
                },
                'cadastral_map': {
                    'available': False,
                    'note': '지적도는 추가 요청 시 제공 가능'
                }
            }
        }
    
    def _compose_lh_analysis(self) -> Dict[str, Any]:
        """
        Section 3: LH 사업 적합성 분석 (4장)
        
        ← 기존 LH Decision Report 통합
        
        Part 3-1: Pass/Fail 예측 및 확률
        Part 3-2: 공급유형 적정성 (CH4 분석)
        Part 3-3: LH 매입가 적정성 판단
        Part 3-4: 감점 요인 및 대응 방안
        
        데이터 소스: lh_judgment, ch4_scoring (JUDGMENT Layer)
        """
        
        # Import LH Decision Report logic
        from app.services.report_composers.lh_decision_report_composer import LHDecisionReportComposer
        
        # Create LH Decision composer
        lh_composer = LHDecisionReportComposer(
            self.appraisal_ctx,
            self.lh_result,
            self.ch3_scores,
            self.ch4_scores
        )
        
        # Get data from LH Decision Report (integrate)
        lh_decision_data = {
            'part_1': lh_composer._generate_supply_type_analysis(),
            'part_2': lh_composer._generate_purchase_price_analysis(),
            'part_3': lh_composer._generate_pass_fail_prediction(),
            'part_4': lh_composer._generate_improvement_strategies()
        }
        
        return {
            'title': 'LH 사업 적합성 분석',
            'page_numbers': '4-7',
            
            # Part 3-1: Pass/Fail 예측 및 확률
            'part_1_pass_fail_prediction': {
                'prediction': lh_decision_data['part_3']['prediction'],
                'prediction_icon': lh_decision_data['part_3']['prediction_icon'],
                'prediction_text': lh_decision_data['part_3']['prediction_text'],
                'pass_probability': lh_decision_data['part_3']['confidence_percentage'] / 100,
                'confidence_factors': lh_decision_data['part_3']['pass_factors'],
                'deduction_factors': lh_decision_data['part_3']['fail_risks'],
                'overall_score': lh_decision_data['part_3']['overall_score']
            },
            
            # Part 3-2: 공급유형 적정성 (CH4 분석)
            'part_2_supply_type_analysis': {
                'ch4_scores': self.ch4_scores.get('type_scores', {}),
                'recommended_type': lh_decision_data['part_1']['recommended_type'],
                'demand_score': lh_decision_data['part_1']['normalized_score'],
                'suitability': lh_decision_data['part_1']['suitability'],
                'suitability_text': lh_decision_data['part_1']['suitability_text'],
                'alternative_types': lh_decision_data['part_1']['alternative_types'],
                'regional_analysis': lh_decision_data['part_1']['analysis']
            },
            
            # Part 3-3: LH 매입가 적정성 판단
            'part_3_purchase_price_adequacy': {
                'verified_cost_breakdown': {
                    'land_appraisal': lh_decision_data['part_2']['land_appraisal'],
                    'construction_cost': lh_decision_data['part_2']['construction_cost'],
                    'verified_cost': lh_decision_data['part_2']['verified_cost'],
                    'total_cost': lh_decision_data['part_2']['total_cost']
                },
                'lh_purchase_price': lh_decision_data['part_2']['lh_purchase_price'],
                'price_ratio': lh_decision_data['part_2']['price_ratio'],
                'adequacy': lh_decision_data['part_2']['adequacy'],
                'adequacy_text': lh_decision_data['part_2']['adequacy_text'],
                'adequacy_formula': f"adequacy = |lh_purchase_price - total_cost| / total_cost",
                'adequacy_note': lh_decision_data['part_2']['note']
            },
            
            # Part 3-4: 감점 요인 및 대응 방안
            'part_4_improvement_strategies': {
                'deduction_factors': lh_decision_data['part_3']['deduction_factors'],
                'improvement_strategies': lh_decision_data['part_4']['improvement_strategies'],
                'priority_actions': lh_decision_data['part_4']['priority_actions'],
                'estimated_timeline': lh_decision_data['part_4']['estimated_timeline'],
                'alternative_scenarios': lh_decision_data['part_4']['alternative_scenarios']
            }
        }
    
    def _compose_development(self) -> Dict[str, Any]:
        """
        Section 4: 개발 타당성 분석 (3장)
        
        포함 내용:
        - 건축 개요 (예상 연면적, 예상 층수, 예상 세대수)
        - 주차장 분석 (필요 대수 vs 확보 가능 대수)
        - 인허가 리스크 (예상 인허가 기간, 주요 허가 항목 체크리스트)
        
        데이터 소스: land_diagnosis (INTERPRETATION Layer)
        """
        
        # 기본 정보
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm', 0)
        far = self.appraisal_ctx.get('zoning.floor_area_ratio', 0)
        bcr = self.appraisal_ctx.get('zoning.building_coverage_ratio', 0)
        
        # 건축 개요 계산
        total_buildable_area = land_area * (far / 100) if far > 0 else 0
        estimated_floors = int(far / bcr) if bcr > 0 else 0
        min_units = int(total_buildable_area / 80) if total_buildable_area > 0 else 0
        max_units = int(total_buildable_area / 60) if total_buildable_area > 0 else 0
        
        # 주차장 분석
        estimated_units = int((min_units + max_units) / 2)
        required_parking = int(estimated_units * 1.0)  # 세대당 1.0대
        
        return {
            'title': '개발 타당성 분석',
            'page_numbers': '8-10',
            
            # Part 1: 건축 개요
            'architectural_overview': {
                'buildable_area': {
                    'total_sqm': round(total_buildable_area, 1),
                    'total_pyeong': round(total_buildable_area / 3.3058, 1),
                    'calculation': f'{land_area}㎡ × {far}% = {round(total_buildable_area, 1)}㎡'
                },
                'estimated_floors': {
                    'value': estimated_floors,
                    'calculation': f'FAR {far}% ÷ BCR {bcr}% = 약 {estimated_floors}층',
                    'note': '실제 높이제한 확인 필요'
                },
                'estimated_units': {
                    'min': min_units,
                    'max': max_units,
                    'average': estimated_units,
                    'calculation': f'연면적 {round(total_buildable_area, 1)}㎡ ÷ 전용면적 60~80㎡'
                }
            },
            
            # Part 2: 주차장 분석
            'parking_analysis': {
                'required_spaces': {
                    'value': required_parking,
                    'standard': '세대당 1.0대 (지역별 상이)',
                    'note': '실제 지자체 조례 확인 필요'
                },
                'available_spaces': {
                    'surface_parking': int(land_area * bcr / 100 / 25),  # 단순 추정
                    'mechanical_parking': 'TBD',
                    'note': '기계식 주차장 필요 여부 검토'
                },
                'shortage_alternative': [
                    '기계식 주차장 설치',
                    '인근 공영주차장 활용',
                    '탄력적 주차기준 적용 신청'
                ]
            },
            
            # Part 3: 인허가 리스크
            'permit_risk_analysis': {
                'estimated_timeline': {
                    'total_months': 12,
                    'breakdown': {
                        '사업계획 승인': '3개월',
                        '건축허가': '2개월',
                        '착공신고': '1개월',
                        '기타 인허가': '6개월'
                    }
                },
                'major_permits_checklist': [
                    {'item': '지구단위계획 적합 여부', 'status': 'CHECK', 'priority': 'HIGH'},
                    {'item': '건축심의 대상 여부', 'status': 'CHECK', 'priority': 'HIGH'},
                    {'item': '환경영향평가 대상 여부', 'status': 'CHECK', 'priority': 'MEDIUM'},
                    {'item': '교통영향평가 대상 여부', 'status': 'CHECK', 'priority': 'MEDIUM'},
                    {'item': '문화재 지표조사 필요 여부', 'status': 'CHECK', 'priority': 'LOW'}
                ],
                'risk_level': 'MEDIUM',
                'mitigation_strategies': [
                    '사전 협의를 통한 인허가 리스크 최소화',
                    '전문 인허가 대행사 활용',
                    '지자체 담당자와 긴밀한 협력'
                ]
            }
        }
    
    def _compose_financial(self) -> Dict[str, Any]:
        """
        Section 5: 수익성 분석 (3장)
        
        ← 기존 Investor Report 핵심 통합
        
        포함 내용:
        - 사업비 추정 (토지비, 건축비, 금융비용, 기타비용, 총 사업비)
        - 수익성 지표 (IRR, ROI, NPV, 투자금 회수 기간)
        - 시나리오 분석 (Best/Base/Worst)
        
        데이터 소스: financial_engine (JUDGMENT Layer)
        """
        
        # 기본 데이터
        land_appraisal = self.appraisal_ctx.get('calculation.final_appraised_total', 0)
        construction_cost = self.lh_result.get('construction_cost', 0)
        total_cost = self.lh_result.get('total_cost', 0)
        lh_purchase_price = self.lh_result.get('lh_purchase_price', 0)
        roi = self.lh_result.get('roi', 0)
        
        # Financial analysis (만약 제공되면 사용, 아니면 LH result 기반)
        irr = self.financial_analysis.get('irr', roi)
        npv = self.financial_analysis.get('npv', lh_purchase_price - total_cost)
        payback_months = self.financial_analysis.get('payback_months', 24)
        
        # 사업비 분해
        financial_cost = total_cost - land_appraisal - construction_cost
        other_cost = financial_cost
        
        return {
            'title': '수익성 분석',
            'page_numbers': '11-13',
            
            # Part 1: 사업비 추정
            'project_cost_estimation': {
                'land_cost': {
                    'value': land_appraisal,
                    'percentage': round((land_appraisal / total_cost * 100), 1) if total_cost > 0 else 0,
                    'note': '감정평가 확정 가격 (AppraisalContextLock)'
                },
                'construction_cost': {
                    'direct_cost': construction_cost,
                    'indirect_cost': int(construction_cost * 0.15),
                    'total': int(construction_cost * 1.15),
                    'percentage': round((construction_cost / total_cost * 100), 1) if total_cost > 0 else 0,
                    'note': 'LH 표준 건축비 기준'
                },
                'financial_cost': {
                    'value': financial_cost,
                    'interest_rate': 5.0,  # 가정
                    'percentage': round((financial_cost / total_cost * 100), 1) if total_cost > 0 else 0,
                    'note': '금융비용 (이자, 대출 수수료 등)'
                },
                'other_cost': {
                    'value': other_cost,
                    'percentage': round((other_cost / total_cost * 100), 1) if total_cost > 0 else 0,
                    'note': '기타비용 (설계비, 감리비, 분양비 등)'
                },
                'total_project_cost': {
                    'value': total_cost,
                    'formatted': f'{total_cost:,}원'
                }
            },
            
            # Part 2: 수익성 지표
            'profitability_metrics': {
                'irr': {
                    'label': 'IRR (Internal Rate of Return)',
                    'value': round(irr, 2),
                    'unit': '%',
                    'interpretation': '양호' if irr >= 15 else '보통' if irr >= 10 else '미흡',
                    'note': '내부수익률 - 사업의 수익성을 나타내는 지표'
                },
                'roi': {
                    'label': 'ROI (Return on Investment)',
                    'value': round(roi, 2),
                    'unit': '%',
                    'calculation': f'(LH 매입가 - 총 사업비) / 총 사업비 × 100',
                    'interpretation': '우수' if roi >= 20 else '양호' if roi >= 15 else '보통',
                    'note': '투자 대비 수익률'
                },
                'npv': {
                    'label': 'NPV (Net Present Value)',
                    'value': npv,
                    'unit': '원',
                    'interpretation': '양호' if npv > 0 else '검토 필요',
                    'note': '순현재가치 - 미래 현금흐름의 현재가치'
                },
                'payback_period': {
                    'label': '투자금 회수 기간',
                    'value': payback_months,
                    'unit': '개월',
                    'interpretation': '양호' if payback_months <= 24 else '보통' if payback_months <= 36 else '장기',
                    'note': 'LH 매입 후 자금 회수까지 예상 기간'
                }
            },
            
            # Part 3: 시나리오 분석
            'scenario_analysis': {
                'best_case': {
                    'name': 'Best Case',
                    'conditions': '공사비 -5%, 매입가 +5%',
                    'irr': round(irr * 1.25, 2),
                    'roi': round(roi * 1.25, 2),
                    'npv': int(npv * 1.3),
                    'probability': '20%'
                },
                'base_case': {
                    'name': 'Base Case',
                    'conditions': '현재 추정 기준',
                    'irr': round(irr, 2),
                    'roi': round(roi, 2),
                    'npv': npv,
                    'probability': '60%'
                },
                'worst_case': {
                    'name': 'Worst Case',
                    'conditions': '공사비 +10%, 매입가 -5%',
                    'irr': round(irr * 0.6, 2),
                    'roi': round(roi * 0.6, 2),
                    'npv': int(npv * 0.5),
                    'probability': '20%'
                }
            }
        }
    
    def _compose_risk_matrix(self) -> Dict[str, Any]:
        """
        Section 6: 리스크 매트릭스 (2장)
        
        포함 내용:
        - 리스크 항목별 평가 테이블 (카테고리, 리스크 항목, 레벨, 영향도, 대응 전략)
        - 리스크 히트맵 시각화 (발생확률 x 영향도)
        - 종합 리스크 점수
        
        데이터 소스: risk_matrix (INTERPRETATION Layer)
        """
        
        # 리스크 항목 정의 (기본값, risk_matrix가 제공되면 override)
        risk_items = self.risk_matrix.get('risk_items', self._generate_default_risk_items())
        
        # 리스크 평가
        total_risk_score = self._calculate_total_risk_score()
        
        return {
            'title': '리스크 매트릭스',
            'page_numbers': '14-15',
            
            # Part 1: 리스크 항목별 평가 테이블
            'risk_evaluation_table': risk_items,
            
            # Part 2: 리스크 히트맵 시각화
            'risk_heatmap': {
                'chart_type': 'heatmap',
                'dimensions': {
                    'x_axis': '발생 확률',
                    'y_axis': '영향도',
                    'levels': ['LOW', 'MEDIUM', 'HIGH']
                },
                'data_points': [
                    {
                        'risk_id': item['risk_id'],
                        'risk_name': item['risk_item'],
                        'probability': item['probability'],
                        'impact': item['impact'],
                        'position': f"({item['probability']}, {item['impact']})"
                    }
                    for item in risk_items
                ]
            },
            
            # Part 3: 종합 리스크 점수
            'total_risk_assessment': {
                'total_risk_score': total_risk_score,
                'max_score': 100,
                'risk_level': '낮음' if total_risk_score <= 30 else '보통' if total_risk_score <= 60 else '높음',
                'risk_level_color': 'green' if total_risk_score <= 30 else 'yellow' if total_risk_score <= 60 else 'red',
                'interpretation': self._interpret_risk_score(total_risk_score)
            }
        }
    
    def _compose_conclusion(self) -> Dict[str, Any]:
        """
        Section 7: 결론 및 권고사항 (1장)
        
        포함 내용:
        - 종합 판단 (사업 추진 권고 여부)
        - Action Items (즉시, 단기, 중기 조치사항)
        - 다음 단계 안내
        """
        
        # 종합 판단
        final_judgment = self._generate_final_judgment()
        
        # Action Items
        action_items = self._generate_action_items()
        
        return {
            'title': '결론 및 권고사항',
            'page_number': 16,
            
            # 종합 판단 (1문단)
            'final_judgment': final_judgment,
            
            # Action Items
            'action_items': {
                'immediate_actions': action_items['immediate'],
                'short_term_actions': action_items['short_term'],
                'mid_term_actions': action_items['mid_term']
            },
            
            # 다음 단계 안내
            'next_steps': {
                'step_1': '토지주와 최종 가격 협상',
                'step_2': 'LH 사업계획 승인 신청 준비',
                'step_3': '인허가 사전 협의',
                'step_4': '시공사 선정 및 계약',
                'expected_timeline': '6-12개월'
            }
        }
    
    def _compose_appendix(self) -> Dict[str, Any]:
        """
        Appendix: 부록
        
        포함 내용:
        - 데이터 출처
        - 계산 공식
        - 용어 정의
        - 법적 고지
        """
        
        return {
            'title': 'Appendix',
            
            'data_sources': [
                '국토교통부 표준지공시지가',
                '실거래가 공개시스템',
                'Kakao Map API',
                'LH 건설비 기준',
                'CH4 수요 분석 (ZeroSite 자체 모델)'
            ],
            
            'formulas': {
                'appraised_value': '감정가 = 기준 단가 × (1 + 프리미엄 비율) × 면적',
                'lh_purchase_price': 'LH 매입가 = 토지감정가 + Verified Cost',
                'roi': 'ROI = (LH 매입가 - 총 사업비) / 총 사업비 × 100',
                'irr': 'IRR = NPV가 0이 되는 할인율',
                'total_risk_score': '총 리스크 = Σ(발생확률 × 영향도 × 가중치)'
            },
            
            'terms': {
                'FACT': '감정평가 결과 - 수정 불가능한 확정 데이터',
                'INTERPRETATION': '토지진단 - 감정평가 참조 분석',
                'JUDGMENT': 'LH 판단 - 감정평가 기반 의사결정',
                'Verified Cost': 'LH 인정 건축비 + 간접비 + 금융비용',
                'CH4 Scoring': '공급유형별 지역 수요 분석 모델'
            },
            
            'legal_disclaimer': (
                '본 보고서는 ZeroSite v3.3 분석 엔진을 기반으로 작성되었으며, '
                '참고용으로만 사용되어야 합니다. 실제 사업 추진 시에는 전문가의 '
                '상세한 검토가 필요하며, 본 보고서의 내용에 대한 법적 책임은 '
                '사용자에게 있습니다.'
            )
        }
    
    # ========== Helper Methods ==========
    
    def _calculate_lh_possibility(self) -> str:
        """LH 가능성 계산"""
        decision = self.lh_result.get('decision', 'CONDITIONAL')
        roi = self.lh_result.get('roi', 0)
        
        if decision == 'GO' and roi >= 20:
            return 'HIGH'
        elif decision == 'GO' or (decision == 'CONDITIONAL' and roi >= 15):
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _calculate_estimated_units(self) -> int:
        """예상 세대수 계산"""
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm', 0)
        far = self.appraisal_ctx.get('zoning.floor_area_ratio', 0)
        total_buildable = land_area * (far / 100) if far > 0 else 0
        return int(total_buildable / 70) if total_buildable > 0 else 0  # 평균 70㎡
    
    def _calculate_total_risk_score(self) -> int:
        """총 리스크 점수 계산 (0-100)"""
        if self.risk_matrix and 'total_risk_score' in self.risk_matrix:
            return self.risk_matrix['total_risk_score']
        
        # 기본 계산
        roi = self.lh_result.get('roi', 0)
        far = self.appraisal_ctx.get('zoning.floor_area_ratio', 0)
        
        risk_score = 50  # 기본값
        
        # ROI 기반 리스크
        if roi >= 20:
            risk_score -= 15
        elif roi >= 15:
            risk_score -= 10
        elif roi < 10:
            risk_score += 20
        
        # FAR 기반 리스크
        if far >= 250:
            risk_score -= 10
        elif far < 200:
            risk_score += 15
        
        return max(0, min(100, risk_score))
    
    def _generate_key_conclusion(self, lh_possibility: str, irr: float) -> str:
        """핵심 결론 생성"""
        if lh_possibility == 'HIGH' and irr >= 15:
            return f"본 토지는 LH 신축매입임대 사업에 매우 적합하며, 예상 IRR {irr:.1f}%로 우수한 수익성이 예상됩니다."
        elif lh_possibility == 'MEDIUM':
            return f"본 토지는 LH 신축매입임대 사업 진행이 가능하며, 예상 IRR {irr:.1f}%입니다. 일부 개선이 필요합니다."
        else:
            return f"본 토지는 현재 조건으로 LH 사업 진행이 어려우며, 대대적 개선이 필요합니다 (예상 IRR {irr:.1f}%)."
    
    def _generate_top_recommendations(self) -> List[str]:
        """주요 권고사항 생성 (3개)"""
        recommendations = []
        
        decision = self.lh_result.get('decision', 'CONDITIONAL')
        roi = self.lh_result.get('roi', 0)
        
        if decision == 'GO' and roi >= 20:
            recommendations.append('즉시 LH 사업계획 승인 신청 준비')
            recommendations.append('토지주와 최종 가격 협상 진행')
            recommendations.append('인허가 사전 협의 시작')
        elif decision == 'GO':
            recommendations.append('수익성 개선 방안 검토 후 진행')
            recommendations.append('LH 사업계획 승인 신청 준비')
            recommendations.append('리스크 완화 전략 수립')
        else:
            recommendations.append('토지 조건 개선 방안 재검토')
            recommendations.append('대안 사업 모델 검토')
            recommendations.append('전문가 추가 자문')
        
        return recommendations[:3]
    
    def _generate_default_risk_items(self) -> List[Dict[str, Any]]:
        """기본 리스크 항목 생성"""
        return [
            {
                'risk_id': 'R001',
                'category': '접근성',
                'risk_item': '도로 접근',
                'level': 'MEDIUM',
                'probability': 'MEDIUM',
                'impact': 'HIGH',
                'mitigation_strategy': '도로 확장 또는 우회로 확보'
            },
            {
                'risk_id': 'R002',
                'category': '규제',
                'risk_item': '인허가 지연',
                'level': 'MEDIUM',
                'probability': 'MEDIUM',
                'impact': 'MEDIUM',
                'mitigation_strategy': '사전 협의 및 전문가 활용'
            },
            {
                'risk_id': 'R003',
                'category': '시장',
                'risk_item': '수요 변동',
                'level': 'LOW',
                'probability': 'LOW',
                'impact': 'MEDIUM',
                'mitigation_strategy': 'CH4 분석 기반 수요 예측'
            },
            {
                'risk_id': 'R004',
                'category': '재무',
                'risk_item': '금리 상승',
                'level': 'MEDIUM',
                'probability': 'MEDIUM',
                'impact': 'HIGH',
                'mitigation_strategy': '금리 헷지 또는 조기 자금 조달'
            },
            {
                'risk_id': 'R005',
                'category': '공사',
                'risk_item': '공사비 증가',
                'level': 'MEDIUM',
                'probability': 'MEDIUM',
                'impact': 'HIGH',
                'mitigation_strategy': '고정가 계약 또는 예비비 확보'
            }
        ]
    
    def _interpret_risk_score(self, score: int) -> str:
        """리스크 점수 해석"""
        if score <= 30:
            return '전반적인 리스크가 낮은 편이며, 사업 추진에 큰 장애가 없을 것으로 예상됩니다.'
        elif score <= 60:
            return '일부 리스크가 존재하나 관리 가능한 수준입니다. 대응 전략 수립이 필요합니다.'
        else:
            return '높은 리스크가 존재합니다. 신중한 검토와 리스크 완화 방안이 필수적입니다.'
    
    def _generate_final_judgment(self) -> str:
        """최종 판단 생성"""
        decision = self.lh_result.get('decision', 'CONDITIONAL')
        roi = self.lh_result.get('roi', 0)
        lh_possibility = self._calculate_lh_possibility()
        
        if decision == 'GO' and roi >= 20:
            return (
                f"본 토지는 LH 신축매입임대 사업에 매우 적합한 조건을 갖추고 있습니다. "
                f"예상 ROI {roi:.1f}%로 우수한 수익성이 예상되며, LH 승인 가능성도 {lh_possibility} 수준입니다. "
                f"즉시 사업 추진을 권장합니다."
            )
        elif decision == 'GO':
            return (
                f"본 토지는 LH 신축매입임대 사업 진행이 가능합니다. "
                f"예상 ROI {roi:.1f}%로 양호한 수익성이 예상되나, 일부 개선이 필요합니다. "
                f"리스크 관리 후 사업 추진을 권장합니다."
            )
        elif decision == 'CONDITIONAL':
            return (
                f"본 토지는 조건부 진행이 가능합니다. "
                f"예상 ROI {roi:.1f}%로 보통 수준의 수익성이 예상됩니다. "
                f"주요 리스크 완화 후 재검토가 필요합니다."
            )
        else:
            return (
                f"현재 조건으로는 LH 사업 진행이 어렵습니다. "
                f"예상 ROI {roi:.1f}%로 수익성이 부족하며, 대대적 개선이 필요합니다. "
                f"대안 사업 모델을 검토하시기 바랍니다."
            )
    
    def _generate_action_items(self) -> Dict[str, List[str]]:
        """Action Items 생성"""
        decision = self.lh_result.get('decision', 'CONDITIONAL')
        
        if decision == 'GO':
            return {
                'immediate': [
                    '토지주와 최종 가격 협상',
                    'LH 사업계획 승인 신청 서류 준비'
                ],
                'short_term': [
                    '인허가 사전 협의 (지자체)',
                    '시공사 후보 선정 및 견적 요청',
                    '금융기관 대출 사전 상담'
                ],
                'mid_term': [
                    'LH 사업계획 승인 신청',
                    '건축허가 신청 준비',
                    '시공사 최종 선정 및 계약'
                ]
            }
        elif decision == 'CONDITIONAL':
            return {
                'immediate': [
                    '주요 리스크 완화 방안 수립',
                    '전문가 자문 (인허가, 재무)'
                ],
                'short_term': [
                    '토지 조건 개선 (용도지역 변경 등)',
                    '재무 모델 재검토',
                    'LH 사전 협의'
                ],
                'mid_term': [
                    '개선 후 재평가',
                    'LH 사업계획 승인 신청 준비',
                    '대안 시나리오 검토'
                ]
            }
        else:
            return {
                'immediate': [
                    '대안 사업 모델 검토',
                    '전문가 종합 자문'
                ],
                'short_term': [
                    '토지 재평가',
                    '다른 개발 방식 검토 (민간 분양 등)',
                    '매각 옵션 검토'
                ],
                'mid_term': [
                    '최종 의사결정',
                    '선택한 대안 실행'
                ]
            }
    
    def _calculate_page_count(self, report: Dict[str, Any]) -> int:
        """보고서 페이지 수 계산"""
        # Section별 예상 페이지
        section_pages = {
            'section_1': 1,
            'section_2': 2,
            'section_3': 4,
            'section_4': 3,
            'section_5': 3,
            'section_6': 2,
            'section_7': 1,
            'appendix': 1
        }
        return sum(section_pages.values())  # 17 pages
    
    def _get_possibility_color(self, possibility: str) -> str:
        """LH 가능성 색상"""
        return {
            'HIGH': 'green',
            'MEDIUM': 'yellow',
            'LOW': 'red'
        }.get(possibility, 'gray')
    
    def _get_possibility_icon(self, possibility: str) -> str:
        """LH 가능성 아이콘"""
        return {
            'HIGH': '🟢',
            'MEDIUM': '🟡',
            'LOW': '🔴'
        }.get(possibility, '⚪')


def create_comprehensive_report_composer(
    appraisal_ctx,
    land_diagnosis: Dict[str, Any],
    lh_result: Dict[str, Any],
    ch3_scores: Optional[Dict[str, Any]] = None,
    ch4_scores: Optional[Dict[str, Any]] = None,
    risk_matrix: Optional[Dict[str, Any]] = None,
    financial_analysis: Optional[Dict[str, Any]] = None
) -> ComprehensiveReportComposer:
    """
    Factory function to create Comprehensive Report Composer v3.3
    
    v3.3 New Report Type:
    - 15-20 pages comprehensive report for contracted clients
    - Integrates LH Decision + Investor + Risk Matrix
    - Customizable for landowner or investor audience
    
    Args:
        appraisal_ctx: Locked appraisal context (READ-ONLY)
        land_diagnosis: Land diagnosis results
        lh_result: LH analysis results
        ch3_scores: CH3 feasibility scores (optional)
        ch4_scores: CH4 demand scores (optional)
        risk_matrix: Risk matrix analysis (optional)
        financial_analysis: Financial engine results (optional)
    
    Returns:
        ComprehensiveReportComposer v3.3 instance
    """
    return ComprehensiveReportComposer(
        appraisal_ctx,
        land_diagnosis,
        lh_result,
        ch3_scores,
        ch4_scores,
        risk_matrix,
        financial_analysis
    )


__all__ = [
    'ComprehensiveReportComposer',
    'create_comprehensive_report_composer'
]
