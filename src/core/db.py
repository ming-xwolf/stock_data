"""
数据库操作模块

提供 Supabase (PostgreSQL) 数据库连接和基本操作功能。
"""
import logging
from typing import Optional

from .config import db_config
from .db_adapters import SupabaseConnection

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, config=None):
        """
        初始化数据库管理器
        
        Args:
            config: 数据库配置对象，如果为None则使用默认配置
        """
        self.config = config or db_config
        self._connection = SupabaseConnection(self.config.config)
    
    def get_connection(self):
        """
        获取数据库连接的上下文管理器
            
        Yields:
            数据库连接对象
        """
        return self._connection.get_connection()
    
    def execute_query(self, sql: str, params: Optional[tuple] = None) -> list:
        """
        执行查询语句
        
        Args:
            sql: SQL查询语句（PostgreSQL 语法）
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        return self._connection.execute_query(sql, params)
    
    def execute_update(self, sql: str, params: Optional[tuple] = None) -> int:
        """
        执行更新语句（INSERT, UPDATE, DELETE）
        
        Args:
            sql: SQL更新语句（PostgreSQL 语法）
            params: 更新参数
            
        Returns:
            受影响的行数
        """
        return self._connection.execute_update(sql, params)
    
    def execute_many(self, sql: str, params_list: list) -> int:
        """
        批量执行更新语句
        
        Args:
            sql: SQL更新语句（PostgreSQL 语法）
            params_list: 参数列表
            
        Returns:
            受影响的行数
        """
        return self._connection.execute_many(sql, params_list)
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            连接是否成功
        """
        return self._connection.test_connection()


# 全局数据库管理器实例
db_manager = DatabaseManager()

