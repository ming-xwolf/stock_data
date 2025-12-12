"""
数据库操作模块

提供数据库连接和基本操作功能。
"""
import logging
from contextlib import contextmanager
from typing import Optional

import pymysql
from pymysql.cursors import DictCursor

from .config import db_config

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
        self._connection: Optional[pymysql.Connection] = None
    
    @contextmanager
    def get_connection(self, cursor_type=DictCursor):
        """
        获取数据库连接的上下文管理器
        
        Args:
            cursor_type: 游标类型，默认为DictCursor
            
        Yields:
            数据库连接对象
        """
        conn = None
        try:
            params = self.config.get_connection_params()
            params['cursorclass'] = cursor_type
            conn = pymysql.connect(**params)
            logger.debug(f"数据库连接已建立: {self.config}")
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库操作失败: {e}", exc_info=True)
            raise
        finally:
            if conn:
                conn.close()
                logger.debug("数据库连接已关闭")
    
    def execute_query(self, sql: str, params: Optional[tuple] = None) -> list:
        """
        执行查询语句
        
        Args:
            sql: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
    
    def execute_update(self, sql: str, params: Optional[tuple] = None) -> int:
        """
        执行更新语句（INSERT, UPDATE, DELETE）
        
        Args:
            sql: SQL更新语句
            params: 更新参数
            
        Returns:
            受影响的行数
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                affected_rows = cursor.execute(sql, params)
                conn.commit()
                return affected_rows
    
    def execute_many(self, sql: str, params_list: list) -> int:
        """
        批量执行更新语句
        
        Args:
            sql: SQL更新语句
            params_list: 参数列表
            
        Returns:
            受影响的行数
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                affected_rows = cursor.executemany(sql, params_list)
                conn.commit()
                return affected_rows
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            连接是否成功
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result is not None
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False


# 全局数据库管理器实例
db_manager = DatabaseManager()

