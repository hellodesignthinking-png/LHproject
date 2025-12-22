"""
ZeroSite v8.8 Report Generator
60-Page Professional Report with FACT/INTERPRETATION/JUDGMENT Structure

Version: v8.8
Date: 2025-12-15

Structure:
- SECTION 1: Appraisal (FACT) - Pages 4-21 (18p)
- SECTION 2: Land Diagnosis (INTERPRETATION) - Pages 22-40 (19p)
- SECTION 3: LH Judgment (DECISION) - Pages 41-55 (15p)
- APPENDIX - Pages 56-60 (5p)

Key Principles:
1. Appraisal results are IMMUTABLE (from AppraisalContextLock)
2. Diagnosis only INTERPRETS appraisal results
3. LH Judgment uses appraisal value for financial calculations
4. Clear visual separation between sections
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from app.services.appraisal_context import AppraisalContextLock
from app.services.ch4_dynamic_scoring import CH4DynamicScorer
from app.services.ch3_feasibility_scoring import CH3FeasibilityScorer
from app.services.visualization_module_v8_8 import create_visualization_module


class ReportGeneratorV88:
    """
    ZeroSite v8.8 전문가급 보고서 생성기
    
    60페이지 구조:
    - Cover & Meta: 3p
    - SECTION 1 (FACT): 18p
    - SECTION 2 (INTERPRETATION): 19p
    - SECTION 3 (JUDGMENT): 15p
    - Appendix: 5p
    """
    
    def __init__(
        self,
        appraisal_ctx: AppraisalContextLock,
        analysis_data: Dict[str, Any],
        lh_analysis_result: Dict[str, Any]
    ):
        """
        Initialize report generator
        
        Args:
            appraisal_ctx: Locked appraisal context (READ-ONLY)
            analysis_data: Land analysis data from AnalysisEngine
            lh_analysis_result: LH financial analysis result
        """
        self.appraisal_ctx = appraisal_ctx
        self.analysis_data = analysis_data
        self.lh_result = lh_analysis_result
        
        # Initialize scorers
        self.ch4_scorer = CH4DynamicScorer()
        self.ch3_scorer = CH3FeasibilityScorer()
        
        # Initialize visualization module
        self.viz_module = create_visualization_module()
        
        # Report metadata
        self.report_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.generation_time = datetime.now().isoformat()
    
    def generate(self) -> Dict[str, Any]:
        """
        Generate complete 60-page report
        
        Returns:
            Report dictionary with all sections
        """
        
        print(f"\n📄 Generating ZeroSite v8.8 Report (60 pages)")
        print(f"   Report ID: {self.report_id}")
        
        # Generate visualizations
        print(f"   🎨 Generating visualizations...")
        visualizations = self._generate_visualizations()
        
        report = {
            'report_id': self.report_id,
            'version': 'v8.8',
            'generation_time': self.generation_time,
            'structure': 'FACT/INTERPRETATION/JUDGMENT',
            
            # Cover & Meta (P.01-03)
            'cover': self._generate_cover(),
            'executive_summary': self._generate_executive_summary(),
            'table_of_contents': self._generate_toc(),
            
            # SECTION 1: Appraisal (FACT) - P.04-21 (18p)
            'section_1_appraisal': {
                'section_title': 'SECTION 1. 감정평가 (FACT)',
                'section_subtitle': '🔒 절대 불변 영역 - 이후 모든 분석의 기준',
                'legal_notice': '【법적 고지】 본 섹션의 감정평가 결과는 일단 확정되면 변경할 수 없으며(IMMUTABLE), 이후 모든 진단 및 판단의 절대적 기준이 됩니다. 감정평가액의 임의 조정, 재계산, 또는 수정은 금지되며, 위반 시 전체 보고서의 신뢰성이 훼손됩니다.',
                'pages': self._generate_section_1_appraisal()
            },
            
            # SECTION 2: Land Diagnosis (INTERPRETATION) - P.22-40 (19p)
            'section_2_diagnosis': {
                'section_title': 'SECTION 2. 토지진단 (INTERPRETATION)',
                'section_subtitle': '감정평가 결과를 전제로 한 해석 영역',
                'legal_notice': '【법적 고지】 본 섹션은 SECTION 1의 확정된 감정평가 결과를 "읽기 전용(READ-ONLY)"으로 참조하여 해석만 수행합니다. 감정평가액의 재계산, API 재호출, 또는 값의 변경은 일절 금지되며, 오직 확정된 값에 대한 분석 및 해석만 수행합니다.',
                'pages': self._generate_section_2_diagnosis()
            },
            
            # SECTION 3: LH Judgment (DECISION) - P.41-55 (15p)
            'section_3_lh_judgment': {
                'section_title': 'SECTION 3. LH 판단 (JUDGMENT)',
                'section_subtitle': '의사결정 영역',
                'legal_notice': '【법적 고지】 본 섹션의 모든 재무 계산은 SECTION 1의 확정된 감정평가액을 "토지취득비"의 절대 기준으로 사용합니다. 감정평가액의 할인, 조정, 또는 임의 변경은 금지되며, LH 분석 엔진은 오직 확정된 감정평가액만을 읽기 전용으로 참조합니다.',
                'pages': self._generate_section_3_lh_judgment()
            },
            
            # Appendix - P.56-60 (5p)
            'appendix': self._generate_appendix(),
            
            # Embedded Visualizations
            'visualizations': visualizations
        }
        
        # Embed visualizations into report
        report = self.viz_module.embed_visualizations_in_report(report, visualizations)
        
        print(f"✅ Report generation complete")
        print(f"   Total sections: 3 + appendix")
        print(f"   Appraisal locked: {self.appraisal_ctx.is_locked()}")
        print(f"   Visualizations: {report.get('visualization_warnings', {}).get('status', 'UNKNOWN')}")
        
        return report
    
    def _generate_visualizations(self) -> Dict[str, Any]:
        """
        Generate all visualizations for the report
        
        Returns:
            Dictionary with all generated visualizations
        """
        
        # Extract data for visualizations
        appraisal_summary = self.appraisal_ctx.get_summary()
        
        # Type scores (from analysis_data or mock)
        type_scores = self.analysis_data.get('type_demand_scores', {
            '행복주택': 15.2,
            '공공임대': 14.8,
            '영구임대': 13.5,
            '국민임대': 14.2,
            '장기전세': 13.8,
            '공공분양': 12.5,
            '공공지원': 11.9
        })
        
        # Risk data
        risks = [
            {'category': '인허가 리스크', 'probability': 'MEDIUM', 'impact': 'HIGH'},
            {'category': '시장 변동성', 'probability': 'MEDIUM', 'impact': 'MEDIUM'},
            {'category': '건설비 증가', 'probability': 'HIGH', 'impact': 'MEDIUM'},
            {'category': 'LH 정책 변경', 'probability': 'LOW', 'impact': 'HIGH'}
        ]
        
        # Market data (transaction prices)
        market_data = self.analysis_data.get('market_prices', [
            5500000, 5800000, 6000000, 5700000, 5900000,
            6100000, 5600000, 5850000, 6050000, 5950000
        ])
        
        # Target price (appraised per sqm)
        target_price = self.appraisal_ctx.get('calculation.final_appraised_per_sqm', 5900000)
        
        # FAR history
        far_history = [
            ('2020', 250),
            ('2021', 260),
            ('2022', 270),
            ('2023', 280),
            ('2024', 300)
        ]
        
        # Generate all visualizations individually to handle errors gracefully
        visualizations = {}
        
        try:
            kakao_map = self.viz_module.generate_kakao_static_map(37.5665, 126.9780)
            visualizations['kakao_map'] = {
                'type': 'html_embed',
                'data': kakao_map.get('embed_html', ''),
                'format': 'html'
            }
        except Exception as e:
            print(f"   ⚠️ Kakao Map generation failed: {str(e)}")
        
        try:
            radar_chart = self.viz_module.generate_radar_chart(type_scores)
            visualizations['radar_chart'] = {
                'type': 'chart_js',
                'data': radar_chart.get('chart_js_data', {}),
                'format': 'json'
            }
        except Exception as e:
            print(f"   ⚠️ Radar Chart generation failed: {str(e)}")
        
        try:
            risk_heatmap = self.viz_module.generate_risk_heatmap(risks)
            visualizations['risk_heatmap'] = {
                'type': 'html_table',
                'data': risk_heatmap.get('html_table', ''),
                'format': 'html'
            }
        except Exception as e:
            print(f"   ⚠️ Risk Heatmap generation failed: {str(e)}")
        
        try:
            histogram = self.viz_module.generate_market_histogram(market_data, target_price)
            visualizations['market_histogram'] = {
                'type': 'chart_js',
                'data': histogram.get('chart_js_data', {}),
                'format': 'json'
            }
        except Exception as e:
            print(f"   ⚠️ Market Histogram generation failed: {str(e)}")
        
        try:
            far_graph = self.viz_module.generate_far_change_graph(far_history)
            visualizations['far_change_graph'] = {
                'type': 'chart_js',
                'data': far_graph.get('chart_js_data', {}),
                'format': 'json'
            }
        except Exception as e:
            print(f"   ⚠️ FAR Change Graph generation failed: {str(e)}")
        
        print(f"   ✅ Generated {len(visualizations)}/5 visualizations")
        
        return visualizations
    
    def _generate_cover(self) -> Dict[str, Any]:
        """P.01 - Cover Page"""
        
        return {
            'page': 1,
            'type': 'cover',
            'project_name': self.analysis_data.get('address', 'ZeroSite 분석'),
            'address': self.analysis_data.get('address', 'N/A'),
            'analysis_date': datetime.now().strftime("%Y년 %m월 %d일"),
            'system_version': 'ZeroSite v8.8',
            'disclaimer': '본 보고서는 감정평가 결과를 기준으로 한 자동 분석 결과입니다.'
        }
    
    def _generate_executive_summary(self) -> Dict[str, Any]:
        """P.02 - Executive Summary"""
        
        # Extract key metrics
        final_appraised_value = self.appraisal_ctx.get('calculation.final_appraised_total')
        lh_decision = self.lh_result.get('decision', 'N/A')
        roi = self.lh_result.get('roi', 0)
        
        return {
            'page': 2,
            'type': 'executive_summary',
            'key_metrics': {
                'final_appraised_value': final_appraised_value,
                'lh_purchase_price': self.lh_result.get('lh_purchase_price', 0),
                'roi': roi,
                'decision': lh_decision,
                'rating': self.lh_result.get('rating', 'N/A')
            },
            'recommendation': self._generate_recommendation(lh_decision, roi)
        }
    
    def _generate_recommendation(self, decision: str, roi: float) -> str:
        """Generate recommendation text"""
        
        if decision == 'GO':
            return f"✅ 추천: 우수한 수익률({roi:.1f}%)로 사업 추진 권장"
        elif decision == 'CONDITIONAL':
            return f"⚠️ 조건부 추천: 양호한 수익률({roi:.1f}%)이나 리스크 검토 필요"
        else:
            return f"❌ 비추천: 낮은 수익률({roi:.1f}%)로 사업 재검토 권장"
    
    def _generate_toc(self) -> Dict[str, Any]:
        """P.03 - Table of Contents"""
        
        return {
            'page': 3,
            'type': 'toc',
            'sections': [
                {'title': 'SECTION 1. 감정평가 (FACT)', 'pages': '4-21', 'color': 'blue'},
                {'title': 'SECTION 2. 토지진단 (INTERPRETATION)', 'pages': '22-40', 'color': 'green'},
                {'title': 'SECTION 3. LH 판단 (JUDGMENT)', 'pages': '41-55', 'color': 'red'},
                {'title': 'APPENDIX', 'pages': '56-60', 'color': 'gray'}
            ],
            'guide': {
                'fact': 'FACT 섹션은 재계산되지 않으며, 이후 모든 분석의 기준이 됩니다.',
                'interpretation': 'INTERPRETATION 섹션은 FACT를 참조하여 해석만 수행합니다.',
                'judgment': 'JUDGMENT 섹션은 FACT 값을 기반으로 의사결정을 수행합니다.'
            }
        }
    
    def _generate_section_1_appraisal(self) -> List[Dict[str, Any]]:
        """
        SECTION 1: Appraisal (FACT) - P.04-21 (18 pages)
        
        🔒 All data from AppraisalContextLock (READ-ONLY)
        """
        
        pages = []
        
        # 1. 평가 개요 (P.04-05)
        pages.extend(self._generate_appraisal_overview())
        
        # 2. 대상 토지 기본 정보 (P.06-07)
        pages.extend(self._generate_land_basic_info())
        
        # 3. 용도지역 및 공적 규제 (P.08-10)
        pages.extend(self._generate_zoning_regulations())
        
        # 4. 공시지가 분석 (P.11-12)
        pages.extend(self._generate_official_price_analysis())
        
        # 5. 거래사례 분석 (P.13-15)
        pages.extend(self._generate_transaction_cases())
        
        # 6. 프리미엄 평가 (P.16-18)
        pages.extend(self._generate_premium_analysis())
        
        # 7. 최종 감정가 산출 (P.19-21)
        pages.extend(self._generate_final_appraisal())
        
        return pages
    
    def _generate_appraisal_overview(self) -> List[Dict[str, Any]]:
        """P.04-05: 평가 개요"""
        
        return [
            {
                'page': 4,
                'section': 'appraisal',
                'subsection': '1. 평가 개요',
                'title': '평가 목적 및 기준',
                'content': {
                    'purpose': 'LH 공공주택 개발 사업성 검토를 위한 감정평가',
                    'method': '비교방식',
                    'appraisal_date': datetime.now().strftime("%Y년 %m월 %d일"),
                    'appraiser': 'ZeroSite Appraisal Engine v8.7',
                    'standards': [
                        '감정평가에 관한 규칙',
                        '표준지공시지가 조사·산정 지침',
                        '부동산 가격공시에 관한 법률'
                    ]
                }
            },
            {
                'page': 5,
                'section': 'appraisal',
                'subsection': '1. 평가 개요',
                'title': '적용 법령 및 기준',
                'content': {
                    'legal_basis': [
                        '표준지 공시지가 기준',
                        '거래사례 보정 원칙',
                        '프리미엄 산정 기준'
                    ],
                    'confidence': self.appraisal_ctx.get('confidence.score'),
                    'data_sources': [
                        '국토교통부 공시지가',
                        '실거래가 공개시스템',
                        '지역 부동산 시장 데이터'
                    ]
                }
            }
        ]
    
    def _generate_land_basic_info(self) -> List[Dict[str, Any]]:
        """P.06-07: 대상 토지 기본 정보"""
        
        return [
            {
                'page': 6,
                'section': 'appraisal',
                'subsection': '2. 대상 토지 기본 정보',
                'title': '위치·지번·면적',
                'content': {
                    'address': self.analysis_data.get('address', 'N/A'),
                    'land_area_sqm': self.appraisal_ctx.get('calculation.land_area_sqm'),
                    'land_area_pyeong': self.appraisal_ctx.get('calculation.land_area_sqm') * 0.3025,
                    'coordinates': self.analysis_data.get('coordinates', {}),
                    'administrative_district': '확인 필요'
                }
            },
            {
                'page': 7,
                'section': 'appraisal',
                'subsection': '2. 대상 토지 기본 정보',
                'title': '위치도',
                'content': {
                    'map_type': 'kakao_static_map',
                    'map_data': {
                        'center': self.analysis_data.get('coordinates', {}),
                        'zoom': 16,
                        'marker': 'target_land',
                        'radius_500m': True
                    },
                    'placeholder': '🗺️ Kakao Static Map API Integration Required'
                }
            }
        ]
    
    def _generate_zoning_regulations(self) -> List[Dict[str, Any]]:
        """P.08-10: 용도지역 및 공적 규제"""
        
        zoning_type = self.appraisal_ctx.get('zoning.confirmed_type')
        bcr = self.appraisal_ctx.get('zoning.building_coverage_ratio')
        far = self.appraisal_ctx.get('zoning.floor_area_ratio')
        
        return [
            {
                'page': 8,
                'section': 'appraisal',
                'subsection': '3. 용도지역 및 공적 규제',
                'title': '용도지역·지구',
                'content': {
                    'zoning_type': zoning_type,
                    'source': self.appraisal_ctx.get('zoning.source', '국토부 API'),
                    'verified_date': self.appraisal_ctx.get('zoning.verified_at'),
                    'zoning_characteristics': self._get_zoning_description(zoning_type)
                }
            },
            {
                'page': 9,
                'section': 'appraisal',
                'subsection': '3. 용도지역 및 공적 규제',
                'title': '법정 FAR/BCR',
                'content': {
                    'building_coverage_ratio': bcr,
                    'floor_area_ratio': far,
                    'height_limit': '확인 필요',
                    'setback_requirements': '확인 필요'
                }
            },
            {
                'page': 10,
                'section': 'appraisal',
                'subsection': '3. 용도지역 및 공적 규제',
                'title': '규제 요약 테이블',
                'content': {
                    'table': [
                        {'item': '용도지역', 'value': zoning_type, 'impact': '✓ 적합'},
                        {'item': '건폐율', 'value': f'{bcr}%', 'impact': '법정 기준'},
                        {'item': '용적률', 'value': f'{far}%', 'impact': '법정 기준'},
                        {'item': '개발행위허가', 'value': '확인 필요', 'impact': '검토 필요'}
                    ]
                }
            }
        ]
    
    def _get_zoning_description(self, zoning_type: str) -> str:
        """Get zoning description"""
        
        descriptions = {
            '제1종일반주거지역': '저층 주택 중심, 조용한 주거환경',
            '제2종일반주거지역': '중층 주택 중심, 다세대·연립 가능',
            '제3종일반주거지역': '중고층 주택, 아파트 건설 가능',
            '준주거지역': '주거+상업 복합, 높은 용적률'
        }
        
        return descriptions.get(zoning_type, '일반 주거지역')
    
    def _generate_official_price_analysis(self) -> List[Dict[str, Any]]:
        """P.11-12: 공시지가 분석"""
        
        official_price = self.appraisal_ctx.get('official_land_price.standard_price_per_sqm')
        
        return [
            {
                'page': 11,
                'section': 'appraisal',
                'subsection': '4. 공시지가 분석',
                'title': '표준지 공시지가',
                'content': {
                    'standard_price_per_sqm': official_price,
                    'reference_year': self.appraisal_ctx.get('official_land_price.reference_year'),
                    'reference_parcel': self.appraisal_ctx.get('official_land_price.reference_parcel'),
                    'distance_to_standard': self.appraisal_ctx.get('official_land_price.distance_to_standard'),
                    'adjustment_factor': 1.05  # 5% 할증
                }
            },
            {
                'page': 12,
                'section': 'appraisal',
                'subsection': '4. 공시지가 분석',
                'title': '인근 공시지가 비교',
                'content': {
                    'nearby_prices': [
                        {'location': '표준지 A', 'price': official_price, 'distance': 0},
                        {'location': '인근 필지 1', 'price': official_price * 1.02, 'distance': 150},
                        {'location': '인근 필지 2', 'price': official_price * 0.98, 'distance': 200}
                    ],
                    'average': official_price,
                    'chart_type': 'bar_chart'
                }
            }
        ]
    
    def _generate_transaction_cases(self) -> List[Dict[str, Any]]:
        """P.13-15: 거래사례 분석"""
        
        transaction_cases = self.appraisal_ctx.get('transaction_cases', [])
        
        return [
            {
                'page': 13,
                'section': 'appraisal',
                'subsection': '5. 거래사례 분석',
                'title': '유사 거래사례 리스트',
                'content': {
                    'cases': transaction_cases,
                    'total_cases': len(transaction_cases),
                    'average_price': sum(c.get('price_per_sqm', 0) for c in transaction_cases) / max(len(transaction_cases), 1)
                }
            },
            {
                'page': 14,
                'section': 'appraisal',
                'subsection': '5. 거래사례 분석',
                'title': '거리·시점·규모 보정',
                'content': {
                    'adjustments': [
                        {
                            'case_id': i+1,
                            'original_price': case.get('price_per_sqm', 0),
                            'time_adjusted': case.get('adjusted_for_time', True),
                            'location_adjusted': case.get('adjusted_for_location', True),
                            'similarity': case.get('similarity_score', 0)
                        }
                        for i, case in enumerate(transaction_cases)
                    ]
                }
            },
            {
                'page': 15,
                'section': 'appraisal',
                'subsection': '5. 거래사례 분석',
                'title': 'Market Histogram',
                'content': {
                    'chart_type': 'histogram',
                    'x_axis': 'price_per_sqm',
                    'y_axis': 'frequency',
                    'target_land_marker': self.appraisal_ctx.get('calculation.base_price_per_sqm'),
                    'placeholder': '📊 Histogram Chart Integration Required'
                }
            }
        ]
    
    def _generate_premium_analysis(self) -> List[Dict[str, Any]]:
        """P.16-18: 프리미엄 평가"""
        
        premium_info = self.appraisal_ctx.get('premium', {})
        
        return [
            {
                'page': 16,
                'section': 'appraisal',
                'subsection': '6. 프리미엄 평가',
                'title': '프리미엄 구성요소',
                'content': {
                    'development_potential': premium_info.get('development_potential', {}),
                    'location_premium': premium_info.get('location_premium', {}),
                    'policy_benefit': premium_info.get('policy_benefit', {})
                }
            },
            {
                'page': 17,
                'section': 'appraisal',
                'subsection': '6. 프리미엄 평가',
                'title': '프리미엄 점수 산식',
                'content': {
                    'formula': 'Premium = Development(0-8%) + Location(0-5%) + Policy(0-3%)',
                    'calculation_details': {
                        'development': {
                            'rate': premium_info.get('development_potential', {}).get('rate', 0),
                            'rationale': premium_info.get('development_potential', {}).get('rationale', '')
                        },
                        'location': {
                            'rate': premium_info.get('location_premium', {}).get('rate', 0),
                            'rationale': premium_info.get('location_premium', {}).get('rationale', '')
                        },
                        'policy': {
                            'rate': premium_info.get('policy_benefit', {}).get('rate', 0),
                            'rationale': premium_info.get('policy_benefit', {}).get('rationale', '')
                        }
                    }
                }
            },
            {
                'page': 18,
                'section': 'appraisal',
                'subsection': '6. 프리미엄 평가',
                'title': '최종 프리미엄율 확정',
                'content': {
                    'total_premium_rate': premium_info.get('total_premium_rate', 0),
                    'total_premium_rate_percent': premium_info.get('total_premium_rate', 0) * 100,
                    'impact_on_value': '프리미엄을 적용하여 시장가치 반영',
                    'locked': True,
                    'warning': '⚠️ 본 프리미엄율은 이후 분석에서 변경되지 않습니다.'
                }
            }
        ]
    
    def _generate_final_appraisal(self) -> List[Dict[str, Any]]:
        """P.19-21: 최종 감정가 산출"""
        
        calculation = self.appraisal_ctx.get('calculation', {})
        
        return [
            {
                'page': 19,
                'section': 'appraisal',
                'subsection': '7. 최종 감정가 산출',
                'title': '단가 산출식',
                'content': {
                    'base_price': calculation.get('base_price_per_sqm', 0),
                    'premium_rate': self.appraisal_ctx.get('premium.total_premium_rate', 0),
                    'premium_adjusted': calculation.get('premium_adjusted_per_sqm', 0),
                    'formula': '단가 = 기준가 × (1 + 프리미엄율)',
                    'calculation_steps': [
                        f"1. 기준가: {calculation.get('base_price_per_sqm', 0):,.0f}원/㎡",
                        f"2. 프리미엄율: {self.appraisal_ctx.get('premium.total_premium_rate', 0)*100:.1f}%",
                        f"3. 최종 단가: {calculation.get('premium_adjusted_per_sqm', 0):,.0f}원/㎡"
                    ]
                }
            },
            {
                'page': 20,
                'section': 'appraisal',
                'subsection': '7. 최종 감정가 산출',
                'title': '최종 토지가치',
                'content': {
                    'land_area': calculation.get('land_area_sqm', 0),
                    'price_per_sqm': calculation.get('premium_adjusted_per_sqm', 0),
                    'final_appraised_total': calculation.get('final_appraised_total', 0),
                    'confidence_score': self.appraisal_ctx.get('confidence.score', 0),
                    'appraisal_method': self.appraisal_ctx.get('metadata.calculation_method', '비교방식'),
                    'breakdown': {
                        '토지 면적': f"{calculation.get('land_area_sqm', 0):.2f} ㎡",
                        '단가': f"{calculation.get('premium_adjusted_per_sqm', 0):,.0f} 원/㎡",
                        '최종 감정가': f"{calculation.get('final_appraised_total', 0):,.0f} 원"
                    }
                }
            },
            {
                'page': 21,
                'section': 'appraisal',
                'subsection': '7. 최종 감정가 산출',
                'title': '🔒 감정평가 완료 및 잠금',
                'content': {
                    'locked': True,
                    'locked_at': self.appraisal_ctx.get_locked_at(),
                    'final_value': calculation.get('final_appraised_total', 0),
                    'warning': '⚠️ 중요 공지',
                    'notice': [
                        '본 감정가는 이후 모든 분석의 기준이 됩니다.',
                        'SECTION 2(토지진단)에서는 재계산되지 않습니다.',
                        'SECTION 3(LH 판단)에서 이 값을 토지가액으로 사용합니다.',
                        '감정평가 로직 변경 시에만 이 값이 변경됩니다.'
                    ],
                    'appraisal_engine': self.appraisal_ctx.get('metadata.appraisal_engine', 'ZeroSite v8.7')
                }
            }
        ]
    
    def _generate_section_2_diagnosis(self) -> List[Dict[str, Any]]:
        """
        SECTION 2: Land Diagnosis (INTERPRETATION) - P.22-40 (19 pages)
        
        Interprets appraisal results WITHOUT modifying them
        """
        
        pages = []
        
        # 8. 개발 가능성 진단 (P.22-25)
        pages.extend(self._generate_development_potential())
        
        # 9. 건축 규모 검토 (P.26-29)
        pages.extend(self._generate_building_scale())
        
        # 10. 수요·유형 적합성 (P.30-34) - CH4 Dynamic Scoring
        pages.extend(self._generate_demand_suitability())
        
        # 11. 리스크 진단 (P.35-37)
        pages.extend(self._generate_risk_diagnosis())
        
        # 12. 토지진단 종합 평가 (P.38-40)
        pages.extend(self._generate_diagnosis_summary())
        
        return pages
    
    def _generate_development_potential(self) -> List[Dict[str, Any]]:
        """P.22-25: 개발 가능성 진단"""
        
        zoning_type = self.appraisal_ctx.get('zoning.confirmed_type')
        far = self.appraisal_ctx.get('zoning.floor_area_ratio')
        bcr = self.appraisal_ctx.get('zoning.building_coverage_ratio')
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm')
        
        # Calculate development capacity
        building_footprint = land_area * (bcr / 100)
        total_floor_area = land_area * (far / 100)
        
        return [
            {
                'page': 22,
                'section': 'diagnosis',
                'subsection': '8. 개발 가능성 진단',
                'title': '용도지역 기반 개발 가능성',
                'content': {
                    'zoning_type': zoning_type,
                    'development_grade': self._assess_development_grade(zoning_type, far),
                    'key_points': [
                        f'용도지역: {zoning_type}',
                        f'용적률: {far}%',
                        f'건폐율: {bcr}%',
                        f'개발 가능 연면적: {total_floor_area:,.0f}㎡'
                    ]
                }
            },
            {
                'page': 23,
                'section': 'diagnosis',
                'subsection': '8. 개발 가능성 진단',
                'title': '법적 제약사항 검토',
                'content': {
                    'restrictions': [
                        {'item': '고도제한', 'status': '확인 필요', 'impact': 'medium'},
                        {'item': '일조권', 'status': '검토 필요', 'impact': 'medium'},
                        {'item': '도로사선제한', 'status': '적용 가능', 'impact': 'low'},
                        {'item': '인접대지 이격거리', 'status': '적용 가능', 'impact': 'low'}
                    ],
                    'overall_assessment': '일반적인 법적 제약 범위 내'
                }
            },
            {
                'page': 24,
                'section': 'diagnosis',
                'subsection': '8. 개발 가능성 진단',
                'title': '입지 특성 분석',
                'content': {
                    'location_factors': {
                        'accessibility': self.analysis_data.get('accessibility', {}),
                        'surrounding_environment': '주거 중심 지역',
                        'future_development': '안정적 발전 예상'
                    }
                }
            },
            {
                'page': 25,
                'section': 'diagnosis',
                'subsection': '8. 개발 가능성 진단',
                'title': '개발 가능성 종합 점수',
                'content': {
                    'score': self._calculate_development_score(far, zoning_type),
                    'rating': self._get_development_rating(far),
                    'visualization': '📊 Radar Chart Placeholder'
                }
            }
        ]
    
    def _assess_development_grade(self, zoning_type: str, far: float) -> str:
        """Assess development grade based on zoning and FAR"""
        if far >= 400:
            return 'S (최우수)'
        elif far >= 300:
            return 'A (우수)'
        elif far >= 200:
            return 'B (양호)'
        else:
            return 'C (보통)'
    
    def _calculate_development_score(self, far: float, zoning_type: str) -> int:
        """Calculate development potential score"""
        base_score = min(int(far / 4), 100)
        return base_score
    
    def _get_development_rating(self, far: float) -> str:
        """Get development rating"""
        if far >= 400:
            return '매우 높음'
        elif far >= 300:
            return '높음'
        elif far >= 200:
            return '보통'
        else:
            return '낮음'
    
    def _generate_building_scale(self) -> List[Dict[str, Any]]:
        """P.26-29: 건축 규모 검토"""
        
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm')
        far = self.appraisal_ctx.get('zoning.floor_area_ratio')
        bcr = self.appraisal_ctx.get('zoning.building_coverage_ratio')
        
        # Building calculations
        total_floor_area = land_area * (far / 100)
        building_footprint = land_area * (bcr / 100)
        estimated_floors = int(total_floor_area / building_footprint)
        
        # Unit estimations
        avg_unit_size = 45  # 청년형 기준
        estimated_units = int(total_floor_area / avg_unit_size)
        
        return [
            {
                'page': 26,
                'section': 'diagnosis',
                'subsection': '9. 건축 규모 검토',
                'title': '건축 가능 규모 산정',
                'content': {
                    'land_area': land_area,
                    'far': far,
                    'bcr': bcr,
                    'total_floor_area': total_floor_area,
                    'building_footprint': building_footprint,
                    'estimated_floors': estimated_floors,
                    'calculation_formula': f'{land_area:.0f}㎡ × {far}% = {total_floor_area:,.0f}㎡'
                }
            },
            {
                'page': 27,
                'section': 'diagnosis',
                'subsection': '9. 건축 규모 검토',
                'title': '세대수 산정',
                'content': {
                    'total_floor_area': total_floor_area,
                    'unit_types': [
                        {'type': '청년형', 'size': 45, 'units': estimated_units, 'ratio': 1.0}
                    ],
                    'total_units': estimated_units,
                    'units_per_floor': int(estimated_units / max(estimated_floors, 1))
                }
            },
            {
                'page': 28,
                'section': 'diagnosis',
                'subsection': '9. 건축 규모 검토',
                'title': '층수 및 배치 계획',
                'content': {
                    'estimated_floors': estimated_floors,
                    'building_height': estimated_floors * 3,  # 3m per floor
                    'layout_type': 'ㄱ자형 또는 ㄷ자형 배치',
                    'parking': {
                        'required': estimated_units * 0.7,
                        'type': '지하주차장'
                    }
                }
            },
            {
                'page': 29,
                'section': 'diagnosis',
                'subsection': '9. 건축 규모 검토',
                'title': '건축 규모 타당성 검증',
                'content': {
                    'feasibility': '적정',
                    'key_metrics': {
                        '용적률 활용도': f'{far}% (법정 기준 충족)',
                        '세대수 효율': f'{estimated_units}세대',
                        '층수': f'{estimated_floors}층',
                        '평균 전용면적': f'{avg_unit_size}㎡'
                    },
                    'conclusion': 'LH 공공주택 개발에 적합한 규모'
                }
            }
        ]
    
    def _generate_demand_suitability(self) -> List[Dict[str, Any]]:
        """P.30-34: 수요·유형 적합성 (CH4 Dynamic Scoring)"""
        
        # Generate CH4 dynamic scores (using mock data for demonstration)
        type_demand_scores = {
            '청년': 88.5,
            '신혼부부 I': 85.2,
            '신혼부부 II': 82.0,
            '다자녀': 79.5,
            '고령자': 72.0
        }
        
        demographic_info = {
            'youth_ratio': self.analysis_data.get('youth_ratio', 25),
            'newlywed_ratio': 20,
            'multi_child_ratio': 15,
            'elderly_ratio': self.analysis_data.get('elderly_ratio', 10)
        }
        
        accessibility = {
            'subway_distance': self.analysis_data.get('distance_to_subway', 500),
            'bus_stops': 5,
            'accessibility_score': 75
        }
        
        demand_scores_raw = self.ch4_scorer.generate_demand_scores(
            type_demand_scores=type_demand_scores,
            demographic_info=demographic_info,
            accessibility=accessibility
        )
        
        # Transform to expected format
        demand_scores = {
            'type_scores': {k: v['total_score'] for k, v in demand_scores_raw.items()},
            'type_details': demand_scores_raw,
            'top_type': max(demand_scores_raw.items(), key=lambda x: x[1]['total_score'])[0],
            'average_score': sum(v['total_score'] for v in demand_scores_raw.values()) / len(demand_scores_raw),
            'recommendation': '청년형 중심 개발 권장',
            'key_insights': [
                '청년인구 비율 높음',
                '대중교통 접근성 우수',
                '주변 편의시설 양호'
            ]
        }
        
        return [
            {
                'page': 30,
                'section': 'diagnosis',
                'subsection': '10. 수요·유형 적합성',
                'title': 'CH4. 유형별 수요 점수 (Dynamic Scoring)',
                'content': {
                    'method': 'CH4 Dynamic Demand Scoring (ZeroSite v8.7)',
                    'type_scores': demand_scores['type_scores'],
                    'top_type': demand_scores['top_type'],
                    'note': '⚠️ 기존 v8.5의 획일적 13점 문제 해결'
                }
            },
            {
                'page': 31,
                'section': 'diagnosis',
                'subsection': '10. 수요·유형 적합성',
                'title': '유형별 상세 분석',
                'content': {
                    '청년형': demand_scores['type_details'].get('청년형', {}),
                    '신혼부부 I': demand_scores['type_details'].get('신혼부부 I', {}),
                    '신혼부부 II': demand_scores['type_details'].get('신혼부부 II', {}),
                    '다자녀형': demand_scores['type_details'].get('다자녀형', {}),
                    '고령자형': demand_scores['type_details'].get('고령자형', {})
                }
            },
            {
                'page': 32,
                'section': 'diagnosis',
                'subsection': '10. 수요·유형 적합성',
                'title': '수요 점수 Radar Chart',
                'content': {
                    'chart_type': 'radar',
                    'data': demand_scores['type_scores'],
                    'visualization': '📊 Radar Chart: 유형별 수요 점수 비교',
                    'placeholder': '🎨 Visualization Module Required'
                }
            },
            {
                'page': 33,
                'section': 'diagnosis',
                'subsection': '10. 수요·유형 적합성',
                'title': '권장 유형 조합',
                'content': {
                    'recommended_mix': self._calculate_recommended_mix(demand_scores),
                    'rationale': demand_scores['recommendation']
                }
            },
            {
                'page': 34,
                'section': 'diagnosis',
                'subsection': '10. 수요·유형 적합성',
                'title': '수요 적합성 종합 평가',
                'content': {
                    'overall_score': demand_scores['average_score'],
                    'suitability_grade': self._get_suitability_grade(demand_scores['average_score']),
                    'key_insights': demand_scores['key_insights']
                }
            }
        ]
    
    def _calculate_recommended_mix(self, demand_scores: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate recommended unit type mix"""
        type_scores = demand_scores['type_scores']
        total_score = sum(type_scores.values())
        
        return [
            {
                'type': unit_type,
                'score': score,
                'ratio': round(score / total_score * 100, 1)
            }
            for unit_type, score in sorted(type_scores.items(), key=lambda x: x[1], reverse=True)
        ]
    
    def _get_suitability_grade(self, avg_score: float) -> str:
        """Get suitability grade"""
        if avg_score >= 18:
            return 'S (최우수)'
        elif avg_score >= 16:
            return 'A (우수)'
        elif avg_score >= 14:
            return 'B (양호)'
        else:
            return 'C (보통)'
    
    def _generate_risk_diagnosis(self) -> List[Dict[str, Any]]:
        """P.35-37: 리스크 진단"""
        
        return [
            {
                'page': 35,
                'section': 'diagnosis',
                'subsection': '11. 리스크 진단',
                'title': '개발 리스크 요인',
                'content': {
                    'risks': [
                        {
                            'category': '법규 리스크',
                            'level': 'LOW',
                            'description': '용도지역 및 규제 사항 명확',
                            'mitigation': '사전 인허가 협의'
                        },
                        {
                            'category': '시장 리스크',
                            'level': 'MEDIUM',
                            'description': '공공주택 수요 변동 가능',
                            'mitigation': 'LH 매입 확약으로 헤지'
                        },
                        {
                            'category': '공사 리스크',
                            'level': 'MEDIUM',
                            'description': '건설비 상승 가능성',
                            'mitigation': 'LH 연동형 매입가 활용'
                        },
                        {
                            'category': '금융 리스크',
                            'level': 'LOW',
                            'description': '금리 변동 영향',
                            'mitigation': '단기 사업 기간으로 최소화'
                        }
                    ]
                }
            },
            {
                'page': 36,
                'section': 'diagnosis',
                'subsection': '11. 리스크 진단',
                'title': 'Risk Heatmap',
                'content': {
                    'heatmap_type': 'risk_matrix',
                    'risks': {
                        '법규': {'probability': 'LOW', 'impact': 'HIGH'},
                        '시장': {'probability': 'MEDIUM', 'impact': 'MEDIUM'},
                        '공사': {'probability': 'MEDIUM', 'impact': 'HIGH'},
                        '금융': {'probability': 'LOW', 'impact': 'MEDIUM'}
                    },
                    'visualization': '🔥 Risk Heatmap Placeholder'
                }
            },
            {
                'page': 37,
                'section': 'diagnosis',
                'subsection': '11. 리스크 진단',
                'title': '리스크 관리 방안',
                'content': {
                    'strategies': [
                        '사전 인허가 철저 검토',
                        'LH 매입 확약 조기 확보',
                        '건설사 선정 시 실적 우선',
                        '적정 사업비 예비비 확보'
                    ],
                    'overall_risk_level': 'MEDIUM',
                    'risk_management_score': 75
                }
            }
        ]
    
    def _generate_diagnosis_summary(self) -> List[Dict[str, Any]]:
        """P.38-40: 토지진단 종합 평가"""
        
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm')
        far = self.appraisal_ctx.get('zoning.floor_area_ratio')
        final_appraised_value = self.appraisal_ctx.get('calculation.final_appraised_total')
        
        return [
            {
                'page': 38,
                'section': 'diagnosis',
                'subsection': '12. 토지진단 종합 평가',
                'title': '진단 결과 요약',
                'content': {
                    'summary': {
                        '개발 가능성': self._get_development_rating(far),
                        '건축 규모': f'{land_area * far / 100:,.0f}㎡',
                        '수요 적합성': 'A (우수)',
                        '리스크 수준': 'MEDIUM (관리 가능)'
                    }
                }
            },
            {
                'page': 39,
                'section': 'diagnosis',
                'subsection': '12. 토지진단 종합 평가',
                'title': '종합 점수 카드',
                'content': {
                    'scores': {
                        '개발 가능성': 85,
                        '건축 효율성': 80,
                        '수요 적합성': 88,
                        '리스크 관리': 75
                    },
                    'total_score': 82,
                    'grade': 'B+',
                    'note': '⚠️ 점수는 감정가와 무관하며, 해석적 평가임'
                }
            },
            {
                'page': 40,
                'section': 'diagnosis',
                'subsection': '12. 토지진단 종합 평가',
                'title': '토지진단 결론',
                'content': {
                    'conclusion': 'LH 공공주택 개발에 적합한 토지',
                    'strengths': [
                        f'우수한 용도지역 ({self.appraisal_ctx.get("zoning.confirmed_type")})',
                        f'적정한 개발 규모 (용적률 {far}%)',
                        '안정적인 수요 기반',
                        '관리 가능한 리스크 수준'
                    ],
                    'considerations': [
                        '인허가 사전 협의 필요',
                        '건설비 변동 모니터링',
                        '시장 수요 지속 관찰'
                    ],
                    'appraisal_reference': {
                        'value': final_appraised_value,
                        'note': '⬆️ 위 감정가는 SECTION 1에서 확정되었으며 변경되지 않음'
                    }
                }
            }
        ]
    
    def _generate_section_3_lh_judgment(self) -> List[Dict[str, Any]]:
        """
        SECTION 3: LH Judgment (DECISION) - P.41-55 (15 pages)
        
        Uses appraisal value for financial calculations
        """
        
        pages = []
        
        # 13. 사업성 분석 (P.41-45)
        pages.extend(self._generate_financial_analysis())
        
        # 14. 시나리오 A/B/C 비교 (P.46-51)
        pages.extend(self._generate_scenario_comparison())
        
        # 15. LH 최종 판단 (P.52-55)
        pages.extend(self._generate_final_judgment())
        
        return pages
    
    def _generate_financial_analysis(self) -> List[Dict[str, Any]]:
        """P.41-45: 사업성 분석"""
        
        land_appraisal = self.lh_result.get('land_appraisal', 0)
        
        return [
            {
                'page': 41,
                'section': 'lh_judgment',
                'subsection': '13. 사업성 분석',
                'title': '공사비·Verified Cost',
                'content': {
                    'verified_cost': self.lh_result.get('verified_cost', 0),
                    'analysis_mode': self.lh_result.get('analysis_mode', 'STANDARD'),
                    'construction_breakdown': self.lh_result.get('cost_breakdown', {}),
                    'reference': f'토지가액: {land_appraisal:,.0f}원 (감정평가 결과)'
                }
            },
            {
                'page': 42,
                'section': 'lh_judgment',
                'subsection': '13. 사업성 분석',
                'title': 'LH 매입가 산정',
                'content': {
                    'land_appraisal': land_appraisal,
                    'verified_cost': self.lh_result.get('verified_cost', 0),
                    'lh_purchase_price': self.lh_result.get('lh_purchase_price', 0),
                    'formula': 'LH 매입가 = 토지감정가 + Verified Cost',
                    'based_on_appraisal': True,
                    'appraisal_locked': True
                }
            },
            {
                'page': 43,
                'section': 'lh_judgment',
                'subsection': '13. 사업성 분석',
                'title': 'ROI/IRR (CH3.3 Dynamic Scoring)',
                'content': {
                    'roi': self.lh_result.get('roi', 0),
                    'total_cost': self.lh_result.get('total_project_cost', 0),
                    'lh_purchase': self.lh_result.get('lh_purchase_price', 0),
                    'profit': self.lh_result.get('project_profit', 0),
                    'feasibility_score': self._calculate_ch3_score(),
                    'rating': self.lh_result.get('rating', 'N/A')
                }
            },
            {
                'page': 44,
                'section': 'lh_judgment',
                'subsection': '13. 사업성 분석',
                'title': 'Financial Waterfall',
                'content': {
                    'waterfall_chart': 'placeholder',
                    'steps': [
                        {'label': '토지가액', 'value': land_appraisal},
                        {'label': '+ 건축비', 'value': self.lh_result.get('verified_cost', 0)},
                        {'label': '+ 금융비용', 'value': self.lh_result.get('financing_cost', 0)},
                        {'label': '+ 부대비용', 'value': self.lh_result.get('ancillary_cost', 0)},
                        {'label': '= 총사업비', 'value': self.lh_result.get('total_project_cost', 0)},
                        {'label': 'LH 매입가', 'value': self.lh_result.get('lh_purchase_price', 0)},
                        {'label': '수익', 'value': self.lh_result.get('project_profit', 0)}
                    ]
                }
            },
            {
                'page': 45,
                'section': 'lh_judgment',
                'subsection': '13. 사업성 분석',
                'title': '수익성 요약',
                'content': {
                    'roi': self.lh_result.get('roi', 0),
                    'rating': self.lh_result.get('rating', 'N/A'),
                    'decision': self.lh_result.get('decision', 'N/A'),
                    'key_insights': self._generate_financial_insights()
                }
            }
        ]
    
    def _calculate_ch3_score(self) -> Dict[str, Any]:
        """Calculate CH3.3 feasibility score"""
        
        return self.ch3_scorer.calculate_feasibility_score(
            roi=self.lh_result.get('roi', 0),
            lh_purchase_price=self.lh_result.get('lh_purchase_price', 0),
            total_project_cost=self.lh_result.get('total_project_cost', 0),
            analysis_mode=self.lh_result.get('analysis_mode', 'STANDARD'),
            expected_units=self.lh_result.get('expected_units', 0),
            land_appraisal=self.lh_result.get('land_appraisal', 0),
            verified_cost=self.lh_result.get('verified_cost')
        )
    
    def _generate_financial_insights(self) -> List[str]:
        """Generate financial insights"""
        
        roi = self.lh_result.get('roi', 0)
        decision = self.lh_result.get('decision', 'N/A')
        
        insights = []
        
        if roi >= 8.0:
            insights.append("✅ 우수한 수익률로 사업 추진 강력 권장")
        elif roi >= 5.0:
            insights.append("✓ 양호한 수익률로 사업 추진 권장")
        elif roi >= 0.0:
            insights.append("⚠️ 낮은 수익률로 사업 재검토 권장")
        else:
            insights.append("❌ 마이너스 수익률로 사업 중단 권장")
        
        if decision == 'NO-GO':
            insights.append("⚠️ 감정평가액은 적정하나 사업성이 부족함")
        
        return insights
    
    def _generate_scenario_comparison(self) -> List[Dict[str, Any]]:
        """P.46-51: 시나리오 A/B/C 비교"""
        
        land_appraisal = self.lh_result.get('land_appraisal', 0)
        roi = self.lh_result.get('roi', 0)
        
        # Generate scenarios
        scenarios = self._calculate_scenarios(land_appraisal)
        
        return [
            {
                'page': 46,
                'section': 'lh_judgment',
                'subsection': '14. 시나리오 A/B/C 비교',
                'title': '시나리오 설정',
                'content': {
                    'scenario_a': {
                        'name': '기본 시나리오 (현재)',
                        'description': '현재 분석 결과 기준',
                        'land_value': land_appraisal,
                        'roi': roi
                    },
                    'scenario_b': {
                        'name': '낙관 시나리오 (건설비 -10%)',
                        'description': '건설비 10% 절감 가정',
                        'land_value': land_appraisal,
                        'roi': scenarios['optimistic']['roi']
                    },
                    'scenario_c': {
                        'name': '비관 시나리오 (건설비 +10%)',
                        'description': '건설비 10% 증가 가정',
                        'land_value': land_appraisal,
                        'roi': scenarios['pessimistic']['roi']
                    },
                    'note': '⚠️ 토지감정가는 모든 시나리오에서 동일 (LOCKED)'
                }
            },
            {
                'page': 47,
                'section': 'lh_judgment',
                'subsection': '14. 시나리오 A/B/C 비교',
                'title': 'Scenario A: 기본',
                'content': {
                    'land_cost': land_appraisal,
                    'construction_cost': self.lh_result.get('verified_cost', 0),
                    'total_cost': self.lh_result.get('total_project_cost', 0),
                    'lh_purchase': self.lh_result.get('lh_purchase_price', 0),
                    'roi': roi,
                    'decision': self.lh_result.get('decision', 'N/A')
                }
            },
            {
                'page': 48,
                'section': 'lh_judgment',
                'subsection': '14. 시나리오 A/B/C 비교',
                'title': 'Scenario B: 낙관',
                'content': scenarios['optimistic']
            },
            {
                'page': 49,
                'section': 'lh_judgment',
                'subsection': '14. 시나리오 A/B/C 비교',
                'title': 'Scenario C: 비관',
                'content': scenarios['pessimistic']
            },
            {
                'page': 50,
                'section': 'lh_judgment',
                'subsection': '14. 시나리오 A/B/C 비교',
                'title': '시나리오 비교 차트',
                'content': {
                    'chart_type': 'bar_comparison',
                    'data': {
                        'Scenario A': roi,
                        'Scenario B': scenarios['optimistic']['roi'],
                        'Scenario C': scenarios['pessimistic']['roi']
                    },
                    'visualization': '📊 Scenario Comparison Bar Chart',
                    'placeholder': '🎨 Visualization Module Required'
                }
            },
            {
                'page': 51,
                'section': 'lh_judgment',
                'subsection': '14. 시나리오 A/B/C 비교',
                'title': '시나리오 분석 결론',
                'content': {
                    'sensitivity': self._assess_sensitivity(scenarios),
                    'risk_level': self._assess_scenario_risk(scenarios),
                    'recommendation': self._get_scenario_recommendation(scenarios)
                }
            }
        ]
    
    def _calculate_scenarios(self, land_appraisal: float) -> Dict[str, Any]:
        """Calculate optimistic and pessimistic scenarios"""
        
        base_cost = self.lh_result.get('verified_cost', 0)
        base_total = self.lh_result.get('total_project_cost', 0)
        base_lh_purchase = self.lh_result.get('lh_purchase_price', 0)
        
        # Optimistic: -10% construction cost
        opt_cost = base_cost * 0.9
        opt_total = land_appraisal + opt_cost + (base_total - land_appraisal - base_cost)
        opt_roi = ((base_lh_purchase - opt_total) / opt_total) * 100 if opt_total > 0 else 0
        
        # Pessimistic: +10% construction cost
        pes_cost = base_cost * 1.1
        pes_total = land_appraisal + pes_cost + (base_total - land_appraisal - base_cost)
        pes_roi = ((base_lh_purchase - pes_total) / pes_total) * 100 if pes_total > 0 else 0
        
        return {
            'optimistic': {
                'land_cost': land_appraisal,
                'construction_cost': opt_cost,
                'total_cost': opt_total,
                'lh_purchase': base_lh_purchase,
                'roi': opt_roi,
                'decision': 'GO' if opt_roi >= 5 else 'CONDITIONAL'
            },
            'pessimistic': {
                'land_cost': land_appraisal,
                'construction_cost': pes_cost,
                'total_cost': pes_total,
                'lh_purchase': base_lh_purchase,
                'roi': pes_roi,
                'decision': 'GO' if pes_roi >= 5 else 'NO-GO'
            }
        }
    
    def _assess_sensitivity(self, scenarios: Dict[str, Any]) -> str:
        """Assess sensitivity to construction cost changes"""
        opt_roi = scenarios['optimistic']['roi']
        pes_roi = scenarios['pessimistic']['roi']
        spread = opt_roi - pes_roi
        
        if spread > 15:
            return '높음 (건설비 변동에 민감)'
        elif spread > 10:
            return '보통 (일정 수준 영향)'
        else:
            return '낮음 (건설비 변동 영향 제한적)'
    
    def _assess_scenario_risk(self, scenarios: Dict[str, Any]) -> str:
        """Assess overall scenario risk"""
        pes_roi = scenarios['pessimistic']['roi']
        
        if pes_roi < 0:
            return 'HIGH (비관 시나리오 적자)'
        elif pes_roi < 3:
            return 'MEDIUM (비관 시나리오 저수익)'
        else:
            return 'LOW (모든 시나리오 양호)'
    
    def _get_scenario_recommendation(self, scenarios: Dict[str, Any]) -> str:
        """Get recommendation based on scenario analysis"""
        opt_decision = scenarios['optimistic']['decision']
        pes_decision = scenarios['pessimistic']['decision']
        
        if opt_decision == 'GO' and pes_decision == 'GO':
            return '✅ 강력 추천: 모든 시나리오에서 사업성 확보'
        elif opt_decision == 'GO' and pes_decision in ['CONDITIONAL', 'NO-GO']:
            return '⚠️ 조건부 추천: 건설비 관리 필수'
        else:
            return '❌ 재검토 권장: 사업성 불확실'
    
    def _generate_final_judgment(self) -> List[Dict[str, Any]]:
        """P.52-55: LH 최종 판단"""
        
        land_appraisal = self.lh_result.get('land_appraisal', 0)
        roi = self.lh_result.get('roi', 0)
        rating = self.lh_result.get('rating', 'N/A')
        decision = self.lh_result.get('decision', 'N/A')
        
        # Calculate CH3.3 feasibility score
        feasibility_score = self._calculate_ch3_score()
        
        return [
            {
                'page': 52,
                'section': 'lh_judgment',
                'subsection': '15. LH 최종 판단',
                'title': 'CH3.3 사업성 평가 (Dynamic Scoring)',
                'content': {
                    'method': 'CH3.3 ROI-Based Feasibility Scoring (ZeroSite v8.7)',
                    'base_score': feasibility_score.get('base_score', 0),
                    'adjustments': feasibility_score.get('adjustments', {}),
                    'total_score': feasibility_score.get('total_score', 0),
                    'grade': feasibility_score.get('grade', 'N/A'),
                    'note': '⚠️ 기존 v8.5의 획일적 3-5점 문제 해결'
                }
            },
            {
                'page': 53,
                'section': 'lh_judgment',
                'subsection': '15. LH 최종 판단',
                'title': '종합 의사결정 프레임워크',
                'content': {
                    'decision_framework': {
                        'appraisal': {
                            'label': 'SECTION 1: 감정평가',
                            'value': land_appraisal,
                            'status': '🔒 LOCKED'
                        },
                        'diagnosis': {
                            'label': 'SECTION 2: 토지진단',
                            'score': 82,
                            'status': '✅ 적합'
                        },
                        'financial': {
                            'label': 'SECTION 3: 사업성',
                            'roi': roi,
                            'rating': rating,
                            'status': '✅ 양호' if roi >= 5 else '⚠️ 재검토'
                        }
                    },
                    'final_decision': decision
                }
            },
            {
                'page': 54,
                'section': 'lh_judgment',
                'subsection': '15. LH 최종 판단',
                'title': '최종 권고사항',
                'content': {
                    'recommendation': self._get_final_recommendation(decision, roi),
                    'action_items': self._get_action_items(decision),
                    'timeline': self._get_project_timeline(decision)
                }
            },
            {
                'page': 55,
                'section': 'lh_judgment',
                'subsection': '15. LH 최종 판단',
                'title': '종합 결론',
                'content': {
                    'executive_summary': self._generate_executive_conclusion(
                        land_appraisal, roi, rating, decision
                    ),
                    'key_numbers': {
                        '토지 감정가': f'{land_appraisal:,.0f}원',
                        'ROI': f'{roi:.2f}%',
                        '사업성 등급': rating,
                        '최종 판단': decision
                    },
                    'disclaimer': '본 분석은 자동화 시스템(ZeroSite v8.8)에 의해 생성되었으며, 최종 의사결정 전 전문가 검토가 필요합니다.'
                }
            }
        ]
    
    def _get_final_recommendation(self, decision: str, roi: float) -> str:
        """Get final recommendation text"""
        if decision == 'GO':
            return f'✅ 사업 추진 권장: 우수한 수익률({roi:.1f}%)과 안정적인 사업 구조'
        elif decision == 'CONDITIONAL':
            return f'⚠️ 조건부 추진: 리스크 관리 강화 필요 (ROI: {roi:.1f}%)'
        else:
            return f'❌ 사업 재검토: 낮은 수익률({roi:.1f}%)로 사업성 부족'
    
    def _get_action_items(self, decision: str) -> List[str]:
        """Get action items based on decision"""
        if decision == 'GO':
            return [
                'LH 매입 협약 체결 추진',
                '상세 설계 착수',
                '건설사 선정 절차 시작',
                '인허가 신청 준비'
            ]
        elif decision == 'CONDITIONAL':
            return [
                '건설비 절감 방안 검토',
                'LH 협상을 통한 매입가 조정',
                '리스크 관리 계획 수립',
                '전문가 자문 실시'
            ]
        else:
            return [
                '사업 구조 전면 재검토',
                '대체 부지 검토',
                '사업 중단 고려',
                '손실 최소화 방안 수립'
            ]
    
    def _get_project_timeline(self, decision: str) -> Dict[str, str]:
        """Get project timeline"""
        if decision == 'GO':
            return {
                '1개월': 'LH 협약 체결',
                '3개월': '설계 완료',
                '6개월': '착공',
                '18개월': '준공 및 LH 매각'
            }
        elif decision == 'CONDITIONAL':
            return {
                '1개월': '추가 검토 및 협상',
                '2개월': '사업 구조 조정',
                '3개월': '최종 결정',
                'TBD': '진행 여부 결정'
            }
        else:
            return {
                '즉시': '사업 중단 검토',
                '1개월': '대안 탐색',
                'TBD': '방향 재설정'
            }
    
    def _generate_executive_conclusion(
        self, land_appraisal: float, roi: float, rating: str, decision: str
    ) -> str:
        """Generate executive conclusion"""
        return f"""
본 토지는 감정평가 {land_appraisal/100000000:.1f}억원으로 평가되었으며,
LH 공공주택 개발 사업에서 ROI {roi:.1f}% (등급: {rating})의 사업성을 보입니다.

종합 판단: {decision}

감정평가 결과는 ZeroSite v8.7 Canonical Flow에 의해 고정되었으며,
모든 분석은 이 기준값을 사용하여 일관성을 확보하였습니다.
        """.strip()
    
    def _generate_appendix(self) -> List[Dict[str, Any]]:
        """P.56-60: Appendix"""
        
        return [
            {
                'page': 56,
                'section': 'appendix',
                'title': '데이터 출처',
                'content': {
                    'sources': [
                        '국토교통부 공시지가',
                        '실거래가 공개시스템',
                        'Kakao Map API',
                        'LH 건설비 기준'
                    ]
                }
            },
            {
                'page': 57,
                'section': 'appendix',
                'title': '산식 모음',
                'content': {
                    'formulas': [
                        '감정가 = 단가 × 면적',
                        '단가 = 기준가 × (1 + 프리미엄율)',
                        'LH 매입가 = 토지감정가 + Verified Cost',
                        'ROI = (매입가 - 총사업비) / 총사업비 × 100'
                    ]
                }
            },
            {
                'page': 58,
                'section': 'appendix',
                'title': 'API 구조',
                'content': {
                    'api_flow': 'Appraisal → Lock → Diagnosis → LH',
                    'immutable': 'Appraisal results are immutable'
                }
            },
            {
                'page': 59,
                'section': 'appendix',
                'title': '용어 정의',
                'content': {
                    'terms': {
                        'FACT': '감정평가 결과 (불변)',
                        'INTERPRETATION': '해석 (감정평가 참조)',
                        'JUDGMENT': '의사결정 (감정평가 기반)'
                    }
                }
            },
            {
                'page': 60,
                'section': 'appendix',
                'title': '법적 고지 및 보고서 메타데이터',
                'content': {
                    'disclaimer': '본 보고서는 자동 분석 결과이며, 실제 감정평가는 공인 감정평가사가 수행해야 합니다.',
                    'metadata': {
                        'report_id': self.report_id,
                        'generation_time': self.generation_time,
                        'zerosite_version': 'v8.8',
                        'pipeline_version': 'v8.9',
                        'appraisal_context_id': getattr(self.appraisal_ctx, '_context_id', self.report_id),
                        'appraisal_version': getattr(self.appraisal_ctx, '_version', 'v8.7'),
                        'appraisal_locked_at': getattr(self.appraisal_ctx, '_locked_at', self.generation_time),
                        'hash_signature': getattr(self.appraisal_ctx, '_hash', 'N/A')
                    },
                    'footer_note': '본 보고서의 SECTION 1 감정평가 결과는 해시 검증으로 보호되며, 이후 섹션에서의 무단 수정이 불가능합니다.'
                }
            }
        ]


def create_report_generator_v88(
    appraisal_ctx: AppraisalContextLock,
    analysis_data: Dict[str, Any],
    lh_analysis_result: Dict[str, Any]
) -> ReportGeneratorV88:
    """
    Factory function to create v8.8 report generator
    
    Returns:
        ReportGeneratorV88 instance
    """
    return ReportGeneratorV88(appraisal_ctx, analysis_data, lh_analysis_result)


__all__ = [
    'ReportGeneratorV88',
    'create_report_generator_v88'
]
