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
-- 6. stock_financial_balance - 股票财务数据表（资产负债表）
-- ============================================
CREATE TABLE IF NOT EXISTS stock_financial_balance (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL COMMENT '股票代码',
    report_date DATE NOT NULL COMMENT '报告日期',
    report_period VARCHAR(20) COMMENT '报告期（如：2024Q1, 2024）',
    report_type VARCHAR(20) COMMENT '报告类型（年报/中报/季报）',
    total_assets DECIMAL(20,2) COMMENT '资产总计（元）',
    total_liabilities DECIMAL(20,2) COMMENT '负债合计（元）',
    total_equity DECIMAL(20,2) COMMENT '股东权益合计（元）',
    current_assets DECIMAL(20,2) COMMENT '流动资产合计（元）',
    non_current_assets DECIMAL(20,2) COMMENT '非流动资产合计（元）',
    current_liabilities DECIMAL(20,2) COMMENT '流动负债合计（元）',
    non_current_liabilities DECIMAL(20,2) COMMENT '非流动负债合计（元）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_code (code),
    INDEX idx_report_date (report_date),
    UNIQUE KEY uk_code_date (code, report_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票财务数据表-资产负债表';

-- ============================================
-- 7. stock_financial_income - 股票财务数据表（利润表）
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
-- 8. stock_financial_cashflow - 股票财务数据表（现金流量表）
-- ============================================
CREATE TABLE IF NOT EXISTS stock_financial_cashflow (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL COMMENT '股票代码',
    report_date DATE NOT NULL COMMENT '报告日期',
    report_period VARCHAR(20) COMMENT '报告期（如：2024Q1, 2024）',
    report_type VARCHAR(20) COMMENT '报告类型（年报/中报/季报）',
    operating_cashflow DECIMAL(20,2) COMMENT '经营活动产生的现金流量净额（元）',
    investing_cashflow DECIMAL(20,2) COMMENT '投资活动产生的现金流量净额（元）',
    financing_cashflow DECIMAL(20,2) COMMENT '筹资活动产生的现金流量净额（元）',
    net_cashflow DECIMAL(20,2) COMMENT '现金及现金等价物净增加额（元）',
    ending_cash_balance DECIMAL(20,2) COMMENT '期末现金及现金等价物余额（元）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_code (code),
    INDEX idx_report_date (report_date),
    UNIQUE KEY uk_code_date (code, report_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票财务数据表-现金流量表';

-- ============================================
-- 9. stock_financial_indicators - 股票财务指标表
-- ============================================
CREATE TABLE IF NOT EXISTS stock_financial_indicators (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL COMMENT '股票代码',
    report_date DATE NOT NULL COMMENT '报告日期',
    report_period VARCHAR(20) COMMENT '报告期（如：2024Q1, 2024）',
    report_type VARCHAR(20) COMMENT '报告类型（年报/中报/季报）',
    roe DECIMAL(10,4) COMMENT '净资产收益率（%）',
    roa DECIMAL(10,4) COMMENT '总资产收益率（%）',
    gross_profit_rate DECIMAL(10,4) COMMENT '销售毛利率（%）',
    net_profit_rate DECIMAL(10,4) COMMENT '销售净利率（%）',
    asset_liability_ratio DECIMAL(10,4) COMMENT '资产负债率（%）',
    current_ratio DECIMAL(10,4) COMMENT '流动比率',
    quick_ratio DECIMAL(10,4) COMMENT '速动比率',
    eps DECIMAL(10,4) COMMENT '每股收益（元）',
    bps DECIMAL(10,4) COMMENT '每股净资产（元）',
    pe_ratio DECIMAL(10,4) COMMENT '市盈率',
    pb_ratio DECIMAL(10,4) COMMENT '市净率',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_code (code),
    INDEX idx_report_date (report_date),
    UNIQUE KEY uk_code_date (code, report_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票财务指标表';

