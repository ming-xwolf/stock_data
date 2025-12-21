"""
SQL 查询语句管理模块

提供统一的 SQL 查询语句管理，支持 Supabase (PostgreSQL)。
"""

from .sql_manager import SQLManager, sql_manager

__all__ = ['SQLManager', 'sql_manager']
