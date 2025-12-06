"""
Cache Manager for in-memory caching and DAX integration
Provides fast access to frequently accessed data
"""
import os
import logging
import time
from typing import Any, Optional
from collections import OrderedDict
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages in-memory cache and DAX cluster for ultra-low latency"""
    
    def __init__(self):
        self.in_memory_cache = OrderedDict()
        self.cache_size = int(os.getenv('CACHE_SIZE', '10000'))
        self.dax_endpoint = os.getenv('DAX_ENDPOINT', None)
        self.dax_client = None
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0
        }
        
        # Initialize DAX client if endpoint is provided
        if self.dax_endpoint:
            try:
                from amazondax import AmazonDaxClient
                self.dax_client = AmazonDaxClient(
                    endpoint_url=self.dax_endpoint,
                    region_name=os.getenv('AWS_REGION', 'us-east-1')
                )
                logger.info(f"DAX client initialized: {self.dax_endpoint}")
            except ImportError:
                logger.warning("DAX client not available. Install amazon-dax-client package.")
            except Exception as e:
                logger.warning(f"Failed to initialize DAX client: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache (checks in-memory first, then DAX)
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None
        """
        # Check in-memory cache first
        if key in self.in_memory_cache:
            value, expiry = self.in_memory_cache[key]
            if expiry is None or time.time() < expiry:
                # Move to end (LRU)
                self.in_memory_cache.move_to_end(key)
                self.cache_stats['hits'] += 1
                return value
            else:
                # Expired, remove it
                del self.in_memory_cache[key]
        
        # Check DAX if available
        if self.dax_client:
            try:
                response = self.dax_client.get_item(
                    TableName=os.getenv('CACHE_TABLE_NAME', 'RecommendationCache'),
                    Key={'cache_key': {'S': key}}
                )
                if 'Item' in response:
                    value = self._deserialize(response['Item']['value']['S'])
                    expiry = float(response['Item'].get('expiry', {}).get('N', '0'))
                    if expiry == 0 or time.time() < expiry:
                        # Also store in in-memory cache
                        self._set_in_memory(key, value, expiry)
                        self.cache_stats['hits'] += 1
                        return value
            except Exception as e:
                logger.debug(f"DAX get error: {e}")
        
        self.cache_stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache (both in-memory and DAX)
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        
        Returns:
            True if successful
        """
        expiry = time.time() + ttl if ttl > 0 else None
        
        # Set in in-memory cache
        self._set_in_memory(key, value, expiry)
        
        # Set in DAX if available
        if self.dax_client:
            try:
                item = {
                    'cache_key': {'S': key},
                    'value': {'S': self._serialize(value)},
                    'expiry': {'N': str(expiry) if expiry else '0'},
                    'ttl': {'N': str(int(time.time()) + ttl)}
                }
                self.dax_client.put_item(
                    TableName=os.getenv('CACHE_TABLE_NAME', 'RecommendationCache'),
                    Item=item
                )
            except Exception as e:
                logger.debug(f"DAX set error: {e}")
        
        self.cache_stats['sets'] += 1
        return True
    
    def _set_in_memory(self, key: str, value: Any, expiry: Optional[float]):
        """Set value in in-memory LRU cache"""
        # Remove if exists
        if key in self.in_memory_cache:
            del self.in_memory_cache[key]
        
        # Add new entry
        self.in_memory_cache[key] = (value, expiry)
        
        # Evict if cache is full
        while len(self.in_memory_cache) > self.cache_size:
            self.in_memory_cache.popitem(last=False)  # Remove oldest
            self.cache_stats['evictions'] += 1
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        deleted = False
        
        if key in self.in_memory_cache:
            del self.in_memory_cache[key]
            deleted = True
        
        if self.dax_client:
            try:
                self.dax_client.delete_item(
                    TableName=os.getenv('CACHE_TABLE_NAME', 'RecommendationCache'),
                    Key={'cache_key': {'S': key}}
                )
                deleted = True
            except Exception as e:
                logger.debug(f"DAX delete error: {e}")
        
        return deleted
    
    def clear(self):
        """Clear all cache"""
        self.in_memory_cache.clear()
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0
        }
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'sets': self.cache_stats['sets'],
            'evictions': self.cache_stats['evictions'],
            'hit_rate': round(hit_rate, 2),
            'size': len(self.in_memory_cache),
            'max_size': self.cache_size,
            'dax_enabled': self.dax_client is not None
        }
    
    def is_active(self) -> bool:
        """Check if cache is active"""
        return True
    
    def _serialize(self, value: Any) -> str:
        """Serialize value for storage"""
        import json
        return json.dumps(value)
    
    def _deserialize(self, value: str) -> Any:
        """Deserialize value from storage"""
        import json
        return json.loads(value)

