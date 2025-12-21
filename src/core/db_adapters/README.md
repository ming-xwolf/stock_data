# 数据库适配器模块

本模块提供了对不同数据库类型的支持，将配置和连接逻辑分离到独立的文件中，便于维护和扩展。

## 目录结构

```
db_adapters/
├── __init__.py              # 模块导出
├── sql_adapter.py           # SQL 语法适配器（MySQL ↔ PostgreSQL）
├── supabase_config.py       # Supabase (PostgreSQL) 配置
├── supabase_connection.py   # Supabase (PostgreSQL) 连接管理
├── dolt_config.py           # Dolt (MySQL) 配置
└── dolt_connection.py       # Dolt (MySQL) 连接管理
```

## 模块说明

### SQL 适配器 (`sql_adapter.py`)

负责处理 MySQL 和 PostgreSQL 之间的 SQL 语法差异，主要功能：
- 将 MySQL 的 `ON DUPLICATE KEY UPDATE` 转换为 PostgreSQL 的 `ON CONFLICT ... DO UPDATE`
- 处理 `VALUES()` 到 `EXCLUDED.` 的转换
- 支持复合主键的冲突检测

### Supabase 配置 (`supabase_config.py`)

Supabase (PostgreSQL) 数据库配置类：
- 支持 URI 连接和单独参数连接
- 从环境变量读取配置
- 提供连接参数字典

### Supabase 连接 (`supabase_connection.py`)

Supabase (PostgreSQL) 数据库连接管理：
- 连接池管理
- 游标管理（使用 `RealDictCursor`）
- 事务管理
- 查询和更新操作

### Dolt 配置 (`dolt_config.py`)

Dolt (MySQL) 数据库配置类：
- 从环境变量读取配置
- 提供连接参数字典

### Dolt 连接 (`dolt_connection.py`)

Dolt (MySQL) 数据库连接管理：
- 连接池管理
- 游标管理（使用 `DictCursor`）
- 事务管理
- 查询和更新操作

## 使用方式

### 直接使用适配器

```python
from src.core.db_adapters import SupabaseConfig, SupabaseConnection

# 创建配置
config = SupabaseConfig()

# 创建连接
connection = SupabaseConnection(config)

# 执行查询
results = connection.execute_query("SELECT * FROM stocks")
```

### 通过统一接口使用

```python
from src.core.db import db_manager
from src.core.config import db_config

# 使用全局管理器（自动根据配置选择适配器）
results = db_manager.execute_query("SELECT * FROM stocks")
```

## 扩展新数据库类型

要添加新的数据库类型支持：

1. 创建配置类（如 `newdb_config.py`）：
   ```python
   class NewDBConfig:
       def __init__(self):
           # 初始化配置
           pass
       
       def get_connection_params(self):
           # 返回连接参数
           pass
   ```

2. 创建连接类（如 `newdb_connection.py`）：
   ```python
   class NewDBConnection:
       def __init__(self, config):
           # 初始化连接
           pass
       
       def execute_query(self, sql, params):
           # 实现查询
           pass
   ```

3. 在 `__init__.py` 中导出：
   ```python
   from .newdb_config import NewDBConfig
   from .newdb_connection import NewDBConnection
   ```

4. 在 `config.py` 和 `db.py` 中添加支持

## 优势

1. **模块化**：每个数据库类型的配置和连接逻辑独立
2. **易维护**：修改某个数据库的支持不影响其他数据库
3. **易扩展**：添加新数据库类型只需添加新文件
4. **清晰职责**：配置、连接、SQL 适配各司其职
5. **向后兼容**：保持原有的统一接口不变
