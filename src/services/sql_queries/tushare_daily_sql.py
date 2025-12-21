"""
Tushare 日线数据服务 SQL 查询语句

提供 Supabase (PostgreSQL) 数据库的 SQL 语句。
"""

INSERT_DAILY_QUOTE = """
    INSERT INTO stock_daily (
        code, trade_date, open_price, high_price, low_price, 
        close_price, volume, amount, outstanding_share, turnover
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (code, trade_date) DO UPDATE SET
        open_price = EXCLUDED.open_price,
        high_price = EXCLUDED.high_price,
        low_price = EXCLUDED.low_price,
        close_price = EXCLUDED.close_price,
        volume = EXCLUDED.volume,
        amount = EXCLUDED.amount,
        outstanding_share = EXCLUDED.outstanding_share,
        turnover = EXCLUDED.turnover
"""

SELECT_LATEST_DATE = """
    SELECT MAX(trade_date) as latest_date 
    FROM stock_daily 
    WHERE code = %s
"""
