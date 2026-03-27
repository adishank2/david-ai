"""
Response caching system for David AI.
Caches common responses to avoid redundant LLM calls.
"""

import json
import os
import hashlib
import time
from typing import Optional, Dict, Any
from core.logger import get_logger

logger = get_logger(__name__)

class ResponseCache:
    """LRU cache for AI responses."""
    
    def __init__(self, max_size=100, ttl_seconds=3600):
        """
        Initialize response cache.
        
        Args:
            max_size: Maximum number of cached responses
            ttl_seconds: Time to live for cached responses (default 1 hour)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_order = []
        
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key from query."""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def get(self, query: str) -> Optional[str]:
        """
        Get cached response for query.
        
        Args:
            query: User query
            
        Returns:
            Cached response or None if not found/expired
        """
        key = self._get_cache_key(query)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if time.time() - entry['timestamp'] > self.ttl_seconds:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
            logger.debug(f"Cache expired for query: {query[:50]}")
            return None
        
        # Update access order (LRU)
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        
        logger.debug(f"Cache hit for query: {query[:50]}")
        return entry['response']
    
    def set(self, query: str, response: str):
        """
        Cache a response.
        
        Args:
            query: User query
            response: AI response
        """
        key = self._get_cache_key(query)
        
        # Evict oldest if at max size
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
            logger.debug("Cache evicted oldest entry")
        
        self.cache[key] = {
            'query': query,
            'response': response,
            'timestamp': time.time()
        }
        
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        
        logger.debug(f"Cached response for query: {query[:50]}")
    
    def clear(self):
        """Clear all cached responses."""
        self.cache.clear()
        self.access_order.clear()
        logger.info("Response cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'ttl_seconds': self.ttl_seconds
        }

# Global cache instance
_cache = ResponseCache()

def get_cache() -> ResponseCache:
    """Get the global cache instance."""
    return _cache
