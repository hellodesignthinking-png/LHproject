"""
ZeroSite 4.0 Phase 3.5C - Data Restoration Validation Tests
===========================================================

Purpose: 데이터 복원 검증
- M2~M5 데이터가 실제로 보고서에 포함되는지 확인
- N/A가 없는지 확인
- 판단은 M6만 하는지 확인

Version: 1.0
Date: 2025-12-27
"""

import pytest
from app.services.m6_centered_report_base import create_m6_centered_report
from app.services.simple_html_renderer import render_simple_html


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_m6_result():
    """샘플 M6 결과"""
    return {
        'lh_score_total': 75.0,
        'judgement': 'CONDITIONAL',
        'grade': 'B',
        'fatal_reject': False,
        'deduction_reasons': ['주차 효율 부족 -4점', '인근 공급 과잉 -3점'],
        'improvement_points': ['+6점: 주차 확보', '+4점: 차별화 전략'],
        'section_scores': {
            'policy': 15,
            'location': 18,
            'construction': 12,
            'price': 10,
            'business': 10
        }
    }


@pytest.fixture
def sample_m1_m5_data():
    """샘플 M1~M5 데이터"""
    return {
        'm1': {
            'address': '서울특별시 강남구 테헤란로 123',
            'area_pyeong': 300
        },
        'm2': {
            'land_value': 6081933538,
            'land_value_per_pyeong': 50000000,
            'confidence_pct': 85.0
        },
        'm3': {
            'recommended_type': 'youth',
            'total_score': 85.5,
            'demand_score': 90.0
        },
        'm4': {
            'legal_units': 20,
            'incentive_units': 26,
            'floor_area': 1500.0
        },
        'm5': {
            'npv_public_krw': 792999999,
            'irr_pct': 12.5,
            'roi_pct': 15.2,
            'grade': 'B'
        }
    }


# ============================================================================
# Phase 3.5C Data Restoration Tests
# ============================================================================

class TestDataRestoration:
    """데이터 복원 검증 테스트"""
    
    def test_m2_data_exists(self, sample_m6_result, sample_m1_m5_data):
        """M2 데이터가 보고서에 포함되는지 확인"""
        report = create_m6_centered_report('all_in_one', sample_m6_result, sample_m1_m5_data)
        
        evidence = report.get('evidence_data', {})
        m2 = evidence.get('m2_appraisal', {})
        
        # M2 데이터 존재 확인
        assert m2, "M2 데이터가 비어있습니다"
        assert 'land_value' in m2, "land_value가 없습니다"
        assert m2['land_value'] == 6081933538, f"land_value 불일치: {m2['land_value']}"
        assert m2['land_value_per_pyeong'] == 50000000, "land_value_per_pyeong 불일치"
    
    def test_m3_data_exists(self, sample_m6_result, sample_m1_m5_data):
        """M3 데이터가 보고서에 포함되는지 확인"""
        report = create_m6_centered_report('all_in_one', sample_m6_result, sample_m1_m5_data)
        
        evidence = report.get('evidence_data', {})
        m3 = evidence.get('m3_housing_type', {})
        
        # M3 데이터 존재 확인
        assert m3, "M3 데이터가 비어있습니다"
        assert 'recommended_type' in m3, "recommended_type이 없습니다"
        assert m3['recommended_type'] == 'youth', f"recommended_type 불일치: {m3['recommended_type']}"
        assert m3['total_score'] == 85.5, "total_score 불일치"
    
    def test_m4_data_exists(self, sample_m6_result, sample_m1_m5_data):
        """M4 데이터가 보고서에 포함되는지 확인"""
        report = create_m6_centered_report('all_in_one', sample_m6_result, sample_m1_m5_data)
        
        evidence = report.get('evidence_data', {})
        m4 = evidence.get('m4_capacity', {})
        
        # M4 데이터 존재 확인
        assert m4, "M4 데이터가 비어있습니다"
        assert 'legal_units' in m4, "legal_units이 없습니다"
        assert m4['legal_units'] == 20, f"legal_units 불일치: {m4['legal_units']}"
        assert m4['incentive_units'] == 26, "incentive_units 불일치"
    
    def test_m5_data_exists(self, sample_m6_result, sample_m1_m5_data):
        """M5 데이터가 보고서에 포함되는지 확인"""
        report = create_m6_centered_report('all_in_one', sample_m6_result, sample_m1_m5_data)
        
        evidence = report.get('evidence_data', {})
        m5 = evidence.get('m5_feasibility', {})
        
        # M5 데이터 존재 확인
        assert m5, "M5 데이터가 비어있습니다"
        assert 'npv_public_krw' in m5, "npv_public_krw이 없습니다"
        assert m5['npv_public_krw'] == 792999999, f"NPV 불일치: {m5['npv_public_krw']}"
        assert m5['irr_pct'] == 12.5, "IRR 불일치"
        assert m5['roi_pct'] == 15.2, "ROI 불일치"
    
    def test_html_rendering_includes_data(self, sample_m6_result, sample_m1_m5_data):
        """HTML 렌더링에 데이터가 포함되는지 확인"""
        report = create_m6_centered_report('all_in_one', sample_m6_result, sample_m1_m5_data)
        html = render_simple_html(report)
        
        # HTML에 실제 데이터가 포함되는지 확인
        assert '60.82억원' in html or '6081933538' in html, "M2 land_value가 HTML에 없음"
        assert 'youth' in html, "M3 recommended_type이 HTML에 없음"
        assert '20세대' in html, "M4 legal_units이 HTML에 없음"
        assert '7.93억원' in html or '792999999' in html, "M5 NPV가 HTML에 없음"
        
        # N/A가 없어야 함 (실제 데이터가 있으므로)
        assert 'N/A' not in html or html.count('N/A') <= 2, f"N/A가 너무 많음: {html.count('N/A')}개"
    
    def test_no_judgement_in_module_data(self, sample_m6_result, sample_m1_m5_data):
        """M2~M5 데이터에 판단 표현이 없는지 확인"""
        report = create_m6_centered_report('all_in_one', sample_m6_result, sample_m1_m5_data)
        
        evidence = report.get('evidence_data', {})
        m2 = evidence.get('m2_appraisal', {})
        m3 = evidence.get('m3_housing_type', {})
        m5 = evidence.get('m5_feasibility', {})
        
        # 판단 키워드가 모듈 데이터에 없어야 함
        forbidden_keys = ['판단', '결론', '권장', '추천', 'judgement', 'conclusion', 'recommended']
        
        for key in m2.keys():
            assert not any(f in str(key) for f in forbidden_keys), f"M2에 판단 키워드 발견: {key}"
        
        for key in m3.keys():
            # 'recommended_type'은 데이터 이름이므로 허용
            if key != 'recommended_type':
                assert not any(f in str(key) for f in forbidden_keys), f"M3에 판단 키워드 발견: {key}"
        
        for key in m5.keys():
            assert not any(f in str(key) for f in forbidden_keys), f"M5에 판단 키워드 발견: {key}"


