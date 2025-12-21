"""
数据库适配器模块

提供 Supabase (PostgreSQL) 数据库的配置和连接适配器。
"""

from .supabase_config import SupabaseConfig
from .supabase_connection import SupabaseConnection

__all__ = [
    'SupabaseConfig',
    'SupabaseConnection',
]
