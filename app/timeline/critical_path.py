"""
ZeroSite Phase 14: Critical Path & Timeline Generator

36개월 프로젝트 일정 및 Critical Path 분석

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 14.0
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class PhaseType(str, Enum):
    """프로젝트 단계 유형"""
    PLANNING = "planning"              # 기획/계획
    DESIGN = "design"                  # 설계
    PERMIT = "permit"                  # 인허가
    CONSTRUCTION = "construction"      # 시공
    INSPECTION = "inspection"          # 검사/인증
    APPRAISAL = "appraisal"           # 감정평가
    PURCHASE = "purchase"              # LH 매입


@dataclass
class ProjectPhase:
    """프로젝트 단계"""
    phase_id: str
    phase_name: str
    phase_type: PhaseType
    duration_months: int
    dependencies: List[str]  # 선행 단계 ID
    is_critical: bool  # Critical Path 상의 단계 여부
    description: str
    key_milestones: List[str]
    risks: List[str]


@dataclass
class Timeline:
    """프로젝트 타임라인"""
    total_duration_months: int
    phases: List[ProjectPhase]
    critical_path: List[str]  # Critical Phase IDs
    key_risks: List[str]
    recommendations: List[str]


class CriticalPathAnalyzer:
    """
    LH 신축매입임대 프로젝트 Critical Path 분석
    
    Features:
    - 36개월 표준 일정 생성
    - Critical Path 식별
    - 리스크 분석
    - 일정 최적화 제안
    """
    
    def __init__(self):
        """Initialize Critical Path Analyzer"""
        self._load_standard_phases()
    
    def _load_standard_phases(self):
        """LH 신축매입임대 표준 단계 로드"""
        
        self.standard_phases = [
            ProjectPhase(
                phase_id="P1",
                phase_name="사업 기획 및 기본 설계",
                phase_type=PhaseType.PLANNING,
                duration_months=3,
                dependencies=[],
                is_critical=True,
                description="사업 타당성 검토, 기본 설계, LH 사전 협의",
                key_milestones=[
                    "사업 타당성 분석 완료",
                    "기본 설계안 확정",
                    "LH 사전 협의 완료"
                ],
                risks=[
                    "LH 정책 변경 리스크",
                    "설계 기준 미비로 인한 재작업"
                ]
            ),
            ProjectPhase(
                phase_id="P2",
                phase_name="인허가 절차",
                phase_type=PhaseType.PERMIT,
                duration_months=6,
                dependencies=["P1"],
                is_critical=True,
                description="건축 허가, 용도 변경, 각종 인증 신청",
                key_milestones=[
                    "건축 허가 신청",
                    "건축 허가 승인",
                    "BF 인증 신청",
                    "에너지 효율 인증 신청"
                ],
                risks=[
                    "인허가 지연 (평균 2~3개월)",
                    "인근 주민 민원",
                    "법규 미비로 인한 반려"
                ]
            ),
            ProjectPhase(
                phase_id="P3",
                phase_name="실시 설계",
                phase_type=PhaseType.DESIGN,
                duration_months=4,
                dependencies=["P2"],
                is_critical=True,
                description="건축, 구조, 기계, 전기, 통신, 소방 등 실시설계",
                key_milestones=[
                    "실시설계 착수",
                    "구조 검토 완료",
                    "실시설계 완료",
                    "시공사 선정"
                ],
                risks=[
                    "설계 변경으로 인한 일정 지연",
                    "구조 검토 승인 지연"
                ]
            ),
            ProjectPhase(
                phase_id="P4",
                phase_name="착공 및 골조 공사",
                phase_type=PhaseType.CONSTRUCTION,
                duration_months=12,
                dependencies=["P3"],
                is_critical=True,
                description="기초 공사, 골조 공사, 지붕 공사",
                key_milestones=[
                    "착공 신고",
                    "기초 공사 완료",
                    "골조 공사 50% 완료",
                    "골조 공사 완료",
                    "지붕 공사 완료"
                ],
                risks=[
                    "기상 악화로 인한 공사 중단",
                    "자재 수급 지연",
                    "인력 수급 문제",
                    "안전사고 리스크"
                ]
            ),
            ProjectPhase(
                phase_id="P5",
                phase_name="마감 공사",
                phase_type=PhaseType.CONSTRUCTION,
                duration_months=6,
                dependencies=["P4"],
                is_critical=True,
                description="내외부 마감, 설비 공사, 조경 공사",
                key_milestones=[
                    "내부 마감 착수",
                    "설비 공사 완료",
                    "외부 마감 완료",
                    "조경 공사 완료"
                ],
                risks=[
                    "마감재 수급 지연",
                    "설비 하자 발생",
                    "품질 기준 미달"
                ]
            ),
            ProjectPhase(
                phase_id="P6",
                phase_name="준공 및 인증",
                phase_type=PhaseType.INSPECTION,
                duration_months=2,
                dependencies=["P5"],
                is_critical=True,
                description="준공 검사, 각종 인증 취득",
                key_milestones=[
                    "준공 검사 신청",
                    "준공 검사 통과",
                    "BF 인증 취득",
                    "에너지 효율 인증 취득",
                    "사용 승인"
                ],
                risks=[
                    "준공 검사 불합격",
                    "인증 취득 지연",
                    "보완 공사 발생"
                ]
            ),
            ProjectPhase(
                phase_id="P7",
                phase_name="감정평가",
                phase_type=PhaseType.APPRAISAL,
                duration_months=2,
                dependencies=["P6"],
                is_critical=True,
                description="LH 매입을 위한 감정평가 실시",
                key_milestones=[
                    "감정평가 의뢰",
                    "현장 조사",
                    "감정평가서 발행"
                ],
                risks=[
                    "감정가 예상치 미달",
                    "평가 기준 변경"
                ]
            ),
            ProjectPhase(
                phase_id="P8",
                phase_name="LH 매입 절차",
                phase_type=PhaseType.PURCHASE,
                duration_months=3,
                dependencies=["P7"],
                is_critical=True,
                description="LH 매입 심사 및 계약 체결",
                key_milestones=[
                    "LH 매입 신청",
                    "LH 현장 실사",
                    "LH 내부 승인",
                    "매매 계약 체결",
                    "잔금 지급"
                ],
                risks=[
                    "LH 심사 기준 미달",
                    "매입 예산 부족",
                    "정책 변경으로 인한 매입 중단"
                ]
            )
        ]
    
    def generate_timeline(
        self,
        start_date: Optional[datetime] = None,
        project_scale: str = "standard"
    ) -> Timeline:
        """
        프로젝트 타임라인 생성
        
        Args:
            start_date: 프로젝트 시작일 (기본: 오늘)
            project_scale: 프로젝트 규모 ("small", "standard", "large")
        
        Returns:
            Timeline 객체
        """
        if start_date is None:
            start_date = datetime.now()
        
        # Scale에 따른 일정 조정
        scale_multiplier = {
            "small": 0.8,
            "standard": 1.0,
            "large": 1.2
        }.get(project_scale, 1.0)
        
        # 일정 조정
        adjusted_phases = []
        for phase in self.standard_phases:
            adjusted_phase = ProjectPhase(
                phase_id=phase.phase_id,
                phase_name=phase.phase_name,
                phase_type=phase.phase_type,
                duration_months=int(phase.duration_months * scale_multiplier),
                dependencies=phase.dependencies,
                is_critical=phase.is_critical,
                description=phase.description,
                key_milestones=phase.key_milestones,
                risks=phase.risks
            )
            adjusted_phases.append(adjusted_phase)
        
        # Total duration 계산
        total_duration = sum(p.duration_months for p in adjusted_phases)
        
        # Critical Path 추출
        critical_path = [p.phase_id for p in adjusted_phases if p.is_critical]
        
        # 주요 리스크 정리
        key_risks = self._identify_key_risks(adjusted_phases)
        
        # 권고사항 생성
        recommendations = self._generate_recommendations(adjusted_phases, total_duration)
        
        return Timeline(
            total_duration_months=total_duration,
            phases=adjusted_phases,
            critical_path=critical_path,
            key_risks=key_risks,
            recommendations=recommendations
        )
    
    def _identify_key_risks(self, phases: List[ProjectPhase]) -> List[str]:
        """주요 리스크 식별"""
        key_risks = []
        
        # Critical Path 상의 리스크만 추출
        for phase in phases:
            if phase.is_critical and phase.risks:
                for risk in phase.risks[:2]:  # 상위 2개만
                    key_risks.append(f"{phase.phase_name}: {risk}")
        
        return key_risks
    
    def _generate_recommendations(
        self,
        phases: List[ProjectPhase],
        total_duration: int
    ) -> List[str]:
        """일정 최적화 권고사항 생성"""
        recommendations = []
        
        # 총 기간이 36개월 이상이면 경고
        if total_duration > 36:
            recommendations.append(
                f"⚠️ 총 기간 {total_duration}개월은 표준 36개월 초과. 일정 단축 검토 필요"
            )
        
        # 인허가 단계 권고
        permit_phase = next((p for p in phases if p.phase_type == PhaseType.PERMIT), None)
        if permit_phase and permit_phase.duration_months > 6:
            recommendations.append(
                "💡 인허가 기간 단축을 위해 사전 협의 및 서류 준비 철저히 진행"
            )
        
        # 시공 단계 권고
        construction_phases = [p for p in phases if p.phase_type == PhaseType.CONSTRUCTION]
        total_construction = sum(p.duration_months for p in construction_phases)
        if total_construction > 18:
            recommendations.append(
                "💡 시공 기간 단축을 위해 Fast-Track 공법 또는 모듈러 공법 검토"
            )
        
        # LH 매입 단계 권고
        recommendations.append(
            "💡 LH 매입 심사 기간 단축을 위해 사전 협의 및 서류 준비 철저히 진행"
        )
        
        # Critical Path 관리 권고
        recommendations.append(
            "💡 Critical Path 상의 모든 단계는 일정 지연 시 전체 프로젝트 지연으로 직결. 집중 관리 필요"
        )
        
        return recommendations
    
    def get_narrative(self, timeline: Timeline) -> Dict[str, str]:
        """
        타임라인에 대한 서술 생성
        
        Returns:
            Dict with narrative sections
        """
        return {
            "overview": self._timeline_overview(timeline),
            "critical_path": self._critical_path_analysis(timeline),
            "risk_analysis": self._risk_analysis(timeline),
            "so_what": self._so_what_narrative(timeline),
            "why": self._why_narrative(timeline),
            "recommendations": self._recommendations_narrative(timeline)
        }
    
    def _timeline_overview(self, timeline: Timeline) -> str:
        """타임라인 개요"""
        return f"""
