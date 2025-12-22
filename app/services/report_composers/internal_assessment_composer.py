"""
ZeroSite Internal Assessment Composer v1.0 (5 pages)

목적:
- 내부 의사결정용 간략 평가서
- Model A (직접개발) 시 빠른 Go/No-Go 판단용
- 토지 발굴 후 초기 스크리닝
- 내부 회의용 자료

구조 (5개 섹션):
- Section 1: Executive Decision (1장)
- Section 2: Key Metrics (1장)
- Section 3: Risk Flags (1장)
- Section 4: Financial Snapshot (1장)
- Section 5: Action Items (1장)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class InternalAssessmentComposer:
    """
    v1.0 Internal Assessment - 내부 의사결정용
    Target: 내부 전용 (5 pages)
    
    Focus: 빠른 Go/No-Go 판단
    """
    
    def __init__(
        self,
        appraisal_ctx,
        land_diagnosis: Dict[str, Any],
        lh_result: Dict[str, Any],
        ch4_scores: Optional[Dict[str, Any]] = None,
        risk_matrix: Optional[Dict[str, Any]] = None,
        financial_analysis: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Internal Assessment Composer
        
        Args:
            appraisal_ctx: Locked appraisal context (READ-ONLY)
            land_diagnosis: Land diagnosis results
            lh_result: LH analysis results
            ch4_scores: CH4 demand scores (optional)
            risk_matrix: Risk matrix analysis (optional)
            financial_analysis: Financial engine results (optional)
        """
        self.appraisal_ctx = appraisal_ctx
        self.land_diagnosis = land_diagnosis
        self.lh_result = lh_result
        self.ch4_scores = ch4_scores or {}
        self.risk_matrix = risk_matrix or {}
        self.financial_analysis = financial_analysis or {}
        
        self.report_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.generation_time = datetime.now().isoformat()
        self.version = "v1.0"
    
    def compose(self) -> Dict[str, Any]:
        """
        Generate complete Internal Assessment (5 pages)
        
        Returns:
            Dictionary with all 5 sections
        """
        
        print(f"\n📄 Generating Internal Assessment v1.0 (5 pages)")
        print(f"   Report ID: {self.report_id}")
        print(f"   Focus: Quick Go/No-Go Decision")
        
        report = {
            'report_id': self.report_id,
            'report_type': 'internal_assessment',
            'version': self.version,
            'generation_time': self.generation_time,
            'estimated_pages': '5',
            
            'section_1_executive_decision': self._compose_executive_decision(),
            'section_2_key_metrics': self._compose_key_metrics(),
            'section_3_risk_flags': self._compose_risk_flags(),
            'section_4_financial_snapshot': self._compose_financial_snapshot(),
            'section_5_action_items': self._compose_action_items()
        }
        
        # Set actual page count
        report['actual_pages'] = 5
        
        print(f"✅ Internal Assessment v1.0 generation complete")
        print(f"   Total Pages: 5")
        print(f"   Decision: {report['section_1_executive_decision']['final_decision']['decision']}")
        print(f"   Overall Score: {report['section_2_key_metrics']['overall_score']}/100")
        
        return report
    
    def _compose_executive_decision(self) -> Dict[str, Any]:
        """
        Section 1: Executive Decision (1장)
        최종 의사결정 요약
        """
        
        # Extract key data
        address = '서울특별시 마포구 월드컵북로 120'  # Mock
        review_date = datetime.now().strftime("%Y-%m-%d")
        
        # Calculate decision based on multiple factors
        roi = self.lh_result.get('roi', 0)
        lh_decision = self.lh_result.get('decision', 'GO')
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm')
        far = self.appraisal_ctx.get('zoning.floor_area_ratio', 0)
        
        # Decision logic
        decision_factors = {
            'lh_possibility': lh_decision == 'GO',
            'roi_adequate': roi >= 10,
            'far_adequate': far >= 200,
            'no_critical_risks': True  # Simplified
        }
        
        passed_factors = sum(decision_factors.values())
        total_factors = len(decision_factors)
        
        # Final decision
        if passed_factors >= 4:
            decision = 'GO'
            decision_icon = '✅'
            decision_color = 'green'
        elif passed_factors >= 3:
            decision = 'CONDITIONAL'
            decision_icon = '⚠️'
            decision_color = 'yellow'
        else:
            decision = 'NO-GO'
            decision_icon = '❌'
            decision_color = 'red'
        
        # Decision rationale
        if decision == 'GO':
            rationale = f"LH 통과 가능성 HIGH, IRR {roi:.1f}% 이상 예상되어 추진 권고"
        elif decision == 'CONDITIONAL':
            rationale = f"조건부 추진 가능, 일부 개선 필요 (ROI {roi:.1f}%)"
        else:
            rationale = f"수익성 미달 또는 LH 승인 리스크 높음 (ROI {roi:.1f}%)"
        
        # Conditions (if CONDITIONAL)
        conditions = []
        if decision == 'CONDITIONAL':
            if roi < 15:
                conditions.append('토지 매입가 협상 필수 (목표: 10% 인하)')
            if far < 200:
                conditions.append('FAR 상향 가능성 검토')
            if not decision_factors['no_critical_risks']:
                conditions.append('Critical 리스크 해결 방안 확보')
        
        return {
            'title': '🎯 의사결정 요약',
            'page_number': 1,
            
            # Target info
            'target_info': {
                'address': address,
                'review_date': review_date,
                'reviewer': '내부 검토팀'
            },
            
            # Final decision
            'final_decision': {
                'decision': decision,
                'decision_icon': decision_icon,
                'decision_color': decision_color,
                'rationale': rationale,
                'confidence': f'{(passed_factors / total_factors) * 100:.0f}%'
            },
            
            # Decision factors
            'decision_factors': decision_factors,
            'passed_factors_count': passed_factors,
            'total_factors_count': total_factors,
            
            # Conditions (if any)
            'conditions': conditions if conditions else ['조건 없음 - 즉시 추진 가능'],
            'has_conditions': len(conditions) > 0
        }
    
    def _compose_key_metrics(self) -> Dict[str, Any]:
        """
        Section 2: Key Metrics (1장)
        핵심 지표 평가
        """
        
        # Extract metrics
        lh_decision = self.lh_result.get('decision', 'GO')
        roi = self.lh_result.get('roi', 0)
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm')
        far = self.appraisal_ctx.get('zoning.floor_area_ratio', 0)
        appraised_total = self.appraisal_ctx.get('calculation.final_appraised_total')
        
        # Calculate LH possibility percentage
        if lh_decision == 'GO':
            lh_possibility_pct = 85
        elif lh_decision == 'CONDITIONAL':
            lh_possibility_pct = 65
        else:
            lh_possibility_pct = 35
        
        # Estimate units
        buildable_area = land_area * (far / 100)
        estimated_units = int(buildable_area / 70)  # 70㎡ per unit average
        
        # Calculate risk score (simplified)
        risk_score = 25  # Mock - would come from risk_matrix
        
        # Price adequacy
        asking_price = appraised_total * 1.07
        price_adequacy_pct = ((asking_price - appraised_total) / appraised_total) * 100
        
        # Create metrics table
        metrics = {
            'lh_possibility': {
                'label': 'LH 가능성',
                'value': lh_possibility_pct,
                'threshold': 75,
                'unit': '%',
                'judgment': '✅' if lh_possibility_pct >= 75 else '⚠️' if lh_possibility_pct >= 60 else '❌',
                'status': 'PASS' if lh_possibility_pct >= 75 else 'WARNING' if lh_possibility_pct >= 60 else 'FAIL'
            },
            'estimated_units': {
                'label': '예상 세대수',
                'value': estimated_units,
                'threshold': 50,
                'unit': '세대',
                'judgment': '✅' if estimated_units >= 50 else '⚠️' if estimated_units >= 30 else '❌',
                'status': 'PASS' if estimated_units >= 50 else 'WARNING' if estimated_units >= 30 else 'FAIL'
            },
            'expected_irr': {
                'label': '예상 IRR',
                'value': roi,
                'threshold': 10,
                'unit': '%',
                'judgment': '✅' if roi >= 10 else '⚠️' if roi >= 7 else '❌',
                'status': 'PASS' if roi >= 10 else 'WARNING' if roi >= 7 else 'FAIL'
            },
            'risk_score': {
                'label': '리스크 점수',
                'value': risk_score,
                'threshold': 30,
                'unit': '/100',
                'judgment': '✅' if risk_score <= 30 else '⚠️' if risk_score <= 50 else '❌',
                'status': 'PASS' if risk_score <= 30 else 'WARNING' if risk_score <= 50 else 'FAIL',
                'note': '낮을수록 좋음'
            },
            'price_adequacy': {
                'label': '토지가 적정성',
                'value': price_adequacy_pct,
                'threshold': 10,
                'unit': '%',
                'judgment': '✅' if price_adequacy_pct <= 10 else '⚠️' if price_adequacy_pct <= 15 else '❌',
                'status': 'PASS' if price_adequacy_pct <= 10 else 'WARNING' if price_adequacy_pct <= 15 else 'FAIL',
                'note': '호가 대비 적정가 차이'
            }
        }
        
        # Calculate overall score
        scores = []
        for metric in metrics.values():
            if metric['status'] == 'PASS':
                scores.append(100)
            elif metric['status'] == 'WARNING':
                scores.append(70)
            else:
                scores.append(40)
        
        overall_score = int(sum(scores) / len(scores))
        
        # Overall assessment
        if overall_score >= 85:
            overall_assessment = '우수 - 적극 추진 권장'
            overall_color = 'green'
        elif overall_score >= 70:
            overall_assessment = '양호 - 추진 가능'
            overall_color = 'blue'
        elif overall_score >= 55:
            overall_assessment = '보통 - 조건부 추진'
            overall_color = 'yellow'
        else:
            overall_assessment = '미흡 - 재검토 필요'
            overall_color = 'red'
        
        return {
            'title': '핵심 지표 평가',
            'page_number': 2,
            
            'metrics': metrics,
            'overall_score': overall_score,
            'overall_assessment': overall_assessment,
            'overall_color': overall_color,
            
            # Status counts
            'pass_count': sum(1 for m in metrics.values() if m['status'] == 'PASS'),
            'warning_count': sum(1 for m in metrics.values() if m['status'] == 'WARNING'),
            'fail_count': sum(1 for m in metrics.values() if m['status'] == 'FAIL'),
            'total_metrics': len(metrics)
        }
    
    def _compose_risk_flags(self) -> Dict[str, Any]:
        """
        Section 3: Risk Flags (1장)
        리스크 플래그 분류
        """
        
        # Risk assessment
        far = self.appraisal_ctx.get('zoning.floor_area_ratio', 0)
        bcr = self.appraisal_ctx.get('zoning.building_coverage_ratio', 0)
        land_area = self.appraisal_ctx.get('calculation.land_area_sqm')
        roi = self.lh_result.get('roi', 0)
        
        # Categorize risks
        critical_risks = []
        warning_risks = []
        clear_items = []
        
        # Critical risks (즉시 해결 필요)
        if roi < 5:
            critical_risks.append({
                'risk': '수익성 심각 미달',
                'detail': f'ROI {roi:.1f}% < 5% 기준',
                'action': '사업 재검토 또는 중단'
            })
        
        if far < 150:
            critical_risks.append({
                'risk': 'FAR 현저히 부족',
                'detail': f'FAR {far}% < 150% 최소 기준',
                'action': 'FAR 상향 조정 협의 또는 사업 포기'
            })
        
        # Warning risks (검토 필요)
        if roi < 10:
            warning_risks.append({
                'risk': '수익성 개선 필요',
                'detail': f'ROI {roi:.1f}% < 10% 목표',
                'action': '토지가 협상 또는 공사비 절감'
            })
        
        # Mock parking issue
        estimated_units = int(land_area * (far / 100) / 70)
        required_parking = estimated_units
        available_parking = int(land_area * (bcr / 100) / 25)  # 25㎡ per space
        
        if available_parking < required_parking:
            warning_risks.append({
                'risk': '주차장 확보 면적 부족',
                'detail': f'필요 {required_parking}대, 가능 {available_parking}대',
                'action': '기계식 주차장 또는 인근 공영주차장 활용'
            })
        
        # Mock road access
        warning_risks.append({
            'risk': '도로 접근성 협소',
            'detail': '4m 도로 접면',
            'action': '도로 확장 가능성 검토'
        })
        
        # Clear items
        clear_items.append({
            'item': '용도지역 적합',
            'detail': '제2종일반주거지역 - LH 공공주택 개발 가능'
        })
        
        clear_items.append({
            'item': '인허가 리스크 낮음',
            'detail': '지구단위계획 미해당, 특별 규제 없음'
        })
        
        if self.ch4_scores:
            clear_items.append({
                'item': 'LH 공급유형 적합',
                'detail': 'CH4 분석 결과 수요 충분'
            })
        
        return {
            'title': '리스크 플래그',
            'page_number': 3,
            
            # Critical risks
            'critical_risks': {
                'label': '🔴 Critical (즉시 해결 필요)',
                'risks': critical_risks,
                'count': len(critical_risks)
            },
            
            # Warning risks
            'warning_risks': {
                'label': '🟡 Warning (검토 필요)',
                'risks': warning_risks,
                'count': len(warning_risks)
            },
            
            # Clear items
            'clear_items': {
                'label': '🟢 Clear',
                'items': clear_items,
                'count': len(clear_items)
            },
            
            # Summary
            'risk_summary': {
                'has_critical': len(critical_risks) > 0,
                'has_warnings': len(warning_risks) > 0,
                'overall_status': 'CRITICAL' if len(critical_risks) > 0 else 'WARNING' if len(warning_risks) > 0 else 'CLEAR'
            }
        }
    
    def _compose_financial_snapshot(self) -> Dict[str, Any]:
        """
        Section 4: Financial Snapshot (1장)
        재무 스냅샷
        """
        
        # Extract financial data
        land_appraisal = self.appraisal_ctx.get('calculation.final_appraised_total')
        construction_cost = self.lh_result.get('analysis_result', {}).get('construction_cost', 0)
        total_cost = self.lh_result.get('analysis_result', {}).get('total_cost', 0)
        lh_purchase_price = self.lh_result.get('lh_purchase_price', 0)
        roi = self.lh_result.get('roi', 0)
        
        # Calculate expected profit
        expected_profit = lh_purchase_price - total_cost
        
        # Payback period (simplified)
        if roi > 0:
            payback_months = int(100 / roi * 12)
        else:
            payback_months = 999
        
        # IRR (use ROI as approximation)
        irr = roi
        
        return {
            'title': '재무 스냅샷',
            'page_number': 4,
            
            # Cost breakdown
            'cost_breakdown': {
                'land_cost': {
                    'label': '예상 토지비',
                    'value': land_appraisal,
                    'formatted': f'{land_appraisal / 100000000:.1f}억원'
                },
                'construction_cost': {
                    'label': '예상 건축비',
                    'value': construction_cost,
                    'formatted': f'{construction_cost / 100000000:.1f}억원'
                },
                'total_project_cost': {
                    'label': '총 사업비',
                    'value': total_cost,
                    'formatted': f'{total_cost / 100000000:.1f}억원'
                },
                'lh_purchase_price': {
                    'label': 'LH 매입가',
                    'value': lh_purchase_price,
                    'formatted': f'{lh_purchase_price / 100000000:.1f}억원'
                },
                'expected_profit': {
                    'label': '예상 순이익',
                    'value': expected_profit,
                    'formatted': f'{expected_profit / 100000000:.1f}억원'
                }
            },
            
            # Key metrics
            'key_financial_metrics': {
                'irr': {
                    'label': 'IRR',
                    'value': irr,
                    'formatted': f'{irr:.1f}%',
                    'assessment': '우수' if irr >= 15 else '양호' if irr >= 10 else '보통' if irr >= 5 else '미흡'
                },
                'roi': {
                    'label': 'ROI',
                    'value': roi,
                    'formatted': f'{roi:.1f}%',
                    'assessment': '우수' if roi >= 20 else '양호' if roi >= 15 else '보통' if roi >= 10 else '미흡'
                },
                'payback_period': {
                    'label': '회수기간',
                    'value': payback_months,
                    'formatted': f'{payback_months}개월',
                    'assessment': '양호' if payback_months <= 24 else '보통' if payback_months <= 36 else '장기'
                }
            },
            
            # Quick assessment
            'quick_assessment': {
                'profitability': '양호' if roi >= 10 else '미흡',
                'profitability_color': 'green' if roi >= 10 else 'red',
                'note': f'예상 ROI {roi:.1f}%로 {"투자 기준 충족" if roi >= 10 else "투자 기준 미달"}'
            }
        }
    
    def _compose_action_items(self) -> Dict[str, Any]:
        """
        Section 5: Action Items (1장)
        실행 계획
        """
        
        # Determine action items based on decision
        decision = self._get_decision_status()
        
        # Immediate actions
        immediate_actions = []
        if decision in ['GO', 'CONDITIONAL']:
            immediate_actions.append({
                'priority': 'HIGH',
                'action': '토지주 접촉 및 가격 협상 시작',
                'owner': '토지개발팀',
                'status': 'PENDING'
            })
        
        if decision == 'CONDITIONAL':
            immediate_actions.append({
                'priority': 'HIGH',
                'action': '주요 리스크 해결 방안 검토',
                'owner': '리스크관리팀',
                'status': 'PENDING'
            })
        
        # 1-week actions
        one_week_actions = []
        if decision in ['GO', 'CONDITIONAL']:
            one_week_actions.append({
                'priority': 'HIGH',
                'action': '현장 실사 수행',
                'owner': '현장조사팀',
                'deadline': (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            })
            
            one_week_actions.append({
                'priority': 'MEDIUM',
                'action': '상세 인허가 검토',
                'owner': '인허가팀',
                'deadline': (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            })
        
        # Decision deadline
        decision_deadline = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Responsible person
        responsible_person = '프로젝트 매니저'
        
        # Next steps
        if decision == 'GO':
            next_steps = [
                '즉시: 토지 매입 협상 착수',
                '1주: 현장 실사 및 인허가 상세 검토',
                '2주: 시공사 견적 요청',
                '1개월: 최종 투자 의사결정'
            ]
        elif decision == 'CONDITIONAL':
            next_steps = [
                '즉시: 조건 충족 방안 검토',
                '1주: 리스크 해소 계획 수립',
                '2주: 조건 충족 가능성 재평가',
                '1개월: Go/No-Go 최종 판단'
            ]
        else:
            next_steps = [
                '사업 중단',
                '대안 토지 탐색',
                '프로젝트 종료 보고'
            ]
        
        return {
            'title': 'Action Items',
            'page_number': 5,
            
            # Immediate actions
            'immediate_actions': {
                'label': '✅ 즉시 조치',
                'actions': immediate_actions,
                'count': len(immediate_actions)
            },
            
            # 1-week actions
            'one_week_actions': {
                'label': '📋 1주일 내',
                'actions': one_week_actions,
                'count': len(one_week_actions)
            },
            
            # Decision info
            'decision_info': {
                'decision_deadline': decision_deadline,
                'responsible_person': responsible_person,
                'approval_required': '투자위원회' if decision == 'GO' else '사업개발본부장'
            },
            
            # Next steps
            'next_steps': next_steps,
            'next_steps_count': len(next_steps)
        }
    
    # ========== Helper Methods ==========
    
    def _get_decision_status(self) -> str:
        """Get current decision status"""
        roi = self.lh_result.get('roi', 0)
        lh_decision = self.lh_result.get('decision', 'GO')
        
        if roi >= 10 and lh_decision == 'GO':
            return 'GO'
        elif roi >= 7 and lh_decision in ['GO', 'CONDITIONAL']:
            return 'CONDITIONAL'
        else:
            return 'NO-GO'
