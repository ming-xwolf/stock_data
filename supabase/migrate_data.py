#!/usr/bin/env python3
"""
数据迁移脚本：从 Dolt 数据库迁移数据到 Supabase

此脚本会：
1. 连接到 Dolt (MySQL) 数据库
2. 连接到 Supabase (PostgreSQL) 数据库
3. 获取所有表的数据
4. 将数据迁移到 Supabase
"""

import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse

import pymysql
from pymysql.cursors import DictCursor
import psycopg2
from psycopg2 import sql

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(dotenv_path=None):
        """简单的.env文件加载实现"""
        if dotenv_path is None:
            env_path = project_root / ".env"
        else:
            env_path = Path(dotenv_path)
        
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

# 加载环境变量（从项目根目录）
env_path = project_root / ".env"
load_dotenv(env_path)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DoltConnection:
    """Dolt 数据库连接类"""
    
    def __init__(self):
        """初始化 Dolt 连接配置"""
        self.host = os.getenv('DOLT_HOST', '192.168.2.35')
        self.port = int(os.getenv('DOLT_PORT', '13306'))
        self.user = os.getenv('DOLT_USER', 'root')
        self.password = os.getenv('DOLT_ROOT_PASSWORD', 'test')
        self.database = os.getenv('DOLT_DATABASE', 'a_stock')
        self.connection = None
    
    def connect(self):
        """连接到 Dolt 数据库"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=DictCursor
            )
            logger.info(f"成功连接到 Dolt 数据库: {self.host}:{self.port}/{self.database}")
            return True
        except Exception as e:
            logger.error(f"连接 Dolt 数据库失败: {e}")
            return False
    
    def get_tables(self) -> List[str]:
        """获取所有表名"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = [row[f'Tables_in_{self.database}'] for row in cursor.fetchall()]
                logger.info(f"找到 {len(tables)} 个表: {', '.join(tables)}")
                return tables
        except Exception as e:
            logger.error(f"获取表列表失败: {e}")
            return []
    
    def get_table_data(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表的所有数据"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM `{table_name}`")
                data = cursor.fetchall()
                logger.info(f"表 {table_name} 有 {len(data)} 条记录")
                return data
        except Exception as e:
            logger.error(f"获取表 {table_name} 数据失败: {e}")
            return []
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """获取表的列名"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DESCRIBE `{table_name}`")
                columns = [row['Field'] for row in cursor.fetchall()]
                return columns
        except Exception as e:
            logger.error(f"获取表 {table_name} 列信息失败: {e}")
            return []
    
    def close(self):
        """关闭连接"""
        if self.connection:
            self.connection.close()
            logger.info("Dolt 数据库连接已关闭")


class SupabaseConnection:
    """Supabase 数据库连接类"""
    
    def __init__(self, uri: str):
        """
        初始化 Supabase 连接
        
        Args:
            uri: PostgreSQL 连接 URI
        """
        self.uri = uri
        self.connection = None
        self._parse_uri()
    
    def _parse_uri(self):
        """解析连接 URI（用于日志显示）"""
        parsed = urlparse(self.uri)
        self.host = parsed.hostname
        self.port = parsed.port or 5432
        self.database = parsed.path.lstrip('/')
    
    def connect(self):
        """连接到 Supabase 数据库"""
        try:
            # 直接使用 URI 连接（psycopg2 支持 URI 格式）
            self.connection = psycopg2.connect(self.uri)
            self.connection.autocommit = False
            logger.info(f"成功连接到 Supabase 数据库: {self.host}:{self.port}/{self.database}")
            return True
        except Exception as e:
            logger.error(f"连接 Supabase 数据库失败: {e}")
            return False
    
    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    )
                """, (table_name,))
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"检查表 {table_name} 是否存在失败: {e}")
            return False
    
    def truncate_table(self, table_name: str):
        """清空表数据"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f'TRUNCATE TABLE "{table_name}" CASCADE')
                self.connection.commit()
                logger.info(f"已清空表 {table_name}")
        except Exception as e:
            logger.error(f"清空表 {table_name} 失败: {e}")
            self.connection.rollback()
            raise
    
    def insert_data(self, table_name: str, columns: List[str], data: List[Dict[str, Any]]):
        """
        插入数据到表
        
        Args:
            table_name: 表名
            columns: 列名列表
            data: 数据列表（字典列表）
        """
        if not data:
            logger.warning(f"表 {table_name} 没有数据需要插入")
            return
        
        try:
            with self.connection.cursor() as cursor:
                # 构建 INSERT 语句
                columns_quoted = [sql.Identifier(col) for col in columns]
                placeholders = ', '.join(['%s'] * len(columns))
                
                insert_query = sql.SQL("INSERT INTO {table} ({columns}) VALUES ({values})").format(
                    table=sql.Identifier(table_name),
                    columns=sql.SQL(', ').join(columns_quoted),
                    values=sql.SQL(placeholders)
                )
                
                # 准备数据
                values_list = []
                for row in data:
                    values = []
                    for col in columns:
                        value = row.get(col)
                        # 处理 None 值
                        if value is None:
                            values.append(None)
                        else:
                            values.append(value)
                    values_list.append(tuple(values))
                
                # 批量插入
                batch_size = 1000
                total_inserted = 0
                
                for i in range(0, len(values_list), batch_size):
                    batch = values_list[i:i + batch_size]
                    cursor.executemany(insert_query, batch)
                    total_inserted += len(batch)
                    logger.info(f"表 {table_name}: 已插入 {total_inserted}/{len(values_list)} 条记录")
                
                self.connection.commit()
                logger.info(f"表 {table_name}: 成功插入 {total_inserted} 条记录")
                
        except Exception as e:
            logger.error(f"插入表 {table_name} 数据失败: {e}")
            self.connection.rollback()
            raise
    
    def close(self):
        """关闭连接"""
        if self.connection:
            self.connection.close()
            logger.info("Supabase 数据库连接已关闭")


def migrate_table(dolt: DoltConnection, supabase: SupabaseConnection, table_name: str, 
                  truncate: bool = False):
    """
    迁移单个表的数据
    
    Args:
        dolt: Dolt 连接对象
        supabase: Supabase 连接对象
        table_name: 表名
        truncate: 是否在插入前清空目标表
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"开始迁移表: {table_name}")
    logger.info(f"{'='*60}")
    
    # 检查表是否存在
    if not supabase.table_exists(table_name):
        logger.warning(f"表 {table_name} 在 Supabase 中不存在，跳过")
        return
    
    # 获取列信息
    columns = dolt.get_table_columns(table_name)
    if not columns:
        logger.warning(f"无法获取表 {table_name} 的列信息，跳过")
        return
    
    logger.info(f"表 {table_name} 的列: {', '.join(columns)}")
    
    # 获取数据
    data = dolt.get_table_data(table_name)
    if not data:
        logger.info(f"表 {table_name} 没有数据，跳过")
        return
    
    # 如果需要，清空目标表
    if truncate:
        supabase.truncate_table(table_name)
    
    # 插入数据
    try:
        supabase.insert_data(table_name, columns, data)
        logger.info(f"✓ 表 {table_name} 迁移完成")
    except Exception as e:
        logger.error(f"✗ 表 {table_name} 迁移失败: {e}")
        raise


