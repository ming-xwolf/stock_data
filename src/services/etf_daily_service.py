"""
ETF 日线行情数据服务模块

提供 ETF 日线行情数据的存储和查询功能。
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime

from ..core.db import db_manager

logger = logging.getLogger(__name__)


class ETFDailyService:
    """ETF 日线行情数据服务类"""
    
    INSERT_DAILY_SQL = """
        INSERT INTO etf_daily (code, trade_date, open_price, high_price, low_price, 
                              close_price, volume, amount, change_amount, change_rate, turnover)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            open_price = VALUES(open_price),
            high_price = VALUES(high_price),
            low_price = VALUES(low_price),
            close_price = VALUES(close_price),
            volume = VALUES(volume),
            amount = VALUES(amount),
            change_amount = VALUES(change_amount),
            change_rate = VALUES(change_rate),
            turnover = VALUES(turnover)
    """
    
    SELECT_LATEST_DATE_SQL = """
        SELECT MAX(trade_date) as latest_date 
        FROM etf_daily 
        WHERE code = %s
    """
    
    SELECT_DAILY_DATA_SQL = """
        SELECT * FROM etf_daily 
        WHERE code = %s AND trade_date >= %s AND trade_date <= %s
        ORDER BY trade_date
    """
    
    COUNT_DAILY_SQL = """
        SELECT COUNT(*) as count 
        FROM etf_daily 
        WHERE code = %s
    """
    
    def insert_daily_data(self, data: Dict[str, any]) -> bool:
        """
        插入或更新单条日线数据
        
        Args:
            data: 日线数据字典
            
        Returns:
            是否成功
        """
        try:
            affected_rows = db_manager.execute_update(
                self.INSERT_DAILY_SQL,
                (
                    data['code'],
                    data['trade_date'],
                    data.get('open_price'),
                    data.get('high_price'),
                    data.get('low_price'),
                    data.get('close_price'),
                    data.get('volume'),
                    data.get('amount'),
                    data.get('change_amount'),
                    data.get('change_rate'),
                    data.get('turnover')
                )
            )
            logger.debug(f"插入/更新 ETF {data['code']} 日线数据 {data['trade_date']}: {affected_rows} 行受影响")
            return True
        except Exception as e:
            logger.error(f"插入日线数据失败: {e}")
            return False
    
    def batch_insert_daily_data(self, data_list: List[Dict[str, any]]) -> int:
        """
        批量插入或更新日线数据
        
        Args:
            data_list: 日线数据列表
            
        Returns:
            成功插入/更新的数据条数
        """
        if not data_list:
            return 0
        
        try:
            params_list = [
                (
                    data['code'],
                    data['trade_date'],
                    data.get('open_price'),
                    data.get('high_price'),
                    data.get('low_price'),
                    data.get('close_price'),
                    data.get('volume'),
                    data.get('amount'),
                    data.get('change_amount'),
                    data.get('change_rate'),
                    data.get('turnover')
                )
                for data in data_list
            ]
            
            affected_rows = db_manager.execute_many(
                self.INSERT_DAILY_SQL,
                params_list
            )
            
            logger.info(f"批量插入/更新日线数据: {affected_rows} 行受影响")
            return affected_rows
            
        except Exception as e:
            logger.error(f"批量插入日线数据失败: {e}", exc_info=True)
            raise
    
    def get_latest_date(self, code: str) -> Optional[str]:
        """
        获取指定 ETF 的最新交易日期
        
        Args:
            code: ETF 代码
            
        Returns:
            最新交易日期（YYYY-MM-DD格式），如果没有数据返回 None
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
            logger.error(f"查询 ETF {code} 最新日期失败: {e}")
            return None
    
    def get_daily_data(self, code: str, start_date: str, end_date: str) -> List[Dict[str, any]]:
        """
        查询指定日期范围的日线数据
        
        Args:
            code: ETF 代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            日线数据列表
        """
        try:
            return db_manager.execute_query(
                self.SELECT_DAILY_DATA_SQL,
                (code, start_date, end_date)
            )
        except Exception as e:
            logger.error(f"查询 ETF {code} 日线数据失败: {e}")
            return []
    
    def count_daily_records(self, code: str) -> int:
        """
        统计指定 ETF 的日线数据条数
        
        Args:
            code: ETF 代码
            
        Returns:
            数据条数
        """
        try:
            results = db_manager.execute_query(self.COUNT_DAILY_SQL, (code,))
            if results:
                return results[0]['count']
            return 0
        except Exception as e:
            logger.error(f"统计 ETF {code} 日线数据失败: {e}")
            return 0
