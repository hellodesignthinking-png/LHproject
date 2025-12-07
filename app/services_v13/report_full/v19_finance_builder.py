"""
ZeroSite v19 - Enhanced Finance Context Builder
================================================

This module builds the v19 financial context with:
- Complete narratives for all financial tables
- Academic + policy reasoning for all calculations
- Dual-logic decision system (financial + policy)
- Transaction model explanations
- All 13 deficiency fixes integrated
"""

from typing import Dict, Any, Optional, List
import logging

from app.services_v13.report_full.v19_financial_narrative import V19FinancialNarrative

logger = logging.getLogger(__name__)


def build_v19_finance_with_narratives(
    v18_transaction: Dict[str, Any],
    finance_data: Dict[str, Any],
    zoning_data: Dict[str, Any],
    demand_data: Dict[str, Any],
    address: str
) -> Dict[str, Any]:
    """
    Build v19 Finance Context with Complete Narratives
    
    This function addresses all 13 deficiencies from v18:
    1. ✅ 총사업비 근거 표 + 설명
    2. ✅ 실거래가 10건 비교 + 해석
    3. ✅ 감정평가 계산 논리 설명
    4. ✅ 민감도 분석 결론
    5. ✅ Payback 재정의 (거래형 모델)
    6. ✅ 지역별 감정평가율 설명
    7. ✅ PF 금융비용 표준 설명
    8. ✅ 건축비 지수 연동 설명
    9. ✅ 사업 개요 재작성 (거래형)
    10. ✅ "거래형 사업 모델" 섹션 추가
    11. ✅ 기타 섹션 거래형 관점 업데이트
    12. ✅ 의사결정 이중 기준 (재무+정책)
    13. ✅ 사업 리스크 및 대응 전략
    
    Args:
        v18_transaction: v18 transaction finance data
        finance_data: Traditional finance data (for appendix)
        zoning_data: Zoning analysis results
        demand_data: Demand analysis results
        address: Project address
        
    Returns:
        Complete v19 finance context with narratives
    """
    logger.info("=" * 80)
    logger.info("🎓 v19 Enhanced Financial Analysis with Narratives")
    logger.info("=" * 80)
    
    narrative_gen = V19FinancialNarrative()
    
    # Extract key data
    summary = v18_transaction.get('summary', {})
    capex_detail = v18_transaction.get('capex_detail', {})
    appraisal = v18_transaction.get('appraisal', {})
    land_comps = v18_transaction.get('land_comps', [])
    building_comps = v18_transaction.get('building_comps', [])
    sensitivity = v18_transaction.get('sensitivity', {})
    
    roi_pct = summary.get('roi_pct', 0)
    irr_pct = summary.get('irr_pct', 0)
    
    # Get region for regional appraisal rates
    region = _extract_region(address)
    housing_type = demand_data.get('recommended_type_kr', '청년형')
    
    # Load regional appraisal rates
    land_appraisal_rate, building_ack_rate = _get_regional_rates(region, housing_type)
    
    # Determine policy priority
    policy_priority = _determine_policy_priority(region, housing_type, demand_data)
    
    # Build v19 context
    v19_context = {
        # Section 1: Project Overview (거래형 관점)
        'project_overview': {
            'business_model': 'LH 신축매입임대 (거래형)',
            'business_model_en': 'LH Build-to-Sell Transaction Model',
            'business_structure': 'Build (토지매입+건축) → Sell (LH 매입) → Exit (사업종료)',
            'revenue_model': 'LH 최종 매입가 (NOT 30년 임대수익)',
            'investment_horizon': '2.5년 (공사완료 시 매입)',
            'investment_horizon_en': '2.5 years (Upon construction completion)',
            'risk_profile': '낮음 (LH 매입 확정 + 공사비 연동제)',
            'explanation': narrative_gen.explain_transaction_business_model()
        },
        
        # Section 2: Total Project Cost (Deficiency #1)
        'total_cost': {
            'breakdown': capex_detail,
            'total': capex_detail.get('total_capex', 0),
            'total_krw': capex_detail.get('total_capex_krw', '0억'),
            'narrative': narrative_gen.explain_total_cost_structure(
                _convert_capex_for_narrative(capex_detail)
            )
        },
        
        # Section 3: Land Comparables Analysis (Deficiency #2)
        'land_analysis': {
            'comparables': land_comps,
            'count': len(land_comps),
            'avg_price_m2': v18_transaction.get('avg_land_price', 0),
            'avg_price_m2_krw': v18_transaction.get('avg_land_price_krw', '0만원/㎡'),
            'narrative': narrative_gen.explain_land_comp_analysis(
                land_comps,
                v18_transaction.get('avg_land_price', 0)
            )
        },
        
        # Section 4: Building Comparables Analysis (Deficiency #2)
        'building_analysis': {
            'comparables': building_comps,
            'count': len(building_comps),
            'avg_price_m2': v18_transaction.get('avg_building_price', 0),
            'avg_price_m2_krw': v18_transaction.get('avg_building_price_krw', '0만원/㎡'),
            'narrative': narrative_gen.explain_construction_comp_analysis(
                building_comps,
                v18_transaction.get('avg_building_price', 0)
            )
        },
        
        # Section 5: LH Appraisal Mechanism (Deficiency #3)
        'lh_appraisal': {
            'appraisal_data': appraisal,
            'land_appraisal_rate': land_appraisal_rate,
            'building_acknowledgment_rate': building_ack_rate,
            'land_cost': capex_detail.get('land_cost', 0),
            'construction_cost': capex_detail.get('indexed_construction_cost', 0),
            'narrative': narrative_gen.explain_lh_appraisal_logic(
                land_appraisal_rate,
                building_ack_rate,
                capex_detail.get('land_cost', 0),
                capex_detail.get('indexed_construction_cost', 0)
            )
        },
        
        # Section 6: Transaction Profit Calculation
        'profit_calculation': {
            'total_capex': summary.get('total_capex', 0),
            'total_capex_krw': summary.get('total_capex_krw', '0억'),
            'lh_purchase_price': summary.get('lh_purchase_price', 0),
            'lh_purchase_price_krw': summary.get('lh_purchase_price_krw', '0억'),
            'profit': summary.get('profit', 0),
            'profit_krw': summary.get('profit_krw', '0억'),
            'roi_pct': roi_pct,
            'irr_pct': irr_pct,
            'formula': 'Profit = LH Purchase Price - Total CAPEX',
            'roi_formula': 'ROI = (Profit / Total CAPEX) × 100%',
            'irr_formula': 'IRR = (Profit / CAPEX) / Construction Period (2.5yr)'
        },
        
        # Section 7: Sensitivity Analysis (Deficiency #4)
        'sensitivity_analysis': {
            'results': sensitivity.get('results', []),
            'interpretation': sensitivity.get('interpretation', ''),
            'tornado_diagram_data': _extract_tornado_data(sensitivity),
            'narrative': narrative_gen.explain_sensitivity_conclusion(
                _extract_tornado_data(sensitivity)
            )
        },
        
        # Section 8: Payback Period Re-definition (Deficiency #5)
        'payback_period': {
            'construction_period_years': 2.5,
            'payback_traditional': summary.get('payback_years', 0),
            'payback_transaction_model': 2.5,
            'explanation': '거래형 사업 모델에서는 완공 즉시 LH 매입가를 수령하므로, 실질적 투자회수기간은 공사기간(2.5년)입니다.',
            'narrative': narrative_gen.explain_payback_transaction_model(2.5)
        },
        
        # Section 9: Regional Appraisal Rates (Deficiency #6)
        'regional_rates': {
            'region': region,
            'housing_type': housing_type,
            'land_appraisal_rate': land_appraisal_rate,
            'building_acknowledgment_rate': building_ack_rate,
            'narrative': narrative_gen.explain_regional_appraisal_rates(
                region,
                land_appraisal_rate,
                building_ack_rate,
                housing_type
            )
        },
        
        # Section 10: PF Financing Cost (Deficiency #7)
        'pf_financing': {
            'financing_cost': capex_detail.get('financing_cost', 0),
            'financing_cost_krw': capex_detail.get('financing_cost_krw', '0억'),
            'total_capex': capex_detail.get('total_capex', 0),
            'narrative': narrative_gen.explain_pf_financing_cost(
                capex_detail.get('financing_cost', 0),
                capex_detail.get('total_capex', 0)
            )
        },
        
        # Section 11: Construction Cost Indexing (Deficiency #8)
        'construction_indexing': {
            'base_cost': capex_detail.get('base_construction_cost', 0),
            'base_cost_krw': capex_detail.get('base_construction_cost_krw', '0억'),
            'indexed_cost': capex_detail.get('indexed_construction_cost', 0),
            'indexed_cost_krw': capex_detail.get('indexed_construction_cost_krw', '0억'),
            'index_change_pct': _calculate_index_change(capex_detail),
            'narrative': narrative_gen.explain_construction_cost_indexing(
                _calculate_index_change(capex_detail)
            )
        },
        
        # Section 12: Decision with Dual Logic (Deficiency #12)
        'decision': narrative_gen.explain_dual_decision_logic(
            roi_pct,
            irr_pct,
            policy_priority
        ),
        
        # Section 13: Business Risks & Response Strategies (Deficiency #13)
        'risk_strategy': {
            'narrative': narrative_gen.explain_business_risks_and_responses(roi_pct)
        },
        
        # Metadata
        'version': 'v19.0.0',
        'deficiencies_fixed': 13,
        'generated_at': summary.get('generated_at', ''),
        'is_complete': True
    }
    
    logger.info(f"✅ v19 Enhanced Financial Analysis Complete")
    logger.info(f"   ROI: {roi_pct:.2f}%")
    logger.info(f"   Decision: {v19_context['decision']['decision']}")
    logger.info(f"   Narratives: 13 sections generated")
    
    return v19_context


