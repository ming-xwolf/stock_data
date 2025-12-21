"""
SQL 查询管理器

自动选择 Supabase (PostgreSQL) 对应的 SQL 语句。
"""
from typing import Dict, Any
from ...core.config import db_config


class SQLManager:
    """SQL 查询管理器"""
    
    def __init__(self):
        """初始化 SQL 管理器"""
        self._cache: Dict[str, Any] = {}
    
    def get_sql(self, sql_module: Any, sql_name: str) -> str:
        """
        获取 SQL 语句
        
        Args:
            sql_module: SQL 模块对象（如 stock_sql, etf_sql 等）
            sql_name: SQL 语句名称（如 'INSERT_STOCK', 'SELECT_STOCK' 等）
            
        Returns:
            SQL 语句字符串
        """
        # 直接使用 sql_name（已统一为 PostgreSQL 语法）
        if hasattr(sql_module, sql_name):
            return getattr(sql_module, sql_name)
        
        raise AttributeError(
            f"SQL '{sql_name}' not found in module {sql_module.__name__}"
        )


# 全局 SQL 管理器实例
sql_manager = SQLManager()
