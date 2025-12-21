"""
股票图表模块

提供股票K线图绘制功能，支持MACD和BOLL指标的可视化。
数据源使用 Supabase 数据库。
"""

from .stock_chart import StockChartGenerator
from .indicators import calculate_indicators

# 数据获取功能已迁移到 services/fetch_data_service.py
# 如需使用，请从 src.services.fetch_data_service 导入 fetch_data_service

__all__ = [
    "StockChartGenerator",
    "calculate_indicators",
]
