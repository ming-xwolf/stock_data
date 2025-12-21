"""
选股条件基类

定义统一的选股条件接口，采用管道式设计。
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class BaseCondition(ABC):
    """选股条件基类 - 管道式设计"""
    
    def __init__(self, **kwargs):
        """
        初始化条件
        
        Args:
            **kwargs: 条件参数
        """
        self.params = kwargs
    
    @abstractmethod
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选股票代码
        
        Args:
            stock_codes: 输入的股票代码列表
            context: 上下文信息（可选），可包含：
                - db_manager: 数据库管理器
                - fetch_service: 数据获取服务
                - 其他共享数据
        
        Returns:
            符合条件的股票代码列表
        """
        pass
    
    def get_name(self) -> str:
        """
        获取条件名称（用于日志和调试）
        
        Returns:
            条件名称
        """
        return self.__class__.__name__
    
    def get_description(self) -> str:
        """
        获取条件描述（用于展示）
        
        Returns:
            条件描述
        """
        return f"{self.get_name()}({self.params})"
