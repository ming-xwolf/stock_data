"""
ETF 服务 SQL 查询语句

提供 Supabase (PostgreSQL) 数据库的 SQL 语句。
"""

INSERT_ETF = """
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

SELECT_ETF = "SELECT * FROM etf_funds WHERE code = %s"

SELECT_ALL_ETFS = "SELECT * FROM etf_funds ORDER BY code"

COUNT_ETFS = "SELECT COUNT(*) as count FROM etf_funds"
