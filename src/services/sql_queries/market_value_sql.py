"""
市值数据服务 SQL 查询语句

分别为 Dolt (MySQL) 和 Supabase (PostgreSQL) 提供 SQL 语句。
"""

# ============================================
# Dolt (MySQL) SQL 语句
# ============================================

INSERT_MARKET_VALUE_DOLT = """
    INSERT INTO stock_market_value (
        code, total_shares, circulating_shares, total_market_cap,
        circulating_market_cap, price, update_date
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        total_shares = VALUES(total_shares),
        circulating_shares = VALUES(circulating_shares),
        total_market_cap = VALUES(total_market_cap),
        circulating_market_cap = VALUES(circulating_market_cap),
        price = VALUES(price),
        updated_at = CURRENT_TIMESTAMP
"""

SELECT_MARKET_VALUE_DOLT = """
    SELECT * FROM stock_market_value 
    WHERE code = %s 
    ORDER BY update_date DESC 
    LIMIT 1
"""


# ============================================
# Supabase (PostgreSQL) SQL 语句
# ============================================

INSERT_MARKET_VALUE_SUPABASE = """
    INSERT INTO stock_market_value (
        code, total_shares, circulating_shares, total_market_cap,
        circulating_market_cap, price, update_date
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (code, update_date) DO UPDATE SET
        total_shares = EXCLUDED.total_shares,
        circulating_shares = EXCLUDED.circulating_shares,
        total_market_cap = EXCLUDED.total_market_cap,
        circulating_market_cap = EXCLUDED.circulating_market_cap,
        price = EXCLUDED.price,
        updated_at = CURRENT_TIMESTAMP
"""

SELECT_MARKET_VALUE_SUPABASE = """
    SELECT * FROM stock_market_value 
    WHERE code = %s 
    ORDER BY update_date DESC 
    LIMIT 1
"""
