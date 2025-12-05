"""
Cache Persistence with Optional Redis Backend
- Auto-switch between MemoryCache <-> RedisCache
- Per-service TTL: POI=24h, zoning=72h, coordinates=24h
- Graceful fallback to memory cache if Redis unavailable
"""

import json
import pickle
import hashlib
from typing import Any, Optional, Dict
from datetime import timedelta
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """Cache Backend 인터페이스"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """값 조회"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """값 저장"""
        pass
    
    @abstractmethod
    def delete(self, key: str):
        """값 삭제"""
        pass
    
    @abstractmethod
    def clear(self):
        """전체 캐시 삭제"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """키 존재 여부"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """통계 조회"""
        pass


class MemoryCacheBackend(CacheBackend):
    """메모리 기반 캐시 (v7.1 cache.py 호환)"""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """값 조회"""
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """값 저장 (TTL은 메모리 캐시에서는 무시)"""
        self.cache[key] = value
    
    def delete(self, key: str):
        """값 삭제"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """전체 캐시 삭제"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def exists(self, key: str) -> bool:
        """키 존재 여부"""
        return key in self.cache
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 조회"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "backend": "memory",
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "total_keys": len(self.cache)
        }


class RedisCacheBackend(CacheBackend):
    """Redis 기반 캐시"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """값 조회"""
        try:
            value = self.redis.get(key)
            if value is not None:
                self.hits += 1
                # Pickle로 역직렬화
                return pickle.loads(value)
            self.misses += 1
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            self.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """값 저장"""
        try:
            # Pickle로 직렬화
            serialized = pickle.dumps(value)
            if ttl:
                self.redis.setex(key, ttl, serialized)
            else:
                self.redis.set(key, serialized)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    def delete(self, key: str):
        """값 삭제"""
        try:
            self.redis.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
    
    def clear(self):
        """전체 캐시 삭제"""
        try:
            self.redis.flushdb()
            self.hits = 0
            self.misses = 0
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
    
    def exists(self, key: str) -> bool:
        """키 존재 여부"""
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 조회"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        try:
            info = self.redis.info()
            return {
                "backend": "redis",
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": f"{hit_rate:.2f}%",
                "total_keys": self.redis.dbsize(),
                "redis_version": info.get("redis_version", "unknown"),
                "used_memory_human": info.get("used_memory_human", "unknown")
            }
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return {
                "backend": "redis",
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": f"{hit_rate:.2f}%",
                "error": str(e)
            }


class CacheTTL:
    """서비스별 TTL 설정 (초)"""
    POI = 24 * 60 * 60  # 24시간
    ZONING = 72 * 60 * 60  # 72시간 (3일)
    COORDINATES = 24 * 60 * 60  # 24시간
    DEFAULT = 60 * 60  # 1시간


class PersistentCache:
    """자동 전환 캐시 시스템"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.backend = self._initialize_backend(redis_url)
        self.prefix = "zerosite_v7:"
    
    def _initialize_backend(self, redis_url: Optional[str]) -> CacheBackend:
        """Backend 초기화 (Redis → Memory fallback)"""
        if redis_url:
            try:
                import redis
                redis_client = redis.from_url(redis_url, decode_responses=False)
                # 연결 테스트
                redis_client.ping()
                logger.info("✅ Redis cache backend initialized")
                return RedisCacheBackend(redis_client)
            except ImportError:
                logger.warning("⚠️ redis-py not installed, falling back to memory cache")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed: {e}, falling back to memory cache")
        
        logger.info("✅ Memory cache backend initialized")
        return MemoryCacheBackend()
    
    def _make_key(self, service: str, identifier: str) -> str:
        """캐시 키 생성"""
        # identifier를 해시로 변환 (긴 키 방지)
        id_hash = hashlib.md5(identifier.encode()).hexdigest()
        return f"{self.prefix}{service}:{id_hash}"
    
    def get_poi(self, location_key: str) -> Optional[Any]:
        """POI 캐시 조회"""
        key = self._make_key("poi", location_key)
        return self.backend.get(key)
    
    def set_poi(self, location_key: str, value: Any):
        """POI 캐시 저장 (24시간)"""
        key = self._make_key("poi", location_key)
        self.backend.set(key, value, ttl=CacheTTL.POI)
    
    def get_zoning(self, address: str) -> Optional[Any]:
        """용도지역 캐시 조회"""
        key = self._make_key("zoning", address)
        return self.backend.get(key)
    
    def set_zoning(self, address: str, value: Any):
        """용도지역 캐시 저장 (72시간)"""
        key = self._make_key("zoning", address)
        self.backend.set(key, value, ttl=CacheTTL.ZONING)
    
    def get_coordinates(self, address: str) -> Optional[Any]:
        """좌표 캐시 조회"""
        key = self._make_key("coordinates", address)
        return self.backend.get(key)
    
    def set_coordinates(self, address: str, value: Any):
        """좌표 캐시 저장 (24시간)"""
        key = self._make_key("coordinates", address)
        self.backend.set(key, value, ttl=CacheTTL.COORDINATES)
    
    def get_generic(self, service: str, identifier: str) -> Optional[Any]:
        """범용 캐시 조회"""
        key = self._make_key(service, identifier)
        return self.backend.get(key)
    
    def set_generic(self, service: str, identifier: str, value: Any, ttl: Optional[int] = None):
        """범용 캐시 저장"""
        key = self._make_key(service, identifier)
        if ttl is None:
            ttl = CacheTTL.DEFAULT
        self.backend.set(key, value, ttl=ttl)
    
    def delete(self, service: str, identifier: str):
        """캐시 삭제"""
        key = self._make_key(service, identifier)
        self.backend.delete(key)
    
    def clear_all(self):
        """전체 캐시 삭제"""
        self.backend.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계"""
        return self.backend.get_stats()
    
    def is_redis(self) -> bool:
        """Redis backend 사용 여부"""
        return isinstance(self.backend, RedisCacheBackend)
    
    def switch_to_memory(self):
        """Memory backend로 전환 (Redis 장애 시)"""
        if self.is_redis():
            logger.warning("Switching to memory cache backend")
            self.backend = MemoryCacheBackend()


# 전역 캐시 인스턴스 생성 함수
def create_cache(redis_url: Optional[str] = None) -> PersistentCache:
    """캐시 인스턴스 생성"""
    return PersistentCache(redis_url=redis_url)


# 전역 인스턴스 (환경 변수에서 REDIS_URL 읽기)
import os
_redis_url = os.getenv("REDIS_URL")
persistent_cache = create_cache(_redis_url)


# v7.1 cache.py 호환 함수들
def get_from_cache(cache_key: str) -> Optional[Any]:
    """캐시 조회 (v7.1 호환)"""
    return persistent_cache.get_generic("legacy", cache_key)


def save_to_cache(cache_key: str, value: Any, ttl: int = CacheTTL.DEFAULT):
    """캐시 저장 (v7.1 호환)"""
    persistent_cache.set_generic("legacy", cache_key, value, ttl=ttl)


def clear_cache():
    """전체 캐시 삭제 (v7.1 호환)"""
    persistent_cache.clear_all()


def get_cache_stats() -> Dict[str, Any]:
    """캐시 통계 (v7.1 호환)"""
    return persistent_cache.get_stats()
