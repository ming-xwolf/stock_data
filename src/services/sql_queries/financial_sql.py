"""
财务数据服务 SQL 查询语句

分别为 Dolt (MySQL) 和 Supabase (PostgreSQL) 提供 SQL 语句。
"""

# ============================================
# Dolt (MySQL) SQL 语句
# ============================================

INSERT_INCOME_DOLT = """
    INSERT INTO stock_financial_income (
        code, report_date, report_period, report_type,
        total_revenue, operating_revenue, operating_cost,
        operating_profit, total_profit, net_profit,
        net_profit_attributable, basic_eps, diluted_eps
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        report_period = VALUES(report_period),
        report_type = VALUES(report_type),
        total_revenue = VALUES(total_revenue),
        operating_revenue = VALUES(operating_revenue),
        operating_cost = VALUES(operating_cost),
        operating_profit = VALUES(operating_profit),
        total_profit = VALUES(total_profit),
        net_profit = VALUES(net_profit),
        net_profit_attributable = VALUES(net_profit_attributable),
        basic_eps = VALUES(basic_eps),
        diluted_eps = VALUES(diluted_eps),
        updated_at = CURRENT_TIMESTAMP
"""

SELECT_INCOME_COUNT_DOLT = """
    SELECT COUNT(*) as count, MAX(report_date) as latest_date
    FROM stock_financial_income
    WHERE code = %s
"""

SELECT_INCOME_DATES_DOLT = """
    SELECT report_date
    FROM stock_financial_income
    WHERE code = %s
    ORDER BY report_date DESC
"""

SELECT_LATEST_INCOME_DOLT = """
    SELECT report_date, report_period, report_type
    FROM stock_financial_income
    WHERE code = %s
    ORDER BY report_date DESC
    LIMIT 1
"""

SELECT_STOCKS_WITHOUT_REPORT_DATE_DOLT = """
    SELECT DISTINCT s.code
    FROM stocks s
    LEFT JOIN stock_financial_income i ON s.code = i.code AND i.report_date = %s
    WHERE i.code IS NULL
    ORDER BY s.code
"""


# ============================================
# Supabase (PostgreSQL) SQL 语句
# ============================================

INSERT_INCOME_SUPABASE = """
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

SELECT_INCOME_COUNT_SUPABASE = """
    SELECT COUNT(*) as count, MAX(report_date) as latest_date
    FROM stock_financial_income
    WHERE code = %s
"""

SELECT_INCOME_DATES_SUPABASE = """
    SELECT report_date
    FROM stock_financial_income
    WHERE code = %s
    ORDER BY report_date DESC
"""

SELECT_LATEST_INCOME_SUPABASE = """
    SELECT report_date, report_period, report_type
    FROM stock_financial_income
    WHERE code = %s
    ORDER BY report_date DESC
    LIMIT 1
"""

SELECT_STOCKS_WITHOUT_REPORT_DATE_SUPABASE = """
    SELECT DISTINCT s.code
    FROM stocks s
    LEFT JOIN stock_financial_income i ON s.code = i.code AND i.report_date = %s
    WHERE i.code IS NULL
    ORDER BY s.code
"""
