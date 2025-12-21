# Supabase 数据迁移说明

本目录包含从 Dolt 数据库迁移数据到 Supabase 的脚本和 SQL 文件。

## 文件说明

- `001_init_database.sql`: Supabase/PostgreSQL 兼容的数据库初始化脚本
- `migrate_data.py`: 数据迁移脚本，用于将 Dolt 数据库中的数据迁移到 Supabase

## 前置条件

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**：
   在项目根目录的 `.env` 文件中配置以下环境变量：
   ```bash
   # Dolt 数据库配置
   DOLT_HOST=192.168.2.37
   DOLT_PORT=13306
   DOLT_USER=root
   DOLT_ROOT_PASSWORD=test
   DOLT_DATABASE=a_stock
   
   # Supabase 配置
   SUPABASE_URI=postgresql://postgres:09b8e4ced9eda38c2017883ecf2cf88a@192.168.2.49:5432/postgres?options=reference%3Dming2046
   ```
   
   **注意**：`.env` 文件应放在项目根目录（`/Users/ming/workspace_financing/stock_data/.env`），而不是 `database/.env`。

3. **确保 Supabase 数据库已初始化**：
   在 Supabase 中执行 `001_init_database.sql` 脚本创建表结构。

## 使用步骤

### 1. 初始化 Supabase 数据库结构

首先需要在 Supabase 中创建表结构。可以通过以下方式之一：

- **方式1：使用 Supabase Dashboard**
  1. 登录 Supabase Dashboard
  2. 进入 SQL Editor
  3. 复制 `001_init_database.sql` 的内容
  4. 执行 SQL 脚本

- **方式2：使用 psql 命令行工具**
  ```bash
  psql "postgresql://postgres:09b8e4ced9eda38c2017883ecf2cf88a@192.168.2.49:5432/postgres?options=reference%3Dming2046" < 001_init_database.sql
  ```

### 2. 运行数据迁移脚本

```bash
# 激活 conda 环境（如果使用）
conda activate stock_data

# 运行迁移脚本
python supabase/migrate_data.py
```

或者直接执行：

```bash
./supabase/migrate_data.py
```

### 3. 迁移过程

脚本会：
1. 连接到 Dolt 数据库
2. 连接到 Supabase 数据库
3. 列出所有需要迁移的表
4. 询问是否在插入前清空目标表数据
5. 逐个迁移每个表的数据
6. 显示迁移进度和结果

## 注意事项

1. **数据备份**：在迁移前，建议先备份 Supabase 数据库中的数据。

2. **表结构一致性**：确保 Supabase 中的表结构与 Dolt 中的表结构一致（列名、数据类型等）。

3. **数据量**：如果数据量很大，迁移可能需要较长时间。脚本会显示进度信息。

4. **错误处理**：如果某个表迁移失败，脚本会询问是否继续迁移其他表。

5. **唯一约束**：如果目标表中已有数据且存在唯一约束冲突，迁移可能会失败。建议先清空目标表或处理冲突数据。

6. **数据类型兼容性**：
   - MySQL 的 `AUTO_INCREMENT` 在 PostgreSQL 中对应 `SERIAL`/`BIGSERIAL`
   - MySQL 的 `TIMESTAMP` 在 PostgreSQL 中对应 `TIMESTAMP`
   - 大部分数据类型是兼容的，但需要注意差异

## 故障排除

### 连接失败

- 检查网络连接
- 验证环境变量配置是否正确
- 确认数据库服务是否运行

### 表不存在错误

- 确保已在 Supabase 中执行了 `001_init_database.sql`
- 检查表名是否正确（大小写敏感）

### 数据类型错误

- 检查源表和目标表的列定义是否一致
- 查看错误日志了解具体的数据类型问题

### 唯一约束冲突

- 选择在插入前清空目标表
- 或者手动处理冲突的数据

## 迁移脚本功能

- ✅ 自动检测所有表
- ✅ 批量插入数据（每批 1000 条）
- ✅ 显示迁移进度
- ✅ 错误处理和回滚
- ✅ 支持选择是否清空目标表
- ✅ 详细的日志输出

## 示例输出

```
2025-12-20 10:00:00 - INFO - ============================================================
2025-12-20 10:00:00 - INFO - 开始数据迁移：Dolt -> Supabase
2025-12-20 10:00:00 - INFO - ============================================================
2025-12-20 10:00:01 - INFO - 成功连接到 Dolt 数据库: 192.168.2.37:13306/a_stock
2025-12-20 10:00:02 - INFO - 成功连接到 Supabase 数据库: 192.168.2.49:5432/postgres
2025-12-20 10:00:03 - INFO - 找到 10 个表: stocks, stock_daily, stock_industry, ...

是否在插入前清空目标表的数据？(y/n): y

============================================================
开始迁移表: stocks
============================================================
2025-12-20 10:00:04 - INFO - 表 stocks 的列: code, name, market, ...
2025-12-20 10:00:05 - INFO - 表 stocks 有 5000 条记录
2025-12-20 10:00:05 - INFO - 已清空表 stocks
2025-12-20 10:00:06 - INFO - 表 stocks: 已插入 1000/5000 条记录
...
2025-12-20 10:00:10 - INFO - ✓ 表 stocks 迁移完成
```
