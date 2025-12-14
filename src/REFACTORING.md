# 代码重构说明

## 重构概述

本次重构将 `src` 文件夹下的代码按照功能进行了分类组织，创建了清晰的文件夹结构。

## 新的文件夹结构

```
src/
├── __init__.py              # 模块初始化文件（提供向后兼容的导入）
├── clients/                 # 数据源客户端
│   ├── __init__.py
│   ├── akshare_client.py    # AKShare API 客户端
│   └── tushare_client.py    # Tushare API 客户端
├── services/                # 业务服务层
│   ├── __init__.py
│   ├── limit_service.py     # 涨跌停查询服务
│   ├── stock_service.py     # 股票服务
│   ├── industry_service.py  # 行业服务
│   ├── shareholder_service.py # 股东服务
│   ├── market_value_service.py # 市值服务
│   ├── financial_service.py # 财务服务
│   ├── trading_calendar_service.py # 交易日历服务
│   ├── akshare_daily_service.py # AKShare 日线数据服务
│   └── tushare_daily_service.py # Tushare 日线数据服务
├── scripts/                 # 脚本文件（更新和查询）
│   ├── __init__.py
│   ├── fetch_stocks.py      # 获取股票列表
│   ├── query_limit_stocks.py # 查询涨跌停股票
│   ├── update_akshare_stock_data.py # 更新 AKShare 股票数据
│   ├── update_akshare_daily.py # 更新 AKShare 日线数据
│   ├── update_tushare_daily.py # 更新 Tushare 日线数据
│   └── update_trading_calendar.py # 更新交易日历
└── core/                    # 核心基础设施
    ├── __init__.py
    ├── db.py                # 数据库管理
    ├── config.py            # 配置管理
    └── cache_manager.py     # 缓存管理
```

## 导入路径变更

### 新的导入方式（推荐）

```python
# 核心模块
from src.core.db import db_manager
from src.core.config import db_config
from src.core.cache_manager import cached_api_call

# 客户端
from src.clients.akshare_client import AKShareClient
from src.clients.tushare_client import TushareClient

# 服务
from src.services.stock_service import StockService
from src.services.limit_service import LimitService
# ... 其他服务
```

### 向后兼容的导入方式（仍然支持）

由于 `src/__init__.py` 中导出了所有常用模块，以下导入方式仍然可以工作：

```python
# 这些导入仍然有效（向后兼容）
from src import db_manager, AKShareClient, StockService
# 或者
from src.db import db_manager
from src.akshare_client import AKShareClient
from src.stock_service import StockService
```

## 文件分类说明

### clients/ - 数据源客户端
包含与外部数据源 API 交互的客户端代码：
- `akshare_client.py`: AKShare API 封装
- `tushare_client.py`: Tushare API 封装

### services/ - 业务服务层
包含业务逻辑和数据操作服务：
- 各种 `*_service.py` 文件：提供数据存储、查询等业务功能

### scripts/ - 脚本文件
包含可执行的脚本文件：
- `fetch_*.py`: 数据获取脚本
- `update_*.py`: 数据更新脚本
- `query_*.py`: 数据查询脚本

### core/ - 核心基础设施
包含项目的基础设施代码：
- `db.py`: 数据库连接和操作
- `config.py`: 配置管理
- `cache_manager.py`: 缓存管理

## 注意事项

1. **向后兼容性**: 通过 `src/__init__.py` 的导出，旧的导入方式仍然可以工作，但建议逐步迁移到新的导入方式。

2. **相对导入**: 在模块内部使用相对导入（如 `from ..core.db import db_manager`），在脚本中使用绝对导入（如 `from src.core.db import db_manager`）。

3. **脚本文件**: 所有脚本文件都位于 `scripts/` 目录下，它们使用绝对导入路径，因为它们是作为独立脚本运行的。

## 迁移指南

如果您的代码中使用了旧的导入方式，可以：

1. **保持现状**: 旧的导入方式仍然可以工作（向后兼容）
2. **逐步迁移**: 建议在修改代码时，将导入语句更新为新的路径
3. **批量替换**: 可以使用 IDE 的查找替换功能批量更新导入路径

## 重构完成时间

重构完成日期：2024年
