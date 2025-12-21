"""
Context Snapshot Model
======================

DB Snapshot for Context Resilience
Redis → DB Fallback 시스템의 영구 백업

Purpose:
- Redis 장애 시 복구용 DB 백업
- Context 장기 보존 (Redis TTL 만료 후에도 유지)
- 감사 추적 (Audit Trail)

Storage Strategy:
- PRIMARY: Redis (fast, TTL 24h)
- BACKUP: DB Snapshot (permanent)

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import json

Base = declarative_base()


class ContextSnapshot(Base):
    """
    Context Snapshot 영구 저장소
    
    Redis 장애 시 복구용 + 장기 보존용
    """
    __tablename__ = "context_snapshots"
    
    # Primary Key
    context_id = Column(String(64), primary_key=True, index=True)
    
    # Context Data (JSON)
    context_data = Column(Text, nullable=False)  # Serialized CanonicalLandContext
    context_type = Column(String(50), nullable=False)  # "M1_FINAL", "M2_APPRAISAL", etc.
    
    # Metadata
    parcel_id = Column(String(100), index=True)  # For filtering by parcel
    frozen = Column(Boolean, default=True, nullable=False)  # Immutability flag
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=True)  # NULL = never expires
    accessed_at = Column(DateTime, default=func.now(), onupdate=func.now())
    access_count = Column(Integer, default=0, nullable=False)  # Track usage
    
    # Source Tracking
    created_by = Column(String(50), default="system")  # "api", "migration", etc.
    redis_ttl_seconds = Column(Integer, nullable=True)  # Original Redis TTL
    
    def __repr__(self):
        return (
            f"<ContextSnapshot("
            f"context_id='{self.context_id}', "
            f"type='{self.context_type}', "
            f"parcel='{self.parcel_id}', "
            f"created={self.created_at}, "
            f"access_count={self.access_count}"
            f")>"
        )
    
    @property
    def is_expired(self) -> bool:
        """Check if context has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def age_hours(self) -> float:
        """Age in hours since creation"""
        delta = datetime.utcnow() - self.created_at
        return delta.total_seconds() / 3600
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "context_id": self.context_id,
            "parcel_id": self.parcel_id,
            "context_type": self.context_type,
            "frozen": self.frozen,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "accessed_at": self.accessed_at.isoformat(),
            "access_count": self.access_count,
            "age_hours": self.age_hours,
            "is_expired": self.is_expired,
            "created_by": self.created_by,
            "redis_ttl_seconds": self.redis_ttl_seconds
        }
    
    def get_context_data(self) -> dict:
        """Deserialize context_data JSON"""
        try:
            return json.loads(self.context_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in context_data: {e}")


__all__ = ["ContextSnapshot", "Base"]
