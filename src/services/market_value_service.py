"""
市值数据服务模块

提供股票市值信息的存储和查询功能。
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime

from ..core.db import db_manager
from .sql_queries import sql_manager
from .sql_queries import market_value_sql

logger = logging.getLogger(__name__)


class MarketValueService:
    """市值数据服务类"""
    
    def __init__(self):
        """初始化服务，加载 SQL 语句"""
        self.INSERT_MARKET_VALUE_SQL = sql_manager.get_sql(market_value_sql, 'INSERT_MARKET_VALUE')
        self.SELECT_MARKET_VALUE_SQL = sql_manager.get_sql(market_value_sql, 'SELECT_MARKET_VALUE')
    
    def insert_market_value(self, code: str, total_shares: Optional[int] = None,
                           circulating_shares: Optional[int] = None,
                           total_market_cap: Optional[float] = None,
                           circulating_market_cap: Optional[float] = None,
                           price: Optional[float] = None,
                           update_date: Optional[str] = None) -> bool:
        """
        插入或更新市值信息
        
        Args:
            code: 股票代码
            total_shares: 总股本（股）
            circulating_shares: 流通股本（股）
            total_market_cap: 总市值（元）
            circulating_market_cap: 流通市值（元）
            price: 当前价格（元）
            update_date: 更新日期（YYYY-MM-DD格式），如果为None则使用今天
            
        Returns:
            是否成功
        """
        if update_date is None:
            update_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            affected_rows = db_manager.execute_update(
                self.INSERT_MARKET_VALUE_SQL,
                (code, total_shares, circulating_shares, total_market_cap,
                 circulating_market_cap, price, update_date)
            )
            logger.debug(f"插入/更新股票 {code} 市值信息: {affected_rows} 行受影响")
            return True
        except Exception as e:
            logger.error(f"插入股票 {code} 市值信息失败: {e}")
            return False
    
    def batch_insert_market_values(self, market_values: List[Dict[str, any]]) -> int:
        """
        批量插入市值信息
        
        Args:
            market_values: 市值信息列表
            
        Returns:
            成功插入的数量
        """
        if not market_values:
            return 0
        
        try:
            params_list = []
            for mv in market_values:
                update_date = mv.get('update_date')
                if update_date is None:
                    update_date = datetime.now().strftime('%Y-%m-%d')
                
                params_list.append((
                    mv['code'],
                    mv.get('total_shares'),
                    mv.get('circulating_shares'),
                    mv.get('total_market_cap'),
                    mv.get('circulating_market_cap'),
                    mv.get('price'),
                    update_date
                ))
            
            affected_rows = db_manager.execute_many(
                self.INSERT_MARKET_VALUE_SQL,
                params_list
            )
            
            logger.info(f"批量插入市值信息: {affected_rows} 行受影响")
            return affected_rows
            
        except Exception as e:
            logger.error(f"批量插入市值信息失败: {e}", exc_info=True)
            raise
    
    def get_market_value(self, code: str) -> Optional[Dict[str, any]]:
        """
        查询最新市值信息
        
        Args:
            code: 股票代码
            
        Returns:
            市值信息字典，如果不存在返回None
        """
        try:
            results = db_manager.execute_query(self.SELECT_MARKET_VALUE_SQL, (code,))
            if results:
                return results[0]
            return None
        except Exception as e:
            logger.error(f"查询股票 {code} 市值信息失败: {e}")
            return None

