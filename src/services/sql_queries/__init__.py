"""
SQL 查询语句管理模块

提供统一的 SQL 查询语句管理，支持 Dolt (MySQL) 和 Supabase (PostgreSQL)。
根据数据库类型自动选择对应的 SQL 语句。
"""

from .sql_manager import SQLManager, sql_manager

__all__ = ['SQLManager', 'sql_manager']
