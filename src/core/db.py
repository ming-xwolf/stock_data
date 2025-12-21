"""
数据库操作模块

提供数据库连接和基本操作功能。
支持 Supabase (PostgreSQL) 和 Dolt (MySQL) 数据库。
默认使用 Supabase 数据库。
"""
import logging
from typing import Optional

from .config import db_config
from .db_adapters import (
    SupabaseConnection,
    DoltConnection,
    SQLAdapter,
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理类（统一接口）"""
    
    def __init__(self, config=None):
        """
        初始化数据库管理器
        
        Args:
            config: 数据库配置对象，如果为None则使用默认配置
        """
        self.config = config or db_config
        self._connection = None
        self.sql_adapter = SQLAdapter()
        
        # 根据配置类型创建对应的连接对象
        if self.config.db_type == 'supabase':
            self._connection = SupabaseConnection(self.config.config)
        else:
            self._connection = DoltConnection(self.config.config)
    
    def get_connection(self, cursor_type=None):
        """
        获取数据库连接的上下文管理器
        
        Args:
            cursor_type: 游标类型（仅用于 MySQL，PostgreSQL 固定使用 RealDictCursor）
            
        Yields:
            数据库连接对象
        """
        return self._connection.get_connection(cursor_type)
    
    def _adapt_sql(self, sql: str) -> str:
        """
        根据数据库类型适配 SQL 语句
        
        Args:
            sql: 原始 SQL 语句
            
        Returns:
            适配后的 SQL 语句
        """
        if self.config.db_type == 'supabase':
            return self.sql_adapter.convert_mysql_to_postgresql(sql)
        return sql
    
    def execute_query(self, sql: str, params: Optional[tuple] = None) -> list:
        """
        执行查询语句
        
        Args:
            sql: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        sql = self._adapt_sql(sql)
        return self._connection.execute_query(sql, params)
    
    def execute_update(self, sql: str, params: Optional[tuple] = None) -> int:
        """
        执行更新语句（INSERT, UPDATE, DELETE）
        
        Args:
            sql: SQL更新语句
            params: 更新参数
            
        Returns:
            受影响的行数
        """
        sql = self._adapt_sql(sql)
        return self._connection.execute_update(sql, params)
    
    def execute_many(self, sql: str, params_list: list) -> int:
        """
        批量执行更新语句
        
        Args:
            sql: SQL更新语句
            params_list: 参数列表
            
        Returns:
            受影响的行数
        """
        sql = self._adapt_sql(sql)
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

