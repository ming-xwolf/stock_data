"""
ETF 净值服务 SQL 查询语句

分别为 Dolt (MySQL) 和 Supabase (PostgreSQL) 提供 SQL 语句。
"""

# ============================================
# Dolt (MySQL) SQL 语句
# ============================================

INSERT_NET_VALUE_DOLT = """
    INSERT INTO etf_net_value (code, net_value_date, unit_net_value, accumulated_net_value,
                              daily_growth_rate, subscription_status, redemption_status)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        unit_net_value = VALUES(unit_net_value),
        accumulated_net_value = VALUES(accumulated_net_value),
        daily_growth_rate = VALUES(daily_growth_rate),
        subscription_status = VALUES(subscription_status),
        redemption_status = VALUES(redemption_status),
        updated_at = CURRENT_TIMESTAMP
"""

SELECT_LATEST_DATE_DOLT = """
    SELECT MAX(net_value_date) as latest_date 
    FROM etf_net_value 
    WHERE code = %s
"""

SELECT_NET_VALUE_DOLT = """
    SELECT * FROM etf_net_value 
    WHERE code = %s AND net_value_date >= %s AND net_value_date <= %s
    ORDER BY net_value_date
"""

COUNT_NET_VALUE_DOLT = """
    SELECT COUNT(*) as count 
    FROM etf_net_value 
    WHERE code = %s
"""


# ============================================
# Supabase (PostgreSQL) SQL 语句
# ============================================

INSERT_NET_VALUE_SUPABASE = """
    INSERT INTO etf_net_value (code, net_value_date, unit_net_value, accumulated_net_value,
                              daily_growth_rate, subscription_status, redemption_status)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (code, net_value_date) DO UPDATE SET
        unit_net_value = EXCLUDED.unit_net_value,
        accumulated_net_value = EXCLUDED.accumulated_net_value,
        daily_growth_rate = EXCLUDED.daily_growth_rate,
        subscription_status = EXCLUDED.subscription_status,
        redemption_status = EXCLUDED.redemption_status,
        updated_at = CURRENT_TIMESTAMP
"""

SELECT_LATEST_DATE_SUPABASE = """
    SELECT MAX(net_value_date) as latest_date 
    FROM etf_net_value 
    WHERE code = %s
"""

SELECT_NET_VALUE_SUPABASE = """
    SELECT * FROM etf_net_value 
    WHERE code = %s AND net_value_date >= %s AND net_value_date <= %s
    ORDER BY net_value_date
"""

COUNT_NET_VALUE_SUPABASE = """
    SELECT COUNT(*) as count 
    FROM etf_net_value 
    WHERE code = %s
"""
