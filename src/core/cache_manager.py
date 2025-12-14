"""
缓存管理模块

为AKShare API调用提供统一的缓存机制。
"""
import logging
from functools import lru_cache, wraps
from datetime import datetime, timedelta
from typing import Callable, Any, Optional, Dict
import hashlib
import json

logger = logging.getLogger(__name__)


class TimedCache:
    """带过期时间的缓存类"""
    
    def __init__(self, default_ttl: int = 3600):
        """
        初始化缓存
        
        Args:
            default_ttl: 默认过期时间（秒），默认1小时
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期返回None
        """
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        expire_time = entry.get('expire_time')
        
        if expire_time and datetime.now() > expire_time:
            # 缓存已过期，删除
            del self._cache[key]
            return None
        
        return entry.get('value')
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），如果为None则使用默认值
        """
        ttl = ttl or self.default_ttl
        expire_time = datetime.now() + timedelta(seconds=ttl)
        
        self._cache[key] = {
            'value': value,
            'expire_time': expire_time,
            'created_at': datetime.now()
        }
    
    def clear(self) -> None:
        """清除所有缓存"""
        self._cache.clear()
        logger.info("缓存已清除")
    
    def clear_expired(self) -> int:
        """
        清除已过期的缓存
        
        Returns:
            清除的缓存数量
        """
        now = datetime.now()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.get('expire_time') and now > entry['expire_time']
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"清除了 {len(expired_keys)} 个过期缓存")
        
        return len(expired_keys)
    
    def size(self) -> int:
        """返回缓存数量"""
        return len(self._cache)


# 全局缓存实例
# 不同API使用不同的缓存时间
_cache_stock_basic_info = TimedCache(default_ttl=86400)  # 24小时
_cache_stock_list = TimedCache(default_ttl=3600)  # 1小时
_cache_stock_controller = TimedCache(default_ttl=86400)  # 24小时
_cache_stock_shareholders = TimedCache(default_ttl=86400)  # 24小时
_cache_stock_market_value = TimedCache(default_ttl=300)  # 5分钟（市值数据变化较快）
_cache_stock_financial = TimedCache(default_ttl=86400)  # 24小时


def cached_api_call(cache_instance: TimedCache, ttl: Optional[int] = None):
    """
    装饰器：为API调用添加缓存
    
    Args:
        cache_instance: 缓存实例
        ttl: 缓存过期时间（秒），如果为None则使用缓存实例的默认值
    
    Usage:
        @cached_api_call(_cache_stock_basic_info, ttl=3600)
        def get_stock_info(code: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键：函数名 + 参数
            cache_key_parts = [func.__name__]
            
            # 添加位置参数
            for arg in args:
                cache_key_parts.append(str(arg))
            
            # 添加关键字参数（排序以确保一致性）
            if kwargs:
                sorted_kwargs = sorted(kwargs.items())
                cache_key_parts.extend([f"{k}={v}" for k, v in sorted_kwargs])
            
            cache_key = "|".join(cache_key_parts)
            
            # 尝试从缓存获取
            cached_value = cache_instance.get(cache_key)
            if cached_value is not None:
                logger.debug(f"缓存命中: {func.__name__}({cache_key})")
                return cached_value
            
            # 调用原函数
            try:
                result = func(*args, **kwargs)
                
                # 如果结果不为None，则缓存
                if result is not None:
                    cache_instance.set(cache_key, result, ttl)
                    logger.debug(f"缓存设置: {func.__name__}({cache_key})")
                
                return result
            except Exception as e:
                logger.error(f"API调用失败: {func.__name__}({cache_key}): {e}")
                raise
        
        return wrapper
    return decorator


def clear_all_caches():
    """清除所有缓存"""
    _cache_stock_basic_info.clear()
    _cache_stock_list.clear()
    _cache_stock_controller.clear()
    _cache_stock_shareholders.clear()
    _cache_stock_market_value.clear()
    _cache_stock_financial.clear()
    logger.info("所有缓存已清除")


def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    return {
        'stock_basic_info': _cache_stock_basic_info.size(),
        'stock_list': _cache_stock_list.size(),
        'stock_controller': _cache_stock_controller.size(),
        'stock_shareholders': _cache_stock_shareholders.size(),
        'stock_market_value': _cache_stock_market_value.size(),
        'stock_financial': _cache_stock_financial.size(),
    }

