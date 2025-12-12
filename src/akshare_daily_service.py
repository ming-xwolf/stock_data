"""
AKShare日线行情数据服务模块

提供股票日线行情数据的获取和存储功能。
使用 stock_zh_a_hist_tx (腾讯) 和 stock_zh_a_hist_min_em (东方财富) API。
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

import akshare as ak
from .db import db_manager

logger = logging.getLogger(__name__)


class DailyQuoteService:
    """日线行情数据服务类"""
    
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
    
    @staticmethod
    def convert_code(code: str) -> str:
        """
        将6位股票代码转换为带市场标识的格式
        
        Args:
            code: 股票代码（6位数字）
            
        Returns:
            带市场标识的代码（如 'sz000001' 或 'sh600519'）
        """
        if code.startswith(('0', '3')):
            return f'sz{code}'  # 深圳
        else:
            return f'sh{code}'  # 上海
    
    @staticmethod
    def get_daily_quote_tx(
        code: str, 
        start_date: str, 
        end_date: str,
        adjust: str = 'qfq'
    ) -> Optional[pd.DataFrame]:
        """
        使用腾讯数据源获取日线数据
        
        Args:
            code: 股票代码（6位数字）
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            adjust: 复权方式 ('qfq'=前复权, 'hfq'=后复权, ''=不复权)
            
        Returns:
            日线数据DataFrame，列名: ['date', 'open', 'close', 'high', 'low', 'amount']
            注意：此API没有成交量字段，只有成交额
        """
        try:
            symbol = DailyQuoteService.convert_code(code)
            
            logger.debug(f"使用腾讯API获取股票 {code} ({symbol}) 日线数据: {start_date} 到 {end_date}")
            df = ak.stock_zh_a_hist_tx(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            
            if df is None or df.empty:
                logger.warning(f"股票 {code} 未获取到数据")
                return None
            
            logger.debug(f"成功获取股票 {code} {len(df)} 条日线数据")
            return df
            
        except Exception as e:
            logger.error(f"使用腾讯API获取股票 {code} 日线数据失败: {e}")
            return None
    
    @staticmethod
    def get_daily_quote_from_minute(
        code: str, 
        start_date: str, 
        end_date: str,
        adjust: str = ''
    ) -> Optional[pd.DataFrame]:
        """
        通过分时数据聚合获取日线数据（备选方案）
        
        Args:
            code: 股票代码（6位数字）
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            adjust: 复权方式
            
        Returns:
            日线数据DataFrame，包含完整的OHLCV数据
        """
        try:
            logger.debug(f"使用东方财富分时API获取股票 {code} 日线数据: {start_date} 到 {end_date}")
            
            # 获取1分钟分时数据
            df = ak.stock_zh_a_hist_min_em(
                symbol=code,
                start_date=start_date,
                end_date=end_date,
                period='1',  # 1分钟
                adjust=adjust
            )
            
            if df is None or df.empty:
                logger.warning(f"股票 {code} 未获取到分时数据")
                return None
            
            # 聚合为日线
            df['日期'] = pd.to_datetime(df['时间']).dt.date
            daily = df.groupby('日期').agg({
                '开盘': 'first',
                '收盘': 'last',
                '最高': 'max',
                '最低': 'min',
                '成交量': 'sum',
                '成交额': 'sum'
            }).reset_index()
            
            # 重命名列
            daily = daily.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount'
            })
            
            logger.debug(f"成功聚合股票 {code} {len(daily)} 条日线数据")
            return daily
            
        except Exception as e:
            logger.error(f"使用分时API获取股票 {code} 日线数据失败: {e}")
            return None
    
    def get_daily_quote(
        self,
        code: str,
        start_date: str,
        end_date: str,
        adjust: str = 'qfq',
        use_minute: bool = False
    ) -> Optional[pd.DataFrame]:
        """
        获取日线数据（优先使用腾讯API，失败时使用分时API）
        
        Args:
            code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            adjust: 复权方式
            use_minute: 是否强制使用分时API（用于获取成交量）
            
        Returns:
            日线数据DataFrame
        """
        if use_minute:
            # 强制使用分时API（可以获取成交量）
            return self.get_daily_quote_from_minute(code, start_date, end_date, adjust)
        
        # 优先使用腾讯API
        df = self.get_daily_quote_tx(code, start_date, end_date, adjust)
        
        if df is not None and not df.empty:
            # 如果需要成交量，尝试使用分时API补充
            if 'volume' not in df.columns:
                df_minute = self.get_daily_quote_from_minute(code, start_date, end_date, adjust)
                if df_minute is not None and not df_minute.empty:
                    # 合并成交量数据
                    df['date'] = pd.to_datetime(df['date'])
                    df_minute['date'] = pd.to_datetime(df_minute['date'])
                    df = pd.merge(df, df_minute[['date', 'volume']], on='date', how='left')
        
        return df
    
    def save_daily_quote(self, code: str, df: pd.DataFrame) -> int:
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
                # 处理日期格式
                trade_date = row.get('date')
                if isinstance(trade_date, str):
                    trade_date = datetime.strptime(trade_date, '%Y-%m-%d').date()
                elif isinstance(trade_date, pd.Timestamp):
                    trade_date = trade_date.date()
                elif hasattr(trade_date, 'date'):
                    trade_date = trade_date.date()
                else:
                    trade_date = pd.to_datetime(trade_date).date()
                
                # 提取数据
                open_price = float(row.get('open', 0)) if pd.notna(row.get('open')) else None
                high_price = float(row.get('high', 0)) if pd.notna(row.get('high')) else None
                low_price = float(row.get('low', 0)) if pd.notna(row.get('low')) else None
                close_price = float(row.get('close', 0)) if pd.notna(row.get('close')) else None
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
    
    def fetch_and_save(
        self,
        code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        adjust: str = 'qfq',
        use_minute: bool = False
    ) -> bool:
        """
        获取并保存日线数据
        
        Args:
            code: 股票代码
            start_date: 开始日期 (YYYYMMDD)，如果为None则从最新日期开始
            end_date: 结束日期 (YYYYMMDD)，如果为None则使用今天
            adjust: 复权方式
            use_minute: 是否使用分时API（用于获取成交量）
            
        Returns:
            是否成功
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
            df = self.get_daily_quote(code, start_date, end_date, adjust, use_minute)
            
            if df is None or df.empty:
                logger.warning(f"股票 {code} 未获取到数据")
                return False
            
            # 保存数据
            saved_count = self.save_daily_quote(code, df)
            
            if saved_count > 0:
                logger.info(f"成功更新股票 {code} {saved_count} 条日线数据")
                return True
            else:
                logger.warning(f"股票 {code} 没有新数据需要保存")
                return False
                
        except Exception as e:
            logger.error(f"获取并保存股票 {code} 日线数据失败: {e}", exc_info=True)
            return False
