"""
Intelligent Caching Layer for ZeroSite v11.0
=============================================
Caches expensive operations to improve performance
Uses in-memory cache (can be upgraded to Redis for distributed systems)
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Callable
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


class CacheManager:
    """
    In-memory cache manager with TTL support
    """
    
    def __init__(self):
        # Storage: {key: {"value": data, "expires_at": datetime, "hits": int}}
        self.cache: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0
        }
        
        # Default TTLs (in seconds)
        self.default_ttls = {
            "address_resolve": 3600,        # 1 hour (addresses don't change often)
            "zoning_data": 3600,            # 1 hour
            "report_generation": 1800,      # 30 minutes
            "analysis_result": 1800,        # 30 minutes
        }
        
        logger.info("✅ Cache Manager initialized (In-Memory)")
        logger.info("   📊 Default TTLs:")
        for key, ttl in self.default_ttls.items():
            logger.info(f"      - {key}: {ttl}s ({ttl//60}min)")
    
    def _generate_key(self, prefix: str, data: Dict[str, Any]) -> str:
        """
        Generate cache key from data
        Uses MD5 hash for consistent key generation
        """
        # Sort keys for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True)
        hash_value = hashlib.md5(sorted_data.encode()).hexdigest()
        return f"{prefix}:{hash_value}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        Returns None if not found or expired
        """
        if key not in self.cache:
            self.stats["misses"] += 1
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if datetime.now() > entry["expires_at"]:
            del self.cache[key]
            self.stats["misses"] += 1
            self.stats["evictions"] += 1
            return None
        
        # Update hit count
        entry["hits"] += 1
        self.stats["hits"] += 1
        
        logger.debug(f"✅ Cache HIT: {key} (hits: {entry['hits']})")
        return entry["value"]
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """
        Set value in cache with TTL
        """
        if ttl_seconds is None:
            ttl_seconds = 1800  # Default 30 minutes
        
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "hits": 0,
            "created_at": datetime.now()
        }
        
        self.stats["sets"] += 1
        logger.debug(f"💾 Cache SET: {key} (TTL: {ttl_seconds}s)")
    
    def delete(self, key: str):
        """
        Delete specific key from cache
        """
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"🗑️ Cache DELETE: {key}")
    
    def clear(self):
        """
        Clear all cache
        """
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"🧹 Cache cleared: {count} entries removed")
    
    def cleanup_expired(self):
        """
        Remove expired entries
        Should be called periodically
        """
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now > entry["expires_at"]
        ]
        
        for key in expired_keys:
            del self.cache[key]
            self.stats["evictions"] += 1
        
        if expired_keys:
            logger.info(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_entries": len(self.cache),
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "sets": self.stats["sets"],
            "evictions": self.stats["evictions"],
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests
        }
    
    def cache_report(self, address: str, land_area: float, 
                     land_price: float, zone_type: str, 
                     report_data: Any, ttl_seconds: int = 1800):
        """
        Cache a generated report
        """
        key = self._generate_key("report", {
            "address": address,
            "land_area": land_area,
            "land_price": land_price,
            "zone_type": zone_type
        })
        self.set(key, report_data, ttl_seconds)
        return key
    
    def get_cached_report(self, address: str, land_area: float,
                          land_price: float, zone_type: str) -> Optional[Any]:
        """
        Get cached report
        """
        key = self._generate_key("report", {
            "address": address,
            "land_area": land_area,
            "land_price": land_price,
            "zone_type": zone_type
        })
        return self.get(key)
    
    def cache_analysis(self, address: str, land_area: float,
                      land_price: float, zone_type: str,
                      analysis_data: Any, ttl_seconds: int = 1800):
        """
        Cache analysis result
        """
        key = self._generate_key("analysis", {
            "address": address,
            "land_area": land_area,
            "land_price": land_price,
            "zone_type": zone_type
        })
        self.set(key, analysis_data, ttl_seconds)
        return key
    
    def get_cached_analysis(self, address: str, land_area: float,
                           land_price: float, zone_type: str) -> Optional[Any]:
        """
        Get cached analysis
        """
        key = self._generate_key("analysis", {
            "address": address,
            "land_area": land_area,
            "land_price": land_price,
            "zone_type": zone_type
        })
        return self.get(key)


# Global cache instance
cache_manager = CacheManager()


def cached(cache_type: str = "general", ttl_seconds: int = 1800):
    """
    Decorator for caching function results
    
    Usage:
        @cached(cache_type="address", ttl_seconds=3600)
        async def resolve_address(address: str):
            # expensive operation
            return result
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._generate_key(
                cache_type,
                {"args": args, "kwargs": kwargs}
            )
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Cache result
            cache_manager.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator


async def start_cache_cleanup_task():
    """
    Background task to cleanup expired cache entries
    Run this in FastAPI startup
    """
    logger.info("🚀 Starting cache cleanup background task")
    
    while True:
        await asyncio.sleep(300)  # Run every 5 minutes
        cache_manager.cleanup_expired()
        
        # Log stats
        stats = cache_manager.get_stats()
        logger.info(f"📊 Cache Stats: {stats['total_entries']} entries, "
                   f"Hit Rate: {stats['hit_rate_percent']}%")
