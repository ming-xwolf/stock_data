"""
AND组合器

所有条件必须同时满足。
"""
import logging
from typing import List, Optional, Dict, Any

from .base import BaseCombinator

logger = logging.getLogger(__name__)


class AndCombinator(BaseCombinator):
    """AND组合器：所有条件必须同时满足"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        链式筛选：每个条件基于上一个条件的结果
        
        Args:
            stock_codes: 输入的股票代码列表
            context: 上下文信息
        
        Returns:
            同时满足所有条件的股票代码列表
        """
        if not self.conditions:
            return stock_codes
        
        if not stock_codes:
            return []
        
        # 链式筛选：每个条件基于上一个条件的结果
        result = stock_codes
        for i, condition in enumerate(self.conditions):
            before_count = len(result)
            result = condition.filter(result, context)
            after_count = len(result)
            
            logger.debug(
                f"AND条件 {i+1}/{len(self.conditions)} ({condition.get_name()}): "
                f"{before_count} -> {after_count}"
            )
            
            if not result:  # 提前终止
                logger.debug("AND组合器提前终止：没有符合条件的股票")
                break
        
        return result
