"""
股东数据服务模块

提供股票股东信息的存储和查询功能。
"""
import logging
from typing import List, Dict, Optional

from ..core.db import db_manager
from .sql_queries import sql_manager
from .sql_queries import shareholder_sql

logger = logging.getLogger(__name__)


class ShareholderService:
    """股东数据服务类"""
    
    def __init__(self):
        """初始化服务，加载 SQL 语句"""
        self.INSERT_SHAREHOLDER_SQL = sql_manager.get_sql(shareholder_sql, 'INSERT_SHAREHOLDER')
        self.SELECT_SHAREHOLDERS_SQL = sql_manager.get_sql(shareholder_sql, 'SELECT_SHAREHOLDERS')
        self.SELECT_LATEST_SHAREHOLDERS_SQL = sql_manager.get_sql(shareholder_sql, 'SELECT_LATEST_SHAREHOLDERS')
    
    def insert_shareholder(self, code: str, shareholder_name: str,
                          shareholder_type: Optional[str] = None,
                          holding_ratio: Optional[float] = None,
                          holding_amount: Optional[int] = None,
                          change_amount: Optional[int] = None,
                          change_ratio: Optional[float] = None,
                          report_date: Optional[str] = None,
                          report_period: Optional[str] = None) -> bool:
        """
        插入或更新股东信息
        
        Args:
            code: 股票代码
            shareholder_name: 股东名称
            shareholder_type: 股东类型
            holding_ratio: 持股比例（%）
            holding_amount: 持股数量（股）
            change_amount: 持股变化（股）
            change_ratio: 持股变化比例（%）
            report_date: 报告日期（YYYY-MM-DD格式）
            report_period: 报告期（如：2024Q1）
            
        Returns:
            是否成功
        """
        try:
            affected_rows = db_manager.execute_update(
                self.INSERT_SHAREHOLDER_SQL,
                (code, shareholder_name, shareholder_type, holding_ratio, holding_amount,
                 change_amount, change_ratio, report_date, report_period)
            )
            logger.debug(f"插入/更新股东信息 {code}-{shareholder_name}: {affected_rows} 行受影响")
            return True
        except Exception as e:
            logger.error(f"插入股东信息失败: {e}")
            return False
    
    def batch_insert_shareholders(self, shareholders: List[Dict[str, any]]) -> int:
        """
        批量插入股东信息
        
        Args:
            shareholders: 股东信息列表
            
        Returns:
            成功插入的数量
        """
        if not shareholders:
            return 0
        
        try:
            params_list = [
                (
                    sh['code'],
                    sh['shareholder_name'],
                    sh.get('shareholder_type'),
                    sh.get('holding_ratio'),
                    sh.get('holding_amount'),
                    sh.get('change_amount'),
                    sh.get('change_ratio'),
                    sh.get('report_date'),
                    sh.get('report_period')
                )
                for sh in shareholders
            ]
            
            affected_rows = db_manager.execute_many(
                self.INSERT_SHAREHOLDER_SQL,
                params_list
            )
            
            # 注意：affected_rows 对于 ON DUPLICATE KEY UPDATE：
            # - 新插入的行计为 1
            # - 更新的行计为 2（MySQL行为：1行匹配 + 1行更新）
            # - 无变化的行计为 0
            # 所以实际插入/更新的行数可能小于 affected_rows
            logger.debug(f"批量插入/更新股东信息: {affected_rows} 行受影响（包含新插入和更新）")
            return affected_rows
            
        except Exception as e:
            logger.error(f"批量插入股东信息失败: {e}", exc_info=True)
            raise
    
    def get_shareholders(self, code: str, report_date: Optional[str] = None) -> List[Dict[str, any]]:
        """
        查询股东信息
        
        Args:
            code: 股票代码
            report_date: 报告日期，如果为None则返回最新报告期的数据
            
        Returns:
            股东信息列表
        """
        try:
            if report_date:
                return db_manager.execute_query(
                    self.SELECT_SHAREHOLDERS_SQL,
                    (code, report_date)
                )
            else:
                return db_manager.execute_query(
                    self.SELECT_LATEST_SHAREHOLDERS_SQL,
                    (code, code)
                )
        except Exception as e:
            logger.error(f"查询股东信息失败: {e}")
            return []

