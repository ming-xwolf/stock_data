# Stock Data - 中国A股行情数据准备工具

本项目用于准备中国A股的行情数据，为本地量化交易提供数据支持。项目包含从GitHub下载qlib行情数据并更新到本地，同时也会通过Tushare、akshare等数据源获取股票的其它基本信息，包括个股基本信息、财务信息、行业信息等。

## 功能特性

### 已实现功能

- **Qlib行情数据更新**
  - 自动从GitHub Release下载最新的qlib行情数据
  - 支持手动指定本地tar包文件进行更新
  - 自动备份现有数据，确保数据安全
  - 智能日期检测，自动选择最新的交易日数据
  - 数据验证机制，确保数据完整性

- **A股股票列表获取和存储**
  - 使用AKShare API获取A股股票列表
  - 自动识别股票市场（上海/深圳/北京）
  - 支持获取股票上市日期
  - 批量存储到Supabase数据库
  - 支持数据更新和去重

- **股票扩展数据获取和存储**
  - ✅ 公司信息：企业性质（央企国资控股、民企、外资等）、实际控制人、主营产品
  - ✅ 行业信息：行业名称、行业代码、概念板块、地区
  - ✅ 股东信息：前十大股东、持股比例、持股变化
  - ✅ 市值信息：总市值、流通市值、总股本、流通股本
  - ✅ 财务数据：利润表
    - 利润表：支持获取所有报告期的利润表数据（年报、中报、季报），包含营业收入、营业成本、营业利润、净利润、归母净利润、每股收益等完整字段

- **日线行情数据获取和存储**
  - ✅ 使用AKShare获取日线行情数据（腾讯、东方财富数据源）
  - ✅ 使用Tushare获取日线行情数据（专业数据源，需要积分）
  - ✅ 自动检测最新日期，只获取新数据
  - ✅ 内置API频率限制保护，避免超出调用限制

- **A股交易日历获取和存储**
  - ✅ 使用AKShare获取A股交易日历
  - ✅ 自动检测最新日期，只更新新数据
  - ✅ 支持查询指定日期是否为交易日

- **ETF（交易型开放式指数基金）数据获取和存储**
  - ✅ ETF 基金列表获取和存储
  - ✅ ETF 日线行情数据获取和存储（使用 AKShare）
  - ✅ ETF 净值数据获取和存储
  - ✅ 自动检测最新日期，只获取新数据
  - ✅ 内置 API 频率限制保护，避免超出调用限制

### 计划功能

- **数据增强**
  - 通过Tushare API获取更详细的财务数据
  - 历史财务数据批量归档
  - 财务指标自动计算
  - 行业指数数据获取

- **数据分析和可视化**
  - 数据质量检查工具
  - 数据可视化工具
  - 数据报表生成

- **自动化**
  - 定时任务自动更新数据
  - 数据变更通知
  - 数据备份自动化

## 项目结构

