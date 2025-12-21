"""
ETF 净值数据服务模块

提供 ETF 净值数据的存储和查询功能。
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime

from ..core.db import db_manager
from .sql_queries import sql_manager
from .sql_queries import etf_net_value_sql

logger = logging.getLogger(__name__)


class ETFNetValueService:
    """ETF 净值数据服务类"""
    
    def __init__(self):
        """初始化服务，加载 SQL 语句"""
        self.INSERT_NET_VALUE_SQL = sql_manager.get_sql(etf_net_value_sql, 'INSERT_NET_VALUE')
        self.SELECT_LATEST_DATE_SQL = sql_manager.get_sql(etf_net_value_sql, 'SELECT_LATEST_DATE')
        self.SELECT_NET_VALUE_SQL = sql_manager.get_sql(etf_net_value_sql, 'SELECT_NET_VALUE')
        self.COUNT_NET_VALUE_SQL = sql_manager.get_sql(etf_net_value_sql, 'COUNT_NET_VALUE')
        self.SELECT_ETFS_NEED_UPDATE_SQL = sql_manager.get_sql(etf_net_value_sql, 'SELECT_ETFS_NEED_UPDATE')
    
    def insert_net_value(self, data: Dict[str, any]) -> bool:
        """
        插入或更新单条净值数据
        
        Args:
            data: 净值数据字典
            
        Returns:
            是否成功
        """
        try:
            affected_rows = db_manager.execute_update(
                self.INSERT_NET_VALUE_SQL,
                (
                    data['code'],
                    data['net_value_date'],
                    data.get('unit_net_value'),
                    data.get('accumulated_net_value'),
                    data.get('daily_growth_rate'),
                    data.get('subscription_status'),
                    data.get('redemption_status')
                )
            )
            logger.debug(f"插入/更新 ETF {data['code']} 净值数据 {data['net_value_date']}: {affected_rows} 行受影响")
            return True
        except Exception as e:
            logger.error(f"插入净值数据失败: {e}")
            return False
    
    def batch_insert_net_value(self, data_list: List[Dict[str, any]]) -> int:
        """
        批量插入或更新净值数据
        
        Args:
            data_list: 净值数据列表
            
        Returns:
            成功插入/更新的数据条数
        """
        if not data_list:
            return 0
        
        try:
            params_list = [
                (
                    data['code'],
                    data['net_value_date'],
                    data.get('unit_net_value'),
                    data.get('accumulated_net_value'),
                    data.get('daily_growth_rate'),
                    data.get('subscription_status'),
                    data.get('redemption_status')
                )
                for data in data_list
            ]
            
            affected_rows = db_manager.execute_many(
                self.INSERT_NET_VALUE_SQL,
                params_list
            )
            
            logger.info(f"批量插入/更新净值数据: {affected_rows} 行受影响")
            return affected_rows
            
        except Exception as e:
            logger.error(f"批量插入净值数据失败: {e}", exc_info=True)
            raise
    
    def get_latest_date(self, code: str) -> Optional[str]:
        """
        获取指定 ETF 的最新净值日期
        
        Args:
            code: ETF 代码
            
        Returns:
            最新净值日期（YYYY-MM-DD格式），如果没有数据返回 None
        """
        try:
            results = db_manager.execute_query(self.SELECT_LATEST_DATE_SQL, (code,))
            if results and results[0]['latest_date']:
                latest_date = results[0]['latest_date']
                # 转换为字符串格式
                if isinstance(latest_date, datetime):
                    return latest_date.strftime('%Y-%m-%d')
                return str(latest_date)
            return None
        except Exception as e:
            logger.error(f"查询 ETF {code} 最新净值日期失败: {e}")
            return None
    
    def get_net_value(self, code: str, start_date: str, end_date: str) -> List[Dict[str, any]]:
        """
        查询指定日期范围的净值数据
        
        Args:
            code: ETF 代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            净值数据列表
        """
        try:
            return db_manager.execute_query(
                self.SELECT_NET_VALUE_SQL,
                (code, start_date, end_date)
            )
        except Exception as e:
            logger.error(f"查询 ETF {code} 净值数据失败: {e}")
            return []
    
    def count_net_value_records(self, code: str) -> int:
        """
        统计指定 ETF 的净值数据条数
        
        Args:
            code: ETF 代码
            
        Returns:
            数据条数
        """
        try:
            results = db_manager.execute_query(self.COUNT_NET_VALUE_SQL, (code,))
            if results:
                return results[0]['count']
            return 0
        except Exception as e:
            logger.error(f"统计 ETF {code} 净值数据失败: {e}")
            return 0
    
    def get_etfs_need_update(self) -> List[Dict[str, any]]:
        """
        获取需要更新的 ETF 列表（缺少最新交易日净值数据的 ETF）
        
        该方法会：
        1. 查询交易日历的最新交易日（只考虑今天或今天以前）
        2. 结合 etf_funds 表，找出 etf_net_value 中缺少最新交易日净值数据的 ETF
        3. 返回需要更新的 ETF 列表，包含建议的起始日期
        
        Returns:
            需要更新的 ETF 列表，每个元素包含：
            - code: ETF 代码
            - name: ETF 名称
            - latest_net_value_date: 该 ETF 在数据库中的最新净值日期
            - latest_trading_date: 交易日历中的最新交易日
            - start_date: 建议的更新起始日期（从该 ETF 最新净值日期的下一天开始）
        """
        try:
            results = db_manager.execute_query(self.SELECT_ETFS_NEED_UPDATE_SQL)
            
            # 转换日期格式
            etfs_need_update = []
            for row in results:
                etf_info = {
                    'code': row['code'],
                    'name': row.get('name', ''),
                    'latest_net_value_date': None,
                    'latest_trading_date': None,
                    'start_date': None
                }
                
                # 转换 latest_net_value_date
                if row.get('latest_net_value_date'):
                    latest_net_value = row['latest_net_value_date']
                    if isinstance(latest_net_value, datetime):
                        etf_info['latest_net_value_date'] = latest_net_value.strftime('%Y-%m-%d')
                    else:
                        etf_info['latest_net_value_date'] = str(latest_net_value)
                
                # 转换 latest_trading_date
                if row.get('latest_trading_date'):
                    latest_trading = row['latest_trading_date']
                    if isinstance(latest_trading, datetime):
                        etf_info['latest_trading_date'] = latest_trading.strftime('%Y-%m-%d')
                    else:
                        etf_info['latest_trading_date'] = str(latest_trading)
                
                # 转换 start_date
                if row.get('start_date'):
                    start = row['start_date']
                    if isinstance(start, datetime):
                        etf_info['start_date'] = start.strftime('%Y-%m-%d')
                    else:
                        etf_info['start_date'] = str(start)
                
                etfs_need_update.append(etf_info)
            
            return etfs_need_update
            
        except Exception as e:
            logger.error(f"查询需要更新的 ETF 列表失败: {e}", exc_info=True)
            return []
