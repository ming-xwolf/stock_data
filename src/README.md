# Stock Data Python 模块说明

## 模块结构

```
src/
├── __init__.py                # 包初始化文件
├── config.py                  # 数据库配置模块
├── db.py                      # 数据库连接和操作模块
├── akshare_client.py          # AKShare数据获取客户端
├── tushare_client.py          # Tushare数据获取客户端
├── tushare_daily_service.py   # Tushare日线数据服务模块
├── stock_service.py           # 股票数据服务模块
├── industry_service.py        # 行业数据服务模块
├── shareholder_service.py      # 股东数据服务模块
├── market_value_service.py    # 市值数据服务模块
├── financial_service.py       # 财务数据服务模块
├── akshare_daily_service.py   # AKShare日线行情数据服务模块
├── fetch_stocks.py            # 主程序：获取股票列表并存入数据库
├── update_stock_data.py       # 主程序：更新股票扩展数据
├── update_akshare_daily.py    # 主程序：使用AKShare更新日线行情数据
└── update_tushare_daily.py    # 主程序：使用Tushare更新日线行情数据
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置数据库

1. 确保Dolt数据库服务已启动：
```bash
cd database
docker-compose up -d
```

2. 配置数据库密码（可选）：
```bash
cd database
cp env.example .env
# 编辑 .env 文件设置 DOLT_ROOT_PASSWORD
```

默认配置：
- 主机: localhost
- 端口: 13306
- 用户: root
- 密码: test
- 数据库: a_stock

## 使用方法

### 1. 获取股票列表并存入数据库

基本用法（不获取上市日期，较快）：
```bash
python src/fetch_stocks.py
```

获取上市日期（较慢，但信息更完整）：
```bash
python src/fetch_stocks.py --with-list-date
```

自定义批量大小：
```bash
python src/fetch_stocks.py --batch-size 500
```

仅测试数据库连接：
```bash
python src/fetch_stocks.py --test-connection
```

### 2. 更新股票扩展数据

更新单只股票的扩展数据：
```bash
python src/update_stock_data.py --code 000001
```

更新所有股票的行业信息：
```bash
python src/update_stock_data.py --data-type industry
```

更新所有股票的股东信息：
```bash
python src/update_stock_data.py --data-type shareholders
```

更新所有股票的市值信息：
```bash
python src/update_stock_data.py --data-type market_value
```

更新所有股票的财务数据：
```bash
python src/update_stock_data.py --data-type financial
```

更新股票日线行情数据（使用AKShare）：
```bash
# 更新单只股票（从最新日期开始，默认使用新浪API，包含成交量和更多字段）
python src/update_akshare_daily.py --code 000001

# 更新单只股票（指定日期范围）
python src/update_akshare_daily.py --code 000001 --start-date 20230101 --end-date 20231201

# 更新所有股票（从最新日期开始）
python src/update_akshare_daily.py --all

# 不使用新浪API（使用腾讯API作为备选）
python src/update_akshare_daily.py --code 000001 --no-sina

# 使用分时API获取成交量数据（如果新浪和腾讯API都失败）
python src/update_akshare_daily.py --code 000001 --use-minute
```

**数据字段说明**:
- 新浪API (`stock_zh_a_daily`) 提供完整数据：成交量、成交额、流通股本、换手率
- 腾讯API (`stock_zh_a_hist_tx`) 提供：成交额（无成交量）
- 分时API (`stock_zh_a_hist_min_em`) 提供：成交量、成交额（需聚合）

更新股票日线行情数据（使用Tushare）：
```bash
# 更新单只股票（从最新日期开始，自动检测最新日期）
python src/update_tushare_daily.py --code 000001

# 更新单只股票（指定日期范围）
python src/update_tushare_daily.py --code 000001 --start-date 20230101 --end-date 20231201

# 更新所有股票（从最新日期开始）
python src/update_tushare_daily.py --all

# 更新所有股票（指定日期范围）
python src/update_tushare_daily.py --all --start-date 20230101 --end-date 20231201

# 自定义批次大小和延迟（推荐用于批量更新）
python src/update_tushare_daily.py --all --batch-size 20 --delay 1.0

# 仅测试数据库连接
python src/update_tushare_daily.py --test-connection
```

更新所有股票的公司信息（企业性质、实际控制人、主营产品）：
```bash
python src/update_stock_data.py --data-type company_info
```

更新所有股票的所有扩展数据：
```bash
python src/update_stock_data.py
```

### 3. 在代码中使用模块

#### 使用AKShare

```python
from src.akshare_client import AKShareClient
from src.stock_service import StockService
from src.industry_service import IndustryService
from src.shareholder_service import ShareholderService

