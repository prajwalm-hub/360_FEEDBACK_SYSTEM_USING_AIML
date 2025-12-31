"""
High-performance caching layer for NLP results
Provides in-memory LRU cache with optional Redis backend for distributed caching
"""
from __future__ import annotations
import hashlib
import json
import logging
from typing import Any, Optional, Dict
from functools import lru_cache
from datetime import timedelta

logger = logging.getLogger(__name__)

# Try to import Redis, fall back to in-memory only
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache only")


class NewsCache:
    """High-performance cache for NLP analysis results"""
    
    def __init__(self, redis_url: Optional[str] = None, ttl: int = 86400):
        """
        Initialize cache
        
        Args:
            redis_url: Redis connection URL (optional)
            ttl: Time-to-live in seconds (default: 24 hours)
        """
        self.ttl = ttl
        self.redis_client = None
        
        # Try to connect to Redis if available
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Connected to Redis cache")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}, using in-memory cache only")
                self.redis_client = None
    
    @staticmethod
    def _hash_key(text: str, prefix: str = "") -> str:
        """Generate cache key from text"""
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"{prefix}:{text_hash}" if prefix else text_hash
    
    def get_sentiment(self, text: str) -> Optional[Dict[str, Any]]:
        """Get cached sentiment analysis result"""
        key = self._hash_key(text, "sentiment")
        
        # Try Redis first
        if self.redis_client:
            try:
                cached = self.redis_client.get(key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
        
        return None
    
    def set_sentiment(self, text: str, result: Dict[str, Any]) -> None:
        """Cache sentiment analysis result"""
        key = self._hash_key(text, "sentiment")
        
        if self.redis_client:
            try:
                self.redis_client.setex(
                    key,
                    self.ttl,
                    json.dumps(result)
                )
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")
    
    def get_translation(self, text: str, src_lang: str, tgt_lang: str) -> Optional[str]:
        """Get cached translation"""
        key = self._hash_key(f"{text}:{src_lang}:{tgt_lang}", "translate")
        
        if self.redis_client:
            try:
                return self.redis_client.get(key)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
        
        return None
    
    def set_translation(self, text: str, src_lang: str, tgt_lang: str, translation: str) -> None:
        """Cache translation result"""
        key = self._hash_key(f"{text}:{src_lang}:{tgt_lang}", "translate")
        
        if self.redis_client:
            try:
                self.redis_client.setex(key, self.ttl, translation)
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")
    
    def get_classification(self, text: str) -> Optional[Dict[str, Any]]:
        """Get cached classification result"""
        key = self._hash_key(text, "classify")
        
        if self.redis_client:
            try:
                cached = self.redis_client.get(key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
        
        return None
    
    def set_classification(self, text: str, result: Dict[str, Any]) -> None:
        """Cache classification result"""
        key = self._hash_key(text, "classify")
        
        if self.redis_client:
            try:
                self.redis_client.setex(
                    key,
                    self.ttl,
                    json.dumps(result)
                )
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")
    
    def get_entities(self, text: str) -> Optional[list]:
        """Get cached NER result"""
        key = self._hash_key(text, "ner")
        
        if self.redis_client:
            try:
                cached = self.redis_client.get(key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
        
        return None
    
    def set_entities(self, text: str, entities: list) -> None:
        """Cache NER result"""
        key = self._hash_key(text, "ner")
        
        if self.redis_client:
            try:
                self.redis_client.setex(
                    key,
                    self.ttl,
                    json.dumps(entities)
                )
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")
    
    def get_scheme_detection(self, text: str, language: str) -> Optional[list]:
        """Get cached scheme detection result"""
        key = self._hash_key(f"{text}:{language}", "schemes")
        
        if self.redis_client:
            try:
                cached = self.redis_client.get(key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
        
        return None
    
    def set_scheme_detection(self, text: str, language: str, schemes: list) -> None:
        """Cache scheme detection result"""
        key = self._hash_key(f"{text}:{language}", "schemes")
        
        if self.redis_client:
            try:
                # Longer TTL for scheme detection (rarely changes)
                self.redis_client.setex(
                    key,
                    self.ttl * 7,  # 7 days
                    json.dumps(schemes)
                )
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")
    
    def clear(self) -> None:
        """Clear all cache"""
        if self.redis_client:
            try:
                # Delete all keys with our prefixes
                for prefix in ['sentiment', 'translate', 'classify', 'ner', 'schemes']:
                    keys = self.redis_client.keys(f"{prefix}:*")
                    if keys:
                        self.redis_client.delete(*keys)
                logger.info("Cache cleared")
            except Exception as e:
                logger.warning(f"Failed to clear cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if self.redis_client:
            try:
                info = self.redis_client.info('stats')
                return {
                    'total_keys': self.redis_client.dbsize(),
                    'hits': info.get('keyspace_hits', 0),
                    'misses': info.get('keyspace_misses', 0),
                    'hit_rate': info.get('keyspace_hits', 0) / max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1), 1)
                }
            except Exception as e:
                logger.warning(f"Failed to get cache stats: {e}")
        
        return {'total_keys': 0, 'hits': 0, 'misses': 0, 'hit_rate': 0.0}


# Global cache instance
_cache_instance: Optional[NewsCache] = None


def get_cache(redis_url: Optional[str] = None) -> NewsCache:
    """Get or create global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = NewsCache(redis_url=redis_url)
    return _cache_instance


# In-memory LRU cache decorators for frequently called functions
@lru_cache(maxsize=1000)
def cached_language_detection(text_hash: str):
    """LRU cache for language detection (stores text hash -> language)"""
    pass  # Actual implementation in language_processor.py


@lru_cache(maxsize=500)
def cached_goi_keywords(language: str):
    """LRU cache for GoI keywords by language"""
    pass  # Actual implementation in goi_filter.py


@lru_cache(maxsize=10)
def cached_scheme_names():
    """LRU cache for scheme names list"""
    pass  # Actual implementation in schemes_database.py
