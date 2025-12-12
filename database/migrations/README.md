# 数据库迁移脚本说明

## 迁移脚本列表

### 001_init_database.sql
初始数据库脚本，创建所有表结构。

**包含的表**:
- stocks - 股票基本信息表
- stock_daily - 股票日线数据表（包含 outstanding_share 和 turnover 字段）
- stock_industry - 股票行业信息表
- stock_shareholders - 股票股东信息表
- stock_market_value - 股票市值信息表
- stock_financial - 股票财务数据表

### 002_add_daily_fields.sql
添加日线数据表的额外字段。

**添加的字段**:
- `outstanding_share` BIGINT - 流通股本（股）
- `turnover` DECIMAL(10,6) - 换手率（%）

**注意**: 如果使用 001_init_database.sql 创建数据库，这些字段已经包含在内，无需执行此迁移脚本。

## 使用方法

### 方法1: 使用 MySQL 客户端

```bash
mysql -h 127.0.0.1 -P 13306 -u root -p a_stock < database/migrations/001_init_database.sql
mysql -h 127.0.0.1 -P 13306 -u root -p a_stock < database/migrations/002_add_daily_fields.sql
```

### 方法2: 使用 Python 脚本

```python
from src.db import db_manager

# 读取并执行SQL文件
with open('database/migrations/002_add_daily_fields.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# 执行SQL语句
statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
for stmt in statements:
    if stmt:
        db_manager.execute_update(stmt)
```

## 注意事项

1. **执行顺序**: 必须先执行 001_init_database.sql，再执行后续的迁移脚本
2. **数据备份**: 执行迁移前建议备份数据库
3. **字段已存在**: 如果字段已存在，ALTER TABLE 会报错，可以忽略或先检查字段是否存在
4. **ON DUPLICATE KEY UPDATE**: stock_daily 表使用 `ON DUPLICATE KEY UPDATE` 机制，重复执行不会产生重复数据
