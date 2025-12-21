"""
选股服务

提供统一的选股接口。
"""
import logging
from typing import List, Optional, Dict, Any

from .conditions.base import BaseCondition
from ..core.db import db_manager
from ..services.stock_service import StockService
from ..services.fetch_data_service import fetch_data_service

logger = logging.getLogger(__name__)


class ScreeningService:
    """选股服务"""
    
    def __init__(self):
        self.stock_service = StockService()
        # 缓存所有股票列表（避免重复查询）
        self._all_stocks_cache = None
    
    def _get_initial_codes(self, initial_codes: Optional[List[str]]) -> List[str]:
        """
        获取初始股票代码列表（使用缓存）
        
        Args:
            initial_codes: 用户提供的初始代码列表
        
        Returns:
            股票代码列表
        """
        if initial_codes is not None:
            return initial_codes
        
        # 使用缓存
        if self._all_stocks_cache is None:
            all_stocks = self.stock_service.get_all_stocks()
            self._all_stocks_cache = [s['code'] for s in all_stocks]
        
        return self._all_stocks_cache
    
    def _prepare_context(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        准备上下文信息
        
        Args:
            context: 用户提供的上下文
        
        Returns:
            准备好的上下文
        """
        if context is None:
            context = {}
        
        # 设置默认服务
        context.setdefault('db_manager', db_manager)
        context.setdefault('fetch_service', fetch_data_service)
        
        return context
    
    def screen_stocks(
        self,
        condition: BaseCondition,
        initial_codes: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        执行选股查询
        
        Args:
            condition: 选股条件（可以是单个条件或组合器）
            initial_codes: 初始股票代码列表，如果为None则使用所有股票
            context: 上下文信息（可选），可包含：
                - db_manager: 数据库管理器
                - fetch_service: 数据获取服务
                - 其他共享数据
        
        Returns:
            符合条件的股票信息列表
        """
        # 准备上下文和初始代码
        context = self._prepare_context(context)
        initial_codes = self._get_initial_codes(initial_codes)
        
        logger.info(f"开始选股，初始股票数量: {len(initial_codes)}")
        logger.info(f"选股条件: {condition.get_description()}")
        
        # 执行筛选
        filtered_codes = condition.filter(initial_codes, context)
        
        logger.info(f"筛选完成，符合条件的股票数量: {len(filtered_codes)}")
        
        # 获取股票详细信息
        result = []
        for code in filtered_codes:
            stock = self.stock_service.get_stock(code)
            if stock:
                result.append(stock)
        
        return result
    
    def count_stocks(
        self,
        condition: BaseCondition,
        initial_codes: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        统计符合条件的股票数量（不获取详细信息，性能更好）
        
        Args:
            condition: 选股条件
            initial_codes: 初始股票代码列表
            context: 上下文信息
        
        Returns:
            符合条件的股票数量
        """
        # 准备上下文和初始代码
        context = self._prepare_context(context)
        initial_codes = self._get_initial_codes(initial_codes)
        
        filtered_codes = condition.filter(initial_codes, context)
        return len(filtered_codes)
    
    def get_stock_codes(
        self,
        condition: BaseCondition,
        initial_codes: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        获取符合条件的股票代码列表（不获取详细信息，性能最好）
        
        Args:
            condition: 选股条件
            initial_codes: 初始股票代码列表
            context: 上下文信息
        
        Returns:
            符合条件的股票代码列表
        """
        # 准备上下文和初始代码
        context = self._prepare_context(context)
        initial_codes = self._get_initial_codes(initial_codes)
        
        return condition.filter(initial_codes, context)
    
    def clear_cache(self):
        """清除缓存"""
        self._all_stocks_cache = None