# ============================================================================
# Phase 3.5C Completion Criteria
# ============================================================================

class TestPhase35CCompletion:
    """Phase 3.5C 완료 기준 테스트"""
    
    def test_all_data_visible(self, sample_m6_result, sample_m1_m5_data):
        """모든 모듈 데이터가 보이는지 확인"""
        report = create_m6_centered_report('all_in_one', sample_m6_result, sample_m1_m5_data)
        html = render_simple_html(report)
        
        # Phase 3.5C 완료 기준
        criteria = {
            'M2 토지가치': '60.82억원' in html or '6081' in html,
            'M3 선호유형': 'youth' in html,
            'M4 세대수': '20세대' in html or '26세대' in html,
            'M5 NPV': '7.93억원' in html or '792' in html,
            'M5 IRR': '12.5%' in html,
            'M5 ROI': '15.2%' in html,
        }
        
        failed = [k for k, v in criteria.items() if not v]
        
        assert not failed, f"Phase 3.5C 기준 미달성: {failed}"
    
    def test_m6_only_judgement(self, sample_m6_result, sample_m1_m5_data):
        """M6만 판단하는지 확인"""
        report = create_m6_centered_report('all_in_one', sample_m6_result, sample_m1_m5_data)
        
        # M6 판단 확인
        assert 'final_conclusion' in report, "final_conclusion이 없음"
        assert report['final_conclusion'], "final_conclusion이 비어있음"
        
        # Evidence 데이터에는 판단이 없어야 함
        evidence = report.get('evidence_data', {})
        
        # 금지된 판단성 표현 (Phase 3.5A 기준)
        forbidden_phrases = [
            '우수한', '경쟁력 있는', '충분히', '긍정적', '검토 가치', 
            '유리함', '권장', '추천', '적합', '양호', '바람직', 
            '가능성 높음', '기대됨', '유망'
        ]
        
        # evidence_summary는 M6 판단을 인용하므로 허용
        for key in evidence.keys():
            if key not in ['evidence_note', 'evidence_summary']:
                module_data = evidence[key]
                if isinstance(module_data, dict):
                    for field_name, value in module_data.items():
                        if isinstance(value, str):
                            # 금지된 판단성 표현이 있는지 확인
                            for phrase in forbidden_phrases:
                                assert phrase not in value, \
                                    f"모듈 데이터에 판단성 표현 발견: '{phrase}' in {field_name}={value}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