# Helper functions

def _extract_region(address: str) -> str:
    """Extract region from address"""
    if '서울' in address:
        return 'seoul'
    elif '경기' in address:
        return 'gyeonggi'
    elif '인천' in address:
        return 'incheon'
    elif '부산' in address:
        return 'busan'
    elif '대구' in address:
        return 'daegu'
    elif '세종' in address:
        return 'sejong'
    else:
        return 'other'


def _get_regional_rates(region: str, housing_type: str) -> tuple:
    """
    Get regional appraisal rates from database
    
    Uses app/services/regional_appraisal_rates.py
    """
    try:
        from app.services.regional_appraisal_rates import get_rates_for_region
        
        rates = get_rates_for_region(region, housing_type)
        return rates.get('land_appraisal_rate', 0.90), rates.get('building_ack_rate', 0.90)
    except:
        # Fallback defaults
        return 0.90, 0.90


def _determine_policy_priority(region: str, housing_type: str, demand_data: Dict[str, Any]) -> str:
    """
    Determine policy priority level
    
    VERY_HIGH: Seoul youth housing
    HIGH: Metropolitan youth/newlyweds
    MEDIUM: General housing
    LOW: Low-demand regions
    """
    demand_score = demand_data.get('overall_score', 60.0)
    
    if region == 'seoul' and '청년' in housing_type:
        return 'VERY_HIGH'
    elif region in ['seoul', 'gyeonggi', 'incheon'] and demand_score >= 70:
        return 'HIGH'
    elif demand_score >= 60:
        return 'MEDIUM'
    else:
        return 'LOW'


