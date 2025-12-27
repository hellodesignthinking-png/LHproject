"""
ZeroSite v4.0 Database Models
==============================

SQLAlchemy ORM Models for PostgreSQL

Author: ZeroSite Database Team
Date: 2025-12-27
Version: 1.0
"""

from sqlalchemy import Column, String, Boolean, Integer, Float, TIMESTAMP, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()


class User(Base):
    """사용자 테이블"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    analysis_jobs = relationship("AnalysisJob", back_populates="user")
    
    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"


class APIKey(Base):
    """API 키 테이블"""
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    key_hash = Column(String(64), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    expires_at = Column(TIMESTAMP)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    last_used = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    # Indexes
    __table_args__ = (
        Index('idx_api_keys_user_id', 'user_id'),
        Index('idx_api_keys_key_hash', 'key_hash'),
    )
    
    def __repr__(self):
        return f"<APIKey(name={self.name}, user_id={self.user_id})>"


class AnalysisJob(Base):
    """분석 작업 테이블"""
    __tablename__ = "analysis_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False, index=True)  # pending, processing, completed, failed
    progress = Column(Integer, default=0)
    
    # Land information (JSONB for flexibility)
    land_info = Column(JSONB, nullable=False)
    
    # Analysis results (JSONB)
    result = Column(JSONB)
    
    # Error tracking
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(TIMESTAMP)
    
    # Relationships
    user = relationship("User", back_populates="analysis_jobs")
    
    # Indexes
    __table_args__ = (
        Index('idx_analysis_jobs_user_id', 'user_id'),
        Index('idx_analysis_jobs_status', 'status'),
        Index('idx_analysis_jobs_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<AnalysisJob(id={self.id}, status={self.status})>"


class ComparisonReport(Base):
    """다중 부지 비교 보고서 테이블"""
    __tablename__ = "comparison_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    report_name = Column(String(255), nullable=False)
    
    # Comparison data (JSONB)
    sites_data = Column(JSONB, nullable=False)
    comparison_result = Column(JSONB)
    
    # Statistics
    total_sites = Column(Integer, default=0)
    average_lh_score = Column(Float)
    average_npv = Column(Float)
    average_irr = Column(Float)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_comparison_reports_user_id', 'user_id'),
        Index('idx_comparison_reports_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ComparisonReport(name={self.report_name}, total_sites={self.total_sites})>"


class AuditLog(Base):
    """감사 로그 테이블"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(50), nullable=False)  # login, logout, create_analysis, etc.
    resource_type = Column(String(50))  # user, analysis_job, api_key, etc.
    resource_id = Column(UUID(as_uuid=True))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    details = Column(JSONB)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_logs_user_id', 'user_id'),
        Index('idx_audit_logs_action', 'action'),
        Index('idx_audit_logs_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<AuditLog(action={self.action}, user_id={self.user_id})>"
