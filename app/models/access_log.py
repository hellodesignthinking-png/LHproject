"""
v1.6.0: Access Log Model
접근 로그 추적 및 다운로드 제한 관리
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import json
from pathlib import Path


class AccessAction(str, Enum):
    """접근 행위 타입"""
    VIEW_HTML = "view_html"
    DOWNLOAD_PDF = "download_pdf"
    CREATE_SHARE = "create_share"
    USE_SHARE_TOKEN = "use_share_token"
    VIEW_DASHBOARD = "view_dashboard"


class AccessLog(BaseModel):
    """접근 로그 엔트리"""
    
    # Primary Keys
    log_id: str = Field(description="로그 고유 ID (UUID)")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # User Information
    user_email: Optional[str] = Field(None, description="사용자 이메일 (인증된 경우)")
    user_role: Optional[str] = Field(None, description="사용자 역할")
    
    # Request Information
    ip_address: str = Field(description="요청자 IP 주소")
    user_agent: Optional[str] = Field(None, description="User-Agent 헤더")
    
    # Resource Information
    run_id: str = Field(description="접근한 RUN_ID")
    report_type: str = Field(description="보고서 타입 (master, landowner, etc.)")
    action: AccessAction = Field(description="접근 행위")
    
    # Share Token (if applicable)
    share_token: Optional[str] = Field(None, description="사용한 공유 토큰")
    
    # Response Information
    success: bool = Field(True, description="요청 성공 여부")
    error_message: Optional[str] = Field(None, description="에러 메시지 (실패 시)")
    
    # Additional Metadata
    request_path: str = Field(description="요청 경로")
    response_time_ms: Optional[int] = Field(None, description="응답 시간 (밀리초)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "log_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2026-01-01T12:00:00Z",
                "user_email": "admin@zerosite.com",
                "user_role": "ADMIN",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "run_id": "TEST_6REPORT",
                "report_type": "master",
                "action": "view_html",
                "success": True,
                "request_path": "/api/v4/reports/six-types/master/html"
            }
        }


class DownloadLimit(BaseModel):
    """다운로드 횟수 제한 추적"""
    
    # Primary Keys
    limit_id: str = Field(description="제한 ID")
    run_id: str = Field(description="RUN_ID")
    report_type: str = Field(description="보고서 타입")
    
    # Limit Information
    user_email: Optional[str] = Field(None, description="사용자 이메일 (인증된 경우)")
    share_token: Optional[str] = Field(None, description="공유 토큰 (비인증 경우)")
    
    # Count Tracking
    download_count: int = Field(default=0, description="다운로드 횟수")
    max_downloads: int = Field(default=10, description="최대 다운로드 허용 횟수")
    
    # Timestamps
    first_download: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_download: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_exceeded(self) -> bool:
        """다운로드 제한 초과 여부"""
        return self.download_count >= self.max_downloads
    
    def increment(self):
        """다운로드 횟수 증가"""
        self.download_count += 1
        self.last_download = datetime.now(timezone.utc)


class IPWhitelist(BaseModel):
    """IP 화이트리스트 엔트리"""
    
    # Primary Keys
    whitelist_id: str = Field(description="화이트리스트 ID")
    ip_address: str = Field(description="허용된 IP 주소 또는 CIDR")
    
    # Metadata
    description: str = Field(description="IP 설명 (조직명 등)")
    created_by: str = Field(description="등록한 관리자")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Status
    is_active: bool = Field(default=True, description="활성화 여부")
    
    def matches(self, ip: str) -> bool:
        """IP 주소가 화이트리스트에 매칭되는지 확인"""
        # Simple exact match for now
        # TODO: Implement CIDR matching in future
        return self.ip_address == ip


class AccessLogStorage:
    """
    접근 로그 저장 및 조회 관리
    Redis 실패 시 파일 기반 저장소 사용
    """
    
    def __init__(self, storage_path: str = "/tmp/zerosite_access_logs"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 로그 파일 경로
        self.logs_file = self.storage_path / "access_logs.jsonl"
        self.limits_file = self.storage_path / "download_limits.json"
        self.whitelist_file = self.storage_path / "ip_whitelist.json"
        
        # In-memory cache for fast lookup
        self._limits_cache: Dict[str, DownloadLimit] = {}
        self._whitelist_cache: List[IPWhitelist] = []
        
        # Load existing data
        self._load_limits()
        self._load_whitelist()
    
    # ========== Access Logs ==========
    
    def log_access(self, log: AccessLog):
        """접근 로그 저장 (Append-only JSONL)"""
        with open(self.logs_file, "a", encoding="utf-8") as f:
            f.write(log.model_dump_json() + "\n")
    
    def get_logs(
        self,
        run_id: Optional[str] = None,
        user_email: Optional[str] = None,
        action: Optional[AccessAction] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AccessLog]:
        """접근 로그 조회 (필터링)"""
        logs = []
        
        if not self.logs_file.exists():
            return logs
        
        with open(self.logs_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    log = AccessLog.model_validate_json(line.strip())
                    
                    # Apply filters
                    if run_id and log.run_id != run_id:
                        continue
                    if user_email and log.user_email != user_email:
                        continue
                    if action and log.action != action:
                        continue
                    if start_time and log.timestamp < start_time:
                        continue
                    if end_time and log.timestamp > end_time:
                        continue
                    
                    logs.append(log)
                    
                    if len(logs) >= limit:
                        break
                except Exception as e:
                    print(f"Error parsing log line: {e}")
                    continue
        
        # Return most recent first
        return list(reversed(logs))
    
    def get_log_statistics(self, run_id: Optional[str] = None) -> Dict[str, Any]:
        """로그 통계 조회"""
        logs = self.get_logs(run_id=run_id, limit=10000)
        
        stats = {
            "total_accesses": len(logs),
            "by_action": {},
            "by_report_type": {},
            "unique_users": set(),
            "unique_ips": set(),
            "failed_requests": 0
        }
        
        for log in logs:
            # By action
            action_key = log.action.value
            stats["by_action"][action_key] = stats["by_action"].get(action_key, 0) + 1
            
            # By report type
            stats["by_report_type"][log.report_type] = stats["by_report_type"].get(log.report_type, 0) + 1
            
            # Unique users/IPs
            if log.user_email:
                stats["unique_users"].add(log.user_email)
            stats["unique_ips"].add(log.ip_address)
            
            # Failed requests
            if not log.success:
                stats["failed_requests"] += 1
        
        # Convert sets to counts
        stats["unique_users"] = len(stats["unique_users"])
        stats["unique_ips"] = len(stats["unique_ips"])
        
        return stats
    
    # ========== Download Limits ==========
    
    def _load_limits(self):
        """다운로드 제한 데이터 로드"""
        if self.limits_file.exists():
            try:
                with open(self.limits_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for key, value in data.items():
                        self._limits_cache[key] = DownloadLimit(**value)
            except Exception as e:
                print(f"Error loading download limits: {e}")
    
    def _save_limits(self):
        """다운로드 제한 데이터 저장"""
        data = {k: v.model_dump(mode="json") for k, v in self._limits_cache.items()}
        with open(self.limits_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_download_limit(
        self,
        run_id: str,
        report_type: str,
        user_email: Optional[str] = None,
        share_token: Optional[str] = None
    ) -> DownloadLimit:
        """다운로드 제한 조회 (없으면 생성)"""
        # Create unique key
        if user_email:
            key = f"{run_id}:{report_type}:{user_email}"
        elif share_token:
            key = f"{run_id}:{report_type}:token:{share_token}"
        else:
            key = f"{run_id}:{report_type}:anonymous"
        
        if key not in self._limits_cache:
            limit = DownloadLimit(
                limit_id=key,
                run_id=run_id,
                report_type=report_type,
                user_email=user_email,
                share_token=share_token,
                max_downloads=10  # Default limit
            )
            self._limits_cache[key] = limit
            self._save_limits()
        
        return self._limits_cache[key]
    
    def increment_download(
        self,
        run_id: str,
        report_type: str,
        user_email: Optional[str] = None,
        share_token: Optional[str] = None
    ) -> DownloadLimit:
        """다운로드 횟수 증가"""
        limit = self.get_download_limit(run_id, report_type, user_email, share_token)
        limit.increment()
        self._save_limits()
        return limit
    
    # ========== IP Whitelist ==========
    
    def _load_whitelist(self):
        """IP 화이트리스트 로드"""
        if self.whitelist_file.exists():
            try:
                with open(self.whitelist_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._whitelist_cache = [IPWhitelist(**item) for item in data]
            except Exception as e:
                print(f"Error loading IP whitelist: {e}")
    
    def _save_whitelist(self):
        """IP 화이트리스트 저장"""
        data = [item.model_dump(mode="json") for item in self._whitelist_cache]
        with open(self.whitelist_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    
    def add_to_whitelist(self, whitelist: IPWhitelist):
        """IP 화이트리스트에 추가"""
        self._whitelist_cache.append(whitelist)
        self._save_whitelist()
    
    def remove_from_whitelist(self, whitelist_id: str):
        """IP 화이트리스트에서 제거"""
        self._whitelist_cache = [
            w for w in self._whitelist_cache if w.whitelist_id != whitelist_id
        ]
        self._save_whitelist()
    
    def is_ip_whitelisted(self, ip: str) -> bool:
        """IP가 화이트리스트에 있는지 확인"""
        for whitelist in self._whitelist_cache:
            if whitelist.is_active and whitelist.matches(ip):
                return True
        return False
    
    def get_whitelist(self) -> List[IPWhitelist]:
        """전체 화이트리스트 조회"""
        return self._whitelist_cache


# Singleton instance
_storage_instance: Optional[AccessLogStorage] = None


def get_access_log_storage() -> AccessLogStorage:
    """접근 로그 저장소 싱글톤 인스턴스"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = AccessLogStorage()
    return _storage_instance
