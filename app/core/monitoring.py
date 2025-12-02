"""
모니터링 및 알림 시스템
- Slack 알림
- 시스템 헬스 체크
- 에러 추적
"""

import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import psutil
import json

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Slack 알림 전송"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url
        self.enabled = bool(webhook_url)
    
    async def send_notification(
        self,
        title: str,
        message: str,
        level: str = "info",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """알림 전송"""
        if not self.enabled:
            logger.info(f"Slack notification (disabled): {title} - {message}")
            return
        
        color_map = {
            "info": "#36a64f",
            "warning": "#ff9900",
            "error": "#ff0000",
            "critical": "#8b0000"
        }
        
        fields = []
        if metadata:
            for key, value in metadata.items():
                fields.append({
                    "title": key,
                    "value": str(value),
                    "short": True
                })
        
        payload = {
            "attachments": [{
                "color": color_map.get(level, "#808080"),
                "title": title,
                "text": message,
                "fields": fields,
                "footer": "ZeroSite v7.1",
                "ts": int(datetime.now().timestamp())
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status != 200:
                        logger.error(f"Slack notification failed: {response.status}")
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
    
    async def notify_error(self, error: Exception, context: Dict[str, Any]):
        """에러 알림"""
        await self.send_notification(
            title="🚨 시스템 에러 발생",
            message=f"Error: {str(error)}",
            level="error",
            metadata={
                "Error Type": type(error).__name__,
                "Context": json.dumps(context, ensure_ascii=False)[:100]
            }
        )
    
    async def notify_performance_issue(self, metrics: Dict[str, Any]):
        """성능 이슈 알림"""
        await self.send_notification(
            title="⚠️ 성능 이슈 감지",
            message="응답 시간이 임계값을 초과했습니다",
            level="warning",
            metadata=metrics
        )
    
    async def notify_health_check_failure(self, service: str, reason: str):
        """헬스 체크 실패 알림"""
        await self.send_notification(
            title="❌ 헬스 체크 실패",
            message=f"Service: {service}\nReason: {reason}",
            level="critical",
            metadata={"Service": service, "Status": "DOWN"}
        )


class HealthChecker:
    """시스템 헬스 체크"""
    
    def __init__(self):
        self.checks: Dict[str, callable] = {}
    
    def register_check(self, name: str, check_func: callable):
        """헬스 체크 등록"""
        self.checks[name] = check_func
    
    async def check_all(self) -> Dict[str, Any]:
        """전체 헬스 체크 실행"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {}
        }
        
        for name, check_func in self.checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                
                results["checks"][name] = {
                    "status": "pass" if result else "fail",
                    "details": result if isinstance(result, dict) else {}
                }
                
                if not result:
                    results["status"] = "unhealthy"
            
            except Exception as e:
                results["checks"][name] = {
                    "status": "error",
                    "error": str(e)
                }
                results["status"] = "unhealthy"
        
        return results
    
    def check_system_resources(self) -> Dict[str, Any]:
        """시스템 리소스 체크"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "healthy": cpu_percent < 90 and memory.percent < 90 and disk.percent < 90
        }


class ErrorTracker:
    """에러 추적 및 집계"""
    
    def __init__(self, max_errors: int = 1000):
        self.errors: List[Dict[str, Any]] = []
        self.max_errors = max_errors
        self.error_counts: Dict[str, int] = {}
    
    def track_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ):
        """에러 추적"""
        error_type = type(error).__name__
        
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "message": str(error),
            "context": context or {}
        }
        
        self.errors.append(error_record)
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # 최대 개수 유지
        if len(self.errors) > self.max_errors:
            removed = self.errors.pop(0)
            removed_type = removed["error_type"]
            self.error_counts[removed_type] = max(0, self.error_counts[removed_type] - 1)
        
        logger.error(f"Error tracked: {error_type} - {str(error)}", extra={"context": context})
    
    def get_error_summary(self) -> Dict[str, Any]:
        """에러 요약 정보"""
        return {
            "total_errors": len(self.errors),
            "error_counts": self.error_counts,
            "recent_errors": self.errors[-10:] if self.errors else []
        }
    
    def clear(self):
        """에러 기록 초기화"""
        self.errors.clear()
        self.error_counts.clear()


# 전역 인스턴스
slack_notifier = SlackNotifier()
health_checker = HealthChecker()
error_tracker = ErrorTracker()


# 기본 헬스 체크 등록
health_checker.register_check("system_resources", health_checker.check_system_resources)


async def notify_if_needed(metrics: Dict[str, Any]):
    """메트릭 기반 알림 전송"""
    # 응답 시간 체크
    if metrics.get("avg_response_time", 0) > 1.0:
        await slack_notifier.notify_performance_issue({
            "Avg Response Time": f"{metrics['avg_response_time']:.3f}s",
            "P95 Response Time": f"{metrics.get('p95_response_time', 0):.3f}s"
        })
    
    # 에러율 체크
    if metrics.get("error_rate", 0) > 0.05:  # 5% 이상
        await slack_notifier.notify_error(
            Exception("High error rate detected"),
            {"error_rate": f"{metrics['error_rate']*100:.2f}%"}
        )
