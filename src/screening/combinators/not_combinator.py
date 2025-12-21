"""
NOT组合器

条件取反。
"""
import logging
from typing import List, Optional, Dict, Any, Set

from .base import BaseCombinator

logger = logging.getLogger(__name__)


class NotCombinator(BaseCombinator):
    """NOT组合器：条件取反"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        返回不满足条件的股票代码
        
        Args:
            stock_codes: 输入的股票代码列表
            context: 上下文信息
        
        Returns:
            不满足条件的股票代码列表
        """
        if not self.conditions:
            return stock_codes
        
        if not stock_codes:
            return []
        
        # 获取满足条件的股票代码
        matched_set: Set[str] = set()
        for condition in self.conditions:
            matched = condition.filter(stock_codes, context)
            matched_set.update(matched)
        
        # 返回不满足条件的股票代码
        all_set = set(stock_codes)
        result = list(all_set - matched_set)
        
        logger.debug(
            f"NOT组合器: 输入 {len(stock_codes)} 只股票, "
            f"匹配 {len(matched_set)} 只, "
            f"结果 {len(result)} 只"
        )
        
        return result
