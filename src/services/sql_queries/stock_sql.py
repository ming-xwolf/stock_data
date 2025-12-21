"""
股票服务 SQL 查询语句

分别为 Dolt (MySQL) 和 Supabase (PostgreSQL) 提供 SQL 语句。
"""

# ============================================
# Dolt (MySQL) SQL 语句
# ============================================

INSERT_STOCK_DOLT = """
    INSERT INTO stocks (code, name, market, list_date)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        market = VALUES(market),
        list_date = VALUES(list_date),
        updated_at = CURRENT_TIMESTAMP
"""

UPDATE_COMPANY_INFO_DOLT = """
    UPDATE stocks 
    SET company_type = %s,
        actual_controller = %s,
        direct_controller = %s,
        main_business = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE code = %s
"""

SELECT_STOCK_DOLT = "SELECT * FROM stocks WHERE code = %s"

SELECT_ALL_STOCKS_DOLT = "SELECT * FROM stocks ORDER BY code"

COUNT_STOCKS_DOLT = "SELECT COUNT(*) as count FROM stocks"


# ============================================
# Supabase (PostgreSQL) SQL 语句
# ============================================

INSERT_STOCK_SUPABASE = """
    INSERT INTO stocks (code, name, market, list_date)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (code) DO UPDATE SET
        name = EXCLUDED.name,
        market = EXCLUDED.market,
        list_date = EXCLUDED.list_date,
        updated_at = CURRENT_TIMESTAMP
"""

UPDATE_COMPANY_INFO_SUPABASE = """
    UPDATE stocks 
    SET company_type = %s,
        actual_controller = %s,
        direct_controller = %s,
        main_business = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE code = %s
"""

SELECT_STOCK_SUPABASE = "SELECT * FROM stocks WHERE code = %s"

SELECT_ALL_STOCKS_SUPABASE = "SELECT * FROM stocks ORDER BY code"

COUNT_STOCKS_SUPABASE = "SELECT COUNT(*) as count FROM stocks"
