# API 参考文档

本文档列出了项目中使用的所有 AKShare 和 Tushare API。

## 目录

- [API 使用情况总览](#api-使用情况总览)
- [AKShare API](#akshare-api)
  - [股票列表和基本信息](#股票列表和基本信息)
  - [日线行情数据](#日线行情数据)
  - [股东信息](#股东信息)
  - [市值信息](#市值信息)
  - [财务数据](#财务数据)
  - [实际控制人信息](#实际控制人信息)
- [Tushare API](#tushare-api)
  - [日线行情数据](#日线行情数据-1)
  - [股票基本信息](#股票基本信息)
- [API 限制和注意事项](#api-限制和注意事项)
- [代码位置](#代码位置)
- [使用建议](#使用建议)

---

## API 使用情况总览

### AKShare API 使用情况

| API名称 | 功能 | 优先级 | 数据源 | 使用位置 | 状态 |
|---------|------|--------|--------|----------|------|
| `stock_info_a_code_name()` | 股票列表 | 主API | AKShare | `akshare_client.py::get_stock_list()` | ✅ 使用中 |
| `stock_individual_info_em()` | 股票基本信息 | 主API | 东方财富 | `akshare_client.py::get_stock_basic_info()` | ✅ 使用中 |
| `stock_individual_basic_info_xq()` | 股票基本信息 | 备用 | 雪球 | `akshare_client.py::get_stock_basic_info()` | ✅ 备用 |
| `stock_zh_a_daily()` | 日线行情数据 | ⭐最推荐 | 新浪 | `akshare_daily_service.py::get_daily_quote_sina()` | ✅ 使用中 |
| `stock_zh_a_hist_tx()` | 日线行情数据 | 备选 | 腾讯 | `akshare_daily_service.py::get_daily_quote_tx()` | ✅ 备选 |
| `stock_zh_a_hist_min_em()` | 分时数据 | 最后备选 | 东方财富 | `akshare_daily_service.py::get_daily_quote_from_minute()` | ✅ 备选 |
| `stock_main_stock_holder()` | 股东信息 | 主API | AKShare | `akshare_client.py::get_stock_shareholders()` | ✅ 使用中 |
| `stock_zh_a_spot_em()` | 实时行情（批量） | 主API | 东方财富 | `akshare_client.py::get_all_market_value()` | ✅ 使用中 |
| `stock_individual_spot_xq()` | 实时行情（单只） | 备用 | 雪球 | `akshare_client.py::get_stock_market_value()` | ✅ 备用 |
| `stock_balance_sheet_by_report_em()` | 资产负债表 | 主API | 东方财富 | `akshare_client.py::get_stock_financial_data()` | ✅ 使用中 |
| `stock_profit_sheet_by_report_em()` | 利润表 | 主API | 东方财富 | `akshare_client.py::get_stock_financial_data()` | ✅ 使用中 |
| `stock_cash_flow_sheet_by_report_em()` | 现金流量表 | 主API | 东方财富 | `akshare_client.py::get_stock_financial_data()` | ✅ 使用中 |
| `stock_hold_control_cninfo()` | 实际控制人 | 主API | 巨潮资讯 | `akshare_client.py::get_stock_controller_info()` | ✅ 使用中 |

### Tushare API 使用情况

| API名称 | 功能 | 优先级 | 权限要求 | 使用位置 | 状态 |
|---------|------|--------|----------|----------|------|
| `pro.daily()` | 日线行情数据 | 主API | 基础权限 | `tushare_client.py::get_daily_data()` | ✅ 使用中 |
| `pro.daily_basic()` | 日线基本面数据 | 补充 | ⚠️ 需要更高积分 | `tushare_client.py::get_daily_basic_data()` | ✅ 使用中 |
| `pro.stock_basic()` | 股票基本信息列表 | 主API | 基础权限 | `tushare_client.py::get_all_stock_codes()` | ✅ 使用中 |

### 数据字段对比

| 字段 | stock_zh_a_daily (新浪) | stock_zh_a_hist_tx (腾讯) | stock_zh_a_hist_min_em (分时) | Tushare daily | Tushare daily_basic |
|------|------------------------|---------------------------|------------------------------|---------------|---------------------|
| 开盘价 | ✅ | ✅ | ✅ | ✅ | - |
| 最高价 | ✅ | ✅ | ✅ | ✅ | - |
| 最低价 | ✅ | ✅ | ✅ | ✅ | - |
| 收盘价 | ✅ | ✅ | ✅ | ✅ | - |
| 成交量 | ✅ | ❌ | ✅ | ✅ | - |
| 成交额 | ✅ | ✅ | ✅ | ✅ | - |
| 流通股本 | ✅ | ❌ | ❌ | ❌ | ✅ |
| 换手率 | ✅ | ❌ | ❌ | ❌ | ✅ |

---

## AKShare API

### 股票列表和基本信息

#### 1. `stock_info_a_code_name()`

**功能**: 获取所有A股股票代码和名称列表

**参数**: 无

**返回数据**:
- `code`: 股票代码
- `name`: 股票名称

**使用位置**: `src/akshare_client.py::get_stock_list()`

**示例**:
```python
import akshare as ak
df = ak.stock_info_a_code_name()
```

---

#### 2. `stock_individual_info_em(symbol)`

**功能**: 获取股票详细信息（东方财富）

**参数**:
- `symbol`: 股票代码（6位数字，如 '000001'）

**返回数据**: DataFrame，包含以下字段：
- `上市时间`: 上市日期
- `行业`: 行业名称
- `企业性质`: 企业性质
- `实际控制人`: 实际控制人
- `主营业务`: 主营业务
- `概念板块`: 概念板块
- `所属地域`: 所属地区

**使用位置**: `src/akshare_client.py::get_stock_basic_info()`

**备用API**: `stock_individual_basic_info_xq()` (雪球)

**示例**:
```python
import akshare as ak
df = ak.stock_individual_info_em(symbol='000001')
```

---

#### 3. `stock_individual_basic_info_xq(symbol)`

**功能**: 获取股票基本信息（雪球，备用）

**参数**:
- `symbol`: 股票代码（需要带市场标识，如 'SZ000001' 或 'SH600519'）

**返回数据**: DataFrame，包含公司基本信息

**使用位置**: `src/akshare_client.py::get_stock_basic_info()` (备用)

**代码转换**: `000001` → `SZ000001`, `600519` → `SH600519`

**示例**:
```python
import akshare as ak
df = ak.stock_individual_basic_info_xq(symbol='SZ000001')
```

---

### 日线行情数据

#### 4. `stock_zh_a_daily(symbol, start_date, end_date, adjust)` ⭐最推荐

**功能**: 获取A股历史K线数据（日线）- 新浪数据源

**参数**:
- `symbol`: 股票代码（需要带市场标识，如 'sz000001' 或 'sh600519'）
- `start_date`: 开始日期（格式：'YYYYMMDD'，默认：'19900101'）
- `end_date`: 结束日期（格式：'YYYYMMDD'，默认：'21000118'）
- `adjust`: 复权方式（'qfq'=前复权, 'hfq'=后复权, ''=不复权）

**返回数据**: DataFrame，列名：
- `date`: 交易日期
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量（股）
- `amount`: 成交额（元）
- `outstanding_share`: 流通股本（股）⭐
- `turnover`: 换手率（%）⭐

**优点**: 
- ✅ 包含完整的OHLCV数据
- ✅ 包含流通股本和换手率字段
- ✅ 数据完整，无需额外API调用

**使用位置**: `src/akshare_daily_service.py::get_daily_quote_sina()`

**代码转换**: `000001` → `sz000001`, `600519` → `sh600519`

**注意**: 
- ⚠️ 大量抓取容易封IP，建议设置适当延迟
- ✅ 项目默认优先使用此API

**示例**:
```python
import akshare as ak
df = ak.stock_zh_a_daily(
    symbol='sz000001',
    start_date='20231101',
    end_date='20231201',
    adjust='qfq'
)
```

---

#### 5. `stock_zh_a_hist_tx(symbol, start_date, end_date, adjust)` (备选)

**功能**: 获取A股历史K线数据（日线）- 腾讯数据源

**参数**:
- `symbol`: 股票代码（需要带市场标识，如 'sz000001' 或 'sh600519'）
- `start_date`: 开始日期（格式：'YYYYMMDD'）
- `end_date`: 结束日期（格式：'YYYYMMDD'）
- `adjust`: 复权方式（'qfq'=前复权, 'hfq'=后复权, ''=不复权）

**返回数据**: DataFrame，列名：
- `date`: 交易日期
- `open`: 开盘价
- `close`: 收盘价
- `high`: 最高价
- `low`: 最低价
- `amount`: 成交额

**注意**: ⚠️ 没有成交量字段，只有成交额

**使用位置**: `src/akshare_daily_service.py::get_daily_quote_tx()` (备选)

**代码转换**: `000001` → `sz000001`, `600519` → `sh600519`

**示例**:
```python
import akshare as ak
df = ak.stock_zh_a_hist_tx(
    symbol='sz000001',
    start_date='20231101',
    end_date='20231201',
    adjust='qfq'
)
```

---

#### 6. `stock_zh_a_hist_min_em(symbol, start_date, end_date, period, adjust)` (备选)

**功能**: 获取A股分时数据，可以聚合为日线数据（东方财富）

**参数**:
- `symbol`: 股票代码（6位数字，如 '000001'）
- `start_date`: 开始日期（格式：'YYYYMMDD'）
- `end_date`: 结束日期（格式：'YYYYMMDD'）
- `period`: 周期（'1'=1分钟, '5'=5分钟, '15'=15分钟, '30'=30分钟, '60'=60分钟）
- `adjust`: 复权方式（''=不复权, 'qfq'=前复权, 'hfq'=后复权）

**返回数据**: DataFrame，列名：
- `时间`: 时间戳
- `开盘`: 开盘价
- `收盘`: 收盘价
- `最高`: 最高价
- `最低`: 最低价
- `成交量`: 成交量
- `成交额`: 成交额
- `均价`: 均价

**使用位置**: `src/akshare_daily_service.py::get_daily_quote_from_minute()` (备选)

**注意**: 
- 需要手动聚合为日线数据
- 速度较慢，仅作为最后备选方案

**示例**:
```python
import akshare as ak
import pandas as pd

df = ak.stock_zh_a_hist_min_em(
    symbol='000001',
    start_date='20231201',
    end_date='20231201',
    period='1',
    adjust=''
)

# 聚合为日线
df['日期'] = pd.to_datetime(df['时间']).dt.date
daily = df.groupby('日期').agg({
    '开盘': 'first',
    '收盘': 'last',
    '最高': 'max',
    '最低': 'min',
    '成交量': 'sum',
    '成交额': 'sum'
}).reset_index()
```

---

### 股东信息

#### 7. `stock_main_stock_holder(stock)`

**功能**: 获取股票主要股东信息

**参数**:
- `stock`: 股票代码（6位数字，如 '000001'）

**返回数据**: DataFrame，包含股东名称、持股比例、持股数量等信息

**使用位置**: `src/akshare_client.py::get_stock_shareholders()`

**示例**:
```python
import akshare as ak
df = ak.stock_main_stock_holder(stock='000001')
```

---

### 市值信息

#### 8. `stock_zh_a_spot_em()`

**功能**: 批量获取所有A股实时行情数据（东方财富）

**参数**: 无

**返回数据**: DataFrame，包含所有A股的实时行情，字段包括：
- `代码`: 股票代码
- `名称`: 股票名称
- `最新价`: 最新价
- `总市值`: 总市值
- `流通市值`: 流通市值
- `总股本`: 总股本
- `流通股`: 流通股

**使用位置**: `src/akshare_client.py::get_stock_market_value()` (主API)

**示例**:
```python
import akshare as ak
df = ak.stock_zh_a_spot_em()
# 筛选特定股票
stock_data = df[df['代码'] == '000001']
```

---

#### 9. `stock_individual_spot_xq(symbol)`

**功能**: 获取单只股票实时行情数据（雪球，备用）

**参数**:
- `symbol`: 股票代码（需要带市场标识，如 'SZ000001' 或 'SH600519'）

**返回数据**: DataFrame，字段包括：
- `资产净值/总市值`: 总市值
- `流通值`: 流通市值
- `基金份额/总股本`: 总股本
- `流通股`: 流通股
- `最新`: 最新价

**使用位置**: `src/akshare_client.py::get_stock_market_value()` (备用)

**代码转换**: `000001` → `SZ000001`, `600519` → `SH600519`

**示例**:
```python
import akshare as ak
df = ak.stock_individual_spot_xq(symbol='SZ000001')
```

---

### 财务数据

#### 10. `stock_balance_sheet_by_report_em(symbol)`

**功能**: 获取资产负债表数据（东方财富）

**参数**:
- `symbol`: 股票代码（需要带市场标识，如 'SZ000001' 或 'SH600519'）

**返回数据**: DataFrame，包含资产负债表各项数据

**使用位置**: `src/akshare_client.py::get_stock_financial_data()`

**代码转换**: `000001` → `SZ000001`, `600519` → `SH600519`

**示例**:
```python
import akshare as ak
df = ak.stock_balance_sheet_by_report_em(symbol='SZ000001')
```

---

#### 11. `stock_profit_sheet_by_report_em(symbol)`

**功能**: 获取利润表数据（东方财富）

**参数**:
- `symbol`: 股票代码（需要带市场标识，如 'SZ000001' 或 'SH600519'）

**返回数据**: DataFrame，包含利润表各项数据

**使用位置**: `src/akshare_client.py::get_stock_financial_data()`

**代码转换**: `000001` → `SZ000001`, `600519` → `SH600519`

**示例**:
```python
import akshare as ak
df = ak.stock_profit_sheet_by_report_em(symbol='SZ000001')
```

---

#### 12. `stock_cash_flow_sheet_by_report_em(symbol)`

**功能**: 获取现金流量表数据（东方财富）

**参数**:
- `symbol`: 股票代码（需要带市场标识，如 'SZ000001' 或 'SH600519'）

**返回数据**: DataFrame，包含现金流量表各项数据

**使用位置**: `src/akshare_client.py::get_stock_financial_data()`

**代码转换**: `000001` → `SZ000001`, `600519` → `SH600519`

**示例**:
```python
import akshare as ak
df = ak.stock_cash_flow_sheet_by_report_em(symbol='SZ000001')
```

---

### 实际控制人信息

#### 13. `stock_hold_control_cninfo(symbol)`

**功能**: 获取股票的实际控制人信息

**参数**:
- `symbol`: 股票代码或 '全部'（获取所有股票的数据）

**返回数据**: DataFrame，字段包括：
- `证券代码`: 股票代码
- `证券简称`: 股票简称
- `变动日期`: 变动日期
- `实际控制人名称`: 实际控制人名称
- `控股数量`: 控股数量
- `控股比例`: 控股比例（%）
- `直接控制人名称`: 直接控制人名称
- `控制类型`: 控制类型

**使用位置**: `src/akshare_client.py::get_stock_controller_info()`

**注意**: 需要传入 '全部' 参数获取所有股票数据，然后筛选

**示例**:
```python
import akshare as ak
# 获取所有股票的实际控制人信息
df = ak.stock_hold_control_cninfo(symbol='全部')
# 查找特定股票
stock_data = df[df['证券代码'] == '000001']
```

---

## Tushare API

### 日线行情数据

#### 1. `pro.daily(ts_code, start_date, end_date, fields)`

**功能**: 获取股票日线行情数据

**参数**:
- `ts_code`: Tushare格式股票代码（如 '000001.SZ' 或 '600000.SH'）
- `start_date`: 开始日期（格式：'YYYYMMDD'）
- `end_date`: 结束日期（格式：'YYYYMMDD'）
- `fields`: 字段列表（默认：'ts_code,trade_date,open,high,low,close,vol,amount'）

**返回数据**: DataFrame，字段包括：
- `ts_code`: Tushare代码
- `trade_date`: 交易日期（YYYYMMDD格式）
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `vol`: 成交量（手）
- `amount`: 成交额（千元）

**注意**: 
- ⚠️ `daily` 接口**不支持** `float_share`（流通股本）和 `turnover_rate`（换手率）字段
- ✅ 这些字段需要通过 `daily_basic` 接口获取（需要更高积分权限）
- 代码会自动尝试获取 `daily_basic` 数据并合并，如果账户没有权限则这些字段为 `None`

**使用位置**: `src/tushare_client.py::get_daily_data()`

**代码转换**: `000001` → `000001.SZ`, `600519` → `600519.SH`

**数据转换**:
- 成交量：手 → 股（乘以100）
- 成交额：千元 → 元（乘以1000）
- 流通股本：万股 → 股（乘以10000，如果API支持）

**API限制**:
- 免费版：每日500次，每分钟30次
- Pro版：每日2000次，每分钟50次（日线数据接口）

**自动延迟**: 默认1.3秒（每分钟最多约46次，确保不超过50次限制）

**示例**:
```python
import tushare as ts

# 设置token
ts.set_token('your_token')
pro = ts.pro_api()

df = pro.daily(
    ts_code='000001.SZ',
    start_date='20230101',
    end_date='20231201',
    fields='ts_code,trade_date,open,high,low,close,vol,amount'
)
```

---

#### 2. `pro.daily_basic(ts_code, start_date, end_date, fields)` ⚠️需要更高积分权限

**功能**: 获取股票日线基本面数据（包含流通股本和换手率等字段）

**参数**:
- `ts_code`: Tushare格式股票代码（如 '000001.SZ' 或 '600000.SH'）
- `start_date`: 开始日期（格式：'YYYYMMDD'）
- `end_date`: 结束日期（格式：'YYYYMMDD'）
- `fields`: 字段列表（默认：'ts_code,trade_date,float_share,turnover_rate'）

**返回数据**: DataFrame，字段包括：
- `ts_code`: Tushare代码
- `trade_date`: 交易日期（YYYYMMDD格式）
- `float_share`: 流通股本（万股）
- `turnover_rate`: 换手率（%）
- `turnover_rate_f`: 换手率（自由流通股）
- `volume_ratio`: 量比
- `pe`: 市盈率
- `pb`: 市净率
- 等更多字段

**使用位置**: `src/tushare_client.py::get_daily_basic_data()`

**权限要求**: ⚠️ 需要更高积分权限，免费版和部分Pro版账户可能无法访问

**数据转换**:
- 流通股本：万股 → 股（乘以10000）

**示例**:
```python
import tushare as ts

ts.set_token('your_token')
pro = ts.pro_api()

# 注意：需要更高积分权限
df = pro.daily_basic(
    ts_code='000001.SZ',
    start_date='20230101',
    end_date='20231201',
    fields='ts_code,trade_date,float_share,turnover_rate'
)
```

---

#### 3. `pro.stock_basic(exchange, list_status, fields)`

**功能**: 获取股票基本信息列表

**参数**:
- `exchange`: 交易所（''=全部, 'SSE'=上交所, 'SZSE'=深交所）
- `list_status`: 上市状态（'L'=上市, 'D'=退市, 'P'=暂停）
- `fields`: 字段列表（默认：'ts_code,symbol,name,area,industry,list_date'）

**返回数据**: DataFrame，字段包括：
- `ts_code`: Tushare代码
- `symbol`: 股票代码（6位数字）
- `name`: 股票名称
- `area`: 地区
- `industry`: 行业
- `list_date`: 上市日期

**使用位置**: `src/tushare_client.py::get_all_stock_codes()`

**示例**:
```python
import tushare as ts

ts.set_token('your_token')
pro = ts.pro_api()

df = pro.stock_basic(
    exchange='',
    list_status='L',
    fields='ts_code,symbol,name,area,industry,list_date'
)
```

---

## API 限制和注意事项

### AKShare API

- **无官方限制**: AKShare API 通常没有严格的调用频率限制
- **网络要求**: 部分API（特别是东方财富的API）可能受代理设置影响
- **备用机制**: 项目已实现备用API机制，主API失败时自动使用备用API
- **缓存机制**: 项目已实现缓存机制，减少API调用次数
- **API优先级**:
  - 日线数据：优先使用 `stock_zh_a_daily` (新浪)，包含完整字段
  - 基本信息：优先使用 `stock_individual_info_em` (东方财富)，备用 `stock_individual_basic_info_xq` (雪球)
  - 市值数据：优先使用 `stock_zh_a_spot_em` (东方财富)，备用 `stock_individual_spot_xq` (雪球)
- **注意事项**:
  - `stock_zh_a_daily` 大量抓取容易封IP，建议设置适当延迟
  - 部分API可能受代理设置影响

### Tushare API

- **调用限制**:
  - 免费版：每日500次，每分钟30次
  - Pro版：每日2000次，每分钟50次（日线数据接口）
- **自动延迟**: 客户端内置自动延迟机制（默认1.3秒，每分钟最多约46次）
- **Token配置**: 需要在 `database/.env` 文件中配置 `TUSHARE_TOKEN`
- **数据格式**: 注意成交量（手）和成交额（千元）的单位转换
- **权限要求**:
  - `daily` 接口：基础权限，支持OHLCV数据
  - `daily_basic` 接口：需要更高积分权限，支持流通股本和换手率
  - 代码会自动尝试合并两个接口的数据，如果无权限则新字段为 `None`

---

## 代码位置

### AKShare 客户端
- **文件**: `src/akshare_client.py`
- **类**: `AKShareClient`
- **缓存**: `src/cache_manager.py`

### Tushare 客户端
- **文件**: `src/tushare_client.py`
- **类**: `TushareClient`
- **服务**: `src/tushare_daily_service.py`

### 日线数据服务
- **AKShare**: `src/akshare_daily_service.py`
  - `DailyQuoteService` 类
  - 优先使用 `stock_zh_a_daily` (新浪)
  - 备选：`stock_zh_a_hist_tx` (腾讯) 和 `stock_zh_a_hist_min_em` (分时)
- **Tushare**: `src/tushare_daily_service.py`
  - `TushareDailyService` 类
  - 自动合并 `daily` 和 `daily_basic` 接口数据

---

## API 使用优先级

### 日线行情数据

1. **AKShare - stock_zh_a_daily** (新浪) ⭐最推荐
   - 包含完整字段：OHLCV + 流通股本 + 换手率
   - 数据完整，无需额外API调用
   - 注意：大量抓取可能封IP

2. **AKShare - stock_zh_a_hist_tx** (腾讯) - 备选
   - 速度快，但缺少成交量和流通股本、换手率字段

3. **AKShare - stock_zh_a_hist_min_em** (分时) - 最后备选
   - 需要聚合，速度较慢
   - 包含成交量，但缺少流通股本和换手率

4. **Tushare - daily + daily_basic** - 备选
   - 需要合并两个接口
   - `daily_basic` 需要更高积分权限

### 股票基本信息

1. **AKShare - stock_individual_info_em** (东方财富) - 主API
2. **AKShare - stock_individual_basic_info_xq** (雪球) - 备用

### 市值信息

1. **AKShare - stock_zh_a_spot_em** (东方财富) - 主API（批量）
2. **AKShare - stock_individual_spot_xq** (雪球) - 备用（单只）

## 使用建议

1. **优先使用主API**: 主API通常提供更完整的数据
2. **自动降级**: 当主API失败时，自动使用备用API
3. **遵守限制**: 
   - Tushare API有调用限制，已内置自动延迟机制
   - AKShare API 建议设置适当延迟，避免封IP
4. **数据验证**: 获取数据后应进行验证，确保数据完整性
5. **错误处理**: 所有API调用都应包含适当的错误处理和日志记录
6. **字段完整性**: 
   - 优先使用包含完整字段的API（如 `stock_zh_a_daily`）
   - 如果API不支持某些字段，代码会自动尝试使用其他API补充
