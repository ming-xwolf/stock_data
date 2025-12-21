"""
数据获取服务模块

提供从数据库获取股票数据的功能，主要用于图表绘制。
"""
import logging
from typing import Optional
import pandas as pd

from ..core.db import db_manager
from .sql_queries import sql_manager
from .sql_queries import fetch_data_sql

logger = logging.getLogger(__name__)


class FetchDataService:
    """数据获取服务类"""
    
    def __init__(self):
        """初始化服务，加载 SQL 语句"""
        self.SELECT_STOCK_DAILY_DATA = sql_manager.get_sql(fetch_data_sql, 'SELECT_STOCK_DAILY_DATA')
        self.SELECT_STOCK_NAME = sql_manager.get_sql(fetch_data_sql, 'SELECT_STOCK_NAME')
        self.SELECT_EARLIEST_TRADE_DATE_BY_CODE = sql_manager.get_sql(fetch_data_sql, 'SELECT_EARLIEST_TRADE_DATE_BY_CODE')
        self.SELECT_EARLIEST_TRADE_DATE = sql_manager.get_sql(fetch_data_sql, 'SELECT_EARLIEST_TRADE_DATE')
        self.SELECT_LATEST_TRADE_DATE_BY_CODE = sql_manager.get_sql(fetch_data_sql, 'SELECT_LATEST_TRADE_DATE_BY_CODE')
        self.SELECT_LATEST_TRADE_DATE = sql_manager.get_sql(fetch_data_sql, 'SELECT_LATEST_TRADE_DATE')
    
    def fetch_stock_data_from_supabase(
        self, stock_code: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        从Supabase获取股票数据

        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            DataFrame: 包含OHLCV数据的DataFrame，索引为DatetimeIndex

        Raises:
            ValueError: 如果数据获取失败
        """
        try:
            # 执行查询
            results = db_manager.execute_query(
                self.SELECT_STOCK_DAILY_DATA, 
                (stock_code, start_date, end_date)
            )
            
            if not results:
                raise ValueError(
                    f"未获取到 {stock_code} 的数据（日期范围: {start_date} 至 {end_date}）"
                )
            
            # 转换为DataFrame
            df = pd.DataFrame(results)
            
            # 转换日期列为datetime类型并设置为索引
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df = df.set_index('trade_date')
            df.index.name = None
            
            # 确保数据类型正确
            for col in ["open", "high", "low", "close", "volume"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            
            # 删除无效数据
            df = df.dropna()
            
            # 添加openinterest列（mplfinance需要）
            df["openinterest"] = 0
            
            # 只保留需要的列
            df = df[["open", "high", "low", "close", "volume", "openinterest"]].copy()
            
            logger.debug(f"从Supabase获取数据成功，日期范围: {df.index[0]} 到 {df.index[-1]}")
            return df
            
        except Exception as e:
            logger.error(f"从Supabase获取数据失败: {e}", exc_info=True)
            raise ValueError(f"从Supabase获取数据失败: {e}")
    
    def get_stock_name_from_supabase(self, stock_code: str) -> Optional[str]:
        """
        从Supabase获取股票名称

        Args:
            stock_code: 股票代码

        Returns:
            股票名称，如果不存在则返回None
        """
        try:
            results = db_manager.execute_query(self.SELECT_STOCK_NAME, (stock_code,))
            if results and results[0].get('name'):
                return results[0]['name']
            return None
        except Exception as e:
            logger.error(f"获取股票名称失败: {e}")
            return None
    
    def fetch_stock_data(
        self, stock_code: str, start_date: str, end_date: str, data_source: str = "supabase"
    ) -> pd.DataFrame:
        """
        获取股票数据（支持Supabase数据源）

        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            data_source: 数据源，目前只支持 'supabase'，默认 'supabase'

        Returns:
            DataFrame: 包含OHLCV数据的DataFrame

        Raises:
            ValueError: 如果数据获取失败
        """
        if data_source == "supabase":
            df = self.fetch_stock_data_from_supabase(stock_code, start_date, end_date)
            logger.info(f"从Supabase获取数据成功，日期范围: {df.index[0]} 到 {df.index[-1]}")
            return df
        else:
            raise ValueError(f"不支持的数据源: {data_source}，目前只支持 'supabase'")
    
    def get_earliest_trade_date(self, stock_code: Optional[str] = None) -> Optional[str]:
        """
        获取最早的交易日期
        
        Args:
            stock_code: 股票代码，如果为None则返回全局最早日期
        
        Returns:
            最早交易日期（YYYY-MM-DD格式），如果没有数据返回None
        """
        try:
            from datetime import datetime
            
            if stock_code:
                sql = self.SELECT_EARLIEST_TRADE_DATE_BY_CODE
                params = (stock_code,)
            else:
                sql = self.SELECT_EARLIEST_TRADE_DATE
                params = None
            
            results = db_manager.execute_query(sql, params)
            if results and results[0].get('earliest_date'):
                earliest_date = results[0]['earliest_date']
                if isinstance(earliest_date, datetime):
                    return earliest_date.strftime('%Y-%m-%d')
                elif isinstance(earliest_date, str):
                    return earliest_date
                else:
                    return str(earliest_date)
            return None
        except Exception as e:
            logger.error(f"查询最早交易日期失败: {e}")
            return None
    
    def get_latest_trade_date(self, stock_code: Optional[str] = None) -> Optional[str]:
        """
        获取最新的交易日期
        
        Args:
            stock_code: 股票代码，如果为None则返回全局最新日期
        
        Returns:
            最新交易日期（YYYY-MM-DD格式），如果没有数据返回None
        """
        try:
            from datetime import datetime
            
            if stock_code:
                sql = self.SELECT_LATEST_TRADE_DATE_BY_CODE
                params = (stock_code,)
            else:
                sql = self.SELECT_LATEST_TRADE_DATE
                params = None
            
            results = db_manager.execute_query(sql, params)
            if results and results[0].get('latest_date'):
                latest_date = results[0]['latest_date']
                if isinstance(latest_date, datetime):
                    return latest_date.strftime('%Y-%m-%d')
                elif isinstance(latest_date, str):
                    return latest_date
                else:
                    return str(latest_date)
            return None
        except Exception as e:
            logger.error(f"查询最新交易日期失败: {e}")
            return None


# 创建全局服务实例
fetch_data_service = FetchDataService()