```
stock_data/
├── src/                           # Python源代码目录
│   ├── __init__.py                # Python包初始化文件
│   ├── clients/                   # 数据源客户端
│   │   ├── akshare_client.py      # AKShare客户端
│   │   └── tushare_client.py      # Tushare客户端
│   ├── core/                      # 核心模块
│   │   ├── config.py              # 数据库配置（统一接口）
│   │   ├── db.py                  # 数据库管理器（统一接口）
│   │   ├── cache_manager.py       # 缓存管理器
│   │   └── db_adapters/           # 数据库适配器模块
│   │       ├── supabase_config.py      # Supabase配置
│   │       └── supabase_connection.py   # Supabase连接管理
│   ├── services/                  # 业务服务模块
│   │   ├── stock_service.py            # 股票服务
│   │   ├── akshare_daily_service.py    # AKShare日线服务
│   │   ├── tushare_daily_service.py    # Tushare日线服务
│   │   ├── etf_service.py              # ETF服务
│   │   ├── etf_daily_service.py        # ETF日线服务
│   │   ├── etf_net_value_service.py    # ETF净值服务
│   │   ├── industry_service.py         # 行业服务
│   │   ├── trading_calendar_service.py # 交易日历服务
│   │   ├── market_value_service.py     # 市值服务
│   │   ├── shareholder_service.py      # 股东服务
│   │   ├── financial_service.py        # 财务服务
│   │   ├── limit_service.py            # 涨跌停服务
│   │   └── sql_queries/                # SQL查询语句模块
│   │       ├── sql_manager.py          # SQL管理器
│   │       ├── stock_sql.py             # 股票SQL
│   │       ├── akshare_daily_sql.py    # AKShare日线SQL
│   │       ├── tushare_daily_sql.py    # Tushare日线SQL
│   │       └── ...                      # 其他服务SQL
│   └── scripts/                   # 脚本目录
│       ├── fetch_stocks.py             # 获取股票列表
│       ├── fetch_etfs.py              # 获取ETF列表
│       ├── update_akshare_daily.py    # 更新AKShare日线
│       ├── update_tushare_daily.py    # 更新Tushare日线
│       ├── update_akshare_stock_data.py # 更新股票扩展数据
│       ├── update_trading_calendar.py  # 更新交易日历
│       ├── update_etf_daily.py         # 更新ETF日线
│       ├── update_etf_net_value.py     # 更新ETF净值
│       └── query_limit_stocks.py       # 查询涨跌停
├── qlib/                          # Qlib相关工具目录
│   ├── data/                      # 数据存储目录
│   │   └── qlib_bin_YYYY-MM-DD.tar.gz # qlib行情数据压缩包
│   └── update_from_github_release.sh  # qlib数据更新脚本
├── supabase/                      # Supabase相关文件
├── supabase/                      # Supabase相关文件
│   ├── 001_init_database.sql      # Supabase初始化脚本
│   └── migrate_data.py            # 数据迁移脚本
├── .gitignore                     # Git忽略文件配置
├── requirements.txt                # Python依赖
└── README.md                      # 项目说明文档
```

## 环境要求

- **操作系统**: macOS / Linux
- **Python**: Python 3.8+
- **Python依赖**: 见 `requirements.txt`
  - `psycopg2>=2.9.0` - PostgreSQL/Supabase 支持
  - `akshare>=1.12.0` - AKShare数据源
  - `tushare>=1.4.0` - Tushare数据源
  - `python-dotenv>=1.0.0` - 环境变量管理
- **工具**: 
  - `wget`（用于下载数据）
  - `tar`（用于解压数据）
  - `bash`（脚本执行环境）
- **数据库**: 
  - Supabase (PostgreSQL) - 默认数据库

## 安装和使用

### 1. 克隆项目

```bash
git clone <repository-url>
cd stock_data
```

### 2. 使用Qlib数据更新脚本

#### 自动下载最新数据

```bash
bash qlib/update_from_github_release.sh
```

脚本会自动：
- 检测当前工作日
- 从GitHub Release下载最新的qlib数据
- 备份现有数据到 `~/.qlib/backup/`
- 解压并安装数据到 `~/.qlib/qlib_data/cn_data/`
- 验证数据完整性

#### 使用本地tar包

```bash
# 使用完整路径
bash qlib/update_from_github_release.sh --file /path/to/qlib_bin_YYYYMMDD.tar.gz

# 使用简短参数
bash qlib/update_from_github_release.sh -f /path/to/qlib_bin_YYYYMMDD.tar.gz
```

#### 查看帮助信息

```bash
bash qlib/update_from_github_release.sh --help
```

### 3. 配置数据库

项目使用 Supabase (PostgreSQL) 作为数据库。

#### 配置 Supabase

在项目根目录 `.env` 文件中配置：

```bash
# 方式1: 使用连接 URI（推荐）
SUPABASE_URI=postgresql://user:password@host:port/database

# 方式2: 使用单独参数
SUPABASE_HOST=your-supabase-host.supabase.co
SUPABASE_PORT=5432
SUPABASE_USER=postgres
SUPABASE_PASSWORD=your-password
SUPABASE_DATABASE=postgres
```

#### 初始化数据库（首次使用前）

**Supabase (PostgreSQL)**:
```bash
# 执行 Supabase 初始化脚本
psql $SUPABASE_URI < supabase/001_init_database.sql
```

### 4. 获取A股股票列表并存入数据库

#### 安装Python依赖

```bash
pip install -r requirements.txt
```

#### 启动数据库服务

项目使用 Supabase 云端数据库，无需本地启动数据库服务。如果需要本地开发环境，请参考 Supabase 官方文档设置本地实例。

#### 运行股票列表获取脚本

基本用法（快速，不获取上市日期）：
```bash
python -m src.scripts.fetch_stocks
```

