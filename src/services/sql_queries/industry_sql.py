"""
行业数据服务 SQL 查询语句

分别为 Dolt (MySQL) 和 Supabase (PostgreSQL) 提供 SQL 语句。
"""

# ============================================
# Dolt (MySQL) SQL 语句
# ============================================

INSERT_INDUSTRY_DOLT = """
    INSERT INTO stock_industry (code, industry_name, industry_code, concept, area, update_date)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        industry_name = VALUES(industry_name),
        industry_code = VALUES(industry_code),
        concept = VALUES(concept),
        area = VALUES(area),
        update_date = VALUES(update_date),
        updated_at = CURRENT_TIMESTAMP
"""

SELECT_INDUSTRY_DOLT = "SELECT * FROM stock_industry WHERE code = %s"


# ============================================
# Supabase (PostgreSQL) SQL 语句
# ============================================

INSERT_INDUSTRY_SUPABASE = """
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

SELECT_INDUSTRY_SUPABASE = "SELECT * FROM stock_industry WHERE code = %s"
