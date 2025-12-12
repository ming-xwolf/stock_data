# Dolt 数据库部署和初始化说明

本项目使用 Dolt 作为股票数据的存储数据库。Dolt 是一个版本控制的 SQL 数据库，类似于 Git，可以追踪数据的变化历史。

## 快速开始

### 1. 配置环境变量

```bash
cp env.example .env
# 编辑 .env 文件，设置数据库密码（DOLT_ROOT_PASSWORD）
```

### 2. 启动数据库

```bash
docker-compose up -d
```

### 3. 初始化数据库

#### 方法1: 使用自动化初始化脚本（推荐）

```bash
# 确保脚本有执行权限
chmod +x init_dolt_db.sh

# 运行初始化脚本
./init_dolt_db.sh
```

初始化脚本会自动完成以下步骤：
1. 停止 Docker Compose 服务
2. 删除本地 dolt-data 目录（清理旧数据）
3. 启动 Docker Compose 服务
4. 等待容器就绪
5. 创建数据库 `a_stock`
6. 初始化 Dolt 仓库
7. 执行迁移脚本创建表结构
8. 提交表结构到版本控制
9. 验证表可以通过 SQL Server 访问
10. 执行最终验证测试

#### 方法2: 手动初始化

```bash
# 创建数据库（如果不存在）
mysql -h 127.0.0.1 -P 13306 -u root -p -e "CREATE DATABASE IF NOT EXISTS a_stock;"

# 执行初始化脚本
mysql -h 127.0.0.1 -P 13306 -u root -p a_stock < migrations/001_init_database.sql
```

或使用 Docker：

```bash
# 创建数据库（如果不存在）
docker exec stock_data_dolt mysql -uroot -ptest -e "CREATE DATABASE IF NOT EXISTS a_stock;"

# 执行初始化脚本
docker exec -i stock_data_dolt mysql -uroot -ptest a_stock < migrations/001_init_database.sql
```

### 4. 连接数据库

使用 MySQL 客户端连接：

```bash
mysql -h 127.0.0.1 -P 13306 -u root -p
```

连接后，选择数据库：

```sql
USE a_stock;
SHOW TABLES;
```

## 数据库初始化脚本说明

### `init_dolt_db.sh` 脚本功能

自动化初始化脚本 `init_dolt_db.sh` 用于完成 Dolt 数据库的完整初始化过程。

#### 脚本功能

1. **停止 Docker Compose 服务**
   - 安全停止现有容器

2. **删除本地 dolt-data 目录**
   - 清理旧数据，确保全新初始化

3. **启动 Docker Compose 服务**
   - 启动 Dolt 数据库容器

4. **等待容器就绪**
   - 检查容器状态，确保服务可用

5. **创建数据库**
   - 创建 `a_stock` 数据库

6. **初始化 Dolt 仓库**
   - 在数据库目录中初始化 Dolt 版本控制
   - 配置用户信息（用户名和邮箱）

7. **执行迁移脚本创建表结构**
   - 执行 `migrations/001_init_database.sql`
   - 创建所有必要的表结构
   - 验证表创建成功

8. **提交到版本控制**
   - 将表结构添加到 Dolt 版本控制
   - 创建初始提交

9. **验证表可以通过 SQL Server 访问**
   - 测试每个表的可访问性
   - 确保表在 information_schema 中可见

10. **执行最终验证测试**
    - 测试数据库查询功能
    - 测试表读写功能

#### 使用方法

```bash
# 确保脚本有执行权限
chmod +x init_dolt_db.sh

# 运行脚本
./init_dolt_db.sh
```

#### 脚本输出

脚本会显示详细的执行过程，包括：
- 每个步骤的执行状态
- 成功/警告/错误消息（带颜色）
- 最终数据库信息
- 表列表
- 提交历史

#### 注意事项

1. **数据备份**: 脚本会删除 `dolt-data` 目录，请确保重要数据已备份
2. **环境变量**: 脚本会读取 `.env` 文件中的 `DOLT_ROOT_PASSWORD`（默认为 'test'）
3. **容器名称**: 默认容器名称为 `stock_data_dolt`
4. **数据库名称**: 默认数据库名称为 `a_stock`
5. **迁移文件**: 需要确保 `migrations/001_init_database.sql` 文件存在

#### 故障排除

如果脚本执行失败：

1. **检查 Docker 服务**:
   ```bash
   docker ps
   docker-compose logs
   ```

2. **检查容器状态**:
   ```bash
   docker exec stock_data_dolt dolt version
   ```

3. **手动执行步骤**:
   可以按照脚本中的步骤手动执行，查看具体错误信息

4. **查看日志**:
   ```bash
   docker-compose logs -f
   ```

## 数据库连接信息

- **主机**: localhost
- **端口**: 13306
- **用户名**: root
- **密码**: 在 `.env` 文件中配置（默认: test）
- **数据库**: a_stock

## 数据库结构

数据库包含以下表：

- `stocks` - 股票基本信息表
- `stock_daily` - 股票日线数据表
- `stock_industry` - 股票行业信息表
- `stock_shareholders` - 股票股东信息表
- `stock_market_value` - 股票市值信息表
- `stock_financial_balance` - 资产负债表
- `stock_financial_income` - 利润表
- `stock_financial_cashflow` - 现金流量表
- `stock_financial_indicators` - 财务指标表

详细的表结构说明请参考 `migrations/001_init_database.sql`。

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

## 重新创建数据库

如果需要重新创建数据库（删除所有数据）：

```bash
# 方法1: 使用初始化脚本（推荐）
./init_dolt_db.sh

# 方法2: 手动删除并重新创建
docker-compose down
rm -rf dolt-data
docker-compose up -d
# 然后执行初始化步骤
```

## 注意事项

1. **客户端连接**: 连接时请确保选择数据库 `USE a_stock;`，或在连接字符串中指定默认数据库
2. **表访问**: 如果遇到 'table not found' 错误，请先执行 `USE a_stock;`
3. **数据备份**: 重要操作前建议备份 `dolt-data` 目录
4. **版本控制**: 所有数据变更都会被 Dolt 追踪，可以随时回滚到历史版本
5. **数据更新**: 使用 `ON DUPLICATE KEY UPDATE` 机制，重复运行不会产生重复数据

## 故障排除

### 问题1: 容器无法启动

```bash
# 检查端口是否被占用
lsof -i :13306

# 查看容器日志
docker-compose logs
```

### 问题2: 无法连接数据库

```bash
# 检查容器是否运行
docker ps | grep dolt

# 检查数据库是否创建
docker exec stock_data_dolt dolt sql -q "SHOW DATABASES;"
```

### 问题3: 表不存在错误

确保已执行初始化脚本，并且已选择正确的数据库：

```sql
USE a_stock;
SHOW TABLES;
```

### 问题4: 权限问题

确保 `.env` 文件中的密码配置正确，并且 Docker 容器有足够的权限访问数据目录。
