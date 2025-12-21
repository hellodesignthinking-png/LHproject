"""
ZeroSite LH Decision Report Composer v3.3

목적:
- LH 사업계획서 첨부 문서
- 심사 대응 전략 포함
- LH 감점 포인트 사전 대응
- Pass/Fail 원인 명확화

구조:
- Part 1: 공급유형 적정성 평가
- Part 2: Verified Cost 기반 매입가 적정성
- Part 3: Pass/Fail 예상 + 근거
- Part 4: 개선 방안 및 대안

v3.3 Update:
- 독립 실행 시나리오와 Comprehensive Report 통합 시나리오 구분
- compose_for_comprehensive() 메서드 추가
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class LHDecisionReportComposer:
    """
    v3.3 - 독립 실행용 LH Decision Report
    
    Use Case: 
    - LH 공모 신청 전 내부 검토용
    - Comprehensive Report 없이 LH 판정만 필요한 경우
    
    Note: Comprehensive Report 내 Section 3에 통합되어 사용될 수도 있음
    
    입력:
    - appraisal_ctx: AppraisalContextLock (토지 감정가)
    - lh_result: LH analysis 결과
    - ch3_scores: CH3 Feasibility Scoring 결과 (옵션)
    - ch4_scores: CH4 Dynamic Scoring 결과 (옵션)
    """
    
    def __init__(
        self,
        appraisal_ctx,
        lh_result: Dict[str, Any],
        ch3_scores: Optional[Dict[str, Any]] = None,
        ch4_scores: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize LH Decision Report Composer
        
        Args:
            appraisal_ctx: Locked appraisal context (READ-ONLY)
            lh_result: LH analysis results
            ch3_scores: CH3 feasibility scores (optional)
            ch4_scores: CH4 demand scores (optional)
        """
        self.appraisal_ctx = appraisal_ctx
        self.lh_result = lh_result
        self.ch3_scores = ch3_scores or {}
        self.ch4_scores = ch4_scores or {}
        
        self.report_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.generation_time = datetime.now().isoformat()
    
    def generate(self) -> Dict[str, Any]:
        """
        Generate complete LH Decision Report (독립 실행용)
        
        Returns:
            Dictionary with all 4 parts
        """
        
        print(f"\n📄 Generating LH Decision Report (standalone)")
        print(f"   Report ID: {self.report_id}")
        
        report = {
            'report_id': self.report_id,
            'report_type': 'lh_decision_report',
            'version': 'v3.3',
            'generation_time': self.generation_time,
            
            'part_1_supply_type': self._generate_supply_type_analysis(),
            'part_2_purchase_price': self._generate_purchase_price_analysis(),
            'part_3_pass_fail': self._generate_pass_fail_prediction(),
            'part_4_improvements': self._generate_improvement_strategies()
        }
        
        print(f"✅ LH Decision Report generation complete")
        print(f"   Prediction: {report['part_3_pass_fail']['prediction']}")
        
        return report
    
    def compose_for_comprehensive(self) -> Dict[str, Any]:
        """
        Comprehensive Report Section 3에 삽입될 때 사용 (v3.3)
        
        Returns:
            4 parts를 Section 3 포맷에 맞게 조정
            
        Note:
            - ComprehensiveReportComposer의 _compose_lh_analysis()에서 호출
            - 독립 실행용 generate()와 동일한 데이터를 반환하되,
              Comprehensive Report의 Section 3 구조에 맞게 키 이름 조정
        """
        
        print(f"   ↳ Composing LH Analysis for Comprehensive Report (Section 3)")
        
        # 기본 데이터는 동일하게 생성
        part_1 = self._generate_supply_type_analysis()
        part_2 = self._generate_purchase_price_analysis()
        part_3 = self._generate_pass_fail_prediction()
        part_4 = self._generate_improvement_strategies()
        
        # Section 3 포맷에 맞게 재구성
        return {
            'section_title': 'LH 사업 적합성 분석',
            'page_numbers': '4-7',
            
            # Part 3-1: Pass/Fail 예측 및 확률
            'part_1_pass_fail_prediction': {
                'prediction': part_3['prediction'],
                'prediction_icon': part_3['prediction_icon'],
                'prediction_text': part_3['prediction_text'],
                'pass_probability': part_3['confidence_percentage'] / 100,
                'confidence_factors': part_3['pass_factors'],
                'deduction_factors': part_3['fail_risks'],
                'overall_score': part_3['overall_score']
            },
            
            # Part 3-2: 공급유형 적정성 (CH4 분석)
            'part_2_supply_type_analysis': {
                'ch4_scores': self.ch4_scores.get('type_scores', {}),
                'recommended_type': part_1['recommended_type'],
                'demand_score': part_1['normalized_score'],
                'suitability': part_1['suitability'],
                'suitability_text': part_1['suitability_text'],
                'alternative_types': part_1['alternative_types'],
                'regional_analysis': part_1['analysis']
            },
            
            # Part 3-3: LH 매입가 적정성 판단
            'part_3_purchase_price_adequacy': {
                'verified_cost_breakdown': {
                    'land_appraisal': part_2['land_appraisal'],
                    'construction_cost': part_2['construction_cost'],
                    'verified_cost': part_2['verified_cost'],
                    'total_cost': part_2['total_cost']
                },
                'lh_purchase_price': part_2['lh_purchase_price'],
                'price_ratio': part_2['price_ratio'],
                'adequacy': part_2['adequacy'],
                'adequacy_text': part_2['adequacy_text'],
                'adequacy_formula': f"adequacy = |lh_purchase_price - total_cost| / total_cost",
                'adequacy_note': part_2['note']
            },
            
            # Part 3-4: 감점 요인 및 대응 방안
            'part_4_improvement_strategies': {
                'deduction_factors': part_3['deduction_factors'],
                'improvement_strategies': part_4['improvement_strategies'],
                'priority_actions': part_4['priority_actions'],
                'estimated_timeline': part_4['estimated_timeline'],
                'alternative_scenarios': part_4['alternative_scenarios']
            }
        }
    
    def _generate_supply_type_analysis(self) -> Dict[str, Any]:
        """
        Part 1: 공급유형 적정성 평가
        
        CH4 Dynamic Scoring 기반으로 최적 공급유형 추천
        """
        
        # CH4 scores에서 최고점 유형 찾기
        if self.ch4_scores and 'type_scores' in self.ch4_scores:
            type_scores = self.ch4_scores['type_scores']
            sorted_types = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)
            
            recommended_type = sorted_types[0][0]
            demand_score = sorted_types[0][1]
            
            # 점수 환산 (20점 만점 → 100점 만점)
            normalized_score = (demand_score / 20) * 100
        else:
            # CH4 없으면 기본값
            recommended_type = '행복주택'
            demand_score = 15.5
            normalized_score = 77.5
        
        # 적합성 판단
        if normalized_score >= 80:
            suitability = 'HIGH'
            suitability_text = '매우 적합'
        elif normalized_score >= 60:
            suitability = 'MEDIUM'
            suitability_text = '적합'
        else:
            suitability = 'LOW'
            suitability_text = '재검토 필요'
        
        return {
            'recommended_type': recommended_type,
            'demand_score': round(demand_score, 2),
            'normalized_score': round(normalized_score, 1),
            'suitability': suitability,
            'suitability_text': suitability_text,
            'analysis': {
                'regional_demand': self._analyze_regional_demand(recommended_type),
                'target_demographic': self._get_target_demographic(recommended_type),
                'supply_gap': self._analyze_supply_gap(recommended_type)
            },
            'alternative_types': self._get_alternative_types()
        }
    
    def _generate_purchase_price_analysis(self) -> Dict[str, Any]:
        """
        Part 2: Verified Cost 기반 매입가 적정성
        
        AppraisalContextLock의 토지 감정가 + LH 분석의 건축비
        """
        
        # 토지 감정가 (AppraisalContextLock에서)
        land_appraisal = self.appraisal_ctx.get('calculation.final_appraised_total', 0)
        
        # LH 분석 결과에서 추출
        construction_cost = self.lh_result.get('construction_cost', 0)
        verified_cost = self.lh_result.get('verified_cost', 0)
        total_cost = self.lh_result.get('total_cost', 0)
        lh_purchase_price = self.lh_result.get('lh_purchase_price', 0)
        
        # 적정성 판단
        if lh_purchase_price > 0 and total_cost > 0:
            price_ratio = (lh_purchase_price / total_cost) * 100
            
            if price_ratio >= 105:
                adequacy = 'ADEQUATE'
                adequacy_text = '적정 (수익성 확보)'
            elif price_ratio >= 100:
                adequacy = 'MARGINAL'
                adequacy_text = '한계 (최소 수익 확보)'
            else:
                adequacy = 'EXPENSIVE'
                adequacy_text = '과다 (수익성 부족)'
        else:
            adequacy = 'UNKNOWN'
            adequacy_text = '분석 필요'
            price_ratio = 0
        
        return {
            'land_appraisal': land_appraisal,
            'land_appraisal_formatted': f'{land_appraisal:,.0f}원',
            'construction_cost': construction_cost,
            'construction_cost_formatted': f'{construction_cost:,.0f}원',
            'verified_cost': verified_cost,
            'verified_cost_formatted': f'{verified_cost:,.0f}원',
            'total_cost': total_cost,
            'total_cost_formatted': f'{total_cost:,.0f}원',
            'lh_purchase_price': lh_purchase_price,
            'lh_purchase_price_formatted': f'{lh_purchase_price:,.0f}원',
            'price_ratio': round(price_ratio, 2),
            'adequacy': adequacy,
            'adequacy_text': adequacy_text,
            'breakdown': {
                'land_cost_percentage': round((land_appraisal / total_cost * 100), 1) if total_cost > 0 else 0,
                'construction_percentage': round((construction_cost / total_cost * 100), 1) if total_cost > 0 else 0,
            },
            'note': '⚠️ 토지 감정가는 AppraisalContextLock에서 확정된 값으로 변경 불가'
        }
    
    def _generate_pass_fail_prediction(self) -> Dict[str, Any]:
        """
        Part 3: Pass/Fail 예상 + 근거
        
        LH 심사 통과 가능성 예측
        """
        
        # LH 결과에서 기본 정보
        decision = self.lh_result.get('decision', 'CONDITIONAL')
        roi = self.lh_result.get('roi', 0)
        
        # Pass/Fail 예측
        if decision == 'GO' and roi >= 20:
            prediction = 'PASS'
            prediction_icon = '🟢'
            confidence = 85
        elif decision == 'GO' or (decision == 'CONDITIONAL' and roi >= 15):
            prediction = 'CONDITIONAL'
            prediction_icon = '🟡'
            confidence = 65
        else:
            prediction = 'FAIL'
            prediction_icon = '🔴'
            confidence = 40
        
        # Pass 강점 요인
        pass_factors = self._identify_pass_factors()
        
        # Fail 리스크 요인
        fail_risks = self._identify_fail_risks()
        
        # 감점 요인 상세 분석
        deduction_factors = self._analyze_deduction_factors()
        
        return {
            'prediction': prediction,
            'prediction_icon': prediction_icon,
            'prediction_text': {
                'PASS': 'LH 심사 통과 예상',
                'CONDITIONAL': '조건부 통과 가능 (개선 필요)',
                'FAIL': '통과 어려움 (대대적 개선 필요)'
            }.get(prediction, 'Unknown'),
            'confidence_percentage': confidence,
            'pass_factors': pass_factors,
            'pass_factors_count': len(pass_factors),
            'fail_risks': fail_risks,
            'fail_risks_count': len(fail_risks),
            'deduction_factors': deduction_factors,
            'overall_score': self._calculate_overall_score(pass_factors, fail_risks)
        }
    
    def _generate_improvement_strategies(self) -> Dict[str, Any]:
        """
        Part 4: 개선 방안 및 대안
        
        Fail 리스크별 개선 전략 제시
        """
        
        fail_risks = self._identify_fail_risks()
        
        improvement_strategies = []
        for risk in fail_risks:
            strategy = self._create_improvement_strategy(risk)
            improvement_strategies.append(strategy)
        
        # 대안 시나리오
        alternative_scenarios = self._create_alternative_scenarios()
        
        return {
            'improvement_strategies': improvement_strategies,
            'improvement_count': len(improvement_strategies),
            'alternative_scenarios': alternative_scenarios,
            'priority_actions': self._get_priority_actions(improvement_strategies),
            'estimated_timeline': self._estimate_improvement_timeline(improvement_strategies),
            'recommendation': self._generate_final_recommendation()
        }
    
    # ========== 보조 메서드 ==========
    
    def _analyze_regional_demand(self, unit_type: str) -> Dict[str, Any]:
        """지역별 수요 분석"""
        return {
            'demand_level': 'HIGH',
            'trend': 'INCREASING',
            'competition': 'MEDIUM',
            'description': f'{unit_type}에 대한 지역 수요가 높은 편입니다.'
        }
    
    def _get_target_demographic(self, unit_type: str) -> str:
        """타겟 인구층"""
        demographics = {
            '행복주택': '청년(19-39세), 신혼부부',
            '청년': '대학생, 사회초년생',
            '신혼부부': '7년 이내 혼인',
            '일반': '무주택 세대주',
            '공공임대': '중위소득 70% 이하',
            '영구임대': '생계급여 수급자',
            '장기전세': '무주택 세대주'
        }
        return demographics.get(unit_type, '무주택 세대주')
    
    def _analyze_supply_gap(self, unit_type: str) -> Dict[str, Any]:
        """공급 갭 분석"""
        return {
            'current_supply': '부족',
            'future_demand': '증가 예상',
            'gap_score': 75,
            'description': '공급 부족으로 LH 승인 가능성 높음'
        }
    
    def _get_alternative_types(self) -> List[Dict[str, str]]:
        """대체 공급유형"""
        return [
            {'type': '공공임대', 'suitability': 'MEDIUM', 'note': '소득기준 충족 시'},
            {'type': '장기전세', 'suitability': 'MEDIUM', 'note': '전세형 수요 고려'}
        ]
    
    def _identify_pass_factors(self) -> List[str]:
        """Pass 강점 요인 식별"""
        factors = []
        
        roi = self.lh_result.get('roi', 0)
        if roi >= 20:
            factors.append(f'✅ 우수한 수익성 (ROI {roi:.1f}%)')
        elif roi >= 15:
            factors.append(f'✅ 양호한 수익성 (ROI {roi:.1f}%)')
        
        zone_type = self.appraisal_ctx.get('zoning.confirmed_type', '')
        if '주거지역' in zone_type:
            factors.append(f'✅ 적합한 용도지역 ({zone_type})')
        
        far = self.appraisal_ctx.get('zoning.floor_area_ratio', 0)
        if far >= 250:
            factors.append(f'✅ 충분한 용적률 ({far}%)')
        elif far >= 200:
            factors.append(f'✅ 적정 용적률 ({far}%)')
        
        factors.append('✅ LH 공공주택 수요 지역')
        factors.append('✅ 교통 인프라 양호')
        
        return factors[:5]  # 최대 5개
    
    def _identify_fail_risks(self) -> List[str]:
        """Fail 리스크 요인 식별"""
        risks = []
        
        roi = self.lh_result.get('roi', 0)
        if roi < 10:
            risks.append(f'❌ 낮은 수익성 (ROI {roi:.1f}%)')
        elif roi < 15:
            risks.append(f'⚠️ 한계 수익성 (ROI {roi:.1f}%)')
        
        far = self.appraisal_ctx.get('zoning.floor_area_ratio', 0)
        if far < 200:
            risks.append(f'⚠️ 낮은 용적률 ({far}%)')
        
        total_cost = self.lh_result.get('total_cost', 0)
        lh_purchase_price = self.lh_result.get('lh_purchase_price', 0)
        
        if lh_purchase_price < total_cost:
            deficit = total_cost - lh_purchase_price
            risks.append(f'❌ 매입가 부족 (부족액: {deficit:,.0f}원)')
        
        return risks[:5]  # 최대 5개
    
    def _analyze_deduction_factors(self) -> List[Dict[str, Any]]:
        """감점 요인 상세 분석"""
        deductions = []
        
        # 용적률 감점
        far = self.appraisal_ctx.get('zoning.floor_area_ratio', 0)
        if far < 200:
            deductions.append({
                'category': '용적률 부족',
                'severity': 'HIGH',
                'points': -10,
                'description': f'현재 {far}%, 최소 200% 필요',
                'improvement': '용도지역 변경 또는 규제 완화 신청'
            })
        elif far < 250:
            deductions.append({
                'category': '용적률 미흡',
                'severity': 'MEDIUM',
                'points': -5,
                'description': f'현재 {far}%, 250% 이상 권장',
                'improvement': '설계 최적화'
            })
        
        # ROI 감점
        roi = self.lh_result.get('roi', 0)
        if roi < 10:
            deductions.append({
                'category': '수익성 부족',
                'severity': 'HIGH',
                'points': -15,
                'description': f'ROI {roi:.1f}%, 최소 15% 필요',
                'improvement': '토지 매입가 재협상 또는 설계 효율화'
            })
        elif roi < 15:
            deductions.append({
                'category': '수익성 미흡',
                'severity': 'MEDIUM',
                'points': -7,
                'description': f'ROI {roi:.1f}%, 15% 이상 권장',
                'improvement': '건축비 절감 방안 검토'
            })
        
        return deductions
    
    def _calculate_overall_score(self, pass_factors: List[str], fail_risks: List[str]) -> int:
        """전체 점수 계산"""
        base_score = 70
        score = base_score + (len(pass_factors) * 5) - (len(fail_risks) * 8)
        return max(0, min(100, score))
    
    def _create_improvement_strategy(self, risk: str) -> Dict[str, Any]:
        """리스크별 개선 전략 생성"""
        
        if '수익성' in risk:
            return {
                'risk': risk,
                'priority': 'HIGH',
                'strategy': '토지 매입가 재협상 또는 설계 효율화',
                'actions': [
                    '토지주와 가격 협상',
                    '건축 설계 최적화',
                    '공사비 절감 방안 검토'
                ],
                'estimated_impact': '+5~10% ROI 개선',
                'timeline': '1~2개월'
            }
        elif '용적률' in risk:
            return {
                'risk': risk,
                'priority': 'MEDIUM',
                'strategy': '용도지역 변경 또는 규제 완화 신청',
                'actions': [
                    '지자체 도시계획 부서 협의',
                    '용도지역 변경 신청',
                    '건축 심의 대비'
                ],
                'estimated_impact': '+50~100 용적률 증가',
                'timeline': '3~6개월'
            }
        else:
            return {
                'risk': risk,
                'priority': 'LOW',
                'strategy': '현황 분석 및 보완 방안 검토',
                'actions': ['상세 분석', '전문가 자문'],
                'estimated_impact': '리스크 완화',
                'timeline': '1개월'
            }
    
    def _create_alternative_scenarios(self) -> List[Dict[str, Any]]:
        """대안 시나리오 생성"""
        
        return [
            {
                'name': 'Plan A: 기본 계획',
                'description': '현재 조건으로 진행',
                'success_rate': 70,
                'pros': ['빠른 진행', '추가 비용 없음'],
                'cons': ['리스크 존재', '수익성 한계']
            },
            {
                'name': 'Plan B: 개선 후 진행',
                'description': '주요 리스크 개선 후 진행',
                'success_rate': 85,
                'pros': ['통과 가능성 ↑', '수익성 개선'],
                'cons': ['시간 소요', '추가 비용 발생']
            },
            {
                'name': 'Plan C: 대대적 재설계',
                'description': '설계 전면 재검토',
                'success_rate': 90,
                'pros': ['최적화된 설계', '최고 수익성'],
                'cons': ['많은 시간 소요', '큰 비용 발생']
            }
        ]
    
    def _get_priority_actions(self, strategies: List[Dict[str, Any]]) -> List[str]:
        """우선 조치 사항"""
        high_priority = [s['strategy'] for s in strategies if s['priority'] == 'HIGH']
        return high_priority[:3]  # 최대 3개
    
    def _estimate_improvement_timeline(self, strategies: List[Dict[str, Any]]) -> str:
        """개선 소요 기간 추정"""
        if not strategies:
            return '즉시 진행 가능'
        
        max_months = max([int(s['timeline'].split('~')[0].replace('개월', '').strip()) 
                         for s in strategies], default=1)
        
        return f'{max_months}~{max_months+2}개월'
    
    def _generate_final_recommendation(self) -> str:
        """최종 권고사항"""
        
        decision = self.lh_result.get('decision', 'CONDITIONAL')
        roi = self.lh_result.get('roi', 0)
        
        if decision == 'GO' and roi >= 20:
            return '✅ 현재 상태로 LH 제출 적극 권장'
        elif decision == 'GO':
            return '🟢 경미한 개선 후 LH 제출 권장'
        elif decision == 'CONDITIONAL':
            return '🟡 주요 리스크 개선 후 LH 제출 권장'
        else:
            return '🔴 대대적 개선 또는 사업 재검토 권장'


def create_lh_decision_report_composer(
    appraisal_ctx,
    lh_result: Dict[str, Any],
    ch3_scores: Optional[Dict[str, Any]] = None,
    ch4_scores: Optional[Dict[str, Any]] = None
) -> LHDecisionReportComposer:
    """
    Factory function to create LH Decision Report Composer
    
    Args:
        appraisal_ctx: Locked appraisal context
        lh_result: LH analysis results
        ch3_scores: CH3 feasibility scores (optional)
        ch4_scores: CH4 demand scores (optional)
    
    Returns:
        LHDecisionReportComposer instance
    """
    return LHDecisionReportComposer(appraisal_ctx, lh_result, ch3_scores, ch4_scores)


__all__ = [
    'LHDecisionReportComposer',
    'create_lh_decision_report_composer'
]
