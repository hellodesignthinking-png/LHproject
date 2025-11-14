"""
정책 알림 시스템
"""

import logging
from typing import List
from datetime import datetime
from .models import PolicyUpdate, PolicyAlert, PolicyChange

logger = logging.getLogger(__name__)


class PolicyNotifier:
    """정책 알림 클래스"""
    
    def __init__(self):
        self.notification_channels = {
            "email": self._send_email,
            "slack": self._send_slack,
            "webhook": self._send_webhook
        }
    
    async def send_alert(
        self,
        policy: PolicyUpdate,
        recipients: List[str],
        channels: List[str] = ["email"]
    ) -> PolicyAlert:
        """알림 전송"""
        
        # 알림 유형 결정
        alert_type = self._determine_alert_type(policy)
        
        # 알림 생성
        alert = PolicyAlert(
            alert_id=f"alert_{datetime.now().timestamp()}",
            policy_update=policy,
            alert_type=alert_type,
            recipients=recipients,
            sent_at=datetime.now()
        )
        
        # 각 채널로 알림 전송
        for channel in channels:
            if channel in self.notification_channels:
                await self.notification_channels[channel](alert)
        
        logger.info(f"알림 전송 완료: {alert.alert_id}")
        return alert
    
    async def send_batch_alert(
        self,
        policies: List[PolicyUpdate],
        recipients: List[str],
        channels: List[str] = ["email"]
    ) -> List[PolicyAlert]:
        """일괄 알림 전송"""
        alerts = []
        
        for policy in policies:
            alert = await self.send_alert(policy, recipients, channels)
            alerts.append(alert)
        
        logger.info(f"일괄 알림 전송 완료: {len(alerts)}건")
        return alerts
    
    def _determine_alert_type(self, policy: PolicyUpdate) -> str:
        """알림 유형 결정"""
        if policy.importance == "high":
            if any(keyword in policy.title for keyword in ["긴급", "중요", "즉시"]):
                return "긴급"
            else:
                return "제도변경"
        else:
            return "신규공고"
    
    async def _send_email(self, alert: PolicyAlert):
        """이메일 전송"""
        logger.info(f"[이메일] 알림 전송: {alert.policy_update.title}")
        
        # 실제 이메일 전송 로직 (예: SMTP, SendGrid, AWS SES 등)
        # 여기서는 로깅만 수행
        
        email_content = f"""
        [정책 알림] {alert.alert_type}
        
        제목: {alert.policy_update.title}
        출처: {alert.policy_update.source.name}
        발행일: {alert.policy_update.published_at.strftime('%Y-%m-%d %H:%M')}
        중요도: {alert.policy_update.importance}
        
        내용:
        {alert.policy_update.content}
        
        상세보기: {alert.policy_update.url}
        
        키워드: {', '.join(alert.policy_update.keywords)}
        """
        
        logger.debug(f"이메일 내용:\n{email_content}")
        
        return True
    
    async def _send_slack(self, alert: PolicyAlert):
        """Slack 메시지 전송"""
        logger.info(f"[Slack] 알림 전송: {alert.policy_update.title}")
        
        # Slack Webhook 전송 로직
        # 실제로는 requests 또는 aiohttp로 Webhook URL에 POST
        
        slack_message = {
            "text": f"🔔 정책 알림: {alert.alert_type}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": alert.policy_update.title
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*출처:*\n{alert.policy_update.source.name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*중요도:*\n{alert.policy_update.importance}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": alert.policy_update.content
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "상세보기"
                            },
                            "url": alert.policy_update.url
                        }
                    ]
                }
            ]
        }
        
        logger.debug(f"Slack 메시지: {slack_message}")
        
        return True
    
    async def _send_webhook(self, alert: PolicyAlert):
        """Webhook 전송"""
        logger.info(f"[Webhook] 알림 전송: {alert.policy_update.title}")
        
        # 사용자 정의 Webhook 전송
        webhook_payload = {
            "event": "policy_update",
            "alert_id": alert.alert_id,
            "alert_type": alert.alert_type,
            "policy": {
                "title": alert.policy_update.title,
                "source": alert.policy_update.source.name,
                "category": alert.policy_update.category.main,
                "importance": alert.policy_update.importance,
                "url": alert.policy_update.url,
                "published_at": alert.policy_update.published_at.isoformat()
            },
            "timestamp": alert.sent_at.isoformat()
        }
        
        logger.debug(f"Webhook payload: {webhook_payload}")
        
        return True


class ChangeNotifier(PolicyNotifier):
    """정책 변화 알림 클래스"""
    
    async def notify_changes(
        self,
        changes: List[PolicyChange],
        recipients: List[str],
        channels: List[str] = ["email", "slack"]
    ):
        """정책 변화 알림"""
        
        high_impact_changes = [c for c in changes if c.impact_level == "high"]
        
        if high_impact_changes:
            logger.warning(f"고영향 정책 변화 {len(high_impact_changes)}건 감지!")
            
            # 긴급 알림
            for change in high_impact_changes:
                await self._send_change_alert(change, recipients, channels, urgent=True)
        
        # 일반 변화 알림 (일괄)
        medium_changes = [c for c in changes if c.impact_level == "medium"]
        if medium_changes:
            await self._send_batch_change_alert(medium_changes, recipients, channels)
    
    async def _send_change_alert(
        self,
        change: PolicyChange,
        recipients: List[str],
        channels: List[str],
        urgent: bool = False
    ):
        """개별 변화 알림"""
        
        prefix = "🚨 긴급" if urgent else "📢"
        
        message = f"""
        {prefix} 정책 변화 알림
        
        변화 유형: {change.change_type}
        영향도: {change.impact_level}
        
        설명:
        {change.description}
        
        감지 시간: {change.detected_at.strftime('%Y-%m-%d %H:%M')}
        """
        
        logger.info(f"정책 변화 알림: {change.description}")
        
        # 실제 전송 (이메일, Slack 등)
        for channel in channels:
            if channel == "email":
                logger.info(f"[이메일] 변화 알림 전송")
            elif channel == "slack":
                logger.info(f"[Slack] 변화 알림 전송")
    
    async def _send_batch_change_alert(
        self,
        changes: List[PolicyChange],
        recipients: List[str],
        channels: List[str]
    ):
        """일괄 변화 알림"""
        
        message = f"""
        📊 정책 변화 요약 ({len(changes)}건)
        
        """
        
        for i, change in enumerate(changes, 1):
            message += f"{i}. [{change.change_type}] {change.description}\n"
        
        logger.info(f"일괄 변화 알림: {len(changes)}건")


# 테스트용
if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        notifier = PolicyNotifier()
        
        # 테스트 정책
        test_policy = PolicyUpdate(
            source={"name": "LH 공사", "url": "https://lh.or.kr"},
            category={"main": "매입임대"},
            title="긴급: 2024년 신축매입임대 제도 개정",
            content="중요 제도 변경사항이 있습니다.",
            url="https://lh.or.kr/notice/12345",
            published_at=datetime.now(),
            importance="high",
            keywords=["신축매입임대", "제도개정"]
        )
        
        # 알림 전송
        alert = await notifier.send_alert(
            test_policy,
            recipients=["admin@example.com"],
            channels=["email", "slack"]
        )
        
        print(f"알림 전송 완료: {alert.alert_id}")
    
    asyncio.run(test())
