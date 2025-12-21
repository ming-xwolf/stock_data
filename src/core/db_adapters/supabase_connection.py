"""
Supabase (PostgreSQL) 数据库连接模块
"""
import logging
from contextlib import contextmanager
from typing import Optional

from .supabase_config import SupabaseConfig

logger = logging.getLogger(__name__)

# 尝试导入 PostgreSQL 驱动
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    psycopg2 = None
    RealDictCursor = None


class SupabaseConnection:
    """Supabase (PostgreSQL) 数据库连接类"""
    
    def __init__(self, config: Optional[SupabaseConfig] = None):
        """
        初始化 Supabase 连接
        
        Args:
            config: Supabase 配置对象，如果为 None 则创建新配置
        """
        self.config = config or SupabaseConfig()
        self._check_driver()
    
    def _check_driver(self):
        """检查 PostgreSQL 驱动是否可用"""
        if not POSTGRESQL_AVAILABLE:
            raise ImportError(
                "psycopg2 未安装，无法使用 Supabase 数据库。"
                "请运行: pip install psycopg2"
            )
    
    def _get_cursor(self, conn, cursor_type=None):
        """
        获取游标对象
        
        Args:
            conn: 数据库连接对象
            cursor_type: 游标类型（PostgreSQL 固定使用 RealDictCursor，此参数被忽略）
            
        Returns:
            游标对象
        """
        return conn.cursor(cursor_factory=RealDictCursor)
    
    @contextmanager
    def get_connection(self, cursor_type=None):
        """
        获取数据库连接的上下文管理器
        
        Args:
            cursor_type: 游标类型（PostgreSQL 固定使用 RealDictCursor，此参数被忽略）
            
        Yields:
            数据库连接对象
        """
        conn = None
        try:
            params = self.config.get_connection_params()
            
            if 'uri' in params:
                conn = psycopg2.connect(params['uri'])
            else:
                conn = psycopg2.connect(
                    host=params['host'],
                    port=params['port'],
                    user=params['user'],
                    password=params['password'],
                    database=params['database']
                )
            conn.autocommit = False
            
            logger.debug(f"Supabase 数据库连接已建立: {self.config}")
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Supabase 数据库操作失败: {e}", exc_info=True)
            raise
        finally:
            if conn:
                conn.close()
                logger.debug("Supabase 数据库连接已关闭")
    
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
                cursor.execute(sql, params)
                affected_rows = cursor.rowcount
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
                cursor.executemany(sql, params_list)
                affected_rows = cursor.rowcount
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
            logger.error(f"Supabase 数据库连接测试失败: {e}")
            return False
