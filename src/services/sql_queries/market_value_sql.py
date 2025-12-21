"""
市值数据服务 SQL 查询语句

提供 Supabase (PostgreSQL) 数据库的 SQL 语句。
"""

INSERT_MARKET_VALUE = """
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

SELECT_MARKET_VALUE = """
    SELECT * FROM stock_market_value 
    WHERE code = %s 
    ORDER BY update_date DESC 
    LIMIT 1
"""
