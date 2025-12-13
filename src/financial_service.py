"""
财务数据服务模块

提供股票财务数据的存储和查询功能。
"""
import logging
from typing import List, Dict, Optional

from .db import db_manager

logger = logging.getLogger(__name__)


class FinancialService:
    """财务数据服务类"""
    
    # 利润表
    INSERT_INCOME_SQL = """
        INSERT INTO stock_financial_income (
            code, report_date, report_period, report_type,
            total_revenue, operating_revenue, operating_cost,
            operating_profit, total_profit, net_profit,
            net_profit_attributable, basic_eps, diluted_eps
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            report_period = VALUES(report_period),
            report_type = VALUES(report_type),
            total_revenue = VALUES(total_revenue),
            operating_revenue = VALUES(operating_revenue),
            operating_cost = VALUES(operating_cost),
            operating_profit = VALUES(operating_profit),
            total_profit = VALUES(total_profit),
            net_profit = VALUES(net_profit),
            net_profit_attributable = VALUES(net_profit_attributable),
            basic_eps = VALUES(basic_eps),
            diluted_eps = VALUES(diluted_eps),
            updated_at = CURRENT_TIMESTAMP
    """
    
    def insert_income_statement(self, code: str, report_date: str,
                               report_period: Optional[str] = None,
                               report_type: Optional[str] = None,
                               total_revenue: Optional[float] = None,
                               operating_revenue: Optional[float] = None,
                               operating_cost: Optional[float] = None,
                               operating_profit: Optional[float] = None,
                               total_profit: Optional[float] = None,
                               net_profit: Optional[float] = None,
                               net_profit_attributable: Optional[float] = None,
                               basic_eps: Optional[float] = None,
                               diluted_eps: Optional[float] = None) -> bool:
        """插入利润表数据"""
        try:
            affected_rows = db_manager.execute_update(
                self.INSERT_INCOME_SQL,
                (code, report_date, report_period, report_type,
                 total_revenue, operating_revenue, operating_cost,
                 operating_profit, total_profit, net_profit,
                 net_profit_attributable, basic_eps, diluted_eps)
            )
            logger.debug(f"插入利润表 {code}-{report_date}: {affected_rows} 行受影响")
            return True
        except Exception as e:
            logger.error(f"插入利润表失败: {e}")
            return False

