"""
数据获取服务 SQL 查询语句

提供 Supabase (PostgreSQL) 数据库的 SQL 语句。
"""

# 获取股票日线数据
SELECT_STOCK_DAILY_DATA = """
    SELECT 
        trade_date,
        open_price as open,
        high_price as high,
        low_price as low,
        close_price as close,
        volume
    FROM stock_daily
    WHERE code = %s 
        AND trade_date >= %s 
        AND trade_date <= %s
    ORDER BY trade_date
"""

# 获取股票名称
SELECT_STOCK_NAME = "SELECT name FROM stocks WHERE code = %s"

# 获取指定股票最早交易日期
SELECT_EARLIEST_TRADE_DATE_BY_CODE = "SELECT MIN(trade_date) as earliest_date FROM stock_daily WHERE code = %s"

# 获取全局最早交易日期
SELECT_EARLIEST_TRADE_DATE = "SELECT MIN(trade_date) as earliest_date FROM stock_daily"

# 获取指定股票最新交易日期
SELECT_LATEST_TRADE_DATE_BY_CODE = "SELECT MAX(trade_date) as latest_date FROM stock_daily WHERE code = %s"

# 获取全局最新交易日期
SELECT_LATEST_TRADE_DATE = "SELECT MAX(trade_date) as latest_date FROM stock_daily"