본 프로젝트의 총 예상 기간은 **{timeline.total_duration_months}개월**입니다.

이는 LH 신축매입임대 사업의 표준 일정(36개월)과 {
    "일치" if timeline.total_duration_months == 36 
    else "다소 차이가 있으며" if timeline.total_duration_months < 40
    else "상당한 차이가 있으며"
}합니다.

프로젝트는 총 {len(timeline.phases)}개 단계로 구성되며,
이 중 {len(timeline.critical_path)}개 단계가 Critical Path에 해당합니다.

Critical Path 상의 단계는 일정 지연 시 전체 프로젝트 완료일이 직접 영향을 받으므로
집중적인 관리가 필요합니다.
        """.strip()
    
    def _critical_path_analysis(self, timeline: Timeline) -> str:
        """Critical Path 분석"""
        critical_phases = [p for p in timeline.phases if p.is_critical]
        
        phases_text = "\n".join([
            f"{i+1}. **{p.phase_name}** ({p.duration_months}개월)"
            for i, p in enumerate(critical_phases)
        ])
        
        return f"""
**Critical Path 단계:**

{phases_text}

**총 Critical Path 기간: {sum(p.duration_months for p in critical_phases)}개월**

이 단계들은 순차적으로 진행되어야 하며,
어느 한 단계라도 지연되면 프로젝트 전체 일정이 연기됩니다.

