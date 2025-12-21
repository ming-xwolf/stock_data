"""
ETF 净值服务 SQL 查询语句

提供 Supabase (PostgreSQL) 数据库的 SQL 语句。
"""

INSERT_NET_VALUE = """
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

SELECT_LATEST_DATE = """
    SELECT MAX(net_value_date) as latest_date 
    FROM etf_net_value 
    WHERE code = %s
"""

SELECT_NET_VALUE = """
    SELECT * FROM etf_net_value 
    WHERE code = %s AND net_value_date >= %s AND net_value_date <= %s
    ORDER BY net_value_date
"""

COUNT_NET_VALUE = """
    SELECT COUNT(*) as count 
    FROM etf_net_value 
    WHERE code = %s
"""

# 查询需要更新的 ETF 列表（缺少最新交易日净值数据的 ETF）
# 只考虑今天或今天以前的交易日
SELECT_ETFS_NEED_UPDATE = """
    WITH latest_trading_date AS (
        SELECT MAX(trade_date) as latest_date 
        FROM trading_calendar
        WHERE trade_date <= CURRENT_DATE
    ),
    etf_latest_dates AS (
        SELECT 
            e.code,
            COALESCE(MAX(n.net_value_date), '1900-01-01'::date) as latest_net_value_date
        FROM etf_funds e
        LEFT JOIN etf_net_value n ON e.code = n.code
        GROUP BY e.code
    )
    SELECT 
        e.code,
        f.name,
        e.latest_net_value_date,
        t.latest_date as latest_trading_date,
        CASE 
            WHEN e.latest_net_value_date < t.latest_date THEN 
                (e.latest_net_value_date + INTERVAL '1 day')::date
            ELSE NULL
        END as start_date
    FROM etf_latest_dates e
    CROSS JOIN latest_trading_date t
    LEFT JOIN etf_funds f ON e.code = f.code
    WHERE e.latest_net_value_date < t.latest_date
    ORDER BY e.code
"""
