"""
OR组合器

任一条件满足即可。
"""
import logging
from typing import List, Optional, Dict, Any, Set

from .base import BaseCombinator

logger = logging.getLogger(__name__)


class OrCombinator(BaseCombinator):
    """OR组合器：任一条件满足即可"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        每个条件独立筛选，然后取并集
        
        Args:
            stock_codes: 输入的股票代码列表
            context: 上下文信息
        
        Returns:
            满足任一条件的股票代码列表
        """
        if not self.conditions:
            return stock_codes
        
        if not stock_codes:
            return []
        
        # 每个条件独立筛选，然后取并集
        result_set: Set[str] = set()
        for i, condition in enumerate(self.conditions):
            filtered = condition.filter(stock_codes, context)
            result_set.update(filtered)
            
            logger.debug(
                f"OR条件 {i+1}/{len(self.conditions)} ({condition.get_name()}): "
                f"筛选出 {len(filtered)} 只股票"
            )
        
        result = list(result_set)
        logger.debug(f"OR组合器最终结果: {len(result)} 只股票")
        return result
