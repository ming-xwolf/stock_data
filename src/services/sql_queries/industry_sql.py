"""
行业数据服务 SQL 查询语句

提供 Supabase (PostgreSQL) 数据库的 SQL 语句。
"""

INSERT_INDUSTRY = """
    INSERT INTO stock_industry (code, industry_name, industry_code, concept, area, update_date)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (code) DO UPDATE SET
        industry_name = EXCLUDED.industry_name,
        industry_code = EXCLUDED.industry_code,
        concept = EXCLUDED.concept,
        area = EXCLUDED.area,
        update_date = EXCLUDED.update_date,
        updated_at = CURRENT_TIMESTAMP
"""

SELECT_INDUSTRY = "SELECT * FROM stock_industry WHERE code = %s"
