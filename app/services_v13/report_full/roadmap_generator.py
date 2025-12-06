"""
ZeroSite Expert Edition v3: 36-Month Roadmap Generator
=======================================================

Generates comprehensive 36-month implementation roadmap (2-3 pages) covering:
- Phase 1: Preparation & Approval (Months 1-6)
- Phase 2: Design & Contracting (Months 7-12)
- Phase 3: Construction (Months 13-30)
- Phase 4: Completion & Handover (Months 31-36)

Includes Gantt-style timeline, key milestones, resource allocation,
and risk management checkpoints.

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0 (Expert Edition)
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RoadmapGenerator:
    """
    Generate Expert-level 36-month implementation roadmap
    
    Target: 2-3 pages with actionable timeline
    Style: Gantt chart + narrative milestones
    """
    
    def __init__(self):
        """Initialize roadmap generator"""
        logger.info("✅ RoadmapGenerator initialized")
    
    def generate_roadmap(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive 36-month implementation roadmap
        
        Args:
            context: Report context from ReportContextBuilder
        
        Returns:
            Dict with roadmap phases, milestones, and timeline
        """
        logger.info("🗓️ Generating 36-month implementation roadmap...")
        
        address = context['site']['address']
        housing_type = context['demand']['recommended_type_kr']
        decision = context['decision']['recommendation']
        
        # Generate start date (assumed 3 months from report date)
        start_date = datetime.now() + timedelta(days=90)
        
        roadmap = {
            'overview': self._generate_overview(decision, housing_type),
            'start_date': start_date.strftime('%Y년 %m월'),
            'end_date': (start_date + timedelta(days=1095)).strftime('%Y년 %m월'),  # 36 months
            'phases': self._generate_phases(start_date),
            'milestones': self._generate_milestones(start_date),
            'resources': self._generate_resource_allocation(),
            'risk_checkpoints': self._generate_risk_checkpoints(),
            'success_criteria': self._generate_success_criteria()
        }
        
        logger.info("✅ 36-month roadmap complete")
        return roadmap
    
    def _generate_overview(self, decision: str, housing_type: str) -> str:
        """Generate roadmap overview narrative"""
        
        if decision == 'GO':
            overview = f"""
본 36개월 실행 로드맵은 LH 신축매입임대 {housing_type} 사업의 계획 수립부터 준공 및 인도까지의 전체 과정을 체계적으로 제시합니다. 
본 로드맵은 국토교통부 '공공주택 사업 관리 지침', LH '신축매입임대주택 사업 실무 매뉴얼', 
그리고 실제 사업 경험을 바탕으로 작성되었으며, 각 단계별 소요 기간, 주요 업무, 핵심 산출물, 리스크 관리 포인트를 포함합니다.

전체 사업 기간 36개월은 4개 Phase로 구성됩니다. Phase 1(준비 및 승인, 1-6개월)은 사업 계획 수립, 인허가 확보, 
LH 사전협의 완료를 목표로 합니다. Phase 2(설계 및 계약, 7-12개월)는 상세 설계 확정, 건설사 선정, 공사 계약 체결을 수행합니다. 
Phase 3(건설, 13-30개월)는 토목/건축 공사, 품질 관리, LH 감리를 진행합니다. 
Phase 4(준공 및 인도, 31-36개월)는 준공 검사, LH 매입, 입주자 모집 및 인도를 완료합니다.

본 로드맵의 특징은 '선행 업무 최대화 전략'으로, 인허가와 설계를 동시 진행하여 전체 기간을 3개월 단축하고, 
'리스크 관리 체계'로 각 Phase마다 3회의 리스크 점검 지점을 설정하여 조기 경보 시스템을 운영하며, 
'유연성 확보'로 각 Phase에 1개월의 예비 기간을 포함하여 불확실성에 대응할 수 있도록 설계되었습니다.
"""
        elif decision == 'CONDITIONAL':
            overview = f"""
본 36개월 실행 로드맵은 조건부 추진 시나리오를 반영하여 작성되었습니다. 
우선 Phase 0(사전 조건 충족, 0-3개월)를 통해 재무 구조 개선, 대지 규모 확대, 또는 정책 변화 대기 등 
조건부 권고 사항을 해결한 후, 본격적인 36개월 실행 로드맵이 시작됩니다.

조건 충족 후 전체 기간은 39개월(사전 조건 3개월 + 실행 36개월)이 소요되며, 
조건 미충족 시 사업은 보류 또는 재설계 단계로 전환됩니다. 
각 조건의 해결 가능성과 소요 시간을 사전에 명확히 평가하여 최종 의사결정을 내리는 것이 중요합니다.
"""
        elif decision == 'REVISE':
            overview = f"""
본 로드맵은 대규모 재설계를 전제로 작성되었습니다. 
Phase 0(재설계 및 재평가, 0-6개월)를 통해 대지 규모 확대, 인근 필지 병합, 또는 개발 계획 변경을 수행한 후, 
재분석을 통해 타당성을 재검증합니다. 재설계 완료 및 타당성 확보 시 36개월 실행 로드맵이 시작되며, 
전체 기간은 42개월(재설계 6개월 + 실행 36개월)이 소요됩니다.
"""
        else:  # NO-GO
            overview = f"""
현재 조건에서는 사업 추진이 권장되지 않으므로, 본 로드맵은 참고 자료로만 활용하시기 바랍니다. 
사업 추진을 위해서는 대지 규모 확대, 입지 변경, 또는 정책 환경 개선 등 근본적인 조건 변화가 필요하며, 
이 경우 새로운 타당성 분석과 로드맵 재작성이 필요합니다.
"""
        
        return overview.strip()
    
    def _generate_phases(self, start_date: datetime) -> List[Dict[str, Any]]:
        """Generate detailed 4-phase breakdown"""
        
        phases = []
        
        # Phase 1: Preparation & Approval (1-6 months)
        phase1_start = start_date
        phase1_end = start_date + timedelta(days=180)
        phases.append({
            'phase_number': 1,
            'phase_name': '준비 및 승인',
            'phase_name_en': 'Preparation & Approval',
            'start_month': 1,
            'end_month': 6,
            'duration_months': 6,
            'start_date': phase1_start.strftime('%Y년 %m월'),
            'end_date': phase1_end.strftime('%Y년 %m월'),
            'key_activities': [
                '사업 계획서 작성 및 내부 검토',
                '지자체 사전 협의 및 인허가 신청',
                'LH 사전협의 신청 및 승인',
                '감정평가 3사 선정 및 평가',
                '설계 공모 및 건축사 선정',
                '토지 소유권 확인 및 매매 계약'
            ],
            'deliverables': [
                '사업계획승인서',
                'LH 사전협의 완료 통보서',
                '건축허가증',
                '감정평가서 (3사 평균)',
                '설계 용역 계약서',
                '토지 매매계약서'
            ],
            'resources': {
                '인력': '프로젝트 매니저 1명, 기획팀 3명, 법무팀 2명',
                '예산': '설계비 2억원, 감정평가비 5천만원, 인허가비 3천만원',
                '협력사': '설계사무소, 감정평가법인 3사, 법무법인'
            },
            'risks': [
                {
                    'risk': '인허가 지연 (예상 확률 30%)',
                    'impact': '전체 일정 1-2개월 지연',
                    'mitigation': 'Fast Track 제도 활용, 사전 협의 강화'
                },
                {
                    'risk': 'LH 사전협의 부결 (예상 확률 15%)',
                    'impact': '사업 구조 재설계 필요 (3개월 소요)',
                    'mitigation': '사전 컨설팅 통해 LH 기준 충족 여부 확인'
                },
                {
                    'risk': '감정평가 하락 (예상 확률 25%)',
                    'impact': '매입가 10% 감소, NPV 악화',
                    'mitigation': '다양한 평가 기법 활용, 인근 시세 조사 철저히'
                }
            ],
            'checkpoints': [
                {'month': 2, 'checkpoint': 'LH 사전협의 완료'},
                {'month': 4, 'checkpoint': '건축허가 확보'},
                {'month': 6, 'checkpoint': 'Phase 1 완료 검토'}
            ]
        })
        
        # Phase 2: Design & Contracting (7-12 months)
        phase2_start = phase1_end
        phase2_end = phase1_end + timedelta(days=180)
        phases.append({
            'phase_number': 2,
            'phase_name': '설계 및 계약',
            'phase_name_en': 'Design & Contracting',
            'start_month': 7,
            'end_month': 12,
            'duration_months': 6,
            'start_date': phase2_start.strftime('%Y년 %m월'),
            'end_date': phase2_end.strftime('%Y년 %m월'),
            'key_activities': [
                '건축 기본설계 및 LH 검토',
                '건축 실시설계 완료',
                '시공사 입찰 공고 및 평가',
                '공사 계약 체결',
                '금융 조달 계약 (PF)',
                'LH 매입 확약서 체결'
            ],
            'deliverables': [
                '기본설계도서 (LH 승인)',
                '실시설계도서',
                '공사계약서',
                '금융 약정서 (PF 대출)',
                'LH 매입 확약서',
                '착공 신고서'
            ],
            'resources': {
                '인력': '설계팀 5명, 시공팀 3명, 금융팀 2명',
                '예산': '실시설계비 5억원, 입찰 준비비 1억원',
                '협력사': '건축설계사무소, 시공사, 금융기관'
            },
            'risks': [
                {
                    'risk': '설계 변경 요청 (예상 확률 40%)',
                    'impact': '일정 1개월 지연, 설계비 10% 증가',
                    'mitigation': 'LH 사전 검토 강화, 표준설계 활용'
                },
                {
                    'risk': '시공사 선정 지연 (예상 확률 20%)',
                    'impact': '착공 1-2개월 지연',
                    'mitigation': '복수 후보사 확보, 조기 입찰 공고'
                },
                {
                    'risk': 'PF 금리 상승 (예상 확률 30%)',
                    'impact': '금융비용 20% 증가',
                    'mitigation': '복수 금융기관 협의, 금리 상한 설정'
                }
            ],
            'checkpoints': [
                {'month': 8, 'checkpoint': '기본설계 LH 승인'},
                {'month': 10, 'checkpoint': '시공사 선정'},
                {'month': 12, 'checkpoint': '착공 신고 완료'}
            ]
        })
        
        # Phase 3: Construction (13-30 months)
        phase3_start = phase2_end
        phase3_end = phase2_end + timedelta(days=540)
        phases.append({
            'phase_number': 3,
            'phase_name': '건설',
            'phase_name_en': 'Construction',
            'start_month': 13,
            'end_month': 30,
            'duration_months': 18,
            'start_date': phase3_start.strftime('%Y년 %m월'),
            'end_date': phase3_end.strftime('%Y년 %m월'),
            'key_activities': [
                '토공사 및 기초 공사 (2개월)',
                '골조 공사 (6개월)',
                '마감 공사 (6개월)',
                '설비 및 전기 공사 (4개월, 병행)',
                'LH 중간 감리 (분기별 3회)',
                '안전 점검 및 품질 검사 (상시)'
            ],
            'deliverables': [
                '골조 완료 보고서',
                '마감 완료 보고서',
                'LH 중간 감리 보고서 (3회)',
                '품질 검사 합격증',
                '안전 점검 통과 확인서'
            ],
            'resources': {
                '인력': '현장 소장 1명, 감리단 5명, 안전 관리자 2명',
                '예산': '공사비 100억원 (단계별 지급)',
                '협력사': '시공사, 감리단, 전문 건설사 (설비/전기)'
            },
            'risks': [
                {
                    'risk': '공사비 증가 (예상 확률 50%)',
                    'impact': '사업비 10-15% 초과',
                    'mitigation': '계약서에 물가연동제 반영, 예비비 10% 확보'
                },
                {
                    'risk': '공기 지연 (예상 확률 35%)',
                    'impact': '준공 2-3개월 지연',
                    'mitigation': '공정표 주간 점검, 지체상금 조항 설정'
                },
                {
                    'risk': '안전 사고 (예상 확률 10%)',
                    'impact': '공사 중단 1-2개월, 보상금',
                    'mitigation': '안전 교육 강화, 보험 가입'
                },
                {
                    'risk': 'LH 감리 부적합 (예상 확률 20%)',
                    'impact': '재시공 비용 및 일정 지연',
                    'mitigation': 'LH 기준 철저히 준수, 사전 협의'
                }
            ],
            'checkpoints': [
                {'month': 15, 'checkpoint': '기초 공사 완료 및 LH 1차 감리'},
                {'month': 21, 'checkpoint': '골조 공사 완료 및 LH 2차 감리'},
                {'month': 27, 'checkpoint': '마감 공사 완료 및 LH 3차 감리'},
                {'month': 30, 'checkpoint': 'Phase 3 완료 검토'}
            ]
        })
        
        # Phase 4: Completion & Handover (31-36 months)
        phase4_start = phase3_end
        phase4_end = phase3_end + timedelta(days=180)
        phases.append({
            'phase_number': 4,
            'phase_name': '준공 및 인도',
            'phase_name_en': 'Completion & Handover',
            'start_month': 31,
            'end_month': 36,
            'duration_months': 6,
            'start_date': phase4_start.strftime('%Y년 %m월'),
            'end_date': phase4_end.strftime('%Y년 %m월'),
            'key_activities': [
                '사용승인 신청 및 확보',
                'LH 최종 감리 및 매입 검사',
                'LH 매입 계약 체결 및 대금 지급',
                '입주자 모집 공고',
                '입주자 자격 심사',
                '임대차 계약 체결 및 인도'
            ],
            'deliverables': [
                '사용승인서',
                'LH 매입 확인서',
                '매매계약서',
                '입주자 명단',
                '임대차계약서',
                '인도인수증'
            ],
            'resources': {
                '인력': 'PM 1명, 법무팀 2명, 입주관리팀 3명',
                '예산': '준공 검사비 3천만원, 마케팅비 2천만원',
                '협력사': 'LH, 입주관리대행사'
            },
            'risks': [
                {
                    'risk': '사용승인 지연 (예상 확률 25%)',
                    'impact': '인도 1-2개월 지연, 입주율 저하',
                    'mitigation': '사전 서류 완비, 지자체 협조'
                },
                {
                    'risk': 'LH 매입 거부 (예상 확률 5%)',
                    'impact': '사업 실패, 재무 손실',
                    'mitigation': '공사 단계부터 LH 기준 철저히 준수'
                },
                {
                    'risk': '입주율 저조 (예상 확률 15%)',
                    'impact': '임대수익 감소, NOI 저하',
                    'mitigation': '마케팅 강화, 임대료 탄력적 조정'
                }
            ],
            'checkpoints': [
                {'month': 32, 'checkpoint': '사용승인 확보'},
                {'month': 34, 'checkpoint': 'LH 매입 계약 체결'},
                {'month': 36, 'checkpoint': 'Phase 4 완료 및 사업 종료'}
            ]
        })
        
        return phases
    
    def _generate_milestones(self, start_date: datetime) -> List[Dict[str, Any]]:
        """Generate key milestones with dates"""
        
        milestones = []
        
        milestone_data = [
            {'month': 2, 'name': 'LH 사전협의 완료', 'critical': True},
            {'month': 4, 'name': '건축허가 확보', 'critical': True},
            {'month': 6, 'name': 'Phase 1 완료', 'critical': False},
            {'month': 8, 'name': '기본설계 승인', 'critical': True},
            {'month': 10, 'name': '시공사 선정', 'critical': True},
            {'month': 12, 'name': '착공 신고', 'critical': True},
            {'month': 15, 'name': '기초 공사 완료', 'critical': False},
            {'month': 21, 'name': '골조 공사 완료', 'critical': False},
            {'month': 27, 'name': '마감 공사 완료', 'critical': False},
            {'month': 30, 'name': 'Phase 3 완료', 'critical': False},
            {'month': 32, 'name': '사용승인 확보', 'critical': True},
            {'month': 34, 'name': 'LH 매입 완료', 'critical': True},
            {'month': 36, 'name': '입주 완료 및 사업 종료', 'critical': True}
        ]
        
        for m in milestone_data:
            milestone_date = start_date + timedelta(days=30 * m['month'])
            milestones.append({
                'month': m['month'],
                'name': m['name'],
                'date': milestone_date.strftime('%Y년 %m월'),
                'critical': m['critical'],
                'description': f"{m['month']}개월차 주요 이정표"
            })
        
        return milestones
    
    def _generate_resource_allocation(self) -> Dict[str, Any]:
        """Generate resource allocation plan"""
        
        return {
            'narrative': """
본 사업의 36개월 동안 소요되는 자원은 인력, 예산, 협력사 3개 카테고리로 구분됩니다.

인력 자원은 Phase별로 변동되며, Phase 1(준비 및 승인)에는 내부 기획/법무팀 중심으로 5-7명, 
Phase 2(설계 및 계약)에는 설계/시공 전문가 추가로 10-12명, 
Phase 3(건설)에는 현장 인력 중심으로 50-70명(감리 포함), 
Phase 4(준공 및 인도)에는 입주관리팀 중심으로 5-8명이 투입됩니다.

예산 자원은 총 사업비 150억원 기준으로, Phase 1에 설계/인허가비 3억원(2%), 
Phase 2에 실시설계/금융비 8억원(5%), Phase 3에 건설비 130억원(87%), 
Phase 4에 준공/마케팅비 1억원(1%), 예비비 8억원(5%)이 배분됩니다.

협력사 자원은 설계사무소(7-12개월), 시공사(13-30개월), 금융기관(7-36개월), 
감리단(13-30개월), LH(전 기간) 등이 단계별로 투입됩니다.
""",
            'workforce': {
                'phase_1': {'count': [5, 7], 'composition': '기획팀 + 법무팀'},
                'phase_2': {'count': [10, 12], 'composition': '설계팀 + 시공팀 + 금융팀'},
                'phase_3': {'count': [50, 70], 'composition': '현장팀 + 감리단 + 안전팀'},
                'phase_4': {'count': [5, 8], 'composition': '입주관리팀 + 법무팀'}
            },
            'budget': {
                'phase_1': {'amount': 3e8, 'pct': 2.0, 'description': '설계/인허가비'},
                'phase_2': {'amount': 8e8, 'pct': 5.3, 'description': '실시설계/금융비'},
                'phase_3': {'amount': 130e8, 'pct': 86.7, 'description': '건설비'},
                'phase_4': {'amount': 1e8, 'pct': 0.7, 'description': '준공/마케팅비'},
                'reserve': {'amount': 8e8, 'pct': 5.3, 'description': '예비비'},
                'total': 150e8
            },
            'partners': [
                {'type': '설계사무소', 'engagement_months': '7-12'},
                {'type': '시공사', 'engagement_months': '13-30'},
                {'type': '금융기관', 'engagement_months': '7-36'},
                {'type': '감리단', 'engagement_months': '13-30'},
                {'type': 'LH', 'engagement_months': '전 기간'}
            ]
        }
    
    def _generate_risk_checkpoints(self) -> List[Dict[str, Any]]:
        """Generate quarterly risk review checkpoints"""
        
        return [
            {
                'quarter': 'Q1 (1-3개월)',
                'focus': 'LH 사전협의 및 인허가',
                'review_items': ['사전협의 진행 상황', '인허가 서류 완비도', '지자체 협의 진도'],
                'action_trigger': '2개월 경과 시점까지 사전협의 미완료 시 에스컬레이션'
            },
            {
                'quarter': 'Q2 (4-6개월)',
                'focus': '건축허가 및 설계 착수',
                'review_items': ['건축허가 확보 여부', '설계사 선정 완료', '감정평가 진행'],
                'action_trigger': '4개월 경과 시점까지 건축허가 미확보 시 법무 자문'
            },
            {
                'quarter': 'Q3 (7-9개월)',
                'focus': '기본설계 및 입찰 준비',
                'review_items': ['기본설계 LH 승인', '시공사 입찰 공고', 'PF 금융 협의'],
                'action_trigger': '8개월 경과 시점까지 기본설계 미승인 시 재설계'
            },
            {
                'quarter': 'Q4 (10-12개월)',
                'focus': '실시설계 및 착공 준비',
                'review_items': ['실시설계 완료', '시공사 선정', '착공 신고'],
                'action_trigger': '11개월 경과 시점까지 시공사 미선정 시 재입찰'
            },
            {
                'quarter': 'Q5-Q8 (13-24개월)',
                'focus': '건설 공정 관리',
                'review_items': ['공정률 (목표 대비)', '공사비 집행률', 'LH 감리 결과', '안전 사고 발생'],
                'action_trigger': '공정 지연 10% 이상 시 회복 계획 수립'
            },
            {
                'quarter': 'Q9-Q10 (25-30개월)',
                'focus': '마감 공사 및 준공 준비',
                'review_items': ['마감 공정률', 'LH 최종 감리 준비', '사용승인 서류 준비'],
                'action_trigger': '29개월 경과 시점까지 마감 미완료 시 공기 연장 검토'
            },
            {
                'quarter': 'Q11-Q12 (31-36개월)',
                'focus': '준공 및 입주',
                'review_items': ['사용승인 확보', 'LH 매입 완료', '입주율'],
                'action_trigger': '33개월 경과 시점까지 사용승인 미확보 시 법적 대응'
            }
        ]
    
    def _generate_success_criteria(self) -> Dict[str, Any]:
        """Generate success criteria for roadmap completion"""
        
        return {
            'narrative': """
36개월 로드맵의 성공적 완료는 다음 기준으로 평가됩니다.

정량적 기준으로는 첫째, 일정 준수로 36개월 이내 사업 완료(±3개월 허용), 
둘째, 예산 준수로 초기 사업비 대비 110% 이내 집행, 
셋째, 품질 준수로 LH 감리 및 사용승인 일회 통과, 
넷째, 입주율로 6개월 이내 95% 이상 달성이 포함됩니다.

정성적 기준으로는 LH 관계 유지로 협력 관계 긍정적 평가, 
안전 관리로 중대 사고 Zero 달성, 지역사회 협력으로 민원 최소화, 
팀 역량 강화로 차기 프로젝트 적용 가능한 노하우 축적이 있습니다.

최종 성공 판단은 재무적 목표 달성(NPV ≥ 0, IRR ≥ 2%), 
LH 만족도(Good 이상 평가), 입주자 만족도(평균 4.0/5.0 이상)를 종합하여 결정됩니다.
""",
            'quantitative': [
                {'criterion': '일정 준수', 'target': '36개월 ±3개월', 'weight': 30},
                {'criterion': '예산 준수', 'target': '초기 예산 110% 이내', 'weight': 25},
                {'criterion': '품질 준수', 'target': 'LH 감리 일회 통과', 'weight': 25},
                {'criterion': '입주율', 'target': '6개월 내 95% 이상', 'weight': 20}
            ],
            'qualitative': [
                'LH 관계 긍정적 평가 (Good 이상)',
                '중대 안전 사고 Zero',
                '민원 최소화 (분기당 5건 이하)',
                '차기 프로젝트 적용 가능한 노하우 축적'
            ],
            'final_success': [
                '재무적 목표 달성 (NPV ≥ 0, IRR ≥ 2%)',
                'LH 만족도 Good 이상',
                '입주자 만족도 평균 4.0/5.0 이상'
            ]
        }


# Convenience function
def generate_implementation_roadmap(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to generate 36-month implementation roadmap
    
    Args:
        context: Report context from ReportContextBuilder
    
    Returns:
        Roadmap dictionary
    """
    generator = RoadmapGenerator()
    return generator.generate_roadmap(context)
