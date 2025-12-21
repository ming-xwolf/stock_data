"""
交易日历服务模块

使用AKShare API获取A股交易日历并存储到数据库。
"""
import logging
from datetime import datetime
from typing import List, Optional
import pandas as pd

import akshare as ak
from ..core.db import db_manager
from .sql_queries import sql_manager
from .sql_queries import trading_calendar_sql

logger = logging.getLogger(__name__)


class TradingCalendarService:
    """交易日历服务类"""
    
    def __init__(self):
        """初始化交易日历服务，加载 SQL 语句"""
        self.INSERT_TRADING_DATE_SQL = sql_manager.get_sql(trading_calendar_sql, 'INSERT_TRADING_DATE')
        self.SELECT_LATEST_DATE_SQL = sql_manager.get_sql(trading_calendar_sql, 'SELECT_LATEST_DATE')
        self.SELECT_TRADING_DATE_SQL = sql_manager.get_sql(trading_calendar_sql, 'SELECT_TRADING_DATE')
    
    def fetch_trading_calendar(self) -> Optional[pd.DataFrame]:
        """
        从AKShare获取A股交易日历
        
        Returns:
            交易日历DataFrame，包含trade_date列
        """
        try:
            logger.info("开始从AKShare获取A股交易日历...")
            df = ak.tool_trade_date_hist_sina()
            
            if df is None or df.empty:
                logger.warning("未获取到交易日历数据")
                return None
            
            logger.info(f"成功获取 {len(df)} 条交易日历数据")
            return df
            
        except Exception as e:
            logger.error(f"获取交易日历失败: {e}", exc_info=True)
            return None
    
    def get_latest_trading_date(self) -> Optional[str]:
        """
        获取数据库中最新交易日
        
        Returns:
            最新交易日字符串（YYYY-MM-DD格式），如果不存在则返回None
        """
        try:
            result = db_manager.execute_query(self.SELECT_LATEST_DATE_SQL)
            if result and result[0].get('latest_date'):
                latest_date = result[0]['latest_date']
                if isinstance(latest_date, str):
                    return latest_date
                elif hasattr(latest_date, 'strftime'):
                    return latest_date.strftime('%Y-%m-%d')
                return str(latest_date)
            return None
        except Exception as e:
            logger.error(f"获取最新交易日失败: {e}", exc_info=True)
            return None
    
    def is_trading_date(self, date: str) -> bool:
        """
        检查指定日期是否为交易日
        
        Args:
            date: 日期字符串（YYYY-MM-DD格式）
            
        Returns:
            如果是交易日返回True，否则返回False
        """
        try:
            result = db_manager.execute_query(self.SELECT_TRADING_DATE_SQL, (date,))
            return len(result) > 0
        except Exception as e:
            logger.error(f"检查交易日失败: {e}", exc_info=True)
            return False
    
    def save_trading_calendar(self, df: pd.DataFrame, update_existing: bool = True) -> int:
        """
        保存交易日历到数据库
        
        Args:
            df: 交易日历DataFrame，应包含trade_date列
            update_existing: 是否更新已存在的记录
            
        Returns:
            保存的记录数
        """
        if df is None or df.empty:
            logger.warning("交易日历数据为空，无法保存")
            return 0
        
        try:
            # 准备数据
            records = []
            for _, row in df.iterrows():
                # 提取日期（AKShare返回的列名可能是'trade_date'）
                trade_date = row.get('trade_date', None)
                
                # 处理日期格式
                if trade_date is None:
                    continue
                
                # 转换为字符串格式
                if isinstance(trade_date, str):
                    # 尝试解析日期字符串
                    try:
                        date_obj = datetime.strptime(trade_date, '%Y-%m-%d')
                        trade_date_str = date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        # 尝试其他格式
                        try:
                            date_obj = datetime.strptime(trade_date, '%Y/%m/%d')
                            trade_date_str = date_obj.strftime('%Y-%m-%d')
                        except ValueError:
                            logger.warning(f"无法解析日期格式: {trade_date}")
                            continue
                elif hasattr(trade_date, 'strftime'):
                    # pandas Timestamp或datetime对象
                    trade_date_str = trade_date.strftime('%Y-%m-%d')
                else:
                    logger.warning(f"未知的日期类型: {type(trade_date)}")
                    continue
                
                records.append((trade_date_str,))
            
            if not records:
                logger.warning("没有有效的交易日历数据")
                return 0
            
            # 批量插入
            affected_rows = db_manager.execute_many(self.INSERT_TRADING_DATE_SQL, records)
            logger.info(f"成功保存 {affected_rows} 条交易日历记录")
            return affected_rows
            
        except Exception as e:
            logger.error(f"保存交易日历失败: {e}", exc_info=True)
            raise
    
    def fetch_and_save(self, update_existing: bool = True) -> bool:
        """
        获取交易日历并保存到数据库
        
        Args:
            update_existing: 是否更新已存在的记录
            
        Returns:
            是否成功
        """
        try:
            # 获取交易日历
            df = self.fetch_trading_calendar()
            if df is None or df.empty:
                logger.error("获取交易日历失败")
                return False
            
            # 保存到数据库
            count = self.save_trading_calendar(df, update_existing)
            if count > 0:
                logger.info(f"交易日历更新成功，共 {count} 条记录")
                return True
            else:
                logger.warning("交易日历保存失败，没有记录被保存")
                return False
                
        except Exception as e:
            logger.error(f"获取并保存交易日历失败: {e}", exc_info=True)
            return False
    
    def update_trading_calendar(self) -> bool:
        """
        更新交易日历（智能更新：只获取新数据）
        
        Returns:
            是否成功
        """
        try:
            # 获取最新交易日
            latest_date = self.get_latest_trading_date()
            
            if latest_date:
                logger.info(f"数据库中最新交易日: {latest_date}")
                # 获取所有交易日历（AKShare API返回所有历史数据）
                df = self.fetch_trading_calendar()
                if df is None or df.empty:
                    logger.error("获取交易日历失败")
                    return False
                
                # 过滤出需要更新的数据（大于最新日期的）
                if 'trade_date' in df.columns:
                    # 转换日期列为datetime类型以便比较
                    df['trade_date'] = pd.to_datetime(df['trade_date'])
                    latest_date_obj = pd.to_datetime(latest_date)
                    # 只保留大于最新日期的数据
                    df_new = df[df['trade_date'] > latest_date_obj].copy()
                    
                    if df_new.empty:
                        logger.info("交易日历已是最新，无需更新")
                        return True
                    
                    logger.info(f"发现 {len(df_new)} 条新交易日历数据，开始更新...")
                    count = self.save_trading_calendar(df_new, update_existing=True)
                    if count > 0:
                        logger.info(f"交易日历更新成功，共更新 {count} 条记录")
                        return True
                    else:
                        logger.warning("交易日历更新失败")
                        return False
                else:
                    # 如果没有trade_date列，保存所有数据
                    logger.warning("交易日历DataFrame缺少trade_date列，将保存所有数据")
                    return self.save_trading_calendar(df, update_existing=True)
            else:
                # 如果没有最新日期，保存所有数据
                logger.info("数据库中无交易日历数据，开始初始化...")
                return self.fetch_and_save(update_existing=True)
                
        except Exception as e:
            logger.error(f"更新交易日历失败: {e}", exc_info=True)
            return False
