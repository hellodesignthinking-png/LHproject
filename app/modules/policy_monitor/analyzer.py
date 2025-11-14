"""
정책 변화 분석기
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .models import PolicyUpdate, PolicyChange, PolicyReport

logger = logging.getLogger(__name__)


class PolicyAnalyzer:
    """정책 변화 분석 클래스"""
    
    # 중요 키워드 가중치
    IMPORTANCE_KEYWORDS = {
        "신축매입임대": 10,
        "건축비": 8,
        "매입단가": 8,
        "감정평가": 7,
        "사전약정": 7,
        "준공검사": 6,
        "제도개선": 9,
        "법령개정": 9,
        "긴급": 10,
        "변경": 8,
        "폐지": 7
    }
    
    def __init__(self):
        self.previous_policies: Dict[str, PolicyUpdate] = {}
        
    def analyze_importance(self, policy: PolicyUpdate) -> str:
        """정책 중요도 분석"""
        score = 0
        text = policy.title + " " + policy.content
        
        # 키워드 기반 점수 계산
        for keyword, weight in self.IMPORTANCE_KEYWORDS.items():
            if keyword in text:
                score += weight
        
        # 출처별 가중치
        if "LH" in policy.source.name:
            score += 5
        if "국토교통부" in policy.source.name:
            score += 8
        
        # 점수에 따른 중요도 분류
        if score >= 15:
            return "high"
        elif score >= 8:
            return "medium"
        else:
            return "low"
    
    def detect_changes(self, new_policies: List[PolicyUpdate]) -> List[PolicyChange]:
        """정책 변화 감지"""
        changes = []
        
        for policy in new_policies:
            # 제목 기반 유사 정책 검색
            similar_policy = self._find_similar_policy(policy)
            
            if similar_policy:
                # 변경사항 분석
                change = self._analyze_change(similar_policy, policy)
                if change:
                    changes.append(change)
            else:
                # 신규 정책
                change = PolicyChange(
                    policy_id=policy.id or f"new_{datetime.now().timestamp()}",
                    change_type="신규",
                    old_value=None,
                    new_value=policy.title,
                    impact_level=self.analyze_importance(policy),
                    description=f"신규 정책 발표: {policy.title}",
                    detected_at=datetime.now()
                )
                changes.append(change)
        
        logger.info(f"정책 변화 {len(changes)}건 감지")
        return changes
    
    def _find_similar_policy(self, policy: PolicyUpdate) -> Optional[PolicyUpdate]:
        """유사 정책 찾기 (제목 유사도 기반)"""
        # 간단한 키워드 매칭 (실제로는 더 정교한 알고리즘 필요)
        for prev_policy in self.previous_policies.values():
            if self._calculate_similarity(prev_policy.title, policy.title) > 0.7:
                return prev_policy
        return None
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산 (간단한 버전)"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _analyze_change(self, old_policy: PolicyUpdate, new_policy: PolicyUpdate) -> Optional[PolicyChange]:
        """변경사항 상세 분석"""
        # 내용 비교
        if old_policy.content != new_policy.content:
            return PolicyChange(
                policy_id=new_policy.id or f"change_{datetime.now().timestamp()}",
                change_type="개정",
                old_value=old_policy.content[:100],  # 처음 100자만
                new_value=new_policy.content[:100],
                impact_level=self.analyze_importance(new_policy),
                description=f"정책 내용 변경: {new_policy.title}",
                detected_at=datetime.now()
            )
        return None
    
    def generate_report(
        self, 
        policies: List[PolicyUpdate],
        changes: List[PolicyChange],
        period_days: int = 7
    ) -> PolicyReport:
        """정책 리포트 생성"""
        
        period_start = datetime.now() - timedelta(days=period_days)
        period_end = datetime.now()
        
        # 중요 변화 필터링
        important_changes = [
            change for change in changes 
            if change.impact_level in ["high", "medium"]
        ]
        
        # 요약 생성
        summary = self._generate_summary(policies, important_changes)
        
        # 권장사항 생성
        recommendations = self._generate_recommendations(important_changes)
        
        report = PolicyReport(
            report_id=f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            period_start=period_start,
            period_end=period_end,
            total_updates=len(policies),
            important_changes=important_changes,
            summary=summary,
            recommendations=recommendations,
            created_at=datetime.now()
        )
        
        logger.info(f"정책 리포트 생성 완료: {report.report_id}")
        return report
    
    def _generate_summary(self, policies: List[PolicyUpdate], changes: List[PolicyChange]) -> str:
        """요약 생성"""
        high_priority = len([p for p in policies if p.importance == "high"])
        new_policies = len([c for c in changes if c.change_type == "신규"])
        revised_policies = len([c for c in changes if c.change_type == "개정"])
        
        summary = f"""
