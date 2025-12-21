"""
财务数据服务 SQL 查询语句

提供 Supabase (PostgreSQL) 数据库的 SQL 语句。
"""

INSERT_INCOME = """
    INSERT INTO stock_financial_income (
        code, report_date, report_period, report_type,
        total_revenue, operating_revenue, operating_cost,
        operating_profit, total_profit, net_profit,
        net_profit_attributable, basic_eps, diluted_eps
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (code, report_date, report_type) DO UPDATE SET
        report_period = EXCLUDED.report_period,
        report_type = EXCLUDED.report_type,
        total_revenue = EXCLUDED.total_revenue,
        operating_revenue = EXCLUDED.operating_revenue,
        operating_cost = EXCLUDED.operating_cost,
        operating_profit = EXCLUDED.operating_profit,
        total_profit = EXCLUDED.total_profit,
        net_profit = EXCLUDED.net_profit,
        net_profit_attributable = EXCLUDED.net_profit_attributable,
        basic_eps = EXCLUDED.basic_eps,
        diluted_eps = EXCLUDED.diluted_eps,
        updated_at = CURRENT_TIMESTAMP
"""

SELECT_INCOME_COUNT = """
    SELECT COUNT(*) as count, MAX(report_date) as latest_date
    FROM stock_financial_income
    WHERE code = %s
"""

SELECT_INCOME_DATES = """
    SELECT report_date
    FROM stock_financial_income
    WHERE code = %s
    ORDER BY report_date DESC
"""

SELECT_LATEST_INCOME = """
    SELECT report_date, report_period, report_type
    FROM stock_financial_income
    WHERE code = %s
    ORDER BY report_date DESC
    LIMIT 1
"""

SELECT_STOCKS_WITHOUT_REPORT_DATE = """
    SELECT DISTINCT s.code
    FROM stocks s
    LEFT JOIN stock_financial_income i ON s.code = i.code AND i.report_date = %s
    WHERE i.code IS NULL
    ORDER BY s.code
"""
