"""
SQL 语法适配器

用于处理 MySQL 和 PostgreSQL 之间的 SQL 语法差异。
"""
import re
from typing import Dict


class SQLAdapter:
    """SQL 语法适配器，用于处理 MySQL 和 PostgreSQL 的语法差异"""
    
    # 表的主键映射（用于 ON CONFLICT）
    TABLE_PRIMARY_KEYS: Dict[str, str] = {
        'stocks': 'code',
        'stock_daily': 'code, trade_date',  # 复合主键
        'stock_industry': 'code',
        'etfs': 'code',
        'etf_daily': 'code, trade_date',
        'etf_net_value': 'code, net_value_date',
        'trading_calendar': 'trade_date',
        'market_value': 'code, trade_date',
        'shareholder': 'code, shareholder_name, report_date',
        'financial': 'code, report_date, report_type',
    }
    
    @staticmethod
    def convert_mysql_to_postgresql(sql: str) -> str:
        """
        将 MySQL 语法转换为 PostgreSQL 语法
        
        Args:
            sql: MySQL SQL 语句
            
        Returns:
            PostgreSQL SQL 语句
        """
        # 转换 ON DUPLICATE KEY UPDATE 为 ON CONFLICT ... DO UPDATE
        # MySQL: INSERT ... ON DUPLICATE KEY UPDATE ...
        # PostgreSQL: INSERT ... ON CONFLICT (key) DO UPDATE ...
        
        # 匹配 ON DUPLICATE KEY UPDATE 模式
        pattern = r'ON DUPLICATE KEY UPDATE\s+(.+)'
        match = re.search(pattern, sql, re.IGNORECASE | re.DOTALL)
        
        if match:
            # 提取 INSERT 语句的表名和列
            insert_match = re.search(r'INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)', sql, re.IGNORECASE)
            if insert_match:
                table_name = insert_match.group(1).lower()
                columns = [col.strip() for col in insert_match.group(2).split(',')]
                
                # 查找主键或唯一键
                conflict_key = SQLAdapter.TABLE_PRIMARY_KEYS.get(table_name)
                if not conflict_key:
                    # 如果没有预定义，尝试从列中推断
                    if 'code' in columns:
                        conflict_key = 'code'
                    elif 'id' in columns:
                        conflict_key = 'id'
                    else:
                        conflict_key = columns[0] if columns else 'id'
                
                # 提取 UPDATE 部分
                update_clause = match.group(1).strip()
                
                # 转换 VALUES(column) 为 EXCLUDED.column
                # 处理 VALUES(name), VALUES(market) 等
                def replace_values(m):
                    column_name = m.group(1)
                    return f'EXCLUDED.{column_name}'
                
                update_clause = re.sub(
                    r'VALUES\((\w+)\)',
                    replace_values,
                    update_clause,
                    flags=re.IGNORECASE
                )
                
                # 构建 PostgreSQL 的 ON CONFLICT 语句
                postgresql_sql = re.sub(
                    pattern,
                    f'ON CONFLICT ({conflict_key}) DO UPDATE SET {update_clause}',
                    sql,
                    flags=re.IGNORECASE | re.DOTALL
                )
                
                return postgresql_sql
        
        return sql
