"""
Tushare日线数据服务模块

提供使用Tushare获取日线行情数据并更新到数据库的功能。
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd

from .tushare_client import get_tushare_client, TushareClient
from .db import db_manager

logger = logging.getLogger(__name__)


class TushareDailyService:
    """Tushare日线数据服务类"""
    
    INSERT_DAILY_QUOTE_SQL = """
        INSERT INTO stock_daily (
            code, trade_date, open_price, high_price, low_price, 
            close_price, volume, amount
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            open_price = VALUES(open_price),
            high_price = VALUES(high_price),
            low_price = VALUES(low_price),
            close_price = VALUES(close_price),
            volume = VALUES(volume),
            amount = VALUES(amount)
    """
    
    SELECT_LATEST_DATE_SQL = """
        SELECT MAX(trade_date) as latest_date 
        FROM stock_daily 
        WHERE code = %s
    """
    
    def __init__(self, client: Optional[TushareClient] = None):
        """
        初始化服务
        
        Args:
            client: Tushare客户端，如果为None则使用默认客户端
        """
        self.client = client or get_tushare_client()
    
    def get_latest_date(self, code: str) -> Optional[str]:
        """
        获取股票最新的交易日期
        
        Args:
            code: 股票代码
            
        Returns:
            最新交易日期（YYYY-MM-DD格式），如果没有数据返回None
        """
        try:
            results = db_manager.execute_query(self.SELECT_LATEST_DATE_SQL, (code,))
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
            logger.error(f"查询股票 {code} 最新交易日期失败: {e}")
            return None
    
    def fetch_daily_data(
        self,
        code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        获取日线数据
        
        Args:
            code: 股票代码（6位数字）
            start_date: 开始日期（YYYYMMDD格式），如果为None则从最新日期开始
            end_date: 结束日期（YYYYMMDD格式），如果为None则使用今天
            
        Returns:
            格式化后的日线数据DataFrame
        """
        try:
            # 如果没有指定开始日期，从最新日期开始
            if start_date is None:
                latest_date = self.get_latest_date(code)
                if latest_date:
                    # 从最新日期的下一天开始
                    latest_dt = datetime.strptime(latest_date, '%Y-%m-%d')
                    start_date = (latest_dt + timedelta(days=1)).strftime('%Y%m%d')
                else:
                    # 如果没有数据，获取最近一年的数据
                    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            
            # 如果没有指定结束日期，使用今天
            if end_date is None:
                end_date = datetime.now().strftime('%Y%m%d')
            
            # 获取数据
            df = self.client.get_daily_data(code, start_date, end_date)
            
            if df is None or df.empty:
                logger.warning(f"股票 {code} 未获取到数据")
                return None
            
            # 格式化数据
            formatted_df = self.client.format_daily_data_for_db(df, code)
            
            return formatted_df
            
        except Exception as e:
            logger.error(f"获取股票 {code} 日线数据失败: {e}", exc_info=True)
            return None
    
    def save_daily_data(self, code: str, df: pd.DataFrame) -> int:
        """
        保存日线数据到数据库
        
        Args:
            code: 股票代码
            df: 日线数据DataFrame
            
        Returns:
            成功保存的记录数
        """
        if df is None or df.empty:
            return 0
        
        try:
            params_list = []
            for _, row in df.iterrows():
                # 提取数据
                trade_date = row.get('trade_date')
                if isinstance(trade_date, str):
                    trade_date = datetime.strptime(trade_date, '%Y-%m-%d').date()
                elif hasattr(trade_date, 'date'):
                    trade_date = trade_date.date()
                else:
                    trade_date = pd.to_datetime(trade_date).date()
                
                open_price = float(row.get('open_price', 0)) if pd.notna(row.get('open_price')) else None
                high_price = float(row.get('high_price', 0)) if pd.notna(row.get('high_price')) else None
                low_price = float(row.get('low_price', 0)) if pd.notna(row.get('low_price')) else None
                close_price = float(row.get('close_price', 0)) if pd.notna(row.get('close_price')) else None
                volume = int(row.get('volume', 0)) if pd.notna(row.get('volume')) else None
                amount = float(row.get('amount', 0)) if pd.notna(row.get('amount')) else None
                
                params_list.append((
                    code,
                    trade_date,
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume,
                    amount
                ))
            
            if not params_list:
                return 0
            
            affected_rows = db_manager.execute_many(
                self.INSERT_DAILY_QUOTE_SQL,
                params_list
            )
            
            logger.info(f"成功保存股票 {code} {affected_rows} 条日线数据")
            return affected_rows
            
        except Exception as e:
            logger.error(f"保存股票 {code} 日线数据失败: {e}", exc_info=True)
            raise
    
    def fetch_and_save(
        self,
        code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> bool:
        """
        获取并保存日线数据
        
        Args:
            code: 股票代码
            start_date: 开始日期（YYYYMMDD格式），如果为None则从最新日期开始
            end_date: 结束日期（YYYYMMDD格式），如果为None则使用今天
            
        Returns:
            是否成功
        """
        try:
            # 获取数据
            df = self.fetch_daily_data(code, start_date, end_date)
            
            if df is None or df.empty:
                logger.warning(f"股票 {code} 未获取到数据")
                return False
            
            # 保存数据
            saved_count = self.save_daily_data(code, df)
            
            if saved_count > 0:
                logger.info(f"成功更新股票 {code} {saved_count} 条日线数据")
                return True
            else:
                logger.warning(f"股票 {code} 没有新数据需要保存")
                return False
                
        except Exception as e:
            logger.error(f"获取并保存股票 {code} 日线数据失败: {e}", exc_info=True)
            return False
    
    def batch_update(
        self,
        codes: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        delay: float = 1.0
    ) -> dict:
        """
        批量更新多只股票的日线数据
        
        Args:
            codes: 股票代码列表
            start_date: 开始日期（YYYYMMDD格式）
            end_date: 结束日期（YYYYMMDD格式）
            delay: 每次API调用之间的延迟（秒）
            
        Returns:
            统计信息字典，包含success_count, failed_count等
        """
        import time
        
        success_count = 0
        failed_count = 0
        
        logger.info(f"开始批量更新 {len(codes)} 只股票的日线数据...")
        
        for i, code in enumerate(codes, 1):
            if i % 10 == 0:
                logger.info(f"已处理 {i}/{len(codes)} 只股票...")
            
            try:
                success = self.fetch_and_save(code, start_date, end_date)
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                
                # 添加延迟，避免API限流
                # 注意：TushareClient内部已经有默认延迟（0.2秒），这里添加额外延迟
                # 以确保批量更新时更加保守
                if delay > 0 and i < len(codes):
                    # 如果delay小于客户端默认延迟，使用客户端延迟
                    # 否则使用指定的delay（减去客户端已等待的时间）
                    client_delay = getattr(self.client, 'api_delay', 0.2)
                    additional_delay = max(0, delay - client_delay)
                    if additional_delay > 0:
                        time.sleep(additional_delay)
                    
            except Exception as e:
                logger.error(f"更新股票 {code} 失败: {e}")
                failed_count += 1
                continue
        
        result = {
            'total': len(codes),
            'success_count': success_count,
            'failed_count': failed_count
        }
        
        logger.info(f"批量更新完成: 成功 {success_count} 只，失败 {failed_count} 只，总计 {len(codes)} 只")
        
        return result