获取上市日期（较慢，但信息更完整）：
```bash
python -m src.scripts.fetch_stocks --with-list-date
```

查看帮助：
```bash
python -m src.scripts.fetch_stocks --help
```

**市场识别规则**：
- 0、3开头 → SZ（深圳证券交易所）
- 6开头 → SH（上海证券交易所）
- 8、92开头 → BJ（北京证券交易所）

### 5. 更新股票扩展数据

更新单只股票的所有扩展数据：
```bash
python -m src.scripts.update_akshare_stock_data --code 000001
```

更新所有股票的行业信息：
```bash
python -m src.scripts.update_akshare_stock_data --data-type industry
```

更新所有股票的股东信息：
```bash
python -m src.scripts.update_akshare_stock_data --data-type shareholders
```

更新所有股票的市值信息：
```bash
python -m src.scripts.update_akshare_stock_data --data-type market_value
```

更新所有股票的财务数据（包括所有报告期的利润表数据）：
```bash
python -m src.scripts.update_akshare_stock_data --data-type financial
```

**利润表数据更新说明**：
- 使用 `stock_profit_sheet_by_report_em` API 获取所有报告期的利润表数据
- 自动识别报告类型（年报/中报/季报）和报告期（如：2024Q1, 2024Q2, 2024Q3, 2024Q4）
- 支持完整字段更新，包括：
  - 营业收入、营业成本、营业利润
  - 利润总额、净利润、归母净利润
  - 基本每股收益、稀释每股收益
- 批量更新所有历史报告期数据，不只是最新一期

更新所有股票的公司信息（企业性质、实际控制人、主营产品）：
```bash
python -m src.scripts.update_akshare_stock_data --data-type company_info
```

更新所有股票的所有扩展数据（推荐使用延迟避免API限制）：
```bash
python -m src.scripts.update_akshare_stock_data --delay 1.0
```

### 6. 使用Tushare更新日线行情数据

#### 配置Tushare Token

在项目根目录 `.env` 文件中添加：
```bash
TUSHARE_TOKEN=your_tushare_token_here
```

#### 更新单只股票

```bash
# 从最新日期开始更新（自动检测）
python -m src.scripts.update_tushare_daily --code 000001

# 指定日期范围
python -m src.scripts.update_tushare_daily --code 000001 --start-date 20230101 --end-date 20231201
```

#### 批量更新所有股票

```bash
# 从最新日期开始更新
python -m src.scripts.update_tushare_daily --all

# 指定日期范围
python -m src.scripts.update_tushare_daily --all --start-date 20230101 --end-date 20231201

# 自定义批次大小和延迟（推荐）
python -m src.scripts.update_tushare_daily --all --batch-size 20 --delay 1.0
```

#### 注意事项

- **API限制**: Tushare有调用频率限制，程序已内置自动延迟机制
- **默认延迟**: 客户端默认延迟0.2秒，批量更新建议使用 `--delay 1.0` 或更长
- **数据格式**: 自动转换成交量（手→股）和成交额（千元→元）
- **智能更新**: 自动检测数据库中的最新日期，只获取新数据

### 7. 使用AKShare更新日线行情数据

AKShare提供免费的数据源，包含完整的日线行情数据（OHLCV、流通股本、换手率等）。

#### 更新单只股票

```bash
# 从最新日期开始更新（自动检测数据库中的最新日期）
python -m src.scripts.update_akshare_daily --code 000001

# 指定日期范围
python -m src.scripts.update_akshare_daily --code 000001 --start-date 20230101 --end-date 20231201

# 使用后复权数据
python -m src.scripts.update_akshare_daily --code 000001 --adjust hfq

# 使用分时API获取成交量数据（如果新浪API失败）
python -m src.scripts.update_akshare_daily --code 000001 --use-minute

# 不使用新浪API（使用腾讯API作为备选）
python -m src.scripts.update_akshare_daily --code 000001 --no-sina
```

#### 批量更新所有股票

```bash
# 从最新日期开始更新（自动跳过已是最新的股票）
python -m src.scripts.update_akshare_daily --all

# 指定日期范围
python -m src.scripts.update_akshare_daily --all --start-date 20230101 --end-date 20231201

# 自定义延迟（推荐 >= 2.0 秒以避免新浪API封IP）
python -m src.scripts.update_akshare_daily --all --delay 2.5

# 自定义批次大小和延迟
python -m src.scripts.update_akshare_daily --all --batch-size 10 --delay 2.0
```