def _convert_capex_for_narrative(capex_detail: Dict[str, Any]) -> Dict[str, float]:
    """Convert CAPEX detail for narrative generator"""
    return {
        'land': capex_detail.get('land_cost', 0),
        'construction': capex_detail.get('indexed_construction_cost', 0),
        'acquisition_tax': capex_detail.get('land_acquisition_tax', 0),
        'design_fee': capex_detail.get('design_cost', 0),
        'supervision_fee': capex_detail.get('supervision_cost', 0),
        'contingency': capex_detail.get('contingency_cost', 0),
        'financing_cost': capex_detail.get('financing_cost', 0),
        'other_costs': capex_detail.get('misc_cost', 0),
        'total': capex_detail.get('total_capex', 0)
    }


def _extract_tornado_data(sensitivity: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract tornado diagram data from sensitivity results"""
    results = sensitivity.get('results', [])
    
    # Group by variable and calculate swing
    variable_swings = {}
    for result in results:
        var = result.get('variable', '')
        roi = result.get('roi_pct', 0)
        
        if var not in variable_swings:
            variable_swings[var] = {'name_kr': var, 'roi_values': []}
        
        variable_swings[var]['roi_values'].append(roi)
    
    # Calculate NPV swing for each variable
    tornado_data = []
    for var, data in variable_swings.items():
        if len(data['roi_values']) >= 2:
            swing = max(data['roi_values']) - min(data['roi_values'])
            tornado_data.append({
                'variable': var,
                'name_kr': var,
                'npv_swing': swing * 1e8,  # Convert to currency
                'impact_pct': swing
            })
    
    # Sort by swing (largest first)
    tornado_data.sort(key=lambda x: abs(x['npv_swing']), reverse=True)
    
    return tornado_data


def _calculate_index_change(capex_detail: Dict[str, Any]) -> float:
    """Calculate construction cost index change percentage"""
    base = capex_detail.get('base_construction_cost', 0)
    indexed = capex_detail.get('indexed_construction_cost', 0)
    
    if base > 0:
        return ((indexed - base) / base) * 100
    return 0.0
