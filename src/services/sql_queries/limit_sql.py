"""
涨跌停查询服务 SQL 查询语句

分别为 Dolt (MySQL) 和 Supabase (PostgreSQL) 提供 SQL 语句。
注意：这些 SQL 语句在 MySQL 和 PostgreSQL 中基本兼容。
"""

# ============================================
# Dolt (MySQL) SQL 语句
# ============================================

SELECT_LIMIT_STOCKS_DOLT = """
    SELECT 
        d.code,
        s.name,
        s.market,
        d.trade_date,
        d.open_price,
        d.high_price,
        d.low_price,
        d.close_price,
        d.volume,
        d.amount,
        d.turnover,
        prev.close_price as prev_close_price,
        CASE 
            WHEN d.code LIKE '60%%' THEN 0.10
            WHEN d.code LIKE '68%%' THEN 0.20
            WHEN d.code LIKE '00%%' THEN 0.10
            WHEN d.code LIKE '30%%' THEN 0.20
            WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
            ELSE 0.10
        END as limit_ratio,
        CASE 
            WHEN d.close_price >= prev.close_price * (1 + 
                CASE 
                    WHEN d.code LIKE '60%%' THEN 0.10
                    WHEN d.code LIKE '68%%' THEN 0.20
                    WHEN d.code LIKE '00%%' THEN 0.10
                    WHEN d.code LIKE '30%%' THEN 0.20
                    WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
                    ELSE 0.10
                END
            ) - 0.01 THEN '涨停'
            WHEN d.close_price <= prev.close_price * (1 - 
                CASE 
                    WHEN d.code LIKE '60%%' THEN 0.10
                    WHEN d.code LIKE '68%%' THEN 0.20
                    WHEN d.code LIKE '00%%' THEN 0.10
                    WHEN d.code LIKE '30%%' THEN 0.20
                    WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
                    ELSE 0.10
                END
            ) + 0.01 THEN '跌停'
            ELSE '正常'
        END as limit_status,
        ROUND((d.close_price - prev.close_price) / prev.close_price * 100, 2) as change_pct
    FROM stock_daily d
    INNER JOIN stocks s ON d.code = s.code
    INNER JOIN stock_daily prev ON d.code = prev.code 
        AND prev.trade_date = (
            SELECT MAX(trade_date) 
            FROM stock_daily 
            WHERE code = d.code 
            AND trade_date < d.trade_date
        )
    WHERE d.trade_date >= %s
    AND d.trade_date <= %s
    AND prev.close_price IS NOT NULL
    AND prev.close_price > 0
    HAVING limit_status IN ('涨停', '跌停')
    ORDER BY d.trade_date DESC, limit_status ASC, change_pct DESC
"""

SELECT_STOCK_LIMIT_DOLT = """
    SELECT 
        d.code,
        s.name,
        s.market,
        d.trade_date,
        d.open_price,
        d.high_price,
        d.low_price,
        d.close_price,
        d.volume,
        d.amount,
        d.turnover,
        prev.close_price as prev_close_price,
        CASE 
            WHEN d.code LIKE '60%%' THEN 0.10
            WHEN d.code LIKE '68%%' THEN 0.20
            WHEN d.code LIKE '00%%' THEN 0.10
            WHEN d.code LIKE '30%%' THEN 0.20
            WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
            ELSE 0.10
        END as limit_ratio,
        CASE 
            WHEN d.close_price >= prev.close_price * (1 + 
                CASE 
                    WHEN d.code LIKE '60%%' THEN 0.10
                    WHEN d.code LIKE '68%%' THEN 0.20
                    WHEN d.code LIKE '00%%' THEN 0.10
                    WHEN d.code LIKE '30%%' THEN 0.20
                    WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
                    ELSE 0.10
                END
            ) - 0.01 THEN '涨停'
            WHEN d.close_price <= prev.close_price * (1 - 
                CASE 
                    WHEN d.code LIKE '60%%' THEN 0.10
                    WHEN d.code LIKE '68%%' THEN 0.20
                    WHEN d.code LIKE '00%%' THEN 0.10
                    WHEN d.code LIKE '30%%' THEN 0.20
                    WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
                    ELSE 0.10
                END
            ) + 0.01 THEN '跌停'
            ELSE '正常'
        END as limit_status,
        ROUND((d.close_price - prev.close_price) / prev.close_price * 100, 2) as change_pct
    FROM stock_daily d
    INNER JOIN stocks s ON d.code = s.code
    INNER JOIN stock_daily prev ON d.code = prev.code 
        AND prev.trade_date = (
            SELECT MAX(trade_date) 
            FROM stock_daily 
            WHERE code = d.code 
            AND trade_date < d.trade_date
        )
    WHERE d.code = %s
    AND d.trade_date >= %s
    AND d.trade_date <= %s
    AND prev.close_price IS NOT NULL
    AND prev.close_price > 0
    HAVING limit_status IN ('涨停', '跌停')
    ORDER BY d.trade_date DESC, limit_status ASC, change_pct DESC
"""


