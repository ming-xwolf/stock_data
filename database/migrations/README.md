# 数据库迁移脚本说明

## 迁移脚本列表

### 001_init_database.sql
初始数据库脚本，创建所有表结构。

**创建时间**: 2025-12-12

**说明**: 此脚本包含所有表的完整CREATE TABLE语句，用于初始化或重新创建数据库。

**包含的表**（共7个）:

1. **stocks** - 股票基本信息表
   - 主键: `code` (股票代码)
   - 主要字段: 股票名称、市场、上市日期、企业性质、实际控制人、直接控制人、主营产品等
   - 索引: 市场、名称、企业性质、控制人等

2. **stock_daily** - 股票日线数据表
   - 主键: `id` (自增)
   - 唯一键: `(code, trade_date)` - 股票代码和交易日期
   - 主要字段: 开盘价、最高价、最低价、收盘价、成交量、成交额、流通股本、换手率
   - 索引: 股票代码、交易日期
   - **注意**: 包含 `outstanding_share`（流通股本）和 `turnover`（换手率）字段

3. **stock_industry** - 股票行业信息表
   - 主键: `id` (自增)
   - 唯一键: `code` - 股票代码
   - 主要字段: 行业名称、行业代码、概念板块、地区
   - 索引: 股票代码、行业名称、更新日期

4. **stock_shareholders** - 股票股东信息表
   - 主键: `id` (自增)
   - 唯一键: `(code, report_date, shareholder_name)` - 股票代码、报告日期、股东名称
   - 主要字段: 股东名称、股东类型、持股比例、持股数量、持股变化
   - 索引: 股票代码、报告日期、股东名称

5. **stock_market_value** - 股票市值信息表
   - 主键: `id` (自增)
   - 唯一键: `(code, update_date)` - 股票代码和更新日期
   - 主要字段: 总股本、流通股本、总市值、流通市值、当前价格
   - 索引: 股票代码、更新日期

6. **stock_financial_income** - 股票财务数据表（利润表）
   - 主键: `id` (自增)
   - 唯一键: `(code, report_date)` - 股票代码和报告日期
   - 主要字段: 营业总收入、营业收入、营业成本、营业利润、净利润、每股收益等
   - 索引: 股票代码、报告日期

7. **trading_calendar** - A股交易日历表
    - 主键: `trade_date` (交易日期)
    - 主要字段: 交易日期
    - 索引: 交易日期
    - **数据来源**: AKShare `tool_trade_date_hist_sina` API
    - **数据范围**: 从1990年12月19日至今的所有交易日
    - **说明**: AKShare API只返回交易日，表中存在的日期就是交易日，不存在则不是交易日



## 使用方法

### 方法1: 使用 MySQL 客户端（推荐）

#### 首次初始化数据库

```bash
# 1. 创建数据库（如果不存在）
mysql -h 127.0.0.1 -P 13306 -u root -p -e "CREATE DATABASE IF NOT EXISTS a_stock;"

# 2. 执行初始化脚本（包含所有表结构）
mysql -h 127.0.0.1 -P 13306 -u root -p a_stock < database/migrations/001_init_database.sql
```

#### 使用 Docker

```bash
# 1. 创建数据库（如果不存在）
docker exec stock_data_dolt mysql -uroot -ptest -e "CREATE DATABASE IF NOT EXISTS a_stock;"

# 2. 执行初始化脚本
docker exec -i stock_data_dolt mysql -uroot -ptest a_stock < database/migrations/001_init_database.sql
```

#### 重新创建数据库（删除现有数据）

```bash
# ⚠️ 警告：此操作会删除所有现有数据！

# 1. 删除数据库
mysql -h 127.0.0.1 -P 13306 -u root -p -e "DROP DATABASE IF EXISTS a_stock;"

# 2. 重新创建数据库
mysql -h 127.0.0.1 -P 13306 -u root -p -e "CREATE DATABASE a_stock;"

# 3. 执行初始化脚本
mysql -h 127.0.0.1 -P 13306 -u root -p a_stock < database/migrations/001_init_database.sql
```

