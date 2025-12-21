"""
Dolt (MySQL) 数据库连接模块
"""
import logging
from contextlib import contextmanager
from typing import Optional

from .dolt_config import DoltConfig

logger = logging.getLogger(__name__)

# 尝试导入 MySQL 驱动
try:
    import pymysql
    from pymysql.cursors import DictCursor
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    pymysql = None
    DictCursor = None


class DoltConnection:
    """Dolt (MySQL) 数据库连接类"""
    
    def __init__(self, config: Optional[DoltConfig] = None):
        """
        初始化 Dolt 连接
        
        Args:
            config: Dolt 配置对象，如果为 None 则创建新配置
        """
        self.config = config or DoltConfig()
        self._check_driver()
    
    def _check_driver(self):
        """检查 MySQL 驱动是否可用"""
        if not MYSQL_AVAILABLE:
            raise ImportError(
                "pymysql 未安装，无法使用 Dolt 数据库。"
                "请运行: pip install pymysql"
            )
    
    def _get_cursor(self, conn, cursor_type=None):
        """
        获取游标对象
        
        Args:
            conn: 数据库连接对象
            cursor_type: 游标类型，默认为 DictCursor
            
        Returns:
            游标对象
        """
        cursor_class = cursor_type if cursor_type else DictCursor
        return conn.cursor(cursor_class)
    
    @contextmanager
    def get_connection(self, cursor_type=None):
        """
        获取数据库连接的上下文管理器
        
        Args:
            cursor_type: 游标类型，默认为 DictCursor
            
        Yields:
            数据库连接对象
        """
        conn = None
        try:
            params = self.config.get_connection_params()
            params['cursorclass'] = cursor_type if cursor_type else DictCursor
            conn = pymysql.connect(**params)
            
            logger.debug(f"Dolt 数据库连接已建立: {self.config}")
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Dolt 数据库操作失败: {e}", exc_info=True)
            raise
        finally:
            if conn:
                conn.close()
                logger.debug("Dolt 数据库连接已关闭")
    
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
            with self._get_cursor(conn) as cursor:
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
            with self._get_cursor(conn) as cursor:
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
            with self._get_cursor(conn) as cursor:
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
                with self._get_cursor(conn) as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result is not None
        except Exception as e:
            logger.error(f"Dolt 数据库连接测试失败: {e}")
            return False
