"""
Phase 10.5: LH Official Full Submission Report Generator
Generates comprehensive 30-50 page reports for immediate LH submission

This is the PRODUCT - the complete deliverable for LH projects.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import logging

# Core ZeroSite engines
from app.services.financial_engine_v7_4 import FinancialEngine

# Phase 8: Verified Cost
try:
    from app.services_v8.verified_cost_loader import VerifiedCostLoader
    VERIFIED_COST_AVAILABLE = True
except ImportError:
    VERIFIED_COST_AVAILABLE = False

# Phase 2.5: Enhanced Financial Metrics
try:
    from app.services_v2.financial_enhanced import FinancialEnhanced
    from config.financial_parameters import load_financial_parameters
    ENHANCED_METRICS_AVAILABLE = True
except ImportError:
    ENHANCED_METRICS_AVAILABLE = False

# Phase 6.8: Local Demand Model
try:
    from app.services_v3.demand_model.demand_predictor import DemandPredictor
    DEMAND_MODEL_AVAILABLE = True
except ImportError:
    DEMAND_MODEL_AVAILABLE = False

# Phase 7.7: Market Data
try:
    from app.services_v3.market_data.market_signal_analyzer import MarketSignalAnalyzer
    MARKET_DATA_AVAILABLE = True
except ImportError:
    MARKET_DATA_AVAILABLE = False

logger = logging.getLogger(__name__)


class LHFullReportGenerator:
    """
    Generate comprehensive 30-50 page LH submission reports
    
    Report Structure (15 sections):
    1. 표지 (Cover Page)
    2. 목차 (Table of Contents)
    3. 대상지 개요 (Site Overview)
    4. 도시계획 및 법규 (Zoning & Regulations)
    5. 입지 분석 (Location Analysis)
    6. 지역 분석 (Regional Analysis - Phase 6.8)
    7. 교통 분석 (Transportation Analysis)
    8. 생활편의시설 분석 (Amenities Analysis)
    9. 개발계획 및 건축규모 (Development Plan)
    10. 공사비 분석 (Construction Cost - Phase 8)
    11. 재무 분석 (Financial Analysis - Phase 2.5)
    12. 시장 분석 (Market Analysis - Phase 7.7)
    13. 세대유형 및 커뮤니티 계획 (Unit Types & Community)
    14. 비교 시나리오 분석 (Scenario Comparison)
    15. 리스크 분석 및 결론 (Risk & Conclusion)
    16. 부록 (Appendix)
    """
    
    def __init__(self):
        """Initialize report generator with all phase engines"""
        self.financial_engine = FinancialEngine()
        
        # Phase 8: Verified Cost
        if VERIFIED_COST_AVAILABLE:
            self.verified_cost_loader = VerifiedCostLoader()
        else:
            self.verified_cost_loader = None
        
        # Phase 2.5: Enhanced Metrics (uses static methods)
        self.enhanced_metrics_available = ENHANCED_METRICS_AVAILABLE
        if ENHANCED_METRICS_AVAILABLE:
            self.financial_params = load_financial_parameters()
        
        # Phase 6.8: Demand Model
        if DEMAND_MODEL_AVAILABLE:
            self.demand_predictor = DemandPredictor()
        else:
            self.demand_predictor = None
        
        # Phase 7.7: Market Data
        if MARKET_DATA_AVAILABLE:
            self.market_analyzer = MarketSignalAnalyzer()
        else:
            self.market_analyzer = None
    
    def generate_full_report_data(
        self,
        address: str,
        land_area_sqm: float,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate complete report data for LH submission
        
        Args:
            address: Target site address
            land_area_sqm: Land area in square meters
            additional_params: Optional parameters (appraisal_price, etc.)
            
        Returns:
            Complete report data dictionary
        """
        logger.info(f"Generating full LH report for: {address}")
        
        # Initialize report data
        report_data = {
            'metadata': self._generate_metadata(address),
            'site_overview': {},
            'zoning_regulations': {},
            'location_analysis': {},
            'regional_analysis': {},
            'transportation': {},
            'amenities': {},
            'development_plan': {},
            'construction_cost': {},
            'financial_analysis': {},
            'market_analysis': {},
            'unit_types': {},
            'scenario_comparison': {},
            'risk_analysis': {},
            'appendix': {}
        }
        
        # 1. Site Overview & Basic Data
        report_data['site_overview'] = {
            'address': address,
            'land_area_sqm': land_area_sqm,
            'land_area_pyeong': land_area_sqm / 3.3058,
            'analysis_date': datetime.now().strftime('%Y년 %m월 %d일'),
            'project_code': self._generate_project_code(address)
        }
        
        # 2. Zoning & Regulations (Default values for now)
        # Use default values for stable operation
        report_data['zoning_regulations'] = {
            'zone_type': '제2종일반주거지역',
            'bcr': 60,
            'far': 200,
            'max_height': 35,
            'parking_required': int(land_area_sqm * 2.0 / 45),  # Estimate: 1 parking per unit
            'building_area': land_area_sqm * 0.6,
            'gross_floor_area': land_area_sqm * 2.0
        }
        
        # 3. Regional Demand Analysis (Phase 6.8)
        # Initialize with defaults
        report_data['regional_analysis'] = {
            'recommended_type': 'youth',
            'demand_score': 60.0,
            'confidence_level': 'medium',
            'all_scores': {'youth': 60.0, 'newlyweds': 55.0, 'senior': 50.0},
            'key_factors': ['인구 밀도', '교통 접근성', '생활 편의시설'],
            'status': 'unavailable'
        }
        
        if self.demand_predictor:
            try:
                demand_result = self.demand_predictor.predict_optimal_housing_type(address)
                report_data['regional_analysis'].update({
                    'recommended_type': demand_result.get('recommended_type', 'youth'),
                    'demand_score': demand_result.get('demand_score', 60.0),
                    'confidence_level': demand_result.get('confidence_level', 'medium'),
                    'all_scores': demand_result.get('all_scores', {}),
                    'key_factors': demand_result.get('key_factors', []),
                    'status': 'available'
                })
            except Exception as e:
                logger.warning(f"Demand analysis failed: {e}")
        
        # 4. Construction Cost Analysis (Phase 8)
        # Always start with estimated cost as fallback
        report_data['construction_cost'] = self._estimate_construction_cost(
            report_data['zoning_regulations']['gross_floor_area']
        )
        
        if self.verified_cost_loader:
            try:
                # Extract region from address for verified cost lookup
                region = self._extract_region(address)
                housing_type = report_data['regional_analysis'].get('recommended_type', 'youth')
                
                verified_cost = self.verified_cost_loader.get_verified_cost(
                    region=region,
                    housing_type=housing_type
                )
                
                if verified_cost and verified_cost.get('cost_per_sqm'):
                    report_data['construction_cost'] = {
                        'cost_per_sqm': verified_cost['cost_per_sqm'],
                        'source': verified_cost.get('source', 'LH Official'),
                        'verification_year': verified_cost.get('verification_year', datetime.now().year),
                        'housing_type': verified_cost.get('housing_type', housing_type),
                        'total_construction_cost': verified_cost['cost_per_sqm'] * report_data['zoning_regulations']['gross_floor_area'],
                        'status': 'verified'
                    }
            except Exception as e:
                logger.warning(f"Verified cost loading failed: {e}")
        
        # 5. Financial Analysis (Phase 2.5)
        try:
            # Run financial engine with correct parameter names
            recommended_type = report_data['regional_analysis'].get('recommended_type', 'youth')
            financial_result = self.financial_engine.run_sensitivity_analysis(
                land_area=land_area_sqm,
                address=address,
                unit_type=recommended_type,
                construction_type='standard',
                land_appraisal_price=additional_params.get('appraisal_price') if additional_params else None,
                housing_type=recommended_type
            )
            
            # Extract base scenario
            base_scenario = financial_result.get('base', {})
            
            # Initialize with defaults
            report_data['financial_analysis'] = {
                'capex_total': base_scenario.get('capex_total', 0),
                'annual_revenue': base_scenario.get('annual_revenue', 0),
                'annual_opex': base_scenario.get('year_1_opex', 0),
                'stabilized_noi': base_scenario.get('stabilized_noi', 0),
                'cap_rate': base_scenario.get('cap_rate', 0),
                'npv_public': 0,
                'npv_private': 0,
                'irr': 0,
                'payback_period': 0,
                'scenarios': financial_result,
                'status': 'basic'
            }
            
            # Enhanced metrics (Phase 2.5)
            if self.enhanced_metrics_available and base_scenario.get('capex_total', 0) > 0:
                try:
                    # Extract cashflows from NOI projections
                    stabilized_noi = base_scenario.get('stabilized_noi', 0)
                    project_period_years = 10
                    annual_cashflows = [stabilized_noi] * project_period_years
                    capex = base_scenario['capex_total']
                    
                    # Calculate enhanced metrics using static methods
                    npv_public = FinancialEnhanced.npv(
                        self.financial_params['discount_rates']['public'],
                        annual_cashflows,
                        capex
                    )
                    npv_private = FinancialEnhanced.npv(
                        self.financial_params['discount_rates']['private'],
                        annual_cashflows,
                        capex
                    )
                    payback = FinancialEnhanced.payback(annual_cashflows, capex)
                    irr_value = FinancialEnhanced.irr(annual_cashflows, capex)
                    
                    enhanced = {
                        'npv_public': npv_public,
                        'npv_private': npv_private,
                        'payback_period': payback,
                        'irr': irr_value
                    }
                    
                    # Update with enhanced metrics
                    report_data['financial_analysis'].update({
                        'npv_public': enhanced.get('npv_public', 0),
                        'npv_private': enhanced.get('npv_private', 0),
                        'irr': enhanced.get('irr', 0),
                        'payback_period': enhanced.get('payback_period', 0),
                        'status': 'enhanced'
                    })
                except Exception as e:
                    logger.warning(f"Enhanced metrics calculation failed: {e}")
        except Exception as e:
            logger.error(f"Financial analysis failed: {e}")
            # Provide default values to prevent template errors
            report_data['financial_analysis'] = {
                'status': 'failed',
                'error': str(e),
                'capex_total': 0,
                'annual_revenue': 0,
                'annual_opex': 0,
                'stabilized_noi': 0,
                'npv_public': 0,
                'npv_private': 0,
                'irr': 0,
                'payback_period': 0,
                'cap_rate': 0
            }
        
        # 6. Market Analysis (Phase 7.7)
        zerosite_price = report_data['financial_analysis'].get('capex_total', 0)
        
        # Initialize with defaults
        report_data['market_analysis'] = {
            'signal': 'FAIR',
            'delta_pct': 0,
            'market_avg': zerosite_price,
            'zerosite_value': zerosite_price,
            'temperature': 'STABLE',
            'investment_recommendation': '시장 적정가 수준으로 안정적인 투자 가능',
            'status': 'unavailable'
        }
        
        if self.market_analyzer:
            try:
                market_result = self.market_analyzer.generate_market_report(
                    address=address,
                    zerosite_value=zerosite_price
                )
                
                report_data['market_analysis'].update({
                    'signal': market_result.get('signal', 'FAIR'),
                    'delta_pct': market_result.get('delta_pct', 0),
                    'market_avg': market_result.get('market_avg', zerosite_price),
                    'temperature': market_result.get('temperature', 'STABLE'),
                    'investment_recommendation': market_result.get('recommendation', ''),
                    'status': 'available'
                })
            except Exception as e:
                logger.warning(f"Market analysis failed: {e}")
        
        # 7. Unit Types & Community Plan
        report_data['unit_types'] = self._generate_unit_types(
            report_data['zoning_regulations']['gross_floor_area'],
            report_data['regional_analysis'].get('recommended_type', 'youth')
        )
        
        # 8. Scenario Comparison
        if 'scenarios' in report_data['financial_analysis']:
            report_data['scenario_comparison'] = self._generate_scenario_comparison(
                report_data['financial_analysis']['scenarios']
            )
        
        # 9. Risk Analysis
        report_data['risk_analysis'] = self._generate_risk_analysis(report_data)
        
        # 10. Appendix
        report_data['appendix'] = self._generate_appendix(report_data)
        
        logger.info(f"Full report data generation complete for {address}")
        return report_data
    
    def _generate_metadata(self, address: str) -> Dict[str, Any]:
        """Generate report metadata"""
        return {
            'report_title': 'LH 신축매입임대 사업 타당성 분석 보고서',
            'report_type': 'LH_SUBMISSION_FULL',
            'generated_date': datetime.now().strftime('%Y년 %m월 %d일'),
            'generated_datetime': datetime.now().isoformat(),
            'version': 'ZeroSite v13.0',
            'address': address,
            'report_code': self._generate_project_code(address)
        }
    
    def _generate_project_code(self, address: str) -> str:
        """Generate unique project code"""
        # Extract city/district
        parts = address.split()
        region_code = ''.join([p[0] for p in parts[:2]]) if len(parts) >= 2 else 'XX'
        date_code = datetime.now().strftime('%Y%m%d')
        return f"LH-{region_code}-{date_code}"
    
    def _extract_region(self, address: str) -> str:
        """Extract region from address for verified cost lookup"""
        address_lower = address.lower()
        if '서울' in address or 'seoul' in address_lower:
            return 'seoul'
        elif '경기' in address or 'gyeonggi' in address_lower:
            return 'gyeonggi'
        elif '인천' in address or 'incheon' in address_lower:
            return 'incheon'
        else:
            return 'other'
    
    def _estimate_construction_cost(self, gross_floor_area: float) -> Dict[str, Any]:
        """Fallback construction cost estimation"""
        cost_per_sqm = 3_500_000  # Standard cost
        return {
            'cost_per_sqm': cost_per_sqm,
            'source': 'Estimated (LH Standard)',
            'verification_year': datetime.now().year,
            'housing_type': 'standard',
            'total_construction_cost': cost_per_sqm * gross_floor_area,
            'status': 'estimated'
        }
    
    def _generate_unit_types(self, gross_floor_area: float, recommended_type: str) -> Dict[str, Any]:
        """Generate unit types and community plan"""
        # Average unit size assumptions
        unit_sizes = {
            'youth': 42,  # 청년: 42㎡
            'newlyweds': 45,  # 신혼부부: 45㎡
            'newlyweds_growth': 59,  # 신혼부부 성장형: 59㎡
            'multichild': 85,  # 다자녀: 85㎡
            'senior': 36  # 고령자: 36㎡
        }
        
        avg_unit_size = unit_sizes.get(recommended_type, 45)
        estimated_units = int(gross_floor_area / avg_unit_size * 0.75)  # 75% efficiency
        
        return {
            'recommended_type': recommended_type,
            'avg_unit_size_sqm': avg_unit_size,
            'estimated_units': estimated_units,
            'community_facilities': self._get_community_facilities(recommended_type)
        }
    
    def _get_community_facilities(self, housing_type: str) -> List[str]:
        """Get recommended community facilities by housing type"""
        facilities_map = {
            'youth': ['공유 오피스', '피트니스센터', '공유 라운지', '세탁실'],
            'newlyweds': ['어린이집', '맘스카페', '놀이터', '커뮤니티센터'],
            'newlyweds_growth': ['어린이집', '키즈카페', '독서실', '놀이터'],
            'multichild': ['어린이집', '키즈카페', '독서실', '놀이터', '체육시설'],
            'senior': ['경로당', '건강관리실', '산책로', '휴게시설']
        }
        return facilities_map.get(housing_type, ['커뮤니티센터'])
    
    def _generate_scenario_comparison(self, scenarios: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scenario comparison analysis"""
        comparison = {
            'base': scenarios.get('base', {}),
            'optimistic': scenarios.get('optimistic', {}),
            'pessimistic': scenarios.get('pessimistic', {})
        }
        
        # Extract key metrics for comparison
        metrics = ['capex_total', 'stabilized_noi', 'irr', 'npv', 'payback_period']
        comparison_table = {}
        
        for metric in metrics:
            comparison_table[metric] = {
                'base': scenarios.get('base', {}).get(metric, 0),
                'optimistic': scenarios.get('optimistic', {}).get(metric, 0),
                'pessimistic': scenarios.get('pessimistic', {}).get(metric, 0)
            }
        
        return {
            'scenarios': comparison,
            'comparison_table': comparison_table
        }
    
    def _generate_risk_analysis(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk analysis"""
        risks = []
        
        # Financial risks
        financial = report_data.get('financial_analysis', {})
        if financial.get('payback_period', 0) > 8:
            risks.append({
                'category': '재무 리스크',
                'risk': '회수기간 장기화',
                'description': f"회수기간 {financial.get('payback_period', 0):.1f}년으로 장기",
                'mitigation': '임대료 인상 또는 운영비 절감 전략 수립'
            })
        
        # Market risks
        market = report_data.get('market_analysis', {})
        if market.get('signal') == 'OVERVALUED':
            risks.append({
                'category': '시장 리스크',
                'risk': '시장 대비 고평가',
                'description': f"시장가 대비 {market.get('delta_pct', 0):+.1f}% 고평가",
                'mitigation': '가격 조정 또는 가치 제고 전략 필요'
            })
        
        # Demand risks
        regional = report_data.get('regional_analysis', {})
        if regional.get('confidence_level') == 'low':
            risks.append({
                'category': '수요 리스크',
                'risk': '지역 수요 불확실',
                'description': '수요 예측 신뢰도 낮음',
                'mitigation': '시장 조사 및 수요 검증 필요'
            })
        
        return {
            'total_risks': len(risks),
            'risks': risks,
            'overall_risk_level': 'HIGH' if len(risks) >= 3 else 'MEDIUM' if len(risks) >= 1 else 'LOW'
        }
    
    def _generate_appendix(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appendix data"""
        return {
            'data_sources': [
                '국토교통부 실거래가 공개시스템',
                'LH 표준공사비 (2024년)',
                'Statistics Korea (KOSIS)',
                'ZeroSite Internal Database'
            ],
            'calculation_methods': [
                'NPV: 순현재가치법 (할인율 공공 2%, 민간 5.5%)',
                'IRR: 내부수익률 (Newton-Raphson Method)',
                'Payback: 투자회수기간 (선형보간법)'
            ],
            'assumptions': [
                f"분석 기준일: {datetime.now().strftime('%Y년 %m월 %d일')}",
                '사업기간: 10년 가정',
                '공실률: 안정화 후 5% 가정',
                '임대료 상승률: 연 2% 가정'
            ]
        }


# Convenience function
def generate_lh_full_report(
    address: str,
    land_area_sqm: float,
    **kwargs
) -> Dict[str, Any]:
    """
    Quick function to generate full LH report
    
    Args:
        address: Target site address
        land_area_sqm: Land area in square meters
        **kwargs: Additional parameters
        
    Returns:
        Complete report data dictionary
    """
    generator = LHFullReportGenerator()
    return generator.generate_full_report_data(address, land_area_sqm, kwargs)
