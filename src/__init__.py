"""
Stock Data - 中国A股行情数据准备工具

Python代码模块，用于处理股票数据获取、清洗和存储。
"""

__version__ = "0.1.0"

# 向后兼容：导出常用模块
from .core.db import db_manager
from .core.config import db_config
from .core.cache_manager import (
    cached_api_call,
    clear_all_caches,
    get_cache_stats
)

# 导出客户端
from .clients.akshare_client import AKShareClient
from .clients.tushare_client import TushareClient, get_tushare_client

# 导出服务
from .services.limit_service import LimitService
from .services.stock_service import StockService
from .services.industry_service import IndustryService
from .services.shareholder_service import ShareholderService
from .services.market_value_service import MarketValueService
from .services.financial_service import FinancialService
from .services.trading_calendar_service import TradingCalendarService
from .services.akshare_daily_service import DailyQuoteService
from .services.tushare_daily_service import TushareDailyService

__all__ = [
    # 版本
    '__version__',
    # 核心模块
    'db_manager',
    'db_config',
    'cached_api_call',
    'clear_all_caches',
    'get_cache_stats',
    # 客户端
    'AKShareClient',
    'TushareClient',
    'get_tushare_client',
    # 服务
    'LimitService',
    'StockService',
    'IndustryService',
    'ShareholderService',
    'MarketValueService',
    'FinancialService',
    'TradingCalendarService',
    'DailyQuoteService',
    'TushareDailyService',
]
