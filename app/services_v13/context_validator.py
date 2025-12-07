"""
Context Validator for ZeroSite v14.5
Ensures Data → Context → Narrative consistency

Purpose:
- Validate financial data (NPV/IRR/Payback negative case handling)
- Validate demand data (ensure score always exists)
- Validate market data (ensure signal always exists)
- Guarantee no empty values in context that would cause narrative fallback
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def validate_financial(financial: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize financial data to ensure no empty values.
    
    Handles negative cases:
    - NPV = 0 or None → 'negative_case' status
    - IRR invalid/None → '<0' with explanation
    - Payback None → 'Not achievable'
    
    Args:
        financial: Raw financial data from finance engine
        
    Returns:
        Validated financial dict with guaranteed non-empty values
    """
    validated = financial.copy()
    
    # Extract core values
    npv_public = financial.get('npv_public_krw', 0)
    npv_private = financial.get('npv_private_krw', 0)
    irr_public = financial.get('irr_public_pct', None)
    irr_private = financial.get('irr_private_pct', None)
    payback = financial.get('payback_period_years', None)
    capex = financial.get('capex', {}).get('total_krw', 0)
    
    # CASE 1: NPV Validation
    if npv_public is None or npv_public == 0:
        if capex > 0:
            # Negative NPV case
            validated['npv_public_krw'] = npv_public if npv_public is not None else 0
            validated['npv_status'] = 'negative_case'
            validated['npv_reason'] = '건설비 대비 수익구조 부족으로 순현재가치 음수'
            logger.warning(f"NPV validation: Negative case detected (CAPEX={capex}, NPV={npv_public})")
        else:
            # Missing data case
            validated['npv_public_krw'] = 0
            validated['npv_status'] = 'missing_data'
            validated['npv_reason'] = '재무 데이터 불충분'
    else:
        validated['npv_status'] = 'positive' if npv_public > 0 else 'negative_case'
        validated['npv_reason'] = '정상 산출' if npv_public > 0 else '건설비 대비 수익구조 부족'
    
    # CASE 2: IRR Validation
    if irr_public is None or (isinstance(irr_public, (int, float)) and irr_public <= -100):
        validated['irr_public_pct'] = '<0'
        validated['irr_status'] = 'negative'
        validated['irr_reason'] = '음수 현금흐름으로 인한 내부수익률 산출 불가'
        logger.warning(f"IRR validation: Negative/invalid case (IRR={irr_public})")
    elif isinstance(irr_public, str):
        # Already formatted as string (e.g., '<0')
        validated['irr_status'] = 'negative'
        validated['irr_reason'] = '음수 현금흐름으로 인한 내부수익률 산출 불가'
    else:
        validated['irr_status'] = 'positive' if irr_public > 0 else 'negative'
        validated['irr_reason'] = '정상 산출' if irr_public > 0 else '낮은 수익률'
    
    # CASE 3: Payback Validation
    if payback is None or payback <= 0 or payback > 100:
        validated['payback_period_years'] = 'Not achievable'
        validated['payback_status'] = 'unreachable'
        validated['payback_reason'] = '30년 운영기간 내 투자금 회수 불가'
        logger.warning(f"Payback validation: Not achievable (payback={payback})")
    else:
        validated['payback_status'] = 'achievable'
        validated['payback_reason'] = f'{payback:.1f}년 내 회수 가능'
    
    # Add validation metadata
    validated['_validated'] = True
    validated['_validation_timestamp'] = _get_timestamp()
    
    return validated