# 获取股票列表
stocks = AKShareClient.get_stock_list()

# 存入数据库
service = StockService()
service.batch_insert_stocks(stocks)

# 查询股票
stock = service.get_stock('000001')
print(stock)

# 获取并存储行业信息
industry_info = AKShareClient.get_stock_industry_info('000001')
industry_service = IndustryService()
industry_service.insert_industry(code='000001', **industry_info)

# 获取并存储公司信息
company_info = AKShareClient.get_stock_company_info('000001')
stock_service.update_company_info(
    code='000001',
    company_type=company_info.get('company_type'),
    actual_controller=company_info.get('actual_controller'),
    main_business=company_info.get('main_business')
)

# 获取并存储股东信息
shareholders = AKShareClient.get_stock_shareholders('000001')
shareholder_service = ShareholderService()
shareholder_service.batch_insert_shareholders(shareholders)
```

#### 使用Tushare

```python
from src.tushare_client import TushareClient, get_tushare_client
from src.tushare_daily_service import TushareDailyService

# 方式1: 使用全局客户端（推荐）
client = get_tushare_client()

# 方式2: 创建自定义客户端（可设置自定义延迟）
client = TushareClient(api_delay=0.5)  # 设置0.5秒延迟

# 获取日线数据
df = client.get_daily_data('000001', '20230101', '20231201')

# 格式化数据为数据库格式
formatted_df = client.format_daily_data_for_db(df, '000001')

# 使用服务类（推荐）
service = TushareDailyService()

# 获取并保存日线数据（自动检测最新日期）
success = service.fetch_and_save('000001')

