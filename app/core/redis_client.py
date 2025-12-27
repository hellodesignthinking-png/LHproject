"""
ZeroSite v4.0 Redis Client
===========================

Async Redis Client for Caching & Session Management

Author: ZeroSite Cache Team
Date: 2025-12-27
Version: 1.0
"""

import redis.asyncio as aioredis
import json
import pickle
from typing import Optional, Any, Union
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class RedisClient:
    """Async Redis Client"""
    
    def __init__(self, url: str = REDIS_URL):
        self.redis = aioredis.from_url(
            url,
            encoding="utf-8",
            decode_responses=False  # For pickle support
        )
    
    async def get(self, key: str, decode: bool = True) -> Optional[Any]:
        """
        Get value by key
        
        Args:
            key: Redis key
            decode: If True, decode as JSON. If False, unpickle
            
        Returns:
            Value or None
        """
        value = await self.redis.get(key)
        
        if value is None:
            return None
        
        if decode:
            return json.loads(value)
        else:
            return pickle.loads(value)
    
    async def set(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = None,
        encode: bool = True
    ):
        """
        Set key-value with optional expiration
        
        Args:
            key: Redis key
            value: Value to store
            ex: Expiration in seconds
            encode: If True, encode as JSON. If False, pickle
        """
        if encode:
            serialized = json.dumps(value)
        else:
            serialized = pickle.dumps(value)
        
        await self.redis.set(key, serialized, ex=ex)
    
    async def delete(self, key: str) -> int:
        """Delete key"""
        return await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.redis.exists(key) > 0
    
    async def incr(self, key: str) -> int:
        """Increment counter"""
        return await self.redis.incr(key)
    
    async def expire(self, key: str, seconds: int):
        """Set expiration"""
        await self.redis.expire(key, seconds)
    
    async def ttl(self, key: str) -> int:
        """Get time to live"""
        return await self.redis.ttl(key)
    
    async def keys(self, pattern: str = "*") -> list:
        """Get keys matching pattern"""
        return await self.redis.keys(pattern)
    
    async def flush_db(self):
        """Flush database (CAUTION!)"""
        await self.redis.flushdb()
    
    async def close(self):
        """Close connection"""
        await self.redis.close()
    
    # ==================== High-level methods ====================
    
    async def cache_analysis_result(self, job_id: str, result: dict, ttl: int = 3600):
        """Cache analysis result (1 hour default)"""
        key = f"analysis:{job_id}"
        await self.set(key, result, ex=ttl, encode=True)
    
    async def get_cached_analysis(self, job_id: str) -> Optional[dict]:
        """Get cached analysis result"""
        key = f"analysis:{job_id}"
        return await self.get(key, decode=True)
    
    async def cache_user_session(self, session_id: str, user_data: dict, ttl: int = 1800):
        """Cache user session (30 min default)"""
        key = f"session:{session_id}"
        await self.set(key, user_data, ex=ttl, encode=True)
    
    async def get_user_session(self, session_id: str) -> Optional[dict]:
        """Get user session"""
        key = f"session:{session_id}"
        return await self.get(key, decode=True)
    
    async def delete_user_session(self, session_id: str):
        """Delete user session"""
        key = f"session:{session_id}"
        await self.delete(key)
    
    async def rate_limit_check(
        self,
        identifier: str,
        limit: int = 1000,
        window: int = 3600
    ) -> tuple[bool, int]:
        """
        Check rate limit
        
        Args:
            identifier: User/API key identifier
            limit: Max requests
            window: Time window in seconds
            
        Returns:
            (allowed, current_count)
        """
        from datetime import datetime
        
        key = f"rate_limit:{identifier}:{datetime.now().hour}"
        count = await self.incr(key)
        
        if count == 1:
            await self.expire(key, window)
        
        return (count <= limit, count)


# Global instance
redis_client = RedisClient()


# Connection test
async def test_redis_connection():
    """Test Redis connection"""
    try:
        await redis_client.redis.ping()
        print("✅ Redis connection successful!")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False
