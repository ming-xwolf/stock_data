"""
条件组合器基类

提供条件组合的基础功能。
"""
from typing import List, Optional, Dict, Any
from ..conditions.base import BaseCondition


class BaseCombinator(BaseCondition):
    """组合器基类"""
    
    def __init__(self, conditions: List[BaseCondition], **kwargs):
        """
        初始化组合器
        
        Args:
            conditions: 条件列表
            **kwargs: 其他参数
        """
        super().__init__(**kwargs)
        self.conditions = conditions
    
    def get_description(self) -> str:
        """获取组合器描述"""
        conditions_desc = [c.get_description() for c in self.conditions]
        return f"{self.get_name()}({', '.join(conditions_desc)})"
