-- 数据库初始化脚本：创建所有表结构（Supabase/PostgreSQL 版本）
-- 创建时间: 2025-12-12
-- 说明: 此脚本包含所有表的完整CREATE TABLE语句，用于在 Supabase 中创建数据库

-- ============================================
-- 1. stocks - 股票基本信息表
-- ============================================
CREATE TABLE IF NOT EXISTS stocks (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    market VARCHAR(10),
    list_date DATE,
    company_type VARCHAR(50),
    actual_controller VARCHAR(200),
    direct_controller VARCHAR(200),
    main_business TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE stocks IS '股票基本信息表';
COMMENT ON COLUMN stocks.code IS '股票代码';
COMMENT ON COLUMN stocks.name IS '股票名称';
COMMENT ON COLUMN stocks.market IS '市场（SH/SZ）';
COMMENT ON COLUMN stocks.list_date IS '上市日期';
COMMENT ON COLUMN stocks.company_type IS '企业性质（如：央企国资控股、民企、外资等）';
COMMENT ON COLUMN stocks.actual_controller IS '实际控制人';
COMMENT ON COLUMN stocks.direct_controller IS '直接控制人';
COMMENT ON COLUMN stocks.main_business IS '主营产品/主营业务';
COMMENT ON COLUMN stocks.created_at IS '创建时间';
COMMENT ON COLUMN stocks.updated_at IS '更新时间';

CREATE INDEX IF NOT EXISTS idx_stocks_market ON stocks(market);
CREATE INDEX IF NOT EXISTS idx_stocks_name ON stocks(name);
CREATE INDEX IF NOT EXISTS idx_stocks_company_type ON stocks(company_type);
CREATE INDEX IF NOT EXISTS idx_stocks_actual_controller ON stocks(actual_controller);
CREATE INDEX IF NOT EXISTS idx_stocks_direct_controller ON stocks(direct_controller);

-- ============================================
-- 2. stock_daily - 股票日线数据表
-- ============================================
CREATE TABLE IF NOT EXISTS stock_daily (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    open_price DECIMAL(10,2),
    high_price DECIMAL(10,2),
    low_price DECIMAL(10,2),
    close_price DECIMAL(10,2),
    volume BIGINT,
    amount DECIMAL(20,2),
    outstanding_share BIGINT,
    turnover DECIMAL(10,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE stock_daily IS '股票日线数据表';
COMMENT ON COLUMN stock_daily.id IS '主键ID';
COMMENT ON COLUMN stock_daily.code IS '股票代码';
COMMENT ON COLUMN stock_daily.trade_date IS '交易日期';
COMMENT ON COLUMN stock_daily.open_price IS '开盘价';
COMMENT ON COLUMN stock_daily.high_price IS '最高价';
COMMENT ON COLUMN stock_daily.low_price IS '最低价';
COMMENT ON COLUMN stock_daily.close_price IS '收盘价';
COMMENT ON COLUMN stock_daily.volume IS '成交量';
COMMENT ON COLUMN stock_daily.amount IS '成交额';
COMMENT ON COLUMN stock_daily.outstanding_share IS '流通股本（股）';
COMMENT ON COLUMN stock_daily.turnover IS '换手率（%）';
COMMENT ON COLUMN stock_daily.created_at IS '创建时间';

CREATE INDEX IF NOT EXISTS idx_stock_daily_code ON stock_daily(code);
CREATE INDEX IF NOT EXISTS idx_stock_daily_trade_date ON stock_daily(trade_date);
CREATE UNIQUE INDEX IF NOT EXISTS uk_stock_daily_code_date ON stock_daily(code, trade_date);

-- ============================================
-- 3. stock_industry - 股票行业信息表
-- ============================================
CREATE TABLE IF NOT EXISTS stock_industry (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    industry_name VARCHAR(100),
    industry_code VARCHAR(20),
    concept VARCHAR(200),
    area VARCHAR(50),
    update_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE stock_industry IS '股票行业信息表';
COMMENT ON COLUMN stock_industry.id IS '主键ID';
COMMENT ON COLUMN stock_industry.code IS '股票代码';
COMMENT ON COLUMN stock_industry.industry_name IS '行业名称';
COMMENT ON COLUMN stock_industry.industry_code IS '行业代码';
COMMENT ON COLUMN stock_industry.concept IS '概念板块';
COMMENT ON COLUMN stock_industry.area IS '地区';
COMMENT ON COLUMN stock_industry.update_date IS '更新日期';
COMMENT ON COLUMN stock_industry.created_at IS '创建时间';
COMMENT ON COLUMN stock_industry.updated_at IS '更新时间';

CREATE INDEX IF NOT EXISTS idx_stock_industry_code ON stock_industry(code);
CREATE INDEX IF NOT EXISTS idx_stock_industry_industry_name ON stock_industry(industry_name);
CREATE INDEX IF NOT EXISTS idx_stock_industry_update_date ON stock_industry(update_date);
CREATE UNIQUE INDEX IF NOT EXISTS uk_stock_industry_code ON stock_industry(code);

-- ============================================
-- 4. stock_shareholders - 股票股东信息表
-- ============================================
CREATE TABLE IF NOT EXISTS stock_shareholders (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    shareholder_name VARCHAR(200) NOT NULL,
    shareholder_type VARCHAR(50),
    holding_ratio DECIMAL(10,4),
    holding_amount BIGINT,
    change_amount BIGINT,
    change_ratio DECIMAL(10,4),
    report_date DATE NOT NULL,
    report_period VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE stock_shareholders IS '股票股东信息表';
COMMENT ON COLUMN stock_shareholders.id IS '主键ID';
COMMENT ON COLUMN stock_shareholders.code IS '股票代码';
COMMENT ON COLUMN stock_shareholders.shareholder_name IS '股东名称';
COMMENT ON COLUMN stock_shareholders.shareholder_type IS '股东类型（个人/机构/法人）';
COMMENT ON COLUMN stock_shareholders.holding_ratio IS '持股比例（%）';
COMMENT ON COLUMN stock_shareholders.holding_amount IS '持股数量（股）';
COMMENT ON COLUMN stock_shareholders.change_amount IS '持股变化（股）';
COMMENT ON COLUMN stock_shareholders.change_ratio IS '持股变化比例（%）';
COMMENT ON COLUMN stock_shareholders.report_date IS '报告日期';
COMMENT ON COLUMN stock_shareholders.report_period IS '报告期（如：2024Q1）';
COMMENT ON COLUMN stock_shareholders.created_at IS '创建时间';

CREATE INDEX IF NOT EXISTS idx_stock_shareholders_code ON stock_shareholders(code);
CREATE INDEX IF NOT EXISTS idx_stock_shareholders_report_date ON stock_shareholders(report_date);
CREATE INDEX IF NOT EXISTS idx_stock_shareholders_shareholder_name ON stock_shareholders(shareholder_name);
CREATE UNIQUE INDEX IF NOT EXISTS uk_stock_shareholders_code_date_name ON stock_shareholders(code, report_date, shareholder_name);

-- ============================================
-- 5. stock_market_value - 股票市值信息表
-- ============================================
CREATE TABLE IF NOT EXISTS stock_market_value (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    total_shares BIGINT,
    circulating_shares BIGINT,
    total_market_cap DECIMAL(20,2),
    circulating_market_cap DECIMAL(20,2),
    price DECIMAL(10,2),
    update_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE stock_market_value IS '股票市值信息表';
COMMENT ON COLUMN stock_market_value.id IS '主键ID';
COMMENT ON COLUMN stock_market_value.code IS '股票代码';
COMMENT ON COLUMN stock_market_value.total_shares IS '总股本（股）';
COMMENT ON COLUMN stock_market_value.circulating_shares IS '流通股本（股）';
COMMENT ON COLUMN stock_market_value.total_market_cap IS '总市值（元）';
COMMENT ON COLUMN stock_market_value.circulating_market_cap IS '流通市值（元）';
COMMENT ON COLUMN stock_market_value.price IS '当前价格（元）';
COMMENT ON COLUMN stock_market_value.update_date IS '更新日期';
COMMENT ON COLUMN stock_market_value.created_at IS '创建时间';
COMMENT ON COLUMN stock_market_value.updated_at IS '更新时间';

CREATE INDEX IF NOT EXISTS idx_stock_market_value_code ON stock_market_value(code);
CREATE INDEX IF NOT EXISTS idx_stock_market_value_update_date ON stock_market_value(update_date);
CREATE UNIQUE INDEX IF NOT EXISTS uk_stock_market_value_code_date ON stock_market_value(code, update_date);

-- ============================================
-- 6. stock_financial_income - 股票财务数据表（利润表）
-- ============================================
CREATE TABLE IF NOT EXISTS stock_financial_income (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    report_period VARCHAR(20),
    report_type VARCHAR(20),
    total_revenue DECIMAL(20,2),
    operating_revenue DECIMAL(20,2),
    operating_cost DECIMAL(20,2),
    operating_profit DECIMAL(20,2),
    total_profit DECIMAL(20,2),
    net_profit DECIMAL(20,2),
    net_profit_attributable DECIMAL(20,2),
    basic_eps DECIMAL(10,4),
    diluted_eps DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE stock_financial_income IS '股票财务数据表-利润表';
COMMENT ON COLUMN stock_financial_income.id IS '主键ID';
COMMENT ON COLUMN stock_financial_income.code IS '股票代码';
COMMENT ON COLUMN stock_financial_income.report_date IS '报告日期';
COMMENT ON COLUMN stock_financial_income.report_period IS '报告期（如：2024Q1, 2024）';
COMMENT ON COLUMN stock_financial_income.report_type IS '报告类型（年报/中报/季报）';
COMMENT ON COLUMN stock_financial_income.total_revenue IS '营业总收入（元）';
COMMENT ON COLUMN stock_financial_income.operating_revenue IS '营业收入（元）';
COMMENT ON COLUMN stock_financial_income.operating_cost IS '营业成本（元）';
COMMENT ON COLUMN stock_financial_income.operating_profit IS '营业利润（元）';
COMMENT ON COLUMN stock_financial_income.total_profit IS '利润总额（元）';
COMMENT ON COLUMN stock_financial_income.net_profit IS '净利润（元）';
COMMENT ON COLUMN stock_financial_income.net_profit_attributable IS '归属于母公司所有者的净利润（元）';
COMMENT ON COLUMN stock_financial_income.basic_eps IS '基本每股收益（元）';
COMMENT ON COLUMN stock_financial_income.diluted_eps IS '稀释每股收益（元）';
COMMENT ON COLUMN stock_financial_income.created_at IS '创建时间';
COMMENT ON COLUMN stock_financial_income.updated_at IS '更新时间';

CREATE INDEX IF NOT EXISTS idx_stock_financial_income_code ON stock_financial_income(code);
CREATE INDEX IF NOT EXISTS idx_stock_financial_income_report_date ON stock_financial_income(report_date);
CREATE UNIQUE INDEX IF NOT EXISTS uk_stock_financial_income_code_date ON stock_financial_income(code, report_date);

-- ============================================
-- 7. trading_calendar - A股交易日历表
-- ============================================
CREATE TABLE IF NOT EXISTS trading_calendar (
    trade_date DATE PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE trading_calendar IS 'A股交易日历表';
COMMENT ON COLUMN trading_calendar.trade_date IS '交易日期';
COMMENT ON COLUMN trading_calendar.created_at IS '创建时间';
COMMENT ON COLUMN trading_calendar.updated_at IS '更新时间';

CREATE INDEX IF NOT EXISTS idx_trading_calendar_trade_date ON trading_calendar(trade_date);

-- ============================================
-- 8. etf_funds - ETF 基金基本信息表
-- ============================================
CREATE TABLE IF NOT EXISTS etf_funds (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    fund_type VARCHAR(50),
    fund_company VARCHAR(100),
    listing_date DATE,
    tracking_index VARCHAR(100),
    management_fee DECIMAL(6,4),
    custodian_fee DECIMAL(6,4),
    exchange VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE etf_funds IS 'ETF基金基本信息表';
COMMENT ON COLUMN etf_funds.code IS 'ETF基金代码';
COMMENT ON COLUMN etf_funds.name IS 'ETF基金名称';
COMMENT ON COLUMN etf_funds.fund_type IS '基金类型（如：股票型ETF、债券型ETF等）';
COMMENT ON COLUMN etf_funds.fund_company IS '基金管理公司';
COMMENT ON COLUMN etf_funds.listing_date IS '上市日期';
COMMENT ON COLUMN etf_funds.tracking_index IS '跟踪指数';
COMMENT ON COLUMN etf_funds.management_fee IS '管理费率（%）';
COMMENT ON COLUMN etf_funds.custodian_fee IS '托管费率（%）';
COMMENT ON COLUMN etf_funds.exchange IS '交易所（SH/SZ）';
COMMENT ON COLUMN etf_funds.created_at IS '创建时间';
COMMENT ON COLUMN etf_funds.updated_at IS '更新时间';

CREATE INDEX IF NOT EXISTS idx_etf_funds_name ON etf_funds(name);
CREATE INDEX IF NOT EXISTS idx_etf_funds_fund_company ON etf_funds(fund_company);
CREATE INDEX IF NOT EXISTS idx_etf_funds_tracking_index ON etf_funds(tracking_index);
CREATE INDEX IF NOT EXISTS idx_etf_funds_exchange ON etf_funds(exchange);

-- ============================================
-- 9. etf_daily - ETF 日线行情数据表
-- ============================================
CREATE TABLE IF NOT EXISTS etf_daily (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    open_price DECIMAL(10,4),
    high_price DECIMAL(10,4),
    low_price DECIMAL(10,4),
    close_price DECIMAL(10,4),
    volume BIGINT,
    amount DECIMAL(25,2),
    change_amount DECIMAL(10,4),
    change_rate DECIMAL(14,4),
    turnover DECIMAL(14,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE etf_daily IS 'ETF日线行情数据表';
COMMENT ON COLUMN etf_daily.id IS '主键ID';
COMMENT ON COLUMN etf_daily.code IS 'ETF基金代码';
COMMENT ON COLUMN etf_daily.trade_date IS '交易日期';
COMMENT ON COLUMN etf_daily.open_price IS '开盘价（元）';
COMMENT ON COLUMN etf_daily.high_price IS '最高价（元）';
COMMENT ON COLUMN etf_daily.low_price IS '最低价（元）';
COMMENT ON COLUMN etf_daily.close_price IS '收盘价（元）';
COMMENT ON COLUMN etf_daily.volume IS '成交量（手）';
COMMENT ON COLUMN etf_daily.amount IS '成交额（元）';
COMMENT ON COLUMN etf_daily.change_amount IS '涨跌额（元）';
COMMENT ON COLUMN etf_daily.change_rate IS '涨跌幅（%）';
COMMENT ON COLUMN etf_daily.turnover IS '换手率（%）';
COMMENT ON COLUMN etf_daily.created_at IS '创建时间';

CREATE INDEX IF NOT EXISTS idx_etf_daily_code ON etf_daily(code);
CREATE INDEX IF NOT EXISTS idx_etf_daily_trade_date ON etf_daily(trade_date);
CREATE UNIQUE INDEX IF NOT EXISTS uk_etf_daily_code_date ON etf_daily(code, trade_date);

-- ============================================
-- 10. etf_net_value - ETF 净值数据表
-- ============================================
CREATE TABLE IF NOT EXISTS etf_net_value (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    net_value_date DATE NOT NULL,
    unit_net_value DECIMAL(10,4),
    accumulated_net_value DECIMAL(10,4),
    daily_growth_rate DECIMAL(10,4),
    subscription_status VARCHAR(20),
    redemption_status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE etf_net_value IS 'ETF净值数据表';
COMMENT ON COLUMN etf_net_value.id IS '主键ID';
COMMENT ON COLUMN etf_net_value.code IS 'ETF基金代码';
COMMENT ON COLUMN etf_net_value.net_value_date IS '净值日期';
COMMENT ON COLUMN etf_net_value.unit_net_value IS '单位净值（元）';
COMMENT ON COLUMN etf_net_value.accumulated_net_value IS '累计净值（元）';
COMMENT ON COLUMN etf_net_value.daily_growth_rate IS '日增长率（%）';
COMMENT ON COLUMN etf_net_value.subscription_status IS '申购状态';
COMMENT ON COLUMN etf_net_value.redemption_status IS '赎回状态';
COMMENT ON COLUMN etf_net_value.created_at IS '创建时间';
COMMENT ON COLUMN etf_net_value.updated_at IS '更新时间';

CREATE INDEX IF NOT EXISTS idx_etf_net_value_code ON etf_net_value(code);
CREATE INDEX IF NOT EXISTS idx_etf_net_value_net_value_date ON etf_net_value(net_value_date);
CREATE UNIQUE INDEX IF NOT EXISTS uk_etf_net_value_code_date ON etf_net_value(code, net_value_date);

-- ============================================
-- 创建 updated_at 自动更新触发器函数
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 为需要的表创建 updated_at 触发器
-- ============================================
CREATE TRIGGER update_stocks_updated_at
    BEFORE UPDATE ON stocks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stock_industry_updated_at
    BEFORE UPDATE ON stock_industry
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stock_market_value_updated_at
    BEFORE UPDATE ON stock_market_value
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stock_financial_income_updated_at
    BEFORE UPDATE ON stock_financial_income
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trading_calendar_updated_at
    BEFORE UPDATE ON trading_calendar
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_etf_funds_updated_at
    BEFORE UPDATE ON etf_funds
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_etf_net_value_updated_at
    BEFORE UPDATE ON etf_net_value
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
