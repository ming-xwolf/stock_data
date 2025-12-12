# Dolt 数据库部署说明

本项目使用 Dolt 作为股票数据的存储数据库。Dolt 是一个版本控制的 SQL 数据库，类似于 Git，可以追踪数据的变化历史。

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，设置数据库密码
```

### 2. 启动数据库

```bash
docker-compose up -d
```

### 3. 连接数据库

使用 MySQL 客户端连接：
- 主机: `localhost`
- 端口: `13306`
- 用户名: `root`
- 密码: `.env` 文件中设置的 `DOLT_ROOT_PASSWORD`

### 4. 停止数据库

```bash
docker-compose down
```

### 5. 查看日志

```bash
docker-compose logs -f dolt
```

## 数据持久化

数据库数据存储在 `./dolt-data` 目录中，即使容器停止或删除，数据也会保留。

## 版本控制

Dolt 支持类似 Git 的版本控制功能：

```bash
# 进入容器
docker exec -it stock_data_dolt bash

# 初始化仓库（如果需要）
dolt init

# 查看提交历史
dolt log

# 创建分支
dolt branch feature-branch

# 提交更改
dolt add .
dolt commit -m "更新股票数据"
```

## 常用操作

### 使用 MySQL 客户端连接

```bash
mysql -h 127.0.0.1 -P 13306 -u root -p
```

### 使用 Python 连接

```python
import pymysql

conn = pymysql.connect(
    host='localhost',
    port=13306,
    user='root',
    password='your_password',
    database='stock_data'
)
```

## 认证配置

Dolt 默认使用 `caching_sha2_password` 认证方法，这需要 TLS 连接。为了简化开发环境的使用，已配置为使用 `mysql_native_password` 认证方法。

如果遇到 "No authentication methods available" 错误，可以手动执行以下命令修复：

```bash
docker exec stock_data_dolt dolt sql -q "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'test'; FLUSH PRIVILEGES;"
docker exec stock_data_dolt dolt sql -q "CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'test'; GRANT ALL PRIVILEGES ON *.* TO 'root'@'%'; FLUSH PRIVILEGES;"
```

## 注意事项

- 确保端口 13306 未被其他服务占用
- 定期备份 `dolt-data` 目录
- 生产环境请修改默认密码
- 配置文件 `config.yaml` 中已禁用 TLS 要求（`require_secure_transport: false`），适合开发环境使用
