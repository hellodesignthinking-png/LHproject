"""
Context Storage Service
=======================

Redis-based storage for frozen CanonicalLandContext
WITH DB SNAPSHOT FALLBACK for resilience

Features:
- PRIMARY: Redis (fast, TTL 24h)
- BACKUP: DB Snapshot (permanent)
- Automatic failover: Redis → DB
- Dual-write for reliability

Storage Strategy:
1. WRITE: Save to both Redis AND DB simultaneously
2. READ: Try Redis first → if fail, try DB (restore to Redis if found)
3. DELETE: Delete from both Redis AND DB

Author: ZeroSite Backend Team
Date: 2025-12-17
Version: 2.0 (WITH RESILIENCE)
"""

import json
import redis
from datetime import timedelta, datetime
from typing import Optional, Dict, Any
import logging
from sqlalchemy.orm import Session

from app.core.context.canonical_land import CanonicalLandContext
from app.config import get_settings
from app.models.context_snapshot import ContextSnapshot
from app.database import SessionLocal  # DB Session

settings = get_settings()
logger = logging.getLogger(__name__)

# Redis client instance
try:
    redis_client = redis.Redis(
        host=settings.redis_host if hasattr(settings, 'redis_host') else 'localhost',
        port=settings.redis_port if hasattr(settings, 'redis_port') else 6379,
        db=0,
        decode_responses=True
    )
    # Test connection
    redis_client.ping()
    logger.info("✅ Redis connected successfully")
except Exception as e:
    logger.warning(f"⚠️ Redis connection failed: {e}. Using fallback in-memory storage.")
    redis_client = None

# Fallback: In-memory storage if Redis unavailable
_memory_storage: Dict[str, Dict[str, Any]] = {}


