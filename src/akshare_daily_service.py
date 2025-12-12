"""
AKShare日线行情数据服务模块

提供股票日线行情数据的获取和存储功能。
优先使用 stock_zh_a_daily (新浪)，包含成交量和更多字段。
备选方案：stock_zh_a_hist_tx (腾讯) 和 stock_zh_a_hist_min_em (东方财富) API。
"""
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

import akshare as ak
from .db import db_manager

logger = logging.getLogger(__name__)


class DailyQuoteService:
    """
    日线行情数据服务类
    
    优化策略：
    1. 自动检测最新日期，只获取新数据
    2. 优先使用新浪API（包含完整字段，一次调用即可）
    3. 避免一次更新调用多个API
    4. 日期范围验证，跳过无效请求
    """
    
    # API调用延迟控制（秒）
    # 新浪API建议延迟 >= 2.0 秒以避免封IP
    DEFAULT_API_DELAY = 2.0
    
    INSERT_DAILY_QUOTE_SQL = """
        INSERT INTO stock_daily (
            code, trade_date, open_price, high_price, low_price, 
            close_price, volume, amount, outstanding_share, turnover
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            open_price = VALUES(open_price),
            high_price = VALUES(high_price),
            low_price = VALUES(low_price),
            close_price = VALUES(close_price),
            volume = VALUES(volume),
            amount = VALUES(amount),
            outstanding_share = VALUES(outstanding_share),
            turnover = VALUES(turnover)
    """
    
    SELECT_LATEST_DATE_SQL = """
        SELECT MAX(trade_date) as latest_date 
        FROM stock_daily 
        WHERE code = %s
    """
    
    def __init__(self, api_delay: float = None):
        """
        初始化服务
        
        Args:
            api_delay: API调用延迟（秒），如果为None则使用默认值
        """
        self.api_delay = api_delay if api_delay is not None else self.DEFAULT_API_DELAY
        self._last_api_call_time = 0
    
    def _wait_for_rate_limit(self):
        """
        等待以确保不超过API调用频率限制
        
        注意：新浪API大量抓取容易封IP，建议延迟 >= 2.0 秒
        """
        if self.api_delay > 0:
            elapsed = time.time() - self._last_api_call_time
            if elapsed < self.api_delay:
                sleep_time = self.api_delay - elapsed
                time.sleep(sleep_time)
            self._last_api_call_time = time.time()
    
    def get_daily_quote_sina(
        self,
        code: str,
        start_date: str,
        end_date: str,
        adjust: str = 'qfq'
    ) -> Optional[pd.DataFrame]:
        """
        使用新浪数据源获取日线数据（推荐，包含成交量和更多字段）
        
        Args:
            code: 股票代码（6位数字）
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            adjust: 复权方式 ('qfq'=前复权, 'hfq'=后复权, ''=不复权)
            
        Returns:
            日线数据DataFrame，列名: ['date', 'open', 'high', 'low', 'close', 
                                    'volume', 'amount', 'outstanding_share', 'turnover']
        """
        try:
            # 添加延迟控制
            self._wait_for_rate_limit()
            
            symbol = DailyQuoteService.convert_code(code)
            
            logger.debug(f"使用新浪API获取股票 {code} ({symbol}) 日线数据: {start_date} 到 {end_date}")
            df = ak.stock_zh_a_daily(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            
            if df is None or df.empty:
                logger.warning(f"股票 {code} 未获取到数据")
                return None
            
            logger.debug(f"成功获取股票 {code} {len(df)} 条日线数据")
            logger.debug(f"数据字段: {list(df.columns)}")
            return df
            
        except Exception as e:
            logger.error(f"使用新浪API获取股票 {code} 日线数据失败: {e}")
            return None
    
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
    
    def get_daily_quote_tx(
        self,
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
            # 添加延迟控制
            self._wait_for_rate_limit()
            
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
    
    def get_daily_quote_from_minute(
        self,
        code: str, 
        start_date: str, 
        end_date: str,
        adjust: str = ''
    ) -> Optional[pd.DataFrame]:
        """
        通过分时数据聚合获取日线数据（备选方案）
        
        注意：此方法速度较慢，建议优先使用新浪API
        
        Args:
            code: 股票代码（6位数字）
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            adjust: 复权方式
            
        Returns:
            日线数据DataFrame，包含完整的OHLCV数据
        """
        try:
            # 添加延迟控制
            self._wait_for_rate_limit()
            
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
        use_minute: bool = False,
        use_sina: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        获取日线数据（优先使用新浪API，包含成交量和更多字段）
        
        优化策略：
        1. 优先使用新浪API（包含完整字段，一次调用即可）
        2. 如果新浪API失败，使用腾讯API（不包含成交量）
        3. 只有在明确需要成交量且腾讯API成功时，才使用分时API补充
        4. 避免一次更新调用多个API
        
        Args:
            code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            adjust: 复权方式
            use_minute: 是否强制使用分时API（用于获取成交量）
            use_sina: 是否优先使用新浪API（默认True，推荐）
            
        Returns:
            日线数据DataFrame
        """
        if use_minute:
            # 强制使用分时API（可以获取成交量）
            return self.get_daily_quote_from_minute(code, start_date, end_date, adjust)
        
        # 优先使用新浪API（包含成交量和更多字段，一次调用即可）
        if use_sina:
            df = self.get_daily_quote_sina(code, start_date, end_date, adjust)
            if df is not None and not df.empty:
                # 新浪API包含完整字段，直接返回（避免额外API调用）
                logger.debug(f"股票 {code} 使用新浪API成功获取数据（包含完整字段）")
                return df
            # 如果新浪API失败，记录日志但不立即尝试其他API
            logger.debug(f"股票 {code} 新浪API获取失败，尝试备选方案")
        
        # 备选方案：使用腾讯API（不包含成交量，但速度快）
        df = self.get_daily_quote_tx(code, start_date, end_date, adjust)
        
        if df is not None and not df.empty:
            # 腾讯API没有成交量字段，但为了减少API调用，不自动补充
            # 只有在明确需要成交量时才使用分时API
            # 注意：这里不自动补充成交量，避免额外的API调用
            # 如果需要成交量，应该使用新浪API或设置 use_minute=True
            logger.debug(f"股票 {code} 使用腾讯API获取数据（不包含成交量）")
            return df
        
        # 如果所有API都失败，返回None
        logger.warning(f"股票 {code} 所有API都获取失败")
        return None
    
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
                outstanding_share = int(row.get('outstanding_share', 0)) if pd.notna(row.get('outstanding_share')) else None
                turnover = float(row.get('turnover', 0)) if pd.notna(row.get('turnover')) else None
                
                params_list.append((
                    code,
                    trade_date,
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume,
                    amount,
                    outstanding_share,
                    turnover
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
            use_minute: bool = False,
            use_sina: bool = True
    ) -> bool:
        """
        获取并保存日线数据
        
        Args:
            code: 股票代码
            start_date: 开始日期 (YYYYMMDD)，如果为None则从最新日期开始
            end_date: 结束日期 (YYYYMMDD)，如果为None则使用今天
            adjust: 复权方式
            use_minute: 是否使用分时API（用于获取成交量）
            use_sina: 是否优先使用新浪API
            
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
            
            # 检查日期范围是否有效
            start_dt = datetime.strptime(start_date, '%Y%m%d')
            end_dt = datetime.strptime(end_date, '%Y%m%d')
            
            if start_dt > end_dt:
                logger.debug(f"股票 {code} 开始日期 {start_date} 大于结束日期 {end_date}，跳过（已是最新数据）")
                return True  # 返回True表示不需要更新
            
            # 如果开始日期是未来日期，也跳过
            today = datetime.now().date()
            if start_dt.date() > today:
                logger.debug(f"股票 {code} 开始日期 {start_date} 是未来日期，跳过")
                return True
            
            # 获取数据
            df = self.get_daily_quote(code, start_date, end_date, adjust, use_minute, use_sina)
            
            if df is None or df.empty:
                logger.debug(f"股票 {code} 未获取到数据（日期范围: {start_date} 到 {end_date}）")
                return False
            
            # 保存数据
            saved_count = self.save_daily_quote(code, df)
            
            if saved_count > 0:
                logger.info(f"成功更新股票 {code} {saved_count} 条日线数据")
                return True
            else:
                # 如果保存了0条，可能是因为数据已存在（ON DUPLICATE KEY UPDATE）
                # 检查是否是因为日期范围没有新数据
                latest_date = self.get_latest_date(code)
                if latest_date:
                    latest_dt = datetime.strptime(latest_date, '%Y-%m-%d')
                    end_dt = datetime.strptime(end_date, '%Y%m%d')
                    # 如果最新日期 >= 结束日期，说明数据已是最新，返回True
                    if latest_dt.date() >= end_dt.date():
                        logger.debug(f"股票 {code} 数据已是最新（最新日期: {latest_date} >= 结束日期: {end_date}）")
                        return True
                logger.debug(f"股票 {code} 没有新数据需要保存（可能数据已存在或日期范围内无数据）")
                return False
                
        except Exception as e:
            logger.error(f"获取并保存股票 {code} 日线数据失败: {e}", exc_info=True)
            return False
