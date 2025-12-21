"""
ETF 日线数据服务 SQL 查询语句

分别为 Dolt (MySQL) 和 Supabase (PostgreSQL) 提供 SQL 语句。
"""

# ============================================
# Dolt (MySQL) SQL 语句
# ============================================

INSERT_DAILY_DOLT = """
    INSERT INTO etf_daily (code, trade_date, open_price, high_price, low_price, 
                          close_price, volume, amount, change_amount, change_rate, turnover)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        open_price = VALUES(open_price),
        high_price = VALUES(high_price),
        low_price = VALUES(low_price),
        close_price = VALUES(close_price),
        volume = VALUES(volume),
        amount = VALUES(amount),
        change_amount = VALUES(change_amount),
        change_rate = VALUES(change_rate),
        turnover = VALUES(turnover)
"""

SELECT_LATEST_DATE_DOLT = """
    SELECT MAX(trade_date) as latest_date 
    FROM etf_daily 
    WHERE code = %s
"""

SELECT_DAILY_DATA_DOLT = """
    SELECT * FROM etf_daily 
    WHERE code = %s AND trade_date >= %s AND trade_date <= %s
    ORDER BY trade_date
"""

COUNT_DAILY_DOLT = """
    SELECT COUNT(*) as count 
    FROM etf_daily 
    WHERE code = %s
"""

SELECT_EXISTING_DATES_DOLT = """
    SELECT trade_date 
    FROM etf_daily 
    WHERE code = %s AND trade_date >= %s AND trade_date <= %s
    ORDER BY trade_date
"""


# ============================================
# Supabase (PostgreSQL) SQL 语句
# ============================================

INSERT_DAILY_SUPABASE = """
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

SELECT_LATEST_DATE_SUPABASE = """
    SELECT MAX(trade_date) as latest_date 
    FROM etf_daily 
    WHERE code = %s
"""

SELECT_DAILY_DATA_SUPABASE = """
    SELECT * FROM etf_daily 
    WHERE code = %s AND trade_date >= %s AND trade_date <= %s
    ORDER BY trade_date
"""

COUNT_DAILY_SUPABASE = """
    SELECT COUNT(*) as count 
    FROM etf_daily 
    WHERE code = %s
"""

SELECT_EXISTING_DATES_SUPABASE = """
    SELECT trade_date 
    FROM etf_daily 
    WHERE code = %s AND trade_date >= %s AND trade_date <= %s
    ORDER BY trade_date
"""
