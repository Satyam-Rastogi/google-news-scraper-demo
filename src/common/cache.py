"""
Redis caching utilities
"""

import json
import pickle
from typing import Any, Optional, Union
from .config import config
from .logger import get_logger

logger = get_logger(__name__)

# Try to import redis, fallback to mock if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available. Caching will be disabled.")


class CacheManager:
    """Redis cache manager with fallback to in-memory cache"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self.enabled = config.enable_cache and REDIS_AVAILABLE
        
        if self.enabled:
            try:
                self.redis_client = redis.Redis(
                    host=config.redis_host,
                    port=config.redis_port,
                    db=config.redis_db,
                    password=config.redis_password,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache connected successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self.redis_client = None
                self.enabled = False
        else:
            logger.info("Using in-memory cache (Redis disabled)")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return self.memory_cache.get(key)
        
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        if not self.enabled:
            self.memory_cache[key] = value
            return True
        
        try:
            if self.redis_client:
                ttl = ttl or config.cache_ttl
                serialized_value = json.dumps(value, default=str)
                return self.redis_client.setex(key, ttl, serialized_value)
            return False
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return self.memory_cache.pop(key, None) is not None
        
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            return False
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.enabled:
            return key in self.memory_cache
        
        try:
            if self.redis_client:
                return bool(self.redis_client.exists(key))
            return False
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        if not self.enabled:
            self.memory_cache.clear()
            return True
        
        try:
            if self.redis_client:
                return bool(self.redis_client.flushdb())
            return False
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled:
            return {
                "type": "memory",
                "keys": len(self.memory_cache),
                "enabled": False
            }
        
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    "type": "redis",
                    "keys": info.get("db0", {}).get("keys", 0),
                    "memory_used": info.get("used_memory_human", "0B"),
                    "connected_clients": info.get("connected_clients", 0),
                    "enabled": True
                }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
        
        return {"type": "redis", "keys": 0, "enabled": False}


# Global cache manager instance
cache_manager = CacheManager()


def cache_key(prefix: str, *args) -> str:
    """Generate cache key from prefix and arguments"""
    key_parts = [prefix] + [str(arg) for arg in args]
    return ":".join(key_parts)


def cached(ttl: Optional[int] = None, key_prefix: str = "default"):
    """Decorator for caching function results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = cache_key(key_prefix, func.__name__, str(args), str(sorted(kwargs.items())))
            
            # Try to get from cache
            cached_result = cache_manager.get(key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {key}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(key, result, ttl)
            logger.debug(f"Cached result for key: {key}")
            return result
        
        return wrapper
    return decorator
