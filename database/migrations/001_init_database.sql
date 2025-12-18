-- 数据库初始化脚本：创建所有表结构
-- 创建时间: 2025-12-12
-- 说明: 此脚本包含所有表的完整CREATE TABLE语句，用于重新创建数据库

USE a_stock;

-- ============================================
-- 1. stocks - 股票基本信息表
-- ============================================
CREATE TABLE IF NOT EXISTS stocks (
    code VARCHAR(10) PRIMARY KEY COMMENT '股票代码',
    name VARCHAR(100) NOT NULL COMMENT '股票名称',
    market VARCHAR(10) COMMENT '市场（SH/SZ）',
    list_date DATE COMMENT '上市日期',
    company_type VARCHAR(50) COMMENT '企业性质（如：央企国资控股、民企、外资等）',
    actual_controller VARCHAR(200) COMMENT '实际控制人',
    direct_controller VARCHAR(200) COMMENT '直接控制人',
    main_business TEXT COMMENT '主营产品/主营业务',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_market (market),
    INDEX idx_name (name),
    INDEX idx_company_type (company_type),
    INDEX idx_actual_controller (actual_controller(50)),
    INDEX idx_direct_controller (direct_controller(50))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票基本信息表';

-- ============================================
-- 2. stock_daily - 股票日线数据表
-- ============================================
CREATE TABLE IF NOT EXISTS stock_daily (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL COMMENT '股票代码',
    trade_date DATE NOT NULL COMMENT '交易日期',
    open_price DECIMAL(10,2) COMMENT '开盘价',
    high_price DECIMAL(10,2) COMMENT '最高价',
    low_price DECIMAL(10,2) COMMENT '最低价',
    close_price DECIMAL(10,2) COMMENT '收盘价',
    volume BIGINT COMMENT '成交量',
    amount DECIMAL(20,2) COMMENT '成交额',
    outstanding_share BIGINT COMMENT '流通股本（股）',
    turnover DECIMAL(10,6) COMMENT '换手率（%）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_code (code),
    INDEX idx_trade_date (trade_date),
    UNIQUE KEY uk_code_date (code, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票日线数据表';

-- ============================================
-- 3. stock_industry - 股票行业信息表
-- ============================================
CREATE TABLE IF NOT EXISTS stock_industry (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL COMMENT '股票代码',
    industry_name VARCHAR(100) COMMENT '行业名称',
    industry_code VARCHAR(20) COMMENT '行业代码',
    concept VARCHAR(200) COMMENT '概念板块',
    area VARCHAR(50) COMMENT '地区',
    update_date DATE COMMENT '更新日期',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_code (code),
    INDEX idx_industry (industry_name),
    INDEX idx_update_date (update_date),
    UNIQUE KEY uk_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票行业信息表';

-- ============================================
-- 4. stock_shareholders - 股票股东信息表
-- ============================================
CREATE TABLE IF NOT EXISTS stock_shareholders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL COMMENT '股票代码',
    shareholder_name VARCHAR(200) NOT NULL COMMENT '股东名称',
    shareholder_type VARCHAR(50) COMMENT '股东类型（个人/机构/法人）',
    holding_ratio DECIMAL(10,4) COMMENT '持股比例（%）',
    holding_amount BIGINT COMMENT '持股数量（股）',
    change_amount BIGINT COMMENT '持股变化（股）',
    change_ratio DECIMAL(10,4) COMMENT '持股变化比例（%）',
    report_date DATE NOT NULL COMMENT '报告日期',
    report_period VARCHAR(20) COMMENT '报告期（如：2024Q1）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_code (code),
    INDEX idx_report_date (report_date),
    INDEX idx_shareholder (shareholder_name),
    UNIQUE KEY uk_code_date_name (code, report_date, shareholder_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票股东信息表';

-- ============================================
-- 5. stock_market_value - 股票市值信息表
-- ============================================
CREATE TABLE IF NOT EXISTS stock_market_value (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL COMMENT '股票代码',
    total_shares BIGINT COMMENT '总股本（股）',
    circulating_shares BIGINT COMMENT '流通股本（股）',
    total_market_cap DECIMAL(20,2) COMMENT '总市值（元）',
    circulating_market_cap DECIMAL(20,2) COMMENT '流通市值（元）',
    price DECIMAL(10,2) COMMENT '当前价格（元）',
    update_date DATE NOT NULL COMMENT '更新日期',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_code (code),
    INDEX idx_update_date (update_date),
    UNIQUE KEY uk_code_date (code, update_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票市值信息表';

-- ============================================
-- 6. stock_financial_income - 股票财务数据表（利润表）
-- ============================================
CREATE TABLE IF NOT EXISTS stock_financial_income (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL COMMENT '股票代码',
    report_date DATE NOT NULL COMMENT '报告日期',
    report_period VARCHAR(20) COMMENT '报告期（如：2024Q1, 2024）',
    report_type VARCHAR(20) COMMENT '报告类型（年报/中报/季报）',
    total_revenue DECIMAL(20,2) COMMENT '营业总收入（元）',
    operating_revenue DECIMAL(20,2) COMMENT '营业收入（元）',
    operating_cost DECIMAL(20,2) COMMENT '营业成本（元）',
    operating_profit DECIMAL(20,2) COMMENT '营业利润（元）',
    total_profit DECIMAL(20,2) COMMENT '利润总额（元）',
    net_profit DECIMAL(20,2) COMMENT '净利润（元）',
    net_profit_attributable DECIMAL(20,2) COMMENT '归属于母公司所有者的净利润（元）',
    basic_eps DECIMAL(10,4) COMMENT '基本每股收益（元）',
    diluted_eps DECIMAL(10,4) COMMENT '稀释每股收益（元）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_code (code),
    INDEX idx_report_date (report_date),
    UNIQUE KEY uk_code_date (code, report_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票财务数据表-利润表';

-- ============================================
-- 7. trading_calendar - A股交易日历表
-- ============================================
CREATE TABLE IF NOT EXISTS trading_calendar (
    trade_date DATE PRIMARY KEY COMMENT '交易日期',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_trade_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='A股交易日历表';


-- ============================================
-- 8. etf_funds - ETF 基金基本信息表
-- ============================================
CREATE TABLE IF NOT EXISTS etf_funds (
    code VARCHAR(10) PRIMARY KEY COMMENT 'ETF基金代码',
    name VARCHAR(100) NOT NULL COMMENT 'ETF基金名称',
    fund_type VARCHAR(50) COMMENT '基金类型（如：股票型ETF、债券型ETF等）',
    fund_company VARCHAR(100) COMMENT '基金管理公司',
    listing_date DATE COMMENT '上市日期',
    tracking_index VARCHAR(100) COMMENT '跟踪指数',
    management_fee DECIMAL(6,4) COMMENT '管理费率（%）',
    custodian_fee DECIMAL(6,4) COMMENT '托管费率（%）',
    exchange VARCHAR(10) COMMENT '交易所（SH/SZ）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_name (name),
    INDEX idx_fund_company (fund_company),
    INDEX idx_tracking_index (tracking_index),
    INDEX idx_exchange (exchange)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='ETF基金基本信息表';

-- ============================================
-- 9. etf_daily - ETF 日线行情数据表
-- ============================================
CREATE TABLE IF NOT EXISTS etf_daily (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL COMMENT 'ETF基金代码',
    trade_date DATE NOT NULL COMMENT '交易日期',
    open_price DECIMAL(10,4) COMMENT '开盘价（元）',
    high_price DECIMAL(10,4) COMMENT '最高价（元）',
    low_price DECIMAL(10,4) COMMENT '最低价（元）',
    close_price DECIMAL(10,4) COMMENT '收盘价（元）',
    volume BIGINT COMMENT '成交量（手）',
    amount DECIMAL(25,2) COMMENT '成交额（元）',
    change_amount DECIMAL(10,4) COMMENT '涨跌额（元）',
    change_rate DECIMAL(14,4) COMMENT '涨跌幅（%）',
    turnover DECIMAL(14,4) COMMENT '换手率（%）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_code (code),
    INDEX idx_trade_date (trade_date),
    UNIQUE KEY uk_code_date (code, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='ETF日线行情数据表';

-- ============================================
-- 10. etf_net_value - ETF 净值数据表
-- ============================================
CREATE TABLE IF NOT EXISTS etf_net_value (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL COMMENT 'ETF基金代码',
    net_value_date DATE NOT NULL COMMENT '净值日期',
    unit_net_value DECIMAL(10,4) COMMENT '单位净值（元）',
    accumulated_net_value DECIMAL(10,4) COMMENT '累计净值（元）',
    daily_growth_rate DECIMAL(10,4) COMMENT '日增长率（%）',
    subscription_status VARCHAR(20) COMMENT '申购状态',
    redemption_status VARCHAR(20) COMMENT '赎回状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_code (code),
    INDEX idx_net_value_date (net_value_date),
    UNIQUE KEY uk_code_date (code, net_value_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='ETF净值数据表';
