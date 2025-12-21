"""
AKShare 日线数据服务 SQL 查询语句

分别为 Dolt (MySQL) 和 Supabase (PostgreSQL) 提供 SQL 语句。
"""

# ============================================
# Dolt (MySQL) SQL 语句
# ============================================

INSERT_DAILY_QUOTE_DOLT = """
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

SELECT_LATEST_DATE_DOLT = """
    SELECT MAX(trade_date) as latest_date 
    FROM stock_daily 
    WHERE code = %s
"""


# ============================================
# Supabase (PostgreSQL) SQL 语句
# ============================================

INSERT_DAILY_QUOTE_SUPABASE = """
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

SELECT_LATEST_DATE_SUPABASE = """
    SELECT MAX(trade_date) as latest_date 
    FROM stock_daily 
    WHERE code = %s
"""
