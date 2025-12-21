"""
交易日历服务 SQL 查询语句

提供 Supabase (PostgreSQL) 数据库的 SQL 语句。
"""

INSERT_TRADING_DATE = """
    INSERT INTO trading_calendar (trade_date)
    VALUES (%s)
    ON CONFLICT (trade_date) DO UPDATE SET
        updated_at = CURRENT_TIMESTAMP
"""

SELECT_LATEST_DATE = """
    SELECT MAX(trade_date) as latest_date 
    FROM trading_calendar
"""

SELECT_TRADING_DATE = """
    SELECT trade_date 
    FROM trading_calendar 
    WHERE trade_date = %s
"""
