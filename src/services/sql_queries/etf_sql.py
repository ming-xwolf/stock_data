"""
ETF 服务 SQL 查询语句

分别为 Dolt (MySQL) 和 Supabase (PostgreSQL) 提供 SQL 语句。
"""

# ============================================
# Dolt (MySQL) SQL 语句
# ============================================

INSERT_ETF_DOLT = """
    INSERT INTO etf_funds (code, name, fund_type, fund_company, listing_date, 
                          tracking_index, management_fee, custodian_fee, exchange)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        fund_type = VALUES(fund_type),
        fund_company = VALUES(fund_company),
        listing_date = VALUES(listing_date),
        tracking_index = VALUES(tracking_index),
        management_fee = VALUES(management_fee),
        custodian_fee = VALUES(custodian_fee),
        exchange = VALUES(exchange),
        updated_at = CURRENT_TIMESTAMP
"""

SELECT_ETF_DOLT = "SELECT * FROM etf_funds WHERE code = %s"

SELECT_ALL_ETFS_DOLT = "SELECT * FROM etf_funds ORDER BY code"

COUNT_ETFS_DOLT = "SELECT COUNT(*) as count FROM etf_funds"


# ============================================
# Supabase (PostgreSQL) SQL 语句
# ============================================

INSERT_ETF_SUPABASE = """
    INSERT INTO etf_funds (code, name, fund_type, fund_company, listing_date, 
                          tracking_index, management_fee, custodian_fee, exchange)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (code) DO UPDATE SET
        name = EXCLUDED.name,
        fund_type = EXCLUDED.fund_type,
        fund_company = EXCLUDED.fund_company,
        listing_date = EXCLUDED.listing_date,
        tracking_index = EXCLUDED.tracking_index,
        management_fee = EXCLUDED.management_fee,
        custodian_fee = EXCLUDED.custodian_fee,
        exchange = EXCLUDED.exchange,
        updated_at = CURRENT_TIMESTAMP
"""

SELECT_ETF_SUPABASE = "SELECT * FROM etf_funds WHERE code = %s"

SELECT_ALL_ETFS_SUPABASE = "SELECT * FROM etf_funds ORDER BY code"

COUNT_ETFS_SUPABASE = "SELECT COUNT(*) as count FROM etf_funds"
