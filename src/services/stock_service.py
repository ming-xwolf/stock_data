"""
股票数据服务模块

提供股票数据的存储和查询功能。
"""
import logging
from typing import List, Dict, Optional

from ..core.db import db_manager
from .sql_queries import sql_manager
from .sql_queries import stock_sql

logger = logging.getLogger(__name__)


class StockService:
    """股票数据服务类"""
    
    def __init__(self):
        """初始化服务，加载 SQL 语句"""
        self.INSERT_STOCK_SQL = sql_manager.get_sql(stock_sql, 'INSERT_STOCK')
        self.UPDATE_COMPANY_INFO_SQL = sql_manager.get_sql(stock_sql, 'UPDATE_COMPANY_INFO')
        self.SELECT_STOCK_SQL = sql_manager.get_sql(stock_sql, 'SELECT_STOCK')
        self.SELECT_ALL_STOCKS_SQL = sql_manager.get_sql(stock_sql, 'SELECT_ALL_STOCKS')
        self.COUNT_STOCKS_SQL = sql_manager.get_sql(stock_sql, 'COUNT_STOCKS')
    
    def insert_stock(self, code: str, name: str, market: str, 
                     list_date: Optional[str] = None) -> bool:
        """
        插入或更新单只股票信息
        
        Args:
            code: 股票代码
            name: 股票名称
            market: 市场代码（SH/SZ）
            list_date: 上市日期（YYYY-MM-DD格式）
            
        Returns:
            是否成功
        """
        try:
            affected_rows = db_manager.execute_update(
                self.INSERT_STOCK_SQL,
                (code, name, market, list_date)
            )
            logger.debug(f"插入/更新股票 {code} ({name}): {affected_rows} 行受影响")
            return True
        except Exception as e:
            logger.error(f"插入股票 {code} 失败: {e}")
            return False
    
    def batch_insert_stocks(self, stocks: List[Dict[str, any]]) -> int:
        """
        批量插入或更新股票信息
        
        Args:
            stocks: 股票列表，每个元素包含 code, name, market, list_date
            
        Returns:
            成功插入/更新的股票数量
        """
        if not stocks:
            return 0
        
        try:
            # 准备参数列表
            params_list = [
                (
                    stock['code'],
                    stock['name'],
                    stock['market'],
                    stock.get('list_date')
                )
                for stock in stocks
            ]
            
            affected_rows = db_manager.execute_many(
                self.INSERT_STOCK_SQL,
                params_list
            )
            
            logger.info(f"批量插入/更新股票: {affected_rows} 行受影响")
            return affected_rows
            
        except Exception as e:
            logger.error(f"批量插入股票失败: {e}", exc_info=True)
            raise
    
    def get_stock(self, code: str) -> Optional[Dict[str, any]]:
        """
        根据股票代码查询股票信息
        
        Args:
            code: 股票代码
            
        Returns:
            股票信息字典，如果不存在返回None
        """
        try:
            results = db_manager.execute_query(self.SELECT_STOCK_SQL, (code,))
            if results:
                return results[0]
            return None
        except Exception as e:
            logger.error(f"查询股票 {code} 失败: {e}")
            return None
    
    def get_all_stocks(self) -> List[Dict[str, any]]:
        """
        获取所有股票信息
        
        Returns:
            股票信息列表
        """
        try:
            return db_manager.execute_query(self.SELECT_ALL_STOCKS_SQL)
        except Exception as e:
            logger.error(f"查询所有股票失败: {e}")
            return []
    
    def count_stocks(self) -> int:
        """
        统计股票数量
        
        Returns:
            股票数量
        """
        try:
            results = db_manager.execute_query(self.COUNT_STOCKS_SQL)
            if results:
                return results[0]['count']
            return 0
        except Exception as e:
            logger.error(f"统计股票数量失败: {e}")
            return 0
    
    def update_company_info(self, code: str, company_type: Optional[str] = None,
                           actual_controller: Optional[str] = None,
                           direct_controller: Optional[str] = None,
                           main_business: Optional[str] = None) -> bool:
        """
        更新股票的公司信息（企业性质、实际控制人、直接控制人、主营产品）
        
        Args:
            code: 股票代码
            company_type: 企业性质（如：央企国资控股、民企、外资等）
            actual_controller: 实际控制人
            direct_controller: 直接控制人
            main_business: 主营产品/主营业务
            
        Returns:
            是否成功
        """
        try:
            affected_rows = db_manager.execute_update(
                self.UPDATE_COMPANY_INFO_SQL,
                (company_type, actual_controller, direct_controller, main_business, code)
            )
            logger.debug(f"更新股票 {code} 公司信息: {affected_rows} 行受影响")
            return True
        except Exception as e:
            logger.error(f"更新股票 {code} 公司信息失败: {e}")
            return False

