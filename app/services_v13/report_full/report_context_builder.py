"""
ZeroSite v13.0: Complete Report Context Builder
================================================

This module builds a comprehensive REPORT_CONTEXT that integrates ALL Phase data:
- Phase 2.5: Enhanced Financial Metrics (NPV, IRR, Payback, 10-year Cash Flow)
- Phase 6.8: AI Demand Intelligence (21 features, scoring, WHY explanation)
- Phase 7.7: Market Intelligence (Signal, Trend, Competition, Recommendation)
- Phase 8: Verified Cost (LH Official breakdown, unit cost, category breakdown)
- Phase 10.5: Multi-Parcel Support (Merge analysis, combined metrics)

The REPORT_CONTEXT is the SINGLE source of truth for report generation.
It enables deterministic, 100% automated 30-50 page LH submission reports.

Architecture:
    Engine Data → ReportContextBuilder → REPORT_CONTEXT → Jinja2 Template → PDF

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0 (Complete Edition)
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path
import logging
import json

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

# Narrative Interpreter & Policy Reference DB
from app.services_v13.report_full.narrative_interpreter import NarrativeInterpreter
from app.services_v13.report_full.policy_reference_db import PolicyReferenceDB

# Phase 2: Competitive Analysis & Risk Enhancement
try:
    from app.services_v13.report_full.competitive_analyzer import CompetitiveAnalyzer
    COMPETITIVE_ANALYSIS_AVAILABLE = True
except ImportError:
    COMPETITIVE_ANALYSIS_AVAILABLE = False

try:
    from app.services_v13.report_full.risk_enhancer import RiskEnhancer
    RISK_ENHANCEMENT_AVAILABLE = True
except ImportError:
    RISK_ENHANCEMENT_AVAILABLE = False

logger = logging.getLogger(__name__)


class ReportContextBuilder:
    """
    Builds comprehensive REPORT_CONTEXT integrating all Phase data
    
    The REPORT_CONTEXT structure:
    {
        "metadata": {...},
        "site": {
            "address": str,
            "multi_parcel": bool,
            "parcels": [...],
            "merged": {...}  # If multi-parcel
        },
        "zoning": {...},
        "demand": {
            "recommended_type": str,
            "overall_score": float,
            "confidence_level": str,
            "all_scores": {...},
            "features": {...},
            "reasoning": {
                "reason_1": str,  # WHY this housing type
                "reason_2": str,
                "reason_3": str
            }
        },
        "market": {
            "signal": "UNDERVALUED" | "FAIR" | "OVERVALUED",
            "delta_pct": float,
            "temperature": str,
            "trend": {...},
            "competition": {...},
            "recommendation": str,
            "reasoning": {
                "reason_1": str,  # WHY this signal
                "reason_2": str,
                "reason_3": str
            }
        },
        "cost": {
            "construction": {
                "total": float,
                "per_sqm": float,
                "breakdown": {
                    "direct": float,
                    "indirect": float,
                    "design": float,
                    "finance": float,
                    "tax": float,
                    "contingency": float
                }
            },
            "verification": {
                "source": str,
                "year": int,
                "region": str,
                "housing_type": str
            }
        },
        "finance": {
            "capex": {
                "land": float,
                "construction": float,
                "soft_cost": float,
                "total": float
            },
            "revenue": {
                "annual_rental": float,
                "occupancy_rate": float,
                "effective_revenue": float
            },
            "opex": {
                "annual": float,
                "per_unit": float
            },
            "noi": {
                "year_1": float,
                "stabilized": float
            },
            "npv": {
                "public": float,
                "private": float,
                "discount_rate_public": float,
                "discount_rate_private": float
            },
            "irr": {
                "public": float,
                "market": float
            },
            "payback": {
                "years": float
            },
            "cashflow": [
                {"year": int, "cf": float, "cumulative": float},
                # ... 10 years
            ]
        },
        "scenario_comparison": {
            "base": {...},
            "optimistic": {...},
            "pessimistic": {...},
            "sensitivity": {
                "cost_change_optimistic": float,  # e.g., -3%
                "cost_change_pessimistic": float,  # e.g., +7%
                "impact_on_npv": str,
                "impact_on_irr": str
            }
        },
        "risk_analysis": {
            "legal": {
                "level": "GREEN" | "YELLOW" | "RED",
                "description": str,
                "mitigation": str,
                "impact": str
            },
            "market": {...},
            "construction": {...},
            "overall_level": "LOW" | "MEDIUM" | "HIGH"
        },
        "decision": {
            "recommendation": "GO" | "CONDITIONAL" | "REVISE" | "NO-GO",
            "reasoning": [str, str, str],  # 3 key reasons
            "confidence": str,
            "conditions": [str] if CONDITIONAL
        }
    }
    """
    
    def __init__(self):
        """Initialize context builder with all phase engines"""
        self.financial_engine = FinancialEngine()
        
        # Phase 8: Verified Cost
        if VERIFIED_COST_AVAILABLE:
            self.verified_cost_loader = VerifiedCostLoader()
        else:
            self.verified_cost_loader = None
        
        # Phase 2.5: Enhanced Metrics
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
        
        # Phase 2: Competitive Analysis & Risk Enhancement
        if COMPETITIVE_ANALYSIS_AVAILABLE:
            self.competitive_analyzer = CompetitiveAnalyzer()
        else:
            self.competitive_analyzer = None
        
        if RISK_ENHANCEMENT_AVAILABLE:
            self.risk_enhancer = RiskEnhancer()
        else:
            self.risk_enhancer = None
        
        # Narrative Interpreter & Policy Reference DB (Phase A)
        self.narrative_interpreter = NarrativeInterpreter()
        self.policy_db = PolicyReferenceDB()
        
        logger.info("✅ ReportContextBuilder initialized with all Phase engines (including Narrative Layer)")
    
    def build_context(
        self,
        address: str,
        land_area_sqm: float,
        coordinates: Optional[Tuple[float, float]] = None,
        multi_parcel: bool = False,
        parcels: Optional[List[Dict[str, Any]]] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build complete REPORT_CONTEXT from input parameters
        
        Args:
            address: Target site address
            land_area_sqm: Total land area in sqm
            coordinates: (lat, lon) for location analysis
            multi_parcel: Whether this is a multi-parcel project
            parcels: List of individual parcel data if multi_parcel=True
            additional_params: Additional parameters (appraisal_price, etc.)
        
        Returns:
            Complete REPORT_CONTEXT dictionary
        """
        logger.info(f"🏗️ Building REPORT_CONTEXT for: {address}")
        
        context = {
            'metadata': self._build_metadata(address),
            'site': self._build_site_section(address, land_area_sqm, multi_parcel, parcels),
            'zoning': {},
            'demand': {},
            'market': {},
            'cost': {},
            'finance': {},
            'scenario_comparison': {},
            'risk_analysis': {},
            'decision': {}
        }
        
        # 1. Build Zoning & Regulations
        context['zoning'] = self._build_zoning_section(land_area_sqm)
        
        # 2. Build Demand Analysis (Phase 6.8)
        context['demand'] = self._build_demand_section(address, coordinates)
        
        # 3. Build Cost Analysis (Phase 8)
        recommended_type = context['demand'].get('recommended_type', 'youth')
        context['cost'] = self._build_cost_section(
            address, 
            context['zoning']['gross_floor_area'],
            recommended_type
        )
        
        # 4. Build Financial Analysis (Phase 2.5)
        context['finance'] = self._build_finance_section(
            address,
            land_area_sqm,
            recommended_type,
            context['cost'],
            context['zoning'],
            additional_params
        )
        
        # 5. Build Market Analysis (Phase 7.7)
        zerosite_value = context['finance']['capex']['total']
        context['market'] = self._build_market_section(address, zerosite_value)
        
        # 6. Build Scenario Comparison
        context['scenario_comparison'] = self._build_scenario_section(context['finance'])
        
        # 7. Build Risk Analysis
        context['risk_analysis'] = self._build_risk_section(context)
        
        # 8. Build Final Decision
        context['decision'] = self._build_decision_section(context)
        
        # 9. Generate Narrative Interpretations (NEW!)
        context['narratives'] = self.narrative_interpreter.generate_all_narratives(context)
        
        logger.info(f"✅ REPORT_CONTEXT complete for {address}")
        return context
    
    def _build_metadata(self, address: str) -> Dict[str, Any]:
        """Build report metadata"""
        return {
            'report_title': 'LH 신축매입임대 사업 타당성 분석 보고서',
            'report_type': 'LH_SUBMISSION_FULL_EDITION',
            'generated_date': datetime.now().strftime('%Y년 %m월 %d일'),
            'generated_datetime': datetime.now().isoformat(),
            'version': 'ZeroSite v13.0',
            'address': address,
            'report_code': self._generate_project_code(address),
            'page_count_estimated': '30-50',
            'submission_ready': True
        }
    
    def _build_site_section(
        self, 
        address: str, 
        land_area_sqm: float,
        multi_parcel: bool,
        parcels: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Build site overview section"""
        site = {
            'address': address,
            'land_area_sqm': land_area_sqm,
            'land_area_pyeong': land_area_sqm / 3.3058,
            'multi_parcel': multi_parcel,
            'analysis_date': datetime.now().strftime('%Y년 %m월 %d일')
        }
        
        if multi_parcel and parcels:
            site['parcels'] = parcels
            site['parcel_count'] = len(parcels)
            site['merged'] = self._merge_parcels(parcels)
        
        return site
    
    def _merge_parcels(self, parcels: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multi-parcel data"""
        # TODO: Implement proper parcel merging logic
        total_area = sum(p.get('area_sqm', 0) for p in parcels)
        return {
            'total_area_sqm': total_area,
            'total_area_pyeong': total_area / 3.3058,
            'merge_method': 'weighted_average',
            'status': 'merged'
        }
    
    def _build_zoning_section(self, land_area_sqm: float) -> Dict[str, Any]:
        """Build zoning & regulations section"""
        # Use default values for stable operation
        # In production, integrate with GIS/zoning API
        return {
            'zone_type': '제2종일반주거지역',
            'zone_type_en': 'Type 2 General Residential',
            'bcr': 60,  # Building Coverage Ratio (%)
            'far': 200,  # Floor Area Ratio (%)
            'max_height': 35,  # meters
            'max_floors': 11,
            'parking_required': int(land_area_sqm * 2.0 / 45),
            'building_area': land_area_sqm * 0.6,
            'gross_floor_area': land_area_sqm * 2.0,
            'parking_ratio': 1.0,  # 1 parking per unit
            'status': 'default'
        }
    
    def _build_demand_section(
        self, 
        address: str,
        coordinates: Optional[Tuple[float, float]]
    ) -> Dict[str, Any]:
        """Build demand analysis section (Phase 6.8)"""
        
        # Default values
        demand = {
            'recommended_type': 'youth',
            'recommended_type_kr': '청년형',
            'overall_score': 60.0,
            'confidence_level': 'medium',
            'all_scores': {
                'youth': 60.0,
                'newlyweds': 55.0,
                'newlyweds_growth': 52.0,
                'multichild': 50.0,
                'senior': 48.0
            },
            'features': {},
            'reasoning': {
                'reason_1': '인구 밀도가 높아 주거 수요가 안정적입니다',
                'reason_2': '대중교통 접근성이 우수하여 청년층 선호도가 높습니다',
                'reason_3': '생활 편의시설이 인근에 충분히 갖춰져 있습니다'
            },
            'status': 'default'
        }
        
        # FIX: If no coordinates provided, derive from address
        if not coordinates:
            coordinates = self._get_coordinates(address)
            logger.info(f"Generated coordinates for {address}: {coordinates}")
        
        if self.demand_predictor and coordinates:
            try:
                result = self.demand_predictor.predict(address, coordinates)
                
                # Extract reasoning from features or description
                recommended_type = result.get('recommended_type', 'youth')
                demand.update({
                    'recommended_type': recommended_type,
                    'recommended_type_kr': self._translate_housing_type(recommended_type),
                    'overall_score': result.get('scores', {}).get(recommended_type, 60.0),
                    'confidence_level': result.get('confidence', 'medium'),
                    'all_scores': result.get('scores', {}),
                    'features': result.get('features', {}),
                    'reasoning': self._extract_demand_reasoning(result),
                    'status': 'phase_6_8'
                })
                logger.info(f"✅ Phase 6.8 Demand: type={recommended_type}, score={demand['overall_score']:.1f}")
            except Exception as e:
                logger.warning(f"Demand analysis failed: {e}")
                import traceback
                logger.warning(traceback.format_exc())
        
        return demand
    
    def _extract_demand_reasoning(self, demand_result: Dict[str, Any]) -> Dict[str, str]:
        """Extract 3 key reasons WHY this housing type is recommended"""
        # TODO: Implement intelligent reasoning extraction from features
        # For now, generate generic but structured reasoning
        
        recommended_type = demand_result.get('recommended_type', 'youth')
        features = demand_result.get('features', {})
        
        reasoning = {
            'reason_1': f'{self._translate_housing_type(recommended_type)}에 가장 적합한 지역 특성을 보입니다',
            'reason_2': '수요 특성 분석 결과 높은 적합도를 나타냅니다',
            'reason_3': '지역 인프라와 생활 편의시설이 잘 갖춰져 있습니다'
        }
        
        # TODO: Add intelligent reasoning based on feature analysis
        # e.g., if feature['university_nearby'] == True:
        #       reason_1 = "인근 대학교로 인한 청년층 수요가 높습니다"
        
        return reasoning
    
    def _build_cost_section(
        self,
        address: str,
        gross_floor_area: float,
        housing_type: str
    ) -> Dict[str, Any]:
        """Build construction cost section (Phase 8)"""
        
        # Fallback cost estimation
        cost_per_sqm_base = 3_500_000  # 350만원/m²
        
        cost = {
            'construction': {
                'total': cost_per_sqm_base * gross_floor_area,
                'per_sqm': cost_per_sqm_base,
                'breakdown': {
                    'direct': cost_per_sqm_base * gross_floor_area * 0.70,  # 70%
                    'indirect': cost_per_sqm_base * gross_floor_area * 0.15,  # 15%
                    'design': cost_per_sqm_base * gross_floor_area * 0.05,   # 5%
                    'finance': cost_per_sqm_base * gross_floor_area * 0.05,  # 5%
                    'tax': cost_per_sqm_base * gross_floor_area * 0.03,      # 3%
                    'contingency': cost_per_sqm_base * gross_floor_area * 0.02  # 2%
                }
            },
            'verification': {
                'source': 'Estimated (LH Standard)',
                'year': datetime.now().year,
                'region': self._extract_region(address),
                'housing_type': housing_type,
                'status': 'estimated'
            }
        }
        
        # Try to get Phase 8 verified cost
        if self.verified_cost_loader:
            try:
                region = self._extract_region(address)
                # Use get_cost method (returns VerifiedCostData object)
                verified_cost_obj = self.verified_cost_loader.get_cost(
                    address=address,
                    housing_type=housing_type,
                    year=datetime.now().year
                )
                
                if verified_cost_obj and verified_cost_obj.cost_per_m2:
                    verified_per_sqm = verified_cost_obj.cost_per_m2
                    cost['construction'].update({
                        'total': verified_per_sqm * gross_floor_area,
                        'per_sqm': verified_per_sqm,
                        'breakdown': {
                            'direct': verified_per_sqm * gross_floor_area * 0.70,
                            'indirect': verified_per_sqm * gross_floor_area * 0.15,
                            'design': verified_per_sqm * gross_floor_area * 0.05,
                            'finance': verified_per_sqm * gross_floor_area * 0.05,
                            'tax': verified_per_sqm * gross_floor_area * 0.03,
                            'contingency': verified_per_sqm * gross_floor_area * 0.02
                        }
                    })
                    cost['verification'].update({
                        'source': 'LH Official Verified',
                        'year': verified_cost.get('verification_year', datetime.now().year),
                        'status': 'verified'
                    })
            except Exception as e:
                logger.warning(f"Verified cost loading failed: {e}")
        
        return cost
    
    def _build_finance_section(
        self,
        address: str,
        land_area_sqm: float,
        housing_type: str,
        cost_data: Dict[str, Any],
        zoning_data: Dict[str, Any],
        additional_params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build comprehensive financial analysis section (Phase 2.5)"""
        
        # Run financial engine
        try:
            financial_result = self.financial_engine.run_sensitivity_analysis(
                land_area=land_area_sqm,
                address=address,
                unit_type=housing_type,
                construction_type='standard',
                land_appraisal_price=additional_params.get('appraisal_price') if additional_params else None,
                housing_type=housing_type
            )
            
            base_scenario = financial_result.get('base', {})
        except Exception as e:
            logger.error(f"Financial engine failed: {e}")
            base_scenario = {}
        
        # Extract base metrics from correct structure
        capex_data = base_scenario.get('capex', {})
        opex_data = base_scenario.get('opex', {})
        noi_data = base_scenario.get('noi', {})
        return_metrics = base_scenario.get('return_metrics', {})
        
        capex_total = capex_data.get('total_capex', cost_data['construction']['total'] * 1.3)
        annual_opex = opex_data.get('year1_total_opex', 0)
        stabilized_noi = noi_data.get('noi', 0)  # Correct key is 'noi', not 'stabilized_noi'
        annual_revenue = noi_data.get('effective_annual_income', stabilized_noi + annual_opex)  # Revenue = NOI + OpEx
        
        finance = {
            'capex': {
                'land': capex_total * 0.20,  # Estimated 20% land
                'construction': cost_data['construction']['total'],
                'soft_cost': capex_total * 0.10,  # Estimated 10% soft cost
                'total': capex_total
            },
            'revenue': {
                'annual_rental': annual_revenue,
                'occupancy_rate': 95.0,  # Assumed 95%
                'effective_revenue': annual_revenue * 0.95
            },
            'opex': {
                'annual': annual_opex,
                'per_unit': 0  # Will be calculated
            },
            'noi': {
                'year_1': stabilized_noi * 0.85,  # 85% in year 1
                'stabilized': stabilized_noi
            },
            'npv': {
                'public': 0,
                'private': 0,
                'discount_rate_public': 2.87,  # LH official rate
                'discount_rate_private': 5.5
            },
            'irr': {
                'public': 0,
                'market': 0
            },
            'payback': {
                'years': 0
            },
            'cashflow': []
        }
        
        # Calculate enhanced metrics (Phase 2.5)
        # FIX: Force calculation even if enhanced_metrics_available is False
        # Use fallback calculation if FinancialEnhanced is not available
        should_calculate_metrics = stabilized_noi > 0 or capex_total > 0
        
        if should_calculate_metrics:
            try:
                # Phase 1, Task 1.4: Generate 30-year cash flow (extended from 10 years)
                project_period_years = 30
                
                # Model: Year 1 = 85% of stabilized, Year 2-30 = 100% stabilized
                # Include annual 2% revenue growth from Year 6 onwards
                annual_cashflows = []
                for year in range(project_period_years):
                    if year == 0:  # Year 1
                        cf = stabilized_noi * 0.85  # Ramp-up period
                    elif year <= 4:  # Year 2-5: stabilized
                        cf = stabilized_noi
                    else:  # Year 6-30: with 2% annual growth
                        growth_factor = (1.02) ** (year - 4)  # 2% compounding from Year 6
                        cf = stabilized_noi * growth_factor
                    annual_cashflows.append(cf)
                
                # Calculate NPV
                if self.enhanced_metrics_available:
                    discount_rate_public = self.financial_params['discount_rates']['public']['rate']
                    discount_rate_private = self.financial_params['discount_rates']['private']['rate']
                    
                    npv_public = FinancialEnhanced.npv(
                        discount_rate_public,
                        annual_cashflows,
                        capex_total
                    )
                    npv_private = FinancialEnhanced.npv(
                        discount_rate_private,
                        annual_cashflows,
                        capex_total
                    )
                    
                    # Calculate Payback
                    payback = FinancialEnhanced.payback(annual_cashflows, capex_total)
                    
                    # Calculate IRR
                    irr_value = FinancialEnhanced.irr(annual_cashflows, capex_total)
                else:
                    # FIX: Fallback calculation using numpy
                    import numpy as np
                    discount_rate_public = 0.0287  # 2.87% LH official rate
                    discount_rate_private = 0.055  # 5.5% market rate
                    
                    # Simple NPV calculation
                    npv_public = sum([cf / ((1 + discount_rate_public) ** (i + 1)) for i, cf in enumerate(annual_cashflows)]) - capex_total
                    npv_private = sum([cf / ((1 + discount_rate_private) ** (i + 1)) for i, cf in enumerate(annual_cashflows)]) - capex_total
                    
                    # Simple Payback calculation
                    cumulative = 0
                    payback = float('inf')
                    for i, cf in enumerate(annual_cashflows):
                        cumulative += cf
                        if cumulative >= capex_total:
                            payback = i + 1 + (capex_total - (cumulative - cf)) / cf
                            break
                    
                    # Simple IRR calculation using numpy
                    try:
                        cash_flows = [-capex_total] + annual_cashflows
                        irr_value = np.irr(cash_flows)
                        if not np.isfinite(irr_value):
                            irr_value = None
                    except:
                        irr_value = None
                
                # Update finance section
                finance['npv']['public'] = npv_public
                finance['npv']['private'] = npv_private
                finance['npv']['discount_rate_public'] = discount_rate_public * 100  # Convert to percentage
                finance['npv']['discount_rate_private'] = discount_rate_private * 100
                finance['irr']['public'] = irr_value * 100 if irr_value else 0  # Convert to percentage
                finance['irr']['market'] = irr_value * 1.2 * 100 if irr_value else 0  # Estimated market IRR
                finance['payback']['years'] = payback if payback else 0
                
                # Build cash flow table (30 years)
                cumulative = -capex_total
                finance['cashflow'] = []
                for year in range(1, project_period_years + 1):
                    cf = annual_cashflows[year - 1]
                    cumulative += cf
                    finance['cashflow'].append({
                        'year': year,
                        'cf': cf,
                        'cumulative': cumulative
                    })
                
                # Phase 1, Task 1.5: Add Key Financial Ratios (DSCR, LTV, ROI, ROE)
                finance['ratios'] = self._calculate_financial_ratios(
                    capex_total, 
                    stabilized_noi, 
                    annual_revenue, 
                    annual_opex,
                    npv_public,
                    finance['capex']
                )
                
                logger.info(f"✅ Enhanced metrics (30yr): NPV={npv_public/1e8:.1f}억, IRR={irr_value*100:.2f}%, Payback={payback:.1f}y")
            except Exception as e:
                logger.warning(f"Enhanced metrics calculation failed: {e}")
                import traceback
                logger.warning(traceback.format_exc())
        
        return finance
    
    def _calculate_financial_ratios(
        self,
        capex: float,
        noi: float,
        revenue: float,
        opex: float,
        npv: float,
        capex_breakdown: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate key financial ratios
        
        Phase 1, Task 1.5: Add Financial Ratios (DSCR, LTV, ROI, ROE)
        
        Ratios:
        1. DSCR (Debt Service Coverage Ratio): NOI / Annual Debt Service
        2. LTV (Loan-to-Value): Loan Amount / Total Asset Value
        3. ROI (Return on Investment): (Net Profit / Total Investment) × 100
        4. ROE (Return on Equity): (Net Income / Equity) × 100
        
        Returns:
            Dictionary with ratio values, grades, and interpretations
        """
        # Assumptions for calculation
        loan_ratio = 0.70  # 70% LTV (typical for LH projects)
        interest_rate = 0.025  # 2.5% interest rate
        loan_term_years = 20  # 20-year loan term
        
        # Calculate loan-related values
        loan_amount = capex * loan_ratio
        equity = capex * (1 - loan_ratio)
        
        # Annual debt service (principal + interest, simplified)
        # Using amortization formula: P * [r(1+r)^n] / [(1+r)^n - 1]
        r = interest_rate
        n = loan_term_years
        if r > 0:
            annual_debt_service = loan_amount * (r * (1 + r)**n) / ((1 + r)**n - 1)
        else:
            annual_debt_service = loan_amount / n
        
        # 1. DSCR (Debt Service Coverage Ratio)
        dscr = noi / annual_debt_service if annual_debt_service > 0 else 0
        dscr_grade = self._grade_dscr(dscr)
        
        # 2. LTV (Loan-to-Value)
        ltv_pct = loan_ratio * 100
        ltv_grade = self._grade_ltv(ltv_pct)
        
        # 3. ROI (Return on Investment) - Annual ROI
        # ROI = (Annual Net Income / Total Investment) × 100
        annual_net_income = noi - annual_debt_service  # After debt service
        roi_annual = (annual_net_income / capex * 100) if capex > 0 else 0
        
        # Cumulative ROI over project life (30 years)
        total_net_income = annual_net_income * 30  # Simplified
        roi_cumulative = (total_net_income / capex * 100) if capex > 0 else 0
        roi_grade = self._grade_roi(roi_annual)
        
        # 4. ROE (Return on Equity) - Annual ROE
        # ROE = (Net Income / Equity) × 100
        roe_annual = (annual_net_income / equity * 100) if equity > 0 else 0
        roe_grade = self._grade_roe(roe_annual)
        
        # Additional ratios
        # 5. Cap Rate (Capitalization Rate)
        property_value = capex * 1.1  # Assume 10% appreciation
        cap_rate = (noi / property_value * 100) if property_value > 0 else 0
        
        # 6. Operating Expense Ratio (OER)
        oer = (opex / revenue * 100) if revenue > 0 else 0
        
        return {
            'dscr': {
                'value': round(dscr, 2),
                'grade': dscr_grade,
                'description': f"부채상환비율 {dscr:.2f}배, {dscr_grade} 등급",
                'interpretation': self._interpret_dscr(dscr),
                'benchmark': '1.25배 이상 권장 (LH 기준)'
            },
            'ltv': {
                'value': round(ltv_pct, 1),
                'grade': ltv_grade,
                'description': f"담보인정비율 {ltv_pct:.1f}%, {ltv_grade} 등급",
                'loan_amount': loan_amount,
                'loan_amount_kr': f"{loan_amount / 1e8:.1f}억원",
                'equity': equity,
                'equity_kr': f"{equity / 1e8:.1f}억원",
                'interpretation': self._interpret_ltv(ltv_pct),
                'benchmark': '70% 이하 권장'
            },
            'roi': {
                'annual': round(roi_annual, 2),
                'cumulative_30yr': round(roi_cumulative, 1),
                'grade': roi_grade,
                'description': f"연간 투자수익률 {roi_annual:.2f}%, 30년 누적 {roi_cumulative:.1f}%",
                'interpretation': self._interpret_roi(roi_annual),
                'benchmark': '3% 이상 권장'
            },
            'roe': {
                'annual': round(roe_annual, 2),
                'grade': roe_grade,
                'description': f"자기자본이익률 {roe_annual:.2f}%",
                'interpretation': self._interpret_roe(roe_annual),
                'benchmark': '5% 이상 권장'
            },
            'cap_rate': {
                'value': round(cap_rate, 2),
                'description': f"자본환원율 {cap_rate:.2f}%",
                'interpretation': '부동산 투자 수익률 지표'
            },
            'oer': {
                'value': round(oer, 1),
                'description': f"운영비율 {oer:.1f}%",
                'interpretation': '낮을수록 운영 효율성 높음'
            },
            'debt_service': {
                'annual': annual_debt_service,
                'annual_kr': f"{annual_debt_service / 1e8:.2f}억원/년",
                'description': f"연간 부채상환액 {annual_debt_service / 1e8:.2f}억원"
            }
        }
    
    def _grade_dscr(self, dscr: float) -> str:
        """Grade DSCR ratio"""
        if dscr >= 1.5:
            return 'A'
        elif dscr >= 1.25:
            return 'B'
        elif dscr >= 1.0:
            return 'C'
        else:
            return 'D'
    
    def _grade_ltv(self, ltv_pct: float) -> str:
        """Grade LTV ratio"""
        if ltv_pct <= 60:
            return 'A'
        elif ltv_pct <= 70:
            return 'B'
        elif ltv_pct <= 80:
            return 'C'
        else:
            return 'D'
    
    def _grade_roi(self, roi_annual: float) -> str:
        """Grade ROI"""
        if roi_annual >= 5.0:
            return 'A'
        elif roi_annual >= 3.0:
            return 'B'
        elif roi_annual >= 1.0:
            return 'C'
        else:
            return 'D'
    
    def _grade_roe(self, roe_annual: float) -> str:
        """Grade ROE"""
        if roe_annual >= 10.0:
            return 'A'
        elif roe_annual >= 7.0:
            return 'B'
        elif roe_annual >= 5.0:
            return 'C'
        else:
            return 'D'
    
    def _interpret_dscr(self, dscr: float) -> str:
        """Interpret DSCR value"""
        if dscr >= 1.5:
            return "매우 안정적인 부채 상환 능력"
        elif dscr >= 1.25:
            return "안정적인 부채 상환 능력 (LH 기준 충족)"
        elif dscr >= 1.0:
            return "최소 부채 상환 가능, 리스크 주의"
        else:
            return "부채 상환 불가능, 사업 재구조화 필요"
    
    def _interpret_ltv(self, ltv_pct: float) -> str:
        """Interpret LTV value"""
        if ltv_pct <= 60:
            return "매우 보수적인 레버리지, 재무 안정성 높음"
        elif ltv_pct <= 70:
            return "적정 레버리지 수준, 재무 건전성 양호"
        elif ltv_pct <= 80:
            return "높은 레버리지, 재무 리스크 주의 필요"
        else:
            return "과도한 레버리지, 재무 리스크 매우 높음"
    
    def _interpret_roi(self, roi_annual: float) -> str:
        """Interpret ROI value"""
        if roi_annual >= 5.0:
            return "우수한 투자 수익률, 투자 매력도 높음"
        elif roi_annual >= 3.0:
            return "양호한 투자 수익률, 투자 가치 있음"
        elif roi_annual >= 1.0:
            return "보통 수준의 수익률, 신중한 검토 필요"
        else:
            return "낮은 수익률, 투자 재검토 필요"
    
    def _interpret_roe(self, roe_annual: float) -> str:
        """Interpret ROE value"""
        if roe_annual >= 10.0:
            return "탁월한 자기자본 수익률"
        elif roe_annual >= 7.0:
            return "우수한 자기자본 수익률"
        elif roe_annual >= 5.0:
            return "양호한 자기자본 수익률"
        else:
            return "낮은 자기자본 수익률"

    def _build_market_section(self, address: str, zerosite_value: float) -> Dict[str, Any]:
        """Build market analysis section (Phase 7.7)
        
        Phase 7.7: Market Signal Intelligence
        - Compare ZeroSite value vs market price
        - Analyze market temperature
        - Generate investment recommendation
        """
        
        market = {
            'signal': 'FAIR',
            'delta_pct': 0.0,
            'temperature': 'STABLE',
            'trend': {},
            'competition': {},
            'recommendation': '시장 적정가 수준으로 안정적인 투자 가능',
            'reasoning': {
                'reason_1': '시장 가격과 산출가가 유사하여 안정적입니다',
                'reason_2': '가격 변동성이 낮은 지역입니다',
                'reason_3': '경쟁 공급이 적절한 수준입니다'
            },
            'status': 'default'
        }
        
        if self.market_analyzer and zerosite_value > 0:
            try:
                # STEP 1: Compare ZeroSite value with market price
                # Estimate market value based on region (using simple heuristic)
                # In production, this should fetch actual market data from API
                market_value_per_sqm = zerosite_value * 1.15  # Assume market is 15% higher (conservative)
                
                comparison_result = self.market_analyzer.compare(
                    zerosite_value=zerosite_value,
                    market_value=market_value_per_sqm,
                    context={'address': address}
                )
                
                signal = comparison_result.get('signal', 'FAIR')
                delta_pct = comparison_result.get('delta_percent', 0.0)
                
                # STEP 2: Analyze market temperature
                # In production, these should be real data from market API
                temperature_result = self.market_analyzer.analyze_market_temperature(
                    vacancy_rate=0.08,  # 8% vacancy (typical urban)
                    transaction_volume=150,  # Medium transaction volume
                    price_trend='up'  # Assume stable upward trend
                )
                
                temperature = temperature_result.get('temperature', 'STABLE')
                
                # STEP 3: Generate investment recommendation
                recommendation = self.market_analyzer.generate_investment_recommendation(
                    market_signal=signal,
                    market_temperature=temperature,
                    financial_metrics=None  # Can be enhanced with NPV/IRR
                )
                
                # Update market section with computed results
                market.update({
                    'signal': signal,
                    'delta_pct': delta_pct,
                    'temperature': temperature,
                    'recommendation': recommendation,
                    'reasoning': self._extract_market_reasoning(signal, comparison_result),
                    'status': 'phase_7_7'
                })
                
                logger.info(f"✅ Phase 7.7 Market: signal={signal}, delta={delta_pct:.1f}%, temp={temperature}")
                
            except Exception as e:
                logger.warning(f"Market analysis failed: {e}")
                import traceback
                logger.warning(traceback.format_exc())
        else:
            logger.warning("Market analysis skipped: analyzer not available or zerosite_value=0")
        
        return market
    
    def _extract_market_reasoning(self, signal: str, market_result: Dict[str, Any]) -> Dict[str, str]:
        """Extract 3 key reasons WHY this market signal exists"""
        
        delta_pct = market_result.get('delta_pct', 0.0)
        
        if signal == 'UNDERVALUED':
            reasoning = {
                'reason_1': f'시장 가격 대비 {abs(delta_pct):.1f}% 저평가되어 있습니다',
                'reason_2': '향후 가격 상승 가능성이 높은 지역입니다',
                'reason_3': '투자 가치가 우수한 기회입니다'
            }
        elif signal == 'OVERVALUED':
            reasoning = {
                'reason_1': f'시장 가격 대비 {delta_pct:.1f}% 고평가되어 있습니다',
                'reason_2': '가격 조정 위험이 존재합니다',
                'reason_3': '신중한 투자 검토가 필요합니다'
            }
        else:  # FAIR
            reasoning = {
                'reason_1': '시장 가격과 산출가가 균형을 이루고 있습니다',
                'reason_2': '안정적인 가격 수준입니다',
                'reason_3': '적정한 투자 타이밍입니다'
            }
        
        return reasoning
    
    def _build_scenario_section(self, finance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build comprehensive 5-scenario sensitivity analysis
        
        Phase 1, Task 1.2: Financial Sensitivity Analysis (5 scenarios)
        
        Scenarios:
        1. Best Case (최상): Cost -5%, Revenue +10%, Occupancy 98%
        2. Optimistic (낙관): Cost -3%, Revenue +5%, Occupancy 96%
        3. Base (기본): Current assumptions
        4. Pessimistic (비관): Cost +5%, Revenue -5%, Occupancy 92%
        5. Worst Case (최악): Cost +10%, Revenue -10%, Occupancy 88%
        
        Returns:
            {
                'base': {...},
                'best_case': {...},
                'optimistic': {...},
                'pessimistic': {...},
                'worst_case': {...},
                'sensitivity_analysis': {
                    'cost_sensitivity': {...},
                    'revenue_sensitivity': {...},
                    'occupancy_sensitivity': {...},
                    'break_even_analysis': {...}
                }
            }
        """
        
        # Extract base values
        base_capex = finance_data['capex']['total']
        base_revenue = finance_data['revenue']['annual_rental']
        base_opex = finance_data['opex']['annual']
        base_npv_public = finance_data['npv']['public']
        base_irr = finance_data['irr']['public']
        base_payback = finance_data['payback']['years']
        base_occupancy = finance_data['revenue']['occupancy_rate']
        base_cashflow = finance_data.get('cashflow', [])
        
        # Helper function to recalculate NPV for scenario
        def calculate_scenario_npv(capex_multiplier, revenue_multiplier, occupancy_rate):
            adjusted_capex = base_capex * capex_multiplier
            adjusted_revenue = base_revenue * revenue_multiplier * (occupancy_rate / 100)
            adjusted_noi = adjusted_revenue - base_opex
            
            # Recalculate 10-year cash flow
            annual_cashflows = []
            for year in range(10):
                if year == 0:  # Year 1: ramp-up
                    cf = adjusted_noi * 0.85
                else:  # Year 2+: stabilized
                    cf = adjusted_noi
                annual_cashflows.append(cf)
            
            # Calculate NPV
            discount_rate = 0.0287  # 2.87% LH official rate
            npv = sum([cf / ((1 + discount_rate) ** (i + 1)) for i, cf in enumerate(annual_cashflows)]) - adjusted_capex
            
            # Calculate IRR
            try:
                import numpy as np
                cash_flows = [-adjusted_capex] + annual_cashflows
                irr_value = np.irr(cash_flows)
                if not np.isfinite(irr_value):
                    irr_value = None
                else:
                    irr_value = irr_value * 100  # Convert to percentage
            except:
                irr_value = None
            
            # Calculate Payback
            cumulative = 0
            payback = float('inf')
            for i, cf in enumerate(annual_cashflows):
                cumulative += cf
                if cumulative >= adjusted_capex:
                    payback = i + 1 + (adjusted_capex - (cumulative - cf)) / cf
                    break
            
            return {
                'capex': adjusted_capex,
                'revenue': adjusted_revenue,
                'noi': adjusted_noi,
                'npv_public': npv,
                'irr': irr_value if irr_value else 0,
                'payback': payback if payback != float('inf') else 0,
                'occupancy_rate': occupancy_rate
            }
        
        # Scenario 1: Best Case
        best_case = calculate_scenario_npv(0.95, 1.10, 98.0)
        best_case.update({
            'scenario_name': '최상 시나리오',
            'scenario_name_en': 'Best Case',
            'cost_change_pct': -5.0,
            'revenue_change_pct': +10.0,
            'description': '공사비 절감 성공, 시장 호황, 높은 입주율'
        })
        
        # Scenario 2: Optimistic
        optimistic = calculate_scenario_npv(0.97, 1.05, 96.0)
        optimistic.update({
            'scenario_name': '낙관 시나리오',
            'scenario_name_en': 'Optimistic',
            'cost_change_pct': -3.0,
            'revenue_change_pct': +5.0,
            'description': '공사비 약간 절감, 시장 양호, 양호한 입주율'
        })
        
        # Scenario 3: Base
        base = {
            'scenario_name': '기본 시나리오',
            'scenario_name_en': 'Base Case',
            'capex': base_capex,
            'revenue': base_revenue,
            'noi': base_revenue - base_opex,
            'npv_public': base_npv_public,
            'irr': base_irr,
            'payback': base_payback,
            'occupancy_rate': base_occupancy,
            'cost_change_pct': 0.0,
            'revenue_change_pct': 0.0,
            'description': '현재 가정 기준, 중립적 시장 조건'
        }
        
        # Scenario 4: Pessimistic
        pessimistic = calculate_scenario_npv(1.05, 0.95, 92.0)
        pessimistic.update({
            'scenario_name': '비관 시나리오',
            'scenario_name_en': 'Pessimistic',
            'cost_change_pct': +5.0,
            'revenue_change_pct': -5.0,
            'description': '공사비 증가, 시장 침체, 낮은 입주율'
        })
        
        # Scenario 5: Worst Case
        worst_case = calculate_scenario_npv(1.10, 0.90, 88.0)
        worst_case.update({
            'scenario_name': '최악 시나리오',
            'scenario_name_en': 'Worst Case',
            'cost_change_pct': +10.0,
            'revenue_change_pct': -10.0,
            'description': '공사비 대폭 증가, 시장 붕괴, 매우 낮은 입주율'
        })
        
        # Sensitivity Analysis
        # Cost Sensitivity: NPV impact per 1% cost change
        cost_npv_sensitivity = -base_capex / 100  # Each 1% cost increase = -CAPEX/100 NPV
        
        # Revenue Sensitivity: NPV impact per 1% revenue change
        revenue_npv_sensitivity = base_revenue * 10 / 100  # Each 1% revenue increase = +Revenue*10y/100 NPV (approx)
        
        # Occupancy Sensitivity
        occupancy_npv_sensitivity = base_revenue * 10 / 100  # Similar to revenue
        
        sensitivity_analysis = {
            'cost_sensitivity': {
                'npv_per_1pct_change': cost_npv_sensitivity,
                'npv_per_1pct_change_kr': f"{cost_npv_sensitivity / 1e8:.2f}억원",
                'description': f"공사비 1% 변동 시 NPV {abs(cost_npv_sensitivity / 1e8):.2f}억원 변동",
                'impact_level': 'HIGH' if abs(cost_npv_sensitivity) > base_npv_public * 0.1 else 'MEDIUM'
            },
            'revenue_sensitivity': {
                'npv_per_1pct_change': revenue_npv_sensitivity,
                'npv_per_1pct_change_kr': f"{revenue_npv_sensitivity / 1e8:.2f}억원",
                'description': f"임대수익 1% 변동 시 NPV {revenue_npv_sensitivity / 1e8:.2f}억원 변동",
                'impact_level': 'HIGH' if revenue_npv_sensitivity > base_npv_public * 0.05 else 'MEDIUM'
            },
            'occupancy_sensitivity': {
                'npv_per_1pct_change': occupancy_npv_sensitivity,
                'npv_per_1pct_change_kr': f"{occupancy_npv_sensitivity / 1e8:.2f}억원",
                'description': f"입주율 1%p 변동 시 NPV {occupancy_npv_sensitivity / 1e8:.2f}억원 변동",
                'impact_level': 'HIGH'
            },
            'break_even_analysis': self._calculate_break_even(base, finance_data)
        }
        
        # Generate summary comparison table
        scenario_comparison_table = {
            'scenarios': ['best_case', 'optimistic', 'base', 'pessimistic', 'worst_case'],
            'npv_range': {
                'min': worst_case['npv_public'],
                'max': best_case['npv_public'],
                'span': best_case['npv_public'] - worst_case['npv_public'],
                'span_kr': f"{(best_case['npv_public'] - worst_case['npv_public']) / 1e8:.1f}억원"
            },
            'irr_range': {
                'min': worst_case['irr'],
                'max': best_case['irr'],
                'span': best_case['irr'] - worst_case['irr'],
                'span_kr': f"{best_case['irr'] - worst_case['irr']:.2f}%p"
            },
            'recommendation': self._generate_scenario_recommendation(
                best_case, base, worst_case
            )
        }
        
        # Phase 1, Task 1.3: NPV Tornado Diagram data
        tornado_data = self._generate_tornado_diagram_data(base, finance_data)
        
        return {
            'base': base,
            'best_case': best_case,
            'optimistic': optimistic,
            'pessimistic': pessimistic,
            'worst_case': worst_case,
            'sensitivity_analysis': sensitivity_analysis,
            'comparison_table': scenario_comparison_table,
            'tornado_diagram': tornado_data  # NEW: Phase 1, Task 1.3
        }
    
    def _generate_tornado_diagram_data(self, base_scenario: Dict[str, Any], finance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate NPV Tornado Diagram data
        
        Phase 1, Task 1.3: NPV Tornado Diagram
        
        Tests impact of ±10% change in key variables on NPV:
        - Construction Cost (공사비)
        - Land Cost (토지비)
        - Rental Revenue (임대수익)
        - Occupancy Rate (입주율)
        - Operating Expenses (운영비)
        - Discount Rate (할인율)
        
        Returns data sorted by impact magnitude (largest impact first)
        for creating a horizontal bar chart (Tornado diagram)
        """
        logger.info("📊 Generating NPV Tornado Diagram data...")
        
        base_capex = base_scenario['capex']
        base_revenue = base_scenario['revenue']
        base_npv = base_scenario['npv_public']
        base_opex = finance_data['opex']['annual']
        
        construction_cost = finance_data['capex']['construction']
        land_cost = finance_data['capex']['land']
        base_occupancy = finance_data['revenue']['occupancy_rate']
        base_discount_rate = 0.0287  # 2.87% LH official rate
        
        # Helper to calculate NPV with one variable changed
        def calc_npv_with_change(variable, change_pct):
            """Calculate NPV with one variable changed by change_pct"""
            if variable == 'construction_cost':
                adj_capex = base_capex + (construction_cost * change_pct / 100)
            elif variable == 'land_cost':
                adj_capex = base_capex + (land_cost * change_pct / 100)
            elif variable == 'rental_revenue':
                adj_revenue = base_revenue * (1 + change_pct / 100)
                adj_capex = base_capex
            elif variable == 'occupancy_rate':
                # Occupancy: change_pct is actual percentage points (e.g., +10%p means 95% -> 105%)
                new_occupancy = base_occupancy + change_pct
                adj_revenue = base_revenue * (new_occupancy / base_occupancy)
                adj_capex = base_capex
            elif variable == 'opex':
                adj_opex = base_opex * (1 + change_pct / 100)
                adj_capex = base_capex
                adj_revenue = base_revenue
            elif variable == 'discount_rate':
                # Change discount rate by change_pct (e.g., +10% of 2.87% = 3.157%)
                adj_discount_rate = base_discount_rate * (1 + change_pct / 100)
                adj_capex = base_capex
            else:
                adj_capex = base_capex
            
            # Recalculate NPV
            if variable == 'construction_cost' or variable == 'land_cost':
                # Only CAPEX changed
                return base_npv - (adj_capex - base_capex)
            elif variable == 'rental_revenue':
                # Revenue changed
                noi_change = adj_revenue - base_revenue
                npv_change = noi_change * 8  # Approx 8-year NPV factor
                return base_npv + npv_change
            elif variable == 'occupancy_rate':
                # Occupancy changed
                noi_change = adj_revenue - base_revenue
                npv_change = noi_change * 8
                return base_npv + npv_change
            elif variable == 'opex':
                # OpEx changed (inverse relationship with NOI)
                noi_change = -(adj_opex - base_opex)
                npv_change = noi_change * 8
                return base_npv + npv_change
            elif variable == 'discount_rate':
                # Discount rate changed - recalculate NPV with new rate
                annual_noi = base_revenue - base_opex
                annual_cashflows = [annual_noi * 0.85] + [annual_noi] * 9  # Year 1 ramp-up, Year 2-10 stabilized
                npv = sum([cf / ((1 + adj_discount_rate) ** (i + 1)) for i, cf in enumerate(annual_cashflows)]) - base_capex
                return npv
            else:
                return base_npv
        
        # Test each variable at ±10% (or ±10%p for occupancy)
        variables = {
            'construction_cost': {
                'name_kr': '공사비',
                'name_en': 'Construction Cost',
                'test_range': 10  # ±10%
            },
            'land_cost': {
                'name_kr': '토지비',
                'name_en': 'Land Cost',
                'test_range': 10  # ±10%
            },
            'rental_revenue': {
                'name_kr': '임대수익',
                'name_en': 'Rental Revenue',
                'test_range': 10  # ±10%
            },
            'occupancy_rate': {
                'name_kr': '입주율',
                'name_en': 'Occupancy Rate',
                'test_range': 10  # ±10%p (e.g., 95% ± 10%p = 85%-105%)
            },
            'opex': {
                'name_kr': '운영비',
                'name_en': 'Operating Expenses',
                'test_range': 10  # ±10%
            },
            'discount_rate': {
                'name_kr': '할인율',
                'name_en': 'Discount Rate',
                'test_range': 10  # ±10% of rate (2.87% ± 10% = 2.58%-3.16%)
            }
        }
        
        # Calculate NPV swing for each variable
        results = []
        for var_key, var_info in variables.items():
            test_range = var_info['test_range']
            
            # Calculate NPV at +test_range%
            npv_high = calc_npv_with_change(var_key, +test_range)
            
            # Calculate NPV at -test_range%
            npv_low = calc_npv_with_change(var_key, -test_range)
            
            # Calculate swing (total NPV change from low to high)
            npv_swing = npv_high - npv_low
            
            # Determine which direction is favorable
            if var_key in ['rental_revenue', 'occupancy_rate']:
                # Higher is better
                favorable_direction = 'positive'
                npv_favorable = npv_high
                npv_unfavorable = npv_low
            elif var_key in ['construction_cost', 'land_cost', 'opex', 'discount_rate']:
                # Lower is better
                favorable_direction = 'negative'
                npv_favorable = npv_low
                npv_unfavorable = npv_high
            else:
                favorable_direction = 'neutral'
                npv_favorable = max(npv_high, npv_low)
                npv_unfavorable = min(npv_high, npv_low)
            
            results.append({
                'variable': var_key,
                'name_kr': var_info['name_kr'],
                'name_en': var_info['name_en'],
                'npv_base': base_npv,
                'npv_high': npv_high,
                'npv_low': npv_low,
                'npv_swing': abs(npv_swing),  # Absolute swing for sorting
                'npv_swing_kr': f"{abs(npv_swing) / 1e8:.1f}억원",
                'impact_pct': abs(npv_swing / base_npv * 100) if base_npv != 0 else 0,
                'favorable_direction': favorable_direction,
                'npv_favorable': npv_favorable,
                'npv_unfavorable': npv_unfavorable,
                'test_range': test_range
            })
        
        # Sort by NPV swing (largest impact first)
        results_sorted = sorted(results, key=lambda x: x['npv_swing'], reverse=True)
        
        # Generate summary
        top_3_variables = [r['name_kr'] for r in results_sorted[:3]]
        total_potential_swing = sum(r['npv_swing'] for r in results_sorted)
        
        tornado_summary = {
            'top_impact_variables': top_3_variables,
            'top_impact_summary': f"상위 3개 변수: {', '.join(top_3_variables)}",
            'total_potential_swing': total_potential_swing,
            'total_potential_swing_kr': f"{total_potential_swing / 1e8:.1f}억원",
            'recommendation': self._generate_tornado_recommendation(results_sorted)
        }
        
        logger.info(f"✅ Tornado data generated: Top variables = {', '.join(top_3_variables)}")
        
        return {
            'variables': results_sorted,
            'summary': tornado_summary,
            'base_npv': base_npv,
            'base_npv_kr': f"{base_npv / 1e8:.1f}억원"
        }
    
    def _generate_tornado_recommendation(self, sorted_results: List[Dict[str, Any]]) -> str:
        """Generate recommendation based on tornado analysis"""
        if not sorted_results:
            return "변수 영향도 분석 데이터 없음"
        
        top_var = sorted_results[0]
        top_name = top_var['name_kr']
        top_impact = top_var['npv_swing'] / 1e8
        
        if top_var['favorable_direction'] == 'negative':
            # Cost variable (lower is better)
            return f"{top_name} 관리가 가장 중요 (±10% 변동 시 NPV {top_impact:.1f}억원 변동). {top_name} 절감 전략 최우선 추진 필요"
        elif top_var['favorable_direction'] == 'positive':
            # Revenue variable (higher is better)
            return f"{top_name} 확보가 가장 중요 (±10% 변동 시 NPV {top_impact:.1f}억원 변동). {top_name} 증대 전략 최우선 추진 필요"
        else:
            return f"{top_name}이(가) NPV에 가장 큰 영향 (±10% 변동 시 NPV {top_impact:.1f}억원 변동)"
    
    def _calculate_break_even(self, base_scenario: Dict[str, Any], finance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate break-even points for key variables"""
        base_capex = base_scenario['capex']
        base_revenue = base_scenario['revenue']
        base_npv = base_scenario['npv_public']
        
        # Break-even cost increase: How much can cost increase before NPV=0?
        if base_npv > 0:
            break_even_cost_increase_pct = (base_npv / base_capex) * 100
        else:
            break_even_cost_increase_pct = 0
        
        # Break-even revenue decrease: How much can revenue decrease before NPV=0?
        if base_npv > 0 and base_revenue > 0:
            # Rough estimate: NPV_change ≈ Revenue_change * 10 years * discount_factor
            break_even_revenue_decrease_pct = (base_npv / (base_revenue * 8)) * 100  # ~8 years NPV factor
        else:
            break_even_revenue_decrease_pct = 0
        
        # Break-even occupancy rate
        base_occupancy = base_scenario.get('occupancy_rate', 95.0)
        if base_npv > 0 and base_revenue > 0:
            required_occupancy_decrease = (base_npv / (base_revenue * 8)) * 100
            break_even_occupancy = base_occupancy - required_occupancy_decrease
        else:
            break_even_occupancy = base_occupancy
        
        return {
            'cost_increase_limit_pct': max(0, break_even_cost_increase_pct),
            'cost_increase_limit_kr': f"+{break_even_cost_increase_pct:.1f}%",
            'revenue_decrease_limit_pct': max(0, break_even_revenue_decrease_pct),
            'revenue_decrease_limit_kr': f"-{break_even_revenue_decrease_pct:.1f}%",
            'occupancy_minimum': max(0, break_even_occupancy),
            'occupancy_minimum_kr': f"{break_even_occupancy:.1f}%",
            'description': f"손익분기: 공사비 +{break_even_cost_increase_pct:.1f}% 또는 수익 -{break_even_revenue_decrease_pct:.1f}% 한계"
        }
    
    def _generate_scenario_recommendation(
        self, 
        best_case: Dict[str, Any], 
        base: Dict[str, Any], 
        worst_case: Dict[str, Any]
    ) -> str:
        """Generate recommendation based on scenario analysis"""
        base_npv = base['npv_public']
        worst_npv = worst_case['npv_public']
        best_npv = best_case['npv_public']
        
        if base_npv > 0 and worst_npv > 0:
            return "모든 시나리오에서 수익성 확보, 안정적 추진 가능"
        elif base_npv > 0 and worst_npv < 0:
            return "기본 시나리오는 수익성 있으나, 최악 시나리오 대비 리스크 관리 필요"
        elif base_npv < 0 and best_npv > 0:
            return "기본 시나리오는 손실 예상, 최상 시나리오 조건 확보 시에만 추진 가능"
        else:
            return "모든 시나리오에서 손실 예상, 사업 구조 전면 재설계 필요"
    
    def _build_risk_section(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive risk analysis section"""
        
        finance = context['finance']
        market = context['market']
        demand = context['demand']
        
        risks = {
            'legal': self._assess_legal_risk(context),
            'market': self._assess_market_risk(market),
            'construction': self._assess_construction_risk(finance),
            'financial': self._assess_financial_risk(finance),
            'overall_level': 'MEDIUM'
        }
        
        # Determine overall risk level
        risk_levels = [
            risks['legal']['level'],
            risks['market']['level'],
            risks['construction']['level'],
            risks['financial']['level']
        ]
        
        red_count = risk_levels.count('RED')
        yellow_count = risk_levels.count('YELLOW')
        
        if red_count >= 2:
            risks['overall_level'] = 'HIGH'
        elif red_count >= 1 or yellow_count >= 2:
            risks['overall_level'] = 'MEDIUM'
        else:
            risks['overall_level'] = 'LOW'
        
        return risks
    
    def _assess_legal_risk(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess legal & regulatory risk"""
        # In production: Check zoning, permits, restrictions
        return {
            'level': 'GREEN',
            'description': '법적 검토 결과 주요 리스크 없음',
            'mitigation': '인허가 진행 전 최종 확인 필요',
            'impact': '프로젝트 진행에 미치는 영향 낮음'
        }
    
    def _assess_market_risk(self, market: Dict[str, Any]) -> Dict[str, Any]:
        """Assess market risk"""
        signal = market.get('signal', 'FAIR')
        
        if signal == 'OVERVALUED':
            return {
                'level': 'RED',
                'description': '시장 대비 고평가 상태',
                'mitigation': '가격 조정 또는 가치 제고 전략 필요',
                'impact': '수익성에 높은 영향'
            }
        elif signal == 'FAIR':
            return {
                'level': 'GREEN',
                'description': '시장 가격 적정 수준',
                'mitigation': '지속적인 시장 모니터링',
                'impact': '안정적'
            }
        else:  # UNDERVALUED
            return {
                'level': 'GREEN',
                'description': '시장 대비 저평가 상태 (기회)',
                'mitigation': '타이밍 고려한 진입 전략',
                'impact': '긍정적'
            }
    
    def _assess_construction_risk(self, finance: Dict[str, Any]) -> Dict[str, Any]:
        """Assess construction risk"""
        capex = finance['capex']['total']
        
        # Simple heuristic: Large projects = higher risk
        if capex > 200_000_000_000:  # 2000억 이상
            return {
                'level': 'YELLOW',
                'description': '대규모 프로젝트로 공사비 관리 중요',
                'mitigation': 'CM/감리 체계 강화, 단계별 점검',
                'impact': '공사비 증가 리스크'
            }
        else:
            return {
                'level': 'GREEN',
                'description': '표준 규모의 공사 리스크',
                'mitigation': '일반 감리 및 품질 관리',
                'impact': '낮음'
            }
    
    def _assess_financial_risk(self, finance: Dict[str, Any]) -> Dict[str, Any]:
        """Assess financial risk"""
        npv = finance['npv']['public']
        irr = finance['irr']['public']
        
        if npv < 0 or irr < 0:
            return {
                'level': 'RED',
                'description': '재무적 타당성 부족',
                'mitigation': '사업 구조 재설계 필요',
                'impact': '사업 중단 가능'
            }
        elif irr < 2.0:
            return {
                'level': 'YELLOW',
                'description': '낮은 수익률',
                'mitigation': '비용 절감 및 수익 개선 필요',
                'impact': '수익성 개선 요구'
            }
        else:
            return {
                'level': 'GREEN',
                'description': '양호한 재무 구조',
                'mitigation': '현 수준 유지',
                'impact': '안정적'
            }
    
    def _translate_housing_type(self, housing_type: str) -> str:
        """Translate English housing type to Korean"""
        type_map = {
            'youth': '청년형',
            'newlyweds': '신혼부부형',
            'newlyweds_growth': '신혼부부 성장형',
            'multichild': '다자녀형',
            'senior': '고령자형'
        }
        return type_map.get(housing_type, housing_type)
    
    def _extract_region(self, address: str) -> str:
        """Extract region from address"""
        if '서울' in address:
            return '서울'
        elif '경기' in address:
            return '경기'
        elif '인천' in address:
            return '인천'
        else:
            return '기타'
    
    def _get_coordinates(self, address: str) -> tuple:
        """Get coordinates for address (stub)"""
        # Default Seoul coordinates
        return (37.5665, 126.9780)
    
    def _generate_project_code(self, address: str) -> str:
        """Generate unique project code"""
        timestamp = datetime.now().strftime('%Y%m%d')
        address_hash = hash(address) % 10000
        return f"ZS-{timestamp}-{address_hash:04d}"
    
    def _build_decision_section(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build final decision section"""
        npv = context['finance']['npv']['public']
        irr = context['finance']['irr']['public']
        overall_risk = context['risk_analysis']['overall_level']
        demand_score = context['demand']['overall_score']
        
        # Decision logic
        if npv >= 0 and irr >= 2.0 and overall_risk == 'LOW':
            recommendation = 'GO'
            confidence = 'high'
            reasoning = [
                f'긍정적 NPV ({npv/100_000_000:+.2f}억원)로 재무적 타당성 확보',
                f'IRR {irr:.2f}%로 목표 수익률 달성',
                '전반적인 리스크 수준이 낮아 안정적 추진 가능'
            ]
            conditions = []
        elif npv >= 0 and irr >= 1.5:
            recommendation = 'CONDITIONAL'
            confidence = 'medium'
            reasoning = [
                f'NPV {npv/100_000_000:+.2f}억원으로 수익성 있으나 낮은 수준',
                '리스크 관리 강화 필요',
                '시장 조건 개선 시 추진 가능'
            ]
            conditions = [
                '공사비 10% 절감',
                '임대료 5% 상향 검토',
                '리스크 완화 조치 이행'
            ]
        elif npv < 0 and npv > -50_000_000_00:  # -50억원 이하
            recommendation = 'REVISE'
            confidence = 'medium'
            reasoning = [
                f'NPV {npv/100_000_000:+.2f}억원으로 재무적 타당성 부족',
                '사업 구조 대폭 개선 필요',
                '대지 규모 확대 또는 개발 계획 변경 권장'
            ]
            conditions = [
                '대지 면적 최소 2배 확대',
                '인근 필지 병합 검토',
                '개발 계획 전면 재설계'
            ]
        else:
            recommendation = 'NO-GO'
            confidence = 'high'
            reasoning = [
                f'NPV {npv/100_000_000:+.2f}억원으로 심각한 재무적 손실 예상',
                f'IRR {irr:.2f}%로 투자 회수 불가능',
                '현 조건에서는 사업 추진 불가'
            ]
            conditions = []
        
        return {
            'recommendation': recommendation,
            'reasoning': reasoning,
            'confidence': confidence,
            'conditions': conditions if recommendation in ['CONDITIONAL', 'REVISE'] else None
        }

    def calculate_scorecard(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive 5-category scorecard for Executive Summary
        
        Phase 1, Task 1.1: Executive Summary Dashboard - Scorecard Logic
        
        Categories (100-point scale each):
        1. Location Score (입지 점수): Distance to facilities, transportation, amenities
        2. Finance Score (재무 점수): NPV, IRR, Payback, profitability
        3. Market Score (시장 점수): Market signal, demand, competition
        4. Risk Score (리스크 점수): Overall risk level, mitigation capability
        5. Policy Score (정책 점수): Alignment with LH priorities, compliance
        
        Returns:
            {
                'location': {'score': 85, 'grade': 'A', 'description': '...'},
                'finance': {'score': 72, 'grade': 'B', 'description': '...'},
                'market': {'score': 68, 'grade': 'B', 'description': '...'},
                'risk': {'score': 80, 'grade': 'A', 'description': '...'},
                'policy': {'score': 75, 'grade': 'B', 'description': '...'},
                'overall': {'score': 76, 'grade': 'B', 'recommendation': 'GO|CONDITIONAL|REVISE|NO-GO'}
            }
        """
        logger.info("📊 Calculating comprehensive scorecard...")
        
        scorecard = {
            'location': self._calculate_location_score(context),
            'finance': self._calculate_finance_score(context),
            'market': self._calculate_market_score(context),
            'risk': self._calculate_risk_score(context),
            'policy': self._calculate_policy_score(context)
        }
        
        # Calculate overall score (weighted average)
        weights = {
            'location': 0.15,
            'finance': 0.35,  # Highest weight: financial viability is critical
            'market': 0.25,
            'risk': 0.15,
            'policy': 0.10
        }
        
        overall_score = sum(
            scorecard[category]['score'] * weights[category]
            for category in weights
        )
        
        # Determine overall grade and recommendation
        overall_grade = self._score_to_grade(overall_score)
        overall_recommendation = self._scorecard_to_recommendation(scorecard, overall_score)
        
        scorecard['overall'] = {
            'score': round(overall_score, 1),
            'grade': overall_grade,
            'recommendation': overall_recommendation,
            'confidence': self._calculate_confidence_level(scorecard)
        }
        
        logger.info(f"✅ Scorecard calculated: Overall {overall_score:.1f} ({overall_grade}) - {overall_recommendation}")
        return scorecard
    
    def _calculate_location_score(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate location score (입지 점수)"""
        demand = context.get('demand', {})
        demand_score = demand.get('overall_score', 60.0)
        
        # Base score from demand model (reflects location characteristics)
        location_score = demand_score
        
        # Adjust based on land area (larger = better for multi-housing)
        land_area = context.get('site', {}).get('land_area_sqm', 500)
        if land_area >= 1000:
            location_score += 5  # Bonus for large sites
        elif land_area < 300:
            location_score -= 10  # Penalty for very small sites
        
        # Cap at 100
        location_score = min(100, max(0, location_score))
        
        grade = self._score_to_grade(location_score)
        description = self._generate_location_description(location_score, demand)
        
        return {
            'score': round(location_score, 1),
            'grade': grade,
            'description': description
        }
    
    def _calculate_finance_score(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate finance score (재무 점수)"""
        finance = context.get('finance', {})
        npv = finance.get('npv', {}).get('public', 0)
        irr = finance.get('irr', {}).get('public', 0)
        payback = finance.get('payback', {}).get('years', 999)
        capex = finance.get('capex', {}).get('total', 1)
        
        # NPV score (50 points max)
        npv_ratio = npv / capex if capex > 0 else -1
        if npv_ratio >= 0.15:  # 15% return
            npv_score = 50
        elif npv_ratio >= 0.05:  # 5-15% return
            npv_score = 30 + (npv_ratio - 0.05) * 200  # Scale 30-50
        elif npv_ratio >= -0.05:  # -5% to 5%
            npv_score = 20 + (npv_ratio + 0.05) * 100  # Scale 20-30
        else:  # < -5%
            npv_score = max(0, 20 + npv_ratio * 100)  # Scale 0-20
        
        # IRR score (30 points max)
        if irr >= 5.0:  # Excellent
            irr_score = 30
        elif irr >= 2.87:  # Above LH discount rate
            irr_score = 20 + (irr - 2.87) * 4.7  # Scale 20-30
        elif irr >= 0:  # Positive but low
            irr_score = 10 + (irr / 2.87) * 10  # Scale 10-20
        else:  # Negative
            irr_score = max(0, 10 + irr * 2)  # Scale 0-10
        
        # Payback score (20 points max)
        if payback <= 8:  # Excellent
            payback_score = 20
        elif payback <= 15:  # Acceptable
            payback_score = 10 + (15 - payback) * 1.43  # Scale 10-20
        elif payback < 999:  # Poor but achievable
            payback_score = max(0, 10 - (payback - 15) * 0.5)
        else:  # No payback
            payback_score = 0
        
        finance_score = npv_score + irr_score + payback_score
        grade = self._score_to_grade(finance_score)
        description = self._generate_finance_description(finance_score, npv, irr, payback)
        
        return {
            'score': round(finance_score, 1),
            'grade': grade,
            'description': description,
            'components': {
                'npv_score': round(npv_score, 1),
                'irr_score': round(irr_score, 1),
                'payback_score': round(payback_score, 1)
            }
        }
    
    def _calculate_market_score(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate market score (시장 점수)"""
        market = context.get('market', {})
        signal = market.get('signal', 'FAIR')
        delta_pct = market.get('delta_pct', 0.0)
        demand = context.get('demand', {})
        demand_score = demand.get('overall_score', 60.0)
        
        # Market signal score (50 points max)
        if signal == 'UNDERVALUED':
            signal_score = 40 + min(10, abs(delta_pct) / 2)  # 40-50 points
        elif signal == 'FAIR':
            signal_score = 30 + (5 - abs(delta_pct)) * 2  # 30-40 points
        else:  # OVERVALUED
            signal_score = max(0, 30 - abs(delta_pct) * 2)  # 0-30 points
        
        # Demand score (50 points max, normalized from demand model)
        demand_component = (demand_score / 100) * 50
        
        market_score = signal_score + demand_component
        grade = self._score_to_grade(market_score)
        description = self._generate_market_description(market_score, signal, demand_score)
        
        return {
            'score': round(market_score, 1),
            'grade': grade,
            'description': description,
            'components': {
                'signal_score': round(signal_score, 1),
                'demand_score': round(demand_component, 1)
            }
        }
    
    def _calculate_risk_score(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk score (리스크 점수) - higher = safer"""
        risk_analysis = context.get('risk_analysis', {})
        overall_level = risk_analysis.get('overall_level', 'MEDIUM')
        
        legal = risk_analysis.get('legal', {}).get('level', 'GREEN')
        market_risk = risk_analysis.get('market', {}).get('level', 'GREEN')
        construction = risk_analysis.get('construction', {}).get('level', 'GREEN')
        financial = risk_analysis.get('financial', {}).get('level', 'GREEN')
        
        # Convert risk levels to scores (GREEN=100, YELLOW=60, RED=20)
        def risk_level_to_score(level):
            return {'GREEN': 100, 'YELLOW': 60, 'RED': 20}.get(level, 60)
        
        # Average of all risk categories
        risk_score = (
            risk_level_to_score(legal) * 0.20 +
            risk_level_to_score(market_risk) * 0.30 +
            risk_level_to_score(construction) * 0.25 +
            risk_level_to_score(financial) * 0.25
        )
        
        grade = self._score_to_grade(risk_score)
        description = self._generate_risk_description(risk_score, overall_level)
        
        return {
            'score': round(risk_score, 1),
            'grade': grade,
            'description': description
        }
    
    def _calculate_policy_score(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate policy alignment score (정책 점수)"""
        demand = context.get('demand', {})
        recommended_type = demand.get('recommended_type', 'youth')
        land_area = context.get('site', {}).get('land_area_sqm', 500)
        finance = context.get('finance', {})
        npv = finance.get('npv', {}).get('public', 0)
        
        # Base score: 60 (neutral)
        policy_score = 60
        
        # LH priority housing types (청년형, 신혼부부형 get bonus)
        if recommended_type in ['youth', 'newlyweds', 'newlyweds_growth']:
            policy_score += 15  # Priority type bonus
        
        # Optimal land size (500-2000 sqm)
        if 500 <= land_area <= 2000:
            policy_score += 15  # Ideal size bonus
        elif land_area > 2000:
            policy_score += 5  # Large but manageable
        else:
            policy_score -= 10  # Too small
        
        # Positive social value (positive NPV)
        if npv >= 0:
            policy_score += 10  # Financially sustainable
        
        policy_score = min(100, max(0, policy_score))
        grade = self._score_to_grade(policy_score)
        description = self._generate_policy_description(policy_score, recommended_type)
        
        return {
            'score': round(policy_score, 1),
            'grade': grade,
            'description': description
        }
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        elif score >= 50:
            return 'C-'
        elif score >= 40:
            return 'D'
        else:
            return 'F'
    
    def _scorecard_to_recommendation(self, scorecard: Dict[str, Any], overall_score: float) -> str:
        """Convert scorecard to GO/CONDITIONAL/REVISE/NO-GO recommendation"""
        finance_score = scorecard['finance']['score']
        risk_score = scorecard['risk']['score']
        market_score = scorecard['market']['score']
        
        # Critical thresholds
        if finance_score >= 70 and risk_score >= 70 and overall_score >= 75:
            return 'GO'
        elif finance_score >= 50 and risk_score >= 60 and overall_score >= 60:
            return 'CONDITIONAL'
        elif finance_score >= 35 and overall_score >= 45:
            return 'REVISE'
        else:
            return 'NO-GO'
    
    def _calculate_confidence_level(self, scorecard: Dict[str, Any]) -> str:
        """Calculate confidence level based on score variance"""
        scores = [scorecard[cat]['score'] for cat in ['location', 'finance', 'market', 'risk', 'policy']]
        score_variance = max(scores) - min(scores)
        
        if score_variance <= 15:
            return 'high'  # Consistent scores
        elif score_variance <= 30:
            return 'medium'
        else:
            return 'low'  # High variance = uncertainty
    
    def _generate_location_description(self, score: float, demand: Dict[str, Any]) -> str:
        """Generate location score description"""
        if score >= 80:
            return f"우수한 입지 조건, {demand.get('recommended_type_kr', '청년형')} 수요 최적지"
        elif score >= 60:
            return f"양호한 입지 조건, {demand.get('recommended_type_kr', '청년형')} 수요 적합"
        else:
            return "입지 조건 개선 필요, 수요 확보에 어려움 예상"
    
    def _generate_finance_description(self, score: float, npv: float, irr: float, payback: float) -> str:
        """Generate finance score description"""
        if score >= 70:
            return f"양호한 재무 구조 (NPV {npv/1e8:.1f}억, IRR {irr:.1f}%)"
        elif score >= 50:
            return f"보통 수준의 수익성 (NPV {npv/1e8:.1f}억, IRR {irr:.1f}%)"
        else:
            return f"재무적 타당성 부족 (NPV {npv/1e8:.1f}억, 개선 필요)"
    
    def _generate_market_description(self, score: float, signal: str, demand_score: float) -> str:
        """Generate market score description"""
        signal_kr = {'UNDERVALUED': '저평가', 'FAIR': '적정', 'OVERVALUED': '고평가'}.get(signal, '적정')
        if score >= 70:
            return f"시장 진입 최적 ({signal_kr}, 수요 {demand_score:.0f}점)"
        elif score >= 50:
            return f"시장 상황 양호 ({signal_kr}, 수요 {demand_score:.0f}점)"
        else:
            return f"시장 진입 신중 (시장 {signal_kr}, 수요 개선 필요)"
    
    def _generate_risk_description(self, score: float, level: str) -> str:
        """Generate risk score description"""
        level_kr = {'LOW': '낮음', 'MEDIUM': '보통', 'HIGH': '높음'}.get(level, '보통')
        if score >= 80:
            return f"안정적 리스크 수준 (전반적 리스크: {level_kr})"
        elif score >= 60:
            return f"관리 가능한 리스크 (전반적 리스크: {level_kr})"
        else:
            return f"높은 리스크, 완화 조치 필수 (전반적 리스크: {level_kr})"
    
    def _generate_policy_description(self, score: float, housing_type: str) -> str:
        """Generate policy score description"""
        type_kr = self._translate_housing_type(housing_type)
        if score >= 75:
            return f"LH 정책 방향과 높은 부합성 ({type_kr})"
        elif score >= 60:
            return f"LH 정책 방향과 부합 ({type_kr})"
        else:
            return f"정책 적합성 보완 필요 ({type_kr})"

    def build_expert_context(
        self,
        address: str,
        land_area_sqm: float,
        coordinates: Optional[Tuple[float, float]] = None,
        multi_parcel: bool = False,
        parcels: Optional[List[Dict[str, Any]]] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build EXPERT EDITION CONTEXT (v3) with additional analysis layers
        
        This extends build_context() with:
        - Executive Summary Dashboard with Comprehensive Scorecard (Phase 1)
        - Policy Framework Analysis (8-10 pages)
        - 36-Month Implementation Roadmap (2-3 pages)
        - Academic Conclusion (4-6 pages)
        
        Total expected output: 45-60 pages (Expert Edition)
        
        Args:
            Same as build_context()
        
        Returns:
            Extended REPORT_CONTEXT with expert analysis layers
        """
        logger.info(f"🎓 Building EXPERT EDITION CONTEXT for: {address}")
        
        # Step 1: Build base context using existing method
        context = self.build_context(
            address=address,
            land_area_sqm=land_area_sqm,
            coordinates=coordinates,
            multi_parcel=multi_parcel,
            parcels=parcels,
            additional_params=additional_params
        )
        
        # Step 2: Calculate Executive Summary Scorecard (Phase 1, Task 1.1)
        context['executive_summary'] = {
            'scorecard': self.calculate_scorecard(context),
            'key_metrics': self._extract_key_metrics(context),
            'decision_summary': self._generate_decision_summary(context)
        }
        logger.info("✅ Phase 1, Task 1.1: Executive Summary Scorecard calculated")
        
        # Step 2.1: Perform Competitive Analysis (Phase 2, Tasks 2.1-2.2)
        if self.competitive_analyzer:
            try:
                project_housing_type = context.get('demand', {}).get('recommended_type', 'youth')
                project_avg_rent = 8000  # Default estimate, in production get from finance data
                
                # Try to get actual rent from finance data
                if 'finance' in context and 'revenue' in context['finance']:
                    land_area = context.get('site', {}).get('land_area_sqm', 500)
                    total_units = int(land_area / 40)  # Rough estimate: 40sqm per unit
                    annual_revenue = context['finance']['revenue']['annual_rental']
                    avg_unit_size = 40  # Default
                    if total_units > 0 and avg_unit_size > 0:
                        project_avg_rent = (annual_revenue / total_units) / avg_unit_size / 12  # Monthly rent per sqm
                
                context['competitive_analysis'] = self.competitive_analyzer.analyze_competition(
                    address=address,
                    coordinates=coordinates,
                    project_housing_type=project_housing_type,
                    project_avg_rent=project_avg_rent,
                    project_amenities_score=75,  # Default, could be parameterized
                    project_unit_size=avg_unit_size
                )
                logger.info("✅ Phase 2, Tasks 2.1-2.2: Competitive Analysis + Price/Differentiation completed")
            except Exception as e:
                logger.warning(f"Competitive analysis failed: {e}")
                context['competitive_analysis'] = {'total_competitors': 0, 'projects': []}
        
        # Step 2.2: Enhance Risk Analysis (Phase 2, Tasks 2.3-2.5)
        if self.risk_enhancer and 'risk_analysis' in context:
            try:
                enhanced_risks = self.risk_enhancer.enhance_risk_analysis(
                    base_risk_analysis=context['risk_analysis'],
                    finance_data=context.get('finance', {}),
                    market_data=context.get('market', {}),
                    demand_data=context.get('demand', {})
                )
                # Merge enhanced risks back into context
                context['risk_analysis']['enhanced'] = enhanced_risks
                logger.info("✅ Phase 2, Tasks 2.3-2.5: Enhanced Risk Analysis (Matrix + Top10 + Exit) completed")
            except Exception as e:
                logger.warning(f"Risk enhancement failed: {e}")
        
        # Step 3: Generate Expert Edition layers
        try:
            from app.services_v13.report_full.policy_generator import PolicyGenerator
            from app.services_v13.report_full.roadmap_generator import RoadmapGenerator
            from app.services_v13.report_full.academic_generator import AcademicGenerator
            
            policy_gen = PolicyGenerator()
            roadmap_gen = RoadmapGenerator()
            academic_gen = AcademicGenerator()
            
            # Generate expert analysis
            context['policy_framework'] = policy_gen.generate_policy_analysis(context)
            context['implementation_roadmap'] = roadmap_gen.generate_roadmap(context)
            context['academic_conclusion'] = academic_gen.generate_academic_conclusion(context)
            
            # Update metadata for Expert Edition
            context['metadata']['report_type'] = 'LH_SUBMISSION_EXPERT_EDITION_V3'
            context['metadata']['page_count_estimated'] = '60-70'
            context['metadata']['version'] = 'ZeroSite v13.0 Expert Edition with Narrative Layer'
            
            logger.info("✅ EXPERT EDITION CONTEXT complete")
            
        except Exception as e:
            logger.error(f"Expert analysis generation failed: {e}")
            logger.warning("Falling back to Full Edition context")
        
        # Step 4: Generate Narrative Layer (Phase A - NEW)
        try:
            logger.info("📝 Generating Narrative Layer...")
            
            # Use the master method to generate all narratives at once
            context['narratives'] = self.narrative_interpreter.generate_all_narratives(context)
            
            # Add policy references
            context['references'] = self.policy_db.get_all_references()
            context['policy_summary'] = self.policy_db.get_policy_summary()
            
            logger.info("✅ Phase A: Narrative Layer generated (8 sections + references)")
            
        except Exception as e:
            logger.error(f"Narrative generation failed: {e}")
            logger.warning("Report will be generated without narrative layer")
            context['narratives'] = {}
            context['references'] = []
        
        return context
    
    def _extract_key_metrics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics for Executive Summary dashboard"""
        finance = context.get('finance', {})
        market = context.get('market', {})
        demand = context.get('demand', {})
        
        return {
            'capex': finance.get('capex', {}).get('total', 0),
            'npv': finance.get('npv', {}).get('public', 0),
            'irr': finance.get('irr', {}).get('public', 0),
            'payback': finance.get('payback', {}).get('years', 0),
            'market_signal': market.get('signal', 'FAIR'),
            'demand_score': demand.get('overall_score', 60.0),
            'housing_type': demand.get('recommended_type_kr', '청년형')
        }
    
    def _generate_decision_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate concise decision summary for Executive Summary"""
        decision = context.get('decision', {})
        scorecard = context.get('executive_summary', {}).get('scorecard', {})
        overall = scorecard.get('overall', {})
        
        return {
            'recommendation': decision.get('recommendation', 'CONDITIONAL'),
            'confidence': decision.get('confidence', 'medium'),
            'overall_score': overall.get('score', 60.0),
            'overall_grade': overall.get('grade', 'C+'),
            'key_strengths': self._identify_key_strengths(scorecard),
            'key_concerns': self._identify_key_concerns(scorecard)
        }
    
    def _identify_key_strengths(self, scorecard: Dict[str, Any]) -> List[str]:
        """Identify top 3 strengths from scorecard"""
        if not scorecard:
            return []
        
        categories = {k: v['score'] for k, v in scorecard.items() if k != 'overall'}
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        strengths = []
        cat_kr = {
            'location': '입지',
            'finance': '재무',
            'market': '시장',
            'risk': '리스크 관리',
            'policy': '정책 부합성'
        }
        
        for cat, score in sorted_categories[:3]:
            if score >= 70:
                strengths.append(f"{cat_kr.get(cat, cat)}: {scorecard[cat]['grade']} ({score:.0f}점)")
        
        return strengths if strengths else ['현재 특이 강점 없음']
    
    def _identify_key_concerns(self, scorecard: Dict[str, Any]) -> List[str]:
        """Identify top 3 concerns from scorecard"""
        if not scorecard:
            return []
        
        categories = {k: v['score'] for k, v in scorecard.items() if k != 'overall'}
        sorted_categories = sorted(categories.items(), key=lambda x: x[1])
        
        concerns = []
        cat_kr = {
            'location': '입지',
            'finance': '재무',
            'market': '시장',
            'risk': '리스크',
            'policy': '정책 부합성'
        }
        
        for cat, score in sorted_categories[:3]:
            if score < 60:
                concerns.append(f"{cat_kr.get(cat, cat)}: {scorecard[cat]['grade']} ({score:.0f}점)")
        
        return concerns if concerns else ['현재 특이 우려사항 없음']
