"""
SQL 查询管理器

根据数据库类型自动选择对应的 SQL 语句。
"""
from typing import Dict, Any
from ...core.config import db_config


class SQLManager:
    """SQL 查询管理器"""
    
    def __init__(self, db_type: str = None):
        """
        初始化 SQL 管理器
        
        Args:
            db_type: 数据库类型，'supabase' 或 'dolt'。如果为 None，则从配置读取
        """
        self.db_type = db_type or db_config.db_type
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
        # 构建属性名：sql_name + _DOLT 或 _SUPABASE
        db_suffix = 'DOLT' if self.db_type == 'dolt' else 'SUPABASE'
        sql_attr = f"{sql_name}_{db_suffix}"
        
        # 先尝试获取特定数据库的 SQL
        if hasattr(sql_module, sql_attr):
            return getattr(sql_module, sql_attr)
        
        # 如果没有特定数据库的 SQL，尝试通用 SQL（向后兼容）
        if hasattr(sql_module, sql_name):
            return getattr(sql_module, sql_name)
        
        raise AttributeError(
            f"SQL '{sql_name}' not found in module. "
            f"Tried: {sql_attr}, {sql_name}"
        )


# 全局 SQL 管理器实例
sql_manager = SQLManager()
