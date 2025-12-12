# a_stock 数据库结构说明

## 数据库信息

- **数据库名称**: `a_stock`
- **数据库类型**: Dolt (版本控制的 SQL 数据库)
- **字符集**: utf8mb4
- **存储引擎**: InnoDB

## 表结构

### 1. stocks - 股票基本信息表

存储股票的基本信息。

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| code | VARCHAR(10) | 股票代码 | PRIMARY KEY |
| name | VARCHAR(100) | 股票名称 | NOT NULL |
| market | VARCHAR(10) | 市场（SH/SZ） | INDEX |
| list_date | DATE | 上市日期 | |
| created_at | TIMESTAMP | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | 更新时间 | DEFAULT CURRENT_TIMESTAMP ON UPDATE |

**索引**:
- PRIMARY KEY: `code`
- INDEX: `idx_market` (market)
- INDEX: `idx_name` (name)

### 2. stock_daily - 股票日线数据表

存储股票的每日交易数据。

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | BIGINT | 自增ID | PRIMARY KEY, AUTO_INCREMENT |
| code | VARCHAR(10) | 股票代码 | NOT NULL, INDEX |
| trade_date | DATE | 交易日期 | NOT NULL, INDEX |
| open_price | DECIMAL(10,2) | 开盘价 | |
| high_price | DECIMAL(10,2) | 最高价 | |
| low_price | DECIMAL(10,2) | 最低价 | |
| close_price | DECIMAL(10,2) | 收盘价 | |
| volume | BIGINT | 成交量 | |
| amount | DECIMAL(20,2) | 成交额 | |
| created_at | TIMESTAMP | 创建时间 | DEFAULT CURRENT_TIMESTAMP |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE KEY: `uk_code_date` (code, trade_date)
- INDEX: `idx_trade_date` (trade_date)
- INDEX: `idx_code` (code)

## 使用示例

### 连接数据库

```bash
# 使用 MySQL 客户端
mysql -h 127.0.0.1 -P 13306 -u root -p

# 使用 Python
import pymysql
conn = pymysql.connect(
    host='localhost',
    port=13306,
    user='root',
    password='test',
    database='a_stock'
)
```

### 插入股票基本信息

```sql
USE a_stock;

INSERT INTO stocks (code, name, market, list_date) VALUES
('000001', '平安银行', 'SZ', '1991-04-03'),
('600000', '浦发银行', 'SH', '1999-11-10'),
('600519', '贵州茅台', 'SH', '2001-08-27');
```

### 插入日线数据

```sql
USE a_stock;

INSERT INTO stock_daily (code, trade_date, open_price, high_price, low_price, close_price, volume, amount) VALUES
('000001', '2025-12-12', 12.50, 12.80, 12.45, 12.75, 1000000, 12750000.00),
('600519', '2025-12-12', 1850.00, 1860.00, 1845.00, 1855.00, 500000, 927500000.00);
```

### 查询数据

```sql
USE a_stock;

-- 查询所有股票
SELECT * FROM stocks;

-- 查询特定股票的日线数据
SELECT * FROM stock_daily 
WHERE code = '000001' 
ORDER BY trade_date DESC 
LIMIT 10;

-- 关联查询股票信息和最新价格
SELECT s.code, s.name, s.market, 
       sd.trade_date, sd.close_price, sd.volume
FROM stocks s
LEFT JOIN stock_daily sd ON s.code = sd.code
WHERE sd.trade_date = (SELECT MAX(trade_date) FROM stock_daily WHERE code = s.code);
```

## Dolt 版本控制

### 查看状态

```bash
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/a_stock && dolt status"
```

### 提交更改

```bash
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/a_stock && dolt add stocks stock_daily"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/a_stock && dolt commit -m '更新股票数据'"
```

### 查看提交历史

```bash
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/a_stock && dolt log --oneline"
```

### 查看数据差异

```bash
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/a_stock && dolt diff stocks"
```

## 注意事项

1. **唯一约束**: `stock_daily` 表中的 `(code, trade_date)` 组合是唯一的，避免重复插入同一天的同一股票数据
2. **索引优化**: 已为常用查询字段创建索引，提高查询性能
3. **版本控制**: 所有数据变更都会被 Dolt 追踪，可以随时回滚到历史版本
4. **数据备份**: 数据库数据存储在 `./dolt-data/a_stock` 目录中

## 初始提交

数据库已创建并完成初始提交：
- 提交哈希: `db4i2sr4ke0b9cum79f4ddsva9a2fqvs`
- 提交信息: "初始提交: 创建股票基本信息和日线数据表"
