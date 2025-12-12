# API 参考文档

本文档列出了项目中使用的所有 AKShare 和 Tushare API。

## 目录

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

#### 4. `stock_zh_a_hist_tx(symbol, start_date, end_date, adjust)`

**功能**: 获取A股历史K线数据（日线）- 腾讯数据源 ⭐推荐

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

**使用位置**: `src/akshare_daily_service.py::get_daily_quote_tx()`

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

#### 5. `stock_zh_a_hist_min_em(symbol, start_date, end_date, period, adjust)`

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

**使用位置**: `src/akshare_daily_service.py::get_daily_quote_from_minute()`

**注意**: 需要手动聚合为日线数据

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

#### 6. `stock_main_stock_holder(stock)`

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

#### 7. `stock_zh_a_spot_em()`

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

#### 8. `stock_individual_spot_xq(symbol)`

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

#### 9. `stock_balance_sheet_by_report_em(symbol)`

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

#### 10. `stock_profit_sheet_by_report_em(symbol)`

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

#### 11. `stock_cash_flow_sheet_by_report_em(symbol)`

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

#### 12. `stock_hold_control_cninfo(symbol)`

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

**使用位置**: `src/tushare_client.py::get_daily_data()`

**代码转换**: `000001` → `000001.SZ`, `600519` → `600519.SH`

**数据转换**:
- 成交量：手 → 股（乘以100）
- 成交额：千元 → 元（乘以1000）

**API限制**:
- 免费版：每日500次，每分钟30次
- Pro版：每日2000次，每分钟可能更多

**自动延迟**: 默认0.2秒（每分钟最多300次）

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

#### 2. `pro.stock_basic(exchange, list_status, fields)`

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

### Tushare API

- **调用限制**:
  - 免费版：每日500次，每分钟30次
  - Pro版：每日2000次，每分钟可能更多
- **自动延迟**: 客户端内置自动延迟机制（默认0.2秒）
- **Token配置**: 需要在 `database/.env` 文件中配置 `TUSHARE_TOKEN`
- **数据格式**: 注意成交量（手）和成交额（千元）的单位转换

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
- **Tushare**: `src/tushare_daily_service.py`

---

## 使用建议

1. **优先使用主API**: 主API通常提供更完整的数据
2. **自动降级**: 当主API失败时，自动使用备用API
3. **遵守限制**: Tushare API有调用限制，注意延迟设置
4. **数据验证**: 获取数据后应进行验证，确保数据完整性
5. **错误处理**: 所有API调用都应包含适当的错误处理和日志记录
