"""
ZeroSite v4.0 - Multi-tenancy Implementation
조직별 데이터 격리 (Row-Level Security)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.database import Base


class Organization(Base):
    """조직 모델 (Multi-tenancy)"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # 설정
    is_active = Column(Boolean, default=True)
    max_users = Column(Integer, default=10)
    max_analyses_per_month = Column(Integer, default=100)
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    users = relationship("User", back_populates="organization")
    analysis_jobs = relationship("AnalysisJob", back_populates="organization")
    api_keys = relationship("APIKey", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', slug='{self.slug}')>"


# User 모델에 organization_id 추가
"""
class User(Base):
    ...
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    organization = relationship("Organization", back_populates="users")
"""

# AnalysisJob 모델에 organization_id 추가
"""
class AnalysisJob(Base):
    ...
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    organization = relationship("Organization", back_populates="analysis_jobs")
"""

# APIKey 모델에 organization_id 추가
"""
class APIKey(Base):
    ...
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    organization = relationship("Organization", back_populates="api_keys")
"""