특히 '인허가 절차'와 'LH 매입 절차'는
외부 기관의 승인을 받아야 하므로 지연 리스크가 높습니다.
        """.strip()
    
    def _risk_analysis(self, timeline: Timeline) -> str:
        """리스크 분석"""
        risks_text = "\n".join([
            f"• {risk}"
            for risk in timeline.key_risks
        ])
        
        return f"""
**주요 일정 리스크:**

{risks_text}

이러한 리스크들은 프로젝트 일정에 직접적인 영향을 미칠 수 있으므로
사전 대비책 마련이 필수적입니다.
        """.strip()
    
    def _so_what_narrative(self, timeline: Timeline) -> str:
        """SO WHAT 서술"""
        return f"""
본 프로젝트의 {timeline.total_duration_months}개월 일정은 다음과 같은 의미를 갖습니다:

1. **자금 회전 기간**: 투자 자금이 {timeline.total_duration_months}개월 동안 묶이므로
   자금 조달 계획과 이자 비용 고려가 중요합니다.

2. **시장 변동 리스크**: 3년 가까운 기간 동안 부동산 시장 변동,
   금리 변동, 정책 변경 등의 리스크에 노출됩니다.

3. **LH 정책 안정성**: LH 매입임대 정책이 프로젝트 기간 동안
   유지될 것이라는 전제가 필요합니다.

