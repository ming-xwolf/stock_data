"""
交易日历服务 SQL 查询语句

分别为 Dolt (MySQL) 和 Supabase (PostgreSQL) 提供 SQL 语句。
"""

# ============================================
# Dolt (MySQL) SQL 语句
# ============================================

INSERT_TRADING_DATE_DOLT = """
    INSERT INTO trading_calendar (trade_date)
    VALUES (%s)
    ON DUPLICATE KEY UPDATE
        updated_at = CURRENT_TIMESTAMP
"""

SELECT_LATEST_DATE_DOLT = """
    SELECT MAX(trade_date) as latest_date 
    FROM trading_calendar
"""

SELECT_TRADING_DATE_DOLT = """
    SELECT trade_date 
    FROM trading_calendar 
    WHERE trade_date = %s
"""


# ============================================
# Supabase (PostgreSQL) SQL 语句
# ============================================

INSERT_TRADING_DATE_SUPABASE = """
    INSERT INTO trading_calendar (trade_date)
    VALUES (%s)
    ON CONFLICT (trade_date) DO UPDATE SET
        updated_at = CURRENT_TIMESTAMP
"""

SELECT_LATEST_DATE_SUPABASE = """
    SELECT MAX(trade_date) as latest_date 
    FROM trading_calendar
"""

SELECT_TRADING_DATE_SUPABASE = """
    SELECT trade_date 
    FROM trading_calendar 
    WHERE trade_date = %s
"""