최근 {len(policies)}건의 정책 업데이트가 있었습니다.

• 고중요도 정책: {high_priority}건
• 신규 정책: {new_policies}건
• 개정 정책: {revised_policies}건

주요 변화:
"""
        for i, change in enumerate(changes[:3], 1):
            summary += f"{i}. {change.description}\n"
        
        return summary.strip()
    
    def _generate_recommendations(self, changes: List[PolicyChange]) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        # 고위험 변화가 있는 경우
        high_impact_changes = [c for c in changes if c.impact_level == "high"]
        if high_impact_changes:
            recommendations.append(
                f"긴급: {len(high_impact_changes)}건의 고영향 정책 변화가 감지되었습니다. "
                "즉시 내부 프로세스 검토가 필요합니다."
            )
        
        # 신규 정책
        new_changes = [c for c in changes if c.change_type == "신규"]
        if new_changes:
            recommendations.append(
                f"{len(new_changes)}건의 신규 정책이 발표되었습니다. "
                "컨설팅 프로세스 및 서류양식 업데이트를 검토하세요."
            )
        
        # 개정 정책
        revised_changes = [c for c in changes if c.change_type == "개정"]
        if revised_changes:
            recommendations.append(
                f"{len(revised_changes)}건의 정책이 개정되었습니다. "
                "입지평가모델 및 심사기준 조정이 필요할 수 있습니다."
            )
        
        # 기본 권장사항
        if not recommendations:
            recommendations.append("현재 주요 정책 변화는 없습니다. 정기 모니터링을 계속하세요.")
        
        return recommendations
    
    def update_policy_cache(self, policies: List[PolicyUpdate]):
        """정책 캐시 업데이트"""
        for policy in policies:
            key = policy.id or policy.title
            self.previous_policies[key] = policy
        
        logger.info(f"정책 캐시 업데이트: {len(policies)}건")


# 테스트용
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 테스트 데이터
    test_policies = [
        PolicyUpdate(
            source={"name": "LH 공사", "url": "https://lh.or.kr"},
            category={"main": "매입임대"},
            title="2024년 신축매입임대 건축비 기준 변경",
            content="2024년부터 신축매입임대 건축비 기준이 상향 조정됩니다.",
            url="https://lh.or.kr/notice/12345",
            published_at=datetime.now(),
            importance="high",
            keywords=["신축매입임대", "건축비"]
        )
    ]
    
    analyzer = PolicyAnalyzer()
    
    # 중요도 분석
    for policy in test_policies:
        importance = analyzer.analyze_importance(policy)
        print(f"정책: {policy.title}")
        print(f"중요도: {importance}\n")
    
    # 변화 감지
    changes = analyzer.detect_changes(test_policies)
    for change in changes:
        print(f"변화: {change.description}")
        print(f"영향도: {change.impact_level}\n")
    
    # 리포트 생성
    report = analyzer.generate_report(test_policies, changes)
    print(f"\n리포트 요약:\n{report.summary}")
    print(f"\n권장사항:")
    for rec in report.recommendations:
        print(f"• {rec}")
