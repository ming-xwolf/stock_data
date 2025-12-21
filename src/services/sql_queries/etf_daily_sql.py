"""
ETF 日线数据服务 SQL 查询语句

提供 Supabase (PostgreSQL) 数据库的 SQL 语句。
"""

INSERT_DAILY = """
    INSERT INTO etf_daily (code, trade_date, open_price, high_price, low_price, 
                          close_price, volume, amount, change_amount, change_rate, turnover)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (code, trade_date) DO UPDATE SET
        open_price = EXCLUDED.open_price,
        high_price = EXCLUDED.high_price,
        low_price = EXCLUDED.low_price,
        close_price = EXCLUDED.close_price,
        volume = EXCLUDED.volume,
        amount = EXCLUDED.amount,
        change_amount = EXCLUDED.change_amount,
        change_rate = EXCLUDED.change_rate,
        turnover = EXCLUDED.turnover
"""

SELECT_LATEST_DATE = """
    SELECT MAX(trade_date) as latest_date 
    FROM etf_daily 
    WHERE code = %s
"""

SELECT_DAILY_DATA = """
    SELECT * FROM etf_daily 
    WHERE code = %s AND trade_date >= %s AND trade_date <= %s
    ORDER BY trade_date
"""

COUNT_DAILY = """
    SELECT COUNT(*) as count 
    FROM etf_daily 
    WHERE code = %s
"""

SELECT_EXISTING_DATES = """
    SELECT trade_date 
    FROM etf_daily 
    WHERE code = %s AND trade_date >= %s AND trade_date <= %s
    ORDER BY trade_date
"""

# 查询需要更新的 ETF 列表（缺少最新交易日数据的 ETF）
# 只考虑今天或今天以前的交易日
SELECT_ETFS_NEED_UPDATE = """
    WITH latest_trading_date AS (
        SELECT MAX(trade_date) as latest_date 
        FROM trading_calendar
        WHERE trade_date <= CURRENT_DATE
    ),
    etf_latest_dates AS (
        SELECT 
            e.code,
            COALESCE(MAX(d.trade_date), '1900-01-01'::date) as latest_daily_date
        FROM etf_funds e
        LEFT JOIN etf_daily d ON e.code = d.code
        GROUP BY e.code
    )
    SELECT 
        e.code,
        f.name,
        e.latest_daily_date,
        t.latest_date as latest_trading_date,
        CASE 
            WHEN e.latest_daily_date < t.latest_date THEN 
                (e.latest_daily_date + INTERVAL '1 day')::date
            ELSE NULL
        END as start_date
    FROM etf_latest_dates e
    CROSS JOIN latest_trading_date t
    LEFT JOIN etf_funds f ON e.code = f.code
    WHERE e.latest_daily_date < t.latest_date
    ORDER BY e.code
"""
