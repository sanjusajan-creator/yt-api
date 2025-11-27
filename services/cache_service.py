"""
Cache Service
Provides intelligent caching for API responses
"""
from cachetools import TTLCache
from typing import Any, Optional, Dict
import hashlib
import json
import logging
from config import CACHE_ENABLED, CACHE_TTL

logger = logging.getLogger(__name__)


class CacheService:
    """TTL-based cache service for API responses"""
    
    def __init__(self):
        self.enabled = CACHE_ENABLED
        self.caches: Dict[str, TTLCache] = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0
        }
        self._initialize_caches()
    
    def _initialize_caches(self):
        """Initialize separate caches for different endpoint types"""
        for cache_type, ttl in CACHE_TTL.items():
            # Create cache with max 1000 items and specified TTL
            self.caches[cache_type] = TTLCache(maxsize=1000, ttl=ttl)
            logger.info(f"Initialized {cache_type} cache with TTL={ttl}s")
    
    def _generate_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate a unique cache key from endpoint and parameters"""
        # Sort params for consistent key generation
        sorted_params = json.dumps(params, sort_keys=True)
        combined = f"{endpoint}:{sorted_params}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, cache_type: str, endpoint: str, params: Dict[str, Any]) -> Optional[Any]:
        """
        Get cached value
        
        Args:
            cache_type: Type of cache (search, video, etc.)
            endpoint: API endpoint name
            params: Request parameters
        
        Returns:
            Cached value or None
        """
        if not self.enabled:
            return None
        
        cache = self.caches.get(cache_type, self.caches.get("default"))
        key = self._generate_key(endpoint, params)
        
        try:
            value = cache.get(key)
            if value is not None:
                self.stats["hits"] += 1
                logger.debug(f"Cache HIT for {endpoint}")
                return value
            else:
                self.stats["misses"] += 1
                logger.debug(f"Cache MISS for {endpoint}")
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, cache_type: str, endpoint: str, params: Dict[str, Any], value: Any):
        """
        Set cached value
        
        Args:
            cache_type: Type of cache (search, video, etc.)
            endpoint: API endpoint name
            params: Request parameters
            value: Value to cache
        """
        if not self.enabled:
            return
        
        cache = self.caches.get(cache_type, self.caches.get("default"))
        key = self._generate_key(endpoint, params)
        
        try:
            cache[key] = value
            self.stats["sets"] += 1
            logger.debug(f"Cached {endpoint}")
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def clear(self, cache_type: Optional[str] = None):
        """Clear cache(s)"""
        if cache_type:
            if cache_type in self.caches:
                self.caches[cache_type].clear()
                logger.info(f"Cleared {cache_type} cache")
        else:
            for cache in self.caches.values():
                cache.clear()
            logger.info("Cleared all caches")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        cache_sizes = {
            cache_type: len(cache) 
            for cache_type, cache in self.caches.items()
        }
        
        return {
            "enabled": self.enabled,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "sets": self.stats["sets"],
            "total_requests": total_requests,
            "hit_rate": f"{hit_rate:.2f}%",
            "cache_sizes": cache_sizes
        }


# Global cache service instance
cache_service = CacheService()
