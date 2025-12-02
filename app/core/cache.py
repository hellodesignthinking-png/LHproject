"""
Caching Layer for Performance Optimization

Implements in-memory caching for API responses, POI searches, and coordinate lookups.
"""

import json
import hashlib
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from functools import wraps
import time


class CacheService:
    """
    In-memory cache service with TTL support
    
    Features:
    - Key-value storage with expiration
    - Automatic cleanup of expired entries
    - Cache statistics tracking
    - JSON serialization support
    """
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize cache service
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate cache key from arguments
        
        Args:
            prefix: Key prefix (e.g., 'coords', 'poi', 'zone')
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Cache key hash
        """
        # Create deterministic key from arguments
        key_data = f"{prefix}:{json.dumps(args, sort_keys=True)}:{json.dumps(kwargs, sort_keys=True)}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            self._stats["misses"] += 1
            return None
        
        entry = self._cache[key]
        
        # Check expiration
        if datetime.now() > entry["expires_at"]:
            # Expired - delete and return None
            del self._cache[key]
            self._stats["misses"] += 1
            return None
        
        self._stats["hits"] += 1
        return entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL override (seconds)
        """
        ttl = ttl if ttl is not None else self._default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        self._cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": datetime.now()
        }
        
        self._stats["sets"] += 1
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            self._stats["deletes"] += 1
            return True
        return False
    
    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()
        print(f"🗑️  Cache cleared ({len(self._cache)} entries removed)")
    
    def cleanup_expired(self):
        """Remove expired entries"""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now > entry["expires_at"]
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            print(f"🗑️  Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._stats,
            "size": len(self._cache),
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests
        }
    
    def cache_coordinates(self, address: str, coordinates: Dict) -> str:
        """Cache address → coordinates lookup"""
        key = self._generate_key("coords", address=address)
        self.set(key, coordinates, ttl=86400)  # 24 hours
        return key
    
    def get_coordinates(self, address: str) -> Optional[Dict]:
        """Get cached coordinates"""
        key = self._generate_key("coords", address=address)
        return self.get(key)
    
    def cache_poi_search(self, latitude: float, longitude: float, category: str, results: list) -> str:
        """Cache POI search results"""
        key = self._generate_key("poi", lat=latitude, lon=longitude, cat=category)
        self.set(key, results, ttl=3600)  # 1 hour
        return key
    
    def get_poi_search(self, latitude: float, longitude: float, category: str) -> Optional[list]:
        """Get cached POI search"""
        key = self._generate_key("poi", lat=latitude, lon=longitude, cat=category)
        return self.get(key)
    
    def cache_zone_info(self, latitude: float, longitude: float, zone_data: Dict) -> str:
        """Cache zoning information"""
        key = self._generate_key("zone", lat=latitude, lon=longitude)
        self.set(key, zone_data, ttl=86400)  # 24 hours (zoning rarely changes)
        return key
    
    def get_zone_info(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Get cached zoning info"""
        key = self._generate_key("zone", lat=latitude, lon=longitude)
        return self.get(key)


# Global cache instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """
    Get or create global cache service instance
    
    Returns:
        CacheService singleton instance
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


def cached(prefix: str, ttl: Optional[int] = None):
    """
    Decorator to cache function results
    
    Args:
        prefix: Cache key prefix
        ttl: Optional TTL in seconds
        
    Example:
        @cached("poi", ttl=3600)
        def search_poi(lat, lon, category):
            # ... expensive operation
            return results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_service()
            key = cache._generate_key(prefix, *args, **kwargs)
            
            # Check cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Cache miss - call function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator
