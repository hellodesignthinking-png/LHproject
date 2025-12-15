"""
ZeroSite Pre-Report Composer v3.3 (2 pages)

목적:
- 신규 고객 유입 (무료 또는 저가 제공) - 영업 도구
- 계약 전 사업성·가능성 판단
- LH 가능성 High/Medium/Low 표시
- 종합보고서 계약 유도 (CTA)

구조 (v3.3 Updated):
- Page 1: Executive Summary (영업 관점 강조)
  - 대상 토지 기본 정보
  - LH 신축매입임대 사업 가능성 (시각적 게이지)
  - 핵심 지표 3개 (개발가능 연면적, 예상 세대수, 추천 공급유형)
  - 주요 장점 (bullet 3개)
  - 검토 필요 사항 (bullet 1-2개)
  
- Page 2: Quick Analysis (개발 개요 + CTA 강조)
  - 개발 개요 테이블
  - 추천 공급유형 시각화 (CH4 스코어 바 차트)
  - "다음 단계" CTA 섹션 (종합보고서 안내)
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime


class PreReportComposer:
    """
    Pre-Report (2페이지) 생성기
    
    입력:
    - appraisal_ctx: AppraisalContextLock (감정평가 결과)
    - land_diagnosis: Land diagnosis 결과
    - lh_result: LH analysis 결과
    - ch4_scores: CH4 Dynamic Scoring 결과 (옵션)
    """
    
    def __init__(
        self,
        appraisal_ctx,
        land_diagnosis: Dict[str, Any],
        lh_result: Dict[str, Any],
        ch4_scores: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Pre-Report Composer v3.3
        
        Args:
            appraisal_ctx: Locked appraisal context (READ-ONLY)
            land_diagnosis: Land diagnosis results
            lh_result: LH analysis results
            ch4_scores: CH4 demand scores (optional)
        """
        self.appraisal_ctx = appraisal_ctx
        self.land_diagnosis = land_diagnosis
        self.lh_result = lh_result
        self.ch4_scores = ch4_scores or {}
        
        self.report_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.generation_time = datetime.now().isoformat()
        self.version = "v3.3"
    
    def generate(self) -> Dict[str, Any]:
        """
        Generate complete 2-page Pre-Report v3.3
        
        Returns:
            Dictionary with page_1 (Executive Summary) and page_2 (Quick Analysis) data
        """
        
        print(f"\n📄 Generating Pre-Report v3.3 (2 pages)")
        print(f"   Report ID: {self.report_id}")
        
        report = {
            'report_id': self.report_id,
            'report_type': 'pre_report',
            'version': self.version,
            'generation_time': self.generation_time,
            'total_pages': 2,
            
            'page_1_executive_summary': self._generate_page_1_executive_summary(),
            'page_2_quick_analysis': self._generate_page_2_quick_analysis()
        }
        
        print(f"✅ Pre-Report v3.3 generation complete")
        print(f"   LH Possibility: {report['page_1_executive_summary']['lh_possibility_gauge']}")
        
        return report
    
    def _generate_page_1_executive_summary(self) -> Dict[str, Any]:
        """
        Page 1: Executive Summary (v3.3 - 영업 관점 강조)
        
        포함 내용:
        - 대상 토지 기본 정보 (주소, 면적, 용도지역)
        - LH 신축매입임대 사업 가능성 (시각적 게이지: HIGH/MEDIUM/LOW)
        - 핵심 지표 3개: 개발가능 연면적, 예상 세대수, 추천 공급유형
        - 주요 장점 (bullet 3개)
        - 검토 필요 사항 (bullet 1-2개)
        """
        
        # 기본 정보 추출
        address = self.land_diagnosis.get('address', 'N/A')
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm', 0)
        zone_type = self.appraisal_ctx.get('zoning.confirmed_type', 'N/A')
        far = self.appraisal_ctx.get('zoning.floor_area_ratio', 0)
        bcr = self.appraisal_ctx.get('zoning.building_coverage_ratio', 0)
        
        # 개발가능 연면적 계산
        total_buildable_area = land_area * (far / 100) if far > 0 else 0
        
        # 예상 세대수 범위 계산 (평균 전용면적 60~80㎡ 가정)
        min_units = int(total_buildable_area / 80) if total_buildable_area > 0 else 0
        max_units = int(total_buildable_area / 60) if total_buildable_area > 0 else 0
        estimated_units_avg = int((min_units + max_units) / 2)
        
        # 추천 세대유형 (CH4 scores 기반)
        recommended_types = self._get_recommended_unit_types()
        top_recommended_type = recommended_types[0]['type'] if recommended_types else '행복주택'
        
        # LH 가능성 판단
        lh_possibility, lh_color = self._calculate_lh_possibility()
        
        # 주요 장점 추출
        key_strengths = self._extract_key_strengths()
        
        # 검토 필요 사항 추출
        review_items = self._extract_review_items()
        
        return {
            'title': 'Executive Summary',
            'subtitle': 'LH 신축매입임대 사업 초기 검토 결과',
            
            # 대상 토지 기본 정보
            'land_basic_info': {
                'address': address,
                'land_area_sqm': land_area,
                'land_area_pyeong': round(land_area / 3.3058, 1),
                'zone_type': zone_type,
                'zone_type_formatted': f"{zone_type} (FAR {far}%, BCR {bcr}%)"
            },
            
            # LH 사업 가능성 게이지 (시각적)
            'lh_possibility_gauge': lh_possibility,
            'lh_possibility_color': lh_color,
            'lh_possibility_icon': self._get_lh_icon(lh_possibility),
            'lh_possibility_description': self._get_possibility_description(lh_possibility),
            
            # 핵심 지표 3개
            'key_metrics': {
                '1_buildable_area': {
                    'label': '개발가능 연면적',
                    'value': round(total_buildable_area, 1),
                    'unit': '㎡',
                    'value_pyeong': round(total_buildable_area / 3.3058, 1),
                    'description': f'토지면적 {land_area}㎡ × 용적률 {far}%'
                },
                '2_estimated_units': {
                    'label': '예상 세대수',
                    'value': estimated_units_avg,
                    'unit': '세대',
                    'range': f'{min_units}~{max_units}세대',
                    'description': '전용면적 60~80㎡ 기준'
                },
                '3_recommended_supply_type': {
                    'label': '추천 공급유형',
                    'value': top_recommended_type,
                    'unit': '',
                    'description': 'CH4 수요 분석 기반 최적 유형'
                }
            },
            
            # 주요 장점 (bullet 3개)
            'key_strengths': key_strengths,
            
            # 검토 필요 사항 (bullet 1-2개)
            'review_items': review_items
        }
    
    def _generate_page_2_quick_analysis(self) -> Dict[str, Any]:
        """
        Page 2: Quick Analysis (v3.3 - 개발 개요 + CTA 강조)
        
        포함 내용:
        - 개발 개요 테이블 (건폐율/용적률, 최고층수, 예상연면적, 예상세대수, 필요주차대수)
        - 추천 공급유형 시각화 (CH4 스코어 바 차트: 청년/신혼/고령/일반)
        - "다음 단계" CTA 섹션 (종합보고서 안내)
        """
        
        # 기본 정보 추출
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm', 0)
        zone_type = self.appraisal_ctx.get('zoning.confirmed_type', 'N/A')
        far = self.appraisal_ctx.get('zoning.floor_area_ratio', 0)
        bcr = self.appraisal_ctx.get('zoning.building_coverage_ratio', 0)
        
        # 개발 개요 계산
        total_buildable_area = land_area * (far / 100) if far > 0 else 0
        min_units = int(total_buildable_area / 80) if total_buildable_area > 0 else 0
        max_units = int(total_buildable_area / 60) if total_buildable_area > 0 else 0
        estimated_units_avg = int((min_units + max_units) / 2)
        
        # 최고층수 추정 (단순 계산: 용적률 기준)
        estimated_max_floors = int(far / bcr) if bcr > 0 else 0
        
        # 필요 주차대수 (세대당 1.0대 기준)
        required_parking = estimated_units_avg
        
        # 추천 공급유형 시각화 데이터 (CH4 스코어)
        supply_type_chart = self._generate_supply_type_chart()
        
        return {
            'title': 'Quick Analysis',
            'subtitle': '개발 개요 및 다음 단계 안내',
            
            # 개발 개요 테이블
            'development_overview_table': {
                '1_regulations': {
                    'item': '건폐율 / 용적률',
                    'value': f'{bcr}% / {far}%',
                    'note': zone_type
                },
                '2_max_floors': {
                    'item': '예상 최고층수',
                    'value': f'약 {estimated_max_floors}층',
                    'note': '용적률 기준 추정 (실제 높이제한 확인 필요)'
                },
                '3_buildable_area': {
                    'item': '예상 연면적',
                    'value': f'{round(total_buildable_area, 1):,}㎡',
                    'note': f'{round(total_buildable_area / 3.3058, 1):,}평'
                },
                '4_estimated_units': {
                    'item': '예상 세대수',
                    'value': f'약 {estimated_units_avg}세대',
                    'note': f'{min_units}~{max_units}세대 범위'
                },
                '5_required_parking': {
                    'item': '필요 주차대수',
                    'value': f'약 {required_parking}대',
                    'note': '세대당 1.0대 기준 (지역별 상이)'
                }
            },
            
            # 추천 공급유형 시각화 (CH4 스코어 바 차트)
            'supply_type_visualization': supply_type_chart,
            
            # "다음 단계" CTA 섹션
            'next_steps_cta': {
                'title': '📋 다음 단계: 종합보고서 계약 안내',
                'intro_text': '본 Pre-Report는 초기 검토용입니다.\n정식 컨설팅 계약 시 다음 내용이 포함된 종합보고서를 제공합니다:',
                'features': [
                    '✓ LH 매입가 적정성 분석 (Verified Cost 기반)',
                    '✓ 상세 수익성 분석 (IRR/ROI/NPV)',
                    '✓ 리스크 매트릭스 및 대응 방안',
                    '✓ LH Pass/Fail 상세 예측 및 감점 요인'
                ],
                'report_types': [
                    '• 종합보고서 (Comprehensive Report): 15-20페이지',
                    '• Full Report: 60페이지 (감정평가 + 토지진단 + LH 판단)'
                ],
                'contact_info': {
                    'title': '상담 문의',
                    'phone': '1234-5678',
                    'email': 'contact@zerosite.com',
                    'note': '정식 계약 시 상세 분석 + 전문가 컨설팅 제공'
                }
            }
        }
    
    def _get_recommended_unit_types(self) -> List[Dict[str, Any]]:
        """
        추천 세대유형 도출 (CH4 scores 기반)
        
        Returns:
            Top 2 추천 유형
        """
        
        if not self.ch4_scores:
            # CH4 scores 없으면 기본값 반환
            return [
                {'type': '행복주택', 'score': 85, 'suitability': 'HIGH'},
                {'type': '청년', 'score': 82, 'suitability': 'HIGH'}
            ]
        
        # CH4 scores에서 상위 2개 추출
        type_scores = self.ch4_scores.get('type_scores', {})
        sorted_types = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)[:2]
        
        recommended = []
        for unit_type, score in sorted_types:
            suitability = 'HIGH' if score >= 15 else 'MEDIUM' if score >= 10 else 'LOW'
            recommended.append({
                'type': unit_type,
                'score': round(score * 5, 1),  # 20점 만점 → 100점 환산
                'suitability': suitability
            })
        
        return recommended
    
    def _calculate_lh_possibility(self) -> Tuple[str, str]:
        """
        LH 가능성 판단
        
        Returns:
            (possibility: 'HIGH'|'MEDIUM'|'LOW', color: 'green'|'yellow'|'red')
        """
        
        # LH 분석 결과에서 판단
        decision = self.lh_result.get('decision', 'CONDITIONAL')
        roi = self.lh_result.get('roi', 0)
        
        # Decision + ROI 기반 판단
        if decision == 'GO' and roi >= 20:
            return 'HIGH', 'green'
        elif decision == 'GO' or (decision == 'CONDITIONAL' and roi >= 15):
            return 'MEDIUM', 'yellow'
        else:
            return 'LOW', 'red'
    
    def _get_lh_icon(self, possibility: str) -> str:
        """LH 가능성 아이콘"""
        icons = {
            'HIGH': '🟢',
            'MEDIUM': '🟡',
            'LOW': '🔴'
        }
        return icons.get(possibility, '⚪')
    
    def _evaluate_risk_items(self) -> List[Dict[str, Any]]:
        """
        6대 리스크 항목 평가
        
        Returns:
            List of risk evaluation results
        """
        
        # 기본 정보 추출
        zone_type = self.appraisal_ctx.get('zoning.confirmed_type', '')
        far = self.appraisal_ctx.get('zoning.floor_area_ratio', 0)
        bcr = self.appraisal_ctx.get('zoning.building_coverage_ratio', 0)
        roi = self.lh_result.get('roi', 0)
        
        risk_items = []
        
        # 1. 용도지역 적합성
        zone_suitable = '주거지역' in zone_type or '준주거지역' in zone_type
        risk_items.append({
            'category': '용도지역 적합성',
            'status': 'PASS' if zone_suitable else 'WARNING',
            'description': f'{zone_type} - LH 공공주택 개발 {"적합" if zone_suitable else "검토 필요"}',
            'detail': '제2종일반주거지역 이상 권장'
        })
        
        # 2. 용적률 충족 여부
        far_adequate = far >= 200
        risk_items.append({
            'category': '용적률 충족',
            'status': 'PASS' if far_adequate else 'FAIL',
            'description': f'용적률 {far}% - {"충분" if far_adequate else "부족"} (최소 200% 권장)',
            'detail': '용적률이 높을수록 개발 가능 세대수 증가'
        })
        
        # 3. 건폐율 적정성
        bcr_adequate = 40 <= bcr <= 60
        risk_items.append({
            'category': '건폐율 적정성',
            'status': 'PASS' if bcr_adequate else 'WARNING',
            'description': f'건폐율 {bcr}% - {"적정" if bcr_adequate else "확인 필요"}',
            'detail': '40~60% 범위가 이상적'
        })
        
        # 4. 주변 인프라
        # (실제로는 상세 분석 필요, 여기서는 기본값)
        risk_items.append({
            'category': '주변 인프라',
            'status': 'PASS',
            'description': '역세권 또는 주요 교통시설 접근 가능',
            'detail': '대중교통 접근성 확인 필요'
        })
        
        # 5. 접근성
        risk_items.append({
            'category': '접근성',
            'status': 'PASS',
            'description': '도로 접근 가능 (도로 폭 확인 필요)',
            'detail': '최소 6m 이상 도로 접면 권장'
        })
        
        # 6. 수익성 (ROI)
        roi_good = roi >= 15
        risk_items.append({
            'category': '수익성',
            'status': 'PASS' if roi_good else 'WARNING',
            'description': f'ROI {roi:.1f}% - {"양호" if roi_good else "재검토 필요"}',
            'detail': '15% 이상 권장'
        })
        
        return risk_items
    
    def _get_overall_assessment(self, pass_count: int, warning_count: int, fail_count: int) -> str:
        """전체 평가 요약"""
        
        total = pass_count + warning_count + fail_count
        
        if fail_count >= 2:
            return '❌ LH 진행 재검토 필요 (중대 리스크 존재)'
        elif fail_count == 1 or warning_count >= 3:
            return '⚠️ 조건부 진행 가능 (개선 방안 필요)'
        elif pass_count >= 5:
            return '✅ LH 진행 적극 권장 (양호한 조건)'
        else:
            return '🟡 LH 진행 가능 (일부 보완 필요)'
    
    def _get_possibility_description(self, possibility: str) -> str:
        """LH 가능성 설명 텍스트"""
        descriptions = {
            'HIGH': '본 토지는 LH 신축매입임대 사업에 매우 적합한 조건을 갖추고 있습니다.',
            'MEDIUM': '본 토지는 LH 신축매입임대 사업 진행이 가능하나, 일부 개선이 필요합니다.',
            'LOW': '본 토지는 현재 조건으로 LH 사업 진행이 어려우며, 대대적 개선이 필요합니다.'
        }
        return descriptions.get(possibility, '추가 검토가 필요합니다.')
    
    def _extract_key_strengths(self) -> List[str]:
        """주요 장점 추출 (bullet 3개)"""
        strengths = []
        
        # 1. ROI 기반
        roi = self.lh_result.get('roi', 0)
        if roi >= 20:
            strengths.append(f'✓ 우수한 수익성 (예상 ROI {roi:.1f}%)')
        elif roi >= 15:
            strengths.append(f'✓ 양호한 수익성 (예상 ROI {roi:.1f}%)')
        
        # 2. 용도지역 기반
        zone_type = self.appraisal_ctx.get('zoning.confirmed_type', '')
        if '주거지역' in zone_type:
            strengths.append(f'✓ LH 공공주택 개발에 적합한 용도지역 ({zone_type})')
        
        # 3. 용적률 기반
        far = self.appraisal_ctx.get('zoning.floor_area_ratio', 0)
        if far >= 250:
            strengths.append(f'✓ 충분한 용적률 ({far}%)로 세대수 확보 유리')
        elif far >= 200:
            strengths.append(f'✓ 적정한 용적률 ({far}%)로 개발 가능')
        
        # 4. CH4 기반
        if self.ch4_scores and 'type_scores' in self.ch4_scores:
            type_scores = self.ch4_scores['type_scores']
            max_score = max(type_scores.values()) if type_scores else 0
            if max_score >= 15:
                top_type = max(type_scores, key=type_scores.get)
                strengths.append(f'✓ 높은 수요가 예상되는 공급유형 ({top_type}) 적합')
        
        # 기본값 (장점이 부족한 경우)
        if len(strengths) < 3:
            strengths.append('✓ LH 공공주택 정책 수혜 가능 지역')
            strengths.append('✓ 교통 접근성 양호 (추가 검토 필요)')
        
        return strengths[:3]  # 최대 3개
    
    def _extract_review_items(self) -> List[str]:
        """검토 필요 사항 추출 (bullet 1-2개)"""
        review_items = []
        
        # 1. ROI 기반
        roi = self.lh_result.get('roi', 0)
        if roi < 15:
            review_items.append(f'• 수익성 개선 방안 검토 필요 (현재 ROI {roi:.1f}%)')
        
        # 2. 용적률 기반
        far = self.appraisal_ctx.get('zoning.floor_area_ratio', 0)
        if far < 200:
            review_items.append(f'• 용적률 부족 (현재 {far}%) - 용도지역 변경 또는 규제 완화 검토')
        
        # 3. 건폐율 기반
        bcr = self.appraisal_ctx.get('zoning.building_coverage_ratio', 0)
        if bcr < 40 or bcr > 60:
            review_items.append(f'• 건폐율 확인 필요 (현재 {bcr}%)')
        
        # 4. Decision 기반
        decision = self.lh_result.get('decision', 'CONDITIONAL')
        if decision == 'NOT_RECOMMENDED':
            review_items.append('• LH 사업 진행 여부 재검토 필요 (대안 검토)')
        
        # 기본값 (검토 사항이 없는 경우)
        if len(review_items) == 0:
            review_items.append('• 인허가 절차 사전 확인 권장')
        
        return review_items[:2]  # 최대 2개
    
    def _generate_supply_type_chart(self) -> Dict[str, Any]:
        """추천 공급유형 시각화 데이터 (CH4 스코어 바 차트)"""
        
        if not self.ch4_scores or 'type_scores' not in self.ch4_scores:
            # CH4 scores 없으면 기본값
            return {
                'chart_type': 'horizontal_bar',
                'data': [
                    {'type': '행복주택', 'score': 85, 'percentage': 85},
                    {'type': '청년', 'score': 82, 'percentage': 82},
                    {'type': '신혼부부', 'score': 78, 'percentage': 78},
                    {'type': '일반', 'score': 70, 'percentage': 70}
                ]
            }
        
        # CH4 scores에서 데이터 추출 및 정규화
        type_scores = self.ch4_scores['type_scores']
        
        # 20점 만점 → 100점 환산
        chart_data = []
        for unit_type, score in sorted(type_scores.items(), key=lambda x: x[1], reverse=True):
            normalized_score = (score / 20) * 100
            chart_data.append({
                'type': unit_type,
                'score': round(score, 2),
                'percentage': round(normalized_score, 1)
            })
        
        return {
            'chart_type': 'horizontal_bar',
            'title': '공급유형별 수요 점수 (CH4 분석)',
            'data': chart_data,
            'note': '점수가 높을수록 해당 유형에 대한 지역 수요가 높음'
        }


def create_pre_report_composer(
    appraisal_ctx,
    land_diagnosis: Dict[str, Any],
    lh_result: Dict[str, Any],
    ch4_scores: Optional[Dict[str, Any]] = None
) -> PreReportComposer:
    """
    Factory function to create Pre-Report Composer v3.3
    
    v3.3 Changes:
    - Page 1: Executive Summary (영업 도구로 강화)
    - Page 2: Quick Analysis with CTA (종합보고서 유도)
    
    Args:
        appraisal_ctx: Locked appraisal context (READ-ONLY)
        land_diagnosis: Land diagnosis results
        lh_result: LH analysis results
        ch4_scores: CH4 demand scores (optional, enhances supply type recommendations)
    
    Returns:
        PreReportComposer v3.3 instance
    """
    return PreReportComposer(appraisal_ctx, land_diagnosis, lh_result, ch4_scores)


__all__ = [
    'PreReportComposer',
    'create_pre_report_composer'
]