def main():
    """主函数"""
    logger.info("="*60)
    logger.info("开始数据迁移：Dolt -> Supabase")
    logger.info("="*60)
    
    # 获取 Supabase URI
    supabase_uri = os.getenv('SUPABASE_URI')
    if not supabase_uri:
        logger.error("未找到 SUPABASE_URI 环境变量")
        logger.error("请在 .env 文件中设置 SUPABASE_URI")
        return 1
    
    # 连接 Dolt
    dolt = DoltConnection()
    if not dolt.connect():
        return 1
    
    # 连接 Supabase
    supabase = SupabaseConnection(supabase_uri)
    if not supabase.connect():
        dolt.close()
        return 1
    
    try:
        # 获取所有表
        tables = dolt.get_tables()
        if not tables:
            logger.warning("没有找到任何表")
            return 0
        
        # 询问是否清空目标表
        print("\n是否在插入前清空目标表的数据？(y/n): ", end='')
        truncate_input = input().strip().lower()
        truncate = truncate_input in ('y', 'yes', '是')
        
        # 迁移每个表
        success_count = 0
        fail_count = 0
        
        for table_name in tables:
            try:
                migrate_table(dolt, supabase, table_name, truncate=truncate)
                success_count += 1
            except Exception as e:
                logger.error(f"迁移表 {table_name} 时发生错误: {e}")
                fail_count += 1
                # 询问是否继续
                print(f"\n迁移表 {table_name} 失败，是否继续迁移其他表？(y/n): ", end='')
                continue_input = input().strip().lower()
                if continue_input not in ('y', 'yes', '是'):
                    break
        
        # 输出总结
        logger.info("\n" + "="*60)
        logger.info("迁移完成")
        logger.info("="*60)
        logger.info(f"成功: {success_count} 个表")
        logger.info(f"失败: {fail_count} 个表")
        logger.info(f"总计: {len(tables)} 个表")
        
        return 0 if fail_count == 0 else 1
        
    finally:
        dolt.close()
        supabase.close()


if __name__ == '__main__':
    sys.exit(main())
