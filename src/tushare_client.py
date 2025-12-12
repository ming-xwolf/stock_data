"""
Tushare数据获取客户端

提供使用Tushare API获取股票数据的封装。
"""
import os
import logging
import time
from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import tushare as ts

try:
    from dotenv import load_dotenv
except ImportError:
    # 如果没有安装python-dotenv，使用简单的实现
    def load_dotenv(dotenv_path=None):
        """简单的.env文件加载实现"""
        import os
        if dotenv_path is None:
            project_root = Path(__file__).parent.parent
            dotenv_path = project_root / "database" / ".env"
        
        env_file = Path(dotenv_path)
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

logger = logging.getLogger(__name__)

# 加载环境变量
project_root = Path(__file__).parent.parent
env_path = project_root / "database" / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)
else:
    # 也尝试从项目根目录加载
    load_dotenv(project_root / ".env", override=True)

# 初始化Tushare token
TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN')
if TUSHARE_TOKEN:
    ts.set_token(TUSHARE_TOKEN)
else:
    logger.warning("未找到TUSHARE_TOKEN环境变量")


class TushareClient:
    """
    Tushare客户端类
    
    自动处理API调用频率限制：
    - Tushare API限制：
      * 免费版：每日500次，每分钟30次
      * Pro版：每日2000次，每分钟可能更多
    - 默认延迟设置为0.2秒（每分钟最多300次），确保不会超出限制
    - 每次API调用后会自动等待，确保调用间隔符合限制
    """
    
    # Tushare API限制：
    # - 免费版：每日500次，每分钟30次
    # - Pro版：每日2000次，每分钟可能更多
    # 默认延迟设置为0.2秒（每分钟最多300次），确保不会超出限制
    DEFAULT_API_DELAY = 0.2  # 秒
    
    def __init__(self, api_delay: float = None):
        """
        初始化Tushare客户端
        
        Args:
            api_delay: API调用之间的延迟（秒），如果为None则使用默认值
        """
        if not TUSHARE_TOKEN:
            raise ValueError("TUSHARE_TOKEN未配置，请检查环境变量")
        self.pro = ts.pro_api()
        self.api_delay = api_delay if api_delay is not None else self.DEFAULT_API_DELAY
        self._last_api_call_time = 0
        logger.debug(f"Tushare客户端初始化成功，API延迟设置为 {self.api_delay} 秒")
    
    def convert_code_to_ts_code(self, code: str) -> str:
        """
        将6位股票代码转换为Tushare格式
        
        Args:
            code: 股票代码（6位数字，如 '000001'）
            
        Returns:
            Tushare格式代码（如 '000001.SZ' 或 '600000.SH'）
        """
        if len(code) != 6:
            raise ValueError(f"股票代码长度不正确: {code}")
        
        if code.startswith(('0', '3')):
            return f"{code}.SZ"  # 深圳
        else:
            return f"{code}.SH"  # 上海
    
    def convert_ts_code_to_code(self, ts_code: str) -> str:
        """
        将Tushare格式代码转换为6位股票代码
        
        Args:
            ts_code: Tushare格式代码（如 '000001.SZ'）
            
        Returns:
            6位股票代码（如 '000001'）
        """
        return ts_code.split('.')[0]
    
    def _wait_for_rate_limit(self):
        """
        等待以确保不超过API调用频率限制
        """
        if self.api_delay > 0:
            elapsed = time.time() - self._last_api_call_time
            if elapsed < self.api_delay:
                sleep_time = self.api_delay - elapsed
                time.sleep(sleep_time)
            self._last_api_call_time = time.time()
    
    def get_daily_data(
        self,
        code: str,
        start_date: str,
        end_date: str,
        fields: Optional[list] = None
    ) -> Optional[pd.DataFrame]:
        """
        获取日线数据
        
        Args:
            code: 股票代码（6位数字）
            start_date: 开始日期（YYYYMMDD格式）
            end_date: 结束日期（YYYYMMDD格式）
            fields: 字段列表，如果为None则使用默认字段
            
        Returns:
            日线数据DataFrame，包含以下列：
            - ts_code: Tushare代码
            - trade_date: 交易日期（YYYYMMDD）
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - vol: 成交量（手）
            - amount: 成交额（千元）
        """
        try:
            ts_code = self.convert_code_to_ts_code(code)
            
            if fields is None:
                fields = 'ts_code,trade_date,open,high,low,close,vol,amount'
            
            logger.debug(f"获取股票 {code} ({ts_code}) 日线数据: {start_date} 到 {end_date}")
            
            # 等待以确保不超过API调用频率限制
            self._wait_for_rate_limit()
            
            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                fields=fields
            )
            
            if df is None or df.empty:
                logger.warning(f"股票 {code} 未获取到数据")
                return None
            
            logger.debug(f"成功获取股票 {code} {len(df)} 条日线数据")
            return df
            
        except Exception as e:
            logger.error(f"获取股票 {code} 日线数据失败: {e}")
            return None
    
    def get_all_stock_codes(self) -> Optional[pd.DataFrame]:
        """
        获取所有股票代码列表
        
        Returns:
            股票基本信息DataFrame，包含ts_code, symbol, name等字段
        """
        try:
            logger.debug("获取所有股票代码列表...")
            
            # 等待以确保不超过API调用频率限制
            self._wait_for_rate_limit()
            
            df = self.pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,symbol,name,area,industry,list_date'
            )
            
            if df is None or df.empty:
                logger.warning("未获取到股票列表")
                return None
            
            logger.debug(f"成功获取 {len(df)} 只股票代码")
            return df
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return None
    
    def format_daily_data_for_db(self, df: pd.DataFrame, code: str) -> pd.DataFrame:
        """
        格式化日线数据为数据库格式
        
        Args:
            df: Tushare返回的日线数据DataFrame
            code: 股票代码（6位数字）
            
        Returns:
            格式化后的DataFrame，包含以下列：
            - code: 股票代码
            - trade_date: 交易日期（date类型）
            - open_price: 开盘价
            - high_price: 最高价
            - low_price: 最低价
            - close_price: 收盘价
            - volume: 成交量（股）
            - amount: 成交额（元）
        """
        if df is None or df.empty:
            return pd.DataFrame()
        
        # 复制数据框
        result = df.copy()
        
        # 转换代码格式
        result['code'] = code
        
        # 转换日期格式
        result['trade_date'] = pd.to_datetime(result['trade_date'], format='%Y%m%d').dt.date
        
        # 重命名列
        column_mapping = {
            'open': 'open_price',
            'high': 'high_price',
            'low': 'low_price',
            'close': 'close_price',
            'vol': 'volume',  # Tushare返回的是手，需要转换为股
            'amount': 'amount'  # Tushare返回的是千元，需要转换为元
        }
        
        result = result.rename(columns=column_mapping)
        
        # 转换成交量：Tushare返回的是手（1手=100股），转换为股
        if 'volume' in result.columns:
            result['volume'] = result['volume'] * 100
        
        # 转换成交额：Tushare返回的是千元，转换为元
        if 'amount' in result.columns:
            result['amount'] = result['amount'] * 1000
        
        # 选择需要的列
        required_columns = ['code', 'trade_date', 'open_price', 'high_price', 
                          'low_price', 'close_price', 'volume', 'amount']
        
        # 只保留存在的列
        available_columns = [col for col in required_columns if col in result.columns]
        result = result[available_columns]
        
        return result


# 全局客户端实例
_tushare_client: Optional[TushareClient] = None


def get_tushare_client(api_delay: Optional[float] = None) -> TushareClient:
    """
    获取Tushare客户端单例
    
    Args:
        api_delay: API调用之间的延迟（秒），如果为None则使用默认值
                   仅在首次调用时生效
    
    Returns:
        TushareClient实例
    """
    global _tushare_client
    if _tushare_client is None:
        _tushare_client = TushareClient(api_delay=api_delay)
    return _tushare_client
