"""
股东数据服务 SQL 查询语句

提供 Supabase (PostgreSQL) 数据库的 SQL 语句。
"""

INSERT_SHAREHOLDER = """
    INSERT INTO stock_shareholders (
        code, shareholder_name, shareholder_type, holding_ratio, holding_amount,
        change_amount, change_ratio, report_date, report_period
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (code, shareholder_name, report_date) DO UPDATE SET
        shareholder_type = EXCLUDED.shareholder_type,
        holding_ratio = EXCLUDED.holding_ratio,
        holding_amount = EXCLUDED.holding_amount,
        change_amount = EXCLUDED.change_amount,
        change_ratio = EXCLUDED.change_ratio,
        report_period = EXCLUDED.report_period
"""

SELECT_SHAREHOLDERS = """
    SELECT * FROM stock_shareholders 
    WHERE code = %s AND report_date = %s
    ORDER BY holding_ratio DESC
"""

SELECT_LATEST_SHAREHOLDERS = """
    SELECT * FROM stock_shareholders 
    WHERE code = %s 
    AND report_date = (SELECT MAX(report_date) FROM stock_shareholders WHERE code = %s)
    ORDER BY holding_ratio DESC
"""
