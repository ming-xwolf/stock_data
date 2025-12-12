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
    
    # 资产负债表
    INSERT_BALANCE_SQL = """
        INSERT INTO stock_financial_balance (
            code, report_date, report_period, report_type,
            total_assets, total_liabilities, total_equity,
            current_assets, non_current_assets,
            current_liabilities, non_current_liabilities
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            report_period = VALUES(report_period),
            report_type = VALUES(report_type),
            total_assets = VALUES(total_assets),
            total_liabilities = VALUES(total_liabilities),
            total_equity = VALUES(total_equity),
            current_assets = VALUES(current_assets),
            non_current_assets = VALUES(non_current_assets),
            current_liabilities = VALUES(current_liabilities),
            non_current_liabilities = VALUES(non_current_liabilities),
            updated_at = CURRENT_TIMESTAMP
    """
    
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
    
    # 现金流量表
    INSERT_CASHFLOW_SQL = """
        INSERT INTO stock_financial_cashflow (
            code, report_date, report_period, report_type,
            operating_cashflow, investing_cashflow,
            financing_cashflow, net_cashflow, ending_cash_balance
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            report_period = VALUES(report_period),
            report_type = VALUES(report_type),
            operating_cashflow = VALUES(operating_cashflow),
            investing_cashflow = VALUES(investing_cashflow),
            financing_cashflow = VALUES(financing_cashflow),
            net_cashflow = VALUES(net_cashflow),
            ending_cash_balance = VALUES(ending_cash_balance),
            updated_at = CURRENT_TIMESTAMP
    """
    
    # 财务指标表
    INSERT_INDICATORS_SQL = """
        INSERT INTO stock_financial_indicators (
            code, report_date, report_period, report_type,
            roe, roa, gross_profit_rate, net_profit_rate,
            asset_liability_ratio, current_ratio, quick_ratio,
            eps, bps, pe_ratio, pb_ratio
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            report_period = VALUES(report_period),
            report_type = VALUES(report_type),
            roe = VALUES(roe),
            roa = VALUES(roa),
            gross_profit_rate = VALUES(gross_profit_rate),
            net_profit_rate = VALUES(net_profit_rate),
            asset_liability_ratio = VALUES(asset_liability_ratio),
            current_ratio = VALUES(current_ratio),
            quick_ratio = VALUES(quick_ratio),
            eps = VALUES(eps),
            bps = VALUES(bps),
            pe_ratio = VALUES(pe_ratio),
            pb_ratio = VALUES(pb_ratio),
            updated_at = CURRENT_TIMESTAMP
    """
    
    def insert_balance_sheet(self, code: str, report_date: str,
                            report_period: Optional[str] = None,
                            report_type: Optional[str] = None,
                            total_assets: Optional[float] = None,
                            total_liabilities: Optional[float] = None,
                            total_equity: Optional[float] = None,
                            current_assets: Optional[float] = None,
                            non_current_assets: Optional[float] = None,
                            current_liabilities: Optional[float] = None,
                            non_current_liabilities: Optional[float] = None) -> bool:
        """插入资产负债表数据"""
        try:
            affected_rows = db_manager.execute_update(
                self.INSERT_BALANCE_SQL,
                (code, report_date, report_period, report_type,
                 total_assets, total_liabilities, total_equity,
                 current_assets, non_current_assets,
                 current_liabilities, non_current_liabilities)
            )
            logger.debug(f"插入资产负债表 {code}-{report_date}: {affected_rows} 行受影响")
            return True
        except Exception as e:
            logger.error(f"插入资产负债表失败: {e}")
            return False
    
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
    
    def insert_cashflow_statement(self, code: str, report_date: str,
                                 report_period: Optional[str] = None,
                                 report_type: Optional[str] = None,
                                 operating_cashflow: Optional[float] = None,
                                 investing_cashflow: Optional[float] = None,
                                 financing_cashflow: Optional[float] = None,
                                 net_cashflow: Optional[float] = None,
                                 ending_cash_balance: Optional[float] = None) -> bool:
        """插入现金流量表数据"""
        try:
            affected_rows = db_manager.execute_update(
                self.INSERT_CASHFLOW_SQL,
                (code, report_date, report_period, report_type,
                 operating_cashflow, investing_cashflow,
                 financing_cashflow, net_cashflow, ending_cash_balance)
            )
            logger.debug(f"插入现金流量表 {code}-{report_date}: {affected_rows} 行受影响")
            return True
        except Exception as e:
            logger.error(f"插入现金流量表失败: {e}")
            return False
    
    def insert_indicators(self, code: str, report_date: str,
                         report_period: Optional[str] = None,
                         report_type: Optional[str] = None,
                         roe: Optional[float] = None,
                         roa: Optional[float] = None,
                         gross_profit_rate: Optional[float] = None,
                         net_profit_rate: Optional[float] = None,
                         asset_liability_ratio: Optional[float] = None,
                         current_ratio: Optional[float] = None,
                         quick_ratio: Optional[float] = None,
                         eps: Optional[float] = None,
                         bps: Optional[float] = None,
                         pe_ratio: Optional[float] = None,
                         pb_ratio: Optional[float] = None) -> bool:
        """插入财务指标数据"""
        try:
            affected_rows = db_manager.execute_update(
                self.INSERT_INDICATORS_SQL,
                (code, report_date, report_period, report_type,
                 roe, roa, gross_profit_rate, net_profit_rate,
                 asset_liability_ratio, current_ratio, quick_ratio,
                 eps, bps, pe_ratio, pb_ratio)
            )
            logger.debug(f"插入财务指标 {code}-{report_date}: {affected_rows} 行受影响")
            return True
        except Exception as e:
            logger.error(f"插入财务指标失败: {e}")
            return False

