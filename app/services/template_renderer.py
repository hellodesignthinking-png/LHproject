"""
ZeroSite Template Renderer Service
===================================

Jinja2 기반 템플릿 렌더링 서비스

Version: 1.0
Date: 2025-01-10
"""

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# 템플릿 디렉토리 경로
TEMPLATE_DIR = Path(__file__).parent.parent / "templates_v13"

# Jinja2 환경 설정
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True
)


def render_template(template_name: str, context: Dict[str, Any]) -> str:
    """
    Jinja2 템플릿을 렌더링합니다.
    
    Args:
        template_name: 템플릿 파일명 (예: "master_comprehensive_report.html")
        context: 템플릿 변수 딕셔너리
    
    Returns:
        렌더링된 HTML 문자열
    """
    try:
        template = jinja_env.get_template(template_name)
        html = template.render(**context)
        logger.info(f"✅ Template '{template_name}' rendered successfully")
        return html
    except Exception as e:
        logger.error(f"❌ Template rendering failed for '{template_name}': {e}")
        raise


def prepare_master_report_context(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Master 종합보고서용 컨텍스트를 준비합니다.
    
    기획서 대비 모든 필수 데이터를 매핑합니다:
    - Executive Summary
    - M2: 토지감정평가 (거래사례, 설명 포함)
    - M3: 선호유형분석 (후보 리스트, 매트릭스)
    - M4: 건축규모결정 (법적/현실 비교)
    - M5: 사업성분석 (비용 구조, 리스크)
    - M6: LH심사예측 (종합 평가)
    """
    from datetime import datetime
    
    # 기본 메타 정보
    context = {
        'generated_at': data.get('generated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'context_id': data.get('context_id', 'N/A'),
        'address': data.get('address', '주소 정보 없음'),
        'current_year': datetime.now().year,
    }
    
    # ===== Executive Summary =====
    final_decision = data.get('final_decision', '검토 필요')
    context['final_decision'] = final_decision
    context['final_decision_interpretation'] = data.get(
        'final_decision_interpretation', 
        '분석 결과를 검토 중입니다.'
    )
    
    # Decision class (CSS 스타일링용)
    if "추진 권장" in final_decision:
        context['decision_class'] = ""
    elif "조건부" in final_decision:
        context['decision_class'] = "conditional"
    else:
        context['decision_class'] = "negative"
    
    context['approval_probability_pct'] = data.get('approval_probability_pct', 'N/A')
    context['grade'] = data.get('grade', 'N/A')
    context['total_score'] = data.get('total_score', 'N/A')
    
    # Key Findings & Risks
    context['key_findings'] = data.get('key_findings', [
        '분석 결과를 집계 중입니다.'
    ])
    context['key_risks'] = data.get('key_risks', [
        '리스크 분석을 진행 중입니다.'
    ])
    
    # ===== M2: 토지감정평가 =====
    m2_data = data.get('m2', {})
    context['land_value_krw'] = format_currency(m2_data.get('land_value_total_krw', 0))
    context['unit_price_sqm'] = format_currency(m2_data.get('unit_price_sqm', 0))
    context['unit_price_pyeong'] = format_currency(m2_data.get('unit_price_pyeong', 0))
    context['confidence_pct'] = m2_data.get('confidence_pct', 0)
    context['transaction_count'] = m2_data.get('transaction_count', 0)
    context['avg_price_sqm'] = format_currency(m2_data.get('avg_price_sqm', 0))
    context['official_price_krw'] = format_currency(m2_data.get('official_price_total_krw', 0))
    context['official_price_ratio'] = m2_data.get('official_price_ratio', 70)
    
    # ===== M3: 선호유형분석 =====
    m3_data = data.get('m3', {})
    context['recommended_housing_type'] = m3_data.get('recommended_type', '분석 중')
    context['housing_type_score'] = m3_data.get('total_score', 0)
    context['second_choice_type'] = m3_data.get('second_choice', '없음')
    
    # 라이프스타일 요인 (기획서: 후보 비교 테이블)
    context['lifestyle_factors'] = m3_data.get('lifestyle_factors', [
        {'name': '청년층 집중도', 'score': 85, 'weight': 30, 'description': '주변 청년층 인구 비율 높음'},
        {'name': '대중교통 접근성', 'score': 90, 'weight': 25, 'description': '지하철역 도보 5분 거리'},
        {'name': '편의시설 밀집도', 'score': 80, 'weight': 20, 'description': '편의점, 마트 등 풍부'},
    ])
    
    # ===== M4: 건축규모결정 =====
    m4_data = data.get('m4', {})
    
    # 법적 상한
    context['legal_far'] = m4_data.get('legal_far', 200)
    context['legal_bcr'] = m4_data.get('legal_bcr', 60)
    context['legal_units'] = m4_data.get('legal_units', 0)
    context['legal_gfa'] = format_number(m4_data.get('legal_gfa', 0))
    
    # 인센티브 적용
    context['incentive_far'] = m4_data.get('incentive_far', 250)
    context['incentive_units'] = m4_data.get('incentive_units', 0)
    context['incentive_gfa'] = format_number(m4_data.get('incentive_gfa', 0))
    context['units_increase'] = m4_data.get('incentive_units', 0) - m4_data.get('legal_units', 0)
    
    # 주차 계획
    context['parking_alt_a_count'] = m4_data.get('parking_alt_a', 0)
    context['parking_alt_a_type'] = m4_data.get('parking_alt_a_type', '지상 주차')
    context['parking_alt_a_cost'] = format_currency(m4_data.get('parking_alt_a_cost', 0))
    
    context['parking_alt_b_count'] = m4_data.get('parking_alt_b', 0)
    context['parking_alt_b_type'] = m4_data.get('parking_alt_b_type', '지하 주차')
    context['parking_alt_b_cost'] = format_currency(m4_data.get('parking_alt_b_cost', 0))
    
    # ===== M5: 사업성분석 =====
    m5_data = data.get('m5', {})
    
    # 재무지표
    context['irr_pct'] = m5_data.get('irr_pct', 0)
    context['npv_krw'] = format_currency(m5_data.get('npv_krw', 0))
    context['roi_pct'] = m5_data.get('roi_pct', 0)
    context['payback_years'] = m5_data.get('payback_years', 'N/A')
    
    # 비용 구조
    costs = m5_data.get('costs', {})
    total_cost = costs.get('total', 1)  # 0 방지
    
    context['land_cost_krw'] = format_currency(costs.get('land', 0))
    context['land_cost_ratio'] = round((costs.get('land', 0) / total_cost) * 100, 1) if total_cost > 0 else 0
    
    context['construction_cost_krw'] = format_currency(costs.get('construction', 0))
    context['construction_cost_ratio'] = round((costs.get('construction', 0) / total_cost) * 100, 1) if total_cost > 0 else 0
    
    context['indirect_cost_krw'] = format_currency(costs.get('indirect', 0))
    context['indirect_cost_ratio'] = round((costs.get('indirect', 0) / total_cost) * 100, 1) if total_cost > 0 else 0
    
    context['total_cost_krw'] = format_currency(total_cost)
    
    # 수익 구조
    revenues = m5_data.get('revenues', {})
    context['rental_revenue_krw'] = format_currency(revenues.get('rental', 0))
    context['total_revenue_krw'] = format_currency(revenues.get('total', 0))
    context['net_profit_krw'] = format_currency(revenues.get('total', 0) - total_cost)
    
    # ===== M6: LH심사예측 =====
    m6_data = data.get('m6', {})
    
    context['m6_total_score'] = m6_data.get('total_score', 0)
    context['m6_grade'] = m6_data.get('grade', 'N/A')
    context['m6_approval_probability'] = m6_data.get('approval_probability_pct', 0)
    context['m6_decision'] = m6_data.get('decision', '검토 필요')
    
    # 세부 점수
    scores = m6_data.get('scores', {})
    context['location_score'] = scores.get('location', 0)
    context['location_max'] = 30
    context['location_ratio'] = round((scores.get('location', 0) / 30) * 100, 1) if scores.get('location', 0) > 0 else 0
    
    context['scale_score'] = scores.get('scale', 0)
    context['scale_max'] = 15
    context['scale_ratio'] = round((scores.get('scale', 0) / 15) * 100, 1) if scores.get('scale', 0) > 0 else 0
    
    context['feasibility_score'] = scores.get('feasibility', 0)
    context['feasibility_max'] = 40
    context['feasibility_ratio'] = round((scores.get('feasibility', 0) / 40) * 100, 1) if scores.get('feasibility', 0) > 0 else 0
    
    context['compliance_score'] = scores.get('compliance', 0)
    context['compliance_max'] = 15
    context['compliance_ratio'] = round((scores.get('compliance', 0) / 15) * 100, 1) if scores.get('compliance', 0) > 0 else 0
    
    # 필수 요건 검증
    context['hard_fail_items'] = m6_data.get('hard_fail_items', [
        {'name': '용적률', 'limit': '200%', 'value': '180%', 'passed': True},
        {'name': '주차대수', 'limit': '20대', 'value': '22대', 'passed': True},
    ])
    
    # 다음 단계
    context['next_steps'] = m6_data.get('next_steps', [
        'LH 본부 검토 의뢰',
        '추가 서류 준비',
        '현장 실사 준비'
    ])
    
    # ===== M7: 커뮤니티 운영 계획 (NEW) =====
    community_plan = data.get('community_plan')
    if community_plan and isinstance(community_plan, dict):
        context['community_plan'] = {
            'primary_resident_type': community_plan.get('primary_resident_type', '일반'),
            'community_goal': community_plan.get('community_goal', '커뮤니티 목표 수립 중'),
            'goal_interpretation': community_plan.get('goal_interpretation', ''),
            'program_plan': community_plan.get('program_plan', ''),
            'operation_model': community_plan.get('operation_model', 'LH 직접 운영'),
            'operation_model_detail': community_plan.get('operation_model_detail', ''),
            'sustainability_detail': community_plan.get('sustainability_detail', ''),
            'key_programs_count': community_plan.get('key_programs_count', 0),
            'monthly_program_frequency': community_plan.get('monthly_program_frequency', 0),
            'participation_target_pct': community_plan.get('participation_target_pct', 0),
            'space_count': community_plan.get('space_count', 0),
            'sustainability_score': community_plan.get('sustainability_score')
        }
    else:
        context['community_plan'] = None
    
    return context


def format_currency(value: Any) -> str:
    """통화 포맷팅 (원화)"""
    if value is None or value == 'N/A':
        return 'N/A'
    try:
        num = float(value)
        if num >= 100_000_000:  # 1억 이상
            return f"₩{num / 100_000_000:.1f}억"
        elif num >= 10_000:  # 1만 이상
            return f"₩{num / 10_000:.0f}만"
        else:
            return f"₩{num:,.0f}"
    except (ValueError, TypeError):
        return str(value)


def format_number(value: Any) -> str:
    """숫자 포맷팅 (천 단위 쉼표)"""
    if value is None or value == 'N/A':
        return 'N/A'
    try:
        return f"{float(value):,.0f}"
    except (ValueError, TypeError):
        return str(value)


def render_master_comprehensive_report(data: Dict[str, Any]) -> str:
    """
    Master 종합보고서를 렌더링합니다.
    
    템플릿: app/templates_v13/master_comprehensive_report.html
    """
    context = prepare_master_report_context(data)
    return render_template("master_comprehensive_report.html", context)


def render_m7_community_plan_report(data: Dict[str, Any]) -> str:
    """
    M7 커뮤니티 계획 독립 보고서를 렌더링합니다.
    
    템플릿: app/templates_v13/m7_community_plan_report.html
    
    Args:
        data: 보고서 데이터 (community_plan 포함 필수)
    
    Returns:
        렌더링된 M7 HTML 보고서
    """
    from datetime import datetime
    
    # M7 데이터 검증
    community_plan = data.get('community_plan')
    if not community_plan:
        raise ValueError("M7 커뮤니티 계획 데이터가 없습니다.")
    
    # 컨텍스트 구성
    context = {
        'generated_at': data.get('generated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'context_id': data.get('context_id', 'N/A'),
        'address': data.get('address', '주소 정보 없음'),
        'current_year': datetime.now().year,
        'community_plan': community_plan
    }
    
    logger.info(f"✅ M7 독립 보고서 렌더링: context_id={context['context_id']}")
    return render_template("m7_community_plan_report.html", context)