### 方法2: 使用 Python 脚本

```python
from src.db import db_manager

# 读取并执行SQL文件
with open('database/migrations/001_init_database.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# 执行SQL语句（按分号分割）
statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
for stmt in statements:
    if stmt:
        db_manager.execute_update(stmt)
```

## 表结构特点

### 数据完整性

- **唯一键约束**: 所有表都使用唯一键约束防止重复数据
  - `stock_daily`: `(code, trade_date)` - 同一股票同一日期只能有一条记录
  - `stock_industry`: `code` - 每只股票只有一条行业信息记录
  - `stock_shareholders`: `(code, report_date, shareholder_name)` - 同一股东在同一报告期只有一条记录
  - `stock_market_value`: `(code, update_date)` - 同一股票同一日期只能有一条市值记录
  - `stock_financial_*`: `(code, report_date)` - 同一股票同一报告期只有一条财务记录
  - `trading_calendar`: `trade_date` - 每个日期只有一条记录

### 更新机制

- **ON DUPLICATE KEY UPDATE**: 
  - `stock_daily` 表使用 `ON DUPLICATE KEY UPDATE` 机制，重复执行插入操作会自动更新现有记录
  - `trading_calendar` 表也使用 `ON DUPLICATE KEY UPDATE` 机制
  - 其他表在插入前需要先检查是否存在，或使用 `REPLACE INTO` 语句

### 时间戳字段

- **created_at**: 记录创建时间，使用 `DEFAULT CURRENT_TIMESTAMP`
- **updated_at**: 记录更新时间，使用 `ON UPDATE CURRENT_TIMESTAMP`（部分表）

### 索引优化

- 所有表都针对常用查询字段建立了索引
- 主键和唯一键自动创建索引
- 外键关联字段（如 `code`、`trade_date`）都建立了索引

## 注意事项

1. **执行顺序**: 
   - 必须先执行 `001_init_database.sql` 创建所有表结构

2. **数据备份**: 
   - 执行迁移前**强烈建议**备份数据库
   - 重新创建数据库会**删除所有现有数据**

3. **字段已存在**: 
   - 如果字段已存在，`ALTER TABLE` 会报错
   - 可以使用 `CREATE TABLE IF NOT EXISTS` 避免表已存在的错误
   - 使用 `ON DUPLICATE KEY UPDATE` 的表可以安全地重复执行插入操作

4. **字符集**: 
   - 所有表使用 `utf8mb4` 字符集，支持完整的 Unicode 字符（包括 emoji）

5. **存储引擎**: 
   - 所有表使用 `InnoDB` 存储引擎，支持事务和外键约束

6. **日期格式**: 
   - 所有日期字段使用 `DATE` 类型，格式为 `YYYY-MM-DD`
   - 时间戳字段使用 `TIMESTAMP` 类型

7. **数值精度**: 
   - 价格字段使用 `DECIMAL(10,2)` - 保留2位小数
   - 成交额使用 `DECIMAL(20,2)` - 支持大数值
   - 比例字段使用 `DECIMAL(10,4)` 或 `DECIMAL(10,6)` - 保留4-6位小数
   - 股本和成交量使用 `BIGINT` - 支持大整数

## 相关脚本

- **更新交易日历**: `python src/update_trading_calendar.py`
- **获取股票列表**: `python src/fetch_stocks.py`
- **更新股票数据**: `python src/update_akshare_stock_data.py`
- **更新日线数据**: `python src/update_akshare_daily.py` 或 `python src/update_tushare_daily.py`

## 数据库连接配置

数据库连接配置位于 `database/.env` 文件或环境变量中：

- `DOLT_HOST`: 数据库主机（默认: localhost）
- `DOLT_PORT`: 数据库端口（默认: 13306）
- `DOLT_USER`: 数据库用户（默认: root）
- `DOLT_ROOT_PASSWORD`: 数据库密码（默认: test）
- `DOLT_DATABASE`: 数据库名称（默认: a_stock）
