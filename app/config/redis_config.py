"""
Redis Configuration for ZeroSite v11.0
========================================

Environment-based Redis configuration with fallback to in-memory storage.

Environment Variables:
    REDIS_HOST - Redis server host (default: localhost)
    REDIS_PORT - Redis server port (default: 6379)
    REDIS_DB - Redis database number (default: 0)
    REDIS_PASSWORD - Redis password (optional)
    REDIS_SSL - Enable SSL/TLS (default: false)
    REDIS_ENABLED - Enable Redis (default: true)
    
Example .env file:
    REDIS_HOST=localhost
    REDIS_PORT=6379
    REDIS_DB=0
    REDIS_PASSWORD=your_password_here
    REDIS_SSL=false
    REDIS_ENABLED=true
"""

import os
from typing import Optional
import redis
import logging

logger = logging.getLogger(__name__)


class RedisConfig:
    """Redis configuration manager"""
    
    def __init__(self):
        """Load configuration from environment"""
        self.enabled = os.getenv('REDIS_ENABLED', 'true').lower() == 'true'
        self.host = os.getenv('REDIS_HOST', 'localhost')
        self.port = int(os.getenv('REDIS_PORT', '6379'))
        self.db = int(os.getenv('REDIS_DB', '0'))
        self.password = os.getenv('REDIS_PASSWORD', None)
        self.ssl = os.getenv('REDIS_SSL', 'false').lower() == 'true'
        self.socket_timeout = 5  # seconds
        self.socket_connect_timeout = 5  # seconds
        self.retry_on_timeout = True
        self.max_connections = 10
    
    def get_connection_kwargs(self) -> dict:
        """Get Redis connection parameters"""
        kwargs = {
            'host': self.host,
            'port': self.port,
            'db': self.db,
            'socket_timeout': self.socket_timeout,
            'socket_connect_timeout': self.socket_connect_timeout,
            'retry_on_timeout': self.retry_on_timeout,
            'decode_responses': True,  # Return strings instead of bytes
        }
        
        if self.password:
            kwargs['password'] = self.password
        
        if self.ssl:
            kwargs['ssl'] = True
            kwargs['ssl_cert_reqs'] = 'required'
        
        return kwargs
    
    def create_client(self) -> Optional[redis.Redis]:
        """
        Create Redis client
        
        Returns:
            Redis client or None if disabled/unavailable
        """
        if not self.enabled:
            logger.info("📍 Redis is DISABLED via REDIS_ENABLED=false")
            return None
        
        try:
            client = redis.Redis(**self.get_connection_kwargs())
            
            # Test connection
            client.ping()
            
            logger.info(f"✅ Redis connected: {self.host}:{self.port} (DB {self.db})")
            return client
            
        except redis.ConnectionError as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            logger.info("📍 Falling back to in-memory storage")
            return None
            
        except Exception as e:
            logger.error(f"❌ Redis initialization error: {e}")
            logger.info("📍 Falling back to in-memory storage")
            return None
    
    def __repr__(self):
        """String representation"""
        return (
            f"RedisConfig("
            f"enabled={self.enabled}, "
            f"host={self.host}, "
            f"port={self.port}, "
            f"db={self.db}, "
            f"ssl={self.ssl})"
        )


# Global Redis configuration
redis_config = RedisConfig()


def get_redis_client() -> Optional[redis.Redis]:
    """
    Get Redis client (convenience function)
    
    Returns:
        Redis client or None if unavailable
    """
    return redis_config.create_client()


def test_redis_connection() -> bool:
    """
    Test Redis connection
    
    Returns:
        True if Redis is available, False otherwise
    """
    client = get_redis_client()
    if client:
        try:
            client.ping()
            return True
        except:
            return False
    return False


# Example usage:
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("Redis Configuration Test")
    print("=" * 60)
    print()
    print(f"Configuration: {redis_config}")
    print()
    
    client = get_redis_client()
    if client:
        print("✅ Redis is available!")
        print(f"   Server Info: {client.info('server')['redis_version']}")
    else:
        print("⚠️  Redis is not available (using in-memory fallback)")
    
    print()
    print("=" * 60)
