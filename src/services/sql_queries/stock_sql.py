"""
股票服务 SQL 查询语句

提供 Supabase (PostgreSQL) 数据库的 SQL 语句。
"""

INSERT_STOCK = """
    INSERT INTO stocks (code, name, market, list_date)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (code) DO UPDATE SET
        name = EXCLUDED.name,
        market = EXCLUDED.market,
        list_date = EXCLUDED.list_date,
        updated_at = CURRENT_TIMESTAMP
"""

UPDATE_COMPANY_INFO = """
    UPDATE stocks 
    SET company_type = %s,
        actual_controller = %s,
        direct_controller = %s,
        main_business = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE code = %s
"""

SELECT_STOCK = "SELECT * FROM stocks WHERE code = %s"

SELECT_ALL_STOCKS = "SELECT * FROM stocks ORDER BY code"

COUNT_STOCKS = "SELECT COUNT(*) as count FROM stocks"
