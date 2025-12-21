"""
ETF 基金数据服务模块

提供 ETF 基金数据的存储和查询功能。
"""
import logging
from typing import List, Dict, Optional

from ..core.db import db_manager
from .sql_queries import sql_manager
from .sql_queries import etf_sql

logger = logging.getLogger(__name__)


class ETFService:
    """ETF 基金数据服务类"""
    
    def __init__(self):
        """初始化服务，加载 SQL 语句"""
        self.INSERT_ETF_SQL = sql_manager.get_sql(etf_sql, 'INSERT_ETF')
        self.SELECT_ETF_SQL = sql_manager.get_sql(etf_sql, 'SELECT_ETF')
        self.SELECT_ALL_ETFS_SQL = sql_manager.get_sql(etf_sql, 'SELECT_ALL_ETFS')
        self.COUNT_ETFS_SQL = sql_manager.get_sql(etf_sql, 'COUNT_ETFS')
    
    def insert_etf(self, code: str, name: str, exchange: str,
                   fund_type: Optional[str] = None,
                   fund_company: Optional[str] = None,
                   listing_date: Optional[str] = None,
                   tracking_index: Optional[str] = None,
                   management_fee: Optional[float] = None,
                   custodian_fee: Optional[float] = None) -> bool:
        """
        插入或更新单只 ETF 基金信息
        
        Args:
            code: ETF 代码
            name: ETF 名称
            exchange: 交易所（SH/SZ）
            fund_type: 基金类型
            fund_company: 基金公司
            listing_date: 上市日期（YYYY-MM-DD格式）
            tracking_index: 跟踪指数
            management_fee: 管理费率
            custodian_fee: 托管费率
            
        Returns:
            是否成功
        """
        try:
            affected_rows = db_manager.execute_update(
                self.INSERT_ETF_SQL,
                (code, name, fund_type, fund_company, listing_date,
                 tracking_index, management_fee, custodian_fee, exchange)
            )
            logger.debug(f"插入/更新 ETF {code} ({name}): {affected_rows} 行受影响")
            return True
        except Exception as e:
            logger.error(f"插入 ETF {code} 失败: {e}")
            return False
    
    def batch_insert_etfs(self, etfs: List[Dict[str, any]]) -> int:
        """
        批量插入或更新 ETF 基金信息
        
        Args:
            etfs: ETF 列表，每个元素包含 code, name, exchange 等字段
            
        Returns:
            成功插入/更新的 ETF 数量
        """
        if not etfs:
            return 0
        
        try:
            # 准备参数列表
            params_list = [
                (
                    etf['code'],
                    etf['name'],
                    etf.get('fund_type'),
                    etf.get('fund_company'),
                    etf.get('listing_date'),
                    etf.get('tracking_index'),
                    etf.get('management_fee'),
                    etf.get('custodian_fee'),
                    etf.get('exchange')
                )
                for etf in etfs
            ]
            
            affected_rows = db_manager.execute_many(
                self.INSERT_ETF_SQL,
                params_list
            )
            
            logger.info(f"批量插入/更新 ETF: {affected_rows} 行受影响")
            return affected_rows
            
        except Exception as e:
            logger.error(f"批量插入 ETF 失败: {e}", exc_info=True)
            raise
    
    def get_etf(self, code: str) -> Optional[Dict[str, any]]:
        """
        根据代码查询 ETF 信息
        
        Args:
            code: ETF 代码
            
        Returns:
            ETF 信息字典，如果不存在返回 None
        """
        try:
            results = db_manager.execute_query(self.SELECT_ETF_SQL, (code,))
            if results:
                return results[0]
            return None
        except Exception as e:
            logger.error(f"查询 ETF {code} 失败: {e}")
            return None
    
    def get_all_etfs(self) -> List[Dict[str, any]]:
        """
        获取所有 ETF 信息
        
        Returns:
            ETF 信息列表
        """
        try:
            return db_manager.execute_query(self.SELECT_ALL_ETFS_SQL)
        except Exception as e:
            logger.error(f"查询所有 ETF 失败: {e}")
            return []
    
    def count_etfs(self) -> int:
        """
        统计 ETF 数量
        
        Returns:
            ETF 数量
        """
        try:
            results = db_manager.execute_query(self.COUNT_ETFS_SQL)
            if results:
                return results[0]['count']
            return 0
        except Exception as e:
            logger.error(f"统计 ETF 数量失败: {e}")
            return 0
