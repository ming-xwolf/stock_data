"""
ETF 净值数据服务模块

提供 ETF 净值数据的存储和查询功能。
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime

from ..core.db import db_manager

logger = logging.getLogger(__name__)


class ETFNetValueService:
    """ETF 净值数据服务类"""
    
    INSERT_NET_VALUE_SQL = """
        INSERT INTO etf_net_value (code, net_value_date, unit_net_value, accumulated_net_value,
                                   daily_growth_rate, subscription_status, redemption_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            unit_net_value = VALUES(unit_net_value),
            accumulated_net_value = VALUES(accumulated_net_value),
            daily_growth_rate = VALUES(daily_growth_rate),
            subscription_status = VALUES(subscription_status),
            redemption_status = VALUES(redemption_status),
            updated_at = CURRENT_TIMESTAMP
    """
    
    SELECT_LATEST_DATE_SQL = """
        SELECT MAX(net_value_date) as latest_date 
        FROM etf_net_value 
        WHERE code = %s
    """
    
    SELECT_NET_VALUE_SQL = """
        SELECT * FROM etf_net_value 
        WHERE code = %s AND net_value_date >= %s AND net_value_date <= %s
        ORDER BY net_value_date
    """
    
    COUNT_NET_VALUE_SQL = """
        SELECT COUNT(*) as count 
        FROM etf_net_value 
        WHERE code = %s
    """
    
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
