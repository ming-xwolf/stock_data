# 选股模块使用指南

## 概述

选股模块提供了灵活的选股功能，支持多种选股条件和组合逻辑。采用管道式设计，每个条件接收股票代码列表作为输入，返回符合条件的股票代码列表。

## 基本使用

### 1. 简单条件筛选

```python
from src.screening import ScreeningService
from src.screening.conditions import MarketCondition, MarketValueCondition
from src.screening.combinators import AndCombinator

# 创建选股服务
service = ScreeningService()

# 筛选：上海市场 AND 市值在100-500亿
condition = AndCombinator([
    MarketCondition(market='SH'),
    MarketValueCondition(min_value=100_0000_0000, max_value=500_0000_0000)
])

# 执行选股
stocks = service.screen_stocks(condition)
print(f"找到 {len(stocks)} 只符合条件的股票")
```

### 2. 链式筛选（AND）

```python
from src.screening.conditions import PriceChangeCondition

# 筛选：上海市场 -> 市值>100亿 -> 最近5日涨幅>10%
condition = AndCombinator([
    MarketCondition(market='SH'),
    MarketValueCondition(min_value=100_0000_0000),
    PriceChangeCondition(days=5, min_rate=0.10)
])

stocks = service.screen_stocks(condition)
```

### 3. 复杂嵌套组合

```python
from src.screening.combinators import OrCombinator

# 筛选：(上海市场 OR 深圳市场) AND (市值>100亿 OR 行业=科技)
condition = AndCombinator([
    OrCombinator([
        MarketCondition(market='SH'),
        MarketCondition(market='SZ')
    ]),
    OrCombinator([
        MarketValueCondition(min_value=100_0000_0000),
        IndustryCondition(industry_name='科技')
    ])
])

stocks = service.screen_stocks(condition)
```

### 4. 技术指标筛选

```python
from src.screening.conditions import MACDCondition, BOLLCondition

# 筛选：MACD金叉的股票
condition = MACDCondition(signal='golden_cross', period='D', days=60)
stocks = service.screen_stocks(condition)

# 筛选：BOLL顶背离的股票（价格创新高但中轨未创新高）
condition = BOLLCondition(signal='top_divergence', period='D', days=60, lookback_days=20)
stocks = service.screen_stocks(condition)

# 筛选：BOLL底背离的股票（价格创新低但中轨未创新低）
condition = BOLLCondition(signal='bottom_divergence', period='D', days=60, lookback_days=20)
stocks = service.screen_stocks(condition)
```

### 5. 财务指标筛选

```python
from src.screening.conditions import ProfitCondition, EPSCondition

# 筛选：净利润>1亿 AND 每股收益>0.5元
condition = AndCombinator([
    ProfitCondition(min_profit=100_000_000),
    EPSCondition(min_eps=0.5)
])

stocks = service.screen_stocks(condition)
```

## 可用条件

### 基础条件

- `MarketCondition`: 市场筛选（SH/SZ）
- `MarketValueCondition`: 市值筛选
- `IndustryCondition`: 行业筛选
- `ListDateCondition`: 上市日期筛选
- `CompanyTypeCondition`: 企业性质筛选
- `CodeListCondition`: 股票代码列表筛选

### 技术指标条件

- `PriceCondition`: 价格筛选
- `VolumeCondition`: 成交量筛选
- `ChangeRateCondition`: 涨跌幅筛选
- `TurnoverCondition`: 换手率筛选
- `MACDCondition`: MACD指标条件
- `BOLLCondition`: 布林带条件
  - `signal='upper'`: 价格触及上轨
  - `signal='lower'`: 价格触及下轨
  - `signal='middle'`: 价格在中轨附近
  - `signal='top_divergence'`: 顶背离（价格创新高但中轨未创新高）
  - `signal='bottom_divergence'`: 底背离（价格创新低但中轨未创新低）
  - `lookback_days`: 背离检测的回看天数（默认20）
- `MovingAverageCondition`: 均线条件

### 财务指标条件

- `RevenueCondition`: 营收筛选
- `ProfitCondition`: 利润筛选
- `EPSCondition`: 每股收益筛选
- `GrowthRateCondition`: 增长率筛选

## 组合器

- `AndCombinator`: AND组合器（所有条件必须同时满足）
- `OrCombinator`: OR组合器（任一条件满足即可）
- `NotCombinator`: NOT组合器（条件取反）

## 性能优化

1. **使用 `get_stock_codes()` 方法**：如果只需要股票代码列表，使用此方法可以避免获取详细信息，性能更好。

2. **使用 `count_stocks()` 方法**：如果只需要统计数量，使用此方法性能最好。

3. **缓存机制**：选股服务会自动缓存所有股票列表，避免重复查询。

4. **提前终止**：AND组合器在遇到空结果时会提前终止，提高性能。

## 注意事项

1. 技术指标条件（如MACD、BOLL）需要计算，可能较慢，建议先使用快速条件（如市场、市值）进行初步筛选。

2. 对于大数据量，建议先使用基础条件筛选，再用技术指标条件细化。

3. 财务数据可能不是最新的，使用财务条件时注意报告日期的选择。