#### API数据源说明

- **优先使用**: `stock_zh_a_daily` (新浪) - 包含完整字段（OHLCV、流通股本、换手率）
- **备选方案**: `stock_zh_a_hist_tx` (腾讯) - 不包含成交量字段
- **分时API**: `stock_zh_a_hist_min_em` (东方财富) - 速度较慢，但可获取成交量

#### 注意事项

- **API限制**: 新浪API大量抓取容易封IP，建议设置延迟 >= 2.0 秒
- **默认延迟**: 批量更新默认延迟2.0秒，单只股票更新不需要延迟
- **智能更新**: 自动检测数据库中的最新日期，只获取新数据
- **自动跳过**: 批量更新时自动跳过已是最新数据的股票，减少API调用
- **数据完整性**: 优先使用新浪API，一次调用即可获取完整数据（包含成交量、流通股本、换手率）
- **复权方式**: 支持前复权（qfq，默认）、后复权（hfq）、不复权（空）

### 8. 使用AKShare更新A股交易日历

交易日历用于记录A股市场的交易日信息，可用于判断某个日期是否为交易日。

#### 更新交易日历

```bash
# 智能更新（只更新新数据，推荐）
python -m src.scripts.update_trading_calendar

# 强制更新所有数据（忽略已有数据）
python -m src.scripts.update_trading_calendar --force

# 检查指定日期是否为交易日
python -m src.scripts.update_trading_calendar --check-date 2024-01-01
```

#### 功能说明

- **智能更新**: 自动检测数据库中的最新交易日，只获取新数据
- **数据来源**: 使用AKShare的 `tool_trade_date_hist_sina` API，数据范围从1990年12月19日至今
- **数据格式**: 交易日历表只包含交易日期，表中存在的日期就是交易日，不存在则不是交易日

#### 注意事项

- **数据范围**: AKShare提供的交易日历数据从1990年12月19日开始
- **更新频率**: 建议定期更新（如每周或每月），以获取最新的交易日信息
- **数据完整性**: 交易日历表使用 `ON CONFLICT ... DO UPDATE` 机制，重复执行不会产生重复数据
- **表结构**: AKShare API只返回交易日，因此表中只存储交易日，不需要额外的标识字段

### 9. 使用 AKShare 获取和更新 ETF 数据

ETF（交易型开放式指数基金）是一种在交易所上市交易的开放式基金。项目支持获取 ETF 的基本信息、日线行情数据和净值数据。

#### 初始化 ETF 数据库表（首次使用前）

ETF 表结构已包含在 Supabase 初始化脚本中（`supabase/001_init_database.sql`），无需单独初始化。

#### 获取 ETF 基金列表

```bash
# 获取所有场内 ETF 列表并存入数据库
python -m src.scripts.fetch_etfs

# 自定义批次大小
python -m src.scripts.fetch_etfs --batch-size 100

# 仅测试数据库连接
python -m src.scripts.fetch_etfs --test-connection
```

#### 更新 ETF 日线行情数据

```bash
# 更新单只 ETF（从最新日期开始，以 510050 - 50ETF 为例）
python -m src.scripts.update_etf_daily --code 510050

# 指定日期范围
python -m src.scripts.update_etf_daily --code 510050 --start-date 20230101 --end-date 20231201

# 更新所有 ETF（从最新日期开始，自动跳过已是最新的）
python -m src.scripts.update_etf_daily --all

# 自定义延迟（推荐 >= 1.0 秒）
python -m src.scripts.update_etf_daily --all --delay 1.5

# 使用前复权数据
python -m src.scripts.update_etf_daily --code 510050 --adjust qfq

# 获取周线或月线数据
python -m src.scripts.update_etf_daily --code 510050 --period weekly
```

#### 更新 ETF 净值数据

```bash
# 更新单只 ETF 的净值数据
python -m src.scripts.update_etf_net_value --code 510050

# 指定日期范围
python -m src.scripts.update_etf_net_value --code 510050 --start-date 20230101 --end-date 20231201

# 更新所有 ETF 的净值数据
python -m src.scripts.update_etf_net_value --all

# 自定义延迟
python -m src.scripts.update_etf_net_value --all --delay 1.5
```