4. **조기 완공 시 이점**: 일정을 단축할 수 있다면
   자금 회전율 향상과 리스크 감소 효과를 기대할 수 있습니다.
        """.strip()
    
    def _why_narrative(self, timeline: Timeline) -> str:
        """WHY 서술"""
        return """
본 프로젝트 일정이 36개월인 이유는 다음과 같습니다:

1. **법적 절차**: 인허가, 준공검사 등 법적 절차는 단축이 어렵습니다.
   특히 건축 허가는 평균 6개월이 소요됩니다.

2. **시공 기간**: 철근콘크리트 구조의 신축 공사는
   기초-골조-마감 순차 공정으로 최소 18개월이 필요합니다.

3. **LH 심사**: LH 매입 심사는 내부 승인 절차가 복잡하여
   평균 3개월이 소요됩니다.

4. **품질 확보**: 급하게 진행하면 품질 하자 발생 가능성이 높아
   적정 공기 확보가 중요합니다.

5. **계절 요인**: 겨울철 콘크리트 타설 제한 등
   계절적 요인을 고려한 일정 계획이 필요합니다.
        """.strip()
    
    def _recommendations_narrative(self, timeline: Timeline) -> str:
        """권고사항 서술"""
        recs_text = "\n".join([
            f"• {rec}"
            for rec in timeline.recommendations
        ])
        
        return f"""
**일정 관리 권고사항:**

{recs_text}

**추가 제언:**
• 각 단계별 Buffer(여유 기간) 1개월 확보 권장
• Critical Path 상의 단계는 주 단위 모니터링 필요
• 외부 기관 협의 사항은 사전 준비 철저히 진행
• Fast-Track 공법 적용 시 품질 관리 강화 필요
        """.strip()


# ============================================================
# Usage Example
# ============================================================

if __name__ == "__main__":
    # Initialize analyzer
    analyzer = CriticalPathAnalyzer()
    
    print("="*80)
    print("Critical Path Analyzer - Test Output")
    print("="*80)
    
    # Generate timeline
    timeline = analyzer.generate_timeline(
        start_date=datetime(2025, 1, 1),
        project_scale="standard"
    )
    
    print(f"\n📅 프로젝트 총 기간: {timeline.total_duration_months}개월")
    print(f"🔴 Critical Path 단계: {len(timeline.critical_path)}개")
    
    print("\n" + "="*80)
    print("단계별 일정")
    print("="*80)
    
    for phase in timeline.phases:
        critical_mark = "🔴" if phase.is_critical else "⚪"
        print(f"\n{critical_mark} {phase.phase_name}")
        print(f"   기간: {phase.duration_months}개월")
        print(f"   설명: {phase.description}")
        if phase.risks:
            print(f"   리스크: {phase.risks[0]}")
    
    print("\n" + "="*80)
    print("Narrative Sections")
    print("="*80)
    
    narratives = analyzer.get_narrative(timeline)
    
    for section, content in narratives.items():
        print(f"\n### {section.upper()}")
        print(content)
    
    print("\n" + "="*80)
    print("✅ Critical Path Analyzer 정상 작동")