# 批量更新多只股票
codes = ['000001', '000002', '600000']
result = service.batch_update(
    codes=codes,
    start_date='20230101',
    end_date='20231201',
    delay=1.0  # 每次调用延迟1秒
)
print(f"成功: {result['success_count']}, 失败: {result['failed_count']}")
```

## 模块说明

### config.py
数据库配置模块，从环境变量或.env文件读取数据库连接信息。

### db.py
数据库连接和操作模块，提供：
- `DatabaseManager`: 数据库管理器类
- `get_connection()`: 获取数据库连接的上下文管理器
- `execute_query()`: 执行查询
- `execute_update()`: 执行更新
- `execute_many()`: 批量执行

### akshare_daily_service.py
AKShare日线行情数据服务模块，提供：
- `get_daily_quote_sina()`: 使用新浪API获取日线数据（⭐推荐，包含成交量和更多字段）
- `get_daily_quote_tx()`: 使用腾讯API获取日线数据（备选）
- `get_daily_quote_from_minute()`: 使用分时API聚合日线数据（备选）
- `get_daily_quote()`: 智能选择API获取日线数据（默认优先使用新浪API）
- `fetch_and_save()`: 获取并保存日线数据到数据库
- `save_daily_quote()`: 保存日线数据到数据库（包含流通股本和换手率字段）

**数据字段**:
- 新浪API (`stock_zh_a_daily`) 返回字段：date, open, high, low, close, volume, amount, outstanding_share, turnover
- 包含完整的OHLCV数据以及流通股本和换手率

### tushare_client.py
Tushare数据获取客户端模块，提供：
- `TushareClient`: Tushare API客户端类
- `get_daily_data()`: 获取日线数据（基础字段）
- `get_daily_basic_data()`: 获取日线基本面数据（包含流通股本和换手率，需要更高积分权限）
- `get_all_stock_codes()`: 获取所有股票代码列表
- `format_daily_data_for_db()`: 格式化数据为数据库格式（支持新字段）
- **自动延迟机制**: 每次API调用后自动延迟，避免超出API频率限制
  - 默认延迟：1.3秒（每分钟最多约46次，确保不超过50次限制）
  - 支持自定义延迟时间

**字段支持说明**:
- `daily` 接口：支持基础OHLCV数据，不支持流通股本和换手率
- `daily_basic` 接口：支持流通股本和换手率，但需要更高积分权限
- 代码会自动尝试合并两个接口的数据，如果 `daily_basic` 无权限，新字段为 `None`

### tushare_daily_service.py
Tushare日线数据服务模块，提供：
- `TushareDailyService`: Tushare日线数据服务类
- `fetch_daily_data()`: 获取日线数据（自动检测最新日期）
- `save_daily_data()`: 保存日线数据到数据库
- `fetch_and_save()`: 获取并保存日线数据
- `batch_update()`: 批量更新多只股票的日线数据
- **智能日期检测**: 自动从数据库查询最新日期，只获取新数据

### akshare_client.py
AKShare客户端模块，提供：
- `get_stock_list()`: 获取A股股票列表
- `get_stock_list_date()`: 获取股票上市日期
- `enrich_stock_info()`: 丰富股票信息
- `get_stock_company_info()`: 获取公司信息（企业性质、实际控制人、主营产品）
- `get_stock_industry_info()`: 获取行业信息
- `get_stock_shareholders()`: 获取股东信息
- `get_stock_market_value()`: 获取市值信息
- `get_stock_financial_data()`: 获取财务数据

### stock_service.py
股票数据服务模块，提供：
- `insert_stock()`: 插入或更新单只股票
- `batch_insert_stocks()`: 批量插入或更新股票
- `get_stock()`: 查询单只股票
- `get_all_stocks()`: 查询所有股票
- `count_stocks()`: 统计股票数量
- `update_company_info()`: 更新公司信息（企业性质、实际控制人、主营产品）

### fetch_stocks.py
主程序，整合数据获取和数据库存储功能，用于获取股票列表。

### industry_service.py
行业数据服务模块，提供：
- `insert_industry()`: 插入或更新股票行业信息
- `get_industry()`: 查询股票行业信息

### shareholder_service.py
股东数据服务模块，提供：
- `insert_shareholder()`: 插入或更新股东信息
- `batch_insert_shareholders()`: 批量插入股东信息
- `get_shareholders()`: 查询股东信息

### market_value_service.py
市值数据服务模块，提供：
- `insert_market_value()`: 插入或更新市值信息
- `batch_insert_market_values()`: 批量插入市值信息
- `get_market_value()`: 查询最新市值信息

### financial_service.py
财务数据服务模块，提供：
- `insert_balance_sheet()`: 插入资产负债表数据
- `insert_income_statement()`: 插入利润表数据
- `insert_cashflow_statement()`: 插入现金流量表数据
- `insert_indicators()`: 插入财务指标数据

### update_stock_data.py
主程序，用于更新股票的扩展数据（行业、股东、财务、市值）。

### update_akshare_daily.py
主程序，使用AKShare更新股票日线行情数据。

### update_tushare_daily.py
主程序，使用Tushare更新股票日线行情数据。
- 支持单只股票和批量更新
- 自动检测最新日期，只获取新数据
- 内置API频率限制保护

## 注意事项

1. **数据库连接**: 确保Dolt数据库服务已启动
2. **数据库初始化**: 首次使用前，需要执行数据库初始化脚本：
   - `database/migrations/001_init_database.sql` - 完整数据库初始化脚本（推荐）
   - 包含所有表的CREATE TABLE语句，包括stocks表的所有字段
3. **网络连接**: 获取数据需要网络连接
4. **Tushare配置**: 使用Tushare功能前，需要在 `database/.env` 文件中配置 `TUSHARE_TOKEN`
   ```bash
   TUSHARE_TOKEN=your_token_here
   ```
5. **API限制**: 
   - **AKShare API**: 可能有访问频率限制，批量更新数据时请设置适当的延迟（`--delay` 参数）
- **Tushare API**: 
  - 免费版：每日500次，每分钟30次
  - Pro版：每日2000次，每分钟50次（日线数据接口）
  - Tushare客户端已内置自动延迟机制（默认1.3秒），确保每分钟不超过50次
  - 批量更新时默认延迟为0（客户端已控制频率），如需更保守可设置额外延迟
6. **数据更新**: 使用 `ON DUPLICATE KEY UPDATE` 机制，重复运行不会产生重复数据
7. **数据完整性**: 某些API可能返回不完整的数据，程序会跳过缺失字段继续处理
8. **企业性质字段**: 企业性质可能包括：央企国资控股、地方国企、民企、外资、其他等
9. **重新创建数据库**: 如果需要重新创建数据库，请先删除现有数据库，然后重新执行初始化脚本
10. **Tushare数据格式**: 
    - Tushare返回的成交量单位为"手"（1手=100股），程序会自动转换为股
    - Tushare返回的成交额单位为"千元"，程序会自动转换为元

## 错误处理

如果遇到连接错误，请检查：
1. 数据库服务是否运行：`docker ps | grep dolt`
2. 端口是否被占用：`lsof -i :13306`
3. 数据库密码是否正确
4. 网络连接是否正常