#### ETF 功能说明

- **数据来源**: 使用 AKShare 的 ETF 相关 API
  - `fund_etf_fund_daily_em`: 获取所有 ETF 实时数据和列表
  - `fund_etf_hist_em`: 获取 ETF 历史行情数据
  - `fund_etf_fund_info_em`: 获取 ETF 历史净值数据
- **智能更新**: 自动检测数据库中的最新日期，只获取新数据
- **自动跳过**: 批量更新时自动跳过已是最新数据的 ETF，减少 API 调用
- **API 限制**: 建议设置延迟 >= 1.0 秒以避免 API 限流
- **复权方式**: 支持前复权（qfq）、后复权（hfq）、不复权（空字符串，默认）
- **数据周期**: 支持日线（daily）、周线（weekly）、月线（monthly）

### 10. 数据存储位置

- **Qlib数据**: `~/.qlib/qlib_data/cn_data/`
- **数据备份**: `~/.qlib/backup/`
- **下载的tar包**: `qlib/data/qlib_bin_YYYY-MM-DD.tar.gz`
- **Supabase数据库**: 云端托管

## 数据源说明

### Qlib行情数据

- **来源**: GitHub Release ([chenditc/investment_data](https://github.com/chenditc/investment_data))
- **数据内容**: 中国A股历史行情数据（OHLCV）
- **更新频率**: 每日更新
- **数据格式**: qlib标准格式

### Tushare（已实现）

- **用途**: 获取日线行情数据、个股基本信息、财务数据
- **API**: 需要注册获取Token，配置在项目根目录 `.env` 文件中
- **数据内容**: 
  - ✅ 日线行情数据（OHLCV）
  - 股票基本信息（计划中）
  - 财务报表数据（计划中）
  - 财务指标（计划中）
- **API限制**:
  - 免费版：每日500次，每分钟30次
  - Pro版：每日2000次，每分钟可能更多
- **自动延迟机制**: 客户端内置延迟机制（默认0.2秒），确保不会超出API限制

### AKShare（已实现）

- **用途**: 获取股票列表、行业信息、日线行情数据、交易日历、财务数据、ETF 数据
- **数据内容**:
  - ✅ 股票列表和基本信息（已实现）
  - ✅ 日线行情数据（OHLCV、流通股本、换手率）（已实现）
  - ✅ 行业分类信息（已实现）
  - ✅ 股东信息（已实现）
  - ✅ 市值信息（已实现）
  - ✅ 财务数据（已实现）
    - 利润表：使用 `stock_profit_sheet_by_report_em` API，支持所有报告期（年报/中报/季报）
  - ✅ 交易日历（已实现）
  - ✅ ETF 数据（已实现）
    - ETF 列表：使用 `fund_etf_fund_daily_em` API
    - ETF 日线行情：使用 `fund_etf_hist_em` API
    - ETF 净值数据：使用 `fund_etf_fund_info_em` API
  - 行业指数数据（计划中）
- **API限制**: 
  - 新浪API大量抓取容易封IP，建议延迟 >= 2.0 秒
  - 程序已内置延迟控制机制，避免触发API限制
- **数据源优先级**: 
  - 日线数据：优先使用新浪API（`stock_zh_a_daily`），包含完整字段
  - 备选：腾讯API（`stock_zh_a_hist_tx`），不包含成交量
  - 交易日历：使用新浪API（`tool_trade_date_hist_sina`），数据范围从1990年12月19日至今
  - 财务数据：使用东方财富API（`stock_profit_sheet_by_report_em` 等），数据完整且稳定

## 使用示例

### 更新Qlib数据

```bash
# 自动下载最新数据
bash qlib/update_from_github_release.sh

# 输出示例：
# 开始更新投资数据...
# 初始下载日期: 2025-12-11
# 远程release存在，开始下载: 2025-12-11
# 创建数据备份...
# 备份已创建: ~/.qlib/backup/cn_data_backup_20251211_143022
# 解压数据到 ~/.qlib/qlib_data/cn_data
# ✓ 日期验证通过: 日历文件最后日期与期望日期一致
# 更新完成！
```

### 使用本地数据包

```bash
# 如果已经下载了数据包
bash qlib/update_from_github_release.sh -f qlib/data/qlib_bin_2025-12-11.tar.gz
```

## 注意事项

1. **数据备份**: 脚本会自动备份现有数据，但建议在重要操作前手动备份
2. **网络连接**: 自动下载模式需要稳定的网络连接
3. **磁盘空间**: 确保有足够的磁盘空间存储数据（建议至少10GB）
4. **权限问题**: 确保对 `~/.qlib/` 目录有读写权限

## Python模块说明

详细的Python模块使用说明请参考 [src/README.md](src/README.md)

### 模块结构

#### 核心模块 (`src/core/`)

- **`config.py`** - 数据库配置模块
  - 支持 Supabase (PostgreSQL)
  - 自动从环境变量读取配置

- **`db.py`** - 数据库管理器（统一接口）
  - 根据配置自动选择对应的数据库适配器
  - 提供统一的数据库操作接口

- **`db_adapters/`** - 数据库适配器模块
  - `supabase_config.py` - Supabase 配置
  - `supabase_connection.py` - Supabase 连接管理

#### 客户端模块 (`src/clients/`)

- **`akshare_client.py`** - AKShare数据获取客户端
  - `get_stock_income_statements()` - 获取所有报告期的利润表数据
  - `get_stock_financial_data()` - 获取最新一期财务数据

- **`tushare_client.py`** - Tushare数据获取客户端

#### 服务模块 (`src/services/`)

- **`stock_service.py`** - 股票数据服务模块
- **`akshare_daily_service.py`** - AKShare日线数据服务
- **`tushare_daily_service.py`** - Tushare日线数据服务
- **`etf_service.py`** - ETF基金服务
- **`etf_daily_service.py`** - ETF日线服务
- **`etf_net_value_service.py`** - ETF净值服务
- **`industry_service.py`** - 行业数据服务
- **`trading_calendar_service.py`** - 交易日历服务
- **`market_value_service.py`** - 市值数据服务
- **`shareholder_service.py`** - 股东数据服务
- **`financial_service.py`** - 财务数据服务
  - `insert_income_statement()` - 插入利润表数据
- **`limit_service.py`** - 涨跌停查询服务

- **`sql_queries/`** - SQL查询语句模块
  - `sql_manager.py` - SQL管理器
  - 每个服务都有对应的SQL文件，使用 PostgreSQL 原生语法

#### 脚本模块 (`src/scripts/`)

- **`fetch_stocks.py`** - 获取股票列表并存入数据库
- **`fetch_etfs.py`** - 获取ETF列表
- **`update_akshare_daily.py`** - 更新AKShare日线数据
- **`update_tushare_daily.py`** - 更新Tushare日线数据
- **`update_akshare_stock_data.py`** - 更新股票扩展数据（公司信息、行业、股东、市值、财务等）
- **`update_trading_calendar.py`** - 更新交易日历
- **`update_etf_daily.py`** - 更新ETF日线数据
- **`update_etf_net_value.py`** - 更新ETF净值数据
- **`query_limit_stocks.py`** - 查询涨跌停股票

### 架构特点

1. **数据库适配器模式**: 使用适配器模式实现统一的数据库接口
2. **SQL分离管理**: SQL语句独立管理，使用 PostgreSQL 原生语法，便于维护和修改
3. **PostgreSQL 原生语法**: 所有 SQL 语句使用 PostgreSQL 原生语法（`ON CONFLICT ... DO UPDATE`）
4. **模块化设计**: 清晰的模块划分，职责明确，易于扩展

## 开发计划

- [x] 集成AKShare获取股票列表（已完成）
- [x] 集成AKShare获取行业信息（已完成）
- [x] 集成AKShare获取股东数据（已完成）
- [x] 集成AKShare获取市值数据（已完成）
- [x] 集成AKShare获取财务数据（已完成）
  - [x] 利润表：支持获取所有报告期的利润表数据（已完成）
- [x] 集成AKShare获取日线行情数据（已完成）
- [x] 集成AKShare获取交易日历（已完成）
- [x] 集成Tushare API获取日线行情数据（已完成）
- [ ] 集成Tushare API获取更详细的财务数据
- [ ] 数据清洗和标准化处理
- [ ] 数据更新自动化脚本
- [ ] 数据质量检查工具
- [ ] 数据可视化工具

## 贡献

欢迎提交Issue和Pull Request来帮助改进项目。

## 许可证

[待定]

## 联系方式

如有问题或建议，请通过Issue反馈。