def validate_demand(demand: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize demand data to ensure score always exists.
    
    If score is missing:
    - Use regional defaults based on location type
    - Mark as 'estimated' for transparency
    
    Args:
        demand: Raw demand data from demand engine
        
    Returns:
        Validated demand dict with guaranteed score
    """
    validated = demand.copy()
    
    overall_score = demand.get('overall_score', None)
    
    # CASE 1: Score exists and valid
    if overall_score is not None and 0 <= overall_score <= 100:
        validated['score_status'] = 'computed'
        validated['score_source'] = 'demand_engine'
    
    # CASE 2: Score missing or invalid
    else:
        # Estimate based on location type
        location_type = demand.get('location_type', 'urban')
        
        if location_type == 'urban_core':
            estimated_score = 75.0
        elif location_type == 'urban':
            estimated_score = 65.0
        elif location_type == 'suburban':
            estimated_score = 55.0
        elif location_type == 'rural':
            estimated_score = 45.0
        else:
            estimated_score = 50.0
        
        validated['overall_score'] = estimated_score
        validated['score_status'] = 'estimated'
        validated['score_source'] = f'regional_default ({location_type})'
        validated['score_reason'] = '데이터 부족으로 지역 평균값 사용'
        
        logger.warning(f"Demand validation: Score estimated (type={location_type}, score={estimated_score})")
    
    # Ensure subcategories exist
    if 'by_type' not in validated or not validated['by_type']:
        validated['by_type'] = {
            'youth': validated.get('overall_score', 50) * 1.1,
            'newlyweds': validated.get('overall_score', 50) * 1.0,
            'elderly': validated.get('overall_score', 50) * 0.9,
            'general': validated.get('overall_score', 50) * 0.95
        }
        validated['by_type_status'] = 'estimated'
    
    validated['_validated'] = True
    validated['_validation_timestamp'] = _get_timestamp()
    
    return validated


def validate_market(market: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize market data to ensure signal always exists.
    
    If market signal is missing:
    - Use regional defaults (Seoul: FAIR, Metro: HOT, Regional: STABLE)
    - Mark as 'fallback' for transparency
    
    Args:
        market: Raw market data from market engine
        
    Returns:
        Validated market dict with guaranteed signal
    """
    validated = market.copy()
    
    market_signal = market.get('signal', None)
    
    # CASE 1: Signal exists and valid
    valid_signals = ['UNDERVALUED', 'FAIR', 'OVERVALUED', 'HOT', 'STABLE', 'COOLING']
    if market_signal in valid_signals:
        validated['signal_status'] = 'computed'
        validated['signal_source'] = 'market_engine'
    
    # CASE 2: Signal missing or invalid
    else:
        # Determine region from address
        address = market.get('address', '')
        region = _detect_region(address)
        
        # Regional defaults
        if region == 'seoul':
            default_signal = 'FAIR'
        elif region == 'metro':
            default_signal = 'HOT'
        elif region == 'regional':
            default_signal = 'STABLE'
        else:
            default_signal = 'FAIR'
        
        validated['signal'] = default_signal
        validated['signal_status'] = 'fallback'
        validated['signal_source'] = f'regional_default ({region})'
        validated['signal_reason'] = '시장 데이터 부족으로 지역 기본값 사용'
        
        logger.warning(f"Market validation: Signal fallback (region={region}, signal={default_signal})")
    
    # Ensure temperature exists
    if 'temperature' not in validated or not validated['temperature']:
        validated['temperature'] = 'STABLE'
        validated['temperature_status'] = 'default'
    
    # Ensure price_change_pct exists
    if 'price_change_pct' not in validated:
        validated['price_change_pct'] = 0.0
        validated['price_change_status'] = 'estimated'
    
    validated['_validated'] = True
    validated['_validation_timestamp'] = _get_timestamp()
    
    return validated


def validate_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Master validation function to ensure entire context is consistent.
    
    Validates:
    - financial data
    - demand data
    - market data
    
    Args:
        context: Full report context
        
    Returns:
        Fully validated context with guaranteed non-empty values
    """
    validated = context.copy()
    
    # Validate finance
    if 'finance' in context:
        validated['finance'] = validate_financial(context['finance'])
    
    # Validate demand
    if 'demand' in context:
        validated['demand'] = validate_demand(context['demand'])
    
    # Validate market
    if 'market' in context:
        validated['market'] = validate_market(context['market'])
    
    # Add overall validation metadata
    validated['_context_validated'] = True
    validated['_validation_timestamp'] = _get_timestamp()
    
    logger.info("Context validation complete")
    
    return validated


# Helper functions

def _get_timestamp() -> str:
    """Get current timestamp for validation metadata"""
    from datetime import datetime
    return datetime.now().isoformat()


def _detect_region(address: str) -> str:
    """
    Detect region type from address string
    
    Returns:
        'seoul', 'metro', 'regional', or 'unknown'
    """
    address_lower = address.lower()
    
    if '서울' in address or 'seoul' in address_lower:
        return 'seoul'
    elif any(city in address for city in ['인천', '부천', '성남', '수원', '용인', '고양', '남양주', '화성']):
        return 'metro'
    elif any(city in address for city in ['부산', '대구', '대전', '광주', '울산']):
        return 'regional'
    else:
        return 'unknown'


# Export validation functions
__all__ = [
    'validate_financial',
    'validate_demand',
    'validate_market',
    'validate_context'
]