# ============================================
# Supabase (PostgreSQL) SQL 语句
# ============================================
# 注意：PostgreSQL 的 LIKE 语法与 MySQL 相同，但需要使用 ESCAPE 或不同的转义方式
# 这里使用 PostgreSQL 的 SIMILAR TO 或保持 LIKE（PostgreSQL 也支持 LIKE）

SELECT_LIMIT_STOCKS_SUPABASE = """
    SELECT 
        d.code,
        s.name,
        s.market,
        d.trade_date,
        d.open_price,
        d.high_price,
        d.low_price,
        d.close_price,
        d.volume,
        d.amount,
        d.turnover,
        prev.close_price as prev_close_price,
        CASE 
            WHEN d.code LIKE '60%%' THEN 0.10
            WHEN d.code LIKE '68%%' THEN 0.20
            WHEN d.code LIKE '00%%' THEN 0.10
            WHEN d.code LIKE '30%%' THEN 0.20
            WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
            ELSE 0.10
        END as limit_ratio,
        CASE 
            WHEN d.close_price >= prev.close_price * (1 + 
                CASE 
                    WHEN d.code LIKE '60%%' THEN 0.10
                    WHEN d.code LIKE '68%%' THEN 0.20
                    WHEN d.code LIKE '00%%' THEN 0.10
                    WHEN d.code LIKE '30%%' THEN 0.20
                    WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
                    ELSE 0.10
                END
            ) - 0.01 THEN '涨停'
            WHEN d.close_price <= prev.close_price * (1 - 
                CASE 
                    WHEN d.code LIKE '60%%' THEN 0.10
                    WHEN d.code LIKE '68%%' THEN 0.20
                    WHEN d.code LIKE '00%%' THEN 0.10
                    WHEN d.code LIKE '30%%' THEN 0.20
                    WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
                    ELSE 0.10
                END
            ) + 0.01 THEN '跌停'
            ELSE '正常'
        END as limit_status,
        ROUND((d.close_price - prev.close_price) / prev.close_price * 100, 2) as change_pct
    FROM stock_daily d
    INNER JOIN stocks s ON d.code = s.code
    INNER JOIN stock_daily prev ON d.code = prev.code 
        AND prev.trade_date = (
            SELECT MAX(trade_date) 
            FROM stock_daily 
            WHERE code = d.code 
            AND trade_date < d.trade_date
        )
    WHERE d.trade_date >= %s
    AND d.trade_date <= %s
    AND prev.close_price IS NOT NULL
    AND prev.close_price > 0
    HAVING limit_status IN ('涨停', '跌停')
    ORDER BY d.trade_date DESC, limit_status ASC, change_pct DESC
"""

SELECT_STOCK_LIMIT_SUPABASE = """
    SELECT 
        d.code,
        s.name,
        s.market,
        d.trade_date,
        d.open_price,
        d.high_price,
        d.low_price,
        d.close_price,
        d.volume,
        d.amount,
        d.turnover,
        prev.close_price as prev_close_price,
        CASE 
            WHEN d.code LIKE '60%%' THEN 0.10
            WHEN d.code LIKE '68%%' THEN 0.20
            WHEN d.code LIKE '00%%' THEN 0.10
            WHEN d.code LIKE '30%%' THEN 0.20
            WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
            ELSE 0.10
        END as limit_ratio,
        CASE 
            WHEN d.close_price >= prev.close_price * (1 + 
                CASE 
                    WHEN d.code LIKE '60%%' THEN 0.10
                    WHEN d.code LIKE '68%%' THEN 0.20
                    WHEN d.code LIKE '00%%' THEN 0.10
                    WHEN d.code LIKE '30%%' THEN 0.20
                    WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
                    ELSE 0.10
                END
            ) - 0.01 THEN '涨停'
            WHEN d.close_price <= prev.close_price * (1 - 
                CASE 
                    WHEN d.code LIKE '60%%' THEN 0.10
                    WHEN d.code LIKE '68%%' THEN 0.20
                    WHEN d.code LIKE '00%%' THEN 0.10
                    WHEN d.code LIKE '30%%' THEN 0.20
                    WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
                    ELSE 0.10
                END
            ) + 0.01 THEN '跌停'
            ELSE '正常'
        END as limit_status,
        ROUND((d.close_price - prev.close_price) / prev.close_price * 100, 2) as change_pct
    FROM stock_daily d
    INNER JOIN stocks s ON d.code = s.code
    INNER JOIN stock_daily prev ON d.code = prev.code 
        AND prev.trade_date = (
            SELECT MAX(trade_date) 
            FROM stock_daily 
            WHERE code = d.code 
            AND trade_date < d.trade_date
        )
    WHERE d.code = %s
    AND d.trade_date >= %s
    AND d.trade_date <= %s
    AND prev.close_price IS NOT NULL
    AND prev.close_price > 0
    HAVING limit_status IN ('涨停', '跌停')
    ORDER BY d.trade_date DESC, limit_status ASC, change_pct DESC
"""