class ContextStorageService:
    """
    Service for storing and retrieving frozen land contexts
    """

    @staticmethod
    def store_frozen_context(
        context_id: str,
        land_context,  # Union[CanonicalLandContext, Dict, M1FinalContext]
        ttl_hours: int = 24,
        parcel_id: Optional[str] = None
    ) -> bool:
        """
        Store frozen context in BOTH Redis AND DB (dual-write)
        
        Strategy:
        - PRIMARY: Redis (fast, TTL)
        - BACKUP: DB Snapshot (permanent)
        
        Args:
            context_id: Unique context identifier
            land_context: CanonicalLandContext instance, M1FinalContext, or dict
            ttl_hours: Time-to-live in hours (default: 24)
            parcel_id: Optional parcel identifier
            
        Returns:
            bool: True if stored successfully (at least one succeeded)
        """
        redis_success = False
        db_success = False
        
        try:
            # Handle both object and dict input
            if isinstance(land_context, dict):
                context_data = land_context
            elif hasattr(land_context, 'to_dict'):
                context_data = land_context.to_dict()
            else:
                raise ValueError(f"Invalid land_context type: {type(land_context)}")
            context_data['_frozen'] = True
            context_data['_context_id'] = context_id
            
            key = f"context:{context_id}"
            value = json.dumps(context_data, ensure_ascii=False)
            
            # STEP 1: Try Redis (PRIMARY), fallback to memory if fails
            if redis_client:
                try:
                    redis_client.setex(
                        key,
                        timedelta(hours=ttl_hours),
                        value
                    )
                    redis_success = True
                    logger.info(f"✅ [Redis] Context stored: {context_id} (TTL: {ttl_hours}h)")
                except Exception as redis_err:
                    logger.error(f"❌ [Redis] Failed to store: {redis_err}")
                    # Fallback to memory storage when Redis fails
                    _memory_storage[key] = {
                        'data': context_data,
                        'expires_at': None
                    }
                    redis_success = True
                    logger.info(f"✅ [Memory] Context stored (Redis failed): {context_id}")
            else:
                # Fallback to memory storage when Redis is not available
                _memory_storage[key] = {
                    'data': context_data,
                    'expires_at': None
                }
                redis_success = True
                logger.info(f"✅ [Memory] Context stored: {context_id}")
            
            # STEP 2: Save to DB (BACKUP) - ALWAYS, regardless of Redis success
            try:
                db: Session = SessionLocal()
                expires_at = datetime.utcnow() + timedelta(hours=ttl_hours) if ttl_hours else None
                
                snapshot = ContextSnapshot(
                    context_id=context_id,
                    context_data=value,
                    context_type="M1_FINAL",
                    parcel_id=parcel_id or "unknown",
                    frozen=True,
                    created_by="api",
                    redis_ttl_seconds=ttl_hours * 3600,
                    expires_at=expires_at
                )
                
                db.merge(snapshot)  # INSERT or UPDATE
                db.commit()
                db_success = True
                logger.info(f"✅ [DB] Context snapshot saved: {context_id}")
                
            except Exception as db_err:
                logger.error(f"❌ [DB] Failed to save snapshot: {db_err}")
                if 'db' in locals():
                    db.rollback()
            finally:
                if 'db' in locals():
                    db.close()
            
            # Success if at least one storage succeeded
            if redis_success or db_success:
                status = []
                if redis_success:
                    status.append("Redis")
                if db_success:
                    status.append("DB")
                logger.info(f"✅ Context stored successfully in: {', '.join(status)}")
                return True
            else:
                logger.error(f"❌ Failed to store context in ANY storage: {context_id}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Critical failure storing context {context_id}: {e}")
            return False

    @staticmethod
    def get_frozen_context(context_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve frozen context with RESILIENT FALLBACK
        
        Strategy:
        1. Try Redis (FAST)
        2. If not found → Try DB Snapshot (RELIABLE)
        3. If found in DB → Restore to Redis for future requests
        
        Args:
            context_id: Unique context identifier
            
        Returns:
            Optional[Dict]: Context data if found, None otherwise
        """
        try:
            key = f"context:{context_id}"
            
            # STEP 1: Try Redis (PRIMARY, FAST)
            if redis_client:
                try:
                    data = redis_client.get(key)
                    if data:
                        context_data = json.loads(data)
                        logger.info(f"✅ [Redis] Context retrieved: {context_id}")
                        return context_data
                except Exception as redis_err:
                    logger.warning(f"⚠️ [Redis] Retrieval failed: {redis_err}")
            else:
                # Try memory storage
                if key in _memory_storage:
                    context_data = _memory_storage[key]['data']
                    logger.info(f"✅ [Memory] Context retrieved: {context_id}")
                    return context_data
            
            # 🔥 CRITICAL FIX: Always try in-memory before DB fallback
            # This ensures data stored in memory (when Redis fails) can be retrieved
            if key in _memory_storage:
                context_data = _memory_storage[key]['data']
                logger.info(f"✅ [Memory] Context retrieved (pre-DB check): {context_id}")
                return context_data
            
            # STEP 2: Redis miss → Try DB Snapshot (FALLBACK)
            logger.info(f"⚠️ [Redis] Context not found, trying DB fallback: {context_id}")
            
            try:
                db: Session = SessionLocal()
                snapshot = db.query(ContextSnapshot).filter(
                    ContextSnapshot.context_id == context_id
                ).first()
                
                if snapshot:
                    # Found in DB!
                    context_data = json.loads(snapshot.context_data)
                    logger.info(f"✅ [DB] Context recovered from snapshot: {context_id}")
                    
                    # Update access tracking
                    snapshot.accessed_at = datetime.utcnow()
                    snapshot.access_count += 1
                    db.commit()
                    
                    # STEP 3: Restore to Redis for future requests
                    if redis_client and not snapshot.is_expired:
                        try:
                            redis_client.setex(
                                key,
                                timedelta(hours=24),  # Default TTL
                                snapshot.context_data
                            )
                            logger.info(f"✅ [Redis] Context restored from DB: {context_id}")
                        except Exception as restore_err:
                            logger.warning(f"⚠️ [Redis] Failed to restore: {restore_err}")
                    
                    return context_data
                else:
                    logger.warning(f"⚠️ [DB] Context not found: {context_id}")
                    # 🔥 FINAL FALLBACK: Try memory one last time before giving up
                    if key in _memory_storage:
                        context_data = _memory_storage[key]['data']
                        logger.info(f"✅ [Memory] Context retrieved (final fallback): {context_id}")
                        return context_data
                    return None
                    
            except Exception as db_err:
                logger.error(f"❌ [DB] Fallback retrieval failed: {db_err}")
                # 🔥 CRITICAL: Try memory storage as final resort
                if key in _memory_storage:
                    context_data = _memory_storage[key]['data']
                    logger.info(f"✅ [Memory] Context retrieved (after DB error): {context_id}")
                    return context_data
                return None
            finally:
                if 'db' in locals():
                    db.close()
            
        except Exception as e:
            logger.error(f"❌ Critical failure retrieving context {context_id}: {e}")
            return None

    @staticmethod
    def delete_context(context_id: str) -> bool:
        """
        Delete context from BOTH Redis AND DB
        
        Args:
            context_id: Unique context identifier
            
        Returns:
            bool: True if deleted from at least one storage
        """
        redis_deleted = False
        db_deleted = False
        
        try:
            key = f"context:{context_id}"
            
            # Delete from Redis
            if redis_client:
                try:
                    result = redis_client.delete(key)
                    redis_deleted = result > 0
                    if redis_deleted:
                        logger.info(f"✅ [Redis] Context deleted: {context_id}")
                except Exception as redis_err:
                    logger.error(f"❌ [Redis] Delete failed: {redis_err}")
            else:
                if key in _memory_storage:
                    del _memory_storage[key]
                    redis_deleted = True
                    logger.info(f"✅ [Memory] Context deleted: {context_id}")
            
            # Delete from DB
            try:
                db: Session = SessionLocal()
                result = db.query(ContextSnapshot).filter(
                    ContextSnapshot.context_id == context_id
                ).delete()
                db.commit()
                db_deleted = result > 0
                if db_deleted:
                    logger.info(f"✅ [DB] Snapshot deleted: {context_id}")
            except Exception as db_err:
                logger.error(f"❌ [DB] Delete failed: {db_err}")
                if 'db' in locals():
                    db.rollback()
            finally:
                if 'db' in locals():
                    db.close()
            
            return redis_deleted or db_deleted
            
        except Exception as e:
            logger.error(f"❌ Failed to delete context {context_id}: {e}")
            return False

    @staticmethod
    def context_exists(context_id: str) -> bool:
        """
        Check if context exists in storage
        
        Args:
            context_id: Unique context identifier
            
        Returns:
            bool: True if context exists
        """
        try:
            key = f"context:{context_id}"
            
            if redis_client:
                return redis_client.exists(key) > 0
            else:
                return key in _memory_storage
                
        except Exception as e:
            logger.error(f"❌ Failed to check context existence {context_id}: {e}")
            return False

    @staticmethod
    def get_context_ttl(context_id: str) -> Optional[int]:
        """
        Get remaining TTL for context in seconds
        
        Args:
            context_id: Unique context identifier
            
        Returns:
            Optional[int]: TTL in seconds, None if not found or no expiration
        """
        try:
            if not redis_client:
                return None
            
            key = f"context:{context_id}"
            ttl = redis_client.ttl(key)
            
            if ttl < 0:
                return None
            
            return ttl
            
        except Exception as e:
            logger.error(f"❌ Failed to get TTL for context {context_id}: {e}")
            return None

    @staticmethod
    def extend_ttl(context_id: str, additional_hours: int = 24) -> bool:
        """
        Extend TTL for existing context
        
        Args:
            context_id: Unique context identifier
            additional_hours: Additional hours to add
            
        Returns:
            bool: True if TTL extended successfully
        """
        try:
            if not redis_client:
                return False
            
            key = f"context:{context_id}"
            result = redis_client.expire(key, timedelta(hours=additional_hours))
            
            if result:
                logger.info(f"✅ TTL extended for context: {context_id} (+{additional_hours}h)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to extend TTL for context {context_id}: {e}")
            return False

    @staticmethod
    def get_all_context_ids() -> list:
        """
        Get all stored context IDs
        
        Returns:
            list: List of context IDs
        """
        try:
            if redis_client:
                keys = redis_client.keys("context:*")
                return [key.replace("context:", "") for key in keys]
            else:
                return [key.replace("context:", "") for key in _memory_storage.keys()]
                
        except Exception as e:
            logger.error(f"❌ Failed to get context IDs: {e}")
            return []

    @staticmethod
    def health_check() -> Dict[str, Any]:
        """
        Check storage health status
        
        Returns:
            Dict: Health status information
        """
        try:
            if redis_client:
                redis_client.ping()
                info = redis_client.info()
                return {
                    "status": "healthy",
                    "backend": "redis",
                    "connected": True,
                    "used_memory": info.get("used_memory_human", "unknown"),
                    "total_keys": redis_client.dbsize()
                }
            else:
                return {
                    "status": "healthy",
                    "backend": "memory",
                    "connected": True,
                    "total_keys": len(_memory_storage)
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "backend": "unknown",
                "connected": False,
                "error": str(e)
            }


# Create singleton instance
context_storage = ContextStorageService()
